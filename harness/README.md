# ACGH — 하네스 (실행 코드)

OpenMetadata 커스터마이징 자동 검증 도구의 구현.

> **통합 전략:** 기본 운영은 vendor merge이며, 현재 구현된
> `patchlock`·`reapply`·`resolve`·`replay`는 선택 patch-replay 모드다.
> T24~T29 candidate/ancestry/survival/conflict/routing과 실제 7개 snapshot
> 기능 + 4개 candidate-follow-up 등록부까지
> 구현됐고 T25-R은 ancestry 없는 snapshot의 안전한 재구성 계획과 candidate를
> 검증한다. 실제 7-ID vendor branch와 T62 runtime 실행 경계까지 구현했지만
> 운영 contract 전체 pass와 release artifact 생성 전에는 release pass가 아니다.

> **요구사항 충족(영역 A1~A8)·검증기 23종의 왜/안 지키면/방법론·전체 개발 범위·
> 설계 배경은 루트 [`../README.md`](../README.md) 가 정본이다.** 이 파일은 하네스
> 실행에 필요한 최소 정보만 둔다.

## 빠른 시작

```bash
pip install jsonschema pathspec pyyaml pytest
OPENMETADATA_PRODUCT_REPO=/path/to/OpenMetadata \
  python -m pytest harness/tests tests/bank/contracts
# 고정 mirror + product repo 연결 시 405개: 398 pass·7 operational skip
#   (2026-07-31 CI run 30606935109 기준)
# mirror·product repo 없이 실행하면 395 pass·10 skip — 늘어난 3개 skip이
#   mirror 의존 테스트이며, 실패가 아니다
bash harness/fixtures/fetch_upstream.sh            # 실제 OM 미러(없으면 미러 테스트 자동 skip)
```

Python 3.11 · git 2.43+ · 의존: PyYAML·jsonschema≥4.18·pathspec≥0.11.

## 실행기 종료코드

게이트 실행기 4개는 모두 `verdict.aggregate()` → `verdict.to_exit_code()`를
거친다. 손으로 쓴 `return 0`/`return 1`은 남아 있지 않으며
`tests/test_runner_exit_codes.py`가 AST로 이를 검사한다.

| 판정 | 종료코드 | 뜻 |
|---|---:|---|
| `pass` | 0 | 통과 |
| `block` | 1 | 규칙을 적용해 거절 |
| `approval` | 2 | 사람 판단 필요 |
| `analysis_error` | 3 | 판단 자체를 못 함 |

집계 severity rank(`pass < approval < block < analysis_error`)와 종료코드
순서는 **일부러 다르다.** 종료코드로 `max()`를 하면 `2(approval)`가
`1(block)`을 이겨 차단이 승인필요로 뒤집힌다(P0-3). 게이트가 하나도 없으면
`aggregate([])`는 `analysis_error`를 낸다(P0-4, fail-closed).

> **운영 주의:** `run_upgrade_watch.py`는 이전에 판정과 무관하게 `0`을
> 반환했다. 지금 저장된 1.13.1 결과의 gate 판정이 `approval`이므로 이 실행기는
> **`2`를 반환한다.** `$?`가 0인지만 보는 스크립트가 있으면 고쳐야 한다.
> 다만 이 실행기는 어느 workflow에서도 호출하지 않으므로 CI는 영향받지 않는다.
> CI가 부르는 것은 `run_source_candidate_gates.py`(8개 게이트 전부 `pass` →
> `0`)와 `run_source_patch_kills.py`뿐이다.

## 구현 모듈 (CI 기준 405개 테스트: 398 pass·7 operational skip)

| 모듈 | 담당 | 루트 README 검증기# / 영역 |
|---|---|---|
| `verdict.py` | 4상태 판정 집계(fail-closed) | 21 / A6 |
| `result_io.py` | 결과계약·CI 어댑터(원자적·stale=analysis_error) | A6 |
| `evidence.py` | 감사카드(승인/LLM 분리) | 22 / A6 |
| `binding.py` | SHA 결속(repo-qualified inputs) | 17 / A6 |
| `candidate.py` | 통합 전략·candidate-lock·결과 입력 결속 | 11 / A2·A3 |
| `ancestry.py` | vendor 공통 이력·승인 target 포함 검증 | 1 / A2 |
| `vendor_rebuild.py` | root snapshot 재구성 계획·공유 hunk 소유·candidate 검증 | 1 / A1·A2 |
| `survival.py`·`registry.py` | active ID 생존·7개 snapshot + candidate-follow-up 등록 그래프 | 1·14·15 / A1·A2 |
| `contracts.py` | contract 결속·required selector 파일/함수 구현 존재 | 14·15 / A6 |
| `conflicts.py`·`routing.py` | merge 해결 증거·vendor/replay 명시 라우팅 | 1 / A2 |
| `gitprim.py` | git 프리미티브(trailer·-z·tree) | — |
| `layout.py` | 경로 소유·glob 문법(공용) | 6·7 / A4 |
| `manifest.py` | manifest 스키마·의미검증 | 12 / A1 |
| `patchlock.py`·`integrator.py` | patch-lock(분리·CAS) | 11 / A3 |
| `invariants.py` | 커밋·ID 등록 검사 | 2·3 / A1 |
| `reapply.py`·`resolve.py` | 재적용 탐지/해결 2모드 | 1 / A2 |
| `replay.py` | clean-room replay | 5 / A3 |
| `drift.py` | 구현범위 drift(touched/net) | 6 / A4 |
| `zones.py` | 민감영역·의도 게이트 | 7 / A4 |
| `finalstate.py` | 최종상태 불변식(counterfactual) | 4 / A3 |
| `scope.py` | 보장범위 표(게이트 출력 결합) | — |
| `upgrade_watch.py`·`impact.py` | upgrade_watch(케이스 D)·영향분석 | 9·22 / A5 |
| `policy_drift.py` | 정책 노후화 drift | 8 / A5 |
| `verifier.py` | 선언형 verifier(비실행형) | 12 / A4 |
| `testruns.py`·`pytest_runs.py` | 필수 테스트 실행·JUnit/재시도·candidate/artifact/version 결속 | 14·17 / A6 |
| `tsc_baseline.py` | 공식 upstream 대비 UI typecheck 진단 multiset 비교 | 23 / A6 |
| `fastlane.py`·`breakglass.py` | 변경 유형별 경량 경로·긴급 예외 검증 | 19 / A7 |
| `impact_memo.py` | 근거 기반 LLM Memo·품질지표(판정권 없음) | 22 / A5 |
| `upgrade_run.py` | migration·차등·rollback 12단계 결과 계약 | 18 / A6 |
| `release.py` | 동일 candidate/image/Helm digest 승격 | 20 / A6 |
| `retirement.py` | active→retired 증거·상태 전환 | 3·4 / A1·A3 |
| `airgap.py` | 내부망 파일 해시·release-lock·오프라인 서명 재검증 | 20 / A6 |

입력(manifest·patch-source-lock·정책 YAML)·출력(acgh-result·change-evidence)·판정
4상태 상세는 루트 README '개발자 빠른 시작' 참조.

## T25-R vendor 재구성

`--repo`에는 공식 target과 root snapshot의 두 고정 commit object가 모두 있어야
한다. `plan`은 실제 tree diff가 등록한 113개 경로와 같은지 확인하고 결정적 JSON
계획을 출력한다.

```bash
acgh-vendor-rebuild \
  --repo /path/to/object-complete-repo \
  --registration registrations/kb-openmetadata \
  plan
```

실제 고정 Git 객체에서 source plan이 통과했으며 결과는 67개 단독 소유, 44개
공유 파일, 2개 제외 경로다. 공유 파일의 실제 symbol·JSON key·route·SQL block을
검사해 `registrations/kb-openmetadata/shared-path-owners.yaml`에 owner를
기록했다.

```bash
acgh-vendor-rebuild \
  --repo /path/to/object-complete-repo \
  --registration registrations/kb-openmetadata \
  verify \
  --candidate <full-candidate-sha> \
  --shared-owners registrations/kb-openmetadata/shared-path-owners.yaml
```

검증기는 candidate가 공식 target에서 시작했는지, unrelated snapshot commit을
merge하지 않았는지, commit마다 ID가 정확히 하나인지, 경로 소유가 맞는지,
registered JSON의 최종 의미 값과 나머지 파일 내용은 snapshot과 같은지, 제외
경로는 upstream 그대로인지 확인한다.

실제 재구성 결과와 재현 도구:

- `registrations/kb-openmetadata/source-candidate-evidence.yaml`
- `registrations/kb-openmetadata/reconstruct_series.py`
- `registrations/kb-openmetadata/run_source_candidate_gates.py`
- `registrations/kb-openmetadata/patch-kill-plan.yaml`
- `registrations/kb-openmetadata/source-patch-kill-evidence.yaml`
- `registrations/kb-openmetadata/run_source_patch_kills.py`
- product branch:
  `easyseop/OpenMetadata:codex/bank-vendor-1.13.1-rebuild`
- reconstruction checkpoint: `e1ffc5a1eb270c3225736544bb309a0c85af6d2c`
- current candidate: `849ae756cd238f218b5e3a6c795a392305cb32ee`

`RegistryEntry.provenance`는 원본 snapshot에서 재구성한 ID와 그 뒤 후보에서
추가한 안전 보강을 구분한다. `source-snapshot` 7개만 T25-R 재구성 계획에
들어가고, `candidate-follow-up`인 `BANK-OM-008`·`BANK-OM-009`·
`BANK-OM-010`·`BANK-OM-011`도
T26/T30/T31과 runtime
candidate lock에는 포함된다. 따라서 후속 수정을 과거 snapshot에 있었다고
왜곡하지 않으면서 현재 후보의 필수 상태는 계속 fail-closed로 검사한다.

## T61 source patch-kill

`run_source_patch_kills.py`는 고정 candidate와 plan이 일치하는지, 각
without-patch SHA가 candidate의 조상인지, 그 뒤에 해당 Customization-ID commit이
실제로 있는지, selector가 contract에 결속됐는지를 먼저 확인한다. 그 다음 별도
worktree에서 selector를 실행한다.

```bash
python harness/registrations/kb-openmetadata/run_source_patch_kills.py \
  --repo /path/to/locked/OpenMetadata \
  --harness harness \
  --registration harness/registrations/kb-openmetadata \
  --output /safe/evidence/source-patch-kill.yaml
```

JUnit상 assertion failure만 `proven/pass`다. 패치가 없는데 통과하면
`shell_test/block`, skip·test error면 `inconclusive/analysis_error`, pytest
내부 오류·timeout이면 `infra_error/analysis_error`다. 현재 Sybase와 Tibero 두 source experiment는
pass이며, InstanceCode·QueryReport·Data Assertions는 제거본을 실제 배포해야
하므로 pending이다. 즉 전체 high/critical T61 통과가 아니라 2/5 scoped pass다.
Source CI artifact는 실행별 고유 이름으로 90일 보존된다.

## T61 deployed runtime patch-kill

`Runtime patch-kill` workflow는 source plan에서 pending인 InstanceCode,
QueryReport, Data Assertions 중 하나를 별도 제거본 환경에서 검사한다. 대상
required selector는 연속 두 번 실패해야 하고, 기능과 독립적인 API·fixture·UI
health probe는 실행 전후 모두 통과해야 한다. 대상 통과는 `block`, probe
실패·skip·error·timeout·JUnit/exit 불일치는 `analysis_error`다.

정본 plan은 `runtime-patch-kill-plan.yaml`이다. full candidate와 predecessor
source/tree, 배포 artifact digest, source→artifact·fixture 배포 기록 digest,
governance/suite digest, 환경 ID를 결과에 묶고 전용
`openmetadata-runtime-patch-kill` 승인 환경에서 한 스택당 직렬 실행한다.
증거는 덮어쓰기 없이 90일 보존한다. 세 제거본의 실제 build·배포·실행은 아직
0건이며, 고정 predecessor가 완전한 candidate-minus-one은 아니라는 한계가 있다.

## T62 실제 환경 계약 실행

GitHub Actions의 `Runtime contracts`를 수동 실행하거나 아래 runner를 사용한다.
Playwright가 필요한 실제 브라우저 계약은 `harness[runtime]` 의존성과 Chromium을
설치해야 한다.

```bash
python -m pip install -e "harness[dev,runtime]"
python -m playwright install chromium
python harness/registrations/kb-openmetadata/run_runtime_contracts.py \
  --repo /path/to/locked/OpenMetadata \
  --harness harness \
  --registration harness/registrations/kb-openmetadata \
  --artifact-digest sha256:<deployed-artifact-digest> \
  --output-dir /safe/evidence/path
```

이 행내 workflow의 필수 환경은 `OPENMETADATA_BASE_URL`, auth token,
`BANK_CONTRACT_QUERY_ID`, `BANK_FAILED_ASSERTION_FQN`,
`BANK_COLUMN_TABLE_FQN`, `BANK_COLUMN_NAME`, `BANK_IME_EDITOR_URL`,
`BANK_DATA_ASSERTIONS_URL`, `BANK_COLUMN_UI_URL`이다.
로그인된 브라우저 상태가 필요하면 JSON storage state를 base64로 인코딩해
`BANK_BROWSER_STORAGE_STATE_B64`로 주입한다. 비밀값은 파일·인수인계서에
기록하지 않는다. 하나라도 skip이면 runner는 `block`으로 종료한다.

출력은 `candidate-lock.yaml`, `test-run-set.yaml`, `acgh-result.yaml`이다.
`interpret_runtime_result.py`가 실제 process exit와 result를 다시 대조하고,
누락·파손·stale·불일치를 `analysis_error`로 처리한다.

## T63 UI typecheck 기준선 비교

공식 upstream과 candidate를 같은 Node/Yarn·생성 단계·명령으로 실행한 전체
로그를 비교한다. 경로와 TypeScript 오류 코드의 **multiset**을 사용하므로 같은
오류가 한 번 더 생긴 경우도 신규 진단으로 차단한다.

```bash
python harness/registrations/kb-openmetadata/compare_ui_typecheck.py \
  --harness harness \
  --upstream-log /safe/evidence/upstream-tsc.log \
  --candidate-log /safe/evidence/candidate-tsc.log \
  --upstream-exit 2 \
  --candidate-exit 2
```

후보에 신규 진단이 있으면 `block`, 로그 형식이나 exit가 모순이면
`analysis_error`, 둘 다 깨끗하면 `pass`다. 공식 원본과 후보가 같은 비영
기준선을 가지면 `approval`이다. 현재 Node 22 증거는 upstream 396건·141파일,
candidate 356건·135파일, 신규 path/code 0건·제거 40건이다. 메시지 multiset도
별도 fingerprint해 신규 변형 4건·제거 변형 44건을 review 대상으로 남겼으며
`ui-typecheck-baseline-evidence.yaml`에 고정했다. 메시지 내용만 같은
경로·코드 안에서 바뀌는 경우도 이제 탐지하지만, TypeScript가 같은 union을
다르게 출력할 수 있어 자동 block 대신 approval 근거로 남긴다. full log review
또는 전체 수정 없이는 release pass가 아니다.

GitHub workflow는 결과가 pass·block·approval·analysis_error 중 무엇이든 이
3개 파일을 `runtime-contract-evidence-<run_id>-<run_attempt>` artifact로
업로드한다. 같은 실행 증거는 덮어쓸 수 없고 90일 보존되며, 파일이 없으면 업로드
단계도 실패한다. artifact ID·GitHub digest·URL은 job summary에서 확인한다.
90일을 넘는 조직 감사 보존은 만료 전에 별도 장기 저장소로 이관한다.

## 디렉터리

```
harness/
  acgh/            # 구현 모듈(위 표)
    schema/        # 모든 입력·결과·attestation·release/transfer JSON Schema
  registrations/   # 실제 7개 snapshot + 3개 candidate-follow-up manifest·contract·registry
  policies/        # repository-layout.yaml · sensitive-zones.yaml
  fixtures/        # fetch_upstream.sh · upstream-lock.yaml
  tests/           # 모듈별 테스트(conftest.py가 실제 미러 제공)
  pyproject.toml
```

## 문제 해결

- `ModuleNotFoundError: jsonschema/pathspec` → `pip install jsonschema pathspec`.
- 미러 의존 테스트가 skip → `bash fixtures/fetch_upstream.sh` 실행 후 재시도.
- 프록시/TLS 오류 → `/root/.ccr/README.md` 참조.
