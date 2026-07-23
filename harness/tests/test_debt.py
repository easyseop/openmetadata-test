"""T43 debt-gate tests (pure threshold logic — synthetic)."""
from acgh import debt as D
from acgh import verdict as V


def test_within_budget_passes():
    r = D.evaluate_debt({"core_patch_count": 10, "changed_lines": 500,
                         "conflict_rate": 0.05, "hotspot_overlap": 1})
    assert r.verdict == V.PASS


def test_over_soft_is_approval():
    r = D.evaluate_debt({"core_patch_count": 25})  # >20 soft, <40 hard
    assert r.verdict == V.APPROVAL
    assert any("soft" in x for x in r.reasons)


def test_over_hard_is_block():
    r = D.evaluate_debt({"conflict_rate": 0.5})  # >0.35 hard
    assert r.verdict == V.BLOCK
    assert any("hard" in x for x in r.reasons)


def test_hard_dominates_soft():
    r = D.evaluate_debt({"core_patch_count": 25, "changed_lines": 9000})
    assert r.verdict == V.BLOCK  # changed_lines over hard wins


def test_unknown_metric_ignored():
    r = D.evaluate_debt({"made_up_metric": 999999})
    assert r.verdict == V.PASS
