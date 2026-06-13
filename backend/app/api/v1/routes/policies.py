"""Policy CRUD routes."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from supabase import Client

from app.dependencies import get_current_user, get_supabase
from app.domain.policies.repository import PolicyRepository
from app.domain.policies.service import PolicyService
from app.schemas import DataResponse, PaginationMeta, PolicyCreate, PolicyUpdate

router = APIRouter(prefix="/policies", tags=["policies"])


def _get_service(supabase: Client = Depends(get_supabase)) -> PolicyService:
    return PolicyService(PolicyRepository(supabase))


@router.get("/")
async def list_policies(
    organization_id: UUID = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    service: PolicyService = Depends(_get_service),
) -> DataResponse:
    policies, total = service.list_policies(organization_id, page, page_size)
    pages = (total + page_size - 1) // page_size
    return DataResponse(
        data=policies,
        meta=PaginationMeta(total=total, page=page, page_size=page_size, pages=pages).model_dump(),
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_policy(
    payload: PolicyCreate,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: PolicyService = Depends(_get_service),
) -> DataResponse:
    policy = service.create_policy(organization_id, payload, current_user.get("sub"))
    return DataResponse(data=policy)


@router.get("/{policy_id}")
async def get_policy(
    policy_id: UUID,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: PolicyService = Depends(_get_service),
) -> DataResponse:
    policy = service.get_policy(policy_id, organization_id)
    return DataResponse(data=policy)


@router.patch("/{policy_id}")
async def update_policy(
    policy_id: UUID,
    payload: PolicyUpdate,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: PolicyService = Depends(_get_service),
) -> DataResponse:
    policy = service.update_policy(policy_id, organization_id, payload)
    return DataResponse(data=policy)


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_policy(
    policy_id: UUID,
    organization_id: UUID = Query(...),
    current_user: dict = Depends(get_current_user),
    service: PolicyService = Depends(_get_service),
) -> None:
    service.update_policy(policy_id, organization_id, PolicyUpdate(status="archived"))
