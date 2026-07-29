# Codex 작업 인수인계

> 갱신 기준: 2026-07-29 10:49 KST
> 거버넌스 저장소: `easyseop/openmetadata-test`
> 작업 브랜치: `codex/strict-manifest-gates`
> 문서 묶음 작성 전 기준 commit: `0a6d009107a18e69a2150388442adffb6332f08c`
> 제품 코드 상태: `easyseop/OpenMetadata` commit
> `849ae756cd238f218b5e3a6c795a392305cb32ee`
> 공유문서·스킬 최초 로컬 commit: `becb18e` (이후 보강은 현재 브랜치의 `git log`로 확인)
> 원격 push: `easyseop/openmetadata-test`의 `codex/strict-manifest-gates`
> branch는 이번 공유문서·스킬·검사자료 배치까지 push 완료. 사용자가 만든
> `easyseop/OM_TEMP`에는 1.13.0 시연용 제품 코드 두 branch를 push함

이 문서는 다른 노트북이나 새 작업에서 바로 이어가기 위한 현재 정본이다.
과거 Claude 작업의 상세 기록은
[`CLAUDE_REVIEW_HANDOFF.md`](CLAUDE_REVIEW_HANDOFF.md)에 남아 있지만, 공유문서
1차·2차·3차·4차 작업은 이 문서와
[`SHARING_ARTIFACT_REQUIREMENTS.md`](SHARING_ARTIFACT_REQUIREMENTS.md)를 먼저
따른다.

## 0. 최신 공유문서 상태

공유문서의 **읽는 순서**를 다음과 같이 확정했다.

1. 목적과 브랜치 전략
2. 검사기 원리
3. 검사 전 사전환경 설정
4. 검사 결과와 책임자 판단
5. 실제 `1.13.0 → 1.13.1` 업그레이드

이 순서는 실제 명령 실행 순서와 다르다. 처음 보는 독자는 검사기가 무엇을
판단하는지 먼저 알아야 Manifest·Registry·Contracts를 왜 준비하는지 이해할 수
있으므로 검사기 원리를 먼저 읽는다. 실제 작업에서는 3번의 사전환경 설정을
완료한 뒤 검사기를 실행한다. 이 차이를 3번 문서 첫 화면에 명시했다.

다섯 페이지 모두 위·아래에 이전·다음 이동을 넣었다. 1차·2차·4차의
`visualize` 미리보기는 본문이 iframe 안에 있으므로, `file://`로 열었을 때도
동작하도록 이동 버튼을 iframe 바깥 preview 문서에 생성한다. fragment를 다시
렌더링한 직후 다음 명령을 실행한다.

```bash
./.venv/bin/python harness/tools/enable_guide_navigation.py
```

`enable_guide_navigation.py`는 여러 번 실행해도 기존 바깥 이동 버튼을 지우고
한 번만 다시 생성한다. 2026-07-29 KST에 브라우저에서
`1 → 2 → 3 → 4 → 5` 이동과 `5 → 4` 이전 이동을 실제 클릭해 확인했다.

다섯 페이지의 일반 본문 폰트는 다음 하나의 규칙으로 통일했다. 코드 블록은
가독성을 위해 기존 고정폭 글꼴을 유지한다.

```css
font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo",
  "Noto Sans KR", "Segoe UI", sans-serif;
```

브라우저 계산값도 다섯 페이지에서 동일한 것을 확인했다. 생성형 페이지인 3번과
5번은 각 renderer의 원본 CSS에, iframe형 페이지인 1번·2번·4번은 fragment
본문 루트와 바깥 이동 영역에 같은 규칙을 넣었다.

이번 배치에서 추가로 반영한 내용은 다음과 같다.

- 1차 branch SVG는 왼쪽 `patch` branch의 공식 코드와 오른쪽의 BANK-OM
  commit이 중앙의 새 `custom` branch로 합류하는 구조를 먼저 보여준 뒤,
  `적용 완료 commit → 검사 → 검증 tag·배포`로 이어지는 Cycle로 구성했다.
- 두 입력 화살표 설명은 별도 라벨 안에 넣고, 합류 지점은 긴 설명이 들어가는
  둥근 사각형으로 바꿨다. 충돌 해결 복귀선은 설명 아래쪽으로 우회시켜 화살표와
  글자 겹침을 제거했다.
- 실제 Git 충돌은 BANK-OM commit이 새 `custom` branch에 합류하는 단계에서
  발생한다고 표시했다. 충돌
  해결 commit을 `custom` branch에 남기고 다시 재적용하는 loop와, 적용 완료 후
  검사 BLOCK 때문에 `custom`을 보완하고 재검사하는 loop를 서로 분리했다.
- `custom` branch는 `patch`의 공식 코드에서 시작하고, 사전에 관리한 BANK-OM
  ID별 commit이 오른쪽 입력으로 들어와 순서대로 재적용된다는 관계를 별도
  화살표로 표시했다.
- 충돌 해결 commit은 현재 버전의 `custom` branch에 기록하고 재검사한다.
  `patch` branch에는 공식 원본만 유지한다.
- 검사 통과 시 `verified/...` tag로 배포 검토 대상 commit을 고정한다. 다음
  공식 버전에는 새 `patch`·`custom` branch를 만들고 BANK-OM 변경을 다시
  적용한다.
- 2차에는 각 검사기의 입력, 판단 방법, 출력, 실패 조건을 한 표로 정리했다.
- 3번 사전환경 설정에는 Manifest·Registry·Contracts·공용 파일 소유정보·전체
  변경 목록·선택적 Patch-lock의 필드 의미와 실제 사용 검사를 정리했다.
- 4번 결과 문서는 기존 `easyseop/OpenMetadata`의 `849ae756...` 제품 후보를
  검사했던 과거 결과임을 명시하고, 5번 OM_TEMP 업그레이드와 구분했다.
- 5번에는 `cherry-pick`의 사용 시점, 실제 Git 충돌 표식, 해결 전후 diff,
  JSON 충돌 해결 도구의 제한, 담당자와 검사기의 역할을 구분해 설명했다.

## 1. 저장소와 브랜치

| 구분 | 저장소와 브랜치 | 의미 |
|---|---|---|
| 행내 배포용 OpenMetadata 소스 | `easyseop/OpenMetadata` 브랜치 `codex/bank-vendor-1.13.1-rebuild` | 공식 원본 위에 BANK-OM-001~011 코드가 적용된 검토 상태. 008~011 ID는 사용자 확정 전 |
| 현재 로컬 제품 검토 브랜치 | `codex/strict-gate-validation` | remote 이름이 `product`인 위 제품 브랜치를 추적하며 검사에 사용 |
| 변경관리·검사 저장소 | `easyseop/openmetadata-test` 브랜치 `codex/strict-manifest-gates` | BANK-OM 변경관리표, 검사기, 테스트, 공유문서와 인수인계를 관리 |
| 공식 원본 | `open-metadata/OpenMetadata` `1.13.1-release` commit `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9` | 현재 커스터마이징 적용 기준 |
| 업그레이드 시연 제품 저장소 | `easyseop/OM_TEMP` | Manifest 없이 1.13.0 공식 코드와 001~007 재구현 코드까지만 준비 |

`easyseop/OpenMetadata`의 기본 브랜치에 행내 커스터마이징이 보이지 않는 것은
이상 상태가 아니다. 현재 커스터마이징은 위의 별도 제품 브랜치에 있으며,
BANK-OM 변경관리 정보와 검사기는 `easyseop/openmetadata-test`에 있다.

## 2. 공유문서 진행 상태

| 페이지 | 현재 상태 | 저장된 파일 | 남은 일 |
|---|---|---|---|
| 1 · 목적과 브랜치 전략 | 목적·두 branch 원칙과 버전 반복 흐름을 같은 SVG에서 설명하는 검토본 | `docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-fragment.html`, `openmetadata-phase1-sharing-preview.html` | 최종 부서 공유 전 문장과 도식 최종 승인 |
| 2 · 검사기 원리 | 검사기별 입력·판단·출력·실패 조건과 예외를 설명하는 검토본 | `docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-fragment.html`, `openmetadata-phase2-verifier-table-preview.html` | 최종 부서 공유 전 검사명·한계 최종 승인 |
| 3 · 검사 전 사전환경 설정 | 실제 OM_TEMP commit 캡처와 Manifest 7개, 검사 기준자료의 의미·시점·사용 예시를 연결한 검토본 | `docs/00-사용가이드/OM_TEMP_커밋별_Manifest_등록_가이드_미리보기.html` | 담당자 지정과 선택적 Patch-lock 여부 확정 |
| 4 · 검사 결과와 책임자 판단 | 기존 `easyseop/OpenMetadata` 후보 `849ae756...`의 검사 결과를 설명하는 검토본 | `docs/00-사용가이드/공유문서/openmetadata-phase3-demo-fragment.html`, `openmetadata-phase3-demo-preview.html` | OM_TEMP 결과와 혼동 없는지 최종 승인 |
| 5 · 실제 업그레이드 | 실제 OM_TEMP `1.13.0 → 1.13.1` 적용·충돌·해결·검사 결과를 설명하는 검토본 | `docs/00-사용가이드/OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드_미리보기.html` | 환경 test, 담당자 승인, 검증 tag와 배포 화면 추가 |

2026-07-29 KST에 1차·2차 문서의 확정된 본문은 유지하고, 1.13.1 업그레이드
가이드와 같은 파란색 헤더·흰색 카드·표·펼치기 디자인을 적용했다. 수정된
fragment와 standalone preview를 함께 다시 생성했으며, 두 화면 모두 본문 폭
1100px에서 가로 넘침이 없음을 확인했다.

같은 날 다섯 페이지의 일반 본문 폰트 스택과 렌더링 품질을 통일했다.
1차·2차·4차 미리보기의 이전·다음 버튼은 iframe 내부가 아니라 바깥 preview에
배치해 `file://`와 로컬 HTTP 미리보기에서 같은 상대경로를 사용하도록 고쳤다.

4차 업그레이드 시연 범위는 `1.13.0→1.13.1` 한 구간으로 좁혔다. 먼저 공식
1.13.0 구조에 맞춰 BANK-OM-001~007을 재구현하고 검사한 뒤, 그 commit을 공식
1.13.1 기준에 다시 적용해 충돌·보완·재검사 과정을 보여준다. 1.12.x 구간은
1.13.1 기준 commit의 역방향 적용으로 충돌이 과장되므로 이번 시연에서 제외한다.

### OM_TEMP 현재 구성

2026-07-29 KST에 다음 두 브랜치를 원격에 push했다.

| 브랜치 | 원격 SHA | 내용 |
|---|---|---|
| `patch/om-1.13.0` | `2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50` | 공식 `1.13.0-release` commit `f329dd4…`의 코드 트리와 동일한 독립 스냅샷 |
| `custom/om-1.13.0` | `7d19c8952612e77467b0a80d6287170d814f1de1` | 공식 1.13.0 전체 코드에 1.13.0 구조로 재구성한 BANK-OM-001~007과 007 후속 commit을 순서대로 적용 |

OM_TEMP는 전체 OpenMetadata 과거 Git 이력을 복사하지 않았다. 첫 push에서 전체
이력 전송이 GitHub HTTP 500으로 실패해, 공식 1.13.0 시점의 파일 전체를 독립
기준 commit으로 만들고 원본 tag·commit·Git tree 값을 commit 본문에 기록했다.
Git tree는 해당 commit의 전체 파일 내용을 식별하는 값이다. 공식 1.13.0 tree와
OM_TEMP patch tree가
`da56c24d61a98dc4ed1001800c80866a13bc1645`로 동일한 것을 확인했다.

`custom/om-1.13.0`에는 BANK-OM 커밋 8개가 있다. 001~006은 각각 한 commit이고,
007은 최초 적용과 후속 보완 두 commit이다. 008~011은 넣지 않았다. 두 브랜치
사이 실제 변경 파일은 111개다.

2026-07-29 KST에 실제 OM_TEMP commit을 기준으로 다음 작업을 추가했다.

- `harness/registrations/om-temp-1.13.0/manifests/`에 BANK-OM-001~007
  Manifest 초안 7개 생성
- `generate_manifest_drafts.py`로 각 commit의 전체 변경 파일을 다시 추출할 수
  있도록 자동화
- BANK-OM-007의 최초 8개 경로와 후속 commit의 추가 2개 경로를 분리 등록
- 7개 Manifest의 스키마·기본 의미 검사와 실제 Git diff 일치 확인 통과
- 각 commit의 실제 GitHub 캡처, 설명용 강조본, BANK-OM-005 전체 diff 캡처,
  Manifest 전체를 ID별 펼치기로 구성
- 같은 미리보기에 `1. Manifest 등록 → 2. 검사 기준자료 등록 → 3. 로컬 검사
  대상 연결`을 추가하고 화면 제목을 `OM_TEMP 검사 전 사전환경 설정 가이드`로
  변경
- Registry·Contracts·공용 파일 소유정보·111개 전체 변경 목록·선택
  Patch-lock을 각각 `의미 → 만드는 시점 → 실제 사용 → 예시 → 검사 결과`로
  설명
- `.agents/skills/clarity-preflight-review/SKILL.md`에도 위 설명 순서를
  필수 검토 기준으로 추가

Registry·Contracts·공용 파일 소유정보·111개 전체 변경 목록은 이후 실제
생성했고, 등록자료 검사 5종과 소스 검사 8종이 PASS했다. `1.13.1` 업그레이드도
로컬에서 수행했다. 아직 남은 일은 환경이 필요한 Contract test 7개, 전체 build,
담당자 지정, `verified/...` tag 생성과 배포 승인이다. Patch-lock은
patch-replay를 선택할 때만 생성한다. `candidate/...` branch는 설계에서
제외했다.

Manifest 작성 절차는
[`OM_TEMP_Manifest_작성_단계별_가이드.md`](../00-사용가이드/OM_TEMP_Manifest_작성_단계별_가이드.md)에
정리했다. 각 commit 캡처와 실제 Manifest 초안 전체는
[`OM_TEMP_커밋별_Manifest_등록_가이드.md`](../00-사용가이드/OM_TEMP_커밋별_Manifest_등록_가이드.md),
화면 미리보기는
[`OM_TEMP_커밋별_Manifest_등록_가이드_미리보기.html`](../00-사용가이드/OM_TEMP_커밋별_Manifest_등록_가이드_미리보기.html)에
있다. 기존 `harness/registrations/kb-openmetadata/`는 1.13.1 기준이므로
수정하지 않았고, 1.13.0 초안은 별도 등록 묶음으로 생성했다.

향후 태그는 `patch/om-1.13.0` snapshot에
`baseline/om-1.13.0`, 검사에 사용한 정확한 `custom/om-1.13.0` SHA에
`verified/om-1.13.0-bank.1` 형식으로 붙인다. 현재 두 태그는 아직 만들지
않았다. 검증 태그는 Manifest·Git 범위·필수 test와 정해진 gate를 통과한 뒤에만
만들며, 그 자체가 행내 운영 배포 완료를 뜻하지 않는다고 기록한다.

검토본을 승인본이라고 표시하지 않는다. 사용자가 명시적으로 승인한 범위와 아직
검토 중인 범위를 문서와 화면에서 구분한다.

## 3. 1차에서 확정한 설계 설명

- 공식 OpenMetadata 저장소의 새 버전은 패치 브랜치로 가져온다.
- 행내 커스터마이징 브랜치는 BANK-OM ID별 커밋을 유지한다.
- 버전별 장기 작업 브랜치는 `patch/om-<version>`과
  `custom/om-<version>` 두 개만 사용한다.
- 별도의 장기 `candidate/...` 브랜치는 만들지 않는다. 검사 대상은
  `custom/...` 브랜치의 Git commit SHA와 digest로 고정하고, 통과한 상태는
  `verified/om-<version>-bank.<revision>` tag로 보존한다.
- 4차 시연의 임시 upgrade branch는 충돌 재현을 위한 작업 공간이며 결과와
  검증 tag를 보존한 뒤 삭제할 수 있다. 검사기 코드에서 `candidate`는 Git
  브랜치 이름이 아니라 검사 대상 코드 상태를 뜻한다.
- 새 공식 버전에 커스터마이징을 적용한 뒤 검사기를 실행하고, 필수 검사가 끝난
  경우에만 배포 검토로 넘어간다.
- BANK-OM ID는 사람이 정해진 양식으로 발급한다. LLM이 임의로 번호를 결정하지
  않는다.
- 커밋 메시지에는 본문과 별도로 `Customization-ID: BANK-OM-nnn` 항목을 넣는다.
  BANK-OM ID와 Git commit SHA는 서로 다른 값이다.
- `allowed_changed_paths`는 해당 BANK-OM ID의 커밋이 실제로 변경할 수 있는
  전체 파일 목록이다.
- `required_changed_paths`는 그중 최종 코드에서 실제 변경이 확인되지 않으면
  해당 커스터마이징이 빠졌다고 판단할 핵심 파일 목록이다.
- `upgrade_watch`는 행내에서 직접 수정하지 않았더라도 커스터마이징이 의존하기
  때문에 공식 업그레이드 때 변경 여부를 다시 확인할 파일·설정·라이브러리 목록이다.
- 폴더 전체를 넓게 허용하지 않고 현재 확인된 파일을 개별 경로로 등록하는 것이
  기본 원칙이다.

등록과 운영 방법의 정본은
[`docs/02-설계/bank_om_registration_policy.md`](../02-설계/bank_om_registration_policy.md)다.

## 4. 2차에서 확인한 검사기 원리와 한계

관련 검사기 구현 코드와 단위 테스트를 다시 확인했다. 관련 단위 테스트는
통과했지만, 다음 예외 가능성은 남아 있다.

Git 커밋과 파일 변경을 확인하는 T25-R·T25·T26·T30·T31·T40·T41·T42·T43·T93은
Java·TypeScript·Python·JSON·YAML·SQL 등 파일 종류와 관계없이 사용할 수 있다.
공식 원본 이후 각 커밋에서 바뀐 파일 경로와 공식 원본 대비 최종 파일 상태를
확인하므로 프론트엔드와 백엔드에 같은 변경관리 규칙을 적용할 수 있다. 그러나
이 공통 계층은 Java·TypeScript 등 파일 내부 코드의 의미나 실행 동작을
언어에 관계없이 해석하지는 않는다. T60-I는 현재 Python pytest 코드만 확인하고
T63은 TypeScript 전용이며, T61·T62는 Python pytest 실행 연결을 사용한다.
Java JUnit·TypeScript Jest를 직접 등록하고 실행하려면 언어·도구별 연결을
추가해야 한다.

정리하면 “모든 변경 파일이 검사 대상이 되는가?”에는 예라고 답할 수 있지만,
“모든 언어의 코드 동작을 현재 검사기가 직접 이해하고 테스트하는가?”에는
아니라고 답해야 한다. 저장소 경로 분류와 BANK-OM Manifest에 등록하지 않은
변경 경로는 공통 변경관리 검사에서 통과시키지 않는다.

| 검사 | 확인된 핵심 원리 | 운영 전에 필요한 보완 |
|---|---|---|
| T25-R | JSON은 값으로 비교하고, 나머지 파일은 Git 차이가 없어야 한다. Java 파일의 빈 줄 하나도 차이로 판단한다. | 서식 차이를 자동 통과시키지 말고 별도 표시 후 담당자 검토 |
| T25 | Git 포함 관계로 공식 commit이 행내 코드 이력에 있는지 확인한다. | 충돌 해결과 실제 동작은 별도 검사 |
| T26 | 모든 활성 BANK-OM ID의 필수 파일·계약·테스트 연결을 확인한다. | 파일 존재만으로 기능 정상이라고 판단하지 않음 |
| T60-I | `contracts.yaml`에 등록한 Python pytest 파일과 함수가 실제로 존재하는지 AST로 확인한다. 현재 9개 테스트는 API·검색·화면·한글 입력·연결 스키마를 다룬다. | Java JUnit·TypeScript Jest와 Manifest의 `direct_tests` 존재 확인을 추가하고, 테스트 품질과 실행 성공은 T61·T62에서 확인 |
| T30 | 공식 원본 이후의 모든 Git 커밋과 `Customization-ID:` 항목을 읽는다. | 하나의 ID에 다른 목적을 섞지 않도록 리뷰 |
| T31 | 여러 커밋 사용 허용, 연속성, 폐기 ID, 선행 관계 순환을 확인한다. | 누락된 업무 선행 관계는 사람이 등록 |
| T40 | 커밋별 전체 변경 파일과 최종 필수 변경 파일을 양방향으로 비교한다. | 파일 내부의 잘못된 줄은 코드 리뷰와 테스트로 확인 |
| T41 | AST가 아니라 민감 경로 규칙과 실제 변경 파일을 비교한다. | 정적 보안 분석과 보안 담당자 리뷰 추가 |
| T42 | 새 공식 버전의 Git 차이와 `upgrade_watch`를 비교한다. | 감시 대상 누락을 줄이는 자동 제안과 담당자 확인 |
| T43 | 커스터마이징 수·변경 줄·공유 파일 수·충돌률을 정책 한도와 비교한다. | 충돌률을 명령 인자가 아니라 실제 재적용 결과에서 자동 계산 |
| T93 | ID별 실제 변경 파일과 등록 파일을 비교하고, 새 공식 버전에서 감시 규칙이 유효한지 확인한다. | 민감 경로 규칙도 노후화 검사에 포함 |
| T61 | 커스터마이징이 없는 버전에서 필수 테스트가 실패하는지 확인한다. | 누락 때문에 실패했는지 오류 종류와 메시지까지 확인 |
| T62 | 제품 commit SHA, 배포 파일 digest, 검사기와 테스트 버전을 결과에 연결한다. | DB·검색엔진·설정 등 실행 환경 digest와 실행 시스템 서명 추가 |
| T63 | 공식 원본과 행내 코드의 TypeScript 파일 경로·오류 코드 발생 횟수를 비교한다. | Node·Yarn·전체 로그 digest를 검사 결과에 강제 연결 |
| T90 | 정해진 업그레이드 12단계 결과 문서와 코드·배포 파일·T62 결과의 연결을 확인한다. | 각 단계를 실제로 실행한 로그와 서명 검증 |
| T91 | 승인한 commit·이미지·Helm·검사 결과 digest와 실제 배포값을 비교한다. | 외부망에서 내부망으로 옮긴 뒤 별도 서명·해시 재검증 |

## 5. 현재 확인된 실제 상태

- 현재 제품 코드 commit: `849ae756cd238f218b5e3a6c795a392305cb32ee`
- 공식 원본 commit: `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9`
- 현재 제품 코드에는 `BANK-OM-001`부터 `BANK-OM-011`까지의 commit이 있다.
  008~011은 이전 Codex 작업에서 기술 보완용으로 추가한 임시 ID이므로 사용자가
  정식 커스터마이징 ID로 확정하기 전에는 승인된 11개라고 표현하지 않는다.
- 소스 검사: T25·T26·T60-I·T30·T31·T40·T41·T93 통과
- T60-I: 등록한 필수 Python 테스트 함수 9개 확인
- T42: 같은 버전을 양쪽에 넣은 연결 확인만 했으며 실제 다음 공식 버전
  업그레이드 증거는 없음
- T43: 실제 업그레이드 충돌률이 아니라 연결 확인용 입력을 사용했으므로 실제
  업그레이드 승인 근거가 아님
- T61: 소스에서 실행 가능한 2개만 확인했으며 전체 5개 중 나머지 3개는 행내
  배포 환경이 필요
- T62: 실행기와 사전 환경 점검은 구현했지만 실제 행내 실행 결과 없음
- T63: 새로운 파일 경로·오류 코드 조합은 없지만 공식 원본부터 있던 오류가
  남아 있어 담당자 승인 필요
- T90·T91: 실제 행내 업그레이드와 배포 승격을 실행하지 않음
- 결론: 소스 커스터마이징 관리 검사는 진행됐지만 운영 배포 승인 상태는 아님
- 3차 초안 작성 시 소스 검사 명령을 다시 실행해 T25·T26·T60-I·T30·T31·
  T40·T41·T93 통과를 확인했다. 이 실행은 다음 공식 버전 업그레이드나 행내
  운영 환경 검사가 아니다.

## 6. 검증 명령

소스 검사:

```bash
./.venv/bin/python harness/registrations/kb-openmetadata/run_source_candidate_gates.py \
  --repo ../review-kb-openmetadata \
  --harness harness \
  --registration harness/registrations/kb-openmetadata \
  --layout harness/policies/repository-layout.yaml \
  --sensitive-zones harness/policies/sensitive-zones.yaml
```

이번 2차 검토에서 다시 실행한 관련 단위 테스트:

```bash
./.venv/bin/pytest -q \
  harness/tests/test_ancestry.py \
  harness/tests/test_contracts.py \
  harness/tests/test_debt.py \
  harness/tests/test_drift.py \
  harness/tests/test_invariants.py \
  harness/tests/test_patchkill.py \
  harness/tests/test_policy_drift.py \
  harness/tests/test_release.py \
  harness/tests/test_survival.py \
  harness/tests/test_testruns.py \
  harness/tests/test_tsc_baseline.py \
  harness/tests/test_upgrade_run.py \
  harness/tests/test_upgrade_watch.py \
  harness/tests/test_vendor_rebuild.py \
  harness/tests/test_zones.py
```

관련 단위 테스트는 통과했으며, 환경이 필요한 테스트는 skip으로 남았다.

### OM_TEMP 1.13.0 등록 및 소스 검사

2026-07-28 기준으로 다음 실제 등록자료를
`harness/registrations/om-temp-1.13.0/`에 생성했다.

- `customization-registry.yaml`: BANK-OM-001~007 7개, 담당자 상태는 `pending`
- `contracts.yaml`: Contract 7개, 필수 Python pytest selector 9개
- `shared-path-owners.yaml`: 여러 ID가 함께 변경한 경로 37개
- `source-diff-paths.txt`: 공식 1.13.0 대비 전체 변경 경로 111개
- `repository-layout.yaml`, `sensitive-zones.yaml`: 공식 1.13.0 SHA에 고정한 경로 정책
- `registration-validation-results.json`: 사전자료 검증 5개 PASS
- `source-gate-results.json`: 소스 검사 8개 PASS

원격 OM_TEMP는 공식 1.13.0 파일 tree를 독립 commit으로 가져와 공식 계보가
없다. 검사에는 공식 `f329dd4a7e...`에서 시작해 같은 BANK-OM 변경을 순서대로
적용한 로컬 `custom/om-1.13.0` commit `63820f88eb...`을 사용했다. 이 로컬
후보와 원격 custom commit `7d19c89526...`의 최종 tree는
`9495a31c99...`로 같다.

사전자료 검증:

```bash
./.venv/bin/python \
  harness/registrations/om-temp-1.13.0/validate_registration_bundle.py \
  --repo ../om-temp-1.13.0-custom \
  --output harness/registrations/om-temp-1.13.0/registration-validation-results.json
```

소스 검사:

```bash
./.venv/bin/python harness/run_source_candidate_gates.py \
  --repo ../om-temp-1.13.0-custom \
  --harness harness \
  --registration harness/registrations/om-temp-1.13.0 \
  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \
  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \
  --output harness/registrations/om-temp-1.13.0/source-gate-results.json
```

소스 검사 PASS는 코드 구조와 변경 이력이 등록자료와 일치한다는 뜻이다.
OpenMetadata 전체 build, Contract test 실행, 담당자 지정, 1.13.1 업그레이드,
운영 배포 승인은 아직 수행하지 않았다.

### OM_TEMP 1.13.0 → 1.13.1 실제 업그레이드

1.13.1 업그레이드는 2026-07-28 로컬에서 실제 수행했다.

- 공식 기준: `1.13.1-release`
  (`afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9`)
- 공식 코드 branch: `patch/om-1.13.1`
- 커스터마이징 적용 branch: `custom/om-1.13.1`
- 최종 검사 대상 commit:
  `dee330ebd5abfe33e1ac61e1ca31879746a1b423`
- 공식 1.13.0→1.13.1 변경: 834개 파일
- `upgrade_watch` 결과: BANK-OM-001~007 모두 영향 경로가 있어 `approval`
- 실제 충돌: BANK-OM-001~004 적용 시 같은 번역 JSON 18개에서 반복 발생
- 충돌 해결: 공식 변경 leaf key와 BANK-OM leaf key가 겹치지 않을 때만
  공식 JSON에 BANK-OM 키를 추가. 겹치면 자동 중단하는 도구 사용
- 위 JSON 해결 도구는 OpenMetadata의 기존 기능이나 확정된 행내 정책이 아니다.
  이번 업그레이드 연습에서 추가했으며 현재는 선택 화면·승인자 기록 없이
  담당자가 명령을 직접 실행한다. 동일 항목 겹침과 JSON 외 충돌은 자동 해결하지
  않고 중단한다.
- BANK-OM-005~007: 충돌 없이 적용
- 1.13.1 등록자료: Manifest 7개, Contract 7개, test selector 9개,
  전체 경로 111개, 공용 경로 37개
- 1.13.1 사전자료 검증 5종 PASS
- 1.13.1 소스 검사 8종 PASS
- Contract test 수집 10개: 필수 Contract test 2개 PASS·7개 SKIP,
  추가 한글 입력 소스 검사 1개 PASS, 실패 0개
- SKIP 사유: `OPENMETADATA_BASE_URL`, `BANK_COLUMN_UI_URL`,
  `BANK_DATA_ASSERTIONS_URL`, `BANK_IME_EDITOR_URL` 미설정
- 전체 build 사전확인: 현재 노트북에 Java Runtime·Maven·Yarn·UI
  `node_modules`가 없어 실행 전(`environment_pending`)

상세 결과:

- `harness/registrations/om-temp-1.13.1/upgrade-watch-results.json`
- `harness/registrations/om-temp-1.13.1/upgrade-application-results.json`
- `harness/registrations/om-temp-1.13.1/conflict-replay-evidence.txt`
- `harness/registrations/om-temp-1.13.1/registration-validation-results.json`
- `harness/registrations/om-temp-1.13.1/source-gate-results.json`
- `harness/registrations/om-temp-1.13.1/contract-test-results.json`
- `harness/registrations/om-temp-1.13.1/build-preflight-results.json`
- `docs/00-사용가이드/OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드_미리보기.html`

두 1.13.1 branch는 로컬에만 만들었고 아직 GitHub에 push하지 않았다. 전체
build, 환경이 필요한 Contract test 7개, 담당자 지정, 검증 tag와 배포 승인은
남아 있다. SKIP은 PASS로 계산하지 않는다.

2026-07-29 KST에 BANK-OM-001의 원래 1.13.0 commit `4df83b311f`를 공식
1.13.1에 다시 적용해 충돌을 재현했다. Git에서 `Entity.java`와
`CollectionDAO.java`는 자동 병합됐고 번역 JSON 18개는 `UU`로 중단되는 것을
확인했다. 가이드에는 실제 Git 출력, `ko-kr.json`의 BANK-OM 추가 항목 9개,
해결 결과 commit `83b1e0ac7d`, 현재 구현과 정식 승인 절차의 차이를 추가했다.
정식 운영 전 추가 개발 대상은 dry-run 비교, 자동 병합/수동 해결 선택,
승인자·대상 commit·결과 기록, `BLOCK` 결과 연결이다.

같은 시점에 `capture_conflict_replay.py`로 BANK-OM-001 충돌을 다시 재현하고
다음 증거를 `harness/registrations/om-temp-1.13.1/conflict-evidence/`에
보관했다.

- `BANK-OM-001_ko-kr_full_conflict.txt`: Git 충돌 표식을 포함한 실제
  `ko-kr.json` 6,614줄
- `BANK-OM-001_ko-kr_resolution.diff`: 공식 1.13.1과 해결 commit의 실제
  43줄 diff
- `BANK-OM-001_ko-kr_resolved.json`: 해결 후 전체 JSON
- `BANK-OM-001_ko-kr_capture.json`: BANK-OM ID, source commit, target tag,
  해결 commit과 충돌 경로 18개

업그레이드 가이드에는 다음 설명을 추가했다.

- 업그레이드 전 영향 확인은 `upgrade-watch`(T42)가 담당하고, 이번 watch
  자료는 Git 변경 경로 자동 등록과 담당자 의존 경로 수동 등록을 함께 쓰는
  부분 자동 방식
- 검사 대상 `dee330ebd5...`는 공식 commit이나 BANK-OM ID가 아니라
  `custom/om-1.13.1`의 최종 Git commit SHA
- 번역 항목 이름의 교집합은 0개였지만 공식 JSON의 전체 서식 변경과 BANK-OM
  항목 추가가 같은 객체에 있어 Git의 줄 단위 충돌이 발생한 이유
- 현재 Git 원문에는 source commit SHA만 나오며 BANK-OM ID 자동 표시는
  추가 개발 대상
- 현재 해결 도구에는 선택·승인자 기록이 없고, 정식 운영에는 dry-run plan,
  담당자 선택, 승인 파일 검증, ID 포함 로그, BLOCK과 재검사 연결이 필요
- 현재 검사기로 증명한 소스 수준 범위와 build·실제 업무 동작·사람 승인·배포
  안전성처럼 아직 증명하지 못한 범위

HTML 다시 생성:

```bash
python3 /Users/seop/.codex/plugins/cache/openai-bundled/visualize/1.0.15/skills/visualize/scripts/render.py \
  docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-fragment.html \
  docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-preview.html

python3 /Users/seop/.codex/plugins/cache/openai-bundled/visualize/1.0.15/skills/visualize/scripts/render.py \
  docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-fragment.html \
  docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-preview.html

python3 /Users/seop/.codex/plugins/cache/openai-bundled/visualize/1.0.15/skills/visualize/scripts/render.py \
  docs/00-사용가이드/공유문서/openmetadata-phase3-demo-fragment.html \
  docs/00-사용가이드/공유문서/openmetadata-phase3-demo-preview.html

./.venv/bin/python harness/tools/enable_guide_navigation.py
```

다른 노트북에서 위 절대 경로가 다르면 설치된 `visualize` 스킬의
`scripts/render.py` 경로를 찾아 바꾼다.

## 7. 다른 노트북에서 재개하는 순서

1. `easyseop/openmetadata-test`의 `codex/strict-manifest-gates` 브랜치를 받는다.
2. 이 문서와 `SHARING_ARTIFACT_REQUIREMENTS.md`를 읽는다.
3. `.agents/skills/clarity-preflight-review/SKILL.md`를 읽고 이후 모든 공유문서
   검토에 적용한다.
4. 공유문서는 `목적과 브랜치 전략 → 검사기 원리 → 검사 전 사전환경 설정 →
   검사 결과와 책임자 판단 → 실제 업그레이드` 순서로 읽는다.
5. `OM_TEMP_커밋별_Manifest_등록_가이드_미리보기.html`에서 Manifest 등록,
   기준자료 생성, 로컬 연결, 실제 소스 검사 4단계를 확인한다. 파일명은 유지했지만
   화면 제목은 `OM_TEMP 검사 전 사전환경 설정 가이드`다. 실제 명령 실행에서는
   이 사전환경 설정을 검사기보다 먼저 완료한다.
6. 담당 부서가 Registry의 `UNASSIGNED` 7개를 실제 담당자로 바꾸기 전에는
   배포 준비 완료로 표시하지 않는다.
7. Patch-lock은 vendor-merge 소스 검사의 필수가 아니다. patch-replay·복구·
   재현 시연을 선택할 때만 만든다.
8. `custom/om-1.13.1`에서 가능한 build와 Contract test를 실행하고 결과를
   1.13.1 가이드에 추가한다.
9. 다섯 HTML에 남은 사용자 피드백을 반영한다.
10. 환경 test·담당자 승인·검증 tag·배포 결과 화면을 5번 페이지에 추가한다.
11. 다섯 페이지의 중복과 용어를 다시 검토한다.
12. fragment를 다시 렌더링했다면 `harness/tools/enable_guide_navigation.py`를
   실행해 iframe 바깥의 이전·다음 이동 영역을 다시 생성한다.
13. 작업 완료 후 이 문서의 상태·검증·다음 단계를 갱신하고 같은 브랜치에
   커밋·푸시한다.

## 8. 작업 시 주의

- `docs/00-사용가이드/.비개발자_시연_가이드.md.swp`는 사용자의 편집기 임시
  파일이다. 수정하거나 stage하지 않는다.
- 비밀값, 인증 토큰, 행내 URL과 실제 데이터는 문서나 Git에 넣지 않는다.
- 공유문서 묶음은 로컬 commit으로 계속 저장한다. 최초 묶음은 `becb18e`이며
  최신 보강 commit은 현재 브랜치의 `git log`로 확인한다. 원격
  `https://github.com/easyseop/openmetadata-test.git`에 행내 커스터마이징 구조를
  올려도 된다는 사용자의 명시적 확인을 받은 뒤 push한다.
- GitHub CLI 인증이 없더라도 기존 Git credential로 push가 가능한 경우가 있다.
  인증 오류가 나면 사용자가 해당 노트북에서 GitHub 로그인을 완료해야 한다.
- PR은 사용자가 요청하지 않으면 만들지 않는다.
