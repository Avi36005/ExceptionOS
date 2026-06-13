"""Analytics and insights endpoints."""
from __future__ import annotations

from datetime import datetime, timedelta
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
    total_resp = (
        supabase.table("exception_cases")
        .select("id", count="exact")
        .eq("organization_id", oid)
        .execute()
    )
    total_cases = total_resp.count or 0

    # Open cases
    open_resp = (
        supabase.table("exception_cases")
        .select("id", count="exact")
        .eq("organization_id", oid)
        .in_("status", ["submitted", "intake", "analyzing", "pending_decision"])
        .execute()
    )
    open_cases = open_resp.count or 0

    # Pending decision
    pending_resp = (
        supabase.table("exception_cases")
        .select("id", count="exact")
        .eq("organization_id", oid)
        .eq("status", "pending_decision")
        .execute()
    )
    pending = pending_resp.count or 0

    # Resolved this month
    resolved_resp = (
        supabase.table("exception_cases")
        .select("id", count="exact")
        .eq("organization_id", oid)
        .in_("status", ["approved", "partially_approved", "denied", "closed"])
        .gte("updated_at", month_start)
        .execute()
    )
    resolved_month = resolved_resp.count or 0

    # Decisions for approval rate
    decisions_resp = (
        supabase.table("human_decisions")
        .select("decision_type")
        .eq("case_id", oid)
        .execute()
    )
    decisions = decisions_resp.data or []
    # Calculate via joining through cases
    cases_resp = (
        supabase.table("exception_cases")
        .select("status")
        .eq("organization_id", oid)
        .in_("status", ["approved", "partially_approved", "denied"])
        .execute()
    )
    resolved_all = cases_resp.data or []
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
