# Phase 번들링 반례 테스트 케이스

> 작성일: 2026-08-07  
> 관련 설계: `PHASE_BUNDLING_개발설계_수정보완_20260807.md`  
> 목적: 정상 동작뿐 아니라 잘못된 PASS, 잘못된 candidate 선택, 오래된 승인 재사용을 막는다.

## 1. 테스트 원칙

- C1~C20은 기존 계획의 기본 테스트를 유지한다.
- C21 이후는 운영 중 발생 가능한 반례다.
- P0는 구현 완료 전에 반드시 통과한다.
- P1은 phase 번들링 통합 테스트에서 통과한다.
- P2는 범용화·보안·성능 테스트다.
- 기존 gate의 결과를 번들러에 맞게 변경하지 않는다. 직접 실행 결과와 번들 실행
  결과의 verdict·사유·검사 건수가 같아야 한다.

## 2. 기존 기본 테스트 C1~C20

| ID | 대상 | 입력·상황 | 기대 결과 |
|---|---|---|---|
| C1 | candidate 선택 | 승인 lock 2개 | 명시된 활성 lock 선택 |
| C2 | candidate 선택 | approval digest와 lock 불일치 | 해당 lock 선택 금지 |
| C3 | candidate 선택 | 승인 lock 없음 | `analysis_error` |
| C4 | consistency | 적용 대상 활성 출처가 모두 같은 SHA | `consistent=true` |
| C5 | consistency | Runtime lock만 다른 SHA | STOP, 파일·값 표시 |
| C6 | provenance | 과거 snapshot SHA만 다름 | provenance 표시, 통과 |
| C7 | preflight | change-intent 없음 | T41 미실행 예고, 다른 gate는 계속 가능 |
| C8 | preflight | base 객체 없음 | blocking STOP, exit 3 |
| C9 | gate 실행 | conflict-rate 없음 | T43만 미실행 |
| C10 | aggregate | 필수 gate 1개 미실행 | incomplete·analysis_error·exit 3 |
| C11 | aggregate | 모든 필수 gate pass | pass·exit 0 |
| C12 | aggregate | approval 1개와 pass | approval·exit 2 |
| C13 | candidate pinning | 실행 중 branch 이동 | 처음 고정한 SHA 유지 |
| C14 | rollup | 임의 phase 결과 | 3단 출력 verdict·수량 동일 |
| C15 | parity | conflict-rate 없는 직접 실행과 번들 실행 | T43 외 결과 동일 |
| C16 | parity | conflict-rate 포함 | T43 포함 결과 동일 |
| C17 | approval | lock 내용 변경 | 기존 approval 무효 |
| C18 | prep-official | target tag 존재 | official branch 생성, tree 일치 |
| C19 | prep-official | target tag 없음 | STOP, branch 미생성 |
| C20 | 종료코드 | verdict 네 종류 | 기존 EXIT_CODE와 일치 |

## 3. P0 — candidate 선택과 승인

| ID | 입력·반례 | 기대 결과 |
|---|---|---|
| C21 | 승인된 lock은 여러 개지만 active-candidate 없음 | 임의 최신 선택 금지, `analysis_error` |
| C22 | active-candidate가 미승인 lock을 지정 | phase 시작 금지 |
| C23 | active-candidate digest와 실제 lock digest 불일치 | phase 시작 금지, 두 값 표시 |
| C24 | approval의 승인자·근거가 자리표시자 | 미승인 처리, 수정 필드 표시 |
| C25 | approval 시각 형식 오류 | 미승인 처리, RFC 3339 예시 표시 |
| C26 | 실행 A 종료 후 새 lock B를 승인·활성화 | 다음 실행은 B 사용 |
| C27 | 실행 중 active-candidate가 A에서 B로 변경 | 현재 실행은 A 유지 |
| C28 | commit은 다르지만 tree가 같은 두 lock | 서로 다른 provenance로 보존, 자동 교체 금지 |
| C29 | lock의 commit은 존재하지만 tree SHA 불일치 | binding 실패 |
| C30 | build artifact digest 불일치 | runtime 단계 시작 금지 |
| C31 | 기존 CandidateLock schema v1 입력 | 기존 loader로 정상 해석 |
| C32 | 기존 CandidateLock schema v2 입력 | 기존 loader로 정상 해석 |
| C33 | lock YAML 손상·필수 필드 누락 | `analysis_error`, 파일·필드 표시 |
| C34 | 과거 proposal·evidence·snapshot SHA가 다름 | provenance로만 표시, 활성 정합성 실패 아님 |

## 4. P0 — premerge·postmerge 단계 분리

| ID | 입력·반례 | 기대 결과 |
|---|---|---|
| C35 | premerge에 승인된 1.13.1 기준선 사용 | T42·T93 policy·T51/T52 실행 |
| C36 | premerge에서 T41 실행 요청 | 비적용 gate로 제외, 실행하지 않음 |
| C37 | premerge에서 T43 실행 요청 | 비적용 gate로 제외, conflict-rate 요구하지 않음 |
| C38 | premerge에서 T93 exact-scope 실행 요청 | 비적용 gate로 제외 |
| C39 | watch-suggest가 많은 후보를 생성 | 참고정보만 기록, verdict에 미포함 |
| C40 | postmerge candidate가 공식 target의 후손이 아님 | ancestry 오류로 STOP |
| C41 | 1.13.1 기준선을 1.13.2 postmerge candidate로 전달 | 잘못된 단계 입력으로 거부 |
| C42 | 올바른 1.13.2 병합 candidate | T41·T43·T93 exact-scope 실행 가능 |
| C43 | premerge result digest로 postmerge 승인 | phase 불일치로 승인 거부 |
| C44 | postmerge 검사 후 candidate에 commit 추가 | 기존 결과·승인 무효, 재검사 요구 |
| C45 | target branch 이름은 맞지만 commit이 공식 tag와 다름 | STOP, 두 SHA 표시 |

## 5. P0 — 입력 누락과 실행 오류

| ID | 입력·반례 | 기대 결과 |
|---|---|---|
| C46 | change-intent만 없음 | T41만 `skipped_missing_input` |
| C47 | conflict-rate만 없음 | T43만 `skipped_missing_input` |
| C48 | 필수 입력 여러 개 동시 누락 | 모든 누락을 한 번에 보고 |
| C49 | change-intent YAML 문법 오류 | missing이 아닌 `analysis_error` |
| C50 | conflict-rate가 -0.1 또는 1.1 | 입력 오류 |
| C51 | conflict-rate가 NaN 또는 Infinity | 입력 오류 |
| C52 | gate 내부 Python 예외 | `execution_status=failed`, verdict analysis_error |
| C53 | gate timeout | failed·analysis_error, timeout 시간과 로그 표시 |
| C54 | gate가 잘못된 JSON 출력 | failed·analysis_error, 원본 로그 보존 |
| C55 | JSON verdict pass, 실제 종료코드 1 | 결과 불일치 analysis_error |
| C56 | T43 실패 중 T42는 실행 가능 | T42 계속 실행, 전체는 analysis_error |
| C57 | 실행 가능한 gate가 0개 | 빈 결과 pass 금지, analysis_error |

## 6. P0 — verdict·phase 상태·종료코드

| ID | 입력·반례 | 기대 결과 |
|---|---|---|
| C58 | pass+approval | approval, exit 2 |
| C59 | approval+block | block, exit 1 |
| C60 | block+analysis_error | analysis_error, exit 3 |
| C61 | gate 순서만 변경 | overall verdict 동일 |
| C62 | 필수 gate 하나 미실행, 나머지 pass | incomplete·analysis_error·exit 3 |
| C63 | 적용 대상이 아닌 gate 미실행 | incomplete로 만들지 않음 |
| C64 | 임의 verdict 조합 property test | 항상 SEVERITY_RANK로 집계 |
| C65 | exit-code 숫자 최대값으로 집계하는 변이 구현 | 테스트가 실패해야 함 |

## 7. P0 — 직접 실행 대비 parity

| ID | 입력·반례 | 기대 결과 |
|---|---|---|
| C66 | 기존 러너 결과 pass | 번들의 gate·사유·건수 동일 |
| C67 | 기존 러너 결과 approval | 동일 |
| C68 | 기존 러너 결과 block | 동일 |
| C69 | 기존 러너 결과 analysis_error | 오류를 숨기지 않고 동일 |
| C70 | conflict-rate 없음 | T43 외 실행 가능 gate 동일 |
| C71 | 구조화 diff에 JSON·YAML·텍스트 혼합 | 파일별 결과 동일 |
| C72 | 출력 순서만 다름 | 의미가 같으면 parity 통과 |
| C73 | 사유·경로·검사 건수 하나가 다름 | parity 실패 |
| C74 | 기존 러너를 호출하지 않고 재구현한 변이 | 골든 parity 테스트 실패 |

## 8. P1 — partial clone·네트워크·공식 코드 준비

| ID | 입력·반례 | 기대 결과 |
|---|---|---|
| C75 | 필요한 객체가 로컬에 있고 네트워크 단절 | 정상 실행 |
| C76 | blobless clone에 필요한 blob 없음 | fetch 필요 객체·다음 행동 표시 후 STOP |
| C77 | fetch 도중 연결 중단 | 불완전 결과를 정상 evidence로 확정하지 않음 |
| C78 | base commit은 있지만 target tree 없음 | 누락 객체 SHA 표시 |
| C79 | lightweight tag | 실제 commit으로 정상 고정 |
| C80 | annotated tag | tag object가 아닌 commit으로 고정 |
| C81 | tag와 기존 official branch의 commit 불일치 | 기존 branch 덮어쓰기 금지 |
| C82 | existing official branch가 정확함 | 변경 없이 성공하는 idempotent 동작 |
| C83 | partial clone promisor 설정은 있으나 blob 접근 가능 | 불필요한 실패 없이 통과 |

## 9. P1 — evidence·digest·승인 재사용 방지

| ID | 입력·반례 | 기대 결과 |
|---|---|---|
| C84 | 같은 판단 입력으로 재실행 | canonical result digest 동일 |
| C85 | timestamp·duration만 변경 | 판단 digest 동일 |
| C86 | candidate·정책·등록자료 하나 변경 | digest 변경 |
| C87 | 저장된 JSON 수동 수정 | digest 검증 실패 |
| C88 | 승인 후 입력 파일 하나 변경 | 기존 승인 무효 |
| C89 | candidate A 승인서를 B 결과에 사용 | 승인 거부 |
| C90 | 사람이 block을 pass로 승인하려 함 | machine verdict 유지, 반영 금지 |
| C91 | 같은 run-id 재사용 | 기존 evidence 덮어쓰기 금지 |
| C92 | 두 phase 동시 실행 | 서로 다른 폴더에 완전한 결과 저장 |
| C93 | 결과 저장 중 프로세스 종료 | 반쪽 JSON을 최종 결과로 남기지 않음 |

## 10. P1 — 3단 출력과 관리자 요약

| ID | 입력·반례 | 기대 결과 |
|---|---|---|
| C94 | 관리자 pass, 시스템 JSON approval | 출력 불변식 실패 |
| C95 | 검증 대상 100개 중 99개 정상 | `99/100`, 미확인 1개와 다음 행동 표시 |
| C96 | 실행 gate는 pass지만 필수 gate 미실행 | 관리자 화면에 정상 표시 금지 |
| C97 | 대상 0개 | `0/0 정상` 대신 검사 대상 없음 표시 |
| C98 | 동일 경로가 여러 ID에 포함 | 고유 경로 수와 경로·ID 조합 수를 구분 |
| C99 | 사유·경로 수백 건 | 관리자 요약은 건수, 실무자 상세는 전체 제공 |
| C100 | 3단 출력의 수량 계산 순서 변경 | 동일 시스템 JSON에서 같은 수치 유지 |

## 11. P1 — conflict-rate 경계값

| ID | 입력·반례 | 기대 결과 |
|---|---|---|
| C101 | 승인된 기준 없음 | 0으로 추정하지 않고 T43 미실행 |
| C102 | 임계값 바로 아래 | 정책에 따른 낮은 단계 verdict |
| C103 | 임계값과 정확히 같음 | 경계 규칙대로 고정된 verdict |
| C104 | 임계값 바로 위 | 정책에 따른 높은 단계 verdict |
| C105 | 비교 대상 파일 수 0 | 0으로 나누지 않고 명시적 결과 |
| C106 | 수동 입력과 병합 증거 계산값 불일치 | 자동 통과 금지, 불일치 표시 |

## 12. P2 — 범용성·안전성·성능

| ID | 입력·반례 | 기대 결과 |
|---|---|---|
| C107 | 다른 OpenMetadata 버전 | 특정 버전·SHA 하드코딩 없이 동작 |
| C108 | 다른 등록 제품 | kb-openmetadata 전용 경로 의존 없음 |
| C109 | run-id에 `../` 포함 | evidence 경로 이탈 거부 |
| C110 | ref에 shell 특수문자 포함 | 명령 삽입 없이 안전하게 실패 |
| C111 | 환경변수에 token·password 포함 | 출력과 인수인계에 비밀정보 미노출 |
| C112 | evidence 경로가 외부 symlink | 허용 경로 밖 쓰기 거부 |
| C113 | 1,000개 경로·수백 ID | 누락 없이 완료, 세 출력 수량 일치 |
| C114 | 매우 긴 오류 사유 | JSON은 원문 보존, 관리자 요약은 잘림 없이 핵심 표시 |

## 13. 테스트 계층

| 계층 | 대상 | 대표 사례 |
|---|---|---|
| 단위 테스트 | 선택·digest·집계·상태 변환 | C21~C34, C58~C65 |
| property-based | 순서·조합·SHA 고정·digest | C27, C61, C64, C84~C86 |
| 통합 테스트 | preflight·gate 독립실행·evidence | C35~C57, C75~C93 |
| 골든 parity | 직접 러너와 번들 결과 비교 | C66~C74 |
| end-to-end | premerge→승인→postmerge→rollup | C42~C45, C94~C100 |
| 장애 주입 | timeout·잘못된 JSON·네트워크 중단 | C52~C55, C76~C78 |

## 14. 최소 완료 기준

개발 완료는 다음 조건을 모두 만족해야 한다.

- C1~C20과 P0(C21~C74) 전부 통과
- P1에서 미실행 항목이 있으면 사유와 후속 실행 계획 기록
- 직접 실행과 번들 실행의 네 verdict parity 통과
- candidate 기준을 교체할 수 있지만 한 실행의 SHA는 변하지 않음
- 프로그램 오류가 `skipped_missing_input`으로 숨지 않음
- premerge와 postmerge 결과·승인이 서로 재사용되지 않음
- 필수 gate 미실행 상태가 pass로 표시되지 않음
- 승인 후 판단 입력 변경 시 승인 자동 무효
- 관리자·실무자·시스템 출력의 verdict와 수량 일치

## 15. 구현 결과 보고 형식

```text
P0: 74/74 PASS
P1: <통과>/<전체> PASS, <미실행> SKIP(사유 포함)
P2: <통과>/<전체> PASS
Parity: pass/approval/block/analysis_error 4종 일치
변경 파일: <목록>
미해결 반례: <없음 또는 ID와 사유>
다음 사람 STOP: <승인이 필요한 항목>
```
