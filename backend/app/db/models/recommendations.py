from __future__ import annotations
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class RecommendationRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID
    version: int = 1
    recommendation_type: str
    recommended_amount: float | None = None
    conditions_json: str = "[]"
    confidence: float = 0.5
    reasoning: str = ""
    risk_json: str = "{}"
    provider_summary_json: str = "{}"
    hindsight_evidence_json: str = "[]"
    created_at: datetime
