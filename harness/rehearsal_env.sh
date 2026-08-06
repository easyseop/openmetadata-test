#!/usr/bin/env sh
# Source this file from a clone of the openmetadata-test repository.
# It keeps the rehearsal commands independent from one developer's home path.

OM_TEST_REPO="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "검사기 저장소 안에서 source harness/rehearsal_env.sh 를 실행하세요." >&2
  return 1 2>/dev/null || exit 1
}
OM_CODE_REPO="${OM_CODE_REPO:-$HOME/om-work/om-temp-real-1.13.1}"

if [ -z "${KB_SOURCE_REPO:-}" ]; then
  KB_HOME_CANDIDATE="$HOME/om-work/kb_openmetadata"
  KB_SIBLING_CANDIDATE="$(dirname "$OM_TEST_REPO")/review-kb-openmetadata"

  if [ -d "$KB_HOME_CANDIDATE/.git" ]; then
    KB_SOURCE_REPO="$KB_HOME_CANDIDATE"
  elif [ -d "$KB_SIBLING_CANDIDATE/.git" ]; then
    KB_SOURCE_REPO="$KB_SIBLING_CANDIDATE"
  else
    KB_SOURCE_REPO="$KB_HOME_CANDIDATE"
  fi
fi

export OM_TEST_REPO
export OM_CODE_REPO
export KB_SOURCE_REPO

unset KB_HOME_CANDIDATE KB_SIBLING_CANDIDATE

printf 'OM_TEST_REPO=%s\n' "$OM_TEST_REPO"
printf 'OM_CODE_REPO=%s\n' "$OM_CODE_REPO"
printf 'KB_SOURCE_REPO=%s\n' "$KB_SOURCE_REPO"
