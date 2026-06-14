"""Apply ExceptionOS SQL migrations to Supabase Postgres.

The Supabase PostgREST API (anon/service-role keys) can only do CRUD on
tables that already exist — it cannot run ``CREATE TABLE``. Applying the
schema therefore needs a direct Postgres connection.

This script runs every ``migrations/*.sql`` file (in numeric order) against a
Postgres connection, inside a single transaction per file, and records applied
files in a ``schema_migrations`` bookkeeping table so re-runs are idempotent.

Connection resolution (first match wins):
  1. ``--dsn`` argument
  2. ``DATABASE_URL`` env var (e.g. the Supabase "Connection string" / pooler URL)
  3. ``SUPABASE_DB_PASSWORD`` env var + ``SUPABASE_URL`` (we derive the host)

No secret is ever printed.

Usage::

    # Preferred: paste the full Supabase connection string into backend/.env as
    #   DATABASE_URL=postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
    python -m scripts.apply_migrations
    python -m scripts.apply_migrations --dry-run     # list pending files only
    python -m scripts.apply_migrations --dsn "postgresql://..."
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import quote, urlparse

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

MIGRATIONS_DIR = BACKEND_DIR / "migrations"

from scripts.synthetic.config import get_env, load_env  # noqa: E402


def _resolve_dsn(cli_dsn: str | None) -> str | None:
    if cli_dsn:
        return cli_dsn
    dsn = get_env("DATABASE_URL")
    if dsn:
        return dsn
    # Derive from SUPABASE_URL host + SUPABASE_DB_PASSWORD (direct connection).
    password = get_env("SUPABASE_DB_PASSWORD")
    supabase_url = get_env("SUPABASE_URL")
    if password and supabase_url:
        host = urlparse(supabase_url).hostname or ""
        # https://<ref>.supabase.co -> db.<ref>.supabase.co
        ref = host.split(".")[0]
        if ref:
            # URL-encode the password so special chars (@, :, /, etc.) don't
            # corrupt the libpq URI parse.
            pw = quote(password, safe="")
            return f"postgresql://postgres:{pw}@db.{ref}.supabase.co:5432/postgres"
    return None


def _migration_files() -> list[Path]:
    # Exclude helper files like _combined.sql (the single-paste bundle).
    return sorted(
        (p for p in MIGRATIONS_DIR.glob("*.sql") if not p.name.startswith("_")),
        key=lambda p: p.name,
    )


def main(argv: list[str] | None = None) -> int:
    load_env()
    parser = argparse.ArgumentParser(description="Apply ExceptionOS SQL migrations to Supabase Postgres.")
    parser.add_argument("--dsn", default=None, help="Postgres connection string (overrides env).")
    parser.add_argument("--dry-run", action="store_true", help="List migration files without applying.")
    args = parser.parse_args(argv)

    files = _migration_files()
    if not files:
        print(f"No .sql files found in {MIGRATIONS_DIR}")
        return 1
    print(f"found {len(files)} migration file(s): {', '.join(f.name for f in files)}")

    if args.dry_run:
        print("[dry-run] not connecting; the above files would be applied in order.")
        return 0

    dsn = _resolve_dsn(args.dsn)
    if not dsn:
        print(
            "ERROR: no database connection available.\n"
            "  Provide ONE of:\n"
            "    - DATABASE_URL in backend/.env (Supabase Dashboard > Project Settings > Database > Connection string)\n"
            "    - SUPABASE_DB_PASSWORD in backend/.env (we derive the host from SUPABASE_URL)\n"
            "    - --dsn 'postgresql://...'\n"
            "  Alternatively, paste migrations/_combined.sql into the Supabase SQL Editor.",
            file=sys.stderr,
        )
        return 2

    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 is required. pip install psycopg2-binary", file=sys.stderr)
        return 2

    conn = psycopg2.connect(dsn)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS schema_migrations ("
                "  filename TEXT PRIMARY KEY,"
                "  applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"
            )
            conn.commit()
            cur.execute("SELECT filename FROM schema_migrations")
            applied = {row[0] for row in cur.fetchall()}

        for path in files:
            if path.name in applied:
                print(f"  skip {path.name} (already applied)")
                continue
            sql = path.read_text(encoding="utf-8")
            print(f"  applying {path.name} ...", end=" ", flush=True)
            with conn.cursor() as cur:
                cur.execute(sql)
                cur.execute(
                    "INSERT INTO schema_migrations (filename) VALUES (%s) "
                    "ON CONFLICT (filename) DO NOTHING",
                    (path.name,),
                )
            conn.commit()
            print("done")
    except Exception as exc:
        conn.rollback()
        print(f"\nFAILED: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    print("all migrations applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
