# GPT 2차 검토에 대한 Claude 판정 및 반영 내역

> 2차 검토(`openmetadata_governance_second_review_gpt.md`)를 원본과 대조한 판정과,
> 실제 문서에 반영한 내역. 결론: **전면 수용, 즉시 반영 완료.**

---

## 1. 종합 판정

**A~E 전 항목 동의.** 반대하는 지적이 없다. 2차 검토의 성격이 정확했다 —
"P0 정정 방향은 맞고, 정정이 만든 2차 공백(일관성·보안·운영)을 닫아라."
특히 다음 세 가지는 그대로 구현했으면 실제 사고가 났을 결함이다:

1. **exit/result 불일치 규칙 부재**(A-1) — stale pass 파일을 읽거나 분석
   실패가 승인으로 약화되는 경로가 실존했다.
2. **`Source-Commit` trailer가 저절로 생기지 않음**(A-2) — 일반 cherry-pick은
   커스텀 trailer를 각인하지 않으므로, CB-02의 대조가 **처음부터 공집합**과
   비교하는 무의미한 검사가 될 뻔했다.
3. **"선언형=비실행" 혼동**(D-3) — `python_import_succeeds`는 코드를 실행한다.
   sandbox 없이는 P0-8의 구멍이 "허용된 verifier" 경로로 이동할 뿐이었다.

소소한 재보정 하나만 기록한다: counterfactual replay(A-5)는 ID당 전체 재생이
필요해 패치 수가 늘면 비용이 커진다. GPT도 "MVP는 high/critical 우선"을
암시했고, 부칙에는 **intrinsic 검사는 상시 + counterfactual은 high/critical
우선·나머지는 주기 실행**으로 반영했다.

## 2. 판정 상세 (요약)

| 영역 | 판정 | 반영 위치 |
|---|---|---|
| A-1 결과 계약(불일치·원자성·digest·attestation) | 동의 | SRS 부칙 A-1, 신규 T15 |
| A-2 lock 분리·trailer 각인·직렬화·object 보존·상태 분류 | 동의 | SRS 부칙 A-2, 신규 T23 |
| A-3 verifier sandbox·JSONPath 통제·신규 타입 2종 | 동의 | SRS 부칙 A-3.5~6 |
| A-4 required⊆allowed·glob 고정·contract 정본·series 소유 | 동의 | SRS 부칙 A-3.1~4 |
| A-5 순효과 2단·touched/net·path-ownership·순서 검증·verdict 확정 | 동의 | SRS 부칙 A-3.7, 신규 T05 |
| A-6 object 보존·lineage 정본·raw metadata 한계 | 동의 | SRS 부칙 A-2.2~4 |
| B Build Plan 재배치·MVP 2단계 | 동의 | Build Plan §2·§4 개정 |
| C-1~C-6 판정(부분동의 포함 우선순위 재조정) | 수용 | patch-id 문구·C-5 분리 채택 |
| D-1~D-9 신규 발견 | 전부 동의 | 부칙 A 각 항 + 구표현 정정 |
| E M1 조건부 착수(3조건) | 동의 | Build Plan §4 착수 규칙 |

## 3. 실제 반영한 것 (이번 커밋)

1. **SRS 구세대 표현 제거**(D-7): 용어표·아키텍처 출력·GZ verdict·Phase
   "3상태"·V5 "승인필요 이상"·Q5 "최신 리비전 탐지"를 4상태·patch-lock
   세대로 정정. (Q5는 "해소됨" 처리)
2. **SRS 부칙 A 신설**: A-1(결과 계약 CI 경계), A-2(lock·lineage·동시성),
   A-3(스키마 의미 기반 + sandbox + CG 보강). 본문과 충돌 시 부칙 우선 명시.
3. **Build Plan 개정**: 마일스톤 순서 재배치(M1.5 preflight, T93→T42,
   T62·T70 앞당김), 신규 태스크 T05·T15·T23 정의, T50a/b 분리,
   MVP 2단계(Candidate-control / Production-upgrade) 수용,
   착수 규칙에 "T10·T11 동결 전 3조건" 명시.

## 4. 개발 착수 상태

- **지금 시작 가능**: T12(git 프리미티브), T13(verdict 엔진) —
  부칙 A의 severity rank·canonical digest 계약을 그대로 구현.
- **동결 대기**: T10(manifest 스키마)·T11(patch-lock)은 부칙 A의
  path-ownership(T05)·lock 분리 스키마를 확정한 뒤 동결.
- **3차 검토는 불필요**: 2차가 "조건부 가능 + 조건 3개"라는 닫힌 결론을
  줬고 조건은 전부 문서에 반영됐다. 다음 외부 검증 시점은 코드가 나온 뒤
  (M1 완료 시 구현 리뷰)가 적절하다.
