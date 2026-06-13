"""Domain models for recommendations."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class Recommendation:
    id: UUID
    case_id: UUID
    version: int
    recommendation_type: str
    recommended_amount: float | None
    confidence: float
    reasoning: str
    conditions: list[str] = field(default_factory=list)
    risk: dict = field(default_factory=dict)

    @classmethod
    def from_row(cls, row: dict) -> "Recommendation":
        import json
        return cls(
            id=UUID(row["id"]),
            case_id=UUID(row["case_id"]),
            version=row.get("version", 1),
            recommendation_type=row.get("recommendation_type", "needs_more_info"),
            recommended_amount=row.get("recommended_amount"),
            confidence=row.get("confidence", 0.5),
            reasoning=row.get("reasoning", ""),
            conditions=json.loads(row["conditions_json"]) if row.get("conditions_json") else [],
            risk=json.loads(row["risk_json"]) if row.get("risk_json") else {},
        )
