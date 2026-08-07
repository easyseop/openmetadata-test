"""Fail-closed behavior for the OM_TEMP registration validator."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from acgh import vendor_rebuild

_ROOT = Path(__file__).resolve().parents[2]
_REGISTRATION = _ROOT / "harness" / "registrations" / "om-temp-1.13.0"
_SCRIPT = _REGISTRATION / "validate_registration_bundle.py"


def _load_script():
    spec = importlib.util.spec_from_file_location(
        "om_temp_registration_validator",
        _SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_reconstruction_error_is_structured_analysis_error(
    monkeypatch,
    tmp_path,
):
    module = _load_script()
    output = tmp_path / "result.json"

    def fail_plan(*_args, **_kwargs):
        raise vendor_rebuild.ReconstructionError(
            "BANK-OM-008: explicit provenance is required"
        )

    monkeypatch.setattr(
        vendor_rebuild,
        "build_reconstruction_plan",
        fail_plan,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(_SCRIPT),
            "--repo",
            str(tmp_path / "product"),
            "--registration",
            str(_REGISTRATION),
            "--output",
            str(output),
        ],
    )

    assert module.main() == 3
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["checks"] == [
        {
            "name": "등록자료 분석",
            "verdict": "analysis_error",
            "detail": "BANK-OM-008: explicit provenance is required",
        }
    ]


def test_emit_result_creates_missing_output_directory(tmp_path, capsys):
    module = _load_script()
    output = tmp_path / "new-evidence" / "nested" / "result.json"
    result = {"checks": [], "release_note": "saved"}

    module.emit_result(result, output)

    assert json.loads(output.read_text(encoding="utf-8")) == result
    assert json.loads(capsys.readouterr().out) == result
