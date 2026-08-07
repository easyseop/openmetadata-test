# 현재 작업 인수인계

> 마지막 갱신: 2026-08-07 13:00 PDT
>
> 현재 작업: BANK-OM-007 공용 generated file 누락 수정 전 중단
>
> 이 문서는 다음 세션이 가장 먼저 읽는 현재 상태 정본입니다.

## 1. 작업 목적과 현재 위치

OpenMetadata 공식 1.13.1에 BANK-OM-001~007 커스터마이징을 적용한 코드를
1.13.2로 업그레이드하기 전에, 1.13.1 기능 기준선을 먼저 남기는 작업입니다.

현재까지 최초 등록자료의 `plan → 승인 → apply`, 등록자료 검사, 소스 검사는
완료했습니다. 지금은 실행 중인 OpenMetadata가 승인한 1.13.1 candidate commit과
같은 코드로 만들어졌는지 확인한 뒤 Runtime Contract test 9개를 실행하는
5-4 단계입니다. 1.13.2 코드는 아직 병합하지 않습니다.

## 2. 저장소·branch·commit

| 역할 | 위치 | 현재 branch·commit |
|---|---|---|
| 검사기 저장소 | 이 저장소 `easyseop/openmetadata-test` | `codex/om-1.13.1-rehearsal-baseline-20260806` · 작업 시작 기준 `b5d5c922387f8041e1f04153378e266be104e11d` |
| OpenMetadata 코드 저장소 | `$HOME/om-work/om-temp-real-1.13.1` | `codex/om-1.13.1-id-series-upstream` · `d952a83896940116d3d6022323ad76bfe60991e8` |
| 1.13.2 공식 코드 branch | 같은 OpenMetadata 코드 저장소 | `official/om-1.13.2` · 공식 `1.13.2-release` commit `2763bf97…` |

현재 작업 branch는 같은 이름의 `origin` branch를 추적합니다. 가이드·검토서·
1.13.2 병합 전 증거를 함께 공유한 commit은 `e1258a8e80`입니다. 이 인수인계만
후속 갱신한 최신 commit은 `git log -1 --oneline`으로 확인합니다.
`origin/claude/markdown-file-feedback-26933w`는 날짜상 최근 원격 branch이지만
현재 5-4 작업 branch가 아니므로 대신 사용하지 않습니다.

## 3. 완료된 작업

1. BANK-OM-001~007을 각각 구분한 1.13.1 commit series를 구성했습니다.
2. 실제 공식 OpenMetadata Git 이력에서 시작한 candidate branch를 만들었습니다.
3. 재구성 검사는 `pass`입니다.
4. 1.13.1 최초 등록 제안·승인·apply를 완료했습니다.
5. 등록자료 검사 5개가 모두 `pass`입니다.
6. 소스 검사 9개가 모두 `pass`입니다.
   - 등록 경로 111개
   - 제외 경로 2개
   - 공용 경로 37개
   - 공용 경로·BANK-OM ID 조합 114개
   - 코드 정의 assertion 790개
7. Claude가 1.13.1→1.13.2 병합 전 읽기 전용 검사를 수행했습니다.
   - T42: `approval`, 영향 ID 001·002·003·004·006·007
   - T93 exact scope: `pass`
   - T93 policy drift: BANK-OM-004 감시 경로 1건 재매핑 필요
   - T41: change-intent 입력이 없어 `analysis_error`
   - T43: 승인된 conflict-rate가 없어 `not_evaluated`
   - vendor merge와 custom 코드 수정은 실행하지 않았습니다.

## 4. Docker candidate 실행 상태

승인한 candidate `d952a838…`와 같은 코드로 OpenMetadata Docker 서비스를
실행했습니다. 이전 컨테이너의 revision `59dae915…`는 더 이상 사용하지 않습니다.

첫 빌드는 시스템 JDK 26 때문에 중단됐습니다. 프로젝트가 요구하는 JDK 21을
설치한 뒤 아래 명령으로 다시 시작했습니다.

```bash
env JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home \
  PATH=/opt/homebrew/opt/openjdk@21/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin \
  ./docker/run_local_docker.sh -i false -r false
```

Maven과 UI production build는 완료됐습니다. 이후 Docker image를 만드는
단계에서 Alpine package 서버 접속이 두 번 timeout 되어 중단됐습니다.

```text
https://dl-cdn.alpinelinux.org/alpine/v3.24/main/aarch64/APKINDEX.tar.gz:
Operation timed out

https://dl-cdn.alpinelinux.org/alpine/v3.24/community/aarch64/APKINDEX.tar.gz:
Operation timed out
```

`bash`와 `openjdk21-jre`를 설치하지 못해 원본 Dockerfile build는 종료 코드 2로
끝났습니다. 커스터마이징 코드나 Contract test 실패가 아니라 Docker 내부의
외부 package 다운로드 실패입니다.

완료된 Maven·UI 산출물을 재사용하도록 `-s true`를 지정해 재시도했지만,
`main`과 `community` package index가 다시 각각 timeout 되어 같은 종료 코드 2로
끝났습니다. 원본 Dockerfile의 반복 재시도는 중단했습니다.

```bash
env JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home \
  PATH=/opt/homebrew/opt/openjdk@21/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin \
  ./docker/run_local_docker.sh -s true -i false -r false
```

대신 기존 로컬 OpenMetadata image의 JDK 21·bash runtime layer를 재사용하고,
완성된 `openmetadata-dist/target/openmetadata-1.13.1.tar.gz`만 교체한 별도
candidate image를 만들었습니다. 제품 저장소와 원본 Compose 파일은 수정하지
않았습니다.

| 항목 | 현재 값 |
|---|---|
| candidate image | `development-openmetadata-server:candidate-d952a838` |
| image digest | `sha256:85138760e3da7a037bfbe882f8a6c509dae93aac8a0abee2e792fd64e13c9352` |
| image revision label | `d952a83896940116d3d6022323ad76bfe60991e8` |
| 임시 Dockerfile | `/private/tmp/OM_TEMP_Dockerfile.offline-candidate` |
| 임시 Compose override | `/private/tmp/OM_TEMP_docker-compose.offline-candidate.yml` |

Compose override는 `execute-migrate-all`과 `openmetadata-server`만 위 candidate
image로 바꿉니다. 기존 DB volume은 삭제하지 않았습니다. migration 종료 코드는
0이며 MySQL·Elasticsearch·OpenMetadata server가 모두 `healthy`입니다.

새 세션에서는 기존 터미널의 process를 제어할 수 있다고 가정하지 마십시오.
먼저 다음 명령으로 실행 여부를 확인합니다.

```bash
ps aux | grep '[r]un_local_docker.sh'
```

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
```

현재 빌드 process는 없고 candidate 컨테이너 3개가 실행 중입니다. Alpine package
서버 timeout은 원본 base image를 처음부터 다시 만들 때는 여전히 문제지만,
현재 5-4 Runtime test 진행을 막지는 않습니다. 사용자에게 알리지 않고 JDK
버전을 바꾸거나 DB volume을 삭제하지 않습니다.

## 5. 빌드 완료 직후 확인할 값

다음 API가 반환하는 `revision`이 반드시 승인한 candidate
`d952a83896940116d3d6022323ad76bfe60991e8`과 같아야 합니다.

```bash
curl -fsS http://127.0.0.1:8585/api/v1/system/version | jq '{version, revision}'
```

정상 기준:

```json
{
  "version": "1.13.1",
  "revision": "d952a83896940116d3d6022323ad76bfe60991e8"
}
```

2026-08-07 확인 결과는 정상 기준과 일치합니다. 현재 Docker image 식별값은
`sha256:85138760e3da7a037bfbe882f8a6c509dae93aac8a0abee2e792fd64e13c9352`입니다.

revision이 다르면 Runtime Contract test를 실행하지 않고 중단합니다. 컨테이너
이미지 식별값은 다음 명령으로 확인하며 `DEPLOYED_ARTIFACT_DIGEST` 입력에
사용합니다.

```bash
docker inspect --format '{{.Image}}' openmetadata_server
```

## 6. 5-4 Runtime Contract test의 남은 입력

Contract 9개 가운데 실행 전에 11개 환경값이 필요합니다.

- 공통 연결: `OPENMETADATA_BASE_URL`, `OPENMETADATA_AUTH_TOKEN`
- QueryReport fixture: `BANK_CONTRACT_QUERY_ID`
- DataAssertions fixture: `BANK_FAILED_ASSERTION_FQN`, `BANK_DATA_ASSERTIONS_URL`
- 확장 컬럼 fixture: `BANK_COLUMN_TABLE_FQN`, `BANK_COLUMN_NAME`, `BANK_COLUMN_UI_URL`
- 한글 IME 화면: `BANK_IME_EDITOR_URL`, `BANK_BROWSER_STORAGE_STATE_B64`
- 실행 이미지 고정: `DEPLOYED_ARTIFACT_DIGEST`

토큰과 브라우저 인증 상태는 문서·Git·인수인계에 기록하지 않습니다. fixture는
실행 중인 candidate 환경에서 실제로 만들거나 기존 값을 확인한 뒤 사용합니다.
값을 추측해서 넣거나 skip을 pass로 기록하지 않습니다.

Playwright Python 1.62.0과 Chromium은 검사기 `.venv`에 설치했습니다. headless
Chromium으로 `http://127.0.0.1:8585`에 접속하고 페이지 제목 `OpenMetadata`를
확인했습니다.

로컬 예행연습 fixture도 만들었습니다.

| 환경변수 | 준비한 값 |
|---|---|
| `BANK_CONTRACT_QUERY_ID` | `0df8e7ef-291b-40c5-b018-9a68071e5814` |
| `BANK_FAILED_ASSERTION_FQN` | `bank_contract_runtime.bank_contract_db.bank_contract_schema.bank_contract_table.bank_contract_column.bank_contract_column_not_null` |
| `BANK_COLUMN_TABLE_FQN` | `bank_contract_runtime.bank_contract_db.bank_contract_schema.bank_contract_table` |
| `BANK_COLUMN_NAME` | `bank_contract_column` |

브라우저를 제외한 Contract를 사전 실행한 결과 7개 중 5개가 통과하고 2개가
실패했습니다. QueryReport 실패는 API가 `ChangeEvent`를 반환하는데 검사기가
`id`를 Query ID로 해석한 검사 오류였습니다. `entityId`를 우선 확인하도록
수정한 뒤 Tibero를 제외한 6개 사전 검사가 모두 통과했습니다.

Tibero 실패는 실제 candidate 누락입니다. 과거 원본 commit `7d19c89526`의
`serviceConnection.ts`에는 `Tibero = "Tibero"`가 있지만, 현재 BANK-OM-007
commit `d952a83896`은 이 공용 generated file을 포함하지 않습니다. 현재 candidate
SHA와 Docker image로 5-4 전체 PASS를 진행하면 안 됩니다.

환경값이 준비되면 검사기 저장소에서 다음 명령을 실행합니다.

```bash
./.venv/bin/python harness/om_workflow.py runtime \
  --repo "$OM_CODE_REPO" \
  --version 1.13.1 \
  --artifact-digest "$DEPLOYED_ARTIFACT_DIGEST" \
  --run-id "om-1.13.1-baseline-<실행ID>"
```

완료 조건은 필수 selector 9개가 모두 실행되고 모두 통과하는 것입니다. 환경값
부족으로 실행되지 않은 test는 5-4 완료로 처리하지 않습니다.

## 7. 현재 변경 파일과 보존 대상

현재 검사기 저장소의 의도한 변경은 다음과 같습니다.

- `AGENTS.md`
- `docs/04-진행/CODEX_CURRENT_HANDOFF.md`
- `docs/04-진행/CODEX_클로드_하네스경량화_스킬자동화_비판검토_20260807.md`
- 5-4 설명을 보강한 등록·승인·기준검사 가이드 Markdown과 HTML
- Claude가 만든 `evidence/om-1.13.2-premerge-20260807-premerge-01/` 증거 2개

다음 미추적 파일은 이전부터 있던 사용자 자료입니다. 현재 작업 범위로 간주하지
말고 수정·삭제·stage하지 않습니다.

- `docs/00-사용가이드/OM_TEMP_wiki_context_logic_Claude_review_package_20260730 2/`
- `docs/00-사용가이드/OM_TEMP_wiki_context_logic_Claude_review_package_20260730.zip`
- `docs/00-사용가이드/OM_TEMP_wiki_context_logic_Claude_review_package_20260730/`
- `evidence/om-1.13.1-initial-bootstrap-20260806-01/`

## 8. 다음 작업 순서

1. BANK-OM-007 재구성 입력에 `serviceConnection.ts`의 Tibero 정의를 추가합니다.
2. 공식 1.13.1에서 BANK-OM-001~007을 다시 재구성하고 새 candidate SHA를 만듭니다.
3. 재구성·등록자료·소스 검사를 다시 실행합니다.
4. 새 candidate SHA 기준으로 최초 등록 plan·승인·apply를 다시 수행합니다.
5. 새 candidate image를 만들고 API revision과 image digest를 다시 고정합니다.
6. 세 UI URL을 확정하고 로그인 browser storage state를 현재 terminal에만 준비합니다.
7. Runtime preflight가 `ready: true`인지 확인합니다.
8. Runtime Contract test 9개를 실행합니다.
9. 실행 결과와 evidence 경로를 이 문서에 갱신합니다.
10. 그 뒤에만 1.13.2 vendor merge 단계로 이동합니다.

## 9. 중단 조건

- 실행 중인 OpenMetadata revision이 `d952a838…`과 다름
- Docker image 식별값을 확인할 수 없음
- 필요한 fixture 또는 인증값을 확인하지 못함
- Contract test가 skip, fail 또는 analysis error로 끝남
- 기존 사용자 변경과 현재 작업 변경을 안전하게 분리할 수 없음
- 네트워크 오류로 Maven·Yarn dependency 또는 Docker image를 받을 수 없음
- BANK-OM 원본에 있던 코드가 ID별 candidate에서 누락됨

중단 시 결과를 임의로 pass로 바꾸지 말고, 오류 원문·실행 명령·마지막 정상
단계·다음 재시도 명령을 이 문서에 남깁니다.
