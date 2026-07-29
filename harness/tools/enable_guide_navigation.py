#!/usr/bin/env python3
"""Allow user-clicked previous/next links to leave rendered preview iframes."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREVIEWS = (
    ROOT
    / "docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-preview.html",
    ROOT
    / "docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-preview.html",
    ROOT
    / "docs/00-사용가이드/공유문서/openmetadata-phase3-demo-preview.html",
)
DEFAULT = 'sandbox="allow-scripts"'
WITH_NAVIGATION = (
    'sandbox="allow-scripts allow-top-navigation-by-user-activation"'
)


def main() -> int:
    for preview in PREVIEWS:
        text = preview.read_text(encoding="utf-8")
        if WITH_NAVIGATION in text:
            print(f"unchanged {preview}")
            continue
        if DEFAULT not in text:
            raise ValueError(f"{preview}: expected preview iframe sandbox not found")
        preview.write_text(
            text.replace(DEFAULT, WITH_NAVIGATION, 1),
            encoding="utf-8",
        )
        print(f"updated {preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
