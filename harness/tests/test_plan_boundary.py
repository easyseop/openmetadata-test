from pathlib import Path

from acgh.plancore.boundary import boundary_violations


def test_plancore_has_no_product_literals_or_reverse_dependency():
    assert boundary_violations() == []


def test_boundary_lint_catches_product_literal_mutant(tmp_path: Path):
    (tmp_path / "mutant.py").write_text('RULE = "BANK-OM-999"\n', encoding="utf-8")
    violations = boundary_violations(tmp_path)
    assert violations
    assert "mutant.py" in violations[0]


def test_boundary_lint_catches_integration_import_mutant(tmp_path: Path):
    (tmp_path / "mutant.py").write_text(
        "from acgh.integrations.om import OpenMetadataPlanAdapter\n",
        encoding="utf-8",
    )
    assert boundary_violations(tmp_path)
