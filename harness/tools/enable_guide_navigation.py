#!/usr/bin/env python3
"""Add file://-safe previous/next navigation outside rendered preview iframes."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
PREVIEWS = (
    (
        ROOT
        / "docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-preview.html",
        None,
        ("openmetadata-phase2-verifier-table-preview.html", "검사기 원리"),
        "1 · 목적과 브랜치 전략",
    ),
    (
        ROOT
        / "docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-preview.html",
        ("openmetadata-phase1-sharing-preview.html", "목적과 브랜치 전략"),
        ("../OM_TEMP_커밋별_Manifest_등록_가이드_미리보기.html", "검사 전 사전환경 설정"),
        "2 · 검사기 원리",
    ),
    (
        ROOT
        / "docs/00-사용가이드/공유문서/openmetadata-phase3-demo-preview.html",
        (
            "../OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드_미리보기.html",
            "OM_TEMP 코드 업그레이드 연습",
        ),
        None,
        "부록 · 과거 참고 코드 검사",
    ),
)
DEFAULT = 'sandbox="allow-scripts"'
WITH_NAVIGATION = (
    'sandbox="allow-scripts allow-top-navigation-by-user-activation"'
)
START = "<!-- OUTER_GUIDE_NAV_START -->"
END = "<!-- OUTER_GUIDE_NAV_END -->"
OUTER_STYLE = """
/* file:// 미리보기에서도 동작하는 프레임 바깥 페이지 이동 */
body {
  font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo",
    "Noto Sans KR", "Segoe UI", sans-serif;
  font-weight: 400;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
.outer-guide-pagination {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  gap: 10px;
  width: min(1100px, 100%);
  margin: 0 auto 12px;
  color: #172033;
}
.outer-guide-pagination.is-bottom { margin: 12px auto 0; }
.outer-guide-pagination a,
.outer-guide-pagination span {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  padding: 11px 14px;
  border: 1px solid #d8dfeb;
  border-radius: 13px;
  color: inherit;
  background: #fff;
  text-decoration: none;
}
.outer-guide-pagination a:hover {
  border-color: #2457d6;
  box-shadow: 0 7px 20px rgb(36 87 214 / 12%);
}
.outer-guide-pagination .is-current { text-align: center; }
.outer-guide-pagination .is-next { text-align: right; }
.outer-guide-pagination .is-disabled { color: #98a2b3; background: #f8fafc; }
.outer-guide-pagination small { margin-bottom: 3px; color: #667085; font-size: 12px; }
.outer-guide-pagination strong { overflow-wrap: anywhere; }
iframe { height: calc(100vh - 10rem); min-height: 640px; }
@media (max-width: 720px) {
  .outer-guide-pagination { grid-template-columns: 1fr 1fr; }
  .outer-guide-pagination .is-current { grid-column: 1 / -1; grid-row: 1; }
  iframe { height: calc(100vh - 14rem); min-height: 560px; }
}
"""


def nav_item(
    destination: tuple[str, str] | None,
    direction: str,
) -> str:
    if destination is None:
        label = "첫 페이지" if direction == "prev" else "마지막 페이지"
        arrow = "← 이전 가이드" if direction == "prev" else "다음 가이드 →"
        return (
            f'<span class="is-disabled"><small>{arrow}</small>'
            f"<strong>{label}</strong></span>"
        )
    href, label = destination
    arrow = "← 이전 가이드" if direction == "prev" else "다음 가이드 →"
    css_class = ' class="is-next"' if direction == "next" else ""
    return (
        f'<a{css_class} href="{href}"><small>{arrow}</small>'
        f"<strong>{label}</strong></a>"
    )


def pagination(
    previous: tuple[str, str] | None,
    next_page: tuple[str, str] | None,
    current: str,
    *,
    bottom: bool,
) -> str:
    bottom_class = " is-bottom" if bottom else ""
    return (
        f"{START}\n"
        f'<nav class="outer-guide-pagination{bottom_class}" '
        'aria-label="가이드 페이지 이동">\n'
        f"  {nav_item(previous, 'prev')}\n"
        '  <span class="is-current"><small>전체 5개 중</small>'
        f"<strong>{current}</strong></span>\n"
        f"  {nav_item(next_page, 'next')}\n"
        "</nav>\n"
        f"{END}"
    )


def main() -> int:
    for preview, previous, next_page, current in PREVIEWS:
        text = preview.read_text(encoding="utf-8")
        text = re.sub(
            rf"\s*{re.escape(START)}.*?{re.escape(END)}\s*",
            "\n",
            text,
            flags=re.DOTALL,
        )
        if DEFAULT in text:
            text = text.replace(DEFAULT, WITH_NAVIGATION, 1)
        elif WITH_NAVIGATION not in text:
            raise ValueError(f"{preview}: expected preview iframe sandbox not found")
        if OUTER_STYLE.strip() not in text:
            text = text.replace("</style>", f"{OUTER_STYLE}</style>", 1)
        text = text.replace(
            "<body>",
            f"<body>\n{pagination(previous, next_page, current, bottom=False)}",
            1,
        )
        text = text.replace(
            "</body>",
            f"{pagination(previous, next_page, current, bottom=True)}\n</body>",
            1,
        )
        preview.write_text(text, encoding="utf-8")
        print(f"updated {preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
