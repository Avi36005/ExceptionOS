from __future__ import annotations
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class OutcomeRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID
    decision_id: UUID | None = None
    actual_outcome: str
    outcome_date: datetime | None = None
    financial_impact: float | None = None
    notes: str | None = None
    recorded_by: UUID
    created_at: datetime
