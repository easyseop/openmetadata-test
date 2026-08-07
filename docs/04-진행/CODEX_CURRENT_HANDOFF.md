# 현재 작업 인수인계

> 마지막 갱신: 2026-08-07 14:35 PDT
>
> 현재 작업: 1.13.1 Runtime Contract 9개 정식 통과 및 원격 공유 완료
>
> 이 문서는 다음 세션이 가장 먼저 읽는 현재 상태 정본입니다.

## 1. 목적과 현재 위치

공식 OpenMetadata 1.13.1에 BANK-OM-001~007을 적용한 코드를 1.13.2로
업그레이드하기 전에 1.13.1 기능 기준선을 확정하는 작업입니다.

최초 등록 `plan → 승인 → apply`, 등록자료 검사, 소스 검사는 완료했습니다.
5-4 Runtime Contract는 깨끗한 검사기 worktree에서 9/9 정식 통과했습니다.
candidate SHA·image digest·검사기 commit이 묶인 증거도 생성했습니다.

1.13.2 vendor merge와 custom 코드 수정은 아직 실행하지 않습니다.

공유 원격은 다음 두 branch입니다.

- 검사기: `easyseop/openmetadata-test`의 `codex/om-1.13.1-rehearsal-baseline-20260806`
- 제품 코드: `easyseop/OpenMetadata`의 `codex/om-1.13.1-runtime-ready`

제품 코드를 `easyseop/OM_TEMP`에 처음 push했을 때 공식 Git 이력 객체 전송 중
GitHub HTTP 500이 발생했습니다. 공식 1.13.1 tag를 이미 가진 실제 fork
`easyseop/OpenMetadata`에는 정상 push됐습니다. 다른 컴퓨터에서는 위 실제 fork
branch를 사용합니다.

## 2. 저장소·branch·commit

| 역할 | 위치 | 현재 branch·commit |
|---|---|---|
| 검사기 저장소 | 이 저장소 `easyseop/openmetadata-test` | `codex/om-1.13.1-rehearsal-baseline-20260806` · Runtime 실행 기준 `c6e403125f953fef8f6b0757ac70d68aeeeca6f1` |
| OpenMetadata 코드 저장소 | `$HOME/om-work/om-temp-real-1.13.1` | `codex/om-1.13.1-runtime-ready` · `8ac18ad053d9274774e274ba17b35911ac0b9dcb` · `easyseop-fork` 추적 |
| 공식 1.13.1 기준 | 같은 코드 저장소 | `upstream-1.13.1-release` · `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9` |
| 공식 1.13.2 | 같은 코드 저장소 | `official/om-1.13.2` · 공식 `1.13.2-release` commit `2763bf97…` |

## 3. 완료된 기준선

- BANK-OM-001~007을 실제 공식 Git 이력에서 ID 순서대로 재구성했습니다.
- BANK-OM-005와 BANK-OM-007의 후속 보정 commit도 같은 ID 구간에 배치했습니다.
- 최종 custom HEAD는 `8ac18ad...`입니다.
- 최초 등록 제안·승인·apply를 다시 완료했습니다.
- 등록자료 검사 5개와 소스 검사 9개가 모두 `pass`입니다.
- 현재 등록 범위는 변경 경로 111개, 제외 경로 2개, 공용 경로 37개,
  공용 경로·ID 조합 114개, 코드 정의 assertion 790개입니다.
- 최신 검사 결과:
  - `evidence/om-1.13.1-runtime-ready-20260807-01/`
  - `evidence/om-1.13.1-runtime-ready-validation-20260807-01/`

## 4. Docker 실행 상태

| 항목 | 현재 값 |
|---|---|
| candidate image | `development-openmetadata-server:candidate-8ac18ad0` |
| image digest | `sha256:96854a63064e563d8a1ce8f9289e3d8b2aad35a0d78836badf7cd7409aff7319` |
| image revision label | `8ac18ad053d9274774e274ba17b35911ac0b9dcb` |
| 임시 Dockerfile | `/private/tmp/OM_TEMP_Dockerfile.offline-candidate` |
| 임시 Compose override | `/private/tmp/OM_TEMP_docker-compose.offline-candidate.yml` |

Maven 전체 package는 성공했습니다. 로컬 image는 네트워크가 필요한 Alpine package
재다운로드를 피하고 기존 JDK 21 runtime layer에 새 배포 산출물을 넣어 만들었습니다.
MySQL·Elasticsearch·OpenMetadata server는 현재 `healthy`입니다.

## 5. 인증 시간 문제와 처리

Colima VM 시간이 호스트보다 약 16시간 느려 1시간 로그인 token이 발급 즉시
만료됐습니다. 무제한 token은 만들지 않았습니다. 로컬 예행연습 DB의
`loginConfiguration.jwtTokenExpiryTime`만 86400초로 바꾸고 server를 재시작했습니다.
현재 API와 브라우저 로그인이 정상입니다.

이 변경은 제품 코드나 등록자료가 아니라 현재 로컬 Docker DB 설정입니다. 다른
환경에서는 먼저 시계를 동기화하고 운영 인증 정책을 임의로 변경하지 않습니다.

## 6. Runtime Contract 결과

범용 준비 도구를 추가했습니다.

```text
harness/prepare_runtime_contract_environment.py
```

이 도구는 로그인, Query·실패 test case·확장 컬럼 table fixture, 브라우저 로그인
상태, 실행 image digest를 한 번에 준비해 `/private/tmp/om-runtime-contract.env`에
권한 600으로 저장합니다. 인증정보는 Git과 인수인계에 기록하지 않습니다.

2026-08-07 정식 실행 결과는 `pass`입니다.

- API Contract 6개 통과
- 브라우저 Contract 3개 통과
- pass 9, skip 0, fail 0, error 0
- 제품 candidate: `8ac18ad053d9274774e274ba17b35911ac0b9dcb`
- 검사기 commit: `c6e403125f953fef8f6b0757ac70d68aeeeca6f1`
- 실행 image: `sha256:96854a63064e563d8a1ce8f9289e3d8b2aad35a0d78836badf7cd7409aff7319`
- 정식 증거: `evidence/om-1.13.1-runtime-20260807-01/`

한글 IME Contract는 기존에 모든 조합 단계를 한 JavaScript 작업 안에서 실행해
React가 단계 사이에 렌더링할 수 없었습니다. 실제 IME처럼 각 조합 단계를 별도
브라우저 작업으로 실행하도록 바꿨습니다. 같은 실행 image에서 `ㅎ → 하 → 한 →
한ㄱ → 한그 → 한글`이 단계별로 유지되고 최종 값 `한글`을 확인했습니다.

## 7. 현재 의도한 변경

- `harness/acgh/registration_prep.py`
- `harness/tests/test_registration_prep.py`
- `harness/prepare_runtime_contract_environment.py`
- `tests/bank/contracts/test_korean_ime.py`
- `harness/registrations/om-temp-1.13.1/manifests/BANK-OM-005.yaml`
- `harness/registrations/om-temp-1.13.1/manifests/BANK-OM-007.yaml`
- `harness/registrations/om-temp-1.13.1/commit-inventory.yaml`
- `harness/registrations/om-temp-1.13.1/current-diff-paths.txt`
- 5-4 가이드 Markdown·HTML
- 이 인수인계
- `om-1.13.1-runtime-ready-*` plan·검사 evidence

### 7.1 API 목 메타데이터 시연 환경

재실행 가능한 목 메타데이터 등록 도구를 추가했습니다.

```text
harness/create_mock_database_metadata.py
```

이 도구는 실제 원천 DB에 연결하지 않고 OpenMetadata API로 Oracle·Tibero·Sybase·
DB2·PostgreSQL 서비스와 DB·스키마·테이블·컬럼을 등록합니다. 각 DB에는 고객 및
계좌 거래 테이블과 화면 확인용 데이터 품질 정상 1건·의도적 실패 1건을 만듭니다.
동일한 FQN이 있으면 재사용하므로 다시 실행해도 중복 생성되지 않습니다.

2026-08-07 확인 결과:

- 서비스 5, DB 5, 스키마 5, 테이블 10
- Elasticsearch `table_search_index`에서 테이블 10개 검색 확인
- 데이터 품질 Test Case 10개: Success 5, Failed 5
- 내부 MySQL에서 서비스 5, DB 5, 스키마 5, 테이블 10, Test Case 10 확인
- 결과: `evidence/mock-database-metadata-20260807-01/result.json`
- 화면 예시: `http://127.0.0.1:8585/table/bank_mock_oracle.oracle_bank.banking.customer/profiler/data-quality`

제품 코드 커스터마이징은 추가하지 않았습니다. Tibero·Sybase 유형은 현재 candidate에
이미 구현되어 있고, 나머지는 OpenMetadata 공통 메타데이터·데이터 품질 API를 사용합니다.

다음 미추적 자료는 기존 사용자 파일이므로 수정·삭제·stage하지 않습니다.

- `docs/00-사용가이드/OM_TEMP_wiki_context_logic_Claude_review_package_20260730 2/`
- `docs/00-사용가이드/OM_TEMP_wiki_context_logic_Claude_review_package_20260730.zip`
- `docs/00-사용가이드/OM_TEMP_wiki_context_logic_Claude_review_package_20260730/`
- `evidence/om-1.13.1-initial-bootstrap-20260806-01/`

## 8. 다음 실행 순서

1. 다른 세션에서는 위 두 원격 branch와 이 문서를 먼저 확인합니다.
2. 정식 evidence의 candidate·검사기·image digest가 이 문서와 같은지 확인합니다.
3. 사용자 지시 후 1.13.2 vendor merge 단계로 이동합니다.

정식 실행 명령:

```bash
source /private/tmp/om-runtime-contract.env
```

```bash
./.venv/bin/python harness/om_workflow.py runtime \
  --repo "$HOME/om-work/om-temp-real-1.13.1" \
  --version 1.13.1 \
  --artifact-digest "$DEPLOYED_ARTIFACT_DIGEST" \
  --run-id "om-1.13.1-runtime-20260807-01"
```

## 9. 중단 조건

- 실행 image revision과 제품 코드 HEAD가 다름
- Runtime preflight가 `ready: false`
- 필수 Contract가 skip·fail·error
- 정식 runner가 제품 또는 검사기 worktree의 미반영 변경을 감지함
- 기존 사용자 변경과 현재 변경을 안전하게 분리할 수 없음
- 네트워크 오류가 의존성 또는 image 준비를 실제로 막음

중단 시 pass로 바꾸지 말고 오류 원문, 마지막 정상 단계, 다음 재시도 명령을 이
문서에 기록합니다.
