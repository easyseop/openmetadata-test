# 세션 상태 / 인수인계 (SESSION_STATE)

> **2026-08-08 Claude 최종 검토 반영:** 단순 target→candidate 경로 검사를
> 폐기하고 병합 전 승인 custom head, 이전 기준선 Candidate lock, 실제 merge-base,
> `git merge-tree` 원시 출력 digest와 충돌 경로를 canonical 결과에 결속했다.
> conflict-rate는 경로 수로만 계산하며 사람이 생략할 수 있다. 6단계 status와
> human 출력은 source-only 배포 오인을 차단하고, 구버전·잔존 lock 복구와
> vendor merge 이후 수작업을 명시한다. LLM G-룰은 참고자료이며 이번 구현
> 범위가 아니다. 전체 회귀는 560 passed, 38 skipped, 실패 0건이다.

> **2026-08-08 Phase 외부 검토 후속 보완:** artifact digest↔Candidate lock,
> 공식 tag↔premerge target, conflict evidence↔Candidate SHA, 등록자료↔결과
> digest를 결속했다. run-id 경로 이탈, 동시 결과 덮어쓰기, 관리자·실무자 파일
> 변조도 fail-closed로 차단한다. 여섯 공개 명령은 기본적으로 짧은 사람용 결과와
> 정확한 다음 행동을 출력하며 `--output-format json`으로 기계용 형식을 유지한다.
> 출력 문구는 Claude 검토 전 초안이다. 실제 조직 승인 권한과 운영 입력은
> 자동으로 추측하지 않는다.

> **2026-08-08 외부 모델 설계 검토 요청서:** Claude 초기 구현, Codex 독립
> 검토·안전 보완, OpenMetadata 1.13.1 기준과 1.13.2 목표, 후속 commit·
> 사람 판단 경계, 미실행 범위, 필수 설계 질문 20개를 하나의 Markdown으로
> 정리했다. 검토자는 코드를 수정하지 않고 SHA 비교와 반례를 근거로
> P0·P1·P2와 최종 승인 권고를 작성한다.

> **2026-08-08 고객용 버전 업그레이드 가이드 폐기:** 고객사·솔루션
> 제공업체 관점으로 작성한 독립 Markdown·HTML은 사용자 요청으로 삭제했다.
> 전용 renderer 옵션과 공유·검토 문서의 관련 현행 설명도 제거했다. 기존
> 11단계 예행연습 문서와 Phase 구현은 수정하지 않았다.

> **2026-08-08 Phase 안전 보완:** `codex/phase-bundling-safety-fix-20260808`
> branch에서 2026-08-07 Codex 검토의 P0 6건과 P1 2건을 수정했다. Phase 결과
> digest는 verdict뿐 아니라 reasons·evidence·detail도 보호하고, 승인에는 실제
> 승인자·RFC3339 시각·구체적 사유가 필요하다. timeout과 단계별 gate catalog가
> 실제 실행에서 강제되며 active source 0개와 debt 정책 누락은 fail-closed다.
> `om_workflow.py`의 6개 Phase 명령과 synthetic Git E2E를 추가했다. 실제
> 1.13.2 postmerge 후보 실행과 조직 승인·운영 배포 증거는 생성하지 않았다.
> 정확한 재개 순서는 `docs/04-진행/PHASE_BUNDLING_진척_인수인계_20260807.md`
> 13절을 따른다.

> **2026-08-04 최신 시연 초안:** 실제 OM_TEMP 1.13.1 branch를 비교해 113개
> 변경 경로(추가 43·수정 70)를 전용 74·공용 37·제외 2로 분류한 전체 YAML을
> 만들었다. 사용자는 공용 파일을 관련 BANK-OM ID 여러 개에 연결하는 방식을
> 시연용으로 선택했다. 같은 경로·ID 조합의 중복은 허용하지 않으며 37개 공용
> 경로에서 114개 고유 조합을 생성했다. `shared-code-definitions` 시연 초안의
> assertions는 모두 비어 있어 실제 검사 입력이 아니다. 2026-08-05 사용자는
> BANK-OM-001~007 유지와 공용 37개 경로의 관련 ID 다중 연결을 시연용으로
> 승인했다. 다음 작업은 실제 diff로 114개 정의를 채우고 별도로 승인받는 것이다. 상세
> 상태와 경로는 `docs/04-진행/CODEX_HANDOFF.md`의 `0-current`를 따른다.

> **2026-07-30 최신 작업:** 검사 전 등록자료 준비 자동화를 구현했다.
> 구현 commit은 `b63ce67bd303865224339a0dfe6e4becb252bea6`이다.
> `harness/prepare_registration.py`는 읽기 전용 `plan`, 미승인 template,
> digest 결속 `apply`를 제공한다. Git 사실만 자동 계산하고 owner·required
> path·Contract·승인자는 추측하지 않는다. dirty/unrelated/merge/ID 오류,
> 혼합 영역, required/source/shared owner 불일치, symlink·submodule·LFS,
> stale SHA·등록자료, 동시 apply를 fail-closed로 차단한다. Candidate lock
> v2는 `source-tree`와 `build-artifact`를 구분한다. 실제 OM_TEMP 1.13.0
> plan은 변경 0·판단 5·차단 0·분석 오류 0의 `REVIEW_REQUIRED`이며 digest는
> `sha256:502a6824bb60e02b0d6cf4a66043e9e5d9ec0b22ed70b2c3387437b738d278b7`다.
> 승인·apply는 실행하지 않았다. 등록 5종과 source 8종은 새 source-tree
> lock으로 PASS했고 전체 harness는 341 passed, 환경 의존 37 skipped다.
> 원격 run `30468709056`도 `7ee1fdb...`에서 381 passed, 운영 의존
> 7 skipped로 성공했다. source gate와 source patch-kill 2건이 통과했고
> 90일 artifact ID는 `8730765604`, SHA-256은
> `d229c78dfd2d9739b057d2d82cf7eb3cc4c98daa4d951fec00bb0c319eb96189`다.
> 쉬운 절차는
> `docs/00-사용가이드/OM_TEMP_검사전_준비도구_쉬운사용법.md`, 실제 제안은
> `harness/preparation-plans/om-temp-1.13.0-20260730/`이 정본이다.

> **2026-07-29 23:42 KST 최신 작업:** 사전준비 자동화 설계의 독립 검토를
> 반영해 먼저 0단계 기준선을 복구했다. 구현 commit은
> `2d017846b2cb4fb9883929f00b4f20bb8aa6c85a`다. T41은 Manifest v1/v2를
> 공용 `manifest.declared_scope()`로 읽고, Registry `provenance`는 필수이며,
> 등록자료 분석 실패는 traceback 대신 `analysis_error` JSON으로 남는다.
> OM_TEMP 1.13.0 결정론적 후보 `3a2811cf...`에서 등록 5종·소스 8종 PASS를
> 다시 확인했다. 전체 로컬 suite는 365개 중 318 passed, 환경 의존 47 skipped다.
> 원격 fixed-mirror run `30462316326`도 `23a8129...`에서 358 passed,
> 운영 의존 7 skipped로 성공했고 source gates와 source patch-kill 2건을
> 통과했다. 90일 artifact ID는 `8728243380`, SHA-256은
> `6e15ea0a3c4f33f7a22bee27602be0da86e70f7cb79de9c2f81b71f80b27745e`다.
> 원격에 1.13.1 후보 branch가 없어 T41은 재실행하지 못했으며 2차 공유 HTML의
> 초록 체크를 9개에서 8개로 정정했다. 다음 작업은 쓰기 없는 1단계 Git
> 분석기이며 `plan`·`apply` 자동화와 운영 배포는 아직 완료되지 않았다.
> 상세 변경·재현 명령·남은 차단 조건은
> `docs/04-진행/PREP_AUTOMATION_DESIGN_REVIEW_RESPONSE_20260729.md`,
> `harness/registrations/om-temp-1.13.0/REPRODUCIBILITY.md`,
> `docs/04-진행/CODEX_HANDOFF.md`의 최신 절을 따른다.

> **2026-07-29 현재 공유문서 작업 정본:** 작업 브랜치는
> `codex/strict-manifest-gates`다. 1차·2차 HTML, 3차 시연 요구사항, 검사기별
> 예외 검토와 다른 노트북 재개 절차는
> [`docs/04-진행/CODEX_HANDOFF.md`](docs/04-진행/CODEX_HANDOFF.md)와
> [`docs/04-진행/SHARING_ARTIFACT_REQUIREMENTS.md`](docs/04-진행/SHARING_ARTIFACT_REQUIREMENTS.md)를
> 먼저 따른다. 아래 내용에는 과거 작업 브랜치와 장기 구현 기록이 포함돼 있다.
> 이번 문서 개편 commit은 `dd45b578e189f9e6e3cc2beae5e5dc99184bd6d3`이며
> 원격 `Source candidate` run `30371799025`는 성공했다.
> 오늘 추가된 공유문서·OM_TEMP 시연·스킬과 다음 실행 순서는
> `docs/04-진행/CODEX_HANDOFF.md` §10이 정본이다.
> 현재 노트북 검증은 다섯 HTML의 1280px·390px 화면과 실제 이동 링크 통과,
> harness `308 passed, 37 mirror skips`, `git diff --check` 통과다.
> 원격 `0b0f7797...` 검증 run `30368181793`도 `348 passed, 7 operational
> skips`로 성공했고 source patch-kill 증거 artifact ID는 `8691825442`다.
> 2026-07-29 개편에서는 1차의 과거 저장소 역할 카드를 제거하고, 실제
> BANK-OM-007의 최초 8개·후속 2개로 `candidate_additional_paths`를 설명했다.
> 2차는 검사기 지도 → 검사기별 독립 상세보기 → 전체 입출력 상세보기 순서로
> 재구성하고 T번호가 전체 개발계획의 안정적인 태스크 ID임을 명시했다. 관련
> 집중 검사는 55 passed, 9 mirror skips이며 로컬 `file://` 브라우저 자동검수는
> 보안 제한으로 실행하지 못했다. 새 원격 증거 artifact ID는 `8693322667`,
> SHA-256은 `504a5850834bd2d94f3966e6b30e4850a0cb39c041597a4c215bec251e6d0743`다.
> 후속 2차 개편에서는 T60-I를 C로 이동해 지도와 상세 분류를 맞췄다. 최초
> 초록 체크 12개는 Claude 독립 검토에서 OM_TEMP와 kb-openmetadata 후보,
> 스모크 결과를 섞은 오류가 확인됐다. 수정 기준은 OM_TEMP commit
> `dee330e...`에 결속된 결과만 인정하며 A 7개·B 1개·C 1개, 합계 9개다.
> T25-R은 현재 후보 해당 없음, T61은 별도 후보 2건 확인, T63·T93 정책은
> 현재 후보 미실행이다. 남은 개발·외부 입력과 완료 기준은 2차 HTML 및
> `CODEX_HANDOFF.md` §12가 정본이다.
> 이 개편 commit `20b8592...`의 원격 run `30373496657`은
> `348 passed, 7 operational skips`로 성공했다. 90일 증거 artifact ID는
> `8693987394`, GitHub SHA-256은
> `3d089c30b3fcbc141674a964c8a803d1f51f2352cb9962af385e428a10dee29c`다.
> Claude 검토 반영 commit `10f8647...`의 원격 run `30376209792`도
> `348 passed, 7 operational skips`로 성공했다. 90일 증거 artifact ID는
> `8695135853`, GitHub SHA-256은
> `465b509049c81782de6100d499411e845b33bac4b0b9a4afccf431f0a7ffde3c`다.

> **목적**: 컨텍스트가 리셋돼도 이 문서 하나로 작업을 이어갈 수 있게 현재까지의
> 모든 결정·산출물·다음 단계를 세세하게 기록한다. **작업 재개 시 이 문서를 먼저 읽는다.**
> 최종 갱신: 2026-07-28 공유문서 1~5번, OM_TEMP 1.13.0 등록과
> 1.13.0→1.13.1 실제 충돌 연습, 저장소용 `clarity-preflight-review` 스킬,
> 실제 7-ID 재구축, Tibero 후속 보강,
> `BANK-OM-008` 후보 전용 UI 타입 정합성 보강,
> `BANK-OM-009` 공통 검색 결과 타입 보강,
> `BANK-OM-010` 알림 엔터티 ID 검색 안전성 보강,
> `BANK-OM-011` 검색 목록 변환 타입 계약,
> T25-R/T25/T26/T60-I/T30/T31 통과, 실제 GitHub 캡처 10장을 포함한
> 비개발자용 사용·시연 가이드와 커스터마이징 구성품·검사기별 쉬운 설명,
> T62 runtime 계약 실행기·Data Assertions/은행 컬럼/IME 실제 브라우저 계약·
> 90일 증거 보존, T63 공식 upstream UI typecheck 기준선 비교까지 반영.
> **현재 상태 정본은 [`STATUS.md`](STATUS.md), Claude 검토용 상세는
> [`docs/04-진행/CLAUDE_REVIEW_HANDOFF.md`](docs/04-진행/CLAUDE_REVIEW_HANDOFF.md)다.**
> **비개발자 안내 정본은
> [`docs/00-사용가이드/비개발자_사용_가이드.md`](docs/00-사용가이드/비개발자_사용_가이드.md)다.**
> **직접 시연 절차는
> [`docs/00-사용가이드/비개발자_시연_가이드.md`](docs/00-사용가이드/비개발자_시연_가이드.md)다.**
> 개발 태스크가 끝날 때마다 상태표·인수인계서를 갱신하고, 작업 주체 변경 또는 컨텍스트
> 소진 전에는 branch/commit, 정확한 테스트 결과, blocker, push 상태와 다음 실행
> 단계를 남긴다. 사용자에게 보이는 상태·용어·절차가 바뀌면 비개발자 가이드도
> 같은 작업 묶음에서 갱신한다. 전체 유지 계약은 [`CLAUDE.md`](CLAUDE.md)에
> 고정되어 있다.

---

## 0. 지금 어디인가 (한 줄)

vendor merge 기본 / patch replay 선택 전략의 게이트 엔진과 7개 원본 기능,
4개 후보 보강 등록부를 구현했다. `easyseop/OpenMetadata`에 공식
`1.13.1-release` 기반 7-ID vendor checkpoint `e1ffc5a1...`를 재구축한 뒤
Tibero 보강, 은행 탐색 UI 타입 정합성, 공통 검색 타입 매핑, 알림 엔터티 ID
fallback과 명시적 목록 변환 계약을 적용해 현재 candidate `849ae756...`를
만들었다. T25-R은 원본 checkpoint에서, T25/T26/T30/T31은 11개 active ID가
있는 현재 candidate에서 통과했다.
T60-I도 9/9 selector 구현
존재를 확인했다.
계약 테스트는 소스 기반 3개가 통과했고 실제 API 4개·브라우저 3개는 skip이다.
실제 upgrade 실행과 release artifact가 없으므로 첫 production release는 아직
차단 상태다.
비개발자는 커밋 `258bb8a`의 실제 GitHub 캡처 10장과 전체 흐름 설명으로
명령어 없이 현재 소스 증거를 확인할 수 있고, 테스트 환경 준비 후 같은 문서의
`Runtime contracts` 절차로 9개 실제 selector 실행과 증거 다운로드를 진행할 수
있다. 운영 흐름은 “커스터마이징 포함 현재 버전 → 공식 버전 vendor merge →
충돌 해결·필요 보강 → 후보 확정 → 소스 검사 → 테스트 환경 배포 → runtime
검사 → T90/T91/T94 → 결과”로 안내한다.
커밋 `705bb4f`는 한 customization에 필요한 ID·owner·허용/필수/감시 경로·
contract·test·series·commit trailer와 T24/T25/T26/T30/T31/T60-I/T61/T62/
T63/T90/T91/T94의 쉬운 역할·현재 결과를 같은 가이드에 추가했다.

## 1. 리포지토리·브랜치

- 작업 리포: `easyseop/openmetadata-test` (docs + 앞으로의 harness 코드)
- **현재 작업 브랜치: `codex/strict-manifest-gates`**
- 과거 `claude/markdown-file-feedback-26933w`는 구현 이력 보존용이며 새
  공유문서·OM_TEMP 작업을 그 브랜치에 커밋하지 않는다.
- 제품 리포: `easyseop/OpenMetadata`
- 제품 브랜치: `codex/bank-vendor-1.13.1-rebuild`
- 제품 재구축 checkpoint: `e1ffc5a1eb270c3225736544bb309a0c85af6d2c`
- 제품 candidate: `849ae756cd238f218b5e3a6c795a392305cb32ee`
- 2026-07-27 06:00 KST 정기 점검: 거버넌스 `434d92b`, 제품
  `b80d24d`의 로컬/원격이 각각 일치하고 작업 트리는 깨끗하다. 최종 동기화
  run `30219859614`는 성공했고 고정 mirror 로컬 suite는 316 pass·운영 7
  skip이다. 열린 PR·리뷰는 없으며 두 작업 브랜치는 아직 보호되지 않았다.
- 커밋 작성자·도구 출처는 실제 작업 주체에 맞게 기록한다. 과거 세션이나 다른
  도구의 출처를 새 커밋에 복사하지 않는다.
- 푸시: `git push -u origin codex/strict-manifest-gates`
- PR은 사용자가 명시 요청 시에만 생성(아직 요청 없음).

## 2. 최종 목표 (변하지 않는 것)

공식 OpenMetadata 버전업 시 행내 커스터마이징을 **누락 없이·추적 가능하게·검증
가능하게 보존**한다. 기본 전략은 공식 target SHA를 vendor branch에 merge하는
방식이다. cherry-pick/clean-room replay는 이식성 진단·복구·다중 버전 지원용
선택 모드다. 자동 구조 검증과 실제 기능 테스트를 구분하며 LLM은 배포 판정에서 제외한다.

## 3. 산출 문서 지도 (모두 커밋됨, 이 브랜치)

| 파일 | 역할 | 정본 우선순위 |
|---|---|---|
| `README.md` | 전체 개요·문서 지도·테스트 정책 | — |
| `docs/00-사용가이드/비개발자_사용_가이드.md` | 비개발자용 상태 해석·요청 정보·운영 시나리오 | 사용자 안내 정본 |
| `docs/00-사용가이드/비개발자_시연_가이드.md` | 명령어 없는 GitHub 확인·실제 runtime 시연·증거 체크표 | 비개발자 시연 절차 |
> **경로 이동/정리(2026-07-23)**: 문서는 `docs/` 하위 4분류 — 01-보고용
> (strategy_briefing)·02-설계(upstream_customization_design·governance_requirements)·
> 03-기술참조(verifier_catalog)·04-진행(build_plan·dev_roadmap). **검토이력(05)은
> 삭제됨.** 루트에는 README·EXECUTIVE_SUMMARY·SESSION_STATE만.

| `docs/01-보고용/openmetadata_strategy_briefing.md` | 왜 패치 스택인가 (경영진용, 정정 완료) | |
| `openmetadata_upstream_customization_design.md` | 상세 설계 (정정 완료) | |
| `openmetadata_governance_requirements.md` | **SRS — P0 9건 반영 + 부칙 A(2차 검토)** | **본문 충돌 시 부칙 A 우선** |
| `docs/04-진행/openmetadata_build_plan.md` | **순차 개발 실행 계획** — M0~M9, T01~T94 | 개발 스펙 정본 |
| `docs/04-진행/openmetadata_dev_roadmap.md` | **개발 로드맵 & MVP 커버리지 맵** — 진행 추적 | 커버리지 정본 |
| `docs/03-기술참조/openmetadata_verifier_catalog.md` | 검증기 23종(§0.1 구현현황) | |
| `docs/02-설계/ADR-001-vendor-merge-default.md` | **vendor merge 기본·replay 선택 결정** | **최우선 정본** |

> **검토이력 삭제(2026-07-23)**: 과거 검토 대화 5종(1·2차 요청·응답·외부검토)은
> **제거**(git 이력 보존). 수용된 정정 요약은 루트 `README.md` '설계 정정 이력' 참조.
> **정본 우선순위(충돌 시)**: ADR-001 > SRS 부칙 A > build_plan > SRS 본문.

## 4. 확정된 핵심 결정 (재론 불필요, 전부 합의됨)

- **vendor merge 기본**. 공식 upstream ancestry를 유지하고 승인된 target SHA를 merge한다.
- patch replay는 선택 진단·복구 모드다. 기존 T20~T23 구현은 유지하되 기본 합격 조건이 아니다.
- 불변 ID `BANK-OM-xxx`는 커밋 재생 단위보다 **기능·계약 식별자**가 우선이다.
- 공통 잠금은 upstream-lock·candidate-lock이며 patch-lock은 replay 모드에서만 필수다.
- **verdict 4상태**: `pass<approval<block<analysis_error`(severity rank로 집계, exit는 0/2/1/3
  으로 **마지막 1회 변환**). analysis_error=차단(승인 우회 불가). exit `max()` 집계 금지(P0-3).
- **등록·통합 생존 완전성 ≠ 기능 완전성**(문구 분리). ID 집합 일치는 등록 존재만 증명.
- **선언형 verifier**만(manifest 임의 shell 금지, P0-8). 실행형(python_import·allowlist
  script·container)은 **sandbox 필수**.
- 경로 필드 분리: `allowed_changed_paths`(상한)/`required_changed_paths`(하한)/`upgrade_watch`
  (paths·config_keys·dependencies·contracts). 구필드 `affected_paths`·`verification.command` 거부.
- range-diff는 **사람 리뷰용**(기계 판정은 patch-lock+trailer+`diff-tree --raw -z`). patch-id는 힌트 전용.
- **케이스 A~E**: A 무관 / B 우리파일 다른줄(자동) / C 같은줄(충돌) / D 의존대상 변경(upgrade_watch
  +verifier+LLM→테스트) / E 깊은 의존·의미붕괴(테스트만). D·E는 텍스트 충돌 없음.
- LLM Impact Memo: 읽기전용·pass 권한 없음·근거 첨부·"영향 없음" 금지("확인된 후보 없음").
- 테스트가 생존 증명: contract-id ↔ 테스트 결속 + patch-kill test(high/critical 우선).

## 5. GPT 2차 검토 반영 (SRS 부칙 A) — M1 동결 전 필수 3묶음

- **A-1 결과 계약 CI 경계**: exit/result 불일치·stale·누락 = `analysis_error`. 원자적 생성
  (임시파일→스키마검증→SHA/digest 자체검증→fsync+rename). `result_digest`=canonical JSON
  SHA-256(관측 메타데이터 제외). `approval-attestation`/`break-glass-attestation`/`acgh-result`
  분리(사람이 verdict를 pass로 못 바꿈). inputs는 repository-qualified(upstream/core/platform/policy).
- **A-2 lock·lineage·동시성**: source lock/application lock 분리. **모든 적용 커밋에
  `Source-Commit(s)`·`Patch-Revision`·`Application-Record-ID`(+해결 시 `Resolution-Record-ID`)
  자동 각인**(일반 cherry-pick은 안 만듦 → `git interpret-trailers`). object 보존
  (`cat-file -e` preflight, 누락=analysis_error, 동적 대체 금지). resolve **직렬화**
  (단일 integrator·base_lock_digest CAS). 재적용 상태 7종(applied/content_conflict/
  redundant_or_empty/missing_source_object/invalid_source_commit/skipped_due_to_dependency/
  internal_error).
- **A-3 스키마 의미 기반**: 신규 **T05 path-ownership + glob 문법 정본**. `required⊆allowed`
  semantic validator(required는 literal). contract catalog가 test 매핑 단일 정본
  (`assurance.contracts`/`assurance.direct_tests`, upgrade_watch 밖). verifier sandbox.
  JSONPath는 RFC 9535·eval 금지·자원 제한. verifier 타입에 `document_query_assert`·
  `file_hash_equals` 추가. CG 순효과 2단(intrinsic tree diff + counterfactual replay),
  touched/net 경로 분리, 비연속 series=block(MVP).

## 6. 개발 순서 (2026-07-25 개정)

```
T24 integration_strategy/candidate-lock ✅
  → T25 vendor ancestry ✅
  → T25-R source plan·44 shared hunk owner·실 candidate 검증 ✅
  → T26 customization survival ✅
  → T29 실제 kb_openmetadata manifest/contract ✅(test 명세)
  → T27 merge conflict evidence ✅
  → T28 전략 라우팅 ✅
  → 실제 vendor candidate의 논리 ID commit 생성 ✅
  → owner 배정·T60/61 contract 실행 ← 다음
  → T90 실제 스택 실행 → T91 실제 승격 → T94 실제 반입

T28에서 기존 T20·T21·T22·T23을 선택 replay 모드로 라우팅
```
- 신규 태스크 상세는 ADR-001 §6과 Build Plan을 따른다.
- 기존 replay-mode MVP1 완료 표시는 vendor-merge Candidate-control 완료를 뜻하지 않는다.
- 실제 첫 검사 기준은 공식 `1.13.1-release` 대비 `kangdkdk/kb_openmetadata` 변경이다.
- MVP2(Production-upgrade): +T60·T61·T72·T90·T91·T94·(T92).

## 7. OpenMetadata OSS 픽스처 (확보 완료 — 절대 잊지 말 것)

- 미러 위치: `/home/user/om-mirror` (blobless, 두 태그만; **repo 밖, 커밋 안 함**)
- **고정 태그·SHA (모든 테스트 기준)**:
  - UPSTREAM_A = `1.12.13-release` = `e6c665019a583b7938f30fbb7bafb7e1f82c5dd7`
  - UPSTREAM_B = `1.13.0-release` = `f329dd4a7e47134a2bd5a06af6181b0ee527ddd9`
- 재획득: `git init om-mirror && cd om-mirror && git remote add origin
  https://github.com/open-metadata/OpenMetadata.git && git fetch --depth 1
  --filter=blob:none origin refs/tags/1.12.13-release:refs/tags/UPSTREAM_A
  refs/tags/1.13.0-release:refs/tags/UPSTREAM_B`
- **실제 OM 경로(픽스처·T05용, 검증됨)**:
  - 모듈: `openmetadata-service/`, `openmetadata-spec/`, `openmetadata-ui/`,
    `openmetadata-ui-core-components/`, `ingestion/`, `openmetadata-clients/`,
    `openmetadata-sdk/`, `bootstrap/`, `conf/`, `common/`, `docker/`
  - 인증 코드: `openmetadata-service/src/main/java/org/openmetadata/service/security/`
    (예: `AuthenticationCodeFlowHandler.java`, `AuthCallbackServlet.java`)
  - 인증 스키마: `openmetadata-spec/src/main/resources/json/schema/auth/*.json`
- 테스트 정책: 합성 더미 금지. 실제 경로 위에 BANK-OM 합성 패치를 얹어 케이스 A~E 재현.
  M9 업그레이드 테스트는 실제 OM Docker·DB migration.

## 8. 환경

- cwd `/home/user/openmetadata-test`. git 2.43.0, python 3.11.15. 디스크 여유 ~30G.
- 아웃바운드 HTTPS 프록시 있음(HTTPS_PROXY 설정됨, git clone 정상 동작 확인).
- `add_repo`로 open-metadata 편입은 **불가**(교차 소유자 제약) → 직접 clone으로 대체(위 §7).

## 9. 하네스 초기 스캐폴딩 스펙 (역사적 참고 — 아래 T12/T13/T05는 모두 구현·완료됨)

> 이 절은 최초 스캐폴딩 지침의 기록이다. **현재 상태·다음 태스크는 §10을 본다.**

**하네스 프로젝트를 `harness/`에 스캐폴딩하고 T12·T13·T05 구현 중.** 계획한 파일:

```
harness/
  pyproject.toml            # pytest, pyyaml
  acgh/__init__.py
  acgh/verdict.py           # T13: 4상태·SEVERITY_RANK·EXIT_CODE·aggregate()·canonical_digest()·result 빌더
  acgh/gitprim.py           # T12: 커밋경계 trailer 파싱(-z)·changed_paths(diff-tree --raw -z)·object_exists(cat-file -e)
  tests/test_verdict.py     # block+approval→block(핵심 뮤테이션), 빈입력→analysis_error, exit매핑, digest안정성
  tests/test_gitprim.py     # 임시 git repo에 ID커밋+ID없는커밋 사이끼움 → 커밋단위로 정확 추출(CG-01 핵심)
  fixtures/upstream-lock.yaml  # §7 태그·SHA 기록
  fixtures/fetch_upstream.sh   # 재현 가능한 blobless fetch
  policies/repository-layout.yaml  # T05: 위 실제 OM roots + path_grammar(gitignore-pathspec, NFC, negation=false, symlink=reject)
```

### T13 verdict.py 스펙 (구현 지침)
- `SEVERITY_RANK={pass:0,approval:1,block:2,analysis_error:3}`, `EXIT_CODE={pass:0,block:1,approval:2,analysis_error:3}`.
- `aggregate(verdicts)`: rank의 max. **빈 입력→analysis_error**(fail-closed). exit code로 집계 금지.
- `to_exit_code(v)`. `canonical_digest(payload)`=`"sha256:"+sha256(json.dumps(sort_keys,separators=(",",":")))`.
- result 빌더: `{schema_version, canonical_payload:{verdict,gates,inputs,harness_version},
  observational_metadata:{generated_at,duration_ms,runner_id,run_id}, result_digest, expected_exit_code}`.
  digest는 canonical_payload만 대상.
- 핵심 수용: `aggregate(["block","approval"])=="block"`(뮤테이션: EXIT_CODE로 집계하면 이게 실패해야 함).

### T12 gitprim.py 스펙
- `commits(repo, base, head) -> list[Commit(sha, subject, customization_ids:list[str])]`.
  `git log --reverse -z --format=%H%x1f%s%x1f%(trailers:key=Customization-ID,valueonly,separator=%x1e) base..head`.
  -z로 커밋 NUL 구분. 필드 US(0x1f) 구분. IDs는 RS(0x1e) 구분, 빈 문자열→[].
- `changed_paths(repo, sha) -> list[str]`: `git diff-tree --no-commit-id --name-only -r -z <sha>`.
- `object_exists(repo, sha) -> bool`: `git cat-file -e <sha>^{commit}` exit 0.
- 환경 고정: 서브프로세스에 `-c core.quotepath=false` 등, locale 고정 검토.
- 핵심 수용: ID커밋 사이에 ID없는 커밋을 끼운 뒤 commits()가 그 커밋을 **빈 ids로 별도 레코드**로 반환(집합 축약 금지).

### T05 repository-layout.yaml 스펙
- `upstream_base_sha: e6c665019a583b7938f30fbb7bafb7e1f82c5dd7`
- `path_grammar`(name/version/root_relative/separator/case_sensitive/unicode_normalization=NFC/
  negation_allowed=false/symlink_policy=reject/submodule_policy=reject/lfs_policy=reject)
- `upstream_owned_roots`(§7 모듈들), `bank_governance_roots`(.bank/**, docs/bank/**, tests/bank/**),
  `platform_extension_roots`(bank-extensions/**), `unknown_path_policy: analysis_error`.

## 10. 재개 절차 (다음 세션)

### 현재 위치 (2026-07-27, 최신)

**완료:** 기존 patch-replay M1~M4, vendor-merge T24~T29·T25-R, 실제 7개
snapshot 등록과 4개 candidate-follow-up 등록부,
T62/T71/T72/T80/T81/T90/T91/T92/T94의 Docker-free 판정 계약.
현재 통합 테스트는 323개이며, 고정 upstream mirror와 product checkout을
연결한 CI-equivalent 환경에서 316개 통과(30.67초), API 4개와 실제 브라우저 3개만
skip됐다.
- **T60** contract 카탈로그+결속 `contracts.py` · **T61** patch-kill
  `patchkill.py` · **T51/52** 구조화 diff `structdiff.py`(실제 table.json
  dataContract 검출) · **T70** 정책 self-protection `policy_guard.py` · **T43**
  부채 게이트 `debt.py`.
- **Docker 데몬 없음(이 세션)** → T90의 12단계 결과계약은 구현했으나 실제
  구·신 OM 스택, DB 복원/migration, 검색/ingestion 차등과 rollback은 미실행.
- **제품 집중 검증**: Tibero `DatabaseServiceUtils.test.tsx` 13/13 pass.
  공식 Node 22.17.0·Yarn 1.22.22·6GB heap의 전체 UI typecheck에서 후보가
  만든 오류 3건을 확인하고 `ddf0dd2e...`에서 전부 수정했다. 전체 진단은
  399→396으로 줄었고 candidate-introduced 오류는 0개다. 남은 오류 중
  candidate 변경 파일에 보이는 16건은 공식 upstream과 같은 소스 줄이다.
  수정 2경로 Prettier도 pass다.
- **BANK-OM-009 검색 타입 보강**: `SearchIndex.METADATA_SERVICE`의 누락된
  generated source mapping과 InstanceCode/QueryReport 공통 union을 보강하고,
  Curated Assets 상태를 실제 `DATA_ASSET` 결과로 좁혔다. 제품 commit
  `70d028a0...`, Prettier pass, focused Jest 18/18 pass다. 기존 test의
  React `act(...)` warning은 남지만 테스트 실패는 아니다.
- **BANK-OM-010 알림 엔터티 ID 검색 안전성**: search-source union에
  `_source.id`가 없는 경우에도 hit `_id`를 fallback으로 사용한다. source ID가
  있으면 계속 우선 사용한다. 제품 commit `b80d24d8...`, Prettier pass,
  AlertsUtil Jest 112/112 pass다. 기존 FormContext warning은 테스트 실패가 아니다.
- **BANK-OM-011 검색 목록 변환 타입 계약**: `useDataFetching`의 안전하지 않은
  기본 변환을 제거하고 `SearchIndex`별 응답 타입을 transform 계약으로 전달한다.
  Domain/DataProduct 호출자가 구체 변환을 명시하며 hook 상태에는 변환 결과만
  들어간다. 제품 commit `849ae756...`, tree `22f92a8e...`, Prettier 6경로
  pass, focused data-fetching/listing Jest 7/7 pass다.
- **T63 UI typecheck 기준선 비교**: 공식 `1.13.1-release`도 같은 Node/Yarn,
  같은 ANTLR·schema 생성과 같은 dependency tree에서 전체 실행했다. 원본은
  396 diagnostics·141 files, 후보는 355 diagnostics·133 files다.
  신규 path/code 0·제거 41이며, clean-cache 메시지 변형도 신규 10·제거 51로
  fingerprint한다.
  `acgh/tsc_baseline.py`는 신규/증가를 block, malformed/exit 불일치를
  analysis_error로 만들고, 비어 있지 않은 후보 결과는 pass가 아니라
  approval로 유지한다.
- **T60-I/contract 구현**: catalog의 9 selector 모두 실제 파일·함수로 resolve.
  Sybase·Tibero 2개 required contract와 별도 IME source guard는 pass.
  OpenMetadata live URL이 필요한 InstanceCode·QueryReport·failed assertion·
  bank column API 4개, 실제 Data Assertions·bank column·SchemaEditor 화면이
  필요한 browser selector 3개는 skip.
- **T61 source patch-kill**: `patch-kill-plan.yaml`과
  `run_source_patch_kills.py`를 추가했다. Sybase 없는 `6e5b654f...`와 Tibero
  없는 `41b224ad...`에서 각 required test가 JUnit assertion failure를 내므로
  두 source experiment는 pass다. candidate `849ae756...`·governance
  `b1d3fa6...`·plan
  digest·selector·without-patch SHA가
  `source-patch-kill-evidence.yaml`에 결속됐다. API 기반 high ID 3개는
  제거본 runtime 미배포로 pending이므로 전체 T61 pass는 아니다.
- **T61 runtime patch-kill 검사기**:
  `runtime-patch-kill-plan.yaml`, 별도 runner/interpreter와
  `.github/workflows/runtime-patch-kill.yml`을 구현했다. source pending 세 ID를
  정확히 포괄하고, target 2회 실패와 전후 API/data/UI health pass를 함께
  요구하며 source/tree/artifact/deployment evidence/governance/suite/environment
  identity를 결속한다. 무환경 모의 세 건과 거짓 exit는 모두
  `analysis_error`로 차단됐다. 실제 제거본 build·배포·실행은 0건이다.
- **T62 runtime job**: `.github/workflows/runtime-contracts.yml`,
  `acgh/pytest_runs.py`, `run_runtime_contracts.py`,
  `interpret_runtime_result.py`를 구현했다. 각 selector를 shell 없이 별도
  pytest/JUnit으로 실행하고 candidate SHA·배포 digest·governance commit·suite
  digest에 결속하며, 원자적 결과와 실제 exit 불일치를 `analysis_error`로
  바꾼다. 로컬 무환경 시뮬레이션은 `2 pass·7 skip → block`; 실제 운영 run은
  아직 없다. 결과 3종은 pass 여부와 무관하게 실행별 overwrite 불가 GitHub
  artifact로 90일 보존하고 artifact ID·digest·URL을 job summary에 남긴다.
  90일 이후 조직 장기 보존 연결은 남았다.
- **source-candidate CI**: `.github/workflows/source-candidate.yml` 추가. action과
  product commit을 SHA로 고정하고 mirror·통합 테스트·T25/T26/T60-I/T30/T31을
  자동 실행하고 source patch-kill 결과를 90일 artifact로 보존한다. 현재 exact
  command의 clean local simulation은 316 pass·7 skip, source gate 5개,
  source patch-kill 2개 pass. 확인 run `30212561441`은 297 pass·5 skip,
  source gate 5개·patch-kill 2개·artifact upload pass로 success. 증거 artifact
  ID `8634882239`, digest `sha256:d5afd822...a7bfa32f`, 만료
  `2026-10-24T17:26:01Z`. 이 run에서 upload-artifact v4 Node 20 경고가 생겨
  `8ec6e28`에서 공식 v7.0.1 고정 SHA(Node 24)로 전환했다. 최종 확인 run
  `30212703620`은 annotation 0, 297 pass·5 skip, source gate 5개·patch-kill
  2개·Node 24 artifact upload pass. artifact ID `8634920602`, digest
  `sha256:bb8b9751...b12cf109`, 만료 `2026-10-24T17:30:09Z`.
  이전 확인 run `30162134698`은 293 pass·5 skip, source gate 5개 pass. 최초 remote run
  `30160752510`은 success. Node 20
  deprecation 때문에 checkout v5/setup-python v6 SHA로 올렸고 Node 24
  재검증 run `30160846880`도 annotation 없이 success.
  최신 확인 run `30213348947`은 297 pass·7 skip, T60-I 9/9, source gate
  5개·patch-kill 2개 pass이며 artifact ID `8635093639`, digest
  `sha256:2cd41e38...aaeee1b`, 만료 `2026-10-24T17:48:17Z`다.
  `BANK-OM-008` 후보 재결속 run `30214885448`은 306 pass·7 skip,
  T60-I 9/9, source gate 5개·patch-kill 2개 pass다. artifact ID
  `8635517530`, digest `sha256:bbb2bddf...ca40a27`, 만료
  `2026-10-24T18:31:08Z`다.
  T63 문서까지 포함한 run `30215596535`는 315 pass·7 skip,
  T60-I 9/9, source gate 5개·patch-kill 2개 pass다. artifact ID
  `8635710912`, digest `sha256:231137d0...4c110b`, 만료
  `2026-10-24T18:50:55Z`다.
  `BANK-OM-009` 후보까지 결속한 기록 run `30216708258`은 product
  `70d028a035...`, governance head `bc0e957`에서 316 pass·7 skip,
  T60-I 9/9, source gate 5개·patch-kill 2개 pass다. artifact ID
  `8636012730`, digest `sha256:813c26df...50860b4`, 만료
  `2026-10-24T19:22:20Z`다.
  직전 `BANK-OM-010` 후보 결속 run `30219786626`은 product `b80d24d831...`,
  governance head `90036ff`에서 316 pass·7 skip, active ID 10개, T60-I 9/9,
  source gate 5개·patch-kill 2개 pass다. artifact ID `8636860716`, digest
  `sha256:88a16a93...7eb5910`, 만료 `2026-10-24T20:49:23Z`다.
  현재 `BANK-OM-011` 후보 `849ae756...` 결속 run `30222439344`는 governance
  head `a715092`에서 316 pass·7 skip, active ID 11개, T60-I 9/9, source gate
  5개·patch-kill 2개 pass다. artifact ID `8637594508`, digest
  `sha256:c6221ec8...47c38d5`, 만료 `2026-10-24T22:05:46Z`다.
- **현재 차단 조건**: 11개 owner 미배정, live API selector 4개와 browser 3개의
  candidate-bound T62 결과 없음, 제품 전체 Java build와 full UI
  suite/typecheck green, 실제 T90/T91/T94 증거 없음.
  T63 메시지 변형 10건의 full-log 기술 검토에서는 새 의미 회귀가 식별되지
  않았지만, 지정 owner의 355건 기준선 승인 또는 수리가 아니므로 판정은
  `approval`로 유지한다.
  GitHub API 확인 시 governance·product 작업 브랜치는 모두
  `protected: false`이고 열린 PR이 없다. required check·지정 리뷰·2인 승인을
  저장소가 강제하지 않으므로 관리자가 보호 대상 통합 브랜치와 required
  `Source candidate` check를 정해 설정하기 전에는 릴리스 통제로 간주하지 않는다.

> **T93/T42 라벨 정정(중요)**: build_plan 정본에서 **T42 = upgrade_watch(업스트림
> 변경 ∩ 감시 → 케이스 D)** = `upgrade_watch.py`+`impact.py`, **T93 = 정책 노후화
> drift(패턴이 신버전에 ≥1 매칭? 신규 미분류 모듈?)** = `policy_drift.py`. 초기
> 커밋들이 이 둘을 뒤바꿔 라벨링했으나 커밋 `21bfc15`에서 정정(기능은 둘 다 구현
> 완료). 검증기 카탈로그 §0.1에 전체 23개 구현현황표 있음.

| 태스크 | 상태 | 모듈 |
|---|---|---|
| T25-R snapshot 재구성 검증 | ✅ source/owner/엔진·실 candidate 통과 | `acgh/vendor_rebuild.py` + `registrations/kb-openmetadata/source-candidate-evidence.yaml` |
| T25 vendor ancestry gate | ✅ | `acgh/ancestry.py` + `acgh/gitprim.py` |
| T24 integration strategy·candidate-lock | ✅ | `acgh/candidate.py` + `schema/candidate-lock.schema.json` + `binding.py` |
| T05 path-ownership 운영층 | ✅ | `acgh/layout.py` + `policies/repository-layout.yaml` |
| T12 git 프리미티브 | ✅ | `acgh/gitprim.py`(+parents/change_type/is_merge) |
| T13 verdict 엔진 | ✅ | `acgh/verdict.py` |
| T10 manifest 스키마·의미검증 | ✅ | `acgh/manifest.py` + `schema/manifest.schema.json` |
| T11 patch-lock | ✅ | `acgh/patchlock.py` + `schema/patch-source-lock.schema.json` |
| T15 result writer/CI adapter | ✅ | `acgh/result_io.py` + `schema/acgh-result.schema.json` |
| T14 evidence 카드 | ✅ | `acgh/evidence.py` + `schema/change-evidence.schema.json` |
| T30 커밋 단위 불변식 | ✅ | `acgh/invariants.py` (check_commit_invariants) |
| T31 ID 단위 불변식 | ✅ | `acgh/invariants.py` (check_id_invariants) |
| T20 재적용 CI 탐지 | ✅ | `acgh/reapply.py` |
| T21 재적용 담당자 해결 | ✅ | `acgh/resolve.py` |
| T22 clean-room replay | ✅ | `acgh/replay.py`(`replay_tree`·`replay_and_compare`) |
| T23 단일 integrator CAS | ✅ | `acgh/integrator.py` |
| T40 drift(touched/net) | ✅ | `acgh/drift.py` |
| T62 SHA 결속 | ✅ | `acgh/binding.py` |
| T32 최종상태 불변식 | ✅ | `acgh/finalstate.py` |
| T33 게이트 명칭·보장범위 | ✅ | `acgh/scope.py`(evidence 결합) |
| T41 민감영역·의도 게이트 | ✅ | `acgh/zones.py` + `policies/sensitive-zones.yaml` |
| T42 upgrade_watch(케이스 D) | ✅ | `acgh/upgrade_watch.py` + `acgh/impact.py` |
| T93 정책 노후화 drift | ✅ | `acgh/policy_drift.py` |
| T50 선언형 verifier | ✅ | `acgh/verifier.py` |
| T26 customization survival | ✅ | `acgh/survival.py` |
| T27 merge conflict evidence | ✅ | `acgh/conflicts.py` |
| T28 전략 라우팅 | ✅ | `acgh/routing.py` |
| T29 실제 7개 snapshot + 4개 후보 보강 등록 | ✅ 등록·⚠ 운영증거 | `acgh/registry.py` + `registrations/kb-openmetadata/` |
| T61 patch-kill | 🟡 source 2/5 증거·runtime 3/5 검사기 구현 | `acgh/patchkill.py` + source/runtime plan·workflow + `source-patch-kill-evidence.yaml` |
| T62 test-run 결속·실행 경계 | ✅ 실행기·90일 증거 보존·⚠ 운영미실행 | `acgh/testruns.py` + `acgh/pytest_runs.py` + `runtime-contracts.yml` |
| T63 UI typecheck 기준선 delta | ✅ 검사기·실제 원본/후보 증거·⚠ 승인 필요 | `acgh/tsc_baseline.py` + `compare_ui_typecheck.py` + `ui-typecheck-baseline-evidence.yaml` |
| T71/T72 fast lane·break-glass | ✅ | `acgh/fastlane.py` + `acgh/breakglass.py` |
| T80/T81 LLM Memo·지표 | ✅ | `acgh/impact_memo.py` |
| T90 업그레이드 결과계약 | 🟡 실제 실행 필요 | `acgh/upgrade_run.py` |
| T91 동일 digest 승격 | ✅ 엔진·⚠ 실제 승격 | `acgh/release.py` |
| T92 retirement | ✅ | `acgh/retirement.py` |
| T94 내부망 재검증 | 🟡 실제 서명/반입 필요 | `acgh/airgap.py` |

**커밋 SHA**: 스캐폴드 `7ccc00e` → `3cc0539`(T10/11/05) → `f38b124`(T15/14) →
`e5729dd`(T30/31) → `ee5a28e`(T20) → `da96332`(T21) → `47199cb`(T22) →
`febb929`(T23) → `cd1c9b5`(T40) → `03b05ff`(T62) → `90d09fe`(T32) →
`c5a0db5`(T33) → `cb52e76`(T41) (+ 사이사이 docs).

**환경 재현**: `pip install jsonschema pathspec`(pyproject deps 반영됨). 경로
문법 pathspec factory=`gitignore` 고정. 테스트: `cd harness && python -m pytest`
→ 80 통과. 실제 OM 콘텐츠는 `tests/conftest.py`가 미러에서 blob 온디맨드로
가져옴(미러 없으면 skip). `tests/test_reapply.py`는 실제 AuthLoginServlet.java를
공통 조상으로 케이스 B(clean)/C(conflict)/redundant 구성.

### 다음 태스크 — 첫 실제 production-upgrade 증거

1. 11개 active ID의 owner/승인 라우팅을 배정한다.
2. InstanceCode·QueryReport·Data Assertions 제거본을 실제 배포해 남은 T61
   3건을 실행하고, API·DB·검색·권한·UI/IME 전체 T62 candidate-bound result를
   만든다.
3. T63은 공식 원본 396건 대비 후보 355건, 신규 path/code 0·제거 41과
   메시지 변형 10건을 확인했지만 `approval`이다. 전체 로그를 검토해 기준선을
   조직적으로 승인하거나 오류를
   수정하고, 전체 Java/UI 테스트를 후보와 결속한다.
4. Docker/운영 유사 데이터로 T90 12단계를 실행한다.
5. T91 실제 artifact 승격과 T94 실제 오프라인 서명·내부망 재검증을 수행한다.

> 아래 M4 재개 지침은 기존 replay-mode 개발 이력으로 보존한다.

### 기존 다음 태스크 기록 (M4 — 역사적 참고)

build_plan §M4 + 부칙 A-3.5/3.6 참조. 순서: **T93 → T42 → T50**. 전부 실제 OM
미러로 테스트. 재사용: `layout`(경로 문법)·`gitprim.net_changed_paths`(업스트림
변경)·`verdict`.

**T93 upgrade_watch 감시** (케이스 D, 선행 T10·T62): manifest의 `upgrade_watch`
(paths·configuration_keys·dependencies·contracts)가 가리키는 **업스트림 파일이
A→B 업그레이드에서 변경됐는지** 플래그. `gitprim.net_changed_paths(mirror,
UPSTREAM_A, UPSTREAM_B)` ∩ watch globs → 변경 시 approval(리뷰 유발). 텍스트
충돌은 없지만 우리가 의존하는 심볼/설정이 바뀐 케이스 D를 잡는 핵심. glob 문법은
T05 `layout.make_spec` 재사용.

**T42 영향 분석** (케이스 D 보강, 선행 T93): watch에 걸린 변경의 영향 표면을
정리 — 어떤 ID가 어떤 watch 항목 때문에 리뷰 대상인지 매핑. LLM Impact-Memo는
보조(§7, verdict 권한 없음) — evidence 카드 `llm_suggestions`로만.

**T50 선언형 verifier** (P0-8, 선행 T04·T14): manifest `assurance.direct_tests`/
contract 파생 테스트를 **선언형**으로 실행 — `document_query_assert`(JSON
Pointer)·`file_hash_equals`·`python_module_present`(정적) 타입. 임의 shell 금지
(이미 manifest 스키마가 `verification.command` 구조적 차단). 실행형(import 등)은
sandbox 필수(부칙 A-3.5). **M4 끝 = MVP1(Candidate-control) 완성.**

> (M3 상세 스펙은 아래에 역사적 참고로 남김 — 전부 구현·완료됨.)

### (완료·참고) M3 상세 스펙

**T40 drift 검사** (P0-6, 선행 T10·T12): candidate가 **구현 범위 밖**의 upstream
파일을 바꿨는지 탐지. 각 커밋/전체 net 변경 경로를 manifest의
`allowed_changed_paths`(상한, pathspec)와 대조 — allowed 밖 upstream 변경=block,
`required_changed_paths` net 누락=block(CG-03 확정, A-3.7). touched paths(상한)와
net changed paths(하한) 분리(A-3.7). `layout.classify` + manifest 로더 재사용.

**T62 SHA 결속** (§10.1): 게이트 입력의 upstream/patch-source를 동적 조회 없이
고정 SHA로 결속(이미 patchlock·layout이 SHA 고정). candidate 평가 시점의
repository-qualified SHA 세트를 result inputs로 봉인(result_io와 연결).

**T32 최종상태 불변식** (P0-5, 선행 T22·T31): active 패치 **순효과 0**(적용 후
무변화)=실패/retirement, active ID revert=상태전환·ADR 필수, candidate HEAD ==
replay tree(T22 `replay.replay_and_compare` 재사용), candidate 변경 시 기존
테스트·승인 무효화(result_io.attestation_is_valid 연계).

**T33 게이트 명칭·보장범위** (P0-5·P0-7): 산출물에서 "완전성=기능 보장" 표현
제거, 보장/미보장 표를 게이트 출력에 포함(문서+GateResult reasons).

**T41**: build_plan 참조(범위 보강). M3 완료 후 M4 T93·T42·T50 → **MVP1 완성**.

### 재개 절차
1. 이 파일 + `docs/04-진행/openmetadata_build_plan.md` + SRS 부칙 A(`docs/02-설계/openmetadata_governance_requirements.md`) 읽기.
2. `/home/user/om-mirror` 존재 확인(없으면 §7 재획득), `pip install jsonschema pathspec`.
3. `OPENMETADATA_PRODUCT_REPO=/path/to/OpenMetadata python -m pytest
   harness/tests tests/bank/contracts` → mirror 연결 기준 현재
   323개(316 pass·7 operational skip) 재확인.
4. `STATUS.md`의 production blocker와
   `docs/04-진행/CLAUDE_REVIEW_HANDOFF.md`의 실제 실행 순서를 따른다.
5. 각 태스크 완료 시 `openmetadata_dev_roadmap.md` §4.1 로그 + 이 표 갱신.
6. 실제 작업 주체에 맞는 커밋 메타데이터를 사용하고, 이 브랜치
   (`claude/markdown-file-feedback-26933w`)로 push.
7. 게이트/재적용 테스트는 **반드시 실제 OM 미러**로(합성 더미 금지, §7).

### 문서 정리 백로그 (외부 검토 반영 — `harness/` 코드 무관)

외부 검토(`.../openmetadata_repository_documentation_feedback.md`) 반영. 사용자
지시: **네 트랙 전부 수행**. 순서 ①→④. **코드/테스트 변경 없음.**

- ✅ **완료분**: build_plan 순환의존(T93↔T42·T62↔T32) 해소·T50 통일(`e04ed64`),
  verifier_catalog "3→4계층", `harness/README.md` 신설, 카탈로그 §0.1 구현현황표,
  T93/T42 라벨 정정(`21bfc15`), `EXECUTIVE_SUMMARY.md` 신설(`84734f8`).
- ① **정본 단일화**: SRS(`openmetadata_governance_requirements.md`) 부칙 A를
  **본문에 병합**해 "부칙 우선" 구조 제거. REQ별 상태(planned/implemented/verified)
  부여. 문서 상단 Draft→버전/승인 상태 갱신. SRS 내부 자체 개발계획은 build_plan
  참조로 대체. 1.1이 1.0보다 앞·용어절 중복 정리.
- ② **구형 설계 정리**: `openmetadata_upstream_customization_design.md`(2894줄)의
  `affected_paths`→allowed/required_changed_paths, `range-diff` 기계판정→
  patch-lock+trailer+구조화JSON(사람리뷰용만 range-diff), 충돌 `abort`→2모드
  (탐지/해결), `verification.command`→선언형 verifier, "최신 브랜치"→고정 SHA.
  deprecated 표기 없이 남기지 말 것.
- ③ **경영진/개발자 분리**: README를 목적·현재상태·보장/미보장·읽는순서·빠른시작
  중심으로 축약(검증기 전체표는 카탈로그로 이동). 과장표현 정직화(검토 §9 금지표현).
  테스트정책 문구: "미러 의존 통합/업그레이드=실제 OM, 순수 판정 단위=합성 픽스처 가능".
- ④ **구조/위생**: 문서 `docs/`(architecture·spec·ci·runbooks·reference·ai·
  reviews/archive) 분할, 검토문서 archive로 이동(+메타데이터), 용어집 신설.
  **`SESSION_STATE.md`→`.claude/`로 이동 + 세션URL·로컬절대경로·브랜치지침 제거**
  (공개 노출 이슈). 상태/테스트수는 단일 소스(STATUS.md/CI)로.
- **정정된 사실(문서 갱신 시 반영)**: 정본 T42=upgrade_watch(케이스D),
  T93=정책노후화. clean-room replay는 **소스 트리 재현성**만(빌드 바이트재현 아님, T91).
