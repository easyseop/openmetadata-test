# OM_TEMP 통합 실행 도구 사용법

`harness/om_workflow.py`는 위키의 긴 Python 명령에서 반복되던 등록 폴더와 정책 파일 경로를 자동으로 선택합니다.

## 실행 전 준비

- 터미널의 현재 위치: 검사기 저장소 최상위 폴더
- Python: 검사기 저장소의 `.venv`
- 제품 코드 저장소: 검사할 커스텀 브랜치가 checkout된 로컬 clone
- 기본 입력: 제품 코드 저장소 경로와 제품 버전

예시에서 `/path/to/OM_TEMP`는 실제 로컬 제품 코드 저장소 경로로 바꿉니다.

## 도구가 버전으로 자동 선택하는 값

`--version 1.13.0`을 입력하면 다음 경로를 자동으로 찾습니다.

- 등록 폴더: `harness/registrations/om-temp-1.13.0`
- Manifest와 Registry·Contract
- `repository-layout.yaml`
- `sensitive-zones.yaml`
- 기본 결과 파일 경로
- plan에서 사용할 `origin/fork/om-1.13.0`
- plan에서 사용할 `origin/custom/om-1.13.0`

실행 전에 터미널에 `자동으로 선택한 입력`이 표시됩니다. 예상한 버전과 경로가 아니면 계속 진행하지 않습니다.

## 작업별 명령

### 승인 전 등록 변경안

```bash
./.venv/bin/python harness/om_workflow.py plan \
  --repo /path/to/OM_TEMP \
  --version 1.13.0
```

- 직접 입력: 제품 코드 저장소 경로, 제품 버전
- 자동 선택: 등록 폴더, 포크·커스텀 브랜치, 새 제안 폴더
- 출력: `summary.md`, `proposal.yaml`, `diff.patch`, 검토 질문과 파생 목록
- 다음 단계: `summary.md` 상태가 READY 또는 REVIEW_REQUIRED일 때만 승인 양식을 만듭니다.

새 BANK-OM ID를 등록할 때만 `--new-id-input /path/to/new-bank-om.yaml`을 추가합니다.

### 빈 승인 양식

```bash
./.venv/bin/python harness/om_workflow.py approval-template \
  --proposal /path/to/proposal.yaml
```

- 직접 입력: plan이 만든 `proposal.yaml`
- 자동 선택: 같은 폴더의 `registration-approval.yaml`
- 출력: 빈 승인 양식
- 다음 단계: 실제 승인자가 자리표시자와 판단 사유를 작성합니다.

### 승인된 변경안 반영

```bash
./.venv/bin/python harness/om_workflow.py apply \
  --repo /path/to/OM_TEMP \
  --version 1.13.0 \
  --proposal /path/to/proposal.yaml \
  --approval /path/to/registration-approval.yaml
```

- 직접 입력: 제품 코드 저장소, 버전, 제안 파일, 승인서
- 자동 선택: 등록 폴더, 적용 결과 파일
- 출력: 변경된 등록자료와 `registration-apply-result.json`
- 다음 단계: 상태가 APPLIED일 때만 등록 검사를 실행합니다.

### 등록자료 5종 검사

```bash
./.venv/bin/python harness/om_workflow.py validate \
  --repo /path/to/OM_TEMP \
  --version 1.13.0
```

- 자동 선택: 등록 폴더, 코드 경로 분류표, 결과 파일
- 출력: `registration-validation-results.json`
- 다음 단계: 5개 항목이 모두 PASS이면 소스 검사를 실행합니다.

### 소스 검사 8종

```bash
./.venv/bin/python harness/om_workflow.py source \
  --repo /path/to/OM_TEMP \
  --version 1.13.0
```

- 자동 선택: 등록 폴더, 코드 경로 분류표, 중요 경로 정책, 결과 파일
- 출력: Candidate lock과 `source-gate-results.json`
- 다음 단계: BLOCK·ANALYSIS ERROR의 원인을 수정한 뒤 같은 검사 대상에서 다시 실행합니다.

### 새 공식 버전의 watch 영향

```bash
./.venv/bin/python harness/om_workflow.py watch \
  --repo /path/to/OM_TEMP \
  --version 1.13.0 \
  --target <새-공식-버전-commit>
```

- 자동 선택: Registry의 현재 공식 commit, 등록 폴더, 결과 파일
- 직접 입력: 새 공식 버전 commit 또는 tag
- 실행 시점: vendor-merge 전
- 출력: `upgrade-watch-results.json`

### 업그레이드 위험 검사

```bash
./.venv/bin/python harness/om_workflow.py risk \
  --repo /path/to/OM_TEMP \
  --version 1.13.0 \
  --target <새-공식-버전-commit> \
  --conflict-rate <실제-충돌률>
```

- 자동 선택: 현재 공식 commit, 커스텀 브랜치 HEAD, 등록 폴더, 경로·위험 정책
- 직접 입력: 새 공식 commit과 실제 충돌률
- 출력: `upgrade-risk-results.json`
- 중단 조건: 사람이 작성해야 하는 `change-intent.yaml`이 없으면 필요한 파일 경로를 표시하고 중단합니다.

### Runtime Contract test

```bash
./.venv/bin/python harness/om_workflow.py runtime \
  --repo /path/to/OM_TEMP \
  --version 1.13.0 \
  --artifact /path/to/deployment-file
```

- 자동 선택: 등록 폴더, 실행 ID, 증거 폴더
- 자동 계산: 배포 파일의 SHA-256 digest
- 출력: Candidate lock, Test run set, 검사 결과

### BANK-OM 제거 test

```bash
./.venv/bin/python harness/om_workflow.py patch-kill \
  --repo /path/to/OM_TEMP \
  --version 1.13.0
```

- 자동 선택: 등록 폴더의 `patch-kill-plan.yaml`, 실행 ID, 결과 경로
- 사람 준비: 어떤 BANK-OM을 제거하고 어떤 test가 실패해야 하는지 계획 파일에 작성
- 중단 조건: 계획 파일이 없으면 필요한 파일 경로를 표시하고 중단합니다.

### JSON 충돌 보조

```bash
./.venv/bin/python harness/om_workflow.py resolve-json \
  --repo /path/to/OM_TEMP
```

- 자동 입력: Git index의 BASE·현재 브랜치·적용하려는 변경
- 출력: 겹치지 않는 JSON 항목만 합친 작업 파일
- 사람 작업: diff와 test를 확인한 뒤 `git add`로 해결 완료를 표시합니다.

## 자동화하지 않는 값

다음 값은 업무 의미 또는 실제 운영 결과이므로 도구가 추측하지 않습니다.

- 새 BANK-OM ID의 담당자·중요도
- required 경로와 간접 watch 경로
- Contract의 정상 조건과 필수 test
- 같은 ID의 여러 commit 허용 여부
- 충돌 해결 코드의 최종 선택
- 실제 충돌률
- 새 공식 버전 commit
- 실제 배포 파일
- 승인자·승인 시각·판단 사유

도구가 자동 선택한 경로와 사람이 입력한 값을 모두 확인한 뒤 결과를 승인합니다.
