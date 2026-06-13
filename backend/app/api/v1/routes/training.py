"""Training scenario endpoints."""
from __future__ import annotations

import random
from collections import defaultdict
from datetime import datetime
from typing import Any
from uuid import NAMESPACE_DNS, UUID, uuid4, uuid5

import structlog
from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.config import get_settings
from app.dependencies import get_current_user, get_supabase
from app.schemas import DataResponse

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/training", tags=["training"])

_TRAINING_NAMESPACE = uuid5(NAMESPACE_DNS, "exceptionos.training.scenarios")

_SCENARIO_TEMPLATES = [
    {
        "title": "Customer Discount Exception — Long-term Partner",
        "description": "A key account manager requests a 35% discount for a 5-year customer whose contract is up for renewal.",
        "entity_name": "Acme Corp",
        "requested_amount": 50000,
        "urgency": "high",
        "category": "discount",
    },
    {
        "title": "Vendor Payment Terms Extension",
        "description": "Finance team requests 90-day payment terms for a critical supplier instead of standard 30-day terms.",
        "entity_name": "SupplyChain Ltd",
        "requested_amount": 200000,
        "urgency": "medium",
        "category": "payment_terms",
    },
    {
        "title": "SLA Breach Compensation",
        "description": "Customer support requests approval to compensate a client for a 4-hour SLA breach with service credits.",
        "entity_name": "TechStart Inc",
        "requested_amount": 15000,
        "urgency": "critical",
        "category": "compensation",
    },
    {
        "title": "Budget Reallocation for Q4 Campaign",
        "description": "Marketing requests reallocation of $80k from operations budget to support an unexpected partnership opportunity.",
        "entity_name": "Internal",
        "requested_amount": 80000,
        "urgency": "high",
        "category": "budget",
    },
    {
        "title": "Regulatory Compliance Exception",
        "description": "Legal requests a temporary 30-day exception to data retention policy while migration completes.",
        "entity_name": "IT Department",
        "requested_amount": None,
        "urgency": "critical",
        "category": "compliance",
    },
]


def _safe_data(query: Any, fallback: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    try:
        resp = query.execute()
        return resp.data or (fallback or [])
    except Exception as exc:  # pragma: no cover - defensive around remote schema drift
        logger.warning("training_query_failed", error=str(exc))
        return fallback or []


def _num(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _scenario_id(index: int) -> str:
    return str(uuid5(_TRAINING_NAMESPACE, f"scenario-{index + 1}"))


def _synthetic_scenarios() -> list[dict[str, Any]]:
    settings = get_settings()
    rng = random.Random(settings.EXCEPTIONOS_SYNTHETIC_SEED)

    scenarios = []
    for i, template in enumerate(_SCENARIO_TEMPLATES):
        scenario = {
            "id": _scenario_id(i),
            "scenario_number": i + 1,
            "difficulty": rng.choice(["easy", "medium", "hard"]),
            "expected_outcome": rng.choice(["approve", "deny", "partially_approve", "escalate"]),
            **template,
        }
        scenarios.append(scenario)
    return scenarios


def _fallback_history(user_id: str | None = None) -> list[dict[str, Any]]:
    scenarios = _synthetic_scenarios()
    return [
        {
            "id": str(uuid5(_TRAINING_NAMESPACE, f"history-{i + 1}-{user_id or 'demo'}")),
            "scenario_id": scenario["id"],
            "scenario_title": scenario["title"],
            "user_id": user_id,
            "score": score,
            "submitted_decision": {"decision": scenario["expected_outcome"]},
            "feedback": {"summary": "Demo attempt showing the expected training history shape."},
            "completed_at": f"2026-06-{10 - i:02d}T10:00:00Z",
            "source": "fallback",
        }
        for i, (scenario, score) in enumerate(zip(scenarios[:3], [92.0, 84.0, 78.0], strict=False))
    ]


def _fallback_team() -> dict[str, Any]:
    members = [
        {"user_id": "demo-user-1", "name": "Demo Manager", "attempts": 5, "average_score": 88.4, "completed": 5},
        {"user_id": "demo-user-2", "name": "Demo Analyst", "attempts": 4, "average_score": 82.0, "completed": 4},
        {"user_id": "demo-user-3", "name": "Demo Approver", "attempts": 3, "average_score": 76.7, "completed": 3},
    ]
    return {
        "source": "fallback",
        "summary": {
            "team_members": len(members),
            "attempts": sum(m["attempts"] for m in members),
            "average_score": round(sum(m["average_score"] for m in members) / len(members), 1),
            "completed_attempts": sum(m["completed"] for m in members),
        },
        "members": members,
    }


@router.get("/scenarios")
async def list_scenarios(
    current_user: dict = Depends(get_current_user),
) -> DataResponse:
    """Return training scenarios with synthetic data."""
    return DataResponse(data=_synthetic_scenarios())


@router.post("/scenarios/{scenario_id}/run")
async def run_training_scenario(
    scenario_id: str,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Create a training case from a scenario and run analysis."""
    scenarios = _synthetic_scenarios()
    scenario = next((s for s in scenarios if s["id"] == scenario_id), scenarios[0])

    # Create a real case for training purposes
    case_id = str(uuid4())
    now = datetime.utcnow().isoformat()
    supabase.table("exception_cases").insert({
        "id": case_id,
        "organization_id": str(organization_id),
        "case_number": f"TRN-{case_id[:8].upper()}",
        "title": f"[TRAINING] {scenario['title']}",
        "description": scenario["description"],
        "entity_name": scenario.get("entity_name"),
        "requested_amount": scenario.get("requested_amount"),
        "urgency": scenario.get("urgency", "medium"),
        "status": "submitted",
        "version": 1,
        "created_at": now,
        "updated_at": now,
    }).execute()

    return DataResponse(
        data={
            "case_id": case_id,
            "scenario": scenario,
            "message": "Training case created. Use /exceptions/{case_id}/debate to run analysis.",
        }
    )


@router.get("/history")
async def get_training_history(
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Return training attempts for the organization."""
    attempts = _safe_data(
        supabase.table("training_attempts")
        .select("id,scenario_id,user_id,submitted_decision_json,score,feedback_json,completed_at,created_at")
        .eq("organization_id", str(organization_id))
        .order("created_at", desc=True)
        .limit(100)
    )
    if not attempts:
        return DataResponse(data=_fallback_history(current_user.get("sub")))

    scenario_ids = list({a.get("scenario_id") for a in attempts if a.get("scenario_id")})
    scenarios = _safe_data(
        supabase.table("training_scenarios")
        .select("id,title,difficulty")
        .in_("id", scenario_ids)
    ) if scenario_ids else []
    scenario_by_id = {s.get("id"): s for s in scenarios}

    history = []
    for attempt in attempts:
        scenario = scenario_by_id.get(attempt.get("scenario_id"), {})
        history.append({
            "id": attempt.get("id"),
            "scenario_id": attempt.get("scenario_id"),
            "scenario_title": scenario.get("title"),
            "difficulty": scenario.get("difficulty"),
            "user_id": attempt.get("user_id"),
            "score": _num(attempt.get("score")) if attempt.get("score") is not None else None,
            "submitted_decision": attempt.get("submitted_decision_json") or {},
            "feedback": attempt.get("feedback_json") or {},
            "completed_at": attempt.get("completed_at"),
            "created_at": attempt.get("created_at"),
            "source": "supabase",
        })
    return DataResponse(data=history)


@router.get("/team")
async def get_training_team(
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Return team-level training participation and score rollups."""
    attempts = _safe_data(
        supabase.table("training_attempts")
        .select("id,user_id,score,completed_at,created_at")
        .eq("organization_id", str(organization_id))
        .order("created_at", desc=True)
        .limit(500)
    )
    if not attempts:
        return DataResponse(data=_fallback_team())

    user_ids = list({a.get("user_id") for a in attempts if a.get("user_id")})
    profiles = _safe_data(
        supabase.table("profiles")
        .select("id,full_name,email")
        .in_("id", user_ids)
    ) if user_ids else []
    profile_by_id = {p.get("id"): p for p in profiles}

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for attempt in attempts:
        grouped[attempt.get("user_id") or "unknown"].append(attempt)

    members = []
    completed_total = 0
    scored_values = []
    for user_id, rows in grouped.items():
        profile = profile_by_id.get(user_id, {})
        scores = [_num(r.get("score")) for r in rows if r.get("score") is not None]
        completed = sum(1 for r in rows if r.get("completed_at"))
        completed_total += completed
        scored_values.extend(scores)
        members.append({
            "user_id": user_id,
            "name": profile.get("full_name") or profile.get("email") or "Unknown user",
            "email": profile.get("email"),
            "attempts": len(rows),
            "completed": completed,
            "average_score": round(sum(scores) / len(scores), 1) if scores else None,
            "last_attempt_at": rows[0].get("created_at"),
        })
    members.sort(key=lambda m: (m["attempts"], m["average_score"] or 0), reverse=True)

    return DataResponse(data={
        "source": "supabase",
        "summary": {
            "team_members": len(members),
            "attempts": len(attempts),
            "average_score": round(sum(scored_values) / len(scored_values), 1) if scored_values else None,
            "completed_attempts": completed_total,
        },
        "members": members,
    })
