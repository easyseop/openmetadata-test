# OM_TEMP 1.13.0 → 1.13.1 업그레이드 실행 가이드

> 공식 기준: OpenMetadata `1.13.0-release` → `1.13.1-release`
>
> 로컬 branch: `patch/om-1.13.1`, `custom/om-1.13.1`
>
> 최종 검사 대상 commit: `dee330ebd5abfe33e1ac61e1ca31879746a1b423`

## 1. 이번 작업의 목적

공식 1.13.1 코드 위에 BANK-OM-001~007을 순서대로 다시 적용하고, 실제 충돌을
해결한 뒤 Manifest와 Git 이력이 일치하는지 검사했습니다. 이 결과는 소스 코드
수준의 업그레이드 검증이며 운영 배포 완료를 뜻하지 않습니다.

## 2. 적용 전에 확인한 영향

공식 1.13.0과 1.13.1 사이에서 834개 파일이 바뀌었습니다. 그중 Manifest의
`upgrade_watch.paths`와 겹치는 경로가 7개 BANK-OM 모두에서 발견되어
`APPROVAL` 결과가 나왔습니다.

`APPROVAL`은 실패가 아닙니다. 자동 적용 전에 담당자가 영향 경로를 확인해야
한다는 뜻입니다.

| BANK-OM | 공식 버전에서 바뀐 감시 경로 |
|---|---:|
| BANK-OM-001 | 22개 |
| BANK-OM-002 | 23개 |
| BANK-OM-003 | 19개 |
| BANK-OM-004 | 20개 |
| BANK-OM-005 | 1개 |
| BANK-OM-006 | 4개 |
| BANK-OM-007 | 1개 |

## 3. branch 생성과 커스터마이징 적용

```bash
git worktree add -b patch/om-1.13.1 \
  ../om-temp-1.13.1-upgrade 1.13.1-release
git -C ../om-temp-1.13.1-upgrade switch -c custom/om-1.13.1
```

`patch/om-1.13.1`은 공식 1.13.1 코드만 보관합니다. `custom/om-1.13.1`은
그 위에 BANK-OM 커밋을 적용한 검사 대상 branch입니다. 두 branch는 현재 로컬에만
있고 GitHub에는 아직 push하지 않았습니다.

## 4. 실제 충돌과 해결

| BANK-OM | 1.13.1 적용 commit | 실제 충돌 | 처리 |
|---|---|---|---|
| BANK-OM-001 | `83b1e0ac7d` | 번역 JSON 18개 | 각 파일의 BANK-OM 키 9개 |
| BANK-OM-002 | `8b368af0a2` | 번역 JSON 18개 | 각 파일의 BANK-OM 키 11개 |
| BANK-OM-003 | `e1d181d728` | 번역 JSON 18개 | 각 파일의 BANK-OM 키 5개 |
| BANK-OM-004 | `ed870cd63d` | 번역 JSON 18개 | 각 파일의 BANK-OM 키 9개 |
| BANK-OM-005 | `dfd3ad5e1c` | 충돌 없음 | 자동 적용 |
| BANK-OM-006 | `15b85814f5` | 충돌 없음 | 자동 적용 |
| BANK-OM-007 | `e7e4ba67b6 + dee330ebd5` | 충돌 없음 | 두 커밋을 순서대로 적용 |

001~004에서 표시된 18개는 매번 같은 번역 JSON 경로입니다. 따라서 서로 다른
72개 파일이 충돌한 것이 아니라, **18개 고유 파일에서 네 번의 충돌 사건**이
발생한 것입니다.

각 충돌 파일에서 세 값을 비교했습니다.

1. 공통 기준 JSON
2. 공식 1.13.1 JSON
3. 적용 중인 BANK-OM JSON

여기서 leaf key는 `label.instance-code`처럼 JSON에서 실제 값을 담는 마지막
항목 이름입니다. 공식 변경 키와 BANK-OM 변경 키가 하나도 겹치지 않은 경우에만
공식 1.13.1 JSON을 유지하고 BANK-OM 키를 추가했습니다. 같은 키를 양쪽이 모두 바꿨다면
자동 해결하지 않고 명령이 중단되도록 했습니다.

이 규칙은 OpenMetadata의 기존 기능이나 확정된 행내 정책이 아니라, 이번
업그레이드 연습에서 사용한 임시 규칙입니다. 아래에서 현재 구현과 정식 운영에
필요한 승인 절차를 구분해 설명합니다.

### 실제 Git 충돌을 다시 확인한 결과

BANK-OM-001의 1.13.0 commit `4df83b311f`를 공식 1.13.1에 다시 적용해
충돌을 재현했습니다.

```text
Auto-merging .../Entity.java
Auto-merging .../CollectionDAO.java
Auto-merging .../languages/ko-kr.json
CONFLICT (content): Merge conflict in .../languages/ko-kr.json
error: could not apply 4df83b311f... add InstanceCode customization

$ git diff --name-only --diff-filter=U | wc -l
18
```

`Entity.java`와 `CollectionDAO.java`는 자동으로 병합됐지만 번역 JSON 18개는
Git이 자동으로 결정하지 못해 중단됐습니다. 공식 1.13.1이 JSON 전체의 들여쓰기를
바꾸고 새 번역 항목도 추가한 상태에서 BANK-OM-001도 같은 JSON 객체에 번역 항목
9개를 추가했기 때문입니다.

대표 파일인 `ko-kr.json`에서 BANK-OM-001이 추가한 실제 항목은 다음과 같습니다.

```diff
+ "code-group": "Code Group"
+ "code-name": "Code Name"
+ "code-value": "Code Value"
+ "instance-code": "인스턴스 코드"
+ "instance-code-lowercase-plural": "인스턴스 코드"
+ "instance-code-plural": "인스턴스 코드"
+ "sort-order": "Sort Order"
+ "instance-code-description": "Manage common/reference codes..."
+ "instance-code-group-description": "The code group contains..."
```

해결 후에는 공식 1.13.1의 번역 항목과 형식을 유지하면서 위 9개 항목도 남아
있음을 Git에서 다시 확인했습니다. 이 결과가 BANK-OM-001의 새 1.13.1 commit
`83b1e0ac7d`에 기록됐습니다.

전체 재현 기록은
`harness/registrations/om-temp-1.13.1/conflict-replay-evidence.txt`에
보관했습니다.

### 이번에 사용한 해결 규칙과 승인 여부

이 해결 규칙은 OpenMetadata의 기존 기능이 아닙니다. **이번 업그레이드 연습을
위해 추가한 임시 운영 규칙과 도구**이며, 현재 은행의 정식 승인 정책으로 확정된
상태도 아닙니다.

현재 도구는 선택 화면이나 승인 요청을 제공하지 않습니다. 담당자가 아래 명령을
직접 실행하면, 동일한 JSON 항목이 겹치지 않을 때만 자동으로 파일을 작성합니다.
동일 항목이 겹치거나 JSON 이외의 파일에서 충돌하면 아무것도 결정하지 않고
중단합니다.

```bash
./.venv/bin/python \
  harness/tools/resolve_nonoverlapping_json_conflicts.py \
  --repo ../om-temp-1.13.1-upgrade
```

정식 운영에서는 다음 단계가 추가돼야 합니다.

1. 검사기가 충돌 예상 파일과 양쪽 변경 항목을 먼저 보여줍니다.
2. 담당자가 `겹치지 않는 항목만 자동 병합` 또는 `수동 해결`을 선택합니다.
3. 자동 병합을 선택한 경우 승인자·대상 commit·결과를 기록합니다.
4. 동일 항목이 겹치거나 JSON 이외의 충돌이면 `BLOCK`하고 수동 검토합니다.

## 5. 1.13.1 기준자료 다시 생성

1.13.0 자료를 그대로 검사하지 않고 `om-temp-1.13.1` 등록 폴더를 새로
만들었습니다. Manifest와 Contract의 업무 기준은 재사용하고, 공식 SHA·검사 대상
SHA·전체 diff·공용 경로·정책 파일은 1.13.1 기준으로 다시 생성했습니다.

| 자료 | 실제 결과 |
|---|---:|
| Manifest | 7개 |
| Registry | BANK-OM 7개 |
| Contract | 7개, 필수 Python test 9개 |
| 전체 변경 경로 | 111개 |
| 공용 경로 | 37개 |

## 6. 실제 검사 결과

| 검사명 | 무엇을 확인했나 | 결과 |
|---|---|---|
| 공식 기준 이력 포함 | 공식 1.13.1에서 시작했는지 | PASS |
| 커스터마이징 생존 | 핵심 파일과 Contract 연결이 남았는지 | PASS |
| 필수 테스트 코드 존재 | Python test 파일·함수가 있는지 | PASS |
| 커밋 작성 규칙 | 각 커밋에 BANK-OM ID가 하나인지 | PASS |
| ID 연결 규칙 | 미등록 ID와 잘못된 후속 커밋이 없는지 | PASS |
| 변경 범위 | Manifest에 등록된 파일만 바꿨는지 | PASS |
| 민감 경로 | 별도 정책을 위반하지 않았는지 | PASS |
| 커밋별 실제 경로 일치 | 실제 변경 파일과 Manifest가 같은지 | PASS |

## 7. Contract test와 build 환경 확인

로컬 1.13.1 코드를 연결해 Contract test 10개를 수집했습니다.

| 구분 | 결과 | 해석 |
|---|---:|---|
| 필수 Contract test | 2 PASS · 7 SKIP | Sybase·Tibero는 PASS, 서버·브라우저가 필요한 7개는 실행되지 않음 |
| 추가 소스 검사 | 1 PASS | 한글 입력 처리 코드가 남았는지 확인 |
| 실패 | 0 | 실행된 test에서는 실패가 없었음 |

`SKIP`은 성공이 아닙니다. `OPENMETADATA_BASE_URL`과 세 가지 브라우저 검사용
URL이 준비된 행내 환경에서 나머지 7개를 실행해야 합니다.

전체 build도 실행 전입니다. 현재 노트북에는 Java Runtime·Maven·Yarn과 UI
`node_modules`가 없어 build 명령을 시작할 수 없었습니다. 이는 코드가 build에
성공했다거나 실패했다는 결과가 아니라 **build 환경 준비가 필요하다**는 뜻입니다.

## 8. 현재 완료와 다음 단계

- 완료: 공식 1.13.1 branch 생성, BANK-OM-001~007 적용, JSON 충돌 해결
- 완료: 1.13.1 등록자료 생성 및 사전자료 검증 5종 PASS
- 완료: 소스 검사 8종 PASS
- 부분 완료: 소스로 실행 가능한 Contract 관련 test 3개 PASS, 환경이 필요한 7개 SKIP
- 미완료: OpenMetadata 전체 build 환경 준비와 실제 build
- 미완료: 기능 담당자 지정과 배포 승인
- 미완료: GitHub push와 검증 tag 생성

다음 단계는 Java·Maven·Yarn과 행내 test URL을 준비해 build와 남은 Contract
test를 수행한 뒤, 실제 Git 화면·터미널·검사 결과를 캡처해 시연 문서에
추가하는 것입니다.
