#!/usr/bin/env bash
# 재현 가능한 OpenMetadata 미러 획득 (blobless, 두 고정 태그만).
# 결과: $MIRROR 에 refs/tags/UPSTREAM_A(1.12.13), UPSTREAM_B(1.13.0).
set -euo pipefail

MIRROR="${1:-/home/user/om-mirror}"
URL="https://github.com/open-metadata/OpenMetadata.git"
A="1.12.13-release"; A_SHA="e6c665019a583b7938f30fbb7bafb7e1f82c5dd7"
B="1.13.0-release";  B_SHA="f329dd4a7e47134a2bd5a06af6181b0ee527ddd9"

rm -rf "$MIRROR"
git init -q "$MIRROR"
git -C "$MIRROR" remote add origin "$URL"
git -C "$MIRROR" fetch -q --depth 1 --filter=blob:none origin \
  "refs/tags/${A}:refs/tags/UPSTREAM_A" \
  "refs/tags/${B}:refs/tags/UPSTREAM_B"

got_a="$(git -C "$MIRROR" rev-parse UPSTREAM_A^{commit})"
got_b="$(git -C "$MIRROR" rev-parse UPSTREAM_B^{commit})"
[ "$got_a" = "$A_SHA" ] || { echo "A SHA mismatch: $got_a != $A_SHA" >&2; exit 1; }
[ "$got_b" = "$B_SHA" ] || { echo "B SHA mismatch: $got_b != $B_SHA" >&2; exit 1; }
echo "OK  UPSTREAM_A=$got_a  UPSTREAM_B=$got_b"
