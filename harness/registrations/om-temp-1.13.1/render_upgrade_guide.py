#!/usr/bin/env python3
"""Render the actual OM_TEMP 1.13.0 -> 1.13.1 upgrade guide."""

from __future__ import annotations

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MD = ROOT / "docs/00-사용가이드/OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드.md"
HTML = ROOT / "docs/00-사용가이드/OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드_미리보기.html"
EVIDENCE = ROOT / "harness/registrations/om-temp-1.13.1/conflict-evidence"
RESOLUTION_DIFF = EVIDENCE / "BANK-OM-001_ko-kr_resolution.diff"


ROWS = [
    ("BANK-OM-001", "83b1e0ac7d", "번역 JSON 18개", "각 파일에 행내 번역 항목 9개 추가"),
    ("BANK-OM-002", "8b368af0a2", "번역 JSON 18개", "각 파일에 행내 번역 항목 11개 추가"),
    ("BANK-OM-003", "e1d181d728", "번역 JSON 18개", "각 파일에 행내 번역 항목 5개 추가"),
    ("BANK-OM-004", "ed870cd63d", "번역 JSON 18개", "각 파일에 행내 번역 항목 9개 추가"),
    ("BANK-OM-005", "dfd3ad5e1c", "충돌 없음", "자동 적용"),
    ("BANK-OM-006", "15b85814f5", "충돌 없음", "자동 적용"),
    ("BANK-OM-007", "e7e4ba67b6 + dee330ebd5", "충돌 없음", "두 커밋을 순서대로 적용"),
]


def markdown() -> str:
    rows = "\n".join(f"| {a} | `{b}` | {c} | {d} |" for a, b, c, d in ROWS)
    resolution_diff = RESOLUTION_DIFF.read_text(encoding="utf-8").rstrip()
    return f"""# OM_TEMP 1.13.0 → 1.13.1 코드 업그레이드 연습 결과

> 공식 기준: OpenMetadata `1.13.0-release` → `1.13.1-release`
>
> 로컬 branch: `patch/om-1.13.1`, `custom/om-1.13.1`
>
> 최종 검사 대상 commit: `dee330ebd5abfe33e1ac61e1ca31879746a1b423`

> **이 페이지가 답하는 질문:** 커밋별 재적용 진단에서 어떤 충돌이 발생했고, 현재 검사기로 어디까지 확인했는가?
> **이 페이지가 답하지 않는 것:** 기본 운영 방식인 vendor-merge 전체와 행내 배포 완료 여부는 아직 검증하지 않았습니다.
> **읽고 나면:** 현재 완료·미완료를 구분한 뒤, 필요한 경우 부록의 과거 참고 코드 검사와 비교합니다.

> **이번 연습에만 사용한 방법:** commit별 재적용과 JSON 충돌 보조 도구는 BANK-OM별
> 충돌을 분리해 보기 위해 이번 OM_TEMP 연습에서 사용했습니다. OpenMetadata 공식
> 업그레이드 기능이나 확정된 행내 운영 절차가 아닙니다.

## 1. 이번 작업의 목적

공식 1.13.1 코드 위에 BANK-OM-001~007을 순서대로 다시 적용하고, 실제 충돌을
해결한 뒤 Manifest와 Git 이력이 일치하는지 검사했습니다. 이 결과는 소스 코드
수준의 **커밋별 재적용 진단**이며, 기본 운영 방식인 vendor-merge나 운영 배포
완료를 뜻하지 않습니다.

여기서 **Manifest**는 BANK-OM별 변경 경로, 반드시 유지할 구현 경로, 공식
업그레이드 때 확인할 경로와 연결 test를 기록한 커스터마이징 등록 문서입니다.

## 2. 적용 전에 확인한 영향

이 결과는 **공식 변경 영향 확인 검사(upgrade-watch, T42)**가 만들었습니다.
검사기는 Git으로 공식 1.13.0과 1.13.1 사이에서 바뀐 834개 경로를 구하고,
각 BANK-OM Manifest의 `upgrade_watch.paths`와 겹치는 경로를 찾습니다.
7개 BANK-OM 모두에서 겹치는 경로가 발견되어 `APPROVAL` 결과가 나왔습니다.

`APPROVAL`은 실패가 아닙니다. 자동 적용 전에 담당자가 영향 경로를 확인해야
한다는 뜻입니다.

`upgrade_watch.paths`는 현재 다음 방식으로 등록합니다.

- Manifest 생성기가 해당 BANK-OM commit에서 실제 변경한 전체 경로를 Git에서
  읽어 자동으로 포함합니다.
- 행내에서 수정하지 않았지만 기능이 의존하는 경로는 담당자가
  `watch_dependencies`에 적습니다.
- 새 공식 버전에서 바뀐 파일 이름을 커스터마이징 코드가 직접 참조하면 검사기가
  추가 watch 후보와 참조 근거를 제시합니다. 담당자가 확인한 뒤 Manifest에
  반영합니다.

따라서 실제 변경 경로 자동 포함과 직접 참조 후보 제시는 현재 구현되어 있습니다.
다만 간접 호출이나 런타임 설정처럼 코드에 이름이 드러나지 않는 의존 관계는
담당자가 직접 확인해야 합니다.

이 단계의 Git 비교 대상은 **공식 이전 버전과 공식 새 버전**입니다.
행내 branch로 실행할 때는 공식 코드만 담은 `patch/om-1.13.0`과
`patch/om-1.13.1`을 비교해도 같은 결과가 나옵니다. 커스터마이징이 들어간
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

## 3. branch 생성과 커스터마이징 적용

```bash
git worktree add -b patch/om-1.13.1 \\
  ../om-temp-1.13.1-upgrade 1.13.1-release
git -C ../om-temp-1.13.1-upgrade switch -c custom/om-1.13.1
```

`patch/om-1.13.1`은 공식 1.13.1 코드만 보관합니다. `custom/om-1.13.1`은
그 위에 BANK-OM 커밋을 적용한 검사 대상 branch입니다. 두 branch는 현재 로컬에만
있고 GitHub에는 아직 push하지 않았습니다.

이 단계의 최종 검사 대상 commit `dee330ebd5...`는 공식 commit이나
BANK-OM ID가 아닙니다. 공식 1.13.1 위에 BANK-OM-001~007의 8개 commit을 모두
적용한 `custom/om-1.13.1` branch의 마지막 Git commit SHA입니다. 검사기는 이
SHA를 지정해 “바로 이 코드 상태”의 Git 이력과 111개 변경 경로를 확인했습니다.

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

1.13.0의 BANK-OM 변경은 기능별 Git commit으로 나뉘어 있습니다. 이 연습에서는
**어느 BANK-OM에서 충돌하는지 기능별로 구분해 확인하려고** 각 commit의 변경을
공식 1.13.1 위에 하나씩 다시 적용했습니다. 이때 실제로 사용한 Git 명령이
`git cherry-pick <BANK-OM commit SHA>`입니다.

이 문서에서는 이 작업을 **BANK-OM 변경 적용**이라고 부릅니다. `cherry-pick`은
이번 진단에서 선택한 commit 단위 적용 방법이지, 충돌을 재현하는 데 반드시
필요한 명령도 아니고 모든 업그레이드에서 사용해야 하는 규칙도 아닙니다.
branch를 합치거나 rebase할 때도 같은 코드 구간이 겹치면 충돌할 수 있습니다.

이번에는 BANK-OM별 충돌 파일을 바로 식별하려고 `cherry-pick`을 사용했습니다.
따라서 아래 결과가 증명하는 범위는 **commit별 재적용에서 발생한 충돌과 해결
과정**입니다. 실제 운영 전략을 `vendor-merge`로 정한다면 patch branch와 custom
branch를 실제 방식으로 합친 뒤 검사기까지 실행하는 별도 운영경로 검증이
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
{rows}

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

### 이번 충돌을 해결한 방법

한쪽 전체를 선택하면 공식 1.13.1 변경이나 BANK-OM 변경 중 하나를 잃을 수
있습니다. 그래서 공식 1.13.1 JSON을 기준으로 유지하고, BANK-OM이 새로 추가한
9개 번역 항목만 넣었습니다. 이 중 7개는 `label`, 2개는 `message` 객체에
들어갑니다. 해결 후 실제 diff는 아래와 같습니다.

```diff
{resolution_diff}
```

해결 후에는 공식 1.13.1의 번역 항목과 형식을 유지하면서 위 9개 항목도 남아
있음을 Git에서 다시 확인했습니다. 이 결과가 BANK-OM-001의 새 1.13.1 commit
`83b1e0ac7d`에 기록됐습니다.

### 실제로 사용한 JSON 충돌 보조 도구

도구는 실제로 `harness/tools/resolve_nonoverlapping_json_conflicts.py`에
구현되어 있습니다. 검사기 전체의 필수 단계가 아니라, **Git이 JSON 충돌로
멈췄을 때만 실행하는 제한된 보조 도구**입니다. 각 충돌 파일에서 Git이 보관한
세 값을 입력으로 읽습니다.

1. `stage 1` — 공식 1.13.0과 BANK-OM 변경이 갈라지기 전 공통 기준 JSON
2. `stage 2` — 지금 유지해야 할 공식 1.13.1 JSON
3. `stage 3` — 지금 적용하려는 BANK-OM commit의 JSON

도구는 세 JSON에서 실제 값을 담는 항목별로 변경 여부를 비교합니다. 예를 들어
`label` 안의 `instance-code`는 `label.instance-code`라는 한 항목으로
구분합니다. 이는 사용자가 별도로 입력하는 설정이 아니라 도구 내부의 비교
방법입니다.

- 공식 1.13.1과 BANK-OM이 **서로 다른 JSON 항목**을 바꿨으면 공식 1.13.1
  JSON을 유지하고 BANK-OM 변경만 추가합니다.
- 양쪽이 **같은 JSON 항목**을 바꿨거나 JSON 이외의 파일이 충돌하면 도구가
  아무 값도 선택하지 않고 중단합니다.

이번 18개 JSON에서는 양쪽이 함께 바꾼 동일 JSON 항목이 0개였으므로 보조 도구가
해결 파일을 작성했습니다. 이 처리 방식은 반복 가능한 업그레이드 연습을 위해
구현했으며 OpenMetadata의 기존 기능이나 확정된 행내 승인 정책은 아닙니다.

도구를 실행하면 충돌 난 JSON 파일 자체를 작업 branch에서 수정하고, 터미널에
파일별 적용 건수를 출력합니다. 현재 도구는 별도의 결과 보고서, 승인 파일,
`plan.json`을 만들지 않습니다. 담당자는 수정된 JSON을 확인한 뒤 `git add`와
`git cherry-pick --continue`를 실행해야 합니다.

```text
resolved .../languages/ko-kr.json: BANK-OM leaf changes=9
```

위 실제 출력의 `leaf changes`는 “최종 값을 담는 JSON 항목 9개”라는 도구 내부
표현입니다.

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
| 배포 가능한 상태인지 | 미충족 | build·남은 test·승인·검증 tag가 필요 |

따라서 현재 검사기로는 **공식 변경 영향, BANK-OM commit 적용, 파일 범위,
필수 구현 파일과 테스트 코드의 존재**까지 확인할 수 있습니다. 하지만
**전체 build, 실제 화면·API 업무 동작, 사람의 승인과 배포 안전성**까지
증명하지는 못합니다.

다음 단계는 Java·Maven·Yarn과 행내 test URL을 준비해 build와 남은 Contract
test를 수행하는 것입니다. 그와 별도로 직전 custom branch에 공식 1.13.1을 실제
merge해 vendor-merge 후보를 만들고, merge 기록·충돌 증거·candidate lock의
전략값이 일치하는지 다시 검사해야 합니다. 이후 충돌 비교 plan과 승인 기록
기능을 추가하고 실제 Git 화면·터미널·검사 결과를 시연 문서에 추가합니다.
"""


def html_page() -> str:
    conflict_rows = "".join(
        f"<tr><td>{a}</td><td><code>{b}</code></td><td>{c}</td><td>{d}</td></tr>"
        for a, b, c, d in ROWS
    )
    resolution_diff = escape(RESOLUTION_DIFF.read_text(encoding="utf-8").rstrip())
    pagination = """
<nav class="guide-pagination" aria-label="가이드 페이지 이동">
  <a class="guide-page-link" href="OM_TEMP_커밋별_Manifest_등록_가이드_미리보기.html" target="_top">
    <small>← 이전 가이드</small>
    <strong>검사 전 사전환경 설정</strong>
  </a>
  <div class="guide-page-current">
    <small>전체 5개 중</small>
    <strong>4 · OM_TEMP 코드 업그레이드 연습</strong>
  </div>
  <a class="guide-page-link is-next" href="공유문서/openmetadata-phase3-demo-preview.html" target="_top">
    <small>다음 가이드 →</small>
    <strong>부록 · 과거 참고 코드 검사</strong>
  </a>
</nav>
    """.strip()
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OM_TEMP 1.13.0 → 1.13.1 코드 업그레이드 연습 결과</title>
<style>
:root{{--ink:#172033;--muted:#667085;--line:#d8dfeb;--blue:#2457d6;--green:#067647;--amber:#b54708}}
*{{box-sizing:border-box}} body{{margin:0;background:#eef2f7;color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR","Segoe UI",sans-serif;font-weight:400;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}}
main{{width:min(1100px,calc(100% - 28px));margin:28px auto 64px}}
.guide-pagination{{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);gap:10px;align-items:stretch;margin:0 0 16px}}
.guide-pagination-bottom{{margin:18px 0 0}} .guide-page-link,.guide-page-current{{display:flex;flex-direction:column;justify-content:center;min-width:0;padding:12px 14px;border:1px solid var(--line);border-radius:13px;background:white}}
.guide-page-link{{color:var(--blue);text-decoration:none}} .guide-page-link.is-disabled{{color:var(--muted);text-align:right;opacity:.55}} .guide-page-current{{align-items:center;text-align:center;background:#e8efff}}
.guide-pagination small{{margin-bottom:3px;color:var(--muted);font-size:12px}} .guide-pagination strong{{overflow-wrap:anywhere}}
.hero{{padding:34px;border-radius:24px;color:white;background:linear-gradient(135deg,#172554,#2457d6);box-shadow:0 20px 55px #193b7b2e}}
h1{{margin:0 0 12px;font-size:clamp(28px,4vw,43px);letter-spacing:-.04em}} .hero p{{margin:6px 0;color:#e5edff;line-height:1.65}}
.chips{{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}} .chips span{{padding:7px 11px;border:1px solid #ffffff42;border-radius:999px;background:#ffffff16;font-size:13px}}
.page-scope{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:18px 0}}
.page-scope>div{{padding:14px 16px;border:1px solid var(--line);border-radius:14px;background:white}}
.page-scope strong{{display:block;margin-bottom:6px}} .page-scope p{{margin:0;color:var(--muted);line-height:1.65}}
.internal-scope{{margin:0 0 18px;padding:11px 13px;border-left:4px solid var(--amber);background:#fff7ed;color:var(--ink)}}
.summary{{margin:18px 0;padding:22px;border:1px solid var(--line);border-radius:18px;background:white;line-height:1.7}}
details{{margin:14px 0;border:1px solid var(--line);border-radius:18px;background:white;overflow:hidden;box-shadow:0 6px 22px #13234a0d}}
summary{{display:grid;grid-template-columns:42px minmax(0,1fr) auto;gap:12px;align-items:center;padding:19px 21px;cursor:pointer;list-style:none}}
summary::-webkit-details-marker{{display:none}} summary::after{{content:"펼치기";color:var(--blue);font-size:13px;font-weight:750}} details[open] summary::after{{content:"접기"}}
.n{{display:grid;place-items:center;width:38px;height:38px;border-radius:11px;color:white;background:var(--blue);font-weight:800}}
.title strong{{display:block;font-size:19px}} .title small{{display:block;margin-top:4px;color:var(--muted)}}
.body{{padding:4px 21px 22px;border-top:1px solid var(--line);overflow-x:auto}} p{{line-height:1.75}}
table{{width:100%;min-width:620px;border-collapse:collapse;margin:16px 0;font-size:14px}} th,td{{padding:11px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;line-height:1.5}} th{{background:#f8fafc}}
code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}} p code,li code,td code,summary code{{overflow-wrap:anywhere;word-break:break-word}} pre{{overflow:auto;padding:16px;border-radius:11px;color:#e6edf7;background:#101827;font-size:12px;line-height:1.6}}
.pass{{color:var(--green);font-weight:850}} .approval{{color:var(--amber);font-weight:850}} .note{{padding:13px 15px;border-radius:11px;background:#eef4ff}}
.mobile-table-note{{display:none;margin:8px 0;color:var(--muted);font-size:13px}}
.flow{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:16px 0}} .flow div{{padding:15px;border-radius:13px;background:#f5f7fb;line-height:1.55}} .flow b{{display:block;color:var(--blue);margin-bottom:5px}}
.subhead{{margin:26px 0 8px;font-size:17px}} .warning{{padding:15px;border-left:4px solid var(--amber);border-radius:10px;background:#fff7ed;line-height:1.7}}
.evidence{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:14px 0}} .evidence>div{{min-width:0;padding:15px;border:1px solid var(--line);border-radius:13px;background:#fbfcfe}}
.evidence h4{{margin:0 0 10px}} .diff-add{{display:block;color:#b7f7d2;background:#123b2b;padding:2px 8px}} .label{{display:inline-flex;padding:4px 8px;border-radius:999px;font-size:12px;font-weight:800;background:#e8efff;color:var(--blue)}}
.term-ok{{color:#b7f7d2}} .term-conflict{{display:block;margin:3px -6px;padding:2px 6px;color:#ffd4d2;background:#5d2020;font-weight:800}}
.conflict-line{{display:block;margin:0 -6px;padding:1px 6px;background:#5d2020;color:#ffd4d2;font-weight:800}}
.conflict-structure{{margin:16px 0;padding:18px;border:2px solid #f0a35f;border-radius:16px;background:#fff9f3}}
.conflict-structure h4{{margin:0 0 8px;color:#8f3608}} .conflict-structure p{{margin:8px 0 12px}}
.conflict-structure pre{{margin:10px 0;background:#111827}} .conflict-structure .source-note{{font-size:14px;color:#4b5563}}
.tool-output{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:14px 0}} .tool-output>div{{padding:14px;border:1px solid var(--line);border-radius:12px;background:#f8fafc;line-height:1.6}} .tool-output b{{display:block;margin-bottom:5px;color:var(--blue)}}
.mini{{margin:10px 0;border-radius:13px;box-shadow:none}} .mini summary{{grid-template-columns:minmax(0,1fr) auto;padding:14px 16px}} .mini .body{{padding:14px 16px}}
.artifact-links{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}} .artifact-links a{{padding:8px 11px;border:1px solid #b8c8ee;border-radius:9px;color:var(--blue);background:#f7f9ff;text-decoration:none;font-weight:700;font-size:13px}}
.steps{{display:grid;gap:9px;margin:14px 0}} .steps div{{display:grid;grid-template-columns:28px minmax(0,1fr);gap:10px;align-items:start;padding:12px;border-radius:12px;background:#f7f9fc;line-height:1.65}} .steps b{{display:grid;place-items:center;width:25px;height:25px;border-radius:8px;background:var(--blue);color:white}}
.status-ok{{color:var(--green);font-weight:850}} .status-part{{color:var(--amber);font-weight:850}} .status-no{{color:#b42318;font-weight:850}}
@media(max-width:720px){{main{{width:min(100% - 18px,1100px);margin-top:9px}}.guide-pagination{{grid-template-columns:1fr 1fr}}.guide-page-current{{grid-column:1 / -1;grid-row:1}}.hero{{padding:24px;border-radius:18px}}.page-scope,.flow,.evidence,.tool-output{{grid-template-columns:1fr}}summary{{padding:16px}}.mobile-table-note{{display:block}}}}
</style>
</head>
<body><main>
{pagination}
<section class="hero">
  <h1>1.13.0 → 1.13.1 코드 업그레이드 연습</h1>
  <p>BANK-OM별 충돌을 분리해 보기 위해 공식 1.13.1 위에 커밋을 하나씩 적용하고 소스 검사를 수행한 결과입니다.</p>
  <div class="chips"><span>공식 변경 834개 파일</span><span>번역 JSON 18개 충돌</span><span>소스 검사 8종 PASS</span><span>Contract test 7개 SKIP</span><span>전체 build 미실행</span></div>
</section>
<section class="page-scope" aria-label="이 페이지가 답하는 질문과 범위">
  <div><strong>이 페이지가 답하는 질문</strong><p>커밋별 재적용 진단에서 어떤 충돌이 발생했고 검사기로 어디까지 확인했는가?</p></div>
  <div><strong>여기서 답하지 않는 것</strong><p>기본 운영 방식인 vendor-merge 전체와 행내 배포 완료 여부는 아직 검증하지 않았습니다.</p></div>
  <div><strong>읽고 나면</strong><p>완료·미완료를 구분하고, 필요한 경우 부록의 과거 참고 코드 검사와 비교합니다.</p></div>
</section>
<p class="internal-scope"><strong>이번 연습에만 사용한 방법:</strong> commit별 재적용과 JSON 충돌 보조 도구는 BANK-OM별 충돌을 분리해 보기 위해 사용했습니다. OpenMetadata 공식 업그레이드 기능이나 확정된 행내 운영 절차가 아닙니다.</p>
<section class="summary">
  <strong>결론:</strong> 커밋별 재적용으로 만든 후보에서 BANK-OM-001~007의 소스 범위는 확인했습니다.
  그러나 실제 vendor-merge 기록, 전체 build, Contract test 7개, 담당자 승인과 배포 검증은 남아 있습니다.
</section>
<p class="mobile-table-note">작은 화면에서는 표를 좌우로 밀어 모든 열을 확인하세요.</p>

<details open><summary><span class="n">1</span><span class="title"><strong>업그레이드 전 영향 확인</strong><small>공식 변경과 upgrade_watch 비교</small></span></summary>
<div class="body">
  <p><strong>Manifest</strong>는 BANK-OM별 변경 경로, 반드시 유지할 구현 경로, 공식 업그레이드 때 확인할 경로와 연결 test를 기록한 커스터마이징 등록 문서입니다.</p>
  <p><strong>공식 변경 영향 확인 검사(upgrade-watch, T42)</strong>가 Git으로 공식 1.13.0→1.13.1의 변경 경로 834개를 구하고, 각 BANK-OM Manifest의 <code>upgrade_watch.paths</code>와 비교했습니다. 7개 BANK-OM 모두 겹치는 경로가 있어 <span class="approval">APPROVAL</span>이 나왔습니다.</p>
  <div class="flow"><div><b>입력 1</b>공식 버전 사이에서 바뀐 834개 경로</div><div><b>입력 2</b>Manifest의 BANK-OM별 watch 경로</div><div><b>비교</b>두 목록의 같은 경로 찾기</div><div><b>결과</b>7개 ID 모두 검토 필요</div></div>
  <p class="note"><strong>APPROVAL의 뜻:</strong> 실패나 충돌 확정이 아니라, 공식 버전이 관련 경로를 바꿨으므로 커스터마이징을 적용하기 전에 담당자가 영향 내용을 확인하라는 뜻입니다.</p>
  <table><thead><tr><th>BANK-OM</th><th>변경된 감시 경로</th><th>대표 경로</th></tr></thead><tbody>
    <tr><td>001</td><td>22개</td><td>Entity.java</td></tr><tr><td>002</td><td>23개</td><td>Entity.java</td></tr>
    <tr><td>003</td><td>19개</td><td>번역 JSON</td></tr><tr><td>004</td><td>20개</td><td>SchemaTable.component.tsx</td></tr>
    <tr><td>005</td><td>1개</td><td>package.json</td></tr><tr><td>006</td><td>4개</td><td>ServiceIconUtils.ts</td></tr>
    <tr><td>007</td><td>1개</td><td>ServiceIconUtils.ts</td></tr>
  </tbody></table>
  <p class="note"><strong>어떤 코드끼리 비교했나?</strong> 이 단계는 커스터마이징이 없는 공식 1.13.0과 공식 1.13.1의 Git 변경 경로를 비교합니다. 행내에서는 공식 코드만 담은 <code>patch/om-1.13.0</code>과 <code>patch/om-1.13.1</code>을 비교해도 같습니다. <code>custom/...</code> branch는 영향 검토 후 BANK-OM 재적용과 소스 검사에서 별도로 확인합니다.</p>
  <h3 class="subhead">watch 경로는 어떻게 등록됐나?</h3>
  <table><thead><tr><th>등록 내용</th><th>이번 자료의 방식</th><th>한계</th></tr></thead><tbody>
    <tr><td>BANK-OM commit이 실제 변경한 경로</td><td><span class="status-ok">Manifest 생성기가 Git에서 자동 포함</span></td><td>파일 관계의 의미까지 판단하는 것은 아님</td></tr>
    <tr><td>새 공식 버전의 변경 파일을 커스터마이징 코드가 직접 참조</td><td><span class="status-ok">검사기가 watch 후보와 참조 근거 제시</span></td><td>담당자 확인 후 Manifest에 반영</td></tr>
    <tr><td>간접 호출·런타임 설정 등 이름이 드러나지 않는 의존 관계</td><td><span class="status-part">담당자가 직접 등록</span></td><td>코드 이름 비교만으로는 찾을 수 없음</td></tr>
  </tbody></table>
  <p>실제 변경 경로 자동 포함과 직접 참조 후보 제시는 현재 동작합니다. 후보는 자동으로 Manifest를 수정하지 않으며, 간접 의존 관계는 담당자가 확인해 등록합니다.</p>
</div></details>

<details open><summary><span class="n">2</span><span class="title"><strong>branch 생성</strong><small>공식 코드와 커스터마이징 적용 코드를 분리</small></span></summary>
<div class="body">
  <div class="flow"><div><b>공식 tag</b>1.13.1-release</div><div><b>patch branch</b>patch/om-1.13.1</div><div><b>custom branch</b>custom/om-1.13.1</div><div><b>검사 대상</b>dee330ebd5...</div></div>
  <pre><code>git worktree add -b patch/om-1.13.1 ../om-temp-1.13.1-upgrade 1.13.1-release
git -C ../om-temp-1.13.1-upgrade switch -c custom/om-1.13.1</code></pre>
  <p><strong><code>dee330ebd5...</code>는 무엇인가?</strong> 공식 commit이나 BANK-OM ID가 아닙니다. 공식 1.13.1 위에 BANK-OM-001~007의 8개 commit을 모두 적용한 <code>custom/om-1.13.1</code> branch의 마지막 Git commit SHA입니다.</p>
  <div class="flow"><div><b>공식 시작점</b><code>afcb2d2...</code><br>공식 1.13.1</div><div><b>순차 적용</b>BANK-OM-001~006</div><div><b>마지막 기능</b>BANK-OM-007과 후속 보완</div><div><b>최종 코드 상태</b><code>dee330ebd5...</code><br>검사기가 고정한 대상</div></div>
  <p class="note">검사기는 이 SHA를 입력으로 받아 “그 시점의 전체 코드와 Git 이력”을 검사합니다. 이후 commit이 하나라도 추가되면 코드 상태가 달라지므로 다시 검사해야 합니다.</p>
  <p class="warning"><strong>운영 전략과 이번 후보 생성 방식은 다릅니다.</strong> 저장된 검사 결과에는 <code>integration_strategy: vendor-merge</code>가 기록됐지만, 실제 후보는 아래의 커밋별 재적용으로 만들었습니다. 따라서 공식 1.13.1 포함 관계는 확인했어도 실제 vendor branch 병합 기록과 충돌 해결 증거까지 검증한 것은 아닙니다. 이 후보를 vendor-merge 운영경로 통과로 해석하면 안 됩니다.</p>
  <p class="note">두 branch는 현재 로컬에만 있고 GitHub에는 아직 push하지 않았습니다.</p>
</div></details>

<details open><summary><span class="n">3</span><span class="title"><strong>커스터마이징 적용과 충돌 해결</strong><small>실제 커밋별 결과</small></span></summary>
<div class="body">
  <h3 class="subhead">먼저, BANK-OM별 충돌을 분리해 확인한 방법</h3>
  <p>이 연습에서는 어느 BANK-OM에서 충돌하는지 바로 구분하려고 1.13.0의 기능별 commit을 공식 1.13.1 위에 하나씩 적용했습니다. 실제 명령은 <code>git cherry-pick &lt;BANK-OM commit SHA&gt;</code>였지만, 이 문서에서는 이해하기 쉽게 <strong>BANK-OM 변경 적용</strong>이라고 부릅니다.</p>
  <div class="flow"><div><b>이전 버전</b>1.13.0의 BANK-OM commit</div><div><b>이번 진단 방법</b>공식 1.13.1에 commit별 적용</div><div><b>충돌 없음</b>해당 BANK-OM 적용 완료</div><div><b>충돌 발생</b>Git이 멈추고 해결 대기</div></div>
  <p class="note"><strong>왜 cherry-pick을 썼나?</strong> 충돌을 만들기 위해 필요한 명령이라서가 아니라, 충돌을 BANK-OM ID별로 분리해 기록하기 쉬웠기 때문입니다. branch merge나 rebase도 같은 코드 구간이 겹치면 충돌할 수 있습니다. 따라서 아래는 commit별 진단 결과이며 vendor-merge 운영경로 전체 결과가 아닙니다.</p>
  <table><thead><tr><th>BANK-OM</th><th>1.13.1 commit</th><th>실제 충돌</th><th>처리</th></tr></thead><tbody>{conflict_rows}</tbody></table>
  <p>001~004는 각각 번역 JSON 18개에서 충돌한 것으로 기록됐습니다. BANK-OM-001은 18개 상세 경로까지 보관했지만 002~004는 건수만 보관했으므로, 네 차례의 파일 목록이 완전히 같다고 단정하지 않습니다.</p>

  <h3 class="subhead">1. 실제로 충돌이 발생한 순간</h3>
  <p>BANK-OM-001의 1.13.0 변경 <code>4df83b311f</code>를 공식 1.13.1에 하나의 기능 단위로 적용했습니다. 실제 명령은 <code>git cherry-pick 4df83b311f</code>였고, Git이 아래 지점에서 자동 적용을 중단했습니다.</p>
  <pre><code><span class="term-ok">Auto-merging .../Entity.java
Auto-merging .../CollectionDAO.java</span>
Auto-merging .../languages/ko-kr.json
<span class="term-conflict">CONFLICT (content): Merge conflict in .../languages/ko-kr.json
error: could not apply 4df83b311f... add InstanceCode customization</span>

$ git diff --name-only --diff-filter=U | wc -l
18</code></pre>
  <p><code>Entity.java</code>와 <code>CollectionDAO.java</code>는 자동 병합됐지만, 번역 JSON 18개는 Git이 자동으로 결정하지 못해 적용이 중단됐습니다.</p>
  <p><strong>왜 서로 다른 번역 항목인데 충돌했나?</strong> 두 변경 모두 공식 1.13.0에서 출발했습니다. 공식 1.13.1은 JSON 파일의 형식과 항목 배치를 크게 바꾸고 공식 번역 항목도 변경했습니다. BANK-OM-001은 1.13.0의 기존 형식을 유지한 채 같은 JSON 객체에 행내 번역 항목 9개를 추가했습니다. Git은 JSON의 의미가 아니라 줄 단위 차이를 계산하므로 충돌 구간의 두 결과를 자동으로 조립하지 못했습니다.</p>
  <div class="flow">
    <div><b>공통 기준</b>공식 1.13.0<br>행내 번역 없음</div>
    <div><b>공식 쪽 결과</b>1.13.1<br>파일 형식·배치와 공식 항목 변경</div>
    <div><b>BANK 쪽 결과</b>BANK-OM-001<br>1.13.0 형식에 행내 항목 9개 추가</div>
    <div><b>Git 판단</b>파일의 큰 충돌 구간을 줄 단위로 조립할 수 없음<br>자동 병합 중단</div>
  </div>
  <p class="note">항목 이름별로 다시 비교한 결과 공식 1.13.1과 BANK-OM-001이 동시에 바꾼 동일 항목은 0개였습니다. 즉, 같은 번역 값을 서로 다르게 고친 충돌이 아닙니다. 파일 형식과 항목 배치가 크게 달라져 Git의 줄 단위 자동 병합이 실패한 충돌입니다.</p>

  <div class="conflict-structure">
    <h4>Git이 충돌 파일에 실제로 남긴 구조</h4>
    <p><strong>HEAD는 현재 작업 branch의 코드</strong>를 뜻하며, 이번 실행에서는 공식 1.13.1입니다. 아래 두 영역은 같은 줄의 왼쪽·오른쪽 코드가 아니라, Git이 한 파일 안에서 자동으로 합치지 못한 <strong>두 개의 큰 충돌 블록</strong>입니다.</p>
    <pre><code><span class="conflict-line">&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD</span>
[공식 1.13.1 쪽 충돌 내용 약 2,373줄]
<span class="conflict-line">=======</span>
[공식 1.13.0 형식에 BANK-OM-001을 추가한 쪽 충돌 내용 약 3,178줄]
<span class="conflict-line">&gt;&gt;&gt;&gt;&gt;&gt;&gt; 4df83b311f</span></code></pre>
    <p class="source-note">실제 원문은 6,614행입니다. 충돌 표시는 2~5,555행에 있고, 1행과 5,556~6,614행은 Git이 자동으로 맞춘 영역입니다.</p>
    <p class="note">BANK 쪽 충돌 내용이 약 805줄 더 긴 주된 이유는 행내 항목을 805줄 추가했기 때문이 아니라 1.13.0의 더 긴 기존 형식을 유지했기 때문입니다. 실제 BANK-OM-001 추가는 9개 항목입니다.</p>
  </div>

  <h3 class="subhead">2. 충돌을 해결한 결과</h3>
  <p>위 충돌 블록 중 한쪽만 선택하면 공식 변경이나 BANK-OM 변경 중 하나를 잃을 수 있습니다. 공식 1.13.1의 번역과 형식을 유지한 뒤 BANK-OM-001의 새 항목 9개만 추가했습니다. 실제 위치는 <code>label</code> 7개와 <code>message</code> 2개로 나뉩니다.</p>
  <div class="conflict-structure">
      <h4><span class="label">해결 후</span> 공식 형식 + BANK-OM 항목</h4>
      <pre><code>"label": {{
        ... 공식 1.13.1 번역 유지 ...
<span class="diff-add">+ "code-group": "Code Group"</span>
<span class="diff-add">+ "code-name": "Code Name"</span>
<span class="diff-add">+ "code-value": "Code Value"</span>
<span class="diff-add">+ "instance-code": "인스턴스 코드"</span>
<span class="diff-add">+ "instance-code-lowercase-plural": "인스턴스 코드"</span>
<span class="diff-add">+ "instance-code-plural": "인스턴스 코드"</span>
<span class="diff-add">+ "sort-order": "Sort Order"</span>
}}

"message": {{
        ... 공식 1.13.1 번역 유지 ...
<span class="diff-add">+ "instance-code-description": "Manage common/reference codes..."</span>
<span class="diff-add">+ "instance-code-group-description": "The code group contains..."</span>
}}</code></pre>
  </div>
  <details class="mini"><summary><span class="title"><strong>실제 해결 diff 전체 보기</strong><small>공식 1.13.1과 해결 commit 83b1e0ac7d 비교 · 43줄</small></span></summary>
    <div class="body"><pre><code>{resolution_diff}</code></pre></div>
  </details>
  <p class="note"><strong>해결 결과:</strong> 공식 1.13.1의 번역과 형식을 유지하면서 BANK-OM-001의 9개 항목도 남겼고, 새 commit <code>83b1e0ac7d</code>에 기록했습니다.</p>

  <h3 class="subhead">3. 실제로 사용한 JSON 충돌 보조 도구</h3>
  <p><code>harness/tools/resolve_nonoverlapping_json_conflicts.py</code>라는 실제 Python 도구가 있습니다. 검사기 전체의 필수 단계가 아니라, <strong>Git이 JSON 충돌로 멈췄을 때만 실행하는 제한된 보조 도구</strong>입니다.</p>
  <table><thead><tr><th>입력</th><th>이번 사례의 의미</th><th>사용 목적</th></tr></thead><tbody>
    <tr><td><code>stage 1</code></td><td>공식 1.13.0과 BANK-OM 변경이 갈라지기 전 공통 JSON</td><td>양쪽이 무엇을 바꿨는지 계산하는 기준</td></tr>
    <tr><td><code>stage 2</code></td><td>지금 유지해야 할 공식 1.13.1 JSON</td><td>해결 파일의 기본 내용</td></tr>
    <tr><td><code>stage 3</code></td><td>적용하려는 BANK-OM-001 commit의 JSON</td><td>다시 추가할 BANK-OM 변경 계산</td></tr>
  </tbody></table>
  <p>도구는 세 JSON에서 <strong>실제 값을 담는 항목별로</strong> 변경 여부를 비교합니다. 예를 들어 <code>label</code> 안의 <code>instance-code</code>는 <code>label.instance-code</code>라는 한 항목으로 구분합니다. 이는 사용자가 별도로 입력하는 설정이 아니라 도구 내부의 비교 방법입니다.</p>
  <div class="tool-output">
    <div><b>자동 처리</b>공식과 BANK-OM이 서로 다른 JSON 항목을 바꾼 경우, 공식 JSON에 BANK-OM 항목을 추가</div>
    <div><b>즉시 중단</b>양쪽이 같은 JSON 항목을 바꿨거나 JSON 이외의 파일이 충돌한 경우</div>
    <div><b>사람이 할 일</b>수정된 JSON 확인 후 <code>git add</code>와 <code>git cherry-pick --continue</code></div>
  </div>
  <pre><code>./.venv/bin/python harness/tools/resolve_nonoverlapping_json_conflicts.py \
  --repo ../om-temp-1.13.1-upgrade

resolved .../languages/ko-kr.json: BANK-OM leaf changes=9</code></pre>
  <p class="note"><strong>도구가 실제로 남기는 것:</strong> 충돌 난 JSON 파일을 작업 branch에서 수정하고 터미널에 파일별 적용 건수를 출력합니다. 출력의 <code>leaf changes=9</code>는 “최종 값을 담는 JSON 항목 9개”라는 내부 표현입니다. 현재 도구는 별도 결과 보고서, 승인 파일, <code>plan.json</code>을 만들지 않습니다.</p>
  <p class="warning"><strong>현재 운영 상태:</strong> 이 도구와 “같은 JSON 항목이 겹치지 않을 때만 합친다”는 기준은 이번 업그레이드 연습을 위해 구현했습니다. OpenMetadata의 기존 기능도, 확정된 행내 승인 정책도 아닙니다.</p>
  <details class="mini"><summary><span class="title"><strong>충돌 재현 증거 자료 보기</strong><small>도구의 자동 보고서가 아니라 이번 재현을 위해 별도 보관한 자료</small></span></summary>
    <div class="body">
      <p>아래 파일은 보조 도구의 자동 산출물이 아닙니다. 이번 충돌이 실제로 어떻게 발생했고 어떻게 해결됐는지 검토할 수 있도록 별도로 저장했습니다.</p>
      <div class="artifact-links">
        <a href="../../harness/registrations/om-temp-1.13.1/conflict-evidence/BANK-OM-001_ko-kr_full_conflict.txt" target="_blank">전체 충돌 원문</a>
        <a href="../../harness/registrations/om-temp-1.13.1/conflict-evidence/BANK-OM-001_ko-kr_resolution.diff" target="_blank">해결 diff 전체</a>
        <a href="../../harness/registrations/om-temp-1.13.1/conflict-evidence/BANK-OM-001_ko-kr_resolved.json" target="_blank">해결된 JSON 전체</a>
        <a href="../../harness/registrations/om-temp-1.13.1/conflict-evidence/BANK-OM-001_ko-kr_capture.json" target="_blank">ID·commit·18개 경로 기록</a>
      </div>
      <p class="source-note">저장소 경로: <code>harness/registrations/om-temp-1.13.1/conflict-evidence/</code>. HTML만 따로 복사하면 위 상대 링크가 열리지 않으므로 공유 묶음에는 이 폴더를 함께 포함해야 합니다.</p>
    </div>
  </details>

  <h3 class="subhead">현재 Git 로그에서 BANK-OM ID는 어떻게 찾나?</h3>
  <p>현재 Git 원문은 <code>error: could not apply 4df83b311f...</code>처럼 source commit SHA만 보여주고 <code>BANK-OM-001</code>은 바로 표시하지 않습니다. commit 본문의 <code>Customization-ID: BANK-OM-001</code>을 한 번 더 조회해야 하므로 운영 로그로는 불친절합니다.</p>
  <div class="evidence">
    <div><h4>현재 로그</h4><pre><code>error: could not apply 4df83b311f...
add InstanceCode customization</code></pre><p>commit SHA를 다시 조회해야 ID를 알 수 있습니다.</p></div>
    <div><h4>개선할 로그</h4><pre><code>[BANK-OM-001] APPLY source=4df83b311f
[BANK-OM-001] CONFLICT files=18
[BANK-OM-001] RESOLVED result=83b1e0ac7d</code></pre><p>적용 명령이 commit trailer를 읽어 ID를 모든 로그와 결과 JSON에 붙입니다.</p></div>
  </div>
  <p class="warning"><strong>현재 상태:</strong> commit과 ID의 연결은 결과 파일에 기록했지만, 실제 적용 명령의 모든 로그에 ID를 자동 표시하는 wrapper는 아직 추가 개발 대상입니다.</p>

  <h3 class="subhead">4. 정식 운영 전에 추가할 승인 기록</h3>
  <p class="warning"><strong>현재 미구현:</strong> 보조 도구는 충돌 파일을 수정하지만, 누가 비교 결과를 확인하고 해결을 승인했는지 별도 파일에 기록하지 않습니다. 아래 절차와 파일은 추가 개발 항목입니다.</p>
  <div class="steps">
    <div><b>1</b><span><strong>비교만 수행:</strong> 공식 변경, BANK-OM 변경, 동일 항목을 <code>plan.json</code>으로 출력하고 아직 코드는 수정하지 않습니다.</span></div>
    <div><b>2</b><span><strong>담당자 선택:</strong> 기능 담당자가 <code>자동 병합 승인</code>, <code>수동 해결</code>, <code>적용 중단</code> 중 하나를 선택합니다.</span></div>
    <div><b>3</b><span><strong>승인 기록:</strong> 승인자, BANK-OM ID, 공식 target SHA, source commit SHA, 선택 방법과 시각을 <code>approval.yaml</code>에 남깁니다.</span></div>
    <div><b>4</b><span><strong>승인 후 적용:</strong> 승인 파일과 비교 계획의 digest가 일치할 때만 해결 도구가 코드를 수정합니다.</span></div>
    <div><b>5</b><span><strong>자동 차단:</strong> 동일 JSON 항목이 겹치거나 JSON 외 코드가 충돌하면 <span class="status-no">BLOCK</span>하고 코드 담당자가 수동 해결합니다. BLOCK은 자동 진행을 멈추고 사람이 원인을 확인해야 한다는 판정입니다.</span></div>
    <div><b>6</b><span><strong>적용 후 재검사:</strong> Manifest 범위, build, Contract test를 실행하고 결과에 승인 기록을 연결합니다.</span></div>
  </div>
  <pre><code>customization_id: BANK-OM-001
target_sha: afcb2d2...
source_commit: 4df83b311f...
decision: approve_non_overlapping_json
approved_by: 담당자 사번 또는 계정
approved_at: 승인 시각
plan_digest: sha256:...</code></pre>
  <p>정식 운영 전 추가 개발: <strong>① dry-run plan 생성 ② 세 가지 선택 입력 ③ 승인 파일 검증 ④ ID 포함 로그 ⑤ BLOCK 결과와 재검사 연결</strong></p>
</div></details>

<details><summary><span class="n">4</span><span class="title"><strong>1.13.1 기준자료 생성</strong><small>버전별 SHA와 diff를 다시 고정</small></span></summary>
<div class="body">
  <p>업무 기준인 Manifest와 Contract는 재사용했습니다. 공식 SHA, 검사 대상 SHA, 전체 변경 목록, 공용 경로와 정책 SHA는 1.13.1 기준으로 다시 생성했습니다.</p>
  <table><thead><tr><th>자료</th><th>실제 결과</th></tr></thead><tbody>
    <tr><td>Manifest / Registry</td><td>7개 / 7개 ID</td></tr><tr><td>Contract</td><td>7개, 필수 Python test 9개</td></tr>
    <tr><td>전체 변경 경로</td><td>111개</td></tr><tr><td>공용 경로</td><td>37개</td></tr>
  </tbody></table>
</div></details>

<details open><summary><span class="n">5</span><span class="title"><strong>실제 소스 검사 결과</strong><small>등록자료와 1.13.1 코드 비교</small></span></summary>
<div class="body">
  <table><thead><tr><th>검사명</th><th>확인 내용</th><th>결과</th></tr></thead><tbody>
    <tr><td>공식 기준 이력 포함</td><td>공식 1.13.1에서 시작했는지</td><td class="pass">PASS</td></tr>
    <tr><td>커스터마이징 생존</td><td>핵심 파일·Contract 연결</td><td class="pass">PASS</td></tr>
    <tr><td>필수 테스트 코드 존재</td><td>Python test 파일·함수</td><td class="pass">PASS</td></tr>
    <tr><td>커밋 작성 규칙</td><td>커밋별 BANK-OM ID</td><td class="pass">PASS</td></tr>
    <tr><td>ID 연결 규칙</td><td>미등록·잘못된 후속 커밋</td><td class="pass">PASS</td></tr>
    <tr><td>변경 범위</td><td>Manifest 밖 변경</td><td class="pass">PASS</td></tr>
    <tr><td>민감 경로</td><td>보안·설정·DB 경로 정책</td><td class="pass">PASS</td></tr>
    <tr><td>커밋별 실제 경로 일치</td><td>실제 변경과 Manifest 목록</td><td class="pass">PASS</td></tr>
    <tr><td>운영 통합 방식 일치</td><td>실제 vendor-merge 기록과 충돌 해결 증거</td><td class="status-no">NOT VERIFIED</td></tr>
  </tbody></table>
  <p class="note">소스 검사 PASS는 build와 업무 동작 test 성공을 대신하지 않습니다.</p>
</div></details>

<details open><summary><span class="n">6</span><span class="title"><strong>Contract test와 build 환경</strong><small>실행 결과와 SKIP 이유</small></span></summary>
<div class="body">
  <table><thead><tr><th>구분</th><th>결과</th><th>해석</th></tr></thead><tbody>
    <tr><td>필수 Contract test</td><td><span class="pass">2 PASS</span> · 7 SKIP</td><td>Sybase·Tibero PASS, 서버·브라우저가 필요한 7개는 미실행</td></tr>
    <tr><td>추가 소스 검사</td><td class="pass">1 PASS</td><td>한글 입력 처리 코드가 남았는지 확인</td></tr>
    <tr><td>실패</td><td>0</td><td>실행된 test에서 실패 없음</td></tr>
  </tbody></table>
  <p class="note">SKIP은 성공이 아닙니다. 행내 서버와 브라우저 test URL을 준비해 7개를 다시 실행해야 합니다.</p>
  <p>전체 build는 Java Runtime·Maven·Yarn과 UI <code>node_modules</code>가 없어 시작하지 못했습니다. 코드 build 성공이나 실패 결과가 아니라, build 환경 준비가 필요한 상태입니다.</p>
</div></details>

<details open><summary><span class="n">7</span><span class="title"><strong>현재 상태와 다음 단계</strong><small>완료와 미완료를 분리</small></span></summary>
<div class="body">
  <p><strong>우리의 목적:</strong> 공식 업그레이드 후 행내 커스터마이징이 코드에 빠짐없이 적용됐고, 업무 동작까지 정상인지 확인한 뒤 배포 검토로 넘기는 것입니다.</p>
  <table><thead><tr><th>목적에 필요한 확인</th><th>현재 결과</th><th>지금 말할 수 있는 범위</th></tr></thead><tbody>
    <tr><td>공식 변경의 영향 확인</td><td class="status-ok">충족</td><td>upgrade-watch가 7개 BANK-OM을 검토 대상으로 표시</td></tr>
    <tr><td>BANK-OM별 commit 재적용</td><td class="status-ok">충족</td><td>8개 commit과 최종 SHA 확인</td></tr>
    <tr><td>실제 충돌과 해결 기록</td><td class="status-ok">충족</td><td>001~004 충돌, 18개 경로, 해결 commit과 전체 원문 보관</td></tr>
    <tr><td>Manifest와 최종 소스 일치</td><td class="status-ok">충족</td><td>사전자료 5종·소스 검사 8종 PASS</td></tr>
    <tr><td>목표 vendor-merge 절차</td><td class="status-no">미충족</td><td>후보는 커밋별 재적용으로 생성됐고 실제 merge 증거가 없음</td></tr>
    <tr><td>전체 코드 build</td><td class="status-no">미충족</td><td>Java·Maven·Yarn 환경이 없어 미실행</td></tr>
    <tr><td>실제 업무 기능 동작</td><td class="status-part">부분 충족</td><td>필수 2개 PASS, 7개는 행내 서버·브라우저가 없어 SKIP</td></tr>
    <tr><td>사람의 충돌 해결 승인</td><td class="status-no">미충족</td><td>선택·승인자·승인 시각 기록 없음</td></tr>
    <tr><td>배포 가능한 상태</td><td class="status-no">미충족</td><td>build·남은 test·승인·검증 tag 필요</td></tr>
  </tbody></table>
  <p class="note"><strong>현재 검사기로 확인 가능한 범위:</strong> 공식 변경 영향, BANK-OM commit 적용, 변경 파일 범위, 필수 구현 파일과 테스트 코드의 존재입니다. 실제 vendor-merge 수행 여부는 이번 증거로 확인되지 않았습니다.</p>
  <p class="warning"><strong>아직 증명하지 못한 범위:</strong> 전체 build 성공, 실제 화면·API 업무 동작, 사람의 승인과 배포 안전성입니다. 따라서 현재 결과는 <strong>소스 수준 업그레이드 검증 완료</strong>이지 <strong>배포 승인 완료</strong>가 아닙니다.</p>
  <p>다음에는 Java·Maven·Yarn과 행내 test URL을 준비해 build와 남은 Contract test를 수행합니다. 그와 별도로 직전 custom branch에 공식 1.13.1을 실제 merge한 후보를 만들고, merge 기록·충돌 증거·candidate lock의 전략값이 일치하는지 다시 검사해야 합니다. 이후 충돌 비교 plan과 승인 기록 기능을 추가하고 실제 Git 화면·터미널·검사 결과를 시연 문서에 추가합니다.</p>
</div></details>
<div class="guide-pagination-bottom">{pagination}</div>
</main></body></html>"""


def main() -> None:
    MD.write_text(markdown().rstrip() + "\n", encoding="utf-8")
    HTML.write_text(html_page().rstrip() + "\n", encoding="utf-8")
    print(MD)
    print(HTML)


if __name__ == "__main__":
    main()
