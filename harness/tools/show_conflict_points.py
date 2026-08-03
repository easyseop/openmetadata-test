#!/usr/bin/env python3
"""충돌한 JSON 파일에서 실제로 쟁점이 되는 항목만 뽑아 보여준다.

충돌 표시(``<<<<<<<``)는 파일을 통째로 감싸기 때문에, 3천 줄짜리 문구
파일이 충돌하면 어디가 문제인지 눈으로 찾을 수 없다. 이 도구는 Git 이
들고 있는 세 벌(출발점/새 버전/우리 것)을 항목 단위로 갈라 비교해서
사람이 볼 것만 남긴다.

읽기만 한다. 파일을 고치지도, 충돌을 해결하지도 않는다. 해결은
``resolve_nonoverlapping_json_conflicts.py`` 가 한다.

사용법:
    show_conflict_points.py --repo <충돌이 난 작업 폴더> [--file <경로>]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


MISSING = object()


def git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True
    )
    if done.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} 실패: {done.stderr.strip()}")
    return done.stdout


def stage(repo: Path, number: int, path: str) -> dict:
    return json.loads(git(repo, "show", f":{number}:{path}"))


def flatten(value: object, prefix: tuple[str, ...] = ()) -> dict:
    if isinstance(value, dict):
        out: dict = {}
        for key, child in value.items():
            out.update(flatten(child, (*prefix, key)))
        return out
    return {prefix: value}


def changed(before: dict, after: dict) -> set:
    a, b = flatten(before), flatten(after)
    return {k for k in set(a) | set(b) if a.get(k, MISSING) != b.get(k, MISSING)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--file", help="한 파일만 볼 때 지정")
    parser.add_argument(
        "--max-items", type=int, default=12, help="파일당 보여줄 항목 수"
    )
    args = parser.parse_args()
    repo = args.repo.resolve()

    conflicted = [
        line
        for line in git(repo, "diff", "--name-only", "--diff-filter=U").split()
        if args.file is None or line == args.file
    ]
    if not conflicted:
        print("충돌한 파일이 없습니다.")
        return 0

    non_json = [p for p in conflicted if not p.endswith(".json")]
    json_paths = [p for p in conflicted if p.endswith(".json")]

    print(f"충돌한 파일 {len(conflicted)}개 "
          f"(JSON {len(json_paths)}개, 그 외 {len(non_json)}개)\n")
    for path in non_json:
        print(f"  [자동 해결 대상 아님] {path}")
    if non_json:
        print()

    total_ours = total_overlap = 0
    for path in json_paths:
        base = stage(repo, 1, path)
        theirs_new = stage(repo, 2, path)   # 지금 얹고 있는 쪽 = 새 버전
        ours_bank = stage(repo, 3, path)    # 가져오는 쪽 = 우리 기능

        new_side = changed(base, theirs_new)
        bank_side = changed(base, ours_bank)
        overlap = new_side & bank_side
        total_ours += len(bank_side)
        total_overlap += len(overlap)

        flat_bank = flatten(ours_bank)
        mark = "겹침 있음 ⚠" if overlap else "겹침 없음"
        print(f"── {path}")
        print(f"   새 버전이 바꾼 항목 {len(new_side):>4}개 · "
              f"우리가 넣는 항목 {len(bank_side):>3}개 · {mark}")

        for key in sorted(bank_side)[: args.max_items]:
            value = flat_bank.get(key, MISSING)
            shown = "(삭제)" if value is MISSING else str(value)
            if len(shown) > 58:
                shown = shown[:55] + "…"
            flag = "  ← 겹침" if key in overlap else ""
            print(f"     {'.'.join(key):<44} {shown}{flag}")
        if args.max_items and len(bank_side) > args.max_items:
            print(f"     … 그 외 {len(bank_side) - args.max_items}개")
        print()

    print("─" * 68)
    print(f"우리가 넣는 항목 합계 {total_ours}개 · 겹치는 항목 {total_overlap}개")
    if total_overlap:
        print("겹치는 항목이 있으므로 자동으로 해결하지 않습니다. "
              "코드 담당자가 어느 쪽을 남길지 정해야 합니다.")
    else:
        print("겹치는 항목이 없으므로 새 버전 내용을 그대로 두고 "
              "우리 항목만 끼워 넣으면 됩니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
