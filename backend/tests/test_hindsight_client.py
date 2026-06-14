"""Unit tests for the Hindsight client request contract.

Locks in the real Hindsight Cloud REST shape discovered via /openapi.json:
namespaced ``/v1/<namespace>/banks/...`` paths, client-chosen bank ids created
via PUT, retain ``items[]`` with string-only metadata, and recall via
``/memories/recall``. No network: we stub the AsyncClient.
"""
from __future__ import annotations

from typing import Any

import pytest

from app.memory.hindsight_client import HindsightClient


class _FakeResponse:
    def __init__(self, payload: dict[str, Any] | None = None, status: int = 200):
        self._payload = payload if payload is not None else {}
        self.status_code = status
        self.content = b"{}"

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict[str, Any]:
        return self._payload


class _FakeAsyncClient:
    """Records every call so tests can assert URL + JSON body."""

    def __init__(self, response: dict[str, Any] | None = None):
        self.calls: list[dict[str, Any]] = []
        self._response = response or {}

    async def post(self, url, json=None, headers=None, **kw):
        self.calls.append({"method": "POST", "url": url, "json": json})
        return _FakeResponse(self._response)

    async def put(self, url, json=None, headers=None, **kw):
        self.calls.append({"method": "PUT", "url": url, "json": json})
        return _FakeResponse(self._response)


def _client_with(fake: _FakeAsyncClient) -> HindsightClient:
    c = HindsightClient(api_key="test-key", base_url="https://api.hindsight.test", namespace="default")
    c._client = fake  # inject stub
    return c


def test_bank_url_is_namespaced():
    c = HindsightClient(api_key="k", base_url="https://api.hindsight.test/", namespace="default")
    assert c._bank_url("bank-1") == "https://api.hindsight.test/v1/default/banks/bank-1"
    assert c._bank_url("bank-1", "/memories") == "https://api.hindsight.test/v1/default/banks/bank-1/memories"


def test_string_metadata_coerces_all_values():
    flat = HindsightClient._string_metadata(
        {"synthetic": True, "n": 3, "f": 1.5, "obj": {"a": 1}, "skip": None, "s": "x"}
    )
    assert flat == {"synthetic": "True", "n": "3", "f": "1.5", "obj": '{"a": 1}', "s": "x"}
    assert "skip" not in flat


def test_slug_bank_id_is_url_safe():
    assert HindsightClient._slug_bank_id("ExceptionOS Demo / NovaFlow!") == "exceptionos-demo-novaflow"


@pytest.mark.asyncio
async def test_retain_posts_items_array_with_string_metadata():
    fake = _FakeAsyncClient({"id": "doc-1"})
    c = _client_with(fake)
    await c.retain(
        bank_id="synthetic-bank-novaflow",
        content="hello",
        metadata={"synthetic": True, "kind": "decision"},
        document_id="case:o:c:decision:r",
    )
    call = fake.calls[-1]
    assert call["method"] == "POST"
    assert call["url"].endswith("/v1/default/banks/synthetic-bank-novaflow/memories")
    body = call["json"]
    assert body["async"] is False
    item = body["items"][0]
    assert item["content"] == "hello"
    assert item["document_id"] == "case:o:c:decision:r"
    assert item["update_mode"] == "replace"
    # metadata values must all be strings
    assert all(isinstance(v, str) for v in item["metadata"].values())
    assert item["metadata"]["synthetic"] == "True"


@pytest.mark.asyncio
async def test_recall_posts_to_memories_recall():
    fake = _FakeAsyncClient({"memories": [{"id": "m1"}]})
    c = _client_with(fake)
    out = await c.recall("bank-1", "late refund", top_k=3)
    call = fake.calls[-1]
    assert call["url"].endswith("/v1/default/banks/bank-1/memories/recall")
    assert call["json"]["query"] == "late refund"
    assert call["json"]["limit"] == 3
    assert out == [{"id": "m1"}]


@pytest.mark.asyncio
async def test_create_bank_puts_client_chosen_id():
    fake = _FakeAsyncClient({})
    c = _client_with(fake)
    res = await c.create_bank(name="exceptionos synthetic", bank_id="synthetic-bank-novaflow")
    call = fake.calls[-1]
    assert call["method"] == "PUT"
    assert call["url"].endswith("/v1/default/banks/synthetic-bank-novaflow")
    assert res["id"] == "synthetic-bank-novaflow"
