# 현재 작업 인수인계 — `/om-plan` GitLab 보호 CI 배선

> 마지막 갱신: 2026-08-15 02:26 KST
> 현재 작업: GitHub을 사용하지 않는 GitLab CI 보호 배선과 runner bytecode 방어
> 상태: source 구현 commit·로컬 회귀 검증 완료, Claude 재검토와 실제 GitLab 설정·실행 대기

## 1. 이번 결론

기존 E-hardening과 `harness/ci/om_plan_ci.py`의 지문·격리·fresh validation
함수는 수정하지 않고 재사용했습니다. 새 `.gitlab-ci.yml`이 GitLab의 job artifact,
`dependencies`/`needs:artifacts`, `GIT_STRATEGY: clone`, protected branch,
protected environment deployment approval로 기존 보호 경계를 다시 구성합니다.

GitLab Runner 재사용 환경에서는 지문에서 제외된 조작 `.pyc`가 실행될 수 있으므로
다음 두 방어를 필수로 추가했습니다.

1. checker Python을 시작하기 전에 `__pycache__`, `.pyc`, `.pyo`를 제거합니다.
2. 각 trusted job이 `PYTHONDONTWRITEBYTECODE=1`을 직접 export합니다.

timestamp와 source size가 맞는 조작 `.pyc`가 정리 전에는 악성 값을 실행하고,
정리 후에는 원본 `.py`만 실행되는 반례 test를 추가했습니다.

## 2. 저장소·branch·commit

| 항목 | 값 |
|---|---|
| 저장소 | `easyseop/openmetadata-test` |
| 로컬 경로 | `/Users/seop/Documents/Codex/om-plan-claude-review-20260814/openmetadata-test` |
| branch | `codex/om-plan-ci-wiring-20260815` |
| GitLab 배선 기준 | `150a539465fa41f00135625d56657fa4ab2a83fa` |
| E-hardening | `1f02e1d3a0c77b9d62f5763835d91cbadc1d5804` |
| provider-neutral CI helper | `9bc4cd2c3dca064d2d181b4e500415e18c336e9c` |
| bytecode digest 제외 | `7aaa18f53e47a0a98185cfcb27f22966a637c025` |
| GitLab 배선 구현 | `ee9f033aea9446e19a0b7420c85a8eb8bd70dc44` |

최종 전달 시 `git status --short` 출력은 없으며 working tree는 clean입니다.

## 3. 구현한 pipeline 흐름

1. `om_plan_preflight`
   - protected default branch의 fresh clone에서 preflight 실행
   - trusted run, expected digest receipt, intent summary를 artifact로 보관
2. `om_plan_intent_review`
   - `om-plan-intent-review` protected environment를 사용하는 blocking manual job
   - environment 승인 뒤에도 권한 있는 사용자가 manual job을 실행해야 다음 stage 진행
3. `om_plan_package_proposal`
   - `dependencies: []`로 preflight artifact를 받지 않음
   - proposal checkout의 YAML·JSON regular file만 data로 packaging
4. `om_plan_validate`
   - preflight와 proposal artifact만 명시적으로 다운로드
   - fresh product/checker에서 저장 결과가 아닌 방금 실행한 stdout·종료 코드로 판정

expected digest는 dotenv report나 CI/CD variable로 전달하지 않습니다. proposal job이
자동 상속하지 않는 일반 preflight artifact의 text file로만 전달합니다.

## 4. GitLab 적대 경계

| 위험 | 구현 결과 |
|---|---|
| proposal에 expected 변수 유출 | expected를 variable로 만들지 않고 proposal에 `dependencies: []` 적용 |
| proposal이 preflight artifact 다운로드 | 자동 다운로드 차단; validate만 `needs:artifacts`로 지정 |
| reused runner의 조작 bytecode | fresh clone 강제 확인, 실행 전 cache 제거, bytecode 재생성 억제 |
| 비보호 branch 실행 | `reject_untrusted_context`가 종료 코드 3으로 명시적 실패 |
| fork MR·push·schedule 우회 | `workflow:rules`가 수동 web pipeline 외에는 pipeline을 만들지 않음 |
| 승인 없는 진행 | blocking manual job과 protected environment 외부 승인 규칙 필요 |
| 저장 결과 위조 | `run_fresh_validation`의 fresh stdout·exit만 신뢰 |

GitLab 설정의 실제 protected branch, Allowed to deploy, Approvers, required approval
수는 repository 밖에 있으므로 source test만으로 성립을 주장하지 않습니다.

## 5. 변경 파일

- `.gitlab-ci.yml`
  - typed pipeline inputs와 protected default branch rules
  - preflight → intent review → proposal data → fresh validate stage
  - artifact 전달 최소화와 exit 2 보존
- `harness/ci/prepare_trusted_checker.sh`
  - checker HEAD 확인과 Python bytecode 사전 제거
  - tracked file이 바뀌면 종료 코드 3으로 실패
- `harness/tests/test_om_plan_gitlab_ci.py`
  - GitLab 구조·artifact·승인·branch·exit 의미 test
  - timestamp-valid 조작 `.pyc` 실행과 무력화 반례
- `docs/04-진행/OM_PLAN_GITLAB_CI_OPERATIONS_20260815.md`
  - 관리자 준비, 실행, 승인, 결과 해석, 복구, 증적 가이드
- `docs/04-진행/OM_PLAN_GITLAB_CI_CLAUDE_REVIEW_REQUEST_20260815.md`
  - 구현 commit 대상 읽기 전용 적대 재검토 요청

기존 `.github/workflows/om-plan-ci.yml`은 참조용으로 보존했고 수정하지 않았습니다.
`verdict.py`, exit code, 제품 코드, registration도 변경하지 않았습니다.

## 6. 로컬 검증

### GitLab 전용 test

- 5 passed, failure 0, error 0, skip 0
- typed inputs, protected rules, artifact 격리, approval job, fresh exit 보존,
  조작 `.pyc` 무력화를 확인

### CI 경계 집중 test

- 23 tests, failure 0, error 0, skip 0
- JUnit: `/private/tmp/om-plan-gitlab-ci-focused-20260815.xml`

### 계획·CI 집중 회귀

- 115 tests, failure 0, error 0, skip 0
- JUnit: `/private/tmp/om-plan-gitlab-focused-20260815.xml`

### 전체 harness

- 534 tests, failure 0, error 0, 37 skipped
- JUnit: `/private/tmp/om-plan-gitlab-harness-20260815.xml`
- 37 skip은 기존 OM mirror·Runtime 등 환경 의존 항목입니다.

`git diff --check`도 통과했습니다. GitLab CI Lint와 실제 pipeline은 아직 실행하지
않았습니다.

## 7. GitLab에서 반드시 설정할 것

자세한 절차는 `OM_PLAN_GITLAB_CI_OPERATIONS_20260815.md`에 있습니다.

- GitLab 17.11 이상과 protected environment approval 지원 tier
- protected default branch
- protected environment `om-plan-intent-review`
- Allowed to deploy와 Approvers를 분리하고 triggerer self-approval 비활성화
- protected·masked·environment-scoped marker
  `OM_PLAN_INTENT_REVIEW_ENFORCED=protected`
- pipeline variables 사용 금지 또는 `no_one_allowed`; typed inputs 사용
- product project의 `CI_JOB_TOKEN` allowlist
- Git·Python 3.11·venv를 제공하고 `om-plan-protected` tag로 잠근 protected runner
- artifact 보관·삭제·조직 archive 정책(Q7)은 별도 결정

## 8. 의도적으로 결정하지 않은 것

- Q3, Q6, Q7, Q8, Q9
- exit 2를 GitLab 성공 0 또는 allowed failure로 바꾸는 정책
- 승인자 이름·그룹·필요 승인 수
- artifact 영구 보관 기간
- 실제 GitLab project URL과 runner 종류
- merge, release, deploy, 운영 완료

현재 `approval/review_ready`는 기존 의미대로 exit 2입니다. GitLab은 이를 실패로
표시하지만 Q9 결정 전에는 변환하지 않습니다. fresh summary와 stdout artifact에
`verdict`, `review_state`, exit code를 모두 남깁니다.

## 9. 다음 실행 순서

1. Claude가 구현 commit `ee9f033aea9446e19a0b7420c85a8eb8bd70dc44`의
   GitLab ①~⑤ 경계와 조작 `.pyc` 반례를 읽기 전용 재검토합니다.
2. P0/P1이 없으면 사용자가 GitLab project에 반영할지 결정합니다.
3. 사용자 승인 후에만 CI Lint, 외부 protected 설정 확인, 실제 pipeline을 실행합니다.

현재 정확한 다음 명령:

```bash
git show --stat --oneline ee9f033aea9446e19a0b7420c85a8eb8bd70dc44
git diff 150a539465fa41f00135625d56657fa4ab2a83fa..ee9f033aea9446e19a0b7420c85a8eb8bd70dc44 -- \
  .gitlab-ci.yml \
  harness/ci/prepare_trusted_checker.sh \
  harness/tests/test_om_plan_gitlab_ci.py \
  docs/04-진행/OM_PLAN_GITLAB_CI_OPERATIONS_20260815.md
```

## 10. 중단 조건

- expected digest가 proposal job의 variable이나 artifact로 전달됨
- proposal checkout의 code·script·CI 설정을 실행함
- trusted checker가 fresh protected commit이 아님
- bytecode 정리 전에 checker Python을 실행함
- protected environment 승인 없이 proposal stage로 진행함
- 저장된 `validation-result.json`을 최종 판정 입력으로 사용함
- exit 2를 조직 결정 없이 0으로 변환함
- 실제 GitLab 미실행 상태를 운영 완료나 배포 완료로 표시함
