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
