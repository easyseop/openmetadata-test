# `/om-plan` 보호 CI 배선 운영 가이드

> 작성: 2026-08-15 KST
> 구현 기준: `9bc4cd2c3dca064d2d181b4e500415e18c336e9c`
> 상태: 코드·로컬 반례 검증 완료, GitHub 보호 환경 설정과 실제 workflow 실행은 대기

## 1. 무엇이 달라졌나

기존에는 `plan-preflight`가 만든 `input_lock_digest`를 사람이 복사해 마지막
`plan-validate`에 넣어야 했습니다. 이제 `.github/workflows/om-plan-ci.yml`이 다음
경계를 만듭니다.

1. 신뢰된 `preflight` job이 요청 ref와 공식 문서 bytes를 포함한 지문을 계산합니다.
2. 지문은 저장소 파일이 아니라 GitHub job output과 별도 receipt artifact에 둡니다.
3. 사람이 `intent_summary`의 요청 ref·고정 SHA·모드 등을 확인합니다.
4. proposal은 비신뢰 데이터로만 받으며 YAML·JSON 이외의 파일을 실행하지 않습니다.
5. 마지막 job이 preflight job output을 직접 받아 fresh `plan-validate`를 실행합니다.
6. 판정은 이 job의 stdout과 종료 코드만 사용합니다. run에 남아 있던
   `validation-result.json`은 CI 판정 입력으로 읽지 않습니다.

내부 verdict와 종료 코드는 바꾸지 않았습니다.

| verdict | 종료 코드 | CI 의미 |
|---|---:|---|
| `pass` | 0 | 기계 검사 통과 |
| `block` | 1 | 실패 |
| `approval` | 2 | 사람 검토 준비 상태, 자동 통과 아님 |
| `analysis_error` | 3 | 입력·검사·결속 오류 |

## 2. 실제 workflow 경계

### `preflight`

- default branch에서 실행한 workflow 정의만 허용합니다.
- request는 정확한 40자 commit SHA에서 data로 checkout합니다.
- 제품 저장소는 clean clone으로 준비합니다.
- 공식 문서가 request 저장소 파일이면 request root 밖 경로와 symlink를 거부합니다.
- trusted run artifact와 지문 receipt를 서로 다른 artifact로 보관합니다.

### `intent-review`

- GitHub environment `om-plan-intent-review`를 참조합니다.
- 환경 변수 `OM_PLAN_INTENT_REVIEW_ENFORCED=true`가 없으면 종료 코드 3으로 중단합니다.
- 이 승인은 run-request 의도가 맞는지 확인하는 단계입니다. 구현·배포 승인이 아닙니다.

### `untrusted-proposal`

- `preflight` job이나 지문 output을 dependency로 받지 않습니다.
- exact `proposal_ref`에서 proposal을 읽되 YAML·JSON regular file만 복사합니다.
- proposal checkout의 스크립트, workflow, symlink를 실행하거나 artifact에 넣지 않습니다.

### `validate`

- trusted run과 untrusted proposal artifact를 별도로 다운로드합니다.
- proposal data만 trusted run의 빈 proposal 디렉터리에 넣습니다.
- 새 runner의 제품·검사기 경로와 session marker를 다시 결속합니다.
- expected 지문은 `${{ needs.preflight.outputs.input_lock_digest }}`에서만 받습니다.
- fresh CLI stdout verdict와 실제 process exit가 다르면 `analysis_error`로 중단합니다.

## 3. GitHub에서 먼저 설정할 것

이 설정이 없으면 E안의 보안 경계가 완성되지 않습니다.

1. workflow를 default branch에 반영하고 default branch 직접 push를 제한합니다.
2. repository Settings → Environments에서 `om-plan-intent-review`를 만듭니다.
3. Required reviewers를 지정합니다.
4. Prevent self-review를 켭니다.
5. 관리자 우회를 허용하지 않는 옵션이 제공되면 우회를 끕니다.
6. deployment branch 정책은 default branch만 허용합니다.
7. environment variable `OM_PLAN_INTENT_REVIEW_ENFORCED=true`를 추가합니다.
8. custom deployment protection app을 이 환경에 함께 쓰지 않습니다.
   workflow가 `deployment: false`이므로 그런 app과는 호환되지 않습니다.

GitHub 요금제·저장소 공개 범위에 따라 Required reviewers 제공 여부가 다릅니다.
Required reviewers를 쓸 수 없는 환경에서는 이 workflow를 보호 경계로 운영했다고
표시하면 안 됩니다.

## 4. 실행 입력

workflow_dispatch에 다음 다섯 값을 넣습니다.

| 입력 | 의미 |
|---|---|
| `request_ref` | run-request가 있는 정확한 40자 governance commit SHA |
| `request_path` | 그 commit 안의 repository-relative run-request YAML 경로 |
| `product_repository` | 검사할 제품 저장소 `owner/name` |
| `proposal_ref` | LLM proposal data가 있는 정확한 40자 commit SHA |
| `proposal_path` | 그 commit 안의 repository-relative proposal 디렉터리 |

예시 형식은 다음과 같습니다. 실제 SHA와 경로는 실행 대상에 맞게 바꿉니다.

```bash
gh workflow run om-plan-ci.yml \
  --ref <DEFAULT_BRANCH> \
  -f request_ref=<40_CHAR_REQUEST_SHA> \
  -f request_path=<REQUEST_YAML_PATH> \
  -f product_repository=<OWNER/PRODUCT_REPOSITORY> \
  -f proposal_ref=<40_CHAR_PROPOSAL_SHA> \
  -f proposal_path=<PROPOSAL_DIRECTORY>
```

## 5. 중요한 한계

- 이 workflow는 특정 LLM API를 호출하지 않습니다. provider가 정해지지 않았기 때문에
  LLM 생성물은 exact `proposal_ref`의 data로 입력합니다. 지문 전달과 독립 검증은
  자동화됐지만, LLM 호출 자체는 외부 단계입니다.
- 따라서 `proposal_ref`가 사람 의도 확인 뒤 생성됐다는 시간 순서를 이 workflow 하나가
  증명하지는 않습니다. 다만 proposal은 지문을 보거나 바꿀 수 없고 최종 판정을 완화하지
  못합니다.
- 실제 GitHub-hosted runner 실행은 아직 하지 않았습니다. workflow가 default branch에
  없고, environment owner 설정도 아직 없기 때문입니다.
- 실제 제품 계획의 `review_ready`, merge, release, deploy는 수행하지 않았습니다.
- Q3·Q6·Q7·Q8·Q9는 계속 보류입니다. 특히 종료 코드 2를 최종 사람 승인으로 어떻게
  라우팅할지는 이번 구현에서 결정하지 않았습니다.

## 6. 로컬 검증 증적

```bash
PYTHONDONTWRITEBYTECODE=1 \
/Users/seop/om-work/openmetadata-test/.venv/bin/python -m pytest \
  -p no:cacheprovider \
  harness/tests/test_plan_workflow.py \
  harness/tests/test_om_workflow.py \
  harness/tests/test_plan_boundary.py \
  harness/tests/test_om_plan_ci.py \
  --junitxml=/private/tmp/om-plan-ci-focused-20260815.xml -q
```

- 집중 회귀: 108 tests, failure 0, error 0, skip 0

```bash
PYTHONDONTWRITEBYTECODE=1 \
/Users/seop/om-work/openmetadata-test/.venv/bin/python -m pytest \
  -p no:cacheprovider harness/tests \
  --junitxml=/private/tmp/om-plan-ci-harness-20260815.xml -q
```

- 전체 harness: 527 tests, failure 0, error 0, 37 skipped
- 37 skip은 기존 OM mirror·Runtime 등 이 clone에 없는 환경 의존 항목입니다.
- `git diff --check` 통과

## 7. 실제 운영 전 완료 조건

1. Claude가 구현 commit `9bc4cd2c...`를 다시 적대 검토해 P0/P1 없음으로 판정합니다.
2. workflow를 보호된 default branch에 반영합니다.
3. `om-plan-intent-review` environment 보호 규칙을 저장소 owner가 설정합니다.
4. 무해한 fixture request/proposal로 GitHub Actions 종단 실행을 1회 수행합니다.
5. proposal이 workflow 파일·지문·expected 값을 바꾸려 해도 fresh validation 결과가
   완화되지 않는 실행 증적을 보관합니다.
6. 그 전에는 `CI 운영 완료`, `최종 PASS`, `배포 승인`으로 표시하지 않습니다.
