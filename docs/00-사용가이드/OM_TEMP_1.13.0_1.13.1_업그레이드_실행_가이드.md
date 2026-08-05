# OM_TEMP 1.13.0 → 1.13.1 코드 업그레이드 연습 결과

> 공식 기준: OpenMetadata `1.13.0-release` → `1.13.1-release`
>
> 로컬 브랜치: `fork/om-1.13.1`, `custom/om-1.13.1`
>
> 최종 검사 대상 Git 번호: `dee330ebd5abfe33e1ac61e1ca31879746a1b423`

> **이 페이지가 답하는 질문:** 커밋별 재적용 진단에서 어떤 충돌이 발생했고, 현재 검사기로 어디까지 확인했는가?
> **이 페이지가 답하지 않는 것:** 기본 운영 방식인 vendor-merge 전체와 행내 배포 완료 여부는 아직 검증하지 않았습니다.
> **읽고 나면:** 현재 완료·미완료를 구분한 뒤, 필요한 경우 부록의 과거 참고 코드 검사와 비교합니다.

> **이번 연습에만 사용한 방법:** Git 변경 기록별 재적용과 JSON 충돌 보조 도구는 BANK-OM별
> 충돌을 분리해 보기 위해 이번 OM_TEMP 연습에서 사용했습니다. OpenMetadata 공식
> 업그레이드 기능이나 확정된 행내 운영 절차가 아닙니다.

## 1. 이번 작업의 목적

공식 1.13.1 코드 위에 BANK-OM-001~007을 순서대로 다시 적용하고, 실제 충돌을
해결한 뒤 Manifest와 Git 이력이 일치하는지 검사했습니다. 이 결과는 소스 코드
수준의 **변경 기록별 재적용 진단**이며, 기본 운영 방식인 vendor-merge나 운영 배포
완료를 뜻하지 않습니다.

여기서 **Manifest**는 BANK-OM별 변경 경로, 반드시 유지할 구현 경로, 공식
업그레이드 때 확인할 경로와 연결 test를 기록한 커스터마이징 등록 문서입니다.

### 정식 운영에서 따를 전체 순서

이 연습의 커밋별 재적용 순서와 정식 운영 절차를 혼동하면 안 됩니다. 정식
운영에서는 다음 순서를 사용합니다.

```text
새 공식 버전의 OpenMetadata 포크 브랜치 준비
→ T42로 이전 공식 버전과 새 공식 버전의 영향 경로 확인
→ 직전 커스텀 브랜치와 새 포크 브랜치를 vendor-merge
→ Git 충돌 해결
→ 최종 커스텀 브랜치 기준 plan → 담당자 승인 → apply
→ 등록자료 검사 → 소스 검사 → build·Contract test → T90
→ 검증 완료 tag·Release lock → 릴리즈 브랜치 승격
```

T42는 병합 결과를 검사하는 단계가 아니라, 새 공식 버전이 BANK-OM의 watch
경로를 바꿨는지 병합 전에 알려주는 단계입니다.

## 2. 적용 전에 확인한 영향

이 결과는 **공식 변경 영향 확인 검사(upgrade-watch, T42)**가 만들었습니다.
검사기는 Git으로 공식 1.13.0과 1.13.1 사이에서 바뀐 834개 경로를 구하고,
각 BANK-OM Manifest의 `upgrade_watch.paths`와 겹치는 경로를 찾습니다.
7개 BANK-OM 모두에서 겹치는 경로가 발견되어 `APPROVAL` 결과가 나왔습니다.

`APPROVAL`은 실패가 아닙니다. 자동 적용 전에 담당자가 영향 경로를 확인해야
한다는 뜻입니다.

`upgrade_watch.paths`는 현재 다음 방식으로 등록합니다.

- 준비도구(plan)가 BANK-OM commit의 실제 변경 경로 중 **공식 OpenMetadata 포크
  브랜치에도 존재하는 경로**를 자동 후보로 제안합니다.
- 공식 코드에 없는 행내 전용 파일과 간접 의존 경로는 담당자 질문으로 남겨 사람이
  watch 포함 여부를 결정합니다.
- 행내에서 수정하지 않았지만 기능이 의존하는 경로는 담당자가
  `watch_dependencies`에 적습니다.
- 새 공식 버전에서 바뀐 파일 이름을 커스터마이징 코드가 직접 참조하면 검사기가
  추가 watch 후보와 참조 근거를 제시합니다. 담당자가 확인한 뒤 Manifest에
  반영합니다.

따라서 공식 코드에도 있는 직접 변경 경로의 자동 제안과 직접 참조 후보 제시는 현재
구현되어 있습니다.
다만 간접 호출이나 런타임 설정처럼 코드에 이름이 드러나지 않는 의존 관계는
담당자가 직접 확인해야 합니다.

이 단계의 Git 비교 대상은 **공식 이전 버전과 공식 새 버전**입니다.
제품 코드 저장소에서 실행할 때는 공식 코드만 담은 `fork/om-1.13.0`과
`fork/om-1.13.1`을 비교해도 같은 결과가 나옵니다. 커스터마이징이 들어간
`custom/...` branch는 이 비교에 사용하지 않고, 영향 검토가 끝난 뒤 BANK-OM
재적용과 소스 검사 단계에서 별도로 확인합니다.

| BANK-OM | 공식 버전에서 바뀐 감시 경로 |
|---|---:|
| BANK-OM-001 | 22개 |
| BANK-OM-002 | 23개 |
| BANK-OM-003 | 19개 |
| BANK-OM-004 | 20개 |
| BANK-OM-005 | 1개 |
| BANK-OM-006 | 4개 |
| BANK-OM-007 | 1개 |

## 3. 브랜치 생성과 커스터마이징 적용

```bash
git worktree add -b fork/om-1.13.1 \
  ../om-temp-1.13.1-upgrade 1.13.1-release
git -C ../om-temp-1.13.1-upgrade switch -c custom/om-1.13.1
```

`fork/om-1.13.1`은 공식 1.13.1 코드만 보관하는 OpenMetadata 포크 브랜치입니다.
`custom/om-1.13.1`은 그 위에 BANK-OM 커밋을 적용한 검사 대상 커스텀 브랜치입니다.
두 브랜치는 현재 로컬에만
있고 GitHub에는 아직 push하지 않았습니다.

이 단계의 최종 검사 대상 Git 번호 `dee330ebd5...`는 공식 버전 번호나
BANK-OM ID가 아닙니다. 공식 1.13.1 위에 BANK-OM-001~007의 변경 기록 8개를 모두
적용한 `custom/om-1.13.1` branch의 마지막 상태를 가리킵니다. 검사기는 이 번호를
입력받아 “바로 이 시점의 코드”와 111개 변경 경로를 확인했습니다.

여기에는 운영 판단상 중요한 제한이 있습니다. 저장된 소스 검사 결과의
`integration_strategy`는 `vendor-merge`로 기록됐지만, 이 후보를 만든 실제
방법은 아래에 설명한 커밋별 재적용입니다. 따라서 T25의 PASS는 “공식 1.13.1이
후보의 Git 이력에 포함됐다”는 사실만 증명합니다. 실제 vendor branch 병합 기록과
충돌 해결 증거까지 검증한 결과가 아니므로, 이 후보를 vendor-merge 운영경로
통과로 해석하면 안 됩니다.

```text
공식 1.13.1 afcb2d2...
  └─ BANK-OM-001 적용
      └─ ...
          └─ BANK-OM-007 후속 적용 dee330ebd5...  ← 최종 검사 대상
```

## 4. 실제 충돌과 해결

### 먼저, BANK-OM별 충돌을 분리해 확인한 진단 방법

1.13.0의 BANK-OM 변경은 기능별 Git 변경 기록으로 나뉘어 있습니다. 이 연습에서는
**어느 BANK-OM에서 충돌하는지 기능별로 구분해 확인하려고** 각 기록의 변경을
공식 1.13.1 위에 하나씩 다시 적용했습니다. 이때 실제로 사용한 Git 명령이
`git cherry-pick <BANK-OM commit SHA>`입니다.

`cherry-pick`은 다른 branch에 저장된 특정 변경 기록 하나를 현재 branch에
복사해 적용하는 Git 명령입니다. 커밋 순서를 임의로 바꾸는 명령이라는 뜻은
아닙니다. 이번에는 BANK-OM 변경을 한 건씩 적용해 어느 ID에서 충돌했는지 바로
기록하려고 사용했습니다. 충돌을 만들기 위해 반드시 필요한 명령은 아니며,
branch 전체를 병합해도 같은 코드 구간이 겹치면 충돌할 수 있습니다.

이번에는 BANK-OM별 충돌 파일을 바로 식별하려고 `cherry-pick`을 사용했습니다.
따라서 아래 결과가 증명하는 범위는 **commit별 재적용에서 발생한 충돌과 해결
과정**입니다. 실제 운영 전략을 `vendor-merge`로 정한다면 OpenMetadata 포크
브랜치와 커스텀 브랜치를 실제 방식으로 합친 뒤 검사기까지 실행하는 별도 운영경로 검증이
필요합니다.

```text
1.13.0에서 만든 BANK-OM commit
  → 공식 1.13.1에 BANK-OM 변경을 하나씩 적용
    (이번 실행 명령: git cherry-pick)
    → 충돌 없음: 해당 BANK-OM 적용 완료
    → 충돌 발생: Git이 멈추고 사람이 해결한 뒤 계속 진행
```

> **현재 검증 범위:** 아래 표와 충돌 화면은 BANK-OM별 진단 결과입니다.
> `vendor-merge` 운영경로 전체가 검증됐다는 의미는 아닙니다.

| BANK-OM | 1.13.1 적용 commit | 실제 충돌 | 처리 |
|---|---|---|---|
| BANK-OM-001 | `83b1e0ac7d` | 번역 JSON 18개 | 각 파일에 행내 번역 항목 9개 추가 |
| BANK-OM-002 | `8b368af0a2` | 번역 JSON 18개 | 각 파일에 행내 번역 항목 11개 추가 |
| BANK-OM-003 | `e1d181d728` | 번역 JSON 18개 | 각 파일에 행내 번역 항목 5개 추가 |
| BANK-OM-004 | `ed870cd63d` | 번역 JSON 18개 | 각 파일에 행내 번역 항목 9개 추가 |
| BANK-OM-005 | `dfd3ad5e1c` | 충돌 없음 | 자동 적용 |
| BANK-OM-006 | `15b85814f5` | 충돌 없음 | 자동 적용 |
| BANK-OM-007 | `e7e4ba67b6 + dee330ebd5` | 충돌 없음 | 두 커밋을 순서대로 적용 |

001~004는 각각 번역 JSON 18개에서 충돌한 것으로 기록됐습니다. BANK-OM-001은
18개 상세 경로까지 보관했지만 002~004는 건수만 보관했으므로, 네 차례의 파일
목록이 완전히 같다고 단정하지 않습니다.

### 실제로 충돌이 발생한 순간

BANK-OM-001의 1.13.0 변경 `4df83b311f`를 공식 1.13.1에 하나의 기능 단위로
다시 적용했습니다. 실제 명령은 `git cherry-pick 4df83b311f`였고, Git이 아래
지점에서 자동 적용을 중단했습니다.

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
Git이 자동으로 결정하지 못해 중단됐습니다. 공식 1.13.1은 JSON 파일의 형식과
항목 배치를 크게 바꾸고 공식 번역 항목도 변경했습니다. 반면 BANK-OM-001은
공식 1.13.0의 기존 형식을 바탕으로 같은 JSON 객체에 행내 번역 항목 9개를
추가했습니다.

이 충돌은 공식과 BANK-OM이 같은 번역 항목의 값을 서로 다르게 고친 충돌이
아닙니다. Git은 JSON 항목의 의미를 이해하지 않고 줄 단위로 비교합니다.

1. 공통 기준인 공식 1.13.0에는 BANK-OM 번역 항목이 없습니다.
2. 공식 1.13.1은 같은 `label`·`message` 객체의 형식과 공식 번역 항목을
   변경했습니다.
3. BANK-OM-001은 공식 1.13.0 형식을 기준으로 같은 객체의 끝에 행내 번역
   항목 9개를 추가했습니다.

두 변경은 공통 기준인 1.13.0에서 서로 다른 방향으로 파일의 넓은 영역을
바꿨습니다. Git은 JSON 항목의 의미가 아니라 줄 단위 차이를 계산하기 때문에,
두 결과를 자동으로 한 파일로 조립하지 못했습니다. 이후 항목 이름별로 다시
비교한 결과, 양쪽이 동시에 바꾼 동일 항목은 0개였습니다.

Git CLI는 별도 선택 창을 띄우지 않고 충돌 파일에 `<<<<<<<`, `=======`,
`>>>>>>>` 구분선을 넣습니다. **HEAD는 현재 작업 branch의 코드**를 뜻하며,
이번 실행에서는 공식 1.13.1입니다. `4df83b311f`는 적용하려는 BANK-OM-001
쪽입니다. 아래 표시는 같은 한 줄의 왼쪽·오른쪽 값을 비교한 것이 아닙니다.
Git이 한 파일 안에서 자동으로 합치지 못한 **두 개의 큰 충돌 블록**입니다.

```text
[공식 버전 시작 표시] <<<<<<< HEAD
[공식 1.13.1 쪽 충돌 내용 약 2,373줄]
[두 버전 구분 표시] =======
[공식 1.13.0 형식에 BANK-OM-001을 추가한 쪽 충돌 내용 약 3,178줄]
[BANK 버전 끝 표시] >>>>>>> 4df83b311f (add InstanceCode customization)
```

실제 충돌 원문에서 `HEAD` 영역은 2~2,375행, BANK-OM 영역은
2,377~5,554행입니다. 원문 전체는 6,614행이며, 1행과 5,556~6,614행은
충돌 표시 밖에서 Git이 자동으로 맞춘 영역입니다. BANK 쪽 충돌 내용이 공식
쪽보다 약 805줄 긴 주된 이유는 행내 항목을 805줄 추가했기 때문이 아니라,
공식 1.13.0의 더 긴 기존 형식을 유지했기 때문입니다. 실제 BANK-OM-001 추가는
9개 항목입니다.

#### 실제 충돌 파일에서 발췌한 코드

아래는 설명을 위해 새로 만든 예시가 아니라
`BANK-OM-001_ko-kr_full_conflict.txt`의 실제 행입니다. 첫 블록은 충돌 시작과
두 버전의 경계, 두 번째 블록은 BANK 쪽 충돌 블록 안에 실제로 들어 있던
9개 추가 항목의 위치를 보여줍니다. 서로 떨어진 행 사이에는 `[중간 생략]`을
표시했습니다.

```text
   1 │ {
   2 │ <<<<<<< HEAD
   3 │     "label": {
   4 │         "-with-colon": "{{text}}:",
     │         [공식 1.13.1 쪽 충돌 내용 중간 생략]
2374 │         "zoom-in": "확대",
2375 │         "zoom-out": "축소"
2376 │ =======
2377 │   "label": {
2378 │     "-with-colon": "{{text}}:",
     │     [BANK-OM-001 쪽 충돌 내용 계속]
```

```text
2676 │     "code-group": "Code Group",
2677 │     "code-name": "Code Name",
2678 │     "code-value": "Code Value",
     │     [중간 생략]
3441 │     "instance-code": "인스턴스 코드",
3442 │     "instance-code-lowercase-plural": "인스턴스 코드",
3443 │     "instance-code-plural": "인스턴스 코드",
     │     [중간 생략]
4300 │     "sort-order": "Sort Order",
     │     [중간 생략]
5112 │     "instance-code-description": "Manage common/reference codes used as shared master data across the platform.",
5113 │     "instance-code-group-description": "The {{codeGroupName}} code group contains {{count}} registered code(s).",
     │     [BANK 쪽 충돌 내용 계속]
5555 │ >>>>>>> 4df83b311f (add InstanceCode customization)
5556 │     },
5557 │     "message": {
```

즉, Git이 `zoom-out` 한 줄과 `label` 한 줄 중 하나를 고르라는 의미가 아닙니다.
2~5,555행에 걸친 큰 충돌 구간 안에서 공식 쪽과 BANK 쪽 내용을 모두 남긴
것이며, BANK의 9개 항목도 그 BANK 쪽 블록의 서로 다른 위치에 들어 있었습니다.

### 이번 충돌을 해결한 방법

한쪽 전체를 선택하면 공식 1.13.1 변경이나 BANK-OM 변경 중 하나를 잃을 수
있습니다. 그래서 공식 1.13.1 JSON을 기준으로 유지하고, BANK-OM이 새로 추가한
9개 번역 항목만 넣었습니다. 이 중 7개는 `label`, 2개는 `message` 객체에
들어갑니다. 해결 후 실제 diff는 아래와 같습니다.

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

### 실제로 사용한 제한적 JSON 충돌 보조 도구

도구는 실제로 `harness/tools/resolve_nonoverlapping_json_conflicts.py`에
구현되어 있습니다. 검사기 전체의 필수 단계가 아니라, **Git이 JSON 충돌로
멈췄을 때만 실행하는 제한된 보조 도구**입니다. 각 충돌 파일에서 Git이 보관한
세 값을 입력으로 읽습니다. `stage 1·2·3`은 실행 순서가 아니라 Git이 충돌
파일 하나에 보관한 세 버전의 번호입니다.

| Git 표기 | Git에서 고정된 의미 | 이번 연습의 실제 내용 | 직접 확인 명령 | 도구에서 하는 일 |
|---|---|---|---|---|
| `stage 1 · BASE` | 두 변경의 공통 기준 | 공식 1.13.0과 BANK-OM이 갈라지기 전 JSON | `git show :1:<파일경로>` | 양쪽 변경을 계산하는 기준 |
| `stage 2 · OURS` | 현재 checkout한 branch의 내용 | 이번 연습에서는 HEAD인 공식 1.13.1 JSON | `git show :2:<파일경로>` | 해결 파일의 바탕으로 유지 |
| `stage 3 · THEIRS` | 지금 적용 중인 반대편 변경 | 이번 cherry-pick에서는 BANK-OM commit의 JSON | `git show :3:<파일경로>` | 다시 반영할 BANK-OM 변경 계산 |

이번 연습에서는 공식 1.13.1 branch에서 BANK-OM commit을 cherry-pick했기 때문에
`stage 2=공식`, `stage 3=BANK-OM`입니다. 일반 merge에서도 stage 2는 현재
checkout한 쪽(OURS), stage 3은 들어오는 쪽(THEIRS)이므로 branch 방향을 바꾸면
공식/BANK-OM 대응도 바뀔 수 있습니다.

도구는 먼저 `stage 1→stage 2`에서 바뀐 최종 JSON 항목 목록과
`stage 1→stage 3`에서 바뀐 최종 JSON 항목 목록을 각각 만듭니다. 예를 들어
`label` 안의 `instance-code`는 `label.instance-code`라는 한 항목입니다.
줄 번호와 들여쓰기는 비교하지 않습니다.

| 판단 | 도구가 비교하는 값 | 계속 진행 | 중단 |
|---|---|---|---|
| 충돌 파일 종류 | `git diff --name-only --diff-filter=U` 결과 | 모두 JSON | JSON 이외 파일이 하나라도 있으면 파일을 쓰기 전에 중단 |
| OURS 변경 계산 | BASE와 OURS의 최종 JSON 항목별 값 | 변경 항목 목록 생성 | JSON을 읽을 수 없으면 파일을 쓰기 전에 중단 |
| THEIRS 변경 계산 | BASE와 THEIRS의 최종 JSON 항목별 값 | 변경 항목 목록 생성 | JSON을 읽을 수 없으면 파일을 쓰기 전에 중단 |
| 두 목록 겹침 | OURS 변경 항목 경로와 THEIRS 변경 항목 경로의 교집합 | 0개면 OURS에 THEIRS 변경 반영 | 1개라도 겹치면 최종 값이 같아도 파일을 쓰기 전에 중단 |

이번 18개 JSON에서는 OURS와 THEIRS가 함께 바꾼 최종 JSON 항목이 0개였으므로
공식 1.13.1인 OURS 전체를 유지하고 BANK-OM인 THEIRS 변경만 반영했습니다.

이번 18개 JSON에서는 양쪽이 함께 바꾼 동일 JSON 항목이 0개였으므로 보조 도구가
해결 파일을 작성했습니다. 이 처리 방식은 반복 가능한 업그레이드 연습을 위해
구현했으며 OpenMetadata의 기존 기능이나 확정된 행내 승인 정책은 아닙니다.

도구를 실행하면 충돌 난 JSON 파일 자체를 작업 branch에서 수정하고, 터미널에
파일별 적용 건수를 출력합니다. 이때 **작업 폴더의 파일 내용만 바뀌며 Git
index는 아직 충돌 미해결 상태**입니다. 담당자가 diff와 test를 확인한 뒤
`git add`를 해야 Git이 해당 파일을 해결 완료로 인식합니다. 현재 도구는 별도의
결과 보고서, 승인 파일, `plan.json`을 만들지 않고 `git add`, test,
`git cherry-pick --continue`도 실행하지 않습니다.

```text
resolved .../languages/ko-kr.json: BANK-OM leaf changes=9
```

위 출력의 `leaf changes=9`는 도구가 BANK-OM 쪽에서 새로 추가된 최종 JSON
항목 9개를 공식 1.13.1 파일에 반영했다는 뜻입니다. 사용자가 입력하는 설정
이름도, 검사 PASS도, Git 충돌 해결 완료도 아닙니다.

아래 자료는 도구가 자동 생성한 운영 보고서가 아니라, **이번 충돌 재현 결과를
가이드에서 확인할 수 있도록 별도로 보관한 증거 자료**입니다.

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

### 정식 운영 전에 추가할 승인 기록

현재 보조 도구는 충돌 파일을 수정하지만, 누가 비교 결과를 확인하고 해결을
승인했는지 별도 파일에 기록하지 않습니다. 정식 운영에서는 다음 기능을 추가해야
합니다.

1. **비교만 수행:** 공식·BANK-OM 변경 항목과 겹침 여부를 `plan.json`으로
   출력하며 아직 코드를 수정하지 않습니다.
2. **담당자 선택:** 기능 담당자가 `자동 병합 승인`, `수동 해결`, `적용 중단`
   중 하나를 선택합니다.
3. **승인 기록:** 승인자, BANK-OM ID, 공식 target SHA, source commit SHA,
   선택한 방법과 시간을 `approval.yaml`에 남깁니다.
4. **코드 적용:** 승인 파일과 plan의 digest가 일치할 때만 해결 도구가 파일을
   작성합니다.
5. **자동 차단:** 동일 JSON 항목이 겹치거나 JSON 외 코드가 충돌하면 선택과
   관계없이 `BLOCK`하고 코드 담당자가 해결합니다. `BLOCK`은 자동 진행을
   멈추고 사람이 원인을 확인해야 한다는 판정입니다.
6. **적용 후 검사:** Manifest 범위 검사, build와 Contract test를 다시 실행해
   최종 결과에 승인 기록을 연결합니다.

## 5. 1.13.1 기준자료 다시 생성

1.13.0 자료를 그대로 검사하지 않고 `om-temp-1.13.1` 등록 폴더를 새로
만들었습니다. 새 버전 운영에서는 최종 커스텀 브랜치를 기준으로 준비도구의
`plan → 담당자 승인 → apply`를 실행합니다. 도구는 Manifest와 파생 등록자료의
변경안을 만들고, Registry 변경이 필요한 경우에만 proposal에 함께 표시합니다.
Contract는 업무 동작과 필수 test가 달라진 경우 담당자가 직접 갱신합니다.

이번 연습 자료는 자동화 도입 전에 만든 과거 진단 결과이므로 공식 SHA·검사 대상
SHA·전체 diff·공용 경로·정책 파일을 1.13.1 기준으로 다시 생성했습니다. 이
과거 생성 방식을 일반 후속 commit의 운영 명령으로 사용하지 않습니다.

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
| 운영 통합 방식 일치 | 실제 vendor-merge 기록과 충돌 해결 증거가 있는지 | NOT VERIFIED |

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
| 목표 vendor-merge 절차를 통과했는지 | 미충족 | 후보는 커밋별 재적용으로 생성됐고 실제 merge 증거가 없음 |
| 전체 코드가 build되는지 | 미충족 | Java·Maven·Yarn 환경이 없어 미실행 |
| 실제 업무 기능이 정상 동작하는지 | 부분 충족 | 2개 PASS, 7개는 행내 서버·브라우저가 없어 SKIP |
| 사람이 충돌 해결을 승인했는지 | 미충족 | 선택·승인자·승인 시각 기록 없음 |
| 배포 가능한 상태인지 | 미충족 | build·남은 test·승인·검증 완료 태그·Release lock·릴리즈 브랜치 승격이 필요 |

따라서 현재 검사기로는 **공식 변경 영향, BANK-OM commit 적용, 파일 범위,
필수 구현 파일과 테스트 코드의 존재**까지 확인할 수 있습니다. 하지만
**전체 build, 실제 화면·API 업무 동작, 사람의 승인과 배포 안전성**까지
증명하지는 못합니다.

다음 단계는 Java·Maven·Yarn과 행내 test URL을 준비해 build와 남은 Contract
test를 수행하는 것입니다. 그와 별도로 직전 custom branch에 공식 1.13.1을 실제
merge해 vendor-merge 후보를 만들고, merge 기록·충돌 증거·candidate lock의
전략값이 일치하는지 다시 검사해야 합니다. 이후 충돌 비교 plan과 승인 기록
기능을 추가하고 실제 Git 화면·터미널·검사 결과를 시연 문서에 추가합니다.
