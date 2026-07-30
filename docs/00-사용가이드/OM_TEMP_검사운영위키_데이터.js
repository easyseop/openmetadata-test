window.WIKI_GATES = {
  t25r: {
    group: "소스·등록 검사",
    title: "T25-R · 과거 보관 소스 재구성 확인",
    question: "공식 변경 기록 없이 파일 상태만 남은 과거 행내 소스를 공식 원본과 등록자료로 같은 내용까지 다시 만들 수 있는가?",
    status: "구현·단위 테스트 완료 · 현재 OM_TEMP에는 공식 변경 기록이 있어 실행 대상 아님",
    statusLevel: "neutral",
    timing: "과거 행내 소스의 Git 변경 기록이 없고 파일 snapshot만 남은 경우에만 T25 대신 실행합니다. 현재 OM_TEMP처럼 공식 버전과 BANK-OM commit 이력이 남아 있으면 사용하지 않습니다.",
    inputs: [
      ["공식 원본과 과거 보관 소스", "재구성의 시작 코드와 최종 비교 대상", "공식 1.13.0 · 과거 행내 source snapshot"],
      ["Manifest와 과거 코드 경로 소유정보", "파일별 BANK-OM 적용 범위와 재구성 순서", "source-snapshot-path-owners.yaml"],
      ["전체 변경 파일 목록", "공식 원본과 과거 보관 소스가 다른 전체 경로", "source-diff-paths.txt"]
    ],
    steps: [
      "공식 원본에서 시작해 과거 코드 경로 소유정보에 따라 BANK-OM 변경을 기능별로 복원합니다.",
      "다시 만든 코드와 과거 보관 소스의 파일 목록이 같은지 확인합니다.",
      "JSON은 공백·줄바꿈·항목 순서가 달라도 항목 경로와 값이 같으면 같은 내용으로 판단합니다.",
      "Java·TypeScript·Python 등 나머지 파일은 바이트 단위 내용이 같은지 확인합니다."
    ],
    verdicts: [
      ["PASS", "다시 만든 파일 목록과 내용이 과거 보관 소스와 같습니다."],
      ["BLOCK", "누락·추가 파일이 있거나 파일 내용이 다릅니다."],
      ["ANALYSIS ERROR", "공식 원본, 과거 snapshot 또는 경로 소유정보가 없어 재구성을 신뢰할 수 없습니다."]
    ],
    limit: "재구성 결과가 과거 파일 상태와 같다는 사실만 확인합니다. 빈 줄 차이도 JSON 이외 파일에서는 불일치가 될 수 있으며, 기능 동작 정상은 Contract test가 따로 확인합니다.",
    command: "# 현재 OM_TEMP는 공식 commit 이력이 남아 있어 T25-R을 실행하지 않습니다.\n# 과거 snapshot만 남은 대상에 사용하는 T25-R 전용 CLI는 아직 제공되지 않습니다.\n# 구현의 단위 테스트만 확인하려면 다음 명령을 실행합니다.\n./.venv/bin/pytest -q harness/tests/test_vendor_rebuild.py",
    resultExample: "실행 상태 | 이번 대상에서는 실행하지 않음\n이 문장은 PASS·APPROVAL·BLOCK 같은 검사 판정이 아닙니다.\n현재 OM_TEMP는 공식 1.13.0과 BANK-OM commit 이력을 보존하므로 T25로 출발점을 확인합니다.",
    output: "과거 source snapshot 재구성 결과에 누락·추가·내용 불일치 경로가 남습니다. 과거 코드 복원 담당자가 Manifest와 source-snapshot-path-owners.yaml 중 잘못된 입력을 확인합니다.",
    code: ["harness/acgh/vendor_rebuild.py", "harness/tests/test_vendor_rebuild.py"]
  },
  t25: {
    group: "소스·등록 검사",
    title: "T25 · 공식 버전 출발점 확인",
    question: "검사할 행내 코드가 승인한 공식 OpenMetadata 버전을 실제 Git 이력에 포함하는가?",
    status: "구현·단위 테스트 완료 · 현재 근거는 재검증을 마친 OM_TEMP 1.13.0 후보 3a2811cf… 결과 · 1.13.1 결과 파일은 Manifest v2 도입 이전 산출물이고 후보 branch가 원격에 없어 재검증 대기",
    statusLevel: "pass",
    timing: "vendor-merge로 공식 코드와 BANK-OM 변경을 합친 검사 대상 코드를 만든 뒤, 다른 소스 검사를 시작하기 전에 실행합니다.",
    inputs: [
      ["Candidate lock", "공식 새 버전 commit, 검사 대상 commit·tree와 실제 통합 방식", "현재 진단: 공식 afcb2d2… · 후보 dee330ebd5… · 커밋별 재적용"],
      ["검사 대상 OpenMetadata Git 저장소", "위 세 commit 객체와 Git 포함 관계를 조회할 저장소", "/workspace/OM_TEMP"]
    ],
    steps: [
      "Candidate lock에 적힌 공식 이전 버전, 공식 새 버전과 검사 대상 commit이 저장소에 존재하는지 확인합니다.",
      "검사 대상 commit과 전체 파일 상태가 Candidate lock의 값과 같은지 확인합니다.",
      "공식 이전·새 버전에 공통 Git 이력이 있는지 확인합니다.",
      "공식 이전 버전과 승인한 새 공식 버전이 모두 검사 대상 commit의 이력에 포함되는지 확인합니다."
    ],
    verdicts: [
      ["PASS", "승인한 공식 새 버전이 검사 대상 이력에 포함되고 lock 값도 일치합니다."],
      ["BLOCK", "공식 이전 또는 새 버전이 검사 대상 이력에 포함되지 않습니다."],
      ["ANALYSIS ERROR", "commit 객체가 없거나 lock 값이 현재 코드와 달라 신뢰할 수 있는 판단을 할 수 없습니다."]
    ],
    limit: "공식 코드를 포함했다는 사실만 확인합니다. 병합 과정에서 BANK-OM 기능이 올바르게 유지됐는지는 T26과 실제 테스트가 따로 확인합니다.",
    command: "./.venv/bin/python harness/run_source_candidate_gates.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\\n  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \\\n  --output harness/registrations/om-temp-1.13.0/source-gate-results.json",
    resultExample: "T25 | PASS\n공식 1.13.1 commit afcb2d2…가 진단 후보 dee330ebd5…의 Git 이력에 포함됨\n주의: 이 결과는 공식 출발점만 확인하며 실제 vendor-merge 수행 증거는 아님",
    output: "통합 소스 검사 결과 source-gate-results.json의 T25 항목에 판정과 이유가 남습니다. 업그레이드 담당자와 검토 책임자가 공식 버전 출발점이 맞는지 확인합니다.",
    code: ["harness/acgh/ancestry.py", "harness/tests/test_ancestry.py"]
  },
  t26: {
    group: "소스·등록 검사",
    title: "T26 · 필수 커스터마이징 유지 확인",
    question: "공식 새 버전을 적용한 뒤에도 모든 active BANK-OM 기능의 필수 코드와 Contract 연결이 남아 있는가?",
    status: "구현·단위 테스트 완료 · 현재 근거는 재검증을 마친 OM_TEMP 1.13.0 후보 3a2811cf… 결과 · 1.13.1 결과 파일은 Manifest v2 도입 이전 산출물이고 후보 branch가 원격에 없어 재검증 대기",
    statusLevel: "pass",
    timing: "vendor-merge 후보가 만들어지고 Manifest·Registry·Contract가 준비된 뒤 실행합니다.",
    inputs: [
      ["Candidate lock", "공식 새 버전과 검사 대상 commit", "공식 afcb2d2… · 진단 후보 dee330ebd5…"],
      ["Manifest", "required_changed_paths, 전체 기대 경로, assurance", "BANK-OM-007 · .../tiberoConnection.json · CONTRACT-TIBERO-CONNECTOR"],
      ["Registry·Contract catalog", "active ID와 Contract·필수 test 연결", "BANK-OM-007 active → test_tibero.py::test_connection_schema_roundtrip"]
    ],
    steps: [
      "Registry에서 active BANK-OM ID를 가져옵니다.",
      "각 ID의 Manifest와 required_changed_paths가 비어 있지 않은지 확인합니다.",
      "필수 파일이 검사 대상 코드에 존재하고 공식 새 버전과 실제로 다른지 확인합니다.",
      "필수 이외의 등록 파일이 사라졌거나 공식 원본과 같아졌다면 담당자 검토 대상으로 표시합니다.",
      "Contract가 존재하고 같은 BANK-OM ID를 역방향으로 참조하며 필수 test로 연결되는지 확인합니다."
    ],
    verdicts: [
      ["PASS", "모든 active 기능의 필수 코드와 Contract·test 연결이 확인됩니다."],
      ["APPROVAL", "필수로 지정하지 않은 등록 파일이 사라졌거나 공식 코드와 같아져 담당자 확인이 필요합니다."],
      ["BLOCK", "필수 파일, Manifest, Contract 또는 필수 test 연결이 없습니다."],
      ["ANALYSIS ERROR", "검사 대상 commit이나 Candidate lock을 신뢰할 수 없어 검사할 수 없습니다."]
    ],
    limit: "필수 파일이 존재하고 공식 원본과 다르다는 사실을 확인할 뿐, 그 코드가 올바르게 동작한다는 뜻은 아닙니다. T62 실행 결과가 필요합니다.",
    command: "./.venv/bin/python harness/run_source_candidate_gates.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\\n  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \\\n  --output harness/registrations/om-temp-1.13.0/source-gate-results.json",
    resultExample: "T26 | PASS\nactive_customizations=7 · BANK-OM-007 필수 파일과 Contract 연결 확인",
    output: "통합 소스 검사 결과 source-gate-results.json의 T26 항목에 기능별 누락 여부가 남습니다. 기능 담당자와 배포 검토자가 BLOCK·APPROVAL 사유를 확인합니다.",
    code: ["harness/acgh/survival.py", "harness/tests/test_survival.py"]
  },
  t30: {
    group: "소스·등록 검사",
    title: "T30 · 커밋별 BANK-OM ID 확인",
    question: "공식 코드 영역을 변경한 각 commit에 정확히 하나의 등록된 BANK-OM ID가 있는가?",
    status: "구현·단위 테스트 완료 · 현재 근거는 재검증을 마친 OM_TEMP 1.13.0 후보 3a2811cf… 결과 · 1.13.1 결과 파일은 Manifest v2 도입 이전 산출물이고 후보 branch가 원격에 없어 재검증 대기",
    statusLevel: "pass",
    timing: "BANK-OM commit이 추가될 때마다, 소스 후보 검사에서 실행합니다.",
    inputs: [
      ["Git commit 이력", "공식 기준 이후의 각 commit 메시지와 변경 파일", "7d19c895… 본문: Customization-ID: BANK-OM-007"],
      ["Repository layout", "공식 코드·행내 거버넌스·알 수 없는 경로의 구분", "openmetadata-ui/** = 공식 코드 영역"],
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
    command: "git commit -m \"InstanceCode 기능 추가\" \\\n  -m \"Customization-ID: BANK-OM-001\"\n\n./.venv/bin/python harness/run_source_candidate_gates.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\\n  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \\\n  --output harness/registrations/om-temp-1.13.0/source-gate-results.json",
    resultExample: "T30 | PASS\ncommit 7d19c895…에서 등록된 ID BANK-OM-007 하나를 확인",
    output: "통합 소스 검사 결과 source-gate-results.json의 T30 항목에 문제가 있는 commit과 ID가 남습니다. 변경 작성자와 변경관리 담당자가 commit 메시지를 수정할지 판단합니다.",
    code: ["harness/acgh/invariants.py", "harness/tests/test_invariants.py"]
  },
  t31: {
    group: "소스·등록 검사",
    title: "T31 · BANK-OM 적용 순서 확인",
    question: "같은 ID의 여러 commit과 기능 간 선행 관계가 Manifest에 등록한 순서를 지키는가?",
    status: "구현·단위 테스트 완료 · 현재 근거는 재검증을 마친 OM_TEMP 1.13.0 후보 3a2811cf… 결과 · 1.13.1 결과 파일은 Manifest v2 도입 이전 산출물이고 후보 branch가 원격에 없어 재검증 대기",
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
    command: "./.venv/bin/python harness/run_source_candidate_gates.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\\n  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \\\n  --output harness/registrations/om-temp-1.13.0/source-gate-results.json",
    resultExample: "T31 | PASS\nBANK-OM-007의 두 commit 순서와 series.allowed=true를 확인",
    output: "통합 소스 검사 결과 source-gate-results.json의 T31 항목에 적용 순서·revision 위반이 남습니다. 변경관리 담당자가 Manifest 또는 Patch-lock 순서를 확인합니다.",
    code: ["harness/acgh/invariants.py", "harness/tests/test_invariants.py"]
  },
  t40: {
    group: "소스·등록 검사",
    title: "T40 · 변경 파일 범위 확인",
    question: "각 BANK-OM commit이 Manifest에 등록한 파일만 변경했고, 최종 후보에 필수 변경이 반영됐는가?",
    status: "구현·단위 테스트 완료 · 현재 근거는 재검증을 마친 OM_TEMP 1.13.0 후보 3a2811cf… 결과 · 1.13.1 결과 파일은 Manifest v2 도입 이전 산출물이고 후보 branch가 원격에 없어 재검증 대기",
    statusLevel: "pass",
    timing: "Manifest 초안을 만든 뒤와 새로운 후속 commit이 추가될 때마다 실행합니다.",
    inputs: [
      ["Git diff", "BANK-OM commit별 실제 변경 파일과 최종 후보의 공식 원본 대비 차이", "BANK-OM-007 두 commit의 8개 + 2개 파일"],
      ["Manifest", "changed_paths, required_changed_paths", "changed_paths 10개 · required .../tiberoConnection.json"],
      ["Repository layout", "검사할 코드 영역", "openmetadata-spec/**, openmetadata-ui/**"]
    ],
    steps: [
      "commit별 실제 변경 파일과 Manifest의 현재 변경 범위를 비교합니다.",
      "Manifest에 없는 파일을 commit이 변경했는지 확인합니다.",
      "required_changed_paths가 현재 변경 범위에 포함되는지 확인합니다.",
      "최종 후보에서 필수 파일이 공식 새 버전과 실제로 다른지 확인합니다."
    ],
    verdicts: [
      ["PASS", "실제 변경 파일이 등록 범위와 같고 필수 변경이 최종 후보에 있습니다."],
      ["APPROVAL", "Manifest에는 등록했지만 실제 commit에서 변경하지 않은 비필수 파일이 있습니다."],
      ["BLOCK", "등록하지 않은 파일을 변경했거나 필수 변경이 최종 후보에 없습니다."],
      ["ANALYSIS ERROR", "경로 소유 영역을 판정할 수 없습니다."]
    ],
    limit: "파일 단위 검사입니다. 허용된 파일 안의 잘못된 코드 줄은 코드 리뷰와 test로 확인해야 합니다.",
    command: "./.venv/bin/python harness/run_source_candidate_gates.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\\n  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \\\n  --output harness/registrations/om-temp-1.13.0/source-gate-results.json",
    resultExample: "T40 | PASS\nBANK-OM-007 실제 변경 10개 = Manifest changed_paths 10개",
    output: "통합 소스 검사 결과 source-gate-results.json의 T40 항목에 등록 밖 변경과 누락된 필수 경로가 남습니다. 기능 담당자가 코드와 Manifest 중 잘못된 쪽을 고칩니다.",
    code: ["harness/acgh/drift.py", "harness/tests/test_drift.py"]
  },
  t41: {
    group: "소스·등록 검사",
    title: "T41 · 중요 시스템 경로 확인",
    question: "보안·인증·설정·DB처럼 별도 검토가 필요한 경로를 BANK-OM commit이 변경했는가?",
    status: "구현·단위 테스트 완료 · 현재 근거는 재검증을 마친 OM_TEMP 1.13.0 후보 3a2811cf… 결과 · 1.13.1 결과 파일은 Manifest v2 도입 이전 산출물이고 후보 branch가 원격에 없어 재검증 대기",
    statusLevel: "pass",
    timing: "소스 후보 검사에서 실제 변경 파일을 분류할 때 실행합니다.",
    inputs: [
      ["실제 변경 파일", "공식 기준 이후 BANK-OM commit의 경로", "bootstrap/sql/migrations/.../schemaChanges.sql"],
      ["Sensitive zones", "frozen, protected, watched 경로 규칙", "watched: bootstrap/sql/migrations/**"],
      ["Change intent", "허용된 중요 변경 사유와 승인 정보가 있는 경우", "BANK-OM-001 schema migration 승인 참조"]
    ],
    steps: [
      "변경 파일을 Sensitive zones 규칙과 비교합니다.",
      "frozen, protected, watched 중 어느 분류에 속하는지 확인합니다.",
      "필요한 change intent 또는 승인 정보가 있는지 확인합니다."
    ],
    verdicts: [
      ["PASS", "중요 경로 변경이 없거나 필요한 조건을 충족했습니다."],
      ["APPROVAL", "protected·watched 경로 변경으로 담당자 검토가 필요합니다."],
      ["BLOCK", "frozen 경로를 변경했거나 필수 승인 조건을 충족하지 못했습니다."],
      ["ANALYSIS ERROR", "경로를 규칙에 따라 분류할 수 없습니다."]
    ],
    limit: "경로 이름을 기준으로 판정하며 AST나 보안 취약점 분석을 수행하지 않습니다.",
    command: "./.venv/bin/python harness/run_source_candidate_gates.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\\n  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \\\n  --output harness/registrations/om-temp-1.13.0/source-gate-results.json",
    resultExample: "T41 | PASS (OM_TEMP 1.13.0 재검증 후보 3a2811cf… 결과)\nMySQL·PostgreSQL migration 2개는 watched 경로로 결과에 표시됐지만 현재 정책이 visibility_only라 자동 차단하지 않음\n주의: 정책을 approval_required로 바꾸면 같은 변경은 APPROVAL",
    output: "통합 소스 검사 결과 source-gate-results.json의 T41 항목에 민감 경로와 필요한 승인 수준이 남습니다. 보안·DB·플랫폼 담당자 중 해당 경로 책임자가 확인합니다.",
    code: ["harness/acgh/zones.py", "harness/tests/test_zones.py"]
  },
  t42: {
    group: "업그레이드 영향 검사",
    title: "T42 · 공식 변경 영향 확인",
    question: "새 공식 OpenMetadata 버전이 BANK-OM 기능과 관련된 파일을 변경했는가?",
    status: "구현·단위 테스트 완료 · OM_TEMP 1.13.1 영향 검사 결과가 있으나 후보 branch가 원격에 없어 재검증 대기",
    statusLevel: "approval",
    timing: "새 공식 버전을 patch branch에 준비한 뒤, 커스터마이징 병합 전에 실행합니다.",
    inputs: [
      ["공식 이전·새 버전 commit", "공식 A→B 사이의 Git 변경 파일", "f329dd4a…(1.13.0) → afcb2d2…(1.13.1)"],
      ["Manifest", "upgrade_watch.paths와 watch_dependencies", "BANK-OM-001 · .../Entity.java"],
      ["직접 참조 후보", "watch_suggest.py가 발견한 담당자 검토용 후보", ".../SearchIndexFactory.java · InstanceCode 참조"]
    ],
    steps: [
      "Git에서 공식 이전 버전과 새 버전 사이의 변경 파일 목록을 구합니다.",
      "각 Manifest의 upgrade_watch.paths와 공식 변경 파일을 비교합니다.",
      "겹친 경로가 있으면 BANK-OM ID와 검토할 경로를 결과에 기록합니다.",
      "직접 참조 후보는 자동 승인하지 않고 담당자에게 제시합니다."
    ],
    verdicts: [
      ["PASS", "등록된 관련 경로가 공식 버전에서 바뀌지 않았습니다."],
      ["APPROVAL", "관련 경로가 공식 버전에서도 변경돼 재적용 전 검토가 필요합니다."],
      ["ANALYSIS ERROR", "공식 commit 또는 경로 규칙을 읽지 못했습니다."]
    ],
    limit: "APPROVAL은 Git 충돌 확정이 아닙니다. 경로가 겹치지 않는 간접 런타임 의존도 자동으로 모두 찾지 못합니다.",
    command: "./.venv/bin/python harness/run_upgrade_watch.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --upstream-base <공식-이전-SHA> \\\n  --upstream-target <공식-새버전-SHA> \\\n  --output harness/registrations/om-temp-1.13.1/upgrade-watch-results.json",
    resultExample: "T42 | APPROVAL\nBANK-OM-001 watch 경로 .../Entity.java가 공식 1.13.1에서도 변경됨",
    output: "upgrade-watch-results.json의 T42 판정과 affected_customizations에 BANK-OM ID와 겹친 경로가 남습니다. 기능 담당자가 공식 diff와 커스터마이징 연결 부분을 확인합니다.",
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
      ["Manifest·Git diff", "활성 기능 수, 변경 줄 수, 한 파일을 함께 수정한 ID의 최대 수", "기준 후보 예시: Core 변경 11개 · 12,488줄 · 최대 공동 소유 4개"],
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
    command: "./.venv/bin/python harness/run_upgrade_risk_gates.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\\n  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \\\n  --debt-policy harness/policies/debt-thresholds.yaml \\\n  --change-intent harness/registrations/om-temp-1.13.1/change-intent.yaml \\\n  --upstream-base <공식-이전-SHA> \\\n  --upstream-target <공식-새버전-SHA> \\\n  --candidate <검사-대상-SHA> \\\n  --conflict-rate <실제-충돌률> \\\n  > /path/to/upgrade-risk-results.json",
    resultExample: "T43 | APPROVAL (판정 예시)\nchanged_lines=14,500이 soft 기준 14,000을 초과 · 구조 개선 검토",
    output: "업그레이드 위험 검사 JSON의 T43 항목과 debt_metrics에 계산값과 기준 초과 이유가 남습니다. 기술 책임자가 유지 부담을 수용할지 구조 개선할지 결정합니다.",
    code: ["harness/acgh/debt.py", "harness/tests/test_debt.py"]
  },
  t93_scope: {
    group: "소스·등록 검사",
    title: "T93-범위 · 실제 변경과 Manifest 일치 확인",
    question: "BANK-OM ID별 실제 변경 파일이 Manifest에 빠짐없이 정확하게 등록됐는가?",
    status: "구현·단위 테스트 완료 · 현재 근거는 재검증을 마친 OM_TEMP 1.13.0 후보 3a2811cf… 결과 · 1.13.1 결과 파일은 Manifest v2 도입 이전 산출물이고 후보 branch가 원격에 없어 재검증 대기",
    statusLevel: "pass",
    timing: "Manifest 생성·갱신 직후와 소스 후보 검사 때 실행합니다.",
    inputs: [
      ["Git commit 이력", "BANK-OM ID별 실제 변경 파일", "BANK-OM-007: 62e39da8… 8개 + 7d19c895… 2개"],
      ["Manifest", "changed_paths", "BANK-OM-007 changed_paths 10개"],
      ["공용 파일 소유정보", "여러 ID가 같은 경로를 수정한 경우의 소유 ID", ".../databaseService.json → BANK-OM-006·007"]
    ],
    steps: [
      "commit 메시지의 BANK-OM ID로 실제 변경 파일을 묶습니다.",
      "같은 ID의 모든 commit에서 나온 경로 합집합과 Manifest changed_paths를 비교합니다.",
      "실제 경로와 등록 경로가 양방향으로 같은지 확인합니다.",
      "여러 ID가 공유한 경로가 shared-path-owners.yaml에 모두 등록됐는지 확인합니다."
    ],
    verdicts: [
      ["PASS", "실제 변경 파일과 등록 범위가 일치합니다."],
      ["APPROVAL", "등록했지만 실제 변경에서 확인되지 않은 비필수 경로가 있습니다."],
      ["BLOCK", "실제 변경했지만 등록하지 않은 경로가 있습니다."],
      ["ANALYSIS ERROR", "경로 분류나 commit 분석을 완료할 수 없습니다."]
    ],
    limit: "경로가 같다는 사실만 확인하며, Manifest에 적은 업무 설명의 정확성은 사람이 검토합니다.",
    command: "./.venv/bin/python harness/registrations/om-temp-1.13.0/validate_registration_bundle.py \\\n  --repo /path/to/OM_TEMP \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\\n  --output harness/registrations/om-temp-1.13.0/registration-validation-results.json\n\n./.venv/bin/python harness/run_source_candidate_gates.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\\n  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \\\n  --output harness/registrations/om-temp-1.13.0/source-gate-results.json",
    resultExample: "T93-범위 | PASS\nBANK-OM-007 Git 변경 10개 = Manifest 등록 10개 · 공유 경로 소유 ID 일치",
    output: "등록 검증 결과 registration-validation-results.json과 통합 소스 검사 결과에 ID별 실제 경로·등록 경로 비교가 남습니다. Manifest 작성자와 리뷰어가 확인합니다.",
    code: ["harness/acgh/drift.py", "harness/registrations/om-temp-1.13.0/validate_registration_bundle.py"]
  },
  t93_policy: {
    group: "업그레이드 영향 검사",
    title: "T93-정책 · 검사 경로 최신성 확인",
    question: "공식 파일 이동이나 모듈 추가로 기존 경로 정책과 watch 규칙이 낡았는가?",
    status: "검사 구현 완료 · 현재 OM_TEMP source-gate-results.json에는 T93-정책 실행 결과 없음",
    statusLevel: "approval",
    timing: "공식 새 버전의 구조 변경을 분석할 때 실행합니다.",
    inputs: [
      ["공식 이전·새 버전", "파일 이동·삭제·추가 정보", "f329dd4a…(1.13.0) → afcb2d2…(1.13.1)"],
      ["Manifest·경로 정책", "watch, repository layout과 민감 경로 규칙", ".../Entity.java · upstream_owned_roots: openmetadata-service/**"]
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
    command: "./.venv/bin/python harness/run_upgrade_risk_gates.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\\n  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \\\n  --debt-policy harness/policies/debt-thresholds.yaml \\\n  --change-intent harness/registrations/om-temp-1.13.1/change-intent.yaml \\\n  --upstream-base <공식-이전-SHA> \\\n  --upstream-target <공식-새버전-SHA> \\\n  --candidate <검사-대상-SHA> \\\n  --conflict-rate <실제-충돌률> \\\n  > /path/to/upgrade-risk-results.json",
    resultExample: "T93-정책 | APPROVAL (판정 예시)\n등록된 watch 파일이 공식 새 버전에서 이동됨 · Manifest 경로 재검토",
    output: "업그레이드 위험 검사 JSON의 T93-정책 항목에 이동·삭제된 watch 경로와 오래된 경로 정책이 남습니다. 플랫폼 담당자와 Manifest 담당자가 갱신 여부를 확인합니다.",
    code: ["harness/acgh/policy_drift.py", "harness/tests/test_policy_drift.py"]
  },
  t60i: {
    group: "테스트·실행 검사",
    title: "T60-I · 필수 테스트 코드 존재 확인",
    question: "Contract에 등록한 필수 test의 파일과 Python 함수가 실제 검사 저장소에 존재하는가?",
    status: "Python pytest 확인 구현 완료 · 현재 근거는 재검증을 마친 OM_TEMP 1.13.0 후보 3a2811cf… 결과 · Java·TypeScript test 연결은 추가 개발 대상",
    statusLevel: "approval",
    timing: "Contract를 등록·갱신한 뒤와 Runtime test 실행 전에 실행합니다.",
    inputs: [
      ["Manifest", "assurance.contracts와 direct_tests", "BANK-OM-005 → CONTRACT-KOREAN-IME"],
      ["Contract catalog", "required_tests의 pytest 선택자", "tests/.../test_korean_ime.py::test_hangul_composition_roundtrip"],
      ["검사 저장소", "실제 Python test 파일과 함수", "easyseop/openmetadata-test의 test_korean_ime.py"]
    ],
    steps: [
      "Manifest가 참조하는 Contract ID를 찾습니다.",
      "Contract의 required_tests 선택자를 파일 경로와 함수 이름으로 분리합니다.",
      "Python AST로 파일을 읽어 지정한 test 함수가 실제 존재하는지 확인합니다.",
      "Manifest와 Contract의 양방향 BANK-OM 연결도 확인합니다."
    ],
    verdicts: [
      ["PASS", "등록한 Python test 파일과 함수가 모두 존재합니다."],
      ["BLOCK", "Contract, test 파일 또는 test 함수가 없습니다."],
      ["ANALYSIS ERROR", "Python 파일 문법을 읽을 수 없거나 입력 형식이 잘못됐습니다."]
    ],
    limit: "test가 존재한다는 사실만 확인합니다. 실행 성공은 T62가 확인하며 Java JUnit·TypeScript Jest는 현재 직접 확인하지 않습니다.",
    command: "./.venv/bin/python harness/registrations/om-temp-1.13.0/validate_registration_bundle.py \\\n  --repo /path/to/OM_TEMP \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\\n  --output harness/registrations/om-temp-1.13.0/registration-validation-results.json",
    resultExample: "T60-I | PASS\nCONTRACT-KOREAN-IME의 Python test 파일과 함수가 실제로 존재함",
    output: "등록 검증 결과 registration-validation-results.json의 “필수 테스트 코드 존재” 항목에 누락 여부가 남습니다. Contract 작성자와 테스트 담당자가 확인합니다.",
    code: ["harness/acgh/contracts.py", "harness/tests/test_contracts.py"]
  },
  t61: {
    group: "테스트·실행 검사",
    title: "T61 · 커스터마이징 제거 시 테스트 실패 확인",
    question: "BANK-OM 변경을 제거한 상태에서는 해당 기능의 필수 test가 실제로 실패하는가?",
    status: "검사 엔진 구현 완료 · OM_TEMP용 patch-kill-plan.yaml 작성과 환경 실행은 아직 필요",
    statusLevel: "approval",
    timing: "Contract test가 준비된 뒤, 테스트가 커스터마이징을 실제로 보호하는지 확인할 때 실행합니다.",
    inputs: [
      ["Patch-kill plan", "제거할 BANK-OM ID, 대상 파일·패치와 예상 실패 test", "BANK-OM-005 제거 → test_hangul_composition_roundtrip 실패 예상"],
      ["Candidate lock", "변경 제거 전 검사 대상 commit·배포 파일", "형식 예시: 후보 <실행 대상 SHA> · artifact <실제 digest>"],
      ["Test 결과", "변경 제거 전·후 test outcome", "정상 후보 pass · BANK-OM-005 제거 상태 fail"]
    ],
    steps: [
      "정상 후보에서 필수 test가 성공하는지 확인합니다.",
      "대상 BANK-OM 변경만 제거한 비교 상태를 만듭니다.",
      "등록한 필수 test를 다시 실행합니다.",
      "제거 상태에서 모든 목표 test가 실패하는지 확인합니다."
    ],
    verdicts: [
      ["PASS", "정상 후보에서는 성공하고 변경 제거 상태에서는 목표 test가 실패합니다."],
      ["BLOCK", "변경을 제거해도 test가 성공하거나 목표 test를 실행하지 못했습니다."],
      ["ANALYSIS ERROR", "제거 상태나 실행 결과가 지정 후보와 연결되지 않습니다."]
    ],
    limit: "실패했다는 사실만으로 실패 원인이 정확히 기능 제거 때문인지 단정하기 어렵습니다. 오류 종류·메시지를 함께 검토해야 합니다.",
    command: "# 먼저 om-temp-1.13.1/patch-kill-plan.yaml에 제거할 BANK-OM과\n# 실패해야 할 필수 test를 담당자가 등록해야 합니다. 현재 이 파일은 없습니다.\n./.venv/bin/python harness/run_source_patch_kills.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --output /path/to/evidence/source-patch-kill-result.yaml \\\n  --run-id source-patch-kill-001",
    resultExample: "T61 | PASS (실행 결과 형식 예시)\n정상 후보 PASS · BANK-OM-005 제거 상태에서 목표 test FAIL\n주의: 현재 OM_TEMP용 patch-kill 계획과 실행 증거는 아직 없음",
    output: "소스 제거 검사는 --output으로 지정한 source-patch-kill-result.yaml에, Runtime 제거 검사는 별도의 acgh-result.yaml에 정상·제거 상태의 test 결과를 남깁니다. 기능 담당자가 실패 원인이 의도한 기능 제거인지 확인합니다.",
    code: ["harness/acgh/patchkill.py", "harness/tests/test_patchkill.py"]
  },
  t62: {
    group: "테스트·실행 검사",
    title: "T62 · 테스트 결과와 후보 연결 확인",
    question: "필수 test가 정확히 검사 대상으로 고정한 commit과 배포 파일에서 실행됐는가?",
    status: "실행기·단위 테스트 완료 · 실제 행내 환경 실행 대기",
    statusLevel: "approval",
    timing: "테스트 환경에 검사 대상 코드를 배포하고 Contract test를 실행할 때마다 수행합니다.",
    inputs: [
      ["Candidate lock", "검사 대상 commit과 artifact digest", "형식 예시: <실행 대상 SHA> · <실제 artifact digest>"],
      ["Test run set", "test ID, 시도 번호, outcome, 검사기·suite 버전", "test_tibero.py::test_connection_schema_roundtrip · attempt 1 · pass"],
      ["Manifest·Contract·Registry", "필수 test와 기능 중요도", "BANK-OM-007 · CONTRACT-TIBERO-CONNECTOR · high"]
    ],
    steps: [
      "Test run set의 commit·artifact가 Candidate lock과 같은지 확인합니다.",
      "검사기 버전과 test suite 버전이 예상값과 같은지 확인합니다.",
      "모든 active BANK-OM의 필수 test가 실행 목록에 있는지 확인합니다.",
      "SKIP·FAIL·ERROR와 재시도 이력을 숨기지 않고 판정합니다."
    ],
    verdicts: [
      ["PASS", "필수 test가 같은 후보에서 누락 없이 성공했습니다."],
      ["APPROVAL", "high·critical 기능이 실패 후 재시도에서 성공해 불안정성 검토가 필요합니다."],
      ["BLOCK", "필수 test 누락·SKIP·FAIL·ERROR가 있습니다."],
      ["ANALYSIS ERROR", "후보·artifact·검사기·suite 버전이 맞지 않습니다."]
    ],
    limit: "등록된 test만 확인합니다. Contract가 다루지 않은 업무 동작까지 자동으로 보장하지 않습니다.",
    command: "./.venv/bin/python harness/run_runtime_contracts.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --artifact-digest sha256:<배포파일해시> \\\n  --output-dir /path/to/evidence \\\n  --run-id runtime-contract-001",
    resultExample: "T62 | PASS (형식 예시)\n<실행 대상 SHA>와 <실제 artifact digest>에서 BANK-OM-007 필수 test 성공\n주의: 현재 OM_TEMP 행내 Runtime 실행 결과는 아직 없음",
    output: "실행별 evidence 폴더에 test-run-set.yaml과 acgh-result.yaml이 새로 생성됩니다. 기능 담당자와 배포 검토자가 후보·artifact 일치와 test 결과를 확인합니다.",
    code: ["harness/acgh/testruns.py", "harness/acgh/pytest_runs.py", "harness/tests/test_testruns.py"]
  },
  t63: {
    group: "테스트·실행 검사",
    title: "T63 · TypeScript 오류 증가 확인",
    question: "공식 원본과 비교해 행내 후보에 새 TypeScript 오류가 추가됐는가?",
    status: "비교 도구 구현 완료 · 전체 환경 로그 결속 보완 대상",
    statusLevel: "approval",
    timing: "공식 원본과 행내 후보에서 같은 TypeScript 검사를 각각 실행한 뒤 사용합니다.",
    inputs: [
      ["공식 원본 typecheck 로그", "파일 경로·오류 코드별 발생 정보와 종료 코드", "upstream.log · TS2322 3건 · exit 2"],
      ["행내 후보 typecheck 로그", "같은 명령으로 실행한 결과와 종료 코드", "candidate.log · TS2322 3건 · exit 2"]
    ],
    steps: [
      "두 로그에서 파일 경로와 TypeScript 오류 코드를 정규화합니다.",
      "같은 경로·오류 코드의 발생 횟수를 비교합니다.",
      "행내 후보에서 새로 생기거나 증가한 오류를 찾습니다."
    ],
    verdicts: [
      ["PASS", "행내 후보에 공식 원본보다 새 TypeScript 오류가 없습니다."],
      ["BLOCK", "새 오류 또는 오류 횟수 증가가 있습니다."],
      ["ANALYSIS ERROR", "로그 형식이나 실행 정보가 비교 가능하지 않습니다."]
    ],
    limit: "TypeScript만 비교하며 Node·Yarn 버전과 전체 로그 digest를 T63 결과에 강제 연결하는 기능은 보완 대상입니다.",
    command: "./.venv/bin/python harness/compare_ui_typecheck.py \\\n  --harness harness \\\n  --upstream-log /path/to/upstream.log \\\n  --candidate-log /path/to/candidate.log \\\n  --upstream-exit <공식-typecheck-종료코드> \\\n  --candidate-exit <행내-typecheck-종료코드> \\\n  > /path/to/typecheck-comparison.json",
    resultExample: "T63 | PASS (비교 예시)\n공식 3건 · 행내 후보 3건 · 새 TypeScript 오류 0건",
    output: "TypeScript 비교 명령의 JSON 표준 출력에 공식·행내 오류 수와 새 오류 목록이 남습니다. 프론트엔드 담당자가 로그의 실행 환경과 새 오류를 확인합니다.",
    code: ["harness/compare_ui_typecheck.py", "harness/tests/test_tsc_baseline.py"]
  },
  t90: {
    group: "업그레이드·배포 검사",
    title: "T90 · 업그레이드 전 과정 결과 확인",
    question: "복원·migration·색인·수집·권한·API·검색·rollback 등 필수 업그레이드 단계를 모두 실행해 통과했는가?",
    status: "판정 모듈·스키마 구현 완료 · 실제 행내 업그레이드 실행 증거 대기",
    statusLevel: "approval",
    timing: "실제와 유사한 테스트 환경에서 후보 업그레이드 연습을 수행한 뒤 실행합니다.",
    inputs: [
      ["Upgrade test run", "이전·새 버전, 후보, 12개 필수 단계 outcome", "가상 형식 예시: 1.13.0 → 1.13.1 · migration/search/rollback 등 12개가 모두 pass인 경우"],
      ["Candidate lock", "검사 대상 commit·artifact", "형식 예시: <실행 대상 SHA> · <실제 artifact digest>"],
      ["Test run set", "같은 후보의 Contract test 결과 digest", "환경 실행 예시: sha256:04bd…"]
    ],
    steps: [
      "업그레이드 결과의 검사 대상 commit·artifact가 Candidate lock과 같은지 확인합니다.",
      "연결된 Test run set digest가 실제 실행 결과와 같은지 확인합니다.",
      "정해진 12개 단계가 모두 존재하고 outcome이 pass인지 확인합니다."
    ],
    verdicts: [
      ["PASS", "같은 후보에서 12개 필수 업그레이드 단계가 모두 성공했습니다."],
      ["BLOCK", "필수 단계가 없거나 pass가 아닙니다."],
      ["ANALYSIS ERROR", "후보·artifact·Test run set 연결이 맞지 않거나 결과 형식이 잘못됐습니다."]
    ],
    limit: "결과 문서가 올바른 형식이고 같은 검사 대상을 가리키는지를 확인합니다. 각 단계를 실제로 수행했다는 외부 실행 로그·서명 검증은 추가 결속이 필요합니다.",
    command: "현재는 실행 시스템이 만든 upgrade-test-run.yaml을\nharness/acgh/upgrade_run.py의 check_upgrade_run()에 전달합니다.",
    resultExample: "T90 | PASS (형식 예시)\n<실행 대상 SHA>에서 필수 업그레이드 단계 12/12 PASS\n주의: 현재 OM_TEMP 행내 업그레이드 실행 결과는 아직 없음",
    output: "실행 시스템이 upgrade-test-run.yaml과 해당 판정을 포함한 acgh-result.yaml을 보관합니다. 업그레이드 책임자가 12개 단계와 연결된 후보·artifact를 확인합니다.",
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
      ["Release lock", "후보·정책·검사기·suite·결과·이미지·Helm digest", "형식 예시: candidate <검증 SHA> · image <검증 digest>"],
      ["Candidate lock·Test run set·검사 결과", "검증한 대상의 고정값", "형식 예시: 세 파일 모두 같은 <검증 SHA>"],
      ["실제 배포 관측값", "배포할 commit, 이미지와 Helm digest, 재빌드 여부", "형식 예시: <검증 SHA> · <검증 digest> · rebuilt=false"]
    ],
    steps: [
      "Release lock과 Candidate lock·검사 결과·Test run set의 digest 연결을 확인합니다.",
      "검증한 이미지·Helm digest와 실제 배포 관측값을 비교합니다.",
      "검증 후 재빌드한 artifact인지 확인합니다."
    ],
    verdicts: [
      ["PASS", "검증한 동일 artifact를 재빌드 없이 배포합니다."],
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
    owner: "Git 변경 경로 초안은 생성기가 만들고, 기능 담당자가 required·간접 watch·Contract를 결정합니다.",
    readers: "변경 생존 확인, 적용 순서 확인, 등록 범위 확인, 공식 업그레이드 영향 확인, 필수 test 연결·실행 확인에 사용됩니다.",
    fields: [
      ["customization_id", "필수·문자열", "코드 commit과 관리자료를 연결하는 BANK-OM ID", "관리자 발급", "BANK-OM-007"],
      ["title", "필수·문자열", "사람이 읽는 기능명", "기능 담당자", "Tibero 연결 유형"],
      ["status", "필수", "현재 검사할 기능은 active, 폐기 절차를 마친 기능은 retired", "관리 담당자", "active"],
      ["kind", "필수", "공식 Core 수정 여부와 변경 유형", "설계 검토자", "core-patch"],
      ["implementation.changed_paths", "필수·목록", "현재 버전에서 이 ID가 붙은 모든 commit이 변경한 전체 파일. 목록 밖 파일을 같은 ID로 변경하면 등록 범위 검사가 BLOCK", "Git 자동 추출 후 확인", ".../tiberoConnection.json"],
      ["implementation.required_changed_paths", "필수·목록", "현재 변경 범위 중 누락되면 기능 미적용으로 즉시 BLOCK할 핵심 파일", "기능 담당자", ".../tiberoConnection.json"],
      ["upgrade_watch.paths", "필수·목록", "공식 버전 변경 시 다시 비교할 관련 경로", "공식 patch에 있는 실제 변경 경로만 자동 포함 + 담당자 의존 추가", ".../databaseService.json"],
      ["assurance.contracts", "필수·목록", "업무 정상 조건과 필수 test를 연결하는 Contract ID", "기능 담당자", "CONTRACT-TIBERO-CONNECTOR"],
      ["assurance.direct_tests", "목록", "Contract에서 파생되지 않은 별도 기술 test", "개발자", "tests/.../test_tibero.py::test_schema"],
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
        command: "PYTHONPATH=harness python harness/prepare_registration.py plan \\\n  --repo /path/to/OM_TEMP \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --patch-ref origin/patch/om-1.13.0 \\\n  --custom-ref origin/custom/om-1.13.0 \\\n  --product-version 1.13.0 \\\n  --output harness/preparation-plans/om-temp-1.13.0-YYYYMMDD"
      },
      {
        label: "등록자료 검증 · Manifest는 바뀌지 않음",
        meaning: "수정한 Manifest가 Registry·Contract·전체 변경 파일 목록·공용 파일 소유정보·필수 test 연결과 맞는지 읽어서 검사합니다. Manifest를 직접 수정한 뒤에는 이 검증을 실행합니다.",
        command: "python harness/registrations/om-temp-1.13.0/validate_registration_bundle.py \\\n  --repo /path/to/OM_TEMP"
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
    owner: "목록·연결 초안은 생성기가 만들고 담당자·중요도·상태는 관리 책임자가 승인합니다.",
    readers: "활성 기능 목록 확인, 담당자 배정 확인, 적용 순서 확인, 필수 test 연결 확인과 등록자료 완전성 검사에 사용됩니다.",
    fields: [
      ["source.repository", "필수", "분석한 OpenMetadata 코드 저장소", "자동/관리자 확인", "easyseop/OM_TEMP"],
      ["source.snapshot_sha", "필수", "최초 등록자료가 설명하는 행내 코드 상태", "Git 자동 확인", "62e39da8…"],
      ["source.upstream_sha", "필수", "비교 기준 공식 OpenMetadata 상태", "공식 tag에서 확인", "f329dd4a…"],
      ["entries[].customization_id", "필수", "Manifest와 같은 BANK-OM ID", "Manifest에서 생성", "BANK-OM-007"],
      ["entries[].owner", "필수", "기능과 결과를 책임지는 조직·담당자", "관리 책임자", "데이터플랫폼팀"],
      ["entries[].owner_status", "필수", "담당 확정은 assigned, 미정은 pending", "관리 책임자", "assigned"],
      ["entries[].status", "필수", "검사 대상은 active, 폐기 완료는 retired", "관리 책임자", "active"],
      ["entries[].criticality", "필수", "low·medium·high·critical 중 업무 영향 등급", "업무 영향 평가", "high"],
      ["entries[].manifest", "필수", "해당 Manifest 경로", "생성기", "manifests/BANK-OM-007.yaml"],
      ["entries[].contracts", "목록", "연결된 Contract ID", "Manifest·Contract에서 생성", "[CONTRACT-TIBERO-CONNECTOR]"],
      ["entries[].provenance", "필수", "최초 snapshot에 있던 기능인지 이후 추가 기능인지 구분", "Git 분석 후 확인", "source-snapshot"]
    ],
    before: "- customization_id: BANK-OM-001\n  owner: UNASSIGNED\n  owner_status: pending\n  criticality: high",
    after: "- customization_id: BANK-OM-001\n  owner: 데이터플랫폼팀\n  owner_status: assigned\n  criticality: high",
    updateReason: "실제 책임 조직이 정해졌으므로 owner와 owner_status만 승인해 변경합니다. commit SHA나 Manifest 경로는 관련 코드·파일이 바뀌지 않았다면 수정하지 않습니다.",
    commands: [
      "python harness/registrations/om-temp-1.13.0/generate_registration_bundle.py --repo /path/to/OM_TEMP",
      "python harness/registrations/om-temp-1.13.0/validate_registration_bundle.py --repo /path/to/OM_TEMP"
    ],
    storage: "버전별 등록 폴더에서 Git으로 관리합니다. 생성기를 다시 실행하기 전에 사람 입력인 owner·criticality가 덮어써지지 않는지 diff를 검토합니다."
  },
  contracts: {
    title: "Contract catalog",
    path: "harness/registrations/<버전>/contracts.yaml",
    purpose: "파일 존재만으로 확인할 수 없는 업무 정상 조건과 그 조건을 확인할 필수 test를 연결합니다.",
    created: "BANK-OM 기능을 최초 등록할 때 기능 책임자가 정상 조건을 정하고 만듭니다.",
    update: "업무 정상 조건, test 파일·함수 이름, 보호할 BANK-OM ID가 바뀔 때 갱신합니다. test 실행마다 수정하지 않습니다.",
    owner: "업무 정상 조건은 기능 책임자가 정하고, test 선택자는 개발자와 test 담당자가 확인합니다.",
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
      "python harness/registrations/om-temp-1.13.0/validate_registration_bundle.py --repo /path/to/OM_TEMP",
      "pytest -q harness/tests/test_contracts.py"
    ],
    storage: "버전별 등록 폴더에서 Git으로 관리합니다. 과거 실행 결과의 Contract를 바꾸지 않고, 변경 commit 이후 새 suite_version으로 다시 test합니다."
  },
  shared_paths: {
    title: "공용 파일 소유정보",
    path: "harness/registrations/<버전>/shared-path-owners.yaml",
    purpose: "여러 BANK-OM ID가 같은 파일을 수정했을 때 해당 경로를 어느 기능들이 함께 소유하는지 기록합니다.",
    created: "등록 묶음 생성 시 Manifest의 전체 경로를 비교해 생성합니다.",
    update: "기준으로 삼은 과거 코드 commit이나 과거 commit 분류를 바로잡을 때만 다시 만듭니다. 일반 후속 commit이나 현재 Manifest 변경 때문에 갱신하지 않습니다.",
    owner: "생성기가 계산하고 담당자가 실제 기능 관계를 검토합니다.",
    readers: "현재 버전에서 한 파일을 여러 기능이 함께 변경했는지 확인하는 등록 범위·소유관계 검사에 사용됩니다.",
    fields: [
      ["paths[].path", "필수", "두 개 이상 BANK-OM이 공유하는 정확한 파일 경로", "생성기", ".../Entity.java"],
      ["paths[].owners", "필수·목록", "현재 버전에서 그 경로를 변경한 BANK-OM ID 전체", "생성기·담당자 확인", "[BANK-OM-001, BANK-OM-002]"]
    ],
    before: "paths:\n  - path: openmetadata-service/.../Entity.java\n    owners: [BANK-OM-001]",
    after: "paths:\n  - path: openmetadata-service/.../Entity.java\n    owners: [BANK-OM-001, BANK-OM-002]",
    updateReason: "BANK-OM-002도 Entity.java를 실제로 변경했다면 owners에 추가합니다. 실제 변경 이력이 없는데 임의로 소유자를 추가하지 않습니다.",
    commands: [
      "python harness/registrations/om-temp-1.13.0/generate_registration_bundle.py --repo /path/to/OM_TEMP",
      "python harness/registrations/om-temp-1.13.0/validate_registration_bundle.py --repo /path/to/OM_TEMP"
    ],
    storage: "버전별 최초 과거 코드 복사본에서 만든 파생 파일입니다. generate_registration_bundle.py는 과거 기준 commit과 사람 정책값까지 다시 쓰므로 일반 후속 commit 처리에는 실행하지 않습니다. 담당자·Contract 같은 승인된 값이 초기화될 수 있습니다."
  },
  source_snapshot_owners: {
    title: "과거 코드 경로 소유정보",
    path: "harness/registrations/<버전>/source-snapshot-path-owners.yaml",
    purpose: "최초 등록에 사용한 과거 행내 코드 시점에서 각 변경 파일이 어느 BANK-OM 기능에 속했는지 기록합니다. 현재 Manifest의 검사 범위를 나누는 파일이 아니라, 과거 코드를 공식 코드 위에 기능별로 다시 구성하는 검사에서만 사용합니다.",
    created: "한 버전의 등록 묶음을 처음 만들 때, 기준이 되는 과거 행내 code snapshot의 commit 이력을 읽어 자동 생성합니다.",
    update: "기준으로 삼는 과거 snapshot SHA가 바뀔 때만 다시 생성합니다. 같은 ID의 후속 commit이 생겼다는 이유만으로 과거 snapshot 기록을 고치지 않습니다.",
    owner: "Git 이력과 생성기가 자동으로 만듭니다. 담당자는 잘못 분류된 commit ID가 없는지 검토하며 파일을 임의로 편집하지 않습니다.",
    readers: "과거 행내 코드 재구성 검사(T25-R)가 어떤 파일을 어느 BANK-OM 단계에서 복원할지 결정할 때 사용합니다. 현재 버전의 등록 범위 검사(T40·T93)는 이 파일이 아니라 Manifest의 changed_paths를 사용합니다.",
    fields: [
      ["<파일 경로>", "필수·문자열 key", "과거 snapshot에서 공식 원본과 달랐던 정확한 파일", "Git 자동 추출", "openmetadata-ui/.../serviceConnection.ts"],
      ["<BANK-OM ID 목록>", "필수·목록", "그 과거 snapshot 시점까지 해당 파일을 변경한 기능 ID", "commit 메시지에서 자동 추출", "[BANK-OM-006]"]
    ],
    before: "openmetadata-ui/.../serviceConnection.ts:\n- BANK-OM-006",
    after: "openmetadata-ui/.../serviceConnection.ts:\n- BANK-OM-006",
    updateReason: "BANK-OM-007의 후속 commit이 나중에 같은 파일을 수정해도, 최초 source snapshot에는 그 후속 commit이 없었습니다. 따라서 과거 snapshot 소유정보는 BANK-OM-006으로 유지하고, 현재 버전 Manifest의 changed_paths와 shared-path-owners.yaml에는 BANK-OM-007까지 반영합니다.",
    scopeFlow: [
      ["과거 snapshot 시점", "serviceConnection.ts = 006", ""],
      ["007 후속 commit", "같은 파일 추가 변경", "→"],
      ["현재 버전 범위", "006 + 007 공동 변경", "→"]
    ],
    scopeOutcome: "T25-R은 과거 snapshot을 재구성할 때 serviceConnection.ts를 BANK-OM-006 단계에서 복원합니다. 현재 범위 검사에서는 BANK-OM-006과 BANK-OM-007이 모두 그 파일을 변경한 것으로 확인합니다. 두 파일은 서로 다른 시점을 설명하므로 결과가 달라도 오류가 아닙니다.",
    scopeExamples: [
      ["source-snapshot-path-owners.yaml", "BANK-OM-006", "과거 snapshot 재구성에만 사용"],
      ["BANK-OM-007 Manifest changed_paths", "serviceConnection.ts 포함", "현재 버전 범위 검사에 사용"],
      ["shared-path-owners.yaml", "BANK-OM-006·007", "현재 버전 공동 소유관계 검사에 사용"]
    ],
    commands: [
      {
        label: "등록 묶음 재생성 · 이 파일이 바뀜",
        meaning: "지정한 source snapshot까지의 commit을 읽어 파일별 BANK-OM 소유정보를 다시 만듭니다. source snapshot SHA를 바꾸지 않았다면 생성 결과도 같아야 합니다.",
        command: "python harness/registrations/om-temp-1.13.0/generate_registration_bundle.py \\\n  --repo /path/to/OM_TEMP"
      },
      {
        label: "등록자료 검증 · 이 파일은 바뀌지 않음",
        meaning: "과거 snapshot 소유정보의 경로와 ID가 실제 snapshot·Manifest와 모순되지 않는지 확인합니다.",
        command: "python harness/registrations/om-temp-1.13.0/validate_registration_bundle.py \\\n  --repo /path/to/OM_TEMP"
      }
    ],
    storage: "버전별 등록 폴더의 자동 생성 파일로 Git에 보관합니다. 현재 기능 범위를 설명하려고 수동으로 최신화하지 않습니다. 현재 범위는 Manifest changed_paths와 commit-inventory.yaml에서 확인합니다. generate_registration_bundle.py는 과거 기준 commit과 사람 정책값까지 다시 쓰므로 일반 후속 commit 처리에는 실행하지 않습니다. 담당자·Contract 같은 승인된 값이 초기화될 수 있습니다."
  },
  diff_inventory: {
    title: "전체 변경 파일 목록",
    path: "harness/registrations/<버전>/source-diff-paths.txt",
    purpose: "공식 원본과 행내 코드 사이에서 실제로 달라진 모든 파일 경로를 한 줄에 하나씩 기록합니다.",
    created: "등록 묶음을 처음 만들 때 Git diff로 생성합니다.",
    update: "기준으로 삼는 과거 코드 commit 또는 공식 기준 commit이 바뀔 때만 다시 생성합니다. 같은 ID의 후속 commit이 생겼다는 이유만으로는 다시 만들지 않습니다. 현재 버전의 변경 범위는 Manifest changed_paths와 commit-inventory.yaml이 기록합니다.",
    owner: "과거 기준을 바꾸는 별도 승인 작업에서 생성기가 만듭니다. 사람이 파일 목록을 직접 보정하지 않습니다.",
    readers: "등록자료가 실제 Git diff를 빠짐없이 설명하는지 확인하는 전체 변경 범위 검사에 사용됩니다.",
    fields: [
      ["한 줄의 경로", "필수", "저장소 root 기준 실제 변경 파일", "Git diff 자동 생성", "openmetadata-service/.../Entity.java"]
    ],
    before: "openmetadata-service/.../Entity.java\nopenmetadata-spec/.../instanceCode.json",
    after: "openmetadata-service/.../Entity.java\nopenmetadata-spec/.../instanceCode.json\nopenmetadata-ui/.../instanceCodeAPI.ts",
    updateReason: "공식 기준 commit을 새 버전으로 바꾸는 별도 승인 작업에서 전체 목록을 Git에서 다시 생성합니다. 텍스트 파일만 수정하면 실제 코드와 달라져 검사에 실패합니다. 일반 후속 commit으로 늘어난 변경 파일은 이 목록이 아니라 commit-inventory.yaml과 current-diff-paths.txt에 기록됩니다.",
    commands: [
      "python harness/registrations/om-temp-1.13.0/generate_registration_bundle.py --repo /path/to/product-code-repo"
    ],
    storage: "후보·공식 기준별 파생 파일입니다. 생성 기준 SHA와 함께 Git에 보관해 재현합니다. generate_registration_bundle.py는 과거 기준 commit과 사람 정책값까지 다시 쓰므로 일반 후속 commit 처리에는 실행하지 않습니다. 담당자·Contract 같은 승인된 값이 초기화될 수 있습니다."
  },
  layout: {
    title: "Repository layout",
    path: "harness/registrations/<버전>/repository-layout.yaml",
    purpose: "파일 경로가 공식 OpenMetadata 코드, 행내 거버넌스 코드, 플랫폼 확장 또는 알 수 없는 영역 중 어디에 속하는지 정합니다.",
    created: "저장소를 검사 체계에 처음 등록할 때 만듭니다.",
    update: "공식 버전에서 최상위 모듈이 추가·이동되거나 행내 확장 root가 바뀔 때 갱신합니다.",
    owner: "저장소 구조를 아는 플랫폼 담당자가 승인합니다.",
    readers: "commit·경로 정책 확인, 등록 범위 확인, 민감 경로 확인 등 파일 위치를 해석하는 모든 소스 검사에 사용됩니다.",
    fields: [
      ["upstream_base_sha", "필수", "이 경로 정책을 작성한 공식 기준 commit", "공식 tag에서 확인", "f329dd4a…"],
      ["path_grammar", "필수", "대소문자·Unicode·symlink 등 경로 해석 규칙", "플랫폼 담당자", "case_sensitive: true"],
      ["upstream_owned_roots", "필수·목록", "공식 OpenMetadata 코드 영역", "저장소 구조 분석", "openmetadata-service/**"],
      ["bank_governance_roots", "필수·목록", "검사 정책·test·문서 영역", "검사 저장소 담당자", "harness/**"],
      ["platform_extension_roots", "목록", "공식 코드와 분리한 행내 확장 영역", "플랫폼 담당자", "bank-extensions/**"],
      ["unknown_path_policy", "필수", "분류하지 못한 경로의 처리", "정책 담당자", "analysis_error"]
    ],
    before: "upstream_owned_roots:\n  - openmetadata-service/**\n  - openmetadata-ui/**",
    after: "upstream_owned_roots:\n  - openmetadata-service/**\n  - openmetadata-ui/**\n  - openmetadata-mcp/**",
    updateReason: "새 공식 버전에서 openmetadata-mcp 모듈이 검사 대상 공식 코드로 추가됐음을 확인했을 때 root를 추가합니다. 단순히 오류를 없애려고 unknown 경로를 넓게 허용하지 않습니다.",
    commands: [
      "pytest -q harness/tests/test_layout.py",
      "python harness/registrations/om-temp-1.13.0/validate_registration_bundle.py --repo /path/to/OM_TEMP"
    ],
    storage: "공식 기준 버전별 정책입니다. upstream_base_sha가 달라지면 기존 정책을 그대로 복사하지 말고 경로 구조를 재검토합니다."
  },
  zones: {
    title: "Sensitive zones",
    path: "harness/registrations/<버전>/sensitive-zones.yaml",
    purpose: "보안·인증·설정·DB처럼 변경 시 차단 또는 별도 승인이 필요한 경로를 분류합니다.",
    created: "저장소의 위험 경로 정책을 최초 정의할 때 만듭니다.",
    update: "새 보안·인증 모듈, migration 경로 또는 조직 통제 정책이 바뀔 때 갱신합니다.",
    owner: "보안·플랫폼·DB 담당자가 함께 승인합니다.",
    readers: "민감 경로 변경 검사와 업그레이드 위험 검사에서 변경 경로의 승인 수준을 정할 때 사용됩니다.",
    fields: [
      ["frozen", "목록", "일반 BANK-OM 변경을 허용하지 않는 경로", "정책 담당자", ".github/workflows/release/**"],
      ["protected", "목록", "별도 승인 없이는 진행할 수 없는 경로", "보안·플랫폼 담당자", "openmetadata-service/**/security/**"],
      ["watched", "목록", "변경 사실을 반드시 결과에 표시할 경로", "업무·DB 담당자", "bootstrap/sql/migrations/**"]
    ],
    before: "protected:\n  - openmetadata-service/src/main/java/**/security/**",
    after: "protected:\n  - openmetadata-service/src/main/java/**/security/**\n  - openmetadata-service/src/main/java/**/auth/**",
    updateReason: "새 공식 버전의 인증 코드가 auth 경로로 분리됐고 같은 승인 통제가 필요하다고 보안 담당자가 판단했을 때 추가합니다.",
    commands: [
      "pytest -q harness/tests/test_zones.py",
      "./.venv/bin/python harness/run_upgrade_risk_gates.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\\n  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \\\n  --debt-policy harness/policies/debt-thresholds.yaml \\\n  --change-intent harness/registrations/om-temp-1.13.1/change-intent.yaml \\\n  --upstream-base <공식-1.13.0-SHA> \\\n  --upstream-target <공식-1.13.1-SHA> \\\n  --candidate <행내-후보-SHA> \\\n  --conflict-rate 0.0 > harness/registrations/om-temp-1.13.1/upgrade-risk-results.json"
    ],
    storage: "정책 파일이므로 변경 사유와 승인자를 Git 리뷰에 남깁니다. 과거 검사 결과에 사용한 정책은 수정하지 않습니다."
  },
  candidate_lock: {
    title: "Candidate lock",
    path: "검사 실행별 evidence/candidate-lock.yaml",
    purpose: "검사할 행내 commit과 전체 파일 상태를 고정하고, Runtime·배포 검사 단계에서는 그 코드로 만든 실제 이미지·패키지까지 같은 대상으로 묶습니다.",
    created: "소스 검사 후보가 확정되면 commit·tree와 소스 내용 확인값으로 생성합니다. 실제 이미지·패키지를 만든 뒤에는 그 artifact digest를 포함한 Runtime·배포용 새 lock을 생성합니다.",
    update: "기존 파일을 갱신하지 않습니다. commit·tree·소스 내용·실제 artifact·공식 목표·통합 방식 중 하나라도 바뀌면 새 후보와 새 lock을 만듭니다.",
    owner: "CI·Runtime 실행기가 자동 생성하고 배포 담당자가 검사 대상이 맞는지 승인합니다.",
    readers: "검사 대상 고정, 변경 생존 확인, Runtime test 실행, 증거 연결과 실제 배포 일치 검사에 사용됩니다.",
    fields: [
      ["integration_strategy", "필수", "공식 코드와 행내 변경을 합친 방식", "운영 절차 선택", "vendor-merge"],
      ["upstream.repository", "필수", "공식 저장소", "자동/관리자 확인", "open-metadata/OpenMetadata"],
      ["upstream.base_sha", "필수", "업그레이드 전 공식 commit", "공식 tag", "f329dd4a… (1.13.0)"],
      ["upstream.target_sha", "필수", "업그레이드할 공식 commit", "공식 tag", "afcb2d2… (1.13.1)"],
      ["candidate.repository", "필수", "검사 대상 행내 저장소", "자동", "easyseop/OM_TEMP"],
      ["candidate.commit_sha", "필수", "모든 BANK-OM 변경을 포함한 최종 검사 대상 commit 하나", "Git 자동", "1.13.0 재검증 예: 3a2811cf… · 1.13.1 과거 진단 예: dee330ebd5…"],
      ["candidate.tree_sha", "필수", "그 commit에서 보이는 전체 파일 내용의 식별값", "Git 자동", "9495a31c…"],
      ["candidate.artifact_digest", "필수", "소스 검사에서는 source tree 내용을 묶는 SHA-256, Runtime·배포 검사에서는 실제 이미지·패키지 SHA-256", "소스 검사기 또는 빌드 자동", "현재 소스 결과: source tree digest · 환경 실행 예시: image sha256:61a3…"],
      ["patch_source_lock_digest", "조건부", "patch-replay에서 사용한 Patch-lock 파일의 SHA-256", "자동", "patch-replay 예시: sha256:8ce1…"]
    ],
    before: "candidate:\n  commit_sha: aaa111...\n  artifact_digest: sha256:old...",
    after: "candidate:\n  commit_sha: bbb222...\n  artifact_digest: sha256:new...",
    updateReason: "코드나 빌드 파일이 바뀌면 기존 lock을 수정하지 않고 bbb222 후보용 새 evidence 폴더와 새 Candidate lock을 생성합니다. 이전 결과는 aaa111 후보의 기록으로 보존합니다.",
    commands: [
      "./.venv/bin/python harness/run_runtime_contracts.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --artifact-digest sha256:<배포파일해시> \\\n  --output-dir /path/to/new-evidence \\\n  --run-id runtime-contract-001"
    ],
    storage: "검사 대상별 불변 실행 증거입니다. 실행 번호·검사 대상 Git commit SHA별 디렉터리 또는 CI artifact로 분리하고 덮어쓰지 않습니다. 현재 OM_TEMP 1.13.1 결과의 candidate는 dee330ebd5…이지만 실제 생성 방식은 커밋별 재적용입니다. 저장된 integration_strategy: vendor-merge 값과 실제 과정이 다르므로 이 lock은 vendor-merge 완료 증거로 사용하지 않습니다."
  },
  test_run_set: {
    title: "Test run set",
    path: "검사 실행별 evidence/test-run-set.yaml",
    purpose: "어떤 필수 test를 몇 번째 시도에서 실행했고 결과가 무엇인지, 정확한 후보·검사기·suite 버전과 함께 기록합니다.",
    created: "Runtime Contract test를 실행할 때마다 자동 생성합니다.",
    update: "기존 파일을 수정하지 않습니다. 재실행·재시도·후보 변경마다 새 실행 결과를 만듭니다.",
    owner: "Runtime test 실행기가 자동 생성합니다.",
    readers: "Runtime test 재시도 판정, 실행 증거 연결과 실제 배포 일치 검사에 사용됩니다.",
    fields: [
      ["candidate.commit_sha", "필수", "test를 실행한 최종 후보 commit 하나", "Candidate lock에서 자동", "형식 예시: <실제로 test한 후보 SHA>"],
      ["candidate.artifact_digest", "필수", "test한 배포 artifact", "Candidate lock에서 자동", "환경 실행 예시: sha256:61a3…"],
      ["harness_version", "필수", "검사기 코드 버전", "Git/빌드 자동", "849ae756…"],
      ["suite_version", "필수", "Manifest·Registry·Contract·test 묶음 버전", "내용 digest 자동", "sha256:5164…"],
      ["runs[].test_id", "필수", "실행한 test 파일과 함수", "실행기", "tests/.../test_tibero.py::test_connection_schema_roundtrip"],
      ["runs[].attempt", "필수", "1부터 연속되는 시도 번호", "실행기", "2"],
      ["runs[].outcome", "필수", "pass·fail·error·skip 중 실행 결과", "test 실행 결과", "pass"]
    ],
    before: "runs:\n  - test_id: tests/...::test_instance_code\n    attempt: 1\n    outcome: fail",
    after: "runs:\n  - test_id: tests/...::test_instance_code\n    attempt: 1\n    outcome: fail\n  - test_id: tests/...::test_instance_code\n    attempt: 2\n    outcome: pass",
    updateReason: "재시도 성공으로 첫 실패를 덮어쓰지 않습니다. 두 시도를 모두 새 Test run set에 남겨 T62가 기능 중요도에 따라 APPROVAL 여부를 판단하게 합니다.",
    commands: [
      "./.venv/bin/python harness/run_runtime_contracts.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --artifact-digest sha256:<배포파일해시> \\\n  --output-dir /path/to/run-002 \\\n  --run-id runtime-contract-002"
    ],
    storage: "실행별 불변 증거입니다. CI run ID·attempt와 함께 보관하고 같은 파일명을 다른 실행 결과로 덮어쓰지 않습니다."
  },
  result: {
    title: "검사 결과",
    path: "검사 실행별 evidence/acgh-result.yaml 또는 source-gate-results.json",
    purpose: "어떤 입력으로 어떤 검사들을 실행했고 각 판정과 이유가 무엇인지, 나중에 같은 결과인지 확인할 digest와 함께 기록합니다.",
    created: "소스 검사 또는 Runtime 검사를 실행할 때마다 자동 생성합니다.",
    update: "기존 결과는 수정하지 않습니다. 코드·정책·검사기·test·실행이 바뀌면 새 결과를 생성합니다.",
    owner: "검사 실행기가 자동 생성하고 책임자는 개별 gate의 reasons를 확인합니다.",
    readers: "책임자, T91 배포 승격 검사와 감사·인수인계",
    fields: [
      ["canonical_payload.verdict", "필수", "전체 기계 판정", "판정 엔진", "pass"],
      ["canonical_payload.gates[].name", "필수", "개별 검사 이름", "실행기", "customization-survival"],
      ["canonical_payload.gates[].verdict", "필수", "개별 판정", "판정 엔진", "block"],
      ["canonical_payload.gates[].reasons", "필수", "판정의 구체적 이유", "각 검사기", "required_path_missing: .../Entity.java"],
      ["canonical_payload.inputs", "필수", "후보·정책·저장소 등 판정 입력", "실행기", "1.13.1 소스 진단 예: candidate_commit: dee330ebd5…"],
      ["canonical_payload.harness_version", "필수", "검사기 버전", "자동", "849ae756…"],
      ["result_digest", "필수", "판정 본문 전체의 SHA-256", "자동", "sha256:2f8c…"],
      ["observational_metadata.run_id", "실행정보", "결과를 찾기 위한 실행 번호", "CI/실행기", "run-20260729-001"],
      ["expected_exit_code", "필수", "verdict에 대응하는 명령 종료 코드", "판정 엔진", "0 (PASS)"]
    ],
    before: "canonical_payload:\n  verdict: block\n  gates:\n    - name: customization-survival\n      verdict: block\n      reasons: [\"required_path_missing: ...\"]",
    after: "canonical_payload:\n  verdict: pass\n  gates:\n    - name: customization-survival\n      verdict: pass\n      reasons: [\"active_customizations=7\"]",
    updateReason: "BLOCK 결과 파일을 PASS로 직접 고치지 않습니다. 코드를 보완하고 검사기를 다시 실행해 새로운 결과와 result_digest를 만듭니다.",
    commands: [
      "./.venv/bin/python harness/run_source_candidate_gates.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \\\n  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \\\n  --output harness/registrations/om-temp-1.13.0/source-gate-results.json",
      "./.venv/bin/python harness/run_runtime_contracts.py \\\n  --repo /path/to/OM_TEMP \\\n  --harness harness \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --artifact-digest sha256:<배포파일해시> \\\n  --output-dir /path/to/runtime-evidence \\\n  --run-id runtime-contract-001"
    ],
    storage: "실행별 불변 증거입니다. 검사 대상 Git commit SHA·실행 번호·검사기 버전과 함께 보관합니다."
  },
  patch_lock: {
    title: "Patch-lock",
    path: "patch-replay 전략의 patch-source-lock.yaml",
    purpose: "patch-replay 방식을 사용할 때 BANK-OM commit을 어느 순서와 개정으로 다시 적용할지 고정합니다.",
    created: "통합 전략이 patch-replay일 때만 후보를 만들기 전에 생성합니다.",
    update: "같은 ID의 후속 commit, 적용 순서 또는 개정 번호가 바뀌면 새 Patch-lock revision을 만듭니다. vendor-merge에서는 만들지 않습니다.",
    owner: "변경관리 담당자가 순서를 승인하고 생성기가 commit 존재와 digest를 확인합니다.",
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
        label: "현재 OM_TEMP에는 생성 명령 없음",
        meaning: "현재 연습은 vendor-merge 전략이므로 Patch-lock을 만들지 않습니다. patch-replay를 채택하면 담당자가 적용 순서를 승인한 별도 생성 절차가 필요합니다.",
        command: "./.venv/bin/pytest -q harness/tests/test_patchlock.py"
      }
    ],
    storage: "patch-replay 후보별 불변 입력입니다. 이전 revision을 덮어쓰지 않고 Candidate lock에 사용한 Patch-lock digest를 기록합니다."
  }
};

window.WIKI_TOPICS = {
  repositories: {
    group: "목적과 브랜치 전략 상세",
    title: "현재 사용하는 두 저장소와 과거 참고 저장소",
    summary: "현재 운영 흐름은 OpenMetadata 코드를 관리하는 OM_TEMP와 검사 기준·결과를 관리하는 openmetadata-test 두 저장소를 사용합니다. easyseop/OpenMetadata는 과거 사례를 확인할 때만 보는 참고 저장소입니다.",
    sections: [
      ["현재 코드 저장소 · easyseop/OM_TEMP", "공식 1.13.0 코드에 BANK-OM-001~007을 재구현하고 1.13.1 업그레이드를 연습하는 OpenMetadata 코드 저장소입니다."],
      ["현재 검사 저장소 · easyseop/openmetadata-test", "Manifest·Registry·Contract, 검사기, 검사 결과, 정책과 문서를 관리합니다. 직원이 사용하는 OpenMetadata 화면을 제공하는 저장소가 아닙니다."],
      ["과거 참고만 · easyseop/OpenMetadata", "과거 BANK-OM-001~011 구현과 소스 검사 사례를 확인하는 참고 코드입니다. 현재 OM_TEMP 업그레이드 검사 대상이나 운영 배포 완료 코드로 표현하지 않습니다."]
    ],
    example: "OM_TEMP 코드 commit 메시지의 Customization-ID\n        ↕\n검사 저장소 Manifest의 customization_id",
    resultExample: "코드 저장소: easyseop/OM_TEMP · BANK-OM 구현 코드\n검사 저장소: easyseop/openmetadata-test · Manifest와 검사 결과\n연결 기준: Customization-ID와 Git commit SHA",
    update: "OpenMetadata 코드 저장소 branch·공식 기준·검사 등록 버전이 바뀌면 위키의 저장소 역할 표와 Registry source 값을 함께 갱신합니다.",
    caution: "OpenMetadata 코드와 검사자료를 한 저장소에 중복 복사하면 어느 쪽이 정본인지 달라질 수 있으므로 ID와 SHA로 연결합니다."
  },
  branches: {
    group: "목적과 브랜치 전략 상세",
    title: "patch branch와 custom branch",
    summary: "patch branch는 행내 변경이 없는 공식 버전 코드이고, custom branch는 공식 코드와 승인된 BANK-OM 변경이 함께 있는 행내 후보 이력입니다.",
    sections: [
      ["patch/om-<version>", "공식 OpenMetadata 특정 버전 전체 코드를 고정합니다. 행내 커스터마이징을 넣지 않습니다."],
      ["custom/om-<version>", "해당 공식 버전 위에 BANK-OM 변경과 충돌 해결 commit을 기록합니다."],
      ["verified tag", "검사가 끝난 정확한 custom commit을 다시 찾기 위해 붙입니다. tag 자체가 운영 배포 완료를 뜻하지는 않습니다."],
      ["다음 버전 Cycle", "직전 custom 이력에 새 공식 patch를 vendor-merge하고 충돌 해결·검사·tag 절차를 반복합니다."]
    ],
    sharedReportFigure: {
      title: "보고용 1차와 동일한 브랜치 Cycle",
      report: "공유문서/openmetadata-phase1-sharing-preview.html",
      selector: ".om-branch-visual"
    },
    example: "custom/om-1.13.0 + patch/om-1.13.1\n              ↓ vendor-merge\n       custom/om-1.13.1 후보\n              ↓ 검사·승인\n verified/om-1.13.1-bank.1",
    resultExample: "patch/om-1.13.1: 공식 코드만 존재\ncustom/om-1.13.1: 공식 코드 + BANK-OM + 충돌 해결 commit\nverified tag: 검사를 끝낸 정확한 custom commit 표시",
    update: "공식 목표 버전이 바뀌면 새 patch/custom branch를 만들고 Candidate lock의 upstream target과 candidate 값을 새로 생성합니다.",
    caution: "patch와 custom을 합치는 지점에서 Git 충돌이 발생할 수 있습니다. 검사기가 충돌 코드를 자동 선택하지 않으며 담당자가 해결 commit을 남깁니다."
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
      ["최종 검사 대상 commit SHA", "모든 BANK-OM 변경이 반영된 custom branch 전체 상태는 SHA 하나로 검사합니다. 1.13.0은 결정론적으로 재구성한 3a2811cf…로 다시 검사했고, 1.13.1 과거 커밋별 재적용 진단은 dee330ebd5…를 사용했습니다. 둘은 서로 다른 버전과 실행을 가리키며 BANK-OM-007만의 SHA가 아닙니다."],
      ["Artifact digest", "최종 후보 코드로 만든 이미지·패키지 파일의 SHA-256입니다. 예: sha256:61a3…. Git SHA와 별개이며 실제 배포 파일이 검사한 파일과 같은지 확인할 때 사용합니다. 현재 OM_TEMP 문서의 digest 예시는 형식 설명이고 운영 이미지 생성 증거는 아직 없습니다."]
    ],
    example: "git commit -m \"Tibero 연결 파일 누락 보완\" \\\n  -m \"Customization-ID: BANK-OM-007\"\n# Git이 새 SHA 7d19c895...를 자동 생성\n\nBANK-OM-007\n├─ 62e39da8...  최초 구현 8개 파일\n└─ 7d19c895...  누락 보완 2개 파일\n   → Manifest changed_paths = 현재 10개 파일\n\n공식 1.13.0에서 결정론적으로 다시 만든 최종 후보 3a2811cf...\n   → Candidate lock candidate.commit_sha = 3a2811cf...\n   → 모든 BANK-OM을 포함한 검사 대상 하나",
    resultExample: "기능 식별: BANK-OM-007\n기능 이력: 62e39da8… + 7d19c895…\n현재 기능 범위: changed_paths 10개\n1.13.0 재검증 대상: 3a2811cf…\n1.13.1 과거 커밋별 재적용 진단 대상: dee330ebd5…\n실제 vendor-merge 후보: 아직 만들지 않음",
    update: "기존 기능의 누락 보완이면 같은 ID로 새 commit을 만들고 Manifest의 series와 changed_paths를 갱신합니다. 독립 기능이면 새 ID를 발급합니다. 최종 custom branch SHA가 바뀌면 Candidate lock도 새로 만듭니다.",
    caution: "같은 문자열인 SHA가 기능의 마지막 commit과 현재 branch HEAD를 동시에 가리킬 수 있지만 역할은 다릅니다. 기능 이력 검사는 ID가 붙은 각 commit을 보고, 배포 전 검사는 custom branch의 최종 SHA 하나를 봅니다."
  },
  registration: {
    group: "검사 전 사전환경 상세",
    title: "새 BANK-OM 등록 절차",
    summary: "코드를 먼저 변경한 뒤 Git diff를 기준으로 Manifest 초안을 만들고, 사람이 기능 의미와 test를 확정합니다. Manifest 없이 코드만 commit하면 등록 검사에서 BLOCK됩니다.",
    sections: [
      ["1. ID 발급", "미사용 BANK-OM ID를 관리자가 발급합니다."],
      ["2. 코드와 commit", "한 업무 기능 단위로 코드를 변경하고 commit 본문에 Customization-ID를 넣습니다."],
      ["3. Manifest 초안", "생성기가 같은 ID가 붙은 모든 commit의 실제 변경 파일을 합쳐 changed_paths와 watch 초안을 만듭니다."],
      ["4. 사람 승인", "required, 간접 watch, Contract, owner와 criticality를 담당자가 정합니다."],
      ["5. 승인안 적용", "같은 digest의 승인서가 있을 때 현재 버전 Manifest·Registry 변경안과 commit inventory·최종 diff를 적용합니다. 과거 source snapshot 소유파일은 일반 후속 commit 때문에 다시 만들지 않습니다."],
      ["6. 검사", "등록자료 검사와 소스 검사를 실행하고 BLOCK 원인을 수정합니다."]
    ],
    example: "PYTHONPATH=harness python harness/prepare_registration.py plan \\\n  --repo /path/to/OM_TEMP \\\n  --registration harness/registrations/om-temp-1.13.0 \\\n  --patch-ref origin/patch/om-1.13.0 \\\n  --custom-ref origin/custom/om-1.13.0 \\\n  --product-version 1.13.0 \\\n  --output harness/preparation-plans/om-temp-1.13.0-YYYYMMDD\n\n# 사람 검토·digest 승인 뒤에만 apply\npython harness/registrations/om-temp-1.13.0/validate_registration_bundle.py --repo /path/to/OM_TEMP",
    resultExample: "등록 검증 PASS 예시\n- Manifest 구조와 작성 규칙: 7개 PASS\n- Registry·Manifest·Contract 연결: 7개 PASS\n- 공식 1.13.0 ↔ 행내 custom 1.13.0 차이: 111개 경로 PASS\n- 공용 파일 소유정보: 37개 경로 PASS\n- 필수 Python test 코드: 9개 PASS\n\n참고: 공식 1.13.0 → 공식 1.13.1 변경은 별도 비교 축이며 834개 경로입니다.",
    update: "같은 ID의 후속 commit에서 새 파일이 확인되면 plan이 해당 버전 Manifest의 changed_paths, commit inventory와 최종 diff 변경안을 만듭니다. required·watch·Contract 판단을 승인한 뒤 apply하고 등록자료 검사를 다시 실행합니다.",
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
      ["6. 제안 적용·검사", "담당자가 같은 digest의 제안을 승인하면 apply한 뒤 등록자료 검사와 T30·T31·T40·T42·T93을 다시 실행합니다. source snapshot 소유자료는 일반 후속 commit에서 자동 재생성하지 않습니다."]
    ],
    example: "git commit -m \"Tibero 연결 파일 누락 보완\" \\\n  -m \"Customization-ID: BANK-OM-007\"\n\n# 변경 전: 8개\nimplementation:\n  changed_paths:\n    - openmetadata-spec/.../tiberoConnection.json\n\n# 변경 후: 기존 8개 + 새 파일 2개\nimplementation:\n  changed_paths:\n    - openmetadata-spec/.../tiberoConnection.json\n    - openmetadata-ui/.../serviceConnection.ts\n    - openmetadata-ui/.../DatabaseServiceUtils.test.tsx",
    resultExample: "후속 commit 7d19c895…를 별도 기능으로 만들지 않고 BANK-OM-007에 연결\n→ series.allowed=true 확인\n→ changed_paths 8개에서 현재 전체 10개로 갱신\n→ 등록 범위 검사 PASS",
    update: "Manifest, 필요한 경우 Contract·Registry를 승인된 제안으로 갱신합니다. source snapshot을 새로 등록하는 별도 작업에서만 shared/source 소유자료를 갱신하고, patch-replay 전략에서만 Patch-lock revision과 source_commits를 추가합니다.",
    caution: "changed_paths는 현재 버전의 전체 범위만 보여줍니다. 어느 commit에서 파일이 추가됐는지는 Git 이력에서 확인하며, Manifest에 최초·후속 목록을 따로 만들지 않습니다."
  },
  automation: {
    group: "검사 전 사전환경 상세",
    title: "커밋 후 자동화와 사람 승인",
    summary: "현재 plan은 commit과 경로를 자동 분석해 제안·질문·diff를 만들고, apply는 사람이 승인한 같은 digest만 원자적으로 반영합니다. 자동 commit 감지와 운영 검사 시작은 CI 연동 범위로 남아 있습니다.",
    sections: [
      ["자동화한 항목", "patch/custom SHA, BANK-OM별 commit·변경 경로, 최종 diff, Manifest 변경안, 스키마·안전 차단, 제안 digest와 원자 적용"],
      ["사람이 결정할 항목", "required 파일, 간접 watch 의존, Contract invariant와 test, owner·criticality, 충돌 해결 코드와 최종 승인"],
      ["후보 확정 뒤 자동 생성", "Candidate lock v2는 소스 검사면 source-tree, 실제 빌드 결과면 build-artifact를 명시합니다."],
      ["환경 test 때 자동 생성", "Test run set과 검사 결과는 실행마다 새로 만들고 기존 결과를 덮어쓰지 않습니다."]
    ],
    example: "OM_TEMP 코드 commit\n  → plan: SHA·경로·Manifest 변경안\n  → 담당자 의미 확인·digest 승인\n  → apply: 승인한 등록 변경만 원자 적용\n  → 등록자료·소스 검사 또는 BLOCK",
    resultExample: "현재 1.13.0 plan: REVIEW_REQUIRED\n- 자동 변경 0\n- 기능별 사람 판단 5\n- 차단 0\n- 분석 오류 0\n- 승인·apply는 미실행\n사람 판단: required·Contract·bank-only watch·owner·충돌 해결은 자동 확정하지 않음",
    update: "생성 스크립트나 스키마가 바뀌면 CI workflow와 이 위키의 자동/수동 구분을 함께 갱신합니다.",
    caution: "자동화가 관리 branch를 직접 덮어쓰기보다 변경안을 Pull Request로 제시하고, 불일치가 남으면 병합을 차단하는 구성이 안전합니다."
  },
  upgrade: {
    group: "OM_TEMP 업그레이드 상세",
    title: "공식 버전 업그레이드 절차",
    summary: "공식 새 버전을 준비한 뒤 영향 경로를 먼저 확인하고, 직전 custom 이력에 공식 patch를 병합한 후보에서 충돌 해결·소스 검사·환경 test를 순서대로 수행합니다.",
    sections: [
      ["1. 공식 patch 준비", "공식 tag와 commit을 확인해 patch/om-<새버전>을 고정합니다."],
      ["2. 사전 영향 확인", "T42로 공식 A→B 변경과 upgrade_watch를 비교합니다."],
      ["3. vendor-merge", "직전 custom branch에 새 공식 patch를 병합합니다."],
      ["4. 충돌 해결", "공식 변경과 BANK-OM 의도를 모두 확인해 custom branch에 해결 commit을 남깁니다."],
      ["5. 등록 갱신", "해결 과정에서 새 파일·Contract·watch가 생기면 같은 ID의 Manifest를 갱신합니다."],
      ["6. 재검사", "소스 검사, build, Contract test, 업그레이드 test와 배포 일치 검사를 실행합니다."],
      ["7. tag·승인", "같은 후보와 artifact의 검사가 끝난 뒤 verified tag와 승인 자료를 만듭니다."]
    ],
    example: "patch/om-1.13.1 ─┐\n                    ├─ custom/om-1.13.1 후보 → 검사 → verified tag\ncustom/om-1.13.0 ─┘",
    resultExample: "OM_TEMP 1.13.1 연습 결과\n- BANK-OM-001~004: 언어 JSON 18개 경로에서 충돌\n- BANK-OM-005~007: 충돌 없이 적용\n- 충돌 해결 후 소스 검사: PASS\n- 전체 build·행내 Runtime test: 아직 실행 증거 없음\n- 1.13.1 진단 branch와 후보: 현재 로컬 작업 기록이며 easyseop/OM_TEMP 원격 branch·tag로 확인되지 않음",
    update: "업그레이드 과정에서 Manifest 경로가 바뀌면 새 버전 등록 폴더를 갱신하고, 후보 commit·artifact가 바뀌면 Candidate lock과 이후 결과를 모두 새로 생성합니다.",
    caution: "현재 OM_TEMP 1.13.1 연습은 BANK-OM별 충돌 진단을 위해 commit별 재적용을 사용했습니다. 이것을 실제 vendor-merge 완료 증거로 표현하지 않습니다."
  },
  conflicts: {
    group: "OM_TEMP 업그레이드 상세",
    title: "Git 충돌과 해결 보조 도구",
    summary: "이 보조 도구의 목적은 공식 JSON과 BANK-OM JSON이 서로 다른 항목을 바꿨는데도 Git이 큰 JSON 구간 전체를 충돌로 표시한 경우, 반복적인 수작업을 줄이기 위해 두 변경을 계산해 하나의 해결 파일 초안을 만드는 것입니다. 업무적으로 어느 값이 맞는지는 결정하지 않으며 담당자가 결과와 test를 확인해야 합니다.",
    sections: [
      ["1. 왜 사용하는가", "언어 JSON처럼 한 파일이 크면 공식 버전은 파일 뒤쪽을 바꾸고 BANK-OM은 중간에 새 항목을 추가했어도 Git이 같은 큰 구간을 충돌로 표시할 수 있습니다. 도구는 실제 JSON 항목 단위로 다시 비교해 함께 보존 가능한 변경인지 계산합니다."],
      ["2. 언제 사용할 수 있나", "이 Python 도구는 Git이 BANK-OM commit을 재적용하다 JSON 충돌로 멈춘 작업 폴더에서만 사용합니다. 일반 JSON 파일 정리 도구나 모든 branch merge 충돌 해결기가 아닙니다."],
      ["3. 같은 충돌 파일에서 읽는 세 버전", "Git은 충돌한 파일 하나에 공통 기준(BASE), 현재 branch의 내용(OURS), 지금 적용 중인 반대편 변경(THEIRS)을 함께 보관합니다. Git은 이 세 버전을 stage 1·2·3이라고 부릅니다. 숫자는 실행 순서가 아닙니다."],
      ["4. 무엇을 비교하나", "도구는 BASE→OURS에서 바뀐 JSON 최종 항목 목록과 BASE→THEIRS에서 바뀐 JSON 최종 항목 목록을 만듭니다. 예를 들어 label 객체 안의 instance-code는 label.instance-code라는 한 항목으로 비교합니다. 줄 번호와 들여쓰기는 비교 기준이 아닙니다."],
      ["5. 자동으로 합치는 조건", "두 변경 목록에 같은 JSON 항목이 하나도 없을 때만 OURS 전체를 유지하고 THEIRS에서 바뀐 항목을 추가·수정·삭제합니다. 이번 연습에서는 OURS가 공식 1.13.1, THEIRS가 BANK-OM입니다."],
      ["6. 자동으로 중단하는 조건", "양쪽이 같은 JSON 항목을 하나라도 변경했으면 최종 값이 같더라도 중단합니다. JSON 이외 파일이 충돌하거나 JSON을 읽을 수 없어도 중단합니다. 이때 도구가 임의로 값을 선택하지 않으며 담당자가 직접 비교해야 합니다."],
      ["7. 도구가 실제로 남기는 것", "성공하면 작업 폴더의 충돌 JSON을 깨끗한 JSON으로 다시 쓰고 터미널에 파일별 BANK-OM 적용 항목 수를 출력합니다. 그러나 Git index에는 아직 충돌 상태가 남아 있습니다. 별도 승인 보고서나 plan.json도 만들지 않습니다."],
      ["8. 사람이 이어서 하는 일", "git diff와 test로 수정 결과를 확인한 뒤 git add로 해당 파일을 '충돌 해결 확인' 상태로 바꿉니다. 이번 재적용 연습은 cherry-pick으로 시작했으므로 cherry-pick --continue를 사용했습니다. 실제 branch merge 중 충돌이었다면 merge --continue 또는 해결 commit을 사용합니다."]
    ],
    stageMap: [
      ["stage 1 · BASE", "두 변경의 공통 기준", "공식 1.13.0과 BANK-OM이 갈라지기 전 JSON", "git show :1:<파일경로>", "stage 1→2와 stage 1→3의 변경을 계산하는 기준"],
      ["stage 2 · OURS", "현재 checkout한 branch의 내용", "이번 연습에서는 HEAD인 공식 1.13.1 JSON", "git show :2:<파일경로>", "해결 파일의 바탕으로 유지"],
      ["stage 3 · THEIRS", "지금 적용 중인 반대편 변경", "이번 cherry-pick에서는 BANK-OM-001 commit의 JSON", "git show :3:<파일경로>", "BANK-OM이 추가·수정·삭제한 항목 계산"]
    ],
    stageNote: "이번 연습에서는 공식 1.13.1 branch에서 BANK-OM commit을 cherry-pick했기 때문에 stage 2=공식, stage 3=BANK-OM입니다. 일반 merge에서도 stage 2는 항상 현재 checkout한 쪽(OURS), stage 3은 들어오는 쪽(THEIRS)이므로 branch 방향을 바꾸면 공식/BANK-OM 대응도 바뀔 수 있습니다.",
    conditionMap: [
      ["충돌 파일 선별", "git diff --name-only --diff-filter=U로 아직 충돌 중인 파일 목록을 읽음", "모두 .json이면 다음 비교 진행", "JSON 이외 파일이 하나라도 있으면 모든 JSON을 쓰기 전에 중단"],
      ["현재 branch 변경 계산", "stage 1(BASE)과 stage 2(OURS)의 최종 JSON 항목별 값을 비교", "값이 달라진 항목 경로를 OURS 변경 목록으로 만듦", "JSON 문법 오류 또는 최상위 값이 객체가 아니면 모든 JSON을 쓰기 전에 중단"],
      ["적용할 변경 계산", "stage 1(BASE)과 stage 3(THEIRS)의 최종 JSON 항목별 값을 비교", "추가·수정·삭제된 항목을 THEIRS 변경 목록으로 만듦", "JSON 문법 오류 또는 최상위 값이 객체가 아니면 모든 JSON을 쓰기 전에 중단"],
      ["두 목록 겹침 확인", "OURS 변경 항목 경로 ∩ THEIRS 변경 항목 경로", "교집합이 0개면 OURS에 THEIRS 변경을 반영", "한 항목이라도 겹치면 최종 값이 같아도 모든 JSON을 쓰기 전에 중단"],
      ["반영 가능 여부", "THEIRS 변경을 OURS 구조에 실제로 넣을 수 있는지 확인", "가능하면 파일을 쓰고 resolved ... leaf changes=N 출력", "중간 객체 구조가 달라 반영할 수 없으면 오류. 앞에서 이미 쓴 파일이 있을 수 있으므로 git status와 diff를 확인"]
    ],
    conditionNote: "이번 BANK-OM-001 결과는 언어 JSON 18개 모두에서 겹치는 최종 항목이 0개였으므로 자동 작성 조건을 통과했습니다. 이 조건 통과는 JSON 병합 가능 여부만 뜻하며 기능 test PASS를 뜻하지 않습니다.",
    outcomeMap: [
      ["resolved ... leaf changes=9", "공식 JSON을 바탕으로 BANK-OM 항목 9개를 넣은 작업 파일을 작성했다는 뜻", "git diff로 9개 항목과 공식 항목 보존 여부를 확인하고 JSON·관련 기능 test 실행", "확인 전에는 git add나 Git 작업 계속 실행 금지"],
      ["git status에 UU", "도구가 파일 내용은 썼지만 Git에는 아직 충돌 미해결로 남아 있다는 뜻", "검토와 test를 통과한 파일만 git add", "UU를 도구 실패로 오해해 다시 실행하지 않음"],
      ["overlapping leaf changes", "공식과 BANK-OM이 같은 최종 JSON 항목을 둘 다 변경했다는 뜻", "자동 선택을 중단하고 두 값과 업무 의도를 담당자·승인자가 직접 결정", "결정 전 git add·continue 금지"],
      ["unresolved non-JSON conflicts", "Java·TypeScript 등 이 보조 도구가 처리하지 않는 충돌이 함께 있다는 뜻", "해당 파일을 일반 Git 충돌 해결 절차로 직접 비교·수정", "JSON 도구로 비JSON 코드를 자동 해결하려 하지 않음"],
      ["test 실패", "JSON 형식은 합쳐졌지만 실제 기능 조건을 만족하지 못했다는 뜻", "git add 전이면 파일을 다시 수정하고 test 재실행. 이미 add했다면 수정 후 다시 add", "test가 PASS할 때까지 cherry-pick/merge 완료 금지"]
    ],
    outcomeNote: "보조 도구의 완료 조건은 '해결 파일 초안 작성'까지입니다. 운영 담당자의 완료 조건은 diff 확인, JSON·관련 기능 test PASS, git add, 시작했던 Git 작업의 정상 완료, 해결 commit과 검사 결과 보관까지입니다.",
    walkthrough: [
      ["1", "Git", "BANK-OM 변경을 적용하다 충돌한 JSON을 stage 1·2·3으로 보관", "git diff --name-only --diff-filter=U에 충돌 파일 표시"],
      ["2", "담당자", "resolve_nonoverlapping_json_conflicts.py에 충돌 중인 저장소 경로 전달", "도구가 JSON 이외 충돌 여부와 동일 항목 겹침 여부를 먼저 검사"],
      ["3", "보조 도구", "공식 1.13.1 JSON을 기준으로 겹치지 않는 BANK-OM 항목만 적용", "작업 폴더의 JSON 수정 + 터미널에 파일별 적용 항목 수 출력"],
      ["4", "담당자", "git diff와 JSON·기능 test로 수정 결과 확인", "공식 항목 유지와 BANK-OM 항목 추가를 모두 확인"],
      ["5", "담당자", "확인한 파일만 git add 후 시작한 Git 작업을 계속", "재적용 연습이면 cherry-pick --continue, branch merge면 merge --continue 또는 해결 commit"]
    ],
    comparison: {
      title: "BANK-OM-001 ko-kr.json 실제 실행 전후",
      beforeTitle: "실행 전: Git이 선택하지 못해 남긴 충돌",
      before: "<<<<<<< HEAD  (공식 1.13.1)\n\"zoom-out\": \"축소\"\n=======\n\"instance-code\": \"인스턴스 코드\",\n\"sort-order\": \"Sort Order\"\n>>>>>>> 4df83b311f  (BANK-OM-001)",
      afterTitle: "실행 후: 공식 JSON에 BANK-OM 항목을 추가",
      after: "\"zoom-out\": \"축소\",\n\"code-group\": \"Code Group\",\n\"code-name\": \"Code Name\",\n\"code-value\": \"Code Value\",\n\"instance-code\": \"인스턴스 코드\",\n\"instance-code-lowercase-plural\": \"인스턴스 코드\",\n\"instance-code-plural\": \"인스턴스 코드\",\n\"sort-order\": \"Sort Order\"",
      note: "이 비교는 같은 한 줄을 서로 다른 값으로 바꾼 충돌이 아닙니다. 두 버전이 같은 큰 JSON 객체 구간을 각각 편집했기 때문에 Git은 자동 병합을 멈췄습니다. 보조 도구는 줄 위치가 아니라 JSON 항목 경로를 비교했고, 동일 항목 겹침이 0개여서 두 변경을 함께 보존했습니다."
    },
    example: "# 전제: Git이 JSON 충돌로 멈춘 작업 폴더\n# 세 버전을 직접 확인하는 명령(실제 파일 경로 사용)\ngit show :1:openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json\ngit show :2:openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json\ngit show :3:openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json\n\n# 보조 도구 실행\n./.venv/bin/python harness/tools/resolve_nonoverlapping_json_conflicts.py \\\n  --repo ../om-temp-1.13.1-upgrade\n\n# 성공 출력\nresolved .../languages/ko-kr.json: BANK-OM leaf changes=9\n\n# 도구 직후: 파일 내용은 해결됐지만 Git index는 아직 U(충돌 미해결)\ngit status --short\nUU openmetadata-ui/.../languages/ko-kr.json\n\n# 사람이 결과와 test를 확인한 뒤에만 해결로 표시\ngit diff -- .../languages/ko-kr.json\ngit add .../languages/ko-kr.json\ngit cherry-pick --continue",
    resultExample: "성공 시 터미널 출력\nresolved openmetadata-ui/.../languages/ko-kr.json: BANK-OM leaf changes=9\n\n이 한 줄의 정확한 뜻\n- 도구가 stage 2의 공식 JSON을 바탕으로 새 파일 내용을 작성함\n- stage 1→stage 3에서 찾은 BANK-OM 최종 항목 9개를 그 파일에 반영함\n- '검사 PASS'나 'Git 충돌 해결 완료'를 뜻하지 않음\n\n도구 실행 직후 상태\n- 작업 폴더 JSON: 충돌 표식 없이 공식 1.13.1 항목 + BANK-OM-001 항목이 함께 있음\n- Git index: git add 전이므로 아직 UU(충돌 미해결)\n- 별도 산출물: 없음. 결과는 수정된 JSON과 터미널 출력뿐임\n\n도구가 자동 실행하지 않는 것\n- git add·commit·test·cherry-pick --continue\n- 별도 결과 보고서·승인 파일·plan.json 생성\n\nBANK-OM-001 실제 전체 결과\n- 충돌한 언어 JSON: 고유 경로 18개\n- 각 파일에서 BANK-OM이 추가한 최종 항목: 9개\n- 공식과 BANK-OM이 동시에 바꾼 동일 항목: 0개\n- 담당자가 diff와 test를 확인한 뒤 남긴 해결 commit: 83b1e0ac7d…\n\n동일 항목이 겹칠 때의 실패 출력\nValueError: .../ko-kr.json: overlapping leaf changes: ['label.instance-code']\n→ 도구는 계획한 JSON을 하나도 쓰지 않고 중단\n→ 담당자가 공식 값과 BANK-OM 값을 비교하고 승인받은 값으로 직접 해결\n\nJSON 이외 충돌이 있을 때의 실패 출력\nValueError: unresolved non-JSON conflicts require manual review: ['.../Entity.java']\n→ 이 보조 도구의 처리 범위가 아니므로 파일을 수정하지 않음",
    evidence: [
      ["../../harness/tools/resolve_nonoverlapping_json_conflicts.py", "실제 JSON 충돌 보조 도구", "stage 1(BASE)·2(OURS)·3(THEIRS)를 읽고, BASE→OURS와 BASE→THEIRS의 최종 JSON 항목 목록을 비교하며, 같은 항목 또는 JSON 외 충돌에서 중단하는 구현을 확인합니다."],
      ["../../harness/registrations/om-temp-1.13.1/conflict-evidence/BANK-OM-001_ko-kr_full_conflict.txt", "Git이 남긴 실제 충돌 파일", "HEAD·BANK-OM 양쪽 전체 내용과 충돌 표식을 확인합니다."],
      ["../../harness/registrations/om-temp-1.13.1/conflict-evidence/BANK-OM-001_ko-kr_resolution.diff", "해결 전후 실제 diff", "공식 JSON을 유지하면서 BANK-OM 항목 9개가 추가된 결과를 확인합니다."],
      ["../../harness/registrations/om-temp-1.13.1/conflict-evidence/BANK-OM-001_ko-kr_resolved.json", "해결된 전체 JSON", "도구 실행 후 최종 파일 전체를 확인합니다."],
      ["../../harness/registrations/om-temp-1.13.1/upgrade-application-results.json", "BANK-OM별 적용 결과", "충돌 경로 수, 동일 항목 겹침 수와 결과 commit을 확인합니다."]
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
      ["승인 기록", "검사 run ID, 후보 commit, 판정 이유, 검토한 diff·test 링크, 조치 내용, 승인자와 승인 시각을 PR 또는 조직이 정한 승인 기록에 남깁니다. 현재 저장소에는 조직 표준 승인 양식이 없으므로 운영 도입 전에 정해야 합니다."],
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
    summary: "전체 PASS 문구만 보지 않고 먼저 어떤 저장소·commit·artifact를 검사했는지 확인한 뒤 각 gate의 판정과 이유, 실행하지 않은 범위를 읽습니다.",
    sections: [
      ["1. 검사 대상", "저장소, branch, candidate commit, 공식 기준과 artifact digest가 현재 검토 대상과 같은지 확인합니다."],
      ["2. 전체 판정", "PASS·APPROVAL·BLOCK·ANALYSIS ERROR 중 전체 결과를 확인합니다."],
      ["3. 개별 gate", "gates[].name·verdict·reasons에서 무엇이 통과·실패했는지 확인합니다."],
      ["4. 실행 범위", "소스 검사인지 Runtime test인지, NOT RUN 항목이 무엇인지 확인합니다."],
      ["5. 다음 조치", "BLOCK은 수정 후 재검사, APPROVAL은 담당자 근거·승인, ANALYSIS ERROR는 입력을 고친 뒤 재실행합니다."]
    ],
    example: "PASS: 해당 검사 조건만 통과\nAPPROVAL: 담당자 확인·승인 필요\nBLOCK: 코드·등록자료 수정 후 재검사\nANALYSIS ERROR: 검사 미완료, PASS로 간주 금지\nNOT RUN: 아직 결과 없음",
    resultExample: "OM_TEMP 1.13.1 source-gate-results.json 예시\ncandidate_lock.candidate.commit_sha: dee330ebd5…\ngates[T40].verdict: pass\ngates[T40].reasons: 실제 변경 경로와 Manifest 일치\nartifact_note: 소스 tree만 확인, 배포 이미지 미생성\n주의: 후보 생성은 커밋별 재적용이므로 vendor-merge 완료 증거는 아님",
    update: "새 검사 실행 결과를 만들 때 이전 결과를 수정하지 않고 검사 대상 Git commit SHA와 run ID가 다른 새 파일로 보관합니다.",
    caution: "소스 검사 PASS만으로 행내 환경 동작이나 운영 배포 완료를 뜻하지 않습니다. 현재 저장소에는 CI 보관 기간과 별개인 조직 소유 장기 증적 저장소·보존 기간이 정의돼 있지 않습니다. 이 정책과 저장 위치를 정하기 전에는 감사 대응이 가능한 운영 절차가 완성됐다고 표현하지 않습니다."
  },
  release: {
    group: "검사 결과 상세",
    title: "검증 tag와 배포 승인",
    summary: "검증 tag는 정해진 검사를 통과한 정확한 Git commit을 다시 찾기 위한 표시입니다. 실제 배포 승인은 같은 commit으로 만든 artifact와 설정이 검증 결과와 일치할 때 별도로 결정합니다.",
    sections: [
      ["verified tag", "예: verified/om-1.13.1-bank.1. 검사 완료 commit을 가리키지만 운영 배포 완료를 뜻하지 않습니다."],
      ["Candidate lock", "검사한 commit·tree·artifact를 고정합니다."],
      ["Release lock", "검사 결과, test 결과, 이미지와 Helm digest를 하나의 승격 대상으로 묶습니다."],
      ["T91", "실제 배포 관측값이 Release lock과 같고 검증 후 재빌드하지 않았는지 확인합니다."],
      ["사람 승인", "APPROVAL 사유, 운영 일정, rollback과 책임자를 확인한 뒤 최종 승인합니다."]
    ],
    example: "custom commit → Candidate lock → source/runtime/upgrade PASS\n→ verified tag → Release lock → T91 일치 확인 → 배포 승인",
    resultExample: "현재 확인된 결과\n- 1.13.0 결정론적 재검증 후보 3a2811cf…: 등록 검증 5종·소스 검사 8종 PASS\n- 1.13.1 과거 커밋별 재적용 진단 후보 dee330ebd5…: 당시 소스 검사 PASS\n- 1.13.1 진단 branch·후보: 로컬 기록이며 easyseop/OM_TEMP 원격에 게시된 branch·tag가 아님. 현재 Manifest v2 T41 결과는 재검증 필요\n- 실제 vendor-merge 후보, Runtime·업그레이드·배포 환경 결과: 아직 없음\n따라서 verified 배포 tag와 운영 배포 승인 완료로 표현하지 않음",
    update: "코드·artifact·Helm 중 하나라도 바뀌면 기존 tag·lock 결과를 재사용하지 않고 새 후보 revision과 검사를 만듭니다.",
    caution: "같은 소스에서 재빌드한 이미지라도 digest가 달라지면 검증한 artifact와 동일하지 않으므로 다시 검사해야 합니다."
  }
};

window.WIKI_TOPIC_OPERATION_CASES = {
  repositories: [
    ["현재 두 저장소의 역할·주소·연결 방식이 그대로임", "그대로 유지", "문서와 Registry source를 수정하지 않음", "정기 링크 점검만 수행"],
    ["코드 branch 또는 공식 기준 버전만 바뀜", "관련 값만 갱신", "저장소 역할 설명은 유지하고 branch·버전·Registry source 값 수정", "등록 검증과 문서 링크 검사"],
    ["저장소가 교체·분리·통합됨", "구조 전체 갱신", "정본 저장소, 권한, CI 연결, 명령 경로와 인수인계서 수정", "책임자 승인 후 전체 사전환경 검사"]
  ],
  branches: [
    ["같은 공식 버전의 custom branch에 일반 후속 commit만 추가", "브랜치 전략은 그대로 유지", "새 patch/custom branch를 만들지 않음. 기능 Manifest와 Candidate lock 변경 여부만 판단", "영향받은 소스 검사 재실행"],
    ["공식 목표 버전이 1.13.1에서 다음 버전으로 바뀜", "새 버전 기준으로 갱신", "새 patch/custom branch 생성, 도식의 버전 예시와 Candidate lock upstream·candidate 갱신", "T42→병합→충돌 해결→전체 검사"],
    ["vendor-merge 대신 다른 통합 전략을 채택", "전략·도식·검사 입력 모두 갱신", "branch 방향, 충돌 지점, Patch-lock 사용 여부와 운영 명령 수정", "전략 승인 후 T25·T30·T40·T93 재검토"]
  ],
  identity: [
    ["코드와 commit 이력에 변화가 없음", "그대로 유지", "BANK-OM ID·기능 commit SHA 목록·Candidate lock을 수정하지 않음", "추가 조치 없음"],
    ["기존 기능을 보완하는 새 commit 생성", "같은 ID의 이력 갱신", "기존 BANK-OM ID를 commit 본문에 사용하고 series와 현재 changed_paths 갱신", "T30·T31·T40·T93 재실행"],
    ["기존 기능과 독립적으로 배포·제거할 새 기능", "새 ID 발급", "새 BANK-OM ID, Manifest, Contract와 Registry 항목 생성", "신규 등록 검사 전체 실행"]
  ],
  registration: [
    ["등록된 코드·경로·업무 조건이 바뀌지 않음", "그대로 유지", "Manifest·Registry·Contract·파생 파일을 다시 만들지 않음", "정기 검사에서 기존 입력 digest 확인"],
    ["같은 ID가 이미 등록된 파일의 내용만 수정", "commit 이력과 파생 결과 갱신", "series에 새 SHA를 연결하되 changed_paths 파일명 목록은 그대로 유지", "등록 묶음 재생성 후 T30·T31·T40·T93"],
    ["새 파일·필수 조건·간접 의존·test가 생김", "관련 관리 파일 갱신", "changed_paths 갱신, required·watch·Contract는 담당자가 재판단, 파생 파일 재생성", "등록 검사와 영향받은 Contract test"]
  ],
  followup: [
    ["기존 등록 파일 안의 코드만 수정", "경로 목록은 그대로 유지", "같은 ID로 commit하고 series에 SHA 추가. changed_paths 파일명은 중복 추가하지 않음", "파생 파일 재생성, T30·T31·T40·T93"],
    ["기존 기능에 새 파일을 추가", "현재 범위 갱신", "changed_paths에 새 경로 추가하고 required·watch·Contract 해당 여부 판단", "등록 검사, T26·T40·T42·T93"],
    ["업무 목적·배포 단위가 기존 기능과 달라짐", "기존 ID를 갱신하지 않음", "새 ID를 발급하고 별도 Manifest·Contract 작성", "신규 등록 절차 실행"]
  ],
  automation: [
    ["생성기·스키마·CI 동작이 바뀌지 않음", "운영 설명은 그대로 유지", "현재 스크립트를 실행하고 생성 결과만 검토", "기존 자동/수동 책임 구분 유지"],
    ["생성기 출력 또는 Manifest 스키마 변경", "자동화 설명과 예시 갱신", "CI 명령, 생성 파일, 담당자 승인 지점과 실패 복구 절차 수정", "단위 test·등록 묶음 회귀검사"],
    ["검사 결과만 BLOCK 또는 ERROR", "자동화 문서를 바꾸지 않음", "결과가 가리킨 코드·입력·환경을 수정", "같은 자동화와 영향받은 검사 재실행"]
  ],
  upgrade: [
    ["같은 후보를 입력 변경 없이 다시 확인", "관리 입력은 그대로 유지", "Manifest·Candidate lock은 수정하지 않고 새 run ID로 결과만 추가", "실패했던 검사와 후속 검사 재실행"],
    ["공식 목표 버전 또는 후보 commit이 바뀜", "새 버전 입력으로 갱신", "새 등록 폴더·Candidate lock 생성, 기존 결과는 보존", "T42부터 전체 업그레이드 흐름 재실행"],
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
    ["같은 후보를 환경 복구 후 재검사", "새 결과 추가", "기존 실패·SKIP 결과를 남기고 새 run ID 결과 생성", "이전·새 결과와 변경된 환경 근거 함께 보관"],
    ["후보 commit·artifact·설정이 바뀜", "새 검사 묶음 생성", "새 Candidate lock 또는 Release lock과 전체 결과 생성", "과거 결과와 섞지 않고 revision별 보관"]
  ],
  release: [
    ["검사한 commit·artifact·Helm digest가 모두 같고 승인 유효", "기존 lock과 tag 유지", "검증 후 재빌드 없이 같은 대상을 배포 단계로 전달", "T91로 실제 배포 관측값 일치 확인"],
    ["코드·이미지·패키지·Helm 중 하나라도 변경", "새 후보와 lock 생성", "기존 verified tag를 옮기지 않고 새 revision·digest·검사 결과 생성", "Runtime·업그레이드·T91 재실행"],
    ["배포 관측값이 Release lock과 다름", "배포 승인 중단", "실제 배포 대상과 빌드·설정 변경 원인 조사", "일치하는 artifact로 교체하거나 새 후보 전체 재검사"]
  ]
};

Object.entries(window.WIKI_TOPIC_OPERATION_CASES).forEach(([key, cases]) => {
  if (window.WIKI_TOPICS[key]) {
    window.WIKI_TOPICS[key].operationCases = cases;
  }
});
