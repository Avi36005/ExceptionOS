# Pre-existing GCP Resource Inventory

Captured before any ExceptionOS provisioning, per architecture spec safety constraints.

- **Project**: `mediflow-nexus-2026`
- **Project number**: `3692981377` (verified, matches spec)
- **Account**: `avinashgehi3@gmail.com`
- **Default region**: `asia-south1`

## Cloud Run services

| Name | Region | URL |
|---|---|---|
| bfai-hardik-backend | asia-south1 | https://bfai-hardik-backend-m477e5mida-el.a.run.app |
| dealradar-backend | asia-south1 | https://dealradar-backend-m477e5mida-el.a.run.app |
| dealradar-frontend | asia-south1 | https://dealradar-frontend-m477e5mida-el.a.run.app |
| fundflow-backend | asia-south1 | https://fundflow-backend-m477e5mida-el.a.run.app |
| qrshield | asia-south1 | https://qrshield-m477e5mida-el.a.run.app |
| qrshield-api | asia-south1 | https://qrshield-api-m477e5mida-el.a.run.app |
| qrshield-web | asia-south1 | https://qrshield-web-m477e5mida-el.a.run.app |
| trustqr | asia-south1 / us-central1 | https://trustqr-m477e5mida-el.a.run.app / https://trustqr-m477e5mida-uc.a.run.app |
| trustqr-api | asia-south1 / us-central1 | https://trustqr-api-m477e5mida-el.a.run.app / https://trustqr-api-m477e5mida-uc.a.run.app |
| trustqr-web | asia-south1 / us-central1 | https://trustqr-web-m477e5mida-el.a.run.app / https://trustqr-web-m477e5mida-uc.a.run.app |
| zeroone | asia-south1 | https://zeroone-m477e5mida-el.a.run.app |
| zeroonone | asia-south1 | https://zeroonone-m477e5mida-el.a.run.app |
| creatrix-ai-backend | us-central1 | https://creatrix-ai-backend-m477e5mida-uc.a.run.app |
| creatrix-iq | us-central1 | https://creatrix-iq-m477e5mida-uc.a.run.app |
| creatrix-studio | us-central1 | https://creatrix-studio-m477e5mida-uc.a.run.app |
| mediflow-nexus-frontend | us-central1 | https://mediflow-nexus-frontend-m477e5mida-uc.a.run.app |
| ssrmediflownexus2026 | us-central1 | https://ssrmediflownexus2026-m477e5mida-uc.a.run.app |

## Firebase Hosting sites

- bfai-hardik
- creatrix-iq
- creatrix-studio
- creatrixai
- documentiq-app
- docvault-ai-app
- fundflow-app-2026
- mediflow-nexus-2026
- zeroone-in
- zeroonone

> `exceptionos-nexus-2026` does **not** exist yet — needs to be created.

## Secret Manager secrets (names only)

- ALLOWED_ORIGINS
- ANAKIN_API_KEY
- BFAI_ALLOWED_ORIGINS
- BFAI_ELEVENLABS_API_KEY
- BFAI_GROQ_API_KEY
- BFAI_OPENAI_API_KEY
- CORS_ORIGINS
- ELEVENLABS_API_KEY
- ELEVENLABS_VOICE_ID
- GEMINI_API_KEY
- GROQ_API_KEY
- OPENAI_API_KEY
- REDIS_URL
- documentiq-api-secret-key
- documentiq-elevenlabs-api-key
- documentiq-gemini-api-key
- documentiq-groq-api-key
- documentiq-openai-api-key

> No `EXCEPTIONOS_*`-prefixed secrets exist yet.

## Service Accounts

- fundflow-sa@mediflow-nexus-2026.iam.gserviceaccount.com
- mediflow-nexus-2026@appspot.gserviceaccount.com (App Engine default)
- firebase-adminsdk-fbsvc@mediflow-nexus-2026.iam.gserviceaccount.com
- 3692981377-compute@developer.gserviceaccount.com (Default compute)

> No `exceptionos-*` service accounts exist yet.

## Artifact Registry repositories

- bfai-hardik (Docker)
- cloud-run-source-deploy (Docker) — appears twice (multi-region)
- zeroone (Docker)
- gcr.io (Docker)
- gcf-artifacts (Docker)

> No `exceptionos-containers` repository exists yet.

## Cloud Tasks queues

- Cloud Tasks API (`cloudtasks.googleapis.com`) is **not enabled** on this project.
- No queues exist.

## Pub/Sub topics

- None found (`pubsub.googleapis.com` is enabled, but no topics exist).

## Enabled APIs (relevant)

Already enabled: `run.googleapis.com`, `artifactregistry.googleapis.com`, `secretmanager.googleapis.com`,
`iam.googleapis.com`, `cloudbuild.googleapis.com`, `firebase.googleapis.com`, `firebasehosting.googleapis.com`,
`pubsub.googleapis.com`, `generativelanguage.googleapis.com` (Gemini), `cloudresourcemanager.googleapis.com`,
`secretmanager.googleapis.com`, `logging.googleapis.com`, `monitoring.googleapis.com`, `cloudtrace.googleapis.com`.

**Not enabled** (needed if Cloud Tasks-based jobs are used): `cloudtasks.googleapis.com`.

## Safety conclusion

Project number matches expected `3692981377` — deployment may proceed. All new resources must use the
`exceptionos-` prefix (Cloud Run services, service accounts, Artifact Registry repo, Cloud Tasks queue,
Pub/Sub topic) and Firebase site `exceptionos-nexus-2026`. No existing resource listed above may be
modified, updated, or deleted.
