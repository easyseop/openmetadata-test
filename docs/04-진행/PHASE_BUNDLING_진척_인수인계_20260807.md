# Phase 번들링 진척·인수인계 (다른 컴퓨터에서 이어받기용)

> 브랜치: `codex/phase-bundling`, 원격 `origin/codex/phase-bundling` 추적.
> 구현 HEAD `446b5a0e53`, Codex 검토·인수인계 commit `cb225109d3`까지 2026-08-07
> 원격 push 완료. 아래 로컬 전용 파일을 원격 작업과 구분한다.
> 작성: 2026-08-07. 격리 원칙: 예행연습 브랜치(`codex/om-1.13.1-rehearsal-baseline-20260806`)·제품 코드·evidence·vendor merge **무수정**.

## 1. 이어받기 (다른 컴퓨터)
```bash
git clone https://github.com/easyseop/openmetadata-test.git   # 이미 있으면 fetch
git checkout codex/phase-bundling
git pull
# 개발계획·수정보완·반례 테스트와 이 문서를 먼저 읽는다:
#   docs/04-진행/PHASE_BUNDLING_개발계획_20260807.md   (구현 사양 + 테스트 케이스 시드)
#   docs/04-진행/PHASE_BUNDLING_개발설계_수정보완_20260807.md
#   docs/04-진행/PHASE_BUNDLING_반례테스트케이스_20260807.md
#   docs/04-진행/PHASE_BUNDLING_진척_인수인계_20260807.md (이 문서)
```

## 2. 현재 상태 (한 줄)
**phase 번들링 L1~L8 라이브러리 구현은 commit됐으나 Codex 검토에서 P0 문제 6건이
확인됐다. 현재 상태는 구현 완료가 아니라 검토용 WIP다.** 제품 코드·vendor merge·
기존 예행연습 evidence는 수정하지 않는다.

## 3. 확정된 결정 (LOCKED — 재논의 불필요)
- `8ac18ad053d9274774e274ba17b35911ac0b9dcb`(tree `e86980f6…`)는 현재
  승인 기준 예시이며 영구 하드코딩하지 않는다. `d952a838`는 최초 snapshot,
  `85e60d42`는 동일 tree 병렬 commit으로 provenance에만 남긴다.
- 승인 시각이 가장 최근인 lock을 자동 선택하지 않는다. 관리자가 승인된 lock을
  `active-candidate.yaml`로 명시한다. 다음 실행부터 새 활성 기준을 사용하되, 한
  실행이 시작되면 선택한 commit·tree를 끝까지 고정한다.
- verdict는 기존 **4종 고정**(pass/approval/block/analysis_error), `EXIT_CODE={pass0,block1,approval2,analysis_error3}`. `not_evaluated`·`incomplete`를 **verdict로 신설 금지** → `execution_status`(gate)·`phase_status`(실행) 직교 필드로 표현.
- 기존 `acgh/candidate.py`의 schema v1·v2 `CandidateLock`을 재사용한다. 기존 계획의
  평면형 lock schema를 새로 만들지 않는다.
- candidate-lock=기술 기준만, 승인은 별도 `*.approval.yaml`(+`candidate_lock_digest` 연결, 변경 시 자동 무효).
- gate 로직 **재구현 금지** — 기존 러너 호출 + 회귀(parity) test로 동일 보장.
- premerge는 T42·T93 policy·T51/T52·watch-suggest를 수행한다. T41·T43·T93
  exact-scope는 공식 target을 병합한 실제 postmerge candidate에서 수행한다.
- 입력 누락은 `skipped_missing_input`, 프로그램 예외·timeout·잘못된 JSON은
  `failed + analysis_error`로 구분한다.
- 상세 사양과 C1~C114 테스트는 수정보완·반례 테스트 문서를 참조한다.

## 4. 이 커밋에 포함된 것 / 포함 안 된 것
- commit `8d7de50d62`: 최초 개발계획과 이 인수인계 문서.
- commit `7f7bf1b383`: 개발설계 수정보완과 C1~C114 반례 테스트 문서.
- commit `ae1bdbce4b`: L1 active candidate 선택 구현과 테스트.
- commit `446b5a0e53`: L2~L8 preflight·gate 실행·집계·catalog·rollup·evidence와 테스트.
- **포함 안 됨(의도적):**
  - 테스트 스킬(`.claude/skills/test`, `.claude/skills/property-based-testing`) — third-party라 커밋 제외. 아래 6절로 재설치.
  - `.claude/` — 사용자·Claude 로컬 도구 자료로 commit 제외.

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

## 7. 다음 실행 단계

1. `PHASE_BUNDLING_CODEX_구현검토_20260807.md`의 P0 여섯 건을 실패 테스트로 추가한다.
2. digest 보호 범위, 실제 timeout, phase catalog 강제, 빈 active source, debt threshold
   정책을 수정한다.
3. `om_workflow.py`에 candidate-select·preflight·premerge-check·postmerge-check·
   prep-official·status 명령을 연결한다.
4. validate·source·contract GateSpec을 postmerge runner에 실제 연결한다.
5. 직접 runner parity와 end-to-end phase 실행을 다시 검증한다.
6. 수정 후 P0 완료 여부를 다시 검토받고, 그 전에는 병합하지 않는다.

## 8. 미완료·보류 (기록)
- P0 runtime baseline, runtime Contract 9개 — 보류.
- T41(change-intent 입력 없음), T43(승인된 conflict-rate 없음) — 입력 확보 후.
- ingestion(airflow) — contract에 불필요, 보류.
- 08-07 사전검사(T93 exact-scope 등)는 candidate=d952a838로 실행됨 → 정본 8ac18ad로 **재실행 필요**(T42·공식 구조화 diff는 유지 가능).

## 9. 제약 (항상 유지)
예행연습 브랜치·제품 코드·evidence·vendor merge 무수정. custom branch 수정/충돌해결/merge 금지. 구현은 격리 브랜치에서만, 병합은 승인 후.

## 10. 2026-08-07 원격 공유 후 로컬 상태

```text
?? .claude/
```

- `.claude/`는 기존 사용자·Claude 도구 자료이므로 수정·stage하지 않는다.
- L1~L8 Python 파일은 commit `ae1bdbce4b`, `446b5a0e53`에 포함됐다.
- 구현 완료보고·Codex 검토·인수인계는 commit `cb225109d3`까지 원격에 포함됐다.
- 다른 세션이 계속 작업할 수 있으므로 재개
  시 이 목록만 믿지 말고 가장 먼저 `git status --short --branch`를 다시 실행한다.
- branch는 `origin/codex/phase-bundling`을 추적한다. 다른 컴퓨터에서는 fetch 후 이
  원격 branch와 `CODEX_CURRENT_HANDOFF.md`를 먼저 확인한다.

## 11. Codex가 이번에 수행한 내용

1. 최초 계획의 C1~C20을 실제 `CandidateLock`, verdict, 기존 risk runner와 대조했다.
2. 다음 설계 결함을 확인했다.
   - 특정 SHA를 영구 기준처럼 설명한 점
   - 최신 승인 시각 자동 선택의 모호성
   - 기존 CandidateLock과 다른 평면형 schema
   - premerge에 postmerge gate가 혼합된 점
   - 프로그램 예외를 입력 누락과 함께 skip하는 점
3. `PHASE_BUNDLING_개발설계_수정보완_20260807.md`에 수정 설계를 작성했다.
4. `PHASE_BUNDLING_반례테스트케이스_20260807.md`에 C1~C114를 작성했다.
   P0는 C1~C74, P1은 C75~C106, P2는 C107~C114다.
5. 두 문서에 대해 `git diff --check`를 통과했다. 하네스 실행 테스트는 이 문서 작성
   작업에서는 수행하지 않았다.

## 12. Codex 구현 검토 결과

검토 문서: `docs/04-진행/PHASE_BUNDLING_CODEX_구현검토_20260807.md`

재실행 결과:

- phase 테스트 125개 통과, pytest skip 없음
- 기존 `test_verdict.py`, `test_candidate.py` 통과
- 실제 T42 subprocess parity가 현재 환경에서 실행됨

그러나 다음 P0 문제 때문에 완료 승인을 거부했다.

1. `om_workflow.py` phase 명령과 end-to-end orchestration이 없음
2. result digest가 gate reasons·evidence·detail을 보호하지 않음
3. `GateSpec.timeout`이 선언만 되고 실제 적용되지 않음
4. `run_gates()`가 phase catalog를 강제하지 않음
5. active source 0개가 consistency 통과
6. debt thresholds 누락 시 fail-closed가 아니라 기본값으로 실행

추가 P1 문제는 phase 승인자·시각·근거 검증 부재와 GateExecution detail 유실이다.
원격에는 검토용 WIP branch로만 공유하고, 수정 전 병합·운영 사용을 금지한다.
