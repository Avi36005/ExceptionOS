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

    def __init__(self, api_key: str | None = None, base_url: str | None = None, namespace: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.HINDSIGHT_API_KEY
        self.base_url = (base_url or settings.HINDSIGHT_BASE_URL).rstrip("/")
        self.namespace = namespace or getattr(settings, "HINDSIGHT_NAMESPACE", "default")
        self._client: httpx.AsyncClient | None = None

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _bank_url(self, bank_id: str, suffix: str = "") -> str:
        """Build a namespaced bank URL: /v1/<namespace>/banks/<bank_id><suffix>."""
        return f"{self.base_url}/v1/{self.namespace}/banks/{bank_id}{suffix}"

    @staticmethod
    def _string_metadata(metadata: dict[str, Any]) -> dict[str, str]:
        """Hindsight MemoryItem.metadata only accepts string values. Coerce
        scalars to strings and JSON-encode anything structured; drop None."""
        import json as _json

        flat: dict[str, str] = {}
        for key, value in (metadata or {}).items():
            if value is None:
                continue
            if isinstance(value, (str, int, float, bool)):
                flat[key] = str(value)
            else:
                flat[key] = _json.dumps(value, default=str)
        return flat

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
        url = self._bank_url(bank_id, "/memories")
        meta = dict(metadata)
        tags = meta.pop("tags", None) or meta.pop("memory_tags", None)
        item: dict[str, Any] = {
            "content": content,
            "metadata": self._string_metadata(meta),
        }
        if document_id:
            item["document_id"] = document_id
            item["update_mode"] = "replace"
        if isinstance(tags, (list, tuple)):
            item["tags"] = [str(t) for t in tags]
        payload = {"items": [item], "async": False}
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
            if isinstance(data, dict) and "id" not in data:
                # Retain returns batch info; surface the first memory/document id.
                first_id = None
                for key in ("memory_ids", "document_ids", "ids", "results"):
                    seq = data.get(key)
                    if isinstance(seq, list) and seq:
                        first_id = seq[0].get("id") if isinstance(seq[0], dict) else seq[0]
                        break
                data = {**data, "id": first_id or document_id}
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

        POST /v1/<namespace>/banks/{bank_id}/memories/recall
        """
        url = self._bank_url(bank_id, "/memories/recall")
        payload: dict[str, Any] = {"query": query, "limit": top_k}
        if metadata_filter:
            tags = metadata_filter.get("tags")
            if isinstance(tags, (list, tuple)):
                payload["tags"] = [str(t) for t in tags]
            payload["metadata"] = self._string_metadata(
                {k: v for k, v in metadata_filter.items() if k != "tags"}
            )
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
            memories: list[dict[str, Any]] = (
                data.get("memories")
                or data.get("results")
                or data.get("items")
                or []
            )
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

        POST /v1/<namespace>/banks/{bank_id}/reflect
        """
        url = self._bank_url(bank_id, "/reflect")
        payload = {"query": topic}
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

    @staticmethod
    def _slug_bank_id(name: str) -> str:
        """Derive a stable, URL-safe bank id from a human name. Hindsight
        bank ids are client-chosen path segments, so they must be slugs."""
        import re

        slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", name.strip().lower()).strip("-")
        return slug[:120] or "exceptionos-bank"

    async def create_bank(
        self, name: str, description: str = "", bank_id: str | None = None
    ) -> dict[str, Any]:
        """Create (or upsert) a memory bank.

        PUT /v1/<namespace>/banks/{bank_id}

        Hindsight uses client-chosen bank ids. When no id is given we derive a
        stable slug from ``name`` so repeated calls are idempotent.
        """
        bank_id = bank_id or self._slug_bank_id(name)
        url = self._bank_url(bank_id)
        payload = {"name": name, "description": description}
        resp = await self.http.put(url, json=payload, headers=self.headers)
        resp.raise_for_status()
        data = resp.json() if resp.content else {}
        if not isinstance(data, dict):
            data = {}
        data.setdefault("id", bank_id)
        return data

    async def get_bank(self, bank_id: str) -> dict[str, Any]:
        """Get bank info.

        GET /v1/<namespace>/banks/{bank_id}
        """
        url = self._bank_url(bank_id)
        resp = await self.http.get(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    async def delete_memory(self, bank_id: str, memory_id: str) -> None:
        """Delete a specific memory."""
        url = self._bank_url(bank_id, f"/memories/{memory_id}")
        resp = await self.http.delete(url, headers=self.headers)
        resp.raise_for_status()


# Module-level singleton
_client: HindsightClient | None = None


def get_hindsight_client() -> HindsightClient:
    global _client
    if _client is None:
        _client = HindsightClient()
    return _client
