"""Outcome recording routes."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.dependencies import get_current_user, get_supabase
from app.schemas import DataResponse

router = APIRouter(prefix="/outcomes", tags=["outcomes"])


@router.get("/")
async def list_outcomes(
    organization_id: UUID = Query(...),
    case_id: UUID | None = Query(None),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    q = supabase.table("outcomes").select("*")
    if case_id:
        q = q.eq("case_id", str(case_id))
    resp = q.order("created_at", desc=True).limit(100).execute()
    return DataResponse(data=resp.data or [])


@router.get("/{outcome_id}")
async def get_outcome(
    outcome_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    resp = (
        supabase.table("outcomes")
        .select("*")
        .eq("id", str(outcome_id))
        .maybe_single()
        .execute()
    )
    if not resp.data:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Outcome not found")
    return DataResponse(data=resp.data)
