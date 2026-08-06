#!/usr/bin/env python3
"""Create the empty path/ID skeleton for shared code definitions.

This command only creates the complete path/ID skeleton.  A separate proposal
command may infer candidate assertions from exact BANK-OM commit diffs, but an
inferred assertion is never treated as a human-approved definition.
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


def inspect_existing_draft(existing: object, expected: dict) -> dict:
    """Confirm that an existing draft still covers the current owner pairs."""
    if not isinstance(existing, dict):
        raise DraftError("existing output must be a YAML mapping")
    definitions = existing.get("definitions")
    if not isinstance(definitions, list):
        raise DraftError("existing output has no definitions list")

    expected_pairs = {
        (item["path"], item["customization_id"])
        for item in expected["definitions"]
    }
    existing_pairs: set[tuple[str, str]] = set()
    completed_pairs = 0
    for index, item in enumerate(definitions, start=1):
        if not isinstance(item, dict):
            raise DraftError(f"existing definition #{index} must be a mapping")
        path = item.get("path")
        customization_id = item.get("customization_id")
        assertions = item.get("assertions")
        if not isinstance(path, str) or not isinstance(customization_id, str):
            raise DraftError(
                f"existing definition #{index} needs path and customization_id"
            )
        if not isinstance(assertions, list):
            raise DraftError(f"existing definition #{index} assertions must be a list")
        pair = (path, customization_id)
        if pair in existing_pairs:
            raise DraftError(f"existing output has duplicate pair: {path} / {customization_id}")
        existing_pairs.add(pair)
        if assertions:
            completed_pairs += 1

    missing = sorted(expected_pairs - existing_pairs)
    unexpected = sorted(existing_pairs - expected_pairs)
    if missing or unexpected:
        raise DraftError(
            "existing output does not match the current shared owner list: "
            f"missing={len(missing)}, unexpected={len(unexpected)}"
        )
    return {
        "definition_pairs": len(existing_pairs),
        "completed_pairs": completed_pairs,
        "remaining_pairs": len(existing_pairs) - completed_pairs,
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
        owners = yaml.safe_load(args.owners.read_text(encoding="utf-8"))
        draft = build_draft(owners)
        if args.output.exists():
            existing = yaml.safe_load(args.output.read_text(encoding="utf-8"))
            counts = inspect_existing_draft(existing, draft)
            print(
                json.dumps(
                    {
                        "status": "DRAFT_ALREADY_EXISTS",
                        "output": str(args.output.absolute()),
                        **counts,
                        "next_action": (
                            "기존 파일을 그대로 사용하고, 별도의 자동 assertion "
                            "제안 명령을 실행하십시오. 자동 추출할 수 없는 항목만 "
                            "수동으로 작성합니다."
                        ),
                    },
                    ensure_ascii=False,
                )
            )
            return 0
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
                "requires_assertion_proposal": True,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
