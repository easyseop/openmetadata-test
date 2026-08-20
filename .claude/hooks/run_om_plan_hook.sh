#!/bin/sh
set -eu

project_dir=${CLAUDE_PROJECT_DIR:-$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)}
wrapper="$project_dir/.claude/hooks/run_om_plan_hook.py"

if [ -n "${OM_PLAN_PYTHON:-}" ]; then
  exec "$OM_PLAN_PYTHON" "$wrapper"
fi

for candidate in "$project_dir/.venv/bin/python" python3.12 python3.11 python3; do
  if [ -x "$candidate" ] || command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c 'import sys, yaml, jsonschema, pathspec; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
      exec "$candidate" "$wrapper"
    fi
  fi
done

echo "om-plan hook requires Python 3.11+ with PyYAML, jsonschema, and pathspec installed" >&2
exit 2
