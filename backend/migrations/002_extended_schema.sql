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
