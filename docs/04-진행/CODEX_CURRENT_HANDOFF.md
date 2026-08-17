# 현재 작업 인수인계 — `/om-plan` GitLab 제품 clone blob 확보

> 마지막 갱신: 2026-08-17 KST
>
> 상태: 코드 수정·로컬 회귀 완료, Claude 읽기 전용 재검토와 실제 GitLab 실행 대기

## 1. 이번 문제와 결론

GitLab pipeline이 OpenMetadata 제품 저장소를 `--filter=blob:none`으로
clone하면, 검사기가 `GIT_NO_LAZY_FETCH=1`로 소스 blob을 확인할 때
`SOURCE_BLOBS_UNAVAILABLE`로 중단됩니다. fail-closed 경계를 완화하지
않고, preflight와 validate의 **제품 clone 2곳만 전체 clone**으로
바꾸었습니다.

request·proposal 저장소는 소스 내용을 읽지 않으므로 기존
`--filter=blob:none --no-checkout`을 유지합니다.

## 2. 저장소·branch·commit

| 항목 | 값 |
|---|---|
| 저장소 | `easyseop/openmetadata-test` |
| 로컬 경로 | `/Users/seop/Documents/Codex/om-plan-claude-review-20260814/openmetadata-test` |
| branch | `codex/om-plan-gitlab-product-clone-20260817` |
| 기존 GitLab CI 기준 | `ee9f033aea9446e19a0b7420c85a8eb8bd70dc44` |
| 수정 코드 commit | `ef48a8eee0b3c6b99f2fcd0d4f8f5d70ebc57d3a` |
| 수정 코드 tree | `c34fdae790602c139cb6868b34b1d6ab511d8797` |

## 3. 실제 변경

- `.gitlab-ci.yml`
  - `om_plan_preflight` 제품 clone에서 `--filter=blob:none` 제거
  - `om_plan_validate` 제품 clone에서 `--filter=blob:none` 제거
  - request·proposal clone은 기존 부분 clone 유지
- `harness/tests/test_om_plan_gitlab_ci.py`
  - 제품만 전체 clone하는지 정적 검사
  - blobless 제품에서 `SOURCE_BLOBS_UNAVAILABLE`로 차단되는 반례
  - 전체 clone에서 base·target 소스 blob 수집이 통과하는 대조군

## 4. 불변 보안 경계

다음은 수정하지 않았습니다.

- `GIT_NO_LAZY_FETCH=1`
- `SOURCE_BLOBS_UNAVAILABLE` fail-closed
- expected digest, E-hardening, proposal 격리, fresh validation
- `.pyc` 정리와 bytecode 재생성 억제
- verdict enum과 exit code 2
- 제품 코드·활성 registration
- Q3·Q6·Q7·Q8·Q9

## 5. 로컬 검증

| 범위 | 결과 | JUnit |
|---|---|---|
| GitLab·CI·plan 집중 회귀 | 116 passed, 0 failed, 0 skipped | `/private/tmp/om-plan-gitlab-product-clone-focused-20260817.xml` |
| 전체 harness | 536 passed, 0 failed, 37 skipped | `/private/tmp/om-plan-gitlab-product-clone-harness-20260817.xml` |

집중 회귀에는 protected CI의 preflight→fresh validate가 재계산된
소스와 expected digest를 대조해 `review_ready`(내부 verdict `approval`,
exit 2)에 도달하는 기존 종단 반례가 포함됩니다.

37 skip은 기존 OM mirror·Runtime 등 환경 의존 항목입니다.
`git diff --check`도 통과했습니다.

## 6. 아직 확인하지 않은 것

- 실제 GitLab server의 CI Lint
- 실제 product project를 통한 pipeline
- 실제 GitLab runner의 clone 시간·네트워크·디스크 비용
- protected branch·environment·approval·job-token allowlist 외부 설정
- Q3·Q6·Q7·Q8·Q9

따라서 현재 상태는 **source 수정과 로컬 검증 완료**이며,
실제 GitLab 운영 완료나 배포 완료가 아닙니다.

## 7. 다음 순서

1. Claude가 `OM_PLAN_GITLAB_PRODUCT_CLONE_CLAUDE_REVIEW_REQUEST_20260817.md`를
   기준으로 commit `ef48a8e...`를 읽기 전용 적대적 재검토합니다.
2. P0/P1이 없으면 사용자가 실제 GitLab 반영·실행 여부를
   승인합니다.
3. 사용자 승인 후에만 CI Lint, 외부 보호 설정, 실제 pipeline을
   확인합니다.

## 8. 중단 조건

- 제품 clone을 blobless로 되돌리면서 lazy fetch만 허용하는 변경
- request·proposal clone을 불필요하게 전체 clone으로 확대
- `GIT_NO_LAZY_FETCH` 또는 `SOURCE_BLOBS_UNAVAILABLE` 완화
- exit 2를 Q9 결정 없이 0으로 변환
- 실제 GitLab 미실행 상태를 운영·배포 완료로 표시
