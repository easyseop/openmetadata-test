# 현재 작업 인수인계 — `/om-plan` 보강 E안

> 마지막 갱신: 2026-08-14 23:15 KST
> 현재 작업: Claude 최종 설계 검토를 반영한 보강 E안 구현·로컬 검증 완료
> 상태: 코드·인수인계 원격 branch 보관, Claude 구현 적대 검토 대기

## 1. 목적과 현재 위치

`/om-plan`은 LLM이 업그레이드 계획을 작성하기 전에 Git·등록자료·공식 문서에서
사실을 수집하고, 계획 작성 후 같은 사실을 재계산해 결과를 검증합니다.

기존 구현에서는 `run-request.yaml`, `input-lock.yaml`,
`discovered-facts.json`을 다른 commit 기준으로 함께 다시 작성하면 내부 파일끼리는
일관된 상태가 되어 `approval`에 도달할 수 있었습니다. Claude가 이 P1-A 공격을
실제로 재현했고, 사람이나 보호된 CI가 preflight 직후 보관한 digest를 마지막
검증에 다시 제공하는 E안을 권고했습니다.

이번 구현은 그 권고를 다음과 같이 반영했습니다.

- 사람 또는 보호된 CI가 보관한 `input_lock_digest`를 final validation의 외부
  기대값으로 요구합니다.
- upgrade에 사용한 공식 문서 목록과 byte digest를
  `official_doc_sources_digest`로 묶어 `input-lock`에 포함합니다.
- 내부 verdict `approval`은 유지하고 `/om-plan` 결과에
  `review_state: review_ready`를 별도로 표시합니다.
- 내용이 없는 proposal을 차단하고, 무변경 계획은 `no_change`와 재계산 사실
  evidence를 함께 요구합니다.

## 2. 저장소·branch·commit

| 항목 | 값 |
|---|---|
| 저장소 | `easyseop/openmetadata-test` |
| 작업 위치 | `/Users/seop/Documents/Codex/om-plan-claude-review-20260814/openmetadata-test` |
| branch | `codex/om-plan-e-hardening-20260814` |
| 검토 기준 commit | `a564d483e2c9727ffdaff6bea67662a24232bbb2` |
| 보강 E안 구현 commit | `1f02e1d3a0c77b9d62f5763835d91cbadc1d5804` |
| 구현 tree | `d5dd83ded1fd5689a8c630d99452e5f0bf836afc` |

## 3. 구현 내용

### 3.1 사람이 확인할 preflight 출력

`plan-preflight`는 다음 값을 추가로 출력합니다.

- `request_digest`: 사람이 확인할 run-request 식별값
- `intent_summary`: mode, run ID, 요청 ref와 실제로 고정된 commit SHA,
  버전, 배포 방식, 공식 문서 목록, 커스터마이징 ID, 요구사항,
  변경 경로, hop 정책, 담당자
- `intent_review_required: true`: 처음부터 다른 요청으로 시작하는 문제는 기계가
  판별할 수 없으므로 사람이 내용을 확인해야 한다는 경계
- `operator_action`: `input_lock_digest`를 LLM이 바꿀 수 없는 곳에 보관하라는 안내

### 3.2 final validation의 외부 기대값

실행 형식은 다음과 같습니다.

```bash
./.venv/bin/python harness/om_workflow.py plan-validate \
  --run-dir <RUN_DIR> \
  --expected-input-lock-digest <사람이_preflight_직후_보관한_sha256_digest>
```

`expected` 값이 누락되거나 형식이 틀리거나 저장된 input-lock과 다르면
`analysis_error`입니다. 형식이 유효한 expected와 대조 결과는 validation
attempt에 기록하고, 형식 오류는 reason에 기록합니다. 이 내부 기록은
사람이 별도로 보관한 expected를 대체하지 못합니다.

### 3.3 upgrade 공식 문서 결속

preflight가 저장한 `official-doc-sources.yaml` 전체의 canonical digest를
`input-lock.canonical_payload.official_doc_sources_digest`에 포함합니다. 마지막
검사에서는 문서 snapshot byte digest를 다시 확인하고, 문서 목록·digest에서
재계산한 input-lock이 기존 input-lock과 같은지도 확인합니다.

따라서 문서 snapshot, 문서 출처 기록, discovered facts를 함께 바꾸더라도 사람이
보관한 기존 `input_lock_digest`와 달라져 `analysis_error`가 됩니다.

### 3.4 계획 최소 기준

proposal은 다음 중 하나를 포함해야 합니다.

1. 한 개 이상의 `decisions`
2. 한 개 이상의 `findings`
3. 명시적인 `no_change`

`no_change`는 `true`, 비어 있지 않은 `rationale`,
`affected_customization_ids`, `expected` 값이 포함된
`discovered-facts.json` evidence ref가 필요합니다. `{"note": "ok"}`처럼 판단이나
근거가 없는 파일은 `block`입니다.

### 3.5 결과 표시

- 내부 verdict는 계속 `approval`입니다. 공용 `acgh.verdict` enum은 변경하지
  않았습니다.
- digest 대조까지 성공한 `/om-plan` 결과만
  `review_state: review_ready`입니다.
- `review_ready`는 구현 또는 배포 승인이 아니라 사람이 계획 내용을 검토할 준비가
  됐다는 의미입니다.
- 그 밖의 verdict는 `review_state: not_ready`입니다.

## 4. 검증 결과

사용한 Python은 기존 로컬 검사기 환경의
`/Users/seop/om-work/openmetadata-test/.venv/bin/python`입니다.

### 집중 회귀

```bash
/Users/seop/om-work/openmetadata-test/.venv/bin/python -m pytest \
  harness/tests/test_plan_workflow.py \
  harness/tests/test_om_workflow.py \
  harness/tests/test_plan_boundary.py \
  --junitxml=/private/tmp/om-plan-e-focused-tests-final2.xml -q
```

- 92 passed
- failure 0, error 0, skip 0

### 전체 harness

```bash
/Users/seop/om-work/openmetadata-test/.venv/bin/python -m pytest \
  harness/tests \
  --junitxml=/private/tmp/om-plan-e-harness-tests-final2.xml -q
```

- 511 tests
- failure 0, error 0
- 37 skipped: 이 clone에 없는 OM mirror·Runtime 등 환경 의존 항목
- JUnit 기록 시간: 133.361초

추가 확인:

```bash
git diff --check
/Users/seop/om-work/openmetadata-test/.venv/bin/python -m compileall -q \
  harness/acgh/plancore harness/om_workflow.py
```

두 명령 모두 성공했습니다.

## 5. 새로 고정한 공격·경계 테스트

1. expected digest 누락 → `analysis_error`
2. expected digest 형식 오류 → `analysis_error`
3. expected digest 불일치 → `analysis_error`
4. run-request·input-lock·facts 3파일을 다른 commit 기준으로 함께 재작성 →
   사람이 보관한 기존 digest와 달라 `analysis_error`
5. 공식 문서 snapshot·문서 출처 기록·facts를 함께 재작성 → 재계산 input-lock
   불일치로 `analysis_error`
6. branch가 이동해도 preflight 당시 pinned SHA와 expected가 유지됨 → 기존 C03 통과
7. 내용 없는 proposal → `block`
8. evidence 없는 `no_change` → `block`
9. evidence가 결속된 `no_change` → 내부 `approval`, 표시 `review_ready`

## 6. 남은 신뢰 경계와 보류 항목

E안은 preflight 이후의 바꿔치기를 막습니다. 사람이 처음부터 잘못된 run-request를
확인하거나, LLM이 preflight와 expected 값 전달을 모두 통제하면 E안은 안전하지
않습니다. 현재 운영 결정은 다음과 같습니다.

- 지금은 사람이 preflight의 `intent_summary`를 확인하고 digest를 직접 보관·전달합니다.
- 보호 CI를 사용할 때는 LLM 단계가 이전 job output, workflow 정의, expected 전달
  경로를 수정할 수 없어야 합니다.
- 완전 무인 운영은 이번 범위가 아닙니다. 그때는 서명·권한 분리가 포함된 C+가
  별도로 필요합니다.

다음 항목은 이번 P1-A와 분리한 P2입니다.

- C44 전용 회귀 test
- boundary lint의 문자열 결합 회피
- hook 실행기 신뢰 판별을 파일명 접미사가 아닌 절대경로로 강화
- Q3·Q6·Q7·Q8·Q9 조직 결정

## 7. 다음 실행 순서

1. `docs/04-진행/OM_PLAN_E_HARDENING_CLAUDE_REVIEW_REQUEST_20260814.md`로
   Claude 구현 적대 검토를 수행합니다.
2. Claude가 재현 가능한 P0/P1을 찾으면 해당 반례를 먼저 test로 추가하고 수정합니다.
3. 집중 92건과 전체 harness를 다시 실행합니다.
4. P0/P1이 없으면 clean clone에서 preflight → 사람 digest 보관 → proposal →
   final validation 종단 시연을 수행합니다.
5. 실제 운영 Skill 설치, merge, release는 별도 사용자 승인 전까지 수행하지 않습니다.

## 8. 중단 조건

- final validation이 expected 없이 `review_ready`에 도달함
- 공식 문서를 바꿔도 `input_lock_digest`가 유지됨
- 내부 `APPROVAL` enum 또는 비-plan 소비자 동작이 변경됨
- 빈 proposal이나 근거 없는 `no_change`가 `review_ready`에 도달함
- LLM이 expected 생성·선택·전달을 모두 통제하는 환경을 안전하다고 표시함
- 테스트 실패를 문서에서 통과로 바꿈
