"""Service for retrieving relevant memories from Hindsight."""
from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

import structlog

from app.memory.hindsight_client import HindsightClient
from app.memory.operation_logger import OperationLogContext

logger = structlog.get_logger(__name__)


def dedupe_and_rank(memories: list[dict[str, Any]], top_k: int | None = None) -> list[dict[str, Any]]:
    """Deduplicate recalled memories (by ``document_id`` or memory ``id``) and
    rank by descending score.

    When multiple Hindsight queries return the same logical memory, keep the
    copy with the highest score.
    """
    best: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for mem in memories:
        meta = mem.get("metadata", {}) or {}
        key = meta.get("document_id") or mem.get("id") or repr(mem.get("content", ""))[:120]
        score = mem.get("score", 0.0) or 0.0
        existing = best.get(key)
        if existing is None:
            best[key] = mem
            order.append(key)
        elif score > (existing.get("score", 0.0) or 0.0):
            best[key] = mem

    ranked = sorted((best[key] for key in order), key=lambda m: m.get("score", 0.0) or 0.0, reverse=True)
    if top_k is not None:
        ranked = ranked[:top_k]
    return ranked


class RecallService:
    def __init__(self, hindsight: HindsightClient):
        self.hindsight = hindsight

    async def recall_precedents(
        self,
        bank_id: str,
        case_description: str,
        entity_name: str | None = None,
        top_k: int = 10,
        log_ctx: OperationLogContext | None = None,
    ) -> list[dict[str, Any]]:
        """Recall precedent cases similar to the current case."""
        query = case_description
        if entity_name:
            query = f"{entity_name}: {query}"
        memories = await self.hindsight.recall(
            bank_id, query, top_k=top_k, metadata_filter={"type": "case_decision"}, log_ctx=log_ctx
        )
        logger.info(
            "recalled_precedents",
            bank_id=bank_id,
            count=len(memories),
        )
        return dedupe_and_rank(memories, top_k=top_k)

    async def recall_policy_context(
        self,
        bank_id: str,
        policy_name: str,
        context: str,
        top_k: int = 5,
        log_ctx: OperationLogContext | None = None,
    ) -> list[dict[str, Any]]:
        """Recall policy-related notes."""
        query = f"Policy '{policy_name}': {context}"
        memories = await self.hindsight.recall(
            bank_id, query, top_k=top_k, metadata_filter={"type": "policy_note"}, log_ctx=log_ctx
        )
        return dedupe_and_rank(memories, top_k=top_k)

    async def recall_outcomes(
        self,
        bank_id: str,
        query: str,
        top_k: int = 5,
        log_ctx: OperationLogContext | None = None,
    ) -> list[dict[str, Any]]:
        """Recall historical outcomes."""
        memories = await self.hindsight.recall(
            bank_id, query, top_k=top_k, metadata_filter={"type": "outcome"}, log_ctx=log_ctx
        )
        return dedupe_and_rank(memories, top_k=top_k)

    async def recall_all(
        self,
        bank_id: str,
        query: str,
        top_k: int = 10,
        log_ctx: OperationLogContext | None = None,
    ) -> list[dict[str, Any]]:
        """Recall all types of memories matching the query."""
        memories = await self.hindsight.recall(bank_id, query, top_k=top_k, log_ctx=log_ctx)
        return dedupe_and_rank(memories, top_k=top_k)

    async def recall_structured(
        self,
        bank_id: str,
        case_description: str,
        entity_name: str | None = None,
        policy_name: str | None = None,
        top_k: int = 10,
        log_ctx: OperationLogContext | None = None,
        raise_on_error: bool = True,
    ) -> dict[str, Any]:
        """Recall precedents, outcomes, outcome lessons, and policy notes in
        parallel for a case, returning each bucket deduped/ranked plus a
        combined, deduped/ranked ``merged`` list and a list of per-bucket
        ``errors`` (when ``raise_on_error`` is True, e.g. for callers that
        want to surface OPERATION_FAILED events).

        Used to build the Hindsight evidence view for a case and to feed the
        precedent agent.
        """
        query = case_description
        if entity_name:
            query = f"{entity_name}: {query}"

        tasks = {
            "precedents": self.hindsight.recall(
                bank_id, query, top_k=top_k, metadata_filter={"type": "case_decision"},
                log_ctx=log_ctx, raise_on_error=raise_on_error,
            ),
            "outcomes": self.hindsight.recall(
                bank_id, query, top_k=top_k, metadata_filter={"type": "outcome"},
                log_ctx=log_ctx, raise_on_error=raise_on_error,
            ),
            "outcome_lessons": self.hindsight.recall(
                bank_id, query, top_k=top_k, metadata_filter={"type": "outcome_lesson"},
                log_ctx=log_ctx, raise_on_error=raise_on_error,
            ),
        }
        if policy_name:
            tasks["policy_notes"] = self.hindsight.recall(
                bank_id,
                f"Policy '{policy_name}': {case_description}",
                top_k=top_k,
                metadata_filter={"type": "policy_note"},
                log_ctx=log_ctx,
                raise_on_error=raise_on_error,
            )

        keys = list(tasks.keys())
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        buckets: dict[str, list[dict[str, Any]]] = {}
        errors: list[dict[str, str]] = []
        all_memories: list[dict[str, Any]] = []
        for key, result in zip(keys, results):
            if isinstance(result, Exception):
                logger.warning("recall_structured_bucket_failed", bucket=key, error=str(result))
                buckets[key] = []
                errors.append({"bucket": key, "error": str(result)})
                continue
            ranked = dedupe_and_rank(result, top_k=top_k)
            buckets[key] = ranked
            all_memories.extend(result)

        buckets["merged"] = dedupe_and_rank(all_memories, top_k=top_k)
        buckets["errors"] = errors
        return buckets
