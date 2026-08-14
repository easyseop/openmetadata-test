# Claude 재검토 요청 — `/om-plan` GitLab 보호 CI 배선

> 검토 방식: 읽기 전용 적대 검토
> 대상 branch: `codex/om-plan-ci-wiring-20260815`
> 기준 commit: `150a539465fa41f00135625d56657fa4ab2a83fa`
> 구현 commit: `ee9f033aea9446e19a0b7420c85a8eb8bd70dc44`
> 실제 GitLab CI Lint·pipeline·protected 설정은 아직 실행하거나 확인하지 않음

## 1. 검토 목적

GitHub을 사용하지 않는 조건에서 기존 E-hardening과 provider-neutral CI helper를
재사용하고, GitLab 기능으로 같은 신뢰 경계를 다시 구성했는지 검토해 주세요.

다음 질문에 P0·P1·P2와 재현 가능한 반례를 우선해 답해 주세요.

1. expected digest가 trusted preflight에서만 생성되고 proposal job에 variable이나
   artifact로 전달되지 않는가?
2. proposal checkout은 YAML·JSON data로만 다뤄지고 checker·expected·token을 이용한
   실행 경로가 없는가?
3. GitLab Runner가 재사용돼도 checker는 trusted `CI_COMMIT_SHA`의 fresh clone이며,
   조작된 timestamp-valid `.pyc`가 Python 실행 전에 제거되는가?
4. protected default branch와 `om-plan-intent-review` protected environment를 실제로
   설정하면 승인 없이 proposal stage로 진행할 수 없는가?
5. final job이 stored `validation-result.json`이 아니라 방금 실행한
   `run_fresh_validation` stdout·종료 코드만 신뢰하는가?

## 2. 변경 범위

```text
.gitlab-ci.yml
harness/ci/prepare_trusted_checker.sh
harness/tests/test_om_plan_gitlab_ci.py
docs/04-진행/OM_PLAN_GITLAB_CI_OPERATIONS_20260815.md
```

다음은 변경하지 않았습니다.

- `.github/workflows/om-plan-ci.yml` — GitHub 참조용으로 보존
- `harness/ci/om_plan_ci.py`의 provider-neutral 함수 6개
- `harness/acgh/plancore/paths.py`의 채택된 bytecode 지문 제외 로직
- `verdict.py`, exit code, 제품 코드, registration

## 3. GitLab 경계별 확인점

### 3.1 pipeline 입력과 보호 ref

- `spec:inputs`가 request/proposal ref를 정확한 40자 소문자 SHA로 제한하는가?
- trusted job rule이 수동 web pipeline, default branch, protected ref 세 조건을 모두
  요구하는가?
- 비보호 수동 pipeline은 `reject_untrusted_context`로 명시적 실패하는가?
- MR·push·schedule이 이 보호 workflow를 실행하지 않는다는 경계가 과대주장 없이
  문서화됐는가?

### 3.2 artifact와 variable 노출

- preflight artifact가 expected receipt와 trusted run을 함께 보관해도 proposal job의
  `dependencies: []` 때문에 자동 다운로드되지 않는가?
- validate의 `needs:artifacts`가 preflight·proposal artifact만 받는가?
- dotenv report를 사용하지 않아 expected가 후속 job variable로 퍼지지 않는가?
- `OM_PLAN_INTENT_REVIEW_ENFORCED`가 protected·masked·environment-scoped marker일 뿐,
  실제 승인 보안의 근거라고 과대평가하지 않는가?

### 3.3 runner 재사용과 조작 bytecode

- 모든 trusted job이 `om-plan-protected` runner tag와 `GIT_STRATEGY: clone`을 요구하고,
  runtime에서 값이 `clone`인지 다시 확인하는가?
- `prepare_trusted_checker.sh`가 첫 명령으로 실행돼 `__pycache__`, `.pyc`, `.pyo`를
  checker Python보다 먼저 제거하는가?
- `CI_COMMIT_SHA`와 checker HEAD 불일치, cache 제거로 tracked file이 바뀌는 경우가
  종료 코드 3으로 닫히는가?
- `PYTHONDONTWRITEBYTECODE=1`을 job script가 직접 export해 project variable 우선순위로
  덮인 값을 다시 고정하는가?

### 3.4 사람 승인

- `om_plan_intent_review`가 `when: manual`, `allow_failure: false`, protected environment
  deployment job으로 정의됐는가?
- GitLab deployment approval 뒤 manual job을 별도로 실행해야 한다는 절차가 맞는가?
- Allowed to deploy, Approvers, required approval, triggerer self-approval 금지는 GitLab
  외부 설정이며 아직 미검증이라고 정확히 표시했는가?

### 3.5 fresh validation과 exit 2

- validate job이 expected receipt를 artifact에서 읽고 fresh helper에 직접 전달하는가?
- job log와 artifact에 stdout, verdict, review_state, exit code가 남는가?
- exit 2를 0이나 allowed failure로 바꾸지 않아 Q9를 임의 확정하지 않았는가?

## 4. 필수 공격 반례

`test_cache_cleaner_neutralizes_timestamp_valid_crafted_pyc`는 다음 순서입니다.

1. benign `.py`와 mtime·size가 일치하는 악성 `.pyc`를 생성합니다.
2. 정리 전 새 Python process가 악성 값 `PWNED!`를 실행하는지 확인합니다.
3. GitLab의 첫 준비 script를 실행합니다.
4. `PYTHONDONTWRITEBYTECODE=1` 상태의 새 process가 benign 값만 실행하고
   `__pycache__`를 다시 만들지 않는지 확인합니다.

이 test가 실제 GitLab job의 실행 순서와 같은 보안 성질을 증명하는지, 우회 가능한
cache·import 경로가 남는지 확인해 주세요.

## 5. 로컬 선언 결과

모든 결과는 실제 GitLab 실행이 아니라 local source test입니다.

- GitLab 전용: 5 passed, failure 0, error 0, skip 0
- CI 경계 집중: 23 tests, failure 0, error 0, skip 0
- 계획·CI 집중: 115 tests, failure 0, error 0, skip 0
- 전체 harness: 534 tests, failure 0, error 0, 37 skipped
- `git diff --check`: 통과
- `sh -n harness/ci/prepare_trusted_checker.sh`: 통과
- `.gitlab-ci.yml`: PyYAML 2개 document parsing 통과

GitLab CI Lint와 실제 pipeline은 미실행입니다. YAML parsing 성공을 GitLab 실행 성공으로
간주하지 말아 주세요.

## 6. 계속 보류할 항목

다음 항목은 권고할 수 있지만 임의로 확정하지 말아 주세요.

- Q3, Q6, Q7, Q8, Q9
- exit 2를 GitLab 성공으로 매핑할지 여부
- 승인자·그룹·필요 승인 수
- artifact 보관·삭제·조직 archive 기간
- 실제 GitLab project URL과 runner 종류
- merge, release, deploy, 운영 완료

## 7. 원하는 출력

1. P0·P1·P2 findings와 정확한 파일·행·반례
2. GitLab 기능별로 “source에서 성립”, “외부 설정 필요”, “실제 pipeline 검증 필요” 구분
3. 조작 `.pyc` 통로가 닫혔는지 독립 실행 결과
4. GitLab CI Lint 또는 실제 pipeline 전에 반드시 고칠 항목
5. 최종 판정: 채택 / 수정 후 재검토 / 보류

검토 중 원본 branch·file·Git index를 수정하거나 commit·push·merge·release·deploy하지
말아 주세요.
