"""AI recommendation endpoints."""
from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.dependencies import get_current_user, get_supabase
from app.schemas import DataResponse

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/")
async def list_recommendations(
    organization_id: UUID = Query(...),
    case_id: UUID | None = Query(None),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    q = supabase.table("recommendations").select("*")
    if case_id:
        q = q.eq("case_id", str(case_id))
    resp = q.order("created_at", desc=True).limit(100).execute()
    data = resp.data or []

    # Deserialise JSON columns
    for rec in data:
        for col in ("conditions_json", "risk_json", "provider_summary_json", "hindsight_evidence_json"):
            if rec.get(col):
                try:
                    rec[col.replace("_json", "")] = json.loads(rec[col])
                except Exception:
                    pass
    return DataResponse(data=data)


@router.get("/{recommendation_id}")
async def get_recommendation(
    recommendation_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    resp = (
        supabase.table("recommendations")
        .select("*")
        .eq("id", str(recommendation_id))
        .maybe_single()
        .execute()
    )
    if not resp.data:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Recommendation not found")
    rec = resp.data
    for col in ("conditions_json", "risk_json", "provider_summary_json", "hindsight_evidence_json"):
        if rec.get(col):
            try:
                rec[col.replace("_json", "")] = json.loads(rec[col])
            except Exception:
                pass
    return DataResponse(data=rec)
