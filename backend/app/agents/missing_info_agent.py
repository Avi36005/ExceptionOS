"""Missing-information agent — identifies blocking gaps before the debate runs.

Runs immediately after the intake agent. Given the intake agent's extracted
facts and ``missing_information`` list, decides whether the case has enough
information to proceed to the full multi-agent debate, or whether the
requester must answer one or more questions first.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog

from app.llm.provider_router import ProviderRouter

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a case-intake quality reviewer for ExceptionOS.
Given the extracted facts and known gaps for an exception request, decide what
additional information (if any) is required before a multi-agent decision
debate can run.
Only flag a question as blocking if the debate genuinely cannot produce a
sound recommendation without it (e.g. missing requested amount, missing
entity/customer name, no description of the root cause). Prefer to proceed
with reasonable assumptions when possible.
Respond with valid JSON only."""

OUTPUT_SCHEMA = """{
  "questions": [
    {
      "field_key": "string — short machine key, e.g. requested_amount",
      "question": "string — human-readable question to ask the requester",
      "why_needed": "string — why this is needed for a sound decision",
      "blocking": true
    }
  ],
  "can_proceed": true,
  "summary": "string — one or two sentences summarising the assessment"
}"""


class MissingInfoAgent:
    def __init__(self, router: ProviderRouter):
        self.router = router
        self.name = "missing_info_agent"

    async def run(
        self,
        case_id: UUID,
        case_facts: dict[str, Any],
        intake_output: dict[str, Any],
        demo_mode: bool = False,
    ) -> dict[str, Any]:
        missing_information = intake_output.get("missing_information", [])
        key_facts = intake_output.get("key_facts", [])

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Case facts:\n{case_facts}\n\n"
                    f"Key facts extracted by intake:\n{key_facts}\n\n"
                    f"Gaps flagged by intake:\n{missing_information}\n\n"
                    f"Decide whether the case can proceed to the decision debate. "
                    f"Return JSON: {OUTPUT_SCHEMA}"
                ),
            },
        ]

        result = await self.router.complete_json(
            messages,
            temperature=0.1,
            demo_mode=demo_mode,
            required_keys=["questions", "can_proceed", "summary"],
        )
        parsed = result.get("parsed", {})

        # Normalise defensively — never let a malformed LLM response block
        # the pipeline on a missing key.
        questions = parsed.get("questions")
        if not isinstance(questions, list):
            questions = []
        normalized_questions: list[dict[str, Any]] = []
        for q in questions:
            if not isinstance(q, dict):
                continue
            normalized_questions.append({
                "field_key": q.get("field_key") or q.get("field") or "general",
                "question": q.get("question", ""),
                "why_needed": q.get("why_needed") or q.get("reason", ""),
                "blocking": bool(q.get("blocking", False)),
            })

        can_proceed = parsed.get("can_proceed")
        if not isinstance(can_proceed, bool):
            # Fall back to: proceed unless there's at least one blocking question.
            can_proceed = not any(q["blocking"] for q in normalized_questions)

        summary = parsed.get("summary") or ""

        logger.info(
            "missing_info_agent_done",
            case_id=str(case_id),
            provider=result.get("final_provider"),
            can_proceed=can_proceed,
            question_count=len(normalized_questions),
        )
        return {
            "agent": self.name,
            "provider": result.get("final_provider"),
            "usage": result.get("usage").to_dict() if result.get("usage") else {},
            "output": {
                "questions": normalized_questions,
                "can_proceed": can_proceed,
                "summary": summary,
            },
            "fallback_path": result.get("fallback_path", []),
        }
