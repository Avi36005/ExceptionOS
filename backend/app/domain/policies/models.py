"""Domain models for policies."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Policy:
    id: UUID
    organization_id: UUID
    name: str
    category: str | None
    status: str

    @classmethod
    def from_row(cls, row: dict) -> "Policy":
        return cls(
            id=UUID(row["id"]),
            organization_id=UUID(row["organization_id"]),
            name=row.get("name", ""),
            category=row.get("category"),
            status=row.get("status", "draft"),
        )
