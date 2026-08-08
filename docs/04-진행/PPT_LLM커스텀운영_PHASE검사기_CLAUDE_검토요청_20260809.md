# PPT LLM 커스텀 운영 ↔ Phase 검사기 역할 분석 및 Claude 검토 요청

> 작성일: 2026-08-09 KST
>
> 검토 방식: 읽기 전용·적대적 검토
>
> 코드·PPT·저장소 파일을 수정하지 말 것

## 1. 검토 목적

사용자가 제공한 13장 PPT는 Claude를 이용해 OpenMetadata 커스터마이징 코드를
작성하고, 수기 Markdown으로 변경·test·버전 포팅 이력을 누적하는 운영 방식을
설명한다. 이 문서의 목적은 다음을 검토받는 것이다.

1. PPT가 설명하는 각 과정에 현재 Phase 검사기를 어디에 연결할 수 있는가?
2. 검사기가 이미 관리할 수 있는 것과 추가 개발이 필요한 것을 정확히 나누었는가?
3. LLM이 실행해도 되는 작업과, 담당자가 판단·승인해야 하는 작업의 경계가 올바른가?
4. PPT의 운영 방식을 검사기와 결합하면 어떤 구조로 개선해야 하는가?

## 2. 고정 입력과 현재 구현

### 2.1 PPT

- 원본: `/Users/seop/Downloads/오픈메타데이터럴~.pptx`
- 슬라이드: 13장
- SHA-256: `7320961cf39d4da1f18368bf8bd3d44a3593fac0d5be346c453d02aba0e7e628`
- PPT는 이 요청서 작성 과정에서 수정하지 않았다.
- PPT 내부의 파일명은 슬라이드 2의 `KB-CUST-NEW.md`와 슬라이드
  3~4의 `KB-CUSTOM-NEW.md`가 혼재한다. 이 요청서는 설명을 위해
  `KB-CUSTOM-*`으로 통일해 표기했으며, PPT 자체의 원문이 일치한다고
  주장하지 않는다.
- PPT의 실증 버전 라인은 1.12.8 → 1.12.13 → 1.13.1의 과거 회고이다.
  현재 Phase 검사기를 실제로 적용할 대상은 1.13.1 기준선 → 1.13.2
  목표 라인이다. 두 라인의 실행 증거를 섞어서 인용하면 안 된다.

### 2.2 검사기 저장소

- 위치: `/private/tmp/openmetadata-phase-fix-20260808`
- branch: `codex/phase-bundling-safety-fix-20260808`
- 현재 HEAD: `e2b445edbd057e611084f0194d8780b6683b0c5e`
- 최종 검사기 구현 commit:
  `6079aaff4d1b227df699d3f67262d60a96cd6b07`
- 문서 결속 commit:
  `e2b445edbd057e611084f0194d8780b6683b0c5e`
- 집중 회귀: `188 passed, 1 skipped`
- 전체 harness: `566 passed, 38 skipped`, 실패 0
- 검증 범위: 합성 Git 반례·검사기 자체 test
- 미수행: 실제 OM_TEMP 1.13.2 종단 vendor merge, 실제 build artifact,
  Runtime Contract, 조직 승인, 운영 배포

### 2.3 Claude가 먼저 확인할 파일

1. `docs/04-진행/CODEX_CURRENT_HANDOFF.md`
2. `harness/om_workflow.py`
3. `harness/acgh/phase.py`
4. `harness/acgh/registration_prep.py`
5. `harness/acgh/manifest.py`
6. `harness/acgh/candidate.py`
7. `harness/acgh/survival.py`
8. `harness/acgh/drift.py`
9. `harness/acgh/upgrade_watch.py`
10. `harness/acgh/structdiff.py`
11. `harness/acgh/zones.py`
12. `harness/acgh/debt.py`
13. `harness/tests/test_phase_cli.py`
14. `harness/tests/test_gitprim.py`
15. `harness/tests/test_registration_prep.py`

## 3. PPT가 제시하는 운영 과정

PPT의 업무 흐름은 크게 네 부분이다.

1. **LLM 코드 작업 규칙**
   - 버전·기능별 custom branch 생성
   - 기능 단위 commit
   - 신규 파일은 `KB-CUSTOM-NEW.md`, 기존 파일 수정은
     `KB-CUSTOM-MODIFIED.md`에 기록
2. **build·test·commit**
   - 일반 코드 오류는 Claude가 수정
   - 환경·인프라·DB·token·license 문제는 담당자에게 알리고 중단
   - `KB-CUSTOM-TEST.md` 14개 항목 통과 후 commit
3. **vendor 버전 포팅**
   - Vendor → Custom → KB Release 반복
   - 네이밍 충돌, 구조 리팩터링, 생성코드, Flyway,
     `parseSchemas.js`, build 툴체인, 임시 branch 리허설을 점검
   - `KB-CUSTOM-UPGRADE-CHECK.md`에 사전 판단과 실제 결과를 누적
4. **Claude skill로 반복 작업 자동화**
   - upgrade check, 14개 test, entity scaffold, artifact freshness,
     sample data 생성

PPT는 이 방식으로 버전 포팅 시간이 4~5시간에서 30분~1시간으로,
전체 작업 시간이 4~5시간에서 1~2시간으로 줄었다고 설명한다. 이 수치는
PPT의 기록이며 현재 Phase 검사기가 독립적으로 재계산하거나 입증하지 않는다.

## 4. 핵심 판단

PPT의 자동화는 **LLM이 코드를 작성·수정하는 작업 자동화**에 중점을
둔다. 현재 Phase 검사기는 **그 LLM 작업이 범위를 벗어나지 않았는지,
정확한 candidate와 test 결과가 결속됐는지, 사람 승인 없이 다음 단계로
넘어가지 않는지를 통제하는 작업 관리·검증 장치**에 중점을 둔다.

따라서 두 방식은 경쟁하는 기능이 아니라 다음처럼 연결할 수 있다.

```text
LLM이 코드·문서·vendor-merge Candidate를 작성
  → Phase 검사기가 Git 범위·SHA·lock·digest·test 증거를 검사
  → PASS만 자동 진행
  → APPROVAL은 사람에게 보고하고 정지
  → BLOCK·ANALYSIS_ERROR는 원인 해결 후 전체 재실행
```

## 5. PPT 과정별 검사기 역할

| PPT 과정 | 현재 검사기가 할 수 있는 일 | 현재 경계·남은 사람 판단 | 상태 |
|---|---|---|---|
| custom branch 생성 | branch 생성·이름 규칙은 직접 검사하지 않는다. 이후 선택된 candidate commit과 공식 base/target SHA를 lock으로 고정한다. | branch 생성·이름 규칙과 업무적 적절성 | 직접 미구현 |
| 기능 단위 commit | `Customization-ID` trailer, ID 중복·분산·scope 이탈 검사 | PPT commit 규칙에 trailer 필수를 추가해야 한다. 같은 기능의 후속 commit인지 새 ID인지는 담당자가 판단한다. | PPT 규칙 보완 후 연결 가능 |
| NEW/MODIFIED 목록 | Git diff로 `changed_paths`·commit inventory를 생성하고 Manifest·Registry 정합성 검사 | 새 파일이 `required_changed_paths`인지, Contract·watch·공유 책임이 바뀌는지 | 구현 |
| build 전 사전 확인 | preflight가 누락 입력·미실행 gate·다음 조치를 목록화 | 환경·network·license·비밀값 제공 | 구현 |
| 코드 실패 수정 | 수정 commit이 선언 scope를 벗어났는지, 후속 commit 후 재검사했는지 확인 | 어떤 코드 수정이 업무적으로 올바른지 | 구현 |
| 14개 test 실행 | Contract·required test 존재, 실행 결과, exit, candidate SHA·image digest를 결속하는 실행 기반은 있다. | PPT의 14개 항목별 Contract YAML·fixture·runner·실행 환경 매핑은 아직 없다. | 추가 개발 필요 |
| test 결과 누적 | run-id별 evidence, canonical result, 관리자 요약, 실무자 상세, digest 재검증 | 조직 보존 기간·권한·서명 정책 | 구현 |
| vendor 버전 선택 | 공식 tag·commit·로컬 branch를 `prep-official`로 결속 | 어떤 공식 버전으로 올릴지 결정 | 구현 |
| 버전업 사전 영향 검사 | `upgrade-watch`, `policy-drift`, `structdiff`, `watch-suggest`로 공식 변경·감시 경로·구조 변화 제시 | 변화가 업무 기능을 깨뜨리는지, watch 추가 여부 | 구현 |
| 임시 branch cherry-pick 리허설 | CandidateLock schema·patch-lock·T22 clean-room replay 개별 도구는 있지만, 현재 Phase postmerge 체인은 vendor-merge 전용이다. | PPT 흐름을 vendor-merge Candidate 생성으로 전환할지, 별도 patch-replay Phase를 개발할지 결정해야 한다. | 개별 도구만 존재·Phase 미연결 |
| vendor merge·충돌 해결 | merge-tree 재현과 자동 수집기로 충돌 경로·conflict-rate 결속, target·custom head·candidate 계보 검사 | 실제 merge 실행과 충돌 코드의 의미적 해결 | 검사 구현, 해결은 사람 |
| 병합 후 소스 검사 | vendor ancestry, customization survival, exact scope history, sensitive zones, debt, Manifest·Registry 검사 | `APPROVAL` 결과의 실무 영향 판단 | 구현 |
| build artifact 검사 | build-artifact lock과 artifact digest, candidate SHA를 대조하고 `artifact-verified` 범위로 구분 | 실제 build 실행, 신뢰할 수 있는 CI·image 제공 | 결속 구현, 실환경 입력 대기 |
| Runtime Contract | 필수 test를 실행하고 candidate·artifact·suite digest·exit를 결속 | 외부 DB·API·browser 환경과 업무 Contract 정의 | 실행기 구현, 실환경 입력 대기 |
| release·운영 배포 | `phase-status`로 저장된 결과 3종과 digest를 재검증하고 source-only의 배포 승인을 금지 | 승인자 실권한, 배포, rollback, 운영 관찰 | 일부 통제만 구현 |

## 6. PPT 6개 버전업 점검과 검사기 대응

| PPT 점검 | Phase 검사기 대응 | 판단 |
|---|---|---|
| 1. 네이밍 충돌 | add/add는 merge-tree 반례와 충돌 수집기가 검출한다. 병합 전 독립 신규 파일명 충돌 사전 판정은 명시적 gate가 아니다. | 부분 |
| 1-1. 구조적 리팩터링 | `upgrade-watch`로 감시 파일 변경을 찾고 `structdiff`로 JSON/YAML 구조 변화를 제시한다. Java/TS 클래스·함수 의미 변화는 build·test·사람 검토가 필요하다. | 조건부 |
| 2. 생성코드 재생성 | required path·exact scope는 누락을 찾을 수 있지만 스키마 생성기 재실행 후 의미가 올바른지는 해당 build·test가 필요하다. | 조건부 |
| 3. Flyway | sensitive zone·watch·구조 diff로 migration 변경을 검토 대상으로 올릴 수 있다. 실제 DB 체크섬·재기동·데이터 보존은 Runtime Contract가 필요하다. | 조건부 |
| 4. `parseSchemas.js` | watch path로 등록하면 upstream 변경을 `APPROVAL`로 올릴 수 있다. 실제 UI schema resolve는 build·test 대상이다. | 조건부 |
| 5. build 툴체인 | 의존성·설정 변화 감시와 실패 증거 결속은 가능하다. 실제 Node·Yarn·Maven·Docker 실행은 CI/build 환경이 필요하다. | 조건부 |
| 6. 리허설 | 실제 vendor merge Candidate를 만든 뒤 candidate lock·충돌 증거·postmerge 결과를 재현 검사한다. PPT의 cherry-pick 리허설과는 기본 전략이 다르다. | 구현되었지만 흐름 조정 필요 |

## 7. PPT 14개 test 항목과 검사기 연결

아래의 `조건부`는 검사 실행기가 존재하더라도 PPT가 말하는 실제 test를
Contract·CI·실행 환경으로 정의해야 한다는 뜻이다.

| # | PPT test | 연결 위치 | 현재 판단 |
|---:|---|---|---|
| 1 | Maven·TypeScript·lint build | source test, T63, build artifact | 조건부 |
| 2 | 화면 XHR 200 응답 | browser Runtime Contract | 조건부 |
| 3 | browser console·pageerror | browser Runtime Contract | 조건부 |
| 4 | 검색 결과 | API·browser Runtime Contract | 조건부 |
| 5 | Explore 카테고리 노출 | browser Runtime Contract | 조건부 |
| 6 | 기존·신규 기능 회귀 | Contract catalog·required tests | 구조 구현, test 보강 필요 |
| 7 | ingestion | Runtime Contract·차등 test | 실환경 필요 |
| 8 | CRUD·DB 연결 | API Runtime Contract | 조건부 |
| 9 | entity version history | API Runtime Contract | 조건부 |
| 10 | 무권한 401/403 | API Runtime Contract | 조건부 |
| 11 | server·worker log | Runtime/CI 검사 | 추가 Contract 필요 |
| 12 | locale JSON 파싱·정렬 | source test·declarative verifier | 연결 가능 |
| 13 | 재기동 후 healthy | deployment rehearsal Contract | 실환경 필요 |
| 14 | 배포 image·bundle 신선도 | T62, artifact digest, image revision | 결속 구현, 실제 artifact 필요 |

현재 1.13.1 기준선은 별도 Runtime Contract 9개를 실제로 통과했지만, 이는
PPT의 14개 항목 전부가 1.13.2 후보에서 검증됐다는 뜻이 아니다.

## 8. 판정 증거를 Markdown에서 관리할 때의 한계

PPT의 Markdown 4종은 사람이 이해하기 쉬운 설명 기록으로는 유용하다.
그러나 검사 통과 판정의 정본으로는 다음 제한이 있다.

| PPT 파일 | 유지할 용도 | 기계 판정 정본 |
|---|---|---|
| `KB-CUSTOM-NEW.md` | 신규 파일의 목적·배경 설명 | Manifest `changed_paths`, Git diff, commit inventory |
| `KB-CUSTOM-MODIFIED.md` | 수정 이유·해결 메모 | Manifest, `Customization-ID`, exact-scope history |
| `KB-CUSTOM-TEST.md` | 사람용 test 시나리오·해석 | Contract catalog, 실제 test 산출물, candidate·artifact·suite digest |
| `KB-CUSTOM-UPGRADE-CHECK.md` | 사전 예측과 실무자 판단 내역 | premerge·postmerge canonical result, approval, evidence digest |

권고는 Markdown을 삭제하는 것이 아니라, **설명·회고용 기록으로 유지하되
Git에서 생성한 Manifest·lock·evidence를 통과 판정의 정본으로 두는 것**이다.

## 9. LLM이 관리할 수 있는 작업과 금지 작업

### 9.1 LLM 실행·관리 가능

- 등록 변경 `plan` 생성
- Git commit·`changed_paths` 수집
- candidate 선택·공식 target 준비·preflight
- premerge·postmerge·source·Runtime 명령 실행. 단, Runtime에 필요한
  비밀값·외부 환경은 담당자가 준비한다.
- 충돌 증거 자동 수집기 실행
- `result.json`과 `phase-status` 재검증
- `PASS`만 다음 자동 단계로 진행한다. `APPROVAL`은 exit code 2를
  포함해 사람에게 보고하고 반드시 정지하며,
  `BLOCK`·`ANALYSIS_ERROR`는 중단·재실행
- candidate SHA·result digest·검사기 commit SHA를 포함한 결과 보고

### 9.2 LLM은 제안만, 담당자가 결정

- 후속 commit이 같은 BANK-OM ID인지 새 ID인지
- 새 파일이 `required_changed_paths`인지
- watch path·Contract·공유 코드 책임을 바꿀지
- 구조 변화가 실제 기능에 문제를 만드는지
- 충돌 코드의 의미적 해결이 올바른지
- `APPROVAL` 결과를 수용할지

### 9.3 LLM 금지

- 승인 파일·승인자·조직 권한 임의 생성
- 측정하지 않은 conflict-rate·test 성공·artifact digest 작성
- 자신의 작업을 통과시키기 위해 검사기 코드나 `layout`·`zones`·
  `thresholds`·Contract 정책 파일을 수정
- `APPROVAL`을 `PASS`로 해석
- `BLOCK`·`ANALYSIS_ERROR`를 승인으로 우회
- 후속 commit 후 예전 result·approval 재사용
- 이전 run-id나 기존 evidence 출력 경로를 새 실행에 재사용
- Markdown에 evidence digest 근거 없이 `✅ 성공`·`완료`를 기록
- 운영 비밀값·외부 환경값 추측
- 사람 확인 없이 release·운영 배포

## 10. 통합하면 권고하는 실행 흐름

| 순서 | 실행 주체 | 작업 | 결과·중단 기준 |
|---:|---|---|---|
| 1 | LLM + 담당자 | 기능 단위 commit과 `Customization-ID` 준비 | ID·업무 의미는 담당자 확정 |
| 2 | LLM | `plan → approval-template` 실행 | 필수·watch·Contract 질문이 있으면 정지 |
| 3 | 담당자 | proposal·필수 경로·Contract·승인 확정 | 승인 없이 `apply` 금지 |
| 4 | LLM | `apply → validate → source` 실행 | 실패나 범위 이탈은 중단 |
| 5 | LLM | `candidate-select → prep-official → phase-preflight(premerge) → premerge-check` | `APPROVAL`은 담당자 검토 대기 |
| 6 | 담당자 + LLM 보조 | 별도 제품 branch에서 vendor merge·충돌 해결·commit | 사람이 해결 의미 검토 |
| 7 | 담당자 + LLM | 새 Candidate lock 승인·활성화, `candidate-select` 재실행 | 이전 evidence·approval 재사용 금지 |
| 8 | LLM | `collect-conflict-evidence → phase-preflight(postmerge) → postmerge-check → phase-status` | source-only는 운영 배포 금지 |
| 9 | CI + LLM | build artifact·Runtime Contract 실행 후 artifact-verified postmerge 재실행 | 실패·skip·불일치는 중단 |
| 10 | 승인자·운영자 | result digest 승인, 별도 배포·rollback 절차 | 검사기는 조직 실권한을 대체하지 않음 |

## 11. PPT에서 바로 고쳐야 할 가능성이 큰 표현

Claude는 아래 항목이 실제로 오도 가능성이 있는지 판정해 달라.

1. **“크리티컬 오류 발생 가능성은 X”**
   - 실제로는 환경·DB·license·network·migration·승인 오류가 발생할 수 있으므로
     “자동 해결 금지·담당자 조치 필요”로 바꾸는 편이 정확해 보인다.
2. **“일반 오류는 Claude 자동 해결”**
   - 자동 수정 후에도 새 commit·새 candidate에 대한 전체 검사가 필요하다.
   - 민감 경로·DB migration·인증·권한 변경은 일반 오류로 분류하면 안 된다.
   - 특히 PPT 슬라이드 9의 Flyway “Claude 자동 수정 가능”은
     “담당자 판단, LLM은 원인 분석·수정안 제안만”으로 바꾸어야 한다.
3. **“test 전부 통과 = commit 확정”**
   - commit 가능 여부와 release·배포 가능 여부를 분리해야 한다.
   - test 통과 후 commit할 수는 있지만, candidate·artifact·승인 결속 전에는
     배포 가능 판정이 아니다.
4. **“리허설 충돌 0건이면 바로 진행”**
   - text 충돌이 없어도 upstream 의미 변경·생성코드·migration·Runtime 회귀가 남는다.
5. **“실제 결과: 가능”**
   - PPT 자체가 Playwright 미실시·codegen 비호환 미해결을 기록하므로,
     `PASS`가 아니라 `incomplete`·`APPROVAL`·`BLOCK` 중 어떤 표현이 정확한지 검토가 필요하다.
6. **“누적 Markdown이 검증 결과”**
   - Markdown은 어떤 candidate·artifact·test suite에서 나온 결과인지 자동으로
     증명하지 못한다. 이를 표시용 기록으로 남기고 digest 결속 evidence를
     판정 정본으로 사용하는 방향이 적절한지 확인이 필요하다.

## 12. Claude 필수 검토 질문

다음 질문에 모두 답해 달라.

1. 이 문서가 PPT 13장의 목적·작업 흐름·위험을 정확히 요약했는가?
2. PPT 과정별 검사기 역할 매핑 중 실제 코드보다 과장된 항목이 있는가?
3. “구현”·“조건부 구현”·“실환경 입력 대기” 구분이 정확한가?
4. PPT의 `KB-CUSTOM-NEW/MODIFIED/TEST/UPGRADE-CHECK.md`를 설명·회고용으로
   남기고, Manifest·Candidate lock·digest evidence를 판정 정본으로 두는 권고가 타당한가?
5. PPT의 custom branch·cherry-pick 반복 전략과 현재 기본 vendor-merge 전략 사이에
   추가로 조정해야 할 부분이 있는가?
6. 6개 버전업 점검 매핑에서 현재 gate가 놓치는 중요 실패 유형은 무엇인가?
7. 14개 test를 source·build·API·browser·DB·deployment 계층으로 나눈 현재 분류가 적절한가?
8. PPT 14개를 실제 Phase 완료 조건으로 사용하려면 추가해야 할 Contract·runner·evidence는 무엇인가?
9. LLM 실행·제안·금지 경계가 충분한가? LLM이 조작·생략·과장할 수 있는
   추가 경로가 있는가?
10. `PASS`·`APPROVAL`·`BLOCK`·`ANALYSIS_ERROR`를 PPT 각 단계에 어떻게 배치해야 하는가?
11. 후속 commit·required path·watch path·Contract를 사람이 판단하는 구조에
    독립 검증이 부족한 곳은 어디인가?
12. 현재 conflict evidence 자동 수집기와 rename·merge-driver 정책이 PPT의
    “충돌 성격 분류”까지 충분히 지원하는가, 아니면 단순 충돌 경로 재현에 그치는가?
13. build artifact·Runtime Contract·release 경계를 더 엄격하게 분리해야 하는가?
14. PPT의 “60~70% 시간 단축”·“70% 재작업 감소”를 검사기 결과와 함께 보여주려면
    어떤 측정·감사 데이터가 추가로 필요한가?
15. 현재 구현에 P0·P1·P2로 분류할 추가 개선점이 있는가?
16. 최종적으로 이 PPT 운영 방식에 Phase 검사기를 어느 범위까지 적용할 것인가?

## 13. Claude 응답 형식

1. **사실 확인**
   - PPT 요약과 구현 commit 대조 결과
2. **P0**
   - 배포·승인 판단에 바로 오용될 수 있는 문제
3. **P1**
   - 통합 전 반드시 보완해야 하는 문제
4. **P2**
   - 문서·편의·재현성 개선
5. **PPT 과정별 권고**
   - 현재 검사기 연결 / 추가 개발 / 사람 전용을 표로 제시
6. **LLM 운영 규칙 수정안**
   - 실행·제안·금지 목록의 수정 필요 여부
7. **추가 반례 test**
   - 각 문제를 재현하는 구체적 test 시나리오
8. **최종 판정**
   - `즉시 채택 / 수정 후 채택 / 부분 채택 / 폐기` 중 하나

단순한 의견보다 파일·함수·test·실행 반례 근거를 우선해 달라. 코드나
문서는 수정하지 말고, 읽기 전용 검토 결과만 제출해 달라.
