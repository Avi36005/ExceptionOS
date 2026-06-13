"""Precedent search and retrieval routes."""
from __future__ import annotations

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Query
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
