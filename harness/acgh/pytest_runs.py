"""Deterministic pytest execution adapter for T62 runtime contracts.

Required selectors come from the validated contract catalog. They are executed
without a shell, one selector per fresh Python process, and summarized from
JUnit XML rather than from human-oriented console text. Missing/corrupt XML,
timeouts, internal pytest exits, and exit/XML disagreement are harness errors;
they must not be flattened into an ordinary test failure.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from acgh import testruns
from acgh import verdict


class PytestRunError(RuntimeError):
    """The test harness could not produce trustworthy execution evidence."""


def _count(root: ET.Element, name: str) -> int:
    if root.tag == "testsuite":
        nodes = [root]
    elif root.tag == "testsuites":
        nodes = list(root.findall("testsuite"))
    else:
        raise PytestRunError(f"unexpected JUnit root element: {root.tag}")
    try:
        return sum(int(node.attrib.get(name, "0")) for node in nodes)
    except ValueError as exc:
        raise PytestRunError(f"invalid JUnit {name} count") from exc


def parse_junit_outcome(path, *, exit_code: int) -> str:
    """Return pass/fail/error/skipped after reconciling JUnit and pytest exit."""
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        raise PytestRunError(f"cannot read JUnit result: {exc}") from exc

    tests = _count(root, "tests")
    failures = _count(root, "failures")
    errors = _count(root, "errors")
    skipped = _count(root, "skipped")
    if tests <= 0:
        raise PytestRunError("JUnit result contains no tests")
    if any(value < 0 for value in (failures, errors, skipped)):
        raise PytestRunError("JUnit result contains a negative count")
    if failures + errors + skipped > tests:
        raise PytestRunError("JUnit result counts are internally inconsistent")

    if exit_code not in {0, 1}:
        raise PytestRunError(f"pytest internal/usage exit code: {exit_code}")
    if errors:
        outcome = "error"
    elif failures:
        outcome = "fail"
    elif skipped:
        # Any skip means this required selector was not fully proven.
        outcome = "skipped"
    else:
        outcome = "pass"

    expected_exit = 1 if outcome in {"fail", "error"} else 0
    if exit_code != expected_exit:
        raise PytestRunError(
            f"pytest exit/JUnit mismatch: exit={exit_code}, outcome={outcome}"
        )
    return outcome


def run_selector(
    root,
    selector: str,
    *,
    timeout_seconds: int = 300,
    environment: dict[str, str] | None = None,
) -> str:
    """Execute one already-validated selector and return its worst outcome."""
    if timeout_seconds < 1:
        raise PytestRunError("timeout_seconds must be positive")
    resolved_root = Path(root).resolve(strict=True)
    env = os.environ.copy()
    if environment:
        env.update(environment)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    with tempfile.TemporaryDirectory(prefix="acgh-t62-") as temp:
        junit = Path(temp) / "junit.xml"
        command = [
            sys.executable,
            "-m",
            "pytest",
            selector,
            "-q",
            "--tb=short",
            f"--junitxml={junit}",
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=resolved_root,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise PytestRunError(
                f"required selector timed out after {timeout_seconds}s: "
                f"{selector}"
            ) from exc
        except OSError as exc:
            raise PytestRunError(
                f"could not start pytest for {selector}: {exc}"
            ) from exc
        return parse_junit_outcome(junit, exit_code=completed.returncode)


def run_required_tests(
    root,
    selectors,
    *,
    retries: int = 1,
    timeout_seconds: int = 300,
    environment: dict[str, str] | None = None,
) -> tuple[testruns.TestAttempt, ...]:
    """Run each required selector and retain every fail/error retry."""
    if retries < 0:
        raise PytestRunError("retries must be zero or greater")
    normalized = sorted(set(selectors))
    if not normalized:
        raise PytestRunError("required selector set is empty")

    attempts: list[testruns.TestAttempt] = []
    for selector in normalized:
        for attempt in range(1, retries + 2):
            outcome = run_selector(
                root,
                selector,
                timeout_seconds=timeout_seconds,
                environment=environment,
            )
            attempts.append(testruns.TestAttempt(selector, attempt, outcome))
            if outcome not in {"fail", "error"}:
                break
    return tuple(attempts)


def suite_digest(root, selectors, *, metadata_paths=()) -> str:
    """Bind suite identity to selector source and catalog/manifest bytes."""
    resolved_root = Path(root).resolve(strict=True)
    payload = {"selectors": [], "metadata": []}
    for selector in sorted(set(selectors)):
        raw_path = selector.split("::", 1)[0]
        candidate = resolved_root / raw_path
        path = candidate.resolve(strict=True)
        try:
            relative = path.relative_to(resolved_root)
        except ValueError as exc:
            raise PytestRunError(
                f"suite selector escapes root: {selector}"
            ) from exc
        if candidate.is_symlink() or not path.is_file():
            raise PytestRunError(
                f"suite selector is not a regular file: {selector}"
            )
        payload["selectors"].append(
            {
                "selector": selector,
                "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )

    for item in sorted(Path(value) for value in metadata_paths):
        candidate = item
        path = candidate.resolve(strict=True)
        try:
            relative = path.relative_to(resolved_root)
        except ValueError as exc:
            raise PytestRunError(f"suite metadata escapes root: {item}") from exc
        if candidate.is_symlink() or not path.is_file():
            raise PytestRunError(f"suite metadata is not a regular file: {item}")
        payload["metadata"].append(
            {
                "path": relative.as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    return verdict.canonical_digest(payload)
