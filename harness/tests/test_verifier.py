"""T50 declarative-verifier tests. file_hash_equals uses real OM content."""
import hashlib

from acgh import verifier as VF
from acgh import verdict as V


def _write(root, rel, content):
    fp = root / rel
    fp.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        fp.write_bytes(content)
    else:
        fp.write_text(content)


def test_document_query_assert_pass_and_fail(tmp_path):
    _write(tmp_path, "conf/auth.yaml",
           "authenticationConfiguration:\n  provider: saml\n")
    ok = VF.run_verifier(
        {"type": "document_query_assert", "file": "conf/auth.yaml",
         "pointer": "/authenticationConfiguration/provider", "equals": "saml"},
        str(tmp_path))
    assert ok.verdict == V.PASS
    bad = VF.run_verifier(
        {"type": "document_query_assert", "file": "conf/auth.yaml",
         "pointer": "/authenticationConfiguration/provider", "equals": "google"},
        str(tmp_path))
    assert bad.verdict == V.BLOCK  # ran, assertion false


def test_document_query_missing_file_is_analysis_error(tmp_path):
    r = VF.run_verifier(
        {"type": "document_query_assert", "file": "nope.yaml",
         "pointer": "/x", "equals": 1}, str(tmp_path))
    assert r.verdict == V.ANALYSIS_ERROR


def test_unresolvable_pointer_is_analysis_error(tmp_path):
    _write(tmp_path, "d.json", '{"a": {"b": 1}}')
    r = VF.run_verifier(
        {"type": "document_query_assert", "file": "d.json",
         "pointer": "/a/z", "equals": 1}, str(tmp_path))
    assert r.verdict == V.ANALYSIS_ERROR


def test_file_hash_equals_on_real_om_content(tmp_path, om_auth_content, om_auth_path):
    _write(tmp_path, om_auth_path, om_auth_content)
    real = "sha256:" + hashlib.sha256(om_auth_content.encode()).hexdigest()
    ok = VF.run_verifier(
        {"type": "file_hash_equals", "file": om_auth_path, "sha256": real},
        str(tmp_path))
    assert ok.verdict == V.PASS
    bad = VF.run_verifier(
        {"type": "file_hash_equals", "file": om_auth_path,
         "sha256": "sha256:" + "0" * 64}, str(tmp_path))
    assert bad.verdict == V.BLOCK


def test_python_module_present_static(tmp_path):
    _write(tmp_path, "ingestion/src/metadata/foo.py", "x = 1\n")
    present = VF.run_verifier(
        {"type": "python_module_present",
         "module_path": "ingestion/src/metadata/foo.py"}, str(tmp_path))
    assert present.verdict == V.PASS
    absent = VF.run_verifier(
        {"type": "python_module_present",
         "module_path": "ingestion/src/metadata/bar.py"}, str(tmp_path))
    assert absent.verdict == V.BLOCK


def test_executable_verifier_refused(tmp_path):
    r = VF.run_verifier({"type": "python_import_succeeds", "module": "os"},
                        str(tmp_path))
    assert r.verdict == V.ANALYSIS_ERROR
    assert "sandbox" in r.reason


def test_unknown_type_is_analysis_error(tmp_path):
    r = VF.run_verifier({"type": "curl_and_run"}, str(tmp_path))
    assert r.verdict == V.ANALYSIS_ERROR


def test_path_escape_blocked(tmp_path):
    # '..' in a verifier path must not read outside the candidate root.
    r = VF.run_verifier(
        {"type": "file_hash_equals", "file": "../secret", "sha256": "0" * 64},
        str(tmp_path))
    assert r.verdict == V.ANALYSIS_ERROR  # normalize_path rejects '..'


def test_run_verifiers_aggregates(tmp_path):
    _write(tmp_path, "d.json", '{"a": 1}')
    gate, results = VF.run_verifiers([
        {"type": "document_query_assert", "file": "d.json", "pointer": "/a", "equals": 1},
        {"type": "document_query_assert", "file": "d.json", "pointer": "/a", "equals": 2},
    ], str(tmp_path))
    assert gate.verdict == V.BLOCK  # one pass + one fail -> block
    assert len(results) == 2


def test_no_verifiers_passes(tmp_path):
    gate, results = VF.run_verifiers([], str(tmp_path))
    assert gate.verdict == V.PASS and results == []


def test_required_empty_verifier_set_fails_closed(tmp_path):
    gate, results = VF.run_verifiers(
        [], str(tmp_path), require_declared=True
    )
    assert gate.verdict == V.ANALYSIS_ERROR
    assert results == []
    assert "empty" in gate.reasons[0]
