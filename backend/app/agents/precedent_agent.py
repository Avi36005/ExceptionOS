"""Precedent agent — ranks and analyses historical precedents recalled from Hindsight.

Recall itself (with SSE instrumentation + ``hindsight_operations`` logging) is
performed by the orchestrator; this agent receives the already-recalled,
deduped/ranked memories and produces the precedent analysis.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.llm.provider_router import ProviderRouter

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a precedent analysis specialist for ExceptionOS.
Given an exception case and a list of recalled historical memories, identify the most relevant precedents.
Respond with valid JSON only."""

OUTPUT_SCHEMA = """{
  "top_precedents": [
    {
      "memory_id": "string",
      "case_id": "string or null",
      "relevance_score": 0.0-1.0,
      "similarity_reasons": ["list"],
      "difference_reasons": ["list"],
      "decision": "approved|denied|partially_approved|escalated",
      "amount_approved": "number or null",
      "key_lesson": "string"
    }
  ],
  "consistency_pattern": "consistent|mixed|inconsistent",
  "precedent_summary": "string — overall pattern from precedents",
  "recommended_alignment": "string — how this case should align with precedents"
}"""


class PrecedentAgent:
    def __init__(self, router: ProviderRouter):
        self.router = router
        self.name = "precedent_agent"

    async def run(
        self,
        case_id: UUID,
        case_facts: dict[str, Any],
        memories: list[dict[str, Any]],
        demo_mode: bool = False,
    ) -> dict[str, Any]:
        if not memories:
            return {
                "agent": self.name,
                "provider": "none",
                "usage": {},
                "output": {
                    "top_precedents": [],
                    "consistency_pattern": "consistent",
                    "precedent_summary": "No precedents found — this may be a novel case.",
                    "recommended_alignment": "Establish a new precedent with clear documentation.",
                },
                "raw_memories": [],
            }

        memories_text = "\n\n".join(
            f"Memory {i+1} (score={m.get('score', 0):.2f}):\n{m.get('content', '')}"
            for i, m in enumerate(memories[:10])
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Current case facts:\n{case_facts}\n\n"
                    f"Historical memories recalled:\n{memories_text}\n\n"
                    f"Analyse precedents. Return JSON: {OUTPUT_SCHEMA}"
                ),
            },
        ]

        result = await self.router.complete_json(
            messages, temperature=0.1, demo_mode=demo_mode
        )
        parsed = result.get("parsed", {})

        logger.info(
            "precedent_agent_done",
            case_id=str(case_id),
            memories_found=len(memories),
            pattern=parsed.get("consistency_pattern"),
        )
        return {
            "agent": self.name,
            "provider": result.get("final_provider"),
            "usage": result.get("usage").to_dict() if result.get("usage") else {},
            "output": parsed,
            "raw_memories": memories,
            "fallback_path": result.get("fallback_path", []),
        }
