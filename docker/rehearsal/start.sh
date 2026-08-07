#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
source "$SCRIPT_DIR/common.sh"

require_docker
prepare_directories
download_base_compose

echo "[1/4] 고정된 Docker image를 받습니다."
compose pull mysql elasticsearch execute-migrate-all openmetadata-server

echo "[2/4] MySQL·Elasticsearch·OpenMetadata server를 시작합니다."
compose up --detach mysql elasticsearch execute-migrate-all openmetadata-server

echo "[3/4] OpenMetadata 화면이 응답할 때까지 기다립니다."
ready=0
for attempt in $(seq 1 120); do
  server_container="$(compose ps --quiet openmetadata-server)"
  server_health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$server_container" 2>/dev/null || true)"
  if [ "$server_health" = "healthy" ]; then
    ready=1
    break
  fi
  sleep 5
done
if [ "$ready" -ne 1 ]; then
  echo "[중단] 10분 안에 OpenMetadata가 정상 상태가 되지 않았습니다." >&2
  compose ps
  exit 3
fi

echo "[4/4] 5종 DB 목 메타데이터와 데이터 품질 결과를 등록합니다."
compose --profile fixtures run --rm mock-metadata-loader

echo "[완료] OpenMetadata: http://127.0.0.1:8585"
echo "[완료] 목 데이터 결과: $OM_REHEARSAL_OUTPUT_DIR/mock-database-metadata-result.json"
