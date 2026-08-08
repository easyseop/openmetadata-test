"""T12 git primitive tests against real temp git repos.

The key acceptance (P0-5 root cause): an ID-less commit sitting between ID'd
commits must be returned as its own record with empty ids — not collapsed.
"""
import subprocess

import pytest

from acgh import gitprim as G


def _run(repo, *args):
    subprocess.run(["git", "-C", repo, *args], check=True,
                   capture_output=True, text=True)


def _commit(repo, path, content, message):
    (repo / path).parent.mkdir(parents=True, exist_ok=True)
    (repo / path).write_text(content)
    _run(str(repo), "add", "-A")
    _run(str(repo), "commit", "-m", message)
    return G.git(str(repo), "rev-parse", "HEAD").strip()


@pytest.fixture()
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    _run(str(r), "init", "-q")
    _run(str(r), "config", "user.email", "t@example.com")
    _run(str(r), "config", "user.name", "t")
    _run(str(r), "config", "commit.gpgsign", "false")
    return r


def test_commits_extract_ids_and_preserve_idless_commit(repo):
    base = _commit(repo, "README", "base\n", "base")
    _commit(repo, "a.java", "a\n",
            "add A\n\nCustomization-ID: BANK-OM-001")
    # ID-less commit deliberately sits BETWEEN two ID'd commits.
    idless = _commit(repo, "sneaky.java", "x\n", "no id here")
    _commit(repo, "b.java", "b\n",
            "add B\n\nCustomization-ID: BANK-OM-002")

    cs = G.commits(str(repo), base, "HEAD")
    assert [c.customization_ids for c in cs] == [
        ["BANK-OM-001"], [], ["BANK-OM-002"]
    ]
    # The ID-less commit is a distinct record (not collapsed away).
    assert any(c.sha == idless and c.customization_ids == [] for c in cs)


def test_multiple_ids_in_one_commit(repo):
    base = _commit(repo, "README", "base\n", "base")
    _commit(repo, "c.java", "c\n",
            "mix\n\nCustomization-ID: BANK-OM-001\nCustomization-ID: BANK-OM-002")
    cs = G.commits(str(repo), base, "HEAD")
    assert cs[-1].customization_ids == ["BANK-OM-001", "BANK-OM-002"]


def test_changed_paths(repo):
    base = _commit(repo, "README", "base\n", "base")
    sha = _commit(repo, "openmetadata-service/x/Auth.java", "z\n", "touch auth")
    assert G.changed_paths(str(repo), sha) == [
        "openmetadata-service/x/Auth.java"
    ]


def test_object_exists(repo):
    base = _commit(repo, "README", "base\n", "base")
    assert G.object_exists(str(repo), base) is True
    assert G.object_exists(str(repo), "0" * 40) is False


def test_change_type_trailer_and_non_merge(repo):
    base = _commit(repo, "README", "base\n", "base")
    _commit(repo, ".bank/p.yaml", "p\n", "policy\n\nChange-Type: governance")
    c = G.commits(str(repo), base, "HEAD")[-1]
    assert c.change_type == "governance"
    assert c.is_merge is False
    assert len(c.parents) == 1


def test_merge_commit_has_two_parents(repo):
    base = _commit(repo, "README", "base\n", "base")
    _commit(repo, "main.txt", "m\n", "main work")
    _run(str(repo), "checkout", "-q", "-b", "feat")
    _commit(repo, "feat.txt", "f\n", "feat work")
    _run(str(repo), "checkout", "-q", "-")
    _commit(repo, "main2.txt", "m2\n", "more main")
    _run(str(repo), "merge", "--no-ff", "-m", "merge feat", "feat")
    merge = G.commits(str(repo), base, "HEAD")[-1]
    assert merge.is_merge is True
    assert len(merge.parents) == 2


def test_ref_worktree_and_tree_primitives(repo):
    base = _commit(repo, "README", "base\n", "base")
    assert G.resolve_commit(str(repo), "HEAD") == base
    assert G.worktree_is_dirty(str(repo)) is False

    (repo / "untracked.txt").write_text("local\n")
    assert G.worktree_is_dirty(str(repo)) is True
    (repo / "untracked.txt").unlink()

    entries = G.tree_entries(str(repo), "HEAD")
    assert entries["README"].mode == "100644"
    assert entries["README"].object_type == "blob"
    assert G.blob_bytes(str(repo), "HEAD", "README") == b"base\n"


def test_invalid_ref_becomes_structured_git_error(repo):
    _commit(repo, "README", "base\n", "base")
    with pytest.raises(G.GitPrimitiveError, match="failed"):
        G.resolve_commit(str(repo), "--definitely-not-a-ref")


def test_merge_tree_reports_add_add_conflict(repo):
    base = _commit(repo, "README", "base\n", "base")
    _run(str(repo), "switch", "-qc", "target", base)
    target = _commit(repo, "shared.json", '{"side":"target"}\n', "target add")
    _run(str(repo), "switch", "-qc", "custom", base)
    custom = _commit(repo, "shared.json", '{"side":"custom"}\n', "custom add")

    replay = G.merge_tree_conflicts(str(repo), target, custom)

    assert replay.conflicted_paths == ("shared.json",)
    assert replay.tree_sha
    assert replay.output_digest.startswith("sha256:")


def test_merge_tree_reports_rename_rename_conflict(repo):
    base = _commit(repo, "old.txt", "base\n", "base")
    _run(str(repo), "switch", "-qc", "target", base)
    (repo / "old.txt").rename(repo / "target.txt")
    _run(str(repo), "add", "-A")
    _run(str(repo), "commit", "-m", "target rename")
    target = G.resolve_commit(str(repo), "HEAD")
    _run(str(repo), "switch", "-qc", "custom", base)
    (repo / "old.txt").rename(repo / "custom.txt")
    _run(str(repo), "add", "-A")
    _run(str(repo), "commit", "-m", "custom rename")
    custom = G.resolve_commit(str(repo), "HEAD")

    replay = G.merge_tree_conflicts(str(repo), target, custom)

    assert set(replay.conflicted_paths) == {"old.txt", "custom.txt", "target.txt"}


def test_merge_tree_rejects_unapproved_repository_merge_driver_configuration(repo):
    _run(str(repo), "config", "merge.keep-current.driver", "true")
    _commit(repo, ".gitattributes", "*.json merge=keep-current\n", "attributes")
    base = _commit(repo, "config.json", '{"value":"base"}\n', "base")
    _run(str(repo), "switch", "-qc", "target", base)
    target = _commit(repo, "config.json", '{"value":"target"}\n', "target edit")
    _run(str(repo), "switch", "-qc", "custom", base)
    custom = _commit(repo, "config.json", '{"value":"custom"}\n', "custom edit")

    with pytest.raises(G.GitPrimitiveError, match="not allowed"):
        G.merge_tree_conflicts(str(repo), target, custom)


def test_rename_policy_is_stable_across_user_configuration(repo):
    base = _commit(repo, "old.txt", "same content\n", "base")
    _run(str(repo), "switch", "-qc", "renamed", base)
    (repo / "old.txt").rename(repo / "new.txt")
    _run(str(repo), "add", "-A")
    _run(str(repo), "commit", "-m", "rename")
    renamed = G.resolve_commit(str(repo), "HEAD")

    _run(str(repo), "config", "diff.renames", "true")
    _run(str(repo), "config", "merge.renames", "true")
    first_paths = G.net_changed_paths(str(repo), base, renamed)
    first_replay = G.merge_tree_conflicts(str(repo), base, renamed)

    _run(str(repo), "config", "diff.renames", "false")
    _run(str(repo), "config", "merge.renames", "false")
    second_paths = G.net_changed_paths(str(repo), base, renamed)
    second_replay = G.merge_tree_conflicts(str(repo), base, renamed)

    assert first_paths == second_paths == ["new.txt", "old.txt"]
    assert first_replay.output_digest == second_replay.output_digest
    assert first_replay.rename_detection_policy == "disabled"
