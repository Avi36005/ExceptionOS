"""Service layer for policies."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog
from fastapi import HTTPException, status

from app.domain.policies.repository import PolicyRepository
from app.schemas import PolicyCreate, PolicyUpdate

logger = structlog.get_logger(__name__)


class PolicyService:
    def __init__(self, repo: PolicyRepository):
        self.repo = repo

    def list_policies(self, organization_id: UUID, page: int, page_size: int) -> tuple[list[dict], int]:
        return self.repo.list(organization_id, page, page_size)

    def get_policy(self, policy_id: UUID, organization_id: UUID) -> dict:
        policy = self.repo.get_by_id(policy_id, organization_id)
        if not policy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
        return policy

    def create_policy(self, organization_id: UUID, payload: PolicyCreate, created_by: str | None) -> dict:
        data = payload.model_dump(exclude={"content", "effective_from"})
        effective_from = payload.effective_from.isoformat() if payload.effective_from else None
        return self.repo.create(organization_id, data, payload.content, created_by, effective_from)

    def update_policy(self, policy_id: UUID, organization_id: UUID, payload: PolicyUpdate) -> dict:
        self.get_policy(policy_id, organization_id)
        data = {k: v for k, v in payload.model_dump().items() if v is not None}
        if "status" in data:
            data["status"] = data["status"].value if hasattr(data["status"], "value") else data["status"]
        updated = self.repo.update(policy_id, organization_id, data)
        if not updated:
            raise HTTPException(status_code=500, detail="Update failed")
        return self.get_policy(policy_id, organization_id)
