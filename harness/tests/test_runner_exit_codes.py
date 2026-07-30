"""Every gate runner must map its verdict through the shared exit-code table.

`verdict.py` fixes the 4-state contract (P0-3/P0-4) and `test_verdict.py`
proves the table itself. Nothing proved that the *runners* actually use it, so
a runner could collapse approval/block/analysis_error into one exit code while
the whole suite stayed green. These tests close that gap at both levels:

1. structurally — no runner may decide its exit code with a hand-written
   comparison; and
2. behaviourally — a runner given an approval-only gate set must exit 2, not 1
   and not 0.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

from acgh import verdict as V

_HARNESS = Path(__file__).resolve().parents[1]

# Runners whose process exit code carries a gate verdict.
_RUNNERS = (
    "run_upgrade_watch.py",
    "registrations/kb-openmetadata/run_source_candidate_gates.py",
    "registrations/kb-openmetadata/run_upgrade_risk_gates.py",
    "registrations/om-temp-1.13.0/validate_registration_bundle.py",
)


def _main_returns(path: Path) -> list[ast.expr]:
    """Every `return <expr>` inside the module-level ``main`` function."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            return [
                child.value
                for child in ast.walk(node)
                if isinstance(child, ast.Return) and child.value is not None
            ]
    raise AssertionError(f"{path} has no module-level main()")


def _is_standard_exit(expr: ast.expr) -> bool:
    return (
        isinstance(expr, ast.Call)
        and isinstance(expr.func, ast.Attribute)
        and expr.func.attr == "to_exit_code"
    )


@pytest.mark.parametrize("relative", _RUNNERS)
def test_runner_exit_code_comes_from_the_verdict_table(relative):
    path = _HARNESS / relative
    returns = _main_returns(path)
    assert returns, f"{relative}: main() returns nothing"
    offenders = [
        ast.unparse(expr) for expr in returns if not _is_standard_exit(expr)
    ]
    assert not offenders, (
        f"{relative}: main() must return verdict.to_exit_code(...); "
        f"hand-written exit codes found: {offenders}"
    )


def test_approval_only_run_exits_two_not_one(monkeypatch, tmp_path):
    """An approval-only gate set must be distinguishable from a failure."""
    sys.path.insert(0, str(_HARNESS))
    import run_upgrade_watch
    from acgh import gitprim, upgrade_watch, vendor_rebuild

    registration = tmp_path / "registration"
    registration.mkdir()

    class _Registry:
        def active_ids(self):
            return ("BANK-OM-001",)

    monkeypatch.setattr(
        vendor_rebuild,
        "load_registration_bundle",
        lambda _dir: (_Registry(), {"BANK-OM-001": {}}, []),
    )
    monkeypatch.setattr(
        upgrade_watch, "evaluate_upgrade_watch", lambda *a, **k: ()
    )
    monkeypatch.setattr(
        upgrade_watch,
        "to_gate_result",
        lambda _findings: V.GateResult(
            "upgrade-watch", V.APPROVAL, ("watched path changed upstream",)
        ),
    )
    monkeypatch.setattr(gitprim, "net_changed_paths", lambda *a, **k: [])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_upgrade_watch.py",
            "--repo", str(tmp_path),
            "--harness", str(_HARNESS),
            "--registration", str(registration),
            "--upstream-base", "A",
            "--upstream-target", "B",
        ],
    )

    assert run_upgrade_watch.main() == V.EXIT_CODE[V.APPROVAL] == 2


def test_empty_gate_set_never_exits_zero():
    """P0-4: nothing judged must not read as success."""
    assert V.to_exit_code(V.aggregate([])) == V.EXIT_CODE[V.ANALYSIS_ERROR]
    # The historical `all(g.verdict == "pass" for g in gates)` idiom returns
    # True for an empty list, i.e. exit 0. Guard against its reintroduction.
    assert all(g == "pass" for g in []) is True
