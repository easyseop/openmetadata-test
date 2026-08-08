# OpenMetadata Phase 번들링 외부 모델 설계 검토 요청서

> 작성일: 2026-08-08 KST
> 검토 방식: 읽기 전용. 코드·문서·branch·결과를 수정하거나 push하지 않는다.
> 검토 대상: Claude의 초기 Phase 번들링 구현과 Codex의 안전성 보완
> 최종 질문: 현재 설계가 잘 되었는지, 운영 적용 전 무엇을 반드시 고쳐야 하는지 근거와 함께 판정해 달라.

## 1. 검토자가 먼저 알아야 할 결론

이 작업은 OpenMetadata 제품 기능을 새로 만드는 개발이 아니다. 기존
개별 검사기를 업그레이드 단계별로 묶고, 어느 repository의 어느
commit을 어떤 정책으로 검사했는지 결속하는 orchestration 계층을 만든
작업이다.

현재 상태는 다음과 같다.

- Phase 번들링 코드 구현: 완료
- 독립 검토에서 발견한 안전성 문제 보완: 완료
- synthetic Git repository E2E: 완료
- 실제 OpenMetadata 1.13.2 vendor-merge 후보 postmerge: 미실행
- 실제 conflict-rate·change-intent·조직 승인·운영 배포: 미완료

따라서 구현과 합성 E2E 완료를 실제 1.13.2 업그레이드 또는 운영 배포
완료로 판정하면 안 된다.

## 2. repository별 역할

| repository | 저장하는 내용 | 현재 검토 범위 |
|---|---|---|
| `easyseop/OpenMetadata` | 실제 OpenMetadata 제품 코드와 BANK-OM 커스터마이징 commit | 1.13.1 기준 candidate와 향후 1.13.2 vendor merge 대상 |
| `easyseop/openmetadata-test` | Manifest·Registry·Contract·정책·검사기·결과·문서 | 이 요청서의 주 검토 repository |

검사기 repository:

- URL: `https://github.com/easyseop/openmetadata-test`
- 현재 branch: `codex/phase-bundling-safety-fix-20260808`
- 이 문서 작성 직전 HEAD: `295307d6568b5102c065fc5a093dfa7fa1b46ba5`
- Phase 실제 보완 구현 commit: `7a963853c7554be60db64cd1ba1fc4ce1bad26ef`

`7a96385...` 이후 commit은 Phase 실행 코드가 아닌 인수인계·사용자 문서
정리가 중심이다. 현재 HEAD에서는 사용자가 폐기를 요청한 고객사·솔루션
제공업체 관점의 독립 HTML·Markdown 가이드도 삭제된 상태다. 그 가이드는
설계 검토 대상에서 제외한다.

## 3. OpenMetadata 제품 기준과 목표 버전

### 3.1 현재 1.13.1 커스터마이징 기준

| 항목 | 값 |
|---|---|
| 공식 OpenMetadata 버전 | `1.13.1` |
| 공식 1.13.1 commit | `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9` |
| BANK-OM 커스터마이징 기준 branch | `codex/om-1.13.1-runtime-ready` |
| 최종 1.13.1 candidate | `8ac18ad053d9274774e274ba17b35911ac0b9dcb` |
| 관리 기능 | `BANK-OM-001`~`BANK-OM-007` |

1.13.1 기준선에서 확인한 내용:

- 등록 변경 경로 111개
- 제외 경로 2개
- 공용 경로 37개
- 공용 경로·BANK-OM ID 조합 114개
- 공용 코드 assertion 790개
- 등록자료 검사 5개 통과
- 소스 검사 9개 통과
- Runtime Contract 9개 통과: API 6개, 브라우저 3개

### 3.2 업그레이드 목표

| 항목 | 값·상태 |
|---|---|
| 목표 OpenMetadata 버전 | `1.13.2` |
| 공식 tag | `1.13.2-release` |
| 알려진 공식 commit | `2763bf97...`; 실행 전 repository에서 전체 SHA 재확인 필요 |
| 병합 전 영향 검사 | 실행 완료 |
| 실제 vendor-merge candidate | 미생성 |
| 실제 postmerge Phase | 미실행 |

병합 전 영향 검사에서 공식 1.13.2 변경 1,702개 경로와 BANK-OM
감시 경로를 비교했다. BANK-OM 6개에 영향 신호가 있었고 BANK-OM-005는
직접 영향이 없었다. BANK-OM-004의 `EntityUtils.tsx`는 감시 경로 재매핑
검토 신호가 있었다.

## 4. Phase 번들링을 만든 이유

기존에는 `plan`, `approval-template`, `apply`, `validate`, `source`, `watch`,
`risk`, `runtime`, `patch-kill`, `typecheck` 등을 개별로 실행했다.

개별 검사는 여전히 필요하지만 다음 운영 위험이 있었다.

1. 어느 검사를 어느 순서로 실행할지 담당자가 직접 조합한다.
2. 결과 JSON이 여러 폴더에 나뉘어 다른 candidate 결과가 섞일 수 있다.
3. premerge 결과와 postmerge 결과를 잘못 재사용할 수 있다.
4. 검사 후 commit이 바뀌었는데 기존 승인을 재사용할 수 있다.
5. 필수 입력 누락과 프로그램 실행 오류의 구분이 불분명할 수 있다.
6. 관리자·실무자·자동화가 각자 원본 JSON을 다시 해석해야 한다.
7. 결과와 승인서가 같은 candidate·phase·digest를 가리키는지 별도로 확인해야 한다.

Phase 번들링은 개별 검사기를 재구현하지 않고 기존 검사기를 재사용하며,
단계 순서·candidate 고정·결과 집계·증거·승인 결속을 추가한다.

## 5. commit 이력과 비교 기준

> 주의: commit 시각은 서로 다른 컴퓨터·시간대 기록이므로 순서가 어색할 수 있다. 검토는 표시 시각이 아니라 Git 부모·자식 계보와 SHA를 기준으로 한다.

| 단계 | commit | Git에 기록된 시각 | 내용 |
|---|---|---|---|
| 설계·반례 기준 | `7f7bf1b3835e881e2bcf7985798c9d1d8e929ea2` | `2026-08-07T19:48:52-07:00` | 개발설계 보완과 C1~C114 반례 테스트 기준 |
| Claude L1 | `ae1bdbce4b6df16492e8e039b467d780aeda91a3` | `2026-08-07T19:54:35-07:00` | 명시적 active candidate 선택과 test |
| Claude L2~L8 | `446b5a0e53546cf5df32d5a4a0b537487be59e9a` | `2026-08-07T20:38:57-07:00` | preflight, gate 실행, 집계, catalog, rollup, evidence, test |
| Claude 구현 검토 기준 | `dbf169bfd4d1a721dd196a643f2080b84b013b43` | `2026-08-07T21:06:11-07:00` | Claude 코드와 검토·인수인계 문서를 외부 검토용으로 분리한 head |
| Codex 안전 보완 | `7a963853c7554be60db64cd1ba1fc4ce1bad26ef` | `2026-08-08T00:54:49+09:00` | P0·P1 보완, 실제 CLI orchestration과 synthetic E2E |
| Codex 원격 인수인계 | `10026080924d8ca6a25f3b326ed8349f505ba237` | `2026-08-08T00:56:52+09:00` | 구현 SHA·검증·다음 실행 절차 기록 |
| 요청서 작성 직전 branch head | `295307d6568b5102c065fc5a093dfa7fa1b46ba5` | `2026-08-08T02:23:26+09:00` | 폐기 가이드 삭제·현행 인수인계 정리; Phase 코드 무변경 |

Claude 구현 핵심:

- `ae1bdbc...`: `harness/acgh/candidate_select.py`, `harness/tests/test_phase_candidate_select.py`
- `446b5a0...`: `harness/acgh/phase.py`, `harness/acgh/preflight.py`,
  `harness/acgh/rollup.py`, Phase test 10개 파일
- Claude 구현 commit에 기록된 당시 결과: 125 tests passed, 0 skipped

Codex 보완은 다음 비교로 확인한다.

```bash
git diff --stat \
  dbf169bfd4d1a721dd196a643f2080b84b013b43..\
  7a963853c7554be60db64cd1ba1fc4ce1bad26ef
```

주요 구현 diff를 파일별로 보려면:

```bash
git diff \
  dbf169bfd4d1a721dd196a643f2080b84b013b43..\
  7a963853c7554be60db64cd1ba1fc4ce1bad26ef \
  -- harness/acgh harness/om_workflow.py harness/run_phase_bundle.py harness/tests
```

## 6. Claude 초기 구현

Claude 구현은 다음 구조를 만들었다.

```text
candidate 선택
→ preflight
→ phase별 gate catalog 구성
→ gate 실행
→ verdict 집계
→ manager / practitioner / system 결과
→ evidence digest
→ 승인 결속
```

의도는 적절했지만 Codex 독립 검토에서 다음 주요 문제를 확인했다.

| 영역 | 초기 구현 문제 |
|---|---|
| timeout | 설정값이 실제 장시간 gate process를 종료하지 못함 |
| phase 경계 | `run_gates()`에 다른 phase gate를 전달하거나 같은 gate를 중복 실행할 수 있음 |
| 빈 입력 | active source가 0개인 상태가 차단되지 않는 경로 |
| digest 범위 | verdict 외 reasons·evidence·detail 변경을 완전히 보호하지 못함 |
| 표시 일치 | system JSON 세부 판단이 canonical payload와 달라도 감지하지 못할 수 있음 |
| debt 정책 | 임계값 누락 시 기본값으로 진행하는 fail-open 가능성 |
| CLI 연결 | 모듈은 있지만 사용자가 실제 premerge·postmerge를 한 흐름으로 실행할 공개 CLI가 완성되지 않음 |
| 승인 | 승인자·시각·구체적 사유·단계·결과 digest 결속 검증 부족 |
| 오류 보존 | gate detail 유실 가능성과 사용자 중단을 일반 분석 오류로 취급할 가능성 |

정확한 독립 검토 문서:

- `docs/04-진행/PHASE_BUNDLING_CODEX_구현검토_20260807.md`

## 7. Codex 보완 구현

Codex는 `7a963853...`에서 다음을 반영했다.

1. POSIX wall-clock timeout을 실제 process 실행에 강제했다.
2. premerge·postmerge gate catalog와 gate ID 중복 금지를 `run_gates()`에서 강제했다.
3. active source가 0개이면 preflight를 blocking `missing`으로 종료한다.
4. canonical digest에 verdict·reasons·evidence·detail을 포함했다.
5. system JSON의 판단 필드와 canonical payload 일치를 검증한다.
6. debt 임계값 누락을 기본값으로 대체하지 않고 fail-closed한다.
7. 승인자, timezone이 포함된 RFC3339 `approved_at`, 구체적 `rationale`를 공통 검증한다.
8. `GateExecution.detail`을 최종 결과에 보존한다.
9. `KeyboardInterrupt`를 일반 `analysis_error`로 삼키지 않는다.
10. 다음 공개 CLI를 `harness/om_workflow.py`에 연결했다.
11. postmerge에 기존 registration validator·source runner와 선택적 Runtime Contract를 연결했다.
12. synthetic Git repository E2E에서 candidate 선택, preflight, gate 실행,
    3단 결과, digest 재검증을 확인했다.

추가·변경된 핵심 파일:

| 파일 | 역할 |
|---|---|
| `harness/acgh/candidate_select.py` | 승인된 active Candidate lock 선택·digest 결속 |
| `harness/acgh/preflight.py` | phase 실행 전 Git object·정책·입력 누락 일괄 검사 |
| `harness/acgh/phase.py` | gate catalog, timeout, 실행 상태, 집계, canonical result |
| `harness/acgh/rollup.py` | manager·practitioner·system 3단 출력 |
| `harness/acgh/approval.py` | 승인자·RFC3339 시각·사유 공통 검증 |
| `harness/run_phase_bundle.py` | candidate·official·preflight·premerge·postmerge·status 실제 orchestration |
| `harness/om_workflow.py` | 사용자가 실행할 6개 Phase subcommand 노출 |
| `harness/registrations/kb-openmetadata/run_source_candidate_gates.py` | 기존 source runner 종료코드를 4상태 집계와 맞춤 |
| `harness/tests/test_phase_cli.py` | 공개 CLI·E2E·candidate 모순·결과 출력 회귀 테스트 |

## 8. 현재 공개 CLI의 기능

| 명령 | 역할 | 사용자가 생략할 수 있는 값 |
|---|---|---|
| `candidate-select` | 등록 묶음의 승인된 active Candidate lock 선택 | 기본 결과 경로 |
| `prep-official` | 공식 tag commit과 동일한 로컬 official branch 준비 | 기본 결과 경로 |
| `phase-preflight` | phase별 commit·정책·후보·입력 사전 검사 | 기본 결과 경로 |
| `premerge-check` | 새 공식 버전 병합 전 영향 검사 | `run-id`, 기본 결과 경로 |
| `postmerge-check` | vendor-merge 후보의 등록·소스·위험·선택 Runtime 검사 | `run-id`, 기본 결과 경로; artifact digest는 Runtime을 포함할 때만 |
| `phase-status` | 저장된 Phase result digest와 판정 필드 재검증 | 없음; `--result`는 필수 |

`run-id`를 생략하면 phase 이름과 시각으로 생성한다. 그러나 BANK-OM ID,
Candidate lock, 실제 Git commit SHA, 실제 conflict-rate, change-intent, 승인자,
승인 사유, 운영 입력은 자동 생성하지 않는다.

한 phase는 같은 canonical result에서 다음 세 파일을 생성한다.

- `manager-summary.json`: 계속 가능 여부와 필요 승인
- `practitioner-detail.json`: gate별 입력·판정·근거·오류·detail
- `result.json`: canonical payload·result digest·자동화 입력

## 9. 후속 commit과 사람 판단 경계

기존 기능의 버그 수정·누락 보완·업그레이드 적응은 같은 BANK-OM ID의
후속 commit으로 관리할 수 있다. 독립 기능은 새 ID 발급을 검토한다.

자동으로 확인하는 내용:

- commit의 `Customization-ID`
- 같은 ID의 복수 commit 허용 여부
- commit 순서와 의존관계
- ID별 전체 `changed_paths`
- 필수 경로·Contract·test 연결
- 최종 candidate에 커스터마이징 코드가 남았는지

사람이 반드시 결정하는 내용:

- 새 BANK-OM ID 발급 또는 기존 ID 유지
- 새 경로가 `required_changed_paths`인지
- 직접 수정하지 않은 간접 `upgrade_watch` 경로인지
- 공용 파일에서 어느 코드가 어느 BANK-OM 기능을 증명하는지
- Contract의 정상 업무 동작과 필수 test
- Git 충돌 해결안
- `change-intent.yaml`
- 기능 담당 조직·승인자·승인 사유
- 운영 승격·배포 결정

`changed_paths`는 Git이 찾은 해당 ID의 전체 변경 파일이다.
`required_changed_paths`는 그중 빠지면 기능 소실이 확실한 핵심 파일이다.
자동화는 새 경로 후보를 제안할 수 있지만 어느 경로가 업무적으로
필수인지는 임의로 결정하지 않는다.

검사 후 commit이 하나라도 추가되면 기존 결과·승인을 재사용하지 않는다.
새 Candidate lock을 만들고 해당 phase를 전체 재실행해야 한다.

## 10. 주요 코드와 문서를 읽는 순서

외부 검토자는 다음 순서로 읽는다.

1. `docs/04-진행/PHASE_BUNDLING_개발설계_수정보완_20260807.md`
   - phase 분리, candidate 선택, 오류, 승인 결속 설계
2. `docs/04-진행/PHASE_BUNDLING_반례테스트케이스_20260807.md`
   - C1~C114 반례와 예상 판정
3. `docs/04-진행/PHASE_BUNDLING_CODEX_구현검토_20260807.md`
   - Claude 초기 구현의 독립 검토 결과
4. `docs/04-진행/PHASE_BUNDLING_진척_인수인계_20260807.md`
   - 13절의 Codex 보완, 검증, 미실행 범위, 다음 명령
5. `docs/04-진행/CODEX_CURRENT_HANDOFF.md`
   - 현재 branch·SHA·외부 입력 대기 상태
6. `harness/acgh/candidate_select.py`
7. `harness/acgh/preflight.py`
8. `harness/acgh/phase.py`
9. `harness/acgh/rollup.py`
10. `harness/acgh/approval.py`
11. `harness/run_phase_bundle.py`
12. `harness/om_workflow.py`
13. `harness/tests/test_phase_candidate_select.py`
14. `harness/tests/test_phase_preflight.py`
15. `harness/tests/test_phase_catalog.py`
16. `harness/tests/test_phase_exec.py`
17. `harness/tests/test_phase_evidence.py`
18. `harness/tests/test_phase_cli.py`

## 11. 검증 상태

Codex 보완 직후 기록:

- Phase 관련 집중 검증: `145 passed, 1 skipped`
- 전체 harness: `531 passed, 38 skipped`
- 실패: 0개

skip은 실제 제품 repository ref, API·브라우저, Docker·외부 환경 등이
필요한 항목이며 PASS에 포함하지 않았다.

최근 문서 회귀 확인에서:

- `.venv/bin/python -m pytest harness/tests/test_phase_cli.py -q`: `6 passed`

외부 검토자가 의존성이 설치된 환경을 갖고 있다면 다음을 재현한다.

```bash
.venv/bin/python -m pytest harness/tests/test_phase*.py -o addopts='' -q
```

테스트 통과 수만으로 설계를 승인하지 말고, 검증되지 않은 실제
OpenMetadata 병합·병렬 실행·오래된 증거·승인 재사용 반례를 추가로 검토한다.

## 12. 아직 실제로 완료하지 않은 범위

다음은 코드 미구현과 외부 입력·실제 실행 대기를 구분해야 한다.

- 실제 OpenMetadata 1.13.2 vendor-merge candidate
- 실제 merge 증거로 계산한 conflict-rate
- 승인된 `change-intent.yaml`
- 실제 1.13.2 candidate의 `postmerge-check`
- 실제 배포 artifact digest에 결속한 Runtime Contract
- 기능·보안·운영 담당 조직과 승인자 지정
- 운영 승격·배포

이 값들을 추측하거나 가상 산출물을 실제 증거로 표시해 PASS를 만들면 안 된다.

## 13. 외부 모델이 반드시 답할 설계 질문

다음 질문에 단순 의견이 아니라 코드·test·Git diff·문서 근거를 들어 답한다.

1. 기존 개별 검사기를 재사용하고 Phase orchestration 계층을 추가한 구조가 적절한가?
2. premerge와 postmerge의 입력·gate catalog·승인을 분리한 방식에 우회 경로가 있는가?
3. Candidate lock이 repository·commit SHA·tree·정책·결과를 충분히 결속하는가?
4. 검사 후 commit이 추가되면 이전 결과·승인 무효화가 모든 실행 경로에서 강제되는가?
5. canonical digest가 verdict·reasons·evidence·detail의 의미 변경을 모두 감지하는가?
6. `manager-summary.json`, `practitioner-detail.json`, `result.json`이 하나의 canonical result에서 생성되며 서로 다르게 표시될 가능성이 없는가?
7. 시간 기반 자동 `run-id`가 병렬 실행, 같은 시각 재실행, CI retry에서 충돌할 가능성이 있는가?
8. `--version 1.13.1`이 기준 등록 묶음을 선택하고 Candidate lock은 1.13.2 postmerge 후보를 가리키는 구조가 명확하고 안전한가? `--registration-version`과 같은 이름이 더 적절한가?
9. `required_changed_paths`를 사람이 결정할 때 핵심 파일을 실수·의도적으로 누락하는 상황을 검출할 독립 기준이 충분한가?
10. 간접 `upgrade_watch` 경로를 사람이 누락했을 때 의존성·정적 분석으로 보완할 필요가 있는가?
11. 실제 conflict-rate의 분자·분모·측정 시점·증거 형식이 명확하고 재현 가능한가?
12. `change-intent.yaml`과 민감 경로 검사 사이에 오래된 승인 재사용·candidate 바꿔치기 가능성이 있는가?
13. 승인자·시각·사유 검증이 형식 확인을 넘어 실제 승인 권한까지 검증하는가? 아니라면 어떤 IAM·GitHub·행내 승인 시스템과 결속해야 하는가?
14. artifact digest가 없을 때 Runtime Contract를 생략할 수 있는 구조가 전체 업그레이드 PASS로 오해될 위험이 있는가?
15. source-only 완료, artifact 검증 완료, 운영 승격 완료를 코드 상태 모델에서 더 강하게 분리해야 하는가?
16. 한 gate의 timeout·예외·잘못된 JSON이 다른 독립 gate 결과를 잃지 않게 하면서 전체를 fail-closed로 만드는가?
17. 후속 commit의 새 경로가 required·watch·shared definition·Contract 변경을 필요로 하는지 사람이 판단하도록 한 경계가 적절한가?
18. synthetic E2E는 통과했지만 실제 OpenMetadata repository에서만 나타날 수 있는 Git history·merge·submodule·LFS·symlink·대형 repository 문제는 무엇인가?
19. 현재 test가 놓친 fail-open, race condition, stale evidence, path traversal, symlink, 병렬 쓰기 충돌 반례를 구체적으로 제시할 수 있는가?
20. 운영 적용 전 반드시 수정할 P0·P1과 추후 개선 가능한 P2를 구분해 달라.

## 14. 외부 모델에게 요청할 답변 형식

### 14.1 전체 결론

- 설계 적합 여부
- 현재 운영 적용 가능 여부
- 가장 위험한 문제 한 문장

### 14.2 발견 사항

각 항목에 다음을 포함한다.

- 심각도: P0 / P1 / P2
- 문제 위치: 파일과 함수 또는 문서 절
- 재현 조건
- 실제 영향
- 현재 test가 발견하지 못하는 이유
- 권장 수정
- 수정 후 추가할 test

### 14.3 잘 설계된 부분

코드·test·Git diff 근거가 있는 장점만 적는다.

### 14.4 추가 반례 test

구체적 입력, 실행 순서, 예상 판정과 process exit code를 제시한다.

### 14.5 최종 권고

다음 중 하나를 선택한다.

- 승인 가능
- 조건부 승인
- 재검토 필요
- 운영 적용 불가

## 15. 검토 제약

- test pass 수만으로 승인하지 않는다.
- 실제로 실행하지 않은 1.13.2 vendor merge·postmerge·운영 배포를 완료로 간주하지 않는다.
- 사람 입력이 필요한 값을 임의로 채우는 해결책을 제안하지 않는다.
- 정책을 완화해 PASS를 만드는 방안을 제안하지 않는다.
- 승인자·owner·실제 URL·token·artifact digest를 추측하지 않는다.
- 검토 중에는 코드·문서·branch를 수정하지 않고 오직 발견 사항만 보고한다.

## 16. 다른 모델에게 전달할 짧은 지시문

아래 문장과 이 파일을 함께 전달한다.

```text
이 repository의
docs/04-진행/PHASE_BUNDLING_외부모델_설계검토_요청서_20260808.md를
먼저 끝까지 읽은 뒤, 문서에 적힌 SHA·코드·test·Git diff를 직접
대조해 읽기 전용 설계 검토를 수행해 주세요. 테스트 통과 수만으로
승인하지 말고, 아직 실제로 수행하지 않은 1.13.2 vendor merge와
postmerge를 완료로 간주하지 마세요. 코드는 수정하지 말고 P0·P1·P2
발견 사항, 반례 test, 최종 승인 권고를 근거와 함께 작성해 주세요.
```
