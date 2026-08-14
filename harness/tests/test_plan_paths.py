from pathlib import Path

from acgh.plancore.paths import directory_digest


def test_directory_digest_ignores_only_python_bytecode_artifacts(tmp_path: Path):
    root = tmp_path / "catalog"
    root.mkdir()
    source = root / "validate.py"
    source.write_text("CHECK = 'trusted'\n", encoding="utf-8")
    expected = directory_digest(root)

    cache = root / "__pycache__"
    cache.mkdir()
    (cache / "validate.cpython-311.pyc").write_bytes(b"first runner cache")
    (cache / "validate.pyo").write_bytes(b"optimized cache")
    (root / "standalone.pyc").write_bytes(b"standalone cache")
    (root / "standalone.pyo").write_bytes(b"standalone optimized cache")

    assert directory_digest(root) == expected

    source.write_text("CHECK = 'tampered'\n", encoding="utf-8")

    assert directory_digest(root) != expected
