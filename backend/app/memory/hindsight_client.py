"""HTTP client for Hindsight Cloud API (vectorize.io)."""
from __future__ import annotations

from typing import Any

import httpx
import structlog

from app.config import get_settings
from app.retry import retry_async

logger = structlog.get_logger(__name__)


class HindsightClient:
    """Async HTTP client wrapping the Hindsight Cloud REST API."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.HINDSIGHT_API_KEY
        self.base_url = (base_url or settings.HINDSIGHT_BASE_URL).rstrip("/")
        self._client: httpx.AsyncClient | None = None

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @property
    def http(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    async def retain(self, bank_id: str, content: str, metadata: dict[str, Any]) -> dict[str, Any]:
        """Store a memory in Hindsight.

        POST /v1/banks/{bank_id}/memories
        """
        url = f"{self.base_url}/v1/banks/{bank_id}/memories"
        payload = {"content": content, "metadata": metadata}
        try:
            resp = await retry_async(
                self.http.post,
                url,
                json=payload,
                headers=self.headers,
                max_attempts=3,
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info("hindsight_retain", bank_id=bank_id, memory_id=data.get("id"))
            return data
        except httpx.HTTPStatusError as exc:
            logger.error(
                "hindsight_retain_failed",
                bank_id=bank_id,
                status=exc.response.status_code,
                body=exc.response.text[:500],
            )
            raise
        except Exception as exc:
            logger.error("hindsight_retain_error", bank_id=bank_id, error=str(exc))
            raise

    async def recall(
        self,
        bank_id: str,
        query: str,
        top_k: int = 10,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant memories from Hindsight.

        POST /v1/banks/{bank_id}/query
        """
        url = f"{self.base_url}/v1/banks/{bank_id}/query"
        payload: dict[str, Any] = {"query": query, "top_k": top_k}
        if metadata_filter:
            payload["filter"] = metadata_filter
        try:
            resp = await retry_async(
                self.http.post,
                url,
                json=payload,
                headers=self.headers,
                max_attempts=3,
            )
            resp.raise_for_status()
            data = resp.json()
            memories: list[dict[str, Any]] = data.get("memories", data.get("results", []))
            logger.info(
                "hindsight_recall",
                bank_id=bank_id,
                query_snippet=query[:80],
                results=len(memories),
            )
            return memories
        except httpx.HTTPStatusError as exc:
            logger.error(
                "hindsight_recall_failed",
                bank_id=bank_id,
                status=exc.response.status_code,
            )
            return []
        except Exception as exc:
            logger.warning("hindsight_recall_error", bank_id=bank_id, error=str(exc))
            return []

    async def reflect(self, bank_id: str, topic: str) -> dict[str, Any]:
        """Reflect on accumulated memories.

        POST /v1/banks/{bank_id}/reflect
        """
        url = f"{self.base_url}/v1/banks/{bank_id}/reflect"
        payload = {"topic": topic}
        try:
            resp = await retry_async(
                self.http.post,
                url,
                json=payload,
                headers=self.headers,
                max_attempts=2,
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info("hindsight_reflect", bank_id=bank_id, topic=topic)
            return data
        except httpx.HTTPStatusError as exc:
            logger.error(
                "hindsight_reflect_failed",
                bank_id=bank_id,
                status=exc.response.status_code,
            )
            return {"topic": topic, "reflection": "", "error": exc.response.text}
        except Exception as exc:
            logger.warning("hindsight_reflect_error", bank_id=bank_id, error=str(exc))
            return {"topic": topic, "reflection": "", "error": str(exc)}

    async def create_bank(self, name: str, description: str = "") -> dict[str, Any]:
        """Create a new memory bank.

        POST /v1/banks
        """
        url = f"{self.base_url}/v1/banks"
        payload = {"name": name, "description": description}
        resp = await self.http.post(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    async def get_bank(self, bank_id: str) -> dict[str, Any]:
        """Get bank info.

        GET /v1/banks/{bank_id}
        """
        url = f"{self.base_url}/v1/banks/{bank_id}"
        resp = await self.http.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    async def delete_memory(self, bank_id: str, memory_id: str) -> None:
        """Delete a specific memory."""
        url = f"{self.base_url}/v1/banks/{bank_id}/memories/{memory_id}"
        resp = await self.http.delete(url, headers=self.headers)
        resp.raise_for_status()


# Module-level singleton
_client: HindsightClient | None = None


def get_hindsight_client() -> HindsightClient:
    global _client
    if _client is None:
        _client = HindsightClient()
    return _client
