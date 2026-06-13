"""Service for reflection and pattern analysis using Hindsight."""
from __future__ import annotations

from typing import Any

import structlog

from app.memory.hindsight_client import HindsightClient
from app.memory.operation_logger import OperationLogContext

logger = structlog.get_logger(__name__)


class ReflectService:
    def __init__(self, hindsight: HindsightClient):
        self.hindsight = hindsight

    async def reflect_on_policy(
        self, bank_id: str, policy_name: str, log_ctx: OperationLogContext | None = None
    ) -> dict[str, Any]:
        """Reflect on patterns related to a policy."""
        topic = f"What patterns exist in decisions related to policy '{policy_name}'?"
        return await self.hindsight.reflect(bank_id, topic, log_ctx=log_ctx)

    async def reflect_on_entity(
        self, bank_id: str, entity_name: str, log_ctx: OperationLogContext | None = None
    ) -> dict[str, Any]:
        """Reflect on an entity's exception history."""
        topic = f"What is the history and pattern of exceptions for entity '{entity_name}'?"
        return await self.hindsight.reflect(bank_id, topic, log_ctx=log_ctx)

    async def reflect_on_drift(
        self, bank_id: str, log_ctx: OperationLogContext | None = None
    ) -> dict[str, Any]:
        """Reflect on policy drift patterns."""
        topic = (
            "Are there signs of policy drift? "
            "Identify cases where decisions deviated from stated policy, "
            "and whether those deviations are becoming the new norm."
        )
        return await self.hindsight.reflect(bank_id, topic, log_ctx=log_ctx)

    async def reflect_on_topic(
        self, bank_id: str, topic: str, log_ctx: OperationLogContext | None = None
    ) -> dict[str, Any]:
        """General reflection."""
        return await self.hindsight.reflect(bank_id, topic, log_ctx=log_ctx)
