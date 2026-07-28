"""T70 policy self-protection tests (pure path logic — synthetic)."""
from acgh import policy_guard as PG
from acgh import verdict as V

_POL = "harness/policies/sensitive-zones.yaml"
_CODE = "openmetadata-service/src/main/java/org/openmetadata/service/security/X.java"


def test_no_policy_change_passes():
    r = PG.check_self_approval([_CODE], used_policy_ref="cand", base_ref="base")
    assert r.verdict == V.PASS


def test_policy_change_judged_by_base_is_approval():
    r = PG.check_self_approval([_CODE, _POL], used_policy_ref="base", base_ref="base")
    assert r.verdict == V.APPROVAL


def test_policy_change_judged_by_candidate_is_bypass_block():
    r = PG.check_self_approval([_POL], used_policy_ref="cand", base_ref="base")
    assert r.verdict == V.BLOCK
    assert any("self-weakening" in x for x in r.reasons)


def test_evaluation_ref_is_base_when_policy_touched():
    assert PG.evaluation_policy_ref("base", "cand", [_POL]) == "base"
    assert PG.evaluation_policy_ref("base", "cand", [_CODE]) == "cand"


def test_workflow_change_is_policy():
    r = PG.check_self_approval([".github/workflows/ci.yml"],
                               used_policy_ref="cand", base_ref="base")
    assert r.verdict == V.BLOCK


def test_checker_and_schema_changes_are_policy():
    paths = [
        "harness/acgh/drift.py",
        "harness/acgh/schema/manifest.schema.json",
        "harness/tests/test_drift.py",
    ]
    assert set(PG.touched_policy_paths(paths)) == set(paths)


def test_registration_and_governance_docs_are_policy():
    paths = [
        "harness/registrations/kb-openmetadata/manifests/BANK-OM-001.yaml",
        "docs/02-설계/openmetadata_governance_requirements.md",
        "docs/03-기술참조/openmetadata_verifier_catalog.md",
        "docs/04-진행/openmetadata_build_plan.md",
        "STATUS.md",
        "CLAUDE.md",
    ]
    assert set(PG.touched_policy_paths(paths)) == set(paths)
