# Codex 작업 인수인계

> 갱신 기준: 2026-07-28 11:41 KST
> 거버넌스 저장소: `easyseop/openmetadata-test`
> 작업 브랜치: `codex/strict-manifest-gates`
> 문서 묶음 작성 전 기준 commit: `0a6d009107a18e69a2150388442adffb6332f08c`
> 제품 코드 상태: `easyseop/OpenMetadata` commit
> `849ae756cd238f218b5e3a6c795a392305cb32ee`
> 공유문서·스킬 최초 로컬 commit: `becb18e` (이후 보강은 현재 브랜치의 `git log`로 확인)
> 원격 push: 행내 커스터마이징 정보의 외부 GitHub 전송 승인 확인 전까지 대기

이 문서는 다른 노트북이나 새 작업에서 바로 이어가기 위한 현재 정본이다.
과거 Claude 작업의 상세 기록은
[`CLAUDE_REVIEW_HANDOFF.md`](CLAUDE_REVIEW_HANDOFF.md)에 남아 있지만, 공유문서
1차·2차·3차 작업은 이 문서와
[`SHARING_ARTIFACT_REQUIREMENTS.md`](SHARING_ARTIFACT_REQUIREMENTS.md)를 먼저
따른다.

## 1. 저장소와 브랜치

| 구분 | 저장소와 브랜치 | 의미 |
|---|---|---|
| 행내 배포용 OpenMetadata 소스 | `easyseop/OpenMetadata` 브랜치 `codex/bank-vendor-1.13.1-rebuild` | 공식 원본 위에 승인된 BANK-OM 커스터마이징을 적용한 코드 상태 |
| 현재 로컬 제품 검토 브랜치 | `codex/strict-gate-validation` | remote 이름이 `candidate`인 위 제품 브랜치를 추적하며 검사에 사용 |
| 변경관리·검사 저장소 | `easyseop/openmetadata-test` 브랜치 `codex/strict-manifest-gates` | BANK-OM 변경관리표, 검사기, 테스트, 공유문서와 인수인계를 관리 |
| 공식 원본 | `open-metadata/OpenMetadata` `1.13.1-release` commit `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9` | 현재 커스터마이징 적용 기준 |

`easyseop/OpenMetadata`의 기본 브랜치에 행내 커스터마이징이 보이지 않는 것은
이상 상태가 아니다. 현재 커스터마이징은 위의 별도 제품 브랜치에 있으며,
BANK-OM 변경관리 정보와 검사기는 `easyseop/openmetadata-test`에 있다.

## 2. 공유문서 진행 상태

| 단계 | 현재 상태 | 저장된 파일 | 다음 결정 |
|---|---|---|---|
| 1차 | 목적과 브랜치 전략은 사용자 검토를 통과했다. 전체 문서는 최종 승인 전 검토본이다. | `docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-fragment.html`, `openmetadata-phase1-sharing-preview.html` | 현재 파일 하단에는 이전 통합안의 검사기·결과·로드맵도 남아 있다. 3차를 만들 때 2차·3차와 중복되는 하단 내용을 분리하고 최종 통합본에서 한 번만 설명 |
| 2차 | 검사 방법과 예외 가능성을 상세히 보강한 검토본이다. 사용자 최종 승인은 아직 받지 않았다. | `docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-fragment.html`, `openmetadata-phase2-verifier-table-preview.html` | 사용자 피드백을 받은 뒤 문장 길이를 줄이되 검사 원리와 예외 설명은 유지 |
| 3차 | 실제 제품 코드·BANK-OM-001 Manifest·Git 기록·소스 검사 결과를 연결한 HTML 초안을 만들었다. 화면 캡처와 실제 공식 업그레이드·행내 환경 결과는 아직 없다. | `docs/00-사용가이드/공유문서/openmetadata-phase3-demo-fragment.html`, `openmetadata-phase3-demo-preview.html` | 사용자 검토 후 문장과 구성을 조정하고, 다음 공식 버전 및 행내 환경이 준비되면 실제 실행 화면을 캡처해 교체 |

검토본을 승인본이라고 표시하지 않는다. 사용자가 명시적으로 승인한 범위와 아직
검토 중인 범위를 문서와 화면에서 구분한다.

## 3. 1차에서 확정한 설계 설명

- 공식 OpenMetadata 저장소의 새 버전은 패치 브랜치로 가져온다.
- 행내 커스터마이징 브랜치는 BANK-OM ID별 커밋을 유지한다.
- 새 공식 버전에 커스터마이징을 적용한 뒤 검사기를 실행하고, 필수 검사가 끝난
  경우에만 배포 검토로 넘어간다.
- BANK-OM ID는 사람이 정해진 양식으로 발급한다. LLM이 임의로 번호를 결정하지
  않는다.
- 커밋 메시지에는 본문과 별도로 `Customization-ID: BANK-OM-nnn` 항목을 넣는다.
  BANK-OM ID와 Git commit SHA는 서로 다른 값이다.
- `allowed_changed_paths`는 해당 BANK-OM ID의 커밋이 실제로 변경할 수 있는
  전체 파일 목록이다.
- `required_changed_paths`는 그중 최종 코드에서 실제 변경이 확인되지 않으면
  해당 커스터마이징이 빠졌다고 판단할 핵심 파일 목록이다.
- `upgrade_watch`는 행내에서 직접 수정하지 않았더라도 커스터마이징이 의존하기
  때문에 공식 업그레이드 때 변경 여부를 다시 확인할 파일·설정·라이브러리 목록이다.
- 폴더 전체를 넓게 허용하지 않고 현재 확인된 파일을 개별 경로로 등록하는 것이
  기본 원칙이다.

등록과 운영 방법의 정본은
[`docs/02-설계/bank_om_registration_policy.md`](../02-설계/bank_om_registration_policy.md)다.

## 4. 2차에서 확인한 검사기 원리와 한계

관련 검사기 구현 코드와 단위 테스트를 다시 확인했다. 관련 단위 테스트는
통과했지만, 다음 예외 가능성은 남아 있다.

Git 커밋과 파일 변경을 확인하는 T25-R·T25·T26·T30·T31·T40·T41·T42·T43·T93은
Java·TypeScript·Python·JSON·YAML·SQL 등 파일 종류와 관계없이 사용할 수 있다.
공식 원본 이후 각 커밋에서 바뀐 파일 경로와 공식 원본 대비 최종 파일 상태를
확인하므로 프론트엔드와 백엔드에 같은 변경관리 규칙을 적용할 수 있다. 그러나
이 공통 계층은 Java·TypeScript 등 파일 내부 코드의 의미나 실행 동작을
언어에 관계없이 해석하지는 않는다. T60-I는 현재 Python pytest 코드만 확인하고
T63은 TypeScript 전용이며, T61·T62는 Python pytest 실행 연결을 사용한다.
Java JUnit·TypeScript Jest를 직접 등록하고 실행하려면 언어·도구별 연결을
추가해야 한다.

정리하면 “모든 변경 파일이 검사 대상이 되는가?”에는 예라고 답할 수 있지만,
“모든 언어의 코드 동작을 현재 검사기가 직접 이해하고 테스트하는가?”에는
아니라고 답해야 한다. 저장소 경로 분류와 BANK-OM Manifest에 등록하지 않은
변경 경로는 공통 변경관리 검사에서 통과시키지 않는다.

| 검사 | 확인된 핵심 원리 | 운영 전에 필요한 보완 |
|---|---|---|
| T25-R | JSON은 값으로 비교하고, 나머지 파일은 Git 차이가 없어야 한다. Java 파일의 빈 줄 하나도 차이로 판단한다. | 서식 차이를 자동 통과시키지 말고 별도 표시 후 담당자 검토 |
| T25 | Git 포함 관계로 공식 commit이 행내 코드 이력에 있는지 확인한다. | 충돌 해결과 실제 동작은 별도 검사 |
| T26 | 모든 활성 BANK-OM ID의 필수 파일·계약·테스트 연결을 확인한다. | 파일 존재만으로 기능 정상이라고 판단하지 않음 |
| T60-I | `contracts.yaml`에 등록한 Python pytest 파일과 함수가 실제로 존재하는지 AST로 확인한다. 현재 9개 테스트는 API·검색·화면·한글 입력·연결 스키마를 다룬다. | Java JUnit·TypeScript Jest와 Manifest의 `direct_tests` 존재 확인을 추가하고, 테스트 품질과 실행 성공은 T61·T62에서 확인 |
| T30 | 공식 원본 이후의 모든 Git 커밋과 `Customization-ID:` 항목을 읽는다. | 하나의 ID에 다른 목적을 섞지 않도록 리뷰 |
| T31 | 여러 커밋 사용 허용, 연속성, 폐기 ID, 선행 관계 순환을 확인한다. | 누락된 업무 선행 관계는 사람이 등록 |
| T40 | 커밋별 전체 변경 파일과 최종 필수 변경 파일을 양방향으로 비교한다. | 파일 내부의 잘못된 줄은 코드 리뷰와 테스트로 확인 |
| T41 | AST가 아니라 민감 경로 규칙과 실제 변경 파일을 비교한다. | 정적 보안 분석과 보안 담당자 리뷰 추가 |
| T42 | 새 공식 버전의 Git 차이와 `upgrade_watch`를 비교한다. | 감시 대상 누락을 줄이는 자동 제안과 담당자 확인 |
| T43 | 커스터마이징 수·변경 줄·공유 파일 수·충돌률을 정책 한도와 비교한다. | 충돌률을 명령 인자가 아니라 실제 재적용 결과에서 자동 계산 |
| T93 | ID별 실제 변경 파일과 등록 파일을 비교하고, 새 공식 버전에서 감시 규칙이 유효한지 확인한다. | 민감 경로 규칙도 노후화 검사에 포함 |
| T61 | 커스터마이징이 없는 버전에서 필수 테스트가 실패하는지 확인한다. | 누락 때문에 실패했는지 오류 종류와 메시지까지 확인 |
| T62 | 제품 commit SHA, 배포 파일 digest, 검사기와 테스트 버전을 결과에 연결한다. | DB·검색엔진·설정 등 실행 환경 digest와 실행 시스템 서명 추가 |
| T63 | 공식 원본과 행내 코드의 TypeScript 파일 경로·오류 코드 발생 횟수를 비교한다. | Node·Yarn·전체 로그 digest를 검사 결과에 강제 연결 |
| T90 | 정해진 업그레이드 12단계 결과 문서와 코드·배포 파일·T62 결과의 연결을 확인한다. | 각 단계를 실제로 실행한 로그와 서명 검증 |
| T91 | 승인한 commit·이미지·Helm·검사 결과 digest와 실제 배포값을 비교한다. | 외부망에서 내부망으로 옮긴 뒤 별도 서명·해시 재검증 |

## 5. 현재 확인된 실제 상태

- 현재 제품 코드 commit: `849ae756cd238f218b5e3a6c795a392305cb32ee`
- 공식 원본 commit: `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9`
- 활성 커스터마이징: `BANK-OM-001`부터 `BANK-OM-011`까지 11개
- 소스 검사: T25·T26·T60-I·T30·T31·T40·T41·T93 통과
- T60-I: 등록한 필수 Python 테스트 함수 9개 확인
- T42: 같은 버전을 양쪽에 넣은 연결 확인만 했으며 실제 다음 공식 버전
  업그레이드 증거는 없음
- T43: 실제 업그레이드 충돌률이 아니라 연결 확인용 입력을 사용했으므로 실제
  업그레이드 승인 근거가 아님
- T61: 소스에서 실행 가능한 2개만 확인했으며 전체 5개 중 나머지 3개는 행내
  배포 환경이 필요
- T62: 실행기와 사전 환경 점검은 구현했지만 실제 행내 실행 결과 없음
- T63: 새로운 파일 경로·오류 코드 조합은 없지만 공식 원본부터 있던 오류가
  남아 있어 담당자 승인 필요
- T90·T91: 실제 행내 업그레이드와 배포 승격을 실행하지 않음
- 결론: 소스 커스터마이징 관리 검사는 진행됐지만 운영 배포 승인 상태는 아님
- 3차 초안 작성 시 소스 검사 명령을 다시 실행해 T25·T26·T60-I·T30·T31·
  T40·T41·T93 통과를 확인했다. 이 실행은 다음 공식 버전 업그레이드나 행내
  운영 환경 검사가 아니다.

## 6. 검증 명령

소스 검사:

```bash
./.venv/bin/python harness/registrations/kb-openmetadata/run_source_candidate_gates.py \
  --repo ../review-kb-openmetadata \
  --harness harness \
  --registration harness/registrations/kb-openmetadata \
  --layout harness/policies/repository-layout.yaml \
  --sensitive-zones harness/policies/sensitive-zones.yaml
```

이번 2차 검토에서 다시 실행한 관련 단위 테스트:

```bash
./.venv/bin/pytest -q \
  harness/tests/test_ancestry.py \
  harness/tests/test_contracts.py \
  harness/tests/test_debt.py \
  harness/tests/test_drift.py \
  harness/tests/test_invariants.py \
  harness/tests/test_patchkill.py \
  harness/tests/test_policy_drift.py \
  harness/tests/test_release.py \
  harness/tests/test_survival.py \
  harness/tests/test_testruns.py \
  harness/tests/test_tsc_baseline.py \
  harness/tests/test_upgrade_run.py \
  harness/tests/test_upgrade_watch.py \
  harness/tests/test_vendor_rebuild.py \
  harness/tests/test_zones.py
```

관련 단위 테스트는 통과했으며, 환경이 필요한 테스트는 skip으로 남았다.

HTML 다시 생성:

```bash
python3 /Users/seop/.codex/plugins/cache/openai-bundled/visualize/1.0.15/skills/visualize/scripts/render.py \
  docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-fragment.html \
  docs/00-사용가이드/공유문서/openmetadata-phase1-sharing-preview.html

python3 /Users/seop/.codex/plugins/cache/openai-bundled/visualize/1.0.15/skills/visualize/scripts/render.py \
  docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-fragment.html \
  docs/00-사용가이드/공유문서/openmetadata-phase2-verifier-table-preview.html
```

다른 노트북에서 위 절대 경로가 다르면 설치된 `visualize` 스킬의
`scripts/render.py` 경로를 찾아 바꾼다.

## 7. 다른 노트북에서 재개하는 순서

1. `easyseop/openmetadata-test`의 `codex/strict-manifest-gates` 브랜치를 받는다.
2. 이 문서와 `SHARING_ARTIFACT_REQUIREMENTS.md`를 읽는다.
3. `.agents/skills/clarity-preflight-review/SKILL.md`를 읽고 이후 모든 공유문서
   검토에 적용한다.
4. 2차 HTML을 열어 사용자 피드백이 남았는지 확인한다.
5. 2차가 승인되면 3차 시연 HTML을 만든다.
6. 실제 소스·변경관리표·Git 커밋·검사 명령 결과를 캡처한다.
7. 1차·2차·3차를 하나의 최종 공유문서로 합치고 중복과 용어를 다시 검토한다.
8. 작업 완료 후 이 문서의 상태·검증·다음 단계를 갱신하고 같은 브랜치에
   커밋·푸시한다.

## 8. 작업 시 주의

- `docs/00-사용가이드/.비개발자_시연_가이드.md.swp`는 사용자의 편집기 임시
  파일이다. 수정하거나 stage하지 않는다.
- 비밀값, 인증 토큰, 행내 URL과 실제 데이터는 문서나 Git에 넣지 않는다.
- 공유문서 묶음은 로컬 commit으로 계속 저장한다. 최초 묶음은 `becb18e`이며
  최신 보강 commit은 현재 브랜치의 `git log`로 확인한다. 원격
  `https://github.com/easyseop/openmetadata-test.git`에 행내 커스터마이징 구조를
  올려도 된다는 사용자의 명시적 확인을 받은 뒤 push한다.
- GitHub CLI 인증이 없더라도 기존 Git credential로 push가 가능한 경우가 있다.
  인증 오류가 나면 사용자가 해당 노트북에서 GitHub 로그인을 완료해야 한다.
- PR은 사용자가 요청하지 않으면 만들지 않는다.
