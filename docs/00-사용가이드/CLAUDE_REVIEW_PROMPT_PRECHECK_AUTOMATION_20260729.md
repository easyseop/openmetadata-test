# OM_TEMP 검사 전 사전 준비 자동화 설계 검토 요청

첨부한 `OM_TEMP_검사전_사전준비_자동화_설계서_20260729.md`와 관련 코드 파일을 함께 검토해 주세요.

이 요청은 구현을 맡기는 요청이 아닙니다. 첫 답변에서는 파일을 수정하거나 새 코드를 작성하지 말고, 설계의 사실 오류·누락·위험만 보고해 주세요.

## 검토 목표

개발자가 BANK-OM ID를 포함해 commit하면 검사 실행 전까지 필요한 관리 파일 변경안이 자동 생성되고, 사람이 업무 판단이 필요한 항목만 검토·승인한 뒤 실제 등록자료에 반영되는 구조를 만들려 합니다.

설계가 다음 두 조건을 동시에 만족하는지 확인해 주세요.

1. Git으로 계산할 수 있는 값은 사람이 중복 입력하지 않는다.
2. 업무 의미를 판단해야 하는 값은 자동화가 추측하거나 덮어쓰지 않는다.

## 반드시 실제 코드와 대조할 파일

- `harness/acgh/gitprim.py`
- `harness/acgh/invariants.py`
- `harness/acgh/manifest.py`
- `harness/acgh/registry.py`
- `harness/acgh/vendor_rebuild.py`
- `harness/acgh/drift.py`
- `harness/acgh/policy_drift.py`
- `harness/acgh/candidate.py`
- `harness/acgh/testruns.py`
- `harness/acgh/schema/manifest.schema.json`
- `harness/acgh/schema/customization-registry.schema.json`
- `harness/registrations/om-temp-1.13.0/generate_manifest_drafts.py`
- `harness/registrations/om-temp-1.13.0/generate_registration_bundle.py`
- `harness/registrations/om-temp-1.13.0/customization-registry.yaml`
- `harness/registrations/om-temp-1.13.0/manifests/BANK-OM-007.yaml`
- `harness/registrations/kb-openmetadata/run_source_candidate_gates.py`
- `harness/registrations/kb-openmetadata/run_runtime_contracts.py`

HTML 위키나 설계서의 설명만 믿지 말고 위 코드에서 실제 읽는 필드, 생성하는 산출물, 차단 조건을 확인해 주세요.

## 중점 검토 항목

### 1. SHA 역할 분리

- `Registry source.snapshot_sha`는 과거 source snapshot 재구성 기준으로 실제 사용되는가?
- 일반 후속 commit에서 이 SHA를 갱신하지 않는 설계가 맞는가?
- 현재 최신 custom HEAD를 `commit-inventory.yaml`과 Candidate lock에 분리해 기록하는 방식이 적절한가?
- BANK-OM별 commit SHA의 원본을 Git으로만 두고 자동 생성 inventory를 파생 자료로 두는 것이 재현 가능하고 감사 가능한가?

### 2. 버전 관리

- 1.13.0과 1.13.1 등록 폴더를 분리하는 방식이 적절한가?
- 같은 BANK-OM ID를 새 공식 버전에서도 유지하되 버전별 SHA와 `changed_paths`를 다시 계산하는 것이 맞는가?
- 같은 버전의 후속 commit은 최신 custom HEAD까지 다시 계산하면서 과거 상태는 검사기 repository Git 이력으로 보존하는 방식이 충분한가?

### 3. changed paths의 두 의미

설계는 다음 값을 분리합니다.

- Manifest `changed_paths`: BANK-OM ID의 commit이 실제로 변경한 파일
- `current-diff-paths.txt`: patch와 custom 최종 상태가 다른 파일

파일을 변경했다가 뒤 commit에서 원복한 경우 두 목록이 달라질 수 있습니다. 이 구분이 현재 T40, T26, T93의 실제 동작과 일치하는지 확인해 주세요.

### 4. source snapshot 자료

다음 파일이 현재 코드에서 어떤 판단에 사용되는지 확인해 주세요.

- `source-diff-paths.txt`
- `source-snapshot-path-owners.yaml`
- `shared-path-owners.yaml`

설계는 이 파일들을 일반 후속 commit에서 갱신하지 않습니다. 이 결정이 맞는지, 이름 때문에 최신 소유정보처럼 오해될 가능성이 있는지 검토해 주세요.

### 5. 사람 입력값 보존

자동화가 다음 값을 그대로 보존해야 한다는 설계가 충분한지 확인해 주세요.

- `required_changed_paths`
- 수정하지 않은 watch 의존 경로
- Contract와 direct test
- `series.depends_on`
- Registry의 제목·담당자·중요도·상태
- Contract의 업무 정상 조건과 필수 test

새 변경 파일 때문에 기존 값이 더 이상 유효하지 않을 때 단순 보존이 오히려 위험해지는 경우와 필요한 차단 조건을 제시해 주세요.

### 6. 신규 ID와 기존 ID

- 기존 ID 후속 commit을 자동 발견하는 방식
- 신규 ID를 발견했을 때 최종 파일을 임의 값으로 만들지 않고 `REVIEW_REQUIRED`로 중단하는 방식
- `series.allowed: false`인 ID에 두 번째 commit이 생겼을 때 승인받는 방식
- retired ID가 다시 사용됐을 때 차단하는 방식

각 동작이 현재 검사기의 불변조건과 맞는지 확인해 주세요.

### 7. 승인 안전성

- `plan → proposal digest → approval → apply` 구조가 승인 후 branch나 등록자료가 달라지는 문제를 차단하는가?
- proposal에 어떤 입력 digest가 추가로 들어가야 하는가?
- 등록 폴더 전체 digest, 개별 파일 digest, Git tree SHA 중 무엇이 필요한가?
- 승인 기록을 Git에 보관할지 실행 evidence로 보관할지 판단해 주세요.
- 동시 작업자가 같은 등록 폴더에 제안을 적용할 때 발생할 경쟁 조건을 검토해 주세요.

### 8. Git edge case

다음을 빠짐없이 검토해 주세요.

- merge commit
- revert commit
- commit에서 파일 수정 후 다른 commit에서 원복
- rename
- delete
- binary file
- symlink
- submodule
- Git LFS
- 한글·공백 파일명
- 같은 ID commit 사이에 다른 ID commit이 끼는 경우
- ID가 없는 commit
- 여러 ID가 있는 commit
- 등록되지 않은 ID
- branch가 rebase 또는 force-push된 경우
- patch와 custom의 공통 기준을 계산할 수 없는 경우
- working tree에 commit되지 않은 변경이 있는 경우

각 경우에 `READY`, `REVIEW_REQUIRED`, `BLOCKED`, `ERROR` 중 어떤 결과가 맞는지 제안해 주세요.

### 9. Manifest v2

- 새 자동화가 `allowed_changed_paths`와 `candidate_additional_paths`를 생성하지 않는지
- 기존 v1 등록자료를 읽기만 하고 새 출력은 v2로 만드는 전략이 필요한지
- `run_source_candidate_gates.py`의 T41 입력이 현재 v1 필드를 읽는다는 설계서의 지적이 맞는지
- `manifest.declared_changed_paths()`로 통일하면 다른 검사와 의미가 일치하는지

### 10. Candidate lock과 test-run-set

- Candidate lock을 준비 단계에서 성공 증거처럼 만들지 않는 결정이 맞는지
- 소스 검사 시작 시 source tree digest로 만드는 lock과 실제 build artifact digest를 사용하는 lock을 어떻게 구분해야 하는지
- test-run-set은 실제 test 실행 후에만 생성해야 한다는 설명이 맞는지
- 준비 자동화와 검사 evidence 사이에 동일한 custom HEAD SHA를 강제하는 방법이 충분한지

### 11. 테스트 계획

설계서의 단위·통합·회귀 test로 다음을 증명할 수 있는지 확인해 주세요.

- SHA 자동 발견
- 사람 값 보존
- 결정론적 재생성
- 승인한 제안서만 적용
- 버전 간 파일 격리
- source snapshot 자료 불변
- Manifest v2 gate 동작
- 실제 OM_TEMP 1.13.0 BANK-OM-001~007 재현

빠진 test와 예상 assertion을 구체적으로 제안해 주세요.

### 12. 문장과 운영 가능성

설계 문장을 한 문장씩 읽고 다음을 확인해 주세요.

- 누가 어떤 시점에 무엇을 실행하는지 한 가지로만 해석되는가?
- 현재 구현과 제안 기능이 명확히 구분되는가?
- 자동 생성, 자동 검사, 사람 판단, 사람 승인이 구분되는가?
- 파일을 갱신하는 경우와 그대로 두는 경우가 명확한가?
- 신입 개발자가 구현을 맡아도 추가 질문 없이 모듈·입력·출력·차단 조건·test를 이해할 수 있는가?

## 원하는 답변 형식

### 1. 발견 사항

| 우선순위 | 설계서 위치 또는 코드 위치 | 발견한 문제 | 발생 가능한 잘못된 동작 | 근거 | 권장 수정 |
|---|---|---|---|---|---|

우선순위:

- **치명적**: 잘못된 등록자료 생성, 승인 우회, 실제 검사 대상 불일치 가능
- **높음**: 데이터 손실, 사람 값 덮어쓰기, 후속 commit 누락 가능
- **중간**: edge case 또는 test 누락
- **낮음**: 용어, 문장, 파일명, 구성 개선

### 2. 설계 결정별 판정

다음 각 항목에 `수용`, `조건부 수용`, `거절` 중 하나를 표시하고 이유를 적어 주세요.

- Git을 BANK-OM SHA 원본으로 사용
- Registry source snapshot과 최신 custom HEAD 분리
- `commit-inventory.yaml` 추가
- `current-diff-paths.txt` 추가
- source snapshot 자료 불변
- plan/apply 분리
- digest 기반 승인
- 신규 ID에서 REVIEW_REQUIRED
- Manifest v2만 생성
- merge commit 차단 유지

### 3. 추가해야 할 차단 조건

설계에 없는 차단 조건을 실행 순서와 함께 적어 주세요.

### 4. 추가해야 할 test

test 이름, 입력 Git 이력, 예상 상태 또는 assertion까지 적어 주세요.

### 5. 구현 순서 수정안

현재 5단계 도입 순서보다 안전한 순서가 있다면 제안해 주세요.

확인할 수 없는 내용은 추측하지 말고 `추가 코드 또는 실제 OM_TEMP repository 확인 필요`라고 표시해 주세요.
