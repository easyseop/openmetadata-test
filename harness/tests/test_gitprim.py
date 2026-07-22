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
