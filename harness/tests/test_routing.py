"""T28 strategy routing tests."""
from acgh import candidate as C
from acgh import routing as R
from acgh import verdict as V

_DIGEST = "sha256:" + "a" * 64


def _lock(strategy):
    data = {
        "schema_version": 1,
        "integration_strategy": strategy,
        "upstream": {
            "repository": "open-metadata/OpenMetadata",
            "base_sha": "a" * 40,
            "target_sha": "b" * 40,
        },
        "candidate": {
            "repository": "bank/vendor",
            "commit_sha": "c" * 40,
            "tree_sha": "d" * 40,
            "artifact_digest": _DIGEST,
        },
    }
    if strategy == C.PATCH_REPLAY:
        data["patch_source_lock_digest"] = "sha256:" + "e" * 64
    return C.parse_candidate_lock(data)


def test_vendor_plan_excludes_replay_mechanics():
    plan = R.build_gate_plan(_lock(C.VENDOR_MERGE))
    assert "vendor-ancestry" in plan.required_gates
    assert "customization-survival" in plan.required_gates
    assert "patch-lock" not in plan.required_gates
    assert "clean-room-replay" not in plan.required_gates


def test_patch_plan_excludes_vendor_mechanics():
    plan = R.build_gate_plan(_lock(C.PATCH_REPLAY))
    assert "patch-lock" in plan.required_gates
    assert "clean-room-replay" in plan.required_gates
    assert "vendor-ancestry" not in plan.required_gates
    assert "customization-survival" not in plan.required_gates


def test_complete_mode_plan_passes():
    lock = _lock(C.VENDOR_MERGE)
    plan = R.build_gate_plan(lock)
    result = R.check_gate_routing(lock, plan.required_gates)
    assert result.verdict == V.PASS
    assert result.reasons[0] == "strategy=vendor-merge"


def test_missing_mode_gate_is_analysis_error():
    lock = _lock(C.VENDOR_MERGE)
    plan = R.build_gate_plan(lock)
    available = set(plan.required_gates) - {"customization-survival"}
    result = R.check_gate_routing(lock, available)
    assert result.verdict == V.ANALYSIS_ERROR
    assert "customization-survival" in result.reasons[0]
