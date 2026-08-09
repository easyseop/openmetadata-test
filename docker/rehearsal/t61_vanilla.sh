#!/usr/bin/env bash
# T61 순정 negative control.
#
# 커스텀 스택과 같은 Contract suite 를 공식 순정 이미지에 돌려서,
# 각 필수 test 가 실제로 BANK 커스터마이징을 보고 있는지 확인한다.
# 순정에서 통과하는 test 는 그 기능의 생존을 입증하지 못한다.
#
# 기존 rehearsal 프로젝트(om-bank-rehearsal-1131)와 별도 project name 을 쓰므로
# Elasticsearch 볼륨은 자동으로 분리된다. 다만 MySQL 은 compose 가
# ./docker-volume/db-data 호스트 경로에 bind mount 하므로 project name 으로
# 분리되지 않는다. 반드시 아래 순서로 커스텀 DB 를 옆으로 옮긴 뒤 실행한다.
#
#   cd <repo>
#   bash docker/rehearsal/stop.sh
#   mv var/rehearsal/docker-volume/db-data var/rehearsal/docker-volume/db-data.custom
#   bash docker/rehearsal/t61_vanilla.sh
#   ...
#   mv var/rehearsal/docker-volume/db-data var/rehearsal/docker-volume/db-data.vanilla
#   mv var/rehearsal/docker-volume/db-data.custom var/rehearsal/docker-volume/db-data
#
# BANK 데이터가 남아 있는 DB 로 순정을 띄우면 마이그레이션이
# IllegalArgumentException: Sybase 로 exit 1 이 되고 서버가 기동하지 않는다.
# 이 스크립트는 그 상태를 감지하면 중단한다.
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
source "$SCRIPT_DIR/common.sh"

OM_SERVER_IMAGE="${OM_SERVER_IMAGE:-docker.getcollate.io/openmetadata/server:1.13.1}"
export OM_SERVER_IMAGE
OM_PROJECT_NAME="om-bank-t61-vanilla"

compose() {
  docker compose \
    --project-name "$OM_PROJECT_NAME" \
    --file "$OM_BASE_COMPOSE" \
    --file "$OM_OVERRIDE_COMPOSE" \
    "$@"
}

require_docker
prepare_directories
download_base_compose

RUNTIME_RUN_ID="${RUNTIME_RUN_ID:-om-1.13.1-t61-vanilla-$(date +%Y%m%d-%H%M%S)}"
export RUNTIME_RUN_ID

echo "[1/4] 순정 이미지를 받습니다: $OM_SERVER_IMAGE"
compose pull mysql elasticsearch openmetadata-server

echo "[2/4] 순정 스택을 시작합니다 (project: $OM_PROJECT_NAME)."
compose up --detach mysql elasticsearch execute-migrate-all openmetadata-server

echo "[3/4] 순정 서버가 healthy 가 될 때까지 기다립니다."
ready=0
for _ in $(seq 1 120); do
  server_container="$(compose ps --quiet openmetadata-server)"
  server_health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$server_container" 2>/dev/null || true)"
  if [ "$server_health" = "healthy" ]; then
    ready=1
    break
  fi
  migrate_container="$(compose ps -a --quiet execute-migrate-all)"
  migrate_state="$(docker inspect --format '{{.State.Status}}:{{.State.ExitCode}}' "$migrate_container" 2>/dev/null || true)"
  if [ "${migrate_state%%:*}" = "exited" ] && [ "${migrate_state##*:}" != "0" ]; then
    echo "[중단] 순정 마이그레이션이 실패했습니다: $migrate_state" >&2
    echo "       BANK 데이터가 남아 있는 DB 일 가능성이 높습니다." >&2
    echo "       docker logs execute_migrate_all | grep -i 'Caused by' 로 확인합니다." >&2
    exit 3
  fi
  sleep 5
done
if [ "$ready" -ne 1 ]; then
  echo "[중단] 10분 안에 순정 서버가 정상 상태가 되지 않았습니다." >&2
  compose ps -a
  exit 3
fi

repo_digest="$(docker image inspect "$OM_SERVER_IMAGE" --format '{{index .RepoDigests 0}}')"
DEPLOYED_ARTIFACT_DIGEST="${repo_digest##*@}"
if [ -z "$DEPLOYED_ARTIFACT_DIGEST" ] || [ "$DEPLOYED_ARTIFACT_DIGEST" = "$repo_digest" ]; then
  echo "[중단] 순정 image 의 원격 digest 를 확인할 수 없습니다." >&2
  exit 4
fi
export DEPLOYED_ARTIFACT_DIGEST

if [ "${OM_CONTRACT_RUNNER_PULL:-1}" = "1" ]; then
  compose --profile contracts pull runtime-contract-runner
elif ! docker image inspect "$OM_CONTRACT_RUNNER_IMAGE" >/dev/null 2>&1; then
  echo "[중단] 로컬에 image 가 없습니다: $OM_CONTRACT_RUNNER_IMAGE" >&2
  exit 2
fi

echo "[4/4] Contract 9개를 순정 스택에서 실행합니다."
echo "- server image  : $OM_SERVER_IMAGE"
echo "- server digest : $DEPLOYED_ARTIFACT_DIGEST"
echo "- candidate     : ${PRODUCT_COMMIT:-8ac18ad053d9274774e274ba17b35911ac0b9dcb} (테스트 suite 출처이며 서버가 아니다)"

set +e
compose --profile contracts run --rm runtime-contract-runner
rc=$?
set -e

echo
echo "[결과] runner exit=$rc  (기대: 0 이 아님. 0 이면 필수 test 가 전부 통과했다는 뜻이고,"
echo "       그 경우 해당 test 들은 커스터마이징 생존을 입증하지 못한다.)"
echo "[증거] $OM_REHEARSAL_OUTPUT_DIR/$RUNTIME_RUN_ID"
echo
echo "[정리] 끝나면 아래를 실행한다."
echo "  docker compose --project-name $OM_PROJECT_NAME \\"
echo "    --file $OM_BASE_COMPOSE --file $OM_OVERRIDE_COMPOSE down"
exit 0
