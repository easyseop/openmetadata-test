# PPT LLM 커스텀 운영 ↔ Phase 검사기 Claude 검토 반영

> 작성일: 2026-08-09 KST
>
> 대상 요청서: `PPT_LLM커스텀운영_PHASE검사기_CLAUDE_검토요청_20260809.md`
>
> 현재 검사기 구현: `6079aaff4d1b227df699d3f67262d60a96cd6b07`
>
> 문서 HEAD: `e2b445edbd057e611084f0194d8780b6683b0c5e`

## 1. 결론

Claude의 최종 판정은 `수정 후 채택`이다. 요청서의 핵심 구조는 현재
코드와 부합하며 다음 권고도 타당하다.

- LLM은 코드·명령·증거 수집을 실행한다.
- Phase 검사기는 scope·Candidate SHA·lock·digest·test 결속을 통제한다.
- Markdown 4종은 설명·회고용으로 남기고 Manifest·lock·evidence를
  판정 정본으로 사용한다.
- required path·Contract·충돌 의미·승인·배포는 사람이 판단한다.

Claude가 P0로 분류한 3건은 **현재 검사기 코드의 P0 결함이 아니라
PPT 운영 규칙을 그대로 따를 때의 P0 오용 위험**이다. 검사기 구현에서
새로 확인된 P0는 없다.

## 2. 사실 보정 반영

### 2.1 PPT 파일명

PPT는 `KB-CUST-NEW.md`와 `KB-CUSTOM-NEW.md`를 혼용한다. 분석 요청서는
후자로 통일해 썼으며, 이 사실을 요청서 2.1에 명시했다.

### 2.2 버전 라인

- PPT: 1.12.8 → 1.12.13 → 1.13.1 과거 작업 회고
- Phase 적용 대상: 1.13.1 기준선 → 1.13.2 목표

두 라인의 실행 결과를 섞어 인용하지 않도록 요청서에 경계를 추가했다.

### 2.3 patch-replay

CandidateLock schema, patch-lock, T22 clean-room replay는 개별 도구 수준에서
존재한다. 현재 Phase postmerge는 vendor-merge 전용이며 patch-replay
Candidate는 ancestry 검사에서 `analysis_error`가 된다. 요청서의 “선택
patch-replay 가능” 표현을 “개별 도구만 존재·Phase 미연결”로 보정했다.

## 3. PPT P0 위험

### P0-1. Flyway·DB migration의 LLM 자동 수정

PPT는 Flyway 오류를 Claude가 자동 수정할 수 있는 항목으로 표시한다.
실제 migration·인증·권한·민감 경로는 담당자가 판단해야 하며 LLM은
원인 분석과 수정안만 제안해야 한다.

현재 `sensitive-zones.yaml`에서 `bootstrap/sql/**`은 `watched`이다. 이는
변경 사실을 보여주지만 그 경로라는 이유만으로 `APPROVAL`을 만들지
않는다. migration을 항상 사람 판단으로 올리려면 해당 경로를
`protected`로 올리는 정책 변경이 필요하다. 이 변경은 기존 판정을 바꿀 수
있으므로 임의로 적용하지 않는다.

### P0-2. 확률 0 단정

`크리티컬 오류 가능성 X`와 `네이밍 충돌 가능성 0`은 PPT가 스스로
기록한 TS·Java·migration·codegen 이슈와 모순된다. “가능성은 낮지만,
발생하면 자동 해결하지 말고 담당자에게 보고”로 바꾸어야 한다.

### P0-3. 미실행·미해결 상태의 “가능·완료”

Playwright 미실시·codegen 비호환 미해결 상태는 `PASS`가 아니다. Phase에서
필수 검사가 빠지면 `phase_status=incomplete`이며 진행 가능 판정으로
사용하면 안 된다. PPT의 “가능/위험” 2상태 어휘를 폐기하고
`PASS / APPROVAL / BLOCK / ANALYSIS_ERROR`와 `incomplete`을 분리해 표시해야 한다.

## 4. P1 통합 조건

### P1-1. PPT commit 규칙에 `Customization-ID` trailer 추가

PPT 흐름으로 생성된 commit에 trailer가 없으면 Manifest·ID·scope 연결이
성립하지 않는다. 다만 현재 소스 검사 전체가 이를 조용히 통과시키는
것은 아니다. T30 `check_commit_invariants()`는 upstream 경로를 수정한
무 ID commit을 `CORE_CHANGE_WITHOUT_ID` `BLOCK`으로 처리한다.

재확인:

```text
./.venv/bin/python -m pytest \
  harness/tests/test_invariants.py::test_core_change_without_id_blocks_P0_5 -q

1 passed
```

따라서 이 항목의 우선 조치는 새 탐지기 개발이 아니라 PPT 규칙에
trailer를 필수로 추가하는 것이다.

### P1-2. cherry-pick과 vendor-merge 중 전략 결정

권고는 PPT의 실행 흐름을 vendor-merge Candidate 생성으로 전환하고,
cherry-pick 리허설은 참고 결과로 격하하는 것이다. patch-replay Phase를
새로 만들면 상당한 추가 개발이 필요하다.

### P1-3. “text 충돌 0”의 재정의

merge-tree와 conflict evidence 수집기는 충돌 경로를 결정적으로 재현하지만,
컴파일 케이스·업무 의미 변화까지 판단하지 않는다. 실행 조건은
다음으로 바꾸어야 한다.

```text
text 충돌 0
+ candidate SHA에 결속된 build 성공
+ 필수 Runtime Contract 통과
+ 담당자 승인
= 다음 단계 진행 가능
```

현재 postmerge Phase에는 독립적인 build-success gate가 없다.

### P1-4. PPT 14개 test의 Contract 매핑

실행기와 digest 결속 구조는 있지만 PPT 14개 항목별 Contract YAML,
fixture, runner, 환경 매핑은 없다. 이 목록을 확정하기 전에는
“14개 test가 Phase에 연결됐다”고 표시하면 안 된다.

## 5. P2 보완

- PPT 파일명 `KB-CUST-*`·`KB-CUSTOM-*` 통일
- Markdown 각 결과 블록에 candidate SHA·run-id·result digest 인용
- Runtime 명령은 LLM이 실행해도 비밀값·환경 준비는 사람이 수행
- `APPROVAL` exit code 2에서 반드시 정지
- 검사기 코드·layout·zones·thresholds·Contract 정책을 LLM이 자기 승인용으로
  수정하지 못하게 저장소 권한으로 분리
- 이전 run-id·evidence 출력 경로 재사용 금지
- evidence digest 없는 Markdown `✅ 성공`·`완료` 기록 금지
- 충돌 “기계적/구조적 분류”는 현재 수집기의 기능이 아니다. 현재는
  충돌 경로 재현이며, diff3 stage 분석을 추가해야 충돌 유형 분류가 가능하다.

## 6. 추가 개발 백로그

| 우선순위 | 항목 | 완료 조건 | 외부 판단·입력 |
|---:|---|---|---|
| 1 | postmerge build-success gate | build command·exit·log·artifact가 candidate SHA와 digest로 결속되고 미실행은 incomplete | 신뢰할 CI·build 정책 |
| 2 | PPT 14개 → Contract catalog 매핑 | 각 항목의 Contract ID·fixture·runner·정상/실패 증거·환경 소유자 확정 | DB·API·browser·deployment 환경 |
| 3 | migration 정책 강화 | 해당 경로가 `protected`로 분류되고 담당자 판단 없이 진행하지 못함 | 정책 owner 승인 |
| 4 | 충돌 유형 분류 | add/add·modify/delete·rename·동일 파일 양쪽 변경 등을 결정적으로 분류하고 반례 test로 고정 | 분류 정책 |
| 5 | release T91 Phase 연결 | artifact-verified result·승인·release digest가 하나의 승격 증거로 결속 | 조직 승인·서명 정책 |
| 6 | 효율 측정 | 단계별 시작/종료, 재실행 횟수, verdict 전이, 승인 대기, token 사용량을 별도 감사 데이터로 저장 | 성과 측정 정책 |

1·2·3·5·6번은 신뢰 환경·조직 정책·업무 Contract 선택이 필요하다.
임의값으로 구현하지 않는다.

## 7. 추가 반례 test 후보

1. trailer 없는 upstream commit이 T30에서 `BLOCK`되는지
2. merge-tree 충돌 0이지만 컴파일이 실패하는 candidate가 source-only에서
   어떤 판정을 내는지
3. migration 변경과 change-intent 누락·정책 레벨에 따른 판정 차이
4. 생성코드 재생성으로 required path가 사라졌을 때 T26·drift 차단
5. premerge `APPROVAL` exit code 2에서 LLM orchestration이 정지하는지

1번은 기존
`test_core_change_without_id_blocks_P0_5`로 재확인했다. 2~5번은 각 정책·
build gate·LLM orchestrator 범위를 확정한 뒤 추가한다.

## 8. 즉시 적용 범위

현재 검사기만으로 시작할 수 있는 범위는 다음과 같다.

1. `Customization-ID` trailer가 있는 기능 commit 준비
2. `plan → 담당자 승인 → apply → validate → source`
3. `candidate-select → prep-official → preflight → premerge`
4. 별도 제품 branch에서 사람 판단을 포함한 vendor merge
5. 새 Candidate lock 승인·활성화·재선택
6. `collect-conflict-evidence → preflight → postmerge → phase-status`

이 이후 단계에는 실제 build artifact·Runtime Contract·승인·배포 입력이 필요하다.
따라서 현재 단계의 정확한 표현은 **운영 완료가 아니라, PPT 운영
흐름을 Phase 검사기에 연결할 수 있는 설계를 수정 후 채택한 상태**이다.
