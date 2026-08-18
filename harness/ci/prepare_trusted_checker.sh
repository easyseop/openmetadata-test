#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "usage: prepare_trusted_checker.sh CHECKER_ROOT" >&2
  exit 3
fi

checker_root=$1
case "$checker_root" in
  ""|/)
    echo "refusing unsafe checker root: $checker_root" >&2
    exit 3
    ;;
esac

if [ ! -d "$checker_root/.git" ] || [ ! -d "$checker_root/harness" ]; then
  echo "checker root must be a Git checkout containing harness/: $checker_root" >&2
  exit 3
fi

if [ -n "${CI_COMMIT_SHA:-}" ] && \
   [ "$(git -C "$checker_root" rev-parse HEAD)" != "$CI_COMMIT_SHA" ]; then
  echo "checker HEAD does not match CI_COMMIT_SHA" >&2
  exit 3
fi

harness_root=$checker_root/harness

# This must run before any checker Python process. A timestamp-valid .pyc can
# otherwise execute code that is intentionally excluded from directory_digest.
find "$harness_root" -name __pycache__ -prune -exec rm -rf -- {} +
find "$harness_root" \( -name '*.pyc' -o -name '*.pyo' \) -exec rm -f -- {} +

remaining=$(find "$harness_root" \
  \( -name __pycache__ -o -name '*.pyc' -o -name '*.pyo' \) \
  -print -quit)
if [ -n "$remaining" ]; then
  echo "Python bytecode remains in trusted checker: $remaining" >&2
  exit 3
fi

if ! git -C "$checker_root" diff --quiet --ignore-submodules -- . || \
   ! git -C "$checker_root" diff --cached --quiet --ignore-submodules -- .; then
  echo "cache cleanup changed tracked checker files" >&2
  exit 3
fi
