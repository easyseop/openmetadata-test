# GPT 2차 검토 요청 — 정정 반영 확인 · Build Plan · 추가 발견 검증

> **문서 목적**
> 1차 검토(P0-1~P0-9)는 전부 수용되어 SRS 본문에 정정 반영이 완료되었다.
> 2차 검토는 **P0 재론이 아니다.** 아래 3가지만 검증해 달라:
> ① 정정된 명세가 P0를 **올바르게** 반영했는가 (정정 자체의 결함 여부)
> ② Build Plan(M0~M9)의 순서·의존성·범위가 타당한가
> ③ Claude가 추가 발견한 6건이 맞는가, 우선순위는 적절한가
>
> **첨부 문서**
> - `openmetadata_governance_requirements.md` — 정정 완료된 SRS (P0 9건 반영)
> - `openmetadata_build_plan.md` — 마일스톤 M0~M9 · 태스크 T01~T94
> - `openmetadata_review_response.md` — 1차 검토에 대한 판정(A~F)
> - `openmetadata_verifier_catalog.md` — 검증기 22종 카탈로그
>
> **검토에서 제외 (재론 불필요)**
> - 패치 스택 vs merge 전략 선택 — 합의 완료
> - P0 9건의 타당성 자체 — 전부 수용됨
> - LLM 배포 판정 배제 원칙 — 합의 완료

---

## 1. 검증 요청 ① — 정정 명세가 P0를 올바르게 반영했는가

각 정정본에 대해 "반영 정확 / 반영했으나 새 결함 있음 / 반영 미흡"으로 판정하고,
새 결함이 있으면 구체적으로 지적해 달라. 아래는 정정 요지다(전문은 SRS 본문).

### 1.1 §1.4 + REQ-OR-01/02 (P0-3·P0-4 정정)
- severity rank(`pass0 < approval1 < block2 < analysis_error3`)로 집계,
  exit 변환(`pass0/block1/approval2/analysis_error3`)은 최종 1회.
- analysis_error 판정 조건 5종 열거(게이트 부재·Traceback·타임아웃·정책 파싱
  실패·필수 입력 누락), 승인 우회 불가·차단 취급.
- `acgh-result.yaml`(verdict 정본·게이트별 사유·승인자·입력 SHA·harness 버전),
  CI는 exit code가 아니라 이 파일을 읽음.
- 수용 기준에 뮤테이션 포함("EXIT_CODE로 집계하게 바꾸면 픽스처가 실패해야").
- **특히 봐 달라**: exit code 3(analysis_error)을 CI가 2(approval)와 혼동할
  경로가 남았는가? result 파일과 exit code가 불일치할 때의 우선순위 규정이 필요한가?

### 1.2 REQ-RA-01/02/03 (P0-2 정정)
- 탐지 모드: 임시 worktree에서 재적용→충돌 수집→worktree 폐기, 본 트리 오염 0.
- 해결 모드: 전용 worktree에서 충돌 유지→`--continue`→해결 커밋에 trailer 4종
  (`Customization-ID`·`Source-Commit`·`Patch-Revision`·`Resolution-Record`)
  →patch-lock 새 리비전 고정→clean-room 재생 검증.
- **특히 봐 달라**: (a) 해결 모드에서 담당자가 여러 명이 동시에 서로 다른 ID의
  충돌을 해결할 때의 경합(worktree·lock 갱신 순서) 규정이 필요한가?
  (b) 해결 커밋이 원본 패치와 "논리적으로 같은 변경"인지 검증할 방법이 없는데
  (텍스트가 다르므로), 이 간극을 수용 기준에 어떻게 반영해야 하는가?

### 1.3 REQ-EV-01 (P0-8 정정)
- 선언형 verifier 타입 6종, 파라미터는 데이터로만 해석, shell/eval 경로 부재.
- allowlist 스크립트는 보호 저장소 경로+해시, 불일치 시 analysis_error.
- `verification.command` 필드는 스키마에서 거부.
- **특히 봐 달라**: `helm_jsonpath_equals`의 JSONPath 표현식 자체가 공격
  표면이 될 수 있는가(라이브러리 취약점·과도한 표현력)? 타입 세트에
  빠진 필수 verifier가 있는가?

### 1.4 REQ-MF-01 (P0-6 정정)
- `affected_paths` 폐기 → `allowed_changed_paths`(상한)/`required_changed_paths`
  (하한)/`upgrade_watch`(paths·configuration_keys·dependencies·contracts).
- 구버전 필드 사용 시 스키마 거부.
- **특히 봐 달라**: allowed와 required의 관계 제약(required ⊆ allowed)을
  스키마 수준에서 강제해야 하는가? upgrade_watch.contracts와
  tests.required의 중복·불일치 처리 규정이 필요한가?

### 1.5 REQ-CG-01~05 (P0-5 정정)
- 게이트 개명(등록·재적용 완전성) + 보장/미보장 표.
- CG-01 커밋 불변식 7종(커밋 경계 파싱, `-z`), CG-02 ID·series 불변식,
  CG-03 drift(upgrade_watch 제외), CG-04 3중 포함, CG-05 최종상태
  (순효과 0·무단 revert·replay tree 결속·테스트 무효화).
- **특히 봐 달라**: (a) CG-05의 "순효과 0" 판정 — series 누적 diff가 비었는지를
  어떻게 결정적으로 계산할지(예: `git diff <series시작^>..<series끝> -- <경로>`)
  명세가 더 필요한가? (b) "업스트림 원본 경로를 건드린 커밋"의 판별 기준
  (core 경로 목록의 출처)이 명확한가?

### 1.6 REQ-CB-02 (P0-1 정정)
- 기계 판정: patch-lock 고정 SHA ↔ trailer ↔ `git diff-tree --raw -z`.
- `patch-id --stable`은 힌트 전용. range-diff는 사람 리뷰 첨부물(파싱 금지).
- **특히 봐 달라**: Source-Commit trailer가 가리키는 SHA가 이전 릴리스
  이력에서 GC되거나 도달 불가능해지는 경우(브랜치 정리 후)의 처리 규정이 필요한가?

---

## 2. 검증 요청 ② — Build Plan(M0~M9)의 타당성

`openmetadata_build_plan.md`의 마일스톤·태스크에 대해:

1. **순서**: M1(스키마·patch-lock·git·verdict) → M2(재적용) → M3(완전성) →
   M4(경로·부채) → M5(증거) → M6(테스트 결속) → M7(자기보호) → M8(LLM) →
   M9(업그레이드·승격) 순서에 결함이 있는가? 앞당기거나 미뤄야 할 태스크는?
2. **의존성 누락**: 태스크 간 선행 관계에서 빠진 것이 있는가?
   (예: T50 선언형 verifier가 T14 감사카드보다 먼저여도 되는가)
3. **범위 적정성**: 첫 실제 업그레이드 전에 반드시 있어야 하는데 P1/P2로
   밀린 것, 반대로 과하게 앞에 배치된 것이 있는가?
4. **최소 동작 세트(MVP)**: "첫 업그레이드를 이 하네스로 통제한다"를 위한
   최소 태스크 집합을 뽑는다면 무엇인가? (우리는 M0~M3 + T50 + T62 정도로
   추정하는데 동의하는가?)

---

## 3. 검증 요청 ③ — Claude 추가 발견 6건의 타당성

각각 "동의/부분 동의/반대 + 권장 우선순위(P0/P1/P2)"로 판정해 달라.

| # | 발견 | 요지 |
|---|---|---|
| C-1 | patch-id 취약성 명시 | 베이스·문맥이 다르면 값이 변하므로 판정 근거 금지, 힌트 전용을 REQ에 못박음 |
| C-2 | upgrade_watch drift | sensitive-zones만이 아니라 upgrade_watch glob도 신버전에서 0-매칭 검사 필요 |
| C-3 | Evidence Provider 자기보호 | API/Helm/DB diff 생성기 코드도 protected 등록 + 버전 고정(안 하면 P0-9 구멍이 증거 계층으로 이동) |
| C-4 | contract-id + patch-kill 쌍 | 업무 불변식↔테스트 결속과 patch-kill을 한 쌍의 REQ로 — 있어야 "등록≠생존" 간극을 실질 보강 |
| C-5 | clean-room replay의 bit 재현성 | replay==tree 불변식이 성립하려면 빌드 비결정성(타임스탬프·정렬·locale) 제거가 선행 |
| C-6 | 승격=동일 digest REQ화 | 테스트-candidate 결속과 재빌드 금지를 명시적 REQ로 |

추가로: **우리 둘 다 놓친 것**이 있으면 새 번호로 제시해 달라.

---

## 4. 출력 형식

### A. 정정 반영 판정표
| 정정 | 판정(정확/새 결함/미흡) | 새 결함·보완 내용 |
|---|---|---|
| §1.4+OR | | |
| RA 2-모드 | | |
| EV-01 | | |
| MF-01 | | |
| CG-01~05 | | |
| CB-02 | | |

### B. Build Plan 수정 제안
- 순서 변경 / 의존성 추가 / 범위 이동 목록 (태스크 번호 기준)
- MVP 최소 태스크 집합

### C. 추가 발견 6건 판정
| # | 판정 | 우선순위 | 비고 |
|---|---|---|---|

### D. 신규 발견 (있으면)

### E. 최종 결론
- **M1 개발 착수 가능 여부** (가능 / 조건부 가능+조건 / 불가+사유)
- 착수 전 마지막으로 반드시 고칠 것 (있다면 3개 이내로)
