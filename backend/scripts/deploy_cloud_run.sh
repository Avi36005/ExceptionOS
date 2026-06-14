#!/usr/bin/env bash
# Deploy the ExceptionOS FastAPI backend to Google Cloud Run.
#
# Usage:
#   ./scripts/deploy_cloud_run.sh /path/to/env.yaml
#
# The env.yaml is a Cloud Run --env-vars-file (KEY: 'value' per line) built
# from backend/.env. It is NOT committed (contains secrets). Generate it with:
#
#   python - <<'PY'
#   for line in open('.env',encoding='utf-8'):
#       line=line.rstrip('\n')
#       if not line.strip() or line.lstrip().startswith('#') or '=' not in line: continue
#       k,v=line.split('=',1); print(f"{k.strip()}: '{v.strip().strip(chr(34)).strip(chr(39))}'")
#   PY > env.yaml
#
set -euo pipefail

ENV_FILE="${1:?Usage: deploy_cloud_run.sh <env-vars-file.yaml>}"
PROJECT="${GCP_PROJECT:-mediflow-nexus-2026}"
REGION="${GCP_REGION:-asia-south1}"
SERVICE="${SERVICE_NAME:-exceptionos-backend}"

cd "$(dirname "$0")/.."

gcloud run deploy "$SERVICE" \
  --source . \
  --region "$REGION" \
  --project "$PROJECT" \
  --port 8000 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --env-vars-file "$ENV_FILE"

echo "Deployed. Service URL:"
gcloud run services describe "$SERVICE" --region "$REGION" --project "$PROJECT" \
  --format="value(status.url)"
