"""Final decision agent — synthesises all inputs into the final recommendation."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.llm.provider_router import ProviderRouter

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are the final recommendation synthesiser for ExceptionOS.
Integrate all analysis from specialist agents into a single, well-reasoned recommendation.
Respond with valid JSON only."""

OUTPUT_SCHEMA = """{
  "recommendation_type": "approve|partially_approve|deny|escalate|needs_more_info",
  "recommended_amount": "number or null",
  "confidence": "0.0-1.0",
  "reasoning": "string — comprehensive reasoning (3-5 paragraphs)",
  "conditions": ["list of strings — conditions that must be met if approved"],
  "risk": {
    "level": "low|medium|high|critical",
    "factors": ["list of risk factors"],
    "score": "0.0-1.0"
  },
  "key_drivers": ["list of the top 3-5 factors driving this recommendation"],
  "dissenting_views": ["list of strings — notable counter-arguments considered"],
  "monitoring_requirements": ["list of strings — what to monitor if approved"],
  "escalation_path": "string or null — who to escalate to if escalation chosen",
  "provider_summary": {
    "finance": "string",
    "risk": "string",
    "customer": "string",
    "precedent": "string"
  }
}"""


class FinalDecisionAgent:
    def __init__(self, router: ProviderRouter):
        self.router = router
        self.name = "final_decision_agent"

    async def run(
        self,
        case_id: UUID,
        case_facts: dict[str, Any],
        all_outputs: dict[str, Any],
        critic_output: dict[str, Any],
        demo_mode: bool = False,
    ) -> dict[str, Any]:
        summary = "\n\n".join(
            f"=== {k} ===\n{v}" for k, v in all_outputs.items()
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Case facts:\n{case_facts}\n\n"
                    f"All agent analyses:\n{summary}\n\n"
                    f"Critic review:\n{critic_output}\n\n"
                    f"Synthesise the final recommendation. Return JSON: {OUTPUT_SCHEMA}"
                ),
            },
        ]

        result = await self.router.complete_json(
            messages, temperature=0.15, max_tokens=6000, demo_mode=demo_mode
        )
        parsed = result.get("parsed", {})

        logger.info(
            "final_decision_agent_done",
            case_id=str(case_id),
            provider=result.get("final_provider"),
            recommendation=parsed.get("recommendation_type"),
            confidence=parsed.get("confidence"),
        )
        return {
            "agent": self.name,
            "provider": result.get("final_provider"),
            "usage": result.get("usage").to_dict() if result.get("usage") else {},
            "output": parsed,
            "fallback_path": result.get("fallback_path", []),
        }
