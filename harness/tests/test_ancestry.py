"""T25 vendor ancestry gate tests using real temporary Git histories."""
import copy
import subprocess

from acgh import ancestry as A
from acgh import candidate as C
from acgh import verdict as V

_ARTIFACT = "sha256:" + "a" * 64
_PATCH_LOCK = "sha256:" + "b" * 64


def _run(repo, *args, check=True):
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def _commit(repo, filename, content, message):
    (repo / filename).write_text(content)
    _run(repo, "add", filename)
    _run(repo, "commit", "-m", message)
    return _run(repo, "rev-parse", "HEAD")


def _topology(tmp_path):
    """Create diverged upstream/vendor histories joined by a real merge."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(repo, "init", "-q", "-b", "upstream")
    _run(repo, "config", "user.email", "t@example.com")
    _run(repo, "config", "user.name", "t")
    _run(repo, "config", "commit.gpgsign", "false")

    base = _commit(repo, "base.txt", "base\n", "base")
    _run(repo, "branch", "vendor")
    target = _commit(repo, "upstream.txt", "target\n", "upstream target")

    _run(repo, "switch", "-q", "vendor")
    vendor_before_merge = _commit(repo, "bank.txt", "custom\n", "bank custom")
    _run(repo, "merge", "--no-ff", "upstream", "-m", "merge upstream target")
    candidate = _run(repo, "rev-parse", "HEAD")
    tree = _run(repo, "rev-parse", "HEAD^{tree}")
    return repo, base, target, vendor_before_merge, candidate, tree


def _lock(base, target, candidate, tree, *, strategy=C.VENDOR_MERGE):
    data = {
        "schema_version": 1,
        "integration_strategy": strategy,
        "upstream": {
            "repository": "open-metadata/OpenMetadata",
            "base_sha": base,
            "target_sha": target,
        },
        "candidate": {
            "repository": "bank/kb_openmetadata",
            "commit_sha": candidate,
            "tree_sha": tree,
            "artifact_digest": _ARTIFACT,
        },
    }
    if strategy == C.PATCH_REPLAY:
        data["patch_source_lock_digest"] = _PATCH_LOCK
    return C.parse_candidate_lock(data)


def test_valid_vendor_merge_passes_with_audit_evidence(tmp_path):
    repo, base, target, _, candidate, tree = _topology(tmp_path)
    lock = _lock(base, target, candidate, tree)
    result = A.check_vendor_ancestry(str(repo), lock)
    assert result.verdict == V.PASS
    assert any(f"approved_target={target}" == reason for reason in result.reasons)
    assert any(reason.startswith("candidate_lock_digest=sha256:")
               for reason in result.reasons)


def test_candidate_before_merge_blocks_missing_target(tmp_path):
    repo, base, target, vendor_before, _, _ = _topology(tmp_path)
    tree = _run(repo, "rev-parse", f"{vendor_before}^{{tree}}")
    lock = _lock(base, target, vendor_before, tree)
    result = A.check_vendor_ancestry(str(repo), lock)
    assert result.verdict == V.BLOCK
    assert any(
        "does not contain approved upstream target" in reason
        for reason in result.reasons
    )


def test_target_only_candidate_blocks_missing_vendor_base_lineage(tmp_path):
    repo, base, _, _, _, _ = _topology(tmp_path)
    _run(repo, "switch", "-q", "--orphan", "unrelated")
    unrelated_target = _commit(repo, "other.txt", "other\n", "unrelated target")
    tree = _run(repo, "rev-parse", "HEAD^{tree}")
    lock = _lock(base, unrelated_target, unrelated_target, tree)
    result = A.check_vendor_ancestry(str(repo), lock)
    assert result.verdict == V.BLOCK
    assert any(
        "upstream base and target have no common ancestor" in reason
        for reason in result.reasons
    )
    assert any(
        "candidate does not contain locked upstream base" in reason
        for reason in result.reasons
    )


def test_missing_locked_object_is_analysis_error(tmp_path):
    repo, base, _, _, candidate, tree = _topology(tmp_path)
    lock = _lock(base, "0" * 40, candidate, tree)
    result = A.check_vendor_ancestry(str(repo), lock)
    assert result.verdict == V.ANALYSIS_ERROR
    assert "required commit object missing" in result.reasons[0]


def test_stale_candidate_tree_is_analysis_error(tmp_path):
    repo, base, target, _, candidate, tree = _topology(tmp_path)
    lock = _lock(base, target, candidate, tree)
    data = copy.deepcopy(lock.canonical())
    data["candidate"]["tree_sha"] = "0" * 40
    result = A.check_vendor_ancestry(
        str(repo), C.parse_candidate_lock(data)
    )
    assert result.verdict == V.ANALYSIS_ERROR
    assert "tree mismatch" in result.reasons[0]


def test_patch_replay_is_fail_closed_when_misrouted(tmp_path):
    repo, base, target, _, candidate, tree = _topology(tmp_path)
    lock = _lock(
        base, target, candidate, tree, strategy=C.PATCH_REPLAY
    )
    result = A.check_vendor_ancestry(str(repo), lock)
    assert result.verdict == V.ANALYSIS_ERROR
    assert "requires integration_strategy=vendor-merge" in result.reasons[0]
