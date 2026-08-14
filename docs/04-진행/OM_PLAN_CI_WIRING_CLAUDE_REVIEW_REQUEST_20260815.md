# Claude 적대 검토 요청 — `/om-plan` 보호 CI 배선

## 1. 검토 대상

- 저장소: `easyseop/openmetadata-test`
- branch: `codex/om-plan-ci-wiring-20260815`
- 구현 commit: `9bc4cd2c3dca064d2d181b4e500415e18c336e9c`
- tree: `ff83a8492ccbd4abc0e5448945d2bf6c614cb6ab`
- E-hardening 기준: `1f02e1d3a0c77b9d62f5763835d91cbadc1d5804`

우선 다음 파일을 읽어라.

1. `.github/workflows/om-plan-ci.yml`
2. `harness/ci/om_plan_ci.py`
3. `harness/tests/test_om_plan_ci.py`
4. `harness/acgh/plancore/preflight.py`
5. `harness/acgh/plancore/validate.py`
6. `docs/04-진행/OM_PLAN_CI_WIRING_OPERATIONS_20260815.md`
7. `docs/04-진행/CODEX_CURRENT_HANDOFF.md`

## 2. 검토 방식

- 읽기 전용 적대 검토다. 저장소·workflow·문서·Git 상태를 수정하지 마라.
- 구현 설명을 사실로 가정하지 말고 workflow 그래프와 실행 반례로 확인하라.
- 실제 GitHub environment가 설정됐거나 workflow가 실행됐다고 추정하지 마라.
- P0/P1은 재현 명령·입력·기대 결과·실제 결과를 함께 제시하라.
- Q3·Q6·Q7·Q8·Q9를 임의로 결정하지 마라.

## 3. 반드시 공격할 수용 조건

### A. protected digest 분리

1. `input_lock_digest`가 repository file이나 proposal artifact에서 유도되는 경로가
   없는지 확인하라.
2. untrusted proposal job이 preflight job output, receipt, expected 값을 읽을 수
   있는지 공격하라.
3. proposal ref가 workflow 파일·input-lock·facts·가짜 digest를 함께 포함해도
   validate expected를 바꿀 수 없는지 확인하라.
4. job output 전달이 GitHub Actions 표현식이나 artifact 이름 충돌로 덮이는 경로가
   없는지 확인하라.

### B. 비신뢰 proposal 실행 격리

1. path traversal, absolute path, symlink, nested symlink, unsupported extension,
   기존 비어 있지 않은 output을 공격하라.
2. proposal checkout의 `.github/workflows`, Python, shell 파일이 실행·import되거나
   artifact에 포함되는지 확인하라.
3. proposal data가 checker `PYTHONPATH`, dependency install, shell command를
   오염할 수 있는지 확인하라.
4. proposal job이 `preflight`를 직접 need하지 않더라도 간접적으로 지문을 볼 수
   있는 GitHub context가 있는지 확인하라.

### C. fresh validation만 신뢰

1. `validation-result.json` 선주입, 변조, completed-run denial을 시도하라.
2. stdout verdict와 process exit를 서로 다르게 만들어 fail-closed인지 확인하라.
3. `approval=2`가 자동 성공 0으로 취급되는 경로가 없는지 확인하라.
4. downloaded run의 옛 absolute path와 `.plan-active` marker를 이용해 재계산을
   건너뛸 수 있는지 확인하라.
5. validate runner에서 제품·검사기 repo를 바꿔치기하거나 dirty 상태로 만들었을 때
   fresh recomputation이 잘못된 review_ready를 내는지 공격하라.

### D. upgrade 공식 문서 결속

1. official document snapshot, `official-doc-sources.yaml`, facts를 함께 바꾸고
   기존 expected로 통과할 수 있는지 E06을 CI 이동 경로까지 확장해 확인하라.
2. URL document와 repository-relative document가 runner 이동 뒤 서로 다르게
   처리되어 digest 재계산을 우회하는지 확인하라.

### E. 사람 intent review 경계

1. default branch가 아닌 workflow dispatch가 all-skipped green처럼 오독될 수 있는지
   확인하라.
2. `environment.deployment: false`, required reviewers, prevent self-review,
   branch policy, environment variable의 실제 GitHub 의미를 확인하라.
3. environment가 이름만 자동 생성되고 보호 규칙이 없는 상태에서
   `OM_PLAN_INTENT_REVIEW_ENFORCED`만 위조할 수 있는지 확인하라.
4. workflow 입력에 proposal ref가 이미 존재하므로 LLM 생성 시점이 사람 intent review
   뒤였다는 사실은 이 workflow가 보증하지 않는다는 문서 경계가 충분한지 판정하라.

## 4. 확인할 회귀

다음 로컬 결과가 재현되는지 확인하라.

```bash
PYTHONDONTWRITEBYTECODE=1 \
/Users/seop/om-work/openmetadata-test/.venv/bin/python -m pytest \
  -p no:cacheprovider \
  harness/tests/test_plan_workflow.py \
  harness/tests/test_om_workflow.py \
  harness/tests/test_plan_boundary.py \
  harness/tests/test_om_plan_ci.py -q
```

- 선언 결과: 108 passed, failure 0, error 0, skip 0

```bash
PYTHONDONTWRITEBYTECODE=1 \
/Users/seop/om-work/openmetadata-test/.venv/bin/python -m pytest \
  -p no:cacheprovider harness/tests -q
```

- 선언 결과: 527 tests, failure 0, error 0, 37 skipped

## 5. 출력 형식

1. 사실 정정
2. P0 / P1 / P2
3. 수용 조건 A·B·C 각각 `성립 / 불성립 / 실제 CI 설정 전 미검증`
4. 공격 시나리오별 재현 결과
5. test가 놓친 반례
6. 실제 GitHub 환경 설정이 있어야만 확인 가능한 항목
7. 최종 판정: `채택 / 수정 후 재검토 / 폐기`

마지막에 구현 파일을 수정하지 않았다는 사실과 검토한 commit·tree를 다시 적어라.
