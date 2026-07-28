import base64
import importlib.util
import json
from pathlib import Path

_PATH = (
    Path(__file__).resolve().parents[1]
    / "registrations"
    / "kb-openmetadata"
    / "runtime_preflight.py"
)
_SPEC = importlib.util.spec_from_file_location("runtime_preflight", _PATH)
RP = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(RP)


def _valid():
    env = {name: "value" for name in RP.REQUIRED}
    for name in RP.URL_FIELDS:
        env[name] = "https://openmetadata.bank.local/page"
    env["DEPLOYED_ARTIFACT_DIGEST"] = "sha256:" + "a" * 64
    env["BANK_BROWSER_STORAGE_STATE_B64"] = base64.b64encode(
        json.dumps({"cookies": [], "origins": []}).encode()
    ).decode()
    return env


def test_complete_environment_is_ready_without_echoing_secrets():
    report = RP.inspect_environment(_valid())
    assert report == {
        "ready": True,
        "missing_fields": [],
        "invalid_fields": [],
        "checked_field_count": len(RP.REQUIRED),
        "secrets_echoed": False,
    }


def test_missing_and_malformed_environment_fails_closed():
    env = _valid()
    env["OPENMETADATA_AUTH_TOKEN"] = ""
    env["BANK_IME_EDITOR_URL"] = "not-a-url"
    env["DEPLOYED_ARTIFACT_DIGEST"] = "latest"
    env["BANK_BROWSER_STORAGE_STATE_B64"] = "not-base64"
    report = RP.inspect_environment(env)
    assert not report["ready"]
    assert report["missing_fields"] == ["OPENMETADATA_AUTH_TOKEN"]
    assert len(report["invalid_fields"]) == 3
    assert "value" not in json.dumps(report)
