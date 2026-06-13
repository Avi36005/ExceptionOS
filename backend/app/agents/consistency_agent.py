"""Consistency agent — checks whether the emerging recommendation is consistent with policy and precedent."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.llm.provider_router import ProviderRouter

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a consistency and fairness analyst for ExceptionOS.
Check whether the emerging recommendation is consistent with past decisions and policy.
Respond with valid JSON only."""

OUTPUT_SCHEMA = """{
  "consistency_score": "0.0-1.0",
  "is_consistent": true,
  "inconsistencies": [
    {
      "description": "string",
      "severity": "minor|moderate|major"
    }
  ],
  "fairness_assessment": "fair|unfair|borderline",
  "similar_case_outcomes": "string — brief summary of what similar cases resulted in",
  "consistency_verdict": "proceed|flag_for_review|escalate",
  "consistency_reasoning": "string"
}"""


class ConsistencyAgent:
    def __init__(self, router: ProviderRouter):
        self.router = router
        self.name = "consistency_agent"

    async def run(
        self,
        case_id: UUID,
        case_facts: dict[str, Any],
        precedent_output: dict[str, Any],
        policy_output: dict[str, Any],
        current_direction: str,
        demo_mode: bool = False,
    ) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Case facts:\n{case_facts}\n\n"
                    f"Current recommendation direction: {current_direction}\n\n"
                    f"Precedent analysis:\n{precedent_output}\n\n"
                    f"Policy analysis:\n{policy_output}\n\n"
                    f"Check consistency. Return JSON: {OUTPUT_SCHEMA}"
                ),
            },
        ]

        result = await self.router.complete_json(
            messages, temperature=0.1, demo_mode=demo_mode
        )
        parsed = result.get("parsed", {})

        logger.info(
            "consistency_agent_done",
            case_id=str(case_id),
            provider=result.get("final_provider"),
            score=parsed.get("consistency_score"),
            verdict=parsed.get("consistency_verdict"),
        )
        return {
            "agent": self.name,
            "provider": result.get("final_provider"),
            "usage": result.get("usage").to_dict() if result.get("usage") else {},
            "output": parsed,
            "fallback_path": result.get("fallback_path", []),
        }
