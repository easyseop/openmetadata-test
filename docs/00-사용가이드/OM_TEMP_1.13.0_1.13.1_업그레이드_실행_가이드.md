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

이 결과는 **공식 변경 영향 확인 검사(upgrade-watch, T42)**가 만들었습니다.
검사기는 Git으로 공식 1.13.0과 1.13.1 사이에서 바뀐 834개 경로를 구하고,
각 BANK-OM Manifest의 `upgrade_watch.paths`와 겹치는 경로를 찾습니다.
7개 BANK-OM 모두에서 겹치는 경로가 발견되어 `APPROVAL` 결과가 나왔습니다.

`APPROVAL`은 실패가 아닙니다. 자동 적용 전에 담당자가 영향 경로를 확인해야
한다는 뜻입니다.

`upgrade_watch.paths`는 이번 초안에서 **부분 자동 등록**했습니다.

- Git이 해당 BANK-OM commit에서 실제 변경한 전체 경로는 자동으로 등록했습니다.
- 행내에서 수정하지 않았지만 기능이 의존하는 경로는 담당자가
  `watch_dependencies`에 직접 적었습니다.
- 코드 의미를 분석해 숨은 의존 경로까지 자동으로 찾는 기능은 아직 없습니다.

따라서 이번 영향 확인은 “Manifest에 이미 등록된 watch 경로가 공식 버전에서
바뀌었는가?”를 검사합니다. 등록 자체가 빠진 의존 경로는 찾아내지 못합니다.

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

여기서 최종 검사 대상 commit `dee330ebd5...`는 공식 commit이나
BANK-OM ID가 아닙니다. 공식 1.13.1 위에 BANK-OM-001~007의 8개 commit을 모두
적용한 `custom/om-1.13.1` branch의 마지막 Git commit SHA입니다. 검사기는 이
SHA를 지정해 “바로 이 코드 상태”의 Git 이력과 111개 변경 경로를 확인했습니다.

```text
공식 1.13.1 afcb2d2...
  └─ BANK-OM-001 적용
      └─ ...
          └─ BANK-OM-007 후속 적용 dee330ebd5...  ← 최종 검사 대상
```

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

여기서 “공식 변경”과 “BANK-OM 추가 항목 9개”의 이름이 겹치지 않는데도
충돌한 이유가 중요합니다. Git은 JSON의 의미를 이해하지 않고 줄 단위로
병합합니다. 공식 1.13.1이 `label` 객체 전체의 들여쓰기를 바꿨고,
BANK-OM-001도 같은 `label` 객체 안에 새 항목을 넣었기 때문에 Git은 객체
전체를 하나의 충돌 구간으로 표시했습니다. 즉 **코드 의미상의 동일 항목 충돌은
0개였지만, 텍스트 줄 기준 충돌은 발생**했습니다.

대표 파일인 `ko-kr.json`의 전체 충돌 원문은 6,614줄입니다. 본문에는 결과를
판단하는 데 필요한 실제 해결 diff 전체를 표시하고, 충돌 원문과 해결된 JSON은
별도 파일로 보관했습니다.

```diff
diff --git a/openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json b/openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json
index 5300c8cf5a..1219c95cf2 100644
--- a/openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json
+++ b/openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json
@@ -2368,13 +2368,20 @@
         "yes-comma-confirm": "예, 확인합니다",
         "yesterday": "어제",
         "yesterday-activity": "Yesterday's Activity",
         "your-entity": "당신의 {{entity}}",
         "z-to-a": "Z에서 A",
         "zoom-in": "확대",
-        "zoom-out": "축소"
+        "zoom-out": "축소",
+        "code-group": "Code Group",
+        "code-name": "Code Name",
+        "code-value": "Code Value",
+        "instance-code": "인스턴스 코드",
+        "instance-code-lowercase-plural": "인스턴스 코드",
+        "instance-code-plural": "인스턴스 코드",
+        "sort-order": "Sort Order"
     },
     "message": {
         "access-block-time-message": "최대 로그인 실패 시도 횟수 이후 밀리초 동안 접근이 차단됩니다.",
         "access-control-description": "역할과 정책을 통해 조직 계층 구조 및 팀 접근 권한을 조정합니다.",
         "access-to-collaborate": "누구나 팀에 참여하고, 데이터를 보고, 협업할 수 있도록 개방적인 접근을 허용합니다.",
         "action-has-been-done-but-deploy-successfully": "{{action}}되었고 성공적으로 배포되었습니다",
@@ -3339,13 +3346,15 @@
         "welcome-to-open-metadata": "{{brandName}}에 오신 것을 환영합니다!",
         "would-like-to-start-adding-some": "일부를 추가하시겠습니까?",
         "write-markdown-content": "마크다운 콘텐츠를 여기에 작성하세요...",
         "write-your-announcement-lowercase": "공지사항 작성",
         "write-your-description": "설명 작성",
         "write-your-text": "{{text}} 작성",
-        "you-can-also-set-up-the-metadata-ingestion": "메타데이터 수집을 설정할 수도 있습니다."
+        "you-can-also-set-up-the-metadata-ingestion": "메타데이터 수집을 설정할 수도 있습니다.",
+        "instance-code-description": "Manage common/reference codes used as shared master data across the platform.",
+        "instance-code-group-description": "The {{codeGroupName}} code group contains {{count}} registered code(s)."
     },
     "server": {
         "account-verify-success": "이메일이 성공적으로 인증되었습니다",
         "add-entity-error": "{{entity}} 추가 중 오류가 발생했습니다!",
         "article-fetch-error": "Error fetching article content",
         "auth-provider-not-supported-renewing": "{{provider}} 인증 제공자는 토큰 갱신을 지원하지 않습니다.",
```

해결 후에는 공식 1.13.1의 번역 항목과 형식을 유지하면서 위 9개 항목도 남아
있음을 Git에서 다시 확인했습니다. 이 결과가 BANK-OM-001의 새 1.13.1 commit
`83b1e0ac7d`에 기록됐습니다.

전체 증거 파일:

- 충돌 원문: `conflict-evidence/BANK-OM-001_ko-kr_full_conflict.txt`
- 해결 diff: `conflict-evidence/BANK-OM-001_ko-kr_resolution.diff`
- 해결된 전체 JSON: `conflict-evidence/BANK-OM-001_ko-kr_resolved.json`
- commit과 18개 충돌 경로의 연결:
  `conflict-evidence/BANK-OM-001_ko-kr_capture.json`

### 충돌 로그에서 BANK-OM ID를 확인하는 방법

현재 Git 원문은 `error: could not apply 4df83b311f...`까지만 보여주므로
`BANK-OM-001`이 바로 보이지 않습니다. ID는 source commit `4df83b311f`의
commit 본문에 있는 `Customization-ID: BANK-OM-001`에서 확인할 수 있습니다.
즉, 현재는 commit SHA를 한 번 더 조회해야 하므로 운영 로그로는 불친절합니다.

개선 방식은 적용 명령이 시작될 때 commit trailer를 읽어 다음처럼 ID를 함께
출력하고, 결과 JSON에도 같은 값을 저장하는 것입니다.

```text
[BANK-OM-001] APPLY source=4df83b311f target=1.13.1-release
[BANK-OM-001] CONFLICT files=18 representative=.../ko-kr.json
[BANK-OM-001] RESOLVED result=83b1e0ac7d method=json-non-overlap
```

이 ID 표시 wrapper와 승인 기록 연결은 아직 구현되지 않았으며 추가 개발
대상입니다.

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

현재 흐름은 `watch 결과 확인 → 담당자가 cherry-pick 실행 → 충돌 발생 →
JSON 항목이 겹치지 않으면 해결 도구가 바로 파일 작성 → cherry-pick 계속`입니다.
누가 어떤 선택을 승인했는지는 별도 파일에 남지 않습니다.

정식 운영 흐름은 다음처럼 명확히 고정하는 것이 좋습니다.

1. **비교만 수행:** 공식·BANK-OM 변경 항목과 겹침 여부를 `plan.json`으로
   출력하며 아직 코드를 수정하지 않습니다.
2. **담당자 선택:** 기능 담당자가 `자동 병합 승인`, `수동 해결`, `적용 중단`
   중 하나를 선택합니다.
3. **승인 기록:** 승인자, BANK-OM ID, 공식 target SHA, source commit SHA,
   선택한 방법과 시간을 `approval.yaml`에 남깁니다.
4. **코드 적용:** 승인 파일과 plan의 digest가 일치할 때만 해결 도구가 파일을
   작성합니다.
5. **자동 차단:** 동일 JSON 항목이 겹치거나 JSON 외 코드가 충돌하면 선택과
   관계없이 `BLOCK`하고 코드 담당자가 해결합니다.
6. **적용 후 검사:** Manifest 범위 검사, build와 Contract test를 다시 실행해
   최종 결과에 승인 기록을 연결합니다.

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

우리의 목적은 “공식 업그레이드 후 행내 커스터마이징이 코드에 빠짐없이
적용됐고, 업무 동작까지 정상인지 확인한 뒤 배포 검토로 넘기는 것”입니다.

| 목적에 필요한 확인 | 현재 결과 | 지금 말할 수 있는 범위 |
|---|---|---|
| 공식 변경이 커스터마이징에 영향을 주는지 | 충족 | upgrade-watch가 7개 BANK-OM을 검토 대상으로 표시 |
| BANK-OM별 commit이 다시 적용됐는지 | 충족 | 8개 commit과 최종 SHA 확인 |
| 실제 충돌과 해결 결과가 남았는지 | 충족 | 001~004 충돌, 18개 경로, 해결 commit 기록 |
| Manifest와 최종 소스가 일치하는지 | 충족 | 사전자료 5종·소스 검사 8종 PASS |
| 전체 코드가 build되는지 | 미충족 | Java·Maven·Yarn 환경이 없어 미실행 |
| 실제 업무 기능이 정상 동작하는지 | 부분 충족 | 2개 PASS, 7개는 행내 서버·브라우저가 없어 SKIP |
| 사람이 충돌 해결을 승인했는지 | 미충족 | 선택·승인자·승인 시각 기록 없음 |
| 배포 가능한 상태인지 | 미충족 | build·남은 test·승인·검증 tag가 필요 |

따라서 현재 검사기로는 **공식 변경 영향, BANK-OM commit 적용, 파일 범위,
필수 구현 파일과 테스트 코드의 존재**까지 확인할 수 있습니다. 하지만
**전체 build, 실제 화면·API 업무 동작, 사람의 승인과 배포 안전성**까지
증명하지는 못합니다.

다음 단계는 Java·Maven·Yarn과 행내 test URL을 준비해 build와 남은 Contract
test를 수행하고, 충돌 비교 plan과 승인 기록 기능을 추가한 뒤 실제 Git
화면·터미널·검사 결과를 시연 문서에 추가하는 것입니다.
