# OM_TEMP 작업기록 및 인수인계 정본

## 2026-08-06 — ID별 재구성 보조 스크립트 중복 실행 알림 추가

- `reconstruct_series.py`는 기존에는 같은 BANK-OM ID를 두 번 실행하면 이미 들어간 공용 코드에서 `produced no source insertion` 오류가 발생했습니다.
- 현재 미커밋 경로가 해당 ID의 예상 경로와 정확히 같을 때, 깨끗한 `HEAD`에 ID를 한 번 적용한 예상 파일 내용을 임시 폴더에서 계산하고 현재 내용과 비교하도록 변경했습니다.
- 경로와 내용이 모두 같으면 `ALREADY_MATERIALIZED (<N> paths)`와 `Continue with step 5-2`를 출력하고 정상 종료합니다.
- 일부 경로 누락, 예상 밖 경로 또는 내용 불일치가 있으면 완료 알림을 내지 않고 중단합니다.
- 현재 `BANK-OM-001` 작업 폴더에서 48개 경로·내용이 모두 일치하여 완료 알림이 출력되는 것을 확인했습니다.
- 깨끗한 임시 복제본에서 첫 실행 `materialized 48 paths`, 두 번째 실행 `ALREADY_MATERIALIZED (48 paths)`를 확인했습니다.
- Python 문법 검사와 관련 기존 테스트 13개가 통과했습니다.

## 2026-08-06 — 4번 가이드 산출물과 5-1·5-2 출력 해석 보강

- 4-1은 단일 결과 파일을 만드는 단계가 아니라 `custom/om-1.13.1` 전체 파일을 읽기 전용 Git worktree에 펼치는 단계임을 명시했습니다.
- 4-2는 단일 결과 파일이 아니라 공식 1.13.1 상태에서 시작하는 `codex/om-1.13.1-id-series` branch를 만드는 단계임을 명시했습니다.
- 5-1 보조 스크립트는 `proposal.yaml`을 생성하지 않고 코드 작업 폴더의 실제 파일을 수정해 미커밋 Git diff를 만든다는 설명과 실제 터미널 출력 형식을 추가했습니다.
- `BANK-OM-001`의 현재 등록자료 기준 처리 경로 수가 48개임을 코드로 확인해 정상 출력 예시에 반영했습니다.
- 5-2는 `변경 파일 목록 → 파일별 변경 규모 → 파일별 실제 코드 diff` 순서로 나누고, `M`·`??` 표시와 `+`·`-` 줄을 해석하는 방법을 추가했습니다.
- 새 파일은 `git diff`에 아직 보이지 않을 수 있으므로 `status --short`와 파일 내용 확인을 함께 사용하도록 명시했습니다.
- 공통 Markdown 렌더러에 4단계 제목을 추가하고 HTML을 다시 만들었습니다. 끊어진 로컬 링크 0건, 원시 `####` 표시 0건, `git diff --check` 통과를 확인했습니다.

## 2026-08-06 — 현재 컴퓨터 경로 재검증

- `source harness/rehearsal_env.sh`를 다시 실행해 검사기 저장소와 코드 저장소 경로가 존재하는지 확인했습니다.
- `$HOME/om-work/kb_openmetadata`는 없고 기존 원본 복제본은 검사기 저장소의 형제 폴더인 `review-kb-openmetadata`에 있음을 확인했습니다.
- 환경 설정 스크립트가 두 위치를 순서대로 자동 탐색하도록 수정했습니다. 사용자가 `KB_SOURCE_REPO`를 지정하면 그 값을 우선합니다.
- 자동 탐색과 사용자 경로 우선 동작을 각각 실행해 모두 PASS를 확인했습니다.
- 코드 저장소에는 `official/om-1.13.1`과 `custom/om-1.13.1`만 있으며, 다음 단계의 `codex/om-1.13.1-id-series`와 `codex/om-1.13.1-registration-baseline`은 아직 생성되지 않았습니다.

## 2026-08-05 — 다른 컴퓨터에서 재개하기 위한 경로 일반화와 최초 등록 폴더 분리

- 검사기 저장소 루트에서 `source harness/rehearsal_env.sh`를 실행하면 `OM_TEST_REPO`, `OM_CODE_REPO`, `KB_SOURCE_REPO`를 설정하도록 만들었습니다. 새 문서에는 개인의 `/Users/...` 절대 경로를 사용하지 않습니다.
- `harness/initialize_registration_workspace.py`를 추가했습니다. 이 도구는 등록 기준 branch가 official 대비 정확히 111개 경로만 바꾸는지 먼저 확인하고, 확인을 통과한 경우에만 과거 활성 등록 폴더를 지정된 보관 폴더로 이동한 뒤 깨끗한 1.13.1 등록 폴더를 만듭니다.
- 과거 자료는 Git 이력에서 삭제하지 않습니다. 현재 검사가 읽는 활성 폴더에서만 분리해 `harness/registration-archives/` 아래에 보관합니다.
- 현재 로컬에는 `codex/om-1.13.1-registration-baseline` branch가 없고 `custom/om-1.13.1`에는 제외 경로 2개가 남아 있으므로 실제 초기화는 실행하지 않았습니다. 4번 페이지의 111개 등록 기준 branch를 만든 뒤 실행해야 합니다.
- 초기화 도구와 공용 코드 검사 단위검사는 `9 passed`입니다.
- 현재 `plan`에는 완전한 빈 등록 폴더에서 Manifest 7개·Registry·Contract 전체를 생성하는 bootstrap 기능이 없습니다. 최초 초안은 아직 사람이 작성하고 승인해야 하며, 이 사실을 5번·7번 가이드에 명시했습니다.
- Markdown 경로 일반화는 진행됐지만 HTML은 재렌더링 전까지 과거 경로와 설명을 보일 수 있습니다. HTML 재생성·링크 검사·시각 검토가 끝나기 전에는 완성본으로 취급하지 않습니다.
- 자세한 재개 순서와 수정 주의사항은 `docs/04-진행/CODEX_HANDOFF.md`의 `2026-08-05 — 다른 컴퓨터에서 1.13.1 최초 등록 작업 재개` 절을 정본으로 사용합니다.

## 2026-08-05 — 1.13.1 기준 검사 묶음과 결과 JSON 설명 보강

- 등록 승인·기준 검사 가이드 5장에 묶음 실행 명령과 `results.json`의 차이를 추가했습니다. 결과 JSON에는 실행 명령이 아니라 판정과 근거만 저장된다고 명시했습니다.
- 5-1은 `checks[]`의 등록자료 상태 검사 5개, 5-2는 `candidate_lock`과 `gates[]`의 T25·T26·T60-I·T30·T31·T40·T41·T93 및 선택적 공용 코드 검사, 5-3은 단일 `gate` 공용 코드 정의 검사임을 실제 코드 기준으로 정리했습니다.
- 각 검사에 입력·확인 내용·실패 시 확인 대상을 표로 추가하고 세 가지 결과 JSON 구조 예시를 추가했습니다.
- Registry가 `source.shared_code_definitions`를 선언하면 5-2에도 공용 코드 검사가 포함되며, 5-3은 같은 검사를 단독 재실행하여 원인을 좁히는 절차라고 명시했습니다.

## 2026-08-05 — 1.13.1 → 1.13.2 예행연습 목차 순서 고정

- 예행연습의 정본 진입 페이지 `OM_TEMP_1.13.1_1.13.2_예행연습_전체목차.html`을 추가했습니다.
- 전체 작업을 11단계로 고정했습니다: 기준환경 준비 → branch 검증 → 파일·ID 연결 → ID별 commit → 등록 준비 → 검사기 학습 → 1.13.1 기준 등록·검사 → 1.13.2 사전 영향 검사 → vendor merge → 최종 검사 → 검증 tag·release branch.
- 각 HTML에 현재 위치 `1/11`~`11/11`과 전체 목차 링크를 표시했습니다.
- 12개 HTML(목차 1개와 실행 페이지 11개)의 로컬 링크를 검사했으며 누락 링크는 0개입니다.
- `harness/tests/test_om_workflow.py`와 `harness/tests/test_shared_code.py`를 실행했으며 13개 test가 통과했습니다.

> 최초 작성: 2026-08-04
> 용도: Codex 컨텍스트 압축 후 작업 재개, Claude 검토·개발 인계, 작업 결과 감사
> 갱신 규칙: 작업을 시작할 때 목적과 범위를 기록하고, 작업이 끝날 때 실제 변경·검증·미완료 항목·다음 시작점을 같은 항목에 추가합니다.

## 0. 새 작업자가 가장 먼저 읽을 내용

현재 목표는 `kb_openmetadata`에 남아 있는 실제 OpenMetadata 1.13.1 커스터마이징 코드를 `easyseop/OM_TEMP`의 다음 업그레이드 검사 기준환경으로 복원하는 것입니다.

2026-08-04 기준으로 코드 기준환경 복원은 끝났습니다. Manifest·Registry·Contract는 아직 만들지 않았습니다. 다음 작업자는 등록자료를 자동 생성하거나 검사를 실행하지 말고, 113개 변경 파일을 사용자와 기능 단위로 분류하는 작업부터 시작해야 합니다.

## 1. 저장소별 역할

| 저장소 | 역할 | 현재 사용 범위 |
|---|---|---|
| `easyseop/OM_TEMP` | 공식 OpenMetadata 코드와 실제 커스터마이징 코드를 branch로 관리하는 코드 저장소 | `official/om-1.13.1`, `custom/om-1.13.1` 생성 완료 |
| `easyseop/openmetadata-test` | Manifest·Registry·Contract와 검사기·검사 결과를 관리하는 검사기 저장소 | 이번 작업에서는 수정하지 않음 |
| 로컬 `review-kb-openmetadata` | 실제 1.13.1 커스터마이징 원본 스냅샷 | `custom/om-1.13.1` 복원 입력으로 사용 |

문서에서 `코드 저장소`는 `easyseop/OM_TEMP`, `검사기 저장소`는 `easyseop/openmetadata-test`를 뜻합니다. 두 저장소를 합쳐서 하나의 저장소처럼 설명하면 안 됩니다.

## 2. 현재 확정된 운영 결정

1. 공식 버전 코드는 `official/om-<version>` branch에서 관리합니다.
2. 실제 커스터마이징 코드는 `custom/om-<version>` branch에서 관리합니다.
3. 최초 1.13.1 커스터마이징 기준환경에는 release branch를 만들지 않습니다.
4. 상위 공식 버전으로 업그레이드한 뒤 검사와 승인을 통과한 코드에 release branch를 만듭니다.
5. 실제 커스터마이징 원본과 같은지는 commit SHA만 보지 않고 Git tree와 전체 diff로 확인합니다.
6. Manifest·Registry·Contract의 기능 분류와 업무 정상 조건은 사람이 승인해야 합니다.

## 3. 현재 코드 기준값

### 3-1. 입력

| 항목 | 전체 값 |
|---|---|
| 공식 OpenMetadata 1.13.1 commit | `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9` |
| 공식 OpenMetadata 1.13.1 tree | `a8290d23b0fb7a4bdc860c2ff414d799f66417c5` |
| 실제 `kb_openmetadata` snapshot commit | `2c2347043235aa2a4ecba4729774c770fcee5d67` |
| 실제 `kb_openmetadata` snapshot tree | `1df344b65844307fb4637f427778afa4d3b13bf7` |
| OM_TEMP 기존 공식 1.13.0 snapshot commit | `2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50` |

### 3-2. 생성 결과

| branch | 원격 commit | 파일 상태 |
|---|---|---|
| `official/om-1.13.1` | `e6199070c35f717f7ced512bb7b435b9d46b33a3` | 공식 1.13.1 tree와 동일 |
| `custom/om-1.13.1` | `59dae915342eaa3bdca1f9571bfa2ba4533c9a6f` | 실제 `kb_openmetadata` tree와 동일 |

GitHub:

- `https://github.com/easyseop/OM_TEMP/tree/official/om-1.13.1`
- `https://github.com/easyseop/OM_TEMP/tree/custom/om-1.13.1`

## 4. 검증 증거

| 검증 질문 | 실제 결과 | 판정 |
|---|---|---|
| `custom/om-1.13.1`과 `kb-source/main`의 추적 파일이 모두 같은가? | `git diff --quiet` 종료 코드 `0` | PASS |
| 두 대상의 Git tree가 같은가? | 양쪽 모두 `1df344b65844307fb4637f427778afa4d3b13bf7` | PASS |
| 공식 1.13.1 대비 실제 커스터마이징 변경 파일 수는 몇 개인가? | `113` | 확인 완료 |
| `custom/om-1.13.1`이 `official/om-1.13.1` 다음에 이어지는가? | `git merge-base --is-ancestor` 종료 코드 `0` | PASS |
| 작업 폴더에 커밋하지 않은 변경이 남았는가? | `git status --porcelain` 빈 출력 | PASS |
| 원격 branch가 정확한 commit을 가리키는가? | `git ls-remote`에서 위 두 commit 확인 | PASS |

## 5. 구현 방식과 선택 이유

### 공식 1.13.1

OM_TEMP는 공식 OpenMetadata 전체 과거 이력을 복제하는 저장소가 아니라 버전별 전체 파일 상태를 스냅샷 커밋으로 보관해 왔습니다. 따라서 공식 1.13.1도 다음 정보를 한 커밋에 기록했습니다.

- 실제 파일 상태: 공식 1.13.1 tree
- 원본 tag: `1.13.1-release`
- 원본 commit: `afcb2d2…`
- 원본 tree: `a8290d23…`

이 방식은 공식 원본 출처를 보존하면서 OM_TEMP에 불필요한 공식 전체 Git 이력을 복사하지 않습니다.

### 실제 커스터마이징 1.13.1

`custom/om-1.13.1`은 공식 스냅샷 commit을 부모로 두고 실제 `kb_openmetadata` tree를 그대로 기록했습니다. 이 커밋은 BANK-OM 기능별 후속 commit을 대신하지 않습니다. 실제 원본 전체를 손실 없이 복원하기 위한 기준 커밋입니다.

## 6. 이번 작업에서 의도적으로 하지 않은 일

| 하지 않은 일 | 이유 |
|---|---|
| 113개 파일을 BANK-OM ID별로 자동 분류 | 파일 경로만으로 업무 기능 소속을 확정할 수 없음 |
| Manifest 생성 | 필수·허용·감시 경로를 사용자와 함께 결정해야 함 |
| Registry 생성·갱신 | ID·담당자·상태·기준 commit 이력에 대한 승인이 필요함 |
| Contract 생성 | 기능의 정상 업무 동작과 필수 test는 사람이 정의해야 함 |
| 검사 실행 | 검사 입력인 등록자료가 아직 없음 |
| release branch 생성 | 최초 기준환경은 업그레이드 검사·승인 통과 결과가 아님 |

## 7. 다음 작업의 정확한 시작점

다음 작업자는 아래 순서로 진행합니다.

1. 원격 `official/om-1.13.1`과 `custom/om-1.13.1` commit을 다시 확인합니다.
2. 두 branch 사이의 113개 변경 파일 목록을 생성합니다.
3. 각 변경을 기존 BANK-OM ID, 새 BANK-OM ID 후보, 공용 파일 후보로 분류합니다.
4. 분류 근거와 실제 diff 예시를 사용자에게 보여줍니다.
5. 사용자와 Manifest 초안을 확정합니다.
6. Manifest에서 참조할 Registry 항목과 Contract를 함께 확정합니다.
7. 사용자 승인 후 검사기 저장소에 등록자료를 반영합니다.
8. 등록자료가 준비된 뒤에만 검사를 실행합니다.

### 사용자와 Codex의 역할

| 단계 | Codex가 수행할 일 | 사용자가 수행할 일 | 단계 종료 조건 |
|---|---|---|---|
| 1. 변경 목록 준비 | 두 코드 branch를 비교해 113개 파일의 경로·변경 종류·diff 요약을 생성 | 없음 | 113개 파일이 빠짐없이 목록에 있음 |
| 2. 기능별 후보 분류 | 파일 경로와 실제 diff를 근거로 기존 BANK-OM ID·새 ID·공용 파일 후보를 제시 | 후보가 실제 업무 기능과 맞는지 승인·수정 | 모든 파일에 승인된 기능 소속 또는 보류 사유가 있음 |
| 3. Manifest 초안 | 승인된 분류를 기준으로 기능별 Manifest 초안을 생성하고 각 필드의 근거를 표시 | 필수·허용·감시 경로와 기능 설명을 승인 | Manifest별 변경 범위가 확정됨 |
| 4. Registry 초안 | 승인된 BANK-OM ID와 코드 기준 commit을 Registry 형식으로 제시 | ID·담당자·상태·이력 정책을 승인 | Registry 항목이 확정됨 |
| 5. Contract 초안 | 코드와 기존 test를 조사해 정상 업무 동작과 필수 test 후보를 제시 | 실제 정상 조건과 필수 test 여부를 승인 | Contract 또는 보류 사유가 확정됨 |
| 6. 등록 반영 | 승인된 초안을 검사기 저장소의 준비 도구로 plan 생성 | plan의 변경 파일과 내용을 최종 승인 | 승인된 plan이 준비됨 |
| 7. 검사 실행 | 승인된 plan을 apply한 뒤 해당 검사를 실행하고 결과를 설명 | REVIEW·BLOCK 결과에서 업무 판단이 필요한 항목을 결정 | 검사 결과와 결정 근거가 보관됨 |

사용자는 Git 명령을 직접 실행할 필요가 없습니다. 사용자의 첫 번째 행동은 Codex가 제시할 **113개 변경 파일의 기능별 분류 후보를 검토하는 것**입니다.

### 중단 조건

다음 상황에서는 임의로 결정하지 말고 사용자에게 보고합니다.

- 한 파일 또는 코드 구간이 두 BANK-OM 기능에 동시에 속할 수 있을 때
- 기존 BANK-OM ID인지 새 ID인지 업무 의미만으로 판단해야 할 때
- Contract의 정상 조건이나 필수 test가 코드 diff만으로 확인되지 않을 때
- 실제 원본 tree 또는 원격 branch commit이 이 문서의 값과 다를 때

## 8. 관련 산출물

- 예행연습 HTML: `deliverables/OM_TEMP_1.13.1_실제커스터마이징_기준환경_예행연습.html`
- 예행연습 Markdown: `deliverables/OM_TEMP_1.13.1_실제커스터마이징_기준환경_예행연습.md`
- 격리 작업 폴더: `work/om-temp-real-1.13.1`

## 9. 작업 이력

### 2026-08-04 — 실제 1.13.1 기준환경 복원

**목적**
1.13.0 재구현본이 아니라 실제 `kb_openmetadata` 1.13.1 코드를 다음 업그레이드 검사의 출발점으로 만들기 위함입니다.

**작업 내용**

- 공식 1.13.1 tree를 `official/om-1.13.1` 스냅샷 commit으로 기록했습니다.
- 실제 커스터마이징 tree를 `custom/om-1.13.1` 기준 commit으로 기록했습니다.
- 실제 원본 동일성, 113개 변경 파일, branch 관계, 원격 commit을 검증했습니다.
- 두 branch를 `easyseop/OM_TEMP`에 푸시했습니다.
- 동일 과정을 설명하는 Markdown·HTML 예행연습 가이드를 만들었습니다.
- HTML을 브라우저에서 렌더링해 코드 박스와 가로 넘침을 점검했습니다.

**완료 조건**
두 원격 branch가 정확한 commit과 tree를 가리키고, 등록자료가 생성되지 않은 상태입니다.

**다음 작업**
113개 변경 파일을 사용자와 BANK-OM 기능별로 분류한 뒤 Manifest·Registry·Contract를 함께 작성합니다.

### 2026-08-04 — 별도 사전 준비 가이드 생성

**목적**
기존 코덱스 수정본을 변경하지 않고, 처음 따라 하는 운영자가 입력·권한·작업 폴더부터 확인할 수 있는 독립 문서를 제공하기 위함입니다.

**작업 내용**

- `OM_TEMP_1.13.1_기준환경_사전준비_가이드.md`를 새로 만들었습니다.
- 동일 내용을 독립 HTML 문서로 새로 만들었습니다.
- 각 명령을 분리하고, 명령의 역할·정상 결과·중단 조건을 짧게 설명했습니다.
- 기존 `OM_TEMP_1.13.1_실제커스터마이징_기준환경_예행연습` MD·HTML은 변경하지 않았습니다.

**완료된 것 / 완료되지 않은 것**
사전 준비 문서만 생성했습니다. 코드 branch, Manifest·Registry·Contract와 검사 상태에는 변화가 없습니다.

**렌더링 수정**
최초 HTML 검토에서 hero 영역의 밝은 중단 안내 박스가 상위 영역의 흰색 글씨를 상속해 대비가 부족한 문제를 놓쳤습니다. 안내 박스의 글씨를 진한 남색으로 고정하고, 강조 문구는 진한 주황색으로 수정했습니다. 이후 검토에는 가로 넘침뿐 아니라 실제 텍스트·배경 색 대비 검사도 포함합니다.

**로컬 경로 현행화**
기본 로컬 작업 루트는 `$HOME/om-work`입니다. 현재 컴퓨터의 실제 경로는 `source harness/rehearsal_env.sh`로 설정하며, 다른 컴퓨터에서는 `OM_CODE_REPO`와 `KB_SOURCE_REPO`를 해당 폴더에 맞게 덮어씁니다. 새 사전 준비 가이드는 1.13.1 예행연습 복제본을 `$OM_CODE_REPO`에 만들고, 실제 `kb_openmetadata` 원본은 `$KB_SOURCE_REPO`에서 읽도록 일반화했습니다.

**초보자 설명 보완**
3-7은 실제 원본 폴더의 위치를 `kb-source`라는 이름으로 등록할 뿐 코드를 복사하지 않고, 3-8은 등록한 위치에서 실제 커스터마이징 commit과 공식 tag를 가져오는 단계임을 명시했습니다. 각 단계가 최초 복원 재현에 필요한 이유, 다음 단계에서 사용하는 입력, 정상 결과, 중단 조건과 이미 완성된 원격 branch만 받을 때의 생략 조건을 추가했습니다.

**기술 정보 시각 구분**
사전 준비 HTML 본문의 branch 이름, 경로, Git 옵션과 짧은 명령을 연한 파란색 배경·얇은 테두리의 정보 칩으로 표시했습니다. `하는 일`, `왜 필요한가`, `정상 결과`, `중단 조건` 표지도 별도의 연한 명암으로 구분했습니다. 전체 명령을 담은 어두운 코드 박스의 스타일은 유지했습니다. 브라우저 렌더링 결과 가로 넘침은 0건이었고, 본문 정보 칩과 단계 표지의 배경·글자·테두리 색 적용을 확인했습니다.

**Git 작성자 등록 보완**
3-9의 확인 결과가 비어 있을 때 사용할 저장소별(`--local`) 이름·이메일 등록 명령과 재확인 명령을 추가했습니다. 작성자 정보는 commit에 기록되는 값이며 GitHub 로그인·push 권한과는 별개임을 명시했습니다. 이메일은 사용자가 본인 GitHub 계정에서 확인해 입력해야 하며, 예시 placeholder를 그대로 등록하지 않도록 중단 조건을 추가했습니다.

### 2026-08-04 — 로컬 branch 연결 및 검증 가이드 생성

**목적**
사전 준비가 끝난 작업 폴더에서 이미 원격에 준비된 official·custom branch를 다시 생성하지 않고, 정확한 local branch로 연결하여 등록자료 작성 직전 상태까지 안내하기 위함입니다.

**시작 전 입력과 상태**

- 작업 폴더: `$OM_CODE_REPO`
- 현재 local branch: `patch/om-1.13.0`
- `--no-checkout`에 따른 `D` 표시: 13,853개
- 원격 official commit: `e6199070c35f717f7ced512bb7b435b9d46b33a3`
- 원격 custom commit: `59dae915342eaa3bdca1f9571bfa2ba4533c9a6f`
- 실제 커스터마이징 원본 commit: `2c2347043235aa2a4ecba4729774c770fcee5d67`

**실제 작업 내용**

- `OM_TEMP_1.13.1_로컬브랜치_연결_및_검증_가이드.md`를 새로 작성했습니다.
- 같은 내용을 독립 HTML 문서로 작성했습니다.
- 모든 절차를 `수행 내용`, `입력`, `실행 명령`, `예상 결과`, `산출물`, `중단 조건`으로 구분했습니다.
- 기존 사전 준비 문서의 다음 단계 안내를 현행 원격 branch 연결 절차로 수정했습니다.
- 기존 `OM_TEMP_1.13.1_실제커스터마이징_기준환경_예행연습` 문서는 변경하지 않았습니다.

**검증과 증거**

- `/private/tmp`에 별도 `--no-checkout` clone을 만들어 문서의 local branch 연결 명령을 순서대로 실행했습니다.
- custom branch 전환 후 작업 폴더 변경 항목은 0개였습니다.
- official·custom commit은 각각 `e6199070…`, `59dae915…`와 일치했습니다.
- custom과 `kb-source/main`의 파일 동일성 결과는 `0`이었습니다.
- official·custom 간 변경 파일 수는 113개였습니다.
- official 기준 commit의 custom 이력 포함 여부 결과는 `0`이었습니다.

**완료된 것 / 완료되지 않은 것**

- 완료: 실행 가이드와 실제 명령 검증
- 미실행: 사용자의 실제 작업 폴더 branch 전환, 원격 push, 새 commit 생성, Manifest·Registry·Contract 생성, 검사기 실행

**다음 시작점과 중단 조건**
사용자는 새 실행 가이드의 3-1부터 순서대로 진행합니다. 원격 commit, 작업 폴더 상태, 변경 파일 수 또는 branch 관계가 문서의 예상값과 다르면 등록자료 작성으로 이동하지 않습니다.

**문서 간 이동 연결**
사전 준비 HTML·Markdown의 하단에 로컬 branch 연결 및 검증 가이드로 이동하는 링크를 추가했습니다. 로컬 branch 연결 및 검증 HTML·Markdown에는 상단과 하단에 사전 준비 가이드로 돌아가는 링크를 추가했습니다. 두 단계는 `사전 준비 → branch 연결 및 검증` 순서로 직접 이동할 수 있습니다.

### 2026-08-04 — 113개 변경 파일 기능 분류 가이드 생성

**목적**
Manifest 생성 전에 실제 113개 변경 파일을 업무 기능 단위로 분류하고, 자동 분석 결과와 사용자 승인 대상을 분리하기 위함입니다.

**실제 작업 내용**

- 기존 `kb-openmetadata` 등록자료를 참고자료로 사용하여 113개 변경 경로를 대조했습니다.
- 74개 전용 경로, 37개 공용 경로, 2개 미등록 경로로 분류했습니다.
- 7개 주요 기능 후보와 각 기능의 연결·전용·공용 경로 수를 정리했습니다.
- `.claude/settings.json`과 `docker/development/docker-compose.yml`은 BANK-OM 등록에서 제외하기로 결정했습니다. 최종 custom candidate에서는 두 파일을 official branch 내용으로 복원해야 합니다.
- 과거 재구성 과정에서 만든 `BANK-OM-008`~`011`은 이번 1.13.1 등록 대상에서 제외했습니다.
- 공용 변경 파일 37개는 하나의 파일에 여러 ID의 코드 구간이 함께 있으므로, 실제 관련 ID를 모두 `shared-path-owners.yaml`에 기록하는 방식을 권장했습니다.
- Markdown·HTML 기능 분류 가이드와 이전·다음 문서 이동 링크를 만들었습니다.

**검증과 증거**

- 실제 Git diff는 총 113개이며, 수정 `M` 70개와 추가 `A` 43개입니다.
- 7개 주요 기능 참고자료 기준으로 111개 고유 경로가 연결되고 2개 경로가 미등록 상태입니다.
- 기능별 경로 수는 공용 경로를 반복 집계하므로 합산값이 113보다 큽니다.
- `BANK-OM-007`의 추가 후보 2개를 실제 diff로 확인한 결과 Sybase 코드만 있고 Tibero 코드는 없었습니다. 따라서 `BANK-OM-007`은 8개 경로를 유지하는 것이 권장안입니다.

**완료된 것 / 완료되지 않은 것**

- 완료: 분류 후보와 승인표 작성, 미등록 2개 경로 제외 결정, 과거 후속 보정 ID 제외 결정
- 미완료: `BANK-OM-001`~`007` 유지 승인, 공용 변경 파일 37개의 다중 연결 승인, 두 제외 경로의 official 내용 복원 commit, 신규 Manifest·Registry·Contract 생성, 검사기 실행

## 10. 앞으로 추가할 작업기록 형식

### 2026-08-05 — 검사기 간단 학습 페이지 추가

**목적**

- 1.13.1→1.13.2 예행연습에서 사용할 검사기를 실행 전에 익히고, 각 검사의 실행 시점을 브랜치 전략과 연결하기 위함입니다.

**실제 작업 내용**

- 카탈로그 23종과 공용 파일 ID별 코드 정의 검사 1종을 A~E 단계로 분류했습니다.
- `새 OpenMetadata 포크 브랜치 + 직전 커스텀 브랜치 → 다음 커스텀 브랜치의 vendor merge → 검사 → 릴리즈 브랜치`로 이어지는 흐름에 검사 위치를 표시했습니다.
- Git 충돌은 검사기 판정이 아니며, 담당자가 해결한 뒤 소스·동작 검사를 실행한다는 경계를 명시했습니다.
- T20·T21·T22·patch-lock은 선택 `patch-replay` 모드로, T80은 판정권이 없는 보조 자료로 구분했습니다.
- T61·T62·T90·T91의 운영 실행 대기 범위를 현재 구현 상태와 분리해 표시했습니다.
- 후속 가독성 검토에서 모든 검사 설명을 `실제 상황 예시 → 검사기가 묻는 질문 → 결과와 조치` 구조로 바꾸어, 어떤 경우를 말하는지 바로 확인할 수 있게 했습니다.

**검증과 증거**

- HTML 구조를 Python `html.parser`로 파싱하여 주요 용어·링크·테이블 구조를 확인했습니다.
- 공용 파일 ID별 코드 정의 검사의 관련 단위 test 8개가 통과했습니다.
- 브라우저 자동 시각 검사는 로컬 파일 URL 정책 제한으로 실행하지 못했습니다. 페이지는 반응형 그리드와 표 횡스크롤을 적용했습니다.

**완료된 것 / 완료되지 않은 것**

- 완료: 검사기 개념·사용 위치·판정 해석 페이지
- 미완료: 각 검사기의 실행 명령·입력 파일·성공·실패 출력을 담은 후속 실행 페이지, 현재 대기 중인 운영 runtime·승격 증거

**다음 시작점과 중단 조건**

- 113개 변경 파일–BANK-OM ID 연결 승인과 공용 파일 ID별 코드 정의를 완료한 뒤 Manifest·Registry·Contract를 작성합니다.
- 등록자료가 확정되기 전에는 전체 검사 통과를 판정하지 않습니다.

```markdown
### YYYY-MM-DD — 작업명

**목적**
- 이 작업이 필요한 이유

**시작 전 입력과 상태**
- 저장소, branch, commit, 파일, 승인 상태

**실제 작업 내용**
- 변경한 코드·설정·문서
- 자동으로 처리한 부분과 사람이 결정한 부분

**검증과 증거**
- 실행한 명령 또는 검사
- 기대값과 실제값
- PASS·REVIEW·BLOCK 판정

**의사결정과 이유**
- 선택한 방식
- 선택하지 않은 방식과 이유

**완료된 것 / 완료되지 않은 것**
- 현재 구현 상태를 구분

**다음 시작점과 중단 조건**
- 다음 작업자가 첫 번째로 할 일
- 임의 판단하지 말고 사용자에게 물어야 하는 조건
```

## 2026-08-05 — 1.13.1→1.13.2 남은 예행연습 가이드 완성

**목적**
- ID별 commit 후보 구성 이후부터 검증 tag·release branch까지의 순서를 신규 운영자가 페이지 순서대로 따라갈 수 있게 완성했습니다.

**작성한 페이지**
- `OM_TEMP_1.13.1_등록승인_apply_및_기준검사_가이드.md/html`
- `OM_TEMP_1.13.2_공식코드_준비_및_사전영향검사_가이드.md/html`
- `OM_TEMP_1.13.2_vendor_merge_및_충돌해결_가이드.md/html`
- `OM_TEMP_1.13.2_최종검사_및_승인_가이드.md/html`
- `OM_TEMP_1.13.2_검증tag_및_release브랜치_가이드.md/html`

**도구 보완**
- `harness/om_workflow.py validate`가 1.13.1 이후 등록 폴더에서도 공용 validator를 자동 선택하도록 수정했습니다.
- `acgh.shared_code`에 `--output`을 추가해 터미널 판정과 같은 JSON을 증거 파일로 보관할 수 있게 했습니다.

**검증**
- `test_om_workflow.py`와 `test_shared_code.py` 13개가 통과했습니다.
- 실제 1.13.1 등록 검사 명령은 실행됐으며, 현재 제품 코드 작업 폴더가 등록자료의 기준 candidate와 달라 변경 경로 검사에서 `analysis_error`를 반환했습니다. 이 결과는 입력 불일치 시 fail-closed 동작한다는 진단 증거입니다.

**현재 중단 조건**
- 공식 `1.13.2-release` tag는 현재 로컬 저장소에서 확인되지 않았습니다. 실제 공식 target을 확인하기 전에는 1.13.2 branch·merge를 실행하지 않습니다.
- T91 release lock 함수는 구현돼 있지만 신규 운영자용 CLI·CI 연동이 없습니다. 유효한 release lock과 T91 결과가 없으면 검증 tag·release branch를 생성하지 않습니다.

## 2026-08-05 — 등록 승인·기준 검사 가이드 판정 예시 보강

**목적**
- 신규 운영자가 명령만 복사하지 않고, 각 결과 상태가 언제 발생하며 무엇을 고쳐야 하는지 판단할 수 있게 했습니다.

**수정 내용**
- 3-2에 branch 이름을 40자리 commit SHA로 확인하는 이유와 이후 대조 위치를 설명했습니다.
- 1.13.1 단계의 `candidate`는 도구 내부 필드명일 뿐이며, 문서에서는 `1.13.1 기준검사 대상 commit`으로 표현했습니다. 공식 1.13.2를 합친 뒤의 `1.13.2 업그레이드 후보 commit`과 구분합니다.
- `proposal.yaml`은 `등록 변경 제안서`, `source-gate-results.json`은 `소스 검사 결과 파일`로 설명했습니다. `candidate_lock.candidate.commit_sha`는 점으로 연결된 각 요소를 따로 풀어 쓰고, 전체 의미를 `소스 검사가 대상으로 고정하고 실제로 검사한 1.13.1 코드의 commit SHA`로 정리했습니다.
- 코드 이력은 OpenMetadata 코드 저장소, 등록자료 이력은 검사기 저장소, 실행 증거는 실행 ID별 증거 폴더에서 관리한다는 구분을 추가했습니다. `plan`은 기존 등록자료를 바꾸지 않고 제안 파일만 만들며, `apply`가 승인 후 정본 등록자료를 수정한다는 경계를 명시했습니다.
- `빈 승인 양식`은 `승인서 작성용 양식`으로 바꿨습니다. 도구가 제안서 digest와 검토 항목 ID를 채우고 사용자가 승인자·시각·판단·근거를 작성하는 파일임을 설명했습니다.
- 1.13.1 단계의 비교군은 공식 1.13.1과 커스텀 1.13.1이며, 실제 Git 차이와 등록자료 선언을 비교한다고 명시했습니다. 초기 자료 생성만으로 끝나는 것이 아니라 사용자 승인·`apply`·기준 검사 결과 보관까지가 종료 조건입니다.
- `harness/registrations/om-temp-1.13.1/`의 기존 파일은 commit `c2b5c6a`에서 만든 과거 1.13.0→1.13.1 예행연습 자료이며, 현재 실제 1.13.1 승인본이 아님을 확인했습니다. Registry도 `UNASSIGNED/pending` 상태이므로 이번 `plan`에서 비교·수정할 입력으로만 사용하고 사용자가 다시 승인해야 합니다.
- 3-3에 한 실행의 범위, 실행 ID 재사용·교체 기준, 증거 폴더 보관 목적을 설명했습니다.
- 4-1에 official·custom branch가 명령의 어느 인수인지와 기존 등록 폴더의 역할을 표시했습니다.
- 빈 승인 양식의 생성 주기와 작성 전·후 예시를 추가했습니다.
- apply의 `APPLIED`, `STALE_PROPOSAL`, `APPLY_LOCKED`, `ANALYSIS_ERROR` 예시와 조치를 추가했습니다.
- 5-1·5-2·5-3에 낱개 검사별 지원 판정, 축약 결과, 발생 조건과 조치를 펼치기로 추가했습니다.
- 일반적인 `FAIL` 대신 실제 네 판정 `pass`, `approval`, `block`, `analysis_error`의 차이를 명시했습니다.

**검증 기준**
- 지원하지 않는 판정을 검사 예시에 임의로 추가하지 않습니다.
- 붉은 굵은 글씨로 판정 차이를 표시하고, 각 예시에 발생 조건과 다음 조치를 함께 둡니다.
- Markdown을 다시 렌더링하여 펼치기와 강조 표시가 HTML에 생성되는지 확인합니다.
## 2026-08-05 — 예행연습 5~11번 명확성·사실관계 전면 재검토

- `clarity-preflight-review` 기준으로 5~11번 Markdown을 문장·명령·결과 단위로 다시 검토함.
- 5번의 구식 `prepare_registration.py plan` 중복을 제거하고 7번의 `om_workflow.py plan → approval-template → apply`를 정본 절차로 통일함.
- `candidate`를 단계별로 `1.13.1 기준검사 대상`과 `1.13.2 업그레이드 후보`로 구분함.
- 8번 T42는 JSON verdict와 프로세스 종료코드가 일치하지 않을 수 있다는 현재 구현 경계를 추가함.
- 9번에 merge 결과와 JSON 충돌 보조 도구의 성공·중단 사례를 추가함.
- 10번 source 묶음의 실제 구성에서 T32가 미연결임을 코드 대조로 정정함.
- 10·11번의 runtime/build/T90/T91 미실행·CLI 공백을 완료 상태와 분리함.
- 결과 문서: `OM_TEMP_5-11_문장명확성_재검토_결과.md`.
- 후속 사용자 결정: `.claude/settings.json`과 `docker/development/docker-compose.yml` 복원은 이번 1.13.1 기준환경 정리에만 필요한 일회성 작업이므로 5번 운영 가이드 본문에서 삭제함. 실행 명령은 사용자에게 별도로 전달하고, 5번은 정리 완료된 111개 등록 대상 branch 확인부터 시작하도록 변경함.

## 2026-08-06 — ID별 변경의 승인 전 Git 검토 흐름 보강

- `git status --short → git diff → git add -A → git diff --cached → 사용자 승인 → commit` 순서를 5번 가이드에 명시함.
- 각 명령 바로 아래에 신규 운영자가 실제로 확인할 항목을 `여기서는 … 확인하면 됩니다` 형식으로 추가함.
- `git diff`에는 추적 중인 기존 파일의 미커밋 변경만 나오고, `??` 새 파일 내용은 나오지 않는다는 범위를 명시함.
- `git add -A`는 commit이나 원격 전송이 아니라 기존 수정 파일과 새 파일을 승인 전 검토 대상으로 올리는 단계임을 명시함.
- `git diff --cached --name-status`, `--stat`, 전체 diff 순으로 commit 예정 파일 범위·규모·실제 내용을 확인하도록 구성함.
- 새 파일까지 검토한 뒤 승인하도록 `git add -A`와 cached diff를 5-4 commit 단계가 아닌 5-2 승인 전 검토 단계로 이동함.
- 사용자가 제공한 실제 `BANK-OM-001` 터미널 화면을 `git diff` 성공 예시로 추가함. 파일 시작 표시, 초록색 추가 줄, 변경되지 않은 문맥 줄, 다음 파일 시작 표시를 각각 어떻게 읽는지 설명하고 예상하지 않은 삭제 줄이 있으면 승인하지 않도록 명시함.
- ID별 commit 명령을 `★ 핵심 운영기준`으로 표시함. 이 지점은 검사 실행 시작이 아니라 실제 코드 변경과 BANK-OM ID의 추적 이력을 만드는 시작점이며, 이후 별표 항목 요약본에서 검색·수집할 수 있도록 동일한 표기를 사용하기로 함.
- commit 직후 `git show -s --format=fuller HEAD`로 `Customization-ID`가 실제 commit 본문에 기록됐는지 확인하는 절차와 정상·중단 조건을 추가함.
- `BANK-OM-002`~`007` 반복을 한 명령으로 진행하는 `reconstruct_remaining_ids.sh`를 추가함. 각 ID의 적용·staging·전체 cached diff 출력은 자동화하지만, 사용자가 정확한 ID를 입력해야만 commit하도록 승인 경계는 유지함.
- 각 commit 뒤 실제 trailer와 깨끗한 작업 폴더를 자동 확인하며, 불일치·미커밋 잔여 파일·다른 승인 입력이 나오면 다음 ID로 넘어가지 않음.
- 실제 첫 실행에서 `BANK-OM-002` 55개 파일이 staging된 뒤 commit 전에 중단된 상태를 확인함. commit 이력에 001만 보인 것은 002가 아직 commit되지 않았기 때문임.
- 반복 도구를 재실행 가능하게 보완함. 최신 commit의 BANK-OM ID를 읽어 다음 ID부터 시작하고, 다음 ID의 staged 변경이 남아 있으면 재적용하지 않고 검토·승인 단계부터 이어감.
- macOS 터미널에서 전체 diff pager를 `q`로 닫을 때 Git의 SIGPIPE 상태가 `|| exit 3`에 걸려 승인 질문 전에 도구가 종료되는 실제 문제를 확인함.
- 전체 diff를 명시적인 `less -R` pager로 연결하여 `q`를 정상적인 검토 화면 종료로 처리하고, 이후 승인 질문이 계속 표시되도록 수정함. staged된 ID 변경은 재실행 시 그대로 재사용함.
- 실제 7-1 Git log 캡처를 가이드에 추가하고, 짧은 commit SHA·commit 제목·BANK-OM ID 열을 각각 어떻게 확인하는지 설명함. 실제 상태는 001~007 일곱 commit, 최종 변경 경로 111개, 깨끗한 작업 폴더로 확인함.
- `official/om-1.13.1`의 파일 동일성과 Git 이력 연결을 분리해 설명함. 잠재적인 upstream 계보 `block`은 코드 또는 ID별 commit 실패가 아니라 승인된 공식 commit과의 Git 이력 연결 미확인이라는 뜻이며, 실제 발생 전에는 가능성 설명일 뿐임을 명시함.

## 2026-08-06 — 7-4 재구성 검사 결과 축약·실제 차단 해결 절차 반영

- 사용자가 제공한 실제 7-4 화면 두 장을 가이드에 추가함. 첫 화면은 전체 판정·인식 ID·제외 파일·계획 지문, 두 번째 화면은 BANK-OM-001 전용 경로와 공용 경로 예시를 보여 줌.
- 재구성 검사를 화면 확인 때마다 반복하지 않도록 전체 JSON을 `evidence/om-1.13.1-id-series/vendor-rebuild-result.json`에 한 번 저장하고, 이후 `jq`로 필요한 항목만 확인하도록 변경함.
- `gate.name`, `gate.verdict`, `gate.reasons`, `active_ids`, `excluded_paths`, `plan_digest`, `unique_assignments`, `shared_candidates`, `customization_id`, `candidate_ids`, `path`의 의미와 확인 기준을 추가함.
- `plan_digest`는 성공·실패 값이 아니라 경로·ID 연결 계획을 구분하는 SHA-256 지문이며, 입력 계획이 달라지면 값도 달라진다고 명시함.
- 실제 `block`의 세 reason을 조사함. 승인된 공식 1.13.1 commit은 `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9`, 현재 import official commit은 `e6199070c35f717f7ced512bb7b435b9d46b33a3`이며 두 commit의 tree는 동일하지만 ancestor 관계가 없음.
- `candidate does not descend...`와 두 `expected exactly one Customization-ID`는 서로 별개의 코드 오류가 아니라, import commit이 공식 upstream 뒤에 연결되지 않아 검사기가 중간 commit까지 커스터마이징 commit으로 읽은 같은 계보 문제임을 확인함.
- 별도 임시 복제본에서 `upstream-1.13.1-release`를 시작점으로 새 branch를 만들고 001~007 commit을 순서대로 cherry-pick한 뒤 재구성 검사를 실행함. 변경 경로 111개, 제외 파일 2개, active ID 7개가 유지되면서 verdict가 `pass`로 바뀌는 것을 확인함.
- 실제 작업 branch를 강제로 다시 쓰지 않고 `codex/om-1.13.1-id-series-upstream` 새 branch를 만드는 복구 절차를 가이드에 추가함. 기존 branch는 비교·복구용으로 보존하고, 충돌 시 자동 선택하지 않도록 `★ 핵심 운영기준`으로 표시함.

## 2026-08-06 — 재구성 검사 block 사유 구조화

- `harness/acgh/vendor_rebuild.py` 결과에 `diagnosis`를 추가하여 영어 `reasons`를 운영자가 판단할 수 있는 문제 범주로 자동 분류함.
- 분류 코드는 `git_lineage`(공식 Git 이력), `commit_identity`(commit·BANK-OM ID), `path_registration`(111개 경로·제외 경로·소유 ID), `content_mismatch`(최종 파일 내용), `analysis_input`(입력·Git object·등록파일), `other`(미분류)임.
- `diagnosis.primary_category`는 우선 해결할 대표 범주, `diagnosis.categories`는 발견된 모든 범주·원문 사유·다음 행동, `diagnosis.summary`는 한 줄 요약을 제공함.
- 현재 실제 차단 결과를 새 코드로 재실행하여 대표 원인이 `git_lineage`, 함께 표시된 범주가 `commit_identity`임을 확인함. 두 commit ID 사유는 잘못 연결된 import commit을 검사 범위로 읽은 결과이므로, 계보를 고치면 함께 해소되는 부수 사유임.
- 111개 경로 문제가 발생하면 `path_registration`, 경로는 같지만 코드 내용이 다르면 `content_mismatch`로 별도 출력되도록 구현함.
- `test_vendor_rebuild.py`에 다중 범주 분류와 pass 시 빈 차단 범주 검사를 추가함. 전체 22개 테스트가 통과함.
- 7-4 가이드의 축약 명령에 `block_summary`, `primary_block_reason`, `block_details`를 포함하고 각 코드별 발생 사례와 조치를 추가함.

## 2026-08-06 — 7-4 결과 저장 명령의 폴더 누락·block 종료 처리

- 사용자가 7-4 Python 명령만 실행했을 때 `evidence/om-1.13.1-id-series/`가 없어 셸의 출력 redirection 단계에서 Python 실행 전에 중단되는 문제를 확인함.
- `mkdir -p`, 검사 실행, 종료코드 보관, 구조화된 결과 `jq` 출력을 하나의 복사·실행 블록으로 합침.
- 검사기가 정상적으로 `block`을 판정하면 종료코드 `1`을 반환한다는 점을 명시함. 이는 JSON 생성 실패가 아니라 차단 사유를 발견했다는 뜻임.
- 종료코드 `0`·`1`·`2`·`3`과 `pass`·`block`·`approval`·`analysis_error` 대응표를 추가함.
- 7-4-2는 검사를 다시 실행하는 단계가 아니라 저장된 JSON의 핵심 결과를 나중에 재확인하는 명령으로 역할을 명확히 함.
- 수동 명령 블록도 일부만 복사하면 폴더 생성 단계를 빠뜨릴 수 있다는 사용자 피드백에 따라 `run_vendor_rebuild_check.sh` 실행 도구를 추가함.
- 새 실행 도구는 검사기 저장소 위치를 자동 탐색하고, evidence 폴더 생성, 재구성 검사, JSON 유효성 확인, 구조화된 사유 출력과 종료코드별 다음 행동을 한 번에 처리함.
- 가이드의 정본 실행 명령을 `bash harness/registrations/kb-openmetadata/run_vendor_rebuild_check.sh` 한 줄로 교체함.
- 7-4-3의 긴 `jq` 명령도 `show_vendor_rebuild_id_paths.sh BANK-OM-001` 한 줄로 교체함.
- ID별 경로 확인 도구는 입력 ID가 활성 ID인지 확인하고, 전용·공용 경로의 전체 개수와 각각 앞의 3개·2개 예시를 출력함. 결과 파일이 없으면 7-4-1 선행 실행을 안내하며 빈 결과를 만들지 않음.
- 마지막 인수만 BANK-OM-001~007로 바꾸면 모든 ID에 동일하게 사용할 수 있도록 일반화함.

## 2026-08-06 — Git 계보 차단 시 commit_identity를 부수 확인 정보로 정정

- 실제 현재 결과에서 `git_lineage`와 함께 나온 두 `commit_identity` 사유는 독립적인 commit 결함이 아니라, 잘못 연결된 import commit이 검사 범위에 포함되어 나타난 부수 정보임.
- `git_lineage`와 `commit_identity`가 함께 있을 때 `commit_identity`의 label을 `Git 이력 연결 때문에 함께 표시된 commit ID 확인 정보`로 바꾸고 `classification: secondary_observation`을 출력하도록 수정함.
- 실제 차단 원인은 `classification: blocking_cause`, 대표 원인 때문에 함께 나온 정보는 `secondary_observation`으로 구분함.
- 요약에서는 `secondary_observation`을 별도 차단 범주 수에 포함하지 않도록 수정함. 현재 요약은 `공식 commit과 Git 이력 연결 문제` 하나만 표시함.
- 계보 문제가 없는 상태에서 `Customization-ID`가 누락된 경우에는 기존처럼 `commit_identity`를 실제 `blocking_cause`로 유지하는 회귀 테스트를 추가함.
- 7-4 실행이 한 줄 스크립트로 바뀐 뒤에도 복구 절차에 구식 `--candidate` 단독 예시가 남아 있음을 사용자 피드백으로 확인함.
- 새 계보 branch 재검사 절차를 실제 7-1 log, 7-2 111개 경로, 7-3 제외 파일, 7-4 스크립트 실행 명령으로 모두 다시 작성함.
- 7-4는 `VENDOR_REBUILD_CANDIDATE=codex/om-1.13.1-id-series-upstream bash .../run_vendor_rebuild_check.sh` 형식으로 새 branch를 전달하도록 수정함.

## 2026-08-06 — 공식 Git 이력 기반 후보 branch 최종 통과 및 페이지 이동 오류 수정

- 사용자가 공식 OpenMetadata 1.13.1 commit에서 시작한 후보 branch의 재구성 검사를 완료함.
- 최종 결과는 종료코드 `0`, `verdict: pass`, `block_summary: 차단 사유가 없습니다.`, `primary_block_reason: null`, `block_details: []`임.
- `BANK-OM-001`~`007` 일곱 ID, 제외 파일 2개와 분석 계획 지문이 최종 결과에 포함된 것을 확인함.
- 최종 통과 터미널 화면을 `assets/vendor-rebuild-gate-pass-summary.png`로 추가하고 7-4-2 본문을 차단 예시가 아닌 실제 통과 결과 중심으로 수정함.
- 초기 `git_lineage` 차단 설명은 오류 재발 시 참고할 해결 이력으로 남기되, 현재 상태처럼 읽히지 않도록 과거형과 `수행 완료`로 변경함.
- 완료 기준 여섯 항목을 실제 완료 상태로 표시함.
- 앞쪽 예행연습 4개 문서의 이전·다음 링크가 Markdown 원본 `.md`를 가리켜 브라우저에 스크립트가 표시되던 문제를 확인함.
- 해당 이동 링크를 모두 렌더링 결과인 `.html`로 변경함. 다음 단계 클릭 시 문서 소스가 아니라 가이드 화면이 열림.

## 2026-08-06 — 일회성 과거 자료 정리를 일반 가이드에서 분리

- 5번 가이드의 `과거 1.13.0→1.13.1 재현 자료 보관`은 현재 사용자 로컬에만 필요한 일회성 정리 작업임을 확인함.
- 이 작업을 일반 최초 등록 절차처럼 읽지 않도록 문서 성격·단계 요약·본문 3장·완료 체크 항목에서 모두 제거함.
- 사용자가 일회성 초기화를 별도로 실행한 뒤 시작할 수 있도록 가이드 시작 조건에 `경로 기준 파일 준비 완료`를 명시함.
- 후속 장 번호를 다시 정리하여 공용 코드 정의 작성은 3장, 나머지 최초 등록 입력 작성은 4장, 입력 확인은 5장, 완료 기준은 6장이 됨.
- 다음 단계가 앞 단계에서 통과한 실제 branch를 계속 사용하도록 `upstream-1.13.1-release`와 `codex/om-1.13.1-id-series-upstream`으로 기준을 통일함.
- 실제 branch SHA는 공식 `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9`, 커스터마이징 `d952a83896940116d3d6022323ad76bfe60991e8`이며 변경 경로 111개를 확인함.
- 파일 이동 전 분석 명령을 실제 환경에서 실행하여 `READY_TO_INITIALIZE`, 등록 경로 111개, 제외 경로 2개, 공용 경로 37개, 공용 경로·ID 조합 114개를 확인함. 파일 이동은 사용자가 직접 실행하도록 남김.
- 7-4 최종 통과 캡처를 검사 대상 branch `codex/om-1.13.1-id-series-upstream`이 함께 보이는 최신 화면으로 교체함.
- 사용자 피드백에 따라 7-4-2의 캡처는 최초 `block` 화면으로 원복함. 이 위치는 최초 검사 결과와 차단 원인을 설명하는 구간임.
- 최신 `pass` 캡처는 7-4-5 맨 아래의 새 branch 재검사 결과로 이동함. 문서 흐름을 `최초 block 확인 → Git 이력 수정 → 재검사 pass` 순서로 맞춤.
- 5번 가이드의 저장소 경로·환경변수 설정은 사용자가 예행연습 전에 별도로 완료한 준비 작업이므로 본문 1장에서 제거함.
- 환경변수 설정은 실행 절차로 반복하지 않고 문서 시작 조건으로만 남김.
- 남은 장 번호를 다시 정리하여 branch 확인은 1장, 공용 코드 정의 작성은 2장, 나머지 등록 입력은 3장, 입력 확인은 4장, 완료 기준은 5장이 됨.
- 삭제된 장을 가리키던 완료 체크 항목과 `초기화` 표현을 제거하고, 작성 양식 내부 참조를 새 번호에 맞춤.
- `rev-parse codex/om-1.13.1-id-series-upstream`이 일곱 ID commit 중 어떤 값을 출력하는지 불명확하다는 피드백을 반영함.
- 출력 SHA는 일곱 commit을 합친 별도 commit이 아니라 branch 끝의 `BANK-OM-007` commit이며, parent 연결을 통해 `001`~`006`과 공식 1.13.1까지 포함한 최종 코드 상태를 식별한다고 설명함.
- 실제 확인값 `d952a83896940116d3d6022323ad76bfe60991e8`과 commit 연결 그림을 추가함.
- 일곱 commit의 개별 SHA·BANK-OM ID를 모두 확인하는 `git log --reverse` 명령과 정상 기준을 추가함.
- `그 branch의 맨 끝`도 어떤 branch인지 모호하다는 후속 피드백을 반영함.
- `codex/om-1.13.1-id-series-upstream`을 공식 1.13.1 위에 BANK-OM-001~007을 모두 적용한 `1.13.1 커스터마이징 기준검사 branch`로 명시하고, official branch·release branch와 구분함.
- `rev-parse` 결과가 이 branch에서 일곱 번째로 적용한 `BANK-OM-007` commit의 SHA임을 직접 명시함.
- 현재 페이지에서 처음 등장한 branch가 어느 단계에서 만들어졌는지 찾기 어렵다는 피드백을 반영함.
- 1-1에 `이전 4/11 페이지 7-4-5에서 공식 1.13.1을 출발점으로 만들고 재구성 검사를 통과한 branch`라고 연결 설명을 추가함.
- 1-2에서 `upstream-1.13.1-release`와 `codex/om-1.13.1-id-series-upstream` 각각의 이전 단계 역할을 한 줄씩 구분함.
- 2-2의 `definition_pairs: 114`가 파일 수처럼 읽힌다는 피드백을 반영함.
- 실제 분류표를 재계산하여 공용 파일 37개가 `ID 2개 연결 파일 16개`, `ID 3개 연결 파일 2개`, `ID 4개 연결 파일 19개`이고, `32 + 6 + 76 = 114`개 경로·ID 작성칸이 생성됨을 표로 추가함.
- `<공용-파일-경로>`가 2-2 작성 양식의 `path` 값을 넣는 자리표시자이며 꺾쇠를 입력하지 않는다고 명시함.
- 실제 YAML 항목과 `Entity.java` 경로로 치환한 완성 명령을 함께 추가함.
- 공용 파일 37개를 각각 입력해야 하는 것처럼 읽힌다는 피드백을 반영함.
- 2-2 생성 명령은 한 번만 실행하며 `shared-path-owners.yaml`을 읽어 37개 파일과 114개 파일·ID 작성칸을 모두 자동 생성한다고 명시함.
- 현재 일곱 ID commit을 대조한 결과 114개 조합 모두 해당 ID commit의 비어 있지 않은 파일 diff가 존재함을 확인함.
- 경로·ID 목록 생성과 diff 후보 수집은 자동화 가능하지만, 어떤 코드가 기능을 증명하는지는 보조 수정과 공통 코드가 섞일 수 있어 사용자 승인이 필요하다고 경계를 구분함.

## 2026-08-06 — 공용 코드 정의 초안 재실행 결과 명확화

- 사용자가 2-2 생성 명령을 이미 한 번 실행한 뒤 다시 실행하여, 정상 초안이 존재함에도 `ANALYSIS_ERROR: output already exists`가 출력되는 문제를 확인함.
- 실제 기존 `shared-code-definitions-draft.yaml`을 확인한 결과 `definitions` 114개가 모두 있고 `assertions` 114개가 비어 있는 정상 생성 직후 초안임을 확인함.
- 생성기는 기존 파일을 절대 덮어쓰지 않는 원칙을 유지하되, 현재 `shared-path-owners.yaml`의 경로·ID 조합과 기존 파일이 일치하면 `DRAFT_ALREADY_EXISTS`와 완료·잔여 작성칸 수를 출력하고 성공 종료하도록 수정함.
- 기존 파일이 손상됐거나 현재 공용 경로·ID 조합과 다를 때만 `ANALYSIS_ERROR`로 중단하도록 구분함.
- 2-2 가이드에 최초 생성 `DRAFT_WRITTEN`, 정상 재실행 `DRAFT_ALREADY_EXISTS`, 실제 불일치 `ANALYSIS_ERROR`의 의미와 다음 행동을 각각 추가함.
- 기존 작성 내용 보존과 오래된 초안 감지 테스트를 추가함.

## 2026-08-06 — 2-2 생성 후 작성 흐름 통합

- 2-2가 114개 빈 작성칸을 만든 뒤 사용자가 어느 파일을 열고 무엇을 채울지 바로 이어지지 않는 문제를 확인함.
- 기존 2-3·2-4의 diff 확인과 assertion 작성 절차를 독립 단계에서 제거하고 2-2 아래 `개별 작성칸의 diff 확인 및 assertions 작성 방법` 펼치기로 통합함.
- 사용자가 수정할 파일을 `$OM_TEST_REPO/harness/preparation-inputs/om-temp-1.13.1/shared-code-definitions-draft.yaml` 한 개로 명시하고 macOS에서 여는 명령을 추가함.
- `path`·`customization_id`는 자동 생성되며 사용자는 `assertions: []`만 실제 코드 조각 또는 JSON/YAML 값으로 채운다는 역할 구분을 표로 추가함.
- 같은 생성 명령을 다시 실행하면 기존 파일을 보존하면서 `completed_pairs`·`remaining_pairs`로 작성 진행률을 확인한다는 절차를 추가함.
- 114개 작성칸 생성은 자동으로 끝나지만 실제 코드 정의 선택은 사용자 승인 사항이므로 2-2만으로 승인까지 대체되지는 않는다고 명시함.

## 2026-08-06 — 공용 코드 assertion 필드 작성 규칙 보완

- JSON assertion 예시만 있고 `id`의 생성 주체, `matcher` 지원 값, `pointer`·`expected` 작성 규칙이 없어 사용자가 예시를 변형할 수 없는 문제를 확인함.
- 실제 `shared-code-definitions.schema.json`과 `acgh/shared_code.py`를 기준으로 현재 matcher를 `code_fragment`, `json_value`, `yaml_value` 세 가지로 한정해 설명함.
- `id`는 사용자가 정하는 검사 항목 이름이며 같은 경로·BANK-OM ID의 assertion 목록 안에서 중복할 수 없다는 규칙을 추가함.
- 각 matcher가 지원하는 확장자와 필수 필드, `fragment`·`occurrences`·`pointer`·`expected`의 작성 방법을 표로 추가함.
- JSON pointer가 `/label/query-report`를 어떻게 찾는지 실제 JSON 구조로 보여주고, 값 일치는 `PASS`, 키·값 불일치는 `BLOCK`, 형식·matcher 오류는 `ANALYSIS_ERROR`로 구분함.
- 하나의 경로·ID 조합에 assertion을 여러 개 작성할 수 있으며 모두 일치해야 통과한다는 판정 조건을 명시함.

## 2026-08-06 — 작성 파일 경로와 실제 작성 전·후 예시 보완

- `사용자가 수정할 파일은 한 개이며 37개 파일을 각각 만들지 않는다`는 부정형 설명이 핵심 관리 단위를 늦게 전달한다는 피드백을 반영함.
- 문장을 `114개 작성 항목은 다음 YAML 파일 한 개로 관리합니다`로 바꾸고 실제 작성 파일 경로와 macOS 열기 명령을 바로 배치함.
- 명료성 검토 스킬에 `관리 단위와 필요한 행동을 긍정형으로 먼저 말하고, 안전상 필요한 경우에만 부정형 금지 문장을 사용한다`는 규칙을 추가함.
- 실제 BANK-OM commit diff에서 SQL·Java·TypeScript·TSX·JSON 항목 다섯 개를 골라 작성 전 `assertions: []`와 작성 후 실제 정의를 추가함.
- 예시 제목은 `BANK-OM-001 - schemaChanges.sql`, `BANK-OM-002 - Entity.java`, `BANK-OM-003 - constants.ts`, `BANK-OM-003 - AuthenticatedAppRouter.tsx`, `BANK-OM-004 - en-us.json` 형식으로 통일함.

## 2026-08-06 — diff 결과 해석과 공용 파일의 ID 구분 위치 수정

- `diff가 빈 출력인 경우` 안내가 다섯 작성 예시 뒤에 있어 어떤 명령의 결과인지 늦게 연결되는 문제를 확인함.
- 빈 출력 해석과 중단 행동을 공용 파일 diff 명령 바로 아래로 이동함.
- `한 파일에서 여러 ID 코드가 함께 보이는 경우`라는 문장이 발생 이유를 설명하지 않아 불필요한 경고처럼 읽히는 문제를 수정함.
- 공식 1.13.1과 최종 커스터마이징 branch를 비교하면 같은 공용 파일에 들어간 여러 BANK-OM ID 변경이 하나의 diff에 함께 보인다는 원인을 먼저 설명함.
- 실제 `Entity.java`의 `BANK-OM-001 / INSTANCE_CODE`, `BANK-OM-002 / QUERY_REPORT` 관계와 두 ID별 commit을 따로 확인하는 실제 `git show` 명령을 추가함.

## 2026-08-06 — assertion 자동 제안·최종 코드 검산과 사람 승인 연결

- 공용 파일의 다중 ID 설명이 오류 경고처럼 읽힌다는 피드백에 따라 해당 참고 문단·표·개별 `git show` 예시를 본문에서 제거함.
- 빈 작성 양식 생성기와 assertion 자동 제안기를 분리함. `generate_shared_code_definition_draft.py`는 114개 경로·ID 빈 작성칸과 `completed_pairs`·`remaining_pairs`만 관리함.
- `propose_shared_code_definitions.py`를 추가함. 각 `Customization-ID` commit의 실제 diff를 읽어 JSON/YAML의 변경값과 Java·TypeScript·TSX·SQL의 연속 추가 코드 블록을 자동 제안함.
- 자동 추출은 첫 번째 추가 줄을 임의 선택하지 않음. 주석·공백만 있는 변경을 제외하고, 이후 commit 때문에 바뀌거나 사라져 최종 커스텀 branch에서 검출되지 않는 정의도 채택하지 않음.
- 한 줄 실행 도구 `harness/registrations/om-temp-1.13.1/propose_shared_code_definitions.sh`를 추가함. 빈 양식을 입력으로 읽고 `shared-code-definitions-proposed.yaml`을 별도로 생성함.
- 실제 `upstream-1.13.1-release → codex/om-1.13.1-id-series-upstream` 범위에서 실행한 결과 114개 경로·ID 조합, assertion 790개가 생성됐고 최종 branch 검산이 `PASS`함.
- matcher별 실제 생성 수는 `code_fragment` 53개, `json_value` 737개이며 빈 definition은 0개임.
- 같은 명령 재실행 시 기존 제안이 현재 branch에서도 유효하면 `PROPOSAL_ALREADY_EXISTS`와 `PASS`를 출력하고 파일을 덮어쓰지 않도록 구현함.
- 사람 승인은 자동검증 `PASS`만 보고 끝내지 않음. 이전 4/11 페이지에서 승인한 일곱 ID commit SHA, 114개 경로·ID 조합, 제안 내용의 ID 귀속을 확인한 뒤 등록 초안 폴더에 복사함.
- 등록 초안 복사는 정식 승인 완료가 아님을 명시함. 이후 7/11 페이지의 `plan`이 주요 등록자료 전체 digest를 만들고, 사용자가 `registration-approval.yaml`에 승인자·시각·근거를 작성하며, `apply`가 같은 digest인지 확인해야 정식 승인이 완료됨.
- 관련 단위 test 16개와 실제 114개 정의 검사기 실행을 통과함.

## 2026-08-06 — 최초 등록 필수 입력 자동 차단

- 최초 등록 입력에서 담당자가 `UNASSIGNED`이거나 `owner_status`가 `assigned`가 아닌데도 승인 가능한 proposal이 만들어지던 문제를 수정함.
- 빈 필수 경로, 미완성 Contract, 알 수 없는 선행 ID, 자기 자신 의존, 순환 의존도 plan 단계에서 중단하도록 검증을 추가함.
- 의미상 미완성 입력은 `BLOCKED` proposal과 수정 항목을 남기고, YAML 구조·빈 필수 목록처럼 분석 자체가 불가능한 입력은 `ANALYSIS_ERROR`로 구분함.
- 차단된 proposal은 승인 양식을 만들거나 `apply`할 수 없으며 `PROPOSAL_NOT_APPLY_READY`와 종료코드 `1`을 반환함.
- `summary.md`에 ID별 담당자·담당자 상태·중요도·선행 ID와 반드시 수정할 항목·다음 행동을 표시함.
- 실제 1.13.1 입력으로 실행하여 7개 ID의 `OWNER_NOT_ASSIGNED`가 각각 표시되고 plan이 차단되는 것을 확인함.
- 5/11 가이드에 입력 완료 기준, `BLOCKED`·`PROPOSAL_WRITTEN`·`ANALYSIS_ERROR`별 예시와 재실행 방법을 추가함.
- 7/11 가이드에서 빈 증거 폴더를 먼저 만드는 절차를 제거하고, 앞 페이지가 만든 `summary.md`를 확인한 뒤에만 승인하도록 수정함.
- 실행 경로는 `PLAN_DIR`과 `BASELINE_DIR`로 통일하여 `<실행ID>` 자리표시자를 여러 명령에 반복 입력하지 않도록 개선함.
- 관련 최초 등록·워크플로 test 20개와 실제 차단 proposal의 승인 양식 재차단을 통과함.

## 2026-08-06 · 7/11 가이드 경로 설정 오류 정정

- `OM_TEMP_1.13.1_등록승인_apply_및_기준검사_가이드.md/html`의 `공통 경로 설정` 절을 제거함.
- 7단계는 이전 단계와 같은 터미널의 `OM_TEST_REPO`·`OM_CODE_REPO`를 이어 사용하며, 경로를 다시 설정하지 않고 두 값을 확인한 뒤 진행하도록 수정함.
- 이 단계에서 사용하지 않는 `KB_SOURCE_REPO` 설명과 복사해 실행할 수 없는 `<검사기-저장소-clone-경로>` 명령을 삭제함.
- 등록자료의 `shared-path-owners.yaml`도 7개 BANK-OM commit의 실제 변경 경로와 다시 대조함. 실제·선언 모두 공용 경로 37개·경로-ID 조합 114개였고, 누락·추가·ID 불일치는 0개였음.
- `20260806-02` proposal의 `proposed-registration/shared-path-owners.yaml`과 현재 등록 폴더의 파일은 내용과 SHA-256이 같음.
- 7/11 가이드에 과거 기준 SHA `dee330eb…`가 현재 정상값처럼 남아 있던 오류를 수정함. 현재 branch·`20260806-01`·`20260806-02` proposal의 기준은 모두 `d952a83896940116d3d6022323ad76bfe60991e8`임.
- 제안서 SHA 필드 설명을 실제 `proposal.yaml`과 다른 `custom_head_sha`에서 `custom_sha`로 정정함.
- 7/11 가이드의 `git status --short`가 검사기 저장소 전체 변경을 보여 이번 등록 변경과 관계없는 문서·코드 변경까지 섞이던 문제를 수정함. `harness/registrations/om-temp-1.13.1`만 확인하도록 경로를 제한함.
- `status --short`의 빈 출력·`M`·`??`·`D` 해석, `git diff`의 `+`·`-` 해석, 새 파일은 `git diff`에 보이지 않는 주의사항과 출력 발생 시 재승인 절차를 추가함.

## 2026-08-06 · 최초 등록 승인서 오류 한국어 진단

- `bootstrap-apply`의 승인서 오류가 영어 `message`만 반환하던 문제를 수정함.
- 기존 `status`·`message`를 유지하고 `code`·`field`·`current_value`·`message_ko`·`next_action`·`file`을 추가하여 자동화 호환성과 사용자 해석을 모두 유지함.
- 승인자·승인 시각·승인 근거 자리표시자, 승인서 스키마 오류, proposal 검토 항목 누락·추가를 서로 다른 오류 코드로 구분함.
- 승인 시각은 문자열 여부만 보지 않고 RFC 3339 형식과 timezone 포함 여부를 실제로 검증하도록 보완함.
- 승인서 자리표시자·복수 스키마 오류·검토 항목 누락 test를 추가하고 관련 test 25개가 통과함.
- 복수 오류를 한 번에 수정할 수 있도록 최상위 `APPROVAL_INPUT_INVALID`와 `issues` 목록을 추가함.
- 실제 `20260806-02` 승인서로 `om_workflow.py bootstrap-apply`를 재실행하여 `approved_by`·`approved_at`·`decisions[0].reason`의 문제 필드·현재 값·한국어 원인·수정 방법·파일 경로가 함께 출력되는 것을 확인함.

## 2026-08-06 · 등록 검사 결과 폴더 자동 생성

- `om_workflow.py validate --output <새 폴더>/registration-validation-results.json` 실행 시 상위 폴더가 없으면 검사 판정 출력 뒤 `FileNotFoundError`가 발생하던 문제를 수정함.
- 워크플로와 공용 등록자료 검사기가 결과 파일의 상위 폴더를 자동 생성하도록 보완함.
- 중첩된 새 결과 경로 생성 회귀 test를 추가했으며 관련 test 9개가 통과함.
- 실제 `20260806-02` 기준 검사로 재실행하여 종료코드 `0`, 다섯 검사 `pass`, 결과 JSON 저장을 확인함.
