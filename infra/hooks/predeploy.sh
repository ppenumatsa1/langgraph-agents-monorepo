#!/usr/bin/env sh
set -e
set -x

echo "Predeploy hook: build and push researcher-agent image."

ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)

if command -v azd >/dev/null 2>&1; then
  echo "Loading azd environment values..."
  AZD_ENV_VALUES=$(AZD_DEBUG=0 azd env get-values 2>/dev/null | grep -E '^[A-Za-z_][A-Za-z0-9_]*=')
  if [ -n "$AZD_ENV_VALUES" ]; then
    AZD_ENV_FILE=$(mktemp)
    printf '%s\n' "$AZD_ENV_VALUES" > "$AZD_ENV_FILE"
    # shellcheck disable=SC1090
    . "$AZD_ENV_FILE" || true
    rm -f "$AZD_ENV_FILE"
  fi
fi

AZD_ENV_FILE="$ROOT_DIR/.azure/${AZURE_ENV_NAME}/.env"
if [ -f "$AZD_ENV_FILE" ]; then
  echo "Loading azd .env overrides..."
  set -a
  # shellcheck disable=SC1090
  . "$AZD_ENV_FILE"
  set +a
fi

AGENT_ENV_FILE="$ROOT_DIR/agents/researcher-agent/.env"

if [ -z "$AZURE_OPENAI_ENDPOINT" ] || [ -z "$AZURE_OPENAI_DEPLOYMENT_NAME" ]; then
  echo "Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_DEPLOYMENT_NAME in agent .env."
  exit 1
fi

if [ -n "$AZURE_RESOURCE_GROUP" ] && command -v az >/dev/null 2>&1; then
  CONTAINER_APP_NAME=$(az containerapp list -g "$AZURE_RESOURCE_GROUP" --query "[0].name" -o tsv || true)
  if [ -n "$CONTAINER_APP_NAME" ]; then
    echo "Updating container app env vars for $CONTAINER_APP_NAME"
    az containerapp update -g "$AZURE_RESOURCE_GROUP" -n "$CONTAINER_APP_NAME" \
      --set-env-vars \
        AZURE_OPENAI_ENDPOINT="$AZURE_OPENAI_ENDPOINT" \
        AZURE_OPENAI_DEPLOYMENT_NAME="$AZURE_OPENAI_DEPLOYMENT_NAME" \
        AZURE_OPENAI_MODEL_NAME="$AZURE_OPENAI_MODEL_NAME" \
        AZURE_OPENAI_API_VERSION="${AZURE_OPENAI_API_VERSION:-2024-12-01-preview}"
  fi
fi

if [ -z "$acrLoginServer" ]; then
  echo "acrLoginServer not set; cannot build/push image."
  exit 1
fi

IMAGE_TAG="${acrLoginServer}/researcher-agent:latest"

echo "Logging into ACR: ${acrLoginServer%%.*}"
az acr login --name "${acrLoginServer%%.*}"

echo "Building image: $IMAGE_TAG"
docker build -t "$IMAGE_TAG" "$ROOT_DIR/agents/researcher-agent"

echo "Pushing image: $IMAGE_TAG"
docker push "$IMAGE_TAG"

echo "Setting azd env overrides for image and port"

azd env set containerImage "$IMAGE_TAG"
azd env set containerTargetPort "8000"

echo "Built and pushed $IMAGE_TAG"
