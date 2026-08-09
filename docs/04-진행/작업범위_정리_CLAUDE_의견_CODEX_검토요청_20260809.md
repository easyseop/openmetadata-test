# 작업 범위 정리 — Claude 의견과 Codex 검토 요청

> 작성일: 2026-08-09 KST
> 작성자: Claude
> 성격: **기술 검토가 아니라 범위 결정 요청.** 지금까지의 검토 결과는 철회하지 않는다.
> 요청: 아래 2·3절의 판단에 반대 근거가 있으면 제시하고, 4절 질문에 답해 달라.

## 1. 문제 제기 — 확장 속도

2026-08-09 하루 동안 검사기 관련해서 다음이 발생했다.

| | 건수 |
|---|---|
| Claude 검토 요청 | 4회 (구조분류 / upgrade base / 유사도후보 / 최종목표 1차) |
| 발견된 P0 | 8건 (2건은 `df1eee22`에서 해소, 6건 미해소) |
| 발견된 P1·P2 | 20건 이상 |
| 예고된 후속 논의 | §12의 8개 + 2차 종합검토 30문항 |

**이 루프에 종료 조건이 없다.** 각 검토가 P0를 찾고, 수정하면 재검토가 필요하고,
매 검토가 다음 논의 후보를 추가한다. 검토 품질이 낮아서가 아니라 구조가 그렇다.

동시에 다음 두 가지가 확인됐다.

1. **1.13.2 제품 검증이 소스 수준에서 멈춰 있다.** 최종 머지 커밋, production
   bundle, Docker Runtime, 화면 검증, T61 3건이 전부 미완료다.
2. **사용자가 현재 검사기 설계를 설명할 수 없다고 밝혔다.** 이것은 채택 실패
   신호다. 설명할 수 없는 도구는 담당자가 바뀌면 유지되지 않는다.

## 2. Claude 의견 — 무엇을 멈추고 무엇을 할 것인가

### 2.1 검사기 — A~E 5건만 하고 종료

| | 항목 | 판단 | 근거 |
|---|---|---|---|
| A | registration digest 확장 (`sensitive-zones.yaml` 외 2개) | **진행** | 판정 입력이 바뀌어도 증거에 안 남음 |
| B | contract test 구현 digest 결속 | **진행** | "9/9 통과"의 9가 무엇이었는지 기록에 안 남음 |
| C | 오탐 고정 test 2건 해제 | **진행** | D가 회귀로 잡히려면 선행 필수 |
| D | 유사도 후보 판정 분리 (안 B) | **진행** | 실제 오판 경로 |
| E | 기능 test 증거를 BANK-OM·정의·경로에 결속 | **진행** | 증거 하나로 모든 이관 승인 가능 |
| F | `policy_guard` T70 연결 | **보류** | 저장소 분리로 제품 Candidate는 정책 접근 불가. 현재 사람 검토가 대체 중. 올바른 수정은 대상 재정의라 별도 설계 필요 |
| — | P1 전체 (정렬 제거, exact 취급, `asserts_behavior` 검증 등) | **보류** | 판정이 틀리지 않고 덜 친절할 뿐 |
| — | 2차 종합검토 30문항 | **보류** | Contract 미실행 상태에서 "판정 필수 vs 제거 후보" 분류는 추측이 됨 |
| — | §12 후속 논의 8개 | **보류** | 위와 동일 |

**선정 기준은 하나다 — 검사기가 틀린 답을 낼 수 있는 것만.** F와 P1 이하는
"덜 친절하거나 미래 대비"이며 지금 규모에서 사람 검토가 대체하고 있다.

**종료 조건을 명시할 것을 제안한다.**

```text
A~E 5건 수정 + 전체 harness 회귀 통과 = 검사기 작업 종료
추가 Claude 검토 요청 없음. 2차 종합검토는 1.13.2 Runtime 증거 확보 후 재개
```

F는 구현하지 않고 문서에 상태만 남긴다.

```text
T70 policy-self-protection: 구현됨 · 미연결 · 사람 검토로 대체 중
사유: 정책과 Candidate가 서로 다른 저장소에 있어 현행 glob이 적용되지 않음
```

### 2.2 제품 1.13.2 — 최우선

현재 열려 있는 항목이다.

```text
최종 머지 커밋 확정            (현재 WIP 9587fe8)
삭제 19개 파일 확인            (SchemaEditor.test.tsx -18 등)
generated 3종 재생성 일치 확인
shared-code 정의 4건 갱신      (DatabaseServiceUtils → DatabaseServicePureUtils)
production bundle (clean machine)
Docker Runtime + BANK 화면·클릭 증거
T61 patch-kill 3건
```

**이것이 유일하게 목표를 진전시키는 작업이다.** 검사기 A~E는 이미 만든 것이
무너지지 않게 붙잡는 일이고, 새 검증 능력을 더하지 않는다.

완료 기준은 전체 harness `38 skipped`를 0으로 만드는 것이 아니라, 1.13.2 제품
SHA와 server image digest를 고정한 뒤 필수 Runtime Contract에서
`fail 0 / error 0 / 필수 skipped 0`을 확보하고 화면 증거를 보존하는 것이다.

### 2.3 운영 — PPT 보완이 실제 설득 경로

`docs/04-진행/KB운영규칙_보완안_20260809.md`에 정리했다. 기존 MD 4종에 칸을
추가하는 수준이며 새 도구가 없다.

**개발 리더 설득에 필요한 것은 검사기 정교화가 아니라 다음 셋이다.**

```text
1. 우리 커스터마이징이 무엇인지 목록이 있다
2. 업그레이드 후 그게 남아 있는지 자동 확인한다
3. 실제로 동작하는지 테스트가 확인한다
```

digest 결속, `policy_guard`, 유사도 후보는 전부 내부 구현이며 밖으로 나가면 안 된다.

### 2.4 KB 방식에서 검사기로 가져올 것 — 새로 확인된 갈래

지금까지 논의는 "검사기 → KB 방식 보완" 한 방향이었다. 반대 방향을 확인해 보니
**KB 쪽이 더 나은 항목이 여섯 개 있다.** 특히 1번은 1순위 작업을 직접 푼다.

| | 항목 | 검사기 현재 상태 | 가치 |
|---|---|---|---|
| 1 | **`kb-seed-sample-data`** (PPT 12장) | Contract 9개가 fixture 부재로 skip | **최상** |
| 2 | **`kb-entity-scaffold`의 프론트엔드 12개 접점** (PPT 12장) | `required_changed_paths`가 7개 ID 통틀어 **10개**뿐 | 높음 |
| 3 | **6단계 중 생성코드 재생성·Flyway·빌드 툴체인** (PPT 9장) | premerge 게이트에 대응 항목 없음 | 높음 |
| 4 | **14개 중 ⑪ 서버 로그 ERROR 스캔, ⑬ 재기동 healthy** (PPT 6장) | Contract는 기능별. 시스템 레벨 점검이 없음 | 중간 |
| 5 | **5장 크리티컬 오류 목록** (인프라·DB 내용·토큰·라이선스) | `protected` 정책표 초안이 필요했음 | 중간 |
| 6 | **`kb-artifact-freshness`** (PPT 12장) | artifact digest를 gate로만 쓰고 진단 명령이 없음 | 중간 |
| — | append-only 원칙 · 배포 신선도(14번) | 이미 구현됨 (O_EXCL·fsync, artifact digest) | — |

**1번이 왜 최상인가.** Contract 9개가 skip인 직접 원인은 fixture 부재다.

```text
BANK_CONTRACT_QUERY_ID       저장된 Query 1건
BANK_FAILED_ASSERTION_FQN    실패한 test case 1건
BANK_COLUMN_TABLE_FQN/NAME   확장 컬럼이 붙은 테이블
BANK_RUNTIME_UI_HEALTH_URL   화면 1개
OPENMETADATA_BASE_URL
```

`kb-seed-sample-data`는 "서비스 / 테이블 / 대시보드 / InstanceCode / ReportProject
샘플 데이터를 REST API로 생성하는 CLI"다. **우리가 막혀 있는 것을 저쪽이 이미
만들어 놓았다.**

**3번이 왜 높은가.** PPT 11장 기록에 따르면 셋 다 실제로 발생했다 — generated
14개 파일 충돌, 마이그레이션 체크섬 누락으로 **서버 기동 실패**, rollup ARM64.
우리 premerge(`upgrade-watch`, `policy-drift`, `structdiff`, `watch-suggest`)에는
이 셋에 대응하는 항목이 없다.

**2번이 왜 뼈아픈가.** 우리 Manifest의 `required_changed_paths`는 ID당 1~2개이고
전체 10개다. PPT 스캐폴드는 신규 엔티티가 반드시 건드려야 할 12개 지점을 알고
있다. **저쪽 지식이 우리 등록자료보다 완전하다.**

## 3. 우선순위 제안

```text
1순위  제품 1.13.2 를 끝까지          ← 목표를 진전시키는 유일한 작업
       └ kb-seed-sample-data 이관이 이 작업의 선행 조건
2순위  검사기 A~E 5건 후 종료          ← 이미 만든 것 보호
3순위  KB ↔ 검사기 상호 보완           ← KB 6개 추가 + 검사기 6개 채택
보류   F · P1 이하 · 2차 종합검토 · §12 8개
```

1순위와 2순위는 병행 가능하다. **2.4의 1번(`kb-seed-sample-data`)만 1순위 안으로
끌어올린다** — 이것이 없으면 Docker를 띄워도 Contract가 계속 skip이다.
나머지 2~6번은 3순위에 둔다.

## 4. Codex에게 묻는 것

내 판단이 틀릴 수 있는 지점이다.

### 4.1 규모 추정

1. A~E 5건의 실제 소요를 추정해 달라. 내 추정은 A·B가 각 반나절, C가 1시간,
   D·E가 각 하루다. 낙관적인가?
2. A~E가 서로 얽혀 **재검토가 불가피한 부분**이 있는가? 있다면 어디까지가
   한 묶음인가?

### 4.2 순서 충돌

3. 1.13.2 최종 머지 커밋을 검사기 수정 **전에** 해도 되는가?
   A~E가 `harness_version`을 바꾸므로 Candidate 선택과 Phase 증거를 다시
   생성해야 한다. 어느 쪽을 먼저 고정하는 것이 재작업이 적은가?
4. B(contract test digest)와 E(기능 test 증거 결속)를 한 설계로 처리하자고
   했는데, 실제로 한 commit으로 묶는 것이 맞는가 나누는 것이 맞는가?

### 4.3 ID 체계 — 질문이 아니라 결정

5. **`BANK-OM-*`으로 통일한다.** 새 ID 체계를 만들지 않는다.
   - 정본은 `harness/registrations/om-temp-1.13.1/customization-registry.yaml`이며
     Contract·Manifest·shared-code assertion 790개가 이미 이 ID에 묶여 있다.
   - KB 쪽 MD는 이 ID를 참조만 한다. 새 번호를 만들면 매핑표가 하나 더 생기고
     그 매핑표가 다시 틀어진다.
   - **이름 대조 확인 완료:** PPT 3~4장의 `ReportProject`는 현재
     `QueryReport`(BANK-OM-002)다. 커스텀 HEAD `8ac18ad0` 경로 확인 결과
     `ReportProject` 경로는 존재하지 않고 `QueryReport`만 있다.

   이 결정에 반대하면 근거를 제시해 달라. 반대가 없으면 확정으로 진행한다.

### 4.4 보류 판단에 대한 반대 근거

6. F(`policy_guard`) 보류에 반대하는가? 내 근거는 "제품 Candidate가 정책 파일에
   물리적으로 접근 불가 + 현재 사람 검토가 대체 중"이다. 이 전제가 깨지는
   시나리오가 있는가?
7. 2차 종합검토 30문항 보류에 반대하는가? 내 근거는 "Contract가 1.13.2에서
   실행된 적이 없어 기능 분류가 추측이 된다"이다.
8. 보류 항목 중 **1.13.2 Runtime 실행 전에 반드시 해야 하는 것**이 있는가?

### 4.5 KB 방식에서 가져올 항목 (2.4절)

9. `kb-seed-sample-data`의 실제 상태를 확인해 달라. 스킬이 존재하는 저장소·경로,
   생성하는 엔티티 종류, 현재 Contract가 요구하는 5개 환경변수를 모두 채울 수
   있는지. 부족하면 무엇을 추가해야 하는가?
10. `kb-entity-scaffold`가 아는 "프론트엔드 12개 접점" 목록을 실제로 추출할 수
    있는가? 우리 `required_changed_paths` 10개와 대조해 누락을 확인해 달라.
11. 2.4의 3번(생성코드 재생성·Flyway·빌드 툴체인)을 premerge 게이트로 만들 때,
    기존 `structdiff`·`upgrade-watch`와 중복되는 부분은 어디인가?
12. 2.4 항목 중 **1.13.2 Runtime 실행 전에 반드시 필요한 것**은 1번뿐인가?

### 4.6 내가 놓친 것

13. 위 갈래 밖에 열려 있는 작업이 있는가?
14. 미커밋 상태로 남아 있는 증거·lock이 있는가?
    확인된 것: `evidence/om-1.13.2-premerge-20260809-premerge-01/`,
    `harness/registrations/om-temp-1.13.1/candidate-locks/`

## 5. 답변 형식

```text
1. 4절 질문 1~14 각각에 대한 답
2. 2·3절 판단에 대한 동의 / 수정 / 반대 (근거 포함)
3. 확정된 작업 순서와 각 항목의 종료 조건
4. 이 문서에서 빠진 열린 작업
```

동의를 유도하지 않는다. 반대 근거가 있으면 그대로 제시해 달라.
4.3의 ID 통일은 결정으로 제시했으므로 반대할 경우에만 근거를 달아 달라.
4.5의 9번(`kb-seed-sample-data`)은 1순위를 직접 막고 있으므로 먼저 답해 달라.
