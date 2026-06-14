# ExceptionOS Synthetic Data System

Deterministic, reproducible, **100% fictional** demo data for ExceptionOS. No
real people, customers, or company-confidential information is used. Every
generated row carries `synthetic: true` and is tracked in
`synthetic_data_registry`, so the entire dataset can be located and purged.

> Generator code lives in [`backend/scripts/synthetic/`](../backend/scripts/synthetic/).

## Why it exists

The platform needs a believable, multi-tenant corpus — companies, policies,
exception cases, agent debates, decisions, outcomes, budgets, SLAs, and
Hindsight memories — to demo decision intelligence end to end without touching
production data. The system is **deterministic**: the same seed always produces
the same primary keys (UUIDv5), so loads are idempotent and resets are exact.

## Modes

| Mode | Companies | Cases | Use |
| --- | --- | --- | --- |
| `demo-small` (default) | 12 | hero 30–40, others 10–15 (~165 total) | local demos, CI |
| `full-synthetic` | 15 | 40–60 each (~740 total) | staging / load |

The hero company is **NovaFlow Systems** (B2B workflow SaaS, **INR**), which
gets a richer policy set (refund policy v1→v2→v3) and curated hero cases.

## Determinism

- Seed: `EXCEPTIONOS_SYNTHETIC_SEED` (default `2026`).
- IDs: UUIDv5 from a fixed namespace + a stable path string
  (`backend/scripts/synthetic/ids.py`).
- Hindsight document IDs use the same stable scheme as the live app
  (`app/memory/document_ids.py`): `case:<org>:<case>:decision:<rec>` and
  `case:<org>:<case>:outcome`.

## Tables produced

25 tables in FK-safe order (see `schema.py:TABLE_LOAD_ORDER`):

`organizations`, `departments`, `exception_categories`, `policies`,
`policy_versions`, `feature_flags`, `sla_rules`, `exception_cases`,
`case_facts`, `case_evidence`, `recommendations`, `agent_runs`,
`agent_outputs`, `case_events`, `hindsight_operations`, `exception_budgets`,
`budget_transactions`, `benchmark_cohorts`, `policy_drift_findings`,
`repeated_exception_clusters`, `memory_contradictions`, `training_scenarios`,
`openclaw_sessions`, `voice_sessions`, `synthetic_data_registry`.

### Budgets & SLAs (spec logic)

- **`exception_budgets`** — one Q2-2026 budget per consuming category, with
  `spent_amount` reconciled to its transactions. Every 5th budget is
  intentionally **breached** (`spent_amount > budget_amount`) to exercise the
  over-budget dashboard state.
- **`budget_transactions`** — a `debit` per consuming case, a `credit` for
  released reservations, and an `adjustment` flagging overages.
- **`sla_rules`** — one canonical rule per category per org. The
  `operational_exception` rule is left **paused** (`active = false`) so every
  org exposes a paused-SLA state. Health (met / at-risk / breached / on-track)
  is derived at query time by `GET /api/v1/insights/sla`.

### Personas

Fictional internal users (requester, CSM, finance manager, CFO, auditor, …) are
**not** written to `profiles` (which FKs to `auth.users`). They are embedded as
JSON in `case_facts`, conversation/outcome artifacts, and Hindsight metadata.
Emails are always `*.example.com`.

## CLI

All commands run from `backend/` and load `backend/.env` for credentials. No
secret is ever printed.

```bash
# 1. Generate JSON (writes backend/scripts/synthetic/out/<mode>.json)
python -m scripts.synthetic.generate --mode demo-small --pretty
python -m scripts.synthetic.generate --mode demo-small --dry-run   # counts only

# 2. Validate (offline: flags, FK integrity, budget reconciliation, registry, PII/secrets)
python -m scripts.synthetic.validate_dataset --mode demo-small
#   exit code is non-zero on any error -> safe to gate CI on it

# 3. Load into Supabase (idempotent upsert by id; service-role key)
python -m scripts.synthetic.seed_supabase --mode demo-small --dry-run
python -m scripts.synthetic.seed_supabase --mode demo-small
python -m scripts.synthetic.seed_supabase --mode demo-small --reset   # purge synthetic rows first

# 4. Ingest case decisions/outcomes into Hindsight (stable doc IDs, idempotent)
python -m scripts.synthetic.ingest_hindsight --mode demo-small --dry-run
python -m scripts.synthetic.ingest_hindsight --mode demo-small --limit 25
```

The loader runs validation first and **aborts** if the dataset is invalid
(override with `--skip-validate`). The `exception_cases ⇄ recommendations`
circular FK is handled by inserting cases without `current_recommendation_id`,
then patching it after recommendations load.

## Safety & secrets

- `backend/.env` is git-ignored; loaders read env var **names** only.
- Generated `out/*.json` is git-ignored (unvalidated/large generated output).
- The validator scans every string value for API-key / JWT / private-key
  patterns and fails on a hit, and warns on any non-`example.com` email.
- All data is fictional; no real customer or personal data is present.

## Tests

`backend/tests/test_synthetic_dataset.py` and `test_insights_sla.py` cover
determinism, validation, budget reconciliation, SLA paused/breached states,
load ordering, the deferred-FK split, and Hindsight memory ID stability.

```bash
cd backend && python -m pytest tests/test_synthetic_dataset.py tests/test_insights_sla.py -q
```
