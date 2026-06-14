# ExceptionOS — Live Load Runbook (Supabase + Hindsight)

This is the exact sequence to put the deterministic synthetic dataset into the
live Supabase database and the live Hindsight Cloud memory banks. All commands
run from `backend/` and read credentials from `backend/.env` (never printed).

## Status / prerequisites

| Step | Needs | Present in `.env`? |
| --- | --- | --- |
| Hindsight ingest | `HINDSIGHT_API_KEY`, `HINDSIGHT_BASE_URL` | ✅ yes — **works today** |
| Supabase load (CRUD) | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` | ✅ yes |
| Supabase **migrations** (`CREATE TABLE`) | a Postgres connection (see below) | ❌ **missing — blocker** |

The PostgREST API behind the anon/service-role keys can only read/write tables
that **already exist** — it cannot create them. The schema must be applied via a
direct Postgres connection (or pasted into the Supabase SQL Editor) **once**,
after which the service-role load works.

## 1. Apply the schema (one-time)

Pick **either** path.

### Path A — programmatic (preferred)

Add a Postgres connection string to `backend/.env`. From the Supabase Dashboard:
**Project Settings → Database → Connection string → URI** (the pooler URI is
fine). Then:

```bash
# in backend/.env  (do NOT commit this)
DATABASE_URL=postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
# — or just the DB password, and the host is derived from SUPABASE_URL:
SUPABASE_DB_PASSWORD=<your-db-password>
```

```bash
python -m scripts.apply_migrations --dry-run   # lists pending files
python -m scripts.apply_migrations             # applies 001, 002, 004, 005
```

The script is idempotent (records applied files in `schema_migrations`) and
wraps each file in a transaction.

### Path B — manual paste (no extra credential)

Open the **Supabase SQL Editor** and paste the contents of
[`backend/migrations/_combined.sql`](../backend/migrations/_combined.sql)
(001 + 002 + 004 + 005, in order) and run it. It is idempotent
(`CREATE TABLE IF NOT EXISTS` / `ADD COLUMN IF NOT EXISTS`).

### Verify

```bash
python -m scripts.synthetic.seed_supabase --mode demo-small --dry-run
# should connect and print a load plan with no PGRST205 "table not found" errors
```

## 2. Load Supabase (idempotent upsert)

```bash
python -m scripts.synthetic.validate_dataset --mode demo-small   # gate
python -m scripts.synthetic.seed_supabase    --mode demo-small   # upsert by id
# re-runnable; use --reset to purge synthetic rows first
```

## 3. Ingest Hindsight (works today)

```bash
python -m scripts.synthetic.ingest_hindsight --mode demo-small --dry-run
python -m scripts.synthetic.ingest_hindsight --mode demo-small            # live
```

Banks (`synthetic-bank-<slug>`) are created via idempotent `PUT` before retain;
decision/outcome memories use stable document IDs so re-ingestion de-duplicates.

## 4. QA

```bash
cd backend && python -m pytest -q
```

Live API smoke (after schema + load): `GET /api/v1/insights/sla`,
`/insights/budgets`, `/hindsight/health`.

## Notes

- `DATABASE_URL` / `SUPABASE_DB_PASSWORD` are secrets — keep them in `.env`
  (git-ignored). Never commit or print them.
- `migrations/_combined.sql` is generated from the individual files; regenerate
  by concatenating `001`, `002`, `004`, `005` in order.
