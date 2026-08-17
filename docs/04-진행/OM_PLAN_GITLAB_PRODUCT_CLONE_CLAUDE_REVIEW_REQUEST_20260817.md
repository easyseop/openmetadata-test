# Claude 재검토 요청 — GitLab 제품 clone blob 확보

## 1. 목적

commit `ef48a8eee0b3c6b99f2fcd0d4f8f5d70ebc57d3a`가 GitLab CI의
제품 clone과 `/om-plan` 소스 blob fail-closed 정책 사이의 충돌을
정확히 해소했는지 읽기 전용으로 적대적 검토합니다.

## 2. 검토 대상

| 항목 | 값 |
|---|---|
| repository | `easyseop/openmetadata-test` |
| branch | `codex/om-plan-gitlab-product-clone-20260817` |
| 기존 GitLab CI 기준 | `ee9f033aea9446e19a0b7420c85a8eb8bd70dc44` |
| 구현 commit | `ef48a8eee0b3c6b99f2fcd0d4f8f5d70ebc57d3a` |
| 구현 tree | `c34fdae790602c139cb6868b34b1d6ab511d8797` |

정확한 diff:

```bash
git diff ee9f033aea9446e19a0b7420c85a8eb8bd70dc44..ef48a8eee0b3c6b99f2fcd0d4f8f5d70ebc57d3a -- \
  .gitlab-ci.yml \
  harness/tests/test_om_plan_gitlab_ci.py
```

## 3. 구현자가 선택한 방법

- preflight와 validate의 제품 clone 2곳에서만 `--filter=blob:none`을
  제거했습니다.
- request·proposal source clone의 `--filter=blob:none --no-checkout`은
  변경하지 않았습니다.
- `GIT_NO_LAZY_FETCH=1`과 `SOURCE_BLOBS_UNAVAILABLE` 차단은
  변경하지 않았습니다.
- blobless 실패와 full clone 성공을 같은 collector로 대조하는
  회귀 test를 추가했습니다.

## 4. 검증 결과

| 범위 | 결과 |
|---|---|
| GitLab·CI·plan 집중 회귀 | 116 passed, 0 failed, 0 skipped |
| 전체 harness | 536 passed, 0 failed, 37 skipped |
| `git diff --check` | pass |

집중 회귀는 기존 cross-runner 종단 test를 포함합니다. 정상 계획은
preflight→fresh validate에서 `review_ready`(내부 verdict `approval`, exit 2)에
도달합니다.

실제 GitLab CI Lint와 pipeline은 사용자 승인 전이므로 실행하지
않았습니다. 운영 통과로 추정하지 마십시오.

## 5. 필수 검토 질문

1. 제품 clone 직후, pinned base·target commit의 필요 blob이 지연 fetch
   없이 로컬에 존재하는가?
2. `GIT_NO_LAZY_FETCH=1`과 `SOURCE_BLOBS_UNAVAILABLE` fail-closed가
   어떤 경로로든 완화되지 않았는가?
3. request·proposal clone은 정확히 기존 부분 clone으로 남았는가?
4. 정적 test가 제품과 data clone 경계를 잘못된 문자열 비교로
   통과시키는 반례가 있는가?
5. blobless 실패 test와 full clone 성공 test가 실제 collector 경계를
   증명하는가, 아니면 fixture와 실제 GitLab 동작 사이에 P0/P1 차이가
   있는가?
6. 기존 expected digest·E-hardening·proposal 격리·fresh validation·`.pyc`
   방어·exit 2 의미가 변경되지 않았는가?
7. 전체 clone으로 인한 성능·디스크 비용 외에, 정확성이나
   보안성을 깨는 부작용이 있는가?

## 6. 판정 형식

다음 순서로만 보고하십시오.

1. 사실 정정
2. P0 / P1 / P2 발견 사항
3. 각 발견의 정확한 파일·행·실행 반례
4. 수용 기준 1∼5 개별 판정
5. 빠진 회귀 test
6. 최종 판정: 채택 / 수정 후 재검토 / 기각

근거 없는 동의는 제외하고, 실제 GitLab pipeline 미실행 부분은
명확히 `미검증`으로 남기십시오. 저장소·코드·문서를 수정하지 마십시오.

## 7. Claude에게 전달할 한 줄

```text
docs/04-진행/OM_PLAN_GITLAB_PRODUCT_CLONE_CLAUDE_REVIEW_REQUEST_20260817.md를 처음부터 끝까지 읽고, 지정된 commit만 읽기 전용으로 적대적 검토해줘. 실제 GitLab pipeline은 사용자 승인 전이므로 실행하지 마.
```
