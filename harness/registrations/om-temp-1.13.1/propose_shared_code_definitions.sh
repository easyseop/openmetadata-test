#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OM_TEST_REPO=$(CDPATH= cd -- "$SCRIPT_DIR/../../.." && pwd)

if [[ -z "${OM_CODE_REPO:-}" ]]; then
  echo '[중단] OM_CODE_REPO가 설정되지 않았습니다.' >&2
  echo '예: export OM_CODE_REPO="$HOME/om-work/om-temp-real-1.13.1"' >&2
  exit 2
fi

OFFICIAL_REF=${SHARED_CODE_OFFICIAL_REF:-upstream-1.13.1-release}
CANDIDATE_REF=${SHARED_CODE_CANDIDATE_REF:-codex/om-1.13.1-id-series-upstream}
INPUT_DIR="$OM_TEST_REPO/harness/preparation-inputs/om-temp-1.13.1"

PYTHONPATH="$OM_TEST_REPO/harness" "$OM_TEST_REPO/.venv/bin/python" \
  "$OM_TEST_REPO/harness/propose_shared_code_definitions.py" \
  --repo "$OM_CODE_REPO" \
  --official "$OFFICIAL_REF" \
  --candidate "$CANDIDATE_REF" \
  --owners "$OM_TEST_REPO/harness/registrations/om-temp-1.13.1/shared-path-owners.yaml" \
  --draft "$INPUT_DIR/shared-code-definitions-draft.yaml" \
  --output "$INPUT_DIR/shared-code-definitions-proposed.yaml"
