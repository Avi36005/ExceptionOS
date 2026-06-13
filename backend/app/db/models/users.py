from __future__ import annotations
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ProfileRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    display_name: str | None = None
    avatar_url: str | None = None
    timezone: str | None = None
    created_at: datetime


class MembershipRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    organization_id: UUID
    user_id: UUID
    role: str
    department_id: UUID | None = None
    status: str = "active"
    invited_by: UUID | None = None
    joined_at: datetime | None = None
