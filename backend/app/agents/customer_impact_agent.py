"""Customer impact agent — assesses impact on customers / relationships."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.llm.provider_router import ProviderRouter

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a customer relationship and impact analyst for ExceptionOS.
Assess how denying or approving this exception will affect the customer relationship.
Respond with valid JSON only."""

OUTPUT_SCHEMA = """{
  "customer_segment": "string — classify the customer/entity",
  "relationship_value": "low|medium|high|strategic",
  "churn_risk_if_denied": "low|medium|high|critical",
  "satisfaction_impact": "string",
  "reputational_risk": "low|medium|high",
  "alternative_solutions": ["list of strings — ways to satisfy customer without full approval"],
  "customer_impact_verdict": "approve|deny|negotiate",
  "customer_impact_reasoning": "string"
}"""


class CustomerImpactAgent:
    def __init__(self, router: ProviderRouter):
        self.router = router
        self.name = "customer_impact_agent"

    async def run(
        self,
        case_id: UUID,
        case_facts: dict[str, Any],
        intake_output: dict[str, Any],
        demo_mode: bool = False,
    ) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Case facts:\n{case_facts}\n\n"
                    f"Intake analysis:\n{intake_output}\n\n"
                    f"Assess customer impact. Return JSON: {OUTPUT_SCHEMA}"
                ),
            },
        ]

        result = await self.router.complete_json(
            messages, temperature=0.15, demo_mode=demo_mode
        )
        parsed = result.get("parsed", {})

        logger.info(
            "customer_impact_agent_done",
            case_id=str(case_id),
            provider=result.get("final_provider"),
            verdict=parsed.get("customer_impact_verdict"),
        )
        return {
            "agent": self.name,
            "provider": result.get("final_provider"),
            "usage": result.get("usage").to_dict() if result.get("usage") else {},
            "output": parsed,
            "fallback_path": result.get("fallback_path", []),
        }
