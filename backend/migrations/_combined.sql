-- =============================================================================
-- ExceptionOS — COMBINED migration (auto-generated; paste into Supabase SQL Editor)
-- Order: 001_initial, 002_extended_schema, 004_synthetic_markers, 005_openclaw_extensions
-- Idempotent (CREATE TABLE IF NOT EXISTS / ADD COLUMN IF NOT EXISTS).
-- =============================================================================

-- >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  001_initial.sql  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
-- =============================================================================
-- ExceptionOS — Initial Database Migration
-- Target: Supabase (PostgreSQL 15+)
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- ORGANISATIONS
-- =============================================================================

CREATE TABLE IF NOT EXISTS organizations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    slug            TEXT NOT NULL UNIQUE,
    industry        TEXT,
    size            TEXT,
    currency        TEXT NOT NULL DEFAULT 'USD',
    timezone        TEXT NOT NULL DEFAULT 'UTC',
    status          TEXT NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'suspended', 'trial')),
    hindsight_bank_id TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_organizations_slug    ON organizations (slug);
CREATE INDEX IF NOT EXISTS idx_organizations_status  ON organizations (status);

-- =============================================================================
-- PROFILES (extends auth.users)
-- =============================================================================

CREATE TABLE IF NOT EXISTS profiles (
    id              UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name    TEXT,
    avatar_url      TEXT,
    timezone        TEXT DEFAULT 'UTC',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- DEPARTMENTS
-- =============================================================================

CREATE TABLE IF NOT EXISTS departments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name                TEXT NOT NULL,
    code                TEXT,
    manager_user_id     UUID REFERENCES profiles(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_departments_org ON departments (organization_id);

-- =============================================================================
-- ORGANISATION MEMBERSHIPS
-- =============================================================================

CREATE TABLE IF NOT EXISTS organization_memberships (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    role            TEXT NOT NULL DEFAULT 'viewer'
                        CHECK (role IN ('owner', 'admin', 'manager', 'analyst', 'viewer')),
    department_id   UUID REFERENCES departments(id) ON DELETE SET NULL,
    status          TEXT NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'pending', 'removed')),
    invited_by      UUID REFERENCES profiles(id) ON DELETE SET NULL,
    joined_at       TIMESTAMPTZ,
    UNIQUE (organization_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_memberships_org    ON organization_memberships (organization_id);
CREATE INDEX IF NOT EXISTS idx_memberships_user   ON organization_memberships (user_id);
CREATE INDEX IF NOT EXISTS idx_memberships_status ON organization_memberships (status);

-- =============================================================================
-- EXCEPTION CATEGORIES
-- =============================================================================

CREATE TABLE IF NOT EXISTS exception_categories (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id             UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name                        TEXT NOT NULL,
    code                        TEXT,
    description                 TEXT,
    default_sla_minutes         INTEGER DEFAULT 2880,  -- 48 hours
    default_escalation_rule_id  UUID,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_exc_categories_org ON exception_categories (organization_id);

-- =============================================================================
-- POLICIES
-- =============================================================================

CREATE TABLE IF NOT EXISTS policies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    category        TEXT,
    status          TEXT NOT NULL DEFAULT 'draft'
                        CHECK (status IN ('draft', 'active', 'archived')),
    owner_user_id   UUID REFERENCES profiles(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_policies_org    ON policies (organization_id);
CREATE INDEX IF NOT EXISTS idx_policies_status ON policies (status);

-- =============================================================================
-- POLICY VERSIONS
-- =============================================================================

CREATE TABLE IF NOT EXISTS policy_versions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id               UUID NOT NULL REFERENCES policies(id) ON DELETE CASCADE,
    version_label           TEXT NOT NULL,
    content                 TEXT NOT NULL,
    effective_from          TIMESTAMPTZ,
    effective_to            TIMESTAMPTZ,
    status                  TEXT NOT NULL DEFAULT 'draft'
                                CHECK (status IN ('draft', 'active', 'archived')),
    created_by              UUID REFERENCES profiles(id) ON DELETE SET NULL,
    approved_by             UUID REFERENCES profiles(id) ON DELETE SET NULL,
    hindsight_document_id   TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_policy_versions_policy ON policy_versions (policy_id);
CREATE INDEX IF NOT EXISTS idx_policy_versions_status ON policy_versions (status);

-- =============================================================================
-- EXCEPTION CASES
-- =============================================================================

CREATE TABLE IF NOT EXISTS exception_cases (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id             UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    case_number                 TEXT NOT NULL UNIQUE,
    category_id                 UUID REFERENCES exception_categories(id) ON DELETE SET NULL,
    department_id               UUID REFERENCES departments(id) ON DELETE SET NULL,
    requester_user_id           UUID REFERENCES profiles(id) ON DELETE SET NULL,
    assignee_user_id            UUID REFERENCES profiles(id) ON DELETE SET NULL,
    title                       TEXT NOT NULL,
    description                 TEXT,
    entity_name                 TEXT,
    requested_amount            NUMERIC(20, 4),
    currency                    TEXT NOT NULL DEFAULT 'USD',
    annual_value                NUMERIC(20, 4),
    request_date                TIMESTAMPTZ,
    transaction_date            TIMESTAMPTZ,
    root_cause                  TEXT,
    urgency                     TEXT NOT NULL DEFAULT 'medium'
                                    CHECK (urgency IN ('low', 'medium', 'high', 'critical')),
    status                      TEXT NOT NULL DEFAULT 'draft'
                                    CHECK (status IN (
                                        'draft', 'submitted', 'intake', 'analyzing',
                                        'pending_decision', 'approved', 'partially_approved',
                                        'denied', 'escalated', 'closed'
                                    )),
    current_policy_version_id   UUID REFERENCES policy_versions(id) ON DELETE SET NULL,
    current_recommendation_id   UUID,  -- FK added after recommendations table
    sla_due_at                  TIMESTAMPTZ,
    resolved_at                 TIMESTAMPTZ,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    version                     INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_exc_cases_org       ON exception_cases (organization_id);
CREATE INDEX IF NOT EXISTS idx_exc_cases_status    ON exception_cases (status);
CREATE INDEX IF NOT EXISTS idx_exc_cases_requester ON exception_cases (requester_user_id);
CREATE INDEX IF NOT EXISTS idx_exc_cases_assignee  ON exception_cases (assignee_user_id);
CREATE INDEX IF NOT EXISTS idx_exc_cases_number    ON exception_cases (case_number);

-- =============================================================================
-- CASE FACTS
-- =============================================================================

CREATE TABLE IF NOT EXISTS case_facts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id     UUID NOT NULL REFERENCES exception_cases(id) ON DELETE CASCADE,
    key         TEXT NOT NULL,
    value_json  JSONB NOT NULL DEFAULT '""',
    source      TEXT DEFAULT 'intake_agent',
    confidence  NUMERIC(4, 3) DEFAULT 0.8,
    verified    BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_case_facts_case ON case_facts (case_id);

-- =============================================================================
-- CASE EVIDENCE
-- =============================================================================

CREATE TABLE IF NOT EXISTS case_evidence (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id             UUID NOT NULL REFERENCES exception_cases(id) ON DELETE CASCADE,
    file_path           TEXT,
    evidence_type       TEXT,
    title               TEXT,
    extracted_text      TEXT,
    verification_status TEXT DEFAULT 'pending',
    uploaded_by         UUID REFERENCES profiles(id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_case_evidence_case ON case_evidence (case_id);

-- =============================================================================
-- CASE EVENTS (audit log)
-- =============================================================================

CREATE TABLE IF NOT EXISTS case_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id         UUID NOT NULL REFERENCES exception_cases(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    event_type      TEXT NOT NULL,
    actor_type      TEXT NOT NULL DEFAULT 'user'
                        CHECK (actor_type IN ('user', 'agent', 'system', 'webhook')),
    actor_id        TEXT,
    payload_json    JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_case_events_case ON case_events (case_id);
CREATE INDEX IF NOT EXISTS idx_case_events_type ON case_events (event_type);

-- =============================================================================
-- RECOMMENDATIONS
-- =============================================================================

CREATE TABLE IF NOT EXISTS recommendations (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id                 UUID NOT NULL REFERENCES exception_cases(id) ON DELETE CASCADE,
    version                 INTEGER NOT NULL DEFAULT 1,
    recommendation_type     TEXT NOT NULL
                                CHECK (recommendation_type IN (
                                    'approve', 'partially_approve', 'deny',
                                    'escalate', 'needs_more_info'
                                )),
    recommended_amount      NUMERIC(20, 4),
    conditions_json         JSONB DEFAULT '[]',
    confidence              NUMERIC(4, 3) NOT NULL DEFAULT 0.5,
    reasoning               TEXT NOT NULL DEFAULT '',
    risk_json               JSONB DEFAULT '{}',
    provider_summary_json   JSONB DEFAULT '{}',
    hindsight_evidence_json JSONB DEFAULT '[]',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_recommendations_case ON recommendations (case_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_type ON recommendations (recommendation_type);

-- Add FK from exception_cases to recommendations
ALTER TABLE exception_cases
    ADD CONSTRAINT fk_current_recommendation
    FOREIGN KEY (current_recommendation_id)
    REFERENCES recommendations(id)
    ON DELETE SET NULL
    DEFERRABLE INITIALLY DEFERRED;

-- =============================================================================
-- AGENT RUNS
-- =============================================================================

CREATE TABLE IF NOT EXISTS agent_runs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id             UUID NOT NULL REFERENCES exception_cases(id) ON DELETE CASCADE,
    run_type            TEXT NOT NULL DEFAULT 'full_debate',
    status              TEXT NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    started_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at        TIMESTAMPTZ,
    trace_id            TEXT,
    final_provider      TEXT,
    fallback_path_json  JSONB DEFAULT '[]',
    latency_ms          INTEGER,
    token_usage_json    JSONB DEFAULT '{}',
    error_json          JSONB
);

CREATE INDEX IF NOT EXISTS idx_agent_runs_case   ON agent_runs (case_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_status ON agent_runs (status);

-- =============================================================================
-- AGENT OUTPUTS
-- =============================================================================

CREATE TABLE IF NOT EXISTS agent_outputs (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_run_id            UUID NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    agent_name              TEXT NOT NULL,
    provider                TEXT,
    model                   TEXT,
    status                  TEXT NOT NULL DEFAULT 'completed',
    structured_output_json  JSONB DEFAULT '{}',
    latency_ms              INTEGER,
    token_usage_json        JSONB DEFAULT '{}',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_outputs_run ON agent_outputs (agent_run_id);

-- =============================================================================
-- PRECEDENT LINKS
-- =============================================================================

CREATE TABLE IF NOT EXISTS precedent_links (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id                 UUID NOT NULL REFERENCES exception_cases(id) ON DELETE CASCADE,
    precedent_case_id       UUID,  -- may reference a historical case or be external
    similarity_score        NUMERIC(4, 3) DEFAULT 0.0,
    similarity_reasons_json JSONB DEFAULT '[]',
    difference_reasons_json JSONB DEFAULT '[]',
    memory_confidence       NUMERIC(4, 3) DEFAULT 0.0,
    relevance_adjustment    NUMERIC(4, 3) DEFAULT 0.0,
    source_memory_ids_json  JSONB DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_precedent_links_case  ON precedent_links (case_id);
CREATE INDEX IF NOT EXISTS idx_precedent_links_score ON precedent_links (similarity_score DESC);

-- =============================================================================
-- HUMAN DECISIONS
-- =============================================================================

CREATE TABLE IF NOT EXISTS human_decisions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id             UUID NOT NULL REFERENCES exception_cases(id) ON DELETE CASCADE,
    recommendation_id   UUID REFERENCES recommendations(id) ON DELETE SET NULL,
    decision_type       TEXT NOT NULL
                            CHECK (decision_type IN (
                                'approved', 'partially_approved', 'denied', 'escalated'
                            )),
    approved_amount     NUMERIC(20, 4),
    conditions_json     JSONB DEFAULT '[]',
    reasoning           TEXT NOT NULL DEFAULT '',
    override            BOOLEAN NOT NULL DEFAULT FALSE,
    decided_by          UUID NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
    decided_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_human_decisions_case ON human_decisions (case_id);

-- =============================================================================
-- OUTCOMES
-- =============================================================================

CREATE TABLE IF NOT EXISTS outcomes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id         UUID NOT NULL REFERENCES exception_cases(id) ON DELETE CASCADE,
    decision_id     UUID REFERENCES human_decisions(id) ON DELETE SET NULL,
    actual_outcome  TEXT NOT NULL,
    outcome_date    TIMESTAMPTZ,
    financial_impact NUMERIC(20, 4),
    notes           TEXT,
    recorded_by     UUID NOT NULL REFERENCES profiles(id) ON DELETE RESTRICT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_outcomes_case ON outcomes (case_id);

-- =============================================================================
-- OPENCLAW SESSIONS
-- =============================================================================

CREATE TABLE IF NOT EXISTS openclaw_sessions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID REFERENCES organizations(id) ON DELETE SET NULL,
    external_session_id TEXT NOT NULL UNIQUE,
    channel             TEXT NOT NULL DEFAULT 'chat',
    linked_case_id      UUID REFERENCES exception_cases(id) ON DELETE SET NULL,
    action_type         TEXT,
    status              TEXT NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active', 'closed', 'error')),
    metadata_json       JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_openclaw_sessions_org    ON openclaw_sessions (organization_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_sessions_ext    ON openclaw_sessions (external_session_id);
CREATE INDEX IF NOT EXISTS idx_openclaw_sessions_status ON openclaw_sessions (status);

-- =============================================================================
-- TRIGGERS — updated_at
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_organizations_updated_at') THEN
        CREATE TRIGGER trg_organizations_updated_at
            BEFORE UPDATE ON organizations
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_exception_cases_updated_at') THEN
        CREATE TRIGGER trg_exception_cases_updated_at
            BEFORE UPDATE ON exception_cases
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_openclaw_sessions_updated_at') THEN
        CREATE TRIGGER trg_openclaw_sessions_updated_at
            BEFORE UPDATE ON openclaw_sessions
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

-- Enable RLS on all tenant-scoped tables
ALTER TABLE organizations             ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE departments               ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_memberships  ENABLE ROW LEVEL SECURITY;
ALTER TABLE exception_categories      ENABLE ROW LEVEL SECURITY;
ALTER TABLE policies                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE policy_versions           ENABLE ROW LEVEL SECURITY;
ALTER TABLE exception_cases           ENABLE ROW LEVEL SECURITY;
ALTER TABLE case_facts                ENABLE ROW LEVEL SECURITY;
ALTER TABLE case_evidence             ENABLE ROW LEVEL SECURITY;
ALTER TABLE case_events               ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations           ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_runs                ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_outputs             ENABLE ROW LEVEL SECURITY;
ALTER TABLE precedent_links           ENABLE ROW LEVEL SECURITY;
ALTER TABLE human_decisions           ENABLE ROW LEVEL SECURITY;
ALTER TABLE outcomes                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE openclaw_sessions         ENABLE ROW LEVEL SECURITY;

-- ── Helper function ──────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION auth_user_org_ids()
RETURNS SETOF UUID AS $$
    SELECT organization_id
    FROM organization_memberships
    WHERE user_id = auth.uid()
      AND status = 'active';
$$ LANGUAGE SQL STABLE SECURITY DEFINER;

-- ── profiles ─────────────────────────────────────────────────────────────────

CREATE POLICY "profiles_select_own"
    ON profiles FOR SELECT
    USING (id = auth.uid());

CREATE POLICY "profiles_update_own"
    ON profiles FOR UPDATE
    USING (id = auth.uid());

CREATE POLICY "profiles_insert_own"
    ON profiles FOR INSERT
    WITH CHECK (id = auth.uid());

-- ── organizations ─────────────────────────────────────────────────────────────

CREATE POLICY "orgs_select_member"
    ON organizations FOR SELECT
    USING (id IN (SELECT auth_user_org_ids()));

CREATE POLICY "orgs_insert_authenticated"
    ON organizations FOR INSERT
    WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "orgs_update_admin"
    ON organizations FOR UPDATE
    USING (
        id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid()
              AND role IN ('owner', 'admin')
              AND status = 'active'
        )
    );

-- ── organization_memberships ──────────────────────────────────────────────────

CREATE POLICY "memberships_select_member"
    ON organization_memberships FOR SELECT
    USING (
        organization_id IN (SELECT auth_user_org_ids())
        OR user_id = auth.uid()
    );

CREATE POLICY "memberships_insert_admin"
    ON organization_memberships FOR INSERT
    WITH CHECK (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid()
              AND role IN ('owner', 'admin')
              AND status = 'active'
        )
    );

-- ── exception_cases ───────────────────────────────────────────────────────────

CREATE POLICY "cases_select_member"
    ON exception_cases FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

CREATE POLICY "cases_insert_member"
    ON exception_cases FOR INSERT
    WITH CHECK (organization_id IN (SELECT auth_user_org_ids()));

CREATE POLICY "cases_update_member"
    ON exception_cases FOR UPDATE
    USING (organization_id IN (SELECT auth_user_org_ids()));

-- ── policies ──────────────────────────────────────────────────────────────────

CREATE POLICY "policies_select_member"
    ON policies FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

CREATE POLICY "policies_insert_admin"
    ON policies FOR INSERT
    WITH CHECK (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid()
              AND role IN ('owner', 'admin', 'manager')
              AND status = 'active'
        )
    );

CREATE POLICY "policies_update_admin"
    ON policies FOR UPDATE
    USING (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid()
              AND role IN ('owner', 'admin', 'manager')
              AND status = 'active'
        )
    );

-- ── policy_versions ───────────────────────────────────────────────────────────

CREATE POLICY "policy_versions_select_member"
    ON policy_versions FOR SELECT
    USING (
        policy_id IN (
            SELECT id FROM policies
            WHERE organization_id IN (SELECT auth_user_org_ids())
        )
    );

-- ── case_facts ────────────────────────────────────────────────────────────────

CREATE POLICY "case_facts_select_member"
    ON case_facts FOR SELECT
    USING (
        case_id IN (
            SELECT id FROM exception_cases
            WHERE organization_id IN (SELECT auth_user_org_ids())
        )
    );

-- ── recommendations ───────────────────────────────────────────────────────────

CREATE POLICY "recommendations_select_member"
    ON recommendations FOR SELECT
    USING (
        case_id IN (
            SELECT id FROM exception_cases
            WHERE organization_id IN (SELECT auth_user_org_ids())
        )
    );

-- ── human_decisions ───────────────────────────────────────────────────────────

CREATE POLICY "decisions_select_member"
    ON human_decisions FOR SELECT
    USING (
        case_id IN (
            SELECT id FROM exception_cases
            WHERE organization_id IN (SELECT auth_user_org_ids())
        )
    );

CREATE POLICY "decisions_insert_manager"
    ON human_decisions FOR INSERT
    WITH CHECK (
        case_id IN (
            SELECT ec.id FROM exception_cases ec
            JOIN organization_memberships om
              ON om.organization_id = ec.organization_id
             AND om.user_id = auth.uid()
             AND om.role IN ('owner', 'admin', 'manager')
             AND om.status = 'active'
        )
    );

-- ── outcomes ──────────────────────────────────────────────────────────────────

CREATE POLICY "outcomes_select_member"
    ON outcomes FOR SELECT
    USING (
        case_id IN (
            SELECT id FROM exception_cases
            WHERE organization_id IN (SELECT auth_user_org_ids())
        )
    );

-- ── case_events ───────────────────────────────────────────────────────────────

CREATE POLICY "case_events_select_member"
    ON case_events FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

-- ── agent_runs ────────────────────────────────────────────────────────────────

CREATE POLICY "agent_runs_select_member"
    ON agent_runs FOR SELECT
    USING (
        case_id IN (
            SELECT id FROM exception_cases
            WHERE organization_id IN (SELECT auth_user_org_ids())
        )
    );

-- ── departments ───────────────────────────────────────────────────────────────

CREATE POLICY "departments_select_member"
    ON departments FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

-- ── exception_categories ─────────────────────────────────────────────────────

CREATE POLICY "exc_categories_select_member"
    ON exception_categories FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

-- ── openclaw_sessions ─────────────────────────────────────────────────────────

CREATE POLICY "openclaw_select_member"
    ON openclaw_sessions FOR SELECT
    USING (
        organization_id IS NULL
        OR organization_id IN (SELECT auth_user_org_ids())
    );

-- =============================================================================
-- SERVICE ROLE BYPASS (backend uses service role key — bypasses RLS)
-- The policies above apply to authenticated frontend clients using anon key.
-- =============================================================================


-- >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  002_extended_schema.sql  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
-- =============================================================================
-- ExceptionOS — Extended Schema Migration
-- Adds tables required by the Architecture spec that were not part of 001:
-- hindsight_operations, audit_logs, llm_usage, notifications,
-- escalation_rules, escalations, sla_rules, exception_budgets,
-- budget_transactions, policy_drift_findings, repeated_exception_clusters,
-- memory_contradictions, training_scenarios, training_attempts,
-- benchmark_cohorts, voice_sessions, feature_flags
-- Target: Supabase (PostgreSQL 15+)
-- =============================================================================

-- =============================================================================
-- HINDSIGHT OPERATIONS (Retain / Recall / Reflect operation log)
-- =============================================================================

CREATE TABLE IF NOT EXISTS hindsight_operations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    case_id         UUID REFERENCES exception_cases(id) ON DELETE SET NULL,
    agent_run_id    UUID REFERENCES agent_runs(id) ON DELETE SET NULL,
    operation_type  TEXT NOT NULL
                        CHECK (operation_type IN ('retain', 'recall', 'reflect')),
    document_id     TEXT,
    bank_id         TEXT,
    status          TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'completed', 'failed')),
    request_json    JSONB DEFAULT '{}',
    response_json   JSONB DEFAULT '{}',
    latency_ms      INTEGER,
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_hindsight_ops_org    ON hindsight_operations (organization_id);
CREATE INDEX IF NOT EXISTS idx_hindsight_ops_case   ON hindsight_operations (case_id);
CREATE INDEX IF NOT EXISTS idx_hindsight_ops_type   ON hindsight_operations (operation_type);
CREATE INDEX IF NOT EXISTS idx_hindsight_ops_status ON hindsight_operations (status);
CREATE INDEX IF NOT EXISTS idx_hindsight_ops_created ON hindsight_operations (created_at DESC);

-- =============================================================================
-- AUDIT LOGS (immutable, org-wide audit trail)
-- =============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    actor_type      TEXT NOT NULL DEFAULT 'user'
                        CHECK (actor_type IN ('user', 'agent', 'system', 'webhook')),
    actor_id        TEXT,
    action          TEXT NOT NULL,
    resource_type   TEXT NOT NULL,
    resource_id     TEXT,
    payload_json    JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_org      ON audit_logs (organization_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs (resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created  ON audit_logs (created_at DESC);

-- =============================================================================
-- LLM USAGE (per-call token + cost ledger)
-- =============================================================================

CREATE TABLE IF NOT EXISTS llm_usage (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    case_id             UUID REFERENCES exception_cases(id) ON DELETE SET NULL,
    agent_run_id        UUID REFERENCES agent_runs(id) ON DELETE SET NULL,
    agent_name          TEXT,
    provider            TEXT NOT NULL,
    model               TEXT NOT NULL,
    prompt_tokens       INTEGER NOT NULL DEFAULT 0,
    completion_tokens   INTEGER NOT NULL DEFAULT 0,
    total_tokens        INTEGER NOT NULL DEFAULT 0,
    cost_usd            NUMERIC(12, 6) NOT NULL DEFAULT 0,
    latency_ms          INTEGER,
    status              TEXT NOT NULL DEFAULT 'success'
                            CHECK (status IN ('success', 'error', 'fallback')),
    failure_category    TEXT
                            CHECK (failure_category IS NULL OR failure_category IN (
                                'timeout', 'rate_limit', 'authentication_error', 'provider_5xx',
                                'invalid_response', 'schema_validation', 'content_filter',
                                'context_too_large'
                            )),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_llm_usage_org      ON llm_usage (organization_id);
CREATE INDEX IF NOT EXISTS idx_llm_usage_case     ON llm_usage (case_id);
CREATE INDEX IF NOT EXISTS idx_llm_usage_provider ON llm_usage (provider);
CREATE INDEX IF NOT EXISTS idx_llm_usage_created  ON llm_usage (created_at DESC);

-- =============================================================================
-- NOTIFICATIONS (per-user notification queue)
-- =============================================================================

CREATE TABLE IF NOT EXISTS notifications (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    notification_type   TEXT NOT NULL,
    title               TEXT NOT NULL,
    body                TEXT,
    link                TEXT,
    related_case_id     UUID REFERENCES exception_cases(id) ON DELETE SET NULL,
    read                BOOLEAN NOT NULL DEFAULT FALSE,
    read_at             TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notifications_org  ON notifications (organization_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications (user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications (user_id, read);

-- =============================================================================
-- ESCALATION RULES
-- =============================================================================

CREATE TABLE IF NOT EXISTS escalation_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    category_id         UUID REFERENCES exception_categories(id) ON DELETE CASCADE,
    name                TEXT NOT NULL,
    min_amount          NUMERIC(20, 4),
    max_amount          NUMERIC(20, 4),
    required_role       TEXT NOT NULL DEFAULT 'manager'
                            CHECK (required_role IN ('owner', 'admin', 'manager', 'analyst', 'viewer')),
    escalate_to_role    TEXT NOT NULL DEFAULT 'admin'
                            CHECK (escalate_to_role IN ('owner', 'admin', 'manager', 'analyst', 'viewer')),
    active              BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_escalation_rules_org      ON escalation_rules (organization_id);
CREATE INDEX IF NOT EXISTS idx_escalation_rules_category ON escalation_rules (category_id);

-- Link exception_categories.default_escalation_rule_id (column existed without FK in 001)
ALTER TABLE exception_categories
    ADD CONSTRAINT fk_default_escalation_rule
    FOREIGN KEY (default_escalation_rule_id)
    REFERENCES escalation_rules(id)
    ON DELETE SET NULL
    DEFERRABLE INITIALLY DEFERRED;

-- =============================================================================
-- ESCALATIONS (actual escalation records per case)
-- =============================================================================

CREATE TABLE IF NOT EXISTS escalations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id             UUID NOT NULL REFERENCES exception_cases(id) ON DELETE CASCADE,
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    escalation_rule_id  UUID REFERENCES escalation_rules(id) ON DELETE SET NULL,
    from_role           TEXT,
    to_role             TEXT NOT NULL,
    reason              TEXT,
    status              TEXT NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending', 'acknowledged', 'resolved')),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at         TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_escalations_case   ON escalations (case_id);
CREATE INDEX IF NOT EXISTS idx_escalations_org    ON escalations (organization_id);
CREATE INDEX IF NOT EXISTS idx_escalations_status ON escalations (status);

-- =============================================================================
-- SLA RULES
-- =============================================================================

CREATE TABLE IF NOT EXISTS sla_rules (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id         UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    category_id             UUID REFERENCES exception_categories(id) ON DELETE CASCADE,
    urgency                 TEXT NOT NULL DEFAULT 'medium'
                                CHECK (urgency IN ('low', 'medium', 'high', 'critical')),
    sla_minutes             INTEGER NOT NULL DEFAULT 2880,
    warning_threshold_pct   NUMERIC(4, 3) NOT NULL DEFAULT 0.75,
    active                  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sla_rules_org      ON sla_rules (organization_id);
CREATE INDEX IF NOT EXISTS idx_sla_rules_category ON sla_rules (category_id);

-- =============================================================================
-- EXCEPTION BUDGETS + TRANSACTIONS
-- =============================================================================

CREATE TABLE IF NOT EXISTS exception_budgets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    department_id   UUID REFERENCES departments(id) ON DELETE CASCADE,
    category_id     UUID REFERENCES exception_categories(id) ON DELETE CASCADE,
    period_start    DATE NOT NULL,
    period_end      DATE NOT NULL,
    budget_amount   NUMERIC(20, 4) NOT NULL,
    currency        TEXT NOT NULL DEFAULT 'USD',
    spent_amount    NUMERIC(20, 4) NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_exception_budgets_org    ON exception_budgets (organization_id);
CREATE INDEX IF NOT EXISTS idx_exception_budgets_dept   ON exception_budgets (department_id);
CREATE INDEX IF NOT EXISTS idx_exception_budgets_period ON exception_budgets (period_start, period_end);

CREATE TABLE IF NOT EXISTS budget_transactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    budget_id           UUID NOT NULL REFERENCES exception_budgets(id) ON DELETE CASCADE,
    case_id             UUID REFERENCES exception_cases(id) ON DELETE SET NULL,
    amount              NUMERIC(20, 4) NOT NULL,
    transaction_type    TEXT NOT NULL DEFAULT 'debit'
                            CHECK (transaction_type IN ('debit', 'credit', 'adjustment')),
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_budget_txns_budget ON budget_transactions (budget_id);
CREATE INDEX IF NOT EXISTS idx_budget_txns_case   ON budget_transactions (case_id);

-- =============================================================================
-- POLICY DRIFT FINDINGS
-- =============================================================================

CREATE TABLE IF NOT EXISTS policy_drift_findings (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id         UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    policy_id               UUID REFERENCES policies(id) ON DELETE CASCADE,
    policy_version_id       UUID REFERENCES policy_versions(id) ON DELETE SET NULL,
    finding_type            TEXT NOT NULL,
    description             TEXT NOT NULL,
    evidence_json           JSONB DEFAULT '[]',
    affected_case_ids_json  JSONB DEFAULT '[]',
    severity                TEXT NOT NULL DEFAULT 'medium'
                                CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    status                  TEXT NOT NULL DEFAULT 'open'
                                CHECK (status IN ('open', 'acknowledged', 'resolved', 'dismissed')),
    detected_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at             TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_policy_drift_org    ON policy_drift_findings (organization_id);
CREATE INDEX IF NOT EXISTS idx_policy_drift_policy ON policy_drift_findings (policy_id);
CREATE INDEX IF NOT EXISTS idx_policy_drift_status ON policy_drift_findings (status);

-- =============================================================================
-- REPEATED EXCEPTION CLUSTERS
-- =============================================================================

CREATE TABLE IF NOT EXISTS repeated_exception_clusters (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    cluster_key         TEXT NOT NULL,
    title               TEXT NOT NULL,
    description         TEXT,
    root_cause          TEXT,
    case_ids_json       JSONB DEFAULT '[]',
    occurrence_count    INTEGER NOT NULL DEFAULT 0,
    first_seen_at       TIMESTAMPTZ,
    last_seen_at        TIMESTAMPTZ,
    status              TEXT NOT NULL DEFAULT 'open'
                            CHECK (status IN ('open', 'acknowledged', 'resolved')),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_repeated_clusters_org    ON repeated_exception_clusters (organization_id);
CREATE INDEX IF NOT EXISTS idx_repeated_clusters_status ON repeated_exception_clusters (status);

-- =============================================================================
-- MEMORY CONTRADICTIONS
-- =============================================================================

CREATE TABLE IF NOT EXISTS memory_contradictions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    memory_id_a         TEXT NOT NULL,
    memory_id_b         TEXT NOT NULL,
    case_id_a           UUID REFERENCES exception_cases(id) ON DELETE SET NULL,
    case_id_b           UUID REFERENCES exception_cases(id) ON DELETE SET NULL,
    contradiction_type  TEXT NOT NULL,
    description         TEXT NOT NULL,
    severity            TEXT NOT NULL DEFAULT 'medium'
                            CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    status              TEXT NOT NULL DEFAULT 'open'
                            CHECK (status IN ('open', 'acknowledged', 'resolved')),
    detected_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at         TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_memory_contradictions_org    ON memory_contradictions (organization_id);
CREATE INDEX IF NOT EXISTS idx_memory_contradictions_status ON memory_contradictions (status);

-- =============================================================================
-- TRAINING SCENARIOS + ATTEMPTS
-- =============================================================================

CREATE TABLE IF NOT EXISTS training_scenarios (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id         UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    source_case_id          UUID REFERENCES exception_cases(id) ON DELETE SET NULL,
    category_id             UUID REFERENCES exception_categories(id) ON DELETE SET NULL,
    title                   TEXT NOT NULL,
    description             TEXT,
    scenario_json           JSONB NOT NULL DEFAULT '{}',
    correct_decision_json   JSONB DEFAULT '{}',
    difficulty              TEXT NOT NULL DEFAULT 'medium'
                                CHECK (difficulty IN ('easy', 'medium', 'hard')),
    active                  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_training_scenarios_org      ON training_scenarios (organization_id);
CREATE INDEX IF NOT EXISTS idx_training_scenarios_category ON training_scenarios (category_id);

CREATE TABLE IF NOT EXISTS training_attempts (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id                 UUID NOT NULL REFERENCES training_scenarios(id) ON DELETE CASCADE,
    user_id                     UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    organization_id             UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    submitted_decision_json     JSONB NOT NULL DEFAULT '{}',
    score                       NUMERIC(5, 2),
    feedback_json               JSONB DEFAULT '{}',
    completed_at                TIMESTAMPTZ,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_training_attempts_scenario ON training_attempts (scenario_id);
CREATE INDEX IF NOT EXISTS idx_training_attempts_user     ON training_attempts (user_id);
CREATE INDEX IF NOT EXISTS idx_training_attempts_org      ON training_attempts (organization_id);

-- =============================================================================
-- BENCHMARK COHORTS (anonymous cross-company benchmarking)
-- =============================================================================

CREATE TABLE IF NOT EXISTS benchmark_cohorts (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cohort_key              TEXT NOT NULL,
    industry                TEXT,
    organization_size       TEXT,
    category                TEXT,
    metric_name             TEXT NOT NULL,
    metric_value            NUMERIC(20, 6) NOT NULL,
    percentile_data_json    JSONB DEFAULT '{}',
    period_start            DATE,
    period_end              DATE,
    sample_size             INTEGER NOT NULL DEFAULT 0,
    synthetic               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_benchmark_cohorts_key      ON benchmark_cohorts (cohort_key);
CREATE INDEX IF NOT EXISTS idx_benchmark_cohorts_industry ON benchmark_cohorts (industry);

-- =============================================================================
-- VOICE SESSIONS (ElevenLabs)
-- =============================================================================

CREATE TABLE IF NOT EXISTS voice_sessions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id             UUID REFERENCES profiles(id) ON DELETE SET NULL,
    case_id             UUID REFERENCES exception_cases(id) ON DELETE SET NULL,
    external_session_id TEXT,
    agent_id            TEXT,
    status              TEXT NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active', 'completed', 'error')),
    consent_given       BOOLEAN NOT NULL DEFAULT FALSE,
    transcript_json     JSONB DEFAULT '[]',
    started_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at            TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_voice_sessions_org  ON voice_sessions (organization_id);
CREATE INDEX IF NOT EXISTS idx_voice_sessions_user ON voice_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_voice_sessions_case ON voice_sessions (case_id);

-- =============================================================================
-- FEATURE FLAGS
-- =============================================================================

CREATE TABLE IF NOT EXISTS feature_flags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    flag_key        TEXT NOT NULL,
    enabled         BOOLEAN NOT NULL DEFAULT FALSE,
    config_json     JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (organization_id, flag_key)
);

CREATE INDEX IF NOT EXISTS idx_feature_flags_org ON feature_flags (organization_id);
CREATE INDEX IF NOT EXISTS idx_feature_flags_key ON feature_flags (flag_key);

-- =============================================================================
-- TRIGGERS — updated_at
-- =============================================================================

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_exception_budgets_updated_at') THEN
        CREATE TRIGGER trg_exception_budgets_updated_at
            BEFORE UPDATE ON exception_budgets
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_repeated_clusters_updated_at') THEN
        CREATE TRIGGER trg_repeated_clusters_updated_at
            BEFORE UPDATE ON repeated_exception_clusters
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_feature_flags_updated_at') THEN
        CREATE TRIGGER trg_feature_flags_updated_at
            BEFORE UPDATE ON feature_flags
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- =============================================================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================================================

ALTER TABLE hindsight_operations         ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs                   ENABLE ROW LEVEL SECURITY;
ALTER TABLE llm_usage                    ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications                ENABLE ROW LEVEL SECURITY;
ALTER TABLE escalation_rules             ENABLE ROW LEVEL SECURITY;
ALTER TABLE escalations                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE sla_rules                    ENABLE ROW LEVEL SECURITY;
ALTER TABLE exception_budgets            ENABLE ROW LEVEL SECURITY;
ALTER TABLE budget_transactions          ENABLE ROW LEVEL SECURITY;
ALTER TABLE policy_drift_findings        ENABLE ROW LEVEL SECURITY;
ALTER TABLE repeated_exception_clusters  ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_contradictions        ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_scenarios           ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_attempts            ENABLE ROW LEVEL SECURITY;
ALTER TABLE benchmark_cohorts            ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_sessions               ENABLE ROW LEVEL SECURITY;
ALTER TABLE feature_flags                ENABLE ROW LEVEL SECURITY;

-- ── hindsight_operations ─────────────────────────────────────────────────────

CREATE POLICY "hindsight_ops_select_member"
    ON hindsight_operations FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

-- ── audit_logs (admin/owner only — sensitive) ────────────────────────────────

CREATE POLICY "audit_logs_select_admin"
    ON audit_logs FOR SELECT
    USING (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid()
              AND role IN ('owner', 'admin')
              AND status = 'active'
        )
    );

-- ── llm_usage ─────────────────────────────────────────────────────────────────

CREATE POLICY "llm_usage_select_member"
    ON llm_usage FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

-- ── notifications (own only) ─────────────────────────────────────────────────

CREATE POLICY "notifications_select_own"
    ON notifications FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "notifications_update_own"
    ON notifications FOR UPDATE
    USING (user_id = auth.uid());

-- ── escalation_rules ──────────────────────────────────────────────────────────

CREATE POLICY "escalation_rules_select_member"
    ON escalation_rules FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

CREATE POLICY "escalation_rules_write_admin"
    ON escalation_rules FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid()
              AND role IN ('owner', 'admin')
              AND status = 'active'
        )
    );

-- ── escalations ───────────────────────────────────────────────────────────────

CREATE POLICY "escalations_select_member"
    ON escalations FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

-- ── sla_rules ─────────────────────────────────────────────────────────────────

CREATE POLICY "sla_rules_select_member"
    ON sla_rules FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

CREATE POLICY "sla_rules_write_admin"
    ON sla_rules FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid()
              AND role IN ('owner', 'admin')
              AND status = 'active'
        )
    );

-- ── exception_budgets / budget_transactions ──────────────────────────────────

CREATE POLICY "exception_budgets_select_member"
    ON exception_budgets FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

CREATE POLICY "exception_budgets_write_admin"
    ON exception_budgets FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid()
              AND role IN ('owner', 'admin')
              AND status = 'active'
        )
    );

CREATE POLICY "budget_txns_select_member"
    ON budget_transactions FOR SELECT
    USING (
        budget_id IN (
            SELECT id FROM exception_budgets
            WHERE organization_id IN (SELECT auth_user_org_ids())
        )
    );

-- ── policy_drift_findings ─────────────────────────────────────────────────────

CREATE POLICY "policy_drift_select_member"
    ON policy_drift_findings FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

-- ── repeated_exception_clusters ───────────────────────────────────────────────

CREATE POLICY "repeated_clusters_select_member"
    ON repeated_exception_clusters FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

-- ── memory_contradictions ─────────────────────────────────────────────────────

CREATE POLICY "memory_contradictions_select_member"
    ON memory_contradictions FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

-- ── training_scenarios / training_attempts ───────────────────────────────────

CREATE POLICY "training_scenarios_select_member"
    ON training_scenarios FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

CREATE POLICY "training_attempts_select_member"
    ON training_attempts FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

CREATE POLICY "training_attempts_insert_own"
    ON training_attempts FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- ── benchmark_cohorts (anonymous, readable by any authenticated user) ────────

CREATE POLICY "benchmark_cohorts_select_authenticated"
    ON benchmark_cohorts FOR SELECT
    USING (auth.uid() IS NOT NULL);

-- ── voice_sessions ────────────────────────────────────────────────────────────

CREATE POLICY "voice_sessions_select_member"
    ON voice_sessions FOR SELECT
    USING (organization_id IN (SELECT auth_user_org_ids()));

-- ── feature_flags ─────────────────────────────────────────────────────────────

CREATE POLICY "feature_flags_select_member"
    ON feature_flags FOR SELECT
    USING (
        organization_id IS NULL
        OR organization_id IN (SELECT auth_user_org_ids())
    );

CREATE POLICY "feature_flags_write_admin"
    ON feature_flags FOR ALL
    USING (
        organization_id IN (
            SELECT organization_id FROM organization_memberships
            WHERE user_id = auth.uid()
              AND role IN ('owner', 'admin')
              AND status = 'active'
        )
    );

-- =============================================================================
-- SERVICE ROLE BYPASS (backend uses service role key — bypasses RLS)
-- =============================================================================


-- >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  004_synthetic_markers.sql  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
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


-- >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  005_openclaw_extensions.sql  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
-- =============================================================================
-- ExceptionOS — OpenClaw Integration Extensions Migration
-- Additive only. Per "OpenClaw Integration Guidelines":
--   - OpenClaw is an OPTIONAL bonus integration, disabled by default via
--     ENABLE_OPENCLAW=false.
--   - The only OpenClaw-specific table (openclaw_sessions) already exists in
--     001_initial.sql with the exact fields specified by the guidelines.
--   - This migration only adds:
--       1. exception_cases.source — lets the frontend show a small
--          "Created through OpenClaw" badge on cases that originated via the
--          optional OpenClaw conversational channel.
--       2. organizations.openclaw_enabled — an org-level override so a single
--          organisation can disable the (globally-enabled) OpenClaw
--          integration for itself via POST /integrations/openclaw/disable,
--          without requiring an env var change / redeploy.
-- Target: Supabase (PostgreSQL 15+)
-- =============================================================================

-- =============================================================================
-- exception_cases.source
-- =============================================================================

ALTER TABLE exception_cases
    ADD COLUMN IF NOT EXISTS source TEXT NOT NULL DEFAULT 'web'
        CHECK (source IN ('web', 'openclaw'));

CREATE INDEX IF NOT EXISTS idx_exc_cases_source ON exception_cases (organization_id, source);

-- =============================================================================
-- organizations.openclaw_enabled
-- Org-level override on top of the global ENABLE_OPENCLAW flag. When TRUE
-- (the default) the org follows the global flag; when FALSE the integration
-- is treated as disabled for that org regardless of the global flag.
-- =============================================================================

ALTER TABLE organizations
    ADD COLUMN IF NOT EXISTS openclaw_enabled BOOLEAN NOT NULL DEFAULT TRUE;


