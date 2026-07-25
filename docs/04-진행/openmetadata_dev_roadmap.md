# 개발 로드맵 & 커버리지 맵

> **2026-07-25 변경:** [`ADR-001`](../02-설계/ADR-001-vendor-merge-default.md)이
> 통합 전략의 정본이다. 현재 replay 기반 MVP1 구현은 선택 모드로 재분류되며,
> T24~T29·T25-R 기본 경로와 실제 7개 등록부, 잔여 Docker-free 운영 게이트까지
> 구현됐다. 실제 113경로 source plan과 44개 shared owner 분석, 7-ID vendor
> candidate 생성과 T25-R/T25/T26/T30/T31 검증까지 완료했다. contract/upgrade
> test와 승격·반입 증거가 없으므로
> Production-upgrade 달성으로 표기하지 않는다.

> **이 문서의 용도**
> "무엇을 · 어떤 순서로 만들고, 각 MVP를 완성하면 **어디까지 커버되는지**"를
> 추적하는 진행 기준. 상세 구현 스펙은 `openmetadata_build_plan.md`(+ SRS 부칙 A),
> 검증기 상세는 `openmetadata_verifier_catalog.md`가 정본이다.
>
> 이 문서는 **커버리지 렌즈** — 태스크를 완료할 때마다 여기서 "이제 무엇을
> 보장할 수 있는가"를 갱신한다.

---

## 0. 추천 착수 순서

**결론: vendor-merge Candidate-control을 목표로, 의존성 순서로 쌓는다.** MVP 순서와
"추천"은 충돌하지 않는다 — MVP는 커버리지 이정표, 빌드는 의존성 순서이며,
MVP1을 향해 의존성 순으로 진행하면 자동으로 정렬된다.

**지금 병행 착수 (서로 독립):**
- **T12** git 프리미티브 · **T13** verdict 엔진 — 코드. 부칙 A의 severity
  rank·canonical digest 계약을 그대로 구현. 다른 무엇에도 의존하지 않음.
- **T05** path-ownership·glob 문법 정본 — 문서(정책). 실제 OpenMetadata 소스의
  디렉터리 구조를 근거로 작성. T10·T30·T40·T93의 의미를 고정하는 전제.

**핵심 경로 (2차 검토 권장):**
```
T01~T05
   ↓
T10 · T12 · T13 · T15 · T14 · T11        (M1 기반)
   ↓
T30 · T31                                 (M1.5 source preflight)
   ↓
T24 · T25 · T26 · T29                     (M2 vendor merge 기본)
   ├── T27                                (충돌 증거)
   └── T28 → T20 · T21 · T22             (선택 replay)
   ↓
T40 · T62 · T32 · T41                     (M3 완전성·결속)
   ↓
T93 → T42 + T50                           (M4 감시·영향·verifier)
   ↓
T60 · T61(high/critical)                  (M6 테스트 결속)
   ↓
T70 · T72                                 (M7 정책)
   ↓
T90 → T91 → T94                           (M9 릴리스·반입)

T51·T52 병행 보강 · T80·T81 마지막
```

**동결 규칙**: T10(스키마)·T11(patch-lock)은 SRS 부칙 A(결과 계약·lock 모델·
path 문법)를 반영한 뒤 동결. T12·T13은 즉시 진행 가능.

---

## 1. 테스트 정책 (전역) — OpenMetadata 오픈소스 기반

> **모든 픽스처·통합·업그레이드 테스트는 실제 OpenMetadata 오픈소스로 진행한다.**
> 합성 더미 저장소가 아니라 진짜 OM 소스 위에서 검증한다.

1. **업스트림 미러 확보**: `open-metadata/OpenMetadata`를 미러로 받아,
   **두 개의 고정 태그**(예: `1.5.x` = UPSTREAM_A, `1.6.x` = UPSTREAM_B)를
   테스트 기준으로 삼는다. (실제 개발 착수 시 세션에 add_repo로 편입)
2. **픽스처 = 실제 경로 + 합성 패치**: BANK-OM 패치는 OM의 **실제 파일 경로**
   (예: `openmetadata-service/.../AuthenticationFilter.java`) 위에 얹는다.
   경로·모듈 구조가 진짜여야 T05 path-ownership·T40 drift·T93 glob이 유효하다.
3. **케이스 A~E 재현**: A(무관 변경)·B(다른 줄)·C(같은 줄 충돌)·D(의존 대상
   변경)·E(깊은 의존)를 UPSTREAM_A→B 실제 diff에서 골라 픽스처로 구성.
   가능하면 OM이 실제로 바꾼 변경(예: 응답 필드 구조 변경)을 케이스 D·E로 사용.
4. **업그레이드 테스트(M9)는 실제 OM 스택**: 실제 OM Docker·DB 마이그레이션·
   재색인·Ingestion으로 구·신 버전 차등 테스트를 수행한다.
5. **결정성 검증**: 동일 입력 3회 → canonical payload digest 일치(부칙 A-1.3),
   실행 시각·worktree 경로 등 관측 메타데이터는 digest 대상 밖.

> 개발 착수 시 첫 작업: **OpenMetadata 미러를 세션에 편입**하고 A/B 태그 고정.

---

## 2. 태스크별 목적 (상세)

### M0 — 사전 셋팅 (정책·명세 저작)
- **T01 인벤토리 추출·분류** — 현재 행내 변경을 전수 추출해 config/deployment/
  extension/core로 분류하고 목적 불명 변경을 식별. *왜*: 무엇을 통제 대상으로
  삼을지 정하지 않으면 이후 전부가 허공에 뜬다.
- **T02 ID series 재구성** — 코어 변경을 `BANK-OM-xxx` 이름표 커밋 series로 분해.
  *왜*: "셀 수 있어야" 누락을 검증한다. 셈의 단위를 만드는 작업.
- **T03 민감·라우팅·임계치 저작** — 민감 경로 지도·승인자·부채 상한. *왜*:
  위험 변경을 사람에게 올리는 기준을 미리 정의.
- **T04 명세·테스트·contract 초안** — ID별 명세와 업무 불변식. *왜*: 게이트가
  판정할 대상(선언)을 만든다.
- **T05 🆕 path-ownership·glob 문법 정본** — upstream/행내/확장 경로 소유 지도 +
  경로 문법 고정(정규화·부정 패턴·symlink 정책). *왜*: 여러 게이트가 **같은
  파일 집합**을 판정하게 하는 전제. 없으면 게이트마다 다른 답을 낸다.

### M1 — 기반
- **T12 git 프리미티브** — trailer 파싱·`-z` 출력·커밋 경계 유지·환경 고정.
  *왜*: 모든 게이트의 결정적 입력 계층. 집합 축약으로 ID 없는 커밋을 놓치지
  않게 하는 토대.
- **T13 verdict 엔진** — severity rank 집계·analysis_error=차단·exit 변환.
  *왜*: 차단이 승인으로 격하되거나 검사 고장을 승인으로 우회하는 것을 막는 판정 코어.
- **T15 🆕 result/CI adapter** — 원자적 결과 생성·canonical digest·exit/result
  불일치=analysis_error·attestation 분리·다중 저장소 입력 결속. *왜*: 판정이
  CI 경계에서 붕괴(stale·불일치·set -e 단락)되는 것을 막는다.
- **T14 감사카드** — 게이트·증거·LLM 산출을 한 카드로 집계. *왜*: 사람이
  위험 변경만 정독하게 하는 산출물.
- **T10 명세 스키마** — allowed/required_changed_paths·upgrade_watch·assurance,
  구버전 필드 거부. *왜*: 구현 범위와 감시 범위를 분리(P0-6)해 drift 오탐·감시
  협소를 동시에 막는다.
- **T11 patch-lock** — source lock(불변 입력)/application lock(결과) 분리·lineage
  mapping. *왜*: 재적용 소스를 고정 SHA로 잠가 재현성을 확보하고, 정본이
  실행 중 흔들리지 않게 한다.

### M1.5 — source stack preflight
- **T30 커밋 불변식** — 1커밋=1ID·merge/empty 금지·core+governance 분리 등 7종.
  *왜*: 셈이 무너지는 원인(이름표 없는 코어 커밋·뭉치기)을 재적용 **전에** 차단.
- **T31 ID·series 불변식** — 순서·개수·의존 순서·retired 재사용. *왜*: 한 수정의
  절반만 반영되는 것을 차단.

### M2 — 재적용
- **T20 탐지 모드** — 임시 worktree 재적용·상태 7종 분류·본 트리 오염 0. *왜*:
  충돌 유무를 안전하게 확인. non-zero를 전부 충돌로 오분류하지 않음.
- **T21 해결 모드** — 충돌 유지·`--continue`·trailer 자동 각인·lock 리비전 고정.
  *왜*: 사람이 실제로 해결할 작업 공간을 주고 결과를 재현 가능하게 고정.
- **T23 🆕 resolve 직렬화** — 단일 integrator·base_lock_digest CAS. *왜*: 병렬
  해결이 lock을 덮어쓰거나 낡은 predecessor에서 해결되는 경합을 막는다.
- **T22 clean-room replay** — 재생 tree == candidate tree(source tree 범위). *왜*:
  검증받지 않은 은밀한 변경이 섞이지 않았음을 증명.

### M3 — 완전성·결속
- **T40 구현범위 drift** — touched(상한)/net(하한) 분리, upgrade_watch 제외.
  *왜*: 명세와 실제가 어긋나 뒤의 분석이 무력화되는 것을 막는다.
- **T62 테스트-SHA 결속** — 테스트 실행 **전에** candidate SHA·digest 결속,
  retry-pass 구분. *왜*: 옛 테스트 결과를 유효로 착각하거나 flaky를 성공으로
  뭉개는 것을 막는다.
- **T32 최종상태 불변식** — 순효과 0(intrinsic + counterfactual 2단)·무단 revert.
  *왜*: "이름표는 있는데 기능은 사라진" 상태를 잡는다.
- **T33 게이트 문구 정정** — 등록·재적용 ≠ 기능 완전성 표기. *왜*: 보장 범위
  과장을 산출물에서 제거.
- **T41 민감·의도 게이트** — frozen/protected/watched·범위 이탈·fail-closed. *왜*:
  위험 변경이 검토 없이 통과하는 것을 막는다.

### M4 — 감시·영향
- **T93 감시경로 drift** — glob 0-매칭·급감·미분류 모듈 검출(T42보다 먼저). *왜*:
  정책이 "빈 총"이 된 걸 모른 채 통과만 뜨는 것을 막는다.
- **T42 영향분석** — upgrade_watch ∩ 업스트림 변경 → 검토 플래그. *왜*: 우리가
  편집 안 한 의존 대상(tenant) 변경을 케이스 D로 잡는다.
- **T50a/b 선언형 verifier** — 타입 세트(sandbox 필수)·evaluator/게이트 통합 분리.
  *왜*: 설정·확장 반영을 검증하되 임의 코드 실행 통로를 봉쇄.

### M5 — 증거 생성기
- **T51 구조화 diff(API/schema)** — OpenAPI·JSON Schema diff. *왜*: 의미 변경의
  근거를 LLM보다 먼저 결정적으로 확보.
- **T52 구조화 diff(Helm/DB/dep/search)** + provider 자기보호. *왜*: 비코드 변경
  근거 확보 + 증거 생성기 자체의 위·변조 방지(C-3).

### M6 — 테스트 결속
- **T60 contract 결속** — contract catalog가 업무 불변식↔테스트 단일 정본. *왜*:
  "어떤 업무 규칙이 지켜지는지"를 이름 확인이 아니라 결속으로 보장.
- **T61 patch-kill** — high/critical 우선·상태 4종(killed/survived/inconclusive/
  infra_error). *왜*: 테스트가 커스터마이징 생존을 실제로 입증하는지 검증(껍데기
  테스트 방지).

### M7 — 정책·운영
- **T70 정책 base-평가** — policy PR을 base 정책으로 판정·attestation 분리. *왜*:
  완화된 정책으로 자기 자신을 통과시키는 우회 차단.
- **T71 fast lane** — 변경 유형별 경량 경로. *왜*: config 한 줄이 전체 게이트를
  타지 않게 해 우회 유인을 없앤다.
- **T72 break-glass** — 원 verdict 보존·범위·만료·사후 재검증. *왜*: 긴급 예외의
  공식 경로가 없으면 사용자가 도구 밖으로 나간다.

### M8 — LLM (보조)
- **T80 Impact Memo** — 읽기 전용·근거 첨부·pass 권한 없음. *왜*: 충돌 없는
  의미 변경(케이스 D)을 사람이 놓치기 전에 검토건으로 좁힘.
- **T81 Memo 지표** — recall·false positive·채택률. *왜*: 위키 확장 판단 데이터.

### M9 — 릴리스·반입
- **T90 업그레이드 테스트** — DB 복원·migration·재색인·**구/신 차등 테스트**.
  *왜*: 빌드 성공 ≠ 업그레이드 성공. 관계·의미 손상을 실측으로 잡는다.
- **T92 retirement** — 업스트림 흡수 패치 제거 흐름. *왜*: 빈 패치를 강제 유지하지
  않고 공식 대체로 전환.
- **T91 digest 승격** — 검증된 동일 commit·digest만 승격, 재빌드 금지. *왜*:
  검증본과 다른 산출물이 배포되는 것을 막는다.
- **T94 내부망 반입·재검증** — bundle·해시·서명·내부 재검증. *왜*: 외부망 =
  내부망 산출물 동일성 증명.

---

## 3. MVP별 커버리지 (완성 시 무엇이 충족되나)

> 문제(P1~P7)는 설계서 1장, 케이스(A~E)는 검증기 카탈로그, 검증기 계층(1~4)도
> 카탈로그 기준.

### ▸ MVP0 — 기반 (M0 + M1 완성)
**충족**: 판정 **인프라**만. 게이트 로직은 아직 없음.
- 결정적 판정 틀(verdict 4상태·result 계약·감사카드), 결정적 git 접근,
  스키마·patch-lock·path 문법 정본.
- **커버 문제**: 없음(직접적). 단 P7(결정성)·보안 경계의 **토대**를 놓음.
- **아직 못 함**: 누락·범위·의미 어느 것도 판정 못 함(로직 미구현).
- **말할 수 있는 것**: "판정할 수 있는 결정적 틀과 소스 고정 체계가 섰다."

### ▸ MVP1 — Candidate-control (candidate를 기계적으로 통제)
**포함**: T01~T05 · T10~T15 · T30·T31 · T20~T23 · T40·T41·T62·T32·T33 ·
T93·T42 · T50 · T70 최소.

**커버되는 문제**:
- ✅ **P1 (누락)** — 등록·재적용 완전성으로. *단 "등록·재적용" 범위* (기능 생존은
  T32가 부분 보강, 확정은 MVP2).
- ✅ **P3 (추적)** — ID·명세·trailer로 "무엇을 왜 바꿨나" 추적.
- ✅ **P6 (담당·목적)** — 명세 owner·retirement.
- ✅ **P7 (결정적 판정)** — LLM 불개입 결정적 게이트.

**커버되는 케이스**:
- ✅ A(무관 판정) · B(자동 적용) · C(충돌 탐지·해결)
- ◐ D(의존 대상 변경) — **플래그·검토건까지**(upgrade_watch + verifier + Memo).
  *영향의 확정은 테스트라 MVP2*.

**커버되는 검증기**:
- ✅ 계층 1 전부(재적용·커밋/ID/최종상태 불변식·replay·drift·민감·경로drift·
  upgrade_watch·부채·patch-lock)
- ✅ 계층 2(선언형 verifier·구조화 diff는 T51/52 병행분까지)
- ◐ 계층 4(verdict 엔진·정책 base-평가 최소; digest 승격은 MVP2)

**아직 못 함**:
- ✗ **기능 의미 확정** — 테스트 결속(T60/61) 없음. 케이스 E 방어 없음.
- ✗ 실제 업그레이드 동작(DB·migration·재색인)
- ✗ 릴리스 승격·내부망 반입

**상급자에게 말할 수 있는 것**:
> "candidate가 규칙대로·누락 없이·재현 가능하게 만들어졌음을 CI가 결정적으로
> 보장합니다. 위험 변경은 승인 대상으로 자동 분류됩니다. 다만 **기능이 실제로
> 동작하는지, 운영 배포가 가능한지는 아직**입니다."

### ▸ MVP2 — Production-upgrade (운영 릴리스·반입까지 통제)
**추가 포함**: T60 · T61(high/critical) · T72 · T90 · T91 · T94 · T92(해당 시).

**추가로 커버되는 문제**:
- ✅ **P2 (논리 동작)** — contract·테스트·patch-kill로 동작 확정.
- ✅ **P5 (전 계층 호환성)** — 업그레이드 테스트(DB·검색·ingestion·인증 차등).
- ✅ **P4 (반입 동일성)** — digest 승격 + 내부망 재검증.

**추가로 커버되는 케이스**:
- ✅ D 확정 — 테스트가 의존 변경의 실제 영향을 확정.
- ✅ **E (깊은 의존·의미 붕괴)** — patch-kill·contract·차등 테스트가 최종 안전망.

**추가로 커버되는 검증기**:
- ✅ 계층 3 전부(필수테스트·contract·patch-kill·SHA결속·차등)
- ✅ 계층 4 완성(digest 승격)

**여전히 잔여 위험 (정직하게)**:
- 테스트에 아직 없는 **미지의 의미 차원**(케이스 E의 문서화 안 된 내부 변경) —
  릴리스 노트 리뷰·도메인 검토·운영 관찰로 관리하는 잔여 위험. 100% 자동 보장 아님.

**상급자에게 말할 수 있는 것**:
> "업그레이드가 실제로 동작하고(테스트), 검증한 그대로 배포되며(digest),
> 내부망에서 동일하게 재현됨을 보장합니다. 상급자 원 질문('벤더/패치 스택이
> 잘 도는지 검증')에 **CI 통과 여부로 증명**한다고 답할 수 있습니다.
> 단 충돌 없는 미지의 의미 변경은 잔여 위험으로 관리합니다."

### ▸ 이후 보강 (MVP 밖)
- T43 hard-block 임계치(2~3회 데이터 후) · T51/52 전체 범용화 · T71 완전판 ·
  T80/81 LLM 위키 확장 · low/medium 상시 patch-kill.

---

## 4. 진행 체크리스트 (완료 시 켜지는 커버리지)

| 마일스톤 | 태스크 | 완료 시 켜지는 것 |
|---|---|---|
| M0 | T01·T02·T03·T04·T05 | 판정 대상(명세·경로 정본) 존재 |
| M1 | T12·T13·T15·T14·T10·T11 | 결정적 판정 틀·소스 고정 |
| M1.5 | T30·T31 | 커밋/ID 불변식(셈의 신뢰) |
| M2 | T20·T21·T23·T22 | 재적용·충돌 흐름·재현성 |
| M3 | T40·T62·T32·T33·T41 | 범위·최종상태·민감 통제 → **케이스 A·B·C 커버** |
| M4 | T93·T42·T50 | 감시·의존 영향·설정 검증 → **케이스 D 플래그** · **MVP1 완성** |
| M6 | T60·T61 | 동작·생존 입증 → **케이스 E 커버** |
| M7 | T70·T72 | 자기보호·긴급 경로 |
| M9 | T90·T91·T94·T92 | 업그레이드 동작·동일 승격·반입 → **MVP2 완성** |
| 보강 | T51·T52·T71·T80·T81·T43 | 정밀도·효율·LLM |

> 이 표를 **진행 추적**에 쓴다. 마일스톤을 완료할 때마다 "켜지는 것" 열이
> 현재 커버리지다.

### 4.1 태스크 단위 완료 로그

마일스톤 표는 커버리지 지도이고, 아래는 개별 태스크의 실제 완료 현황이다.

| 태스크 | 상태 | 산출물 | 검증 |
|---|---|---|---|
| T25-R snapshot→vendor 재구성 | ✅ 실제 branch·candidate 통과 | `acgh/vendor_rebuild.py` + `shared-path-owners.yaml` + `source-candidate-evidence.yaml` | 13 단위 테스트 + 실제 candidate `e1ffc5a1...`. 113경로=67 단독·44 공유·2 제외, target ancestry·snapshot commit 비포함·7 ID/path owner·JSON 의미/기타 content 동일성 통과 |
| T26 customization survival | ✅ 구현 | `acgh/survival.py` | 7 테스트. required path 존재·target 대비 순효과·registry/manifest/contract/effective test 생존, stale 객체=analysis_error |
| T27 merge conflict evidence | ✅ 구현 | `acgh/conflicts.py` + schema | 5 테스트. `ls-files -u -z` stage 1/2/3, 해결 blob/rationale/승인/candidate-lock 결속 |
| T28 통합전략 라우팅 | ✅ 구현 | `acgh/routing.py` | 4 테스트. vendor/replay gate 분리, 필수 gate 미구성=analysis_error |
| T29 실제 7개 등록 | ✅ 등록·⚠ 운영미완 | `registrations/kb-openmetadata/` + `acgh/registry.py` | 5 테스트. 실제 113경로 전수목록, 111경로→7ID·7contract, 2개 비제품 변경 명시 차단. ancestry=false·owner pending·실제 test 미구현 |
| T25 vendor ancestry gate | ✅ 완료 | `acgh/ancestry.py` + `gitprim.py` | 6 테스트. base/target 공통 조상, locked base·approved target의 candidate 포함 검증, topology 위반=block, 객체 누락·stale tree·모드 오라우팅=analysis_error |
| T24 integration strategy·candidate-lock | ✅ 완료 | `acgh/candidate.py` + `schema/candidate-lock.schema.json` + `binding.py` | 9 테스트. 기본 `vendor-merge`, patch-replay lock 필수화, base/target/candidate commit·tree·artifact digest 고정, 결과 입력 결속·stale 무효화 |
| T05 path-ownership·glob 정본 | ✅ 완료 | `policies/repository-layout.yaml` + **운영층** `acgh/layout.py` | 실제 OM 모듈 루트로 검증, `upstream_base_sha` 결속, 모든 게이트 공용 문법(부칙 A-3.1), pathspec factory=`gitignore` 고정 |
| T12 git 프리미티브 | ✅ 완료 | `harness/acgh/gitprim.py` | 4 테스트 통과(ID-less 커밋 보존 P0-5 가드 포함) |
| T13 verdict 엔진 | ✅ 완료 | `harness/acgh/verdict.py` | 9 테스트 통과(P0-3 mutation guard·P0-4 fail-closed·digest 제외) |
| T10 manifest 스키마·의미검증 | ✅ 완료 | `acgh/manifest.py` + `schema/manifest.schema.json` | 10 테스트. `verification.command` 구조적 금지(P0-8), required⊆allowed·literal·소유일치·assurance 분리(부칙 A-3.2/3.3), set 내 ID 유일 |
| T11 patch-lock | ✅ 완료 | `acgh/patchlock.py` + `schema/patch-source-lock.schema.json` | 10 테스트. source/application lock 분리(부칙 A-2.1), 고정 40-hex SHA, canonical digest, topological order(A-3.7), source object preflight(A-2.4) |
| T15 result writer·CI adapter | ✅ 완료 | `acgh/result_io.py` + `schema/acgh-result.schema.json` | 12 테스트. 원자적 write(temp→검증→digest self-check→fsync→replace), interpret 4대 analysis_error(누락·파손·digest·stale·exit불일치), attestation 무효화(부칙 A-1) |
| T14 감사카드(evidence) | ✅ 완료 | `acgh/evidence.py` + `schema/change-evidence.schema.json` | 5 테스트. 게이트 집계·approver/LLM 분리 필드·LLM verdict 금지(§7)·headline=집계 강제(P0-3) |
| — 하네스 스캐폴드 | ✅ 완료 | `harness/pyproject.toml`·`fixtures/`·`.gitignore` | `pytest` **57 통과**, 결정성 2회 동일, 실제 OM smoke 통과 |

| T30 커밋 단위 불변식 | ✅ 완료 | `acgh/invariants.py`(+`gitprim` parents/change_type 확장) | 13 테스트(실제 temp git·실제 OM 경로). ID없는 core 커밋 block(P0-5), 다중 ID·merge·empty·core/governance 혼합·unknown=analysis_error |
| T31 ID 단위 불변식 | ✅ 완료 | `acgh/invariants.py` | series 미승인·비연속(A-3.7)·의존 순환(DFS)·retired 재사용·미등록 ID 각각 검출 |

| T20 재적용 CI 탐지 모드 | ✅ 완료 | `acgh/reapply.py` | 6 테스트(실제 OM auth 소스 기반). 임시 worktree cherry-pick, A-2.6 상태 분류(applied/content_conflict/redundant/missing/skip), 충돌=block·missing=analysis_error, worktree 폐기·트리 clean 유지(P0-2) |
| T21 재적용 담당자 해결 모드 | ✅ 완료 | `acgh/resolve.py` | 3 테스트(실제 OM conflict). 충돌 worktree 유지·해결, 모든 적용 커밋에 Source-Commit/Patch-Revision/Application-Record/Resolution-Record trailer 각인(A-2.2), 무충돌=동일 revision·해결=revision 증가(A-2.3), application lock 결속 |
| T22 clean-room replay | ✅ 완료 | `acgh/replay.py` | 4 테스트(실제 OM). 재생 tree==candidate tree=pass, 불일치=block+경로 리포트, 재생불가=analysis_error, 3회 동일 해시(content-addressed), 추적 tree만(A-3.8) |
| T23 단일 integrator CAS | ✅ 완료 | `acgh/integrator.py` | 6 테스트. logical(digest)+physical(update-ref old-OID) 2중 CAS, 동일 base 동시 갱신 stale 거부, malformed 사전 차단(A-2.5) |
| T40 drift(touched/net) | ✅ 완료 | `acgh/drift.py`(+`gitprim.net_changed_paths`) | 4 테스트(실제 OM). 상한(touched⊆allowed)·하한(required∈net), net-zero도 차단(P0-6·A-3.7) |
| T62 SHA 결속 | ✅ 완료 | `acgh/binding.py` | 7 테스트. ref→고정 SHA pin(실제 미러), repository-qualified inputs 봉인, 비-SHA 거부(§10.1) |
| T32 최종상태 불변식 | ✅ 완료 | `acgh/finalstate.py`(+`replay.replay_tree`) | 5 테스트. counterfactual 기여도(inert=block·inconclusive=analysis_error), candidate==replay, 승인 무효화(P0-5·A-3.7) |
| T33 게이트 명칭·보장범위 | ✅ 완료 | `acgh/scope.py`(evidence 카드 결합) | 3 테스트. 보장/미보장 표를 게이트 출력에 결속(기능 보장 아님 명시, P0-5·P0-7) |
| T41 민감영역·의도 게이트 | ✅ 완료 | `acgh/zones.py` + `policies/sensitive-zones.yaml` | 8 테스트(실제 OM zone). frozen=block/protected=approval/watched=pass, intent 부재=fail-closed(REQ-GZ-01/02) |

| T42 upgrade_watch(케이스 D) | ✅ 완료 | `acgh/upgrade_watch.py`+`impact.py` | 8 테스트(실제 A→B diff 4789변경). watch∩net→approval, 영향표면+판정없는 LLM memo(§7) |
| T93 정책 노후화 drift | ✅ 완료 | `acgh/policy_drift.py` | 5 테스트. 0-매칭 패턴(빈 총)=approval, 신규 미분류 모듈(실제 openmetadata-mcp 등)=analysis_error |
| T50 선언형 verifier | ✅ 완료 | `acgh/verifier.py` | 10 테스트. JSON Pointer·file_hash·module_present(비실행), 실행형 거부, `..` 경로이탈 차단(P0-8) |
| T62 test-result 결속 잔여 | ✅ 구현 | `acgh/testruns.py` + schema | 8 테스트. SHA/artifact/harness/suite 결속, required 누락 차단, high/critical retry-pass=approval |
| T71 fast lane | ✅ 구현 | `acgh/fastlane.py` | 5 테스트. 유형별 최소 gate, mixed=합집합, core=전체 전략 route |
| T72 break-glass | ✅ 구현 | `acgh/breakglass.py` + schema | 8 테스트. 2인·만료·scope·사후검증·통계·timezone, 무결성 gate 비면제, verdict 불변 |
| T80/T81 Impact Memo | ✅ 구현 | `acgh/impact_memo.py` + schema | 7 테스트. 사실/추론/미확인·근거·snapshot, verdict/command 금지, 품질지표 |
| T90 upgrade orchestration | 🟡 계약 구현 | `acgh/upgrade_run.py` + schema | 5 테스트. 12단계 누락/skip 차단·candidate/test 결속. 실제 스택 실행은 미수행 |
| T91 동일 digest 승격 | ✅ 엔진 구현 | `acgh/release.py` + schema | 8 테스트. policy/catalog/core/platform/harness 포함 release-lock, stale 무효화, 재빌드·digest 불일치 차단 |
| T92 retirement | ✅ 구현 | `acgh/retirement.py` + schema | 6 테스트. 공식대체·ADR·회귀·2인·active→retired |
| T94 내부망 반입 | 🟡 검증기 구현 | `acgh/airgap.py` + schema | 6 테스트. 파일 hash·release-lock·signature verifier fail-closed. 실제 서명/내부망 미수행 |

> **게이트 엔진 구현 현황:** 현재 테스트 함수는 271개이며, 2026-07-25 기준
> 236개 통과·실제 OM 미러 의존 35개 skip이다. T25-R 실제 source plan과
> 44개 shared owner는 확정했지만 논리 ID commit의 vendor candidate를 만들기
> 전까지 현재 snapshot은 T25에서 차단돼야 한다. 실제 7개 contract test와 T90
> 운영 증거가 생기기 전에는
> **MVP2 달성 또는 배포 가능**으로 표현하지 않는다.
> (T93/T42 라벨: 정본은 T42=upgrade_watch·T93=정책노후화. 초기 커밋 라벨 오류를
> `21bfc15`에서 정정.) **다음 = MVP2(운영·승격)**: T60·T61·T90(계층3 테스트)·
> T70·T91(계층4) + 잔여 T43·T51/52·T80. 검증기 카탈로그 §0.1 구현현황 참조.
