# Phase Candidate 준비·승인·활성화 자동화 개발 요청

> 작성일: 2026-08-09 KST
>
> 대상 저장소: `easyseop/openmetadata-test`
>
> 대상 branch: `codex/phase-bundling-safety-fix-20260808`
> 요청 범위: Candidate lock을 준비하고, 사람의 승인을 기록하고, 활성 Candidate로
> 지정하는 공개 CLI와 사용자 안내를 추가한다. 기존 11단계 예행연습 가이드는
> 수정하지 않는다.

## 1. 개발이 필요한 이유

현재 `candidate-select`는 승인된 Candidate lock과 `active-candidate.yaml`이 이미
있을 때만 동작한다. 이 안전 정책은 맞지만, 두 파일을 만드는 공개 CLI가 없다.
처음 실행하는 사용자는 다음 메시지를 받은 뒤 어떤 파일을 어떤 순서로 만들어야
하는지 알기 어렵다.

```text
[1/6] 활성 Candidate 확인
결과: 중단 · 분석 오류
사유: no active-candidate pointer: .../candidate-locks/active-candidate.yaml
다음 행동: 승인된 Candidate lock과 active-candidate.yaml을 준비한 뒤 다시 실행하세요.
```

2026-08-09 임시 복구 명령도 Python 코드를 heredoc으로 전달하면서 같은 코드 안에서
`input()`을 호출해 다음 오류가 발생했다.

```text
승인자 표기 [데이터시스템부]:
EOFError: EOF when reading a line
```

이 오류는 Candidate 검증 실패가 아니라 표준입력 사용 방식의 결함이다. 정식 CLI는
heredoc 안에서 대화형 입력을 요구하지 않아야 한다.

## 2. 현재 기준선과 실제 입력

1.13.2 병합 전 기준선으로 활성화할 1.13.1 Candidate는 다음과 같다.

| 항목 | 값 |
|---|---|
| 등록 묶음 | `om-temp-1.13.1` |
| Candidate 저장소 | `easyseop/OpenMetadata` |
| Candidate commit | `8ac18ad053d9274774e274ba17b35911ac0b9dcb` |
| Candidate tree | `e86980f6d71295465fe6e75e5169fab57cebd4c4` |
| 산출물 종류 | `build-artifact` |
| 산출물 digest | `sha256:96854a63064e563d8a1ce8f9289e3d8b2aad35a0d78836badf7cd7409aff7319` |
| Candidate lock digest | `sha256:f722e874dade55f1edb56e1c284edf1d97633138d0a3c1ba38c98a108833419d` |
| 검증된 원본 lock | `evidence/om-1.13.1-runtime-20260807-01/candidate-lock.yaml` |
| Runtime 결과 | `evidence/om-1.13.1-runtime-20260807-01/acgh-result.yaml` · canonical verdict `pass` |

`candidate-select`가 읽는 최종 구조는 다음과 같다.

```text
harness/registrations/om-temp-1.13.1/candidate-locks/
├── om-1.13.1-runtime-ready.yaml
├── om-1.13.1-runtime-ready.approval.yaml
└── active-candidate.yaml
```

## 3. 반드시 유지할 안전 경계

도구가 Candidate를 자동으로 승인하면 안 된다. 다음 책임을 분리한다.

| 구분 | 도구가 수행 | 사람이 수행 |
|---|---|---|
| lock 준비 | schema, commit, tree, artifact digest와 기존 결과 결속 검사 | 준비할 Candidate와 근거 결과 선택 |
| 승인 | 승인 양식 생성, 필수값·RFC3339·digest 검증 | 승인자 표기, 승인 사유, 승인 결정 |
| 활성화 | 승인된 lock digest와 파일을 다시 검사하고 포인터를 원자적으로 기록 | 어느 승인된 Candidate를 활성화할지 명시 |

다음 규칙을 완화하지 않는다.

1. 가장 최근 lock을 자동으로 선택하지 않는다.
2. 승인 파일이 없거나 placeholder이면 활성화하지 않는다.
3. 승인 파일의 `candidate_lock_digest`가 실제 lock digest와 다르면 차단한다.
4. 기존 lock, 승인 파일, 활성 포인터를 기본 동작으로 덮어쓰지 않는다.
5. 자동화·LLM은 승인자 이름이나 승인 사유를 추측해 채우지 않는다.
6. 실제 조직 권한은 이 도구가 검증했다고 주장하지 않는다.
7. 파일 생성 도중 실패하면 부분 파일을 정식 결과로 남기지 않는다.

## 4. 요청하는 공개 CLI

`harness/om_workflow.py`에 다음 명령을 추가한다. 최종 이름은 기존 CLI 네이밍과
충돌하지 않는 범위에서 조정할 수 있지만, 역할은 합치지 않는다.

### 4.1 `candidate-prepare`

검증된 Candidate lock을 등록 묶음의 `candidate-locks/`에 준비한다.

예시:

```bash
./.venv/bin/python harness/om_workflow.py candidate-prepare \
  --version 1.13.1 \
  --source-lock evidence/om-1.13.1-runtime-20260807-01/candidate-lock.yaml \
  --source-result evidence/om-1.13.1-runtime-20260807-01/acgh-result.yaml \
  --name om-1.13.1-runtime-ready
```

필수 검사:

- source lock schema와 canonical digest
- source result의 canonical verdict가 `pass`인지
- result에 결속된 Candidate commit, tree, artifact digest, lock digest가 source
  lock과 완전히 같은지
- 대상 등록 묶음이 존재하는지
- 출력 이름의 경로 이탈, 절대경로, 예약 파일명 차단
- 기존 같은 이름 파일은 내용이 완전히 같을 때만 `already prepared`; 다르면 차단

성공 출력에는 대상 파일, Candidate SHA, artifact kind·digest, lock digest와 다음
행동인 `candidate-approval-template`을 표시한다.

### 4.2 `candidate-approval-template`

사람이 작성할 승인 양식을 stdout 또는 명시한 출력 파일에 만든다. 이 명령은
승인을 완료하지 않는다.

예시:

```bash
./.venv/bin/python harness/om_workflow.py candidate-approval-template \
  --version 1.13.1 \
  --lock-name om-1.13.1-runtime-ready \
  --output /private/tmp/om-1.13.1-runtime-ready.approval.yaml
```

양식 예시:

```yaml
candidate_lock_digest: sha256:f722e874dade55f1edb56e1c284edf1d97633138d0a3c1ba38c98a108833419d
approver: ""
approved_at: ""
rationale: ""
```

빈 값은 양식에서만 허용한다. 활성화 단계에서는 기존
`validate_approval_metadata`를 사용해 빈 값과 placeholder를 차단한다.

선택적으로 비대화형 승인 파일 생성도 지원할 수 있다. 이 경우 세 값을 모두
명시해야 하며, 누락되면 터미널에서 `input()`을 호출하지 말고 사용법과 누락 필드를
출력한 뒤 종료 코드 2로 끝낸다.

```bash
./.venv/bin/python harness/om_workflow.py candidate-approval-template \
  --version 1.13.1 \
  --lock-name om-1.13.1-runtime-ready \
  --approver '데이터시스템부' \
  --approved-at '2026-08-09T12:00:00+09:00' \
  --rationale '1.13.1 Runtime Contract 9/9 통과 기준선을 1.13.2 사전검사에 사용 승인' \
  --output /private/tmp/om-1.13.1-runtime-ready.approval.yaml
```

### 4.3 `candidate-activate`

사용자가 준비한 승인 파일을 읽고 승인된 lock을 활성화한다.

예시:

```bash
./.venv/bin/python harness/om_workflow.py candidate-activate \
  --version 1.13.1 \
  --lock-name om-1.13.1-runtime-ready \
  --approval /private/tmp/om-1.13.1-runtime-ready.approval.yaml
```

필수 동작:

1. lock을 다시 parse하고 canonical digest를 계산한다.
2. 승인 파일의 digest와 lock digest를 비교한다.
3. `approver`, `approved_at`, `rationale`를 기존 공통 검증기로 검사한다.
4. 승인 파일을 `<lock-name>.approval.yaml`에 O_EXCL 또는 동등한 비덮어쓰기
   방식으로 보관한다.
5. `active-candidate.yaml`을 임시 파일, fsync, atomic replace 방식으로 기록한다.
6. 기존 활성 포인터가 다른 digest를 가리키면 `--replace-active` 같은 명시적 옵션
   없이 변경하지 않는다. 옵션 사용 시 이전·새 digest를 출력한다.
7. 생성 직후 `select_active_candidate()`를 호출해 self-check한다.

성공하면 사용자가 즉시 실행할 다음 명령을 출력한다.

```bash
./.venv/bin/python harness/om_workflow.py candidate-select \
  --version 1.13.1 \
  --output "$OM_EVIDENCE_DIR/candidate-selection.json"
```

## 5. 출력 요구사항

사람용 기본 출력은 현재 `[n/6]` 형식과 어울리는 짧은 한국어로 작성한다. JSON
자동화 출력은 기존 `--output-format json` 규약을 따른다.

각 명령은 다음 항목을 순서대로 보여준다.

1. 무엇을 확인하거나 만들었는지
2. 결과와 종료 코드
3. Candidate commit·artifact kind·lock digest
4. 생성 또는 읽은 파일의 절대경로
5. 자동으로 수행한 부분과 사람 승인이 필요한 부분
6. 다음에 복사해 실행할 정확한 명령

실패 예시는 원인과 복구 행동을 함께 출력한다.

```text
결과: 중단 · 승인 정보 누락
누락 항목: approver, approved_at, rationale
자동 승인: 수행하지 않음
다음 행동: 승인 양식을 담당자에게 전달하고 세 값을 작성한 뒤
  candidate-activate를 다시 실행하세요.
```

## 6. 필수 test와 반례

정상 test:

- 검증된 build-artifact lock 준비
- 승인 양식 생성
- 완전한 승인 파일로 활성화
- 활성화 직후 기존 `candidate-select`가 `selected`
- 같은 내용을 다시 준비했을 때 안전한 `already prepared`
- JSON 출력이 stdout에서 단일 JSON 문서 유지

반례 test:

1. source result verdict가 pass가 아님
2. result와 lock의 Candidate SHA, tree, artifact digest 또는 lock digest 불일치
3. lock 이름의 `../`, 절대경로, `active-candidate`, `.approval` 예약 이름
4. 승인자·시각·사유 누락 또는 placeholder
5. timezone 없는 `approved_at`
6. 승인 digest 변조
7. 승인되지 않은 lock 활성화
8. 기존 다른 lock·승인 파일 덮어쓰기 시도
9. 기존 활성 포인터를 명시적 옵션 없이 교체
10. 파일 생성 중 예외 후 부분 파일이 정식 파일명으로 남지 않음
11. 동시 활성화 시 한 실행만 성공하고 결과가 손상되지 않음
12. stdin이 없는 CI·heredoc 환경에서 대기하거나 `EOFError`를 내지 않음
13. 승인 양식 생성 명령이 승인 완료로 표시되지 않음
14. 조직 권한 미검증 상태를 승인 권한 확인 완료로 표시하지 않음

최소 실행 범위:

```bash
./.venv/bin/python -m pytest \
  harness/tests/test_phase_candidate_select.py \
  harness/tests/test_phase_cli.py \
  harness/tests/test_candidate_prepare.py -q
```

새 test 파일명은 구현 구조에 맞게 조정할 수 있다. 완료 보고에는 정확한 test 파일
목록, passed·skipped 수, 전체 harness 결과와 실패 0을 따로 기록한다.

## 7. 문서·인수인계 완료 조건

- 기존 11단계 예행연습 가이드는 수정하지 않는다.
- 새 Phase 병행 적용 초안에는 기존 수동 파일 생성 설명을 정식 CLI 명령으로만
  교체한다.
- 비개발자용 설명에는 Candidate lock의 의미, 생성 시점, 승인 주체,
  `active-candidate.yaml`과의 차이, 실패 복구를 첫 사용 위치에 설명한다.
- `docs/04-진행/CODEX_CURRENT_HANDOFF.md`에 구현 commit, test 결과, 미완료 외부
  입력, 다음 정확한 명령을 기록한다.
- 구현·test·문서 변경을 한 commit 또는 추적 가능한 연속 commit으로 결속하고
  원격 branch에 push한다.
- 제품 변경 commit이라면 기존 BANK-OM·Customization-ID 규칙을 지킨다. 이번
  요청은 검사기 저장소 변경이므로 제품 코드는 수정하지 않는다.

## 8. 클로드 최종 보고 형식

다음 순서로 보고한다.

1. 구현 commit SHA와 변경 파일
2. 세 CLI의 실제 정상 출력
3. 승인 누락, digest 변조, 기존 포인터 충돌, stdin 없음 반례의 실제 출력
4. 집중 test와 전체 harness 결과
5. 자동화된 부분과 여전히 사람이 해야 하는 승인 판단
6. 실제 OM_TEMP 1.13.2 vendor merge·postmerge·운영 배포가 이번 개발 범위에
   포함되지 않았다는 경계
7. 남은 blocker와 다음 한 개의 실행 명령
