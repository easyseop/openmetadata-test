#!/usr/bin/env python3
"""Capture a real cherry-pick conflict and its resolved comparison artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def run(
    repo: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--resolved-commit", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    customization_id = run(
        repo,
        "show",
        "-s",
        "--format=%(trailers:key=Customization-ID,valueonly)",
        args.source_commit,
    ).stdout.strip()
    if not customization_id:
        raise ValueError(f"{args.source_commit}: missing Customization-ID trailer")

    worktree = Path(
        tempfile.mkdtemp(prefix="om-conflict-capture-", dir="/private/tmp")
    )
    try:
        run(repo, "worktree", "add", "--detach", str(worktree), args.target)
        cherry_pick = run(
            worktree,
            "cherry-pick",
            args.source_commit,
            check=False,
        )
        if cherry_pick.returncode == 0:
            raise ValueError("expected a conflict, but cherry-pick succeeded")
        unmerged = run(
            worktree,
            "diff",
            "--name-only",
            "--diff-filter=U",
        ).stdout.splitlines()
        if args.path not in unmerged:
            raise ValueError(f"{args.path}: not present in unmerged paths")

        slug = f"{customization_id}_ko-kr"
        conflict_path = output / f"{slug}_full_conflict.txt"
        resolved_path = output / f"{slug}_resolved.json"
        diff_path = output / f"{slug}_resolution.diff"
        metadata_path = output / f"{slug}_capture.json"

        conflict_path.write_bytes((worktree / args.path).read_bytes())
        resolved_path.write_text(
            run(
                repo,
                "show",
                f"{args.resolved_commit}:{args.path}",
            ).stdout,
            encoding="utf-8",
        )
        diff_path.write_text(
            run(
                repo,
                "diff",
                "--unified=6",
                args.target,
                args.resolved_commit,
                "--",
                args.path,
            ).stdout,
            encoding="utf-8",
        )
        metadata = {
            "customization_id": customization_id,
            "target": args.target,
            "source_commit": args.source_commit,
            "resolved_commit": args.resolved_commit,
            "path": args.path,
            "unmerged_path_count": len(unmerged),
            "unmerged_paths": unmerged,
            "cherry_pick_output": (
                cherry_pick.stdout.rstrip() + "\n" + cherry_pick.stderr.rstrip()
            ).strip(),
            "artifacts": {
                "full_conflict": conflict_path.name,
                "resolved": resolved_path.name,
                "resolution_diff": diff_path.name,
            },
        }
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(metadata_path)
        print(conflict_path)
        print(resolved_path)
        print(diff_path)
    finally:
        run(worktree, "cherry-pick", "--abort", check=False)
        run(repo, "worktree", "remove", "--force", str(worktree), check=False)
        if worktree.exists():
            worktree.rmdir()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
