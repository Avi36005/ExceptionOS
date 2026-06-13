from __future__ import annotations
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ExceptionCaseRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    case_number: str
    category_id: UUID | None = None
    department_id: UUID | None = None
    requester_user_id: UUID | None = None
    assignee_user_id: UUID | None = None
    title: str
    description: str | None = None
    entity_name: str | None = None
    requested_amount: float | None = None
    currency: str = "USD"
    annual_value: float | None = None
    request_date: datetime | None = None
    transaction_date: datetime | None = None
    root_cause: str | None = None
    urgency: str = "medium"
    status: str = "draft"
    current_policy_version_id: UUID | None = None
    current_recommendation_id: UUID | None = None
    sla_due_at: datetime | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    version: int = 1
