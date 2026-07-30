#!/usr/bin/env python3
"""Generate OM_TEMP 1.13.0 Manifest drafts from the recorded Git commits.

The script automates facts that Git can determine:

* the complete current-version file list changed by every commit of a BANK-OM ID;
* a conservative T42 watch list containing the current change scope.

The required implementation files, behavior contract, title, and unmodified
dependency paths remain explicit review decisions in ``CUSTOMIZATIONS``.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml


CUSTOMIZATIONS = {
    "BANK-OM-001": {
        "title": "기준코드(InstanceCode)",
        "commits": ["4df83b311f1ec38156c9b992f34607b22224db85"],
        "required": [
            "openmetadata-service/src/main/java/org/openmetadata/service/resources/instancecode/InstanceCodeResource.java",
            "openmetadata-spec/src/main/resources/json/schema/entity/data/instanceCode.json",
        ],
        "watch_dependencies": [],
        "contract": "CONTRACT-INSTANCE-CODE",
    },
    "BANK-OM-002": {
        "title": "쿼리 리포트(QueryReport)",
        "commits": ["68ebed4801715f0c30b8a1a614572183fa6097b8"],
        "required": [
            "openmetadata-service/src/main/java/org/openmetadata/service/resources/queryreport/QueryReportResource.java",
            "openmetadata-spec/src/main/resources/json/schema/entity/data/queryReport.json",
        ],
        "watch_dependencies": [
            "openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/QueryRepository.java",
        ],
        "contract": "CONTRACT-QUERY-REPORT",
    },
    "BANK-OM-003": {
        "title": "데이터 검증 결과(Data Assertions)",
        "commits": ["57ee1b3b23d644f13e0c1716f0810ddf962e5264"],
        "required": [
            "openmetadata-ui/src/main/resources/ui/src/pages/DataAssertionsPage/DataAssertionsPage.tsx",
            "openmetadata-ui/src/main/resources/ui/src/rest/dataAssertionsAPI.ts",
        ],
        "watch_dependencies": [
            "openmetadata-spec/src/main/resources/json/schema/tests/testCase.json",
            "openmetadata-ui/src/main/resources/ui/src/generated/tests/testCase.ts",
        ],
        "contract": "CONTRACT-DATA-ASSERTIONS",
    },
    "BANK-OM-004": {
        "title": "은행 컬럼 확장 표시",
        "commits": ["274f2b79b424e01537a7f2253c33aeecb43aaac4"],
        "required": [
            "openmetadata-ui/src/main/resources/ui/src/components/Database/SchemaTable/SchemaTable.component.tsx",
        ],
        "watch_dependencies": [
            "openmetadata-spec/src/main/resources/json/schema/entity/data/table.json",
        ],
        "contract": "CONTRACT-BANK-COLUMN-VIEW",
    },
    "BANK-OM-005": {
        "title": "한글 입력 조합 보정",
        "commits": ["d983f7c540d3fa1fe56ca91adef3f37374890f77"],
        "required": [
            "openmetadata-ui/src/main/resources/ui/src/components/Database/SchemaEditor/SchemaEditor.tsx",
        ],
        "watch_dependencies": [
            "openmetadata-ui/src/main/resources/ui/package.json",
        ],
        "contract": "CONTRACT-KOREAN-IME",
    },
    "BANK-OM-006": {
        "title": "Sybase 연결 유형",
        "commits": ["010750c514e9bbb7a765414ded3b161b1f5eb621"],
        "required": [
            "openmetadata-spec/src/main/resources/json/schema/entity/services/connections/database/sybaseConnection.json",
        ],
        "watch_dependencies": [
            "openmetadata-spec/src/main/resources/json/schema/entity/services/connections/serviceConnection.json",
        ],
        "contract": "CONTRACT-SYBASE-CONNECTOR",
    },
    "BANK-OM-007": {
        "title": "Tibero 연결 유형",
        "commits": [
            "62e39da8be65c3ff259802c1cd35f4b0c8baa333",
            "7d19c8952612e77467b0a80d6287170d814f1de1",
        ],
        "required": [
            "openmetadata-spec/src/main/resources/json/schema/entity/services/connections/database/tiberoConnection.json",
        ],
        "watch_dependencies": [
            "openmetadata-spec/src/main/resources/json/schema/entity/services/connections/serviceConnection.json",
        ],
        "contract": "CONTRACT-TIBERO-CONNECTOR",
    },
}


def changed_paths(repo: Path, commit: str) -> list[str]:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            commit,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted({line for line in result.stdout.splitlines() if line})


def commit_trailer(repo: Path, commit: str) -> str:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "show",
            "-s",
            "--format=%(trailers:key=Customization-ID,valueonly)",
            commit,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def build_manifest(repo: Path, customization_id: str, policy: dict) -> dict:
    commits = policy["commits"]
    for commit in commits:
        trailer = commit_trailer(repo, commit)
        if trailer != customization_id:
            raise ValueError(
                f"{commit}: expected Customization-ID {customization_id}, got {trailer!r}"
            )

    current_scope = set()
    for commit in commits:
        current_scope.update(changed_paths(repo, commit))

    missing_required = sorted(set(policy["required"]) - current_scope)
    if missing_required:
        raise ValueError(
            f"{customization_id}: required paths not changed by its commits: "
            f"{missing_required}"
        )

    implementation = {
        "changed_paths": sorted(current_scope),
    }
    implementation["required_changed_paths"] = policy["required"]

    return {
        "schema_version": 2,
        "customization_id": customization_id,
        "status": "active",
        "kind": "core-patch",
        "title": policy["title"],
        "implementation": implementation,
        "upgrade_watch": {
            "paths": sorted(current_scope | set(policy["watch_dependencies"])),
        },
        "assurance": {
            "contracts": [policy["contract"]],
            "direct_tests": [],
        },
        "series": {
            "allowed": len(commits) > 1,
            "depends_on": [],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo",
        type=Path,
        required=True,
        help="Local OM_TEMP repository containing all recorded commits",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "manifests",
    )
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    for customization_id, policy in CUSTOMIZATIONS.items():
        manifest = build_manifest(args.repo.resolve(), customization_id, policy)
        output = args.output / f"{customization_id}.yaml"
        output.write_text(
            yaml.safe_dump(
                manifest,
                allow_unicode=True,
                sort_keys=False,
                width=1000,
            ),
            encoding="utf-8",
        )
        print(f"{customization_id}: wrote {output}")


if __name__ == "__main__":
    main()
