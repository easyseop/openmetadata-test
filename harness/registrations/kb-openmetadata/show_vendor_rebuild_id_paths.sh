#!/usr/bin/env bash

# Show one BANK-OM ID's unique and shared path examples from saved evidence.
# Compatible with macOS Bash 3.2.

set -u

CUSTOMIZATION_ID="${1:-}"
if ! printf '%s\n' "$CUSTOMIZATION_ID" | grep -Eq '^BANK-OM-[0-9][0-9][0-9]$'; then
  echo "[입력 오류] 확인할 ID를 BANK-OM-001 형식으로 입력합니다."
  echo "예: bash harness/registrations/kb-openmetadata/show_vendor_rebuild_id_paths.sh BANK-OM-001"
  exit 3
fi

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TEST_REPO=$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)
if [ -z "$TEST_REPO" ]; then
  echo "[입력 오류] 검사기 저장소의 최상위 폴더를 찾지 못했습니다."
  exit 3
fi

cd "$TEST_REPO" || exit 3

RESULT_FILE="evidence/om-1.13.1-id-series/vendor-rebuild-result.json"
if [ ! -s "$RESULT_FILE" ]; then
  echo "[결과 없음] 먼저 7-4-1 재구성 검사를 실행합니다."
  echo "bash harness/registrations/kb-openmetadata/run_vendor_rebuild_check.sh"
  exit 3
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "[입력 오류] 결과를 읽는 jq 명령을 찾을 수 없습니다."
  exit 3
fi

if ! jq -e --arg id "$CUSTOMIZATION_ID" \
  '.plan.active_ids | index($id) != null' \
  "$RESULT_FILE" >/dev/null; then
  echo "[ID 없음] 검사 결과에서 $CUSTOMIZATION_ID를 찾지 못했습니다."
  exit 1
fi

echo "[확인 ID] $CUSTOMIZATION_ID"
echo "[결과 파일] $TEST_REPO/$RESULT_FILE"

jq --arg id "$CUSTOMIZATION_ID" '
  ([.plan.unique_assignments[]
    | select(.customization_id == $id)]) as $unique
  | ([.plan.shared_candidates[]
      | select(.candidate_ids | index($id))]) as $shared
  | {
      customization_id: $id,
      unique_path_count: ($unique | length),
      shared_path_count: ($shared | length),
      unique_path_examples: $unique[0:3],
      shared_path_examples: $shared[0:2]
    }
' "$RESULT_FILE"

echo "[확인 방법] count는 전체 개수이고 examples는 화면 확인용 일부 경로입니다."
