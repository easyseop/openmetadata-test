# OpenMetadata 커스터마이징 거버넌스

공식 OpenMetadata 버전이 올라가도 **행내 커스터마이징을 누락 없이 · 재현 가능하게 ·
검증 가능하게 재적용**하여, 버전 업그레이드 운영을 원활하게 만들기 위한 설계·개발 기준.

---

## 무엇을 하려는가 (한 줄)

> 오픈소스 새 버전이 나올 때마다 우리 수정이 **빠지거나 · 왜 고쳤는지 잊히거나 ·
> 위험한 곳을 건드려도 모른 채 넘어가는** 사고를, 사람 기억이 아니라 **자동 검사(CI)**로 막는다.

전략: **패치 스택** — 커스터마이징을 이름표(`BANK-OM-xxx`) 붙인 독립 커밋으로 유지하고,
새 공식 태그(고정 SHA) 위에 **cherry-pick으로 재적용**한다. merge가 아니다.

## 무엇을 보장하고, 무엇은 보장하지 않는가 (중요)

자동 검증의 범위를 정확히 나눈다. "등록·재적용"은 결정적으로 보장하지만
"기능 의미"는 테스트·운영으로 관리한다(100% 자동 보장이 아님).

| 계층 | 자동 보장 | 보장하지 않음(다른 계층 담당) |
|---|---|---|
| 등록·재적용 완전성 게이트 | 코어 수정이 등록되고 고정 SHA 위에 순서대로 재현됨 | 로직 생존·기능 의미 |
| 계약·업그레이드 테스트 | 명시된 업무 불변식의 동작 | 테스트에 없는 새 의미 차원(잔여 위험) |
| 구조화 증거 생성기 | API·설정·DB·의존성의 구조 변화 사실 | 그 변화의 업무 영향 판단 |
| 운영 관찰(canary) | 실제 부하·데이터 거동 | — |

## 변경 케이스별 — 무엇이 잡나

```
A 무관한 변경        → 경로 대조 (무관 판정)
B 우리 파일·다른 줄   → cherry-pick 자동 + 경로 플래그
C 같은 줄 충돌        → cherry-pick 충돌 → 사람 해결
D 의존 대상 변경      → upgrade_watch + 구조화 diff + LLM Memo → 테스트 확정
E 깊은 의존·의미 붕괴 → 테스트만 (patch-kill·contract·차등 테스트)
```

---

## 검증기 요약 (막는 사고)

전체·상세는 [`docs/03-기술참조/openmetadata_verifier_catalog.md`](docs/03-기술참조/openmetadata_verifier_catalog.md) 참조.

| 검증기 | 막는 사고 | 계층 |
|---|---|---|
| 재적용 게이트 | 수정이 안 얹힌 채 진행 | 1 |
| 커밋 불변식 | 셀 수 없게 돼 누락 검증 무의미 | 1 |
| ID·series 불변식 | 한 수정의 절반만 반영 | 1 |
| 최종상태 불변식 | 이름표는 있는데 기능은 사라짐 | 1 |
| clean-room replay | 은밀한 변경 섞임 / 재현 불가 | 1 |
| 구현범위 drift | 명세가 실제와 어긋나 믿을 수 없음 | 1 |
| 민감·의도 게이트 | 위험 변경이 검토 없이 통과 | 1 |
| 경로 drift | 정책이 빈 총인데 통과만 뜸 | 1 |
| upgrade_watch | 의존 대상 변경(tenant) 놓침 | 1 |
| 부채 게이트 | 업그레이드 불가 포크로 붕괴 | 1 |
| patch-lock 일치 | 소스가 흔들려 재현 불가 | 1 |
| 선언형 verifier | 설정·확장 반영 누락 / 임의 실행 홀 | 2 |
| 구조화 diff | 의미 변경 근거를 결정적으로 못 확보 | 2 |
| 필수 테스트 존재 | 없는 테스트를 검증했다고 착각 | 3 |
| contract 결속 | 어떤 업무 규칙이 지켜지는지 모름 | 3 |
| patch-kill | 생존 못 증명하는 껍데기 테스트 | 3 |
| 테스트-SHA 결속 | 옛 결과를 유효로 착각 / flaky 뭉갬 | 3 |
| 차등 테스트 | 관계·의미 손상을 건수 대사로 놓침 | 3 |
| 정책 base-평가 | 자기 완화 우회 | 4 |
| digest 승격 | 검증본과 다른 산출물 배포 | 4 |
| verdict 엔진 | 차단이 승인으로 격하 / 고장 우회 | 4 |
| LLM Memo | (보조) 의미 변경 놓침 전에 후보 제시 | 보조 |

---

## 문서 지도

문서는 성격별로 `docs/` 하위에 정리돼 있다. 진입 문서 3종만 루트에 둔다:
[`README.md`](README.md)(개발 진입)·[`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md)
(경영진 5분 요약)·`SESSION_STATE.md`(작업 인수인계).

| 폴더 | 문서 | 용도 | 대상 |
|---|---|---|---|
| `docs/01-보고용/` | [strategy_briefing](docs/01-보고용/openmetadata_strategy_briefing.md) | 왜 이 전략인가 (merge vs 패치 스택) | 경영진·심의 |
| `docs/02-설계/` | [upstream_customization_design](docs/02-설계/openmetadata_upstream_customization_design.md) | 상세 설계 (저장소·게이트·업그레이드 절차) | 설계·개발 |
| `docs/02-설계/` | [governance_requirements (SRS)](docs/02-설계/openmetadata_governance_requirements.md) | 요구사항 정의서 ※부칙 A 우선 | 개발 |
| `docs/03-기술참조/` | [verifier_catalog](docs/03-기술참조/openmetadata_verifier_catalog.md) | 검증기 카탈로그(§0.1 구현현황) | 개발 |
| `docs/04-진행/` | [build_plan](docs/04-진행/openmetadata_build_plan.md) | **순차 개발 실행 계획** | 개발 |
| `docs/04-진행/` | [dev_roadmap](docs/04-진행/openmetadata_dev_roadmap.md) | **로드맵 & MVP 커버리지 맵** | 개발·심의 |

> **개발 착수 기준**: 진행·커버리지는 `docs/04-진행/openmetadata_dev_roadmap.md`,
> 상세 스펙은 `docs/04-진행/openmetadata_build_plan.md`(+ SRS 부칙 A). 충돌 시
> 우선순위는 **SRS 부칙 A > build_plan > 설계서 본문**. (과거 검토 대화 원문은
> 제거했고 git 이력에 보존됨. 수용된 정정의 핵심은 아래 '설계 정정 이력' 참조.)

## 설계 정정 이력 (검토 반영 요약)

> 두 차례 아키텍처 검토(P0/2차 결함) + 문서 검토를 거쳐 정정했다. 원문 대화는
> 제거했고, **수용된 정정의 핵심과 반영 위치**만 남긴다.

| 검토 | 수용한 핵심 정정 | 반영 위치 |
|---|---|---|
| **1차** (설계 P0 9건) | ① 판정을 **심각도 순위로 집계**(차단이 승인으로 격하 금지)·**분석실패=차단** ② 충돌 **탐지/해결 2모드** ③ **선언형 verifier**(manifest 임의 shell 제거) ④ range-diff 기계판정 제거 → **patch-lock+trailer** ⑤ `affected_paths` → **allowed/required_changed_paths + upgrade_watch** ⑥ **"등록·재적용 완전성" ≠ 기능 완전성** ⑦ 정책 **self-approval 차단** | SRS 본문 · build_plan · 코드 |
| **2차** (2차 결함) | **부칙 A** — ⓐ 결과계약을 CI 경계까지(불일치=analysis_error·원자적 기록·정규 해시) ⓑ **lock 분리·출처 자동각인·CAS** ⓒ 스키마 의미(path-ownership·required⊆allowed·verifier sandbox) | SRS 부칙 A · 코드 |
| **문서** (외부) | build_plan **순환의존 해소**·검증기 4계층 표기·`harness/README`·`EXECUTIVE_SUMMARY`·`docs/` 분류·SRS 상태 메타데이터 | 각 문서 (적용 완료) |

## 테스트 정책

**OpenMetadata의 파일 구조·업그레이드 차이·재적용 동작에 의존하는 통합 및
업그레이드 테스트는 실제 고정 버전의 OpenMetadata를 사용한다.** 합성 더미가
아니라 `open-metadata/OpenMetadata`의 고정 두 태그(UPSTREAM_A/B)를 미러로 받아,
실제 파일 경로 위에 BANK-OM 패치를 얹어 케이스 A~D를 재현한다. **순수 판정
로직(집계·스키마 검증 등)의 단위 테스트는 최소 합성 픽스처를 쓸 수 있다.**
업그레이드 테스트(M9)는 실제 OM Docker·DB migration·재색인으로 수행한다.
(상세: `docs/04-진행/openmetadata_dev_roadmap.md` §1)

## 개발 순서 (마일스톤)

```
M0 사전 셋팅(정책·명세 저작)
M1 기반(스키마·patch-lock·git·verdict)   ← 먼저 완성
M2 재적용 파이프라인(2-모드 충돌·replay)
M3 등록·재적용 완전성 게이트(불변식)
M4 경로·민감·부채 게이트 + 영향분석(upgrade_watch)
M5 증거 생성기(선언형 verifier·구조화 diff)
M6 테스트 결속(contract·patch-kill·SHA)
M7 정책 자기보호·fast lane·break-glass
M8 LLM Upgrade Impact Memo
M9 업그레이드 검증·릴리스 승격(digest 결속)·반입
```

## 핵심 원칙 (정정 후)

1. 코어 수정 최소화 (설정→배포→확장→코어 4단계 관문). 충돌은 코어에서만 난다.
2. 불변 ID + 순서 있는 patch series (1커밋=1ID).
3. 고정 SHA 기반 patch-lock (동적 "최신 브랜치" 아님).
4. clean-room replay 재현성 (재생 == candidate tree).
5. 판정 스파인(언어 무관·결정적) / 증거 생성기(대상별) 분리.
6. **등록·재적용 완전성 ≠ 기능 완전성** (분리해 표기).
7. verdict severity rank (분석 실패 = 차단).
8. 선언형 verifier (manifest 임의 실행 금지).
9. 정책 자기보호 (policy PR은 base 정책으로 평가).
10. LLM은 배포 판정 배제 (Memo·후보 제시만).
11. 테스트가 생존을 증명 (contract-id + patch-kill).
12. range-diff는 사람 리뷰용 (기계 판정은 patch-lock+trailer+raw diff).
