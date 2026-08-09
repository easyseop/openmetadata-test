# 구조보완 최종 목적 — 사람·LLM 동등 검사 Claude 설계 검토 요청

작성일: 2026-08-09

## 1. 이 검토가 필요한 이유

이 프로젝트의 최종 목적은 LLM이 OpenMetadata 버전 업그레이드와 커스터마이징
이관을 수행하도록 만드는 것만이 아니다. **사람이 작업하든 LLM이 작업하든,
승인된 같은 기준과 같은 Candidate를 검사하면 같은 판정이 나오는 독립 검사기**가
필요하다.

LLM은 병합·충돌 해소·코드 이관·test 실행을 수행할 수 있는 선택적 작업자다.
LLM이 없어도 사람이 같은 관리파일과 명령으로 전체 절차를 실행하고, 실패 원인과
다음 행동을 이해할 수 있어야 한다. 검사기의 PASS·BLOCK은 LLM의 설명·추천·자기
평가가 아니라 Git 객체, 승인된 관리파일, assertion, 필수 test와 결속된 증거로만
결정해야 한다.

최근 구조보완 구현은 Git 비교·Candidate 결속·정의 이관·승인 증거를 강화했지만,
유사도 후보가 BLOCK을 APPROVAL로 완화하고 기능 test 증거가 BANK-OM ID·정의·경로와
충분히 결속되지 않는 문제가 확인됐다. 동시에 기능이 계속 추가되면서 최초 목적보다
복잡한 거버넌스 절차가 커졌다는 사용자 문제의식도 있다.

따라서 코드를 더 수정하기 전에 다음 두 질문을 적대적으로 검토한다.

1. 현재 검사기가 사람·LLM 어느 쪽에도 동일하고 신뢰 가능한 독립 판정기인가?
2. 최종 목적에 직접 필요하지 않거나 오히려 판단을 흐리는 기능은 무엇인가?

## 2. 검토 대상과 현재 상태

```text
repository: easyseop/openmetadata-test
branch: codex/structural-upgrade-safety-20260809
review baseline HEAD: 24130b7de812c395394804edf8e914f8bc5a0dc1
structural implementation: d5153f284d8808e7856896b106f0539e8fcf2c83
review-01 repair: df1eee22f2e8c0c0b7db999a2428f8637696124f
```

주요 구현과 관리자료:

```text
harness/registrations/om-temp-1.13.1/customization-registry.yaml
harness/registrations/om-temp-1.13.1/manifests/BANK-OM-*.yaml
harness/registrations/om-temp-1.13.1/contracts.yaml
harness/registrations/om-temp-1.13.1/shared-code-definitions.yaml
harness/acgh/policy_guard.py
harness/acgh/contracts.py
harness/acgh/evidence.py
harness/acgh/structural_review.py
harness/acgh/shared_code_migration.py
harness/acgh/phase.py
harness/acgh/verdict.py
harness/run_phase_bundle.py
harness/om_workflow.py
harness/tests/test_policy_guard.py
harness/tests/test_contracts.py
harness/tests/test_evidence.py
harness/tests/test_phase_*.py
tests/bank/contracts/
```

현재 확인된 상태를 구분한다.

- 구현·검증 완료: `df1eee2`의 rename 진단 정본 분리, merge-base 회귀 탐지,
  여러 best merge-base fail-closed, WATCHED 이름 충돌 해소
- 마지막 전체 회귀: `591 passed, 38 skipped`, 실패 0
- 아직 미수정: 유사도 후보의 판정 완화, 기능 test의 BANK-OM·정의·경로 결속 부족,
  해당 오탐을 APPROVAL로 고정한 test
- 아직 미검토: `watch-suggest`, `required changed path` 등 이번 구조보완 diff 밖의
  기존 기능을 포함한 전체 사람·LLM 동등성
- 실환경 미완료: 최종 1.13.2 production bundle, Docker Runtime 화면 검증,
  최종 Candidate lock·조직 승인·postmerge·release

이번 요청은 읽기 전용 설계 검토다. 코드·문서·Git 상태, 제품 WIP, Candidate lock,
기존 증거를 수정하지 않는다. 제품 build와 Docker도 실행하지 않는다.

## 3. 고정하려는 최종 목적

### 3.1 실행 주체와 판정 주체를 분리한다

```text
사람 실행: 사람 작업 → 검사기 → PASS / BLOCK / APPROVAL / ANALYSIS_ERROR
LLM 실행:  LLM 작업  → 같은 검사기 → 같은 네 상태
```

검사 입력이 같다면 실행 주체, 프롬프트, 설명 문장, 로그 표현이 달라도 canonical
판정과 result digest가 같아야 한다. LLM은 검사 결과를 읽고 수정 작업을 반복할 수
있지만, 판정 기준을 만들거나 자기 결과를 승인할 수 없다.

가능하면 검사기는 작업자가 사람인지 LLM인지 입력받지 않는다. 사람용 text와
자동화용 JSON은 같은 canonical 결과를 표현하는 출력 형식 차이일 뿐이다. 작업자
종류를 verdict 입력으로 사용해야 한다면 그 필요성과 안전성을 별도로 증명해야 한다.

### 3.2 LLM은 필수 의존성이 아니다

사람은 LLM 없이 다음 작업을 수행할 수 있어야 한다.

1. 검사 대상 repository·branch·Candidate SHA 확인
2. 승인된 관리파일 확인
3. premerge·postmerge·필수 test 실행
4. PASS·BLOCK·APPROVAL·ANALYSIS_ERROR 해석
5. 실패 대상 BANK-OM ID·파일·test와 다음 재실행 명령 확인
6. 증거 보존과 담당자 검토 요청

검사 결과를 이해하기 위해 숨은 prompt, LLM 요약, 별도 대화 기록이 필요하면 이
목적을 충족하지 못한다.

### 3.3 관리파일은 작업자의 자기평가가 아니라 사전 승인된 정책이다

현재 관리자료의 의도는 다음과 같다. 실제 구현이 이 의도를 만족하는지 Claude가
코드로 검증한다.

| 관리자료 | 의미 | 작성·변경 주체 | 검사에서의 사용 |
|---|---|---|---|
| `customization-registry.yaml` | BANK-OM ID, owner, 중요도, Manifest·Contract 연결 | 사람의 등록·승인 절차 | 검사할 커스터마이징 목록과 연결 확인 |
| `manifests/BANK-OM-*.yaml` | 변경 범위, 필수 경로, upgrade watch, Contract | 사람 승인 정책 | 범위 누락·공식 변경 영향·필수 경로 검사 |
| `contracts.yaml` | BANK 기능의 정상 조건과 필수 test | 업무·기술 담당자 승인 | 기능 test 누락·실패 시 진행 차단 |
| `shared-code-definitions.yaml` | 버전별로 확인할 코드·설정 assertion | 사람 승인 정책 | Candidate에서 assertion 존재·값 검사 |
| Candidate lock | 검사할 commit·tree·artifact의 정확한 신원 | 도구 생성, 사람 승인·활성화 | 다른 Candidate 증거 재사용 차단 |
| Phase result·digest | 검사기가 생성한 판정과 판단 입력 | 검사기만 생성 | 변조·후속 commit·교차 Phase 재사용 탐지 |
| 승인 파일 | 기계로 결정할 수 없는 사람 판단 기록 | 실제 권한을 가진 사람 | BLOCK 우회가 아니라 APPROVAL 상태 해소에만 사용 |

LLM은 제품 코드와 test를 수정할 수 있다. 그러나 같은 실행에서 관리 정책까지
바꾸고 그 새 정책으로 자기 코드를 판정하면 자기승인이 된다. 관리파일 변경은
현재 Candidate 판정과 분리해 이전 승인 정책으로 검토하거나 별도 사람 승인을
받아야 한다.

## 4. 원하는 전체 작업 흐름

### 4.1 정책 준비

사람이 BANK-OM별 정상 기능, 필수 test, 필수 assertion과 검사 범위를 등록하고
승인한다. 이 정책의 commit SHA와 digest를 고정한다.

### 4.2 병합 전 검사

검사기는 공식 target이 BANK 관리 경로·assertion·Contract에 미칠 영향을 기계적으로
수집한다. 확정 사실과 조사 추천을 분리한다.

```text
확정 사실: 공식 target에서 기존 경로가 삭제됨
미확인 참고: symbol이 겹치는 후보 경로가 있음
사람 판단: 공식 기능 대체 여부와 BANK 재이식 위치
```

추천이나 유사도는 작업자에게 조사 단서를 제공할 수 있지만 PASS·BLOCK을 완화하지
않는다.

### 4.3 사람 또는 LLM의 업그레이드 작업

작업자는 vendor merge, 충돌 해소, 구조 변경에 맞춘 BANK 기능 재이식, test 수정을
수행한다. LLM도 이 범위에서는 사람과 같은 비신뢰 작업자로 취급한다.

### 4.4 병합 후 독립 검사

검사기는 최소한 다음을 독립적으로 확인한다.

1. 승인된 base·target·custom head·Candidate SHA 결속
2. 공식 변경과 BANK 변경이 Candidate에서 빠진 경로 의심
3. BANK-OM별 필수 assertion
4. BANK-OM별 필수 test의 존재·실행·개별 결과
5. build artifact·Runtime Contract가 필요한 단계의 실제 결과
6. 관리 정책과 검사기 자체가 Candidate에 의해 자기승인 방식으로 바뀌지 않았는지
7. 결과 이후 Candidate 후속 commit이 생기지 않았는지

### 4.5 판정과 반복

| 상태 | 의미 | 자동 진행 |
|---|---|---|
| `PASS` | 사전 승인된 필수 기계 검사가 모두 통과 | 다음 단계 허용 |
| `BLOCK` | 필수 기능·경로·assertion·test·증거가 누락 또는 실패 | 작업자가 수정 후 재실행 |
| `APPROVAL` | 기계로 결정할 수 없는 실제 사람 판단이 필요 | 자동 진행 중단 |
| `ANALYSIS_ERROR` | 검사 입력·도구·증거가 불완전하거나 일관되지 않음 | 자동 진행 중단, 검사 환경 복구 |

`APPROVAL`은 약한 PASS가 아니다. 자동화 관점에서는 `BLOCK`과 마찬가지로 사람이
판단하기 전 다음 단계로 진행할 수 없는 정지 상태다. 사람 승인은 기존 BLOCK을
덮어쓸 수 없다.

## 5. 현재 구현에서 이미 확인된 위험

### 5.1 유사도 후보가 판정을 완화한다

현재 `find_relocations()`는 후보의 evidence strength와 무관하게 source context면
`eligible_for_migration: true`로 표시한다. eligible 후보 하나가 있으면 기존 정의
실패가 `BLOCK`에서 `APPROVAL`로 완화된다. 함수가 함께 반환하는 “diagnostic only”
rule과 상태 전이가 모순된다.

현재 논의 방향은 안 B다.

```text
기존 정의 실패 → 후보 유무와 관계없이 BLOCK
후보 검색 결과 → UNVERIFIED_CANDIDATE, automated_decision: none
사람이 새 경로·assertion 제출 → 독립 검증
기능 test·정의·사람 승인 완료 후 재실행 → 그때만 BLOCK 해제 가능
```

검색 자체는 실제 1.13.2에서 조사 범위를 줄인 편익이 있어 유지 후보지만, 검색
결과는 정답이나 이관 허가가 아니다.

### 5.2 기능 test 증거 결속이 부족하다

현재 `_functional_evidence()`는 주로 subject SHA·role·PASS·test ID·설명·명령을
확인한다. BANK-OM ID, definition ID·digest, 제안 경로·blob digest, assertion
digest와의 일치가 필수 입력이 아니다. 하나의 일반 PASS 증거를 서로 다른 정의
이관에 재사용할 가능성을 차단해야 한다.

단, 같은 test suite 결과 파일 안에 여러 BANK-OM별 독립 결과가 있는 정상 사용까지
무조건 금지해서는 안 된다. 공용 산출물을 허용하려면 각 결과가 BANK-OM·Contract·
정의·경로에 독립적으로 결속돼야 한다.

### 5.3 잘못된 기대를 test가 고정한다

현재 synthetic test는 BANK 값이 공식 값으로 바뀐 source 후보를
`symbol_overlap`, `eligible_for_migration: true`, finding `APPROVAL`로 기대한다.
전체 test 통과가 설계 안전성을 보장하지 않는 실제 사례다.

### 5.4 기존 사람·LLM 분리 test의 증명 범위가 좁다

현재 `test_llm_and_approvals_do_not_change_machine_verdict_or_digest()`는 이미 만들어진
하나의 machine result에 LLM memo와 approval 표시를 붙여도 evidence card의 verdict·
digest가 변하지 않는 것을 확인한다. 이것은 필요한 안전장치지만 사람과 LLM이 실제
공개 CLI·Phase 전체를 각각 실행했을 때 동일하다는 종단 parity 증명은 아니다.

### 5.5 필수 test의 존재와 test의 의미는 다르다

현재 `check_required_test_implementations()`는 Contract selector가 안전한 Python
경로를 가리키고 지정 함수가 AST에 존재하는지 확인한다. 함수 본문이 BANK 기능을
실제로 검증하는지, LLM이 `assert true`와 같은 무의미한 구현으로 약화했는지는
판정하지 않는다. 이 차이를 숨기지 않고, test 구현 변경 결속·base 비교·patch-kill·
사람 승인 중 어떤 방어가 필요한지 검토해야 한다.

## 6. Codex의 잠정 분석 — 검토할 설계 원칙

다음은 확정 결정이 아니라 Claude가 반례로 재검토할 잠정 분석이다.

### 6.1 유지 가치가 큰 정본 기능

- base·target·custom head·Candidate Git 결속
- BANK-OM별 Manifest·Contract·assertion 연결
- 필수 test의 존재·실행·개별 판정
- Candidate·artifact·Phase 결과 digest 결속
- 후속 commit·다른 Candidate·다른 Phase 증거 재사용 차단
- 관리 정책 변경을 이전 정책 또는 별도 승인으로 검사하는 self-approval 방지

이 기능들은 작업자가 사람인지 LLM인지와 무관하게 같은 사실을 검사할 수 있다.

### 6.2 판정에서 분리할 가능성이 큰 보조 정보

- fuzzy relocation 순위
- rename·binary 진단
- watch-suggest 후보
- conflict-rate
- LLM이 작성한 요약·권고·변경 이유

보조 정보가 실제 조사 시간을 줄일 수는 있다. 그러나 정확성을 확정하지 못하는
정보는 canonical verdict를 완화하지 않고, 출력에서 `미확인 참고`임을 기계적으로
표시해야 한다.

### 6.3 단순화 가능성을 검토할 운영 기능

- 중복되는 approval 양식과 상태 전이
- 충돌 해결과 직접 관계없는 상세 점수·통계
- 동일한 결속을 여러 관리파일에서 반복하는 필드
- 사람이 실행할 때 이해하기 어려운 중간 lock·template 명령

단순화는 감사 추적·재현성·자기승인 차단을 훼손하면 안 된다. 복잡해 보인다는
이유만으로 Candidate lock이나 digest를 제거하지 말고 실제 중복과 필수 신뢰 경계를
구분해야 한다.

## 7. Claude가 반드시 답해야 할 설계 질문

### 7.1 최종 목적의 타당성

1. “LLM은 선택적 비신뢰 작업자, 검사기는 사람·LLM 공통 독립 판정기”라는 구조가
   적절한가?
2. 같은 Candidate·정책·검사기 버전에서 실행 주체 차이가 canonical verdict와
   digest에 영향을 줄 현재 경로가 있는가?
3. 사람이 LLM 없이 현재 CLI와 관리파일만으로 준비·실행·복구할 수 있는가?
4. 사람이 결과를 이해하려면 현재 출력에 어떤 BANK-OM·경로·test·다음 명령 정보가
   부족한가?

### 7.2 관리파일 신뢰 경계

5. LLM이 제품 코드와 Manifest·Contract·assertion·test를 같은 Candidate에서 함께
   수정하면 자기 결과를 통과시킬 수 있는가?
6. `policy_guard`와 base policy 사용이 모든 공개 CLI·Phase 경로에 실제로 연결되는가?
7. required path나 required test를 삭제·이름 변경·빈 test로 바꾸는 공격을 어느
   gate가 차단하는가? 우회 가능한 경로를 반례로 제시한다.
8. 관리파일 변경이 정당하게 필요한 버전 업그레이드에서 어떤 별도 proposal·사람
   승인·재실행 절차가 최소한 필요한가?
9. LLM이 관리파일 변경안을 제안하되 현재 실행의 판정에는 사용하지 못하도록 schema,
   digest, Git ref를 어떻게 분리해야 하는가?

### 7.3 판정 규칙

10. PASS가 오직 사전 승인된 필수 기계 검사 통과로만 만들어지는가?
11. BLOCK이 APPROVAL이나 advisory 결과에 의해 완화되는 다른 경로가 있는가?
12. 사람 승인이 BLOCK을 직접 덮어쓸 수 있는 경로가 있는가?
13. `APPROVAL`을 자동화 정지 상태로 일관되게 다루는가, 일부 화면·exit code·Phase가
    다음 단계 진행 가능 상태로 오해하게 하는가?
14. `ANALYSIS_ERROR`가 실패한 검사를 누락된 PASS처럼 처리하지 않는가?
15. 동일 입력 재실행의 canonical verdict·digest 결정성이 기기·Git config·순서·LLM
    메모에 의해 깨지는가?

### 7.4 기능 증거와 test

16. 기능 test 증거를 BANK-OM ID, Contract ID, definition digest, 새 경로와 blob,
    assertion digest, Candidate SHA에 어느 수준까지 결속해야 하는가?
17. 하나의 공용 test 결과 파일을 여러 BANK-OM이 사용하는 안전한 schema는 무엇인가?
18. test 파일 자체를 LLM이 약화하거나 `assert true`로 바꾼 뒤 PASS시키는 것을
    어떻게 차단해야 하는가?
19. 소스 assertion 통과와 기능 test 통과가 각각 무엇을 증명하며, 어느 쪽도 전체
    기능 보장으로 과장되지 않는가?
20. build·Runtime 입력이 없는 source-only 상태에서 PASS라는 단어를 사용해도 되는가,
    아니면 scope가 붙은 별도 완료 상태가 필요한가?

### 7.5 사람 운영성과 LLM 자동화

21. 모든 필수 명령에 사람이 복사해 실행할 수 있는 입력 출처·정상 출력·실패 복구·
    재실행 명령이 존재하는가?
22. LLM 전용 JSON과 사람용 출력이 같은 canonical 결과에서 생성되는가?
23. LLM이 후보·설명·요약을 왜곡해도 gate 결과가 변하지 않는가?
24. 사람과 LLM이 각각 같은 Candidate를 검사했을 때 동일성을 검증하는 parity test가
    충분한가?
25. LLM이 실패를 반복 수정할 때 run-id·Candidate SHA·증거가 섞이거나 이전 결과를
    재사용할 수 있는가?

### 7.6 필요성·복잡성 재평가

26. 현재 기능을 `판정 필수`, `조사 보조`, `사람 전용`, `제거 후보`로 전부 분류한다.
27. conflict-rate, fuzzy 순위, rename 진단, watch-suggest가 실제 판정에 필요한가?
28. Candidate lock·digest·Phase 결속 중 같은 위험을 중복 방어하는 부분과 반드시
    유지해야 하는 신뢰 경계는 각각 무엇인가?
29. 현재 CLI 단계 수를 줄여도 자기승인 차단과 증거 재현성을 유지할 수 있는가?
30. 최종 목적을 달성하는 최소 관리파일·gate·상태 전이를 제안한다.

## 8. 필수 반례 test

| 반례 | 기대 결과 |
|---|---|
| 같은 Candidate를 사람 모드와 LLM 자동화 모드로 실행 | canonical verdict·digest 완전 동일 |
| LLM 메모·요약·추천만 변경 | verdict·digest 불변 |
| 제품 코드와 관리 정책을 같은 Candidate에서 함께 완화 | 이전 승인 정책 기준 BLOCK 또는 사람 승인 정지 |
| required path를 Manifest에서 삭제 | 현재 실행에서 삭제된 정책을 사용하지 않고 차단 |
| required test를 Contract에서 삭제·이름 변경 | 필수 test catalog 불일치로 차단 |
| 필수 test 구현을 무조건 PASS하도록 변경 | test 구현 결속 또는 독립 기준에서 차단·승인 정지 |
| 서로 다른 BANK-OM 이관에 같은 일반 PASS 증거 사용 | definition·Contract 결속 불일치로 차단 |
| 하나의 suite에 BANK-OM별 독립 결과가 정확히 존재 | 각 항목 결속 후 허용 가능 |
| fuzzy source 후보만 존재 | 후보는 보이되 기존 정의 실패는 계속 BLOCK |
| 후보가 generated·test 파일에만 존재 | 이관 후보로 사용 금지, BLOCK 유지 |
| LLM이 새 경로를 정답이라고 서술 | 설명과 무관하게 독립 assertion·test 전까지 BLOCK |
| 사람이 LLM 없이 같은 명령 실행 | 누락된 숨은 입력 없이 동일 결과 생성 |
| Candidate에 후속 commit 추가 | 이전 결과·승인·digest 재사용 거부 |
| APPROVAL 파일로 기존 BLOCK을 덮으려 함 | BLOCK 유지 |
| 필수 gate 실행 오류 | PASS가 아니라 ANALYSIS_ERROR |
| 결과 순서·관찰 메타데이터·host만 변경 | canonical verdict·digest 불변 |

기존 test 이름만 인용하지 않는다. fixture가 실제 공격·오입력을 재현하는지 확인한다.
필수 반례가 없으면 먼저 실패해야 할 test 코드, 예상 verdict, 수정 대상 함수를
제시한다.

## 9. Claude 결과 형식

```text
1. 현재 구현 사실 정정
2. 최종 목적 타당성: 채택 / 수정 후 채택 / 재설계
3. 사람·LLM 동등성 판정
4. 관리파일별 신뢰 경계 표
5. 현재 기능 전체 분류표
   - 기능
   - 판정 필수 / 조사 보조 / 사람 전용 / 제거 후보
   - 기계적 사실
   - 추정·사람 판단
   - 현재 verdict 영향
   - 유지·격하·단순화·제거 권고
6. P0 — 허위 PASS·자기승인·BLOCK 완화
7. P1 — 구현 전 필수 설계 변경
8. P2 — 출력·운영성·성능 개선
9. 필수 반례 test 완전성 표
10. 최소 권장 관리파일·gate·상태 전이
11. 구현 순서와 각 단계 재검토 조건
12. 최종 판정
```

근거 없는 동의, “test가 많으니 안전하다”, “LLM 시스템 prompt로 금지하면 된다”는
결론을 금지한다. 실제 코드·schema·공개 CLI·test fixture로 판정한다. 현재 구현과
제안 설계를 명확히 구분하며, 구현되지 않은 안전장치를 현재 기능으로 계산하지
않는다.

## 10. Claude 전달 프롬프트

```text
docs/04-진행/구조보완_최종목표_사람LLM동등검사_CLAUDE_설계검토요청_20260809.md를
끝까지 읽고 요청서 9절 형식대로 읽기 전용 적대적 설계 검토를 수행해줘.

최종 목적은 LLM 자동화 자체가 아니라, 사람과 LLM 어느 쪽이 업그레이드 작업을
수행해도 승인된 같은 관리 정책·Candidate·검사기 버전이면 같은 PASS/BLOCK 계열
판정이 나오는 독립 검사기다. LLM은 선택적 비신뢰 작업자이고 판정자나 승인자가
아니다. LLM 없이 사람도 전체 절차를 실행·이해·복구할 수 있어야 한다.

Manifest·Contract·shared-code definition·test·Candidate lock·Phase digest의 실제
신뢰 경계를 코드로 확인해. LLM이 제품 코드와 정책·test를 함께 약화해 자기 결과를
통과시키는 반례, 실행 주체에 따라 verdict·digest가 달라지는 반례, 유사도 후보와
사람 승인이 BLOCK을 완화하는 반례를 우선 확인해. 현재 기능 전체를 판정 필수,
조사 보조, 사람 전용, 제거 후보로 분류하고 최소 관리파일·gate·상태 전이를 제안해.

기존 test 이름만 믿지 말고 fixture가 실패 모드를 실제 재현하는지 확인해. 코드·문서·
Git 상태·제품 WIP·Candidate lock·증거는 수정하지 마.
```

## 11. 검토 후 결정 순서

1. Claude가 최종 목적과 현재 신뢰 경계를 적대적으로 검토한다.
2. Codex가 Claude 근거를 코드·반례와 다시 대조한다.
3. 사용자에게 개발 전·후 차이와 유지·단순화·제거 항목을 쉬운 말로 설명한다.
4. 사용자가 목표 범위를 확정한 뒤 P0부터 단계별로 구현한다.
5. 각 구현 commit마다 집중 반례·전체 회귀·Claude 재검토를 수행한다.
6. 모든 검사기 검토가 끝난 뒤에만 예행연습 적용 여부를 결정한다.

이 문서 작성 시점에는 최종 목적을 논의·검토 요청으로 정리했을 뿐, 안 B나 새로운
관리 schema를 구현하지 않았다. 현재 예행연습 Candidate와 기존 Phase 증거도 바꾸지
않았다.
