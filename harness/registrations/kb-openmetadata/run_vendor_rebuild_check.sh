#!/usr/bin/env bash

# Run the kb-openmetadata vendor reconstruction check and preserve its JSON.
# Compatible with macOS Bash 3.2.

set -u

if [ -z "${OM_CODE_REPO:-}" ]; then
  echo "[입력 오류] OM_CODE_REPO가 설정되지 않았습니다."
  echo "예: export OM_CODE_REPO=~/om-work/om-temp-real-1.13.1"
  exit 3
fi

if [ ! -d "$OM_CODE_REPO/.git" ]; then
  echo "[입력 오류] 제품 코드 저장소를 찾을 수 없습니다: $OM_CODE_REPO"
  exit 3
fi

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TEST_REPO=$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)
if [ -z "$TEST_REPO" ]; then
  echo "[입력 오류] 검사기 저장소의 최상위 폴더를 찾지 못했습니다."
  exit 3
fi

cd "$TEST_REPO" || exit 3

PYTHON_BIN="${VENDOR_REBUILD_PYTHON:-./.venv/bin/python}"
CANDIDATE_REF="${VENDOR_REBUILD_CANDIDATE:-codex/om-1.13.1-id-series}"
REGISTRATION_DIR="harness/registrations/kb-openmetadata"
OUTPUT_DIR="evidence/om-1.13.1-id-series"
OUTPUT_FILE="$OUTPUT_DIR/vendor-rebuild-result.json"

if [ ! -x "$PYTHON_BIN" ]; then
  echo "[입력 오류] Python 실행 파일을 찾을 수 없습니다: $PYTHON_BIN"
  exit 3
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "[입력 오류] 결과를 요약하는 jq 명령을 찾을 수 없습니다."
  exit 3
fi

mkdir -p "$OUTPUT_DIR" || exit 3

echo "[검사 대상] $CANDIDATE_REF"
echo "[결과 파일] $TEST_REPO/$OUTPUT_FILE"

PYTHONPATH=harness "$PYTHON_BIN" -m acgh.vendor_rebuild \
  --repo "$OM_CODE_REPO" \
  --registration "$REGISTRATION_DIR" \
  verify \
  --candidate "$CANDIDATE_REF" \
  --shared-owners "$REGISTRATION_DIR/shared-path-owners.yaml" \
  > "$OUTPUT_FILE"
VENDOR_REBUILD_EXIT=$?

if ! "$PYTHON_BIN" -m json.tool "$OUTPUT_FILE" >/dev/null 2>&1; then
  echo "[저장 오류] 결과 파일이 올바른 JSON이 아닙니다: $OUTPUT_FILE"
  exit 3
fi

echo "[검사 종료코드] $VENDOR_REBUILD_EXIT"

jq '{
  verdict: .gate.verdict,
  block_summary: .diagnosis.summary,
  primary_block_reason: .diagnosis.primary_category,
  block_details: .diagnosis.categories,
  active_ids: .plan.active_ids,
  excluded_paths: .plan.excluded_paths,
  plan_digest: .plan_digest
}' "$OUTPUT_FILE"

case "$VENDOR_REBUILD_EXIT" in
  0) echo "[다음 행동] 통과했습니다. 다음 단계로 이동할 수 있습니다." ;;
  1) echo "[다음 행동] 검사는 완료됐지만 block입니다. primary_block_reason부터 해결합니다." ;;
  2) echo "[다음 행동] 담당자 승인이 필요합니다." ;;
  3) echo "[다음 행동] 검사를 완료하지 못했습니다. 입력과 Git object를 확인합니다." ;;
  *) echo "[다음 행동] 알 수 없는 종료코드입니다: $VENDOR_REBUILD_EXIT" ;;
esac

exit "$VENDOR_REBUILD_EXIT"
