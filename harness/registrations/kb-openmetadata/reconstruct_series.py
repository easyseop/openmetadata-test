#!/usr/bin/env python3
"""Materialize one logical BANK-OM commit from the pinned root snapshot.

This registration-specific helper is the reproducible implementation used for
the first vendor reconstruction.  Unique paths are copied directly from the
source snapshot.  Shared paths are applied incrementally so every resolved
owner contributes a real source hunk; the final owner closes the file to the
pinned snapshot.  Locale JSON is reconstructed semantically to avoid replaying
the source snapshot's formatting-only churn.
"""
from __future__ import annotations

import argparse
import copy
import difflib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


OWNER_TOKENS = {
    "BANK-OM-001": (
        "instancecode",
        "instance_code",
        "instance-code",
        "instance code",
        "instancecodes",
        "instance_codes",
    ),
    "BANK-OM-002": (
        "queryreport",
        "query_report",
        "query-report",
        "query report",
        "queryreports",
        "query_reports",
    ),
    "BANK-OM-003": (
        "dataassertion",
        "data_assertion",
        "data-assertion",
        "data assertion",
        "failed assertion",
        "re-valid",
    ),
    "BANK-OM-004": (),
    "BANK-OM-005": ("composition",),
    "BANK-OM-006": ("sybase",),
    "BANK-OM-007": ("tibero",),
}

LOCALE_OWNER_1 = {
    "label.code-group",
    "label.code-name",
    "label.code-value",
    "label.instance-code",
    "label.instance-code-lowercase-plural",
    "label.instance-code-plural",
    "label.sort-order",
    "message.instance-code-description",
    "message.instance-code-group-description",
}
LOCALE_OWNER_2 = {
    "label.business-rule",
    "label.encryption-transform-info",
    "label.info-type",
    "label.is-encrypted",
    "label.message",
    "label.other",
    "label.query-report",
    "label.query-report-lowercase-plural",
    "label.query-report-plural",
    "label.variable-name",
    "message.query-report-description",
}
LOCALE_OWNER_3 = {
    "label.data-assertion-plural",
    "label.my-failed-assertion-plural",
    "label.pass-rate",
    "label.re-validate-data",
    "message.data-assertions-revalidate-placeholder",
}
LOCALE_OWNER_BY_PATH = {
    **{path: "BANK-OM-001" for path in LOCALE_OWNER_1},
    **{path: "BANK-OM-002" for path in LOCALE_OWNER_2},
    **{path: "BANK-OM-003" for path in LOCALE_OWNER_3},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--id", required=True)
    parser.add_argument("--only-locales", action="store_true")
    parser.add_argument("--restore-locales-ref")
    parser.add_argument("--only-path", action="append", default=[])
    parser.add_argument("--restore-ref")
    return parser.parse_args()


def copy_snapshot_path(snapshot: Path, product: Path, relative: str) -> None:
    source = snapshot / relative
    target = product / relative
    if source.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    elif target.exists():
        target.unlink()


def flatten_differences(current, source, prefix: str = ""):
    if isinstance(current, dict) and isinstance(source, dict):
        for key, value in source.items():
            path = f"{prefix}.{key}" if prefix else key
            if key not in current:
                yield path, copy.deepcopy(value)
            else:
                yield from flatten_differences(current[key], value, path)
        for key in current.keys() - source.keys():
            path = f"{prefix}.{key}" if prefix else key
            yield path, None
        return
    if current != source:
        yield prefix, copy.deepcopy(source)


def set_json_path(value, dotted_path: str, replacement) -> None:
    keys = dotted_path.split(".")
    parent = value
    for key in keys[:-1]:
        parent = parent[key]
    if replacement is None:
        del parent[keys[-1]]
    else:
        parent[keys[-1]] = replacement


def locale_owner(path: str) -> str:
    if path in LOCALE_OWNER_BY_PATH:
        return LOCALE_OWNER_BY_PATH[path]
    return "BANK-OM-004"


def apply_locale_json(current_path: Path, source_path: Path, owner: str) -> None:
    current_text = current_path.read_text(encoding="utf-8")
    current = json.loads(current_text)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    changes = list(flatten_differences(current, source))
    selected = [
        (path, replacement)
        for path, replacement in changes
        if locale_owner(path) == owner
    ]
    if not selected:
        raise RuntimeError(f"{owner} has no locale semantic delta in {source_path}")
    for path, replacement in selected:
        set_json_path(current, path, replacement)
    indent_match = re.search(r"\n( +)\"", current_text)
    indent = len(indent_match.group(1)) if indent_match else 2
    current_path.write_text(
        json.dumps(current, ensure_ascii=False, indent=indent) + "\n",
        encoding="utf-8",
    )


def merge_token_additions(current, source, token: str):
    needle = token.casefold()
    if isinstance(current, dict) and isinstance(source, dict):
        result = copy.deepcopy(current)
        for key, source_value in source.items():
            if key not in current:
                encoded = json.dumps(
                    {key: source_value}, ensure_ascii=False
                ).casefold()
                if needle in encoded:
                    result[key] = copy.deepcopy(source_value)
            else:
                result[key] = merge_token_additions(
                    current[key], source_value, token
                )
        return result
    if isinstance(current, list) and isinstance(source, list):
        result = []
        remaining = list(current)
        for source_item in source:
            if source_item in remaining:
                result.append(copy.deepcopy(source_item))
                remaining.remove(source_item)
                continue
            encoded = json.dumps(source_item, ensure_ascii=False).casefold()
            if needle in encoded:
                result.append(copy.deepcopy(source_item))
        result.extend(copy.deepcopy(remaining))
        return result
    if current != source and needle in str(source).casefold():
        return copy.deepcopy(source)
    return copy.deepcopy(current)


def write_json(path: Path, value) -> None:
    current_text = path.read_text(encoding="utf-8")
    indent_match = re.search(r"\n( +)\"", current_text)
    indent = len(indent_match.group(1)) if indent_match else 2
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=indent) + "\n",
        encoding="utf-8",
    )


def apply_shared_json(
    current_path: Path,
    source_path: Path,
    relative: str,
    owner: str,
    is_last: bool,
) -> None:
    if "/locale/languages/" in relative:
        apply_locale_json(current_path, source_path, owner)
        return

    if relative.endswith("/elasticsearch/indexMapping.json"):
        source_text = source_path.read_text(encoding="utf-8")
        current_text = current_path.read_text(encoding="utf-8")
        key, next_key = {
            "BANK-OM-001": ("instanceCode", "queryReport"),
            "BANK-OM-002": ("queryReport", "glossary"),
        }[owner]
        start_marker = f'  "{key}":'
        end_marker = f'  "{next_key}":'
        start = source_text.index(start_marker)
        end = source_text.index(end_marker, start)
        block = source_text[start:end]
        if start_marker not in current_text:
            insertion = (
                current_text.index(end_marker)
                if end_marker in current_text
                else current_text.index('  "glossary":')
            )
            current_path.write_text(
                current_text[:insertion] + block + current_text[insertion:],
                encoding="utf-8",
            )
        return

    if relative.endswith("/entity/services/databaseService.json") and not is_last:
        apply_shared_text(current_path, source_path, owner)
        json.loads(current_path.read_text(encoding="utf-8"))
        return

    current = json.loads(current_path.read_text(encoding="utf-8"))
    source = json.loads(source_path.read_text(encoding="utf-8"))

    if not is_last:
        token = OWNER_TOKENS[owner][0]
        merged = merge_token_additions(current, source, token)
        if merged == current:
            raise RuntimeError(
                f"{owner} produced no semantic JSON delta for {relative}"
            )
        write_json(current_path, merged)
        return

    write_json(current_path, source)


def chunk_insertions(lines: list[str]) -> list[list[str]]:
    chunks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if not line.strip():
            if current:
                chunks.append(current)
                current = []
            chunks.append([line])
        else:
            current.append(line)
    if current:
        chunks.append(current)
    return chunks


def contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    folded = text.casefold()
    return any(token in folded for token in tokens)


def select_owner_insertions(lines: list[str], owner: str) -> list[str]:
    own_tokens = OWNER_TOKENS[owner]
    other_tokens = tuple(
        token
        for other_owner, tokens in OWNER_TOKENS.items()
        if other_owner != owner
        for token in tokens
    )
    selected: list[str] = []
    for chunk in chunk_insertions(lines):
        text = "".join(chunk)
        if not contains_any(text, own_tokens):
            continue
        if not contains_any(text, other_tokens):
            selected.extend(chunk)
            continue
        selected.extend(
            line for line in chunk if contains_any(line, own_tokens)
        )
    return selected


def apply_shared_text(
    current_path: Path, source_path: Path, owner: str
) -> None:
    current = current_path.read_text(encoding="utf-8").splitlines(keepends=True)
    source = source_path.read_text(encoding="utf-8").splitlines(keepends=True)
    matcher = difflib.SequenceMatcher(a=current, b=source, autojunk=False)
    output: list[str] = []
    inserted_count = 0
    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        if opcode == "equal":
            output.extend(current[a0:a1])
        elif opcode == "insert":
            selected = select_owner_insertions(source[b0:b1], owner)
            output.extend(selected)
            inserted_count += len(selected)
        else:
            # Deletions/replacements are closed by the final owner.  Earlier
            # owners only introduce their positively attributable source hunks.
            output.extend(current[a0:a1])
    if inserted_count == 0:
        raise RuntimeError(f"{owner} produced no source insertion in {current_path}")
    current_path.write_text("".join(output), encoding="utf-8")


def planned_paths(plan, owners, args) -> list[str]:
    customization_id = args.id
    selected = {
        relative
        for relative, owner in plan.unique_assignments
        if owner == customization_id
        and not args.only_locales
        and (not args.only_path or relative in args.only_path)
    }
    selected.update(
        relative
        for relative, path_owners in owners.items()
        if customization_id in path_owners
        and (not args.only_locales or "/locale/languages/" in relative)
        and (not args.only_path or relative in args.only_path)
    )
    return sorted(selected)


def working_tree_paths(product: Path) -> set[str]:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(product),
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "-z",
        ],
        check=True,
        capture_output=True,
    )
    records = [record for record in result.stdout.decode().split("\0") if record]
    paths: set[str] = set()
    for record in records:
        status = record[:2]
        if "R" in status or "C" in status:
            raise RuntimeError(
                "rename/copy changes are not supported while reconstructing a BANK-OM ID"
            )
        paths.add(record[3:])
    return paths


def restore_head_path(repo: Path, target_root: Path, relative: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"HEAD:{relative}"],
        check=False,
        capture_output=True,
    )
    target = target_root / relative
    if result.returncode == 0:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(result.stdout)


def same_path_content(left_root: Path, right_root: Path, relative: str) -> bool:
    left = left_root / relative
    right = right_root / relative
    if left.exists() != right.exists():
        return False
    if not left.exists():
        return True
    return left.read_bytes() == right.read_bytes()


def materialize(args, plan, owners, product: Path) -> list[str]:
    customization_id = args.id
    changed: list[str] = []
    for relative, owner in plan.unique_assignments:
        if (
            owner == customization_id
            and not args.only_locales
            and (not args.only_path or relative in args.only_path)
        ):
            copy_snapshot_path(args.snapshot, product, relative)
            changed.append(relative)

    for relative, path_owners in owners.items():
        if customization_id not in path_owners:
            continue
        if args.only_locales and "/locale/languages/" not in relative:
            continue
        if args.only_path and relative not in args.only_path:
            continue
        current_path = product / relative
        source_path = args.snapshot / relative
        is_last = customization_id == path_owners[-1]
        if args.restore_ref:
            restored = subprocess.run(
                [
                    "git",
                    "-C",
                    str(args.product),
                    "show",
                    f"{args.restore_ref}:{relative}",
                ],
                check=True,
                capture_output=True,
            ).stdout
            current_path.write_bytes(restored)
        if args.restore_locales_ref and "/locale/languages/" in relative:
            restored = subprocess.run(
                [
                    "git",
                    "-C",
                    str(args.product),
                    "show",
                    f"{args.restore_locales_ref}:{relative}",
                ],
                check=True,
                capture_output=True,
            ).stdout
            current_path.write_bytes(restored)
        if relative.endswith(".json"):
            apply_shared_json(
                current_path,
                source_path,
                relative,
                customization_id,
                is_last,
            )
        elif is_last:
            copy_snapshot_path(args.snapshot, product, relative)
        else:
            apply_shared_text(current_path, source_path, customization_id)
        changed.append(relative)
    return changed


def already_materialized(args, plan, owners) -> tuple[bool, list[str]]:
    if (
        args.only_locales
        or args.only_path
        or args.restore_ref
        or args.restore_locales_ref
    ):
        return False, []

    expected_paths = planned_paths(plan, owners, args)
    actual_paths = working_tree_paths(args.product)
    if not actual_paths:
        return False, expected_paths

    if actual_paths != set(expected_paths):
        missing = sorted(set(expected_paths) - actual_paths)
        unexpected = sorted(actual_paths - set(expected_paths))
        raise RuntimeError(
            f"{args.id} cannot start because the working tree is not clean and "
            f"does not exactly match its {len(expected_paths)} expected paths; "
            f"missing={missing[:3]} unexpected={unexpected[:3]}"
        )

    with tempfile.TemporaryDirectory(prefix=f"{args.id.lower()}-expected-") as tmp:
        expected_root = Path(tmp)
        for relative in expected_paths:
            restore_head_path(args.product, expected_root, relative)
        materialize(args, plan, owners, expected_root)
        mismatches = [
            relative
            for relative in expected_paths
            if not same_path_content(args.product, expected_root, relative)
        ]
        if mismatches:
            raise RuntimeError(
                f"{args.id} has the expected path set but incomplete or different "
                f"content; mismatches={mismatches[:3]}"
            )
    return True, expected_paths


def main() -> int:
    args = parse_args()
    sys.path.insert(0, str(args.harness))
    from acgh import vendor_rebuild as vr

    registry, manifests, inventory = vr.load_registration_bundle(
        args.registration
    )
    plan = vr.build_reconstruction_plan(registry, manifests, inventory)
    owners = yaml.safe_load(
        (args.registration / "shared-path-owners.yaml").read_text(
            encoding="utf-8"
        )
    )
    customization_id = args.id
    if customization_id not in plan.active_ids:
        raise RuntimeError(f"unknown active customization: {customization_id}")

    complete, expected_paths = already_materialized(args, plan, owners)
    if complete:
        print(
            f"{customization_id}: ALREADY_MATERIALIZED "
            f"({len(expected_paths)} paths)"
        )
        print("No files changed. Continue with step 5-2; do not rerun step 5-1.")
        return 0

    changed = materialize(args, plan, owners, args.product)

    print(f"{customization_id}: materialized {len(changed)} paths")
    for relative in changed:
        print(relative)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
