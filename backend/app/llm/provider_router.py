"""LLM provider router with fallback chain.

Priority: Groq (primary key) → Groq (secondary key) → Gemini → OpenAI → Demo mode.
"""
from __future__ import annotations

import json
from typing import Any

import structlog

from app.config import Settings, get_settings
from app.llm.groq_provider import GroqProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.openai_provider import OpenAIProvider
from app.usage import TokenUsage

logger = structlog.get_logger(__name__)

_DEMO_RESPONSE = {
    "recommendation_type": "approve",
    "confidence": 0.75,
    "reasoning": "[DEMO MODE] This is a synthetic response generated without a live LLM provider. Configure GROQ_API_KEY to enable real AI analysis.",
    "risk": {"level": "low", "factors": ["demo mode"], "score": 0.1},
    "conditions": ["Subject to standard approval workflow"],
}


class ProviderRouter:
    """Routes LLM calls through a prioritised fallback chain."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._build_providers()

    def _build_providers(self) -> None:
        s = self.settings
        self._providers: list[tuple[str, Any]] = []

        if s.GROQ_API_KEY:
            self._providers.append(
                ("groq_primary", GroqProvider(s.GROQ_API_KEY, s.GROQ_MODEL, "groq_primary"))
            )
        if s.GROQ_API_KEY_2:
            self._providers.append(
                ("groq_secondary", GroqProvider(s.GROQ_API_KEY_2, s.GROQ_MODEL, "groq_secondary"))
            )
        if s.GEMINI_API_KEY:
            self._providers.append(("gemini", GeminiProvider(s.GEMINI_API_KEY, s.GEMINI_MODEL)))
        if s.OPENAI_API_KEY:
            self._providers.append(("openai", OpenAIProvider(s.OPENAI_API_KEY, s.OPENAI_MODEL)))

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        demo_mode: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """Try each provider in order.  Returns provider result or demo fallback."""
        fallback_path: list[str] = []
        last_error: Exception | None = None

        for name, provider in self._providers:
            try:
                result = await provider.complete(
                    messages, temperature=temperature, max_tokens=max_tokens, **kwargs
                )
                result["fallback_path"] = fallback_path
                result["final_provider"] = name
                return result
            except Exception as exc:
                logger.warning("provider_failed", provider=name, error=str(exc))
                fallback_path.append(name)
                last_error = exc

        if demo_mode or self.settings.DEMO_MODE:
            logger.warning("using_demo_mode", reason="all_providers_failed")
            dummy_usage = TokenUsage(provider="demo", model="demo")
            return {
                "content": json.dumps(_DEMO_RESPONSE),
                "usage": dummy_usage,
                "provider": "demo",
                "fallback_path": fallback_path,
                "final_provider": "demo",
                "demo": True,
            }

        if last_error:
            raise RuntimeError(
                f"All LLM providers exhausted. Last error: {last_error}"
            ) from last_error
        raise RuntimeError("No LLM providers configured. Set GROQ_API_KEY in .env")

    async def complete_json(
        self,
        messages: list[dict[str, str]],
        schema_hint: str = "",
        temperature: float = 0.1,
        max_tokens: int = 4096,
        demo_mode: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """Complete and parse the response as JSON.  Retries once on parse error."""
        if schema_hint:
            # Append JSON instruction to last user message
            messages = list(messages)
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Respond with valid JSON only matching this structure: {schema_hint}. "
                        "Do not include markdown code fences."
                    ),
                }
            )

        result = await self.complete(messages, temperature=temperature, max_tokens=max_tokens, demo_mode=demo_mode, **kwargs)
        content = result.get("content", "")

        # Strip markdown fences if present
        if content.startswith("```"):
            lines = content.splitlines()
            content = "\n".join(
                line for line in lines if not line.startswith("```")
            )

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            # Attempt to extract first JSON object
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    parsed = json.loads(content[start:end])
                except json.JSONDecodeError:
                    parsed = {"raw_response": content}
            else:
                parsed = {"raw_response": content}

        result["parsed"] = parsed
        return result


# Module-level singleton
_router: ProviderRouter | None = None


def get_provider_router() -> ProviderRouter:
    global _router
    if _router is None:
        _router = ProviderRouter()
    return _router
