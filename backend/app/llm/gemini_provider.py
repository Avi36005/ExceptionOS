"""Google Gemini LLM provider."""
from __future__ import annotations

from typing import Any

import structlog

from app.usage import TokenUsage

logger = structlog.get_logger(__name__)


class GeminiProvider:
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        self.api_key = api_key
        self.model = model
        self.label = "gemini"
        self._genai = None

    def _get_genai(self):
        if self._genai is None:
            import google.generativeai as genai  # type: ignore

            genai.configure(api_key=self.api_key)
            self._genai = genai
        return self._genai

    def _build_prompt(self, messages: list[dict[str, str]]) -> str:
        parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                parts.append(f"[System]: {content}")
            elif role == "assistant":
                parts.append(f"[Assistant]: {content}")
            else:
                parts.append(f"[User]: {content}")
        return "\n\n".join(parts)

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        **kwargs,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise ValueError("Gemini: API key not configured")

        import asyncio

        genai = self._get_genai()
        prompt = self._build_prompt(messages)

        loop = asyncio.get_event_loop()

        def _sync_call():
            model = genai.GenerativeModel(self.model)
            config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            return model.generate_content(prompt, generation_config=config)

        try:
            response = await loop.run_in_executor(None, _sync_call)
            content = response.text if hasattr(response, "text") else ""
            # Gemini usage metadata
            usage_meta = getattr(response, "usage_metadata", None)
            prompt_tokens = getattr(usage_meta, "prompt_token_count", 0) or 0
            completion_tokens = getattr(usage_meta, "candidates_token_count", 0) or 0
            usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                provider="gemini",
                model=self.model,
            )
            logger.info("gemini_completion", model=self.model, tokens=usage.total_tokens)
            return {"content": content, "usage": usage, "provider": "gemini"}
        except Exception as exc:
            logger.error("gemini_error", error=str(exc))
            raise
