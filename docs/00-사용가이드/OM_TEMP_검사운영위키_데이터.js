window.WIKI_GATES = {
  t25r: {
    group: "소스·등록 검사",
    title: "T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
    question: "Git commit 기록을 잃고 특정 버전의 코드 폴더만 남았을 때, 공식 OpenMetadata 코드와 당시 등록자료를 이용해 그 코드 폴더와 동일한 파일들을 복구할 수 있는가?",
    status: "구현·단위 테스트 완료 · 현재 적용 예시인 OM_TEMP에는 공식 변경 기록이 있어 실행 대상 아님",
    statusLevel: "neutral",
    timing: "Git commit 기록이 유실되고 당시의 코드 폴더만 남은 비상 상황에서 T25 대신 실행합니다. OM_TEMP에는 공식 버전과 BANK-OM commit 기록이 모두 남아 있으므로 이 검사를 실행하지 않습니다.",
    inputs: [
      ["복구를 시작할 공식 코드", "BANK-OM을 적용하기 전의 공식 OpenMetadata commit", "공식 1.13.0 commit"],
      ["비교할 보관 코드", "Git 기록은 없지만 파일은 남아 있는 당시의 코드 폴더", "보관해 둔 제품 코드 폴더"],
      ["파일–BANK-OM 연결표", "각 파일에 어떤 BANK-OM 변경을 적용해야 하는지 알려주는 등록자료", "source-snapshot-path-owners.yaml"],
      ["공식 코드와 보관 코드의 차이 목록", "공식 코드와 보관 코드 사이에서 달라진 모든 파일 경로", "source-diff-paths.txt"]
    ],
    steps: [
      "공식 OpenMetadata 코드에서 시작해 파일–BANK-OM 연결표에 기록된 변경을 순서대로 적용합니다.",
      "복구한 코드와 보관 코드에 같은 파일이 있고 내용도 같은지 비교합니다.",
      "JSON은 공백·줄바꿈·항목 순서가 달라도 항목 경로와 값이 같으면 같은 내용으로 판단합니다.",
      "Java·TypeScript·Python 등 나머지 파일은 바이트 단위 내용이 같은지 확인합니다."
    ],
    verdicts: [
      ["PASS", "복구한 코드의 파일 목록과 내용이 보관 코드와 같습니다."],
      ["BLOCK", "누락·추가 파일이 있거나 파일 내용이 다릅니다."],
      ["ANALYSIS ERROR", "공식 코드, 보관 코드 또는 파일–BANK-OM 연결표가 없어 비교할 수 없습니다."]
    ],
    limit: "복구한 파일과 보관 파일이 같다는 사실만 확인합니다. 기능이 정상 동작하는지는 Contract test가 따로 확인합니다.",
    command: "# 현재 적용 예시인 OM_TEMP는 공식 commit 이력이 남아 있어 T25-R을 실행하지 않습니다.\n# 과거 snapshot만 남은 대상에 사용하는 T25-R 전용 CLI는 아직 제공되지 않습니다.\n# 구현의 단위 테스트만 확인하려면 다음 명령을 실행합니다.\n./.venv/bin/pytest -q harness/tests/test_vendor_rebuild.py",
    resultExample: "실행 상태 | 이번 대상에서는 실행하지 않음\n이 문장은 PASS·APPROVAL·BLOCK 같은 검사 판정이 아닙니다.\n현재 적용 예시인 OM_TEMP는 공식 1.13.0과 BANK-OM commit 이력을 보존하므로 T25로 출발점을 확인합니다.",
    output: "결과 파일에는 누락된 파일, 추가된 파일, 내용이 다른 파일이 기록됩니다. 복구 담당자는 이 목록을 보고 등록자료나 복구 순서 중 무엇을 고쳐야 하는지 판단합니다.",
    code: ["harness/acgh/vendor_rebuild.py", "harness/tests/test_vendor_rebuild.py"]
  },
  t25: {
    group: "소스·등록 검사",
    title: "T25 · 공식 버전 출발점 확인",
    question: "검사할 커스텀 브랜치가 우리가 선택한 공식 OpenMetadata 버전에서 만들어졌는가?",
    status: "구현·단위 테스트 완료 · 현재 적용 예시: OM_TEMP 1.13.0 재검증 결과 PASS",
    statusLevel: "pass",
    timing: "새 공식 버전과 BANK-OM 변경을 합쳐 커스텀 브랜치를 만든 뒤, 다른 소스 검사보다 먼저 실행합니다.",
    inputs: [
      ["Candidate lock", "업그레이드 전 공식 commit, 새 공식 commit, 검사할 커스텀 브랜치 commit을 기록한 검사 대상 고정 정보", "공식 f329dd4a… · 검사 대상 custom commit 3a2811cf…"],
      ["제품 코드 저장소", "Candidate lock에 적힌 세 commit과 그 연결 순서를 확인할 Git 저장소", "/workspace/product-repo"]
    ],
    steps: [
      "Candidate lock에 적힌 업그레이드 전 공식 commit, 새 공식 commit과 검사할 커스텀 브랜치 commit이 실제로 존재하는지 확인합니다.",
      "Git 기록에서 업그레이드 전 공식 commit 다음에 새 공식 commit이 이어지는지 확인합니다.",
      "Git 기록에서 새 공식 commit 다음에 검사할 커스텀 브랜치 commit이 이어지는지 확인합니다.",
      "현재 검사 중인 커스텀 브랜치 commit과 파일 내용이 Candidate lock에 기록된 값과 같은지 확인합니다."
    ],
    verdicts: [
      ["PASS", "검사할 커스텀 브랜치가 선택한 새 공식 버전에서 만들어졌고 Candidate lock과도 일치합니다."],
      ["BLOCK", "커스텀 브랜치가 선택한 공식 버전에서 만들어졌다는 Git 연결 기록이 없습니다."],
      ["ANALYSIS ERROR", "필요한 commit이 없거나 현재 코드와 Candidate lock이 달라 검사를 완료할 수 없습니다."]
    ],
    limit: "커스텀 브랜치의 출발점만 확인합니다. BANK-OM 기능이 남아 있고 정상 동작하는지는 T26과 기능 test가 따로 확인합니다.",
    command: "./.venv/bin/python harness/om_workflow.py source \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0",
    resultExample: "T25 | PASS\n검사할 커스텀 브랜치 commit 3a2811cf…가 공식 1.13.0 commit f329dd4a…에서 이어짐\n주의: 공식 버전 출발점만 확인한 결과이며, 기능 정상이나 운영 배포 완료를 뜻하지 않음",
    output: "source-gate-results.json의 T25 항목에 PASS·BLOCK·ANALYSIS ERROR와 그 이유가 기록됩니다. 담당자는 이 결과로 잘못된 공식 버전에서 만든 커스텀 브랜치를 검사하는 실수를 찾습니다.",
    code: ["harness/acgh/ancestry.py", "harness/tests/test_ancestry.py"]
  },
  t26: {
    group: "소스·등록 검사",
    title: "T26 · 필수 커스터마이징 유지 확인",
    question: "공식 새 버전을 적용한 뒤에도 모든 active BANK-OM 기능의 필수 코드와 Contract 연결이 남아 있는가?",
    status: "구현·단위 테스트 완료 · 현재 적용 예시: OM_TEMP 1.13.0 재검증 결과 PASS",
    statusLevel: "pass",
    timing: "vendor-merge 결과가 되는 검사 대상 custom branch commit이 만들어지고 Manifest·Registry·Contract가 준비된 뒤 실행합니다.",
    inputs: [
      ["Candidate lock", "공식 버전과 검사 대상 custom branch commit", "공식 f329dd4a… · 검사 대상 custom commit 3a2811cf…"],
      ["Manifest", "required_changed_paths, 전체 기대 경로, assurance", "BANK-OM-007 · .../tiberoConnection.json · CONTRACT-TIBERO-CONNECTOR"],
      ["Registry·Contract catalog", "active ID와 Contract·필수 test 연결", "BANK-OM-007 active → test_tibero.py::test_connection_schema_roundtrip"]
    ],
    steps: [
      "Registry에서 active BANK-OM ID를 가져옵니다.",
      "각 ID의 Manifest와 required_changed_paths가 비어 있지 않은지 확인합니다.",
      "필수 파일이 검사 대상 코드에 존재하고 공식 새 버전과 실제로 다른지 확인합니다.",
      "필수 이외의 등록 파일이 사라졌거나 공식 원본과 같아졌다면 담당자 검토 대상으로 표시합니다.",
      "Manifest가 가리키는 Contract가 실제로 있고, 그 Contract에도 같은 BANK-OM ID와 필수 test가 적혀 있는지 확인합니다."
    ],
    verdicts: [
      ["PASS", "모든 active 기능의 필수 코드와 Contract·test 연결이 확인됩니다."],
      ["APPROVAL", "필수로 지정하지 않은 등록 파일이 사라졌거나 공식 코드와 같아져 담당자 확인이 필요합니다."],
      ["BLOCK", "필수 파일, Manifest, Contract 또는 필수 test 연결이 없습니다."],
      ["ANALYSIS ERROR", "검사 대상 commit이나 Candidate lock을 신뢰할 수 없어 검사할 수 없습니다."]
    ],
    limit: "필수 파일이 존재하고 공식 원본과 다르다는 사실을 확인할 뿐, 그 코드가 올바르게 동작한다는 뜻은 아닙니다. T62 실행 결과가 필요합니다.",
    command: "./.venv/bin/python harness/om_workflow.py source \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0",
    resultExample: "T26 | PASS\nactive_customizations=7 · BANK-OM-007 필수 파일과 Contract 연결 확인",
    output: "통합 소스 검사 결과 source-gate-results.json의 T26 항목에 기능별 누락 여부가 남습니다. 기능 담당자와 배포 검토자가 BLOCK·APPROVAL 사유를 확인합니다.",
    code: ["harness/acgh/survival.py", "harness/tests/test_survival.py"]
  },
  t30: {
    group: "소스·등록 검사",
    title: "T30 · 커밋별 BANK-OM ID 확인",
    question: "공식 코드 영역을 변경한 각 commit에 정확히 하나의 등록된 BANK-OM ID가 있는가?",
    status: "구현·단위 테스트 완료 · 현재 적용 예시: OM_TEMP 1.13.0 재검증 결과 PASS",
    statusLevel: "pass",
    timing: "BANK-OM commit이 추가될 때마다, 검사 대상 custom branch commit에 대한 소스 검사에서 실행합니다.",
    inputs: [
      ["Git commit 이력", "공식 기준 이후의 각 commit 메시지와 변경 파일", "7d19c895… 본문: Customization-ID: BANK-OM-007"],
      ["코드 경로 분류표", "공식 코드·행내 거버넌스·알 수 없는 경로의 구분", "openmetadata-ui/** = 공식 코드 영역"],
      ["Manifest 목록", "사용 가능한 BANK-OM ID", "BANK-OM-001.yaml ~ BANK-OM-007.yaml"]
    ],
    steps: [
      "공식 기준 이후의 commit을 하나씩 읽습니다.",
      "각 commit에서 변경된 경로를 공식 코드, 거버넌스 코드 또는 알 수 없는 경로로 분류합니다.",
      "공식 코드 경로를 바꾼 commit의 본문에서 Customization-ID 항목을 읽습니다.",
      "ID가 없거나 여러 개인지, 공식 코드와 거버넌스 코드를 한 commit에 섞었는지 확인합니다."
    ],
    verdicts: [
      ["PASS", "공식 코드를 변경한 각 commit에 정확히 하나의 ID가 있습니다."],
      ["BLOCK", "ID 누락·중복, 빈 commit, 허용하지 않은 merge commit 또는 코드 영역 혼합이 있습니다."],
      ["ANALYSIS ERROR", "어느 영역인지 판단할 수 없는 경로가 있습니다."]
    ],
    limit: "ID가 있다고 해서 commit의 업무 목적이 한 가지라는 사실까지 자동으로 알 수는 없습니다. commit 리뷰가 필요합니다.",
    command: "git commit -m \"InstanceCode 기능 추가\" \\\n  -m \"Customization-ID: BANK-OM-001\"\n\n./.venv/bin/python harness/om_workflow.py source \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0",
    resultExample: "T30 | PASS\ncommit 7d19c895…에서 등록된 ID BANK-OM-007 하나를 확인",
    output: "통합 소스 검사 결과 source-gate-results.json의 T30 항목에 문제가 있는 commit과 ID가 남습니다. 변경 작성자와 변경관리 담당자가 commit 메시지를 수정할지 판단합니다.",
    code: ["harness/acgh/invariants.py", "harness/tests/test_invariants.py"]
  },
  t31: {
    group: "소스·등록 검사",
    title: "T31 · BANK-OM 적용 순서 확인",
    question: "같은 ID의 여러 commit과 기능 간 선행 관계가 Manifest에 등록한 순서를 지키는가?",
    status: "구현·단위 테스트 완료 · 현재 적용 예시: OM_TEMP 1.13.0 재검증 결과 PASS",
    statusLevel: "pass",
    timing: "같은 BANK-OM ID의 후속 commit이나 depends_on 관계가 추가될 때 실행합니다.",
    inputs: [
      ["Git commit 이력", "commit별 Customization-ID와 순서", "62e39da8… → 7d19c895… 모두 BANK-OM-007"],
      ["Manifest", "series.allowed와 series.depends_on", "allowed: true · depends_on: []"],
      ["Registry", "active·retired ID 상태", "BANK-OM-007 status: active"]
    ],
    steps: [
      "commit을 BANK-OM ID별로 묶습니다.",
      "한 ID가 여러 commit에 쓰였다면 series.allowed가 true인지 확인합니다.",
      "같은 ID의 commit이 중간에 다른 ID로 끊겼다가 다시 나타나는지 확인합니다.",
      "depends_on 관계에 순환이 있는지와 retired ID가 재사용됐는지 확인합니다."
    ],
    verdicts: [
      ["PASS", "후속 commit과 선행 관계가 등록 규칙을 지킵니다."],
      ["BLOCK", "승인되지 않은 여러 commit, 비연속 series, 의존 관계 순환 또는 retired ID 재사용이 있습니다."]
    ],
    limit: "Manifest에 선행 관계 자체를 빠뜨리면 검사기가 업무 관계를 새로 추론하지 못합니다.",
    command: "./.venv/bin/python harness/om_workflow.py source \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0",
    resultExample: "T31 | PASS\nBANK-OM-007의 두 commit 순서와 series.allowed=true를 확인",
    output: "source-gate-results.json의 T31 항목에는 잘못된 적용 순서와 후속 변경 묶음 번호가 기록됩니다. 변경관리 담당자는 Manifest를 확인하고, patch-replay 전략을 쓰는 경우에만 Patch-lock도 확인합니다.",
    code: ["harness/acgh/invariants.py", "harness/tests/test_invariants.py"]
  },
  t40: {
    group: "소스·등록 검사",
    title: "T40 · 변경 파일 범위 확인",
    question: "각 BANK-OM commit이 Manifest에 등록한 파일만 변경했고, 최종 검사 대상 custom branch commit에 필수 변경이 반영됐는가?",
    status: "구현·단위 테스트 완료 · 현재 적용 예시: OM_TEMP 1.13.0 재검증 결과 PASS",
    statusLevel: "pass",
    timing: "Manifest 초안을 만든 뒤와 새로운 후속 commit이 추가될 때마다 실행합니다.",
    inputs: [
      ["Git diff", "BANK-OM commit별 실제 변경 파일과 최종 검사 대상 custom branch commit의 공식 원본 대비 차이", "BANK-OM-007 두 commit의 8개 + 2개 파일"],
      ["Manifest", "changed_paths, required_changed_paths", "changed_paths 10개 · required .../tiberoConnection.json"],
      ["코드 경로 분류표", "검사할 코드 영역", "openmetadata-spec/**, openmetadata-ui/**"]
    ],
    steps: [
      "commit별 실제 변경 파일과 Manifest의 현재 변경 범위를 비교합니다.",
      "Manifest에 없는 파일을 commit이 변경했는지 확인합니다.",
      "required_changed_paths가 현재 변경 범위에 포함되는지 확인합니다.",
      "최종 검사 대상 custom branch commit에서 필수 파일이 공식 새 버전과 실제로 다른지 확인합니다."
    ],
    verdicts: [
      ["PASS", "실제 변경 파일이 등록 범위와 같고 필수 변경이 최종 검사 대상 custom branch commit에 있습니다."],
      ["APPROVAL", "Manifest에는 등록했지만 실제 commit에서 변경하지 않은 비필수 파일이 있습니다."],
      ["BLOCK", "등록하지 않은 파일을 변경했거나 필수 변경이 최종 검사 대상 custom branch commit에 없습니다."],
      ["ANALYSIS ERROR", "변경 파일이 어느 코드 영역에 속하는지 판정할 수 없습니다."]
    ],
    limit: "파일 단위 검사입니다. 허용된 파일 안의 잘못된 코드 줄은 코드 리뷰와 test로 확인해야 합니다.",
    command: "./.venv/bin/python harness/om_workflow.py source \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0",
    resultExample: "T40 | PASS\nBANK-OM-007 실제 변경 10개 = Manifest changed_paths 10개",
    output: "통합 소스 검사 결과 source-gate-results.json의 T40 항목에 등록 밖 변경과 누락된 필수 경로가 남습니다. 기능 담당자가 코드와 Manifest 중 잘못된 쪽을 고칩니다.",
    code: ["harness/acgh/drift.py", "harness/tests/test_drift.py"]
  },
  t41: {
    group: "소스·등록 검사",
    title: "T41 · 중요 시스템 경로 확인",
    question: "보안·인증·설정·DB처럼 별도 검토가 필요한 경로를 BANK-OM commit이 변경했는가?",
    status: "검사 구현·단위 테스트 완료 · 1.13.0 소스 재검사 결과는 PASS · 1.13.1 운영 배포 대상 코드는 재검증 필요",
    statusLevel: "approval",
    timing: "검사 대상 custom branch commit의 소스 검사에서 실제 변경 파일을 분류할 때 실행합니다.",
    inputs: [
      ["실제 변경 파일", "공식 기준 이후 BANK-OM commit의 경로", "bootstrap/sql/migrations/.../schemaChanges.sql"],
      ["중요 경로 정책(Sensitive zones)", "변경 금지(frozen), 사전 승인 필요(protected), 결과 표시 필요(watched) 경로", "watched: bootstrap/sql/migrations/**"],
      ["Change intent", "허용된 중요 변경 사유와 승인 정보가 있는 경우", "BANK-OM-001 schema migration 승인 참조"]
    ],
    steps: [
      "변경 파일을 중요 경로 정책과 비교합니다.",
      "변경 금지, 사전 승인 필요, 결과 표시 필요 중 어디에 해당하는지 확인합니다.",
      "사전 승인이 필요한 변경이라면 변경 사유와 승인 정보가 있는지 확인합니다."
    ],
    verdicts: [
      ["PASS", "중요 경로 변경이 없거나 필요한 조건을 충족했습니다."],
      ["APPROVAL", "사전 승인 또는 결과 표시가 필요한 경로를 변경해 담당자 검토가 필요합니다."],
      ["BLOCK", "변경 금지 경로를 수정했거나 필요한 승인 정보를 제출하지 않았습니다."],
      ["ANALYSIS ERROR", "경로를 규칙에 따라 분류할 수 없습니다."]
    ],
    limit: "파일 경로만 비교합니다. 코드 내부 구조를 분석하거나 보안 취약점을 찾지는 않습니다.",
    command: "./.venv/bin/python harness/om_workflow.py source \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0",
    resultExample: "T41 | PASS (1.13.0 검사 대상 custom commit 3a2811cf…)\nMySQL·PostgreSQL migration 2개는 watched 경로로 표시됐지만 현재 정책이 visibility_only라 자동 차단하지 않음\n2026-07-30 문서 상태 | APPROVAL · 1.13.1 운영 배포 대상 custom commit을 만들면 같은 정책으로 다시 실행해야 함",
    output: "통합 소스 검사 결과 source-gate-results.json의 T41 항목에 민감 경로와 필요한 승인 수준이 남습니다. 보안·DB·플랫폼 담당자 중 해당 경로 책임자가 확인합니다.",
    code: ["harness/acgh/zones.py", "harness/tests/test_zones.py"]
  },
  t42: {
    group: "업그레이드 영향 검사",
    title: "T42 · 공식 변경 영향 확인",
    question: "새 공식 OpenMetadata 버전이 BANK-OM 기능과 관련된 파일을 변경했는가?",
    status: "검사 구현·단위 테스트 완료 · 1.13.1 영향 진단 기록 있음 · 실제 운영 배포 대상 custom branch를 병합하기 전에 재실행 필요",
    statusLevel: "approval",
    timing: "새 공식 버전을 OpenMetadata 포크 브랜치에 준비한 뒤, 커스터마이징 병합 전에 실행합니다.",
    inputs: [
      ["공식 이전·새 버전 commit", "공식 A→B 사이의 Git 변경 파일", "f329dd4a…(1.13.0) → afcb2d2…(1.13.1)"],
      ["Manifest", "upgrade_watch.paths와 watch_dependencies", "BANK-OM-001 · .../Entity.java"],
      ["직접 참조 가능성이 있는 경로", "watch_suggest.py가 발견해 담당자에게 검토를 요청하는 경로", ".../SearchIndexFactory.java · InstanceCode 참조"]
    ],
    steps: [
      "Git에서 공식 이전 버전과 새 버전 사이의 변경 파일 목록을 구합니다.",
      "각 Manifest의 upgrade_watch.paths와 공식 변경 파일을 비교합니다.",
      "겹친 경로가 있으면 BANK-OM ID와 검토할 경로를 결과에 기록합니다.",
      "직접 참조 가능성이 있는 경로는 자동 승인하지 않고 담당자에게 제시합니다."
    ],
    verdicts: [
      ["PASS", "등록된 관련 경로가 공식 버전에서 바뀌지 않았습니다."],
      ["APPROVAL", "관련 경로가 공식 버전에서도 변경돼 재적용 전 검토가 필요합니다."],
      ["ANALYSIS ERROR", "공식 commit 또는 경로 규칙을 읽지 못했습니다."]
    ],
    limit: "APPROVAL은 Git 충돌이 이미 발생했다는 뜻이 아닙니다. 파일 경로는 다르지만 실행 중 서로 연결되는 코드까지 모두 찾지는 못합니다.",
    command: "./.venv/bin/python harness/om_workflow.py watch \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0 \\\n  --target <새-공식-버전-commit>",
    resultExample: "T42 | APPROVAL\nBANK-OM-001 watch 경로 .../Entity.java가 공식 1.13.1에서도 변경됨",
    output: "upgrade-watch-results.json의 affected_customizations에는 영향받을 수 있는 BANK-OM ID와 공식 버전에서도 바뀐 경로가 기록됩니다. 기능 담당자는 공식 변경 내용과 커스터마이징 연결 부분을 확인합니다.",
    code: ["harness/acgh/upgrade_watch.py", "harness/acgh/watch_suggest.py", "harness/tests/test_upgrade_watch.py"]
  },
  t43: {
    group: "업그레이드 영향 검사",
    title: "T43 · 커스터마이징 유지 부담 확인",
    question: "커스터마이징 규모와 공유 파일·충돌률이 조직이 정한 유지 한도를 넘었는가?",
    status: "검사 구현 완료 · 실제 충돌 증거 자동 연결은 보완 대상",
    statusLevel: "approval",
    timing: "새 공식 버전과의 영향·충돌 분석이 끝난 뒤 실행합니다.",
    inputs: [
      ["Manifest·Git diff", "활성 기능 수, 변경 줄 수, 한 파일을 함께 수정한 BANK-OM ID의 최대 수", "비교 기준 검사 대상 코드 예시: Core 변경 11개 · 12,488줄 · 한 파일에 연결된 ID 최대 4개"],
      ["Debt policy", "경고·차단 한도", "변경 줄 수 soft 14,000 · hard 18,000"],
      ["충돌률", "현재는 실행 인자로 전달하며 실제 병합 결과 자동 계산은 추가 개발 대상", "예시 입력: --conflict-rate 0.12"]
    ],
    steps: [
      "활성 커스터마이징 수와 실제 변경 줄 수를 계산합니다.",
      "여러 BANK-OM이 함께 수정한 파일 수를 계산합니다.",
      "전달받은 충돌률과 각 값을 정책 한도와 비교합니다."
    ],
    verdicts: [
      ["PASS", "모든 유지 부담 지표가 허용 범위입니다."],
      ["APPROVAL", "경고 한도를 넘어 구조 개선 검토가 필요합니다."],
      ["BLOCK", "조직이 정한 차단 한도를 넘었습니다."],
      ["ANALYSIS ERROR", "필요한 diff나 정책 값을 계산할 수 없습니다."]
    ],
    limit: "현재 충돌률을 실제 vendor-merge 기록에서 자동 계산하지 않으므로, 전달한 값의 출처를 별도 증거로 확인해야 합니다.",
    command: "./.venv/bin/python harness/om_workflow.py risk \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0 \\\n  --target <새-공식-버전-commit> \\\n  --conflict-rate <실제-충돌률>",
    resultExample: "T43 | APPROVAL (판정 예시)\nchanged_lines=14,500이 soft 기준 14,000을 초과 · 구조 개선 검토",
    output: "업그레이드 위험 검사 JSON의 T43 항목과 debt_metrics에 계산값과 기준 초과 이유가 남습니다. 기술 책임자가 유지 부담을 수용할지 구조 개선할지 결정합니다.",
    code: ["harness/acgh/debt.py", "harness/tests/test_debt.py"]
  },
  t93_scope: {
    group: "소스·등록 검사",
    title: "T93-범위 · 실제 변경과 Manifest 일치 확인",
    question: "BANK-OM ID별 실제 변경 파일이 Manifest에 빠짐없이 정확하게 등록됐는가?",
    status: "구현·단위 테스트 완료 · 현재 적용 예시: OM_TEMP 1.13.0 재검증 결과 PASS",
    statusLevel: "pass",
    timing: "Manifest 생성·갱신 직후와 검사 대상 custom branch commit의 소스 검사 때 실행합니다.",
    inputs: [
      ["Git commit 이력", "BANK-OM ID별 실제 변경 파일", "BANK-OM-007: 62e39da8… 8개 + 7d19c895… 2개"],
      ["Manifest", "changed_paths", "BANK-OM-007 changed_paths 10개"]
    ],
    steps: [
      "commit 메시지의 BANK-OM ID로 실제 변경 파일을 묶습니다.",
      "같은 ID의 모든 commit에서 나온 경로 합집합과 Manifest changed_paths를 비교합니다.",
      "실제 변경했지만 등록하지 않은 경로와, 등록했지만 실제로 변경하지 않은 경로를 모두 확인합니다."
    ],
    verdicts: [
      ["PASS", "실제 변경 파일과 등록 범위가 일치합니다."],
      ["APPROVAL", "등록했지만 실제 변경에서 확인되지 않은 비필수 경로가 있습니다."],
      ["BLOCK", "실제 변경했지만 등록하지 않은 경로가 있습니다."],
      ["ANALYSIS ERROR", "경로 분류나 commit 분석을 완료할 수 없습니다."]
    ],
    limit: "경로가 같다는 사실만 확인하며, Manifest에 적은 업무 설명의 정확성은 사람이 검토합니다.",
    command: "./.venv/bin/python harness/om_workflow.py validate \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0\n\n./.venv/bin/python harness/om_workflow.py source \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0",
    resultExample: "T93-범위 | PASS\nBANK-OM-007 Git 변경 10개 = Manifest 등록 10개 · 공용 파일에 연결된 BANK-OM ID 일치",
    output: "등록 검증 결과 registration-validation-results.json과 통합 소스 검사 결과에 ID별 실제 경로·등록 경로 비교가 남습니다. Manifest 작성자와 리뷰어가 확인합니다.",
    code: ["harness/acgh/drift.py", "harness/registrations/om-temp-1.13.0/validate_registration_bundle.py"]
  },
  t93_policy: {
    group: "업그레이드 영향 검사",
    title: "T93-정책 · 검사 경로 최신성 확인",
    question: "공식 파일 이동이나 모듈 추가로 기존 경로 정책과 watch 규칙이 낡았는가?",
    status: "검사 구현 완료 · 현재 적용 예시인 OM_TEMP의 source-gate-results.json에는 T93-정책 실행 결과 없음",
    statusLevel: "approval",
    timing: "공식 새 버전의 구조 변경을 분석할 때 실행합니다.",
    inputs: [
      ["공식 이전·새 버전", "파일 이동·삭제·추가 정보", "f329dd4a…(1.13.0) → afcb2d2…(1.13.1)"],
      ["Manifest·경로 정책", "watch, 코드 경로 분류표와 민감 경로 규칙", ".../Entity.java · upstream_owned_roots: openmetadata-service/**"]
    ],
    steps: [
      "기존 watch 경로가 새 공식 버전에도 존재하는지 확인합니다.",
      "공식 변경으로 경로가 이동·삭제됐는지 확인합니다.",
      "새로운 관련 모듈 때문에 기존 규칙이 변경을 놓칠 가능성이 있는지 표시합니다."
    ],
    verdicts: [
      ["PASS", "기존 검사 경로가 새 공식 버전에서도 유효합니다."],
      ["APPROVAL", "경로 이동·삭제 또는 구조 변경으로 정책 갱신 검토가 필요합니다."],
      ["ANALYSIS ERROR", "공식 버전이나 경로 정책을 읽지 못했습니다."]
    ],
    limit: "경로와 직접 참조를 중심으로 확인합니다. 의미상 새로 생긴 의존 관계는 담당자가 추가해야 할 수 있습니다.",
    command: "./.venv/bin/python harness/om_workflow.py risk \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0 \\\n  --target <새-공식-버전-commit> \\\n  --conflict-rate <실제-충돌률>",
    resultExample: "T93-정책 | APPROVAL (판정 예시)\n등록된 watch 파일이 공식 새 버전에서 이동됨 · Manifest 경로 재검토",
    output: "업그레이드 위험 검사 JSON의 T93-정책 항목에 이동·삭제된 watch 경로와 오래된 경로 정책이 남습니다. 플랫폼 담당자와 Manifest 담당자가 갱신 여부를 확인합니다.",
    code: ["harness/acgh/policy_drift.py", "harness/tests/test_policy_drift.py"]
  },
  t60i: {
    group: "테스트·실행 검사",
    title: "T60-I · 필수 테스트 코드 존재 확인",
    question: "Contract에 등록한 필수 test의 파일과 Python 함수가 실제 검사기 저장소에 존재하는가?",
    status: "Python pytest 확인 구현 완료 · 현재 적용 예시: OM_TEMP 1.13.0 재검증 결과 PASS · Java·TypeScript test 연결은 추가 개발 대상",
    statusLevel: "approval",
    timing: "Contract를 등록·갱신한 뒤와 Runtime test 실행 전에 실행합니다.",
    inputs: [
      ["Manifest", "assurance.contracts와 direct_tests", "BANK-OM-005 → CONTRACT-KOREAN-IME"],
      ["Contract catalog", "required_tests의 pytest 선택자", "tests/.../test_korean_ime.py::test_hangul_composition_roundtrip"],
      ["검사기 저장소", "실제 Python test 파일과 함수", "현재 적용 예시: easyseop/openmetadata-test의 test_korean_ime.py"]
    ],
    steps: [
      "Manifest가 참조하는 Contract ID를 찾습니다.",
      "Contract의 required_tests 선택자를 파일 경로와 함수 이름으로 분리합니다.",
      "Python 문법 분석기로 파일 안의 함수 이름을 읽어 지정한 test 함수가 실제로 있는지 확인합니다.",
      "Manifest가 Contract를 가리키고 Contract도 같은 BANK-OM ID를 가리키는지 확인합니다."
    ],
    verdicts: [
      ["PASS", "등록한 Python test 파일과 함수가 모두 존재합니다."],
      ["BLOCK", "Contract, test 파일 또는 test 함수가 없습니다."],
      ["ANALYSIS ERROR", "Python 파일 문법을 읽을 수 없거나 입력 형식이 잘못됐습니다."]
    ],
    limit: "test가 존재한다는 사실만 확인합니다. 실행 성공은 T62가 확인하며 Java JUnit·TypeScript Jest는 현재 직접 확인하지 않습니다.",
    command: "./.venv/bin/python harness/om_workflow.py validate \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0",
    resultExample: "T60-I | PASS\nCONTRACT-KOREAN-IME의 Python test 파일과 함수가 실제로 존재함",
    output: "등록 검증 결과 registration-validation-results.json의 “필수 테스트 코드 존재” 항목에 누락 여부가 남습니다. Contract 작성자와 테스트 담당자가 확인합니다.",
    code: ["harness/acgh/contracts.py", "harness/tests/test_contracts.py"]
  },
  t61: {
    group: "테스트·실행 검사",
    title: "T61 · 커스터마이징 제거 시 테스트 실패 확인",
    question: "BANK-OM 변경을 제거한 상태에서는 해당 기능의 필수 test가 실제로 실패하는가?",
    status: "검사 엔진 구현 완료 · 현재 적용 예시인 OM_TEMP용 patch-kill-plan.yaml 작성과 환경 실행은 아직 필요",
    statusLevel: "approval",
    timing: "Contract test가 준비된 뒤, 테스트가 커스터마이징을 실제로 보호하는지 확인할 때 실행합니다.",
    inputs: [
      ["Patch-kill plan", "제거할 BANK-OM ID, 대상 파일·패치와 예상 실패 test", "BANK-OM-005 제거 → test_hangul_composition_roundtrip 실패 예상"],
      ["Candidate lock", "변경을 제거하기 전에 검사할 custom branch commit과 배포 파일을 고정한 자료", "형식 예시: 검사 대상 commit <실행 대상 SHA> · 배포 파일 <내용 확인값>"],
      ["Test 결과", "BANK-OM 변경을 넣었을 때와 뺐을 때의 test 결과", "정상 검사 대상 코드 pass · BANK-OM-005 제거 상태 fail"]
    ],
    steps: [
      "BANK-OM 변경이 들어 있는 정상 검사 대상 custom branch commit에서 필수 test가 성공하는지 확인합니다.",
      "대상 BANK-OM 변경만 제거한 비교 상태를 만듭니다.",
      "등록한 필수 test를 다시 실행합니다.",
      "제거 상태에서 모든 목표 test가 실패하는지 확인합니다."
    ],
    verdicts: [
      ["PASS", "정상 검사 대상 custom branch commit에서는 성공하고 변경 제거 상태에서는 목표 test가 실패합니다."],
      ["BLOCK", "변경을 제거해도 test가 성공하거나 목표 test를 실행하지 못했습니다."],
      ["ANALYSIS ERROR", "제거 상태나 실행 결과가 Candidate lock에 기록된 검사 대상 custom branch commit과 연결되지 않습니다."]
    ],
    limit: "실패했다는 사실만으로 실패 원인이 정확히 기능 제거 때문인지 단정하기 어렵습니다. 오류 종류·메시지를 함께 검토해야 합니다.",
    command: "# 먼저 버전 등록 폴더의 patch-kill-plan.yaml에 제거할 BANK-OM과\n# 실패해야 할 필수 test를 담당자가 등록해야 합니다. 현재 이 파일은 없습니다.\n./.venv/bin/python harness/om_workflow.py patch-kill \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0",
    resultExample: "T61 | PASS (실행 결과 형식 예시)\n정상 검사 대상 custom commit PASS · BANK-OM-005 제거 상태에서 목표 test FAIL\n주의: 현재 OM_TEMP용 patch-kill 계획과 실행 증거는 아직 없음",
    output: "소스 제거 결과는 source-patch-kill-result.yaml에, 실행 환경의 제거 결과는 acgh-result.yaml에 기록됩니다. 두 파일에는 정상 상태와 변경 제거 상태의 test 결과가 함께 남으며, 기능 담당자가 예상한 이유로 실패했는지 확인합니다.",
    code: ["harness/acgh/patchkill.py", "harness/tests/test_patchkill.py"]
  },
  t62: {
    group: "테스트·실행 검사",
    title: "T62 · 테스트 결과와 검사 대상 commit 연결 확인",
    question: "필수 test가 정확히 검사 대상으로 고정한 commit과 배포 파일에서 실행됐는가?",
    status: "실행기·단위 테스트 완료 · 실제 행내 환경 실행 대기",
    statusLevel: "approval",
    timing: "테스트 환경에 검사 대상 코드를 배포하고 Contract test를 실행할 때마다 수행합니다.",
    inputs: [
      ["Candidate lock", "검사할 코드와 그 코드로 만든 배포 파일을 고정한 자료", "형식 예시: <실행 대상 SHA> · <배포 파일 내용 확인값>"],
      ["Test run set", "실행한 test, 시도 번호, 결과와 test 묶음 버전", "test_tibero.py::test_connection_schema_roundtrip · 1차 시도 · pass"],
      ["Manifest·Contract·Registry", "필수 test와 기능 중요도", "BANK-OM-007 · CONTRACT-TIBERO-CONNECTOR · high"]
    ],
    steps: [
      "Test run set에 적힌 코드와 배포 파일이 Candidate lock에 고정한 대상과 같은지 확인합니다.",
      "검사기 버전과 test 묶음 버전이 승인한 값과 같은지 확인합니다.",
      "모든 active BANK-OM의 필수 test가 실행 목록에 있는지 확인합니다.",
      "SKIP·FAIL·ERROR와 재시도 이력을 숨기지 않고 판정합니다."
    ],
    verdicts: [
      ["PASS", "필수 test가 Candidate lock에 기록된 같은 검사 대상 custom branch commit에서 누락 없이 성공했습니다."],
      ["APPROVAL", "high·critical 기능이 실패 후 재시도에서 성공해 불안정성 검토가 필요합니다."],
      ["BLOCK", "필수 test 누락·SKIP·FAIL·ERROR가 있습니다."],
      ["ANALYSIS ERROR", "검사한 코드·배포 파일·검사기·test 묶음 버전이 서로 맞지 않습니다."]
    ],
    limit: "등록된 test만 확인합니다. Contract가 다루지 않은 업무 동작까지 자동으로 보장하지 않습니다.",
    command: "./.venv/bin/python harness/om_workflow.py runtime \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0 \\\n  --artifact /path/to/deployment-file",
    resultExample: "T62 | PASS (형식 예시)\n<실행 대상 SHA>와 <실제 artifact digest>에서 BANK-OM-007 필수 test 성공\n주의: 현재 OM_TEMP 행내 Runtime 실행 결과는 아직 없음",
    output: "각 실행의 증거 폴더에는 test-run-set.yaml과 acgh-result.yaml이 새로 생깁니다. 기능 담당자와 배포 검토자는 검사한 코드·배포 파일이 맞는지와 test 결과를 확인합니다.",
    code: ["harness/acgh/testruns.py", "harness/acgh/pytest_runs.py", "harness/tests/test_testruns.py"]
  },
  t63: {
    group: "테스트·실행 검사",
    title: "T63 · TypeScript 오류 증가 확인",
    question: "공식 OpenMetadata commit과 비교해 검사 대상 custom branch commit에 새 TypeScript 오류가 추가됐는가?",
    status: "비교 도구 구현 완료 · 전체 환경 로그 결속 보완 대상",
    statusLevel: "approval",
    timing: "공식 OpenMetadata commit과 검사 대상 custom branch commit에서 같은 TypeScript 검사를 각각 실행한 뒤 사용합니다.",
    inputs: [
      ["공식 원본 typecheck 로그", "파일 경로·오류 코드별 발생 정보와 종료 코드", "upstream.log · TS2322 3건 · exit 2"],
      ["검사 대상 custom branch commit의 typecheck 로그", "같은 명령으로 실행한 결과와 종료 코드", "candidate.log · TS2322 3건 · exit 2"]
    ],
    steps: [
      "두 로그의 파일 경로와 오류 코드를 같은 표기 방식으로 맞춥니다.",
      "같은 경로·오류 코드의 발생 횟수를 비교합니다.",
      "검사 대상 custom branch commit에서 새로 생기거나 증가한 오류를 찾습니다."
    ],
    verdicts: [
      ["PASS", "검사 대상 custom branch commit에 공식 OpenMetadata commit보다 새 TypeScript 오류가 없습니다."],
      ["BLOCK", "새 오류 또는 오류 횟수 증가가 있습니다."],
      ["ANALYSIS ERROR", "로그 형식이나 실행 정보가 비교 가능하지 않습니다."]
    ],
    limit: "TypeScript 오류만 비교합니다. Node·Yarn 버전과 로그 전체의 내용 확인값을 결과에 자동 연결하는 기능은 아직 없습니다.",
    command: "./.venv/bin/python harness/om_workflow.py typecheck \\\n  --upstream-log /path/to/upstream.log \\\n  --candidate-log /path/to/candidate.log \\\n  --upstream-exit <공식-typecheck-종료코드> \\\n  --candidate-exit <커스텀-typecheck-종료코드>",
    resultExample: "T63 | PASS (비교 예시)\n공식 OpenMetadata commit 3건 · 검사 대상 custom commit 3건 · 새 TypeScript 오류 0건",
    output: "TypeScript 비교 명령의 JSON 표준 출력에 공식·행내 오류 수와 새 오류 목록이 남습니다. 프론트엔드 담당자가 로그의 실행 환경과 새 오류를 확인합니다.",
    code: ["harness/compare_ui_typecheck.py", "harness/tests/test_tsc_baseline.py"]
  },
  t90: {
    group: "업그레이드·배포 검사",
    title: "T90 · 업그레이드 전 과정 결과 확인",
    question: "데이터 복원, DB 변경, 검색 색인, 수집, 권한, API, 검색, 이전 버전 복귀 등 필수 업그레이드 단계를 모두 실행해 통과했는가?",
    status: "판정 모듈·스키마 구현 완료 · 실제 행내 업그레이드 실행 증거 대기",
    statusLevel: "approval",
    timing: "실제와 유사한 테스트 환경에서 검사 대상 release commit의 업그레이드 연습을 수행한 뒤 실행합니다.",
    inputs: [
      ["업그레이드 실행 결과", "이전·새 버전, 검사 대상과 12개 필수 단계의 결과", "형식 예시: 1.13.0 → 1.13.1 · DB 변경/검색/이전 버전 복귀 등 12개 모두 pass"],
      ["Candidate lock", "검사할 코드와 배포 파일을 고정한 자료", "형식 예시: <실행 대상 SHA> · <배포 파일 내용 확인값>"],
      ["Test run set", "같은 검사 대상에서 실행한 Contract test 결과의 내용 확인값", "환경 실행 예시: sha256:04bd…"]
    ],
    steps: [
      "업그레이드 결과가 Candidate lock에 고정한 코드와 배포 파일에서 나온 것인지 확인합니다.",
      "연결된 Test run set의 내용 확인값이 실제 test 결과와 같은지 확인합니다.",
      "정해진 12개 단계가 모두 있고 각 결과가 pass인지 확인합니다. 결과 파일에서는 운영 데이터 복원(restore-production-snapshot), DB 변경 적용(migration), 데이터 건수 대조(row-reconciliation), 검색 인덱스 재생성(reindex), 메타데이터 수집 확인(ingestion), 로그인 동작 비교(differential-authentication), 권한 동작 비교(differential-authorization), API 동작 비교(differential-api), 관계 정보 비교(differential-relations), 검색 결과 비교(differential-search), 수집 결과 비교(differential-ingestion), 되돌리기 연습(rollback-drill)이라는 실제 단계 ID를 사용합니다."
    ],
    verdicts: [
      ["PASS", "Candidate lock에 기록된 같은 검사 대상 release commit에서 12개 필수 업그레이드 단계가 모두 성공했습니다."],
      ["BLOCK", "필수 단계가 없거나 pass가 아닙니다."],
      ["ANALYSIS ERROR", "검사한 코드·배포 파일·Test run set의 연결이 맞지 않거나 결과 형식이 잘못됐습니다."]
    ],
    limit: "결과 파일의 형식과 검사 대상의 일치 여부를 확인합니다. 각 단계를 실제로 실행했다는 사실을 외부 로그나 전자서명으로 확인하는 기능은 아직 연결하지 않았습니다.",
    command: "현재는 실행 시스템이 만든 upgrade-test-run.yaml을\nharness/acgh/upgrade_run.py의 check_upgrade_run()에 전달합니다.",
    resultExample: "T90 | PASS (형식 예시)\n<실행 대상 SHA>에서 필수 업그레이드 단계 12/12 PASS\nrestore-production-snapshot=pass · migration=pass · row-reconciliation=pass\nreindex=pass · ingestion=pass · differential-authentication=pass\ndifferential-authorization=pass · differential-api=pass · differential-relations=pass\ndifferential-search=pass · differential-ingestion=pass · rollback-drill=pass\n주의: 현재 OM_TEMP 행내 업그레이드 실행 결과는 아직 없음",
    output: "실행 시스템은 upgrade-test-run.yaml과 판정이 들어 있는 acgh-result.yaml을 보관합니다. 업그레이드 책임자는 12개 단계가 같은 코드와 배포 파일에서 실행됐는지 확인합니다.",
    code: ["harness/acgh/upgrade_run.py", "harness/acgh/schema/upgrade-test-run.schema.json", "harness/tests/test_upgrade_run.py"]
  },
  t91: {
    group: "업그레이드·배포 검사",
    title: "T91 · 검증 대상과 배포 대상 일치 확인",
    question: "검사한 commit·이미지·Helm 설정을 다시 만들지 않고 그대로 배포하는가?",
    status: "판정 모듈·스키마 구현 완료 · 실제 배포 환경 결속 대기",
    statusLevel: "approval",
    timing: "모든 필수 검사가 끝난 뒤 배포 승격 직전에 실행합니다.",
    inputs: [
      ["Release lock", "검사한 코드·정책·검사기·test 묶음·결과·이미지·Helm 설정을 한 배포 대상으로 묶은 자료", "형식 예시: candidate <검증 SHA> · image <검증 내용 확인값>"],
      ["Candidate lock·Test run set·검사 결과", "검증한 대상의 고정값", "형식 예시: 세 파일 모두 같은 <검증 SHA>"],
      ["실제 배포 정보", "배포할 commit, 이미지와 Helm 설정의 내용 확인값, 재빌드 여부", "형식 예시: <검증 SHA> · <검증 내용 확인값> · rebuilt=false"]
    ],
    steps: [
      "Release lock이 Candidate lock, 검사 결과, Test run set과 같은 검사 대상을 가리키는지 확인합니다.",
      "검증한 이미지·Helm 설정의 내용 확인값을 실제 배포 정보와 비교합니다.",
      "검증이 끝난 뒤 배포 파일을 다시 만들었는지 확인합니다."
    ],
    verdicts: [
      ["PASS", "검증한 동일 배포 파일을 다시 만들지 않고 배포합니다."],
      ["BLOCK", "이미지·Helm·commit이 다르거나 검증 후 재빌드했습니다."],
      ["ANALYSIS ERROR", "Release lock과 검사 증거의 연결이 오래됐거나 손상됐습니다."]
    ],
    limit: "외부망에서 내부망으로 파일을 옮긴 뒤의 별도 서명·해시 재검증과 배포 시스템 서명은 추가 운영 연동이 필요합니다.",
    command: "현재는 배포 자동화가 release-lock과 관측값을\nharness/acgh/release.py의 check_promotion()에 전달합니다.",
    resultExample: "T91 | PASS (배포 연동 예시)\n검사한 이미지 sha256:61a3…와 배포 이미지가 같고 재빌드하지 않음",
    output: "승격 검사 결과의 T91 항목에 Release lock과 실제 배포 관측값의 불일치가 남습니다. 배포 승인자와 운영 담당자가 최종 배포 전에 확인합니다.",
    code: ["harness/acgh/release.py", "harness/acgh/schema/release-lock.schema.json", "harness/tests/test_release.py"]
  }
};

window.WIKI_FILES = {
  manifest: {
    title: "Manifest",
    path: "harness/registrations/<버전>/manifests/BANK-OM-NNN.yaml",
    purpose: "하나의 BANK-OM 기능이 현재 OpenMetadata 버전에서 변경하는 전체 파일, 그중 반드시 유지할 핵심 파일, 공식 업그레이드 때 다시 볼 경로와 기능 test 연결을 기록합니다.",
    created: "새 BANK-OM ID를 최초 등록할 때 기능별로 한 파일을 만듭니다.",
    update: "같은 ID의 후속 commit에서 새 파일이 추가되면 changed_paths에 포함하고, 필수 파일·watch 의존·Contract·적용 순서가 바뀔 때 함께 갱신합니다. 기존 등록 파일의 내용만 다시 수정했다면 changed_paths의 파일명 목록은 바뀌지 않습니다.",
    owner: "plan 명령은 Git에서 전체 변경 파일과 공식 업그레이드 때 다시 볼 직접 변경 경로를 계산합니다. 기능 담당자는 필수 파일, 직접 변경하지 않았지만 함께 확인할 경로, Contract를 결정합니다. 승인자는 제안 내용 확인값(proposal digest)이 적힌 승인서에 판단 사유를 남깁니다. 이 값으로 승인 뒤 제안이 바뀌지 않았는지 확인합니다.",
    readers: "변경 생존 확인, 적용 순서 확인, 등록 범위 확인, 공식 업그레이드 영향 확인, 필수 test 연결·실행 확인에 사용됩니다.",
    fields: [
      ["customization_id", "필수·문자열", "코드 commit과 관리자료를 연결하는 BANK-OM ID", "관리자 발급", "BANK-OM-007"],
      ["title", "필수·문자열", "사람이 읽는 기능명", "기능 담당자", "Tibero 연결 유형"],
      ["status", "필수", "현재 검사할 기능은 active, 폐기 절차를 마친 기능은 retired", "관리 담당자", "active"],
      ["kind", "필수", "공식 Core 수정 여부와 변경 유형", "설계 검토자", "core-patch"],
      ["implementation.changed_paths", "필수·목록", "현재 버전에서 이 ID가 붙은 모든 commit이 변경한 전체 파일. 목록 밖 파일을 같은 ID로 변경하면 등록 범위 검사가 BLOCK", "Git 자동 추출 후 확인", ".../tiberoConnection.json"],
      ["implementation.required_changed_paths", "필수·목록", "현재 변경 범위 중 누락되면 기능 미적용으로 즉시 BLOCK할 핵심 파일", "기능 담당자", ".../tiberoConnection.json"],
      ["upgrade_watch.paths", "필수·목록", "공식 버전 변경 시 다시 비교할 관련 경로", "준비도구가 changed_paths 중 공식 OpenMetadata 포크 브랜치에도 존재하는 경로만 자동 제안하고, 행내 전용 경로·간접 의존 경로는 담당자가 추가 여부를 결정", ".../databaseService.json"],
      ["assurance.contracts", "필수·목록", "업무 정상 조건과 필수 test를 연결하는 Contract ID", "기능 담당자", "CONTRACT-TIBERO-CONNECTOR"],
      ["assurance.direct_tests", "목록", "Contract에 연결하지 않고 이 기능에 직접 지정한 기술 test", "개발자", "tests/.../test_tibero.py::test_schema"],
      ["series.allowed", "필수·boolean", "같은 ID의 후속 commit을 허용하는지", "변경관리 담당자", "true"],
      ["series.depends_on", "목록", "먼저 적용돼야 하는 BANK-OM ID", "기능 설계자", "[BANK-OM-006]"]
    ],
    before: "implementation:\n  changed_paths:\n    - openmetadata-spec/.../tiberoConnection.json\n    - openmetadata-ui/.../DatabaseServiceUtils.tsx\nseries:\n  allowed: true",
    after: "implementation:\n  changed_paths:\n    - openmetadata-spec/.../tiberoConnection.json\n    - openmetadata-ui/.../DatabaseServiceUtils.tsx\n    - openmetadata-ui/.../serviceConnection.ts\n    - openmetadata-ui/.../DatabaseServiceUtils.test.tsx\nseries:\n  allowed: true",
    updateReason: "BANK-OM-007 후속 commit이 기존 목록에 없던 파일 두 개를 변경했으므로, 현재 1.13.0 버전의 changed_paths를 8개에서 10개로 갱신합니다. 어떤 파일이 후속 commit에서 추가됐는지는 Git 이력이 보존합니다. 새 파일이 기능의 필수 구성요소라면 required_changed_paths에도 같은 경로를 별도로 추가합니다.",
    scopeFlow: [
      ["BANK-OM-007 최초 commit", "변경 파일 8개", ""],
      ["BANK-OM-007 후속 commit", "새 변경 파일 2개", "+"],
      ["현재 1.13.0 검사 범위", "changed_paths 10개", "="]
    ],
    scopeOutcome: "T40은 changed_paths 밖의 변경을 BLOCK하고, T93은 changed_paths와 실제 ID별 Git 변경 이력이 같은지 확인합니다. T26은 changed_paths의 일반 파일이 사라지거나 공식 원본과 같아지면 APPROVAL을 요구합니다. required_changed_paths에도 등록한 파일은 같은 상황에서 BLOCK합니다. T42는 changed_paths가 아니라 upgrade_watch.paths를 읽으므로, 새 경로가 공식 업그레이드 영향 감시에도 필요한지 별도로 확인합니다.",
    scopeExamples: [
      ["BANK-OM-007의 현재 10개 파일", "changed_paths", "모두 현재 검사 범위에 포함"],
      ["serviceConnection.ts", "changed_paths + watch", "사라지면 T26 APPROVAL, 공식 버전에서도 바뀌면 T42 APPROVAL"],
      ["DatabaseServiceUtils.test.tsx", "changed_paths", "등록 밖 변경인지 검사하고, 사라지면 T26 APPROVAL"],
      ["tiberoConnection.json", "changed_paths + required + watch", "사라지거나 공식 원본과 같으면 T26 BLOCK"],
      ["Manifest 어느 목록에도 없는 새 파일", "미등록", "같은 ID의 commit이 변경하면 T40 BLOCK"]
    ],
    commands: [
      {
        label: "변경안 생성 · 실제 등록자료는 바뀌지 않음",
        meaning: "Git commit 이력에서 BANK-OM ID별 SHA와 changed_paths를 계산하고 기존 사람 정책과 비교합니다. 제안·질문·diff를 등록 폴더 밖에 만들며, 승인 전에는 실제 Manifest를 수정하지 않습니다.",
        command: "./.venv/bin/python harness/om_workflow.py plan \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0"
      },
      {
        label: "승인안 적용 · Manifest와 자동 생성 목록이 바뀜",
        meaning: "승인서가 같은 변경안을 가리키고 모든 검토 질문에 답했으며 Git과 등록 입력도 그대로일 때만 Manifest·Registry·commit inventory·전체 변경 목록을 반영합니다. Contract는 자동으로 바꾸지 않습니다.",
        command: "./.venv/bin/python harness/om_workflow.py apply \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0 \\\n  --proposal /path/to/proposal.yaml \\\n  --approval /path/to/registration-approval.yaml"
      },
      {
        label: "등록자료 검증 · Manifest는 바뀌지 않음",
        meaning: "수정한 Manifest가 Registry·Contract·전체 변경 파일 목록·Registry source.snapshot_sha의 파일–BANK-OM 연결표·필수 test 연결과 맞는지 읽어서 검사합니다. Manifest를 직접 수정한 뒤에는 이 검증을 실행합니다.",
        command: "./.venv/bin/python harness/om_workflow.py validate \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0"
      }
    ],
    storage: "버전별 등록 폴더에서 Git 이력으로 관리합니다. 새 공식 버전에서도 같은 업무 기능이면 같은 BANK-OM ID를 유지하되 새 버전 폴더의 changed_paths를 다시 생성·검토합니다. 최초 구현과 후속 수정의 구분은 Manifest 목록을 나누지 않고 Git commit SHA와 커밋 순서로 확인합니다. 새 plan 명령은 --output을 필수로 요구하고 등록 폴더 내부 출력을 차단합니다."
  },
  registry: {
    title: "Customization Registry",
    path: "harness/registrations/<버전>/customization-registry.yaml",
    purpose: "검사할 BANK-OM 전체 목록, 담당자, 상태, 중요도와 Manifest·Contract 연결을 한곳에서 관리합니다.",
    created: "한 버전의 등록 묶음을 처음 만들 때 생성합니다.",
    update: "ID 추가·폐기, 담당자·배정 상태, 중요도, Manifest 또는 Contract 연결이 바뀔 때 갱신합니다.",
    owner: "plan은 새 ID의 Manifest·Contract 연결과 Git에서 확인한 코드 기준값을 제안합니다. 담당자·중요도·상태는 관리 책임자가 새 ID 입력 파일과 승인서에서 확정합니다.",
    readers: "활성 기능 목록 확인, 담당자 배정 확인, 적용 순서 확인, 필수 test 연결 확인과 등록자료 완전성 검사에 사용됩니다.",
    fields: [
      ["source.repository", "필수", "분석한 제품 코드 저장소", "자동/관리자 확인", "현재 적용 예시: easyseop/OM_TEMP"],
      ["source.snapshot_sha", "필수", "해당 제품 버전의 등록 revision을 처음 만든 시점에 BANK-OM 변경이 적용돼 있던 코드 commit", "Git 자동 확인", "62e39da8…"],
      ["source.upstream_sha", "필수", "비교 기준 공식 OpenMetadata 상태", "공식 tag에서 확인", "f329dd4a…"],
      ["entries[].customization_id", "필수", "Manifest와 같은 BANK-OM ID", "Manifest에서 생성", "BANK-OM-007"],
      ["entries[].owner", "필수", "기능과 결과를 책임지는 조직·담당자", "관리 책임자", "데이터플랫폼팀"],
      ["entries[].owner_status", "필수", "담당 확정은 assigned, 미정은 pending", "관리 책임자", "assigned"],
      ["entries[].status", "필수", "검사 대상은 active, 폐기 완료는 retired", "관리 책임자", "active"],
      ["entries[].criticality", "필수", "low·medium·high·critical 중 업무 영향 등급", "업무 영향 평가", "high"],
      ["entries[].manifest", "필수", "해당 Manifest 경로", "생성기", "manifests/BANK-OM-007.yaml"],
      ["entries[].contracts", "목록", "연결된 Contract ID", "Manifest·Contract에서 생성", "[CONTRACT-TIBERO-CONNECTOR]"],
      ["entries[].provenance", "필수", "Registry source.snapshot_sha의 custom commit에 이미 있던 기능인지 그 commit 이후에 추가한 기능인지 구분", "Git 분석 후 확인", "source-snapshot"]
    ],
    before: "- customization_id: BANK-OM-001\n  owner: UNASSIGNED\n  owner_status: pending\n  criticality: high",
    after: "- customization_id: BANK-OM-001\n  owner: 데이터플랫폼팀\n  owner_status: assigned\n  criticality: high",
    updateReason: "실제 책임 조직이 정해졌으므로 owner와 owner_status만 승인해 변경합니다. source.snapshot_sha는 같은 버전의 일반 후속 commit이 생겼다는 이유만으로 최신 commit으로 바꾸지 않습니다. 같은 제품 버전의 등록 revision을 새로 만들 때 기존 값을 덮어쓸지 새 revision으로 보관할지는 조직 정책을 먼저 정해야 합니다.",
    commands: [
      {
        label: "Registry 변경안 생성 · 실제 파일은 바뀌지 않음",
        meaning: "새 BANK-OM ID라면 사람이 작성한 새 ID 입력과 contracts.yaml에 적힌 같은 BANK-OM ID를 함께 확인해 Registry 변경안을 만듭니다. 기존 ID의 후속 commit만 있다면 Registry에 새 항목을 만들지 않습니다.",
        command: "./.venv/bin/python harness/om_workflow.py plan \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0 \\\n  --new-id-input /path/to/new-bank-om.yaml"
      },
      {
        label: "승인·apply 뒤 연결 검증 · Registry는 바뀌지 않음",
        meaning: "Registry entry가 Manifest와 Contract를 정확히 가리키고 owner·상태·중요도 형식을 지키는지 읽어서 검사합니다. 검증 명령은 파일을 수정하지 않습니다.",
        command: "./.venv/bin/python harness/om_workflow.py validate \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0"
      }
    ],
    storage: "버전별 등록 폴더에서 Git으로 관리합니다. plan의 diff.patch에서 사람 입력인 owner·criticality가 승인 내용과 같은지 확인하고, apply 결과의 written_files에 customization-registry.yaml이 있을 때만 실제 Registry가 바뀐 것으로 판단합니다."
  },
  contracts: {
    title: "Contract catalog",
    path: "harness/registrations/<버전>/contracts.yaml",
    purpose: "파일 존재만으로 확인할 수 없는 업무 정상 조건과 그 조건을 확인할 필수 test를 연결합니다.",
    created: "BANK-OM 기능을 최초 등록할 때 기능 책임자가 정상 조건을 정하고 만듭니다.",
    update: "업무 정상 조건, test 파일·함수 이름, 보호할 BANK-OM ID가 바뀔 때 갱신합니다. test 실행마다 수정하지 않습니다.",
    owner: "업무 정상 조건은 기능 책임자가 정하고, test 선택자는 개발자와 test 담당자가 확인합니다. prepare_registration.py는 Contract를 읽어 연결을 검사하지만 내용을 자동 작성하거나 apply하지 않습니다.",
    readers: "필수 test 파일·이름 확인, 실제 test 실행, 재시도 판정과 변경 생존 확인에 사용됩니다.",
    fields: [
      ["contracts[].id", "필수", "CONTRACT-... 형식의 고유 ID", "관리자/기능 담당자", "CONTRACT-KOREAN-IME"],
      ["contracts[].title", "필수", "사람이 읽는 Contract 이름", "기능 담당자", "한글 입력 조합 보존"],
      ["contracts[].invariant", "필수", "버전이 바뀌어도 유지돼야 하는 업무 동작", "기능 책임자", "한글 자모가 중복·역전·소실되지 않는다"],
      ["contracts[].required_tests", "필수·목록", "정상 조건을 확인할 pytest 파일과 함수", "개발·test 담당자", "tests/.../test_korean_ime.py::test_hangul_composition_roundtrip"],
      ["contracts[].customization_ids", "필수·목록", "이 Contract가 보호하는 BANK-OM ID", "기능 담당자", "[BANK-OM-005]"]
    ],
    before: "- id: CONTRACT-KOREAN-IME\n  invariant: 한글 입력 중 자모가 중복·역전·소실되지 않는다.\n  required_tests:\n    - tests/bank/contracts/test_korean_ime.py::test_hangul_composition_roundtrip",
    after: "- id: CONTRACT-KOREAN-IME\n  invariant: 한글 입력·붙여넣기 중 자모가 중복·역전·소실되지 않는다.\n  required_tests:\n    - tests/bank/contracts/test_korean_ime.py::test_hangul_composition_roundtrip\n    - tests/bank/contracts/test_korean_ime.py::test_hangul_paste_roundtrip",
    updateReason: "기존 입력뿐 아니라 붙여넣기 동작도 공식 정상 조건에 포함하기로 승인했으므로 invariant와 필수 test를 함께 갱신합니다.",
    commands: [
      "./.venv/bin/python harness/om_workflow.py validate \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0",
      "cd harness\n../.venv/bin/python -m pytest -q tests/test_contracts.py"
    ],
    storage: "버전별 등록 폴더에서 Git으로 관리합니다. 과거 실행 결과의 Contract를 바꾸지 않고, 변경 commit 이후 새 suite_version으로 다시 test합니다."
  },
  shared_paths: {
    title: "Registry source.snapshot_sha의 custom commit에서 여러 BANK-OM ID가 함께 바꾼 파일 연결표",
    path: "harness/registrations/<버전>/shared-path-owners.yaml",
    purpose: "해당 제품 버전의 등록자료를 만들 때 Registry의 source.snapshot_sha에 기록한 custom branch commit에서 두 개 이상의 BANK-OM ID가 함께 변경한 파일만 기록합니다. 사람이나 조직의 파일 소유권을 뜻하지 않으며, 최신 커스텀 브랜치의 공용 파일 목록도 아닙니다. 파일명에 owners가 포함되지만, 값은 사람이나 조직이 아니라 해당 파일을 변경한 BANK-OM ID 목록입니다.",
    created: "제품 버전별 등록 묶음을 처음 만들 때 source-snapshot-path-owners.yaml에서 BANK-OM ID가 두 개 이상 연결된 경로만 자동 추출합니다.",
    update: "Registry의 source.snapshot_sha로 기록한 custom branch commit을 다른 commit으로 바꾸거나, 그 commit까지의 BANK-OM 분류 오류를 바로잡을 때만 다시 만듭니다. 같은 제품 버전의 일반 후속 commit이나 최신 Manifest 변경 때문에 갱신하지 않습니다.",
    owner: "Registry의 source.snapshot_sha까지 이어지는 Git commit 이력과 등록 묶음 생성기가 계산합니다. 담당자는 각 commit의 BANK-OM ID 분류가 맞는지 검토합니다.",
    readers: "Git 기록이 유실되고 당시 코드 폴더만 남은 비상 상황에서, 공용 파일에 어떤 BANK-OM 변경을 적용해야 하는지 확인하는 데 사용합니다. 최신 커스텀 브랜치의 변경 범위 검사는 Manifest changed_paths와 commit inventory를 읽습니다.",
    fields: [
      ["<파일 경로>", "필수·문자열 key", "Registry source.snapshot_sha의 custom branch commit까지 두 ID 이상이 함께 변경한 정확한 파일", "Git 자동 추출", ".../Entity.java"],
      ["<BANK-OM ID 목록>", "필수·목록", "Registry source.snapshot_sha의 custom branch commit까지 해당 파일을 변경한 기능 ID", "commit 메시지에서 자동 추출", "[BANK-OM-001, BANK-OM-002]"]
    ],
    before: "paths:\n  - path: openmetadata-service/.../Entity.java\n    owners: [BANK-OM-001]",
    after: "paths:\n  - path: openmetadata-service/.../Entity.java\n    owners: [BANK-OM-001, BANK-OM-002]",
    updateReason: "Registry source.snapshot_sha의 custom branch commit까지 BANK-OM-002도 Entity.java를 변경한 사실이 확인되면 owners 목록에 추가합니다. source.snapshot_sha 이후의 후속 commit 때문에 이 연결표를 바꾸지는 않습니다.",
    commands: [
      "./.venv/bin/python harness/om_workflow.py bootstrap \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0 \\\n  --confirm-replace-registration",
      "./.venv/bin/python harness/om_workflow.py validate \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0"
    ],
    storage: "Registry source.snapshot_sha의 custom branch commit을 기준으로 자동 생성해 제품 버전별 등록 폴더에 보관합니다. generate_registration_bundle.py는 그 commit까지의 Git 이력과 사람 정책을 사용하므로 일반 후속 commit 처리에는 실행하지 않습니다. Registry source.snapshot_sha를 바꾸는 별도 승인 작업에서만 변경 내용을 검토하고 다시 만듭니다."
  },
  source_snapshot_owners: {
    title: "Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
    path: "harness/registrations/<버전>/source-snapshot-path-owners.yaml",
    purpose: "Registry의 source.snapshot_sha가 가리키는 custom branch commit까지, 각 파일을 어떤 BANK-OM commit들이 변경했는지 기록합니다. 사람이나 조직의 파일 소유권을 뜻하지 않습니다. Git 기록이 유실되고 당시 코드 폴더만 남은 비상 상황에서 코드 복구 순서를 정할 때 사용합니다.",
    created: "제품 버전별 등록 묶음을 처음 만들 때 Registry source.snapshot_sha에 기록할 custom branch commit까지의 Git commit 이력을 읽어 자동 생성합니다.",
    update: "Registry source.snapshot_sha의 custom branch commit을 다른 commit으로 바꿀 때만 다시 생성합니다. 같은 ID의 후속 commit이 생겼다는 이유만으로 기존 source.snapshot_sha의 연결표를 고치지 않습니다.",
    owner: "Git 이력과 생성기가 자동으로 만듭니다. 담당자는 잘못 분류된 commit ID가 없는지 검토하며 파일을 임의로 편집하지 않습니다.",
    readers: "비상 복구 검사(T25-R)가 각 파일에 어떤 BANK-OM 변경을 적용할지 결정할 때 사용합니다. 최신 커스텀 브랜치의 등록 범위 검사(T40·T93)는 이 파일이 아니라 Manifest의 changed_paths를 사용합니다.",
    fields: [
      ["<파일 경로>", "필수·문자열 key", "Registry source.snapshot_sha의 custom branch commit에서 공식 OpenMetadata commit과 달랐던 정확한 파일", "Git 자동 추출", "openmetadata-ui/.../serviceConnection.ts"],
      ["<BANK-OM ID 목록>", "필수·목록", "Registry source.snapshot_sha의 custom branch commit까지 해당 파일을 변경한 기능 ID", "commit 메시지에서 자동 추출", "[BANK-OM-006]"]
    ],
    before: "openmetadata-ui/.../serviceConnection.ts:\n- BANK-OM-006",
    after: "openmetadata-ui/.../serviceConnection.ts:\n- BANK-OM-006",
    updateReason: "BANK-OM-007의 후속 commit은 Registry source.snapshot_sha에 기록된 custom branch commit 이후에 만들어졌습니다. 따라서 이 연결표는 바꾸지 않습니다. 최신 커스텀 브랜치의 BANK-OM-007 Manifest changed_paths와 commit-inventory.yaml이 후속 변경을 기록합니다.",
    scopeFlow: [
      ["Registry source.snapshot_sha의 custom commit", "serviceConnection.ts = 006", ""],
      ["007 후속 commit", "같은 파일 추가 변경", "→"],
      ["최신 커스텀 브랜치 범위", "Manifest·commit inventory에 007 반영", "→"]
    ],
    scopeOutcome: "비상 복구 검사(T25-R)는 serviceConnection.ts에 BANK-OM-006 변경을 먼저 적용합니다. 최신 커스텀 브랜치의 변경 범위 검사는 BANK-OM-007 Manifest와 commit-inventory.yaml에서 후속 변경을 확인합니다. 두 자료는 서로 다른 commit 상태를 설명하므로 값이 달라도 오류가 아닙니다.",
    scopeExamples: [
      ["source-snapshot-path-owners.yaml", "BANK-OM-006", "Registry source.snapshot_sha의 코드 상태 복원에만 사용"],
      ["BANK-OM-007 Manifest changed_paths", "serviceConnection.ts 포함", "최신 커스텀 브랜치의 범위 검사에 사용"],
      ["shared-path-owners.yaml", "Registry source.snapshot_sha의 custom commit까지 여러 ID가 연결된 파일만 포함", "Git 이력 없이 보관된 코드 복원에 사용"]
    ],
    commands: [
      {
        label: "등록 묶음 재생성 · 이 파일이 바뀜",
        meaning: "Registry source.snapshot_sha에 기록할 custom branch commit까지 읽어 파일별 BANK-OM 연결표를 다시 만듭니다. source.snapshot_sha가 같다면 생성 결과도 같아야 합니다.",
        command: "./.venv/bin/python harness/om_workflow.py bootstrap \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0 \\\n  --confirm-replace-registration"
      },
      {
        label: "등록자료 검증 · 이 파일은 바뀌지 않음",
        meaning: "source-snapshot-path-owners.yaml의 경로와 BANK-OM ID가 Registry source.snapshot_sha의 custom commit 및 Manifest와 모순되지 않는지 확인합니다.",
        command: "./.venv/bin/python harness/om_workflow.py validate \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0"
      }
    ],
    storage: "제품 버전별 등록 폴더의 자동 생성 파일로 Git에 보관합니다. 최신 커스텀 브랜치의 기능 범위를 설명하려고 수동으로 최신화하지 않습니다. 최신 범위는 Manifest changed_paths와 commit-inventory.yaml에서 확인합니다."
  },
  diff_inventory: {
    title: "전체 변경 파일 목록",
    path: "harness/registrations/<버전>/source-diff-paths.txt",
    purpose: "공식 원본과 행내 코드 사이에서 실제로 달라진 모든 파일 경로를 한 줄에 하나씩 기록합니다.",
    created: "등록 묶음을 처음 만들 때 Git diff로 생성합니다.",
    update: "검사 대상 OpenMetadata 코드 commit 또는 공식 기준 commit이 바뀔 때마다 다시 생성합니다.",
    owner: "Git과 생성기가 자동으로 만듭니다. 사람이 파일 목록을 직접 보정하지 않습니다.",
    readers: "등록자료가 실제 Git diff를 빠짐없이 설명하는지 확인하는 전체 변경 범위 검사에 사용됩니다.",
    fields: [
      ["한 줄의 경로", "필수", "제품 코드 저장소의 최상위 폴더 기준 실제 변경 파일", "Git diff 자동 생성", "openmetadata-service/.../Entity.java"]
    ],
    before: "openmetadata-service/.../Entity.java\nopenmetadata-spec/.../instanceCode.json",
    after: "openmetadata-service/.../Entity.java\nopenmetadata-spec/.../instanceCode.json\nopenmetadata-ui/.../instanceCodeAPI.ts",
    updateReason: "검사 대상 OpenMetadata 코드에 새 변경 파일이 생겼으므로 전체 목록을 Git에서 다시 생성합니다. 텍스트 파일만 수정하면 실제 코드와 달라져 검사에 실패합니다.",
    commands: [
      "./.venv/bin/python harness/om_workflow.py bootstrap --repo /path/to/OM_TEMP --version 1.13.0 --confirm-replace-registration"
    ],
    storage: "검사 대상 코드와 공식 기준 코드를 비교해 자동 생성한 파일입니다. 어떤 두 commit을 비교했는지 함께 Git에 보관합니다."
  },
  layout: {
    title: "코드 경로 분류표",
    path: "harness/registrations/<버전>/repository-layout.yaml",
    purpose: "파일 경로가 공식 OpenMetadata 코드, 행내 거버넌스 코드, 플랫폼 확장 또는 알 수 없는 영역 중 어디에 속하는지 정합니다.",
    created: "제품 코드 저장소를 검사 체계에 처음 등록할 때 만듭니다.",
    update: "공식 버전에서 최상위 모듈이 추가·이동되거나 행내 확장 root가 바뀔 때 갱신합니다.",
    owner: "제품 코드 저장소의 폴더 구조를 아는 플랫폼 담당자가 승인합니다.",
    readers: "commit·경로 정책 확인, 등록 범위 확인, 민감 경로 확인 등 파일 위치를 해석하는 모든 소스 검사에 사용됩니다.",
    fields: [
      ["upstream_base_sha", "필수", "이 경로 정책을 작성한 공식 기준 commit", "공식 tag에서 확인", "f329dd4a…"],
      ["path_grammar", "필수", "대소문자·Unicode·symlink 등 경로 해석 규칙", "플랫폼 담당자", "case_sensitive: true"],
      ["upstream_owned_roots", "필수·목록", "공식 OpenMetadata 코드 영역", "제품 코드 저장소 구조 분석", "openmetadata-service/**"],
      ["bank_governance_roots", "필수·목록", "검사 정책·test·문서 영역", "검사기 저장소 담당자", "harness/**"],
      ["platform_extension_roots", "목록", "공식 코드와 분리한 행내 확장 영역", "플랫폼 담당자", "bank-extensions/**"],
      ["unknown_path_policy", "필수", "분류하지 못한 경로의 처리", "정책 담당자", "analysis_error"]
    ],
    before: "upstream_owned_roots:\n  - openmetadata-service/**\n  - openmetadata-ui/**",
    after: "upstream_owned_roots:\n  - openmetadata-service/**\n  - openmetadata-ui/**\n  - openmetadata-mcp/**",
    updateReason: "새 공식 버전에서 openmetadata-mcp 모듈이 검사 대상 공식 코드로 추가됐음을 확인했을 때 root를 추가합니다. 단순히 오류를 없애려고 unknown 경로를 넓게 허용하지 않습니다.",
    commands: [
      "pytest -q harness/tests/test_layout.py",
      "./.venv/bin/python harness/om_workflow.py validate --repo /path/to/OM_TEMP --version 1.13.0"
    ],
    storage: "공식 기준 버전별 정책입니다. upstream_base_sha가 달라지면 기존 정책을 그대로 복사하지 말고 경로 구조를 재검토합니다."
  },
  zones: {
    title: "중요 경로 정책(Sensitive zones)",
    path: "harness/registrations/<버전>/sensitive-zones.yaml",
    purpose: "보안·인증·설정·DB처럼 변경 시 차단 또는 별도 승인이 필요한 경로를 분류합니다.",
    created: "제품 코드 저장소의 위험 경로 정책을 최초 정의할 때 만듭니다.",
    update: "새 보안·인증 모듈, migration 경로 또는 조직 통제 정책이 바뀔 때 갱신합니다.",
    owner: "보안·플랫폼·DB 담당자가 함께 승인합니다.",
    readers: "민감 경로 변경 검사와 업그레이드 위험 검사에서 변경 경로의 승인 수준을 정할 때 사용됩니다.",
    fields: [
      ["frozen", "목록", "일반 BANK-OM 작업에서는 변경할 수 없는 경로", "정책 담당자", ".github/workflows/release/**"],
      ["protected", "목록", "보안·플랫폼 담당자의 별도 승인이 필요한 경로", "보안·플랫폼 담당자", "openmetadata-service/**/security/**"],
      ["watched", "목록", "변경 사실을 검사 결과에 반드시 표시할 경로", "업무·DB 담당자", "bootstrap/sql/migrations/**"]
    ],
    before: "protected:\n  - openmetadata-service/src/main/java/**/security/**",
    after: "protected:\n  - openmetadata-service/src/main/java/**/security/**\n  - openmetadata-service/src/main/java/**/auth/**",
    updateReason: "새 공식 버전의 인증 코드가 auth 경로로 분리됐고 같은 승인 통제가 필요하다고 보안 담당자가 판단했을 때 추가합니다.",
    commands: [
      "pytest -q harness/tests/test_zones.py",
      "./.venv/bin/python harness/om_workflow.py risk \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0 \\\n  --target <새-공식-버전-commit> \\\n  --conflict-rate 0.0"
    ],
    storage: "정책 파일이므로 변경 사유와 승인자를 Git 리뷰에 남깁니다. 과거 검사 결과에 사용한 정책은 수정하지 않습니다."
  },
  candidate_lock: {
    title: "Candidate lock",
    path: "현재 소스 검사: source-gate-results.json의 candidate_lock 항목 · 별도 배포 실행: evidence/candidate-lock.yaml",
    purpose: "어떤 행내 코드를 검사했는지 고정합니다. 실행·배포 검사에서는 그 코드로 만든 이미지나 패키지도 같은 검사 대상으로 묶습니다.",
    created: "현재 소스 검사 명령은 실행할 때 제품 코드 저장소의 HEAD commit, 전체 파일 상태와 소스 내용 확인값을 자동 계산해 source-gate-results.json의 candidate_lock 항목에 기록합니다. 소스 검사 전에 사람이 별도 YAML을 작성하지 않습니다. 실제 이미지나 패키지를 검사할 때는 그 배포 파일의 내용 확인값을 사용한 별도 Candidate lock이 필요합니다.",
    update: "기존 파일을 고치지 않습니다. 코드, 전체 파일 상태, 배포 파일, 공식 목표 버전, 통합 방식 중 하나라도 바뀌면 새 Candidate lock을 만듭니다.",
    owner: "소스 검사기 또는 CI·Runtime 실행기가 계산하고, 담당자는 결과에 기록된 제품 코드 저장소·commit·내용 확인값이 실제 검사 대상과 같은지 확인합니다.",
    readers: "검사 대상 고정, 변경 생존 확인, Runtime test 실행, 증거 연결과 실제 배포 일치 검사에 사용됩니다.",
    fields: [
      ["integration_strategy", "필수", "공식 코드와 행내 변경을 합친 방식", "운영 절차 선택", "vendor-merge"],
      ["upstream.repository", "필수", "공식 원본 저장소", "자동/관리자 확인", "open-metadata/OpenMetadata"],
      ["upstream.base_sha", "필수", "업그레이드 전 공식 commit", "공식 tag", "f329dd4a… (1.13.0)"],
      ["upstream.target_sha", "필수", "업그레이드할 공식 commit", "공식 tag", "afcb2d2… (1.13.1)"],
      ["candidate.repository", "필수", "검사 대상 제품 코드 저장소", "자동", "현재 적용 예시: easyseop/OM_TEMP"],
      ["candidate.commit_sha", "필수", "모든 BANK-OM 변경을 포함한 최종 검사 대상 custom branch commit 하나", "Git 자동", "1.13.0 소스 재검사 예: 3a2811cf… · 1.13.1 commit별 재적용 진단 예: dee330ebd5…"],
      ["candidate.tree_sha", "필수", "그 commit에서 보이는 전체 파일 내용에 Git이 붙인 식별값", "Git 자동", "9495a31c…"],
      ["candidate.artifact_digest", "필수", "소스 검사에서는 전체 소스 내용의 SHA-256 확인값, 실행·배포 검사에서는 실제 이미지·패키지의 SHA-256 확인값", "소스 검사기 또는 빌드 자동", "현재 소스 결과: 전체 소스 확인값 · 환경 실행 예시: image sha256:61a3…"],
      ["patch_source_lock_digest", "조건부", "patch-replay에서 사용한 Patch-lock 파일의 SHA-256", "자동", "patch-replay 예시: sha256:8ce1…"]
    ],
    before: "candidate:\n  commit_sha: aaa111...\n  artifact_digest: sha256:old...",
    after: "candidate:\n  commit_sha: bbb222...\n  artifact_digest: sha256:new...",
    updateReason: "코드나 빌드 파일이 바뀌면 기존 결과의 Candidate lock을 수정하지 않습니다. 새 검사를 실행해 bbb222용 결과와 Candidate lock을 새로 만들고, 이전 결과는 aaa111을 검사한 기록으로 보존합니다.",
    commands: [
      "./.venv/bin/python harness/om_workflow.py runtime \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0 \\\n  --artifact /path/to/deployment-file"
    ],
    storage: "소스 검사에서는 source-gate-results.json 전체를 새 파일로 보관하면 그 안의 Candidate lock도 함께 보존됩니다. 별도 배포 실행이 Candidate lock YAML을 만들면 같은 실행 증거 폴더에 보관합니다. OM_TEMP 1.13.0 소스 검사를 다시 수행한 custom commit은 3a2811cf…입니다. 1.13.1의 dee330ebd5…는 BANK-OM commit을 하나씩 다시 적용해 충돌 위치를 확인한 진단 코드이므로 정식 vendor-merge 결과나 운영 배포 증거로 사용하지 않습니다."
  },
  test_run_set: {
    title: "Test run set",
    path: "검사 실행별 evidence/test-run-set.yaml",
    purpose: "어떤 필수 test를 몇 번째 시도에서 실행했고 결과가 무엇인지, 정확한 검사 대상 commit·검사기 commit·suite 버전과 함께 기록합니다.",
    created: "Runtime Contract test를 실행할 때마다 자동 생성합니다.",
    update: "기존 파일을 수정하지 않습니다. 재실행·재시도·검사 대상 commit 변경마다 새 실행 결과를 만듭니다.",
    owner: "Runtime test 실행기가 자동 생성합니다.",
    readers: "Runtime test 재시도 판정, 실행 증거 연결과 실제 배포 일치 검사에 사용됩니다.",
    fields: [
      ["candidate.commit_sha", "필수", "test를 실행한 최종 검사 대상 commit 하나", "Candidate lock에서 자동", "형식 예시: <실제로 test한 custom branch commit SHA>"],
      ["candidate.artifact_digest", "필수", "test한 이미지나 패키지의 내용 확인값", "Candidate lock에서 자동", "환경 실행 예시: sha256:61a3…"],
      ["harness_version", "필수", "검사기 코드 버전", "Git/빌드 자동", "849ae756…"],
      ["suite_version", "필수", "Manifest·Registry·Contract·test 묶음의 내용 확인값", "도구가 내용 확인값 자동 계산", "sha256:5164…"],
      ["runs[].test_id", "필수", "실행한 test 파일과 함수", "실행기", "tests/.../test_tibero.py::test_connection_schema_roundtrip"],
      ["runs[].attempt", "필수", "1부터 연속되는 시도 번호", "실행기", "2"],
      ["runs[].outcome", "필수", "pass·fail·error·skip 중 실행 결과", "test 실행 결과", "pass"]
    ],
    before: "runs:\n  - test_id: tests/...::test_instance_code\n    attempt: 1\n    outcome: fail",
    after: "runs:\n  - test_id: tests/...::test_instance_code\n    attempt: 1\n    outcome: fail\n  - test_id: tests/...::test_instance_code\n    attempt: 2\n    outcome: pass",
    updateReason: "재시도 성공으로 첫 실패를 덮어쓰지 않습니다. 두 시도를 모두 새 Test run set에 남겨 T62가 기능 중요도에 따라 APPROVAL 여부를 판단하게 합니다.",
    commands: [
      "./.venv/bin/python harness/om_workflow.py runtime \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0 \\\n  --artifact /path/to/deployment-file"
    ],
    storage: "실행별 불변 증거입니다. CI run ID·attempt와 함께 보관하고 같은 파일명을 다른 실행 결과로 덮어쓰지 않습니다."
  },
  result: {
    title: "검사 결과",
    path: "검사 실행별 evidence/acgh-result.yaml 또는 source-gate-results.json",
    purpose: "어떤 입력으로 어떤 검사를 실행했고 각 판정과 이유가 무엇인지 기록합니다. 결과 본문 전체에서 계산한 내용 확인값도 함께 저장합니다.",
    created: "소스 검사 또는 Runtime 검사를 실행할 때마다 자동 생성합니다.",
    update: "기존 결과는 수정하지 않습니다. 코드·정책·검사기·test·실행이 바뀌면 새 결과를 생성합니다.",
    owner: "검사 실행기가 자동 생성하고 책임자는 개별 gate의 reasons를 확인합니다.",
    readers: "책임자, T91 배포 승격 검사와 감사·인수인계",
    fields: [
      ["canonical_payload.verdict", "필수", "전체 기계 판정", "판정 엔진", "pass"],
      ["canonical_payload.gates[].name", "필수", "개별 검사 이름", "실행기", "customization-survival"],
      ["canonical_payload.gates[].verdict", "필수", "개별 판정", "판정 엔진", "block"],
      ["canonical_payload.gates[].reasons", "필수", "판정의 구체적 이유", "각 검사기", "required_path_missing: .../Entity.java"],
      ["canonical_payload.inputs", "필수", "검사 대상 제품 코드 저장소·commit·정책 등 판정 입력", "실행기", "1.13.0 재검증 예: candidate_commit: 3a2811cf…"],
      ["canonical_payload.harness_version", "필수", "검사기 버전", "자동", "849ae756…"],
      ["result_digest", "필수", "결과가 나중에 바뀌지 않았는지 확인할 판정 본문 전체의 SHA-256 값", "자동", "sha256:2f8c…"],
      ["observational_metadata.run_id", "실행정보", "결과를 찾기 위한 실행 번호", "CI/실행기", "run-20260729-001"],
      ["expected_exit_code", "필수", "verdict에 대응하는 명령 종료 코드", "판정 엔진", "0 (PASS)"]
    ],
    before: "canonical_payload:\n  verdict: block\n  gates:\n    - name: customization-survival\n      verdict: block\n      reasons: [\"required_path_missing: ...\"]",
    after: "canonical_payload:\n  verdict: pass\n  gates:\n    - name: customization-survival\n      verdict: pass\n      reasons: [\"active_customizations=7\"]",
    updateReason: "BLOCK 결과 파일을 PASS로 직접 고치지 않습니다. 코드를 보완하고 검사기를 다시 실행해 새 결과와 그 결과 내용의 확인값(result_digest)을 만듭니다.",
    commands: [
      "./.venv/bin/python harness/om_workflow.py source \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0",
      "./.venv/bin/python harness/om_workflow.py runtime \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0 \\\n  --artifact /path/to/deployment-file"
    ],
    storage: "실행별 불변 증거입니다. 검사 대상 Git commit SHA·실행 번호·검사기 버전과 함께 보관합니다."
  },
  patch_lock: {
    title: "Patch-lock",
    path: "patch-replay 전략의 patch-source-lock.yaml",
    purpose: "patch-replay 방식을 사용할 때 BANK-OM commit을 어느 순서와 개정으로 다시 적용할지 고정합니다.",
    created: "통합 전략이 patch-replay일 때만 검사 대상 custom branch commit을 만들기 전에 생성합니다.",
    update: "같은 ID의 후속 commit, 적용 순서 또는 개정 번호가 바뀌면 새 Patch-lock revision을 만듭니다. vendor-merge에서는 만들지 않습니다.",
    owner: "변경관리 담당자가 순서를 승인하고 생성기가 commit 존재 여부와 Patch-lock 내용 확인값을 계산합니다.",
    readers: "patch-replay 실행, commit 규칙·적용 순서 검사와 Candidate lock 연결에 사용됩니다. vendor-merge 전략에서는 사용하지 않습니다.",
    fields: [
      ["source_release_tag·sha", "필수", "커스터마이징 commit을 가져올 이전 행내 릴리스", "릴리스 담당자", "verified/om-1.13.0-bank.1 · 7d19c895…"],
      ["patch_series[].id", "필수", "적용할 BANK-OM ID", "Registry·Manifest", "BANK-OM-007"],
      ["patch_series[].revision", "필수", "같은 ID 변경 묶음의 개정 번호", "변경관리 담당자", "2"],
      ["patch_series[].source_commits", "필수", "그 기능을 구성하는 commit SHA를 적용 순서대로 기록", "Git 자동 확인", "[62e39da8…, 7d19c895…]"],
      ["patch_series[].depends_on", "목록", "먼저 적용할 BANK-OM ID", "Manifest", "[BANK-OM-006]"]
    ],
    before: "- id: BANK-OM-007\n  revision: 1\n  source_commits: [62e39da...]",
    after: "- id: BANK-OM-007\n  revision: 2\n  source_commits: [62e39da..., 7d19c89...]",
    updateReason: "patch-replay 전략에서 같은 기능의 후속 commit이 추가됐으므로 같은 ID의 revision과 source_commits를 갱신한 새 Patch-lock을 만듭니다. 후속 commit이 새 파일을 변경했다면 Manifest의 changed_paths도 함께 갱신합니다.",
    commands: [
      {
        label: "현재 적용 예시인 OM_TEMP에는 생성 명령 없음",
        meaning: "현재 연습은 vendor-merge 전략이므로 Patch-lock을 만들지 않습니다. patch-replay를 채택하면 담당자가 적용 순서를 승인한 별도 생성 절차가 필요합니다.",
        command: "./.venv/bin/pytest -q harness/tests/test_patchlock.py"
      }
    ],
    storage: "patch-replay 검사 대상마다 새 파일로 보관합니다. 이전 개정 번호의 파일을 덮어쓰지 않고 Candidate lock에 사용한 Patch-lock의 내용 확인값을 기록합니다."
  },
  release_lock: {
    title: "Release lock",
    path: "검사 실행별 evidence/release-lock.yaml",
    purpose: "운영에 올릴 릴리즈 브랜치의 정확한 commit, 검증 완료 태그, 이미지·Helm 설정과 검사 결과를 하나의 배포 대상으로 묶습니다.",
    created: "필수 검사가 끝나고 운영 승인자가 릴리즈 브랜치로 승격할 대상을 선택할 때 새로 만듭니다. 현재 OM_TEMP 연습에는 아직 생성된 Release lock이 없습니다.",
    update: "코드 commit, 검증 완료 태그, 이미지, Helm 설정 또는 연결한 검사 결과 중 하나라도 바뀌면 기존 파일을 고치지 않고 새 Release lock을 만듭니다.",
    owner: "배포 담당자가 기술 값을 수집하고 운영 승인자가 어떤 검증 완료 태그를 릴리즈 브랜치에 반영할지 승인합니다.",
    readers: "T91과 배포 자동화가 검증한 대상과 실제 릴리즈 브랜치·배포 파일이 같은지 확인할 때 사용합니다.",
    fields: [
      ["release_branch", "필수", "운영 배포에 사용하는 릴리즈 브랜치", "운영 승인자", "release/om-1.13.1"],
      ["release_commit_sha", "필수", "릴리즈 브랜치가 가리켜야 하는 정확한 commit", "Git 자동 확인", "3a2811cf…"],
      ["verified_tag", "필수", "필수 검사를 통과한 같은 commit의 고정 태그", "검사 담당자", "verified/om-1.13.1-bank.1"],
      ["image_digest", "필수", "배포할 컨테이너 이미지의 내용 확인값", "빌드 시스템", "sha256:61a3…"],
      ["helm_digest", "필수", "배포 설정 묶음의 내용 확인값", "배포 시스템", "sha256:82be…"],
      ["evidence_digests", "필수·목록", "Candidate lock·Test run set·검사 결과의 내용 확인값", "검사 시스템", "[sha256:2c96…, sha256:71de…]"]
    ],
    before: "# 현재 OM_TEMP 연습에는 Release lock이 아직 없습니다.",
    after: "release_branch: release/om-1.13.1\nrelease_commit_sha: 3a2811cf...\nverified_tag: verified/om-1.13.1-bank.1\nimage_digest: sha256:61a3...\nhelm_digest: sha256:82be...\nevidence_digests:\n  - sha256:2c96...\n  - sha256:71de...",
    updateReason: "검증 완료 태그가 가리키는 commit과 운영에 사용할 이미지·설정·검사 결과를 한 묶음으로 승인하기 위해 만듭니다. 이 파일을 만들었다고 배포가 끝난 것은 아니며, T91 일치 확인과 사람의 최종 승인이 남습니다.",
    commands: [
      {
        label: "현재 상태 · 형식과 판정 코드만 준비됨",
        meaning: "현재 OM_TEMP에는 실제 이미지·Helm 내용 확인값과 운영 승인이 없으므로 Release lock을 생성하지 않습니다. 운영 연결 뒤에는 전용 생성 명령이 필요합니다.",
        command: "# 예정 절차\n# 1. 검증 완료 태그와 릴리즈 브랜치 commit 일치 확인\n# 2. 이미지·Helm·검사 결과 digest 수집\n# 3. release-lock.yaml 생성\n# 4. T91 실행 후 승인"
      }
    ],
    storage: "배포 실행별 불변 증거로 보관합니다. 기존 Release lock을 덮어쓰지 않고 릴리즈 브랜치·버전·실행 번호가 다른 새 파일을 만듭니다."
  }
};

window.WIKI_TOPICS = {
  repositories: {
    group: "목적과 브랜치 전략 상세",
    title: "제품 코드 저장소와 검사기 저장소",
    summary: "제품 코드 저장소는 공식 OpenMetadata 코드와 BANK-OM 구현을 관리하고, 검사기 저장소는 Manifest·검사 프로그램·검사 결과를 관리합니다. 두 저장소는 BANK-OM ID와 Git commit SHA로 연결됩니다.",
    sections: [
      ["제품 코드 저장소", "공식 OpenMetadata 코드와 커스터마이징 구현 commit을 관리합니다. OpenMetadata 포크 브랜치에는 공식 코드를 그대로 두고 커스텀 브랜치에는 같은 공식 코드와 승인된 커스터마이징을 함께 둡니다. 검증과 승인이 끝나면 운영에 사용할 정확한 commit을 릴리즈 브랜치로 승격합니다."],
      ["검사기 저장소", "Manifest·Registry·Contract, 검사기, 검사 결과, 정책과 운영 문서를 관리합니다. 사용자가 실행하는 OpenMetadata 제품 코드를 대신 보관하지 않습니다."],
      ["두 저장소의 연결 기준", "commit 메시지의 `Customization-ID` 필드에는 BANK-OM ID를 적습니다. Manifest의 `customization_id`에도 같은 BANK-OM ID를 적어 코드 변경과 검사 기준을 연결합니다. Git commit SHA는 실제 변경 commit을 가리키는 별도 값이며, 하나의 BANK-OM ID에 여러 commit SHA가 연결될 수 있습니다."],
      ["Registry의 source 값", "검사기 저장소의 Registry에는 `source.repository`, `source.upstream_sha`, `source.snapshot_sha`가 있습니다. 검사기는 이 값으로 어떤 제품 코드 저장소와 어떤 공식·커스터마이징 commit을 기준으로 등록자료를 만들었는지 확인합니다."],
      ["현재 적용 예시", "제품 코드 저장소는 easyseop/OM_TEMP, 검사기 저장소는 easyseop/openmetadata-test입니다. easyseop/OpenMetadata는 과거 구현 사례를 확인할 때만 사용하는 참고 저장소입니다."]
    ],
    example: "제품 코드 저장소\n└─ 커스터마이징 코드 commit 메시지\n   Customization-ID: BANK-OM-007\n                 ↕ 같은 BANK-OM ID로 연결\n검사기 저장소\n└─ BANK-OM-007 Manifest\n   customization_id: BANK-OM-007\n\n별도 Git 식별값\n└─ 해당 커스터마이징 commit SHA: 62e39da8…",
    resultExample: "일반 구조\n- 제품 코드 저장소: 공식 코드와 커스터마이징 구현 commit\n- 검사기 저장소: Manifest와 검사 결과\n- 기능 연결 값: BANK-OM ID\n- 변경 이력 값: Git commit SHA\n\n현재 적용 예시\n- 제품 코드 저장소: easyseop/OM_TEMP\n- 검사기 저장소: easyseop/openmetadata-test\n- 과거 참고 저장소: easyseop/OpenMetadata",
    update: "아래 표에서 바꿀 항목이 `없음`이면 관리 파일을 수정하지 않습니다. 제품 코드 저장소의 URL·공식 버전·검사 대상 commit이 바뀐 경우에만 Registry의 source 값을 새 기준으로 바꾸고, 검사기 저장소의 URL이 바뀌면 실행 명령·CI·문서 링크를 바꿉니다.",
    caution: "제품 코드와 검사자료를 두 저장소에 중복 보관하지 않습니다. 제품 코드는 제품 코드 저장소를 기준으로 삼고, 검사 기준과 결과는 검사기 저장소를 기준으로 삼습니다. 두 저장소는 BANK-OM ID와 Git commit SHA로 연결합니다."
  },
  branches: {
    group: "목적과 브랜치 전략 상세",
    title: "OpenMetadata 포크·커스텀·릴리즈 브랜치",
    summary: "세 브랜치는 모두 제품 코드 저장소 안에 있습니다. OpenMetadata 포크 브랜치는 공식 코드를 그대로 보관하고, 커스텀 브랜치는 BANK-OM을 합치고 검사하는 작업선이며, 릴리즈 브랜치는 검증과 승인이 끝난 버전을 실제 운영에 제공하는 배포 기준선입니다.",
    sections: [
      ["fork/om-<version> · OpenMetadata 포크 브랜치", "공식 OpenMetadata의 특정 릴리즈 전체 코드를 그대로 가져와 보관합니다. BANK-OM과 충돌 해결 commit을 넣지 않습니다."],
      ["custom/om-<version> · 커스텀 브랜치", "같은 공식 코드 위에 BANK-OM 변경과 충돌 해결 commit을 합칩니다. 검사는 이 브랜치의 정확한 commit을 대상으로 실행합니다."],
      ["verified/om-<version>-bank.<번호> · 검증 완료 태그", "필수 검사를 끝낸 정확한 커스텀 commit에 붙이는 움직이지 않는 표시입니다. 태그만으로 운영 배포가 승인된 것은 아닙니다."],
      ["release/om-<version> · 릴리즈 브랜치", "운영 승인 후 검증 완료 태그와 같은 commit을 가리키도록 갱신합니다. 실제 운영 배포는 이 브랜치를 기준으로 수행합니다."],
      ["현재 OM_TEMP 브랜치 이름과 운영에 사용할 이름", "현재 OM_TEMP 원격에는 기존 이름인 patch/om-1.13.0이 남아 있습니다. 실제 운영을 시작하기 전에 공식 코드 브랜치를 fork/om-<version> 이름으로 전환하고 release/om-<version> 브랜치를 생성해야 합니다. CLI 옵션 --patch-ref는 프로그램이 기존 옵션명을 하위 호환용으로 유지하므로 그대로 사용합니다."],
      ["다음 버전 Cycle", "새 공식 버전의 OpenMetadata 포크 브랜치를 만들고, 직전 커스텀 브랜치의 BANK-OM 변경을 새 커스텀 브랜치에 합칩니다. 충돌 해결과 검사를 통과하면 새 검증 완료 태그를 만들고, 승인 후 새 릴리즈 브랜치를 운영 기준으로 사용합니다."]
    ],
    sharedReportFigure: {
      title: "1차 요약과 동일한 브랜치 Cycle",
      report: "공유문서/openmetadata-phase1-sharing-preview.html",
      selector: ".om-branch-visual"
    },
    example: "custom/om-1.13.0 + fork/om-1.13.1\n              ↓ vendor-merge\n custom/om-1.13.1의 검사 대상 commit\n              ↓ 필수 검사 통과\n verified/om-1.13.1-bank.1\n              ↓ 운영 승인·같은 SHA 확인\n       release/om-1.13.1\n              ↓ 실제 운영 배포",
    resultExample: "fork/om-1.13.1: 공식 코드만 존재\ncustom/om-1.13.1: 공식 코드 + BANK-OM + 충돌 해결 commit\n검증 완료 태그: 검사를 끝낸 정확한 커스텀 commit 고정\nrelease/om-1.13.1: 검증 완료 태그와 같은 commit을 가리키는 운영 배포 기준선",
    update: "공식 목표 버전이 바뀌면 새 OpenMetadata 포크 브랜치와 커스텀 브랜치를 만듭니다. 검사 대상을 고정하는 Candidate lock도 새 공식 버전과 새 커스텀 commit을 기준으로 다시 만듭니다. 필수 검사와 운영 승인이 끝난 뒤에만 릴리즈 브랜치를 검증 완료 태그와 같은 commit으로 갱신합니다.",
    caution: "OpenMetadata 포크 브랜치와 커스텀 브랜치를 합치는 지점에서 Git 충돌이 발생할 수 있습니다. 검사기가 충돌 코드를 자동 선택하지 않으며 담당자가 해결 commit을 남깁니다. 릴리즈 브랜치는 Release lock과 T91 확인 전에는 운영 기준으로 갱신하지 않습니다."
  },
  identity: {
    group: "목적과 브랜치 전략 상세",
    title: "BANK-OM ID, commit 메시지와 Git SHA",
    summary: "BANK-OM ID는 업무 기능 번호이고 Git commit SHA는 Git이 각 변경 상태에 자동 부여하는 식별값입니다. 같은 값이 아니며 서로 대신할 수 없습니다.",
    sections: [
      ["BANK-OM ID", "사람이 업무 기능마다 한 번 발급합니다. 예: Tibero 연결 기능은 BANK-OM-007입니다. 공식 버전이 1.13.0에서 1.13.1로 바뀌어도 같은 기능이면 BANK-OM-007을 유지합니다."],
      ["Commit 메시지", "변경 목적을 제목에 적고 본문에 `Customization-ID: BANK-OM-007`을 넣습니다. 생성기는 이 ID를 읽어 해당 commit의 변경 파일을 BANK-OM-007 Manifest에 연결합니다."],
      ["기능 변경 commit SHA", "코드를 commit할 때마다 Git이 자동 생성합니다. 예: 최초 Tibero 구현은 62e39da8…, 누락 파일 보완은 7d19c895…입니다. 사람이 두 SHA를 임의로 할당한 것이 아닙니다."],
      ["왜 최신 기능 SHA 하나로 줄이지 않는가", "7d19c895…만 남기면 최초 commit 62e39da8…에서 변경한 8개 파일의 근거가 사라집니다. 생성기는 두 commit을 모두 읽어 현재 BANK-OM-007의 changed_paths 10개를 만듭니다."],
      ["최종 검사 대상 commit SHA", "모든 BANK-OM 변경이 들어 있는 custom branch의 마지막 상태는 SHA 하나로 검사합니다. 1.13.0은 같은 입력으로 다시 만들면 같은 결과가 나오도록 재구성한 3a2811cf…를 검사했습니다. 1.13.1 commit별 재적용 진단에는 dee330ebd5…를 사용했습니다. 두 SHA는 서로 다른 버전의 전체 코드를 가리키며 BANK-OM-007 하나만 가리키는 값이 아닙니다."],
      ["Artifact digest", "Artifact는 코드로 만든 이미지나 패키지 같은 배포 파일입니다. digest는 그 파일 내용으로 계산한 SHA-256 확인값입니다. 예: sha256:61a3…. Git commit SHA와 별개이며, 검사한 배포 파일과 실제 배포 파일이 같은지 확인할 때 사용합니다. 현재 값은 형식 예시일 뿐이며 OM_TEMP 운영 이미지를 만들었다는 증거는 아직 없습니다."]
    ],
    example: "git commit -m \"Tibero 연결 파일 누락 보완\" \\\n  -m \"Customization-ID: BANK-OM-007\"\n# Git이 새 SHA 7d19c895...를 자동 생성\n\nBANK-OM-007\n├─ 62e39da8...  최초 구현 8개 파일\n└─ 7d19c895...  누락 보완 2개 파일\n   → Manifest changed_paths = 현재 10개 파일\n\n공식 1.13.0과 같은 입력으로 다시 만든 최종 검사 대상 3a2811cf...\n   → Candidate lock candidate.commit_sha = 3a2811cf...\n   → 모든 BANK-OM을 포함한 검사 대상 하나",
    resultExample: "기능 식별: BANK-OM-007\n기능 이력: 62e39da8… + 7d19c895…\n최신 커스텀 브랜치의 기능 범위: changed_paths 10개\n1.13.0 소스 검사 대상 custom commit: 3a2811cf…\n1.13.1 commit별 재적용 진단 코드: dee330ebd5…\n실제 vendor-merge 결과 custom commit: 아직 만들지 않음",
    update: "기존 기능을 보완할 때 개발자는 같은 BANK-OM ID로 commit합니다. plan은 같은 ID의 모든 commit SHA와 변경 경로를 자동으로 찾아 Manifest changed_paths와 commit-inventory 변경안을 만듭니다. 여러 commit을 허용하는 series.allowed, required·watch·Contract는 사람이 판단합니다. apply는 승인된 변경안만 반영합니다. 이후 소스 검사를 실행하면 검사기가 custom 브랜치의 최신 commit과 전체 파일 상태로 Candidate lock을 다시 계산해 결과 JSON 안에 기록합니다.",
    caution: "기능의 마지막 commit과 custom 브랜치의 마지막 commit이 우연히 같을 수 있습니다. 그래도 쓰임은 다릅니다. 기능 범위를 만들 때는 같은 BANK-OM ID가 붙은 모든 commit을 읽고, 배포 전에는 custom 브랜치 전체를 대표하는 마지막 commit 하나를 확인합니다."
  },
  registration: {
    group: "검사 전 사전환경 상세",
    title: "새 BANK-OM 등록 절차",
    summary: "새 기능 코드를 BANK-OM ID와 함께 commit한 뒤, 사람 정책 입력과 Contract를 준비하고 plan으로 Manifest·Registry 변경안을 만듭니다. 새 ID를 설명할 사람 입력 없이 plan을 실행하면 BLOCK됩니다.",
    sections: [
      ["1. ID 발급", "미사용 BANK-OM ID를 관리자가 발급합니다."],
      ["2. 코드와 commit", "한 업무 기능 단위로 코드를 변경하고 commit 본문에 Customization-ID를 넣습니다."],
      ["3. 사람 정책 입력", "owner·criticality·required·간접 watch·series를 new-ID YAML에 작성합니다. 모르는 값을 임시로 넣지 않습니다."],
      ["4. Contract 작성", "업무 정상 조건과 필수 test를 contracts.yaml에 작성하고 customization_ids에 새 ID를 연결합니다. 준비도구가 이 내용을 대신 만들지 않습니다."],
      ["5. 변경안 생성", "plan이 같은 ID가 붙은 commit의 실제 변경 파일을 합쳐 changed_paths와 watch를 계산하고 Manifest·Registry 변경안을 만듭니다. 이때 등록 폴더는 바뀌지 않습니다."],
      ["6. 사람 승인·적용", "담당자가 required·watch·Contract·owner와 diff를 확인합니다. 승인서에는 검토한 제안의 내용 확인값(proposal digest)과 승인 사유를 적습니다. apply 명령은 승인한 제안과 확인값이 같을 때만 등록자료를 바꿉니다."],
      ["7. 검사", "APPLIED 뒤 등록자료 5종을 검사합니다. 이어서 공식 새 버전에서 출발한 검사 대상 코드로 소스 검사를 실행합니다. BLOCK이 나오면 결과 파일이 아니라 코드나 등록 입력을 수정합니다."]
    ],
    example: "# 1. 터미널에서 commit 본문에 새 ID 기록\ngit commit -m \"새 커스터마이징 기능 구현\" \\\n  -m \"Customization-ID: BANK-OM-008\"\n\n# 2. 편집기로 contracts.yaml에 CONTRACT-NEW-FEATURE 작성·승인\n# contracts[].customization_ids: [BANK-OM-008]\n\n# 3. 아래 YAML은 터미널 명령이 아닙니다.\n# 편집기로 /path/to/new-bank-om.yaml 파일에 저장합니다.\nBANK-OM-008:\n  title: 새 커스터마이징 기능\n  owner: 데이터플랫폼팀\n  owner_status: assigned\n  criticality: high\n  kind: core-patch\n  provenance: candidate-follow-up\n  required_changed_paths:\n    - openmetadata-service/.../RequiredResource.java\n  contracts:\n    - CONTRACT-NEW-FEATURE\n  direct_tests: []\n  watch_dependencies: []\n  series_allowed: false\n  depends_on: []\n\n# 4. 다시 터미널에서 읽기 전용 plan 실행\n# 등록 폴더·브랜치·결과 폴더는 도구가 버전으로 자동 선택합니다.\n./.venv/bin/python harness/om_workflow.py plan \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0 \\\n  --new-id-input /path/to/new-bank-om.yaml\n\n# 5. 이후 승인서 생성·apply·등록 검사는\n# 왼쪽 메뉴의 ‘검사 전 준비 자동화’ 절차를 그대로 실행",
    resultExample: "등록 검증 PASS 예시\n- Manifest 구조와 작성 규칙: 7개 PASS\n- Registry·Manifest·Contract 연결: 7개 PASS\n- 공식 1.13.0 ↔ 행내 custom 1.13.0 차이: 111개 경로 PASS\n- 과거 source snapshot의 공용 경로: 37개 PASS\n- 필수 Python test 코드: 9개 PASS\n\n참고: 공식 1.13.0 → 공식 1.13.1 변경은 별도 비교 축이며 834개 경로입니다.",
    update: "새 ID 등록 뒤 같은 기능의 후속 commit이 생기면 새 ID 입력을 다시 만들지 않습니다. 같은 ID를 commit 본문에 쓰고 plan을 다시 실행해 changed_paths·commit inventory 변경안을 검토합니다. required·watch·Contract 판단이 바뀌었다면 사람 정책도 함께 갱신합니다.",
    caution: "생성기가 required나 업무 invariant를 임의로 확정하지 않습니다. 자동 초안을 검토하지 않고 그대로 병합하면 기능 누락을 잘못 판단할 수 있습니다."
  },
  followup: {
    group: "작업 절차 상세",
    title: "기존 BANK-OM ID의 후속 commit",
    summary: "기존 기능의 누락 보완·버그 수정처럼 같은 업무 목적과 함께 배포되는 변경은 같은 BANK-OM ID로 후속 commit을 만들 수 있습니다.",
    sections: [
      ["1. 같은 ID 여부 판단", "업무 목적, 배포·제거 단위, 담당 조직과 Contract가 기존 기능과 같은지 확인합니다. 독립 기능이면 새 ID를 발급합니다."],
      ["2. Manifest series 확인", "같은 ID에 여러 commit을 허용하도록 series.allowed가 true인지 확인합니다."],
      ["3. 후속 commit 작성", "commit 본문에 기존 Customization-ID를 그대로 넣습니다."],
      ["4. 현재 변경 범위 갱신", "후속 commit이 새 파일을 변경했다면 changed_paths에 추가합니다. 기존 등록 파일의 내용만 수정했다면 파일명 목록은 그대로 둡니다."],
      ["5. 필수·watch·Contract 재검토", "새 파일이 기능 필수 요소인지, 공식 업그레이드 감시와 test 갱신이 필요한지 확인합니다."],
      ["6. 제안 적용·검사", "담당자가 자신이 본 것과 같은 변경안을 승인하면 apply를 실행합니다. 그 뒤 등록자료 검사와 T30·T31·T40·T93 등 영향받은 소스 검사를 다시 실행합니다. T42는 공식 버전이 바뀔 때 vendor-merge 전에 실행하며, 같은 공식 버전의 일반 후속 commit 등록에서는 다시 실행하지 않습니다. Registry source.snapshot_sha의 custom commit을 설명하는 두 연결표도 일반 후속 commit에서 다시 만들지 않습니다."]
    ],
    example: "git commit -m \"Tibero 연결 파일 누락 보완\" \\\n  -m \"Customization-ID: BANK-OM-007\"\n\n# 변경 전: 8개\nimplementation:\n  changed_paths:\n    - openmetadata-spec/.../tiberoConnection.json\n\n# 변경 후: 기존 8개 + 새 파일 2개\nimplementation:\n  changed_paths:\n    - openmetadata-spec/.../tiberoConnection.json\n    - openmetadata-ui/.../serviceConnection.ts\n    - openmetadata-ui/.../DatabaseServiceUtils.test.tsx",
    resultExample: "후속 commit 7d19c895…를 별도 기능으로 만들지 않고 BANK-OM-007에 연결\n→ series.allowed=true 확인\n→ changed_paths 8개에서 현재 전체 10개로 갱신\n→ 등록 범위 검사 PASS",
    update: "승인된 제안으로 변경 대상 Manifest와 commit-inventory.yaml·current-diff-paths.txt를 갱신합니다. Registry 변경이 필요한 경우에만 proposal에 Registry 변경을 함께 표시합니다. Contract는 사람이 직접 수정하고 새 plan으로 다시 검토합니다. Registry source.snapshot_sha의 custom commit을 바꾸는 별도 작업에서만 그 commit을 설명하는 두 연결표를 갱신합니다. Patch-lock의 개정 번호와 commit 목록은 patch-replay 전략에서만 사용합니다.",
    caution: "changed_paths는 현재 버전의 전체 범위만 보여줍니다. 어느 commit에서 파일이 추가됐는지는 Git 이력에서 확인하며, Manifest에 최초·후속 목록을 따로 만들지 않습니다."
  },
  automation: {
    group: "검사 전 사전환경 상세",
    title: "검사 전 자동 갱신 범위와 전체 실행 절차",
    summary: "담당자는 통합 실행 도구에 제품 코드 저장소 경로와 제품 버전을 입력합니다. 도구가 버전별 등록 폴더와 필요한 정책 파일을 자동으로 찾고 plan·검사 명령을 실행합니다. 필수 파일, Contract, watch, owner와 충돌 해결처럼 업무 판단이 필요한 값은 사람이 검토하고 승인합니다.",
    sections: [
      ["통합 실행 도구", "`harness/om_workflow.py`가 제품 버전으로 등록 폴더, 코드 경로 분류표, 중요 경로 정책과 기본 결과 위치를 자동 선택합니다. 사용자는 제품 코드 저장소 경로와 제품 버전을 입력하고, 새 공식 commit·실제 배포 파일처럼 도구가 추측하면 안 되는 값만 작업별로 추가합니다."],
      ["commit 직후", "Git은 새 commit SHA와 diff를 기록합니다. 준비도구가 자동으로 시작되거나 Manifest·Registry가 자동으로 바뀌지는 않습니다. 담당자가 plan 명령을 실행해야 다음 단계가 시작됩니다."],
      ["plan 실행 후", "plan은 proposal.yaml, diff.patch, commit-inventory.yaml, current-diff-paths.txt와 변경 후 파일 미리보기를 새 제안 폴더에 만듭니다. 이 단계는 읽기 전용이며 실제 버전별 등록 폴더를 수정하지 않습니다."],
      ["승인 후 apply가 갱신", "apply는 변경 대상 Manifest, commit-inventory.yaml, current-diff-paths.txt를 갱신하고 새 ID 등 Registry 변경안이 있을 때만 customization-registry.yaml도 갱신합니다. contracts.yaml과 Registry source.snapshot_sha의 custom commit을 설명하는 두 파일–BANK-OM 연결표는 일반 commit 처리에서 자동 갱신하지 않습니다."],
      ["목적", "커스터마이징 commit을 만든 뒤 검사기가 읽을 Manifest·Registry·commit inventory의 변경안을 Git 사실에 맞게 준비합니다. 준비 완료와 운영 배포 완료는 서로 다른 단계입니다."],
      ["현재 적용 예시의 두 저장소", "제품 코드 저장소는 easyseop/OM_TEMP이고 검사기 저장소는 easyseop/openmetadata-test입니다. 준비도구·Manifest·Registry·Contract는 검사기 저장소의 codex/strict-manifest-gates 작업 브랜치에서 실행·관리합니다."],
      ["실행 위치와 도구", "검사기 저장소의 최상위 폴더에서 `./.venv/bin/python harness/om_workflow.py <작업>` 형식으로 실행합니다. 제품 코드 저장소에는 원격 OpenMetadata 포크·커스텀 브랜치를 받아와야 하며 git status --short 출력이 비어 있어야 합니다."],
      ["자동 계산", "OpenMetadata 포크·커스텀 브랜치의 commit SHA, BANK-OM별 commit 순서와 변경 경로, 최종 diff, Manifest 변경안과 승인 뒤 입력 변경 여부를 계산합니다."],
      ["제안 내용 확인값", "proposal.yaml 전체 내용에서 계산한 SHA-256 값입니다. Git commit SHA와 다릅니다. 승인자가 본 변경안과 apply가 반영할 변경안이 같은지 확인하는 데 사용합니다."],
      ["등록 상태 내용 확인값", "Registry, Contract, 저장소 구조 설정, 공식 원본 기준 경로 분류 자료, 여러 BANK-OM이 함께 사용하는 경로 자료와 모든 Manifest의 내용을 묶어 계산합니다. plan 뒤 이 자료 중 하나라도 바뀌면 기존 승인을 재사용하지 않고 새 plan을 만듭니다."],
      ["검사 대상 코드(Candidate)", "승인한 공식 OpenMetadata 버전에서 출발해 BANK-OM 변경을 적용한 최종 코드입니다. 공식 Git 기록과 연결되지 않은 단순 파일 복사본은 이 검사 대상의 조건을 충족하지 않습니다."],
      ["사람 판단", "required 파일, 간접 watch 경로, Contract의 업무 정상 조건과 test, owner·criticality, 충돌 해결 코드와 최종 승인은 자동으로 확정하지 않습니다. Contract 내용은 사람이 등록자료에 직접 작성합니다."],
      ["승인과 적용", "plan이 만든 제안에 approval-template을 실행하면 아직 승인되지 않은 빈 양식이 생깁니다. 실제 승인자가 모든 질문에 사유를 적은 뒤 apply를 실행합니다. 제안 내용, Git commit, 등록 입력 중 하나라도 달라졌으면 apply가 중단됩니다."],
      ["적용 뒤 검사", "APPLIED가 나온 뒤 등록자료 5종을 검사하고, 공식 버전에서 출발한 최종 코드로 소스 검사를 실행합니다. 소스 검사 PASS는 build, 실행 환경, 배포까지 통과했다는 뜻이 아닙니다."],
      ["증거 보관", "제안 폴더 전체, 실제 승인서, apply 결과, 등록 검증 결과와 동일 Candidate lock의 후속 검사 결과를 삭제하지 않고 함께 보관합니다."]
    ],
    preparationFilesTitle: "검사 전에 준비하는 파일별 자동화 범위",
    preparationFilesIntro: "아래 표는 일반적인 후속 commit을 등록할 때를 기준으로 합니다. ‘자동’은 commit만 하면 저절로 실행된다는 뜻이 아닙니다. 담당자가 plan을 실행하고 변경안을 승인한 뒤 apply를 실행해야 실제 등록 폴더에 반영됩니다.",
    preparationFiles: [
      {
        file: "manifests/BANK-OM-xxx.yaml",
        level: "partial",
        status: "부분 자동 · 정책값은 직접 수정 필요",
        command: "om_workflow.py plan → 담당자 검토·승인 → om_workflow.py apply. changed_paths와 공식 코드에 존재하는 watch 경로는 제안되지만, required·간접 watch·Contract·series 허용 여부는 사람이 직접 확인하고 수정합니다."
      },
      {
        file: "customization-registry.yaml",
        level: "partial",
        status: "새 ID일 때만 조건부 자동",
        command: "새 ID의 담당자·중요도·Contract를 새 ID 입력 파일에 직접 작성 → om_workflow.py plan --new-id-input ... → 승인 → apply. 기존 ID의 후속 commit이면 Registry는 보통 그대로 둡니다."
      },
      {
        file: "contracts.yaml",
        level: "manual",
        status: "직접 수정 필요",
        command: "업무 정상 조건과 연결할 test를 담당자가 직접 작성 → om_workflow.py plan 재실행 → om_workflow.py validate. plan과 apply는 Contract 내용을 만들거나 고치지 않습니다."
      },
      {
        file: "commit-inventory.yaml",
        level: "auto",
        status: "자동 생성 · 직접 수정 금지",
        command: "om_workflow.py plan이 제안 폴더에 생성 → 승인 후 om_workflow.py apply가 버전별 등록 폴더에 반영합니다."
      },
      {
        file: "current-diff-paths.txt",
        level: "auto",
        status: "자동 생성 · 직접 수정 금지",
        command: "om_workflow.py plan이 포크·커스텀 브랜치의 최종 차이를 계산해 생성 → 승인 후 apply가 반영합니다."
      },
      {
        file: "source-snapshot-path-owners.yaml",
        level: "bootstrap",
        status: "초기 기준 생성만 · 일반 후속 commit에서는 유지",
        command: "제품 버전의 등록자료를 처음 만들거나 Registry source.snapshot_sha의 custom commit을 교체할 때만 om_workflow.py bootstrap을 명시적 확인 옵션과 함께 실행하고 담당자가 검토합니다. 일반 후속 commit에는 실행하지 않습니다."
      },
      {
        file: "shared-path-owners.yaml",
        level: "bootstrap",
        status: "초기 기준 생성만 · 일반 후속 commit에서는 유지",
        command: "제품 버전의 등록자료를 처음 만들거나 Registry source.snapshot_sha의 custom commit을 교체할 때만 om_workflow.py bootstrap으로 다시 생성합니다. 일반 후속 commit에서는 Manifest와 commit-inventory로 최신 커스텀 브랜치 범위를 관리합니다."
      },
      {
        file: "source-diff-paths.txt",
        level: "bootstrap",
        status: "초기 기준 생성만 · 일반 후속 commit에서는 유지",
        command: "제품 버전의 등록자료를 처음 만들거나 Registry source.snapshot_sha의 custom commit을 교체할 때만 om_workflow.py bootstrap으로 다시 생성합니다. 최신 커스텀 브랜치의 commit 범위는 current-diff-paths.txt에서 확인합니다."
      },
      {
        file: "repository-layout.yaml",
        level: "manual",
        status: "직접 수정 필요",
        command: "제품 코드의 폴더 구조나 경로 분류 규칙이 바뀔 때 담당자가 직접 수정 → om_workflow.py plan 재실행 → om_workflow.py validate."
      },
      {
        file: "sensitive-zones.yaml",
        level: "manual",
        status: "직접 수정 필요",
        command: "중요 경로의 범위나 허용 기준이 바뀔 때 담당자가 직접 수정 → om_workflow.py validate → om_workflow.py source."
      },
      {
        file: "proposal.yaml · diff.patch · review-required.yaml · summary.md",
        level: "auto",
        status: "plan 실행 시 자동 생성 · 직접 수정 금지",
        command: "om_workflow.py plan이 겹치지 않는 새 제안 폴더를 자동으로 만듭니다. 결과를 직접 고치지 말고 입력 코드나 관리 파일을 수정한 뒤 plan을 다시 실행합니다."
      },
      {
        file: "registration-approval.yaml",
        level: "partial",
        status: "양식만 자동 · 승인 내용은 직접 작성 필요",
        command: "om_workflow.py approval-template로 빈 양식 생성 → 실제 승인자가 approved_by·approved_at·모든 판단 사유를 직접 작성 → om_workflow.py apply."
      }
    ],
    preparationFilesNote: "빨간색 ‘직접 수정 필요’ 파일은 준비도구가 업무 의미를 추측해 대신 작성하지 않습니다. 수정한 뒤에는 기존 proposal이나 승인서를 재사용하지 말고 새 출력 폴더에서 plan을 다시 실행한 다음 등록 검증을 다시 수행합니다. 현재 digest는 주요 등록자료와 제안 내용을 고정하지만, 준비도구 자체의 Git commit이나 버전을 승인서에 별도 필드로 고정하는 기능은 추가 설계 대상입니다.",
    conditionTitle: "준비도구가 진행 전에 확인하는 조건",
    conditionIntro: "담당자가 아래 조건을 하나씩 직접 검사할 필요는 없습니다. 담당자가 plan 명령을 한 번 실행하면 준비도구가 조건을 자동으로 확인하고, 터미널과 summary.md에 전체 상태와 건수를 표시합니다. 문제가 있으면 proposal.yaml의 blocked 또는 analysis_errors에 문제 코드·설명을 남기고 중단합니다. 다만 준비도구는 commit 뒤 자동으로 시작되지 않으므로 plan 명령 자체는 담당자가 실행해야 합니다.",
    conditionMap: [
      ["제품 코드 저장소의 작업 폴더", "commit하지 않은 수정과 Git에 아직 등록하지 않은 새 파일이 없는지 git status로 확인", "출력이 비어 있으면 Git 분석 진행", "로컬 변경이 있으면 BLOCK. 올바른 BANK-OM ID로 commit하거나 제품 코드 저장소 밖으로 옮긴 뒤 plan 재실행"],
      ["포크·커스텀 브랜치 관계", "두 브랜치를 정확한 commit SHA로 고정하고 커스텀 브랜치가 OpenMetadata 포크 브랜치의 공식 코드에서 이어지는지 확인", "포크 브랜치 뒤에 커스텀 commit이 이어지면 분석 진행", "두 브랜치 이력이 이어지지 않거나 분석하지 못하는 merge 구조이면 ANALYSIS_ERROR. 포크·커스텀 브랜치와 fetch 상태를 바로잡음"],
      ["commit의 BANK-OM ID", "각 commit 본문에서 Customization-ID를 읽음", "commit마다 정확히 한 ID가 있으면 기능별 이력 생성", "ID 없음·여러 ID·merge·빈 commit이면 BLOCK. commit 이력을 수정한 뒤 새 plan 생성"],
      ["변경 경로 영역", "각 commit의 파일을 제품 Core·행내 전용·검사기 관리자료 영역으로 분류", "한 commit이 한 영역만 변경하면 진행", "영역 혼합·미분류 경로·영역 분류 불일치면 BLOCK 또는 ANALYSIS_ERROR"],
      ["파일 형식 안전성", "custom 브랜치의 코드에 다른 위치를 가리키는 symlink, 별도 제품 코드 저장소를 가리키는 submodule, Git LFS 자리표시자가 있는지 확인", "일반 파일이면 Manifest 변경안 계산", "지원하지 않는 파일 형식이 있으면 BLOCK. 자동으로 실제 내용을 추측하지 않음"],
      ["사람 정책", "실제 변경 경로와 기존 required·watch·Contract·Registry를 비교", "Git 사실과 기존 정책이 일치하면 READY 또는 변경안 생성", "업무 판단이 필요하면 REVIEW_REQUIRED, 필수 경로 소실·폐기 ID 재사용이면 BLOCK"],
      ["승인 후 입력 고정", "제안 내용 확인값, 포크·커스텀 commit과 등록자료 내용 확인값을 apply 직전에 다시 비교", "승인한 시점과 모두 같으면 다른 apply 작업을 막은 뒤 적용", "하나라도 바뀌면 STALE_PROPOSAL로 BLOCK. 기존 승인서를 고치지 않고 plan부터 다시 실행"],
      ["동시 적용과 파일 쓰기", "한 번에 하나의 apply만 실행되도록 잠그고, 모든 새 파일이 준비된 뒤 기존 파일을 교체", "잠금을 확보하고 모든 파일을 쓰면 APPLIED", "APPLY_LOCKED면 다른 작업 종료 여부를 확인. 파일 쓰기에 실패하면 이번에 바꾼 파일을 원래 상태로 복구하고 중단"]
    ],
    conditionNote: "확인 순서는 summary.md에서 전체 상태와 문제 건수를 본 뒤, BLOCKED이면 proposal.yaml의 blocked, ANALYSIS_ERROR이면 analysis_errors, REVIEW_REQUIRED이면 review-required.yaml을 여는 방식입니다. 조건표의 각 항목을 별도 명령으로 반복 검사하거나 결과 파일의 상태값을 직접 편집하지 않습니다. 원인이 된 제품 코드·OpenMetadata 포크 브랜치·커스텀 브랜치·등록 입력을 수정한 뒤 새 출력 폴더에 plan을 다시 실행합니다.",
    outcomeTitle: "준비도구 상태별 다음 행동",
    outcomeIntro: "준비도구가 실행됐는지는 plan 출력 폴더의 summary.md와 proposal.yaml로 확인합니다. 두 파일이 없으면 준비도구를 실행하지 않은 것이므로 plan부터 실행합니다. 파일이 있으면 아래 상태에 맞는 조치를 합니다. 이 상태는 배포 판정이 아닙니다.",
    outcomeMap: [
      ["READY · 종료코드 0", "자동 계산이 끝났고 사람 질문·차단·분석 오류가 없음", "diff.patch와 proposal.yaml을 검토하고 승인서를 작성", "READY를 자동 승인이나 배포 가능으로 해석하지 않음"],
      ["REVIEW_REQUIRED · 종료코드 2", "도구가 대신 결정하면 안 되는 업무 질문이 남음", "review-required.yaml의 모든 검토 항목 ID를 실제 담당자가 확인하고 질문별 사유 기록", "실패로 오해해 정책을 삭제하거나 자리표시자 승인서를 사용하지 않음"],
      ["BLOCKED · 종료코드 1", "확인된 안전 위반 때문에 제안을 적용할 수 없음", "터미널의 code와 proposal의 blocked 항목을 수정한 뒤 새 plan 생성", "BLOCK 상태에서 apply 실행 또는 결과값 직접 수정 금지"],
      ["ANALYSIS_ERROR · 종료코드 3", "포크·커스텀 브랜치 관계, commit, 경로 또는 등록자료 형식을 믿을 수 없어 분석을 끝내지 못함", "원격 포크·커스텀 브랜치 정보, Git commit, 등록자료 형식을 바로잡은 뒤 plan 재실행", "검사 결과가 없으므로 승인 단계로 이동하지 않음"],
      ["APPLIED · 종료코드 0", "승인한 동일 제안이 등록자료에 반영됨", "apply 결과를 보관하고 등록 검증 5종과 소스 검사를 새로 실행", "APPLIED를 기능 test·build·운영 배포 완료로 표현하지 않음"],
      ["STALE_PROPOSAL", "승인 뒤 branch의 마지막 commit 또는 등록 입력이 바뀌어 승인이 현재 상태와 다름", "기존 승인서를 증거로 보관한 뒤 새 plan과 새 승인 생성", "승인서의 내용 확인값이나 commit SHA를 손으로 고쳐 재사용하지 않음"],
      ["APPLY_LOCKED", "다른 apply 작업이 등록 폴더를 사용 중이거나 잠금이 남음", "다른 작업 종료 여부와 담당자를 확인하고 필요하면 운영 책임자에게 상신", "작업자 확인 없이 잠금 파일 삭제 금지"]
    ],
    outcomeNote: "현재 적용 예시인 OM_TEMP 1.13.0 준비 결과는 REVIEW_REQUIRED입니다. 자동으로 바꿀 파일은 없지만, 공식 원본에는 없고 행내 코드에만 있는 watch 경로를 계속 유지할지 확인할 질문 5건이 남았습니다. 따라서 아직 승인과 apply를 실행하지 않았습니다.",
    walkthrough: [
      ["0. 준비", "개발자", "검사기 저장소 루트, .venv, 변경 중인 파일이 없는 제품 코드 저장소 clone과 fetch된 포크·커스텀 브랜치를 확인", "git -C /path/to/OM_TEMP status --short 출력이 비어 있음"],
      ["1. 제안 생성", "개발자", "om_workflow.py plan에 제품 코드 저장소 경로와 제품 버전 전달. 도구가 등록 폴더·두 브랜치·새 출력 폴더를 자동 선택", "화면의 자동 선택 목록과 결과 폴더의 summary.md 생성"],
      ["2. 제안 범위 확인", "개발자·기능 담당자", "summary.md → review-required.yaml → diff.patch 순서로 확인", "상태, 질문·차단 건수, 승인 시 바뀔 파일을 설명할 수 있음"],
      ["3. 상세 근거 확인", "검토자", "proposal.yaml, commit-inventory.yaml, current-diff-paths.txt에서 고정 SHA와 BANK-OM별 경로 확인", "Git diff와 Manifest 변경안이 같은 commit 범위를 가리킴"],
      ["4. 승인 양식 생성", "개발자", "om_workflow.py approval-template에 proposal.yaml 경로를 전달", "같은 폴더에 registration-approval.yaml 생성. 아직 실제 승인이 아님"],
      ["5. 사람 승인", "실제 승인자", "approved_by·approved_at과 모든 검토 항목의 구체적인 reason을 작성", "자리표시자가 없고 review-required.yaml의 검토 항목 ID를 정확히 한 번씩 포함"],
      ["6. 승인안 적용", "개발자", "om_workflow.py apply에 제품 코드 저장소·버전·proposal·실제 승인서를 전달. 등록 폴더와 결과 경로는 자동 선택", "APPLIED와 written_files 출력 또는 상태별 중단 결과"],
      ["7. 등록 검증", "개발자", "om_workflow.py validate에 제품 코드 저장소 경로와 버전 전달", "자동 선택된 등록자료의 검사 5종이 모두 pass"],
      ["8. 소스 검사", "개발자·검토자", "공식 새 버전에서 출발한 커스텀 브랜치를 준비하고 om_workflow.py source 실행", "자동 선택된 정책으로 만든 Candidate lock과 8개 소스 검사 결과"],
      ["9. 증거 보관·인계", "변경관리 담당자", "제안 폴더·승인서·apply 결과·검사 결과·Candidate lock을 같은 변경 기록에 보관", "다음 담당자가 commit, 내용 확인값, 승인자, 실행 결과를 다시 확인할 수 있음"]
    ],
    comparison: {
      title: "plan 실행 전후에 실제로 바뀌는 위치",
      beforeTitle: "실행 전: 등록 폴더는 현재 승인본",
      before: "harness/registrations/om-temp-1.13.0/\n├─ manifests/\n├─ customization-registry.yaml\n├─ contracts.yaml\n└─ source-snapshot-path-owners.yaml",
      afterTitle: "plan 실행 후: 등록 폴더는 그대로, 제안 폴더만 추가",
      after: "harness/registrations/om-temp-1.13.0/  # 변경 없음\n\nharness/preparation-plans/om-temp-1.13.0-20260730/\n├─ summary.md\n├─ review-required.yaml\n├─ diff.patch\n├─ proposal.yaml\n├─ proposal-digest.txt\n├─ commit-inventory.yaml\n├─ current-diff-paths.txt\n└─ proposed-registration/\n\n# approval-template 명령 후 지정한 별도 위치에 생성\n/approved/location/registration-approval.yaml",
      note: "plan은 등록자료와 승인서를 수정하지 않습니다. approval-template은 별도의 빈 승인 양식만 만듭니다. 사람이 같은 변경안을 승인하고 apply가 APPLIED로 끝났을 때만 Manifest, commit-inventory.yaml, current-diff-paths.txt와 필요한 Registry가 바뀝니다. Contract와 Registry source.snapshot_sha의 custom commit을 설명하는 연결표는 apply가 자동으로 작성하거나 갱신하지 않습니다."
    },
    exampleTitle: "단계별 실행 명령",
    exampleIntro: "아래 블록 전체를 한 번에 복사해 실행하는 것이 아닙니다. 0번부터 한 단계씩 실행하고, 각 단계의 주석에 적힌 예상 결과를 확인한 뒤 다음 번호로 이동합니다. 1번 plan 결과가 BLOCKED 또는 ANALYSIS_ERROR이면 2번으로 가지 않고 원인을 수정해 plan부터 다시 실행합니다. REVIEW_REQUIRED이면 담당자 검토와 승인을 거친 뒤 2~4번을 진행합니다. 4번 결과가 APPLIED일 때만 5번 등록 검사를 실행합니다.",
    exampleStepShells: true,
    example: "# 0. 실행 위치와 Git 입력 준비\n# 검사기 저장소의 최상위 폴더에서 한 단계씩 실행합니다.\n# /path/to/OM_TEMP만 실제 제품 코드 저장소 clone 경로로 바꿉니다.\ngit -C /path/to/OM_TEMP fetch origin fork/om-1.13.0 custom/om-1.13.0\ngit -C /path/to/OM_TEMP status --short\n# 완료 조건: status --short 출력이 비어 있음\n# 파일명이 출력되면 멈추고 commit하지 않은 변경을 먼저 처리합니다.\n\n# 1. 읽기 전용 제안 생성\n# 등록 폴더·두 브랜치·새 결과 폴더는 버전으로 자동 선택됩니다.\n./.venv/bin/python harness/om_workflow.py plan \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0\n# 완료 증거: 화면의 ‘자동으로 선택한 입력’을 확인하고 새 결과 폴더의 summary.md를 읽습니다.\n# READY 또는 REVIEW_REQUIRED이면 2번으로 이동합니다.\n# BLOCKED 또는 ANALYSIS_ERROR이면 표시된 원인을 고친 뒤 1번을 다시 실행합니다.\n\n# 새 BANK-OM ID를 등록할 때만 1번 명령에 아래 옵션을 추가합니다.\n# --new-id-input /path/to/new-bank-om.yaml\n\n# 2. 빈 승인 양식 생성\n# 1번 화면에 표시된 결과 폴더의 proposal.yaml 경로를 넣습니다.\n./.venv/bin/python harness/om_workflow.py approval-template \\\n  --proposal /path/to/proposal.yaml\n# 완료 조건: 같은 폴더에 registration-approval.yaml이 생김\n# 주의: 아직 빈 양식이므로 승인이 아닙니다.\n\n# 3. 사람 승인\n# 승인자가 registration-approval.yaml의 자리표시자를 모두 바꾸고 판단 사유를 적습니다.\n\n# 4. 승인한 제안 적용\n./.venv/bin/python harness/om_workflow.py apply \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0 \\\n  --proposal /path/to/proposal.yaml \\\n  --approval /path/to/registration-approval.yaml\n# 완료 조건: status가 APPLIED이고 실제 변경 파일이 표시됨\n\n# 5. 등록자료 5종 검사\n./.venv/bin/python harness/om_workflow.py validate \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0\n# 완료 조건: 결과 JSON의 5개 checks가 모두 pass\n\n# 6. 소스 검사\n# 제품 코드 저장소가 공식 버전에서 출발한 커스텀 브랜치를 가리키는지 먼저 확인합니다.\n./.venv/bin/python harness/om_workflow.py source \\\n  --repo /path/to/OM_TEMP \\\n  --version 1.13.0\n# 완료 조건: T25·T26 등 8개 소스 검사 결과와 Candidate lock이 생성됨\n# 이 결과만으로 build·기능 test·운영 배포가 완료된 것은 아닙니다.",
    resultExample: "현재 적용 예시 · OM_TEMP 1.13.0 plan 실제 결과\n{\n  \"status\": \"REVIEW_REQUIRED\",\n  \"change_count\": 0,\n  \"review_count\": 5,\n  \"blocked_count\": 0,\n  \"analysis_error_count\": 0,\n  \"proposal_digest\": \"sha256:502a6824bb60e02b0d6cf4a66043e9e5d9ec0b22ed70b2c3387437b738d278b7\"\n}\n\n정확한 해석\n- Git 분석과 기존 등록자료 비교는 완료됨\n- 자동으로 적용할 Manifest·Registry 변경은 0건\n- 공식 OpenMetadata 포크 브랜치에 없는 기존 watch 경로를 유지할지 기능별 질문 5건이 남음\n- 승인서 자리표시자는 실제 승인으로 인정되지 않음\n- 승인·apply는 아직 실행하지 않음\n\n집중 회귀 테스트\ncd harness\n../.venv/bin/python -m pytest \\\n  tests/test_registration_prep.py \\\n  tests/test_gitprim.py \\\n  tests/test_candidate.py \\\n  tests/test_registration_validation_workflow.py \\\n  tests/test_source_candidate_workflow.py\n결과: 42 passed\n범위: 등록자료·소스 검사. 전체 build·runtime·운영 배포 증거가 아님",
    evidence: [
      ["OM_TEMP_통합실행도구_사용법.md", "통합 실행 도구 사용법", "작업별 짧은 명령, 자동 선택되는 파일과 사람이 입력할 값을 확인합니다."],
      ["OM_TEMP_검사전_준비도구_쉬운사용법.md", "검사 전 준비도구 쉬운 사용법", "준비 조건, 전체 명령, 결과별 복구와 증거 보관을 확인합니다."],
      ["OM_TEMP_검사전_자동화_구현_코드안내_20260730.md", "자동화 구현·코드 안내", "CLI·분석기·Git 입력·스키마·테스트의 실제 역할과 완료 범위를 확인합니다."],
      ["../../harness/om_workflow.py", "통합 실행 도구", "버전별 경로 자동 선택과 plan·validate·source·watch·risk·runtime 등 단순화된 명령을 확인합니다."],
      ["../../harness/prepare_registration.py", "등록 준비 내부 CLI", "통합 실행 도구가 호출하는 plan·approval-template·apply 구현과 상태별 종료코드를 확인합니다."],
      ["../../harness/acgh/registration_prep.py", "자동화 핵심 구현", "Git 분석, 사람 질문 분리, digest 승인, 잠금·원자 적용·rollback을 확인합니다."],
      ["../../harness/preparation-plans/om-temp-1.13.0-20260730/summary.md", "실제 1.13.0 제안 요약", "REVIEW_REQUIRED와 자동 변경 0·사람 판단 5를 확인합니다."],
      ["../../harness/preparation-plans/om-temp-1.13.0-20260730/review-required.yaml", "실제 사람 판단 질문", "기능별 watch 보존 질문과 proposal digest를 확인합니다."],
      ["../../harness/tests/test_registration_prep.py", "준비 자동화 회귀 테스트", "정상·후속 commit·ID 오류·stale 승인·잠금·rollback 사례를 확인합니다."]
    ],
    update: "같은 제품 commit과 등록 입력을 다시 볼 때는 기존 제안·승인·결과를 수정하지 않습니다. 코드 commit, branch의 마지막 commit, Manifest·Registry·Contract, 생성기 또는 파일 작성 규칙 중 하나라도 바뀌면 새 출력 폴더에서 plan을 다시 실행하고 새 제안 내용 확인값으로 승인받습니다.",
    caution: "통합 실행 도구는 경로와 반복 옵션을 자동 선택하지만 commit 이후 스스로 시작되거나 Pull Request를 만들지는 않습니다. 담당자가 작업 명령을 실행해야 하며, 도구는 사람 정책과 충돌 해결 코드를 결정하지 않습니다. APPLIED와 소스 gate PASS만으로 전체 build·runtime·운영 배포가 완료됐다고 표현하지 않습니다."
  },
  upgrade: {
    group: "OM_TEMP 업그레이드 상세",
    title: "공식 버전 업그레이드 절차",
    summary: "공식 새 버전을 OpenMetadata 포크 브랜치에 준비한 뒤 영향 경로를 먼저 확인하고, 새 커스텀 브랜치에서 직전 BANK-OM 이력과 합칩니다. 충돌 해결·소스 검사·환경 test를 통과하면 검증 완료 태그를 만들고, 승인 후 릴리즈 브랜치를 같은 commit으로 갱신합니다.",
    sections: [
      ["1. OpenMetadata 포크 브랜치 준비", "공식 태그와 commit을 확인해 fork/om-<새버전>을 고정합니다."],
      ["2. 사전 영향 확인", "T42로 공식 A→B 변경과 upgrade_watch를 비교합니다."],
      ["3. vendor-merge", "새 커스텀 브랜치에서 직전 BANK-OM 이력과 새 OpenMetadata 포크 브랜치의 공식 코드를 병합합니다."],
      ["4. 충돌 해결", "공식 변경과 BANK-OM 의도를 모두 확인해 custom branch에 해결 commit을 남깁니다."],
      ["5. 등록 변경안 승인·반영", "최종 커스텀 브랜치를 기준으로 plan을 실행합니다. 담당자는 Manifest·Registry 변경안과 required·watch·Contract 질문을 검토하고 승인한 뒤 apply를 실행합니다. Contract 변경이 필요하면 담당자가 직접 수정합니다."],
      ["6. 재검사", "소스 검사, build, Contract test, 업그레이드 test와 배포 일치 검사를 실행합니다."],
      ["7. 검증 완료 태그·릴리즈 승격", "같은 검사 대상 코드와 그 코드로 만든 배포 파일의 검사가 끝난 뒤 검증 완료 태그와 Release lock을 만들고, 승인 후 릴리즈 브랜치를 같은 commit으로 갱신합니다."]
    ],
    example: "fork/om-1.13.1 ───┐\n                    ├─ custom/om-1.13.1의 검사 대상 commit → 검사 → 검증 완료 태그\ncustom/om-1.13.0 ─┘                                                        ↓ 승인\n                                                                 release/om-1.13.1 → 운영",
    resultExample: "현재 적용 예시 · OM_TEMP 1.13.1 연습 결과\n- BANK-OM-001~004: 언어 JSON 18개 경로에서 충돌\n- BANK-OM-005~007: 충돌 없이 적용\n- 충돌 해결 후 소스 검사: PASS\n- 전체 build·행내 Runtime test: 아직 실행 증거 없음\n- 1.13.1 commit별 재적용 진단 브랜치와 진단 코드: 현재 로컬 작업 기록이며 easyseop/OM_TEMP 원격 브랜치·tag로 확인되지 않음",
    update: "최종 커스텀 브랜치에서 plan을 실행해 새 버전 Manifest와 파생 등록자료 변경안을 만듭니다. Registry 변경이 필요한 경우에만 proposal에 함께 표시하며 Contract는 업무 동작이나 필수 test가 바뀌었을 때 담당자가 직접 갱신합니다. 검사 대상 commit이나 그 코드로 만든 배포 파일이 바뀌면 Candidate lock과 이후 검사 결과를 모두 새로 만듭니다.",
    caution: "현재 OM_TEMP 1.13.1 연습은 BANK-OM별 충돌 진단을 위해 commit별 재적용을 사용했습니다. 이것을 실제 vendor-merge 완료 증거로 표현하지 않습니다."
  },
  conflicts: {
    group: "OM_TEMP 업그레이드 상세",
    title: "Git 충돌과 해결 보조 도구",
    summary: "공식 코드와 BANK-OM이 JSON의 서로 다른 항목을 바꿨는데도 Git이 자동 병합을 멈추는 경우가 있습니다. 이 보조 도구는 두 변경을 함께 넣은 해결 파일 초안을 만듭니다. 어느 값이 업무상 맞는지는 결정하지 않으므로 담당자가 diff와 test를 확인해야 합니다.",
    sections: [
      ["1. 왜 사용하는가", "언어 JSON처럼 한 파일이 크면 공식 버전은 파일 뒤쪽을 바꾸고 BANK-OM은 중간에 새 항목을 추가했어도 Git이 같은 큰 구간을 충돌로 표시할 수 있습니다. 도구는 실제 JSON 항목 단위로 다시 비교해 함께 보존 가능한 변경인지 계산합니다."],
      ["2. 언제 사용할 수 있나", "이 Python 도구는 Git이 BANK-OM commit을 재적용하다 JSON 충돌로 멈춘 제품 코드 저장소 작업 폴더에서만 사용합니다. 일반 JSON 파일 정리 도구나 모든 브랜치 병합 충돌 해결기가 아닙니다."],
      ["3. 같은 충돌 파일에서 읽는 세 버전", "Git은 충돌한 파일의 공통 기준(BASE), 현재 작업 브랜치 내용(OURS), 병합해 들어오는 변경(THEIRS)을 함께 보관합니다. Git 명령에서는 각각 stage 1·2·3으로 표시하지만 숫자는 작업 순서가 아닙니다."],
      ["4. 무엇을 비교하나", "도구는 BASE와 OURS를 비교해 현재 branch가 바꾼 JSON 항목을 찾고, BASE와 THEIRS를 비교해 들어오는 쪽이 바꾼 항목을 찾습니다. 예를 들어 label 안의 instance-code는 label.instance-code로 표시합니다. 줄 번호나 들여쓰기는 비교하지 않습니다."],
      ["5. 자동으로 합치는 조건", "두 변경 목록에 같은 JSON 항목이 하나도 없을 때만 OURS 전체를 유지하고 THEIRS에서 바뀐 항목을 추가·수정·삭제합니다. 이번 연습에서는 OURS가 공식 1.13.1, THEIRS가 BANK-OM입니다."],
      ["6. 자동으로 중단하는 조건", "양쪽이 같은 JSON 항목을 하나라도 변경했으면 최종 값이 같더라도 중단합니다. JSON 이외 파일이 충돌하거나 JSON을 읽을 수 없어도 중단합니다. 이때 도구가 임의로 값을 선택하지 않으며 담당자가 직접 비교해야 합니다."],
      ["7. 도구가 실제로 남기는 것", "성공하면 작업 폴더의 충돌 JSON을 다시 쓰고 터미널에 적용한 BANK-OM 항목 수를 출력합니다. Git 상태에는 아직 충돌 미해결로 표시됩니다. 별도 승인 보고서나 결과 파일은 만들지 않습니다."],
      ["8. 사람이 이어서 하는 일", "git diff와 test로 수정 결과를 확인한 뒤 git add로 해당 파일을 '충돌 해결 확인' 상태로 바꿉니다. 이번 재적용 연습은 cherry-pick으로 시작했으므로 cherry-pick --continue를 사용했습니다. 실제 custom 브랜치 병합 중 충돌이었다면 merge --continue 또는 해결 commit을 사용합니다."]
    ],
    stageMap: [
      ["stage 1 · BASE", "양쪽 변경이 시작되기 전 공통 내용", "공식 1.13.0과 BANK-OM이 갈라지기 전 JSON", "git show :1:<파일경로>", "현재 branch와 들어오는 쪽의 변경을 계산하는 기준"],
      ["stage 2 · OURS", "현재 열어 둔 branch의 내용", "이번 연습에서는 공식 1.13.1 JSON", "git show :2:<파일경로>", "해결 파일의 바탕으로 사용"],
      ["stage 3 · THEIRS", "현재 적용하려는 반대편 변경", "이번 연습에서는 BANK-OM-001 commit의 JSON", "git show :3:<파일경로>", "BANK-OM이 바꾼 JSON 항목을 계산"]
    ],
    stageNote: "이번 연습은 공식 1.13.1 코드가 있는 작업 브랜치에 BANK-OM commit 하나를 적용했으므로 stage 2가 공식 코드이고 stage 3이 BANK-OM입니다. 일반 브랜치 병합에서도 stage 2는 현재 작업 브랜치, stage 3은 병합해 들어오는 브랜치입니다. 병합 방향을 바꾸면 공식 코드와 BANK-OM의 위치도 바뀔 수 있습니다.",
    conditionMap: [
      ["충돌 파일 선별", "git diff --name-only --diff-filter=U로 아직 충돌 중인 파일 목록을 읽음", "모두 .json이면 다음 비교 진행", "JSON 이외 파일이 하나라도 있으면 모든 JSON을 쓰기 전에 중단"],
      ["현재 작업 브랜치 변경 계산", "BASE와 OURS의 JSON 항목별 값을 비교", "현재 작업 브랜치가 바꾼 항목 목록 생성", "JSON 문법이 틀렸거나 최상위 값이 객체가 아니면 파일을 쓰기 전에 중단"],
      ["들어오는 변경 계산", "BASE와 THEIRS의 JSON 항목별 값을 비교", "들어오는 쪽이 추가·수정·삭제한 항목 목록 생성", "JSON 문법이 틀렸거나 최상위 값이 객체가 아니면 파일을 쓰기 전에 중단"],
      ["두 목록 겹침 확인", "양쪽 변경 목록에 같은 JSON 항목이 있는지 확인", "겹치는 항목이 없으면 OURS에 THEIRS 변경 반영", "한 항목이라도 겹치면 최종 값이 같아도 파일을 쓰기 전에 중단"],
      ["반영 가능 여부", "THEIRS 변경을 OURS JSON 구조에 넣을 수 있는지 확인", "가능하면 파일을 쓰고 적용한 항목 수 출력", "중간 JSON 구조가 달라 넣을 수 없으면 중단. git status와 diff로 이미 쓴 파일이 있는지 확인"]
    ],
    conditionNote: "이번 BANK-OM-001 결과는 언어 JSON 18개 모두에서 겹치는 최종 항목이 0개였으므로 자동 작성 조건을 통과했습니다. 이 조건 통과는 JSON 병합 가능 여부만 뜻하며 기능 test PASS를 뜻하지 않습니다.",
    outcomeMap: [
      ["resolved ... leaf changes=9", "공식 JSON을 바탕으로 BANK-OM의 마지막 항목 9개를 넣은 작업 파일을 만들었다는 뜻", "git diff로 9개 항목과 공식 항목 보존 여부를 확인하고 JSON·관련 기능 test 실행", "확인 전에는 git add나 Git 작업 계속 실행 금지"],
      ["git status에 UU", "도구가 파일 내용은 썼지만 Git에는 아직 충돌 미해결로 남아 있다는 뜻", "검토와 test를 통과한 파일만 git add", "UU를 도구 실패로 오해해 다시 실행하지 않음"],
      ["overlapping leaf changes", "공식과 BANK-OM이 같은 JSON 항목을 둘 다 변경했다는 뜻", "자동 선택을 중단하고 두 값과 업무 의도를 담당자·승인자가 직접 결정", "결정 전 git add·continue 금지"],
      ["unresolved non-JSON conflicts", "Java·TypeScript 등 이 보조 도구가 처리하지 않는 충돌이 함께 있다는 뜻", "해당 파일을 일반 Git 충돌 해결 절차로 직접 비교·수정", "JSON 도구로 비JSON 코드를 자동 해결하려 하지 않음"],
      ["test 실패", "JSON 형식은 합쳐졌지만 실제 기능 조건을 만족하지 못했다는 뜻", "git add 전이면 파일을 다시 수정하고 test 재실행. 이미 add했다면 수정 후 다시 add", "test가 PASS할 때까지 cherry-pick/merge 완료 금지"]
    ],
    outcomeNote: "보조 도구는 해결 파일 초안까지만 만듭니다. 담당자는 diff 확인, JSON·관련 기능 test PASS, git add, 시작한 Git 작업 완료, 해결 commit과 검사 결과 보관까지 마쳐야 합니다.",
    walkthrough: [
      ["1", "Git", "BANK-OM 변경을 적용하다 충돌한 JSON을 stage 1·2·3으로 보관", "git diff --name-only --diff-filter=U에 충돌 파일 표시"],
      ["2", "담당자", "resolve_nonoverlapping_json_conflicts.py에 충돌 중인 제품 코드 저장소의 로컬 경로 전달", "도구가 JSON 이외 충돌 여부와 동일 항목 겹침 여부를 먼저 검사"],
      ["3", "보조 도구", "공식 1.13.1 JSON을 기준으로 겹치지 않는 BANK-OM 항목만 적용", "작업 폴더의 JSON 수정 + 터미널에 파일별 적용 항목 수 출력"],
      ["4", "담당자", "git diff와 JSON·기능 test로 수정 결과 확인", "공식 항목 유지와 BANK-OM 항목 추가를 모두 확인"],
      ["5", "담당자", "확인한 파일만 git add 후 시작한 Git 작업을 계속", "재적용 연습이면 cherry-pick --continue, custom 브랜치 병합이면 merge --continue 또는 해결 commit"]
    ],
    comparison: {
      title: "BANK-OM-001 ko-kr.json 실제 실행 전후",
      beforeTitle: "실행 전: Git이 선택하지 못해 남긴 충돌",
      before: "<<<<<<< HEAD  (공식 1.13.1)\n\"zoom-out\": \"축소\"\n=======\n\"instance-code\": \"인스턴스 코드\",\n\"sort-order\": \"Sort Order\"\n>>>>>>> 4df83b311f  (BANK-OM-001)",
      afterTitle: "실행 후: 공식 JSON에 BANK-OM 항목을 추가",
      after: "\"zoom-out\": \"축소\",\n\"code-group\": \"Code Group\",\n\"code-name\": \"Code Name\",\n\"code-value\": \"Code Value\",\n\"instance-code\": \"인스턴스 코드\",\n\"instance-code-lowercase-plural\": \"인스턴스 코드\",\n\"instance-code-plural\": \"인스턴스 코드\",\n\"sort-order\": \"Sort Order\"",
      note: "이 충돌은 같은 한 줄을 서로 다른 값으로 바꾼 경우가 아닙니다. 공식 코드와 BANK-OM이 같은 큰 JSON 객체 안의 서로 다른 위치를 편집해 Git이 자동 병합을 멈춘 경우입니다. 보조 도구는 JSON 항목 이름을 비교했고 같은 항목을 함께 바꾼 경우가 없어 두 변경을 모두 보존했습니다."
    },
    example: "# 전제: Git이 JSON 충돌로 멈춘 작업 폴더\n# 세 버전을 직접 확인하는 명령(실제 파일 경로 사용)\ngit show :1:openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json\ngit show :2:openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json\ngit show :3:openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json\n\n# 보조 도구 실행\n# 제품 코드 저장소 경로만 입력하면 나머지 입력은 Git 충돌 상태에서 자동으로 읽습니다.\n./.venv/bin/python harness/om_workflow.py resolve-json \\\n  --repo /path/to/OM_TEMP\n\n# 성공 출력\nresolved .../languages/ko-kr.json: BANK-OM leaf changes=9\n\n# 도구 직후: 파일 내용은 해결됐지만 Git index는 아직 U(충돌 미해결)\ngit status --short\nUU openmetadata-ui/.../languages/ko-kr.json\n\n# 사람이 결과와 test를 확인한 뒤에만 해결로 표시\ngit diff -- .../languages/ko-kr.json\ngit add .../languages/ko-kr.json\ngit cherry-pick --continue",
    resultExample: "성공 시 터미널 출력\nresolved openmetadata-ui/.../languages/ko-kr.json: BANK-OM leaf changes=9\n\n이 한 줄의 정확한 뜻\n- 도구가 stage 2의 공식 JSON을 바탕으로 새 파일 내용을 작성함\n- stage 1→stage 3에서 찾은 BANK-OM 최종 항목 9개를 그 파일에 반영함\n- '검사 PASS'나 'Git 충돌 해결 완료'를 뜻하지 않음\n\n도구 실행 직후 상태\n- 작업 폴더 JSON: 충돌 표식 없이 공식 1.13.1 항목 + BANK-OM-001 항목이 함께 있음\n- Git index: git add 전이므로 아직 UU(충돌 미해결)\n- 별도 산출물: 없음. 결과는 수정된 JSON과 터미널 출력뿐임\n\n도구가 자동 실행하지 않는 것\n- git add·commit·test·cherry-pick --continue\n- 별도 결과 보고서·승인 파일·plan.json 생성\n\nBANK-OM-001 실제 전체 결과\n- 충돌한 언어 JSON: 고유 경로 18개\n- 각 파일에서 BANK-OM이 추가한 최종 항목: 9개\n- 공식과 BANK-OM이 동시에 바꾼 동일 항목: 0개\n- 담당자가 diff와 test를 확인한 뒤 남긴 해결 commit: 83b1e0ac7d…\n\n동일 항목이 겹칠 때의 실패 출력\nValueError: .../ko-kr.json: overlapping leaf changes: ['label.instance-code']\n→ 도구는 계획한 JSON을 하나도 쓰지 않고 중단\n→ 담당자가 공식 값과 BANK-OM 값을 비교하고 승인받은 값으로 직접 해결\n\nJSON 이외 충돌이 있을 때의 실패 출력\nValueError: unresolved non-JSON conflicts require manual review: ['.../Entity.java']\n→ 이 보조 도구의 처리 범위가 아니므로 파일을 수정하지 않음",
    evidence: [
      ["../../harness/tools/resolve_nonoverlapping_json_conflicts.py", "실제 JSON 충돌 보조 도구", "stage 1(BASE)·2(OURS)·3(THEIRS)를 읽고, BASE→OURS와 BASE→THEIRS의 최종 JSON 항목 목록을 비교하며, 같은 항목 또는 JSON 외 충돌에서 중단하는 구현을 확인합니다."],
      ["../../harness/registrations/om-temp-1.13.1/conflict-evidence/BANK-OM-001_ko-kr_full_conflict.txt", "Git이 남긴 실제 충돌 파일", "공식 1.13.1과 BANK-OM 양쪽 전체 내용 및 충돌 표식을 확인합니다."],
      ["../../harness/registrations/om-temp-1.13.1/conflict-evidence/BANK-OM-001_ko-kr_resolution.diff", "해결 전후 실제 diff", "공식 1.13.1 JSON을 유지하면서 BANK-OM 항목 9개가 추가된 결과를 확인합니다."],
      ["../../harness/registrations/om-temp-1.13.1/conflict-evidence/BANK-OM-001_ko-kr_resolved.json", "해결된 전체 JSON", "도구 실행 후 최종 파일 전체를 확인합니다."],
      ["../../harness/registrations/om-temp-1.13.1/upgrade-application-results.json", "BANK-OM별 1.13.1 적용 결과", "충돌 경로 수, 동일 항목 겹침 수와 결과 commit을 확인합니다."]
    ],
    update: "충돌 해결로 Manifest에 없던 파일을 새로 수정했다면 changed_paths와 필요한 watch를 갱신하고, 동작 조건이 바뀌면 Contract를 갱신합니다.",
    caution: "이 도구는 이번 OM_TEMP commit별 재적용 연습을 위해 만든 제한 도구이며 행내 표준 승인 절차로 확정되지 않았습니다. 성공해도 기능 정상은 확정되지 않으므로 JSON 문법, Manifest 범위, Contract test와 전체 build를 다시 실행합니다."
  },
  block_action: {
    group: "작업 절차 상세",
    title: "BLOCK·APPROVAL·ANALYSIS ERROR 조치",
    summary: "판정마다 조치 주체와 재실행 위치가 다릅니다. 결과 파일의 verdict를 직접 바꾸지 않고 원인을 수정한 뒤 새 검사를 실행합니다.",
    sections: [
      ["BLOCK", "코드·Manifest·Contract·필수 test 등 확인된 위반을 담당자가 수정합니다. 같은 검사와 영향을 받는 후속 검사를 다시 실행합니다."],
      ["APPROVAL", "자동 실패는 아니지만 reasons에 적힌 경로·재시도·중요 변경을 책임자가 검토하고 승인 근거를 남깁니다."],
      ["ANALYSIS ERROR", "commit 객체 누락, stale lock, 잘못된 경로·스키마처럼 검사 입력을 수정합니다. 검사 미완료이므로 승인으로 넘어가지 않습니다."],
      ["NOT RUN", "필요한 환경·artifact·권한을 준비하고 실제 검사를 실행합니다. 결과가 없는 상태를 PASS로 표시하지 않습니다."],
      ["중단·상신 시점", "BLOCK·ANALYSIS ERROR·NOT RUN은 다음 병합·tag·배포 단계로 진행하지 않습니다. APPROVAL은 지정된 기술 승인권자가 reasons와 근거 링크를 확인하기 전까지 진행하지 않습니다."],
      ["승인 기록", "검사 run ID, 검사 대상 commit, 판정 이유, 검토한 diff·test 링크, 조치 내용, 승인자와 승인 시각을 PR 또는 조직이 정한 승인 기록에 남깁니다. 현재 검사기 저장소에는 조직 표준 승인 양식이 없으므로 운영 도입 전에 정해야 합니다."],
      ["재검사 결과", "이전 결과를 덮어쓰지 않고 새 run ID와 digest를 가진 결과로 보관합니다."]
    ],
    example: "BLOCK: required_path_missing\n  → Manifest를 억지로 삭제하지 않음\n  → 누락 코드 또는 잘못된 required 판단 수정\n  → T26·T40·T62 재실행\n  → 새 결과 파일 생성",
    resultExample: "수정 전: T26 | BLOCK | required_path_missing: .../InstanceCodeResource.java\n코드 또는 required 판단 수정 후 재실행\n수정 후: T26 | PASS | BANK-OM-001 필수 파일 확인\n이전 BLOCK 결과 파일은 삭제하지 않음",
    update: "원인에 따라 OpenMetadata 코드, Manifest·Registry·Contract, Candidate lock 또는 실행 환경을 갱신합니다. 어떤 파일을 바꿨는지는 새 결과의 inputs와 Git diff에 남깁니다.",
    caution: "결과 JSON·YAML의 verdict나 reasons를 직접 편집해 PASS로 만들면 result_digest와 실제 검사 증거가 맞지 않습니다."
  },
  evidence: {
    group: "검사 결과 상세",
    title: "검사 결과를 읽는 순서",
    summary: "전체 PASS 문구만 보지 않고 먼저 어떤 제품 코드 저장소·commit·배포 파일을 검사했는지 확인한 뒤 각 검사의 판정과 이유, 실행하지 않은 범위를 읽습니다.",
    sections: [
      ["1. 검사 대상", "제품 코드 저장소, OpenMetadata 포크·커스텀·릴리즈 브랜치, 검사 대상 commit, 공식 기준과 배포 파일 내용 확인값이 현재 검토 대상과 같은지 확인합니다."],
      ["2. 전체 판정", "PASS·APPROVAL·BLOCK·ANALYSIS ERROR 중 전체 결과를 확인합니다."],
      ["3. 개별 gate", "gates[].name·verdict·reasons에서 무엇이 통과·실패했는지 확인합니다."],
      ["4. 실행 범위", "소스 검사인지 Runtime test인지, NOT RUN 항목이 무엇인지 확인합니다."],
      ["5. 다음 조치", "BLOCK은 수정 후 재검사, APPROVAL은 담당자 근거·승인, ANALYSIS ERROR는 입력을 고친 뒤 재실행합니다."]
    ],
    example: "PASS: 해당 검사 조건만 통과\nAPPROVAL: 담당자 확인·승인 필요\nBLOCK: 코드·등록자료 수정 후 재검사\nANALYSIS ERROR: 검사 미완료, PASS로 간주 금지\nNOT RUN: 아직 결과 없음",
    resultExample: "OM_TEMP 1.13.0 source-gate-results.json 예시\ncandidate_lock.candidate.commit_sha: 3a2811cf…\ncandidate_lock.candidate.artifact_kind: source-tree\ngates[T40].verdict: pass\ngates[T40].reasons: 실제 변경 경로와 Manifest 일치\n주의: 소스 tree 검사 결과이며 Runtime·릴리즈 브랜치·운영 배포 완료 증거는 아님",
    update: "새 검사 실행 결과를 만들 때 이전 결과를 수정하지 않고 검사 대상 Git commit SHA와 run ID가 다른 새 파일로 보관합니다.",
    caution: "소스 검사 PASS만으로 행내 환경 동작이나 운영 배포 완료를 뜻하지 않습니다. 현재 검사기 저장소에는 CI 보관 기간과 별개로 검사 증거를 장기간 보관할 조직 저장 위치와 보존 기간이 정의돼 있지 않습니다. 이 정책과 저장 위치를 정하기 전에는 감사 대응이 가능한 운영 절차가 완성됐다고 표현하지 않습니다."
  },
  release: {
    group: "검사 결과 상세",
    title: "검증 완료 태그·릴리즈 브랜치·배포 승인",
    summary: "검증 완료 태그는 필수 검사를 통과한 정확한 Git commit을 고정합니다. 운영 승인 후 릴리즈 브랜치가 그 태그와 같은 commit을 가리키게 하고, 실제 운영은 릴리즈 브랜치를 기준으로 배포합니다.",
    sections: [
      ["검증 완료 태그", "예: verified/om-1.13.1-bank.1. 검사 완료 commit을 움직이지 않게 표시하지만 운영 배포 완료를 뜻하지 않습니다."],
      ["릴리즈 브랜치", "예: release/om-1.13.1. 운영 승인 후 검증 완료 태그와 같은 commit을 가리키며 실제 운영 배포가 읽는 기준선입니다."],
      ["Candidate lock", "검사한 commit·tree·artifact를 고정합니다."],
      ["Release lock", "릴리즈 브랜치, 검증 완료 태그, 검사 결과, test 결과, 이미지와 Helm digest를 하나의 승격 대상으로 묶습니다."],
      ["T91", "릴리즈 브랜치와 실제 배포 관측값이 Release lock과 같고 검증 후 재빌드하지 않았는지 확인합니다."],
      ["사람 승인", "APPROVAL 사유, 운영 일정, rollback과 책임자를 확인한 뒤 최종 승인합니다."]
    ],
    example: "커스텀 commit → Candidate lock → 필수 검사 PASS\n→ 검증 완료 태그 → Release lock·운영 승인\n→ 릴리즈 브랜치를 같은 commit으로 갱신 → T91 일치 확인 → 운영 배포",
    resultExample: "2026-07-30 문서 기준 확인 결과\n- 1.13.0 소스 검사를 다시 수행한 custom commit 3a2811cf…: 등록 검증 5종·소스 검사 8종 PASS\n- 1.13.1 commit별 재적용 진단 코드 dee330ebd5…: 충돌 위치 확인용 기록이며 운영 배포 대상 코드가 아님\n- 실제 vendor-merge 결과 commit, Runtime·업그레이드·배포 환경 결과: 아직 없음\n- 검증 완료 태그, Release lock, 릴리즈 브랜치 승격 증거: 아직 없음\n따라서 2026-07-30 상태를 운영 배포 승인 완료라고 표현하지 않음",
    update: "코드·artifact·Helm 중 하나라도 바뀌면 기존 태그·lock 결과를 재사용하지 않고 새 검사 대상 commit과 검사 결과를 만듭니다. 릴리즈 브랜치는 새 검증 완료 태그와 Release lock·승인을 준비한 뒤에만 새 commit으로 이동합니다.",
    caution: "같은 소스에서 재빌드한 이미지라도 digest가 달라지면 검증한 artifact와 동일하지 않으므로 다시 검사해야 합니다. 현재는 담당자가 승인 근거를 확인해 Release lock에 승인 정보를 기록합니다. 승인 ID 자동 발급과 승인 완료 전 릴리즈 브랜치 이동을 자동 차단하는 최종 게이트는 아직 없으며, 추가 개발과 조직 정책 결정 대상입니다."
  }
};

window.WIKI_TOPIC_OPERATION_CASES = {
  repositories: [
    [
      "제품 코드 저장소와 검사기 저장소의 URL·역할, OpenMetadata 포크·커스텀·릴리즈 브랜치, 공식 버전과 검사 대상 commit이 모두 이전 점검 때와 같은 경우",
      "바꾸지 않음",
      "운영 담당자는 두 저장소 링크가 열리고 권한이 유지되는지만 확인합니다. Registry, Manifest와 검사 명령은 수정하지 않습니다.",
      "새 검사 결과를 만들지 않습니다. 링크 확인 일자와 확인자만 정기 점검 기록에 남깁니다."
    ],
    [
      "두 저장소의 역할과 URL 및 공식 버전은 그대로지만, 커스텀 브랜치의 최종 commit만 바뀐 경우",
      "해당 제품 버전의 검사 대상 custom branch commit과 등록자료만 갱신",
      "개발자는 같은 BANK-OM ID로 후속 commit을 만들고 준비도구 plan을 실행합니다. 담당자는 Manifest와 파생 등록자료 변경안을 승인합니다. Registry 변경이 필요한 경우에만 proposal에 Registry 변경이 표시됩니다.",
      "apply 뒤 등록 검증과 T30·T31·T40·T93 등 영향받은 소스 검사를 실행합니다. 공식 버전이 같으므로 T42는 다시 실행하지 않습니다."
    ],
    [
      "두 저장소의 역할과 URL은 그대로지만 공식 목표 버전이 바뀐 경우",
      "새 버전 등록자료와 공식 비교 결과를 별도로 준비",
      "업그레이드 담당자는 새 버전의 OpenMetadata 포크 브랜치와 등록 폴더 초안을 준비합니다. 이전 공식 버전과 새 공식 버전으로 T42를 먼저 실행한 뒤, 영향받을 BANK-OM ID와 경로를 확인하고 vendor-merge를 진행합니다.",
      "vendor-merge와 충돌 해결이 끝난 최종 커스텀 브랜치로 plan·승인·apply를 실행합니다. 기존 버전 폴더를 덮어쓰지 않고 새 제안·승인서·검사 결과를 함께 보관합니다."
    ],
    [
      "제품 코드 저장소의 URL이 바뀌거나, 제품 코드 저장소와 검사기 저장소를 다른 저장소로 분리·통합한 경우",
      "저장소 연결 구조를 다시 정함",
      "운영 책임자가 어느 저장소가 제품 코드와 검사자료를 각각 관리할지 먼저 승인합니다. 담당자는 Registry의 source.repository, CI checkout URL, 실행 명령의 로컬 경로, 접근 권한과 위키의 현재 적용 예시를 새 구조에 맞게 바꿉니다.",
      "구조 변경 승인 기록과 이전·새 URL 대응표를 보관합니다. 준비도구 plan, 등록 검증과 소스 검사를 새 저장소 연결로 모두 다시 실행하고 첫 성공 결과를 남깁니다."
    ]
  ],
  branches: [
    ["같은 공식 버전의 커스텀 브랜치에 기존 BANK-OM 기능의 후속 commit만 추가한 경우", "OpenMetadata 포크 브랜치는 유지하고 검사 대상 custom branch commit만 갱신", "같은 BANK-OM ID로 commit하고 Manifest 변경안을 확인합니다. 커스텀 브랜치의 마지막 commit이 바뀌므로 새 Candidate lock과 검사 결과를 만듭니다. 기존 릴리즈 브랜치는 검사·승인 전까지 움직이지 않습니다.", "영향받은 소스·기능 검사를 다시 실행하고 새 검증 완료 태그와 Release lock을 준비한 뒤 승인 후 릴리즈 브랜치를 갱신합니다."],
    ["공식 목표 버전이 1.13.1에서 다음 버전으로 바뀐 경우", "새 버전용 포크·커스텀·릴리즈 브랜치를 준비", "새 공식 코드를 담은 OpenMetadata 포크 브랜치와 그 코드를 BANK-OM 변경과 합칠 커스텀 브랜치를 만듭니다. Candidate lock에는 새 공식 commit과 새 커스텀 브랜치의 마지막 commit을 기록합니다. 릴리즈 브랜치는 승인 전에는 만들거나 이동하지 않습니다.", "T42 사전 영향 확인 → 커스텀 브랜치 병합 → 충돌 해결 → 전체 검사 → 검증 완료 태그·Release lock → 승인 → 릴리즈 브랜치 갱신 순서로 진행합니다."],
    ["vendor-merge 대신 다른 통합 전략을 채택한 경우", "전략·도식·검사 입력을 모두 다시 정함", "책임자가 새 전략을 승인한 뒤 어느 브랜치에서 무엇을 합치는지, 충돌을 어디서 해결하는지, Patch-lock이 필요한지와 실제 명령을 문서에 반영합니다.", "전략 승인 기록을 보관하고 T25·T30·T40·T93의 입력과 판정 방식이 새 전략에서도 맞는지 다시 검토합니다."]
  ],
  identity: [
    [
      "제품 코드와 commit 이력이 이전 승인 때와 같은 경우",
      "바꾸지 않음",
      "[자동 처리] 새 commit이 없으므로 준비도구가 제안할 변경도 없습니다. [담당자 확인] BANK-OM ID, Manifest와 commit-inventory를 수정하지 않습니다. 기존 검사 결과 안의 Candidate lock도 손으로 고치지 않습니다.",
      "추가 조치가 없습니다. 정기 점검이 필요한 경우에만 제품 코드 저장소의 최종 commit과 기존 검사 결과의 대상이 같은지 확인한 기록을 남깁니다."
    ],
    [
      "기존 BANK-OM 기능의 누락을 보완하는 새 commit을 custom 브랜치에 추가한 경우",
      "commit 발견·경로 계산·파일 반영은 자동, 기능 기준은 담당자가 승인",
      "[개발자 입력] 기존 BANK-OM ID를 commit 본문에 적고 plan을 실행합니다. [자동 처리] plan이 같은 ID의 모든 commit SHA와 실제 변경 경로를 찾아 changed_paths·commit-inventory 변경안을 만듭니다. [담당자 판단] 여러 commit 허용 여부, 필수 파일, 업그레이드 감시 경로와 Contract가 맞는지 확인하고 승인합니다. [자동 처리] apply가 승인된 변경안만 관리 파일에 반영합니다.",
      "plan 제안·승인서·apply 결과를 보관하고 등록 검증과 T30·T31·T40·T93을 실행합니다. 이어서 소스 검사를 실행하면 검사 대상 custom 브랜치의 최종 commit과 파일 상태가 Candidate lock으로 자동 계산되어 결과 JSON 안에 기록됩니다."
    ],
    [
      "기존 BANK-OM 기능과 별도로 배포하거나 제거할 수 있는 새 기능을 만든 경우",
      "새 ID와 기능 기준은 담당자가 정하고, 변경안 생성·반영은 자동",
      "[담당자 판단] 새 BANK-OM ID를 발급하고 담당 조직, 필수 파일, 업그레이드 감시 경로와 Contract를 입력합니다. [개발자 입력] 새 ID를 commit 본문에 적습니다. [자동 처리] plan이 commit과 변경 경로를 읽어 Manifest·Registry 변경안과 commit 목록을 만듭니다. [담당자 승인] 생성된 기준이 실제 기능과 맞는지 확인합니다. [자동 처리] apply가 승인된 변경안만 관리 파일에 반영합니다.",
      "신규 등록 검증 전체와 관련 소스·Contract 검사를 실행합니다. 제안 폴더, 승인서, apply 결과와 첫 검사 결과를 함께 보관합니다. 소스 검사 결과의 Candidate lock도 검사 실행 때 자동 생성됩니다."
    ]
  ],
  registration: [
    ["등록된 코드·경로·업무 조건이 바뀌지 않음", "그대로 유지", "Manifest·Registry·Contract와 자동 생성 목록을 다시 만들지 않음", "정기 검사에서 기존 입력의 내용 확인값 확인"],
    ["같은 ID가 이미 등록된 파일의 내용만 수정", "commit 기록과 자동 생성 목록 갱신", "같은 ID의 새 commit을 기록하되 changed_paths의 파일명 목록은 그대로 유지", "새 plan과 승인 후 T30·T31·T40·T93"],
    ["새 파일·필수 조건·간접 의존·test가 생김", "관련 관리 파일 갱신", "changed_paths 갱신, required·watch·Contract는 담당자가 다시 판단", "새 plan과 승인 후 등록 검사와 관련 Contract test"]
  ],
  followup: [
    ["기존 등록 파일 안의 코드만 수정", "경로 목록은 그대로 유지", "같은 ID로 commit하고 기능별 commit 목록에 새 SHA 추가. changed_paths 파일명은 중복 추가하지 않음", "새 plan과 승인 후 T30·T31·T40·T93"],
    ["기존 기능에 새 파일을 추가", "현재 범위 갱신", "changed_paths에 새 경로 추가하고 required·watch·Contract 해당 여부 판단", "등록 검사와 T26·T40·T93 등 영향받은 소스 검사. T42는 공식 버전 업그레이드 때 별도로 실행"],
    ["업무 목적·배포 단위가 기존 기능과 달라짐", "기존 ID를 갱신하지 않음", "새 ID를 발급하고 별도 Manifest·Contract 작성", "신규 등록 절차 실행"]
  ],
  automation: [
    ["같은 commit·같은 등록 입력의 제안을 다시 조회", "기존 파일 그대로 유지", "기존 제안·승인·결과를 수정하지 않고 제안 내용 확인값과 보관 위치만 확인", "추가 실행 없음. 재실행이 필요하면 새 출력 폴더 사용"],
    ["기존 BANK-OM에 새 commit 또는 새 파일 추가", "새 plan과 새 승인 필요", "같은 ID로 commit한 뒤 changed_paths 변경안과 required·watch·Contract 질문 검토", "새 proposal·승인 보관 후 apply, 등록 검사와 영향 gate 재실행"],
    ["신규 BANK-OM ID 발견", "사람 정책 입력 추가 후 새 plan", "owner·criticality·required·Contract를 new-ID 입력에 작성하고 담당자 승인", "신규 Registry·Manifest 제안 검토 후 전체 등록 검사"],
    ["OpenMetadata 포크·커스텀 브랜치의 마지막 commit 또는 등록자료가 승인 뒤 변경", "기존 승인 재사용 금지", "STALE_PROPOSAL 결과를 보관하고 현재 입력으로 plan부터 다시 실행", "새 제안 내용 확인값 승인·apply·등록 검사"],
    ["생성기 출력·Manifest 스키마·CI 동작 변경", "코드·위키·테스트 함께 갱신", "생성 파일, 상태·종료코드, 승인 지점, 실패 복구와 증거 보관 설명 수정", "42개 집중 회귀 테스트와 전체 harness·CI 실행"],
    ["BLOCKED·ANALYSIS_ERROR 발생", "자동화 설명은 그대로 유지", "blocked·analysis_errors가 가리킨 Git·코드·등록 입력만 수정", "결과를 편집하지 않고 새 plan 실행"]
  ],
  upgrade: [
    ["같은 검사 대상 custom branch commit을 입력 변경 없이 다시 확인", "관리 입력은 그대로 유지", "Manifest·Candidate lock은 수정하지 않고 새 run ID로 결과만 추가", "실패했던 검사와 후속 검사 재실행"],
    ["공식 목표 버전 또는 검사 대상 custom branch commit이 바뀜", "새 버전 입력으로 갱신", "새 등록 폴더·Candidate lock 생성, 기존 결과는 보존", "T42부터 전체 업그레이드 흐름 재실행"],
    ["충돌 해결 중 새 경로·동작 조건이 생김", "해당 기능 등록 갱신", "같은 BANK-OM ID의 changed_paths·watch·Contract를 재판단", "등록 검사·소스 검사·Contract test 재실행"]
  ],
  conflicts: [
    ["Git 충돌이 없거나 충돌 파일에 JSON 이외 파일이 포함됨", "보조 도구를 사용하지 않음", "충돌이 없으면 그대로 진행. 비JSON 충돌은 사람이 일반 Git 절차로 해결", "병합 후 소스·기능 검사"],
    ["JSON 충돌이고 OURS/THEIRS 변경 항목이 겹치지 않음", "보조 도구로 해결 파일 초안 작성", "resolved 출력 후 diff와 test 확인. 기존 등록 경로만 남으면 Manifest 경로는 그대로 유지", "확인한 파일만 git add 후 Git 작업 계속"],
    ["같은 JSON 항목이 겹치거나 해결로 새 경로·동작이 생김", "자동 진행 중단 및 등록 재판단", "값은 담당자·승인자가 결정. 새 경로는 changed_paths, 간접 영향은 watch, 동작 변경은 Contract 갱신", "승인 기록 후 관련 등록·소스·기능 검사 전체 재실행"]
  ],
  block_action: [
    ["PASS이며 검사 대상 SHA·입력이 현재 검토 대상과 같음", "코드·관리 파일 그대로 유지", "결과를 수정하지 않고 다음 검사 또는 승인 단계로 이동", "해당 결과와 입력 digest 보관"],
    ["BLOCK·APPROVAL 원인이 코드나 관리 기준임", "원인 파일만 갱신", "reasons가 가리킨 코드·Manifest·Contract를 수정하거나 승인 근거 기록", "같은 검사와 영향을 받는 후속 검사 새 run으로 실행"],
    ["ANALYSIS ERROR·NOT RUN 원인이 환경이나 잘못된 입력임", "업무 기준은 그대로 유지", "SHA·경로·권한·서버·artifact 입력을 바로잡음", "결과 파일을 편집하지 않고 새 run 생성"]
  ],
  evidence: [
    ["기존 결과를 단순 조회·보고", "그대로 유지", "결과 JSON·YAML을 편집하지 않고 해당 SHA·run ID를 인용", "원본 digest와 저장 위치 유지"],
    ["같은 검사 대상 release commit을 환경 복구 후 재검사", "새 결과 추가", "기존 실패·SKIP 결과를 남기고 새 run ID 결과 생성", "이전·새 결과와 변경된 환경 근거 함께 보관"],
    ["검사 대상 commit·artifact·설정이 바뀜", "새 검사 묶음 생성", "새 Candidate lock 또는 Release lock과 전체 결과 생성", "이전 검사 결과와 섞지 않고 revision별 보관"]
  ],
  release: [
    ["검사한 commit·artifact·Helm digest가 모두 같고 승인 유효", "기존 lock과 tag 유지", "검증 후 재빌드 없이 같은 대상을 배포 단계로 전달", "T91로 실제 배포 관측값 일치 확인"],
    ["코드·이미지·패키지·Helm 중 하나라도 변경", "새 검사 대상 commit·검증 완료 태그·lock 생성", "기존 검증 완료 태그를 옮기지 않고 새 revision·digest·검사 결과 생성. 릴리즈 브랜치는 새 승인이 끝날 때까지 기존 commit 유지", "Runtime·업그레이드·T91 재실행 후 Release lock 승인과 릴리즈 브랜치 갱신"],
    ["배포 관측값이 Release lock과 다름", "배포 승인 중단", "실제 배포 대상과 빌드·설정 변경 원인 조사", "일치하는 artifact로 교체하거나 새 검사 대상 release commit 전체 재검사"]
  ]
};

Object.entries(window.WIKI_TOPIC_OPERATION_CASES).forEach(([key, cases]) => {
  if (window.WIKI_TOPICS[key]) {
    window.WIKI_TOPICS[key].operationCases = cases;
  }
});
