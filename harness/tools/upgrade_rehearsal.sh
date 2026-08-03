#!/usr/bin/env bash
# OM_TEMP 1.13.0 -> 1.13.1 업그레이드 예행연습.
#
# 공식 배포본과 OM_TEMP 원격 branch만으로 검사 후보를 처음부터 다시 만든다.
# 각 단계는 실행한 명령과 기대값을 그대로 출력하므로, 화면을 그대로 캡처해
# 증거로 쓸 수 있다. 등록 폴더나 원격 branch를 바꾸지 않는다.
#
# 사용법:
#   harness/tools/upgrade_rehearsal.sh <OM_TEMP-clone-경로> [작업-경로]
#
# 사전 준비:
#   - OM_TEMP clone에 origin/patch/om-1.13.0 과 origin/custom/om-1.13.0 이 있어야 한다
#   - 공식 OpenMetadata 저장소에 네트워크로 접근할 수 있어야 한다
#   - 검사 저장소 루트에서 실행한다

set -euo pipefail

OM_TEMP="${1:?OM_TEMP clone 경로를 첫 번째 인자로 주십시오}"
WORK="${2:-$(pwd)/../upgrade-rehearsal}"
GOV="$(pwd)"
PY="${PYTHON:-python3}"

UPSTREAM_URL="https://github.com/open-metadata/OpenMetadata.git"
TAG_A="1.13.0-release"
TAG_B="1.13.1-release"
SHA_A="f329dd4a7e47134a2bd5a06af6181b0ee527ddd9"
SHA_B="afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9"
PATCH_REF="origin/patch/om-1.13.0"
CUSTOM_REF="origin/custom/om-1.13.0"

step()  { printf '\n\033[1;36m━━ %s ━━\033[0m\n' "$*"; }
run()   { printf '\033[36m$\033[0m %s\n' "$*"; eval "$@"; }
ok()    { printf '\033[32m  OK  %s\033[0m\n' "$*"; }
warn()  { printf '\033[33m  !!  %s\033[0m\n' "$*"; }
die()   { printf '\033[31m  중단: %s\033[0m\n' "$*" >&2; exit 1; }

expect() {  # expect <설명> <실제> <기대>
  if [ "$2" = "$3" ]; then ok "$1 = $2"
  else die "$1 이(가) 기대와 다릅니다. 실제=$2 기대=$3"; fi
}

# ── 0. 사전 점검 ────────────────────────────────────────────
step "0. 사전 점검"
[ -d "$OM_TEMP/.git" ] || die "$OM_TEMP 은(는) git 저장소가 아닙니다"
[ -f "$GOV/harness/prepare_registration.py" ] || die "검사 저장소 루트에서 실행하십시오"
command -v git >/dev/null || die "git 이 없습니다"
"$PY" -c 'import yaml, jsonschema' 2>/dev/null || die "python 의존성 부족: pip install pyyaml jsonschema pathspec"

if [ -n "$(git -C "$OM_TEMP" status --porcelain)" ]; then
  die "제품 저장소에 커밋하지 않은 변경이 있습니다. 정리 후 다시 실행하십시오"
fi
ok "제품 저장소가 깨끗합니다"

for ref in "$PATCH_REF" "$CUSTOM_REF"; do
  git -C "$OM_TEMP" rev-parse --verify --quiet "$ref^{commit}" >/dev/null || die \
"제품 저장소에 $ref 이(가) 없습니다. 먼저 받아 주십시오:
    git -C '$OM_TEMP' fetch origin patch/om-1.13.0 custom/om-1.13.0"
done

PATCH_SHA="$(git -C "$OM_TEMP" rev-parse "$PATCH_REF")"
CUSTOM_SHA="$(git -C "$OM_TEMP" rev-parse "$CUSTOM_REF")"
expect "1.13.0 공식 기준 branch" "$PATCH_SHA" "2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50"
expect "1.13.0 행내 branch"      "$CUSTOM_SHA" "7d19c8952612e77467b0a80d6287170d814f1de1"

DIFF_N="$(git -C "$OM_TEMP" diff --name-only "$PATCH_REF..$CUSTOM_REF" | wc -l | tr -d ' ')"
expect "두 branch 사이 변경 파일 수" "$DIFF_N" "111"

# ── 1. 기능별 변경 기록 확인 ─────────────────────────────────
step "1. 기능별 변경 기록과 이름표 확인"

# 변경 기록 목록을 읽는다.
#
# macOS 기본 Bash 는 3.2 이므로 다음 두 가지를 피해야 한다.
#   - mapfile/readarray  : Bash 4 전용 내장 명령이라 아예 없다
#   - 빈 배열의 "${arr[@]}" 전개 : set -u 에서 unbound variable 로 죽는다
# 그래서 먼저 문자열로 받아 비었는지 확인한 뒤에만 배열을 만든다.
BANK_SHA_LIST="$(git -C "$OM_TEMP" rev-list --reverse "$PATCH_REF..$CUSTOM_REF")"
[ -n "$BANK_SHA_LIST" ] || die "$PATCH_REF..$CUSTOM_REF 사이에 변경 기록이 없습니다"

BANK_SHAS=()
while IFS= read -r line; do
  [ -n "$line" ] || continue
  BANK_SHAS[${#BANK_SHAS[@]}]="$line"
done <<EOF
$BANK_SHA_LIST
EOF

# 화면에 찍는 기록 번호는 항상 10자리로 고정한다.
# %h 나 rev-parse --short 는 저장소의 core.abbrev 설정에 따라 자릿수가
# 달라지므로, 전체 SHA 에서 앞 10자리를 직접 잘라 쓴다.
printf '\033[36m$\033[0m git log --reverse %s..%s\n' "$PATCH_REF" "$CUSTOM_REF"
MISSING=""
for sha in "${BANK_SHAS[@]}"; do
  sha10="$(printf '%s' "$sha" | cut -c1-10)"
  id="$(git -C "$OM_TEMP" log -1 \
        --format='%(trailers:key=Customization-ID,valueonly,separator=%x2C)' "$sha" \
        | tr -d '\n')"
  subject="$(git -C "$OM_TEMP" log -1 --format='%s' "$sha")"
  printf '%s | %s | %s\n' "$sha10" "${id:-(이름표 없음)}" "$subject"

  n="$(git -C "$OM_TEMP" log -1 \
       --format='%(trailers:key=Customization-ID,valueonly)' "$sha" | grep -c . || true)"
  [ "$n" = "1" ] || MISSING="$MISSING $sha10(${n}개)"
done
[ -z "$MISSING" ] || die "이름표가 하나가 아닌 변경 기록:$MISSING"
ok "변경 기록 ${#BANK_SHAS[@]}건 모두 이름표가 정확히 하나입니다"
expect "옮길 변경 기록 수" "${#BANK_SHAS[@]}" "8"

# ── 2. 공식 배포본 받기 ─────────────────────────────────────
step "2. 공식 1.13.0 / 1.13.1 배포본 받기"

# --filter=blob:none 을 쓰지 않는다.
#
# 필터를 걸면 git 이 promisor remote 를 등록하고, 파일 내용이 필요할 때마다
# 그 자리에서 원격을 다시 부른다. 그 호출이 실패하는 환경에서는 예행연습이
# 한참 뒤 단계에서 갑자기 죽는다. 필요한 두 시점을 지금 완전히 받아 두면
# 이후로는 네트워크가 끊겨도 끝까지 돈다.
#
# 대신 --depth 1 로 그 두 시점만 받는다. 전체 이력까지 받으면 2.8GB·3분이
# 되지만, 이렇게 하면 200MB·15초 안팎이고 필요한 것은 다 들어 있다.
run "git -C '$OM_TEMP' fetch --depth 1 --no-tags '$UPSTREAM_URL' \
  'refs/tags/$TAG_A:refs/tags/OFFICIAL_1_13_0' \
  'refs/tags/$TAG_B:refs/tags/OFFICIAL_1_13_1'"
expect "공식 1.13.0 고유번호" "$(git -C "$OM_TEMP" rev-parse OFFICIAL_1_13_0^{commit})" "$SHA_A"
expect "공식 1.13.1 고유번호" "$(git -C "$OM_TEMP" rev-parse OFFICIAL_1_13_1^{commit})" "$SHA_B"

# 받은 것이 정말 온전한지 여기서 확인한다.
# 파일 내용을 실제로 한 번 읽어 본다. 빠져 있으면 3단계나 5단계에서
# 알아보기 어려운 오류로 터지는 대신, 여기서 원인과 함께 멈춘다.
PROBE="openmetadata-ui/src/main/resources/ui/package.json"
for tag in OFFICIAL_1_13_0 OFFICIAL_1_13_1; do
  git -C "$OM_TEMP" cat-file blob "$tag:$PROBE" >/dev/null 2>&1 || die \
"$tag 의 파일 내용을 읽지 못했습니다. 공식 배포본을 온전히 받지 못한 상태입니다.
    아래를 실행해 다시 받은 뒤 예행연습을 재시도하십시오:
      git -C '$OM_TEMP' fetch --depth 1 --no-tags --refetch '$UPSTREAM_URL' \\
        'refs/tags/$TAG_A:refs/tags/OFFICIAL_1_13_0' \\
        'refs/tags/$TAG_B:refs/tags/OFFICIAL_1_13_1'"
done
ok "공식 배포본 두 시점의 파일 내용까지 확인했습니다"

# ── 3. 적용 전 영향 확인 (T42) ──────────────────────────────
step "3. 적용 전 영향 확인 — 공식 변경이 우리 기능에 닿는가"
WATCH_OUT="$WORK/upgrade-watch.json"
mkdir -p "$WORK"
set +e
PYTHONPATH="$GOV/harness" "$PY" "$GOV/harness/run_upgrade_watch.py" \
  --repo "$OM_TEMP" --harness "$GOV/harness" \
  --registration "$GOV/harness/registrations/om-temp-1.13.1" \
  --upstream-base OFFICIAL_1_13_0 --upstream-target OFFICIAL_1_13_1 \
  --output "$WATCH_OUT"
WATCH_EXIT=$?
set -e
printf '  종료코드 %s  ' "$WATCH_EXIT"
case "$WATCH_EXIT" in
  0) ok "통과" ;;
  2) warn "확인 필요 — 담당자가 영향 경로를 검토해야 합니다 (실패 아님)" ;;
  1) die "중단 판정" ;;
  3) die "검사 불능 — 입력을 신뢰할 수 없습니다" ;;
esac

# ── 4. 작업 폴더 준비 ───────────────────────────────────────
step "4. 공식 1.13.1 위에 작업 폴더 만들기"
[ -e "$WORK/tree" ] && die "$WORK/tree 이(가) 이미 있습니다. 지우거나 다른 경로를 지정하십시오"
run "git -C '$OM_TEMP' worktree add -q -b rehearsal/patch-1.13.1 '$WORK/tree' OFFICIAL_1_13_1"
run "git -C '$WORK/tree' switch -q -c rehearsal/custom-1.13.1"
ok "작업 폴더: $WORK/tree"

# ── 5. 기능을 하나씩 옮겨 얹기 ──────────────────────────────
step "5. 기능 8건을 하나씩 옮겨 얹기"
CONFLICT_LOG="$WORK/conflicts.tsv"
: > "$CONFLICT_LOG"
for sha in "${BANK_SHAS[@]}"; do
  id="$(git -C "$OM_TEMP" log -1 --format='%(trailers:key=Customization-ID,valueonly)' "$sha" | tr -d '\n')"
  short="$(printf '%s' "$sha" | cut -c1-10)"   # core.abbrev 와 무관하게 10자리
  printf '\n\033[36m$\033[0m git cherry-pick %s   # %s\n' "$short" "$id"

  if git -C "$WORK/tree" cherry-pick "$sha" >/dev/null 2>&1; then
    ok "$id  충돌 없음"
    printf '%s\t%s\t0\t0\n' "$id" "$short" >> "$CONFLICT_LOG"
    continue
  fi

  n="$(git -C "$WORK/tree" diff --name-only --diff-filter=U | wc -l | tr -d ' ')"
  warn "$id  부딪힌 파일 ${n}개 — 정리 도구를 실행합니다"

  nonjson="$(git -C "$WORK/tree" diff --name-only --diff-filter=U | grep -v '\.json$' || true)"
  if [ -n "$nonjson" ]; then
    printf '%s\n' "$nonjson"
    die "$id: JSON 이외 파일이 부딪혔습니다. 자동 정리 대상이 아니므로 코드 담당자가 직접 해결해야 합니다"
  fi

  # 정리 도구는 파일마다 한 줄씩 낸다. 첫 줄만 읽으면 파일 하나의 값이
  # 전체 합계처럼 보이므로, 모든 줄을 더한다.
  #
  # 양쪽이 같은 항목을 고쳤으면 도구가 거부한다. set -e 에 맡기면 파이썬
  # traceback 만 뜨고 끝나므로, 상태를 직접 받아 한국어로 설명한다.
  set +e
  resolved="$(PYTHONPATH="$GOV/harness" "$PY" "$GOV/harness/tools/resolve_nonoverlapping_json_conflicts.py" \
              --repo "$WORK/tree" 2>"$WORK/resolve-error.txt")"
  resolve_status=$?
  set -e
  if [ "$resolve_status" -ne 0 ]; then
    sed 's/^/    /' "$WORK/resolve-error.txt"
    die "$id: 새 버전과 우리가 같은 항목을 고쳤습니다. 어느 쪽을 남길지는
    자동으로 정할 수 없으므로 코드 담당자가 직접 결정해야 합니다.
    위 overlapping leaf changes 줄에 그 항목 이름이 있습니다."
  fi
  [ -n "$resolved" ] || die "$id: 정리 도구가 아무것도 처리하지 못했습니다. 양쪽이 같은 항목을 고쳤을 수 있습니다"
  printf '%s\n' "$resolved" | sed 's/^/    /'
  fixed="$(printf '%s\n' "$resolved" | grep -c 'leaf changes=')"
  leaf="$(printf '%s\n' "$resolved" | grep -oE 'leaf changes=[0-9]+' | cut -d= -f2 \
          | awk '{sum += $1} END {print sum + 0}')"
  ok "$id  파일 ${fixed}개에서 항목 ${leaf}개를 되살렸습니다"

  git -C "$WORK/tree" add -A
  GIT_EDITOR=true git -C "$WORK/tree" cherry-pick --continue >/dev/null
  printf '%s\t%s\t%s\t%s\n' "$id" "$short" "$n" "$leaf" >> "$CONFLICT_LOG"
done

echo
printf '  %-14s %-12s %10s %12s\n' 기능 원본기록 부딪힌파일 되살린항목
awk -F'\t' '{printf "  %-14s %-12s %10s %12s\n",$1,$2,$3,$4}' "$CONFLICT_LOG"
echo "  (부딪힌파일 = 충돌한 파일 수, 되살린항목 = 그 파일들 안에서 되살린 항목 수의 합)"

# ── 6. 결과 확인 ────────────────────────────────────────────
step "6. 만들어진 후보 확인"
CAND="$(git -C "$WORK/tree" rev-parse HEAD)"
NEW_DIFF="$(git -C "$WORK/tree" diff --name-only OFFICIAL_1_13_1..HEAD | wc -l | tr -d ' ')"
NEW_N="$(git -C "$WORK/tree" rev-list --count OFFICIAL_1_13_1..HEAD)"
echo "  검사 후보 고유번호 : $CAND"
expect "옮겨진 변경 기록 수" "$NEW_N" "8"
expect "공식 1.13.1 대비 변경 파일 수" "$NEW_DIFF" "$DIFF_N"

cat > "$WORK/candidate.txt" <<EOF
candidate_sha=$CAND
upstream_sha=$SHA_B
changed_paths=$NEW_DIFF
applied_commits=$NEW_N
EOF

step "예행연습 완료"
cat <<EOF
  작업 폴더    : $WORK/tree
  검사 후보    : $CAND
  요약 파일    : $WORK/candidate.txt
  영향 확인    : $WATCH_OUT
  충돌 기록    : $CONFLICT_LOG

  다음 단계는 등록자료를 이 후보에 맞추는 것입니다. 등록자료는 손으로
  고치지 않고 준비도구의 plan -> 승인 -> apply 를 사용합니다. 절차는
  docs/00-사용가이드/OM_TEMP_검사전_준비도구_쉬운사용법.md 에 있습니다.

  정리하려면:
    git -C "$OM_TEMP" worktree remove "$WORK/tree"
    git -C "$OM_TEMP" branch -D rehearsal/patch-1.13.1 rehearsal/custom-1.13.1
EOF
