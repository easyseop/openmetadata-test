# OpenMetadata 커스터마이징 거버넌스 — 개발 실행 계획 (Build Plan)

> **2026-07-24 변경:** [`ADR-001`](../02-설계/ADR-001-vendor-merge-default.md)에
> 따라 vendor merge가 기본 통합 전략이다. 아래 기존 T20~T23 replay 파이프라인은
> 선택 모드로 유지한다. T24 candidate-lock과 T25 vendor ancestry는 완료됐고,
> 기본 경로를 완성하는 T26~T29가 후속 작업이다.

> **이 문서의 위치**
> 최종 목표부터 개별 개발 태스크까지를 **순차 개발 가능한 형태**로 기록한다.
> GPT 검토(P0~P2)와 그 재검토 응답을 반영한 **정정 후 아키텍처** 기준이다.
> 실제 개발은 이 문서의 마일스톤 순서대로 진행한다.
>
> **선행 문서**: 상세 설계 / 전략 브리핑 / SRS / 검토 응답(`openmetadata_review_response.md`)

---

## 0. 최종 목표

> 공식 OpenMetadata 버전이 올라가도 **행내 커스터마이징을 누락 없이 · 추적 가능하게 ·
> 검증 가능하게 보존**하여, vendor branch 업그레이드 운영을 원활하게 만든다.

보장 범위를 정확히 나눈다 (P0-5·P0-7 반영):

| 계층 | 자동으로 보장하는 것 | 보장하지 않는 것 (다른 계층이 담당) |
|---|---|---|
| 등록·통합 생존 게이트 | 승인된 공식 SHA가 통합되고 등록된 수정이 candidate에 남음 | 로직 생존·기능 의미 |
| 계약 테스트 / 업그레이드 테스트 | 명시된 업무 불변식의 **동작** | 테스트에 없는 새 의미 차원 |
| 증거 생성기(구조화 diff) | API·설정·DB·의존성의 **구조 변화 사실** | 그 변화의 업무 영향 판단 |
| 운영 관찰(canary) | 실제 부하·데이터에서의 거동 | — |

**한 줄**: 자동 검증은 "등록·업스트림 통합·candidate 생존"을 구조적으로 확인하고, "기능 의미"는
테스트·업그레이드 검증·운영 관찰·LLM 보조로 **잔여 위험을 관리**한다.

---

## 1. 아키텍처 원칙 (정정 후)

1. **코어 최소화** — 새 요구는 설정→배포→확장→코어 4단계 관문. 충돌은 코어에서만 난다.
2. **불변 ID + customization registry** — 기능·계약의 안정된 식별자. replay 모드에서는 series 허용.
3. **고정 SHA 기반 upstream/candidate lock** — 공식 target과 검증 candidate를 고정한다.
4. **vendor ancestry·생존 검증 기본** — clean-room replay는 선택 진단·복구 모드다.
5. **판정 스파인 / 증거 생성기 분리** — 판정은 언어 무관·결정적, 증거는 대상별 전문화(§8).
6. **등록·통합 생존 ≠ 기능 완전성** — 게이트 명칭·문구에 분리 반영(P0-5).
7. **verdict severity rank** — pass<approval<block<analysis_error, 분석실패=차단(P0-3·4).
8. **선언형 verifier** — manifest에 임의 command 금지(P0-8).
9. **정책 자기보호** — policy PR은 base 정책으로 평가 + 2인 승인 + 플랫폼 통제(P0-9).
10. **LLM 배포 판정 배제** — 읽기·설명·후보(Memo)만, pass 권한 없음(§7).
11. **테스트가 생존을 증명** — contract-id ↔ 테스트 결속 + patch-kill test(§5·C-4).
12. **range-diff는 리뷰용** — 기계 판정은 ancestry·lock·manifest·raw diff(P0-1).

---

## 2. 마일스톤 개요 (개발 순서) — 2차 검토 반영 개정판

> 2차 검토(B절)의 재배치를 반영: source 불변식 preflight를 재적용보다 앞으로,
> T93을 T42보다 앞으로, T62·T70 최소 기능을 앞당김. 신규 태스크 T05·T15·T23.

```
M0    사전 셋팅: T01~T04 + [신규 T05] path-ownership·glob grammar 정본
M1    기반: T10(스키마)·T12(git)·T13(verdict) + [신규 T15] result/CI adapter
      + T14(감사카드) + T11(patch-lock — source/application 분리)
      ※ T12·T13 즉시 착수 가능 / T10·T11은 부칙 A 반영 후 동결
M1.5  source stack preflight: T30·T31 (재적용 전에 소스 불변식 검사)
M2    통합: T24→T25→T26(vendor merge 기본) + T20→T23(replay 선택 모드)
M3    완전성·결속: T40(touched/net 분리) → T32(최종상태) → T62(테스트-SHA 결속) → T33 → T41
M4    감시·영향: T93(watch drift, 먼저) → T42(영향분석) + T50(선언형 verifier; 실행형·sandbox는 후속)
M5    증거 생성기: T51·T52 (공통 provider SDK 후 병렬 가능) + provider 자기보호(C-3)
M6    테스트 결속: T60(contract 정본) → T61(patch-kill — high/critical 우선, 상태 4종)
M7    정책: T70(base-policy 최소 기능은 M3 전 선행 가능) → T71 → T72
M8    LLM: T80 → T81
M9    릴리스: T90 → T92(해당 시) → T91(digest 승격) → T94(내부망)
```

각 태스크 기술 형식: **목적 / 충족(문제·게이트·P0·REQ) / 구현(입출력·자료구조·로직) /
수용 기준 / 선행**. 신규 태스크(T05·T15·T23)와 변경된 의존성·범위는
`2차 검토 결과 문서의 B-3 표`를 정본으로 따른다.

### 신규 태스크 (2차 검토 반영)

- **T05 · path-ownership·glob grammar 정본** (M0) — upstream SHA에 결속된
  `repository-layout.yaml`(upstream/bank/extension roots, unknown=analysis_error)
  + path 문법 고정(문법 버전·정규화·부정 패턴·symlink 정책). CG-01·MF-01·GZ·
  T93이 같은 의미를 쓰게 하는 전제. → 부칙 A-3.1
- **T15 · result writer/CI adapter** (M1) — 원자적 결과 생성, canonical
  digest, exit/result 불일치=analysis_error, attestation 분리, 다중 저장소
  입력 결속. → 부칙 A-1
- **T23 · resolve 직렬화/단일 integrator** (M2) — resolve queue를 lock 순서로
  직렬화, 담당자는 제안만, integrator가 base_lock_digest CAS 확인 후 반영.
  → 부칙 A-2.5

### vendor-merge 전환 태스크 (ADR-001)

- **T24 · integration strategy + candidate lock (✅ 완료)** — 기본값
  `vendor-merge`, 공식 base/target SHA와 candidate commit/tree/artifact digest를
  고정하고 결과 입력을 candidate-lock digest에 결속.
- **T25 · vendor ancestry gate (✅ 완료)** — candidate가 공식 target SHA와
  locked base를 ancestry에 포함하고, base/target이 공통 조상을 유지하는지
  결정적으로 검증. 객체 누락·stale lock·모드 오라우팅은 analysis_error.
- **T26 · customization survival gate (✅ 구현·단위검증 완료)** — ID별 required state·path·contract가
  merge candidate에 남아 있는지 검증.
- **T27 · merge conflict evidence (✅ 구현·단위검증 완료)** — 충돌 파일·해결 결정·승인자를 구조화 기록.
- **T28 · replay optional routing (✅ 구현·단위검증 완료)** — T20~T23을 선택 진단 모드로 라우팅.
- **T29 · 실제 커스터마이징 등록 (✅ 등록 완료·운영 증거 미완)** — `kb_openmetadata`의 InstanceCode,
  QueryReport, Assertions, 컬럼 확장, IME, Sybase, Tibero를 manifest/contract화.
  원본이 ancestry 없는 단일 root snapshot이므로 vendor branch 재구성 전 T25는
  의도대로 차단하며, owner 배정과 실제 contract test 구현은 남아 있다. 전체
  113개 diff 중 111개는 7개 manifest에 귀속했고, `.claude/settings.json`의
  자동승인 확대와 Docker Compose의 ingestion `1.9.6` 고정은 별도 blocking
  finding으로 등록했다.

### MVP 2단계 (2차 검토 B-5 수용)

- **Candidate-control MVP** — candidate를 기계적으로 통제:
  T01~T05 · T10~T15 · T30·T31 · T20~T23 · T40·T41·T62·T32·T33 · T93·T42 ·
  T50(활성 non-core 커스터마이징 있으면) · T70 최소 기능
- **Production-upgrade MVP** — 운영 릴리스·반입까지 통제(위에 추가):
  T60 · T61(high/critical) · T72 · T90 · T91 · T94 · T92(해당 시)
- 제외 가능: T43 hard-block 임계치 · T51/52 전체 범용화(수동 evidence 절차
  전제) · T71 완전판 · T80/81 · low/medium 상시 patch-kill

---

## M0. 사전 셋팅 (정책·명세 저작 — 코드 아님)

### T01. 현재 커스터마이징 인벤토리 추출·분류
- **목적**: 현재 행내 변경을 전수 추출하고 config/deployment/extension/core-patch로 분류.
- **충족**: P3·P6 / 원천 억제 기반.
- **구현**: 공식 기준 태그 대비 전체 diff 추출 → 파일·기능 단위로 분류표 작성.
  목적 불명 변경 식별. 산출물: `inventory.csv`(파일·유형·추정 목적·담당 후보).
- **수용**: 모든 현재 변경이 유형 분류됨, 목적 불명 항목이 목록화됨.
- **선행**: 없음.

### T02. 코어 변경을 이름표 커밋 series로 재구성
- **목적**: core-patch를 `BANK-OM-xxx` ID 붙인 **순서형 커밋 series**로 분해.
- **충족**: P1·P3 / P0-5(series 모델).
- **구현**: 논리 단위로 커밋 분해, 각 커밋에 `Customization-ID` trailer.
  1커밋=1ID, 1ID=여러 커밋 허용(series). `docs/upgrade/.../series.md` 초안.
- **수용**: 모든 코어 변경 커밋이 정확히 1개 ID trailer 보유, ID 없는 코어 커밋 0.
- **선행**: T01.

### T03. 민감 영역·승인 라우팅·임계치 저작
- **목적**: `sensitive-zones.yaml`, `approval-routing.yaml`, `thresholds.yaml` 작성.
- **충족**: 원천 억제·Gate 4·자기보호.
- **구현**: 코어 경로 frozen/protected/watched 분류(인증·마이그레이션·검색 등).
  criticality별 승인자. 부채 상한(초기 경고 수준).
- **수용**: 각 민감 패턴이 현재 버전에서 ≥1 실제 경로 매칭(P0/§10.5 사전).
- **선행**: T01.

### T04. 명세·테스트 카탈로그·계약 초안
- **목적**: `customizations/*.yaml`, `test-catalog/*.yaml`, `contracts/*.yaml` 초안.
- **충족**: P3·P6 / Gate 2 / 테스트 결속.
- **구현**: 각 ID 명세(요구사항·owner·retirement + 아래 M1 스키마 필드).
  업무 불변식을 contract-id로(예: `AUTH-INV-001`).
- **수용**: 모든 active ID에 owner·필수 테스트·contract 연결 존재.
- **선행**: T02.

---

## M1. 기반 (스키마 · patch-lock · git 프리미티브 · verdict 엔진)

### T10. 명세 JSON Schema — 역할 분리 반영
- **목적**: manifest 스키마 확정. **구현 범위와 감시 범위 분리**(P0-6).
- **충족**: P0-6 / REQ-MF-01 / 방향 C.
- **구현**: 필드
  ```yaml
  implementation:
    allowed_changed_paths: []   # 이 패치가 변경 허용된 파일
    required_changed_paths: []  # 반드시 변경돼야 하는 파일
  upgrade_watch:
    paths: []                   # 업스트림 변경 감시(의존 포함)
    configuration_keys: []
    dependencies: []
    contracts: []               # 연결된 업무 불변식 ID
  ```
  `jsonschema`(2020-12)로 검증 + 코드 규칙(중복 ID, core-patch인데 required_changed_paths 없음 등).
- **수용**: allowed/required/upgrade_watch 분리 검증 픽스처 통과, verification.command 필드 **부재**(T50에서 선언형으로 대체).
- **선행**: T04.

### T11. patch-lock 자료구조·생성기
- **목적**: 재적용 소스를 **고정 SHA**로 잠그는 patch-lock 도입(P0-1·§10.2).
- **충족**: P0-1 / REQ-CB-02 대체.
- **구현**: 릴리스별 lock
  ```yaml
  patch_series:
    - id: BANK-OM-001
      revision: 4
      source_release_tag: om-1.5-bank.2
      source_release_sha: abc123
      source_commits: [ ... ]      # 고정 SHA 목록
      depends_on: [BANK-OM-002]
  ```
  생성기: candidate 확정 시 실제 applied_commits·SHA 기록.
- **수용**: 동일 patch-lock으로 재적용 시 동일 결과(재현). 최신 브랜치 동적 조회 없음.
- **선행**: T10.

### T12. git 프리미티브 라이브러리
- **목적**: 결정적 git 접근 계층(줄바꿈 아닌 `-z`, 커밋 경계 유지).
- **충족**: P0-1·P0-5 / §8 결정론.
- **구현**: `trailers:key=Customization-ID,valueonly`로 trailer 파싱(본문 정규식 금지),
  `git diff-tree --raw -z`, `git log --format` 커밋 경계별 파싱, `patch-id --stable`(힌트 전용).
  환경 고정: git 버전·locale·rename 임계치·정렬·전역설정 비활성(§8).
- **수용**: ID 없는 커밋을 커밋 단위로 식별(집합 축약으로 놓치지 않음), 3회 실행 동일 출력.
- **선행**: 없음(M1 병행).

### T13. verdict 엔진 (severity rank + exit 매핑)
- **목적**: 게이트 결과 집계를 severity rank로(P0-3), 분석실패=차단(P0-4).
- **충족**: P0-3·P0-4 / REQ-OR-01·02.
- **구현**:
  ```python
  RANK = {"pass":0,"approval":1,"block":2,"analysis_error":3}
  EXIT = {"pass":0,"block":1,"approval":2,"analysis_error":3}
  ```
  최종 = 최고 rank. 게이트 파일 부재·Traceback·타임아웃 → `analysis_error`.
  결과를 exit code와 **별도로** `acgh-result.yaml`(verdict enum)로 산출.
- **수용**: block+approval 동시 → **block**(격하 안 됨). 분석실패 → 차단. CI가 result 파일로 구분.
- **선행**: 없음.

### T14. 감사카드(evidence) 스키마·집계
- **목적**: 게이트·증거·LLM 산출을 한 카드로.
- **충족**: G4 / REQ-GZ-04.
- **구현**: `change-evidence.yaml`(gate별 verdict·근거·승인자·`llm_suggestions` 분리 필드).
  입력 snapshot SHA·harness version 포함. 출력 경로는 대상 repo 밖/gitignore.
- **수용**: 여러 게이트 결과가 한 카드로 집계, 승인자·근거·LLM 필드 분리.
- **선행**: T13.

---

## M2. 재적용 파이프라인 (2-모드 충돌 · clean-room replay)

### T20. 재적용 — CI 탐지 모드
- **목적**: 충돌 유무를 임시 worktree에서 안전 탐지(P0-2).
- **충족**: P0-2·Gate 1 / REQ-RA-01.
- **구현**: 임시 worktree에서 patch-lock 순서대로 `cherry-pick` → 충돌 시 ID·파일·상태
  리포트 후 **worktree 폐기·exit 1**. (본 저장소 트리 오염 없음)
- **수용**: 무충돌 스택 exit 0, 충돌 시 해당 ID·파일 리포트 + 트리 clean 유지.
- **선행**: T11·T12.

### T21. 재적용 — 담당자 해결 모드
- **목적**: 충돌을 사람이 실제로 해결할 수 있는 흐름(P0-2).
- **충족**: P0-2·P3 / REQ-RA-02.
- **구현**: 전용 worktree에서 충돌 상태 **유지** → 담당자 해결 → `cherry-pick --continue`
  → 해결 커밋을 **새 patch revision으로 고정** + `Source-Commit`·`Patch-Revision`·`Resolution-Record` 기록.
- **수용**: 해결 결과가 patch-lock 리비전으로 저장되어 다음 재적용에서 재현됨.
- **선행**: T20.

### T22. clean-room replay 검증
- **목적**: 깨끗한 환경 재생 결과 == candidate tree(P0-5·C-5).
- **충족**: P0-5·재현성 / 신규 REQ.
- **구현**: 격리 환경에서 patch-lock 전체 재생 → 결과 tree 해시와 candidate HEAD tree 해시 비교.
  빌드 비결정성(타임스탬프·정렬·locale) 제거.
- **수용**: 재생 tree == candidate tree(불일치 시 차단). 동일 입력 3회 동일 해시.
- **선행**: T21.

---

## M3. 등록·재적용 완전성 게이트 (불변식)

### T30. 커밋 단위 불변식 검사
- **목적**: 커밋 경계에서 등록 규칙 강제(P0-5).
- **충족**: P0-5 / REQ-CG-01 개편.
- **구현**: 업스트림 경로를 건드린 커밋은 정확히 1 ID / ID 없는 커밋 실패 / 다중 ID 실패 /
  merge·empty 커밋 실패 / core·governance 혼합 실패(`Change-Type: governance` 분리).
- **수용**: 각 위반을 개별 픽스처로 검출. 집합 축약으로 ID 없는 커밋을 놓치지 않음.
- **선행**: T12.

### T31. ID 단위 불변식 검사
- **목적**: series 정합·의존·재사용 통제.
- **충족**: P0-5 / REQ-CG-02 개편.
- **구현**: 한 ID 다중 커밋이면 manifest series로 선언·순서/개수 검증, 의존 순환 검사,
  비연속 분산 시 실패/승인, retired ID 영구 재사용 금지.
- **수용**: series 누락·순서 어긋남·순환·retired 재사용 각각 검출.
- **선행**: T30·T11.

### T32. 최종 상태 불변식 검사
- **목적**: "등록"이 아니라 "생존"에 근접(P0-5).
- **충족**: P0-5 / REQ-CG 신규.
- **구현**: active 패치 순효과 0(적용 후 무변화)이면 실패/retirement, active ID revert는
  상태 전환·ADR 필수, candidate HEAD == replay tree(T22), candidate 변경 시 기존 테스트·승인 무효화.
- **수용**: revert·순효과 0·무효화 누락을 각각 차단.
- **선행**: T22·T31.

### T33. 게이트 명칭·문구 정정
- **목적**: "등록·재적용 완전성 게이트"로 개명, 보장 범위 문서화(P0-5·§11).
- **충족**: P0-5·P0-7.
- **구현**: 산출물·문서에서 "완전성=기능 보장" 표현 제거, §11 표현표 반영.
- **수용**: 보장/미보장 표가 게이트 출력에 포함.
- **선행**: T30~T32.

---

## M4. 경로·민감·부채 게이트 + 영향 분석

### T40. 구현 범위 drift 검사 (방향 C)
- **목적**: 실제 변경 파일 vs 선언(allowed/required) 정합(P0-6).
- **충족**: P0-6 / REQ-CG-03.
- **구현**: CI가 `observed_changed_paths` 생성 → required 미변경/allowed 밖 변경 검출.
  **upgrade_watch는 drift 대상 아님**(편집 안 하므로).
- **수용**: allowed 밖 변경·required 미변경 검출, upgrade_watch 경로는 오탐 없음.
- **선행**: T10·T12.

### T41. 민감 영역·의도 게이트
- **목적**: 민감 경로 접촉·범위 이탈 판정.
- **충족**: 원천 억제·보완책 2 / REQ-GZ-01·02.
- **구현**: 변경파일 × zones glob(`pathspec`) → frozen=block/protected=approval/watched=경고.
  change-intent allowed 밖=approval, forbidden 안=block, intent 부재=fail-closed.
- **수용**: 각 레벨 판정 픽스처 통과.
- **선행**: T13·T03.

### T42. 업그레이드 영향 분석 (upgrade_watch 기반)
- **목적**: 업스트림 변경 ∩ 감시 범위 → 검토 플래그(케이스 D).
- **충족**: P1·케이스 D / REQ-CG 신규.
- **구현**: `git diff --name-only OLD NEW` ∩ (`allowed`∪`upgrade_watch.paths`) + 설정키·의존성 diff 대조 →
  영향 ID·필수 테스트·contract 목록 산출(감사카드에).
- **수용**: 편집 안 한 감시 파일 변경도 해당 ID를 플래그(tenant 케이스), 무관 파일은 제외.
- **선행**: T10·T12·T14·**T93**(유효한 감시 경로 확보 후 영향분석).

### T43. 부채 게이트 (Gate 4) — 단계적 임계치
- **목적**: 코어 수정 과다 억제, 단계적 도입(§9).
- **충족**: Gate 4 / REQ-GD.
- **구현**: 지표 수집(자동적용률·수동해결시간·반복충돌률·hotspot 겹침·의존수·유지기간·제거율).
  라인은 보조 지표. 임계치는 경고→승인→(데이터 후)차단 단계.
- **수용**: 즉시 차단 항목(미등록·담당없음·테스트없음·우회·재현실패·SHA불일치)만 초기 차단.
- **선행**: T13·T30.

---

## M5. 증거 생성기 (선언형 verifier · 구조화 diff)

### T50. 선언형 verifier 엔진
- **목적**: manifest 임의 command 제거, 선언형으로(P0-8).
- **충족**: P0-8 / REQ-GZ 신규.
- **구현**: verifier 타입 세트 구현 — `yaml_value_equals`·`helm_jsonpath_equals`·
  `file_exists_in_image`·`python_import_succeeds`·`api_schema_contains`·`package_version_equals`.
  스크립트 필요 시 allowlist 경로+해시만 참조. shell 문자열 실행 없음.
- **수용**: config/deployment/extension 명세가 선언형 verifier로 존재 검증됨, 임의 명령 불가.
- **선행**: T10.

### T51. 구조화 Evidence Provider — Git/path·API/schema
- **목적**: LLM보다 먼저 도는 결정적 증거(§6 보강3·§8).
- **충족**: 케이스 ②·D / 신규 REQ.
- **구현**: OpenAPI·JSON Schema diff, 공개 인터페이스 diff → 구조화 JSON(감사카드 입력).
- **수용**: 스키마 필드·enum 추가/삭제/변경을 구조화 출력.
- **선행**: T14.

### T52. 구조화 Evidence Provider — Helm/config·dependency/DB·search
- **목적**: 비코드 변경의 결정적 증거.
- **충족**: 케이스 ②·§6 보강3.
- **구현**: Helm values schema·렌더 결과 diff, 환경변수·설정키 diff, dependency lock·SBOM diff,
  DB migration 목록·schema diff, 검색 mapping diff.
- **수용**: 각 대상의 구조 변화가 결정적 JSON으로 산출.
- **선행**: T51.

---

## M6. 테스트 결속 (contract-id · patch-kill · candidate 결속)

### T60. contract-id ↔ 테스트 결속
- **목적**: 업무 불변식과 테스트를 연결(§6 보강1).
- **충족**: P0-7·C-4 / 신규 REQ.
- **구현**: `contracts/*.yaml`의 불변식 ↔ required 테스트 매핑. 릴리스마다 "어떤 불변식이
  어떤 테스트로 입증됐는지" 검증(이름 존재만 아님).
- **수용**: contract에 연결 테스트 없으면 실패, 감사카드에 불변식-테스트 매핑 표시.
- **선행**: T04·T14.

### T61. patch-kill test
- **목적**: 테스트가 커스터마이징 생존을 실제로 입증(§5·C-4).
- **충족**: P0-5·P0-7 / 신규 REQ.
- **구현**: critical/high 패치를 제외한 임시 스택 생성 → 그 ID required 테스트 실행 →
  **적어도 하나는 실패해야** 함. 전부 통과하면 그 테스트는 생존 미입증 → 경고/승인.
- **수용**: 패치 제거 시 테스트가 실패하는 것을 확인, 실패 안 하면 플래그.
- **선행**: T60·T20.

### T62. 테스트-candidate SHA 결속
- **상태(2026-07-25)**: ✅ 결과계약·flaky 판정 구현/단위검증 완료.
  실제 7개 contract suite 실행 결과는 아직 없음.
- **목적**: 시간차 결함 방지(§10.1).
- **충족**: P0(§10.1) / REQ-OR 신규.
- **구현**: 테스트 결과를 candidate SHA·이미지 digest·harness/suite 버전에 결속.
  candidate 변경 시 결과 자동 무효화. 재시도 결과 구분(first/retry/flaky/fail), critical retry-pass=승인.
- **수용**: candidate에 커밋 추가 시 기존 결과 무효, retry-pass가 성공으로 뭉개지지 않음.
- **선행**: T32.

---

## M7. 정책 자기보호 · fast lane · break-glass

### T70. 정책 PR base-정책 평가
- **목적**: 자기 완화 차단(P0-9).
- **충족**: P0-9 / REQ-OR-03.
- **구현**: policy/게이트/CI 경로 변경 PR은 **base branch 정책으로 판정** + 새 정책 별도 시뮬 +
  2인 승인 + 다음 리비전부터 활성. 플랫폼 required check·branch protection 병행 문서화.
- **수용**: 완화된 정책으로 자기 PR을 통과시키려는 시도가 base 정책에서 차단.
- **선행**: T41.

### T71. 변경 유형별 fast lane
- **상태(2026-07-25)**: ✅ config/deployment/extension/core/governance 명시
  라우팅과 혼합 변경 합집합 규칙 구현/단위검증 완료.
- **목적**: 우회 방지 위해 경량 경로 제공(§9).
- **충족**: 운영 부담 / 신규 REQ.
- **구현**: config/deployment=명세·렌더·선언형 verifier·smoke / extension=포함·SDK계약·import·통합 /
  core-patch=전체 게이트 / governance=base 평가·2인.
- **수용**: config 한 줄 변경이 core 전체 게이트를 타지 않음.
- **선행**: T50·T41.

### T72. break-glass 절차
- **상태(2026-07-25)**: ✅ 2인 승인·digest/SHA/policy 결속·만료·허용 gate·통계와
  무결성 gate 비면제 규칙 구현/단위검증 완료. 조직 실제 승인 체계 연동은 남음.
- **목적**: 긴급 예외의 공식 경로(§9).
- **충족**: 운영 리스크 / 신규 REQ.
- **구현**: 긴급 티켓·2인 승인·대상/만료·허용 게이트 명시·산출물 저장·사후 정상 재수행·통계.
- **수용**: 예외가 기록·만료·사후 재검증되며 통계로 집계.
- **선행**: T70.

---

## M8. LLM Upgrade Impact Memo (보조)

### T80. 릴리스별 Impact Memo 생성기
- **상태(2026-07-25)**: ✅ strict schema·근거 결속·판정/명령 필드 금지·금지 문구와
  T81 품질지표 구현/단위검증 완료. 실제 릴리스 품질 데이터는 아직 없음.
- **목적**: 지속형 위키 이전, 릴리스별 Memo로 안전 시작(§7).
- **충족**: §7 / P0-7.
- **구현**: 읽기 전용(shell·git write·PR·네트워크 없음). 입력=diff·릴리스노트·명세·증거 provider 출력.
  출력=감사카드 `llm_suggestions`(사실/추론/미확인 분리, 모든 주장에 근거 첨부).
  "영향 없음" 금지→"확인된 후보 없음". snapshot SHA·model/prompt version 기록.
- **수용**: pass 부여 불가, 근거 없는 주장 0 목표, upgrade_watch 심볼 범위로 케이스 D 후보 생성.
- **선행**: T42·T51·T52.

### T81. Memo 품질 지표
- **목적**: 위키 확장 판단용 데이터(§7).
- **충족**: §7.
- **구현**: recall(알려진 영향 ID)·false positive·근거없음 비율·채택률·검토시간 절감 측정.
- **수용**: 지표가 릴리스마다 기록됨.
- **선행**: T80.

---

## M9. 업그레이드 검증 · 릴리스 승격 · 반입

### T90. 업그레이드 테스트 오케스트레이션
- **상태(2026-07-25)**: 🟡 12단계 executor-neutral 결과계약과 candidate 결속은
  구현/단위검증 완료. Docker·DB·검색·ingestion 실제 실행은 미수행.
- **목적**: 빌드 성공 ≠ 업그레이드 성공을 실측(§6 보강2).
- **충족**: P2·P5 / REQ(업그레이드 계층).
- **구현**: 운영 DB 복원→migration→건수 대사→reindex→ingestion→rollback 훈련.
  **구·신 버전 차등 테스트**(인증·권한·API·관계·검색·ingestion 결과 비교).
- **수용**: 관계·의미 손상을 건수 대사만이 아닌 차등 비교로 검출.
- **선행**: T62.

### T91. 릴리스 승격 — 동일 digest
- **상태(2026-07-25)**: ✅ release-lock·동일 digest·재빌드 금지 판정 구현/단위검증
  완료. 실제 artifact registry 승격은 미수행.
- **목적**: 검증된 것과 배포되는 것의 동일성(§10.1).
- **충족**: P4 / REQ(반입).
- **구현**: candidate를 재빌드·복사하지 않고 **검증된 동일 commit SHA·artifact digest 승격**.
  release-lock에 candidate SHA·core/platform SHA·policy/harness/suite version·test digest·image/helm digest·approval IDs 결속.
- **수용**: 승격 산출물의 digest가 검증 시점과 일치, 재빌드 없음.
- **선행**: T90·T22.

### T92. retirement 흐름
- **상태(2026-07-25)**: ✅ 공식 대체·ADR·contract/removal 증거·2인 승인과
  registry/manifest active→retired 전환 구현/단위검증 완료.
- **목적**: 업스트림이 패치를 흡수한 경우 처리(§10.3).
- **충족**: 패치 부채 / REQ.
- **구현**: 공식 대체 확인→요구 충족 테스트→제거 상태 회귀→manifest `retired`→대체 commit·ADR 기록→active set 제외.
  빈 placeholder 커밋 강제 유지 금지.
- **수용**: empty가 된 패치가 강제 유지되지 않고 retirement로 전환.
- **선행**: T31.

### T93. 민감·감시 경로 drift 검사
- **목적**: 정책 노후화 검출(§10.5·C-2).
- **충족**: 운영 리스크 / REQ.
- **구현**: 민감 패턴·upgrade_watch glob이 신버전에서 ≥1 매칭하는지, 이전 매칭 경로 소멸,
  신규 최상위 모듈 미분류, 지나치게 넓은 `**` 검출.
- **수용**: 리팩터로 0-매칭이 된 패턴을 검출.
- **선행**: T03·T05. (T42는 **후행** — T93이 유효 감시경로를 먼저 확정하고 T42가 그 위에서 영향분석. 이전 'T42 선행' 표기는 순환 오류였으므로 제거.)

### T94. 내부망 반입·재검증
- **상태(2026-07-25)**: 🟡 inventory 해시·release-lock 결속·안전 경로·필수
  오프라인 서명 verifier 계약은 구현/단위검증 완료. 실제 bundle/키/내부망
  재검증은 미수행.
- **목적**: 외부망=내부망 산출물 동일성(P4).
- **충족**: P4 / REQ(반입).
- **구현**: git bundle·이미지 digest·helm·설정 해시·SHA256SUMS·서명 + 내부망 재검증 스크립트.
  서명 필수, 생성 순서(해시→서명) 고정.
- **수용**: 내부망에서 동일 release-lock 재현·무결성 검증.
- **선행**: T91.

---

## 3. 태스크 → 충족 대상 추적표 (요약)

| 태스크 | 주 충족 | 관련 P0 |
|---|---|---|
| T10 스키마 분리 | 경로 역할 분리 | P0-6 |
| T11 patch-lock | 재현성·정본 | P0-1·§10.2 |
| T12 git 프리미티브 | 결정적 파싱 | P0-1·P0-5·§8 |
| T13 verdict 엔진 | 집계·차단 | P0-3·P0-4 |
| T20/21 재적용 2-모드 | 충돌 해결 | P0-2 |
| T22 replay | 재현성 | P0-5·C-5 |
| T30~33 완전성 불변식 | 등록·재적용 | P0-5·P0-7 |
| T40 drift | 구현 범위 | P0-6 |
| T42 영향분석 | 케이스 D | P0-6 |
| T50 선언형 verifier | 임의실행 제거 | P0-8 |
| T60/61 contract·patch-kill | 생존 입증 | P0-5·P0-7·C-4 |
| T62 SHA 결속 | 시간차 | §10.1 |
| T70 정책 base 평가 | 자기보호 | P0-9 |
| T80 LLM Memo | 보조 | P0-7·§7 |
| T91 digest 승격 | 재현성 | §10.1 |

---

## 4. 개발 착수 규칙 (2차 검토 반영)

1. **즉시 착수 가능**: T12(git 프리미티브)·T13(verdict 엔진).
2. **T10·T11 동결 전 필수 3조건**(2차 검토 E 결론 = SRS 부칙 A):
   ① 결과 계약을 CI 경계까지 닫기(A-1: 불일치=analysis_error·원자적 생성·
   canonical digest·attestation 분리) ② patch-lock·lineage·동시성 모델
   (A-2: source/application lock 분리·trailer 자동 각인·object 보존·직렬화·
   상태 분류) ③ 스키마 의미 기반(A-3: T05 path-ownership·required⊆allowed·
   contract 정본·verifier sandbox).
3. **재적용 전에 소스 검증**: T30·T31은 T20보다 먼저(M1.5 preflight).
4. 각 태스크는 완료 시 **실패 픽스처 + 재현성(canonical payload digest 기준,
   부칙 A-1.3) + 뮤테이션 테스트**로 증명.
5. 게이트는 스스로에게도 적용한다(dogfooding, T70 최소 기능을 조기 가동).
6. "완전성" 산출물·문서는 **등록·재적용과 기능 의미를 항상 분리**해 표기.
7. 첫 운영 릴리스는 **Production-upgrade MVP**(T90·T91·T94 포함)를 완료해야
   한다 — candidate 통제만으로 "끝까지 통제했다"고 말하지 않는다.
