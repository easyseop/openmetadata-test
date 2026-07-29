#!/usr/bin/env python3
"""Validate the OM_TEMP registration bundle before source-gate execution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


def parse_args() -> argparse.Namespace:
    registration = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--registration", type=Path, default=registration)
    parser.add_argument(
        "--layout",
        type=Path,
        default=registration / "repository-layout.yaml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="선택: 화면에 표시한 JSON 결과를 같은 내용으로 저장할 파일",
    )
    return parser.parse_args()


def emit_result(output: dict, output_path: Path | None) -> None:
    rendered = json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True)
    print(rendered)
    if output_path:
        output_path.write_text(rendered + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    harness = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(harness))

    from acgh import contracts
    from acgh import gitprim
    from acgh import layout
    from acgh import manifest
    from acgh import registry
    from acgh import verdict
    from acgh import vendor_rebuild

    registration_label = args.registration.as_posix()
    registration = args.registration.resolve()
    try:
        repository_layout = layout.load_layout(args.layout)
        registered, raw_manifests, inventory = (
            vendor_rebuild.load_registration_bundle(registration)
        )
        manifests = {
            customization_id: manifest.validate_manifest(
                data,
                repository_layout,
            )
            for customization_id, data in raw_manifests.items()
        }
        catalog = contracts.load_catalog(registration / "contracts.yaml")
        registry.validate_references(registered, manifests, catalog)
        plan = vendor_rebuild.build_reconstruction_plan(
            registered,
            manifests,
            inventory,
            source_path_owners=vendor_rebuild.load_source_snapshot_owners(
                registration
            ),
        )
    except (
        OSError,
        UnicodeError,
        yaml.YAMLError,
        contracts.ContractError,
        gitprim.GitPrimitiveError,
        layout.LayoutError,
        manifest.ManifestError,
        registry.RegistryError,
        vendor_rebuild.ReconstructionError,
    ) as exc:
        output = {
            "registration": registration_label,
            "checks": [
                {
                    "name": "등록자료 분석",
                    "verdict": verdict.ANALYSIS_ERROR,
                    "detail": str(exc),
                }
            ],
            "release_note": (
                "등록자료를 신뢰할 수 있게 분석하지 못했다. "
                "원인을 수정하고 처음부터 다시 검사해야 한다."
            ),
        }
        emit_result(output, args.output)
        return verdict.to_exit_code(verdict.ANALYSIS_ERROR)

    source_result = vendor_rebuild.inspect_source_inventory(args.repo, plan)
    test_result = contracts.check_required_test_implementations(
        harness.parent, catalog
    )

    owners = yaml.safe_load(
        (registration / "shared-path-owners.yaml").read_text(encoding="utf-8")
    )
    expected_owners = {
        path: list(candidate_ids)
        for path, candidate_ids in plan.shared_candidates
    }
    shared_owner_match = owners == expected_owners

    output = {
        "registration": registration_label,
        "checks": [
            {
                "name": "Manifest 구조와 작성 규칙",
                "verdict": "pass",
                "detail": f"{len(manifests)}개 Manifest",
            },
            {
                "name": "Registry·Manifest·Contract 연결",
                "verdict": "pass",
                "detail": f"{len(registered.entries)}개 BANK-OM",
            },
            {
                "name": "공식 원본과 행내 custom 코드의 변경 경로",
                "verdict": source_result.verdict,
                "detail": f"{len(inventory)}개 경로",
            },
            {
                "name": "공용 파일 소유정보",
                "verdict": "pass" if shared_owner_match else "block",
                "detail": f"{len(owners)}개 공용 경로",
            },
            {
                "name": "필수 테스트 코드 존재",
                "verdict": test_result.verdict,
                "detail": (
                    f"{len({selector for item in catalog.values() for selector in item.required_tests})}"
                    "개 Python pytest"
                ),
            },
        ],
        "reconstruction_plan_digest": plan.digest(),
        "release_note": (
            "이 결과는 검사 입력자료가 서로 일치한다는 뜻이다. "
            "코드 build, test 실행, 담당자 지정, 배포 승인은 별도 단계다."
        ),
    }
    emit_result(output, args.output)

    passed = (
        source_result.verdict == "pass"
        and test_result.verdict == "pass"
        and shared_owner_match
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
