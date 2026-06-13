"""Service for storing memories to Hindsight."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.memory.hindsight_client import HindsightClient
from app.memory.operation_logger import OperationLogContext

logger = structlog.get_logger(__name__)


class RetainService:
    def __init__(self, hindsight: HindsightClient):
        self.hindsight = hindsight

    async def retain_case_decision(
        self,
        bank_id: str,
        case_id: UUID,
        case_title: str,
        decision_type: str,
        reasoning: str,
        outcome: str | None = None,
        metadata: dict[str, Any] | None = None,
        document_id: str | None = None,
        log_ctx: OperationLogContext | None = None,
    ) -> dict[str, Any]:
        """Retain a case decision memory."""
        content = (
            f"Case: {case_title}\n"
            f"Decision: {decision_type}\n"
            f"Reasoning: {reasoning}"
        )
        if outcome:
            content += f"\nOutcome: {outcome}"

        meta: dict[str, Any] = {
            "type": "case_decision",
            "case_id": str(case_id),
            "decision_type": decision_type,
        }
        if metadata:
            meta.update(metadata)

        return await self.hindsight.retain(bank_id, content, meta, document_id=document_id, log_ctx=log_ctx)

    async def retain_policy_note(
        self,
        bank_id: str,
        policy_id: UUID,
        policy_name: str,
        note: str,
        metadata: dict[str, Any] | None = None,
        document_id: str | None = None,
        log_ctx: OperationLogContext | None = None,
    ) -> dict[str, Any]:
        """Retain a policy interpretation or amendment note."""
        content = f"Policy: {policy_name}\nNote: {note}"
        meta: dict[str, Any] = {
            "type": "policy_note",
            "policy_id": str(policy_id),
        }
        if metadata:
            meta.update(metadata)
        return await self.hindsight.retain(bank_id, content, meta, document_id=document_id, log_ctx=log_ctx)

    async def retain_outcome(
        self,
        bank_id: str,
        case_id: UUID,
        case_title: str,
        actual_outcome: str,
        financial_impact: float | None,
        notes: str | None,
        document_id: str | None = None,
        log_ctx: OperationLogContext | None = None,
    ) -> dict[str, Any]:
        """Retain an observed outcome for learning."""
        content = (
            f"Case: {case_title}\n"
            f"Actual Outcome: {actual_outcome}\n"
        )
        if financial_impact is not None:
            content += f"Financial Impact: {financial_impact}\n"
        if notes:
            content += f"Notes: {notes}"

        meta: dict[str, Any] = {
            "type": "outcome",
            "case_id": str(case_id),
        }
        return await self.hindsight.retain(bank_id, content, meta, document_id=document_id, log_ctx=log_ctx)

    async def retain_raw(
        self,
        bank_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        document_id: str | None = None,
        log_ctx: OperationLogContext | None = None,
    ) -> dict[str, Any]:
        """Retain arbitrary content."""
        return await self.hindsight.retain(bank_id, content, metadata or {}, document_id=document_id, log_ctx=log_ctx)
