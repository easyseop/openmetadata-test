# OM_TEMP 1.13.2 최종 검사 및 승인 가이드

**전체 순서:** 10/11 · [전체 목차](./OM_TEMP_1.13.1_1.13.2_예행연습_전체목차.html)

> 시작 조건: `codex/om-1.13.2-merge-candidate`의 merge·충돌 해결이 완료돼야 합니다.  
> 종료점: 1.13.2 버전용 등록자료와 실행 가능한 검사 결과를 같은 **1.13.2 업그레이드 후보 SHA**에 묶고, 미실행 검사를 명시합니다.  
> 이 문서에서 하지 않는 일: 미실행 test를 PASS로 간주, 검증 tag·release branch 생성.

**문서 이동:** [← 이전 — vendor merge·충돌 해결](./OM_TEMP_1.13.2_vendor_merge_및_충돌해결_가이드.html) · [다음 — 검증 tag·release branch →](./OM_TEMP_1.13.2_검증tag_및_release브랜치_가이드.html)

## 공통 경로 설정

이 페이지의 명령을 실행할 터미널에서 검사기 저장소로 이동한 뒤 공통 경로를 불러옵니다. 다른 컴퓨터에서는 clone 위치만 바꾸면 됩니다.

```bash
cd <검사기-저장소-clone-경로>
```

```bash
source harness/rehearsal_env.sh
```

`OM_TEST_REPO`는 검사기 저장소, `OM_CODE_REPO`는 OpenMetadata 코드 작업 폴더, `KB_SOURCE_REPO`는 실제 커스터마이징 원본 폴더를 가리킵니다. 새 터미널을 열면 다시 실행합니다.

## 1. 최종 검사의 입력 관계

```text
1.13.2 업그레이드 후보 SHA
  ├─ 1.13.2 Registry·Manifest·Contract
  ├─ 공용 경로·공용 코드 정의
  ├─ candidate lock
  ├─ 등록·소스·위험 검사 결과
  ├─ build·Contract·patch-kill·typecheck 결과
  └─ 담당자 승인
          ↓ 모두 같은 SHA·digest
       승격 가능 여부 판단
```

> **\*참고 — 검사 대상 lock(`candidate lock`)**은 이번에 검사할 1.13.2 업그레이드 후보 commit SHA·Git tree·공식 1.13.2 commit을 한 묶음으로 고정한 정보입니다. 검사 도중 branch에 commit이 추가되면 기존 결과를 재사용하지 못하게 합니다.

> **\*참고 — 결과 digest**는 검사 결과의 판정·입력·근거를 해시한 값입니다. 결과 파일이 승인 뒤 바뀌었는지 확인할 때 사용합니다.

```bash
git -C "$OM_CODE_REPO" switch codex/om-1.13.2-merge-candidate
```

```bash
git -C "$OM_CODE_REPO" status --short
```

두 번째 명령은 빈 출력이어야 합니다. 다른 branch 또는 미커밋 변경에서 생성한 결과는 최종 검사 증거로 사용하지 않습니다.

`<실행ID>`는 같은 1.13.2 업그레이드 후보 SHA에 대해 등록 변경부터 최종 검사까지 수행하는 한 번의 시도를 나타냅니다. 예: `20260805-final-01`. 입력 코드·등록자료를 고친 뒤 다시 시작하면 `...-02`처럼 새 ID를 사용합니다.

```bash
mkdir -p "$OM_TEST_REPO"/evidence/om-1.13.2-final-<실행ID>
```

**산출물:** 등록 변경 제안서·승인서·apply 결과와 모든 최종 검사 결과를 함께 보관할 폴더.

## 2. 1.13.2 버전용 등록자료 준비

1.13.1 등록자료는 1.13.1 기준 이력으로 보존합니다. 1.13.2는 새 폴더에서 별도로 갱신합니다. 아래 복사는 **7번 페이지에서 승인·apply까지 끝난 1.13.1 등록 폴더에만** 실행합니다. 과거 재현 초안이나 `UNASSIGNED/pending` 상태를 복사해서는 안 됩니다.

### 2-1. 기준 입력만 복사

```bash
cd "$OM_TEST_REPO"
```

```bash
mkdir -p harness/registrations/om-temp-1.13.2/manifests
```

```bash
cp harness/registrations/om-temp-1.13.1/customization-registry.yaml \
  harness/registrations/om-temp-1.13.1/contracts.yaml \
  harness/registrations/om-temp-1.13.1/repository-layout.yaml \
  harness/registrations/om-temp-1.13.1/sensitive-zones.yaml \
  harness/registrations/om-temp-1.13.1/shared-path-owners.yaml \
  harness/registrations/om-temp-1.13.1/shared-code-definitions.yaml \
  harness/registrations/om-temp-1.13.1/source-snapshot-path-owners.yaml \
  harness/registrations/om-temp-1.13.2/
```

```bash
cp harness/registrations/om-temp-1.13.1/manifests/*.yaml \
  harness/registrations/om-temp-1.13.2/manifests/
```

검사 결과 JSON, 등록 변경 제안서(`proposal.yaml`), 승인서, 검사 대상 lock(`candidate lock`)은 복사하지 않습니다. 이들은 1.13.1 SHA에 묶인 실행 산출물이기 때문입니다.

:::details 복사하는 파일과 복사하지 않는 파일

| 분류 | 예 | 이유 |
|---|---|---|
| 복사 후 1.13.2 기준으로 검토 | Registry·Manifest·Contract·경로 정책·공용 코드 정의 | 1.13.1에서 승인한 기준을 새 버전 변경안의 출발점으로 사용 |
| 복사 금지 | `proposal/`, 승인서, `*-results.json`, 검사 대상 lock | 특정 1.13.1 commit과 한 번의 실행에 묶인 결과이므로 1.13.2에 재사용 불가 |
| 필요할 때 별도 준비 | `patch-kill-plan.yaml`, runtime 계획 | 실제 1.13.2 test와 제거 실험 범위를 사용자 승인 후 작성 |

:::

### 2-2. 1.13.2 plan 생성

plan 실행 전에 T42 영향표와 merge diff를 대조합니다. 공용 코드의 실제 정의가 바뀌었으면 `shared-code-definitions.yaml`의 기대 조각·값을 사용자가 다시 승인하고, 정상 업무 동작이나 필수 test가 바뀌었으면 `contracts.yaml`을 사용자가 수정합니다. 준비도구는 이 업무 의미를 자동으로 추측하지 않습니다.

```bash
./.venv/bin/python harness/om_workflow.py plan \
  --repo "$OM_CODE_REPO" \
  --version 1.13.2 \
  --fork-ref official/om-1.13.2 \
  --custom-ref codex/om-1.13.2-merge-candidate \
  --output evidence/om-1.13.2-final-<실행ID>/proposal
```

준비도구가 commit·현재 변경 경로·공식 1.13.2 기준 변화를 제안합니다. Contract의 업무 정상 조건과 공용 코드 정의는 자동으로 새 의미를 추측하지 않습니다. `READY`, `REVIEW_REQUIRED`, `BLOCKED`, `ANALYSIS_ERROR`의 뜻과 승인서 작성 예시는 7번 페이지의 같은 절차를 따릅니다.

### 2-3. 승인·apply

```bash
./.venv/bin/python harness/om_workflow.py approval-template \
  --proposal evidence/om-1.13.2-final-<실행ID>/proposal/proposal.yaml \
  --output evidence/om-1.13.2-final-<실행ID>/registration-approval.yaml
```

사용자는 T42 영향표와 충돌 해결 근거를 보며 Manifest 감시 경로, 코드 정의, Contract 변경 여부를 승인합니다.

```bash
./.venv/bin/python harness/om_workflow.py apply \
  --repo "$OM_CODE_REPO" \
  --version 1.13.2 \
  --proposal evidence/om-1.13.2-final-<실행ID>/proposal/proposal.yaml \
  --approval evidence/om-1.13.2-final-<실행ID>/registration-approval.yaml \
  --result evidence/om-1.13.2-final-<실행ID>/registration-apply-result.json
```

## 3. 로컬에서 바로 실행 가능한 검사

### 3-1. 등록자료 연결 검사

```bash
./.venv/bin/python harness/om_workflow.py validate \
  --repo "$OM_CODE_REPO" \
  --version 1.13.2 \
  --output evidence/om-1.13.2-final-<실행ID>/registration-validation-results.json
```

### 3-2. 소스 검사 묶음

```bash
./.venv/bin/python harness/om_workflow.py source \
  --repo "$OM_CODE_REPO" \
  --version 1.13.2 \
  --output evidence/om-1.13.2-final-<실행ID>/source-gate-results.json
```

현재 묶음은 **T25, T26, T60-I, T30, T31, T40, T41, T93**을 실행합니다. Registry가 공용 코드 정의 파일을 선언했으면 공용 파일 ID별 코드 정의 검사도 마지막에 포함합니다. **T32는 이 묶음에 포함되지 않습니다.** T32 구현은 별도 모듈에 있으므로 실제 실행 연결이 추가되기 전에는 `미실행`으로 기록합니다.

:::details 소스 검사 결과 예시

```json
{"name":"vendor-ancestry","verdict":"pass","reasons":["approved official target is an ancestor"]}
```

공식 1.13.2 commit이 업그레이드 후보 이력에 포함된 경우입니다.

```json
{"name":"implementation-drift","verdict":"block","reasons":["BANK-OM-002: undeclared changed path ..."]}
```

실제 변경 파일이 Manifest 범위에 빠져 있을 때 발생합니다. 코드 또는 Manifest의 ID 소유 관계를 바로잡고 다시 실행합니다.

```json
{"name":"required-test-implementations","verdict":"analysis_error","reasons":["test selector cannot be resolved"]}
```

Contract가 가리킨 test 파일·이름을 찾지 못하거나 읽을 수 없을 때 발생합니다. test 이름을 임의 승인하지 않고 실제 구현을 확인합니다.

:::

### 3-3. 공용 파일 ID별 코드 정의

```bash
PYTHONPATH=harness ./.venv/bin/python -m acgh.shared_code \
  --repo "$OM_CODE_REPO" \
  --candidate codex/om-1.13.2-merge-candidate \
  --owners harness/registrations/om-temp-1.13.2/shared-path-owners.yaml \
  --definitions harness/registrations/om-temp-1.13.2/shared-code-definitions.yaml \
  --output evidence/om-1.13.2-final-<실행ID>/shared-code-results.json
```

### 3-4. BANK-OM 제거 test

```bash
./.venv/bin/python harness/om_workflow.py patch-kill \
  --repo "$OM_CODE_REPO" \
  --version 1.13.2 \
  --run-id om-1.13.2-patch-kill-<실행ID> \
  --output evidence/om-1.13.2-final-<실행ID>/patch-kill-result.yaml
```

해당 BANK-OM 변경을 제거했는데 필수 test가 계속 통과하면 test가 그 기능을 검증하지 못하므로 `BLOCK`입니다. 1.13.2 폴더에 `patch-kill-plan.yaml`이 없으면 먼저 계획을 승인해야 하며, 없는 파일을 임의 생성해 통과시키지 않습니다.

:::details 3장 검사 결과가 달라지는 대표 경우

| 검사 | PASS 예 | BLOCK 예 | ANALYSIS_ERROR 예 | APPROVAL 가능 여부 |
|---|---|---|---|---|
| 등록자료 연결 검사 | Registry의 7개 ID가 Manifest·Contract와 모두 연결 | Registry에는 활성 ID가 있는데 Manifest가 없음 | YAML 문법 오류·필수 파일 읽기 실패 | 검사 항목별 구현에 따름; 이유를 확인 |
| 소스 검사 묶음 | 공식 계보·ID commit·변경 경로가 선언과 일치 | Manifest 밖의 실제 변경, 공식 계보 누락 | 필요한 Git object·test selector를 읽지 못함 | T41 등 담당자 판단이 필요한 gate에서 가능 |
| 공용 파일 코드 정의 | 114개 경로·ID 조합의 승인 코드·값이 모두 존재 | BANK-OM-002 정의만 삭제되거나 값이 다름 | 정의 YAML 오류·대상 파일을 읽지 못함 | 없음 |
| patch-kill | BANK-OM 변경을 제거하자 연결된 필수 test가 실패 | 변경을 제거해도 필수 test가 통과 | 제거 실험을 만들 수 없거나 test 실행기 오류 | 계획상 runtime 실험이 필요한 ID는 별도 대기 가능 |

`PASS` 예는 해당 검사 하나의 조건만 충족했다는 뜻입니다. 다른 검사 미실행이나 BLOCK을 덮어쓰지 않습니다.

:::

## 4. 실행 환경을 준비한 뒤 실행하는 검사

### 4-1. Contract runtime test

```bash
./.venv/bin/python harness/om_workflow.py runtime \
  --repo "$OM_CODE_REPO" \
  --version 1.13.2 \
  --artifact-digest sha256:<실제-배포파일-digest> \
  --run-id om-1.13.2-runtime-<실행ID> \
  --output-dir evidence/om-1.13.2-final-<실행ID>/runtime
```

API·브라우저·DB 주소가 없어 test가 skip되면 `환경 대기`입니다. 이는 PASS가 아닙니다. 실행기·입력 오류는 `analysis_error`, 환경은 정상인데 필수 업무 동작 test가 실패하면 `block`으로 구분합니다.

### 4-2. UI typecheck 기준선 비교

먼저 동일한 Node·Yarn 버전으로 공식 1.13.2 코드와 업그레이드 후보 코드의 로그를 각각 생성합니다. **현재 이 위키에는 로그 생성 명령이 확정돼 있지 않습니다.** OpenMetadata 1.13.2의 실제 package script와 실행 환경을 확인하기 전에는 아래 비교 명령으로 넘어가지 않습니다.

```bash
./.venv/bin/python harness/om_workflow.py typecheck \
  --upstream-log evidence/om-1.13.2-final-<실행ID>/official-typecheck.log \
  --candidate-log evidence/om-1.13.2-final-<실행ID>/candidate-typecheck.log \
  --upstream-exit <공식-종료코드> \
  --candidate-exit <후보-종료코드> \
  --output evidence/om-1.13.2-final-<실행ID>/typecheck-comparison.json
```

공식 코드에는 없던 TypeScript 오류가 업그레이드 후보에 생기면 `BLOCK`입니다. 공식과 후보 로그의 Node·Yarn 버전 또는 실행 명령이 다르면 비교 결과를 사용하지 않습니다.

### 4-3. build

Java·Maven·Node·Yarn 의존성이 준비된 동일 환경에서 공식 1.13.2 코드와 업그레이드 후보 코드를 각각 build합니다. 이 문서에는 아직 확정된 build 실행 명령이 없습니다. 동일 환경을 준비하지 못했거나 명령이 확정되지 않았으면 `환경 대기`로 기록하며 PASS로 표시하지 않습니다.

## 5. 현재 별도 실행 연동이 필요한 검사

| 검사 | 현재 구현 | 실제 예행연습에서 필요한 것 | 미충족 시 표현 |
|---|---|---|---|
| T32 최종 상태 | 판정 모듈 구현 | 현재 `source` 묶음 또는 별도 운영 CLI에 연결 | `미실행`, PASS 아님 |
| T90 업그레이드 차등 test | 결과 schema·판정 함수 구현 | CI 또는 담당자가 restore·migration·reindex·rollback 결과를 생성 | `미실행`, PASS 아님 |
| T91 검증·배포 대상 일치 | release lock 생성·검증 함수 구현 | 동일 업그레이드 후보·배포 파일·test 실행·승인 정보를 연결하는 운영 실행기 | `승격 대기` |
| 보안·라이선스·SBOM | 정책 구성에 따라 외부 도구 필요 | 조직이 승인한 scanner와 결과 파일 | `환경/정책 대기` |

> **\*참고 — T90 단계**는 `restore-production-snapshot`, `migration`, `reindex`, `rollback-drill` 등 담당자나 CI가 실행한 단계 결과가 모두 성공인지 판정합니다. T90 자체가 DB 복원이나 migration을 대신 실행하지 않습니다.

## 6. 결과를 읽는 공통 규칙

| verdict | 종료코드 | 해석 | 최종 승인 가능 여부 |
|---|---:|---|---|
| `pass` | 0 | 자동 조건 충족 | 다른 필수 검사도 충족해야 가능 |
| `approval` | 2 | 담당자 판단 필요 | 승인 근거를 결과 digest에 연결해야 가능 |
| `block` | 1 | 코드·등록자료·test 실패 | 수정·재실행 전 불가 |
| `analysis_error` | 3 | 입력·환경·분석을 신뢰할 수 없음 | 복구·재실행 전 불가 |

결과 형식은 실행기마다 다릅니다. `source-gate-results.json`처럼 `gates[].verdict`와 `reasons`를 기록하는 파일도 있고, 공통 결과 규격처럼 `expected_exit_code`와 `result_digest`까지 기록하는 파일도 있습니다. **모든 파일에 같은 필드가 있다고 가정하지 말고**, 각 파일에서 검사 대상 SHA 또는 lock, 판정, 이유를 확인합니다. 해당 실행기가 digest를 제공하면 승인 기록에도 함께 연결합니다.

### 6-1. 검사 카탈로그 전체 실행 위치

| 검사기 | 이번 vendor merge 예행연습에서의 실행 위치 | 현재 처리 |
|---|---|---|
| T93·T42·T51·T52 | 공식 1.13.2 병합 전 페이지의 `watch`·`risk` | 로컬 실행 가능 |
| T41·T43 | 병합 전 `risk`, 병합 후 최종 소스 검사 | 로컬 실행 가능 |
| T24·T25·T26·T29 | merge 계보·검사 대상 lock·기능 생존 | 현재 `source`는 T25·T26을 실행; T24·T29는 별도 연결 여부를 확인해 미실행을 기록 |
| T27 | 충돌 stage·해결 diff·승인 근거 | 충돌 발생 시 증거 작성 필요 |
| T30·T31·T32·T40·T50·T60 | Registry·Manifest·Contract·최종 소스 | `validate`·`source`는 T30·T31·T40·T60-I 등을 실행; T32·T50·T60 전체 연결은 결과의 실제 gate 목록으로 확인 |
| 공용 파일 ID별 코드 정의 | 공용 파일에서 ID별 승인 코드 생존 | 별도 `acgh.shared_code`로 실행 |
| T61 | BANK-OM 제거 후 필수 test 실패 확인 | `patch-kill` 계획·환경 필요 |
| T62 | test 결과와 업그레이드 후보·배포 파일 결속 | `runtime` 결과에서 확인 |
| T63 | 공식 코드·업그레이드 후보 UI typecheck 비교 | 두 로그 생성 환경 필요 |
| T70 | 검사 정책이 자기 변경을 완화하지 않는지 확인 | 정책 변경 PR의 CI에서 실행 |
| T80 | LLM 영향 검토 메모 | 보조 자료이며 verdict 없음 |
| T90 | restore·migration·reindex·rollback 결과 판정 | CI/운영 실행 결과 필요; 로컬 CLI 없음 |
| T91 | 검증 대상과 승격 대상 일치 | release lock 함수 구현; 운영 CLI 없음 |
| T13 | 여러 verdict를 가장 심각한 결과로 집계 | 검사 실행기·CI 내부 집계 |
| T20·T21·T22·T23·T11 | commit별 patch-replay·재현·lock | 선택 `patch-replay` 방식에서만 실행; 이번 기본 vendor merge에는 미적용 |

“전체 검사 완료”는 위 표의 모든 행이 PASS라는 뜻이 아닙니다. 이번 전략에 적용되는 검사는 실행·판정하고, 선택 전략 검사는 `미적용`, 환경이 필요한 검사는 `환경 대기`, 운영 CLI가 없는 검사는 `도구 연동 대기`로 각각 기록해야 합니다.

## 7. 최종 승인표

| 영역 | 결과 파일 | 업그레이드 후보 SHA 일치 | verdict·미실행 | 사용자 결정 |
|---|---|---|---|---|
| 등록 | `registration-validation-results.json` | 확인 |  |  |
| 소스 | `source-gate-results.json` | 확인 |  |  |
| 공용 코드 | `shared-code-results.json` | 확인 |  |  |
| patch-kill | `patch-kill-result.yaml` | 확인 |  |  |
| runtime Contract | `runtime/` | 확인 |  |  |
| typecheck·build | 비교 JSON·로그 | 확인 |  |  |
| T90 | CI 실행 결과 | 확인 |  |  |

:::details 승인표 작성 예시

| 영역 | 업그레이드 후보 SHA 일치 | verdict·미실행 | 사용자 결정 예시 |
|---|---|---|---|
| 소스 | 확인 | `pass` | 다음 검사 진행 |
| 공용 코드 | 확인 | `block` — BANK-OM-002 코드 조각 없음 | 코드 복원 후 전체 관련 검사 재실행 |
| runtime Contract | 확인 불가 | `환경 대기` | 배포 가능한 test 환경 준비 전 승격 금지 |
| T90 | 확인 불가 | `미실행` | CI 연동 전 승격 금지 |

:::

## 8. 완료 기준

- 1.13.2 등록자료와 모든 실행 결과가 같은 1.13.2 업그레이드 후보 SHA를 가리킵니다.
- `block`·`analysis_error`가 0개입니다.
- 모든 `approval`에 담당자·근거·대상 result digest가 있습니다.
- 필수 runtime·build·T90이 미실행이면 release 준비 완료로 표현하지 않습니다.
- 검증 tag에 사용할 정확한 1.13.2 업그레이드 후보 SHA와 배포 파일 digest가 확정됐습니다.

> **중단 조건:** 필수 검사가 미실행이거나 결과 대상 SHA가 다르면 다음 페이지에서 tag 또는 release branch를 만들지 않습니다.

**문서 이동:** [← 이전 — vendor merge·충돌 해결](./OM_TEMP_1.13.2_vendor_merge_및_충돌해결_가이드.html) · [다음 — 검증 tag·release branch →](./OM_TEMP_1.13.2_검증tag_및_release브랜치_가이드.html)
