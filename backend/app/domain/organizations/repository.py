"""Repository for organisations (Supabase data access)."""
from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4
from datetime import datetime

from supabase import Client
import structlog

logger = structlog.get_logger(__name__)


class OrganizationRepository:
    def __init__(self, supabase: Client):
        self.db = supabase

    def list(self, page: int = 1, page_size: int = 20) -> tuple[list[dict], int]:
        offset = (page - 1) * page_size
        resp = (
            self.db.table("organizations")
            .select("*", count="exact")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        return resp.data or [], resp.count or 0

    def get_by_id(self, org_id: UUID) -> dict | None:
        resp = (
            self.db.table("organizations")
            .select("*")
            .eq("id", str(org_id))
            .maybe_single()
            .execute()
        )
        return resp.data

    def get_by_slug(self, slug: str) -> dict | None:
        resp = (
            self.db.table("organizations")
            .select("*")
            .eq("slug", slug)
            .maybe_single()
            .execute()
        )
        return resp.data

    def create(self, data: dict[str, Any]) -> dict:
        org_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        row = {
            "id": org_id,
            "status": "active",
            "created_at": now,
            "updated_at": now,
            **data,
        }
        resp = self.db.table("organizations").insert(row).execute()
        return resp.data[0]

    def update(self, org_id: UUID, data: dict[str, Any]) -> dict | None:
        data["updated_at"] = datetime.utcnow().isoformat()
        resp = (
            self.db.table("organizations")
            .update(data)
            .eq("id", str(org_id))
            .execute()
        )
        return resp.data[0] if resp.data else None

    def delete(self, org_id: UUID) -> bool:
        resp = (
            self.db.table("organizations")
            .update({"status": "suspended", "updated_at": datetime.utcnow().isoformat()})
            .eq("id", str(org_id))
            .execute()
        )
        return bool(resp.data)
