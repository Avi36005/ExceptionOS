from __future__ import annotations
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class HumanDecisionRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID
    recommendation_id: UUID | None = None
    decision_type: str
    approved_amount: float | None = None
    conditions_json: str = "[]"
    reasoning: str = ""
    override: bool = False
    decided_by: UUID
    decided_at: datetime
