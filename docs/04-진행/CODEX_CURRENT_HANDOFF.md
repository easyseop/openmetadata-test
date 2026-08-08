# 현재 작업 인수인계

> 마지막 갱신: 2026-08-08 KST
>
> 현재 작업: Phase 안전 보완 완료, 고객용 버전 업그레이드 가이드는 사용자 요청으로 폐기
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
| 검사기 저장소 | 이 저장소 `easyseop/openmetadata-test` | 작업 branch `codex/om-1.13.1-rehearsal-baseline-20260806` · Docker workflow 기준 `80a4dd1f9b877bf7fae15515fa185f1f1fd0883d` · Runtime 고정 tag `om-1.13.1-rehearsal-runtime-v1` |
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

### 7.2 다른 컴퓨터용 Docker 전용 예행연습

다른 컴퓨터에서 Java·Maven·Python 없이 Docker Desktop과 Git만으로 같은 환경을
실행하도록 다음 묶음을 추가했습니다.

```text
docker/rehearsal/
├── README.md
├── start.sh
├── test.sh
├── stop.sh
├── common.sh
├── docker-compose.override.yml
├── Dockerfile.contract-runner
└── run_portable_contracts.sh
```

공개 image 이름은 다음과 같습니다.

- server: `ghcr.io/easyseop/openmetadata-bank:1.13.1-bank-8ac18ad0`
- Contract runner: `ghcr.io/easyseop/openmetadata-contract-runner:1.13.1-runtime`

고정 입력:

- 제품 candidate: `8ac18ad053d9274774e274ba17b35911ac0b9dcb`
- 검사기 tag: `om-1.13.1-rehearsal-runtime-v1`
- 검사기 commit: `7fdb182c299e51fd94a4a9c7d56473a3e849c019`
- 공식 Compose 기준: `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9`

GitHub Actions의 깨끗한 Ubuntu 장비에서 server 시작, 5종 DB 목 데이터 등록,
Runtime Contract 9개 실행까지 검증하는 워크플로도 추가했습니다.

- workflow: `.github/workflows/publish-rehearsal-images.yml`
- 최종 실행: `https://github.com/easyseop/openmetadata-test/actions/runs/31156553806`
- 최종 상태: server·Contract runner image 발행, 깨끗한 Ubuntu 환경 시작,
  목 데이터 등록, Runtime Contract 9개가 모두 성공
- 네트워크 보호: Maven 다운로드가 20분 동안 끝나지 않으면 프로세스를 강제
  종료하고 이미 받은 의존성을 보존한 채 최대 3회 재시도

공개 image 확인 결과:

- server: `ghcr.io/easyseop/openmetadata-bank:1.13.1-bank-8ac18ad0`
  - index digest: `sha256:a28ade3e3b2ab27c9f34ae4d1c745e295dc665df400a29b31a9f753374c58c00`
  - platform: `linux/amd64`, `linux/arm64`
- Contract runner: `ghcr.io/easyseop/openmetadata-contract-runner:1.13.1-runtime`
  - index digest: `sha256:08f27c0776c381a3d10b78c49a646f4939759ccfad95d241bcf3fd661047eca4`
  - platform: `linux/amd64`
- 두 image 모두 인증 없는 GHCR manifest 요청이 HTTP 200이므로 공개 pull 가능
- 원본 배포 tar.gz는 별도 공개 파일로 올리지 않았습니다. 다른 컴퓨터는 공개
  container image만 받습니다.

깨끗한 환경 증거:

- artifact: `docker-only-rehearsal-evidence`
- 보존 기한: `2026-11-05T07:09:15Z`
- candidate: `8ac18ad053d9274774e274ba17b35911ac0b9dcb`
- 검사기: `7fdb182c299e51fd94a4a9c7d56473a3e849c019`
- Contract: 9개 모두 `pass`, 재시도 없음
- 목 데이터: 서비스 5, DB 5, 스키마 5, 테이블 10, 검색 색인 테이블 10,
  데이터 품질 결과 10

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

## 10. Phase 번들링 격리 작업

현재 worktree branch는 `codex/phase-bundling`입니다. 기존 예행연습 branch와 제품
코드는 수정하지 않았습니다.

2026-08-07에 기존 개발계획을 검토해 다음 두 문서를 추가했습니다. 두 문서는
commit `7f7bf1b383`에 포함됐습니다.

- `docs/04-진행/PHASE_BUNDLING_개발설계_수정보완_20260807.md`
- `docs/04-진행/PHASE_BUNDLING_반례테스트케이스_20260807.md`

주요 보완 내용은 승인된 활성 candidate 포인터, 실행 단위 SHA 고정, 기존
CandidateLock schema 재사용, premerge·postmerge 분리, 입력 누락과 프로그램 실패
구분, 결과 digest 기반 승인 결속입니다. 테스트 명세는 C1~C114이며 P0는 C1~C74입니다.

이후 같은 branch에 commit `ae1bdbce4b`(L1)와 `446b5a0e53`(L2~L8)이 추가됐습니다.
Codex는 구현 코드를 수정하지 않고 독립 검토했습니다.

구현 완료보고, Codex 검토, 두 인수인계는 commit `cb225109d3`까지
`origin/codex/phase-bundling`에 push했습니다. 현재 남은 미추적 항목은 로컬 테스트
스킬뿐입니다.

```text
?? .claude/
```

`.claude/`는 stage하지 않습니다. 검토 결론은 phase 테스트 125개 통과와 별개로 P0 문제 6건이 남아 있어
운영 완료 승인을 할 수 없다는 것입니다. 정확한 문제와 다음 순서는
`PHASE_BUNDLING_진척_인수인계_20260807.md` 12절과
`PHASE_BUNDLING_CODEX_구현검토_20260807.md`를 확인합니다.

## 11. 2026-08-08 Phase 검토 보완 branch

Codex 독립 검토에서 확인한 P0 6건과 P1 2건은
`codex/phase-bundling-safety-fix-20260808`에서 수정했다. phase 명령, 실제
timeout, catalog 강제, 빈 후보 차단, 판단 근거 digest, 승인 메타데이터,
debt 정책 fail-closed와 detail 보존을 회귀 테스트로 고정했다. 기존 validate·
source runner와 선택적 Runtime Contract도 postmerge Phase에 연결했다.

구현 commit은 `7a963853c7554be60db64cd1ba1fc4ce1bad26ef`이다. 이 SHA 뒤의
인수인계 전용 commit은 구현 동작을 바꾸지 않는다.
원격 `origin/codex/phase-bundling-safety-fix-20260808`에 push했다.

현재 완료 상태는 **구현과 synthetic E2E 검증 완료**다. 실제 1.13.2
vendor-merge 후보의 postmerge 결과나 운영 승인 완료를 뜻하지 않는다. 상세 구현,
검증 명령, 외부 입력 대기 항목은
`PHASE_BUNDLING_진척_인수인계_20260807.md` 13절이 정본이다.

## 12. 2026-08-08 고객용 버전 업그레이드 가이드 폐기

고객사·솔루션 제공업체 관점으로 작성했던 독립 Markdown·HTML은
사용자 요청으로 삭제했다. 해당 가이드만을 위해 추가했던 renderer
`--stylesheet` 옵션도 원복했다. 삭제 대상은 Git 이력에서 복구할 수 있다.

기존 `예행연습-1.13.1-1.13.2` 11단계 문서, Phase 구현, 검사
증거와 제품 코드는 수정하지 않았다. 삭제한 가이드는 더 이상
Claude 검토 대상이 아니다.

## 13. 2026-08-08 외부 모델 설계 검토 요청서

다음 단일 Markdown에 Claude 초기 구현, Codex 보완, 제품 1.13.1→1.13.2
상태, 후속 commit·사람 판단 경계, 필수 설계 질문 20개를 정리했다.

- `docs/04-진행/PHASE_BUNDLING_외부모델_설계검토_요청서_20260808.md`

외부 모델은 이 문서를 먼저 끝까지 읽고 `dbf169b...`→`7a96385...`
diff와 코드·test를 직접 대조한다. 코드 수정·push 없이 P0·P1·P2,
반례 test, 최종 승인 권고만 작성한다. 폐기한 고객사 관점 HTML·Markdown은
검토 대상에서 제외했다.

검증: 문서가 참조하는 7개 commit 객체와 주요 설계·코드·test 파일의
존재를 확인했고, `.venv/bin/python -m pytest harness/tests/test_phase_cli.py -q`
결과는 `6 passed`이다. `git diff --check`도 통과했다.

## 14. 2026-08-08 외부 검토 후속 안전성·출력 보완

Claude 외부 검토에서 새로 확인한 artifact 결속, 공개 CLI run-id, 동시 기록,
3단 출력 무결성, 등록자료 digest, 공식 tag, conflict-rate 근거 문제를 보완했다.
`om_workflow.py`의 여섯 Phase 명령은 기본 `human` 요약을 출력하고 기존 자동화는
`--output-format json`으로 하위 실행기 JSON을 그대로 받을 수 있다.

현재 branch는 `codex/phase-bundling-safety-fix-20260808`이다. 구현 commit은
`cf17ed206de63a8dd4dfb88ca54cee6cd6a081c8`이다. 출력 초안·예시·Claude
검토 질문은 `PHASE_BUNDLING_출력형식_CLAUDE_검토요청_20260808.md`가 정본이다.

최종 집중 테스트는 `53 passed`, 전체 harness는 `543 passed, 38 skipped`, 실패
0건이다. skip은 실제 제품 ref·API·브라우저·실행 환경 입력이 필요한 기존
항목이며 PASS 증거로 계산하지 않았다.

조직 승인자의 실권한 확인은 코드 변경으로 완료 처리하지 않았다. 보호 branch,
CODEOWNERS 또는 사내 결재 ID·서명 정책이 필요하다. 실제 1.13.2 vendor-merge,
실측 conflict evidence, change-intent, build-artifact와 Runtime Contract, 운영 배포도
외부 입력 대기 상태다.

## 15. 2026-08-08 Claude 최종 검토 후속 묶음

Claude와 Codex의 재검토에서 기존 `net(base, candidate)` 조건이 병합 전 custom
변경을 증명하지 못한다는 데 합의했다. 최종 구현은 conflict evidence의
`custom_head_sha`를 승인된 이전 기준선 Candidate lock과 대조하고, custom head가
postmerge Candidate의 ancestor인지, `merge_base(target, custom_head)`가 현재
lock의 base인지 검사한다. `merge_changed_paths`는 base 대비 target·custom head
변경 경로 합집합과 완전 일치해야 하고, `conflicted_paths`는
`git merge-tree --write-tree` 재현 결과와 완전 일치해야 한다. Git 버전·명령·
result tree·원시 출력 digest·merge-driver 설정 digest·분자·분모·계산 비율은
canonical inputs에 포함된다.

추가 반영:

- `phase-status`가 canonical inputs의 `verification_scope`를 표시한다.
- scope 누락 구버전 증거와 source-only 결과는 운영 배포 금지로 표시한다.
- preflight는 누락 target을 다른 누락과 함께 수집하고 premerge 실행은 명확히 중단한다.
- reservation lock에 PID·host·시각·run-id를 기록하며 자동 삭제하지 않는다.
- conflict-rate는 선택 입력이고 판정에는 항상 경로에서 계산한 값을 사용한다.
- human 출력은 정렬 공백을 제거하고 긴 설명을 80열 기준으로 줄바꿈한다.
- premerge 뒤 vendor merge·새 lock 승인·candidate 재선택·postmerge 순서를 출력한다.
- `--registration-version`을 호환 별칭으로 추가했으며 `--version`은 폐기하지 않았다.

검증 결과:

```text
Phase·Git 집중: 182 passed, 1 skipped
전체 harness: 560 passed, 38 skipped
실패: 0
```

skip은 실제 제품 ref·외부 API·브라우저·환경 입력이 필요한 기존 항목이며 PASS에
포함하지 않았다. 최종 구현 commit은
`01a1a49d0f6354fa4a3c491e99543506357fcb4f`이다. rename/rename, add/add,
custom merge-driver와 attributes 동작은 합성 Git 반례로 고정했다. 실제 vendor
merge가 다른 merge-driver 설정을 쓰면 결과가
달라질 수 있으므로 같은 설정을 사용해야 하며, 실제 merge 로그 자동 수집은 후속
개발 항목이다. LLM G-룰은 참고자료로만 보관하고 구현하지 않았다.

## 16. 2026-08-08 새 검사기 병행 적용 화면 초안

사용자는 기존 1.13.1→1.13.2 예행연습과 새 Phase 검사기 개발이 별도 작업이며,
기존 11단계 가이드를 변경하지 않겠다고 다시 확정했다. 이에 원본 Markdown·HTML과
11개 단계별 페이지는 수정하지 않고 다음 비교 시안 HTML만 새로 만들었다.

```text
docs/00-사용가이드/예행연습-1.13.1-1.13.2/
OM_TEMP_1.13.1_1.13.2_예행연습_새검사기_병행적용_초안.html
```

첫 시안은 원본 11단계 옆에 검사 역할만 표시했으나, 통합 효과가 보이지 않는다는
사용자 피드백에 따라 비교 화면 안에서는 11단계를 7단계로 묶었다. 원본 1~2는
환경·branch 확인, 3~5는 BANK-OM 등록 준비, 6~7은 기준선 승인·검증으로 합쳤다.
원본 8은 공식 버전·병합 전 검사, 10은 종합 검사·승인 판단으로 유지하고, 사람의
코드·조직 판단이 필요한 원본 9 vendor merge와 11 tag·release는 독립 단계로
남겼다. 원본 파일과 현재 실행 절차는 수정하지 않았으며 실제 OM_TEMP에 적용한
결과가 아니라는 경계를 첫 화면과 출력 예시에 반복 표시했다.

검사기 검증 수치는 초안 생성 시점에 Phase·Git `182 passed, 1 skipped`, 전체
harness `560 passed, 38 skipped`, 실패 0건이었고, 2차 보완 후 HTML은 아래의
`188 passed, 1 skipped` / `566 passed, 38 skipped`로 갱신했다. 실제 OM_TEMP 1.13.2
종단 실행, 조직 승인, build artifact·Runtime Contract와 운영 배포는 이 시안의
완료 결과가 아니다. HTML parser와 `git diff --check`는 통과했다. 인앱 브라우저의
로컬 `file://` 이동은 URL 보안 정책이 차단했으므로 자동 시각 검수 완료를 주장하지
않는다. 현재 변경은 사용자 검토 전 초안이며 commit·push하지 않았다.

사용자 요청에 따라 같은 HTML에 7개 가이드별 `반드시 넣을 내용 / 강조할 부분 /
완료 결과와 중단 조건`을 나열식으로 추가했다. 외부 모델에 그대로 전달할 수 있는
검토 요청서는 다음 파일이다.

```text
docs/04-진행/PHASE_7단계_가이드구성_외부검토요청_20260808.md
```

검토 질문은 통합 범위의 적정성, 사람·자동 경계, 완료·중단 조건, 예시·복구·증거
누락과 최종 채택 여부다. 두 파일 모두 사용자 피드백 전 초안이며 원본 11단계
Markdown·HTML은 수정하지 않았다.

1차 외부 검토는 P0 없음, P1 2건, P2 6건, `수정 후 채택`으로 판정했다.
단계 번호를 `새 n단계(원본 n) · 검사기 [n/6]`로 통일하고, 재실행되는
candidate-select·preflight, APPROVAL의 실무자 검토, 승인 권한 미검증 경계,
Candidate 변경 시 재실행, custom head 완전 일치 제약, 잔존 lock·구버전 증거
예시, 당시 182건 테스트 파일 범위를 초안에 반영했다. 경로 원시 생성 Git
명령과 손으로 목록을 편집하지 말라는 경계를 표시했다. 이후 2차
검토를 반영해 공식 자동 수집기를 구현했으며, 현재 HTML은 원시 명령 대신
공개 수집 명령을 안내한다.

2차 Claude 검토에서 사용자 Git rename 설정에 따라 경로 집합이 달라지고,
custom merge driver digest를 기록만 하고 차단하지 않는 P1 2건을 확인했다.
`gitprim` 공통 Git 설정에 `diff.renames=false`, `merge.renames=false`,
`merge.directoryRenames=false`를 고정하고 net diff에 `--no-renames`를 명시했다.
허용 merge driver config digest의 기본값은 빈 설정 digest이며, 다른 설정이
있으면 merge-tree 실행 전 `GitPrimitiveError`로 fail-closed한다.

`om_workflow.py collect-conflict-evidence`를 추가했다. 승인된 이전 기준선
lock digest와 custom head를 명시하면 현재 활성 postmerge lock에서 base·target·
Candidate를 결속하고, byte 정렬된 `merge_changed_paths`와 `conflicted_paths`,
merge-tree·Git·config digest, harness digest를 YAML로 생성한다. 생성 즉시
`_bind_conflict_evidence`로 self-check하며 O_EXCL reservation, fsync, atomic replace를
사용하고 기존 출력은 덮어쓰지 않는다. 수정 후 집중 회귀는
`187 passed, 1 skipped`, 전체 harness는 `565 passed, 38 skipped`, 실패 0건이었다.

3차 Claude 검토에서 새 postmerge lock을 활성화하기 전에 수집기를 실행하면
`candidate_sha == custom_head_sha`, conflict-rate 0인 퇴화 증거가 남는 P1을 확인했다.
수집기와 `_bind_conflict_evidence` 모두 `custom_head == active candidate`를 거부하고
“활성 lock이 아직 병합 전 기준선” 복구 안내를 출력한다. 가이드의 순서는
`merge → 해결 commit → 새 lock 작성·승인·활성화 → candidate-select → 수집
→ preflight → postmerge`로 고정했다. rename 비활성 conflict-rate의 의미, custom
driver override 미지원 제약, `replay_config_digest`가 머신별로 달라질 수 있는
감사용 정보 필드임도 문서화했다. 구현 commit은
`6079aaff4d1b227df699d3f67262d60a96cd6b07`이며, 이 SHA 기준 집중 회귀는
`188 passed, 1 skipped`, 전체 harness는 `566 passed, 38 skipped`, 실패 0건이다.

## 17. 2026-08-09 PPT LLM 커스텀 운영과 Phase 검사기 역할 분석

사용자가 제공한 13장 PPT
`/Users/seop/Downloads/오픈메타데이터럴~.pptx`를 읽기 전용으로
분석했다. PPT 원본은 수정하지 않았고 저장소에 복사하지도 않았다.

분석·Claude 검토 요청서는 다음 파일이다.

```text
docs/04-진행/PPT_LLM커스텀운영_PHASE검사기_CLAUDE_검토요청_20260809.md
```

요청서는 PPT의 branch·commit·Markdown 4종·build·14개 test·버전
포팅·6개 점검·Claude skill 흐름을 현재 Manifest·Candidate lock·
premerge·conflict evidence·postmerge·Runtime Contract·phase-status에
대응시킰다. 각 항목을 현재 구현, 조건부 구현, 실환경 입력
대기, 사람 전용으로 구분했다. Claude에게는 코드 수정 없이
사실 대조, P0·P1·P2, 추가 반례 test, 최종 채택 권고만 요청한다.

이 작업 시작 HEAD는
`e2b445edbd057e611084f0194d8780b6683b0c5e`이다. 요청서 전체를
저장소의 가독성 스킬로 점검했고 `git diff --check`를 통과했다.

Claude CLI를 `--permission-mode plan`으로 실행했지만 다음 인증
오류로 응답 생성 전에 중단됐다.

```text
Not logged in · Please run /login
```

따라서 Claude 검토 완료를 주장하지 않는다. 다음 정확한 절차는
이 컴퓨터에서 Claude CLI `/login`을 완료한 뒤, 위 검토 요청서를
읽기 전용으로 다시 전달하고 응답을 별도 검토 결과 문서로
보존하는 것이다.

### 17.1 외부 Claude 검토 수신·반영

사용자가 별도 Claude 검토 결과를 전달했다. PPT SHA·13장 전문,
저장소 HEAD·구현 commit, `188 passed, 1 skipped`·`566 passed,
38 skipped`를 재현했고 최종 판정은 `수정 후 채택`이다.

반영 결과는 다음 문서가 정본이다.

```text
docs/04-진행/PPT_LLM커스텀운영_PHASE검사기_CLAUDE_검토반영_20260809.md
```

요청서에 PPT의 `KB-CUST-*`·`KB-CUSTOM-*` 혼용, 과거
1.12.8→1.12.13→1.13.1과 현재 1.13.1→1.13.2의 시점 차이,
patch-replay가 개별 도구만 있고 Phase postmerge에 미연결인 점,
PPT 14개 test는 Contract·fixture·runner 추가 개발이 필요한 점을
보정했다. LLM의 정책 자기 수정, run-id 재사용, digest 없는
Markdown 성공 표시도 금지 목록에 추가했다.

Claude가 P0로 표시한 3건은 검사기 코드 결함이 아니라 PPT 운영
규칙의 오용 위험이다. 현재 코드에 새 P0는 없다. trailer 없는
upstream commit은 T30 `CORE_CHANGE_WITHOUT_ID` `BLOCK`으로 이미 검출하며,
다음 집중 test를 재확인했다.

```text
./.venv/bin/python -m pytest \
  harness/tests/test_invariants.py::test_core_change_without_id_blocks_P0_5 -q

1 passed
```

임의로 적용하지 않은 외부 결정 필요 항목은 다음과 같다.

1. PPT 실행 전략을 vendor-merge로 전환할지 patch-replay Phase를 개발할지
2. `bootstrap/sql/**`을 `watched`에서 `protected`로 올릴지
3. 신뢰할 build-success gate의 CI·산출물 계약
4. PPT 14개의 Contract ID·fixture·runner·환경 owner
5. 조직 승인·release T91·서명·보존 정책

이 문서 batch의 범위는 이 인수인계서, Claude 검토 요청서,
Claude 검토 반영 문서 3개다. PPT·검사기 코드·정책 파일은
수정하지 않았다.
