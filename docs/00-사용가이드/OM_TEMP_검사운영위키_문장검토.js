window.WIKI_SENTENCE_REVIEW = {
  "generated_at": "2026-07-30",
  "counts": {
    "유지": 572,
    "수정": 435,
    "삭제": 7,
    "추가": 90
  },
  "rows": [
    {
      "id": "1|topic.repositories.group",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.group",
      "original": "목적과 브랜치 전략 상세",
      "action": "유지",
      "final": "목적과 브랜치 전략 상세",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "1|topic.repositories.title",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.title",
      "original": "현재 사용하는 두 저장소와 과거 참고 저장소",
      "action": "수정",
      "final": "제품 코드 저장소와 검사기 저장소",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.repositories.summary",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.summary",
      "original": "현재 운영 흐름은 OpenMetadata 코드를 관리하는 OM_TEMP와 검사 기준·결과를 관리하는 openmetadata-test 두 저장소를 사용합니다. easyseop/OpenMetadata는 과거 사례를 확인할 때만 보는 참고 저장소입니다.",
      "action": "수정",
      "final": "제품 코드 저장소는 공식 OpenMetadata 코드와 BANK-OM 구현을 관리하고, 검사기 저장소는 Manifest·검사 프로그램·검사 결과를 관리합니다. 두 저장소는 BANK-OM ID와 Git commit SHA로 연결됩니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "1|topic.repositories.sections.0.0",
      "chapter": "1",
      "page": "상세 · 현재 사용하는 두 저장소와 과거 참고 저장소",
      "location": "topic.repositories.sections.0.0",
      "original": "현재 코드 저장소 · easyseop/OM_TEMP",
      "action": "삭제",
      "final": "삭제",
      "reason": "앞뒤 내용과 중복되거나 운영 판단에 필요하지 않아 삭제"
    },
    {
      "id": "1|topic.repositories.sections.0.1",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.sections.0.1",
      "original": "공식 1.13.0 코드에 BANK-OM-001~007을 재구현하고 1.13.1 업그레이드를 연습하는 OpenMetadata 코드 저장소입니다.",
      "action": "수정",
      "final": "공식 OpenMetadata 코드와 커스터마이징 구현 commit을 관리합니다. OpenMetadata 포크 브랜치에는 공식 코드를 그대로 두고 커스텀 브랜치에는 같은 공식 코드와 승인된 커스터마이징을 함께 둡니다. 검증과 승인이 끝나면 운영에 사용할 정확한 commit을 릴리즈 브랜치로 승격합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.repositories.sections.1.0",
      "chapter": "1",
      "page": "상세 · 현재 사용하는 두 저장소와 과거 참고 저장소",
      "location": "topic.repositories.sections.1.0",
      "original": "현재 검사 저장소 · easyseop/openmetadata-test",
      "action": "삭제",
      "final": "삭제",
      "reason": "앞뒤 내용과 중복되거나 운영 판단에 필요하지 않아 삭제"
    },
    {
      "id": "1|topic.repositories.sections.1.1",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.sections.1.1",
      "original": "Manifest·Registry·Contract, 검사기, 검사 결과, 정책과 문서를 관리합니다. 직원이 사용하는 OpenMetadata 화면을 제공하는 저장소가 아닙니다.",
      "action": "수정",
      "final": "Manifest·Registry·Contract, 검사기, 검사 결과, 정책과 운영 문서를 관리합니다. 사용자가 실행하는 OpenMetadata 제품 코드를 대신 보관하지 않습니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.repositories.sections.2.0",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.sections.2.0",
      "original": "과거 참고만 · easyseop/OpenMetadata",
      "action": "수정",
      "final": "두 저장소의 연결 기준",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.repositories.sections.2.1",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.sections.2.1",
      "original": "과거 BANK-OM-001~011 구현과 소스 검사 사례를 확인하는 참고 코드입니다. 현재 OM_TEMP 업그레이드 검사 대상이나 운영 배포 완료 코드로 표현하지 않습니다.",
      "action": "수정",
      "final": "commit 메시지의 `Customization-ID` 필드에는 BANK-OM ID를 적습니다. Manifest의 `customization_id`에도 같은 BANK-OM ID를 적어 코드 변경과 검사 기준을 연결합니다. Git commit SHA는 실제 변경 commit을 가리키는 별도 값이며, 하나의 BANK-OM ID에 여러 commit SHA가 연결될 수 있습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.repositories.update",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.update",
      "original": "OpenMetadata 코드 저장소 branch·공식 기준·검사 등록 버전이 바뀌면 위키의 저장소 역할 표와 Registry source 값을 함께 갱신합니다.",
      "action": "수정",
      "final": "아래 표에서 바꿀 항목이 `없음`이면 관리 파일을 수정하지 않습니다. 제품 코드 저장소의 URL·공식 버전·검사 대상 commit이 바뀐 경우에만 Registry의 source 값을 새 기준으로 바꾸고, 검사기 저장소의 URL이 바뀌면 실행 명령·CI·문서 링크를 바꿉니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.repositories.caution",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.caution",
      "original": "OpenMetadata 코드와 검사자료를 한 저장소에 중복 복사하면 어느 쪽이 정본인지 달라질 수 있으므로 ID와 SHA로 연결합니다.",
      "action": "수정",
      "final": "제품 코드와 검사자료를 두 저장소에 중복 보관하지 않습니다. 제품 코드는 제품 코드 저장소를 기준으로 삼고, 검사 기준과 결과는 검사기 저장소를 기준으로 삼습니다. 두 저장소는 BANK-OM ID와 Git commit SHA로 연결합니다.",
      "reason": "‘정본’ 대신 실제 기준 저장소를 직접 명시"
    },
    {
      "id": "1|topic.repositories.operationCases.0.0",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.0.0",
      "original": "현재 두 저장소의 역할·주소·연결 방식이 그대로임",
      "action": "수정",
      "final": "제품 코드 저장소와 검사기 저장소의 URL·역할, OpenMetadata 포크·커스텀·릴리즈 브랜치, 공식 버전과 검사 대상 commit이 모두 이전 점검 때와 같은 경우",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.repositories.operationCases.0.2",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.0.2",
      "original": "문서와 Registry source를 수정하지 않음",
      "action": "수정",
      "final": "운영 담당자는 두 저장소 링크가 열리고 권한이 유지되는지만 확인합니다. Registry, Manifest와 검사 명령은 수정하지 않습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.repositories.operationCases.0.3",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.0.3",
      "original": "정기 링크 점검만 수행",
      "action": "수정",
      "final": "새 검사 결과를 만들지 않습니다. 링크 확인 일자와 확인자만 정기 점검 기록에 남깁니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.repositories.operationCases.1.0",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.1.0",
      "original": "코드 branch 또는 공식 기준 버전만 바뀜",
      "action": "수정",
      "final": "두 저장소의 역할과 URL 및 공식 버전은 그대로지만, 커스텀 브랜치의 최종 commit만 바뀐 경우",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.repositories.operationCases.1.2",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.1.2",
      "original": "저장소 역할 설명은 유지하고 branch·버전·Registry source 값 수정",
      "action": "수정",
      "final": "개발자는 같은 BANK-OM ID로 후속 commit을 만들고 준비도구 plan을 실행합니다. 담당자는 Manifest와 파생 등록자료 변경안을 승인합니다. Registry 변경이 필요한 경우에만 proposal에 Registry 변경이 표시됩니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.repositories.operationCases.1.3",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.1.3",
      "original": "등록 검증과 문서 링크 검사",
      "action": "수정",
      "final": "apply 뒤 등록 검증과 T30·T31·T40·T93 등 영향받은 소스 검사를 실행합니다. 공식 버전이 같으므로 T42는 다시 실행하지 않습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.repositories.operationCases.2.0",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.2.0",
      "original": "저장소가 교체·분리·통합됨",
      "action": "수정",
      "final": "두 저장소의 역할과 URL은 그대로지만 공식 목표 버전이 바뀐 경우",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.repositories.operationCases.2.2",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.2.2",
      "original": "정본 저장소, 권한, CI 연결, 명령 경로와 인수인계서 수정",
      "action": "수정",
      "final": "업그레이드 담당자는 새 버전의 OpenMetadata 포크 브랜치와 등록 폴더 초안을 준비합니다. 이전 공식 버전과 새 공식 버전으로 T42를 먼저 실행한 뒤, 영향받을 BANK-OM ID와 경로를 확인하고 vendor-merge를 진행합니다.",
      "reason": "‘정본’ 대신 실제 기준 저장소를 직접 명시"
    },
    {
      "id": "1|topic.repositories.operationCases.2.3",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.2.3",
      "original": "책임자 승인 후 전체 사전환경 검사",
      "action": "수정",
      "final": "vendor-merge와 충돌 해결이 끝난 최종 커스텀 브랜치로 plan·승인·apply를 실행합니다. 기존 버전 폴더를 덮어쓰지 않고 새 제안·승인서·검사 결과를 함께 보관합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.group",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.group",
      "original": "목적과 브랜치 전략 상세",
      "action": "유지",
      "final": "목적과 브랜치 전략 상세",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "1|topic.branches.title",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.title",
      "original": "patch branch와 custom branch",
      "action": "수정",
      "final": "OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.summary",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.summary",
      "original": "patch branch는 행내 변경이 없는 공식 버전 코드이고, custom branch는 공식 코드와 승인된 BANK-OM 변경이 함께 있는 행내 후보 이력입니다.",
      "action": "수정",
      "final": "세 브랜치는 모두 제품 코드 저장소 안에 있습니다. OpenMetadata 포크 브랜치는 공식 코드를 그대로 보관하고, 커스텀 브랜치는 BANK-OM을 합치고 검사하는 작업선이며, 릴리즈 브랜치는 검증과 승인이 끝난 버전을 실제 운영에 제공하는 배포 기준선입니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.sections.0.1",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.sections.0.1",
      "original": "공식 OpenMetadata 특정 버전 전체 코드를 고정합니다. 행내 커스터마이징을 넣지 않습니다.",
      "action": "수정",
      "final": "공식 OpenMetadata의 특정 릴리즈 전체 코드를 그대로 가져와 보관합니다. BANK-OM과 충돌 해결 commit을 넣지 않습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.sections.1.1",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.sections.1.1",
      "original": "해당 공식 버전 위에 BANK-OM 변경과 충돌 해결 commit을 기록합니다.",
      "action": "수정",
      "final": "같은 공식 코드 위에 BANK-OM 변경과 충돌 해결 commit을 합칩니다. 검사는 이 브랜치의 정확한 commit을 대상으로 실행합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.sections.2.1",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.sections.2.1",
      "original": "검사가 끝난 정확한 custom commit을 다시 찾기 위해 붙입니다. tag 자체가 운영 배포 완료를 뜻하지는 않습니다.",
      "action": "수정",
      "final": "필수 검사를 끝낸 정확한 커스텀 commit에 붙이는 움직이지 않는 표시입니다. 태그만으로 운영 배포가 승인된 것은 아닙니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.sections.3.1",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.sections.3.1",
      "original": "직전 custom 이력에 새 공식 patch를 vendor-merge하고 충돌 해결·검사·tag 절차를 반복합니다.",
      "action": "수정",
      "final": "운영 승인 후 검증 완료 태그와 같은 commit을 가리키도록 갱신합니다. 실제 운영 배포는 이 브랜치를 기준으로 수행합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.branches.sharedReportFigure.title",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.sharedReportFigure.title",
      "original": "1차 요약과 동일한 브랜치 Cycle",
      "action": "유지",
      "final": "1차 요약과 동일한 브랜치 Cycle",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "1|topic.branches.sharedReportFigure.report",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.sharedReportFigure.report",
      "original": "공유문서/openmetadata-phase1-sharing-preview.html",
      "action": "유지",
      "final": "공유문서/openmetadata-phase1-sharing-preview.html",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "1|topic.branches.update",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.update",
      "original": "공식 목표 버전이 바뀌면 새 patch/custom branch를 만들고 Candidate lock의 upstream target과 candidate 값을 새로 생성합니다.",
      "action": "수정",
      "final": "공식 목표 버전이 바뀌면 새 OpenMetadata 포크 브랜치와 커스텀 브랜치를 만듭니다. 검사 대상을 고정하는 Candidate lock도 새 공식 버전과 새 커스텀 commit을 기준으로 다시 만듭니다. 필수 검사와 운영 승인이 끝난 뒤에만 릴리즈 브랜치를 검증 완료 태그와 같은 commit으로 갱신합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.branches.caution",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.caution",
      "original": "patch와 custom을 합치는 지점에서 Git 충돌이 발생할 수 있습니다. 검사기가 충돌 코드를 자동 선택하지 않으며 담당자가 해결 commit을 남깁니다.",
      "action": "수정",
      "final": "OpenMetadata 포크 브랜치와 커스텀 브랜치를 합치는 지점에서 Git 충돌이 발생할 수 있습니다. 검사기가 충돌 코드를 자동 선택하지 않으며 담당자가 해결 commit을 남깁니다. 릴리즈 브랜치는 Release lock과 T91 확인 전에는 운영 기준으로 갱신하지 않습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.operationCases.0.0",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.operationCases.0.0",
      "original": "같은 공식 버전의 custom branch에 일반 후속 commit만 추가",
      "action": "수정",
      "final": "같은 공식 버전의 커스텀 브랜치에 기존 BANK-OM 기능의 후속 commit만 추가한 경우",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.operationCases.0.1",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.operationCases.0.1",
      "original": "브랜치 전략은 그대로 유지",
      "action": "수정",
      "final": "OpenMetadata 포크 브랜치는 유지하고 검사 대상 custom branch commit만 갱신",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.operationCases.0.2",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.operationCases.0.2",
      "original": "새 patch/custom branch를 만들지 않음. 기능 Manifest와 Candidate lock 변경 여부만 판단",
      "action": "수정",
      "final": "같은 BANK-OM ID로 commit하고 Manifest 변경안을 확인합니다. 커스텀 브랜치의 마지막 commit이 바뀌므로 새 Candidate lock과 검사 결과를 만듭니다. 기존 릴리즈 브랜치는 검사·승인 전까지 움직이지 않습니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.branches.operationCases.0.3",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.operationCases.0.3",
      "original": "영향받은 소스 검사 재실행",
      "action": "수정",
      "final": "영향받은 소스·기능 검사를 다시 실행하고 새 검증 완료 태그와 Release lock을 준비한 뒤 승인 후 릴리즈 브랜치를 갱신합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.operationCases.1.0",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.operationCases.1.0",
      "original": "공식 목표 버전이 1.13.1에서 다음 버전으로 바뀜",
      "action": "수정",
      "final": "공식 목표 버전이 1.13.1에서 다음 버전으로 바뀐 경우",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.operationCases.1.1",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.operationCases.1.1",
      "original": "새 버전 기준으로 갱신",
      "action": "수정",
      "final": "새 버전용 포크·커스텀·릴리즈 브랜치를 준비",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.operationCases.1.2",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.operationCases.1.2",
      "original": "새 patch/custom branch 생성, 도식의 버전 예시와 Candidate lock upstream·candidate 갱신",
      "action": "수정",
      "final": "새 공식 코드를 담은 OpenMetadata 포크 브랜치와 그 코드를 BANK-OM 변경과 합칠 커스텀 브랜치를 만듭니다. Candidate lock에는 새 공식 commit과 새 커스텀 브랜치의 마지막 commit을 기록합니다. 릴리즈 브랜치는 승인 전에는 만들거나 이동하지 않습니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.branches.operationCases.1.3",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.operationCases.1.3",
      "original": "T42→병합→충돌 해결→전체 검사",
      "action": "수정",
      "final": "T42 사전 영향 확인 → 커스텀 브랜치 병합 → 충돌 해결 → 전체 검사 → 검증 완료 태그·Release lock → 승인 → 릴리즈 브랜치 갱신 순서로 진행합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.operationCases.2.0",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.operationCases.2.0",
      "original": "vendor-merge 대신 다른 통합 전략을 채택",
      "action": "수정",
      "final": "vendor-merge 대신 다른 통합 전략을 채택한 경우",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.operationCases.2.1",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.operationCases.2.1",
      "original": "전략·도식·검사 입력 모두 갱신",
      "action": "수정",
      "final": "전략·도식·검사 입력을 모두 다시 정함",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.branches.operationCases.2.2",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.operationCases.2.2",
      "original": "branch 방향, 충돌 지점, Patch-lock 사용 여부와 운영 명령 수정",
      "action": "수정",
      "final": "책임자가 새 전략을 승인한 뒤 어느 브랜치에서 무엇을 합치는지, 충돌을 어디서 해결하는지, Patch-lock이 필요한지와 실제 명령을 문서에 반영합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.branches.operationCases.2.3",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.operationCases.2.3",
      "original": "전략 승인 후 T25·T30·T40·T93 재검토",
      "action": "수정",
      "final": "전략 승인 기록을 보관하고 T25·T30·T40·T93의 입력과 판정 방식이 새 전략에서도 맞는지 다시 검토합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.identity.group",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.group",
      "original": "목적과 브랜치 전략 상세",
      "action": "유지",
      "final": "목적과 브랜치 전략 상세",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "1|topic.identity.title",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.title",
      "original": "BANK-OM ID, commit 메시지와 Git SHA",
      "action": "유지",
      "final": "BANK-OM ID, commit 메시지와 Git SHA",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "1|topic.identity.summary",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.summary",
      "original": "BANK-OM ID는 업무 기능 번호이고 Git commit SHA는 Git이 각 변경 상태에 자동 부여하는 식별값입니다. 같은 값이 아니며 서로 대신할 수 없습니다.",
      "action": "유지",
      "final": "BANK-OM ID는 업무 기능 번호이고 Git commit SHA는 Git이 각 변경 상태에 자동 부여하는 식별값입니다. 같은 값이 아니며 서로 대신할 수 없습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "1|topic.identity.sections.0.1",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.sections.0.1",
      "original": "사람이 업무 기능마다 한 번 발급합니다. 예: Tibero 연결 기능은 BANK-OM-007입니다. 공식 버전이 1.13.0에서 1.13.1로 바뀌어도 같은 기능이면 BANK-OM-007을 유지합니다.",
      "action": "유지",
      "final": "사람이 업무 기능마다 한 번 발급합니다. 예: Tibero 연결 기능은 BANK-OM-007입니다. 공식 버전이 1.13.0에서 1.13.1로 바뀌어도 같은 기능이면 BANK-OM-007을 유지합니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "1|topic.identity.sections.1.1",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.sections.1.1",
      "original": "변경 목적을 제목에 적고 본문에 `Customization-ID: BANK-OM-007`을 넣습니다. 생성기는 이 ID를 읽어 해당 commit의 변경 파일을 BANK-OM-007 Manifest에 연결합니다.",
      "action": "유지",
      "final": "변경 목적을 제목에 적고 본문에 `Customization-ID: BANK-OM-007`을 넣습니다. 생성기는 이 ID를 읽어 해당 commit의 변경 파일을 BANK-OM-007 Manifest에 연결합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "1|topic.identity.sections.2.0",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.sections.2.0",
      "original": "기능 변경 commit SHA",
      "action": "유지",
      "final": "기능 변경 commit SHA",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "1|topic.identity.sections.2.1",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.sections.2.1",
      "original": "코드를 commit할 때마다 Git이 자동 생성합니다. 예: 최초 Tibero 구현은 62e39da8…, 누락 파일 보완은 7d19c895…입니다. 사람이 두 SHA를 임의로 할당한 것이 아닙니다.",
      "action": "유지",
      "final": "코드를 commit할 때마다 Git이 자동 생성합니다. 예: 최초 Tibero 구현은 62e39da8…, 누락 파일 보완은 7d19c895…입니다. 사람이 두 SHA를 임의로 할당한 것이 아닙니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "1|topic.identity.sections.3.0",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.sections.3.0",
      "original": "왜 최신 기능 SHA 하나로 줄이지 않는가",
      "action": "유지",
      "final": "왜 최신 기능 SHA 하나로 줄이지 않는가",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "1|topic.identity.sections.3.1",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.sections.3.1",
      "original": "7d19c895…만 남기면 최초 commit 62e39da8…에서 변경한 8개 파일의 근거가 사라집니다. 생성기는 두 commit을 모두 읽어 현재 BANK-OM-007의 changed_paths 10개를 만듭니다.",
      "action": "유지",
      "final": "7d19c895…만 남기면 최초 commit 62e39da8…에서 변경한 8개 파일의 근거가 사라집니다. 생성기는 두 commit을 모두 읽어 현재 BANK-OM-007의 changed_paths 10개를 만듭니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "1|topic.identity.sections.4.0",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.sections.4.0",
      "original": "최종 검사 대상 commit SHA",
      "action": "유지",
      "final": "최종 검사 대상 commit SHA",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "1|topic.identity.sections.4.1",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.sections.4.1",
      "original": "모든 BANK-OM 변경이 반영된 custom branch 전체 상태는 SHA 하나로 검사합니다. 1.13.0은 결정론적으로 재구성한 3a2811cf…로 다시 검사했고, 1.13.1 과거 커밋별 재적용 진단은 dee330ebd5…를 사용했습니다. 둘은 서로 다른 버전과 실행을 가리키며 BANK-OM-007만의 SHA가 아닙니다.",
      "action": "수정",
      "final": "모든 BANK-OM 변경이 들어 있는 custom branch의 마지막 상태는 SHA 하나로 검사합니다. 1.13.0은 같은 입력으로 다시 만들면 같은 결과가 나오도록 재구성한 3a2811cf…를 검사했습니다. 1.13.1 commit별 재적용 진단에는 dee330ebd5…를 사용했습니다. 두 SHA는 서로 다른 버전의 전체 코드를 가리키며 BANK-OM-007 하나만 가리키는 값이 아닙니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.identity.sections.5.1",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.sections.5.1",
      "original": "최종 후보 코드로 만든 이미지·패키지 파일의 SHA-256입니다. 예: sha256:61a3…. Git SHA와 별개이며 실제 배포 파일이 검사한 파일과 같은지 확인할 때 사용합니다. 현재 OM_TEMP 문서의 digest 예시는 형식 설명이고 운영 이미지 생성 증거는 아직 없습니다.",
      "action": "수정",
      "final": "Artifact는 코드로 만든 이미지나 패키지 같은 배포 파일입니다. digest는 그 파일 내용으로 계산한 SHA-256 확인값입니다. 예: sha256:61a3…. Git commit SHA와 별개이며, 검사한 배포 파일과 실제 배포 파일이 같은지 확인할 때 사용합니다. 현재 값은 형식 예시일 뿐이며 OM_TEMP 운영 이미지를 만들었다는 증거는 아직 없습니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.identity.update",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.update",
      "original": "기존 기능의 누락 보완이면 같은 ID로 새 commit을 만들고 Manifest의 series와 changed_paths를 갱신합니다. 독립 기능이면 새 ID를 발급합니다. 최종 custom branch SHA가 바뀌면 Candidate lock도 새로 만듭니다.",
      "action": "수정",
      "final": "기존 기능을 보완할 때 개발자는 같은 BANK-OM ID로 commit합니다. plan은 같은 ID의 모든 commit SHA와 변경 경로를 자동으로 찾아 Manifest changed_paths와 commit-inventory 변경안을 만듭니다. 여러 commit을 허용하는 series.allowed, required·watch·Contract는 사람이 판단합니다. apply는 승인된 변경안만 반영합니다. 이후 소스 검사를 실행하면 검사기가 custom 브랜치의 최신 commit과 전체 파일 상태로 Candidate lock을 다시 계산해 결과 JSON 안에 기록합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.identity.caution",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.caution",
      "original": "같은 문자열인 SHA가 기능의 마지막 commit과 현재 branch HEAD를 동시에 가리킬 수 있지만 역할은 다릅니다. 기능 이력 검사는 ID가 붙은 각 commit을 보고, 배포 전 검사는 custom branch의 최종 SHA 하나를 봅니다.",
      "action": "수정",
      "final": "기능의 마지막 commit과 custom 브랜치의 마지막 commit이 우연히 같을 수 있습니다. 그래도 쓰임은 다릅니다. 기능 범위를 만들 때는 같은 BANK-OM ID가 붙은 모든 commit을 읽고, 배포 전에는 custom 브랜치 전체를 대표하는 마지막 commit 하나를 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.identity.operationCases.0.0",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.operationCases.0.0",
      "original": "코드와 commit 이력에 변화가 없음",
      "action": "수정",
      "final": "제품 코드와 commit 이력이 이전 승인 때와 같은 경우",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.identity.operationCases.0.2",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.operationCases.0.2",
      "original": "BANK-OM ID·기능 commit SHA 목록·Candidate lock을 수정하지 않음",
      "action": "수정",
      "final": "[자동 처리] 새 commit이 없으므로 준비도구가 제안할 변경도 없습니다. [담당자 확인] BANK-OM ID, Manifest와 commit-inventory를 수정하지 않습니다. 기존 검사 결과 안의 Candidate lock도 손으로 고치지 않습니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.identity.operationCases.1.0",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.operationCases.1.0",
      "original": "기존 기능을 보완하는 새 commit 생성",
      "action": "수정",
      "final": "기존 BANK-OM 기능의 누락을 보완하는 새 commit을 custom 브랜치에 추가한 경우",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.identity.operationCases.1.1",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.operationCases.1.1",
      "original": "같은 ID의 이력 갱신",
      "action": "수정",
      "final": "commit 발견·경로 계산·파일 반영은 자동, 기능 기준은 담당자가 승인",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.identity.operationCases.1.2",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.operationCases.1.2",
      "original": "기존 BANK-OM ID를 commit 본문에 사용하고 series와 현재 changed_paths 갱신",
      "action": "수정",
      "final": "[개발자 입력] 기존 BANK-OM ID를 commit 본문에 적고 plan을 실행합니다. [자동 처리] plan이 같은 ID의 모든 commit SHA와 실제 변경 경로를 찾아 changed_paths·commit-inventory 변경안을 만듭니다. [담당자 판단] 여러 commit 허용 여부, 필수 파일, 업그레이드 감시 경로와 Contract가 맞는지 확인하고 승인합니다. [자동 처리] apply가 승인된 변경안만 관리 파일에 반영합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.identity.operationCases.1.3",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.operationCases.1.3",
      "original": "T30·T31·T40·T93 재실행",
      "action": "수정",
      "final": "plan 제안·승인서·apply 결과를 보관하고 등록 검증과 T30·T31·T40·T93을 실행합니다. 이어서 소스 검사를 실행하면 검사 대상 custom 브랜치의 최종 commit과 파일 상태가 Candidate lock으로 자동 계산되어 결과 JSON 안에 기록됩니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.identity.operationCases.2.0",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.operationCases.2.0",
      "original": "기존 기능과 독립적으로 배포·제거할 새 기능",
      "action": "수정",
      "final": "기존 BANK-OM 기능과 별도로 배포하거나 제거할 수 있는 새 기능을 만든 경우",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|topic.identity.operationCases.2.2",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.operationCases.2.2",
      "original": "새 BANK-OM ID, Manifest, Contract와 Registry 항목 생성",
      "action": "수정",
      "final": "[담당자 판단] 새 BANK-OM ID를 발급하고 담당 조직, 필수 파일, 업그레이드 감시 경로와 Contract를 입력합니다. [개발자 입력] 새 ID를 commit 본문에 적습니다. [자동 처리] plan이 commit과 변경 경로를 읽어 Manifest·Registry 변경안과 commit 목록을 만듭니다. [담당자 승인] 생성된 기준이 실제 기능과 맞는지 확인합니다. [자동 처리] apply가 승인된 변경안만 관리 파일에 반영합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.identity.operationCases.2.3",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.operationCases.2.3",
      "original": "신규 등록 검사 전체 실행",
      "action": "수정",
      "final": "신규 등록 검증 전체와 관련 소스·Contract 검사를 실행합니다. 제안 폴더, 승인서, apply 결과와 첫 검사 결과를 함께 보관합니다. 소스 검사 결과의 Candidate lock도 검사 실행 때 자동 생성됩니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.registration.group",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.group",
      "original": "검사 전 사전환경 상세",
      "action": "유지",
      "final": "검사 전 사전환경 상세",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.registration.title",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.title",
      "original": "새 BANK-OM 등록 절차",
      "action": "유지",
      "final": "새 BANK-OM 등록 절차",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.registration.summary",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.summary",
      "original": "새 기능 코드를 BANK-OM ID와 함께 commit한 뒤, 사람 정책 입력과 Contract를 준비하고 plan으로 Manifest·Registry 변경안을 만듭니다. 새 ID를 설명할 사람 입력 없이 plan을 실행하면 BLOCK됩니다.",
      "action": "유지",
      "final": "새 기능 코드를 BANK-OM ID와 함께 commit한 뒤, 사람 정책 입력과 Contract를 준비하고 plan으로 Manifest·Registry 변경안을 만듭니다. 새 ID를 설명할 사람 입력 없이 plan을 실행하면 BLOCK됩니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.registration.sections.0.1",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.sections.0.1",
      "original": "미사용 BANK-OM ID를 관리자가 발급합니다.",
      "action": "유지",
      "final": "미사용 BANK-OM ID를 관리자가 발급합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|topic.registration.sections.1.0",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.sections.1.0",
      "original": "2. 코드와 commit",
      "action": "유지",
      "final": "2. 코드와 commit",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.registration.sections.1.1",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.sections.1.1",
      "original": "한 업무 기능 단위로 코드를 변경하고 commit 본문에 Customization-ID를 넣습니다.",
      "action": "유지",
      "final": "한 업무 기능 단위로 코드를 변경하고 commit 본문에 Customization-ID를 넣습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.registration.sections.2.1",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.sections.2.1",
      "original": "owner·criticality·required·간접 watch·series를 new-ID YAML에 작성합니다. 모르는 값을 임시로 넣지 않습니다.",
      "action": "유지",
      "final": "owner·criticality·required·간접 watch·series를 new-ID YAML에 작성합니다. 모르는 값을 임시로 넣지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.registration.sections.3.0",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.sections.3.0",
      "original": "4. Contract 작성",
      "action": "유지",
      "final": "4. Contract 작성",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.registration.sections.3.1",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.sections.3.1",
      "original": "업무 정상 조건과 필수 test를 contracts.yaml에 작성하고 customization_ids에 새 ID를 연결합니다. 준비도구가 이 내용을 대신 만들지 않습니다.",
      "action": "유지",
      "final": "업무 정상 조건과 필수 test를 contracts.yaml에 작성하고 customization_ids에 새 ID를 연결합니다. 준비도구가 이 내용을 대신 만들지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.registration.sections.4.1",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.sections.4.1",
      "original": "plan이 같은 ID가 붙은 commit의 실제 변경 파일을 합쳐 changed_paths와 watch를 계산하고 Manifest·Registry 변경안을 만듭니다. 이때 등록 폴더는 바뀌지 않습니다.",
      "action": "유지",
      "final": "plan이 같은 ID가 붙은 commit의 실제 변경 파일을 합쳐 changed_paths와 watch를 계산하고 Manifest·Registry 변경안을 만듭니다. 이때 등록 폴더는 바뀌지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.registration.sections.5.1",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.sections.5.1",
      "original": "담당자가 required·watch·Contract·owner와 diff를 확인해 proposal digest에 연결된 승인서를 작성합니다. apply는 승인한 동일 제안만 반영합니다.",
      "action": "수정",
      "final": "담당자가 required·watch·Contract·owner와 diff를 확인합니다. 승인서에는 검토한 제안의 내용 확인값(proposal digest)과 승인 사유를 적습니다. apply 명령은 승인한 제안과 확인값이 같을 때만 등록자료를 바꿉니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.registration.sections.6.1",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.sections.6.1",
      "original": "APPLIED 뒤 등록자료 5종과 공식 계보 Candidate의 소스 검사를 실행합니다. BLOCK 원인은 결과를 편집하지 않고 코드·등록 입력에서 수정합니다.",
      "action": "수정",
      "final": "APPLIED 뒤 등록자료 5종을 검사합니다. 이어서 공식 새 버전에서 출발한 검사 대상 코드로 소스 검사를 실행합니다. BLOCK이 나오면 결과 파일이 아니라 코드나 등록 입력을 수정합니다.",
      "reason": "‘공식 계보’ 대신 ‘공식 버전에서 출발한 코드’로 설명"
    },
    {
      "id": "3|topic.registration.update",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.update",
      "original": "새 ID 등록 뒤 같은 기능의 후속 commit이 생기면 새 ID 입력을 다시 만들지 않습니다. 같은 ID를 commit 본문에 쓰고 plan을 다시 실행해 changed_paths·commit inventory 변경안을 검토합니다. required·watch·Contract 판단이 바뀌었다면 사람 정책도 함께 갱신합니다.",
      "action": "유지",
      "final": "새 ID 등록 뒤 같은 기능의 후속 commit이 생기면 새 ID 입력을 다시 만들지 않습니다. 같은 ID를 commit 본문에 쓰고 plan을 다시 실행해 changed_paths·commit inventory 변경안을 검토합니다. required·watch·Contract 판단이 바뀌었다면 사람 정책도 함께 갱신합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.registration.caution",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.caution",
      "original": "생성기가 required나 업무 invariant를 임의로 확정하지 않습니다. 자동 초안을 검토하지 않고 그대로 병합하면 기능 누락을 잘못 판단할 수 있습니다.",
      "action": "유지",
      "final": "생성기가 required나 업무 invariant를 임의로 확정하지 않습니다. 자동 초안을 검토하지 않고 그대로 병합하면 기능 누락을 잘못 판단할 수 있습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|topic.registration.operationCases.0.0",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.operationCases.0.0",
      "original": "등록된 코드·경로·업무 조건이 바뀌지 않음",
      "action": "유지",
      "final": "등록된 코드·경로·업무 조건이 바뀌지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.registration.operationCases.0.2",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.operationCases.0.2",
      "original": "Manifest·Registry·Contract·파생 파일을 다시 만들지 않음",
      "action": "수정",
      "final": "Manifest·Registry·Contract와 자동 생성 목록을 다시 만들지 않음",
      "reason": "‘파생’ 대신 자동으로 생성되는 파일을 직접 설명"
    },
    {
      "id": "3|topic.registration.operationCases.0.3",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.operationCases.0.3",
      "original": "정기 검사에서 기존 입력 digest 확인",
      "action": "수정",
      "final": "정기 검사에서 기존 입력의 내용 확인값 확인",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "3|topic.registration.operationCases.1.0",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.operationCases.1.0",
      "original": "같은 ID가 이미 등록된 파일의 내용만 수정",
      "action": "유지",
      "final": "같은 ID가 이미 등록된 파일의 내용만 수정",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.registration.operationCases.1.1",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.operationCases.1.1",
      "original": "commit 이력과 파생 결과 갱신",
      "action": "수정",
      "final": "commit 기록과 자동 생성 목록 갱신",
      "reason": "‘파생’ 대신 자동으로 생성되는 파일을 직접 설명"
    },
    {
      "id": "3|topic.registration.operationCases.1.2",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.operationCases.1.2",
      "original": "series에 새 SHA를 연결하되 changed_paths 파일명 목록은 그대로 유지",
      "action": "수정",
      "final": "같은 ID의 새 commit을 기록하되 changed_paths의 파일명 목록은 그대로 유지",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.registration.operationCases.1.3",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.operationCases.1.3",
      "original": "등록 묶음 재생성 후 T30·T31·T40·T93",
      "action": "수정",
      "final": "새 plan과 승인 후 T30·T31·T40·T93",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.registration.operationCases.2.0",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.operationCases.2.0",
      "original": "새 파일·필수 조건·간접 의존·test가 생김",
      "action": "유지",
      "final": "새 파일·필수 조건·간접 의존·test가 생김",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.registration.operationCases.2.2",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.operationCases.2.2",
      "original": "changed_paths 갱신, required·watch·Contract는 담당자가 재판단, 파생 파일 재생성",
      "action": "수정",
      "final": "changed_paths 갱신, required·watch·Contract는 담당자가 다시 판단",
      "reason": "‘파생’ 대신 자동으로 생성되는 파일을 직접 설명"
    },
    {
      "id": "3|topic.registration.operationCases.2.3",
      "chapter": "3",
      "page": "상세 · 새 BANK-OM 등록 절차",
      "location": "topic.registration.operationCases.2.3",
      "original": "등록 검사와 영향받은 Contract test",
      "action": "수정",
      "final": "새 plan과 승인 후 등록 검사와 관련 Contract test",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.followup.title",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.title",
      "original": "기존 BANK-OM ID의 후속 commit",
      "action": "유지",
      "final": "기존 BANK-OM ID의 후속 commit",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.followup.summary",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.summary",
      "original": "기존 기능의 누락 보완·버그 수정처럼 같은 업무 목적과 함께 배포되는 변경은 같은 BANK-OM ID로 후속 commit을 만들 수 있습니다.",
      "action": "유지",
      "final": "기존 기능의 누락 보완·버그 수정처럼 같은 업무 목적과 함께 배포되는 변경은 같은 BANK-OM ID로 후속 commit을 만들 수 있습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.followup.sections.0.0",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.sections.0.0",
      "original": "1. 같은 ID 여부 판단",
      "action": "유지",
      "final": "1. 같은 ID 여부 판단",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.followup.sections.0.1",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.sections.0.1",
      "original": "업무 목적, 배포·제거 단위, 담당 조직과 Contract가 기존 기능과 같은지 확인합니다. 독립 기능이면 새 ID를 발급합니다.",
      "action": "유지",
      "final": "업무 목적, 배포·제거 단위, 담당 조직과 Contract가 기존 기능과 같은지 확인합니다. 독립 기능이면 새 ID를 발급합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.followup.sections.1.0",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.sections.1.0",
      "original": "2. Manifest series 확인",
      "action": "유지",
      "final": "2. Manifest series 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.followup.sections.1.1",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.sections.1.1",
      "original": "같은 ID에 여러 commit을 허용하도록 series.allowed가 true인지 확인합니다.",
      "action": "유지",
      "final": "같은 ID에 여러 commit을 허용하도록 series.allowed가 true인지 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.followup.sections.2.0",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.sections.2.0",
      "original": "3. 후속 commit 작성",
      "action": "유지",
      "final": "3. 후속 commit 작성",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.followup.sections.2.1",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.sections.2.1",
      "original": "commit 본문에 기존 Customization-ID를 그대로 넣습니다.",
      "action": "유지",
      "final": "commit 본문에 기존 Customization-ID를 그대로 넣습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.followup.sections.3.0",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.sections.3.0",
      "original": "4. 현재 변경 범위 갱신",
      "action": "유지",
      "final": "4. 현재 변경 범위 갱신",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.followup.sections.3.1",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.sections.3.1",
      "original": "후속 commit이 새 파일을 변경했다면 changed_paths에 추가합니다. 기존 등록 파일의 내용만 수정했다면 파일명 목록은 그대로 둡니다.",
      "action": "유지",
      "final": "후속 commit이 새 파일을 변경했다면 changed_paths에 추가합니다. 기존 등록 파일의 내용만 수정했다면 파일명 목록은 그대로 둡니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.followup.sections.4.0",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.sections.4.0",
      "original": "5. 필수·watch·Contract 재검토",
      "action": "유지",
      "final": "5. 필수·watch·Contract 재검토",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.followup.sections.4.1",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.sections.4.1",
      "original": "새 파일이 기능 필수 요소인지, 공식 업그레이드 감시와 test 갱신이 필요한지 확인합니다.",
      "action": "유지",
      "final": "새 파일이 기능 필수 요소인지, 공식 업그레이드 감시와 test 갱신이 필요한지 확인합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|topic.followup.sections.5.1",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.sections.5.1",
      "original": "담당자가 같은 digest의 제안을 승인하면 apply한 뒤 등록자료 검사와 T30·T31·T40·T42·T93을 다시 실행합니다. source snapshot 소유자료는 일반 후속 commit에서 자동 재생성하지 않습니다.",
      "action": "수정",
      "final": "담당자가 자신이 본 것과 같은 변경안을 승인하면 apply를 실행합니다. 그 뒤 등록자료 검사와 T30·T31·T40·T93 등 영향받은 소스 검사를 다시 실행합니다. T42는 공식 버전이 바뀔 때 vendor-merge 전에 실행하며, 같은 공식 버전의 일반 후속 commit 등록에서는 다시 실행하지 않습니다. Registry source.snapshot_sha의 custom commit을 설명하는 두 연결표도 일반 후속 commit에서 다시 만들지 않습니다.",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "3|topic.followup.update",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.update",
      "original": "Manifest, 필요한 경우 Contract·Registry를 승인된 제안으로 갱신합니다. source snapshot을 새로 등록하는 별도 작업에서만 shared/source 소유자료를 갱신하고, patch-replay 전략에서만 Patch-lock revision과 source_commits를 추가합니다.",
      "action": "수정",
      "final": "승인된 제안으로 변경 대상 Manifest와 commit-inventory.yaml·current-diff-paths.txt를 갱신합니다. Registry 변경이 필요한 경우에만 proposal에 Registry 변경을 함께 표시합니다. Contract는 사람이 직접 수정하고 새 plan으로 다시 검토합니다. Registry source.snapshot_sha의 custom commit을 바꾸는 별도 작업에서만 그 commit을 설명하는 두 연결표를 갱신합니다. Patch-lock의 개정 번호와 commit 목록은 patch-replay 전략에서만 사용합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.followup.caution",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.caution",
      "original": "changed_paths는 현재 버전의 전체 범위만 보여줍니다. 어느 commit에서 파일이 추가됐는지는 Git 이력에서 확인하며, Manifest에 최초·후속 목록을 따로 만들지 않습니다.",
      "action": "유지",
      "final": "changed_paths는 현재 버전의 전체 범위만 보여줍니다. 어느 commit에서 파일이 추가됐는지는 Git 이력에서 확인하며, Manifest에 최초·후속 목록을 따로 만들지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.followup.operationCases.0.0",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.operationCases.0.0",
      "original": "기존 등록 파일 안의 코드만 수정",
      "action": "유지",
      "final": "기존 등록 파일 안의 코드만 수정",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.followup.operationCases.0.1",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.operationCases.0.1",
      "original": "경로 목록은 그대로 유지",
      "action": "유지",
      "final": "경로 목록은 그대로 유지",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.followup.operationCases.0.2",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.operationCases.0.2",
      "original": "같은 ID로 commit하고 series에 SHA 추가. changed_paths 파일명은 중복 추가하지 않음",
      "action": "수정",
      "final": "같은 ID로 commit하고 기능별 commit 목록에 새 SHA 추가. changed_paths 파일명은 중복 추가하지 않음",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.followup.operationCases.0.3",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.operationCases.0.3",
      "original": "파생 파일 재생성, T30·T31·T40·T93",
      "action": "수정",
      "final": "새 plan과 승인 후 T30·T31·T40·T93",
      "reason": "‘파생’ 대신 자동으로 생성되는 파일을 직접 설명"
    },
    {
      "id": "3|topic.followup.operationCases.1.0",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.operationCases.1.0",
      "original": "기존 기능에 새 파일을 추가",
      "action": "유지",
      "final": "기존 기능에 새 파일을 추가",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.followup.operationCases.1.2",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.operationCases.1.2",
      "original": "changed_paths에 새 경로 추가하고 required·watch·Contract 해당 여부 판단",
      "action": "유지",
      "final": "changed_paths에 새 경로 추가하고 required·watch·Contract 해당 여부 판단",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.followup.operationCases.1.3",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.operationCases.1.3",
      "original": "등록 검사, T26·T40·T42·T93",
      "action": "수정",
      "final": "등록 검사와 T26·T40·T93 등 영향받은 소스 검사. T42는 공식 버전 업그레이드 때 별도로 실행",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.followup.operationCases.2.0",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.operationCases.2.0",
      "original": "업무 목적·배포 단위가 기존 기능과 달라짐",
      "action": "유지",
      "final": "업무 목적·배포 단위가 기존 기능과 달라짐",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.followup.operationCases.2.1",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.operationCases.2.1",
      "original": "기존 ID를 갱신하지 않음",
      "action": "유지",
      "final": "기존 ID를 갱신하지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.followup.operationCases.2.2",
      "chapter": "3",
      "page": "상세 · 기존 BANK-OM ID의 후속 commit",
      "location": "topic.followup.operationCases.2.2",
      "original": "새 ID를 발급하고 별도 Manifest·Contract 작성",
      "action": "유지",
      "final": "새 ID를 발급하고 별도 Manifest·Contract 작성",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.group",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.group",
      "original": "검사 전 사전환경 상세",
      "action": "유지",
      "final": "검사 전 사전환경 상세",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.title",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.title",
      "original": "검사 전 자동 갱신 범위와 전체 실행 절차",
      "action": "유지",
      "final": "검사 전 자동 갱신 범위와 전체 실행 절차",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.summary",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.summary",
      "original": "commit만으로 관리 파일이 바뀌지는 않습니다. 담당자가 plan을 실행하면 Git에서 확인 가능한 commit SHA·BANK-OM ID·변경 경로와 변경안을 계산하지만 실제 등록 폴더는 그대로 둡니다. 사람이 required·Contract·watch·owner와 변경안을 승인한 뒤 apply를 실행해야 승인된 관리 파일만 자동 갱신됩니다.",
      "action": "수정",
      "final": "담당자는 통합 실행 도구에 제품 코드 저장소 경로와 제품 버전을 입력합니다. 도구가 버전별 등록 폴더와 필요한 정책 파일을 자동으로 찾고 plan·검사 명령을 실행합니다. 필수 파일, Contract, watch, owner와 충돌 해결처럼 업무 판단이 필요한 값은 사람이 검토하고 승인합니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "3|topic.automation.sections.0.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.0.1",
      "original": "Git은 새 commit SHA와 diff를 기록합니다. 준비도구가 자동으로 시작되거나 Manifest·Registry가 자동으로 바뀌지는 않습니다. 담당자가 plan 명령을 실행해야 다음 단계가 시작됩니다.",
      "action": "수정",
      "final": "`harness/om_workflow.py`가 제품 버전으로 등록 폴더, 코드 경로 분류표, 중요 경로 정책과 기본 결과 위치를 자동 선택합니다. 사용자는 제품 코드 저장소 경로와 제품 버전을 입력하고, 새 공식 commit·실제 배포 파일처럼 도구가 추측하면 안 되는 값만 작업별로 추가합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.automation.sections.1.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.1.1",
      "original": "plan은 proposal.yaml, diff.patch, commit-inventory.yaml, current-diff-paths.txt와 변경 후 파일 미리보기를 새 제안 폴더에 만듭니다. 이 단계는 읽기 전용이며 실제 버전별 등록 폴더를 수정하지 않습니다.",
      "action": "수정",
      "final": "Git은 새 commit SHA와 diff를 기록합니다. 준비도구가 자동으로 시작되거나 Manifest·Registry가 자동으로 바뀌지는 않습니다. 담당자가 plan 명령을 실행해야 다음 단계가 시작됩니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "3|topic.automation.sections.2.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.2.0",
      "original": "승인 후 apply가 갱신",
      "action": "삭제",
      "final": "삭제",
      "reason": "앞뒤 내용과 중복되거나 운영 판단에 필요하지 않아 삭제"
    },
    {
      "id": "3|topic.automation.sections.2.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.2.1",
      "original": "apply는 변경 대상 Manifest, commit-inventory.yaml, current-diff-paths.txt를 갱신하고 새 ID 등 Registry 변경안이 있을 때만 customization-registry.yaml도 갱신합니다. contracts.yaml과 두 과거 코드 파일–BANK-OM 연결표는 일반 commit 처리에서 자동 갱신하지 않습니다.",
      "action": "수정",
      "final": "plan은 proposal.yaml, diff.patch, commit-inventory.yaml, current-diff-paths.txt와 변경 후 파일 미리보기를 새 제안 폴더에 만듭니다. 이 단계는 읽기 전용이며 실제 버전별 등록 폴더를 수정하지 않습니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "3|topic.automation.sections.3.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.3.1",
      "original": "커스터마이징 commit을 만든 뒤 검사기가 읽을 Manifest·Registry·commit inventory의 변경안을 Git 사실에 맞게 준비합니다. 준비 완료와 운영 배포 완료는 서로 다른 단계입니다.",
      "action": "수정",
      "final": "apply는 변경 대상 Manifest, commit-inventory.yaml, current-diff-paths.txt를 갱신하고 새 ID 등 Registry 변경안이 있을 때만 customization-registry.yaml도 갱신합니다. contracts.yaml과 Registry source.snapshot_sha의 custom commit을 설명하는 두 파일–BANK-OM 연결표는 일반 commit 처리에서 자동 갱신하지 않습니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.automation.sections.4.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.4.1",
      "original": "제품 코드는 easyseop/OM_TEMP에서 확인하고, 준비도구·Manifest·Registry·Contract는 easyseop/openmetadata-test의 codex/strict-manifest-gates branch에서 실행·관리합니다.",
      "action": "수정",
      "final": "커스터마이징 commit을 만든 뒤 검사기가 읽을 Manifest·Registry·commit inventory의 변경안을 Git 사실에 맞게 준비합니다. 준비 완료와 운영 배포 완료는 서로 다른 단계입니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "3|topic.automation.sections.5.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.5.1",
      "original": "openmetadata-test 저장소 루트에서 Git과 저장소의 .venv Python을 사용합니다. 제품 저장소는 원격 patch/custom branch를 받아왔고 git status --short 출력이 비어 있어야 합니다.",
      "action": "수정",
      "final": "제품 코드 저장소는 easyseop/OM_TEMP이고 검사기 저장소는 easyseop/openmetadata-test입니다. 준비도구·Manifest·Registry·Contract는 검사기 저장소의 codex/strict-manifest-gates 작업 브랜치에서 실행·관리합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.automation.sections.6.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.6.1",
      "original": "patch/custom commit SHA, BANK-OM별 commit 순서와 변경 경로, 최종 diff, Manifest 변경안과 승인 뒤 입력 변경 여부를 계산합니다.",
      "action": "수정",
      "final": "검사기 저장소의 최상위 폴더에서 `./.venv/bin/python harness/om_workflow.py <작업>` 형식으로 실행합니다. 제품 코드 저장소에는 원격 OpenMetadata 포크·커스텀 브랜치를 받아와야 하며 git status --short 출력이 비어 있어야 합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.automation.sections.7.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.7.1",
      "original": "proposal.yaml 내용 전체에서 계산한 SHA-256 식별값입니다. Git commit SHA와 다르며, 승인자가 본 변경안과 apply가 반영할 변경안이 정확히 같은지 확인하는 데 사용합니다.",
      "action": "수정",
      "final": "OpenMetadata 포크·커스텀 브랜치의 commit SHA, BANK-OM별 commit 순서와 변경 경로, 최종 diff, Manifest 변경안과 승인 뒤 입력 변경 여부를 계산합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.sections.8.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.8.0",
      "original": "검사 Candidate",
      "action": "삭제",
      "final": "삭제",
      "reason": "앞뒤 내용과 중복되거나 운영 판단에 필요하지 않아 삭제"
    },
    {
      "id": "3|topic.automation.sections.8.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.8.1",
      "original": "공식 OpenMetadata commit 이력 위에 BANK-OM 변경이 적용된 소스 검사 대상입니다. 독립 snapshot인 OM_TEMP custom HEAD를 그대로 공식 계보 Candidate라고 부르지 않습니다.",
      "action": "수정",
      "final": "proposal.yaml 전체 내용에서 계산한 SHA-256 값입니다. Git commit SHA와 다릅니다. 승인자가 본 변경안과 apply가 반영할 변경안이 같은지 확인하는 데 사용합니다.",
      "reason": "snapshot을 ‘과거 전체 파일 복사본’으로 설명 · ‘공식 계보’ 대신 ‘공식 버전에서 출발한 코드’로 설명"
    },
    {
      "id": "3|topic.automation.sections.9.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.9.1",
      "original": "required 파일, 간접 watch 경로, Contract의 업무 정상 조건과 test, owner·criticality, 충돌 해결 코드와 최종 승인은 자동으로 확정하지 않습니다. Contract 내용은 사람이 등록자료에 직접 작성합니다.",
      "action": "수정",
      "final": "Registry, Contract, 저장소 구조 설정, 공식 원본 기준 경로 분류 자료, 여러 BANK-OM이 함께 사용하는 경로 자료와 모든 Manifest의 내용을 묶어 계산합니다. plan 뒤 이 자료 중 하나라도 바뀌면 기존 승인을 재사용하지 않고 새 plan을 만듭니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.automation.sections.10.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.10.1",
      "original": "plan이 만든 proposal에 approval-template을 실행하면 미승인 양식이 생깁니다. 실제 승인자가 모든 질문에 사유를 기록한 뒤 apply를 실행하며, digest·Git SHA·등록 입력이 달라지면 중단합니다.",
      "action": "수정",
      "final": "승인한 공식 OpenMetadata 버전에서 출발해 BANK-OM 변경을 적용한 최종 코드입니다. 공식 Git 기록과 연결되지 않은 단순 파일 복사본은 이 검사 대상의 조건을 충족하지 않습니다.",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "3|topic.automation.sections.11.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.11.1",
      "original": "APPLIED가 나온 뒤 등록자료 5종을 검사하고, 공식 Git 계보를 가진 Candidate에서 소스 게이트를 실행합니다. 소스 PASS는 build·runtime·배포 PASS가 아닙니다.",
      "action": "수정",
      "final": "required 파일, 간접 watch 경로, Contract의 업무 정상 조건과 test, owner·criticality, 충돌 해결 코드와 최종 승인은 자동으로 확정하지 않습니다. Contract 내용은 사람이 등록자료에 직접 작성합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.automation.sections.12.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.12.1",
      "original": "제안 폴더 전체, 실제 승인서, apply 결과, 등록 검증 결과와 동일 Candidate lock의 후속 검사 결과를 삭제하지 않고 함께 보관합니다.",
      "action": "수정",
      "final": "plan이 만든 제안에 approval-template을 실행하면 아직 승인되지 않은 빈 양식이 생깁니다. 실제 승인자가 모든 질문에 사유를 적은 뒤 apply를 실행합니다. 제안 내용, Git commit, 등록 입력 중 하나라도 달라졌으면 apply가 중단됩니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.conditionTitle",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionTitle",
      "original": "준비도구가 진행 전에 확인하는 조건",
      "action": "유지",
      "final": "준비도구가 진행 전에 확인하는 조건",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.conditionIntro",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionIntro",
      "original": "각 조건은 자동화를 편하게 만들기 위한 권고가 아니라 잘못된 등록자료 적용을 막는 중단 기준입니다.",
      "action": "수정",
      "final": "담당자가 아래 조건을 하나씩 직접 검사할 필요는 없습니다. 담당자가 plan 명령을 한 번 실행하면 준비도구가 조건을 자동으로 확인하고, 터미널과 summary.md에 전체 상태와 건수를 표시합니다. 문제가 있으면 proposal.yaml의 blocked 또는 analysis_errors에 문제 코드·설명을 남기고 중단합니다. 다만 준비도구는 commit 뒤 자동으로 시작되지 않으므로 plan 명령 자체는 담당자가 실행해야 합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.conditionMap.0.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.0.1",
      "original": "Git에 기록한 파일의 미commit 수정과 아직 Git에 등록하지 않은 새 파일이 없는지 git status로 확인",
      "action": "수정",
      "final": "commit하지 않은 수정과 Git에 아직 등록하지 않은 새 파일이 없는지 git status로 확인",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.conditionMap.0.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.0.2",
      "original": "출력이 비어 있으면 Git 분석 진행",
      "action": "유지",
      "final": "출력이 비어 있으면 Git 분석 진행",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.conditionMap.0.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.0.3",
      "original": "로컬 변경이 있으면 BLOCK. 올바른 BANK-OM ID로 commit하거나 제품 저장소 밖으로 옮긴 뒤 plan 재실행",
      "action": "수정",
      "final": "로컬 변경이 있으면 BLOCK. 올바른 BANK-OM ID로 commit하거나 제품 코드 저장소 밖으로 옮긴 뒤 plan 재실행",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.conditionMap.1.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.1.0",
      "original": "patch/custom 관계",
      "action": "수정",
      "final": "포크·커스텀 브랜치 관계",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.automation.conditionMap.1.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.1.1",
      "original": "두 branch를 정확한 commit SHA로 고정하고 custom이 patch 이후 BANK-OM commit만 이어지는 구조인지 확인",
      "action": "수정",
      "final": "두 브랜치를 정확한 commit SHA로 고정하고 커스텀 브랜치가 OpenMetadata 포크 브랜치의 공식 코드에서 이어지는지 확인",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.conditionMap.1.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.1.2",
      "original": "patch 뒤에 custom commit이 한 줄로 이어지면 분석 진행",
      "action": "수정",
      "final": "포크 브랜치 뒤에 커스텀 commit이 이어지면 분석 진행",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.conditionMap.1.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.1.3",
      "original": "두 branch 이력이 이어지지 않거나 merge commit으로 갈라지면 ANALYSIS_ERROR. branch와 fetch 상태를 바로잡음",
      "action": "수정",
      "final": "두 브랜치 이력이 이어지지 않거나 분석하지 못하는 merge 구조이면 ANALYSIS_ERROR. 포크·커스텀 브랜치와 fetch 상태를 바로잡음",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.conditionMap.2.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.2.0",
      "original": "commit의 BANK-OM ID",
      "action": "유지",
      "final": "commit의 BANK-OM ID",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.conditionMap.2.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.2.1",
      "original": "각 commit 본문에서 Customization-ID를 읽음",
      "action": "유지",
      "final": "각 commit 본문에서 Customization-ID를 읽음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.conditionMap.2.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.2.2",
      "original": "commit마다 정확히 한 ID가 있으면 기능별 이력 생성",
      "action": "유지",
      "final": "commit마다 정확히 한 ID가 있으면 기능별 이력 생성",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.conditionMap.2.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.2.3",
      "original": "ID 없음·여러 ID·merge·빈 commit이면 BLOCK. commit 이력을 수정한 뒤 새 plan 생성",
      "action": "유지",
      "final": "ID 없음·여러 ID·merge·빈 commit이면 BLOCK. commit 이력을 수정한 뒤 새 plan 생성",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.automation.conditionMap.3.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.3.1",
      "original": "각 commit의 파일을 제품 Core·행내 전용·검사기 관리자료 영역으로 분류",
      "action": "유지",
      "final": "각 commit의 파일을 제품 Core·행내 전용·검사기 관리자료 영역으로 분류",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.conditionMap.3.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.3.2",
      "original": "한 commit이 한 영역만 변경하면 진행",
      "action": "유지",
      "final": "한 commit이 한 영역만 변경하면 진행",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.conditionMap.3.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.3.3",
      "original": "영역 혼합·미분류 경로·영역 분류 불일치면 BLOCK 또는 ANALYSIS_ERROR",
      "action": "유지",
      "final": "영역 혼합·미분류 경로·영역 분류 불일치면 BLOCK 또는 ANALYSIS_ERROR",
      "reason": "판정 이름과 그 판정이 뜻하는 결과가 함께 적혀 있어 유지"
    },
    {
      "id": "3|topic.automation.conditionMap.4.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.4.1",
      "original": "custom 소스에 실제 파일 대신 다른 위치를 가리키는 symlink, 별도 저장소를 가리키는 submodule, Git LFS 자리표시자가 있는지 확인",
      "action": "수정",
      "final": "custom 브랜치의 코드에 다른 위치를 가리키는 symlink, 별도 제품 코드 저장소를 가리키는 submodule, Git LFS 자리표시자가 있는지 확인",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.conditionMap.4.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.4.2",
      "original": "일반 파일이면 Manifest 변경안 계산",
      "action": "유지",
      "final": "일반 파일이면 Manifest 변경안 계산",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.conditionMap.4.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.4.3",
      "original": "지원하지 않는 파일 형식이 있으면 BLOCK. 자동으로 실제 내용을 추측하지 않음",
      "action": "유지",
      "final": "지원하지 않는 파일 형식이 있으면 BLOCK. 자동으로 실제 내용을 추측하지 않음",
      "reason": "판정 이름과 그 판정이 뜻하는 결과가 함께 적혀 있어 유지"
    },
    {
      "id": "3|topic.automation.conditionMap.5.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.5.1",
      "original": "실제 변경 경로와 기존 required·watch·Contract·Registry를 비교",
      "action": "유지",
      "final": "실제 변경 경로와 기존 required·watch·Contract·Registry를 비교",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.automation.conditionMap.5.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.5.2",
      "original": "Git 사실과 기존 정책이 일치하면 READY 또는 변경안 생성",
      "action": "유지",
      "final": "Git 사실과 기존 정책이 일치하면 READY 또는 변경안 생성",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.conditionMap.5.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.5.3",
      "original": "업무 판단이 필요하면 REVIEW_REQUIRED, 필수 경로 소실·폐기 ID 재사용이면 BLOCK",
      "action": "유지",
      "final": "업무 판단이 필요하면 REVIEW_REQUIRED, 필수 경로 소실·폐기 ID 재사용이면 BLOCK",
      "reason": "판정 이름과 그 판정이 뜻하는 결과가 함께 적혀 있어 유지"
    },
    {
      "id": "3|topic.automation.conditionMap.6.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.6.1",
      "original": "proposal digest, patch/custom SHA와 등록자료 digest를 apply 직전에 재확인",
      "action": "수정",
      "final": "제안 내용 확인값, 포크·커스텀 commit과 등록자료 내용 확인값을 apply 직전에 다시 비교",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "3|topic.automation.conditionMap.6.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.6.2",
      "original": "승인한 시점과 모두 같으면 잠금 후 적용",
      "action": "수정",
      "final": "승인한 시점과 모두 같으면 다른 apply 작업을 막은 뒤 적용",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.conditionMap.6.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.6.3",
      "original": "하나라도 바뀌면 STALE_PROPOSAL로 BLOCK. 기존 승인서를 고치지 않고 plan부터 다시 실행",
      "action": "유지",
      "final": "하나라도 바뀌면 STALE_PROPOSAL로 BLOCK. 기존 승인서를 고치지 않고 plan부터 다시 실행",
      "reason": "판정 이름과 그 판정이 뜻하는 결과가 함께 적혀 있어 유지"
    },
    {
      "id": "3|topic.automation.conditionMap.7.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.7.0",
      "original": "동시 적용과 파일 쓰기",
      "action": "유지",
      "final": "동시 적용과 파일 쓰기",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.conditionMap.7.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.7.1",
      "original": "등록 폴더에 독점 apply lock을 만들고 임시 파일을 원자 교체",
      "action": "수정",
      "final": "한 번에 하나의 apply만 실행되도록 잠그고, 모든 새 파일이 준비된 뒤 기존 파일을 교체",
      "reason": "구현 용어 대신 파일 교체와 실패 시 복구 행동을 설명"
    },
    {
      "id": "3|topic.automation.conditionMap.7.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.7.2",
      "original": "잠금 확보와 모든 파일 쓰기가 성공하면 APPLIED",
      "action": "수정",
      "final": "잠금을 확보하고 모든 파일을 쓰면 APPLIED",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.conditionMap.7.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.7.3",
      "original": "APPLY_LOCKED면 다른 작업 종료 확인. 쓰기 실패 시 이미 바꾼 파일을 복구하고 중단",
      "action": "수정",
      "final": "APPLY_LOCKED면 다른 작업 종료 여부를 확인. 파일 쓰기에 실패하면 이번에 바꾼 파일을 원래 상태로 복구하고 중단",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.conditionNote",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionNote",
      "original": "자동 중단 결과를 승인으로 바꾸거나 결과 파일의 상태값을 직접 편집하지 않습니다. 코드·branch·등록 입력을 수정한 뒤 새 출력 폴더에 plan을 다시 실행합니다.",
      "action": "수정",
      "final": "확인 순서는 summary.md에서 전체 상태와 문제 건수를 본 뒤, BLOCKED이면 proposal.yaml의 blocked, ANALYSIS_ERROR이면 analysis_errors, REVIEW_REQUIRED이면 review-required.yaml을 여는 방식입니다. 조건표의 각 항목을 별도 명령으로 반복 검사하거나 결과 파일의 상태값을 직접 편집하지 않습니다. 원인이 된 제품 코드·OpenMetadata 포크 브랜치·커스텀 브랜치·등록 입력을 수정한 뒤 새 출력 폴더에 plan을 다시 실행합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.automation.outcomeTitle",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeTitle",
      "original": "준비도구 상태별 다음 행동",
      "action": "유지",
      "final": "준비도구 상태별 다음 행동",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeIntro",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeIntro",
      "original": "준비도구 상태는 배포 판정이 아닙니다. 아래 담당자 조치가 끝나야 다음 단계로 이동할 수 있습니다.",
      "action": "수정",
      "final": "준비도구가 실행됐는지는 plan 출력 폴더의 summary.md와 proposal.yaml로 확인합니다. 두 파일이 없으면 준비도구를 실행하지 않은 것이므로 plan부터 실행합니다. 파일이 있으면 아래 상태에 맞는 조치를 합니다. 이 상태는 배포 판정이 아닙니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.outcomeMap.0.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.0.0",
      "original": "READY · 종료코드 0",
      "action": "유지",
      "final": "READY · 종료코드 0",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.0.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.0.1",
      "original": "자동 계산이 끝났고 사람 질문·차단·분석 오류가 없음",
      "action": "유지",
      "final": "자동 계산이 끝났고 사람 질문·차단·분석 오류가 없음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.0.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.0.2",
      "original": "diff.patch와 proposal.yaml을 검토하고 승인서를 작성",
      "action": "유지",
      "final": "diff.patch와 proposal.yaml을 검토하고 승인서를 작성",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.0.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.0.3",
      "original": "READY를 자동 승인이나 배포 가능으로 해석하지 않음",
      "action": "유지",
      "final": "READY를 자동 승인이나 배포 가능으로 해석하지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.1.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.1.0",
      "original": "REVIEW_REQUIRED · 종료코드 2",
      "action": "유지",
      "final": "REVIEW_REQUIRED · 종료코드 2",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.1.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.1.1",
      "original": "도구가 대신 결정하면 안 되는 업무 질문이 남음",
      "action": "유지",
      "final": "도구가 대신 결정하면 안 되는 업무 질문이 남음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.1.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.1.2",
      "original": "review-required.yaml의 모든 검토 항목 ID를 실제 담당자가 확인하고 질문별 사유 기록",
      "action": "유지",
      "final": "review-required.yaml의 모든 검토 항목 ID를 실제 담당자가 확인하고 질문별 사유 기록",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.automation.outcomeMap.1.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.1.3",
      "original": "실패로 오해해 정책을 삭제하거나 자리표시자 승인서를 사용하지 않음",
      "action": "유지",
      "final": "실패로 오해해 정책을 삭제하거나 자리표시자 승인서를 사용하지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.2.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.2.0",
      "original": "BLOCKED · 종료코드 1",
      "action": "유지",
      "final": "BLOCKED · 종료코드 1",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.2.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.2.1",
      "original": "확인된 안전 위반 때문에 제안을 적용할 수 없음",
      "action": "유지",
      "final": "확인된 안전 위반 때문에 제안을 적용할 수 없음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.2.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.2.2",
      "original": "터미널의 code와 proposal의 blocked 항목을 수정한 뒤 새 plan 생성",
      "action": "유지",
      "final": "터미널의 code와 proposal의 blocked 항목을 수정한 뒤 새 plan 생성",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.2.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.2.3",
      "original": "BLOCK 상태에서 apply 실행 또는 결과값 직접 수정 금지",
      "action": "유지",
      "final": "BLOCK 상태에서 apply 실행 또는 결과값 직접 수정 금지",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.3.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.3.0",
      "original": "ANALYSIS_ERROR · 종료코드 3",
      "action": "유지",
      "final": "ANALYSIS_ERROR · 종료코드 3",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.3.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.3.1",
      "original": "Git 관계·경로·스키마를 신뢰할 수 없어 분석을 완료하지 못함",
      "action": "수정",
      "final": "포크·커스텀 브랜치 관계, commit, 경로 또는 등록자료 형식을 믿을 수 없어 분석을 끝내지 못함",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.automation.outcomeMap.3.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.3.2",
      "original": "ref·Git 객체·등록자료 형식을 복구한 뒤 plan 재실행",
      "action": "수정",
      "final": "원격 포크·커스텀 브랜치 정보, Git commit, 등록자료 형식을 바로잡은 뒤 plan 재실행",
      "reason": "Git 내부 용어 대신 branch·작업 폴더의 실제 상태를 설명"
    },
    {
      "id": "3|topic.automation.outcomeMap.3.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.3.3",
      "original": "검사 결과가 없으므로 승인 단계로 이동하지 않음",
      "action": "유지",
      "final": "검사 결과가 없으므로 승인 단계로 이동하지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.4.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.4.0",
      "original": "APPLIED · 종료코드 0",
      "action": "유지",
      "final": "APPLIED · 종료코드 0",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.4.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.4.1",
      "original": "승인한 동일 제안이 등록자료에 반영됨",
      "action": "유지",
      "final": "승인한 동일 제안이 등록자료에 반영됨",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.4.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.4.2",
      "original": "apply 결과를 보관하고 등록 검증 5종과 소스 검사를 새로 실행",
      "action": "유지",
      "final": "apply 결과를 보관하고 등록 검증 5종과 소스 검사를 새로 실행",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.4.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.4.3",
      "original": "APPLIED를 기능 test·build·운영 배포 완료로 표현하지 않음",
      "action": "유지",
      "final": "APPLIED를 기능 test·build·운영 배포 완료로 표현하지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.5.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.5.1",
      "original": "승인 뒤 branch SHA 또는 등록 입력이 바뀌어 승인이 현재 상태와 다름",
      "action": "수정",
      "final": "승인 뒤 branch의 마지막 commit 또는 등록 입력이 바뀌어 승인이 현재 상태와 다름",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.outcomeMap.5.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.5.2",
      "original": "기존 승인서를 폐기하지 말고 증거로 보관한 뒤 새 plan과 새 승인 생성",
      "action": "수정",
      "final": "기존 승인서를 증거로 보관한 뒤 새 plan과 새 승인 생성",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.outcomeMap.5.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.5.3",
      "original": "승인서 digest나 SHA를 손으로 맞춰서 재사용하지 않음",
      "action": "수정",
      "final": "승인서의 내용 확인값이나 commit SHA를 손으로 고쳐 재사용하지 않음",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "3|topic.automation.outcomeMap.6.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.6.1",
      "original": "다른 apply 작업이 등록 폴더를 사용 중이거나 잠금이 남음",
      "action": "유지",
      "final": "다른 apply 작업이 등록 폴더를 사용 중이거나 잠금이 남음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.6.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.6.2",
      "original": "다른 작업 종료 여부와 담당자를 확인하고 필요하면 운영 책임자에게 상신",
      "action": "유지",
      "final": "다른 작업 종료 여부와 담당자를 확인하고 필요하면 운영 책임자에게 상신",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeMap.6.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeMap.6.3",
      "original": "작업자 확인 없이 잠금 파일 삭제 금지",
      "action": "유지",
      "final": "작업자 확인 없이 잠금 파일 삭제 금지",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.outcomeNote",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.outcomeNote",
      "original": "현재 OM_TEMP 1.13.0은 REVIEW_REQUIRED입니다. 자동 변경은 0건이지만 기존 bank-only watch 경로를 유지할지 묻는 기능별 질문 5건이 남아 있어 승인·apply를 실행하지 않았습니다.",
      "action": "수정",
      "final": "현재 적용 예시인 OM_TEMP 1.13.0 준비 결과는 REVIEW_REQUIRED입니다. 자동으로 바꿀 파일은 없지만, 공식 원본에는 없고 행내 코드에만 있는 watch 경로를 계속 유지할지 확인할 질문 5건이 남았습니다. 따라서 아직 승인과 apply를 실행하지 않았습니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.automation.walkthrough.0.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.0.2",
      "original": "openmetadata-test 루트, .venv, clean OM_TEMP clone, fetch된 patch/custom ref, 등록 폴더 쓰기 권한을 확인",
      "action": "수정",
      "final": "검사기 저장소 루트, .venv, 변경 중인 파일이 없는 제품 코드 저장소 clone과 fetch된 포크·커스텀 브랜치를 확인",
      "reason": "Git 내부 용어 대신 branch·작업 폴더의 실제 상태를 설명"
    },
    {
      "id": "3|topic.automation.walkthrough.0.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.0.3",
      "original": "git -C /path/to/OM_TEMP status --short 출력이 비어 있음",
      "action": "유지",
      "final": "git -C /path/to/OM_TEMP status --short 출력이 비어 있음",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|topic.automation.walkthrough.1.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.1.2",
      "original": "prepare_registration.py plan에 제품 저장소·등록 폴더·patch/custom ref·버전과 아직 존재하지 않는 새 출력 폴더 전달",
      "action": "수정",
      "final": "om_workflow.py plan에 제품 코드 저장소 경로와 제품 버전 전달. 도구가 등록 폴더·두 브랜치·새 출력 폴더를 자동 선택",
      "reason": "Git 내부 용어 대신 branch·작업 폴더의 실제 상태를 설명"
    },
    {
      "id": "3|topic.automation.walkthrough.1.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.1.3",
      "original": "터미널 JSON과 출력 폴더의 summary.md 생성",
      "action": "수정",
      "final": "화면의 자동 선택 목록과 결과 폴더의 summary.md 생성",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.walkthrough.2.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.2.2",
      "original": "summary.md → review-required.yaml → diff.patch 순서로 확인",
      "action": "유지",
      "final": "summary.md → review-required.yaml → diff.patch 순서로 확인",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.automation.walkthrough.2.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.2.3",
      "original": "상태, 질문·차단 건수, 승인 시 바뀔 파일을 설명할 수 있음",
      "action": "유지",
      "final": "상태, 질문·차단 건수, 승인 시 바뀔 파일을 설명할 수 있음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.walkthrough.3.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.3.2",
      "original": "proposal.yaml, commit-inventory.yaml, current-diff-paths.txt에서 고정 SHA와 BANK-OM별 경로 확인",
      "action": "유지",
      "final": "proposal.yaml, commit-inventory.yaml, current-diff-paths.txt에서 고정 SHA와 BANK-OM별 경로 확인",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.automation.walkthrough.3.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.3.3",
      "original": "Git diff와 Manifest 변경안이 같은 commit 범위를 가리킴",
      "action": "유지",
      "final": "Git diff와 Manifest 변경안이 같은 commit 범위를 가리킴",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.walkthrough.4.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.4.2",
      "original": "approval-template 명령으로 proposal digest에 연결된 새 양식 생성",
      "action": "수정",
      "final": "om_workflow.py approval-template에 proposal.yaml 경로를 전달",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "3|topic.automation.walkthrough.4.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.4.3",
      "original": "TEMPLATE_WRITTEN. 아직 실제 승인이 아님",
      "action": "수정",
      "final": "같은 폴더에 registration-approval.yaml 생성. 아직 실제 승인이 아님",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.walkthrough.5.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.5.2",
      "original": "approved_by·approved_at과 모든 검토 항목의 구체적인 reason을 작성",
      "action": "유지",
      "final": "approved_by·approved_at과 모든 검토 항목의 구체적인 reason을 작성",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|topic.automation.walkthrough.5.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.5.3",
      "original": "자리표시자가 없고 review-required.yaml의 검토 항목 ID를 정확히 한 번씩 포함",
      "action": "유지",
      "final": "자리표시자가 없고 review-required.yaml의 검토 항목 ID를 정확히 한 번씩 포함",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.automation.walkthrough.6.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.6.2",
      "original": "apply 명령에 같은 제품 저장소·등록 폴더·proposal·실제 승인서를 전달",
      "action": "수정",
      "final": "om_workflow.py apply에 제품 코드 저장소·버전·proposal·실제 승인서를 전달. 등록 폴더와 결과 경로는 자동 선택",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.automation.walkthrough.6.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.6.3",
      "original": "APPLIED와 written_files 출력 또는 상태별 중단 결과",
      "action": "유지",
      "final": "APPLIED와 written_files 출력 또는 상태별 중단 결과",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.walkthrough.7.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.7.2",
      "original": "validate_registration_bundle.py를 같은 제품 저장소와 버전 등록 폴더에 실행",
      "action": "수정",
      "final": "om_workflow.py validate에 제품 코드 저장소 경로와 버전 전달",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.walkthrough.7.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.7.3",
      "original": "등록자료 검사 5종이 모두 pass",
      "action": "수정",
      "final": "자동 선택된 등록자료의 검사 5종이 모두 pass",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.walkthrough.8.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.8.2",
      "original": "공식 Git 계보를 가진 Candidate를 준비하고 source gate runner 실행",
      "action": "수정",
      "final": "공식 새 버전에서 출발한 커스텀 브랜치를 준비하고 om_workflow.py source 실행",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.walkthrough.8.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.8.3",
      "original": "동일 Candidate lock에 연결된 8개 소스 gate 결과",
      "action": "수정",
      "final": "자동 선택된 정책으로 만든 Candidate lock과 8개 소스 검사 결과",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.walkthrough.9.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.9.2",
      "original": "제안 폴더·승인서·apply 결과·검사 결과·Candidate lock을 같은 변경 기록에 보관",
      "action": "유지",
      "final": "제안 폴더·승인서·apply 결과·검사 결과·Candidate lock을 같은 변경 기록에 보관",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|topic.automation.walkthrough.9.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.walkthrough.9.3",
      "original": "다음 담당자가 SHA·digest·승인자·실행 결과를 재확인 가능",
      "action": "수정",
      "final": "다음 담당자가 commit, 내용 확인값, 승인자, 실행 결과를 다시 확인할 수 있음",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "3|topic.automation.comparison.title",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.comparison.title",
      "original": "plan 실행 전후에 실제로 바뀌는 위치",
      "action": "유지",
      "final": "plan 실행 전후에 실제로 바뀌는 위치",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.comparison.beforeTitle",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.comparison.beforeTitle",
      "original": "실행 전: 등록 폴더는 현재 승인본",
      "action": "유지",
      "final": "실행 전: 등록 폴더는 현재 승인본",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.comparison.afterTitle",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.comparison.afterTitle",
      "original": "plan 실행 후: 등록 폴더는 그대로, 제안 폴더만 추가",
      "action": "유지",
      "final": "plan 실행 후: 등록 폴더는 그대로, 제안 폴더만 추가",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.comparison.note",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.comparison.note",
      "original": "plan은 등록자료와 승인서를 수정하지 않습니다. approval-template은 별도 미승인 양식만 만듭니다. 사람이 같은 digest를 승인한 뒤 apply가 APPLIED로 끝났을 때 변경 대상 Manifest, commit-inventory.yaml, current-diff-paths.txt와 필요한 Registry만 바뀝니다. Contract와 과거 코드 연결표는 apply가 자동 작성하거나 갱신하지 않습니다.",
      "action": "수정",
      "final": "plan은 등록자료와 승인서를 수정하지 않습니다. approval-template은 별도의 빈 승인 양식만 만듭니다. 사람이 같은 변경안을 승인하고 apply가 APPLIED로 끝났을 때만 Manifest, commit-inventory.yaml, current-diff-paths.txt와 필요한 Registry가 바뀝니다. Contract와 Registry source.snapshot_sha의 custom commit을 설명하는 연결표는 apply가 자동으로 작성하거나 갱신하지 않습니다.",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "3|topic.automation.update",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.update",
      "original": "같은 제품 commit과 등록 입력을 다시 검토할 때 기존 제안·승인·결과를 수정하지 않습니다. 코드 commit, branch SHA, Manifest·Registry·Contract, 생성기 또는 스키마 중 하나라도 바뀌면 새 출력 폴더에 plan을 다시 실행하고 새 digest로 승인받습니다.",
      "action": "수정",
      "final": "같은 제품 commit과 등록 입력을 다시 볼 때는 기존 제안·승인·결과를 수정하지 않습니다. 코드 commit, branch의 마지막 commit, Manifest·Registry·Contract, 생성기 또는 파일 작성 규칙 중 하나라도 바뀌면 새 출력 폴더에서 plan을 다시 실행하고 새 제안 내용 확인값으로 승인받습니다.",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "3|topic.automation.caution",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.caution",
      "original": "현재 구현은 commit 이후 자동 감지나 Pull Request 생성을 자동 실행하지 않습니다. 담당자가 plan 명령을 실행해야 하며, 도구는 사람 정책과 충돌 해결 코드를 결정하지 않습니다. 준비도구 APPLIED와 소스 gate PASS만으로 전체 build·행내 runtime·운영 배포가 완료됐다고 표현하지 않습니다.",
      "action": "수정",
      "final": "통합 실행 도구는 경로와 반복 옵션을 자동 선택하지만 commit 이후 스스로 시작되거나 Pull Request를 만들지는 않습니다. 담당자가 작업 명령을 실행해야 하며, 도구는 사람 정책과 충돌 해결 코드를 결정하지 않습니다. APPLIED와 소스 gate PASS만으로 전체 build·runtime·운영 배포가 완료됐다고 표현하지 않습니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.automation.operationCases.0.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.0.0",
      "original": "같은 commit·같은 등록 입력의 제안을 다시 조회",
      "action": "유지",
      "final": "같은 commit·같은 등록 입력의 제안을 다시 조회",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.0.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.0.1",
      "original": "기존 파일 그대로 유지",
      "action": "유지",
      "final": "기존 파일 그대로 유지",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.0.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.0.2",
      "original": "기존 proposal·승인·결과를 수정하지 않고 digest와 보관 위치만 확인",
      "action": "수정",
      "final": "기존 제안·승인·결과를 수정하지 않고 제안 내용 확인값과 보관 위치만 확인",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "3|topic.automation.operationCases.0.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.0.3",
      "original": "추가 실행 없음. 재실행이 필요하면 새 출력 폴더 사용",
      "action": "유지",
      "final": "추가 실행 없음. 재실행이 필요하면 새 출력 폴더 사용",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.1.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.1.0",
      "original": "기존 BANK-OM에 새 commit 또는 새 파일 추가",
      "action": "유지",
      "final": "기존 BANK-OM에 새 commit 또는 새 파일 추가",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.1.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.1.1",
      "original": "새 plan과 새 승인 필요",
      "action": "유지",
      "final": "새 plan과 새 승인 필요",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.1.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.1.2",
      "original": "같은 ID로 commit한 뒤 changed_paths 변경안과 required·watch·Contract 질문 검토",
      "action": "유지",
      "final": "같은 ID로 commit한 뒤 changed_paths 변경안과 required·watch·Contract 질문 검토",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.automation.operationCases.1.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.1.3",
      "original": "새 proposal·승인 보관 후 apply, 등록 검사와 영향 gate 재실행",
      "action": "유지",
      "final": "새 proposal·승인 보관 후 apply, 등록 검사와 영향 gate 재실행",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.2.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.2.0",
      "original": "신규 BANK-OM ID 발견",
      "action": "유지",
      "final": "신규 BANK-OM ID 발견",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.2.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.2.1",
      "original": "사람 정책 입력 추가 후 새 plan",
      "action": "유지",
      "final": "사람 정책 입력 추가 후 새 plan",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.2.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.2.2",
      "original": "owner·criticality·required·Contract를 new-ID 입력에 작성하고 담당자 승인",
      "action": "유지",
      "final": "owner·criticality·required·Contract를 new-ID 입력에 작성하고 담당자 승인",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|topic.automation.operationCases.2.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.2.3",
      "original": "신규 Registry·Manifest 제안 검토 후 전체 등록 검사",
      "action": "유지",
      "final": "신규 Registry·Manifest 제안 검토 후 전체 등록 검사",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.3.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.3.0",
      "original": "patch/custom SHA 또는 등록자료가 승인 뒤 변경",
      "action": "수정",
      "final": "OpenMetadata 포크·커스텀 브랜치의 마지막 commit 또는 등록자료가 승인 뒤 변경",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|topic.automation.operationCases.3.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.3.1",
      "original": "기존 승인 재사용 금지",
      "action": "유지",
      "final": "기존 승인 재사용 금지",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.3.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.3.2",
      "original": "STALE_PROPOSAL을 보관하고 현재 입력으로 plan부터 다시 실행",
      "action": "수정",
      "final": "STALE_PROPOSAL 결과를 보관하고 현재 입력으로 plan부터 다시 실행",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|topic.automation.operationCases.3.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.3.3",
      "original": "새 digest 승인·apply·등록 검사",
      "action": "수정",
      "final": "새 제안 내용 확인값 승인·apply·등록 검사",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "3|topic.automation.operationCases.4.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.4.0",
      "original": "생성기 출력·Manifest 스키마·CI 동작 변경",
      "action": "유지",
      "final": "생성기 출력·Manifest 스키마·CI 동작 변경",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.4.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.4.1",
      "original": "코드·위키·테스트 함께 갱신",
      "action": "유지",
      "final": "코드·위키·테스트 함께 갱신",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.4.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.4.2",
      "original": "생성 파일, 상태·종료코드, 승인 지점, 실패 복구와 증거 보관 설명 수정",
      "action": "유지",
      "final": "생성 파일, 상태·종료코드, 승인 지점, 실패 복구와 증거 보관 설명 수정",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.4.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.4.3",
      "original": "42개 집중 회귀 테스트와 전체 harness·CI 실행",
      "action": "유지",
      "final": "42개 집중 회귀 테스트와 전체 harness·CI 실행",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.5.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.5.0",
      "original": "BLOCKED·ANALYSIS_ERROR 발생",
      "action": "유지",
      "final": "BLOCKED·ANALYSIS_ERROR 발생",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.5.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.5.1",
      "original": "자동화 설명은 그대로 유지",
      "action": "유지",
      "final": "자동화 설명은 그대로 유지",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.5.2",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.5.2",
      "original": "blocked·analysis_errors가 가리킨 Git·코드·등록 입력만 수정",
      "action": "유지",
      "final": "blocked·analysis_errors가 가리킨 Git·코드·등록 입력만 수정",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|topic.automation.operationCases.5.3",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.operationCases.5.3",
      "original": "결과를 편집하지 않고 새 plan 실행",
      "action": "유지",
      "final": "결과를 편집하지 않고 새 plan 실행",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.upgrade.group",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.group",
      "original": "OM_TEMP 업그레이드 상세",
      "action": "유지",
      "final": "OM_TEMP 업그레이드 상세",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.upgrade.title",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.title",
      "original": "공식 버전 업그레이드 절차",
      "action": "유지",
      "final": "공식 버전 업그레이드 절차",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.upgrade.summary",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.summary",
      "original": "공식 새 버전을 준비한 뒤 영향 경로를 먼저 확인하고, 직전 custom 이력에 공식 patch를 병합한 후보에서 충돌 해결·소스 검사·환경 test를 순서대로 수행합니다.",
      "action": "수정",
      "final": "공식 새 버전을 OpenMetadata 포크 브랜치에 준비한 뒤 영향 경로를 먼저 확인하고, 새 커스텀 브랜치에서 직전 BANK-OM 이력과 합칩니다. 충돌 해결·소스 검사·환경 test를 통과하면 검증 완료 태그를 만들고, 승인 후 릴리즈 브랜치를 같은 commit으로 갱신합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|topic.upgrade.sections.0.0",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.sections.0.0",
      "original": "1. 공식 patch 준비",
      "action": "수정",
      "final": "1. OpenMetadata 포크 브랜치 준비",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.upgrade.sections.0.1",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.sections.0.1",
      "original": "공식 tag와 commit을 확인해 patch/om-<새버전>을 고정합니다.",
      "action": "수정",
      "final": "공식 태그와 commit을 확인해 fork/om-<새버전>을 고정합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|topic.upgrade.sections.1.1",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.sections.1.1",
      "original": "T42로 공식 A→B 변경과 upgrade_watch를 비교합니다.",
      "action": "유지",
      "final": "T42로 공식 A→B 변경과 upgrade_watch를 비교합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|topic.upgrade.sections.2.1",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.sections.2.1",
      "original": "직전 custom branch에 새 공식 patch를 병합합니다.",
      "action": "수정",
      "final": "새 커스텀 브랜치에서 직전 BANK-OM 이력과 새 OpenMetadata 포크 브랜치의 공식 코드를 병합합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.upgrade.sections.3.1",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.sections.3.1",
      "original": "공식 변경과 BANK-OM 의도를 모두 확인해 custom branch에 해결 commit을 남깁니다.",
      "action": "유지",
      "final": "공식 변경과 BANK-OM 의도를 모두 확인해 custom branch에 해결 commit을 남깁니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|topic.upgrade.sections.4.1",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.sections.4.1",
      "original": "해결 과정에서 새 파일·Contract·watch가 생기면 같은 ID의 Manifest를 갱신합니다.",
      "action": "수정",
      "final": "최종 커스텀 브랜치를 기준으로 plan을 실행합니다. 담당자는 Manifest·Registry 변경안과 required·watch·Contract 질문을 검토하고 승인한 뒤 apply를 실행합니다. Contract 변경이 필요하면 담당자가 직접 수정합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|topic.upgrade.sections.5.1",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.sections.5.1",
      "original": "소스 검사, build, Contract test, 업그레이드 test와 배포 일치 검사를 실행합니다.",
      "action": "유지",
      "final": "소스 검사, build, Contract test, 업그레이드 test와 배포 일치 검사를 실행합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|topic.upgrade.sections.6.1",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.sections.6.1",
      "original": "같은 후보와 artifact의 검사가 끝난 뒤 verified tag와 승인 자료를 만듭니다.",
      "action": "수정",
      "final": "같은 검사 대상 코드와 그 코드로 만든 배포 파일의 검사가 끝난 뒤 검증 완료 태그와 Release lock을 만들고, 승인 후 릴리즈 브랜치를 같은 commit으로 갱신합니다.",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "4|topic.upgrade.update",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.update",
      "original": "업그레이드 과정에서 Manifest 경로가 바뀌면 새 버전 등록 폴더를 갱신하고, 후보 commit·artifact가 바뀌면 Candidate lock과 이후 결과를 모두 새로 생성합니다.",
      "action": "수정",
      "final": "최종 커스텀 브랜치에서 plan을 실행해 새 버전 Manifest와 파생 등록자료 변경안을 만듭니다. Registry 변경이 필요한 경우에만 proposal에 함께 표시하며 Contract는 업무 동작이나 필수 test가 바뀌었을 때 담당자가 직접 갱신합니다. 검사 대상 commit이나 그 코드로 만든 배포 파일이 바뀌면 Candidate lock과 이후 검사 결과를 모두 새로 만듭니다.",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "4|topic.upgrade.caution",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.caution",
      "original": "현재 OM_TEMP 1.13.1 연습은 BANK-OM별 충돌 진단을 위해 commit별 재적용을 사용했습니다. 이것을 실제 vendor-merge 완료 증거로 표현하지 않습니다.",
      "action": "유지",
      "final": "현재 OM_TEMP 1.13.1 연습은 BANK-OM별 충돌 진단을 위해 commit별 재적용을 사용했습니다. 이것을 실제 vendor-merge 완료 증거로 표현하지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|topic.upgrade.operationCases.0.0",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.operationCases.0.0",
      "original": "같은 후보를 입력 변경 없이 다시 확인",
      "action": "수정",
      "final": "같은 검사 대상 custom branch commit을 입력 변경 없이 다시 확인",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.upgrade.operationCases.0.1",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.operationCases.0.1",
      "original": "관리 입력은 그대로 유지",
      "action": "유지",
      "final": "관리 입력은 그대로 유지",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.upgrade.operationCases.0.2",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.operationCases.0.2",
      "original": "Manifest·Candidate lock은 수정하지 않고 새 run ID로 결과만 추가",
      "action": "유지",
      "final": "Manifest·Candidate lock은 수정하지 않고 새 run ID로 결과만 추가",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|topic.upgrade.operationCases.0.3",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.operationCases.0.3",
      "original": "실패했던 검사와 후속 검사 재실행",
      "action": "유지",
      "final": "실패했던 검사와 후속 검사 재실행",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.upgrade.operationCases.1.0",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.operationCases.1.0",
      "original": "공식 목표 버전 또는 후보 commit이 바뀜",
      "action": "수정",
      "final": "공식 목표 버전 또는 검사 대상 custom branch commit이 바뀜",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.upgrade.operationCases.1.1",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.operationCases.1.1",
      "original": "새 버전 입력으로 갱신",
      "action": "유지",
      "final": "새 버전 입력으로 갱신",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.upgrade.operationCases.1.2",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.operationCases.1.2",
      "original": "새 등록 폴더·Candidate lock 생성, 기존 결과는 보존",
      "action": "유지",
      "final": "새 등록 폴더·Candidate lock 생성, 기존 결과는 보존",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.upgrade.operationCases.1.3",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.operationCases.1.3",
      "original": "T42부터 전체 업그레이드 흐름 재실행",
      "action": "유지",
      "final": "T42부터 전체 업그레이드 흐름 재실행",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.upgrade.operationCases.2.0",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.operationCases.2.0",
      "original": "충돌 해결 중 새 경로·동작 조건이 생김",
      "action": "유지",
      "final": "충돌 해결 중 새 경로·동작 조건이 생김",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.upgrade.operationCases.2.2",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.operationCases.2.2",
      "original": "같은 BANK-OM ID의 changed_paths·watch·Contract를 재판단",
      "action": "유지",
      "final": "같은 BANK-OM ID의 changed_paths·watch·Contract를 재판단",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|topic.upgrade.operationCases.2.3",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.operationCases.2.3",
      "original": "등록 검사·소스 검사·Contract test 재실행",
      "action": "유지",
      "final": "등록 검사·소스 검사·Contract test 재실행",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.group",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.group",
      "original": "OM_TEMP 업그레이드 상세",
      "action": "유지",
      "final": "OM_TEMP 업그레이드 상세",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.title",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.title",
      "original": "Git 충돌과 해결 보조 도구",
      "action": "유지",
      "final": "Git 충돌과 해결 보조 도구",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.summary",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.summary",
      "original": "이 보조 도구의 목적은 공식 JSON과 BANK-OM JSON이 서로 다른 항목을 바꿨는데도 Git이 큰 JSON 구간 전체를 충돌로 표시한 경우, 반복적인 수작업을 줄이기 위해 두 변경을 계산해 하나의 해결 파일 초안을 만드는 것입니다. 업무적으로 어느 값이 맞는지는 결정하지 않으며 담당자가 결과와 test를 확인해야 합니다.",
      "action": "수정",
      "final": "공식 코드와 BANK-OM이 JSON의 서로 다른 항목을 바꿨는데도 Git이 자동 병합을 멈추는 경우가 있습니다. 이 보조 도구는 두 변경을 함께 넣은 해결 파일 초안을 만듭니다. 어느 값이 업무상 맞는지는 결정하지 않으므로 담당자가 diff와 test를 확인해야 합니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "4|topic.conflicts.sections.0.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.sections.0.1",
      "original": "언어 JSON처럼 한 파일이 크면 공식 버전은 파일 뒤쪽을 바꾸고 BANK-OM은 중간에 새 항목을 추가했어도 Git이 같은 큰 구간을 충돌로 표시할 수 있습니다. 도구는 실제 JSON 항목 단위로 다시 비교해 함께 보존 가능한 변경인지 계산합니다.",
      "action": "유지",
      "final": "언어 JSON처럼 한 파일이 크면 공식 버전은 파일 뒤쪽을 바꾸고 BANK-OM은 중간에 새 항목을 추가했어도 Git이 같은 큰 구간을 충돌로 표시할 수 있습니다. 도구는 실제 JSON 항목 단위로 다시 비교해 함께 보존 가능한 변경인지 계산합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|topic.conflicts.sections.1.0",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.sections.1.0",
      "original": "2. 언제 사용할 수 있나",
      "action": "유지",
      "final": "2. 언제 사용할 수 있나",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.sections.1.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.sections.1.1",
      "original": "이 Python 도구는 Git이 BANK-OM commit을 재적용하다 JSON 충돌로 멈춘 작업 폴더에서만 사용합니다. 일반 JSON 파일 정리 도구나 모든 branch merge 충돌 해결기가 아닙니다.",
      "action": "수정",
      "final": "이 Python 도구는 Git이 BANK-OM commit을 재적용하다 JSON 충돌로 멈춘 제품 코드 저장소 작업 폴더에서만 사용합니다. 일반 JSON 파일 정리 도구나 모든 브랜치 병합 충돌 해결기가 아닙니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.sections.2.0",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.sections.2.0",
      "original": "3. 같은 충돌 파일에서 읽는 세 버전",
      "action": "유지",
      "final": "3. 같은 충돌 파일에서 읽는 세 버전",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.sections.2.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.sections.2.1",
      "original": "Git은 충돌한 파일 하나에 공통 기준(BASE), 현재 branch의 내용(OURS), 지금 적용 중인 반대편 변경(THEIRS)을 함께 보관합니다. Git은 이 세 버전을 stage 1·2·3이라고 부릅니다. 숫자는 실행 순서가 아닙니다.",
      "action": "수정",
      "final": "Git은 충돌한 파일의 공통 기준(BASE), 현재 작업 브랜치 내용(OURS), 병합해 들어오는 변경(THEIRS)을 함께 보관합니다. Git 명령에서는 각각 stage 1·2·3으로 표시하지만 숫자는 작업 순서가 아닙니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "4|topic.conflicts.sections.3.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.sections.3.1",
      "original": "도구는 BASE→OURS에서 바뀐 JSON 최종 항목 목록과 BASE→THEIRS에서 바뀐 JSON 최종 항목 목록을 만듭니다. 예를 들어 label 객체 안의 instance-code는 label.instance-code라는 한 항목으로 비교합니다. 줄 번호와 들여쓰기는 비교 기준이 아닙니다.",
      "action": "수정",
      "final": "도구는 BASE와 OURS를 비교해 현재 branch가 바꾼 JSON 항목을 찾고, BASE와 THEIRS를 비교해 들어오는 쪽이 바꾼 항목을 찾습니다. 예를 들어 label 안의 instance-code는 label.instance-code로 표시합니다. 줄 번호나 들여쓰기는 비교하지 않습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.sections.4.0",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.sections.4.0",
      "original": "5. 자동으로 합치는 조건",
      "action": "유지",
      "final": "5. 자동으로 합치는 조건",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.sections.4.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.sections.4.1",
      "original": "두 변경 목록에 같은 JSON 항목이 하나도 없을 때만 OURS 전체를 유지하고 THEIRS에서 바뀐 항목을 추가·수정·삭제합니다. 이번 연습에서는 OURS가 공식 1.13.1, THEIRS가 BANK-OM입니다.",
      "action": "유지",
      "final": "두 변경 목록에 같은 JSON 항목이 하나도 없을 때만 OURS 전체를 유지하고 THEIRS에서 바뀐 항목을 추가·수정·삭제합니다. 이번 연습에서는 OURS가 공식 1.13.1, THEIRS가 BANK-OM입니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|topic.conflicts.sections.5.0",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.sections.5.0",
      "original": "6. 자동으로 중단하는 조건",
      "action": "유지",
      "final": "6. 자동으로 중단하는 조건",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.sections.5.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.sections.5.1",
      "original": "양쪽이 같은 JSON 항목을 하나라도 변경했으면 최종 값이 같더라도 중단합니다. JSON 이외 파일이 충돌하거나 JSON을 읽을 수 없어도 중단합니다. 이때 도구가 임의로 값을 선택하지 않으며 담당자가 직접 비교해야 합니다.",
      "action": "유지",
      "final": "양쪽이 같은 JSON 항목을 하나라도 변경했으면 최종 값이 같더라도 중단합니다. JSON 이외 파일이 충돌하거나 JSON을 읽을 수 없어도 중단합니다. 이때 도구가 임의로 값을 선택하지 않으며 담당자가 직접 비교해야 합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|topic.conflicts.sections.6.0",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.sections.6.0",
      "original": "7. 도구가 실제로 남기는 것",
      "action": "유지",
      "final": "7. 도구가 실제로 남기는 것",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.sections.6.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.sections.6.1",
      "original": "성공하면 작업 폴더의 충돌 JSON을 깨끗한 JSON으로 다시 쓰고 터미널에 파일별 BANK-OM 적용 항목 수를 출력합니다. 그러나 Git index에는 아직 충돌 상태가 남아 있습니다. 별도 승인 보고서나 plan.json도 만들지 않습니다.",
      "action": "수정",
      "final": "성공하면 작업 폴더의 충돌 JSON을 다시 쓰고 터미널에 적용한 BANK-OM 항목 수를 출력합니다. Git 상태에는 아직 충돌 미해결로 표시됩니다. 별도 승인 보고서나 결과 파일은 만들지 않습니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "4|topic.conflicts.sections.7.0",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.sections.7.0",
      "original": "8. 사람이 이어서 하는 일",
      "action": "유지",
      "final": "8. 사람이 이어서 하는 일",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.sections.7.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.sections.7.1",
      "original": "git diff와 test로 수정 결과를 확인한 뒤 git add로 해당 파일을 '충돌 해결 확인' 상태로 바꿉니다. 이번 재적용 연습은 cherry-pick으로 시작했으므로 cherry-pick --continue를 사용했습니다. 실제 branch merge 중 충돌이었다면 merge --continue 또는 해결 commit을 사용합니다.",
      "action": "수정",
      "final": "git diff와 test로 수정 결과를 확인한 뒤 git add로 해당 파일을 '충돌 해결 확인' 상태로 바꿉니다. 이번 재적용 연습은 cherry-pick으로 시작했으므로 cherry-pick --continue를 사용했습니다. 실제 custom 브랜치 병합 중 충돌이었다면 merge --continue 또는 해결 commit을 사용합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.stageMap.0.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.stageMap.0.2",
      "original": "공식 1.13.0과 BANK-OM이 갈라지기 전 JSON",
      "action": "유지",
      "final": "공식 1.13.0과 BANK-OM이 갈라지기 전 JSON",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.stageMap.0.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.stageMap.0.3",
      "original": "git show :1:<파일경로>",
      "action": "유지",
      "final": "git show :1:<파일경로>",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.stageMap.0.4",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.stageMap.0.4",
      "original": "stage 1→2와 stage 1→3의 변경을 계산하는 기준",
      "action": "수정",
      "final": "현재 branch와 들어오는 쪽의 변경을 계산하는 기준",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.stageMap.1.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.stageMap.1.1",
      "original": "현재 checkout한 branch의 내용",
      "action": "수정",
      "final": "현재 열어 둔 branch의 내용",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.stageMap.1.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.stageMap.1.2",
      "original": "이번 연습에서는 HEAD인 공식 1.13.1 JSON",
      "action": "수정",
      "final": "이번 연습에서는 공식 1.13.1 JSON",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.stageMap.1.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.stageMap.1.3",
      "original": "git show :2:<파일경로>",
      "action": "유지",
      "final": "git show :2:<파일경로>",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.stageMap.1.4",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.stageMap.1.4",
      "original": "해결 파일의 바탕으로 유지",
      "action": "수정",
      "final": "해결 파일의 바탕으로 사용",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.stageMap.2.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.stageMap.2.1",
      "original": "지금 적용 중인 반대편 변경",
      "action": "수정",
      "final": "현재 적용하려는 반대편 변경",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.stageMap.2.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.stageMap.2.2",
      "original": "이번 cherry-pick에서는 BANK-OM-001 commit의 JSON",
      "action": "수정",
      "final": "이번 연습에서는 BANK-OM-001 commit의 JSON",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.stageMap.2.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.stageMap.2.3",
      "original": "git show :3:<파일경로>",
      "action": "유지",
      "final": "git show :3:<파일경로>",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.stageMap.2.4",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.stageMap.2.4",
      "original": "BANK-OM이 추가·수정·삭제한 항목 계산",
      "action": "수정",
      "final": "BANK-OM이 바꾼 JSON 항목을 계산",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|topic.conflicts.stageNote",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.stageNote",
      "original": "이번 연습에서는 공식 1.13.1 branch에서 BANK-OM commit을 cherry-pick했기 때문에 stage 2=공식, stage 3=BANK-OM입니다. 일반 merge에서도 stage 2는 항상 현재 checkout한 쪽(OURS), stage 3은 들어오는 쪽(THEIRS)이므로 branch 방향을 바꾸면 공식/BANK-OM 대응도 바뀔 수 있습니다.",
      "action": "수정",
      "final": "이번 연습은 공식 1.13.1 코드가 있는 작업 브랜치에 BANK-OM commit 하나를 적용했으므로 stage 2가 공식 코드이고 stage 3이 BANK-OM입니다. 일반 브랜치 병합에서도 stage 2는 현재 작업 브랜치, stage 3은 병합해 들어오는 브랜치입니다. 병합 방향을 바꾸면 공식 코드와 BANK-OM의 위치도 바뀔 수 있습니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "4|topic.conflicts.conditionMap.0.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.0.1",
      "original": "git diff --name-only --diff-filter=U로 아직 충돌 중인 파일 목록을 읽음",
      "action": "유지",
      "final": "git diff --name-only --diff-filter=U로 아직 충돌 중인 파일 목록을 읽음",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.conditionMap.0.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.0.2",
      "original": "모두 .json이면 다음 비교 진행",
      "action": "유지",
      "final": "모두 .json이면 다음 비교 진행",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.conditionMap.0.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.0.3",
      "original": "JSON 이외 파일이 하나라도 있으면 모든 JSON을 쓰기 전에 중단",
      "action": "유지",
      "final": "JSON 이외 파일이 하나라도 있으면 모든 JSON을 쓰기 전에 중단",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.conditionMap.1.0",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.1.0",
      "original": "현재 branch 변경 계산",
      "action": "수정",
      "final": "현재 작업 브랜치 변경 계산",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.conditionMap.1.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.1.1",
      "original": "stage 1(BASE)과 stage 2(OURS)의 최종 JSON 항목별 값을 비교",
      "action": "수정",
      "final": "BASE와 OURS의 JSON 항목별 값을 비교",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.conditionMap.1.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.1.2",
      "original": "값이 달라진 항목 경로를 OURS 변경 목록으로 만듦",
      "action": "수정",
      "final": "현재 작업 브랜치가 바꾼 항목 목록 생성",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.conditionMap.1.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.1.3",
      "original": "JSON 문법 오류 또는 최상위 값이 객체가 아니면 모든 JSON을 쓰기 전에 중단",
      "action": "수정",
      "final": "JSON 문법이 틀렸거나 최상위 값이 객체가 아니면 파일을 쓰기 전에 중단",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.conditionMap.2.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.2.1",
      "original": "stage 1(BASE)과 stage 3(THEIRS)의 최종 JSON 항목별 값을 비교",
      "action": "수정",
      "final": "BASE와 THEIRS의 JSON 항목별 값을 비교",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.conditionMap.2.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.2.2",
      "original": "추가·수정·삭제된 항목을 THEIRS 변경 목록으로 만듦",
      "action": "수정",
      "final": "들어오는 쪽이 추가·수정·삭제한 항목 목록 생성",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|topic.conflicts.conditionMap.2.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.2.3",
      "original": "JSON 문법 오류 또는 최상위 값이 객체가 아니면 모든 JSON을 쓰기 전에 중단",
      "action": "수정",
      "final": "JSON 문법이 틀렸거나 최상위 값이 객체가 아니면 파일을 쓰기 전에 중단",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.conditionMap.3.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.3.1",
      "original": "OURS 변경 항목 경로 ∩ THEIRS 변경 항목 경로",
      "action": "수정",
      "final": "양쪽 변경 목록에 같은 JSON 항목이 있는지 확인",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.conditionMap.3.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.3.2",
      "original": "교집합이 0개면 OURS에 THEIRS 변경을 반영",
      "action": "수정",
      "final": "겹치는 항목이 없으면 OURS에 THEIRS 변경 반영",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.conditionMap.3.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.3.3",
      "original": "한 항목이라도 겹치면 최종 값이 같아도 모든 JSON을 쓰기 전에 중단",
      "action": "수정",
      "final": "한 항목이라도 겹치면 최종 값이 같아도 파일을 쓰기 전에 중단",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.conditionMap.4.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.4.1",
      "original": "THEIRS 변경을 OURS 구조에 실제로 넣을 수 있는지 확인",
      "action": "수정",
      "final": "THEIRS 변경을 OURS JSON 구조에 넣을 수 있는지 확인",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.conditionMap.4.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.4.2",
      "original": "가능하면 파일을 쓰고 resolved ... leaf changes=N 출력",
      "action": "수정",
      "final": "가능하면 파일을 쓰고 적용한 항목 수 출력",
      "reason": "leaf를 ‘마지막 JSON 항목’으로 설명"
    },
    {
      "id": "4|topic.conflicts.conditionMap.4.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionMap.4.3",
      "original": "중간 객체 구조가 달라 반영할 수 없으면 오류. 앞에서 이미 쓴 파일이 있을 수 있으므로 git status와 diff를 확인",
      "action": "수정",
      "final": "중간 JSON 구조가 달라 넣을 수 없으면 중단. git status와 diff로 이미 쓴 파일이 있는지 확인",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.conditionNote",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.conditionNote",
      "original": "이번 BANK-OM-001 결과는 언어 JSON 18개 모두에서 겹치는 최종 항목이 0개였으므로 자동 작성 조건을 통과했습니다. 이 조건 통과는 JSON 병합 가능 여부만 뜻하며 기능 test PASS를 뜻하지 않습니다.",
      "action": "유지",
      "final": "이번 BANK-OM-001 결과는 언어 JSON 18개 모두에서 겹치는 최종 항목이 0개였으므로 자동 작성 조건을 통과했습니다. 이 조건 통과는 JSON 병합 가능 여부만 뜻하며 기능 test PASS를 뜻하지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.0.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.0.1",
      "original": "공식 JSON을 바탕으로 BANK-OM 항목 9개를 넣은 작업 파일을 작성했다는 뜻",
      "action": "수정",
      "final": "공식 JSON을 바탕으로 BANK-OM의 마지막 항목 9개를 넣은 작업 파일을 만들었다는 뜻",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.0.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.0.2",
      "original": "git diff로 9개 항목과 공식 항목 보존 여부를 확인하고 JSON·관련 기능 test 실행",
      "action": "유지",
      "final": "git diff로 9개 항목과 공식 항목 보존 여부를 확인하고 JSON·관련 기능 test 실행",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.0.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.0.3",
      "original": "확인 전에는 git add나 Git 작업 계속 실행 금지",
      "action": "유지",
      "final": "확인 전에는 git add나 Git 작업 계속 실행 금지",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.1.0",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.1.0",
      "original": "git status에 UU",
      "action": "유지",
      "final": "git status에 UU",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.1.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.1.1",
      "original": "도구가 파일 내용은 썼지만 Git에는 아직 충돌 미해결로 남아 있다는 뜻",
      "action": "유지",
      "final": "도구가 파일 내용은 썼지만 Git에는 아직 충돌 미해결로 남아 있다는 뜻",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.1.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.1.2",
      "original": "검토와 test를 통과한 파일만 git add",
      "action": "유지",
      "final": "검토와 test를 통과한 파일만 git add",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.1.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.1.3",
      "original": "UU를 도구 실패로 오해해 다시 실행하지 않음",
      "action": "유지",
      "final": "UU를 도구 실패로 오해해 다시 실행하지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.2.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.2.1",
      "original": "공식과 BANK-OM이 같은 최종 JSON 항목을 둘 다 변경했다는 뜻",
      "action": "수정",
      "final": "공식과 BANK-OM이 같은 JSON 항목을 둘 다 변경했다는 뜻",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.2.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.2.2",
      "original": "자동 선택을 중단하고 두 값과 업무 의도를 담당자·승인자가 직접 결정",
      "action": "유지",
      "final": "자동 선택을 중단하고 두 값과 업무 의도를 담당자·승인자가 직접 결정",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.2.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.2.3",
      "original": "결정 전 git add·continue 금지",
      "action": "유지",
      "final": "결정 전 git add·continue 금지",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.3.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.3.1",
      "original": "Java·TypeScript 등 이 보조 도구가 처리하지 않는 충돌이 함께 있다는 뜻",
      "action": "유지",
      "final": "Java·TypeScript 등 이 보조 도구가 처리하지 않는 충돌이 함께 있다는 뜻",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.3.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.3.2",
      "original": "해당 파일을 일반 Git 충돌 해결 절차로 직접 비교·수정",
      "action": "유지",
      "final": "해당 파일을 일반 Git 충돌 해결 절차로 직접 비교·수정",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.3.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.3.3",
      "original": "JSON 도구로 비JSON 코드를 자동 해결하려 하지 않음",
      "action": "유지",
      "final": "JSON 도구로 비JSON 코드를 자동 해결하려 하지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.4.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.4.1",
      "original": "JSON 형식은 합쳐졌지만 실제 기능 조건을 만족하지 못했다는 뜻",
      "action": "유지",
      "final": "JSON 형식은 합쳐졌지만 실제 기능 조건을 만족하지 못했다는 뜻",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.4.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.4.2",
      "original": "git add 전이면 파일을 다시 수정하고 test 재실행. 이미 add했다면 수정 후 다시 add",
      "action": "유지",
      "final": "git add 전이면 파일을 다시 수정하고 test 재실행. 이미 add했다면 수정 후 다시 add",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.outcomeMap.4.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeMap.4.3",
      "original": "test가 PASS할 때까지 cherry-pick/merge 완료 금지",
      "action": "유지",
      "final": "test가 PASS할 때까지 cherry-pick/merge 완료 금지",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.outcomeNote",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.outcomeNote",
      "original": "보조 도구의 완료 조건은 '해결 파일 초안 작성'까지입니다. 운영 담당자의 완료 조건은 diff 확인, JSON·관련 기능 test PASS, git add, 시작했던 Git 작업의 정상 완료, 해결 commit과 검사 결과 보관까지입니다.",
      "action": "수정",
      "final": "보조 도구는 해결 파일 초안까지만 만듭니다. 담당자는 diff 확인, JSON·관련 기능 test PASS, git add, 시작한 Git 작업 완료, 해결 commit과 검사 결과 보관까지 마쳐야 합니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "4|topic.conflicts.walkthrough.0.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.walkthrough.0.2",
      "original": "BANK-OM 변경을 적용하다 충돌한 JSON을 stage 1·2·3으로 보관",
      "action": "유지",
      "final": "BANK-OM 변경을 적용하다 충돌한 JSON을 stage 1·2·3으로 보관",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.walkthrough.0.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.walkthrough.0.3",
      "original": "git diff --name-only --diff-filter=U에 충돌 파일 표시",
      "action": "유지",
      "final": "git diff --name-only --diff-filter=U에 충돌 파일 표시",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.walkthrough.1.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.walkthrough.1.2",
      "original": "resolve_nonoverlapping_json_conflicts.py에 충돌 중인 저장소 경로 전달",
      "action": "수정",
      "final": "resolve_nonoverlapping_json_conflicts.py에 충돌 중인 제품 코드 저장소의 로컬 경로 전달",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.walkthrough.1.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.walkthrough.1.3",
      "original": "도구가 JSON 이외 충돌 여부와 동일 항목 겹침 여부를 먼저 검사",
      "action": "유지",
      "final": "도구가 JSON 이외 충돌 여부와 동일 항목 겹침 여부를 먼저 검사",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.walkthrough.2.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.walkthrough.2.2",
      "original": "공식 1.13.1 JSON을 기준으로 겹치지 않는 BANK-OM 항목만 적용",
      "action": "유지",
      "final": "공식 1.13.1 JSON을 기준으로 겹치지 않는 BANK-OM 항목만 적용",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.walkthrough.2.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.walkthrough.2.3",
      "original": "작업 폴더의 JSON 수정 + 터미널에 파일별 적용 항목 수 출력",
      "action": "유지",
      "final": "작업 폴더의 JSON 수정 + 터미널에 파일별 적용 항목 수 출력",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.walkthrough.3.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.walkthrough.3.2",
      "original": "git diff와 JSON·기능 test로 수정 결과 확인",
      "action": "유지",
      "final": "git diff와 JSON·기능 test로 수정 결과 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.walkthrough.3.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.walkthrough.3.3",
      "original": "공식 항목 유지와 BANK-OM 항목 추가를 모두 확인",
      "action": "유지",
      "final": "공식 항목 유지와 BANK-OM 항목 추가를 모두 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.walkthrough.4.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.walkthrough.4.2",
      "original": "확인한 파일만 git add 후 시작한 Git 작업을 계속",
      "action": "유지",
      "final": "확인한 파일만 git add 후 시작한 Git 작업을 계속",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.walkthrough.4.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.walkthrough.4.3",
      "original": "재적용 연습이면 cherry-pick --continue, branch merge면 merge --continue 또는 해결 commit",
      "action": "수정",
      "final": "재적용 연습이면 cherry-pick --continue, custom 브랜치 병합이면 merge --continue 또는 해결 commit",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.comparison.title",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.comparison.title",
      "original": "BANK-OM-001 ko-kr.json 실제 실행 전후",
      "action": "유지",
      "final": "BANK-OM-001 ko-kr.json 실제 실행 전후",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.comparison.beforeTitle",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.comparison.beforeTitle",
      "original": "실행 전: Git이 선택하지 못해 남긴 충돌",
      "action": "유지",
      "final": "실행 전: Git이 선택하지 못해 남긴 충돌",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.comparison.afterTitle",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.comparison.afterTitle",
      "original": "실행 후: 공식 JSON에 BANK-OM 항목을 추가",
      "action": "유지",
      "final": "실행 후: 공식 JSON에 BANK-OM 항목을 추가",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.comparison.note",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.comparison.note",
      "original": "이 비교는 같은 한 줄을 서로 다른 값으로 바꾼 충돌이 아닙니다. 두 버전이 같은 큰 JSON 객체 구간을 각각 편집했기 때문에 Git은 자동 병합을 멈췄습니다. 보조 도구는 줄 위치가 아니라 JSON 항목 경로를 비교했고, 동일 항목 겹침이 0개여서 두 변경을 함께 보존했습니다.",
      "action": "수정",
      "final": "이 충돌은 같은 한 줄을 서로 다른 값으로 바꾼 경우가 아닙니다. 공식 코드와 BANK-OM이 같은 큰 JSON 객체 안의 서로 다른 위치를 편집해 Git이 자동 병합을 멈춘 경우입니다. 보조 도구는 JSON 항목 이름을 비교했고 같은 항목을 함께 바꾼 경우가 없어 두 변경을 모두 보존했습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|topic.conflicts.update",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.update",
      "original": "충돌 해결로 Manifest에 없던 파일을 새로 수정했다면 changed_paths와 필요한 watch를 갱신하고, 동작 조건이 바뀌면 Contract를 갱신합니다.",
      "action": "유지",
      "final": "충돌 해결로 Manifest에 없던 파일을 새로 수정했다면 changed_paths와 필요한 watch를 갱신하고, 동작 조건이 바뀌면 Contract를 갱신합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|topic.conflicts.caution",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.caution",
      "original": "이 도구는 이번 OM_TEMP commit별 재적용 연습을 위해 만든 제한 도구이며 행내 표준 승인 절차로 확정되지 않았습니다. 성공해도 기능 정상은 확정되지 않으므로 JSON 문법, Manifest 범위, Contract test와 전체 build를 다시 실행합니다.",
      "action": "유지",
      "final": "이 도구는 이번 OM_TEMP commit별 재적용 연습을 위해 만든 제한 도구이며 행내 표준 승인 절차로 확정되지 않았습니다. 성공해도 기능 정상은 확정되지 않으므로 JSON 문법, Manifest 범위, Contract test와 전체 build를 다시 실행합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|topic.conflicts.operationCases.0.0",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.operationCases.0.0",
      "original": "Git 충돌이 없거나 충돌 파일에 JSON 이외 파일이 포함됨",
      "action": "유지",
      "final": "Git 충돌이 없거나 충돌 파일에 JSON 이외 파일이 포함됨",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.operationCases.0.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.operationCases.0.1",
      "original": "보조 도구를 사용하지 않음",
      "action": "유지",
      "final": "보조 도구를 사용하지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.operationCases.0.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.operationCases.0.2",
      "original": "충돌이 없으면 그대로 진행. 비JSON 충돌은 사람이 일반 Git 절차로 해결",
      "action": "유지",
      "final": "충돌이 없으면 그대로 진행. 비JSON 충돌은 사람이 일반 Git 절차로 해결",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.operationCases.0.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.operationCases.0.3",
      "original": "병합 후 소스·기능 검사",
      "action": "유지",
      "final": "병합 후 소스·기능 검사",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.operationCases.1.0",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.operationCases.1.0",
      "original": "JSON 충돌이고 OURS/THEIRS 변경 항목이 겹치지 않음",
      "action": "유지",
      "final": "JSON 충돌이고 OURS/THEIRS 변경 항목이 겹치지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.operationCases.1.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.operationCases.1.1",
      "original": "보조 도구로 해결 파일 초안 작성",
      "action": "유지",
      "final": "보조 도구로 해결 파일 초안 작성",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.operationCases.1.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.operationCases.1.2",
      "original": "resolved 출력 후 diff와 test 확인. 기존 등록 경로만 남으면 Manifest 경로는 그대로 유지",
      "action": "유지",
      "final": "resolved 출력 후 diff와 test 확인. 기존 등록 경로만 남으면 Manifest 경로는 그대로 유지",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|topic.conflicts.operationCases.1.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.operationCases.1.3",
      "original": "확인한 파일만 git add 후 Git 작업 계속",
      "action": "유지",
      "final": "확인한 파일만 git add 후 Git 작업 계속",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.operationCases.2.0",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.operationCases.2.0",
      "original": "같은 JSON 항목이 겹치거나 해결로 새 경로·동작이 생김",
      "action": "유지",
      "final": "같은 JSON 항목이 겹치거나 해결로 새 경로·동작이 생김",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.operationCases.2.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.operationCases.2.1",
      "original": "자동 진행 중단 및 등록 재판단",
      "action": "유지",
      "final": "자동 진행 중단 및 등록 재판단",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|topic.conflicts.operationCases.2.2",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.operationCases.2.2",
      "original": "값은 담당자·승인자가 결정. 새 경로는 changed_paths, 간접 영향은 watch, 동작 변경은 Contract 갱신",
      "action": "유지",
      "final": "값은 담당자·승인자가 결정. 새 경로는 changed_paths, 간접 영향은 watch, 동작 변경은 Contract 갱신",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|topic.conflicts.operationCases.2.3",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.operationCases.2.3",
      "original": "승인 기록 후 관련 등록·소스·기능 검사 전체 재실행",
      "action": "유지",
      "final": "승인 기록 후 관련 등록·소스·기능 검사 전체 재실행",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.purpose",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.purpose",
      "original": "하나의 BANK-OM 기능이 현재 OpenMetadata 버전에서 변경하는 전체 파일, 그중 반드시 유지할 핵심 파일, 공식 업그레이드 때 다시 볼 경로와 기능 test 연결을 기록합니다.",
      "action": "유지",
      "final": "하나의 BANK-OM 기능이 현재 OpenMetadata 버전에서 변경하는 전체 파일, 그중 반드시 유지할 핵심 파일, 공식 업그레이드 때 다시 볼 경로와 기능 test 연결을 기록합니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "3|file.manifest.created",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.created",
      "original": "새 BANK-OM ID를 최초 등록할 때 기능별로 한 파일을 만듭니다.",
      "action": "유지",
      "final": "새 BANK-OM ID를 최초 등록할 때 기능별로 한 파일을 만듭니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "3|file.manifest.update",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.update",
      "original": "같은 ID의 후속 commit에서 새 파일이 추가되면 changed_paths에 포함하고, 필수 파일·watch 의존·Contract·적용 순서가 바뀔 때 함께 갱신합니다. 기존 등록 파일의 내용만 다시 수정했다면 changed_paths의 파일명 목록은 바뀌지 않습니다.",
      "action": "유지",
      "final": "같은 ID의 후속 commit에서 새 파일이 추가되면 changed_paths에 포함하고, 필수 파일·watch 의존·Contract·적용 순서가 바뀔 때 함께 갱신합니다. 기존 등록 파일의 내용만 다시 수정했다면 changed_paths의 파일명 목록은 바뀌지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.manifest.owner",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.owner",
      "original": "plan이 Git에서 changed_paths와 실제 변경 경로 watch를 계산합니다. 기능 담당자는 required·간접 watch·Contract를 결정하고, 실제 승인자가 proposal digest에 연결된 승인서에 판단 사유를 남깁니다.",
      "action": "수정",
      "final": "plan 명령은 Git에서 전체 변경 파일과 공식 업그레이드 때 다시 볼 직접 변경 경로를 계산합니다. 기능 담당자는 필수 파일, 직접 변경하지 않았지만 함께 확인할 경로, Contract를 결정합니다. 승인자는 제안 내용 확인값(proposal digest)이 적힌 승인서에 판단 사유를 남깁니다. 이 값으로 승인 뒤 제안이 바뀌지 않았는지 확인합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|file.manifest.readers",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.readers",
      "original": "변경 생존 확인, 적용 순서 확인, 등록 범위 확인, 공식 업그레이드 영향 확인, 필수 test 연결·실행 확인에 사용됩니다.",
      "action": "유지",
      "final": "변경 생존 확인, 적용 순서 확인, 등록 범위 확인, 공식 업그레이드 영향 확인, 필수 test 연결·실행 확인에 사용됩니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|file.manifest.fields.0.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.fields.0.2",
      "original": "코드 commit과 관리자료를 연결하는 BANK-OM ID",
      "action": "유지",
      "final": "코드 commit과 관리자료를 연결하는 BANK-OM ID",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.fields.1.4",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.fields.1.4",
      "original": "Tibero 연결 유형",
      "action": "유지",
      "final": "Tibero 연결 유형",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.fields.2.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.fields.2.2",
      "original": "현재 검사할 기능은 active, 폐기 절차를 마친 기능은 retired",
      "action": "유지",
      "final": "현재 검사할 기능은 active, 폐기 절차를 마친 기능은 retired",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.fields.3.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.fields.3.2",
      "original": "공식 Core 수정 여부와 변경 유형",
      "action": "유지",
      "final": "공식 Core 수정 여부와 변경 유형",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.fields.4.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.fields.4.2",
      "original": "현재 버전에서 이 ID가 붙은 모든 commit이 변경한 전체 파일. 목록 밖 파일을 같은 ID로 변경하면 등록 범위 검사가 BLOCK",
      "action": "유지",
      "final": "현재 버전에서 이 ID가 붙은 모든 commit이 변경한 전체 파일. 목록 밖 파일을 같은 ID로 변경하면 등록 범위 검사가 BLOCK",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.manifest.fields.4.3",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.fields.4.3",
      "original": "Git 자동 추출 후 확인",
      "action": "유지",
      "final": "Git 자동 추출 후 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.fields.5.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.fields.5.2",
      "original": "현재 변경 범위 중 누락되면 기능 미적용으로 즉시 BLOCK할 핵심 파일",
      "action": "유지",
      "final": "현재 변경 범위 중 누락되면 기능 미적용으로 즉시 BLOCK할 핵심 파일",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.fields.6.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.fields.6.2",
      "original": "공식 버전 변경 시 다시 비교할 관련 경로",
      "action": "유지",
      "final": "공식 버전 변경 시 다시 비교할 관련 경로",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.fields.6.3",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.fields.6.3",
      "original": "실제 변경 자동 포함 + 담당자 의존 추가",
      "action": "수정",
      "final": "준비도구가 changed_paths 중 공식 OpenMetadata 포크 브랜치에도 존재하는 경로만 자동 제안하고, 행내 전용 경로·간접 의존 경로는 담당자가 추가 여부를 결정",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.manifest.fields.7.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.fields.7.2",
      "original": "업무 정상 조건과 필수 test를 연결하는 Contract ID",
      "action": "유지",
      "final": "업무 정상 조건과 필수 test를 연결하는 Contract ID",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.fields.8.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.fields.8.2",
      "original": "Contract에서 파생되지 않은 별도 기술 test",
      "action": "수정",
      "final": "Contract에 연결하지 않고 이 기능에 직접 지정한 기술 test",
      "reason": "‘파생’ 대신 자동으로 생성되는 파일을 직접 설명"
    },
    {
      "id": "3|file.manifest.fields.9.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.fields.9.2",
      "original": "같은 ID의 후속 commit을 허용하는지",
      "action": "유지",
      "final": "같은 ID의 후속 commit을 허용하는지",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.fields.10.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.fields.10.2",
      "original": "먼저 적용돼야 하는 BANK-OM ID",
      "action": "유지",
      "final": "먼저 적용돼야 하는 BANK-OM ID",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.updateReason",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.updateReason",
      "original": "BANK-OM-007 후속 commit이 기존 목록에 없던 파일 두 개를 변경했으므로, 현재 1.13.0 버전의 changed_paths를 8개에서 10개로 갱신합니다. 어떤 파일이 후속 commit에서 추가됐는지는 Git 이력이 보존합니다. 새 파일이 기능의 필수 구성요소라면 required_changed_paths에도 같은 경로를 별도로 추가합니다.",
      "action": "유지",
      "final": "BANK-OM-007 후속 commit이 기존 목록에 없던 파일 두 개를 변경했으므로, 현재 1.13.0 버전의 changed_paths를 8개에서 10개로 갱신합니다. 어떤 파일이 후속 commit에서 추가됐는지는 Git 이력이 보존합니다. 새 파일이 기능의 필수 구성요소라면 required_changed_paths에도 같은 경로를 별도로 추가합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.manifest.scopeFlow.0.0",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.scopeFlow.0.0",
      "original": "BANK-OM-007 최초 commit",
      "action": "유지",
      "final": "BANK-OM-007 최초 commit",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.scopeFlow.1.0",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.scopeFlow.1.0",
      "original": "BANK-OM-007 후속 commit",
      "action": "유지",
      "final": "BANK-OM-007 후속 commit",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.scopeFlow.2.0",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.scopeFlow.2.0",
      "original": "현재 1.13.0 검사 범위",
      "action": "유지",
      "final": "현재 1.13.0 검사 범위",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.scopeFlow.2.1",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.scopeFlow.2.1",
      "original": "changed_paths 10개",
      "action": "유지",
      "final": "changed_paths 10개",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.scopeOutcome",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.scopeOutcome",
      "original": "T40은 changed_paths 밖의 변경을 BLOCK하고, T93은 changed_paths와 실제 ID별 Git 변경 이력이 같은지 확인합니다. T26은 changed_paths의 일반 파일이 사라지거나 공식 원본과 같아지면 APPROVAL을 요구합니다. required_changed_paths에도 등록한 파일은 같은 상황에서 BLOCK합니다. T42는 changed_paths가 아니라 upgrade_watch.paths를 읽으므로, 새 경로가 공식 업그레이드 영향 감시에도 필요한지 별도로 확인합니다.",
      "action": "유지",
      "final": "T40은 changed_paths 밖의 변경을 BLOCK하고, T93은 changed_paths와 실제 ID별 Git 변경 이력이 같은지 확인합니다. T26은 changed_paths의 일반 파일이 사라지거나 공식 원본과 같아지면 APPROVAL을 요구합니다. required_changed_paths에도 등록한 파일은 같은 상황에서 BLOCK합니다. T42는 changed_paths가 아니라 upgrade_watch.paths를 읽으므로, 새 경로가 공식 업그레이드 영향 감시에도 필요한지 별도로 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.manifest.scopeExamples.0.0",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.scopeExamples.0.0",
      "original": "BANK-OM-007의 현재 10개 파일",
      "action": "유지",
      "final": "BANK-OM-007의 현재 10개 파일",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.scopeExamples.0.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.scopeExamples.0.2",
      "original": "모두 현재 검사 범위에 포함",
      "action": "유지",
      "final": "모두 현재 검사 범위에 포함",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.scopeExamples.1.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.scopeExamples.1.2",
      "original": "사라지면 T26 APPROVAL, 공식 버전에서도 바뀌면 T42 APPROVAL",
      "action": "유지",
      "final": "사라지면 T26 APPROVAL, 공식 버전에서도 바뀌면 T42 APPROVAL",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.scopeExamples.2.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.scopeExamples.2.2",
      "original": "등록 밖 변경인지 검사하고, 사라지면 T26 APPROVAL",
      "action": "유지",
      "final": "등록 밖 변경인지 검사하고, 사라지면 T26 APPROVAL",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.scopeExamples.3.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.scopeExamples.3.2",
      "original": "사라지거나 공식 원본과 같으면 T26 BLOCK",
      "action": "유지",
      "final": "사라지거나 공식 원본과 같으면 T26 BLOCK",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.scopeExamples.4.0",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.scopeExamples.4.0",
      "original": "Manifest 어느 목록에도 없는 새 파일",
      "action": "유지",
      "final": "Manifest 어느 목록에도 없는 새 파일",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.scopeExamples.4.2",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.scopeExamples.4.2",
      "original": "같은 ID의 commit이 변경하면 T40 BLOCK",
      "action": "유지",
      "final": "같은 ID의 commit이 변경하면 T40 BLOCK",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.commands.0.label",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.commands.0.label",
      "original": "변경안 생성 · 실제 등록자료는 바뀌지 않음",
      "action": "유지",
      "final": "변경안 생성 · 실제 등록자료는 바뀌지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.commands.0.meaning",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.commands.0.meaning",
      "original": "Git commit 이력에서 BANK-OM ID별 SHA와 changed_paths를 계산하고 기존 사람 정책과 비교합니다. 제안·질문·diff를 등록 폴더 밖에 만들며, 승인 전에는 실제 Manifest를 수정하지 않습니다.",
      "action": "유지",
      "final": "Git commit 이력에서 BANK-OM ID별 SHA와 changed_paths를 계산하고 기존 사람 정책과 비교합니다. 제안·질문·diff를 등록 폴더 밖에 만들며, 승인 전에는 실제 Manifest를 수정하지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.manifest.commands.1.label",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.commands.1.label",
      "original": "승인안 적용 · Manifest와 파생 목록이 바뀜",
      "action": "수정",
      "final": "승인안 적용 · Manifest와 자동 생성 목록이 바뀜",
      "reason": "‘파생’ 대신 자동으로 생성되는 파일을 직접 설명"
    },
    {
      "id": "3|file.manifest.commands.1.meaning",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.commands.1.meaning",
      "original": "승인서가 같은 proposal digest의 모든 사람 질문에 답했고 Git SHA와 등록 입력도 그대로일 때만 Manifest·Registry·commit inventory·전체 변경 목록을 반영합니다. Contract는 자동으로 바꾸지 않습니다.",
      "action": "수정",
      "final": "승인서가 같은 변경안을 가리키고 모든 검토 질문에 답했으며 Git과 등록 입력도 그대로일 때만 Manifest·Registry·commit inventory·전체 변경 목록을 반영합니다. Contract는 자동으로 바꾸지 않습니다.",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "3|file.manifest.commands.2.label",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.commands.2.label",
      "original": "등록자료 검증 · Manifest는 바뀌지 않음",
      "action": "유지",
      "final": "등록자료 검증 · Manifest는 바뀌지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.manifest.commands.2.meaning",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.commands.2.meaning",
      "original": "수정한 Manifest가 Registry·Contract·전체 변경 파일 목록·과거 코드 파일–BANK-OM 연결표·필수 test 연결과 맞는지 읽어서 검사합니다. Manifest를 직접 수정한 뒤에는 이 검증을 실행합니다.",
      "action": "수정",
      "final": "수정한 Manifest가 Registry·Contract·전체 변경 파일 목록·Registry source.snapshot_sha의 파일–BANK-OM 연결표·필수 test 연결과 맞는지 읽어서 검사합니다. Manifest를 직접 수정한 뒤에는 이 검증을 실행합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|file.manifest.storage",
      "chapter": "3",
      "page": "상세 · Manifest",
      "location": "file.manifest.storage",
      "original": "버전별 등록 폴더에서 Git 이력으로 관리합니다. 새 공식 버전에서도 같은 업무 기능이면 같은 BANK-OM ID를 유지하되 새 버전 폴더의 changed_paths를 다시 생성·검토합니다. 최초 구현과 후속 수정의 구분은 Manifest 목록을 나누지 않고 Git commit SHA와 커밋 순서로 확인합니다. 새 plan 명령은 --output을 필수로 요구하고 등록 폴더 내부 출력을 차단합니다.",
      "action": "유지",
      "final": "버전별 등록 폴더에서 Git 이력으로 관리합니다. 새 공식 버전에서도 같은 업무 기능이면 같은 BANK-OM ID를 유지하되 새 버전 폴더의 changed_paths를 다시 생성·검토합니다. 최초 구현과 후속 수정의 구분은 Manifest 목록을 나누지 않고 Git commit SHA와 커밋 순서로 확인합니다. 새 plan 명령은 --output을 필수로 요구하고 등록 폴더 내부 출력을 차단합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.registry.purpose",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.purpose",
      "original": "검사할 BANK-OM 전체 목록, 담당자, 상태, 중요도와 Manifest·Contract 연결을 한곳에서 관리합니다.",
      "action": "유지",
      "final": "검사할 BANK-OM 전체 목록, 담당자, 상태, 중요도와 Manifest·Contract 연결을 한곳에서 관리합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.registry.created",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.created",
      "original": "한 버전의 등록 묶음을 처음 만들 때 생성합니다.",
      "action": "유지",
      "final": "한 버전의 등록 묶음을 처음 만들 때 생성합니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "3|file.registry.update",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.update",
      "original": "ID 추가·폐기, 담당자·배정 상태, 중요도, Manifest 또는 Contract 연결이 바뀔 때 갱신합니다.",
      "action": "유지",
      "final": "ID 추가·폐기, 담당자·배정 상태, 중요도, Manifest 또는 Contract 연결이 바뀔 때 갱신합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.registry.owner",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.owner",
      "original": "plan이 새 ID의 Manifest·Contract 연결과 Git에서 확인한 source 값을 제안합니다. 담당자·중요도·상태는 관리 책임자가 new-ID 입력과 승인서에서 확정합니다.",
      "action": "수정",
      "final": "plan은 새 ID의 Manifest·Contract 연결과 Git에서 확인한 코드 기준값을 제안합니다. 담당자·중요도·상태는 관리 책임자가 새 ID 입력 파일과 승인서에서 확정합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|file.registry.readers",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.readers",
      "original": "활성 기능 목록 확인, 담당자 배정 확인, 적용 순서 확인, 필수 test 연결 확인과 등록자료 완전성 검사에 사용됩니다.",
      "action": "유지",
      "final": "활성 기능 목록 확인, 담당자 배정 확인, 적용 순서 확인, 필수 test 연결 확인과 등록자료 완전성 검사에 사용됩니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|file.registry.fields.0.2",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.fields.0.2",
      "original": "분석한 OpenMetadata 코드 저장소",
      "action": "수정",
      "final": "분석한 제품 코드 저장소",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.registry.fields.1.2",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.fields.1.2",
      "original": "최초 등록자료가 설명하는 행내 코드 상태",
      "action": "수정",
      "final": "해당 제품 버전의 등록 revision을 처음 만든 시점에 BANK-OM 변경이 적용돼 있던 코드 commit",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.registry.fields.2.2",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.fields.2.2",
      "original": "비교 기준 공식 OpenMetadata 상태",
      "action": "유지",
      "final": "비교 기준 공식 OpenMetadata 상태",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.registry.fields.3.2",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.fields.3.2",
      "original": "Manifest와 같은 BANK-OM ID",
      "action": "유지",
      "final": "Manifest와 같은 BANK-OM ID",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.registry.fields.3.3",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.fields.3.3",
      "original": "Manifest에서 생성",
      "action": "유지",
      "final": "Manifest에서 생성",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.registry.fields.4.2",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.fields.4.2",
      "original": "기능과 결과를 책임지는 조직·담당자",
      "action": "유지",
      "final": "기능과 결과를 책임지는 조직·담당자",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.registry.fields.5.2",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.fields.5.2",
      "original": "담당 확정은 assigned, 미정은 pending",
      "action": "유지",
      "final": "담당 확정은 assigned, 미정은 pending",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.registry.fields.6.2",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.fields.6.2",
      "original": "검사 대상은 active, 폐기 완료는 retired",
      "action": "유지",
      "final": "검사 대상은 active, 폐기 완료는 retired",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.registry.fields.7.2",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.fields.7.2",
      "original": "low·medium·high·critical 중 업무 영향 등급",
      "action": "유지",
      "final": "low·medium·high·critical 중 업무 영향 등급",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.registry.fields.8.2",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.fields.8.2",
      "original": "해당 Manifest 경로",
      "action": "유지",
      "final": "해당 Manifest 경로",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.registry.fields.9.2",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.fields.9.2",
      "original": "연결된 Contract ID",
      "action": "유지",
      "final": "연결된 Contract ID",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.registry.fields.9.3",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.fields.9.3",
      "original": "Manifest·Contract에서 생성",
      "action": "유지",
      "final": "Manifest·Contract에서 생성",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.registry.fields.10.2",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.fields.10.2",
      "original": "최초 snapshot에 있던 기능인지 이후 추가 기능인지 구분",
      "action": "수정",
      "final": "Registry source.snapshot_sha의 custom commit에 이미 있던 기능인지 그 commit 이후에 추가한 기능인지 구분",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.registry.updateReason",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.updateReason",
      "original": "실제 책임 조직이 정해졌으므로 owner와 owner_status만 승인해 변경합니다. commit SHA나 Manifest 경로는 관련 코드·파일이 바뀌지 않았다면 수정하지 않습니다.",
      "action": "수정",
      "final": "실제 책임 조직이 정해졌으므로 owner와 owner_status만 승인해 변경합니다. source.snapshot_sha는 같은 버전의 일반 후속 commit이 생겼다는 이유만으로 최신 commit으로 바꾸지 않습니다. 같은 제품 버전의 등록 revision을 새로 만들 때 기존 값을 덮어쓸지 새 revision으로 보관할지는 조직 정책을 먼저 정해야 합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|file.registry.commands.0.label",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.commands.0.label",
      "original": "Registry 변경안 생성 · 실제 파일은 바뀌지 않음",
      "action": "유지",
      "final": "Registry 변경안 생성 · 실제 파일은 바뀌지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.registry.commands.0.meaning",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.commands.0.meaning",
      "original": "새 BANK-OM ID라면 사람이 작성한 new-ID 입력과 contracts.yaml의 역방향 연결을 함께 읽어 Registry 변경안을 만듭니다. 기존 ID 후속 commit만 있다면 새 entry를 만들지 않습니다.",
      "action": "수정",
      "final": "새 BANK-OM ID라면 사람이 작성한 새 ID 입력과 contracts.yaml에 적힌 같은 BANK-OM ID를 함께 확인해 Registry 변경안을 만듭니다. 기존 ID의 후속 commit만 있다면 Registry에 새 항목을 만들지 않습니다.",
      "reason": "‘양방향·역방향’ 대신 서로 확인하는 두 항목을 직접 명시"
    },
    {
      "id": "3|file.registry.commands.1.label",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.commands.1.label",
      "original": "승인·apply 뒤 연결 검증 · Registry는 바뀌지 않음",
      "action": "유지",
      "final": "승인·apply 뒤 연결 검증 · Registry는 바뀌지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.registry.commands.1.meaning",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.commands.1.meaning",
      "original": "Registry entry가 Manifest와 Contract를 정확히 가리키고 owner·상태·중요도 형식을 지키는지 읽어서 검사합니다. 검증 명령은 파일을 수정하지 않습니다.",
      "action": "유지",
      "final": "Registry entry가 Manifest와 Contract를 정확히 가리키고 owner·상태·중요도 형식을 지키는지 읽어서 검사합니다. 검증 명령은 파일을 수정하지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.registry.storage",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.storage",
      "original": "버전별 등록 폴더에서 Git으로 관리합니다. plan의 diff.patch에서 사람 입력인 owner·criticality가 승인 내용과 같은지 확인하고, apply 결과의 written_files에 customization-registry.yaml이 있을 때만 실제 Registry가 바뀐 것으로 판단합니다.",
      "action": "유지",
      "final": "버전별 등록 폴더에서 Git으로 관리합니다. plan의 diff.patch에서 사람 입력인 owner·criticality가 승인 내용과 같은지 확인하고, apply 결과의 written_files에 customization-registry.yaml이 있을 때만 실제 Registry가 바뀐 것으로 판단합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.contracts.purpose",
      "chapter": "3",
      "page": "상세 · Contract catalog",
      "location": "file.contracts.purpose",
      "original": "파일 존재만으로 확인할 수 없는 업무 정상 조건과 그 조건을 확인할 필수 test를 연결합니다.",
      "action": "유지",
      "final": "파일 존재만으로 확인할 수 없는 업무 정상 조건과 그 조건을 확인할 필수 test를 연결합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|file.contracts.created",
      "chapter": "3",
      "page": "상세 · Contract catalog",
      "location": "file.contracts.created",
      "original": "BANK-OM 기능을 최초 등록할 때 기능 책임자가 정상 조건을 정하고 만듭니다.",
      "action": "유지",
      "final": "BANK-OM 기능을 최초 등록할 때 기능 책임자가 정상 조건을 정하고 만듭니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "3|file.contracts.update",
      "chapter": "3",
      "page": "상세 · Contract catalog",
      "location": "file.contracts.update",
      "original": "업무 정상 조건, test 파일·함수 이름, 보호할 BANK-OM ID가 바뀔 때 갱신합니다. test 실행마다 수정하지 않습니다.",
      "action": "유지",
      "final": "업무 정상 조건, test 파일·함수 이름, 보호할 BANK-OM ID가 바뀔 때 갱신합니다. test 실행마다 수정하지 않습니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "3|file.contracts.owner",
      "chapter": "3",
      "page": "상세 · Contract catalog",
      "location": "file.contracts.owner",
      "original": "업무 정상 조건은 기능 책임자가 정하고, test 선택자는 개발자와 test 담당자가 확인합니다. prepare_registration.py는 Contract를 읽어 연결을 검사하지만 내용을 자동 작성하거나 apply하지 않습니다.",
      "action": "유지",
      "final": "업무 정상 조건은 기능 책임자가 정하고, test 선택자는 개발자와 test 담당자가 확인합니다. prepare_registration.py는 Contract를 읽어 연결을 검사하지만 내용을 자동 작성하거나 apply하지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.contracts.readers",
      "chapter": "3",
      "page": "상세 · Contract catalog",
      "location": "file.contracts.readers",
      "original": "필수 test 파일·이름 확인, 실제 test 실행, 재시도 판정과 변경 생존 확인에 사용됩니다.",
      "action": "유지",
      "final": "필수 test 파일·이름 확인, 실제 test 실행, 재시도 판정과 변경 생존 확인에 사용됩니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|file.contracts.fields.0.2",
      "chapter": "3",
      "page": "상세 · Contract catalog",
      "location": "file.contracts.fields.0.2",
      "original": "CONTRACT-... 형식의 고유 ID",
      "action": "유지",
      "final": "CONTRACT-... 형식의 고유 ID",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.contracts.fields.1.2",
      "chapter": "3",
      "page": "상세 · Contract catalog",
      "location": "file.contracts.fields.1.2",
      "original": "사람이 읽는 Contract 이름",
      "action": "유지",
      "final": "사람이 읽는 Contract 이름",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.contracts.fields.2.2",
      "chapter": "3",
      "page": "상세 · Contract catalog",
      "location": "file.contracts.fields.2.2",
      "original": "버전이 바뀌어도 유지돼야 하는 업무 동작",
      "action": "유지",
      "final": "버전이 바뀌어도 유지돼야 하는 업무 동작",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.contracts.fields.2.4",
      "chapter": "3",
      "page": "상세 · Contract catalog",
      "location": "file.contracts.fields.2.4",
      "original": "한글 자모가 중복·역전·소실되지 않는다",
      "action": "유지",
      "final": "한글 자모가 중복·역전·소실되지 않는다",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.contracts.fields.3.2",
      "chapter": "3",
      "page": "상세 · Contract catalog",
      "location": "file.contracts.fields.3.2",
      "original": "정상 조건을 확인할 pytest 파일과 함수",
      "action": "유지",
      "final": "정상 조건을 확인할 pytest 파일과 함수",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.contracts.fields.4.2",
      "chapter": "3",
      "page": "상세 · Contract catalog",
      "location": "file.contracts.fields.4.2",
      "original": "이 Contract가 보호하는 BANK-OM ID",
      "action": "유지",
      "final": "이 Contract가 보호하는 BANK-OM ID",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.contracts.updateReason",
      "chapter": "3",
      "page": "상세 · Contract catalog",
      "location": "file.contracts.updateReason",
      "original": "기존 입력뿐 아니라 붙여넣기 동작도 공식 정상 조건에 포함하기로 승인했으므로 invariant와 필수 test를 함께 갱신합니다.",
      "action": "유지",
      "final": "기존 입력뿐 아니라 붙여넣기 동작도 공식 정상 조건에 포함하기로 승인했으므로 invariant와 필수 test를 함께 갱신합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|file.contracts.storage",
      "chapter": "3",
      "page": "상세 · Contract catalog",
      "location": "file.contracts.storage",
      "original": "버전별 등록 폴더에서 Git으로 관리합니다. 과거 실행 결과의 Contract를 바꾸지 않고, 변경 commit 이후 새 suite_version으로 다시 test합니다.",
      "action": "유지",
      "final": "버전별 등록 폴더에서 Git으로 관리합니다. 과거 실행 결과의 Contract를 바꾸지 않고, 변경 commit 이후 새 suite_version으로 다시 test합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.shared_paths.title",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 여러 BANK-OM ID가 함께 바꾼 파일 연결표",
      "location": "file.shared_paths.title",
      "original": "과거 코드 공용 파일–BANK-OM 연결표",
      "action": "수정",
      "final": "Registry source.snapshot_sha의 custom commit에서 여러 BANK-OM ID가 함께 바꾼 파일 연결표",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.shared_paths.purpose",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 여러 BANK-OM ID가 함께 바꾼 파일 연결표",
      "location": "file.shared_paths.purpose",
      "original": "최초 등록에 사용한 과거 source snapshot에서 두 개 이상의 BANK-OM이 함께 변경한 파일만 모아 기록합니다. 사람이나 조직의 파일 소유권을 뜻하지 않으며, 현재 버전 Manifest의 전체 공용 파일 목록도 아닙니다. 실제 파일명에는 owners가 남아 있지만 이 위키에서는 의미에 맞춰 연결표라고 부릅니다.",
      "action": "수정",
      "final": "해당 제품 버전의 등록자료를 만들 때 Registry의 source.snapshot_sha에 기록한 custom branch commit에서 두 개 이상의 BANK-OM ID가 함께 변경한 파일만 기록합니다. 사람이나 조직의 파일 소유권을 뜻하지 않으며, 최신 커스텀 브랜치의 공용 파일 목록도 아닙니다. 파일명에 owners가 포함되지만, 값은 사람이나 조직이 아니라 해당 파일을 변경한 BANK-OM ID 목록입니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.shared_paths.created",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 여러 BANK-OM ID가 함께 바꾼 파일 연결표",
      "location": "file.shared_paths.created",
      "original": "최초 source snapshot 등록 묶음을 만들 때 source-snapshot-path-owners.yaml에서 연결된 BANK-OM ID가 두 개 이상인 경로만 자동 추출합니다.",
      "action": "수정",
      "final": "제품 버전별 등록 묶음을 처음 만들 때 source-snapshot-path-owners.yaml에서 BANK-OM ID가 두 개 이상 연결된 경로만 자동 추출합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.shared_paths.update",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 여러 BANK-OM ID가 함께 바꾼 파일 연결표",
      "location": "file.shared_paths.update",
      "original": "기준 source snapshot SHA나 과거 commit 분류를 바로잡을 때만 재생성합니다. 같은 ID의 일반 후속 commit이나 현재 Manifest 변경 때문에 갱신하지 않습니다.",
      "action": "수정",
      "final": "Registry의 source.snapshot_sha로 기록한 custom branch commit을 다른 commit으로 바꾸거나, 그 commit까지의 BANK-OM 분류 오류를 바로잡을 때만 다시 만듭니다. 같은 제품 버전의 일반 후속 commit이나 최신 Manifest 변경 때문에 갱신하지 않습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.shared_paths.owner",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 여러 BANK-OM ID가 함께 바꾼 파일 연결표",
      "location": "file.shared_paths.owner",
      "original": "과거 Git 이력과 버전별 초기 등록 생성기가 계산합니다. 담당자는 source snapshot의 commit ID 분류가 맞는지 검토합니다.",
      "action": "수정",
      "final": "Registry의 source.snapshot_sha까지 이어지는 Git commit 이력과 등록 묶음 생성기가 계산합니다. 담당자는 각 commit의 BANK-OM ID 분류가 맞는지 검토합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.shared_paths.readers",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 여러 BANK-OM ID가 함께 바꾼 파일 연결표",
      "location": "file.shared_paths.readers",
      "original": "과거 코드를 공식 코드 위에 BANK-OM별로 다시 구성할 때 공용 파일의 적용 순서와 연결된 BANK-OM ID를 확인하는 데 사용합니다. 현재 변경 범위 검사는 Manifest changed_paths와 commit inventory를 읽습니다.",
      "action": "수정",
      "final": "Git 기록이 유실되고 당시 코드 폴더만 남은 비상 상황에서, 공용 파일에 어떤 BANK-OM 변경을 적용해야 하는지 확인하는 데 사용합니다. 최신 커스텀 브랜치의 변경 범위 검사는 Manifest changed_paths와 commit inventory를 읽습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.shared_paths.fields.0.2",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 여러 BANK-OM ID가 함께 바꾼 파일 연결표",
      "location": "file.shared_paths.fields.0.2",
      "original": "과거 source snapshot에서 두 ID 이상이 함께 변경한 정확한 파일",
      "action": "수정",
      "final": "Registry source.snapshot_sha의 custom branch commit까지 두 ID 이상이 함께 변경한 정확한 파일",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.shared_paths.fields.1.0",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 여러 BANK-OM ID가 함께 바꾼 파일 연결표",
      "location": "file.shared_paths.fields.1.0",
      "original": "<BANK-OM ID 목록>",
      "action": "유지",
      "final": "<BANK-OM ID 목록>",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.shared_paths.fields.1.2",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 여러 BANK-OM ID가 함께 바꾼 파일 연결표",
      "location": "file.shared_paths.fields.1.2",
      "original": "그 과거 snapshot 시점까지 해당 파일을 변경한 기능 ID",
      "action": "수정",
      "final": "Registry source.snapshot_sha의 custom branch commit까지 해당 파일을 변경한 기능 ID",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.shared_paths.fields.1.3",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 여러 BANK-OM ID가 함께 바꾼 파일 연결표",
      "location": "file.shared_paths.fields.1.3",
      "original": "commit 메시지에서 자동 추출",
      "action": "유지",
      "final": "commit 메시지에서 자동 추출",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.shared_paths.updateReason",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 여러 BANK-OM ID가 함께 바꾼 파일 연결표",
      "location": "file.shared_paths.updateReason",
      "original": "과거 source snapshot 안에서 BANK-OM-002도 Entity.java를 실제로 변경한 commit이 확인됐다면 owners에 추가합니다. snapshot 이후 후속 commit 때문에 이 과거 기록을 바꾸지 않습니다.",
      "action": "수정",
      "final": "Registry source.snapshot_sha의 custom branch commit까지 BANK-OM-002도 Entity.java를 변경한 사실이 확인되면 owners 목록에 추가합니다. source.snapshot_sha 이후의 후속 commit 때문에 이 연결표를 바꾸지는 않습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.shared_paths.storage",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 여러 BANK-OM ID가 함께 바꾼 파일 연결표",
      "location": "file.shared_paths.storage",
      "original": "버전별 최초 source snapshot의 파생 파일입니다. 버전별 generate_registration_bundle.py는 고정 SHA와 사람 정책을 포함하므로 일반 후속 commit 처리에 실행하지 않습니다. snapshot 기준을 바꾸는 별도 승인 작업에서만 diff를 검토하며 재생성합니다.",
      "action": "수정",
      "final": "Registry source.snapshot_sha의 custom branch commit을 기준으로 자동 생성해 제품 버전별 등록 폴더에 보관합니다. generate_registration_bundle.py는 그 commit까지의 Git 이력과 사람 정책을 사용하므로 일반 후속 commit 처리에는 실행하지 않습니다. Registry source.snapshot_sha를 바꾸는 별도 승인 작업에서만 변경 내용을 검토하고 다시 만듭니다.",
      "reason": "‘파생’ 대신 자동으로 생성되는 파일을 직접 설명"
    },
    {
      "id": "3|file.source_snapshot_owners.title",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.title",
      "original": "과거 코드 파일–BANK-OM 연결표",
      "action": "수정",
      "final": "Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.source_snapshot_owners.purpose",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.purpose",
      "original": "최초 등록에 사용한 과거 행내 코드에서 각 변경 파일을 어떤 BANK-OM commit들이 바꿨는지 기록합니다. 사람이나 조직의 파일 소유권을 뜻하지 않습니다. 실제 파일명에는 owners가 남아 있지만 이 위키에서는 의미에 맞춰 연결표라고 부릅니다. 현재 Manifest의 검사 범위를 나누는 파일이 아니라, 과거 코드를 공식 코드 위에 기능별로 다시 구성하는 검사에서만 사용합니다.",
      "action": "수정",
      "final": "Registry의 source.snapshot_sha가 가리키는 custom branch commit까지, 각 파일을 어떤 BANK-OM commit들이 변경했는지 기록합니다. 사람이나 조직의 파일 소유권을 뜻하지 않습니다. Git 기록이 유실되고 당시 코드 폴더만 남은 비상 상황에서 코드 복구 순서를 정할 때 사용합니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "3|file.source_snapshot_owners.created",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.created",
      "original": "한 버전의 등록 묶음을 처음 만들 때, 기준이 되는 과거 행내 code snapshot의 commit 이력을 읽어 자동 생성합니다.",
      "action": "수정",
      "final": "제품 버전별 등록 묶음을 처음 만들 때 Registry source.snapshot_sha에 기록할 custom branch commit까지의 Git commit 이력을 읽어 자동 생성합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.source_snapshot_owners.update",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.update",
      "original": "기준으로 삼는 과거 snapshot SHA가 바뀔 때만 다시 생성합니다. 같은 ID의 후속 commit이 생겼다는 이유만으로 과거 snapshot 기록을 고치지 않습니다.",
      "action": "수정",
      "final": "Registry source.snapshot_sha의 custom branch commit을 다른 commit으로 바꿀 때만 다시 생성합니다. 같은 ID의 후속 commit이 생겼다는 이유만으로 기존 source.snapshot_sha의 연결표를 고치지 않습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.source_snapshot_owners.owner",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.owner",
      "original": "Git 이력과 생성기가 자동으로 만듭니다. 담당자는 잘못 분류된 commit ID가 없는지 검토하며 파일을 임의로 편집하지 않습니다.",
      "action": "유지",
      "final": "Git 이력과 생성기가 자동으로 만듭니다. 담당자는 잘못 분류된 commit ID가 없는지 검토하며 파일을 임의로 편집하지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.source_snapshot_owners.readers",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.readers",
      "original": "과거 행내 코드 재구성 검사(T25-R)가 어떤 파일을 어느 BANK-OM 단계에서 복원할지 결정할 때 사용합니다. 현재 버전의 등록 범위 검사(T40·T93)는 이 파일이 아니라 Manifest의 changed_paths를 사용합니다.",
      "action": "수정",
      "final": "비상 복구 검사(T25-R)가 각 파일에 어떤 BANK-OM 변경을 적용할지 결정할 때 사용합니다. 최신 커스텀 브랜치의 등록 범위 검사(T40·T93)는 이 파일이 아니라 Manifest의 changed_paths를 사용합니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "3|file.source_snapshot_owners.fields.0.2",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.fields.0.2",
      "original": "과거 snapshot에서 공식 원본과 달랐던 정확한 파일",
      "action": "수정",
      "final": "Registry source.snapshot_sha의 custom branch commit에서 공식 OpenMetadata commit과 달랐던 정확한 파일",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.source_snapshot_owners.fields.1.0",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.fields.1.0",
      "original": "<BANK-OM ID 목록>",
      "action": "유지",
      "final": "<BANK-OM ID 목록>",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.source_snapshot_owners.fields.1.2",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.fields.1.2",
      "original": "그 과거 snapshot 시점까지 해당 파일을 변경한 기능 ID",
      "action": "수정",
      "final": "Registry source.snapshot_sha의 custom branch commit까지 해당 파일을 변경한 기능 ID",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.source_snapshot_owners.fields.1.3",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.fields.1.3",
      "original": "commit 메시지에서 자동 추출",
      "action": "유지",
      "final": "commit 메시지에서 자동 추출",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.source_snapshot_owners.updateReason",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.updateReason",
      "original": "BANK-OM-007의 후속 commit이 나중에 같은 파일을 수정해도 최초 source snapshot에는 그 commit이 없었습니다. 따라서 두 과거 코드 연결표는 바꾸지 않습니다. 현재 버전의 BANK-OM-007 Manifest changed_paths와 commit-inventory.yaml이 후속 변경을 기록합니다.",
      "action": "수정",
      "final": "BANK-OM-007의 후속 commit은 Registry source.snapshot_sha에 기록된 custom branch commit 이후에 만들어졌습니다. 따라서 이 연결표는 바꾸지 않습니다. 최신 커스텀 브랜치의 BANK-OM-007 Manifest changed_paths와 commit-inventory.yaml이 후속 변경을 기록합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.source_snapshot_owners.scopeFlow.0.0",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.scopeFlow.0.0",
      "original": "과거 snapshot 시점",
      "action": "수정",
      "final": "Registry source.snapshot_sha의 custom commit",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.source_snapshot_owners.scopeFlow.1.0",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.scopeFlow.1.0",
      "original": "007 후속 commit",
      "action": "유지",
      "final": "007 후속 commit",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.source_snapshot_owners.scopeFlow.2.1",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.scopeFlow.2.1",
      "original": "Manifest·commit inventory에 007 반영",
      "action": "유지",
      "final": "Manifest·commit inventory에 007 반영",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.source_snapshot_owners.scopeOutcome",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.scopeOutcome",
      "original": "T25-R은 과거 snapshot을 재구성할 때 serviceConnection.ts를 BANK-OM-006 단계에서 복원합니다. 현재 범위 검사는 BANK-OM-007 Manifest와 commit inventory에서 후속 변경을 확인합니다. 과거 연결표와 현재 범위 자료는 서로 다른 시점을 설명하므로 값이 달라도 오류가 아닙니다.",
      "action": "수정",
      "final": "비상 복구 검사(T25-R)는 serviceConnection.ts에 BANK-OM-006 변경을 먼저 적용합니다. 최신 커스텀 브랜치의 변경 범위 검사는 BANK-OM-007 Manifest와 commit-inventory.yaml에서 후속 변경을 확인합니다. 두 자료는 서로 다른 commit 상태를 설명하므로 값이 달라도 오류가 아닙니다.",
      "reason": "snapshot을 ‘과거 전체 파일 복사본’으로 설명"
    },
    {
      "id": "3|file.source_snapshot_owners.scopeExamples.0.2",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.scopeExamples.0.2",
      "original": "과거 snapshot 재구성에만 사용",
      "action": "수정",
      "final": "Registry source.snapshot_sha의 코드 상태 복원에만 사용",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.source_snapshot_owners.scopeExamples.1.1",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.scopeExamples.1.1",
      "original": "serviceConnection.ts 포함",
      "action": "유지",
      "final": "serviceConnection.ts 포함",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.source_snapshot_owners.scopeExamples.1.2",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.scopeExamples.1.2",
      "original": "현재 버전 범위 검사에 사용",
      "action": "수정",
      "final": "최신 커스텀 브랜치의 범위 검사에 사용",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.source_snapshot_owners.scopeExamples.2.1",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.scopeExamples.2.1",
      "original": "과거 snapshot에서 여러 ID가 연결된 파일만 포함",
      "action": "수정",
      "final": "Registry source.snapshot_sha의 custom commit까지 여러 ID가 연결된 파일만 포함",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.source_snapshot_owners.scopeExamples.2.2",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.scopeExamples.2.2",
      "original": "과거 snapshot 재구성에 사용",
      "action": "수정",
      "final": "Git 이력 없이 보관된 코드 복원에 사용",
      "reason": "snapshot을 ‘과거 전체 파일 복사본’으로 설명"
    },
    {
      "id": "3|file.source_snapshot_owners.commands.0.label",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.commands.0.label",
      "original": "등록 묶음 재생성 · 이 파일이 바뀜",
      "action": "유지",
      "final": "등록 묶음 재생성 · 이 파일이 바뀜",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.source_snapshot_owners.commands.0.meaning",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.commands.0.meaning",
      "original": "지정한 source snapshot까지의 commit을 읽어 파일별 BANK-OM 연결표를 다시 만듭니다. source snapshot SHA를 바꾸지 않았다면 생성 결과도 같아야 합니다.",
      "action": "수정",
      "final": "Registry source.snapshot_sha에 기록할 custom branch commit까지 읽어 파일별 BANK-OM 연결표를 다시 만듭니다. source.snapshot_sha가 같다면 생성 결과도 같아야 합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.source_snapshot_owners.commands.1.label",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.commands.1.label",
      "original": "등록자료 검증 · 이 파일은 바뀌지 않음",
      "action": "유지",
      "final": "등록자료 검증 · 이 파일은 바뀌지 않음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.source_snapshot_owners.commands.1.meaning",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.commands.1.meaning",
      "original": "과거 snapshot 연결표의 경로와 BANK-OM ID가 실제 snapshot·Manifest와 모순되지 않는지 확인합니다.",
      "action": "수정",
      "final": "source-snapshot-path-owners.yaml의 경로와 BANK-OM ID가 Registry source.snapshot_sha의 custom commit 및 Manifest와 모순되지 않는지 확인합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|file.source_snapshot_owners.storage",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.storage",
      "original": "버전별 등록 폴더의 자동 생성 파일로 Git에 보관합니다. 현재 기능 범위를 설명하려고 수동으로 최신화하지 않습니다. 현재 범위는 Manifest changed_paths와 commit-inventory.yaml에서 확인합니다.",
      "action": "수정",
      "final": "제품 버전별 등록 폴더의 자동 생성 파일로 Git에 보관합니다. 최신 커스텀 브랜치의 기능 범위를 설명하려고 수동으로 최신화하지 않습니다. 최신 범위는 Manifest changed_paths와 commit-inventory.yaml에서 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.diff_inventory.purpose",
      "chapter": "3",
      "page": "상세 · 전체 변경 파일 목록",
      "location": "file.diff_inventory.purpose",
      "original": "공식 원본과 행내 코드 사이에서 실제로 달라진 모든 파일 경로를 한 줄에 하나씩 기록합니다.",
      "action": "유지",
      "final": "공식 원본과 행내 코드 사이에서 실제로 달라진 모든 파일 경로를 한 줄에 하나씩 기록합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|file.diff_inventory.created",
      "chapter": "3",
      "page": "상세 · 전체 변경 파일 목록",
      "location": "file.diff_inventory.created",
      "original": "등록 묶음을 처음 만들 때 Git diff로 생성합니다.",
      "action": "유지",
      "final": "등록 묶음을 처음 만들 때 Git diff로 생성합니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "3|file.diff_inventory.update",
      "chapter": "3",
      "page": "상세 · 전체 변경 파일 목록",
      "location": "file.diff_inventory.update",
      "original": "검사 대상 OpenMetadata 코드 commit 또는 공식 기준 commit이 바뀔 때마다 다시 생성합니다.",
      "action": "유지",
      "final": "검사 대상 OpenMetadata 코드 commit 또는 공식 기준 commit이 바뀔 때마다 다시 생성합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.diff_inventory.owner",
      "chapter": "3",
      "page": "상세 · 전체 변경 파일 목록",
      "location": "file.diff_inventory.owner",
      "original": "Git과 생성기가 자동으로 만듭니다. 사람이 파일 목록을 직접 보정하지 않습니다.",
      "action": "유지",
      "final": "Git과 생성기가 자동으로 만듭니다. 사람이 파일 목록을 직접 보정하지 않습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|file.diff_inventory.readers",
      "chapter": "3",
      "page": "상세 · 전체 변경 파일 목록",
      "location": "file.diff_inventory.readers",
      "original": "등록자료가 실제 Git diff를 빠짐없이 설명하는지 확인하는 전체 변경 범위 검사에 사용됩니다.",
      "action": "유지",
      "final": "등록자료가 실제 Git diff를 빠짐없이 설명하는지 확인하는 전체 변경 범위 검사에 사용됩니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|file.diff_inventory.fields.0.2",
      "chapter": "3",
      "page": "상세 · 전체 변경 파일 목록",
      "location": "file.diff_inventory.fields.0.2",
      "original": "저장소 root 기준 실제 변경 파일",
      "action": "수정",
      "final": "제품 코드 저장소의 최상위 폴더 기준 실제 변경 파일",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.diff_inventory.fields.0.3",
      "chapter": "3",
      "page": "상세 · 전체 변경 파일 목록",
      "location": "file.diff_inventory.fields.0.3",
      "original": "Git diff 자동 생성",
      "action": "유지",
      "final": "Git diff 자동 생성",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.diff_inventory.updateReason",
      "chapter": "3",
      "page": "상세 · 전체 변경 파일 목록",
      "location": "file.diff_inventory.updateReason",
      "original": "검사 대상 OpenMetadata 코드에 새 변경 파일이 생겼으므로 전체 목록을 Git에서 다시 생성합니다. 텍스트 파일만 수정하면 실제 코드와 달라져 검사에 실패합니다.",
      "action": "유지",
      "final": "검사 대상 OpenMetadata 코드에 새 변경 파일이 생겼으므로 전체 목록을 Git에서 다시 생성합니다. 텍스트 파일만 수정하면 실제 코드와 달라져 검사에 실패합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|file.diff_inventory.storage",
      "chapter": "3",
      "page": "상세 · 전체 변경 파일 목록",
      "location": "file.diff_inventory.storage",
      "original": "후보·공식 기준별 파생 파일입니다. 생성 기준 SHA와 함께 Git에 보관해 재현합니다.",
      "action": "수정",
      "final": "검사 대상 코드와 공식 기준 코드를 비교해 자동 생성한 파일입니다. 어떤 두 commit을 비교했는지 함께 Git에 보관합니다.",
      "reason": "‘파생’ 대신 자동으로 생성되는 파일을 직접 설명"
    },
    {
      "id": "3|file.layout.purpose",
      "chapter": "3",
      "page": "상세 · 코드 경로 분류표",
      "location": "file.layout.purpose",
      "original": "파일 경로가 공식 OpenMetadata 코드, 행내 거버넌스 코드, 플랫폼 확장 또는 알 수 없는 영역 중 어디에 속하는지 정합니다.",
      "action": "유지",
      "final": "파일 경로가 공식 OpenMetadata 코드, 행내 거버넌스 코드, 플랫폼 확장 또는 알 수 없는 영역 중 어디에 속하는지 정합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|file.layout.created",
      "chapter": "3",
      "page": "상세 · 코드 경로 분류표",
      "location": "file.layout.created",
      "original": "저장소를 검사 체계에 처음 등록할 때 만듭니다.",
      "action": "수정",
      "final": "제품 코드 저장소를 검사 체계에 처음 등록할 때 만듭니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.layout.update",
      "chapter": "3",
      "page": "상세 · 코드 경로 분류표",
      "location": "file.layout.update",
      "original": "공식 버전에서 최상위 모듈이 추가·이동되거나 행내 확장 root가 바뀔 때 갱신합니다.",
      "action": "유지",
      "final": "공식 버전에서 최상위 모듈이 추가·이동되거나 행내 확장 root가 바뀔 때 갱신합니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "3|file.layout.owner",
      "chapter": "3",
      "page": "상세 · 코드 경로 분류표",
      "location": "file.layout.owner",
      "original": "저장소 구조를 아는 플랫폼 담당자가 승인합니다.",
      "action": "수정",
      "final": "제품 코드 저장소의 폴더 구조를 아는 플랫폼 담당자가 승인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.layout.readers",
      "chapter": "3",
      "page": "상세 · 코드 경로 분류표",
      "location": "file.layout.readers",
      "original": "commit·경로 정책 확인, 등록 범위 확인, 민감 경로 확인 등 파일 위치를 해석하는 모든 소스 검사에 사용됩니다.",
      "action": "유지",
      "final": "commit·경로 정책 확인, 등록 범위 확인, 민감 경로 확인 등 파일 위치를 해석하는 모든 소스 검사에 사용됩니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.layout.fields.0.2",
      "chapter": "3",
      "page": "상세 · 코드 경로 분류표",
      "location": "file.layout.fields.0.2",
      "original": "이 경로 정책을 작성한 공식 기준 commit",
      "action": "유지",
      "final": "이 경로 정책을 작성한 공식 기준 commit",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.layout.fields.1.2",
      "chapter": "3",
      "page": "상세 · 코드 경로 분류표",
      "location": "file.layout.fields.1.2",
      "original": "대소문자·Unicode·symlink 등 경로 해석 규칙",
      "action": "유지",
      "final": "대소문자·Unicode·symlink 등 경로 해석 규칙",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.layout.fields.2.2",
      "chapter": "3",
      "page": "상세 · 코드 경로 분류표",
      "location": "file.layout.fields.2.2",
      "original": "공식 OpenMetadata 코드 영역",
      "action": "유지",
      "final": "공식 OpenMetadata 코드 영역",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.layout.fields.3.2",
      "chapter": "3",
      "page": "상세 · 코드 경로 분류표",
      "location": "file.layout.fields.3.2",
      "original": "검사 정책·test·문서 영역",
      "action": "유지",
      "final": "검사 정책·test·문서 영역",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.layout.fields.4.2",
      "chapter": "3",
      "page": "상세 · 코드 경로 분류표",
      "location": "file.layout.fields.4.2",
      "original": "공식 코드와 분리한 행내 확장 영역",
      "action": "유지",
      "final": "공식 코드와 분리한 행내 확장 영역",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.layout.fields.5.2",
      "chapter": "3",
      "page": "상세 · 코드 경로 분류표",
      "location": "file.layout.fields.5.2",
      "original": "분류하지 못한 경로의 처리",
      "action": "유지",
      "final": "분류하지 못한 경로의 처리",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|file.layout.updateReason",
      "chapter": "3",
      "page": "상세 · 코드 경로 분류표",
      "location": "file.layout.updateReason",
      "original": "새 공식 버전에서 openmetadata-mcp 모듈이 검사 대상 공식 코드로 추가됐음을 확인했을 때 root를 추가합니다. 단순히 오류를 없애려고 unknown 경로를 넓게 허용하지 않습니다.",
      "action": "유지",
      "final": "새 공식 버전에서 openmetadata-mcp 모듈이 검사 대상 공식 코드로 추가됐음을 확인했을 때 root를 추가합니다. 단순히 오류를 없애려고 unknown 경로를 넓게 허용하지 않습니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "3|file.layout.storage",
      "chapter": "3",
      "page": "상세 · 코드 경로 분류표",
      "location": "file.layout.storage",
      "original": "공식 기준 버전별 정책입니다. upstream_base_sha가 달라지면 기존 정책을 그대로 복사하지 말고 경로 구조를 재검토합니다.",
      "action": "유지",
      "final": "공식 기준 버전별 정책입니다. upstream_base_sha가 달라지면 기존 정책을 그대로 복사하지 말고 경로 구조를 재검토합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|file.zones.purpose",
      "chapter": "3",
      "page": "상세 · 중요 경로 정책(Sensitive zones)",
      "location": "file.zones.purpose",
      "original": "보안·인증·설정·DB처럼 변경 시 차단 또는 별도 승인이 필요한 경로를 분류합니다.",
      "action": "유지",
      "final": "보안·인증·설정·DB처럼 변경 시 차단 또는 별도 승인이 필요한 경로를 분류합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|file.zones.created",
      "chapter": "3",
      "page": "상세 · 중요 경로 정책(Sensitive zones)",
      "location": "file.zones.created",
      "original": "저장소의 위험 경로 정책을 최초 정의할 때 만듭니다.",
      "action": "수정",
      "final": "제품 코드 저장소의 위험 경로 정책을 최초 정의할 때 만듭니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.zones.update",
      "chapter": "3",
      "page": "상세 · 중요 경로 정책(Sensitive zones)",
      "location": "file.zones.update",
      "original": "새 보안·인증 모듈, migration 경로 또는 조직 통제 정책이 바뀔 때 갱신합니다.",
      "action": "유지",
      "final": "새 보안·인증 모듈, migration 경로 또는 조직 통제 정책이 바뀔 때 갱신합니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "3|file.zones.owner",
      "chapter": "3",
      "page": "상세 · 중요 경로 정책(Sensitive zones)",
      "location": "file.zones.owner",
      "original": "보안·플랫폼·DB 담당자가 함께 승인합니다.",
      "action": "유지",
      "final": "보안·플랫폼·DB 담당자가 함께 승인합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|file.zones.readers",
      "chapter": "3",
      "page": "상세 · 중요 경로 정책(Sensitive zones)",
      "location": "file.zones.readers",
      "original": "민감 경로 변경 검사와 업그레이드 위험 검사에서 변경 경로의 승인 수준을 정할 때 사용됩니다.",
      "action": "유지",
      "final": "민감 경로 변경 검사와 업그레이드 위험 검사에서 변경 경로의 승인 수준을 정할 때 사용됩니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "3|file.zones.fields.0.2",
      "chapter": "3",
      "page": "상세 · 중요 경로 정책(Sensitive zones)",
      "location": "file.zones.fields.0.2",
      "original": "일반 BANK-OM 변경을 허용하지 않는 경로",
      "action": "수정",
      "final": "일반 BANK-OM 작업에서는 변경할 수 없는 경로",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.zones.fields.1.2",
      "chapter": "3",
      "page": "상세 · 중요 경로 정책(Sensitive zones)",
      "location": "file.zones.fields.1.2",
      "original": "별도 승인 없이는 진행할 수 없는 경로",
      "action": "수정",
      "final": "보안·플랫폼 담당자의 별도 승인이 필요한 경로",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.zones.fields.2.2",
      "chapter": "3",
      "page": "상세 · 중요 경로 정책(Sensitive zones)",
      "location": "file.zones.fields.2.2",
      "original": "변경 사실을 반드시 결과에 표시할 경로",
      "action": "수정",
      "final": "변경 사실을 검사 결과에 반드시 표시할 경로",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|file.zones.updateReason",
      "chapter": "3",
      "page": "상세 · 중요 경로 정책(Sensitive zones)",
      "location": "file.zones.updateReason",
      "original": "새 공식 버전의 인증 코드가 auth 경로로 분리됐고 같은 승인 통제가 필요하다고 보안 담당자가 판단했을 때 추가합니다.",
      "action": "유지",
      "final": "새 공식 버전의 인증 코드가 auth 경로로 분리됐고 같은 승인 통제가 필요하다고 보안 담당자가 판단했을 때 추가합니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "3|file.zones.storage",
      "chapter": "3",
      "page": "상세 · 중요 경로 정책(Sensitive zones)",
      "location": "file.zones.storage",
      "original": "정책 파일이므로 변경 사유와 승인자를 Git 리뷰에 남깁니다. 과거 검사 결과에 사용한 정책은 수정하지 않습니다.",
      "action": "유지",
      "final": "정책 파일이므로 변경 사유와 승인자를 Git 리뷰에 남깁니다. 과거 검사 결과에 사용한 정책은 수정하지 않습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|file.candidate_lock.purpose",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.purpose",
      "original": "검사할 행내 commit과 전체 파일 상태를 고정하고, Runtime·배포 검사 단계에서는 그 코드로 만든 실제 이미지·패키지까지 같은 대상으로 묶습니다.",
      "action": "수정",
      "final": "어떤 행내 코드를 검사했는지 고정합니다. 실행·배포 검사에서는 그 코드로 만든 이미지나 패키지도 같은 검사 대상으로 묶습니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|file.candidate_lock.created",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.created",
      "original": "소스 검사 후보가 확정되면 commit·tree와 소스 내용 확인값으로 생성합니다. 실제 이미지·패키지를 만든 뒤에는 그 artifact digest를 포함한 Runtime·배포용 새 lock을 생성합니다.",
      "action": "수정",
      "final": "현재 소스 검사 명령은 실행할 때 제품 코드 저장소의 HEAD commit, 전체 파일 상태와 소스 내용 확인값을 자동 계산해 source-gate-results.json의 candidate_lock 항목에 기록합니다. 소스 검사 전에 사람이 별도 YAML을 작성하지 않습니다. 실제 이미지나 패키지를 검사할 때는 그 배포 파일의 내용 확인값을 사용한 별도 Candidate lock이 필요합니다.",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀 · artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "4|file.candidate_lock.update",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.update",
      "original": "기존 파일을 갱신하지 않습니다. commit·tree·소스 내용·실제 artifact·공식 목표·통합 방식 중 하나라도 바뀌면 새 후보와 새 lock을 만듭니다.",
      "action": "수정",
      "final": "기존 파일을 고치지 않습니다. 코드, 전체 파일 상태, 배포 파일, 공식 목표 버전, 통합 방식 중 하나라도 바뀌면 새 Candidate lock을 만듭니다.",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "4|file.candidate_lock.owner",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.owner",
      "original": "CI·Runtime 실행기가 자동 생성하고 배포 담당자가 검사 대상이 맞는지 승인합니다.",
      "action": "수정",
      "final": "소스 검사기 또는 CI·Runtime 실행기가 계산하고, 담당자는 결과에 기록된 제품 코드 저장소·commit·내용 확인값이 실제 검사 대상과 같은지 확인합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|file.candidate_lock.readers",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.readers",
      "original": "검사 대상 고정, 변경 생존 확인, Runtime test 실행, 증거 연결과 실제 배포 일치 검사에 사용됩니다.",
      "action": "유지",
      "final": "검사 대상 고정, 변경 생존 확인, Runtime test 실행, 증거 연결과 실제 배포 일치 검사에 사용됩니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|file.candidate_lock.fields.0.2",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.fields.0.2",
      "original": "공식 코드와 행내 변경을 합친 방식",
      "action": "유지",
      "final": "공식 코드와 행내 변경을 합친 방식",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.candidate_lock.fields.2.2",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.fields.2.2",
      "original": "업그레이드 전 공식 commit",
      "action": "유지",
      "final": "업그레이드 전 공식 commit",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.candidate_lock.fields.3.2",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.fields.3.2",
      "original": "업그레이드할 공식 commit",
      "action": "유지",
      "final": "업그레이드할 공식 commit",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.candidate_lock.fields.4.2",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.fields.4.2",
      "original": "검사 대상 행내 저장소",
      "action": "수정",
      "final": "검사 대상 제품 코드 저장소",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|file.candidate_lock.fields.5.2",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.fields.5.2",
      "original": "모든 BANK-OM 변경을 포함한 최종 검사 대상 commit 하나",
      "action": "수정",
      "final": "모든 BANK-OM 변경을 포함한 최종 검사 대상 custom branch commit 하나",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|file.candidate_lock.fields.5.4",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.fields.5.4",
      "original": "1.13.0 재검증 예: 3a2811cf… · 1.13.1 과거 진단 예: dee330ebd5…",
      "action": "수정",
      "final": "1.13.0 소스 재검사 예: 3a2811cf… · 1.13.1 commit별 재적용 진단 예: dee330ebd5…",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|file.candidate_lock.fields.6.2",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.fields.6.2",
      "original": "그 commit에서 보이는 전체 파일 내용의 식별값",
      "action": "수정",
      "final": "그 commit에서 보이는 전체 파일 내용에 Git이 붙인 식별값",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|file.candidate_lock.fields.7.2",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.fields.7.2",
      "original": "소스 검사에서는 source tree 내용을 묶는 SHA-256, Runtime·배포 검사에서는 실제 이미지·패키지 SHA-256",
      "action": "수정",
      "final": "소스 검사에서는 전체 소스 내용의 SHA-256 확인값, 실행·배포 검사에서는 실제 이미지·패키지의 SHA-256 확인값",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|file.candidate_lock.fields.7.3",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.fields.7.3",
      "original": "소스 검사기 또는 빌드 자동",
      "action": "유지",
      "final": "소스 검사기 또는 빌드 자동",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.candidate_lock.fields.7.4",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.fields.7.4",
      "original": "현재 소스 결과: source tree digest · 환경 실행 예시: image sha256:61a3…",
      "action": "수정",
      "final": "현재 소스 결과: 전체 소스 확인값 · 환경 실행 예시: image sha256:61a3…",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "4|file.candidate_lock.fields.8.2",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.fields.8.2",
      "original": "patch-replay에서 사용한 Patch-lock 파일의 SHA-256",
      "action": "유지",
      "final": "patch-replay에서 사용한 Patch-lock 파일의 SHA-256",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.candidate_lock.fields.8.4",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.fields.8.4",
      "original": "patch-replay 예시: sha256:8ce1…",
      "action": "유지",
      "final": "patch-replay 예시: sha256:8ce1…",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.candidate_lock.updateReason",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.updateReason",
      "original": "코드나 빌드 파일이 바뀌면 기존 lock을 수정하지 않고 bbb222 후보용 새 evidence 폴더와 새 Candidate lock을 생성합니다. 이전 결과는 aaa111 후보의 기록으로 보존합니다.",
      "action": "수정",
      "final": "코드나 빌드 파일이 바뀌면 기존 결과의 Candidate lock을 수정하지 않습니다. 새 검사를 실행해 bbb222용 결과와 Candidate lock을 새로 만들고, 이전 결과는 aaa111을 검사한 기록으로 보존합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|file.candidate_lock.storage",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.storage",
      "original": "검사 대상별 불변 실행 증거입니다. 실행 번호·검사 대상 Git commit SHA별 디렉터리 또는 CI artifact로 분리하고 덮어쓰지 않습니다. 현재 OM_TEMP 1.13.1 결과의 candidate는 dee330ebd5…이지만 실제 생성 방식은 커밋별 재적용입니다. 저장된 integration_strategy: vendor-merge 값과 실제 과정이 다르므로 이 lock은 vendor-merge 완료 증거로 사용하지 않습니다.",
      "action": "수정",
      "final": "소스 검사에서는 source-gate-results.json 전체를 새 파일로 보관하면 그 안의 Candidate lock도 함께 보존됩니다. 별도 배포 실행이 Candidate lock YAML을 만들면 같은 실행 증거 폴더에 보관합니다. OM_TEMP 1.13.0 소스 검사를 다시 수행한 custom commit은 3a2811cf…입니다. 1.13.1의 dee330ebd5…는 BANK-OM commit을 하나씩 다시 적용해 충돌 위치를 확인한 진단 코드이므로 정식 vendor-merge 결과나 운영 배포 증거로 사용하지 않습니다.",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "4|file.test_run_set.purpose",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.purpose",
      "original": "어떤 필수 test를 몇 번째 시도에서 실행했고 결과가 무엇인지, 정확한 후보·검사기·suite 버전과 함께 기록합니다.",
      "action": "수정",
      "final": "어떤 필수 test를 몇 번째 시도에서 실행했고 결과가 무엇인지, 정확한 검사 대상 commit·검사기 commit·suite 버전과 함께 기록합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|file.test_run_set.created",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.created",
      "original": "Runtime Contract test를 실행할 때마다 자동 생성합니다.",
      "action": "유지",
      "final": "Runtime Contract test를 실행할 때마다 자동 생성합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|file.test_run_set.update",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.update",
      "original": "기존 파일을 수정하지 않습니다. 재실행·재시도·후보 변경마다 새 실행 결과를 만듭니다.",
      "action": "수정",
      "final": "기존 파일을 수정하지 않습니다. 재실행·재시도·검사 대상 commit 변경마다 새 실행 결과를 만듭니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|file.test_run_set.owner",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.owner",
      "original": "Runtime test 실행기가 자동 생성합니다.",
      "action": "유지",
      "final": "Runtime test 실행기가 자동 생성합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|file.test_run_set.readers",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.readers",
      "original": "Runtime test 재시도 판정, 실행 증거 연결과 실제 배포 일치 검사에 사용됩니다.",
      "action": "유지",
      "final": "Runtime test 재시도 판정, 실행 증거 연결과 실제 배포 일치 검사에 사용됩니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|file.test_run_set.fields.0.2",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.fields.0.2",
      "original": "test를 실행한 최종 후보 commit 하나",
      "action": "수정",
      "final": "test를 실행한 최종 검사 대상 commit 하나",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|file.test_run_set.fields.0.3",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.fields.0.3",
      "original": "Candidate lock에서 자동",
      "action": "유지",
      "final": "Candidate lock에서 자동",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.test_run_set.fields.0.4",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.fields.0.4",
      "original": "형식 예시: <실제로 test한 후보 SHA>",
      "action": "수정",
      "final": "형식 예시: <실제로 test한 custom branch commit SHA>",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|file.test_run_set.fields.1.2",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.fields.1.2",
      "original": "test한 배포 artifact",
      "action": "수정",
      "final": "test한 이미지나 패키지의 내용 확인값",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "4|file.test_run_set.fields.1.3",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.fields.1.3",
      "original": "Candidate lock에서 자동",
      "action": "유지",
      "final": "Candidate lock에서 자동",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.test_run_set.fields.1.4",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.fields.1.4",
      "original": "환경 실행 예시: sha256:61a3…",
      "action": "유지",
      "final": "환경 실행 예시: sha256:61a3…",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.test_run_set.fields.3.2",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.fields.3.2",
      "original": "Manifest·Registry·Contract·test 묶음 버전",
      "action": "수정",
      "final": "Manifest·Registry·Contract·test 묶음의 내용 확인값",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|file.test_run_set.fields.3.3",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.fields.3.3",
      "original": "내용 digest 자동",
      "action": "수정",
      "final": "도구가 내용 확인값 자동 계산",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "4|file.test_run_set.fields.4.2",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.fields.4.2",
      "original": "실행한 test 파일과 함수",
      "action": "유지",
      "final": "실행한 test 파일과 함수",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.test_run_set.fields.5.2",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.fields.5.2",
      "original": "1부터 연속되는 시도 번호",
      "action": "유지",
      "final": "1부터 연속되는 시도 번호",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.test_run_set.fields.6.2",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.fields.6.2",
      "original": "pass·fail·error·skip 중 실행 결과",
      "action": "유지",
      "final": "pass·fail·error·skip 중 실행 결과",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.test_run_set.updateReason",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.updateReason",
      "original": "재시도 성공으로 첫 실패를 덮어쓰지 않습니다. 두 시도를 모두 새 Test run set에 남겨 T62가 기능 중요도에 따라 APPROVAL 여부를 판단하게 합니다.",
      "action": "유지",
      "final": "재시도 성공으로 첫 실패를 덮어쓰지 않습니다. 두 시도를 모두 새 Test run set에 남겨 T62가 기능 중요도에 따라 APPROVAL 여부를 판단하게 합니다.",
      "reason": "판정 이름과 그 판정이 뜻하는 결과가 함께 적혀 있어 유지"
    },
    {
      "id": "4|file.test_run_set.storage",
      "chapter": "4",
      "page": "상세 · Test run set",
      "location": "file.test_run_set.storage",
      "original": "실행별 불변 증거입니다. CI run ID·attempt와 함께 보관하고 같은 파일명을 다른 실행 결과로 덮어쓰지 않습니다.",
      "action": "유지",
      "final": "실행별 불변 증거입니다. CI run ID·attempt와 함께 보관하고 같은 파일명을 다른 실행 결과로 덮어쓰지 않습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|file.result.purpose",
      "chapter": "4",
      "page": "상세 · 검사 결과",
      "location": "file.result.purpose",
      "original": "어떤 입력으로 어떤 검사들을 실행했고 각 판정과 이유가 무엇인지, 나중에 같은 결과인지 확인할 digest와 함께 기록합니다.",
      "action": "수정",
      "final": "어떤 입력으로 어떤 검사를 실행했고 각 판정과 이유가 무엇인지 기록합니다. 결과 본문 전체에서 계산한 내용 확인값도 함께 저장합니다.",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "4|file.result.created",
      "chapter": "4",
      "page": "상세 · 검사 결과",
      "location": "file.result.created",
      "original": "소스 검사 또는 Runtime 검사를 실행할 때마다 자동 생성합니다.",
      "action": "유지",
      "final": "소스 검사 또는 Runtime 검사를 실행할 때마다 자동 생성합니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "4|file.result.update",
      "chapter": "4",
      "page": "상세 · 검사 결과",
      "location": "file.result.update",
      "original": "기존 결과는 수정하지 않습니다. 코드·정책·검사기·test·실행이 바뀌면 새 결과를 생성합니다.",
      "action": "유지",
      "final": "기존 결과는 수정하지 않습니다. 코드·정책·검사기·test·실행이 바뀌면 새 결과를 생성합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|file.result.owner",
      "chapter": "4",
      "page": "상세 · 검사 결과",
      "location": "file.result.owner",
      "original": "검사 실행기가 자동 생성하고 책임자는 개별 gate의 reasons를 확인합니다.",
      "action": "유지",
      "final": "검사 실행기가 자동 생성하고 책임자는 개별 gate의 reasons를 확인합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|file.result.readers",
      "chapter": "4",
      "page": "상세 · 검사 결과",
      "location": "file.result.readers",
      "original": "책임자, T91 배포 승격 검사와 감사·인수인계",
      "action": "유지",
      "final": "책임자, T91 배포 승격 검사와 감사·인수인계",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.result.fields.4.2",
      "chapter": "4",
      "page": "상세 · 검사 결과",
      "location": "file.result.fields.4.2",
      "original": "후보·정책·저장소 등 판정 입력",
      "action": "수정",
      "final": "검사 대상 제품 코드 저장소·commit·정책 등 판정 입력",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|file.result.fields.4.4",
      "chapter": "4",
      "page": "상세 · 검사 결과",
      "location": "file.result.fields.4.4",
      "original": "1.13.1 소스 진단 예: candidate_commit: dee330ebd5…",
      "action": "수정",
      "final": "1.13.0 재검증 예: candidate_commit: 3a2811cf…",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|file.result.fields.6.2",
      "chapter": "4",
      "page": "상세 · 검사 결과",
      "location": "file.result.fields.6.2",
      "original": "판정 본문 전체의 SHA-256",
      "action": "수정",
      "final": "결과가 나중에 바뀌지 않았는지 확인할 판정 본문 전체의 SHA-256 값",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|file.result.fields.7.2",
      "chapter": "4",
      "page": "상세 · 검사 결과",
      "location": "file.result.fields.7.2",
      "original": "결과를 찾기 위한 실행 번호",
      "action": "유지",
      "final": "결과를 찾기 위한 실행 번호",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.result.fields.8.2",
      "chapter": "4",
      "page": "상세 · 검사 결과",
      "location": "file.result.fields.8.2",
      "original": "verdict에 대응하는 명령 종료 코드",
      "action": "유지",
      "final": "verdict에 대응하는 명령 종료 코드",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.result.updateReason",
      "chapter": "4",
      "page": "상세 · 검사 결과",
      "location": "file.result.updateReason",
      "original": "BLOCK 결과 파일을 PASS로 직접 고치지 않습니다. 코드를 보완하고 검사기를 다시 실행해 새로운 결과와 result_digest를 만듭니다.",
      "action": "수정",
      "final": "BLOCK 결과 파일을 PASS로 직접 고치지 않습니다. 코드를 보완하고 검사기를 다시 실행해 새 결과와 그 결과 내용의 확인값(result_digest)을 만듭니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|file.result.storage",
      "chapter": "4",
      "page": "상세 · 검사 결과",
      "location": "file.result.storage",
      "original": "실행별 불변 증거입니다. 검사 대상 Git commit SHA·실행 번호·검사기 버전과 함께 보관합니다.",
      "action": "유지",
      "final": "실행별 불변 증거입니다. 검사 대상 Git commit SHA·실행 번호·검사기 버전과 함께 보관합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|file.patch_lock.purpose",
      "chapter": "4",
      "page": "상세 · Patch-lock",
      "location": "file.patch_lock.purpose",
      "original": "patch-replay 방식을 사용할 때 BANK-OM commit을 어느 순서와 개정으로 다시 적용할지 고정합니다.",
      "action": "유지",
      "final": "patch-replay 방식을 사용할 때 BANK-OM commit을 어느 순서와 개정으로 다시 적용할지 고정합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|file.patch_lock.created",
      "chapter": "4",
      "page": "상세 · Patch-lock",
      "location": "file.patch_lock.created",
      "original": "통합 전략이 patch-replay일 때만 후보를 만들기 전에 생성합니다.",
      "action": "수정",
      "final": "통합 전략이 patch-replay일 때만 검사 대상 custom branch commit을 만들기 전에 생성합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|file.patch_lock.update",
      "chapter": "4",
      "page": "상세 · Patch-lock",
      "location": "file.patch_lock.update",
      "original": "같은 ID의 후속 commit, 적용 순서 또는 개정 번호가 바뀌면 새 Patch-lock revision을 만듭니다. vendor-merge에서는 만들지 않습니다.",
      "action": "유지",
      "final": "같은 ID의 후속 commit, 적용 순서 또는 개정 번호가 바뀌면 새 Patch-lock revision을 만듭니다. vendor-merge에서는 만들지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|file.patch_lock.owner",
      "chapter": "4",
      "page": "상세 · Patch-lock",
      "location": "file.patch_lock.owner",
      "original": "변경관리 담당자가 순서를 승인하고 생성기가 commit 존재와 digest를 확인합니다.",
      "action": "수정",
      "final": "변경관리 담당자가 순서를 승인하고 생성기가 commit 존재 여부와 Patch-lock 내용 확인값을 계산합니다.",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "4|file.patch_lock.readers",
      "chapter": "4",
      "page": "상세 · Patch-lock",
      "location": "file.patch_lock.readers",
      "original": "patch-replay 실행, commit 규칙·적용 순서 검사와 Candidate lock 연결에 사용됩니다. vendor-merge 전략에서는 사용하지 않습니다.",
      "action": "유지",
      "final": "patch-replay 실행, commit 규칙·적용 순서 검사와 Candidate lock 연결에 사용됩니다. vendor-merge 전략에서는 사용하지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|file.patch_lock.fields.0.2",
      "chapter": "4",
      "page": "상세 · Patch-lock",
      "location": "file.patch_lock.fields.0.2",
      "original": "커스터마이징 commit을 가져올 이전 행내 릴리스",
      "action": "유지",
      "final": "커스터마이징 commit을 가져올 이전 행내 릴리스",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.patch_lock.fields.1.2",
      "chapter": "4",
      "page": "상세 · Patch-lock",
      "location": "file.patch_lock.fields.1.2",
      "original": "적용할 BANK-OM ID",
      "action": "유지",
      "final": "적용할 BANK-OM ID",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.patch_lock.fields.2.2",
      "chapter": "4",
      "page": "상세 · Patch-lock",
      "location": "file.patch_lock.fields.2.2",
      "original": "같은 ID 변경 묶음의 개정 번호",
      "action": "유지",
      "final": "같은 ID 변경 묶음의 개정 번호",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.patch_lock.fields.3.2",
      "chapter": "4",
      "page": "상세 · Patch-lock",
      "location": "file.patch_lock.fields.3.2",
      "original": "그 기능을 구성하는 commit SHA를 적용 순서대로 기록",
      "action": "유지",
      "final": "그 기능을 구성하는 commit SHA를 적용 순서대로 기록",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.patch_lock.fields.4.2",
      "chapter": "4",
      "page": "상세 · Patch-lock",
      "location": "file.patch_lock.fields.4.2",
      "original": "먼저 적용할 BANK-OM ID",
      "action": "유지",
      "final": "먼저 적용할 BANK-OM ID",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|file.patch_lock.updateReason",
      "chapter": "4",
      "page": "상세 · Patch-lock",
      "location": "file.patch_lock.updateReason",
      "original": "patch-replay 전략에서 같은 기능의 후속 commit이 추가됐으므로 같은 ID의 revision과 source_commits를 갱신한 새 Patch-lock을 만듭니다. 후속 commit이 새 파일을 변경했다면 Manifest의 changed_paths도 함께 갱신합니다.",
      "action": "유지",
      "final": "patch-replay 전략에서 같은 기능의 후속 commit이 추가됐으므로 같은 ID의 revision과 source_commits를 갱신한 새 Patch-lock을 만듭니다. 후속 commit이 새 파일을 변경했다면 Manifest의 changed_paths도 함께 갱신합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|file.patch_lock.commands.0.label",
      "chapter": "4",
      "page": "상세 · Patch-lock",
      "location": "file.patch_lock.commands.0.label",
      "original": "현재 OM_TEMP에는 생성 명령 없음",
      "action": "수정",
      "final": "현재 적용 예시인 OM_TEMP에는 생성 명령 없음",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|file.patch_lock.commands.0.meaning",
      "chapter": "4",
      "page": "상세 · Patch-lock",
      "location": "file.patch_lock.commands.0.meaning",
      "original": "현재 연습은 vendor-merge 전략이므로 Patch-lock을 만들지 않습니다. patch-replay를 채택하면 담당자가 적용 순서를 승인한 별도 생성 절차가 필요합니다.",
      "action": "유지",
      "final": "현재 연습은 vendor-merge 전략이므로 Patch-lock을 만들지 않습니다. patch-replay를 채택하면 담당자가 적용 순서를 승인한 별도 생성 절차가 필요합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|file.patch_lock.storage",
      "chapter": "4",
      "page": "상세 · Patch-lock",
      "location": "file.patch_lock.storage",
      "original": "patch-replay 후보별 불변 입력입니다. 이전 revision을 덮어쓰지 않고 Candidate lock에 사용한 Patch-lock digest를 기록합니다.",
      "action": "수정",
      "final": "patch-replay 검사 대상마다 새 파일로 보관합니다. 이전 개정 번호의 파일을 덮어쓰지 않고 Candidate lock에 사용한 Patch-lock의 내용 확인값을 기록합니다.",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "2|gate.t25r.title",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.title",
      "original": "T25-R · 과거 보관 소스 재구성 확인",
      "action": "수정",
      "final": "T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t25r.question",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.question",
      "original": "공식 변경 기록 없이 파일 상태만 남은 과거 행내 소스를 공식 원본과 등록자료로 같은 내용까지 다시 만들 수 있는가?",
      "action": "수정",
      "final": "Git commit 기록을 잃고 특정 버전의 코드 폴더만 남았을 때, 공식 OpenMetadata 코드와 당시 등록자료를 이용해 그 코드 폴더와 동일한 파일들을 복구할 수 있는가?",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25r.status",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.status",
      "original": "구현·단위 테스트 완료 · 현재 OM_TEMP에는 공식 변경 기록이 있어 실행 대상 아님",
      "action": "수정",
      "final": "구현·단위 테스트 완료 · 현재 적용 예시인 OM_TEMP에는 공식 변경 기록이 있어 실행 대상 아님",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t25r.timing",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.timing",
      "original": "과거 행내 소스의 Git 변경 기록이 없고 파일 snapshot만 남은 경우에만 T25 대신 실행합니다. 현재 OM_TEMP처럼 공식 버전과 BANK-OM commit 이력이 남아 있으면 사용하지 않습니다.",
      "action": "수정",
      "final": "Git commit 기록이 유실되고 당시의 코드 폴더만 남은 비상 상황에서 T25 대신 실행합니다. OM_TEMP에는 공식 버전과 BANK-OM commit 기록이 모두 남아 있으므로 이 검사를 실행하지 않습니다.",
      "reason": "snapshot을 ‘과거 전체 파일 복사본’으로 설명"
    },
    {
      "id": "2|gate.t25r.inputs.0.0",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.inputs.0.0",
      "original": "공식 원본과 과거 보관 소스",
      "action": "수정",
      "final": "복구를 시작할 공식 코드",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25r.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.inputs.0.1",
      "original": "재구성의 시작 코드와 최종 비교 대상",
      "action": "수정",
      "final": "BANK-OM을 적용하기 전의 공식 OpenMetadata commit",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25r.inputs.0.2",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.inputs.0.2",
      "original": "공식 1.13.0 · 과거 행내 source snapshot",
      "action": "수정",
      "final": "공식 1.13.0 commit",
      "reason": "snapshot을 ‘과거 전체 파일 복사본’으로 설명"
    },
    {
      "id": "2|gate.t25r.inputs.1.0",
      "chapter": "2",
      "page": "상세 · T25-R · 과거 보관 소스 재구성 확인",
      "location": "gate.t25r.inputs.1.0",
      "original": "Manifest와 과거 코드 파일–BANK-OM 연결표",
      "action": "삭제",
      "final": "삭제",
      "reason": "앞뒤 내용과 중복되거나 운영 판단에 필요하지 않아 삭제"
    },
    {
      "id": "2|gate.t25r.inputs.1.1",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.inputs.1.1",
      "original": "과거 코드의 각 파일을 어느 BANK-OM 단계에서 복원할지 결정",
      "action": "수정",
      "final": "Git 기록은 없지만 파일은 남아 있는 당시의 코드 폴더",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25r.inputs.2.1",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.inputs.2.1",
      "original": "공식 원본과 과거 보관 소스가 다른 전체 경로",
      "action": "수정",
      "final": "각 파일에 어떤 BANK-OM 변경을 적용해야 하는지 알려주는 등록자료",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25r.steps.0",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.steps.0",
      "original": "공식 원본에서 시작해 과거 코드 파일–BANK-OM 연결표에 따라 BANK-OM 변경을 기능별로 복원합니다.",
      "action": "수정",
      "final": "공식 OpenMetadata 코드에서 시작해 파일–BANK-OM 연결표에 기록된 변경을 순서대로 적용합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25r.steps.1",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.steps.1",
      "original": "다시 만든 코드와 과거 보관 소스의 파일 목록이 같은지 확인합니다.",
      "action": "수정",
      "final": "복구한 코드와 보관 코드에 같은 파일이 있고 내용도 같은지 비교합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25r.steps.2",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.steps.2",
      "original": "JSON은 공백·줄바꿈·항목 순서가 달라도 항목 경로와 값이 같으면 같은 내용으로 판단합니다.",
      "action": "유지",
      "final": "JSON은 공백·줄바꿈·항목 순서가 달라도 항목 경로와 값이 같으면 같은 내용으로 판단합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t25r.steps.3",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.steps.3",
      "original": "Java·TypeScript·Python 등 나머지 파일은 바이트 단위 내용이 같은지 확인합니다.",
      "action": "유지",
      "final": "Java·TypeScript·Python 등 나머지 파일은 바이트 단위 내용이 같은지 확인합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t25r.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.verdicts.0.1",
      "original": "다시 만든 파일 목록과 내용이 과거 보관 소스와 같습니다.",
      "action": "수정",
      "final": "복구한 코드의 파일 목록과 내용이 보관 코드와 같습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25r.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.verdicts.1.1",
      "original": "누락·추가 파일이 있거나 파일 내용이 다릅니다.",
      "action": "유지",
      "final": "누락·추가 파일이 있거나 파일 내용이 다릅니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t25r.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.verdicts.2.1",
      "original": "공식 원본, 과거 snapshot 또는 파일–BANK-OM 연결표가 없어 재구성을 신뢰할 수 없습니다.",
      "action": "수정",
      "final": "공식 코드, 보관 코드 또는 파일–BANK-OM 연결표가 없어 비교할 수 없습니다.",
      "reason": "snapshot을 ‘과거 전체 파일 복사본’으로 설명"
    },
    {
      "id": "2|gate.t25r.limit",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.limit",
      "original": "재구성 결과가 과거 파일 상태와 같다는 사실만 확인합니다. 빈 줄 차이도 JSON 이외 파일에서는 불일치가 될 수 있으며, 기능 동작 정상은 Contract test가 따로 확인합니다.",
      "action": "수정",
      "final": "복구한 파일과 보관 파일이 같다는 사실만 확인합니다. 기능이 정상 동작하는지는 Contract test가 따로 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25r.output",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.output",
      "original": "과거 source snapshot 재구성 결과에 누락·추가·내용 불일치 경로가 남습니다. 과거 코드 복원 담당자가 Manifest와 과거 코드 파일–BANK-OM 연결표(source-snapshot-path-owners.yaml) 중 잘못된 입력을 확인합니다.",
      "action": "수정",
      "final": "결과 파일에는 누락된 파일, 추가된 파일, 내용이 다른 파일이 기록됩니다. 복구 담당자는 이 목록을 보고 등록자료나 복구 순서 중 무엇을 고쳐야 하는지 판단합니다.",
      "reason": "snapshot을 ‘과거 전체 파일 복사본’으로 설명"
    },
    {
      "id": "2|gate.t25.title",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.title",
      "original": "T25 · 공식 버전 출발점 확인",
      "action": "유지",
      "final": "T25 · 공식 버전 출발점 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t25.question",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.question",
      "original": "검사할 행내 코드가 승인한 공식 OpenMetadata 버전을 실제 Git 이력에 포함하는가?",
      "action": "수정",
      "final": "검사할 커스텀 브랜치가 우리가 선택한 공식 OpenMetadata 버전에서 만들어졌는가?",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25.status",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.status",
      "original": "구현·단위 테스트 완료 · OM_TEMP 1.13.1 결과 파일 있음(커밋별 재적용 후보)",
      "action": "수정",
      "final": "구현·단위 테스트 완료 · 현재 적용 예시: OM_TEMP 1.13.0 재검증 결과 PASS",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t25.timing",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.timing",
      "original": "vendor-merge로 공식 코드와 BANK-OM 변경을 합친 검사 대상 코드를 만든 뒤, 다른 소스 검사를 시작하기 전에 실행합니다.",
      "action": "수정",
      "final": "새 공식 버전과 BANK-OM 변경을 합쳐 커스텀 브랜치를 만든 뒤, 다른 소스 검사보다 먼저 실행합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.inputs.0.1",
      "original": "공식 새 버전 commit, 검사 대상 commit·tree와 실제 통합 방식",
      "action": "수정",
      "final": "업그레이드 전 공식 commit, 새 공식 commit, 검사할 커스텀 브랜치 commit을 기록한 검사 대상 고정 정보",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t25.inputs.0.2",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.inputs.0.2",
      "original": "현재 진단: 공식 afcb2d2… · 후보 dee330ebd5… · 커밋별 재적용",
      "action": "수정",
      "final": "공식 f329dd4a… · 검사 대상 custom commit 3a2811cf…",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t25.inputs.1.0",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.inputs.1.0",
      "original": "검사 대상 OpenMetadata Git 저장소",
      "action": "삭제",
      "final": "삭제",
      "reason": "앞뒤 내용과 중복되거나 운영 판단에 필요하지 않아 삭제"
    },
    {
      "id": "2|gate.t25.inputs.1.1",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.inputs.1.1",
      "original": "위 세 commit 객체와 Git 포함 관계를 조회할 저장소",
      "action": "수정",
      "final": "Candidate lock에 적힌 세 commit과 그 연결 순서를 확인할 Git 저장소",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25.steps.0",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.steps.0",
      "original": "Candidate lock에 적힌 공식 이전 버전, 공식 새 버전과 검사 대상 commit이 저장소에 존재하는지 확인합니다.",
      "action": "수정",
      "final": "Candidate lock에 적힌 업그레이드 전 공식 commit, 새 공식 commit과 검사할 커스텀 브랜치 commit이 실제로 존재하는지 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25.steps.1",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.steps.1",
      "original": "검사 대상 commit과 전체 파일 상태가 Candidate lock의 값과 같은지 확인합니다.",
      "action": "수정",
      "final": "Git 기록에서 업그레이드 전 공식 commit 다음에 새 공식 commit이 이어지는지 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25.steps.2",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.steps.2",
      "original": "공식 이전·새 버전에 공통 Git 이력이 있는지 확인합니다.",
      "action": "수정",
      "final": "Git 기록에서 새 공식 commit 다음에 검사할 커스텀 브랜치 commit이 이어지는지 확인합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t25.steps.3",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.steps.3",
      "original": "공식 이전 버전과 승인한 새 공식 버전이 모두 검사 대상 commit의 이력에 포함되는지 확인합니다.",
      "action": "수정",
      "final": "현재 검사 중인 커스텀 브랜치 commit과 파일 내용이 Candidate lock에 기록된 값과 같은지 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.verdicts.0.1",
      "original": "승인한 공식 새 버전이 검사 대상 이력에 포함되고 lock 값도 일치합니다.",
      "action": "수정",
      "final": "검사할 커스텀 브랜치가 선택한 새 공식 버전에서 만들어졌고 Candidate lock과도 일치합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.verdicts.1.1",
      "original": "공식 이전 또는 새 버전이 검사 대상 이력에 포함되지 않습니다.",
      "action": "수정",
      "final": "커스텀 브랜치가 선택한 공식 버전에서 만들어졌다는 Git 연결 기록이 없습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.verdicts.2.1",
      "original": "commit 객체가 없거나 lock 값이 현재 코드와 달라 신뢰할 수 있는 판단을 할 수 없습니다.",
      "action": "수정",
      "final": "필요한 commit이 없거나 현재 코드와 Candidate lock이 달라 검사를 완료할 수 없습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25.limit",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.limit",
      "original": "공식 코드를 포함했다는 사실만 확인합니다. 병합 과정에서 BANK-OM 기능이 올바르게 유지됐는지는 T26과 실제 테스트가 따로 확인합니다.",
      "action": "수정",
      "final": "커스텀 브랜치의 출발점만 확인합니다. BANK-OM 기능이 남아 있고 정상 동작하는지는 T26과 기능 test가 따로 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t25.output",
      "chapter": "2",
      "page": "상세 · T25 · 공식 버전 출발점 확인",
      "location": "gate.t25.output",
      "original": "통합 소스 검사 결과 source-gate-results.json의 T25 항목에 판정과 이유가 남습니다. 업그레이드 담당자와 검토 책임자가 공식 버전 출발점이 맞는지 확인합니다.",
      "action": "수정",
      "final": "source-gate-results.json의 T25 항목에 PASS·BLOCK·ANALYSIS ERROR와 그 이유가 기록됩니다. 담당자는 이 결과로 잘못된 공식 버전에서 만든 커스텀 브랜치를 검사하는 실수를 찾습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t26.title",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.title",
      "original": "T26 · 필수 커스터마이징 유지 확인",
      "action": "유지",
      "final": "T26 · 필수 커스터마이징 유지 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t26.question",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.question",
      "original": "공식 새 버전을 적용한 뒤에도 모든 active BANK-OM 기능의 필수 코드와 Contract 연결이 남아 있는가?",
      "action": "유지",
      "final": "공식 새 버전을 적용한 뒤에도 모든 active BANK-OM 기능의 필수 코드와 Contract 연결이 남아 있는가?",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t26.status",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.status",
      "original": "구현·단위 테스트 완료 · OM_TEMP 1.13.1 결과 파일 있음(커밋별 재적용 후보)",
      "action": "수정",
      "final": "구현·단위 테스트 완료 · 현재 적용 예시: OM_TEMP 1.13.0 재검증 결과 PASS",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t26.timing",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.timing",
      "original": "vendor-merge 후보가 만들어지고 Manifest·Registry·Contract가 준비된 뒤 실행합니다.",
      "action": "수정",
      "final": "vendor-merge 결과가 되는 검사 대상 custom branch commit이 만들어지고 Manifest·Registry·Contract가 준비된 뒤 실행합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t26.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.inputs.0.1",
      "original": "공식 새 버전과 검사 대상 commit",
      "action": "수정",
      "final": "공식 버전과 검사 대상 custom branch commit",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t26.inputs.0.2",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.inputs.0.2",
      "original": "공식 afcb2d2… · 진단 후보 dee330ebd5…",
      "action": "수정",
      "final": "공식 f329dd4a… · 검사 대상 custom commit 3a2811cf…",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t26.inputs.1.1",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.inputs.1.1",
      "original": "required_changed_paths, 전체 기대 경로, assurance",
      "action": "유지",
      "final": "required_changed_paths, 전체 기대 경로, assurance",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t26.inputs.2.1",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.inputs.2.1",
      "original": "active ID와 Contract·필수 test 연결",
      "action": "유지",
      "final": "active ID와 Contract·필수 test 연결",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t26.steps.0",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.steps.0",
      "original": "Registry에서 active BANK-OM ID를 가져옵니다.",
      "action": "유지",
      "final": "Registry에서 active BANK-OM ID를 가져옵니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t26.steps.1",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.steps.1",
      "original": "각 ID의 Manifest와 required_changed_paths가 비어 있지 않은지 확인합니다.",
      "action": "유지",
      "final": "각 ID의 Manifest와 required_changed_paths가 비어 있지 않은지 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t26.steps.2",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.steps.2",
      "original": "필수 파일이 검사 대상 코드에 존재하고 공식 새 버전과 실제로 다른지 확인합니다.",
      "action": "유지",
      "final": "필수 파일이 검사 대상 코드에 존재하고 공식 새 버전과 실제로 다른지 확인합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t26.steps.3",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.steps.3",
      "original": "필수 이외의 등록 파일이 사라졌거나 공식 원본과 같아졌다면 담당자 검토 대상으로 표시합니다.",
      "action": "유지",
      "final": "필수 이외의 등록 파일이 사라졌거나 공식 원본과 같아졌다면 담당자 검토 대상으로 표시합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t26.steps.4",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.steps.4",
      "original": "Contract가 존재하고 같은 BANK-OM ID를 역방향으로 참조하며 필수 test로 연결되는지 확인합니다.",
      "action": "수정",
      "final": "Manifest가 가리키는 Contract가 실제로 있고, 그 Contract에도 같은 BANK-OM ID와 필수 test가 적혀 있는지 확인합니다.",
      "reason": "‘양방향·역방향’ 대신 서로 확인하는 두 항목을 직접 명시"
    },
    {
      "id": "2|gate.t26.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.verdicts.0.1",
      "original": "모든 active 기능의 필수 코드와 Contract·test 연결이 확인됩니다.",
      "action": "유지",
      "final": "모든 active 기능의 필수 코드와 Contract·test 연결이 확인됩니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t26.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.verdicts.1.1",
      "original": "필수로 지정하지 않은 등록 파일이 사라졌거나 공식 코드와 같아져 담당자 확인이 필요합니다.",
      "action": "유지",
      "final": "필수로 지정하지 않은 등록 파일이 사라졌거나 공식 코드와 같아져 담당자 확인이 필요합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t26.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.verdicts.2.1",
      "original": "필수 파일, Manifest, Contract 또는 필수 test 연결이 없습니다.",
      "action": "유지",
      "final": "필수 파일, Manifest, Contract 또는 필수 test 연결이 없습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t26.verdicts.3.1",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.verdicts.3.1",
      "original": "검사 대상 commit이나 Candidate lock을 신뢰할 수 없어 검사할 수 없습니다.",
      "action": "유지",
      "final": "검사 대상 commit이나 Candidate lock을 신뢰할 수 없어 검사할 수 없습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t26.limit",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.limit",
      "original": "필수 파일이 존재하고 공식 원본과 다르다는 사실을 확인할 뿐, 그 코드가 올바르게 동작한다는 뜻은 아닙니다. T62 실행 결과가 필요합니다.",
      "action": "유지",
      "final": "필수 파일이 존재하고 공식 원본과 다르다는 사실을 확인할 뿐, 그 코드가 올바르게 동작한다는 뜻은 아닙니다. T62 실행 결과가 필요합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t26.output",
      "chapter": "2",
      "page": "상세 · T26 · 필수 커스터마이징 유지 확인",
      "location": "gate.t26.output",
      "original": "통합 소스 검사 결과 source-gate-results.json의 T26 항목에 기능별 누락 여부가 남습니다. 기능 담당자와 배포 검토자가 BLOCK·APPROVAL 사유를 확인합니다.",
      "action": "유지",
      "final": "통합 소스 검사 결과 source-gate-results.json의 T26 항목에 기능별 누락 여부가 남습니다. 기능 담당자와 배포 검토자가 BLOCK·APPROVAL 사유를 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t30.title",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.title",
      "original": "T30 · 커밋별 BANK-OM ID 확인",
      "action": "유지",
      "final": "T30 · 커밋별 BANK-OM ID 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t30.question",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.question",
      "original": "공식 코드 영역을 변경한 각 commit에 정확히 하나의 등록된 BANK-OM ID가 있는가?",
      "action": "유지",
      "final": "공식 코드 영역을 변경한 각 commit에 정확히 하나의 등록된 BANK-OM ID가 있는가?",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t30.status",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.status",
      "original": "구현·단위 테스트 완료 · OM_TEMP 1.13.1 결과 파일 있음",
      "action": "수정",
      "final": "구현·단위 테스트 완료 · 현재 적용 예시: OM_TEMP 1.13.0 재검증 결과 PASS",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t30.timing",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.timing",
      "original": "BANK-OM commit이 추가될 때마다, 소스 후보 검사에서 실행합니다.",
      "action": "수정",
      "final": "BANK-OM commit이 추가될 때마다, 검사 대상 custom branch commit에 대한 소스 검사에서 실행합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t30.inputs.0.0",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.inputs.0.0",
      "original": "Git commit 이력",
      "action": "유지",
      "final": "Git commit 이력",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t30.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.inputs.0.1",
      "original": "공식 기준 이후의 각 commit 메시지와 변경 파일",
      "action": "유지",
      "final": "공식 기준 이후의 각 commit 메시지와 변경 파일",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t30.inputs.0.2",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.inputs.0.2",
      "original": "7d19c895… 본문: Customization-ID: BANK-OM-007",
      "action": "유지",
      "final": "7d19c895… 본문: Customization-ID: BANK-OM-007",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t30.inputs.1.1",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.inputs.1.1",
      "original": "공식 코드·행내 거버넌스·알 수 없는 경로의 구분",
      "action": "유지",
      "final": "공식 코드·행내 거버넌스·알 수 없는 경로의 구분",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t30.inputs.1.2",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.inputs.1.2",
      "original": "openmetadata-ui/** = 공식 코드 영역",
      "action": "유지",
      "final": "openmetadata-ui/** = 공식 코드 영역",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t30.inputs.2.1",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.inputs.2.1",
      "original": "사용 가능한 BANK-OM ID",
      "action": "유지",
      "final": "사용 가능한 BANK-OM ID",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t30.steps.0",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.steps.0",
      "original": "공식 기준 이후의 commit을 하나씩 읽습니다.",
      "action": "유지",
      "final": "공식 기준 이후의 commit을 하나씩 읽습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t30.steps.1",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.steps.1",
      "original": "각 commit에서 변경된 경로를 공식 코드, 거버넌스 코드 또는 알 수 없는 경로로 분류합니다.",
      "action": "유지",
      "final": "각 commit에서 변경된 경로를 공식 코드, 거버넌스 코드 또는 알 수 없는 경로로 분류합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t30.steps.2",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.steps.2",
      "original": "공식 코드 경로를 바꾼 commit의 본문에서 Customization-ID 항목을 읽습니다.",
      "action": "유지",
      "final": "공식 코드 경로를 바꾼 commit의 본문에서 Customization-ID 항목을 읽습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t30.steps.3",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.steps.3",
      "original": "ID가 없거나 여러 개인지, 공식 코드와 거버넌스 코드를 한 commit에 섞었는지 확인합니다.",
      "action": "유지",
      "final": "ID가 없거나 여러 개인지, 공식 코드와 거버넌스 코드를 한 commit에 섞었는지 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t30.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.verdicts.0.1",
      "original": "공식 코드를 변경한 각 commit에 정확히 하나의 ID가 있습니다.",
      "action": "유지",
      "final": "공식 코드를 변경한 각 commit에 정확히 하나의 ID가 있습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t30.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.verdicts.1.1",
      "original": "ID 누락·중복, 빈 commit, 허용하지 않은 merge commit 또는 코드 영역 혼합이 있습니다.",
      "action": "유지",
      "final": "ID 누락·중복, 빈 commit, 허용하지 않은 merge commit 또는 코드 영역 혼합이 있습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t30.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.verdicts.2.1",
      "original": "어느 영역인지 판단할 수 없는 경로가 있습니다.",
      "action": "유지",
      "final": "어느 영역인지 판단할 수 없는 경로가 있습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t30.limit",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.limit",
      "original": "ID가 있다고 해서 commit의 업무 목적이 한 가지라는 사실까지 자동으로 알 수는 없습니다. commit 리뷰가 필요합니다.",
      "action": "유지",
      "final": "ID가 있다고 해서 commit의 업무 목적이 한 가지라는 사실까지 자동으로 알 수는 없습니다. commit 리뷰가 필요합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t30.output",
      "chapter": "2",
      "page": "상세 · T30 · 커밋별 BANK-OM ID 확인",
      "location": "gate.t30.output",
      "original": "통합 소스 검사 결과 source-gate-results.json의 T30 항목에 문제가 있는 commit과 ID가 남습니다. 변경 작성자와 변경관리 담당자가 commit 메시지를 수정할지 판단합니다.",
      "action": "유지",
      "final": "통합 소스 검사 결과 source-gate-results.json의 T30 항목에 문제가 있는 commit과 ID가 남습니다. 변경 작성자와 변경관리 담당자가 commit 메시지를 수정할지 판단합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t31.title",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.title",
      "original": "T31 · BANK-OM 적용 순서 확인",
      "action": "유지",
      "final": "T31 · BANK-OM 적용 순서 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t31.question",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.question",
      "original": "같은 ID의 여러 commit과 기능 간 선행 관계가 Manifest에 등록한 순서를 지키는가?",
      "action": "유지",
      "final": "같은 ID의 여러 commit과 기능 간 선행 관계가 Manifest에 등록한 순서를 지키는가?",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t31.status",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.status",
      "original": "구현·단위 테스트 완료 · OM_TEMP 1.13.1 결과 파일 있음",
      "action": "수정",
      "final": "구현·단위 테스트 완료 · 현재 적용 예시: OM_TEMP 1.13.0 재검증 결과 PASS",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t31.timing",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.timing",
      "original": "같은 BANK-OM ID의 후속 commit이나 depends_on 관계가 추가될 때 실행합니다.",
      "action": "유지",
      "final": "같은 BANK-OM ID의 후속 commit이나 depends_on 관계가 추가될 때 실행합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t31.inputs.0.0",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.inputs.0.0",
      "original": "Git commit 이력",
      "action": "유지",
      "final": "Git commit 이력",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t31.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.inputs.0.1",
      "original": "commit별 Customization-ID와 순서",
      "action": "유지",
      "final": "commit별 Customization-ID와 순서",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t31.inputs.0.2",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.inputs.0.2",
      "original": "62e39da8… → 7d19c895… 모두 BANK-OM-007",
      "action": "유지",
      "final": "62e39da8… → 7d19c895… 모두 BANK-OM-007",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t31.inputs.1.1",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.inputs.1.1",
      "original": "series.allowed와 series.depends_on",
      "action": "유지",
      "final": "series.allowed와 series.depends_on",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t31.inputs.2.1",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.inputs.2.1",
      "original": "active·retired ID 상태",
      "action": "유지",
      "final": "active·retired ID 상태",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t31.steps.0",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.steps.0",
      "original": "commit을 BANK-OM ID별로 묶습니다.",
      "action": "유지",
      "final": "commit을 BANK-OM ID별로 묶습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t31.steps.1",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.steps.1",
      "original": "한 ID가 여러 commit에 쓰였다면 series.allowed가 true인지 확인합니다.",
      "action": "유지",
      "final": "한 ID가 여러 commit에 쓰였다면 series.allowed가 true인지 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t31.steps.2",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.steps.2",
      "original": "같은 ID의 commit이 중간에 다른 ID로 끊겼다가 다시 나타나는지 확인합니다.",
      "action": "유지",
      "final": "같은 ID의 commit이 중간에 다른 ID로 끊겼다가 다시 나타나는지 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t31.steps.3",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.steps.3",
      "original": "depends_on 관계에 순환이 있는지와 retired ID가 재사용됐는지 확인합니다.",
      "action": "유지",
      "final": "depends_on 관계에 순환이 있는지와 retired ID가 재사용됐는지 확인합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t31.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.verdicts.0.1",
      "original": "후속 commit과 선행 관계가 등록 규칙을 지킵니다.",
      "action": "유지",
      "final": "후속 commit과 선행 관계가 등록 규칙을 지킵니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t31.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.verdicts.1.1",
      "original": "승인되지 않은 여러 commit, 비연속 series, 의존 관계 순환 또는 retired ID 재사용이 있습니다.",
      "action": "유지",
      "final": "승인되지 않은 여러 commit, 비연속 series, 의존 관계 순환 또는 retired ID 재사용이 있습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t31.limit",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.limit",
      "original": "Manifest에 선행 관계 자체를 빠뜨리면 검사기가 업무 관계를 새로 추론하지 못합니다.",
      "action": "유지",
      "final": "Manifest에 선행 관계 자체를 빠뜨리면 검사기가 업무 관계를 새로 추론하지 못합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t31.output",
      "chapter": "2",
      "page": "상세 · T31 · BANK-OM 적용 순서 확인",
      "location": "gate.t31.output",
      "original": "통합 소스 검사 결과 source-gate-results.json의 T31 항목에 적용 순서·revision 위반이 남습니다. 변경관리 담당자가 Manifest 또는 Patch-lock 순서를 확인합니다.",
      "action": "수정",
      "final": "source-gate-results.json의 T31 항목에는 잘못된 적용 순서와 후속 변경 묶음 번호가 기록됩니다. 변경관리 담당자는 Manifest를 확인하고, patch-replay 전략을 쓰는 경우에만 Patch-lock도 확인합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t40.title",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.title",
      "original": "T40 · 변경 파일 범위 확인",
      "action": "유지",
      "final": "T40 · 변경 파일 범위 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t40.question",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.question",
      "original": "각 BANK-OM commit이 Manifest에 등록한 파일만 변경했고, 최종 후보에 필수 변경이 반영됐는가?",
      "action": "수정",
      "final": "각 BANK-OM commit이 Manifest에 등록한 파일만 변경했고, 최종 검사 대상 custom branch commit에 필수 변경이 반영됐는가?",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t40.status",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.status",
      "original": "구현·단위 테스트 완료 · OM_TEMP 1.13.1 결과 파일 있음",
      "action": "수정",
      "final": "구현·단위 테스트 완료 · 현재 적용 예시: OM_TEMP 1.13.0 재검증 결과 PASS",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t40.timing",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.timing",
      "original": "Manifest 초안을 만든 뒤와 새로운 후속 commit이 추가될 때마다 실행합니다.",
      "action": "유지",
      "final": "Manifest 초안을 만든 뒤와 새로운 후속 commit이 추가될 때마다 실행합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t40.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.inputs.0.1",
      "original": "BANK-OM commit별 실제 변경 파일과 최종 후보의 공식 원본 대비 차이",
      "action": "수정",
      "final": "BANK-OM commit별 실제 변경 파일과 최종 검사 대상 custom branch commit의 공식 원본 대비 차이",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t40.inputs.0.2",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.inputs.0.2",
      "original": "BANK-OM-007 두 commit의 8개 + 2개 파일",
      "action": "유지",
      "final": "BANK-OM-007 두 commit의 8개 + 2개 파일",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t40.inputs.1.2",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.inputs.1.2",
      "original": "changed_paths 10개 · required .../tiberoConnection.json",
      "action": "유지",
      "final": "changed_paths 10개 · required .../tiberoConnection.json",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t40.steps.0",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.steps.0",
      "original": "commit별 실제 변경 파일과 Manifest의 현재 변경 범위를 비교합니다.",
      "action": "유지",
      "final": "commit별 실제 변경 파일과 Manifest의 현재 변경 범위를 비교합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t40.steps.1",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.steps.1",
      "original": "Manifest에 없는 파일을 commit이 변경했는지 확인합니다.",
      "action": "유지",
      "final": "Manifest에 없는 파일을 commit이 변경했는지 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t40.steps.2",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.steps.2",
      "original": "required_changed_paths가 현재 변경 범위에 포함되는지 확인합니다.",
      "action": "유지",
      "final": "required_changed_paths가 현재 변경 범위에 포함되는지 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t40.steps.3",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.steps.3",
      "original": "최종 후보에서 필수 파일이 공식 새 버전과 실제로 다른지 확인합니다.",
      "action": "수정",
      "final": "최종 검사 대상 custom branch commit에서 필수 파일이 공식 새 버전과 실제로 다른지 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t40.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.verdicts.0.1",
      "original": "실제 변경 파일이 등록 범위와 같고 필수 변경이 최종 후보에 있습니다.",
      "action": "수정",
      "final": "실제 변경 파일이 등록 범위와 같고 필수 변경이 최종 검사 대상 custom branch commit에 있습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t40.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.verdicts.1.1",
      "original": "Manifest에는 등록했지만 실제 commit에서 변경하지 않은 비필수 파일이 있습니다.",
      "action": "유지",
      "final": "Manifest에는 등록했지만 실제 commit에서 변경하지 않은 비필수 파일이 있습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t40.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.verdicts.2.1",
      "original": "등록하지 않은 파일을 변경했거나 필수 변경이 최종 후보에 없습니다.",
      "action": "수정",
      "final": "등록하지 않은 파일을 변경했거나 필수 변경이 최종 검사 대상 custom branch commit에 없습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t40.verdicts.3.1",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.verdicts.3.1",
      "original": "변경 파일이 어느 코드 영역에 속하는지 판정할 수 없습니다.",
      "action": "유지",
      "final": "변경 파일이 어느 코드 영역에 속하는지 판정할 수 없습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t40.limit",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.limit",
      "original": "파일 단위 검사입니다. 허용된 파일 안의 잘못된 코드 줄은 코드 리뷰와 test로 확인해야 합니다.",
      "action": "유지",
      "final": "파일 단위 검사입니다. 허용된 파일 안의 잘못된 코드 줄은 코드 리뷰와 test로 확인해야 합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t40.output",
      "chapter": "2",
      "page": "상세 · T40 · 변경 파일 범위 확인",
      "location": "gate.t40.output",
      "original": "통합 소스 검사 결과 source-gate-results.json의 T40 항목에 등록 밖 변경과 누락된 필수 경로가 남습니다. 기능 담당자가 코드와 Manifest 중 잘못된 쪽을 고칩니다.",
      "action": "유지",
      "final": "통합 소스 검사 결과 source-gate-results.json의 T40 항목에 등록 밖 변경과 누락된 필수 경로가 남습니다. 기능 담당자가 코드와 Manifest 중 잘못된 쪽을 고칩니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t41.title",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.title",
      "original": "T41 · 중요 시스템 경로 확인",
      "action": "유지",
      "final": "T41 · 중요 시스템 경로 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t41.question",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.question",
      "original": "보안·인증·설정·DB처럼 별도 검토가 필요한 경로를 BANK-OM commit이 변경했는가?",
      "action": "유지",
      "final": "보안·인증·설정·DB처럼 별도 검토가 필요한 경로를 BANK-OM commit이 변경했는가?",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t41.status",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.status",
      "original": "구현·단위 테스트 완료 · OM_TEMP 1.13.1 결과 파일 있음",
      "action": "수정",
      "final": "검사 구현·단위 테스트 완료 · 1.13.0 소스 재검사 결과는 PASS · 1.13.1 운영 배포 대상 코드는 재검증 필요",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t41.timing",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.timing",
      "original": "소스 후보 검사에서 실제 변경 파일을 분류할 때 실행합니다.",
      "action": "수정",
      "final": "검사 대상 custom branch commit의 소스 검사에서 실제 변경 파일을 분류할 때 실행합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t41.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.inputs.0.1",
      "original": "공식 기준 이후 BANK-OM commit의 경로",
      "action": "유지",
      "final": "공식 기준 이후 BANK-OM commit의 경로",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t41.inputs.1.1",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.inputs.1.1",
      "original": "frozen, protected, watched 경로 규칙",
      "action": "수정",
      "final": "변경 금지(frozen), 사전 승인 필요(protected), 결과 표시 필요(watched) 경로",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t41.inputs.2.1",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.inputs.2.1",
      "original": "허용된 중요 변경 사유와 승인 정보가 있는 경우",
      "action": "유지",
      "final": "허용된 중요 변경 사유와 승인 정보가 있는 경우",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t41.inputs.2.2",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.inputs.2.2",
      "original": "BANK-OM-001 schema migration 승인 참조",
      "action": "유지",
      "final": "BANK-OM-001 schema migration 승인 참조",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t41.steps.0",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.steps.0",
      "original": "변경 파일을 Sensitive zones 규칙과 비교합니다.",
      "action": "수정",
      "final": "변경 파일을 중요 경로 정책과 비교합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t41.steps.1",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.steps.1",
      "original": "frozen, protected, watched 중 어느 분류에 속하는지 확인합니다.",
      "action": "수정",
      "final": "변경 금지, 사전 승인 필요, 결과 표시 필요 중 어디에 해당하는지 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t41.steps.2",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.steps.2",
      "original": "필요한 change intent 또는 승인 정보가 있는지 확인합니다.",
      "action": "수정",
      "final": "사전 승인이 필요한 변경이라면 변경 사유와 승인 정보가 있는지 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t41.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.verdicts.0.1",
      "original": "중요 경로 변경이 없거나 필요한 조건을 충족했습니다.",
      "action": "유지",
      "final": "중요 경로 변경이 없거나 필요한 조건을 충족했습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t41.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.verdicts.1.1",
      "original": "protected·watched 경로 변경으로 담당자 검토가 필요합니다.",
      "action": "수정",
      "final": "사전 승인 또는 결과 표시가 필요한 경로를 변경해 담당자 검토가 필요합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t41.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.verdicts.2.1",
      "original": "frozen 경로를 변경했거나 필수 승인 조건을 충족하지 못했습니다.",
      "action": "수정",
      "final": "변경 금지 경로를 수정했거나 필요한 승인 정보를 제출하지 않았습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t41.verdicts.3.1",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.verdicts.3.1",
      "original": "경로를 규칙에 따라 분류할 수 없습니다.",
      "action": "유지",
      "final": "경로를 규칙에 따라 분류할 수 없습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t41.limit",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.limit",
      "original": "경로 이름을 기준으로 판정하며 AST나 보안 취약점 분석을 수행하지 않습니다.",
      "action": "수정",
      "final": "파일 경로만 비교합니다. 코드 내부 구조를 분석하거나 보안 취약점을 찾지는 않습니다.",
      "reason": "AST가 하는 일을 ‘Python 함수 이름을 읽는 분석’으로 설명"
    },
    {
      "id": "2|gate.t41.output",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.output",
      "original": "통합 소스 검사 결과 source-gate-results.json의 T41 항목에 민감 경로와 필요한 승인 수준이 남습니다. 보안·DB·플랫폼 담당자 중 해당 경로 책임자가 확인합니다.",
      "action": "유지",
      "final": "통합 소스 검사 결과 source-gate-results.json의 T41 항목에 민감 경로와 필요한 승인 수준이 남습니다. 보안·DB·플랫폼 담당자 중 해당 경로 책임자가 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t42.title",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.title",
      "original": "T42 · 공식 변경 영향 확인",
      "action": "유지",
      "final": "T42 · 공식 변경 영향 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t42.question",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.question",
      "original": "새 공식 OpenMetadata 버전이 BANK-OM 기능과 관련된 파일을 변경했는가?",
      "action": "유지",
      "final": "새 공식 OpenMetadata 버전이 BANK-OM 기능과 관련된 파일을 변경했는가?",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t42.status",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.status",
      "original": "구현·단위 테스트 완료 · OM_TEMP 1.13.1 영향 검사 결과 있음",
      "action": "수정",
      "final": "검사 구현·단위 테스트 완료 · 1.13.1 영향 진단 기록 있음 · 실제 운영 배포 대상 custom branch를 병합하기 전에 재실행 필요",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t42.timing",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.timing",
      "original": "새 공식 버전을 patch branch에 준비한 뒤, 커스터마이징 병합 전에 실행합니다.",
      "action": "수정",
      "final": "새 공식 버전을 OpenMetadata 포크 브랜치에 준비한 뒤, 커스터마이징 병합 전에 실행합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t42.inputs.0.0",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.inputs.0.0",
      "original": "공식 이전·새 버전 commit",
      "action": "유지",
      "final": "공식 이전·새 버전 commit",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t42.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.inputs.0.1",
      "original": "공식 A→B 사이의 Git 변경 파일",
      "action": "유지",
      "final": "공식 A→B 사이의 Git 변경 파일",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t42.inputs.1.1",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.inputs.1.1",
      "original": "upgrade_watch.paths와 watch_dependencies",
      "action": "유지",
      "final": "upgrade_watch.paths와 watch_dependencies",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t42.inputs.2.1",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.inputs.2.1",
      "original": "watch_suggest.py가 발견한 담당자 검토용 후보",
      "action": "수정",
      "final": "watch_suggest.py가 발견해 담당자에게 검토를 요청하는 경로",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t42.inputs.2.2",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.inputs.2.2",
      "original": ".../SearchIndexFactory.java · InstanceCode 참조",
      "action": "유지",
      "final": ".../SearchIndexFactory.java · InstanceCode 참조",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t42.steps.0",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.steps.0",
      "original": "Git에서 공식 이전 버전과 새 버전 사이의 변경 파일 목록을 구합니다.",
      "action": "유지",
      "final": "Git에서 공식 이전 버전과 새 버전 사이의 변경 파일 목록을 구합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t42.steps.1",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.steps.1",
      "original": "각 Manifest의 upgrade_watch.paths와 공식 변경 파일을 비교합니다.",
      "action": "유지",
      "final": "각 Manifest의 upgrade_watch.paths와 공식 변경 파일을 비교합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t42.steps.2",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.steps.2",
      "original": "겹친 경로가 있으면 BANK-OM ID와 검토할 경로를 결과에 기록합니다.",
      "action": "유지",
      "final": "겹친 경로가 있으면 BANK-OM ID와 검토할 경로를 결과에 기록합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t42.steps.3",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.steps.3",
      "original": "직접 참조 후보는 자동 승인하지 않고 담당자에게 제시합니다.",
      "action": "수정",
      "final": "직접 참조 가능성이 있는 경로는 자동 승인하지 않고 담당자에게 제시합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t42.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.verdicts.0.1",
      "original": "등록된 관련 경로가 공식 버전에서 바뀌지 않았습니다.",
      "action": "유지",
      "final": "등록된 관련 경로가 공식 버전에서 바뀌지 않았습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t42.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.verdicts.1.1",
      "original": "관련 경로가 공식 버전에서도 변경돼 재적용 전 검토가 필요합니다.",
      "action": "유지",
      "final": "관련 경로가 공식 버전에서도 변경돼 재적용 전 검토가 필요합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t42.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.verdicts.2.1",
      "original": "공식 commit 또는 경로 규칙을 읽지 못했습니다.",
      "action": "유지",
      "final": "공식 commit 또는 경로 규칙을 읽지 못했습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t42.limit",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.limit",
      "original": "APPROVAL은 Git 충돌 확정이 아닙니다. 경로가 겹치지 않는 간접 런타임 의존도 자동으로 모두 찾지 못합니다.",
      "action": "수정",
      "final": "APPROVAL은 Git 충돌이 이미 발생했다는 뜻이 아닙니다. 파일 경로는 다르지만 실행 중 서로 연결되는 코드까지 모두 찾지는 못합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t42.output",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.output",
      "original": "upgrade-watch-results.json의 T42 판정과 affected_customizations에 BANK-OM ID와 겹친 경로가 남습니다. 기능 담당자가 공식 diff와 커스터마이징 연결 부분을 확인합니다.",
      "action": "수정",
      "final": "upgrade-watch-results.json의 affected_customizations에는 영향받을 수 있는 BANK-OM ID와 공식 버전에서도 바뀐 경로가 기록됩니다. 기능 담당자는 공식 변경 내용과 커스터마이징 연결 부분을 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t43.title",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.title",
      "original": "T43 · 커스터마이징 유지 부담 확인",
      "action": "유지",
      "final": "T43 · 커스터마이징 유지 부담 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t43.question",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.question",
      "original": "커스터마이징 규모와 공유 파일·충돌률이 조직이 정한 유지 한도를 넘었는가?",
      "action": "유지",
      "final": "커스터마이징 규모와 공유 파일·충돌률이 조직이 정한 유지 한도를 넘었는가?",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t43.status",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.status",
      "original": "검사 구현 완료 · 실제 충돌 증거 자동 연결은 보완 대상",
      "action": "유지",
      "final": "검사 구현 완료 · 실제 충돌 증거 자동 연결은 보완 대상",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t43.timing",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.timing",
      "original": "새 공식 버전과의 영향·충돌 분석이 끝난 뒤 실행합니다.",
      "action": "유지",
      "final": "새 공식 버전과의 영향·충돌 분석이 끝난 뒤 실행합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t43.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.inputs.0.1",
      "original": "활성 기능 수, 변경 줄 수, 한 파일을 함께 수정한 BANK-OM ID의 최대 수",
      "action": "유지",
      "final": "활성 기능 수, 변경 줄 수, 한 파일을 함께 수정한 BANK-OM ID의 최대 수",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t43.inputs.0.2",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.inputs.0.2",
      "original": "기준 후보 예시: Core 변경 11개 · 12,488줄 · 한 파일에 연결된 ID 최대 4개",
      "action": "수정",
      "final": "비교 기준 검사 대상 코드 예시: Core 변경 11개 · 12,488줄 · 한 파일에 연결된 ID 최대 4개",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t43.inputs.1.2",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.inputs.1.2",
      "original": "변경 줄 수 soft 14,000 · hard 18,000",
      "action": "유지",
      "final": "변경 줄 수 soft 14,000 · hard 18,000",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t43.inputs.2.1",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.inputs.2.1",
      "original": "현재는 실행 인자로 전달하며 실제 병합 결과 자동 계산은 추가 개발 대상",
      "action": "유지",
      "final": "현재는 실행 인자로 전달하며 실제 병합 결과 자동 계산은 추가 개발 대상",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t43.inputs.2.2",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.inputs.2.2",
      "original": "예시 입력: --conflict-rate 0.12",
      "action": "유지",
      "final": "예시 입력: --conflict-rate 0.12",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t43.steps.0",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.steps.0",
      "original": "활성 커스터마이징 수와 실제 변경 줄 수를 계산합니다.",
      "action": "유지",
      "final": "활성 커스터마이징 수와 실제 변경 줄 수를 계산합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t43.steps.1",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.steps.1",
      "original": "여러 BANK-OM이 함께 수정한 파일 수를 계산합니다.",
      "action": "유지",
      "final": "여러 BANK-OM이 함께 수정한 파일 수를 계산합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t43.steps.2",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.steps.2",
      "original": "전달받은 충돌률과 각 값을 정책 한도와 비교합니다.",
      "action": "유지",
      "final": "전달받은 충돌률과 각 값을 정책 한도와 비교합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t43.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.verdicts.0.1",
      "original": "모든 유지 부담 지표가 허용 범위입니다.",
      "action": "유지",
      "final": "모든 유지 부담 지표가 허용 범위입니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t43.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.verdicts.1.1",
      "original": "경고 한도를 넘어 구조 개선 검토가 필요합니다.",
      "action": "유지",
      "final": "경고 한도를 넘어 구조 개선 검토가 필요합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t43.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.verdicts.2.1",
      "original": "조직이 정한 차단 한도를 넘었습니다.",
      "action": "유지",
      "final": "조직이 정한 차단 한도를 넘었습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t43.verdicts.3.1",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.verdicts.3.1",
      "original": "필요한 diff나 정책 값을 계산할 수 없습니다.",
      "action": "유지",
      "final": "필요한 diff나 정책 값을 계산할 수 없습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t43.limit",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.limit",
      "original": "현재 충돌률을 실제 vendor-merge 기록에서 자동 계산하지 않으므로, 전달한 값의 출처를 별도 증거로 확인해야 합니다.",
      "action": "유지",
      "final": "현재 충돌률을 실제 vendor-merge 기록에서 자동 계산하지 않으므로, 전달한 값의 출처를 별도 증거로 확인해야 합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t43.output",
      "chapter": "2",
      "page": "상세 · T43 · 커스터마이징 유지 부담 확인",
      "location": "gate.t43.output",
      "original": "업그레이드 위험 검사 JSON의 T43 항목과 debt_metrics에 계산값과 기준 초과 이유가 남습니다. 기술 책임자가 유지 부담을 수용할지 구조 개선할지 결정합니다.",
      "action": "유지",
      "final": "업그레이드 위험 검사 JSON의 T43 항목과 debt_metrics에 계산값과 기준 초과 이유가 남습니다. 기술 책임자가 유지 부담을 수용할지 구조 개선할지 결정합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t93_scope.title",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.title",
      "original": "T93-범위 · 실제 변경과 Manifest 일치 확인",
      "action": "유지",
      "final": "T93-범위 · 실제 변경과 Manifest 일치 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t93_scope.question",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.question",
      "original": "BANK-OM ID별 실제 변경 파일이 Manifest에 빠짐없이 정확하게 등록됐는가?",
      "action": "유지",
      "final": "BANK-OM ID별 실제 변경 파일이 Manifest에 빠짐없이 정확하게 등록됐는가?",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t93_scope.status",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.status",
      "original": "구현·단위 테스트 완료 · OM_TEMP 1.13.1 결과 파일 있음",
      "action": "수정",
      "final": "구현·단위 테스트 완료 · 현재 적용 예시: OM_TEMP 1.13.0 재검증 결과 PASS",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t93_scope.timing",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.timing",
      "original": "Manifest 생성·갱신 직후와 소스 후보 검사 때 실행합니다.",
      "action": "수정",
      "final": "Manifest 생성·갱신 직후와 검사 대상 custom branch commit의 소스 검사 때 실행합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t93_scope.inputs.0.0",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.inputs.0.0",
      "original": "Git commit 이력",
      "action": "유지",
      "final": "Git commit 이력",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t93_scope.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.inputs.0.1",
      "original": "BANK-OM ID별 실제 변경 파일",
      "action": "유지",
      "final": "BANK-OM ID별 실제 변경 파일",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t93_scope.inputs.0.2",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.inputs.0.2",
      "original": "BANK-OM-007: 62e39da8… 8개 + 7d19c895… 2개",
      "action": "유지",
      "final": "BANK-OM-007: 62e39da8… 8개 + 7d19c895… 2개",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t93_scope.inputs.1.2",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.inputs.1.2",
      "original": "BANK-OM-007 changed_paths 10개",
      "action": "유지",
      "final": "BANK-OM-007 changed_paths 10개",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t93_scope.steps.0",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.steps.0",
      "original": "commit 메시지의 BANK-OM ID로 실제 변경 파일을 묶습니다.",
      "action": "유지",
      "final": "commit 메시지의 BANK-OM ID로 실제 변경 파일을 묶습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t93_scope.steps.1",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.steps.1",
      "original": "같은 ID의 모든 commit에서 나온 경로 합집합과 Manifest changed_paths를 비교합니다.",
      "action": "유지",
      "final": "같은 ID의 모든 commit에서 나온 경로 합집합과 Manifest changed_paths를 비교합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t93_scope.steps.2",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.steps.2",
      "original": "실제 경로와 등록 경로가 양방향으로 같은지 확인합니다.",
      "action": "수정",
      "final": "실제 변경했지만 등록하지 않은 경로와, 등록했지만 실제로 변경하지 않은 경로를 모두 확인합니다.",
      "reason": "‘양방향·역방향’ 대신 서로 확인하는 두 항목을 직접 명시"
    },
    {
      "id": "2|gate.t93_scope.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.verdicts.0.1",
      "original": "실제 변경 파일과 등록 범위가 일치합니다.",
      "action": "유지",
      "final": "실제 변경 파일과 등록 범위가 일치합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t93_scope.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.verdicts.1.1",
      "original": "등록했지만 실제 변경에서 확인되지 않은 비필수 경로가 있습니다.",
      "action": "유지",
      "final": "등록했지만 실제 변경에서 확인되지 않은 비필수 경로가 있습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t93_scope.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.verdicts.2.1",
      "original": "실제 변경했지만 등록하지 않은 경로가 있습니다.",
      "action": "유지",
      "final": "실제 변경했지만 등록하지 않은 경로가 있습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t93_scope.verdicts.3.1",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.verdicts.3.1",
      "original": "경로 분류나 commit 분석을 완료할 수 없습니다.",
      "action": "유지",
      "final": "경로 분류나 commit 분석을 완료할 수 없습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t93_scope.limit",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.limit",
      "original": "경로가 같다는 사실만 확인하며, Manifest에 적은 업무 설명의 정확성은 사람이 검토합니다.",
      "action": "유지",
      "final": "경로가 같다는 사실만 확인하며, Manifest에 적은 업무 설명의 정확성은 사람이 검토합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t93_scope.output",
      "chapter": "2",
      "page": "상세 · T93-범위 · 실제 변경과 Manifest 일치 확인",
      "location": "gate.t93_scope.output",
      "original": "등록 검증 결과 registration-validation-results.json과 통합 소스 검사 결과에 ID별 실제 경로·등록 경로 비교가 남습니다. Manifest 작성자와 리뷰어가 확인합니다.",
      "action": "유지",
      "final": "등록 검증 결과 registration-validation-results.json과 통합 소스 검사 결과에 ID별 실제 경로·등록 경로 비교가 남습니다. Manifest 작성자와 리뷰어가 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t93_policy.title",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.title",
      "original": "T93-정책 · 검사 경로 최신성 확인",
      "action": "유지",
      "final": "T93-정책 · 검사 경로 최신성 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t93_policy.question",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.question",
      "original": "공식 파일 이동이나 모듈 추가로 기존 경로 정책과 watch 규칙이 낡았는가?",
      "action": "유지",
      "final": "공식 파일 이동이나 모듈 추가로 기존 경로 정책과 watch 규칙이 낡았는가?",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t93_policy.status",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.status",
      "original": "검사 구현 완료 · 현재 OM_TEMP source-gate-results.json에는 T93-정책 실행 결과 없음",
      "action": "수정",
      "final": "검사 구현 완료 · 현재 적용 예시인 OM_TEMP의 source-gate-results.json에는 T93-정책 실행 결과 없음",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t93_policy.timing",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.timing",
      "original": "공식 새 버전의 구조 변경을 분석할 때 실행합니다.",
      "action": "유지",
      "final": "공식 새 버전의 구조 변경을 분석할 때 실행합니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "2|gate.t93_policy.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.inputs.0.1",
      "original": "파일 이동·삭제·추가 정보",
      "action": "유지",
      "final": "파일 이동·삭제·추가 정보",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t93_policy.inputs.1.0",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.inputs.1.0",
      "original": "Manifest·경로 정책",
      "action": "유지",
      "final": "Manifest·경로 정책",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t93_policy.inputs.1.1",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.inputs.1.1",
      "original": "watch, repository layout과 민감 경로 규칙",
      "action": "수정",
      "final": "watch, 코드 경로 분류표와 민감 경로 규칙",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t93_policy.steps.0",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.steps.0",
      "original": "기존 watch 경로가 새 공식 버전에도 존재하는지 확인합니다.",
      "action": "유지",
      "final": "기존 watch 경로가 새 공식 버전에도 존재하는지 확인합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t93_policy.steps.1",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.steps.1",
      "original": "공식 변경으로 경로가 이동·삭제됐는지 확인합니다.",
      "action": "유지",
      "final": "공식 변경으로 경로가 이동·삭제됐는지 확인합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t93_policy.steps.2",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.steps.2",
      "original": "새로운 관련 모듈 때문에 기존 규칙이 변경을 놓칠 가능성이 있는지 표시합니다.",
      "action": "유지",
      "final": "새로운 관련 모듈 때문에 기존 규칙이 변경을 놓칠 가능성이 있는지 표시합니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "2|gate.t93_policy.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.verdicts.0.1",
      "original": "기존 검사 경로가 새 공식 버전에서도 유효합니다.",
      "action": "유지",
      "final": "기존 검사 경로가 새 공식 버전에서도 유효합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t93_policy.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.verdicts.1.1",
      "original": "경로 이동·삭제 또는 구조 변경으로 정책 갱신 검토가 필요합니다.",
      "action": "유지",
      "final": "경로 이동·삭제 또는 구조 변경으로 정책 갱신 검토가 필요합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t93_policy.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.verdicts.2.1",
      "original": "공식 버전이나 경로 정책을 읽지 못했습니다.",
      "action": "유지",
      "final": "공식 버전이나 경로 정책을 읽지 못했습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t93_policy.limit",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.limit",
      "original": "경로와 직접 참조를 중심으로 확인합니다. 의미상 새로 생긴 의존 관계는 담당자가 추가해야 할 수 있습니다.",
      "action": "유지",
      "final": "경로와 직접 참조를 중심으로 확인합니다. 의미상 새로 생긴 의존 관계는 담당자가 추가해야 할 수 있습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t93_policy.output",
      "chapter": "2",
      "page": "상세 · T93-정책 · 검사 경로 최신성 확인",
      "location": "gate.t93_policy.output",
      "original": "업그레이드 위험 검사 JSON의 T93-정책 항목에 이동·삭제된 watch 경로와 오래된 경로 정책이 남습니다. 플랫폼 담당자와 Manifest 담당자가 갱신 여부를 확인합니다.",
      "action": "유지",
      "final": "업그레이드 위험 검사 JSON의 T93-정책 항목에 이동·삭제된 watch 경로와 오래된 경로 정책이 남습니다. 플랫폼 담당자와 Manifest 담당자가 갱신 여부를 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t60i.title",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.title",
      "original": "T60-I · 필수 테스트 코드 존재 확인",
      "action": "유지",
      "final": "T60-I · 필수 테스트 코드 존재 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t60i.question",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.question",
      "original": "Contract에 등록한 필수 test의 파일과 Python 함수가 실제 검사 저장소에 존재하는가?",
      "action": "수정",
      "final": "Contract에 등록한 필수 test의 파일과 Python 함수가 실제 검사기 저장소에 존재하는가?",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t60i.status",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.status",
      "original": "Python pytest 확인 구현 완료 · OM_TEMP 1.13.1 결과 파일 있음 · Java·TypeScript test 연결은 추가 개발 대상",
      "action": "수정",
      "final": "Python pytest 확인 구현 완료 · 현재 적용 예시: OM_TEMP 1.13.0 재검증 결과 PASS · Java·TypeScript test 연결은 추가 개발 대상",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t60i.timing",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.timing",
      "original": "Contract를 등록·갱신한 뒤와 Runtime test 실행 전에 실행합니다.",
      "action": "유지",
      "final": "Contract를 등록·갱신한 뒤와 Runtime test 실행 전에 실행합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t60i.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.inputs.0.1",
      "original": "assurance.contracts와 direct_tests",
      "action": "유지",
      "final": "assurance.contracts와 direct_tests",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t60i.inputs.1.1",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.inputs.1.1",
      "original": "required_tests의 pytest 선택자",
      "action": "유지",
      "final": "required_tests의 pytest 선택자",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t60i.inputs.2.1",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.inputs.2.1",
      "original": "실제 Python test 파일과 함수",
      "action": "유지",
      "final": "실제 Python test 파일과 함수",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t60i.inputs.2.2",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.inputs.2.2",
      "original": "easyseop/openmetadata-test의 test_korean_ime.py",
      "action": "수정",
      "final": "현재 적용 예시: easyseop/openmetadata-test의 test_korean_ime.py",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t60i.steps.0",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.steps.0",
      "original": "Manifest가 참조하는 Contract ID를 찾습니다.",
      "action": "유지",
      "final": "Manifest가 참조하는 Contract ID를 찾습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t60i.steps.1",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.steps.1",
      "original": "Contract의 required_tests 선택자를 파일 경로와 함수 이름으로 분리합니다.",
      "action": "유지",
      "final": "Contract의 required_tests 선택자를 파일 경로와 함수 이름으로 분리합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t60i.steps.2",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.steps.2",
      "original": "Python AST로 파일을 읽어 지정한 test 함수가 실제 존재하는지 확인합니다.",
      "action": "수정",
      "final": "Python 문법 분석기로 파일 안의 함수 이름을 읽어 지정한 test 함수가 실제로 있는지 확인합니다.",
      "reason": "AST가 하는 일을 ‘Python 함수 이름을 읽는 분석’으로 설명"
    },
    {
      "id": "2|gate.t60i.steps.3",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.steps.3",
      "original": "Manifest와 Contract의 양방향 BANK-OM 연결도 확인합니다.",
      "action": "수정",
      "final": "Manifest가 Contract를 가리키고 Contract도 같은 BANK-OM ID를 가리키는지 확인합니다.",
      "reason": "‘양방향·역방향’ 대신 서로 확인하는 두 항목을 직접 명시"
    },
    {
      "id": "2|gate.t60i.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.verdicts.0.1",
      "original": "등록한 Python test 파일과 함수가 모두 존재합니다.",
      "action": "유지",
      "final": "등록한 Python test 파일과 함수가 모두 존재합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t60i.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.verdicts.1.1",
      "original": "Contract, test 파일 또는 test 함수가 없습니다.",
      "action": "유지",
      "final": "Contract, test 파일 또는 test 함수가 없습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t60i.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.verdicts.2.1",
      "original": "Python 파일 문법을 읽을 수 없거나 입력 형식이 잘못됐습니다.",
      "action": "유지",
      "final": "Python 파일 문법을 읽을 수 없거나 입력 형식이 잘못됐습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t60i.limit",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.limit",
      "original": "test가 존재한다는 사실만 확인합니다. 실행 성공은 T62가 확인하며 Java JUnit·TypeScript Jest는 현재 직접 확인하지 않습니다.",
      "action": "유지",
      "final": "test가 존재한다는 사실만 확인합니다. 실행 성공은 T62가 확인하며 Java JUnit·TypeScript Jest는 현재 직접 확인하지 않습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t60i.output",
      "chapter": "2",
      "page": "상세 · T60-I · 필수 테스트 코드 존재 확인",
      "location": "gate.t60i.output",
      "original": "등록 검증 결과 registration-validation-results.json의 “필수 테스트 코드 존재” 항목에 누락 여부가 남습니다. Contract 작성자와 테스트 담당자가 확인합니다.",
      "action": "유지",
      "final": "등록 검증 결과 registration-validation-results.json의 “필수 테스트 코드 존재” 항목에 누락 여부가 남습니다. Contract 작성자와 테스트 담당자가 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t61.title",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.title",
      "original": "T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "action": "유지",
      "final": "T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t61.question",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.question",
      "original": "BANK-OM 변경을 제거한 상태에서는 해당 기능의 필수 test가 실제로 실패하는가?",
      "action": "유지",
      "final": "BANK-OM 변경을 제거한 상태에서는 해당 기능의 필수 test가 실제로 실패하는가?",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t61.status",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.status",
      "original": "검사 엔진 구현 완료 · OM_TEMP용 patch-kill-plan.yaml 작성과 환경 실행은 아직 필요",
      "action": "수정",
      "final": "검사 엔진 구현 완료 · 현재 적용 예시인 OM_TEMP용 patch-kill-plan.yaml 작성과 환경 실행은 아직 필요",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t61.timing",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.timing",
      "original": "Contract test가 준비된 뒤, 테스트가 커스터마이징을 실제로 보호하는지 확인할 때 실행합니다.",
      "action": "유지",
      "final": "Contract test가 준비된 뒤, 테스트가 커스터마이징을 실제로 보호하는지 확인할 때 실행합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t61.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.inputs.0.1",
      "original": "제거할 BANK-OM ID, 대상 파일·패치와 예상 실패 test",
      "action": "유지",
      "final": "제거할 BANK-OM ID, 대상 파일·패치와 예상 실패 test",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t61.inputs.0.2",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.inputs.0.2",
      "original": "BANK-OM-005 제거 → test_hangul_composition_roundtrip 실패 예상",
      "action": "유지",
      "final": "BANK-OM-005 제거 → test_hangul_composition_roundtrip 실패 예상",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t61.inputs.1.1",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.inputs.1.1",
      "original": "변경 제거 전 검사 대상 commit·배포 파일",
      "action": "수정",
      "final": "변경을 제거하기 전에 검사할 custom branch commit과 배포 파일을 고정한 자료",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t61.inputs.1.2",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.inputs.1.2",
      "original": "형식 예시: 후보 <실행 대상 SHA> · artifact <실제 digest>",
      "action": "수정",
      "final": "형식 예시: 검사 대상 commit <실행 대상 SHA> · 배포 파일 <내용 확인값>",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀 · artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|gate.t61.inputs.2.1",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.inputs.2.1",
      "original": "변경 제거 전·후 test outcome",
      "action": "수정",
      "final": "BANK-OM 변경을 넣었을 때와 뺐을 때의 test 결과",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t61.inputs.2.2",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.inputs.2.2",
      "original": "정상 후보 pass · BANK-OM-005 제거 상태 fail",
      "action": "수정",
      "final": "정상 검사 대상 코드 pass · BANK-OM-005 제거 상태 fail",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t61.steps.0",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.steps.0",
      "original": "정상 후보에서 필수 test가 성공하는지 확인합니다.",
      "action": "수정",
      "final": "BANK-OM 변경이 들어 있는 정상 검사 대상 custom branch commit에서 필수 test가 성공하는지 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t61.steps.1",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.steps.1",
      "original": "대상 BANK-OM 변경만 제거한 비교 상태를 만듭니다.",
      "action": "유지",
      "final": "대상 BANK-OM 변경만 제거한 비교 상태를 만듭니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t61.steps.2",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.steps.2",
      "original": "등록한 필수 test를 다시 실행합니다.",
      "action": "유지",
      "final": "등록한 필수 test를 다시 실행합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t61.steps.3",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.steps.3",
      "original": "제거 상태에서 모든 목표 test가 실패하는지 확인합니다.",
      "action": "유지",
      "final": "제거 상태에서 모든 목표 test가 실패하는지 확인합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t61.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.verdicts.0.1",
      "original": "정상 후보에서는 성공하고 변경 제거 상태에서는 목표 test가 실패합니다.",
      "action": "수정",
      "final": "정상 검사 대상 custom branch commit에서는 성공하고 변경 제거 상태에서는 목표 test가 실패합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t61.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.verdicts.1.1",
      "original": "변경을 제거해도 test가 성공하거나 목표 test를 실행하지 못했습니다.",
      "action": "유지",
      "final": "변경을 제거해도 test가 성공하거나 목표 test를 실행하지 못했습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t61.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.verdicts.2.1",
      "original": "제거 상태나 실행 결과가 지정 후보와 연결되지 않습니다.",
      "action": "수정",
      "final": "제거 상태나 실행 결과가 Candidate lock에 기록된 검사 대상 custom branch commit과 연결되지 않습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t61.limit",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.limit",
      "original": "실패했다는 사실만으로 실패 원인이 정확히 기능 제거 때문인지 단정하기 어렵습니다. 오류 종류·메시지를 함께 검토해야 합니다.",
      "action": "유지",
      "final": "실패했다는 사실만으로 실패 원인이 정확히 기능 제거 때문인지 단정하기 어렵습니다. 오류 종류·메시지를 함께 검토해야 합니다.",
      "reason": "적용 시점이나 실제 예시가 들어 있어 처음 읽는 사람도 행동을 판단할 수 있음"
    },
    {
      "id": "2|gate.t61.output",
      "chapter": "2",
      "page": "상세 · T61 · 커스터마이징 제거 시 테스트 실패 확인",
      "location": "gate.t61.output",
      "original": "소스 제거 검사는 --output으로 지정한 source-patch-kill-result.yaml에, Runtime 제거 검사는 별도의 acgh-result.yaml에 정상·제거 상태의 test 결과를 남깁니다. 기능 담당자가 실패 원인이 의도한 기능 제거인지 확인합니다.",
      "action": "수정",
      "final": "소스 제거 결과는 source-patch-kill-result.yaml에, 실행 환경의 제거 결과는 acgh-result.yaml에 기록됩니다. 두 파일에는 정상 상태와 변경 제거 상태의 test 결과가 함께 남으며, 기능 담당자가 예상한 이유로 실패했는지 확인합니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "2|gate.t62.title",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.title",
      "original": "T62 · 테스트 결과와 후보 연결 확인",
      "action": "수정",
      "final": "T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t62.question",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.question",
      "original": "필수 test가 정확히 검사 대상으로 고정한 commit과 배포 파일에서 실행됐는가?",
      "action": "유지",
      "final": "필수 test가 정확히 검사 대상으로 고정한 commit과 배포 파일에서 실행됐는가?",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t62.status",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.status",
      "original": "실행기·단위 테스트 완료 · 실제 행내 환경 실행 대기",
      "action": "유지",
      "final": "실행기·단위 테스트 완료 · 실제 행내 환경 실행 대기",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t62.timing",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.timing",
      "original": "테스트 환경에 검사 대상 코드를 배포하고 Contract test를 실행할 때마다 수행합니다.",
      "action": "유지",
      "final": "테스트 환경에 검사 대상 코드를 배포하고 Contract test를 실행할 때마다 수행합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t62.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.inputs.0.1",
      "original": "검사 대상 commit과 artifact digest",
      "action": "수정",
      "final": "검사할 코드와 그 코드로 만든 배포 파일을 고정한 자료",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀 · artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|gate.t62.inputs.0.2",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.inputs.0.2",
      "original": "형식 예시: <실행 대상 SHA> · <실제 artifact digest>",
      "action": "수정",
      "final": "형식 예시: <실행 대상 SHA> · <배포 파일 내용 확인값>",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀 · artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|gate.t62.inputs.1.1",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.inputs.1.1",
      "original": "test ID, 시도 번호, outcome, 검사기·suite 버전",
      "action": "수정",
      "final": "실행한 test, 시도 번호, 결과와 test 묶음 버전",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t62.inputs.2.1",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.inputs.2.1",
      "original": "필수 test와 기능 중요도",
      "action": "유지",
      "final": "필수 test와 기능 중요도",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t62.steps.0",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.steps.0",
      "original": "Test run set의 commit·artifact가 Candidate lock과 같은지 확인합니다.",
      "action": "수정",
      "final": "Test run set에 적힌 코드와 배포 파일이 Candidate lock에 고정한 대상과 같은지 확인합니다.",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|gate.t62.steps.1",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.steps.1",
      "original": "검사기 버전과 test suite 버전이 예상값과 같은지 확인합니다.",
      "action": "수정",
      "final": "검사기 버전과 test 묶음 버전이 승인한 값과 같은지 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t62.steps.2",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.steps.2",
      "original": "모든 active BANK-OM의 필수 test가 실행 목록에 있는지 확인합니다.",
      "action": "유지",
      "final": "모든 active BANK-OM의 필수 test가 실행 목록에 있는지 확인합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t62.steps.3",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.steps.3",
      "original": "SKIP·FAIL·ERROR와 재시도 이력을 숨기지 않고 판정합니다.",
      "action": "유지",
      "final": "SKIP·FAIL·ERROR와 재시도 이력을 숨기지 않고 판정합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t62.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.verdicts.0.1",
      "original": "필수 test가 같은 후보에서 누락 없이 성공했습니다.",
      "action": "수정",
      "final": "필수 test가 Candidate lock에 기록된 같은 검사 대상 custom branch commit에서 누락 없이 성공했습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t62.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.verdicts.1.1",
      "original": "high·critical 기능이 실패 후 재시도에서 성공해 불안정성 검토가 필요합니다.",
      "action": "유지",
      "final": "high·critical 기능이 실패 후 재시도에서 성공해 불안정성 검토가 필요합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t62.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.verdicts.2.1",
      "original": "필수 test 누락·SKIP·FAIL·ERROR가 있습니다.",
      "action": "유지",
      "final": "필수 test 누락·SKIP·FAIL·ERROR가 있습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t62.verdicts.3.1",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.verdicts.3.1",
      "original": "후보·artifact·검사기·suite 버전이 맞지 않습니다.",
      "action": "수정",
      "final": "검사한 코드·배포 파일·검사기·test 묶음 버전이 서로 맞지 않습니다.",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|gate.t62.limit",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.limit",
      "original": "등록된 test만 확인합니다. Contract가 다루지 않은 업무 동작까지 자동으로 보장하지 않습니다.",
      "action": "유지",
      "final": "등록된 test만 확인합니다. Contract가 다루지 않은 업무 동작까지 자동으로 보장하지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t62.output",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.output",
      "original": "실행별 evidence 폴더에 test-run-set.yaml과 acgh-result.yaml이 새로 생성됩니다. 기능 담당자와 배포 검토자가 후보·artifact 일치와 test 결과를 확인합니다.",
      "action": "수정",
      "final": "각 실행의 증거 폴더에는 test-run-set.yaml과 acgh-result.yaml이 새로 생깁니다. 기능 담당자와 배포 검토자는 검사한 코드·배포 파일이 맞는지와 test 결과를 확인합니다.",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|gate.t63.title",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.title",
      "original": "T63 · TypeScript 오류 증가 확인",
      "action": "유지",
      "final": "T63 · TypeScript 오류 증가 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t63.question",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.question",
      "original": "공식 원본과 비교해 행내 후보에 새 TypeScript 오류가 추가됐는가?",
      "action": "수정",
      "final": "공식 OpenMetadata commit과 비교해 검사 대상 custom branch commit에 새 TypeScript 오류가 추가됐는가?",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t63.status",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.status",
      "original": "비교 도구 구현 완료 · 전체 환경 로그 결속 보완 대상",
      "action": "유지",
      "final": "비교 도구 구현 완료 · 전체 환경 로그 결속 보완 대상",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t63.timing",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.timing",
      "original": "공식 원본과 행내 후보에서 같은 TypeScript 검사를 각각 실행한 뒤 사용합니다.",
      "action": "수정",
      "final": "공식 OpenMetadata commit과 검사 대상 custom branch commit에서 같은 TypeScript 검사를 각각 실행한 뒤 사용합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t63.inputs.0.0",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.inputs.0.0",
      "original": "공식 원본 typecheck 로그",
      "action": "유지",
      "final": "공식 원본 typecheck 로그",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t63.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.inputs.0.1",
      "original": "파일 경로·오류 코드별 발생 정보와 종료 코드",
      "action": "유지",
      "final": "파일 경로·오류 코드별 발생 정보와 종료 코드",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t63.inputs.0.2",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.inputs.0.2",
      "original": "upstream.log · TS2322 3건 · exit 2",
      "action": "유지",
      "final": "upstream.log · TS2322 3건 · exit 2",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t63.inputs.1.0",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.inputs.1.0",
      "original": "행내 후보 typecheck 로그",
      "action": "수정",
      "final": "검사 대상 custom branch commit의 typecheck 로그",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t63.inputs.1.1",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.inputs.1.1",
      "original": "같은 명령으로 실행한 결과와 종료 코드",
      "action": "유지",
      "final": "같은 명령으로 실행한 결과와 종료 코드",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t63.inputs.1.2",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.inputs.1.2",
      "original": "candidate.log · TS2322 3건 · exit 2",
      "action": "유지",
      "final": "candidate.log · TS2322 3건 · exit 2",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t63.steps.0",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.steps.0",
      "original": "두 로그에서 파일 경로와 TypeScript 오류 코드를 정규화합니다.",
      "action": "수정",
      "final": "두 로그의 파일 경로와 오류 코드를 같은 표기 방식으로 맞춥니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t63.steps.1",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.steps.1",
      "original": "같은 경로·오류 코드의 발생 횟수를 비교합니다.",
      "action": "유지",
      "final": "같은 경로·오류 코드의 발생 횟수를 비교합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t63.steps.2",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.steps.2",
      "original": "행내 후보에서 새로 생기거나 증가한 오류를 찾습니다.",
      "action": "수정",
      "final": "검사 대상 custom branch commit에서 새로 생기거나 증가한 오류를 찾습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t63.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.verdicts.0.1",
      "original": "행내 후보에 공식 원본보다 새 TypeScript 오류가 없습니다.",
      "action": "수정",
      "final": "검사 대상 custom branch commit에 공식 OpenMetadata commit보다 새 TypeScript 오류가 없습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t63.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.verdicts.1.1",
      "original": "새 오류 또는 오류 횟수 증가가 있습니다.",
      "action": "유지",
      "final": "새 오류 또는 오류 횟수 증가가 있습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t63.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.verdicts.2.1",
      "original": "로그 형식이나 실행 정보가 비교 가능하지 않습니다.",
      "action": "유지",
      "final": "로그 형식이나 실행 정보가 비교 가능하지 않습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t63.limit",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.limit",
      "original": "TypeScript만 비교하며 Node·Yarn 버전과 전체 로그 digest를 T63 결과에 강제 연결하는 기능은 보완 대상입니다.",
      "action": "수정",
      "final": "TypeScript 오류만 비교합니다. Node·Yarn 버전과 로그 전체의 내용 확인값을 결과에 자동 연결하는 기능은 아직 없습니다.",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "2|gate.t63.output",
      "chapter": "2",
      "page": "상세 · T63 · TypeScript 오류 증가 확인",
      "location": "gate.t63.output",
      "original": "TypeScript 비교 명령의 JSON 표준 출력에 공식·행내 오류 수와 새 오류 목록이 남습니다. 프론트엔드 담당자가 로그의 실행 환경과 새 오류를 확인합니다.",
      "action": "유지",
      "final": "TypeScript 비교 명령의 JSON 표준 출력에 공식·행내 오류 수와 새 오류 목록이 남습니다. 프론트엔드 담당자가 로그의 실행 환경과 새 오류를 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t90.title",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.title",
      "original": "T90 · 업그레이드 전 과정 결과 확인",
      "action": "유지",
      "final": "T90 · 업그레이드 전 과정 결과 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t90.question",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.question",
      "original": "복원·migration·색인·수집·권한·API·검색·rollback 등 필수 업그레이드 단계를 모두 실행해 통과했는가?",
      "action": "수정",
      "final": "데이터 복원, DB 변경, 검색 색인, 수집, 권한, API, 검색, 이전 버전 복귀 등 필수 업그레이드 단계를 모두 실행해 통과했는가?",
      "reason": "구현 용어 대신 파일 교체와 실패 시 복구 행동을 설명"
    },
    {
      "id": "2|gate.t90.status",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.status",
      "original": "판정 모듈·스키마 구현 완료 · 실제 행내 업그레이드 실행 증거 대기",
      "action": "유지",
      "final": "판정 모듈·스키마 구현 완료 · 실제 행내 업그레이드 실행 증거 대기",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t90.timing",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.timing",
      "original": "실제와 유사한 테스트 환경에서 후보 업그레이드 연습을 수행한 뒤 실행합니다.",
      "action": "수정",
      "final": "실제와 유사한 테스트 환경에서 검사 대상 release commit의 업그레이드 연습을 수행한 뒤 실행합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t90.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.inputs.0.1",
      "original": "이전·새 버전, 후보, 12개 필수 단계 outcome",
      "action": "수정",
      "final": "이전·새 버전, 검사 대상과 12개 필수 단계의 결과",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t90.inputs.0.2",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.inputs.0.2",
      "original": "가상 형식 예시: 1.13.0 → 1.13.1 · migration/search/rollback 등 12개가 모두 pass인 경우",
      "action": "수정",
      "final": "형식 예시: 1.13.0 → 1.13.1 · DB 변경/검색/이전 버전 복귀 등 12개 모두 pass",
      "reason": "구현 용어 대신 파일 교체와 실패 시 복구 행동을 설명"
    },
    {
      "id": "2|gate.t90.inputs.1.1",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.inputs.1.1",
      "original": "검사 대상 commit·artifact",
      "action": "수정",
      "final": "검사할 코드와 배포 파일을 고정한 자료",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|gate.t90.inputs.1.2",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.inputs.1.2",
      "original": "형식 예시: <실행 대상 SHA> · <실제 artifact digest>",
      "action": "수정",
      "final": "형식 예시: <실행 대상 SHA> · <배포 파일 내용 확인값>",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀 · artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|gate.t90.inputs.2.1",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.inputs.2.1",
      "original": "같은 후보의 Contract test 결과 digest",
      "action": "수정",
      "final": "같은 검사 대상에서 실행한 Contract test 결과의 내용 확인값",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "2|gate.t90.inputs.2.2",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.inputs.2.2",
      "original": "환경 실행 예시: sha256:04bd…",
      "action": "유지",
      "final": "환경 실행 예시: sha256:04bd…",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t90.steps.0",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.steps.0",
      "original": "업그레이드 결과의 검사 대상 commit·artifact가 Candidate lock과 같은지 확인합니다.",
      "action": "수정",
      "final": "업그레이드 결과가 Candidate lock에 고정한 코드와 배포 파일에서 나온 것인지 확인합니다.",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|gate.t90.steps.1",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.steps.1",
      "original": "연결된 Test run set digest가 실제 실행 결과와 같은지 확인합니다.",
      "action": "수정",
      "final": "연결된 Test run set의 내용 확인값이 실제 test 결과와 같은지 확인합니다.",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "2|gate.t90.steps.2",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.steps.2",
      "original": "정해진 12개 단계가 모두 존재하고 outcome이 pass인지 확인합니다.",
      "action": "수정",
      "final": "정해진 12개 단계가 모두 있고 각 결과가 pass인지 확인합니다. 결과 파일에서는 운영 데이터 복원(restore-production-snapshot), DB 변경 적용(migration), 데이터 건수 대조(row-reconciliation), 검색 인덱스 재생성(reindex), 메타데이터 수집 확인(ingestion), 로그인 동작 비교(differential-authentication), 권한 동작 비교(differential-authorization), API 동작 비교(differential-api), 관계 정보 비교(differential-relations), 검색 결과 비교(differential-search), 수집 결과 비교(differential-ingestion), 되돌리기 연습(rollback-drill)이라는 실제 단계 ID를 사용합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t90.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.verdicts.0.1",
      "original": "같은 후보에서 12개 필수 업그레이드 단계가 모두 성공했습니다.",
      "action": "수정",
      "final": "Candidate lock에 기록된 같은 검사 대상 release commit에서 12개 필수 업그레이드 단계가 모두 성공했습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|gate.t90.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.verdicts.1.1",
      "original": "필수 단계가 없거나 pass가 아닙니다.",
      "action": "유지",
      "final": "필수 단계가 없거나 pass가 아닙니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t90.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.verdicts.2.1",
      "original": "후보·artifact·Test run set 연결이 맞지 않거나 결과 형식이 잘못됐습니다.",
      "action": "수정",
      "final": "검사한 코드·배포 파일·Test run set의 연결이 맞지 않거나 결과 형식이 잘못됐습니다.",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|gate.t90.limit",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.limit",
      "original": "결과 문서가 올바른 형식이고 같은 검사 대상을 가리키는지를 확인합니다. 각 단계를 실제로 수행했다는 외부 실행 로그·서명 검증은 추가 결속이 필요합니다.",
      "action": "수정",
      "final": "결과 파일의 형식과 검사 대상의 일치 여부를 확인합니다. 각 단계를 실제로 실행했다는 사실을 외부 로그나 전자서명으로 확인하는 기능은 아직 연결하지 않았습니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|gate.t90.output",
      "chapter": "2",
      "page": "상세 · T90 · 업그레이드 전 과정 결과 확인",
      "location": "gate.t90.output",
      "original": "실행 시스템이 upgrade-test-run.yaml과 해당 판정을 포함한 acgh-result.yaml을 보관합니다. 업그레이드 책임자가 12개 단계와 연결된 후보·artifact를 확인합니다.",
      "action": "수정",
      "final": "실행 시스템은 upgrade-test-run.yaml과 판정이 들어 있는 acgh-result.yaml을 보관합니다. 업그레이드 책임자는 12개 단계가 같은 코드와 배포 파일에서 실행됐는지 확인합니다.",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|gate.t91.title",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.title",
      "original": "T91 · 검증 대상과 배포 대상 일치 확인",
      "action": "유지",
      "final": "T91 · 검증 대상과 배포 대상 일치 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t91.question",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.question",
      "original": "검사한 commit·이미지·Helm 설정을 다시 만들지 않고 그대로 배포하는가?",
      "action": "유지",
      "final": "검사한 commit·이미지·Helm 설정을 다시 만들지 않고 그대로 배포하는가?",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t91.status",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.status",
      "original": "판정 모듈·스키마 구현 완료 · 실제 배포 환경 결속 대기",
      "action": "유지",
      "final": "판정 모듈·스키마 구현 완료 · 실제 배포 환경 결속 대기",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t91.timing",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.timing",
      "original": "모든 필수 검사가 끝난 뒤 배포 승격 직전에 실행합니다.",
      "action": "유지",
      "final": "모든 필수 검사가 끝난 뒤 배포 승격 직전에 실행합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t91.inputs.0.1",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.inputs.0.1",
      "original": "후보·정책·검사기·suite·결과·이미지·Helm digest",
      "action": "수정",
      "final": "검사한 코드·정책·검사기·test 묶음·결과·이미지·Helm 설정을 한 배포 대상으로 묶은 자료",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "2|gate.t91.inputs.0.2",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.inputs.0.2",
      "original": "형식 예시: candidate <검증 SHA> · image <검증 digest>",
      "action": "수정",
      "final": "형식 예시: candidate <검증 SHA> · image <검증 내용 확인값>",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "2|gate.t91.inputs.1.0",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.inputs.1.0",
      "original": "Candidate lock·Test run set·검사 결과",
      "action": "유지",
      "final": "Candidate lock·Test run set·검사 결과",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t91.inputs.1.2",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.inputs.1.2",
      "original": "형식 예시: 세 파일 모두 같은 <검증 SHA>",
      "action": "유지",
      "final": "형식 예시: 세 파일 모두 같은 <검증 SHA>",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|gate.t91.inputs.2.1",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.inputs.2.1",
      "original": "배포할 commit, 이미지와 Helm digest, 재빌드 여부",
      "action": "수정",
      "final": "배포할 commit, 이미지와 Helm 설정의 내용 확인값, 재빌드 여부",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "2|gate.t91.inputs.2.2",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.inputs.2.2",
      "original": "형식 예시: <검증 SHA> · <검증 digest> · rebuilt=false",
      "action": "수정",
      "final": "형식 예시: <검증 SHA> · <검증 내용 확인값> · rebuilt=false",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "2|gate.t91.steps.0",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.steps.0",
      "original": "Release lock과 Candidate lock·검사 결과·Test run set의 digest 연결을 확인합니다.",
      "action": "수정",
      "final": "Release lock이 Candidate lock, 검사 결과, Test run set과 같은 검사 대상을 가리키는지 확인합니다.",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "2|gate.t91.steps.1",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.steps.1",
      "original": "검증한 이미지·Helm digest와 실제 배포 관측값을 비교합니다.",
      "action": "수정",
      "final": "검증한 이미지·Helm 설정의 내용 확인값을 실제 배포 정보와 비교합니다.",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "2|gate.t91.steps.2",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.steps.2",
      "original": "검증 후 재빌드한 artifact인지 확인합니다.",
      "action": "수정",
      "final": "검증이 끝난 뒤 배포 파일을 다시 만들었는지 확인합니다.",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|gate.t91.verdicts.0.1",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.verdicts.0.1",
      "original": "검증한 동일 artifact를 재빌드 없이 배포합니다.",
      "action": "수정",
      "final": "검증한 동일 배포 파일을 다시 만들지 않고 배포합니다.",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|gate.t91.verdicts.1.1",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.verdicts.1.1",
      "original": "이미지·Helm·commit이 다르거나 검증 후 재빌드했습니다.",
      "action": "유지",
      "final": "이미지·Helm·commit이 다르거나 검증 후 재빌드했습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|gate.t91.verdicts.2.1",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.verdicts.2.1",
      "original": "Release lock과 검사 증거의 연결이 오래됐거나 손상됐습니다.",
      "action": "유지",
      "final": "Release lock과 검사 증거의 연결이 오래됐거나 손상됐습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t91.limit",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.limit",
      "original": "외부망에서 내부망으로 파일을 옮긴 뒤의 별도 서명·해시 재검증과 배포 시스템 서명은 추가 운영 연동이 필요합니다.",
      "action": "유지",
      "final": "외부망에서 내부망으로 파일을 옮긴 뒤의 별도 서명·해시 재검증과 배포 시스템 서명은 추가 운영 연동이 필요합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|gate.t91.output",
      "chapter": "2",
      "page": "상세 · T91 · 검증 대상과 배포 대상 일치 확인",
      "location": "gate.t91.output",
      "original": "승격 검사 결과의 T91 항목에 Release lock과 실제 배포 관측값의 불일치가 남습니다. 배포 승인자와 운영 담당자가 최종 배포 전에 확인합니다.",
      "action": "유지",
      "final": "승격 검사 결과의 T91 항목에 Release lock과 실제 배포 관측값의 불일치가 남습니다. 배포 승인자와 운영 담당자가 최종 배포 전에 확인합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "1|report.1.chapter",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.chapter",
      "original": "1. 목적과 브랜치 전략",
      "action": "유지",
      "final": "1. 목적과 브랜치 전략",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "1|report.1.summary",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.summary",
      "original": "1차 요약은 목적과 전체 브랜치 Cycle을 보여줍니다. 아래 상세 페이지에서 저장소 역할, 병합 지점, 충돌 위치와 ID·SHA의 차이를 각각 확인합니다.",
      "action": "수정",
      "final": "1차 요약은 목적과 전체 브랜치 Cycle을 보여줍니다. 1-1~1-3에서 두 저장소의 역할, OpenMetadata 포크·커스텀·릴리즈 브랜치의 관계, 충돌 위치와 ID·SHA의 차이를 각각 확인합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|report.1.report.question",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.question",
      "original": "공식 새 버전과 BANK-OM 변경은 어느 branch에서 만나고, 충돌이 나면 어디서 해결하는가?",
      "action": "수정",
      "final": "공식 새 버전과 BANK-OM 변경은 어디서 합치고, 검증한 결과는 어떤 브랜치로 운영에 배포하는가?",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|report.1.report.answer",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.answer",
      "original": "patch branch에는 공식 코드만 보관합니다. 새 공식 버전이 들어 있는 patch branch와 직전 custom branch의 BANK-OM 변경은 다음 버전의 custom branch에서 합칩니다. 이 전체 branch 병합 방식을 이 문서에서는 vendor-merge라고 부릅니다. Git 충돌은 합치는 중인 custom branch에서 담당자가 해결하며, 검사기는 코드를 대신 병합하거나 선택하지 않습니다.",
      "action": "수정",
      "final": "OpenMetadata 포크 브랜치에는 공식 코드만 보관합니다. 새 공식 버전의 포크 브랜치와 직전 커스텀 브랜치의 BANK-OM 변경은 새 커스텀 브랜치에서 합칩니다. 충돌은 커스텀 브랜치에서 담당자가 해결합니다. 필수 검사를 통과한 commit에 검증 완료 태그를 붙이고, 운영 승인 후 릴리즈 브랜치가 같은 commit을 가리키게 합니다. 실제 운영 배포는 릴리즈 브랜치를 사용합니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "1|report.1.report.facts.0.2",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.facts.0.2",
      "original": "easyseop/OM_TEMP에서 해당 버전의 공식 OpenMetadata 코드만 보관합니다.",
      "action": "수정",
      "final": "제품 코드 저장소에서 해당 버전의 공식 OpenMetadata 코드만 보관합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|report.1.report.facts.1.2",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.facts.1.2",
      "original": "easyseop/OM_TEMP에서 공식 코드 위에 BANK-OM 변경과 충돌 해결 commit을 기록합니다.",
      "action": "수정",
      "final": "공식 코드 위에 BANK-OM과 충돌 해결 commit을 기록하고 검사합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|report.1.report.facts.2.2",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.facts.2.2",
      "original": "Manifest·정책·검사 코드와 결과를 관리하며 OpenMetadata 제품 코드를 대신 보관하지 않습니다.",
      "action": "수정",
      "final": "검증 완료 태그·Release lock·승인을 확인한 commit만 운영 배포 기준으로 사용합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|report.1.report.flow.1",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.flow.1",
      "original": "patch branch 갱신",
      "action": "수정",
      "final": "T42 사전 영향 확인",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|report.1.report.flow.2",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.flow.2",
      "original": "T42 사전 영향 확인·등록 갱신",
      "action": "수정",
      "final": "커스텀 브랜치에서 병합",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|report.1.report.flow.3",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.flow.3",
      "original": "custom branch에서 병합",
      "action": "수정",
      "final": "충돌 해결 commit",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|report.1.report.flow.4",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.flow.4",
      "original": "충돌 해결 commit",
      "action": "삭제",
      "final": "삭제",
      "reason": "앞뒤 내용과 중복되거나 운영 판단에 필요하지 않아 삭제"
    },
    {
      "id": "1|report.1.report.status.0.0",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.status.0.0",
      "original": "브랜치 역할과 반복 Cycle",
      "action": "유지",
      "final": "브랜치 역할과 반복 Cycle",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "1|report.1.report.status.0.2",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.status.0.2",
      "original": "patch·custom·검사 저장소의 역할과 병합 지점을 문서화했습니다.",
      "action": "수정",
      "final": "OpenMetadata 포크·커스텀·릴리즈 브랜치와 검사기 저장소의 역할을 문서화했습니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|report.1.report.status.1.0",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.status.1.0",
      "original": "OM_TEMP 1.13.0 초기 상태",
      "action": "수정",
      "final": "현재 적용 예시 · OM_TEMP 1.13.0",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|report.1.report.status.1.2",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.status.1.2",
      "original": "공식 1.13.0과 BANK-OM-001~007 변경 이력을 준비했습니다.",
      "action": "유지",
      "final": "공식 1.13.0과 BANK-OM-001~007 변경 이력을 준비했습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "1|report.1.report.status.2.0",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.status.2.0",
      "original": "1.13.1 커밋별 재적용 진단",
      "action": "유지",
      "final": "1.13.1 커밋별 재적용 진단",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "1|report.1.report.status.2.2",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.status.2.2",
      "original": "ID별 충돌은 확인했지만 운영 방식인 vendor-merge 전체 결과는 아닙니다.",
      "action": "유지",
      "final": "ID별 충돌은 확인했지만 운영 방식인 vendor-merge 전체 결과는 아닙니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "1|report.1.report.status.3.0",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.status.3.0",
      "original": "1.13.1 실제 vendor-merge·배포",
      "action": "수정",
      "final": "1.13.1 실제 vendor-merge·릴리즈 배포",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|report.1.report.status.3.2",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.status.3.2",
      "original": "병합 기록, 전체 test와 배포 승인 증거가 아직 없습니다.",
      "action": "수정",
      "final": "병합 기록, 전체 test, 검증 완료 태그, Release lock과 릴리즈 브랜치 승격 증거가 아직 없습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|report.1.report.next",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.next",
      "original": "다음 공식 버전에서도 같은 Cycle을 반복합니다. 현재 연습에서는 실제 vendor-merge 후보를 만든 뒤 충돌 해결 기록과 전체 검사 결과를 다시 남겨야 합니다.",
      "action": "수정",
      "final": "다음 공식 버전에서도 같은 Cycle을 반복합니다. 현재 연습에서는 실제 vendor-merge 결과가 되는 custom branch commit을 만든 뒤 충돌 해결 기록과 전체 검사 결과를 다시 남겨야 합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|report.1.report.figure.title",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.figure.title",
      "original": "브랜치 전략 한눈에 보기",
      "action": "유지",
      "final": "브랜치 전략 한눈에 보기",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "1|report.1.report.figure.note",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.figure.note",
      "original": "파란색은 공식 patch branch, 주황색은 BANK-OM 변경 이력입니다. 두 흐름은 다음 버전의 custom branch에서 합쳐지며, 그 지점에서 Git 충돌이 발생할 수 있습니다. 충돌을 해결한 뒤 검사하고, 통과한 commit에 검증 tag를 붙여 다음 공식 버전에서 같은 Cycle을 반복합니다.",
      "action": "수정",
      "final": "파란색은 공식 OpenMetadata 포크 브랜치, 주황색은 BANK-OM 변경 이력입니다. 두 흐름은 새 커스텀 브랜치에서 합쳐지고 이 지점에서 Git 충돌이 발생할 수 있습니다. 충돌 해결과 검사를 통과한 commit에 검증 완료 태그를 붙인 뒤, 승인된 같은 commit을 릴리즈 브랜치로 승격해 운영에 배포합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|report.1.report.figure.report",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.figure.report",
      "original": "공유문서/openmetadata-phase1-sharing-preview.html",
      "action": "유지",
      "final": "공유문서/openmetadata-phase1-sharing-preview.html",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "1|report.1.details.0.description",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.details.0.description",
      "original": "현재 OM_TEMP·검사 저장소와 과거 참고 저장소 구분",
      "action": "수정",
      "final": "제품 코드 저장소·검사기 저장소의 일반 구조와 현재 적용 예시",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "1|report.1.details.1.description",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.details.1.description",
      "original": "요약 Cycle 도식의 상세판과 충돌 지점",
      "action": "수정",
      "final": "공식 코드, 검사 대상 custom branch commit과 실제 운영 배포 기준선",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|report.1.details.2.description",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.details.2.description",
      "original": "기능 ID, commit 메시지와 Git 식별값 구분",
      "action": "유지",
      "final": "기능 ID, commit 메시지와 Git 식별값 구분",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "1|report.1.details.3.description",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.details.3.description",
      "original": "다음 공식 버전에서 Cycle을 반복하는 순서",
      "action": "유지",
      "final": "다음 공식 버전에서 Cycle을 반복하는 순서",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|report.2.summary",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.summary",
      "original": "2차 요약은 각 검사가 무엇을 확인하고 실패하면 어떻게 되는지 보여줍니다. 아래 상세 페이지에서 입력값, 판단 순서, 실행 명령, 결과 파일과 예외를 확인합니다.",
      "action": "수정",
      "final": "2차 요약은 각 검사가 무엇을 확인하고 실패하면 어떻게 되는지 보여줍니다. 2-1~2-5에서 입력값, 판단 순서, 실행 명령, 결과 파일과 예외를 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|report.2.report.question",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.question",
      "original": "각 검사는 무엇을 입력받아 어떤 문제를 찾고, 결과가 나오면 무엇을 해야 하는가?",
      "action": "유지",
      "final": "각 검사는 무엇을 입력받아 어떤 문제를 찾고, 결과가 나오면 무엇을 해야 하는가?",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|report.2.report.answer",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.answer",
      "original": "검사는 Git 변경, Manifest와 관리 파일, 실행 결과를 서로 비교합니다. 각 검사는 한 가지 질문만 판정하며, PASS는 그 질문을 통과했다는 뜻일 뿐 전체 기능 정상이나 배포 완료를 의미하지 않습니다.",
      "action": "유지",
      "final": "검사는 Git 변경, Manifest와 관리 파일, 실행 결과를 서로 비교합니다. 각 검사는 한 가지 질문만 판정하며, PASS는 그 질문을 통과했다는 뜻일 뿐 전체 기능 정상이나 배포 완료를 의미하지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|report.2.report.facts.0.2",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.facts.0.2",
      "original": "BANK-OM ID와 실제 변경 파일이 Manifest에 빠짐없이 등록됐는지 확인합니다.",
      "action": "유지",
      "final": "BANK-OM ID와 실제 변경 파일이 Manifest에 빠짐없이 등록됐는지 확인합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|report.2.report.facts.1.1",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.facts.1.1",
      "original": "공식 변경과 어디가 겹치나",
      "action": "유지",
      "final": "공식 변경과 어디가 겹치나",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|report.2.report.facts.1.2",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.facts.1.2",
      "original": "공식 새 버전이 BANK-OM 관련 경로를 바꿨는지 찾아 담당자 검토 대상을 제시합니다.",
      "action": "유지",
      "final": "공식 새 버전이 BANK-OM 관련 경로를 바꿨는지 찾아 담당자 검토 대상을 제시합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|report.2.report.facts.2.1",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.facts.2.1",
      "original": "검사한 코드가 실제 대상과 같은가",
      "action": "유지",
      "final": "검사한 코드가 실제 대상과 같은가",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|report.2.report.facts.2.2",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.facts.2.2",
      "original": "test 결과, 검사 대상 commit과 배포 artifact가 서로 같은 대상을 가리키는지 확인합니다.",
      "action": "수정",
      "final": "test 결과, 검사 대상 commit, 실제 배포 파일이 모두 같은 코드를 가리키는지 확인합니다.",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|report.2.report.status.0.2",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.status.0.2",
      "original": "구현·단위 test와 OM_TEMP 결과 파일이 있으며 실제 Git 변경과 Manifest를 비교할 수 있습니다.",
      "action": "유지",
      "final": "구현·단위 test와 OM_TEMP 결과 파일이 있으며 실제 Git 변경과 Manifest를 비교할 수 있습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "2|report.2.report.status.1.2",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.status.1.2",
      "original": "공식 이전·새 버전과 watch 경로를 비교하며 APPROVAL 대상을 찾습니다.",
      "action": "유지",
      "final": "공식 이전·새 버전과 watch 경로를 비교하며 APPROVAL 대상을 찾습니다.",
      "reason": "판정 이름과 그 판정이 뜻하는 결과가 함께 적혀 있어 유지"
    },
    {
      "id": "2|report.2.report.status.2.0",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.status.2.0",
      "original": "Python 필수 test 연결",
      "action": "유지",
      "final": "Python 필수 test 연결",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|report.2.report.status.2.2",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.status.2.2",
      "original": "pytest 파일과 test 이름 존재를 확인합니다.",
      "action": "유지",
      "final": "pytest 파일과 test 이름 존재를 확인합니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|report.2.report.status.3.0",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.status.3.0",
      "original": "Java·TypeScript 기능 test와 행내 Runtime",
      "action": "유지",
      "final": "Java·TypeScript 기능 test와 행내 Runtime",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|report.2.report.status.3.2",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.status.3.2",
      "original": "일부 검사 코드는 있지만 실제 환경 실행과 증거 연결이 완료되지 않았습니다.",
      "action": "유지",
      "final": "일부 검사 코드는 있지만 실제 환경 실행과 증거 연결이 완료되지 않았습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "2|report.2.report.status.4.2",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.status.4.2",
      "original": "실제 배포 artifact와 승인 기록이 있어야 최종 판정할 수 있습니다.",
      "action": "수정",
      "final": "실제 배포 파일과 승인 기록이 있어야 최종 판정할 수 있습니다.",
      "reason": "artifact를 실제 이미지·패키지·배포 파일로 설명"
    },
    {
      "id": "2|report.2.report.next",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.report.next",
      "original": "검사명만 읽지 말고 각 상세 페이지에서 입력값, 비교 방법, 결과 라벨과 다음 조치를 확인합니다. 환경 실행 대기 항목은 PASS로 간주하지 않습니다.",
      "action": "수정",
      "final": "검사명만 읽지 말고 2-1~2-5의 해당 검사 페이지에서 입력값, 비교 방법, 결과 라벨과 다음 조치를 확인합니다. 환경 실행 대기 항목은 PASS로 간주하지 않습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|report.2.details.0.description",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.details.0.description",
      "original": "17개 상세 항목을 업무 질문 기준으로 찾기",
      "action": "수정",
      "final": "17개 검사 항목을 업무 질문 기준으로 찾기",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|report.2.details.1.description",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.details.1.description",
      "original": "ID, 실제 변경 범위와 필수 파일 확인",
      "action": "유지",
      "final": "ID, 실제 변경 범위와 필수 파일 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|report.2.details.2.description",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.details.2.description",
      "original": "공식 변경이 BANK-OM 관련 경로에 미치는 영향",
      "action": "유지",
      "final": "공식 변경이 BANK-OM 관련 경로에 미치는 영향",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|report.2.details.3.description",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.details.3.description",
      "original": "테스트 존재·효력·후보 연결을 구분해 확인",
      "action": "수정",
      "final": "테스트 존재·효력·검사 대상 commit 연결을 구분해 확인",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|report.2.details.4.description",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.details.4.description",
      "original": "검증 대상과 실제 배포 대상의 일치 확인",
      "action": "유지",
      "final": "검증 대상과 실제 배포 대상의 일치 확인",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.chapter",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.chapter",
      "original": "3. 검사 전 사전환경 설정",
      "action": "유지",
      "final": "3. 검사 전 사전환경 설정",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.summary",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.summary",
      "original": "3차 요약은 commit에서 BANK-OM 등록자료를 준비하는 순서를 보여줍니다. 아래 상세 페이지에서 사람이 결정할 값, 자동 생성 값과 관리 파일별 갱신 규칙을 확인합니다.",
      "action": "수정",
      "final": "3차 요약은 commit에서 BANK-OM 등록자료를 준비하는 순서를 보여줍니다. 3-1~3-11에서 사람이 결정할 값, 자동 생성 값과 관리 파일별 갱신 규칙을 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|report.3.report.question",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.question",
      "original": "검사를 시작하기 전에 commit에서 어떤 관리 자료를 만들고, 누가 어떤 값을 확정하는가?",
      "action": "유지",
      "final": "검사를 시작하기 전에 commit에서 어떤 관리 자료를 만들고, 누가 어떤 값을 확정하는가?",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|report.3.report.answer",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.answer",
      "original": "준비도구의 plan 명령은 commit 메시지와 Git diff에서 BANK-OM별 변경 경로와 Manifest·Registry 변경안을 만듭니다. 담당자가 필수 파일, 간접 의존 경로, 업무 동작 기준과 책임자를 승인하면 apply가 승인한 동일 제안만 반영합니다. commit만으로 plan·승인·apply가 자동 실행되지는 않습니다.",
      "action": "유지",
      "final": "준비도구의 plan 명령은 commit 메시지와 Git diff에서 BANK-OM별 변경 경로와 Manifest·Registry 변경안을 만듭니다. 담당자가 필수 파일, 간접 의존 경로, 업무 동작 기준과 책임자를 승인하면 apply가 승인한 동일 제안만 반영합니다. commit만으로 plan·승인·apply가 자동 실행되지는 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|report.3.report.facts.0.2",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.facts.0.2",
      "original": "변경 기록 식별값과 실제 변경 파일은 Git에서 읽습니다.",
      "action": "유지",
      "final": "변경 기록 식별값과 실제 변경 파일은 Git에서 읽습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|report.3.report.facts.1.1",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.facts.1.1",
      "original": "Manifest·Registry·파생 목록",
      "action": "수정",
      "final": "Manifest·Registry·자동 생성 목록",
      "reason": "‘파생’ 대신 자동으로 생성되는 파일을 직접 설명"
    },
    {
      "id": "3|report.3.report.facts.1.2",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.facts.1.2",
      "original": "같은 BANK-OM ID의 여러 commit을 합쳐 현재 버전의 변경 범위를 제안하지만 등록 폴더는 수정하지 않습니다.",
      "action": "유지",
      "final": "같은 BANK-OM ID의 여러 commit을 합쳐 현재 버전의 변경 범위를 제안하지만 등록 폴더는 수정하지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|report.3.report.facts.2.2",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.facts.2.2",
      "original": "기능상 반드시 필요한 파일, 간접 의존과 정상 동작 기준은 담당자가 결정합니다. Contract 내용은 사람이 직접 작성합니다.",
      "action": "유지",
      "final": "기능상 반드시 필요한 파일, 간접 의존과 정상 동작 기준은 담당자가 결정합니다. Contract 내용은 사람이 직접 작성합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|report.3.report.facts.3.0",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.facts.3.0",
      "original": "apply가 자동 갱신",
      "action": "유지",
      "final": "apply가 자동 갱신",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.report.facts.3.2",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.facts.3.2",
      "original": "승인 후 apply를 실행하면 변경 대상 Manifest, 필요한 경우 Registry, commit-inventory.yaml과 current-diff-paths.txt를 갱신합니다. Contract와 과거 코드 연결표는 자동으로 바꾸지 않습니다.",
      "action": "수정",
      "final": "승인 후 apply를 실행하면 변경 대상 Manifest, 필요한 경우 Registry, commit-inventory.yaml과 current-diff-paths.txt를 갱신합니다. Contract와 Registry source.snapshot_sha의 custom commit을 설명하는 연결표는 자동으로 바꾸지 않습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|report.3.report.flow.0",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.flow.0",
      "original": "commit에 BANK-OM ID 기록",
      "action": "유지",
      "final": "commit에 BANK-OM ID 기록",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.report.flow.1",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.flow.1",
      "original": "plan으로 Git 분석·변경안 생성",
      "action": "유지",
      "final": "plan으로 Git 분석·변경안 생성",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.report.flow.2",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.flow.2",
      "original": "담당자 판단값과 diff 검토",
      "action": "유지",
      "final": "담당자 판단값과 diff 검토",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.report.flow.3",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.flow.3",
      "original": "digest에 연결된 승인서 작성",
      "action": "수정",
      "final": "같은 변경안임을 확인한 승인서 작성",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀"
    },
    {
      "id": "3|report.3.report.flow.4",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.flow.4",
      "original": "apply로 승인안 반영",
      "action": "유지",
      "final": "apply로 승인안 반영",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.report.status.0.0",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.status.0.0",
      "original": "BANK-OM-001~007 등록자료",
      "action": "유지",
      "final": "BANK-OM-001~007 등록자료",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.report.status.0.1",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.status.0.1",
      "original": "1.13.0 현재 등록본 있음",
      "action": "유지",
      "final": "1.13.0 현재 등록본 있음",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.report.status.0.2",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.status.0.2",
      "original": "Manifest·Registry·Contract와 파생 목록이 있으며 준비도구가 현재 Git 이력과 비교할 수 있습니다.",
      "action": "수정",
      "final": "Manifest·Registry·Contract와 자동 생성 목록이 있으며 준비도구가 현재 Git 기록과 비교할 수 있습니다.",
      "reason": "‘파생’ 대신 자동으로 생성되는 파일을 직접 설명"
    },
    {
      "id": "3|report.3.report.status.1.1",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.status.1.1",
      "original": "구현·집중 테스트 완료",
      "action": "유지",
      "final": "구현·집중 테스트 완료",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.report.status.1.2",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.status.1.2",
      "original": "Git 분석, 사람 질문 분리, digest 승인, stale 차단, 잠금·원자 적용·rollback을 지원합니다.",
      "action": "수정",
      "final": "Git 분석, 사람 판단 질문 분리, 변경안 일치 확인, 승인 뒤 입력 변경 차단, 동시 실행 방지와 실패 시 복구를 지원합니다.",
      "reason": "digest를 ‘내용 확인값’으로 풀어 씀 · 구현 용어 대신 파일 교체와 실패 시 복구 행동을 설명"
    },
    {
      "id": "3|report.3.report.status.2.0",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.status.2.0",
      "original": "OM_TEMP 1.13.0 실제 plan",
      "action": "수정",
      "final": "현재 적용 예시 · OM_TEMP 1.13.0 plan",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|report.3.report.status.2.2",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.status.2.2",
      "original": "자동 변경 0건, 사람 판단 5건입니다. 실제 승인과 apply는 아직 실행하지 않았습니다.",
      "action": "유지",
      "final": "자동 변경 0건, 사람 판단 5건입니다. 실제 승인과 apply는 아직 실행하지 않았습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "3|report.3.report.status.3.0",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.status.3.0",
      "original": "commit 직후 자동 실행·PR 생성",
      "action": "유지",
      "final": "commit 직후 자동 실행·PR 생성",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.report.status.3.2",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.status.3.2",
      "original": "현재는 담당자가 plan 명령을 실행합니다. commit만으로 등록자료가 바뀌지 않습니다.",
      "action": "유지",
      "final": "현재는 담당자가 plan 명령을 실행합니다. commit만으로 등록자료가 바뀌지 않습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|report.3.report.status.4.2",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.status.4.2",
      "original": "required·간접 watch·Contract·owner는 기능 담당자가 결정합니다.",
      "action": "유지",
      "final": "required·간접 watch·Contract·owner는 기능 담당자가 결정합니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|report.3.report.next",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.report.next",
      "original": "상세 ‘검사 전 자동 갱신 범위·실행 절차’에서 준비 조건부터 plan·승인·apply·등록 검사·복구 절차를 순서대로 실행합니다. 준비 단계 완료는 APPLIED와 등록자료 검사 5종 PASS이며 배포 완료는 아닙니다.",
      "action": "수정",
      "final": "3-3 ‘자동 갱신 범위·전체 실행 절차’에서 준비 조건부터 plan·승인·apply·등록 검사·복구 절차를 순서대로 실행합니다. 준비 단계 완료는 APPLIED와 등록자료 검사 5종 PASS이며 배포 완료는 아닙니다.",
      "reason": "한 문장에 조건과 결과가 너무 많이 들어 있어 핵심 행동 중심으로 줄임"
    },
    {
      "id": "3|report.3.details.0.label",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.details.0.label",
      "original": "새 BANK-OM 등록",
      "action": "수정",
      "final": "3-1. 새 BANK-OM 등록",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|report.3.details.0.description",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.details.0.description",
      "original": "ID 발급부터 등록 검사까지의 전체 순서",
      "action": "유지",
      "final": "ID 발급부터 등록 검사까지의 전체 순서",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.details.1.label",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.details.1.label",
      "original": "기존 ID 후속 commit",
      "action": "수정",
      "final": "3-2. 기존 ID 후속 commit",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "3|report.3.details.1.description",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.details.1.description",
      "original": "같은 기능을 보완할 때 ID와 Manifest 갱신 방법",
      "action": "유지",
      "final": "같은 기능을 보완할 때 ID와 Manifest 갱신 방법",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.details.2.label",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.details.2.label",
      "original": "검사 전 자동 갱신 범위·실행 절차",
      "action": "수정",
      "final": "3-3. 자동 갱신 범위·전체 실행 절차",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|report.3.details.2.description",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.details.2.description",
      "original": "commit만으로 바뀌는지, apply가 어떤 파일을 갱신하는지와 재검사·복구까지",
      "action": "유지",
      "final": "commit만으로 바뀌는지, apply가 어떤 파일을 갱신하는지와 재검사·복구까지",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "3|report.3.details.3.description",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.details.3.description",
      "original": "changed·required·watch·assurance의 실제 의미",
      "action": "유지",
      "final": "changed·required·watch·assurance의 실제 의미",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.details.4.description",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.details.4.description",
      "original": "BANK-OM ID와 Manifest·Contract 연결",
      "action": "유지",
      "final": "BANK-OM ID와 Manifest·Contract 연결",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.details.5.description",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.details.5.description",
      "original": "파일 존재로 알 수 없는 업무 동작 기준",
      "action": "유지",
      "final": "파일 존재로 알 수 없는 업무 동작 기준",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "3|report.3.details.6.description",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.details.6.description",
      "original": "최초 source snapshot의 공용 파일–BANK-OM 연결표 생성·검증",
      "action": "수정",
      "final": "Registry source.snapshot_sha의 custom commit까지 여러 BANK-OM ID가 함께 바꾼 파일 확인",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "3|report.3.details.7.description",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.details.7.description",
      "original": "Repository layout과 Sensitive zones 운영 기준",
      "action": "수정",
      "final": "파일 영역 구분과 중요 경로의 운영 기준",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|report.4.chapter",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.chapter",
      "original": "4. OM_TEMP 업그레이드 연습",
      "action": "수정",
      "final": "4. 제품 코드 저장소 업그레이드 연습",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|report.4.summary",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.summary",
      "original": "4차 요약은 1.13.0→1.13.1 연습의 순서와 결과를 보여줍니다. 아래 상세 페이지에서 영향 확인, 실제 충돌, 보조 도구의 입출력과 실행 증거를 확인합니다.",
      "action": "수정",
      "final": "4차 요약은 1.13.0→1.13.1 연습의 순서와 결과를 보여줍니다. 4-1~4-7과 관련 검사 페이지에서 영향 확인, 실제 충돌, 보조 도구의 입출력, 검사 증거와 릴리즈 승격 기준을 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|report.4.report.question",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.question",
      "original": "1.13.0→1.13.1 연습에서 실제로 무엇을 확인했고, 무엇은 아직 검증하지 못했는가?",
      "action": "유지",
      "final": "1.13.0→1.13.1 연습에서 실제로 무엇을 확인했고, 무엇은 아직 검증하지 못했는가?",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|report.4.report.answer",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.answer",
      "original": "이번 연습은 공식 1.13.1 위에 BANK-OM 변경 기록을 ID별로 다시 적용해 충돌 위치와 소스 등록 상태를 확인한 진단입니다. BANK-OM-001~004는 각각 번역 JSON 18개에서 충돌했고, 005~007은 충돌 없이 적용됐습니다. 직전 custom branch와 새 patch branch를 통째로 합치는 목표 운영 방식(vendor-merge)과 실제 배포는 아직 검증하지 않았습니다.",
      "action": "수정",
      "final": "이번 연습은 공식 1.13.1 위에 BANK-OM 변경 기록을 ID별로 다시 적용해 충돌 위치와 소스 등록 상태를 확인한 진단입니다. BANK-OM-001~004는 각각 번역 JSON 18개에서 충돌했고, 005~007은 충돌 없이 적용됐습니다. 직전 커스텀 브랜치와 새 OpenMetadata 포크 브랜치를 통째로 합치는 목표 운영 방식(vendor-merge), 검증 완료 태그·릴리즈 브랜치 승격과 실제 운영 배포는 아직 검증하지 않았습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|report.4.report.facts.0.1",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.facts.0.1",
      "original": "001~004 · 각 18개 JSON",
      "action": "유지",
      "final": "001~004 · 각 18개 JSON",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|report.4.report.facts.0.2",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.facts.0.2",
      "original": "공식 1.13.1의 큰 번역 구조 변경과 BANK-OM 추가가 같은 JSON 영역에 있어 Git이 자동 병합을 중단했습니다.",
      "action": "유지",
      "final": "공식 1.13.1의 큰 번역 구조 변경과 BANK-OM 추가가 같은 JSON 영역에 있어 Git이 자동 병합을 중단했습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|report.4.report.facts.1.2",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.facts.1.2",
      "original": "이번 커밋별 재적용 진단에서는 Git 충돌 없이 순서대로 적용됐습니다.",
      "action": "유지",
      "final": "이번 커밋별 재적용 진단에서는 Git 충돌 없이 순서대로 적용됐습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|report.4.report.facts.2.1",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.facts.2.1",
      "original": "JSON 비중복 변경만 제안",
      "action": "수정",
      "final": "겹치지 않는 JSON 변경만 합침",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|report.4.report.facts.2.2",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.facts.2.2",
      "original": "같은 JSON 최종 항목을 양쪽이 함께 바꾸지 않은 경우에만 작업 파일을 수정하며 승인과 commit은 하지 않습니다.",
      "action": "수정",
      "final": "공식 코드와 BANK-OM이 같은 JSON 항목을 함께 바꾸지 않은 경우에만 작업 파일을 수정합니다. 승인, test, commit은 담당자가 진행합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|report.4.report.flow.0",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.flow.0",
      "original": "공식 1.13.1 준비",
      "action": "유지",
      "final": "공식 1.13.1 준비",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|report.4.report.flow.1",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.flow.1",
      "original": "BANK-OM별 재적용 진단",
      "action": "유지",
      "final": "BANK-OM별 재적용 진단",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|report.4.report.flow.3",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.flow.3",
      "original": "보조 도구 또는 수동 해결",
      "action": "유지",
      "final": "보조 도구 또는 수동 해결",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|report.4.report.status.0.0",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.status.0.0",
      "original": "BANK-OM별 충돌 위치",
      "action": "유지",
      "final": "BANK-OM별 충돌 위치",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|report.4.report.status.0.2",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.status.0.2",
      "original": "001~004의 18개 JSON 충돌과 005~007의 무충돌 적용 결과를 기록했습니다.",
      "action": "유지",
      "final": "001~004의 18개 JSON 충돌과 005~007의 무충돌 적용 결과를 기록했습니다.",
      "reason": "실제 파일·필드·Git 이름은 검사 입력과 같아야 하므로 유지하고 뜻은 같은 행의 설명에서 제시"
    },
    {
      "id": "4|report.4.report.status.1.2",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.status.1.2",
      "original": "이번 재적용 후보에서 Git 변경과 Manifest 연결을 확인했습니다.",
      "action": "수정",
      "final": "이번 commit별 재적용 진단 코드에서 Git 변경과 Manifest 연결을 확인했습니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|report.4.report.status.2.2",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.status.2.2",
      "original": "2개 PASS, 행내 서버·브라우저가 필요한 7개는 SKIP입니다.",
      "action": "유지",
      "final": "2개 PASS, 행내 서버·브라우저가 필요한 7개는 SKIP입니다.",
      "reason": "판정 이름과 그 판정이 뜻하는 결과가 함께 적혀 있어 유지"
    },
    {
      "id": "4|report.4.report.status.3.0",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.status.3.0",
      "original": "실제 vendor-merge 후보",
      "action": "수정",
      "final": "실제 vendor-merge 결과 commit",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|report.4.report.status.3.2",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.status.3.2",
      "original": "이번 후보는 커밋별 재적용으로 만들었으므로 운영 병합 방식의 증거가 아닙니다.",
      "action": "수정",
      "final": "이번 진단 코드는 commit별 재적용으로 만들었으므로 운영 병합 방식의 증거가 아닙니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|report.4.report.status.4.0",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.status.4.0",
      "original": "충돌 해결 승인·운영 배포",
      "action": "유지",
      "final": "충돌 해결 승인·운영 배포",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|report.4.report.status.4.2",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.status.4.2",
      "original": "승인자·승인 시각과 실제 배포 증거가 없습니다.",
      "action": "유지",
      "final": "승인자·승인 시각과 실제 배포 증거가 없습니다.",
      "reason": "누가·무엇을·언제 확인하는지가 현재 문장만으로 분명해 유지"
    },
    {
      "id": "4|report.4.report.next",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.report.next",
      "original": "patch branch와 직전 custom branch를 실제 vendor-merge 방식으로 합친 후보를 만들고, 충돌 해결 승인·전체 test·배포 대상 일치 검사를 수행해야 합니다.",
      "action": "수정",
      "final": "OpenMetadata 포크 브랜치와 직전 커스텀 브랜치를 실제 vendor-merge 방식으로 합친 새 custom branch commit을 만들고, 충돌 해결 승인·전체 test·검증 완료 태그·Release lock·릴리즈 브랜치 승격과 배포 대상 일치 검사를 수행해야 합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|report.4.details.0.description",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.details.0.description",
      "original": "patch 준비부터 tag·승인까지의 전체 순서",
      "action": "수정",
      "final": "OpenMetadata 포크 준비부터 릴리즈 브랜치 승격까지",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "4|report.4.details.1.description",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.details.1.description",
      "original": "실제 JSON 충돌과 보조 도구 실행 전후",
      "action": "유지",
      "final": "실제 JSON 충돌과 보조 도구 실행 전후",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|report.4.details.2.label",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.details.2.label",
      "original": "T42 공식 변경 영향",
      "action": "수정",
      "final": "2-3-1. T42 공식 변경 영향",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "4|report.4.details.2.description",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.details.2.description",
      "original": "병합 전에 다시 볼 경로를 찾는 검사",
      "action": "유지",
      "final": "병합 전에 다시 볼 경로를 찾는 검사",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|report.4.details.3.description",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.details.3.description",
      "original": "검사할 commit과 배포 파일 고정",
      "action": "유지",
      "final": "검사할 commit과 배포 파일 고정",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|report.4.details.4.description",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.details.4.description",
      "original": "실행한 test와 재시도 결과 기록",
      "action": "유지",
      "final": "실행한 test와 재시도 결과 기록",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "4|report.4.details.5.description",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.details.5.description",
      "original": "판정, 이유와 실행 대상을 함께 보관",
      "action": "유지",
      "final": "판정, 이유와 실행 대상을 함께 보관",
      "reason": "메뉴 제목·표 항목명·상태 라벨로 쓰이며 짧고 뜻이 분명해 유지"
    },
    {
      "id": "2|article.gate-index.0",
      "chapter": "2",
      "page": "검사기 전체 목록",
      "location": "article.gate-index.0",
      "original": "번호가 아니라 “어떤 질문에 답하는 검사인가”를 기준으로 먼저 찾습니다. 각 검사 상세 페이지에는 현재 구현 상태를 별도로 표시합니다.",
      "action": "수정",
      "final": "2-1 · 검사기 원리",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.gate-index.1",
      "chapter": "2",
      "page": "검사기 전체 목록",
      "location": "article.gate-index.1",
      "original": "과거 소스 재구성 또는 현재 코드의 공식 출발점, BANK-OM ID, 실제 변경 범위, 필수 변경과 중요 경로를 확인합니다.",
      "action": "수정",
      "final": "왼쪽의 2-2~2-5 분류에서 “어떤 질문에 답하는 검사인가”를 먼저 찾습니다. 각 검사 페이지에는 현재 구현 상태를 별도로 표시합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.gate-index.2",
      "chapter": "2",
      "page": "검사기 전체 목록",
      "location": "article.gate-index.2",
      "original": "새 공식 버전이 관련 파일을 바꿨는지, 유지 부담과 경로 정책이 유효한지 확인합니다.",
      "action": "수정",
      "final": "비상시 코드 복구 가능 여부와 검사 대상 custom branch commit의 공식 출발점, BANK-OM ID, 실제 변경 범위, 필수 변경과 중요 경로를 확인합니다. T25-R은 Git 기록이 유실된 경우에만 사용합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.gate-index.3",
      "chapter": "2",
      "page": "검사기 전체 목록",
      "location": "article.gate-index.3",
      "original": "필수 테스트가 존재하는지, 변경을 제거하면 실패하는지, 결과가 정확한 후보에 속하는지 확인합니다.",
      "action": "수정",
      "final": "새 공식 버전이 관련 파일을 바꿨는지, 유지 부담과 경로 정책이 유효한지 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.gate-index.4",
      "chapter": "2",
      "page": "검사기 전체 목록",
      "location": "article.gate-index.4",
      "original": "업그레이드 전 과정 증거와 검증한 코드·실제 배포 파일이 동일한지 확인합니다.",
      "action": "수정",
      "final": "필수 테스트가 존재하는지, 변경을 제거하면 실패하는지, 결과가 정확한 검사 대상 custom branch commit에서 나온 것인지 확인합니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|article.source-gates.0",
      "chapter": "2",
      "page": "소스·등록 검사",
      "location": "article.source-gates.0",
      "original": "이 묶음은 Java·TypeScript·Python 등 파일 종류와 관계없이 Git 변경 경로를 확인합니다. 다만 파일 내부의 업무 동작이 정상인지는 Contract test가 따로 확인합니다.",
      "action": "수정",
      "final": "2-2 · 검사기 원리",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|article.source-gates.1",
      "chapter": "2",
      "page": "소스·등록 검사",
      "location": "article.source-gates.1",
      "original": "각 개별 검사 페이지에 들어갈 내용",
      "action": "수정",
      "final": "이 묶음은 Java·TypeScript·Python 등 파일 종류와 관계없이 Git 변경 경로를 확인합니다. 다만 파일 내부의 업무 동작이 정상인지는 Contract test가 따로 확인합니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.source-gates.2",
      "chapter": "2",
      "page": "소스·등록 검사",
      "location": "article.source-gates.2",
      "original": "이 검사가 답하는 업무 질문",
      "action": "수정",
      "final": "각 개별 검사 페이지에 들어갈 내용",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.source-gates.3",
      "chapter": "2",
      "page": "소스·등록 검사",
      "location": "article.source-gates.3",
      "original": "언제 실행하며 누가 결과를 보는가",
      "action": "수정",
      "final": "이 검사가 답하는 업무 질문",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.source-gates.4",
      "chapter": "2",
      "page": "소스·등록 검사",
      "location": "article.source-gates.4",
      "original": "필수 입력 파일과 입력 변수",
      "action": "수정",
      "final": "언제 실행하며 누가 결과를 보는가",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.source-gates.5",
      "chapter": "2",
      "page": "소스·등록 검사",
      "location": "article.source-gates.5",
      "original": "검사기가 비교하는 순서",
      "action": "수정",
      "final": "필수 입력 파일과 입력 변수",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.source-gates.6",
      "chapter": "2",
      "page": "소스·등록 검사",
      "location": "article.source-gates.6",
      "original": "PASS·APPROVAL·BLOCK 조건",
      "action": "수정",
      "final": "검사기가 비교하는 순서",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|article.source-gates.7",
      "chapter": "2",
      "page": "소스·등록 검사",
      "location": "article.source-gates.7",
      "original": "실제 OM_TEMP 입력·출력 예시",
      "action": "수정",
      "final": "PASS·APPROVAL·BLOCK 조건",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|article.source-gates.8",
      "chapter": "2",
      "page": "소스·등록 검사",
      "location": "article.source-gates.8",
      "original": "검사만으로 알 수 없는 것과 보완 검사",
      "action": "수정",
      "final": "현재 적용 예시인 OM_TEMP의 실제 입력·출력",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.source-gates.9",
      "chapter": "2",
      "page": "소스·등록 검사",
      "location": "article.source-gates.9",
      "original": "실행 명령과 관련 구현·테스트 코드",
      "action": "수정",
      "final": "검사만으로 알 수 없는 것과 보완 검사",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|article.upgrade-gates.0",
      "chapter": "2",
      "page": "업그레이드 영향 검사",
      "location": "article.upgrade-gates.0",
      "original": "업그레이드 영향 검사 묶음",
      "action": "수정",
      "final": "2-3 · 검사기 원리",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.upgrade-gates.1",
      "chapter": "2",
      "page": "업그레이드 영향 검사",
      "location": "article.upgrade-gates.1",
      "original": "이전 공식 버전과 새 공식 버전의 차이가 BANK-OM 커스터마이징에 영향을 줄 가능성이 있는지 확인합니다. “영향 가능성”과 “실제 Git 충돌”은 같은 의미가 아닙니다.",
      "action": "수정",
      "final": "업그레이드 영향 검사 묶음",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.upgrade-gates.2",
      "chapter": "2",
      "page": "업그레이드 영향 검사",
      "location": "article.upgrade-gates.2",
      "original": "T42의 APPROVAL은 관련 경로가 공식 버전에서 바뀌었다는 뜻입니다. 실제 병합 충돌 여부와 기능 오류는 병합 기록·Contract test에서 별도로 확인합니다.",
      "action": "수정",
      "final": "이전 공식 버전과 새 공식 버전의 차이가 BANK-OM 커스터마이징에 영향을 줄 가능성이 있는지 확인합니다. “영향 가능성”과 “실제 Git 충돌”은 같은 의미가 아닙니다.",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|article.runtime-gates.0",
      "chapter": "2",
      "page": "테스트·실행 검사",
      "location": "article.runtime-gates.0",
      "original": "테스트·실행 검사 묶음",
      "action": "수정",
      "final": "2-4 · 검사기 원리",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|article.runtime-gates.1",
      "chapter": "2",
      "page": "테스트·실행 검사",
      "location": "article.runtime-gates.1",
      "original": "테스트 코드가 존재한다는 사실, 커스터마이징 제거 시 테스트가 실패한다는 사실, 실제 후보에서 테스트가 성공했다는 사실을 서로 다른 검사로 나눕니다.",
      "action": "수정",
      "final": "테스트·실행 검사 묶음",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.runtime-gates.2",
      "chapter": "2",
      "page": "테스트·실행 검사",
      "location": "article.runtime-gates.2",
      "original": "등록한 Python pytest 파일과 함수가 존재",
      "action": "수정",
      "final": "테스트 코드가 존재한다는 사실, 커스터마이징 제거 시 테스트가 실패한다는 사실, 실제 검사 대상 custom branch commit에서 테스트가 성공했다는 사실을 서로 다른 검사로 나눕니다.",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.runtime-gates.3",
      "chapter": "2",
      "page": "테스트·실행 검사",
      "location": "article.runtime-gates.3",
      "original": "그 테스트가 실제로 성공했는지",
      "action": "수정",
      "final": "등록한 Python pytest 파일과 함수가 존재",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.runtime-gates.4",
      "chapter": "2",
      "page": "테스트·실행 검사",
      "location": "article.runtime-gates.4",
      "original": "커스터마이징을 제거하면 필수 테스트가 실패",
      "action": "수정",
      "final": "그 테스트가 실제로 성공했는지",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.runtime-gates.5",
      "chapter": "2",
      "page": "테스트·실행 검사",
      "location": "article.runtime-gates.5",
      "original": "모든 미확인 동작이 보호되는지",
      "action": "수정",
      "final": "커스터마이징을 제거하면 필수 테스트가 실패",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.runtime-gates.6",
      "chapter": "2",
      "page": "테스트·실행 검사",
      "location": "article.runtime-gates.6",
      "original": "테스트 결과가 정확한 후보 commit·배포 파일에 연결",
      "action": "수정",
      "final": "모든 미확인 동작이 보호되는지",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|article.runtime-gates.7",
      "chapter": "2",
      "page": "테스트·실행 검사",
      "location": "article.runtime-gates.7",
      "original": "테스트 설계 자체가 충분한지",
      "action": "수정",
      "final": "테스트 결과가 정확한 검사 대상 commit·배포 파일에 연결",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.runtime-gates.8",
      "chapter": "2",
      "page": "테스트·실행 검사",
      "location": "article.runtime-gates.8",
      "original": "공식 원본 대비 새 TypeScript 오류 증가 여부",
      "action": "수정",
      "final": "테스트 설계 자체가 충분한지",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.runtime-gates.9",
      "chapter": "2",
      "page": "테스트·실행 검사",
      "location": "article.runtime-gates.9",
      "original": "Java·Python 오류나 브라우저 실제 동작",
      "action": "수정",
      "final": "공식 원본 대비 새 TypeScript 오류 증가 여부",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|article.release-gates.0",
      "chapter": "2",
      "page": "업그레이드·배포 검사",
      "location": "article.release-gates.0",
      "original": "업그레이드·배포 검사 묶음",
      "action": "수정",
      "final": "2-5 · 검사기 원리",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|article.release-gates.1",
      "chapter": "2",
      "page": "업그레이드·배포 검사",
      "location": "article.release-gates.1",
      "original": "소스 검사 PASS만으로 배포를 승인하지 않도록, 업그레이드 단계의 증거와 실제 배포 대상이 검증한 대상과 같은지를 확인합니다.",
      "action": "수정",
      "final": "업그레이드·배포 검사 묶음",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.release-gates.2",
      "chapter": "2",
      "page": "업그레이드·배포 검사",
      "location": "article.release-gates.2",
      "original": "같은 검사 대상에서 migration·검색·rollback 등 12개 업그레이드 단계를 모두 실행했는지 확인",
      "action": "수정",
      "final": "소스 검사 PASS만으로 배포를 승인하지 않도록, 업그레이드 단계의 증거와 실제 배포 대상이 검증한 대상과 같은지를 확인합니다.",
      "reason": "구현 용어 대신 파일 교체와 실패 시 복구 행동을 설명"
    },
    {
      "id": "2|article.release-gates.3",
      "chapter": "2",
      "page": "업그레이드·배포 검사",
      "location": "article.release-gates.3",
      "original": "판정 코드 구현 · 실제 행내 실행 증거 대기",
      "action": "수정",
      "final": "같은 검사 대상에서 DB 변경·검색·이전 버전 복귀 등 12개 업그레이드 단계를 모두 실행했는지 확인",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|article.release-gates.4",
      "chapter": "2",
      "page": "업그레이드·배포 검사",
      "location": "article.release-gates.4",
      "original": "검증한 commit·이미지·Helm 설정과 실제 배포 대상이 같은지 확인",
      "action": "수정",
      "final": "판정 코드 구현 · 실제 행내 실행 증거 대기",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|article.release-gates.5",
      "chapter": "2",
      "page": "업그레이드·배포 검사",
      "location": "article.release-gates.5",
      "original": "판정 코드 구현 · 실제 배포 환경 연결 대기",
      "action": "수정",
      "final": "검증한 commit·이미지·Helm 설정과 실제 배포 대상이 같은지 확인",
      "reason": "축약된 나열만으로 뜻이 갈릴 수 있어 실제 확인 대상과 행동을 문장으로 풂"
    },
    {
      "id": "2|article.release-gates.6",
      "chapter": "2",
      "page": "업그레이드·배포 검사",
      "location": "article.release-gates.6",
      "original": "입력, 12개 단계, 판정과 아직 없는 실행 증거",
      "action": "수정",
      "final": "판정 코드 구현 · 실제 배포 환경 연결 대기",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "2|article.release-gates.7",
      "chapter": "2",
      "page": "업그레이드·배포 검사",
      "location": "article.release-gates.7",
      "original": "검증 대상과 실제 배포 대상 비교 방법",
      "action": "수정",
      "final": "입력, 12개 단계, 판정과 아직 없는 실행 증거",
      "reason": "가리키는 대상이나 다음 행동이 모호해 주체·입력·결과를 직접 명시"
    },
    {
      "id": "1|topic.repositories.sections.3.0",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.sections.3.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "Registry의 source 값",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.repositories.sections.3.1",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.sections.3.1",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "검사기 저장소의 Registry에는 `source.repository`, `source.upstream_sha`, `source.snapshot_sha`가 있습니다. 검사기는 이 값으로 어떤 제품 코드 저장소와 어떤 공식·커스터마이징 commit을 기준으로 등록자료를 만들었는지 확인합니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.repositories.sections.4.1",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.sections.4.1",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "제품 코드 저장소는 easyseop/OM_TEMP, 검사기 저장소는 easyseop/openmetadata-test입니다. easyseop/OpenMetadata는 과거 구현 사례를 확인할 때만 사용하는 참고 저장소입니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.repositories.operationCases.1.1",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.1.1",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "해당 제품 버전의 검사 대상 custom branch commit과 등록자료만 갱신",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.repositories.operationCases.2.1",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.2.1",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "새 버전 등록자료와 공식 비교 결과를 별도로 준비",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.repositories.operationCases.3.0",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.3.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "제품 코드 저장소의 URL이 바뀌거나, 제품 코드 저장소와 검사기 저장소를 다른 저장소로 분리·통합한 경우",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.repositories.operationCases.3.1",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.3.1",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "저장소 연결 구조를 다시 정함",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.repositories.operationCases.3.2",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.3.2",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "운영 책임자가 어느 저장소가 제품 코드와 검사자료를 각각 관리할지 먼저 승인합니다. 담당자는 Registry의 source.repository, CI checkout URL, 실행 명령의 로컬 경로, 접근 권한과 위키의 현재 적용 예시를 새 구조에 맞게 바꿉니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.repositories.operationCases.3.3",
      "chapter": "1",
      "page": "상세 · 제품 코드 저장소와 검사기 저장소",
      "location": "topic.repositories.operationCases.3.3",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "구조 변경 승인 기록과 이전·새 URL 대응표를 보관합니다. 준비도구 plan, 등록 검증과 소스 검사를 새 저장소 연결로 모두 다시 실행하고 첫 성공 결과를 남깁니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.branches.sections.0.0",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.sections.0.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "fork/om-<version> · OpenMetadata 포크 브랜치",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.branches.sections.1.0",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.sections.1.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "custom/om-<version> · 커스텀 브랜치",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.branches.sections.2.0",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.sections.2.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "verified/om-<version>-bank.<번호> · 검증 완료 태그",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.branches.sections.3.0",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.sections.3.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "release/om-<version> · 릴리즈 브랜치",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.branches.sections.4.0",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.sections.4.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "현재 OM_TEMP 브랜치 이름과 운영에 사용할 이름",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.branches.sections.4.1",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.sections.4.1",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "현재 OM_TEMP 원격에는 기존 이름인 patch/om-1.13.0이 남아 있습니다. 실제 운영을 시작하기 전에 공식 코드 브랜치를 fork/om-<version> 이름으로 전환하고 release/om-<version> 브랜치를 생성해야 합니다. CLI 옵션 --patch-ref는 프로그램이 기존 옵션명을 하위 호환용으로 유지하므로 그대로 사용합니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.branches.sections.5.1",
      "chapter": "1",
      "page": "상세 · OpenMetadata 포크·커스텀·릴리즈 브랜치",
      "location": "topic.branches.sections.5.1",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "새 공식 버전의 OpenMetadata 포크 브랜치를 만들고, 직전 커스텀 브랜치의 BANK-OM 변경을 새 커스텀 브랜치에 합칩니다. 충돌 해결과 검사를 통과하면 새 검증 완료 태그를 만들고, 승인 후 새 릴리즈 브랜치를 운영 기준으로 사용합니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.identity.operationCases.0.3",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.operationCases.0.3",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "추가 조치가 없습니다. 정기 점검이 필요한 경우에만 제품 코드 저장소의 최종 commit과 기존 검사 결과의 대상이 같은지 확인한 기록을 남깁니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|topic.identity.operationCases.2.1",
      "chapter": "1",
      "page": "상세 · BANK-OM ID, commit 메시지와 Git SHA",
      "location": "topic.identity.operationCases.2.1",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "새 ID와 기능 기준은 담당자가 정하고, 변경안 생성·반영은 자동",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.sections.3.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.3.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "승인 후 apply가 갱신",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.sections.5.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.5.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "현재 적용 예시의 두 저장소",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.sections.9.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.9.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "등록 상태 내용 확인값",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.sections.10.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.10.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "검사 대상 코드(Candidate)",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.sections.13.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.13.1",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "APPLIED가 나온 뒤 등록자료 5종을 검사하고, 공식 버전에서 출발한 최종 코드로 소스 검사를 실행합니다. 소스 검사 PASS는 build, 실행 환경, 배포까지 통과했다는 뜻이 아닙니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.sections.14.1",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.sections.14.1",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "제안 폴더 전체, 실제 승인서, apply 결과, 등록 검증 결과와 동일 Candidate lock의 후속 검사 결과를 삭제하지 않고 함께 보관합니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.preparationFilesTitle",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.preparationFilesTitle",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "검사 전에 준비하는 파일별 자동화 범위",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.preparationFilesIntro",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.preparationFilesIntro",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "아래 표는 일반적인 후속 commit을 등록할 때를 기준으로 합니다. ‘자동’은 commit만 하면 저절로 실행된다는 뜻이 아닙니다. 담당자가 plan을 실행하고 변경안을 승인한 뒤 apply를 실행해야 실제 등록 폴더에 반영됩니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.preparationFiles.0.status",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.preparationFiles.0.status",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "부분 자동 · 정책값은 직접 수정 필요",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.preparationFiles.1.status",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.preparationFiles.1.status",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "새 ID일 때만 조건부 자동",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.preparationFiles.3.status",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.preparationFiles.3.status",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "자동 생성 · 직접 수정 금지",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.preparationFiles.4.status",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.preparationFiles.4.status",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "자동 생성 · 직접 수정 금지",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.preparationFiles.5.status",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.preparationFiles.5.status",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "초기 기준 생성만 · 일반 후속 commit에서는 유지",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.preparationFiles.6.status",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.preparationFiles.6.status",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "초기 기준 생성만 · 일반 후속 commit에서는 유지",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.preparationFiles.7.status",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.preparationFiles.7.status",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "초기 기준 생성만 · 일반 후속 commit에서는 유지",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.preparationFiles.10.status",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.preparationFiles.10.status",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "plan 실행 시 자동 생성 · 직접 수정 금지",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.preparationFiles.11.status",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.preparationFiles.11.status",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "양식만 자동 · 승인 내용은 직접 작성 필요",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.preparationFilesNote",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.preparationFilesNote",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "빨간색 ‘직접 수정 필요’ 파일은 준비도구가 업무 의미를 추측해 대신 작성하지 않습니다. 수정한 뒤에는 기존 proposal이나 승인서를 재사용하지 말고 새 출력 폴더에서 plan을 다시 실행한 다음 등록 검증을 다시 수행합니다. 현재 digest는 주요 등록자료와 제안 내용을 고정하지만, 준비도구 자체의 Git commit이나 버전을 승인서에 별도 필드로 고정하는 기능은 추가 설계 대상입니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.conditionMap.0.0",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.conditionMap.0.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "제품 코드 저장소의 작업 폴더",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|topic.automation.exampleIntro",
      "chapter": "3",
      "page": "상세 · 검사 전 자동 갱신 범위와 전체 실행 절차",
      "location": "topic.automation.exampleIntro",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "아래 블록 전체를 한 번에 복사해 실행하는 것이 아닙니다. 0번부터 한 단계씩 실행하고, 각 단계의 주석에 적힌 예상 결과를 확인한 뒤 다음 번호로 이동합니다. 1번 plan 결과가 BLOCKED 또는 ANALYSIS_ERROR이면 2번으로 가지 않고 원인을 수정해 plan부터 다시 실행합니다. REVIEW_REQUIRED이면 담당자 검토와 승인을 거친 뒤 2~4번을 진행합니다. 4번 결과가 APPLIED일 때만 5번 등록 검사를 실행합니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|topic.upgrade.sections.4.0",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.sections.4.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "5. 등록 변경안 승인·반영",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|topic.upgrade.sections.6.0",
      "chapter": "4",
      "page": "상세 · 공식 버전 업그레이드 절차",
      "location": "topic.upgrade.sections.6.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "7. 검증 완료 태그·릴리즈 승격",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|topic.conflicts.stageMap.0.1",
      "chapter": "4",
      "page": "상세 · Git 충돌과 해결 보조 도구",
      "location": "topic.conflicts.stageMap.0.1",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "양쪽 변경이 시작되기 전 공통 내용",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|file.registry.fields.0.4",
      "chapter": "3",
      "page": "상세 · Customization Registry",
      "location": "file.registry.fields.0.4",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "현재 적용 예시: easyseop/OM_TEMP",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|file.source_snapshot_owners.scopeFlow.2.0",
      "chapter": "3",
      "page": "상세 · Registry source.snapshot_sha의 custom commit에서 파일별 BANK-OM ID를 기록한 연결표",
      "location": "file.source_snapshot_owners.scopeFlow.2.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "최신 커스텀 브랜치 범위",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|file.layout.fields.2.3",
      "chapter": "3",
      "page": "상세 · 코드 경로 분류표",
      "location": "file.layout.fields.2.3",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "제품 코드 저장소 구조 분석",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|file.zones.title",
      "chapter": "3",
      "page": "상세 · 중요 경로 정책(Sensitive zones)",
      "location": "file.zones.title",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "중요 경로 정책(Sensitive zones)",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.candidate_lock.fields.4.4",
      "chapter": "4",
      "page": "상세 · Candidate lock",
      "location": "file.candidate_lock.fields.4.4",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "현재 적용 예시: easyseop/OM_TEMP",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.purpose",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.purpose",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "운영에 올릴 릴리즈 브랜치의 정확한 commit, 검증 완료 태그, 이미지·Helm 설정과 검사 결과를 하나의 배포 대상으로 묶습니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.created",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.created",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "필수 검사가 끝나고 운영 승인자가 릴리즈 브랜치로 승격할 대상을 선택할 때 새로 만듭니다. 현재 OM_TEMP 연습에는 아직 생성된 Release lock이 없습니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.update",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.update",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "코드 commit, 검증 완료 태그, 이미지, Helm 설정 또는 연결한 검사 결과 중 하나라도 바뀌면 기존 파일을 고치지 않고 새 Release lock을 만듭니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.owner",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.owner",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "배포 담당자가 기술 값을 수집하고 운영 승인자가 어떤 검증 완료 태그를 릴리즈 브랜치에 반영할지 승인합니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.readers",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.readers",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "T91과 배포 자동화가 검증한 대상과 실제 릴리즈 브랜치·배포 파일이 같은지 확인할 때 사용합니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.fields.0.2",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.fields.0.2",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "운영 배포에 사용하는 릴리즈 브랜치",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.fields.1.2",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.fields.1.2",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "릴리즈 브랜치가 가리켜야 하는 정확한 commit",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.fields.2.2",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.fields.2.2",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "필수 검사를 통과한 같은 commit의 고정 태그",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.fields.3.2",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.fields.3.2",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "배포할 컨테이너 이미지의 내용 확인값",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.fields.4.2",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.fields.4.2",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "배포 설정 묶음의 내용 확인값",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.fields.5.2",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.fields.5.2",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "Candidate lock·Test run set·검사 결과의 내용 확인값",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.updateReason",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.updateReason",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "검증 완료 태그가 가리키는 commit과 운영에 사용할 이미지·설정·검사 결과를 한 묶음으로 승인하기 위해 만듭니다. 이 파일을 만들었다고 배포가 끝난 것은 아니며, T91 일치 확인과 사람의 최종 승인이 남습니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.commands.0.label",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.commands.0.label",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "현재 상태 · 형식과 판정 코드만 준비됨",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.commands.0.meaning",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.commands.0.meaning",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "현재 OM_TEMP에는 실제 이미지·Helm 내용 확인값과 운영 승인이 없으므로 Release lock을 생성하지 않습니다. 운영 연결 뒤에는 전용 생성 명령이 필요합니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|file.release_lock.storage",
      "chapter": "4",
      "page": "상세 · Release lock",
      "location": "file.release_lock.storage",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "배포 실행별 불변 증거로 보관합니다. 기존 Release lock을 덮어쓰지 않고 릴리즈 브랜치·버전·실행 번호가 다른 새 파일을 만듭니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|gate.t25r.inputs.1.2",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.inputs.1.2",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "보관해 둔 제품 코드 폴더",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|gate.t25r.inputs.2.0",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.inputs.2.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "파일–BANK-OM 연결표",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|gate.t25r.inputs.3.0",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.inputs.3.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "공식 코드와 보관 코드의 차이 목록",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|gate.t25r.inputs.3.1",
      "chapter": "2",
      "page": "상세 · T25-R · Git 기록 유실 시 코드 복구 확인(비상용)",
      "location": "gate.t25r.inputs.3.1",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "공식 코드와 보관 코드 사이에서 달라진 모든 파일 경로",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|gate.t41.inputs.1.0",
      "chapter": "2",
      "page": "상세 · T41 · 중요 시스템 경로 확인",
      "location": "gate.t41.inputs.1.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "중요 경로 정책(Sensitive zones)",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|gate.t42.inputs.2.0",
      "chapter": "2",
      "page": "상세 · T42 · 공식 변경 영향 확인",
      "location": "gate.t42.inputs.2.0",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "직접 참조 가능성이 있는 경로",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|gate.t62.inputs.1.2",
      "chapter": "2",
      "page": "상세 · T62 · 테스트 결과와 검사 대상 commit 연결 확인",
      "location": "gate.t62.inputs.1.2",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "test_tibero.py::test_connection_schema_roundtrip · 1차 시도 · pass",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|report.1.report.facts.0.1",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.facts.0.1",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "OpenMetadata 포크 브랜치",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|report.1.report.flow.5",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.flow.5",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "검증 완료 태그·Release lock",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|report.1.report.flow.6",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.report.flow.6",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "릴리즈 브랜치 승격·운영 배포",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|report.1.details.0.label",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.details.0.label",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "1-1. 제품·검사기 저장소 역할",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|report.1.details.1.label",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.details.1.label",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "1-2. 포크·커스텀·릴리즈 브랜치",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "1|report.1.details.3.label",
      "chapter": "1",
      "page": "요약",
      "location": "report.1.details.3.label",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "4-1. 업그레이드 절차",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|report.2.details.0.label",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.details.0.label",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "2-1. 검사기 전체 목록",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|report.2.details.1.label",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.details.1.label",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "2-2. 소스·등록 검사",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|report.2.details.2.label",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.details.2.label",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "2-3. 업그레이드 영향 검사",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|report.2.details.3.label",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.details.3.label",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "2-4. 테스트·실행 검사",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|report.2.details.4.label",
      "chapter": "2",
      "page": "요약",
      "location": "report.2.details.4.label",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "2-5. 업그레이드·배포 검사",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|report.3.details.6.label",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.details.6.label",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "3-7. Registry snapshot_sha의 공용 경로",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "3|report.3.details.7.label",
      "chapter": "3",
      "page": "요약",
      "location": "report.3.details.7.label",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "3-10. 코드 경로 분류표",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|report.4.details.0.label",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.details.0.label",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "4-1. 공식 버전 업그레이드",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|report.4.details.1.label",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.details.1.label",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "4-2. Git 충돌·해결",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|report.4.details.5.label",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.details.5.label",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "4-5. 검사 결과 파일",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "4|report.4.details.6.description",
      "chapter": "4",
      "page": "요약",
      "location": "report.4.details.6.description",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "검증 완료 태그와 운영 릴리즈 브랜치·배포 파일 연결",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|article.gate-index.5",
      "chapter": "2",
      "page": "검사기 전체 목록",
      "location": "article.gate-index.5",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "업그레이드 전 과정 증거와 검증한 코드·실제 배포 파일이 동일한지 확인합니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|article.source-gates.10",
      "chapter": "2",
      "page": "소스·등록 검사",
      "location": "article.source-gates.10",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "실행 명령과 관련 구현·테스트 코드",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|article.upgrade-gates.3",
      "chapter": "2",
      "page": "업그레이드 영향 검사",
      "location": "article.upgrade-gates.3",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "T42의 APPROVAL은 관련 경로가 공식 버전에서 바뀌었다는 뜻입니다. 실제 병합 충돌 여부와 기능 오류는 병합 기록·Contract test에서 별도로 확인합니다.",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|article.runtime-gates.10",
      "chapter": "2",
      "page": "테스트·실행 검사",
      "location": "article.runtime-gates.10",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "Java·Python 오류나 브라우저 실제 동작",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    },
    {
      "id": "2|article.release-gates.8",
      "chapter": "2",
      "page": "업그레이드·배포 검사",
      "location": "article.release-gates.8",
      "original": "해당 문장 없음",
      "action": "추가",
      "final": "검증 대상과 실제 배포 대상 비교 방법",
      "reason": "처음 읽는 사람이 바로 물을 내용을 같은 위치에 추가"
    }
  ]
};
