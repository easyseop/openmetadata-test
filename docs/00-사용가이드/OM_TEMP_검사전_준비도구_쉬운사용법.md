# OM_TEMP 검사 전 준비도구 쉬운 사용법

> 갱신: 2026-07-31
>
> 한 줄 결론: 도구가 Git 사실을 먼저 계산하고, 사람이 업무 의미를 확인한
> 제안만 등록자료에 반영한다.

### 역할별로 읽을 곳

| 역할 | 하는 일 | 읽을 절 |
|---|---|---|
| 개발자 | 코드를 commit하고 `plan`을 실행한다 | 4·5 |
| 업무 담당자 | 질문에 답하고 승인서를 작성한다 | 3·6 |
| 검토자 | `apply` 결과와 증거 보관을 확인한다 | 7·10 |

## 1. 이 도구가 하는 일

OpenMetadata는 외부 오픈소스 제품이고, 행내에서는 여기에 기능을 덧붙여
쓴다. 덧붙인 기능 하나하나에 `BANK-OM-001` 같은 번호를 붙여 관리하는데, 이
번호를 BANK-OM ID라고 부른다.

덧붙인 기능을 고친 뒤 검사하려면 “어느 BANK-OM ID가 어느 파일을 바꿨는지”부터
정확해야 한다. 준비도구는 그 사실을 사람이 손으로 적지 않게 하는 도구이며,
다음을 자동으로 확인한다.

1. patch branch(공식 코드만 있는 쪽)와 custom branch(행내 변경까지 있는 쪽)가
   지금 가리키는 정확한 commit SHA
2. 모든 commit 메시지 본문의 `Customization-ID:` 줄. 이 줄이 그 commit을 어느
   BANK-OM 기능의 변경으로 볼지 정한다
3. BANK-OM별 commit 순서와 각 commit이 바꾼 파일
4. patch와 custom의 **최종 상태**를 비교했을 때 남아 있는 파일 차이
5. 기존 등록자료와 현재 Git 이력의 불일치. 등록자료는 세 가지다 —
   Manifest(기능 하나의 변경 범위), Registry(BANK-OM 목록과 담당자),
   Contract(기능이 정상이라고 판단할 조건과 그 테스트)

도구는 담당자, 중요도, 필수 파일, Contract 같은 업무 판단을 추측하지 않는다.
그 항목은 질문으로 만들고 승인을 기다린다.

## 2. 세 단계만 기억하기

```text
plan(읽기 전용 분석) → 담당자 검토·승인 → apply(승인한 제안 적용)
```

`plan`은 실제 등록자료를 바꾸지 않는다. 제안 폴더에 요약·질문·변경 diff와
고정한 SHA를 만들 뿐이다. 어떤 파일이 생기는지는 5절에 있다.

`apply`는 승인한 시점과 지금이 다르면 중단한다. 다음 값 중 하나라도 달라졌을
때다.

- 승인서에 적힌 제안 digest와 실제 제안서의 digest
- patch 또는 custom branch가 가리키는 commit SHA
- Manifest·Registry·Contract 등 등록 입력 파일의 내용

다른 작업자가 같은 등록 폴더에 `apply`를 실행 중이면, 값이 같더라도
잠금 때문에 중단한다.

## 3. 상태 읽는 법

| 상태 | 쉬운 뜻 | 다음 행동 |
|---|---|---|
| `READY` | 자동 계산은 끝났고 질문·오류가 없음 | 제안 diff를 확인하고 승인 |
| `REVIEW_REQUIRED` | 업무 담당자가 판단할 질문이 있음 | 질문별 사유를 승인서에 기록 |
| `BLOCKED` | 안전하게 적용할 수 없는 문제가 있음 | 원인을 고치고 plan 재실행 |
| `ANALYSIS_ERROR` | 입력이나 Git 관계를 신뢰할 수 없어 판단 자체를 못 함 | 통과로 보지 말고, 빠진 commit을 fetch하거나 잘못된 입력 파일을 되돌린 뒤 plan 재실행 |
| `APPLIED` | 승인한 제안과 현재 입력이 같아 반영됨 | 7절의 등록자료 검사 5종과 소스 게이트 실행 |

`READY`도 자동 승인을 뜻하지 않는다. `REVIEW_REQUIRED`도 실패가 아니라,
자동화가 대신 결정하면 안 되는 업무 질문이 남았다는 뜻이다.

## 4. 시작 전에 준비할 것

저장소가 두 개라는 점을 먼저 구분한다.

| 부르는 이름 | 실제 저장소 | 이 도구에서의 역할 |
|---|---|---|
| 제품 저장소 | `easyseop/OM_TEMP` | 검사 대상 코드. patch/custom branch가 여기에 있다 |
| 검사 저장소 | `easyseop/openmetadata-test` | Manifest·Registry·Contract와 준비도구가 있다 |

개발자가 다음 조건을 확인한다.

- 실행 위치: 검사 저장소를 clone한 폴더의 최상위
- 작업 branch: `claude/markdown-file-feedback-26933w`
- 도구: Git, Python 3, 검사 저장소 안의 `.venv`
- 제품 입력: 로컬에 clone한 OM_TEMP, 그리고 `git fetch`로 최신 상태를 받아 둔
  patch/custom ref
- 공식 기준 commit: Registry 파일(`customization-registry.yaml`)의
  `source.upstream_sha`와 `source.snapshot_sha`에 적힌 두 SHA가 그 OM_TEMP
  clone 안에 실제로 존재해야 한다
- 제품 상태: **변경된 tracked 파일도 untracked 파일도 없는** 상태(=
  `git -C /path/to/OM_TEMP status --porcelain` 출력이 비어 있음)
- 권한: plan은 두 저장소 읽기 권한, apply는 검사 저장소의 등록 폴더 쓰기 권한

공식 기준 commit은 OM_TEMP를 clone해도 따라오지 않는다. OpenMetadata 원본에서
따로 받아야 하고, 받지 않으면 `plan`이 `REGISTRATION_GIT_OBJECT_MISSING`으로
멈춘다. 아래 명령의 마지막 줄은 Registry의 `source.upstream_sha` 값이므로,
버전이 바뀌면 그 파일에 적힌 값으로 바꿔서 실행한다.

```bash
git -C /path/to/OM_TEMP fetch --filter=blob:none \
  https://github.com/open-metadata/OpenMetadata.git \
  f329dd4a7e47134a2bd5a06af6181b0ee527ddd9
```

`source.snapshot_sha`도 같은 방법으로 확인한다. 두 SHA 모두
`git -C /path/to/OM_TEMP cat-file -e <SHA>`가 오류 없이 끝나야 한다.

제품 저장소에 commit하지 않은 변경이나 untracked 파일이 남아 있으면, 도구는
그 파일을 임의로 포함하지 않고 `BLOCKED`로 멈춘다. 필요한 변경을 올바른
BANK-OM ID로 commit하거나, 보존할 로컬 파일을 제품 저장소 밖으로 옮긴 뒤
plan을 다시 실행한다.

## 5. 변경안 만들기

검사 저장소 최상위에서 실행한다. `--output`은 아직 없는 폴더를 지정해야 한다.
이미 있는 폴더를 주면 도구가 예전 제안을 덮어쓰지 않고 즉시 거절한다. 그래서
plan을 다시 돌릴 때마다 새 폴더 이름을 쓴다. 또한 `--output`을
`--registration` 폴더 안에 두지 않는다. 제안은 아직 승인 전 임시 자료이고,
등록 폴더는 승인된 결과만 두는 곳이기 때문이다.

`YYYYMMDD`는 실행한 날짜로 바꾼다. 하루에 두 번 이상 실행하면
`om-temp-1.13.0-20260730-2` 처럼 뒤에 구분자를 붙인다.

```bash
PYTHONPATH=harness ./.venv/bin/python harness/prepare_registration.py plan \
  --repo /path/to/OM_TEMP \
  --registration harness/registrations/om-temp-1.13.0 \
  --patch-ref origin/patch/om-1.13.0 \
  --custom-ref origin/custom/om-1.13.0 \
  --product-version 1.13.0 \
  --output harness/preparation-plans/om-temp-1.13.0-20260730
```

실행이 끝나면 지정한 폴더에 파일 8개가 생긴다. 이 중 먼저 볼 것은 세 개다.

| 파일 | 이 순서로 본다 |
|---|---|
| `summary.md` | ① 전체 상태와 질문·차단 건수를 확인한다 |
| `review-required.yaml` | ② 사람이 답해야 할 질문을 하나씩 읽는다. 각 질문에 관련 BANK-OM ID와 경로가 붙어 있다 |
| `diff.patch` | ③ 승인하면 Manifest·Registry가 실제로 어떻게 바뀌는지 확인한다 |

나머지는 나중에 “왜 이렇게 판단했는가”를 되짚을 때 쓰는 근거 자료다.
처음부터 다 읽을 필요는 없다.

| 파일 | 내용 |
|---|---|
| `proposal.yaml` | 제안 전체. `apply`가 실제로 읽는 파일 |
| `proposal-digest.txt` | 위 파일의 digest. 승인서에 적히는 값 |
| `commit-inventory.yaml` | BANK-OM ID별 commit 목록과 각 commit이 바꾼 파일 |
| `current-diff-paths.txt` | patch와 custom의 최종 상태 차이 경로 목록 |
| `registration-approval.template.yaml` | 6절에서 채울 승인서 양식 |

**이 파일들을 손으로 고치지 않는다.** `apply`는 제안서를 그대로 믿지 않고,
고정된 SHA에서 Git 사실을 처음부터 다시 계산해 제안서와 대조한다. 따라서
제안서를 편집하면 승인서의 digest가 맞더라도 `STALE_PROPOSAL`로 거절된다.
내용을 바꿔야 하면 원인을 고치고 새 출력 폴더에서 `plan`을 다시 실행한다.

`review-required.yaml`에 나오는 질문 코드는 여섯 가지다.

| 코드 | 무엇을 묻는가 |
|---|---|
| `NEW_CUSTOMIZATION_INPUT` | 새 BANK-OM ID의 사람 정책 입력이 아직 없음 |
| `NEW_CUSTOMIZATION_APPROVAL` | 새 BANK-OM의 업무 범위·담당자·필수 경로·Contract 확인 |
| `REQUIRED_PATH_DECISION` | 새로 바뀐 파일을 `required_changed_paths`에 넣을지 |
| `BANK_ONLY_WATCH_DECISION` | 공식 patch에 없는 기존 watch 경로를 계속 둘지 |
| `REVERTED_PATH_DECISION` | 바꿨다가 되돌려 최종 diff에 없는 경로가 의도한 결과인지 |
| `REMOVED_PATH_DECISION` | 삭제하거나 이름을 바꿔 custom 최종 상태에 없는 경로 처리 |

### 새 BANK-OM ID가 발견된 경우

commit 메시지에서 아직 등록된 적 없는 `Customization-ID:`가 나오면, 도구는
그 기능의 담당자·중요도·필수 파일을 알 수 없으므로 Manifest를 스스로 만들지
않는다. 사람이 다음 두 가지를 준비해야 한다.

**첫째, Contract 쪽에서 새 ID를 가리키게 한다.** 연결은 양쪽에 적는다.
Manifest의 `contracts`는 기능 → Contract 방향이고, Contract 파일의
`customization_ids`는 Contract → 기능 방향이다. 아래 예처럼 Contract 파일에도
새 ID를 추가한다.

```yaml
# harness/registrations/om-temp-1.13.0/contracts.yaml
contracts:
- id: CONTRACT-NEW-FEATURE
  title: 예금 상품 코드 검색 확장
  invariant: 예금 상품 코드로 검색한 결과가 재색인 뒤에도 동일하게 조회된다.
  required_tests:
  - tests/bank/contracts/test_deposit_code.py::test_search_roundtrip
  customization_ids:
  - BANK-OM-008        # ← 이 줄을 추가한다
```

`required_tests`에 적은 파일과 함수는 검사 저장소에 실제로 있어야 한다.
없으면 등록자료 검사에서 걸린다.

**둘째, 새 ID의 사람 입력 YAML을 만든다.** 파일 이름은 자유이고, 경로를
plan에 `--new-id-input`으로 넘긴다.

```yaml
BANK-OM-008:
  title: 예금 상품 코드 검색 확장
  owner: 데이터플랫폼팀
  owner_status: assigned
  criticality: high
  kind: core-patch
  provenance: candidate-follow-up
  required_changed_paths:
    - openmetadata-service/src/main/java/org/openmetadata/service/resources/deposits/DepositResource.java
  contracts:
    - CONTRACT-NEW-FEATURE
  direct_tests: []
  watch_dependencies: []
  series_allowed: false
  depends_on: []
```

```bash
PYTHONPATH=harness ./.venv/bin/python harness/prepare_registration.py plan \
  --repo /path/to/OM_TEMP \
  --registration harness/registrations/om-temp-1.13.0 \
  --patch-ref origin/patch/om-1.13.0 \
  --custom-ref origin/custom/om-1.13.0 \
  --product-version 1.13.0 \
  --new-id-input /path/to/new-id-input.yaml \
  --output harness/preparation-plans/om-temp-1.13.0-20260730
```

주의할 값 두 가지가 있다.

- `provenance`는 기본값이 `source-snapshot`이다. 이 값은 “공식 snapshot 시점에
  이미 있던 기능”이라는 뜻이므로, 지금 새로 추가한 기능에 그대로 쓰면 검사가
  차단한다. 새로 만든 기능은 `candidate-follow-up`으로 적는다.
- `required_changed_paths`는 실제 파일 경로를 끝까지 적는다. 예시의 `...`
  같은 줄임 표기나 `**` 같은 넓은 범위를 그대로 두면 안 된다.

owner·필수 파일·Contract를 모르면 임시값을 넣지 않는다. 업무 담당자에게
확인한 뒤 새 plan을 만든다.

## 6. 승인서 만들기

```bash
PYTHONPATH=harness ./.venv/bin/python \
  harness/prepare_registration.py approval-template \
  --proposal harness/preparation-plans/om-temp-1.13.0-20260730/proposal.yaml \
  --output /approved/location/registration-approval.yaml
```

이 명령은 답변 칸이 비어 있는 승인서 양식만 만든다. 아직 승인이 아니다.
다음 자리표시자를 실제 검토 정보로 바꿔야 승인서가 된다.

- `REPLACE_WITH_APPROVER_ID`: 승인자를 식별할 수 있는 조직 ID.
  예: `데이터플랫폼팀/홍길동`
- `REPLACE_WITH_RFC3339_TIME`: 시간대까지 포함한 시각.
  예: `2026-07-30T14:30:00+09:00`
- `REPLACE_WITH_REVIEW_REASON`: 그 판단을 수용한 구체적 이유.
  예: `이 경로는 행내 전용 화면이라 공식 patch에 없는 것이 정상이며 계속 watch한다`

비밀번호, 토큰, 개인 키는 승인서에 쓰지 않는다. `review-required.yaml`에 있는
모든 `REVIEW-nnnn` 질문에 정확히 한 번씩 답해야 한다. 하나라도 빠지거나
같은 번호에 두 번 답하면 apply가 중단한다.

승인서에는 “수용” 한 가지 답만 적을 수 있다. 담당자가 제안에 동의하지 않으면
승인서에서 답을 바꿔 표현할 방법이 없으므로, 그 승인서는 완성하지 말고
apply도 실행하지 않는다. 대신 원인을 고친다 — Manifest·Registry·Contract를
수정하거나, 제품 저장소에서 commit을 다시 만든 뒤, 5절의 plan부터 새 출력
폴더로 다시 실행한다.

## 7. 승인한 제안 적용하기

```bash
PYTHONPATH=harness ./.venv/bin/python harness/prepare_registration.py apply \
  --repo /path/to/OM_TEMP \
  --registration harness/registrations/om-temp-1.13.0 \
  --proposal harness/preparation-plans/om-temp-1.13.0-20260730/proposal.yaml \
  --approval /approved/location/registration-approval.yaml \
  --result /approved/location/registration-apply-result.json
```

`APPLIED`가 나오면 등록자료 자체가 규칙에 맞는지 확인한다. 이 명령은 5개
항목을 한 번에 검사한다.

```bash
./.venv/bin/python \
  harness/registrations/om-temp-1.13.0/validate_registration_bundle.py \
  --repo /path/to/OM_TEMP \
  --registration harness/registrations/om-temp-1.13.0 \
  --layout harness/registrations/om-temp-1.13.0/repository-layout.yaml \
  --output harness/registrations/om-temp-1.13.0/registration-validation-results.json
```

5개가 모두 `pass`가 된 뒤에야 다음 단계인 소스 게이트를 실행한다.

소스 게이트는 아무 코드에서나 돌리면 안 되고, 공식 OpenMetadata 이력 위에
행내 commit이 쌓여 있는 “검사 후보”에서 돌려야 한다. 원격 custom branch의
HEAD는 이 조건을 만족하지 않는다. 그 branch는 공식 이력과 이어지지 않은
독립 snapshot이라서, 겉보기에 파일 내용이 같아도 “공식 어느 버전에서
출발했는가”를 증명하지 못한다.

검사 후보를 어떻게 다시 만드는지는
`harness/registrations/om-temp-1.13.0/REPRODUCIBILITY.md`에 단계별로 있다.
그 문서대로 만든 결과의 digest가 문서에 적힌 값과 같아야 한다.

적용 중 파일 쓰기가 실패하면 도구가 적용 전 내용을 되돌리고 잠금 파일을
지운다. 단, 프로세스가 강제 종료되면(`kill -9`, 터미널 종료, 서버 재부팅)
도구가 정리할 기회를 얻지 못하므로 잠금 파일이 남는다.

- `STALE_PROPOSAL`: 승인 시점과 지금의 입력이 다르다는 뜻이다. 승인서를
  고쳐서 통과시키려 하지 말고, 새 plan과 새 승인서를 만든다.
- `APPLY_LOCKED`: 등록 폴더에 `.registration-apply.lock` 파일이 이미 있다.
  먼저 그 파일을 열어 본다. 안에 `pid`, `host`, `started_at`,
  `proposal_digest`가 적혀 있다.

```bash
cat harness/registrations/om-temp-1.13.0/.registration-apply.lock
```

`host`에 적힌 장비에서 `pid`에 적힌 프로세스가 아직 살아 있는지 확인한다.
살아 있으면 그 작업이 끝날 때까지 기다린다. 살아 있지 않고 담당자에게도
확인한 뒤에만 잠금 파일을 지운다. **확인 없이 지우면 실행 중인 다른 apply와
같은 파일을 동시에 쓰게 된다.**

## 8. 현재 OM_TEMP 1.13.0 결과

2026-07-30에 실제 원격 branch를 대상으로 `plan`(읽기 전용)까지만 실행했다.
승인과 `apply`는 아직 하지 않았다.

| 항목 | 값 |
|---|---|
| patch | `2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50` |
| custom | `7d19c8952612e77467b0a80d6287170d814f1de1` |
| 상태 | `REVIEW_REQUIRED` |
| 도구가 자동으로 바꾼 등록자료 | 0건 |
| 사람이 답해야 할 질문 | 5건(기능마다 1건) |
| 차단 | 0건 |
| 분석 오류 | 0건 |
| 제안 digest | `sha256:502a6824bb60e02b0d6cf4a66043e9e5d9ec0b22ed70b2c3387437b738d278b7` |

5건은 모두 `BANK_ONLY_WATCH_DECISION`이다. Manifest의 watch 경로 중에 공식
patch 쪽에는 없는 것이 있는데, 이것이 행내 전용이라 정상인지 아니면 이제
필요 없는 오래된 항목인지는 업무 담당자만 판단할 수 있다. 도구는 기존 값을
지우지 않고 질문으로 남겼다.

제안 폴더 `harness/preparation-plans/om-temp-1.13.0-20260730/` 안에 승인서
양식(`registration-approval.template.yaml`)이 함께 있지만, 이 파일은 아직
`REPLACE_WITH_...` 자리표시자만 들어 있는 빈 양식이다. 승인 기록이 아니며,
그대로 `apply`에 넘기면 거절된다.

## 9. 자동 중단하는 대표 위험

| 위험 | 무슨 상황인가 |
|---|---|
| 정리되지 않은 작업 폴더 | 제품 저장소에 commit하지 않은 변경이나 untracked 파일이 남아 있다 |
| commit 메시지 문제 | `Customization-ID:` 줄이 없거나, 한 commit에 ID가 둘 이상이거나, merge commit·변경 없는 빈 commit이다 |
| 영역 혼합 | 제품 코드(core)와 검사 정책·문서(governance)를 한 commit에서 같이 바꿨다 |
| 새 ID의 입력 누락 | 처음 보는 BANK-OM ID인데 5절의 `--new-id-input`을 주지 않았다 |
| 필수 파일 소실 | Manifest의 `required_changed_paths`에 적힌 파일이 이번 변경에 없다 |
| 폐기된 ID 재사용 | `retired`로 표시된 BANK-OM ID를 다시 썼다 |
| 끊긴 commit 순서 | 한 BANK-OM의 commit들이 이어지지 않고 사이에 다른 것이 끼었다 |
| 되돌린 필수 파일 | 필수 파일을 바꿨다가 다시 원래대로 돌려, 최종 diff에는 남지 않았다 |
| 이어지지 않는 두 branch | custom이 patch 위에 그대로 얹혀 있지 않다. 즉 patch commit이 custom의 조상이 아니어서, 두 branch의 차이를 “행내 변경”으로 볼 근거가 없다 |
| 분류할 수 없는 경로 | `repository-layout.yaml`의 어느 영역에도 속하지 않는 경로가 나왔다 |
| 일반 파일이 아닌 것 | symlink, submodule, Git LFS pointer는 내용을 그대로 비교할 수 없다 |
| 승인 뒤 바뀐 입력 | 승인한 다음 branch가 움직였거나 등록자료 파일이 바뀌었다 |
| 손으로 고친 제안서 | 제안서 내용이 Git에서 다시 계산한 사실과 다르다 |
| 동시 실행 | 같은 등록 폴더에 다른 `apply`가 이미 실행 중이다 |

이 경우 도구가 ID·owner·Contract를 임의로 채우거나 정책을 완화하지 않는다.
규칙을 적용해 거절한 결과는 `BLOCKED`(종료코드 1)이고, 입력이나 Git 관계를
믿을 수 없어 판단 자체를 못 한 경우만 `ANALYSIS_ERROR`(종료코드 3)다.

## 10. 보관할 증거와 완료 조건

이번 변경 건의 심사 기록(변경관리 티켓 등 나중에 다시 찾아볼 수 있는 곳)에
다음을 한 묶음으로 남긴다. 하나만 빠져도 “왜 이 값이 통과했는가”를 나중에
설명할 수 없다.

| 남길 것 | 무엇을 증명하는가 |
|---|---|
| 제안 폴더 전체 | 도구가 어떤 Git 사실을 근거로 무엇을 제안했는지 |
| 사람이 작성한 승인서 | 누가·언제·어떤 이유로 그 판단을 수용했는지 |
| `registration-apply-result.json` | 그 승인이 실제로 반영된 결과와 시점 |
| 적용 뒤 `registration-validation-results.json` | 반영된 등록자료가 규칙을 만족하는지 |
| 같은 Candidate lock에 묶인 소스·runtime 결과 | 검사 결과가 정확히 어느 코드 상태를 대상으로 나온 것인지 |

Candidate lock은 “이번에 검사한 대상은 정확히 이 commit(그리고 이 build
artifact)이다”를 고정해 두는 파일이다. 이것이 있어야 소스 검사 결과와 runtime
검사 결과가 같은 대상에서 나왔다고 말할 수 있다.

준비 단계의 완료 조건은 `APPLIED`와 등록자료 검사 5종 PASS다. 배포 단계의
완료 조건은 여기에 실제 build artifact digest, Runtime Contract, 업그레이드,
승격·서명·내부망 반입 증거가 추가된 상태다. **준비가 끝난 것을 배포해도 된다는
뜻으로 쓰지 않는다.**

## 11. 아직 사람이 하거나 외부 환경에서 해야 하는 일

아래는 도구가 대신 할 수 없는 일이다. 이 목록이 남아 있는 동안에는 검사가
모두 통과해도 배포 준비가 끝난 것이 아니다.

| 남은 일 | 누가 |
|---|---|
| 8절의 watch 질문 5건에 답하고 승인서를 실제 승인자 이름으로 완성 | 업무 담당자 |
| Registry에서 `owner: UNASSIGNED`·`owner_status: pending`인 7개 기능에 실제 조직 배정 | 업무 담당자 |
| 원격에 아직 없는 1.13.1 patch/custom branch 만들어 push | 개발자 |
| 전체 Java/UI build와 행내 환경에서의 Runtime Contract 실행 | 개발자·인프라 |
| 실제 이미지·패키지 digest 생성과 승격 | 인프라 |
| 운영 배포 승인, 서명, 내부망 반입 | 운영·보안 |

소스 검사가 통과했다는 것은 “등록자료와 코드가 서로 맞는다”는 뜻이지,
“운영에 올려도 된다”는 뜻이 아니다.
