"""T61 patch-kill tests on a real OM auth file (base = without the bank patch)."""
import subprocess
import sys

import pytest

from acgh import gitprim as G
from acgh import patchkill as PK
from acgh import verdict as V


def _run(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True)


@pytest.fixture()
def repo(tmp_path, om_auth_content, om_auth_path):
    r = tmp_path / "repo"
    r.mkdir()
    _run(r, "init", "-q", "-b", "main")
    _run(r, "config", "user.email", "t@example.com")
    _run(r, "config", "user.name", "t")
    _run(r, "config", "commit.gpgsign", "false")
    # base = real OM auth file WITHOUT the bank marker (i.e. patch removed).
    fp = r / om_auth_path
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(om_auth_content)
    _run(r, "add", "-A")
    _run(r, "commit", "-m", "base without patch")
    return r


def _marker_test(auth_path):
    # exits 0 iff the bank marker is present -> without the patch it exits 1.
    return [sys.executable, "-c",
            f"import sys,pathlib;"
            f"sys.exit(0 if 'BANK-OM-001' in pathlib.Path({auth_path!r}).read_text() "
            f"else 1)"]


def test_proven_when_test_fails_without_patch(repo, tmp_path, om_auth_path):
    r = PK.patch_kill(str(repo), "main", _marker_test(om_auth_path),
                      str(tmp_path / "wt"))
    assert r.status == PK.PROVEN
    assert r.verdict() == V.PASS


def test_shell_test_blocks(repo, tmp_path):
    # A test that always passes proves nothing about the patch.
    always_ok = [sys.executable, "-c", "import sys; sys.exit(0)"]
    r = PK.patch_kill(str(repo), "main", always_ok, str(tmp_path / "wt"))
    assert r.status == PK.SHELL
    assert r.verdict() == V.BLOCK


def test_unrunnable_test_is_inconclusive(repo, tmp_path):
    r = PK.patch_kill(str(repo), "main", ["__no_such_binary_xyz__"],
                      str(tmp_path / "wt"))
    assert r.status == PK.INCONCLUSIVE
    assert r.verdict() == V.ANALYSIS_ERROR


def test_worktree_cleaned_after_run(repo, tmp_path):
    wt = tmp_path / "wt"
    PK.patch_kill(str(repo), "main", [sys.executable, "-c", "0"], str(wt))
    listing = G.git(str(repo), "worktree", "list", "--porcelain")
    assert str(wt) not in listing
    assert not wt.exists()
