# OM_TEMP 1.13.1 등록 승인·apply 및 기준 검사 가이드

**전체 순서:** 7/11 · [전체 목차](./OM_TEMP_1.13.1_1.13.2_예행연습_전체목차.html)

> 문서 성격: 사용자가 승인한 1.13.1 등록 변경안을 검사기 저장소에 반영하고, 업그레이드 전 기준 검사를 실행하는 문서입니다.  
> 시작 조건: `codex/om-1.13.1-id-series-upstream`의 111개 변경 경로와 7개 BANK-OM ID별 commit, 공용 코드 정의 114개 조합이 승인돼 있어야 합니다. 이전 단계와 같은 터미널을 사용하여 `OM_TEST_REPO`와 `OM_CODE_REPO`가 설정된 상태에서 시작합니다.
> 종료점: 공식 1.13.1과 커스텀 1.13.1의 실제 차이가 승인한 등록자료와 일치한다는 기준 결과를 보관합니다. 아직 1.13.2와 비교하거나 업그레이드 성공을 판정하지 않습니다.  
> 이 문서에서 하지 않는 일: 공식 1.13.2 준비, vendor merge, release branch 생성.

**문서 이동:** [← 이전 — 검사기 간단 학습](./OM_TEMP_1.13.1_1.13.2_검사기_간단_학습_가이드.html) · [다음 — 공식 1.13.2 준비·사전 영향 검사 →](./OM_TEMP_1.13.2_공식코드_준비_및_사전영향검사_가이드.html)

## 이전 단계의 경로 확인

이전 단계와 같은 터미널을 이어서 사용합니다. 경로를 다시 설정하지 않고, 아래 명령으로 두 값만 확인합니다.

```bash
printf '[검사기 저장소] %s\n[OpenMetadata 코드 저장소] %s\n' \
  "$OM_TEST_REPO" \
  "$OM_CODE_REPO"
```

**확인할 내용:** 두 항목 모두에 실제 폴더 경로가 나와야 합니다. 빈 값이 있으면 진행하지 말고, 예행연습 시작 단계에서 경로를 불러온 뒤 다시 확인합니다.

## 1. 이 단계가 필요한 이유

검사기는 코드만 보고 BANK-OM 기능의 의미를 알아내지 않습니다. 검사기가 읽을 등록자료가 서로 연결돼 있어야 “어느 ID가 어느 파일을 바꾸었고, 무엇이 반드시 남아 있어야 하며, 어떤 test로 정상 동작을 확인할지” 판단할 수 있습니다.

> **\*참고 — 등록자료**는 검사 전에 장기 보관하는 YAML·텍스트 기준 파일입니다. `plan` 결과나 검사 JSON처럼 한 번의 실행에서 만들어지는 결과 파일과 구분합니다.

### 1-1. 이 단계에서 무엇을 비교하는가

| 비교 | 기준 | 비교 대상 | 확인하는 내용 |
|---|---|---|---|
| 코드 차이 | 공식 OpenMetadata 1.13.1 branch | BANK-OM 변경이 적용된 커스텀 1.13.1 branch | 커스터마이징으로 달라진 파일과 코드가 무엇인지 |
| 등록 범위 | 위 두 branch에서 Git이 계산한 실제 변경 경로 | Manifest·Registry·공용 경로 자료 | 실제 변경 경로와 BANK-OM ID 선언이 같은지 |
| 필수 상태 | Manifest의 필수 경로·Contract·test 선언 | 커스텀 1.13.1의 실제 파일과 test 코드 | 업그레이드 전에 반드시 존재해야 할 기준 상태가 갖춰졌는지 |

여기서 공식 1.13.1은 비교 기준이고, 커스텀 1.13.1은 현재 상태를 확인할 대상입니다. 이 단계의 결과는 **1.13.2 업그레이드 전 기준점**으로 사용됩니다. 다음 단계에서 공식 1.13.2가 준비되면 이 기준점과 새 버전의 영향·병합 결과를 비교합니다.

> **이 단계의 종료 기준:** 초기 Registry·Manifest·Contract·공용 경로 자료를 생성하는 것만으로 끝나지 않습니다. 사용자가 내용을 승인하고, `apply`로 검사기 저장소의 등록자료에 반영하고, 실제 1.13.1 코드 차이와 등록자료가 일치한다는 기준 검사 결과까지 저장해야 종료됩니다.

## 2. BANK-OM ID 하나에 필요한 준비파일

| 파일 | 의미 | 생성·갱신 시점 | 읽는 검사·도구 | 불일치 결과 |
|---|---|---|---|---|
| `customization-registry.yaml` | 관리하는 BANK-OM ID, 담당자, Manifest·Contract 위치 | ID 최초 등록·상태 변경 | 준비도구, 등록 연결 검사 | 누락·중복은 `BLOCK`; YAML 오류는 `ANALYSIS_ERROR` |
| `manifests/BANK-OM-001.yaml` | ID의 변경 경로, 필수 경로, 감시 경로, Contract 연결 | 최초 등록·같은 ID 후속 commit | T31·T32·T40·T42·T50 | 실제 코드 범위와 다르면 `BLOCK` 또는 검토 필요 |
| `contracts.yaml` | 기능이 정상이라고 볼 업무 동작과 필수 test | 정상 조건·test 변경 | Contract 연결·필수 test 존재·runtime 검사 | 연결·test 누락은 `BLOCK` |
| `shared-path-owners.yaml` | 한 파일을 여러 BANK-OM ID가 사용할 때 관련 ID 전체 | 공용 파일 관계 변경 | 공용 경로 검사 | 한 ID가 빠지면 `BLOCK` |
| `shared-code-definitions.yaml` | 공용 파일 안에서 ID별로 반드시 남을 실제 코드 조각·구조화 값 | 공용 코드 정의 승인·변경 | 공용 파일 ID별 코드 정의 검사 | 승인한 정의가 없으면 `BLOCK` |
| `repository-layout.yaml` | OpenMetadata 코드 경로를 공식 코드·행내 확장·관리 경로로 분류 | 저장소 구조 변경 | 소스 경로 검사·T93 | 미분류 경로는 `ANALYSIS_ERROR` |
| `sensitive-zones.yaml` | 인증·DB migration 등 중요 경로의 추가 검토 규칙 | 중요 경로 정책 변경 | T41 | 승인 근거가 없으면 `BLOCK` 또는 `APPROVAL` |
| `source-snapshot-path-owners.yaml` | 1.13.1 등록자료를 처음 만든 commit에서 경로와 ID 관계 | 1.13.1 등록자료 최초 작성 | 등록 기준 코드 재구성 검사 | 기준을 재현할 수 없으면 `BLOCK` |

### 2-1. 서로 연결되는 방법

```text
Registry의 BANK-OM-001
  ├─ manifest → manifests/BANK-OM-001.yaml
  └─ contracts → CONTRACT-INSTANCE-CODE
                         │
Manifest의 assurance.contracts ─┘
                         │
contracts.yaml의 customization_ids → BANK-OM-001

Manifest.changed_paths ─┬─ shared-path-owners.yaml의 파일·ID 관계
                        └─ shared-code-definitions.yaml의 파일·ID별 실제 정의
```

`BANK-OM-001` 문자열이 Registry·Manifest·Contract에서 같아야 합니다. 같은 파일을 `BANK-OM-001`과 `BANK-OM-002`가 공유하면 공용 경로 파일에는 두 ID가 모두 있어야 하고, 공용 코드 정의에는 각 ID의 실제 정의가 따로 있어야 합니다.

### 2-2. 자동 생성 파일과 사람이 결정하는 파일

| 구분 | 파일·산출물 | 처리 주체 |
|---|---|---|
| 사람이 의미를 승인 | Registry의 제목·담당자, Manifest의 필수 범위, Contract의 정상 조건, 공용 코드 정의 | 사용자 |
| Git에서 자동 계산 | commit 목록, 현재 변경 경로, 파일 수, commit SHA | 준비도구 |
| 승인 전 제안 | `proposal/proposal.yaml` | 준비도구가 생성하고 사용자가 변경 내용을 검토 |
| 승인 결정 기록 | `registration-approval.yaml` | 준비도구가 양식을 만들고 사용자가 승인 근거 작성 |
| 승인 후 파생자료 | `commit-inventory.yaml`, `current-diff-paths.txt`, 적용 결과 | `apply` |
| 검사 실행 결과 | 등록 검사 JSON, 소스 검사 JSON, 공용 코드 검사 JSON | 각 검사기 |

> **\*참고 — `plan`**은 등록자료를 수정하지 않고 “무엇을 바꿀지” 제안합니다. **`apply`**는 같은 코드·같은 proposal·사용자가 승인한 승인서인지 다시 확인한 뒤 등록자료를 수정합니다.

## 3. 실행 전 입력 확인

### 3-1. 검사기 저장소로 이동

**실행 내용:** 위에서 확인한 검사기 저장소로 이동합니다. **산출물:** 이후 명령의 기준 작업 경로.

```bash
cd "$OM_TEST_REPO"
```

### 3-2. OpenMetadata 코드 branch와 작업 폴더 확인

```bash
git -C "$OM_CODE_REPO" switch codex/om-1.13.1-id-series-upstream
```

```bash
git -C "$OM_CODE_REPO" status --short
```

**정상 결과:** 빈 출력. 미커밋 변경이 있으면 `plan`을 실행하지 않습니다.

아래 명령은 이전 페이지 7-4 재검사에서 통과한 `codex/om-1.13.1-id-series-upstream` branch의 마지막 commit SHA를 출력합니다. 이 commit에는 BANK-OM-001부터 007까지 7개 commit이 순서대로 포함되어 있습니다.

이 commit은 **1.13.1 기준검사 대상 commit**입니다. 아직 1.13.2를 합친 코드는 아닙니다. 뒤에서 공식 1.13.2를 합쳐 만든 commit은 별도로 **1.13.2 업그레이드 후보 commit**이라고 부릅니다.

```bash
git -C "$OM_CODE_REPO" rev-parse codex/om-1.13.1-id-series-upstream
```

**현재 예행연습 출력:** `d952a83896940116d3d6022323ad76bfe60991e8`

이 값은 이전 4/11 가이드에서 만든 7개 BANK-OM commit 중 마지막 `BANK-OM-007` commit입니다. 앞의 6개 commit도 이 commit의 Git 이력에 포함돼 있습니다.

**확인 방법:** 출력된 SHA를 아래 두 결과의 SHA와 비교합니다. 점(`.`)으로 연결된 이름은 JSON 안쪽으로 들어가는 순서를 뜻합니다.

| 실제 이름 | 우리말 의미 |
|---|---|
| `proposal/` | 등록 변경안을 승인받기 전에 보관하는 폴더 |
| `proposal.yaml` | 어떤 등록자료를 어떻게 바꿀지 적은 **등록 변경 제안서** |
| `custom_sha` | 제안서를 만들 때 커스텀 branch가 가리키던 정확한 commit SHA |
| `source-gate-results.json` | 5-2 소스 검사에서 무엇을 검사했고 어떤 판정이 나왔는지 기록한 **소스 검사 결과 파일** |
| `candidate_lock` | 검사 도중 branch가 바뀌어도 대상이 섞이지 않도록, 검사할 commit과 공식 기준 commit을 묶어 고정한 정보 |
| `candidate` | `candidate_lock` 안에서 이번에 검사한 1.13.1 코드 정보 |
| `commit_sha` | 그 1.13.1 코드의 정확한 commit SHA |

따라서 `candidate_lock.candidate.commit_sha` 전체는 **“소스 검사가 대상으로 고정하고 실제로 검사한 1.13.1 코드의 commit SHA”**라는 뜻입니다.

세 SHA가 모두 같아야 `plan`과 소스 검사가 같은 코드를 사용한 것입니다. 하나라도 다르면 서로 다른 코드를 분석한 결과이므로 중단하고 새 실행 ID로 `plan`부터 다시 실행합니다.

### 3-3. 앞 페이지의 실행 ID 연결

`<실행ID>`는 **같은 1.13.1 기준검사 대상 commit에 대해 plan부터 기준 검사까지 수행한 한 번의 시도**를 묶는 폴더 이름입니다. 도구가 무작위로 발급하는 값이 아니라 실행자가 중복되지 않게 정합니다.

| 질문 | 기준 |
|---|---|
| 어떤 값을 쓰는가 | `20260805-01`처럼 `날짜-그날의 순번` 사용을 권장 |
| 언제 같은 ID를 쓰는가 | 같은 1.13.1 기준검사 대상 SHA로 수행하는 `plan → 승인 → apply → 5-1~5-4 검사` 전체 |
| 언제 새 ID를 만드는가 | 코드·등록자료를 수정한 뒤 다시 시도하거나, 이전 결과를 덮어쓰지 않고 재검사할 때 |
| 어디에 남는가 | `evidence/om-1.13.1-baseline-<실행ID>/` 폴더명과 일부 `run-id`에 남음 |
| Registry에 기록되는가 | 아니요. 검사 실행 이력을 묶는 증거 경로이며 Registry의 BANK-OM 이력과는 별개 |

앞 페이지에서 `PROPOSAL_WRITTEN`이 나온 실행 ID를 그대로 넣습니다. 아래 `20260806-02`는 예시입니다.

```bash
RUN_ID=20260806-02
```

```bash
PLAN_DIR="$OM_TEST_REPO/evidence/om-1.13.1-initial-bootstrap-$RUN_ID"
```

```bash
BASELINE_DIR="$OM_TEST_REPO/evidence/om-1.13.1-baseline-$RUN_ID"
```

proposal 폴더는 앞 페이지의 `bootstrap-plan`이 이미 만들었습니다. 이 페이지에서 빈 폴더를 따로 만들지 않습니다. `BASELINE_DIR`은 5장에서 검사 결과를 저장할 때 자동으로 생성됩니다.

## 4. plan → 승인 → apply

### 4-1. 최초 등록 제안 확인

앞 페이지의 `bootstrap-plan`이 만든 제안을 확인합니다. 다음 명령은 파일을 생성하지 않고, 이미 생성된 요약을 화면에 보여줍니다.

```bash
test -f "$PLAN_DIR/proposal/summary.md" && echo "[확인 완료] 최초 등록 제안이 있습니다."
```

`No such file`이 나오면 `RUN_ID`가 앞 페이지와 다르거나 `bootstrap-plan`을 아직 실행하지 않은 것입니다. 빈 폴더를 만들지 말고 앞 페이지 3-3~3-5를 먼저 수행합니다.

```bash
sed -n '1,200p' "$PLAN_DIR/proposal/summary.md"
```

다음 조건을 모두 만족해야 4-2로 이동합니다.

- 상태: `REVIEW_REQUIRED`
- 반영 가능: `yes`
- BANK-OM 7개, commit 7개, 변경 경로 111개, 공용 경로 37개
- **반드시 수정할 항목**이 없음

`BLOCKED`이면 승인 단계가 아닙니다. `summary.md`의 수정 항목에 따라 최초 등록 입력 YAML을 고치고, 새 실행 ID로 `bootstrap-plan`을 다시 실행합니다. 차단된 proposal로 승인 양식을 만들거나 `apply`하면 도구가 `PROPOSAL_NOT_APPLY_READY`로 다시 차단합니다.

| 관리 대상 | 이력이 남는 위치 | 언제 이력이 확정되는가 |
|---|---|---|
| BANK-OM 실제 코드와 commit SHA | OpenMetadata 코드 저장소 | 코드 commit을 만들고 저장소에 보관할 때 |
| Registry·Manifest·Contract 등 등록자료 | 검사기 저장소의 `harness/registrations/om-temp-1.13.1/` | `apply` 후 변경 내용을 검사기 저장소에 commit할 때 |
| proposal·승인서·검사 결과 | `$PLAN_DIR/` | 증거 폴더를 별도 보관하거나 저장소에 commit할 때 |

> **주의 — 도구 실행만으로 Git 이력이 자동 생성되지는 않습니다.** `apply`는 파일을 수정하고, Git commit·push는 그 변경을 장기 이력으로 확정하는 별도 작업입니다.

> **\*참고 — 종료코드:** `1`은 필수 입력 미완료로 차단, `2`는 승인 전 사람 검토 필요, `3`은 분석 불가입니다.

### 4-2. 승인서 작성용 양식 생성

```bash
./.venv/bin/python harness/om_workflow.py bootstrap-approval-template \
  --proposal "$PLAN_DIR/proposal/proposal.yaml" \
  --output "$PLAN_DIR/registration-approval.yaml"
```

승인 양식은 `plan`을 실행할 때마다 새로 만듭니다. `plan`을 다시 실행했다면 새 실행 ID를 사용합니다.

정상 결과는 `status: TEMPLATE_WRITTEN`입니다. 사용자는 승인자·승인 시각·승인 근거만 작성합니다.

| 파일 | 역할 | 누가 작성하는가 |
|---|---|---|
| `proposal/proposal.yaml` | 코드 비교 결과와 제안할 등록자료 변경을 기록한 **등록 변경 제안서** | 준비도구 |
| `registration-approval.yaml` | 제안을 수용한 근거를 기록하는 **승인서** | 준비도구가 틀을 만들고 사용자가 승인 내용을 작성 |

:::details 승인서 작성 전·후 예시 펼치기
**도구가 만든 승인서 작성용 양식 예시**

```yaml
schema_version: 1
proposal_digest: sha256:502a6824bb60e02b0d6cf4a66043e9e5d9ec0b22ed70b2c3387437b738d278b7
approved_by: REPLACE_WITH_APPROVER_ID
approved_at: REPLACE_WITH_RFC3339_TIME
decisions:
- finding_id: REVIEW-0001
  decision: accept_proposal
  reason: REPLACE_WITH_REVIEW_REASON
```

**사용자가 검토 후 작성한 예시**

```yaml
schema_version: 1
proposal_digest: sha256:502a6824bb60e02b0d6cf4a66043e9e5d9ec0b22ed70b2c3387437b738d278b7
approved_by: bank-om-owner@example.com
approved_at: 2026-08-05T14:30:00-07:00
decisions:
- finding_id: REVIEW-0001
  decision: accept_proposal
  reason: BANK-OM-001~007의 담당자·필수 경로·Contract와 111개 변경 경로를 확인함
```

==차이: `REPLACE_WITH_...` 자리표시자가 실제 승인자·승인 시각·검토 근거로 바뀌어야 합니다.== `proposal_digest`와 `finding_id`는 사용자가 임의로 새로 만들거나 수정하지 않습니다.
:::

제안을 수정하거나 거절할 때는 이 승인서에 별도 값을 쓰지 않습니다. 등록 초안을 고친 뒤 새 실행 ID로 `plan`과 승인 양식을 다시 만듭니다.

#### 등록자료가 바뀐 경우

| 변경 시점 | 기존 승인 사용 | 처리 |
|---|---|---|
| `plan` 실행 전 | 해당 없음 | 수정을 마친 뒤 `plan` 실행 |
| `plan` 실행 후 | 사용 불가 | 새 실행 ID로 `plan`과 승인 다시 실행 |
| 승인 후 `apply` 전 | 사용 불가 | `apply`가 중단됨. 새 실행 ID로 다시 진행 |
| `apply` 후 | 사용 불가 | 새 변경 작업으로 `plan → 승인 → apply` 진행 |

파일 한 개만 바뀌어도 등록자료 전체를 다시 승인합니다. `apply` 전에 등록 폴더가 수동으로 바뀌지 않았는지 아래 두 명령으로 확인합니다.

#### 등록 폴더의 변경 파일 유무 확인

아래 명령은 **검사기 저장소 전체가 아니라 1.13.1 등록 폴더만** 확인합니다.

```bash
git -C "$OM_TEST_REPO" status --short -- \
  harness/registrations/om-temp-1.13.1
```

**확인할 내용:** 현재 `plan`이 만들어진 뒤 `apply`는 아직 실행하지 않은 시점이므로, **빈 출력이 정상**입니다.

| 표시 | 의미 | 이 단계의 처리 |
|---|---|---|
| 빈 출력 | 등록 폴더에 수동 변경 없음 | 계속 진행 |
| `M` | Git이 관리하는 파일의 내용이 변경됨 | 중단하고 변경 내용 확인 |
| `??` | Git에 아직 등록되지 않은 새 파일이 생김 | 중단하고 파일 용도 확인 |
| `D` | Git이 관리하는 파일이 삭제됨 | 중단하고 삭제 의도 확인 |

#### 기존 등록 파일의 실제 변경 내용 확인

```bash
git -C "$OM_TEST_REPO" diff -- harness/registrations/om-temp-1.13.1
```

**확인할 내용:** Git이 이미 관리하는 등록 파일에서 `+`는 추가된 내용, `-`는 삭제된 내용입니다. 위 명령이 빈 출력이었다면 이 명령도 빈 출력이어야 합니다.

> **주의:** `??`로 표시된 새 파일의 내용은 `git diff`에 나오지 않습니다. 새 파일 유무는 반드시 첫 번째 `status --short` 결과에서 확인합니다.

두 명령 중 하나라도 출력이 있으면 현재 승인서를 사용하지 않습니다. 변경 의도를 확인한 뒤 새 실행 ID로 `plan → 승인`을 다시 진행합니다.

`apply`는 가장 최근 승인서를 자동으로 찾지 않습니다. 같은 실행 ID 폴더의 `proposal.yaml`과 `registration-approval.yaml`을 명령에 직접 지정합니다.

### 4-3. 승인된 변경 반영

```bash
./.venv/bin/python harness/om_workflow.py bootstrap-apply \
  --repo "$OM_CODE_REPO" \
  --version 1.13.1 \
  --proposal "$PLAN_DIR/proposal/proposal.yaml" \
  --approval "$PLAN_DIR/registration-approval.yaml" \
  --result "$PLAN_DIR/registration-apply-result.json"
```

`apply`는 승인한 제안과 현재 코드·등록자료가 같은지 확인합니다. 같으면 반영하고, 다르면 중단합니다. 반영 중 실패하면 수정된 파일을 원래 상태로 복구합니다.

:::details apply 성공·중단 라벨별 실제 형식 예시 펼치기
**성공 — 등록자료 반영 완료**

```json
{
  "status": "APPLIED",
  "proposal_digest": "sha256:502a...",
  "approved_by": "bank-om-owner@example.com",
  "written_files": [
    "contracts.yaml",
    "customization-registry.yaml",
    "manifests/BANK-OM-001.yaml"
  ]
}
```

==차이: 성공 결과는 `status`가 `APPLIED`이며 `written_files`에 실제 반영 파일이 표시됩니다.==

**중단 — proposal 생성 후 코드나 등록자료가 바뀜**

```json
{
  "status": "BLOCKED",
  "code": "STALE_PROPOSAL",
  "message": "custom ref moved after proposal creation"
}
```

==차이: `APPLIED`가 아니라 `BLOCKED`이고 `code`가 `STALE_PROPOSAL`입니다.== 새 실행 ID를 만들고 4-1 `plan`부터 다시 실행합니다.

**중단 — 다른 apply가 실행 중이거나 이전 잠금이 남음**

```json
{
  "status": "BLOCKED",
  "code": "APPLY_LOCKED",
  "message": "registration apply lock exists: .../.registration-apply.lock"
}
```

==차이: `code`가 `APPLY_LOCKED`입니다.== 다른 apply 실행 여부를 확인합니다. 실행 중인 작업이 없다면 잠금이 남은 원인을 담당자와 확인하고, 잠금 파일을 임의 삭제하지 않습니다.

**분석 오류 — 승인서에 작성하지 않은 항목이 있음**

```json
{
  "code": "APPROVAL_INPUT_INVALID",
  "field": "approved_by",
  "file": ".../registration-approval.yaml",
  "message_ko": "승인서에 수정해야 할 항목이 3개 있습니다.",
  "next_action": "issues의 각 필드와 수정 방법을 확인해 registration-approval.yaml을 수정합니다.",
  "status": "ANALYSIS_ERROR",
  "issues": [
    {
      "code": "APPROVAL_APPROVER_PLACEHOLDER",
      "field": "approved_by",
      "current_value": "REPLACE_WITH_APPROVER_ID",
      "message_ko": "승인자 항목이 아직 기본 자리표시자입니다.",
      "next_action": "approved_by에 실제 승인자 이름이나 조직 식별값을 입력합니다."
    },
    {
      "code": "APPROVAL_TIME_PLACEHOLDER",
      "field": "approved_at",
      "current_value": "REPLACE_WITH_RFC3339_TIME",
      "message_ko": "승인 시각 항목이 아직 기본 자리표시자입니다.",
      "next_action": "approved_at에 RFC 3339 형식의 승인 시각을 입력합니다. 예: 2026-08-06T10:30:00-07:00"
    },
    {
      "code": "APPROVAL_REASON_PLACEHOLDER",
      "field": "decisions[0].reason",
      "current_value": "REPLACE_WITH_REVIEW_REASON",
      "message_ko": "승인 근거 항목이 아직 기본 자리표시자입니다.",
      "next_action": "reason에 제안 내용을 확인하고 승인한 근거를 입력합니다."
    }
  ]
}
```

==확인할 곳: `issues`에 문제 필드, 현재 값, 한국어 원인, 수정 방법이 모두 표시됩니다.== `file`에 표시된 승인서의 항목을 모두 수정한 뒤 같은 `bootstrap-apply` 명령을 다시 실행합니다.

| `code` | 문제 필드 | 수정 내용 |
|---|---|---|
| `APPROVAL_APPROVER_PLACEHOLDER` | `approved_by` | 실제 승인자 이름 또는 조직 식별값 입력 |
| `APPROVAL_TIME_PLACEHOLDER` | `approved_at` | RFC 3339 승인 시각 입력. 예: `2026-08-06T10:30:00-07:00` |
| `APPROVAL_REASON_PLACEHOLDER` | `decisions[0].reason` | 제안 내용을 확인하고 승인한 근거 입력 |
| `APPROVAL_INPUT_INVALID` | `issues[].field` | `issues`에 나온 모든 필드의 자리표시자·형식 오류 수정 |
| `APPROVAL_DECISION_COVERAGE_MISMATCH` | `decisions[].finding_id` | proposal에서 승인 양식을 다시 생성 |

여러 항목에 문제가 있으면 `issues` 배열에 한 번에 표시됩니다.
:::

## 5. 1.13.1 기준 검사 실행

### 5-0. 묶음 실행 명령과 `results.json`의 차이

`om_workflow.py validate`와 `om_workflow.py source`는 여러 검사를 정해진 순서로 호출하는 **묶음 실행 명령**입니다. 반면 `registration-validation-results.json`, `source-gate-results.json`, `shared-code-results.json`은 검사가 끝난 뒤 판정과 근거를 보관하는 **결과 파일**입니다.

| 구분 | 들어 있는 내용 | 들어 있지 않은 내용 | 사용 시점 |
|---|---|---|---|
| 묶음 실행 명령 | 어떤 실행기를 시작할지와 OpenMetadata 코드 저장소·버전·결과 경로 | 개별 검사의 최종 판정 | 터미널에서 검사 시작 |
| 검사기 코드 | 묶음에 포함할 검사와 비교 방법 | 사용자의 업무 승인 | 실행기가 자동 호출 |
| `results.json` | 검사 이름, `verdict`, 판정 근거, 검사한 대상 commit 정보 | 다음 검사를 실행하는 shell 명령 | 실행 후 결과 확인·승인 증거 보관 |

따라서 `results.json`을 실행하거나 그 안에서 명령을 찾는 것이 아닙니다. 사용자는 이 문서의 명령을 실행하고, 생성된 JSON에서 각 검사 결과를 읽습니다.

각 검사기의 전체 사용 시점과 정상·실패 사례는 바로 앞의 [검사기 간단 학습 가이드](./OM_TEMP_1.13.1_1.13.2_검사기_간단_학습_가이드.html)에서 확인할 수 있습니다. 아래 5-1~5-3은 그중 이번 1.13.1 기준 검사 명령에 실제로 묶인 항목만 다시 정리합니다.

검사 결과에는 일반적인 `FAIL` 한 종류 대신 아래 네 판정이 사용됩니다. 검사마다 낼 수 있는 판정이 다르므로, 아래 예시에는 **해당 검사에서 실제로 가능한 판정만** 표시합니다.

| 판정 | 의미 | 다음 행동 |
|---|---|---|
| `pass` | 정해진 비교 조건을 만족함 | 다음 검사로 진행 |
| `approval` | 자동으로 옳고 그름을 확정할 수 없는 변화가 있음 | 담당자가 근거를 확인하고 승인 또는 수정 |
| `block` | 신뢰할 수 있는 비교 결과에서 규칙 위반이 확인됨 | 코드 또는 등록자료를 수정하고 재검사 |
| `analysis_error` | 파일·Git 이력·설정 오류 때문에 비교 자체를 신뢰할 수 없음 | 입력이나 환경을 복구한 뒤 처음부터 재검사 |

### 5-1. 등록자료 상태 5개 검사

```bash
./.venv/bin/python harness/om_workflow.py validate \
  --repo "$OM_CODE_REPO" \
  --version 1.13.1 \
  --output "$BASELINE_DIR/registration-validation-results.json"
```

이 명령은 아래 5개 검사를 한 번에 실행하고 `registration-validation-results.json`의 `checks[]`에 저장합니다. 이 묶음은 등록자료를 실행 가능한 입력으로 신뢰할 수 있는지 확인하는 사전 검사이며, 각 항목에 별도의 T 번호를 붙인 묶음은 아닙니다. 단, 마지막 항목은 검사기 학습 페이지의 **T60-I 필수 test 존재 검사**와 같은 구현을 사용합니다.

| `checks[].name` | 무엇을 읽는가 | 무엇을 확인하는가 | 실패 의미 |
|---|---|---|---|
| Manifest 구조와 작성 규칙 | 7개 Manifest·`repository-layout.yaml` | 필수 필드·경로 표현·작성 규칙을 해석할 수 있는가 | YAML·필드·경로 규칙을 신뢰할 수 없으면 `analysis_error` |
| Registry·Manifest·Contract 연결 | Registry·Manifest·`contracts.yaml` | 같은 BANK-OM ID와 Contract가 서로 빠짐없이 연결됐는가 | 참조 누락·중복이면 `analysis_error` |
| 공식 원본과 행내 custom 코드의 변경 경로 | `commit-inventory.yaml`과 실제 official·custom diff | 등록한 111개 경로가 현재 코드 차이와 일치하는가 | 경로가 추가·누락되면 `analysis_error` |
| 공용 파일 소유정보 | `shared-path-owners.yaml`과 Manifest 전체 | 한 파일을 함께 쓰는 BANK-OM ID 목록이 실제 Manifest 관계와 같은가 | ID가 빠지거나 더 들어가면 `block` |
| 필수 테스트 코드 존재 | `contracts.yaml`의 Python pytest 경로·함수 이름 | Contract가 지정한 test 파일과 함수가 실제로 존재하는가 | 없으면 `block`; test를 실행한 결과는 아님 |

결과 파일의 핵심 구조는 다음과 같습니다. `checks` 배열 한 항목이 검사 하나입니다.

```json
{
  "registration": "harness/registrations/om-temp-1.13.1",
  "checks": [
    {
      "name": "Manifest 구조와 작성 규칙",
      "verdict": "pass",
      "detail": "7개 Manifest"
    }
  ],
  "reconstruction_plan_digest": "sha256:...",
  "release_note": "등록 입력자료 일치 여부만 확인한 결과"
}
```

`pass`는 등록 입력끼리 일치한다는 뜻이며 build·runtime test 통과를 의미하지 않습니다. 실패하면 `checks[]`에서 `pass`가 아닌 항목의 `name`과 `detail`을 먼저 확인합니다.

:::details 5-1 낱개 검사별 모든 판정 예시 펼치기
아래 JSON 조각은 결과를 읽는 방법을 보여주는 축약 예시입니다. **발생 조건**은 그 판정이 나오는 대표 상황입니다. 앞의 두 검사는 등록자료를 읽는 도중 오류가 나면 개별 이름 대신 `등록자료 분석` 하나의 `analysis_error`로 중단됩니다.

| 검사 | 가능한 판정과 예시 | 차이와 조치 |
|---|---|---|
| Manifest 구조와 작성 규칙 | 정상: `{"name":"Manifest 구조와 작성 규칙","verdict":"pass","detail":"7개 Manifest"}`<br>해석 실패: `{"name":"등록자료 분석","verdict":"analysis_error","detail":"schema: implementation.required_changed_paths is required"}` | **발생 조건:** YAML 들여쓰기 오류, 필수 필드 누락, 허용하지 않는 값 또는 경로 형식.<br>==차이: `pass`가 `analysis_error`로 바뀌고 `detail`에 잘못된 필드가 표시됩니다.== Manifest 형식을 고칩니다. 이 검사는 `approval`·`block`을 내지 않습니다. |
| Registry·Manifest·Contract 연결 | 정상: `{"name":"Registry·Manifest·Contract 연결","verdict":"pass","detail":"7개 BANK-OM"}`<br>연결 분석 실패: `{"name":"등록자료 분석","verdict":"analysis_error","detail":"manifest references unknown contract: CONTRACT-X"}` | **발생 조건:** Registry의 Manifest 파일이 없음, Manifest가 미등록 Contract를 참조함, ID가 중복되거나 역참조가 맞지 않음.<br>==차이: 알 수 없는 참조 때문에 개별 검사 전 분석이 중단됩니다.== ID 연결을 고칩니다. 이 검사는 `approval`·`block`을 내지 않습니다. |
| 공식 원본과 커스텀 코드의 변경 경로 | 정상: `{"name":"공식 원본과 행내 custom 코드의 변경 경로","verdict":"pass","detail":"111개 경로"}`<br>불일치: `{"name":"공식 원본과 행내 custom 코드의 변경 경로","verdict":"analysis_error","detail":"111개 경로"}` | **발생 조건:** official·snapshot SHA를 로컬에서 찾지 못함, 두 SHA의 실제 diff와 `commit-inventory.yaml`의 경로가 다름.<br>==차이: 경로 수가 같아 보여도 `verdict`가 `analysis_error`일 수 있습니다.== 터미널의 `registered inventory is stale`와 누락 경로 목록을 확인합니다. 이 검사는 `approval`·`block`을 내지 않습니다. |
| 공용 파일 소유정보 | 정상: `{"name":"공용 파일 소유정보","verdict":"pass","detail":"37개 공용 경로"}`<br>불일치: `{"name":"공용 파일 소유정보","verdict":"block","detail":"37개 공용 경로"}` | **발생 조건:** 같은 파일을 쓰는 BANK-OM ID가 Manifest에는 있는데 `shared-path-owners.yaml`에서 빠졌거나, 반대로 더 들어 있음.<br>==차이: `pass`가 `block`으로 바뀝니다.== 두 ID 목록을 대조합니다. 이 검사는 `approval`·`analysis_error`를 개별 결과로 내지 않습니다. 파일을 읽지 못하면 앞 단계의 `등록자료 분석` 오류로 중단됩니다. |
| 필수 테스트 코드 존재 | 정상: `{"name":"필수 테스트 코드 존재","verdict":"pass","detail":"9개 Python pytest"}`<br>누락: `{"name":"필수 테스트 코드 존재","verdict":"block","detail":"9개 Python pytest"}`<br>분석 불가: `{"name":"필수 테스트 코드 존재","verdict":"analysis_error","detail":"9개 Python pytest"}` | **발생 조건:** test 선택자 형식이 잘못됨, 파일·함수가 없음(`block`), test 파일을 읽지 못하거나 Python 구문 오류가 있음(`analysis_error`).<br>==차이: 누락과 분석 실패를 서로 다른 상태로 구분합니다.== 터미널의 `required-test-implementations` 이유를 확인합니다. 이 검사는 `approval`을 내지 않습니다. |
:::

### 5-2. 소스 검사 묶음

```bash
./.venv/bin/python harness/om_workflow.py source \
  --repo "$OM_CODE_REPO" \
  --version 1.13.1 \
  --output "$BASELINE_DIR/source-gate-results.json"
```

이 명령은 현재 **1.13.1 기준검사 대상 commit**을 `candidate_lock`에 고정하고, 아래 소스 검사들을 같은 commit에 실행합니다. 여기서 고정하는 대상은 아직 1.13.2를 합친 업그레이드 후보가 아닙니다. 각 결과는 `source-gate-results.json`의 `gates[]`에 저장됩니다.

| 검사기 | JSON의 `gates[].name` | 무엇을 검사하는가 | 실패 시 확인할 것 |
|---|---|---|---|
| T25 공식 코드 포함 관계 | `vendor-ancestry` | 1.13.1 기준검사 대상의 Git 이력에 승인한 공식 1.13.1 commit이 포함됐는가 | 잘못된 공식 기준에서 branch를 만들거나 병합하지 않았는지 확인 |
| T26 BANK-OM 변경 생존 | `customization-survival` | 활성 BANK-OM ID의 필수 경로·Contract·test 연결이 1.13.1 기준검사 대상에 남아 있는가 | 누락된 ID와 `required_paths`를 확인 |
| T60-I 필수 test 존재 | `required-test-implementations` | Contract가 지정한 Python pytest 파일과 함수가 실제로 존재하는가 | test 경로·함수 이름을 수정하거나 test 구현 추가 |
| T30 commit 규칙 | `commit-invariants` | 커스터마이징 commit이 승인한 BANK-OM ID 작성 규칙을 지키는가 | 한 commit에 여러 ID가 섞였는지 확인 |
| T31 ID·series 규칙 | `id-invariants` | 한 BANK-OM ID의 commit 개수와 순서가 Manifest `series`와 같은가 | 누락 commit 또는 잘못된 series 확인 |
| T40 변경 범위 일치 | `drift` | 실제 변경 파일이 Manifest가 선언한 허용·필수 범위와 일치하는가 | Manifest 누락 경로 또는 예상 밖 코드 변경 확인 |
| T41 중요 경로 검사 | `sensitive-zones` | DB migration·인증 등 중요 경로 변경이 승인 범위에 포함됐는가 | 중요 경로 변경 의도와 승인 근거 확인 |
| T93 ID별 정확 범위 | `exact-scope-history` | 각 ID의 실제 commit 변경 경로와 해당 Manifest 범위가 정확히 같은가 | ID별 경로 누락·과다 선언 확인 |
| 공용 파일 ID별 코드 정의 | `shared-code-definitions` | Registry가 공용 코드 정의 파일을 선언한 경우, 공용 파일의 ID별 승인 코드가 남았는가 | 누락된 경로·ID·assertion 확인 |

> **\*참고 — 마지막 공용 코드 정의 검사는 선택적으로 묶음에 포함됩니다.** Registry `source.shared_code_definitions`가 설정돼 있을 때만 5-2에서 실행됩니다. 5-3은 같은 검사를 단독으로 다시 실행하여 공용 파일 문제만 별도로 진단하는 절차입니다.

결과 파일의 핵심 구조는 다음과 같습니다. 실행 명령은 없고, 검사한 commit을 고정한 정보와 각 gate의 판정·근거가 있습니다.

```json
{
  "candidate_lock": {
    "candidate": {
      "commit_sha": "d952a838...",
      "tree_sha": "e490ed82..."
    },
    "upstream": {
      "target_tag": "1.13.1-release",
      "target_sha": "afcb2d2c..."
    }
  },
  "candidate_lock_digest": "sha256:...",
  "gates": [
    {
      "name": "vendor-ancestry",
      "verdict": "pass",
      "reasons": ["candidate=d952a838...", "approved_target=afcb2d2c..."]
    }
  ]
}
```

결과를 읽을 때는 `gates[].verdict`만 보지 말고 `reasons`의 `candidate` SHA·대상 BANK-OM ID·문제 경로를 함께 확인합니다. 여기서 `candidate` SHA는 1.13.1 기준검사 대상 SHA입니다. 현재 검사 대상 commit과 다르면 결과를 재사용하지 않습니다.

:::details 5-2 낱개 검사별 모든 판정 예시 펼치기
예시는 `gates[]` 한 항목을 축약한 것입니다. `reasons`가 실제 확인 위치와 다음 조치를 알려줍니다.

| 검사 | 가능한 판정 예시 | 판정 차이와 조치 |
|---|---|---|
| T25 `vendor-ancestry` | `pass`: `approved_target=afcb2d2c...`<br>`block`: `candidate does not contain approved upstream target`<br>`analysis_error`: `required commit object missing` | **발생 조건:** custom branch를 다른 공식 버전에서 만들었거나 공식 1.13.1을 병합하지 않음(`block`), 필요한 commit을 아직 fetch하지 않았거나 검사 대상을 고정한 뒤 branch가 이동함(`analysis_error`).<br>==두 상태는 “관계가 틀림”과 “관계를 확인할 자료가 없음”의 차이입니다.== `approval`은 없습니다. |
| T26 `customization-survival` | `pass`: `BANK-OM-002 required_paths=4`<br>`approval`: `expected_path_missing ... -> approval`<br>`block`: `required_path_missing ... -> block`<br>`analysis_error`: `expected_scope_not_literal ... -> analysis_error` | **발생 조건:** 선택 경로가 없어지거나 공식 코드와 같아짐(`approval`), 필수 경로·Contract·test 연결이 누락됨(`block`), SHA를 읽지 못하거나 정확 경로가 아닌 패턴을 사용함(`analysis_error`).<br>==없어진 항목의 필수 여부에 따라 판정이 달라집니다.== |
| T60-I `required-test-implementations` | `pass`: `implemented_required_tests=9`<br>`block`: `required test symbol is missing`<br>`analysis_error`: `cannot parse required test implementation` | **발생 조건:** Contract의 test 파일·함수가 없음 또는 선택자 형식이 잘못됨(`block`), 파일은 있지만 Python 구문 오류나 읽기 오류로 분석할 수 없음(`analysis_error`).<br>==누락과 분석 불가를 구분합니다.== `approval`은 없습니다. |
| T30 `commit-invariants` | `pass`: 위반 목록 없음<br>`block`: `expected exactly one Customization-ID`<br>`analysis_error`: `unknown path classification` | **발생 조건:** 커스터마이징 commit 본문에 ID가 없거나 2개 이상임, 허용되지 않은 merge commit이 섞임(`block`), 변경 경로를 어느 코드 영역으로 분류할지 설정이 없음(`analysis_error`).<br>==커밋 작성 규칙 위반과 분류 정보 부족의 차이입니다.== `approval`은 없습니다. |
| T31 `id-invariants` | `pass`: Manifest `series`와 commit 순서 일치<br>`block`: `series commit missing`<br>`analysis_error`: commit 정보를 신뢰할 수 없음 | **발생 조건:** 같은 ID의 후속 commit SHA가 Manifest `series`에서 빠짐, 순서가 다름, 미등록 ID가 등장함(`block`), Git commit 목록을 읽지 못함(`analysis_error`).<br>==등록 이력 불일치와 Git 분석 실패를 구분합니다.== `approval`은 없습니다. |
| T40 `drift` | `pass`: 실제 변경 경로가 선언 범위와 일치<br>`block`: `path outside declared scope`<br>`analysis_error`: 선언 경로 패턴을 해석할 수 없음 | **발생 조건:** commit이 Manifest의 허용 경로 밖 파일을 수정하거나 필수 경로가 빠짐(`block`), 경로 표현이 잘못돼 비교 범위를 만들 수 없음(`analysis_error`).<br>==실제 범위 위반과 비교 규칙 오류의 차이입니다.== `approval`은 없습니다. |
| T41 `sensitive-zones` | `pass`: 중요 경로 변경 없음 또는 승인 범위 안<br>`approval`: 검토가 필요한 중요 경로 변화<br>`block`: 금지된 중요 경로 변경<br>`analysis_error`: 중요 경로 정책을 읽지 못함 | **발생 조건:** migration·인증·권한 경로가 검토 등급에 해당함(`approval`), 명시적 금지 경로가 바뀜(`block`), 경로 정책이 누락·오류라 등급을 결정할 수 없음(`analysis_error`).<br>==T41은 네 판정이 모두 가능합니다.== |
| T93 `exact-scope-history` | `pass`: `declared exact scopes equal observed per-ID history`<br>`approval`: `declared_path_not_observed`<br>`block`: `observed_path_outside_exact_scope`<br>`analysis_error`: `non_literal_exact_scope` | **발생 조건:** Manifest에는 경로가 있으나 해당 ID commit에서 실제로 건드리지 않음(`approval`), ID commit이 Manifest에 없는 파일을 변경함(`block`), 와일드카드처럼 파일 하나로 확정할 수 없는 범위를 사용함(`analysis_error`).<br>==과다 선언·누락 선언·정확 비교 불가를 구분합니다.== |
| 선택 검사 `shared-code-definitions` | `pass`: 모든 경로·ID 정의 일치<br>`block`: `code definition occurrence mismatch expected=1 actual=0`<br>`analysis_error`: `coverage mismatch: missing=...` | **발생 조건:** 정의 파일은 정상이나 승인 코드·JSON·YAML 값이 1.13.1 기준검사 대상에서 없어지거나 값이 바뀜(`block`), 공용 경로–ID 조합 또는 비교 방식 자체가 정의되지 않음(`analysis_error`).<br>==실제 코드 불일치와 비교 기준 누락을 구분합니다.== `approval`은 없습니다. |
:::

### 5-3. 공용 파일 ID별 코드 정의 검사

```bash
PYTHONPATH=harness ./.venv/bin/python -m acgh.shared_code \
  --repo "$OM_CODE_REPO" \
  --candidate codex/om-1.13.1-id-series-upstream \
  --owners harness/registrations/om-temp-1.13.1/shared-path-owners.yaml \
  --definitions harness/registrations/om-temp-1.13.1/shared-code-definitions.yaml \
  --output "$BASELINE_DIR/shared-code-results.json"
```

5-3은 여러 검사기의 묶음이 아니라 **공용 파일 ID별 코드 정의 검사 하나만 실행하는 진단 명령**입니다. `shared-path-owners.yaml`에 있는 모든 `공용 파일 경로 + BANK-OM ID` 조합이 `shared-code-definitions.yaml`에 정확히 한 번씩 정의됐는지 먼저 확인하고, `--candidate`로 지정한 1.13.1 기준검사 대상 파일의 실제 내용을 다음 방식으로 비교합니다.

| 대상 파일 | 정의 방식 | 실제 비교 내용 |
|---|---|---|
| Java·TypeScript·TSX·SQL | `code_fragment` | 주석과 공백을 제외한 실제 코드 토큰이 승인한 조각과 정해진 횟수만큼 존재하는가 |
| JSON | `json_value` | JSON Pointer가 가리키는 실제 값이 승인값과 같은가 |
| YAML | `yaml_value` | YAML Pointer가 가리키는 실제 값이 승인값과 같은가 |

파일 경로만 존재해도 특정 ID의 정의가 빠졌으면 `block`입니다. 주석에 같은 단어가 있는 것은 통과 근거가 아닙니다. 정의 파일을 읽지 못하거나 경로–ID 조합 자체가 빠졌으면 신뢰할 수 있는 비교를 못 했으므로 `analysis_error`입니다.

결과 파일에는 단일 `gate`만 들어 있습니다.

```json
{
  "gate": {
    "name": "shared-code-definitions",
    "verdict": "block",
    "reasons": [
      "BANK-OM-002 openmetadata-service/.../Entity.java: query-report-definition: code definition occurrence mismatch expected=1 actual=0"
    ]
  }
}
```

위 예시는 공용 `Entity.java` 파일은 있지만 BANK-OM-002로 승인한 QueryReport 코드 조각이 없다는 뜻입니다. 실제 코드를 복원할지, 승인한 `fragment`가 틀렸는지는 사용자가 diff를 보고 결정한 뒤 5-3을 다시 실행합니다.

:::details 5-3 단독 검사에서 가능한 모든 판정 예시 펼치기
**통과 — 승인한 정의가 모두 존재함**

```json
{"gate":{"name":"shared-code-definitions","verdict":"pass","reasons":["shared_owner_pairs=114","all approved definitions matched"]}}
```

==차이: `verdict`가 `pass`이고 누락된 경로·ID가 없습니다.==

**차단 — 비교 기준은 정상이나 실제 코드가 다름**

```json
{"gate":{"name":"shared-code-definitions","verdict":"block","reasons":["BANK-OM-002 Entity.java: query-report-definition: code definition occurrence mismatch expected=1 actual=0"]}}
```

==차이: `verdict`가 `block`이고 `expected=1 actual=0`이 실제 코드 누락을 표시합니다.== 코드를 복원할지 승인 정의를 수정할지 사용자가 결정합니다.

**분석 오류 — 비교 기준을 만들 수 없음**

```json
{"gate":{"name":"shared-code-definitions","verdict":"analysis_error","reasons":["shared code definition coverage mismatch: missing=[Entity.java, BANK-OM-002]"]}}
```

==차이: `verdict`가 `analysis_error`입니다.== 실제 코드를 비교하기 전 단계에서 경로–ID 정의가 빠졌으므로 `shared-code-definitions.yaml`을 보완합니다. 이 검사는 `approval`을 내지 않습니다.
:::

### 5-4. 실행 환경이 있을 때의 Contract test

이 단계는 **등록·소스 검사를 통과한 1.13.1 commit이 실제 Docker 서비스에서도 정상 동작하는지** 확인합니다. Docker 컨테이너가 `healthy`인 것만으로는 완료되지 않습니다.

#### 5-4-1. Docker 서비스 상태 확인

**확인 내용:** OpenMetadata server, DB, 검색 서비스가 모두 `healthy`인지 확인합니다.

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

**정상 결과:** `openmetadata_server`, `openmetadata_mysql`, `openmetadata_elasticsearch`가 모두 `healthy`입니다.

#### 5-4-2. API 주소와 실행 commit 확인

**준비:** 로컬 Docker 기본 포트 `8585`를 사용합니다.

```bash
export OPENMETADATA_BASE_URL="http://127.0.0.1:8585/api"
```

**확인 내용:** Docker 서비스의 버전과 commit을 표시합니다.

```bash
curl -fsS "$OPENMETADATA_BASE_URL/v1/system/version" | jq
```

**확인 내용:** 이번 기준검사에 사용할 제품 코드 저장소 HEAD를 표시합니다.

```bash
git -C "$OM_CODE_REPO" rev-parse HEAD
```

`system/version`의 `revision`과 `git rev-parse HEAD`가 같아야 합니다. 다르면 **검사하려는 코드와 Docker에서 실행 중인 코드가 다르므로 중단**합니다.

> **2026-08-07 현재 확인 결과:** Docker 서비스는 `59dae915...`를 실행하고, 등록·소스 검사를 통과한 commit은 `d952a838...`입니다. 현재 서비스로는 연결 연습은 가능하지만 5-4 정식 PASS를 남길 수는 없습니다.

#### 5-4-3. 로컬 API 로그인

**작업 내용:** 로컬 개발 환경의 관리자 계정으로 로그인하고 API token을 현재 터미널에만 저장합니다. 아래 값은 기본 개발 계정을 바꾸지 않은 경우에만 사용합니다.

```bash
export OPENMETADATA_AUTH_TOKEN="$(
  curl -fsS -X POST "$OPENMETADATA_BASE_URL/v1/users/login" \
    -H 'Content-Type: application/json' \
    --data '{"email":"admin@open-metadata.org","password":"YWRtaW4="}' \
  | jq -er '.accessToken'
)"
```

**확인 내용:** token 원문을 화면에 표시하지 않고 발급 여부만 확인합니다.

```bash
test -n "$OPENMETADATA_AUTH_TOKEN" && printf 'API token 준비 완료\n'
```

**정상 결과:** `API token 준비 완료`가 출력됩니다. 이 환경변수는 현재 터미널을 닫으면 사라지며 문서·Git·결과 파일에 기록하지 않습니다.

#### 5-4-4. Contract test 입력 준비

| 입력 | 의미 | 준비 방법 |
|---|---|---|
| `OPENMETADATA_AUTH_TOKEN` | API 호출에 쓸 Bearer token | 로컬 basic 로그인으로 발급하고 파일에 저장하지 않음 |
| `BANK_CONTRACT_QUERY_ID` | QueryReport에 연결할 기존 Query ID | 실행 환경에 Query 1개 생성 후 ID 기록 |
| `BANK_FAILED_ASSERTION_FQN` | 실패 상태와 담당자가 있는 test case FQN | 실패 test case 하나를 준비한 후 FQN 기록 |
| `BANK_COLUMN_TABLE_FQN` | 행내 확장 컬럼이 있는 table FQN | table을 생성·수집한 후 FQN 기록 |
| `BANK_COLUMN_NAME` | 위 table에서 검사할 column 이름 | `attributeName`, `instanceName`, `infoType`가 있는 column 선택 |
| `BANK_IME_EDITOR_URL` | 한글 조합을 검사할 SchemaEditor 페이지 | 로그인 후 편집 가능한 페이지 URL 기록 |
| `BANK_DATA_ASSERTIONS_URL` | 실패 test case를 표시하는 행내 페이지 | 위 test case가 보이는 URL 기록 |
| `BANK_COLUMN_UI_URL` | 행내 확장 컬럼을 표시하는 table 페이지 | 위 table의 schema URL 기록 |
| `BANK_BROWSER_STORAGE_STATE_B64` | Playwright가 사용할 브라우저 로그인 상태 | Playwright storage state JSON을 base64로 인코딩 |

> **현재 로컬 환경:** Query, 실패 test case, 행내 확장 컬럼 table이 모두 0개로 확인됐습니다. 위 fixture를 준비하기 전에는 BANK-OM-002·003·004 Contract test가 정상 실행될 수 없습니다.

#### 5-4-5. 실행 image digest 고정

**확인 내용:** `openmetadata_server`가 실행 중인 Docker image ID를 이번 test의 배포 확인값으로 저장합니다.

```bash
export DEPLOYED_ARTIFACT_DIGEST="$(docker inspect --format '{{.Image}}' openmetadata_server)"
```

```bash
printf '%s\n' "$DEPLOYED_ARTIFACT_DIGEST"
```

**정상 결과:** `sha256:` 뒤에 64자리 값이 출력됩니다.

#### 5-4-6. 실행 전 입력 검사

**확인 내용:** 필수 환경변수 11개의 누락·URL 형식·digest 형식을 검사합니다. 비밀값 내용은 출력하지 않습니다.

```bash
./.venv/bin/python \
  harness/registrations/kb-openmetadata/runtime_preflight.py
```

**정상 결과:** `ready: true`, `missing_fields: []`, `invalid_fields: []`입니다. `ready: false`면 표시된 입력을 준비한 후 다시 실행합니다.

#### 5-4-7. Contract test 실행

```bash
./.venv/bin/python harness/om_workflow.py runtime \
  --repo "$OM_CODE_REPO" \
  --version 1.13.1 \
  --artifact-digest "$DEPLOYED_ARTIFACT_DIGEST" \
  --run-id "om-1.13.1-baseline-$RUN_ID"
```

**산출물:** 증거 폴더에 `candidate-lock.yaml`, `test-run-set.yaml`, `acgh-result.yaml`이 생성됩니다. `test-run-set.yaml`의 9개 필수 test가 모두 `pass`이고 `acgh-result.yaml`의 최종 verdict가 `pass`일 때만 5-4를 완료합니다.

실제 API·브라우저·DB 입력이 없으면 runtime test가 `skipped`로 남을 수 있습니다. **실행된 test의 실패가 0개여도 필수 test가 skip이면 전체 PASS가 아닙니다.**

## 6. 결과 확인표

| 확인 대상 | 통과 기준 | 통과가 아닌 예 |
|---|---|---|
| apply 결과 | `status: APPLIED` | `STALE_PROPOSAL`, `APPLY_LOCKED`, `ANALYSIS_ERROR` |
| 등록 검사 | 모든 check가 `pass` | 경로 수·ID 연결·test 파일 누락 |
| 소스 검사 | 필수 gate가 `pass`; `reasons`가 대상 SHA와 일치 | `block`, `analysis_error`, 승인되지 않은 `approval` |
| 공용 코드 정의 | 114개 승인 조합이 모두 존재 | 다른 ID 코드만 존재, 기대값 변경 |
| Contract test | 필수 test가 실제 실행되어 통과 | skip, 환경 미준비, 다른 기준검사 대상 SHA 결과 |

> **주의 — 결과 JSON 보관 위치:** 이번 1.13.1 기준 검사 결과는 `$BASELINE_DIR/`에 새로 생성하고, 다른 SHA를 가리키는 결과를 재사용하지 않습니다.

## 7. 완료 기준

- proposal·승인서·apply 결과가 같은 digest와 1.13.1 기준검사 대상 SHA를 가리킵니다.
- Registry·Manifest·Contract·공용 경로·공용 코드 정의 연결이 통과했습니다.
- 모든 검사 결과 파일에서 verdict뿐 아니라 `reasons`를 확인했습니다.
- 환경이 없어 실행하지 못한 runtime test를 PASS로 기록하지 않았습니다.
- BLOCK·APPROVAL·ANALYSIS_ERROR와 담당자 결정을 증거 폴더에 보관했습니다.

> **중단 조건:** 위 기준을 충족하지 못하면 공식 1.13.2를 병합하지 않습니다. 1.13.1 기준이 불완전하면 업그레이드 뒤 누락 원인을 구분할 수 없습니다.

**문서 이동:** [← 이전 — 검사기 간단 학습](./OM_TEMP_1.13.1_1.13.2_검사기_간단_학습_가이드.html) · [다음 — 공식 1.13.2 준비·사전 영향 검사 →](./OM_TEMP_1.13.2_공식코드_준비_및_사전영향검사_가이드.html)
