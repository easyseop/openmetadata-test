"""T62 pytest adapter tests."""
from pathlib import Path

import pytest

from acgh import pytest_runs as P


def _junit(path: Path, *, tests=1, failures=0, errors=0, skipped=0):
    path.write_text(
        (
            f'<testsuites><testsuite tests="{tests}" failures="{failures}" '
            f'errors="{errors}" skipped="{skipped}"/></testsuites>'
        ),
        encoding="utf-8",
    )


@pytest.mark.parametrize(
    ("counts", "exit_code", "expected"),
    [
        ({}, 0, "pass"),
        ({"skipped": 1}, 0, "skipped"),
        ({"failures": 1}, 1, "fail"),
        ({"errors": 1}, 1, "error"),
    ],
)
def test_junit_outcome_is_fail_closed(tmp_path, counts, exit_code, expected):
    output = tmp_path / "junit.xml"
    _junit(output, **counts)
    assert P.parse_junit_outcome(output, exit_code=exit_code) == expected


def test_junit_missing_empty_or_exit_mismatch_is_harness_error(tmp_path):
    with pytest.raises(P.PytestRunError, match="cannot read"):
        P.parse_junit_outcome(tmp_path / "missing.xml", exit_code=0)

    output = tmp_path / "junit.xml"
    _junit(output, tests=0)
    with pytest.raises(P.PytestRunError, match="no tests"):
        P.parse_junit_outcome(output, exit_code=0)

    _junit(output, failures=1)
    with pytest.raises(P.PytestRunError, match="mismatch"):
        P.parse_junit_outcome(output, exit_code=0)


def test_required_runner_retains_retry_history(monkeypatch):
    outcomes = iter(["fail", "pass", "skipped"])
    monkeypatch.setattr(P, "run_selector", lambda *args, **kwargs: next(outcomes))
    attempts = P.run_required_tests(
        ".",
        ["tests/b.py::test_b", "tests/a.py::test_a"],
        retries=1,
    )
    assert [
        (item.test_id, item.attempt, item.outcome) for item in attempts
    ] == [
        ("tests/a.py::test_a", 1, "fail"),
        ("tests/a.py::test_a", 2, "pass"),
        ("tests/b.py::test_b", 1, "skipped"),
    ]


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("def test_contract(): assert True\n", "pass"),
        (
            "import pytest\n"
            "def test_contract(): pytest.skip('runtime unavailable')\n",
            "skipped",
        ),
        ("def test_contract(): assert False\n", "fail"),
    ],
)
def test_selector_runs_in_a_fresh_pytest_process(tmp_path, body, expected):
    test_file = tmp_path / "tests" / "test_contract.py"
    test_file.parent.mkdir()
    test_file.write_text(body, encoding="utf-8")
    assert (
        P.run_selector(tmp_path, "tests/test_contract.py::test_contract")
        == expected
    )


def test_suite_digest_binds_selector_and_metadata_bytes(tmp_path):
    test_file = tmp_path / "tests" / "test_contract.py"
    test_file.parent.mkdir()
    test_file.write_text("def test_contract(): pass\n", encoding="utf-8")
    catalog = tmp_path / "contracts.yaml"
    catalog.write_text("schema_version: 1\n", encoding="utf-8")
    selector = "tests/test_contract.py::test_contract"

    first = P.suite_digest(
        tmp_path, [selector], metadata_paths=[catalog]
    )
    assert first == P.suite_digest(
        tmp_path, [selector], metadata_paths=[catalog]
    )
    test_file.write_text("def test_contract(): assert True\n", encoding="utf-8")
    assert first != P.suite_digest(
        tmp_path, [selector], metadata_paths=[catalog]
    )
