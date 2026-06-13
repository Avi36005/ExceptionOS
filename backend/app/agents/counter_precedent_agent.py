"""Counter-precedent agent — finds opposing precedents that argue against the recommendation."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.llm.provider_router import ProviderRouter

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a devil's advocate analyst for ExceptionOS.
Given the current recommendation direction and precedents, find counter-arguments and opposing precedents.
Respond with valid JSON only."""

OUTPUT_SCHEMA = """{
  "counter_arguments": [
    {
      "argument": "string",
      "strength": "weak|moderate|strong",
      "counter_precedent_reference": "string or null"
    }
  ],
  "risk_of_current_direction": "string",
  "alternative_recommendation": "approve|deny|partially_approve|escalate",
  "alternative_amount": "number or null",
  "alternative_reasoning": "string",
  "slippery_slope_risk": "low|medium|high",
  "slippery_slope_description": "string or null"
}"""


class CounterPrecedentAgent:
    def __init__(self, router: ProviderRouter):
        self.router = router
        self.name = "counter_precedent_agent"

    async def run(
        self,
        case_id: UUID,
        case_facts: dict[str, Any],
        current_direction: str,
        precedent_output: dict[str, Any],
        finance_output: dict[str, Any],
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
                    f"Financial analysis:\n{finance_output}\n\n"
                    f"Find counter-arguments. Return JSON: {OUTPUT_SCHEMA}"
                ),
            },
        ]

        result = await self.router.complete_json(
            messages, temperature=0.2, demo_mode=demo_mode
        )
        parsed = result.get("parsed", {})

        logger.info(
            "counter_precedent_agent_done",
            case_id=str(case_id),
            provider=result.get("final_provider"),
            alternative=parsed.get("alternative_recommendation"),
        )
        return {
            "agent": self.name,
            "provider": result.get("final_provider"),
            "usage": result.get("usage").to_dict() if result.get("usage") else {},
            "output": parsed,
        }
