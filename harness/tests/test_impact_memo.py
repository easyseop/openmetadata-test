"""T80/T81 advisory Impact Memo tests."""
import copy
from pathlib import Path

import pytest

from acgh import evidence as E
from acgh import impact_memo as M
from acgh import verdict as V

_SHA = "a" * 40


def _evidence(provider="upgrade-watch"):
    return {
        "provider": provider,
        "reference": "BANK-OM-005:SchemaEditor.tsx",
        "snapshot_sha": _SHA,
    }


def _memo():
    return {
        "schema_version": 1,
        "snapshot_sha": _SHA,
        "input_digest": "sha256:" + "b" * 64,
        "model_id": "review-model-1",
        "prompt_version": "impact-v1",
        "affected_customization_ids": ["BANK-OM-005"],
        "facts": [{
            "claim": "SchemaEditor의 조합 이벤트 처리 코드가 커스터마이징되어 있다.",
            "evidence": [_evidence("git-diff")],
        }],
        "inferences": [{
            "claim": "에디터 업그레이드가 한글 조합 입력에 영향을 줄 수 있다.",
            "evidence": [_evidence()],
        }],
        "unknowns": ["실제 브라우저 조합 입력 결과는 아직 실행하지 않았다."],
        "recommended_tests": [
            "tests/bank/contracts/test_korean_ime.py::test_hangul_composition_roundtrip"
        ],
    }


def test_grounded_memo_has_stable_digest_and_card_compatible_summary():
    memo = _memo()
    assert M.impact_memo_digest(memo).startswith("sha256:")
    suggestion = M.to_evidence_suggestion(memo)
    result = V.build_result(
        [V.GateResult("upgrade-watch", V.APPROVAL, ("watch hit",))],
        {"repositories": {"candidate": {"sha": _SHA}}},
        "1.0",
        run_id="memo",
    )
    card = E.build_evidence_card(result, llm_suggestions=[suggestion])
    assert card["machine_verdict"] == V.APPROVAL
    assert "memo_digest=sha256:" in card["llm_suggestions"][0]["memo"]


def test_memo_cannot_carry_verdict_command_or_deployment_action():
    for forbidden in ("verdict", "command", "deployment_action"):
        memo = _memo()
        memo[forbidden] = "pass"
        with pytest.raises(M.ImpactMemoError, match="schema"):
            M.validate_impact_memo(memo)


def test_every_claim_requires_evidence():
    memo = _memo()
    memo["inferences"][0]["evidence"] = []
    with pytest.raises(M.ImpactMemoError, match="schema"):
        M.validate_impact_memo(memo)


def test_evidence_must_bind_the_same_snapshot():
    memo = _memo()
    memo["facts"][0]["evidence"][0]["snapshot_sha"] = "0" * 40
    with pytest.raises(M.ImpactMemoError, match="snapshot"):
        M.validate_impact_memo(memo)


def test_no_impact_claim_is_forbidden_but_no_candidate_wording_is_allowed():
    memo = _memo()
    memo["facts"][0]["claim"] = "영향 없음"
    with pytest.raises(M.ImpactMemoError, match="forbidden certainty"):
        M.validate_impact_memo(memo)

    memo = _memo()
    memo["affected_customization_ids"] = []
    memo["facts"] = []
    memo["inferences"] = []
    memo["unknowns"] = ["확인된 후보 없음; 런타임 동작은 미확인이다."]
    suggestion = M.to_evidence_suggestion(memo)
    assert "확인된 후보 없음" in suggestion["memo"]
    assert suggestion["severity_hint"] == "info"


def test_quality_metrics_report_recall_false_positive_and_adoption():
    memo = _memo()
    memo["affected_customization_ids"].append("BANK-OM-007")
    metrics = M.assess_memo_quality(
        memo,
        known_impacted_ids={"BANK-OM-005", "BANK-OM-006"},
        reviewer_adopted_ids={"BANK-OM-005"},
    )
    assert metrics["recall"] == 0.5
    assert metrics["false_positive_rate"] == 0.5
    assert metrics["adoption_rate"] == 0.5
    assert metrics["ungrounded_claim_rate"] == 0.0


def test_module_has_no_execution_or_network_client_imports():
    source = Path(M.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "import subprocess",
        "import socket",
        "import requests",
        "import httpx",
        "import urllib",
    ):
        assert forbidden not in source
