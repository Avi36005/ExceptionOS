"""Service for retrieving relevant memories from Hindsight."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.memory.hindsight_client import HindsightClient

logger = structlog.get_logger(__name__)


class RecallService:
    def __init__(self, hindsight: HindsightClient):
        self.hindsight = hindsight

    async def recall_precedents(
        self,
        bank_id: str,
        case_description: str,
        entity_name: str | None = None,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Recall precedent cases similar to the current case."""
        query = case_description
        if entity_name:
            query = f"{entity_name}: {query}"
        memories = await self.hindsight.recall(
            bank_id, query, top_k=top_k, metadata_filter={"type": "case_decision"}
        )
        logger.info(
            "recalled_precedents",
            bank_id=bank_id,
            count=len(memories),
        )
        return memories

    async def recall_policy_context(
        self,
        bank_id: str,
        policy_name: str,
        context: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Recall policy-related notes."""
        query = f"Policy '{policy_name}': {context}"
        return await self.hindsight.recall(
            bank_id, query, top_k=top_k, metadata_filter={"type": "policy_note"}
        )

    async def recall_outcomes(
        self,
        bank_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Recall historical outcomes."""
        return await self.hindsight.recall(
            bank_id, query, top_k=top_k, metadata_filter={"type": "outcome"}
        )

    async def recall_all(
        self,
        bank_id: str,
        query: str,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Recall all types of memories matching the query."""
        return await self.hindsight.recall(bank_id, query, top_k=top_k)
