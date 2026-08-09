# Candidate CLI · phase-status · watch-suggest 개발 인수인계

> 작성일: 2026-08-09 KST
>
> 개발 branch: `codex/candidate-activation-cli-20260809`
>
> 분기 기준: `c86632a` (`codex/phase-bundling-safety-fix-20260808`의 문서 commit)
>
> **예행연습 branch에 merge하지 않았습니다.** 원격 push까지만 수행했습니다.

## 1. 구현 commit

| commit | 범위 |
|---|---|
| `49e746f` | Candidate lock 준비·승인·활성화·점검 CLI 4종 |
| `9c344ad` | `phase-status`의 다음 행동을 저장된 phase로 분기 |
| `fdaf782` | `watch-suggest` 참조 역색인·삭제 finding·timeout·단독 재실행 |

요청서의 "독립 commit 분리" 조건에 따라 Candidate CLI, phase-status, watch-suggest를
서로 다른 commit으로 나눴습니다.

## 2. 변경 파일

| 파일 | 목적 |
|---|---|
| `harness/run_phase_bundle.py` | `candidate-prepare/-approval-template/-activate/-verify`, `watch-suggest` 하위 명령. 공통 guarded writer, `CandidatePolicyBlock` |
| `harness/om_workflow.py` | 위 5개 공개 명령, `[준비 n/3]`·`[점검]`·`[watch-suggest]` 한국어 출력, phase-status 분기 |
| `harness/acgh/watch_suggest.py` | 참조 역색인 기반 재작성, 삭제 finding, cache, timeout 보고 |
| `harness/acgh/gitprim.py` | `blob_batch` (git cat-file --batch) |
| `harness/acgh/phase.py` | `validated_timeout`, premerge catalog의 `gate_timeout`·cache·harness_version 전달, watch-suggest 미완료 시 analysis_error |
| `harness/tests/test_candidate_activation.py` | 신규 41건 |
| `harness/tests/test_watch_suggest_scale.py` | 신규 23건 |
| `harness/tests/test_phase_cli.py` | premerge status 출력 회귀 1건 추가 |

## 3. 검증 결과

```bash
PYTHONPATH=harness:. ./.venv/bin/python -m pytest \
  harness/tests/test_candidate_activation.py \
  harness/tests/test_watch_suggest_scale.py \
  harness/tests/test_watch_suggest.py \
  harness/tests/test_phase_cli.py -o addopts='' -q
```

- Candidate CLI 집중: `41 passed`
- watch-suggest 집중: `25 passed` (신규 23 + 기존 2)
- 전체 harness: `631 passed, 38 skipped`, 실패 0 (분기 시점 566 → 631)

### 3.1 실제 저장소 성능·정확성

읽기 전용으로 사용자 clone `~/om-work/OpenMetadata`에서 측정했습니다.

| 항목 | 값 |
|---|---|
| 입력 | base `afcb2d2c…` · target `2763bf97…` · candidate `8ac18ad0…` |
| 등록 묶음 | `om-temp-1.13.1` (BANK-OM-001~007) |
| 이전 결과 | `TimeoutError: gate watch-suggest exceeded 300.0s` |
| 현재 결과 | `complete=True`, **1.06초** |
| 변경 경로 | 1,705 |
| 색인한 커스텀 파일 | 69 |
| 제안 | 283건 (정밀도 개선 전 614건) |
| 삭제 감시 경로 | 1건 — BANK-OM-004 `EntityUtils.tsx`, 후보 26건 (개선 전 68건) |
| 후보 예시 | `EntityBreadcrumbPureUtils.ts`, `EntityDisplayUtils.tsx` 등 `Entity*` 계열 |

요청서 §7의 목표(300초 이내, 60초 이내)를 모두 만족합니다.

## 4. 사람과 도구의 경계

도구가 하는 일과 하지 않는 일을 명령별로 고정했습니다.

- `candidate-prepare`: lock을 배치하고 근거 result와 교차 검증합니다. 승인하지 않습니다.
- `candidate-approval-template`: 양식만 만듭니다. `approval_confirmed`를 `true`로 쓰지
  않으므로 **이 명령만으로는 활성화 가능한 승인이 만들어지지 않습니다.**
- `candidate-activate`: 넘겨받은 승인을 다시 검증하고, 승인 파일을 byte 그대로 보관합니다.
- `candidate-verify`: 읽기 전용입니다. 파일을 고치거나 지우지 않습니다.
- `watch-suggest`: 후보를 제안할 뿐 Manifest를 수정하지 않습니다.

## 5. 해결하지 못한 항목

1. **승인자의 실제 조직 권한은 검증하지 않습니다.** CLI는 형식과 digest 결속까지만
   확인합니다. `candidate-locks/`를 보호 branch·CODEOWNERS로 묶는 저장소 정책이
   별도로 필요합니다. 활성화 성공 출력에 이 경계를 매번 표시합니다.
2. **Registry와 lock의 저장소 표기 불일치가 실제로 남아 있습니다.**
   `customization-registry.yaml`의 `source.repository`는 `easyseop/OM_TEMP`이고
   Candidate lock은 `easyseop/OpenMetadata`입니다. `upstream_sha`는 일치하므로
   차단하지 않고 `--allow-repository-mismatch` 명시 확인으로 처리했습니다.
   Registry를 정정할지는 담당자 결정 사항입니다.
3. **예행연습 clone의 수동 생성 파일은 그대로 두었습니다.** 새 CLI로 덮어쓰거나
   삭제하지 않았습니다. 예행연습 종료 후 `candidate-verify`로 확인한 뒤 정식화할지
   재생성할지 결정하면 됩니다. 현재 그 파일들은 git untracked 상태입니다.
4. **watch-suggest 제안 283건은 여전히 많습니다.** 커스텀이 핵심 파일(`Entity.java`,
   `CollectionDAO.java`)을 실제로 참조하기 때문이며 오탐만은 아닙니다. 우선순위
   정렬이나 BANK-OM별 상위 N 표시는 추가 개발 항목으로 남깁니다.
5. **`.sql`을 참조 근거에서 제외했습니다.** migration 파일이 Java 클래스명을 담고
   있어도 코드 참조로 보지 않습니다. `upgrade-watch`의 감시 대상에서는 빠지지
   않습니다.
6. **실제 1.13.2 vendor merge·postmerge·build artifact·Runtime Contract·운영 배포는
   이번 범위가 아닙니다.**

## 6. 예행연습과의 관계

- 이 branch를 `codex/phase-bundling-safety-fix-20260808`에 merge하지 않았습니다.
- `harness/om_workflow.py`가 `harness_version` 해시 대상이므로, 이 변경을 적용하면
  현재 premerge 증거(`sha256:3c4d5392…`)와 다른 검사기 version이 됩니다.
- 예행연습 종료 후 적용하면 Candidate 선택부터 premerge·postmerge 증거를 새
  harness_version으로 다시 생성해야 합니다.

## 7. 다음 실행 명령

예행연습 종료 후, 적용을 결정했을 때:

```bash
./.venv/bin/python harness/om_workflow.py candidate-verify --version 1.13.1
```

현재 배치된 파일이 CLI 산출물과 같은지부터 확인하고, 그 결과에 따라 정식화 또는
재생성을 결정합니다.
