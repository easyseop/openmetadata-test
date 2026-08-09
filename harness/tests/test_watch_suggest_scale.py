"""watch-suggest at real-repository scale, and the findings it must not lose.

The advisory gate timed out on the real 1.13.1->1.13.2 range and produced no
candidates at all, so these tests pin both halves of the fix: it has to finish on
a thousand-path range, and it still has to report the deletion of a watched file
even when no replacement can be guessed.
"""
from __future__ import annotations

import json
import subprocess
import time
from types import SimpleNamespace

import pytest

from acgh import gitprim
from acgh import watch_suggest as WS


def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
    ).stdout.strip()


def _repo(tmp_path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "t")
    _git(tmp_path, "config", "user.email", "t@example.com")
    return tmp_path


def _commit(repo, message):
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", message)
    return _git(repo, "rev-parse", "HEAD")


def _manifest(declared, watch=()):
    return {
        "implementation": {"allowed_changed_paths": list(declared)},
        "upgrade_watch": {"paths": list(watch)},
    }


# ---- scale -----------------------------------------------------------------
def test_completes_on_a_thousand_path_upstream_range(tmp_path):
    """1,700 changed paths x 7 manifests must finish well inside the deadline."""
    repo = _repo(tmp_path)
    upstream = repo / "upstream"
    upstream.mkdir()
    for index in range(1700):
        (upstream / f"CoreService{index:04d}.java").write_text(
            f"class CoreService{index:04d} {{ int v; }}\n", encoding="utf-8"
        )
    custom_dir = repo / "custom"
    custom_dir.mkdir()
    # a shared 5MB i18n bundle: the file that made the old scan quadratic
    (custom_dir / "ko-kr.json").write_text(
        json.dumps({f"key{i}": f"CoreService{i % 1700:04d} 설명 문구" for i in range(60000)}),
        encoding="utf-8",
    )
    for index in range(112):
        (custom_dir / f"Custom{index:03d}.java").write_text(
            f"class Custom{index:03d} {{ CoreService{index:04d} dep; }}\n", encoding="utf-8"
        )
    base = _commit(repo, "base")

    for index in range(1700):
        (upstream / f"CoreService{index:04d}.java").write_text(
            f"class CoreService{index:04d} {{ int v; int w; }}\n", encoding="utf-8"
        )
    target = _commit(repo, "upstream target")

    manifests = {
        f"BANK-OM-{group:03d}": _manifest(
            ["custom/ko-kr.json"]
            + [f"custom/Custom{index:03d}.java" for index in range(group * 16, group * 16 + 16)]
        )
        for group in range(7)
    }

    started = time.monotonic()
    report = WS.analyze(str(repo), base, target, target, manifests, timeout_seconds=120)
    elapsed = time.monotonic() - started

    assert report.complete is True
    assert elapsed < 60, f"watch-suggest took {elapsed:.1f}s on a 1,700-path range"
    assert report.counts["changed_paths"] == 1700
    assert report.counts["indexed_customization_files"] == 112
    # the shared translation bundle is data, not a reference source
    assert report.excluded["customization_structured"] == 1
    assert report.counts["suggestions"] == 112


def test_blob_batch_reads_many_paths_in_one_process(tmp_path):
    repo = _repo(tmp_path)
    for name in ["a b.txt", "유니코드.txt", "plain.txt"]:
        (repo / name).write_text(f"content of {name}\n", encoding="utf-8")
    head = _commit(repo, "base")
    blobs = gitprim.blob_batch(str(repo), head, ["a b.txt", "유니코드.txt", "missing.txt"])
    assert blobs["a b.txt"] == b"content of a b.txt\n"
    assert blobs["유니코드.txt"].decode("utf-8") == "content of 유니코드.txt\n"
    assert "missing.txt" not in blobs


# ---- precision -------------------------------------------------------------
def test_a_basename_only_in_a_comment_is_not_a_reference(tmp_path):
    repo = _repo(tmp_path)
    (repo / "CoreRegistry.java").write_text("class CoreRegistry {}\n", encoding="utf-8")
    (repo / "CommentOnly.java").write_text(
        "// TODO: someday align with CoreRegistry\n"
        "/* CoreRegistry was considered here */\n"
        "class CommentOnly { int v; }\n",
        encoding="utf-8",
    )
    base = _commit(repo, "base")
    (repo / "CoreRegistry.java").write_text("class CoreRegistry { int v; }\n", encoding="utf-8")
    target = _commit(repo, "target")
    manifests = {"BANK-OM-001": _manifest(["CommentOnly.java"])}
    assert WS.analyze(str(repo), base, target, target, manifests).suggestions == ()


def test_an_import_string_still_counts_as_a_reference(tmp_path):
    repo = _repo(tmp_path)
    (repo / "EntityUtils.ts").write_text("export const a = 1;\n", encoding="utf-8")
    (repo / "CustomPanel.tsx").write_text(
        "// see https://example.com/docs\n"
        "import { a } from './EntityUtils';\n"
        "export const Panel = () => a;\n",
        encoding="utf-8",
    )
    base = _commit(repo, "base")
    (repo / "EntityUtils.ts").write_text("export const a = 2;\n", encoding="utf-8")
    target = _commit(repo, "target")
    manifests = {"BANK-OM-001": _manifest(["CustomPanel.tsx"])}
    report = WS.analyze(str(repo), base, target, target, manifests)
    assert [item.suggested_path for item in report.suggestions] == ["EntityUtils.ts"]
    assert report.suggestions[0].referenced_from == ("CustomPanel.tsx",)


def test_a_translation_bundle_is_not_a_reference_but_stays_watched(tmp_path):
    repo = _repo(tmp_path)
    (repo / "EntityUtils.ts").write_text("export const a = 1;\n", encoding="utf-8")
    (repo / "ko-kr.json").write_text(
        json.dumps({"label": "EntityUtils 화면 설명"}), encoding="utf-8"
    )
    base = _commit(repo, "base")
    (repo / "EntityUtils.ts").write_text("export const a = 2;\n", encoding="utf-8")
    target = _commit(repo, "target")
    manifests = {"BANK-OM-001": _manifest(["ko-kr.json"], watch=["ko-kr.json"])}
    report = WS.analyze(str(repo), base, target, target, manifests)
    assert report.suggestions == ()
    assert report.excluded["customization_structured"] == 1
    # the watch itself is untouched: upgrade-watch still owns that file
    assert manifests["BANK-OM-001"]["upgrade_watch"]["paths"] == ["ko-kr.json"]


def test_two_customizations_sharing_a_file_each_keep_their_evidence(tmp_path):
    repo = _repo(tmp_path)
    (repo / "CoreRegistry.java").write_text("class CoreRegistry {}\n", encoding="utf-8")
    (repo / "Shared.java").write_text(
        "class Shared { CoreRegistry r; }\n", encoding="utf-8"
    )
    base = _commit(repo, "base")
    (repo / "CoreRegistry.java").write_text("class CoreRegistry { int v; }\n", encoding="utf-8")
    target = _commit(repo, "target")
    manifests = {
        "BANK-OM-001": _manifest(["Shared.java"]),
        "BANK-OM-002": _manifest(["Shared.java"]),
    }
    report = WS.analyze(str(repo), base, target, target, manifests)
    assert sorted(item.customization_id for item in report.suggestions) == [
        "BANK-OM-001", "BANK-OM-002",
    ]
    assert all(item.referenced_from == ("Shared.java",) for item in report.suggestions)


def test_a_stem_reused_across_directories_is_not_evidence(tmp_path):
    """`metadata.py` exists under many sources; the token names none of them."""
    repo = _repo(tmp_path)
    for source in ["mssql", "mysql", "postgres"]:
        directory = repo / "ingestion" / source
        directory.mkdir(parents=True)
        (directory / "metadata.py").write_text(f"# {source}\nvalue = 1\n", encoding="utf-8")
    (repo / "Custom.java").write_text(
        "class Custom { String note = \"metadata handling\"; }\n", encoding="utf-8"
    )
    base = _commit(repo, "base")
    for source in ["mssql", "mysql", "postgres"]:
        (repo / "ingestion" / source / "metadata.py").write_text(
            f"# {source}\nvalue = 2\n", encoding="utf-8"
        )
    target = _commit(repo, "target")
    manifests = {"BANK-OM-001": _manifest(["Custom.java"])}
    report = WS.analyze(str(repo), base, target, target, manifests)
    assert report.suggestions == ()
    assert report.excluded["changed_ambiguous_symbol"] == 3


def test_a_file_beside_its_own_test_stays_usable_evidence(tmp_path):
    repo = _repo(tmp_path)
    utils = repo / "src"
    utils.mkdir()
    (utils / "EntityUtils.ts").write_text("export const a = 1;\n", encoding="utf-8")
    (utils / "EntityUtils.test.ts").write_text("test('a', () => {});\n", encoding="utf-8")
    (repo / "Custom.tsx").write_text(
        "import { a } from './src/EntityUtils';\nexport const c = a;\n", encoding="utf-8"
    )
    base = _commit(repo, "base")
    (utils / "EntityUtils.ts").write_text("export const a = 2;\n", encoding="utf-8")
    target = _commit(repo, "target")
    manifests = {"BANK-OM-001": _manifest(["Custom.tsx"])}
    report = WS.analyze(str(repo), base, target, target, manifests)
    assert [item.suggested_path for item in report.suggestions] == ["src/EntityUtils.ts"]


# ---- deleted watch paths ---------------------------------------------------
def _deleted_watch_fixture(tmp_path, *, add_replacements=True):
    repo = _repo(tmp_path)
    utils = repo / "src/utils"
    utils.mkdir(parents=True)
    (utils / "EntityUtils.tsx").write_text("export const getEntityName = () => 1;\n", encoding="utf-8")
    (repo / "CustomPanel.tsx").write_text(
        "import { getEntityName } from './src/utils/EntityUtils';\nexport const P = getEntityName;\n",
        encoding="utf-8",
    )
    base = _commit(repo, "base")
    (utils / "EntityUtils.tsx").unlink()
    if add_replacements:
        (utils / "EntityNameUtils.ts").write_text("export const getEntityName = () => 1;\n", encoding="utf-8")
        (utils / "EntityLinkUtils.ts").write_text("export const getEntityLink = () => 2;\n", encoding="utf-8")
    target = _commit(repo, "upstream split")
    manifests = {
        "BANK-OM-004": _manifest(["CustomPanel.tsx"], watch=["src/utils/EntityUtils.tsx"]),
    }
    return repo, base, target, manifests


def test_a_deleted_watch_path_is_reported_with_move_candidates(tmp_path):
    repo, base, target, manifests = _deleted_watch_fixture(tmp_path)
    report = WS.analyze(str(repo), base, target, base, manifests)
    assert len(report.deleted_watch) == 1
    finding = report.deleted_watch[0]
    assert finding.customization_id == "BANK-OM-004"
    assert finding.watch_path == "src/utils/EntityUtils.tsx"
    assert finding.change_type == "deleted"
    assert finding.authority == "code-owner-review-required"
    assert "src/utils/EntityNameUtils.ts" in finding.candidates
    assert "src/utils/EntityLinkUtils.ts" in finding.candidates


def test_move_candidates_exclude_unrelated_new_files_in_the_same_directory(tmp_path):
    """Sharing only a role word (`Utils`) is not evidence of a move."""
    repo = _repo(tmp_path)
    utils = repo / "src/utils"
    utils.mkdir(parents=True)
    (utils / "EntityUtils.tsx").write_text("export const a = 1;\n", encoding="utf-8")
    (repo / "Custom.tsx").write_text("export const c = 1;\n", encoding="utf-8")
    base = _commit(repo, "base")
    (utils / "EntityUtils.tsx").unlink()
    (utils / "EntityNameUtils.ts").write_text("export const a = 1;\n", encoding="utf-8")
    (utils / "AdvancedSearchPureUtils.ts").write_text("export const b = 2;\n", encoding="utf-8")
    target = _commit(repo, "target")
    manifests = {"BANK-OM-004": _manifest(["Custom.tsx"], watch=["src/utils/EntityUtils.tsx"])}
    finding = WS.analyze(str(repo), base, target, base, manifests).deleted_watch[0]
    assert finding.candidates == ("src/utils/EntityNameUtils.ts",)


def test_a_deletion_without_candidates_is_still_reported(tmp_path):
    repo, base, target, manifests = _deleted_watch_fixture(tmp_path, add_replacements=False)
    report = WS.analyze(str(repo), base, target, base, manifests)
    assert len(report.deleted_watch) == 1
    assert report.deleted_watch[0].candidates == ()
    assert report.packet()["deleted_watch_paths"][0]["candidate_count"] == 0


# ---- timeout ---------------------------------------------------------------
def test_a_deadline_produces_an_incomplete_report_not_an_empty_one(tmp_path):
    repo = _repo(tmp_path)
    (repo / "CoreRegistry.java").write_text("class CoreRegistry {}\n", encoding="utf-8")
    (repo / "Custom.java").write_text("class Custom { CoreRegistry r; }\n", encoding="utf-8")
    base = _commit(repo, "base")
    (repo / "CoreRegistry.java").write_text("class CoreRegistry { int v; }\n", encoding="utf-8")
    target = _commit(repo, "target")
    manifests = {"BANK-OM-001": _manifest(["Custom.java"])}

    # a deadline already in the past stops at the first checkpoint
    report = WS.analyze(str(repo), base, target, target, manifests, timeout_seconds=-1)
    assert report.complete is False
    assert report.stage != WS.STAGE_DONE
    assert report.suggestions == ()
    packet = report.packet()
    assert packet["complete"] is False
    assert packet["suggestion_count"] == 0


@pytest.mark.parametrize("bad", [0, -5, "300", True, None])
def test_an_unusable_gate_timeout_is_rejected(bad):
    from acgh import phase

    if bad is None:
        assert phase.validated_timeout(300) == 300.0
        return
    with pytest.raises(phase.PhaseError):
        phase.validated_timeout(bad)


# ---- cache -----------------------------------------------------------------
def test_cache_hit_and_miss_produce_the_same_judgment_payload(tmp_path):
    repo = _repo(tmp_path / "repo")
    (repo / "CoreRegistry.java").write_text("class CoreRegistry {}\n", encoding="utf-8")
    (repo / "Custom.java").write_text("class Custom { CoreRegistry r; }\n", encoding="utf-8")
    base = _commit(repo, "base")
    (repo / "CoreRegistry.java").write_text("class CoreRegistry { int v; }\n", encoding="utf-8")
    target = _commit(repo, "target")
    manifests = {"BANK-OM-001": _manifest(["Custom.java"])}
    cache = tmp_path / "cache"

    first = WS.analyze(str(repo), base, target, target, manifests, cache_dir=cache)
    second = WS.analyze(str(repo), base, target, target, manifests, cache_dir=cache)
    assert first.telemetry["cache"] == "miss"
    assert second.telemetry["cache"] == "hit"
    assert first.packet() == second.packet()
    # telemetry is observational and must stay out of the judgment payload
    assert "elapsed_seconds" not in json.dumps(first.packet())
    assert "cache" not in first.packet()


def test_a_changed_manifest_invalidates_the_cache(tmp_path):
    repo = _repo(tmp_path / "repo")
    (repo / "CoreRegistry.java").write_text("class CoreRegistry {}\n", encoding="utf-8")
    (repo / "Custom.java").write_text("class Custom { CoreRegistry r; }\n", encoding="utf-8")
    (repo / "Other.java").write_text("class Other { CoreRegistry r; }\n", encoding="utf-8")
    base = _commit(repo, "base")
    (repo / "CoreRegistry.java").write_text("class CoreRegistry { int v; }\n", encoding="utf-8")
    target = _commit(repo, "target")
    cache = tmp_path / "cache"

    first = WS.analyze(
        str(repo), base, target, target,
        {"BANK-OM-001": _manifest(["Custom.java"])}, cache_dir=cache,
    )
    second = WS.analyze(
        str(repo), base, target, target,
        {"BANK-OM-001": _manifest(["Custom.java", "Other.java"])}, cache_dir=cache,
    )
    assert second.telemetry["cache"] == "miss"
    assert first.suggestions[0].referenced_from == ("Custom.java",)
    assert second.suggestions[0].referenced_from == ("Custom.java", "Other.java")


def test_results_are_deterministic_for_the_same_inputs(tmp_path):
    repo = _repo(tmp_path)
    for name in ["Alpha", "Beta", "Gamma"]:
        (repo / f"{name}Service.java").write_text(f"class {name}Service {{}}\n", encoding="utf-8")
    (repo / "Custom.java").write_text(
        "class Custom { AlphaService a; BetaService b; GammaService g; }\n", encoding="utf-8"
    )
    base = _commit(repo, "base")
    for name in ["Alpha", "Beta", "Gamma"]:
        (repo / f"{name}Service.java").write_text(f"class {name}Service {{ int v; }}\n", encoding="utf-8")
    target = _commit(repo, "target")
    manifests = {"BANK-OM-001": _manifest(["Custom.java"])}
    packets = [
        json.dumps(WS.analyze(str(repo), base, target, target, manifests).packet(), sort_keys=True)
        for _ in range(3)
    ]
    assert len(set(packets)) == 1
    order = [item.suggested_path for item in WS.analyze(str(repo), base, target, target, manifests).suggestions]
    assert order == sorted(order)


# ---- standalone rerun ------------------------------------------------------
def test_standalone_command_writes_its_own_file_and_never_a_phase_result(tmp_path):
    from harness import run_phase_bundle

    repo, base, target, manifests = _deleted_watch_fixture(tmp_path / "repo")
    output = tmp_path / "watch-suggest-result.json"
    existing = tmp_path / "phase-result.json"
    existing.write_text('{"canonical_payload": {}}', encoding="utf-8")

    report = WS.analyze(str(repo), base, target, base, manifests)
    payload = {
        "status": "complete", "complete": report.complete, "packet": report.packet(),
    }
    run_phase_bundle._write_guarded(
        output,
        (json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n").encode(),
        label="watch-suggest 결과",
    )
    assert output.is_file()
    assert existing.read_text(encoding="utf-8") == '{"canonical_payload": {}}'
    with pytest.raises(run_phase_bundle.PhaseCLIError, match="덮어쓰지 않습니다"):
        run_phase_bundle._write_guarded(output, b"{}", label="watch-suggest 결과")


def test_om_workflow_exposes_the_standalone_rerun(monkeypatch):
    import sys

    from harness import om_workflow

    monkeypatch.setattr(sys, "argv", [
        "om_workflow.py", "watch-suggest", "--repo", "/work/product",
        "--version", "1.13.1", "--base", "aaa", "--target", "bbb", "--timeout", "600",
    ])
    parsed = om_workflow.parse_args()
    assert parsed.command == "watch-suggest"
    assert parsed.timeout == 600.0


def test_human_timeout_output_refuses_to_present_partial_results(capsys):
    from harness import om_workflow

    om_workflow._print_human_phase("watch-suggest", {
        "status": "incomplete",
        "process_exit_code": 3,
        "complete": False,
        "packet": {"complete": False, "stage": "customization-index",
                   "counts": {"changed_paths": 1702}, "excluded": {}},
        "telemetry": {"elapsed_seconds": 295.0, "cache": "miss"},
        "rerun_command": "harness/om_workflow.py watch-suggest --timeout 900",
    })
    text = capsys.readouterr().out
    assert "중단 · 제한 시간 초과" in text
    assert "마지막 완료 단계: customization-index" in text
    assert "부분 결과는 제안으로 사용할 수 없습니다" in text
    assert "--timeout 900" in text
