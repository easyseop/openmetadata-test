"""T33 — assurance-scope statement embedded in gate output (SRS §11, P0-5·P0-7).

The gate family is the "등록·재적용 완전성 게이트" (registration/reapply
completeness gate) — NOT a functional-correctness gate. To stop "완전성 통과"
from being read as "기능이 보장됨", every evidence card carries this explicit
guarantee / non-guarantee table, so the boundary travels with the verdict
instead of living only in a design doc.
"""
from __future__ import annotations

GATE_FAMILY = "등록·재적용 완전성 게이트"  # registration/reapply completeness gate

GUARANTEES = (
    "모든 upstream(core) 변경이 등록된 Customization-ID를 가진다 — 미등록 core "
    "변경을 차단(T30).",
    "재적용이 고정 SHA 소스에서 결정적으로 재현된다 — candidate tree == replay "
    "tree(T22).",
    "구현 범위(allowed) 밖 upstream 변경과 required 미반영(net)을 차단한다(T40).",
    "판정이 fail-closed이며 사람 승인·LLM 조언이 기계 판정을 격하하지 못한다"
    "(T13·T14·§7).",
)

NON_GUARANTEES = (
    "커스터마이징의 런타임 기능적 정확성 — 이는 기능 보장이 아니며 테스트·"
    "contract(T60/T61)가 별도로 담당한다.",
    "업스트림 의미 변경으로 인한 논리적 회귀의 부재 — 케이스 D/E는 감시(T93)·"
    "테스트로만 포착한다.",
    "빌드 산출물·컨테이너 이미지 레이어의 비트 재현 — T91 digest 승격이 담당한다.",
)


def scope_block() -> dict:
    """The guarantee/non-guarantee table to embed in gate output."""
    return {
        "gate_family": GATE_FAMILY,
        "guarantees": list(GUARANTEES),
        "non_guarantees": list(NON_GUARANTEES),
    }
