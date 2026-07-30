#!/usr/bin/env python3
"""Compare official versions against registered upgrade-watch paths."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--harness", type=Path, required=True)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--upstream-base", required=True)
    parser.add_argument("--upstream-target", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.harness))

    from acgh import gitprim
    from acgh import upgrade_watch
    from acgh import vendor_rebuild
    from acgh import verdict

    registry, manifests, _inventory = vendor_rebuild.load_registration_bundle(
        args.registration
    )
    active = {
        customization_id: manifests[customization_id]
        for customization_id in registry.active_ids()
    }
    findings = upgrade_watch.evaluate_upgrade_watch(
        args.repo,
        args.upstream_base,
        args.upstream_target,
        active,
    )
    result = upgrade_watch.to_gate_result(findings)
    output = {
        "upstream": {
            "base": args.upstream_base,
            "target": args.upstream_target,
            "changed_path_count": len(
                gitprim.net_changed_paths(
                    args.repo, args.upstream_base, args.upstream_target
                )
            ),
        },
        "gate": {
            "name": result.name,
            "verdict": result.verdict,
            "meaning": (
                "approval은 자동 실패가 아니라, 영향을 받은 BANK-OM을 "
                "검토한 뒤 적용하라는 뜻이다."
            ),
            "reasons": list(result.reasons),
        },
        "affected_customizations": [
            {
                "customization_id": item.customization_id,
                "changed_watch_path_count": len(item.changed_watch_paths),
                "changed_watch_paths": list(item.changed_watch_paths),
                "changed_configuration_keys": list(
                    item.changed_configuration_keys
                ),
                "changed_dependencies": list(item.changed_dependencies),
            }
            for item in findings
        ],
    }
    rendered = json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return verdict.to_exit_code(result.verdict)


if __name__ == "__main__":
    raise SystemExit(main())
