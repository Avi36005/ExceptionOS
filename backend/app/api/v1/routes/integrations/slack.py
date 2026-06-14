"""Slack outbound notifications via an Incoming Webhook (optional integration).

Sends exception/approval/decision alerts to a Slack channel. Configured by
``SLACK_WEBHOOK_URL``; if unset, the integration reports as not connected and
never breaks the core app.
"""
from __future__ import annotations

import httpx
import structlog
from fastapi import APIRouter, Body, Depends

from app.config import Settings, get_settings
from app.dependencies import get_current_user
from app.schemas import DataResponse

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/integrations/slack", tags=["integrations"])


async def _post_to_slack(webhook_url: str, text: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(webhook_url, json={"text": text})
            return resp.status_code == 200
    except Exception as exc:  # noqa: BLE001
        logger.warning("slack_post_failed", error=str(exc))
        return False


def _format(payload: dict) -> str:
    """Build a Slack message from a structured event, or use raw text."""
    if payload.get("text"):
        return str(payload["text"])
    event = (payload.get("event") or "update").lower()
    cid = payload.get("case_id", "")
    customer = payload.get("customer", "")
    title = payload.get("title", "")
    amount = payload.get("amount", "")
    actor = payload.get("actor", "")
    head = {
        "submitted": ":new: New exception submitted",
        "approval_needed": ":hourglass_flowing_sand: Exception awaiting approval",
        "approved": ":white_check_mark: Exception approved",
        "rejected": ":x: Exception rejected",
        "recommendation": ":robot_face: AI recommendation ready",
    }.get(event, ":bell: Exception update")
    line = f"*{cid}* — {customer}: {title}".strip(" —:")
    extra = " ".join(p for p in [f"({amount})" if amount else "", f"· {actor}" if actor else ""] if p)
    return f"{head}\n{line} {extra}".strip()


@router.get("/status")
async def slack_status(settings: Settings = Depends(get_settings)) -> DataResponse:
    connected = bool(settings.SLACK_WEBHOOK_URL)
    return DataResponse(data={
        "connected": connected,
        "message": "Slack is connected." if connected else "Set SLACK_WEBHOOK_URL to enable Slack notifications.",
    })


@router.post("/test")
async def slack_test(
    settings: Settings = Depends(get_settings),
    current_user: dict = Depends(get_current_user),
) -> DataResponse:
    if not settings.SLACK_WEBHOOK_URL:
        return DataResponse(data={"sent": False, "message": "Slack not configured."})
    ok = await _post_to_slack(
        settings.SLACK_WEBHOOK_URL,
        ":satellite_antenna: *ExceptionOS test* — Slack notifications are working. "
        "You'll receive exception alerts here.",
    )
    return DataResponse(data={"sent": ok, "message": "Test message sent." if ok else "Slack send failed."})


@router.post("/notify")
async def slack_notify(
    payload: dict = Body(...),
    settings: Settings = Depends(get_settings),
    current_user: dict = Depends(get_current_user),
) -> DataResponse:
    if not settings.SLACK_WEBHOOK_URL:
        return DataResponse(data={"sent": False, "message": "Slack not configured."})
    ok = await _post_to_slack(settings.SLACK_WEBHOOK_URL, _format(payload))
    return DataResponse(data={"sent": ok})
