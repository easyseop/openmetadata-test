"""T26 vendor-merge customization survival tests."""
import copy
import subprocess

from acgh import candidate as C
from acgh import contracts
from acgh import survival as S
from acgh import verdict as V

_ARTIFACT = "sha256:" + "a" * 64


def _run(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _commit(repo, path, content, message):
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    _run(repo, "add", path)
    _run(repo, "commit", "-m", message)
    return _run(repo, "rev-parse", "HEAD")


def _topology(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(repo, "init", "-q", "-b", "upstream")
    _run(repo, "config", "user.email", "t@example.com")
    _run(repo, "config", "user.name", "t")
    _run(repo, "config", "commit.gpgsign", "false")

    base = _commit(repo, "openmetadata-service/base.txt", "base\n", "base")
    target = _commit(repo, "openmetadata-service/upstream.txt", "new\n", "target")
    _run(repo, "switch", "-q", "-c", "vendor", base)
    _commit(
        repo,
        "openmetadata-service/bank/feature.txt",
        "bank feature\n",
        "bank customization",
    )
    _run(repo, "merge", "--no-ff", "upstream", "-m", "merge target")
    candidate = _run(repo, "rev-parse", "HEAD")
    tree = _run(repo, "rev-parse", "HEAD^{tree}")
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
    return repo, lock


def _manifest():
    return {
        "customization_id": "BANK-OM-001",
        "kind": "core-patch",
        "implementation": {
            "allowed_changed_paths": ["openmetadata-service/bank/**"],
            "required_changed_paths": [
                "openmetadata-service/bank/feature.txt"
            ],
        },
        "assurance": {"contracts": ["CONTRACT-FEATURE"], "direct_tests": []},
    }


def _catalog():
    return contracts.parse_catalog(
        {
            "schema_version": 1,
            "contracts": [
                {
                    "id": "CONTRACT-FEATURE",
                    "title": "feature remains available",
                    "required_tests": ["tests/bank/test_feature.py::test_contract"],
                    "customization_ids": ["BANK-OM-001"],
                }
            ],
        }
    )


def test_required_path_and_contract_survive(tmp_path):
    repo, lock = _topology(tmp_path)
    result = S.check_customization_survival(
        str(repo), lock, {"BANK-OM-001": _manifest()}, _catalog()
    )
    assert result.verdict == V.PASS
    assert "required_paths=1" in result.reasons[0]


def test_required_path_missing_blocks(tmp_path):
    repo, lock = _topology(tmp_path)
    manifest = _manifest()
    manifest["implementation"]["required_changed_paths"] = [
        "openmetadata-service/bank/missing.txt"
    ]
    result = S.check_customization_survival(
        str(repo), lock, {"BANK-OM-001": manifest}, _catalog()
    )
    assert result.verdict == V.BLOCK
    assert any("required_path_missing" in reason for reason in result.reasons)


def test_required_path_identical_to_upstream_blocks(tmp_path):
    repo, lock = _topology(tmp_path)
    manifest = _manifest()
    manifest["implementation"]["required_changed_paths"] = [
        "openmetadata-service/upstream.txt"
    ]
    result = S.check_customization_survival(
        str(repo), lock, {"BANK-OM-001": manifest}, _catalog()
    )
    assert result.verdict == V.BLOCK
    assert any(
        "required_state_not_distinct" in reason for reason in result.reasons
    )


def test_missing_reverse_contract_binding_blocks(tmp_path):
    repo, lock = _topology(tmp_path)
    catalog = contracts.parse_catalog(
        {
            "schema_version": 1,
            "contracts": [
                {
                    "id": "CONTRACT-FEATURE",
                    "title": "feature remains available",
                    "required_tests": ["tests/bank/test_feature.py::test_contract"],
                    "customization_ids": [],
                }
            ],
        }
    )
    result = S.check_customization_survival(
        str(repo), lock, {"BANK-OM-001": _manifest()}, catalog
    )
    assert result.verdict == V.BLOCK
    assert any(
        "contract_reverse_binding_missing" in reason
        for reason in result.reasons
    )


def test_active_id_without_manifest_blocks(tmp_path):
    repo, lock = _topology(tmp_path)
    result = S.check_customization_survival(
        str(repo),
        lock,
        {"BANK-OM-001": _manifest()},
        _catalog(),
        active_ids=["BANK-OM-001", "BANK-OM-002"],
    )
    assert result.verdict == V.BLOCK
    assert any("BANK-OM-002 manifest_missing" in r for r in result.reasons)


def test_stale_lock_is_analysis_error(tmp_path):
    repo, lock = _topology(tmp_path)
    data = copy.deepcopy(lock.canonical())
    data["candidate"]["tree_sha"] = "0" * 40
    result = S.check_customization_survival(
        str(repo),
        C.parse_candidate_lock(data),
        {"BANK-OM-001": _manifest()},
        _catalog(),
    )
    assert result.verdict == V.ANALYSIS_ERROR
    assert "tree mismatch" in result.reasons[0]


def test_patch_replay_is_not_routed_to_survival(tmp_path):
    repo, lock = _topology(tmp_path)
    data = copy.deepcopy(lock.canonical())
    data["integration_strategy"] = C.PATCH_REPLAY
    data["patch_source_lock_digest"] = "sha256:" + "b" * 64
    result = S.check_customization_survival(
        str(repo),
        C.parse_candidate_lock(data),
        {"BANK-OM-001": _manifest()},
        _catalog(),
    )
    assert result.verdict == V.ANALYSIS_ERROR
    assert "requires integration_strategy=vendor-merge" in result.reasons[0]
