"""Human decision recording routes."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.dependencies import get_current_user, get_supabase
from app.schemas import DataResponse

router = APIRouter(prefix="/decisions", tags=["decisions"])


@router.get("/")
async def list_decisions(
    organization_id: UUID = Query(...),
    case_id: UUID | None = Query(None),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    q = supabase.table("human_decisions").select("*")
    if case_id:
        q = q.eq("case_id", str(case_id))
    resp = q.order("decided_at", desc=True).limit(100).execute()
    return DataResponse(data=resp.data or [])


@router.get("/{decision_id}")
async def get_decision(
    decision_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    resp = (
        supabase.table("human_decisions")
        .select("*")
        .eq("id", str(decision_id))
        .maybe_single()
        .execute()
    )
    if not resp.data:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Decision not found")
    return DataResponse(data=resp.data)
