"""Organisation CRUD routes."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from supabase import Client

from app.dependencies import get_current_user, get_supabase
from app.domain.organizations.repository import OrganizationRepository
from app.domain.organizations.service import OrganizationService
from app.memory.bank_manager import BankManager
from app.memory.hindsight_client import get_hindsight_client
from app.schemas import (
    DataResponse,
    MessageResponse,
    OrganizationCreate,
    OrganizationUpdate,
    PaginationMeta,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


def _get_service(supabase: Client = Depends(get_supabase)) -> OrganizationService:
    hindsight = get_hindsight_client()
    repo = OrganizationRepository(supabase)
    bank_mgr = BankManager(supabase, hindsight)
    return OrganizationService(repo, bank_mgr)


@router.get("/")
async def list_organizations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    service: OrganizationService = Depends(_get_service),
) -> DataResponse:
    orgs, total = service.list_organizations(page, page_size)
    pages = (total + page_size - 1) // page_size
    return DataResponse(
        data=orgs,
        meta=PaginationMeta(total=total, page=page, page_size=page_size, pages=pages).model_dump(),
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreate,
    current_user: dict = Depends(get_current_user),
    service: OrganizationService = Depends(_get_service),
) -> DataResponse:
    org = await service.create_organization(payload)
    return DataResponse(data=org)


@router.get("/{organization_id}")
async def get_organization(
    organization_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: OrganizationService = Depends(_get_service),
) -> DataResponse:
    org = service.get_organization(organization_id)
    return DataResponse(data=org)


@router.patch("/{organization_id}")
async def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    current_user: dict = Depends(get_current_user),
    service: OrganizationService = Depends(_get_service),
) -> DataResponse:
    org = service.update_organization(organization_id, payload)
    return DataResponse(data=org)


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_organization(
    organization_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: OrganizationService = Depends(_get_service),
) -> None:
    service.delete_organization(organization_id)
