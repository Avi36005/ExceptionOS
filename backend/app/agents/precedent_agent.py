"""Precedent agent — retrieves and ranks historical precedents from Hindsight."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.llm.provider_router import ProviderRouter
from app.memory.hindsight_client import HindsightClient

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
    def __init__(self, router: ProviderRouter, hindsight: HindsightClient):
        self.router = router
        self.hindsight = hindsight
        self.name = "precedent_agent"

    async def run(
        self,
        case_id: UUID,
        bank_id: str,
        case_facts: dict[str, Any],
        case_description: str,
        top_k: int = 10,
        demo_mode: bool = False,
    ) -> dict[str, Any]:
        # Step 1: Recall from Hindsight
        memories = await self.hindsight.recall(bank_id, case_description, top_k=top_k)

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

        # Step 2: Rank and analyse with LLM
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
        }
