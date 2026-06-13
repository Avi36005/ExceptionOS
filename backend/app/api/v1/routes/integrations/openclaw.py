"""OpenClaw integration routes.

OpenClaw is an OPTIONAL bonus integration for ExceptionOS (see
"OpenClaw Integration Guidelines"). It is disabled by default
(``ENABLE_OPENCLAW=false``) and the core ExceptionOS platform must work
completely without it.

This module is intentionally tightly scoped:
    - ONE optional inbound webhook (HMAC-signature verified)
    - ONE optional DB table (``openclaw_sessions``, defined in
      ``migrations/001_initial.sql``)
    - ONE frontend route (``/app/integrations/openclaw``)

OpenClaw may only be used as an optional conversational channel for:
    1. Creating a DRAFT exception through chat
    2. Asking "have we allowed this before?" (Hindsight-backed recall)
    3. Listing pending approvals
    4. Requesting missing outcome information
    5. A short daily exception briefing

OpenClaw must NEVER approve, reject, or modify a final decision. Any
high-impact action request is rejected with a message redirecting the user
to the ExceptionOS web application.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from supabase import Client

from app.config import Settings, get_settings
from app.dependencies import get_current_user, get_supabase, require_org_member
from app.domain.organizations.repository import OrganizationRepository
from app.memory.hindsight_client import get_hindsight_client
from app.memory.recall_service import RecallService
from app.schemas import DataResponse, MessageResponse

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/integrations/openclaw", tags=["openclaw"])


# ---------------------------------------------------------------------------
# Allowed conversational actions (per OpenClaw Integration Guidelines)
# ---------------------------------------------------------------------------

ALLOWED_ACTION_TYPES = {
    "create_draft_case",
    "check_precedent",
    "list_pending_approvals",
    "request_outcome_info",
    "daily_briefing",
}

# Action types that would touch a final decision — explicitly rejected.
DECISION_ACTION_TYPES = {
    "approve_case",
    "reject_case",
    "deny_case",
    "modify_decision",
    "override_decision",
    "escalate_case",
    "approve",
    "reject",
    "deny",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _effective_status(settings: Settings, org: dict | None) -> tuple[bool, str]:
    """Return (enabled, connection_status) for the given org.

    The integration is enabled only when the global ``ENABLE_OPENCLAW`` flag
    is on AND (if an org is known) that org has not opted out via
    ``organizations.openclaw_enabled``.
    """
    if not settings.ENABLE_OPENCLAW:
        return False, "disabled"

    if org is not None and org.get("openclaw_enabled") is False:
        return False, "disabled"

    if not settings.OPENCLAW_WEBHOOK_SECRET:
        # Enabled, but the webhook channel is not fully configured yet.
        return True, "configured_no_secret"

    return True, "connected"


def _verify_signature(secret: str, raw_body: bytes, signature: str | None) -> bool:
    """Verify an ``X-OpenClaw-Signature`` header (HMAC-SHA256 hex digest of
    the raw request body, using ``OPENCLAW_WEBHOOK_SECRET``)."""
    if not secret or not signature:
        return False
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    # Support an optional "sha256=" prefix, mirroring common webhook conventions.
    provided = signature.strip()
    if provided.lower().startswith("sha256="):
        provided = provided[7:]
    return hmac.compare_digest(expected, provided)


async def _get_org_and_bank(organization_id: str | None, supabase: Client) -> tuple[dict | None, str | None]:
    if not organization_id:
        return None, None
    org = OrganizationRepository(supabase).get_by_id(UUID(organization_id))
    bank_id = org.get("hindsight_bank_id") if org else None
    return org, bank_id


def _log_session(
    supabase: Client,
    *,
    organization_id: str | None,
    external_session_id: str,
    channel: str,
    action_type: str | None,
    status_value: str,
    linked_case_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """Insert (or update) a row in ``openclaw_sessions`` for audit logging.

    Per the guidelines, ``openclaw_sessions`` is the ONE optional table and we
    do not store full conversation transcripts — only a small metadata
    summary of the requested action and its outcome.
    """
    now = _now()
    row = {
        "id": str(uuid4()),
        "organization_id": organization_id,
        "external_session_id": external_session_id,
        "channel": channel,
        "linked_case_id": linked_case_id,
        "action_type": action_type,
        "status": status_value,
        "metadata_json": json.dumps(metadata or {}),
        "created_at": now,
        "updated_at": now,
    }
    try:
        resp = supabase.table("openclaw_sessions").insert(row).execute()
        return resp.data[0] if resp.data else row
    except Exception as exc:  # pragma: no cover - logging must never crash the webhook
        logger.warning("openclaw_session_log_failed", error=str(exc))
        return row


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class OpenClawWebhookPayload(BaseModel):
    """Inbound payload from the optional OpenClaw conversational channel."""

    session_id: str = Field(..., description="External (OpenClaw-side) session identifier")
    organization_id: str | None = Field(None, description="ExceptionOS organisation UUID")
    organization_slug: str | None = Field(None, description="ExceptionOS organisation slug (alternative to organization_id)")
    channel: str = Field("chat", description="Conversational channel, e.g. 'chat', 'slack', 'voice'")
    action_type: str = Field(..., description="One of the allowed OpenClaw conversational actions")
    user_id: str | None = Field(None, description="ExceptionOS user UUID associated with this session, if known")
    data: dict[str, Any] = Field(default_factory=dict, description="Action-specific payload")


# ---------------------------------------------------------------------------
# GET /integrations/openclaw/status
# ---------------------------------------------------------------------------

@router.get("/status")
async def openclaw_status(
    organization_id: UUID | None = Query(None),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
    settings: Settings = Depends(get_settings),
) -> DataResponse:
    """Return the OpenClaw integration status.

    Never errors when OpenClaw is disabled — the core system must continue
    running normally regardless of this endpoint's result.
    """
    org: dict | None = None
    if organization_id is not None:
        try:
            org = OrganizationRepository(supabase).get_by_id(organization_id)
        except Exception as exc:
            logger.warning("openclaw_status_org_lookup_failed", error=str(exc))

    enabled, connection_status = _effective_status(settings, org)
    configured = bool(settings.ENABLE_OPENCLAW and settings.OPENCLAW_WEBHOOK_SECRET)

    if not settings.ENABLE_OPENCLAW:
        message = "Integration not enabled. Set ENABLE_OPENCLAW=true to enable this optional bonus integration."
    elif org is not None and org.get("openclaw_enabled") is False:
        message = "OpenClaw has been disabled for this organisation."
    elif not settings.OPENCLAW_WEBHOOK_SECRET:
        message = "OpenClaw is enabled but OPENCLAW_WEBHOOK_SECRET is not configured — the webhook is inactive."
    else:
        message = "OpenClaw is enabled and the webhook is configured."

    return DataResponse(data={
        "enabled": enabled,
        "global_enabled": settings.ENABLE_OPENCLAW,
        "configured": configured,
        "connection_status": connection_status,
        "message": message,
        "allowed_actions": sorted(ALLOWED_ACTION_TYPES),
    })


# ---------------------------------------------------------------------------
# GET /integrations/openclaw/sessions
# ---------------------------------------------------------------------------

@router.get("/sessions")
async def list_openclaw_sessions(
    organization_id: UUID = Query(...),
    limit: int = Query(20, ge=1, le=100),
    member: dict = Depends(require_org_member),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Return the most recent OpenClaw sessions for the organisation."""
    resp = (
        supabase.table("openclaw_sessions")
        .select("*")
        .eq("organization_id", str(organization_id))
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return DataResponse(data=resp.data or [])


# ---------------------------------------------------------------------------
# GET /integrations/openclaw/draft-cases
# ---------------------------------------------------------------------------

@router.get("/draft-cases")
async def list_openclaw_draft_cases(
    organization_id: UUID = Query(...),
    limit: int = Query(20, ge=1, le=100),
    member: dict = Depends(require_org_member),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Return draft exception cases created through the OpenClaw channel."""
    resp = (
        supabase.table("exception_cases")
        .select("id,case_number,title,status,source,urgency,requested_amount,currency,created_at")
        .eq("organization_id", str(organization_id))
        .eq("source", "openclaw")
        .eq("status", "draft")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return DataResponse(data=resp.data or [])


# ---------------------------------------------------------------------------
# POST /integrations/openclaw/disable
# ---------------------------------------------------------------------------

@router.post("/disable")
async def disable_openclaw(
    organization_id: UUID = Query(...),
    member: dict = Depends(require_org_member),
    supabase: Client = Depends(get_supabase),
    settings: Settings = Depends(get_settings),
) -> MessageResponse:
    """Disable OpenClaw for this organisation.

    ``ENABLE_OPENCLAW`` is a global env var, so this sets a per-organisation
    override (``organizations.openclaw_enabled = false``) which is checked in
    addition to the global flag. The integration can be re-enabled by an org
    admin updating that flag (or, if disabled globally, by an operator
    setting ``ENABLE_OPENCLAW=true``).
    """
    if member.get("org_role") not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

    supabase.table("organizations").update({
        "openclaw_enabled": False,
        "updated_at": _now(),
    }).eq("id", str(organization_id)).execute()

    logger.info("openclaw_disabled_for_org", organization_id=str(organization_id))

    return MessageResponse(
        message="OpenClaw has been disabled for this organisation.",
        data={"organization_id": str(organization_id), "enabled": False},
    )


# ---------------------------------------------------------------------------
# POST /integrations/openclaw/webhook
# ---------------------------------------------------------------------------

@router.post("/webhook")
async def openclaw_webhook(
    request: Request,
    x_openclaw_signature: str | None = Header(None, alias="X-OpenClaw-Signature"),
    settings: Settings = Depends(get_settings),
    supabase: Client = Depends(get_supabase),
) -> MessageResponse:
    """Optional inbound webhook for the OpenClaw conversational channel.

    Rejects (401) when OpenClaw is disabled globally, or when the
    ``X-OpenClaw-Signature`` HMAC-SHA256 signature is missing/invalid.
    """
    if not settings.ENABLE_OPENCLAW:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OpenClaw integration is not enabled")

    raw_body = await request.body()

    if not _verify_signature(settings.OPENCLAW_WEBHOOK_SECRET, raw_body, x_openclaw_signature):
        logger.warning("openclaw_webhook_invalid_signature")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing webhook signature")

    try:
        payload = OpenClawWebhookPayload(**json.loads(raw_body))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid payload: {exc}") from exc

    # Resolve organisation
    org: dict | None = None
    org_id = payload.organization_id
    if org_id:
        org = OrganizationRepository(supabase).get_by_id(UUID(org_id))
    elif payload.organization_slug:
        org = OrganizationRepository(supabase).get_by_slug(payload.organization_slug)
        if org:
            org_id = org["id"]

    enabled, _ = _effective_status(settings, org)
    if not enabled:
        _log_session(
            supabase,
            organization_id=org_id,
            external_session_id=payload.session_id,
            channel=payload.channel,
            action_type=payload.action_type,
            status_value="error",
            metadata={"reason": "openclaw_disabled_for_org"},
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OpenClaw is disabled for this organisation")

    if not org_id:
        _log_session(
            supabase,
            organization_id=None,
            external_session_id=payload.session_id,
            channel=payload.channel,
            action_type=payload.action_type,
            status_value="error",
            metadata={"reason": "organization_not_found"},
        )
        return MessageResponse(
            message="Could not resolve an ExceptionOS organisation for this session.",
            data={"session_id": payload.session_id, "status": "error"},
        )

    # Explicitly refuse anything that touches a final decision.
    if payload.action_type in DECISION_ACTION_TYPES:
        _log_session(
            supabase,
            organization_id=org_id,
            external_session_id=payload.session_id,
            channel=payload.channel,
            action_type=payload.action_type,
            status_value="rejected",
            metadata={"reason": "decision_actions_not_allowed"},
        )
        return MessageResponse(
            message=(
                "OpenClaw cannot approve, reject, or modify decisions. "
                "Please open the ExceptionOS web application to review and confirm this action."
            ),
            data={"session_id": payload.session_id, "status": "redirect_to_web_app"},
        )

    if payload.action_type not in ALLOWED_ACTION_TYPES:
        _log_session(
            supabase,
            organization_id=org_id,
            external_session_id=payload.session_id,
            channel=payload.channel,
            action_type=payload.action_type,
            status_value="rejected",
            metadata={"reason": "unsupported_action_type"},
        )
        return MessageResponse(
            message=f"Unsupported action_type '{payload.action_type}'.",
            data={"session_id": payload.session_id, "status": "rejected", "allowed_actions": sorted(ALLOWED_ACTION_TYPES)},
        )

    handler = _ACTION_HANDLERS[payload.action_type]
    try:
        result = await handler(payload, org_id, supabase)
    except Exception as exc:
        logger.error("openclaw_handler_failed", action_type=payload.action_type, error=str(exc))
        _log_session(
            supabase,
            organization_id=org_id,
            external_session_id=payload.session_id,
            channel=payload.channel,
            action_type=payload.action_type,
            status_value="error",
            metadata={"error": str(exc)},
        )
        return MessageResponse(
            message="OpenClaw could not complete this request right now.",
            data={"session_id": payload.session_id, "status": "error"},
        )

    _log_session(
        supabase,
        organization_id=org_id,
        external_session_id=payload.session_id,
        channel=payload.channel,
        action_type=payload.action_type,
        status_value="completed",
        linked_case_id=result.get("linked_case_id"),
        metadata=result.get("metadata", {}),
    )

    return MessageResponse(message=result["message"], data={"session_id": payload.session_id, **result.get("data", {})})


# ---------------------------------------------------------------------------
# Action handlers — the 5 allowed conversational uses
# ---------------------------------------------------------------------------

async def _handle_create_draft_case(payload: OpenClawWebhookPayload, org_id: str, supabase: Client) -> dict:
    """1. Create a DRAFT exception via chat.

    Always creates the case with ``status='draft'`` and ``source='openclaw'``
    so it shows up under "Draft cases created through OpenClaw" and requires
    a human to open the web app to actually submit/process it.
    """
    data = payload.data or {}
    case_id = str(uuid4())
    now = _now()
    short = case_id[:8].upper()

    row = {
        "id": case_id,
        "organization_id": org_id,
        "case_number": f"OCL-{short}",
        "title": data.get("title") or "Exception drafted via OpenClaw",
        "description": data.get("description", ""),
        "entity_name": data.get("entity_name"),
        "requested_amount": data.get("requested_amount"),
        "currency": data.get("currency", "USD"),
        "urgency": data.get("urgency", "medium"),
        "status": "draft",
        "source": "openclaw",
        "version": 1,
        "created_at": now,
        "updated_at": now,
    }
    if payload.user_id:
        row["requester_user_id"] = payload.user_id

    resp = supabase.table("exception_cases").insert(row).execute()
    created = resp.data[0] if resp.data else row

    return {
        "message": (
            f"Draft exception {created.get('case_number', row['case_number'])} created. "
            "Open ExceptionOS to review and submit it."
        ),
        "data": {"case_id": case_id, "case_number": row["case_number"]},
        "linked_case_id": case_id,
        "metadata": {"case_number": row["case_number"]},
    }


async def _handle_check_precedent(payload: OpenClawWebhookPayload, org_id: str, supabase: Client) -> dict:
    """2. "Have we allowed this before?" — answer using Hindsight recall."""
    data = payload.data or {}
    query = data.get("query") or data.get("description") or ""
    if not query:
        return {
            "message": "Please describe the exception you're asking about (e.g. amount, vendor, reason).",
            "data": {"precedents": []},
            "metadata": {"reason": "missing_query"},
        }

    org, bank_id = await _get_org_and_bank(org_id, supabase)
    if not bank_id:
        return {
            "message": "No precedent memory bank is configured for this organisation yet.",
            "data": {"precedents": []},
            "metadata": {"reason": "no_bank_configured"},
        }

    recall = RecallService(get_hindsight_client())
    structured = await recall.recall_structured(
        bank_id,
        case_description=query,
        entity_name=data.get("entity_name"),
        top_k=5,
        raise_on_error=False,
    )
    precedents = structured.get("precedents", [])

    if not precedents:
        message = "I couldn't find a similar past exception in our memory."
    else:
        top = precedents[0]
        meta = top.get("metadata", {}) or {}
        decision = meta.get("decision_type") or meta.get("outcome") or "a decision"
        message = (
            f"Yes — we found {len(precedents)} similar case(s). "
            f"The closest precedent resulted in: {decision}. "
            "Open ExceptionOS for full details."
        )

    summarized = [
        {
            "score": m.get("score"),
            "content": (m.get("content") or "")[:280],
            "metadata": m.get("metadata", {}),
        }
        for m in precedents[:5]
    ]

    return {
        "message": message,
        "data": {"precedents": summarized, "count": len(precedents)},
        "metadata": {"query": query, "result_count": len(precedents)},
    }


async def _handle_list_pending_approvals(payload: OpenClawWebhookPayload, org_id: str, supabase: Client) -> dict:
    """3. Show pending approval reminders."""
    resp = (
        supabase.table("exception_cases")
        .select("id,case_number,title,status,urgency,requested_amount,currency,created_at")
        .eq("organization_id", org_id)
        .in_("status", ["pending_decision", "submitted", "analyzing"])
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    cases = resp.data or []

    if not cases:
        message = "There are no exception cases pending a decision right now."
    else:
        lines = ", ".join(f"{c['case_number']} ({c.get('title', 'untitled')})" for c in cases[:5])
        message = f"There are {len(cases)} case(s) awaiting a decision: {lines}. Open ExceptionOS to review and decide."

    return {
        "message": message,
        "data": {"pending_cases": cases, "count": len(cases)},
        "metadata": {"count": len(cases)},
    }


async def _handle_request_outcome_info(payload: OpenClawWebhookPayload, org_id: str, supabase: Client) -> dict:
    """4. Request missing outcome information.

    Finds approved/partially-approved/denied cases that have been resolved
    but do not yet have a row in ``outcomes``.
    """
    resp = (
        supabase.table("exception_cases")
        .select("id,case_number,title,status,resolved_at")
        .eq("organization_id", org_id)
        .in_("status", ["approved", "partially_approved", "denied", "closed"])
        .order("resolved_at", desc=True)
        .limit(50)
        .execute()
    )
    resolved_cases = resp.data or []
    if not resolved_cases:
        return {
            "message": "There are no resolved cases yet that need an outcome recorded.",
            "data": {"missing_outcomes": []},
            "metadata": {"count": 0},
        }

    case_ids = [c["id"] for c in resolved_cases]
    outcomes_resp = (
        supabase.table("outcomes")
        .select("case_id")
        .in_("case_id", case_ids)
        .execute()
    )
    cases_with_outcomes = {row["case_id"] for row in (outcomes_resp.data or [])}

    missing = [c for c in resolved_cases if c["id"] not in cases_with_outcomes][:10]

    if not missing:
        message = "All resolved cases already have an outcome recorded. Nice work!"
    else:
        lines = ", ".join(f"{c['case_number']} ({c.get('title', 'untitled')})" for c in missing[:5])
        message = (
            f"{len(missing)} resolved case(s) are missing outcome information: {lines}. "
            "Please record the outcome in ExceptionOS."
        )

    return {
        "message": message,
        "data": {"missing_outcomes": missing, "count": len(missing)},
        "metadata": {"count": len(missing)},
    }


async def _handle_daily_briefing(payload: OpenClawWebhookPayload, org_id: str, supabase: Client) -> dict:
    """5. Short daily exception briefing — simple aggregate counts."""
    today_start = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00+00:00")

    new_resp = (
        supabase.table("exception_cases")
        .select("id", count="exact")
        .eq("organization_id", org_id)
        .gte("created_at", today_start)
        .execute()
    )
    pending_resp = (
        supabase.table("exception_cases")
        .select("id", count="exact")
        .eq("organization_id", org_id)
        .in_("status", ["pending_decision", "submitted", "analyzing"])
        .execute()
    )
    escalated_resp = (
        supabase.table("exception_cases")
        .select("id", count="exact")
        .eq("organization_id", org_id)
        .eq("status", "escalated")
        .execute()
    )
    resolved_today_resp = (
        supabase.table("exception_cases")
        .select("id", count="exact")
        .eq("organization_id", org_id)
        .in_("status", ["approved", "partially_approved", "denied", "closed"])
        .gte("resolved_at", today_start)
        .execute()
    )

    new_count = new_resp.count or 0
    pending_count = pending_resp.count or 0
    escalated_count = escalated_resp.count or 0
    resolved_count = resolved_today_resp.count or 0

    message = (
        f"Daily briefing: {new_count} new exception(s) today, "
        f"{pending_count} awaiting a decision, "
        f"{escalated_count} escalated, "
        f"{resolved_count} resolved today."
    )

    return {
        "message": message,
        "data": {
            "new_today": new_count,
            "pending_decision": pending_count,
            "escalated": escalated_count,
            "resolved_today": resolved_count,
        },
        "metadata": {
            "new_today": new_count,
            "pending_decision": pending_count,
            "escalated": escalated_count,
            "resolved_today": resolved_count,
        },
    }


_ACTION_HANDLERS = {
    "create_draft_case": _handle_create_draft_case,
    "check_precedent": _handle_check_precedent,
    "list_pending_approvals": _handle_list_pending_approvals,
    "request_outcome_info": _handle_request_outcome_info,
    "daily_briefing": _handle_daily_briefing,
}
