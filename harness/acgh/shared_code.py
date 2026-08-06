"""Shared-file BANK-OM code-definition integrity gate.

``shared-path-owners.yaml`` states which BANK-OM IDs own a path.  Path
ownership alone cannot prove that every owner's actual code remains in the
final file: a commit can touch a file while contributing only whitespace, or
another owner's commit can accidentally carry both features.

This module closes that narrow gap with a separately approved
``shared-code-definitions.yaml`` catalog.  It deliberately checks source
definitions, not runtime behaviour:

* structured JSON/YAML assertions compare an exact pointer value; and
* code-fragment assertions compare a complete, comment-stripped, whitespace-
  normalized definition.  A symbol name in a comment is therefore not proof.

The catalog must cover every ``(shared path, owner ID)`` pair exactly once.
Missing coverage is an analysis error; a trustworthy content mismatch blocks.
"""
from __future__ import annotations

import argparse
import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import jsonschema
import yaml

from acgh import binding
from acgh import gitprim
from acgh import layout
from acgh import verdict


_SCHEMA_PATH = (
    Path(__file__).parent / "schema" / "shared-code-definitions.schema.json"
)
_CODE_SUFFIXES = frozenset({".java", ".ts", ".tsx", ".sql"})


class SharedCodeError(ValueError):
    """A shared-code catalog is malformed or cannot be trusted."""


@dataclass(frozen=True)
class Definition:
    path: str
    customization_id: str
    assertions: tuple[dict, ...]


@dataclass(frozen=True)
class Catalog:
    definitions: tuple[Definition, ...]

    def pairs(self) -> set[tuple[str, str]]:
        return {
            (item.path, item.customization_id) for item in self.definitions
        }


def _schema_validator() -> jsonschema.protocols.Validator:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def parse_catalog(data: dict) -> Catalog:
    if not isinstance(data, dict):
        raise SharedCodeError("shared code definitions are not a mapping")
    errors = sorted(
        _schema_validator().iter_errors(data),
        key=lambda item: (list(item.absolute_path), item.message),
    )
    if errors:
        def location(item) -> str:
            return "/".join(str(part) for part in item.absolute_path) or "<root>"

        raise SharedCodeError(
            "schema: "
            + "; ".join(
                f"{location(item)}: {item.message}" for item in errors
            )
        )

    definitions: list[Definition] = []
    seen_pairs: set[tuple[str, str]] = set()
    for raw in data["definitions"]:
        try:
            normalized_path = layout.ensure_literal(raw["path"])
        except layout.LayoutError as exc:
            raise SharedCodeError(
                f"invalid shared code path {raw['path']!r}: {exc}"
            ) from exc
        pair = (normalized_path, raw["customization_id"])
        if pair in seen_pairs:
            raise SharedCodeError(
                "duplicate shared code definition: "
                f"path={pair[0]} customization_id={pair[1]}"
            )
        seen_pairs.add(pair)

        assertion_ids = [item["id"] for item in raw["assertions"]]
        if len(assertion_ids) != len(set(assertion_ids)):
            raise SharedCodeError(
                f"{pair[0]} {pair[1]} has duplicate assertion ids"
            )
        for assertion in raw["assertions"]:
            _validate_matcher_for_path(normalized_path, assertion)
        definitions.append(
            Definition(
                path=normalized_path,
                customization_id=raw["customization_id"],
                assertions=tuple(raw["assertions"]),
            )
        )
    return Catalog(tuple(definitions))


def load_catalog(path: str | Path) -> Catalog:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise SharedCodeError(f"cannot load shared code definitions: {exc}") from exc
    return parse_catalog(raw)


def _validate_matcher_for_path(path: str, assertion: dict) -> None:
    suffix = PurePosixPath(path).suffix.lower()
    matcher = assertion["matcher"]
    if matcher == "json_value" and suffix != ".json":
        raise SharedCodeError(f"{path}: json_value requires a .json path")
    if matcher == "yaml_value" and suffix not in {".yaml", ".yml"}:
        raise SharedCodeError(f"{path}: yaml_value requires a YAML path")
    if matcher == "code_fragment" and suffix not in _CODE_SUFFIXES:
        raise SharedCodeError(
            f"{path}: code_fragment supports only {sorted(_CODE_SUFFIXES)}"
        )
    if matcher == "code_fragment":
        tokens = _code_tokens(assertion["fragment"], suffix)
        if not tokens:
            raise SharedCodeError(
                f"{path}: code_fragment {assertion['id']!r} contains no code"
            )


def validate_coverage(
    catalog: Catalog,
    shared_path_owners: dict[str, list[str] | tuple[str, ...]],
) -> None:
    if not isinstance(shared_path_owners, dict):
        raise SharedCodeError("shared path owners are not a mapping")
    expected: set[tuple[str, str]] = set()
    for raw_path, raw_owners in shared_path_owners.items():
        try:
            path = layout.ensure_literal(raw_path)
        except layout.LayoutError as exc:
            raise SharedCodeError(
                f"invalid shared owner path {raw_path!r}: {exc}"
            ) from exc
        if (
            not isinstance(raw_owners, (list, tuple))
            or not raw_owners
            or any(not isinstance(owner, str) for owner in raw_owners)
        ):
            raise SharedCodeError(
                f"{path}: shared owners must be a non-empty string list"
            )
        expected.update((path, owner) for owner in raw_owners)

    actual = catalog.pairs()
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        raise SharedCodeError(
            "shared code definition coverage mismatch: "
            f"missing={missing}, extra={extra}"
        )


def _pointer_value(document, pointer: str):
    current = document
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            if token not in current:
                raise KeyError(pointer)
            current = current[token]
        elif isinstance(current, list):
            try:
                current = current[int(token)]
            except (ValueError, IndexError) as exc:
                raise KeyError(pointer) from exc
        else:
            raise KeyError(pointer)
    return current


def _code_tokens(text: str, suffix: str) -> tuple[str, ...]:
    """Tokenize registered source while discarding comments and whitespace.

    The supported shared source formats use C-style comments, SQL line
    comments, or both. Quoted values are one atomic token. Consequently a
    Java definition pasted inside a comment or one large string cannot satisfy
    a real sequence of code tokens. This lexer intentionally supports only
    the registered formats instead of pretending to parse every language AST.
    """
    line_tokens = ("//",) if suffix in {".java", ".ts", ".tsx"} else ("--",)
    block_comments = suffix in {".java", ".ts", ".tsx", ".sql"}
    text = unicodedata.normalize("NFC", text)
    tokens: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        pair = text[index:index + 2]
        if char.isspace():
            index += 1
            continue
        if char in {"'", '"', "`"}:
            quote = char
            start = index
            index += 1
            escaped = False
            while index < len(text):
                current = text[index]
                if escaped:
                    escaped = False
                elif current == "\\":
                    escaped = True
                elif current == quote:
                    index += 1
                    break
                index += 1
            tokens.append("STRING:" + text[start:index])
            continue
        if block_comments and pair == "/*":
            end = text.find("*/", index + 2)
            if end < 0:
                break
            index = end + 2
            continue
        if pair in line_tokens:
            end = text.find("\n", index + 2)
            if end < 0:
                break
            index = end + 1
            continue
        if char.isalnum() or char in {"_", "$"}:
            start = index
            index += 1
            while index < len(text) and (
                text[index].isalnum() or text[index] in {"_", "$"}
            ):
                index += 1
            tokens.append(text[start:index])
            continue
        tokens.append(char)
        index += 1
    return tuple(tokens)


def _subsequence_count(haystack: tuple[str, ...], needle: tuple[str, ...]) -> int:
    if not needle or len(needle) > len(haystack):
        return 0
    width = len(needle)
    return sum(
        haystack[index:index + width] == needle
        for index in range(len(haystack) - width + 1)
    )


def _check_definition(text: str, definition: Definition) -> list[str]:
    reasons: list[str] = []
    suffix = PurePosixPath(definition.path).suffix.lower()
    parsed_json = None
    parsed_yaml = None
    code_tokens = None
    for assertion in definition.assertions:
        matcher = assertion["matcher"]
        assertion_id = assertion["id"]
        if matcher == "json_value":
            if parsed_json is None:
                parsed_json = json.loads(text)
            try:
                actual = _pointer_value(parsed_json, assertion["pointer"])
            except KeyError:
                reasons.append(f"{assertion_id}: JSON pointer missing")
                continue
            if actual != assertion["expected"]:
                reasons.append(
                    f"{assertion_id}: JSON value mismatch "
                    f"expected={assertion['expected']!r} actual={actual!r}"
                )
        elif matcher == "yaml_value":
            if parsed_yaml is None:
                parsed_yaml = yaml.safe_load(text)
            try:
                actual = _pointer_value(parsed_yaml, assertion["pointer"])
            except KeyError:
                reasons.append(f"{assertion_id}: YAML pointer missing")
                continue
            if actual != assertion["expected"]:
                reasons.append(
                    f"{assertion_id}: YAML value mismatch "
                    f"expected={assertion['expected']!r} actual={actual!r}"
                )
        else:
            if code_tokens is None:
                code_tokens = _code_tokens(text, suffix)
            fragment = _code_tokens(assertion["fragment"], suffix)
            expected_count = assertion.get("occurrences", 1)
            actual_count = _subsequence_count(code_tokens, fragment)
            if actual_count != expected_count:
                reasons.append(
                    f"{assertion_id}: code definition occurrence mismatch "
                    f"expected={expected_count} actual={actual_count}"
                )
    return reasons


def check_shared_code_definitions(
    repo: str,
    candidate_ref: str,
    catalog: Catalog,
    shared_path_owners: dict[str, list[str] | tuple[str, ...]],
    *,
    name: str = "shared-code-definitions",
) -> verdict.GateResult:
    try:
        validate_coverage(catalog, shared_path_owners)
        candidate_sha = binding.pin(repo, candidate_ref)
    except (SharedCodeError, binding.BindingError) as exc:
        return verdict.GateResult(name, verdict.ANALYSIS_ERROR, (str(exc),))

    blocks: list[str] = []
    errors: list[str] = []
    for definition in catalog.definitions:
        label = f"{definition.customization_id} {definition.path}"
        try:
            raw = gitprim.blob_bytes(repo, candidate_sha, definition.path)
            text = raw.decode("utf-8")
            findings = _check_definition(text, definition)
        except (gitprim.GitPrimitiveError, UnicodeError) as exc:
            errors.append(f"{label}: cannot read source: {exc}")
            continue
        except (json.JSONDecodeError, yaml.YAMLError, TypeError) as exc:
            errors.append(f"{label}: cannot parse source: {exc}")
            continue
        blocks.extend(f"{label}: {finding}" for finding in findings)

    if errors:
        return verdict.GateResult(name, verdict.ANALYSIS_ERROR, tuple(errors + blocks))
    if blocks:
        return verdict.GateResult(name, verdict.BLOCK, tuple(blocks))
    return verdict.GateResult(
        name,
        verdict.PASS,
        (
            f"candidate={candidate_sha}",
            f"shared_owner_pairs={len(catalog.definitions)}",
            f"assertions={sum(len(item.assertions) for item in catalog.definitions)}",
        ),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify approved BANK-OM definitions inside shared files"
    )
    parser.add_argument("--repo", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--owners", required=True)
    parser.add_argument("--definitions", required=True)
    parser.add_argument(
        "--output",
        type=Path,
        help="선택: 터미널에 표시한 JSON 결과를 같은 내용으로 저장할 파일",
    )
    args = parser.parse_args(argv)
    try:
        owners = yaml.safe_load(Path(args.owners).read_text(encoding="utf-8"))
        catalog = load_catalog(args.definitions)
        result = check_shared_code_definitions(
            args.repo, args.candidate, catalog, owners
        )
    except (OSError, UnicodeError, yaml.YAMLError, SharedCodeError) as exc:
        result = verdict.GateResult(
            "shared-code-definitions", verdict.ANALYSIS_ERROR, (str(exc),)
        )
    rendered = json.dumps(
        {
            "gate": {
                "name": result.name,
                "verdict": result.verdict,
                "reasons": list(result.reasons),
            }
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    print(rendered)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return verdict.to_exit_code(result.verdict)


if __name__ == "__main__":
    raise SystemExit(main())
