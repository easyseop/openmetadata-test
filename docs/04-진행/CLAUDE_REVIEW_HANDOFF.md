# Claude 독립 검토 인수인계

> 작성일: 2026-07-27
> 대상 브랜치: `claude/markdown-file-feedback-26933w`
> 변경 전 기준 커밋: `9d2a174` (`implement T25 vendor ancestry gate`)
> 마지막 검증 구현 커밋:
> `b1d3fa6d00b75c96d837587ea0730f3d6d9e5323`
> 최신 문서 묶음 커밋:
> `a71509295bdb1f5d7b0a74df0e398e514143ca19` (원격 증적 동기화 직전)
> T63 UI typecheck 기준선 게이트 구현 커밋:
> `39294bf38172f16528833640c03302aa83ade7b4`
> 제품 UI 타입 보강 커밋:
> `ddf0dd2ebaf50bc0aa97143a5e97312bc27bd91d`
> 공통 검색 결과 타입 보강 제품 커밋:
> `70d028a035bb1edb8af5a11f06c4c7dff4cd979b`
> BANK-OM-009 거버넌스 등록 / evidence 재결속:
> `4353f457ca93710f71b08f8c5c6365a33fb3f7d8` /
> `89763f3952868da27af9f8bcc688a34e593da4da`
> 알림 엔터티 ID 검색 안전성 보강 제품 커밋:
> `b80d24d83124435733d5af05d56515b3a855330e`
> BANK-OM-010 거버넌스 등록 / evidence 재결속:
> `d70fe810b65f44b20e79dca7bcdb697f806d99f7` /
> `5e6d0a8`
> 검색 목록 변환 타입 계약 제품 커밋:
> `849ae756cd238f218b5e3a6c795a392305cb32ee`
> BANK-OM-011 거버넌스 등록 / evidence 재결속:
> `b1d3fa6d00b75c96d837587ea0730f3d6d9e5323` /
> `c246ae29e56f51a131c9b5752e901209b0062b06`
> BANK-OM-011 증적 분류·문서 커밋:
> `a71509295bdb1f5d7b0a74df0e398e514143ca19`
> Data Assertions·bank column 실제 화면 계약 보강 커밋:
> `093724faa499458eb4723511914a1376138ef014`
> T61 deployed runtime patch-kill 게이트 구현 커밋:
> `1956b7880506674e37ad2428248a9fc69817dbc2`
> 비개발자 가이드·인수인계 구현 커밋:
> `0f0904b47c08c1febf95d17e2c7364adf01e3b98`
> T62 runtime 계약 게이트 구현 커밋:
> `b29d0ceea3b8b95423242847b0c172415f420411`
> T62 운영 문서·가이드 동기화 커밋: `a291f31`
> T62 CI evidence 90일 보존 구현 커밋:
> `502f42f77734ec4f894aa79360c22e0f67dc1b19`
> T61 source patch-kill 구현 커밋:
> `a2cbb5221f50c10d11af26618d1d310ec8a73552`
> T61 infra_error 분리·고정 증거 검증 커밋:
> `7a2fb5f12af758805cc21abaabb4cb29f1f82dcb`
> artifact action Node 24 전환 커밋:
> `8ec6e28442c1ed483bb2f1c39c0a6d628f1d213d`
> 현재 커밋은 체크아웃 후 `git rev-parse HEAD`로 확인한다.

## 0. 지속 갱신 규칙

이 문서는 한 번 작성하고 끝내는 보고서가 아니라 Claude 또는 다음 작업자가 즉시
개발을 이어받기 위한 살아 있는 인수인계서다.

### 0.1 갱신 시점

다음 시점마다 반드시 갱신한다.

1. 개발 태스크 또는 함께 검증할 수 있는 작업 묶음을 완료했을 때
2. 테스트 수, skip 사유, source SHA, blocker 또는 설계 결정이 바뀌었을 때
3. commit/push 직전 또는 직후 문서와 구현의 상태가 달라졌을 때
4. 작업 주체를 바꾸거나 대화 컨텍스트·토큰이 부족해지기 전

가능하면 코드와 인수인계 문서를 같은 commit에 넣는다. 그러지 못했다면 바로 다음
문서 전용 commit으로 동기화하고 push 여부를 명시한다.

### 0.2 인수인계 문서 경로와 역할

| 경로 | 역할 | 갱신 조건 |
|---|---|---|
| `CLAUDE.md` | Claude 진입점, 읽기 순서, 검토·유지 규칙 | 규칙 또는 검토 범위 변경 |
| `docs/00-사용가이드/비개발자_사용_가이드.md` | 쉬운 상태 해석·업무 입력·운영 시나리오 | 사용자 노출 상태·용어·절차 변경 |
| `STATUS.md` | 가장 짧은 현재 상태와 blocker | 모든 완료 작업 묶음 |
| `docs/04-진행/CLAUDE_REVIEW_HANDOFF.md` | 구현 방식·검증·한계·다음 단계 상세 | 모든 완료 작업 묶음 |
| `SESSION_STATE.md` | 장기 결정과 과거 맥락 | 재개에 필요한 장기 맥락 변경 |
| `docs/04-진행/openmetadata_dev_roadmap.md` | T번호별 진행 상태 | 태스크 상태 변경 |
| `docs/04-진행/openmetadata_build_plan.md` | 구현 계약과 순서의 정본 | 스펙 또는 순서 변경 |

### 0.3 완료 작업마다 남길 내용

- 브랜치와 인수인계 대상 구현 commit
- 완료한 T번호와 사용자에게 보이는 결과
- 변경 파일, 핵심 함수/스키마, 구현 방식과 선택 이유
- 실행한 정확한 검증 명령과 pass/fail/skip 수, skip 사유
- 구현한 판정 계약과 실제 운영에서 실행한 증거의 명확한 구분
- 미완료 작업, blocker, 가정, 결정이 필요한 owner
- worktree clean 여부, commit 여부, 원격 push 여부
- 다음 작업자가 바로 실행할 수 있는 첫 단계 또는 명령

비밀값, 접근 토큰, 개인 키, 임시 승인 정보는 기록하지 않는다. 완료 표시와 실제
코드·테스트가 다르면 완료로 추정하지 않고 인수인계를 미완료 상태로 취급한다.

### 0.4 비개발자 가이드 동기화 계약

`docs/00-사용가이드/비개발자_사용_가이드.md`는 비개발자가 코드를 읽지 않고
현재 상태와 해야 할 일을 판단하는 정본이다. 다음이 바뀌면 같은 개발 묶음에서
반드시 함께 갱신한다.

- 사용자에게 보이는 상태, 화면, 결과 문구
- 업무 담당자가 제출해야 하는 정보
- 승인, 긴급 변경, 테스트, 배포 순서
- `pass`, `approval`, `block`, `analysis_error`, `skip`의 의미
- 새 기능, 새 게이트, 새 운영 blocker

가이드는 source-only CI 성공을 배포 가능으로 표현하면 안 된다. 구현된 계약,
실제로 실행된 운영 증거, 남은 skip과 blocker를 항상 분리한다.

## 1. 최종 목적

공식 OpenMetadata 버전업 때 행내 커스터마이징을 사람 기억이나 LLM의 낙관적
판단에 의존하지 않고 다음 순서로 통제하는 것이 최종 목적이다.

1. 공식 upstream target SHA를 vendor branch의 실제 조상으로 보존한다.
2. 모든 행내 변경을 안정적인 `BANK-OM-nnn` ID, manifest, owner, contract로
   등록한다.
3. candidate에서 각 변경의 required path와 contract 결속이 살아 있는지
   결정적으로 검사한다.
4. 실제 기능 테스트를 candidate commit SHA, 이미지 digest, harness/suite
   version에 결속한다.
5. DB migration, 재색인, ingestion, 인증·권한·API·관계·검색의 구/신 버전 차등
   테스트로 기능 의미를 확인한다.
6. 검증한 동일 commit과 artifact/image/Helm digest만 재빌드 없이 승격한다.
7. 내부망 반입 때 파일 해시, release-lock, 오프라인 서명을 다시 검증한다.
8. LLM은 근거 있는 영향 후보와 테스트 제안만 작성하며 verdict나 배포 권한을
   갖지 않는다.

즉, 목표는 “코드가 컴파일된다”가 아니라 **등록된 수정이 누락 없이 살아 있고,
명시한 업무 불변식이 실제로 동작하며, 검증한 바로 그 바이트가 배포된다**는
연쇄 증거를 만드는 것이다.

## 2. 정본과 신뢰 경계

충돌 시 우선순위는 다음과 같다.

1. `docs/02-설계/ADR-001-vendor-merge-default.md`
2. `docs/04-진행/openmetadata_build_plan.md`
3. `harness/acgh/schema/*.schema.json`과 각 모듈의 의미 검증
4. immutable candidate/test/release/transfer lock과 machine result
5. 사람 승인 attestation
6. LLM Impact Memo

사람 승인과 LLM 메모는 machine result를 수정하지 않는다.
`analysis_error`는 “검사가 실패했다”가 아니라 “검사를 신뢰할 수 없다”는 뜻이며
가장 높은 심각도로 집계한다.

## 3. 실제 소스 비교에서 확인한 사실

비교 대상:

| 항목 | 값 |
|---|---|
| 행내 스냅샷 저장소 | `kangdkdk/kb_openmetadata` |
| 행내 스냅샷 SHA | `2c2347043235aa2a4ecba4729774c770fcee5d67` |
| 공식 저장소 | `open-metadata/OpenMetadata` |
| 공식 기준 태그 | `1.13.1-release` |
| 공식 기준 SHA | `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9` |
| 공식 기준 대비 변경 경로 | 113개 |
| upstream ancestry 보존 | **아니오** |

`kb_openmetadata`는 한 개의 root commit으로 만든 소스 스냅샷이다. 공식
`1.13.1-release`를 부모로 갖지 않으므로 현재 상태는 T29 인벤토리 입력으로는
사용할 수 있지만, T25 vendor ancestry를 통과할 수 없다.

이 사실을 숨기지 않기 위해
`harness/registrations/kb-openmetadata/customization-registry.yaml`의
`source.ancestry_preserved`를 `false`로 기록했다.

113개 변경 경로 중 111개는 다음 일곱 제품 기능군으로 등록했다.

| ID | 기능 | criticality | 현재 owner |
|---|---|---:|---|
| `BANK-OM-001` | InstanceCode | high | `UNASSIGNED` |
| `BANK-OM-002` | QueryReport | high | `UNASSIGNED` |
| `BANK-OM-003` | Data Assertions | high | `UNASSIGNED` |
| `BANK-OM-004` | 은행 컬럼 확장 표시 | medium | `UNASSIGNED` |
| `BANK-OM-005` | 한글 IME 조합 입력 보정 | medium | `UNASSIGNED` |
| `BANK-OM-006` | Sybase connector | high | `UNASSIGNED` |
| `BANK-OM-007` | Tibero connector | high | `UNASSIGNED` |

`BANK-OM-005`는 `SchemaEditor.tsx`의 composition start/end 상태를 사용해
CodeMirror controlled value 갱신 중 한글 자모가 깨지는 것을 방지하는 변경으로
확인했다.

나머지 2개는 제품 기능에 억지로 귀속하지 않고 registry의 명시적 차단 이슈로
기록했다.

| 경로 | 분류/심각도 | 확인한 변경 | 현재 disposition |
|---|---|---|---|
| `.claude/settings.json` | governance/critical | 질문·plan exit 자동 승인과 광범위한 Bash/Edit/Write/Web/MCP allow 추가 | block |
| `docker/development/docker-compose.yml` | deployment/high | ingestion 로컬 빌드를 끄고 `openmetadata/ingestion:1.9.6` 사용 | block |

## 4. 이번 변경에서 구현한 내용

### 4.1 T26 — customization survival

파일:

- `harness/acgh/survival.py`
- `harness/tests/test_survival.py`

개발 방식:

- vendor-merge 모드인지 먼저 확인한다.
- candidate-lock의 target/candidate 객체가 실제 Git 저장소에 존재하는지 확인한다.
- 모든 active ID에 manifest가 있는지 확인한다.
- 각 manifest의 `required_changed_paths`가 candidate tree에 존재하고 공식 target과
  실제로 다른지 확인한다.
- registry ↔ manifest ↔ contract의 정방향/역방향 결속과 effective test 집합을
  확인한다.
- 객체 누락이나 stale binding은 `analysis_error`, 신뢰 가능한 생존 누락은
  `block`으로 분리했다.

검토 포인트: “required path가 존재하지만 기능이 무효화된 경우”는 이 게이트의
보장 밖이며 T61 patch-kill과 실제 contract test가 담당한다.

### 4.2 T27 — merge conflict evidence

파일:

- `harness/acgh/conflicts.py`
- `harness/acgh/schema/merge-conflict-evidence.schema.json`
- `harness/tests/test_conflicts.py`

개발 방식:

- `git ls-files -u -z`를 사용해 충돌 경로와 stage 1/2/3 blob을 줄바꿈 안전하게
  수집한다.
- 해결 기록에 rationale, resolver, approval IDs, resolved blob을 넣는다.
- 기록 전체를 candidate-lock에 결속한다.
- malformed/stale 증거는 `analysis_error`, 충돌 개수 불일치는 `block`, 승인 ID가
  빠진 해결은 `approval`로 판정한다.

### 4.3 T28 — vendor/replay 명시 라우팅

파일:

- `harness/acgh/routing.py`
- `harness/tests/test_routing.py`

개발 방식:

- 모든 전략의 common gates와 전략별 gates를 분리했다.
- vendor merge는 ancestry, survival, merge-conflict evidence를 요구한다.
- patch replay는 patch-lock, reapply, clean-room replay, integrator CAS를
  요구한다.
- 필요한 gate가 runner에 없으면 통과가 아니라 `analysis_error`다.

이 분리는 vendor candidate에 patch-lock이 없다는 이유만으로 잘못 차단하거나,
cherry-pick 성공만으로 vendor release 전체가 완성됐다고 오인하는 문제를 막는다.

### 4.4 T29 — 실제 7개 등록부

파일:

- `harness/registrations/kb-openmetadata/customization-registry.yaml`
- `harness/registrations/kb-openmetadata/contracts.yaml`
- `harness/registrations/kb-openmetadata/manifests/BANK-OM-001.yaml` ~
  `BANK-OM-007.yaml`
- `harness/acgh/registry.py`
- `harness/acgh/schema/customization-registry.schema.json`
- `harness/tests/test_registry.py`

개발 방식:

- 실제 113개 변경 경로를 고정 목록으로 저장하고, 111개가 일곱 기능 manifest에
  포괄되며 나머지 2개가 explicit blocking finding인지 자동 검사한다.
- 각 ID에 최소 한 개의 업무 불변식 contract와 required test ID를 연결했다.
- registry, manifest, contract catalog가 닫힌 그래프인지 양방향으로 검사한다.
- manifest와 registry의 lifecycle status도 일치시킨다.
- snapshot/upstream SHA와 변경 경로 수를 테스트에서 고정했다.

required test ID 7개는 이제 `tests/bank/contracts/`의 실제 Python selector에
연결된다. T60-I는 경로 이탈·symlink·파일 누락·AST symbol 누락을 차단한다.
다만 구현 존재는 실행 성공과 다르며, live API 4개와 browser 3개 결과는
T62 candidate-bound pass가 생길 때까지 운영 증거가 아니다.

### 4.5 T62 — 필수 테스트 실행과 candidate 결속

파일:

- `harness/acgh/testruns.py`
- `harness/acgh/schema/test-run-set.schema.json`
- `harness/tests/test_testruns.py`

개발 방식:

- test-run set을 candidate commit SHA, artifact digest, harness version,
  suite version에 결속한다.
- active manifest의 contract-derived/direct effective test가 0개면 차단한다.
- 필수 테스트 결과가 없거나 skipped/fail/error면 차단한다.
- 재시도 이력을 attempt 1부터 연속적으로 보존한다.
- high/critical 테스트의 fail/error 후 retry-pass는 일반 성공으로 뭉개지 않고
  `approval`로 올린다.
- candidate나 도구 버전이 바뀐 과거 결과는 `analysis_error`로 무효화한다.

### 4.6 T71 — 변경 유형별 fast lane

파일:

- `harness/acgh/fastlane.py`
- `harness/tests/test_fastlane.py`

개발 방식:

- config, deployment, extension, governance의 최소 gate 집합을 코드 상수로
  고정했다.
- core-patch는 T28의 전체 전략별 gate plan으로 확장한다.
- 여러 변경 유형이 섞이면 가장 쉬운 lane을 고르는 대신 필요한 gate의 합집합을
  적용한다.
- 누락 gate는 `analysis_error`다.

### 4.7 T72 — break-glass

파일:

- `harness/acgh/breakglass.py`
- `harness/acgh/schema/break-glass-attestation.schema.json`
- `harness/tests/test_breakglass.py`

개발 방식:

- 티켓, 요청자, 서로 다른 두 승인자, result digest, candidate SHA, policy digest,
  허용 gate, 요청/만료/사후검증 시각, 사유를 strict schema로 요구한다.
- 요청자는 승인자 수에 포함할 수 없다.
- candidate-lock, test-candidate-binding, verdict/artifact/release digest 같은
  무결성 gate는 예외 대상으로 선언할 수 없다.
- stale/형식 오류는 `analysis_error`, 만료·종료·범위 밖 요청은 `block`이다.
- 유효하더라도 별도 예외 기록의 유효성만 pass하며 원 machine verdict는 바꾸지
  않는다.
- active/expired/closed/invalid 통계를 별도로 집계한다.

### 4.8 T80/T81 — LLM Impact Memo와 품질 지표

파일:

- `harness/acgh/impact_memo.py`
- `harness/acgh/schema/impact-memo.schema.json`
- `harness/tests/test_impact_memo.py`

개발 방식:

- 모듈은 모델, shell, Git writer, PR API, network client를 호출하지 않는다.
- snapshot SHA, input digest, model ID, prompt version을 기록한다.
- 사실과 추론을 분리하고 모든 주장에 동일 snapshot의 evidence provider/reference를
  최소 한 개 요구한다.
- strict schema가 verdict, command, deployment action 필드를 거부한다.
- “영향 없음/no impact” 표현을 거부하고 “확인된 후보 없음 + 미확인 사항”을
  사용하게 한다.
- T14 카드에는 기존 `llm_suggestions` 형식의 요약만 넣으므로 machine verdict가
  변하지 않는다.
- recall, false-positive rate, reviewer adoption rate, ungrounded claim rate를
  계산한다.

별도 LLM Wiki는 아직 필요조건이 아니다. Git/YAML/contract/test/ADR가 먼저
신뢰 가능한 관계 그래프가 되어야 하며, Wiki는 이 정본에서 생성되는 검색·온보딩
레이어여야 한다.

### 4.9 T90 — 업그레이드 테스트 오케스트레이션 결과 계약

파일:

- `harness/acgh/upgrade_run.py`
- `harness/acgh/schema/upgrade-test-run.schema.json`
- `harness/tests/test_upgrade_run.py`

개발 방식:

- 실제 executor가 반드시 내야 할 12단계를 고정했다: 운영 스냅샷 복원,
  migration, 건수 대사, reindex, ingestion, 인증·권한·API·관계·검색·ingestion
  차등, rollback drill.
- 각 단계는 pass/fail/error/skipped와 evidence digest를 기록한다.
- 단계 누락 또는 pass 외 결과는 `block`이다.
- 전체 기록을 candidate SHA/artifact와 T62 test-run-set digest에 결속한다.
- 단계 직렬화 순서와 무관한 canonical digest를 만든다.

구현한 것은 **판정 계약**이다. 이 세션에는 Docker daemon, 운영 유사 DB snapshot,
검색/ingestion 인프라가 없어서 12단계를 실제 실행하지 않았다.

### 4.10 T91 — 동일 digest 승격

파일:

- `harness/acgh/release.py`
- `harness/acgh/schema/release-lock.schema.json`
- `harness/tests/test_release.py`

개발 방식:

- release-lock에 candidate repository/commit/tree/artifact/candidate-lock digest,
  core/platform SHA, policy/catalog digest, harness/suite version, source result,
  test-run-set, image/Helm digest, approval IDs를 결속한다.
- machine result가 block/analysis_error면 release-lock을 만들 수 없다.
- approval result는 approval ID가 없으면 만들 수 없다.
- candidate artifact digest는 승격 이미지 집합에 실제로 포함돼야 한다.
- observed candidate/image/Helm이 다르거나 재빌드했다면 `block`이다.
- current candidate/result/test가 lock과 달라지면 stale `analysis_error`다.

### 4.11 T92 — retirement

파일:

- `harness/acgh/retirement.py`
- `harness/acgh/schema/retirement-record.schema.json`
- `harness/tests/test_retirement.py`
- manifest schema의 `status`

개발 방식:

- 공식 대체 commit/reference, ADR, 제거 candidate/result, contract test-run-set,
  공식 대체 확인, 필수 테스트, 제거 회귀, active effect 부재, 2인 승인을 요구한다.
- stale candidate/test 증거는 `analysis_error`다.
- 검증 후 registry와 manifest 복사본을 `active → retired`로 함께 전환한다.
- 빈 placeholder commit을 유지하는 방식은 사용하지 않는다.

### 4.12 T94 — 내부망 반입

파일:

- `harness/acgh/airgap.py`
- `harness/acgh/schema/airgap-manifest.schema.json`
- `harness/tests/test_airgap.py`

개발 방식:

- git bundle, image, Helm, configuration, release-lock 등의 상대 경로, 크기,
  SHA-256을 inventory로 고정한다.
- release-lock digest와 source commit을 signed payload에 포함한다.
- 해시 payload를 만든 뒤 별도 signature를 검증하는 순서를 강제한다.
- 절대경로, `..`, 중복 경로, signature를 signed file 목록에 넣는 순환 구조를
  거부한다.
- 내부망 파일의 size/hash를 다시 계산한다.
- 조직의 오프라인 signature verifier를 주입하지 않으면 unsigned pass가 아니라
  `analysis_error`다. 서명 실패는 `block`, verifier 고장은 `analysis_error`다.

### 4.13 T25-R — ancestry 없는 snapshot의 vendor 재구성 검증

파일:

- `harness/acgh/vendor_rebuild.py`
- `harness/tests/test_vendor_rebuild.py`
- `harness/registrations/kb-openmetadata/shared-path-owners.yaml`
- `harness/pyproject.toml`의 `acgh-vendor-rebuild` CLI

개발 이유:

기존 T25는 완성된 candidate가 공식 target을 ancestry에 포함하는지만 검사한다.
하지만 현재 `kb_openmetadata`는 unrelated root snapshot이므로, snapshot commit을
공식 branch에 억지로 merge하면 ancestry 검사만 형식적으로 만족시키는 잘못된
candidate가 생길 수 있다. 또한 여러 기능이 함께 수정한 파일을 첫 번째로 일치한
manifest에 통째로 귀속하면 기능별 커밋 이력이 거짓이 된다.

개발 방식:

- 공식 upstream SHA와 snapshot SHA의 실제 tree diff가 등록한 113개 inventory와
  정확히 같은지 먼저 확인한다. 객체 누락이나 inventory drift는
  `analysis_error`다.
- 실제 등록부 기준 113개 경로를 결정적으로 **67개 단독 소유, 44개 공유,
  2개 제외**로 분류한다. 계획 digest는
  `sha256:ceaea84c3feb370e638d24322c9a2747b69dbfeef789eeeaba8e73b7aaf96699`다.
- 공개 원격에서 두 commit/tree를 blob 최소화로 가져와 실제 `plan`을 실행했고,
  `source_path_count=113`과 위 digest로 `pass`를 확인했다.
- `.claude/settings.json`과
  `docker/development/docker-compose.yml`은 reconstructed candidate에서 공식
  upstream content 그대로여야 한다.
- 공유 44개 파일의 실제 추가 symbol·JSON key·route·SQL block을 검사해
  `shared-path-owners.yaml`을 채웠다. broad manifest와 달리 실제 snapshot
  변경이 Sybase뿐인 generated file은 `BANK-OM-006`만 owner로 기록했다.
- shared path touch 수는 `BANK-OM-001=32`, `002=32`, `003=21`, `004=19`,
  `006=12`, `007=5`이며 빈 owner 목록은 0개다. `BANK-OM-005`는 IME 단독
  파일만 변경하므로 shared 목록에 없다.
- 19개 비영어 locale JSON은 기능 key 추가와 file-wide 들여쓰기 변경이 함께
  있었다. 포맷 노이즈를 기능 commit에 강제로 복제하지 않도록 JSON은 파싱한
  의미 값으로 비교하고, Java/TS/SQL 등 나머지 파일은 byte content를 비교한다.
- 빈 owner 목록, 후보 밖 ID, 잘못된 자료형은 통과하지 않는다.
- candidate가 공식 target의 descendant인지, unrelated snapshot commit을
  ancestry에 포함하지 않는지 검사한다.
- target..candidate의 모든 commit은 `Customization-ID`가 정확히 하나여야 하며,
  해당 manifest와 명시한 path owner 범위 안에서만 변경해야 한다.
- candidate의 registered JSON 의미와 나머지 path content는 snapshot과 같고,
  제외 path는 upstream과 같은지 재검증한다. 중간에 금지 경로를 수정했다가
  되돌리는 경우도 per-commit touched path 검사로 차단한다.

CLI:

```bash
acgh-vendor-rebuild \
  --repo /path/to/object-complete-repo \
  --registration harness/registrations/kb-openmetadata \
  plan

acgh-vendor-rebuild \
  --repo /path/to/object-complete-repo \
  --registration harness/registrations/kb-openmetadata \
  verify \
  --candidate <full-candidate-sha> \
  --shared-owners harness/registrations/kb-openmetadata/shared-path-owners.yaml
```

planner, 실제 source plan, 44개 shared owner map, candidate verifier까지 완료한
뒤 아래 4.14의 실제 7-ID vendor branch도 생성·검증했다.

### 4.14 실제 7-ID vendor candidate 재구성

제품 저장소:

- fork: `easyseop/OpenMetadata`
- branch: `codex/bank-vendor-1.13.1-rebuild`
- 공식 parent: `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9`
- reconstruction checkpoint: `e1ffc5a1eb270c3225736544bb309a0c85af6d2c`
- tree: `4ac7817d9e495edc14fcfae5af0382f839a098a3`

재현·증거 파일:

- `harness/registrations/kb-openmetadata/reconstruct_series.py`
- `harness/registrations/kb-openmetadata/run_source_candidate_gates.py`
- `harness/registrations/kb-openmetadata/source-candidate-evidence.yaml`

개발 방식:

1. GitHub의 공식 `open-metadata/OpenMetadata`를 `easyseop/OpenMetadata`로
   fork했다.
2. 공식 `1.13.1-release` SHA를 정확한 부모로
   `codex/bank-vendor-1.13.1-rebuild` 브랜치를 만들었다.
3. unrelated root snapshot commit은 merge하지 않고, 등록된 111개 product
   path의 content만 source evidence로 사용했다.
4. 단독 소유 path는 manifest owner commit에 복사하고, shared path는
   `shared-path-owners.yaml` 순서대로 실제 source hunk를 단계적으로 적용했다.
5. locale JSON 19개는 snapshot의 file-wide 들여쓰기 변경을 복제하지 않고
   `BANK-OM-001`~`004`의 semantic key additions만 owner별로 넣었다.
6. `.claude/settings.json`과 `docker/development/docker-compose.yml`은 후보에
   넣지 않아 공식 upstream content를 유지했다.
7. 모든 commit에 정확히 하나의 `Customization-ID` trailer를 넣었다.

커밋:

| ID | commit | touched paths | 내용 |
|---|---|---:|---|
| BANK-OM-001 | `a2566fac322c` | 48 | InstanceCode |
| BANK-OM-002 | `4108411cd5bc` | 55 | QueryReport |
| BANK-OM-003 | `39016640b5fc` | 25 | Data Assertions |
| BANK-OM-004 | `c87877116280` | 33 | 은행 컬럼 확장 표시 |
| BANK-OM-005 | `6e5b654f84ec` | 1 | 한글 IME |
| BANK-OM-006 | `41b224adbd7e` | 18 | Sybase |
| BANK-OM-007 | `e1ffc5a1eb27` | 8 | Tibero |

실제 candidate 검증:

```text
T25-R vendor-reconstructed-candidate  pass
  registered_paths=111
  excluded_paths=2
  plan_digest=sha256:ceaea84c3feb370e638d24322c9a2747b69dbfeef789eeeaba8e73b7aaf96699
T25 vendor-ancestry                  pass
T26 customization-survival           pass
  7 active IDs, 10 required paths, 7 contracts, 7 effective test IDs
T30 commit-invariants                pass
T31 id-invariants                    pass
```

reconstruction checkpoint의 source candidate-lock digest는
`sha256:fb05306222a64581d5aea6894fb8c99dd9fb4080ac2bb89f66f31ee1078243c4`다.
그 lock의 artifact digest는 source Git tree identity를 결속한다. 아직 Java/UI
binary, container image 또는 release package digest를 뜻하지 않는다.

### 4.15 BANK-OM-007 Tibero 후속 보강

7-ID snapshot 재구축은 `e1ffc5a1...`에서 고정했다. 이후 제품 정적 검토에서
Tibero가 아래 위치에는 이미 존재함을 확인했다.

- database service JSON schema와 generated `DatabaseServiceType`
- create service/API model과 `DatabaseServiceUtils.tsx` selector
- connector JSON schema와 service icon

하지만 공통 generated service connection의 `ConfigType`에는 `Tibero`가
빠져 있었고, `getDatabaseConfig(DatabaseServiceType.Tibero)`가 Tibero JSON
schema를 반환한다는 집중 단위 테스트도 없었다. 이 상태는
`CONTRACT-TIBERO-CONNECTOR`의 create UI/API/serviceConnection union 일관성
요건을 충분히 고정하지 못한다.

연속 ID series를 허용한 `BANK-OM-007`의 후속 커밋으로 다음을 보강했다.

| commit | ID | 변경 경로 | 구현 |
|---|---|---|---|
| `38bccf90779a` | BANK-OM-007 | `openmetadata-ui/src/main/resources/ui/src/generated/entity/services/connections/serviceConnection.ts` | `ConfigType.Tibero = "Tibero"` 추가 |
| `38bccf90779a` | BANK-OM-007 | `openmetadata-ui/src/main/resources/ui/src/utils/DatabaseServiceUtils.test.tsx` | Tibero JSON schema·공통 UI schema 반환 단위 테스트 추가 |

Tibero 보강 직후 source candidate(현재 후보의 직전 조상):

- commit: `38bccf90779a8afe4a4f0e9313e11706f6d940d4`
- governance evidence commit: `efd7615470311feb58f1523fb4305561c53410b0`
- tree: `3bfaf8b982c967af764cfbfdfe318b54f4ae9f28`
- source tree digest:
  `sha256:d7efa79efcc700bf05aa8d54070c551954ae2b4a29aac40fb9df5c94a71bd907`
- candidate-lock digest:
  `sha256:9f2e3760b7b1ab44fa24fe8872c74b4003dcf29dbdc7282e403f2595b7ebeacd`

현재 source candidate와 새 lock은 §4.29의 `849ae756...` 및
`source-candidate-evidence.yaml`을 정본으로 사용한다.

후속 candidate 검증:

```text
T25 vendor-ancestry          pass
T26 customization-survival   pass
T30 commit-invariants        pass
T31 id-invariants            pass
```

T25-R은 snapshot과 정확히 같은 재구축 결과만 판정하므로 새 보강 commit이 아닌
checkpoint `e1ffc5a1...`에 계속 결속한다. UI source tree는 `git diff --check`와
schema/type/reference 정적 검사를 통과했다.

실제 UI 집중 검증을 위해 sparse checkout에 UI, UI core, JSON schema, ANTLR
grammar만 materialize했다. 잠금 파일 기준 의존성을 설치하고 공식
`parse-schema`, ANTLR 4.9.2 생성, UI core build를 수행한 뒤 Jest를 실행했다.

```text
Prettier, changed 2 paths                    pass
DatabaseServiceUtils.test.tsx                pass
  test suites                               1/1
  tests                                     13/13
  Tibero schema mapping                     pass
UI tsc --noEmit, 6 GB heap                   fail
  total diagnostics                         399
  diagnostics matching changed 2 paths       0
UI core Vite build                           exit 0
  declaration diagnostics                    2
  candidate changes under UI core            0 paths
```

첫 typecheck는 기본 2GB heap에서 OOM이었고, 프로젝트 build와 같은 6GB로
재실행해 실제 diagnostic을 얻었다. UI core의 두 TS2741은 candidate가 건드리지
않은 upstream 경로에서 발생했다. 전체 UI typecheck의 399개 오류도 변경 두
경로와 직접 매칭되지 않았지만, 이 사실은 broad baseline이 green이라는 뜻이
아니다. release blocker로 유지한다.

환경에는 Node 22가 없어 Node 24.15.0·Yarn 1.22.22로 실행했고, 한 dependency의
engine 상한 때문에 설치에 `--ignore-engines`를 사용했다. Claude는 지원되는
Node 22 환경에서 focused Jest 재현과 전체 typecheck baseline 분류를 해야 한다.
임시 ANTLR 4.9.2 JAR SHA-256은
`bb117b1476691dc2915a318efd36f8957c0ad93447fb1dac01107eb15fe137cd`다.

### 4.16 T60-I required test 구현 존재 게이트와 9개 selector

기존 T60은 catalog의 selector 문자열을 effective test로 계산했지만 실제
파일·함수가 없어도 통과할 수 있었다. `harness/acgh/contracts.py`에
`check_required_test_implementations`를 추가해 다음을 fail-closed로 검사한다.

- selector가 `root-relative.py::test_symbol` 형식인가
- absolute path, `..`, backslash 경로 이탈이 없는가
- 파일이 root 안의 regular non-symlink 파일로 실제 존재하는가
- Python AST가 파싱되고 지정 함수 또는 class method가 존재하는가
- parse 불능은 `analysis_error`, 누락·위험 selector는 `block`인가

실제 source-candidate runner에도 T60-I를 넣었고 결과는
`implemented_required_tests=9`, `pass`다.

구현 파일:

- `tests/bank/contracts/test_instance_code.py`
- `tests/bank/contracts/test_query_report.py`
- `tests/bank/contracts/test_data_assertions.py`
- `tests/bank/contracts/test_bank_columns.py`
- `tests/bank/contracts/test_korean_ime.py`
- `tests/bank/contracts/test_sybase.py`
- `tests/bank/contracts/test_tibero.py`
- 공용 helper `_runtime_contract.py`, `_connector_contract.py`

구현 내용:

- InstanceCode: live POST/GET/PUT/search index polling/hard-delete
- QueryReport: live report 생성, 기존 Query usage 연결·조회·수정 후 보존, 정리
- Data Assertions: live failed status·owner·table/column API와 실제 화면 행 projection
- Bank columns: live ordinal·constraint·은행 extension API와 실제 화면 행 projection
- Korean IME: composition start/end guard와 조합 중 state write 차단 source guard
- Sybase/Tibero: JSON Schema validation·payload round-trip·databaseService ref,
  generated API/entity/serviceConnection enum, UI selector test, icon 일관성

현재 source 환경 실행:

```text
10 collected
3 passed: Korean IME source guard, Sybase, Tibero
7 skipped: OPENMETADATA_BASE_URL이 필요한 live selector 4,
           실제 로그인 URL이 필요한 browser selector 3
```

Korean IME의 required selector는 이제 실제 browser test이며 source guard는
보조 테스트일 뿐이다. skip은 pass로 승격하지 않는다. 실제 스택에서 필요한
추가 환경 변수는
`OPENMETADATA_BASE_URL`, 선택 auth token,
`BANK_CONTRACT_QUERY_ID`, `BANK_FAILED_ASSERTION_FQN`,
`BANK_COLUMN_TABLE_FQN`, `BANK_COLUMN_NAME`, `BANK_IME_EDITOR_URL`,
`BANK_DATA_ASSERTIONS_URL`, `BANK_COLUMN_UI_URL`, 선택
`BANK_BROWSER_STORAGE_STATE_B64`다.

### 4.17 source-candidate GitHub Actions

`.github/workflows/source-candidate.yml`을 추가했다. 수동 문서 명령과 CI가
달라지는 것을 막기 위해 아래를 자동화한다.

1. governance 저장소 checkout과 Python 3.11 설치
2. `harness[dev]` 잠금 범위 설치
3. 고정 SHA의 1.12.13/1.13.0 mirror fixture fetch
4. product branch를 blobless·depth 16·sparse 방식으로 checkout
5. checkout HEAD가 `849ae756cd...`와 정확히 같은지 확인
6. harness + 7개 업무 contract의 9 selector 실행
7. T25/T26/T60-I/T30/T31 source-candidate runner 실행

외부 action은 tag가 아니라 40-hex commit으로 고정했고 workflow permissions는
`contents: read`뿐이다. `harness/tests/test_source_candidate_workflow.py`가 action
pin, product evidence lock, read-only permission, 필수 명령 존재를 검증한다.
API runtime 4개와 browser 3개는 이 source job에서 skip되며 T62 운영
job으로 남긴다.

workflow의 exact product fetch·mirror fetch·test·gate 명령을 빈 임시
환경에서 실행한 결과는 다음과 같다.

```text
product HEAD        849ae756cd... (locked SHA match)
upstream mirror     UPSTREAM_A/UPSTREAM_B SHA match
tests               316 passed, 7 live-runtime skipped in 30.67s
source gates        T25/T26/T60-I/T30/T31 all pass
```

첫 원격 run
[`30160752510`](https://github.com/easyseop/openmetadata-test/actions/runs/30160752510)도
success였다. GitHub가 checkout v4/setup-python v5의 Node 20 deprecation
annotation을 냈으므로 checkout v5와 setup-python v6의 공식 tag commit SHA로
다시 고정했다. Node 24 action pin을 사용한 두 번째 원격 run
[`30160846880`](https://github.com/easyseop/openmetadata-test/actions/runs/30160846880)은
25초에 success했고 annotation은 0개다.
마지막 evidence 동기화 run
[`30160922136`](https://github.com/easyseop/openmetadata-test/actions/runs/30160922136)도
success였고 `280 passed, 4 skipped in 12.23s`를 다시 확인했다.

### 4.18 비개발자 사용 가이드와 지속 인수인계 계약

`docs/00-사용가이드/비개발자_사용_가이드.md`를 새로 추가했다. 개발 지식이 없는
업무 담당자도 다음을 순서대로 이해할 수 있게 작성했다.

- 시스템이 막는 세 가지 사고와 현재 배포 차단 결론
- `pass/approval/block/analysis_error/skip/UNASSIGNED` 해석
- 변경 요청 때 준비할 목적, 기능, 오너, 승인자, 업무 규칙, 테스트 입력
- 공식 버전업, 은행 기능 변경, 초록 CI, 긴급 변경의 실제 시나리오
- LLM 위키의 허용 용도와 배포 판정권이 없다는 경계
- 실제 기능 게이트와 릴리스 게이트가 별도라는 점
- 완성 시의 전체 운영 흐름과 쉬운 용어표

`README.md`, `STATUS.md`, `SESSION_STATE.md`, `CLAUDE.md`, roadmap가 이
가이드를 가리키도록 연결했다. 이후 작업자는 개발 묶음이 끝날 때 사용자에게
보이는 상태·입력·절차가 바뀌었는지 확인하고, 바뀌었다면 코드·상태표·인수인계와
같은 묶음에서 가이드도 갱신한다.

이 문서 배치의 검증 명령과 결과:

```bash
git diff --check
# pass

./harness/.venv/bin/python -m pytest \
  harness/tests/test_source_candidate_workflow.py \
  harness/tests/test_vendor_rebuild.py -q
# 16 passed

OM_MIRROR_PATH=/private/tmp/om-ci-mirror-20260725 \
OPENMETADATA_PRODUCT_REPO=/private/tmp/om-ci-validation-38bccf \
  ./harness/.venv/bin/python -m pytest \
  harness/tests tests/bank/contracts -ra
# 280 passed, 4 skipped in 28.17s

./harness/.venv/bin/python \
  harness/registrations/kb-openmetadata/run_source_candidate_gates.py \
  --repo /private/tmp/om-ci-validation-38bccf \
  --harness harness \
  --registration harness/registrations/kb-openmetadata \
  --layout harness/policies/repository-layout.yaml
# T25/T26/T60-I/T30/T31 pass
```

네 skip은 모두 `OPENMETADATA_BASE_URL`이 필요한 live contract이며 pass로
계산하지 않았다.

이 가이드·인수인계 배치의 원격 run
[`30161253922`](https://github.com/easyseop/openmetadata-test/actions/runs/30161253922)도
24초에 success했다. 로그에서 `280 passed, 4 skipped in 12.83s`,
`implemented_required_tests=7`, T25/T26/T60-I/T30/T31의 `pass`를 확인했다.

### 4.19 T62 실제 runtime 계약 실행기와 browser IME 분리

기존 `test_hangul_composition_roundtrip`는 이름과 달리
`SchemaEditor.tsx`의 문자열 조각만 확인했다. 이 상태에서는 실제 브라우저를
열지 않고도 CONTRACT-KOREAN-IME가 통과한 것처럼 기록될 수 있었다.

구현 커밋:

- `b29d0ceea3b8b95423242847b0c172415f420411`

구현 파일:

- `.github/workflows/runtime-contracts.yml`
- `harness/acgh/pytest_runs.py`
- `harness/acgh/testruns.py`
- `harness/registrations/kb-openmetadata/run_runtime_contracts.py`
- `harness/registrations/kb-openmetadata/interpret_runtime_result.py`
- `tests/bank/contracts/test_korean_ime.py`
- `harness/tests/test_pytest_runs.py`
- `harness/tests/test_runtime_contract_workflow.py`

개발 방식:

1. 한글 IME source wiring 검사를
   `test_hangul_composition_source_guard`로 분리했다.
2. contract catalog가 가리키는 `test_hangul_composition_roundtrip`는
   Playwright Chromium으로 실제 렌더된 CodeMirror를 찾는다.
3. `compositionstart/update/end` 동안 `ㅎ→하→한`, `한ㄱ→한그→한글` 상태를
   실제 컴포넌트에 넣고 React controlled state 왕복 뒤 값이 정확히 `한글`인지
   검사한다.
4. catalog selector마다 shell 없이 새 pytest process를 만들고 JUnit XML의
   tests/failures/errors/skipped와 실제 pytest exit를 대조한다.
5. 실패·오류 재시도 이력을 버리지 않으며 high/critical fail→pass는 기존 T62
   규칙대로 approval이 된다.
6. candidate commit/tree, 배포 artifact digest, governance commit, catalog·
   manifest·selector 파일의 suite digest를 한 test-run-set에 결속한다.
7. candidate-lock, test-run-set, acgh-result를 schema 확인 후 원자적으로
   기록한다.
8. CI 경계에서 실제 process exit와 machine result를 다시 해석한다. 결과 파일
   누락·파손·stale·exit 불일치는 `analysis_error`다.

수동 workflow는 `openmetadata-runtime` GitHub environment 승인을 요구한다.
입력은 배포 artifact `sha256` digest, API base URL, Data Assertions URL,
bank column table URL, 편집 가능한 SchemaEditor URL이다. auth token과
browser storage state는 environment secret, Query ID와
테스트 FQN/테이블/컬럼은 environment variable로 받는다. 입력 문자열은 shell
script에 직접 보간하지 않고 environment를 통해 전달한다.

로컬 fail-closed 통합 시뮬레이션:

```text
candidate_sha       849ae756cd238f218b5e3a6c795a392305cb32ee
harness_version     b1d3fa6d00b75c96d837587ea0730f3d6d9e5323
suite_version       sha256:fa1cc4a7c31bc780157879dff2d0ee176cbfe0cc625a7c1dfacd7073522e1f7b
test_run_set_digest sha256:75281dfccab465827c546448dbb2ec08d150fc1c5b6d46da88317e125ab4b3a6
outcomes            2 pass, 7 skipped
verdict              block
actual exit 1        result와 consistent
위조 actual exit 0   analysis_error
```

이 시뮬레이션은 runner 동작만 검사하기 위해 source tree identity digest를
artifact 입력으로 사용했다. 실제 배포 artifact나 운영 T62 증거가 아니다.
실제 runtime workflow는 아직 실행하지 않았다. 구현 당시에는 비밀이 없는 YAML을
GitHub job summary에만 남겼으며, 이 제한은 바로 다음 §4.20의 90일 CI artifact
보존으로 보강했다. 조직 소유의 영구/장기 보존 연결은 여전히 남은 운영 작업이다.

구현 `b29d0ce`와 문서 `a291f31`은 원격 브랜치에 push됐다. 뒤늦게 확인한
최종 sync run
[`30162134698`](https://github.com/easyseop/openmetadata-test/actions/runs/30162134698)은
head `45d0994`에서 success였고 `293 passed, 5 skipped in 13.68s`,
`implemented_required_tests=7`, T25/T26/T60-I/T30/T31 pass를 기록했다.

```bash
gh run list \
  --repo easyseop/openmetadata-test \
  --branch claude/markdown-file-feedback-26933w \
  --workflow source-candidate.yml \
  --limit 5
```

### 4.20 T62 runtime evidence CI artifact 보존

구현 커밋:

- `502f42f77734ec4f894aa79360c22e0f67dc1b19`

`runtime-contracts.yml`과 `source-candidate.yml`에 공식
`actions/upload-artifact` v7.0.1 commit
`043fb46d1a93c77aae656e7c1c64a875d1fc6a0a`를 40-hex SHA로 고정했다.
공식 `action.yml`의 runtime은 `node24`다. 최초 source patch-kill 원격 실행에서
v4의 Node 20 deprecation annotation을 확인한 뒤 `8ec6e28`에서 두 workflow를
함께 전환했다. 후속 run `30212703620`은 annotation 0으로 success여서 전환이
실제 GitHub-hosted runner에서도 확인됐다.
runtime 결과가 pass, block, approval, analysis_error 중 무엇이든
`candidate-lock.yaml`, `test-run-set.yaml`, `acgh-result.yaml`을 업로드한다.

보존 계약:

- artifact 이름: `runtime-contract-evidence-<run_id>-<run_attempt>`
- 보존 기간: 90일
- overwrite: false
- 파일이 하나도 없으면 upload 단계도 error
- 압축 재해석을 줄이기 위해 compression level 0
- hidden file은 포함하지 않음
- 업로드 성공 시 artifact ID, GitHub 계산 digest, URL을 job summary에 기록
- machine result의 observational run ID도 `<run_id>-<run_attempt>`로 일치

이 보존은 job summary 단독보다 강하지만 영구 감사 저장소는 아니다. 조직 보존
기간이 90일을 넘으면 만료 전에 artifact와 GitHub digest를 별도 증거 저장소로
이관해야 한다. 실제 runtime workflow를 아직 실행하지 않았으므로 실제 artifact
ID/digest는 존재하지 않는다.

### 4.21 T61 source-capable patch-kill

구현 커밋:

- `a2cbb5221f50c10d11af26618d1d310ec8a73552`

구현 파일:

- `harness/acgh/patchkill.py`
- `harness/acgh/schema/patch-kill-plan.schema.json`
- `harness/registrations/kb-openmetadata/patch-kill-plan.yaml`
- `harness/registrations/kb-openmetadata/run_source_patch_kills.py`
- `harness/registrations/kb-openmetadata/source-patch-kill-evidence.yaml`
- `.github/workflows/source-candidate.yml`
- `harness/tests/test_patchkill.py`
- `harness/tests/test_source_candidate_workflow.py`

개발 방식:

1. active high/critical ID 5개를 plan에서 source experiment 또는 runtime
   pending 중 정확히 하나로 분류한다. 중복·누락은 실행 오류다.
2. plan candidate가 실제 product HEAD와 같은지, without-patch SHA가 candidate
   조상인지, 그 뒤 커밋에 대상 `Customization-ID`가 실제 존재하는지 확인한다.
3. selector가 해당 manifest의 contract-derived required test인지 확인한다.
4. 각 고정 predecessor를 임시 detached worktree로 열고 외부 governance
   selector를 실행한다. 제품 소스의 테스트 파일을 신뢰해 실행하는 구조가 아니다.
5. 기존 T62 pytest adapter로 JUnit과 실제 pytest exit를 대조한다. assertion
   failure만 `proven/pass`다. patch가 없는데 pass면 `shell_test/block`,
   skip·test error면 `inconclusive/analysis_error`, internal exit·timeout이면
   `infra_error/analysis_error`다.
6. candidate·governance commit·plan digest·selector·without-patch SHA와
   pending ID를 `acgh-result`에 결속한다.
7. Source candidate CI가 이 두 experiment를 실행하고 결과를
   `source-patch-kill-evidence-<run_id>-<run_attempt>` artifact로 overwrite
   없이 90일 보존한다.

실행 결과:

```text
BANK-OM-006 Sybase
  without patch: 6e5b654f84ec6441e8affcef90c79f83c9a4d986
  selector: tests/bank/contracts/test_sybase.py::test_connection_schema_roundtrip
  outcome: required test failed -> proven/pass

BANK-OM-007 Tibero
  without patch: 41b224adbd7e1906a96d99657693e439e3d8716b
  selector: tests/bank/contracts/test_tibero.py::test_connection_schema_roundtrip
  outcome: required test failed -> proven/pass

source-scoped verdict: pass
result digest: sha256:1cadd0bed3e58b01d5720bd1519452de838785f1d1328b14dc58c4de04bc9e2d
```

첫 원격 실행
[`30212561441`](https://github.com/easyseop/openmetadata-test/actions/runs/30212561441)은
head `17b7427`에서 `297 passed, 5 skipped in 19.57s`, source gate 5개 pass,
source patch-kill 2개 pass로 success였다. 보존된 artifact는
`source-patch-kill-evidence-30212561441-1`, ID `8634882239`, GitHub digest
`sha256:d5afd822d8898e5ed94611f5220caa25ba152a211169f3c990ec73f8a7bfa32f`,
만료 시각 `2026-10-24T17:26:01Z`다.

Node 24 action 전환 후 최종 확인
[`30212703620`](https://github.com/easyseop/openmetadata-test/actions/runs/30212703620)은
head `9326696`에서 annotation 0, `297 passed, 5 skipped in 13.14s`, source
gate 5개와 patch-kill 2개 pass로 success였다. 최신 artifact는
`source-patch-kill-evidence-30212703620-1`, ID `8634920602`, digest
`sha256:bb8b97516ea4b39ba5e14a866327ad18785f3b25ee4aeb02b6da3a2cb12cf109`,
만료 `2026-10-24T17:30:09Z`다.

이 결과는 high/critical T61 전체 pass가 아니다. `BANK-OM-001` InstanceCode,
`BANK-OM-002` QueryReport, `BANK-OM-003` Data Assertions는 코드 predecessor만
읽어서는 API·DB·검색 동작을 반증할 수 없다. 각 ID를 제외한 image를 별도로
빌드·배포하고 같은 runtime contract를 실행해야 한다. 따라서 현 상태는
**source-capable high 2/5 pass, runtime high 3/5 pending**이다.

### 4.22 Data Assertions·bank column 실제 화면 계약 보강

구현 커밋:

- `093724faa499458eb4723511914a1376138ef014`

변경 파일:

- `tests/bank/contracts/_browser_contract.py`
- `tests/bank/contracts/test_data_assertions.py`
- `tests/bank/contracts/test_bank_columns.py`
- `tests/bank/contracts/test_korean_ime.py`
- `harness/registrations/kb-openmetadata/contracts.yaml`
- `.github/workflows/runtime-contracts.yml`
- `harness/tests/test_runtime_contract_workflow.py`

발견한 문제와 개발 방식:

1. `BANK-OM-003`과 `BANK-OM-004` manifest의 변경 경로는 UI 코드인데 기존
   required selector는 API 응답만 확인했다. UI 패치를 제거해도 API 검사는
   통과할 수 있으므로 patch survival 증거로 부족했다.
2. Data Assertions 브라우저 selector는 API에서 고정 실패 test case의
   table·column·owner·Failed 상태를 읽고, 로그인된 실제 페이지의 같은 행에서
   네 값을 다시 대조한다.
3. bank column 브라우저 selector는 API에서 고정 컬럼의
   `attributeName`·`instanceName`·`infoType`을 읽고 실제 schema table 행에서
   세 확장값이 렌더됐는지 대조한다.
4. 세 브라우저 계약은 공통 storage-state decoder와 Playwright import
   fail-closed helper를 공유한다. URL을 설정했는데 Playwright가 없거나 로그인
   상태가 잘못되면 skip/pass가 아니라 test failure다.
5. runtime workflow에 `data_assertions_url`, `bank_column_ui_url` 필수 입력을
   추가했다. 기존 artifact digest, API base URL, IME URL과 합쳐 다섯 수동
   입력이며 비밀 로그인 상태는 계속 environment secret으로만 받는다.
6. 업무 contract 수는 7개 그대로지만 required selector는 7개에서 9개로
   늘었다. 무환경 로컬 실행의 정직한 결과도 `2 pass·7 skip→block`으로 바뀐다.

검증:

```text
targeted contract/workflow tests  13 passed, 6 skipped
fixed mirror full suite           297 passed, 7 skipped in 31.18s
T60-I                             pass (implemented_required_tests=9)
T62 no-runtime simulation         2 pass, 7 skipped -> block
suite digest                      sha256:7fceb9d7...b7dd9df1
test-run-set digest               sha256:96dfec4b...d5b196
```

일곱 skip은 API 환경이 필요한 selector 4개와 실제 로그인 화면이 필요한
Data Assertions·bank column·IME selector 3개다. 실제 runtime 실행 증거는 아직
없으며, 이 구현을 운영 통과로 표현하면 안 된다.

이 배치의 원격 run
[`30213348947`](https://github.com/easyseop/openmetadata-test/actions/runs/30213348947)은
head `a502d92`에서 `297 passed, 7 skipped in 14.87s`, T60-I 9/9, source gate
5개, source patch-kill 2개 pass로 success였다. 증거 artifact는
`source-patch-kill-evidence-30213348947-1`, ID `8635093639`, digest
`sha256:2cd41e38...aaeee1b`, 만료 `2026-10-24T17:48:17Z`다.

### 4.23 T61 deployed runtime patch-kill 전용 게이트

구현 커밋:

- `1956b7880506674e37ad2428248a9fc69817dbc2`

핵심 파일:

- `harness/acgh/patchkill.py`
- `harness/acgh/schema/runtime-patch-kill-plan.schema.json`
- `harness/registrations/kb-openmetadata/runtime-patch-kill-plan.yaml`
- `harness/registrations/kb-openmetadata/run_runtime_patch_kill.py`
- `harness/registrations/kb-openmetadata/interpret_runtime_patch_kill_result.py`
- `tests/bank/contracts/_runtime_patch_kill_probes.py`
- `.github/workflows/runtime-patch-kill.yml`
- `harness/tests/test_runtime_patch_kill_workflow.py`

목적과 개발 방식:

1. source plan의 pending ID 세 개와 runtime plan의 experiment 세 개가 정확히
   같은 집합인지 검사해 고우선순위 범위 누락을 막는다.
2. `BANK-OM-001/002/003`은 각각 커스터마이징을 넣기 직전의 고정 predecessor
   SHA를 사용한다. 선택 selector는 해당 manifest contract에서 파생된
   required selector여야 하고, predecessor 뒤 commit에 같은 ID trailer가
   실제 존재해야 한다.
3. target selector를 연속 두 번 실행해 두 번 모두 assertion failure일 때만
   negative control을 `proven/pass`로 본다. 한 번이라도 pass면
   `shell_test/block`, skip·test error·JUnit/exit 불일치·timeout은
   `analysis_error`다.
4. 단순 서비스 장애를 기능 소실 검출로 오인하지 않도록 독립 health probe를
   target 전후에 실행한다. InstanceCode는 인증 API, QueryReport는 API와 고정
   Query, Data Assertions는 API·실패 test case·별도 로그인 UI 표식을 확인한다.
   전후 probe가 모두 pass하지 않으면 target이 실패했어도 전체는
   `analysis_error`다.
5. result는 full candidate, predecessor source/tree, 배포된 제거본 artifact
   digest, source→artifact·fixture 배포 기록 digest, governance commit,
   suite digest, 비밀이 아닌 환경 ID를 함께 결속한다. URL·token·browser
   storage state는 증거 YAML에 기록하지 않는다.
6. 별도 `openmetadata-runtime-patch-kill` environment 승인과 환경별
   concurrency 직렬화를 사용해 일반 T62 실행과 권한·충돌 범위를 분리했다.
7. 결과와 실제 process exit를 CI 마지막 단계에서 다시 대조하고, pass·block·
   analysis_error 여부와 무관하게 overwrite 불가 artifact로 90일 보존한다.

고정 predecessor:

| ID | without-patch SHA | target |
|---|---|---|
| `BANK-OM-001` | `afcb2d2...` | InstanceCode CRUD/search |
| `BANK-OM-002` | `a2566fac...` | QueryReport usage |
| `BANK-OM-003` | `4108411c...` | Data Assertions rendered row |

검증:

```text
fixed mirror full suite             306 passed, 7 skipped in 34.28s
runtime patch-kill unit/workflow    pass
BANK-OM-001 no-runtime rehearsal    analysis_error
BANK-OM-002 no-runtime rehearsal    analysis_error
BANK-OM-003 no-runtime rehearsal    analysis_error
forged actual exit 0                synthetic analysis_error
```

중요 한계: 이 세 SHA는 순차 재구축 predecessor이지 candidate에서 대상 ID만 뺀
완전한 candidate-minus-one 재빌드가 아니다. 전후 probe와 배포 기록 digest가
거짓 증거 위험을 줄이지만 없애지는 않는다. Claude는 ID 격리 제거본을 추가로
요구할지 독립 검토해야 한다. 또한 실제 predecessor artifact의 build·배포·workflow
실행은 0건이므로 **T61 전체 pass가 아니다**.

### 4.24 BANK-OM-008 — 지원 Node 22 기반 후보 UI 타입 보강

제품 커밋:

- `ddf0dd2ebaf50bc0aa97143a5e97312bc27bd91d`
- trailer: `Customization-ID: BANK-OM-008`

거버넌스 등록 구현 커밋:

- `5823eda35da4b0242aa59c00d6e19802c4a10afc`

수정 파일:

- 제품
  - `openmetadata-ui/src/main/resources/ui/src/components/AppRouter/AuthenticatedAppRouter.tsx`
  - `openmetadata-ui/src/main/resources/ui/src/components/Explore/ExplorePage.interface.ts`
- 거버넌스
  - `harness/acgh/registry.py`
  - `harness/acgh/vendor_rebuild.py`
  - `harness/acgh/schema/customization-registry.schema.json`
  - `harness/registrations/kb-openmetadata/manifests/BANK-OM-008.yaml`
  - `harness/registrations/kb-openmetadata/customization-registry.yaml`
  - 세 workflow와 source/runtime patch-kill candidate lock

발견과 수정 방법:

1. 제품 `.nvmrc`와 같은 공식 Node `22.17.0` darwin-arm64 archive를 사용했다.
   archive SHA-256은
   `cc9cc294eaf782dd93c8c51f460da610cc35753c6a9947411731524d16e97914`
   로 공식 게시값과 일치한다. Yarn은 Corepack의 `1.22.22`다.
2. 수정 전 전체 `yarn tsc:check`는 399 diagnostics였다. 후보 변경 파일과
   교차하면 4개 파일에 오류가 있었지만, source line을 공식
   `afcb2d2...` worktree와 비교해 16건은 upstream에 같은 코드로 존재함을
   확인했다.
3. 후보가 실제로 새로 만든 오류는 세 건이었다.
   - InstanceCode 목록 route의 필수 `pageTitle` 누락
   - QueryReport 목록 route의 필수 `pageTitle` 누락
   - 두 search index가 `ExploreSearchIndex` union에 없어
     `SearchClassBase.getTabsInfo()`가 거부된 오류
4. 두 route에 번역된 복수형 page title을 전달하고 union에
   `INSTANCE_CODE`, `QUERY_REPORT`를 추가했다.
5. 수정 후 동일 Node/Yarn/6GB heap 전체 typecheck는 396 diagnostics다.
   세 후보 오류가 모두 사라졌고, 후보가 만든 새 오류는 0건이다. 수정 두 파일의
   Prettier check도 pass했다. 전체 명령은 여전히 exit 2이므로 제품 전체
   typecheck를 pass로 표현하면 안 된다.

왜 새 ID인가:

기존 제품 이력은 001→007과 연속 007 후속으로 고정돼 있다. 지금 001/002를 다시
사용하면 T31의 non-contiguous series를 깨고, 두 ID를 한 commit에 쓰면 T30의
multiple-ID를 깬다. 과거 이력을 force-push로 재작성하지 않고, 두 기능이 공유하는
탐색 UI 정합성 보강을 `BANK-OM-008` 하나로 등록했다.

등록부에는 `provenance`를 추가했다.

- `source-snapshot`: 원본 `kb_openmetadata` snapshot에서 재구성한 001~007
- `candidate-follow-up`: 재구성 후 현재 후보에서 추가한 008

T25-R plan은 `source_snapshot_ids()`만 사용하므로 008이 과거 snapshot에
있었다고 왜곡하지 않는다. 반면 T26/T30/T31과 runtime candidate lock은 active
008을 포함한다. 현재 source gate 결과는 다음과 같다.

```text
T25 vendor ancestry              pass (candidate ddf0dd2e...)
T26 customization survival       pass (8 IDs, 12 required paths)
T60-I required implementations   pass (9 selectors)
T30 commit invariants            pass
T31 ID invariants                pass
```

원격 재검증 run
[`30214885448`](https://github.com/easyseop/openmetadata-test/actions/runs/30214885448)
도 `306 passed, 7 skipped`, source gate 5개, T60-I 9/9, source
patch-kill 2개 pass로 성공했다. 증거 artifact는 ID `8635517530`,
GitHub digest `sha256:bbb2bddf...ca40a27`, 만료
`2026-10-24T18:31:08Z`다.

로컬 작업 경로 주의:

macOS Documents 아래 작업본이 저장 공간 최적화로 dataless placeholder가 되어
Git read가 중단됐다. 유실 방지를 위해 이 세션은
`/private/tmp/openmetadata-test-recovered-20260727`에서 계속했고, 정본은 매
작업 묶음마다 원격 branch에 push한다. 다음 작업자는 Documents 복제본을 신뢰하기
전에 `stat`/`git status`를 확인하고, 문제가 있으면 원격 branch를 새로 clone한다.

### 4.25 T63 — 공식 upstream 대비 UI typecheck 기준선 delta

구현 커밋:

- `39294bf38172f16528833640c03302aa83ade7b4`

구현 파일:

- `harness/acgh/tsc_baseline.py`
- `harness/tests/test_tsc_baseline.py`
- `harness/registrations/kb-openmetadata/compare_ui_typecheck.py`
- `harness/registrations/kb-openmetadata/ui-typecheck-baseline-evidence.yaml`
- `harness/registrations/kb-openmetadata/source-candidate-evidence.yaml`

개발 목적:

후보 typecheck가 수백 건의 기존 오류를 포함할 때 총건수나 후보 변경 파일만
비교하면, 후보가 새로 만든 오류가 다른 기존 오류의 감소에 상쇄되거나 기존 오류
묶음에 묻힐 수 있다. T63은 공식 upstream과 candidate의 **전체 로그**를 같은
toolchain에서 비교해 이 착시를 차단한다.

구현 방법:

1. ANSI escape를 제거하고 `repo-relative path(line,column): error TSxxxx: ...`
   형식만 primary diagnostic으로 파싱한다.
2. `(path, TS error code)`를 set이 아니라 multiset으로 세어 같은 오류의 중복
   증가도 신규 진단으로 검출한다.
3. 후보 신규/증가는 `block`, unsafe/malformed path와 예상 밖 process exit,
   exit/진단 건수 모순은 `analysis_error`다.
4. upstream/candidate가 모두 clean일 때만 `pass`다. 신규가 없어도 upstream
   baseline이 비어 있지 않으면 반드시 `approval`이다.
5. 정렬된 multiset의 SHA-256 fingerprint와 원본 로그 SHA, toolchain,
   upstream/candidate SHA를 machine evidence에 고정했다.

실제 비교 환경:

```text
official upstream SHA     afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9
candidate SHA             849ae756cd238f218b5e3a6c795a392305cb32ee
Node / Yarn                22.17.0 / 1.22.22
Node archive SHA-256       cc9cc294eaf782dd93c8c51f460da610cc35753c6a9947411731524d16e97914
upstream raw log SHA-256   6bca51ba43a80099f00336469504bdef7120df61c34658a685c7d50a97b18610
candidate raw log SHA-256  619310266436c12a194537bcc2ca75be7d50b51fd91f03b659a039f9a208bda0
```

ANTLR과 parsed schema를 양쪽 worktree에서 생성하고 동일 dependency tree와
`NODE_OPTIONS=--max-old-space-size=6144 yarn tsc:check`를 사용했다. 최초
생성물 없는 upstream 실행의 535건은 준비 불일치라 폐기했고, 준비가 같은 두
로그만 증거로 등록했다.

실제 판정:

```text
upstream diagnostics      396 (141 files)
candidate diagnostics     355 (133 files)
new / removed path+code   0 / 41
upstream path+code fp     sha256:a4158616c8921cc299679553b58ba388493a3aaaf5994314cb1a16f78e342fe8
candidate path+code fp    sha256:887df7115c667ba66350efb3d9f30b0535ef10c5d16c70d7effb24adf63627f2
new / removed messages    10 / 51
upstream message fp       sha256:bb893ff886aecb68e57062e289d306c276a5541aad9bf2b2b5a9d56e025b1f4f
candidate message fp      sha256:6b1766895781fe40749b51c2b4a1f9af0e2dcd5032ddb928767ca5567fd2a9df
verdict / exit             approval / 2
targeted gate tests        10 passed
```

이 결과는 “후보가 새 path/code 진단을 추가하지 않았고 기존 41건을 제거했다”는
근거이지 제품 전체 typecheck pass가 아니다. 같은 path/code 안의 메시지 치환도
두 번째 fingerprint로 탐지한다. 다만 TypeScript가 동등한 union을 다른 순서나
축약으로 출력할 수 있으므로 메시지 변형은 자동 block이 아니라 approval
검토 근거다. Claude는 열 변형이 모두 설명 가능한지 독립 검토해야 한다.

2026-07-27 clean-cache 후속 기술 검토에서는 열 변형을 full log의 같은
path/code와 대조했다.

| 경로·코드 | 판별 | 근거 |
|---|---|---|
| `Suggestions.tsx` TS2345 | 동등한 union 순서 | search-source union 앞부분 순서만 변화, `SuggestionsObject` 할당 실패 동일 |
| `SettingsRouter.test.tsx` TS2551 | 동등한 출력 변화 | route object 생략 개수만 141→146, 누락 키·추천 키 동일 |
| `AuthProvider.tsx` TS2345 | 동등한 union 순서 | callback literal 2개의 순서만 변화, string 할당 실패 동일 |
| `GenericProvider.tsx:94` TS2345 | 동등한 union 순서 | `WidgetConfig[]`와 index-signature member 순서만 변화, state initializer 실패 동일 |
| `GenericProvider.tsx:186` TS2345 | 동등한 union 순서 | 같은 union 순서만 변화, `SetStateAction` 실패 동일 |
| `ContractScehmaFormTab.tsx` TS2322 | 동등한 union 순서 | `Field[]`/`Column[]` 순서만 변화, readonly 배열 할당 실패 동일 |
| `PortNode.component.tsx` TS2322 | 동등한 출력 변화 | 확장 객체 필드 순서만 변화, `LineageNodeType` 실패 동일 |
| `Lineage.test.tsx` TS2739 | 동등한 속성 순서 | 누락 속성 `entityType`/`columns`의 표시 순서만 변화 |
| `ExplorePageV1.component.tsx` TS2322 | 동등한 union 순서 | `never[]`/`QueryFieldInterface` 순서만 변화, 배열 할당 실패 동일 |
| `ExploreUtils.tsx` TS2339 | 동등한 union 순서 | 같은 union 순서만 변화, `flatMap` 부재 실패 동일 |

따라서 이 열 건에서 새 의미 회귀는 식별되지 않았다. 기계 판정은 의도대로
`approval`을 유지한다. 이는 지정 owner의 355건 기준선 승인이나 전체 typecheck
green을 대신하지 않는다. 기계 판독 가능한 상세는
`ui-typecheck-baseline-evidence.yaml`의 `message_variant_review`에 고정했다.

원격 source-candidate 재현:

```text
run                         30216708258
governance head             bc0e957109e473885dc702938286eabf91fdbdd5
product commit              70d028a035bb1edb8af5a11f06c4c7dff4cd979b
suite                       316 passed, 7 skipped in 13.15s
source gates                5 pass
T60-I                       9/9
source patch-kill           2 pass
patch-kill result digest    sha256:965d515da3c307814c027b542c0abc4e9f0d79fc535c7d55bd59ac448b2f797f
artifact ID                 8636012730
artifact digest             sha256:813c26df22d828f5281eb87d92a341adec6c45ee4c5ef81c692a0effc50860b4
artifact expiry             2026-10-24T19:22:20Z
```

Run URL:
`https://github.com/easyseop/openmetadata-test/actions/runs/30216708258`.

이 run은 `BANK-OM-009` 제품 commit `70d028a...`와 거버넌스 등록·증적·문서
batch를 함께 검증한 기록 증거다. 이전 `30215596535`는
`BANK-OM-009` 전 후보의 역사적 증거로만 유지한다.

### 4.26 BANK-OM-009 — 공통 검색 결과 타입 정합성 보강

제품 커밋:

- `70d028a035bb1edb8af5a11f06c4c7dff4cd979b`
- trailer: `Customization-ID: BANK-OM-009`

거버넌스:

- 등록 구현: `4353f457ca93710f71b08f8c5c6365a33fb3f7d8`
- evidence 재결속: `89763f3952868da27af9f8bcc688a34e593da4da`
- manifest:
  `harness/registrations/kb-openmetadata/manifests/BANK-OM-009.yaml`
- provenance: `candidate-follow-up`
- depends_on: `BANK-OM-008`

발견 경로:

T63에 message multiset을 추가해 `396=396`의 내부를 비교하자 후보 메시지 일부에
`Pick<unknown, never>`가 나타났다. 조사 결과 공식 1.13.1에도
`SearchIndex.METADATA_SERVICE` enum은 있지만
`SearchIndexSearchSourceMapping` 항목과 generated source interface가 없었다.
새 InstanceCode/QueryReport 인덱스가 union에 들어오면서 기존 누락이 더 분명히
드러난 것이다.

제품 수정:

1. `search.interface.ts`
   - generated `MetadataService`를 import한다.
   - `MetadataServiceSearchSource`를 정의한다.
   - `METADATA_SERVICE`를 `SearchIndexSearchSourceMapping`에 연결한다.
   - InstanceCode/QueryReport/MetadataService를 공통 search source union에
     포함한다.
2. `CuratedAssetsWidget.tsx`
   - 모든 `SearchIndex` 결과를 받을 수 있다고 선언한 과도한 상태 타입을 실제
     요청인 `SearchIndex.DATA_ASSET` 결과 타입으로 좁힌다.
   - 매핑 보강 뒤 숨어 있던 `item.id` 진단 한 건을 제거한다.

검증:

```text
Prettier                              pass (2 paths)
CuratedAssetsWidget focused Jest      18/18 pass
focused Jest warning                  기존 async state update act(...) 경고, test failure 아님
Node 22 full tsc                       396 -> 357
T63 new/removed path+code             0 / 39
T25/T26/T60-I/T30/T31                 pass / 9 IDs / 14 required paths / 9 selectors
runtime no-environment                2 pass, 7 skip -> block
forged runtime exit                   analysis_error
source patch-kill                     2 pass
full governance suite                 316 pass, 7 operational skip
```

왜 새 ID인가:

008은 route title과 `ExploreSearchIndex` 연결이라는 은행 탐색 화면 정합성을
추적한다. 009는 공식 코드에도 있던 metadata-service mapping 누락과 Curated
Assets 공통 타입을 수정해 범위와 검토 질문이 다르다. 008 이력을 재작성하거나
series 허용으로 넓히지 않고 별도 candidate-follow-up으로 등록했다. T25-R은
여전히 원본 7개만 재구성하고 T26/T30/T31/runtime lock은 009까지 포함한다.

### 4.27 BANK-OM-010 — 알림 엔터티 ID 검색 타입 안전성

제품 커밋:

- `b80d24d83124435733d5af05d56515b3a855330e`
- tree: `5925b80951bbbb033261a66e8b6b4931b57db0fe`
- trailer: `Customization-ID: BANK-OM-010`

거버넌스:

- 등록 구현: `d70fe810b65f44b20e79dca7bcdb697f806d99f7`
- evidence 재결속: `5e6d0a8`
- manifest:
  `harness/registrations/kb-openmetadata/manifests/BANK-OM-010.yaml`
- provenance: `candidate-follow-up`
- depends_on: `BANK-OM-009`

발견과 수정:

1. BANK-OM-009가 `Pick<..., never>`를 실제 search-source 필드로 복구하면서
   `AlertsUtil.tsx`의 엔터티 ID suggestion이 모든 union member에
   `_source.id`가 있다고 가정한 기존 오류가 정확히 드러났다.
2. `_source.id`가 문자열이면 기존처럼 우선 사용한다.
3. 해당 필드가 없는 search-source 결과에서는 `SearchHitBody`가 보장하는
   Elasticsearch hit `_id`를 사용한다.
4. 회귀 테스트는 source ID와 hit ID가 다른 결과, source ID가 없는 결과를
   함께 넣어 우선순위와 fallback을 모두 고정한다.

검증:

```text
Prettier                              pass (2 paths)
AlertsUtil focused Jest               112/112 pass
focused Jest warning                  기존 FormContext warning, test failure 아님
Node 22 full tsc                       357 -> 356
T63 upstream/candidate                396 / 356
T63 new/removed path+code             0 / 40
T63 new/removed messages              4 / 44
T25/T26/T60-I/T30/T31                 pass / 10 IDs / 16 required paths / 9 selectors
candidate source-tree digest          sha256:3ca82def...5c91834
candidate-lock digest                 sha256:3a176aed...554c57
runtime no-environment                2 pass, 7 skip -> block
runtime suite digest                  sha256:6cd7b8ba...64761a0
runtime run-set digest                sha256:b1639032...4b21f9
source patch-kill                     2 pass
source patch-kill result digest       sha256:1925be2e...4c4b56
```

왜 새 ID인가:

009는 공통 매핑과 Curated Assets의 결과 타입을 고친다. 010은 그 매핑을
소비하는 알림 엔터티 ID 선택기의 런타임 fallback과 우선순위를 고정하므로
검토 질문과 변경 경로가 다르다. 009 이력을 수정하지 않고 별도 follow-up으로
등록했으며 T25-R은 원본 7개만, 현재 생존·불변식·runtime lock은 010까지
검사한다.

원격 재현:

```text
run                         30219786626
governance head             90036ff4fdec8292c33bbb65e5bdc7bcfd14d597
product commit              b80d24d83124435733d5af05d56515b3a855330e
suite                       316 passed, 7 skipped in 15.29s
active IDs                  10
source gates                5 pass
T60-I                       9/9
source patch-kill           2 pass
patch-kill result digest    sha256:b6a574091ae2bcc8745811179674b3dff90b83e356dc99fceb2363a19cd18541
artifact ID                 8636860716
artifact digest             sha256:88a16a937b1aa0a590ebcb15798a87d9ef6c33a4dd87d93f2f9f6c5427eb5910
artifact expiry             2026-10-24T20:49:23Z
```

Run URL:
`https://github.com/easyseop/openmetadata-test/actions/runs/30219786626`.

### 4.28 2026-07-27 06:00 KST 저장소·문서 정합성 점검

정기 점검에서 다음을 다시 확인했다.

```text
governance local / remote     434d92bb2c41a9749700525add2355c0ea3f7aeb / equal
product local / remote        b80d24d83124435733d5af05d56515b3a855330e / equal
working trees                 both clean
latest governance run         30219859614 / success
local fixed-mirror suite      316 passed / 7 operational skips / 28.21s
open PR or review             none on both working branches
branch protection             disabled on both working branches
```

비개발자 가이드의 “최근 성공 실행” 링크가 이전 후보 run `30214885448`을
가리키던 문서 불일치를 발견해, 당시 `BANK-OM-010` 후보와 patch-kill 증거가
결속된 run `30219786626`으로 바로잡았다.

T63에 남은 실제 `useDataFetching.tsx` TS2345도 호출 경로까지 다시 검토했다.
기본 변환은 `SearchResponse<SearchIndex>`의 union source를 임의의 제네릭
`T[]`로 돌려주므로 현재 선언만으로는 타입 안전성을 증명할 수 없다. 단순
cast는 진단만 숨기므로 자동 수정하지 않았다. 다음 제품 수정은 검색 인덱스
`SI`와 `SearchIndexSearchSourceMapping[SI]`를 hook·listing props 전체에
연결하는 설계, 또는 custom transform을 필수화하는 설계 중 하나를 오너가
선택한 뒤 focused hook/listing 테스트와 T63 재결속을 함께 수행해야 한다.

### 4.29 BANK-OM-011 — 검색 목록 변환 타입 계약

§4.28에서 남긴 두 설계안 중 custom transform을 필수화하는 방식을 구현했다.
임의의 제네릭 `T`를 search-source union으로부터 자동 추측하지 않고, 실제
호출자인 Domain/DataProduct가 자신의 `SearchIndex` 응답 변환을 명시한다.

제품:

```text
commit                       849ae756cd238f218b5e3a6c795a392305cb32ee
tree                         22f92a8e0fd2855949e7f115f32c3b9d44c681f6
trailer                      Customization-ID: BANK-OM-011
changed paths                6
```

개발 방식:

1. `DataFetchingConfig<T, SI>`가 `SearchIndex` 타입 `SI`를 보존한다.
2. `DataFetchingSearchResponse<SI>`가 `searchQuery`의 단일/배열 조건부
   반환형을 hook 계약에 그대로 전달한다.
3. optional default transform을 제거하고 transform을 필수로 만든다.
4. `useListingData<T, SI>`가 동일 transform을 손실 없이 전달한다.
5. Domain/DataProduct hook은 각각 `SearchIndex.DOMAIN`과
   `SearchIndex.DATA_PRODUCT` 응답을 명시적으로 entity 배열로 변환한다.
6. 새 `useDataFetching.test.tsx`는 raw 응답이 아니라 transform 반환값만
   state에 저장되는 계약을 고정한다.

거버넌스:

```text
registration commit          b1d3fa6d00b75c96d837587ea0730f3d6d9e5323
evidence rebind commit       c246ae2
manifest                     manifests/BANK-OM-011.yaml
provenance                   candidate-follow-up
depends_on                   BANK-OM-010
active IDs / required paths  11 / 22
contract refs / selectors    15 / 9
```

검증:

```text
Prettier                     6/6 paths pass
focused Jest                 2 suites, 7/7 tests pass
focused warning              기존 React Router future warning, failure 아님
T63 upstream / candidate     396 / 355
T63 new / removed path+code  0 / 41
T63 new / removed messages   10 / 51
candidate raw log SHA-256    619310266436c12a194537bcc2ca75be7d50b51fd91f03b659a039f9a208bda0
candidate path+code fp       sha256:887df7115c667ba66350efb3d9f30b0535ef10c5d16c70d7effb24adf63627f2
candidate message fp         sha256:6b1766895781fe40749b51c2b4a1f9af0e2dcd5032ddb928767ca5567fd2a9df
source tree digest           sha256:830cf970f38a93a701743420ec710cda55cd1aa5d9a45f03f7eb7221d9f5b643
candidate-lock digest        sha256:61a3f02d3f22420d36e6c035aa7afab050d0faf34d29b5f369af01553fb00156
T25/T26/T60-I/T30/T31        all pass
full governance suite        316 passed, 7 operational skips in 30.67s
runtime simulation           2 pass, 7 skip -> block
runtime suite digest         sha256:fa1cc4a7c31bc780157879dff2d0ee176cbfe0cc625a7c1dfacd7073522e1f7b
runtime run-set digest       sha256:75281dfccab465827c546448dbb2ec08d150fc1c5b6d46da88317e125ab4b3a6
source patch-kill            2 pass
source patch-kill result     sha256:a0f194b3f566d92fedfe7bc9aeaf35c65fa54ea79f37eb97088aa02ac00e6746
```

T63 verdict는 개선 후에도 `approval`이다. 신규 path/code는 없지만 후보 자체에
355개 진단이 남아 있으므로 designated owner 승인 또는 추가 수리가 필요하다.

원격 재현:

```text
run                         30222439344
governance head             a71509295bdb1f5d7b0a74df0e398e514143ca19
product commit              849ae756cd238f218b5e3a6c795a392305cb32ee
suite                       316 passed, 7 skipped in 13.71s
active IDs                  11
source gates                5 pass
T60-I                       9/9
source patch-kill           2 pass
patch-kill result digest    sha256:9b4e4fecf6016bd0fd8ca8cef66c1538af8e7a215c813069a4d6f945a3be71ae
artifact ID                 8637594508
artifact digest             sha256:c6221ec87d2e0e9052d447022c88af1e2861fa895b35e90864c49476d47c38d5
artifact expiry             2026-10-24T22:05:46Z
```

Run URL:
`https://github.com/easyseop/openmetadata-test/actions/runs/30222439344`.

### 4.30 비개발자 시연·테스트 실행 가이드

비개발자가 개발 도구나 명령어 없이 현재 후보의 증거를 직접 확인하고, 행내
테스트 환경이 준비됐을 때 운영자와 실제 계약 검사를 실행할 수 있도록 별도
runbook을 추가했다.

```text
branch                       claude/markdown-file-feedback-26933w
guide implementation        f833f79fb2e85780b09b6966999be4341c5d1a91
product candidate            849ae756cd238f218b5e3a6c795a392305cb32ee
recorded source run          30222439344
runtime operational run      not executed
```

변경 파일과 동작:

- `docs/00-사용가이드/비개발자_시연_가이드.md`
  - GitHub 화면만 사용하는 10분 source 시연
  - 제품 커밋·11개 등록부·316 pass/7 operational skip·T25/T26/T30/T31
    후보 결속 확인
  - 발표자가 그대로 읽을 수 있는 설명문과 합격 체크표
  - `openmetadata-runtime`의 secret 2개, variable 4개, workflow 입력 5개
  - API 4개·connector 2개·browser 3개, 총 9 selector의 쉬운 기능 설명
  - 결과 판정, 90일 artifact 다운로드, 보조 화면 시연, 장애 해결, 결과 기록지
- `docs/00-사용가이드/비개발자_사용_가이드.md`, `README.md`
  - 새 시연 가이드 진입 링크
- `CLAUDE.md`
  - 새 문서를 지속 갱신 handoff set과 검토 읽기 순서에 포함
- `STATUS.md`, `SESSION_STATE.md`, 이 문서
  - 구현 커밋과 비개발자 시연 절차를 인수인계 정본에 연결

검증:

```text
git diff --cached --check       pass
local linked file existence     pass
candidate/run/workflow values   registration evidence and workflow YAML match
code or test behavior changed   no
source suite rerun              no (documentation-only batch)
runtime suite executed          no
```

이 가이드는 source-only 성공을 deployment-ready로 바꾸지 않는다. 11개 owner
미지정, 실제 API 4개·browser 3개 미실행, deployed high-ID patch-kill 3개
미실행, release artifact·T90·T91·T94 증거 부재, 미보호 브랜치 blocker는
그대로다. 원격 인수인계의 완료 여부는 이 절과 `f833f79`가
`origin/claude/markdown-file-feedback-26933w` ancestry에 함께 있는지로
확인한다.

### 4.31 실제 GitHub 캡처 기반 비개발자 시연 보강

텍스트만으로는 업그레이드와 검사 순서를 이해하기 어렵다는 사용자 피드백을
반영해, 실제 공개 GitHub 화면 10장과 vendor merge 전체 흐름을 시연 가이드에
추가했다.

```text
branch                       claude/markdown-file-feedback-26933w
screenshot guide commit      258bb8a27a148d0500531c98fefecd05013fc7ab
screenshots                  10
image dimensions             1280 x 720
image format                 PNG
product candidate            849ae756cd238f218b5e3a6c795a392305cb32ee
recorded source run          30222439344
runtime operational run      not executed
```

시연 가이드에 고정한 흐름:

```text
현재 OpenMetadata + 행내 커스터마이징
→ 승인한 공식 버전/SHA 고정
→ 공식 버전을 행내 vendor 브랜치에 merge
→ 충돌 해결·필요 보강
→ candidate 확정
→ source gate
→ 격리 테스트 환경 배포
→ runtime API·connector·browser 9 selector
→ T90/T91/T94
→ 결과와 증거
```

이 순서는 “깨끗한 공식 새 버전에 customization을 매번 재복사”하는 것으로
설명하지 않는다. 기존 customization vendor branch에 승인한 공식 target을
merge하는 ADR-001 기본 전략을 비개발자 표현으로 유지한다.

실제 캡처 범위:

1. 제품 commit `849ae756`과 `Customization-ID: BANK-OM-011`
2. customization registry의 `BANK-OM-011`, `UNASSIGNED`, `active`
3. Source candidate Actions `Success`와 artifact 1개
4. 316 pass·7 operational skip·11 active ID·9 selector 수치
5. T25/T26 pass와 현재 candidate 결속
6. runtime simulation `2 pass·7 skip→block`,
   `operational_run_executed: false`
7. `Runtime contracts`의 실제 `0 workflow runs`
8. workflow input 5개와 고정 `PRODUCT_SHA`
9. Actions artifact 다운로드 위치

캡처는 공개 로그아웃 화면만 사용해 secret, token, password, 행내 URL을
포함하지 않는다. 그 때문에 `Runtime contracts` 캡처에는 권한 사용자에게만
보이는 `Run workflow` 버튼이 없음을 가이드에 명시했다.

검증:

```text
git diff --cached --check       pass
local Markdown links/images     pass
PNG signatures                  10/10
image dimensions                10/10 at 1280x720
sensitive runtime values        not captured
code or test behavior changed   no
source suite rerun              no (documentation/image-only batch)
runtime suite executed          no
```

source-only 성공과 deployment-ready의 경계, 11개 owner 미지정, API 4개·
browser 3개 미실행, release artifact·T90·T91·T94 부재, 미보호 브랜치
blocker는 그대로다. 원격 완료 여부는 이 절과 `258bb8a`가
`origin/claude/markdown-file-feedback-26933w` ancestry에 함께 있는지로
확인한다.

### 4.32 커스터마이징 구성품과 검사기 역할의 비개발자 설명

사용자가 요구한 “커스터마이징에 무엇이 들어가야 하고, 병합 후 무엇으로
들어간 것을 확인하며, 각 검사기는 무엇을 검사하는가”를 시연 가이드에
비개발자 표현으로 추가했다.

```text
branch                       claude/markdown-file-feedback-26933w
guide explanation commit     705bb4f93ec5605aa3ea018672e4b7f64cac7f09
product candidate            849ae756cd238f218b5e3a6c795a392305cb32ee
code/test behavior changed   no
runtime operational run      not executed
```

가이드에 추가한 customization 필수 구성:

- BANK-OM ID
- title/status/kind
- owner와 승인 경로
- `allowed_changed_paths`
- `required_changed_paths`
- `upgrade_watch.paths`
- 업무 contract와 필수 selector
- series 허용 여부와 `depends_on`
- 제품 commit의 `Customization-ID` trailer

`BANK-OM-011` 실제 예시는 제품 commit `849ae756`, 필수·감시 경로 6개,
InstanceCode·QueryReport contract, `depends_on: BANK-OM-010`, `active`,
`owner: UNASSIGNED`를 함께 보여준다. 따라서 소스 등록 완료와 owner blocker를
동시에 설명한다.

쉬운 설명을 고정한 검사기:

- 후보 잠금/T24 — 검사 대상을 정확한 SHA·tree·digest로 고정
- T25 — 승인한 공식 target이 candidate에 병합됐는지 확인
- T26 — active customization의 필수 파일·contract 생존 확인
- T30 — 제품 commit의 BANK-OM trailer가 정확히 하나인지 확인
- T31 — ID series·의존 순서·재사용·순환 확인
- T60-I — 필수 selector가 실제 파일·함수로 존재하는지 확인
- T61 — customization을 제거했을 때 테스트가 실패하는지 확인
- T62 — 실제 결과를 candidate·artifact에 묶고 skip/stale/exit 불일치를 차단
- T63 — 공식 원본 대비 신규 UI path/code 진단 증가 확인
- T90 — 실제 데이터 업그레이드 12단계 확인
- T91 — 검증한 동일 digest 산출물 승격 확인
- T94 — 서명한 내부망 반입 payload 동일성 확인

현재 상태 표현은 바뀌지 않는다. T25/T26/T30/T31과 T60-I 9/9는 pass,
T61은 Sybase/Tibero source 범위만 입증, T62 runtime은 0회, T63은
신규 path/code 0이지만 approval, T90/T91/T94는 미실행이다.

검증:

```text
git diff --cached --check       pass
local Markdown links/images     pass
named verifier rows             12 present
code or test behavior changed   no
source suite rerun              no (documentation-only batch)
runtime suite executed          no
```

원격 완료 여부는 이 절과 `705bb4f`가
`origin/claude/markdown-file-feedback-26933w` ancestry에 함께 있는지로
확인한다.

## 5. 테스트 결과

전체 명령:

```bash
OM_MIRROR_PATH=/private/tmp/om-ci-mirror-20260725 \
OPENMETADATA_PRODUCT_REPO=/private/tmp/om-product-rebuild \
  ./harness/.venv/bin/python -m pytest harness/tests tests/bank/contracts -ra
```

결과:

```text
316 passed, 7 skipped in 30.67s
```

초기 구현 기준은 148 passed, 35 skipped였다. 현재까지 168개 passing test가
추가됐고, T25-R과 실제 candidate evidence 묶음은 14개다.

고정 mirror를 연결해 기존 mirror 의존 35개도 모두 실행·통과했다. 남은 7개는
`OPENMETADATA_BASE_URL`이 없는 API selector 4개와
실제 Data Assertions·bank column·SchemaEditor URL이 없는 browser selector
3개다. T25-R 14개와 T60-I,
pytest/JUnit adapter 단위 테스트 중 skip은 없다.

제품 집중 테스트:

```bash
corepack yarn test src/utils/DatabaseServiceUtils.test.tsx --runInBand
```

결과:

```text
1 suite passed, 13 tests passed
```

## 6. 완료와 운영 검증을 구분한 현재 상태

| 영역 | 코드/스키마 | 단위 테스트 | 실제 운영 증거 |
|---|---:|---:|---:|
| T25-R snapshot 재구성 | source plan·owner·엔진·실 candidate 완료 | 완료 | 실제 candidate pass |
| T26~T29 vendor 등록·라우팅 | 완료 | 완료 | T25/T26 실 candidate pass |
| T60-I 구현 존재 | 완료 | 완료 | 9/9 selector resolve pass |
| T61 patch-kill | source·runtime plan/runner/workflow 완료 | 단위·무환경 fail-closed 완료 | Sybase/Tibero 2/5 pass, runtime high 3개 제거본 배포·실행 없음 |
| T62 test-result binding·runner | 완료 | 완료 | local fail-closed `2 required pass·7 skip→block`, 실제 runtime run 없음 |
| T63 UI typecheck baseline delta | 완료 | 10개 완료 | 실제 원본 396/후보 355, 신규 path/code 0·제거 41, verdict `approval` |
| BANK-OM-009 공통 검색 타입 | 완료 | focused Jest 18/18·T63 10개 완료 | 원본 396→후보 357, 신규 path/code 0·제거 39, 원격 run 30216708258 성공 |
| BANK-OM-010 알림 엔터티 ID fallback | 완료 | focused Jest 112/112·T63 10개 완료 | 원본 396→후보 356, 신규 path/code 0·제거 40, 원격 run 30219786626 성공 |
| BANK-OM-011 목록 변환 타입 계약 | 완료 | focused Jest 7/7·T63 10개 완료 | 원본 396→후보 355, 신규 path/code 0·제거 41, 원격 run 30222439344 성공 |
| T71/T72 운영 정책 | 완료 | 완료 | 조직 승인자·CI 연동 필요 |
| T80/T81 LLM memo | 완료 | 완료 | 실제 release memo 평가 데이터 없음 |
| T90 upgrade-run contract | 완료 | 완료 | Docker/DB/search/ingestion 실행 없음 |
| T91 release promotion | 완료 | 완료 | 실제 registry promotion 없음 |
| T92 retirement | 완료 | 완료 | 실제 retire 대상 없음 |
| T94 air-gap verification | 완료 | 완료 | 실제 bundle/key/signature 검증 없음 |

GitHub API 기준 governance branch
`claude/markdown-file-feedback-26933w`와 product branch
`codex/bank-vendor-1.13.1-rebuild`는 모두 `protected: false`이고 열린 PR이 없다.
따라서 현재 CI 성공은 재현 증거이지 GitHub가 우회를 차단하는 required check가
아니다. 저장소 관리자는 보호할 통합 브랜치, `Source candidate` required check,
지정 reviewer와 2인 승인 규칙을 정해야 한다. 이 외부 정책 변경은 자동 적용하지
않았다.

따라서 “게이트 엔진 구현 완료”와 “첫 production upgrade 검증 완료”를 같은 뜻으로
읽으면 안 된다.

## 7. 다음 실행 순서

1. 각 ID의 조직 owner와 두 사람 승인 라우팅을 확정한다.
2. `openmetadata-runtime` environment의 secret/variable을 설정하고
   `Runtime contracts` workflow에서 API 4개와 browser 3개를 실행해 9개
   selector 전체의 T62 candidate-bound pass를 만든다.
3. Node 22에서 후보가 만든 3개 UI diagnostic, 공통 검색 타입 39건, 알림
   엔터티 ID 타입 1건과 목록 변환 타입 1건은 수정 완료했고, T63은 공식 원본
   396건 대비 후보 355건, 신규 path/code 0을 확인했다. clean-cache 메시지
   변형 10건이
   남아 verdict는
   `approval`이다. full log를
   검토해 조직 기준선으로
   승인하거나 오류를 수정하고, 제품 전체 Java/UI build와 source-level test를
   candidate에 결속한다.
4. InstanceCode·QueryReport·Data Assertions 제거본을 각각 빌드·배포해 남은
   high 3개 runtime patch-kill을 실행한다.
5. runtime workflow의 YAML 결과를 조직의 장기 증거 저장소에 보존한다.
6. 실제 OM 구/신 스택에서 T90 12단계 evidence를 생성한다.
7. image/package/Helm digest, SBOM과 서명을 생성한다.
8. T91 release-lock으로 기존 artifact를 승격한다.
9. 실제 오프라인 키로 T94 반입 manifest를 서명하고 내부망에서 검증한다.

### 다음 작업자가 처음 실행할 명령

```bash
git switch claude/markdown-file-feedback-26933w
git pull --ff-only
git status --short --branch
git rev-parse HEAD
sed -n '1,220p' docs/04-진행/CLAUDE_REVIEW_HANDOFF.md
sed -n '1,220p' docs/00-사용가이드/비개발자_사용_가이드.md
```

그 다음에는 owner·승인 라우팅을 입력할 조직 결정을 먼저 확보하고, 실제
OpenMetadata 테스트 스택에서 API 4개와 browser 3개를 실행한다. 운영 URL이나
비밀값이 아직 없으면 임의로 성공 처리하지 말고 `skip/blocker`를 유지한다.

### Claude 이관 시 반드시 답할 다섯 질문

| 질문 | 이 문서에서 확인할 곳 |
|---|---|
| 최종 목적은 무엇인가 | §1 |
| 지금까지 무엇을 만들었는가 | §4.1~§4.27 |
| 어떤 방식으로 만들었는가 | 각 구현 절의 파일·개발 방식 |
| 무엇으로 검증했고 무엇이 미실행인가 | §5~§6 |
| 다음에 무엇을 어떤 순서로 할 것인가 | §7과 첫 실행 명령 |

## 8. Claude에게 요청하는 독립 검토

다음을 집중 검토한다.

1. 113개 원본 변경 경로가 7개 source-snapshot manifest의 allowed path에
   누락 없이 귀속됐고, 008이 그 과거 재구성에 섞이지 않는가.
2. required path가 각 기능의 최소 생존 상태를 대표하는가.
3. contract invariant와 required test ID가 실제 업무 요구를 정확히 표현하는가.
4. stale/malformed 증거가 어떤 경로에서도 pass나 approval로 약화되지 않는가.
5. break-glass가 machine verdict나 무결성 gate를 우회할 수 있는 경로가 있는가.
6. LLM memo에서 verdict/action이 새어 나갈 수 있는가.
7. release-lock이 검증 시점과 승격 시점 사이의 후보·이미지·Helm 변경을 모두
   잡는가.
8. retirement가 active ID 재사용이나 증거 없는 제거를 허용하는가.
9. air-gap payload/signature 구조에 순환 해시나 경로 이탈 취약점이 있는가.
10. T90의 12단계가 OpenMetadata 운영 실패 모드를 충분히 대표하는가.
11. T25-R이 unrelated snapshot merge나 path-level 오귀속으로 T25를 형식적으로
    우회할 수 있는 counterexample이 있는가.
12. 실제 7개 commit의 shared hunk 분리가 기능 경계와 맞으며, 특히 generated
    connector 파일의 Sybase/Tibero 순서가 리뷰 가능한가.
13. runtime workflow가 pytest crash, JUnit/exit 불일치, skip, stale artifact,
    악의적 workflow input을 어떤 경로에서도 pass로 약화하지 않는가.
14. pinned artifact upload와 90일 보존 계약이 실패·차단 증거까지 잃지 않고,
    실행 간 overwrite나 파일 누락을 허용하지 않는가.
15. predecessor source negative control이 대상 패치 이외의 차이 때문에
    거짓 `proven`을 만들 수 있는지, 그리고 JUnit failure와 test error를 모든
    경로에서 올바르게 구분하는가.
16. runtime patch-kill의 전후 health probe가 인증 실패, fixture 손상, UI 장애를
    target 기능 소실과 충분히 분리하는가.
17. ordered predecessor 방식이 candidate-minus-one이 아닌 탓에 거짓 `proven`을
    만들 counterexample이 있는가. 있다면 ID 격리 재빌드를 필수화해야 하는가.
18. counterfactual artifact digest와 deployment evidence digest만으로 실제 URL이
    그 바이트를 서비스했다는 결속이 충분한가.
19. `provenance: candidate-follow-up`이 T25-R에서만 제외되고 T26/T30/T31·
    runtime 결속에는 반드시 포함되는 경계가 우회 불가능한가.
20. `BANK-OM-008` 하나가 InstanceCode와 QueryReport의 공유 UI 타입 보강을
    표현하는 것이 단일 변경 목적 규칙에 맞는가, 아니면 더 나은 추적 모델이
    필요한가.
21. 공식 upstream 동일 toolchain 전체 실행은 396건, 후보는 355건이며 신규
    path/code 0·제거 41이다. 이 근거가 기준선 승인에 충분한가.
22. T63은 message substitution도 fingerprint해 10개 신규 변형을 드러낸다.
    이들을 approval 검토 근거로 두는 것이 맞는가, 자동 block해야 하는가.
23. `BANK-OM-009`의 `METADATA_SERVICE` mapping과 Curated Assets
    `DATA_ASSET` narrowing이 실제 검색 API의 heterogeneous 결과를 충분히
    표현하는가, 별도 `DataAssetSearchSource` union이 필요한가.
24. `BANK-OM-010`이 `_source.id`를 우선하고 hit `_id`로 fallback하는 계약이
    모든 검색 인덱스에서 실제 엔터티 UUID 의미를 보존하는가. `_id`와 source
    ID가 달라질 수 있는 인덱스가 있다면 해당 인덱스를 명시적으로 제외해야 하는가.
25. `BANK-OM-011`의 필수 transform 계약이 새로운 목록 호출자가 변환을 빼먹는
    문제는 컴파일 단계에서 차단하면서도, 잘못된 수동 transform의 런타임 의미
    오류를 충분히 테스트하게 하는가.

검토 결과는 `Blocking / Serious / Minor / Validated`로 나누고, 각 항목에 정확한
파일·라인·재현 테스트를 제시해 달라. 문서의 완료 표시가 아니라 코드와
counterexample을 기준으로 판단해야 한다.

## 9. 2026-07-27 정확 경로 검사기 개선

### 현재 작업 위치

- governance repository: `easyseop/openmetadata-test`
- branch: `codex/strict-manifest-gates`
- first strict-scope implementation commit: `291c6f2`
- product validation repository: `easyseop/OpenMetadata`
- unchanged product candidate: `849ae756cd238f218b5e3a6c795a392305cb32ee`
- 상세 진척도:
  [`STRICT_SCOPE_IMPROVEMENT_PROGRESS.md`](STRICT_SCOPE_IMPROVEMENT_PROGRESS.md)

### 이번에 구현한 내용

1. `materialize_exact_scopes.py`를 추가해 고정 snapshot inventory와 shared
   hunk owner map으로 BANK-OM-001~007의 source scope를 실제 파일 목록으로
   변환했다.
2. T25-R은 source-snapshot manifest의 glob, 중복, inventory 밖 파일, 실제
   공유 소유자와 manifest 소유자의 불일치를 `analysis_error`로 거부한다.
3. T26은 `required` 몇 개만 보지 않고 source manifest에 등록된 원본 파일
   전체를 확인한다. required 소실은 block, 나머지 등록 파일 소실은
   approval이다.
4. T40은 upstream 제품 영역뿐 아니라 검사기·등록부·문서를 포함한 모든 변경
   경로에 상한 범위를 적용한다.
5. T70 보호 범위를 checker, registration, test, 설계·기술·진행 문서,
   `STATUS.md`, `CLAUDE.md`까지 확대했다.

### 숫자와 검증

```text
113 source paths = 74 single-owner + 37 shared + 2 excluded
focused tests     = 39 passed
T25-R checkpoint  = pass (e1ffc5a1...)
source candidate  = T25/T26/T60-I/T30/T31 all pass (849ae756...)
plan digest       = sha256:05e653a8d91f49f7a4b73c0d14c27c0bd82a2d02714c7e19cee4b6914a07de98
```

### 다음 순서

1. T42를 설정·의존성 변화까지 확장하고 watch 후보와 연결 근거를 자동 제안
2. T41의 watched/intent 판정과 T43 임계값을 정책으로 명확화
3. T93으로 너무 넓은 범위와 새 변경 파일 누락을 별도 탐지
4. T50/T51의 빈 선언·scalar/list 형태 차이 보강
5. 설명용 HTML의 검사기 표·실제 diff·결과·향후 단계를 같은 정의로 동기화
6. 행내 환경에서 T61/T62/T90 계열 운영 증거 생성

다음 작업자는 과거 브랜치가 아니라 아래 명령으로 이어서 작업한다.

```bash
git fetch origin
git switch codex/strict-manifest-gates
git pull --ff-only
```
