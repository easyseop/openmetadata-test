# OpenMetadata 커스터마이징 거버넌스

공식 OpenMetadata 버전이 올라가도 **행내 커스터마이징을 누락 없이 · 추적 가능하게 ·
검증 가능하게 보존**하여, 버전 업그레이드 운영을 원활하게 만들기 위한 설계·개발 기준.

> **비개발자는 여기부터:** [비개발자용 OpenMetadata 업그레이드 안전 가이드](docs/00-사용가이드/비개발자_사용_가이드.md)
>
> 결과 읽는 법, 요청할 정보, 실제 사용 시나리오, LLM 위키의 역할을 쉬운 말로 설명한다.

---

## 무엇을 하려는가 (한 줄)

> 오픈소스 새 버전이 나올 때마다 우리 수정이 **빠지거나 · 왜 고쳤는지 잊히거나 ·
> 위험한 곳을 건드려도 모른 채 넘어가는** 사고를, 사람 기억이 아니라 **자동 검사(CI)**로 막는다.

기본 전략: **vendor merge** — 공식 OpenMetadata와 공통 조상을 유지하는 vendor branch에
승인된 공식 태그(고정 SHA)를 merge하고, 이름표(`BANK-OM-xxx`)로 등록한
커스터마이징이 최종 candidate에 남아 있는지 검증한다.

기존 cherry-pick/clean-room replay는 **필수 운영 절차가 아니라 선택적 진단·복구
모드**로 유지한다. 이 결정의 정본은
[`ADR-001`](docs/02-설계/ADR-001-vendor-merge-default.md)이다.

> 현재 상태: T24~T29와 실제 7개 등록부, T25-R snapshot 재구성 검증기,
> Docker-free 운영 게이트를 구현했다. 공식 `1.13.1-release`에서 시작한 실제
> 7-ID vendor candidate도 `easyseop/OpenMetadata`에 만들었고 T25-R/T25/T26/
> T60-I/T30/T31이 통과했다. 7개 업무 계약의 필수 selector 9개는 모두 실제 구현됐고
> Sybase/Tibero 두 계약과 한글 IME 소스 가드는 통과했다. 실제 OpenMetadata
> API 4개와 실제 브라우저 3개는 아직 skip이다. 별도 T62 runtime workflow와
> 원자적 candidate-bound 결과 생성기는 구현했고, 생성된 증거 3종은 실행 결과와
> 관계없이 덮어쓰기 불가 GitHub artifact로 90일 보존한다. 실제 운영 실행은 없다.
> T61은 Sybase/Tibero 패치가 없는 고정 소스에서 두 계약이 실제 실패함을
> 입증했지만, 배포된 제거본이 필요한 high ID 3개는 아직 미실행이다.
> 실제 업그레이드 실행과 release artifact도 없으므로 현재 production release는
> 차단 상태다.
> 상세는 [`STATUS.md`](STATUS.md)와
> [Claude 검토 인수인계](docs/04-진행/CLAUDE_REVIEW_HANDOFF.md)를 본다.

## 무엇을 보장하고, 무엇은 보장하지 않는가 (중요)

자동 검증의 범위를 정확히 나눈다. "등록·통합 생존"은 구조적으로 검증하지만
"기능 의미"는 테스트·운영으로 관리한다(100% 자동 보장이 아님).

| 계층 | 자동 보장 | 보장하지 않음(다른 계층 담당) |
|---|---|---|
| 등록·통합 생존 게이트 | 승인된 공식 SHA가 통합되고 등록된 수정이 candidate에 남아 있음 | 로직 생존·기능 의미 |
| 계약·업그레이드 테스트 | 명시된 업무 불변식의 동작 | 테스트에 없는 새 의미 차원(잔여 위험) |
| 구조화 증거 생성기 | API·설정·DB·의존성의 구조 변화 사실 | 그 변화의 업무 영향 판단 |
| 운영 관찰(canary) | 실제 부하·데이터 거동 | — |

## 변경 케이스별 — 무엇이 잡나

```
A 무관한 변경        → 경로 대조 (무관 판정)
B 우리 파일·다른 줄   → vendor merge + 경로 플래그
C 같은 줄 충돌        → merge conflict → 사람 해결·기록
D 의존 대상 변경      → upgrade_watch + 구조화 diff + LLM Memo → 테스트 확정
E 깊은 의존·의미 붕괴 → 테스트만 (patch-kill·contract·차등 테스트)
```

---

## 내 요구사항은 어디까지 충족되나 (영역 · 체크리스트)

기능을 **영역(Area)**으로 묶어 요구사항과 매핑한다. 각 영역의 상세한 *왜 필요 ·
안 지키면 · 방법론*은 바로 아래 **[검증기 22종]** 표를 본다.

| 영역ID | 영역 | 한 줄 | MVP | 담당 검증기(#) |
|---|---|---|---|---|
| **A1** | 수정 등록 | 바꾼 곳이 이름표 달고 빠짐없이 등록됐나 | 1 | 2·3 |
| **A2** | 업스트림 통합 | 승인된 공식 SHA가 vendor candidate에 들어왔나 | 1 | T24·T25 |
| **A3** | 생존·재현성 | 등록된 수정이 남고 candidate가 고정됐나 | 1 | T26·17·20 |
| **A4** | 범위·민감 통제 | 정한 범위 밖·민감한 곳(인증 등) 건드렸나 | 1 | 6·7·12 |
| **A5** | 업그레이드 영향 감지 | 의존 파일·설정이 바뀌었나·정책이 낡았나 | 1 | 8·9·13·22 |
| **A6** | 판정·결과 무결성 | 판정 뒤집힘·결과 조작·혼동 방지 | 1 | 21 + 결과계약 |
| **A7** | 기능 동작 검증 | 실제 업무 기능(권한·검색·API)이 맞나 | 2 | 14·15·16·17·18 |
| **A8** | 릴리스·반입 통제 | 검증본 그대로 배포·내부망 반입되나 | 2 | 19·20 |

**요구사항 충족 체크리스트**

| 요구ID | 요구사항 (쉬운 말) | 영역 | 상태 |
|---|---|---|---|
| **R1** | 커스터마이징이 새 버전에 **빠짐없이** 올라갔는지 자동 확인 | A1·A2 | ✅ 실제 7-ID vendor candidate에서 T25-R/T25/T26 통과 |
| **R2** | 커스터마이징을 **왜/어디서** 했는지 이력 보존 | A1·A3 | ✅ 완료 |
| **R3** | **범위 밖·위험 변경**이 검토 없이 통과 못하게 | A4 | ✅ 완료 |
| **R4** | 승인된 공식 버전이 vendor candidate에 통합됐음을 확인 | A2 | ✅ T24 lock·T25 ancestry |
| **R5** | 후보 SHA·tree·artifact가 고정되고 추적됨 | A3 | ✅ T24 candidate-lock·결과 입력 결속 |
| **R6** | **충돌 없이 의미만 바뀐** 변경 감지(케이스 D) | A5 | ✅ 완료(감지·리뷰) |
| **R7** | '등록·재적용'과 '기능 정확성'을 **정직하게 구분** | A6 | ✅ 완료 |
| **R8** | 실제 **업무 동작**(권한·API·검색) 검증 | A7 | 🟡 결과계약 구현 / 실제 contract·T90 실행 필요 |
| **R9** | **릴리스 승격·내부망 반입** 통제 | A8 | 🟡 검증기 구현 / 실제 승격·서명·반입 필요 |

> **MVP별 커버**: 게이트 엔진은 vendor/replay와 운영 경계까지 구현됐다.
> Production-upgrade 달성 조건은 owner, 7개 contract test, T90 실행, T91 승격,
> T94 서명 반입 증거다. 단위 테스트 성공을 배포 가능으로
> 해석하지 않는다.

## 전체 검증기 22종 — 왜 필요 · 안 지키면 · 어떻게 구현

> 상태: **✅ 완료 · 🟡 부분 · ⬜ 계획.** 단일 정본은
> [`docs/03-기술참조/openmetadata_verifier_catalog.md`](docs/03-기술참조/openmetadata_verifier_catalog.md) §0.1.
> 계층 1·2·4는 등록·통합 생존·구조를 **결정적으로** 보장, 계층 3(테스트)이 기능 의미,
> 보조(LLM)는 후보만 좁힌다(판정권 없음).

### 계층 1 — 등록·통합 생존 검증 (구조, 결정적)

| # | 검증기 | 왜 필요 · 안 지키면 나올 문제 | 구현 방법론 (또는 계획) | 상태·태스크 |
|---|---|---|---|---|
| 1 | 통합 게이트 | 승인된 공식 버전과 행내 수정이 candidate에 함께 존재해야 한다 | 기본은 vendor ancestry·T25-R snapshot 재구성·target SHA·customization 생존 검사. cherry-pick 탐지/해결은 선택 replay 모드 | ✅ 실제 7-ID candidate에서 T25-R/T25/T26 통과 |
| 2 | 커밋 불변식 | 뭘 바꿨는지 **세야** 누락 검증 가능 · 이름표 없으면 '수정 목록' 자체가 없음 | 커밋 **꼬리표만** 파싱, 업스트림 건드린 커밋=**이름표 정확히 1개**(0·다중·merge·빈·원본+정책 혼합=위반) | ✅ T30 |
| 3 | ID·series 불변식 | 한 수정이 여러 커밋일 때 **절반만 반영**돼도 통과하면 안 됨 | 이름표 단위로 series 승인·**연속성**·의존 순환·폐기 재사용 검사 | ✅ T31 |
| 4 | 최종상태 불변식 | "이름표는 다 있는데 기능은 사라진" 상태 차단 | **counterfactual**: 그 ID만 뺀 재생 tree와 전체 재생 tree 비교, 같으면 기여 0=차단 | ✅ T32 |
| 5 | clean-room replay | 패치의 독립 이식성·복구 가능성 진단 | 선택 replay 모드에서 격리 재생 결과 tree와 후보 비교 | ✅ 선택 모드 T22 |
| 6 | 구현범위 drift | 명세가 실제와 어긋나면 뒤 검사·감시가 **전부 무력화** | 상한(변경 ⊆ 허용 glob) + 하한(필수 경로가 **실제 순변경**에 있나) | ✅ T40 |
| 7 | 민감·의도 게이트 | 인증 등 위험 변경이 **검토 없이** 통과 | 파일×민감영역(**차단/승인/경고 3단**) + 선언(intent) 대조(선언 없음=fail-closed) | ✅ T41 |
| 8 | 정책 노후화 drift | 리팩터로 코드 이사가면 정책이 **'빈 총'**인데 통과만 뜸 | 신버전 트리에서 패턴 **0매칭=빈 총**, 신규 미분류 모듈=analysis_error | ✅ T93 |
| 9 | upgrade_watch | 우리가 안 바꿔도 **의존 대상이 바뀌면** 조용히 깨짐(케이스 D) | 실제 A→B 순변경 ∩ 감시 경로 → 걸리면 승인(리뷰) | ✅ T42 |
| 10 | 부채 게이트 | 코어 수정이 쌓여 **업그레이드 불가 포크**로 붕괴 | 코어 수정 수·변경량·충돌률·hotspot을 soft/hard 임계값과 비교(soft=approval·hard=block) | ✅ T43 |
| 11 | candidate/patch lock | candidate는 SHA·tree·digest로 고정. replay를 사용할 때만 patch source도 고정 | candidate-lock(T24) + 선택 patch-lock(T11) | ✅ T24·T11 |

### 계층 2 — 증거 생성기 (결정적, LLM 이전)

| # | 검증기 | 왜 필요 · 안 지키면 나올 문제 | 구현 방법론 (또는 계획) | 상태·태스크 |
|---|---|---|---|---|
| 12 | 선언형 verifier | 설정·확장이 실수로 되돌려져도 완전성 게이트는 못 잡음 / manifest 임의 shell=CI 권한 임의 실행 | **비실행 타입만**(JSON Pointer·파일 해시·모듈 존재), 실행형은 거부(sandbox 필요) | ✅ T50 |
| 13 | 구조화 diff providers | 반환 구조·설정 기본값·스키마 변경의 **근거를 사람·LLM보다 먼저** 확보 | A↔B JSON/스키마의 구조 diff(추가/삭제 키·타입 변경)를 미러에서 결정적 추출(증거만, 판정 아님) | ✅ T51·T52 |

### 계층 3 — 동작·의미 (테스트)

| # | 검증기 | 왜 필요 · 안 지키면 나올 문제 | 구현 방법론 (또는 계획) | 상태·태스크 |
|---|---|---|---|---|
| 14 | 필수 테스트 존재 | 없는 테스트를 '필수'로 걸고 검증했다 **착각** | catalog selector의 실제 파일·함수 존재를 AST로 확인하고, candidate-bound 실행 결과 누락·skip은 별도 차단 | ✅ `contracts.py` + `testruns.py` |
| 15 | contract 결속 | 릴리스마다 **어떤 업무 규칙**이 지켜지는지 모른 채 넘어감 | contract 카탈로그(업무 불변식↔required_tests) + manifest 참조 결속, effective=direct∪파생, selector 구현 미존재=block | ✅ T60·T60-I |
| 16 | patch-kill | 패치를 빼도 통과하는 **껍데기 테스트**를 모름 | 패치 없는 worktree에서 테스트 실행 → 실패=PROVEN(입증)·통과=SHELL(block)·실행불가=analysis_error | ✅ T61 |
| 17 | 테스트-SHA 결속 | 후보 바뀌었는데 **옛 결과를 유효로** 착각 / flaky 뭉갬 | candidate SHA·artifact·harness/suite 결속, high/critical retry-pass=approval | ✅ T62 |
| 18 | 차등 테스트 | 건수 대사만으론 **관계·의미 손상** 놓침 | 구·신 12단계 결과계약·증거 digest·candidate 결속 | 🟡 T90 계약 구현·실행 미완 |

### 계층 4 — 무결성·정책·집계

| # | 검증기 | 왜 필요 · 안 지키면 나올 문제 | 구현 방법론 (또는 계획) | 상태·태스크 |
|---|---|---|---|---|
| 19 | 정책 base-평가 | 승인 요건을 **스스로 없애는 자기 완화 우회** | 정책 파일 변경 candidate는 **base(변경 전) 정책으로 평가** 강제(신 정책으로 판정 시 block) | ✅ T70 |
| 20 | digest 승격 | **검증본과 다른 산출물**이 배포/반입됨 | release-lock으로 commit·image·Helm·test digest 동일성, 내부망 hash/signature 재검증 | 🟡 T91/T94 엔진·실행 미완 |
| 21 | verdict 엔진 | max 집계로 **차단이 승인으로 격하** / 고장을 통과로 우회 | **심각도 순위** 집계(exit code로 안 함), 분석실패·빈 입력=차단(fail-closed) | ✅ T13 |

### 보조 — LLM (판정 아님)

| # | 검증기 | 무엇을 하나 · 한계 | 구현 방법론 (또는 계획) | 상태·태스크 |
|---|---|---|---|---|
| 22 | LLM Impact Memo | 애매한 의미 변경을 **후보로 좁혀줌** · pass 부여 불가·100% recall 아님 | 사실/추론/미확인·근거·snapshot을 strict schema로, verdict/command/action 금지, 품질지표 | ✅ T80/T81 |

---

## 문서 지도

문서는 성격별로 `docs/` 하위에 정리돼 있다. 현재 상태와 독립 검토 진입점도
루트에 둔다:
[`README.md`](README.md)(개발 진입)·[`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md)
(경영진 5분 요약)·[`STATUS.md`](STATUS.md)(현재 상태)·
[`CLAUDE.md`](CLAUDE.md)(독립 검토)·`SESSION_STATE.md`(역사적 인수인계).

| 폴더 | 문서 | 용도 | 대상 |
|---|---|---|---|
| `docs/00-사용가이드/` | [비개발자용 사용 가이드](docs/00-사용가이드/비개발자_사용_가이드.md) | 결과 읽는 법·업무 요청·운영 시나리오 | 업무 담당·오너·승인·운영 |
| `docs/01-보고용/` | [strategy_briefing](docs/01-보고용/openmetadata_strategy_briefing.md) | 왜 이 전략인가 (merge vs 패치 스택) | 경영진·심의 |
| `docs/02-설계/` | [upstream_customization_design](docs/02-설계/openmetadata_upstream_customization_design.md) | 상세 설계 (저장소·게이트·업그레이드 절차) | 설계·개발 |
| `docs/02-설계/` | [ADR-001](docs/02-설계/ADR-001-vendor-merge-default.md) | **vendor merge 기본·replay 선택 결정 정본** | 전 대상 |
| `docs/02-설계/` | [governance_requirements (SRS)](docs/02-설계/openmetadata_governance_requirements.md) | 요구사항 정의서 ※부칙 A 우선 | 개발 |
| `docs/03-기술참조/` | [verifier_catalog](docs/03-기술참조/openmetadata_verifier_catalog.md) | 검증기 카탈로그(§0.1 구현현황) | 개발 |
| `docs/04-진행/` | [build_plan](docs/04-진행/openmetadata_build_plan.md) | **순차 개발 실행 계획** | 개발 |
| `docs/04-진행/` | [dev_roadmap](docs/04-진행/openmetadata_dev_roadmap.md) | **로드맵 & MVP 커버리지 맵** | 개발·심의 |

> **개발 착수 기준**: 진행·커버리지는 `docs/04-진행/openmetadata_dev_roadmap.md`,
> 상세 스펙은 `docs/04-진행/openmetadata_build_plan.md`(+ SRS 부칙 A). 충돌 시
> 우선순위는 **ADR-001 > SRS 부칙 A > build_plan > 설계서 본문**. (과거 검토 대화 원문은
> 제거했고 git 이력에 보존됨. 수용된 정정의 핵심은 아래 '설계 정정 이력' 참조.)

## 설계 정정 이력 (검토 반영 요약)

> 두 차례 아키텍처 검토(P0/2차 결함) + 문서 검토를 거쳐 정정했다. 원문 대화는
> 제거했고, **수용된 정정의 핵심과 반영 위치**만 남긴다.

| 검토 | 수용한 핵심 정정 | 반영 위치 |
|---|---|---|
| **1차** (설계 P0 9건) | ① 판정을 **심각도 순위로 집계**(차단이 승인으로 격하 금지)·**분석실패=차단** ② 충돌 **탐지/해결 2모드** ③ **선언형 verifier**(manifest 임의 shell 제거) ④ range-diff 기계판정 제거 → **patch-lock+trailer** ⑤ `affected_paths` → **allowed/required_changed_paths + upgrade_watch** ⑥ **"등록·재적용 완전성" ≠ 기능 완전성** ⑦ 정책 **self-approval 차단** | SRS 본문 · build_plan · 코드 |
| **2차** (2차 결함) | **부칙 A** — ⓐ 결과계약을 CI 경계까지(불일치=analysis_error·원자적 기록·정규 해시) ⓑ **lock 분리·출처 자동각인·CAS** ⓒ 스키마 의미(path-ownership·required⊆allowed·verifier sandbox) | SRS 부칙 A · 코드 |
| **문서** (외부) | build_plan **순환의존 해소**·검증기 4계층 표기·`harness/README`·`EXECUTIVE_SUMMARY`·`docs/` 분류·SRS 상태 메타데이터 | 각 문서 (적용 완료) |
| **운영전략** (2026-07-24) | vendor branch에 공식 SHA를 **merge하는 방식을 기본**, cherry-pick/replay는 선택 진단·복구 모드로 변경. 기존 replay 중심 MVP 표시는 범위 한정 | ADR-001 · README · 인수인계 |

## 테스트 정책

**OpenMetadata의 파일 구조·업그레이드 차이·재적용 동작에 의존하는 통합 및
업그레이드 테스트는 실제 고정 버전의 OpenMetadata를 사용한다.** 합성 더미가
아니라 `open-metadata/OpenMetadata`의 고정 두 태그(UPSTREAM_A/B)를 미러로 받아,
실제 파일 경로 위에 BANK-OM 패치를 얹어 케이스 A~D를 재현한다. **순수 판정
로직(집계·스키마 검증 등)의 단위 테스트는 최소 합성 픽스처를 쓸 수 있다.**
업그레이드 테스트(M9)는 실제 OM Docker·DB migration·재색인으로 수행한다.
(상세: `docs/04-진행/openmetadata_dev_roadmap.md` §1)

## 개발 순서 (마일스톤)

```
M0 사전 셋팅(정책·명세 저작)
M1 기반(스키마·patch-lock·git·verdict)   ← 먼저 완성
M2 업스트림 통합(vendor merge 기본 + replay 선택 모드)
M3 등록·통합 생존 게이트(불변식)
M4 경로·민감·부채 게이트 + 영향분석(upgrade_watch)
M5 증거 생성기(선언형 verifier·구조화 diff)
M6 테스트 결속(contract·patch-kill·SHA)
M7 정책 자기보호·fast lane·break-glass
M8 LLM Upgrade Impact Memo
M9 업그레이드 검증·릴리스 승격(digest 결속)·반입
```

## 핵심 원칙 (정정 후)

1. 코어 수정 최소화 (설정→배포→확장→코어 4단계 관문). 충돌은 코어에서만 난다.
2. 불변 ID 기반 customization registry(기능과 계약의 안정된 식별자).
3. 고정 SHA 기반 upstream-lock·candidate-lock. patch-lock은 replay 모드 전용.
4. vendor ancestry·customization 생존 검증을 기본으로 하고 replay는 선택 진단으로 사용.
5. 판정 스파인(언어 무관·결정적) / 증거 생성기(대상별) 분리.
6. **등록·통합 생존 완전성 ≠ 기능 완전성** (분리해 표기).
7. verdict severity rank (분석 실패 = 차단).
8. 선언형 verifier (manifest 임의 실행 금지).
9. 정책 자기보호 (policy PR은 base 정책으로 평가).
10. LLM은 배포 판정 배제 (Memo·후보 제시만).
11. 테스트가 생존을 증명 (contract-id + patch-kill).
12. range-diff는 사람 리뷰용 (기계 판정은 patch-lock+trailer+raw diff).

## 개발자 빠른 시작 (하네스 실행)

구현 코드는 `harness/acgh/`, 게이트 테스트는 `harness/tests/`, 실제 계약은
`tests/bank/contracts/`. Python 3.11 · git 2.43+.

```bash
pip install jsonschema pathspec pyyaml pytest
OPENMETADATA_PRODUCT_REPO=/path/to/OpenMetadata \
  python -m pytest harness/tests tests/bank/contracts
# 고정 mirror 연결 시 313개: 306 pass·7 operational skip
```

동일한 source 범위는
`.github/workflows/source-candidate.yml`이 고정 product SHA와 고정 action SHA로
자동 재현한다. API 4개와 브라우저 3개는
`.github/workflows/runtime-contracts.yml`의 수동 T62 운영 job 대상이다.
이 job은 후보 SHA·배포 artifact digest·하네스 commit·suite digest를 묶고,
skip을 pass로 올리지 않는다. `candidate-lock.yaml`, `test-run-set.yaml`,
`acgh-result.yaml`은 `runtime-contract-evidence-<run_id>-<run_attempt>` 이름으로
90일 보존되고 artifact ID·GitHub digest·URL은 job summary에 남는다. 90일을
넘는 감사 보존은 만료 전에 조직 소유 저장소로 별도 이관해야 한다.

같은 source CI는 `patch-kill-plan.yaml`의 고정 predecessor에서 Sybase/Tibero
계약을 다시 실행한다. 두 계약은 해당 패치가 없을 때 실패해야 통과하며, JUnit과
실제 pytest exit가 불일치하거나 test error/skip이면 성공이 아니라
`analysis_error`다. 결과는
`source-patch-kill-evidence-<run_id>-<run_attempt>` artifact로 90일 보존한다.
이것은 source-capable high ID 2개만의 결과이며, API 기반 high ID 3개는 제거본
배포 후 별도 T61 실행이 필요하다. 그 세 건을 위한
`.github/workflows/runtime-patch-kill.yml`은 일반 T62와 분리된 승인 환경에서
한 ID씩 실행한다. 대상 계약은 두 번 모두 실패해야 하고 독립 API/data/UI
health probe는 전후 모두 통과해야 한다. source/tree/artifact/deployment
evidence/governance/suite/environment를 한 결과에 결속하지만, 실제 제거본
build·배포·운영 실행은 아직 없다.

**실제 OM 미러 연결**(게이트·재적용 테스트용, 없으면 해당 테스트 자동 skip):

```bash
bash fixtures/fetch_upstream.sh   # /home/user/om-mirror 에 두 고정 태그(1.12.13/1.13.0)
```

- **입력**: manifest(커스터마이징 명세, **임의 shell 필드 없음**)·patch-source-lock
  (고정 40-hex SHA)·정책 YAML(`policies/`: 경로 소유·민감영역).
- **출력**: acgh-result(불변 기계 판정, canonical 해시 자체검증)·change-evidence
  (감사카드, 승인/LLM **분리** 필드).
- **판정 4상태**: `pass < approval < block < analysis_error` (exit 0/2/1/3,
  **분석 실패=차단** fail-closed).
- **규칙**: 게이트·재적용 테스트는 실제 OM 미러(합성 더미 금지), 순수 판정 로직은
  합성 픽스처 가능 · 결정성(같은 입력=같은 출력, pathspec=`gitignore` 고정) ·
  불가·미분류·빈 입력 = `analysis_error`.

*(모듈별 상세 표·디렉터리·문제 해결은 `harness/README.md`.)*
