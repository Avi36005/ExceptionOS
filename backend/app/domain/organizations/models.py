"""Domain models for organisations."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class Organization:
    id: UUID
    name: str
    slug: str
    industry: str | None
    size: str | None
    currency: str
    timezone: str
    status: str
    hindsight_bank_id: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "Organization":
        return cls(
            id=UUID(row["id"]),
            name=row["name"],
            slug=row["slug"],
            industry=row.get("industry"),
            size=row.get("size"),
            currency=row.get("currency", "USD"),
            timezone=row.get("timezone", "UTC"),
            status=row.get("status", "active"),
            hindsight_bank_id=row.get("hindsight_bank_id"),
            created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else datetime.utcnow(),
        )
