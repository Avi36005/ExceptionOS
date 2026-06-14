"""Seed 10 rich, demo-ready exception cases into a Hindsight bank.

Each case retains a DECISION memory and an OUTCOME memory (full reasoning,
human override, and what actually happened), exactly like the NovaFlow/Acme
late-refund walkthrough. After seeding, the global chat+voice orb and
Ask-Memory return these specific, grounded cases — ideal for a demo video.

Usage::

    python -m scripts.synthetic.seed_demo_examples --org acme
    python -m scripts.synthetic.seed_demo_examples --org acme --dry-run
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

# Each case: (id, decision_memory, outcome_memory)
CASES: list[tuple[str, str, str]] = [
    ("acme-retail",
     "Acme Retail requested a refund of INR 120000 after 52 days because NovaFlow's integration failed. "
     "Engineering confirmed it was NovaFlow's fault; the customer had only partial service (reports worked, "
     "main workflow did not). Policy allows post-30-day refunds for internal integration failure; refunds "
     "above INR 100000 need CFO approval. AI recommended a 75% refund (INR 90000) plus one free month. "
     "The CFO overrode to a FULL refund of INR 120000, citing a INR 2,000,000 expansion opportunity.",
     "Outcome: Acme accepted the full refund, the integration was fixed, the customer stayed and signed the "
     "INR 2,000,000 expansion. Decision rated highly successful."),
    ("brightlabs",
     "BrightLabs requested a refund after 47 days due to a NovaFlow-caused integration failure with partial "
     "service delivered. AI and manager approved a 50% partial refund.",
     "Outcome: BrightLabs accepted the 50% refund and remained a customer."),
    ("datapeak",
     "DataPeak requested a refund after 46 days; NovaFlow caused the problem and partial service was delivered. "
     "A 60% refund was approved.",
     "Outcome: DataPeak accepted the 60% refund and renewed its annual contract."),
    ("skybridge",
     "SkyBridge requested a refund after 55 days, but the delay was caused by the customer's own staffing, not "
     "NovaFlow. The refund was rejected per policy.",
     "Outcome: SkyBridge cancelled its contract after the rejection."),
    ("pixelworks",
     "PixelWorks requested a refund after 50 days for a NovaFlow integration failure with partial service. "
     "Similar to Acme but with NO expansion opportunity, so AI recommended a 60-70% refund rather than copying "
     "Acme's full refund. A 65% refund (INR 78000) was approved.",
     "Outcome: PixelWorks accepted the 65% refund and stayed; no expansion at this time."),
    ("summitledger",
     "SummitLedger requested a 25% enterprise discount exceeding the 15% standard cap, citing a 3-year commitment. "
     "Finance flagged margin impact; AI recommended 20%. CFO approved the full 25% for the multi-year lock-in.",
     "Outcome: SummitLedger signed a 3-year contract worth INR 4,200,000; positive."),
    ("initech",
     "Initech requested a payment-terms extension from net-30 to net-90. Memory showed a prior payment default, "
     "so AI and finance recommended denial. The request was denied.",
     "Outcome: avoided an estimated INR 300000 bad-debt exposure; positive."),
    ("smallco",
     "SmallCo requested an SLA service credit for downtime, but investigation showed the breach was caused by "
     "the customer's own misconfiguration, not NovaFlow. The SLA-credit exception was denied.",
     "Outcome: SmallCo accepted the explanation after a root-cause report; no credit issued."),
    ("hooli",
     "Hooli requested an NDA carve-out to share NovaFlow deliverables with a third-party auditor. Legal reviewed "
     "and signed off with scoped terms; the carve-out was approved.",
     "Outcome: the deal closed with no compliance incidents to date."),
    ("eu-client",
     "An EU client requested a data-residency exception to keep data in-region. The DPO approved with EU-hosting "
     "conditions; the exception was approved.",
     "Outcome: client onboarded successfully under EU data-residency terms; compliant."),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed 10 rich demo cases into a Hindsight bank.")
    parser.add_argument("--org", default="acme", help="Org slug (bank = synthetic-bank-<org>).")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    bank = f"synthetic-bank-{args.org}"

    if args.dry_run:
        print(f"[dry-run] would retain {len(CASES) * 2} memories into {bank}")
        for cid, dec, _ in CASES:
            print(f"  - {cid}: {dec[:80]}…")
        return 0

    s = get_settings()

    async def run() -> None:
        client = HindsightClient(api_key=s.HINDSIGHT_API_KEY, base_url=s.HINDSIGHT_BASE_URL, namespace=s.HINDSIGHT_NAMESPACE)
        n = 0
        for cid, decision, outcome in CASES:
            await client.retain(bank, decision, {"type": "case_decision", "tags": ["synthetic", "demo"], "case": cid}, document_id=f"demo:{cid}:decision")
            await client.retain(bank, outcome, {"type": "outcome", "tags": ["synthetic", "demo"], "case": cid}, document_id=f"demo:{cid}:outcome")
            n += 2
        print(f"retained {n} memories ({len(CASES)} cases) into {bank}")

        for q in ["late refund integration failure", "enterprise discount exception", "SLA credit"]:
            res = await client.recall(bank, q, top_k=3)
            print(f"  recall '{q}': {len(res)} hits | top: {str((res[0].get('content') or res[0].get('text')) if res else 'none')[:80]}")

    asyncio.run(run())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
