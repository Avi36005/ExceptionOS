# ExceptionOS Application Inventory

Generated for QA validation from the repository implementation on branch `feat/exceptionos-frontend`.

## Stack

- Frontend: React 18 + Vite + TypeScript, React Router, Tailwind, Zustand, Supabase JS.
- Backend: FastAPI + Pydantic v2 + Supabase Python client.
- Tests present: `pytest`, `pytest-asyncio`, frontend `tsc`, ESLint.
- Deployment config: Firebase Hosting target `exceptionos` mapped to `exceptionos-nexus-2026`; backend Dockerfile for FastAPI.
- CI workflows: none found in `.github/workflows`.

## Frontend Routes

Public/auth:
`/`, `/login`, `/signup`, `/forgot-password`, `/reset-password`, `/auth/callback`, `/accept-invite`, `/unauthorized`, `/service-unavailable`.

Onboarding:
`/select-organization`, `/onboarding/company`, `/onboarding/policies`, `/onboarding/team`, `/onboarding/hindsight`.

Demo:
`/demo`, `/demo/story`, `/demo/hindsight-live`, `/demo/before-after`.

Application shell:
`/app`, `/app/inbox`, `/app/my-requests`, `/app/my-approvals`.

Exceptions:
`/app/exceptions/new`, `/app/exceptions/:caseId`, `/app/exceptions/:caseId/intake`, `/evidence`, `/policy`, `/precedents`, `/debate`, `/recommendation`, `/decision`, `/outcome`, `/replay`, `/audit`, `/what-changed`, `/memory`.

Policies:
`/app/policies`, `/app/policies/new`, `/app/policies/drift`, `/app/policies/simulator`, `/app/policies/autopilot`, `/app/policies/:policyId`, `/edit`, `/versions`, `/exceptions`, `/drift`.

Precedents:
`/app/precedents`, `/app/precedents/graph`, `/app/precedents/compare`, `/app/precedents/contradictions`, `/app/precedents/ask`, `/app/precedents/:precedentId`.

Insights:
`/app/insights`, `/policy-drift`, `/repeated`, `/repeated-exceptions`, `/root-causes`, `/consistency`, `/outcomes`, `/success`, `/budgets`, `/benchmarks`, `/memory-health`, `/providers`, `/provider-usage`.

Training, voice, integrations, admin, settings:
`/app/training`, `/app/training/history`, `/app/training/team`, `/app/training/scenarios/:scenarioId`, `/app/training/:scenarioId`, `/app/voice`, `/app/voice/history`, `/app/voice/:sessionId`, `/app/integrations`, `/app/integrations/openclaw`, `/app/integrations/elevenlabs`, `/app/integrations/hindsight`, `/app/admin/organizations`, `/app/admin/users`, `/app/admin/roles`, `/app/admin/departments`, `/app/admin/escalation`, `/app/admin/sla`, `/app/admin/budgets`, `/app/admin/categories`, `/app/admin/system`, `/app/settings/profile`, `/app/settings/org`, `/app/settings/notifications`, `/app/settings/security`, `/app/settings/demo`.

## API Endpoints

OpenAPI generated successfully with 69 paths and 25 schemas.

Core endpoints:
`/api/v1/health`, `/api/v1/organizations`, `/api/v1/users`, `/api/v1/exceptions`, `/api/v1/decisions`, `/api/v1/outcomes`, `/api/v1/recommendations`, `/api/v1/policies`, `/api/v1/precedents`, `/api/v1/insights`, `/api/v1/training`, `/api/v1/voice`, `/api/v1/memory`, `/api/v1/debate`, `/api/v1/admin`, `/api/v1/integrations/openclaw`.

Streaming endpoints:
`GET /api/v1/exceptions/{case_id}/debate`, `GET /api/v1/debate/{case_id}/stream`.

Optional integration endpoints:
`GET /api/v1/integrations/openclaw/status`, `/sessions`, `/draft-cases`; `POST /disable`, `/webhook`.

## Database Tables

`agent_outputs`, `agent_runs`, `audit_logs`, `benchmark_cohorts`, `budget_transactions`, `case_events`, `case_evidence`, `case_facts`, `departments`, `escalation_rules`, `escalations`, `exception_budgets`, `exception_cases`, `exception_categories`, `feature_flags`, `hindsight_operations`, `human_decisions`, `llm_usage`, `memory_contradictions`, `notifications`, `openclaw_sessions`, `organization_memberships`, `organizations`, `outcomes`, `policies`, `policy_drift_findings`, `policy_versions`, `precedent_links`, `profiles`, `recommendations`, `repeated_exception_clusters`, `sla_rules`, `synthetic_data_registry`, `training_attempts`, `training_scenarios`, `voice_sessions`.

## Roles

Required product roles from the QA plan: `platform_super_admin`, `organization_admin`, `policy_admin`, `decision_manager`, `reviewer`, `requester`, `auditor`, `trainee`, `read_only`.

Current backend schema also contains membership roles from earlier implementation: `owner`, `admin`, `manager`, `analyst`, `viewer`. Full role-parity enforcement requires additional live auth/RLS tests.

## Feature Flags And Environment

Feature flags/config:
`ENABLE_OPENCLAW=false` by default, `ENABLE_MULTI_PROVIDER_DEBATE`, `DEMO_MODE`, `EXCEPTIONOS_SYNTHETIC_SEED`.

Public frontend env:
`VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_EXCEPTIONOS_API_URL`, `VITE_EXCEPTIONOS_WS_URL`, `VITE_APP_ENV`, `VITE_DEMO_MODE_ENABLED`.

Backend secrets/config:
Supabase URL/anon/service/JWT secret, Groq primary/secondary, Gemini, OpenAI, Hindsight, ElevenLabs, OpenClaw webhook secret, GCP region.

## External Providers

- Supabase Auth/PostgreSQL.
- Hindsight Cloud for retain/recall/reflect.
- Groq primary and secondary provider.
- Gemini fallback.
- OpenAI fallback.
- ElevenLabs voice.
- OpenClaw optional integration, disabled by default.

## Background Jobs

No standalone worker entrypoint or queue consumer was found. The FastAPI app uses background `asyncio.create_task` for analysis/outcome learning. Cloud Tasks queue is documented as optional but not enabled.

## Deployment Services

- Firebase Hosting site: `exceptionos-nexus-2026`.
- Cloud Run services: no `exceptionos-*` services found in `asia-south1` during QA preflight.
- Artifact Registry: no `exceptionos-containers` repo found in preflight.
