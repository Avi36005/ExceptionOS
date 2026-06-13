"""Policy drift agent — detects when decisions are diverging from stated policy."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.llm.provider_router import ProviderRouter
from app.memory.hindsight_client import HindsightClient

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a policy drift detection agent for ExceptionOS.
Analyse patterns in recent decisions to detect whether the organisation is drifting away from its stated policies.
Respond with valid JSON only."""

OUTPUT_SCHEMA = """{
  "drift_detected": true,
  "drift_score": "0.0-1.0",
  "drift_areas": [
    {
      "policy_area": "string",
      "drift_description": "string",
      "severity": "minor|moderate|major|critical",
      "trend": "increasing|stable|decreasing"
    }
  ],
  "overall_assessment": "string",
  "recommended_actions": ["list of strings"],
  "alert_level": "none|low|medium|high|critical"
}"""


class PolicyDriftAgent:
    def __init__(self, router: ProviderRouter, hindsight: HindsightClient):
        self.router = router
        self.hindsight = hindsight
        self.name = "policy_drift_agent"

    async def run(
        self,
        organization_id: UUID,
        bank_id: str,
        policy_content: str,
        policy_name: str,
        recent_decisions_summary: str,
        demo_mode: bool = False,
    ) -> dict[str, Any]:
        # Recall drift-related memories
        drift_memories = await self.hindsight.recall(
            bank_id=bank_id,
            query=f"policy deviation exception override {policy_name}",
            top_k=15,
        )

        memories_text = "\n\n".join(
            m.get("content", "") for m in drift_memories[:10]
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Policy: {policy_name}\n{policy_content[:3000]}\n\n"
                    f"Recent decision patterns:\n{recent_decisions_summary}\n\n"
                    f"Historical memory patterns:\n{memories_text}\n\n"
                    f"Detect policy drift. Return JSON: {OUTPUT_SCHEMA}"
                ),
            },
        ]

        result = await self.router.complete_json(
            messages, temperature=0.1, demo_mode=demo_mode
        )
        parsed = result.get("parsed", {})

        logger.info(
            "policy_drift_agent_done",
            organization_id=str(organization_id),
            drift_detected=parsed.get("drift_detected"),
            drift_score=parsed.get("drift_score"),
            alert_level=parsed.get("alert_level"),
        )
        return {
            "agent": self.name,
            "provider": result.get("final_provider"),
            "usage": result.get("usage").to_dict() if result.get("usage") else {},
            "output": parsed,
            "fallback_path": result.get("fallback_path", []),
        }
