# OM_TEMP 1.13.0 Manifest 작성 단계별 가이드

## 1. 이 가이드의 목적

`easyseop/OM_TEMP`의 `custom/om-1.13.0` branch에는 공식 OpenMetadata
1.13.0 코드와 BANK-OM-001~007 커스터마이징 코드가 들어 있습니다.

이제 해야 할 일은 각 BANK-OM 커밋이 실제로 변경한 파일을 Git에서 확인하고,
그 결과를 `easyseop/openmetadata-test`의 Manifest에 등록하는 것입니다.
Manifest는 커스터마이징별 변경 범위와 필수 구성요소를 검사기에 알려 주는
YAML 파일입니다.

현재 OM_TEMP에는 Manifest가 없으며, 아직 검사기 통과·검증 태그 생성·행내
배포를 완료한 상태가 아닙니다.

## 2. Manifest는 언제 만드는가

권장 순서는 다음과 같습니다.

1. 개발 전에 관리 담당자가 BANK-OM ID와 기능 목적을 정합니다.
2. 개발자는 임시 작업 branch에서 코드를 작성하고 BANK-OM ID가 들어간 commit을
   만듭니다.
3. commit이 만들어지면 Git에서 실제 변경 파일을 확인해 Manifest를 확정합니다.
4. 검사기가 Manifest, commit의 BANK-OM ID, 실제 변경 파일이 서로 일치하는지
   확인합니다.
5. 필요한 코드 test까지 통과한 정확한 `custom` branch commit에 검증 태그를
   붙입니다.
6. 배포 절차는 검증 태그가 붙은 commit만 입력으로 받습니다.

개발 전에 변경 파일을 추측해 Manifest를 확정하면 실제 코드와 달라질 수
있습니다. 반대로 Manifest 없이 배포까지 진행하면 어떤 커스터마이징이 빠졌는지
자동으로 판단할 기준이 없습니다.

### 배포 차단 조건

Manifest 파일이 존재한다는 사실만으로 배포를 허용해서는 안 됩니다. 다음 조건이
모두 충족되어야 배포 검토 단계로 넘어갑니다.

- 활성 BANK-OM ID마다 Manifest가 존재합니다.
- Manifest가 스키마 검사를 통과합니다.
- Manifest의 변경 파일과 실제 Git commit의 변경 파일이 일치합니다.
- commit 메시지에 올바른 `Customization-ID`가 있습니다.
- 필수 파일과 연결된 test가 검사 기준을 통과합니다.
- 검사 결과가 배포할 코드와 동일한 Git commit SHA를 가리킵니다.

OM_TEMP는 업그레이드 시연 준비를 위해 코드부터 만든 상태입니다. 이번에는
실제 commit을 기준으로 Manifest를 역등록한 뒤 검사하며, 검사 통과 전에는
검증 태그와 배포 승격을 만들지 않습니다.

## 3. 작업할 저장소 두 개

| 저장소 | 이번 단계에서 확인하거나 저장할 내용 |
|---|---|
| `easyseop/OM_TEMP` | 실제 OpenMetadata 1.13.0 코드, BANK-OM commit과 변경 파일 |
| `easyseop/openmetadata-test` | 새 1.13.0 Manifest, 등록부, 계약, 검사 설정과 결과 |

Manifest를 OM_TEMP 안에 넣지 않습니다. 실제 제품 코드와 검사 기준을 같은
저장소에 중복 저장하면 업그레이드 과정에서 어느 쪽이 기준인지 혼동될 수
있기 때문입니다.

기존 `harness/registrations/kb-openmetadata/`는 1.13.1 기준 등록자료입니다.
그 파일을 1.13.0 내용으로 덮어쓰지 않고, 실제 등록 작업을 시작할 때
`harness/registrations/om-temp-1.13.0/`을 별도로 만듭니다.

## 4. 시작 전 확인

### 4.1 OM_TEMP를 처음 받는 경우

```bash
git clone https://github.com/easyseop/OM_TEMP.git
cd OM_TEMP
git fetch --tags origin patch/om-1.13.0 custom/om-1.13.0
git switch --track origin/custom/om-1.13.0
```

### 4.2 이미 OM_TEMP가 있는 경우

OM_TEMP 폴더에서 실행합니다.

```bash
git fetch --tags origin patch/om-1.13.0 custom/om-1.13.0
git switch custom/om-1.13.0
git pull --ff-only origin custom/om-1.13.0
```

### 4.3 현재 기준값 확인

```bash
git rev-parse origin/patch/om-1.13.0
git rev-parse origin/custom/om-1.13.0
git rev-list --count \
  origin/patch/om-1.13.0..origin/custom/om-1.13.0
git diff --name-only \
  origin/patch/om-1.13.0..origin/custom/om-1.13.0 | wc -l
```

현재 원격에서 기대하는 값은 다음과 같습니다.

| 확인 항목 | 기대값 |
|---|---|
| 공식 1.13.0 기준 branch | `patch/om-1.13.0` |
| 공식 기준 snapshot SHA | `2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50` |
| 커스터마이징 branch | `custom/om-1.13.0` |
| 현재 커스터마이징 SHA | `7d19c8952612e77467b0a80d6287170d814f1de1` |
| BANK-OM commit 수 | 8개 |
| 두 branch 사이 변경 파일 수 | 111개 |

값이 다르면 Manifest 작성을 중단하고 원격 branch가 추가로 변경됐는지 먼저
확인합니다. 다른 코드 상태를 기준으로 Manifest를 만들면 이후 검사가
정상적으로 비교할 수 없습니다.

## 5. BANK-OM commit 목록 확인

OM_TEMP 폴더에서 다음 명령을 실행합니다.

```bash
git log --reverse \
  --format='%H | %s | %(trailers:key=Customization-ID,valueonly)' \
  origin/patch/om-1.13.0..origin/custom/om-1.13.0
```

현재 확인되어야 하는 commit은 다음과 같습니다.

| BANK-OM ID | Git commit SHA | 내용 |
|---|---|---|
| BANK-OM-001 | `4df83b311f1ec38156c9b992f34607b22224db85` | InstanceCode |
| BANK-OM-002 | `68ebed4801715f0c30b8a1a614572183fa6097b8` | QueryReport |
| BANK-OM-003 | `57ee1b3b23d644f13e0c1716f0810ddf962e5264` | Data Assertions |
| BANK-OM-004 | `274f2b79b424e01537a7f2253c33aeecb43aaac4` | 은행 컬럼 표시 |
| BANK-OM-005 | `d983f7c540d3fa1fe56ca91adef3f37374890f77` | 한글 IME |
| BANK-OM-006 | `010750c514e9bbb7a765414ded3b161b1f5eb621` | Sybase |
| BANK-OM-007 | `62e39da8be65c3ff259802c1cd35f4b0c8baa333` | Tibero 최초 적용 |
| BANK-OM-007 | `7d19c8952612e77467b0a80d6287170d814f1de1` | Tibero 후속 보완 |

BANK-OM ID는 업무 기능 번호입니다. Git commit SHA는 Git이 각 코드 저장 시점에
부여한 식별값입니다. BANK-OM-007처럼 하나의 기능을 두 번 수정하면 같은
BANK-OM ID에 서로 다른 Git commit SHA가 연결될 수 있습니다.

목록에서 BANK-OM ID가 비어 있거나 하나의 commit에 ID가 여러 개 나오면
Manifest를 작성하기 전에 commit 기록부터 수정해야 합니다.

각 커밋의 실제 GitHub 캡처, 기능 단위 판단 근거, Manifest 전체는
[OM_TEMP 커밋별 Manifest 등록 가이드](OM_TEMP_커밋별_Manifest_등록_가이드.md)에서
ID별 펼치기로 확인할 수 있습니다.

## 6. 각 commit에서 실제 변경 파일 확인

먼저 BANK-OM-001로 절차를 확인한 뒤 같은 방법을 002~007에 반복합니다.

### 6.1 파일 상태와 diff 확인

```bash
git show --name-status \
  4df83b311f1ec38156c9b992f34607b22224db85
```

출력 첫 글자의 의미는 다음과 같습니다.

| 표시 | 의미 | Manifest 판단 |
|---|---|---|
| `A` | 이 commit에서 새 파일을 추가함 | `allowed_changed_paths`에 등록 |
| `M` | 공식 코드에 있던 파일을 수정함 | `allowed_changed_paths`에 등록 |
| `D` | 기존 파일을 삭제함 | 삭제가 의도된 변경인지 담당자 확인 후 등록 |
| `R` | 파일 이름이나 경로를 변경함 | 이전 경로와 새 경로를 함께 검토 |

파일 내용을 직접 비교하려면 다음 명령을 실행합니다.

```bash
git show \
  4df83b311f1ec38156c9b992f34607b22224db85 \
  -- openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
```

이 비교에서 `Entity.java`는 공식 OpenMetadata에 있던 파일에
`INSTANCE_CODE` 연결을 추가한 공용 코드이고,
`InstanceCodeResource.java`는 InstanceCode API를 제공하기 위해 새로 추가한
커스터마이징 구현 파일입니다.

### 6.2 `allowed_changed_paths` 목록 만들기

다음 명령은 선택한 commit이 변경한 모든 파일을 YAML 목록 형태로 출력합니다.

```bash
git show --name-only --format= \
  4df83b311f1ec38156c9b992f34607b22224db85 \
  | sed '/^$/d' \
  | sort -u \
  | sed 's/^/    - /'
```

출력된 파일을 빠짐없이 해당 ID의 `allowed_changed_paths`에 넣습니다. 폴더 전체를
`**`로 등록하지 않습니다. 현재 커밋에서 실제로 확인한 파일만 개별 경로로
등록해야 다음 변경에서 범위 밖 파일을 찾을 수 있습니다.

### 6.3 공용 파일 확인

하나의 파일을 여러 BANK-OM commit이 수정할 수 있습니다. 예를 들어 다음 세
파일은 BANK-OM-001과 BANK-OM-002가 모두 수정합니다.

- `openmetadata-service/src/main/java/org/openmetadata/service/Entity.java`
- `openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/CollectionDAO.java`
- `openmetadata-service/src/main/java/org/openmetadata/service/search/SearchIndexFactory.java`

이 경우 파일을 한 ID에서 빼지 않습니다. 두 Manifest의
`allowed_changed_paths`에 모두 넣고 `shared-path-owners.yaml`에도 두 ID를
등록합니다.

```yaml
openmetadata-service/src/main/java/org/openmetadata/service/Entity.java:
  - BANK-OM-001
  - BANK-OM-002
```

공용 파일 등록은 “파일 전체를 두 기능이 똑같이 소유한다”는 뜻이 아닙니다.
각 ID의 commit이 그 파일 안에서 실제로 다른 상수·API 연결·설정값을 추가했다는
뜻입니다. 최종 등록 전에는 각 commit의 diff를 열어 두 ID가 실제로 수정한
내용을 확인합니다.

## 7. Manifest 항목을 정하는 기준

Manifest 항목은 같은 수준의 선택지가 아니라 서로 다른 질문에 답합니다.

| Manifest 항목 | 답해야 하는 질문 | 등록 방법 | 검사 결과 |
|---|---|---|---|
| `allowed_changed_paths` | 이 BANK-OM commit이 실제로 변경한 파일은 무엇인가? | 최초 commit의 전체 변경 파일을 Git에서 추출 | 목록 밖 변경은 `BLOCK`, 목록 안 파일이 최종 코드에서 바뀌지 않으면 `APPROVAL` |
| `required_changed_paths` | 어떤 파일이 빠지거나 공식 상태로 돌아가면 이 기능의 필수 구현이 빠졌다고 즉시 판단할 수 있는가? | `allowed` 중 핵심 파일만 담당자가 선택 | 누락되거나 공식 원본과 같으면 `BLOCK` |
| `candidate_additional_paths` | 같은 ID의 후속 commit이 처음으로 변경 범위에 추가한 파일은 무엇인가? | 최초 `allowed`에 없고 후속 commit이 변경한 경로만 등록 | 현재 변경 범위와 필수 파일 검사에 포함 |
| `upgrade_watch.paths` | 다음 공식 버전이 바뀔 때 이 기능과의 연결을 다시 검토해야 할 파일은 무엇인가? | Manifest 생성기가 실제 변경 파일을 자동 포함하고, 미수정 의존 파일은 후보 제안과 담당자 검토로 추가 | 공식 버전 사이에서 해당 경로가 바뀌면 `APPROVAL` |
| `assurance.contracts` | 파일이 남아 있다는 사실 외에 어떤 업무 동작을 test할 것인가? | `contracts.yaml`에 정의한 계약 ID를 연결 | 계약이나 test 연결이 없으면 통과 금지 |
| `series.depends_on` | 이 기능보다 먼저 적용돼야 하는 다른 BANK-OM은 무엇인가? | 실제 선행 기능만 등록 | 순서 위반이나 순환 관계는 `BLOCK` |

### 7.1 `allowed`와 `required`의 차이

`allowed`에는 commit이 변경한 파일 전체가 들어갑니다.
`required`에는 그중 필수 기능의 존재를 판단하는 대표 파일만 들어갑니다.

BANK-OM-001에서는 다음처럼 구분할 수 있습니다.

```yaml
implementation:
  allowed_changed_paths:
    - openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
    - openmetadata-service/src/main/java/org/openmetadata/service/resources/instancecode/InstanceCodeResource.java
    - openmetadata-spec/src/main/resources/json/schema/entity/data/instanceCode.json
    # 실제 commit이 변경한 나머지 파일도 모두 계속 등록

  required_changed_paths:
    - openmetadata-service/src/main/java/org/openmetadata/service/resources/instancecode/InstanceCodeResource.java
    - openmetadata-spec/src/main/resources/json/schema/entity/data/instanceCode.json
```

`Entity.java`도 실제 변경 파일이므로 `allowed`에서 빠지면 안 됩니다. 다만
이 파일은 여러 기능이 함께 사용하는 공용 파일이므로, 파일 전체가 다르다는
사실만으로 InstanceCode 기능 전체가 남았다고 판단하기 어렵습니다. 그래서
InstanceCode API 구현 파일과 스키마 파일을 `required`의 대표 근거로 사용하고,
API 동작은 계약 test로 별도 확인합니다.

### 7.2 현재 `upgrade_watch` 등록 방법

T42는 Manifest의 `upgrade_watch.paths`를 공식 버전 전후와 비교합니다. 이 목록을
만들 때는 현재 다음 두 방식을 함께 사용합니다.

1. Manifest 생성기가 각 BANK-OM 커밋의 실제 변경 파일을 Git에서 읽어
   `allowed_changed_paths`와 `upgrade_watch.paths`에 함께 반영합니다. 사용자가
   같은 경로를 두 번 직접 입력하지 않습니다.
2. 커스터마이징이 직접 수정하지 않았지만 호출하거나 구조에 의존하는 공식 파일은
   담당자가 `watch_dependencies`로 추가합니다.
3. 새 공식 버전에서 바뀐 파일 이름을 커스터마이징 코드가 직접 참조하면 검사기가
   추가 watch 후보와 참조한 커스터마이징 파일을 결과에 제시합니다.
4. 후보는 자동으로 Manifest를 수정하지 않습니다. 담당자가 실제 의존 관계인지
   확인한 뒤 등록합니다.

따라서 실제 변경 파일 자동 포함과 직접 참조 후보 제시는 구현되어 있습니다.
다만 런타임 설정, 간접 호출, 문자열 없이 연결되는 구조처럼 코드에 파일·기호 이름이
드러나지 않는 의존 관계는 담당자가 직접 확인해야 합니다.

## 8. BANK-OM-007 후속 commit 처리

BANK-OM-007에는 commit이 두 개 있습니다.

- 최초 적용: `62e39da8be65c3ff259802c1cd35f4b0c8baa333`
- 후속 보완: `7d19c8952612e77467b0a80d6287170d814f1de1`

최초 commit의 파일은 `allowed_changed_paths`에 넣습니다. 후속 commit에서
처음 등장한 경로는 `candidate_additional_paths`에 넣습니다.

다음 명령으로 최초 목록에 없고 후속 commit에만 있는 경로를 확인합니다.

```bash
comm -13 \
  <(git show --name-only --format= \
    62e39da8be65c3ff259802c1cd35f4b0c8baa333 \
    | sed '/^$/d' | sort -u) \
  <(git show --name-only --format= \
    7d19c8952612e77467b0a80d6287170d814f1de1 \
    | sed '/^$/d' | sort -u)
```

현재 결과는 다음 두 파일입니다.

```text
openmetadata-ui/src/main/resources/ui/src/generated/entity/services/connections/serviceConnection.ts
openmetadata-ui/src/main/resources/ui/src/utils/DatabaseServiceUtils.test.tsx
```

따라서 BANK-OM-007 Manifest에는 다음 항목이 필요합니다.

```yaml
implementation:
  candidate_additional_paths:
    - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/connections/serviceConnection.ts
    - openmetadata-ui/src/main/resources/ui/src/utils/DatabaseServiceUtils.test.tsx

series:
  allowed: true
  depends_on: []
```

`candidate_additional_paths`는 Git commit SHA를 대신하는 값이 아닙니다. Git
commit SHA는 patch-lock에 두 개 모두 기록하고, 이 항목은 두 번째 commit으로
해당 기능의 변경 범위에 새로 들어온 파일 경로를 검사기에 알려 줍니다.

## 9. Manifest 파일 작성

### 9.1 자동 생성 도구 사용 여부

현재 저장소에는 OM_TEMP 1.13.0 commit을 읽어 Manifest 등록본을 다시 만드는
`harness/registrations/om-temp-1.13.0/generate_manifest_drafts.py`가 있습니다.
다음 명령을 실행하면 기록된 Git commit의 전체 변경 파일을 다시 추출해
BANK-OM-001~007 Manifest 7개를 생성합니다.

```bash
./.venv/bin/python \
  harness/registrations/om-temp-1.13.0/generate_manifest_drafts.py \
  --repo <OM_TEMP가-있는-절대경로>
```

스크립트는 Git이 확정할 수 있는 전체 변경 파일과 BANK-OM-007의 후속 추가
파일을 자동으로 만듭니다. `required`, 미수정 의존 파일, 계약은 기능 의미를
판단해야 하므로 스크립트 안의 명시적인 검토값으로 관리합니다.

`harness/registrations/kb-openmetadata/materialize_exact_scopes.py`는 기존
1.13.1 등록자료 전용이므로 이번 1.13.0 생성에는 사용하지 않습니다.

### 9.2 파일 위치

`easyseop/openmetadata-test`에서 새 등록 폴더를 준비합니다.

```bash
cd openmetadata-test
mkdir -p harness/registrations/om-temp-1.13.0/manifests
```

```text
harness/registrations/om-temp-1.13.0/
├── customization-registry.yaml
├── contracts.yaml
├── patch-source-lock.yaml
├── shared-path-owners.yaml
├── source-diff-paths.txt
└── manifests/
    ├── BANK-OM-001.yaml
    ├── BANK-OM-002.yaml
    ├── BANK-OM-003.yaml
    ├── BANK-OM-004.yaml
    ├── BANK-OM-005.yaml
    ├── BANK-OM-006.yaml
    └── BANK-OM-007.yaml
```

현재 이 폴더와 BANK-OM-001~007 Manifest 등록본은 생성되어 있습니다.
Manifest 7개는 현재 스키마 및 기본 의미 검사를 통과했습니다. 다만 제품 build,
업무 동작 test, 1.13.1 업그레이드 비교는 아직 실행 전이므로 배포 승인 상태는
아닙니다.

### 9.3 BANK-OM-001 기본 형태

아래 코드는 항목 구조를 설명하기 위해 일부 경로만 넣은 축약 예시입니다.
검사 입력으로 그대로 사용하면 안 됩니다. 실제 파일에는
`allowed_changed_paths`와 `upgrade_watch.paths`를 생략 없이 넣어야 합니다.

```yaml
schema_version: 1
customization_id: BANK-OM-001
status: active
kind: core-patch
title: InstanceCode

implementation:
  allowed_changed_paths:
    - openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
    - openmetadata-service/src/main/java/org/openmetadata/service/resources/instancecode/InstanceCodeResource.java
    - openmetadata-spec/src/main/resources/json/schema/entity/data/instanceCode.json

  required_changed_paths:
    - openmetadata-service/src/main/java/org/openmetadata/service/resources/instancecode/InstanceCodeResource.java
    - openmetadata-spec/src/main/resources/json/schema/entity/data/instanceCode.json

upgrade_watch:
  paths:
    - openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
    - openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/CollectionDAO.java
    - openmetadata-service/src/main/java/org/openmetadata/service/search/SearchIndexFactory.java

assurance:
  contracts:
    - CONTRACT-INSTANCE-CODE
  direct_tests: []

series:
  allowed: false
  depends_on: []
```

현재 001~007은 OpenMetadata 원본 경로 안의 코드를 변경하므로 `kind`는
`core-patch`입니다. 현재 스키마가 허용하는 종류는 다음 세 가지입니다.

| `kind` | 사용 기준 |
|---|---|
| `core-patch` | 공식 OpenMetadata 코드 경로를 변경함 |
| `extension` | `bank-extensions/**`처럼 공식 코드를 직접 수정하지 않는 별도 확장 모듈 |
| `governance` | `.bank/**`, `docs/bank/**`, `tests/bank/**`의 변경관리·검사 자료 |

## 10. Manifest 외에 함께 등록할 자료

Manifest만 만들면 전체 검사를 실행할 수 없습니다. 다음 자료도 같은
1.13.0 등록 폴더에서 연결해야 합니다.

| 자료 | 기록할 내용 |
|---|---|
| `customization-registry.yaml` | 공식 기준 SHA, 커스터마이징 SHA, 활성 ID, 담당 조직, 중요도, Manifest·계약 파일 연결 |
| `contracts.yaml` | 각 BANK-OM 기능이 정상이라고 판단할 업무 조건과 test |
| `shared-path-owners.yaml` | 둘 이상의 BANK-OM commit이 함께 변경한 파일과 실제 ID |
| `source-diff-paths.txt` | `patch/om-1.13.0`과 `custom/om-1.13.0` 사이의 111개 변경 파일 |
| `patch-source-lock.yaml` | 001~007 commit SHA와 적용 순서. 007은 두 SHA를 순서대로 기록 |

Manifest는 정책과 파일 범위를 저장하고, Git commit SHA와 적용 순서는
patch-lock이 저장합니다. Manifest에 commit SHA를 넣지 않습니다.

## 11. 작성 후 확인 순서

각 ID의 Manifest를 만든 뒤 다음 순서로 확인합니다.

1. commit에서 나온 모든 파일이 `allowed_changed_paths`에 있는지 확인합니다.
2. `required_changed_paths`가 `allowed` 또는
   `candidate_additional_paths` 안에 있는지 확인합니다.
3. 여러 ID가 수정한 파일을 `shared-path-owners.yaml`에 등록합니다.
4. 모든 commit에 정확히 하나의 `Customization-ID`가 있는지 확인합니다.
5. `contracts.yaml`의 계약 ID와 Manifest의 `assurance.contracts`가
   일치하는지 확인합니다.
6. 스키마 검사와 소스 검사를 실행합니다.

현재 검사 실행기는 전체 등록 묶음을 입력으로 받기 때문에
`customization-registry.yaml`, Manifest, 계약, 변경 파일 목록을 먼저 완성해야
합니다. Manifest 한 파일만 만든 상태에서 전체 검사 통과로 표시하면 안 됩니다.

## 12. 버전별 태그 생성 시점

태그는 branch가 계속 이동해도 검사한 코드 시점을 다시 찾을 수 있게 하는
고정 표식입니다. 태그는 다음 두 종류로 구분합니다.

| 태그 예시 | 붙일 commit | 생성 조건 |
|---|---|---|
| `baseline/om-1.13.0` | `patch/om-1.13.0`의 정확한 snapshot SHA | 공식 1.13.0 Git tree와 OM_TEMP snapshot Git tree가 동일함을 확인 |
| `verified/om-1.13.0-bank.1` | 검사에 사용한 `custom/om-1.13.0`의 정확한 SHA | Manifest·Git 범위·필수 test와 정해진 gate가 모두 통과 |

검증 태그는 “행내 운영 배포 완료”를 뜻하지 않습니다. 태그 설명과 검사 결과에
어떤 소스 검사·build·환경 test를 통과했는지 기록해야 합니다.

검사 통과 후에만 다음과 같이 annotated tag를 만듭니다.

```bash
git tag -a baseline/om-1.13.0 \
  2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50 \
  -m "Official OpenMetadata 1.13.0 tree-verified baseline"

git tag -a verified/om-1.13.0-bank.1 \
  <검사한-custom-commit-SHA> \
  -m "OM 1.13.0 BANK-OM source verification passed; see linked gate result"

git push origin \
  baseline/om-1.13.0 \
  verified/om-1.13.0-bank.1
```

`<검사한-custom-commit-SHA>`에는 검사 결과가 가리키는 40자리 SHA를 넣습니다.
branch 이름이나 `latest` 같은 움직이는 값을 넣지 않습니다.

1.13.1 업그레이드가 끝나면 같은 규칙으로
`baseline/om-1.13.1`과 `verified/om-1.13.1-bank.1`을 만듭니다.

## 13. 이번 작업의 완료 기준과 다음 단계

### 이번 Manifest 작성 단계의 완료 기준

- BANK-OM-001~007 Manifest가 1.13.0 실제 commit을 기준으로 작성됨
- BANK-OM-007의 두 commit이 구분되어 등록됨
- 111개 변경 파일이 빠짐없이 ID에 연결되거나 미등록 사유가 기록됨
- 공용 파일 소유 ID가 실제 diff와 일치함
- 계약과 필수 test의 담당 검토가 끝남
- Manifest와 등록 묶음의 스키마 검사가 통과함

### 다음 단계

1. OM_TEMP 1.13.0 등록 묶음을 검사기에 연결합니다.
2. 소스 gate와 가능한 test를 실행합니다.
3. 결과가 가리키는 Git commit SHA를 확인합니다.
4. 통과 범위가 명확한 검증 태그를 만듭니다.
5. 공식 1.13.1 기준 branch를 만들고 001~007을 다시 적용해 충돌을 확인합니다.
6. 동일한 Manifest·검사 흐름으로 1.13.1 결과를 비교합니다.

검사 결과와 태그가 생기기 전까지 OM_TEMP의 `custom/om-1.13.0`은
커스터마이징 코드가 들어 있는 시연 준비 상태이며, 배포 승인 상태가 아닙니다.
