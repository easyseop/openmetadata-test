# OpenMetadata 버전 업그레이드 통합 솔루션 고객 가이드

> 문서 대상: OpenMetadata를 커스터마이징해 사용하는 고객사의 업그레이드 검토자·승인자
> 솔루션 범위: 새 공식 버전 준비 → 병합 전 영향 검사 → vendor merge → 병합 후 검사·승인
> 현재 예시: 공식 OpenMetadata `1.13.1`을 기준으로 커스터마이징한 코드를 공식 `1.13.2`로 업그레이드

## 1. 이 솔루션이 필요한 이유

OpenMetadata 공식 코드와 고객사 커스터마이징 코드는 같은 파일을 수정할 수 있습니다. Git 병합이 성공했더라도 고객사 기능이 빠지거나 테스트 기준이 다른 코드에 연결될 수 있습니다.

이 솔루션은 업그레이드 대상 commit과 검사 결과를 하나의 실행 단위로 고정합니다. 병합 전에는 공식 변경의 영향을 알리고, 병합 후에는 커스터마이징 생존·등록 정합성·소스 위험을 다시 검사합니다.

> **★ 핵심:** 이 솔루션은 담당자의 업무 판단을 대신하지 않습니다. 자동 검사가 코드와 증거를 정리하고, 고객사는 업무 기능의 정상 기준과 승격 여부를 승인합니다.

## 2. 기존 방식과 달라진 점

| 항목 | 기존 개별 실행 | 새 통합 실행 솔루션 |
|---|---|---|
| 검사 실행 | 담당자가 검사기별 명령을 조합 | 병합 전·병합 후 단계별 명령으로 실행 |
| 검사 대상 | 결과 파일별로 commit을 따로 확인 | Candidate lock으로 검사 대상 Git commit SHA를 고정 |
| 누락 처리 | 사람이 누락 여부를 추가 확인 | 필수 입력이 없으면 `BLOCK` 또는 `ANALYSIS_ERROR`로 중단 |
| 결과 제공 | 개별 JSON을 실무자가 해석 | 관리자 요약·실무자 상세·시스템 원본을 함께 생성 |
| 승인 결속 | 결과와 승인서의 연결을 별도 확인 | 결과 digest·단계·승인 메타데이터가 다르면 거부 |

`Candidate lock`은 이번 검사가 읽을 제품 repository와 Git commit SHA를 고정한 파일입니다. `digest`는 결과 내용이 바뀌지 않았는지 확인하는 SHA-256 값입니다.

## 3. 고객사와 솔루션 제공팀의 역할

| 구분 | 준비·판단하는 내용 |
|---|---|
| 고객사 | 목표 공식 버전, 업무적 정상 기준, 변경 의도, 승인자, 승격 여부 |
| 솔루션 제공팀 | 공식 코드 고정, 사전 영향 검사, vendor merge, 충돌 해결안, 병합 후 검사, 증거 묶음 |
| 자동화 도구 | 입력 누락 차단, 검사 순서 강제, 결과 집계, commit·증거 digest 결속 |

Git이 변경 경로와 충돌 파일을 계산할 수는 있지만, 충돌 해결 후의 화면·API·DB 동작이 고객사의 업무 기준에 맞는지는 고객사 담당자가 판단합니다.

### 사람이 반드시 결정해야 하는 항목

> **중요:** 아래 값은 솔루션이 추측하거나 빈칸을 임의로 채우지 않습니다. 자동화는 코드에서 후보와 누락을 찾고, 고객사 담당자가 업무 의미를 판단해 승인합니다.

- 기능 범위: BANK-OM ID, 필수 경로, 간접 감시 경로, 공용 코드 정의를 사람이 확정합니다.
- 정상 동작: 어떤 API·화면·DB 결과가 정상인지와 필수 test를 사람이 정합니다.
- 병합 판단: 충돌 해결안과 민감 경로 변경 사유를 사람이 승인합니다.
- 승격·배포: 승인자, 판단 사유, 릴리스·운영 진행 여부를 고객사가 결정합니다.

:::details 사람 판단 항목별 담당자·시점·중단 기준 보기

| 사람이 결정할 항목 | 언제 결정하나요? | 누가 결정하나요? | 결과는 어디에 남나요? | 없으면 어떻게 되나요? |
|---|---|---|---|---|
| 새 BANK-OM ID 또는 기존 ID 유지 | 독립 기능이 추가되거나 후속 commit의 목적이 바뀐 때 | 기능 책임자·변경관리 담당자 | Registry와 commit의 `Customization-ID` | ID 소유가 불명하면 등록·승인 진행 금지 |
| `required_changed_paths` | 최초 등록 또는 후속 commit에서 새 파일이 나온 때 | 기능 책임자·개발 담당자 | 승인된 Manifest | 필수 파일이 정해지지 않으면 등록 변경안 승인 금지 |
| 간접 `upgrade_watch` 경로 | 직접 수정하지 않았지만 기능이 의존하는 공식 코드가 있을 때 | 개발 담당자·기능 책임자 | Manifest의 `upgrade_watch.paths` | 자동 검사가 간접 영향을 알 수 없으므로 담당자 검토 필요 |
| 공용 파일의 BANK-OM별 코드 정의 | 한 파일을 두 개 이상 BANK-OM 기능이 함께 바꿀 때 | 각 기능의 개발 담당자 | `shared-code-definitions.yaml` | 필수 정의 누락은 `ANALYSIS_ERROR`, 승인한 코드 누락은 `BLOCK` |
| Contract의 정상 동작·필수 test | 기능 최초 등록 또는 업무 동작이 바뀌 때 | 업무 책임자·QA·개발 담당자 | Contract·test 연결 | 필수 test 연결·실행 근거가 없으면 통과 금지 |
| Git 충돌 해결안 | vendor merge에서 공식 코드와 고객사 코드가 겹칠 때 | 기능 책임자·개발 담당자 | 해결 diff·commit·판단 기록 | 해결 선택이 없으면 vendor merge 중단 |
| `change-intent.yaml` | 병합 후 민감 경로 변경이 있을 때 | 기능 책임자·보안 담당자 | 변경 의도 파일과 승인 기록 | 필수 의도가 없으면 postmerge Phase 완료 금지 |
| 승인자·승인 시각·구체적 사유 | `APPROVAL` 결과를 받았거나 승격을 결정할 때 | 고객사가 지정한 승인자 | 결과 digest에 결속된 승인서 | 자리표시자·시간대 없는 시각·모호한 사유는 승인 거부 |
| 운영 승격·배포 판단 | 소스·산출물·Runtime 검증 후 | 고객사 운영·보안·서비스 책임자 | Release lock·산출물 digest·배포 승인 | 외부 입력이 없으면 소스 검사 완료만 표시하고 배포 완료로 표시 금지 |

:::

`required_changed_paths`는 `changed_paths`의 다른 이름이 아닙니다. `changed_paths`는 Git이 찾은 해당 기능의 전체 변경 파일이고, `required_changed_paths`는 그중 빠지면 기능 소실이 확실한 핵심 파일입니다. 자동화는 새 경로를 제안할 수 있지만 어느 파일이 핵심인지는 임의로 결정하지 않습니다.

## 4. 네 단계로 진행하는 버전 업그레이드

### 1단계 · 기준과 목표 버전 고정

**무엇을 하나요?** 현재 공식 버전, 현재 커스터마이징 commit, 새 공식 tag를 정확히 고정합니다. 솔루션은 새 공식 tag와 동일한 commit으로 공식 branch를 준비하고, 현재 활성 Candidate lock을 선택합니다.

- 사람이 할 일: 고객사가 목표 버전, 변경 금지 기간, 기능·승인 담당자를 확정합니다.
- 솔루션: tag·branch·commit 존재와 서로의 관계를 검사합니다.
- 완료 기준: 현재 기준 SHA와 목표 공식 SHA가 결과에 기록됩니다.
- 중단 기준: tag가 없거나 등록된 commit을 repository에서 찾을 수 없습니다.

:::details 솔루션 제공팀 실행 예시

```bash
python harness/om_workflow.py prep-official \
  --repo /path/to/OpenMetadata \
  --tag-ref 1.13.2-release \
  --branch official/om-1.13.2

python harness/om_workflow.py candidate-select --version 1.13.1
```

정상이면 공식 branch 준비 결과와 활성 Candidate lock 선택 결과가 `evidence/`에 생성됩니다. 두 명령 중 하나라도 실패하면 2단계로 이동하지 않습니다.

:::

### 2단계 · 병합 전 영향 검사

**무엇을 하나요?** 새 공식 버전이 고객사의 BANK-OM 변경 경로와 의존 경로를 바꾸었는지 병합 전에 확인합니다. BANK-OM ID는 고객사 커스터마이징 기능을 코드·테스트·승인 기록과 연결하는 이 솔루션의 관리 ID입니다.

- 사람이 할 일: 고객사가 영향 경로의 업무 중요도, 간접 `upgrade_watch` 추가 필요성, 병합 계속 여부를 판단합니다.
- 솔루션: 공식 버전 간 diff와 `upgrade_watch` 경로를 비교하고 결과를 하나의 digest로 고정합니다.
- 완료 기준: 결과가 `PASS` 또는 담당자가 검토할 수 있는 `APPROVAL`입니다.
- 중단 기준: 필수 commit·정책·등록 입력이 누락되었거나 결과가 `BLOCK`입니다.

:::details 솔루션 제공팀 실행 예시

```bash
python harness/om_workflow.py phase-preflight \
  --repo /path/to/OpenMetadata \
  --version 1.13.1 \
  --phase premerge \
  --base afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9 \
  --target 2763bf97...

python harness/om_workflow.py premerge-check \
  --repo /path/to/OpenMetadata \
  --version 1.13.1 \
  --base afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9 \
  --target 2763bf97...
```

`2763bf97...`는 읽기 쉽게 줄인 표시입니다. 실제 명령에는 저장소에서 확인한 전체 Git commit SHA를 입력합니다.

:::

### 3단계 · vendor merge와 충돌 해결

**무엇을 하나요?** 직전 커스터마이징 branch에 새 공식 버전을 병합해 새 업그레이드 후보를 만듭니다. `vendor merge`는 직전 커스터마이징 이력을 보존한 채 새 공식 코드를 Git merge하는 이 솔루션의 기본 업그레이드 전략입니다.

- 사람이 할 일: 고객사가 충돌 해결안을 승인하고, 후속 commit의 새 경로가 `required_changed_paths`·`upgrade_watch`·공용 코드 정의·Contract 변경을 필요로 하는지 결정합니다.
- 솔루션: 격리 branch에서 병합하고, 충돌 파일·해결 diff·실제 충돌률을 기록합니다. 병합 후 후보를 가리키는 등록 변경안과 Candidate lock도 제시합니다.
- 완료 기준: 미해결 Git 충돌이 없고, 고객사가 승인한 병합 후 Git commit SHA가 활성 Candidate lock에 고정되며, 실제 충돌률이 기록됩니다.
- 중단 기준: 업무 의미를 결정해야 하는 충돌에 고객사 판단이 없거나, 병합 중 예상하지 못한 변경이 확인됩니다.

> **주의:** 충돌률은 예상값을 입력하지 않습니다. 실제 vendor merge에서 생성된 충돌 증거로 계산한 값만 4단계에 사용합니다.

:::details 충돌이 있을 때 처리 방식

1. 솔루션 제공팀이 충돌 파일과 서로 다른 코드 구간을 제시합니다.
2. 자동 합쳐지지 않는 JSON은 보조 도구로 겹치지 않는 항목만 제안합니다.
3. 고객사 담당자가 업무 규칙·화면 표현·API 행위를 선택합니다.
4. 솔루션 제공팀이 승인된 해결안을 반영하고 같은 파일을 다시 검토합니다.

:::

### 4단계 · 병합 후 검사와 승격 판단

**무엇을 하나요?** 병합된 후보에 BANK-OM 기능 코드·필수 경로·등록자료가 남아 있는지 확인하고, 실제 충돌률과 변경 의도를 위험 정책에 대입합니다. `change-intent.yaml`은 민감 경로를 왜 변경했는지 고객사가 승인한 사유를 기록한 파일입니다. 병합 후 검사 전에 작성하며 민감 경로 검사가 이 파일을 읽습니다.

배포 산출물 digest가 있을 때만 API·화면·DB 동작을 확인하는 Runtime Contract를 같은 단계에 포함합니다. 이 문서의 `승격`은 검사한 후보를 릴리스 대상으로 고정할 수 있다는 판단이며, 고객사 운영 배포 완료를 뜻하지 않습니다.

- 사람이 할 일: 고객사가 `change-intent.yaml`, Contract 결과, 승인 사유를 확정하고 재수정·재검사·승격 중 하나를 결정합니다.
- 솔루션: 등록 검증, 소스 검사, 업그레이드 위험 검사를 같은 후보에서 실행합니다.
- 완료 기준: 필수 검사가 `PASS` 또는 승인 조건을 명시한 `APPROVAL`이고, 고객사 승인이 같은 결과 digest에 결속됩니다.
- 중단 기준: `BLOCK`, `ANALYSIS_ERROR`, 필수 증거 누락, 후보 SHA 변경 중 하나라도 있습니다.

:::details 솔루션 제공팀 실행 예시

```bash
python harness/om_workflow.py phase-preflight \
  --repo /path/to/OpenMetadata \
  --version 1.13.1 \
  --phase postmerge \
  --change-intent /path/to/change-intent.yaml \
  --conflict-rate <실제-측정값>

python harness/om_workflow.py postmerge-check \
  --repo /path/to/OpenMetadata \
  --version 1.13.1 \
  --change-intent /path/to/change-intent.yaml \
  --conflict-rate <실제-측정값>
```

산출물이 준비된 후 Runtime Contract까지 묶으려면 `postmerge-check`에 검증한 `--artifact-digest <SHA-256>`를 추가합니다. 산출물이 없는 소스 검사 단계에서 가상 digest를 만들지 않습니다.

예시의 `--version 1.13.1`은 병합 전에 승인된 기준 등록 묶음을 선택합니다. 실제 검사 대상 코드는 Candidate lock에 고정된 1.13.2 vendor-merge 후보입니다.

:::

## 5. 결과는 어떻게 보나요?

한 번의 단계 실행은 같은 판단에서 만든 세 가지 파일을 남깁니다.

| 파일 | 읽는 사람 | 답하는 질문 |
|---|---|---|
| `manager-summary.json` | 고객사 책임자·승인자 | 지금 계속할 수 있는가? 무엇을 승인해야 하는가? |
| `practitioner-detail.json` | 고객사·제공팀 실무자 | 어느 검사가 어떤 근거로 판정했는가? |
| `result.json` | 자동화·감사 담당자 | 입력 SHA·정책·결과 digest가 일치하는가? |

| 판정 | 의미 | 다음 행동 |
|---|---|---|
| `PASS` | 해당 검사의 자동 기준 충족 | 다음 단계로 이동 |
| `APPROVAL` | 자동 실패는 아니지만 사람 검토가 필요 | 판단 사유와 승인자를 기록한 후 진행 |
| `BLOCK` | 코드·정책·테스트 조건 미충족 | 입력만 고치면 같은 commit, 코드를 고치면 새 commit과 Candidate lock으로 재검사 |
| `ANALYSIS_ERROR` | 입력 누락, 잘못된 형식, 실행 환경 오류 | 입력·환경을 복구하고 해당 단계부터 재실행 |

```bash
python harness/om_workflow.py phase-status \
  --result evidence/<run-id>/result.json
```

`verified: true`는 저장된 결과 digest가 내용과 일치한다는 뜻입니다. 검사 판정이 자동으로 `PASS`로 바뀐다는 뜻은 아닙니다.

## 6. 실패했을 때는 어디서 다시 시작하나요?

| 상황 | 확인할 곳 | 재시작 기준 |
|---|---|---|
| 공식 tag·commit 누락 | 1단계 공식 branch 준비 결과 | 정확한 tag를 fetch한 뒤 1단계 재실행 |
| 병합 전 `APPROVAL` | 영향 BANK-OM ID와 경로 | 고객사 영향 검토 기록 후 3단계 진행 |
| Git 충돌 | 충돌 파일·해결 diff·담당 BANK-OM ID | 해결안 승인·test 후 3단계 완료 |
| 병합 후 `BLOCK` | `practitioner-detail.json`의 해당 gate | 코드 또는 등록자료 수정 후 새 Candidate lock으로 4단계 재실행 |
| `ANALYSIS_ERROR` | 입력 파일·Git 객체·실행 로그 | 후보 코드를 바꾸지 말고 입력·환경을 복구한 후 재실행 |
| 검사 후 commit 변경 | Candidate lock과 repository HEAD | 기존 승인을 재사용하지 않고 4단계 전체 재실행 |

> **중단 및 상위 검토:** 고객사 업무 규칙을 코드로 선택해야 하는 충돌, 승인자 미지정, 실제 배포 산출물 누락, 운영 환경 접근 불가는 자동화가 임의로 채우지 않습니다. 고객사 책임자의 입력을 받은 후 재개합니다.

## 7. 현재 1.13.1 → 1.13.2 예시의 위치

| 항목 | 현재 상태 |
|---|---|
| 1.13.1 커스터마이징 기준선·등록·소스·Runtime Contract | 완료 |
| 공식 1.13.2 확인·병합 전 영향 검사 | 완료 |
| 실제 1.13.2 vendor-merge 후보·실제 충돌률 | 미생성·다음 실행 대상 |
| 병합 후 검사·고객사 승인·운영 승격 | 미실행 |

이 표의 “완료”는 소스 또는 예행 환경의 확인 상태입니다. 고객사 운영 환경에 배포됐다는 뜻이 아닙니다.

## 8. 고객사가 승격 전에 받아야 할 자료

- 실제 vendor-merge 후보 Git commit SHA
- 공식 기준·목표 commit SHA와 Candidate lock
- 병합 전·병합 후 `manager-summary.json`
- 세부 검사 근거가 포함된 `practitioner-detail.json`
- digest가 검증된 `result.json`
- 충돌 파일·해결 diff·실제 충돌률
- 승인자·승인 시각·구체적 판단 사유가 포함된 승인 기록
- 실제 배포 파일이 있는 경우 산출물 digest와 Runtime Contract 결과

위 자료가 같은 후보 commit과 같은 결과 digest를 가리키는지 확인한 후에만 승격을 결정합니다.
