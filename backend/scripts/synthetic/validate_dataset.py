"""Validate a generated synthetic dataset before it is loaded anywhere.

Checks (all offline, no network):

* every row in every table carries ``synthetic: true``;
* all required tables are present and non-empty;
* foreign keys resolve against rows in the same dataset;
* primary keys are unique, valid UUIDs;
* ``exception_budgets.spent_amount`` reconciles to net debit/credit txns;
* ``synthetic_data_registry`` covers every org-scoped row;
* no real-looking PII leaks (emails must be ``*.example.com``; no secrets).

Usage::

    python -m scripts.synthetic.validate_dataset --mode demo-small
    python -m scripts.synthetic.validate_dataset --input path/to.json

Exit code is non-zero when any error-level finding is raised, so CI can gate on
it. Warnings never fail the build.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from scripts.synthetic.config import DEFAULT_MODE, MODE_DEMO_SMALL, MODE_FULL_SYNTHETIC, default_seed, load_env
from scripts.synthetic.schema import FOREIGN_KEYS, REQUIRED_TABLES

# Heuristics for catching accidentally embedded secrets in any string value.
_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"gsk_[A-Za-z0-9]{20,}"),
    re.compile(r"AIza[A-Za-z0-9_\-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}"),  # JWT
)
_EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_ALLOWED_EMAIL_SUFFIX = ".example.com"


class ValidationReport:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict[str, Any] = {}

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    @property
    def ok(self) -> bool:
        return not self.errors

    def render(self) -> str:
        lines = ["synthetic dataset validation"]
        for table, count in sorted(self.stats.get("counts", {}).items()):
            lines.append(f"  {table}: {count}")
        lines.append(f"errors={len(self.errors)} warnings={len(self.warnings)}")
        for message in self.errors:
            lines.append(f"  ERROR  {message}")
        for message in self.warnings:
            lines.append(f"  WARN   {message}")
        lines.append("RESULT: " + ("PASS" if self.ok else "FAIL"))
        return "\n".join(lines)


def _iter_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _iter_strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _iter_strings(item)


def _is_uuid(value: Any) -> bool:
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def validate_dataset(dataset: dict[str, Any]) -> ValidationReport:
    report = ValidationReport()
    rows: dict[str, list[dict[str, Any]]] = dataset.get("rows", {})
    report.stats["counts"] = {name: len(items) for name, items in rows.items()}

    # 1. required tables present and non-empty
    for table in REQUIRED_TABLES:
        if not rows.get(table):
            report.error(f"required table '{table}' is missing or empty")

    # 2. collect ids per table; enforce uniqueness + uuid + synthetic flag
    ids_by_table: dict[str, set[str]] = {}
    for table, items in rows.items():
        seen: set[str] = set()
        for index, row in enumerate(items):
            # synthetic_data_registry has no `synthetic` column; it *is* the
            # registry of synthetic rows and is inherently synthetic.
            if table != "synthetic_data_registry" and row.get("synthetic") is not True:
                report.error(f"{table}[{index}] missing synthetic=true")
            row_id = row.get("id")
            if row_id is not None:
                if not _is_uuid(row_id):
                    report.error(f"{table}[{index}] id is not a valid UUID: {row_id!r}")
                if row_id in seen:
                    report.error(f"{table} has duplicate id {row_id}")
                seen.add(str(row_id))
        ids_by_table[table] = seen

    # 3. foreign-key integrity
    for table, fks in FOREIGN_KEYS.items():
        for row in rows.get(table, []):
            for column, referenced in fks.items():
                value = row.get(column)
                if value is None:
                    continue
                if str(value) not in ids_by_table.get(referenced, set()):
                    report.error(
                        f"{table}.{column}={value} does not reference an existing {referenced} row"
                    )

    # 4. budget reconciliation: spent_amount == sum(debit) - sum(credit)
    _validate_budgets(rows, report)

    # 5. registry coverage for org-scoped rows
    _validate_registry(rows, report)

    # 6. PII / secret scan
    _validate_no_pii_or_secrets(rows, report)

    return report


def _validate_budgets(rows: dict[str, list[dict[str, Any]]], report: ValidationReport) -> None:
    net: dict[str, float] = {}
    for txn in rows.get("budget_transactions", []):
        ttype = txn.get("transaction_type")
        amount = float(txn.get("amount") or 0)
        budget_id = txn.get("budget_id")
        if ttype == "debit":
            net[budget_id] = round(net.get(budget_id, 0.0) + amount, 2)
        elif ttype == "credit":
            net[budget_id] = round(net.get(budget_id, 0.0) - amount, 2)
        # 'adjustment' rows are informational and excluded from spent reconciliation
    breached = 0
    for budget in rows.get("exception_budgets", []):
        budget_id = budget.get("id")
        spent = round(float(budget.get("spent_amount") or 0), 2)
        expected = round(net.get(budget_id, 0.0), 2)
        if spent != expected:
            report.error(
                f"exception_budgets {budget_id} spent_amount={spent} != net transactions {expected}"
            )
        if float(budget.get("budget_amount") or 0) < spent:
            breached += 1
    report.stats["breached_budgets"] = breached
    if rows.get("exception_budgets") and breached == 0:
        report.warn("no breached budgets present; over-budget demo state is missing")


def _validate_registry(rows: dict[str, list[dict[str, Any]]], report: ValidationReport) -> None:
    registry = rows.get("synthetic_data_registry", [])
    registered = {(r.get("table_name"), str(r.get("row_id"))) for r in registry}
    missing = 0
    for table, items in rows.items():
        if table == "synthetic_data_registry":
            continue
        for row in items:
            row_id = row.get("id")
            org = row.get("organization_id")
            if row_id and org and (table, str(row_id)) not in registered:
                missing += 1
    if missing:
        report.error(f"{missing} org-scoped rows are not covered by synthetic_data_registry")


def _validate_no_pii_or_secrets(rows: dict[str, list[dict[str, Any]]], report: ValidationReport) -> None:
    secrets_found = 0
    bad_emails: set[str] = set()
    for table, items in rows.items():
        for row in items:
            for text in _iter_strings(row):
                for pattern in _SECRET_PATTERNS:
                    if pattern.search(text):
                        secrets_found += 1
                for email in _EMAIL_PATTERN.findall(text):
                    if not email.lower().endswith(_ALLOWED_EMAIL_SUFFIX):
                        bad_emails.add(email)
    if secrets_found:
        report.error(f"{secrets_found} possible secret(s) detected in dataset values")
    for email in sorted(bad_emails):
        report.warn(f"non-example.com email found: {email}")


def _load_dataset(args: argparse.Namespace) -> dict[str, Any]:
    if args.input:
        return json.loads(Path(args.input).read_text(encoding="utf-8"))
    from scripts.synthetic.cases_gen import generate_dataset

    seed = args.seed if args.seed is not None else default_seed()
    return generate_dataset(mode=args.mode, seed=seed)


def main(argv: list[str] | None = None) -> int:
    load_env()
    parser = argparse.ArgumentParser(description="Validate an ExceptionOS synthetic dataset.")
    parser.add_argument("--mode", choices=(MODE_DEMO_SMALL, MODE_FULL_SYNTHETIC), default=DEFAULT_MODE)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--input", default=None, help="Validate an existing JSON file instead of generating.")
    args = parser.parse_args(argv)

    dataset = _load_dataset(args)
    report = validate_dataset(dataset)
    print(report.render())
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
