# Claude 검토 요청 — 검사 전 준비 자동화 구현

## 검토 목적

2026-07-29 설계 검토를 반영해 구현한
`plan → 사람 승인 → apply` 준비 자동화가 fail-closed인지 검토해 주세요.
실제 제품 업그레이드, build, runtime test, 운영 배포 승인을 검토하는 문서가
아닙니다.

## 현재 구현 경계

- Git 사실: 자동 계산
- owner, 중요도, required path, Contract, bank-only watch 판단: 사람 결정
- 승인 없는 실제 등록자료 적용: 금지
- 실제 OM_TEMP 1.13.0 plan: `REVIEW_REQUIRED`
- 자동 변경 0, 사람 판단 5, 차단 0, 분석 오류 0
- 승인·apply: 미실행

## 우선 검토할 질문

1. patch/custom ref 고정과 `patch..custom` commit 분석에 빠진 Git edge case가
   있는가?
2. ID 누락·중복, merge·빈 commit, 혼합 ownership, 비연속 series, retired ID,
   무관 이력 판정이 fail-closed인가?
3. source/shared owner 부분집합과 Manifest changed/required/watch 비교가 사람
   정책값을 덮어쓰지 않는가?
4. symlink·submodule·Git LFS pointer와 출력/대상 symlink 차단이 충분한가?
5. proposal digest, patch/custom ref, registration-state digest, exact decision
   set, apply lock이 승인 후 입력 변경과 동시 실행을 충분히 차단하는가?
6. 원자적 파일 교체 중 실패 rollback에 복구되지 않는 경우가 있는가?
7. 공식 patch에 없는 기존 watch 43개를 BANK-OM별 5개 질문으로 묶고 상세
   paths를 보존한 방식이 승인 추적에 적절한가?
8. Candidate lock schema v2의 `source-tree`와 `build-artifact` 구분, schema v1
   digest 호환 방식이 안전한가?
9. 실제 1.13.0 제안이 자동 변경 0인데 `REVIEW_REQUIRED`,
   `apply_ready: true`인 의미가 오해되지 않는가?
10. 테스트에서 빠진 보안·동시성·복구 시나리오가 있는가?

## 검토 시 주의

- 원격에 1.13.1 patch/custom branch가 없으므로 SHA를 추측하지 마세요.
- `UNASSIGNED` owner와 승인자를 임의로 채우지 마세요.
- source gate PASS를 build/runtime/deploy PASS로 해석하지 마세요.
- 발견 사항은 Serious / Minor / Validated로 나누고, 파일·함수·재현 절차를
  함께 적어 주세요.

## 주요 파일

- `DESIGN.md`
- `REVIEW_RESPONSE.md`
- `EASY_GUIDE.md`
- `code/prepare_registration.py`
- `code/acgh/registration_prep.py`
- `code/acgh/gitprim.py`
- `code/acgh/candidate.py`
- `code/acgh/schema/*.json`
- `tests/test_registration_prep.py`
- `tests/test_candidate.py`
- `actual-plan/summary.md`
- `actual-plan/review-required.yaml`
- `actual-plan/proposal.yaml`
