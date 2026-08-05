#!/usr/bin/env python3
"""Create a human-fillable shared code-definition draft.

The owner pairs are deterministic, but the code fragment or structured value
that proves each BANK-OM feature is a business/code-review decision.  This
command therefore creates only the complete path/ID skeleton and never
pretends that an inferred token is an approved definition.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from acgh import layout


class DraftError(ValueError):
    """The owner map cannot produce a trustworthy draft."""


def build_draft(owners: dict) -> dict:
    if not isinstance(owners, dict):
        raise DraftError("shared-path-owners.yaml must be a mapping")
    definitions: list[dict] = []
    for raw_path, raw_ids in sorted(owners.items()):
        try:
            path = layout.ensure_literal(raw_path)
        except layout.LayoutError as exc:
            raise DraftError(f"invalid shared path {raw_path!r}: {exc}") from exc
        if (
            not isinstance(raw_ids, list)
            or len(set(raw_ids)) < 2
            or any(not isinstance(item, str) or not item for item in raw_ids)
        ):
            raise DraftError(
                f"{path}: expected at least two unique BANK-OM IDs"
            )
        for customization_id in sorted(set(raw_ids)):
            definitions.append(
                {
                    "path": path,
                    "customization_id": customization_id,
                    "assertions": [],
                }
            )
    return {
        "schema_version": 1,
        "draft_notice": (
            "각 assertions에 승인할 실제 코드 조각 또는 JSON/YAML 값을 "
            "작성한 뒤 draft_notice를 삭제하십시오. 빈 초안은 검사에 "
            "사용할 수 없습니다."
        ),
        "definitions": definitions,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate every shared path/BANK-OM pair; assertions stay empty "
            "until a reviewer supplies actual code definitions"
        )
    )
    parser.add_argument("--owners", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.output.exists():
            raise DraftError(f"output already exists: {args.output}")
        owners = yaml.safe_load(args.owners.read_text(encoding="utf-8"))
        draft = build_draft(owners)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            yaml.safe_dump(
                draft,
                allow_unicode=True,
                sort_keys=False,
                width=1000,
            ),
            encoding="utf-8",
        )
    except (OSError, UnicodeError, yaml.YAMLError, DraftError) as exc:
        print(
            json.dumps(
                {"status": "ANALYSIS_ERROR", "message": str(exc)},
                ensure_ascii=False,
            )
        )
        return 3
    print(
        json.dumps(
            {
                "status": "DRAFT_WRITTEN",
                "output": str(args.output.absolute()),
                "definition_pairs": len(draft["definitions"]),
                "requires_human_completion": True,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
