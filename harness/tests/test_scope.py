"""T33 assurance-scope tests: the completeness boundary is in the gate output."""
from acgh import evidence as E
from acgh import scope as S
from acgh import verdict as V


def _result():
    return V.build_result([V.GateResult("g", V.PASS, ())],
                          {"repositories": {"upstream": {"sha": "a" * 40}}},
                          "0.0.1", run_id="r1")


def test_scope_block_has_non_guarantees():
    blk = S.scope_block()
    assert blk["gate_family"] == "등록·재적용 완전성 게이트"
    assert blk["non_guarantees"]  # must be non-empty
    joined = " ".join(blk["non_guarantees"])
    assert "기능 보장이 아니" in joined  # functional correctness is NOT guaranteed


def test_evidence_card_embeds_scope():
    card = E.build_evidence_card(_result())
    assert card["assurance_scope"] == S.scope_block()
    # Card still validates (schema now requires assurance_scope).
    E.validate_evidence_card(card)


def test_card_without_scope_is_rejected():
    card = E.build_evidence_card(_result())
    del card["assurance_scope"]
    import pytest
    with pytest.raises(E.EvidenceError, match="schema"):
        E.validate_evidence_card(card)
