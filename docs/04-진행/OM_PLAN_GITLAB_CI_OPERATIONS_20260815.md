# `/om-plan` GitLab CI 설정·실행 가이드

> 대상: GitLab에서 `/om-plan` 보호 검증을 설정하는 관리자와 승인자
> 현재 상태: source 구현과 로컬 test 완료, 실제 GitLab 설정·pipeline 실행은 미완료
> 이 pipeline은 계획을 검증할 뿐 제품을 배포하지 않습니다.

## 1. 왜 필요한가

기존 `/om-plan` 보호 배선은 GitHub Actions의 fresh checkout, job 분리, artifact,
environment 승인을 사용했습니다. `.gitlab-ci.yml`은 같은 지문·검증·proposal 격리
코드를 재사용하면서 그 경계를 GitLab 기능으로 다시 구성합니다.

GitLab Runner는 작업 directory를 재사용할 수 있습니다. 따라서 모든 job을
`GIT_STRATEGY: clone`으로 시작하고, checker Python을 실행하기 전에 기존
`__pycache__`, `.pyc`, `.pyo`를 제거합니다. 그 다음
`PYTHONDONTWRITEBYTECODE=1`을 강제로 export해 job 안에서 cache가 다시 생기지 않게
합니다.

### 1.1 제품과 요청·제안 clone 정책이 다른 이유

preflight와 validate의 OpenMetadata **제품 저장소는 전체 clone**합니다.
검사기는 고정된 base·target commit의 실제 파일 내용(blob)을
`GIT_NO_LAZY_FETCH=1`로 읽으므로, 제품을 `--filter=blob:none`으로 clone하면
`SOURCE_BLOBS_UNAVAILABLE`로 fail-closed합니다. lazy fetch를 허용하지 않고
필요 blob을 clone 시점에 물리적으로 확보합니다.

반면 request·proposal source는 고정 SHA와 허용된 YAML·JSON data만
선택하며 제품 소스 blob을 검사하지 않습니다. 이 두 clone은 기존
`--filter=blob:none --no-checkout`을 유지합니다.

전체 제품 clone은 네트워크·디스크·시간 비용이 늘어날 수 있습니다.
현재는 명확한 fail-closed 성립을 성능보다 우선했습니다. 실제 GitLab
측정 후 최적화가 필요하더라도, 핀된 ref의 blob을 먼저 materialize한 후
현재 fail-closed 회귀를 그대로 통과하는 방식으로만 변경해야 합니다.

## 2. 코드가 구현한 경계

| 필요한 성질 | GitLab 기능과 코드 | 보증하는 것 | 보증하지 않는 것 |
|---|---|---|---|
| trusted expected digest | preflight의 일반 job artifact | proposal이 아니라 trusted preflight 결과에서 digest 생성 | artifact를 볼 수 있는 사용자를 비밀 보유자로 만들지는 않음; digest는 secret이 아님 |
| proposal 격리 | 별도 job, `dependencies: []`, YAML/JSON data-only packaging | proposal job에 preflight artifact가 자동 다운로드되지 않고 proposal 파일을 실행하지 않음 | 보호 branch의 `.gitlab-ci.yml` 자체가 악성으로 바뀌는 공격은 branch 보호가 막아야 함 |
| fresh checker | `GIT_STRATEGY: clone`, exact `CI_COMMIT_SHA` 확인, bytecode 제거 | 이전 runner worktree와 조작 Python cache를 checker 실행 전에 제거 | runner host나 GitLab 관리자가 악성인 경우까지 증명하지 않음 |
| 사람 intent 승인 | blocking manual job, `environment: om-plan-intent-review`, protected environment deployment approval | 허용된 승인자가 승인하고 manual job을 실행하기 전에는 proposal stage가 시작되지 않음 | environment 보호·승인자 목록은 YAML이 만들거나 확인할 수 없음; 관리자가 GitLab에서 설정해야 함 |
| fresh 판정 | `run_fresh_validation`의 stdout·종료 코드 직접 대조 | 저장된 `validation-result.json`을 판정 입력으로 사용하지 않음 | exit 2를 pipeline 성공으로 표시할지는 결정하지 않음(Q9) |

GitLab은 이전 stage의 artifact를 이후 job에 기본 다운로드합니다. proposal job은
`dependencies: []`로 이 기본 동작을 끕니다. validate job만 `needs:artifacts`로
preflight와 proposal artifact를 명시적으로 받습니다.

## 3. GitLab 관리자가 먼저 설정할 것

다음 항목은 repository 코드가 대신 설정할 수 없습니다. 하나라도 빠지면 실제 보호
pipeline 준비가 완료된 것이 아닙니다.

### 3.1 GitLab 버전과 기능

- pipeline inputs를 지원하는 GitLab 17.11 이상이 필요합니다.
- protected environment의 deployment approval을 사용하려면 GitLab Premium 또는
  Ultimate가 필요합니다.
- Runner에는 `git`, Python 3.11, `venv`, 네트워크 접근 권한이 필요합니다.
- trusted job은 `om-plan-protected` tag를 요구합니다. 이 tag를 가진 project runner를
  protected runner로 등록하고 다른 project가 사용하지 못하게 잠급니다.

### 3.2 default branch 보호

GitLab의 `Settings > Repository > Branch rules`에서 default branch를 protected
branch로 설정합니다.

- `Allowed to push and merge`는 `No one`으로 설정해 직접 push를 막습니다.
- `.gitlab-ci.yml`, `harness/ci/`, `harness/acgh/` 변경은 승인된 merge request를
  거치게 합니다.
- 실제 허용 역할·그룹은 조직이 결정합니다. 이 문서는 임의로 정하지 않습니다.

Pipeline은 다음 세 조건이 모두 참일 때만 trusted job을 만듭니다.

```text
CI_PIPELINE_SOURCE == "web"
CI_COMMIT_BRANCH == CI_DEFAULT_BRANCH
CI_COMMIT_REF_PROTECTED == "true"
```

비보호 branch에서 수동 실행하면 `reject_untrusted_context`가 종료 코드 3으로
실패합니다. merge request, push, schedule pipeline은 이 보호 workflow의 실행
입구가 아니므로 `workflow:rules`가 pipeline을 만들지 않습니다.

### 3.3 protected environment와 승인 분리

`Settings > CI/CD > Protected environments`에서
`om-plan-intent-review`를 보호합니다.

1. `Allowed to deploy`에 manual job을 실행할 운영 주체를 지정합니다.
2. `Approvers`와 required approval 수를 지정합니다.
3. pipeline 실행자와 승인자를 분리하려면 `Allow pipeline triggerer to approve
   deployment`를 켜지 않습니다.
4. 승인자·그룹·필요 승인 수는 조직 결정이므로 이 repository가 정하지 않습니다.

GitLab deployment approval 후에도 job은 자동 시작되지 않습니다. 승인 완료 뒤
권한이 있는 사람이 `om_plan_intent_review`의 Run 버튼을 눌러야 합니다.

### 3.4 환경 범위 marker variable

`Settings > CI/CD > Variables`에 다음 변수를 추가합니다.

| 항목 | 값 |
|---|---|
| Key | `OM_PLAN_INTENT_REVIEW_ENFORCED` |
| Value | `protected` |
| Protect variable | 켬 |
| Visibility | Masked |
| Environment scope | `om-plan-intent-review` |

이 변수는 설정 누락을 job에서 조기에 발견하는 marker입니다. 실제 승인 보안은
protected environment의 Allowed to deploy와 Approvers 규칙이 담당합니다.

Pipeline은 typed inputs를 사용하므로 `Settings > CI/CD > Variables > Minimum role
to use pipeline variables`는 `no_one_allowed`를 권장합니다. 이렇게 해야 수동
pipeline variable이 project variable이나 predefined variable을 덮어쓰지 못합니다.

### 3.5 product project 읽기 권한

preflight와 validate는 `CI_JOB_TOKEN`으로 같은 GitLab instance의 product project를
clone합니다. product project의 job token allowlist에 이 checker project를
추가합니다. clone 직후 job은 `CI_JOB_TOKEN`과 `CI_REPOSITORY_URL`을 unset한 뒤
request·proposal 데이터를 처리합니다.

### 3.6 artifact 보관

`.gitlab-ci.yml`은 `expire_in`을 정하지 않았습니다. 현재 artifact 보관 기간은
GitLab instance 또는 project 기본값을 따릅니다. 조직 archive와 삭제 기간은 Q7
결정 전이므로 이 구현이 확정하지 않습니다.

## 4. 실행 순서

### 4.1 실행자: 수동 pipeline 생성

GitLab에서 `Build > Pipelines > New pipeline`을 열고 protected default branch를
선택한 뒤 다음 다섯 input을 입력합니다.

| input | 예시 | 의미 |
|---|---|---|
| `request-ref` | `0123456789abcdef0123456789abcdef01234567` | run request와 공식 문서가 있는 commit |
| `request-path` | `ops/requests/upgrade.yaml` | 위 commit 안의 request YAML 경로 |
| `product-project` | `bank/openmetadata-product` | 같은 GitLab instance의 product project |
| `proposal-ref` | `89abcdef0123456789abcdef0123456789abcdef` | LLM proposal data가 있는 commit |
| `proposal-path` | `ops/proposals/run-001` | proposal YAML/JSON directory |

SHA 형식과 project 형식은 pipeline 생성 시 input regex가 확인합니다. 경로가
repository 밖으로 나가거나 symlink이면 trusted helper가 종료 코드 3으로 차단합니다.

### 4.2 자동: `om_plan_preflight`

이 job은 fresh checker와 product history를 준비하고 preflight를 실행합니다.
성공하면 다음 artifact를 만듭니다.

- `.om-plan-artifacts/trusted-run/`
- `.om-plan-artifacts/trusted-receipt/expected-input-lock-digest.txt`
- `.om-plan-artifacts/intent-summary.md`
- `.om-plan-artifacts/preflight-result.json`

### 4.3 승인자: intent 확인과 승인

승인자는 `om_plan_preflight` artifact의 `intent-summary.md`에서 요청 내용과 고정
commit SHA를 확인합니다. 이 확인은 구현·merge·배포 승인이 아닙니다.

내용이 맞으면 다음 두 동작을 순서대로 수행합니다.

1. `om-plan-intent-review` environment deployment를 승인합니다.
2. 승인이 충족된 뒤 `om_plan_intent_review` manual job을 실행합니다.

내용이 다르면 승인하거나 manual job을 실행하지 않고 pipeline을 중단합니다.

### 4.4 자동: proposal data packaging

승인 job이 성공한 뒤 `om_plan_package_proposal`이 시작됩니다. 이 job은 preflight
artifact를 받지 않으며 proposal checkout에서 YAML·JSON regular file만 복사합니다.
Python 파일, symlink, traversal, 비어 있지 않은 output은 차단됩니다.

### 4.5 자동: fresh validation

`om_plan_validate`는 fresh checker에서 trusted run과 proposal data를 결합한 뒤
preflight receipt의 digest를 사용해 검증을 다시 실행합니다. job log와 artifact에는
방금 실행한 stdout, `verdict`, `review_state`, 종료 코드가 남습니다.

## 5. 결과 해석

| 종료 코드 | verdict | review_state | 현재 GitLab 표시와 행동 |
|---|---|---|---|
| 0 | `pass` | `not_ready` | 기술 검사는 성공했지만 사람 review 준비 완료를 뜻하지 않음 |
| 1 | `block` | `not_ready` | 차단 사유를 수정하고 새 run 수행 |
| 2 | `approval` | `review_ready` | 정상 review 후보지만 GitLab job은 현재 빨강으로 표시; Q9 결정 전 0으로 변환 금지 |
| 3 | `analysis_error` | `not_ready` | 지문·환경·입력 오류를 해결한 뒤 처음부터 재실행 |

`exit 2`를 성공으로 바꾸거나 `allow_failure:exit_codes`로 처리하지 않았습니다. 조직이
Q9를 결정하기 전에는 `fresh-validation/summary.md`와 `stdout.json`을 직접 확인합니다.

## 6. 자주 발생하는 실패와 복구

| 증상 | 원인 | 복구 |
|---|---|---|
| `reject_untrusted_context` 실패 | 비보호 branch 또는 default branch가 아님 | protected default branch의 New pipeline에서 다시 실행 |
| intent review job에서 marker 실패 | protected/environment-scoped variable 누락 | §3.4 설정 후 새 pipeline 실행 |
| product clone 403 | product project job token allowlist 누락 | §3.5 설정 후 새 pipeline 실행 |
| `SOURCE_BLOBS_UNAVAILABLE` | 제품 clone이 blobless이거나 핀된 ref의 blob이 로컬에 없음 | 제품 clone 명령의 `--filter=blob:none` 재도입 여부를 확인하고, lazy fetch 허용 없이 새 pipeline 실행 |
| cache cleanup이 tracked 변경 감지 | checker가 bytecode를 tracked file로 포함하거나 checkout 오염 | 해당 file을 검토된 commit으로 제거하고 pipeline 재실행 |
| validate exit 2로 pipeline 빨강 | `review_ready`의 기존 종료 코드 의미 | 실패로 오해해 코드를 바꾸지 말고 artifact 확인; Q9는 별도 결정 |
| artifact가 없음 | 이전 job 실패 또는 다운로드 경계 오류 | 최초 실패 job부터 로그 확인; stored result를 임의 작성하지 않음 |

## 7. 보관할 증적과 완료선

다음 자료를 보관합니다.

- pipeline URL과 정확한 `CI_COMMIT_SHA`
- preflight의 `intent-summary.md`와 digest receipt
- protected environment 승인 기록과 manual job 실행자
- proposal data artifact
- fresh validation `stdout.json`과 `summary.md`

source 구현 완료선은 로컬 test 통과입니다. 운영 완료선은 실제 GitLab 설정을 확인하고
protected default branch에서 pipeline을 실행해 위 증적을 확보한 시점입니다. 현재는
source 구현 완료선까지만 도달했습니다.

## 8. 공식 GitLab 문서

- [CI/CD inputs](https://docs.gitlab.com/ci/inputs/)
- [Runner Git strategy](https://docs.gitlab.com/ci/runners/configure_runners/#git-strategy)
- [Job artifact 다운로드 제어](https://docs.gitlab.com/ci/jobs/job_artifacts/#fetching-artifacts)
- [Protected environments](https://docs.gitlab.com/ci/environments/protected_environments/)
- [Deployment approvals](https://docs.gitlab.com/ci/environments/deployment_approvals/)
- [Protected branches](https://docs.gitlab.com/user/project/repository/branches/protected/)
- [Pipeline variable 제한](https://docs.gitlab.com/ci/variables/#restrict-pipeline-variables)
