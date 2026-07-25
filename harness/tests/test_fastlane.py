"""T71 fast-lane routing tests."""
from acgh import candidate as C
from acgh import fastlane as F
from acgh import verdict as V


def _lock():
    return C.parse_candidate_lock({
        "schema_version": 1,
        "integration_strategy": "vendor-merge",
        "upstream": {
            "repository": "open-metadata/OpenMetadata",
            "base_sha": "a" * 40,
            "target_sha": "b" * 40,
        },
        "candidate": {
            "repository": "bank/vendor",
            "commit_sha": "c" * 40,
            "tree_sha": "d" * 40,
            "artifact_digest": "sha256:" + "e" * 64,
        },
    })


def test_config_lane_is_lightweight_but_not_empty():
    plan = F.build_fast_lane("config")
    assert "configuration-render" in plan.required_gates
    assert "smoke-tests" in plan.required_gates
    assert "vendor-ancestry" not in plan.required_gates
    assert "verdict-integrity" in plan.required_gates


def test_core_patch_expands_full_strategy_route():
    plan = F.build_fast_lane("core-patch", candidate_lock=_lock())
    assert "vendor-ancestry" in plan.required_gates
    assert "customization-survival" in plan.required_gates
    assert "test-candidate-binding" in plan.required_gates


def test_mixed_change_receives_union_not_easier_lane():
    plan = F.build_fast_lane(["config", "governance"])
    assert "configuration-render" in plan.required_gates
    assert "policy-base-evaluation" in plan.required_gates
    assert "two-person-approval" in plan.required_gates


def test_missing_lane_gate_is_analysis_error():
    plan = F.build_fast_lane("extension")
    available = set(plan.required_gates) - {"sdk-contract"}
    result = F.check_fast_lane("extension", available)
    assert result.verdict == V.ANALYSIS_ERROR
    assert "sdk-contract" in result.reasons[0]


def test_unknown_or_unbound_core_lane_fails_closed():
    assert F.check_fast_lane("unknown", []).verdict == V.ANALYSIS_ERROR
    assert F.check_fast_lane("core-patch", []).verdict == V.ANALYSIS_ERROR
