"""T27 vendor merge-conflict evidence tests."""
import copy
import subprocess

import pytest

from acgh import candidate as C
from acgh import conflicts as CF
from acgh import verdict as V

_ARTIFACT = "sha256:" + "a" * 64


def _run(repo, *args, check=True):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def _commit(repo, content, message):
    (repo / "conflict.txt").write_text(content)
    _run(repo, "add", "conflict.txt")
    _run(repo, "commit", "-m", message)
    return _run(repo, "rev-parse", "HEAD").stdout.strip()


def _resolved_merge(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(repo, "init", "-q", "-b", "upstream")
    _run(repo, "config", "user.email", "t@example.com")
    _run(repo, "config", "user.name", "t")
    _run(repo, "config", "commit.gpgsign", "false")
    base = _commit(repo, "base\n", "base")
    _run(repo, "switch", "-q", "-c", "vendor")
    _commit(repo, "vendor\n", "vendor edit")
    _run(repo, "switch", "-q", "upstream")
    target = _commit(repo, "upstream\n", "upstream edit")
    _run(repo, "switch", "-q", "vendor")
    merge = _run(repo, "merge", "--no-ff", "upstream", "-m", "merge", check=False)
    assert merge.returncode != 0
    captured = CF.capture_unmerged(str(repo))
    assert [item.path for item in captured] == ["conflict.txt"]
    (repo / "conflict.txt").write_text("manual combined\n")
    _run(repo, "add", "conflict.txt")
    _run(repo, "commit", "-m", "resolve merge")
    candidate = _run(repo, "rev-parse", "HEAD").stdout.strip()
    tree = _run(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
    lock = C.parse_candidate_lock(
        {
            "schema_version": 1,
            "integration_strategy": "vendor-merge",
            "upstream": {
                "repository": "open-metadata/OpenMetadata",
                "base_sha": base,
                "target_sha": target,
            },
            "candidate": {
                "repository": "bank/vendor",
                "commit_sha": candidate,
                "tree_sha": tree,
                "artifact_digest": _ARTIFACT,
            },
        }
    )
    return repo, base, lock, captured


def _decision(approvals=None):
    return {
        "resolution": "manual",
        "rationale": "preserve vendor behavior and upstream validation",
        "resolved_by": "integrator@example.com",
        "approval_ids": approvals or [],
    }


def test_capture_finalize_and_approved_gate(tmp_path):
    repo, base, lock, captured = _resolved_merge(tmp_path)
    evidence = CF.build_conflict_evidence(
        str(repo),
        lock,
        merge_base_sha=base,
        captured=captured,
        decisions={"conflict.txt": _decision(["APPROVAL-123"])},
    )
    result = CF.check_conflict_evidence(
        evidence, expected_candidate_lock_digest=lock.digest()
    )
    assert result.verdict == V.PASS
    assert evidence["conflicts"][0]["resolution_blob_sha"]


def test_unapproved_resolution_requires_approval(tmp_path):
    repo, base, lock, captured = _resolved_merge(tmp_path)
    evidence = CF.build_conflict_evidence(
        str(repo),
        lock,
        merge_base_sha=base,
        captured=captured,
        decisions={"conflict.txt": _decision()},
    )
    result = CF.check_conflict_evidence(
        evidence, expected_candidate_lock_digest=lock.digest()
    )
    assert result.verdict == V.APPROVAL
    assert "approval required" in result.reasons[0]


def test_missing_decision_is_rejected(tmp_path):
    repo, base, lock, captured = _resolved_merge(tmp_path)
    with pytest.raises(CF.ConflictEvidenceError, match="missing resolution"):
        CF.build_conflict_evidence(
            str(repo),
            lock,
            merge_base_sha=base,
            captured=captured,
            decisions={},
        )


def test_stale_evidence_is_analysis_error(tmp_path):
    repo, base, lock, captured = _resolved_merge(tmp_path)
    evidence = CF.build_conflict_evidence(
        str(repo),
        lock,
        merge_base_sha=base,
        captured=captured,
        decisions={"conflict.txt": _decision(["APPROVAL-123"])},
    )
    result = CF.check_conflict_evidence(
        evidence,
        expected_candidate_lock_digest="sha256:" + "0" * 64,
    )
    assert result.verdict == V.ANALYSIS_ERROR
    assert "stale" in result.reasons[0]


def test_tampered_count_blocks(tmp_path):
    repo, base, lock, captured = _resolved_merge(tmp_path)
    evidence = CF.build_conflict_evidence(
        str(repo),
        lock,
        merge_base_sha=base,
        captured=captured,
        decisions={"conflict.txt": _decision(["APPROVAL-123"])},
    )
    tampered = copy.deepcopy(evidence)
    tampered["captured_conflict_count"] = 2
    result = CF.check_conflict_evidence(
        tampered, expected_candidate_lock_digest=lock.digest()
    )
    assert result.verdict == V.BLOCK
    assert "count" in result.reasons[0]
