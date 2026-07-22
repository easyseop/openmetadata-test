# 세션 상태 / 인수인계 (SESSION_STATE)

> **목적**: 컨텍스트가 리셋돼도 이 문서 하나로 작업을 이어갈 수 있게 현재까지의
> 모든 결정·산출물·다음 단계를 세세하게 기록한다. **작업 재개 시 이 문서를 먼저 읽는다.**
> 최종 갱신: 개발 착수 직후(M0 fixtures 확보, T12·T13·T05 구현 진입).

---

## 0. 지금 어디인가 (한 줄)

문서 설계(전략→상세설계→SRS→GPT 1·2차 검토 반영→Build Plan→로드맵)가 **전부 완료·정합**
되었고, **실제 개발에 착수**한 상태. OpenMetadata OSS 미러 확보 완료, 이제 T12·T13·T05를 코딩한다.

## 1. 리포지토리·브랜치

- 작업 리포: `easyseop/openmetadata-test` (docs + 앞으로의 harness 코드)
- **작업 브랜치: `claude/markdown-file-feedback-26933w`** (여기에 계속 커밋·푸시)
- 커밋 트레일러(필수):
  ```
  Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01B41zjcR6R3bFtSdzAPuxoQ
  ```
- 푸시: `git push -u origin claude/markdown-file-feedback-26933w`
- PR은 사용자가 명시 요청 시에만 생성(아직 요청 없음).

## 2. 최종 목표 (변하지 않는 것)

공식 OpenMetadata 버전업 시 행내 커스터마이징을 **누락 없이·재현 가능하게·검증 가능하게
재적용**. 전략 = **패치 스택**(merge 아님, cherry-pick 재적용). 자동 검증은 "등록·재적용
완전성"까지 결정적 보장, "기능 의미"는 테스트·업그레이드 검증·운영 관찰로 잔여 위험 관리.
LLM은 배포 판정 배제(보조 Memo만).

## 3. 산출 문서 지도 (모두 커밋됨, 이 브랜치)

| 파일 | 역할 | 정본 우선순위 |
|---|---|---|
| `README.md` | 전체 개요·문서 지도·테스트 정책 | — |
| `openmetadata_strategy_briefing.md` | 왜 패치 스택인가 (경영진용, 정정 완료) | |
| `openmetadata_upstream_customization_design.md` | 상세 설계 (정정 완료) | |
| `openmetadata_governance_requirements.md` | **SRS — P0 9건 반영 + 부칙 A(2차 검토)** | **본문 충돌 시 부칙 A 우선** |
| `openmetadata_review_response.md` | GPT 1차 검토 판정(A~F) + 추가발견 6건 | |
| `openmetadata_second_review_request.md` | GPT 2차 검토 요청문 | |
| `openmetadata_governance_second_review_gpt.md` | **GPT 2차 검토 결과(업로드본)** — ⚠아직 repo에 없을 수 있음, 사용자 업로드 파일 | |
| `openmetadata_second_review_response.md` | 2차 검토 전면 수용·반영 내역 | |
| `openmetadata_build_plan.md` | **순차 개발 실행 계획(2차 반영 개정판)** — M0~M9, T01~T94 | 개발 스펙 정본 |
| `openmetadata_dev_roadmap.md` | **개발 로드맵 & MVP 커버리지 맵** — 진행 추적 | 커버리지 정본 |
| `openmetadata_verifier_catalog.md` | 검증기 22종(뭘 잡나·막는 사고·태스크) | |
| `openmetadata_review_packet.md` | 대화 요약(GPT 1차 전달용) | |

> **정본 우선순위(충돌 시)**: SRS 부칙 A > review_response > build_plan > SRS 본문.

## 4. 확정된 핵심 결정 (재론 불필요, 전부 합의됨)

- 패치 스택(merge 아님). 충돌은 "겹침"이 만들며 코어 수정에서만 발생 → 코어 최소화(4단계 관문).
- 불변 ID `BANK-OM-xxx`, 1커밋=1ID, 1ID=순서형 series 허용.
- 고정 SHA **patch-lock**(동적 "최신 브랜치" 금지). source lock/application lock **분리**.
- **verdict 4상태**: `pass<approval<block<analysis_error`(severity rank로 집계, exit는 0/2/1/3
  으로 **마지막 1회 변환**). analysis_error=차단(승인 우회 불가). exit `max()` 집계 금지(P0-3).
- **등록·재적용 완전성 ≠ 기능 완전성**(문구 분리). ID 집합 일치는 등록 존재만 증명.
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

## 6. 개발 순서 (권장 핵심 경로)

```
T01~T05  →  T10·T12·T13·T15·T14·T11  →  T30·T31(preflight)  →  T20·T21·T23·T22
  →  T40·T62·T32·T33·T41  →  T93→T42+T50  →  T60·T61  →  T70·T72  →  T90→T91→T94
T51·T52 병행 · T80·T81 마지막
```
- **즉시 착수 가능(의존 없음)**: T12(git 프리미티브)·T13(verdict 엔진).
- **동결 대기**: T10(스키마)·T11(patch-lock)은 부칙 A 반영 후.
- 신규 태스크: T05(path-ownership), T15(result/CI adapter), T23(resolve 직렬화).
- MVP1(Candidate-control): T01~T05·T10~T15·T30·T31·T20~T23·T40·T41·T62·T32·T33·T93·T42·T50·T70최소.
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

## 9. 지금 진행 중인 코드 작업 (다음에 이어서 할 것)

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

1. 이 파일(SESSION_STATE.md) + `openmetadata_build_plan.md` + SRS 부칙 A 읽기.
2. `/home/user/om-mirror` 존재 확인(없으면 §7 명령으로 재획득).
3. `harness/` 존재 확인 → 없으면 §9 스캐폴딩부터, 있으면 미완 태스크 이어서.
4. T12·T13 구현→`pytest` 통과 확인→커밋. 이후 T05→T30/T31 순.
5. 각 태스크 완료 시 `openmetadata_dev_roadmap.md` §4 체크리스트 갱신.
6. 커밋마다 §1 트레일러 사용, 이 브랜치로 push.
