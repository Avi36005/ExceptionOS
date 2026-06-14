"""Tests for the SLA insights endpoint and budget insights with real rows."""
from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.api.v1.routes import insights


class _Query:
    def __init__(self, data=None):
        self._data = data or []

    def select(self, *a, **k):
        return self

    def eq(self, *a, **k):
        return self

    def order(self, *a, **k):
        return self

    def limit(self, *a, **k):
        return self

    def execute(self):
        return SimpleNamespace(data=self._data, count=len(self._data))


class _Supabase:
    def __init__(self, tables=None):
        self._tables = tables or {}

    def table(self, name: str):
        return _Query(self._tables.get(name, []))


@pytest.mark.asyncio
async def test_sla_falls_back_when_empty():
    resp = await insights.get_sla_insights(uuid4(), {}, _Supabase())
    assert resp.data["source"] == "demo"
    assert resp.data["summary"]["rules_total"] > 0


@pytest.mark.asyncio
async def test_sla_scores_met_breached_and_paused():
    now = datetime.utcnow()
    past = (now - timedelta(days=2)).isoformat()
    future = (now + timedelta(days=2)).isoformat()
    rules = [
        {"id": str(uuid4()), "category_id": "late_refund", "urgency": "high", "sla_minutes": 600, "warning_threshold_pct": 0.75, "active": True},
        {"id": str(uuid4()), "category_id": "operational_exception", "urgency": "medium", "sla_minutes": 2880, "warning_threshold_pct": 0.75, "active": False},
    ]
    cases = [
        # resolved before due -> met
        {"id": str(uuid4()), "status": "closed", "urgency": "high", "sla_due_at": future, "resolved_at": past, "created_at": past},
        # resolved after due -> breached
        {"id": str(uuid4()), "status": "closed", "urgency": "high", "sla_due_at": past, "resolved_at": now.isoformat(), "created_at": past},
        # open and past due -> breached
        {"id": str(uuid4()), "status": "pending_decision", "urgency": "high", "sla_due_at": past, "resolved_at": None, "created_at": past},
    ]
    resp = await insights.get_sla_insights(
        uuid4(), {}, _Supabase({"sla_rules": rules, "exception_cases": cases})
    )
    data = resp.data
    assert data["source"] == "supabase"
    assert data["summary"]["rules_total"] == 2
    assert data["summary"]["rules_paused"] == 1
    assert data["summary"]["met"] == 1
    assert data["summary"]["breached"] == 2
    assert data["summary"]["compliance_pct"] == pytest.approx(33.3, abs=0.1)


@pytest.mark.asyncio
async def test_budget_insights_aggregate_supabase_rows():
    budgets = [
        {"id": str(uuid4()), "department_id": None, "category_id": "late_refund", "period_start": "2026-04-01", "period_end": "2026-06-30", "budget_amount": 100000, "spent_amount": 40000, "currency": "INR", "updated_at": "2026-06-13"},
        {"id": str(uuid4()), "department_id": None, "category_id": "service_credit", "period_start": "2026-04-01", "period_end": "2026-06-30", "budget_amount": 50000, "spent_amount": 60000, "currency": "INR", "updated_at": "2026-06-13"},
    ]
    resp = await insights.get_budget_insights(uuid4(), {}, _Supabase({"exception_budgets": budgets}))
    data = resp.data
    assert data["source"] == "supabase"
    assert data["summary"]["total_budget"] == 150000
    assert data["summary"]["spent"] == 100000
    # second budget is over-spent -> negative remaining row
    assert any(row["remaining"] < 0 for row in data["budgets"])
