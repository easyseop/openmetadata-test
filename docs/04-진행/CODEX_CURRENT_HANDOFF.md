# 현재 작업 인수인계 — `/om-plan` 보호 CI와 P2-1 수정

> 마지막 갱신: 2026-08-15 01:40 KST
> 현재 작업: checker 지문에 Python bytecode cache가 섞이는 P2-1 수정
> 상태: 구현 commit·로컬 회귀 검증 완료, Claude 재검토 대기

## 1. 이번 결론

서로 다른 runner에서 생긴 `__pycache__`·`.pyc` 내용이 checker catalog 지문에
포함되어, 소스가 같아도 final validation이 `analysis_error`로 끝나는 문제가
재현됐습니다.

`directory_digest()`가 다음 Python bytecode 산출물만 지문에서 제외하도록
수정했습니다.

- 경로 구성요소가 `__pycache__`인 파일
- 확장자가 `.pyc` 또는 `.pyo`인 파일

symlink 거부 검사는 제외 판단보다 먼저 실행합니다. 따라서 symlink 보안 경계는
그대로이고, `.py` 등 실제 checker 소스 변경도 계속 지문 불일치로 차단됩니다.
`_checker_catalog_digest()`는 기존처럼 `directory_digest()`를 호출하므로 별도
예외 로직 없이 같은 규칙을 사용합니다.

## 2. 저장소·branch·commit

| 항목 | 값 |
|---|---|
| 저장소 | `easyseop/openmetadata-test` |
| 기준 로컬 경로 | `/Users/seop/Documents/Codex/om-plan-claude-review-20260814/openmetadata-test` |
| 검증 작업 경로 | `/Users/seop/Documents/Codex/2026-07-25/sites-plugin-sites-openai-bundled/work/om-plan-pyc-fix` |
| branch | `codex/om-plan-ci-wiring-20260815` |
| P2-1 수정 기준 | `649454a403b08ecb7b98316a77b1cf3e471da1d4` |
| CI 배선 구현 | `9bc4cd2c3dca064d2d181b4e500415e18c336e9c` |
| P2-1 구현 | `7aaa18f53e47a0a98185cfcb27f22966a637c025` |

최종 전달 시 `git status --short` 출력은 없으며 working tree는 clean입니다.

## 3. 변경 내용

- `harness/acgh/plancore/paths.py`
  - bytecode cache만 directory 지문에서 제외
  - symlink 거부와 일반 소스 지문 계산은 유지
- `harness/tests/test_plan_paths.py`
  - `__pycache__`, `.pyc`, `.pyo` 추가로 지문이 바뀌지 않는지 확인
  - 실제 `.py` 소스 변경으로 지문이 바뀌는지 함께 확인
- `harness/tests/test_om_plan_ci.py`
  - 서로 다른 runner cache가 있어도 fresh validation이 종료 코드 2와
    `review_ready`에 도달하는 종단 회귀 test
  - checker 소스를 변조하면 종료 코드 3과 `analysis_error`가 유지되는 종단 test

이번 범위에서는 verdict enum, 종료 코드 정책, 제품 코드, registration, workflow,
default branch 설정을 변경하지 않았습니다.

## 4. 재현과 검증 결과

모든 수정 후 검증은 `PYTHONDONTWRITEBYTECODE`를 설정하지 않은 상태에서
실행했습니다.

### 수정 전 재현

- 기존 cross-runner test가 종료 코드 2 대신 3을 반환
- 사유: `recomputed input lock does not match the stored lock`

### 수용 기준 전용 test

- 3 passed, failure 0, error 0, skip 0
- cache 산출물 무시, cross-runner 성공, 실제 checker 소스 변조 차단을 확인

### 집중 회귀

- 109 tests, failure 0, error 0, skip 0
- JUnit: `/private/tmp/om-plan-pyc-focused-20260815.xml`

### 전체 harness

- 529 tests, failure 0, error 0, 37 skipped
- JUnit: `/private/tmp/om-plan-pyc-harness-20260815.xml`
- 37 skip은 기존 OM mirror·Runtime 등 환경 의존 항목입니다.

`git diff --check`도 통과했습니다.

## 5. 수용 기준 판정

| 기준 | 결과 | 근거 |
|---|---|---|
| cache 억제 없이 cross-runner 통과 | 충족 | 종료 코드 2, `review_ready` |
| 회귀 test 추가 | 충족 | unit 1건, cross-runner 종단 2건 |
| 실제 소스 위조 탐지 유지 | 충족 | 종료 코드 3, `analysis_error`와 지문 불일치 사유 |
| 기존 보안 경계 유지 | 충족 | symlink 검사를 먼저 수행하고 전체 harness 통과 |

## 6. 의도적으로 결정하지 않은 것

- P2-2 green/red 표시 반전
- Q3, Q6, Q7, Q8, Q9
- GitHub environment와 required reviewer 설정
- 실제 GitHub Actions 실행
- default branch merge, release, deploy

P2-2는 GitHub 설정과 Q9 결정이 필요한 별도 작업입니다. 이번 patch에 포함하지
않았습니다.

## 7. 다음 실행 순서

1. 기준 로컬 경로의 같은 feature branch에 P2-1 commit을 동기화합니다.
2. Claude가 구현 commit `7aaa18f53e47a0a98185cfcb27f22966a637c025`를
   읽기 전용으로 재검토합니다.
3. 재검토 핵심은 “cache 억제 없이 통과하면서 실제 소스 위조는 여전히
   `analysis_error`로 잡히는가”입니다.
4. P0/P1이 없을 때만 사용자가 원격 push나 실제 Actions 실행 여부를 결정합니다.

현재 정확한 다음 명령:

```bash
git show --stat --oneline 7aaa18f53e47a0a98185cfcb27f22966a637c025
git diff 649454a403b08ecb7b98316a77b1cf3e471da1d4..7aaa18f53e47a0a98185cfcb27f22966a637c025 -- \
  harness/acgh/plancore/paths.py \
  harness/tests/test_plan_paths.py \
  harness/tests/test_om_plan_ci.py
```

## 8. 중단 조건

- cache 외의 일반 소스나 정책 파일까지 지문에서 제외함
- symlink 거부를 우회함
- 실제 checker 소스 변경이 `analysis_error`가 아닌 성공으로 끝남
- 종료 코드 2를 자동 성공 0으로 바꿈
- P2-2 또는 미결정 Q 항목을 이번 수정에 섞음
- 실제 workflow 미실행 상태를 운영 완료 또는 최종 PASS로 표시함
