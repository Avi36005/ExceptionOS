"""Groq LLM provider."""
from __future__ import annotations

from typing import Any

import structlog
from groq import AsyncGroq, APIError, RateLimitError

from app.usage import TokenUsage

logger = structlog.get_logger(__name__)


class GroqProvider:
    def __init__(self, api_key: str, model: str = "llama3-70b-8192", label: str = "groq_primary"):
        self.api_key = api_key
        self.model = model
        self.label = label
        self._client: AsyncGroq | None = None

    @property
    def client(self) -> AsyncGroq:
        if self._client is None:
            self._client = AsyncGroq(api_key=self.api_key)
        return self._client

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        **kwargs,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise ValueError(f"{self.label}: API key not configured")

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
                provider=self.label,
                model=self.model,
            )
            content = response.choices[0].message.content or ""
            logger.info(
                "groq_completion",
                provider=self.label,
                model=self.model,
                tokens=usage.total_tokens,
            )
            return {"content": content, "usage": usage, "provider": self.label}
        except RateLimitError as exc:
            logger.warning("groq_rate_limit", provider=self.label, error=str(exc))
            raise
        except APIError as exc:
            logger.error("groq_api_error", provider=self.label, error=str(exc))
            raise
