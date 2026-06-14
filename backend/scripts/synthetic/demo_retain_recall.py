"""Screenshot-friendly LIVE demo of ExceptionOS <-> Hindsight Cloud.

Runs REAL retain -> recall -> reflect calls against Hindsight and prints clean,
narrated output (the actual HTTP-backed operations, no mocks). Ideal for a
terminal screenshot proving the integration works.

Usage::

    python -m scripts.synthetic.demo_retain_recall
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import get_settings  # noqa: E402
from app.memory.hindsight_client import HindsightClient  # noqa: E402

BANK = "synthetic-bank-acme"
LINE = "=" * 70


def banner(title: str) -> None:
    print(f"\n{LINE}\n  {title}\n{LINE}")


async def main() -> None:
    s = get_settings()
    client = HindsightClient(api_key=s.HINDSIGHT_API_KEY, base_url=s.HINDSIGHT_BASE_URL, namespace=s.HINDSIGHT_NAMESPACE)

    print(LINE)
    print("  ExceptionOS  <->  Hindsight Cloud   (LIVE retain / recall / reflect)")
    print(f"  Endpoint : {s.HINDSIGHT_BASE_URL}")
    print(f"  Bank     : {BANK}")
    print(LINE)

    # ---- RETAIN -------------------------------------------------------------
    banner("STEP 1 - RETAIN  (store a real decision + outcome in memory)")
    memories = [
        ("decision", "Acme Retail: refund requested after 52 days; NovaFlow integration failure (our fault); "
                     "partial service. AI recommended 75% refund; CFO approved FULL refund of INR 120000 "
                     "to protect a INR 2,000,000 expansion."),
        ("outcome", "Acme Retail accepted the full refund, stayed, and signed the INR 2,000,000 expansion. "
                    "Decision rated 90/100."),
    ]
    for kind, text in memories:
        res = await client.retain(BANK, text, {"type": "case_decision" if kind == "decision" else "outcome",
                                               "tags": ["demo"], "case": "acme-live"},
                                  document_id=f"acme-live:{kind}")
        print(f"  >> RETAIN [{kind:8}]  ->  stored  (memory_id={res.get('id')})")

    # ---- RECALL -------------------------------------------------------------
    banner("STEP 2 - RECALL  (find similar past cases for a NEW request)")
    query = "customer wants a refund after an integration failure past the 30-day window"
    print(f"  Query: \"{query}\"\n")
    hits = await client.recall(BANK, query, top_k=5)
    print(f"  >> RECALL  ->  {len(hits)} memories returned. Top matches:\n")
    for i, m in enumerate(hits[:4], 1):
        text = str(m.get("content") or m.get("text") or m.get("memory") or "")[:110]
        print(f"     {i}. {text}...")

    # ---- REFLECT ------------------------------------------------------------
    banner("STEP 3 - REFLECT  (learn the pattern across all stored cases)")
    topic = "what do we usually do for late refunds caused by our own integration failures?"
    print(f"  Topic: \"{topic}\"\n")
    try:
        out = await client.reflect(BANK, topic)
        summary = str(out.get("summary") or out.get("answer") or out.get("content") or out)[:300]
        print(f"  >> REFLECT ->  {summary}")
    except Exception as exc:  # noqa: BLE001
        print(f"  >> REFLECT ->  (no summary returned: {exc})")

    print(f"\n{LINE}\n  DONE — real Retain / Recall / Reflect against Hindsight Cloud.\n{LINE}\n")


if __name__ == "__main__":
    asyncio.run(main())
