# OM_TEMP 1.13.2 vendor merge 및 충돌 해결 가이드

**전체 순서:** 9/11 · [전체 목차](./OM_TEMP_1.13.1_1.13.2_예행연습_전체목차.html)

> 시작 조건: `official/om-1.13.2`와 병합 전 영향 검토표가 승인돼 있어야 합니다.  
> 종료점: 직전 커스텀 코드와 새 공식 코드가 함께 있는 하나의 **1.13.2 업그레이드 후보 commit**을 만듭니다.  
> 이 문서에서 하지 않는 일: 업무 충돌의 자동 선택, 최종 배포 승인, release branch 생성.

**문서 이동:** [← 이전 — 공식 1.13.2 준비·사전 영향 검사](./OM_TEMP_1.13.2_공식코드_준비_및_사전영향검사_가이드.html) · [다음 — 1.13.2 최종 검사·승인 →](./OM_TEMP_1.13.2_최종검사_및_승인_가이드.html)

## 공통 경로 설정

이 페이지의 명령을 실행할 터미널에서 검사기 저장소로 이동한 뒤 공통 경로를 불러옵니다. 다른 컴퓨터에서는 clone 위치만 바꾸면 됩니다.

```bash
cd <검사기-저장소-clone-경로>
```

```bash
source harness/rehearsal_env.sh
```

`OM_TEST_REPO`는 검사기 저장소, `OM_CODE_REPO`는 OpenMetadata 코드 작업 폴더, `KB_SOURCE_REPO`는 실제 커스터마이징 원본 폴더를 가리킵니다. 새 터미널을 열면 다시 실행합니다.

## 1. vendor merge의 의미

`vendor merge`는 직전 custom branch의 전체 이력을 유지한 상태에서 새 공식 OpenMetadata branch를 Git merge하는 이 프로젝트의 기본 통합 방식입니다.

```text
custom/om-1.13.1 ───────────────┐
                                ├─ codex/om-1.13.2-merge-candidate
official/om-1.13.2 ─────────────┘
                      ↑ 같은 코드 구간이면 Git 충돌 가능
```

> **\*참고 — Git 충돌**은 Git이 같은 코드 구간을 자동 결합하지 못했다는 뜻입니다. 어떤 업무 코드가 맞는지는 검사기가 결정하지 않습니다. 담당자가 공식 변경과 BANK-OM 기능을 모두 확인해 해결합니다.

> **\*참고 — JSON 충돌 보조 도구**는 양쪽이 서로 다른 JSON key를 바꾼 경우만 합칩니다. 같은 key를 양쪽이 바꿨거나 JSON이 아닌 파일은 중단하고 사람이 결정하도록 남깁니다.

## 2. 실행 전 확인

이번 merge 시도를 구분할 `<실행ID>`를 정합니다. 예: `20260805-merge-01`. 충돌을 고치고 merge를 처음부터 다시 시도하면 `...-02`처럼 새 ID로 결과를 분리합니다.

```bash
mkdir -p "$OM_TEST_REPO"/evidence/om-1.13.2-merge-<실행ID>
```

이 폴더에는 충돌 파일 목록, 해결 근거, merge 후 공용 코드 검사 결과를 보관합니다.

### 2-1. OpenMetadata 코드 작업 폴더

```bash
git -C "$OM_CODE_REPO" status --short
```

빈 출력이 아니면 merge를 시작하지 않습니다.

### 2-2. 입력 commit 기록

```bash
git -C "$OM_CODE_REPO" rev-parse codex/om-1.13.1-registration-baseline
```

```bash
git -C "$OM_CODE_REPO" rev-parse official/om-1.13.2
```

첫 번째는 직전 커스텀 기준 commit, 두 번째는 새 공식 commit입니다. 두 값을 merge 증거의 입력으로 보관합니다.

## 3. 1.13.2 업그레이드 후보 branch 생성과 merge

### 3-1. 직전 커스텀 기준에서 시작

```bash
git -C "$OM_CODE_REPO" switch codex/om-1.13.1-registration-baseline
```

```bash
git -C "$OM_CODE_REPO" switch -c codex/om-1.13.2-merge-candidate
```

### 3-2. 새 공식 코드 merge

```bash
git -C "$OM_CODE_REPO" merge --no-ff official/om-1.13.2 \
  -m "vendor merge OpenMetadata 1.13.2 into BANK-OM custom baseline"
```

| Git 결과 | 뜻 | 다음 행동 |
|---|---|---|
| merge commit 생성 | Git이 모든 파일을 자동 결합 | 5장 검증으로 이동 |
| `CONFLICT` 후 중단 | 하나 이상의 파일을 자동 결합하지 못함 | 4장에서 경로별 해결 |
| `unrelated histories` | official·custom Git 계보가 연결되지 않음 | `--allow-unrelated-histories`를 임의 사용하지 말고 기준 branch 구성부터 재검토 |

:::details Git 결과별 실제 화면 예시

**자동 병합 완료**

```text
Merge made by the 'ort' strategy.
```

이 경우 merge commit이 이미 만들어졌으므로 5장의 `git commit`은 실행하지 않습니다.

**충돌로 중단**

```text
CONFLICT (content): Merge conflict in openmetadata-ui/.../ko-kr.json
Automatic merge failed; fix conflicts and then commit the result.
```

4장에서 모든 충돌 파일을 해결한 뒤 merge commit을 완료합니다.

**Git 계보가 연결되지 않음**

```text
fatal: refusing to merge unrelated histories
```

공식 branch를 잘못 만든 경우일 수 있으므로 강제 옵션을 붙이지 않고 2-2 입력 commit부터 확인합니다.

:::

## 4. 충돌 확인과 해결

### 4-1. 충돌 파일 목록

```bash
git -C "$OM_CODE_REPO" diff --name-only --diff-filter=U
```

이 출력이 충돌 파일의 전체 목록입니다. 화면에 보이는 첫 파일만 해결하고 끝내지 않습니다.

### 4-2. BASE·OURS·THEIRS 확인

```bash
git -C "$OM_CODE_REPO" ls-files -u
```

| Git stage | 이 merge 방향에서의 의미 |
|---|---|
| stage 1 `BASE` | 두 branch가 갈라지기 전 공통 코드 |
| stage 2 `OURS` | 현재 checkout한 직전 BANK-OM custom 코드 |
| stage 3 `THEIRS` | 지금 merge하는 새 공식 1.13.2 코드 |

stage 번호의 공식/BANK-OM 대응은 merge 방향이 바뀌면 달라집니다. 이 문서의 명령 순서에서만 위 표와 같습니다.

### 4-3. JSON 보조 도구 실행

검사기 저장소에서 실행합니다.

```bash
cd "$OM_TEST_REPO"
```

```bash
./.venv/bin/python harness/om_workflow.py resolve-json \
  --repo "$OM_CODE_REPO"
```

| 결과 | 의미 | 사용자 행동 |
|---|---|---|
| 처리 파일·key 수 출력 | 겹치지 않는 JSON key만 작업 폴더에 결합 | diff 확인 후 `git add` |
| `block` | 같은 key 변경 또는 비 JSON 충돌 | 공식·BANK-OM 의도를 보고 직접 해결 |
| `analysis_error` | Git stage나 JSON을 읽지 못함 | 파일·Git 상태 복구 후 재실행 |

보조 도구 결과가 성공이어도 자동 승인된 것이 아닙니다. 공식 key가 유지되고 BANK-OM key가 추가됐는지 실제 diff를 확인합니다.

:::details JSON 보조 도구가 처리하는 경우와 중단하는 경우

| BASE와 비교한 변경 | 결과 |
|---|---|
| 공식은 `/label/a`, BANK-OM은 `/label/b` 변경 | 두 leaf 경로가 달라 자동 결합 후 파일에 기록 |
| 공식과 BANK-OM 모두 `/label/a` 변경 | 같은 leaf 경로이므로 중단; 사람이 최종 값을 결정 |
| 충돌 목록에 Java·TypeScript 등 비 JSON 파일 포함 | 전체 실행 중단; 해당 파일은 사람이 해결 |
| JSON 문법 오류 또는 Git stage 1·2·3 누락 | 분석 오류로 중단; 파일을 쓰지 않음 |

성공 출력 예: `resolved .../ko-kr.json: BANK-OM leaf changes=9`. 이 숫자는 합친 BANK-OM leaf 변경 수이며 “기능 검사 9개 통과”라는 뜻이 아닙니다.

:::

### 4-4. 파일별 해결과 stage

```bash
git -C "$OM_CODE_REPO" diff -- <충돌-파일-경로>
```

공식 1.13.2 변경과 해당 BANK-OM ID의 승인된 코드 정의를 함께 보존하도록 수정합니다.

```bash
git -C "$OM_CODE_REPO" add <해결한-파일-경로>
```

모든 파일을 해결한 뒤 다음 명령의 출력이 비어야 합니다.

```bash
git -C "$OM_CODE_REPO" diff --name-only --diff-filter=U
```

### 4-5. 충돌 해결 근거 보관

각 파일에 다음 항목을 기록합니다.

| 항목 | 예시 |
|---|---|
| 경로 | `openmetadata-ui/.../ko-kr.json` |
| 관련 BANK-OM ID | `BANK-OM-001`, `BANK-OM-002` |
| 공식 변경 | 공식 1.13.2에서 기존 label 구조 변경 |
| BANK-OM 변경 | `instance-code`, `query-report` label 유지 |
| 해결 내용 | 공식 JSON 기준에 두 BANK-OM key를 추가 |
| 승인자·시각 | 실제 사용자 승인 정보 |

## 5. merge commit 완료

충돌이 있었던 경우에만 모든 해결 파일을 stage한 뒤 실행합니다.

```bash
git -C "$OM_CODE_REPO" commit
```

```bash
git -C "$OM_CODE_REPO" rev-parse HEAD
```

출력된 SHA가 이후 모든 검사의 `<1.13.2-업그레이드-후보-SHA>`입니다.

## 6. merge 직후 최소 검사

### 6-1. 두 입력 계보가 모두 포함됐는지 확인

```bash
git -C "$OM_CODE_REPO" merge-base --is-ancestor official/om-1.13.2 HEAD
```

```bash
git -C "$OM_CODE_REPO" merge-base --is-ancestor codex/om-1.13.1-registration-baseline HEAD
```

두 명령 모두 출력 없이 종료코드 0이어야 합니다.

### 6-2. 공용 파일 ID별 코드 정의 재검사

```bash
cd "$OM_TEST_REPO"
```

```bash
PYTHONPATH=harness ./.venv/bin/python -m acgh.shared_code \
  --repo "$OM_CODE_REPO" \
  --candidate codex/om-1.13.2-merge-candidate \
  --owners harness/registrations/om-temp-1.13.1/shared-path-owners.yaml \
  --definitions harness/registrations/om-temp-1.13.1/shared-code-definitions.yaml \
  --output evidence/om-1.13.2-merge-<실행ID>/shared-code-results.json
```

이 검사는 **아직 1.13.1에서 승인한 정의**를 사용해 merge 직후 명백한 누락을 빠르게 찾습니다. 1.13.2에서 코드 구조가 정당하게 바뀌어 BLOCK이 나올 수도 있습니다. 이 경우 통과시키기 위해 정의를 임의 수정하지 않고, 다음 페이지의 1.13.2 등록 변경안에 새 정의와 근거를 포함해 사용자 승인을 받습니다.

## 7. 완료 기준

- 1.13.2 업그레이드 후보 branch가 직전 custom 기준과 공식 1.13.2를 모두 Git 이력에 포함합니다.
- 미해결 충돌 파일이 0개입니다.
- 충돌 파일마다 관련 ID·선택 이유·승인 근거가 있습니다.
- 공용 파일 코드 정의 누락이 없거나, 누락 원인을 BLOCK으로 보관했습니다.
- 1.13.2 업그레이드 후보 SHA를 다음 페이지 입력으로 기록했습니다.

> **중단 조건:** 업무 의미를 판단할 수 없는 충돌, 공용 코드 정의 누락, 계보 검사 실패가 하나라도 있으면 최종 검사 페이지로 이동하지 않습니다.

**문서 이동:** [← 이전 — 공식 1.13.2 준비·사전 영향 검사](./OM_TEMP_1.13.2_공식코드_준비_및_사전영향검사_가이드.html) · [다음 — 1.13.2 최종 검사·승인 →](./OM_TEMP_1.13.2_최종검사_및_승인_가이드.html)
