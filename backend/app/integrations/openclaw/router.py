"""OpenClaw webhook and session management logic (domain layer).

This module contains business logic independent of FastAPI routing.
"""
from __future__ import annotations

import json
from datetime import datetime
from uuid import UUID, uuid4

import structlog
from supabase import Client

logger = structlog.get_logger(__name__)


class OpenClawRouter:
    """Handles incoming OpenClaw events and translates them to ExceptionOS actions."""

    def __init__(self, supabase: Client):
        self.supabase = supabase

    def get_or_create_session(
        self,
        external_session_id: str,
        organization_id: str | None,
        channel: str,
        metadata: dict,
    ) -> dict:
        resp = (
            self.supabase.table("openclaw_sessions")
            .select("*")
            .eq("external_session_id", external_session_id)
            .maybe_single()
            .execute()
        )
        if resp.data:
            return resp.data

        session_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        row = {
            "id": session_id,
            "organization_id": organization_id,
            "external_session_id": external_session_id,
            "channel": channel,
            "status": "active",
            "metadata_json": json.dumps(metadata),
            "created_at": now,
            "updated_at": now,
        }
        resp = self.supabase.table("openclaw_sessions").insert(row).execute()
        return resp.data[0]

    def link_case(self, external_session_id: str, case_id: str) -> None:
        self.supabase.table("openclaw_sessions").update({
            "linked_case_id": case_id,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("external_session_id", external_session_id).execute()

    def close_session(self, external_session_id: str) -> None:
        self.supabase.table("openclaw_sessions").update({
            "status": "closed",
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("external_session_id", external_session_id).execute()

    def get_active_sessions(self, organization_id: str) -> list[dict]:
        resp = (
            self.supabase.table("openclaw_sessions")
            .select("*")
            .eq("organization_id", organization_id)
            .eq("status", "active")
            .order("created_at", desc=True)
            .execute()
        )
        return resp.data or []
