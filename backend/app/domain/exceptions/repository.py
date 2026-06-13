"""Repository for exception cases."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import structlog
from supabase import Client

logger = structlog.get_logger(__name__)


def _generate_case_number(org_slug: str = "EXC") -> str:
    from datetime import datetime
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    short = str(uuid4())[:4].upper()
    return f"{org_slug.upper()[:3]}-{ts}-{short}"


class ExceptionCaseRepository:
    def __init__(self, supabase: Client):
        self.db = supabase

    def list(
        self,
        organization_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status_filter: str | None = None,
    ) -> tuple[list[dict], int]:
        offset = (page - 1) * page_size
        q = (
            self.db.table("exception_cases")
            .select("*", count="exact")
            .eq("organization_id", str(organization_id))
            .order("created_at", desc=True)
            .range(offset, offset + page_size - 1)
        )
        if status_filter:
            q = q.eq("status", status_filter)
        resp = q.execute()
        return resp.data or [], resp.count or 0

    def get_by_id(self, case_id: UUID, organization_id: UUID) -> dict | None:
        resp = (
            self.db.table("exception_cases")
            .select("*")
            .eq("id", str(case_id))
            .eq("organization_id", str(organization_id))
            .maybe_single()
            .execute()
        )
        return resp.data

    def create(self, organization_id: UUID, data: dict[str, Any], requester_id: str | None = None) -> dict:
        case_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        case_number = _generate_case_number()
        row = {
            "id": case_id,
            "organization_id": str(organization_id),
            "case_number": case_number,
            "status": "draft",
            "version": 1,
            "created_at": now,
            "updated_at": now,
            **data,
        }
        if requester_id:
            row["requester_user_id"] = requester_id
        resp = self.db.table("exception_cases").insert(row).execute()
        return resp.data[0]

    def update(self, case_id: UUID, organization_id: UUID, data: dict[str, Any]) -> dict | None:
        data["updated_at"] = datetime.utcnow().isoformat()
        resp = (
            self.db.table("exception_cases")
            .update(data)
            .eq("id", str(case_id))
            .eq("organization_id", str(organization_id))
            .execute()
        )
        return resp.data[0] if resp.data else None

    def get_facts(self, case_id: UUID) -> list[dict]:
        resp = (
            self.db.table("case_facts")
            .select("*")
            .eq("case_id", str(case_id))
            .execute()
        )
        return resp.data or []

    def save_facts(self, case_id: UUID, facts: list[dict[str, Any]]) -> None:
        # Delete old facts
        self.db.table("case_facts").delete().eq("case_id", str(case_id)).execute()
        rows = []
        for f in facts:
            rows.append({
                "id": str(uuid4()),
                "case_id": str(case_id),
                "key": f.get("key", ""),
                "value_json": json.dumps(f.get("value", f.get("value_json", ""))),
                "source": f.get("source", "intake_agent"),
                "confidence": f.get("confidence", 0.8),
                "verified": False,
                "created_at": datetime.utcnow().isoformat(),
            })
        if rows:
            self.db.table("case_facts").insert(rows).execute()

    def get_recommendation(self, case_id: UUID) -> dict | None:
        resp = (
            self.db.table("recommendations")
            .select("*")
            .eq("case_id", str(case_id))
            .order("version", desc=True)
            .limit(1)
            .execute()
        )
        return resp.data[0] if resp.data else None

    def get_decisions(self, case_id: UUID) -> list[dict]:
        resp = (
            self.db.table("human_decisions")
            .select("*")
            .eq("case_id", str(case_id))
            .order("decided_at", desc=True)
            .execute()
        )
        return resp.data or []

    def save_decision(self, case_id: UUID, data: dict[str, Any], decided_by: str) -> dict:
        decision_id = str(uuid4())
        row = {
            "id": decision_id,
            "case_id": str(case_id),
            "decided_by": decided_by,
            "decided_at": datetime.utcnow().isoformat(),
            **data,
        }
        resp = self.db.table("human_decisions").insert(row).execute()
        return resp.data[0]

    def get_outcome(self, case_id: UUID) -> dict | None:
        resp = (
            self.db.table("outcomes")
            .select("*")
            .eq("case_id", str(case_id))
            .maybe_single()
            .execute()
        )
        return resp.data

    def save_outcome(self, case_id: UUID, data: dict[str, Any], recorded_by: str) -> dict:
        outcome_id = str(uuid4())
        row = {
            "id": outcome_id,
            "case_id": str(case_id),
            "recorded_by": recorded_by,
            "created_at": datetime.utcnow().isoformat(),
            **data,
        }
        resp = self.db.table("outcomes").insert(row).execute()
        return resp.data[0]

    def get_audit_events(self, case_id: UUID) -> list[dict]:
        resp = (
            self.db.table("case_events")
            .select("*")
            .eq("case_id", str(case_id))
            .order("created_at")
            .execute()
        )
        return resp.data or []

    def add_event(self, case_id: UUID, organization_id: UUID, event_type: str, actor_type: str, actor_id: str, payload: dict) -> None:
        self.db.table("case_events").insert({
            "id": str(uuid4()),
            "case_id": str(case_id),
            "organization_id": str(organization_id),
            "event_type": event_type,
            "actor_type": actor_type,
            "actor_id": actor_id,
            "payload_json": json.dumps(payload),
            "created_at": datetime.utcnow().isoformat(),
        }).execute()

    def get_precedent_links(self, case_id: UUID) -> list[dict]:
        resp = (
            self.db.table("precedent_links")
            .select("*")
            .eq("case_id", str(case_id))
            .order("similarity_score", desc=True)
            .execute()
        )
        return resp.data or []
