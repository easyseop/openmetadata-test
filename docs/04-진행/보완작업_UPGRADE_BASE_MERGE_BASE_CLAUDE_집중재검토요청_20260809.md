# Upgrade base와 Git merge base 분리 — Claude 집중 재검토 요청

> 작성일: 2026-08-09 KST
>
> 상태: 1차 검토 P0 반영안에 대한 집중 재검토
>
> 방식: 읽기 전용 · 이 문서의 다섯 질문만 검토
>
> 제품·검사기 코드와 Git 상태를 수정하지 마십시오.

## 0. Claude에 전달할 문장

```text
docs/04-진행/보완작업_UPGRADE_BASE_MERGE_BASE_CLAUDE_집중재검토요청_20260809.md를
읽고 8절 형식으로만 답해줘. 이전 전체 설계를 다시 검토하지 말고, upgrade base와
실제 Git merge base 분리, R5·R6, 후보 0개의 종료 경로만 적대적으로 확인해줘.
저장소·코드·문서·branch를 수정하거나 commit·push하지 마.
```

## 1. 이 집중 재검토가 필요한 이유

1차 Claude 검토는 기존 문서가 `afcb2d2...`를 실제 Git merge base라고 잘못 쓴
사실을 정확히 발견했습니다. 그러나 제안한 다음 절차는 “새 1.13.2 Candidate lock의
`upstream.base_sha`를 실제 merge base `739ee492...`로 바꾼다”였습니다.

현재 코드는 다음 두 조건을 동시에 강제합니다.

1. 이전 1.13.1 기준선 lock의 `upstream.target_sha`와 새 lock의
   `upstream.base_sha`가 정확히 같아야 합니다.
2. 새 lock의 `upstream.base_sha`와 `git merge-base(target, custom_head)`가
   정확히 같아야 합니다.

이번 실제 이력에서는 첫 번째 값이 `afcb2d2...`, 두 번째 값이 `739ee492...`이므로
두 조건을 동시에 만족하는 새 lock을 만들 수 없습니다. SHA 한 줄을 고치는 문제가
아니라, 코드가 **이전 공식 upgrade 기준**과 **Git의 실제 공통 조상**을 같은
`base`로 취급한 것이 원인입니다.

## 2. 독립 확인한 Git·코드 사실

### 2.1 Git SHA

| 의미 | SHA | 확인 결과 |
|---|---|---|
| 이전 공식 1.13.1 release | `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9` | 1.13.1 기준선 lock의 base·target |
| 실제 Git merge base | `739ee49279afe3b35f1e9b7da1df01ff9612425c` | `git merge-base 8ac18ad... 2763bf97...` 계산값 |
| custom head | `8ac18ad053d9274774e274ba17b35911ac0b9dcb` | 승인된 1.13.1 BANK 기준선 |
| 공식 1.13.2 target | `2763bf97ce265662793a1a38d353147cc6d6c2e3` | 공식 tag commit |
| 제품 Candidate | `9587fe8fc7d9e6a18b9c0038b92c5fef24bb8412` | WIP 전달 commit |

`afcb2d2...`는 `739ee492...`의 자손이고 custom head의 조상이지만, 공식 1.13.2
target의 조상은 아닙니다. `739ee492...`는 target과 custom head 양쪽의 조상입니다.

### 2.2 현재 코드의 충돌

`harness/run_phase_bundle.py`의 현재 동작:

- 188행 부근: 이전 기준선 lock target과 현재 lock base의 완전 일치 요구
- 194행 부근: 실제 merge base와 현재 lock base의 완전 일치 요구
- 229행 부근: `merge_changed_paths`를 현재 lock base 대비 target·custom으로 계산
- 315행 부근: 수집기도 같은 방식으로 현재 lock base를 사용

1.13.1 기준선 lock의 실제 값:

```yaml
upstream:
  base_sha: afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9
  target_sha: afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9
candidate:
  commit_sha: 8ac18ad053d9274774e274ba17b35911ac0b9dcb
```

따라서 새 lock base를 `739ee492...`로 바꾸면 188행 기준선 연속성에서 차단되고,
`afcb2d2...`로 유지하면 194행 merge-base 일치에서 차단됩니다.

## 3. 제안하는 수정 모델

### 3.1 두 base의 의미를 분리

| 필드·용어 | 값 | 실제 용도 |
|---|---|---|
| `upgrade_base_sha` | `afcb2d2...` | 이전에 승인한 공식 release와 새 target의 버전 차이 검사 |
| Candidate lock `upstream.base_sha` | `afcb2d2...` | 기존 schema 호환을 위해 upgrade base 의미 유지 |
| `merge_base_sha` | `739ee492...` | target·custom head의 3-way 변경·충돌 분류 기준 |
| `upstream.target_sha` | `2763bf97...` | 새 공식 버전 |

Candidate lock의 `base_sha`는 이전 공식 release라는 기존 의미를 유지합니다. 실제
Git merge base는 이미 conflict evidence에 별도 `merge_base_sha` 필드가 있으므로
그 필드를 사용합니다. Candidate lock schema를 이번 수정에서 바꾸지 않습니다.

### 3.2 기계 검증 규칙

1. 이전 기준선 lock `upstream.target_sha ==` 새 lock `upstream.base_sha`는
   `afcb2d2...`로 계속 완전 일치해야 합니다.
2. `git merge-base(upstream.target_sha, custom_head_sha)`를 매번 계산합니다.
3. 계산한 값과 conflict evidence의 `merge_base_sha`가 다르면
   `ANALYSIS_ERROR`입니다.
4. 계산한 merge base가 Candidate lock의 `upstream.base_sha`와 같을 필요는 없습니다.
5. `merge_changed_paths`는 실제 merge base→target과 실제 merge base→custom head의
   합집합으로 계산합니다.
6. A3의 검토 대상은 실제 merge base→target, 실제 merge base→custom head,
   실제 merge base→Candidate 변경 경로의 합집합입니다.
7. `upgrade_watch`처럼 release 간 차이를 보는 검사는 upgrade base→target을
   유지합니다.
8. 사람용·JSON 출력에는 `upgrade_base_sha`와 `merge_base_sha`를 서로 다른 이름으로
   모두 기록합니다.

### 3.3 필수 반례 test

- 이전 release commit이 새 target의 조상이 아니지만 두 branch가 더 오래된 공통
  조상을 갖는 이번 실제 topology가 정상 처리되어야 합니다.
- 이전 기준선 target과 새 lock의 upgrade base가 다르면 `ANALYSIS_ERROR`입니다.
- evidence의 `merge_base_sha`를 위조하면 `ANALYSIS_ERROR`입니다.
- merge 변경 경로 계산에 upgrade base를 사용하면 검출되는 회귀 test가 있어야 합니다.
- upgrade-watch는 실제 merge base가 아니라 이전 release를 기준으로 유지되어야 합니다.

## 4. R5·R6의 정확한 일반 규칙

1차 검토가 R5 누락을 발견한 것은 맞습니다. 다만 제시된 R6 입력은 “custom도
수정했다”고 하면서 `TARGET_ONLY`로 기대해 분류 정의와 모순됩니다.

경로 부재를 하나의 상태로 취급하고, target과 custom의 상태가 서로 다를 때 다음을
필수 검토 조합으로 지정합니다.

```text
custom_state != merge_base_state
and candidate_state == target_state
and target_state != custom_state
→ CUSTOM_LOSS_SUSPECT

target_state != merge_base_state
and candidate_state == custom_state
and target_state != custom_state
→ OFFICIAL_LOSS_SUSPECT
```

### R5 — 커스텀 전용 신규 파일 누락

- merge base: 경로 없음
- target: 경로 없음
- custom: 신규 파일 존재
- Candidate: 경로 없음
- 기대: `CUSTOM_ONLY + EQUALS_TARGET + CUSTOM_LOSS_SUSPECT`

### R6 — 공식 삭제를 Candidate가 되살림

- merge base: 파일 존재
- target: 파일 삭제
- custom: merge base와 같은 파일 유지, 별도 수정 없음
- Candidate: custom과 같은 파일 유지
- 기대: `TARGET_ONLY + EQUALS_CUSTOM + OFFICIAL_LOSS_SUSPECT`

custom도 파일을 수정했다면 `BOTH_CHANGED_PARENTS_DIVERGE + EQUALS_CUSTOM`이며,
이미 R2의 공식 변경 소실 계열에 포함됩니다.

## 5. A4 후보 0개의 종료 경로

후보 0개는 기능 보존을 확인할 수 없으므로 `BLOCK`을 유지합니다. 다만 해소 경로를
다음처럼 구분합니다.

1. BANK-OM 기능 전체가 폐기되는 경우: 기존 T92 customization retirement 사용
2. BANK-OM은 유지되지만 특정 공유 코드 정의를 공식 target이 흡수한 경우:
   A5에 `absorbed_by_upstream` 정의 disposition을 추가하고 관련 invariant test와
   사람 승인을 결속
3. 새 경로로 이동한 경우: A4 relocation 후보 → A5 정의 이관

T92는 registry와 Manifest의 BANK-OM ID 전체를 `retired`로 바꾸므로, 공유 코드
정의 한 건이 사라졌다는 이유만으로 T92를 실행하면 안 됩니다.

## 6. A5·A16에 반영할 1차 검토의 유효한 P1

다음 지적은 그대로 구현 완료 조건에 추가합니다.

- 승인 artifact가 proposal 전체 digest에 결속되어야 합니다.
- proposal에 `harness_commit`을 넣어 tokenizer·탐색기 버전 변경 후 재사용을
  차단합니다.
- 새 정의는 `supersedes: {definition_id, definition_digest}`를 기록합니다.
- A16 진단 결과는 canonical `disabled` 라벨을 재사용하지 않고
  `diagnostic(-M -C, threshold=...)`처럼 실제 정책을 별도 필드에 기록합니다.

## 7. 참고 자료와 확인 우선순위

Claude는 다음 순서로 근거를 사용합니다. 오래된 요청서의 설명과 실제 코드가 다르면
실제 Git 객체와 현재 branch 코드를 우선합니다.

### 7.1 1순위 — 실제 Git 이력과 현재 코드

| 확인 대상 | 경로·파일 | 확인할 내용 |
|---|---|---|
| 제품 Git 이력 | `/Users/seop/om-work/om-1.13.2-rehearsal` | 네 SHA의 실제 계보·merge base·Candidate tree |
| Phase 결속·수집 | `harness/run_phase_bundle.py` | `_bind_conflict_evidence`, `collect_conflict_evidence_command`, `_assert_transition_binding` |
| Candidate lock 의미 | `harness/acgh/candidate.py` | `UpstreamLock`, canonical digest, 기존 `base_sha` 의미 |
| Candidate lock schema | `harness/acgh/schema/candidate-lock.schema.json` | schema v1·v2 호환성과 필드 제약 |
| 계보 검사 | `harness/acgh/ancestry.py` | base·target·Candidate에 요구하는 Git 관계 |
| Git primitive | `harness/acgh/gitprim.py` | `merge_base`, `is_ancestor`, rename 고정 정책 |

빠른 읽기 전용 확인 명령:

```bash
git -C /Users/seop/om-work/om-1.13.2-rehearsal \
  merge-base \
  8ac18ad053d9274774e274ba17b35911ac0b9dcb \
  2763bf97ce265662793a1a38d353147cc6d6c2e3

git -C /Users/seop/om-work/om-1.13.2-rehearsal \
  merge-base --is-ancestor \
  afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9 \
  2763bf97ce265662793a1a38d353147cc6d6c2e3

git -C /Users/seop/om-work/om-1.13.2-rehearsal \
  show -s --format='%H %T %P %s' \
  9587fe8fc7d9e6a18b9c0038b92c5fef24bb8412
```

첫 명령의 기대값은 `739ee49279afe3b35f1e9b7da1df01ff9612425c`입니다. 두 번째
명령의 종료 코드는 1이며, 이는 `afcb2d2...`가 target의 조상이 아니라는 뜻입니다.

### 7.2 2순위 — 실제 기준선 lock과 관련 gate

| 확인 대상 | 경로 | 주의점 |
|---|---|---|
| 1.13.1 Candidate lock | `harness/registrations/om-temp-1.13.1/candidate-locks/om-1.13.1-runtime-ready.yaml` | 현재 사용자 미추적 파일이므로 읽기만 하고 수정·stage 금지 |
| 활성 포인터 | `harness/registrations/om-temp-1.13.1/candidate-locks/active-candidate.yaml` | 기준선 선택 상태 확인용 |
| retirement | `harness/acgh/retirement.py` | T92가 definition 한 건이 아니라 BANK-OM 전체 상태를 바꾸는지 확인 |
| retirement schema | `harness/acgh/schema/retirement-record.schema.json` | 승인·Candidate·test digest 결속 확인 |
| retirement test | `harness/tests/test_retirement.py` | 전체 retirement 정상·반례 범위 확인 |
| 공유 코드 검사 | `harness/acgh/shared_code.py` | 기존 경로·fragment 판정 범위 |
| 정의 제안기 | `harness/propose_shared_code_definitions.py` | 현재 제안·검증 흐름과 A5 재사용 가능성 |

### 7.3 3순위 — 현재 상태와 과거 검토 문서

| 문서 | 용도 |
|---|---|
| `docs/04-진행/CODEX_CURRENT_HANDOFF.md` 20·21절 | 현재 제품·검사기 SHA, 완료·미완료 범위 |
| `evidence/om-1.13.2-source-checkpoint-20260809/SOURCE_VALIDATION_CHECKPOINT.md` | 소스 WIP 검증 경계와 보존 로그 |
| `docs/04-진행/보완작업_재설계_CLAUDE_최종검토요청_20260809.md` | 1차 검토 당시 전체 설계. 상단 정정 이후에는 역사적 입력으로만 사용 |
| `docs/04-진행/보완작업_누적목록_20260809.md` | A1~A17의 최초 목록. 현재 결론보다 우선하지 않음 |

### 7.4 이번 검토에서 하지 않을 일

- production bundle, Docker, 전체 harness test를 다시 실행하지 않습니다.
- 제품 branch·검사기 branch·인덱스·Candidate lock을 수정하지 않습니다.
- `codex/candidate-activation-cli-20260809` branch를 merge하거나 그 branch의 동작을
  이번 집중 질문과 섞지 않습니다.
- 1차 검토에서 이미 채택한 A1·A3·A4·A5·A16 전체를 처음부터 재검토하지 않습니다.

## 8. 집중 재검토 출력 형식

다음 다섯 질문에만 답합니다.

| # | 질문 |
|---|---|
| 1 | Candidate lock `base_sha`를 upgrade base로 유지하고 conflict evidence의 `merge_base_sha`를 실제 공통 조상으로 쓰는 분리가 기존 코드·schema 의미와 맞는가? |
| 2 | 3.2의 여덟 검증 규칙에 거짓 PASS 또는 정상 차단 반례가 있는가? |
| 3 | R5·수정된 R6와 두 일반 규칙이 커스텀·공식 변경 소실 조합을 빠짐없이 잡는가? |
| 4 | 후보 0개의 T92 전체 폐기와 definition-level `absorbed_by_upstream` 분리가 맞는가? |
| 5 | 이 수정 후 별도 설계 검토 없이 A0(base 분리)→A1→A3→A16→A4→A5 구현에 착수해도 되는가? |

출력은 다음 형식으로 제한합니다.

1. `P0 / P1 / P2` 표 — 반례와 근거 파일·함수 포함
2. 질문 1~5 각각 `예 / 수정 후 예 / 아니오`
3. 필요한 반례 test만 `입력 → 기대 → 잘못된 결과`로 추가
4. 최종 결론 하나:
   - `구현 착수 가능 — 새 P0 없음`
   - `수정 후 구현 — P0 있음`
