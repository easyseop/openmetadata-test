#!/usr/bin/env python3
"""Fill a shared-code draft from BANK-OM commit diffs and verify the proposal.

This command is intentionally separate from the empty-draft generator.  It
uses each BANK-OM commit only as attribution evidence, then accepts an
automatically extracted assertion only when the same definition is present in
the final candidate branch.  The generated file remains a proposal until a
reviewer approves it.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from acgh import shared_code


class ProposalError(ValueError):
    """A complete, verified proposal cannot be generated."""


_CODE_SUFFIXES = frozenset({".java", ".ts", ".tsx", ".sql"})
_MISSING = object()


def _git(repo: str, *args: str, allow_missing: bool = False) -> str | None:
    completed = subprocess.run(
        ["git", "-C", repo, *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode == 0:
        return completed.stdout
    if allow_missing and completed.returncode == 128:
        return None
    message = completed.stderr.strip() or completed.stdout.strip()
    raise ProposalError(f"git {' '.join(args)} failed: {message}")


def _pin(repo: str, ref: str) -> str:
    value = _git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}")
    assert value is not None
    return value.strip()


def discover_id_commits(repo: str, official: str, candidate: str) -> dict[str, str]:
    """Return the one commit carrying each exact Customization-ID trailer."""
    official_sha = _pin(repo, official)
    candidate_sha = _pin(repo, candidate)
    raw = _git(
        repo,
        "log",
        "--reverse",
        "--format=%H%x00%(trailers:key=Customization-ID,valueonly,separator=%x1f)",
        f"{official_sha}..{candidate_sha}",
    )
    assert raw is not None
    found: dict[str, str] = {}
    for line in raw.splitlines():
        if "\x00" not in line:
            continue
        commit_sha, trailer_text = line.split("\x00", 1)
        ids = [item.strip() for item in trailer_text.split("\x1f") if item.strip()]
        if len(ids) != 1 or not re.fullmatch(r"BANK-OM-\d{3,}", ids[0]):
            continue
        customization_id = ids[0]
        if customization_id in found:
            raise ProposalError(
                f"{customization_id} appears on more than one commit in the selected range"
            )
        found[customization_id] = commit_sha
    return found


def _blob(repo: str, ref: str, path: str) -> str | None:
    return _git(repo, "show", f"{ref}:{path}", allow_missing=True)


def _pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _changed_leaves(before: Any, after: Any, pointer: str = "") -> list[tuple[str, Any]]:
    """Return structured leaf values added or changed by one commit."""
    if isinstance(after, dict):
        previous = before if isinstance(before, dict) else {}
        results: list[tuple[str, Any]] = []
        for key in sorted(after):
            child = pointer + "/" + _pointer_escape(str(key))
            results.extend(_changed_leaves(previous.get(key, _MISSING), after[key], child))
        return results
    if isinstance(after, list):
        previous = before if isinstance(before, list) else []
        results = []
        for index, value in enumerate(after):
            old = previous[index] if index < len(previous) else _MISSING
            results.extend(_changed_leaves(old, value, f"{pointer}/{index}"))
        return results
    if before is _MISSING or before != after:
        return [(pointer or "/", after)]
    return []


def _pointer_value(document: Any, pointer: str) -> Any:
    current = document
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            current = current[token]
        elif isinstance(current, list):
            current = current[int(token)]
        else:
            raise KeyError(pointer)
    return current


def _structured_assertions(
    before_text: str | None,
    commit_text: str,
    final_text: str,
    matcher: str,
    assertion_prefix: str,
) -> list[dict]:
    loader = json.loads if matcher == "json_value" else yaml.safe_load
    before = loader(before_text) if before_text is not None else _MISSING
    after = loader(commit_text)
    final = loader(final_text)
    assertions: list[dict] = []
    for pointer, expected in _changed_leaves(before, after):
        try:
            final_value = _pointer_value(final, pointer)
        except (KeyError, IndexError, ValueError, TypeError):
            continue
        if final_value != expected:
            continue
        assertions.append(
            {
                "id": f"{assertion_prefix}-{len(assertions) + 1}",
                "matcher": matcher,
                "pointer": pointer,
                "expected": expected,
            }
        )
    return assertions


def _added_runs(diff_text: str) -> list[list[str]]:
    runs: list[list[str]] = []
    current: list[str] = []
    in_hunk = False
    for line in diff_text.splitlines():
        if line.startswith("@@"):
            if current:
                runs.append(current)
                current = []
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            current.append(line[1:])
        else:
            if current:
                runs.append(current)
                current = []
    if current:
        runs.append(current)
    return runs


def _best_surviving_fragment(lines: list[str], final_text: str, suffix: str) -> tuple[str, int] | None:
    """Choose the longest added code block that still exists in the final file."""
    final_tokens = shared_code._code_tokens(final_text, suffix)
    for width in range(len(lines), 0, -1):
        for start in range(0, len(lines) - width + 1):
            fragment = "\n".join(lines[start : start + width]).strip()
            tokens = shared_code._code_tokens(fragment, suffix)
            # Ignore blank/comment-only and punctuation-only fragments.
            if len(tokens) < 3 or not any(
                token.startswith("STRING:") or any(char.isalnum() for char in token)
                for token in tokens
            ):
                continue
            count = shared_code._subsequence_count(final_tokens, tokens)
            if count:
                return fragment + "\n", count
    return None


def _code_assertions(
    diff_text: str,
    final_text: str,
    suffix: str,
    assertion_prefix: str,
) -> list[dict]:
    assertions: list[dict] = []
    seen: set[tuple[str, int]] = set()
    for run in _added_runs(diff_text):
        selected = _best_surviving_fragment(run, final_text, suffix)
        if selected is None or selected in seen:
            continue
        seen.add(selected)
        fragment, occurrences = selected
        assertion = {
            "id": f"{assertion_prefix}-{len(assertions) + 1}",
            "matcher": "code_fragment",
            "fragment": fragment,
        }
        if occurrences != 1:
            assertion["occurrences"] = occurrences
        assertions.append(assertion)
    return assertions


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def build_proposal(
    repo: str,
    official: str,
    candidate: str,
    draft: dict,
) -> tuple[dict, dict[str, str]]:
    definitions = draft.get("definitions") if isinstance(draft, dict) else None
    if not isinstance(definitions, list):
        raise ProposalError("draft has no definitions list")
    commit_by_id = discover_id_commits(repo, official, candidate)
    candidate_sha = _pin(repo, candidate)
    proposed: list[dict] = []
    unresolved: list[str] = []
    for item in definitions:
        if not isinstance(item, dict):
            raise ProposalError("every draft definition must be a mapping")
        path = item.get("path")
        customization_id = item.get("customization_id")
        if not isinstance(path, str) or not isinstance(customization_id, str):
            raise ProposalError("every draft definition needs path and customization_id")
        commit_sha = commit_by_id.get(customization_id)
        if commit_sha is None:
            unresolved.append(f"{customization_id} {path}: no exact ID commit")
            continue
        parent = f"{commit_sha}^"
        before_text = _blob(repo, parent, path)
        commit_text = _blob(repo, commit_sha, path)
        final_text = _blob(repo, candidate_sha, path)
        if commit_text is None or final_text is None:
            unresolved.append(f"{customization_id} {path}: file is missing")
            continue
        suffix = PurePosixPath(path).suffix.lower()
        prefix = _slug(f"{customization_id}-{PurePosixPath(path).stem}")
        try:
            if suffix == ".json":
                assertions = _structured_assertions(
                    before_text, commit_text, final_text, "json_value", prefix
                )
            elif suffix in {".yaml", ".yml"}:
                assertions = _structured_assertions(
                    before_text, commit_text, final_text, "yaml_value", prefix
                )
            elif suffix in _CODE_SUFFIXES:
                diff_text = _git(
                    repo,
                    "diff",
                    "--unified=0",
                    parent,
                    commit_sha,
                    "--",
                    path,
                )
                assert diff_text is not None
                assertions = _code_assertions(diff_text, final_text, suffix, prefix)
            else:
                assertions = []
        except (json.JSONDecodeError, yaml.YAMLError, TypeError, KeyError) as exc:
            unresolved.append(f"{customization_id} {path}: cannot analyze: {exc}")
            continue
        if not assertions:
            unresolved.append(
                f"{customization_id} {path}: no changed definition survives in candidate"
            )
            continue
        proposed.append(
            {
                "path": path,
                "customization_id": customization_id,
                "assertions": assertions,
            }
        )
    if unresolved:
        preview = "; ".join(unresolved[:10])
        remaining = "" if len(unresolved) <= 10 else f"; ... {len(unresolved) - 10} more"
        raise ProposalError(
            f"unresolved definition pairs={len(unresolved)}: {preview}{remaining}"
        )
    return {"schema_version": 1, "definitions": proposed}, commit_by_id


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Extract proposed shared-code assertions from exact BANK-OM commits "
            "and verify all definitions against the final candidate"
        )
    )
    parser.add_argument("--repo", required=True)
    parser.add_argument("--official", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--owners", required=True, type=Path)
    parser.add_argument("--draft", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.output.exists():
            existing = yaml.safe_load(args.output.read_text(encoding="utf-8"))
            owners = yaml.safe_load(args.owners.read_text(encoding="utf-8"))
            catalog = shared_code.parse_catalog(existing)
            result = shared_code.check_shared_code_definitions(
                args.repo, args.candidate, catalog, owners
            )
            if result.verdict != "pass":
                raise ProposalError(
                    f"existing proposal verification={result.verdict}: "
                    + "; ".join(result.reasons)
                )
            print(
                json.dumps(
                    {
                        "status": "PROPOSAL_ALREADY_EXISTS",
                        "output": str(args.output.absolute()),
                        "definition_pairs": len(catalog.definitions),
                        "assertions": sum(
                            len(item.assertions) for item in catalog.definitions
                        ),
                        "candidate_verification": "PASS",
                        "requires_human_approval": True,
                        "next_action": (
                            "기존 제안 파일을 사람 검토와 등록 plan의 입력으로 "
                            "사용하십시오."
                        ),
                    },
                    ensure_ascii=False,
                )
            )
            return 0
        owners = yaml.safe_load(args.owners.read_text(encoding="utf-8"))
        draft = yaml.safe_load(args.draft.read_text(encoding="utf-8"))
        proposal, commits = build_proposal(
            args.repo, args.official, args.candidate, copy.deepcopy(draft)
        )
        catalog = shared_code.parse_catalog(proposal)
        result = shared_code.check_shared_code_definitions(
            args.repo, args.candidate, catalog, owners
        )
        if result.verdict != "pass":
            raise ProposalError(
                f"final candidate verification={result.verdict}: "
                + "; ".join(result.reasons)
            )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            yaml.safe_dump(
                proposal,
                allow_unicode=True,
                sort_keys=False,
                width=1000,
            ),
            encoding="utf-8",
        )
    except (
        OSError,
        UnicodeError,
        yaml.YAMLError,
        ProposalError,
        shared_code.SharedCodeError,
    ) as exc:
        print(json.dumps({"status": "ANALYSIS_ERROR", "message": str(exc)}, ensure_ascii=False))
        return 3
    assertions = sum(len(item["assertions"]) for item in proposal["definitions"])
    print(
        json.dumps(
            {
                "status": "PROPOSAL_WRITTEN",
                "output": str(args.output.absolute()),
                "definition_pairs": len(proposal["definitions"]),
                "assertions": assertions,
                "candidate_verification": "PASS",
                "id_commits": commits,
                "requires_human_approval": True,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
