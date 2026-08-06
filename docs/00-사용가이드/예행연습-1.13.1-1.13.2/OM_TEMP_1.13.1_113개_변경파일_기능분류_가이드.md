# OM_TEMP 1.13.1 변경 파일과 BANK-OM ID 연결 가이드

**전체 순서:** 3/11 · [전체 목차](./OM_TEMP_1.13.1_1.13.2_예행연습_전체목차.html)

> 문서 성격: 로컬 branch 연결 및 검증 이후에 사용하는 별도 검토 문서
> 목적: official·custom 사이의 113개 변경 파일을 BANK-OM 커스터마이징 ID별로 연결하고 등록 전 사용자 결정을 기록
> 시작 조건: `OM_TEMP_1.13.1_로컬브랜치_연결_및_검증_가이드`의 완료 기준 충족
> 종료점: 7개 BANK-OM 커스터마이징 ID의 업무 분류와 공용 변경 파일 37개의 다중 ID 연결 방식을 시연용으로 승인했습니다. 미등록 2개 경로의 제외 결정도 완료했습니다.
> 제외 범위: Manifest·Registry·Contract 파일 생성 또는 수정, 검사기 실행

**문서 이동:** [← 이전 단계 — 로컬 branch 연결 및 검증](./OM_TEMP_1.13.1_로컬브랜치_연결_및_검증_가이드.html)

## 공통 경로 설정

이 페이지의 명령을 실행할 터미널에서 검사기 저장소로 이동한 뒤 공통 경로를 불러옵니다. 다른 컴퓨터에서는 clone 위치만 바꾸면 됩니다.

```bash
cd <검사기-저장소-clone-경로>
```

```bash
source harness/rehearsal_env.sh
```

`OM_TEST_REPO`는 검사기 저장소, `OM_CODE_REPO`는 OpenMetadata 코드 작업 폴더, `KB_SOURCE_REPO`는 실제 커스터마이징 원본 폴더를 가리킵니다. 새 터미널을 열면 다시 실행합니다.

## 단계 연결 요약

| 구분 | 내용 |
|---|---|
| 이전 단계 요약 | 원격 official·custom branch를 로컬에 연결하고 commit, 작업 폴더 상태, 원본 동일성, 113개 변경 파일과 branch 관계를 검증했습니다. |
| 이번 단계 수행 범위 | 113개 변경 파일을 기존 BANK-OM 커스터마이징 ID별 참고자료와 대조하고, 여러 ID에 연결된 파일과 아직 ID가 없는 파일을 분리합니다. |
| 이번 단계 완료 결과 | Manifest 초안에 사용할 BANK-OM 커스터마이징 ID 목록과 각 변경 파일의 연결 방식이 확정됩니다. |

## 이 가이드에서 사용자가 할 일

| 구분 | 해당 장 | 사용자 행동 |
|---|---|---|
| 결과 이해 | 1~3장 | 분류 기준과 자동 분석 결과를 읽습니다. 미등록 파일 2개는 제외하기로 결정됐습니다. |
| 입력 재확인 | 4장 | 변경 파일이 여전히 113개인지 확인합니다. 직전 단계 이후 코드가 바뀌지 않았다면 생략할 수 있습니다. |
| 결정 결과 | 5장 | `BANK-OM-001`~`007` 유지와 공용 변경 파일 37개의 다중 연결 방식을 시연용으로 승인했습니다. |
| 완료 판정 | 6장 | 이 문서에서 요청한 두 분류 결정이 완료됐는지 확인합니다. 실제 코드 정의 승인은 다음 단계에서 별도로 진행합니다. |

이 문서에서 요구한 분류 결정은 2026-08-05에 완료했습니다. 이제 실제 diff를 근거로 공용 파일의 ID별 코드 정의를 작성하는 다음 단계로 이동합니다.

## 1. 분류 기준

이 문서의 `변경 파일`은 다음 두 branch 사이에서 파일 내용이 다른 경로를 뜻합니다.

| 비교 기준 | branch | Git commit SHA |
|---|---|---|
| 공식 기준 코드 | `official/om-1.13.1` | `e6199070…` |
| 실제 커스터마이징 코드 | `custom/om-1.13.1` | `59dae915…` |

Git은 변경 파일 113개를 자동으로 찾을 수 있습니다. 그러나 Git은 각 변경 파일을 어떤 BANK-OM 커스터마이징 ID에 연결할지 결정하지 못합니다. 업무 기능명, BANK-OM 커스터마이징 ID, 여러 ID가 함께 사용하는 파일의 연결 방식과 아직 ID가 없는 파일의 처리방안은 사용자가 승인해야 합니다.

### 이 문서에서 구분하는 네 가지 대상

| 용어 | 이 문서에서의 의미 | 실제 예시 |
|---|---|---|
| BANK-OM 커스터마이징 ID | 하나의 커스터마이징 업무 단위를 계속 추적하는 관리번호입니다. Git이 자동 생성하지 않습니다. | `BANK-OM-001` |
| 업무 기능명 | 해당 BANK-OM 커스터마이징 ID가 제공하는 동작의 이름입니다. | `InstanceCode` |
| Git commit SHA | 특정 시점의 코드 변경 묶음을 Git이 식별하는 값입니다. BANK-OM 커스터마이징 ID와 다른 값입니다. | `59dae915…` |
| 변경 파일 | official branch와 custom branch를 비교했을 때 내용이 다른 파일입니다. | `Entity.java` |

이 문서의 분류 대상은 **Git commit SHA가 아니라 113개 변경 파일**입니다. 각 변경 파일을 `BANK-OM-001`~`007` 중 어느 커스터마이징 ID에 연결할지 확인합니다. 하나의 BANK-OM 커스터마이징 ID에는 여러 변경 파일과 여러 Git commit SHA가 누적될 수 있습니다.

과거 재구성 과정에서 만든 `BANK-OM-008`~`011`은 이번 1.13.1 등록 대상에서 제외합니다. 이 문서의 분석·승인·완료 조건은 `BANK-OM-001`~`007`만 대상으로 합니다.

## 2. 자동 분석 결과

기존 `kb-openmetadata` 등록자료를 참고자료로 대조한 결과는 다음과 같습니다. 이 표는 신규 1.13.1 등록자료가 아니며, 사용자가 승인하기 전에는 정본으로 사용하지 않습니다.

| 구분 | 고유 경로 수 | 의미 |
|---|---:|---|
| 하나의 BANK-OM 커스터마이징 ID에만 연결된 변경 파일 | 74 | 7개 ID 중 하나에만 연결됩니다. 예: 한글 IME 보정 코드만 담은 파일입니다. |
| 둘 이상의 BANK-OM 커스터마이징 ID에 연결된 공용 변경 파일 | 37 | 한 파일에 여러 커스터마이징의 코드가 함께 있습니다. 예: 여러 화면 경로를 등록하는 router 파일입니다. |
| `BANK-OM-001`~`007` 중 어느 ID에도 연결되지 않은 변경 파일 | 2 | 이번 등록에서 제외하기로 결정한 파일입니다. |
| 전체 변경 경로 | 113 | `74 + 37 + 2`입니다. |

74개와 37개는 서로 겹치지 않는 **고유 변경 파일 수**입니다. 37개 공용 변경 파일을 관련된 각 BANK-OM 커스터마이징 ID에서 다시 표시하므로, 아래 ID별 `연결 경로` 수를 모두 더하면 113보다 커집니다. 미등록 2개를 제외하면 BANK-OM 등록 대상은 111개입니다.

113개 경로 각각의 Git 변경 상태, 분류, 연결 ID는
[`OM_TEMP_1.13.1_113개_변경파일_기능분류_시연초안.yaml`](./OM_TEMP_1.13.1_113개_변경파일_기능분류_시연초안.yaml)에서 확인할 수 있습니다.
이 파일은 실제 `official/om-1.13.1`과 `custom/om-1.13.1`을 다시 비교해 만든 시연용 검토표이며 Manifest나 Registry가 아닙니다.

### 주요 BANK-OM 커스터마이징 ID 후보

| BANK-OM 커스터마이징 ID 후보 | 업무 기능명 | 전체 연결 파일 | 해당 ID 전용 파일 | 다른 ID와 공용인 파일 | 대표 근거 |
|---|---|---:|---:|---:|---|
| `BANK-OM-001` | InstanceCode | 48 | 16 | 32 | InstanceCode schema·Resource·Repository·UI 페이지 |
| `BANK-OM-002` | QueryReport | 55 | 23 | 32 | QueryReport schema·Resource·Repository·UI 페이지 |
| `BANK-OM-003` | Data Assertions | 25 | 4 | 21 | DataAssertionsPage·API·MyData 실패 항목 UI |
| `BANK-OM-004` | 은행 컬럼 확장 표시 | 33 | 14 | 19 | SchemaTable·ExploreTree·검색 결과·Entity 유틸리티 |
| `BANK-OM-005` | 한글 IME 보정 | 1 | 1 | 0 | SchemaEditor 입력 처리 |
| `BANK-OM-006` | Sybase | 18 | 13 | 5 | Sybase schema·아이콘·서비스 연결 UI |
| `BANK-OM-007` | Tibero | 8 | 3 | 5 | Tibero schema·아이콘·서비스 연결 UI |

`전체 연결 파일` 개수에는 공용 변경 파일이 관련된 각 BANK-OM 커스터마이징 ID에 반복 집계됩니다. 따라서 ID별 전체 연결 파일 수를 합산하면 113보다 커지며, 이는 누락이나 중복 파일 생성이 아닙니다.

`BANK-OM-007`은 8개 경로 그대로 유지하는 것을 권장합니다. 추가 후보였던 `serviceConnection.ts`와 `DatabaseServiceUtils.test.tsx`의 실제 diff에는 Sybase 코드만 있고 Tibero 코드는 없으므로 Tibero에 연결하지 않습니다.

### 공용 변경 파일 예시

| 변경 파일 경로 | 함께 연결되는 BANK-OM 커스터마이징 ID | 공용인 이유 |
|---|---|---|
| `bootstrap/sql/migrations/native/1.13.1/mysql/schemaChanges.sql` | `BANK-OM-001`, `BANK-OM-002` | InstanceCode와 QueryReport의 DB 변경이 같은 migration 파일에 기록됨 |
| `openmetadata-service/src/main/java/org/openmetadata/service/Entity.java` | `BANK-OM-001`, `BANK-OM-002` | 두 신규 entity를 공통 등록함 |
| `openmetadata-ui/src/main/resources/ui/src/components/AppRouter/AuthenticatedAppRouter.tsx` | `BANK-OM-001`, `BANK-OM-002`, `BANK-OM-003` | 세 업무 기능의 화면 경로를 같은 router에 등록함 |
| `openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json` | `BANK-OM-001`~`BANK-OM-004` | 네 업무 기능의 번역 항목이 같은 언어 파일에 기록됨 |
| `openmetadata-spec/src/main/resources/json/schema/entity/services/databaseService.json` | `BANK-OM-006`, `BANK-OM-007` | Sybase와 Tibero를 같은 database service 목록에 등록함 |

공용 변경 파일은 하나의 BANK-OM 커스터마이징 ID에 임의로 독점 배정하지 않습니다. 다음 Manifest 단계에서 관련된 모든 BANK-OM 커스터마이징 ID에 연결하고 `shared-path-owners.yaml`에도 같은 관계를 기록합니다.

승인이 필요한 이유는 파일을 여러 번 복사하기 위해서가 아닙니다. 한 파일 안에 둘 이상의 BANK-OM 커스터마이징 코드가 함께 있으므로 실제 관련 ID를 모두 확정해야 합니다. 연결이 빠지면 업그레이드 재구성 과정에서 다른 ID의 코드가 누락될 수 있습니다. 검사기는 공용 경로 연결표가 실제 다중 연결 관계와 다르면 `SHARED_OWNER_MAP_MISMATCH`로 중단합니다.

**권장안:** 37개 공용 변경 파일을 현재 분석표에 기록된 모든 실제 관련 ID에 연결합니다.

**2026-08-04 시연 결정:** 위 권장안을 시연 자료에 적용합니다. 여기서 다중 연결은 같은 파일 경로를 관련된 여러 BANK-OM ID와 연결한다는 뜻입니다. 같은 `(파일 경로, BANK-OM ID)` 조합을 두 번 적는 중복 레코드는 만들지 않습니다. 이 시연 결정은 실제 운영 등록 승인이나 코드 정의 승인을 대신하지 않습니다.

### 공용 경로 연결만으로 부족한 부분과 보완 검사

`shared-path-owners.yaml`은 “이 파일을 어떤 BANK-OM 커스터마이징 ID가 함께 사용하는가”를 확인합니다. 그러나 파일 하나를 `BANK-OM-001`과 `BANK-OM-002`에 연결했다고 해서 두 ID의 코드가 최종 파일에 모두 남았다는 뜻은 아닙니다. 예를 들어 `Entity.java`에 InstanceCode 코드만 남고 QueryReport 코드가 빠져도 경로 연결 자체는 두 ID로 유지될 수 있습니다.

이 문제를 막기 위해 검사기에 `shared-code-definitions.yaml` 검사를 추가했습니다. 이 파일의 정식 명칭은 **공용 파일 ID별 코드 정의**입니다. Java의 변수명만 기록하는 파일이 아니라 Java·TypeScript·TSX·SQL의 실제 코드 조각과 JSON·YAML의 실제 경로·값을 BANK-OM 커스터마이징 ID별로 기록합니다.

```yaml
schema_version: 1
definitions:
  - path: openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
    customization_id: BANK-OM-001
    assertions:
      - id: instance-code-constant
        matcher: code_fragment
        fragment: |
          public static final String INSTANCE_CODE = "instanceCode";
  - path: openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
    customization_id: BANK-OM-002
    assertions:
      - id: query-report-constant
        matcher: code_fragment
        fragment: |
          public static final String QUERY_REPORT = "queryReport";
```

| 구분 | 자동 처리 | 사용자 확인 |
|---|---|---|
| 초안 생성 | `shared-path-owners.yaml`을 읽어 모든 `공용 경로 + BANK-OM ID` 조합을 만듭니다. | 없음 |
| 실제 정의 작성 | 자동 추측하지 않습니다. | 실제 diff를 보고 각 ID를 증명하는 전체 코드 조각 또는 JSON·YAML 경로와 값을 선택합니다. |
| 검사 | 주석과 공백을 제외한 코드 토큰 또는 JSON·YAML 값을 최종 custom commit과 비교합니다. | 불일치가 의도된 변경인지 확인합니다. |
| 결과 | 정의 형식·ID 연결 누락은 `ANALYSIS_ERROR`, 승인한 코드 정의 누락·값 불일치는 `BLOCK`입니다. | 수정 후 같은 검사를 다시 실행합니다. |

주석에 `QUERY_REPORT`라는 이름만 적혀 있거나, 실제 상수 값이 `"wrong"`으로 바뀐 경우에는 통과하지 않습니다. 이 검사는 코드 정의가 남아 있는지 확인하며, QueryReport가 실제로 생성·검색되는지는 Contract test가 별도로 확인합니다.

현재 이 검사 코드와 단위 테스트는 구현됐습니다. 37개 공용 경로에서 중복되지 않는 114개 `(파일 경로, BANK-OM ID)` 조합을 만든
[`OM_TEMP_1.13.1_shared-code-definitions_시연초안.yaml`](./OM_TEMP_1.13.1_shared-code-definitions_시연초안.yaml)도 생성했습니다.
다만 초안의 `assertions`는 모두 비어 있으므로 스키마 검사를 통과하지 않으며 실제 검사 입력으로 사용할 수 없습니다. 다음 Manifest 정의 단계에서 실제 OM_TEMP 1.13.1 diff를 확인해 각 ID를 증명하는 코드 조각·JSON·YAML 값을 채우고, Manifest·Registry·Contract와 같은 proposal에서 승인해야 합니다.

## 3. 미등록 경로 처리 결정

아래 2개 경로는 어느 BANK-OM 커스터마이징 ID에도 연결하지 않고 이번 등록에서 제외하기로 결정했습니다.

두 파일은 현재 source snapshot의 113개 변경 파일에는 포함되지만 BANK-OM 등록 대상에는 포함되지 않습니다. 따라서 등록 대상은 111개입니다. 이후 재구성할 custom candidate에서는 두 파일을 official branch와 같은 내용으로 유지해야 합니다. 검사기는 제외 경로가 official branch와 다르면 중단합니다.

### 3-1. `.claude/settings.json`

| 항목 | 내용 |
|---|---|
| 변경 성격 | Claude Code 개발 도구 권한과 자동 승인 설정 |
| 결정 | BANK-OM 등록 대상에서 제외 |
| 이유 | OpenMetadata 제품 기능 코드가 아니며 제품 커스터마이징 운영에 필요하지 않음 |
| 다음 코드 처리 | 최종 custom candidate에서는 official branch의 파일 내용으로 복원 |

### 3-2. `docker/development/docker-compose.yml`

| 항목 | 내용 |
|---|---|
| 변경 성격 | 로컬 개발용 ingestion image를 `openmetadata/ingestion:1.9.6`으로 바꾸는 설정 |
| 결정 | BANK-OM 등록 예외 경로로 제외 |
| 이유 | `BANK-OM-001`~`007`의 업무 기능과 직접 연결되지 않고 OpenMetadata 1.13.1과 다른 ingestion 버전을 사용할 위험이 있음 |
| 다음 코드 처리 | 최종 custom candidate에서는 official branch의 파일 내용으로 복원 |

**예외 처리의 정확한 의미:** 파일을 현재 내용 그대로 두고 검사만 생략한다는 뜻이 아닙니다. Manifest에는 등록하지 않으며, 최종 custom candidate에서는 official branch와 같은 내용이어야 합니다. 과거 source snapshot에 해당 변경이 있었다는 사실은 source inventory와 Git 이력에 남습니다.

## 4. 변경 파일 목록 확인 명령

**수행 내용**
official·custom 사이의 전체 변경 경로를 터미널에 출력합니다.

**입력**
검증이 끝난 로컬 `official/om-1.13.1`과 `custom/om-1.13.1`

```bash
git -C "$OM_CODE_REPO" diff --name-status official/om-1.13.1 custom/om-1.13.1
```

**예상 결과**
113개 경로가 표시됩니다. 현재 기준은 기존 파일 수정 `M` 70개와 새 파일 추가 `A` 43개입니다.

**중단 조건**
경로가 113개가 아니거나 `D`가 표시되면 이 문서의 분류 기준과 실제 custom branch가 다릅니다. 변경 파일과 BANK-OM 커스터마이징 ID 연결 작업을 중단하고 branch 검증 단계로 돌아갑니다.

## 5. 사용자 승인표

| 승인 항목 | 권장안 또는 결정 | 상태 |
|---|---|---|
| 7개 BANK-OM 커스터마이징 ID | `BANK-OM-001`~`007` 유지. 각 ID가 서로 다른 업무 동작과 변경 경로를 가지므로 합치지 않음 | 시연용 승인 완료 |
| 공용 변경 파일 37개 | 실제 코드가 들어 있는 모든 관련 ID를 연결하고 `shared-path-owners.yaml`에 같은 관계를 기록 | 시연용 승인 완료·운영 승인 아님 |
| 공용 파일 ID별 코드 정의 | 중복되지 않는 114개 경로·ID 조합의 빈 초안을 생성함. 실제 코드 조각·값은 다음 Manifest 정의 단계에서 검토 | 시연 초안 생성 완료·정의 승인 필요 |
| `.claude/settings.json` | BANK-OM 등록에서 제외하고 최종 custom candidate에서 official 내용으로 복원 | 결정 완료 |
| `docker/development/docker-compose.yml` | BANK-OM 등록 예외 경로로 제외하고 최종 custom candidate에서 official 내용으로 복원 | 결정 완료 |

### 왜 업무 분류와 실제 코드 정의를 승인해야 하는가

| 항목 | 승인이 필요한 이유 | 잘못 결정했을 때의 우려 |
|---|---|---|
| 7개 ID 유지 | Git은 파일 차이를 찾을 수 있지만 어떤 변경들이 하나의 업무 기능인지 결정하지 못함 | 서로 다른 기능을 합치면 한 기능만 제거·업그레이드·검증하기 어려워지고 Contract 연결도 불명확해짐 |
| 공용 변경 파일 37개의 실제 코드 정의 | 한 파일 안에 여러 ID의 symbol·JSON key·route·SQL block이 함께 있어 ID별 생존 기준을 사람이 확정해야 함 | 경로만 여러 ID에 연결하고 실제 정의를 비워 두면 특정 ID의 코드가 빠진 상태를 탐지할 수 없음 |

**2026-08-05 승인 결과:** 최종 권장안을 채택했습니다. `BANK-OM-001`~`007`을 유지하고, 공용 변경 파일 37개는 현재 분석된 모든 관련 ID에 연결합니다. 이 승인은 시연용 기능 분류에만 적용되며, 실제 코드 정의와 운영 등록을 승인한 것은 아닙니다.

## 6. 완료 기준

- [x] `BANK-OM-001`~`007` 유지 여부를 시연용으로 승인했습니다.
- [x] 공용 변경 파일 37개의 다중 ID 연결 방식을 시연용으로 승인했습니다.
- [ ] 공용 변경 파일 37개의 ID별 실제 코드 정의가 작성·승인되었습니다.

`.claude/settings.json`과 `docker/development/docker-compose.yml`은 BANK-OM 등록에서 제외하기로 이미 결정했습니다. 이 문서의 두 분류 승인 항목은 완료됐습니다. 실제 코드 정의가 작성·승인되기 전에는 시연 초안을 실제 Registry에 선언하거나 검사 입력으로 사용하지 않습니다.

## 7. 다음 단계

1. 공식 1.13.1에서 ID별 commit 후보 branch를 만들고, 사용자가 각 변경안을 승인한 뒤 `BANK-OM-001`~`007`을 commit마다 하나씩 기록합니다.
2. 후보 branch에서 등록 제외 파일 2개가 official 내용과 같은지 확인하고, official 대비 변경 경로가 111개인지 다시 확인합니다.
3. `shared-code-definitions` 시연 초안의 114개 경로·ID 조합을 실제 diff와 대조하고, ID별 코드 조각·JSON·YAML 값을 사용자와 함께 채웁니다.
4. 실제 코드 정의를 사용자가 승인한 뒤, 승인된 7개 ID와 공용 경로 연결표를 입력으로 Manifest·Registry·Contract 초안을 함께 작성합니다.
5. Registry가 코드 정의 파일을 사용하도록 선언한 뒤 준비도구의 `plan`을 실행합니다. 중단 결과도 현재 준비 상태를 설명하는 진단 결과로 보관합니다.

이 문서에서는 아직 code commit이나 등록자료를 만들지 않습니다. 다음 단계에서 명령과 결과를 별도 가이드로 안내합니다.

**문서 이동:** [← 이전 단계 — 로컬 branch 연결 및 검증](./OM_TEMP_1.13.1_로컬브랜치_연결_및_검증_가이드.html) · [다음 단계 — BANK-OM ID별 commit 후보 branch 구성 →](./OM_TEMP_1.13.1_BANK-OM_ID별_커밋_후보브랜치_구성_가이드.html)
