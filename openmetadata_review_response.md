# GPT 검토에 대한 Claude 재검토 응답

> 원본 4개 문서(상세 설계·전략 브리핑·SRS·시각 개요)와 GPT 검토본을 대조한 결과.
> 형식은 검토본 §15 요청(A~F)을 따른다.

---

## A. 종합 결론

- **전략: 조건부 유지.** 패치 스택 채택은 유지한다. GPT의 "조건부 승인"에 동의.
- **현 SRS 착수: 불가 → P0 9건 반영 후 착수.** 특히 P0-2(충돌 흐름), P0-3(verdict 역전),
  P0-4(분석 실패 처리), P0-8(임의 명령 실행)은 실제 **버그·보안 결함**이라 반드시 선행.
- 핵심 재정의: **"재적용·등록의 완전성"과 "기능의 완전성"을 분리**하고, 문서의
  과장 표현("유일한 구조", "테스트가 잡으므로 안전")을 축소한다.

---

## B. GPT 지적별 판정

| 항목 | 판정 | 근거 | 수정 제안 |
|---|---|---|---|
| **P0-1** range-diff 파싱 | **동의** | `range-diff`는 사람용 출력, git 버전 간 포맷 불안정. REQ-CB-02가 이걸 기계 판정 입력으로 씀 → 취약 | patch-lock의 ID별 source SHA + 커밋 trailer + `git diff-tree --raw -z`로 판정. range-diff는 리뷰 참고. `patch-id --stable`은 힌트로만 |
| **P0-2** 충돌 처리 | **동의(핵심 버그)** | `--abort`하면 충돌 상태 소멸 → 사람이 해결할 트리가 없음. REQ-RA-01 흐름이 성립 안 함 | 2-모드 분리: (탐지) 임시 worktree·abort·exit1 / (해결) 전용 worktree 유지·`--continue`·해결결과를 **새 patch revision으로 고정**·clean-room 재현 검증 |
| **P0-3** verdict 집계 | **동의(버그)** | `max()`이면 `2>1`이라 block(1)이 approval(2)로 **격하** | 내부 severity rank(pass<approval<block<analysis_error)로 집계 후 exit code로 변환 |
| **P0-4** 분석 실패 | **동의** | 검사기 고장 = 검증 미수행. 사람이 승인해도 되는 위험이 아님 | 위험 발견→approval / 분석기 오류·정책 누락·타임아웃→**analysis_error=차단**. 긴급은 break-glass |
| **P0-5** ID 집합 | **동의(가장 중요)** | ID 집합 일치는 **등록 존재**만 증명. revert·빈 커밋·충돌 시 로직 제거·후속 덮어씀·set 축약·ID 혼합에서도 통과. trailer만 set 수집하면 ID 없는 커밋 자체를 못 셈 | 게이트 개명(등록·재적용 완전성). 커밋 경계 유지 파싱. 불변식 추가(1커밋=1ID, merge·empty 금지, revert=상태전환, replay==candidate tree, 테스트=candidate SHA 결속) |
| **P0-6** affected_paths | **강하게 동의** | 구현 범위 ↔ 감시 범위가 다름. 하나로 쓰면 방향 C drift 오탐 또는 감시 협소. **우리가 직전에 논의한 edited/depends_on과 동일 결론** | GPT의 `allowed/required_changed_paths`(구현) + `upgrade_watch`(경로·설정키·의존성·contract) 채택. GPT안이 우리 depends_on보다 풍부 |
| **P0-7** LLM·테스트 | **동의** | 새 의미 차원(tenant)을 기존 테스트가 모르면 LLM 놓친 순간 테스트도 통과. "테스트가 잡으므로 안전"은 거짓. 시나리오도 "충돌 없는 의미 변경"이라며 001을 충돌로 서술(모순) | 문구를 "잔여 위험으로 관리"로. 시나리오에서 **물리 충돌(003)과 의미 변경(001)** 분리 |
| **P0-8** verification.command | **동의(보안홀)** | manifest 편집자가 CI 권한으로 임의 shell 실행. (9.7절에서 우리가 넣은 것) | 선언형 verifier(yaml_value_equals, helm_jsonpath_equals, file_exists_in_image, python_import_succeeds …) 또는 allowlist script 경로+해시 |
| **P0-9** 정책 자기보호 | **동의** | 완화한 정책으로 자기 PR을 평가하면 자기승인 우회 가능 | policy PR은 **base 정책으로 판정** + 새 정책 별도 시뮬 + 2인 승인 + 다음 리비전부터 활성. 플랫폼 required check·branch protection 병행 |

**반대·부분동의는 없음.** 9건 모두 실제 결함 또는 정당한 정밀화이며 채택한다.

---

## C. Claude 추가 발견 (GPT 검토에 없거나 약한 것)

1. **patch-id 취약성 명시** — `patch-id`는 베이스·문맥이 조금만 달라도 값이 변한다.
   "거의 같은 패치 후보" 힌트로만 쓰고, 판정 근거로 삼지 않는다(GPT도 보조라 했으나 REQ에 못박아야).
2. **upgrade_watch glob도 drift 검사 대상** — GPT 10.5는 sensitive-zones drift만 다룸.
   `upgrade_watch.paths`도 업스트림 리팩터 후 0개 매칭이 될 수 있으므로 동일 drift 검사 필요.
3. **Evidence Provider 코드 자체의 형상·자기보호** — API/Helm/DB diff 생성기도 버전 고정 +
   protected(정책 코드와 동급). 안 하면 P0-9의 구멍이 증거 계층으로 이동.
4. **"테스트가 생존을 증명"의 실효 장치** — GPT의 contract-id(§6.1)와 patch-kill test(§5)를
   **한 쌍으로 REQ화**: 업무 불변식↔테스트 결속 + 패치 제거 시 그 테스트가 실제로 실패해야 등록.
   이게 있어야 P0-5의 "생존 미증명"을 부분적으로 메운다.
5. **clean-room replay의 bit 재현성** — "replay == candidate tree" 불변식이 강제되려면
   빌드·생성 코드의 비결정성(타임스탬프·정렬·locale)을 제거해야 함(GPT §8 결정론과 연결).
6. **테스트-후-candidate 변경 무효화의 REQ화** — GPT 10.1을 요구사항으로: 승격은 반드시
   **검증된 동일 commit SHA·artifact digest만**, 재빌드·복사 금지.

---

## D. 수정된 요구사항 (요약)

| REQ | 기존 | 권장 |
|---|---|---|
| REQ-CB-02 | range-diff 파싱 → 존재/누락/변형 판정 | patch-lock+trailer+`diff-tree --raw -z`로 판정, range-diff는 리뷰용 |
| REQ-RA-01/02 | 충돌 시 abort 후 사람 해결·재실행 | 탐지/해결 2-모드, 해결결과를 patch revision으로 고정·재현 검증 |
| REQ-OR-01 | 분석 실패=최소 승인필요 | analysis_error=차단, severity rank 집계 |
| REQ-OR-02 | (exit code만) | severity→exit code 매핑(pass0/block1/approval2/analysis_error3) |
| REQ-CG-01~04 | 완전성 게이트, trailer set 비교 | **등록·재적용 완전성** 개명, 커밋 경계 파싱, 커밋/ID/최종상태 불변식 |
| REQ-MF-01 | affected_paths 단일 | allowed/required_changed_paths + upgrade_watch(경로·설정키·의존성·contract) 분리 |
| REQ-GZ(신규) | — | 선언형 verifier 타입 세트(임의 command 금지) |
| REQ-OR-03 | 정책 경로 protected | + base 정책 평가·2인 승인·단계적 활성·플랫폼 required check |
| REQ(신규) | — | patch-lock / clean-room replay 동일성 / patch-kill test / contract-id / 승격=동일 digest |

수용 기준은 각 REQ에 "실패 픽스처 + 재현성(동일 입력 동일 판정) + 뮤테이션" 유지.

---

## E. 최종 우선순위

GPT의 P0/P1/P2를 대체로 수용하되, **P0 내부는 "실제 버그·보안 먼저"**로 순서화.

**P0-a (즉시 버그·보안):** P0-2 충돌 2-모드 · P0-3 verdict rank · P0-4 분석실패 차단 · P0-8 선언형 verifier
**P0-b (개념·스키마):** P0-5 완전성 보장범위 재정의+불변식 · P0-6 경로 역할 분리 · P0-1 range-diff 제거 · P0-9 정책 base 평가 · P0-7 문구·시나리오 수정
**P1:** patch-lock · empty/revert/순효과0 · patch-kill test · evidence provider(API/설정/DB/의존성) · 민감·감시 경로 drift · retirement · 핫픽스 동시 진행 · break-glass
**P2:** 부채 임계치 보정 · 반복충돌 재설계 권고 · LLM Upgrade Impact Memo 평가 · 위키 확장 · 선택적 AST · rerere 재검토

---

## F. 대상별 요약 3종

**경영진용**
> 전략(패치 스택)은 유지합니다. 다만 착수 전 안전·재현성 결함 9건을 보완해야 합니다.
> 자동 검증이 보장하는 범위는 "행내 수정이 등록되고 정해진 순서로 재현되었는가"까지이며,
> 기능 의미의 정확성은 테스트·업그레이드 검증·운영 관찰로 관리합니다(100% 자동 보장 아님).

**아키텍처 심의용**
> 판정 엔진(언어 무관·결정적)과 증거 생성기(대상별 전문화)를 분리하고, 완전성 게이트의
> 보장 범위를 "등록·재적용"으로 재정의합니다. verdict 심각도 집계·분석실패 차단·정책
> base 평가·clean-room 재현성·테스트-candidate 결속을 요구사항으로 확정합니다.

**개발팀용**
> P0-a(충돌 2-모드, verdict rank, 분석실패 차단, 선언형 verifier)부터 착수하세요.
> range-diff 기계 파싱 제거, affected_paths→allowed/required + upgrade_watch 분리,
> 커밋별 1-ID 불변식과 patch-lock을 이어서 구현합니다.

---

## 부록. §1 특정 질문에 대한 답

- **range-diff를 기계 판정 입력으로?** → 아니오. 리뷰용. 판정은 patch-lock+trailer+raw diff.
- **ID 집합 일치가 보장/미보장?** → 보장: 등록 ID의 이력상 존재. 미보장: 로직 생존·순효과·동작.
- **affected_paths 이중 사용?** → 아니오. 구현(allowed/required)과 감시(upgrade_watch) 분리.
- **abort 후 사람 해결 가능?** → 불가. 전용 worktree 유지 모드 필요.
- **검사기 실패=승인?** → 아니오, 차단. 위험 판정만 승인 대상.
- **테스트가 항상 잡나?** → 아니오. 기존 테스트 범위의 회귀만. 새 의미 차원은 잔여 위험.
- **정책 자기참조?** → base 정책으로 평가 + 2인 승인 + 플랫폼 통제로 차단.
