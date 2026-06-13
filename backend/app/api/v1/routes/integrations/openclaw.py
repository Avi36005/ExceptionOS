"""OpenClaw integration routes.

This module is ONLY activated when ENABLE_OPENCLAW=true.
It is completely isolated from core business logic.
"""
from __future__ import annotations

import json
from datetime import datetime
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from supabase import Client

from app.config import get_settings
from app.dependencies import get_current_user, get_supabase
from app.schemas import DataResponse, MessageResponse

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/integrations/openclaw", tags=["openclaw"])


def _check_enabled() -> None:
    settings = get_settings()
    if not settings.ENABLE_OPENCLAW:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenClaw integration is disabled. Set ENABLE_OPENCLAW=true to enable.",
        )


class OpenClawWebhookPayload(BaseModel):
    event_type: str
    session_id: str
    channel: str = "chat"
    action_type: str | None = None
    payload: dict = {}
    organization_slug: str | None = None


@router.get("/status")
async def openclaw_status(
    current_user: dict = Depends(get_current_user),
) -> DataResponse:
    """Return the OpenClaw integration status."""
    settings = get_settings()
    return DataResponse(data={
        "enabled": settings.ENABLE_OPENCLAW,
        "status": "active" if settings.ENABLE_OPENCLAW else "disabled",
    })


@router.post("/webhook")
async def openclaw_webhook(
    request: Request,
    x_openclaw_signature: str | None = Header(None),
    supabase: Client = Depends(get_supabase),
) -> MessageResponse:
    """Receive webhook events from OpenClaw."""
    _check_enabled()

    body = await request.body()
    try:
        data = json.loads(body)
        payload = OpenClawWebhookPayload(**data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {exc}") from exc

    # Look up organisation by slug if provided
    org_id: str | None = None
    if payload.organization_slug:
        resp = (
            supabase.table("organizations")
            .select("id")
            .eq("slug", payload.organization_slug)
            .maybe_single()
            .execute()
        )
        if resp.data:
            org_id = resp.data["id"]

    # Persist session
    session_row = {
        "id": str(uuid4()),
        "organization_id": org_id,
        "external_session_id": payload.session_id,
        "channel": payload.channel,
        "action_type": payload.action_type,
        "status": "active",
        "metadata_json": json.dumps(payload.payload),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    supabase.table("openclaw_sessions").insert(session_row).execute()

    logger.info(
        "openclaw_webhook_received",
        event_type=payload.event_type,
        session_id=payload.session_id,
        org_id=org_id,
    )

    # Handle specific event types
    if payload.event_type == "exception_request":
        return await _handle_exception_request(payload, org_id, supabase)

    return MessageResponse(message="Webhook received", data={"session_id": payload.session_id})


async def _handle_exception_request(
    payload: OpenClawWebhookPayload,
    org_id: str | None,
    supabase: Client,
) -> MessageResponse:
    """Auto-create a case from an OpenClaw exception request."""
    if not org_id:
        return MessageResponse(
            message="Organisation not found — case not created",
            data={"session_id": payload.session_id},
        )

    from app.domain.exceptions.repository import ExceptionCaseRepository
    from uuid import UUID

    data = payload.payload
    case_id = str(uuid4())
    now = datetime.utcnow().isoformat()
    supabase.table("exception_cases").insert({
        "id": case_id,
        "organization_id": org_id,
        "case_number": f"OCL-{case_id[:8].upper()}",
        "title": data.get("title", f"OpenClaw Exception — {payload.session_id}"),
        "description": data.get("description", ""),
        "entity_name": data.get("entity_name"),
        "requested_amount": data.get("requested_amount"),
        "urgency": data.get("urgency", "medium"),
        "status": "submitted",
        "version": 1,
        "created_at": now,
        "updated_at": now,
    }).execute()

    # Update session with linked case
    supabase.table("openclaw_sessions").update({
        "linked_case_id": case_id,
        "updated_at": now,
    }).eq("external_session_id", payload.session_id).execute()

    return MessageResponse(
        message="Exception case created from OpenClaw",
        data={"case_id": case_id, "session_id": payload.session_id},
    )


@router.post("/disable")
async def disable_openclaw(
    current_user: dict = Depends(get_current_user),
) -> MessageResponse:
    """Disable the OpenClaw integration (informational — requires env var change)."""
    return MessageResponse(
        message="To disable OpenClaw, set ENABLE_OPENCLAW=false in your environment and restart.",
        data={"current_status": "enabled" if get_settings().ENABLE_OPENCLAW else "disabled"},
    )
