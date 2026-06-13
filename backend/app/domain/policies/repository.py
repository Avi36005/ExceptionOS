"""Repository for policies."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from supabase import Client
import structlog

logger = structlog.get_logger(__name__)


class PolicyRepository:
    def __init__(self, supabase: Client):
        self.db = supabase

    def list(self, organization_id: UUID, page: int = 1, page_size: int = 20) -> tuple[list[dict], int]:
        offset = (page - 1) * page_size
        resp = (
            self.db.table("policies")
            .select("*, policy_versions(*)", count="exact")
            .eq("organization_id", str(organization_id))
            .neq("status", "archived")
            .order("name")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        return resp.data or [], resp.count or 0

    def get_by_id(self, policy_id: UUID, organization_id: UUID) -> dict | None:
        resp = (
            self.db.table("policies")
            .select("*, policy_versions(*)")
            .eq("id", str(policy_id))
            .eq("organization_id", str(organization_id))
            .maybe_single()
            .execute()
        )
        return resp.data

    def create(self, organization_id: UUID, data: dict[str, Any], content: str, created_by: str | None, effective_from: str | None) -> dict:
        policy_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        policy_row = {
            "id": policy_id,
            "organization_id": str(organization_id),
            "status": "active",
            **{k: v for k, v in data.items() if k not in ("content", "effective_from")},
        }
        self.db.table("policies").insert(policy_row).execute()

        # Create initial version
        version_id = str(uuid4())
        self.db.table("policy_versions").insert({
            "id": version_id,
            "policy_id": policy_id,
            "version_label": "v1.0",
            "content": content,
            "effective_from": effective_from or now,
            "status": "active",
            "created_by": created_by,
            "created_at": now,
        }).execute()

        return self.get_by_id(UUID(policy_id), organization_id) or {}

    def update(self, policy_id: UUID, organization_id: UUID, data: dict[str, Any]) -> dict | None:
        resp = (
            self.db.table("policies")
            .update(data)
            .eq("id", str(policy_id))
            .eq("organization_id", str(organization_id))
            .execute()
        )
        return resp.data[0] if resp.data else None

    def get_active_content(self, organization_id: UUID) -> tuple[str, str]:
        """Return (content, name) of the most relevant active policy."""
        resp = (
            self.db.table("policies")
            .select("name, policy_versions(content, status)")
            .eq("organization_id", str(organization_id))
            .eq("status", "active")
            .limit(1)
            .execute()
        )
        if resp.data:
            policy = resp.data[0]
            versions = [v for v in (policy.get("policy_versions") or []) if v.get("status") == "active"]
            if versions:
                return versions[0]["content"], policy["name"]
        return "", "No Policy"
