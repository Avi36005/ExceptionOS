"""Outcome learning agent — records outcome data to Hindsight for future learning."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.llm.provider_router import ProviderRouter
from app.memory.hindsight_client import HindsightClient

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a learning and improvement agent for ExceptionOS.
Analyse the outcome of a decision and extract lessons for future cases.
Respond with valid JSON only."""

OUTPUT_SCHEMA = """{
  "lesson_summary": "string — concise lesson learned",
  "decision_quality": "excellent|good|acceptable|poor",
  "prediction_accuracy": "accurate|partially_accurate|inaccurate",
  "key_lessons": ["list of strings"],
  "policy_update_suggestions": ["list of strings or null"],
  "memory_content": "string — content to store in Hindsight",
  "memory_tags": ["list of strings"]
}"""


class OutcomeLearningAgent:
    def __init__(self, router: ProviderRouter, hindsight: HindsightClient):
        self.router = router
        self.hindsight = hindsight
        self.name = "outcome_learning_agent"

    async def run(
        self,
        case_id: UUID,
        bank_id: str,
        case_facts: dict[str, Any],
        recommendation: dict[str, Any],
        human_decision: dict[str, Any],
        actual_outcome: dict[str, Any],
        demo_mode: bool = False,
    ) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Case facts:\n{case_facts}\n\n"
                    f"AI recommendation:\n{recommendation}\n\n"
                    f"Human decision:\n{human_decision}\n\n"
                    f"Actual outcome:\n{actual_outcome}\n\n"
                    f"Extract lessons. Return JSON: {OUTPUT_SCHEMA}"
                ),
            },
        ]

        result = await self.router.complete_json(
            messages, temperature=0.2, demo_mode=demo_mode
        )
        parsed = result.get("parsed", {})

        # Store in Hindsight
        memory_content = parsed.get("memory_content", "")
        if memory_content and bank_id:
            try:
                await self.hindsight.retain(
                    bank_id=bank_id,
                    content=memory_content,
                    metadata={
                        "type": "outcome_lesson",
                        "case_id": str(case_id),
                        "decision_type": human_decision.get("decision_type", ""),
                        "tags": parsed.get("memory_tags", []),
                    },
                )
            except Exception as exc:
                logger.error(
                    "outcome_learning_retain_failed",
                    case_id=str(case_id),
                    error=str(exc),
                )

        logger.info(
            "outcome_learning_agent_done",
            case_id=str(case_id),
            provider=result.get("final_provider"),
            quality=parsed.get("decision_quality"),
        )
        return {
            "agent": self.name,
            "provider": result.get("final_provider"),
            "usage": result.get("usage").to_dict() if result.get("usage") else {},
            "output": parsed,
        }
