# 현재 작업 인수인계 — `/om-plan` 보호 CI 배선

> 마지막 갱신: 2026-08-15 00:30 KST
> 현재 작업: E-hardening의 expected digest를 보호 CI가 보관·전달하도록 배선
> 상태: 코드·로컬 반례 검증 완료, Claude 재검토와 실제 GitHub Actions 실행 대기

## 1. 목적과 결론

E-hardening은 사람이 보관한 `input_lock_digest`가 있어야 preflight 이후의 세 파일
동시 재작성 공격을 차단합니다. 이번 작업은 수동 복사를 없애고 보호된 GitHub Actions가
그 지문을 final validation까지 전달하도록 만들었습니다.

구현된 경계는 다음 세 가지입니다.

1. 지문은 repo 파일이 아니라 preflight job output과 별도 receipt artifact에 둡니다.
2. 비신뢰 proposal job에는 preflight dependency·지문·expected 값을 주지 않습니다.
3. 마지막 판정은 이 job에서 방금 실행한 `plan-validate` stdout과 종료 코드만 사용합니다.

공식 문서 bytes는 기존 E-hardening의 `official_doc_sources_digest`를 통해 단일
`input_lock_digest`에 포함됩니다.

## 2. 저장소·branch·commit

| 항목 | 값 |
|---|---|
| 저장소 | `easyseop/openmetadata-test` |
| 로컬 경로 | `/Users/seop/Documents/Codex/om-plan-claude-review-20260814/openmetadata-test` |
| branch | `codex/om-plan-ci-wiring-20260815` |
| E-hardening 구현 | `1f02e1d3a0c77b9d62f5763835d91cbadc1d5804` |
| E-hardening 인수인계 기준 | `0af1a5989434222656f458b9c88fa69cc9896a75` |
| CI 배선 구현 | `9bc4cd2c3dca064d2d181b4e500415e18c336e9c` |
| CI 배선 tree | `ff83a8492ccbd4abc0e5448945d2bf6c614cb6ab` |

## 3. 변경 파일

- `.github/workflows/om-plan-ci.yml`
  - preflight → intent review → untrusted proposal data → fresh validate
- `harness/ci/om_plan_ci.py`
  - CI-local request 준비, 지문 capture, proposal data-only packaging,
    새 runner 경로·marker 재결속, fresh stdout/exit 검증
- `harness/ci/__init__.py`
- `harness/tests/test_om_plan_ci.py`
  - CI 구조 반례와 실제 두 runner 이동 종단 test 16건
- `docs/04-진행/OM_PLAN_CI_WIRING_OPERATIONS_20260815.md`
  - 설정·실행·신뢰 경계·미완료 항목
- `docs/04-진행/OM_PLAN_CI_WIRING_CLAUDE_REVIEW_REQUEST_20260815.md`
  - 구현 적대 재검토 요청

## 4. 로컬 검증

### CI 경계 test

- 16 passed
- proposal job에 지문 미전달, path escape·symlink 차단, exit/verdict 교차 대조,
  저장 결과 미사용, cross-runner fresh validation을 포함합니다.

### 집중 회귀

- 108 tests
- failure 0, error 0, skip 0
- JUnit: `/private/tmp/om-plan-ci-focused-20260815.xml`

### 전체 harness

- 527 tests
- failure 0, error 0, 37 skipped
- JUnit: `/private/tmp/om-plan-ci-harness-20260815.xml`
- skip은 기존 OM mirror·Runtime 등 환경 의존 항목입니다.

`git diff --check`도 통과했습니다.

## 5. 아직 완료하지 않은 것

- 실제 GitHub Actions 실행
- default branch merge
- `om-plan-intent-review` environment와 required reviewers 설정
- 특정 LLM provider 호출 자동화
- 실제 제품 request/proposal 종단 판정
- 종료 코드 2의 최종 사람 승인 routing(Q9)
- merge, release, deploy

현재 workflow의 `untrusted-proposal` job은 exact commit의 LLM proposal을 데이터로
격리·전달합니다. LLM API를 직접 호출하지는 않습니다. provider와 secret 권한 모델을
추측하지 않기 위해 이 경계를 명시적으로 남겼습니다.

## 6. 다음 실행 순서

1. `OM_PLAN_CI_WIRING_CLAUDE_REVIEW_REQUEST_20260815.md`로 commit `9bc4cd2c...`를
   읽기 전용 적대 검토합니다.
2. 재현 가능한 P0/P1이 있으면 반례 test를 먼저 추가하고 수정합니다.
3. P0/P1이 없으면 branch를 원격에 보관합니다.
4. 저장소 owner가 default branch 보호와 `om-plan-intent-review` 환경을 설정합니다.
5. fixture로 실제 GitHub Actions 종단 실행 후 receipt·fresh stdout을 보관합니다.
6. 그 뒤에만 실제 제품 계획을 대상으로 사용할지 결정합니다.

## 7. 중단 조건

- proposal job이 preflight output 또는 expected digest를 읽음
- proposal checkout의 코드나 workflow를 실행함
- expected digest를 proposal artifact나 저장소 파일에서 유도함
- 저장된 `validation-result.json`을 CI 판정 입력으로 읽음
- fresh stdout verdict와 process exit 불일치를 허용함
- 종료 코드 2를 자동 성공 0으로 바꿈
- 보호 environment가 없는데 사람 intent review가 강제됐다고 표시함
- 실제 workflow 미실행 상태를 운영 완료 또는 최종 PASS로 표시함
