"""Finance agent — assesses financial impact of granting or denying the exception."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.llm.provider_router import ProviderRouter

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a financial impact analyst for ExceptionOS.
Assess the financial implications of approving or denying this exception.
Respond with valid JSON only."""

OUTPUT_SCHEMA = """{
  "requested_amount": "number or null",
  "annual_value": "number or null",
  "approval_cost": "number or null",
  "denial_cost": "number or null",
  "net_benefit_approval": "number or null",
  "payback_period_months": "number or null",
  "financial_risk_level": "low|medium|high|critical",
  "cost_benefit_verdict": "approve|deny|needs_negotiation",
  "financial_reasoning": "string",
  "sensitivity_factors": ["list of strings — factors that could change the financial outcome"],
  "recommended_amount": "number or null — suggest a lower amount if appropriate"
}"""


class FinanceAgent:
    def __init__(self, router: ProviderRouter):
        self.router = router
        self.name = "finance_agent"

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
                    f"Perform financial impact assessment. Return JSON: {OUTPUT_SCHEMA}"
                ),
            },
        ]

        result = await self.router.complete_json(
            messages, temperature=0.1, demo_mode=demo_mode
        )
        parsed = result.get("parsed", {})

        logger.info(
            "finance_agent_done",
            case_id=str(case_id),
            provider=result.get("final_provider"),
            verdict=parsed.get("cost_benefit_verdict"),
            risk=parsed.get("financial_risk_level"),
        )
        return {
            "agent": self.name,
            "provider": result.get("final_provider"),
            "usage": result.get("usage").to_dict() if result.get("usage") else {},
            "output": parsed,
        }
