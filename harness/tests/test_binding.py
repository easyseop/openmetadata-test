"""T62 SHA-binding tests. pin() runs against the real OM mirror."""
import pytest

from acgh import binding as B
from acgh import patchlock as P
from acgh import result_io as R
from acgh import verdict as V

_UPSTREAM_A = "e6c665019a583b7938f30fbb7bafb7e1f82c5dd7"
_DIGEST = "sha256:" + "0" * 64


def test_pin_real_mirror_ref(om_mirror):
    assert B.pin(str(om_mirror), "UPSTREAM_A") == _UPSTREAM_A


def test_pin_bogus_ref_raises(om_mirror):
    with pytest.raises(B.BindingError):
        B.pin(str(om_mirror), "no-such-ref-xyz")


def test_build_inputs_shape_and_sorted():
    inp = B.build_repository_inputs(
        {"upstream": _UPSTREAM_A, "core": "b" * 40},
        patch_source_lock_digest=_DIGEST, verifier_catalog_digest=_DIGEST,
    )
    assert list(inp["repositories"].keys()) == ["core", "upstream"]  # sorted
    assert inp["repositories"]["upstream"] == {"sha": _UPSTREAM_A}
    assert inp["patch_source_lock_digest"] == _DIGEST


def test_build_inputs_rejects_unpinned_value():
    with pytest.raises(B.BindingError, match="not a full 40-hex SHA"):
        B.build_repository_inputs(
            {"upstream": "main"},  # branch name, not a SHA
            patch_source_lock_digest=_DIGEST, verifier_catalog_digest=_DIGEST,
        )


def test_build_inputs_rejects_bad_digest():
    with pytest.raises(B.BindingError, match="digest"):
        B.build_repository_inputs(
            {"upstream": _UPSTREAM_A},
            patch_source_lock_digest="nope", verifier_catalog_digest=_DIGEST,
        )


def test_assert_lock_binding():
    lock = P.parse_source_lock({
        "schema_version": 1,
        "source_release_sha": _UPSTREAM_A,
        "patch_series": [{"id": "BANK-OM-001", "revision": 1,
                          "source_commits": ["a" * 40]}],
    })
    inp = B.build_repository_inputs(
        {"upstream": _UPSTREAM_A},
        patch_source_lock_digest=lock.digest(), verifier_catalog_digest=_DIGEST,
    )
    B.assert_lock_binding(inp, lock)  # matches -> no raise
    bad = dict(inp, patch_source_lock_digest=_DIGEST)
    with pytest.raises(B.BindingError):
        B.assert_lock_binding(bad, lock)


def test_bound_inputs_flow_into_result_and_stale_check(tmp_path):
    # T62 inputs -> T13 result -> T15 interpret: same inputs pass, changed fail.
    inp = B.build_repository_inputs(
        {"upstream": _UPSTREAM_A},
        patch_source_lock_digest=_DIGEST, verifier_catalog_digest=_DIGEST,
    )
    result = V.build_result([V.GateResult("g", V.PASS, ())], inp, "0.0.1",
                            run_id="r1")
    out = tmp_path / "acgh-result.yaml"
    R.write_result(result, out)
    assert R.interpret_result(out, 0, expected_inputs=inp).verdict == V.PASS
    moved = B.build_repository_inputs(
        {"upstream": "c" * 40},
        patch_source_lock_digest=_DIGEST, verifier_catalog_digest=_DIGEST,
    )
    assert R.interpret_result(out, 0, expected_inputs=moved).verdict == V.ANALYSIS_ERROR
