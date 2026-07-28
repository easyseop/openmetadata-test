#!/usr/bin/env python3
"""Render the OM_TEMP commit-to-Manifest evidence guide."""

from __future__ import annotations

import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTRATION = Path(__file__).resolve().parent
MANIFESTS = REGISTRATION / "manifests"
OUTPUT = ROOT / "docs/00-사용가이드/OM_TEMP_커밋별_Manifest_등록_가이드.md"
HTML_OUTPUT = ROOT / "docs/00-사용가이드/OM_TEMP_커밋별_Manifest_등록_가이드_미리보기.html"
ASSETS = "공유문서/assets/om-temp-manifest"


ITEMS = [
    {
        "id": "BANK-OM-001",
        "title": "기준코드(InstanceCode)",
        "commits": [
            (
                "4df83b311f1ec38156c9b992f34607b22224db85",
                "add InstanceCode customization",
                "48개",
                "001-instance-code-highlighted.png",
                "001-instance-code-original.png",
            )
        ],
        "reason": (
            "InstanceCode라는 새 데이터 유형을 정의하고, 저장·검색·API·화면 연결까지 "
            "한 번에 추가한 변경입니다. 파일은 여러 개지만 모두 InstanceCode 기능을 "
            "동작시키기 위한 한 묶음이므로 BANK-OM-001 하나로 관리합니다."
        ),
    },
    {
        "id": "BANK-OM-002",
        "title": "쿼리 리포트(QueryReport)",
        "commits": [
            (
                "68ebed4801715f0c30b8a1a614572183fa6097b8",
                "add QueryReport customization",
                "55개",
                "002-query-report-highlighted.png",
                "002-query-report-original.png",
            )
        ],
        "reason": (
            "QueryReport 데이터 유형, 저장소, API, 검색과 화면 연결을 함께 추가한 "
            "변경입니다. BANK-OM-001과 같은 공용 파일도 수정하지만, diff 안의 "
            "QUERY_REPORT 연결은 별도 업무 기능이므로 BANK-OM-002로 분리합니다."
        ),
    },
    {
        "id": "BANK-OM-003",
        "title": "데이터 검증 결과(Data Assertions)",
        "commits": [
            (
                "57ee1b3b23d644f13e0c1716f0810ddf962e5264",
                "add Data Assertions customization",
                "25개",
                "003-data-assertions-highlighted.png",
                "003-data-assertions-original.png",
            )
        ],
        "reason": (
            "데이터 검증 결과를 조회하는 전용 화면, API 호출, 경로와 메뉴를 함께 "
            "추가한 변경입니다. 이 화면 흐름을 한 기능으로 보고 BANK-OM-003으로 "
            "등록합니다."
        ),
    },
    {
        "id": "BANK-OM-004",
        "title": "은행 컬럼 확장 표시",
        "commits": [
            (
                "274f2b79b424e01537a7f2253c33aeecb43aaac4",
                "add bank column view customization",
                "33개",
                "004-bank-column-view-highlighted.png",
                "004-bank-column-view-original.png",
            )
        ],
        "reason": (
            "테이블 컬럼 화면에 은행용 표시 항목과 관련 타입·문구를 추가한 "
            "변경입니다. 화면에 보이는 결과와 이를 전달하는 타입 변경을 함께 "
            "BANK-OM-004로 관리합니다."
        ),
    },
    {
        "id": "BANK-OM-005",
        "title": "한글 입력 조합 보정",
        "commits": [
            (
                "d983f7c540d3fa1fe56ca91adef3f37374890f77",
                "fix Korean IME handling",
                "1개",
                "005-korean-ime-highlighted.png",
                "005-korean-ime-original.png",
            )
        ],
        "reason": (
            "SchemaEditor.tsx 한 파일에서 한글 조합 시작·종료 처리를 추가한 "
            "변경입니다. 변경 범위가 가장 작고 기능 경계도 분명해, 실제 diff "
            "전체가 Manifest 하나로 등록되는 대표 사례로 사용합니다."
        ),
        "full_diff": [
            "005-korean-ime-diff-part-1.png",
            "005-korean-ime-diff-part-2.png",
            "005-korean-ime-diff-part-3.png",
            "005-korean-ime-diff-part-4.png",
        ],
    },
    {
        "id": "BANK-OM-006",
        "title": "Sybase 연결 유형",
        "commits": [
            (
                "010750c514e9bbb7a765414ded3b161b1f5eb621",
                "add Sybase customization",
                "18개",
                "006-sybase-highlighted.png",
                "006-sybase-original.png",
            )
        ],
        "reason": (
            "Sybase 연결 스키마, 생성 타입, 아이콘과 연결 선택 로직을 함께 "
            "추가한 변경입니다. 하나의 DB 연결 유형을 완성하는 파일들을 "
            "BANK-OM-006으로 묶습니다."
        ),
    },
    {
        "id": "BANK-OM-007",
        "title": "Tibero 연결 유형",
        "commits": [
            (
                "62e39da8be65c3ff259802c1cd35f4b0c8baa333",
                "add Tibero customization",
                "8개",
                "007-tibero-initial-highlighted.png",
                "007-tibero-initial-original.png",
            ),
            (
                "7d19c8952612e77467b0a80d6287170d814f1de1",
                "complete Tibero service connection coverage",
                "2개",
                "007-tibero-followup-highlighted.png",
                "007-tibero-followup-original.png",
            ),
        ],
        "reason": (
            "두 커밋 모두 Tibero 연결 유형 하나를 완성합니다. 최초 8개 파일은 "
            "allowed_changed_paths에, 후속 커밋에서 처음 추가된 2개 파일은 "
            "candidate_additional_paths에 등록합니다. Git commit SHA는 두 개지만 "
            "업무 기능 ID와 Manifest는 BANK-OM-007 하나입니다."
        ),
    },
]


def manifest_text(customization_id: str) -> str:
    return (MANIFESTS / f"{customization_id}.yaml").read_text(encoding="utf-8").rstrip()


def render() -> str:
    lines = [
        "# OM_TEMP 커밋별 Manifest 등록 가이드",
        "",
        "> 대상 코드: `easyseop/OM_TEMP`의 `custom/om-1.13.0`  ",
        "> Manifest 위치: `easyseop/openmetadata-test/harness/registrations/om-temp-1.13.0/manifests/`",
        "",
        "## 이 자료가 필요한 이유",
        "",
        "OpenMetadata를 업그레이드한 뒤에도 각 커스터마이징이 빠지지 않았는지 "
        "검사하려면, 실제 코드 변경과 검사 기준을 BANK-OM 기능별로 연결해야 합니다. "
        "이 자료는 실제 Git commit에서 확인한 변경 파일을 어떤 Manifest에 "
        "등록했는지 보여줍니다.",
        "",
        "## 먼저 구분할 두 식별값",
        "",
        "| 이름 | 의미 | 이 문서에서의 예 |",
        "|---|---|---|",
        "| BANK-OM ID | 사람이 발급하는 업무 기능 번호 | `BANK-OM-005` |",
        "| Git commit SHA | Git이 한 번의 코드 저장에 자동 부여하는 값 | `d983f7c...` |",
        "",
        "Manifest는 **BANK-OM ID마다 한 파일**을 만듭니다. 같은 기능을 후속 보완하면 "
        "BANK-OM-007처럼 Git commit SHA는 여러 개가 될 수 있지만 Manifest는 하나입니다.",
        "",
        "## 이 자료를 보는 순서",
        "",
        "1. 상위 펼치기에서 BANK-OM 기능을 선택합니다.",
        "2. 강조 캡처에서 Git commit SHA, 커밋 제목, Customization-ID를 확인합니다.",
        "3. 기능 단위로 묶은 이유를 읽습니다.",
        "4. 하위 펼치기에서 원본 캡처와 현재 생성된 Manifest 초안 전체를 확인합니다.",
        "",
        "강조 캡처는 위치를 빠르게 찾기 위한 **설명용 사본**입니다. "
        "GitHub 화면 자체를 확인해야 할 때는 같은 항목의 **원본 캡처** 또는 "
        "GitHub commit 링크를 사용합니다.",
        "",
        "## 실제 커밋과 Manifest",
        "",
    ]

    for item in ITEMS:
        customization_id = item["id"]
        lines.extend(
            [
                "<details>",
                f"<summary><strong>{customization_id} · {item['title']}</strong></summary>",
                "",
            ]
        )
        for index, commit in enumerate(item["commits"], start=1):
            sha, title, file_count, highlighted, original = commit
            label = "최초 커밋" if len(item["commits"]) > 1 and index == 1 else ""
            if len(item["commits"]) > 1 and index == 2:
                label = "후속 보완 커밋"
            heading = f"### {label}" if label else "### 실제 GitHub 커밋"
            lines.extend(
                [
                    heading,
                    "",
                    f"- Git commit SHA: `{sha}`",
                    f"- 커밋 제목: `{title}`",
                    f"- 이 커밋에서 변경한 파일: {file_count}",
                    f"- [GitHub에서 실제 커밋 열기](https://github.com/easyseop/OM_TEMP/commit/{sha})",
                    "",
                    f"![{customization_id} {label or '커밋'} 강조 캡처]"
                    f"({ASSETS}/commit-messages/{highlighted})",
                    "",
                    "<details>",
                    "<summary>강조 표시가 없는 원본 캡처 보기</summary>",
                    "",
                    f"![{customization_id} {label or '커밋'} 원본 캡처]"
                    f"({ASSETS}/commit-messages/{original})",
                    "",
                    "</details>",
                    "",
                ]
            )

        lines.extend(
            [
                "### 왜 하나의 BANK-OM 기능으로 보았나",
                "",
                item["reason"],
                "",
            ]
        )

        if item.get("full_diff"):
            lines.extend(
                [
                    "<details>",
                    "<summary><strong>대표 사례: 변경 코드 전체 보기</strong></summary>",
                    "",
                    "이 커밋의 변경은 `SchemaEditor.tsx` 한 파일뿐입니다. 아래 네 장은 "
                    "한 GitHub diff 화면을 위에서 아래 순서로 나눈 것으로, "
                    "초록색 줄은 추가 코드이고 빨간색 줄은 삭제 코드입니다.",
                    "",
                ]
            )
            for index, image in enumerate(item["full_diff"], start=1):
                lines.extend(
                    [
                        f"#### 전체 diff {index}/4",
                        "",
                        f"![BANK-OM-005 전체 diff {index}/4]"
                        f"({ASSETS}/bank-om-005-full-diff/{image})",
                        "",
                    ]
                )
            lines.extend(
                [
                    "이 전체 diff에서 바뀐 파일 경로는 하나이므로 Manifest의 "
                    "`allowed_changed_paths`도 한 경로입니다. 같은 파일이 한글 입력 "
                    "보정의 핵심 구현이므로 `required_changed_paths`에도 같은 경로를 "
                    "등록했습니다.",
                    "",
                    "</details>",
                    "",
                ]
            )

        lines.extend(
            [
                "<details>",
                f"<summary><strong>{customization_id} Manifest 초안 전체 보기</strong></summary>",
                "",
                "```yaml",
                manifest_text(customization_id),
                "```",
                "",
                "</details>",
                "",
                "</details>",
                "",
            ]
        )

    lines.extend(
        [
            "## Manifest 네 목록을 읽는 기준",
            "",
            "| 항목 | 이 초안에 들어간 기준 | 검사에서 쓰는 방식 |",
            "|---|---|---|",
            "| `allowed_changed_paths` | 최초 BANK-OM 커밋이 실제 변경한 모든 파일 | 목록 밖 파일을 같은 ID로 변경하면 차단하고, 목록 안 파일이 최종 후보에서 실제로 달라지지 않으면 검토를 요구 |",
            "| `required_changed_paths` | 기능이 적용됐음을 판단하는 핵심 구현 파일 | 파일이 없거나 공식 원본과 같아지면 기능이 빠진 것으로 보고 차단 |",
            "| `candidate_additional_paths` | 같은 ID의 후속 커밋에서 처음 추가된 파일 | 사전 등록 없이 확장한 변경과 승인된 후속 변경을 구분 |",
            "| `upgrade_watch.paths` | 공식 버전 변경 비교 검사(T42)가 확인할 경로 | 공식 새 버전에서 해당 경로가 바뀌면 자동 통과하지 않고 재검토를 요구 |",
            "",
            "T42는 공식 OpenMetadata의 이전 버전과 새 버전에서 지정 경로가 "
            "바뀌었는지 확인하는 검사입니다. `upgrade_watch.paths`에는 현재 T42 "
            "구현에 맞춰 해당 ID의 변경 범위 전체와 "
            "직접 수정하지 않았지만 기능이 의존하는 공식 파일을 함께 넣었습니다. "
            "따라서 watch에 있다고 해서 그 파일을 이 커밋이 반드시 수정했다는 뜻은 아닙니다.",
            "",
            "## 현재 상태",
            "",
            "- BANK-OM-001~007 Manifest 초안 7개 생성 완료",
            "- 실제 Git commit의 변경 파일 목록을 초안에 반영 완료",
            "- 현재 Manifest 스키마 및 기본 의미 검사 7개 통과",
            "- OM_TEMP 전체 코드 build, 업무 동작 test, 1.13.1 업그레이드 비교는 아직 실행 전",
            "- 따라서 이 문서의 Manifest는 **코드 기준 초안**이며 배포 승인 결과가 아님",
            "",
        ]
    )
    return "\n".join(lines)


def render_html() -> str:
    sections = []
    for item in ITEMS:
        commit_blocks = []
        for index, commit in enumerate(item["commits"], start=1):
            sha, title, file_count, highlighted, original = commit
            label = "실제 GitHub 커밋"
            if len(item["commits"]) > 1:
                label = "최초 커밋" if index == 1 else "후속 보완 커밋"
            commit_blocks.append(
                f"""
                <section class="commit">
                  <h3>{label}</h3>
                  <dl>
                    <div><dt>Git commit SHA</dt><dd><code>{sha}</code></dd></div>
                    <div><dt>커밋 제목</dt><dd><code>{html.escape(title)}</code></dd></div>
                    <div><dt>변경 파일</dt><dd>{file_count}</dd></div>
                  </dl>
                  <a class="github" href="https://github.com/easyseop/OM_TEMP/commit/{sha}">GitHub에서 실제 커밋 열기</a>
                  <img src="{ASSETS}/commit-messages/{highlighted}" alt="{item['id']} 강조 캡처">
                  <details class="sub">
                    <summary>강조 표시가 없는 원본 캡처</summary>
                    <img src="{ASSETS}/commit-messages/{original}" alt="{item['id']} 원본 캡처">
                  </details>
                </section>
                """
            )

        full_diff = ""
        if item.get("full_diff"):
            images = "".join(
                f'<figure><figcaption>전체 diff {index}/4</figcaption>'
                f'<img src="{ASSETS}/bank-om-005-full-diff/{image}" '
                f'alt="BANK-OM-005 전체 diff {index}/4"></figure>'
                for index, image in enumerate(item["full_diff"], start=1)
            )
            full_diff = f"""
              <details class="sub">
                <summary>대표 사례: 변경 코드 전체 보기</summary>
                <p><code>SchemaEditor.tsx</code> 한 파일의 GitHub diff 전체입니다.
                초록색은 추가 코드, 빨간색은 삭제 코드입니다.</p>
                <div class="diff-grid">{images}</div>
                <p>변경 파일이 하나이므로 Manifest의 <code>allowed_changed_paths</code>도
                한 경로입니다. 같은 경로를 핵심 구현인
                <code>required_changed_paths</code>로 등록했습니다.</p>
              </details>
            """

        manifest = html.escape(manifest_text(item["id"]))
        sections.append(
            f"""
            <details class="feature">
              <summary><span>{item['id']}</span><strong>{html.escape(item['title'])}</strong></summary>
              <div class="feature-body">
                {''.join(commit_blocks)}
                <section class="reason">
                  <h3>왜 하나의 BANK-OM 기능으로 보았나</h3>
                  <p>{html.escape(item['reason'])}</p>
                </section>
                {full_diff}
                <details class="sub manifest">
                  <summary>{item['id']} Manifest 초안 전체 보기</summary>
                  <pre><code>{manifest}</code></pre>
                </details>
              </div>
            </details>
            """
        )

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OM_TEMP 커밋별 Manifest 등록 가이드</title>
<style>
:root {{ --ink:#172033; --muted:#667085; --line:#d9dfeb; --blue:#2457d6; --soft:#f5f7fb; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:#eef2f7; color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans KR",sans-serif; }}
main {{ width:min(1120px,calc(100% - 32px)); margin:32px auto 72px; }}
.hero {{ padding:34px; border-radius:24px; color:white; background:linear-gradient(135deg,#172554,#2457d6); box-shadow:0 20px 55px #193b7b2e; }}
.hero h1 {{ margin:0 0 12px; font-size:clamp(28px,4vw,44px); letter-spacing:-.04em; }}
.hero p {{ margin:6px 0; color:#e5edff; line-height:1.65; }}
.status {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }}
.status span {{ padding:7px 11px; border:1px solid #ffffff42; border-radius:999px; background:#ffffff16; font-size:13px; }}
.intro {{ margin:20px 0; padding:24px; border:1px solid var(--line); border-radius:18px; background:white; }}
.intro h2 {{ margin:0 0 12px; font-size:20px; }}
.intro p {{ margin:8px 0; line-height:1.7; }}
.id-table {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:16px; }}
.id-table div {{ padding:14px; border-radius:12px; background:var(--soft); }}
.id-table strong {{ display:block; margin-bottom:5px; }}
details.feature {{ margin:12px 0; border:1px solid var(--line); border-radius:18px; background:white; overflow:hidden; box-shadow:0 5px 20px #13234a0c; }}
.feature>summary {{ display:flex; align-items:center; gap:14px; padding:20px 22px; cursor:pointer; list-style:none; }}
.feature>summary::-webkit-details-marker {{ display:none; }}
.feature>summary::after {{ content:"＋"; margin-left:auto; color:var(--blue); font-size:23px; }}
.feature[open]>summary::after {{ content:"－"; }}
.feature>summary span {{ padding:7px 10px; border-radius:9px; color:#153eaa; background:#e8efff; font:700 13px ui-monospace,monospace; }}
.feature>summary strong {{ font-size:18px; }}
.feature-body {{ padding:4px 22px 24px; border-top:1px solid var(--line); }}
.commit,.reason {{ margin-top:20px; }}
h3 {{ margin:0 0 12px; font-size:16px; }}
dl {{ display:grid; gap:8px; margin:0 0 12px; }}
dl div {{ display:grid; grid-template-columns:128px minmax(0,1fr); gap:10px; align-items:start; }}
dt {{ color:var(--muted); font-size:14px; }}
dd {{ margin:0; min-width:0; overflow-wrap:anywhere; }}
code {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
.github {{ display:inline-block; margin:2px 0 14px; color:var(--blue); font-weight:650; text-decoration:none; }}
img {{ display:block; max-width:100%; height:auto; margin:10px auto; border:1px solid var(--line); border-radius:12px; background:white; }}
.sub {{ margin-top:14px; border:1px solid var(--line); border-radius:12px; background:#fbfcfe; }}
.sub>summary {{ padding:14px 16px; cursor:pointer; font-weight:700; }}
.sub>img,.sub>p,.sub>.diff-grid,.sub>pre {{ margin:0 16px 16px; }}
.reason {{ padding:16px; border-left:4px solid var(--blue); border-radius:10px; background:#f3f6ff; }}
.reason p {{ margin:0; line-height:1.75; }}
.diff-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }}
figure {{ margin:0; }}
figcaption {{ margin:4px 0 7px; color:var(--muted); font-size:13px; font-weight:700; }}
figure img {{ margin:0; width:100%; }}
pre {{ overflow:auto; max-height:580px; padding:16px; border-radius:10px; color:#e6edf7; background:#101827; font-size:12px; line-height:1.55; }}
.foot {{ margin-top:22px; padding:20px; border-radius:16px; background:#fff7e6; border:1px solid #f1d49b; line-height:1.65; }}
@media (max-width:720px) {{
  main {{ width:min(100% - 20px,1120px); margin-top:10px; }}
  .hero {{ padding:24px; border-radius:18px; }}
  .id-table,.diff-grid {{ grid-template-columns:1fr; }}
  dl div {{ grid-template-columns:1fr; gap:2px; }}
}}
</style>
</head>
<body>
<main>
  <section class="hero">
    <h1>OM_TEMP 커밋별 Manifest 등록 가이드</h1>
    <p>실제 Git commit의 변경 파일을 BANK-OM 기능별 Manifest에 어떻게 등록했는지 확인합니다.</p>
    <p>대상: easyseop/OM_TEMP · custom/om-1.13.0</p>
    <div class="status"><span>Manifest 초안 7개</span><span>Git diff 일치 확인</span><span>스키마·기본 의미 검사 PASS</span><span>build·업그레이드 검사는 아직 실행 전</span></div>
  </section>
  <section class="intro">
    <h2>먼저 구분할 두 식별값</h2>
    <p>Manifest는 BANK-OM ID마다 한 파일을 만듭니다. 같은 기능의 후속 보완은 Git commit SHA가 여러 개여도 Manifest 하나에 연결합니다.</p>
    <div class="id-table">
      <div><strong>BANK-OM ID</strong>사람이 발급하는 업무 기능 번호</div>
      <div><strong>Git commit SHA</strong>Git이 저장된 코드 변경에 자동 부여하는 값</div>
    </div>
  </section>
  {''.join(sections)}
  <section class="foot"><strong>현재 상태:</strong> 실제 Git commit 기준 Manifest 초안과 구조 검사는 완료했습니다. OM_TEMP 전체 코드 build, 업무 동작 test, 1.13.1 업그레이드 비교와 배포 승인은 아직 완료하지 않았습니다.</section>
</main>
</body>
</html>
"""


def main() -> None:
    markdown = "\n".join(line.rstrip() for line in render().splitlines()) + "\n"
    preview = "\n".join(line.rstrip() for line in render_html().splitlines()) + "\n"
    OUTPUT.write_text(markdown, encoding="utf-8")
    HTML_OUTPUT.write_text(preview, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    print(f"wrote {HTML_OUTPUT}")


if __name__ == "__main__":
    main()
