# ExceptionOS Deployment Readiness Runbook

This runbook is for a controlled GCP/Firebase deployment of ExceptionOS only. It is not a record of a completed deployment.

## Scope and Safety Rules

- GCP project: `mediflow-nexus-2026`
- Expected project number: `3692981377`
- Primary region: `asia-south1`
- Firebase Hosting site: `exceptionos-nexus-2026`
- Firebase Hosting target alias: `exceptionos`
- Cloud Run services: `exceptionos-api` and `exceptionos-worker`
- Existing resource inventory: [preexisting-resources.md](./preexisting-resources.md)

Only create or update resources with an `exceptionos-` prefix, except Firebase Hosting target alias `exceptionos`. Do not modify, delete, rename, grant broad access to, or redeploy any preexisting resource listed in the inventory.

Do not run deployment commands until every readiness item below is checked. The commands in this document are intentionally written for an operator to copy after review; they were not run while preparing this document.

## Abort Conditions

Abort immediately if any condition is true:

- `gcloud projects describe mediflow-nexus-2026` returns a project number other than `3692981377`.
- The active account is not the intended deployment account for this project.
- `docs/deployment/preexisting-resources.md` is missing, stale, or materially differs from current read-only inventory results.
- Any planned resource name lacks the `exceptionos-` prefix, except the Firebase target alias `exceptionos`.
- Any command would update or delete one of the listed preexisting Cloud Run services, Firebase sites, secrets, service accounts, Artifact Registry repos, Cloud Tasks queues, or Pub/Sub topics.
- `exceptionos-api`, `exceptionos-worker`, `exceptionos-containers`, `exceptionos-nexus-2026`, or another `exceptionos-*` resource already exists and cannot be proven to belong to this ExceptionOS deployment.
- Required backend secrets are missing or empty.
- The frontend build points at localhost, a placeholder Supabase URL, or an API URL outside the intended `exceptionos-api` service.
- Firebase config is absent or does not map hosting target `exceptionos` to site `exceptionos-nexus-2026`.
- Cloud Run health verification returns anything other than an expected healthy/degraded response for the just-deployed `exceptionos-api` revision.
- A command prompt or review output mentions a non-ExceptionOS resource change.

## Readiness Checklist

- [ ] Confirm the operator is in the repository root.
- [ ] Confirm there are no unreviewed deployment config changes.
- [ ] Confirm the active GCP account and Firebase account are the intended operator.
- [ ] Confirm project ID `mediflow-nexus-2026` and project number `3692981377`.
- [ ] Re-run read-only inventory commands and compare with [preexisting-resources.md](./preexisting-resources.md).
- [ ] Confirm no non-ExceptionOS resource will be changed.
- [ ] Confirm all required environment variables and secrets are available.
- [ ] Build backend and frontend locally before any cloud deploy.
- [ ] Create only missing `exceptionos-*` infrastructure.
- [ ] Deploy `exceptionos-api` first and verify `/api/v1/health`.
- [ ] Deploy `exceptionos-worker` only if a worker entrypoint has been reviewed.
- [ ] Deploy Firebase Hosting only through target `exceptionos`.
- [ ] Record final URLs, revisions, image digests, and verification output in a deployment note.

## Local and Account Preflight

Run from the repository root. These commands are read-only.

```powershell
Get-Location
git status --short
gcloud auth list --filter=status:ACTIVE --format="value(account)"
gcloud config get-value project
gcloud config get-value run/region
firebase login:list
```

Expected:

- Repository path is the ExceptionOS repo.
- Any uncommitted changes are reviewed and intentionally unrelated or deployment-scoped.
- Active GCP project is `mediflow-nexus-2026`, or every command below passes `--project=mediflow-nexus-2026`.
- Active region is `asia-south1`, or every regional command below passes `--region=asia-south1`.

## Project Identity Verification

Read-only commands:

```powershell
gcloud projects describe mediflow-nexus-2026 --format="value(projectNumber)"
gcloud projects describe mediflow-nexus-2026 --format="yaml(projectId,projectNumber,lifecycleState,name)"
```

Expected:

- Project number output is exactly `3692981377`.
- Lifecycle state is active.

Abort on any mismatch.

## Current Resource Inventory

Read-only commands:

```powershell
gcloud run services list --project=mediflow-nexus-2026 --platform=managed --format="table(metadata.name,metadata.namespace,status.url)" --regions=asia-south1,us-central1
firebase hosting:sites:list --project mediflow-nexus-2026
gcloud secrets list --project=mediflow-nexus-2026 --format="value(name)"
gcloud iam service-accounts list --project=mediflow-nexus-2026 --format="value(email)"
gcloud artifacts repositories list --project=mediflow-nexus-2026 --location=asia-south1
gcloud services list --project=mediflow-nexus-2026 --enabled --format="value(config.name)"
```

Optional checks for APIs that may not be enabled yet:

```powershell
gcloud pubsub topics list --project=mediflow-nexus-2026
gcloud tasks queues list --project=mediflow-nexus-2026 --location=asia-south1
```

Expected:

- Existing resources match [preexisting-resources.md](./preexisting-resources.md).
- No existing non-ExceptionOS resource is selected for change.
- `cloudtasks.googleapis.com` may be disabled; enable it only if the worker uses Cloud Tasks.

## Required Environment Contract

Backend runtime variables from `backend/app/config.py` and `backend/.env.example`:

| Variable | Required | Source | Notes |
|---|---:|---|---|
| `SUPABASE_URL` | Yes | Secret Manager | Must be production Supabase URL. |
| `SUPABASE_ANON_KEY` | Yes | Secret Manager | Used by backend where needed. |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Secret Manager | Backend-only. Never expose to frontend. |
| `SUPABASE_JWT_SECRET` | Yes | Secret Manager | Required for JWT middleware. |
| `GROQ_API_KEY` or `GROQ_API_KEY_PRIMARY` | Yes | Secret Manager | Primary LLM provider. |
| `GROQ_API_KEY_2` or `GROQ_API_KEY_SECONDARY` | Optional | Secret Manager | Secondary Groq key. |
| `GEMINI_API_KEY` | Optional | Secret Manager | Fallback provider. |
| `OPENAI_API_KEY` | Optional | Secret Manager | Final fallback provider. |
| `HINDSIGHT_API_KEY` | Yes | Secret Manager | Mandatory memory layer. |
| `HINDSIGHT_BASE_URL` | Yes | Plain env | Default `https://api.hindsight.vectorize.io`. |
| `ELEVENLABS_API_KEY` | Optional | Secret Manager | Voice routes only. |
| `ELEVENLABS_VOICE_ID` | Optional | Plain env | Defaults in code. |
| `ENABLE_OPENCLAW` | Yes | Plain env | Use `false` unless intentionally enabled. |
| `OPENCLAW_WEBHOOK_SECRET` | Conditional | Secret Manager | Required only when OpenClaw is enabled. |
| `DEMO_MODE` | Yes | Plain env | Use `false` for production. |
| `APP_ENV` | Yes | Plain env | Use `production`. |
| `GCP_REGION` | Yes | Plain env | Use `asia-south1`. |
| `CORS_ORIGINS` | Yes | Plain env | Restrict to Firebase app domains and localhost only when needed. |

Frontend build variables from `frontend/.env.example`:

| Variable | Required | Expected production value |
|---|---:|---|
| `VITE_SUPABASE_URL` | Yes | Production Supabase URL. |
| `VITE_SUPABASE_ANON_KEY` | Yes | Production Supabase anon key only. |
| `VITE_EXCEPTIONOS_API_URL` | Yes | The deployed `exceptionos-api` HTTPS URL. |
| `VITE_EXCEPTIONOS_WS_URL` | Optional | Matching `wss://` URL if websocket routes are enabled. |
| `VITE_APP_ENV` | Yes | `production`. |
| `VITE_DEMO_MODE_ENABLED` | Yes | `false` unless a labelled demo build is intended. |

## Secret Creation Checklist

Use `EXCEPTIONOS_`-prefixed Secret Manager names. Do not reuse generic preexisting secrets like `GROQ_API_KEY`, `OPENAI_API_KEY`, or `REDIS_URL`.

Create only secrets that do not already exist:

```powershell
gcloud secrets create EXCEPTIONOS_SUPABASE_URL --replication-policy=automatic --project=mediflow-nexus-2026
gcloud secrets create EXCEPTIONOS_SUPABASE_ANON_KEY --replication-policy=automatic --project=mediflow-nexus-2026
gcloud secrets create EXCEPTIONOS_SUPABASE_SERVICE_ROLE_KEY --replication-policy=automatic --project=mediflow-nexus-2026
gcloud secrets create EXCEPTIONOS_SUPABASE_JWT_SECRET --replication-policy=automatic --project=mediflow-nexus-2026
gcloud secrets create EXCEPTIONOS_GROQ_API_KEY --replication-policy=automatic --project=mediflow-nexus-2026
gcloud secrets create EXCEPTIONOS_HINDSIGHT_API_KEY --replication-policy=automatic --project=mediflow-nexus-2026
```

Add secret versions from a secure local prompt or approved secret file. Do not commit secret files.

```powershell
gcloud secrets versions add EXCEPTIONOS_SUPABASE_URL --data-file=- --project=mediflow-nexus-2026
gcloud secrets versions add EXCEPTIONOS_SUPABASE_ANON_KEY --data-file=- --project=mediflow-nexus-2026
gcloud secrets versions add EXCEPTIONOS_SUPABASE_SERVICE_ROLE_KEY --data-file=- --project=mediflow-nexus-2026
gcloud secrets versions add EXCEPTIONOS_SUPABASE_JWT_SECRET --data-file=- --project=mediflow-nexus-2026
gcloud secrets versions add EXCEPTIONOS_GROQ_API_KEY --data-file=- --project=mediflow-nexus-2026
gcloud secrets versions add EXCEPTIONOS_HINDSIGHT_API_KEY --data-file=- --project=mediflow-nexus-2026
```

Optional provider secrets:

```powershell
gcloud secrets create EXCEPTIONOS_GROQ_API_KEY_2 --replication-policy=automatic --project=mediflow-nexus-2026
gcloud secrets create EXCEPTIONOS_GEMINI_API_KEY --replication-policy=automatic --project=mediflow-nexus-2026
gcloud secrets create EXCEPTIONOS_OPENAI_API_KEY --replication-policy=automatic --project=mediflow-nexus-2026
gcloud secrets create EXCEPTIONOS_ELEVENLABS_API_KEY --replication-policy=automatic --project=mediflow-nexus-2026
gcloud secrets create EXCEPTIONOS_OPENCLAW_WEBHOOK_SECRET --replication-policy=automatic --project=mediflow-nexus-2026
```

## Service Account

Create only if missing:

```powershell
gcloud iam service-accounts describe exceptionos-runner@mediflow-nexus-2026.iam.gserviceaccount.com --project=mediflow-nexus-2026
gcloud iam service-accounts create exceptionos-runner --display-name="ExceptionOS Cloud Run runtime" --project=mediflow-nexus-2026
```

Grant access only to `EXCEPTIONOS_*` secrets used by Cloud Run. Repeat for each required secret:

```powershell
gcloud secrets add-iam-policy-binding EXCEPTIONOS_SUPABASE_URL `
  --member="serviceAccount:exceptionos-runner@mediflow-nexus-2026.iam.gserviceaccount.com" `
  --role="roles/secretmanager.secretAccessor" `
  --project=mediflow-nexus-2026
```

Abort if a command would grant this service account project-wide access, owner/editor roles, or access to generic preexisting secrets.

## Build Readiness

Local commands:

```powershell
Set-Location backend
python -m pip install -r requirements.txt
python -m pytest
Set-Location ..\frontend
npm install
npm run build
Set-Location ..
```

Expected:

- Backend tests pass.
- Frontend TypeScript and Vite build pass.
- No `.env`, `.env.local`, service account key, or secret file is created in git-tracked content.

## Artifact Registry

Create only if missing:

```powershell
gcloud artifacts repositories describe exceptionos-containers --location=asia-south1 --project=mediflow-nexus-2026
gcloud artifacts repositories create exceptionos-containers --repository-format=docker --location=asia-south1 --description="ExceptionOS container images" --project=mediflow-nexus-2026
```

Build a reviewed image tag:

```powershell
$IMAGE_TAG = "asia-south1-docker.pkg.dev/mediflow-nexus-2026/exceptionos-containers/exceptionos-api:YYYYMMDD-HHMM"
gcloud builds submit backend --tag $IMAGE_TAG --project=mediflow-nexus-2026
gcloud artifacts docker images describe $IMAGE_TAG --project=mediflow-nexus-2026
```

Record the image digest before deploy.

## Cloud Run API Service

Deploy only service `exceptionos-api`.

```powershell
gcloud run deploy exceptionos-api `
  --image $IMAGE_TAG `
  --project=mediflow-nexus-2026 `
  --region=asia-south1 `
  --platform=managed `
  --allow-unauthenticated `
  --service-account=exceptionos-runner@mediflow-nexus-2026.iam.gserviceaccount.com `
  --set-env-vars='^|^APP_ENV=production|GCP_REGION=asia-south1|HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io|ENABLE_OPENCLAW=false|DEMO_MODE=false|CORS_ORIGINS=["https://exceptionos-nexus-2026.web.app","https://exceptionos-nexus-2026.firebaseapp.com"]' `
  --set-secrets=SUPABASE_URL=EXCEPTIONOS_SUPABASE_URL:latest,SUPABASE_ANON_KEY=EXCEPTIONOS_SUPABASE_ANON_KEY:latest,SUPABASE_SERVICE_ROLE_KEY=EXCEPTIONOS_SUPABASE_SERVICE_ROLE_KEY:latest,SUPABASE_JWT_SECRET=EXCEPTIONOS_SUPABASE_JWT_SECRET:latest,GROQ_API_KEY=EXCEPTIONOS_GROQ_API_KEY:latest,HINDSIGHT_API_KEY=EXCEPTIONOS_HINDSIGHT_API_KEY:latest
```

Notes:

- `--allow-unauthenticated` is required only because browser clients call the API directly; application JWT middleware still protects non-public routes.
- If a private API is required instead, abort and design the authenticated ingress path before deploying.
- Create service account `exceptionos-runner` only if missing, and grant only the minimum Secret Manager access required for `EXCEPTIONOS_*` secrets.

## Cloud Run Worker Service

Deploy only service `exceptionos-worker`.

The current repository has a backend API image but no separately verified worker entrypoint documented in deployment config. Do not deploy a worker until the exact command, queue source, and runtime behavior are reviewed.

When a worker entrypoint exists, it must use an `exceptionos-*` queue or topic only. Example pattern:

```powershell
gcloud run deploy exceptionos-worker `
  --image $IMAGE_TAG `
  --project=mediflow-nexus-2026 `
  --region=asia-south1 `
  --platform=managed `
  --no-allow-unauthenticated `
  --service-account=exceptionos-runner@mediflow-nexus-2026.iam.gserviceaccount.com `
  --set-env-vars=APP_ENV=production,GCP_REGION=asia-south1,DEMO_MODE=false `
  --set-secrets=SUPABASE_URL=EXCEPTIONOS_SUPABASE_URL:latest,SUPABASE_SERVICE_ROLE_KEY=EXCEPTIONOS_SUPABASE_SERVICE_ROLE_KEY:latest,HINDSIGHT_API_KEY=EXCEPTIONOS_HINDSIGHT_API_KEY:latest
```

Abort if the worker would consume from or publish to non-ExceptionOS queues, topics, buckets, services, or databases.

## Firebase Hosting

No root `firebase.json` or `.firebaserc` was present when this runbook was written. Do not run Firebase deploy until those config files exist in a reviewed deployment-prep change.

Required target:

- Site: `exceptionos-nexus-2026`
- Target alias: `exceptionos`

Safe setup commands:

```powershell
firebase projects:list
firebase hosting:sites:list --project mediflow-nexus-2026
firebase hosting:sites:create exceptionos-nexus-2026 --project mediflow-nexus-2026
firebase target:apply hosting exceptionos exceptionos-nexus-2026 --project mediflow-nexus-2026
```

Deploy only after `firebase.json` contains a hosting entry for target `exceptionos` and public directory `frontend/dist`:

```powershell
Set-Location frontend
npm run build
Set-Location ..
firebase deploy --only hosting:exceptionos --project mediflow-nexus-2026
```

Abort if Firebase CLI proposes any target or site other than `exceptionos` / `exceptionos-nexus-2026`.

## Verification

API verification:

```powershell
$API_URL = gcloud run services describe exceptionos-api --project=mediflow-nexus-2026 --region=asia-south1 --format="value(status.url)"
Invoke-RestMethod "$API_URL/api/v1/health"
Invoke-RestMethod "$API_URL/"
```

Expected `/api/v1/health`:

- `status` is `ok` when Supabase is reachable.
- `environment` is `production`.
- `services.hindsight.status` is `configured`.
- `services.groq.status` is `configured`.
- `services.openclaw.status` is `disabled` unless intentionally enabled.

Firebase verification:

```powershell
Invoke-WebRequest "https://exceptionos-nexus-2026.web.app" -UseBasicParsing
Invoke-WebRequest "https://exceptionos-nexus-2026.firebaseapp.com" -UseBasicParsing
```

Cloud Run service verification:

```powershell
gcloud run services describe exceptionos-api --project=mediflow-nexus-2026 --region=asia-south1 --format="yaml(metadata.name,status.url,status.latestReadyRevisionName,status.traffic)"
gcloud run revisions list --service=exceptionos-api --project=mediflow-nexus-2026 --region=asia-south1
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="exceptionos-api"' --project=mediflow-nexus-2026 --limit=50 --format="table(timestamp,severity,textPayload)"
```

Expected:

- Latest ready revision receives intended traffic.
- No logs show missing required environment variables.
- No logs show authentication or CORS failures for the Firebase origin.

## Rollback and Stop Rules

Rollback must only affect `exceptionos-*` resources.

Allowed rollback actions:

- Shift `exceptionos-api` traffic back to a previous known-good `exceptionos-api` revision.
- Disable traffic to a bad `exceptionos-worker` revision.
- Redeploy the previous Firebase Hosting release for site `exceptionos-nexus-2026`.

Not allowed:

- Deleting preexisting non-ExceptionOS resources.
- Reusing generic preexisting secrets.
- Changing IAM bindings for unrelated service accounts.
- Retagging or deleting images outside `exceptionos-containers`.

## Deployment Record Template

```text
Date:
Operator:
GCP project/project number:
Firebase project:
Git commit:
Backend image tag:
Backend image digest:
Cloud Run service URLs:
Firebase Hosting URL:
Secrets created or updated:
Verification commands run:
Verification result:
Known issues:
Rollback target:
```
