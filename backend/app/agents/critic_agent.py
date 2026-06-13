"""Critic agent — critiques the emerging recommendation before final synthesis."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.llm.provider_router import ProviderRouter

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a critical reviewer for ExceptionOS recommendations.
Critique the recommendation thoroughly — identify weaknesses, missing considerations, and potential errors.
Respond with valid JSON only."""

OUTPUT_SCHEMA = """{
  "critique_summary": "string",
  "weaknesses": [
    {
      "issue": "string",
      "severity": "minor|moderate|major|critical",
      "suggested_fix": "string"
    }
  ],
  "missing_considerations": ["list of strings"],
  "confidence_assessment": "overconfident|appropriate|underconfident",
  "recommendation_quality": "poor|acceptable|good|excellent",
  "should_revise": true,
  "revision_notes": "string or null",
  "critic_score": "0.0-1.0"
}"""


class CriticAgent:
    def __init__(self, router: ProviderRouter):
        self.router = router
        self.name = "critic_agent"

    async def run(
        self,
        case_id: UUID,
        case_facts: dict[str, Any],
        all_agent_outputs: dict[str, Any],
        preliminary_recommendation: str,
        demo_mode: bool = False,
    ) -> dict[str, Any]:
        outputs_text = "\n\n".join(
            f"=== {agent_name} ===\n{output}"
            for agent_name, output in all_agent_outputs.items()
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Case facts:\n{case_facts}\n\n"
                    f"Preliminary recommendation: {preliminary_recommendation}\n\n"
                    f"All agent outputs:\n{outputs_text}\n\n"
                    f"Critique the recommendation. Return JSON: {OUTPUT_SCHEMA}"
                ),
            },
        ]

        result = await self.router.complete_json(
            messages, temperature=0.2, demo_mode=demo_mode
        )
        parsed = result.get("parsed", {})

        logger.info(
            "critic_agent_done",
            case_id=str(case_id),
            provider=result.get("final_provider"),
            quality=parsed.get("recommendation_quality"),
            should_revise=parsed.get("should_revise"),
        )
        return {
            "agent": self.name,
            "provider": result.get("final_provider"),
            "usage": result.get("usage").to_dict() if result.get("usage") else {},
            "output": parsed,
        }
