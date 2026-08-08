# Phase 번들링 개발계획 (테스트 케이스 도출용)

> 브랜치: `codex/phase-bundling` (격리 worktree). 현재 예행연습 브랜치·evidence·제품 코드·vendor merge **무수정**, commit/push 안 함.
> 목적: 하네스 명령을 phase 단위로 묶어 사람 손을 줄인다. **gate 로직은 기존 러너를 호출(재구현 금지)** → 회귀 test로 결과 동일 보장.
> 이 문서를 토대로 테스트 케이스를 정의한다. 각 컴포넌트에 **입력/출력/동작/완료정의(DoD)** 를 명시했다.

## 0. 확정 사실 (설계 전제)
- 정본 candidate = `8ac18ad053d9274774e274ba17b35911ac0b9dcb` (tree `e86980f6…`). `d952a838`=최초 snapshot(provenance), `85e60d42`=동일 tree 병렬 commit(provenance).
- 기존 `acgh/verdict.py`: `EXIT_CODE={pass:0, block:1, approval:2, analysis_error:3}`, `aggregate()`, `to_exit_code()`. **verdict 4종 고정, 신설 금지.**
- 기존 `acgh/candidate.py`: `CandidateLock`/`CandidateIdentity(repository, commit_sha, tree_sha, artifact_digest)` — **재사용, candidate_lock.py 신설 금지.**
- 기존 gate 러너: `run_upgrade_watch.py`(T42), `run_upgrade_risk_gates.py`(T41/T43/T93/T51·T52), `om_workflow.py source|validate`.
- `om-temp-1.13.1` 등록엔 `change-intent.yaml` 없음 → T41은 입력 미비 시 `skipped_missing_input`.
- OM_CODE_REPO는 blobless partial clone(structdiff blob은 lazy-fetch 가능).

## 1. 아키텍처 (2계층)
- **불변 계층(기존):** acgh gate 모듈·러너·verdict·candidate. 건드리지 않음.
- **신규 오케스트레이션 계층:** candidate 선택·정합성·preflight·gate 독립실행 래퍼·rollup·phase 커맨드. 기존을 **호출/취합**만.

## 2. 신규/변경 파일
| 파일 | 종류 | 내용 |
|---|---|---|
| `harness/acgh/candidate_select.py` | 신규 | 승인된 활성 candidate-lock 최신 선택 (candidate.py 재사용) |
| `harness/acgh/consistency.py` | 신규 | 활성 기준 SHA 정합성 검사 |
| `harness/acgh/preflight.py` | 신규 | 입력 일괄 사전검사 → preflight.json |
| `harness/acgh/phase.py` | 신규 | gate 독립실행 래퍼 + phase 집계(execution_status/phase_status) |
| `harness/acgh/rollup.py` | 신규 | 3단 출력 생성 |
| `harness/om_workflow.py` | 변경 | 서브커맨드 추가(candidate-select, consistency, preflight, premerge-check, postmerge-check, prep-official, status), `risk --conflict-rate` optional |
| `harness/registrations/kb-openmetadata/run_upgrade_risk_gates.py`(+shim) | 변경 | T43 conflict-rate 분리, gate별 execution_status 반환 |
| `harness/registrations/om-temp-1.13.1/candidate-locks/<sha>.yaml` | 신규 | 기술 기준(commit/tree/repo/digest) |
| `harness/registrations/om-temp-1.13.1/candidate-locks/<sha>.approval.yaml` | 신규 | approver/시각/근거 + `candidate_lock_digest` |
| `harness/tests/test_phase_*.py` | 신규 | 회귀/단위 test |

## 3. 데이터 구조

### 3.1 candidate-lock (`<sha>.yaml`) — 기술 기준만
```yaml
schema_version: 1
repository: om-temp-real-1.13.1
commit_sha: 8ac18ad053d9274774e274ba17b35911ac0b9dcb
tree_sha:   e86980f6d71295465fe6e75e5169fab57cebd4c4
artifact_digest: sha256:...   # docker image digest 등(있으면)
```
### 3.2 approval (`<sha>.approval.yaml`) — lock과 분리
```yaml
candidate_lock_digest: sha256:<lock 파일 정규화 digest>
approver: <사람>
approved_at: 2026-08-07T..Z
rationale: "Runtime Contract 9개 통과 candidate"
```
### 3.3 gate 결과(공통)
```json
{"name":"T41_sensitive_zones","verdict":"pass|approval|block|analysis_error|null",
 "execution_status":"executed|skipped_missing_input|blocked_by_preflight",
 "reasons":[...], "missing":[...], "target_count":{"checked":N,"total":M}}
```
### 3.4 phase 결과(run manifest)
```json
{"run_id":"...","phase":"premerge|postmerge","phase_status":"complete|incomplete",
 "overall_verdict":"pass|approval|block|analysis_error","exit_code":0,
 "upstream":{"base":"...","target":"..."},"candidate":{"commit_sha":"8ac18ad0…","tree_sha":"e86980f6…"},
 "gates":[<3.3>...], "inputs_digest":"sha256:..."}
```

## 4. 컴포넌트 상세 (입력/출력/동작/DoD)

### 4.1 candidate_select
- 입력: `registration` 경로.
- 동작: `candidate-locks/*.yaml` 중 **유효 approval(=approval.candidate_lock_digest == 해당 lock의 정규화 digest)** 을 가진 것만 후보 → `approved_at` 최신 1개 선택.
- 출력: `CandidateIdentity`(commit/tree/repo) + 선택 근거.
- 오류: 승인 lock 0개 → `analysis_error`("no approved candidate-lock"); digest 불일치 lock은 후보에서 제외(+경고).
- **DoD:** 승인 2개면 최신 선택, digest 깨진 approval은 무시, 0개면 실패.

### 4.2 consistency (활성 기준만)
- 입력: 선택된 lock + 활성 출처(commit-inventory.custom_head_sha, Runtime candidate-lock, Docker image revision).
- 동작: **활성 출처끼리 + 선택 lock**의 commit_sha 일치 확인. **과거 값(registry.source.snapshot_sha=d952a838, 과거 proposal/evidence)은 provenance로 표시하고 비교 제외.**
- 출력: `{consistent: bool, active:{...}, provenance:{...}, mismatches:[{file,value}]}`.
- 오류: 활성 출처 불일치 → 검사 시작 금지(STOP) + 파일·값 출력.
- **DoD:** d952a838가 달라도 통과(provenance), 활성 출처 하나 변조 시 STOP+지목.

### 4.3 preflight
- 입력: version, base, target, candidate(commit_sha), [conflict_rate].
- 검사 항목(각 ok|missing|unreachable):
  - ref: base/target/candidate **resolve + commit/tree 객체 존재**; structdiff 대상 경로 **blob 접근**(불가 시 "upstream fetch 필요" 지시).
  - 필수 파일: layout/zones/manifests/registry 존재; T41용 change-intent 존재?; T43용 debt-thresholds + conflict_rate 존재?
  - consistency(4.2) 통과 여부.
- 출력: `preflight.json`. blocking 결손(필수 ref/파일 없음, consistency STOP) → phase 실행 거부(`phase_status=blocked_by_preflight`, `overall_verdict=analysis_error`, exit 3).
- **DoD:** change-intent 없음 → T41 예고 skipped, blocking 아님; base 객체 없음 → blocking STOP.

### 4.4 phase.run_gates (gate 독립 실행)
- 입력: gate 목록 + 고정 candidate_sha + 공통 입력.
- 동작: 각 gate를 **기존 러너/함수 호출**로 실행, 예외/입력미비는 그 gate만 `skipped_missing_input`(verdict=null) 처리하고 **다른 gate 계속**. **candidate_sha는 실행 내내 고정(재조회 없음).**
- 출력: gate 결과 리스트(3.3).
- **DoD:** conflict_rate 없음 → T43만 skipped, T42/T41/T93/T51·T52는 정상 실행.

### 4.5 phase aggregate + exit
- 규칙: verdict는 `verdict.aggregate([executed gate verdicts])`. **필수 gate 중 skipped 있으면 `phase_status=incomplete` & `overall_verdict=analysis_error`.** 없으면 `complete`.
- exit: `verdict.EXIT_CODE[overall_verdict]` (pass0/block1/approval2/analysis_error3). incomplete 전용 코드 없음(=3).
- **DoD:** T43 skipped면 overall=analysis_error·exit3·phase_status=incomplete; 모두 pass면 exit0.

### 4.6 rollup (3단)
- 입력: phase 결과(3.4).
- 출력: (a) 관리자 요약(정상/검토/미실행/차단 수 + 검증대상 수 + 다음행동), (b) 실무자 상세(gate별 verdict/SHA/BANK-OM ID·경로/누락/재실행), (c) 시스템 JSON(입력·digest·SHA·사유·승인).
- 불변식: 세 출력의 verdict·수량 동일.
- **DoD:** 같은 run에서 세 출력 수치 일치(불일치 시 test 실패).

### 4.7 premerge-check / postmerge-check / prep-official / status
- `premerge-check --version --base --target [--run-id] [--conflict-rate]`: candidate=select(4.1)→consistency(4.2)→preflight(4.3)→gates{T42,T41,T93,T51·T52[,T43]}→aggregate→rollup.
- `postmerge-check --version --candidate-ref [--run-id]`: preflight→기존 `validate`+`source` 러너 래핑→aggregate→rollup. (병합 후보 있을 때만 실제 실행; 지금은 명령+단위 test.)
- `prep-official --version --target-tag`: upstream fetch·commit/tree 검증·official/om-X 생성(idempotent). 태그 없으면 STOP.
- `status --run-id`: evidence 읽어 3단 출력(read-only).

## 5. 회귀 test 전략 (핵심)
- **parity:** 고정 base=official/om-1.13.1, target=official/om-1.13.2, candidate=8ac18ad에서
  `premerge-check`의 gate별 `{name, verdict, reasons, target_count}` == 직접 실행한 `run_upgrade_watch.py`(T42) + `run_upgrade_risk_gates.py`(T41/T93/T51·T52; T43은 conflict_rate 줄 때만) 결과와 **동일**.
- conflict_rate 유/무 두 경우 모두 검증(무: T43 skipped, 유: T43 포함 parity).
- 기존 러너 결과는 골든 파일로 저장 후 비교.

## 6. 사람 STOP 지점 (자동 통과 금지)
1. candidate 정본 승인(8ac18ad lock approval) 2. change-intent/conflict-rate 최초 기준 승인
3. T42·T93 approval 검토 4. 업무 충돌 해소 5. 최종 sign-off.

## 7. 구현 순서 + 단계별 DoD
1. candidate_select + lock/approval seed → 4.1 DoD test 통과
2. consistency → 4.2 DoD
3. preflight → 4.3 DoD
4. phase.run_gates + aggregate/exit → 4.4·4.5 DoD
5. rollup → 4.6 DoD
6. premerge-check → **5. parity test 통과**
7. postmerge-check(명령+단위 test) 8. prep-official 9. status
- 각 단계 test 먼저(레드) → 구현(그린).

## 8. 테스트 케이스 시드 (여기서 확장)
> 설치된 스킬 활용: 결정론 동작=`/test`(TDD/커버리지), 불변식(SHA 고정·aggregate·digest)=`/property-based-testing`.

| # | 컴포넌트 | 입력 | 기대 |
|---|---|---|---|
| C1 | candidate_select | 승인 lock 2개(시각 다름) | 최신 approved 선택 |
| C2 | candidate_select | approval.digest ≠ lock | 그 lock 제외 |
| C3 | candidate_select | 승인 lock 0 | analysis_error |
| C4 | consistency | 활성 출처 전부 8ac18ad | consistent=true |
| C5 | consistency | Runtime lock만 다른 SHA | STOP + 그 파일/값 지목 |
| C6 | consistency | registry.snapshot_sha=d952a838(과거) | provenance, 통과 |
| C7 | preflight | change-intent 없음 | T41 skipped 예고, blocking 아님 |
| C8 | preflight | base 객체 없음 | blocking STOP, exit3 |
| C9 | phase.run_gates | conflict_rate 없음 | T43 skipped, 나머지 executed |
| C10 | aggregate | 필수 gate 1개 skipped | phase_status=incomplete, overall=analysis_error, exit3 |
| C11 | aggregate | 모든 executed=pass | overall=pass, exit0 |
| C12 | aggregate | 하나 approval, 나머지 pass | overall=approval, exit2 |
| C13 | SHA 고정(PBT) | 실행 중 branch가 움직여도 | 사용 SHA 불변(고정값) |
| C14 | rollup | 임의 phase 결과 | 관리자/실무자/JSON verdict·수량 동일 |
| C15 | parity | base/target/8ac18ad | premerge gate == 기존 러너 gate |
| C16 | parity | +conflict_rate | T43 포함 parity |
| C17 | approval digest(PBT) | lock 내용 변경 | 기존 approval 무효 |
| C18 | prep-official | 1.13.2 태그 존재 | official/om-1.13.2 생성, tree 일치 |
| C19 | prep-official | 태그 없음 | STOP, 생성 안 함 |
| C20 | 종료코드 | 각 verdict | EXIT_CODE 표와 일치 |

## 9. 보고 (완료 시)
병합하지 않고 **변경 파일 목록 + test 결과(pass/fail/skip) + 기존 명령과의 parity 비교**를 먼저 보고. 승인 후에만 다음 단계.
