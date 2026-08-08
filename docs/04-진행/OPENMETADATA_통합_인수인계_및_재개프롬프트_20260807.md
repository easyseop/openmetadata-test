# OpenMetadata 업그레이드 예행연습·Phase 번들링 통합 인수인계

> 작성일: 2026-08-07 PDT
>
> 용도: 다른 컴퓨터와 새 AI 세션에서 현재 작업을 안전하게 이어받기 위한 단일 문서
>
> 원칙: 예행연습 진행과 Phase 번들링 개발은 서로 독립된 branch에서 수행한다.

## 1. 작업 목적

현재 작업은 다음 두 흐름으로 나뉜다.

1. **OpenMetadata 1.13.1→1.13.2 예행연습**

   공식 OpenMetadata 1.13.1에 BANK-OM-001~007 커스터마이징을 적용한 기준선을
   등록하고 검사한 뒤, 공식 1.13.2로 안전하게 업그레이드하는 절차를 검증한다.
2. **Phase 번들링 개발**

   여러 검사 명령을 phase 단위로 묶고, 입력 확인·검사·결과 요약·증거 저장·승인
   결속을 일관된 명령으로 제공한다.

두 작업을 같은 branch에서 진행하지 않는다. Phase 번들링 보완이 진행 중이어도 기존
가이드의 개별 명령을 이용한 예행연습 확인은 계속할 수 있다. 다만 Phase 번들러를
운영 승인 도구로 사용하는 것은 P0 보완과 독립 재검토가 끝난 뒤에만 가능하다.

## 2. 저장소와 원격 branch

| 구분 | 저장소 | 원격 branch | 2026-08-07 확인 SHA |
|---|---|---|---|
| 예행연습·검사기 | `easyseop/openmetadata-test` | `codex/om-1.13.1-rehearsal-baseline-20260806` | `b2dfb01a5ae1079085e25d978c5909e8305d7d6a` |
| Phase 번들링 | `easyseop/openmetadata-test` | `codex/phase-bundling` | `8acf6f2e4f14b32da469201d42d90ce976971c1f` |
| 1.13.1 제품 코드 | `easyseop/OpenMetadata` | `codex/om-1.13.1-runtime-ready` | `8ac18ad053d9274774e274ba17b35911ac0b9dcb` |
| 공식 1.13.2 | OpenMetadata 코드 저장소 | tag `1.13.2-release` | `2763bf97ce265662793a1a38d353147cc6d6c2e3` |

위 SHA는 작성 당시 확인값이다. 작업을 재개할 때는 `git fetch` 후 원격 최신 SHA를
다시 확인한다. SHA가 달라졌다는 이유만으로 오류라고 단정하지 않고, 새 commit의 목적과
인수인계 갱신 여부를 먼저 확인한다.

## 3. 현재 완료 상태

### 3.1 1.13.1 기준선과 Runtime Contract

- BANK-OM-001~007을 공식 Git 이력 위에 ID별 commit으로 재구성했다.
- 최종 1.13.1 custom 기준 commit은 `8ac18ad053d9274774e274ba17b35911ac0b9dcb`다.
- 최초 등록 `plan → 사람 승인 → apply`를 완료했다.
- 등록자료 검사 5개와 소스 검사 9개가 모두 통과했다.
- Runtime Contract는 API 6개와 브라우저 3개, 총 9/9가 통과했다.
- 등록 범위는 변경 경로 111개, 제외 경로 2개, 공용 경로 37개,
  공용 경로·BANK-OM ID 조합 114개, assertion 790개다.
- Oracle·Tibero·Sybase·DB2·PostgreSQL 목 메타데이터와 데이터 품질 결과를 API로
  생성하는 도구가 준비돼 있다.
- 다른 컴퓨터용 공개 Docker image와 Docker 전용 예행연습 묶음이 준비돼 있다.

주요 증거 경로:

```text
evidence/om-1.13.1-runtime-ready-20260807-01/
evidence/om-1.13.1-runtime-ready-validation-20260807-01/
evidence/om-1.13.1-runtime-20260807-01/
evidence/mock-database-metadata-20260807-01/result.json
```

### 3.2 공식 1.13.2 준비와 병합 전 검사

- 공식 tag `1.13.2-release` commit은 `2763bf97...`로 확인했다.
- T42 사전 영향검사에서 공식 변경 1,702개 경로와 BANK-OM 감시 경로가 겹치는
  ID 6개를 확인했다. BANK-OM-005는 영향이 없었다.
- T93에서 BANK-OM-004의 `EntityUtils.tsx` 감시경로 재매핑 필요 신호가 있었다.
- T41은 `change-intent`, T43은 승인된 `conflict-rate` 입력이 없어 미완료로 남았다.
- 1.13.2 vendor merge, 충돌 해결, custom 코드 수정과 release 생성은 아직 승인 없이
  실행하지 않는다.

병합 전 검사 결과는 재개 환경에서 현재 candidate를 기준으로 다시 확인한다. 과거
candidate로 생성된 T93·T41·watch-suggest·T43 결과를 현재 승인 결과로 재사용하지 않는다.

### 3.3 Phase 번들링 구현과 Codex 검토

Claude가 L1~L8 라이브러리와 테스트를 구현했다. 작성된 phase 테스트 125개와 기존
핵심 회귀 테스트는 통과했다. Codex 독립 검토 결과, 현재 구현은 **검토용 WIP**이며
운영 완료로 승인할 수 없다.

남은 P0:

1. `om_workflow.py`에 실제 phase 명령과 end-to-end orchestration이 없다.
2. 승인 digest가 gate의 사유·증거·상세 결과를 보호하지 않는다.
3. `GateSpec.timeout`이 선언만 있고 실제 실행시간 제한으로 동작하지 않는다.
4. `run_gates()`가 premerge·postmerge phase catalog를 강제하지 않는다.
5. 승인된 active candidate 출처가 0개여도 consistency가 통과한다.
6. debt threshold가 없을 때 fail-closed하지 않고 기본값으로 실행한다.

남은 P1:

1. phase 승인자의 이름·승인 시각·승인 근거를 검증하지 않는다.
2. `GateExecution.detail`이 시스템 JSON에서 빠져 상세 결과가 유실된다.

검토 정본:

```text
docs/04-진행/PHASE_BUNDLING_CODEX_구현검토_20260807.md
```

## 4. 다른 컴퓨터의 공통 준비

각 작업은 별도 폴더 또는 `git worktree`로 분리한다. 기존 변경사항이 있는 폴더에서
branch를 강제로 전환하지 않는다.

### 4.1 처음 clone하는 경우

```bash
mkdir -p "$HOME/om-work"

git clone --branch codex/om-1.13.1-rehearsal-baseline-20260806 \
  https://github.com/easyseop/openmetadata-test.git \
  "$HOME/om-work/openmetadata-test-rehearsal"

git clone --branch codex/phase-bundling \
  https://github.com/easyseop/openmetadata-test.git \
  "$HOME/om-work/openmetadata-test-phase-bundling"

git clone https://github.com/easyseop/OpenMetadata.git \
  "$HOME/om-work/OpenMetadata"
```

### 4.2 이미 clone한 경우

각 저장소에서 먼저 다음을 확인한다.

```bash
git status --short --branch
git remote -v
git fetch --all --tags --prune
```

`git status --short`에 출력이 있으면 사용자 변경일 수 있다. 삭제, `reset --hard`,
`checkout --`, `clean`을 실행하지 말고 변경 파일과 현재 branch를 먼저 보고한다.

### 4.3 기존 검사기 clone에서 worktree를 추가하는 경우

처음 clone할 때는 4.1처럼 저장소를 두 폴더로 나누는 방법이 가장 단순하다. 기존
검사기 clone을 재사용해야 할 때만 다음처럼 두 worktree를 추가한다.

```bash
cd "$HOME/om-work/openmetadata-test"

git worktree add "$HOME/om-work/openmetadata-test-rehearsal" \
  origin/codex/om-1.13.1-rehearsal-baseline-20260806

git worktree add "$HOME/om-work/openmetadata-test-phase-bundling" \
  origin/codex/phase-bundling
```

이 명령으로 만든 worktree는 원격 commit을 확인하는 읽기 전용 시작점이다. 코드를
수정하기 전에 각 worktree에서 해당 원격 branch를 추적하는 로컬 branch가 이미 있는지
확인한다. branch 이름이나 worktree가 이미 사용 중이면 새로 만들지 말고
`git worktree list`와 `git branch -vv` 결과를 먼저 보고한다.

## 5. Codex 작업 A — 예행연습 이어받기 프롬프트

다른 컴퓨터의 새 Codex 세션에 아래 내용을 그대로 전달한다.

```text
easyseop/openmetadata-test와 easyseop/OpenMetadata를 사용해 OpenMetadata
1.13.1→1.13.2 예행연습을 이어서 진행해 주세요.

작업 원칙:
1. 먼저 각 저장소에서 git status --short --branch, remote, HEAD를 확인하세요.
2. 사용자 변경사항이 있으면 삭제·reset·checkout하지 말고 먼저 보고하세요.
3. 검사기 branch는 origin/codex/om-1.13.1-rehearsal-baseline-20260806,
   제품 코드 branch는 origin/codex/om-1.13.1-runtime-ready를 확인하세요.
4. docs/04-진행/OPENMETADATA_통합_인수인계_및_재개프롬프트_20260807.md를
   처음부터 끝까지 읽으세요.
5. docs/04-진행/CODEX_CURRENT_HANDOFF.md와
   docs/00-사용가이드/예행연습-1.13.1-1.13.2/의 전체목차를 확인하세요.
6. 현재 원격 SHA, 완료 evidence, 5-4 Runtime Contract 9/9 결과, 공식
   1.13.2-release commit을 실제 Git과 파일로 재검증하세요.
7. 과거 SHA가 현재와 다르면 즉시 실패로 단정하지 말고 branch 이동 이력과 tree SHA,
   활성 승인 기준을 확인하세요.
8. 현재까지 완료된 단계와 다음 미완료 단계를 표로 먼저 보고하세요.
9. 우선 읽기 전용 확인만 수행하고 다음 실행 단계가 확정되면 멈춰 보고하세요.
10. 사용자 승인 없이 vendor merge, 충돌 해결, custom branch 수정, commit, tag,
    release branch 생성은 하지 마세요.
11. 네트워크 문제로 tag·commit·blob·container image를 검증할 수 없으면 즉시
    원인, 영향, 마지막 정상 단계를 알려주세요.
12. 작업 종료 전에 통합 인수인계와 CODEX_CURRENT_HANDOFF.md에 branch, HEAD,
    실행 결과, evidence 경로와 다음 행동을 갱신하세요.
```

Codex가 처음 보고해야 할 항목:

- 실제 검사기·제품 코드 경로
- 각 저장소의 branch, HEAD, 원격과의 차이
- 사용자 미반영 변경 유무
- 5-4까지의 완료 증거 유무
- 공식 1.13.2 commit 확인 결과
- 다음으로 실행할 정확한 가이드 단계
- 실행 전에 필요한 사람 결정

## 6. Claude 작업 — Phase 번들링 부족 개발 요청 프롬프트

Phase 번들링의 P0/P1 보완은 Claude에게 아래 내용으로 요청한다. Claude는 예행연습
branch나 제품 코드를 수정하지 않고 `codex/phase-bundling`에서만 작업한다.

```text
easyseop/openmetadata-test의 origin/codex/phase-bundling에서 Phase 번들링 구현을
보완해 주세요. 현재 구현은 완료본이 아니라 Codex 검토용 WIP입니다.

먼저 다음 문서를 전부 읽으세요.
- docs/04-진행/OPENMETADATA_통합_인수인계_및_재개프롬프트_20260807.md
- docs/04-진행/PHASE_BUNDLING_CODEX_구현검토_20260807.md
- docs/04-진행/PHASE_BUNDLING_진척_인수인계_20260807.md
- docs/04-진행/PHASE_BUNDLING_개발계획_20260807.md
- docs/04-진행/PHASE_BUNDLING_개발설계_수정보완_20260807.md
- docs/04-진행/PHASE_BUNDLING_반례테스트케이스_20260807.md

작업 규칙:
1. 현재 branch, HEAD, 원격 차이와 dirty 파일을 먼저 보고하세요.
2. 예행연습 branch, OpenMetadata 제품 코드, 기존 evidence, vendor merge를 수정하지 마세요.
3. Codex 검토의 P0 6건을 각각 실제 코드에서 재현하고, 재현 결과·수정 대상·추가할
   실패 테스트를 표로 먼저 보고하세요.
4. P0를 한 건씩 수정하세요. 각 수정 전에는 실패하는 반례 테스트를 먼저 추가하고,
   수정 후 해당 테스트와 전체 회귀 테스트를 실행하세요.
5. P0가 끝난 뒤 P1 2건도 같은 방식으로 보완하세요.
6. 기존 gate 판정 로직을 다시 구현하지 말고 기존 acgh 함수와 CandidateLock을
   재사용하세요.
7. verdict 4종(pass/approval/block/analysis_error)을 유지하세요. 입력 누락은
   execution_status 또는 phase_status로 구분하세요.
8. om_workflow.py에서 실제 사용자가 실행할 수 있는 phase 명령을 제공하고,
   candidate 선택→preflight→gate 실행→집계→3단 출력→evidence 저장→승인 결속을
   end-to-end 테스트하세요.
9. 관리자 요약, 실무자 상세, 시스템 JSON은 동일한 검사 결과와 수치를 사용해야 합니다.
10. timeout은 예외를 수동 발생시키는 테스트가 아니라 실제로 오래 실행되는 gate를
    중단하는 장애 주입 테스트로 검증하세요.
11. result digest가 승인 판단에 사용되는 사유·증거·상세·catalog/version을 보호하는지
    변조 테스트로 검증하세요.
12. 구현 완료를 선언하기 전에 P0/P1별 수정 commit, 테스트 결과, 미구현 항목과
    운영 STOP 지점을 문서로 남기세요.
13. 완료 후 바로 병합하거나 운영 승인하지 말고 Codex 독립 재검토를 요청하세요.
```

Claude의 완료 조건:

- P0 6건과 P1 2건 각각에 실패 전·통과 후 증거가 있다.
- 기존 gate parity와 기존 전체 테스트가 유지된다.
- 한 명령으로 premerge 또는 postmerge phase를 실행할 수 있다.
- 입력 누락, 프로그램 오류, approval, block, pass가 서로 구분된다.
- 결과 JSON과 사람이 읽는 요약의 수치가 일치한다.
- 변경 commit과 인수인계가 원격 `codex/phase-bundling`에 반영된다.

## 7. Codex 작업 B — Claude 수정본 독립 재검토 프롬프트

Claude가 보완 개발을 끝낸 뒤 다른 Codex 세션에 다음 내용을 전달한다.

```text
Claude가 수정한 easyseop/openmetadata-test의 codex/phase-bundling을 독립적으로
재검토해 주세요.

1. 작업 트리와 원격 최신 commit을 확인하고 검토 commit을 고정하세요.
2. OPENMETADATA_통합_인수인계_및_재개프롬프트_20260807.md와
   PHASE_BUNDLING_CODEX_구현검토_20260807.md를 전부 읽으세요.
3. 기존 P0 6건과 P1 2건을 원 보고서가 아니라 실제 코드와 반례로 다시 검증하세요.
4. Claude가 작성한 테스트만 실행하지 말고 timeout, 결과 변조, 빈 active source,
   잘못된 phase gate, threshold 누락, 빈 승인서를 독립적으로 주입하세요.
5. om_workflow.py의 실제 CLI를 깨끗한 임시 evidence 폴더에서 end-to-end 실행하세요.
6. pass 수만 보고 승인하지 말고 skip·xfail·수동 예외·mock으로 통과를 위장하지
   않았는지 확인하세요.
7. 관리자 요약, 실무자 상세, 시스템 JSON의 수치와 verdict를 대조하세요.
8. 운영 승인 가능, 추가 수정 필요, 또는 block 중 하나로 결론을 명시하세요.
9. 검토 중에는 예행연습 branch, 제품 코드와 vendor merge를 수정하지 마세요.
10. 검토 결과와 다음 행동을 통합 인수인계에 갱신하세요.
```

## 8. 사람 승인과 STOP 지점

다음 작업은 AI가 임의로 결정하지 않는다.

| 시점 | 사람 결정 | 결정 전 상태 |
|---|---|---|
| 활성 candidate 변경 | 어떤 승인된 candidate lock을 이번 실행 기준으로 사용할지 | 검사 시작 중단 |
| T41 입력 | `change-intent`의 허용 범위와 근거 | T41 미실행, phase 완료 금지 |
| T43 입력 | 승인된 conflict-rate·debt threshold | T43 미실행, phase 완료 금지 |
| vendor merge | 공식 1.13.2를 어느 custom branch에 병합할지 | 제품 코드 무수정 |
| 충돌 해결 | 어떤 BANK-OM 동작과 공식 변경을 함께 보존할지 | 충돌 상태에서 중단·보고 |
| Phase 번들러 운영 승인 | P0/P1 재검토 결과를 승인할지 | WIP branch 유지 |
| release/tag | 검증한 정확한 commit을 release로 고정할지 | tag·release 생성 금지 |

## 9. 공통 결과 판정

| 결과 | 의미 | 다음 행동 |
|---|---|---|
| `pass` | 해당 검사의 자동 기준을 모두 충족 | 다음 단계 진행 가능 |
| `approval` | 자동 차단은 아니지만 사람 검토가 필요 | 검토표와 evidence 확인 후 결정 |
| `block` | 정책 또는 코드 정합성 문제로 진행 금지 | 원인을 수정하고 같은 입력으로 재검사 |
| `analysis_error` | 입력 누락, 실행 실패 또는 결과 해석 불가 | pass로 바꾸지 말고 입력·환경·프로그램 오류 구분 |

필수 gate가 실행되지 않았다면 일부 gate가 `pass`여도 phase 전체를 완료로 승인하지
않는다.

## 10. 네트워크 문제 보고 규칙

다음 상황은 즉시 사용자에게 알린다.

- 원격 branch·tag·commit을 fetch하지 못해 검사 기준을 고정할 수 없음
- partial clone의 blob을 받지 못해 diff 또는 build를 수행할 수 없음
- container image를 받지 못해 Runtime Contract 환경을 만들 수 없음
- 의존성 다운로드가 반복 실패해 build 결과가 생성되지 않음

보고 내용:

```text
실패한 명령:
오류 원문:
마지막 정상 단계:
영향받는 검사:
로컬에 이미 확보된 자료:
안전한 재시도 명령:
네트워크 복구 전 금지할 작업:
```

네트워크가 느리기만 하고 로컬 자료로 정확한 검사를 계속할 수 있으면 진행할 수 있다.
공식 commit, image 또는 의존성이 없어 결과의 신뢰성이 달라지면 즉시 중단한다.

## 11. 세션 종료 전 인수인계 갱신

각 세션은 종료 전에 이 문서 또는 `CODEX_CURRENT_HANDOFF.md`에 다음을 기록한다.

1. 저장소와 branch
2. 작업 시작 SHA와 종료 SHA
3. 수정한 파일과 commit
4. 실행한 명령과 검사 결과
5. 생성한 evidence 경로
6. 사람 승인 또는 미결정 항목
7. 네트워크·환경 문제
8. 다음 세션이 처음 실행할 명령
9. 원격 push 여부와 원격 SHA

비밀번호, API token, 브라우저 session, `/private/tmp`의 인증 환경 파일은 문서나 Git에
기록하지 않는다.

## 12. 관련 상세 문서

- `docs/04-진행/CODEX_CURRENT_HANDOFF.md`
- `docs/04-진행/PHASE_BUNDLING_진척_인수인계_20260807.md`
- `docs/04-진행/PHASE_BUNDLING_CODEX_구현검토_20260807.md`
- `docs/04-진행/PHASE_BUNDLING_구현완료_검토요청_20260807.md`
- `docs/04-진행/PHASE_BUNDLING_개발계획_20260807.md`
- `docs/04-진행/PHASE_BUNDLING_개발설계_수정보완_20260807.md`
- `docs/04-진행/PHASE_BUNDLING_반례테스트케이스_20260807.md`
- `docs/00-사용가이드/예행연습-1.13.1-1.13.2/OM_TEMP_1.13.1_1.13.2_예행연습_전체목차.html`

이 문서는 재개 순서와 역할 분담을 한 번에 확인하는 통합 진입점이다. 최신 세부 상태는
`CODEX_CURRENT_HANDOFF.md`, 구현 근거와 모든 반례 목록은 관련 상세 문서를 참조한다.
