# 현재 작업 인수인계

> 마지막 갱신: 2026-08-07 11:45 PDT
>
> 현재 작업: OM_TEMP 1.13.1 기준 코드의 5-4 Runtime Contract test 준비
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

## 4. 현재 중단된 작업

승인한 candidate `d952a838…`와 같은 코드로 OpenMetadata Docker 이미지를
만드는 작업을 실행했습니다. 이전 컨테이너의 revision은 `59dae915…`였으므로 공식 5-4
증거로 사용할 수 없었습니다.

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

`bash`와 `openjdk21-jre`를 설치하지 못해 Docker build가 종료 코드 2로
끝났습니다. 커스터마이징 코드나 Contract test 실패가 아니라 Docker 내부의
외부 package 다운로드 실패입니다. candidate image가 만들어지지 않았으므로
5-4 Runtime Contract test는 아직 시작하지 않았습니다.

완료된 Maven·UI 산출물을 재사용하도록 `-s true`를 지정해 한 번 재시도했지만,
`main`과 `community` package index가 다시 각각 timeout 되어 같은 종료 코드 2로
끝났습니다. 반복 재시도는 중단했습니다. 재시도 후 `docker ps`에는 실행 중인
컨테이너가 없습니다.

```bash
env JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home \
  PATH=/opt/homebrew/opt/openjdk@21/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin \
  ./docker/run_local_docker.sh -s true -i false -r false
```

화면의 dependency warning과 TypeScript declaration 진단은 해당 시점의
Maven·UI build를 중단시키지 않았습니다. 현재 차단 사유는 위 네트워크 timeout
한 가지입니다.

새 세션에서는 기존 터미널의 process를 제어할 수 있다고 가정하지 마십시오.
먼저 다음 명령으로 실행 여부를 확인합니다.

```bash
ps aux | grep '[r]un_local_docker.sh'
```

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
```

현재 빌드 process와 컨테이너는 모두 없습니다. 재시도 전 Alpine package 서버가
다시 응답하는지 확인하고, 위 `-s true` 명령으로 Maven·UI 산출물과 Docker
cache를 재사용합니다. 사용자에게 알리지 않고 JDK 버전을 바꾸거나 DB volume을
삭제하지 않습니다.

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

1. Alpine package 서버 연결이 복구됐는지 확인합니다.
2. 복구된 뒤 §4의 `-s true` 명령으로 Docker image build를 다시 실행합니다.
3. 성공하면 API revision과 Docker image 식별값을 확인합니다.
4. Runtime fixture와 비밀 환경값을 현재 terminal에만 준비합니다.
5. Runtime Contract test 9개를 실행합니다.
6. 실행 결과와 evidence 경로를 이 문서에 갱신합니다.
7. 가이드의 5-4 실제 결과를 갱신하고 전체 문서를 가독성 검토합니다.
8. 의도한 파일만 commit하고 현재 branch를 원격에 push합니다.
9. 그 뒤에만 1.13.2 vendor merge 단계로 이동합니다.

## 9. 중단 조건

- 실행 중인 OpenMetadata revision이 `d952a838…`과 다름
- Docker image 식별값을 확인할 수 없음
- 필요한 fixture 또는 인증값을 확인하지 못함
- Contract test가 skip, fail 또는 analysis error로 끝남
- 기존 사용자 변경과 현재 작업 변경을 안전하게 분리할 수 없음
- 네트워크 오류로 Maven·Yarn dependency 또는 Docker image를 받을 수 없음

중단 시 결과를 임의로 pass로 바꾸지 말고, 오류 원문·실행 명령·마지막 정상
단계·다음 재시도 명령을 이 문서에 남깁니다.
