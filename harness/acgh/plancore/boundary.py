"""Static boundary checks for the product-neutral planning package."""

from __future__ import annotations

from pathlib import Path


def boundary_violations(root: str | Path | None = None) -> list[str]:
    package = Path(root) if root is not None else Path(__file__).parent
    forbidden = (
        "BANK" + "-OM",
        "open" + "metadata",
        "om" + "-temp",
        "acgh." + "integrations",
    )
    violations: list[str] = []
    for path in sorted(package.rglob("*")):
        if not path.is_file() or path.suffix not in {".py", ".json", ".yaml", ".yml"}:
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for token in forbidden:
            if token.lower() in lowered:
                violations.append(f"{path.relative_to(package)}: forbidden token {token}")
    return violations
