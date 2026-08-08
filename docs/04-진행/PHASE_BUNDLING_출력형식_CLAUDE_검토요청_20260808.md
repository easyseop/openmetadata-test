# Phase 번들링 출력 형식 Claude 검토 요청

> 상태: 구현 초안·합성 회귀 테스트 완료, 문구 검토 전
> 작업 branch: `codex/phase-bundling-safety-fix-20260808`
> 비교 기준: 외부 검토 기준 `295307d6568b5102c065fc5a093dfa7fa1b46ba5`
> 구현 commit: 이 문서를 포함하는 다음 commit에서 확정

## 1. 왜 다시 고쳤는가

Phase 번들링은 OpenMetadata 공식 새 버전을 기존 커스터마이징과 합치기 전에
영향을 검사하고, 합친 뒤에는 실제 Candidate와 배포 산출물을 다시 검사하는
도구다. 기존 구현은 자동화용 JSON 증거를 만드는 데 집중해 처음 실행하는
사용자가 화면만 보고 다음 행동을 결정하기 어려웠다. 또한 외부 검토에서 실제
Candidate·공식 tag·충돌률·배포 산출물과 검사 결과 사이의 결속 누락이 확인됐다.

이번 변경은 두 목적을 함께 처리한다.

1. 검사 결과가 정확히 어떤 Candidate와 입력에서 나왔는지 검증한다.
2. 여섯 단계 명령이 결과, 중단 이유, 사람이 해야 할 일, 증거 경로를 짧게 출력한다.

이 작업은 실제 OpenMetadata 1.13.2 vendor-merge나 운영 배포를 실행한 것이 아니다.
현재 완료 범위는 검사기 코드와 합성 Git 저장소 회귀 테스트다.

## 2. 검토할 저장소와 실행 방식

- 저장소: `easyseop/openmetadata-test`
- branch: `codex/phase-bundling-safety-fix-20260808`
- 사람용 진입점: `harness/om_workflow.py`
- 자동화용 하위 실행기: `harness/run_phase_bundle.py`
- 기본 출력: `--output-format human`
- 자동화 출력: `--output-format json`

두 출력은 같은 판정 결과를 사용한다. `human`은 화면용 요약이고, `json`은 기존
스크립트·CI가 파싱할 한 줄 JSON이다. 사람용 문구가 바뀌어도 canonical
`result.json`, `manager-summary.json`, `practitioner-detail.json`의 판정 계약은
바뀌지 않는다.

## 3. 여섯 단계에서 사용자가 보는 정보

| 단계 | 명령 | 자동으로 하는 일 | 사람이 판단하거나 준비할 일 |
|---|---|---|---|
| 1/6 | `candidate-select` | 승인된 active Candidate lock의 SHA와 digest 확인 | 승인된 lock과 `active-candidate.yaml` 준비 |
| 2/6 | `prep-official` | 공식 tag, commit, 로컬 branch가 같은 commit인지 고정 | 사용할 공식 release tag 선택 |
| 3/6 | `phase-preflight` | 누락·불일치 입력을 한 번에 수집 | 표시된 담당자 입력과 증거 보완 |
| 4/6 | `premerge-check` | 병합 전 영향·민감 경로 검사 실행 | APPROVAL 항목 검토 후 병합 진행 여부 결정 |
| 5/6 | `postmerge-check` | 병합 Candidate의 소스·선택적 Runtime 검사 실행 | change-intent, 충돌 증거, 배포 산출물과 승인 제공 |
| 6/6 | `phase-status` | canonical·관리자·실무자 파일을 다시 생성해 대조 | 같은 result digest에 승인 결속 또는 불일치 복구 |

`run-id`를 생략하면 마이크로초를 포함한 안전한 시각 기반 값이 자동 생성된다.
사용자가 직접 지정한 `run-id`에 `../` 같은 경로 이탈 표현이 있으면 실행 전에
중단한다. 후속 commit으로 Candidate SHA가 바뀌면 기존 lock과 결과를 재사용할 수
없으며 새 Candidate lock과 새 Phase 실행이 필요하다.

## 4. 사람용 출력 예시

### 4.1 현재 branch에서 실제로 확인한 1단계 중단 예시

현재 등록 폴더에는 활성 Candidate 포인터가 없으므로 다음처럼 exit 3으로
중단된다. 이는 오류를 숨긴 것이 아니라 필요한 준비와 정확한 경로를 알려주는
정상적인 fail-closed 결과다.

```text
[1/6] 활성 Candidate 확인
결과        : 중단 · 분석 오류
종료 코드   : 3
사유        : no active-candidate pointer: .../candidate-locks/active-candidate.yaml
Candidate   : -
산출물 종류 : -
Lock digest : -
다음 행동   : 승인된 Candidate lock과 active-candidate.yaml을 준비한 뒤 다시 실행하세요.
증거 경로   : .../evidence/phase-candidate-1.13.1.json (중단되어 생성되지 않음)
```

### 4.2 합성 회귀 테스트로 확인한 5단계 APPROVAL 예시

```text
[5/6] 병합 후 Candidate 검사
결과        : 담당자 검토 필요 (APPROVAL)
완료 상태   : complete
검사 범위   : source-only
검사 완료   : 5/6
판정 요약   : PASS 5 · APPROVAL 1 · BLOCK 0 · ERROR 0
확인할 검사 : approval(approval)
결과 digest : sha256:1111111111111111111111111111111111111111111111111111111111111111
관리자 요약 : manager-summary.json
실무자 상세 : practitioner-detail.json
다음 행동   : 실무자 상세의 검토 항목을 확인하고 담당자가 승인하세요.
```

`source-only`는 소스 검사까지만 완료했다는 뜻이다. 이 상태가 PASS여도 배포
산출물 검증 완료가 아니다. 운영 배포를 판단하려면 승인된 `build-artifact`
Candidate lock, 일치하는 artifact digest, Runtime Contract 결과가 필요하다.

### 4.3 3단계 입력 보완 예시

정상 항목은 반복하지 않고 조치가 필요한 항목만 표시한다.

```text
[3/6] Phase 실행 전 점검
결과        : 중단 · 입력 보완 필요
차단 항목   : 1개
미실행 검사 : approval
- official-evidence: blocked
  조치: prep-official을 먼저 실행하세요.
다음 행동   : 차단 항목을 해결한 뒤 같은 Phase를 다시 실행하세요.
```

### 4.4 자동화용 JSON 예시

```json
{"candidate_artifact_kind":"source-tree","candidate_commit_sha":"0123456789abcdef0123456789abcdef01234567","candidate_lock_digest":"sha256:...","status":"selected"}
```

CI나 다른 프로그램은 반드시 `--output-format json`을 사용한다. 이 모드는 사람용
머리말과 설명을 섞지 않고 하위 실행기의 JSON을 그대로 출력한다.

## 5. 외부 검토 결과를 어떻게 반영했는가

| 외부 지적 | 이번 구현 | 판정 변화 |
|---|---|---|
| artifact digest가 Candidate와 미결속 | `build-artifact` lock과 digest를 교차 검증하고 `source-tree` lock에 digest 입력을 거부 | 불일치 시 실행 전 중단 |
| `run-id` 경로 이탈 | 실제 공개 CLI에서 `evidence_path()` 사용 | 안전한 증거 폴더 밖 경로면 중단 |
| 동시 실행 결과 덮어쓰기 | 결과 경로 옆 lock 파일을 원자적으로 선점 | 두 실행 중 하나만 기록 가능 |
| 관리자 요약 변조 미탐지 | 세 출력에 result digest를 결속하고 status에서 재렌더링 대조 | 한 파일이라도 다르면 exit 3 |
| Manifest·Registry 미결속 | Registry, Contract, 공유 정의, commit inventory, 전체 Manifest digest 기록 | 등록자료 변경 시 새 result digest 생성 |
| premerge target이 tag와 미결속 | `prep-official` 증거를 premerge 필수 입력으로 사용하고 tag·branch를 다시 SHA 대조 | 다른 target이면 중단 |
| conflict-rate 수기 입력 | Candidate SHA와 변경·충돌 경로가 든 증거 파일을 필수화하고 경로 수로 비율 재계산 | 숫자만 입력하거나 계산이 다르면 중단 |
| harness 일부만 버전 결속 | 전체 `harness/acgh/*.py`와 진입점·runner를 hash | 판정 코드 변경 시 새 harness digest 생성 |
| validator exit 규약 불일치 | PASS·APPROVAL·BLOCK·ANALYSIS_ERROR 집계와 exit code를 공통 verdict 규약으로 정렬 | 원인과 exit code가 같은 의미를 가짐 |

승인자의 실제 조직 권한은 코드만으로 확인할 수 없다. 운영 전에는 GitHub 보호
branch와 CODEOWNERS 또는 사내 결재 ID·전자서명 정책이 별도로 필요하다. 자동화는
승인자 이름, RFC3339 승인 시각, 구체적 사유의 형식과 result digest 결속까지만
검증한다.

## 6. 사람이 준비해야 하는 핵심 입력

`change-intent`는 민감 경로 변경이 의도된 업무 변경인지 담당자가 작성·승인하는
파일이다. Git이 대신 판단할 수 없다. postmerge의 민감 경로 검사가 이 파일을
읽으며, 누락 또는 내용 불일치는 자동 PASS가 아니라 미실행·검토·중단으로 남는다.

`conflict-evidence`는 실제 merge 시도에서 나온 변경 경로와 충돌 경로를 기록한
YAML 또는 JSON이다. 자동화가 Candidate lock의 세 SHA와 경로 수를 다시 대조한다.
예시는 다음과 같다.

```yaml
upstream_base_sha: <1.13.1 전체 commit SHA>
upstream_target_sha: <1.13.2 공식 tag의 전체 commit SHA>
candidate_sha: <vendor-merge Candidate 전체 commit SHA>
merge_changed_paths:
  - openmetadata-ui/src/main/resources/ui/src/App.tsx
  - openmetadata-service/src/main/java/example/Example.java
conflicted_paths:
  - openmetadata-ui/src/main/resources/ui/src/App.tsx
conflict_rate: 0.5
```

현재 구현은 이 파일의 결속과 계산을 검증하지만 merge 명령의 콘솔 로그에서 파일을
자동 생성하지는 않는다. 운영자는 실제 merge 결과로 파일을 작성해야 하며, 자동
수집기가 필요하면 별도 후속 개발 항목으로 다룬다.

## 7. 검토자가 확인할 질문

1. 각 단계의 제목만 보고 단계 목적을 이해할 수 있는가?
2. 출력 첫 화면의 정보량이 과하거나 부족하지 않은가?
3. PASS, APPROVAL, BLOCK, 분석 오류의 표현과 다음 행동이 서로 모순되지 않는가?
4. `source-only`와 `artifact-verified`의 차이가 운영 배포 오인을 막기에 충분한가?
5. 실패 출력이 사용자가 고칠 파일·입력·재실행 단계를 정확히 알려주는가?
6. 사람용 출력과 JSON 출력의 경계가 기존 자동화를 깨지 않는가?
7. 영어로 유지할 실제 코드 용어와 한국어 설명의 조합이 자연스러운가?
8. 화면에는 짧게 두고 관리자·실무자 상세 파일로 내려보낸 정보가 적절한가?

검토 결과는 P0·P1·P2로 구분하고, 수정이 필요한 경우 현재 문구와 권장 문구를
함께 적는다. 이번 검토는 출력 형식과 정보 전달을 중심으로 하되, 출력이 실제
판정·증거와 다르면 안전성 문제로 분류한다.

## 8. 완료와 미완료 경계

완료된 것은 안전성 코드, 사람용·JSON 출력 분리, 합성 회귀 테스트다. 실제
OpenMetadata 1.13.2 공식 tag 준비, vendor-merge Candidate 생성, 실제 충돌률 증거,
담당자 change-intent·승인, build-artifact digest, Runtime Contract, 운영 배포는 아직
수행하지 않았다. 이 외부 입력을 추측해서 예시 PASS를 실제 결과로 기록하면 안 된다.

## 9. 검증 결과

```bash
PYTHONPATH=harness:. .venv/bin/python -m pytest -q \
  harness/tests/test_phase_cli.py \
  harness/tests/test_phase_evidence.py \
  harness/tests/test_phase_rollup.py -o addopts=''
```

결과는 `53 passed`다. 전체 회귀는 다음과 같다.

```bash
PYTHONPATH=harness:. .venv/bin/python -m pytest harness/tests -o addopts='' -q
```

결과는 `543 passed, 38 skipped`, 실패 0건이다. skip은 실제 제품 ref, 외부 API,
브라우저 또는 실행 환경이 필요한 기존 항목이며 PASS에 포함하지 않았다.
