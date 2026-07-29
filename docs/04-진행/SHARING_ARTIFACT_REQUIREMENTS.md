# OpenMetadata 공유문서 요구사항 정본

> 갱신 기준: 2026-07-30 KST
> 목적: 처음 보는 부서 독자가 “왜 필요한가 → 어떤 방식인가 → 무엇을
> 준비하는가 → 실제로 무엇이 확인됐는가 → 무엇이 남았는가”를 끊김 없이
> 판단하게 한다.

## 1. 대상 독자와 문장 원칙

- 대상은 경영진, 책임자, 비개발자와 개발자다.
- 커스터마이징, repository, branch, commit, Manifest, API, test, Git commit
  SHA, digest처럼 실제 업무 용어는 유지하고 바로 옆 문장으로 뜻을 설명한다.
- 영수증, 요리, 레시피, 짐, 신호등처럼 코드와 무관한 비유를 사용하지 않는다.
- “제품”, “후보”, “현재”, “적용”처럼 대상이 여러 개인 말은 저장소·branch·
  commit 또는 코드 상태를 함께 쓴다.
- BANK-OM ID, Git commit 메시지와 Git commit SHA를 구분한다.
- 구현, 소스 검사, 행내 환경 실행, 담당자 승인, 실제 배포를 같은 완료 상태로
  표현하지 않는다.
- 처음 나온 내부 개념에는 “OpenMetadata 기본 기능인지, 이 프로젝트가 만든
  규칙인지, 특정 사례에만 해당하는지”를 명시한다.

## 2. 현재 읽는 순서와 페이지 역할

| 순서 | 페이지 | 이 페이지가 답하는 질문 |
|---|---|---|
| 1 | 목적과 브랜치 전략 | 공식 OpenMetadata를 계속 업데이트하면서 행내 커스터마이징을 어떤 branch 흐름으로 유지하는가? |
| 2 | 검사기 원리 | 각 검사는 어떤 입력을 읽고 어떤 방법으로 PASS·APPROVAL·BLOCK을 판단하는가? |
| 3 | 검사 전 사전환경 설정 | Manifest·Registry·Contract를 언제 만들고 실제 Git diff를 어떻게 등록하는가? |
| 4 | OM_TEMP 코드 업그레이드 연습 | commit별 재적용 진단에서 어떤 충돌이 발생했고 어디까지 확인했는가? |
| 5 | 부록 · 과거 참고 코드 검사 | 과거 `849ae756...` 코드에서 소스 검사 결과가 어떤 형태로 나왔는가? |

페이지를 한 파일로 합치지 않는다. 목적·검사 방법·설정·실제 결과는 판단 범위가
달라 합치면 검사 PASS와 배포 완료가 다시 섞인다. 대신 모든 페이지 위·아래에
이전·다음 이동을 제공한다.

Manifest 전체 필드 설명은 3번 본문을 늘리지 않도록
`OM_TEMP_관리파일_필드_사전_미리보기.html`로 분리한다. 이 사전은 3번에서
왕복할 수 있어야 한다.

## 3. 페이지별 필수 내용

### 1 · 목적과 브랜치 전략

- `easyseop/OM_TEMP`는 현재 업그레이드 연습 코드,
  `easyseop/openmetadata-test`는 기준자료·검사기·결과·문서 저장소라고 설명한다.
- 목표 운영 전략은 직전 `custom` 전체 이력에 새 공식 `patch`를 병합하는
  `vendor-merge`라고 명시한다.
- 도식은 `공식 새 버전 → patch`, `직전 custom`, 두 입력의 병합 지점, Git
  충돌 해결, 검사 BLOCK 보완, 배포 후보 tag, 다음 버전 Cycle을 보여준다.
- Git 충돌과 검사 BLOCK은 서로 다른 문제라고 설명한다.
- 기존 기능의 업그레이드 보완은 같은 BANK-OM ID를 유지하며, 독립 업무 기능이
  생겼을 때만 새 ID를 만든다고 설명한다.
- BANK-OM ID, `patch/custom` 이름과 반복 절차는 OpenMetadata가 기본 제공하는
  규칙이 아니라 이 프로젝트의 운영 방식이라고 표시한다.

### 2 · 검사기 원리

- 특정 commit의 결과를 섞지 않고 검사 방법과 한계만 설명한다.
- 처음에는 A 소스 기준, B 업그레이드 영향, C 테스트·실행, D 승격·배포의
  검사기 지도를 보여주고, 세부 방법은 펼치기로 둔다.
- 각 검사는 `입력 → 판단 방법 → 출력 → 실패·예외`를 설명한다.
- T번호는 이 프로젝트 검사기 개발계획과 결과 파일에서 쓰는 태스크 ID이며
  OpenMetadata 기본 기능이 아니라고 설명한다.
- Git·파일 경로 검사는 언어에 관계없이 적용할 수 있지만 파일 내부 의미나 실제
  동작을 이해하는 검사는 아니라고 구분한다.
- T60-I는 현재 Python pytest 코드 존재만 확인하고, Java JUnit·TypeScript Jest
  직접 확인은 추가 개발이라고 설명한다.
- 다음 질문에 답해야 한다.

| 검사 | 반드시 설명할 내용 |
|---|---|
| T25-R | 빈 줄 한 줄도 일반 파일 차이로 판단하며 snapshot 재구성 때만 쓰는 이유 |
| T25 | 공식 commit 포함 관계를 Git으로 확인하는 방법 |
| T26 | 모든 활성 BANK-OM의 필수 구현·Contract·test 연결 확인 |
| T30·T31 | 공식 원본 이후 모든 행내 commit의 ID와 순서를 읽는 방법 |
| T40 | 실제 변경 전체와 allowed, 최종 필수 구현과 required의 차이 |
| T41 | AST가 아니라 민감 경로 정책을 비교하며 의미 분석은 별도라는 한계 |
| T42 | 공식 버전 간 변경과 `upgrade_watch`를 비교하는 방법 |
| T43 | 규모·공유 파일·충돌률의 입력 출처와 자동화가 남은 부분 |
| T93 | 실제 변경과 Manifest 일치, 경로 정책 노후화를 구분하는 방법 |
| T60-I·T61·T62·T63 | test 존재, 누락 탐지력, 결과 결속, TypeScript 비교의 차이 |
| T90·T91 | 업그레이드 전 과정과 실제 배포 파일 일치에 필요한 외부 증거 |

### 3 · 검사 전 사전환경 설정

- 실제 OM_TEMP 1.13.0 commit diff를 기능 단위로 묶어 BANK-OM-001~007
  Manifest를 만든 근거를 보여준다.
- Manifest는 ID 최초 등록 때 한 번 만들고, 업그레이드 때 같은 ID의 새 버전
  등록 묶음으로 복사해 달라진 경로·검증 기준만 갱신한다고 설명한다.
- `allowed_changed_paths`는 해당 BANK-OM commit의 전체 실제 변경,
  `required_changed_paths`는 빠지면 즉시 기능 미적용으로 판단할 핵심 구현,
  `candidate_additional_paths`는 같은 ID 후속 commit에서 최초 등록 범위에
  새로 들어온 경로,
  `upgrade_watch`는 다음 공식 버전과 비교할 변경·의존 경로라고 설명한다.
- 같은 ID의 후속 commit은 commit 메시지에 기존
  `Customization-ID: BANK-OM-NNN`을 그대로 사용한다. 기존 등록 파일만 다시
  수정하면 Manifest 경로 목록은 유지하고, 새 파일이 생긴 경우에만 생성기가
  `candidate_additional_paths` 초안을 만든다는 실제 예시를 포함한다.
- Registry, Contracts, 공용 파일 소유정보, 전체 변경 목록, Repository layout,
  Sensitive zones, Candidate lock, 선택적 Patch-lock과 결과 파일의 의미·작성
  시점·사용 검사를 설명한다.
- Patch-lock은 `patch-replay`·복구·재현을 선택할 때만 쓰며
  `vendor-merge` 소스 검사의 필수 자료가 아니라고 표시한다.
- 이 기준자료는 OpenMetadata 실행 설정이나 직원용 화면이 아니라
  `easyseop/openmetadata-test`의 내부 관리 파일이라고 표시한다.

### 4 · OM_TEMP 코드 업그레이드 연습

- 공식 1.13.0→1.13.1 변경과 watch 비교, branch·검사 대상 SHA, commit별 적용,
  실제 충돌, 해결 diff, 소스 검사 결과, 완료·미완료를 순서대로 보여준다.
- `cherry-pick`은 충돌을 만들기 위한 필수 명령이 아니라 BANK-OM별 충돌을
  분리해 기록한 이번 진단 방법이라고 설명한다.
- 충돌 표식 `<<<<<<<`, `=======`, `>>>>>>>`와 공식 영역·BANK-OM 영역,
  해결 후 추가 항목을 색과 설명으로 구분한다.
- 공식 1.13.1과 BANK-OM이 같은 JSON 항목 값을 다르게 고친 것이 아니라,
  공통 기준에서 같은 JSON 객체의 같은 줄 주변을 각각 변경해 Git의 줄 단위
  병합이 중단됐다는 원인을 먼저 설명한다. 좌우 발췌는 일대일 줄 비교 화면이
  아니라 Git이 선택하지 못한 두 버전의 대표 부분임을 명시한다.
- JSON 충돌 보조 도구가 실제로 존재하는지, 어떤 입력을 읽고 무엇을 수정하며
  어떤 경우 중단하는지, 자동 보고서·승인 기록을 만들지 않는 현재 한계를
  설명한다.
- 소스 검사 8종 PASS와 실제 `vendor-merge`, 전체 build, Contract test,
  담당자 승인, 배포 검증 미완료를 구분한다.
- 현재 후보는 commit별 재적용으로 만들었으므로 저장 결과의
  `integration_strategy: vendor-merge` 표시를 운영 방식 검증으로 인정하지
  않는다. 실제 vendor-merge 기록은 `NOT VERIFIED`다.

### 부록 · 과거 참고 코드 검사

- `easyseop/OpenMetadata` `849ae756...`와 공식 1.13.1의 과거 소스 검사임을
  첫 화면에 표시한다.
- BANK-OM-001~007 업무 변경과 008~011 TypeScript 정합성 후속 기록이 함께
  있는 당시 코드이며 현재 OM_TEMP 후보나 배포 대상이 아니라고 설명한다.
- 실제 코드 관계, 대표 diff, Manifest·commit 연결, 검사 결과 라벨을 참고
  예시로만 제공한다.
- T42·T43·행내 환경·배포 검사를 수행하지 않았으므로 최종 판단은 BLOCK이다.

## 4. 공통 사실과 상태 표시

- `easyseop/OpenMetadata` 과거 사례와 `easyseop/OM_TEMP` 현재 연습 결과를
  같은 후보의 결과처럼 섞지 않는다.
- PASS는 해당 검사가 확인한 조건만 통과했다는 뜻이며 배포 완료가 아니다.
- APPROVAL은 실패 확정이 아니라 담당자 검토가 필요한 상태다.
- PARTIAL, NOT RUN, ANALYSIS ERROR, BLOCK을 색뿐 아니라 글자로 표시한다.
- commit SHA와 digest가 어떤 저장소·branch·코드 상태를 가리키는지 바로
  설명한다.
- 실제 실행하지 않은 화면이나 값을 실행 결과처럼 만들지 않는다.
- 캡처에는 비밀값, 행내 URL, 인증 토큰, 고객·직원 데이터를 넣지 않는다.

## 5. 현재 완료와 남은 작업

완료:

- OM_TEMP 1.13.0 BANK-OM-001~007 Manifest·Registry·Contracts와 111개 변경 등록
- OM_TEMP 1.13.1 commit별 재적용 충돌 진단과 JSON 해결 보조 도구 실행
- 소스 검사 8종과 공식 변경 영향 결과 저장
- 5개 페이지 이동, 폰트·도식·코드 박스·표 미리보기

남음:

- 실제 `vendor-merge` 후보와 전략 값이 일치하는 결과 생성
- Registry 담당자 지정
- Contract test 7개, OpenMetadata 전체 build, 행내 API·화면·DB 테스트
- 검사한 commit과 실제 배포 파일·이미지·설정의 일치 확인
- 담당자 승인, 검증 tag와 최종 시연 캡처
- T43 실제 충돌 증거 자동 계산, Java JUnit·TypeScript Jest 연결,
  승인 기록·서명·배포 digest 결속

## 6. 생성·검토 절차

1. 정본 fragment 또는 renderer를 수정한다.
2. 3번·4번 renderer를 실행하고 `visualize`로 fragment preview를 다시 만든다.
3. `harness/tools/enable_guide_navigation.py`를 실행한다.
4. `.agents/skills/clarity-preflight-review/SKILL.md`로 중복, 미정의 용어,
   맥락 없이 나온 표현, 상태 과장과 처음 보는 독자의 흐름을 검토한다.
5. 브라우저에서 1→2→3→4→부록 이동, SVG 화살표·글자 겹침, 표 가로 넘침,
   코드·펼치기 가독성을 확인한다.
6. 테스트와 `git diff --check`를 통과한 뒤 인수인계를 갱신하고 같은 branch에
   commit·push한다.
