# Phase 안전성·출력 디자인 Claude 최종 검토 요청

> 요청일: 2026-08-08 KST
> 저장소: `easyseop/openmetadata-test`
> branch: `codex/phase-bundling-safety-fix-20260808`
> 구현 검토 기준: `cf17ed206de63a8dd4dfb88ca54cee6cd6a081c8`
> 검토 시작 원격 HEAD: `89304be225d8c2f5a4ad5e697ad010cae6680f42`
> 최종 보완 commit: `01a1a49d0f6354fa4a3c491e99543506357fcb4f`

> 검토 결과: Claude 최종 검토 완료. S-2의 최초 부분집합 조건은 폐기하고,
> `custom_head_sha` 3중 결속과 `git merge-tree` 완전 일치 방식으로 합의했다.
> 구현 상태: 합의한 S-1~S-6과 출력 보완 구현 및 전체 회귀 완료. 구현은
> `01a1a49d0f6354fa4a3c491e99543506357fcb4f`에 결속했다.

## 1. 이번 검토의 목적과 범위

Phase 번들링은 OpenMetadata 공식 새 버전을 기존 커스터마이징과 합치기 전과
합친 후에 검사하고, 결과를 PASS·APPROVAL·BLOCK·ANALYSIS_ERROR 중 하나로
판정하는 도구다. 이번 검토는 다음 두 범위에 집중한다.

1. **기능·안전성 개선:** 최신 구현에 남은 결속·복구·호환성 문제가 있는지 확인한다.
2. **출력·디자인 개선:** 처음 실행하는 사용자가 화면만 보고 현재 상태와 다음 행동을
   정확히 이해할 수 있는지 확인한다.

맨 아래의 LLM 자동화 내용은 개발 요청 범위가 아니다. 이전 평가의 일부 G-룰이
최신 구현에서도 맞는지 확인하기 위한 참고용 재검토 질문이다.

## 2. 현재까지 확인된 완료 상태

Claude는 별도 clone에서 `cf17ed2`를 실행해 이전 검토의 P0 1건, P1 6건,
P2 2건이 실제로 수정됐음을 확인했다.

- build-artifact Candidate lock과 artifact digest 교차 검증
- `run-id` 경로 이탈 차단
- 동시 실행의 결과 덮어쓰기 차단
- canonical·관리자·실무자 결과의 사후 변조 탐지
- Registry·Contract·공유 정의·commit inventory·전체 Manifest digest 결속
- premerge target과 공식 tag·branch commit 결속
- conflict-rate 단독 입력 거부 및 conflict evidence의 SHA·경로 수 재계산
- 전체 `harness/acgh/*.py`를 포함한 harness digest
- validator의 4상태 exit code 정렬

검증 결과도 재현 일치했다.

```text
집중 테스트: 53 passed
전체 harness: 543 passed, 38 skipped
실패: 0
```

skip은 실제 제품 ref, 외부 API, 브라우저 또는 실행 환경이 필요한 기존 항목이며
PASS 증거로 계산하지 않는다. 실제 OpenMetadata 1.13.2 vendor-merge Candidate,
실측 충돌 증거, 담당자 승인, build artifact Runtime Contract, 운영 배포는 아직
수행하지 않았다.

# 1부. 기능·안전성 개선 검토

## 3. 이번에 검토받을 개선안

아래 내용은 구현 전 최종 검토에 사용한 설계 기록이다. Claude 답변에서 S-1,
S-3~S-6은 채택됐고 S-2는 아래의 최종 합의안으로 교체됐다.

### S-1. 6단계에 검사 범위와 운영 배포 제한 표시

현재 `phase-status`는 canonical·관리자·실무자 파일의 일치 여부를 확인하지만
화면에 `verification_scope`를 표시하지 않는다. 따라서 `source-only` PASS가
배포 산출물까지 검증한 결과처럼 보일 수 있다.

제안:

```text
[6/6] Phase 결과 재검증
저장된 판정: pass (계속 가능)
검사 범위: source-only
Canonical: 확인됨
관리자 요약: 확인됨
실무자 상세: 확인됨
운영 배포: build-artifact 검증 전 승인 금지
결과 digest: sha256:<전체 digest>
다음 행동: build-artifact Candidate lock과 Runtime Contract를 준비해 postmerge를 다시 실행하세요.
```

`artifact-verified`일 때도 자동 배포 완료라고 표현하지 않는다. 다음 행동은
“같은 result digest에 담당자 승인을 결속한 뒤 별도 운영 배포 절차로 진행”으로
표시한다. `phase-status`는 저장된 결과의 무결성을 확인하는 명령이며, 현재
배포 파일이나 active Candidate를 다시 검사하는 명령은 아니다.

검토 질문:

- 이 구분이 source-only 결과의 배포 오인을 충분히 막는가?
- `artifact-verified`도 조직 승인 전에는 배포 가능이라고 표현하지 않는 것이 맞는가?

### S-2. conflict evidence와 실제 Git 변경 경로 교차 검사

최종 합의안은 병합 전 승인된 커스터마이징 commit인 `custom_head_sha`를 증거에
추가하고, 실제 3-way merge 입력과 충돌 결과를 재현하는 방식이다.

제안:

1. `custom_head_sha`가 승인된 이전 기준선 Candidate lock의 commit과 같은지 확인한다.
2. `custom_head_sha`가 postmerge Candidate의 ancestor인지 확인한다.
3. `merge_base(target, custom_head)`가 현재 lock의 `upstream.base_sha`와 같은지 확인한다.
4. `merge_changed_paths`는 base 대비 target·custom head 변경 경로의 합집합과
   완전히 같아야 한다.
5. `git merge-tree --write-tree`를 재실행하고 `conflicted_paths`가 재현 결과와
   완전히 같아야 한다.
6. Git 버전, 명령, merge-base, 결과 tree SHA, 원시 출력 digest, 충돌 경로를
   canonical inputs에 기록한다.
7. rename·add-add·base 내용으로 해결한 충돌·attributes/merge driver 차이를
   반례 테스트와 운영 문서에 기록한다.

검토 질문:

- 위 결속이 빠지면 `custom_head_sha`가 새 수기 신뢰 경계가 되므로 세 결속 검사를
  모두 필수로 구현한다.
- 실제 merge 시도 자체의 자동 수집은 `git merge-tree` 재현과 별도로 남은 후속
  개선 항목이다.

### S-3. premerge 필수 입력 누락 오류 구분

현재 `--target`을 생략하면 공식 증거와 비교하면서 `None != <commit SHA>`가
표시될 수 있다.

제안 오류:

```text
premerge에는 --target이 필요합니다.
prep-official 결과의 commit_sha 전체 값을 입력하세요.
```

`--target`을 공식 증거에서 자동 채우는 방식은 사용자의 비교 대상을 숨길 수 있어
채택하지 않고, 명시 입력을 유지하는 방안을 우선한다.

검토 질문: 명시 입력 유지와 공식 증거 기반 자동 채움 중 어느 쪽이 운영 실수를
더 잘 막는가?

### S-4. 중단 후 남은 reservation lock 복구

동시 기록 방지를 위해 `.result.json.lock`을 원자적으로 선점한다. 프로세스가
정상 종료하면 자동으로 제거되지만 강제 종료되면 남을 수 있다.

제안 오류:

```text
다른 실행이 이 증거 경로를 사용 중입니다: <result 경로>
동시 실행이 없는데 오류가 반복되면 <lock 경로>의 생성 시각과 실행 프로세스를
확인하세요. 실행 중인 프로세스가 없을 때만 lock을 제거하고 같은 Phase를 재실행하세요.
```

도구가 오래된 lock을 자동 삭제하지는 않는다. 실행 중인 다른 프로세스의 lock을
잘못 지울 수 있기 때문이다.

검토 질문: PID·host·생성 시각을 lock 내용에 기록해 수동 판단 근거를 보강해야 하는가?

### S-5. 구버전 증거와 출력 형식 호환성

두 호환성 경계를 명시하려 한다.

1. `om_workflow.py`의 Phase 명령은 기본 출력이 human이다. JSON 파싱 자동화는
   `--output-format json`을 명시해야 한다. 하위 `run_phase_bundle.py`의 JSON
   계약은 바뀌지 않았다.
2. `cf17ed2` 이전 증거는 manager summary에 새 digest·scope가 없어 최신
   `phase-status`의 3단 대조를 통과하지 못할 수 있다.

제안 오류:

```text
관리자 또는 실무자 결과가 canonical 결과와 다릅니다.
구버전 형식의 증거라면 최신 검사기로 해당 Phase를 다시 실행하세요.
```

검토 질문: 구버전 결과를 변환하는 migration 도구보다 Phase 재실행을 요구하는
fail-closed 정책이 적절한가?

### S-6. conflict-rate 반올림 문제

현재 evidence의 `conflict_rate`는 경로 수로 계산한 값과 `1e-12` 이내에서 같아야
한다. `1/3` 같은 값은 운영자가 적은 소수 자릿수로 반올림하면 거부될 수 있다.

우선 제안은 `conflict_rate` 필드를 선택 입력으로 바꾸고, 판정에는 항상
`len(conflicted_paths) / len(merge_changed_paths)`로 계산한 값을 사용하는 것이다.
필드가 있으면 참고 값으로 대조하되, 자동 판정의 입력은 경로 목록에서 계산한 값만
사용한다.

검토 질문: 필드를 제거하는 방식과 선택 입력으로 유지하는 방식 중 감사 추적과
운영 편의의 균형이 더 좋은 것은 무엇인가?

# 2부. 출력·디자인 개선 검토

## 4. 화면 공통 원칙

다음 원칙으로 여섯 단계의 human 출력을 통일하려 한다.

- 정렬용 공백을 없애고 `라벨: 값` 형태를 사용한다.
- 한 줄이 길면 후속 줄을 두 칸 들여쓰고 80열 안에서 줄바꿈한다.
- 기계 판정값은 원문을 유지하고 한글 의미를 함께 쓴다.
- `ERROR` 대신 실제 판정 이름인 `ANALYSIS_ERROR`와 “분석 오류”를 사용한다.
- 전체 SHA와 digest를 축약하지 않는다.
- 정상 gate는 요약하고, 검토·차단·미실행 gate만 화면에 표시한다.
- 세부 reasons와 evidence는 `practitioner-detail.json`에서 확인한다.
- 모든 단계에서 종료 코드, 생성된 증거 파일 또는 생성되지 않은 예정 경로,
  다음 행동을 표시한다.

제안 판정 표현:

| 기계 값 | 사람용 표현 | 다음 행동 |
|---|---|---|
| `pass` | `pass (계속 가능)` | 다음 절차 진행 |
| `approval` | `approval (담당자 검토 필요)` | 자동 진행 금지, 사람 승인 대기 |
| `block` | `block (중단)` | 원인 해결 후 전체 Phase 재실행 |
| `analysis_error` | `analysis_error (분석 오류)` | 입력·환경·검사기 오류 해결 후 재실행 |

## 5. 단계별 다음 행동 보완

### 5.1 4단계 premerge 이후

현재 한 문장으로 끝나는 안내를 다음 순서로 바꾸려 한다.

```text
다음 행동:
  1. 담당자가 premerge 결과를 승인합니다.
  2. 별도 제품 branch에서 vendor-merge Candidate를 만듭니다.
  3. 새 Candidate lock을 작성하고 담당자가 승인합니다.
  4. candidate-select를 다시 실행합니다.
  5. postmerge-check를 실행합니다.
```

이 단계에서 자동화는 vendor merge, Candidate lock 승인 또는 조직 결정을 대신하지
않는다.

### 5.2 5단계 postmerge PASS 이후

조건문을 그대로 출력하지 않고 실제 `verification_scope`로 문장을 분기한다.

```text
source-only:
  소스 검사는 통과했습니다. build-artifact 검증 전에는 운영 배포를 승인하지 마세요.

artifact-verified:
  소스와 build artifact 검사는 완료됐습니다. 같은 result digest에 담당자 승인을
  결속한 뒤 별도 운영 배포 절차로 진행하세요.
```

### 5.3 6단계 결과 표현

`결과`는 저장된 Phase 판정과 `phase-status`의 무결성 확인을 혼동할 수 있으므로
다음처럼 나눈다.

```text
저장된 판정: approval (담당자 검토 필요)
재검증 결과: canonical·관리자·실무자 결과 일치
```

## 6. 옵션 이름과 실제 의미

현재 `--version 1.13.1`은 검사할 제품의 최종 버전이 아니라
`harness/registrations/om-temp-1.13.1` 등록 묶음을 선택한다. 기존 명령 호환성을
위해 `--version`은 유지하되 `--registration-version` 별칭을 추가하고 help와
화면에는 “등록 묶음”으로 표시하는 방안을 제안한다.

검토 질문:

- 별칭 추가 후 `--version`을 즉시 deprecated로 표시해야 하는가?
- 같은 등록 묶음이 1.13.2 Candidate 검사에도 사용된다는 설명이 충분한가?

## 7. 실제 출력 예시 검증 계획

문서의 예시는 손으로 작성한 mockup이 아니라 테스트가 실행한 payload 또는 실제
CLI 출력을 저장해 생성한다. 특히 Candidate 선택 실패는 실패 결과 JSON이 생성되는
현재 동작에 맞춰 다음처럼 표시해야 한다.

```text
[1/6] 활성 Candidate 확인
결과: analysis_error (분석 오류)
종료 코드: 3
사유: no active-candidate pointer: <active-candidate.yaml 경로>
Candidate: -
산출물 종류: -
Lock digest: -
다음 행동: 승인된 Candidate lock과 active-candidate.yaml을 준비한 뒤 다시 실행하세요.
증거 파일: <phase-candidate-1.13.1.json 경로>
```

최소 예시 범위:

- 1단계: 선택 성공, active pointer 누락
- 2단계: 생성, 이미 일치, 기존 branch 불일치
- 3단계: 실행 가능, 누락 입력, 잘못된 입력
- 4단계: PASS, APPROVAL, BLOCK 또는 ANALYSIS_ERROR
- 5단계: source-only PASS, artifact-verified PASS, APPROVAL, artifact 불일치
- 6단계: 3단 일치, 관리자·실무자 변조, 구버전 증거

검토 질문: 이 정도 예시면 처음 실행하는 사용자가 성공·중단·복구를 독립적으로
이해하기에 충분한가?

## 8. 1부·2부에 대한 최종 판정 요청

다음 형식으로 답변을 요청한다.

1. P0·P1·P2 발견 사항
2. S-1~S-6 개선안별 `채택 / 수정 후 채택 / 기각`
3. 출력 공통 원칙과 단계별 문구의 모순 여부
4. 실제 구현 전에 추가해야 할 반례 테스트
5. “이 설계대로 구현해도 되는가”에 대한 최종 권고

# 부록. LLM 자동화 G-룰 재검토 요청 — 개발 범위 아님

이 부록은 별도 LLM 기능 개발을 요청하지 않는다. 이전 평가의 G-룰 중 최신 구현으로
전제가 바뀐 항목만 다시 확인해 달라는 요청이다.

| G-룰 | 최신 구현에서 달라진 사실 | 재검토 요청 |
|---|---|---|
| G-4 | conflict-rate 단독 입력을 거부하고 conflict evidence 경로 수에서 다시 계산한다. | “LLM은 숫자를 생성하지 않는다”를 “신뢰 가능한 merge 결과를 수집하되 경로·비율을 창작·수정하지 않는다”로 바꿔도 되는가? |
| G-7 | artifact digest가 build-artifact Candidate lock과 일치해야 하며 source-tree lock과의 임의 결합은 거부한다. | 실제 산출물에서 도구로 계산한 digest 입력은 허용하고 추측·수기 작성만 금지하면 되는가? |
| G-8 | `phase-status`가 manager·practitioner 파일을 canonical 결과에서 재렌더링해 대조한다. | canonical을 정본으로 유지하되 검증된 두 표시 파일도 보고에 사용해도 되는가? |
| G-13 | 결과 경로를 `.lock` 파일로 원자적으로 선점해 동시 덮어쓰기를 차단한다. | 고유 run-id는 보안 필수 규칙이 아니라 운영상 권장 규칙으로 낮춰도 되는가? |
| G-14 | 전체 `harness/acgh/*.py`와 진입점·source runner가 harness digest에 포함된다. | 검사기 Git commit SHA 병기를 필수에서 감사용 권장으로 낮춰도 되는가? |

부록 답변은 각 항목의 `유지 / 문구 수정 / 제거`와 짧은 근거만 요청한다. 이 답변은
향후 정책 검토 참고자료로만 사용하며, 이번 기능·출력 구현 묶음에는 포함하지 않는다.

## 구현 후 검증 결과

```text
Phase·Git 집중 회귀: 182 passed, 1 skipped
전체 harness 회귀: 560 passed, 38 skipped
실패: 0
```

Claude가 요청한 핵심 반례인 base 내용으로 해결한 충돌, 가짜 custom head,
merge-tree에 없는 충돌 경로, rename/rename, add/add, custom merge-driver,
target 누락, scope 없는 구버전, 잔존·손상 lock을 회귀 테스트에 포함했다. 실제
OpenMetadata 1.13.2 merge와 운영 배포는 실행하지 않았다.
