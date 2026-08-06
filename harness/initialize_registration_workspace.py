#!/usr/bin/env python3
"""Archive one legacy registration and create clean initial-registration facts.

This command does not create or approve Manifest, Registry, Contract, or shared
code assertions.  It only verifies the approved path/ID classification, moves
the previous rehearsal bundle out of the active registration path, and writes
the Git-derived/path-classification inputs needed by the next human review.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


class InitializationError(ValueError):
    """The active registration cannot be replaced safely."""


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        raise InitializationError(completed.stderr.strip() or "Git command failed")
    return completed.stdout.strip()


def load_mapping(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("paths"), list):
        raise InitializationError("분류 파일의 paths 목록을 읽을 수 없습니다.")
    return data


def mapping_facts(data: dict) -> tuple[dict[str, list[str]], list[str], list[str]]:
    owners: dict[str, list[str]] = {}
    excluded: list[str] = []
    for item in data["paths"]:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise InitializationError("분류 파일에 path가 없는 항목이 있습니다.")
        path = item["path"]
        if path in owners or path in excluded:
            raise InitializationError(f"분류 파일에 경로가 중복됐습니다: {path}")
        classification = item.get("classification")
        ids = item.get("customization_ids")
        if classification == "excluded":
            if ids:
                raise InitializationError(f"제외 경로에 BANK-OM ID가 있습니다: {path}")
            excluded.append(path)
            continue
        if classification not in {"exclusive", "shared"}:
            raise InitializationError(f"알 수 없는 경로 분류입니다: {path}")
        if not isinstance(ids, list) or not ids or any(not isinstance(v, str) for v in ids):
            raise InitializationError(f"등록 경로의 BANK-OM ID가 비었습니다: {path}")
        unique = sorted(set(ids))
        if classification == "exclusive" and len(unique) != 1:
            raise InitializationError(f"단독 경로에 ID가 여러 개입니다: {path}")
        if classification == "shared" and len(unique) < 2:
            raise InitializationError(f"공용 경로의 ID가 두 개 미만입니다: {path}")
        owners[path] = unique
    shared = sorted(path for path, ids in owners.items() if len(ids) > 1)
    return owners, sorted(excluded), shared


def yaml_bytes(data: dict) -> bytes:
    return yaml.safe_dump(
        data, allow_unicode=True, sort_keys=False, width=1000
    ).encode("utf-8")


def write_clean_workspace(
    target: Path,
    legacy: Path,
    *,
    owners: dict[str, list[str]],
    shared: list[str],
    official_sha: str,
) -> None:
    target.mkdir(parents=True)
    (target / "manifests").mkdir()
    for name in ("repository-layout.yaml", "sensitive-zones.yaml"):
        source = legacy / name
        if not source.is_file():
            raise InitializationError(f"보존할 정책 파일이 없습니다: {source}")
        if name == "repository-layout.yaml":
            layout = yaml.safe_load(source.read_text(encoding="utf-8"))
            if not isinstance(layout, dict):
                raise InitializationError("repository-layout.yaml 형식이 잘못됐습니다.")
            layout["upstream_base_sha"] = official_sha
            (target / name).write_bytes(yaml_bytes(layout))
        else:
            shutil.copy2(source, target / name)
    (target / "source-diff-paths.txt").write_text(
        "".join(f"{path}\n" for path in sorted(owners)), encoding="utf-8"
    )
    (target / "source-snapshot-path-owners.yaml").write_bytes(yaml_bytes(owners))
    (target / "shared-path-owners.yaml").write_bytes(
        yaml_bytes({path: owners[path] for path in shared})
    )
    (target / "README.md").write_text(
        "# OM_TEMP initial registration workspace\n\n"
        "This directory was initialized from the approved 1.13.1 path/ID mapping.\n"
        "Manifest, Registry, Contract, and shared-code assertions are intentionally\n"
        "absent until a human writes and approves them. Do not run plan yet.\n",
        encoding="utf-8",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--official-ref", required=True)
    parser.add_argument("--custom-ref", required=True)
    parser.add_argument("--mapping", required=True, type=Path)
    parser.add_argument("--registration", required=True, type=Path)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        repo = args.repo.resolve(strict=True)
        mapping = load_mapping(args.mapping.resolve(strict=True))
        owners, excluded, shared = mapping_facts(mapping)
        official_sha = git(repo, "rev-parse", f"{args.official_ref}^{{commit}}")
        custom_sha = git(repo, "rev-parse", f"{args.custom_ref}^{{commit}}")
        actual = sorted(
            line for line in git(repo, "diff", "--name-only", official_sha, custom_sha).splitlines() if line
        )
        if actual != sorted(owners):
            missing = sorted(set(owners) - set(actual))
            extra = sorted(set(actual) - set(owners))
            raise InitializationError(
                f"111개 승인 경로와 실제 diff가 다릅니다: missing={missing}, extra={extra}"
            )
        excluded_diff = sorted(set(actual) & set(excluded))
        if excluded_diff:
            raise InitializationError(
                f"제외 경로가 custom diff에 남았습니다: {excluded_diff}"
            )
        pairs = sum(len(ids) for ids in owners.values() if len(ids) > 1)
        result = {
            "status": "READY_TO_INITIALIZE" if not args.execute else "INITIALIZED",
            "official_sha": official_sha,
            "custom_sha": custom_sha,
            "registered_paths": len(owners),
            "excluded_paths": len(excluded),
            "shared_paths": len(shared),
            "shared_path_id_pairs": pairs,
            "registration": str(args.registration),
            "archive": str(args.archive),
        }
        if not args.execute:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        registration = args.registration.resolve(strict=True)
        archive = args.archive.resolve(strict=False)
        if archive.exists():
            raise InitializationError(f"보관 폴더가 이미 있습니다: {archive}")
        archive.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix=f".{registration.name}-new-", dir=registration.parent
        ) as temp_name:
            staged = Path(temp_name) / registration.name
            write_clean_workspace(
                staged,
                registration,
                owners=owners,
                shared=shared,
                official_sha=official_sha,
            )
            shutil.move(str(registration), str(archive))
            try:
                shutil.move(str(staged), str(registration))
            except Exception:
                shutil.move(str(archive), str(registration))
                raise
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, UnicodeError, yaml.YAMLError, InitializationError) as exc:
        print(
            json.dumps(
                {"status": "ANALYSIS_ERROR", "message": str(exc)},
                ensure_ascii=False,
            )
        )
        return 3


if __name__ == "__main__":
    sys.exit(main())
