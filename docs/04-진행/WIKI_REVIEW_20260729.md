# OM_TEMP 커스터마이징 검사 운영 위키 — 독립 검토 결과

> 검토 대상: `OM_TEMP_operations_wiki_Claude_review_20260729.html` (587KB · 2,705줄)
> 대조 기준: `easyseop/openmetadata-test` @ `codex/strict-manifest-gates` `dfc43f1` ·
> `easyseop/OM_TEMP` @ `patch/om-1.13.0` `2f4f3560` / `custom/om-1.13.0` `7d19c895`
> 검토일: 2026-07-29 · 방법: HTML 정적 분석 + 저장소 코드·스키마·등록파일 대조
> 아티팩트: <https://claude.ai/code/artifact/4dacaa5d-8d17-4358-a39a-76f931ef1302>

## 0. 결론 먼저

위키의 구조·서술 품질·정직성은 높습니다. 특히 **Git 충돌 설명(요구사항 8)은 이전 판의
사실 오류가 전부 교정**됐습니다. 그러나 **Manifest 스키마를 실제 코드와 다르게
가르치고 있어**, 신입사원이 위키대로 작성한 Manifest는 검증기에서 즉시 거부됩니다.
이 한 건이 다른 모든 장점보다 우선 수정 대상입니다.

| 우선순위 | 건수 | 항목 |
|---|---:|---|
| 치명적 | 5 | F1 Manifest 스키마 불일치 · F2 폐기 선언 필드의 코드 잔존 · F8 미실행 T90의 “12개 pass” · **F15 상태 칩이 항상 초록(거짓 통과)** · **F16 정반대를 지시하는 중복 페이지** |
| 높음 | 5 | F3 상대경로 자산 35건 · F7 1.13.1 브랜치 원격 부재 · F9 T25-R 명령 결함 · F10 실행기 이식 공백 · F11 도식에 T42 누락 |
| 중간 | 6 | F4 `NOT APPLICABLE` · F5 없는 문서 링크 · F12 완료·상신·보존 조건 · F13 111 축 미표기 · F14 BLOCK 예시 0건 · F17 장 순서·규격서 노출·빈 페이지·대비 |
| 낮음 | 1 | F6 보고용 그림의 스타일 체계 |
| 문제 없음 | 10+ | 아래 §5 · F17 하단 (JSON 도구 안전문구는 요구 수준 초과 충족, 금지 은유 0건) |

> **가장 먼저 볼 3건**: **F15**(미실행 검사가 초록 PASS로 보임) · **F1/F2**(위키대로 쓰면 검증 거부) · **F16**(구 페이지가 소스 전용 검사 흐름을 중단시키는 지시).

> **오탐 1건 배제**: 심층 검토에서 “111이 전체 diff이므로 723개 미등록 경로가
> 은폐됐다”는 지적이 나왔으나, 111(공식↔행내)과 834(공식 1.13.0→1.13.1)는 **비교 축이
> 달라** 사실이 아닙니다. 대신 축 미표기 문제로 F13에 재분류했습니다.

---

## 1. 발견 사항

### F1 — 치명적 · Manifest 스키마를 실제 코드와 다르게 설명

| 항목 | 내용 |
|---|---|
| **위치** | 등록 주제 · `BANK-OM-007 Manifest 등록본 전체 보기` · 관리파일 `manifest` — `schema_version: 2`가 문서 내 8곳 |
| **문제** | 위키는 `schema_version: 2`와 단일 `changed_paths`(10개)를 정본으로 제시. 실제 스키마는 `schema_version`이 `{"const": 1}`, `implementation`의 필수 항목은 `allowed_changed_paths`, `changed_paths` 필드는 **존재하지 않음**. `additionalProperties: false`라 세 가지가 동시 위반 |
| **독자 오해** | 위키 예시를 복사 → 3중 스키마 위반으로 검증 실패. 오류 메시지만으로는 위키가 틀렸음을 알 수 없어 자기 입력을 계속 고치게 됨 |
| **근거** | `harness/acgh/schema/manifest.schema.json` — `schema_version {"const":1}`, `implementation.required=["allowed_changed_paths"]`, `additionalProperties:false`<br>`harness/registrations/om-temp-1.13.1/manifests/*.yaml` — **7개 전부 `schema_version: 1`**, 맨바닥 `changed_paths` 사용 0건 |
| **권장 수정** | ① 코드가 정본이면 위키 예시를 `schema_version: 1` + 3필드로 환원 ② `changed_paths` 통합이 확정 방향이면 스키마 `const`를 2로 올리고 마이그레이션까지 구현한 뒤 공개. 확정 전에는 예시에 “계획 형식이며 현재 검증기는 거부함”을 명시 |

```yaml
# 위키가 가르치는 형식 (검증 거부됨)        # 실제 등록 파일
schema_version: 2                          schema_version: 1
implementation:                            implementation:
  changed_paths:      # 10개 통합            allowed_changed_paths:      # 8
  - ...                                      candidate_additional_paths: # 2
                                             required_changed_paths:     # 1
```

### F2 — 치명적 · 폐기했다는 `candidate_additional_paths`가 현행 등록부·검사기에 잔존

| 항목 | 내용 |
|---|---|
| **위치** | 위키 전체에 해당 용어 **0회**(요청한 제거는 문서상 완료). 대체 서술: “후속 commit의 2개 파일도 `changed_paths`에 모두 적습니다” |
| **문제** | 코드와 현행 1.13.1 등록부에는 **그대로 사용 중**. 더 중요한 점은 이 분리가 단순 중복이 아니라 **검사 기준을 나누는 장치**라는 것 — T25-R은 *원본 스냅샷 8개*로 과거를 재구성하고, T26·T40·T93은 *합집합 10개*를 검사. 위키처럼 10개를 하나로 합치면 T25-R의 역사적 기준선이 바뀌어 재구성 판정이 달라짐. 위키는 이 결과를 설명하지 않음 |
| **독자 오해** | “후속 경로는 같은 목록에 추가하면 된다” → 실제 파일에서 모르는 필드를 만나고, 임의로 합치면 T25-R 기준이 조용히 변경됨 |
| **근거** | 사용 중: `manifest.py` · `drift.py` · `survival.py` · `policy_drift.py` · `debt.py` · `watch_suggest.py` · `manifest.schema.json`<br>실제 값: `om-temp-1.13.1/manifests/BANK-OM-007.yaml` → `candidate_additional_paths` 2개(`serviceConnection.ts`, `DatabaseServiceUtils.test.tsx`)<br>registry 주석: “The source snapshot stops before the BANK-OM-007 follow-up; the final candidate checks its two candidate_additional_paths.” |
| **권장 수정** | F1과 함께 결정. 유지 시 위키에 **네 번째 경로 필드**로 정식 추가하고 “T25-R=원본 8개, T26·T40·T93=10개” 기준 차이를 표로 명시. 폐기 시 6개 모듈·스키마·BANK-OM-007 등록부를 먼저 정리하고 T25-R 기준선 대체 방안을 문서화한 뒤 공개 |

### F3 — 높음 · 독립 실행형이라 했으나 상대경로 자산 35건이 배포본에서 깨짐

| 항목 | 내용 |
|---|---|
| **위치** | 커밋 캡처 `공유문서/assets/om-temp-manifest/…png` 20건 · 충돌 원문 `<iframe src="../../harness/registrations/om-temp-1.13.1/conflict-evidence/…">` 2건 · 문서 간 링크 10건 (고유 30개) |
| **문제** | 저장소 안에서는 정상 해석되나 HTML 한 개만 전달하면 **전부 로드 실패**. 특히 “저장소의 실제 충돌 원문을 그대로 표시합니다” 바로 아래 iframe이 비어, 문서가 약속한 증거가 사라짐 |
| **독자 오해** | 캡처 미표시 → “아직 안 만든 화면”, 빈 iframe → “증거 없음”으로 읽힘 |
| **근거** | 첨부 zip = HTML 1개 + 검토요청 md 1개(자산 미동봉). 캡처 원본은 저장소 `docs/00-사용가이드/공유문서/assets/om-temp-manifest/commit-messages/`에 실재 |
| **권장 수정** | 배포 시 캡처를 `data:` URI로 인라인하거나 자산 폴더를 동봉. 충돌 원문은 핵심 40여 줄만 `<pre>`로 인라인하고 전문은 GitHub 절대 URL로 연결 |

### F4 — 중간 · 판정 상태에 `NOT APPLICABLE` (엔진이 만들 수 없는 값)

| 항목 | 내용 |
|---|---|
| **위치** | 검사기 `t25r` — `verdicts` 4번째 항목, `resultExample: "T25-R | NOT APPLICABLE"` |
| **문제** | 판정 상태는 `pass · approval · block · analysis_error` 4종뿐. 결과 파일에 기록될 수 없는 값이 다른 검사기와 같은 `verdicts` 목록에 나란히 제시됨 |
| **독자 오해** | 결과 파일에서 해당 값을 찾다 실패하거나, 미실행 검사를 “해당 없음으로 통과”로 보고 |
| **근거** | `harness/acgh/verdict.py` — `VERDICTS = (PASS, APPROVAL, BLOCK, ANALYSIS_ERROR)` |
| **권장 수정** | `verdicts`에서 분리하고 “이번 대상에는 실행하지 않음 — 기계 판정이 아니라 적용 대상 여부”로 `status` 쪽에 표기 |

### F5 — 중간 · 존재하지 않는 문서로 연결되는 링크

| 항목 | 내용 |
|---|---|
| **위치** | `OM_TEMP_관리파일_필드_사전_미리보기.html` |
| **문제** | 저장소 `docs/00-사용가이드/`에도, 위키 내장 5개 보고용 원문에도 없음 → 저장소 안에서도 깨지는 링크 |
| **근거** | 실제 목록 = 업그레이드 실행 가이드 · 커밋별 Manifest 등록 가이드 · demo walkthrough 3개뿐 |
| **권장 수정** | 링크 제거 또는 위키의 `file-detail`로 연결. 별도 문서 계획 시 “작성 예정” 표시 |

### F6 — 낮음 · 보고용 그림이 원본 보고서 스타일 전체를 그대로 사용

| 항목 | 내용 |
|---|---|
| **위치** | `renderReportFigure()` — 원본 `<style>` 전량을 shadow DOM에 주입, `replaceAll(":root", ":host")` |
| **문제** | 추출한 브랜치 그림이 원본 보고서의 색·테두리 체계를 유지. 글꼴·크기·줄간격만 위키 값으로 덮어써 요구사항 12의 “같은 위키 디자인 체계”와 어긋날 수 있음. 문자열 치환이라 주석·문자열 내 `:root`까지 변경 |
| **근거** | HTML 정적 분석 기준. **실제 렌더링 색 차이는 브라우저 확인 필요** |
| **권장 수정** | 필요한 최소 CSS만 화이트리스트로 옮기고 색을 위키 토큰(patch·custom 구분색)으로 재매핑 |

### F7 — 높음 · 1.13.1 브랜치가 원격에 없어 결과를 재현할 수 없음

| 항목 | 내용 |
|---|---|
| **위치** | 위키 전반의 1.13.1 결과(후보 `dee330ebd5…`, 소스 검사 8종 PASS, 충돌 증거) |
| **문제** | `easyseop/OM_TEMP` 원격에는 **`patch/om-1.13.0`과 `custom/om-1.13.0` 두 개만** 존재. 1.13.1 patch/custom 브랜치와 후보 `dee330ebd5…`는 원격에 없음 → 독자가 결과를 직접 확인할 수 없음 |
| **독자 오해** | GitHub에서 후보 SHA를 찾다가 실패. 결과표는 PASS인데 대상 코드가 없어 신뢰가 흔들림 |
| **근거** | `git ls-remote easyseop/OM_TEMP` = `custom/om-1.13.0 7d19c895…`, `patch/om-1.13.0 2f4f3560…` (2개뿐) |
| **권장 수정** | 1.13.1 브랜치를 private 원격에 push하거나, 위키의 1.13.1 결과 절에 “후보 브랜치는 아직 원격에 없어 로컬에서만 재현 가능”을 명시(현재 업그레이드 실행 가이드에는 이 문장이 있으나 위키 결과표에는 없음) |

### F8 — 치명적 · 실행된 적 없는 T90에 “12개 pass”가 라벨 없이 제시됨

| 항목 | 내용 |
|---|---|
| **위치** | `WIKI_GATES.t90.inputs[0]` — `"1.13.0 → 1.13.1 · migration/search/rollback 등 12개 pass"` |
| **문제** | T90은 실제 실행 증거가 없습니다(`build-preflight-results.json` = `status: environment_pending`, Java·Maven·Yarn 전부 `available: false`). 그런데 12단계 **전부 pass**가 예시 라벨 없이 적혀 있습니다. 같은 배열의 `inputs[1]`은 `"형식 예시:"`, `inputs[2]`는 `"환경 실행 예시:"` 접두가 있어, 라벨 없는 첫 항목만 **실측 결과처럼** 읽힙니다 |
| **독자 오해** | “업그레이드 12단계는 이미 통과했다”로 보고. 실제로는 한 번도 실행되지 않았습니다 |
| **근거** | `om-temp-1.13.1/build-preflight-results.json` → `environment_pending`. 문서 전체에 `가상`이라는 단어 **0회** |
| **권장 수정** | `가상 예시:` 접두를 붙이고, 실행 증거가 없는 모든 값에 동일 라벨을 통일 적용. `환경 실행 예시`라는 표현은 “환경에서 실행했다”로 읽히므로 폐기하고, 실측값에만 `실측:`을 사용 |

### F9 — 높음 · T25-R 실행 명령에 diff 마커 `+`가 남았고 다른 도구를 가리킴

| 항목 | 내용 |
|---|---|
| **위치** | `WIKI_GATES.t25r.command` — `... validate_registration_bundle.py \`↵`+  --repo /path/to/OM_TEMP` |
| **문제** | ① 두 번째 줄이 `+`로 시작합니다. **diff 마커가 그대로 남아** 복사·실행 시 실패합니다(다른 16개 명령에는 없음). ② `t25r.code`는 `vendor_rebuild.py`인데 명령은 `validate_registration_bundle.py`(등록자료 검증기)로, **재구성 검사를 실행하는 명령이 아닙니다** |
| **독자 오해** | 등록 검증기를 돌리고 그 PASS를 T25-R 결과로 오인 |
| **근거** | `validate_registration_bundle.py`는 `om-temp-1.13.0/`에만, `vendor_rebuild.py`는 `harness/acgh/`에 존재 |
| **권장 수정** | `+` 제거. 실제 T25-R 진입 명령으로 교체하거나, CLI 진입점이 없으면 “현재 CLI 없음 · 모듈 직접 호출”로 정직하게 표기 |

### F10 — 높음 · 검사 실행기가 `kb-openmetadata`에만 존재해 OM_TEMP 검사가 잘못된 등록 묶음을 가리킴

| 항목 | 내용 |
|---|---|
| **위치** | `t61` · `t62` · `t63` · `t43` · `t93_policy`의 `command` |
| **문제** | `run_source_candidate_gates.py` · `run_upgrade_risk_gates.py` · `run_source_patch_kills.py` · `run_runtime_contracts.py` · `compare_ui_typecheck.py`가 **전부 `harness/registrations/kb-openmetadata/`에만 존재**합니다(om-temp-1.13.0/1.13.1에 없음). 스크립트 경로 표기 자체는 사실이나, 그 결과 T61·T62·T63 명령이 `--registration harness/registrations/kb-openmetadata`까지 지정해 **OM_TEMP 코드를 과거 참고 등록 묶음(BANK-OM-001~011)의 Manifest·Contract로 검사**하게 됩니다. T43·T93-정책도 `--change-intent`만 kb를 가리키는 반쪽 혼합입니다 |
| **독자 오해** | 명령을 그대로 실행 → 다른 Contract·필수 test 기준으로 판정이 나오고 그 결과가 OM_TEMP 증적으로 보관될 수 있습니다(거짓 PASS 경로) |
| **근거** | `find harness/registrations -name 'run_*.py'` → 전부 `kb-openmetadata/`. `change-intent-current.yaml`도 `kb-openmetadata/`에만 존재 |
| **권장 수정** | 실행기를 `om-temp-1.13.1`로 이식하고 `--registration`·`--change-intent`를 해당 묶음으로 교체. 이식 전이라면 각 명령에 **“실행기가 아직 과거 등록 묶음에만 있어 OM_TEMP 검사에 그대로 쓰면 안 됨”**을 경고로 명시 |

### F11 — 높음 · 도식의 Cycle에 “병합 전 T42 영향 확인”이 빠져 있음

| 항목 | 내용 |
|---|---|
| **위치** | 브랜치 Cycle SVG · `REPORT_DETAIL_MAP[phase1].report.flow`(6단계) vs `WIKI_TOPICS.upgrade.sections`(7단계) |
| **문제** | `t42.timing`은 “**커스터마이징 병합 전에 실행**”을 명시하는데, 도식과 phase1 흐름에는 T42 사전 영향 확인과 등록 갱신 단계가 없어 `patch branch → 병합`으로 바로 이어집니다. 같은 Cycle이 문서 안에 **3·4·6·7단계 네 가지 버전**으로 존재합니다 |
| **독자 오해** | 도식을 절차서로 쓰는 담당자가 **병합 전 T42를 건너뜁니다** → APPROVAL 대상이 미검토 상태로 충돌 해결이 진행됩니다 |
| **권장 수정** | SVG에 `T42 사전 영향 확인`과 `등록 갱신` 노드를 추가하고, `upgrade.sections` 7단계를 단일 정본으로 삼아 나머지를 생성 |

### F12 — 중간 · 완료 조건·중단/상신 조건·증적 보존 경계가 비어 있음

| 항목 | 내용 |
|---|---|
| **문제** | ① **완료 조건**이 17개 검사기 어디에도 없습니다(`WIKI_GATES` 스키마에 필드 자체 없음). 문서의 `완료 조건` 4회 중 3회는 “있어야 한다”는 서식 명세입니다. ② **중단·상신**: `에스컬레이션` 1회(체크리스트 행), `상신` 0회 — 누구에게·기한·양식이 없습니다. ③ **보존**: `90일` 0회, `아카이브` 0회. `evidence.update`는 “새 파일로 보관합니다”로 영구 보존을 암시합니다 |
| **독자 오해** | PASS = 완료로 등치(그러나 `t26.limit`은 “T62 결과가 필요”라고 반대로 말함). CI artifact에 남으니 감사 대응이 된다고 판단 → 90일 후 증적 소실 |
| **권장 수정** | 각 gate에 `완료 조건`과 `재실행할 검사`(현재 17/17 누락) 필드 추가. `block_action`에 *판정 × 중요도 × 상신 대상 × 기한* 표 추가. `evidence`에 “현재 증적은 CI artifact 90일이 상한이며 조직 소유 장기 아카이브가 없음”을 fail-closed 문장으로 명시 |

### F13 — 중간 · “전체 변경 목록 111개”의 비교 축이 명시되지 않음

| 항목 | 내용 |
|---|---|
| **위치** | `WIKI_TOPICS.registration.resultExample` — `"Git 전체 변경 목록: 111개 경로 PASS"` |
| **문제** | **수치 자체는 정확합니다.** 111은 `source-diff-paths.txt`(공식 ↔ 행내 커스터마이징 차이 = 등록 대상)이고, 834는 `upgrade-watch-results.json`의 공식 1.13.0→1.13.1 변경입니다. **서로 다른 축**입니다. 그러나 “**전체** 변경 목록”이라는 라벨에 축이 적혀 있지 않아, 같은 문서의 834와 나란히 놓이면 혼동됩니다 |
| **오해 실증** | 이번 검토 과정에서 숙련된 검토자가 실제로 두 수치를 혼동해 “723개 미등록 경로가 은폐됐다”는 잘못된 결론에 도달했습니다. 라벨 모호성이 실제로 오독을 유발함이 입증된 사례입니다 |
| **근거** | `source-diff-paths.txt` 111줄(`Entity.java`, `schemaChanges.sql` 등 행내 수정 파일) / `upgrade-watch-results.json` `{base: 1.13.0-release, target: 1.13.1-release, changed_path_count: 834}` |
| **권장 수정** | `"공식 ↔ 행내 차이 111개 경로"`처럼 축을 라벨에 넣고, T42의 834에는 `"공식 1.13.0 → 1.13.1 변경 834개"`를 병기 |

### F14 — 중간 · 실패(BLOCK) 출력 예시가 17개 검사기 전부에 없음

17개 `resultExample` 중 실패 판정은 **0건**입니다(APPROVAL 4건, `NOT APPLICABLE` 1건). 유일한 BLOCK 예시는 `block_action` 페이지에만 있고 검사기 상세에서 연결되지 않습니다. 담당자가 `required_path_missing: <path>` 같은 `reasons` 형식을 실제 장애 상황에서 처음 보게 됩니다. → 각 gate에 `실패 예시` 최소 1건 추가.

### F15 — 치명적 · 검사기 상태 칩이 항상 초록(PASS)으로 표시돼 미실행을 통과로 보이게 함

| 항목 | 내용 |
|---|---|
| **위치** | HTML 806행 `<span class="pass" id="gate-status"></span>` + 2493행 `document.getElementById("gate-status").textContent = gate.status;` |
| **문제** | 상태 칩의 CSS 클래스가 **`pass`로 하드코딩**돼 있고 JS는 `textContent`만 교체합니다. 따라서 아래 문장들이 전부 **초록 PASS 칩** 안에 렌더링됩니다:<br>· T90 `"…실제 행내 업그레이드 실행 증거 대기"`<br>· T91 `"…실제 배포 환경 결속 대기"`<br>· T62 `"…실제 행내 환경 실행 대기"`<br>· T61 `"…환경별 실행 증거 필요"`<br>· T93-정책 `"…실행 결과 없음"` |
| **독자 오해** | 색을 먼저 읽는 대다수 독자가 **T90·T91을 통과한 검사로 인식**합니다. 문서 자신이 명시한 “결과가 없는 상태를 PASS로 표시하지 않습니다” 원칙과 화면이 정면으로 어긋나는 **거짓 통과(false pass)** 표시입니다 |
| **근거** | `.pass { color: var(--green); background: var(--green-soft); }` (202행). `renderGate`에서 `className` 변경 코드 없음 |
| **권장 수정** | 각 gate에 `statusLevel: "pass"｜"approval"｜"block"`을 추가하고 `renderGate`에서 `el.className = gate.statusLevel`로 교체. 최소 조치로 T61·T62·T90·T91·T93-정책·T43·T63에 `.approval`(호박색) 적용 |

### F16 — 치명적 · nav로 닿지 않는 중복 페이지 6개가 남아 있고, 그중 하나는 현행 규칙과 정반대를 지시함

| 항목 | 내용 |
|---|---|
| **위치** | `#gate-template` · `#t42` · `#manifest` · `#file-template` · `#candidate-lock` · `#procedure` — 6개 모두 `<article>`은 존재하나 `data-page` 참조 **0건** |
| **문제** | nav 클릭으로는 못 열지만 `showPage`가 `location.hash`로 라우팅하므로 **URL·북마크·브라우저 기록으로는 열립니다.** 그중 `#candidate-lock`은 현행 규칙과 **정반대**를 지시합니다:<br>· 구 페이지: “커밋만 완료된 시점에는 배포 이미지가 없으므로 **소스 commit과 빌드 산출물이 모두 확정된 뒤 생성해야 합니다**”<br>· 현행 `WIKI_FILES.candidate_lock.created`: “**소스 검사 후보가 확정되면** commit·tree로 생성하고, 이미지 생성 후 별도 lock을 추가로 만든다” |
| **독자 오해** | 구 페이지를 본 담당자가 **“이미지가 없으면 Candidate lock을 만들면 안 된다”**고 판단해, 현재 OM_TEMP가 수행 중인 **소스 전용 검사 흐름 자체를 중단**시킵니다 |
| **근거** | `grep 'id="candidate-lock"'` = 1건, `grep 'data-page="candidate-lock"'` = 0건 (6개 id 모두 동일 패턴) |
| **권장 수정** | 6개 `<article>`을 삭제. 남긴다면 `showPage`에서 nav 버튼이 없는 id는 `home`으로 되돌리도록 라우팅을 제한 |

### F17 — 중간 · 그 밖에 확인된 문서 구조·표기 문제

| 구분 | 내용 |
|---|---|
| **장 순서** | 요구된 1→7 대비 실제는 **1 → 2 → 5 → 3 → 4 → 6**. 2장에서 17개 검사기를 다 읽은 뒤에야 3장에서 그 검사기가 읽는 Manifest·Registry를 배웁니다. “왜 필요한가”에 해당하는 문장은 렌더링 화면에 **없습니다**(홈 h1이 문서 구조 설명으로 대체됨) |
| **규격서 노출** | `source-gates` 페이지의 “각 개별 검사 페이지에 들어갈 내용” 8개 `<ol>`은 **문서 저자용 목차 규격**인데, 담당자가 자기가 수행할 8단계 절차로 읽습니다 |
| **빈 페이지 / 죽은 메뉴** | `release-gates`는 lead 한 문장 외 **본문이 비어 있고** T90·T91 링크도 없습니다. nav의 「용어 사전」·「실제 파일·코드 위치」는 판정표 하나뿐인 같은 페이지로 연결됩니다 |
| **5요소 결손** | 관리파일 12개 중 **폐기 시점 12/12 누락**, **읽는 검사기 번호 8/12 누락**, **PASS/APPROVAL/BLOCK 비교 9/12 누락** |
| **대비·잘림** | `.flow i { color:#7b879b }` = 3.63:1로 AA 미달인데 `+`·`=`·`→` 연산자를 담습니다(8+2=10 관계가 사라짐). `#file-detail table { min-width:900px }`는 1280px 창의 본문 폭(≈797px)을 넘어 **“실제 값 예시” 열이 기본 화면에서 잘립니다** |
| **문제 없음 확인** | 금지 은유(영수증·요리·레시피·짐·신호등) **0건**, 도메인 용어 보존, BANK-OM ID/커밋 메시지/커밋 SHA 3분 구분 + 실제 예시 완비, 고아 지시어 0건 |

---

## 2. 요약과 상세의 불일치 목록

| 항목 | 보고용 요약 | 상세 페이지 | 판정 |
|---|---|---|---|
| 브랜치 전략 그림 | 1차 요약에 원본 그림 추출 노출 | 같은 그림·같은 병합 지점 | 일치 |
| vendor-merge 정의 | “patch branch와 직전 custom branch의 BANK-OM 변경을 다음 버전 custom branch에서 합치는 전체 branch 병합 방식” | 동일 정의 | 일치 |
| 1.13.1 후보 생성 방식 | “커밋별 재적용 진단 — 부분 확인”, “실제 vendor-merge·배포 — 미확인” | 동일 구분, NOT VERIFIED 표기 | 일치 |
| Manifest 경로 필드 | 요약에 필드 수준 서술 없음 | `changed_paths` 단일 필드 | **상세가 코드와 불일치 (F1·F2)** |
| 보고용 그림 시각 체계 | 원본 보고서 스타일 유지 | 위키 토큰 기반 | **시각 불일치 가능 (F6)** |

> 요약↔상세의 **내용** 불일치는 발견되지 않았습니다. 불일치는 상세 쪽이 코드와
> 어긋난 F1·F2와 시각 체계 F6에 한정됩니다.

## 3. 현재 구현 상태와 설명의 불일치 목록

| 주제 | 위키 설명 | 실제 코드·파일 | 영향 |
|---|---|---|---|
| Manifest 버전 | `schema_version: 2` | `const 1` (등록부 7개 전부 1) | 검증 거부 |
| 경로 필드 | `changed_paths` 1개 | `allowed` / `candidate_additional` / `required` 3개 | 검증 거부 · T25-R 기준 변동 |
| 후속 경로 개념 | 언급 없음(폐기 전제) | 6개 모듈 + BANK-OM-007에 실사용 | 운영 혼선 |
| T25-R 판정 | `NOT APPLICABLE` | 4종 판정에 없음 | 보고 오류 |
| 1.13.1 후보 | 결과 PASS 제시 | 원격에 브랜치 없음 | 재현 불가 |
| T43 임계값 | 14/19 · 14k/18k · 4/8 · 15%/35% | 동일 | **일치** |
| T43 충돌률 | “검사기가 계산하지 않고 사용자가 입력” | `collect_metrics(conflict_rate=…)` 인자 | **일치** |

## 4. 신입사원이 추가로 물을 질문

| 질문 | 답변 가능 여부 |
|---|---|
| “위키대로 Manifest를 만들었는데 `additionalProperties` 오류가 납니다. 무엇이 맞습니까?” | **문서로 답 불가** (F1·F2) |
| “BANK-OM-007 파일의 `candidate_additional_paths`는 무엇입니까?” | **문서로 답 불가** (F2) |
| “새 경로가 생기면 allowed·required·watch 중 어디에 넣습니까?” | **보완 필요** — 단일 모델 서술로 3분법 기준이 흐려짐 |
| “후보 `dee330ebd5…`를 GitHub에서 못 찾겠습니다.” | **보완 필요** (F7) |
| “같은 BANK-OM ID에 후속 commit이 생기면 새 ID를 만듭니까?” | 답 가능 — BANK-OM-007 예시로 설명 |
| “왜 최근 SHA 하나만 쓰면 안 됩니까?” | 답 가능 — `62e39da8…` / `7d19c895…` 구분 설명 |
| “충돌 원문을 보려는데 화면이 비어 있습니다.” | 배포 방식 수정 필요 (F3) |

## 5. 확인 결과 문제 없음 (근거 대조 완료)

1. **요구사항 1 (요약↔상세)** — 보고용 요약은 원본 HTML을 상자에 끼워 넣은 형태가 **아님**.
   `REPORT_DETAIL_MAP`에 질문·답·근거·흐름·상태·다음단계로 재작성되어 위키 자체
   컴포넌트로 렌더링되며 브랜치 전략 그림도 요약에 노출됨.
2. **요구사항 8 (Git 병합·충돌) — 전량 교정 확인** — 이전 판의 “두 개의 *전체 파일* 버전”이
   **“두 개의 큰 충돌 블록”**으로 수정됐고 줄 수도 실제와 일치(2,373 / 3,178).
   `HEAD`를 “현재 작업 branch의 코드, 이번에는 공식 1.13.1”로 정의. `cherry-pick`을
   “다른 branch의 특정 변경 기록 하나를 현재 branch에 적용하는 명령 · 순서를 바꾸는
   명령이 아님”으로 정확히 설명하고 사용 이유와 정식 병합 절차를 구분.
3. **해결 결과의 JSON 위치** — 9개를 모두 `label`에 넣던 오류가 **`label` 7개 /
   `message` 2개**로 교정(실제 해결본과 일치).
4. **근거 없는 단정 완화** — “001~004가 매번 같은 18개”가 “002~004는 건수만 보관했으므로
   파일 목록이 완전히 같다고 단정하지 않습니다”로 교정.
5. **T43 기준값** — “기능 수 14/19, 변경량 14,000/18,000, 한 파일 ID 수 4/8, 충돌률
   15%/35%”가 `harness/policies/debt-thresholds.yaml`과 **정확히 일치**. 충돌률이 사람
   입력이라는 한계도 명시.
6. **판정 용어** — 위키의 `APPROVAL`은 코드와 일치. 오히려 *검토요청서*의 “REVIEW”가
   코드에 없는 용어이므로 요청서 쪽을 `APPROVAL`로 맞추는 편이 좋음.

## 6. 수정 순서 제안

1. **사실 오류 확정 — F1 · F2.** 먼저 *코드가 정본인지, `changed_paths` 통합이 확정
   방향인지*를 결정. 이 결정 없이 문서만 고치면 다시 어긋남. 결정 후 스키마·6개
   모듈·BANK-OM-007 등록부·위키 예시를 한 묶음으로 정렬.
2. **검사 기준 차이 명문화.** T25-R(원본 8개)과 T26·T40·T93(합집합 10개)이 서로 다른
   기준을 본다는 사실을 표 하나로 추가. 빠지면 F2를 고쳐도 같은 혼선이 재발.
3. **재현 경로 확보 — F7.** 1.13.1 브랜치를 원격에 push하거나 위키 결과표에 “원격
   미보관” 사실을 명시.
4. **용어·판정 정리 — F4.** `NOT APPLICABLE`을 판정 목록에서 분리. 검토요청서의
   “REVIEW”도 `APPROVAL`로 통일.
5. **예시·링크 보강 — F5.** 없는 문서 링크 제거 또는 `file-detail` 연결.
6. **배포 방식 — F3.** 캡처 인라인 또는 자산 동봉으로 “독립 실행형” 주장을 실제로 성립.
7. **시각 정리 — F6.** 보고용 그림 색을 위키 토큰으로 재매핑.

---

## 7. 검토 범위와 한계

- 수행: 첨부 HTML 정적 분석 + `openmetadata-test@dfc43f1` 코드·스키마·등록파일 대조 +
  `OM_TEMP` 원격 브랜치 실측.
- **미수행**: 브라우저 실제 렌더링(1280px·390px, 접힘 영역 시각 확인, 색 대비 실측).
  따라서 F6과 요구사항 12의 시각 항목은 브라우저 확인이 남아 있음.
- **진행 중**: 요구사항 2·3·4·7·9·10·11의 문장 단위 전수 점검(개념별 5요소, 검사기별
  8항목, JSON 도구 10항목, 예시 완전성)은 별도 심층 검토가 진행 중이며 완료 시 추가.
- 추측으로 사실을 보완하지 않았으며, HTML만으로 확인 불가한 항목은 위에 명시함.
