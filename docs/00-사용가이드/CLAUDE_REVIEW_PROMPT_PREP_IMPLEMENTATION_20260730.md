# Claude 검토 요청 — 검사 전 준비 자동화 구현

## 검토 목적

2026-07-29 설계 검토를 반영해 구현한
`plan → 사람 승인 → apply` 준비 자동화가 fail-closed인지 검토해 주세요.
실제 제품 업그레이드, build, runtime test, 운영 배포 승인을 검토하는 문서가
아닙니다.

## 검토 대상 기준

- 저장소: `easyseop/openmetadata-test`
- branch: `codex/strict-manifest-gates`
- 구현 commit: `b63ce67bd303865224339a0dfe6e4becb252bea6`
- CI 증적 commit: `7ee1fdb2dfdd4dd513f9df615aca9d332c094b9c`
- 최신 문서 head: `d7aa807`
- 실제 제품 입력: `easyseop/OM_TEMP`의 `patch/om-1.13.0`과
  `custom/om-1.13.0`

## 현재 구현 경계

- Git 사실: 자동 계산
- owner, 중요도, required path, Contract, bank-only watch 판단: 사람 결정
- 승인 없는 실제 등록자료 적용: 금지
- 실제 OM_TEMP 1.13.0 plan: `REVIEW_REQUIRED`
- 자동 변경 0, 사람 판단 5, 차단 0, 분석 오류 0
- 승인·apply: 미실행

## 먼저 읽을 문서

1. `IMPLEMENTATION_CODE_GUIDE.md`: 자동화 흐름, 코드 역할과 완료·미완료 범위
2. `EASY_GUIDE.md`: 운영자가 실제로 실행하는 명령과 결과별 대응
3. `DESIGN.md`: 설계 결정과 보안 경계
4. `REVIEW_RESPONSE.md`: 이전 설계 검토 지적과 반영 결과

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
11. `EASY_GUIDE.md`만 읽은 신규 직원이 준비 조건, `plan`, 질문 검토,
    승인서 작성, `apply`, 재검사, 실패 복구와 증거 보관까지 수행할 수 있는가?
12. 코드·가이드·실제 제안에서 `READY`, `REVIEW_REQUIRED`, `BLOCKED`,
    `ANALYSIS_ERROR`, `APPLIED`의 의미가 동일한가?

## 재현할 테스트

실제 저장소 checkout과 `.venv`를 함께 받았다면 아래 명령을 실행해 주세요.
ZIP만 받아 실행 환경이 없다면 테스트를 실행했다고 표현하지 말고, 정적 코드
검토 결과와 추가 실행이 필요한 항목을 분리해 주세요.

```bash
cd harness
../.venv/bin/python -m pytest \
  tests/test_registration_prep.py \
  tests/test_gitprim.py \
  tests/test_candidate.py \
  tests/test_registration_validation_workflow.py \
  tests/test_source_candidate_workflow.py
```

실제 1.13.0 제안의 정본은 `actual-plan/`이다. 최소한 다음도 확인해 주세요.

- `summary.md`의 상태·건수와 `proposal.yaml` 배열 길이가 같은가?
- `review-required.yaml`의 다섯 질문이 proposal digest에 결속되는가?
- `diff.patch`가 비어 있을 때도 자동 변경 0과 사람 판단 5를 구분하는가?
- 자리표시자 승인 template을 실제 승인으로 잘못 받아들이지 않는가?

## 검토 시 주의

- 원격에 1.13.1 patch/custom branch가 없으므로 SHA를 추측하지 마세요.
- `UNASSIGNED` owner와 승인자를 임의로 채우지 마세요.
- source gate PASS를 build/runtime/deploy PASS로 해석하지 마세요.
- 발견 사항은 Serious / Minor / Validated로 나누고, 파일·함수·재현 절차를
  함께 적어 주세요.

## 답변 형식

먼저 아래 표를 작성해 주세요.

| 우선순위 | 파일·함수 | 발견한 문제 | 실제 위험 | 재현 방법 | 권장 수정 |
|---|---|---|---|---|---|

그다음 아래 항목을 분리해 주세요.

1. **Serious**: 승인 우회, 잘못된 파일 적용, stale 입력 수용, rollback 실패,
   분석 오류를 정상으로 처리하는 문제
2. **Minor**: 가독성, 중복, 오류 메시지, 유지보수성 문제
3. **Validated**: 검토 결과 안전하다고 확인한 동작
4. **Guide gaps**: 신규 직원이 질문해야만 진행할 수 있는 누락 단계
5. **Decision**: 현재 구현을 그대로 승인 가능한지, 수정 후 재검토가 필요한지

## 주요 파일

- `IMPLEMENTATION_CODE_GUIDE.md`
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
