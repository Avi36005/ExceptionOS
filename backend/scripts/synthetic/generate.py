"""CLI for deterministic ExceptionOS synthetic data generation."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from scripts.synthetic.cases_gen import generate_dataset
from scripts.synthetic.config import (
    DEFAULT_MODE,
    MODE_DEMO_SMALL,
    MODE_FULL_SYNTHETIC,
    default_seed,
    load_env,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic ExceptionOS synthetic data as JSON."
    )
    parser.add_argument(
        "--mode",
        choices=(MODE_DEMO_SMALL, MODE_FULL_SYNTHETIC),
        default=DEFAULT_MODE,
        help="Generation size/profile.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Deterministic seed. Defaults to EXCEPTIONOS_SYNTHETIC_SEED or 2026.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON path. Use '-' for stdout. Defaults to backend/scripts/synthetic/out/<mode>.json.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON with indentation.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate in memory and print row counts without writing JSON.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    load_env()
    args = parse_args(argv)
    seed = args.seed if args.seed is not None else default_seed()
    dataset = generate_dataset(mode=args.mode, seed=seed)

    if args.dry_run:
        _print_summary(dataset)
        return 0

    payload = json.dumps(
        dataset,
        indent=2 if args.pretty else None,
        sort_keys=True,
        default=str,
    )
    if args.output == "-":
        print(payload)
        return 0

    output_path = Path(args.output) if args.output else Path(__file__).resolve().parent / "out" / f"{args.mode}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(payload + "\n", encoding="utf-8")
    _print_summary(dataset, output_path)
    return 0


def _print_summary(dataset: dict[str, Any], output_path: Path | None = None) -> None:
    metadata = dataset["metadata"]
    destination = f" -> {output_path}" if output_path else ""
    print(
        f"generated synthetic dataset mode={metadata['mode']} seed={metadata['seed']} "
        f"companies={metadata['company_count']}{destination}"
    )
    for table, count in sorted(dataset["counts"].items()):
        print(f"{table}: {count}")
    for name, items in sorted(dataset["artifacts"].items()):
        print(f"artifact.{name}: {len(items)}")


if __name__ == "__main__":
    raise SystemExit(main())
