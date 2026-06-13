"""Analytics and insights endpoints."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.agents.policy_drift_agent import PolicyDriftAgent
from app.dependencies import get_current_user, get_supabase
from app.domain.organizations.repository import OrganizationRepository
from app.domain.policies.repository import PolicyRepository
from app.llm.provider_router import get_provider_router
from app.memory.hindsight_client import get_hindsight_client
from app.schemas import DataResponse

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/insights", tags=["insights"])

_RESOLVED_STATUSES = ["approved", "partially_approved", "denied", "closed"]
_OPEN_STATUSES = ["submitted", "intake", "analyzing", "pending_decision"]


def _safe_data(query: Any, fallback: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Execute a Supabase query, returning fallback data on empty/error."""
    try:
        resp = query.execute()
        return resp.data or (fallback or [])
    except Exception as exc:  # pragma: no cover - defensive around remote schema drift
        logger.warning("insights_query_failed", error=str(exc))
        return fallback or []


def _safe_count(query: Any) -> int:
    try:
        resp = query.execute()
        return resp.count or 0
    except Exception as exc:  # pragma: no cover
        logger.warning("insights_count_failed", error=str(exc))
        return 0


def _num(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _pct(part: int | float, whole: int | float) -> float:
    return round((_num(part) / _num(whole)) * 100, 1) if whole else 0.0


def _iso_days_ago(days: int) -> str:
    return (datetime.utcnow() - timedelta(days=days)).isoformat()


def _demo_root_causes() -> dict[str, Any]:
    return {
        "source": "fallback",
        "summary": {
            "total_patterns": 3,
            "open_patterns": 2,
            "top_root_cause": "Policy threshold mismatch",
        },
        "root_causes": [
            {
                "root_cause": "Policy threshold mismatch",
                "occurrences": 7,
                "total_requested_amount": 185000.0,
                "representative_cases": ["Strategic discount exception", "Renewal pricing override"],
                "status": "open",
                "recommendation": "Review approval thresholds for strategic accounts.",
            },
            {
                "root_cause": "SLA ambiguity",
                "occurrences": 4,
                "total_requested_amount": 42000.0,
                "representative_cases": ["Service credit request"],
                "status": "open",
                "recommendation": "Clarify compensation bands for SLA misses.",
            },
            {
                "root_cause": "Budget timing gap",
                "occurrences": 3,
                "total_requested_amount": 96000.0,
                "representative_cases": ["Q4 campaign reallocation"],
                "status": "acknowledged",
                "recommendation": "Create a mid-quarter reallocation reserve.",
            },
        ],
    }


def _demo_consistency() -> dict[str, Any]:
    return {
        "source": "fallback",
        "summary": {
            "decision_consistency_score": 91.0,
            "recommendation_alignment_rate": 88.0,
            "cases_analyzed": 25,
        },
        "by_decision": [
            {"decision_type": "approved", "count": 12},
            {"decision_type": "partially_approved", "count": 7},
            {"decision_type": "denied", "count": 4},
            {"decision_type": "escalated", "count": 2},
        ],
        "signals": [
            "High-value discount exceptions are handled consistently.",
            "Escalations cluster around missing financial-impact evidence.",
        ],
    }


def _demo_outcomes() -> dict[str, Any]:
    return {
        "source": "fallback",
        "summary": {
            "recorded_outcomes": 18,
            "positive_outcome_rate": 83.3,
            "total_financial_impact": 247500.0,
            "outcome_completion_rate": 72.0,
        },
        "outcomes": [
            {
                "case_title": "Enterprise renewal pricing exception",
                "actual_outcome": "Customer renewed with no margin leakage beyond approved exception.",
                "financial_impact": 120000.0,
                "outcome_date": _iso_days_ago(8),
            },
            {
                "case_title": "SLA credit compensation",
                "actual_outcome": "Account retained; service-credit amount stayed within approval conditions.",
                "financial_impact": 18000.0,
                "outcome_date": _iso_days_ago(16),
            },
        ],
    }


def _demo_budgets() -> dict[str, Any]:
    return {
        "source": "fallback",
        "summary": {
            "total_budget": 500000.0,
            "spent": 312000.0,
            "remaining": 188000.0,
            "utilization_pct": 62.4,
            "currency": "USD",
        },
        "budgets": [
            {
                "label": "Enterprise exceptions",
                "budget_amount": 300000.0,
                "spent_amount": 196000.0,
                "remaining": 104000.0,
                "utilization_pct": 65.3,
                "currency": "USD",
            },
            {
                "label": "Customer success credits",
                "budget_amount": 200000.0,
                "spent_amount": 116000.0,
                "remaining": 84000.0,
                "utilization_pct": 58.0,
                "currency": "USD",
            },
        ],
    }


def _demo_provider_usage() -> dict[str, Any]:
    return {
        "source": "fallback",
        "summary": {
            "total_calls": 1247,
            "total_tokens": 1842500,
            "cost_usd": 92.37,
            "avg_latency_ms": 1420,
            "fallback_rate": 3.2,
        },
        "by_provider": [
            {"provider": "groq_primary", "calls": 1012, "tokens": 1390000, "cost_usd": 41.7, "avg_latency_ms": 980},
            {"provider": "gemini", "calls": 188, "tokens": 358000, "cost_usd": 35.8, "avg_latency_ms": 1760},
            {"provider": "openai", "calls": 47, "tokens": 94500, "cost_usd": 14.87, "avg_latency_ms": 2310},
        ],
        "recent": [],
    }


def _demo_memory_health() -> dict[str, Any]:
    return {
        "source": "fallback",
        "summary": {
            "health_score": 94.0,
            "bank_configured": True,
            "operations_30d": 318,
            "successful_operations_30d": 306,
            "open_contradictions": 2,
        },
        "operations": [
            {"operation_type": "recall", "count": 181},
            {"operation_type": "retain", "count": 104},
            {"operation_type": "reflect", "count": 33},
        ],
        "contradictions": [
            {"contradiction_type": "decision_conflict", "severity": "medium", "status": "open"},
            {"contradiction_type": "policy_note_conflict", "severity": "low", "status": "open"},
        ],
    }


def _demo_benchmarks() -> dict[str, Any]:
    return {
        "source": "fallback",
        "organization_metrics": {
            "approval_rate": 68.0,
            "average_resolution_hours": 36.0,
            "outcome_completion_rate": 72.0,
        },
        "benchmarks": [
            {"metric_name": "approval_rate", "metric_value": 64.0, "sample_size": 42, "category": "enterprise_saas"},
            {"metric_name": "average_resolution_hours", "metric_value": 48.0, "sample_size": 42, "category": "enterprise_saas"},
            {"metric_name": "outcome_completion_rate", "metric_value": 61.0, "sample_size": 42, "category": "enterprise_saas"},
        ],
        "positioning": [
            {"metric_name": "approval_rate", "comparison": "above cohort median", "delta": 4.0},
            {"metric_name": "average_resolution_hours", "comparison": "faster than cohort median", "delta": -12.0},
            {"metric_name": "outcome_completion_rate", "comparison": "above cohort median", "delta": 11.0},
        ],
    }


def _fetch_cases(supabase: Client, organization_id: UUID, limit: int = 250) -> list[dict[str, Any]]:
    return _safe_data(
        supabase.table("exception_cases")
        .select("id,title,status,urgency,entity_name,requested_amount,currency,root_cause,category_id,department_id,created_at,updated_at,resolved_at")
        .eq("organization_id", str(organization_id))
        .order("created_at", desc=True)
        .limit(limit)
    )


@router.get("/dashboard")
async def get_dashboard(
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Return dashboard metrics for the organisation."""
    oid = str(organization_id)
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1).isoformat()

    # Total cases
    total_cases = _safe_count(
        supabase.table("exception_cases")
        .select("id", count="exact")
        .eq("organization_id", oid)
    )

    # Open cases
    open_cases = _safe_count(
        supabase.table("exception_cases")
        .select("id", count="exact")
        .eq("organization_id", oid)
        .in_("status", ["submitted", "intake", "analyzing", "pending_decision"])
    )

    # Pending decision
    pending = _safe_count(
        supabase.table("exception_cases")
        .select("id", count="exact")
        .eq("organization_id", oid)
        .eq("status", "pending_decision")
    )

    # Resolved this month
    resolved_month = _safe_count(
        supabase.table("exception_cases")
        .select("id", count="exact")
        .eq("organization_id", oid)
        .in_("status", ["approved", "partially_approved", "denied", "closed"])
        .gte("updated_at", month_start)
    )

    # Calculate via joining through cases
    resolved_all = _safe_data(
        supabase.table("exception_cases")
        .select("status")
        .eq("organization_id", oid)
        .in_("status", ["approved", "partially_approved", "denied"])
    )
    approved_count = sum(1 for c in resolved_all if c["status"] in ("approved", "partially_approved"))
    approval_rate = round(approved_count / len(resolved_all) * 100, 1) if resolved_all else 0.0

    return DataResponse(data={
        "total_cases": total_cases,
        "open_cases": open_cases,
        "pending_decision": pending,
        "resolved_this_month": resolved_month,
        "approval_rate": approval_rate,
        "average_resolution_hours": 48.0,  # Placeholder — needs case timing data
        "policy_drift_alerts": 0,
    })


@router.get("/policy-drift")
async def get_policy_drift(
    organization_id: UUID = Query(...),
    demo_mode: bool = Query(False),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Run the policy drift detection agent."""
    org = OrganizationRepository(supabase).get_by_id(organization_id)
    bank_id = org.get("hindsight_bank_id", "") if org else ""

    policy_content, policy_name = PolicyRepository(supabase).get_active_content(organization_id)

    # Build a summary of recent decisions
    resp = (
        supabase.table("exception_cases")
        .select("status, urgency, category_id")
        .eq("organization_id", str(organization_id))
        .order("updated_at", desc=True)
        .limit(50)
        .execute()
    )
    recent = resp.data or []
    summary = f"Last {len(recent)} cases: " + ", ".join(
        f"{c.get('status', 'unknown')} ({c.get('urgency', '')})" for c in recent[:20]
    )

    agent = PolicyDriftAgent(get_provider_router(), get_hindsight_client())
    result = await agent.run(
        organization_id=organization_id,
        bank_id=bank_id,
        policy_content=policy_content,
        policy_name=policy_name,
        recent_decisions_summary=summary,
        demo_mode=demo_mode,
    )
    return DataResponse(data=result["output"])


@router.get("/repeated-exceptions")
async def get_repeated_exceptions(
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Identify recurring exception patterns."""
    resp = (
        supabase.table("exception_cases")
        .select("title, entity_name, status, requested_amount, category_id")
        .eq("organization_id", str(organization_id))
        .order("created_at", desc=True)
        .limit(200)
        .execute()
    )
    cases = resp.data or []

    # Simple grouping by entity_name
    entity_counts: dict[str, list] = {}
    for c in cases:
        key = c.get("entity_name") or "Unknown"
        entity_counts.setdefault(key, []).append(c)

    patterns = []
    for entity, entity_cases in entity_counts.items():
        if len(entity_cases) >= 2:
            amounts = [c.get("requested_amount") for c in entity_cases if c.get("requested_amount")]
            patterns.append({
                "pattern": f"Repeated exceptions from {entity}",
                "occurrences": len(entity_cases),
                "entity_name": entity,
                "average_amount": sum(amounts) / len(amounts) if amounts else None,
                "statuses": list({c["status"] for c in entity_cases}),
            })

    patterns.sort(key=lambda x: x["occurrences"], reverse=True)
    return DataResponse(data=patterns)


@router.get("/root-causes")
async def get_root_causes(
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Summarize recurring root causes from clusters or case metadata."""
    clusters = _safe_data(
        supabase.table("repeated_exception_clusters")
        .select("id,title,description,root_cause,case_ids_json,occurrence_count,status,last_seen_at")
        .eq("organization_id", str(organization_id))
        .order("occurrence_count", desc=True)
        .limit(20)
    )
    if clusters:
        root_causes = [
            {
                "id": c.get("id"),
                "root_cause": c.get("root_cause") or c.get("title") or "Unclassified",
                "description": c.get("description"),
                "occurrences": c.get("occurrence_count") or len(c.get("case_ids_json") or []),
                "affected_case_ids": c.get("case_ids_json") or [],
                "status": c.get("status", "open"),
                "last_seen_at": c.get("last_seen_at"),
                "recommendation": "Review the underlying policy, budget, or workflow guardrail for this cluster.",
            }
            for c in clusters
        ]
        return DataResponse(data={
            "source": "supabase",
            "summary": {
                "total_patterns": len(root_causes),
                "open_patterns": sum(1 for r in root_causes if r["status"] == "open"),
                "top_root_cause": root_causes[0]["root_cause"],
            },
            "root_causes": root_causes,
        })

    cases = _fetch_cases(supabase, organization_id)
    if not cases:
        return DataResponse(data=_demo_root_causes())

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        key = case.get("root_cause") or case.get("entity_name") or f"{case.get('urgency', 'medium')} urgency exceptions"
        grouped[key].append(case)

    root_causes = []
    for root_cause, rows in grouped.items():
        root_causes.append({
            "root_cause": root_cause,
            "occurrences": len(rows),
            "total_requested_amount": round(sum(_num(r.get("requested_amount")) for r in rows), 2),
            "representative_cases": [r.get("title") for r in rows[:3] if r.get("title")],
            "status": "open" if any(r.get("status") in _OPEN_STATUSES for r in rows) else "resolved",
            "recommendation": "Inspect the common request trigger and update the policy playbook if this pattern repeats.",
        })
    root_causes.sort(key=lambda r: (r["occurrences"], r["total_requested_amount"]), reverse=True)
    return DataResponse(data={
        "source": "supabase",
        "summary": {
            "total_patterns": len(root_causes),
            "open_patterns": sum(1 for r in root_causes if r["status"] == "open"),
            "top_root_cause": root_causes[0]["root_cause"] if root_causes else None,
        },
        "root_causes": root_causes[:10],
    })


@router.get("/consistency")
async def get_consistency(
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Compare recommendations and human decisions for consistency signals."""
    cases = _fetch_cases(supabase, organization_id)
    case_ids = [c["id"] for c in cases if c.get("id")]
    if not case_ids:
        return DataResponse(data=_demo_consistency())

    decisions = _safe_data(
        supabase.table("human_decisions")
        .select("id,case_id,recommendation_id,decision_type,created_at")
        .in_("case_id", case_ids)
        .order("created_at", desc=True)
        .limit(250)
    )
    recommendations = _safe_data(
        supabase.table("recommendations")
        .select("id,case_id,recommendation_type,confidence,created_at")
        .in_("case_id", case_ids)
        .order("created_at", desc=True)
        .limit(250)
    )
    if not decisions and not recommendations:
        return DataResponse(data=_demo_consistency())

    rec_by_id = {r.get("id"): r for r in recommendations}
    latest_rec_by_case: dict[str, dict[str, Any]] = {}
    for rec in recommendations:
        case_id = rec.get("case_id")
        if case_id and case_id not in latest_rec_by_case:
            latest_rec_by_case[case_id] = rec

    rec_to_decision = {
        "approve": "approved",
        "partially_approve": "partially_approved",
        "deny": "denied",
        "escalate": "escalated",
    }
    aligned = 0
    comparable = 0
    for decision in decisions:
        rec = rec_by_id.get(decision.get("recommendation_id")) or latest_rec_by_case.get(decision.get("case_id"))
        if not rec:
            continue
        comparable += 1
        if rec_to_decision.get(rec.get("recommendation_type")) == decision.get("decision_type"):
            aligned += 1

    decision_counts = Counter(d.get("decision_type", "unknown") for d in decisions)
    confidence_values = [_num(r.get("confidence")) for r in recommendations if r.get("confidence") is not None]
    alignment_rate = _pct(aligned, comparable)
    avg_confidence = round(sum(confidence_values) / len(confidence_values) * 100, 1) if confidence_values else 0.0
    score = round((alignment_rate * 0.7) + (avg_confidence * 0.3), 1) if comparable else avg_confidence

    return DataResponse(data={
        "source": "supabase",
        "summary": {
            "decision_consistency_score": score,
            "recommendation_alignment_rate": alignment_rate,
            "cases_analyzed": len(case_ids),
            "decisions_analyzed": len(decisions),
            "average_recommendation_confidence": avg_confidence,
        },
        "by_decision": [{"decision_type": k, "count": v} for k, v in decision_counts.most_common()],
        "signals": [
            f"{aligned} of {comparable} comparable decisions matched the latest recommendation.",
            f"{len(decisions)} human decisions and {len(recommendations)} recommendations were included.",
        ],
    })


@router.get("/outcomes")
async def get_outcomes_insights(
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Summarize actual business outcomes for resolved exceptions."""
    cases = _fetch_cases(supabase, organization_id)
    case_ids = [c["id"] for c in cases if c.get("id")]
    if not case_ids:
        return DataResponse(data=_demo_outcomes())

    outcomes = _safe_data(
        supabase.table("outcomes")
        .select("id,case_id,actual_outcome,outcome_date,financial_impact,notes,created_at")
        .in_("case_id", case_ids)
        .order("created_at", desc=True)
        .limit(100)
    )
    if not outcomes:
        return DataResponse(data=_demo_outcomes())

    case_by_id = {c["id"]: c for c in cases}
    positive_terms = ("success", "renewed", "retained", "resolved", "completed", "approved")
    enriched = []
    positive = 0
    financial_total = 0.0
    for outcome in outcomes:
        case = case_by_id.get(outcome.get("case_id"), {})
        text = (outcome.get("actual_outcome") or "").lower()
        impact = _num(outcome.get("financial_impact"))
        financial_total += impact
        if impact > 0 or any(term in text for term in positive_terms):
            positive += 1
        enriched.append({
            "id": outcome.get("id"),
            "case_id": outcome.get("case_id"),
            "case_title": case.get("title"),
            "actual_outcome": outcome.get("actual_outcome"),
            "financial_impact": impact,
            "outcome_date": outcome.get("outcome_date"),
            "notes": outcome.get("notes"),
        })

    resolved_cases = [c for c in cases if c.get("status") in _RESOLVED_STATUSES]
    return DataResponse(data={
        "source": "supabase",
        "summary": {
            "recorded_outcomes": len(outcomes),
            "positive_outcome_rate": _pct(positive, len(outcomes)),
            "total_financial_impact": round(financial_total, 2),
            "outcome_completion_rate": _pct(len(outcomes), len(resolved_cases)),
        },
        "outcomes": enriched,
    })


@router.get("/success")
async def get_success_score(
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Return a composite exception success score."""
    outcomes_data = (await get_outcomes_insights(organization_id, current_user, supabase)).data
    consistency_data = (await get_consistency(organization_id, current_user, supabase)).data

    outcome_summary = outcomes_data.get("summary", {})
    consistency_summary = consistency_data.get("summary", {})
    positive_rate = _num(outcome_summary.get("positive_outcome_rate"))
    completion_rate = _num(outcome_summary.get("outcome_completion_rate"))
    consistency_score = _num(consistency_summary.get("decision_consistency_score"))
    success_score = round((positive_rate * 0.45) + (completion_rate * 0.25) + (consistency_score * 0.30), 1)

    return DataResponse(data={
        "source": "supabase" if outcomes_data.get("source") == "supabase" or consistency_data.get("source") == "supabase" else "fallback",
        "success_score": success_score,
        "metrics": {
            "positive_outcome_rate": positive_rate,
            "outcome_completion_rate": completion_rate,
            "decision_consistency_score": consistency_score,
            "financial_impact": _num(outcome_summary.get("total_financial_impact")),
        },
        "drivers": [
            {"label": "Outcome quality", "score": positive_rate, "weight": 0.45},
            {"label": "Outcome follow-through", "score": completion_rate, "weight": 0.25},
            {"label": "Decision consistency", "score": consistency_score, "weight": 0.30},
        ],
    })


@router.get("/budgets")
async def get_budget_insights(
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Summarize exception budget utilization."""
    budgets = _safe_data(
        supabase.table("exception_budgets")
        .select("id,department_id,category_id,period_start,period_end,budget_amount,spent_amount,currency,updated_at")
        .eq("organization_id", str(organization_id))
        .order("period_end", desc=True)
        .limit(50)
    )
    if not budgets:
        return DataResponse(data=_demo_budgets())

    rows = []
    total_budget = 0.0
    total_spent = 0.0
    currencies = Counter()
    for budget in budgets:
        amount = _num(budget.get("budget_amount"))
        spent = _num(budget.get("spent_amount"))
        total_budget += amount
        total_spent += spent
        currencies.update([budget.get("currency") or "USD"])
        rows.append({
            "id": budget.get("id"),
            "label": budget.get("category_id") or budget.get("department_id") or "Organization budget",
            "period_start": budget.get("period_start"),
            "period_end": budget.get("period_end"),
            "budget_amount": amount,
            "spent_amount": spent,
            "remaining": round(amount - spent, 2),
            "utilization_pct": _pct(spent, amount),
            "currency": budget.get("currency") or "USD",
        })

    return DataResponse(data={
        "source": "supabase",
        "summary": {
            "total_budget": round(total_budget, 2),
            "spent": round(total_spent, 2),
            "remaining": round(total_budget - total_spent, 2),
            "utilization_pct": _pct(total_spent, total_budget),
            "currency": currencies.most_common(1)[0][0] if currencies else "USD",
        },
        "budgets": rows,
    })


@router.get("/benchmarks")
async def get_benchmarks(
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Compare organization metrics to anonymous benchmark cohorts."""
    dashboard = (await get_dashboard(organization_id, current_user, supabase)).data
    outcomes = (await get_outcomes_insights(organization_id, current_user, supabase)).data
    org_metrics = {
        "approval_rate": _num(dashboard.get("approval_rate")),
        "average_resolution_hours": _num(dashboard.get("average_resolution_hours")),
        "outcome_completion_rate": _num(outcomes.get("summary", {}).get("outcome_completion_rate")),
    }
    rows = _safe_data(
        supabase.table("benchmark_cohorts")
        .select("id,cohort_key,industry,organization_size,category,metric_name,metric_value,percentile_data_json,sample_size,period_start,period_end")
        .order("created_at", desc=True)
        .limit(50)
    )
    if not rows:
        return DataResponse(data=_demo_benchmarks())

    benchmarks = []
    positioning = []
    for row in rows:
        metric_name = row.get("metric_name")
        metric_value = _num(row.get("metric_value"))
        benchmarks.append({
            "id": row.get("id"),
            "cohort_key": row.get("cohort_key"),
            "metric_name": metric_name,
            "metric_value": metric_value,
            "sample_size": row.get("sample_size") or 0,
            "category": row.get("category"),
            "percentiles": row.get("percentile_data_json") or {},
            "period_start": row.get("period_start"),
            "period_end": row.get("period_end"),
        })
        if metric_name in org_metrics:
            delta = round(org_metrics[metric_name] - metric_value, 1)
            better = delta >= 0
            if metric_name == "average_resolution_hours":
                better = delta <= 0
            positioning.append({
                "metric_name": metric_name,
                "comparison": "better than cohort" if better else "below cohort",
                "delta": delta,
            })

    return DataResponse(data={
        "source": "supabase",
        "organization_metrics": org_metrics,
        "benchmarks": benchmarks,
        "positioning": positioning,
    })


@router.get("/memory-health")
async def get_memory_health(
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Return Hindsight memory operation and contradiction health."""
    org_rows = _safe_data(
        supabase.table("organizations")
        .select("hindsight_bank_id")
        .eq("id", str(organization_id))
        .limit(1)
    )
    operations = _safe_data(
        supabase.table("hindsight_operations")
        .select("operation_type,status,latency_ms,created_at")
        .eq("organization_id", str(organization_id))
        .gte("created_at", _iso_days_ago(30))
        .order("created_at", desc=True)
        .limit(500)
    )
    contradictions = _safe_data(
        supabase.table("memory_contradictions")
        .select("id,contradiction_type,severity,status,detected_at")
        .eq("organization_id", str(organization_id))
        .order("detected_at", desc=True)
        .limit(50)
    )
    if not operations and not contradictions:
        return DataResponse(data=_demo_memory_health())

    operation_counts = Counter(op.get("operation_type", "unknown") for op in operations)
    completed = sum(1 for op in operations if op.get("status") == "completed")
    open_contradictions = [c for c in contradictions if c.get("status") == "open"]
    success_rate = _pct(completed, len(operations))
    contradiction_penalty = min(len(open_contradictions) * 5, 25)
    health_score = max(0.0, round(success_rate - contradiction_penalty, 1))
    latencies = [_num(op.get("latency_ms")) for op in operations if op.get("latency_ms") is not None]

    return DataResponse(data={
        "source": "supabase",
        "summary": {
            "health_score": health_score,
            "bank_configured": bool((org_rows[0] if org_rows else {}).get("hindsight_bank_id")),
            "operations_30d": len(operations),
            "successful_operations_30d": completed,
            "open_contradictions": len(open_contradictions),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 0) if latencies else 0,
        },
        "operations": [{"operation_type": k, "count": v} for k, v in operation_counts.most_common()],
        "contradictions": contradictions,
    })


@router.get("/provider-usage")
async def get_provider_usage(
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Return LLM provider usage, cost, latency, and fallback metrics."""
    rows = _safe_data(
        supabase.table("llm_usage")
        .select("id,provider,model,agent_name,total_tokens,cost_usd,latency_ms,status,failure_category,created_at")
        .eq("organization_id", str(organization_id))
        .order("created_at", desc=True)
        .limit(500)
    )
    if not rows:
        return DataResponse(data=_demo_provider_usage())

    by_provider: dict[str, dict[str, Any]] = {}
    total_tokens = 0
    total_cost = 0.0
    latencies = []
    fallback_calls = 0
    for row in rows:
        provider = row.get("provider") or "unknown"
        bucket = by_provider.setdefault(provider, {
            "provider": provider,
            "calls": 0,
            "tokens": 0,
            "cost_usd": 0.0,
            "latency_total": 0.0,
            "latency_count": 0,
            "errors": 0,
        })
        tokens = int(_num(row.get("total_tokens")))
        cost = _num(row.get("cost_usd"))
        latency = _num(row.get("latency_ms"))
        total_tokens += tokens
        total_cost += cost
        bucket["calls"] += 1
        bucket["tokens"] += tokens
        bucket["cost_usd"] += cost
        if latency:
            bucket["latency_total"] += latency
            bucket["latency_count"] += 1
            latencies.append(latency)
        if row.get("status") == "fallback":
            fallback_calls += 1
        if row.get("status") == "error":
            bucket["errors"] += 1

    provider_rows = []
    for bucket in by_provider.values():
        latency_count = bucket.pop("latency_count")
        latency_total = bucket.pop("latency_total")
        bucket["cost_usd"] = round(bucket["cost_usd"], 4)
        bucket["avg_latency_ms"] = round(latency_total / latency_count, 0) if latency_count else 0
        provider_rows.append(bucket)
    provider_rows.sort(key=lambda p: p["calls"], reverse=True)

    return DataResponse(data={
        "source": "supabase",
        "summary": {
            "total_calls": len(rows),
            "total_tokens": total_tokens,
            "cost_usd": round(total_cost, 4),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 0) if latencies else 0,
            "fallback_rate": _pct(fallback_calls, len(rows)),
        },
        "by_provider": provider_rows,
        "recent": rows[:20],
    })
