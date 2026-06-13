"""Focused tests for insights/training route helpers."""
from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.api.v1.routes import insights, training


class _Query:
    def __init__(self, data=None, count: int = 0):
        self._data = data or []
        self._count = count

    def select(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def in_(self, *args, **kwargs):
        return self

    def gte(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def execute(self):
        return SimpleNamespace(data=self._data, count=self._count)


class _Supabase:
    def __init__(self, tables=None, counts=None):
        self._tables = tables or {}
        self._counts = counts or {}

    def table(self, name: str):
        return _Query(self._tables.get(name, []), self._counts.get(name, 0))


@pytest.mark.asyncio
async def test_root_causes_falls_back_when_empty():
    resp = await insights.get_root_causes(uuid4(), {}, _Supabase())

    assert resp.data["source"] == "fallback"
    assert resp.data["summary"]["total_patterns"] > 0
    assert resp.data["root_causes"]


@pytest.mark.asyncio
async def test_provider_usage_aggregates_supabase_rows():
    rows = [
        {"provider": "groq", "total_tokens": 100, "cost_usd": 0.10, "latency_ms": 1000, "status": "success"},
        {"provider": "groq", "total_tokens": 200, "cost_usd": 0.20, "latency_ms": 1200, "status": "fallback"},
        {"provider": "openai", "total_tokens": 50, "cost_usd": 0.30, "latency_ms": 2000, "status": "success"},
    ]

    resp = await insights.get_provider_usage(uuid4(), {}, _Supabase({"llm_usage": rows}))

    assert resp.data["source"] == "supabase"
    assert resp.data["summary"]["total_calls"] == 3
    assert resp.data["summary"]["total_tokens"] == 350
    assert resp.data["summary"]["fallback_rate"] == 33.3
    assert resp.data["by_provider"][0]["provider"] == "groq"
    assert resp.data["by_provider"][0]["calls"] == 2


@pytest.mark.asyncio
async def test_training_scenarios_have_stable_ids():
    first = await training.list_scenarios({})
    second = await training.list_scenarios({})

    assert [s["id"] for s in first.data] == [s["id"] for s in second.data]


@pytest.mark.asyncio
async def test_training_history_falls_back_when_empty():
    user_id = str(uuid4())

    resp = await training.get_training_history(uuid4(), {"sub": user_id}, _Supabase())

    assert resp.data[0]["source"] == "fallback"
    assert resp.data[0]["user_id"] == user_id
    assert resp.data[0]["scenario_id"]
