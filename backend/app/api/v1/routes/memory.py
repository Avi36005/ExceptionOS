"""Memory (Hindsight Retain / Recall / Reflect) endpoints."""
from __future__ import annotations

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from app.dependencies import get_current_user, get_supabase
from app.domain.organizations.repository import OrganizationRepository
from app.memory.hindsight_client import get_hindsight_client
from app.memory.recall_service import RecallService
from app.memory.reflect_service import ReflectService
from app.memory.retain_service import RetainService
from app.schemas import DataResponse, RecallRequest, ReflectRequest, RetainRequest

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/memory", tags=["memory"])


async def _get_bank_id(organization_id: UUID, supabase: Client) -> str:
    org = OrganizationRepository(supabase).get_by_id(organization_id)
    bank_id = org.get("hindsight_bank_id", "") if org else ""
    if not bank_id:
        raise HTTPException(status_code=400, detail="No Hindsight bank configured for this organisation")
    return bank_id


@router.post("/retain")
async def retain_memory(
    payload: RetainRequest,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    bank_id = await _get_bank_id(organization_id, supabase)
    hindsight = get_hindsight_client()
    service = RetainService(hindsight)
    meta = dict(payload.metadata)
    if payload.case_id:
        meta["case_id"] = str(payload.case_id)
    meta["user_id"] = current_user.get("sub", "")
    result = await service.retain_raw(bank_id, payload.content, meta)
    return DataResponse(data=result)


@router.post("/recall")
async def recall_memory(
    payload: RecallRequest,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    bank_id = await _get_bank_id(organization_id, supabase)
    hindsight = get_hindsight_client()
    service = RecallService(hindsight)
    memories = await service.recall_all(bank_id, payload.query, top_k=payload.top_k)
    return DataResponse(data={"memories": memories, "total": len(memories)})


@router.post("/reflect")
async def reflect_memory(
    payload: ReflectRequest,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    bank_id = await _get_bank_id(organization_id, supabase)
    hindsight = get_hindsight_client()
    service = ReflectService(hindsight)
    result = await service.reflect_on_topic(bank_id, payload.topic)
    return DataResponse(data=result)
