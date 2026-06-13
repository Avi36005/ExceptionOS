"""Intake agent — extracts structured facts from a case submission."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.llm.provider_router import ProviderRouter

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an intake specialist for ExceptionOS, a decision intelligence platform.
Your job is to analyse an exception request and extract structured facts.
Always respond with valid JSON only."""

EXTRACTION_SCHEMA = """{
  "entity_name": "string or null",
  "requested_amount": "number or null",
  "currency": "string (3-letter ISO code)",
  "annual_value": "number or null",
  "root_cause": "string — 1-2 sentence summary",
  "urgency": "low|medium|high|critical",
  "key_facts": [{"key": "string", "value": "string", "confidence": 0.0-1.0}],
  "missing_information": ["list of strings"],
  "category_suggestion": "string or null",
  "risk_flags": ["list of strings"]
}"""


class IntakeAgent:
    def __init__(self, router: ProviderRouter):
        self.router = router
        self.name = "intake_agent"

    async def run(
        self,
        case_id: UUID,
        title: str,
        description: str,
        additional_context: dict[str, Any] | None = None,
        demo_mode: bool = False,
    ) -> dict[str, Any]:
        ctx = ""
        if additional_context:
            ctx = "\n\nAdditional context:\n" + "\n".join(
                f"- {k}: {v}" for k, v in additional_context.items()
            )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Exception Request:\nTitle: {title}\nDescription: {description}{ctx}\n\n"
                    f"Extract facts and return JSON matching: {EXTRACTION_SCHEMA}"
                ),
            },
        ]

        result = await self.router.complete_json(
            messages, temperature=0.1, demo_mode=demo_mode
        )
        parsed = result.get("parsed", {})

        logger.info(
            "intake_agent_done",
            case_id=str(case_id),
            provider=result.get("final_provider"),
            urgency=parsed.get("urgency"),
            facts_count=len(parsed.get("key_facts", [])),
        )
        return {
            "agent": self.name,
            "provider": result.get("final_provider"),
            "usage": result.get("usage").to_dict() if result.get("usage") else {},
            "output": parsed,
            "fallback_path": result.get("fallback_path", []),
        }
