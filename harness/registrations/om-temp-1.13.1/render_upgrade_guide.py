#!/usr/bin/env python3
"""Render the actual OM_TEMP 1.13.0 -> 1.13.1 upgrade guide."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MD = ROOT / "docs/00-사용가이드/OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드.md"
HTML = ROOT / "docs/00-사용가이드/OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드_미리보기.html"


ROWS = [
    ("BANK-OM-001", "83b1e0ac7d", "번역 JSON 18개", "각 파일의 BANK-OM 키 9개"),
    ("BANK-OM-002", "8b368af0a2", "번역 JSON 18개", "각 파일의 BANK-OM 키 11개"),
    ("BANK-OM-003", "e1d181d728", "번역 JSON 18개", "각 파일의 BANK-OM 키 5개"),
    ("BANK-OM-004", "ed870cd63d", "번역 JSON 18개", "각 파일의 BANK-OM 키 9개"),
    ("BANK-OM-005", "dfd3ad5e1c", "충돌 없음", "자동 적용"),
    ("BANK-OM-006", "15b85814f5", "충돌 없음", "자동 적용"),
    ("BANK-OM-007", "e7e4ba67b6 + dee330ebd5", "충돌 없음", "두 커밋을 순서대로 적용"),
]


def markdown() -> str:
    rows = "\n".join(f"| {a} | `{b}` | {c} | {d} |" for a, b, c, d in ROWS)
    return f"""# OM_TEMP 1.13.0 → 1.13.1 업그레이드 실행 가이드

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
git worktree add -b patch/om-1.13.1 \\
  ../om-temp-1.13.1-upgrade 1.13.1-release
git -C ../om-temp-1.13.1-upgrade switch -c custom/om-1.13.1
```

`patch/om-1.13.1`은 공식 1.13.1 코드만 보관합니다. `custom/om-1.13.1`은
그 위에 BANK-OM 커밋을 적용한 검사 대상 branch입니다. 두 branch는 현재 로컬에만
있고 GitHub에는 아직 push하지 않았습니다.

## 4. 실제 충돌과 해결

| BANK-OM | 1.13.1 적용 commit | 실제 충돌 | 처리 |
|---|---|---|---|
{rows}

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
./.venv/bin/python \\
  harness/tools/resolve_nonoverlapping_json_conflicts.py \\
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
"""


def html_page() -> str:
    conflict_rows = "".join(
        f"<tr><td>{a}</td><td><code>{b}</code></td><td>{c}</td><td>{d}</td></tr>"
        for a, b, c, d in ROWS
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OM_TEMP 1.13.0 → 1.13.1 업그레이드 실행 가이드</title>
<style>
:root{{--ink:#172033;--muted:#667085;--line:#d8dfeb;--blue:#2457d6;--green:#067647;--amber:#b54708}}
*{{box-sizing:border-box}} body{{margin:0;background:#eef2f7;color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans KR",sans-serif}}
main{{width:min(1100px,calc(100% - 28px));margin:28px auto 64px}}
.hero{{padding:34px;border-radius:24px;color:white;background:linear-gradient(135deg,#172554,#2457d6);box-shadow:0 20px 55px #193b7b2e}}
h1{{margin:0 0 12px;font-size:clamp(28px,4vw,43px);letter-spacing:-.04em}} .hero p{{margin:6px 0;color:#e5edff;line-height:1.65}}
.chips{{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}} .chips span{{padding:7px 11px;border:1px solid #ffffff42;border-radius:999px;background:#ffffff16;font-size:13px}}
.summary{{margin:18px 0;padding:22px;border:1px solid var(--line);border-radius:18px;background:white;line-height:1.7}}
details{{margin:14px 0;border:1px solid var(--line);border-radius:18px;background:white;overflow:hidden;box-shadow:0 6px 22px #13234a0d}}
summary{{display:grid;grid-template-columns:42px minmax(0,1fr) auto;gap:12px;align-items:center;padding:19px 21px;cursor:pointer;list-style:none}}
summary::-webkit-details-marker{{display:none}} summary::after{{content:"펼치기";color:var(--blue);font-size:13px;font-weight:750}} details[open] summary::after{{content:"접기"}}
.n{{display:grid;place-items:center;width:38px;height:38px;border-radius:11px;color:white;background:var(--blue);font-weight:800}}
.title strong{{display:block;font-size:19px}} .title small{{display:block;margin-top:4px;color:var(--muted)}}
.body{{padding:4px 21px 22px;border-top:1px solid var(--line);overflow-x:auto}} p{{line-height:1.75}}
table{{width:100%;min-width:620px;border-collapse:collapse;margin:16px 0;font-size:14px}} th,td{{padding:11px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;line-height:1.5}} th{{background:#f8fafc}}
code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}} pre{{overflow:auto;padding:16px;border-radius:11px;color:#e6edf7;background:#101827;font-size:12px;line-height:1.6}}
.pass{{color:var(--green);font-weight:850}} .approval{{color:var(--amber);font-weight:850}} .note{{padding:13px 15px;border-radius:11px;background:#eef4ff}}
.flow{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:16px 0}} .flow div{{padding:15px;border-radius:13px;background:#f5f7fb;line-height:1.55}} .flow b{{display:block;color:var(--blue);margin-bottom:5px}}
.subhead{{margin:26px 0 8px;font-size:17px}} .warning{{padding:15px;border-left:4px solid var(--amber);border-radius:10px;background:#fff7ed;line-height:1.7}}
.evidence{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:14px 0}} .evidence>div{{min-width:0;padding:15px;border:1px solid var(--line);border-radius:13px;background:#fbfcfe}}
.evidence h4{{margin:0 0 10px}} .diff-add{{display:block;color:#b7f7d2;background:#123b2b;padding:2px 8px}} .label{{display:inline-flex;padding:4px 8px;border-radius:999px;font-size:12px;font-weight:800;background:#e8efff;color:var(--blue)}}
@media(max-width:720px){{main{{width:min(100% - 18px,1100px);margin-top:9px}}.hero{{padding:24px;border-radius:18px}}.flow,.evidence{{grid-template-columns:1fr}}summary{{padding:16px}}}}
</style>
</head>
<body><main>
<section class="hero">
  <h1>1.13.0 → 1.13.1 실제 업그레이드</h1>
  <p>공식 1.13.1 위에 BANK-OM-001~007을 다시 적용하고 충돌 해결과 소스 검사까지 수행한 결과입니다.</p>
  <div class="chips"><span>공식 변경 834개 파일</span><span>번역 JSON 18개 충돌</span><span>등록 경로 111개</span><span>소스 검사 8종 PASS</span></div>
</section>
<section class="summary">
  <strong>결론:</strong> BANK-OM-001~007은 공식 1.13.1에 다시 적용됐고 소스 검사 8종을 통과했습니다.
  다만 전체 build, 환경이 필요한 Contract test 7개, 담당자 지정과 배포 승인은 아직 남아 있습니다.
</section>

<details open><summary><span class="n">1</span><span class="title"><strong>업그레이드 전 영향 확인</strong><small>공식 변경과 upgrade_watch 비교</small></span></summary>
<div class="body">
  <p>공식 1.13.0→1.13.1에서 834개 파일이 바뀌었고 7개 BANK-OM 모두 감시 경로가 변경돼 <span class="approval">APPROVAL</span>이 나왔습니다. 실패가 아니라 적용 전에 검토하라는 결과입니다.</p>
  <table><thead><tr><th>BANK-OM</th><th>변경된 감시 경로</th><th>대표 경로</th></tr></thead><tbody>
    <tr><td>001</td><td>22개</td><td>Entity.java</td></tr><tr><td>002</td><td>23개</td><td>Entity.java</td></tr>
    <tr><td>003</td><td>19개</td><td>번역 JSON</td></tr><tr><td>004</td><td>20개</td><td>SchemaTable.component.tsx</td></tr>
    <tr><td>005</td><td>1개</td><td>package.json</td></tr><tr><td>006</td><td>4개</td><td>ServiceIconUtils.ts</td></tr>
    <tr><td>007</td><td>1개</td><td>ServiceIconUtils.ts</td></tr>
  </tbody></table>
</div></details>

<details open><summary><span class="n">2</span><span class="title"><strong>branch 생성</strong><small>공식 코드와 커스터마이징 적용 코드를 분리</small></span></summary>
<div class="body">
  <div class="flow"><div><b>공식 tag</b>1.13.1-release</div><div><b>patch branch</b>patch/om-1.13.1</div><div><b>custom branch</b>custom/om-1.13.1</div><div><b>검사 대상</b>dee330ebd5...</div></div>
  <pre><code>git worktree add -b patch/om-1.13.1 ../om-temp-1.13.1-upgrade 1.13.1-release
git -C ../om-temp-1.13.1-upgrade switch -c custom/om-1.13.1</code></pre>
  <p class="note">두 branch는 현재 로컬에만 있고 GitHub에는 아직 push하지 않았습니다.</p>
</div></details>

<details open><summary><span class="n">3</span><span class="title"><strong>커스터마이징 적용과 충돌 해결</strong><small>실제 커밋별 결과</small></span></summary>
<div class="body">
  <table><thead><tr><th>BANK-OM</th><th>1.13.1 commit</th><th>실제 충돌</th><th>처리</th></tr></thead><tbody>{conflict_rows}</tbody></table>
  <p>001~004는 매번 같은 18개 번역 JSON에서 충돌했습니다. 72개 다른 파일이 아니라 <strong>18개 고유 파일에서 네 번 발생한 충돌</strong>입니다.</p>
  <p>leaf key는 <code>label.instance-code</code>처럼 JSON에서 실제 값을 담는 마지막 항목 이름입니다. 공식 1.13.1과 BANK-OM이 같은 leaf key를 함께 바꿨는지 검사했습니다. 겹친 키는 0개였으므로 공식 JSON을 유지하고 BANK-OM 키만 추가했습니다. 같은 키가 겹치면 자동 해결 도구가 중단됩니다.</p>
  <p class="warning"><strong>먼저 구분할 점:</strong> 이 규칙은 OpenMetadata의 기존 기능이나 확정된 행내 정책이 아니라, 이번 업그레이드 연습에서 사용한 임시 규칙입니다.</p>

  <h3 class="subhead">실제 Git 충돌 재현</h3>
  <p>BANK-OM-001의 1.13.0 commit <code>4df83b311f</code>를 공식 1.13.1에 다시 적용해 같은 충돌을 재현했습니다.</p>
  <pre><code>Auto-merging .../Entity.java
Auto-merging .../CollectionDAO.java
Auto-merging .../languages/ko-kr.json
CONFLICT (content): Merge conflict in .../languages/ko-kr.json
error: could not apply 4df83b311f... add InstanceCode customization

$ git diff --name-only --diff-filter=U | wc -l
18</code></pre>
  <p><code>Entity.java</code>와 <code>CollectionDAO.java</code>는 자동 병합됐지만, 번역 JSON 18개는 Git이 자동으로 결정하지 못해 적용이 중단됐습니다.</p>

  <div class="evidence">
    <div>
      <h4><span class="label">충돌 원인</span> 공식 1.13.1</h4>
      <p>번역 JSON 전체의 들여쓰기가 바뀌었고 공식 번역 항목도 추가됐습니다. Git은 같은 JSON 객체 안의 큰 줄 변경으로 판단했습니다.</p>
      <p><small>아래는 실제 충돌 표식을 읽기 쉽게 축약한 화면입니다.</small></p>
      <pre><code>&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD
    "label": {{ ...공식 1.13.1... }}
Git 구분 표시: =======
  "label": {{ ...BANK-OM-001... }}
&gt;&gt;&gt;&gt;&gt;&gt;&gt; 4df83b311f</code></pre>
    </div>
    <div>
      <h4><span class="label">BANK-OM-001</span> 실제 추가 항목 9개</h4>
      <pre><code><span class="diff-add">+ "code-group": "Code Group"</span>
<span class="diff-add">+ "code-name": "Code Name"</span>
<span class="diff-add">+ "code-value": "Code Value"</span>
<span class="diff-add">+ "instance-code": "인스턴스 코드"</span>
<span class="diff-add">+ "instance-code-lowercase-plural": "인스턴스 코드"</span>
<span class="diff-add">+ "instance-code-plural": "인스턴스 코드"</span>
<span class="diff-add">+ "sort-order": "Sort Order"</span>
<span class="diff-add">+ "instance-code-description": "Manage common/reference codes..."</span>
<span class="diff-add">+ "instance-code-group-description": "The code group contains..."</span></code></pre>
    </div>
  </div>
  <p class="note"><strong>해결 결과:</strong> 공식 1.13.1의 번역과 형식을 유지하면서 BANK-OM-001의 9개 항목도 남겼습니다. 결과는 새 commit <code>83b1e0ac7d</code>에 기록됐습니다.</p>
  <p>전체 재현 기록: <code>harness/registrations/om-temp-1.13.1/conflict-replay-evidence.txt</code></p>

  <h3 class="subhead">현재 해결 도구와 승인 절차의 차이</h3>
  <p class="warning"><strong>정책 확정 전:</strong> 이 해결 규칙과 도구는 OpenMetadata의 기존 기능이 아니라 이번 업그레이드 연습을 위해 추가했습니다. 은행의 정식 승인 정책으로 확정된 상태가 아닙니다.</p>
  <table><thead><tr><th>구분</th><th>현재 구현</th><th>정식 운영에 필요한 방식</th></tr></thead><tbody>
    <tr><td>실행 전 확인</td><td>담당자가 명령을 직접 실행</td><td>충돌 파일과 양쪽 변경 항목을 먼저 표시</td></tr>
    <tr><td>선택·승인</td><td>선택 화면과 승인 기록 없음</td><td>자동 병합 또는 수동 해결을 선택하고 승인자 기록</td></tr>
    <tr><td>동일 항목 겹침</td><td>파일을 쓰지 않고 즉시 중단</td><td><span class="approval">BLOCK</span> 후 담당자가 수동 결정</td></tr>
    <tr><td>JSON 외 충돌</td><td>즉시 중단</td><td><span class="approval">BLOCK</span> 후 코드 담당자가 수동 해결</td></tr>
  </tbody></table>
  <pre><code>./.venv/bin/python harness/tools/resolve_nonoverlapping_json_conflicts.py \\
  --repo ../om-temp-1.13.1-upgrade</code></pre>
  <p>정식 운영 전 추가 개발: <strong>① dry-run 비교 화면 ② 자동 병합/수동 해결 선택 ③ 승인자·commit·결과 기록 ④ BLOCK 결과 연결</strong></p>
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
  </tbody></table>
  <p class="note">소스 검사 PASS는 build와 업무 동작 test 성공을 대신하지 않습니다.</p>
</div></details>

<details><summary><span class="n">6</span><span class="title"><strong>Contract test와 build 환경</strong><small>실행 결과와 SKIP 이유</small></span></summary>
<div class="body">
  <table><thead><tr><th>구분</th><th>결과</th><th>해석</th></tr></thead><tbody>
    <tr><td>필수 Contract test</td><td><span class="pass">2 PASS</span> · 7 SKIP</td><td>Sybase·Tibero PASS, 서버·브라우저가 필요한 7개는 미실행</td></tr>
    <tr><td>추가 소스 검사</td><td class="pass">1 PASS</td><td>한글 입력 처리 코드가 남았는지 확인</td></tr>
    <tr><td>실패</td><td>0</td><td>실행된 test에서 실패 없음</td></tr>
  </tbody></table>
  <p class="note">SKIP은 성공이 아닙니다. 행내 서버와 브라우저 test URL을 준비해 7개를 다시 실행해야 합니다.</p>
  <p>전체 build는 Java Runtime·Maven·Yarn과 UI <code>node_modules</code>가 없어 시작하지 못했습니다. 코드 build 성공이나 실패 결과가 아니라, build 환경 준비가 필요한 상태입니다.</p>
</div></details>

<details><summary><span class="n">7</span><span class="title"><strong>현재 상태와 다음 단계</strong><small>완료와 미완료를 분리</small></span></summary>
<div class="body">
  <table><thead><tr><th>상태</th><th>항목</th></tr></thead><tbody>
    <tr><td class="pass">완료</td><td>1.13.1 branch 생성, BANK-OM 적용, JSON 충돌 해결, 사전자료 5종 PASS, 소스 검사 8종 PASS</td></tr>
    <tr><td class="approval">부분 완료</td><td>Contract 관련 test 3개 PASS, 환경이 필요한 필수 test 7개 SKIP</td></tr>
    <tr><td class="approval">미완료</td><td>전체 build 환경과 실행, 남은 Contract test, 담당자 지정, GitHub push, 검증 tag, 배포 승인</td></tr>
  </tbody></table>
  <p>다음에는 Java·Maven·Yarn과 행내 test URL을 준비하고, 실제 Git 화면·터미널·검사 결과를 캡처해 시연 문서에 추가합니다.</p>
</div></details>
</main></body></html>"""


def main() -> None:
    MD.write_text(markdown().rstrip() + "\n", encoding="utf-8")
    HTML.write_text(html_page().rstrip() + "\n", encoding="utf-8")
    print(MD)
    print(HTML)


if __name__ == "__main__":
    main()
