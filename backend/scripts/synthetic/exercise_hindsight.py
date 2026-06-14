"""Exercise Hindsight across all banks: recall sweeps + reflect.

Genuine usage that demonstrates the full Retain/Recall/Reflect loop at scale
(run after ingesting the synthetic dataset). For every bank it runs several
realistic recall queries and a couple of reflect (pattern-analysis) calls.

Usage::

    python -m scripts.synthetic.exercise_hindsight
    python -m scripts.synthetic.exercise_hindsight --rounds 2
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

SLUGS = [
    "novaflow", "cargonest", "cloudharbor", "retailorbit", "buildsphere",
    "peoplegrid", "procurepilot", "stayroute", "servicemint", "findesk",
    "eventforge", "databridge", "harvestlane", "meridianhealth", "orbitalworks",
    "acme",
]

RECALL_QUERIES = [
    "late refund caused by integration failure",
    "enterprise discount above the standard cap",
    "SLA service credit for downtime",
    "payment terms extension with prior default",
    "contract cancellation refund",
    "vendor payment exception approval",
]

REFLECT_TOPICS = [
    "late refunds caused by integration failures",
    "when enterprise discount exceptions are approved",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Recall + reflect sweep across all Hindsight banks.")
    parser.add_argument("--rounds", type=int, default=1, help="How many times to repeat the sweep.")
    args = parser.parse_args(argv)
    s = get_settings()

    async def run() -> None:
        client = HindsightClient(api_key=s.HINDSIGHT_API_KEY, base_url=s.HINDSIGHT_BASE_URL, namespace=s.HINDSIGHT_NAMESPACE)
        recalls = reflects = 0
        for _ in range(args.rounds):
            for slug in SLUGS:
                bank = f"synthetic-bank-{slug}"
                for q in RECALL_QUERIES:
                    try:
                        await client.recall(bank, q, top_k=5)
                        recalls += 1
                    except Exception:  # noqa: BLE001
                        pass
                for t in REFLECT_TOPICS:
                    try:
                        await client.reflect(bank, t)
                        reflects += 1
                    except Exception:  # noqa: BLE001
                        pass
            print(f"  swept {len(SLUGS)} banks | recalls={recalls} reflects={reflects}")
        print(f"DONE: {recalls} recall ops + {reflects} reflect ops across {len(SLUGS)} banks")

    asyncio.run(run())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
