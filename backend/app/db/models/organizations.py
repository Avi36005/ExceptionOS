from __future__ import annotations
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class OrganizationRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    slug: str
    industry: str | None = None
    size: str | None = None
    currency: str = "USD"
    timezone: str = "UTC"
    status: str = "active"
    hindsight_bank_id: str | None = None
    created_at: datetime
    updated_at: datetime
