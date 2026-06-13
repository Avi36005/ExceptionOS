"""HTTP client for Hindsight Cloud API (vectorize.io)."""
from __future__ import annotations

import time
from typing import Any

import httpx
import structlog

from app.config import get_settings
from app.memory.operation_logger import OperationLogContext, log_hindsight_operation
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

    async def retain(
        self,
        bank_id: str,
        content: str,
        metadata: dict[str, Any],
        document_id: str | None = None,
        log_ctx: OperationLogContext | None = None,
    ) -> dict[str, Any]:
        """Store a memory in Hindsight.

        POST /v1/banks/{bank_id}/memories

        ``document_id`` (if given) is a stable, application-assigned id
        (see ``app.memory.document_ids``) recorded in metadata so repeated
        retains of the same logical memory can be deduplicated on recall.
        """
        url = f"{self.base_url}/v1/banks/{bank_id}/memories"
        meta = dict(metadata)
        if document_id:
            meta["document_id"] = document_id
        payload = {"content": content, "metadata": meta}
        started = time.monotonic()
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
            latency_ms = int((time.monotonic() - started) * 1000)
            logger.info("hindsight_retain", bank_id=bank_id, memory_id=data.get("id"), document_id=document_id)
            log_hindsight_operation(
                log_ctx,
                operation_type="retain",
                bank_id=bank_id,
                status="completed",
                document_id=document_id,
                request_json={"metadata": meta},
                response_json={"id": data.get("id")},
                latency_ms=latency_ms,
            )
            return data
        except httpx.HTTPStatusError as exc:
            latency_ms = int((time.monotonic() - started) * 1000)
            logger.error(
                "hindsight_retain_failed",
                bank_id=bank_id,
                status=exc.response.status_code,
                body=exc.response.text[:500],
            )
            log_hindsight_operation(
                log_ctx,
                operation_type="retain",
                bank_id=bank_id,
                status="failed",
                document_id=document_id,
                request_json={"metadata": meta},
                latency_ms=latency_ms,
                error_message=f"HTTP {exc.response.status_code}: {exc.response.text[:300]}",
            )
            raise
        except Exception as exc:
            latency_ms = int((time.monotonic() - started) * 1000)
            logger.error("hindsight_retain_error", bank_id=bank_id, error=str(exc))
            log_hindsight_operation(
                log_ctx,
                operation_type="retain",
                bank_id=bank_id,
                status="failed",
                document_id=document_id,
                request_json={"metadata": meta},
                latency_ms=latency_ms,
                error_message=str(exc),
            )
            raise

    async def recall(
        self,
        bank_id: str,
        query: str,
        top_k: int = 10,
        metadata_filter: dict[str, Any] | None = None,
        log_ctx: OperationLogContext | None = None,
        raise_on_error: bool = False,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant memories from Hindsight.

        POST /v1/banks/{bank_id}/query
        """
        url = f"{self.base_url}/v1/banks/{bank_id}/query"
        payload: dict[str, Any] = {"query": query, "top_k": top_k}
        if metadata_filter:
            payload["filter"] = metadata_filter
        started = time.monotonic()
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
            latency_ms = int((time.monotonic() - started) * 1000)
            logger.info(
                "hindsight_recall",
                bank_id=bank_id,
                query_snippet=query[:80],
                results=len(memories),
            )
            log_hindsight_operation(
                log_ctx,
                operation_type="recall",
                bank_id=bank_id,
                status="completed",
                request_json={"query": query[:300], "top_k": top_k, "filter": metadata_filter},
                response_json={"result_count": len(memories)},
                latency_ms=latency_ms,
            )
            return memories
        except httpx.HTTPStatusError as exc:
            latency_ms = int((time.monotonic() - started) * 1000)
            logger.error(
                "hindsight_recall_failed",
                bank_id=bank_id,
                status=exc.response.status_code,
            )
            log_hindsight_operation(
                log_ctx,
                operation_type="recall",
                bank_id=bank_id,
                status="failed",
                request_json={"query": query[:300], "top_k": top_k, "filter": metadata_filter},
                latency_ms=latency_ms,
                error_message=f"HTTP {exc.response.status_code}",
            )
            if raise_on_error:
                raise
            return []
        except Exception as exc:
            latency_ms = int((time.monotonic() - started) * 1000)
            logger.warning("hindsight_recall_error", bank_id=bank_id, error=str(exc))
            log_hindsight_operation(
                log_ctx,
                operation_type="recall",
                bank_id=bank_id,
                status="failed",
                request_json={"query": query[:300], "top_k": top_k, "filter": metadata_filter},
                latency_ms=latency_ms,
                error_message=str(exc),
            )
            if raise_on_error:
                raise
            return []

    async def reflect(
        self,
        bank_id: str,
        topic: str,
        log_ctx: OperationLogContext | None = None,
    ) -> dict[str, Any]:
        """Reflect on accumulated memories.

        POST /v1/banks/{bank_id}/reflect
        """
        url = f"{self.base_url}/v1/banks/{bank_id}/reflect"
        payload = {"topic": topic}
        started = time.monotonic()
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
            latency_ms = int((time.monotonic() - started) * 1000)
            logger.info("hindsight_reflect", bank_id=bank_id, topic=topic)
            log_hindsight_operation(
                log_ctx,
                operation_type="reflect",
                bank_id=bank_id,
                status="completed",
                request_json={"topic": topic[:300]},
                response_json={"reflection_snippet": str(data.get("reflection", ""))[:300]},
                latency_ms=latency_ms,
            )
            return data
        except httpx.HTTPStatusError as exc:
            latency_ms = int((time.monotonic() - started) * 1000)
            logger.error(
                "hindsight_reflect_failed",
                bank_id=bank_id,
                status=exc.response.status_code,
            )
            log_hindsight_operation(
                log_ctx,
                operation_type="reflect",
                bank_id=bank_id,
                status="failed",
                request_json={"topic": topic[:300]},
                latency_ms=latency_ms,
                error_message=f"HTTP {exc.response.status_code}",
            )
            return {"topic": topic, "reflection": "", "error": exc.response.text}
        except Exception as exc:
            latency_ms = int((time.monotonic() - started) * 1000)
            logger.warning("hindsight_reflect_error", bank_id=bank_id, error=str(exc))
            log_hindsight_operation(
                log_ctx,
                operation_type="reflect",
                bank_id=bank_id,
                status="failed",
                request_json={"topic": topic[:300]},
                latency_ms=latency_ms,
                error_message=str(exc),
            )
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
