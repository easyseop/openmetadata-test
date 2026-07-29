# OM_TEMP 검사 전 준비도구 쉬운 사용법

> 갱신: 2026-07-30
>
> 대상: 개발자, 업무 담당자, 검토자
>
> 한 줄 결론: 도구가 Git 사실을 먼저 계산하고, 사람이 업무 의미를 확인한
> 제안만 등록자료에 반영한다.

## 1. 이 도구가 하는 일

OpenMetadata 은행 기능을 수정한 뒤 검사하려면 “어느 BANK-OM이 어느 파일을
바꿨는지”부터 정확해야 한다. 준비도구는 다음을 자동으로 확인한다.

1. patch와 custom 브랜치가 가리키는 정확한 commit SHA
2. 모든 commit의 `Customization-ID`
3. BANK-OM별 commit 순서와 변경 파일
4. 최종 patch와 custom의 파일 차이
5. 기존 Manifest·Registry·Contract와 현재 Git 이력의 불일치

도구는 담당자, 중요도, 필수 파일, Contract 같은 업무 판단을 추측하지 않는다.
그 항목은 질문으로 만들고 승인을 기다린다.

## 2. 세 단계만 기억하기

```text
plan(읽기 전용 분석) → 담당자 검토·승인 → apply(승인한 제안 적용)
```

`plan`은 실제 등록자료를 바꾸지 않는다. 제안 폴더에는 요약, 전체 질문,
등록자료 변경 diff, 고정 SHA와 digest가 생긴다.

`apply`는 다음 중 하나라도 달라지면 중단한다.

- 승인한 제안 digest
- patch 또는 custom SHA
- Manifest·Registry·Contract 등 등록 입력
- 다른 작업자의 적용 잠금

## 3. 상태 읽는 법

| 상태 | 쉬운 뜻 | 다음 행동 |
|---|---|---|
| `READY` | 자동 계산은 끝났고 질문·오류가 없음 | 제안 diff를 확인하고 승인 |
| `REVIEW_REQUIRED` | 업무 담당자가 판단할 질문이 있음 | 질문별 사유를 승인서에 기록 |
| `BLOCKED` | 안전하게 적용할 수 없는 문제가 있음 | 원인을 고치고 plan 재실행 |
| `ANALYSIS_ERROR` | 입력이나 Git 관계를 신뢰할 수 없음 | 통과로 보지 말고 입력 복구 |
| `APPLIED` | 승인한 제안과 현재 입력이 같아 반영됨 | 등록자료 검사와 실제 게이트 실행 |

`READY`도 자동 승인을 뜻하지 않는다. `REVIEW_REQUIRED`도 실패가 아니라,
자동화가 대신 결정하면 안 되는 업무 질문이 남았다는 뜻이다.

## 4. 시작 전에 준비할 것

개발자가 다음 조건을 확인한다.

- 거버넌스 저장소: `easyseop/openmetadata-test`
- 작업 branch: `codex/strict-manifest-gates`
- 실행 위치: 거버넌스 저장소 루트
- 도구: Git, Python 3, 저장소의 `.venv`
- 제품 입력: 로컬 OM_TEMP clone과 fetch가 끝난 patch/custom ref
- 제품 상태: tracked·untracked 파일이 하나도 없는 clean worktree
- 권한: plan은 읽기 권한, apply는 등록 폴더 쓰기 권한

제품 저장소가 dirty이면 파일을 자동 포함하지 않고 `BLOCKED`로 멈춘다. 필요한
변경을 올바른 BANK-OM ID로 commit하거나, 보존할 로컬 파일을 제품 저장소
밖으로 옮긴 뒤 plan을 다시 실행한다.

## 5. 변경안 만들기

저장소 루트에서 실행한다. 제안 출력은 등록 폴더 밖에 지정해야 한다.

```bash
PYTHONPATH=harness ./.venv/bin/python harness/prepare_registration.py plan \
  --repo /path/to/OM_TEMP \
  --registration harness/registrations/om-temp-1.13.0 \
  --patch-ref origin/patch/om-1.13.0 \
  --custom-ref origin/custom/om-1.13.0 \
  --product-version 1.13.0 \
  --output harness/preparation-plans/om-temp-1.13.0-YYYYMMDD
```

먼저 볼 파일은 세 개다.

| 파일 | 무엇을 보면 되는가 |
|---|---|
| `summary.md` | 상태와 질문·차단 건수 |
| `review-required.yaml` | 사람이 판단할 질문과 관련 BANK-OM·경로 |
| `diff.patch` | 승인하면 바뀔 Manifest·Registry 내용 |

`proposal.yaml`, `commit-inventory.yaml`, `current-diff-paths.txt`는 감사와
재현을 위한 상세 근거다. 처음부터 모두 읽을 필요는 없다.

### 새 BANK-OM ID가 발견된 경우

새 ID는 사람 입력 없이 적용 가능한 Manifest를 만들 수 없다. 먼저 Contract의
`customization_ids`에 새 ID를 역방향으로 연결하고, 아래처럼 YAML을 준비한
뒤 plan에 `--new-id-input`을 추가한다.

```yaml
BANK-OM-008:
  title: 새 기능명
  owner: 실제-담당조직
  owner_status: assigned
  criticality: high
  kind: core-patch
  provenance: candidate-follow-up
  required_changed_paths:
    - openmetadata-service/.../RequiredResource.java
  contracts:
    - CONTRACT-NEW-FEATURE
  direct_tests: []
  watch_dependencies: []
  series_allowed: false
  depends_on: []
```

owner·필수 파일·Contract를 모르면 임시값을 넣지 않는다. 업무 담당자에게
확인한 뒤 새 plan을 만든다.

## 6. 승인서 만들기

```bash
PYTHONPATH=harness ./.venv/bin/python \
  harness/prepare_registration.py approval-template \
  --proposal harness/preparation-plans/om-temp-1.13.0-YYYYMMDD/proposal.yaml \
  --output /approved/location/registration-approval.yaml
```

생성된 파일은 아직 승인이 아니다. 다음 자리표시자를 실제 검토 정보로 바꾼다.

- `REPLACE_WITH_APPROVER_ID`: 승인자를 식별할 수 있는 조직 ID
- `REPLACE_WITH_RFC3339_TIME`: 예: `2026-07-30T14:30:00+09:00`
- `REPLACE_WITH_REVIEW_REASON`: 해당 판단을 수용한 구체적 이유

비밀번호, 토큰, 개인 키는 승인서에 쓰지 않는다. 모든
`REVIEW-nnnn` 질문에 정확히 한 번씩 답해야 한다.
담당자가 제안을 거절하면 `decision` 값을 억지로 바꾸지 말고 apply를 실행하지
않는다. Manifest·Registry·Contract 또는 제품 commit을 수정한 뒤 plan부터
다시 실행한다.

## 7. 승인한 제안 적용하기

```bash
PYTHONPATH=harness ./.venv/bin/python harness/prepare_registration.py apply \
  --repo /path/to/OM_TEMP \
  --registration harness/registrations/om-temp-1.13.0 \
  --proposal harness/preparation-plans/om-temp-1.13.0-YYYYMMDD/proposal.yaml \
  --approval /approved/location/registration-approval.yaml \
  --result /approved/location/registration-apply-result.json
```

`APPLIED`가 나오면 다음 등록자료 검사를 실행한다.

```bash
./.venv/bin/python \
  harness/registrations/om-temp-1.13.0/validate_registration_bundle.py \
  --repo /path/to/OM_TEMP \
  --registration harness/registrations/om-temp-1.13.0 \
  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \
  --output harness/registrations/om-temp-1.13.0/registration-validation-results.json
```

5개 등록 검사가 모두 `pass`인 뒤, 공식 계보를 보존한 검사 후보에서 소스
게이트를 실행한다. 독립 snapshot인 원격 custom HEAD를 공식 계보 후보로
오해하지 않는다. 1.13.0 후보 재구성 방법은
`harness/registrations/om-temp-1.13.0/REPRODUCIBILITY.md`를 따른다.

적용 중 파일 쓰기가 실패하면 도구가 적용 전 내용을 복구하고 잠금을 정리한다.
`STALE_PROPOSAL`이면 승인서를 수정하지 말고 새 plan과 새 승인을 만든다.
`APPLY_LOCKED`이면 다른 적용 작업의 종료 여부를 확인한다. 작업자가 없는
낡은 잠금이라고 독립적으로 확인하기 전에는 잠금 파일을 삭제하지 않는다.

## 8. 현재 OM_TEMP 1.13.0 결과

2026-07-30 실제 원격 branch를 기준으로 읽기 전용 plan을 실행했다.

- patch: `2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50`
- custom: `7d19c8952612e77467b0a80d6287170d814f1de1`
- 상태: `REVIEW_REQUIRED`
- 자동 등록 변경: 0건
- 사람 판단: 기능별 5건
- 차단: 0건
- 분석 오류: 0건
- 제안 digest:
  `sha256:502a6824bb60e02b0d6cf4a66043e9e5d9ec0b22ed70b2c3387437b738d278b7`

질문은 공식 patch에 없는 기존 watch 경로를 계속 watch로 보존할지 확인하는
내용이다. 도구가 기존 값을 지우지 않았으며, 자리표시자만 있는 승인 template은
실제 승인으로 취급하지 않는다.
현재 제안은
`harness/preparation-plans/om-temp-1.13.0-20260730/`에 있다.

## 9. 자동 중단하는 대표 위험

- 미커밋 파일 또는 untracked 파일
- ID 없음, 한 commit의 여러 ID, merge·빈 commit
- Core와 governance 영역을 한 commit에서 혼합
- 등록되지 않은 새 ID의 사람 입력 누락
- 필수 파일 소실, retired ID 재사용, 비연속 commit series
- patch와 custom의 무관한 Git 이력
- 분류할 수 없는 경로
- symlink, submodule, Git LFS pointer
- 승인 뒤 이동한 branch나 변경된 등록자료
- 동시에 실행 중인 다른 apply

이 경우 도구가 ID·owner·Contract를 임의로 채우거나 정책을 완화하지 않는다.

## 10. 보관할 증거와 완료 조건

다음 파일을 같은 변경 검토 기록에 보관한다.

- 제안 폴더 전체
- 사람이 작성한 승인서
- `registration-apply-result.json`
- 적용 뒤 `registration-validation-results.json`
- 같은 Candidate lock에 결속된 소스·runtime 결과

준비 단계의 완료 조건은 `APPLIED`와 등록자료 검사 5종 PASS다. 배포 단계의
완료 조건은 여기에 실제 build artifact digest, Runtime Contract, 업그레이드,
승격·서명·내부망 반입 증거가 추가된 상태다. 준비 완료를 배포 완료로 표현하지
않는다.

## 11. 아직 사람이 하거나 외부 환경에서 해야 하는 일

- 1.13.0 제안의 5개 watch 판단과 실제 승인자 기록
- 조직 owner 배정
- 원격에 없는 1.13.1 patch/custom branch 제공
- 전체 Java/UI build와 행내 Runtime Contract 실행
- 실제 이미지·패키지 digest 생성과 승격
- 운영 배포 승인, 서명, 내부망 반입

소스 검사 성공과 운영 배포 승인은 서로 다른 단계다.
