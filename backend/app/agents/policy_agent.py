"""Policy agent — identifies applicable policy and assesses compliance."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.llm.provider_router import ProviderRouter

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a policy compliance specialist for ExceptionOS.
Given an exception case and the relevant policy text, determine how the policy applies.
Respond with valid JSON only."""

OUTPUT_SCHEMA = """{
  "policy_applies": true,
  "applicable_sections": ["list of relevant policy section titles or identifiers"],
  "compliance_status": "compliant|non_compliant|partial|unclear",
  "deviation_description": "string — describe how the request deviates from policy",
  "standard_treatment": "string — what policy normally dictates",
  "exception_justification_required": ["list of strings — what must be justified"],
  "approval_authority": "string — who normally approves this type of exception",
  "reasoning": "string"
}"""


class PolicyAgent:
    def __init__(self, router: ProviderRouter):
        self.router = router
        self.name = "policy_agent"

    async def run(
        self,
        case_id: UUID,
        case_facts: dict[str, Any],
        policy_content: str,
        policy_name: str = "Organisational Policy",
        demo_mode: bool = False,
    ) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Policy: {policy_name}\n{policy_content}\n\n"
                    f"Exception case facts:\n{case_facts}\n\n"
                    f"Analyse policy applicability. Return JSON: {OUTPUT_SCHEMA}"
                ),
            },
        ]

        result = await self.router.complete_json(
            messages, temperature=0.1, demo_mode=demo_mode
        )
        parsed = result.get("parsed", {})

        logger.info(
            "policy_agent_done",
            case_id=str(case_id),
            provider=result.get("final_provider"),
            compliance=parsed.get("compliance_status"),
        )
        return {
            "agent": self.name,
            "provider": result.get("final_provider"),
            "usage": result.get("usage").to_dict() if result.get("usage") else {},
            "output": parsed,
        }
