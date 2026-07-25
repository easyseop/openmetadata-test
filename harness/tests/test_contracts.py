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


def _implementation_catalog(*selectors):
    return C.parse_catalog({
        "schema_version": 1,
        "contracts": [{
            "id": "CONTRACT-X",
            "title": "implemented test",
            "required_tests": list(selectors),
        }],
    })


def test_required_test_implementation_gate_passes_function_and_method(tmp_path):
    test_file = tmp_path / "tests" / "bank" / "test_contract.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text(
        "def test_function():\n"
        "    pass\n\n"
        "class TestContract:\n"
        "    def test_method(self):\n"
        "        pass\n",
        encoding="utf-8",
    )
    catalog = _implementation_catalog(
        "tests/bank/test_contract.py::test_function",
        "tests/bank/test_contract.py::TestContract::test_method[param]",
    )

    result = C.check_required_test_implementations(tmp_path, catalog)

    assert result.verdict == V.PASS
    assert result.reasons == ("implemented_required_tests=2",)


def test_required_test_implementation_gate_blocks_missing_and_unsafe(tmp_path):
    catalog = _implementation_catalog(
        "tests/bank/test_missing.py::test_missing",
        "../outside.py::test_escape",
    )

    result = C.check_required_test_implementations(tmp_path, catalog)

    assert result.verdict == V.BLOCK
    assert len(result.reasons) == 2


def test_required_test_implementation_gate_parse_error_is_analysis_error(
    tmp_path,
):
    test_file = tmp_path / "tests" / "bank" / "test_bad.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_bad(:\n", encoding="utf-8")
    catalog = _implementation_catalog(
        "tests/bank/test_bad.py::test_bad",
    )

    result = C.check_required_test_implementations(tmp_path, catalog)

    assert result.verdict == V.ANALYSIS_ERROR
    assert "cannot parse required test implementation" in result.reasons[0]


def test_required_test_implementation_gate_blocks_empty_catalog(tmp_path):
    catalog = C.parse_catalog({"schema_version": 1, "contracts": []})

    result = C.check_required_test_implementations(tmp_path, catalog)

    assert result.verdict == V.BLOCK
    assert result.reasons == (
        "contract catalog has no required test selectors",
    )
