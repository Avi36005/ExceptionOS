"""Seed a small, demo-ready Hindsight bank for a single organization slug.

Retains a handful of realistic decision + outcome memories so the in-app
Memory pages (Insights → Memory Health, Ask Memory, case Precedents) light up
during a live demo. Memories are tagged ``synthetic: true`` and use stable
document ids, so re-running is idempotent.

Usage::

    python -m scripts.synthetic.seed_demo_bank --org acme
    python -m scripts.synthetic.seed_demo_bank --org acme --dry-run

The bank id is ``synthetic-bank-<org>`` to match the synthetic ingest naming.
Reads HINDSIGHT_* from backend/.env via app.config.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import get_settings  # noqa: E402
from app.memory.hindsight_client import HindsightClient  # noqa: E402

# (content, metadata-type) — decisions and their outcomes.
MEMORIES: list[tuple[str, str]] = [
    ("{org} approved an enterprise discount exception of INR 120000 for Globex due to a multi-year commitment.", "case_decision"),
    ("{org} denied a payment-terms extension for Initech citing prior default history.", "case_decision"),
    ("{org} approved an NDA carve-out for Hooli with legal sign-off.", "case_decision"),
    ("{org} approved a vendor onboarding exception for Stark Supplies after risk review.", "case_decision"),
    ("{org} escalated a budget-threshold breach for the Q2 marketing campaign.", "case_decision"),
    ("{org} approved a refund-policy exception for a key customer for goodwill retention.", "case_decision"),
    ("{org} denied an SLA-credit exception for SmallCo as the breach was customer-caused.", "case_decision"),
    ("{org} approved a data-residency exception for an EU client with DPO approval.", "case_decision"),
    ("Outcome: the Globex discount exception delivered a renewed 3-year contract worth INR 4.2M; positive.", "outcome"),
    ("Outcome: the Initech denial avoided an estimated INR 300000 bad-debt exposure; positive.", "outcome"),
    ("Outcome: the Hooli NDA carve-out closed the deal with no compliance incidents to date.", "outcome"),
    ("Outcome: the refund-policy goodwill exception retained a INR 1.1M ARR account; positive.", "outcome"),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed a demo Hindsight bank for one org.")
    parser.add_argument("--org", required=True, help="Org slug, e.g. acme (bank = synthetic-bank-<org>).")
    parser.add_argument("--org-name", default=None, help="Display name used in memory text (defaults to capitalized slug).")
    parser.add_argument("--dry-run", action="store_true", help="Print payloads without calling Hindsight.")
    args = parser.parse_args(argv)

    org_name = args.org_name or args.org.replace("-", " ").title()
    bank = f"synthetic-bank-{args.org}"
    items = [(c.format(org=org_name), t) for c, t in MEMORIES]

    if args.dry_run:
        print(f"[dry-run] {len(items)} memories -> {bank}")
        for c, t in items[:3]:
            print(f"  [{t}] {c}")
        return 0

    s = get_settings()

    async def run() -> None:
        client = HindsightClient(api_key=s.HINDSIGHT_API_KEY, base_url=s.HINDSIGHT_BASE_URL, namespace=s.HINDSIGHT_NAMESPACE)
        for i, (content, mtype) in enumerate(items):
            await client.retain(
                bank,
                content,
                {"type": mtype, "tags": ["synthetic"], "organization": args.org},
                document_id=f"{args.org}:demo-seed:{i}",
            )
        decisions = await client.recall(bank, "exception approval", top_k=5, metadata_filter={"type": "case_decision"})
        outcomes = await client.recall(bank, "outcome revenue retained", top_k=5, metadata_filter={"type": "outcome"})
        print(f"seeded {len(items)} into {bank} | recall decisions={len(decisions)} outcomes={len(outcomes)}")

    asyncio.run(run())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
