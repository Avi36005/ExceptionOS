"""Domain models for exception cases."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ExceptionCase:
    id: UUID
    organization_id: UUID
    case_number: str
    title: str
    description: str | None
    entity_name: str | None
    requested_amount: float | None
    currency: str
    urgency: str
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "ExceptionCase":
        return cls(
            id=UUID(row["id"]),
            organization_id=UUID(row["organization_id"]),
            case_number=row.get("case_number", ""),
            title=row.get("title", ""),
            description=row.get("description"),
            entity_name=row.get("entity_name"),
            requested_amount=row.get("requested_amount"),
            currency=row.get("currency", "USD"),
            urgency=row.get("urgency", "medium"),
            status=row.get("status", "draft"),
            created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else datetime.utcnow(),
        )
