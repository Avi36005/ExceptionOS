"""Conversational assistant: real Groq LLM grounded in Hindsight recall.

Powers the global voice + chat orb. Self-contained (does not require a real
org UUID): it recalls from a Hindsight bank (default the seeded demo bank) and
answers with the live LLM provider chain, so chat and voice are both real.
"""
from __future__ import annotations

import structlog
from fastapi import APIRouter, Body, Depends

from app.dependencies import get_current_user
from app.llm.provider_router import get_provider_router
from app.memory.hindsight_client import get_hindsight_client
from app.memory.recall_service import RecallService
from app.schemas import DataResponse

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/assistant", tags=["assistant"])

DEFAULT_BANK = "synthetic-bank-acme"

SYSTEM_PROMPT = (
    "You are the ExceptionOS assistant — a friendly, professional helper for policy "
    "exceptions, precedents, and decisions. Keep replies short (1-3 sentences) and in a "
    "natural spoken tone suitable for being read aloud.\n"
    "- For greetings or small talk (hi, hello, thanks), reply warmly in ONE sentence and "
    "invite the user to ask about an exception, policy, or precedent. Do NOT list past cases.\n"
    "- Only when the user actually asks about a case, refund, discount, policy, or decision, "
    "use the provided past memories and briefly reference the relevant ones.\n"
    "- Never dump or enumerate memories that the user did not ask about."
)

GREETINGS = {"hi", "hii", "hey", "hello", "yo", "hola", "thanks", "thank you", "ok", "okay", "good morning", "good evening", "good afternoon", "sup", "how are you"}


@router.post("/chat")
async def assistant_chat(
    payload: dict = Body(...),
    current_user: dict = Depends(get_current_user),
) -> DataResponse:
    """Answer a free-form question using Hindsight recall + the live LLM chain."""
    message = (payload.get("message") or "").strip()
    bank_id = payload.get("bank_id") or DEFAULT_BANK  # org-aware: per-org Hindsight bank
    page_context = (payload.get("context") or "").strip()  # page-aware: current case/page
    if not message:
        return DataResponse(data={"answer": "Please ask me something.", "sources": []})

    # Greetings / small talk: skip Hindsight entirely and just reply warmly.
    normalized = message.lower().strip(" .!?")
    is_smalltalk = normalized in GREETINGS or len(normalized) <= 3

    # 1. Recall grounding memories from Hindsight (best-effort) for real queries only.
    memories: list[dict] = []
    if not is_smalltalk:
        try:
            memories = await RecallService(get_hindsight_client()).recall_all(bank_id, message, top_k=5)
        except Exception as exc:  # noqa: BLE001
            logger.warning("assistant_recall_failed", error=str(exc))

    context = ""
    if memories:
        lines = []
        for m in memories[:5]:
            text = m.get("content") or m.get("text") or m.get("memory") or ""
            if text:
                lines.append(f"- {str(text)[:240]}")
        if lines:
            context = "Relevant past memories from Hindsight:\n" + "\n".join(lines)

    blocks = []
    if page_context:
        blocks.append(f"Current screen context (use it if the question is about 'this' case/page):\n{page_context}")
    if context:
        blocks.append(context)
    blocks.append(f"Question: {message}")
    user_content = "\n\n".join(blocks)

    # 2. Answer with the real LLM provider chain (Groq primary).
    try:
        result = await get_provider_router().complete(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.4,
            max_tokens=400,
        )
        answer = (result.get("content") or "").strip() or "I could not generate a response right now."
        provider = result.get("final_provider", "unknown")
    except Exception as exc:  # noqa: BLE001
        logger.warning("assistant_llm_failed", error=str(exc))
        answer = "The assistant is temporarily unavailable. Please try again."
        provider = "error"

    sources = [
        {"text": str(m.get("content") or m.get("text") or m.get("memory") or "")[:200]}
        for m in memories[:3]
    ]
    return DataResponse(data={"answer": answer, "sources": sources, "provider": provider})
