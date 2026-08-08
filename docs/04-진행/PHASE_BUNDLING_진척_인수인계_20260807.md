# Phase 번들링 진척·인수인계 (다른 컴퓨터에서 이어받기용)

> 브랜치: `codex/phase-bundling` (원격 push됨). 다른 컴퓨터에서 이 브랜치를 pull해 이어서 진행한다.
> 작성: 2026-08-07. 격리 원칙: 예행연습 브랜치(`codex/om-1.13.1-rehearsal-baseline-20260806`)·제품 코드·evidence·vendor merge **무수정**.

## 1. 이어받기 (다른 컴퓨터)
```bash
git clone https://github.com/easyseop/openmetadata-test.git   # 이미 있으면 fetch
git checkout codex/phase-bundling
git pull
# 개발계획과 이 문서를 먼저 읽는다:
#   docs/04-진행/PHASE_BUNDLING_개발계획_20260807.md   (구현 사양 + 테스트 케이스 시드)
#   docs/04-진행/PHASE_BUNDLING_진척_인수인계_20260807.md (이 문서)
```

## 2. 현재 상태 (한 줄)
**phase 번들링은 "계획 확정 + 착수 승인 대기" 단계. 코드는 아직 작성 안 함.** worktree/브랜치와 개발계획·테스트 스킬만 준비됨.

## 3. 확정된 결정 (LOCKED — 재논의 불필요)
- **정본 candidate = `8ac18ad053d9274774e274ba17b35911ac0b9dcb`** (tree `e86980f6…`). `d952a838`=최초 snapshot(provenance), `85e60d42`=동일 tree 병렬 commit(provenance). → consistency 검사는 **활성 기준만** 비교, 과거값은 provenance로 제외.
- verdict는 기존 **4종 고정**(pass/approval/block/analysis_error), `EXIT_CODE={pass0,block1,approval2,analysis_error3}`. `not_evaluated`·`incomplete`를 **verdict로 신설 금지** → `execution_status`(gate)·`phase_status`(실행) 직교 필드로 표현.
- 기존 `acgh/candidate.py`(`CandidateLock`) **재사용**, 별도 모듈 신설 금지.
- candidate-lock=기술 기준만, 승인은 별도 `*.approval.yaml`(+`candidate_lock_digest` 연결, 변경 시 자동 무효).
- gate 로직 **재구현 금지** — 기존 러너 호출 + 회귀(parity) test로 동일 보장.
- 착수 순서·컴포넌트 사양·테스트 케이스 시드(C1~C20)는 **개발계획 문서** 참조.

## 4. 이 커밋에 포함된 것 / 포함 안 된 것
- 포함: `PHASE_BUNDLING_개발계획_20260807.md`, 이 인수인계 문서.
- **포함 안 됨(의도적):**
  - 테스트 스킬(`.claude/skills/test`, `.claude/skills/property-based-testing`) — third-party라 커밋 제외. 아래 6절로 재설치.
  - 구현 코드 — 아직 없음(승인 후 작성).

## 5. 이 저장소 밖(원본 머신 로컬)에 있는 것 — 다른 머신엔 없음
| 항목 | 위치(원본 머신) | 다른 머신에서 |
|---|---|---|
| Codex 검토 MD 4종(CODEX-01~04) | `~/openmetadata-lab/docs/` | 필요 시 별도 공유 |
| Docker/OpenMetadata 서비스(custom/om-1.13.1 기동) | colima + 로컬 이미지 | 재구축 필요(`~/openmetadata-lab/scripts`) |
| OM_CODE_REPO + `official/om-1.13.2` + 사전검사 evidence | `~/om-work/om-temp-real-1.13.1`, `evidence/om-1.13.2-premerge-20260807-premerge-01/` | `prep-official`로 재생성 |
| candidate `8ac18ad`/`official/om-1.13.2` git 객체 | 로컬(upstream fetch됨) | upstream에서 재fetch 필요 |

## 6. 테스트 스킬 재설치 (프로젝트 범위, Claude만)
```bash
# 소스
git clone --depth 1 https://github.com/boshu2/agentops.git /tmp/agentops
git clone --depth 1 https://github.com/trailofbits/skills.git /tmp/tob
# 설치 (.agents/AGENTS.md 는 건드리지 않음)
mkdir -p .claude/skills
cp -R /tmp/agentops/skills/test .claude/skills/test
cp -R /tmp/tob/plugins/property-based-testing/skills/property-based-testing .claude/skills/property-based-testing
# 호출: /test , /property-based-testing
```

## 7. 다음 실행 단계 (승인 후)
개발계획 §7 순서: candidate_select → consistency → preflight → gate 독립실행+집계 → rollup → premerge-check(→ parity test) → postmerge-check → prep-official → status. 각 단계 test 먼저(red→green). 완료 후 **병합하지 말고** 변경파일·test 결과·parity 비교 보고.

## 8. 미완료·보류 (기록)
- P0 runtime baseline, runtime Contract 9개 — 보류.
- T41(change-intent 입력 없음), T43(승인된 conflict-rate 없음) — 입력 확보 후.
- ingestion(airflow) — contract에 불필요, 보류.
- 08-07 사전검사(T93 exact-scope 등)는 candidate=d952a838로 실행됨 → 정본 8ac18ad로 **재실행 필요**(T42·공식 구조화 diff는 유지 가능).

## 9. 제약 (항상 유지)
예행연습 브랜치·제품 코드·evidence·vendor merge 무수정. custom branch 수정/충돌해결/merge 금지. 구현은 격리 브랜치에서만, 병합은 승인 후.
