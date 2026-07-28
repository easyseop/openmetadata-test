# 정확 경로 기반 검사기 개선 진척도

> 작업 브랜치: `codex/strict-manifest-gates`  
> 1차 구현 커밋: `291c6f2`  
> 2·3차 구현 커밋: `5f54687`
> 고정 미러 CI 보정 커밋: `f661796`
> 목적: 설명을 바꾸는 데서 끝내지 않고, 실제 검사기가 동일한 기준으로 판정하도록 개선한다.

## 현재 단계

| 단계 | 상태 | 구현 내용 |
|---|---|---|
| 1차 · 범위 정확성 | **개발·로컬 검증 완료** | BANK-OM-001~007의 원본 커스터마이징 범위를 glob이 아닌 실제 파일 목록으로 고정 |
| 1차 · 핵심 검사기 | **개발·로컬 검증 완료** | T25-R, T26, T40, T70 강화 |
| 2차 · 위험 자동 제안 | **개발·통합 검증 완료** | T42 경로·설정·의존성 감지, watch 후보 제안, T41·T43·T93·T50·T51 보강 |
| 3차 · 운영 실행 준비 | **개발 완료·행내 실행 대기** | 필수 환경 사전검사, 후보·산출물·테스트 결과 결속, API·UI 실행 workflow |
| 설명용 HTML | **2·3차 내용 동기화 완료** | 실제 판정과 행내 실행 대기 상태를 구분해 표시 |

원격 고정 미러 검증 run
[`30253003871`](https://github.com/easyseop/openmetadata-test/actions/runs/30253003871)은
**341 passed, 7 operational skips**, 8개 source gate, 2개 source patch-kill
실험과 증거 업로드까지 통과했다.

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
| BANK-OM-007 | 원본 8 + 등록된 후속 2 = 현재 후보 10 |

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

## 2차에서 실제로 바뀐 것

### 1. T42 · 경로뿐 아니라 설정키·의존성 변화 감지

공식 버전 A→B에서 다음 세 종류를 함께 검사한다.

- manifest의 `upgrade_watch.paths`와 실제 변경 경로의 교집합
- 변경된 YAML/JSON/TOML 등에서 등록한 `configuration_keys` 변화
- `pom.xml`, `package.json`, lock 파일 등에서 등록한 dependency 변화

또한 공식 버전에서 실제 변경된 파일 중 커스터마이징 코드가 직접 참조하는
파일을 `watch` 후보로 제안한다. 제안은 자동 등록하지 않으며 코드 책임자가
근거를 검토해야 한다.

### 2. BANK-OM-007 원본 범위와 후속 범위 분리

통합 검사에서 원본 스냅샷 8개 외에 같은 ID의 후속 커밋이 2개 파일을 더
변경한 사실을 발견했다. 원본 재구성 기록을 왜곡하지 않도록 다음처럼 분리했다.

- `allowed_changed_paths`: 과거 스냅샷을 재구성하는 원본 8개
- `candidate_additional_paths`: 등록된 후속 보강 커밋의 2개
- 현재 후보의 T26/T40/T93: 두 목록을 합친 정확한 10개 검사
- 최초 T25-R: 원본 8개만 검사

### 3. T41·T43·T93

- T41: `allowed`가 비어 있으면 `analysis_error`; watched 영역은
  `visibility_only pass`, 의도 밖 변경은 owner approval로 명확히 구분
- T43: 임계값을 `debt-thresholds.yaml`로 분리하고 현재 후보의 측정 기준선
  `11 IDs / 12,488 lines / hotspot 4`에서 보정
- T93: ID별 실제 커밋 파일과 현재 manifest의 정확 범위를 비교해 누락은
  `block`, 과다 선언은 `approval`

이 검사로 BANK-OM-011의 공식 원본에 존재하지 않는 후보 전용 테스트 파일이
`watch`에 잘못 들어간 것도 발견해 제거했다.

### 4. T50·T51

- T50: 선언형 verifier가 필수인 실행에서 빈 검사 목록을 pass로 처리하지 않고
  `analysis_error`
- T51: 키 추가·삭제·타입 변경 외에 같은 타입의 scalar 값 변경과 list 내용
  변경도 경로 단위로 구조화 출력

## 3차에서 실제로 바뀐 것

`runtime_preflight.py`를 추가해 다음 값이 없거나 잘못됐으면 브라우저·API
테스트를 시작하기 전에 exit 3으로 차단한다.

- 행내 OpenMetadata URL과 인증 토큰
- 테스트용 query/assertion/table/column 식별값
- 실제 세 화면 URL
- 브라우저 로그인 storage-state
- 배포 산출물 `sha256` digest

비밀값은 결과에 출력하지 않는다. 이 사전검사는 runtime workflow에 연결됐다.
환경이 준비되면 기존 T62 실행기가 API·DB·검색·브라우저 테스트 결과를 제품
SHA·배포 digest·검사기 버전에 결속하고 90일 증거 artifact를 만든다.

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
T40   changed scope                   pass
T41   sensitive zone / intent         pass
T43   debt policy smoke               pass
T93   exact per-ID scope history      pass
```

T26는 BANK-OM-001~011 전체를 검사했다. BANK-OM-001은 등록 파일 48개,
필수 차단 파일 2개, contract 1개, 테스트 1개가 확인됐다.
BANK-OM-007은 원본 8개와 후속 2개를 합친 현재 후보 10개가 확인됐다.

T25-R 재구성 검사도 checkpoint `e1ffc5a1…`에서 통과했고 새 plan digest는
`sha256:05e653a8d91f49f7a4b73c0d14c27c0bd82a2d02714c7e19cee4b6914a07de98`다.

## 이제 실제 입력이 필요한 일

1. 다음 공식 OpenMetadata target SHA를 정하고 `run_upgrade_risk_gates.py` 실행
2. 실제 재적용 충돌 건수로 T43의 `conflict_rate` 입력
3. 행내 URL·토큰·테스트 데이터·배포 digest를 환경에 설정
4. `Runtime contracts`와 runtime patch-kill workflow 실행
5. 실제 결과 artifact를 근거로 운영 승인 또는 수정

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
