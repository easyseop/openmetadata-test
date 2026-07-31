# OM_TEMP 1.13.0 Manifest 작성 단계별 가이드

> 최종 갱신: 2026-07-31

## 1. 이 가이드의 목적

`easyseop/OM_TEMP`의 `custom/om-1.13.0` branch에는 공식 OpenMetadata
1.13.0 코드와 BANK-OM-001~007 맞춤 변경 코드가 들어 있습니다.

해야 할 일은 각 BANK-OM commit이 실제로 변경한 파일을 Git에서 확인하고,
그 결과를 `easyseop/openmetadata-test`의 Manifest에 등록하는 것입니다.
Manifest는 “이 기능이 어느 파일을 바꿨고, 그중 무엇이 반드시 남아 있어야
하는가”를 검사기에 알려 주는 YAML 파일입니다.

**현재 상태:** BANK-OM-001~007 Manifest 7개는 이미 작성되어
`harness/registrations/om-temp-1.13.0/manifests/`에 있고, 스키마 검사와 등록
검사를 통과했습니다. 아직 하지 않은 것은 제품 build, 실제 업무 동작 test,
1.13.1 업그레이드 비교, 검증 태그 생성, 행내 배포입니다.

따라서 이 문서는 두 가지로 읽으면 됩니다.

- 새 버전이나 새 기능의 Manifest를 앞으로 만들 때 → 처음부터 순서대로
- 지금 등록된 1.13.0 Manifest가 왜 이렇게 생겼는지 알고 싶을 때 → 6·7·8절

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

순서를 이렇게 잡는 이유는 양쪽 실패를 모두 피하기 위해서입니다. 개발 전에
변경 파일을 미리 적어 두면 실제 코드와 어긋납니다. 반대로 Manifest 없이
배포까지 가면, 나중에 어떤 기능이 빠졌는지 판단할 기준 자체가 없습니다.
그래서 **코드를 먼저 commit하고, 그 commit이 실제로 바꾼 파일로 Manifest를
확정합니다.**

### 배포 차단 조건

Manifest 파일이 존재한다는 사실만으로 배포를 허용해서는 안 됩니다. 다음 조건이
모두 충족되어야 배포 검토 단계로 넘어갑니다.

- 활성 BANK-OM ID마다 Manifest가 존재합니다.
- Manifest가 스키마 검사를 통과합니다.
- Manifest의 변경 파일과 실제 Git commit의 변경 파일이 일치합니다.
- commit 메시지에 올바른 `Customization-ID`가 있습니다.
- 필수 파일과 연결된 test가 검사 기준을 통과합니다.
- 검사 결과가 배포할 코드와 동일한 Git commit SHA를 가리킵니다.

OM_TEMP는 업그레이드 시연을 준비하느라 코드를 먼저 만들었습니다. 그래서
1.13.0은 예외적으로 **이미 만들어진 commit을 거꾸로 읽어 Manifest를
작성했습니다.** 이 방식이 정상 순서는 아니지만, Manifest를 사람이 상상해서
적은 것이 아니라 실제 commit에서 뽑았다는 점은 같습니다. 검사가 통과하기
전에는 검증 태그도 배포 승격도 만들지 않습니다.

## 3. 작업할 저장소 두 개

| 저장소 | 이번 단계에서 확인하거나 저장할 내용 |
|---|---|
| `easyseop/OM_TEMP` | 실제 OpenMetadata 1.13.0 코드, BANK-OM commit과 변경 파일 |
| `easyseop/openmetadata-test` | 새 1.13.0 Manifest, 등록부, 계약, 검사 설정과 결과 |

Manifest를 OM_TEMP 안에 넣지 않습니다. 실제 제품 코드와 검사 기준을 같은
저장소에 중복 저장하면 업그레이드 과정에서 어느 쪽이 기준인지 혼동될 수
있기 때문입니다.

등록자료는 버전마다 폴더를 따로 씁니다. 1.13.1 기준 등록자료는
`harness/registrations/kb-openmetadata/`에, 1.13.0은
`harness/registrations/om-temp-1.13.0/`에 있습니다. 한쪽을 다른 쪽 내용으로
덮어쓰지 않습니다. 덮어쓰면 “어느 버전을 기준으로 검사한 결과인가”를 구분할
수 없게 됩니다.

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
| 맞춤 변경 branch | `custom/om-1.13.0` |
| 현재 맞춤 변경 SHA | `7d19c8952612e77467b0a80d6287170d814f1de1` |
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

여러 SHA를 가장 최근 SHA 하나로 줄이지 않습니다. 각 SHA는 서로 다른 변경
묶음의 근거이기 때문입니다. BANK-OM-007에서는 최초 구현 SHA가 8개 파일을,
후속 보완 SHA가 2개 파일을 변경했습니다. 둘 중 하나만 남기면 다른 변경의
근거를 찾을 수 없습니다.

```text
BANK-OM-007
├─ 62e39da8...  최초 구현: 8개 파일
└─ 7d19c895...  후속 보완: 2개 파일

최종 검사 대상 SHA
└─ 위 두 변경과 BANK-OM-001~006까지 모두 반영된 custom branch의 마지막 SHA 1개
```

즉, 두 종류의 SHA를 구분해야 합니다. 위 표의 SHA는 **기능마다 언제 무엇을
바꿨는지**를 남기는 이력입니다. 반면 검사 대상을 고정하는 파일(Candidate
lock)의 `candidate.commit_sha`는 **이번에 통째로 검사할 코드 상태 하나**를
가리킵니다. 앞은 여러 개일 수 있고, 뒤는 항상 하나입니다.

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
| `A` | 이 commit에서 새 파일을 추가함 | `changed_paths`에 등록 |
| `M` | 공식 코드에 있던 파일을 수정함 | `changed_paths`에 등록 |
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
맞춤 변경 구현 파일입니다.

### 6.2 `changed_paths` 목록 만들기

다음 명령은 선택한 commit이 변경한 모든 파일을 YAML 목록 형태로 출력합니다.

```bash
git show --name-only --format= \
  4df83b311f1ec38156c9b992f34607b22224db85 \
  | sed '/^$/d' \
  | sort -u \
  | sed 's/^/    - /'
```

출력된 파일을 빠짐없이 해당 ID의 `changed_paths`에 넣습니다.

**폴더 전체를 `**`로 묶어 등록하지 않습니다.** 예를 들어
`openmetadata-ui/**`라고 적으면 그 폴더 안의 어떤 파일이 바뀌어도 “범위 안”이
되어 버려서, 나중에 누가 관계없는 파일을 건드려도 검사가 잡아내지 못합니다.
commit에서 실제로 확인한 파일만 하나씩 적어야 범위 밖 변경을 찾을 수 있습니다.

### 6.3 공용 파일 확인

하나의 파일을 여러 BANK-OM commit이 수정할 수 있습니다. 예를 들어 다음 세
파일은 BANK-OM-001과 BANK-OM-002가 모두 수정합니다.

- `openmetadata-service/src/main/java/org/openmetadata/service/Entity.java`
- `openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/CollectionDAO.java`
- `openmetadata-service/src/main/java/org/openmetadata/service/search/SearchIndexFactory.java`

이 경우 파일을 한 ID에서 빼지 않습니다. 두 Manifest의
`changed_paths`에 모두 넣고 `shared-path-owners.yaml`에도 두 ID를
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

Manifest 항목은 “어느 쪽에 넣을까” 하고 고르는 선택지가 아닙니다. 각 항목이
서로 다른 질문에 답하므로, 같은 파일이 두 항목에 동시에 들어갈 수도 있습니다.

| Manifest 항목 | 답해야 하는 질문 | 등록 방법 | 어겼을 때 판정 |
|---|---|---|---|
| `changed_paths` | 이 기능의 commit들이 실제로 바꾼 파일은 무엇인가? | 같은 ID의 모든 commit에서 경로를 뽑아 한 목록으로 합침 | 목록 밖 파일을 바꾸면 `block`. 목록 안 파일인데 최종 코드에서 안 바뀌었으면 `approval` |
| `required_changed_paths` | 그중 무엇이 없어지면 “이 기능이 빠졌다”고 즉시 말할 수 있는가? | `changed_paths` 중 핵심 파일만 담당자가 고름 | 없어졌거나 공식 원본과 똑같아졌으면 `block` |
| `upgrade_watch.paths` | 공식 새 버전에서 무엇이 바뀌면 이 기능을 다시 봐야 하는가? | 실제 변경 파일은 도구가 자동 포함. 우리가 안 건드린 의존 파일은 담당자가 추가 | 공식 버전 사이에서 그 경로가 바뀌면 `approval` |
| `assurance.contracts` | 파일이 남아 있다는 것 말고, 어떤 업무 동작을 test할 것인가? | `contracts.yaml`에 정의한 계약 ID를 연결 | 계약이나 test 연결이 없으면 통과시키지 않음 |
| `series.depends_on` | 이 기능보다 먼저 적용돼야 할 다른 BANK-OM은 무엇인가? | 실제 선행 기능만 등록 | 순서가 뒤집히거나 서로 물고 돌면 `block` |

### 7.1 `changed`와 `required`의 차이

`changed`에는 현재 버전에서 같은 ID의 모든 commit이 변경한 파일 전체가 들어갑니다.
`required`에는 그중 필수 기능의 존재를 판단하는 대표 파일만 들어갑니다.

BANK-OM-001에서는 다음처럼 구분할 수 있습니다.

```yaml
implementation:
  changed_paths:
    - openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
    - openmetadata-service/src/main/java/org/openmetadata/service/resources/instancecode/InstanceCodeResource.java
    - openmetadata-spec/src/main/resources/json/schema/entity/data/instanceCode.json
    # 실제 commit이 변경한 나머지 파일도 모두 계속 등록

  required_changed_paths:
    - openmetadata-service/src/main/java/org/openmetadata/service/resources/instancecode/InstanceCodeResource.java
    - openmetadata-spec/src/main/resources/json/schema/entity/data/instanceCode.json
```

`Entity.java`도 실제 변경 파일이므로 `changed`에서 빠지면 안 됩니다. 다만
이 파일은 여러 기능이 함께 사용하는 공용 파일이므로, 파일 전체가 다르다는
사실만으로 InstanceCode 기능 전체가 남았다고 판단하기 어렵습니다. 그래서
InstanceCode API 구현 파일과 스키마 파일을 `required`의 대표 근거로 사용하고,
API 동작은 계약 test로 별도 확인합니다.

### 7.2 현재 `upgrade_watch` 등록 방법

T42 검사는 Manifest의 `upgrade_watch.paths`에 적힌 경로가 공식 버전 사이에서
바뀌었는지 비교합니다. 이 목록은 자동과 수동을 섞어 만듭니다.

1. **자동:** 도구가 각 BANK-OM commit의 실제 변경 파일을 Git에서 읽어
   `changed_paths`와 `upgrade_watch.paths`에 함께 넣습니다. 같은 경로를 사람이
   두 번 입력할 필요가 없습니다.
2. **수동:** 우리가 직접 고치지는 않았지만 호출하거나 구조에 의존하는 공식
   파일은 담당자가 `watch_dependencies`로 추가합니다.
3. **후보 제시:** 우리 코드가 공식 파일 이름을 코드 안에서 직접 언급하고 있고
   그 파일이 새 버전에서 바뀌면, 검사기가 “이것도 watch에 넣을까요?”라고
   후보를 제시합니다.
4. 후보는 **Manifest를 자동으로 고치지 않습니다.** 담당자가 실제 의존 관계인지
   확인한 뒤 직접 등록합니다.

여기서 자동으로 잡히는 것은 코드에 파일 이름이나 기호 이름이 드러나는
경우뿐입니다. 런타임 설정으로 연결되거나, 이름 없이 간접 호출되는 의존
관계는 도구가 알 수 없으므로 담당자가 직접 확인해야 합니다.

## 8. BANK-OM-007 후속 commit 처리

BANK-OM-007에는 commit이 두 개 있습니다.

- 최초 적용: `62e39da8be65c3ff259802c1cd35f4b0c8baa333`
- 후속 보완: `7d19c8952612e77467b0a80d6287170d814f1de1`

최초 commit과 후속 commit의 파일을 모두 합쳐 현재 버전 Manifest의
`changed_paths`에 넣습니다.

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

따라서 BANK-OM-007 Manifest의 `changed_paths`에는 최초 8개와 후속 2개를
합친 10개 경로가 필요합니다. 아래는 그중 네 경로만 발췌한 예시입니다.

```yaml
implementation:
  changed_paths:
    # 최초 구현 commit에서 변경한 경로의 예
    - openmetadata-spec/src/main/resources/json/schema/entity/services/connections/database/tiberoConnection.json
    - openmetadata-ui/src/main/resources/ui/src/utils/DatabaseServiceUtils.tsx
    # 후속 보완 commit에서 새로 변경한 경로
    - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/connections/serviceConnection.ts
    - openmetadata-ui/src/main/resources/ui/src/utils/DatabaseServiceUtils.test.tsx

series:
  allowed: true
  depends_on: []
```

Manifest는 “현재 버전에서 검사할 10개 파일”을 정의하고, Git 이력은
“어느 commit에서 8개와 2개가 각각 변경됐는지”를 보존합니다. 따라서 후속
변경을 표시하기 위한 별도 경로 필드는 사용하지 않습니다.

## 9. Manifest 파일 작성

### 9.1 자동 생성 도구 사용 여부

Manifest 초안은 준비도구의 `plan`이 만듭니다. `plan`은 patch와 custom 사이의
commit을 모두 읽어 BANK-OM ID별 변경 경로를 계산하고, 그 결과를 **제안
폴더에만** 씁니다. 실제 등록 폴더는 사람이 승인한 뒤 `apply`에서만 바뀝니다.

```bash
PYTHONPATH=harness ./.venv/bin/python harness/prepare_registration.py plan \
  --repo <제품-코드-저장소-절대경로> \
  --registration harness/registrations/om-temp-1.13.0 \
  --patch-ref origin/patch/om-1.13.0 \
  --custom-ref origin/custom/om-1.13.0 \
  --product-version 1.13.0 \
  --output harness/preparation-plans/om-temp-1.13.0-20260730
```

`--output`은 아직 없는 폴더여야 합니다. 이미 있는 폴더를 주면 도구가 예전
제안을 덮어쓰지 않고 거절합니다. 실행할 때마다 날짜를 붙여 새 폴더를 씁니다.

`plan`은 Git이 확정할 수 있는 전체 변경 파일을 ID별 `changed_paths`로
계산합니다. BANK-OM-007처럼 commit이 두 개면 두 commit의 경로를 한 목록으로
합칩니다. `required`, 미수정 의존 파일, 계약은 기능 의미를 판단해야 하므로
자동으로 확정하지 않고 `review-required.yaml`의 질문으로 남깁니다.

전체 단계와 상태별 대응은
[`OM_TEMP 검사 전 준비도구 쉬운 사용법`](OM_TEMP_검사전_준비도구_쉬운사용법.md)에
있습니다.

등록 폴더 안의 `generate_manifest_drafts.py`는 예전 파일 이름을 그대로 두기
위한 껍데기입니다. 위 `plan`과 같은 일을 하고 같은 인자를 받습니다. 다만
`--registration`은 자기 폴더가 기본값이라 생략할 수 있습니다. 새로 작성하는
자동화는 이 파일 대신 `harness/prepare_registration.py plan`을 직접
호출합니다.

`harness/registrations/kb-openmetadata/materialize_exact_scopes.py`는 기존
1.13.1 등록자료 전용이므로 이번 1.13.0 생성에는 사용하지 않습니다.

### 9.2 파일 위치

1.13.0 등록 폴더는 이미 만들어져 있습니다. 현재 실제 구성은 다음과 같습니다.

```text
harness/registrations/om-temp-1.13.0/
├── customization-registry.yaml        # 기준 SHA, 활성 ID, 담당자
├── contracts.yaml                     # 업무 계약과 필수 test
├── repository-layout.yaml             # 경로를 어느 영역으로 분류할지
├── sensitive-zones.yaml               # 특별히 주의해서 볼 경로
├── shared-path-owners.yaml            # 여러 ID가 함께 바꾼 파일
├── source-snapshot-path-owners.yaml   # 과거 snapshot 시점의 파일별 ID
├── source-diff-paths.txt              # patch↔custom 차이 111개 경로
├── REPRODUCIBILITY.md                 # 후보를 다시 만드는 방법
├── manifests/
│   ├── BANK-OM-001.yaml
│   │   … BANK-OM-007.yaml 까지 7개
├── registration-validation-results.json   # 등록 검사 5종 결과
└── source-gate-results.json               # 소스 게이트 결과
```

새 버전용 폴더를 처음부터 만들 때는 위 파일들을 같은 이름으로 준비합니다.

```bash
cd openmetadata-test
mkdir -p harness/registrations/om-temp-<버전>/manifests
```

Manifest 7개는 스키마 검사와 등록 검사를 통과한 상태입니다. 다만 제품 build,
실제 업무 동작 test, 1.13.1 업그레이드 비교는 아직 실행 전이므로 배포 승인
상태가 아닙니다.

### 9.3 BANK-OM-001 기본 형태

아래 코드는 항목 구조를 설명하기 위해 일부 경로만 넣은 축약 예시입니다.
검사 입력으로 그대로 사용하면 안 됩니다. 실제 파일에는
`changed_paths`와 `upgrade_watch.paths`를 생략 없이 넣어야 합니다.

```yaml
schema_version: 2
customization_id: BANK-OM-001
status: active
kind: core-patch
title: InstanceCode

implementation:
  changed_paths:
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
| `customization-registry.yaml` | 공식 기준 SHA(`upstream_sha`), snapshot SHA, 활성 ID, 담당 조직, 중요도, Manifest·계약 파일 연결 |
| `contracts.yaml` | 각 BANK-OM 기능이 정상이라고 판단할 업무 조건과 그것을 확인할 test |
| `repository-layout.yaml` | 어떤 경로가 제품 코드이고 어떤 경로가 검사 정책인지의 분류 규칙 |
| `sensitive-zones.yaml` | 변경되면 특별히 주의해서 봐야 하는 경로 |
| `shared-path-owners.yaml` | 둘 이상의 BANK-OM commit이 함께 변경한 파일과 그 ID들 |
| `source-snapshot-path-owners.yaml` | 최초 등록에 쓴 과거 snapshot 시점의 파일별 BANK-OM ID. 과거 코드 재구성 검사(T25-R) 전용 자동 생성 자료 |
| `source-diff-paths.txt` | `patch/om-1.13.0`과 `custom/om-1.13.0` 사이의 111개 변경 파일 |

**Manifest에는 Git commit SHA를 넣지 않습니다.** Manifest는 “어느 파일이 이
기능의 범위인가”만 담고, “어느 commit이 그렇게 만들었는가”는 Registry의
`source` 항목과 Git 이력이 담습니다. 둘을 섞으면 commit이 하나 늘 때마다
Manifest를 고쳐야 하고, 그러면 Manifest가 Git 사실과 어긋나기 쉬워집니다.

`source-snapshot-path-owners.yaml`과 `shared-path-owners.yaml`은 이름이
비슷하지만 시점이 다릅니다. 예를 들어
`serviceConnection.ts`는 최초 source snapshot에서는 BANK-OM-006만
수정했으므로 전자에는 `BANK-OM-006`만 기록됩니다. 이후 BANK-OM-007 후속
commit도 같은 파일을 수정했으므로 현재 버전 기준 후자에는
`BANK-OM-006, BANK-OM-007`이 기록됩니다.

## 11. 작성 후 확인 순서

각 ID의 Manifest를 만든 뒤 다음 순서로 확인합니다.

1. 같은 ID의 모든 commit에서 나온 파일이 `changed_paths`에 있는지 확인합니다.
2. `required_changed_paths`가 `changed_paths` 안에 있는지 확인합니다.
3. 여러 ID가 수정한 파일을 `shared-path-owners.yaml`에 등록합니다.
4. 모든 commit에 정확히 하나의 `Customization-ID`가 있는지 확인합니다.
5. `contracts.yaml`의 계약 ID와 Manifest의 `assurance.contracts`가
   일치하는지 확인합니다.
6. 스키마 검사와 소스 검사를 실행합니다.

현재 검사 실행기는 전체 등록 묶음을 입력으로 받기 때문에
`customization-registry.yaml`, Manifest, 계약, 변경 파일 목록을 먼저 완성해야
합니다. Manifest 한 파일만 만든 상태에서 전체 검사 통과로 표시하면 안 됩니다.

## 12. 버전별 태그 생성 시점

branch는 새 commit이 쌓이면 계속 앞으로 움직입니다. 그래서 “그때 검사한 그
코드”를 branch 이름으로 가리키면 나중에 다른 코드를 가리키게 됩니다. 태그는
움직이지 않는 표식이라 이 문제를 막습니다.

**현재 OM_TEMP 원격에는 태그가 하나도 없습니다.** 아래는 앞으로 만들 때의
규칙입니다. 태그는 두 종류로 구분합니다.

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

### Manifest 작성 단계의 완료 기준

| 기준 | 현재 |
|---|---|
| BANK-OM-001~007 Manifest가 1.13.0 실제 commit을 기준으로 작성됨 | 완료 |
| BANK-OM-007의 두 commit이 구분되어 등록됨 | 완료 |
| 111개 변경 파일이 빠짐없이 ID에 연결되거나 미등록 사유가 기록됨 | 완료 |
| 공용 파일 소유 ID가 실제 diff와 일치함 | 완료 |
| Manifest와 등록 묶음의 스키마 검사가 통과함 | 완료(등록 검사 5종 통과) |
| 계약과 필수 test의 담당자 검토가 끝남 | **미완료 — 담당 조직이 모두 `UNASSIGNED`** |

### 다음 단계

1. Registry의 `owner: UNASSIGNED` 7건에 실제 조직을 배정합니다.
2. 소스 게이트와 실행 가능한 test를 돌립니다.
3. 결과가 가리키는 Git commit SHA가 검사한 코드와 같은지 확인합니다.
4. 무엇이 통과한 태그인지 설명에 적어 검증 태그를 만듭니다.
5. 공식 1.13.1 기준 branch를 만들고 001~007을 다시 적용해 충돌을 확인합니다.
6. 같은 Manifest·검사 흐름으로 1.13.1 결과를 비교합니다.

검사 결과와 태그가 생기기 전까지 OM_TEMP의 `custom/om-1.13.0`은 맞춤 변경
코드가 들어 있는 시연 준비 상태이며, 배포 승인 상태가 아닙니다.
