#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
source "$SCRIPT_DIR/common.sh"

require_docker
prepare_directories
download_base_compose

compose down

echo "[완료] 컨테이너는 중지·삭제했습니다. MySQL·Elasticsearch 데이터는 보존됩니다."
echo "[참고] 데이터까지 삭제하려면 사용자가 직접 'docker compose down --volumes'를 결정해야 합니다."

