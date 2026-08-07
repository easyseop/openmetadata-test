#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
source "$SCRIPT_DIR/common.sh"

require_docker
prepare_directories
download_base_compose

echo "[1/3] Contract runner image를 받습니다."
compose --profile contracts pull runtime-contract-runner

repo_digest="$(docker image inspect "$OM_SERVER_IMAGE" --format '{{index .RepoDigests 0}}')"
DEPLOYED_ARTIFACT_DIGEST="${repo_digest##*@}"
if [ -z "$DEPLOYED_ARTIFACT_DIGEST" ] || [ "$DEPLOYED_ARTIFACT_DIGEST" = "$repo_digest" ]; then
  echo "[중단] 실행 image의 원격 digest를 확인할 수 없습니다." >&2
  exit 4
fi
export DEPLOYED_ARTIFACT_DIGEST

RUNTIME_RUN_ID="${RUNTIME_RUN_ID:-om-1.13.1-portable-runtime-$(date +%Y%m%d-%H%M%S)}"
export RUNTIME_RUN_ID

echo "[2/3] 실행 image와 1.13.1 candidate를 고정합니다."
echo "- candidate: 8ac18ad053d9274774e274ba17b35911ac0b9dcb"
echo "- image digest: $DEPLOYED_ARTIFACT_DIGEST"

echo "[3/3] Runtime Contract 9개를 실행합니다."
compose --profile contracts run --rm runtime-contract-runner

echo "[완료] Contract 증거: $OM_REHEARSAL_OUTPUT_DIR/$RUNTIME_RUN_ID"

