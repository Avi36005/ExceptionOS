"""OpenAI LLM provider (final fallback)."""
from __future__ import annotations

from typing import Any

import structlog
from openai import AsyncOpenAI, APIError, RateLimitError

from app.usage import TokenUsage

logger = structlog.get_logger(__name__)


class OpenAIProvider:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.label = "openai"
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        **kwargs,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise ValueError("OpenAI: API key not configured")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature,
                max_tokens=max_tokens,
            )
            usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                completion_tokens=response.usage.completion_tokens if response.usage else 0,
                total_tokens=response.usage.total_tokens if response.usage else 0,
                provider="openai",
                model=self.model,
            )
            content = response.choices[0].message.content or ""
            logger.info("openai_completion", model=self.model, tokens=usage.total_tokens)
            return {"content": content, "usage": usage, "provider": "openai"}
        except RateLimitError as exc:
            logger.warning("openai_rate_limit", error=str(exc))
            raise
        except APIError as exc:
            logger.error("openai_api_error", error=str(exc))
            raise
