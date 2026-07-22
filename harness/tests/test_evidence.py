"""T14 change-evidence card tests (G4 / §7 LLM advisory-only)."""
import pytest

from acgh import evidence as E
from acgh import verdict as V


def _inputs():
    return {"repositories": {"upstream": {"sha": "e6c6650" + "0" * 33}}}


def _result(gates):
    return V.build_result(gates, _inputs(), "0.0.1", run_id="run-1",
                          observational={"duration_ms": 5})


def test_card_aggregates_gates_and_separates_fields():
    gates = [V.GateResult("reapply", V.PASS, ("clean",)),
             V.GateResult("drift", V.APPROVAL, ("watched path changed",))]
    card = E.build_evidence_card(
        _result(gates),
        evidence_by_gate={"drift": ["diff-tree: openmetadata-spec/.../auth.json"]},
        approvals=[{"approver": "integrator@bank",
                    "target_result_digest": "sha256:" + "a" * 64}],
        llm_suggestions=[{"gate": "drift", "memo": "auth schema field renamed",
                          "severity_hint": "high"}],
    )
    assert card["machine_verdict"] == V.APPROVAL
    assert len(card["gates"]) == 2
    assert card["gates"][1]["evidence"] == [
        "diff-tree: openmetadata-spec/.../auth.json"
    ]
    assert card["approvals"][0]["approver"] == "integrator@bank"
    assert card["llm_suggestions"][0]["severity_hint"] == "high"


def test_llm_and_approvals_do_not_change_machine_verdict_or_digest():
    gates = [V.GateResult("g", V.BLOCK, ("core conflict",))]
    result = _result(gates)
    plain = E.build_evidence_card(result)
    loud = E.build_evidence_card(
        result,
        approvals=[{"approver": "x", "target_result_digest": "sha256:" + "b" * 64}],
        llm_suggestions=[{"gate": "g", "memo": "looks fine to me", "severity_hint": "info"}],
    )
    # Advice is attached but the machine judgment is untouched.
    assert plain["machine_verdict"] == loud["machine_verdict"] == V.BLOCK
    assert plain["result_digest"] == loud["result_digest"]


def test_llm_suggestion_cannot_carry_a_verdict():
    # The schema forbids a 'verdict' key on an LLM suggestion (§7).
    result = _result([V.GateResult("g", V.PASS, ())])
    with pytest.raises(E.EvidenceError, match="schema"):
        E.build_evidence_card(
            result,
            llm_suggestions=[{"gate": "g", "memo": "override", "verdict": "pass"}],
        )


def test_tampered_headline_verdict_rejected():
    # Downgrading the headline below what the gates justify must fail.
    result = _result([V.GateResult("g", V.BLOCK, ("bad",))])
    card = E.build_evidence_card(result)
    card["machine_verdict"] = "pass"
    with pytest.raises(E.EvidenceError, match="aggregate of gates"):
        E.validate_evidence_card(card)


def test_analysis_error_headline_preserved():
    result = _result([V.GateResult("g", V.ANALYSIS_ERROR, ("gate crashed",))])
    card = E.build_evidence_card(result)
    assert card["machine_verdict"] == V.ANALYSIS_ERROR
