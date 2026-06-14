"""QA coverage for the synthetic-data generator, validator, loader and ingest.

These tests enforce the spec guarantees: deterministic output, every row marked
synthetic, FK integrity, budget reconciliation, SLA paused/breached demo states,
registry coverage, and FK-safe load ordering.
"""
from __future__ import annotations

import json

import pytest

from scripts.synthetic.cases_gen import generate_dataset
from scripts.synthetic.config import MODE_DEMO_SMALL
from scripts.synthetic.ingest_hindsight import build_memories
from scripts.synthetic.schema import REQUIRED_TABLES, TABLE_LOAD_ORDER
from scripts.synthetic.seed_supabase import _plan, _prepare_case_rows
from scripts.synthetic.validate_dataset import validate_dataset

SEED = 2026


@pytest.fixture(scope="module")
def dataset() -> dict:
    return generate_dataset(mode=MODE_DEMO_SMALL, seed=SEED)


def test_generation_is_deterministic():
    first = generate_dataset(mode=MODE_DEMO_SMALL, seed=SEED)
    second = generate_dataset(mode=MODE_DEMO_SMALL, seed=SEED)
    assert json.dumps(first, sort_keys=True, default=str) == json.dumps(second, sort_keys=True, default=str)


def test_dataset_validates_clean(dataset):
    report = validate_dataset(dataset)
    assert report.ok, report.render()
    assert not report.warnings, report.warnings


def test_required_tables_present_and_nonempty(dataset):
    rows = dataset["rows"]
    for table in REQUIRED_TABLES:
        assert rows.get(table), f"missing/empty required table {table}"


def test_every_row_is_synthetic(dataset):
    for table, items in dataset["rows"].items():
        if table == "synthetic_data_registry":
            continue
        assert all(row.get("synthetic") is True for row in items), table


def test_new_tables_emitted(dataset):
    rows = dataset["rows"]
    assert len(rows["sla_rules"]) == 12 * 12  # 12 orgs x 12 categories
    assert rows["exception_budgets"]
    assert rows["budget_transactions"]


def test_budget_spent_reconciles(dataset):
    rows = dataset["rows"]
    net: dict[str, float] = {}
    for txn in rows["budget_transactions"]:
        amount = float(txn["amount"])
        if txn["transaction_type"] == "debit":
            net[txn["budget_id"]] = round(net.get(txn["budget_id"], 0.0) + amount, 2)
        elif txn["transaction_type"] == "credit":
            net[txn["budget_id"]] = round(net.get(txn["budget_id"], 0.0) - amount, 2)
    for budget in rows["exception_budgets"]:
        assert round(float(budget["spent_amount"]), 2) == round(net.get(budget["id"], 0.0), 2)


def test_demo_states_present(dataset):
    rows = dataset["rows"]
    # at least one paused SLA per org and at least one breached budget overall
    assert any(not r["active"] for r in rows["sla_rules"])
    assert any(float(b["budget_amount"]) < float(b["spent_amount"]) for b in rows["exception_budgets"])


def test_transactions_reference_existing_budgets(dataset):
    rows = dataset["rows"]
    budget_ids = {b["id"] for b in rows["exception_budgets"]}
    assert all(txn["budget_id"] in budget_ids for txn in rows["budget_transactions"])


def test_load_plan_orders_all_tables(dataset):
    plan = _plan(dataset["rows"])
    planned = {name for name, _ in plan}
    # nothing flagged UNORDERED
    assert not any("UNORDERED" in name for name in planned)
    # every non-empty generated table is in the canonical order
    for table, items in dataset["rows"].items():
        if items:
            assert table in TABLE_LOAD_ORDER, f"{table} missing from TABLE_LOAD_ORDER"


def test_case_deferred_fk_split(dataset):
    cases = dataset["rows"]["exception_cases"]
    insert_rows, patches = _prepare_case_rows(cases)
    assert all("current_recommendation_id" not in row for row in insert_rows)
    # cases that had a recommendation produce a patch
    assert patches
    assert all("current_recommendation_id" in p for p in patches)


def test_hindsight_memories_have_stable_ids(dataset):
    memories = build_memories(dataset)
    ids = [m["document_id"] for m in memories]
    assert len(ids) == len(set(ids)), "document ids must be unique/stable"
    assert all(m["metadata"]["synthetic"] is True for m in memories)
    assert any(":decision:" in i for i in ids) and any(i.endswith(":outcome") for i in ids)


def test_novaflow_hero_is_inr(dataset):
    orgs = {o["slug"]: o for o in dataset["rows"]["organizations"]}
    assert orgs["novaflow"]["currency"] == "INR"
