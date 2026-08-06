from __future__ import annotations

import sys
from pathlib import Path

import pytest

from harness import om_workflow


def test_registration_for_known_version() -> None:
    registration = om_workflow.registration_for("1.13.0")
    assert registration.name == "om-temp-1.13.0"
    assert (registration / "repository-layout.yaml").is_file()


def test_registration_for_unknown_version_is_clear() -> None:
    with pytest.raises(om_workflow.WorkflowInputError, match="등록 폴더가 없습니다"):
        om_workflow.registration_for("9.99.9")


def test_plan_infers_registration_branches_and_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(om_workflow, "timestamp", lambda: "20260730-120000")
    args = type(
        "Args",
        (),
        {
            "version": "1.13.0",
            "repo": Path("/work/OM_TEMP"),
            "output": None,
            "fork_ref": None,
            "custom_ref": None,
            "new_id_input": None,
        },
    )()

    command, selected = om_workflow.plan_command(args)

    assert command[0] == sys.executable
    assert "--registration" in command
    assert str(
        om_workflow.REGISTRATIONS / "om-temp-1.13.0"
    ) in command
    assert "origin/fork/om-1.13.0" in command
    assert "origin/custom/om-1.13.0" in command
    assert str(
        om_workflow.HARNESS
        / "preparation-plans"
        / "om-temp-1.13.0-20260730-120000"
    ) in command
    assert selected["OpenMetadata 포크 브랜치"] == "origin/fork/om-1.13.0"


def test_common_paths_resolve_policy_files() -> None:
    paths = om_workflow.common_paths("1.13.0")
    assert paths["layout"].name == "repository-layout.yaml"
    assert paths["zones"].name == "sensitive-zones.yaml"


def test_registration_validator_falls_back_to_shared_generic_validator() -> None:
    registration = om_workflow.registration_for("1.13.1")
    validator = om_workflow.registration_validator(registration)
    assert validator == (
        om_workflow.REGISTRATIONS
        / "om-temp-1.13.0"
        / "validate_registration_bundle.py"
    )


def test_bootstrap_plan_cli_accepts_any_product_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    argv = [
        "om_workflow.py",
        "bootstrap-plan",
        "--repo",
        "/work/product",
        "--version",
        "42.7",
        "--official-ref",
        "official/42.7",
        "--custom-ref",
        "custom/42.7",
        "--input",
        "/work/business-input.yaml",
        "--output",
        "/work/proposal",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    args = om_workflow.parse_args()

    assert args.command == "bootstrap-plan"
    assert args.version == "42.7"
    assert args.official_ref == "official/42.7"
    assert args.custom_ref == "custom/42.7"
