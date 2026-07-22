"""T15 result writer + CI adapter tests (부칙 A-1)."""
import copy

import pytest
import yaml

from acgh import result_io as R
from acgh import verdict as V


def _inputs():
    return {
        "repositories": {
            "upstream": {"sha": "e6c665019a583b7938f30fbb7bafb7e1f82c5dd7"},
            "core": {"sha": "b" * 40},
        },
        "patch_source_lock_digest": "sha256:" + "0" * 64,
        "verifier_catalog_digest": "sha256:" + "1" * 64,
    }


def _result(verdict_gates=None):
    gates = verdict_gates or [V.GateResult("reapply", V.PASS, ("ok",))]
    return V.build_result(gates, _inputs(), "0.0.1", run_id="run-1",
                          observational={"duration_ms": 12})


def test_write_then_interpret_roundtrip_pass(tmp_path):
    out = tmp_path / "acgh-result.yaml"
    R.write_result(_result(), out)
    d = R.interpret_result(out, actual_exit=0, expected_inputs=_inputs(),
                           harness_version="0.0.1")
    assert d.verdict == V.PASS and d.exit_code == 0 and d.synthetic is False


def test_write_is_atomic_no_tmp_left(tmp_path):
    out = tmp_path / "acgh-result.yaml"
    R.write_result(_result(), out)
    leftovers = [p.name for p in tmp_path.iterdir() if ".tmp." in p.name]
    assert leftovers == []
    assert out.exists()


def test_block_result_maps_to_exit_1(tmp_path):
    out = tmp_path / "r.yaml"
    R.write_result(_result([V.GateResult("g", V.BLOCK, ("bad",))]), out)
    d = R.interpret_result(out, actual_exit=1, expected_inputs=_inputs())
    assert d.verdict == V.BLOCK and d.exit_code == 1 and not d.synthetic


def test_missing_file_is_synthetic_analysis_error(tmp_path):
    d = R.interpret_result(tmp_path / "nope.yaml", actual_exit=0)
    assert d.verdict == V.ANALYSIS_ERROR and d.exit_code == 3 and d.synthetic


def test_corrupt_yaml_is_analysis_error(tmp_path):
    out = tmp_path / "r.yaml"
    out.write_text("verdict: [unterminated\n")
    d = R.interpret_result(out, actual_exit=0)
    assert d.verdict == V.ANALYSIS_ERROR and d.synthetic


def test_tampered_digest_is_analysis_error(tmp_path):
    out = tmp_path / "r.yaml"
    R.write_result(_result(), out)
    data = yaml.safe_load(out.read_text())
    # Flip the recorded verdict without recomputing the digest.
    data["canonical_payload"]["verdict"] = "pass"
    data["canonical_payload"]["gates"][0]["verdict"] = "block"
    out.write_text(yaml.safe_dump(data))
    d = R.interpret_result(out, actual_exit=0, expected_inputs=_inputs())
    assert d.verdict == V.ANALYSIS_ERROR and d.synthetic


def test_stale_inputs_is_analysis_error(tmp_path):
    out = tmp_path / "r.yaml"
    R.write_result(_result(), out)
    other = copy.deepcopy(_inputs())
    other["repositories"]["core"]["sha"] = "c" * 40  # different candidate
    d = R.interpret_result(out, actual_exit=0, expected_inputs=other)
    assert d.verdict == V.ANALYSIS_ERROR and "stale" in d.reason


def test_exit_result_mismatch_is_analysis_error(tmp_path):
    out = tmp_path / "r.yaml"
    R.write_result(_result(), out)  # verdict pass -> expected exit 0
    d = R.interpret_result(out, actual_exit=1, expected_inputs=_inputs())
    assert d.verdict == V.ANALYSIS_ERROR and "exit/result mismatch" in d.reason


def test_harness_version_mismatch_is_analysis_error(tmp_path):
    out = tmp_path / "r.yaml"
    R.write_result(_result(), out)
    d = R.interpret_result(out, actual_exit=0, expected_inputs=_inputs(),
                           harness_version="9.9.9")
    assert d.verdict == V.ANALYSIS_ERROR and "harness_version" in d.reason


def test_writer_rejects_inconsistent_result(tmp_path):
    bad = _result()
    bad["result_digest"] = "sha256:" + "0" * 64  # wrong digest
    with pytest.raises(R.ResultIOError, match="self-check"):
        R.write_result(bad, tmp_path / "r.yaml")


def test_attestation_invalidated_by_candidate_or_policy_change():
    att = {
        "target_result_digest": "sha256:" + "a" * 64,
        "candidate_sha": "d" * 40,
        "policy_digest": "sha256:" + "e" * 64,
        "approver": "integrator@bank",
    }
    kw = dict(result_digest="sha256:" + "a" * 64, candidate_sha="d" * 40,
              policy_digest="sha256:" + "e" * 64)
    assert R.attestation_is_valid(att, **kw) is True
    assert R.attestation_is_valid(att, **{**kw, "candidate_sha": "f" * 40}) is False
    assert R.attestation_is_valid(att, **{**kw, "policy_digest": "sha256:" + "0" * 64}) is False
    assert R.attestation_is_valid(att, **{**kw, "result_digest": "sha256:" + "0" * 64}) is False


def test_break_glass_expiry():
    att = {
        "target_result_digest": "sha256:" + "a" * 64,
        "candidate_sha": "d" * 40,
        "policy_digest": "sha256:" + "e" * 64,
        "expires_at": "2026-07-22T00:00:00Z",
    }
    kw = dict(result_digest="sha256:" + "a" * 64, candidate_sha="d" * 40,
              policy_digest="sha256:" + "e" * 64)
    assert R.attestation_is_valid(att, **kw, now="2026-07-21T23:59:59Z") is True
    assert R.attestation_is_valid(att, **kw, now="2026-07-22T00:00:01Z") is False
