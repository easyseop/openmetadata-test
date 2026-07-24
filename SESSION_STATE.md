# 세션 상태 / 인수인계 (SESSION_STATE)

> **목적**: 컨텍스트가 리셋돼도 이 문서 하나로 작업을 이어갈 수 있게 현재까지의
> 모든 결정·산출물·다음 단계를 세세하게 기록한다. **작업 재개 시 이 문서를 먼저 읽는다.**
> 최종 갱신: 2026-07-24 T25 vendor ancestry 구현·검증 반영.

---

## 0. 지금 어디인가 (한 줄)

기존 patch-replay 중심 MVP1 모듈은 구현됐고, 운영 전략을 **vendor merge 기본 /
patch replay 선택 진단**으로 변경했다. T24 candidate-lock과 T25 ancestry까지
완료했으며 다음은 T26~T29와 실제
`kb_openmetadata` 커스터마이징 manifest·contract 등록이다.

## 1. 리포지토리·브랜치

- 작업 리포: `easyseop/openmetadata-test` (docs + 앞으로의 harness 코드)
- **작업 브랜치: `claude/markdown-file-feedback-26933w`** (여기에 계속 커밋·푸시)
- 커밋 작성자·도구 출처는 실제 작업 주체에 맞게 기록한다. 과거 세션이나 다른
  도구의 출처를 새 커밋에 복사하지 않는다.
- 푸시: `git push -u origin claude/markdown-file-feedback-26933w`
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
> **경로 이동/정리(2026-07-23)**: 문서는 `docs/` 하위 4분류 — 01-보고용
> (strategy_briefing)·02-설계(upstream_customization_design·governance_requirements)·
> 03-기술참조(verifier_catalog)·04-진행(build_plan·dev_roadmap). **검토이력(05)은
> 삭제됨.** 루트에는 README·EXECUTIVE_SUMMARY·SESSION_STATE만.

| `docs/01-보고용/openmetadata_strategy_briefing.md` | 왜 패치 스택인가 (경영진용, 정정 완료) | |
| `openmetadata_upstream_customization_design.md` | 상세 설계 (정정 완료) | |
| `openmetadata_governance_requirements.md` | **SRS — P0 9건 반영 + 부칙 A(2차 검토)** | **본문 충돌 시 부칙 A 우선** |
| `docs/04-진행/openmetadata_build_plan.md` | **순차 개발 실행 계획** — M0~M9, T01~T94 | 개발 스펙 정본 |
| `docs/04-진행/openmetadata_dev_roadmap.md` | **개발 로드맵 & MVP 커버리지 맵** — 진행 추적 | 커버리지 정본 |
| `docs/03-기술참조/openmetadata_verifier_catalog.md` | 검증기 22종(§0.1 구현현황) | |
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

## 6. 개발 순서 (2026-07-24 개정)

```
T24 integration_strategy/candidate-lock ✅
  → T25 vendor ancestry ✅
  → T26 customization survival ← 다음
  → T29 실제 kb_openmetadata manifest/contract
  → T27 merge conflict evidence
  → T60·T61 실제 기능 계약
  → T90·T91·T94

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

### 현재 위치 (2026-07-24, 최신)

**완료:** 기존 patch-replay M1~M4 + MVP2 Docker-free 다수.
**전략 변경:** vendor-merge를 기본으로 확정했고 T24 lock·T25 ancestry를 구현했다.
현재 테스트는 183개이며, 2026-07-24 임시 Python 3.12 환경에서 148개 통과,
실제 OpenMetadata 미러가 필요한 35개는 skip됐다.
- **T60** contract 카탈로그+결속 `contracts.py` · **T61** patch-kill
  `patchkill.py` · **T51/52** 구조화 diff `structdiff.py`(실제 table.json
  dataContract 검출) · **T70** 정책 self-protection `policy_guard.py` · **T43**
  부채 게이트 `debt.py`.
- **Docker 데몬 없음(이 세션)** → **T90 런타임 차등(구·신 OM 스택 기동)은 이후
  태스크로 보류**(compose·migration·CI 스크립트만 나중에 turnkey 준비).
- **남은 Docker-free**: T62 잔여(테스트결과↔SHA 결속·flaky 구분) · T91(digest
  승격 무결성) · T14(필수 테스트 존재) · T92(retirement) · T71/72(break-glass/
  fast-lane) · T80(LLM 위키, 자문). 그 다음 T90(Docker 필요).

> **T93/T42 라벨 정정(중요)**: build_plan 정본에서 **T42 = upgrade_watch(업스트림
> 변경 ∩ 감시 → 케이스 D)** = `upgrade_watch.py`+`impact.py`, **T93 = 정책 노후화
> drift(패턴이 신버전에 ≥1 매칭? 신규 미분류 모듈?)** = `policy_drift.py`. 초기
> 커밋들이 이 둘을 뒤바꿔 라벨링했으나 커밋 `21bfc15`에서 정정(기능은 둘 다 구현
> 완료). 검증기 카탈로그 §0.1에 전체 22개 구현현황표 있음.

| 태스크 | 상태 | 모듈 |
|---|---|---|
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

**커밋 SHA**: 스캐폴드 `7ccc00e` → `3cc0539`(T10/11/05) → `f38b124`(T15/14) →
`e5729dd`(T30/31) → `ee5a28e`(T20) → `da96332`(T21) → `47199cb`(T22) →
`febb929`(T23) → `cd1c9b5`(T40) → `03b05ff`(T62) → `90d09fe`(T32) →
`c5a0db5`(T33) → `cb52e76`(T41) (+ 사이사이 docs).

**환경 재현**: `pip install jsonschema pathspec`(pyproject deps 반영됨). 경로
문법 pathspec factory=`gitignore` 고정. 테스트: `cd harness && python -m pytest`
→ 80 통과. 실제 OM 콘텐츠는 `tests/conftest.py`가 미러에서 blob 온디맨드로
가져옴(미러 없으면 skip). `tests/test_reapply.py`는 실제 AuthLoginServlet.java를
공통 조상으로 케이스 B(clean)/C(conflict)/redundant 구성.

### 다음 태스크 — vendor-merge 기본 경로와 실제 커스터마이징 연결

1. T26: ID별 required state·path·contract 생존 검증
2. T29: 실제 변경 7종을 `BANK-OM-001~007`로 등록
3. T27: merge conflict evidence
4. T28: 기존 replay 모듈의 선택 모드 라우팅
5. 이후 API·DB·검색·권한·UI contract 테스트와 T90 연결

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
3. `cd harness && python -m pytest` → 현재 183개(148 pass·35 mirror skip) 재확인.
4. ✅ MVP1 완성(M1~M4, 케이스 A·B·C·D). 다음 = **MVP2(운영·승격)**: 계층3 테스트
   **T60**(contract↔test)·**T61**(patch-kill)·**T90**(업그레이드 차등 테스트) +
   계층4 **T70**(정책 base-평가)·**T91**(digest 승격). + 잔여 게이트 T43(부채)·
   T51/52(구조화 diff)·T80(범용 LLM Memo). 카탈로그 §0.1 구현현황표 참조.
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
