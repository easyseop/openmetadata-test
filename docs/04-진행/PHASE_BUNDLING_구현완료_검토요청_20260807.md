# Phase 번들링 구현 완료 — 검토 요청

> 브랜치: `codex/phase-bundling` (worktree). 로컬 HEAD `446b5a0e53`.
> 상태: **구현 완료, 로컬 커밋만. 푸시 안 함.** 예행연습 브랜치·제품 코드·evidence·vendor merge 무수정.
> 기준 문서: `PHASE_BUNDLING_개발설계_수정보완_20260807.md`, `PHASE_BUNDLING_반례테스트케이스_20260807.md`
> 검증: 구현은 배경 에이전트가, **재실행·감사는 이 세션(Claude)이 독립적으로** 수행.

## 1. 무엇을 만들었나 (L1~L8)
전부 신규 파일. 기존 모듈은 하나도 수정하지 않았고, gate 판정 로직은 재구현 없이 **기존 acgh 함수/러너를 호출**만 한다.

| 레이어 | 파일 | 내용 |
|---|---|---|
| L1 candidate 선택 | `acgh/candidate_select.py` | 명시적 `active-candidate.yaml` 포인터(최신 자동선택 X), 기존 `CandidateLock`/digest 재사용, 승인 digest 결속 |
| L2 preflight | `acgh/preflight.py` | 입력 문제 **일괄 보고**(첫 오류에서 안 멈춤), blocking vs gate별 선택, consistency는 활성 기준만(과거 provenance 제외), conflict-rate/NaN/Inf 검증, blob fetch 안내 |
| L3 gate 독립실행 | `acgh/phase.py` | gate별 `execution_status`(executed/skipped_missing_input/blocked_by_preflight/**failed**), 한 gate 실패가 다른 gate 안 막음 |
| L4 집계 | `acgh/phase.py` | `SEVERITY_RANK` 집계(종료코드 크기 아님), `phase_status`(complete/incomplete), 필수 gate 미실행→analysis_error·exit3 |
| L5 catalog 분리 | `acgh/phase.py` | premerge={T42,T93 policy,T51/T52,watch-suggest(자문)} / postmerge={ancestry+binding,T41,T43,T93 exact-scope,validate,source,contract}. baseline-as-candidate·비후손 거부 |
| L7 3단 출력 | `acgh/rollup.py` | 한 시스템 JSON에서 관리자/실무자/시스템 렌더 + 불변식 검사 |
| L8 evidence·승인 | `acgh/phase.py` | 판단 digest(timestamp 제외), 원자적 쓰기, 승인=result_digest 결속(입력 변경 시 무효), run-id 경로이탈 차단 |

## 2. 테스트 결과 (이 세션이 직접 재실행)
```
cd harness
PYTHONPATH=$(pwd) <venv>/python -m pytest tests/test_phase_*.py -q
→ 125 passed, 0 skipped   (재실행 확인, 에이전트 보고와 일치)
```
- **P0: 74/74 PASS** (C1~C74 전용 테스트로 커버, 전부 green)
- **P1: 28/32** (미구현 4건은 5절, 런타임 skip 0 — 작성된 테스트는 전부 실행됨)
- **P2: 안전 관련만 커버**(C110 명령삽입, C114 긴 사유, C111 비밀 미노출). 성능/symlink 제외
- **4-verdict parity 일치**: pass(C66)/approval(C67)/block(C68)/analysis_error(C69) 각각 번들 gate vs 동일 acgh 함수 직접호출을 {name,verdict,reasons,target_count}로 비교·일치. **실 러너 subprocess parity**: `run_upgrade_watch.py` vs 번들을 실제 `~/om-work/om-temp-real-1.13.1`(base `official/om-1.13.1`, target `official/om-1.13.2`, 1702 경로)에서 실행·일치. 재구현 mutant는 parity 실패(C74)
- **PBT(hypothesis)**: digest 결정성/commit변경→digest변경(L1), 집계 순서독립·SEVERITY_RANK(C61/C64), exit-code-max mutant 실패(C65)

## 3. 독립 검증·감사 결과 (이 세션)
| 점검 | 결과 |
|---|---|
| 전체 phase 테스트 직접 재실행 | **125 passed, 0 skipped** ✅ |
| skip/xfail로 통과 위장? | 없음(‘skipped_missing_input’은 도메인 상태어일 뿐, pytest skip/xfail 마커 0) ✅ |
| parity가 실제 러너 호출? | `subprocess`로 `run_upgrade_watch.py` 실행 확인 ✅ |
| gate 재구현 아님? | `phase.py`가 `evaluate_upgrade_watch/check_policy_drift/diff_file/suggest_watch_paths/ancestry/debt…` 호출 ✅ |
| 기존 파일 수정? | 없음 — 신규 13개만(git status: 기존 harness M 0) ✅ |
| 회귀? | 기존 `test_verdict`·`test_candidate` 재실행 pass ✅ |

⚠️ **정직히 기록:** 전체 스위트 `--collect-only` 시 `tests/test_om_workflow.py`가 `No module named 'harness'`로 collection 에러. 이 파일은 **내가 안 건드린 기존 파일**이고, `harness` 패키지 import 관례(실행 루트) 문제로 **phase 번들링 변경과 무관**(내 모듈은 `acgh`로 import, 통과한 테스트들과 동일 관례). phase 테스트·핵심 기존 테스트는 영향 없음.

## 4. 설계(수정보완) 준수 확인
- 특정 SHA 영구 하드코딩 없음 — candidate는 lock/인자에서 옴, active 포인터 명시(최신 자동선택 X)
- 기존 `CandidateLock`(schema v1·v2) 재사용, 평면 schema 신설 없음
- verdict 4종 고정 + `SEVERITY_RANK` 집계 + `phase_status`/`execution_status` 직교, `failed`≠`skipped_missing_input`
- premerge는 T41/T43/T93-exact-scope를 **안** 함(postmerge 전용), watch-suggest·structdiff는 자문(verdict 제외)
- 승인=result_digest 결속(입력 변경 시 무효), digest에서 timestamp 제외, 사람이 block/analysis_error→pass 불가

## 5. 미구현·부분 (P1/P2, 정직 고지 — P0엔 없음)
- **C106 미구현**: 수동 conflict-rate vs 병합증거 계산값 교차검증 미구현(새 기능 필요) → 지금은 conflict-rate를 입력으로만 취급
- **C112 미구현**: run-id 경로이탈은 차단(C109)하나, evidence base가 외부 symlink인 경우는 미차단
- **C75/C77 부분**: 네트워크 단절/ fetch 중단 내성은 구조상 성립(로컬 객체만 사용, 원자적 쓰기 C93)하나 실제 오프라인/중단 주입은 미시뮬레이션
- P2 성능(C113)·symlink 등은 범위 밖

## 6. 사람 STOP (실제 운영 전 필요 — 코드가 fail-closed로 막고 있음)
1. **활성 candidate-lock 부재**: `registrations/om-temp-1.13.1/candidate-locks/`에 승인된 lock+`active-candidate.yaml` 없음 → `select_active_candidate`가 정상적으로 `analysis_error` 반환(임의 실행 안 됨). 운영자가 8ac18ad baseline lock+비placeholder 승인 생성 필요.
2. **양성 postmerge 불가**: 실제 1.13.2 vendor-merge candidate가 아직 없음(현 `8ac18ad`는 1.13.1 태그 후손=기준선, 업그레이드 candidate 아님). postmerge 음성경로(C40/C41)는 증명됨, 양성경로는 합성 repo로 검증. 실제 병합 candidate 생성은 사람 단계.
3. **change-intent·debt-threshold 부재**(om-temp-1.13.1): 실제 postmerge 시 T41/T43가 fail-closed로 `incomplete` 처리됨. 운영 전 두 입력 제공 필요.

## 7. 검토 방법
```bash
cd .../review-openmetadata-test-phase-bundling/harness
PYTHONPATH=$(pwd) <mainvenv>/python -m pytest tests/test_phase_*.py -q   # 125 passed
```
변경 파일: `acgh/{candidate_select,preflight,phase,rollup}.py`, `tests/test_phase_*.py`(11) — 전부 신규.

## 8. 상태
- 로컬 커밋 `446b5a0e53`(L2~L8) + `ae1bdbce4b`(L1). **푸시 안 함.**
- 검토 후 지시 주시면: 추가 수정 / P1 보강(C106·C112) / push / premerge-check·postmerge-check를 `om_workflow.py` 서브커맨드로 노출 중 선택 진행.
