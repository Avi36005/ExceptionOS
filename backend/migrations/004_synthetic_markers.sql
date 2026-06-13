-- =============================================================================
-- ExceptionOS — Synthetic Data Markers Migration
-- Adds an additive `synthetic` boolean flag to organization-scoped tables so
-- the synthetic-data generator (scripts/synthetic/) can identify and clean up
-- rows it created, without touching real tenant data.
-- Target: Supabase (PostgreSQL 15+)
-- =============================================================================

-- =============================================================================
-- organizations
-- =============================================================================

ALTER TABLE organizations
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_organizations_synthetic ON organizations (synthetic);

-- =============================================================================
-- departments / exception_categories
-- =============================================================================

ALTER TABLE departments
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE exception_categories
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

-- =============================================================================
-- policies / policy_versions
-- =============================================================================

ALTER TABLE policies
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE policy_versions
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

-- =============================================================================
-- exception_cases and related case data
-- =============================================================================

ALTER TABLE exception_cases
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_exc_cases_synthetic ON exception_cases (organization_id, synthetic);

ALTER TABLE case_facts
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE case_evidence
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE case_events
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

-- =============================================================================
-- recommendations / agent runs / outputs / precedent links
-- =============================================================================

ALTER TABLE recommendations
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE agent_runs
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE agent_outputs
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE precedent_links
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

-- =============================================================================
-- human_decisions / outcomes
-- =============================================================================

ALTER TABLE human_decisions
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE outcomes
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

-- =============================================================================
-- escalation / SLA / budgets
-- =============================================================================

ALTER TABLE escalation_rules
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE escalations
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE sla_rules
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE exception_budgets
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE budget_transactions
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

-- =============================================================================
-- memory / learning tables
-- =============================================================================

ALTER TABLE policy_drift_findings
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE repeated_exception_clusters
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE memory_contradictions
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE hindsight_operations
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

-- =============================================================================
-- training / benchmarks / voice / openclaw
-- =============================================================================

ALTER TABLE training_scenarios
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE training_attempts
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

-- benchmark_cohorts already has a `synthetic` column (default TRUE) from 002.

ALTER TABLE voice_sessions
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE openclaw_sessions
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE feature_flags
    ADD COLUMN IF NOT EXISTS synthetic BOOLEAN NOT NULL DEFAULT FALSE;

-- =============================================================================
-- SYNTHETIC RUN REGISTRY
-- A lightweight ledger of every row the generator has written, keyed by
-- organization + table + row id. Used by `scripts/synthetic` to support
-- `--reset` (delete all synthetic rows for an organization) without needing
-- bespoke delete logic per table, and to make re-runs idempotent.
-- =============================================================================

CREATE TABLE IF NOT EXISTS synthetic_data_registry (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    table_name      TEXT NOT NULL,
    row_id          UUID NOT NULL,
    generator_run_id TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (table_name, row_id)
);

CREATE INDEX IF NOT EXISTS idx_synthetic_registry_org   ON synthetic_data_registry (organization_id);
CREATE INDEX IF NOT EXISTS idx_synthetic_registry_table ON synthetic_data_registry (table_name);

ALTER TABLE synthetic_data_registry ENABLE ROW LEVEL SECURITY;

CREATE POLICY "synthetic_registry_select_member"
    ON synthetic_data_registry FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

-- =============================================================================
-- SERVICE ROLE BYPASS (backend uses service role key — bypasses RLS)
-- =============================================================================
