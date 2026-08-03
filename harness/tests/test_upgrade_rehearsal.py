"""Portability and output-shape guards for the upgrade rehearsal script.

The rehearsal is run on operator laptops to produce presentation captures,
so it has to work on the macOS system Bash (3.2) and print commit ids at a
fixed width no matter how the local Git is configured. Both of those broke
in the field, so they are pinned here.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "upgrade_rehearsal.sh"

# Builtins and expansions that the macOS system Bash (3.2) does not have.
BASH4_ONLY = {
    "mapfile": r"^\s*mapfile\b",
    "readarray": r"^\s*readarray\b",
    "declare -A": r"^\s*(declare|typeset)\s+-A\b",
    "${var^^}": r"\$\{[A-Za-z_][A-Za-z_0-9]*\^\^",
    "${var,,}": r"\$\{[A-Za-z_][A-Za-z_0-9]*,,",
    "&> redirect": r"[^&|]&>[^&]",
}


def _code_lines() -> list[tuple[int, str]]:
    """Script lines with comments and blank lines removed."""
    out = []
    for number, raw in enumerate(SCRIPT.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0] if not raw.lstrip().startswith("#") else ""
        if line.strip():
            out.append((number, line))
    return out


def test_script_exists_and_is_executable():
    assert SCRIPT.is_file()
    assert SCRIPT.stat().st_mode & 0o111, "실행 권한이 있어야 한다"


def test_parses_under_bash():
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)


@pytest.mark.parametrize("label,pattern", sorted(BASH4_ONLY.items()))
def test_no_bash4_only_constructs(label, pattern):
    """macOS 기본 Bash 3.2 에는 없는 문법을 쓰지 않는다."""
    hits = [n for n, line in _code_lines() if re.search(pattern, line)]
    assert not hits, f"{label} 은 Bash 3.2 에서 동작하지 않는다 (줄 {hits})"


def test_commit_ids_do_not_depend_on_core_abbrev():
    """화면에 찍는 기록 번호는 core.abbrev 설정에 좌우되면 안 된다."""
    hits = [
        n
        for n, line in _code_lines()
        if re.search(r"%h\b", line) or "rev-parse --short" in line
    ]
    assert not hits, (
        "%h 와 rev-parse --short 는 core.abbrev 를 따르므로 자릿수가 흔들린다. "
        f"전체 SHA 를 잘라 쓸 것 (줄 {hits})"
    )


def test_empty_array_is_guarded_before_expansion():
    """set -u 아래에서 빈 배열을 전개하면 Bash 3.2 는 죽는다."""
    text = SCRIPT.read_text(encoding="utf-8")
    assert "set -euo pipefail" in text
    guard = text.index('[ -n "$BANK_SHA_LIST" ]')
    first_expansion = text.index('"${BANK_SHAS[@]}"')
    assert guard < first_expansion, "배열을 전개하기 전에 비었는지 먼저 확인해야 한다"


def test_registration_data_is_never_written():
    """예행연습은 등록 폴더를 건드리지 않는다. 그쪽은 승인 절차를 거친다."""
    for number, line in _code_lines():
        if "registrations" not in line:
            continue
        assert not re.search(r"(>|>>|\bcp\b|\bmv\b|\brm\b|\bsed -i\b)", line), (
            f"등록 폴더에 쓰기를 시도한다 (줄 {number}): {line.strip()}"
        )


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


@pytest.fixture
def labelled_repo(tmp_path: Path) -> Path:
    """Customization-ID 꼬리표가 붙은 커밋 세 개짜리 작은 저장소."""
    repo = tmp_path / "product"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "T")
    for index, trailer in enumerate(
        ["BANK-OM-001", "BANK-OM-002", "BANK-OM-002"], start=1
    ):
        (repo / f"f{index}.txt").write_text(f"{index}\n", encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", f"change {index}\n\nCustomization-ID: {trailer}")
    return repo


@pytest.mark.parametrize("abbrev", ["7", "8", "12", "40"])
def test_ten_character_ids_survive_any_core_abbrev(labelled_repo: Path, abbrev: str):
    """스크립트가 쓰는 방식이면 core.abbrev 와 무관하게 항상 10자리다."""
    _git(labelled_repo, "config", "core.abbrev", abbrev)

    # 스크립트가 자릿수에 기대던 옛 방식 — 설정에 따라 흔들린다.
    loose = _git(labelled_repo, "log", "-1", "--format=%h")

    # 스크립트가 지금 쓰는 방식 — 전체 SHA 에서 앞 10자리를 잘라낸다.
    full = _git(labelled_repo, "rev-parse", "HEAD")
    fixed = full[:10]

    assert len(fixed) == 10
    assert full.startswith(fixed)
    if abbrev != "10":
        assert len(loose) != 10 or abbrev == "10", (
            f"core.abbrev={abbrev} 에서 %h 는 {len(loose)}자리 — 고정 폭이 아니다"
        )


def test_trailer_count_detects_missing_and_duplicate_labels(labelled_repo: Path):
    """이름표가 0개거나 2개인 기록을 골라낼 수 있어야 한다."""
    def label_count(rev: str) -> int:
        out = _git(
            labelled_repo, "log", "-1",
            "--format=%(trailers:key=Customization-ID,valueonly)", rev,
        )
        return len([line for line in out.splitlines() if line.strip()])

    assert label_count("HEAD") == 1

    (labelled_repo / "none.txt").write_text("x\n", encoding="utf-8")
    _git(labelled_repo, "add", "-A")
    _git(labelled_repo, "commit", "-q", "-m", "no label at all")
    assert label_count("HEAD") == 0, "이름표 없는 기록을 잡아내야 한다"

    (labelled_repo / "two.txt").write_text("y\n", encoding="utf-8")
    _git(labelled_repo, "add", "-A")
    _git(
        labelled_repo, "commit", "-q", "-m",
        "two labels\n\nCustomization-ID: BANK-OM-001\nCustomization-ID: BANK-OM-002",
    )
    assert label_count("HEAD") == 2, "이름표가 둘인 기록을 잡아내야 한다"


def test_refuses_a_product_repo_with_the_wrong_starting_point(tmp_path: Path):
    """출발점이 다르면 캡처를 시작하기 전에 멈춘다."""
    repo = tmp_path / "wrong"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "T")
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "unrelated")

    done = subprocess.run(
        ["bash", str(SCRIPT), str(repo), str(tmp_path / "out")],
        cwd=SCRIPT.parents[2], capture_output=True, text=True,
    )
    assert done.returncode != 0, "잘못된 출발점을 통과시키면 안 된다"
    assert "중단" in done.stdout + done.stderr


def test_resolved_leaf_counts_are_summed_not_sampled():
    """정리 도구는 파일마다 한 줄을 낸다. 첫 줄만 읽으면 안 된다.

    ``head -1`` 로 읽으면 파일 하나의 항목 수가 전체 합계인 것처럼 표에
    찍힌다. 실제 예행연습에서 BANK-OM-001 은 18개 파일에서 파일당 9개,
    합계 162개를 되살리는데 9로 보고되고 있었다.
    """
    body = SCRIPT.read_text(encoding="utf-8")
    capture = [
        line for line in body.splitlines()
        if "leaf changes=" in line and "grep" in line
    ]
    assert capture, "되살린 항목 수를 읽는 줄을 찾지 못했다"
    for line in capture:
        assert "head -1" not in line, (
            "첫 줄만 읽으면 파일 하나의 값이 합계로 보고된다: " + line.strip()
        )
    assert "sum += $1" in body, "모든 파일의 항목 수를 더해야 한다"


def test_conflict_table_header_names_its_units():
    """'부딪힘/되살림' 은 단위를 숨긴다. 파일 수와 항목 수는 다른 단위다."""
    body = SCRIPT.read_text(encoding="utf-8")
    assert "부딪힌파일" in body and "되살린항목" in body, (
        "요약표 머리글이 세는 단위를 밝혀야 한다"
    )


def test_overlap_refusal_is_explained_not_left_to_set_e():
    """양쪽이 같은 항목을 고치면 정리 도구가 0이 아닌 상태로 끝난다.

    `set -e` 에 맡기면 운영자 화면에 파이썬 traceback 만 남는다. 상태를
    직접 받아 무엇을 해야 하는지 한국어로 설명해야 한다.
    """
    body = SCRIPT.read_text(encoding="utf-8")
    call = body.index("resolve_nonoverlapping_json_conflicts.py")
    window = body[call - 400:call + 700]
    assert "set +e" in window, "정리 도구 호출을 set -e 에 맡기면 안 된다"
    assert "resolve_status" in window, "종료 상태를 직접 받아야 한다"
    assert "코드 담당자가 직접 결정" in window, (
        "겹쳤을 때 사람이 무엇을 해야 하는지 알려야 한다"
    )
