#!/usr/bin/env python3
"""Render the OM_TEMP commit-to-Manifest evidence guide."""

from __future__ import annotations

import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REGISTRATION = Path(__file__).resolve().parent
MANIFESTS = REGISTRATION / "manifests"
OUTPUT = ROOT / "docs/00-사용가이드/OM_TEMP_커밋별_Manifest_등록_가이드.md"
HTML_OUTPUT = ROOT / "docs/00-사용가이드/OM_TEMP_커밋별_Manifest_등록_가이드_미리보기.html"
ASSETS = "공유문서/assets/om-temp-manifest"


ITEMS = [
    {
        "id": "BANK-OM-001",
        "title": "기준코드(InstanceCode)",
        "commits": [
            (
                "4df83b311f1ec38156c9b992f34607b22224db85",
                "add InstanceCode customization",
                "48개",
                "001-instance-code-highlighted.png",
                "001-instance-code-original.png",
            )
        ],
        "reason": (
            "InstanceCode라는 새 데이터 유형을 정의하고, 저장·검색·API·화면 연결까지 "
            "한 번에 추가한 변경입니다. 파일은 여러 개지만 모두 InstanceCode 기능을 "
            "동작시키기 위한 한 묶음이므로 BANK-OM-001 하나로 관리합니다."
        ),
    },
    {
        "id": "BANK-OM-002",
        "title": "쿼리 리포트(QueryReport)",
        "commits": [
            (
                "68ebed4801715f0c30b8a1a614572183fa6097b8",
                "add QueryReport customization",
                "55개",
                "002-query-report-highlighted.png",
                "002-query-report-original.png",
            )
        ],
        "reason": (
            "QueryReport 데이터 유형, 저장소, API, 검색과 화면 연결을 함께 추가한 "
            "변경입니다. BANK-OM-001과 같은 공용 파일도 수정하지만, diff 안의 "
            "QUERY_REPORT 연결은 별도 업무 기능이므로 BANK-OM-002로 분리합니다."
        ),
    },
    {
        "id": "BANK-OM-003",
        "title": "데이터 검증 결과(Data Assertions)",
        "commits": [
            (
                "57ee1b3b23d644f13e0c1716f0810ddf962e5264",
                "add Data Assertions customization",
                "25개",
                "003-data-assertions-highlighted.png",
                "003-data-assertions-original.png",
            )
        ],
        "reason": (
            "데이터 검증 결과를 조회하는 전용 화면, API 호출, 경로와 메뉴를 함께 "
            "추가한 변경입니다. 이 화면 흐름을 한 기능으로 보고 BANK-OM-003으로 "
            "등록합니다."
        ),
    },
    {
        "id": "BANK-OM-004",
        "title": "은행 컬럼 확장 표시",
        "commits": [
            (
                "274f2b79b424e01537a7f2253c33aeecb43aaac4",
                "add bank column view customization",
                "33개",
                "004-bank-column-view-highlighted.png",
                "004-bank-column-view-original.png",
            )
        ],
        "reason": (
            "테이블 컬럼 화면에 은행용 표시 항목과 관련 타입·문구를 추가한 "
            "변경입니다. 화면에 보이는 결과와 이를 전달하는 타입 변경을 함께 "
            "BANK-OM-004로 관리합니다."
        ),
    },
    {
        "id": "BANK-OM-005",
        "title": "한글 입력 조합 보정",
        "commits": [
            (
                "d983f7c540d3fa1fe56ca91adef3f37374890f77",
                "fix Korean IME handling",
                "1개",
                "005-korean-ime-highlighted.png",
                "005-korean-ime-original.png",
            )
        ],
        "reason": (
            "SchemaEditor.tsx 한 파일에서 한글 조합 시작·종료 처리를 추가한 "
            "변경입니다. 변경 범위가 가장 작고 기능 경계도 분명해, 실제 diff "
            "전체가 Manifest 하나로 등록되는 대표 사례로 사용합니다."
        ),
        "full_diff": [
            "005-korean-ime-diff-part-1.png",
            "005-korean-ime-diff-part-2.png",
            "005-korean-ime-diff-part-3.png",
            "005-korean-ime-diff-part-4.png",
        ],
    },
    {
        "id": "BANK-OM-006",
        "title": "Sybase 연결 유형",
        "commits": [
            (
                "010750c514e9bbb7a765414ded3b161b1f5eb621",
                "add Sybase customization",
                "18개",
                "006-sybase-highlighted.png",
                "006-sybase-original.png",
            )
        ],
        "reason": (
            "Sybase 연결 스키마, 생성 타입, 아이콘과 연결 선택 로직을 함께 "
            "추가한 변경입니다. 하나의 DB 연결 유형을 완성하는 파일들을 "
            "BANK-OM-006으로 묶습니다."
        ),
    },
    {
        "id": "BANK-OM-007",
        "title": "Tibero 연결 유형",
        "commits": [
            (
                "62e39da8be65c3ff259802c1cd35f4b0c8baa333",
                "add Tibero customization",
                "8개",
                "007-tibero-initial-highlighted.png",
                "007-tibero-initial-original.png",
            ),
            (
                "7d19c8952612e77467b0a80d6287170d814f1de1",
                "complete Tibero service connection coverage",
                "2개",
                "007-tibero-followup-highlighted.png",
                "007-tibero-followup-original.png",
            ),
        ],
        "reason": (
            "두 커밋 모두 Tibero 연결 유형 하나를 완성합니다. Manifest의 "
            "changed_paths에는 두 커밋이 현재 1.13.0 버전에서 변경한 파일 "
            "10개를 모두 등록합니다. 어떤 파일이 첫 번째 또는 두 번째 커밋에서 "
            "추가됐는지는 Git 이력으로 확인합니다. Git 변경 기록은 두 개지만 "
            "업무 기능 ID와 Manifest는 BANK-OM-007 하나입니다."
        ),
    },
]


def manifest_text(customization_id: str) -> str:
    return (MANIFESTS / f"{customization_id}.yaml").read_text(encoding="utf-8").rstrip()


def render() -> str:
    lines = [
        "# OM_TEMP 검사 전 사전환경 설정 가이드",
        "",
        "> 대상 코드: `easyseop/OM_TEMP`의 `custom/om-1.13.0`  ",
        "> 검사 설정 위치: `easyseop/openmetadata-test/harness/registrations/om-temp-1.13.0/`",
        "",
        "> **이 페이지가 답하는 질문:** 검사 전에 어떤 관리자료를 준비하고, 실제 변경 파일을 "
        "어떤 BANK-OM 기능에 연결하는가?  ",
        "> **이 페이지가 답하지 않는 것:** 1.13.1 충돌과 검사 결과는 4번에서 설명합니다.  ",
        "> **다음 행동:** 등록자료와 로컬 repository를 연결한 뒤 4번 업그레이드 연습으로 이동합니다.",
        "",
        "> **우리 내부에서 만든 기준자료:** Manifest·Registry·Contract와 BANK-OM ID는 "
        "OpenMetadata 공식 설정이 아니라 `easyseop/openmetadata-test`가 행내 변경을 "
        "검사하기 위해 정의한 관리 자료입니다.",
        "",
        "## 이 자료가 필요한 이유",
        "",
        "이 문서는 전체 가이드에서 검사기 원리를 설명한 다음에 읽습니다. 다만 실제 "
        "작업 순서는 반대가 아닙니다. **검사기를 실행하기 전에 이 기준자료를 먼저 "
        "준비해야 합니다.** 검사기 설명을 먼저 읽는 이유는 각 자료가 어느 검사에 "
        "사용되는지 이해한 뒤 설정할 수 있게 하기 위해서입니다.",
        "",
        "검사기는 Git의 실제 코드만 읽는 것이 아니라, 어떤 BANK-OM을 검사하고 "
        "어떤 파일·동작을 정상으로 판단할지 정한 기준자료와 비교합니다. 이 자료는 "
        "검사 전에 준비할 Manifest와 검사 기준자료, 로컬 OM_TEMP 연결 방법을 "
        "실제 1.13.0 예시로 설명합니다.",
        "",
        "## 언제 만들고 언제 갱신하나",
        "",
        "| 구분 | 최초 커스터마이징 등록 | 공식 버전 업그레이드 | 매 검사 실행 |",
        "|---|---|---|---|",
        "| Manifest·Registry·Contract | 최초 작성 | 기존 자료를 복사해 새 코드 기준으로 검토·갱신 | 확정본을 읽음 |",
        "| 현재 공용 경로–BANK-OM 연결표 | 실제 diff의 중복 경로를 계산해 작성 | 새 버전 diff로 다시 계산·검토 | 확정본을 읽음 |",
        "| 과거 코드 경로–BANK-OM 연결표 | 기준 snapshot의 commit 이력에서 자동 생성 | 기준 snapshot SHA가 바뀔 때만 재생성 | 과거 코드 재구성 검사만 읽음 |",
        "| 전체 변경 목록 | Git에서 생성 | 새 버전 branch 사이에서 다시 생성 | 실제 Git diff와 비교 |",
        "| Patch-lock | patch-replay를 쓸 때만 작성 | 재적용 커밋이 바뀌면 새 리비전 작성 | 선택한 전략에서만 읽음 |",
        "",
        "따라서 이 자료들은 검사 때마다 버리는 임시 파일이 아닙니다. 최초 등록자료는 "
        "계속 관리하고, 버전에 따라 달라지는 Git SHA·경로 목록만 새 버전 기준으로 "
        "다시 생성하거나 갱신합니다.",
        "",
        "## 먼저 구분할 두 식별값",
        "",
        "| 이름 | 의미 | 이 문서에서의 예 |",
        "|---|---|---|",
        "| BANK-OM ID | 사람이 발급하는 업무 기능 번호 | `BANK-OM-005` |",
        "| Git 변경 기록 번호(commit SHA) | Git이 한 번 저장한 코드 변경에 자동 부여하는 값 | `d983f7c...` |",
        "",
        "Manifest는 **BANK-OM ID마다 한 파일**을 최초 등록 때 만듭니다. 같은 기능을 "
        "새 공식 버전에 맞추거나 후속 보완해도 새 ID를 만들지 않습니다. 새 버전 등록 "
        "폴더에 기존 Manifest를 복사한 뒤 실제 경로·watch·Contract 변경만 갱신합니다. "
        "BANK-OM-007처럼 Git 변경 기록 번호는 여러 개가 될 수 있지만 Manifest는 하나입니다.",
        "",
        "BANK-OM-007의 실제 예에서는 최초 구현 SHA `62e39da8...`가 8개 파일을 "
        "변경했고 후속 보완 SHA `7d19c895...`가 2개 파일을 추가했습니다. 두 SHA를 "
        "가장 최근 SHA 하나로 바꾸지 않습니다. 각 SHA가 서로 다른 변경 파일의 근거이기 "
        "때문입니다. 반면 최종 검사는 두 변경을 모두 포함한 custom branch의 마지막 "
        "SHA 하나를 Candidate lock에 기록합니다.",
        "",
        "```text",
        "기능 변경 이력: BANK-OM-007 → 62e39da8... + 7d19c895...",
        "현재 파일 범위: changed_paths 10개",
        "최종 검사 대상: custom/om-1.13.0 HEAD의 SHA 1개",
        "```",
        "",
        "## 사전환경 설정 순서",
        "",
        "1. **Manifest 등록** — 커밋별 실제 변경 파일을 BANK-OM ID에 연결합니다.",
        "2. **검사 기준자료 등록** — Registry·Contract·공용 파일·전체 변경 목록을 준비합니다.",
        "3. **로컬 검사 대상 연결** — 검사기가 읽을 OM_TEMP repository와 기준 SHA를 확인합니다.",
        "",
        "강조 캡처는 위치를 빠르게 찾기 위한 **설명용 사본**입니다. "
        "GitHub 화면 자체를 확인해야 할 때는 같은 항목의 **원본 캡처** 또는 "
        "GitHub commit 링크를 사용합니다.",
        "",
        "## 1. Manifest 등록",
        "",
        "각 BANK-OM 제목을 펼치면 실제 GitHub commit, 기능 단위로 묶은 이유, "
        "등록된 Manifest 전체를 확인할 수 있습니다.",
        "",
    ]

    for item in ITEMS:
        customization_id = item["id"]
        lines.extend(
            [
                "<details>",
                f"<summary><strong>{customization_id} · {item['title']}</strong></summary>",
                "",
            ]
        )
        for index, commit in enumerate(item["commits"], start=1):
            sha, title, file_count, highlighted, original = commit
            label = "최초 커밋" if len(item["commits"]) > 1 and index == 1 else ""
            if len(item["commits"]) > 1 and index == 2:
                label = "후속 보완 커밋"
            heading = f"### {label}" if label else "### 실제 GitHub 커밋"
            lines.extend(
                [
                    heading,
                    "",
                    f"- Git commit SHA: `{sha}`",
                    f"- 커밋 제목: `{title}`",
                    f"- 이 커밋에서 변경한 파일: {file_count}",
                    f"- [GitHub에서 실제 커밋 열기](https://github.com/easyseop/OM_TEMP/commit/{sha})",
                    "",
                    f"![{customization_id} {label or '커밋'} 강조 캡처]"
                    f"({ASSETS}/commit-messages/{highlighted})",
                    "",
                    "<details>",
                    "<summary>강조 표시가 없는 원본 캡처 보기</summary>",
                    "",
                    f"![{customization_id} {label or '커밋'} 원본 캡처]"
                    f"({ASSETS}/commit-messages/{original})",
                    "",
                    "</details>",
                    "",
                ]
            )

        lines.extend(
            [
                "### 왜 하나의 BANK-OM 기능으로 보았나",
                "",
                item["reason"],
                "",
            ]
        )

        if item.get("full_diff"):
            lines.extend(
                [
                    "<details>",
                    "<summary><strong>대표 사례: 변경 코드 전체 보기</strong></summary>",
                    "",
                    "이 커밋의 변경은 `SchemaEditor.tsx` 한 파일뿐입니다. 아래 네 장은 "
                    "한 GitHub diff 화면을 위에서 아래 순서로 나눈 것으로, "
                    "초록색 줄은 추가 코드이고 빨간색 줄은 삭제 코드입니다.",
                    "",
                ]
            )
            for index, image in enumerate(item["full_diff"], start=1):
                lines.extend(
                    [
                        f"#### 전체 diff {index}/4",
                        "",
                        f"![BANK-OM-005 전체 diff {index}/4]"
                        f"({ASSETS}/bank-om-005-full-diff/{image})",
                        "",
                    ]
                )
            lines.extend(
                [
                    "이 전체 diff에서 바뀐 파일 경로는 하나이므로 Manifest의 "
                    "`changed_paths`도 한 경로입니다. 같은 파일이 한글 입력 "
                    "보정의 핵심 구현이므로 `required_changed_paths`에도 같은 경로를 "
                    "등록했습니다.",
                    "",
                    "</details>",
                    "",
                ]
            )

        lines.extend(
            [
                "<details>",
                f"<summary><strong>{customization_id} Manifest 등록본 전체 보기</strong></summary>",
                "",
                "```yaml",
                manifest_text(customization_id),
                "```",
                "",
                "</details>",
                "",
                "</details>",
                "",
            ]
        )

    lines.extend(
        [
            "### Manifest 세 목록을 읽는 기준",
            "",
            "| 항목 | 현재 등록 기준 | 검사에서 쓰는 방식 |",
            "|---|---|---|",
            "| `changed_paths` | 현재 OpenMetadata 버전에서 같은 BANK-OM ID의 모든 커밋이 실제 변경한 파일 | 목록 밖 파일을 같은 ID로 변경하면 차단합니다. 목록 안 일반 파일이 최종 코드에서 공식 원본과 같아지면 담당자 검토를 요구합니다. |",
            "| `required_changed_paths` | 기능이 적용됐음을 판단하는 핵심 구현 파일 | 파일이 없거나 공식 원본과 같아지면 기능이 빠진 것으로 보고 차단 |",
            "| `upgrade_watch.paths` | 공식 버전 변경 비교 검사가 확인할 경로 | 공식 새 버전에서 해당 경로가 바뀌면 자동 통과하지 않고 재검토를 요구 |",
            "",
            "공식 버전 변경 비교 검사(검사기 내부 이름 `T42`)는 이전 공식 버전과 "
            "새 공식 버전 사이에서 지정 경로가 바뀌었는지 확인합니다. 준비도구는 "
            "`changed_paths` 중 공식 OpenMetadata 포크 브랜치에도 존재하는 경로만 "
            "`upgrade_watch.paths` 후보로 제안합니다. 행내 전용 파일과 직접 수정하지 "
            "않은 의존 경로는 담당자가 기능 관계를 확인해 추가합니다. 따라서 watch에 "
            "있다고 해서 그 파일을 해당 커밋이 반드시 수정했다는 뜻은 아닙니다.",
            "",
            "[Manifest의 `assurance`·`series`와 나머지 관리파일 필드까지 보는 전체 필드 사전]"
            "(OM_TEMP_관리파일_필드_사전_미리보기.html)",
            "",
            "## 2. 검사 기준자료 등록",
            "",
            "아래 자료는 모두 `openmetadata-test`에 보관합니다. Git이 자동으로 "
            "만들 수 있는 값과 사람이 결정해야 하는 기준을 구분해 등록합니다. "
            "OM_TEMP 1.13.0의 실제 자료를 이미 생성했으며, 아래에는 각 자료의 "
            "역할과 실제 등록 결과를 함께 표시합니다.",
            "",
            "<details>",
            "<summary><strong>2-1. Registry · 검사할 BANK-OM 목록과 연결정보</strong></summary>",
            "",
            "**의미:** 어떤 BANK-OM이 활성 상태이고 어느 Manifest·Contract를 읽을지 "
            "검사기에 알려주는 목록입니다.",
            "",
            "**생성·갱신 시점:** 첫 BANK-OM 등록 때 만들고, ID 추가·폐기·중요도 변경 "
            "또는 검사 대상 버전과 SHA가 바뀔 때 갱신합니다. 임시 파일이 아닙니다.",
            "",
            "**이번 등록 결과:** `customization-registry.yaml`에 BANK-OM-001~007 "
            "7개를 등록했습니다. 기능 담당자는 아직 정하지 않았으므로 `owner_status: "
            "pending`이며, 이 상태는 배포 승인 전 반드시 보완해야 합니다.",
            "",
            "```yaml",
            "entries:",
            "  - customization_id: BANK-OM-005",
            "    title: 한글 입력 조합 보정",
            "    status: active",
            "    criticality: medium",
            "    manifest: manifests/BANK-OM-005.yaml",
            "    contracts: [CONTRACT-KOREAN-IME]",
            "```",
            "",
            "**실제 사용:** 검사기는 이 항목을 읽고 BANK-OM-005 Manifest와 "
            "CONTRACT-KOREAN-IME가 모두 존재하고 서로 같은 ID를 가리키는지 확인합니다. "
            "연결 파일이 없거나 ID가 서로 다르면 입력 묶음을 읽을 수 없어 검사를 "
            "시작하지 않습니다.",
            "",
            "</details>",
            "",
            "<details>",
            "<summary><strong>2-2. Contracts · 기능이 정상이라는 동작 기준</strong></summary>",
            "",
            "**의미:** 파일이 남아 있다는 사실을 넘어 기능이 실제로 어떻게 동작해야 "
            "정상인지 정의합니다. Git만으로는 업무 정상 조건을 정할 수 없으므로 사람이 "
            "기능 담당자와 합의해 작성합니다.",
            "",
            "**생성·갱신 시점:** 최초 기능 등록 때 만들고, OpenMetadata 버전이 바뀌어도 "
            "업무 요구가 같으면 재사용합니다. 기능 기준이나 test가 바뀔 때만 갱신합니다.",
            "",
            "**이번 등록 결과:** `contracts.yaml`에 Contract 7개와 필수 Python pytest "
            "9개를 연결했습니다.",
            "",
            "```yaml",
            "- id: CONTRACT-KOREAN-IME",
            "  invariant: 한글 입력 중 자모가 중복·역전·소실되지 않는다.",
            "  required_tests:",
            "    - tests/bank/contracts/test_korean_ime.py::test_hangul_composition_roundtrip",
            "  customization_ids: [BANK-OM-005]",
            "```",
            "",
            "**실제 사용:** 필수 테스트 코드 존재 검증은 `required_tests`에 적은 "
            "`파일 경로::test 함수명`이 검사 저장소에 실제 Python pytest 코드로 "
            "있는지 확인합니다. Java JUnit·TypeScript test 확인은 추가 개발 "
            "대상입니다.",
            "",
            "**필수 여부와 검사 결과:** 현재 전체 소스 검사에서는 `active` 상태의 "
            "BANK-OM마다 Contract가 하나 이상 있어야 하고, 각 Contract의 "
            "`required_tests`에도 test가 하나 이상 있어야 합니다. 따라서 선택사항이 "
            "아닙니다. Contract 연결, test 경로 또는 test 함수가 없으면 `BLOCK`입니다. "
            "다만 이 검증의 `PASS`는 test 코드가 존재한다는 뜻일 뿐이며, test 실행 "
            "성공은 후속 실행 검사에서 별도로 확인합니다.",
            "",
            "</details>",
            "",
            "<details>",
            "<summary><strong>2-3. 현재 공용 경로–BANK-OM 연결표 · 한 파일을 함께 변경한 ID</strong></summary>",
            "",
            "**의미:** 현재 버전에서 여러 BANK-OM이 같은 파일을 정상적으로 변경했다는 "
            "사실과 실제 소유 ID를 기록합니다.",
            "",
            "**생성·갱신 시점:** Manifest들의 실제 변경 경로를 비교해 중복 경로를 "
            "자동 제안한 뒤, 각 commit diff에서 ID별 코드가 실제로 있는지 사람이 "
            "확인합니다. 업그레이드 버전마다 다시 계산·검토합니다.",
            "",
            "**이번 등록 결과:** `shared-path-owners.yaml`에 37개 공용 경로를 "
            "등록했습니다.",
            "",
            "```yaml",
            "openmetadata-service/src/main/java/org/openmetadata/service/Entity.java:",
            "  - BANK-OM-001  # INSTANCE_CODE",
            "  - BANK-OM-002  # QUERY_REPORT",
            "",
            "openmetadata-spec/src/main/resources/json/schema/entity/services/databaseService.json:",
            "  - BANK-OM-006  # Sybase",
            "  - BANK-OM-007  # Tibero",
            "```",
            "",
            "**실제 사용:** 현재 버전 범위 검사는 공용 파일을 한 ID의 단독 소유로 "
            "잘못 판단하지 않고, 등록된 모든 ID가 해당 경로를 실제로 변경했는지 "
            "확인합니다. 실제 중복 소유와 목록이 다르면 등록자료 검사가 실패합니다.",
            "",
            "</details>",
            "",
            "<details>",
            "<summary><strong>2-4. 과거 코드 경로–BANK-OM 연결표 · 재구성 시점 전용</strong></summary>",
            "",
            "**의미:** 최초 등록에 사용한 과거 행내 code snapshot에서 각 변경 파일이 "
            "어느 BANK-OM 기능에 속했는지 기록합니다. 현재 Manifest 범위를 나누는 "
            "자료가 아니라 T25-R 과거 코드 재구성 검사 전용 자동 생성 자료입니다.",
            "",
            "**생성·갱신 시점:** 기준 source snapshot SHA까지의 commit 이력을 읽어 "
            "자동 생성합니다. 기준 SHA가 바뀔 때만 다시 생성하며, 이후 후속 commit이 "
            "생겼다는 이유로 과거 기록을 고치지 않습니다.",
            "",
            "```yaml",
            "openmetadata-ui/.../serviceConnection.ts:",
            "  - BANK-OM-006",
            "```",
            "",
            "**실제 사용:** 최초 snapshot에서는 BANK-OM-006만 위 파일을 수정했습니다. "
            "이후 BANK-OM-007 후속 commit도 같은 파일을 수정했으므로 현재 버전의 "
            "`shared-path-owners.yaml`에는 006과 007이 함께 표시됩니다. 두 파일은 "
            "서로 다른 시점을 설명하므로 값이 달라도 오류가 아닙니다.",
            "",
            "</details>",
            "",
            "<details>",
            "<summary><strong>2-5. 전체 변경 목록 · OpenMetadata 포크와 커스텀 브랜치 사이의 111개 경로</strong></summary>",
            "",
            "**의미:** `fork/om-1.13.0`과 `custom/om-1.13.0` 사이에서 최종적으로 "
            "달라진 모든 파일 경로입니다.",
            "",
            "**생성·갱신 시점:** 검사 대상 commit이 확정된 뒤 Git으로 생성하며, "
            "업그레이드 버전마다 다시 생성합니다. 사람이 111개를 직접 작성하지 않습니다.",
            "",
            "**이번 등록 결과:** 공식 1.13.0과 BANK-OM-007 최초 커밋까지의 diff를 "
            "기준으로 `source-diff-paths.txt`에 111개 경로를 생성했습니다. "
            "BANK-OM-007 후속 커밋은 이미 목록에 있던 두 공용 파일을 다시 수정했으므로 "
            "최종 경로 수도 111개입니다.",
            "",
            "```text",
            "openmetadata-service/src/main/java/org/openmetadata/service/Entity.java",
            "openmetadata-ui/src/main/resources/ui/src/components/Database/SchemaEditor/SchemaEditor.tsx",
            "openmetadata-spec/src/main/resources/json/schema/entity/services/connections/database/tiberoConnection.json",
            "```",
            "",
            "**실제 사용:** 실제 전체 변경 111개와 모든 Manifest의 변경 범위를 "
            "양방향으로 비교합니다. 어느 Manifest에도 등록되지 않은 실제 변경이나, "
            "Manifest에만 있고 실제 diff에는 없는 경로가 있으면 등록자료 검증이 "
            "실패합니다.",
            "",
            "</details>",
            "",
            "<details>",
            "<summary><strong>2-6. Patch-lock · 커밋 재적용을 선택할 때만 사용하는 순서표</strong></summary>",
            "",
            "**의미:** patch-replay 방식으로 커스터마이징 커밋을 다시 적용할 때 사용할 "
            "정확한 SHA와 순서를 고정합니다.",
            "",
            "**생성·갱신 시점:** 모든 전략의 필수 사전자료가 아닙니다. vendor-merge "
            "소스 검사에서는 선택사항이며, patch-replay·복구·재현 시연을 할 때 "
            "커밋 순서가 확정된 후 만듭니다.",
            "",
            "```yaml",
            "patch_series:",
            "  - id: BANK-OM-007",
            "    revision: 1",
            "    source_commits:",
            "      - 62e39da8be65c3ff259802c1cd35f4b0c8baa333",
            "      - 7d19c8952612e77467b0a80d6287170d814f1de1",
            "```",
            "",
            "**실제 사용:** 재적용 도구는 62e39da 다음에 7d19c89를 적용합니다. "
            "잠금에 없는 SHA나 순서 변경은 동일한 재현으로 인정하지 않습니다. 설계상 "
            "OM_TEMP 첫 vendor-merge 소스 검사에서는 Patch-lock 부재만으로 "
            "차단하지 않습니다.",
            "",
            "</details>",
            "",
            "<details>",
            "<summary><strong>2-7. 실제 생성 명령과 사전검증 결과</strong></summary>",
            "",
            "일반 운영에서는 준비도구가 Git 이력과 기존 등록자료를 비교해 변경안을 "
            "만듭니다. `plan`은 실제 등록자료를 바꾸지 않으며, 담당자가 같은 변경안을 "
            "승인한 뒤 `apply`가 변경 대상 Manifest와 파생 등록자료를 반영합니다. "
            "Registry 변경이 필요한 경우에만 제안에 포함되며 Contract는 사람이 직접 "
            "작성합니다.",
            "",
            "```bash",
            "PYTHONPATH=harness ./.venv/bin/python harness/prepare_registration.py plan \\",
            "  --repo /path/to/OM_TEMP \\",
            "  --registration harness/registrations/om-temp-1.13.0 \\",
            "  --patch-ref origin/fork/om-1.13.0 \\",
            "  --custom-ref origin/custom/om-1.13.0 \\",
            "  --product-version 1.13.0 \\",
            "  --output harness/preparation-plans/om-temp-1.13.0-YYYYMMDD",
            "",
            "PYTHONPATH=harness ./.venv/bin/python harness/prepare_registration.py \\",
            "  approval-template \\",
            "  --proposal harness/preparation-plans/om-temp-1.13.0-YYYYMMDD/proposal.yaml \\",
            "  --output /approved/location/registration-approval.yaml",
            "",
            "# 담당자가 proposal과 질문을 검토하고 승인서를 작성한 뒤 실행",
            "PYTHONPATH=harness ./.venv/bin/python harness/prepare_registration.py apply \\",
            "  --repo /path/to/OM_TEMP \\",
            "  --registration harness/registrations/om-temp-1.13.0 \\",
            "  --proposal harness/preparation-plans/om-temp-1.13.0-YYYYMMDD/proposal.yaml \\",
            "  --approval /approved/location/registration-approval.yaml \\",
            "  --result /approved/location/registration-apply-result.json",
            "",
            "./.venv/bin/python \\",
            "  harness/registrations/om-temp-1.13.0/validate_registration_bundle.py \\",
            "  --repo ../om-temp-1.13.0-custom \\",
            "  --output harness/registrations/om-temp-1.13.0/registration-validation-results.json",
            "```",
            "",
            "| 확인 항목 | 실제 결과 | 무엇을 확인했나 |",
            "|---|---|---|",
            "| Manifest 구조와 작성 규칙 | PASS · 7개 | 필수 항목과 경로 규칙이 맞는지 |",
            "| Registry·Manifest·Contract 연결 | PASS · 7개 ID | 세 자료가 같은 BANK-OM을 가리키는지 |",
            "| Git 전체 변경 목록 | PASS · 111개 경로 | 저장한 목록과 실제 Git diff가 같은지 |",
            "| 현재 공용 경로–BANK-OM 연결표 | PASS · 37개 경로 | 중복 경로의 모든 BANK-OM이 등록됐는지 |",
            "| 필수 테스트 코드 존재 | PASS · 9개 | 등록한 Python test 파일과 함수가 실제로 있는지 |",
            "",
            "이 PASS는 **검사 입력자료가 서로 일치한다**는 뜻입니다. 아직 test 실행 "
            "성공이나 배포 승인을 뜻하지 않습니다.",
            "",
            "</details>",
            "",
            "## 3. 로컬 검사 대상 연결",
            "",
            "<details>",
            "<summary><strong>3-1. OM_TEMP repository 준비와 branch 확인</strong></summary>",
            "",
            "**의미:** 검사기는 GitHub 화면을 원격으로 읽는 것이 아니라 컴퓨터에 "
            "내려받은 OM_TEMP 저장소의 변경 기록·변경 파일·최종 코드를 직접 검사합니다.",
            "",
            "**최초 준비:** 다른 노트북에서는 한 번 clone합니다. 이미 받은 뒤에는 "
            "`git fetch`로 갱신합니다. 현재 노트북에는 "
            "`work/om-temp-1.13.0-custom`에 OM_TEMP 원격 branch도 fetch되어 있으므로 "
            "다시 clone하지 않습니다.",
            "",
            "```bash",
            "git clone https://github.com/easyseop/OM_TEMP.git",
            "cd OM_TEMP",
            "git fetch origin fork/om-1.13.0 custom/om-1.13.0",
            "git rev-parse origin/fork/om-1.13.0",
            "git rev-parse origin/custom/om-1.13.0",
            "```",
            "",
            "**검사 연결:** 검사 실행기의 `--repo`에 이 로컬 경로를 전달합니다. "
            "검사기는 여기서 BANK-OM 변경 기록, Customization-ID, 111개 변경 경로와 최종 "
            "파일 내용을 읽습니다.",
            "",
            "</details>",
            "",
            "<details>",
            "<summary><strong>3-2. 공식 1.13.0과 OM_TEMP 공식 코드 기준 연결 주의사항</strong></summary>",
            "",
            "OM_TEMP는 공식 OpenMetadata의 과거 변경 이력 전체를 가져오지 않고, 공식 "
            "1.13.0 파일만 새로운 Git 변경 기록으로 저장했습니다. 따라서 파일 내용이 "
            "같아도 두 Git 번호는 다릅니다.",
            "",
            "```text",
            "공식 OpenMetadata 1.13.0 Git 번호: f329dd4a...",
            "OM_TEMP 과거 공식 코드 브랜치 Git 번호: 2f4f3560...",
            "두 버전의 파일 내용이 같음을 확인하는 값: da56c24d...",
            "```",
            "",
            "원격 OM_TEMP의 변경 이력에는 “공식 1.13.0에서 시작했다”는 연결 기록이 없어 "
            "그대로는 공식 출발점 검사를 통과할 수 없습니다. 그래서 공식 `f329dd4a...`에서 시작해 같은 "
            "BANK-OM 변경을 순서대로 적용한 로컬 검사 branch를 만들었습니다. 로컬 "
            "검사 대상 Git 번호 `3a2811cf...`의 최종 파일 내용은 원격 custom "
            "`7d19c895...`와 같습니다. 즉, 코드는 바꾸지 않고 공식 1.13.0에서 "
            "시작했다는 이력만 확인할 수 있는 상태로 만들어 검사했습니다.",
            "",
            "</details>",
            "",
            "## 4. 실제 소스 검사 실행",
            "",
            "```bash",
            "./.venv/bin/python harness/run_source_candidate_gates.py \\",
            "  --repo ../om-temp-1.13.0-custom \\",
            "  --harness harness \\",
            "  --registration harness/registrations/om-temp-1.13.0 \\",
            "  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\",
            "  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \\",
            "  --output harness/registrations/om-temp-1.13.0/source-gate-results.json",
            "```",
            "",
            "| 검사명 | 무엇을 확인했나 | 실제 결과 |",
            "|---|---|---|",
            "| 공식 기준 이력 포함 | 공식 1.13.0에서 시작한 후보인지 | PASS |",
            "| 커스터마이징 생존 | 7개 BANK-OM의 핵심 파일과 Contract 연결이 남았는지 | PASS |",
            "| 필수 테스트 코드 존재 | 9개 Python test 파일·함수가 실제로 있는지 | PASS |",
            "| 커밋 작성 규칙 | 각 공식 코드 변경 커밋에 BANK-OM ID가 하나씩 있는지 | PASS |",
            "| ID 연결 규칙 | 미등록 ID나 잘못 나뉜 후속 커밋이 없는지 | PASS |",
            "| 변경 범위 | 각 커밋이 자기 Manifest에 등록된 파일만 바꿨는지 | PASS |",
            "| 민감 경로 | 보안·설정·DB 변경 경로의 별도 정책을 위반하지 않았는지 | PASS |",
            "| 커밋별 실제 경로 일치 | ID별 실제 변경 파일과 Manifest 목록이 정확히 같은지 | PASS |",
            "",
            "이번 결과는 **1.13.0 코드 구조와 변경 이력에 대한 소스 검사 PASS**입니다. "
            "OpenMetadata 전체 build, Contract test 실제 실행, 담당자 지정, 1.13.1 "
            "업그레이드와 운영 배포 승인은 아직 별도 단계입니다.",
            "",
            "## 현재 상태",
            "",
            "- BANK-OM-001~007 Manifest 등록본 7개 생성 완료",
            "- 실제 Git commit의 변경 파일 목록을 Manifest에 반영 완료",
            "- 현재 Manifest 스키마 및 기본 의미 검사 7개 통과",
            "- Registry 7개, Contract 7개·필수 test 9개, 공용 경로 37개, 전체 경로 111개 생성 완료",
            "- 공식 1.13.0 이력을 보존한 로컬 검사 branch 구성 완료",
            "- 소스 검사 8종 PASS 및 JSON 결과 저장 완료",
            "- 기능 담당자(owner)는 아직 미지정이므로 배포 준비 상태는 완료가 아님",
            "- 이 1.13.0 등록 결과에는 전체 build, 업무 동작 test와 1.13.1 업그레이드 결과가 포함되지 않음",
            "- 따라서 이 페이지의 결론은 **1.13.0 소스 검사 통과**이며 배포 승인 결과가 아님",
            "",
        ]
    )
    return "\n".join(lines)


def render_html() -> str:
    pagination = """
  <nav class="guide-pagination" aria-label="가이드 페이지 이동">
    <a class="guide-page-link" href="공유문서/openmetadata-phase2-verifier-table-preview.html" target="_top">
      <small>← 이전 가이드</small>
      <strong>검사기 원리</strong>
    </a>
    <div class="guide-page-current">
      <small>전체 5개 중</small>
      <strong>3 · 검사 전 사전환경 설정</strong>
    </div>
    <a class="guide-page-link is-next" href="OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드_미리보기.html" target="_top">
      <small>다음 가이드 →</small>
      <strong>OM_TEMP 업그레이드 연습</strong>
    </a>
  </nav>
    """.strip()
    sections = []
    for item in ITEMS:
        commit_blocks = []
        for index, commit in enumerate(item["commits"], start=1):
            sha, title, file_count, highlighted, original = commit
            label = "실제 GitHub 커밋"
            if len(item["commits"]) > 1:
                label = "최초 커밋" if index == 1 else "후속 보완 커밋"
            commit_blocks.append(
                f"""
                <section class="commit">
                  <h3>{label}</h3>
                  <dl>
                    <div><dt>Git commit SHA</dt><dd><code>{sha}</code></dd></div>
                    <div><dt>커밋 제목</dt><dd><code>{html.escape(title)}</code></dd></div>
                    <div><dt>변경 파일</dt><dd>{file_count}</dd></div>
                  </dl>
                  <a class="github" href="https://github.com/easyseop/OM_TEMP/commit/{sha}">GitHub에서 실제 커밋 열기</a>
                  <img src="{ASSETS}/commit-messages/{highlighted}" alt="{item['id']} 강조 캡처">
                  <details class="sub">
                    <summary>강조 표시가 없는 원본 캡처</summary>
                    <img src="{ASSETS}/commit-messages/{original}" alt="{item['id']} 원본 캡처">
                  </details>
                </section>
                """
            )

        full_diff = ""
        if item.get("full_diff"):
            images = "".join(
                f'<figure><figcaption>전체 diff {index}/4</figcaption>'
                f'<img src="{ASSETS}/bank-om-005-full-diff/{image}" '
                f'alt="BANK-OM-005 전체 diff {index}/4"></figure>'
                for index, image in enumerate(item["full_diff"], start=1)
            )
            full_diff = f"""
              <details class="sub">
                <summary>대표 사례: 변경 코드 전체 보기</summary>
                <p><code>SchemaEditor.tsx</code> 한 파일의 GitHub diff 전체입니다.
                초록색은 추가 코드, 빨간색은 삭제 코드입니다.</p>
                <div class="diff-grid">{images}</div>
                <p>변경 파일이 하나이므로 Manifest의 <code>changed_paths</code>도
                한 경로입니다. 같은 경로를 핵심 구현인
                <code>required_changed_paths</code>로 등록했습니다.</p>
              </details>
            """

        manifest = html.escape(manifest_text(item["id"]))
        sections.append(
            f"""
            <details class="feature">
              <summary><span>{item['id']}</span><strong>{html.escape(item['title'])}</strong></summary>
              <div class="feature-body">
                {''.join(commit_blocks)}
                <section class="reason">
                  <h3>왜 하나의 BANK-OM 기능으로 보았나</h3>
                  <p>{html.escape(item['reason'])}</p>
                </section>
                {full_diff}
                <details class="sub manifest">
                  <summary>{item['id']} Manifest 등록본 전체 보기</summary>
                  <pre><code>{manifest}</code></pre>
                </details>
              </div>
            </details>
            """
        )

    reference_sections = """
      <details class="reference">
        <summary><span>2-1</span><strong>Registry</strong><small>검사할 BANK-OM과 연결정보</small></summary>
        <div class="reference-body">
          <div class="explain-grid">
            <p><b>의미</b>활성 BANK-OM이 어느 Manifest와 Contract를 사용할지 알려주는 목록입니다.</p>
            <p><b>만드는 시점</b>첫 기능 등록 때 만들고, ID·상태·중요도·대상 SHA가 바뀔 때 갱신합니다.</p>
            <p><b>이번 등록</b><code>customization-registry.yaml</code>에 BANK-OM-001~007 7개를 등록했습니다.</p>
            <p><b>남은 확인</b>담당자는 아직 <code>pending</code>입니다. 담당자를 지정하기 전에는 배포 승인 상태가 아닙니다.</p>
          </div>
          <pre><code>entries:
  - customization_id: BANK-OM-005
    title: 한글 입력 조합 보정
    status: active
    criticality: medium
    manifest: manifests/BANK-OM-005.yaml
    contracts: [CONTRACT-KOREAN-IME]</code></pre>
        </div>
      </details>

      <details class="reference">
        <summary><span>2-2</span><strong>Contracts</strong><small>기능이 정상이라는 동작 기준</small></summary>
        <div class="reference-body">
          <div class="explain-grid">
            <p><b>의미</b>파일 존재만으로 알 수 없는 실제 업무 동작의 정상 조건입니다.</p>
            <p><b>만드는 시점</b>최초 기능 등록 때 담당자가 정하고, 정상 조건이나 test가 바뀔 때 갱신합니다.</p>
            <p><b>실제 사용</b>필수 테스트 코드 존재 검증이 <code>파일 경로::test 함수명</code>을 찾아 실제 Python pytest 코드인지 확인합니다.</p>
            <p><b>필수 여부와 결과</b><code>active</code> BANK-OM에는 Contract와 필수 test가 각각 하나 이상 필요합니다. 이번에는 Contract 7개와 test 9개가 모두 <em class="pass">PASS</em>했습니다. PASS는 test 코드 존재만 뜻하며 실행 성공은 후속 검사에서 확인합니다.</p>
          </div>
          <pre><code>- id: CONTRACT-KOREAN-IME
  invariant: 한글 입력 중 자모가 중복·역전·소실되지 않는다.
  required_tests:
    - tests/bank/contracts/test_korean_ime.py::test_hangul_composition_roundtrip
  customization_ids: [BANK-OM-005]</code></pre>
        </div>
      </details>

      <details class="reference">
        <summary><span>2-3</span><strong>현재 공용 경로–BANK-OM 연결표</strong><small>같은 파일을 변경한 BANK-OM 목록</small></summary>
        <div class="reference-body">
          <div class="explain-grid">
            <p><b>의미</b>여러 기능이 같은 공식 파일을 정상적으로 함께 변경했음을 기록합니다.</p>
            <p><b>만드는 시점</b>Manifest 경로의 중복을 자동 추출한 뒤 사람이 실제 diff를 확인하고, 버전마다 다시 계산합니다.</p>
            <p><b>실제 사용</b>Entity.java를 BANK-OM-001만의 파일로 잘못 판단하지 않고 001·002 공동 변경으로 검사합니다.</p>
            <p><b>이번 등록</b><code>shared-path-owners.yaml</code>에 공용 경로 37개를 등록했고 실제 중복 목록과 일치해 <em class="pass">PASS</em>했습니다.</p>
          </div>
          <pre><code>Entity.java:
  - BANK-OM-001  # INSTANCE_CODE
  - BANK-OM-002  # QUERY_REPORT

databaseService.json:
  - BANK-OM-006  # Sybase
  - BANK-OM-007  # Tibero</code></pre>
        </div>
      </details>

      <details class="reference">
        <summary><span>2-4</span><strong>전체 변경 목록</strong><small>patch와 custom 사이의 111개 경로</small></summary>
        <div class="reference-body">
          <div class="explain-grid">
            <p><b>의미</b>두 branch 사이에서 최종적으로 달라진 모든 파일 경로입니다.</p>
            <p><b>만드는 시점</b>검사 대상 commit이 확정된 뒤 Git으로 만들며, 업그레이드 버전마다 다시 생성합니다.</p>
            <p><b>실제 사용</b>실제 111개 경로와 7개 Manifest가 설명하는 경로를 양방향으로 비교합니다.</p>
            <p><b>이번 등록</b><code>source-diff-paths.txt</code>의 111개 경로가 실제 Git diff와 일치해 <em class="pass">PASS</em>했습니다.</p>
          </div>
          <p class="note">BANK-OM-007 후속 커밋은 이미 목록에 있던 공용 파일 두 개를 다시 수정했습니다. 그래서 후속 수정이 반영돼도 최종 경로 수는 111개입니다.</p>
        </div>
      </details>

      <details class="reference optional">
        <summary><span>2-5</span><strong>Patch-lock</strong><small>커밋 재적용 방식을 쓸 때만 필요</small></summary>
        <div class="reference-body">
          <div class="explain-grid">
            <p><b>의미</b>patch-replay로 커스터마이징을 다시 적용할 때 사용할 SHA와 순서입니다.</p>
            <p><b>만드는 시점</b>vendor-merge 소스 검사의 필수자료가 아닙니다. 재적용·복구·재현을 선택할 때만 만듭니다.</p>
            <p><b>실제 사용</b>BANK-OM-007의 최초 commit 다음에 후속 보완 commit을 적용하도록 고정합니다.</p>
            <p><b>검사 결과</b>patch-replay에서는 잠금에 없는 SHA나 순서 변경을 동일한 재현으로 인정하지 않습니다. 설계상 첫 vendor-merge 소스 검사는 파일이 없어도 차단하지 않습니다.</p>
          </div>
          <pre><code>patch_series:
  - id: BANK-OM-007
    revision: 1
    source_commits:
      - 62e39da...
      - 7d19c89...</code></pre>
        </div>
      </details>

      <details class="reference">
        <summary><span>2-6</span><strong>실제 생성·사전검증</strong><small>자동 생성 뒤 사람이 검토</small></summary>
        <div class="reference-body">
          <p><code>plan</code>은 Git과 기존 등록자료를 비교해 읽기 전용 변경안을 만듭니다. 담당자가 같은 변경안을 승인한 뒤 <code>apply</code>가 Manifest와 파생 등록자료를 반영합니다. Registry는 변경이 필요할 때만 제안에 포함되며 Contract는 사람이 직접 작성합니다.</p>
          <pre><code>PYTHONPATH=harness ./.venv/bin/python harness/prepare_registration.py plan \\
  --repo /path/to/OM_TEMP \\
  --registration harness/registrations/om-temp-1.13.0 \\
  --patch-ref origin/fork/om-1.13.0 \\
  --custom-ref origin/custom/om-1.13.0 \\
  --product-version 1.13.0 \\
  --output harness/preparation-plans/om-temp-1.13.0-YYYYMMDD

PYTHONPATH=harness ./.venv/bin/python harness/prepare_registration.py \\
  approval-template \\
  --proposal harness/preparation-plans/om-temp-1.13.0-YYYYMMDD/proposal.yaml \\
  --output /approved/location/registration-approval.yaml

# 담당자가 proposal과 질문을 확인하고 승인서를 작성한 뒤 실행
PYTHONPATH=harness ./.venv/bin/python harness/prepare_registration.py apply \\
  --repo /path/to/OM_TEMP \\
  --registration harness/registrations/om-temp-1.13.0 \\
  --proposal harness/preparation-plans/om-temp-1.13.0-YYYYMMDD/proposal.yaml \\
  --approval /approved/location/registration-approval.yaml \\
  --result /approved/location/registration-apply-result.json

./.venv/bin/python \\
  harness/registrations/om-temp-1.13.0/validate_registration_bundle.py \\
  --repo ../om-temp-1.13.0-custom \\
  --output harness/registrations/om-temp-1.13.0/registration-validation-results.json</code></pre>
          <table class="result-table">
            <thead><tr><th>확인 항목</th><th>실제 결과</th><th>확인한 내용</th></tr></thead>
            <tbody>
              <tr><td>Manifest 구조와 규칙</td><td><em class="pass">PASS · 7개</em></td><td>필수 항목과 경로 규칙</td></tr>
              <tr><td>Registry·Manifest·Contract 연결</td><td><em class="pass">PASS · 7개 ID</em></td><td>세 자료가 같은 BANK-OM을 가리키는지</td></tr>
              <tr><td>Git 전체 변경 목록</td><td><em class="pass">PASS · 111개</em></td><td>저장 목록과 실제 Git diff가 같은지</td></tr>
              <tr><td>현재 공용 경로–BANK-OM 연결표</td><td><em class="pass">PASS · 37개</em></td><td>중복 경로의 모든 BANK-OM 등록 여부</td></tr>
              <tr><td>필수 테스트 코드 존재</td><td><em class="pass">PASS · 9개</em></td><td>Python test 파일과 함수 존재 여부</td></tr>
            </tbody>
          </table>
          <p class="note">이 PASS는 검사 입력자료가 서로 일치한다는 뜻입니다. test 실행 성공이나 배포 승인을 뜻하지 않습니다.</p>
        </div>
      </details>
    """

    connection_sections = """
      <details class="reference">
        <summary><span>3-1</span><strong>OM_TEMP 로컬 repository 준비</strong><small>검사할 branch와 commit을 가져오기</small></summary>
        <div class="reference-body">
          <div class="explain-grid">
            <p><b>의미</b>검사기는 GitHub 화면이 아니라 로컬 repository의 commit·diff·파일을 읽습니다.</p>
            <p><b>만드는 시점</b>새 노트북에서는 한 번 clone하고, 이후에는 검사 전에 fetch합니다.</p>
            <p><b>실제 사용</b>실행 명령의 <code>--repo</code>에 로컬 OM_TEMP 경로를 전달합니다.</p>
            <p><b>확인 결과</b>OpenMetadata 포크 브랜치와 커스텀 브랜치의 SHA가 예상값인지 확인한 뒤에만 검사를 시작합니다.</p>
          </div>
          <pre><code>git clone https://github.com/easyseop/OM_TEMP.git
cd OM_TEMP
git fetch origin fork/om-1.13.0 custom/om-1.13.0
git rev-parse origin/fork/om-1.13.0
git rev-parse origin/custom/om-1.13.0</code></pre>
        </div>
      </details>

      <details class="reference">
        <summary><span>3-2</span><strong>공식 버전에서 시작했다는 이력 연결</strong><small>코드 내용은 그대로 유지</small></summary>
        <div class="reference-body">
          <p>현재 OM_TEMP 원격의 과거 <code>patch/om-1.13.0</code> 브랜치는 공식 OpenMetadata의 과거 변경 이력 전체를 가져오지 않고,
          공식 1.13.0 파일만 새로운 Git 변경 기록으로 저장했습니다. 파일 내용은 같아도 “공식 코드에서 시작했다”는 연결 기록은 없습니다.</p>
          <pre><code>공식 OpenMetadata 1.13.0 Git 번호  f329dd4a...
OM_TEMP 과거 공식 코드 브랜치 Git 번호  2f4f3560...
두 버전의 파일 내용이 같음을 확인하는 값  da56c24d...</code></pre>
          <div class="explain-grid">
            <p><b>왜 별도 연결했나</b>검사기는 파일 내용뿐 아니라 공식 1.13.0에서 시작한 코드인지도 확인합니다. 파일만 같고 시작 이력이 없으면 통과시킬 수 없습니다.</p>
            <p><b>연결 방법</b>공식 <code>f329dd4a...</code>에서 시작해 BANK-OM 변경을 같은 순서로 적용한 로컬 검사 branch를 만들었습니다.</p>
            <p><b>내용 동일 확인</b>결정론적으로 다시 만든 로컬 검사 대상 Git 번호 <code>3a2811cf...</code>와 원격 custom <code>7d19c895...</code>의 최종 파일 내용 확인값이 <code>9495a31c...</code>로 같습니다.</p>
            <p><b>결과</b>코드 내용은 바꾸지 않고 공식 1.13.0에서 시작했다는 이력을 확인할 수 있는 상태로 소스 검사를 실행했습니다.</p>
          </div>
        </div>
      </details>
    """

    gate_sections = """
      <pre><code>./.venv/bin/python harness/run_source_candidate_gates.py \\
  --repo ../om-temp-1.13.0-custom \\
  --harness harness \\
  --registration harness/registrations/om-temp-1.13.0 \\
  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\
  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \\
  --output harness/registrations/om-temp-1.13.0/source-gate-results.json</code></pre>
      <table class="result-table">
        <thead><tr><th>검사명</th><th>무엇을 확인했나</th><th>실제 결과</th></tr></thead>
        <tbody>
          <tr><td>공식 기준 이력 포함</td><td>공식 1.13.0에서 시작한 후보인지</td><td><em class="pass">PASS</em></td></tr>
          <tr><td>커스터마이징 생존</td><td>7개 BANK-OM의 핵심 파일과 Contract 연결이 남았는지</td><td><em class="pass">PASS</em></td></tr>
          <tr><td>필수 테스트 코드 존재</td><td>9개 Python test 파일·함수가 실제로 있는지</td><td><em class="pass">PASS</em></td></tr>
          <tr><td>커밋 작성 규칙</td><td>공식 코드 변경 커밋마다 BANK-OM ID가 하나씩 있는지</td><td><em class="pass">PASS</em></td></tr>
          <tr><td>ID 연결 규칙</td><td>미등록 ID나 잘못 나뉜 후속 커밋이 없는지</td><td><em class="pass">PASS</em></td></tr>
          <tr><td>변경 범위</td><td>각 커밋이 자기 Manifest에 등록된 파일만 바꿨는지</td><td><em class="pass">PASS</em></td></tr>
          <tr><td>민감 경로</td><td>보안·설정·DB 변경 경로 정책을 위반하지 않았는지</td><td><em class="pass">PASS</em></td></tr>
          <tr><td>커밋별 실제 경로 일치</td><td>ID별 실제 변경 파일과 Manifest 목록이 정확히 같은지</td><td><em class="pass">PASS</em></td></tr>
        </tbody>
      </table>
      <p class="note">1.13.0 코드 구조와 변경 이력에 대한 소스 검사 결과입니다. 전체 build, Contract test 실행, 담당자 지정, 1.13.1 업그레이드와 배포 승인은 별도 단계입니다.</p>
    """

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OM_TEMP 검사 전 사전환경 설정 가이드</title>
<style>
:root {{ --ink:#172033; --muted:#667085; --line:#d9dfeb; --blue:#2457d6; --soft:#f5f7fb; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:#eef2f7; color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR","Segoe UI",sans-serif; font-weight:400; -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility; }}
main {{ width:min(1120px,calc(100% - 32px)); margin:32px auto 72px; }}
.guide-pagination {{ display:grid; grid-template-columns:minmax(0,1fr) auto minmax(0,1fr); gap:10px; align-items:stretch; margin:0 0 16px; }}
.guide-pagination-bottom {{ margin:18px 0 0; }}
.guide-page-link,.guide-page-current {{ display:flex; flex-direction:column; justify-content:center; min-width:0; padding:12px 14px; border:1px solid var(--line); border-radius:13px; background:white; }}
.guide-page-link {{ color:var(--blue); text-decoration:none; }}
.guide-page-link.is-next {{ text-align:right; }}
.guide-page-current {{ align-items:center; text-align:center; background:#e8efff; }}
.guide-pagination small {{ margin-bottom:3px; color:var(--muted); font-size:12px; }}
.guide-pagination strong {{ overflow-wrap:anywhere; }}
.hero {{ padding:34px; border-radius:24px; color:white; background:linear-gradient(135deg,#172554,#2457d6); box-shadow:0 20px 55px #193b7b2e; }}
.hero h1 {{ margin:0 0 12px; font-size:clamp(28px,4vw,44px); letter-spacing:-.04em; }}
.hero p {{ margin:6px 0; color:#e5edff; line-height:1.65; }}
.status {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }}
.status span {{ padding:7px 11px; border:1px solid #ffffff42; border-radius:999px; background:#ffffff16; font-size:13px; }}
.page-scope {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:18px 0; }}
.page-scope>div {{ padding:14px 16px; border:1px solid var(--line); border-radius:14px; background:white; }}
.page-scope strong {{ display:block; margin-bottom:6px; }}
.page-scope p {{ margin:0; color:var(--muted); line-height:1.65; }}
.internal-scope {{ margin:0 0 18px; padding:11px 13px; border-left:4px solid var(--orange); background:#fff7ed; color:var(--ink); }}
.intro {{ margin:20px 0; padding:24px; border:1px solid var(--line); border-radius:18px; background:white; }}
.intro h2 {{ margin:0 0 12px; font-size:20px; }}
.intro p {{ margin:8px 0; line-height:1.7; }}
.artifact-map {{ margin:18px 0; border:1px solid var(--line); border-radius:18px; background:white; overflow:hidden; }}
.artifact-map>summary {{ padding:18px 20px; cursor:pointer; font-size:18px; font-weight:800; }}
.artifact-map[open]>summary {{ border-bottom:1px solid var(--line); }}
.artifact-table-wrap {{ padding:0 18px 18px; overflow-x:auto; }}
.artifact-table {{ width:100%; min-width:820px; border-collapse:collapse; font-size:14px; }}
.artifact-table th,.artifact-table td {{ padding:11px 10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; line-height:1.55; }}
.artifact-table th {{ color:#344054; background:#f8fafc; }}
.field-dictionary-link {{ margin:0 18px 18px; }}
.field-dictionary-link a {{ display:block; padding:12px 14px; border:1px solid #b8c8ee; border-radius:11px; color:var(--blue); background:#f7f9ff; text-decoration:none; font-weight:750; }}
.id-table {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:16px; }}
.id-table div {{ padding:14px; border-radius:12px; background:var(--soft); }}
.id-table strong {{ display:block; margin-bottom:5px; }}
details.phase {{ margin:18px 0; border:1px solid #cbd5e1; border-radius:22px; background:#f8fafc; overflow:hidden; box-shadow:0 9px 28px #13234a12; }}
.phase>summary {{ display:grid; grid-template-columns:46px minmax(0,1fr) auto; gap:14px; align-items:center; padding:22px; cursor:pointer; list-style:none; background:white; }}
.phase>summary::-webkit-details-marker {{ display:none; }}
.phase>summary::after {{ content:"＋"; color:var(--blue); font-size:24px; }}
.phase[open]>summary::after {{ content:"－"; }}
.phase-number {{ display:grid; place-items:center; width:42px; height:42px; border-radius:13px; color:white; background:var(--blue); font-weight:800; }}
.phase-title strong {{ display:block; font-size:21px; }}
.phase-title small {{ display:block; margin-top:4px; color:var(--muted); font-size:14px; font-weight:500; }}
.phase-body {{ padding:16px 18px 20px; border-top:1px solid var(--line); }}
.phase-lead {{ margin:2px 4px 16px; line-height:1.7; }}
details.feature {{ margin:12px 0; border:1px solid var(--line); border-radius:18px; background:white; overflow:hidden; box-shadow:0 5px 20px #13234a0c; }}
.feature>summary {{ display:flex; align-items:center; gap:14px; padding:20px 22px; cursor:pointer; list-style:none; }}
.feature>summary::-webkit-details-marker {{ display:none; }}
.feature>summary::after {{ content:"＋"; margin-left:auto; color:var(--blue); font-size:23px; }}
.feature[open]>summary::after {{ content:"－"; }}
.feature>summary span {{ padding:7px 10px; border-radius:9px; color:#153eaa; background:#e8efff; font:700 13px ui-monospace,monospace; }}
.feature>summary strong {{ font-size:18px; }}
.feature-body {{ padding:4px 22px 24px; border-top:1px solid var(--line); }}
.commit,.reason {{ margin-top:20px; }}
h3 {{ margin:0 0 12px; font-size:16px; }}
dl {{ display:grid; gap:8px; margin:0 0 12px; }}
dl div {{ display:grid; grid-template-columns:128px minmax(0,1fr); gap:10px; align-items:start; }}
dt {{ color:var(--muted); font-size:14px; }}
dd {{ margin:0; min-width:0; overflow-wrap:anywhere; }}
code {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
.github {{ display:inline-block; margin:2px 0 14px; color:var(--blue); font-weight:650; text-decoration:none; }}
img {{ display:block; max-width:100%; height:auto; margin:10px auto; border:1px solid var(--line); border-radius:12px; background:white; }}
.sub {{ margin-top:14px; border:1px solid var(--line); border-radius:12px; background:#fbfcfe; }}
.sub>summary {{ padding:14px 16px; cursor:pointer; font-weight:700; }}
.sub>img,.sub>p,.sub>.diff-grid,.sub>pre {{ margin:0 16px 16px; }}
.reason {{ padding:16px; border-left:4px solid var(--blue); border-radius:10px; background:#f3f6ff; }}
.reason p {{ margin:0; line-height:1.75; }}
.diff-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }}
figure {{ margin:0; }}
figcaption {{ margin:4px 0 7px; color:var(--muted); font-size:13px; font-weight:700; }}
figure img {{ margin:0; width:100%; }}
pre {{ overflow:auto; max-height:580px; padding:16px; border-radius:10px; color:#e6edf7; background:#101827; font-size:12px; line-height:1.55; }}
.manifest-fields {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; margin:14px 0; }}
.manifest-fields p {{ margin:0; padding:14px; border:1px solid var(--line); border-radius:12px; background:white; line-height:1.55; }}
.manifest-fields b {{ display:block; color:var(--blue); margin-bottom:5px; }}
details.reference {{ margin:10px 0; border:1px solid var(--line); border-radius:15px; background:white; overflow:hidden; }}
.reference>summary {{ display:grid; grid-template-columns:42px auto minmax(0,1fr) auto; gap:10px; align-items:center; padding:17px 18px; cursor:pointer; list-style:none; }}
.reference>summary::-webkit-details-marker {{ display:none; }}
.reference>summary::after {{ content:"펼치기"; justify-self:end; color:var(--blue); font-size:13px; font-weight:700; }}
.reference[open]>summary::after {{ content:"접기"; }}
.reference>summary span {{ padding:6px 7px; border-radius:8px; color:#153eaa; background:#e8efff; text-align:center; font:700 12px ui-monospace,monospace; }}
.reference>summary strong {{ font-size:17px; }}
.reference>summary small {{ color:var(--muted); font-size:14px; }}
.reference-body {{ padding:4px 18px 18px; border-top:1px solid var(--line); overflow-x:auto; }}
.reference-body>p {{ line-height:1.7; }}
.explain-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; margin:15px 0; }}
.explain-grid p {{ margin:0; padding:13px 14px; border-radius:11px; background:var(--soft); line-height:1.6; }}
.explain-grid b {{ display:block; margin-bottom:4px; color:#344054; }}
.block {{ color:#b42318; font-style:normal; font-weight:800; }}
.pass {{ color:#067647; font-style:normal; font-weight:800; }}
.review {{ color:#b54708; font-style:normal; font-weight:800; }}
.error {{ color:#7a271a; font-style:normal; font-weight:800; }}
.optional>summary {{ background:#f8fbff; }}
.warning>summary {{ background:#fff9ed; }}
.note {{ padding:12px 14px; border-radius:10px; background:#eef4ff; }}
.lifecycle {{ width:100%; border-collapse:collapse; margin-top:14px; font-size:14px; }}
.lifecycle th,.lifecycle td {{ padding:11px 10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; line-height:1.5; }}
.lifecycle th {{ color:#344054; background:#f8fafc; }}
.result-table {{ width:100%; min-width:620px; border-collapse:collapse; margin:16px 0; font-size:14px; }}
.result-table th,.result-table td {{ padding:11px 10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; line-height:1.5; }}
.result-table th {{ color:#344054; background:#f8fafc; }}
.foot {{ margin-top:22px; padding:20px; border-radius:16px; background:#fff7e6; border:1px solid #f1d49b; line-height:1.65; }}
@media (max-width:720px) {{
  main {{ width:min(100% - 20px,1120px); margin-top:10px; }}
  .guide-pagination {{ grid-template-columns:1fr 1fr; }}
  .guide-page-current {{ grid-column:1 / -1; grid-row:1; }}
  .hero {{ padding:24px; border-radius:18px; }}
  .page-scope {{ grid-template-columns:1fr; }}
  .id-table,.diff-grid,.manifest-fields,.explain-grid {{ grid-template-columns:1fr; }}
  .phase>summary {{ grid-template-columns:42px minmax(0,1fr) auto; padding:17px; }}
  .reference>summary {{ grid-template-columns:38px minmax(0,1fr) auto; }}
  .reference>summary small {{ grid-column:2 / 4; }}
  dl div {{ grid-template-columns:1fr; gap:2px; }}
}}
</style>
</head>
<body>
<main>
  {pagination}
  <section class="hero">
    <h1>OM_TEMP 검사 전 사전환경 설정 가이드</h1>
    <p>검사기가 실제 코드를 어떤 기준자료와 비교하는지, 그 자료를 언제 만들고 어떻게 사용하는지 실제 1.13.0 예시로 확인합니다.</p>
    <p>대상: easyseop/OM_TEMP · custom/om-1.13.0</p>
    <div class="status"><span>Manifest 7개</span><span>전체 변경 111개</span><span>공용 경로 37개</span><span>소스 검사 8종 PASS</span></div>
  </section>
  <section class="page-scope" aria-label="이 페이지가 답하는 질문과 범위">
    <div><strong>이 페이지가 답하는 질문</strong><p>검사 전에 어떤 관리자료를 준비하고, 실제 변경 파일을 어떤 BANK-OM 기능에 연결하는가?</p></div>
    <div><strong>여기서 답하지 않는 것</strong><p>공식 1.13.1 병합 충돌과 현재 검사 대상 코드의 판정은 5번에서 설명합니다.</p></div>
    <div><strong>읽고 나면</strong><p>등록자료와 로컬 repository를 연결한 뒤 OM_TEMP 업그레이드 연습으로 이동합니다.</p></div>
  </section>
  <p class="internal-scope"><strong>우리 내부에서 만든 기준자료:</strong> Manifest·Registry·Contract와 BANK-OM ID는 OpenMetadata 공식 설정이 아니라 <code>easyseop/openmetadata-test</code>가 행내 변경을 검사하기 위해 정의한 관리 자료입니다.</p>
  <section class="intro">
    <h2>왜 먼저 설정해야 하나</h2>
    <p class="note"><strong>읽는 순서와 실행 순서는 다릅니다.</strong> 이 문서는 검사기 원리 다음에 읽지만, 실제 작업에서는 검사기를 실행하기 전에 아래 기준자료를 먼저 준비합니다. 검사기 설명을 먼저 배치한 이유는 Manifest·Registry·Contracts가 어느 검사에 사용되는지 이해한 뒤 설정할 수 있게 하기 위해서입니다.</p>
    <p>검사기는 코드만 보고 업무 기능의 정상 조건을 추측하지 않습니다. 어떤 BANK-OM을 검사하고, 어떤 파일과 동작을 정상으로 볼지 정한 자료를 먼저 등록해야 합니다.</p>
    <p>Manifest는 BANK-OM ID마다 최초 등록 때 한 파일을 만듭니다. 같은 기능을 새 공식 버전에 맞추거나 보완할 때는 새 ID를 만들지 않습니다. 기존 Manifest를 새 버전 폴더에 복사한 뒤 달라진 파일과 검증 기준만 갱신합니다. 한 기능에 Git 변경 기록이 여러 개여도 Manifest는 하나입니다.</p>
    <div class="id-table">
      <div><strong>BANK-OM ID</strong>사람이 발급하는 업무 기능 번호</div>
      <div><strong>Git 변경 기록 번호</strong>Git이 한 번 저장한 코드 변경에 자동 부여하는 값(<code>commit SHA</code>)</div>
    </div>
    <div class="scope">
      <strong>실제 BANK-OM-007 예시</strong><br>
      최초 구현 <code>62e39da8…</code>는 8개 파일을 변경했고, 후속 보완
      <code>7d19c895…</code>는 2개 파일을 추가했습니다. 두 SHA는 각각 다른 변경의
      근거이므로 최근 SHA 하나로 대체하지 않습니다. Manifest의
      <code>changed_paths</code>에는 현재 검사할 10개 파일을 모두 적고, 최종 검사는
      두 변경을 모두 포함한 custom branch의 마지막 SHA 하나를 사용합니다.
    </div>
    <table class="lifecycle">
      <thead><tr><th>자료</th><th>처음 만드는 시점</th><th>업그레이드 때</th></tr></thead>
      <tbody>
        <tr><td>Manifest·Registry·Contract</td><td>최초 기능 등록</td><td>새 코드 기준으로 검토·갱신</td></tr>
        <tr><td>현재 공용 파일·전체 변경 목록</td><td>실제 Git diff 확정 후</td><td>새 branch diff로 다시 생성</td></tr>
        <tr><td>과거 코드 경로–BANK-OM 연결표</td><td>기준 snapshot의 commit 이력 확정 후</td><td>기준 snapshot SHA가 바뀔 때만 재생성</td></tr>
        <tr><td>Patch-lock</td><td>patch-replay를 선택할 때만</td><td>재적용 commit이 바뀔 때 새 revision</td></tr>
      </tbody>
    </table>
  </section>

  <details class="artifact-map" open>
    <summary>검사에 사용하는 산출물과 핵심 요소</summary>
    <div class="artifact-table-wrap">
      <table class="artifact-table">
        <thead><tr><th>산출물</th><th>의미</th><th>핵심 요소</th><th>어디에 사용되나</th></tr></thead>
        <tbody>
          <tr><td><strong>Manifest</strong></td><td>BANK-OM 한 기능의 코드 변경과 검증 기준</td><td>ID·상태·kind, changed·required, watch, Contract·test 연결</td><td>기능 생존, 변경 범위, 공식 업그레이드 영향과 실제 경로 일치 검사에 사용합니다.</td></tr>
          <tr><td><strong>Registry</strong></td><td>검사해야 할 BANK-OM 전체 목록과 관리 상태</td><td>customization_id, title, owner·상태, criticality, Manifest·Contract 경로</td><td>활성·폐기 ID, 미등록 ID, 담당자와 연결 자료 누락을 확인할 때 사용합니다.</td></tr>
          <tr><td><strong>Contracts</strong></td><td>파일 존재만으로 알 수 없는 업무 동작의 정상 조건</td><td>Contract ID, invariant, required_tests, customization_ids</td><td>필수 test 코드 존재, 커스터마이징 제거본의 실패, 실제 기능 실행 결과를 확인할 때 사용합니다.</td></tr>
          <tr><td><strong>현재 공용 경로–BANK-OM 연결표</strong></td><td>현재 버전에서 한 파일을 여러 BANK-OM이 함께 변경했다는 관계</td><td>공용 파일 경로와 현재 버전의 BANK-OM ID 목록</td><td>현재 버전 범위 검사에서 같은 파일의 변경을 한 BANK-OM에 잘못 귀속하지 않도록 사용합니다.</td></tr>
          <tr><td><strong>과거 코드 경로–BANK-OM 연결표</strong></td><td>최초 등록에 사용한 과거 코드 시점의 파일별 BANK-OM 관계</td><td>과거 snapshot 경로와 그 시점까지 변경한 BANK-OM ID</td><td>T25-R이 과거 코드를 기능별로 재구성할 때만 사용합니다. 현재 범위 검사는 이 파일을 읽지 않습니다.</td></tr>
          <tr><td><strong>전체 변경 목록</strong></td><td>공식 원본과 행내 snapshot 사이에서 실제로 달라진 모든 파일</td><td>root 기준 파일 경로 111개</td><td>Manifest 전체 범위가 실제 Git diff를 빠짐없이 설명하는지 사전검증할 때 사용합니다.</td></tr>
          <tr><td><strong>Repository layout</strong></td><td>경로를 공식 코드·행내 정책·확장·미분류로 나누는 규칙</td><td>공식 기준 SHA, 경로 문법, 영역별 root, 미분류 처리 방식</td><td>커밋의 관리 대상 여부, 민감 경로와 미분류 새 모듈을 판단할 때 사용합니다.</td></tr>
          <tr><td><strong>Sensitive zones</strong></td><td>보안·인증·설정·DB 관련 경로의 위험 등급</td><td>frozen·protected·watched 경로 목록</td><td>변경 경로를 즉시 차단, 담당자 승인 또는 결과 표시 대상으로 구분할 때 사용합니다.</td></tr>
          <tr><td><strong>검사 대상 잠금정보</strong><br><small>Candidate lock</small></td><td>검사할 정확한 코드 버전을 기록해 검사 도중 대상이 바뀌지 않게 하는 자료</td><td>공식 시작·업데이트 버전, 검사 대상 Git 번호, 코드 내용 확인값, 적용 방식</td><td>소스 검사·동작 시험·배포 결과가 모두 같은 코드를 대상으로 했는지 확인할 때 사용합니다.</td></tr>
          <tr><td><strong>재적용 순서표</strong> <small>(선택)</small><br><small>Patch-lock</small></td><td>BANK-OM 변경을 하나씩 다시 적용할 때 사용할 변경 기록과 순서를 고정한 자료</td><td>BANK-OM ID, 순서표 개정번호, 적용할 Git 변경 기록과 확인값</td><td>변경을 하나씩 재적용하거나 과거 상태를 재현할 때만 사용합니다. 정식 병합 방식의 필수 자료는 아닙니다.</td></tr>
          <tr><td><strong>검사 결과 JSON·YAML</strong></td><td>검사 당시 입력과 각 판정을 나중에 다시 확인하는 증거</td><td>검사명, 입력 SHA·digest, verdict, reasons, 결과 digest</td><td>책임자 검토·인수인계와 T90·T91의 동일 대상 확인에 사용합니다.</td></tr>
        </tbody>
      </table>
    </div>
    <p class="field-dictionary-link"><a href="OM_TEMP_관리파일_필드_사전_미리보기.html" target="_top">Manifest의 assurance·series와 나머지 관리파일 필드를 설명한 전체 필드 사전 열기 →</a></p>
  </details>

  <details class="phase" open>
    <summary>
      <span class="phase-number">1</span>
      <span class="phase-title"><strong>Manifest 등록</strong><small>실제 commit diff를 BANK-OM 기능과 연결</small></span>
    </summary>
    <div class="phase-body">
      <p class="phase-lead">각 제목을 펼치면 실제 GitHub 변경 기록, 여러 파일을 하나의 BANK-OM 기능으로 묶은 이유와 현재 Manifest 내용을 볼 수 있습니다.</p>
      {''.join(sections)}
      <h3>Manifest 세 목록을 읽는 기준</h3>
      <div class="manifest-fields">
        <p><b>changed_paths</b>현재 OpenMetadata 버전에서 해당 BANK-OM 기능의 모든 커밋이 실제로 변경한 전체 파일입니다.</p>
        <p><b>required_changed_paths</b>그 파일이 없거나 공식 원본과 같아지면 기능 미적용으로 바로 차단할 핵심 파일입니다.</p>
        <p><b>upgrade_watch.paths</b>공식 버전이 바뀔 때 이 기능의 영향 여부를 다시 확인할 파일입니다. 준비도구는 직접 변경한 경로 중 공식 OpenMetadata 포크 브랜치에도 있는 경로만 자동 제안하고, 행내 전용 파일과 간접 의존 경로는 담당자가 추가 여부를 결정합니다.</p>
      </div>
    </div>
  </details>

  <details class="phase">
    <summary>
      <span class="phase-number">2</span>
      <span class="phase-title"><strong>검사 기준자료 등록</strong><small>Registry·Contracts·공용 파일·전체 변경 목록</small></span>
    </summary>
    <div class="phase-body">
      <p class="phase-lead">OM_TEMP 1.13.0의 실제 기준자료를 생성했습니다. 각 제목을 펼치면 의미, 생성 시점, 실제 등록 수와 사전검증 결과를 확인할 수 있습니다.</p>
      {reference_sections}
    </div>
  </details>

  <details class="phase">
    <summary>
      <span class="phase-number">3</span>
      <span class="phase-title"><strong>로컬 검사 대상 연결</strong><small>OM_TEMP branch와 기준 commit 확인</small></span>
    </summary>
    <div class="phase-body">
      <p class="phase-lead">검사기는 컴퓨터에 내려받은 OM_TEMP Git 저장소를 직접 읽습니다. GitHub에 있는 코드와 내용이 같고, 공식 1.13.0에서 시작했다는 변경 이력도 확인할 수 있는 로컬 branch를 연결했습니다.</p>
      {connection_sections}
    </div>
  </details>

  <details class="phase">
    <summary>
      <span class="phase-number">4</span>
      <span class="phase-title"><strong>실제 소스 검사</strong><small>실행 명령과 8개 검사 결과</small></span>
    </summary>
    <div class="phase-body">
      <p class="phase-lead">등록한 관리자료와 로컬 검사 대상 코드를 연결해 소스 검사를 실행하고, 각 판정과 입력 정보를 JSON 결과 파일로 저장했습니다.</p>
      {gate_sections}
    </div>
  </details>

  <section class="foot"><strong>이 페이지의 결론:</strong> 1.13.0 기준 Registry 7개, Contract 7개·필수 test 9개, 현재 공용 경로 37개, 과거 코드 경로–BANK-OM 연결표 111개와 전체 변경 111개를 생성했습니다. 소스 검사 8종 PASS는 원격 raw custom branch가 아니라 공식 1.13.0에서 BANK-OM 변경을 결정론적으로 다시 구성한 로컬 후보 <code>3a2811cf…</code>의 기록입니다. 재현 명령과 전체 SHA는 등록 폴더의 <code>REPRODUCIBILITY.md</code>에 있습니다. 이 결과에는 담당자 지정, OpenMetadata 전체 build, Contract test 실제 실행, 1.13.1 업그레이드와 배포 승인이 포함되지 않습니다. 다음 페이지에서 별도로 수행한 1.13.1 코드 업그레이드 연습을 확인합니다.</section>
  <div class="guide-pagination-bottom">{pagination}</div>
</main>
</body>
</html>
"""


def main() -> None:
    markdown = "\n".join(line.rstrip() for line in render().splitlines()) + "\n"
    preview = "\n".join(line.rstrip() for line in render_html().splitlines()) + "\n"
    OUTPUT.write_text(markdown, encoding="utf-8")
    HTML_OUTPUT.write_text(preview, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    print(f"wrote {HTML_OUTPUT}")


if __name__ == "__main__":
    main()
