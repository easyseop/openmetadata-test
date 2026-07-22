"""T30 (commit-unit) + T31 (ID-unit) registration-completeness tests.

T30 runs against real temp git repos so commit boundaries, merges, empties and
trailers are exercised for real; upstream paths are genuine OM 1.12.13 paths.
"""
import subprocess
from pathlib import Path

import pytest

from acgh import gitprim as G
from acgh import invariants as I
from acgh import layout as L
from acgh import verdict as V

_LAYOUT = Path(__file__).resolve().parents[1] / "policies" / "repository-layout.yaml"
_UP = (
    "openmetadata-service/src/main/java/org/openmetadata/service/"
    "security/AuthLoginServlet.java"
)
_UP2 = (
    "openmetadata-service/src/main/java/org/openmetadata/service/"
    "security/AuthCallbackServlet.java"
)
_GOV = ".bank/policy/login.yaml"


def layout():
    return L.load_layout(_LAYOUT)


def _run(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True,
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


def _commit(repo, files: dict, message: str, allow_empty=False):
    for path, content in files.items():
        fp = repo / path
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content)
    _run(repo, "add", "-A")
    args = ["commit", "-m", message]
    if allow_empty:
        args.insert(1, "--allow-empty")
    _run(repo, *args)
    return G.git(str(repo), "rev-parse", "HEAD").strip()


def _base(repo):
    return _commit(repo, {"README": "base\n"}, "base")


def _check(repo, base):
    return I.check_commit_invariants(str(repo), base, "HEAD", layout())


def test_clean_core_commit_passes(repo):
    base = _base(repo)
    _commit(repo, {_UP: "x\n"}, "hook login\n\nCustomization-ID: BANK-OM-001")
    vs = _check(repo, base)
    assert vs == []
    assert I.violations_to_verdict(vs) == V.PASS


def test_core_change_without_id_blocks_P0_5(repo):
    base = _base(repo)
    _commit(repo, {_UP: "x\n"}, "sneaky core edit, no trailer")
    vs = _check(repo, base)
    assert [v.code for v in vs] == [I.CORE_CHANGE_WITHOUT_ID]
    assert I.violations_to_verdict(vs) == V.BLOCK


def test_multiple_ids_blocks(repo):
    base = _base(repo)
    _commit(repo, {_UP: "x\n"},
            "two ids\n\nCustomization-ID: BANK-OM-001\nCustomization-ID: BANK-OM-002")
    vs = _check(repo, base)
    assert I.MULTIPLE_IDS in [v.code for v in vs]


def test_empty_commit_blocks(repo):
    base = _base(repo)
    _commit(repo, {}, "empty\n\nCustomization-ID: BANK-OM-001", allow_empty=True)
    vs = _check(repo, base)
    assert [v.code for v in vs] == [I.EMPTY_COMMIT]


def test_core_governance_mixed_blocks(repo):
    base = _base(repo)
    _commit(repo, {_UP: "x\n", _GOV: "p\n"},
            "mixed\n\nCustomization-ID: BANK-OM-001")
    codes = [v.code for v in _check(repo, base)]
    assert I.CORE_GOVERNANCE_MIXED in codes


def test_governance_only_commit_needs_no_id(repo):
    base = _base(repo)
    _commit(repo, {_GOV: "p\n"}, "policy update\n\nChange-Type: governance")
    assert _check(repo, base) == []


def test_change_type_governance_touching_core_blocks(repo):
    base = _base(repo)
    _commit(repo, {_UP: "x\n"},
            "mislabeled\n\nChange-Type: governance\nCustomization-ID: BANK-OM-001")
    codes = [v.code for v in _check(repo, base)]
    assert I.GOVERNANCE_TOUCHES_CORE in codes


def test_unknown_path_is_analysis_error(repo):
    base = _base(repo)
    _commit(repo, {"brand-new-toplevel/x.txt": "z\n"}, "unclassified path")
    vs = _check(repo, base)
    assert I.UNKNOWN_PATH in [v.code for v in vs]
    assert I.violations_to_verdict(vs) == V.ANALYSIS_ERROR


def test_merge_commit_blocks(repo):
    base = _base(repo)
    _commit(repo, {_GOV: "a\n"}, "main work\n\nChange-Type: governance")
    _run(repo, "checkout", "-q", "-b", "feat")
    _commit(repo, {".bank/feat.yaml": "f\n"}, "feat\n\nChange-Type: governance")
    _run(repo, "checkout", "-q", "main")
    _commit(repo, {".bank/main2.yaml": "m\n"}, "main2\n\nChange-Type: governance")
    _run(repo, "merge", "--no-ff", "-m", "merge feat", "feat")
    codes = [v.code for v in _check(repo, base)]
    assert I.MERGE_COMMIT in codes


# --- T31 (synthetic commits + manifests) -----------------------------------
def _c(sha, *ids):
    return G.Commit(sha=sha, subject="s", customization_ids=list(ids))


def _manifest(cid, *, series_allowed=False, depends_on=None):
    m = {"customization_id": cid, "kind": "core-patch"}
    if series_allowed or depends_on:
        m["series"] = {"allowed": series_allowed, "depends_on": list(depends_on or [])}
    return m


def test_id_unregistered_blocks():
    commits = [_c("a" * 40, "BANK-OM-001")]
    vs = I.check_id_invariants(commits, manifests_by_id={})
    assert [v.code for v in vs] == [I.UNREGISTERED_ID]


def test_authorized_contiguous_series_ok():
    commits = [_c("a" * 40, "BANK-OM-001"), _c("b" * 40, "BANK-OM-001")]
    m = {"BANK-OM-001": _manifest("BANK-OM-001", series_allowed=True)}
    assert I.check_id_invariants(commits, m) == []


def test_unauthorized_series_blocks():
    commits = [_c("a" * 40, "BANK-OM-001"), _c("b" * 40, "BANK-OM-001")]
    m = {"BANK-OM-001": _manifest("BANK-OM-001", series_allowed=False)}
    assert I.UNAUTHORIZED_SERIES in [v.code for v in I.check_id_invariants(commits, m)]


def test_non_contiguous_series_blocks():
    # 001, 002, 001 -> 001 is interleaved by 002.
    commits = [_c("a" * 40, "BANK-OM-001"),
               _c("b" * 40, "BANK-OM-002"),
               _c("c" * 40, "BANK-OM-001")]
    m = {
        "BANK-OM-001": _manifest("BANK-OM-001", series_allowed=True),
        "BANK-OM-002": _manifest("BANK-OM-002"),
    }
    assert I.NON_CONTIGUOUS_SERIES in [v.code for v in I.check_id_invariants(commits, m)]


def test_retired_id_reuse_blocks():
    commits = [_c("a" * 40, "BANK-OM-009")]
    m = {"BANK-OM-009": _manifest("BANK-OM-009")}
    vs = I.check_id_invariants(commits, m, retired_ids={"BANK-OM-009"})
    assert I.RETIRED_ID_REUSED in [v.code for v in vs]


def test_dependency_cycle_blocks():
    commits = [_c("a" * 40, "BANK-OM-001"), _c("b" * 40, "BANK-OM-002")]
    m = {
        "BANK-OM-001": _manifest("BANK-OM-001", depends_on=["BANK-OM-002"]),
        "BANK-OM-002": _manifest("BANK-OM-002", depends_on=["BANK-OM-001"]),
    }
    vs = I.check_id_invariants(commits, m)
    assert [v.code for v in vs] == [I.DEPENDENCY_CYCLE]
