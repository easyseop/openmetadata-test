# ACGH — OpenMetadata 커스터마이징 자동 검증 도구

> Deterministic CI controls for preserving and validating OpenMetadata
> customizations across upstream upgrades.

행내 커스터마이징이 업스트림 업그레이드에서 **빠짐없이 · 규칙대로 · 재현
가능하게** 새 버전에 올라갔는지를 사람 기억이 아니라 기계가 판정한다. 상세
설계·요구사항은 저장소 루트 문서를 본다(이 README는 **실행 진입점**).

이 도구가 결정적으로 검증하는 것은 **등록·재적용·구조**이고, **업무 동작의
정확성**은 별도 테스트가 담당한다 — 검증기 카탈로그 §0 경계 참조.

## 내 요구사항은 어디까지 충족되나 (영역 매핑 · 체크리스트)

기술 용어 대신 **요구사항 관점**으로 정리한다. 각 요구사항을 기능 **영역(Area)**에
매핑하고, MVP가 완성될 때 어디까지 충족되는지 체크리스트로 본다.

### 기능 영역 (영역별 ID)

| 영역ID | 영역 | 한 줄 설명 | MVP |
|---|---|---|---|
| **A1** | 수정 등록 | 우리가 바꾼 곳이 빠짐없이 '이름표(고유번호)'를 달고 등록됐나 | 1 |
| **A2** | 재적용 | 새 공식 버전 위에 우리 수정이 순서대로 다시 얹히나 · 충돌 처리 | 1 |
| **A3** | 재현성 | 후보가 '고정 소스 + 정해진 패치'로만 똑같이 재현되나(몰래 낀 변경 차단) | 1 |
| **A4** | 범위·민감 통제 | 정한 범위 밖이나 민감한 곳(인증 등)을 건드렸는지 | 1 |
| **A5** | 업그레이드 영향 감지 | 우리가 의존하는 파일·설정이 새 버전에서 바뀌었나 · 정책이 낡았나 | 1 |
| **A6** | 판정·결과 무결성 | 판정이 뒤집히거나 결과가 조작·혼동되지 않게 | 1 |
| **A7** | 기능 동작 검증 | 실제 업무 기능(권한·검색·API 등)이 맞게 동작하나 | 2 |
| **A8** | 릴리스·반입 통제 | 검증한 그것 그대로 배포·내부망 반입되나 | 2 |

### 각 영역이 왜 필요한가 · 안 지키면 나올 문제

| 영역 | 왜 필요한가 | 안 지키면 나올 수 있는 문제 |
|---|---|---|
| **A1** 수정 등록 | 무엇을 바꿨는지 **세어야** 누락을 검증할 수 있다. 등록이 없으면 '우리 수정 목록' 자체가 없다. | 이름표 없이 원본을 고치면 새 버전에서 그 수정이 빠져도 아무도 모른다 → 몇 주 뒤 "이 기능 왜 안 되죠?" / 누가·왜 고쳤는지 추적 불가. |
| **A2** 재적용 | 업그레이드의 핵심. 우리 수정이 새 버전에 **다시 올라가야** 쓸 수 있다. | 수정 하나가 안 얹힌 채 배포 / 충돌을 대충 뭉개 기능이 깨짐 / 업그레이드마다 수작업 반복으로 업그레이드 자체를 미루게 됨. |
| **A3** 재현성 | "이번에 배포한 게 **정확히 무엇**이냐"를 말할 수 있어야 감사·롤백·디버깅이 된다. | 검증 안 받은 변경이 몰래 섞임 / 같은 릴리스가 매번 달라짐 / 사고 시 "왜 이렇게 됐는지" 재현·추적 불가. |
| **A4** 범위·민감 통제 | 인증·마이그레이션 같은 곳은 실수 하나가 **보안·데이터 사고**. 선언 범위를 넘으면 나머지 통제가 무의미해진다. | 위험 변경이 검토 없이 배포 / 범위 밖 변경으로 명세가 실제와 어긋나 **뒤따르는 검사·감시가 전부 무력화**. |
| **A5** 업그레이드 영향 감지 | 우리가 직접 안 바꿔도 **의존하는 업스트림이 바뀌면 조용히 깨진다**. 충돌이 안 나서 더 위험(케이스 D). | 예: `tenant` 의미가 바뀐 걸 놓쳐 권한이 오작동 / 정책 패턴이 낡아 실제로는 아무것도 안 지키는데 '통과'만 뜸. |
| **A6** 판정·결과 무결성 | 게이트가 아무리 좋아도 **판정이 뒤집히거나 결과가 조작·혼동**되면 전부 헛일. | 차단돼야 할 게 '승인 필요'로 격하 / 검사기 고장을 통과로 착각 / 후보가 바뀌었는데 **옛 검증 결과를 유효로 오인**. |
| **A7** 기능 동작 검증 (MVP2) | 등록·재적용이 됐다고 **기능이 맞게 도는 건 아니다**. | 이름표는 다 있는데 실제 업무 기능(권한·검색·API)이 틀림 / 회귀를 배포 후에야 발견. |
| **A8** 릴리스·반입 통제 (MVP2) | 검증한 것과 배포·반입되는 것이 **같아야** 검증이 의미 있다(특히 외부→내부망). | 검증본과 다른 산출물이 배포됨 / 외부망·내부망 불일치 / 반입 후 "정말 그게 그거냐"는 신뢰 붕괴. |

### 각 영역을 어떻게 구현했나 (방법론)

| 영역 | 구현 방법론 (어떻게) | 모듈 |
|---|---|---|
| **A1** 수정 등록 | 커밋을 git으로 **경계 보존하며** 읽고 **메시지 꼬리표(trailer)만** 파싱(본문 정규식 금지). 업스트림 경로를 건드린 커밋은 **이름표 정확히 1개**인지 검사 — 0개·다중·merge·빈 커밋·원본+정책 혼합을 각각 위반으로. 이름표 단위로는 여러 커밋 묶음(series)의 승인·연속성·의존 순환·폐기 재사용을 검사. | `invariants`·`gitprim` |
| **A2** 재적용 | **임시 작업공간(git worktree)**을 새 버전(고정 SHA)에 만들고 patch-lock 순서대로 **cherry-pick**. *탐지 모드*는 결과를 상태별(적용/충돌+충돌파일/중복/누락)로 분류 후 작업공간 폐기·본 저장소는 그대로. *해결 모드*는 충돌을 **유지**해 담당자가 풀고 이어붙이며, 모든 적용 커밋에 **출처·리비전 꼬리표를 각인**. | `reapply`·`resolve` |
| **A3** 재현성 | 격리된 작업공간에서 patch-lock **전체를 재생**한 결과 트리 해시와 후보 트리 해시를 **비교**(같으면 몰래 낀 변경 없음). git 트리는 내용 주소라 같은 입력→같은 해시(결정적). 소스는 **고정 40자리 SHA로 잠그고**(동적 '최신' 조회 금지), 잠금 갱신은 **단일 담당자의 조건부 교체(CAS)**로 동시 충돌 방지. | `replay`·`patchlock`·`integrator` |
| **A4** 범위·민감 통제 | 변경 파일을 **공용 경로 문법(gitignore glob)**으로 판정. *범위*: 상한(변경 경로 ⊆ 허용 패턴) + 하한(필수 경로가 **실제 순변경**에 있나) 둘 다. *민감*: 파일×민감영역(**차단/승인/경고** 3단) + 선언(intent)과 대조(선언 밖=승인, 금지=차단, **선언 없음=fail-closed**). | `drift`·`zones`·`layout` |
| **A5** 업그레이드 영향 감지 | 실제 **A→B 순변경**과 manifest의 **감시 경로를 교집합** → 걸리면 승인(리뷰 유발). 정책 노후화는 신버전 트리에서 패턴이 **0매칭이면 '빈 총'**, 신규 미분류 모듈은 fail-closed. 영향 표면은 의존성·설정·규칙 맥락과 함께 정리하고, LLM 메모는 **자문만**(판정권 없음, 결과에 verdict 필드 금지). | `upgrade_watch`·`impact`·`policy_drift` |
| **A6** 판정·결과 무결성 | 4상태를 **심각도 순위로 집계**(exit code로 집계 안 함 → 차단이 승인으로 **격하 불가**), 빈 입력·검사 실패는 **analysis_error(fail-closed)**. 결과는 **원자적 기록 + 정규 해시 자체검증**, 입력 SHA·exit 불일치·낡음이면 analysis_error. 입력은 **고정 SHA로 봉인**, 사람 승인·LLM은 **분리 필드**. | `verdict`·`result_io`·`binding`·`evidence` |
| **A7** 기능 동작 검증 (MVP2) | *(계획)* 업무 규칙(contract)↔테스트 **결속**, **patch-kill**(패치를 빼면 그 테스트가 실제로 실패하는지로 '껍데기 테스트' 배제), 구·신 버전 **차등 테스트**. | 예정 |
| **A8** 릴리스·반입 통제 (MVP2) | *(계획)* 검증한 commit SHA·산출물 digest와 **배포·반입물 digest 일치** 확인(재빌드·복사 금지), 외부→내부망 **digest 승격**. | 예정 |

### 요구사항 충족 체크리스트

| 요구ID | 요구사항 (쉬운 말) | 영역 | 상태 |
|---|---|---|---|
| **R1** | 커스터마이징이 새 버전에 **빠짐없이** 올라갔는지 자동 확인 | A1·A2 | ✅ 완료 |
| **R2** | 커스터마이징을 **왜/어디서** 했는지 이력이 사라지지 않게 | A1·A3 | ✅ 완료 |
| **R3** | **범위 밖·위험 변경**이 검토 없이 통과 못하게 | A4 | ✅ 완료 |
| **R4** | 업그레이드 후 **즉시·반복 가능하게 재적용** | A2 | ✅ 완료 |
| **R5** | 후보가 **고정 소스로만 재현**됨(몰래 낀 변경 차단) | A3 | ✅ 완료 |
| **R6** | **충돌 없이 의미만 바뀐** 변경 감지·표시(케이스 D) | A5 | ✅ 완료(감지·리뷰 유발) |
| **R7** | '등록·재적용'과 '기능 정확성'을 **정직하게 구분** | A6 | ✅ 완료 |
| **R8** | 실제 **업무 동작**(권한·API·검색) 검증 | A7 | ⬜ 계획(MVP2) |
| **R9** | **릴리스 승격·내부망 반입** 통제 | A8 | ⬜ 계획(MVP2) |

### MVP별 커버 범위 (요구 관점)

- **MVP1 완료 (현재)** → **R1~R7 충족.** 즉 *"새 공식 버전에 우리 수정이
  규칙대로 · 빠짐없이 · 재현 가능하게 올라갔고, 범위 밖·위험 변경은 걸러지며,
  우리가 의존하는 부분이 바뀌면 리뷰가 뜬다"* 를 **릴리스 후보 단계에서 자동
  통제.** (단, 기능이 실제로 맞게 도는지는 아직 = R8.)
- **MVP2 완료 (예정)** → **R8·R9 추가.** *"실제 업무 기능이 동작하고, 검증한
  산출물 그대로 릴리스·내부망 반입된다"* 까지 확장.

### 영역 → 담당 기능 (코드 매핑, 참고)

| 영역 | 담당 (쉬운 설명) | 모듈 |
|---|---|---|
| A1 | 커밋마다 이름표·중복·누락 검사 | `invariants` |
| A2 | 새 버전에 다시 얹기(탐지/해결 2모드) | `reapply`·`resolve` |
| A3 | 격리 재현으로 후보 == 재현 확인 · 소스 잠금 | `replay`·`patchlock`·`integrator` |
| A4 | 범위 밖·민감영역·의도 검사 | `drift`·`zones` |
| A5 | 의존 파일 변경·정책 노후화 감지 | `upgrade_watch`·`impact`·`policy_drift` |
| A6 | 판정 집계(뒤집힘 방지)·결과 봉인·SHA 결속 | `verdict`·`result_io`·`binding`·`evidence` |
| A7 | (MVP2) 테스트·contract·patch-kill | — |
| A8 | (MVP2) digest 승격·반입 | — |

## 현재 지원하는 기능 (개발자용 상세)

> 아래는 모듈 단위 상세다. **요구사항·영역(A1~A8) 관점은 위 체크리스트**를 본다.

| 기능 | 모듈 | 상태 |
|---|---|---|
| 4상태 판정 엔진(severity 집계·fail-closed) | `acgh/verdict.py` | ✅ |
| 결과계약·CI 어댑터(원자적 write·stale=analysis_error) | `acgh/result_io.py` | ✅ |
| 감사카드(게이트 집계·승인/LLM 분리) | `acgh/evidence.py` | ✅ |
| git 프리미티브(trailer·-z·tree) | `acgh/gitprim.py` | ✅ |
| 경로 소유·glob 문법(공용) | `acgh/layout.py` + `policies/repository-layout.yaml` | ✅ |
| manifest 스키마·의미검증 | `acgh/manifest.py` | ✅ |
| patch-lock(source/application 분리·CAS) | `acgh/patchlock.py`·`acgh/integrator.py` | ✅ |
| 수정 등록 검사(커밋마다 이름표·누락·중복) | `acgh/invariants.py` | ✅ |
| 재적용 탐지/해결 모드 | `acgh/reapply.py`·`acgh/resolve.py` | ✅ |
| clean-room replay | `acgh/replay.py` | ✅ |
| 구현범위 drift(touched/net) | `acgh/drift.py` | ✅ |
| 민감영역·의도 게이트 | `acgh/zones.py` + `policies/sensitive-zones.yaml` | ✅ |
| SHA 결속(repository-qualified inputs) | `acgh/binding.py` | ✅ |
| 최종상태 불변식(counterfactual) | `acgh/finalstate.py` | ✅ |
| 보장범위 표(게이트 출력 결합) | `acgh/scope.py` | ✅ |
| upgrade_watch(케이스 D)·영향분석 | `acgh/upgrade_watch.py`·`acgh/impact.py` | ✅ |
| 정책 노후화 drift | `acgh/policy_drift.py` | ✅ |
| 선언형 verifier(비실행형) | `acgh/verifier.py` | ✅ |

## 아직 지원하지 않는 기능 (= 남은 개발 전부)

> 아래가 **남은 개발의 전부**다(테스트 포함). 태스크·상태 단일 정본은
> `docs/03-기술참조/openmetadata_verifier_catalog.md` **§0.1 구현현황표**와
> `docs/04-진행/openmetadata_build_plan.md`(M0~M9). 각 항목은 **자체 테스트 포함**,
> A7/A9(차등)은 실제 OM Docker·DB migration 통합 테스트까지 개발한다.

| 남은 것 | 영역 | 태스크 |
|---|---|---|
| 기능 동작 검증(contract↔test 결속·patch-kill·구/신 **차등 테스트**) | A7 | T60·T61·T90 |
| 릴리스·반입(정책 self-approval 차단·**digest 승격·내부망 반입**) | A8 | T70·T91·T94 |
| 실행형 verifier(import·스크립트·컨테이너 — **sandbox 러너**) | A4 보강 | T50b |
| 구조화 diff provider(API/스키마/설정 변경 증거) | A5 보강 | T51·T52 |
| **LLM 위키·Impact Memo**(케이스 D 자문, 판정권 없음) | A5 보조 | T80·T81 |
| 부채 게이트(코어 수정 누적 상한)·폐기(retirement) 절차 | — | T43·T92 |
| 긴급예외(break-glass)·경량경로(fast-lane) | A6 보강 | T71·T72 |

## 요구 환경

- Python 3.11, git 2.43+
- 의존: `PyYAML`, `jsonschema>=4.18`, `pathspec>=0.11`

## 설치

```bash
cd harness
pip install jsonschema pathspec pyyaml pytest   # 또는: pip install -e ".[dev]"
```

## 테스트 실행

```bash
cd harness
python -m pytest            # 현재 143개 통과
python -m pytest -q         # 조용히
python -m pytest -q; python -m pytest -q   # 결정성 확인(두 번 동일)
```

실제 OpenMetadata 미러가 없으면 미러 의존 테스트는 **자동 skip**된다(순수
판정 로직 테스트는 미러 없이도 통과). 미러 연결은 아래 참조.

## 실제 OpenMetadata 미러 연결

게이트/재적용/업그레이드 테스트는 **고정 버전의 실제 OM**을 쓴다(합성 더미
금지). 두 고정 태그만 blobless로 가져온다:

```bash
bash fixtures/fetch_upstream.sh    # /home/user/om-mirror 에 생성
# UPSTREAM_A = 1.12.13-release (e6c6650…)
# UPSTREAM_B = 1.13.0-release  (f329dd4…)
```

`tests/conftest.py`가 미러에서 실제 파일 blob을 온디맨드로 가져온다.

## 입력 파일

- **manifest**(커스터마이징 명세): `implementation.allowed/required_changed_paths`,
  `upgrade_watch.paths/configuration_keys/dependencies`, `assurance.contracts/direct_tests`,
  `series`. 스키마: `acgh/schema/manifest.schema.json`. **임의 shell 필드 없음**(P0-8).
- **patch-source-lock**: 고정 40-hex SHA만, series 순서(topological). 스키마:
  `acgh/schema/patch-source-lock.schema.json`.
- **정책**: `policies/repository-layout.yaml`(경로 소유), `policies/sensitive-zones.yaml`(민감영역).

## 출력 파일과 판정 상태

- **acgh-result**(불변 기계 판정): `acgh/schema/acgh-result.schema.json`.
  `result_digest`는 canonical payload의 SHA-256(관측 메타데이터 제외).
- **change-evidence**(감사카드): 게이트 집계 + 승인/LLM **분리** 필드.
- **판정 4상태**: `pass < approval < block < analysis_error`(severity 집계).
  exit: pass=0·block=1·approval=2·analysis_error=3. **분석 실패=차단**(fail-closed).

## 디렉터리 구조

```
harness/
  acgh/            # 구현 모듈(위 표)
    schema/        # JSON Schema(manifest·patch-lock·result·evidence)
  policies/        # repository-layout.yaml · sensitive-zones.yaml
  fixtures/        # fetch_upstream.sh · upstream-lock.yaml
  tests/           # 모듈별 테스트(conftest.py가 실제 미러 제공)
  pyproject.toml
```

## 개발·테스트 규칙

- 게이트/재적용 테스트는 **실제 OM 미러**로(합성 더미 금지). 순수 판정 로직
  단위 테스트는 최소 합성 픽스처 가능.
- 결정성: 같은 입력 → 같은 출력(git 환경 고정, pathspec factory=`gitignore` 고정).
- fail-closed: 검증 불가·미분류·빈 입력은 `analysis_error`(승인 불가).
- 커밋마다 트레일러 규칙 사용(루트 `SESSION_STATE.md` 참조).

## 문제 해결

- `ModuleNotFoundError: jsonschema/pathspec` → `pip install jsonschema pathspec`.
- 미러 의존 테스트가 skip → `bash fixtures/fetch_upstream.sh` 실행 후 재시도.
- 프록시/TLS 오류 → 루트 환경 안내(`/root/.ccr/README.md`) 참조.
