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
| 실제 변경 경로의 `upgrade_watch.paths` 자동 포함 | 구현 완료 | OM_TEMP Manifest 생성기 |
| 직접 참조된 공식 변경 파일의 watch 후보 제안 | 구현 완료·담당자 검토 필요 | `watch_suggest.py` |
| 담당자 `owner` 저장·검증 | 구현 완료·실제 배정 대기 | 별도 `customization-registry.yaml`, T29 |

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
| `allowed_changed_paths` | 최초 등록 시 실제로 변경한 파일 전체 | 명단 밖 변경은 block, 명단 안 누락은 approval |
| `required_changed_paths` | 누락만으로 필수 기능 소실을 확정할 파일 | 누락·공식 원본과 동일하면 block |
| `candidate_additional_paths` | 같은 ID의 후속 커밋이 새로 추가한 파일 | 현재 변경 범위에 포함, 최초 재구성에서는 제외 |
| `upgrade_watch.paths` | 실제 변경 경로와 담당자가 등록한 의존 경로 | 공식 A→B에서 바뀌면 approval |
| `assurance` | 실제 동작을 확인할 계약·기술 테스트 | 테스트 연결이 없거나 실패하면 통과 금지 |
| `series.depends_on` | 먼저 적용할 다른 BANK-OM | 순환·순서 위반 시 block |

### allowed와 required

- `allowed`는 “이 기능이 실제로 어느 파일을 변경했는가?”에 답한다.
- `required`는 그중 “어느 파일이 빠지면 즉시 실패할 것인가?”에 답한다.
- `required` 파일은 현재 변경 범위에도 반드시 포함돼야 한다.
- 공용 파일은 파일 전체의 차이만으로 특정 코드 생존을 증명하기 어려우므로
  코드 내용 검사와 동작 검사를 함께 사용한다.

### 현재 watch 운영

현재 OM_TEMP Manifest 생성기는 각 BANK-OM commit의 실제 변경 경로를 Git에서
읽고 `upgrade_watch.paths`에 자동으로 포함한다. 같은 ID의 후속 commit에서 처음
추가된 `candidate_additional_paths`도 현재 변경 범위에 포함된다.

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
2. 실제 커밋의 변경 파일을 확인해 `allowed_changed_paths`에 개별 파일로
   등록한다.
3. 누락만으로 기능 소실을 확정할 파일을 `required_changed_paths`로 지정한다.
4. Manifest 생성기가 실제 변경 경로를 `upgrade_watch.paths`에 포함했는지
   확인하고, 직접 수정하지 않은 의존 경로를 추가한다.
5. 직접 참조 후보가 있으면 담당자가 근거를 검토해 반영 여부를 결정한다.
6. 업무 계약과 실제 테스트를 `assurance`에 연결한다.
7. 별도 Registry에 담당 조직과 상태를 기록한다.
8. 제품 커밋 메시지에 `Customization-ID: BANK-OM-NNN`을 넣는다.
9. patch-replay 전략을 사용할 때만 Git commit SHA와 적용 순서를 patch-lock에
   기록한다.
10. T10·T25·T26·T30·T31·T40·T42·T60-I·T93 검사를 실행한다.

## 5. 같은 ID의 후속 커밋 절차

예: 최초 BANK-OM-001이 48개 파일을 변경한 뒤
`InstanceCodeValidator.java`를 새로 추가하는 경우.

1. 후속 커밋에도 `Customization-ID: BANK-OM-001`을 넣는다.
2. 새 Git 커밋 식별값(SHA)과 적용 순서를 patch-lock에 추가한다.
3. 새 파일을 `candidate_additional_paths`에 추가한다.
4. 파일이 필수 구성요소이면 `required_changed_paths`에도 추가한다.
5. 관련 계약·테스트를 갱신하고 전체 소스 검사를 다시 실행한다.

```yaml
implementation:
  candidate_additional_paths:
    - .../InstanceCodeValidator.java
```

Git 커밋 SHA만 추가하면 “어떤 변경이 생겼는가”는 알 수 있지만, 새 파일이
해당 BANK-OM의 승인 범위인지는 알 수 없다. 반대로 최초
`allowed_changed_paths`를 직접 고치면 과거 최초 스냅샷의 기록이 달라진다.
따라서 최초 범위는 보존하고 후속 파일을 별도로 기록한다.

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
3. `allowed`·`required`·`watch`의 판정 차이 표시
4. 같은 ID 후속 변경과 새 ID 발급 판단표 포함
5. `candidate_additional_paths`를 쓰는 이유와 예시 포함
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
