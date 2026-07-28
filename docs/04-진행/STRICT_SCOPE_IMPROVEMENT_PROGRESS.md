# 정확 경로 기반 검사기 개선 진척도

> 작업 브랜치: `codex/strict-manifest-gates`  
> 1차 구현 커밋: `291c6f2`  
> 목적: 설명을 바꾸는 데서 끝내지 않고, 실제 검사기가 동일한 기준으로 판정하도록 개선한다.

## 현재 단계

| 단계 | 상태 | 구현 내용 |
|---|---|---|
| 1차 · 범위 정확성 | **개발·로컬 검증 완료** | BANK-OM-001~007의 원본 커스터마이징 범위를 glob이 아닌 실제 파일 목록으로 고정 |
| 1차 · 핵심 검사기 | **개발·로컬 검증 완료** | T25-R, T26, T40, T70 강화 |
| 2차 · 위험 자동 제안 | 예정 | T42 설정·의존성 변화 감지, watch 후보 자동 제안, T41·T43 판정 기준 보정 |
| 3차 · 운영 증명 | 행내 환경 필요 | 실제 빌드·기동·API·UI·권한·성능 검사(T61/T62/T90 계열) |
| 설명용 HTML | **1차 내용 동기화 완료** | 목적→브랜치 전략→검사기→실제 예시→결과→현재/향후 단계 순서로 정리 |

## 1차에서 실제로 바뀐 것

### 1. BANK-OM-001~007 변경 범위를 파일 단위로 고정

기존 manifest의 `allowed_changed_paths`에는 `**` 같은 폴더 패턴이 포함돼
있었다. 폴더 안의 미래 파일까지 자동 허용될 수 있어, 현재 버전에서 확인된
실제 변경 파일보다 범위가 넓었다.

현재는 고정된 과거 행내 스냅샷과 공식 원본의 diff, 공유 파일의 hunk 소유자
분석 결과를 이용해 각 ID의 파일을 하나씩 등록한다.

| ID | 등록된 실제 파일 수 |
|---|---:|
| BANK-OM-001 | 48 |
| BANK-OM-002 | 55 |
| BANK-OM-003 | 25 |
| BANK-OM-004 | 33 |
| BANK-OM-005 | 1 |
| BANK-OM-006 | 18 |
| BANK-OM-007 | 8 |

여러 ID가 같은 코어 파일을 수정한 경우에는
`shared-path-owners.yaml`의 symbol·JSON key·route·SQL block 근거로
소유 관계를 판정한다. 전체 113개 경로는 **단독 소유 74개, 공유 37개,
제품 외 제외 2개**로 결정된다.

### 2. T25-R · 원본 커스터마이징 재구성 검사

- manifest에 폴더 패턴이 남아 있으면 `analysis_error`
- 고정 스냅샷에 없는 파일을 허용 목록에 넣으면 `analysis_error`
- 공유 파일의 실제 소유자와 manifest 소유자가 정확히 일치하지 않으면
  `analysis_error`
- 113개 원본 변경 경로가 단독 74 + 공유 37 + 제외 2로 정확히 분류되고,
  후보 내용이 고정 스냅샷과 동일한지 확인

### 3. T26 · 커스터마이징 생존 검사

`required` 파일 몇 개만 보는 검사에서, 등록된 원본 파일 전체를 함께 확인하는
검사로 강화했다.

- `required_changed_paths`: 없어지거나 공식 원본과 같아지면 즉시 `block`
- 그 밖의 등록 파일: 없어지거나 공식 원본과 같아지면 검토가 필요한 `approval`
- 폴더 패턴이 남아 있으면 검사 기준이 정확하지 않으므로 `analysis_error`
- contract와 이를 실행하는 테스트의 존재도 함께 확인

### 4. T40 · 변경 범위 이탈 검사

기존에는 공식 제품 영역의 변경만 범위 위반으로 확인했다. 현재는 제품 코드,
검사기 코드, 등록부, 문서를 포함해 **실제 변경된 모든 경로**가 승인 범위 안에
있는지 확인한다.

### 5. T70 · 검사기 자체 보호

다음 경로를 보호 대상에 추가했다.

- `harness/acgh/**`
- `harness/registrations/**`
- `harness/tests/**`
- `docs/02-설계/**`, `docs/03-기술참조/**`, `docs/04-진행/**`
- `STATUS.md`, `CLAUDE.md`

검사기·등록부·정책 문서를 변경해 검사를 느슨하게 만드는 경우에도 정책 변경
절차를 거치게 한다.

## 검증 결과

### 검사기 단위 테스트

```text
39 passed
```

대상: T25-R 17개, T40 5개, T26 10개, T70 7개.

### 실제 제품 후보 `849ae756…`

```text
T25   vendor ancestry                 pass
T26   customization survival          pass
T60-I required test implementation    pass (9 tests)
T30   duplicate active ID             pass
T31   shared path ownership           pass
```

T26는 BANK-OM-001~011 전체를 검사했다. BANK-OM-001은 등록 파일 48개,
필수 차단 파일 2개, contract 1개, 테스트 1개가 확인됐다.

T25-R 재구성 검사도 checkpoint `e1ffc5a1…`에서 통과했고 새 plan digest는
`sha256:05e653a8d91f49f7a4b73c0d14c27c0bd82a2d02714c7e19cee4b6914a07de98`다.

## 다음 개발 순서

1. **T42와 watch 후보 제안**: 공식 새 버전 diff, import/call/route/schema
   연결을 근거로 영향 가능 파일을 제안한다. 자동 제안은 담당자가 검토·확정한다.
2. **T41 판정 보정**: watch 파일 변화와 manifest 밖 의도 변화를 분리해
   책임자에게 이유가 보이도록 한다.
3. **T43 임계값 외부화**: 코드에 박힌 민감도 값을 정책 파일로 옮기고 실제
   업그레이드 사례로 보정한다.
4. **T93 누락·과다 범위 검사**: 지나치게 넓은 범위와 새 변경 파일 누락을
   별도로 탐지한다.
5. **T50/T51 보강**: 빈 선언과 YAML scalar/list 형태 차이를 명시적으로
   보고한다.
6. **HTML 2·3차 갱신**: 검사기 표, 실제 diff, 판정 결과, 행내 환경에서
   실행할 운영 검사를 같은 용어로 연결한다.

## 다른 컴퓨터에서 이어서 하는 법

```bash
git fetch origin
git switch codex/strict-manifest-gates
git pull --ff-only
```

이 문서의 `현재 단계`와 Git 커밋이 인수인계 기준이다. 실제 제품 소스는
`easyseop/OpenMetadata`의 후보 `849ae756…`를 변경하지 않고 검증 대상으로
사용했다.

설명용 HTML도 저장소에 함께 보관한다.

- [`openmetadata-demo-walkthrough-standalone.html`](../00-사용가이드/openmetadata-demo-walkthrough-standalone.html)
