#!/usr/bin/env python3
"""Resolve JSON cherry-pick conflicts only when leaf changes do not overlap.

Git index stages are used as the three inputs:
  1 = common base (BASE), 2 = currently checked out side (OURS),
  3 = incoming side (THEIRS).

In the OM_TEMP cherry-pick exercise, OURS is the new official JSON and THEIRS is
the BANK-OM commit being applied. The command keeps OURS and applies only
non-overlapping THEIRS leaf changes.
If both sides changed the same leaf key, it stops without writing that file.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


MISSING = object()


@dataclass(frozen=True)
class Change:
    path: tuple[str, ...]
    value: object


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
    ).stdout


def read_stage(repo: Path, stage: int, path: str) -> bytes:
    return git(repo, "show", f":{stage}:{path}")


def load_stage(repo: Path, stage: int, path: str) -> dict:
    value = json.loads(read_stage(repo, stage, path))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return value


def detect_indent(raw: bytes, default: int = 4) -> int:
    """Read the indent width from the side we are keeping.

    The resolved file is re-serialized, not text-patched, so the writer picks
    the layout. Hardcoding a width silently reformats the whole file whenever
    upstream uses a different one, which shows up as a full-file diff that has
    nothing to do with the customization. Follow the incoming version instead.
    """
    for line in raw.decode("utf-8").split("\n")[1:]:
        stripped = line.lstrip(" ")
        if stripped and stripped != line:
            return len(line) - len(stripped)
    return default


def flatten(value: object, prefix: tuple[str, ...] = ()) -> dict:
    if isinstance(value, dict):
        output = {}
        for key, child in value.items():
            output.update(flatten(child, (*prefix, key)))
        return output
    return {prefix: value}


def changes(base: dict, changed: dict) -> list[Change]:
    before = flatten(base)
    after = flatten(changed)
    output = []
    for path in sorted(set(before) | set(after)):
        left = before.get(path, MISSING)
        right = after.get(path, MISSING)
        if left != right:
            output.append(Change(path, right))
    return output


def apply_change(target: dict, change: Change) -> None:
    parent = target
    for key in change.path[:-1]:
        child = parent.get(key)
        if not isinstance(child, dict):
            raise ValueError(
                f"cannot apply {'.'.join(change.path)}: {key} is not an object"
            )
        parent = child
    leaf = change.path[-1]
    if change.value is MISSING:
        parent.pop(leaf, None)
    else:
        parent[leaf] = change.value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    paths = git(
        repo, "diff", "--name-only", "--diff-filter=U"
    ).decode().splitlines()
    json_paths = [path for path in paths if path.endswith(".json")]
    non_json = sorted(set(paths) - set(json_paths))
    if non_json:
        raise ValueError(
            f"unresolved non-JSON conflicts require manual review: {non_json}"
        )

    plans = []
    for path in json_paths:
        base = load_stage(repo, 1, path)
        official = load_stage(repo, 2, path)
        bank = load_stage(repo, 3, path)
        official_changes = {item.path for item in changes(base, official)}
        bank_changes = changes(base, bank)
        overlap = official_changes & {item.path for item in bank_changes}
        if overlap:
            names = [".".join(item) for item in sorted(overlap)]
            raise ValueError(f"{path}: overlapping leaf changes: {names}")
        plans.append((path, official, bank_changes, detect_indent(
            read_stage(repo, 2, path)
        )))

    for path, merged, bank_changes, indent in plans:
        for change in bank_changes:
            apply_change(merged, change)
        target = repo / path
        target.write_text(
            json.dumps(
                merged,
                ensure_ascii=False,
                indent=indent,
                separators=(",", ": "),
            )
            + "\n",
            encoding="utf-8",
        )
        print(
            f"resolved {path}: BANK-OM leaf changes={len(bank_changes)} "
            f"(indent={indent})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
