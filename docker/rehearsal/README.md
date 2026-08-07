# Docker 전용 OM_TEMP 1.13.1 예행연습

## 1. 목적

이 실행 묶음은 다른 컴퓨터에서 OpenMetadata 소스를 빌드하지 않고 다음 환경을
재현합니다.

- 커스텀 1.13.1 OpenMetadata server
- MySQL과 Elasticsearch
- Oracle·Tibero·Sybase·DB2·PostgreSQL 목 메타데이터
- 정상 5건·의도적 실패 5건의 데이터 품질 결과
- Runtime Contract 9개

## 2. 준비

필요한 프로그램은 Docker Desktop과 Git입니다. Java·Maven·Python은 설치하지
않습니다. `curl`이 없는 환경에서는 Docker image로 공식 Compose 파일을 받습니다.
검사기 저장소에서 다음 branch를 사용합니다.

```text
codex/om-1.13.1-rehearsal-baseline-20260806
```

GitHub Container Registry image가 비공개 상태라면 최초 한 번 `docker login
ghcr.io`가 필요합니다. image를 공개로 전환하면 로그인 없이 받을 수 있습니다.

## 3. 환경 시작과 목 데이터 등록

검사기 저장소 최상위 폴더에서 실행합니다.

```bash
bash docker/rehearsal/start.sh
```

이 명령은 image를 받은 뒤 서버를 시작하고 목 메타데이터를 등록합니다. 정상 종료
시 다음 두 결과가 표시됩니다.

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
