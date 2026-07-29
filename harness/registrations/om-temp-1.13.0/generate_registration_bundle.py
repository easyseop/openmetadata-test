#!/usr/bin/env python3
"""Generate the OM_TEMP 1.13.0 source-registration bundle.

Git supplies the pinned source inventory and shared-path candidates. Human
decisions (titles, criticality, business invariants, and required tests) stay
explicit in this file so they can be reviewed before regeneration.

The source snapshot intentionally stops at BANK-OM-007's first commit.
The Manifest stores one current-version ``changed_paths`` list. Git commit
history remains the source of truth for which files belonged to the pinned
source snapshot and which were changed by a later commit.
"""

from __future__ import annotations

import argparse
import subprocess
from collections import defaultdict
from pathlib import Path

import yaml


UPSTREAM_SHA = "f329dd4a7e47134a2bd5a06af6181b0ee527ddd9"
UPSTREAM_TAG = "1.13.0-release"
SOURCE_SNAPSHOT_SHA = "62e39da8be65c3ff259802c1cd35f4b0c8baa333"
FINAL_REMOTE_SHA = "7d19c8952612e77467b0a80d6287170d814f1de1"


CUSTOMIZATIONS = [
    {
        "customization_id": "BANK-OM-001",
        "title": "기준코드(InstanceCode)",
        "criticality": "high",
        "contract": "CONTRACT-INSTANCE-CODE",
    },
    {
        "customization_id": "BANK-OM-002",
        "title": "쿼리 리포트(QueryReport)",
        "criticality": "high",
        "contract": "CONTRACT-QUERY-REPORT",
    },
    {
        "customization_id": "BANK-OM-003",
        "title": "데이터 검증 결과(Data Assertions)",
        "criticality": "high",
        "contract": "CONTRACT-DATA-ASSERTIONS",
    },
    {
        "customization_id": "BANK-OM-004",
        "title": "은행 컬럼 확장 표시",
        "criticality": "medium",
        "contract": "CONTRACT-BANK-COLUMN-VIEW",
    },
    {
        "customization_id": "BANK-OM-005",
        "title": "한글 입력 조합 보정",
        "criticality": "medium",
        "contract": "CONTRACT-KOREAN-IME",
    },
    {
        "customization_id": "BANK-OM-006",
        "title": "Sybase 연결 유형",
        "criticality": "high",
        "contract": "CONTRACT-SYBASE-CONNECTOR",
    },
    {
        "customization_id": "BANK-OM-007",
        "title": "Tibero 연결 유형",
        "criticality": "high",
        "contract": "CONTRACT-TIBERO-CONNECTOR",
    },
]


CONTRACTS = [
    {
        "id": "CONTRACT-INSTANCE-CODE",
        "title": "InstanceCode CRUD, search, and index round-trip",
        "invariant": (
            "InstanceCode의 codeGroup/codeValue가 CRUD와 재색인 뒤에도 "
            "동일하게 조회된다."
        ),
        "required_tests": [
            "tests/bank/contracts/test_instance_code.py::test_crud_search_roundtrip"
        ],
        "customization_ids": ["BANK-OM-001"],
    },
    {
        "id": "CONTRACT-QUERY-REPORT",
        "title": "QueryReport and query usage linkage",
        "invariant": (
            "QueryReport와 연결된 Query 목록이 생성·수정·삭제 및 재색인 "
            "뒤에도 보존된다."
        ),
        "required_tests": [
            "tests/bank/contracts/test_query_report.py::test_query_usage_roundtrip"
        ],
        "customization_ids": ["BANK-OM-002"],
    },
    {
        "id": "CONTRACT-DATA-ASSERTIONS",
        "title": "Data assertion status and ownership view",
        "invariant": (
            "실패한 test case가 상태·소유자·테이블·컬럼과 함께 일관되게 "
            "노출된다."
        ),
        "required_tests": [
            "tests/bank/contracts/test_data_assertions.py::test_failed_assertion_projection",
            "tests/bank/contracts/test_data_assertions.py::test_failed_assertion_rendered_row",
        ],
        "customization_ids": ["BANK-OM-003"],
    },
    {
        "id": "CONTRACT-BANK-COLUMN-VIEW",
        "title": "Bank column metadata presentation",
        "invariant": (
            "컬럼 순번·키·제약조건 등 행내 확장 정보가 스키마와 검색 "
            "화면에서 동일하게 표시된다."
        ),
        "required_tests": [
            "tests/bank/contracts/test_bank_columns.py::test_extended_column_projection",
            "tests/bank/contracts/test_bank_columns.py::test_extended_column_rendered_row",
        ],
        "customization_ids": ["BANK-OM-004"],
    },
    {
        "id": "CONTRACT-KOREAN-IME",
        "title": "Korean IME composition is lossless",
        "invariant": (
            "CodeMirror 입력 중 조합 중인 한글 자모가 중복·역전·소실되지 않는다."
        ),
        "required_tests": [
            "tests/bank/contracts/test_korean_ime.py::test_hangul_composition_roundtrip"
        ],
        "customization_ids": ["BANK-OM-005"],
    },
    {
        "id": "CONTRACT-SYBASE-CONNECTOR",
        "title": "Sybase connection metadata and service selection",
        "invariant": (
            "Sybase 연결 스키마가 생성 UI·API·serviceConnection union에서 "
            "동일하게 유지된다."
        ),
        "required_tests": [
            "tests/bank/contracts/test_sybase.py::test_connection_schema_roundtrip"
        ],
        "customization_ids": ["BANK-OM-006"],
    },
    {
        "id": "CONTRACT-TIBERO-CONNECTOR",
        "title": "Tibero connection metadata and service selection",
        "invariant": (
            "Tibero 연결 스키마가 생성 UI·API·serviceConnection union에서 "
            "동일하게 유지된다."
        ),
        "required_tests": [
            "tests/bank/contracts/test_tibero.py::test_connection_schema_roundtrip"
        ],
        "customization_ids": ["BANK-OM-007"],
    },
]


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def load_manifests(root: Path) -> dict[str, dict]:
    manifests = {}
    for path in sorted((root / "manifests").glob("BANK-OM-*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        manifests[data["customization_id"]] = data
    expected = {item["customization_id"] for item in CUSTOMIZATIONS}
    if set(manifests) != expected:
        raise ValueError(
            "Manifest ID set mismatch: "
            f"missing={sorted(expected - set(manifests))}, "
            f"extra={sorted(set(manifests) - expected)}"
        )
    return manifests


def write_yaml(path: Path, data: dict) -> None:
    path.write_text(
        yaml.safe_dump(
            data,
            allow_unicode=True,
            sort_keys=False,
            width=1000,
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo",
        type=Path,
        required=True,
        help="Local repository containing official and OM_TEMP commit objects",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Registration directory containing manifests/ and receiving outputs",
    )
    parser.add_argument("--upstream-sha", default=UPSTREAM_SHA)
    parser.add_argument("--upstream-tag", default=UPSTREAM_TAG)
    parser.add_argument("--source-snapshot-sha", default=SOURCE_SNAPSHOT_SHA)
    parser.add_argument("--final-sha", default=FINAL_REMOTE_SHA)
    parser.add_argument("--repository", default="easyseop/OM_TEMP")
    parser.add_argument(
        "--patch-ref",
        default="patch/om-1.13.0",
        help="Local patch branch/tag whose tree must equal upstream-sha",
    )
    parser.add_argument(
        "--ancestry-preserved",
        action="store_true",
        help="Set only when the registered source snapshot descends from upstream-sha",
    )
    args = parser.parse_args()

    repo = args.repo.resolve()
    root = args.output_dir.resolve()
    manifests = load_manifests(root)

    for commit in (
        args.upstream_sha,
        args.source_snapshot_sha,
        args.final_sha,
    ):
        git(repo, "cat-file", "-e", f"{commit}^{{commit}}")

    upstream_tree = git(repo, "rev-parse", f"{args.upstream_sha}^{{tree}}")
    patch_tree = git(repo, "rev-parse", f"{args.patch_ref}^{{tree}}")
    if upstream_tree != patch_tree:
        raise ValueError(
            f"{args.patch_ref} tree does not equal {args.upstream_tag} upstream tree"
        )

    source_paths = sorted(
        filter(
            None,
            git(
                repo,
                "diff",
                "--name-only",
                f"{args.upstream_sha}..{args.source_snapshot_sha}",
            ).splitlines(),
        )
    )
    final_paths = sorted(
        filter(
            None,
            git(
                repo,
                "diff",
                "--name-only",
                f"{args.upstream_sha}..{args.final_sha}",
            ).splitlines(),
        )
    )
    source_owners: dict[str, list[str]] = defaultdict(list)
    for commit in git(repo, "rev-list", "--reverse", args.source_snapshot_sha).splitlines():
        customization_id = git(
            repo,
            "show",
            "-s",
            "--format=%(trailers:key=Customization-ID,valueonly)",
            commit,
        )
        if customization_id not in manifests:
            continue
        changed = filter(
            None,
            git(
                repo,
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                commit,
            ).splitlines(),
        )
        for path in changed:
            source_owners[path].append(customization_id)

    unregistered = sorted(set(source_paths) - set(source_owners))
    extra = sorted(set(source_owners) - set(source_paths))
    if unregistered or extra:
        raise ValueError(
            f"source scope mismatch: unregistered={unregistered}, extra={extra}"
        )

    shared_owners = {
        path: sorted(set(owners))
        for path, owners in sorted(source_owners.items())
        if len(set(owners)) > 1
    }

    registry = {
        "schema_version": 1,
        "source": {
            "repository": args.repository,
            "snapshot_sha": args.source_snapshot_sha,
            "upstream_repository": "open-metadata/OpenMetadata",
            "upstream_tag": args.upstream_tag,
            "upstream_sha": args.upstream_sha,
            "changed_path_count": len(source_paths),
            "ancestry_preserved": args.ancestry_preserved,
            "diff_inventory": "source-diff-paths.txt",
            "unregistered_findings": [],
            "limitations": [
                *(
                    []
                    if args.ancestry_preserved
                    else [
                        (
                            "OM_TEMP remote source commits are independent "
                            "snapshots and do not preserve official "
                            "OpenMetadata ancestry."
                        )
                    ]
                ),
                (
                    "The source snapshot stops before the BANK-OM-007 follow-up; "
                    "the final candidate Manifest contains the full current-version "
                    "changed_paths scope."
                ),
                (
                    "BANK-OM owners are pending assignment; registry readiness "
                    "cannot approve release ownership yet."
                ),
            ],
        },
        "entries": [
            {
                "customization_id": item["customization_id"],
                "title": item["title"],
                "owner": "UNASSIGNED",
                "owner_status": "pending",
                "status": "active",
                "criticality": item["criticality"],
                "manifest": f"manifests/{item['customization_id']}.yaml",
                "contracts": [item["contract"]],
                "provenance": "source-snapshot",
            }
            for item in CUSTOMIZATIONS
        ],
    }

    write_yaml(root / "customization-registry.yaml", registry)
    write_yaml(
        root / "contracts.yaml",
        {"schema_version": 1, "contracts": CONTRACTS},
    )
    write_yaml(root / "shared-path-owners.yaml", shared_owners)
    write_yaml(
        root / "source-snapshot-path-owners.yaml",
        {
            path: sorted(set(owners))
            for path, owners in sorted(source_owners.items())
        },
    )
    (root / "source-diff-paths.txt").write_text(
        "\n".join(source_paths) + "\n",
        encoding="utf-8",
    )

    print(f"Registry entries: {len(CUSTOMIZATIONS)}")
    print(f"Contracts: {len(CONTRACTS)}")
    print(f"Source diff paths: {len(source_paths)}")
    print(f"Shared paths: {len(shared_owners)}")
    print(f"Source snapshot ownership paths: {len(source_owners)}")
    print(f"Official upstream tree: {upstream_tree}")


if __name__ == "__main__":
    main()
