# OM_TEMP 1.13.2 공식 코드 준비 및 병합 전 영향 검사 가이드

**전체 순서:** 8/11 · [전체 목차](./OM_TEMP_1.13.1_1.13.2_예행연습_전체목차.html)

> 시작 조건: 1.13.1 등록자료와 기준 검사가 승인돼 있어야 합니다.  
> 종료점: 사용자가 승인한 실제 공식 tag·commit으로 `official/om-1.13.2`를 만들고, T42·위험 검사 결과를 보관합니다.  
> 이 문서에서 하지 않는 일: custom branch 병합, 충돌 해결, Manifest 자동 변경.

**문서 이동:** [← 이전 — 1.13.1 등록 승인·기준 검사](./OM_TEMP_1.13.1_등록승인_apply_및_기준검사_가이드.html) · [다음 — 1.13.2 vendor merge·충돌 해결 →](./OM_TEMP_1.13.2_vendor_merge_및_충돌해결_가이드.html)

## 공통 경로 설정

이 페이지의 명령을 실행할 터미널에서 검사기 저장소로 이동한 뒤 공통 경로를 불러옵니다. 다른 컴퓨터에서는 clone 위치만 바꾸면 됩니다.

```bash
cd <검사기-저장소-clone-경로>
```

```bash
source harness/rehearsal_env.sh
```

`OM_TEST_REPO`는 검사기 저장소, `OM_CODE_REPO`는 OpenMetadata 코드 작업 폴더, `KB_SOURCE_REPO`는 실제 커스터마이징 원본 폴더를 가리킵니다. 새 터미널을 열면 다시 실행합니다.

## 1. 검사 대상과 비교 방향

이 단계는 `official/om-1.13.1`과 **새 공식 OpenMetadata tag**를 비교합니다. `custom/om-1.13.1`을 비교하는 검사가 아닙니다. 목적은 병합 전에 새 공식 버전이 BANK-OM 감시 경로를 바꿨는지 미리 찾는 것입니다.

```text
이전 공식 코드 official/om-1.13.1
              ↕ T42 공식 코드 차이 비교
새 공식 코드 official/om-1.13.2
              ↓
영향받을 BANK-OM ID·경로 목록
```

> **\*참고 — `upgrade_watch.paths`**는 새 공식 버전에서 바뀌면 해당 BANK-OM ID를 다시 검토할 경로입니다. 경로가 겹치면 “충돌 확정”이 아니라 `APPROVAL`, 즉 병합 전에 담당자가 diff를 검토해야 한다는 뜻입니다.

## 2. 실행 전 준비파일

아래 파일은 7번 페이지에서 승인·반영한 **1.13.1 등록자료**입니다. 이 페이지가 새 파일을 만드는 것이 아니라, 새 공식 1.13.2가 기존 BANK-OM에 줄 영향을 계산할 입력으로 읽습니다.

| 입력 | 이전 단계에서 온 값 | 이 단계의 사용 |
|---|---|---|
| Registry `source.upstream_sha` | 승인된 1.13.1 공식 commit | T42 비교 시작점 |
| Manifest `upgrade_watch.paths` | ID별 감시 경로 | 공식 변경 경로와 교집합 계산 |
| `repository-layout.yaml` | 경로 분류 기준 | 새 공식 모듈이 분류되는지 T93 확인 |
| `sensitive-zones.yaml` | 중요 경로 정책 | 인증·DB 등 영향 분류 |
| `change-intent.yaml` | 승인된 변경 목적 | 위험 검사에서 의도와 실제 경로 대조 |
| `debt-thresholds.yaml` | 유지 부담 상한 | T43에서 코어 수정·충돌률 판단 |

## 3. 실제 공식 tag 존재 확인

### 3-1. 공식 원격 저장소 확인

```bash
git -C "$OM_CODE_REPO" remote get-url upstream
```

정상 출력은 `https://github.com/open-metadata/OpenMetadata.git`입니다. `upstream`이 없을 때만 다음 명령으로 등록합니다.

```bash
git -C "$OM_CODE_REPO" remote add upstream https://github.com/open-metadata/OpenMetadata.git
```

### 3-2. tag 목록 갱신

```bash
git -C "$OM_CODE_REPO" fetch upstream --tags
```

```bash
git -C "$OM_CODE_REPO" rev-parse refs/tags/1.13.2-release^{commit}
```

**정상 결과:** 40자리 commit SHA. 이 값을 `<공식-1.13.2-SHA>`로 기록합니다.

> **중단 — tag가 없을 때:** `unknown revision`이면 임의의 main commit을 1.13.2라고 부르지 않습니다. 사용자가 실제 target tag 또는 commit을 승인할 때까지 이 페이지에서 중단합니다. 2026-08-05 현재 로컬 저장소에는 1.13.2 tag가 없으므로 fetch 후 반드시 다시 확인해야 합니다.

## 4. official branch 생성

### 4-1. 공식 코드와 동일한 tree인지 확인

```bash
git -C "$OM_CODE_REPO" show --no-patch --format='%H %T %s' <공식-1.13.2-SHA>
```

출력의 commit SHA·tree SHA·제목을 실행 기록에 보관합니다.

### 4-2. 공식 branch 생성

```bash
git -C "$OM_CODE_REPO" branch official/om-1.13.2 <공식-1.13.2-SHA>
```

같은 branch가 이미 있으면 다음 명령으로 실제 tag와 같은지 확인합니다.

```bash
git -C "$OM_CODE_REPO" rev-parse official/om-1.13.2 refs/tags/1.13.2-release^{commit}
```

두 줄이 다르면 branch를 임의로 덮어쓰지 않고 작성자와 변경 사유를 확인합니다.

## 5. T42 공식 변경 영향 검사

검사기 저장소에서 실행합니다.

`<실행ID>`는 이번 “공식 1.13.2 병합 전 검사” 한 번의 결과를 묶는 값입니다. 예: `20260805-premerge-01`. T42와 6장의 위험 검사에는 같은 값을 사용하고, 입력을 고쳐 다시 검사하면 `...-02`처럼 새 값을 사용합니다.

```bash
mkdir -p evidence/om-1.13.2-premerge-<실행ID>
```

**산출물:** T42와 위험 검사 결과를 함께 보관할 폴더. 같은 입력으로 수행하는 5·6장 명령에는 같은 실행 ID를 사용합니다.

```bash
cd "$OM_TEST_REPO"
```

```bash
./.venv/bin/python harness/om_workflow.py watch \
  --repo "$OM_CODE_REPO" \
  --version 1.13.1 \
  --base official/om-1.13.1 \
  --target official/om-1.13.2 \
  --output evidence/om-1.13.2-premerge-<실행ID>/upgrade-watch-results.json
```

**입력:** 두 official branch와 1.13.1 Manifest. **산출물:** ID별 변경 감시 경로·설정 키·dependency 목록. **다음 사용:** vendor merge 전 검토표와 충돌 예상 범위.

:::details T42 결과 예시와 발생 조건

**변경 경로가 겹치지 않은 경우**

```json
{"gate":{"verdict":"pass","reasons":[]},"affected_customizations":[]}
```

공식 1.13.2 변경 경로와 모든 Manifest의 `upgrade_watch.paths`가 겹치지 않을 때 나옵니다.

**담당자 검토가 필요한 경우**

```json
{"gate":{"verdict":"approval","reasons":["BANK-OM-002: watched path changed"]},"affected_customizations":[{"customization_id":"BANK-OM-002","changed_watch_paths":[".../CollectionDAO.java"]}]}
```

겹치는 경로가 있다는 뜻이며 Git 충돌이나 기능 고장이 확정됐다는 뜻은 아닙니다. 해당 공식 diff를 보고 병합 후 무엇을 재검사할지 기록합니다.

**분석하지 못한 경우**

```text
Traceback ... required Git object or Manifest input could not be read
```

공식 commit을 아직 받지 않았거나 Manifest를 읽을 수 없을 때 발생합니다. 현재 T42 실행기는 이 경우 `analysis_error` JSON을 만들지 못하고 명령 자체가 실패할 수 있습니다. 승인으로 넘기지 말고 터미널 오류를 보관한 뒤 입력을 복구합니다.

:::

| 결과 파일의 verdict | 뜻 | 다음 행동 |
|---|---|---|
| `pass` | 등록한 watch 범위와 공식 변경이 겹치지 않음 | 다른 사전 검사 계속 |
| `approval` | 하나 이상의 BANK-OM ID 감시 범위가 바뀜 | ID·경로·공식 diff를 사용자 검토표로 확정 |

T42는 `approval`이 정상적으로 발생할 수 있습니다. 승인 없이 자동 통과로 바꾸지 않습니다. **현재 `watch` 명령은 verdict와 관계없이 정상 실행이면 종료코드 0을 반환하므로, 종료코드만 보지 말고 JSON의 `gate.verdict`를 반드시 읽습니다.** 명령 자체가 실패하면 결과 파일이 없거나 불완전할 수 있습니다.

## 6. T93·T41·T43·구조화 diff 위험 검사

`<최근-승인-충돌률>`은 이전 업그레이드 기록에서 승인한 0~1 사이 값입니다. 기록이 없으면 `0`으로 추정하지 않고 사용자가 “기준 없음” 처리 방식을 먼저 결정합니다.

여기서 `--candidate`는 **새 1.13.2 업그레이드 후보가 아니라 현재 승인된 1.13.1 커스텀 기준 코드**입니다. 새 공식 변경량과 현재 BANK-OM 변경량을 함께 보아 병합 전 위험을 계산하기 위해 사용합니다.

```bash
./.venv/bin/python harness/om_workflow.py risk \
  --repo "$OM_CODE_REPO" \
  --version 1.13.1 \
  --base official/om-1.13.1 \
  --target official/om-1.13.2 \
  --candidate codex/om-1.13.1-registration-baseline \
  --conflict-rate <최근-승인-충돌률> \
  --output evidence/om-1.13.2-premerge-<실행ID>/upgrade-risk-results.json
```

| 검사 | 확인 내용 | 결과 활용 |
|---|---|---|
| T93 | 기존 경로 규칙이 새 공식 tree에서도 실제 파일을 찾는가 | 미분류 새 모듈은 `ANALYSIS_ERROR` |
| T41 | 중요 경로 변경이 승인된 의도와 일치하는가 | 근거 없으면 `BLOCK`·`APPROVAL` |
| T43 | 코어 수정량·충돌률이 정책 상한 안인가 | 상한 초과 원인을 병합 계획에 반영 |
| T51·T52 | JSON·YAML·schema·dependency 구조가 어떻게 바뀌었는가 | 담당자가 실제 값·타입 변화를 검토 |

:::details 위험 검사 결과가 달라지는 대표 경우

| 결과 | 발생 예 | 조치 |
|---|---|---|
| `pass` | 새 공식 모듈도 기존 경로 규칙으로 분류되고, 중요 경로 변경이 승인 의도 안이며 유지 부담 상한 이내 | 결과의 입력 commit을 확인하고 병합 계획 작성 |
| `approval` | 중요 경로 변경은 있으나 자동으로 오류라고 단정할 수 없음 | 경로·의도·담당자 근거를 기록 |
| `block` | 금지 경로 변경 또는 승인한 유지 부담 상한 초과 | 코드 범위나 정책 예외를 결정한 뒤 재실행 |
| `analysis_error` | 새 공식 tree를 분류하지 못하거나 필수 `change-intent.yaml`을 읽지 못함 | 등록자료·Git 입력을 복구한 뒤 재실행 |

:::

## 7. 사용자 검토표

| BANK-OM ID | 바뀐 공식 경로 | 공식 변경 요약 | 병합 전 결정 |
|---|---|---|---|
| 예: `BANK-OM-002` | `CollectionDAO.java` | 공식 method signature 변경 | 병합 후 QueryReport 구현과 함께 보존 |

검사 결과의 모든 affected ID를 표에 한 행씩 옮깁니다. “영향 없음”은 결과에 ID가 없을 때만 기록합니다.

## 8. 완료 기준

- 실제 공식 tag와 40자리 commit SHA를 확인했습니다.
- `official/om-1.13.2`가 해당 tag commit을 정확히 가리킵니다.
- T42 결과의 affected ID·경로를 사용자가 검토했습니다.
- T93·T41·T43·구조화 diff의 block·approval·analysis error를 숨기지 않았습니다.
- 모든 결과가 `evidence/om-1.13.2-premerge-<실행ID>/`에 있습니다.

> **중단 조건:** 공식 target이 확정되지 않았거나 T93가 새 tree를 분석하지 못하면 vendor merge를 시작하지 않습니다.

**문서 이동:** [← 이전 — 1.13.1 등록 승인·기준 검사](./OM_TEMP_1.13.1_등록승인_apply_및_기준검사_가이드.html) · [다음 — 1.13.2 vendor merge·충돌 해결 →](./OM_TEMP_1.13.2_vendor_merge_및_충돌해결_가이드.html)
