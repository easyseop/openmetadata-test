# OM_TEMP 1.13.1 코드 정리 및 최초 등록 준비 가이드

**전체 순서:** 5/11 · [전체 목차](./OM_TEMP_1.13.1_1.13.2_예행연습_전체목차.html)

> 문서 성격: 실제 1.13.1 커스터마이징의 최초 등록자료를 자동 작성·검증하고 사람 승인 절차에 연결하는 실행 문서  
> 시작 조건: `OM_TEST_REPO`·`OM_CODE_REPO` 설정, `BANK-OM-001`~`007` ID별 commit 후보 branch, 111개 등록 경로, 2개 제외 경로와 경로 기준 파일 준비 완료  
> 종료점: 이번 1.13.1용 등록 초안을 작성하고, 114개 공용 경로·ID 조합의 자동 작성 제안을 최종 커스텀 코드에서 검증한 뒤 등록 `plan`의 검토 입력으로 준비  
> 이 문서에서 하지 않는 일: 원격 push, 최초 등록 제안 승인·반영(`bootstrap-apply`), 1.13.2 병합, 릴리즈 승인

**문서 이동:** [← 이전 단계 — BANK-OM ID별 commit 후보 branch 구성](./OM_TEMP_1.13.1_BANK-OM_ID별_커밋_후보브랜치_구성_가이드.html) · [다음 — 검사기 간단 학습 →](./OM_TEMP_1.13.1_1.13.2_검사기_간단_학습_가이드.html)

## 단계 연결 요약

| 구분 | 내용 |
|---|---|
| 이전 단계 | 공식 1.13.1 위에 사용자가 승인한 111개 변경을 7개 BANK-OM ID별 commit으로 구성했습니다. |
| 이번 단계 | 이번 1.13.1 최초 등록에 필요한 공용 코드 정의를 자동 제안·검증하고 Manifest·Registry·Contract 초안을 준비합니다. |
| 완료 결과 | 7번 페이지의 `plan`이 이번 1.13.1 코드와 검토할 등록 입력을 읽을 수 있습니다. 정식 사람 승인은 그 `plan`의 digest에 연결해 기록합니다. |

## 1. 코드 branch와 111개 변경 확인

### 1-1. 등록 준비 branch로 이동

이 branch는 **이전 4/11 페이지의 7-4-5에서 만든 1.13.1 커스터마이징 기준검사 branch**입니다. 당시 공식 1.13.1 commit에서 새 branch를 시작하고 `BANK-OM-001`~`007` commit을 순서대로 옮긴 뒤 재구성 검사를 통과했습니다.

```bash
git -C "$OM_CODE_REPO" switch codex/om-1.13.1-id-series-upstream
```

```bash
git -C "$OM_CODE_REPO" status --short
```

**정상 결과:** 두 번째 명령의 출력이 비어 있습니다.

**중단 조건:** branch를 찾지 못하면 이전 페이지가 완료되지 않은 것입니다. `status --short`에 한 줄이라도 나오면 그 변경의 용도를 먼저 확인합니다.

### 1-2. 공식 branch와 등록 준비 branch 식별값 확인

- `upstream-1.13.1-release`: 이전 4/11 페이지 7-4-5에서 새 branch의 출발점으로 사용한 **공식 OpenMetadata 1.13.1 branch**입니다.
- `codex/om-1.13.1-id-series-upstream`: 같은 7-4-5에서 공식 branch 위에 일곱 BANK-OM commit을 옮겨 만든 **1.13.1 커스터마이징 기준검사 branch**입니다.

```bash
git -C "$OM_CODE_REPO" rev-parse upstream-1.13.1-release
```

**공식 OpenMetadata 1.13.1 commit 확인값:** `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9`

```bash
git -C "$OM_CODE_REPO" rev-parse codex/om-1.13.1-id-series-upstream
```

**현재 확인값:** `d952a83896940116d3d6022323ad76bfe60991e8`

`codex/om-1.13.1-id-series-upstream`은 **공식 OpenMetadata 1.13.1 코드 위에 `BANK-OM-001`~`007`을 모두 적용한 1.13.1 커스터마이징 기준검사 branch**입니다. 공식 코드만 있는 `upstream-1.13.1-release` branch나 이후 운영에 사용할 release branch가 아닙니다.

위 명령이 출력한 SHA는 일곱 commit을 하나로 합친 별도 값이 아닙니다. 이 커스터마이징 기준검사 branch에서 가장 마지막에 만든 **일곱 번째 `BANK-OM-007` commit의 SHA**입니다.

```text
공식 1.13.1
  └─ BANK-OM-001 commit
      └─ BANK-OM-002 commit
          └─ BANK-OM-003 commit
              └─ BANK-OM-004 commit
                  └─ BANK-OM-005 commit
                      └─ BANK-OM-006 commit
                          └─ BANK-OM-007 commit  ← 커스터마이징 기준검사 branch의 현재 끝
```

Git commit은 바로 앞 commit을 연결해서 보관하므로, 일곱 번째 `BANK-OM-007` commit을 지정하면 그 앞의 `001`~`006`과 공식 1.13.1까지 포함한 전체 코드 상태를 함께 식별할 수 있습니다. 따라서 이 SHA는 **일곱 변경을 모두 적용한 최종 1.13.1 코드 상태**를 고정할 때 사용합니다.

일곱 commit의 SHA와 BANK-OM ID를 각각 확인하려면 다음 명령을 사용합니다.

```bash
git -C "$OM_CODE_REPO" log \
  --reverse \
  --format='%H | %(trailers:key=Customization-ID,valueonly)' \
  upstream-1.13.1-release..codex/om-1.13.1-id-series-upstream
```

**정상 결과:** `BANK-OM-001`부터 `BANK-OM-007`까지 일곱 줄이 나오고, 마지막 줄의 SHA가 위 `rev-parse` 결과와 같아야 합니다.

### 1-3. 등록 대상 경로 수와 제외 경로 확인

```bash
git -C "$OM_CODE_REPO" diff --name-only upstream-1.13.1-release HEAD | wc -l
```

**정상 결과:** `111`

```bash
git -C "$OM_CODE_REPO" diff --name-status upstream-1.13.1-release HEAD -- .claude/settings.json docker/development/docker-compose.yml
```

**정상 결과:** 빈 출력입니다. 이전 단계에서 공식 1.13.1을 기준으로 branch를 만들고 111개만 적용했기 때문에, 두 파일은 이미 공식 내용으로 남습니다. 따라서 별도 복원 commit을 만들지 않습니다.

**빈 출력이 아닌 경우:** 이전 ID별 commit 구성에 제외 파일이 잘못 들어간 것입니다. 다음 작성 단계로 이동하지 말고, 이전 페이지에서 해당 ID 변경을 다시 구성합니다.

## 2. 114개 공용 경로·ID 조합의 코드 정의 자동 작성·검증

### 2-1. 작성 양식이 필요한 이유

`shared-path-owners.yaml`은 공용 파일을 어떤 BANK-OM ID가 함께 사용하는지만 기록합니다. 예를 들어 `Entity.java`가 `BANK-OM-001`·`002`에 연결돼 있어도, 최종 코드에 `001` 코드만 남고 `002` 코드가 빠진 상태를 경로 연결만으로는 찾을 수 없습니다.

작성 양식은 114개 `공용 파일 경로 + BANK-OM ID` 조합을 먼저 나열해 누락을 막습니다. 빈 양식 생성과 assertion 제안은 서로 다른 명령입니다. 두 번째 명령이 각 BANK-OM commit의 실제 diff에서 코드 정의를 자동 추출하고 최종 커스텀 코드에서 다시 검산합니다.

### 2-2. 공용 파일 37개의 작성 양식을 한 번에 생성

이 명령은 공용 파일마다 따로 실행하지 않습니다. **아래 두 명령을 각각 한 번만 실행**하면 됩니다. 생성기가 `shared-path-owners.yaml`을 읽어 공용 파일 37개와 연결된 BANK-OM ID를 모두 찾고, 114개 `파일+ID` 작성칸을 한 파일에 생성합니다.

```bash
mkdir -p "$OM_TEST_REPO/harness/preparation-inputs/om-temp-1.13.1"
```

```bash
PYTHONPATH="$OM_TEST_REPO/harness" "$OM_TEST_REPO/.venv/bin/python" \
  "$OM_TEST_REPO/harness/generate_shared_code_definition_draft.py" \
  --owners "$OM_TEST_REPO/harness/registrations/om-temp-1.13.1/shared-path-owners.yaml" \
  --output "$OM_TEST_REPO/harness/preparation-inputs/om-temp-1.13.1/shared-code-definitions-draft.yaml"
```

**처음 실행한 경우의 정상 결과:**

```json
{
  "status": "DRAFT_WRITTEN",
  "output": ".../shared-code-definitions-draft.yaml",
  "definition_pairs": 114,
  "requires_assertion_proposal": true
}
```

`DRAFT_WRITTEN`은 `output` 경로에 114개 작성칸을 새로 만들었다는 뜻입니다. 실제 코드 정의는 아직 비어 있으므로 검사 `PASS`를 뜻하지 않습니다.

**같은 명령을 다시 실행한 경우의 정상 결과:**

```json
{
  "status": "DRAFT_ALREADY_EXISTS",
  "output": ".../shared-code-definitions-draft.yaml",
  "definition_pairs": 114,
  "completed_pairs": 0,
  "remaining_pairs": 114,
  "next_action": "기존 파일을 그대로 사용하고, 별도의 자동 assertion 제안 명령을 실행하십시오. 자동 추출할 수 없는 항목만 수동으로 작성합니다."
}
```

`DRAFT_ALREADY_EXISTS`는 앞선 실행에서 작성 양식이 이미 만들어졌고, 현재 `shared-path-owners.yaml`의 114개 조합과도 일치한다는 뜻입니다. 생성기는 기존 파일을 보호하기 위해 덮어쓰지 않습니다. **파일을 삭제하거나 다시 생성하지 말고 2-3의 자동 assertion 제안 명령으로 이동합니다.**

| 결과 필드 | 확인할 내용 |
|---|---|
| `definition_pairs` | 현재 양식에 들어 있는 전체 `공용 파일 경로 + BANK-OM ID` 작성칸 수입니다. 이 예행연습에서는 `114`여야 합니다. |
| `completed_pairs` | 빈 양식 안에서 `assertions`가 이미 들어 있는 칸 수입니다. 생성 직후에는 `0`입니다. |
| `remaining_pairs` | 빈 양식 안에서 `assertions`가 비어 있는 칸 수입니다. 생성 직후에는 `114`이며, 다음 2-3의 별도 명령이 자동 작성 제안을 만듭니다. |
| `output` | 다음 2-3 자동 작성 명령이 입력으로 읽을 빈 양식의 경로입니다. |

**중단 결과:** `ANALYSIS_ERROR`가 나오면서 기존 파일과 현재 공용 경로 목록이 일치하지 않는다고 표시되면, 기존 파일을 임의로 삭제하지 않습니다. `shared-path-owners.yaml`이 작성 양식 생성 후 바뀌었는지 확인하고 담당자와 갱신 범위를 결정합니다.

#### 생성된 빈 양식

114개 작성 항목은 다음 YAML 파일 **한 개로 관리합니다.**

```text
$OM_TEST_REPO/harness/preparation-inputs/om-temp-1.13.1/shared-code-definitions-draft.yaml
```

이 파일에는 다음 형태의 작성칸이 114개 들어 있습니다.

```yaml
- path: bootstrap/sql/migrations/native/1.13.1/mysql/schemaChanges.sql
  customization_id: BANK-OM-001
  assertions: []
```

| 필드 | 이미 자동으로 채워진 내용 | 사용자가 할 일 |
|---|---|---|
| `path` | 여러 BANK-OM ID가 함께 수정한 공용 파일 경로 | 수정하지 않고, 어떤 파일을 확인할지 식별합니다. |
| `customization_id` | 그 파일을 사용하는 BANK-OM ID 중 하나 | 수정하지 않고, 어느 ID의 코드를 찾아야 하는지 식별합니다. |
| `assertions` | 생성 직후에는 빈 목록 `[]` | 다음 2-3 명령이 해당 ID commit의 실제 코드 조각 또는 JSON/YAML 값을 제안합니다. |

### 2-3. 114개 assertions 자동 작성·검증

다음 명령은 2-2에서 만든 114개 빈 작성칸을 기준으로, 각 BANK-OM commit의 실제 변경에서 assertions 초안을 자동으로 작성합니다. 자동 작성 결과는 검토용 제안 파일 `shared-code-definitions-proposed.yaml`에 저장됩니다. 관리자가 제안 내용을 확인해 승인하면 2-4에서 이번 1.13.1의 등록 초안 `shared-code-definitions.yaml`로 반영합니다. 정식 승인은 이후 `plan`이 만든 digest를 관리자가 승인하고 `apply`가 그 승인 내용을 확인할 때 완료됩니다.

```bash
bash "$OM_TEST_REPO/harness/registrations/om-temp-1.13.1/propose_shared_code_definitions.sh"
```

이 명령은 다음 작업을 자동으로 수행합니다.

1. 각 BANK-OM ID가 기록된 commit을 찾습니다.
2. commit의 실제 변경에서 JSON·YAML 값과 코드 조각을 찾아 assertions 초안을 작성합니다.
3. 뒤의 commit에서 다시 바뀌거나 삭제된 내용은 초안에서 제외합니다.
4. 작성한 assertions가 최종 1.13.1 커스터마이징 코드에 모두 있는지 검사합니다.

검사가 `PASS`이면 관리자가 자동 작성 제안을 검토합니다. 오류가 나오면 등록 초안에 반영하지 않고 표시된 BANK-OM ID와 파일을 먼저 확인합니다.

**이번 예행연습의 실제 정상 결과:**

```json
{
  "status": "PROPOSAL_WRITTEN",
  "output": ".../shared-code-definitions-proposed.yaml",
  "definition_pairs": 114,
  "assertions": 790,
  "candidate_verification": "PASS",
  "requires_human_approval": true
}
```

| 결과 필드 | 의미와 다음 행동 |
|---|---|
| `definition_pairs: 114` | 공용 파일 경로와 BANK-OM ID 조합 114개가 모두 작성됐습니다. |
| `assertions: 790` | 114개 조합에서 추출한 전체 코드 조각과 JSON/YAML 값의 수입니다. 한 조합에 여러 실제 변경값이 있으면 assertion도 여러 개입니다. |
| `candidate_verification: PASS` | 제안한 790개 정의가 최종 커스텀 branch에서 모두 검출됐습니다. 기능 test 통과나 사람 승인을 뜻하지는 않습니다. |
| `id_commits` | 자동 추출에 사용한 BANK-OM ID별 commit SHA입니다. 이전 4/11 페이지에서 사용자가 승인한 일곱 commit과 같아야 합니다. |
| `output` | 다음 2-4에서 사람이 검토할 자동 작성 제안 파일입니다. |

같은 명령을 다시 실행했을 때 기존 제안 파일이 114개 조합을 포함하고 최종 커스텀 branch 검증도 통과하면 `PROPOSAL_ALREADY_EXISTS`가 나옵니다. 기존 파일을 덮어쓰지 않고 다음 2-4의 사람 검토로 이동합니다.

**중단 결과:** `ANALYSIS_ERROR`이면 제안 파일을 등록 폴더로 복사하지 않습니다. 메시지에 표시된 BANK-OM ID·경로에서 commit을 찾지 못했거나, 해당 commit의 변경이 최종 커스텀 branch에 남아 있지 않거나, 기존 제안 파일이 현재 branch와 일치하지 않는 경우입니다. 원인을 고친 뒤 다시 실행합니다.

:::details 자동 추출이 중단된 항목의 수동 diff 확인 및 assertions 작성 방법 펼치기

작성할 항목의 `path`와 `customization_id`를 먼저 확인합니다. 아래 예시는 `Entity.java`에서 `BANK-OM-001`의 정의를 찾는 경우입니다.

```yaml
- path: openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
  customization_id: BANK-OM-001
  assertions: []
```

`path`에 적힌 파일이 공식 1.13.1과 커스터마이징 1.13.1 사이에서 어떻게 바뀌었는지 확인합니다.

```bash
git -C "$OM_CODE_REPO" diff \
  upstream-1.13.1-release \
  codex/om-1.13.1-id-series-upstream -- \
  openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
```

**확인할 내용:** 출력의 `+` 줄에서 `BANK-OM-001` 구현에 속하고, 나중에 사라지면 `BANK-OM-001` 누락이라고 판단할 수 있는 실제 코드 전체 조각을 고릅니다. 주석의 단어나 다른 BANK-OM ID의 코드는 선택하지 않습니다.

**diff가 빈 출력인 경우:** `path` 오타이거나 현재 111개 변경 대상과 작성 양식이 일치하지 않는 상태입니다. 해당 `assertions`를 추측해서 채우지 말고 `shared-path-owners.yaml`과 작성 양식의 `path`를 다시 확인합니다.

**assertion 공통 필드 작성 규칙:**

| 필드 | 작성 주체와 규칙 | 예시 |
|---|---|---|
| `id` | 사용자가 정하는 **해당 검사 항목의 이름**입니다. 실제 코드에 이미 존재해야 하는 ID가 아닙니다. 같은 `path + customization_id`의 `assertions` 안에서는 중복할 수 없습니다. 무엇을 확인하는지 알 수 있도록 영문 소문자와 `-`를 사용한 이름을 권장합니다. | `query-report-label` |
| `matcher` | 검사 방법을 정합니다. 현재 지원 값은 `code_fragment`, `json_value`, `yaml_value` 세 가지뿐입니다. 파일 종류와 맞는 값을 사용합니다. | JSON 파일이면 `json_value` |

| `matcher` | 사용할 수 있는 파일 | 함께 적어야 할 필드 | 검사기가 확인하는 내용 |
|---|---|---|---|
| `code_fragment` | `.java`, `.ts`, `.tsx`, `.sql` | `fragment`, 선택 항목 `occurrences` | 주석과 공백을 제외한 실제 코드 토큰이 파일 안에 지정 횟수만큼 있는지 확인합니다. |
| `json_value` | `.json` | `pointer`, `expected` | JSON의 `pointer` 위치에 있는 값이 `expected`와 자료형까지 정확히 같은지 확인합니다. |
| `yaml_value` | `.yaml`, `.yml` | `pointer`, `expected` | YAML의 `pointer` 위치에 있는 값이 `expected`와 자료형까지 정확히 같은지 확인합니다. |

**matcher별 추가 필드 작성 규칙:**

| 필드 | 적용 matcher | 작성 방법 |
|---|---|---|
| `fragment` | `code_fragment` | diff의 `+` 줄에서 선택한 실제 코드 전체 조각을 그대로 적습니다. 주석만 적거나 심볼 이름 하나만 적지 않습니다. |
| `occurrences` | `code_fragment` | 같은 코드 조각이 파일에 있어야 하는 횟수입니다. 생략하면 `1`로 검사합니다. 두 번 있어야 정상인 경우에만 `2`처럼 적습니다. |
| `pointer` | `json_value`, `yaml_value` | 최상위부터 값까지의 키를 `/`로 연결합니다. `/label/query-report`는 `label` 객체 안의 `query-report` 값을 뜻합니다. 배열은 `/items/0/name`처럼 순번을 사용합니다. |
| `expected` | `json_value`, `yaml_value` | `pointer` 위치에 실제로 있어야 하는 값을 적습니다. 문자열·숫자·`true`·`false`·목록·객체의 자료형도 원본과 같아야 합니다. |

한 `path + customization_id`에 반드시 남아야 할 정의가 여러 개라면 `assertions` 아래에 여러 항목을 작성할 수 있습니다. 이 경우 **모든 assertion이 일치해야 통과**합니다.

아래 다섯 예시는 현재 1.13.1 BANK-OM commit의 실제 코드를 기준으로 작성했습니다. 각 예시에서 `작성 전`은 생성기가 만든 상태이고, `작성 후`는 사용자가 실제 정의를 선택해 채운 상태입니다.

#### BANK-OM-001 - schemaChanges.sql

**작성 전**

```yaml
- path: bootstrap/sql/migrations/native/1.13.1/mysql/schemaChanges.sql
  customization_id: BANK-OM-001
  assertions: []
```

**작성 후**

```yaml
- path: bootstrap/sql/migrations/native/1.13.1/mysql/schemaChanges.sql
  customization_id: BANK-OM-001
  assertions:
    - id: instance-code-table
      matcher: code_fragment
      fragment: |
        CREATE TABLE IF NOT EXISTS instance_code_entity (
            id VARCHAR(36) GENERATED ALWAYS AS (json_unquote(json_extract(json, '$.id'))) STORED NOT NULL,
            name VARCHAR(256) GENERATED ALWAYS AS (json_unquote(json_extract(json, '$.name'))) VIRTUAL NOT NULL,
            fqnHash VARCHAR(768) NOT NULL COLLATE ascii_bin,
            json JSON NOT NULL,
            updatedAt BIGINT UNSIGNED GENERATED ALWAYS AS (json_unquote(json_extract(json, '$.updatedAt'))) VIRTUAL NOT NULL,
            updatedBy VARCHAR(256) GENERATED ALWAYS AS (json_unquote(json_extract(json, '$.updatedBy'))) VIRTUAL NOT NULL,
            deleted TINYINT(1) GENERATED ALWAYS AS (json_extract(json, '$.deleted')) VIRTUAL,
            PRIMARY KEY (id),
            UNIQUE KEY instance_code_entity_fqn_hash (fqnHash)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

#### BANK-OM-002 - Entity.java

**작성 전**

```yaml
- path: openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
  customization_id: BANK-OM-002
  assertions: []
```

**작성 후**

```yaml
- path: openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
  customization_id: BANK-OM-002
  assertions:
    - id: query-report-constant
      matcher: code_fragment
      fragment: |
        public static final String QUERY_REPORT = "queryReport";
```

#### BANK-OM-003 - constants.ts

**작성 전**

```yaml
- path: openmetadata-ui/src/main/resources/ui/src/constants/constants.ts
  customization_id: BANK-OM-003
  assertions: []
```

**작성 후**

```yaml
- path: openmetadata-ui/src/main/resources/ui/src/constants/constants.ts
  customization_id: BANK-OM-003
  assertions:
    - id: data-assertions-route
      matcher: code_fragment
      fragment: |
        DATA_ASSERTIONS: '/data_assertions',
```

#### BANK-OM-003 - AuthenticatedAppRouter.tsx

**작성 전**

```yaml
- path: openmetadata-ui/src/main/resources/ui/src/components/AppRouter/AuthenticatedAppRouter.tsx
  customization_id: BANK-OM-003
  assertions: []
```

**작성 후**

```yaml
- path: openmetadata-ui/src/main/resources/ui/src/components/AppRouter/AuthenticatedAppRouter.tsx
  customization_id: BANK-OM-003
  assertions:
    - id: data-assertions-page-loader
      matcher: code_fragment
      fragment: |
        const DataAssertionsPage = withSuspenseFallback(
          React.lazy(() => import('../../pages/DataAssertionsPage/DataAssertionsPage'))
        );
```

#### BANK-OM-004 - en-us.json

**작성 전**

```yaml
- path: openmetadata-ui/src/main/resources/ui/src/locale/languages/en-us.json
  customization_id: BANK-OM-004
  assertions: []
```

**작성 후**

```yaml
- path: openmetadata-ui/src/main/resources/ui/src/locale/languages/en-us.json
  customization_id: BANK-OM-004
  assertions:
    - id: attribute-name-label
      matcher: json_value
      pointer: /label/attribute-name
      expected: Attribute Name
```

마지막 JSON 예시는 `label` 객체 안의 `attribute-name` 값이 `Attribute Name`인지 확인합니다. 키가 없거나 값이 다르면 `BLOCK`입니다. 반면 `json_value`에 `fragment`를 적는 등 assertion 형식 자체가 잘못됐거나 JSON 파일에 `yaml_value`를 사용하면 신뢰할 수 있는 검사를 시작할 수 없으므로 `ANALYSIS_ERROR`입니다.

:::

### 2-4. 관리자 사전 검토와 등록 초안 복사

자동검증은 자동 작성한 `fragment`·`pointer`·`expected`가 최종 커스텀 코드에 실제로 있는지만 검산합니다. 해당 정의가 BANK-OM 기능을 대표하는 적절한 기준인지에 대한 최종 판단은 사람이 합니다.

이번 예행연습에서는 이전 4/11 페이지에서 각 BANK-OM commit의 실제 코드를 확인하고 ID별 코드 귀속을 정했습니다. 따라서 790개 assertion을 한 줄씩 판단하지 않고, 다음 세 조건을 확인해 **114개 조합 전체를 하나의 등록 초안으로 검토**합니다.

| 사람이 확인할 조건 | 등록 초안으로 복사할 수 있는 기준 | 중단 기준 |
|---|---|---|
| 자동 추출에 사용한 일곱 commit | 결과의 `id_commits`가 이전 4/11 페이지에서 승인한 `BANK-OM-001`~`007` commit SHA와 모두 같음 | ID가 빠졌거나 다른 commit SHA가 표시됨 |
| 경로·ID 조합과 최종 코드 검산 | `definition_pairs: 114`, `candidate_verification: PASS` | 114가 아니거나 `ANALYSIS_ERROR` |
| 제안 내용의 ID 귀속 | 제안 파일의 `path`·`customization_id`가 앞서 승인한 commit의 기능과 맞음 | 다른 ID의 기능으로 보이는 조합이 있음 |

자동 작성 제안 파일을 엽니다.

```bash
open -t "$OM_TEST_REPO/harness/preparation-inputs/om-temp-1.13.1/shared-code-definitions-proposed.yaml"
```

세 조건이 모두 맞으면 다음 명령으로 제안 파일을 이번 1.13.1 **등록 초안 폴더**에 복사합니다.

```bash
cp "$OM_TEST_REPO/harness/preparation-inputs/om-temp-1.13.1/shared-code-definitions-proposed.yaml" \
  "$OM_TEST_REPO/harness/registrations/om-temp-1.13.1/shared-code-definitions.yaml"
```

이 명령은 확인한 제안을 **등록 초안**으로 복사합니다. 승인은 아직 하지 않습니다.

정식 승인은 다음 순서로 한 번만 진행합니다.

```text
공용 코드 정의 초안 준비
        ↓
Manifest·Registry·Contract 초안 준비
        ↓
모든 등록자료를 대상으로 plan 실행
        ↓
registration-approval.yaml 한 파일에 전체 승인 기록
        ↓
apply
```

등록자료마다 승인서를 따로 만들지 않습니다. 모든 초안을 준비한 뒤 승인서 한 개로 승인합니다. 작성 방법은 7/11 페이지에서 안내합니다.

> **\*참고 — 세 파일의 역할:** `draft`는 빈 양식, `proposed`는 자동 작성 제안, 등록 폴더의 `shared-code-definitions.yaml`은 검토할 등록 초안입니다.

## 3. 나머지 최초 등록 입력 준비

이 단계에서는 다음 두 종류의 파일을 순서대로 만듭니다.

```text
1. 사람이 작성할 최초 등록 입력 파일 생성
                    ↓
2. 입력 파일의 담당자·필수 경로·Contract 확인
                    ↓
3. Manifest·Registry·Contract 제안 파일 자동 생성
```

첫 번째 파일은 사람이 작성하는 입력이고, 세 번째 단계의 파일들은 생성기가 만든 검토용 제안입니다. 아직 승인하거나 활성 등록 폴더에 반영하지 않습니다.

| 입력 | 자동으로 준비되는 부분 | 사용자가 작성·승인할 부분 | 다음 사용 |
|---|---|---|---|
| `source-snapshot-path-owners.yaml` | 사전 준비 도구가 111개 경로와 ID 연결을 기록 | 이전 페이지의 승인 분류와 같은지 확인 | 최초 등록 기준 재구성 검사 |
| `shared-path-owners.yaml` | 사전 준비 도구가 37개 공용 경로를 추출 | 각 경로의 관련 ID 전체 확인 | 공용 경로·ID 일치 검사 |
| `shared-code-definitions.yaml` | 114개 조합의 실제 코드 조각·JSON·YAML 값을 ID commit에서 자동 제안하고 최종 커스텀 branch에서 검산 | 이전 단계에서 승인한 ID commit과 자동 추출 결과의 귀속이 맞는지 확인 | 공용 파일 ID별 코드 정의 검사와 등록 `plan` digest |
| Manifest 7개 | ID별 commit·실제 변경 경로를 Git에서 생성 | 필수 경로·Contract 연결 확인 | 최초 등록 검사 입력 |
| `customization-registry.yaml` | 코드 SHA·경로 수를 Git에서 생성 | 제목·담당자·중요도 확인 | 등록 기준 |
| `contracts.yaml` | 업무 입력 파일의 Contract를 옮겨 생성 | 정상 조건과 필수 test 확인 | Contract test 기준 |

### 3-1. 최초 등록 입력 파일 생성

아래 명령은 BANK-OM commit 이력을 읽어 최초 등록 입력 양식을 만듭니다. 특정 OpenMetadata 버전에만 사용하는 명령이 아닙니다.

```bash
cd "$OM_TEST_REPO"
```

```bash
./.venv/bin/python harness/om_workflow.py bootstrap-input-template \
  --repo "$OM_CODE_REPO" \
  --version 1.13.1 \
  --official-ref upstream-1.13.1-release \
  --custom-ref codex/om-1.13.1-id-series-upstream \
  --repository easyseop/OM_TEMP \
  --upstream-repository open-metadata/OpenMetadata \
  --upstream-tag 1.13.1-release \
  --output harness/preparation-inputs/om-temp-1.13.1/initial-registration-input.yaml
```

**처음 생성한 경우:** `status`가 `INPUT_TEMPLATE_WRITTEN`입니다.

**이미 파일이 있는 경우:** `status`가 `INPUT_TEMPLATE_EXISTS`입니다. 기존 작성 내용을 덮어쓰지 않으므로 그대로 다음 단계로 이동합니다.

```json
{
  "status": "INPUT_TEMPLATE_WRITTEN",
  "input": "harness/preparation-inputs/om-temp-1.13.1/initial-registration-input.yaml",
  "customization_count": 7,
  "contract_count": 7
}
```

### 3-2. 생성된 입력 파일의 경로와 작성 내용 확인

사람이 수정할 파일은 다음 한 개입니다.

```text
$OM_TEST_REPO/harness/preparation-inputs/om-temp-1.13.1/initial-registration-input.yaml
```

경로와 앞부분을 터미널에서 확인합니다. 이 화면은 **최초 등록 입력 파일 생성 결과 예시**로 캡처할 수 있습니다.

```bash
INITIAL_INPUT="$OM_TEST_REPO/harness/preparation-inputs/om-temp-1.13.1/initial-registration-input.yaml"
```

```bash
printf '[최초 등록 입력 파일] %s\n' "$INITIAL_INPUT"
```

```bash
sed -n '1,100p' "$INITIAL_INPUT"
```

| 입력 항목 | 자동으로 채우는 값 | 사람이 확인·수정할 값 |
|---|---|---|
| BANK-OM ID | commit의 `Customization-ID` | ID가 기능과 맞는지 확인 |
| 제목 | commit 제목 | 운영 문서에서 사용할 기능명으로 수정 |
| 담당자 | `UNASSIGNED` | 실제 담당자로 수정 |
| 중요도 | `medium` | 실제 영향도에 맞게 수정 |
| 필수 경로 | 해당 ID commit이 수정한 경로 | 기능에 반드시 필요한 경로만 남김 |
| Contract | ID별 `TODO` 초안 | 정상 동작 설명과 실제 test 경로 작성 |

다음 항목을 모두 채운 뒤 `plan`을 실행합니다.

| 반드시 채울 항목 | 완료 기준 | 누락 시 결과 |
|---|---|---|
| 담당자 | `owner`에 실제 담당자 식별값을 쓰고 `owner_status: assigned`로 변경 | `BLOCKED · OWNER_NOT_ASSIGNED` |
| 필수 경로 | 기능 유지에 반드시 필요한 경로가 한 개 이상 있음 | 입력 형식 오류로 생성 중단 |
| Contract | `invariant`에 정상 동작, `required_tests`에 실제 test를 기록 | `BLOCKED · CONTRACT_INCOMPLETE` |
| 선행 ID | 실제 선행 기능이 있을 때만 `depends_on`에 등록된 BANK-OM ID 작성 | 알 수 없는 ID·자기 자신·순환 관계는 `BLOCKED` |

`depends_on`은 Git이 자동으로 판단하지 않습니다. 예를 들어 `BANK-OM-002`가 `BANK-OM-001`이 만든 공통코드 없이는 동작하지 않을 때만 `BANK-OM-001`을 적습니다.

### 3-3. 제안 파일을 저장할 폴더 지정

`RUN_ID`는 한 번의 `plan → 승인 → apply` 시도를 구분하는 값입니다. 입력이나 코드를 고쳐 `plan`을 다시 실행할 때는 이전 결과를 보존하도록 새 값을 사용합니다.

```bash
RUN_ID=20260806-01
```

```bash
PROPOSAL_DIR="$OM_TEST_REPO/evidence/om-1.13.1-initial-bootstrap-$RUN_ID/proposal"
```

### 3-4. 최초 등록 제안 생성

```bash
cd "$OM_TEST_REPO"
```

```bash
./.venv/bin/python harness/om_workflow.py bootstrap-plan \
  --repo "$OM_CODE_REPO" \
  --version 1.13.1 \
  --official-ref afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9 \
  --custom-ref codex/om-1.13.1-id-series-upstream \
  --input "$INITIAL_INPUT" \
  --output "$PROPOSAL_DIR"
```

먼저 `status`를 확인합니다.

| 결과 | 뜻 | 다음 행동 |
|---|---|---|
| `BLOCKED` · 종료코드 `1` | 담당자·Contract·선행 ID 등 필수 결정이 미완료 | `summary.md`의 **반드시 수정할 항목**을 고치고 새 `RUN_ID`로 다시 실행 |
| `PROPOSAL_WRITTEN` · 종료코드 `2` | 필수 입력이 완성되어 사람 검토 가능 | 수량과 제안 파일을 확인한 뒤 다음 페이지로 이동 |
| `ANALYSIS_ERROR` · 종료코드 `3` | YAML 형식·Git 참조·필수 목록 오류로 분석 불가 | 출력된 오류를 고친 뒤 새 `RUN_ID`로 다시 실행 |

현재 예행연습 입력처럼 담당자가 아직 정해지지 않았다면 다음과 같이 **정상적으로 차단**됩니다.

```json
{
  "status": "BLOCKED",
  "customization_count": 7,
  "commit_count": 7,
  "changed_path_count": 111,
  "shared_path_count": 37,
  "blocking_findings": [
    {
      "code": "OWNER_NOT_ASSIGNED",
      "customization_id": "BANK-OM-001",
      "next_action": "owner에 실제 담당자를 입력하고 owner_status를 assigned로 변경합니다."
    }
  ]
}
```

이 경우 proposal은 진단용으로 남지만 승인 양식 생성과 `apply`는 실행할 수 없습니다.

입력을 모두 고쳐 다시 실행하면 다음 결과가 나와야 합니다.

```json
{
  "status": "PROPOSAL_WRITTEN",
  "customization_count": 7,
  "commit_count": 7,
  "changed_path_count": 111,
  "shared_path_count": 37,
  "proposal": ".../proposal/proposal.yaml",
  "summary": ".../proposal/summary.md",
  "proposed_registration": ".../proposal/proposed-registration"
}
```

`BANK-OM 7개`, `commit 7개`, `변경 경로 111개`, `공용 경로 37개`도 함께 확인합니다. ID별 commit과 전체 변경 경로는 `proposal.yaml`에 저장됩니다.

### 3-5. 생성된 제안 파일의 경로 확인

먼저 요약을 읽습니다. `BLOCKED`이면 **반드시 수정할 항목**이 함께 표시됩니다.

```bash
sed -n '1,200p' "$PROPOSAL_DIR/summary.md"
```

다음 명령은 이번 실행에서 생성된 파일만 경로순으로 보여줍니다. 이 화면은 **최초 등록 제안 생성 결과 예시**로 캡처할 수 있습니다.

```bash
find "$PROPOSAL_DIR" -type f | sort
```

**생성 경로:**

```text
$PROPOSAL_DIR/
├── proposal.yaml
├── proposal-digest.txt
├── summary.md
└── proposed-registration/
    ├── customization-registry.yaml
    ├── contracts.yaml
    ├── manifests/
    │   ├── BANK-OM-001.yaml
    │   ├── BANK-OM-002.yaml
    │   └── ... BANK-OM-007.yaml
    ├── shared-path-owners.yaml
    ├── source-diff-paths.txt
    └── source-snapshot-path-owners.yaml
```

| 생성 결과 | 내용 |
|---|---|
| `proposal.yaml` | 입력·commit·생성 파일의 기준값 |
| `proposal-digest.txt` | 이번 제안 전체를 식별하는 값 |
| `summary.md` | 수량과 제안 식별값 요약 |
| `proposed-registration/customization-registry.yaml` | 7개 BANK-OM ID의 제목·담당자·코드 기준값 제안 |
| `proposed-registration/contracts.yaml` | 정상 동작과 필수 test 연결 제안 |
| `proposed-registration/manifests/` | ID별 Manifest 7개 제안 |
| `proposed-registration/*path*` | 변경 경로와 ID 연결 제안 |

Manifest 한 개를 캡처하려면 다음 명령으로 `BANK-OM-001` 예시를 엽니다.

```bash
sed -n '1,140p' "$PROPOSAL_DIR/proposed-registration/manifests/BANK-OM-001.yaml"
```

활성 등록 폴더는 아직 바뀌지 않습니다. `summary.md`가 `REVIEW_REQUIRED`이고 `반영 가능: yes`일 때만 다음 페이지에서 승인합니다.

## 4. 다음 페이지로 넘길 입력 확인

| 확인할 입력 | 준비 완료 기준 | 미완료 예시 |
|---|---|---|
| 1.13.1 등록 준비 branch | 7개 ID별 commit과 111개 최종 변경 경로 | `Customization-ID`가 없는 commit이 있거나 제외 파일이 diff에 남음 |
| `source-snapshot-path-owners.yaml` | 111개 경로가 하나 이상의 BANK-OM ID에 연결 | 누락 경로가 있음 |
| `shared-path-owners.yaml` | 37개 공용 경로가 114개 경로·ID 조합을 설명 | ID가 하나뿐인 경로가 공용 표에 들어감 |
| `shared-code-definitions.yaml` | 자동 작성 제안이 114개 조합을 모두 포함하고 최종 커스텀 branch 검증이 `PASS`; 등록 `plan`의 검토 입력으로 복사됨 | `assertions: []`, `draft_notice`, 114개 미만 조합 또는 자동검증 오류 |
| 최초 등록 제안 | `status: REVIEW_REQUIRED`, `반영 가능: yes`; 7개 Manifest·Registry·Contract가 생성됨 | `BLOCKED`, `ANALYSIS_ERROR` 또는 수량 불일치 |
| 업무 입력 | 7개 ID의 담당자·필수 경로·Contract·선행 ID 확인 완료 | `UNASSIGNED`, `TODO`, 빈 필수 경로, 잘못된 선행 ID |

## 5. 이번 가이드 완료 기준

- [ ] 공식 branch와 등록 준비 branch의 최종 변경 경로가 111개입니다.
- [ ] 제외 파일 2개가 공식 branch와 같아 별도 복원 commit이 필요하지 않습니다.
- [ ] 이번 1.13.1용 경로 기준 파일이 준비되어 있습니다.
- [ ] 114개 공용 경로·ID 조합의 assertion 자동 작성과 최종 커스텀 branch 검증이 완료됐습니다.
- [ ] 사용자가 ID별 commit SHA와 114개 조합의 귀속을 확인했고, 자동 작성 제안을 등록 `plan`의 검토 입력으로 복사했습니다.
- [ ] `bootstrap-plan` 요약이 `REVIEW_REQUIRED`이고 `반영 가능: yes`입니다.
- [ ] `bootstrap-plan`이 Manifest 7개·Registry·Contract 초안을 생성했습니다.

위 항목을 모두 확인하기 전에는 승인·반영 또는 1.13.2 업그레이드 병합으로 이동하지 않습니다.

## 6. 향후 ID별 관리 구조 개선 계획

현재 검사기와 생성기는 모든 BANK-OM ID의 공용 코드 정의를 등록 폴더의 `shared-code-definitions.yaml` 한 파일에서 읽습니다. 따라서 이 예행연습에서는 자동 작성 제안 114개를 한 파일로 검토하고 등록 초안으로 복사합니다.

커스터마이징 ID와 assertion 수가 늘어나면 한 파일의 검토 범위와 승인 변경 범위도 함께 커집니다. 향후에는 다음과 같이 **BANK-OM ID별 공용 코드 정의 파일**로 분리할 계획입니다.

```text
harness/registrations/om-temp-1.13.1/
├── manifests/
│   ├── BANK-OM-001.yaml
│   └── BANK-OM-002.yaml
├── shared-code-definitions/
│   ├── BANK-OM-001.yaml
│   └── BANK-OM-002.yaml
└── indexes/
    ├── shared-path-owners.yaml
    └── source-snapshot-path-owners.yaml
```

`shared-code-definitions/BANK-OM-001.yaml`에는 공용 파일 안에서 `BANK-OM-001`에 해당하는 코드 정의만 기록합니다. 같은 실제 코드 파일을 `BANK-OM-001`과 `BANK-OM-002`가 함께 사용하면, 실제 코드 파일을 복사하지 않고 각 ID의 정의를 두 YAML 파일에 나누어 기록합니다.

여러 ID의 관계를 나타내는 `shared-path-owners.yaml`과 경로 전체를 찾기 위한 색인은 공통 파일로 유지합니다. 자동 작성 제안은 실행 ID별 증거 폴더에 ID별 파일과 전체 요약을 함께 저장하는 구조로 분리할 계획입니다.

> **현재 구현 상태:** 위 ID별 분리 구조는 개선 계획이며 아직 검사기에서 지원하지 않습니다. 현재 등록과 검사는 `shared-code-definitions.yaml` 한 파일을 사용합니다. ID별 파일 로더, 전체 파일 digest 계산, 중복·누락 검사와 `plan`·`apply` 처리를 구현하고 test한 뒤 운영 구조를 변경합니다.

**다음 문서:** [검사기 간단 학습 가이드](./OM_TEMP_1.13.1_1.13.2_검사기_간단_학습_가이드.html)
