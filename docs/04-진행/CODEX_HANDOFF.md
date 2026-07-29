# Codex 작업 인수인계

## 0-latest. 2026-07-30 검사 전 준비 자동화 구현

독립 검토를 받은 등록자료 준비 설계의 0~6단계를 구현했다.

### 구현 파일과 방식

- `harness/prepare_registration.py`: `plan`, `approval-template`, `apply` CLI
- `harness/acgh/registration_prep.py`: Git 분석, 정책 비교, 상태 판정,
  제안 digest, stale 확인, 잠금, 원자 적용과 rollback
- `harness/acgh/gitprim.py`: ref 고정, dirty 상태, NUL-safe tree entry,
  binary-safe blob 읽기
- `harness/acgh/schema/commit-inventory.schema.json`
- `harness/acgh/schema/registration-proposal.schema.json`
- `harness/acgh/schema/registration-approval.schema.json`
- `harness/tests/test_registration_prep.py`: 정상·후속·ID·소유영역·무관 이력,
  source/shared owner, symlink·submodule·LFS, digest·stale·lock 회귀 test
- `generate_manifest_drafts.py`: BANK-OM SHA 하드코딩 제거, 새 planner 호환
  진입점
- Candidate lock schema v2: `source-tree`와 `build-artifact` 구분. v1은 과거
  digest를 깨지 않도록 read-compatible

자동화는 Git이 알 수 있는 SHA·commit·경로만 계산한다. 신규 ID의 owner,
criticality, required path, Contract, 기존 bank-only watch 보존 여부는
질문으로 남긴다. `READY`도 자동 적용하지 않는다.

### 실제 OM_TEMP 1.13.0 결과

- 제안:
  `harness/preparation-plans/om-temp-1.13.0-20260730/`
- patch: `2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50`
- custom: `7d19c8952612e77467b0a80d6287170d814f1de1`
- 상태: `REVIEW_REQUIRED`
- 자동 변경 0, 기능별 사람 판단 5, 차단 0, 분석 오류 0
- digest:
  `sha256:502a6824bb60e02b0d6cf4a66043e9e5d9ec0b22ed70b2c3387437b738d278b7`
- 두 번째 plan 산출물: byte-identical
- 승인·apply: 미실행

기능별 질문은 공식 patch에 없는 기존 watch 경로를 보존할지 묻는다. 43개
경로를 각각 승인하게 하지 않고 BANK-OM별 5개 묶음으로 보여주되 상세 경로는
그대로 보존한다.

등록자료 검증 5종과 source gate 8종을 결정론적 후보 `3a2811cf...`에서 다시
통과했다. Candidate lock은 schema v2, `artifact_kind: source-tree`, digest
`sha256:2c966250f31897d9aa6a6cee2d80a324c5997f258d02f0a2a6295b45d4f2fc14`다.
이는 build/image 검증이 아니다.

전체 로컬 harness는 378개 중 `341 passed, 37 environment-dependent
skipped`다. 신규 준비·Git·Candidate 집중 test는 `38 passed`다. `py_compile`,
위키 JavaScript 구문 검사, 제안 결정론 diff, ZIP 무결성, `git diff --check`도
통과했다.

### 다음 작업자가 해야 할 정확한 일

1. 담당자에게 `review-required.yaml`의 5개 질문을 전달한다.
2. 실제 승인자 ID·시각·구체 사유로 template을 채운다.
3. 같은 제안 digest인지 검토한 뒤 `apply`를 실행한다.
4. 등록자료 검증과 source gate를 다시 실행한다.
5. 원격 1.13.1 patch/custom branch가 제공되면 1.13.1에서 plan부터 반복한다.

owner·승인자·1.13.1 SHA·비밀값·실제 산출물은 추측하지 않는다. 전체 build,
행내 runtime, 산출물 승격, 운영 배포는 여전히 외부 입력 대기다.

> 갱신 기준: 2026-07-29 23:42 KST
> 거버넌스 저장소: `easyseop/openmetadata-test`
> 작업 브랜치: `codex/strict-manifest-gates`
> 이번 문서 개편 commit: 이 문서를 포함한 현재 branch의 최신 commit
> (`git log -1 --oneline`으로 확인)
> 직전 확인된 원격 검증: `23a8129...`의 `Source candidate` run
> [`30462316326`](https://github.com/easyseop/openmetadata-test/actions/runs/30462316326)
> 성공 (`358 passed, 7 operational skips`, source gates와 source
> patch-kill 2건 통과)
> 문서 묶음 작성 전 기준 commit: `0a6d009107a18e69a2150388442adffb6332f08c`
> 제품 코드 상태: `easyseop/OpenMetadata` commit
> `849ae756cd238f218b5e3a6c795a392305cb32ee`
> 공유문서·스킬 최초 로컬 commit: `becb18e` (이후 보강은 현재 브랜치의 `git log`로 확인)
> 원격 push: `easyseop/openmetadata-test`의 `codex/strict-manifest-gates`
> branch는 이번 공유문서·스킬·검사자료 배치까지 push 완료. 사용자가 만든
> `easyseop/OM_TEMP`에는 1.13.0 시연용 제품 코드 두 branch를 push함

다른 작업 노트북의 Git commit 작성 시각과 문서에는 `2026-07-29`가 기록됐지만,
GitHub push와 Actions 수신 시각은 2026-07-28이다. 이 문서의 “오늘” 집계는
GitHub 서버 시각을 기준으로 한다.

이 문서는 다른 노트북이나 새 작업에서 바로 이어가기 위한 현재 정본이다.
과거 Claude 작업의 상세 기록은
[`CLAUDE_REVIEW_HANDOFF.md`](CLAUDE_REVIEW_HANDOFF.md)에 남아 있지만, 공유문서
1차·2차·3차·4차 작업은 이 문서와
[`SHARING_ARTIFACT_REQUIREMENTS.md`](SHARING_ARTIFACT_REQUIREMENTS.md)를 먼저
따른다.

## 0-current. 사전준비 자동화 설계 검토 반영과 기준선 복구

### 이번에 무엇을 검토받았나

사용자가 전달한 `PREP_AUTOMATION_DESIGN_REVIEW_20260729.md`는 검사 실행 전에
Manifest·Registry·Contract 등 등록자료를 자동으로 준비하는
`plan → 검토 → apply` 설계에 대한 독립 검토다. 실제 제품 업그레이드나 운영
배포 승인 검토가 아니다.

검토는 쓰기 자동화 전에 기존 T41 Manifest v2 범위 오류, Registry 출처 필드,
분석 실패 표현, 승인 후 입력 변경 차단과 Git edge case를 먼저 보완하라고
권고했다. 응답 정본은
[`PREP_AUTOMATION_DESIGN_REVIEW_RESPONSE_20260729.md`](PREP_AUTOMATION_DESIGN_REVIEW_RESPONSE_20260729.md)다.

### 구현 완료

- 구현 commit: `2d017846b2cb4fb9883929f00b4f20bb8aa6c85a`
- T41 소스·업그레이드 실행기는 `manifest.declared_scope()`로 Manifest v1/v2
  범위를 읽는다.
- Registry entry는 `source-snapshot` 또는 `candidate-follow-up` provenance를
  반드시 명시한다.
- 등록자료 재구성 실패는 `analysis_error` JSON과 exit code 3으로 끝난다.
- OM_TEMP 1.13.0을 공식 `f329dd4a...`에서 결정론적으로 다시 구성했다.
  후보 `3a2811cf...`, tree `9495a31c...`, 등록 5종·소스 8종 PASS다.
- 1.13.1은 원격 후보 branch가 없어 T41을 재실행하지 않았다. 2차 공유 HTML은
  이 항목을 `현재 후보 재검증 필요`로 표시하고 후보 결속 초록 체크를 8개로
  정정했다.
- 비개발자 가이드, 설계서, 운영 위키 데이터와 독립 검토용 HTML을 같은
  증거 경계로 갱신했다.

### 검증

- 전체: 365개 중 `318 passed, 47 environment-dependent skipped`
- 원격 fixed mirror: `358 passed, 7 operational skips`
- phase 2 후보 결속 초록 체크: 8개
- 사용자 HTML 4개: 여닫기 불일치·미종료 태그 0
- 1.13.0 결과 JSON 2개: 문법 확인
- `git diff --check`: 통과

47개 skip은 `/home/user/om-mirror`, 행내 OpenMetadata API, 브라우저 URL과
제품 repository 같은 외부 실행 입력이 없기 때문이다. PASS로 세지 않는다.

원격 run은
[`30462316326`](https://github.com/easyseop/openmetadata-test/actions/runs/30462316326)이며
90일 보존 artifact `source-patch-kill-evidence-30462316326-1`의 ID는
`8728243380`, SHA-256은
`6e15ea0a3c4f33f7a22bee27602be0da86e70f7cb79de9c2f81b71f80b27745e`다.

### 당시 다음 작업 기록 — 2026-07-30 구현 완료

1. `prepare_registration.py plan`의 1단계 읽기 전용 Git 분석기를 구현한다.
2. patch/custom ref를 SHA로 고정하고 BANK-OM별 commit·경로를 계산한다.
3. 실제 등록 폴더를 쓰지 않고 제안 폴더에 `commit-inventory.yaml`과
   `current-diff-paths.txt`만 만든다.
4. 무관 이력, merge, ID 누락·중복, rename·한글 경로 등 차단 test를 먼저
   추가한다.
5. 위 판정이 안정된 뒤 proposal/review-required, 마지막에 digest 승인과
   원자적 apply를 구현한다.

위 1~5와 source/build artifact 종류 구분, upstream에 없는 행내 경로의
watch 분리, symlink·submodule·LFS mode 차단은 2026-07-30 완료됐다.
여전히 남은 것은 OM_TEMP 1.13.1 재검증, 실제 runtime/build/deploy와 조직
owner·승인자 지정이다. 원격
`patch/om-1.13.1`·`custom/om-1.13.1`, 비밀값, owner를 추측하지 않는다.

## 0-0. 2026-07-29 Claude 위키 검토 반영

Claude 검토 파일 `WIKI_REVIEW_20260729.md`의 F1~F17을 현재 작업본과 다시
대조했다. 검토가 사용한 `dfc43f1` 이후 Manifest v2 전환이 이미 진행됐으므로
F1·F2를 이유로 코드를 v1으로 되돌리지 않았다. 현재 기준은 다음과 같다.

- 스키마는 v1 호환 읽기와 v2 `implementation.changed_paths`를 구분한다.
- OM_TEMP 1.13.0·1.13.1 Manifest는 v2 형식이다.
- `candidate_additional_paths`는 OM_TEMP 문서·v2 등록에서는 사용하지 않고
  과거 v1 등록 묶음을 읽기 위한 호환 코드에만 남아 있다.
- T90 등 실행 증거가 없는 검사는 초록 PASS가 아니라 APPROVAL로 표시한다.
- T42를 patch 갱신과 custom 병합 사이에 배치했다.
- OM_TEMP 문서가 과거 `kb-openmetadata` 등록 실행기를 직접 가리키지 않도록
  공용 실행기 진입점 4개를 `harness/`에 추가했다.
- 독립 검토 HTML은 이미지 20개와 충돌 근거 파일 10개를 내부 `data:` URI로
  포함한다. 빌드 시 로컬 상대경로가 남으면 실패한다.

검증 결과:

- 전체 Python test: `314 passed, 47 skipped`
- 공용 실행기 4개 `--help`: 정상 종료
- 1280px 브라우저: 가로 넘침 없음
- T90 상태: 호박색 APPROVAL
- 브랜치 Cycle: 병합 전 T42 표시, SVG 내부 글자 겹침 없음
- 독립 HTML 충돌 근거 링크 5개: 모두 내장 `data:` URI
- 브라우저 console error: 없음

최신 전달 파일:

- `docs/00-사용가이드/OM_TEMP_operations_wiki_Claude_review_20260729.html`
- `docs/00-사용가이드/OM_TEMP_Claude_검토패키지_20260729.zip`
- `docs/00-사용가이드/CLAUDE_REVIEW_PROMPT_20260729.md`
- `docs/00-사용가이드/WIKI_REVIEW_RESPONSE_20260729.md`

## 0-A. 검사 운영 통합 위키

2026-07-30 05:34 KST에 기존 보고용 1~5번과 실무 상세 기준을 한 화면의 계층형
목차에서 확인하는 통합 위키 1차 본문을 만들었다.

- 화면:
  `docs/00-사용가이드/OM_TEMP_검사운영위키_구성초안.html`
- 상세 원고 데이터:
  `docs/00-사용가이드/OM_TEMP_검사운영위키_데이터.js`
- 보고용 1~5번은 기존 정본의 내용을 위키 공통 템플릿으로 요약해 보여준다.
  기존 standalone HTML 전체를 iframe으로 삽입하지 않는다.
- 실무 상세에는 저장소·branch·ID·자동화·업그레이드·충돌·결과·배포 승인
  개념 11개, 검사 상세 항목 17개, 관리 파일 12개를 등록했다. T93은 범위와
  정책 질문을 별도 상세 항목으로 나눴다.
- 검사기 페이지는 질문, 실행 시점, 입력, 판단 순서, 판정, 한계, 실행 명령과
  구현·test 파일을 보여준다.
- 관리 파일 페이지는 목적, 최초 생성·갱신 시점, 작성·승인 주체, 변수별 역할,
  변경 전후 예시, 재실행 명령과 덮어쓰기·보관 원칙을 보여준다.
- BANK-OM-007 후속 경로, Registry 담당자 배정, Contract test 추가,
  Repository layout과 Sensitive zones 갱신, Candidate lock·Test run set·검사
  결과의 불변 보관 예시를 포함했다.

위키에서 설명한 주요 검사기와 스키마에 대응하는 단위 테스트 묶음은 로컬에서
통과했다. 브라우저 file URL 미리보기는 사용자가 직접 열어 확인 중이며, 정식
파일명 확정·원격 push와 모든 화면 폭의 시각 검토는 다음 작업에서 마무리한다.

## 0. 최신 공유문서 상태

2026-07-30 KST에 처음 보는 부서 독자가 “이 개념은 누가 만든 것인지, 어느
코드 상태에만 해당하는지, 다음 페이지에서 무엇을 확인해야 하는지”를 계속
질문하는 방식으로 전체 구조를 다시 검토했다. 검토 결과와 페이지별 예상 질문은
[`5개_가이드_논리구조_검토결과.md`](../00-사용가이드/5개_가이드_논리구조_검토결과.md)에
정리했다.

현재 **읽는 순서**는 다음과 같다.

1. 목적과 목표 브랜치 전략: 직전 `custom` 이력에 새 공식 `patch`를 병합하는
   `vendor-merge` 운영 Cycle
2. 검사기 원리: 각 검사가 읽는 입력, 판단 방법, 출력과 한계
3. 검사 전 사전환경 설정: Manifest·Registry·Contract와 실제 Git diff 등록
4. OM_TEMP 코드 업그레이드 연습: 1.13.0 commit을 1.13.1에 하나씩 적용해
   BANK-OM별 충돌을 분리한 진단 결과
5. 실제 적용과 결과 확인: 코드 변경, Manifest, 검사 결과와 배포 승인 조건 연결

과거 `easyseop/OpenMetadata`의 `849ae756...` 사례는 현재 OM_TEMP 흐름과
저장소·ID 범위가 다르므로 보고용 1~5의 결론으로 사용하지 않는다. 보고용
요약은 한 위키 안에서 읽지만 목적·검사 원리·설정·업그레이드·결과 판단의
범위는 장별로 구분한다. 반대로 Manifest 필드 설명은 보고용 3차를 과도하게
늘리므로 상세 페이지인
[`OM_TEMP_관리파일_필드_사전_미리보기.html`](../00-사용가이드/OM_TEMP_관리파일_필드_사전_미리보기.html)로
분리 연결했다.

각 첫 화면에는 다음 경계를 명시했다.

- BANK-OM ID, `patch/custom` 이름과 반복 절차는 OpenMetadata 기본 기능이
  아니라 이 프로젝트의 내부 운영 방식이다.
- T25·T42 같은 번호와 PASS·APPROVAL·BLOCK은
  `easyseop/openmetadata-test`의 내부 검사 체계다.
- Manifest·Registry·Contract·Candidate lock은 OpenMetadata 실행 설정이
  아니라 검사 기준자료다.
- 4번의 commit별 재적용과 JSON 충돌 보조 도구는 BANK-OM별 충돌을 분리한
  이번 연습용 방법이며 확정 운영 절차가 아니다.
- 과거 참고자료의 `849ae756...`와 BANK-OM-008~011 판정은 당시 저장소에만
  해당하며 현재 OM_TEMP 보고용 결과로 사용하지 않는다.

가장 중요한 사실 보정은 **목표 운영 전략과 현재 증거의 분리**다. ADR의 기본
운영 전략은 `vendor-merge`지만, 현재 OM_TEMP 1.13.1 후보는 BANK-OM commit을
하나씩 재적용해 만들었다. 저장된 소스 결과의
`integration_strategy: vendor-merge` 표시는 실제 후보 생성 이력과 맞지 않는다.
따라서 문서에는 소스 범위 검사 8종은 PASS, 실제 vendor-merge 수행과 충돌 해결
증거는 `NOT VERIFIED`로 표시했다. 결과 파일을 사실과 다르게 고쳐 쓰지는
않았으며, 다음 검증에서는 직전 custom 이력과 공식 1.13.1을 실제로 병합한
후보를 새로 만들고 전략 값까지 검사해야 한다.

통합 위키와 별도로 보관하는 standalone 다섯 페이지는 위·아래 이전·다음
이동을 유지한다. fragment를 다시 렌더링한 뒤 아래 명령으로 이동 버튼을
재생성한다.

```bash
./.venv/bin/python harness/tools/enable_guide_navigation.py
```

2026-07-30 KST에 로컬 HTTP 미리보기에서 `1 → 2 → 3 → 4 → 부록` 이동을 실제
클릭해 확인했다. 1번 SVG는 공식 `patch`와 직전 `custom`의 병합 지점, Git 충돌
해결, 검사 BLOCK 보완, 배포 후보 tag와 다음 Cycle 복귀가 겹치지 않는지 독립
화면으로 다시 확인했다.

| 페이지 | 현재 역할 | 정본 파일 |
|---|---|---|
| 1 · 목적과 브랜치 전략 | 목표 `vendor-merge` Cycle과 배포 전 조건 | `docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-fragment.html` |
| 2 · 검사기 원리 | 특정 후보 결과를 섞지 않은 검사 방법·한계 | `docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-fragment.html` |
| 3 · 검사 전 사전환경 설정 | OM_TEMP 1.13.0 실제 diff·Manifest 7개·기준자료 | `harness/registrations/om-temp-1.13.0/render_manifest_evidence_guide.py` |
| 4 · OM_TEMP 코드 업그레이드 연습 | commit별 충돌 진단과 완료·미완료 판정 | `harness/registrations/om-temp-1.13.1/render_upgrade_guide.py` |
| 5 · 실제 적용과 결과 확인 | 코드 변경·Manifest·검사 결과·승인 조건 연결 | `docs/00-사용가이드/공유문서/openmetadata-phase3-demo-fragment.html` |

## 1. 저장소와 브랜치

| 구분 | 저장소와 브랜치 | 의미 |
|---|---|---|
| 과거 구현 참고 소스 | `easyseop/OpenMetadata` 브랜치 `codex/bank-vendor-1.13.1-rebuild` | BANK-OM-001~011 코드의 이전 검사 후보. 현재 업그레이드·배포 대상은 아니며 008~011 ID는 사용자 확정 전 |
| 현재 로컬 제품 검토 브랜치 | `codex/strict-gate-validation` | remote 이름이 `product`인 위 제품 브랜치를 추적하며 검사에 사용 |
| 변경관리·검사 저장소 | `easyseop/openmetadata-test` 브랜치 `codex/strict-manifest-gates` | BANK-OM Manifest, 검사기, 테스트, 공유문서와 인수인계를 관리 |
| 공식 원본 | `open-metadata/OpenMetadata` `1.13.1-release` commit `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9` | 현재 커스터마이징 적용 기준 |
| 업그레이드 시연 제품 저장소 | private `easyseop/OM_TEMP` | 원격에는 1.13.0 공식 코드와 001~007 재구현 코드, 다른 작업 노트북 로컬에는 1.13.1 재적용 결과가 있음 |

`easyseop/OpenMetadata`의 기본 브랜치에 행내 커스터마이징이 보이지 않는 것은
이상 상태가 아니다. 현재 커스터마이징은 위의 별도 제품 브랜치에 있으며,
BANK-OM Manifest와 검사기는 `easyseop/openmetadata-test`에 있다.

## 2. 공유문서 진행 상태

현재 페이지별 역할·정본·논리 판단은 0절과
[`5개_가이드_논리구조_검토결과.md`](../00-사용가이드/5개_가이드_논리구조_검토결과.md)에
한 번만 정리한다. 이 절에서는 남은 실행 작업만 관리한다.

- 실제 `vendor-merge` 방식으로 1.13.1 후보를 다시 만들고 후보 생성 이력,
  candidate lock의 `integration_strategy`와 결과가 일치하는지 검사한다.
- 담당자를 Registry에 지정하고 Contract test 7개, OpenMetadata 전체 build,
  행내 API·화면·DB 테스트를 실행한다.
- 위 결과가 같은 commit·배포 파일을 가리키는지 확인한 뒤에만 검증 tag와 배포
  승인 자료를 만든다.
- 최종 시연에서는 Git 병합 전후, 충돌, 해결 commit, 검사 명령과 PASS·APPROVAL·
  BLOCK 라벨을 실제 화면 캡처로 연결한다.

### OM_TEMP 현재 구성

2026-07-28 KST에 다음 두 브랜치를 원격에 push했다.

| 브랜치 | 원격 SHA | 내용 |
|---|---|---|
| `patch/om-1.13.0` | `2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50` | 공식 `1.13.0-release` commit `f329dd4…`의 코드 트리와 동일한 독립 스냅샷 |
| `custom/om-1.13.0` | `7d19c8952612e77467b0a80d6287170d814f1de1` | 공식 1.13.0 전체 코드에 1.13.0 구조로 재구성한 BANK-OM-001~007과 007 후속 commit을 순서대로 적용 |

OM_TEMP는 전체 OpenMetadata 과거 Git 이력을 복사하지 않았다. 첫 push에서 전체
이력 전송이 GitHub HTTP 500으로 실패해, 공식 1.13.0 시점의 파일 전체를 독립
기준 commit으로 만들고 원본 tag·commit·Git tree 값을 commit 본문에 기록했다.
Git tree는 해당 commit의 전체 파일 내용을 식별하는 값이다. 공식 1.13.0 tree와
OM_TEMP patch tree가
`da56c24d61a98dc4ed1001800c80866a13bc1645`로 동일한 것을 확인했다.

`custom/om-1.13.0`에는 BANK-OM 커밋 8개가 있다. 001~006은 각각 한 commit이고,
007은 최초 적용과 후속 보완 두 commit이다. 008~011은 넣지 않았다. 두 브랜치
사이 실제 변경 파일은 111개다.

2026-07-28 KST에 실제 OM_TEMP commit을 기준으로 다음 작업을 추가했다.

- `harness/registrations/om-temp-1.13.0/manifests/`에 BANK-OM-001~007
  Manifest 등록본 7개 생성
- `generate_manifest_drafts.py`로 각 commit의 전체 변경 파일을 다시 추출할 수
  있도록 자동화
- BANK-OM-007의 최초 8개 경로와 후속 commit의 추가 2개 경로를 분리 등록
- 7개 Manifest의 스키마·기본 의미 검사와 실제 Git diff 일치 확인 통과
- 각 commit의 실제 GitHub 캡처, 설명용 강조본, BANK-OM-005 전체 diff 캡처,
  Manifest 전체를 ID별 펼치기로 구성
- 같은 미리보기에 `1. Manifest 등록 → 2. 검사 기준자료 등록 → 3. 로컬 검사
  대상 연결`을 추가하고 화면 제목을 `OM_TEMP 검사 전 사전환경 설정 가이드`로
  변경
- Registry·Contracts·공용 파일 소유정보·111개 전체 변경 목록·선택
  Patch-lock을 각각 `의미 → 만드는 시점 → 실제 사용 → 예시 → 검사 결과`로
  설명
- `.agents/skills/clarity-preflight-review/SKILL.md`에도 위 설명 순서를
  필수 검토 기준으로 추가

Registry·Contracts·공용 파일 소유정보·111개 전체 변경 목록은 이후 실제
생성했고, 등록자료 검사 5종과 소스 검사 8종이 PASS했다. `1.13.1` 업그레이드도
로컬에서 수행했다. 아직 남은 일은 환경이 필요한 Contract test 7개, 전체 build,
담당자 지정, `verified/...` tag 생성과 배포 승인이다. Patch-lock은
patch-replay를 선택할 때만 생성한다. `candidate/...` branch는 설계에서
제외했다.

Manifest 작성 절차는
[`OM_TEMP_Manifest_작성_단계별_가이드.md`](../00-사용가이드/OM_TEMP_Manifest_작성_단계별_가이드.md)에
정리했다. 각 commit 캡처와 실제 Manifest 등록본 전체는
[`OM_TEMP_커밋별_Manifest_등록_가이드.md`](../00-사용가이드/OM_TEMP_커밋별_Manifest_등록_가이드.md),
화면 미리보기는
[`OM_TEMP_커밋별_Manifest_등록_가이드_미리보기.html`](../00-사용가이드/OM_TEMP_커밋별_Manifest_등록_가이드_미리보기.html)에
있다. 기존 `harness/registrations/kb-openmetadata/`는 1.13.1 기준이므로
수정하지 않았고, 1.13.0 등록본은 별도 등록 묶음으로 생성했다.

향후 태그는 `patch/om-1.13.0` snapshot에
`baseline/om-1.13.0`, 검사에 사용한 정확한 `custom/om-1.13.0` SHA에
`verified/om-1.13.0-bank.1` 형식으로 붙인다. 현재 두 태그는 아직 만들지
않았다. 검증 태그는 Manifest·Git 범위·필수 test와 정해진 gate를 통과한 뒤에만
만들며, 그 자체가 행내 운영 배포 완료를 뜻하지 않는다고 기록한다.

검토본을 승인본이라고 표시하지 않는다. 사용자가 명시적으로 승인한 범위와 아직
검토 중인 범위를 문서와 화면에서 구분한다.

## 3. 1차에서 확정한 설계 설명

- 공식 OpenMetadata 저장소의 새 버전은 패치 브랜치로 가져온다.
- 행내 커스터마이징 브랜치는 BANK-OM ID별 커밋을 유지한다.
- 다음 버전 후보는 새 `patch`에서 커스터마이징 commit을 다시 쌓는 것을 기본으로
  하지 않는다. 직전 `custom` branch의 전체 이력에 새 공식 `patch`를 병합하는
  `vendor-merge`가 기본 운영 전략이다.
- 버전별 장기 작업 브랜치는 `patch/om-<version>`과
  `custom/om-<version>` 두 개만 사용한다.
- 별도의 장기 `candidate/...` 브랜치는 만들지 않는다. 검사 대상은
  `custom/...` 브랜치의 Git commit SHA와 digest로 고정하고, 통과한 상태는
  `verified/om-<version>-bank.<revision>` tag로 보존한다.
- OM_TEMP 1.13.1 연습의 임시 upgrade branch는 충돌 진단을 위한 작업 공간이며 결과와
  검증 tag를 보존한 뒤 삭제할 수 있다. 검사기 코드에서 `candidate`는 Git
  브랜치 이름이 아니라 검사 대상 코드 상태를 뜻한다.
- 새 공식 버전에 커스터마이징을 적용한 뒤 검사기를 실행하고, 필수 검사가 끝난
  경우에만 배포 검토로 넘어간다.
- BANK-OM ID는 사람이 정해진 양식으로 발급한다. LLM이 임의로 번호를 결정하지
  않는다.
- 커밋 메시지에는 본문과 별도로 `Customization-ID: BANK-OM-nnn` 항목을 넣는다.
  BANK-OM ID와 Git commit SHA는 서로 다른 값이다.
- `changed_paths`는 현재 OpenMetadata 버전에서 같은 BANK-OM ID가 붙은 모든
  커밋이 실제로 변경한 전체 파일 목록이다.
- `required_changed_paths`는 그중 최종 코드에서 실제 변경이 확인되지 않으면
  해당 커스터마이징이 빠졌다고 판단할 핵심 파일 목록이다.
- `upgrade_watch`는 공식 업그레이드 때 다시 비교할 파일·설정·라이브러리
  목록이다. Manifest 생성기가 BANK-OM 커밋의 실제 변경 파일을 Git에서 자동
  포함하고, 직접 수정하지 않은 의존 파일은 담당자 등록과 직접 참조 후보 제안을
  함께 사용한다.
- 폴더 전체를 넓게 허용하지 않고 현재 확인된 파일을 개별 경로로 등록하는 것이
  기본 원칙이다.

등록과 운영 방법의 정본은
[`docs/02-설계/bank_om_registration_policy.md`](../02-설계/bank_om_registration_policy.md)다.

## 4. 2차에서 확인한 검사기 원리와 한계

관련 검사기 구현 코드와 단위 테스트를 다시 확인했다. 관련 단위 테스트는
통과했지만, 다음 예외 가능성은 남아 있다.

Git 커밋과 파일 변경을 확인하는 T25-R·T25·T26·T30·T31·T40·T41·T42·T43·T93은
Java·TypeScript·Python·JSON·YAML·SQL 등 파일 종류와 관계없이 사용할 수 있다.
공식 원본 이후 각 커밋에서 바뀐 파일 경로와 공식 원본 대비 최종 파일 상태를
확인하므로 프론트엔드와 백엔드에 같은 변경관리 규칙을 적용할 수 있다. 그러나
이 공통 계층은 Java·TypeScript 등 파일 내부 코드의 의미나 실행 동작을
언어에 관계없이 해석하지는 않는다. T60-I는 현재 Python pytest 코드만 확인하고
T63은 TypeScript 전용이며, T61·T62는 Python pytest 실행 연결을 사용한다.
Java JUnit·TypeScript Jest를 직접 등록하고 실행하려면 언어·도구별 연결을
추가해야 한다.

정리하면 “모든 변경 파일이 검사 대상이 되는가?”에는 예라고 답할 수 있지만,
“모든 언어의 코드 동작을 현재 검사기가 직접 이해하고 테스트하는가?”에는
아니라고 답해야 한다. 저장소 경로 분류와 BANK-OM Manifest에 등록하지 않은
변경 경로는 공통 변경관리 검사에서 통과시키지 않는다.

| 검사 | 확인된 핵심 원리 | 운영 전에 필요한 보완 |
|---|---|---|
| T25-R | JSON은 값으로 비교하고, 나머지 파일은 Git 차이가 없어야 한다. Java 파일의 빈 줄 하나도 차이로 판단한다. | 서식 차이를 자동 통과시키지 말고 별도 표시 후 담당자 검토 |
| T25 | Git 포함 관계로 공식 commit이 행내 코드 이력에 있는지 확인한다. | 충돌 해결과 실제 동작은 별도 검사 |
| T26 | 모든 활성 BANK-OM ID의 필수 파일·계약·테스트 연결을 확인한다. | 파일 존재만으로 기능 정상이라고 판단하지 않음 |
| T60-I | `contracts.yaml`에 등록한 Python pytest 파일과 함수가 실제로 존재하는지 AST로 확인한다. 현재 9개 테스트는 API·검색·화면·한글 입력·연결 스키마를 다룬다. | Java JUnit·TypeScript Jest와 Manifest의 `direct_tests` 존재 확인을 추가하고, 테스트 품질과 실행 성공은 T61·T62에서 확인 |
| T30 | 공식 원본 이후의 모든 Git 커밋과 `Customization-ID:` 항목을 읽는다. | 하나의 ID에 다른 목적을 섞지 않도록 리뷰 |
| T31 | 여러 커밋 사용 허용, 연속성, 폐기 ID, 선행 관계 순환을 확인한다. | 누락된 업무 선행 관계는 사람이 등록 |
| T40 | 커밋별 전체 변경 파일과 최종 필수 변경 파일을 양방향으로 비교한다. | 파일 내부의 잘못된 줄은 코드 리뷰와 테스트로 확인 |
| T41 | AST가 아니라 민감 경로 규칙과 실제 변경 파일을 비교한다. | 정적 보안 분석과 보안 담당자 리뷰 추가 |
| T42 | 새 공식 버전의 Git 차이와 `upgrade_watch`를 비교한다. 실제 변경 경로 자동 포함과 직접 참조 후보 제시는 구현돼 있다. | 간접 호출·런타임 설정처럼 이름이 드러나지 않는 의존 관계는 담당자 확인 |
| T43 | 커스터마이징 수·변경 줄·공유 파일 수·충돌률을 정책 한도와 비교한다. | 충돌률을 명령 인자가 아니라 실제 재적용 결과에서 자동 계산 |
| T93 | ID별 실제 변경 파일과 등록 파일을 비교하고, 새 공식 버전에서 감시 규칙이 유효한지 확인한다. | 민감 경로 규칙도 노후화 검사에 포함 |
| T61 | 커스터마이징이 없는 버전에서 필수 테스트가 실패하는지 확인한다. | 누락 때문에 실패했는지 오류 종류와 메시지까지 확인 |
| T62 | 제품 commit SHA, 배포 파일 digest, 검사기와 테스트 버전을 결과에 연결한다. | DB·검색엔진·설정 등 실행 환경 digest와 실행 시스템 서명 추가 |
| T63 | 공식 원본과 행내 코드의 TypeScript 파일 경로·오류 코드 발생 횟수를 비교한다. | Node·Yarn·전체 로그 digest를 검사 결과에 강제 연결 |
| T90 | 정해진 업그레이드 12단계 결과 문서와 코드·배포 파일·T62 결과의 연결을 확인한다. | 각 단계를 실제로 실행한 로그와 서명 검증 |
| T91 | 승인한 commit·이미지·Helm·검사 결과 digest와 실제 배포값을 비교한다. | 외부망에서 내부망으로 옮긴 뒤 별도 서명·해시 재검증 |

## 5. 현재 확인된 실제 상태

- 현재 제품 코드 commit: `849ae756cd238f218b5e3a6c795a392305cb32ee`
- 공식 원본 commit: `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9`
- 현재 제품 코드에는 `BANK-OM-001`부터 `BANK-OM-011`까지의 commit이 있다.
  008~011은 이전 Codex 작업에서 기술 보완용으로 추가한 임시 ID이므로 사용자가
  정식 커스터마이징 ID로 확정하기 전에는 승인된 11개라고 표현하지 않는다.
- 소스 검사: T25·T26·T60-I·T30·T31·T40·T41·T93 통과
- T60-I: 등록한 필수 Python 테스트 함수 9개 확인
- T42: 이 `849ae756...` 기존 후보만 놓고 보면 같은 1.13.1을 양쪽에 넣은
  연결 확인이므로 실제 업그레이드 증거가 아니다. 별도 OM_TEMP 연습에서는
  공식 1.13.0→1.13.1 비교를 실제 수행했다.
- T43: 실제 업그레이드 충돌률이 아니라 연결 확인용 입력을 사용했으므로 실제
  업그레이드 승인 근거가 아님
- T61: 소스에서 실행 가능한 2개만 확인했으며 전체 5개 중 나머지 3개는 행내
  배포 환경이 필요
- T62: 실행기와 사전 환경 점검은 구현했지만 실제 행내 실행 결과 없음
- T63: 새로운 파일 경로·오류 코드 조합은 없지만 공식 원본부터 있던 오류가
  남아 있어 담당자 승인 필요
- T90·T91: 실제 행내 업그레이드와 배포 승격을 실행하지 않음
- 결론: 소스 커스터마이징 관리 검사는 진행됐지만 운영 배포 승인 상태는 아님
- 부록의 과거 코드 검사 문서 작성 시 소스 검사 명령을 다시 실행해 T25·T26·T60-I·T30·T31·
  T40·T41·T93 통과를 확인했다. 이 실행은 다음 공식 버전 업그레이드나 행내
  운영 환경 검사가 아니다.

## 6. 검증 명령

소스 검사:

```bash
./.venv/bin/python harness/registrations/kb-openmetadata/run_source_candidate_gates.py \
  --repo ../review-kb-openmetadata \
  --harness harness \
  --registration harness/registrations/kb-openmetadata \
  --layout harness/policies/repository-layout.yaml \
  --sensitive-zones harness/policies/sensitive-zones.yaml
```

이번 2차 검토에서 다시 실행한 관련 단위 테스트:

```bash
./.venv/bin/pytest -q \
  harness/tests/test_ancestry.py \
  harness/tests/test_contracts.py \
  harness/tests/test_debt.py \
  harness/tests/test_drift.py \
  harness/tests/test_invariants.py \
  harness/tests/test_patchkill.py \
  harness/tests/test_policy_drift.py \
  harness/tests/test_release.py \
  harness/tests/test_survival.py \
  harness/tests/test_testruns.py \
  harness/tests/test_tsc_baseline.py \
  harness/tests/test_upgrade_run.py \
  harness/tests/test_upgrade_watch.py \
  harness/tests/test_vendor_rebuild.py \
  harness/tests/test_zones.py
```

관련 단위 테스트는 통과했으며, 환경이 필요한 테스트는 skip으로 남았다.

### OM_TEMP 1.13.0 등록 및 소스 검사

2026-07-28 기준으로 다음 실제 등록자료를
`harness/registrations/om-temp-1.13.0/`에 생성했다.

- `customization-registry.yaml`: BANK-OM-001~007 7개, 담당자 상태는 `pending`
- `contracts.yaml`: Contract 7개, 필수 Python pytest selector 9개
- `shared-path-owners.yaml`: 여러 ID가 함께 변경한 경로 37개
- `source-snapshot-path-owners.yaml`: 최초 source snapshot의 111개 변경 경로를
  해당 시점의 BANK-OM ID에 연결한 자동 생성 자료. T25-R 과거 코드 재구성에만
  사용하며 현재 범위 검사는 Manifest `changed_paths`와
  `shared-path-owners.yaml`을 사용한다.
- `source-diff-paths.txt`: 공식 1.13.0 대비 전체 변경 경로 111개
- `repository-layout.yaml`, `sensitive-zones.yaml`: 공식 1.13.0 SHA에 고정한 경로 정책
- `registration-validation-results.json`: 사전자료 검증 5개 PASS
- `source-gate-results.json`: 소스 검사 8개 PASS

Manifest schema v2는 같은 BANK-OM ID의 모든 commit이 현재 버전에서 변경한
파일을 `implementation.changed_paths` 한 목록에 합친다. BANK-OM-007은 최초
commit `62e39da8...`의 8개 파일과 후속 commit `7d19c895...`의 새 파일 2개를
합쳐 10개를 관리한다. 기능 변경 SHA 여러 개는 각각의 변경 근거로 보존하며,
최종 검사 대상은 Candidate lock의 custom branch 후보 SHA 하나로 별도 고정한다.

원격 OM_TEMP는 공식 1.13.0 파일 tree를 독립 commit으로 가져와 공식 계보가
없다. 검사에는 공식 `f329dd4a7e...`에서 시작해 같은 BANK-OM 변경을 순서대로
적용한 로컬 `custom/om-1.13.0` commit `63820f88eb...`을 사용했다. 이 로컬
후보와 원격 custom commit `7d19c89526...`의 최종 tree는
`9495a31c99...`로 같다.

사전자료 검증:

```bash
./.venv/bin/python \
  harness/registrations/om-temp-1.13.0/validate_registration_bundle.py \
  --repo ../om-temp-1.13.0-custom \
  --output harness/registrations/om-temp-1.13.0/registration-validation-results.json
```

소스 검사:

```bash
./.venv/bin/python harness/run_source_candidate_gates.py \
  --repo ../om-temp-1.13.0-custom \
  --harness harness \
  --registration harness/registrations/om-temp-1.13.0 \
  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \
  --sensitive-zones harness/registrations/om-temp-1.13.0/sensitive-zones.yaml \
  --output harness/registrations/om-temp-1.13.0/source-gate-results.json
```

소스 검사 PASS는 코드 구조와 변경 이력이 등록자료와 일치한다는 뜻이다.
OpenMetadata 전체 build, Contract test 실행, 담당자 지정, 1.13.1 업그레이드,
운영 배포 승인은 아직 수행하지 않았다.

### OM_TEMP 1.13.0 → 1.13.1 실제 업그레이드

1.13.1 업그레이드는 2026-07-28 로컬에서 실제 수행했다.

- 공식 기준: `1.13.1-release`
  (`afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9`)
- 공식 코드 branch: `patch/om-1.13.1`
- 커스터마이징 적용 branch: `custom/om-1.13.1`
- 최종 검사 대상 commit:
  `dee330ebd5abfe33e1ac61e1ca31879746a1b423`
- 공식 1.13.0→1.13.1 변경: 834개 파일
- `upgrade_watch` 결과: BANK-OM-001~007 모두 영향 경로가 있어 `approval`
- 실제 충돌: BANK-OM-001~004 적용 시 같은 번역 JSON 18개에서 반복 발생
- 충돌 해결: 공식 변경 leaf key와 BANK-OM leaf key가 겹치지 않을 때만
  공식 JSON에 BANK-OM 키를 추가. 겹치면 자동 중단하는 도구 사용
- 위 JSON 해결 도구는 OpenMetadata의 기존 기능이나 확정된 행내 정책이 아니다.
  이번 업그레이드 연습에서 추가했으며 현재는 선택 화면·승인자 기록 없이
  담당자가 명령을 직접 실행한다. 동일 항목 겹침과 JSON 외 충돌은 자동 해결하지
  않고 중단한다.
- BANK-OM-005~007: 충돌 없이 적용
- 1.13.1 등록자료: Manifest 7개, Contract 7개, test selector 9개,
  전체 경로 111개, 공용 경로 37개
- 1.13.1 사전자료 검증 5종 PASS
- 1.13.1 소스 검사 8종 PASS
- Contract test 수집 10개: 필수 Contract test 2개 PASS·7개 SKIP,
  추가 한글 입력 소스 검사 1개 PASS, 실패 0개
- SKIP 사유: `OPENMETADATA_BASE_URL`, `BANK_COLUMN_UI_URL`,
  `BANK_DATA_ASSERTIONS_URL`, `BANK_IME_EDITOR_URL` 미설정
- 전체 build 사전확인: 현재 노트북에 Java Runtime·Maven·Yarn·UI
  `node_modules`가 없어 실행 전(`environment_pending`)

상세 결과:

- `harness/registrations/om-temp-1.13.1/upgrade-watch-results.json`
- `harness/registrations/om-temp-1.13.1/upgrade-application-results.json`
- `harness/registrations/om-temp-1.13.1/conflict-replay-evidence.txt`
- `harness/registrations/om-temp-1.13.1/registration-validation-results.json`
- `harness/registrations/om-temp-1.13.1/source-gate-results.json`
- `harness/registrations/om-temp-1.13.1/contract-test-results.json`
- `harness/registrations/om-temp-1.13.1/build-preflight-results.json`
- `docs/00-사용가이드/OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드_미리보기.html`

두 1.13.1 branch는 로컬에만 만들었고 아직 GitHub에 push하지 않았다. 전체
build, 환경이 필요한 Contract test 7개, 담당자 지정, 검증 tag와 배포 승인은
남아 있다. SKIP은 PASS로 계산하지 않는다.

2026-07-28 KST에 BANK-OM-001의 원래 1.13.0 commit `4df83b311f`를 공식
1.13.1에 다시 적용해 충돌을 재현했다. Git에서 `Entity.java`와
`CollectionDAO.java`는 자동 병합됐고 번역 JSON 18개는 `UU`로 중단되는 것을
확인했다. 가이드에는 실제 Git 출력, `ko-kr.json`의 BANK-OM 추가 항목 9개,
해결 결과 commit `83b1e0ac7d`, 현재 구현과 정식 승인 절차의 차이를 추가했다.
정식 운영 전 추가 개발 대상은 dry-run 비교, 자동 병합/수동 해결 선택,
승인자·대상 commit·결과 기록, `BLOCK` 결과 연결이다.

같은 시점에 `capture_conflict_replay.py`로 BANK-OM-001 충돌을 다시 재현하고
다음 증거를 `harness/registrations/om-temp-1.13.1/conflict-evidence/`에
보관했다.

- `BANK-OM-001_ko-kr_full_conflict.txt`: Git 충돌 표식을 포함한 실제
  `ko-kr.json` 6,614줄
- `BANK-OM-001_ko-kr_resolution.diff`: 공식 1.13.1과 해결 commit의 실제
  43줄 diff
- `BANK-OM-001_ko-kr_resolved.json`: 해결 후 전체 JSON
- `BANK-OM-001_ko-kr_capture.json`: BANK-OM ID, source commit, target tag,
  해결 commit과 충돌 경로 18개

업그레이드 가이드에는 다음 설명을 추가했다.

- 업그레이드 전 영향 확인은 `upgrade-watch`(T42)가 담당한다. 현재 Manifest
  생성기는 Git의 실제 변경 경로를 watch에 자동 포함하고, 검사기는 새 공식
  변경 파일의 직접 참조 후보를 제시한다. 미수정·간접 의존 경로는 담당자가
  확인해 등록한다.
- 검사 대상 `dee330ebd5...`는 공식 commit이나 BANK-OM ID가 아니라
  `custom/om-1.13.1`의 최종 Git commit SHA
- 번역 항목 이름의 교집합은 0개였지만 공식 JSON의 전체 서식 변경과 BANK-OM
  항목 추가가 같은 객체에 있어 Git의 줄 단위 충돌이 발생한 이유
- 현재 Git 원문에는 source commit SHA만 나오며 BANK-OM ID 자동 표시는
  추가 개발 대상
- 현재 해결 도구에는 선택·승인자 기록이 없고, 정식 운영에는 dry-run plan,
  담당자 선택, 승인 파일 검증, ID 포함 로그, BLOCK과 재검사 연결이 필요
- 현재 검사기로 증명한 소스 수준 범위와 build·실제 업무 동작·사람 승인·배포
  안전성처럼 아직 증명하지 못한 범위

HTML 다시 생성:

```bash
python3 /Users/seop/.codex/plugins/cache/openai-bundled/visualize/1.0.15/skills/visualize/scripts/render.py \
  docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-fragment.html \
  docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-preview.html

python3 /Users/seop/.codex/plugins/cache/openai-bundled/visualize/1.0.15/skills/visualize/scripts/render.py \
  docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-fragment.html \
  docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-preview.html

python3 /Users/seop/.codex/plugins/cache/openai-bundled/visualize/1.0.15/skills/visualize/scripts/render.py \
  docs/00-사용가이드/공유문서/openmetadata-phase3-demo-fragment.html \
  docs/00-사용가이드/공유문서/openmetadata-phase3-demo-preview.html

./.venv/bin/python harness/tools/enable_guide_navigation.py
```

다른 노트북에서 위 절대 경로가 다르면 설치된 `visualize` 스킬의
`scripts/render.py` 경로를 찾아 바꾼다.

### 2026-07-28 문서 현행화 및 시각 검수

- 1~5번 문서에서 과거 용어 `변경관리표`를 현재 정식 용어 `Manifest`로
  통일했다.
- watch 설명은 현재 구현과 일치하도록 수정했다. 커밋의 실제 변경 경로는
  Manifest 생성기가 Git에서 watch에 자동 포함하고, 새 공식 변경 파일의 직접
  참조 후보는 검사기가 결과에 제시한다. 간접 의존 관계는 담당자가 확인한다.
- “watch 자동 등록은 향후 개선”이라는 오래된 문구를 제거했다. 자동 제안이
  Manifest를 임의로 수정하거나 승인하는 기능은 아니라는 한계는 유지했다.
- 1번의 흰 배경 보조문구 색을 진하게 조정하고, 첫 `왜 필요한가` 카드의
  글자·테두리 대비를 높였다.
- 부록(과거 참고 코드 검사)의 코드 비교 박스에 짙은 배경, 밝은 글자, 초록색
  추가 코드 표시와 줄바꿈을 적용했다.
- 다섯 페이지의 상·하단 이전/다음 링크와 가로 넘침 여부를 브라우저에서
  확인했다.
- 관련 watch 단위 테스트:
  `test_watch_suggest.py`, `test_upgrade_watch.py`, `test_impact.py` 통과
  (환경이 필요한 항목은 기존 표시대로 skip).

## 7. 다른 노트북에서 재개하는 순서

1. `easyseop/openmetadata-test`의 `codex/strict-manifest-gates` 브랜치를 받는다.
2. 이 문서와 `SHARING_ARTIFACT_REQUIREMENTS.md`를 읽는다.
3. `.agents/skills/clarity-preflight-review/SKILL.md`를 읽고 이후 모든 공유문서
   검토에 적용한다.
4. 공유문서는 `목적과 브랜치 전략 → 검사기 원리 → 검사 전 사전환경 설정 →
   OM_TEMP 코드 업그레이드 연습 → 실제 적용과 결과 확인` 순서로 읽는다.
5. `OM_TEMP_커밋별_Manifest_등록_가이드_미리보기.html`에서 Manifest 등록,
   기준자료 생성, 로컬 연결, 실제 소스 검사 4단계를 확인한다. 파일명은 유지했지만
   화면 제목은 `OM_TEMP 검사 전 사전환경 설정 가이드`다. 실제 명령 실행에서는
   이 사전환경 설정을 검사기보다 먼저 완료한다.
6. 담당 부서가 Registry의 `UNASSIGNED` 7개를 실제 담당자로 바꾸기 전에는
   배포 준비 완료로 표시하지 않는다.
7. Patch-lock은 vendor-merge 소스 검사의 필수가 아니다. patch-replay·복구·
   재현 시연을 선택할 때만 만든다.
8. `custom/om-1.13.1`에서 가능한 build와 Contract test를 실행하고 결과를
   1.13.1 가이드에 추가한다.
9. 다섯 HTML에 남은 사용자 피드백을 반영한다.
10. 환경 test·담당자 승인·검증 tag·배포 결과 화면을 4번 페이지에 추가한다.
11. 다섯 페이지의 중복과 용어를 다시 검토한다.
12. standalone fragment를 다시 렌더링했다면
   `harness/tools/enable_guide_navigation.py`를 실행해 각 페이지의
   이전·다음 이동 영역을 다시 생성한다.
13. 작업 완료 후 이 문서의 상태·검증·다음 단계를 갱신하고 같은 브랜치에
   커밋·푸시한다.

## 8. 작업 시 주의

- `docs/00-사용가이드/.비개발자_시연_가이드.md.swp`는 사용자의 편집기 임시
  파일이다. 수정하거나 stage하지 않는다.
- 비밀값, 인증 토큰, 행내 URL과 실제 데이터는 문서나 Git에 넣지 않는다.

## 9. 2026-07-28 원격 인수인계

사용자가 노트북을 종료하기 전에 현재 작업을 보존하도록 요청해 이 상태를
커밋·푸시한다.

### 이번에 완료한 내용

- `clarity-preflight-review` 스킬에 문맥 없이 남은 질문·용어·전환 문장을
  차단하는 기준을 추가하고 저장소 안의 휴대용 스킬에도 반영했다.
- 1번 문서의 저장소 역할을 다음처럼 다시 썼다.
  - `easyseop/OpenMetadata`: 처음 분석할 때 참고한 과거 커스터마이징 코드
    보관본이며 현재 업그레이드·배포 대상이 아님
  - `easyseop/OM_TEMP`: 현재 1.13.0→1.13.1 업그레이드와 검사를 재현하는
    코드 저장소
  - `easyseop/openmetadata-test`: Manifest·검사기·결과·가이드·인수인계
    저장소
- 2번 문서의 `행내 배포용 OpenMetadata` 표현을 실제 입력인 `검사할 custom
  branch` 또는 `검사한 custom commit`으로 바꿨다.
- 4번 문서에서 `easyseop/OpenMetadata`를 배포 준비 코드가 아닌 과거 구현
  참고 코드로 정정했다. BANK-OM-001~007 업무 커스터마이징과 008~011 기술
  보완 코드를 구분했다.
- 현재 4번 문서는 실제 cherry-pick 충돌 발생 화면 → 충돌 원문 → 해결 diff →
  JSON 충돌 보조 도구의 입력·출력·한계 → 정식 승인 절차 순서로 다시 구성했다.
  보조 도구는 충돌 JSON 파일을 수정하고 터미널 건수만 출력하며 별도 보고서나
  승인 파일을 만들지 않는다는 점을 명시했다.
- `1 → 2 → 3 → 4 → 부록` 미리보기의 이전·다음 이동 링크를 다시 생성했다.

### 다음 작업에서 먼저 확인할 내용

1. 다섯 페이지를 브라우저에서 한 번씩 열어 가로 넘침, 흐린 글자, 코드 박스,
   이전·다음 링크를 최종 확인한다.
2. Manifest schema v2의 `changed_paths`와 v1 호환 경로가 섞여 보이지 않는지
   확인하고, 사용자 가이드에는 v2만 설명한다.
3. 4번 페이지의 충돌 전·해결 후 색상 구분과 전체 diff 펼치기를 화면 크기별로
   최종 확인한다.
4. 관련 단위 테스트와 `git diff --check`를 다시 실행한다.
- 공유문서 묶음 최초 commit `becb18e`부터 최신 보강 commit `482788d`까지
  `easyseop/openmetadata-test`의 `codex/strict-manifest-gates`에 push 완료했다.
- 최신 push에 대한 `Source candidate` run `30350251032`는 성공했다.
- PR은 사용자가 요청하지 않으면 만들지 않는다.

## 10. 2026-07-28 현재 감사 결과와 다음 실행 순서

### 이번 감사에서 확인·수정한 정합성

- 오늘 GitHub 서버 기준 변경은 `18360e8` 이후 27개 commit, 149개 파일이다.
- 저장소 전용 `clarity-preflight-review` 스킬은 형식 검증을 통과했다.
- `bank_om_registration_policy.md`의 오래된 watch·owner 설명을 실제 구현과
  맞췄다. 실제 변경 경로 자동 포함과 직접 참조 후보 제안은 구현 완료이고,
  owner는 Manifest가 아니라 별도 Registry에 저장·검사한다.
- “push 승인 대기” 문구를 실제 원격 push·CI 성공 상태로 정정했다.
- 다섯 페이지를 1280×900과 390×844에서 검사했다. 전체 페이지 가로 넘침,
  깨진 이미지와 잘린 일반 문장은 0건이다.
- 현재 4번 페이지에서 긴 Python 파일 경로가 390px 화면에서 잘리는 문제 1건을
  발견해 생성기 CSS에 인라인 코드 줄바꿈 규칙을 추가하고 다시 렌더링했다.
- 당시 `1 → 2 → 3 → 과거 결과 → 실제 업그레이드` 이동을 확인했고,
  2026-07-30 재구성 후에는 `1 → 2 → 3 → 4 → 부록` 이동을 다시 확인했다.
- 이 시점 이후의 현행 문서는 후속 경로 분리 필드를 쓰지 않고 현재 버전
  `changed_paths` 하나로 통합한다.
- 전체 harness 단위 테스트는 `308 passed, 37 skipped`다. 37개 skip은 이
  노트북에 `/home/user/om-mirror`가 없어서 실행하지 못한 실제 mirror 연동
  항목이며 PASS로 계산하지 않는다. 관련 집중 테스트는 `14 passed, 5 skipped`,
  `git diff --check`도 통과했다.
- 위 변경 commit `0b0f7797...`의 원격 고정 mirror 검사는
  `348 passed, 7 operational skips`로 성공했다. 소스 gate와 source
  patch-kill 2건은 통과했고 BANK-OM-001~003 runtime 실험은 환경 대기다.
- 90일 증거 artifact:
  `source-patch-kill-evidence-30368181793-1`, ID `8691825442`, GitHub
  SHA-256 `a70e4a8a6b3944a5e2228c1185dfb1fa3142ce58027c514c13e7e8c060e8277d`

### 다음 작업

1. 다른 작업 노트북에만 있는 `patch/om-1.13.1`,
   `custom/om-1.13.1`을 private `easyseop/OM_TEMP`에 push해 재현 가능한 원격
   기준점을 만든다. 해당 로컬 branch가 없는 노트북에서 SHA를 추측해 만들지
   않는다.
2. Java Runtime·Maven·Yarn·UI 의존성이 준비된 환경에서 전체 build를 실행하고,
   실제 URL·인증·fixture가 있는 행내 환경에서 남은 Contract test 7개를
   실행한다.
3. 담당 부서가 BANK-OM-001~007 Registry의 `UNASSIGNED`를 실제 owner로
   배정한 뒤에만 검증 tag와 배포 승인 단계로 이동한다.
4. JSON 충돌 보조 도구의 정식 운영 기능인 dry-run plan, 자동/수동 선택,
   승인자·대상 SHA·결과 기록과 BLOCK 재검사 연결을 구현한다.
5. T43 충돌률을 실제 재적용 증거에서 자동 계산하고, Java JUnit·TypeScript
   Jest 및 Manifest `direct_tests` 연결을 추가한다.

## 11. 2026-07-29 1차·2차 가독성 개편

### 사용자 피드백과 반영

1. 1차 저장소 역할에서 현재 흐름에 필요 없는 `easyseop/OpenMetadata` 과거
   보관본 카드를 제거했다. 첫 화면은 현재 제품 재현 저장소 `easyseop/OM_TEMP`와
   검사 기준 저장소 `easyseop/openmetadata-test`만 보여준다. 과거 실제
   BANK-OM-001 diff의 출처 링크는 증거 provenance이므로 코드 증거 상세에만
   유지했다.
2. BANK-OM-007의 최초 8개와 후속 2개 파일은 현재 버전 Manifest의
   `changed_paths` 10개로 통합한다. 어느 파일이 어느 commit에서 추가됐는지는
   Git commit SHA 두 개와 변경 이력으로 확인한다.
   필수 파일이면 `required_changed_paths`에도 넣고, 같은 ID 후속 commit을
   쓰려면 `series.allowed: true`가 필요하다.
3. 2차 첫 화면에 네 묶음의 `검사기 지도`를 추가했다. 긴 본문은 검사기별
   독립 상세보기 17개로 바꾸고, 펼친 안에서도 `무엇을 확인하나 / 실제 검사 /
   예외·보완`으로 나눴다. T93은 변경범위와 감시규칙 두 역할이 있어 상세보기
   두 개다. 전체 입력·출력 표는 내용 삭제 없이 맨 뒤 상세보기로 이동했다.
4. T번호는 이 화면의 순번이 아니라 `openmetadata_build_plan.md`의 안정적인
   태스크 ID다. T01~T24에는 조사·정책·Manifest 스키마·Git 기반·선택 재적용
   도구가 있고, 2차가 책임자 판정용 검사기만 보여주므로 T25-R·T25부터
   시작한다.
5. 공유문서 요구사항에 `검사 결과와 책임자 판단`은 기존 증거의
   판정·보고 단계, `실제 업그레이드`는 새 버전 위에서 commit을 재적용하고
   충돌을 해결해 새 후보와 증거를 만드는 실행 단계라고 구분했다.

### 수정한 정본과 생성물

- `docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-fragment.html`
- `docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-preview.html`
- `docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-fragment.html`
- `docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-preview.html`
- `docs/02-설계/bank_om_registration_policy.md`
- `docs/04-진행/SHARING_ARTIFACT_REQUIREMENTS.md`

fragment 수정 후 두 preview를 다시 렌더링하고
`harness/tools/enable_guide_navigation.py`를 실행했다.

### 검증과 제한

- HTML 구조 검사: phase1·phase2의 div/section/details/summary/table/tr 등
  선택 요소 여닫기 불일치 0건
- phase2 상세보기: 17개, 검사기 지도 카드: 4개
- 관련 집중 테스트: 64개 수집, `55 passed, 9 skipped`
- skip 9개: 이 노트북에 `/home/user/om-mirror`가 없어 실행하지 못한
  policy-drift 5개와 upgrade-watch 4개이며 PASS로 계산하지 않는다.
- `git diff --check`: 통과
- 인앱 브라우저 자동검수: 로컬 `file://` URL이 브라우저 보안 정책에 차단돼
  이번 배치에서는 새 viewport 시각 통과를 주장하지 않는다. HTML은 생성됐으며
  사용자가 열어 최종 화면 확인을 이어갈 수 있다.
- 원격 `Source candidate` run `30371799025`: 성공. 제품 candidate
  `849ae756...`의 source gates와 source patch-kill 2건이 통과했다.
- 90일 증거 artifact: `source-patch-kill-evidence-30371799025-1`, ID
  `8693322667`, GitHub SHA-256
  `504a5850834bd2d94f3966e6b30e4850a0cb39c041597a4c215bec251e6d0743`

## 12. 2026-07-29 2차 검사기 상태·미완료 작업 표시

### 화면 기준

- 17개 상세보기 제목을 “무엇을 확인하는지” 바로 알 수 있는 이름으로
  정리했다. 예를 들어 T25는 `공식 버전 출발점 확인`, T42는
  `공식 업그레이드 영향 경로 확인`, T91은
  `검사 산출물과 배포 산출물 일치 확인`이다.
- 지도에 A~D 묶음별 현재 사용 범위를 표시했다. A는 현재 사용 가능, B는
  제한적 사용, C는 부분 실행, D는 운영 미실행이다.
- 지도와 상세의 분류가 달랐던 T60-I를 A에서 C로 옮겼다.
- Claude 독립 검토에서 서로 다른 후보의 결과가 초록 체크에 섞인 문제를
  확인했다. 수정 후 초록 원형 체크와 연한 초록 배경은
  `easyseop/OM_TEMP` commit `dee330ebd5abfe33e1ac61e1ca31879746a1b423`에
  결속된 실제 결과만 뜻한다.
- PASS 표시가 아니므로 T42의 실제 APPROVAL 결과도 체크 대상이다. 반대로
  다른 후보의 PASS·APPROVAL이나 runner-wiring 스모크는 체크하지 않는다.

### 초록 체크 분류

- A 7개: T25, T26, T30, T31, T40, T41, T93 정확 범위
- B 1개: T42
- C 1개: T60-I
- D 0개

합계 9개다. T25-R은 현재 ancestry 방식에 `해당 없음`, T61은
`별도 kb-openmetadata 후보 2건 확인`, T63과 T93 정책 노후화는
`현재 OM_TEMP 후보 미실행`으로 표시한다.

### 남은 구현·외부 입력

`운영 적용 전에 우선 보완할 항목`은 후보별 상태를 분리하고 다음 실제 작업과
완료 기준을 기록한다.

1. T25-R: OM_TEMP에 억지로 실행하지 않고 향후 ancestry 없는 snapshot 이관
   후보에서만 실행
2. T43: 실제 재적용 증거에서 충돌률 자동 계산 및 증거 digest 결속
3. T61: BANK-OM-001~003 제거본을 행내 환경에 배포해 의도한 실패와 포함본
   통과를 같은 candidate SHA에 결속
4. T62: 행내 URL·인증·fixture·artifact와 환경 digest로 대기 중인 Contract
   test 7개 실행
5. T63: OM_TEMP 공식 원본·후보 TypeScript 전체 로그와 실행환경 digest 결속
6. T93 policy-drift: OM_TEMP tree와 실제 정책으로 실행해 스모크가 아닌 결과 저장
7. T90: 12단계 실제 업그레이드와 단계별 로그·담당자·SHA 기록
8. T91: 이미지·Helm·검사 결과 digest와 실제 승격 대상을 서명해 비교

현재 OM_TEMP 결과가 있는 T41, T42, T60-I도 각각 정적 보안 분석, 간접 의존,
JUnit/Jest/direct_tests 등 운영 범위 보강이 남아 별도 목록으로 분리했다.

### 검증

- Claude 검토 전 생성물은 상세보기 17개, 초록 표시 12개였으며, 세 후보
  결속 오류(T25-R·T63·T93 policy)를 확인했다.
- 수정본 구조 검사: 상세보기 17개, 초록 표시 9개, 지도 카드 4개, 범례 포함
  체크 아이콘 10개, 후보 상태 pill 4개
- 선택 HTML 요소의 여닫기 불일치 0건
- 관련 집중 테스트: 64개 수집, `55 passed, 9 skipped`
- skip 9개는 `/home/user/om-mirror`가 없는 로컬 환경의 policy-drift 5개와
  upgrade-watch 4개이며 PASS로 계산하지 않는다.
- `git diff --check`: 통과
- 원격 `Source candidate` run `30373496657`: 성공. `348 passed,
  7 operational skips`, 고정 source gates와 source patch-kill 2건 통과
- 90일 증거 artifact: `source-patch-kill-evidence-30373496657-1`, ID
  `8693987394`, GitHub SHA-256
  `3d089c30b3fcbc141674a964c8a803d1f51f2352cb9962af385e428a10dee29c`
- Claude 검토 반영 원격 run `30376209792`: 성공. `348 passed,
  7 operational skips`, 고정 source gates 8개와 source patch-kill 2건 통과
- 새 90일 증거 artifact: `source-patch-kill-evidence-30376209792-1`, ID
  `8695135853`, GitHub SHA-256
  `465b509049c81782de6100d499411e845b33bac4b0b9a4afccf431f0a7ffde3c`

### 다른 기기에서 재개

기존 clone이 있으면 다음 순서로 최신 원격 상태를 받는다.

```bash
git fetch origin
git switch codex/strict-manifest-gates
git pull --ff-only origin codex/strict-manifest-gates
git rev-parse HEAD
```

마지막 출력이 이 문서 상단의 최신 원격 commit과 같은지 확인하고,
`docs/04-진행/CODEX_HANDOFF.md` §12와
`docs/04-진행/CLAUDE_REVIEW_HANDOFF.md` §15부터 읽는다. 새 clone이면
`easyseop/openmetadata-test`를 clone한 뒤 같은 branch로 switch한다.

## 13. 2026-07-30 공유문서 간소화·관리 파일 필드 사전

### 이번에 확정한 문서 구조

1. 1번 문서는 목적과 브랜치 전략만 남겼다. 뒤 페이지와 중복되던
   `브랜치 전략을 이해하기 위한 사전 정보`, Q&A, 검사기·결과·향후 계획
   반복 설명은 삭제했다.
2. 2번의 T61 상태 `별도 후보 2건 확인`을
   `과거 코드에서 2/5 확인`으로 바꾸고, BANK-OM-006·007의 과거
   kb-openmetadata 후보 결과이며 현재 OM_TEMP 결과가 아니라는 점을
   명시했다.
3. 3번의 산출물 표는 T 번호만 나열하지 않고 `기능별 변경 관리`,
   `검사 대상 관리`, `업무 동작 확인`, `검사 대상 고정`처럼 실제 사용
   기능을 먼저 설명한다. T 번호는 보조 표기로만 남겼다.
4. `assurance`를 포함한 관리 파일 필드를 찾을 수 있도록
   `OM_TEMP_관리파일_필드_사전_미리보기.html`을 추가했다. Manifest,
   Registry, Contracts, 공용 파일·전체 변경 목록, 경로·위험 정책,
   Candidate lock·Patch-lock, 검사 결과의 필드별 의미·작성 시점·사용
   검사·문제 시 결과를 실제 JSON Schema 기준으로 설명한다.
5. 5번에서 `cherry-pick`을 운영 필수 절차로 표현하지 않는다. 이번
   1.13.1 실행은 BANK-OM별 충돌을 분리하기 위한 commit 단위 진단이며,
   실제 운영 전략이 `vendor-merge`라면 patch branch와 custom branch를
   실제 방식으로 합친 뒤 검사기를 실행하는 운영경로 검증이 별도로
   필요하다고 명시했다.
6. 공식 버전 업그레이드 충돌을 해결할 때는 기존 BANK-OM ID를 유지한다.
   새 버전 등록 폴더에는 같은 ID의 Manifest를 복사해 후보 기준으로 다시
   검토하되, 기존 파일 안에서 해결됐다면 경로 목록을 바꾸지 않는다. 새
   새 파일은 현재 버전 `changed_paths`, 별도 후속 commit은
   `series.allowed: true`, 독립 업무 기능은 새 ID로 구분한다.
7. 2차 검사기 원리 페이지의 녹색 체크는 구현 코드 존재 표시가 아니다.
   현재 OM_TEMP 1.13.1 등록자료와 결과 파일에 실제 판정이 연결된 9개
   검사(T25·T26·T30·T31·T40·T41·T42·T60-I·T93-범위)에만 표시한다.
   T25-R은 현재 후보 해당 없음, T43·T61은 일부 입력·과거 결과만 존재,
   T93-정책·T62·T63·T90·T91은 현재 후보 또는 행내 운영 증거가 없어
   체크 대신 필요한 조건을 표시한다. 체크 자체는 PASS가 아니라 실제 판정
   확인 가능을 뜻한다.
8. 같은 기능의 후속 commit 메시지는 기존 `Customization-ID`를 유지하고,
   생성기는 같은 ID의 전체 Git diff를 합쳐 현재 버전 `changed_paths` 초안을
   만든다. 기능 변경 commit SHA는 여러 개일 수 있지만 최종 검사 대상 SHA는
   custom branch의 마지막 SHA 한 개다.
9. 1.13.1 충돌 화면 앞에 공통 기준 1.13.0, 공식 1.13.1 변경,
   BANK-OM-001 변경, Git 중단의 네 단계를 추가했다. 이번 JSON 충돌은 양쪽이
   같은 번역 값을 다르게 고친 것이 아니라 파일 형식·항목 배치가 크게 달라져
   Git의 줄 단위 자동 병합이 실패한 충돌이며, 동일 JSON 항목의 동시 변경은
   0개였음을 명시했다.
10. Claude 독립 검토에서 발견한 충돌 도식 오류를 반영했다. 충돌 원문
    6,614행 전체가 충돌한 것이 아니라 2~5,555행에 충돌 표시가 있으며,
    `HEAD` 쪽 약 2,373줄과 BANK 쪽 약 3,178줄은 전체 파일이 아닌 충돌
    블록이다. 해결 표시는 `label` 7개와 `message` 2개로 분리했고,
    HEAD·Manifest 정의, 805줄 차이의 형식 원인, BLOCK 뜻, build 미실행과
    Contract test 7개 SKIP을 첫 화면에 추가했다. 6·7단계는 기본 펼침으로
    바꾸고 증거 저장소 경로를 표시했다.
11. 충돌 구조 요약만으로는 실제 충돌 코드를 확인할 수 없다는 사용자 피드백을
    반영했다. BANK-OM-001 실제 원문에서 충돌 시작, `=======` 경계,
    BANK 쪽 9개 추가 항목의 실제 행 위치, `>>>>>>>` 종료를 행 번호와 함께
    한 방향으로 표시했다. 같은 페이지에서 6,614행 전체 원문을 내부 스크롤로
    열어볼 수 있는 펼치기도 추가했다.

### 정본과 생성물

- `docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-fragment.html`
- `docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-preview.html`
- `docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-fragment.html`
- `docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-preview.html`
- `docs/00-사용가이드/OM_TEMP_커밋별_Manifest_등록_가이드_미리보기.html`
- `docs/00-사용가이드/OM_TEMP_관리파일_필드_사전_fragment.html`
- `docs/00-사용가이드/OM_TEMP_관리파일_필드_사전_미리보기.html`
- `docs/00-사용가이드/OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드.md`
- `docs/00-사용가이드/OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드_미리보기.html`

### 검증

- Manifest·Registry·Contracts·Candidate lock·Patch-lock·commit ID 규칙 관련
  집중 테스트: `60 passed`
- `git diff --check`: 통과
- 인앱 브라우저에서 1번 중복·Q&A 제거, 2번 T61 상태, 3번 사용 기능 표,
  필드 사전 첫 화면과 수평 overflow 없음, 5번 cherry-pick 진단 범위
  문구를 확인했다.
- 1.13.1 업그레이드 페이지는 넓은 화면에서 충돌 블록·해결 구조를 확인했고,
  390px viewport에서 문서 전체 수평 overflow가 없으며 표만 내부 스크롤되는
  것을 확인했다. HTML 내부 링크 8개는 새 Claude 검토 ZIP에서 모두 열리도록
  저장소 상대 경로를 보존했다.
- 실제 충돌 코드 발췌 영역은 넓은 화면에서 행 번호, 충돌 마커, 생략 표시와
  BANK 항목이 잘리지 않고 표시되는 것을 인앱 브라우저에서 확인했다.
- 사용자 소유 Vim swap 파일
  `docs/00-사용가이드/.비개발자_시연_가이드.md.swp`는 수정·추적하지 않는다.

## 14. 2026-07-29 통합 운영 위키 초안·신입 운영 기준

### 추가한 통합 위키

- `docs/00-사용가이드/OM_TEMP_검사운영위키_구성초안.html`
- `docs/00-사용가이드/OM_TEMP_검사운영위키_데이터.js`
- `docs/00-사용가이드/OM_TEMP_검사운영위키_보고용.js`
- `docs/00-사용가이드/generate_wiki_report_data.mjs`

보고용 1~5번 가이드와 검사기·관리 파일·작업 절차 상세를 하나의 왼쪽
목차에서 찾는 위키 구조를 만들었다. 현재는 운영 완료본이 아니라 `구조 초안`
으로 표시한다. 모든 정상 예시·실패 예시·복구 명령·행내 환경값이 채워지기
전에는 신입 운영 완료본으로 표현하지 않는다.

보고용 페이지는 기존 standalone HTML을 iframe이나 `srcdoc`으로 표시하지
않는다. 각 장은 위키 공통 레이아웃 안에서 질문, 핵심 개념, 업무 흐름,
현재 확인 상태, 다음 단계와 상세 페이지 링크를 직접 렌더링한다.
`OM_TEMP_검사운영위키_보고용.js`는 상세 브랜치 페이지에서 보고용 1차의
동일한 Cycle SVG를 재사용하기 위해서만 남아 있다. 해당 SVG 원문이 바뀌면
`node docs/00-사용가이드/generate_wiki_report_data.mjs`를 실행해 재사용
데이터를 갱신한다.

### 현재 schema v2 변경 범위의 실제 검사 연결

현재 OM_TEMP Manifest는 아래 한 목록을 해당 BANK-OM ID의 현재 버전 변경
범위로 사용한다.

```text
현재 변경 범위 =
  changed_paths
```

- T40: 합친 범위 밖을 같은 ID의 commit이 변경하면 BLOCK
- T93 exact-scope: 합친 범위와 실제 ID별 Git 변경 이력을 비교
- T26: 합친 범위의 일반 파일이 없거나 공식 원본과 같으면 APPROVAL
- `required_changed_paths`에도 들어간 파일은 T26에서 같은 문제가 발생하면
  BLOCK

따라서 후속 commit의 새 파일은 `changed_paths`에 합친 순간 현재 범위 검사
대상이 되지만, 필수 파일로 자동 승격되지는 않는다. 그 파일
누락만으로 기능 미적용을 확정할 수 있을 때 담당자가
`required_changed_paths`에도 별도로 등록한다. 이 흐름과 BANK-OM-007
예시를 통합 위키 Manifest 상세에 추가했다.

### 가독성 스킬 강화

저장소와 설치된 `clarity-preflight-review` 스킬에 아래 완료 기준을 추가했다.

1. 문장마다 주체·입력·시점·비교 대상·결과가 하나로만 해석되는지 확인
2. 문단을 읽은 신입 직원이 바로 물을 질문을 예상하고 그 위치에서 답변
3. 관리 필드·명령·검사·작업마다 정상 예시와 필요한 실패 예시 확인
4. 준비 → 실행 → 결과 판정 → 실패 복구 → 재실행 → 증거 보관 →
   에스컬레이션을 문서만으로 수행 가능한지 확인

저장소 스킬과 `/Users/seop/.codex/skills/clarity-preflight-review` 설치본 모두
`quick_validate.py` 검증을 통과했다.

### 이번 변경 검증

- 통합 위키 데이터 JavaScript 문법 검사 통과
- 통합 위키 inline JavaScript 문법 검사 통과
- HTML ID 중복 없음
- `git diff --check` 통과
- Manifest·T26·T40·T93 관련 집중 테스트:
  `30 passed, 5 skipped`
- 인앱 브라우저 자동 검증은 `file://` URL 제어 정책 때문에 실행하지 못했다.
  사용자가 이미 열어 둔 로컬 미리보기에서 새 레이아웃을 직접 확인해야 한다.

### 보고용·상세 브랜치 도식 단일화

통합 위키의 `patch branch와 custom branch` 상세 화면에 별도로 만든 간이 도식을
제거했다. 상세 화면은
`OM_TEMP_검사운영위키_보고용.js`에 저장된 1차 보고용 원문에서
`.om-branch-visual`을 직접 읽어 Shadow DOM 안에 표시한다. 따라서 보고용 1차의
공식 새 버전, patch, 직전 custom, 병합·충돌 지점, 검사, 검증 tag와 다음 버전
Cycle이 상세 화면에도 같은 SVG로 표시된다. 그림 내용은 1차 정본에서 한 번만
관리하고, 상세 화면에는 설명 카드만 추가한다.

- 위키 inline JavaScript 문법 검사: 통과
- 보고용 데이터에서 `.om-branch-visual`과 Cycle 제목 확인: 통과
- 상세 화면의 보고용 파일·선택자 참조 확인: 통과
- 과거 별도 도식 DOM과 중복 HTML ID: 0개
- `git diff --check`: 통과
- 인앱 브라우저의 기존 `file://` 탭 새로고침은 URL 보안 정책이 차단했으므로
  이번 변경에서도 자동 시각 통과를 주장하지 않는다.

### 보고용·상세 위키 동일 개념 대조

보고용 1~5와 연결된 상세 위키를 개념별로 다시 대조해 아래 불일치를
현행화했다.

- 보고용 2차에는 있었지만 상세 위키에 없던 `T25-R` 페이지를 추가했다.
  현재 OM_TEMP는 공식 Git 이력을 보존하므로 T25-R이 아니라 T25를 사용한다는
  적용 조건도 함께 적었다.
- OM_TEMP 1.13.0 등록 검사 후보 `63820f…`와 1.13.1 커밋별 재적용 진단 후보
  `dee330ebd5…`를 분리했다. 실제 vendor-merge 후보는 아직 없다고 명시했다.
- 1.13.1 결과의 `integration_strategy: vendor-merge` 값과 실제 커밋별 재적용
  과정이 다르므로, 현재 Candidate lock을 vendor-merge 완료 증거로 사용하지
  않도록 Candidate lock 상세에도 경고를 추가했다.
- 현재 흐름은 `easyseop/OM_TEMP`와 `easyseop/openmetadata-test` 두 저장소를
  사용하고, `easyseop/OpenMetadata`는 과거 사례 참고용이라는 계층으로
  통일했다.
- T40은 미등록 변경·필수 변경 누락은 BLOCK, 실제 변경이 없는 비필수 등록
  경로는 APPROVAL이라는 판정을 보고용 표와 상세 설명에서 같게 맞췄다.
- T41 현재 OM_TEMP 결과는 migration watched 경로가 `visibility_only` 정책으로
  PASS였음을 상세 결과 예시에 반영했다.
- Candidate lock의 `artifact_digest`는 소스 검사 단계에서는 source tree 내용
  확인값이고, Runtime·배포 단계에서는 실제 이미지·패키지 digest여야 한다는
  단계 차이를 명시했다.
- 과거 참고 부록에서 현재 OM_TEMP 결과를 “다음 5번”이라고 가리키던 잘못된
  안내를 앞의 4번 업그레이드 연습으로 수정했다.

### JSON 충돌 보조 도구의 stage·실행 결과 명확화

통합 위키와 1.13.0→1.13.1 업그레이드 가이드에서 Git stage와 보조 도구의
실제 결과를 아래 기준으로 통일했다.

- `stage 1 · BASE`: 두 변경이 갈라지기 전 공통 기준
- `stage 2 · OURS`: 현재 checkout한 branch의 내용
- `stage 3 · THEIRS`: 지금 적용 중인 반대편 변경

이번 연습은 공식 1.13.1 branch에서 BANK-OM commit을 cherry-pick했으므로
`stage 2=공식 1.13.1`, `stage 3=BANK-OM`이다. 이 대응은 Git의 고정 규칙이
아니며 merge 방향이 바뀌면 공식/BANK-OM 위치도 바뀔 수 있다. stage 숫자는
실행 순서가 아니라 충돌 파일에 저장된 세 버전 번호이다.

`resolve_nonoverlapping_json_conflicts.py` 성공 후 상태도 구분했다.

1. 작업 폴더 JSON은 stage 2를 바탕으로 겹치지 않는 stage 3 변경을 반영한
   깨끗한 JSON으로 바뀐다.
2. 터미널에는 파일별 `BANK-OM leaf changes=<수>`가 출력된다.
3. Git index는 `git add` 전까지 `UU`인 충돌 미해결 상태다.
4. 별도 결과 보고서·승인 파일·`plan.json`은 생성하지 않는다.
5. test, `git add`, commit, `cherry-pick --continue`는 담당자가 확인 후
   실행한다.

도구는 JSON 외 충돌이 있거나 양쪽이 같은 최종 JSON 항목을 변경했다면 계획한
JSON을 쓰기 전에 중단한다. 통합 위키에 성공 출력, `UU` 상태, 동일 항목 겹침
실패 출력, JSON 외 충돌 실패 출력을 각각 추가했다.

후속 명확화에서 “읽는 세 코드, 비교 조건과 중단 조건”이라는 축약 문구도
제거했다. 현재 문서는 같은 충돌 파일의 BASE·OURS·THEIRS 세 버전,
`BASE→OURS`와 `BASE→THEIRS`의 최종 JSON 항목 목록, 두 목록의 교집합을
차례대로 보여준다. 같은 항목을 양쪽이 변경했다면 최종 값이 같아도 자동
중단한다는 실제 구현 조건과 JSON 외 충돌·JSON 파싱 실패의 중단 시점도
명시했다.

### 상세 위키의 운영 사례와 보조 도구 후속 조치

상세 주제 하단의 “언제 문서를 갱신하는가”라는 작성자 중심 제목을 제거하고
“운영 중 언제 무엇을 갱신하고, 언제 그대로 두는가”로 바꿨다. 11개 상세
주제마다 다음 네 열의 운영 사례를 추가했다.

1. 실제 운영 상황
2. 갱신 여부
3. 담당자의 실제 대응
4. 재실행하거나 보관할 검사·증거

각 표에는 변경이 없을 때 그대로 유지하는 사례, 부분 갱신 사례, 구조를 새로
만들어야 하는 사례를 포함했다. 따라서 단순히 “갱신한다”는 지시만 남지 않는다.

충돌 보조 도구 상세에는 목적과 결과별 조치 표도 추가했다. 보조 도구의 목적은
Git이 큰 JSON 구간을 충돌로 표시했을 때 BASE→OURS와 BASE→THEIRS의 실제 JSON
항목 변경을 계산해 해결 파일 초안을 만드는 것이며, 업무 값을 자동 승인하는
것이 아니다. `resolved`, `UU`, `overlapping leaf changes`,
`unresolved non-JSON conflicts`, test 실패별로 정확한 뜻, 바로 할 일과 금지
행동을 구분했다.

### 보고용 1~5를 위키 템플릿으로 재구성

통합 위키의 `보고용 요약`은 더 이상 기존 standalone HTML을 iframe으로
통째로 삽입하지 않는다. 기존 보고서의 대형 gradient hero, 카드 외곽,
페이지 이동 UI와 자체 폰트는 제거하고 다음 위키 공통 구조로 다시 작성했다.

1. 이 장이 답하는 질문
2. 한 문단 답변
3. 보고에 필요한 핵심 개념 세 가지
4. 업무 흐름
5. 현재 확인 완료·부분 확인·미확인 상태
6. 다음 단계
7. 같은 내용을 자세히 설명하는 위키 하위 페이지 링크

보고용 1~5의 내용은 상세 위키의 현재 정의와 맞췄다. 특히 1.13.1 결과는
커밋별 재적용 진단이며 실제 vendor-merge와 운영 배포는 미확인이라는 범위를
보고용 1차·4차·5차 모두에서 동일하게 표시한다. 기존 보고서 데이터는 상세
브랜치 페이지와 보고용 1차 요약에서 동일한 Cycle SVG 하나를 재사용하는
용도로만 남겨 두었다. 보고용 1차에는 그림 바로 위에 patch·custom 색상,
병합·충돌 지점, 검사·tag와 다음 버전 반복의 의미를 한 문단으로 설명한다.
