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
            "두 커밋 모두 Tibero 연결 유형 하나를 완성합니다. 최초 8개 파일은 "
            "allowed_changed_paths에, 후속 커밋에서 처음 추가된 2개 파일은 "
            "candidate_additional_paths에 등록합니다. Git commit SHA는 두 개지만 "
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
        "## 이 자료가 필요한 이유",
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
        "| 공용 파일 소유정보 | 실제 diff의 중복 경로를 계산해 작성 | 새 버전 diff로 다시 계산·검토 | 확정본을 읽음 |",
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
        "| Git commit SHA | Git이 한 번의 코드 저장에 자동 부여하는 값 | `d983f7c...` |",
        "",
        "Manifest는 **BANK-OM ID마다 한 파일**을 만듭니다. 같은 기능을 후속 보완하면 "
        "BANK-OM-007처럼 Git commit SHA는 여러 개가 될 수 있지만 Manifest는 하나입니다.",
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
        "Manifest 초안 전체를 확인할 수 있습니다.",
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
                    "`allowed_changed_paths`도 한 경로입니다. 같은 파일이 한글 입력 "
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
                f"<summary><strong>{customization_id} Manifest 초안 전체 보기</strong></summary>",
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
            "### Manifest 네 목록을 읽는 기준",
            "",
            "| 항목 | 이 초안에 들어간 기준 | 검사에서 쓰는 방식 |",
            "|---|---|---|",
            "| `allowed_changed_paths` | 최초 BANK-OM 커밋이 실제 변경한 모든 파일 | 목록 밖 파일을 같은 ID로 변경하면 차단하고, 목록 안 파일이 검사 대상 custom branch의 최종 코드에서 실제로 달라지지 않으면 검토를 요구 |",
            "| `required_changed_paths` | 기능이 적용됐음을 판단하는 핵심 구현 파일 | 파일이 없거나 공식 원본과 같아지면 기능이 빠진 것으로 보고 차단 |",
            "| `candidate_additional_paths` | 같은 ID의 후속 커밋에서 처음 추가된 파일 | 사전 등록 없이 확장한 변경과 승인된 후속 변경을 구분 |",
            "| `upgrade_watch.paths` | 공식 버전 변경 비교 검사(T42)가 확인할 경로 | 공식 새 버전에서 해당 경로가 바뀌면 자동 통과하지 않고 재검토를 요구 |",
            "",
            "T42는 공식 OpenMetadata의 이전 버전과 새 버전에서 지정 경로가 "
            "바뀌었는지 확인하는 검사입니다. `upgrade_watch.paths`에는 현재 T42 "
            "구현에 맞춰 해당 ID의 변경 범위 전체와 "
            "직접 수정하지 않았지만 기능이 의존하는 공식 파일을 함께 넣었습니다. "
            "따라서 watch에 있다고 해서 그 파일을 이 커밋이 반드시 수정했다는 뜻은 아닙니다.",
            "",
            "## 2. 검사 기준자료 등록",
            "",
            "아래 자료는 모두 `openmetadata-test`에 보관합니다. Git이 자동으로 "
            "만들 수 있는 값과 사람이 결정해야 하는 기준을 구분해 등록합니다. 아래 "
            "코드는 작성 형태를 보여주는 예시이며, OM_TEMP 1.13.0의 실제 기준자료 "
            "파일 생성은 다음 작업입니다.",
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
            "<summary><strong>2-3. 공용 파일 소유정보 · 한 파일을 함께 변경한 ID</strong></summary>",
            "",
            "**의미:** 여러 BANK-OM이 같은 파일을 정상적으로 변경했다는 사실과 실제 "
            "소유 ID를 기록합니다.",
            "",
            "**생성·갱신 시점:** Manifest들의 실제 변경 경로를 비교해 중복 경로를 "
            "자동 제안한 뒤, 각 commit diff에서 ID별 코드가 실제로 있는지 사람이 "
            "확인합니다. 업그레이드 버전마다 다시 계산·검토합니다.",
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
            "**실제 사용:** 검사기는 공용 파일을 한 ID의 단독 소유로 잘못 판단하지 "
            "않고, 등록된 모든 ID가 해당 경로를 실제로 변경했는지 확인합니다. 등록되지 "
            "않은 중복 소유는 담당 ID를 결정할 수 없으므로 재구성 검사가 "
            "`ANALYSIS ERROR`로 중단됩니다.",
            "",
            "</details>",
            "",
            "<details>",
            "<summary><strong>2-4. 전체 변경 목록 · patch와 custom 사이의 111개 경로</strong></summary>",
            "",
            "**의미:** `patch/om-1.13.0`과 `custom/om-1.13.0` 사이에서 최종적으로 "
            "달라진 모든 파일 경로입니다.",
            "",
            "**생성·갱신 시점:** 검사 대상 commit이 확정된 뒤 Git으로 생성하며, "
            "업그레이드 버전마다 다시 생성합니다. 사람이 111개를 직접 작성하지 않습니다.",
            "",
            "```bash",
            "git diff --name-only origin/patch/om-1.13.0..origin/custom/om-1.13.0 \\",
            "  > source-diff-paths.txt",
            "```",
            "",
            "```text",
            "openmetadata-service/src/main/java/org/openmetadata/service/Entity.java",
            "openmetadata-ui/src/main/resources/ui/src/components/Database/SchemaEditor/SchemaEditor.tsx",
            "openmetadata-spec/src/main/resources/json/schema/entity/services/connections/database/tiberoConnection.json",
            "```",
            "",
            "**실제 사용:** 실제 전체 변경 111개와 모든 Manifest의 변경 범위를 "
            "양방향으로 비교합니다. 어느 Manifest에도 등록되지 않은 경로가 있으면 "
            "`BLOCK`, Manifest에만 있고 실제 최종 코드가 바뀌지 않은 경로는 "
            "`APPROVAL` 대상입니다.",
            "",
            "</details>",
            "",
            "<details>",
            "<summary><strong>2-5. Patch-lock · 커밋 재적용을 선택할 때만 사용하는 순서표</strong></summary>",
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
            "## 3. 로컬 검사 대상 연결",
            "",
            "<details>",
            "<summary><strong>3-1. OM_TEMP repository 준비와 branch 확인</strong></summary>",
            "",
            "**의미:** 검사기는 GitHub 화면을 원격으로 읽는 것이 아니라 로컬 Git "
            "repository의 commit·diff·파일을 직접 검사합니다.",
            "",
            "**최초 준비:** 다른 노트북에서는 한 번 clone합니다. 이미 받은 뒤에는 "
            "`git fetch`로 갱신합니다. 현재 노트북에는 "
            "`work/om-temp-1.13.0-custom`에 OM_TEMP 원격 branch도 fetch되어 있으므로 "
            "다시 clone하지 않습니다.",
            "",
            "```bash",
            "git clone https://github.com/easyseop/OM_TEMP.git",
            "cd OM_TEMP",
            "git fetch origin patch/om-1.13.0 custom/om-1.13.0",
            "git rev-parse origin/patch/om-1.13.0",
            "git rev-parse origin/custom/om-1.13.0",
            "```",
            "",
            "**검사 연결:** 검사 실행기의 `--repo`에 이 로컬 경로를 전달합니다. "
            "검사기는 여기서 BANK-OM commit, Customization-ID, 111개 diff와 최종 "
            "파일 내용을 읽습니다.",
            "",
            "</details>",
            "",
            "<details>",
            "<summary><strong>3-2. 공식 1.13.0과 OM_TEMP patch 기준 연결 주의사항</strong></summary>",
            "",
            "OM_TEMP는 공식 OpenMetadata 전체 Git 이력을 복사하지 않고 공식 1.13.0 "
            "파일 상태를 독립 commit으로 가져왔습니다. 따라서 다음 세 값을 구분해야 합니다.",
            "",
            "```text",
            "공식 OpenMetadata 1.13.0 commit: f329dd4a...",
            "OM_TEMP patch/om-1.13.0 commit: 2f4f3560...",
            "두 commit의 동일한 Git tree: da56c24d...",
            "```",
            "",
            "현재 vendor 검사 실행기는 공식 commit이 로컬 이력의 조상이라고 가정하므로 "
            "기존 1.13.1 설정을 그대로 사용하면 T25가 잘못 실패할 수 있습니다. 실제 "
            "검사 전에는 공식 commit과 로컬 baseline commit을 별도 입력으로 구분하거나, "
            "동일 tree를 인정하는 연결 검사를 추가해야 합니다. 이 보완이 끝나기 전에는 "
            "전체 검사 실행 준비 완료로 표시하지 않습니다.",
            "",
            "</details>",
            "",
            "## 현재 상태",
            "",
            "- BANK-OM-001~007 Manifest 초안 7개 생성 완료",
            "- 실제 Git commit의 변경 파일 목록을 초안에 반영 완료",
            "- 현재 Manifest 스키마 및 기본 의미 검사 7개 통과",
            "- Registry·Contract·공용 파일·111개 목록의 생성 원칙과 예시 정리 완료",
            "- 실제 1.13.0 등록 파일 생성과 독립 snapshot 연결 보완은 다음 작업",
            "- OM_TEMP 전체 코드 build, 업무 동작 test, 1.13.1 업그레이드 비교는 아직 실행 전",
            "- 따라서 이 문서의 Manifest는 **코드 기준 초안**이며 배포 승인 결과가 아님",
            "",
        ]
    )
    return "\n".join(lines)


def render_html() -> str:
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
                <p>변경 파일이 하나이므로 Manifest의 <code>allowed_changed_paths</code>도
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
                  <summary>{item['id']} Manifest 초안 전체 보기</summary>
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
            <p><b>실제 사용</b>검사기가 BANK-OM-005의 Manifest와 Contract 연결을 찾아 읽습니다.</p>
            <p><b>검사 결과</b>연결 파일이 없거나 ID가 서로 다르면 입력 묶음을 읽을 수 없어 검사를 시작하지 않습니다.</p>
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
            <p><b>실제 사용</b>필수 테스트 코드 존재 검증은 <code>required_tests</code>의 <code>파일 경로::test 함수명</code>이 실제 Python pytest 코드로 있는지 확인합니다.</p>
            <p><b>필수 여부와 결과</b><code>active</code> BANK-OM에는 Contract와 필수 test가 각각 하나 이상 필요합니다. 없으면 <em class="block">BLOCK</em>입니다. PASS는 test 코드 존재만 뜻하며 실행 성공은 후속 검사에서 확인합니다. Java·TypeScript test 확인은 추가 개발 대상입니다.</p>
          </div>
          <pre><code>- id: CONTRACT-KOREAN-IME
  invariant: 한글 입력 중 자모가 중복·역전·소실되지 않는다.
  required_tests:
    - tests/bank/contracts/test_korean_ime.py::test_hangul_composition_roundtrip
  customization_ids: [BANK-OM-005]</code></pre>
        </div>
      </details>

      <details class="reference">
        <summary><span>2-3</span><strong>공용 파일 소유정보</strong><small>같은 파일을 변경한 BANK-OM 목록</small></summary>
        <div class="reference-body">
          <div class="explain-grid">
            <p><b>의미</b>여러 기능이 같은 공식 파일을 정상적으로 함께 변경했음을 기록합니다.</p>
            <p><b>만드는 시점</b>Manifest 경로의 중복을 자동 추출한 뒤 사람이 실제 diff를 확인하고, 버전마다 다시 계산합니다.</p>
            <p><b>실제 사용</b>Entity.java를 BANK-OM-001만의 파일로 잘못 판단하지 않고 001·002 공동 변경으로 검사합니다.</p>
            <p><b>검사 결과</b>중복 경로의 담당 ID를 결정할 수 없으면 재구성 검사가 <em class="error">ANALYSIS ERROR</em>로 중단됩니다.</p>
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
            <p><b>검사 결과</b>Manifest에 없는 실제 변경은 <em class="block">BLOCK</em>, 실제 변경이 없는 Manifest 경로는 <em class="review">APPROVAL</em> 대상입니다.</p>
          </div>
          <pre><code>git diff --name-only \\
  origin/patch/om-1.13.0..origin/custom/om-1.13.0 \\
  &gt; source-diff-paths.txt</code></pre>
          <p class="note">111개 경로는 사람이 입력하지 않습니다. Git이 만든 목록을 검사 기준자료로 보관합니다.</p>
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
    """

    connection_sections = """
      <details class="reference">
        <summary><span>3-1</span><strong>OM_TEMP 로컬 repository 준비</strong><small>검사할 branch와 commit을 가져오기</small></summary>
        <div class="reference-body">
          <div class="explain-grid">
            <p><b>의미</b>검사기는 GitHub 화면이 아니라 로컬 repository의 commit·diff·파일을 읽습니다.</p>
            <p><b>만드는 시점</b>새 노트북에서는 한 번 clone하고, 이후에는 검사 전에 fetch합니다.</p>
            <p><b>실제 사용</b>실행 명령의 <code>--repo</code>에 로컬 OM_TEMP 경로를 전달합니다.</p>
            <p><b>확인 결과</b>patch와 custom branch의 SHA가 예상값인지 확인한 뒤에만 검사를 시작합니다.</p>
          </div>
          <pre><code>git clone https://github.com/easyseop/OM_TEMP.git
cd OM_TEMP
git fetch origin patch/om-1.13.0 custom/om-1.13.0
git rev-parse origin/patch/om-1.13.0
git rev-parse origin/custom/om-1.13.0</code></pre>
        </div>
      </details>

      <details class="reference warning">
        <summary><span>3-2</span><strong>독립 snapshot 연결 보완</strong><small>검사 실행 전 해결할 항목</small></summary>
        <div class="reference-body">
          <p>OM_TEMP의 patch branch는 공식 OpenMetadata commit 이력을 그대로 포함하지 않고,
          공식 1.13.0 파일 상태를 새 commit으로 가져왔습니다. 파일은 같아도 commit 계보는 다릅니다.</p>
          <pre><code>공식 OpenMetadata 1.13.0 commit  f329dd4a...
OM_TEMP patch/om-1.13.0 commit   2f4f3560...
두 commit의 동일한 Git tree    da56c24d...</code></pre>
          <div class="explain-grid">
            <p><b>왜 확인하나</b>현재 실행기는 공식 commit이 OM_TEMP 이력의 조상이라고 가정해 T25가 잘못 실패할 수 있습니다.</p>
            <p><b>필요한 보완</b>공식 source SHA와 로컬 baseline SHA를 나누거나, 동일한 tree이면 같은 기준 코드로 인정해야 합니다.</p>
            <p><b>현재 상태</b>보완 전에는 전체 검사 연결 완료나 배포 승인으로 표시하지 않습니다.</p>
            <p><b>다음 작업</b>연결 방식을 확정한 뒤 실제 Registry·Contract·공용 파일·111개 목록을 생성합니다.</p>
          </div>
        </div>
      </details>
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
body {{ margin:0; background:#eef2f7; color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans KR",sans-serif; }}
main {{ width:min(1120px,calc(100% - 32px)); margin:32px auto 72px; }}
.hero {{ padding:34px; border-radius:24px; color:white; background:linear-gradient(135deg,#172554,#2457d6); box-shadow:0 20px 55px #193b7b2e; }}
.hero h1 {{ margin:0 0 12px; font-size:clamp(28px,4vw,44px); letter-spacing:-.04em; }}
.hero p {{ margin:6px 0; color:#e5edff; line-height:1.65; }}
.status {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }}
.status span {{ padding:7px 11px; border:1px solid #ffffff42; border-radius:999px; background:#ffffff16; font-size:13px; }}
.intro {{ margin:20px 0; padding:24px; border:1px solid var(--line); border-radius:18px; background:white; }}
.intro h2 {{ margin:0 0 12px; font-size:20px; }}
.intro p {{ margin:8px 0; line-height:1.7; }}
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
.reference-body {{ padding:4px 18px 18px; border-top:1px solid var(--line); }}
.reference-body>p {{ line-height:1.7; }}
.explain-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; margin:15px 0; }}
.explain-grid p {{ margin:0; padding:13px 14px; border-radius:11px; background:var(--soft); line-height:1.6; }}
.explain-grid b {{ display:block; margin-bottom:4px; color:#344054; }}
.block {{ color:#b42318; font-style:normal; font-weight:800; }}
.review {{ color:#b54708; font-style:normal; font-weight:800; }}
.error {{ color:#7a271a; font-style:normal; font-weight:800; }}
.optional>summary {{ background:#f8fbff; }}
.warning>summary {{ background:#fff9ed; }}
.note {{ padding:12px 14px; border-radius:10px; background:#eef4ff; }}
.lifecycle {{ width:100%; border-collapse:collapse; margin-top:14px; font-size:14px; }}
.lifecycle th,.lifecycle td {{ padding:11px 10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; line-height:1.5; }}
.lifecycle th {{ color:#344054; background:#f8fafc; }}
.foot {{ margin-top:22px; padding:20px; border-radius:16px; background:#fff7e6; border:1px solid #f1d49b; line-height:1.65; }}
@media (max-width:720px) {{
  main {{ width:min(100% - 20px,1120px); margin-top:10px; }}
  .hero {{ padding:24px; border-radius:18px; }}
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
  <section class="hero">
    <h1>OM_TEMP 검사 전 사전환경 설정 가이드</h1>
    <p>검사기가 실제 코드를 어떤 기준자료와 비교하는지, 그 자료를 언제 만들고 어떻게 사용하는지 실제 1.13.0 예시로 확인합니다.</p>
    <p>대상: easyseop/OM_TEMP · custom/om-1.13.0</p>
    <div class="status"><span>Manifest 초안 7개</span><span>Git diff 일치 확인</span><span>스키마·기본 의미 검사 PASS</span><span>실제 기준자료 생성·검사 연결은 다음 단계</span></div>
  </section>
  <section class="intro">
    <h2>왜 먼저 설정해야 하나</h2>
    <p>검사기는 코드만 보고 업무 기능의 정상 조건을 추측하지 않습니다. 어떤 BANK-OM을 검사하고, 어떤 파일과 동작을 정상으로 볼지 정한 자료를 먼저 등록해야 합니다.</p>
    <p>Manifest는 BANK-OM ID마다 한 파일을 만듭니다. 같은 기능의 후속 보완은 Git commit SHA가 여러 개여도 Manifest 하나에 연결합니다.</p>
    <div class="id-table">
      <div><strong>BANK-OM ID</strong>사람이 발급하는 업무 기능 번호</div>
      <div><strong>Git commit SHA</strong>Git이 저장된 코드 변경에 자동 부여하는 값</div>
    </div>
    <table class="lifecycle">
      <thead><tr><th>자료</th><th>처음 만드는 시점</th><th>업그레이드 때</th></tr></thead>
      <tbody>
        <tr><td>Manifest·Registry·Contract</td><td>최초 기능 등록</td><td>새 코드 기준으로 검토·갱신</td></tr>
        <tr><td>공용 파일·전체 변경 목록</td><td>실제 Git diff 확정 후</td><td>새 branch diff로 다시 생성</td></tr>
        <tr><td>Patch-lock</td><td>patch-replay를 선택할 때만</td><td>재적용 commit이 바뀔 때 새 revision</td></tr>
      </tbody>
    </table>
  </section>

  <details class="phase" open>
    <summary>
      <span class="phase-number">1</span>
      <span class="phase-title"><strong>Manifest 등록</strong><small>실제 commit diff를 BANK-OM 기능과 연결</small></span>
    </summary>
    <div class="phase-body">
      <p class="phase-lead">각 제목을 펼치면 실제 GitHub commit, 하나의 기능으로 묶은 이유와 Manifest 초안 전체를 볼 수 있습니다.</p>
      {''.join(sections)}
      <h3>Manifest 네 목록을 읽는 기준</h3>
      <div class="manifest-fields">
        <p><b>allowed_changed_paths</b>해당 BANK-OM commit이 실제로 변경한 전체 파일입니다.</p>
        <p><b>required_changed_paths</b>그 파일이 없거나 공식 원본과 같아지면 기능 미적용으로 바로 차단할 핵심 파일입니다.</p>
        <p><b>candidate_additional_paths</b>같은 BANK-OM의 후속 commit에서 처음 추가된 파일입니다.</p>
        <p><b>upgrade_watch.paths</b>공식 버전 변경 시 T42가 다시 비교할 해당 기능의 경로입니다.</p>
      </div>
    </div>
  </details>

  <details class="phase">
    <summary>
      <span class="phase-number">2</span>
      <span class="phase-title"><strong>검사 기준자료 등록</strong><small>Registry·Contracts·공용 파일·전체 변경 목록</small></span>
    </summary>
    <div class="phase-body">
      <p class="phase-lead">Git이 자동으로 만들 수 있는 값과 담당자가 결정해야 하는 기준을 나눠 등록합니다. 아래 코드는 작성 형태를 보여주는 예시이며, OM_TEMP 1.13.0의 실제 기준자료 파일 생성은 다음 작업입니다. 각 제목을 펼치면 의미·시점·실제 사용·예시·검사 결과를 확인할 수 있습니다.</p>
      {reference_sections}
    </div>
  </details>

  <details class="phase">
    <summary>
      <span class="phase-number">3</span>
      <span class="phase-title"><strong>로컬 검사 대상 연결</strong><small>OM_TEMP branch와 기준 commit 확인</small></span>
    </summary>
    <div class="phase-body">
      <p class="phase-lead">검사기는 로컬 Git repository를 읽습니다. 현재는 독립 snapshot의 commit 연결 방식을 보완한 뒤 전체 검사를 실행해야 합니다.</p>
      {connection_sections}
    </div>
  </details>

  <section class="foot"><strong>현재 상태:</strong> 실제 Git commit 기준 Manifest 초안 7개와 구조 검사는 완료했습니다. Registry·Contract·공용 파일·111개 목록의 실제 파일 생성, 독립 snapshot 연결 보완, 전체 코드 build, 업무 동작 test, 1.13.1 업그레이드 비교와 배포 승인은 아직 완료하지 않았습니다.</section>
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
