"""Persist Hindsight Retain/Recall/Reflect operation logs to ``hindsight_operations``."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

import structlog
from supabase import Client

logger = structlog.get_logger(__name__)


@dataclass
class OperationLogContext:
    """Context needed to log a Hindsight operation against a case/run."""

    supabase: Client
    organization_id: UUID | str
    case_id: UUID | str | None = None
    agent_run_id: UUID | str | None = None


def log_hindsight_operation(
    ctx: OperationLogContext | None,
    *,
    operation_type: str,
    bank_id: str,
    status: str,
    document_id: str | None = None,
    request_json: dict[str, Any] | None = None,
    response_json: dict[str, Any] | None = None,
    latency_ms: int | None = None,
    error_message: str | None = None,
) -> None:
    """Write one row to ``hindsight_operations``. No-op if ``ctx`` is None.

    Failures to log are swallowed (logged at warning) so they never break the
    underlying memory operation.
    """
    if ctx is None:
        return
    try:
        ctx.supabase.table("hindsight_operations").insert(
            {
                "id": str(uuid4()),
                "organization_id": str(ctx.organization_id),
                "case_id": str(ctx.case_id) if ctx.case_id else None,
                "agent_run_id": str(ctx.agent_run_id) if ctx.agent_run_id else None,
                "operation_type": operation_type,
                "document_id": document_id,
                "bank_id": bank_id,
                "status": status,
                "request_json": json.dumps(request_json or {}, default=str),
                "response_json": json.dumps(response_json or {}, default=str),
                "latency_ms": latency_ms,
                "error_message": error_message,
            }
        ).execute()
    except Exception as exc:  # pragma: no cover - logging must never break the caller
        logger.warning("hindsight_operation_log_failed", error=str(exc), operation_type=operation_type)
