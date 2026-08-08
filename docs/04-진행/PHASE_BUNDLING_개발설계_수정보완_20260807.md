# Phase 번들링 개발설계 수정보완

> 작성일: 2026-08-07  
> 대상 계획: `PHASE_BUNDLING_개발계획_20260807.md`  
> 목적: 구현 전에 기준 선택, 단계 분리, 오류 처리, 승인 결속 방식을 보완한다.  
> 관련 테스트: `PHASE_BUNDLING_반례테스트케이스_20260807.md`

## 1. 결론

기존 gate의 판정 로직은 다시 만들지 않고 호출·취합만 한다는 방향은 유지한다.
다만 다음 항목은 구현 전에 수정한다.

1. 특정 commit을 영구 고정하지 않고 **승인된 활성 기준**을 실행 시작 시 선택한다.
2. 승인 시각이 가장 최근인 lock을 자동 선택하지 않고 **활성 기준 포인터**로 명시한다.
3. 실행을 시작한 뒤에는 선택한 commit SHA와 tree SHA를 끝까지 고정한다.
4. 기존 `acgh.candidate.CandidateLock` 구조를 그대로 사용한다.
5. 병합 전 검사와 병합 후 검사를 분리한다.
6. 입력 누락과 프로그램 오류를 서로 다른 상태로 기록한다.
7. 결과·승인은 실행 입력과 결과 digest에 결속한다.

## 2. candidate 기준의 변경 방식

### 2.1 운영 원칙

커스터마이징 기준은 앞으로 변경될 수 있다. 따라서 `8ac18ad...`는 현재 최초
등록 기준일 뿐, 프로그램에 영구 하드코딩하지 않는다.

각 실행은 다음 순서로 기준을 확정한다.

1. 승인된 candidate lock을 만든다.
2. 관리자가 사용할 lock을 활성 기준으로 지정한다.
3. phase 실행 시작 시 활성 기준을 한 번 읽는다.
4. 읽은 commit SHA와 tree SHA를 run manifest에 기록한다.
5. 실행 도중 branch나 활성 기준이 변경돼도 현재 실행은 처음 값을 계속 사용한다.
6. 다음 실행부터 새 활성 기준을 사용한다.

### 2.2 활성 기준 포인터

승인된 lock 중 `approved_at`이 가장 최근인 항목을 자동 선택하지 않는다. 시간 오차,
병렬 승인, 잘못 승인한 실험 candidate 때문에 의도하지 않은 기준이 선택될 수 있다.

다음과 같이 활성 기준을 명시한다.

```yaml
schema_version: 1
candidate_lock_digest: sha256:<활성 lock digest>
activated_by: 데이터시스템부
activated_at: 2026-08-07T23:00:00Z
rationale: "1.13.1 Runtime Contract 9개 통과 기준"
```

권장 경로:

```text
harness/registrations/om-temp-1.13.1/candidate-locks/
├── <commit-sha>.yaml
├── <commit-sha>.approval.yaml
└── active-candidate.yaml
```

`active-candidate.yaml`이 가리키는 lock이 없거나, 승인되지 않았거나, digest가 다르면
phase를 시작하지 않는다.

## 3. 기존 CandidateLock 재사용

기존 계획의 평면형 예시는 제거한다.

```yaml
repository: ...
commit_sha: ...
tree_sha: ...
```

대신 `harness/acgh/candidate.py`의 기존 schema v2 구조를 그대로 사용한다.

```yaml
schema_version: 2
integration_strategy: vendor-merge
upstream:
  repository: openmetadata
  base_sha: <공식 base commit>
  target_sha: <공식 target commit>
  base_tag: 1.13.1-release
  target_tag: 1.13.2-release
candidate:
  repository: om-temp-real
  artifact_kind: source-tree
  commit_sha: <candidate commit>
  tree_sha: <candidate tree>
  artifact_digest: sha256:<source-tree 또는 build artifact digest>
```

기존 `load_candidate_lock()`, `parse_candidate_lock()`,
`assert_candidate_binding()`을 사용한다. 별도 schema나 별도 lock parser를 만들지 않는다.

## 4. 기준선과 업그레이드 candidate 구분

다음 두 코드는 역할이 다르다.

| 구분 | 의미 | 현재 예시 |
|---|---|---|
| 활성 기준선 | 업그레이드 전 승인된 커스터마이징 | 1.13.1 `8ac18ad...` |
| 업그레이드 candidate | 새 공식 버전을 병합한 후 검사할 코드 | 향후 생성할 1.13.2 candidate |

병합 전 단계에서 1.13.1 기준선을 1.13.2 candidate로 취급하지 않는다. 병합 전 run
manifest에는 `active_baseline`과 `upstream_transition`을 별도 필드로 기록한다.

```json
{
  "phase": "premerge",
  "active_baseline": {"commit_sha": "8ac18ad...", "tree_sha": "e86980..."},
  "upstream_transition": {"base_sha": "afcb2d...", "target_sha": "2763bf..."}
}
```

병합 후에는 공식 target을 조상으로 가진 새 candidate에 대해 정식 CandidateLock을
만들고 검사한다.

## 5. phase별 검사 범위

### 5.1 premerge-check

공식 base와 target의 차이를 분석하고 사람이 병합 전에 볼 위치를 찾는다.

| 실행 | 역할 |
|---|---|
| T42 upgrade-watch | 공식 변경과 BANK-OM 감시 경로의 겹침 확인 |
| T93 policy-drift | 새 공식 버전에서 감시 경로가 이동·삭제됐는지 확인 |
| T51/T52 structured diff | 공식 JSON·YAML 등의 구조 변화 확인 |
| watch-suggest | 검토 후보 제안. verdict 집계에서는 제외 |

premerge에서는 T41, T43, T93 exact-scope를 실행하지 않는다. 아직 새 공식 버전을
병합한 candidate가 없기 때문이다.

### 5.2 postmerge-check

공식 target을 병합한 실제 업그레이드 candidate를 대상으로 검사한다.

| 실행 | 역할 |
|---|---|
| ancestry·candidate binding | target 계보와 commit·tree·artifact 확인 |
| T41 sensitive-zones | 허용 범위를 벗어난 민감 영역 변경 확인 |
| T43 debt | 실제 병합 결과의 충돌·부채 기준 확인 |
| T93 exact-scope | ID별 등록 범위와 실제 commit 변경 범위 비교 |
| validate·source | 등록자료와 실제 소스 정합성 확인 |
| Contract | 실행 환경이 준비된 경우 기능 기준 확인 |

`conflict-rate`는 실제 병합 증거가 있는 postmerge에서만 사용한다. 승인된 기준이
없으면 0으로 추정하지 않는다.

## 6. 입력 누락과 실행 실패 구분

기존 계획의 "예외/입력미비는 모두 skipped" 규칙을 수정한다.

| 상황 | execution_status | verdict | 처리 |
|---|---|---|---|
| 정상 실행 | `executed` | 4종 verdict 중 하나 | 결과 집계 |
| 필요한 입력 없음 | `skipped_missing_input` | `null` | 필수 gate면 phase incomplete |
| preflight 차단 | `blocked_by_preflight` | `null` | phase 시작 금지 |
| 프로그램 예외·timeout·잘못된 JSON | `failed` | `analysis_error` | 오류 로그 보존, pass 금지 |

프로그램 버그를 입력 누락으로 표시하지 않는다. 한 gate가 실패해도 독립 실행 가능한
다른 gate는 계속 실행하고, 전체 결과는 `analysis_error`로 집계한다.

## 7. preflight 보완

preflight는 첫 오류에서 종료하지 않고 발견한 입력 문제를 한 번에 보고한다.

```json
{
  "ready": false,
  "checks": [
    {"name": "target_ref", "status": "unreachable", "value": "2763bf..."},
    {"name": "change_intent", "status": "missing", "required_for": ["T41"]},
    {"name": "conflict_rate", "status": "missing", "required_for": ["T43"]}
  ]
}
```

blocking 항목과 gate별 선택 항목을 분리한다.

- base·target·candidate 객체, 활성 기준 승인, candidate 계보 오류: phase 차단
- change-intent 없음: T41만 미실행
- conflict-rate 없음: T43만 미실행
- partial clone blob 없음: 필요한 ref/blob과 fetch 안내 후 차단

## 8. 집계와 종료코드

verdict는 기존 네 종류만 사용한다.

```text
pass=0, block=1, approval=2, analysis_error=3
```

집계는 종료코드의 숫자 크기가 아니라 `SEVERITY_RANK`를 사용한다.

- 필수 gate가 모두 실행됨: `phase_status=complete`
- 필수 gate가 입력 부족으로 미실행: `phase_status=incomplete`
- incomplete의 overall verdict: `analysis_error`, exit 3
- 적용 대상이 아닌 gate는 필수 gate 목록에 넣지 않는다.

## 9. evidence와 승인 결속

phase 결과 digest에는 다음 판단 입력이 포함돼야 한다.

- 활성 기준 lock digest
- 공식 base·target SHA
- postmerge candidate lock digest
- 등록자료·정책 입력 digest
- gate catalog·검사기 version
- gate별 판정과 검사 대상 수

timestamp, 실행 시간, 화면 표시 순서 등 관찰 정보는 판단 digest에서 제외한다.

승인은 정확한 `result_digest`를 대상으로 한다. candidate, 등록자료, 정책 입력 중
하나라도 변경되면 새 plan·검사·승인이 필요하다. 사람 승인이 `block`이나
`analysis_error`를 `pass`로 바꾸지는 못한다.

## 10. 3단 출력

동일한 phase 결과에서 다음 세 출력을 생성한다.

1. 관리자 요약: 검사명, 정상·검토·미실행·차단 수, `확인 수/전체 수`, 다음 행동
2. 실무자 상세: gate별 SHA, BANK-OM ID, 경로, 누락 입력, 재실행 명령
3. 시스템 JSON: 전체 입력, digest, gate 결과, 승인 결속 정보

세 출력은 별도로 계산하지 않고 동일한 시스템 JSON을 입력으로 렌더링한다. 수량이나
verdict가 다르면 테스트 실패다.

## 11. 변경할 구현 순서

1. 기존 CandidateLock schema 호환 테스트 작성
2. active-candidate 선택·승인·digest 검증 구현
3. 실행 시작 시 candidate pinning 구현
4. premerge·postmerge gate catalog 분리
5. 입력 누락·실행 실패 상태 분리
6. preflight 일괄 보고 구현
7. gate 독립실행과 verdict 집계 구현
8. 직접 실행 대비 parity 테스트
9. 관리자·실무자·시스템 출력 생성
10. evidence digest·승인 결속 테스트

각 단계는 `PHASE_BUNDLING_반례테스트케이스_20260807.md`의 P0 테스트를 먼저 실패
상태로 추가한 뒤 구현한다.

## 12. 완료 기준

- 특정 candidate SHA가 프로그램에 영구 하드코딩되지 않는다.
- 승인된 활성 기준을 명시적으로 교체할 수 있다.
- 한 실행에서 사용한 commit·tree는 도중에 바뀌지 않는다.
- premerge와 postmerge 결과가 섞이지 않는다.
- 기존 gate의 직접 실행과 번들 실행 결과가 같다.
- 입력 누락과 프로그램 오류가 구분된다.
- 필수 검사 미실행 상태가 pass로 표시되지 않는다.
- 승인 후 판단 입력 변경 시 승인이 자동 무효화된다.
- 관리자·실무자·시스템 출력의 verdict와 수량이 같다.

