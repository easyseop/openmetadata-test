# Phase 번들링 Codex 구현 검토

> 검토일: 2026-08-07
> 검토 commit: `446b5a0e53`
> 대상 보고서: `PHASE_BUNDLING_구현완료_검토요청_20260807.md`
> 결론: **검토용 구현은 원격 공유 가능하지만, 운영 완료 또는 P0 완료로 승인할 수 없다.**

## 1. 검토 결과 요약

기존 gate 함수를 재사용하는 방향, verdict 집계, premerge·postmerge catalog 구분,
candidate 선택 구조는 설계 방향과 대체로 일치한다. 작성된 phase 테스트 125개와 기존
`test_verdict.py`, `test_candidate.py`는 재실행에 성공했다.

그러나 테스트가 통과한 사실과 운영 가능한 phase 번들러가 완성됐다는 결론은 다르다.
다음 P0 문제가 남아 있어 현재 상태를 `구현 완료` 또는 `P0 74/74 완료`로 승인하지
않는다.

| 우선순위 | 문제 | 영향 |
|---|---|---|
| P0 | 실제 phase 명령과 전체 orchestration 없음 | 사용자가 한 명령으로 phase를 실행할 수 없음 |
| P0 | 결과 digest가 gate 사유·상세·evidence를 보호하지 않음 | 검토 내용이 변조돼도 기존 승인이 유효할 수 있음 |
| P0 | `GateSpec.timeout`이 실제로 적용되지 않음 | 멈춘 gate가 무기한 실행될 수 있음 |
| P0 | `run_gates()`가 phase catalog를 강제하지 않음 | 잘못된 phase의 gate도 호출자가 넣으면 실행됨 |
| P0 | 활성 출처가 0개여도 consistency 통과 | 기준을 확인하지 않고 검사가 시작될 수 있음 |
| P0 | debt thresholds가 없으면 기본값으로 실행 | 보고서의 fail-closed 설명과 실제 코드가 다름 |
| P1 | phase 승인자·시각·근거 검증 없음 | digest와 phase만 맞으면 빈 승인도 유효함 |
| P1 | `GateExecution.detail`이 시스템 JSON에서 누락 | watch 제안·debt metrics가 evidence와 실무자 출력에서 사라짐 |

## 2. 확인된 P0 문제

### 2.1 실제 실행 명령과 전체 orchestration 부재

`candidate_select`, `preflight`, `phase`, `rollup` 모듈은 존재하지만 다음 명령은
`om_workflow.py --help`에 없다.

```text
candidate-select
consistency
preflight
premerge-check
postmerge-check
prep-official
status
```

따라서 현재 사용자는 직접 Python 함수를 조합해야 한다. 계획의 목적인 “phase 단위로
묶어 사람 손을 줄인다”가 아직 달성되지 않았다.

또한 postmerge catalog 이름에는 `validate`, `source`, `contract`가 있지만
`build_postmerge_catalog()`가 실제로 만드는 GateSpec은 ancestry, sensitive-zones,
debt, exact-scope 네 개뿐이다.

**필요 조치:** `om_workflow.py`에 phase 명령을 연결하고, 한 실행 안에서
candidate 선택 → preflight → catalog 구성 → gate 실행 → 집계 → 3단 출력 → evidence
저장을 수행하는 end-to-end 테스트를 추가한다.

### 2.2 승인 digest가 실제 검토 내용을 보호하지 않음

`PhaseResult.canonical_payload()`에는 gate의 `reasons`, `evidence`, `detail`이 없다.
`verify_phase_result()`는 canonical payload의 digest와 system JSON 안의 digest 문자열만
비교한다.

재현 결과:

```text
system_json.gates[0].reasons를 "original"에서 "TAMPERED"로 변경
verify_phase_result(...) → (True, "consistent")
```

즉 담당자가 읽고 승인해야 할 차단 사유나 경로 설명이 바뀌어도 탐지되지 않는다.

**필요 조치:** 승인 판단에 사용하는 gate 사유, evidence 식별자, 상세 결과 또는 이들의
digest와 harness version·gate catalog digest를 canonical payload에 포함한다. 저장된
system JSON도 canonical payload에서 다시 생성하거나 두 구조의 완전한 일치를 검증한다.

### 2.3 timeout 미구현

`GateSpec.timeout` 필드는 선언돼 있지만 `execute_gate()`는 `spec.run()`을 직접 호출한다.
현재 C53 테스트는 시간이 초과되는 상황을 만들지 않고 gate 함수가 스스로
`TimeoutError`를 던지도록 작성돼 있다.

재현 결과:

```text
timeout=0.01, gate 실행시간=0.2초
결과: elapsed=0.205, execution_status=executed, verdict=pass
```

**필요 조치:** subprocess 기반 gate에는 실제 timeout을 적용하고, 함수 호출 gate는
프로세스 격리 또는 명시적으로 timeout 비지원 상태를 선언한다. 실제로 잠드는 gate를
사용한 장애 주입 테스트가 필요하다.

`execute_gate()`가 `BaseException`까지 잡는 것도 수정 대상이다. `KeyboardInterrupt`,
`SystemExit`까지 일반 gate 실패로 삼키지 않도록 기본적으로 `Exception`을 처리해야 한다.

### 2.4 phase catalog 강제 부재

`assert_gate_applicable()` 함수는 있지만 `run_gates()`가 호출하지 않는다. 따라서
호출자가 premerge 실행에 `sensitive-zones` GateSpec을 전달하면 그대로 실행된다.

**필요 조치:** `run_gates()`가 gate 이름을 phase catalog와 대조하거나, 외부에서 임의
GateSpec을 넘길 수 없는 phase별 runner를 제공한다. premerge에 postmerge gate를 넣은
end-to-end 음성 테스트가 필요하다.

### 2.5 활성 기준이 없어도 consistency 통과

`check_active_source_consistency([])`는 SHA 집합 크기가 0이므로 일치 상태로 판정한다.

재현 결과:

```text
active_sources=[]
ready=true
candidate_consistency=ok, "all active sources pin (none)"
```

**필요 조치:** 활성 출처가 0개면 blocking `missing`으로 처리한다. 최소 한 개의 승인된
candidate lock이 있어야 consistency 검사가 가능하다.

### 2.6 debt threshold 부재 시 fail-closed하지 않음

완료보고서는 change-intent와 debt-threshold가 없으면 postmerge가 fail-closed한다고
설명한다. 그러나 `build_postmerge_catalog()`은 thresholds가 없으면
`debt.DEFAULT_THRESHOLDS`를 사용한다.

**필요 조치:** 운영 정책이 “승인된 threshold 필수”라면 누락 시 T43을
`skipped_missing_input`으로 만들고 phase를 incomplete로 처리한다. 기본값 사용이 정책이면
보고서와 설계를 그에 맞게 변경하고 기본값 digest를 판단 입력에 포함한다.

## 3. 확인된 P1 문제

### 3.1 phase 승인 필드 검증 없음

다음처럼 승인자·시각·근거가 없는 dict도 `approval_binds()`가 승인한다.

```text
{"target_result_digest": <digest>, "phase": "postmerge"}
→ (True, ())
```

candidate lock 승인과 같은 수준으로 approver, approved_at, rationale의 존재·형식·
자리표시자를 검증해야 한다.

### 3.2 gate 상세 결과 유실

`GateOutcome.detail`은 `GateExecution`까지 전달되지만 `GateExecution.to_json()`에서
제외된다. 이 때문에 watch-suggest packet과 debt metrics가 system JSON·실무자 상세에서
사라진다.

**필요 조치:** detail을 시스템 JSON에 포함하고, 관리자 출력에는 요약만, 실무자
출력에는 전체 상세 또는 evidence 경로를 제공한다.

## 4. 통과 확인 사항

- phase 테스트: `125 passed`, 작성된 테스트의 pytest skip 없음
- 기존 회귀: `test_verdict.py`, `test_candidate.py` 통과
- `SEVERITY_RANK` 집계와 네 verdict 종료코드 일치
- candidate active pointer가 최신 시각을 자동 선택하지 않음
- 기존 `CandidateLock` schema v1·v2 재사용
- T42 실제 runner subprocess parity 테스트 존재 및 현재 환경에서 실행
- 기존 하네스 gate 판정 함수를 호출하고 별도 판정 로직을 만들지 않은 점 확인
- C106, C112, C75/C77 일부가 미구현이라는 원 보고서의 고지는 정확함

## 5. 판정

| 항목 | 판정 |
|---|---|
| 설계 방향 | 적합 |
| 라이브러리 단위 구현 | 검토 가능한 수준 |
| 작성된 테스트 실행 | 통과 |
| P0 완료 주장 | **승인 불가** |
| 운영 사용 가능 | **불가** |
| 원격 공유 | 검토용 WIP branch로 가능 |

다음 완료 기준은 위 P0 여섯 건 수정, 각 반례 테스트 추가, `om_workflow.py` phase
명령 연결, end-to-end 실행 결과 확인이다. 수정 전에는 branch를 병합하거나 운영 승인
기준으로 사용하지 않는다.

## 6. 재현 명령

```bash
cd <openmetadata-test-phase-bundling>
PYTHONPATH="$PWD/harness" ../review-openmetadata-test/.venv/bin/python \
  -m pytest harness/tests/test_phase_*.py -q
```

```bash
PYTHONPATH="$PWD/harness" ../review-openmetadata-test/.venv/bin/python \
  -m pytest harness/tests/test_verdict.py harness/tests/test_candidate.py -q
```
