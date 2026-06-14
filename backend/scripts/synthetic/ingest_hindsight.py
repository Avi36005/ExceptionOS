"""Ingest synthetic case decisions and outcomes into Hindsight Cloud.

For every generated case we retain two stable memories into the company's
Hindsight bank (``synthetic-bank-<slug>``):

* a **decision** memory keyed ``case:<org>:<case>:decision:<recommendation>``;
* an **outcome** memory keyed ``case:<org>:<case>:outcome``.

Stable document IDs (see :mod:`app.memory.document_ids`) make re-ingestion
idempotent: re-running retains the same logical memory rather than piling up
duplicates. The retain payloads are tagged ``synthetic: true`` so they can be
filtered or purged.

``--dry-run`` builds every payload and prints a summary without any network
call, so it is safe to run without a Hindsight key.

Usage::

    python -m scripts.synthetic.ingest_hindsight --mode demo-small --dry-run
    python -m scripts.synthetic.ingest_hindsight --mode demo-small --limit 25
"""
from __future__ import annotations

import argparse
import asyncio
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

from app.memory.document_ids import case_decision_document_id, case_outcome_document_id


def _build_dataset(args: argparse.Namespace) -> dict[str, Any]:
    if args.input:
        return json.loads(Path(args.input).read_text(encoding="utf-8"))
    from scripts.synthetic.cases_gen import generate_dataset

    seed = args.seed if args.seed is not None else default_seed()
    return generate_dataset(mode=args.mode, seed=seed)


def build_memories(dataset: dict[str, Any], limit: int | None = None) -> list[dict[str, Any]]:
    """Return a flat list of retain payloads (no network)."""
    rows = dataset.get("rows", {})
    orgs = {o["id"]: o for o in rows.get("organizations", [])}
    cases = {c["id"]: c for c in rows.get("exception_cases", [])}
    recs_by_case = {r["case_id"]: r for r in rows.get("recommendations", [])}
    outcomes_by_case = {o["case_id"]: o for o in dataset.get("artifacts", {}).get("outcomes", [])}

    memories: list[dict[str, Any]] = []
    for case_id, case in cases.items():
        org = orgs.get(case["organization_id"])
        if not org:
            continue
        bank_id = org.get("hindsight_bank_id") or f"synthetic-bank-{org['slug']}"
        rec = recs_by_case.get(case_id)
        if rec:
            memories.append(
                {
                    "bank_id": bank_id,
                    "document_id": case_decision_document_id(case["organization_id"], case_id, rec["id"]),
                    "content": _decision_content(org, case, rec),
                    "metadata": {
                        "kind": "decision",
                        "organization_slug": org["slug"],
                        "case_number": case["case_number"],
                        "category_id": case["category_id"],
                        "recommendation_type": rec.get("recommendation_type"),
                        "synthetic": True,
                    },
                }
            )
        outcome = outcomes_by_case.get(case_id)
        if outcome:
            memories.append(
                {
                    "bank_id": bank_id,
                    "document_id": case_outcome_document_id(case["organization_id"], case_id),
                    "content": _outcome_content(org, case, outcome),
                    "metadata": {
                        "kind": "outcome",
                        "organization_slug": org["slug"],
                        "case_number": case["case_number"],
                        "actual_outcome": outcome.get("actual_outcome"),
                        "synthetic": True,
                    },
                }
            )
        if limit and len(memories) >= limit:
            break
    return memories


def _decision_content(org: dict, case: dict, rec: dict) -> str:
    return (
        f"[{org['name']}] {case['title']} ({case['case_number']}). "
        f"Entity: {case.get('entity_name')}. Requested {case.get('currency')} "
        f"{case.get('requested_amount')}. Recommendation: {rec.get('recommendation_type')} "
        f"for {rec.get('recommended_amount')}. Reasoning: {rec.get('reasoning')}"
    )


def _outcome_content(org: dict, case: dict, outcome: dict) -> str:
    return (
        f"[{org['name']}] Outcome for {case['case_number']} ({case['title']}): "
        f"decision={outcome.get('decision_type')}, approved={outcome.get('approved_amount')}, "
        f"result={outcome.get('actual_outcome')}, financial_impact={outcome.get('financial_impact')}."
    )


async def _ingest(memories: list[dict[str, Any]]) -> int:
    from app.memory.hindsight_client import HindsightClient

    client = HindsightClient()
    ok = 0
    try:
        for memory in memories:
            await client.retain(
                bank_id=memory["bank_id"],
                content=memory["content"],
                metadata=memory["metadata"],
                document_id=memory["document_id"],
            )
            ok += 1
    finally:
        await client.close()
    return ok


def main(argv: list[str] | None = None) -> int:
    load_env()
    parser = argparse.ArgumentParser(description="Ingest synthetic memories into Hindsight Cloud.")
    parser.add_argument("--mode", choices=(MODE_DEMO_SMALL, MODE_FULL_SYNTHETIC), default=DEFAULT_MODE)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--input", default=None)
    parser.add_argument("--limit", type=int, default=None, help="Cap the number of memories (useful for smoke runs).")
    parser.add_argument("--dry-run", action="store_true", help="Build payloads without calling Hindsight.")
    args = parser.parse_args(argv)

    dataset = _build_dataset(args)
    memories = build_memories(dataset, limit=args.limit)
    banks = sorted({m["bank_id"] for m in memories})
    print(f"prepared {len(memories)} memories across {len(banks)} banks")

    if args.dry_run:
        for memory in memories[:3]:
            print(f"  [sample] {memory['document_id']} -> {memory['bank_id']}")
        print("[dry-run] no memories sent to Hindsight.")
        return 0

    if not get_env("HINDSIGHT_API_KEY"):
        raise SystemExit("HINDSIGHT_API_KEY must be set (in backend/.env) to ingest. Use --dry-run otherwise.")

    sent = asyncio.run(_ingest(memories))
    print(f"done: retained {sent}/{len(memories)} memories.")
    return 0 if sent == len(memories) else 1


if __name__ == "__main__":
    raise SystemExit(main())
