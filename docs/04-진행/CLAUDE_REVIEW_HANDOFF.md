# Claude 독립 검토 인수인계

> 작성일: 2026-07-25
> 대상 브랜치: `claude/markdown-file-feedback-26933w`
> 변경 전 기준 커밋: `9d2a174` (`implement T25 vendor ancestry gate`)
> 마지막 검증 구현 커밋: `81524aa`
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

주의: required test ID는 테스트 **명세**다. 해당 테스트 파일을 이 저장소에
가짜로 만들어 통과시키지 않았다.

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
- candidate: `e1ffc5a1eb270c3225736544bb309a0c85af6d2c`
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

source candidate-lock digest는
`sha256:fb05306222a64581d5aea6894fb8c99dd9fb4080ac2bb89f66f31ee1078243c4`다.
그 lock의 artifact digest는 source Git tree identity를 결속한다. 아직 Java/UI
binary, container image 또는 release package digest를 뜻하지 않는다.

## 5. 테스트 결과

전체 명령:

```bash
./harness/.venv/bin/python -m pytest harness/tests -ra
```

결과:

```text
236 passed, 35 skipped in 25.87s
```

초기 구현 기준은 148 passed, 35 skipped였다. 현재까지 88개 passing test가
추가됐고, T25-R과 실제 candidate evidence 묶음은 14개다.

35개 skip은 `/home/user/om-mirror`가 없는 현재 macOS 작업 환경에서 실제
OpenMetadata 미러 기반 테스트가 자동 skip된 것이다. 이번에 추가한 T25-R
14개 테스트 중 skip은 없다.

## 6. 완료와 운영 검증을 구분한 현재 상태

| 영역 | 코드/스키마 | 단위 테스트 | 실제 운영 증거 |
|---|---:|---:|---:|
| T25-R snapshot 재구성 | source plan·owner·엔진·실 candidate 완료 | 완료 | 실제 candidate pass |
| T26~T29 vendor 등록·라우팅 | 완료 | 완료 | T25/T26 실 candidate pass |
| T62 test-result binding | 완료 | 완료 | 실제 7개 contract run 없음 |
| T71/T72 운영 정책 | 완료 | 완료 | 조직 승인자·CI 연동 필요 |
| T80/T81 LLM memo | 완료 | 완료 | 실제 release memo 평가 데이터 없음 |
| T90 upgrade-run contract | 완료 | 완료 | Docker/DB/search/ingestion 실행 없음 |
| T91 release promotion | 완료 | 완료 | 실제 registry promotion 없음 |
| T92 retirement | 완료 | 완료 | 실제 retire 대상 없음 |
| T94 air-gap verification | 완료 | 완료 | 실제 bundle/key/signature 검증 없음 |

따라서 “게이트 엔진 구현 완료”와 “첫 production upgrade 검증 완료”를 같은 뜻으로
읽으면 안 된다.

## 7. 다음 실행 순서

1. 각 ID의 조직 owner와 두 사람 승인 라우팅을 확정한다.
2. `contracts.yaml`의 7개 테스트를 실제 kb runtime suite에 구현한다.
3. 제품 전체 Java/UI build와 source-level test를 실행해 candidate에 결속한다.
4. high 5개를 우선 patch-kill로 검증한다.
5. T62 형식으로 candidate-bound test-run-set을 생성한다.
6. 실제 OM 구/신 스택에서 T90 12단계 evidence를 생성한다.
7. image/package/Helm digest, SBOM과 서명을 생성한다.
8. T91 release-lock으로 기존 artifact를 승격한다.
9. 실제 오프라인 키로 T94 반입 manifest를 서명하고 내부망에서 검증한다.

## 8. Claude에게 요청하는 독립 검토

다음을 집중 검토한다.

1. 113개 변경 경로가 7개 manifest의 allowed path에 누락 없이 귀속됐는가.
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

검토 결과는 `Blocking / Serious / Minor / Validated`로 나누고, 각 항목에 정확한
파일·라인·재현 테스트를 제시해 달라. 문서의 완료 표시가 아니라 코드와
counterexample을 기준으로 판단해야 한다.
