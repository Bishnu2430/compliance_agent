#!/usr/bin/env bash
# deploy/cloud_run_deploy.sh
set -euo pipefail

PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project)}
REGION=${REGION:-us-central1}
SERVICE_NAME=${SERVICE_NAME:-compliance-agent}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

# build and push image
docker build -t "${IMAGE_NAME}" -f deploy/Dockerfile .
docker push "${IMAGE_NAME}"

# deploy to Cloud Run
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_NAME}" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --set-env-vars GEMINI_API_KEY="${GEMINI_API_KEY}",GITHUB_TOKEN="${GITHUB_TOKEN}"
