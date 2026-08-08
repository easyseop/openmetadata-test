# Docker 전용 OM_TEMP 1.13.1 예행연습

## 1. 목적

이 실행 묶음은 다른 컴퓨터에서 OpenMetadata 소스를 빌드하지 않고 다음 환경을
재현합니다.

- 커스텀 1.13.1 OpenMetadata server
- MySQL과 Elasticsearch
- Oracle·Tibero·Sybase·DB2·PostgreSQL 목 메타데이터
- 정상 5건·의도적 실패 5건의 데이터 품질 결과
- Runtime Contract 9개: 커스텀 기능의 API·화면 동작 검사

## 2. 준비

필요한 프로그램은 Docker Desktop과 Git입니다. Java·Maven·Python은 설치하지
않습니다. `curl`이 없는 환경에서는 Docker image로 공식 Compose 파일을 받습니다.
다른 컴퓨터에서는 먼저 기존 clone이 있는지 확인합니다. 기존 clone 확인부터
1.13.2 예행연습 재개까지의 전체 절차는
[다른 노트북 재개 환경 구성 가이드](../../docs/00-사용가이드/예행연습-1.13.1-1.13.2/OM_TEMP_다른노트북_재개_환경구성_20260809.html)를
따릅니다.

새로 clone해야 할 때는 현재 검사기 작업 branch를 받습니다.

```bash
git clone \
  --branch codex/phase-bundling-safety-fix-20260808 \
  --single-branch \
  https://github.com/easyseop/openmetadata-test.git
```

```bash
cd openmetadata-test
```

이후 명령은 모두 이 폴더에서 실행합니다. 제품 코드 저장소를 별도로 clone하거나
OpenMetadata를 직접 build할 필요는 없습니다.

**입력:** Docker image를 받을 수 있는 네트워크와 실행 중인 Docker Desktop

**산출물:** 커스텀 OpenMetadata·MySQL·Elasticsearch 컨테이너와 검사 증거 파일

검사기 저장소에서 사용하는 branch는 다음 값으로 고정합니다.

```text
codex/phase-bundling-safety-fix-20260808
```

이 branch에 Docker 실행 파일과 최신 가이드가 있습니다. Runtime Contract 실행 코드는
별도 tag와 commit으로 고정됩니다. 따라서 branch에 새 문서나 Phase 검사기 코드가
추가되어도 1.13.1 기준환경에서 실행하는 Contract가 자동으로 바뀌지 않습니다.

```text
tag: om-1.13.1-rehearsal-runtime-v1
commit: 7fdb182c299e51fd94a4a9c7d56473a3e849c019
```

검사 결과에는 위 commit과 제품 candidate commit이 함께 기록됩니다.

```text
제품 candidate commit: 8ac18ad053d9274774e274ba17b35911ac0b9dcb
검사기 commit: 7fdb182c299e51fd94a4a9c7d56473a3e849c019
```

두 GitHub Container Registry image는 공개 상태입니다. `docker login ghcr.io` 없이
받을 수 있습니다.

이 실행 묶음에서 자동으로 받는 핵심 image는 다음과 같습니다.

| 역할 | image | 포함 내용 |
|---|---|---|
| 커스텀 OpenMetadata | `ghcr.io/easyseop/openmetadata-bank:1.13.1-bank-8ac18ad0` | 제품 candidate `8ac18ad...`의 server와 migration |
| Runtime Contract 실행기 | `ghcr.io/easyseop/openmetadata-contract-runner:1.13.1-runtime` | Python·Playwright·9개 Contract 실행 환경 |
| 목 데이터 적재기 | `python:3.12-alpine` | 5종 DB 목 메타데이터 API 등록 |

서버 image는 `linux/amd64`와 `linux/arm64`를 지원합니다. Contract runner는
`linux/amd64`이며 ARM 기반 Docker Desktop에서는 에뮬레이션으로 실행됩니다.

```text
server digest: sha256:a28ade3e3b2ab27c9f34ae4d1c745e295dc665df400a29b31a9f753374c58c00
Contract runner digest: sha256:08f27c0776c381a3d10b78c49a646f4939759ccfad95d241bcf3fd661047eca4
```

MySQL·Elasticsearch 설정은 공식 OpenMetadata 1.13.1 Compose 파일을 사용합니다.
Compose 파일도 공식 commit `afcb2d2...`의 주소로 고정되어 있습니다.

2026-08-07에 깨끗한 Ubuntu 장비에서 환경 시작, 목 데이터 등록, Runtime Contract
9개를 확인했습니다. 결과는 [GitHub Actions 실행 31156553806](https://github.com/easyseop/openmetadata-test/actions/runs/31156553806)에서 확인할 수 있습니다.

## 3. 환경 시작과 목 데이터 등록

검사기 저장소 최상위 폴더에서 실행합니다.

```bash
bash docker/rehearsal/start.sh
```

이 명령은 image를 받은 뒤 서버를 시작하고 목 메타데이터를 등록합니다. 정상 종료
시 다음 두 결과가 표시됩니다.

처음 실행할 때는 image를 받아야 하므로 이후 실행보다 오래 걸릴 수 있습니다.

```text
[완료] OpenMetadata: http://127.0.0.1:8585
[완료] 목 데이터 결과: .../var/rehearsal/evidence/mock-database-metadata-result.json
```

`[중단]`이 나오면 다음 단계로 이동하지 않습니다. Docker Desktop 실행 여부와
함께 다음 명령의 결과를 확인합니다.

```bash
docker compose version
```

## 4. Runtime Contract 9개 실행

서버 시작이 완료된 뒤 실행합니다.

```bash
bash docker/rehearsal/test.sh
```

정상 결과는 `pass 9, fail 0, error 0, skipped 0`입니다. 결과는 다음 폴더에
남습니다.

```text
var/rehearsal/evidence/om-1.13.1-portable-runtime-<실행시각>/
```

하나라도 `fail`, `error`, `skipped`이면 검사를 통과한 것으로 기록하지 않습니다.

## 5. 화면 확인

브라우저에서 다음 주소를 엽니다.

```text
http://127.0.0.1:8585
```

기본 계정은 `admin@open-metadata.org`이며 로컬 예행연습 기본 비밀번호는 `admin`입니다.
Oracle 고객 테이블의 데이터 품질 화면 예시는 다음 주소입니다.

```text
http://127.0.0.1:8585/table/bank_mock_oracle.oracle_bank.banking.customer/profiler/data-quality
```

## 6. 환경 중지

```bash
bash docker/rehearsal/stop.sh
```

컨테이너는 삭제하지만 MySQL·Elasticsearch 데이터는 보존하므로 다시 시작하면 기존
목 데이터를 재사용합니다. 데이터 볼륨 삭제는 복구가 필요한 기존 결과까지 지우므로
이 가이드에서 자동 실행하지 않습니다.
