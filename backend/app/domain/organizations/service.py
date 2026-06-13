"""Service layer for organisations."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog
from fastapi import HTTPException, status

from app.domain.organizations.repository import OrganizationRepository
from app.memory.bank_manager import BankManager
from app.schemas import OrganizationCreate, OrganizationUpdate

logger = structlog.get_logger(__name__)


class OrganizationService:
    def __init__(self, repo: OrganizationRepository, bank_manager: BankManager):
        self.repo = repo
        self.bank_manager = bank_manager

    def list_organizations(self, page: int, page_size: int) -> tuple[list[dict], int]:
        return self.repo.list(page, page_size)

    def get_organization(self, org_id: UUID) -> dict:
        org = self.repo.get_by_id(org_id)
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
        return org

    async def create_organization(self, payload: OrganizationCreate) -> dict:
        # Check slug uniqueness
        existing = self.repo.get_by_slug(payload.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Organisation with slug '{payload.slug}' already exists",
            )
        data = payload.model_dump()
        org = self.repo.create(data)

        # Provision Hindsight bank asynchronously
        try:
            await self.bank_manager.get_or_create_bank(
                organization_id=UUID(org["id"]),
                org_name=org["name"],
            )
        except Exception as exc:
            logger.warning("hindsight_bank_provision_failed", org_id=org["id"], error=str(exc))

        return org

    def update_organization(self, org_id: UUID, payload: OrganizationUpdate) -> dict:
        self.get_organization(org_id)  # raises 404 if not found
        data = {k: v for k, v in payload.model_dump().items() if v is not None}
        updated = self.repo.update(org_id, data)
        if not updated:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Update failed")
        return updated

    def delete_organization(self, org_id: UUID) -> None:
        self.get_organization(org_id)
        self.repo.delete(org_id)
