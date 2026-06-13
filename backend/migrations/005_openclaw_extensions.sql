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
