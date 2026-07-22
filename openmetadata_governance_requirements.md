# OpenMetadata 커스터마이징 거버넌스 하네스 — 요구사항 정의서 (SRS)

> **문서 목적**
> 개발 착수 전, 우리가 만들 "언어 무관 거버넌스 스파인"의 요구사항을 확정한다.
> 각 요구사항이 어떤 **문제**를 풀고, 어떤 **보완책·게이트**를 충족하며,
> **어떤 코드·어떤 방법**으로 구현되는지를 개발 가능한 수준으로 정의한다.
>
> **선행 문서**
> - 전략·근거: `openmetadata_strategy_briefing.md`
> - 상세 설계: `openmetadata_upstream_customization_design.md`
> - 참조 구현: `easyseop/ai-change-governance-harness` (개념·구조 참조, 코드 재사용은 선택)
>
> **상태:** Draft v0.1 · GPT 검토 반영 진행 중

> ⚠ **정정 안내 (GPT 검토 반영)**
>
> **정정 완료 (P0-a — 본문에 정정본 반영됨):**
> - ✅ **§1.4 + REQ-OR-01/02**: severity rank 집계, 분석실패=차단, 4-상태 결과 계약 (P0-3·4)
> - ✅ **REQ-RA-01/02/03**: 충돌 탐지/해결 2-모드, 해결본의 patch-lock 리비전 고정 (P0-2)
> - ✅ **REQ-EV-01**: 선언형 verifier — `verification.command` 폐기 (P0-8)
>
> **정정 완료 (P0-b — 본문에 정정본 반영됨):**
> - ✅ **REQ-CB-02**: range-diff 기계 파싱 제거 → patch-lock+trailer+raw diff 판정, range-diff는 리뷰용 (P0-1)
> - ✅ **REQ-MF-01**: `affected_paths` 폐기 → allowed/required_changed_paths + upgrade_watch 분리 (P0-6)
> - ✅ **REQ-CG-01~05**: "등록·재적용 완전성"으로 축소 + 커밋/ID·series/최종상태 불변식 (P0-5)
>
> P0 9건 전부 SRS 본문에 반영 완료. P1 항목(patch-lock 상세·patch-kill·evidence
> provider·break-glass 등)은 Build Plan(M5~M9)을 따른다.
>
> **2차 검토(GPT) 반영 — 부칙 A 추가:**
> 6개 정정 영역의 2차 결함(결과 계약 CI 경계·lock/lineage/동시성·스키마 의미
> 기반)과 신규 발견 D-1~D-9를 **부칙 A**로 반영. 본문과 충돌 시 부칙 우선.
> T12·T13은 즉시 개발 가능, T10·T11은 부칙 A 반영 후 동결(2차 검토 E 결론).
>
> 정정 근거·상세: `openmetadata_review_response.md`
> 정정 반영 개발 순서: `openmetadata_build_plan.md`
> 검증기 전체 목록: `openmetadata_verifier_catalog.md`

---

## 1. 개요

### 1.1 이 하네스가 하는 일 (한 줄)

> 새 OpenMetadata 공식 버전 위에 행내 수정을 다시 적용할 때,
> **수정 누락·선언 범위 이탈·민감 영역 접촉·수정 과다**를 **코드 내부를 열어보지 않고**
> (변경 이력·파일 위치·선언 파일만으로) 자동 판정해 배포 전 검사로 막는다.

### 1.0 먼저 — 이 문서의 용어

경영진·비개발자도 읽을 수 있도록 용어를 먼저 정리한다.

**우리가 정의한 개념**

| 용어 | 쉬운 설명 |
|---|---|
| 거버넌스 하네스 | 이 문서가 정의하는 검사 도구 전체. 위험한 변경만 사람에게 올린다 |
| 행내 수정 (customization) | 공식 OpenMetadata에 우리가 더한 변경 1건. 번호 `BANK-OM-xxx`로 식별 |
| 재적용 (reapply) | 공식 새 버전이 나오면 우리 수정들을 그 위에 다시 얹는 작업 |
| 명세 (manifest) | 수정 1건의 신상명세서(파일 하나). 목적·담당·영향 범위·테스트·제거 조건 |
| 검사 관문 (gate) | 변경을 통과/차단/승인필요 중 하나로 자동 판정하는 검사 단계 |
| 감사카드 (evidence) | 여러 관문의 판정을 한 장으로 정리한 산출물. 사람은 이것부터 본다 |
| 공통 검사 엔진 (spine) | 프로그래밍 언어와 무관하게 모든 변경을 검사하는 핵심부 |
| 패치·패치 묶음 | 수정 하나(패치)와 그것들을 공식 버전 위에 쌓은 묶음 |
| 수정 과다 (patch debt) | 원본을 고친 수정이 너무 쌓인 상태. 개수에 상한을 둔다 |

**기술 용어 (버전 관리·개발)**

| 용어 | 쉬운 설명 |
|---|---|
| 커밋 (commit) | 변경 한 묶음을 기록한 단위. 규칙: **커밋 하나 = ID 하나**, ID 하나는 짧은 순서형 commit series 허용 |
| 식별 꼬리표 (trailer) | 커밋 기록 끝에 붙이는 식별표. `Customization-ID`를 넣음 |
| 골라 재적용 (cherry-pick) | 특정 커밋만 골라 새 공식 버전 위에 다시 적용 |
| 묶음 비교 (range-diff) | 이전/새 버전의 패치 묶음을 나란히 비교 |
| 선언-실제 어긋남 (drift) | 명세의 영향 범위와 실제 바뀐 파일이 벌어진 상태 |
| 경로 패턴 (glob) | `**/auth/**`처럼 파일 위치를 지정하는 규칙 |
| 자동 검사 (CI) | 코드가 바뀔 때마다 사람 없이 자동 검사를 돌리는 시스템 |
| 안전 차단 (fail-closed) | 애매하거나 검사 실패 시 통과가 아니라 막는 쪽으로 처리 |
| 판정 신호 (verdict) | 검사 결과 4상태 — 통과·승인필요·차단·검증실패(차단 취급). 종료코드 0/2/1/3으로 변환(§1.4) |
| 선언 파일 (YAML) | 사람이 읽기 쉬운 설정·명세 파일 형식 |

### 1.2 언어 무관 원칙 (핵심 설계 결정)

이 하네스의 모든 판정은 **git 메타데이터 + 파일 경로 + YAML**만 입력으로 쓴다.
소스 파일을 열어 문법을 해석하지 않으므로 대상이 Java·Python·TSX·SQL·YAML 무엇이든
동일 로직으로 동작한다. 언어별 딥 분석(능력·콜그래프)은 **본 정의서 범위 밖**이며,
필요 시 후속 부가층으로 분리한다(§9 비범위).

### 1.3 용어

| 용어 | 정의 |
|---|---|
| 커스터마이징 | 공식 OpenMetadata에 대한 행내 변경 1건. 불변 ID `BANK-OM-xxx`로 식별 |
| 명세(Manifest) | 커스터마이징 1건당 YAML 1개. 목적·영향경로·테스트·담당·제거조건 기록 |
| core-patch | 공식 원본 소스 파일 자체를 수정하는 커스터마이징 유형 |
| 패치 스택 | 공식 태그 위에 순서대로 쌓인 커스터마이징 커밋들 |
| 게이트 | 통과(0)/차단(1)/승인필요(2)를 결정적으로 판정하는 검사 단위 |
| 감사카드 | 게이트 결과를 집계한 기계·사람 판독용 산출물(YAML) |
| 스파인 | 언어 무관 판정 코어 (경로·git·YAML만 사용) |

### 1.4 판정 계약 (전 게이트 공통) — 정정본 (P0-3·P0-4 반영)

판정은 **내부 심각도(severity)** 와 **외부 종료코드(exit)** 를 분리한다.
집계는 심각도 rank로 하고, 종료코드 변환은 맨 마지막에 한 번만 한다.

```
내부 심각도 (rank 오름차순):
  pass(0) < approval(1) < block(2) < analysis_error(3)

외부 exit code (변환표 — 순서가 rank와 다름에 주의):
  pass           → 0   통과
  block          → 1   차단 (사람이 풀기 전 진행 불가)
  approval       → 2   승인필요 (지정 승인자 없이는 진행 불가)
  analysis_error → 3   검증 미수행 (차단으로 취급)
```

핵심 규칙:

1. **집계는 exit code의 `max()`가 아니라 severity rank의 `max()`로 한다.**
   exit code로 `max()`하면 `2(approval) > 1(block)`이 되어 차단이 승인필요로
   격하되는 버그가 생긴다(P0-3).
2. **analysis_error는 승인으로 우회할 수 없다.** 검사기가 고장 난 것은
   "위험을 발견"한 게 아니라 "검증을 수행하지 못한" 상태이므로 차단이다(P0-4).
   긴급 시에는 별도 break-glass 절차만 허용한다.
3. 게이트 결과는 exit code와 **별도로** 정본 결과 파일(`acgh-result.yaml`,
   REQ-OR-02)로 산출하며, CI required-check는 이 파일을 읽는다.
   (CI가 exit≠0을 일괄 fail로 뭉개면 1과 2가 구분되지 않기 때문)

---

## 2. 문제 정의 (무엇을 푸는가)

설계서 1장의 문제 중 **이 하네스가 직접 푸는 것**과 **다른 계층이 푸는 것**을 구분한다.

| # | 문제 | 이 하네스가 | 
|---|---|---|
| P1 | 새 버전 적용 시 커스터마이징 누락 | ✅ 직접 (완전성 게이트) |
| P2 | 충돌 없어도 논리적으로 동작 안 함 | △ 간접 (영향 커스터마이징의 필수테스트를 *촉발*, 테스트 실행은 별도) |
| P3 | 변경 이유·요구사항·테스트 연결 추적 불가 | ✅ 직접 (명세 + trailer) |
| P4 | 외부망-내부망 산출물 불일치 | ✗ 비범위 (release-lock·서명 계층) |
| P5 | DB·검색·ingestion·인증 전 계층 호환성 | ✗ 비범위 (업그레이드 테스트 계층) |
| P6 | 담당자 이탈로 목적·범위 소실 | ✅ 직접 (명세 owner·retirement) |
| P7 | LLM이 배포 가능을 확정 보장 못함 | ✅ 직접 (전 판정 결정적, LLM 불개입) |

> 이 하네스는 **P1·P3·P6·P7을 직접** 보장하고, **P2·P5는 "무엇을 테스트해야 하는지"를
> 산출**하되 테스트 실행 자체는 하지 않는다. **P4는 범위 밖**이다.

---

## 3. 목표와 비목표

### 3.1 목표
- G1. 커스터마이징 누락을 **사람 기억이 아니라 CI 실패**로 검출한다.
- G2. 모든 판정을 **결정적**으로 한다(같은 입력 → 같은 판정, LLM 불개입).
- G3. **언어 무관**하게 동작한다(단일 로직으로 전 파일 유형 통제).
- G4. 판정 근거를 **감사카드**로 남겨 사람이 위험 변경만 정독하게 한다.
- G5. 게이트 자신을 무력화하는 변경을 **자기보호**로 승인 대상화한다.

### 3.2 비목표 (본 정의서 범위 밖)
- 언어별 딥 분석(신규 능력·콜그래프·간접영향)
- DB 마이그레이션·재색인·업그레이드 E2E 테스트 실행
- 반입 산출물 무결성(SBOM·서명·digest)
- UI 렌더링·기능 검증

---

## 4. 전체 아키텍처

```
[입력]                         [스파인 게이트]                    [출력]
change-intent.yaml ─┐
customizations/*.yaml ├─▶ G-CG 완전성(방향 A/B/C) ─┐
sensitive-zones.yaml ─┤     G-GZ 민감경로·의도      ├─▶ 감사카드(change-evidence.yaml)
patch-lock ───────────┤     G-GD 부채 상한          │   + 승인자 라우팅
git (base..head) ─────┘     G-CB 정본(lock 대조)     │   + verdict 4상태(§1.4)
                            G-RA 재적용(cherry-pick) ┘
                            (G-RR rerere 검출 — 기본 비활성)
```

전 게이트는 `git`·경로·YAML만 읽는다. Python 3 + 표준 git CLI 외 의존성 최소화.

---

## 5. 기능 요구사항

각 요구사항: **[충족 대상]** · 목적 · 입력→출력 · **구현 방법(코드/방법)** · 수용 기준.

### 5.1 명세 시스템 (MF)

#### REQ-MF-01 · 명세 스키마 검증 — 정정본 (P0-6 반영)
- **충족**: P3·P6 기반, Gate 2의 전제, P0-6(경로 역할 분리)
- **목적**: 커스터마이징 명세가 필수 필드·상태·ID 규칙을 지키는지 검증
- **정정 배경**: 초안의 `affected_paths` 하나가 "실제 변경 범위"와 "업그레이드
  감시 범위"를 동시에 맡았다. 두 범위는 일반적으로 다르다(SSO 패치는
  AuthenticationFilter만 수정하지만, 감시 대상은 인증 DTO·설정 스키마·JWT
  의존성까지). 하나로 쓰면 drift 오탐 또는 감시 협소가 발생한다(P0-6).
  **`affected_paths`는 폐기**하고 역할별 필드로 분리한다.
- **입력→출력**: `customizations/*.yaml` → 위반 목록(있으면 block)
- **구현 방법**:
  - 경로 필드 스키마 (역할 분리):
    ```yaml
    implementation:
      allowed_changed_paths:      # 이 패치가 변경해도 되는 파일 (상한)
        - "openmetadata-service/**/AuthenticationFilter.java"
      required_changed_paths:     # 반드시 변경돼야 하는 파일 (하한)
        - "openmetadata-service/**/AuthenticationFilter.java"
      patch_series:               # 1 ID = 순서형 커밋 series (P0-5)
        ordered: true

    upgrade_watch:                # 업스트림 변경 감시 (편집하지 않는 의존 대상)
      paths:
        - "openmetadata-service/**/authentication/**"
        - "openmetadata-spec/**/user*.json"
      configuration_keys: ["BANK_SSO_USER_CLAIM"]
      dependencies: ["jwt-library"]
      contracts: ["AUTH-IDENTITY-SCOPE"]   # 업무 불변식 ID (테스트 결속용)
    ```
  - `schemas/customization.schema.json`(2020-12) + `jsonschema` 검증
  - 코드 규칙: 중복 ID / `core-patch`인데 `required_changed_paths` 없음 /
    `active`인데 `retirement.target`·`requirement.id` 없음 /
    **`affected_paths`·`verification.command` 필드 존재 시 스키마 거부**(구버전 차단)
- **수용 기준**: 필수 필드 누락·잘못된 상태값·중복 ID·ID 패턴(`^BANK-OM-[0-9]{3,}$`)
  위반을 각각 탐지하고, 구버전 필드(`affected_paths`)를 쓴 명세를 거부하는
  픽스처 테스트가 존재하고 통과한다

#### REQ-MF-02 · 명세 로딩 API
- **충족**: 하위 게이트 공통 기반
- **목적**: 게이트들이 명세를 일관되게 읽는 단일 진입점
- **입력→출력**: 디렉터리 경로 → `{id: 명세dict}` (중복 ID면 예외)
- **구현 방법**: Python 모듈 `spine/manifest.py`, `PyYAML safe_load`, `id` 키로 dict 구성
- **수용 기준**: 두 저장소(core/platform)의 명세를 병합 로딩하고 중복 ID를 예외로 던진다

---

### 5.2 재적용 자동화 (RA) — 정정본 (P0-2 반영)

> **정정 배경**: 초안은 "충돌 시 리포트 후 `--abort`, 사람이 해결하고 재실행"
> 이었다. 그러나 `--abort`하면 충돌 상태가 사라져 **사람이 해결할 작업 트리가
> 남지 않는다**. 재실행하면 같은 충돌이 그대로 재현될 뿐이다. 따라서 재적용을
> **탐지 모드**와 **해결 모드**의 2-모드로 분리한다.

#### REQ-RA-01 · 재적용 — CI 탐지 모드 (detect)
- **충족**: **Gate 1(재적용)**, P0-2, P1
- **목적**: 본 작업 트리를 오염시키지 않고 "충돌이 있는가, 어디서 나는가"만
  안전하게 탐지한다. CI에서 반복 실행되는 모드.
- **입력→출력**: patch-lock(ID별 `source_commits` 고정 SHA 목록, REQ-CB 계열)
  + 대상 태그 → `reapply-report.json`, severity pass/block
- **구현 방법**:
  ```bash
  # 1. 임시 worktree 생성 (본 트리 격리)
  git worktree add --detach "$TMP_WT" "$TARGET_TAG"
  # 2. patch-lock 순서대로 재적용
  for sha in $(locked_source_commits); do
      git -C "$TMP_WT" cherry-pick "$sha" || {
          collect_conflict_files "$TMP_WT" >> report   # ID·파일·hunk 수 수집
          git -C "$TMP_WT" cherry-pick --abort
          break
      }
  done
  # 3. 임시 worktree 폐기 (성공/실패 무관)
  git worktree remove --force "$TMP_WT"
  ```
  - 커밋→ID 매핑은 `git log --format='%(trailers:key=Customization-ID,valueonly)'`
    (커밋 경계 유지, 본문 정규식 금지)
  - report 스키마: `{target_tag, lock_sha, results:[{id, source_commit,
    status: applied|conflict|skipped, conflict_files:[], resolved_by: null}]}`
- **수용 기준**: (a) 무충돌 스택 → 전량 적용 확인 후 pass, 임시 worktree 잔존 0
  (b) 충돌 → 해당 ID·파일이 report에 남고 block, **본 작업 트리는 시작 전과
  동일**(오염 0) (c) 동일 입력 재실행 시 동일 report(결정성)

#### REQ-RA-02 · 재적용 — 담당자 해결 모드 (resolve)
- **충족**: P0-2, **보완책 2(격리)**, P1
- **목적**: 충돌을 사람이 실제로 해결할 수 있는 작업 공간을 제공하고,
  해결 결과를 **재현 가능한 새 패치 리비전으로 고정**한다.
- **입력→출력**: 탐지 모드의 report + 담당자 작업 → 갱신된 patch-lock
  (새 `source_commits` + revision 증가) + Resolution 기록
- **구현 방법**:
  1. **전용 worktree**를 만들고 충돌 상태를 **유지**한 채 담당자에게 전달
     (`git worktree add`, cherry-pick 충돌 지점에서 정지 — abort하지 않음)
  2. 담당자가 충돌 해결 → `git cherry-pick --continue`
  3. 해결된 커밋에 trailer 각인:
     ```
     Customization-ID: BANK-OM-001
     Source-Commit: <원본 패치 SHA>
     Patch-Revision: <n+1>
     Resolution-Record: docs/upgrade/<ver>/conflicts.json#<항목>
     ```
  4. 해결 커밋 SHA를 patch-lock의 새 `source_commits`로 등록(revision 증가)
  5. **깨끗한 환경에서 전체 스택을 처음부터 재생**하여 검증(clean-room replay,
     REQ 신규 — 해결본 포함 재현 확인). 이후 이 해결본이 다음 버전의 정본이 됨
- **수용 기준**: (a) 담당자가 충돌 상태의 실제 작업 트리를 받는다
  (b) 해결 결과가 patch-lock 리비전으로 고정되어, 같은 lock으로 재적용하면
  **사람 개입 없이 동일 결과가 재현**된다 (c) 해결 커밋에 위 trailer 4종이
  모두 존재하지 않으면 완전성 게이트가 block

#### REQ-RA-03 · 충돌 해결 기록
- **충족**: **보완책 2(기록)**, P3
- **목적**: 충돌 해결의 배경·결정을 구조화 기록(강제 산출물)
- **입력→출력**: 충돌 발생 ID → `docs/upgrade/<version>/conflicts.json` 항목
- **구현 방법**: 해결 모드(RA-02)가 충돌 시 템플릿 항목(ID·충돌파일·업스트림
  변경사유 칸·해결유형 enum[유지|공식대체|재작성])을 생성, 사람이 채움.
  `Resolution-Record` trailer가 이 항목을 가리켜야 함
- **수용 기준**: 충돌 1건당 항목이 자동 생성되고, 필수 칸 미기입 또는
  trailer-항목 불일치 시 후속 게이트가 approval로 닫는다

---

### 5.3 등록·재적용 완전성 게이트 (CG) — 정정본 (P0-5 반영)

> **정정 배경 및 보장 범위**: 초안의 "명세 ID 집합 = 커밋 ID 집합" 비교는
> **등록된 ID가 이력에 존재함**만 증명한다. revert로 순효과가 0이 되거나,
> 빈 커밋만 있거나, 충돌 해결에서 로직이 빠져도 집합은 일치할 수 있다(P0-5).
> 따라서 (1) 게이트 이름을 "등록·재적용 완전성"으로 축소하고, (2) 집합 비교를
> **커밋 경계 유지 파싱 + 커밋/ID/최종상태 3단 불변식**으로 강화한다.
> 기능 의미·로직 생존의 최종 입증은 테스트 계층(contract·patch-kill)이 담당한다.

| 이 게이트가 보장 | 보장하지 않음 (담당 계층) |
|---|---|
| 등록된 ID가 규칙대로 이력에 재적용됨 | 로직이 최종 상태에 살아 있음 (최종상태 불변식이 부분 보강, 입증은 테스트) |

#### REQ-CG-01 · 커밋 단위 불변식 (방향 A 확장)
- **충족**: **Gate 2**, P0-5, P1·P3
- **목적**: 코어를 건드린 모든 커밋이 등록 규칙을 지키는지 **커밋 경계에서** 검증
- **입력→출력**: `git <base>..HEAD` + 명세 → 위반 목록(커밋 SHA별), verdict
- **구현 방법**:
  - **커밋별로** 파싱(집합으로 축약 금지 — ID 없는 커밋을 놓치는 원인):
    `git log --format='%H%x00%(trailers:key=Customization-ID,valueonly)%x00...' -z`
  - 불변식: 업스트림 원본 경로를 건드린 커밋은 **정확히 1개 ID** /
    ID 없는 코어 커밋 → block / 한 커밋에 여러 ID → block /
    merge commit → block / 빈 커밋 → block /
    미등록 ID·`retired` ID 사용 → block /
    core 변경과 governance-only 변경 혼합 → block
    (governance 커밋은 `Change-Type: governance` trailer로 분리)
- **수용 기준**: 위 7개 위반 각각을 잡는 픽스처 통과. 특히 "ID 있는 커밋들
  사이에 ID 없는 커밋이 끼어 있는" 픽스처에서 그 커밋을 SHA로 지목한다

#### REQ-CG-02 · ID·series 불변식 (방향 B 확장)
- **충족**: **Gate 2**, P0-5, P1
- **목적**: 모든 active/deprecated core-patch ID가 스택에 **선언된 series 그대로**
  실재하는지 검증
- **입력→출력**: 명세(patch_series) + 스택 커밋 목록 → 누락·불일치 목록, verdict
- **구현 방법**:
  - 존재: `active_core_patch_ids − stack_ids` 차집합 → 누락 block
  - series: 한 ID가 여러 커밋이면 명세 선언과 **순서·개수** 일치 검증,
    비연속 분산(다른 ID 커밋이 series 사이에 끼어듦) → approval,
    의존 관계(`depends_on`) 순환 → block, retired ID 영구 재사용 금지
- **수용 기준**: active 1건 제거 → 누락 검출 / series 3커밋 중 2개만 적용 →
  불일치 검출 / 순환 의존 → block 픽스처 통과

#### REQ-CG-03 · 구현 범위 drift (방향 C — allowed/required 기준)
- **충족**: **Gate 2**, P0-6, P1
- **목적**: 패치의 실제 변경 파일이 선언 범위와 어긋나는지 검출
- **입력→출력**: 커밋 SHA들 + 명세 → drift 목록, verdict
- **구현 방법**:
  - 실제 변경: `git diff-tree --no-commit-id --name-only -r -z <sha>` 합산
    → `observed_changed_paths` 생성(감사카드 기록)
  - `observed ⊄ allowed_changed_paths` → 선언 밖 변경, block(또는 approval)
  - `required_changed_paths` 중 observed에 없는 패턴 → 필수 미변경, block
  - **`upgrade_watch.paths`는 drift 검사에서 제외** — 감시 대상이지 변경
    선언이 아니므로(P0-6 오탐 방지 핵심)
- **수용 기준**: allowed 밖 수정·required 미변경을 각각 잡고, upgrade_watch에만
  있는 경로를 패치가 수정하지 않아도 **오탐 0**인 픽스처 통과

#### REQ-CG-04 · 필수 테스트 존재 검증
- **충족**: **Gate 2**, P2(촉발)
- **목적**: `active` 명세의 `tests.required`·`upgrade_watch.contracts`가
  테스트 카탈로그·contract 정의에 실재하는지 검증
- **입력→출력**: 명세 + `test-catalog/*.yaml` + `contracts/*.yaml`
  → 미연결 목록, verdict
- **구현 방법**: test ID 집합 ⊆ 카탈로그 / contract ID ⊆ contract 정의 /
  contract에 연결된 required_tests 존재 — 3중 포함 검사
- **수용 기준**: 카탈로그에 없는 test ID, 정의 없는 contract를 각각 실패시킨다

#### REQ-CG-05 · 최종 상태 불변식 (신규)
- **충족**: P0-5 ("등록 ≠ 생존" 보강)
- **목적**: 이력엔 있으나 최종 결과물에서 사라진 패치를 검출
- **입력→출력**: candidate 브랜치 + patch-lock → 위반 목록, verdict
- **구현 방법**:
  - **순효과 검사**: ID별 series 전체의 누적 diff가 비어 있으면(뒤 커밋이
    revert·덮어씀) → block 또는 retirement 절차 요구
  - active ID를 revert하는 커밋 → manifest 상태 전환 + ADR 없으면 block
  - candidate HEAD tree == clean-room replay tree (REQ-RA-02의 재생 검증과 결속)
  - candidate에 커밋이 추가되면 기존 테스트·승인 결과 무효화 플래그
- **수용 기준**: "패치 커밋 + 그것을 되돌리는 커밋"이 함께 있는 픽스처에서
  집합 비교는 통과하더라도 이 게이트가 순효과 0을 잡는다

---

### 5.4 민감 경로·의도 게이트 (GZ) — 스파인 코어

#### REQ-GZ-01 · 민감 경로 충돌 판정
- **충족**: **보완책 3(원천 억제) 집행**, P1
- **목적**: diff가 코어 민감 경로(frozen/protected/watched)를 건드렸는지 판정
- **입력→출력**: `git diff --name-only <base>..<head>` + `sensitive-zones.yaml`
  → 접촉 zone 목록 + level, verdict(pass/approval/block — §1.4)
- **구현 방법**:
  - 변경파일 목록 × zones 경로 패턴 glob 매칭(`pathspec`)
  - `frozen` 접촉 → 차단(1) / `protected` → 승인필요(2) / `watched` → 경고·기록(0)
  - zone에 안 걸리는 경로는 free(0)
- **수용 기준**: frozen/protected/watched 각 경로 접촉이 각각 1/2/0을 내고, 무관 경로는 0

#### REQ-GZ-02 · 변경 의도 범위 판정
- **충족**: **보완책 2**(범위 격리), P1·P3
- **목적**: 실제 diff가 선언 의도(`allowed`/`forbidden`) 안에 머물렀는지 판정
- **입력→출력**: diff + `change-intent.yaml` → 범위이탈 목록, verdict(§1.4)
- **구현 방법**:
  - `allowed_paths` 밖 파일 변경 → scope-creep(승인필요 2)
  - `forbidden_paths` 안 변경 → 차단(1)
  - `change-intent.yaml` 부재 → fail-closed(의도 선언 강제)
  - 스키마: `change_intent:` 아래 중첩 필수(top-level 배치 시 빈 선언 오독 방지)
- **수용 기준**: allowed 밖=2, forbidden 안=1, intent 파일 부재=차단, 스키마 오배치 감지

#### REQ-GZ-03 · 패치 생존성(expected_paths)
- **충족**: **보완책 1·2**, **P1(핵심)**
- **목적**: 반드시 나타나야 할 커스터마이징 경로가 diff에 실제로 존재하는지 검증
- **입력→출력**: diff + `change-intent.expected_paths` → 누락 패턴, exit 0/2
- **구현 방법**: 각 expected 패턴에 매칭되는 변경파일이 하나도 없으면 패치 유실
  가능성으로 승인필요(2), 카드 `intent_check.missing_expected`에 기록.
  리터럴 경로 권장(glob은 하위 1건만 바뀌어도 충족되는 거친 보증)
- **수용 기준**: 선언한 필수 경로가 diff에 없으면 2로 닫고 누락 패턴을 카드에 남긴다

#### REQ-GZ-04 · 감사카드 생성 + 승인자 라우팅
- **충족**: **G4**, **보완책 3**(승인 라우팅)
- **목적**: 위 판정을 집계한 감사카드와 필요한 승인자를 산출
- **입력→출력**: 게이트 결과들 + `approval-routing.yaml` → `change-evidence.yaml` + 최종 exit
- **구현 방법**:
  - 카드 스키마 `templates/change-evidence.template.yaml`
  - zone의 `required_approval` + criticality → routing 규칙으로 승인자 결정
  - 최종 판정 = severity rank 집계(REQ-OR-01의 `SEVERITY_RANK` 사용,
    exit code `max()` 금지 — P0-3)
  - 기본 출력 경로 주의: 대상 repo 밖 또는 `.gitignore` 등록(다음 diff 오염 방지)
- **수용 기준**: 3개 게이트 조합 결과가 하나의 카드로 집계되고, protected 접촉 시
  해당 승인자가 카드에 명시된다

#### REQ-EV-01 · 선언형 verifier — 정정본 (P0-8 반영)
- **충족**: P0-8(임의 코드 실행 차단), core-patch 외 유형(§9.7)의 존재 검증
- **목적**: config·deployment·extension 커스터마이징이 실제 릴리스에 반영됐는지를
  검증하되, **manifest에 임의 shell 명령을 넣는 통로를 원천 봉쇄**한다
- **정정 배경**: 초안(설계서 9.7절)은 `verification.command`에 shell 문자열을
  선언하고 CI가 실행하는 방식이었다. 이러면 manifest를 수정할 수 있는 누구나
  **CI 권한으로 임의 코드를 실행**할 수 있다(P0-8). command 필드는 폐기한다
- **입력→출력**: 명세의 `verification` 블록 + 대상 산출물(렌더링 결과·이미지 등)
  → verifier별 pass/fail, 미검증 항목 목록
- **구현 방법**: shell 문자열이 아니라 **타입이 정해진 선언**만 허용
  ```yaml
  verification:
    - type: helm_jsonpath_equals        # 렌더링된 Helm 산출물 검사
      artifact: rendered-manifest.yaml
      expression: "$.spec.template.spec.containers[0].env[?(@.name=='BANK_SSO_ENABLED')].value"
      expected: "true"
    - type: file_exists_in_image        # 이미지 내 파일 존재
      image: bank/openmetadata-connector
      path: /app/connectors/bank_db2/__init__.py
    - type: python_import_succeeds      # 패키지 import 가능
      image: bank/ingestion
      module: bank_db2_connector
  ```
  - 지원 타입(초기 세트): `yaml_value_equals` · `helm_jsonpath_equals` ·
    `file_exists_in_image` · `python_import_succeeds` · `api_schema_contains` ·
    `package_version_equals`
  - 각 타입은 하네스 코드에 구현된 **고정 로직**이며, 파라미터는 데이터로만 해석
    (문자열을 shell·eval에 전달하는 코드 경로 자체가 없어야 함)
  - 커스텀 검증이 꼭 필요하면: manifest에는 **보호 저장소의 allowlist 스크립트
    경로 + 해당 파일 해시**만 참조. 해시 불일치 시 analysis_error
- **수용 기준**:
  (a) `command`·shell 문자열 형태의 verification은 스키마 검증에서 거부됨
  (b) 각 지원 타입의 pass/fail 픽스처 통과
  (c) allowlist 스크립트의 해시 불일치 → analysis_error
  (d) `active` 상태의 config/deployment/extension 명세에 verification이 없으면
      관리 지표로 집계(§9.7 정책 유지)

---

### 5.5 부채 상한 게이트 (GD) — Gate 4

#### REQ-GD-01 · 패치 규모 상한
- **충족**: **Gate 4**, **보완책 3**
- **목적**: 코어 패치 수·총 변경 라인이 상한을 넘으면 경고/실패
- **입력→출력**: 스택 + `thresholds.yaml` → 초과 항목, exit 0/2
- **구현 방법**:
  - core-patch 커밋 수 = 방향 A trailer 집계
  - 총 변경 라인 = `git diff --numstat <base>..HEAD` 합산
  - 상한 초과 → 승인필요(2)(재설계 검토 유도)
- **수용 기준**: 상한을 넘긴 스택을 2로 닫고 어떤 지표가 초과인지 카드에 기록

#### REQ-GD-02 · 반복 충돌 추적
- **충족**: **Gate 4**, **보완책 3**(재설계 신호)
- **목적**: 동일 ID가 N개 버전 연속 충돌하면 재설계 검토 강제
- **입력→출력**: `conflicts.json` 이력 누적 + 임계 K → 초과 ID, exit 0/2
- **구현 방법**: 릴리스마다 REQ-RA-02의 conflicts.json을 누적, ID별 연속 충돌
  카운트 ≥ K 이고 재설계 ADR 부재 → 승인필요(2)
- **수용 기준**: K회 연속 충돌 ID가 ADR 없이 재등장하면 2로 닫는다

---

### 5.6 정본·브랜치 게이트 (CB)

#### REQ-CB-01 · 브랜치 명명 규약 검증
- **충족**: **보완책 4(정본 규칙)**
- **목적**: 브랜치가 `candidate|release/om-<ver>-bank.<rev>` 규약을 따르는지 검증
- **입력→출력**: 브랜치명 → 적합 여부, exit 0/1
- **구현 방법**: 정규식 매칭. CI에서 브랜치 생성·푸시 시 검사
- **수용 기준**: 규약 위반 브랜치명을 실패시킨다

#### REQ-CB-02 · 정본 소스 검증 — 정정본 (P0-1 반영)
- **충족**: **보완책 4**, P0-1, P1
- **목적**: 재적용 소스가 patch-lock에 고정된 SHA 기준인지, 패치가 유실·변형됐는지를
  **기계 판정**한다
- **정정 배경**: 초안은 `git range-diff` 출력을 파싱해 판정했다. range-diff는
  사람 리뷰용 출력이라 git 버전 간 포맷 안정성이 보장되지 않아 기계 판정
  입력으로 부적합하다(P0-1). **기계 판정과 사람 리뷰를 분리**한다.
- **입력→출력**: 이전 patch-lock + 신규 candidate → ID별 판정 JSON, verdict
- **구현 방법**:
  - **기계 판정 (정본)**:
    1. 이전 patch-lock의 ID별 `source_commits`(고정 SHA) ↔ 신규 브랜치의
       커밋 trailer(`Customization-ID`·`Source-Commit`·`Patch-Revision`) 대조
    2. 각 적용 커밋의 변경 메타데이터를 `git diff-tree --raw -z`로 추출해
       파일 집합·변경 유형 비교 (자체 구조화 JSON 생성)
    3. 보조 지문: `git patch-id --stable` — **"거의 같은 패치" 후보 탐색
       힌트로만** 사용, 판정 근거로 쓰지 않음(베이스가 다르면 값이 변함)
    4. 판정: lock에 있는 ID가 candidate에 없음 → block /
       lock에 없는 신규 코어 패치 → approval /
       Source-Commit이 lock의 SHA와 불일치 → block /
       재적용 소스가 lock이 아닌 동적 브랜치 참조 → block
  - **사람 리뷰 (참고 산출물)**: `git range-diff <old_range> <new_range>`
    결과를 리뷰 보고서로 첨부 — 파싱하지 않는다
- **수용 기준**: (a) lock의 ID 1건을 candidate에서 제거 → block
  (b) 미등록 신규 패치 추가 → approval
  (c) git 버전을 바꿔도(range-diff 출력이 달라져도) 기계 판정 결과는 동일
  (d) range-diff 출력은 사람용 산출물로만 존재하며 판정 코드가 읽지 않는다

---

### 5.7 rerere 검출 게이트 (GR) — 기본 비활성

#### REQ-GR-01 · 자동해결 검출 (도입 시에만)
- **충족**: **Gate 3**, **보완책 5(기본 미사용)**
- **목적**: rerere가 재생한 충돌 해결 커밋을 검출해 테스트·리뷰 강제
- **입력→출력**: 재적용 로그 → rerere 개입 커밋 목록, exit 0/2
- **구현 방법**: `git rerere` 활성 시 재적용 중 "Resolved '...' using previous
  resolution" 메시지 캡처 → 해당 ID의 required_tests 강제 + 리뷰 승인 없이는 승격 금지.
  **기본값: rerere 비활성 → 이 게이트 no-op**
- **수용 기준**: rerere 비활성이면 항상 0(no-op), 활성+재생 발생 시 해당 ID를 2로 닫는다

---

### 5.8 오케스트레이션·CI (OR)

#### REQ-OR-01 · 게이트 조립 러너 + verdict 엔진 — 정정본 (P0-3·P0-4 반영)
- **충족**: 전 게이트 통합, P0-3(집계 버그), P0-4(분석실패 우회)
- **목적**: 모든 판정 게이트를 조립하고, 심각도 rank로 집계해 최종 판정을 산출
- **입력→출력**: `run.sh <base>..<head> --repo <r> --policies <dir>`
  → 감사카드 + `acgh-result.yaml` + exit code
- **구현 방법**:
  ```python
  # 내부 심각도 — 집계는 반드시 이 rank로 (exit code max() 금지)
  SEVERITY_RANK = {"pass": 0, "approval": 1, "block": 2, "analysis_error": 3}
  # 외부 exit — 변환은 최종 1회만 (rank와 순서가 다름)
  EXIT_CODE     = {"pass": 0, "block": 1, "approval": 2, "analysis_error": 3}

  def aggregate(gate_results: list[str]) -> str:
      return max(gate_results, key=SEVERITY_RANK.__getitem__)
  ```
  - 각 게이트는 문자열 verdict(enum)를 반환하고, 러너가 rank 집계 후
    **최종 단계에서 한 번만** exit code로 변환
  - **analysis_error 판정 조건**(정상판정으로 흡수 금지): 게이트 파일 부재 /
    게이트 프로세스 Traceback·비정상 종료 / 타임아웃 / 정책 파일 파싱 실패 /
    필수 입력(patch-lock·manifest) 누락
  - analysis_error는 **차단으로 취급**하며 승인으로 우회 불가(P0-4).
    긴급 예외는 break-glass 절차(별도 REQ)만 허용
- **수용 기준**:
  (a) `block + approval` 동시 발생 → 최종 **block** (approval로 격하되지 않음)
  (b) 게이트 하나를 삭제 → analysis_error → exit 3, CI에서 차단으로 표시
  (c) 게이트가 Traceback으로 죽어도 최종 판정은 analysis_error (pass 흡수 0건)
  (d) 뮤테이션: EXIT_CODE로 집계하도록 바꾸면 (a) 픽스처가 실패해야 함

#### REQ-OR-02 · 4-상태 결과 계약 (acgh-result.yaml)
- **충족**: 판정 무결성 (CI 경계에서의 상태 붕괴 방지)
- **목적**: pass/approval/block/analysis_error 4상태가 CI 경계에서
  2단계(0/비0)로 붕괴되지 않게 함
- **입력→출력**: 게이트 결과 → 정본 결과 파일 + CI 매핑
- **구현 방법**: 결과 YAML 스키마
  ```yaml
  schema_version: 1
  verdict: pass | approval | block | analysis_error   # 정본
  gates:
    - name: reapply
      verdict: block
      reasons: ["BANK-OM-001 conflict: AuthenticationFilter.java"]
  required_approvers: []        # approval일 때
  analysis_errors: []           # analysis_error일 때 원인
  inputs: { base: <sha>, head: <sha>, patch_lock: <sha>, policies: <sha> }
  harness_version: <ver>
  ```
  CI required-check는 exit code가 아니라 **이 파일의 `verdict`를 읽어** 구성
- **수용 기준**: 4상태 각각이 CI 상태로 서로 구분되어 나타난다.
  exit code만 보고 판단하는 경로가 없다

#### REQ-OR-03 · 자기보호 (dogfooding)
- **충족**: **G5**
- **목적**: 게이트·정책·CI 집행 경로 편집을 승인 대상화
- **입력→출력**: diff → 통제경로 접촉 여부
- **구현 방법**: `sensitive-zones.yaml`에 `policies/**`·게이트 코드 경로·CI
  워크플로·CODEOWNERS를 protected 등록(REQ-GZ-01이 집행). 새 차단 메커니즘
  발명 금지 — 기존 경로 게이트로 집행
- **수용 기준**: 정책 파일·게이트 코드 변경 시 지정 승인자 없이는 승인필요(2)로 닫힌다

---

## 6. 요구사항 추적표 (Traceability)

| 보완책 / 게이트 | 충족 요구사항 | 해결 문제 |
|---|---|---|
| 보완책 1 · 자동화 | REQ-RA-01, GZ-03, GD(간접) | P1 |
| 보완책 2 · 격리+기록 | REQ-RA-02, GZ-02, CG-01 | P1·P3 |
| 보완책 3 · 원천 억제 | REQ-GZ-01, GZ-04, GD-01, GD-02 | P1 |
| 보완책 4 · 정본 규칙 | REQ-CB-01, CB-02 | P1 |
| 보완책 5 · 기본 미사용 | REQ-GR-01(비활성) | P1 |
| Gate 1 · 재적용 | REQ-RA-01 | P1 |
| Gate 2 · 등록·재적용 완전성 | REQ-CG-01/02/03/04/05 | P1·P3 |
| Gate 3 · rerere 검출 | REQ-GR-01 | P1 |
| Gate 4 · 부채 상한 | REQ-GD-01/02 | P1 |
| 명세 시스템 | REQ-MF-01/02 | P3·P6 |
| 감사·라우팅 | REQ-GZ-04 | P3·P6·P7 |
| 통합 무결성 | REQ-OR-01/02/03 | P7 |

---

## 7. 사전 환경 셋팅 (개발 전/병행, 조직이 저작)

코드가 아니라 **정책 콘텐츠·규약·구조**이며 도구 선택과 무관하게 선행되어야 한다.

| 셋팅 | 산출물 | 연결 요구사항 | 무게 |
|---|---|---|---|
| S1 · 초기 패치 ID 분해 | 현재 변경을 `BANK-OM-xxx` 독립 커밋으로 재구성 | RA-01, CG-* | 무거움 |
| S2 · 민감경로 지도 | `sensitive-zones.yaml` (OM 코어 경로 분류) | GZ-01, OR-03 | 무거움 |
| S3 · 승인 라우팅·임계치 | `approval-routing.yaml`, `thresholds.yaml` | GZ-04, GD-01 | 중간 |
| S4 · 브랜치 규약·보호 | 명명 규칙 + branch protection + 미러 읽기전용 | CB-01/02 | 중간 |
| S5 · 명세·테스트 카탈로그 초안 | `customizations/*.yaml`, `test-catalog/*.yaml` | MF-*, CG-04 | 무거움 |

> S1·S2·S5가 없으면 게이트가 판정할 대상이 존재하지 않는다 → **최우선 선행**.

---

## 8. 개발 계획 (태스크 분해)

우선순위·의존성 기준. 각 태스크는 완료 시 지정 요구사항의 수용 기준을 픽스처로 증명한다.

### Phase 0 · 사전 셋팅 (개발과 병행)
- T00. S1(패치 분해)·S2(민감경로)·S5(명세 초안) 착수 — 나머지 전 태스크의 입력

### Phase 1 · 스파인 코어 (언어 무관, 최고 가치)
- T01 → REQ-MF-01/02 (명세 스키마·로딩)
- T02 → REQ-GZ-01/02/03 (민감경로·의도·생존성)
- T03 → REQ-GZ-04 (감사카드·라우팅)
- T04 → REQ-OR-01 (러너 조립)
- **완료 기준**: change-intent + sensitive-zones만으로 경로 기반 통제가 돈다

### Phase 2 · 완전성·재적용 (누락 검출의 핵심)
- T05 → REQ-CG-01/02 (양방향 ID 검증)
- T06 → REQ-CG-03 (affected_paths drift)
- T07 → REQ-CG-04 (테스트 존재 검증)
- T08 → REQ-RA-01/02 (재적용 자동화·충돌 기록)
- **완료 기준**: 커스터마이징 누락이 CI 실패로 나타난다 (G1 달성)

### Phase 3 · 부채·정본·무결성
- T09 → REQ-GD-01/02 (부채 상한·반복 충돌)
- T10 → REQ-CB-01/02 (브랜치 규약·range-diff)
- T11 → REQ-OR-02/03 (4상태 결과 계약·자기보호)
- **완료 기준**: 게이트가 스스로를 보호하고 CI에서 차단/승인이 구분된다

### Phase 4 · 선택
- T12 → REQ-GR-01 (rerere 검출 — 반복 충돌 실측 데이터가 필요성 증명할 때만)

### 의존성 요약
```
T00(셋팅) ─▶ 전부의 입력
T01 ─▶ T05·T07 (명세 로딩 선행)
T02 ─▶ T03 ─▶ T04 (코어 → 카드 → 러너)
T05·T06·T07·T08 ─▶ T09 (완전성 → 부채)
T04 ─▶ T11 (러너 → 4상태 결과 계약)
```

---

## 9. 비범위 (명시적 제외)

| 항목 | 사유 | 대체 계층 |
|---|---|---|
| 언어별 능력·콜그래프 분석 | 스파인은 경로·git·YAML만 | 후속 부가층(Python 우선) |
| DB·검색·업그레이드 E2E 실행 | 게이트는 무엇을 테스트할지만 산출 | 업그레이드 테스트 계층 |
| 반입 무결성(SBOM·서명·digest) | 변경 거버넌스 밖 | release-lock·서명 계층 |
| UI 기능·렌더링 검증 | 정적 경로 통제만 | 업그레이드 테스트 계층 |

---

## 10. 검증 요구사항 (하네스 자신)

- V1. **결정론**: 동일 입력 3회 실행 결과 md5 일치.
- V2. **픽스처**: 각 REQ 수용 기준마다 통과/실패 픽스처 쌍.
- V3. **뮤테이션**: 기대값을 뒤집었을 때 테스트가 실제로 실패하는지(테스트가 장식이 아님) 확인.
- V4. **자기 적용(dogfooding)**: 이 하네스 저장소 자신의 변경에도 게이트를 적용.
- V5. **fail-safe**: 게이트 파일 부재·예외·타임아웃은 `analysis_error`(차단 취급)로 닫음 — 승인으로 우회 불가(§1.4).

---

## 11. 오픈 이슈 (착수 전 결정 필요)

- Q1. 명세 저장 위치 — core/platform 두 저장소 병합 로딩 방식 확정(설계서 5.4).
- Q2. `thresholds.yaml`의 초기 상한값(패치 수·라인·연속충돌 K) — 조직 합의 필요.
- Q3. glob 라이브러리 선택 — `pathspec`(gitignore 문법) vs `wcmatch`.
- Q4. REQ-OR-02 결과 계약 형식 — 참조 하네스 ADR-002와 정합할지 독자 정의할지.
- ~~Q5. 재적용 소스 브랜치 자동 판별~~ — **해소됨**: 동적 탐지 금지, 고정 SHA
  patch-lock이 유일한 소스(REQ-CB-02 정정본·부칙 A-2).

---

## 부칙 A. 2차 검토 정정 (M1 동결 전 반영 필수)

> GPT 2차 검토에서 확인된 2차 결함의 정정. **본문과 충돌 시 부칙이 우선한다.**
> 아래 3개 묶음이 반영되기 전에는 T10(스키마)·T11(patch-lock)을 동결하지 않는다.
> T12(git 프리미티브)·T13(verdict 엔진)은 즉시 개발 가능.

### A-1. 결과 계약을 CI 경계까지 닫기 [REQ-OR-01/02 보강 + 신규 T15]

1. **exit/result 불일치 = analysis_error.** 결과 파일 누락·파손·stale
   (입력 SHA가 현재 candidate와 다름)·expected_exit 불일치 → 어느 한쪽을
   신뢰하지 않고 synthetic `analysis_error`로 판정한다.
2. **원자적 생성**: 임시 파일 작성 → 스키마 검증 → 입력 SHA·정책/harness
   digest 자체 검증 → fsync + 원자적 rename으로 확정.
3. **canonical digest**: `result_digest`는 YAML 전문 md5가 아니라
   canonical JSON 직렬화(정렬·정규화)의 SHA-256. `generated_at`·duration·
   runner_id 등 관측 메타데이터는 digest 대상 밖(`observational_metadata`).
   → V1(결정론) 수용 기준도 이 canonical payload 기준으로 정정.
4. **attestation 분리**: `acgh-result.yaml`은 불변 기계 판정.
   사람 승인은 `approval-attestation.yaml`(승인자·대상 result digest·
   candidate SHA·정책 버전·시각), 예외는 `break-glass-attestation.yaml`
   (원 verdict 보존·범위·만료·사후검증)로 분리. candidate·정책 digest가
   바뀌면 기존 attestation 자동 무효. release-lock이 유효 attestation ID를 결속.
5. **다중 저장소 입력 결속**: `inputs`는 단일 base/head가 아니라
   repository-qualified(upstream/core/platform/policy 각각의 SHA) +
   `patch_source_lock_digest` + `verifier_catalog_digest`.
6. `acgh-result.yaml`에 `expected_exit_code`·`run_id` 포함. CI wrapper는
   실제 exit 캡처 후 반드시 결과 해석 단계를 실행(`set -e` 단락 금지).

### A-2. patch-lock · lineage · 동시성 모델 확정 [REQ-RA/CB 보강]

1. **lock 분리**: 실행 중 불변의 `patch_source_lock`(digest·source_release_sha·
   ID별 source_commits)과 실행 결과인 `candidate_application_lock`
   (parent_lock_digest·applied_commits·resolution_record_ids)을 분리.
   실행 중 원본 lock을 덮어쓰지 않는다. 승격 후 application lock이 다음
   업그레이드의 source lock이 된다.
2. **lineage 자동 각인**: 일반 cherry-pick은 `Source-Commit` trailer를
   만들지 않는다. 재적용 도구가 충돌 여부와 무관하게 **모든 적용 커밋**에
   `Customization-ID`·`Source-Commit(s)`(반복 허용)·`Patch-Revision`·
   `Application-Record-ID`(+해결 시 `Resolution-Record-ID`)를
   `git interpret-trailers`로 각인. 정본 lineage(1:N/N:1)는 lock의 명시적
   mapping이며 trailer와 불일치 시 block.
3. **Patch-Revision 증가 조건**: 무충돌 포팅=동일 revision+새 application
   record / 충돌 해결·재작성·split/squash=revision 증가.
4. **source object 보존**: 모든 source commit은 immutable tag 또는
   `refs/bank/patch-sources/*`에서 reachable 유지. 재적용 전
   `git cat-file -e <sha>^{commit}` preflight, 누락=analysis_error,
   "최신 브랜치" 자동 대체 금지.
5. **해결 직렬화(MVP)**: resolve는 lock 순서대로 한 번에 한 ID.
   담당자는 코드 제안만, lock 갱신은 단일 integrator가
   `base_lock_digest` 확인(CAS, `git update-ref` old-OID 검증) 후 반영.
   stale base는 자동 거부·재실행.
6. **재적용 상태 분류**: non-zero를 전부 충돌로 취급하지 않는다 —
   `applied / content_conflict / redundant_or_empty / missing_source_object /
   invalid_source_commit / skipped_due_to_dependency / internal_error`.
   `redundant_or_empty`는 자동 drop 금지, retirement 절차(T92)로 연결.
   `missing_source_object`·`internal_error`=analysis_error.
7. **논리 동일성 수용 기준 정정**: 해결본의 논리적 동일성은 자동 증명
   불가. 수용 기준은 "구조 evidence(전후 delta·contract 변경 여부·경로
   검증) + 필수 테스트 + 지정 승인으로 잔여 위험 수용"으로 기술.

### A-3. 스키마 의미 기반 확정 [REQ-MF/CG/EV 보강 + 신규 T05]

1. **신규 T05 — path-ownership·glob grammar 정본**: upstream SHA에 결속된
   `repository-layout.yaml`(upstream_owned_roots / bank_governance_roots /
   platform_extension_roots / `unknown_path_policy: analysis_error`,
   rename은 양쪽 ownership 기록). CG-01의 "업스트림 원본 경로", MF-01,
   GZ 민감영역, T93이 **같은 path 문법**(문법 이름·버전, repo-root 상대,
   `/` 구분, 대소문자·Unicode 정규화, 부정 패턴 여부, symlink/submodule/LFS
   정책)을 사용. M1 전 고정.
2. **required ⊆ allowed 강제**: MVP에서 `required_changed_paths`는 정규화된
   literal path만 허용, semantic validator가 각 literal이 allowed 패턴에
   매칭되는지 검사(JSON Schema 단독으론 불가 — 스키마 검증 단계의 custom rule).
3. **contract↔test 단일 정본**: contract catalog가 업무 불변식과
   `required_tests`의 정본. manifest는 `assurance.contracts`(참조)와
   `assurance.direct_tests`(contract 비파생 기술 테스트)만 선언.
   effective tests = direct ∪ contract-derived. 중복 선언 불일치=block.
   `contracts`는 `upgrade_watch` 밖 `assurance` 블록으로 이동.
4. **series 목록 소유**: manifest는 정책(series 허용·dependency)만,
   release별 실제 SHA·순서는 patch-lock 소유. 중복 저장 금지.
5. **실행형 verifier sandbox**: `python_import_succeeds`·allowlist script·
   컨테이너 실행형은 sandbox 필수 — network off·secret 미주입·read-only
   root·non-root/capability drop·CPU/mem/PID/시간 제한·interpreter digest
   고정·출력 제한. 가능하면 import 대신 정적 `python_module_present` 우선.
6. **JSONPath 통제**: RFC 9535 준수 구현, eval·script expression 금지,
   표현식 길이·깊이·결과 수 제한, 초과=analysis_error. 단순 경로 확인은
   JSON Pointer 기반 `document_query_assert`를 기본값으로. verifier 타입에
   `document_query_assert`·`file_hash_equals` 추가. verifier 입력 artifact는
   blob SHA·파일 SHA-256·OCI digest 중 하나로 candidate에 결속.
7. **CG 보강**: 순효과 검사는 (a) series 내재 효과 = `first^` tree vs
   `last` tree 전체 비교, (b) 전체 스택 기여 = ID 제외 counterfactual
   replay(재생 실패=inconclusive→리뷰, MVP는 high/critical 우선) 2단 분리.
   touched paths(상한 검사)와 net changed paths(하한 검사) 분리.
   비연속 series는 MVP에서 block. dependency는 순환만이 아니라
   **실제 순서**(선행 series가 앞) + lock의 topological order 검증.
   CG-03 verdict 확정: allowed 밖 core 변경=block, required net 누락=block,
   `block 또는 approval` 같은 모호 표현 금지(정책 테이블로만 예외).
8. **tree equality 범위 명시**: replay==tree는 **추적된 source tree**
   동일성만 보장(빌드 산출물 bit 재현·untracked·이미지 layer는 별도 —
   T91 digest 승격이 담당).
