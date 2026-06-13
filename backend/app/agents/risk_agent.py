"""Risk agent — assesses operational and compliance risks."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.llm.provider_router import ProviderRouter

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a risk assessment specialist for ExceptionOS.
Identify and quantify risks associated with approving or denying this exception.
Respond with valid JSON only."""

OUTPUT_SCHEMA = """{
  "overall_risk_level": "low|medium|high|critical",
  "risk_score": "0.0-1.0",
  "risks": [
    {
      "category": "operational|compliance|financial|reputational|legal",
      "description": "string",
      "likelihood": "low|medium|high",
      "impact": "low|medium|high|critical",
      "mitigation": "string"
    }
  ],
  "compliance_concerns": ["list of strings"],
  "regulatory_flags": ["list of strings"],
  "risk_verdict": "approve_with_controls|deny|escalate|approve",
  "risk_reasoning": "string",
  "recommended_controls": ["list of control measures if approved"]
}"""


class RiskAgent:
    def __init__(self, router: ProviderRouter):
        self.router = router
        self.name = "risk_agent"

    async def run(
        self,
        case_id: UUID,
        case_facts: dict[str, Any],
        policy_output: dict[str, Any],
        intake_output: dict[str, Any],
        demo_mode: bool = False,
    ) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Case facts:\n{case_facts}\n\n"
                    f"Policy analysis:\n{policy_output}\n\n"
                    f"Intake analysis:\n{intake_output}\n\n"
                    f"Perform risk assessment. Return JSON: {OUTPUT_SCHEMA}"
                ),
            },
        ]

        result = await self.router.complete_json(
            messages, temperature=0.1, demo_mode=demo_mode
        )
        parsed = result.get("parsed", {})

        logger.info(
            "risk_agent_done",
            case_id=str(case_id),
            provider=result.get("final_provider"),
            risk_level=parsed.get("overall_risk_level"),
            risk_score=parsed.get("risk_score"),
        )
        return {
            "agent": self.name,
            "provider": result.get("final_provider"),
            "usage": result.get("usage").to_dict() if result.get("usage") else {},
            "output": parsed,
        }
