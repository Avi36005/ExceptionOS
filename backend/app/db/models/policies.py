from __future__ import annotations
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class PolicyRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    name: str
    category: str | None = None
    status: str = "draft"
    owner_user_id: UUID | None = None


class PolicyVersionRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    policy_id: UUID
    version_label: str
    content: str
    effective_from: datetime | None = None
    effective_to: datetime | None = None
    status: str = "draft"
    created_by: UUID | None = None
    approved_by: UUID | None = None
    hindsight_document_id: str | None = None
    created_at: datetime
