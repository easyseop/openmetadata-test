import subprocess

from acgh import watch_suggest as WS


def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def _commit(repo, message, trailer=None):
    _git(repo, "add", ".")
    args = ["commit", "-m", message]
    if trailer:
        args += ["-m", trailer]
    _git(repo, *args)
    return _git(repo, "rev-parse", "HEAD")


def test_changed_direct_dependency_is_suggested_but_not_auto_registered(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "t")
    _git(tmp_path, "config", "user.email", "t@example.com")
    (tmp_path / "CoreRegistry.java").write_text(
        "public class CoreRegistry { void connect() {} }\n"
    )
    (tmp_path / "CustomResource.java").write_text(
        "class CustomResource { CoreRegistry registry; }\n"
    )
    base = _commit(tmp_path, "base")
    (tmp_path / "CoreRegistry.java").write_text(
        "public class CoreRegistry { void connectNew() {} }\n"
    )
    target = _commit(tmp_path, "upstream target")
    candidate = target
    manifests = {
        "BANK-OM-001": {
            "implementation": {
                "allowed_changed_paths": ["CustomResource.java"],
            },
            "upgrade_watch": {"paths": []},
        }
    }

    suggestions = WS.suggest_watch_paths(
        str(tmp_path), base, target, candidate, manifests
    )
    assert len(suggestions) == 1
    assert suggestions[0].suggested_path == "CoreRegistry.java"
    assert suggestions[0].referenced_from == ("CustomResource.java",)
    packet = WS.review_packet(suggestions)
    assert packet["authority"] == "code-owner-review-required"


def test_existing_watch_and_unreferenced_change_are_not_suggested(tmp_path):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "t")
    _git(tmp_path, "config", "user.email", "t@example.com")
    (tmp_path / "CoreRegistry.java").write_text("class CoreRegistry {}\n")
    (tmp_path / "OtherService.java").write_text("class OtherService {}\n")
    (tmp_path / "CustomResource.java").write_text(
        "class CustomResource { CoreRegistry registry; }\n"
    )
    base = _commit(tmp_path, "base")
    (tmp_path / "CoreRegistry.java").write_text("class CoreRegistry { int v; }\n")
    (tmp_path / "OtherService.java").write_text("class OtherService { int v; }\n")
    target = _commit(tmp_path, "target")
    manifests = {
        "BANK-OM-001": {
            "implementation": {
                "allowed_changed_paths": ["CustomResource.java"],
            },
            "upgrade_watch": {"paths": ["CoreRegistry.java"]},
        }
    }
    assert WS.suggest_watch_paths(
        str(tmp_path), base, target, target, manifests
    ) == []
