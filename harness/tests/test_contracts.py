"""T60 contract catalog + binding tests (pure judgment logic — synthetic OK)."""
import pytest

from acgh import contracts as C
from acgh import verdict as V


def _catalog():
    return C.parse_catalog({
        "schema_version": 1,
        "contracts": [
            {"id": "CONTRACT-SSO-LOGIN", "title": "tenant binds to session",
             "invariant": "userId 같아도 tenant 다르면 다른 사용자",
             "required_tests": ["tests/bank/test_sso.py::test_tenant_binding"],
             "customization_ids": ["BANK-OM-001"]},
            {"id": "CONTRACT-AUTHZ", "title": "authz rules preserved",
             "required_tests": ["tests/bank/test_authz.py::test_role"]},
        ],
    })


def _manifest(contracts=None, direct=None):
    return {"customization_id": "BANK-OM-001", "kind": "core-patch",
            "assurance": {"contracts": contracts or [], "direct_tests": direct or []}}


def test_effective_tests_union():
    cat = _catalog()
    m = _manifest(contracts=["CONTRACT-SSO-LOGIN"],
                  direct=["tests/bank/test_extra.py::test_x"])
    assert C.effective_tests(m, cat) == {
        "tests/bank/test_sso.py::test_tenant_binding",
        "tests/bank/test_extra.py::test_x",
    }
    assert C.check_binding(m, cat).verdict == V.PASS


def test_unknown_contract_blocks():
    m = _manifest(contracts=["CONTRACT-NOPE"])
    with pytest.raises(C.ContractError, match="unknown contract"):
        C.effective_tests(m, _catalog())
    assert C.check_binding(m, _catalog()).verdict == V.BLOCK


def test_direct_and_derived_overlap_blocks():
    # Same test declared as a direct test AND as a contract's required test.
    m = _manifest(contracts=["CONTRACT-SSO-LOGIN"],
                  direct=["tests/bank/test_sso.py::test_tenant_binding"])
    with pytest.raises(C.ContractError, match="both as direct and contract-derived"):
        C.effective_tests(m, _catalog())


def test_duplicate_contract_id_in_catalog_rejected():
    with pytest.raises(C.ContractError, match="duplicate contract id"):
        C.parse_catalog({
            "schema_version": 1,
            "contracts": [
                {"id": "CONTRACT-X", "title": "a", "required_tests": ["t::a"]},
                {"id": "CONTRACT-X", "title": "b", "required_tests": ["t::b"]},
            ],
        })


def test_bad_contract_id_pattern_rejected():
    with pytest.raises(C.ContractError, match="schema"):
        C.parse_catalog({
            "schema_version": 1,
            "contracts": [{"id": "sso", "title": "x", "required_tests": ["t::a"]}],
        })


def test_no_assurance_is_empty_and_passes():
    m = {"customization_id": "BANK-OM-002", "kind": "core-patch"}
    assert C.effective_tests(m, _catalog()) == set()
    assert C.check_binding(m, _catalog()).verdict == V.PASS


def test_multiple_contracts_merge():
    cat = _catalog()
    m = _manifest(contracts=["CONTRACT-SSO-LOGIN", "CONTRACT-AUTHZ"])
    assert C.effective_tests(m, cat) == {
        "tests/bank/test_sso.py::test_tenant_binding",
        "tests/bank/test_authz.py::test_role",
    }
