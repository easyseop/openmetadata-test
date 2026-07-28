"""T40 drift tests, on real OM upstream paths."""
import subprocess
from pathlib import Path

import pytest

from acgh import drift as D
from acgh import gitprim as G
from acgh import layout as L
from acgh import verdict as V

_LAYOUT = Path(__file__).resolve().parents[1] / "policies" / "repository-layout.yaml"
_SECDIR = "openmetadata-service/src/main/java/org/openmetadata/service/security"
_AUTH = f"{_SECDIR}/AuthLoginServlet.java"
_AUTH2 = f"{_SECDIR}/AuthCallbackServlet.java"
_SPEC = "openmetadata-spec/src/main/resources/json/schema/auth/ssoAuth.json"


def layout():
    return L.load_layout(_LAYOUT)


def _run(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True)


@pytest.fixture()
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    _run(r, "init", "-q", "-b", "main")
    _run(r, "config", "user.email", "t@example.com")
    _run(r, "config", "user.name", "t")
    _run(r, "config", "commit.gpgsign", "false")
    return r


def _write(repo, path, content):
    fp = repo / path
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(content)


def _commit(repo, msg):
    _run(repo, "add", "-A")
    _run(repo, "commit", "-m", msg)
    return G.git(str(repo), "rev-parse", "HEAD").strip()


def _base(repo):
    _write(repo, _AUTH, "line1\nline2\n")
    _write(repo, _AUTH2, "cb1\ncb2\n")
    _write(repo, _SPEC, "{}\n")
    return _commit(repo, "upstream base")


def _manifest(allowed, required, series_allowed=False):
    m = {"customization_id": "BANK-OM-001", "kind": "core-patch",
         "implementation": {"allowed_changed_paths": allowed,
                            "required_changed_paths": required}}
    if series_allowed:
        m["series"] = {"allowed": True}
    return {"BANK-OM-001": m}


def test_in_scope_change_passes(repo):
    base = _base(repo)
    _write(repo, _AUTH, "line1\nBANK\nline2\n")
    _commit(repo, "hook\n\nCustomization-ID: BANK-OM-001")
    vs = D.check_drift(str(repo), base, "HEAD",
                       _manifest([f"{_SECDIR}/**"], [_AUTH]), layout())
    assert vs == []
    assert D.to_gate_result(vs).verdict == V.PASS


def test_out_of_scope_upstream_change_blocks(repo):
    base = _base(repo)
    # allowed only covers the security dir, but the commit also edits a spec file.
    _write(repo, _AUTH, "line1\nBANK\nline2\n")
    _write(repo, _SPEC, '{"changed": true}\n')
    _commit(repo, "hook + spec\n\nCustomization-ID: BANK-OM-001")
    vs = D.check_drift(str(repo), base, "HEAD",
                       _manifest([f"{_SECDIR}/**"], [_AUTH]), layout())
    codes = [v.code for v in vs]
    assert D.OUT_OF_SCOPE in codes
    assert any(_SPEC in v.detail for v in vs)
    assert D.to_gate_result(vs).verdict == V.BLOCK


def test_out_of_scope_governance_change_is_not_skipped(repo):
    base = _base(repo)
    governance = ".bank/policies/relaxed.yaml"
    _write(repo, _AUTH, "line1\nBANK\nline2\n")
    _write(repo, governance, "allow_everything: true\n")
    _commit(repo, "hook + hidden policy\n\nCustomization-ID: BANK-OM-001")
    vs = D.check_drift(
        str(repo),
        base,
        "HEAD",
        _manifest([_AUTH], [_AUTH]),
        layout(),
    )
    assert D.OUT_OF_SCOPE in [v.code for v in vs]
    assert any(governance in v.detail for v in vs)


def test_required_not_in_net_blocks(repo):
    base = _base(repo)
    _write(repo, _AUTH, "line1\nBANK\nline2\n")
    _commit(repo, "hook\n\nCustomization-ID: BANK-OM-001")
    # required lists AUTH2 too, but the candidate never changes it.
    vs = D.check_drift(str(repo), base, "HEAD",
                       _manifest([f"{_SECDIR}/**"], [_AUTH, _AUTH2]), layout())
    assert D.REQUIRED_NET_MISSING in [v.code for v in vs]
    assert any(_AUTH2 in v.detail for v in vs)


def test_net_zero_effect_blocks_even_though_touched(repo):
    # Edit then revert across two commits -> touched but net-zero -> lower bound fires.
    base = _base(repo)
    _write(repo, _AUTH, "line1\nBANK\nline2\n")
    _commit(repo, "add hook\n\nCustomization-ID: BANK-OM-001")
    _write(repo, _AUTH, "line1\nline2\n")  # revert to base content
    _commit(repo, "revert hook\n\nCustomization-ID: BANK-OM-001")
    vs = D.check_drift(str(repo), base, "HEAD",
                       _manifest([f"{_SECDIR}/**"], [_AUTH], series_allowed=True),
                       layout())
    # No out-of-scope (both touches in scope), but required nets to nothing.
    assert [v.code for v in vs] == [D.REQUIRED_NET_MISSING]
