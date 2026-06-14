"""Idempotent Supabase loader for the synthetic dataset.

Upserts every generated table into Supabase in FK-safe order using the
service-role key. Re-running with the same seed is a no-op because primary keys
are deterministic UUIDv5 values, so the loader ``upsert``\\s on ``id``.

The ``exception_cases`` <-> ``recommendations`` circular FK is handled by
inserting cases with ``current_recommendation_id`` stripped, then patching that
column after recommendations land.

Safety:

* refuses to run unless the dataset validates (``--skip-validate`` to override);
* ``--dry-run`` performs zero network calls and just prints the plan;
* ``--reset`` deletes previously generated synthetic rows (matched via
  ``synthetic_data_registry``) before loading;
* never logs secret values.

Usage::

    python -m scripts.synthetic.seed_supabase --mode demo-small --dry-run
    python -m scripts.synthetic.seed_supabase --mode demo-small
    python -m scripts.synthetic.seed_supabase --reset --mode demo-small
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from scripts.synthetic.config import (
    DEFAULT_MODE,
    MODE_DEMO_SMALL,
    MODE_FULL_SYNTHETIC,
    default_seed,
    get_env,
    load_env,
)
from scripts.synthetic.schema import DEFERRED_CASE_COLUMNS, TABLE_LOAD_ORDER
from scripts.synthetic.validate_dataset import validate_dataset

UPSERT_CHUNK = 200


def _build_dataset(args: argparse.Namespace) -> dict[str, Any]:
    if args.input:
        return json.loads(Path(args.input).read_text(encoding="utf-8"))
    from scripts.synthetic.cases_gen import generate_dataset

    seed = args.seed if args.seed is not None else default_seed()
    return generate_dataset(mode=args.mode, seed=seed)


def _chunks(items: list[Any], size: int):
    for start in range(0, len(items), size):
        yield items[start : start + size]


def _get_client():
    """Construct a service-role Supabase client. Imported lazily so --dry-run
    works without credentials or the supabase package installed."""
    url = get_env("SUPABASE_URL")
    key = get_env("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise SystemExit(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set (in backend/.env) to load data."
        )
    from supabase import create_client

    return create_client(url, key)


def _plan(rows: dict[str, list[dict[str, Any]]]) -> list[tuple[str, int]]:
    plan = []
    for table in TABLE_LOAD_ORDER:
        items = rows.get(table)
        if items:
            plan.append((table, len(items)))
    # surface any generated table we forgot to order, so nothing is silently dropped
    for table in rows:
        if table not in TABLE_LOAD_ORDER and rows[table]:
            plan.append((f"{table} (UNORDERED!)", len(rows[table])))
    return plan


def _prepare_case_rows(cases: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split deferred FK columns out of cases. Returns (insert_rows, patches)."""
    insert_rows = []
    patches = []
    for case in cases:
        patch = {col: case[col] for col in DEFERRED_CASE_COLUMNS if case.get(col) is not None}
        stripped = {k: v for k, v in case.items() if k not in DEFERRED_CASE_COLUMNS}
        insert_rows.append(stripped)
        if patch:
            patches.append({"id": case["id"], **patch})
    return insert_rows, patches


def reset_synthetic(client, dry_run: bool) -> None:
    """Delete previously generated synthetic rows via the registry, in reverse
    FK order so children go before parents."""
    if dry_run:
        print("[dry-run] would delete synthetic rows in reverse FK order via synthetic_data_registry")
        return
    for table in reversed(TABLE_LOAD_ORDER):
        if table == "synthetic_data_registry":
            continue
        try:
            client.table(table).delete().eq("synthetic", True).execute()
            print(f"reset: cleared synthetic rows from {table}")
        except Exception as exc:  # pragma: no cover - depends on remote schema
            print(f"reset: skipped {table} ({exc})")
    try:
        client.table("synthetic_data_registry").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("reset: cleared synthetic_data_registry")
    except Exception as exc:  # pragma: no cover
        print(f"reset: skipped synthetic_data_registry ({exc})")


def load(dataset: dict[str, Any], dry_run: bool, do_reset: bool) -> int:
    rows: dict[str, list[dict[str, Any]]] = dataset.get("rows", {})
    plan = _plan(rows)
    total = sum(count for _, count in plan)
    print(f"load plan ({total} rows across {len(plan)} tables):")
    for table, count in plan:
        print(f"  {table}: {count}")

    if dry_run:
        print("[dry-run] no rows written.")
        return 0

    client = _get_client()
    if do_reset:
        reset_synthetic(client, dry_run=False)

    written = 0
    for table in TABLE_LOAD_ORDER:
        items = rows.get(table)
        if not items:
            continue
        if table == "exception_cases":
            insert_rows, patches = _prepare_case_rows(items)
            written += _upsert(client, table, insert_rows)
            for patch in patches:
                client.table(table).update(
                    {k: v for k, v in patch.items() if k != "id"}
                ).eq("id", patch["id"]).execute()
            if patches:
                print(f"  patched current_recommendation_id on {len(patches)} cases")
        else:
            written += _upsert(client, table, items)
    print(f"done: upserted {written} rows.")
    return 0


def _upsert(client, table: str, items: list[dict[str, Any]]) -> int:
    count = 0
    for chunk in _chunks(items, UPSERT_CHUNK):
        client.table(table).upsert(chunk, on_conflict="id").execute()
        count += len(chunk)
    print(f"  upserted {count} -> {table}")
    return count


def main(argv: list[str] | None = None) -> int:
    load_env()
    parser = argparse.ArgumentParser(description="Load ExceptionOS synthetic data into Supabase.")
    parser.add_argument("--mode", choices=(MODE_DEMO_SMALL, MODE_FULL_SYNTHETIC), default=DEFAULT_MODE)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--input", default=None, help="Load an existing JSON file instead of generating.")
    parser.add_argument("--dry-run", action="store_true", help="Print the load plan without writing.")
    parser.add_argument("--reset", action="store_true", help="Delete existing synthetic rows first.")
    parser.add_argument("--skip-validate", action="store_true", help="Skip pre-load validation (not recommended).")
    args = parser.parse_args(argv)

    dataset = _build_dataset(args)

    if not args.skip_validate:
        report = validate_dataset(dataset)
        if not report.ok:
            print(report.render())
            print("ABORT: dataset failed validation; refusing to load. Use --skip-validate to override.")
            return 1

    return load(dataset, dry_run=args.dry_run, do_reset=args.reset)


if __name__ == "__main__":
    raise SystemExit(main())
