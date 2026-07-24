# ADR-001: Vendor Merge를 기본 업그레이드 전략으로 채택

- 상태: 승인
- 결정일: 2026-07-24
- 적용 대상: OpenMetadata 커스터마이징 거버넌스 하네스와 운영 절차
- 대체하는 전제: “모든 업그레이드는 새 공식 태그에 patch stack을 cherry-pick한다”

## 1. 배경

초기 설계는 모든 행내 커스터마이징을 `BANK-OM-xxx` 패치 커밋으로 유지하고,
새 공식 OpenMetadata 태그 위에 순서대로 cherry-pick하는 patch-replay 방식을
유일한 운영 전략으로 가정했다.

그러나 실제 운영 계획은 공식 OpenMetadata와 공통 조상을 유지하는 vendor branch를
운영하고, 새 공식 버전을 vendor branch에 merge한 뒤 커스터마이징 생존 여부와 기능을
검증하는 방식이다. 이 경우 cherry-pick은 필수 운영 절차가 아니며, 다음 문제를 만든다.

- 업그레이드마다 동일한 논리 변경의 commit SHA가 다시 생성된다.
- patch source/application lock과 충돌 해결 리비전 관리가 운영의 중심이 된다.
- 이미 업스트림 ancestry를 가진 vendor branch의 이력을 불필요하게 재구성한다.
- 검증 목적이 “기능과 변경의 생존”보다 “cherry-pick 성공”에 종속된다.
- 테스트 레포가 특정 Git 통합 방식만 허용하게 된다.

커스터마이징 검증의 본질은 Git 명령의 종류가 아니라 다음 질문에 답하는 것이다.

1. 승인된 공식 버전이 vendor candidate에 정확히 통합됐는가?
2. 등록된 커스터마이징이 누락 없이 남아 있는가?
3. 승인되지 않은 변경이나 민감 변경이 섞이지 않았는가?
4. API·DB·검색·권한·UI의 업무 계약이 실제로 유지되는가?
5. 검증한 candidate와 배포 산출물이 동일한가?

## 2. 결정

### 2.1 기본 운영 전략

기본 통합 전략을 `vendor-merge`로 한다.

```text
공식 OpenMetadata A
        │
        └── vendor/A
              ├── BANK-OM 커스터마이징
              │
공식 OpenMetadata B ── merge ──▶ vendor/B candidate
                                  │
                                  └── 구조·계약·기능 검증
```

- 공식 OpenMetadata 태그와 SHA는 계속 고정한다.
- vendor branch는 공식 업스트림과 공통 조상을 유지한다.
- 업그레이드는 승인된 공식 target SHA를 vendor branch에 merge한다.
- merge conflict는 vendor candidate에서 해결하고, 해결 내용을 구조화 기록한다.
- 최종 판정은 merge 성공이 아니라 candidate의 ancestry, 변경 범위, 커스터마이징
  생존, 업무 계약과 런타임 테스트 결과로 내린다.
- 공유 vendor branch에 rebase를 강제하지 않는다.

### 2.2 선택적 patch-replay

기존 cherry-pick/replay 구현은 삭제하지 않고 `patch-replay` 선택 모드로 유지한다.

사용 목적:

- 커스터마이징이 특정 공식 버전에 독립적으로 이식 가능한지 진단
- vendor branch 손상 시 복구 후보 생성
- 여러 공식 버전을 동시에 지원할 때 후보 재구성
- 특정 커스터마이징의 기여도를 counterfactual 방식으로 분석
- 업스트림 흡수 여부와 retirement 가능성 검토

다음은 금지한다.

- cherry-pick 성공만으로 운영 candidate를 합격 처리
- 모든 vendor upgrade에서 source commit SHA 재생성을 강제
- patch-lock이 없다는 이유만으로 정상적인 vendor-merge candidate를 차단

### 2.3 전략 중립 검증

공통 검증은 통합 전략과 분리한다.

| 공통 검증 | `vendor-merge` | `patch-replay` |
|---|---|---|
| 공식 base/target SHA 고정 | 필수 | 필수 |
| `BANK-OM-xxx` manifest | 필수 | 필수 |
| allowed/required path 검사 | 필수 | 필수 |
| 민감 경로·정책 검사 | 필수 | 필수 |
| upgrade_watch·구조화 diff | 필수 | 필수 |
| contract·기능 테스트 | 필수 | 필수 |
| candidate SHA/digest 결속 | 필수 | 필수 |
| upstream ancestry/merge 검증 | 필수 | 해당 없음 |
| patch source lock | 선택 | 필수 |
| clean-room cherry-pick replay | 진단 옵션 | 필수 |

## 3. 정본과 잠금 구조

기존의 patch source/application lock 중심 구조를 다음처럼 일반화한다.

### 공통 정본

- `upstream-lock`: 공식 base/target tag와 40자리 SHA
- `customization-registry`: `BANK-OM-xxx` ID, 목적, owner, 상태
- customization manifest: 변경 범위, 감시 경로, 계약과 테스트
- `candidate-lock`: 검증 대상 repository, commit SHA, tree SHA, artifact digest

### `vendor-merge` 전용 증거

- merge base
- 승인된 upstream target SHA
- candidate가 target SHA를 포함한다는 ancestry 증거
- merge commit 또는 통합 기록
- conflict resolution 기록

### `patch-replay` 전용 증거

- patch source lock
- patch series와 순서
- source/application lineage
- clean-room replay 결과

## 4. 판정 기준

### `vendor-merge` 필수 게이트

1. candidate와 공식 upstream의 공통 조상이 존재한다.
2. candidate가 승인된 upstream target SHA를 ancestry에 포함한다.
3. upstream target과 candidate 사이의 순변경이 manifest 범위와 일치한다.
4. 모든 active customization ID의 required state와 contract가 존재한다.
5. 민감 경로 변경은 정책에 따른 승인을 받는다.
6. candidate SHA에 결속된 테스트 결과가 유효하다.
7. 검증 candidate와 배포 artifact digest가 동일하다.

### `patch-replay` 추가 게이트

1. 모든 source commit object가 존재한다.
2. patch series가 고정 순서로 적용된다.
3. replay tree와 candidate tree가 일치한다.
4. 해결 리비전과 lineage가 patch lock에 기록된다.

## 5. 기존 구현의 처리

다음 모듈은 그대로 공통 사용한다.

- `verdict.py`
- `result_io.py`
- `evidence.py`
- `binding.py`
- `gitprim.py`
- `layout.py`
- `manifest.py`
- `drift.py`
- `zones.py`
- `upgrade_watch.py`
- `impact.py`
- `policy_drift.py`
- `verifier.py`
- `structdiff.py`
- `contracts.py`
- `patchkill.py`
- `policy_guard.py`
- `debt.py`

다음 모듈은 `patch-replay` 선택 모드로 재분류한다.

- `patchlock.py`
- `reapply.py`
- `resolve.py`
- `replay.py`
- `integrator.py`
- replay에 의존하는 `finalstate.py` 일부

## 6. 추가 개발 항목

| 태스크 | 내용 | 우선순위 |
|---|---|---|
| T24 | `integration_strategy`와 `candidate-lock` 스키마 | ✅ 완료 |
| T25 | vendor ancestry·upstream target 포함 검증 | P0 |
| T26 | merge candidate의 customization 생존 게이트 | P0 |
| T27 | merge conflict resolution evidence | P1 |
| T28 | replay 모듈을 선택 진단 모드로 라우팅 | P1 |
| T29 | 실제 `kb_openmetadata` 변경을 manifest/contract로 등록 | P0 |

`T25~T29`가 구현되기 전까지 기존 MVP1 완료 표시는
**patch-replay 모드의 구조 검증 구현 완료**를 뜻한다. `vendor-merge` 기본 경로의
Candidate-control은 아직 완료가 아니다.

## 7. 실제 커스터마이징 등록 기준

첫 실제 검사 대상은 `kangdkdk/kb_openmetadata`의 공식
`1.13.1-release` 대비 변경이다. 기능 단위 초기 ID는 다음을 기준으로 한다.

| ID | 기능 |
|---|---|
| `BANK-OM-001` | InstanceCode |
| `BANK-OM-002` | QueryReport |
| `BANK-OM-003` | Data Assertions |
| `BANK-OM-004` | 은행 컬럼 확장 표시 |
| `BANK-OM-005` | 한글 IME 보정 |
| `BANK-OM-006` | Sybase |
| `BANK-OM-007` | Tibero |

개발용 Docker 설정과 에이전트 설정은 제품 커스터마이징 ID에 섞지 않고 별도
governance/development change로 분류한다.

## 8. 결과

### 기대 효과

- 실제 vendor branch 운영 방식과 검증 체계가 일치한다.
- Git 통합 방법보다 최종 candidate의 내용과 기능을 기준으로 판정한다.
- 기존의 결정적 검증 모듈을 대부분 재사용한다.
- 필요할 때만 replay의 이식성·복구 장점을 사용할 수 있다.

### 비용과 위험

- vendor ancestry와 merge provenance를 검증하는 신규 코드가 필요하다.
- replay 중심으로 작성된 문서와 MVP 상태를 단계적으로 정정해야 한다.
- merge history에서 upstream 변경과 행내 순변경을 정확히 분리하는 로직이 필요하다.

## 9. 문서 우선순위

이 ADR은 2026-07-24 이전 문서의 다음 표현보다 우선한다.

- “patch stack이 유일한 전략”
- “merge가 아니다”
- “모든 업그레이드에서 cherry-pick 재적용”
- “patch-lock 부재는 모든 candidate의 차단 사유”

문서 간 충돌 시 우선순위:

1. 이 ADR
2. SRS 부칙 A
3. Build Plan
4. SRS 본문
5. 상세 설계서와 전략 브리핑
