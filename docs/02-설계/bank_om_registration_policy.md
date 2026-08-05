# BANK-OM 등록·후속 변경 운영규칙

이 문서는 BANK-OM ID를 발급하고, 코드 변경과 Manifest·Git 커밋·검사 결과를
연결하는 단일 기준 문서다. 사람용 가이드와 향후 LLM 위키는 이 문서를 기준으로
설명하며, 코드나 스키마와 충돌하면 실제 검사기 스키마를 먼저 확인한다.

## 1. 현재 구현 상태

| 구분 | 상태 | 기준 |
|---|---|---|
| BANK-OM 형식·Manifest 구조 검사 | 구현 완료 | `manifest.schema.json`, T10 |
| 커밋의 `Customization-ID` 검사 | 구현 완료 | T30·T31 |
| 변경 파일 범위·필수 파일 검사 | 구현 완료 | T26·T40·T93 |
| `upgrade_watch.paths` 비교 | 구현 완료 | T42 |
| 실제 변경 경로의 `upgrade_watch.paths` 자동 포함 | 구현 완료 | 공식 patch tree에 있는 경로만 자동 포함, 행내 신규 경로는 기능별 사람 판단 |
| 직접 참조된 공식 변경 파일의 watch 후보 제안 | 구현 완료·담당자 검토 필요 | `watch_suggest.py` |
| 담당자 `owner` 저장·검증 | 구현 완료·실제 배정 대기 | 별도 `customization-registry.yaml`, T29 |
| 공용 파일의 ID별 실제 코드 정의 검사 | 구현·단위 테스트 완료, 실제 1.13.1 정의 승인 대기 | `shared-code-definitions.yaml`, `shared_code.py` |

“구현 완료”, “담당자 확인 필요”, “행내 환경 대기”와 “추가 개발 예정”을
위키에서 섞어 설명하지 않는다.

## 2. ID 발급 원칙

1. ID 형식은 `BANK-OM-001`처럼 `BANK-OM-` 뒤에 세 자리 이상의 숫자를 쓴다.
2. 하나의 ID는 하나의 업무 기능을 대표한다.
3. 이미 사용했거나 `retired` 처리한 ID는 다시 사용하지 않는다.
4. 새 기능이면 새 ID를 발급한다.
5. 기존 기능의 버그 수정·누락 보완이면 같은 ID의 후속 커밋을 사용할 수 있다.
6. 같은 ID로 여러 커밋을 사용할 때는 Manifest의 `series.allowed: true`가
   필요하다.

### 같은 ID와 새 ID의 판단

| 질문 | 같으면 |
|---|---|
| 기존 기능과 업무 목적이 같은가? | 같은 ID 가능 |
| 기존 기능과 함께 배포·제거되어야 하는가? | 같은 ID 가능 |
| 같은 담당 조직과 테스트 계약으로 검증하는가? | 같은 ID 가능 |
| 독립 기능·독립 배포·독립 테스트가 필요한가? | 새 ID 발급 |

판단이 애매하면 새 ID를 발급하고 `depends_on`으로 선행 관계를 명시한다.

## 3. Manifest 항목

| 항목 | 쉬운 뜻 | 현재 검사 결과 |
|---|---|---|
| `changed_paths` | 현재 OpenMetadata 버전에서 같은 BANK-OM ID가 변경한 파일 전체 | 명단 밖 변경은 block, 일반 파일 누락은 approval |
| `required_changed_paths` | 누락만으로 필수 기능 소실을 확정할 파일 | 누락·공식 원본과 동일하면 block |
| `upgrade_watch.paths` | 실제 변경 경로와 담당자가 등록한 의존 경로 | 공식 A→B에서 바뀌면 approval |
| `assurance` | 실제 동작을 확인할 계약·기술 테스트 | 테스트 연결이 없거나 실패하면 통과 금지 |
| `series.depends_on` | 먼저 적용할 다른 BANK-OM | 순환·순서 위반 시 block |

### changed, required, watch

- `changed`는 “이 버전에서 이 기능이 실제로 어느 파일을 변경했는가?”에 답한다.
- `required`는 그중 “어느 파일이 빠지면 즉시 실패할 것인가?”에 답한다.
- `required` 파일은 현재 변경 범위에도 반드시 포함돼야 한다.
- `watch`는 “우리가 직접 변경했거나 의존하는 경로 중, 공식 새 버전에서도
  바뀌면 담당자가 다시 확인할 경로는 무엇인가?”에 답한다.
- 공용 파일은 파일 전체의 차이만으로 특정 코드 생존을 증명하기 어려우므로
  코드 내용 검사와 동작 검사를 함께 사용한다.

### 공용 파일의 ID별 코드 정의

`shared-path-owners.yaml`은 한 파일을 어떤 BANK-OM ID가 함께 사용하는지
기록한다. 이 연결표만으로는 각 ID의 코드가 최종 파일에 실제로 남아 있는지
판단할 수 없다. 예를 들어 `Entity.java`가 BANK-OM-001과 BANK-OM-002에
연결돼 있어도, 최종 파일에 BANK-OM-001 코드만 남을 수 있다.

새 등록 묶음에서 이 검사를 사용하려면 Registry의 `source`에 다음 파일을
선언한다.

```yaml
source:
  shared_code_definitions: shared-code-definitions.yaml
```

`shared-code-definitions.yaml`은 각 `공용 경로 + BANK-OM ID` 조합마다 승인한
실제 코드 정의를 기록한다. Java·TypeScript·TSX·SQL은 주석과 공백을 제외한
전체 코드 조각을 검사하고, JSON·YAML은 경로와 값을 함께 검사한다. 주석에
이름만 남아 있거나 같은 이름의 값이 달라진 경우에는 통과하지 않는다.

```yaml
schema_version: 1
definitions:
  - path: openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
    customization_id: BANK-OM-001
    assertions:
      - id: instance-code-entity-registration
        matcher: code_fragment
        fragment: |
          public static final String INSTANCE_CODE = "instanceCode";
  - path: openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json
    customization_id: BANK-OM-002
    assertions:
      - id: query-report-label
        matcher: json_value
        pointer: /label/query-report
        expected: 보고서 프로젝트
```

초안 생성기는 `shared-path-owners.yaml`에서 공용 경로와 ID 조합을 모두 만들지만
`assertions`는 비워 둔다. 어떤 코드 조각이 해당 업무 기능을 증명하는지는 Git이
결정할 수 없기 때문이다. 담당자가 실제 diff를 확인해 정의를 채운 뒤
Manifest·Registry·Contract와 같은 proposal에서 승인한다. Registry가 이 파일을
선언하면 준비도구는 파일 내용을 proposal digest에 포함하고 최종 custom commit의
코드와 비교한다. 정의 누락·형식 오류는 `ANALYSIS_ERROR`, 승인한 정의의 누락이나
값 불일치는 `BLOCK`이다.

이 검사는 소스 정의의 존재와 값을 확인한다. API 호출, DB 저장, 화면 동작처럼
실행 결과가 정상인지는 Contract test가 별도로 확인한다.

실제 예시는 다음과 같다.

```yaml
implementation:
  changed_paths:
    # BANK-OM-001이 현재 버전에서 실제로 변경한 파일
    - openmetadata-service/.../Entity.java
    - openmetadata-service/.../InstanceCodeResource.java
  required_changed_paths:
    # 이 파일이 없으면 InstanceCode API 자체가 없다고 판단할 수 있음
    - openmetadata-service/.../InstanceCodeResource.java
upgrade_watch:
  paths:
    # 공식 새 버전에서 Entity.java도 바뀌면 등록 연결을 다시 확인해야 함
    - openmetadata-service/.../Entity.java
    - openmetadata-service/.../CollectionDAO.java
```

이 예시에서 `Entity.java`는 `changed_paths`와 `watch`에 모두 들어간다. 행내
코드가 직접 변경했고, 공식 새 버전에서도 같은 파일이 바뀌면 충돌·누락 가능성을
다시 봐야 하기 때문이다. `InstanceCodeResource.java`는 행내에서 추가한 핵심
구현이므로 `changed_paths`와 `required`에 들어간다. `CollectionDAO.java`는
행내 코드가 직접 변경하지 않았더라도 InstanceCode 저장 동작이 의존하고 있어
공식 변경 시 재검토가 필요한 경우에만 `watch`에 들어간다.

### 현재 watch 운영

현재 검사 전 준비도구는 각 BANK-OM commit의 실제 변경 경로를 Git에서 읽고
`changed_paths`와 `upgrade_watch.paths`의 직접 변경 경로 변경안을 만든다.
같은 ID의 후속 commit에서 새 파일이 추가되면 기존 목록과 별도 필드로 나누지
않고 현재 버전의 `changed_paths`에 합친다.

독립 설계 검토에서 공식 upstream tree에 없는 행내 신규 파일까지 watch에
넣으면 T93 정책 노후화 검사가 매번 `stale_pattern` APPROVAL을 만든다는
문제를 확인했다. 현재 준비 자동화는 공식 upstream tree에 존재하는 변경
경로만 watch 후보에 자동 포함한다. 행내 신규 파일은 `changed_paths`로 계속
검사하되 watch 자동 포함을 보류하고 BANK-OM별 한 개의 담당자 판단 항목으로
묶는다. 기존 watch 값은 승인 없이 삭제하지 않는다.

행내에서 직접 수정하지 않았지만 커스터마이징이 의존하는 경로는 담당자가
`watch_dependencies`로 등록한다. 새 공식 버전에서 바뀐 파일 이름을
커스터마이징 코드가 직접 참조하면 `watch_suggest.py`가 후보 경로와 참조한 파일을
제시한다. 이 제안은 Manifest를 자동 수정하거나 승인하지 않으며 담당자가 확인한
뒤 반영한다.

T42는 이전 공식 버전과 새 공식 버전 사이의 Git 변경 경로를
`upgrade_watch.paths`와 비교한다. 경로가 겹치면 충돌 확정이 아니라
`approval`, 즉 재적용 전에 담당자가 영향을 확인해야 한다는 결과를 낸다. 간접
호출이나 런타임 설정처럼 파일 이름의 직접 참조로 찾기 어려운 관계는 여전히
담당자가 등록해야 한다.

## 4. 최초 등록 절차

1. 관리 담당자가 미사용 BANK-OM ID를 발급한다.
2. 제품 commit 본문에 `Customization-ID: BANK-OM-NNN`을 기록한다.
3. Contract에 정상이라고 판단할 업무 동작과 필수 test를 기록하고 새 ID를
   연결한다.
4. 공용 변경 파일이 있으면 `shared-path-owners.yaml`로 ID 연결을 확정하고,
   초안 생성 후 `shared-code-definitions.yaml`에 ID별 실제 코드 정의를 작성한다.
5. 준비도구의 `plan`을 실행한다. 도구는 실제 commit 변경 파일과 기존
   등록자료를 비교해 Manifest·Registry 변경안과 사람이 답할 질문을 만든다.
6. 담당자는 `changed_paths`, `required_changed_paths`,
   `upgrade_watch.paths`, 의존 경로, 담당 조직과 Contract 연결을 검토한다.
7. 담당자는 proposal의 digest와 질문별 판단 근거를 승인서에 기록한다.
8. `apply`는 승인한 변경안과 현재 Git·등록자료가 그대로일 때만 변경 대상
   Manifest와 `commit-inventory.yaml`, `current-diff-paths.txt`를 반영한다.
   Registry 변경이 필요한 경우에는 proposal에 표시된 변경도 함께 반영한다.
   Contract는 자동으로 수정하지 않는다.
9. Registry에는 담당 조직·상태와 `provenance`를 기록한다. 최초 source
   snapshot에 있던 기능은 `source-snapshot`, snapshot 이후 새 기능은
   `candidate-follow-up`을 명시한다.
10. patch-replay 전략을 사용할 때만 Git commit SHA와 적용 순서를 patch-lock에
   기록한다.
11. 등록자료 검증과 T10·T25·T26·T30·T31·T40·T60-I·T93 검사를 실행한다.
    T42는 공식 버전 업그레이드에서만 vendor-merge 전에 실행한다.

## 5. 같은 ID의 후속 커밋 절차

실제 예: BANK-OM-007은 최초 커밋에서 8개 파일을 변경한 뒤 후속 커밋에서
`serviceConnection.ts`와 `DatabaseServiceUtils.test.tsx`를 새로 추가했다.

1. Manifest의 `series.allowed`가 `true`인지 확인한다.
2. 후속 커밋에도 `Customization-ID: BANK-OM-007`을 넣는다.
3. 준비도구의 `plan`을 실행해 같은 ID의 commit 이력과 새 변경 경로를
   자동으로 찾는다.
4. 담당자는 새 경로가 필수인지, 공식 버전 영향 감시 대상인지, Contract를
   바꿔야 하는지 검토하고 proposal을 승인한다.
5. `apply`로 승인한 Manifest와 파생 등록자료 변경안을 반영한다. Registry
   변경이 필요한 경우에는 proposal에 해당 변경을 함께 표시한다.
6. patch-replay 전략을 사용할 때만 새 Git commit SHA와 적용 순서를
   patch-lock에 추가한다.
7. 관련 Contract·test가 바뀌었다면 담당자가 직접 갱신한다.
8. 등록자료 검증과 T30·T31·T40·T60-I·T93 등 영향을 받는 소스 검사를 다시
   실행한다. 같은 공식 버전 안의 후속 commit에는 T42를 실행하지 않는다.

```yaml
implementation:
  changed_paths:
    # 최초 구현 commit의 8개 파일도 이 목록에 함께 유지
    - .../tiberoConnection.json
    - .../DatabaseServiceUtils.tsx
    # 후속 보완 commit에서 추가된 2개 파일
    - .../connections/serviceConnection.ts
    - .../DatabaseServiceUtils.test.tsx
series:
  allowed: true
```

## 6. 공식 버전 업그레이드 절차

1. 새 공식 버전만 담은 OpenMetadata 포크 브랜치를 준비한다.
2. T42로 이전 공식 버전과 새 공식 버전을 비교해 영향을 받을 BANK-OM ID와
   경로를 먼저 찾는다.
3. 직전 커스텀 브랜치와 새 OpenMetadata 포크 브랜치를 vendor-merge한다.
4. Git 충돌이 있으면 담당자가 코드를 선택·수정하고 해결 commit을 남긴다.
5. 최종 커스텀 브랜치 commit을 기준으로 `plan → 담당자 승인 → apply`를
   실행한다.
6. 등록자료 검사, 소스 검사, build, Contract test, T90 운영 단계 결과 검사를
   순서대로 수행한다.
7. 승인된 동일 commit에 검증 완료 tag와 Release lock을 만들고, 조직의
   승격 절차에 따라 릴리즈 브랜치에 반영한다.

T42는 병합 결과를 검사하지 않는다. 새 공식 버전이 watch 경로를 바꿨는지
병합 전에 알리는 검사다. vendor-merge 뒤 최종 커스텀 브랜치의 등록·소스 상태는
다른 검사 단계에서 확인한다.

현재 버전 Manifest는 과거 최초 범위를 보관하는 문서가 아니라 현재 검사 범위를
정의하는 문서다. 따라서 최초 8개와 후속 2개를 합친 10개를
`changed_paths` 하나에 기록한다. “어느 커밋에서 어떤 파일이 추가됐는가”는
Manifest 필드를 둘로 나누지 않고 Git commit 이력으로 확인한다.

구체적으로 BANK-OM-007에는 기능 변경 commit SHA가 두 개 있다.

```text
62e39da8...  최초 구현: 8개 파일 변경
7d19c895...  누락 보완: 2개 파일 추가
```

두 SHA 중 하나를 “대표 SHA”로 덮어쓰지 않는다. 첫 번째 commit을 지우면 최초
8개 파일을 만든 변경 근거가 사라지고, 두 번째 commit을 지우면 추가 2개 파일의
근거가 사라지기 때문이다. 다만 최종 검사 실행은 두 commit이 모두 반영된
`custom/om-1.13.0`의 마지막 commit SHA 하나를 Candidate lock에 기록한다.

```text
BANK-OM-007 기능 변경 이력: 62e39da8... → 7d19c895...
최종 검사 대상 코드:     custom/om-1.13.0 HEAD의 SHA 1개
```

## 6. 담당자 정보

Manifest 스키마에는 `owner` 필드가 없다. 담당 조직과 배정 상태는 별도
`customization-registry.yaml`의 `owner`, `owner_status`에 기록한다.
T29 Registry 준비 검사는 active BANK-OM의 `owner_status`가 `assigned`가 아니면
배포 준비를 `block`한다.

현재 OM_TEMP BANK-OM-001~007은 모두 `owner: UNASSIGNED`,
`owner_status: pending`이다. 저장·검사 방식은 구현됐지만 실제 담당 조직과
승인자는 외부 입력이 필요하므로 배정 완료로 표시하지 않는다.

## 7. LLM 위키 반영 규칙

LLM 위키는 이 문서를 원본으로 사용하고 다음 항목을 반드시 표시한다.

1. 현재 구현 완료와 향후 개선을 별도 상태로 표시
2. BANK-OM ID와 Git 커밋 SHA를 서로 다른 개념으로 설명
3. `changed`·`required`·`watch`의 판정 차이 표시
4. 같은 ID 후속 변경과 새 ID 발급 판단표 포함
5. 기능 변경 commit SHA 여러 개와 최종 검사 대상 SHA 한 개의 차이와 예시 포함
6. 파일 검사·코드 내용 검사·실제 동작 검사의 한계와 역할 구분
7. `owner`는 Manifest가 아니라 별도 Registry에 저장하며, `UNASSIGNED` 상태를
   배정 완료로 서술하지 않음

스키마나 운영정책이 바뀌면 이 문서를 먼저 갱신한 뒤 사용자 가이드와 LLM
위키를 동기화한다.

## 8. 저장소와 브랜치 역할

| 위치 | 저장하는 것 | 현재 상태 |
|---|---|---|
| `easyseop/OpenMetadata` | 처음 분석한 커스터마이징 코드 보관·참고 | `849ae756…`는 과거 소스 검사 후보이며 현재 OM_TEMP 업그레이드 대상이 아님 |
| `easyseop/OM_TEMP` | 1.13.0→1.13.1 업그레이드·검사 재현용 제품 코드 | private 저장소에 1.13.0 patch/custom branch가 있고 1.13.1 결과는 아직 다른 작업 노트북의 로컬에만 있음 |
| `easyseop/openmetadata-test` | BANK-OM Manifest·검사기·검사 결과·운영규칙 | `codex/strict-manifest-gates`에서 관리 |

`easyseop/OpenMetadata`의 BANK-OM-001~011 코드는
`codex/bank-vendor-1.13.1-rebuild` 브랜치에 보관돼 있다. 이 중 008~011은
기술 보완용 임시 ID이며 사용자 확정 전에는 승인된 업무 커스터마이징으로
표현하지 않는다. 현재 반복 업그레이드 시연은 BANK-OM-001~007만 사용한
`easyseop/OM_TEMP`를 기준으로 한다.

BANK-OM 변경관리표·검사 결과·인수인계 문서는 제품 저장소에 중복 보관하지
않고 `easyseop/openmetadata-test`에서 관리한다. LLM 위키는 두 저장소를
다음처럼 연결해 설명한다.

```text
제품 저장소의 코드·커밋
        ↕ Customization-ID
검사 저장소의 Manifest·테스트·결과
```

`849ae756…`와 OM_TEMP 결과 모두 행내 운영환경에 실제 배포됐다는 증거가
없다. 어느 쪽도 “직원이 현재 사용하는 운영 제품”이라고 표현하지 않는다.
