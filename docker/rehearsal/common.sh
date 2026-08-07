#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
OM_TEST_REPO="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
OM_REHEARSAL_VAR_DIR="$OM_TEST_REPO/var/rehearsal"
OM_REHEARSAL_OUTPUT_DIR="$OM_REHEARSAL_VAR_DIR/evidence"
OM_BASE_COMPOSE="$OM_REHEARSAL_VAR_DIR/docker-compose-1.13.1.yml"
OM_OVERRIDE_COMPOSE="$SCRIPT_DIR/docker-compose.override.yml"
OM_PROJECT_NAME="om-bank-rehearsal-1131"
OM_SERVER_IMAGE="${OM_SERVER_IMAGE:-ghcr.io/easyseop/openmetadata-bank:1.13.1-bank-8ac18ad0}"
OM_CONTRACT_RUNNER_IMAGE="${OM_CONTRACT_RUNNER_IMAGE:-ghcr.io/easyseop/openmetadata-contract-runner:1.13.1-runtime}"

export OM_TEST_REPO
export OM_REHEARSAL_OUTPUT_DIR
export OM_SERVER_IMAGE
export OM_CONTRACT_RUNNER_IMAGE

compose() {
  docker compose \
    --project-name "$OM_PROJECT_NAME" \
    --file "$OM_BASE_COMPOSE" \
    --file "$OM_OVERRIDE_COMPOSE" \
    "$@"
}

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "[중단] Docker 명령을 찾을 수 없습니다. Docker Desktop을 먼저 설치합니다." >&2
    exit 2
  fi
  if ! docker compose version >/dev/null 2>&1; then
    echo "[중단] 'docker compose'를 사용할 수 없습니다. Docker Desktop을 실행합니다." >&2
    exit 2
  fi
}

prepare_directories() {
  mkdir -p "$OM_REHEARSAL_OUTPUT_DIR"
}

download_base_compose() {
  if [ -s "$OM_BASE_COMPOSE" ]; then
    return
  fi
  echo "[준비] 공식 OpenMetadata 1.13.1 Compose 파일을 받습니다."
  compose_url="https://raw.githubusercontent.com/open-metadata/OpenMetadata/afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9/docker/docker-compose-quickstart/docker-compose.yml"
  temporary_compose="$OM_BASE_COMPOSE.tmp"
  if command -v curl >/dev/null 2>&1; then
    curl --fail --silent --show-error --location \
      "$compose_url" \
      --output "$temporary_compose"
  else
    docker run --rm curlimages/curl:8.10.1 \
      --fail --silent --show-error --location "$compose_url" \
      > "$temporary_compose"
  fi
  mv "$temporary_compose" "$OM_BASE_COMPOSE"
}
