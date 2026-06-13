"""Precedent search and retrieval routes."""
from __future__ import annotations

from uuid import UUID

import structlog
from fastapi import APIRouter, Body, Depends, Query
from supabase import Client

from app.dependencies import get_current_user, get_supabase
from app.domain.organizations.repository import OrganizationRepository
from app.memory.hindsight_client import get_hindsight_client
from app.memory.recall_service import RecallService
from app.schemas import DataResponse

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/precedents", tags=["precedents"])


@router.get("/search")
async def search_precedents(
    organization_id: UUID = Query(...),
    q: str = Query(..., min_length=3, description="Search query"),
    top_k: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Search for precedents in Hindsight."""
    org = OrganizationRepository(supabase).get_by_id(organization_id)
    bank_id = org.get("hindsight_bank_id", "") if org else ""

    if not bank_id:
        return DataResponse(data={"results": [], "message": "No Hindsight bank configured"})

    recall = RecallService(get_hindsight_client())
    memories = await recall.recall_all(bank_id, q, top_k=top_k)

    return DataResponse(data={"results": memories, "total": len(memories), "query": q})


@router.get("/")
async def list_precedent_links(
    organization_id: UUID = Query(...),
    case_id: UUID | None = Query(None),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """List precedent links, optionally filtered by case."""
    q = supabase.table("precedent_links").select("*").eq("case_id", str(case_id)) if case_id else supabase.table("precedent_links").select("*")
    resp = q.order("similarity_score", desc=True).limit(50).execute()
    return DataResponse(data=resp.data or [])


@router.get("/graph")
async def precedent_graph(
    organization_id: UUID = Query(...),
    case_id: UUID | None = Query(None),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Build a lightweight graph of cases, linked precedents, policies and outcomes."""
    cases_q = (
        supabase.table("exception_cases")
        .select("id, case_number, title, status, category_id, current_recommendation_id")
        .eq("organization_id", str(organization_id))
        .order("created_at", desc=True)
        .limit(40)
    )
    if case_id:
        cases_q = cases_q.eq("id", str(case_id))
    cases = cases_q.execute().data or []
    case_ids = [row["id"] for row in cases]

    nodes = [
        {
            "id": row["id"],
            "type": "current_request" if str(row["id"]) == str(case_id) else "historical_case",
            "label": row.get("case_number") or row.get("title") or row["id"],
            "data": row,
        }
        for row in cases
    ]
    edges: list[dict] = []

    if case_ids:
        links = (
            supabase.table("precedent_links")
            .select("*")
            .in_("case_id", case_ids)
            .order("similarity_score", desc=True)
            .limit(100)
            .execute()
            .data
            or []
        )
        existing_nodes = {node["id"] for node in nodes}
        for link in links:
            precedent_id = link.get("precedent_case_id") or link.get("id")
            if precedent_id and precedent_id not in existing_nodes:
                nodes.append({
                    "id": precedent_id,
                    "type": "historical_case",
                    "label": f"Precedent {str(precedent_id)[:8]}",
                    "data": {"source": "precedent_links"},
                })
                existing_nodes.add(precedent_id)
            if precedent_id:
                edges.append({
                    "id": link.get("id"),
                    "source": link.get("case_id"),
                    "target": precedent_id,
                    "type": "similar_exception",
                    "label": f"{link.get('similarity_score', 0)} similarity",
                    "data": link,
                })

    return DataResponse(data={"nodes": nodes, "edges": edges})


@router.post("/ask")
async def ask_precedent_memory(
    payload: dict = Body(...),
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Answer 'what would we usually do?' using Hindsight recall when configured."""
    question = payload.get("question") or ""
    org = OrganizationRepository(supabase).get_by_id(organization_id)
    bank_id = org.get("hindsight_bank_id", "") if org else ""
    memories = []
    if bank_id and len(question) >= 3:
        memories = await RecallService(get_hindsight_client()).recall_all(bank_id, question, top_k=8)

    recent = (
        supabase.table("exception_cases")
        .select("id, case_number, title, status, requested_amount, currency")
        .eq("organization_id", str(organization_id))
        .order("created_at", desc=True)
        .limit(20)
        .execute()
        .data
        or []
    )
    status_counts: dict[str, int] = {}
    for row in recent:
        status_counts[row.get("status", "unknown")] = status_counts.get(row.get("status", "unknown"), 0) + 1
    most_common = max(status_counts, key=status_counts.get) if status_counts else "insufficient_history"

    if memories:
        answer = "Similar memories were found in Hindsight. Review the supporting cases before deciding."
    elif recent:
        answer = "No Hindsight recall was available, so this is based on recent transactional cases."
    else:
        answer = "No precedent history is available for this organization yet."

    return DataResponse(data={
        "answer": answer,
        "distribution_of_decisions": status_counts,
        "most_common_resolution": most_common,
        "supporting_cases": recent[:5],
        "important_exceptions": [],
        "hindsight_evidence": memories,
    })


@router.get("/contradictions")
async def precedent_contradictions(
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Detect simple conflicting decision patterns in recent cases."""
    rows = (
        supabase.table("exception_cases")
        .select("id, case_number, title, entity_name, status, category_id, updated_at")
        .eq("organization_id", str(organization_id))
        .in_("status", ["approved", "partially_approved", "denied", "rejected"])
        .order("updated_at", desc=True)
        .limit(200)
        .execute()
        .data
        or []
    )
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        key = f"{row.get('entity_name') or 'unknown'}::{row.get('category_id') or 'general'}"
        grouped.setdefault(key, []).append(row)

    contradictions = []
    for key, cases in grouped.items():
        statuses = {case.get("status") for case in cases}
        has_approval = bool(statuses & {"approved", "partially_approved"})
        has_denial = bool(statuses & {"denied", "rejected"})
        if len(cases) >= 2 and has_approval and has_denial:
            contradictions.append({
                "id": key,
                "conflict_summary": "Similar cases have both approvals and denials.",
                "sources": cases[:6],
                "dates": [case.get("updated_at") for case in cases if case.get("updated_at")],
                "reliability": "medium",
                "suggested_authoritative_source": "Review current policy version and latest successful outcome.",
                "resolution_action": "Escalate to policy admin for precedent clarification.",
                "unresolved": True,
            })

    return DataResponse(data=contradictions)
