# Claude 검토 03 — Phase 결속과 기존 증거 호환성

## 1. 범위와 금지사항

gate orchestration·증거 위변조·버전 호환성을 읽기 전용으로 적대적 검토한다.
코드, Candidate lock, active pointer, 결과 파일을 수정하지 않는다.
관련 pytest 실행과 임시 디렉터리의 독립 반례 재현은 허용한다. 실행한 명령,
exit code, 통과·skip 수를 결과에 기록한다.

```text
repository: easyseop/openmetadata-test
branch: codex/structural-upgrade-safety-20260809
diff: 7319481e24063af7d16e9ae1c7bce34d396bbd27..d5153f284d8808e7856896b106f0539e8fcf2c83
```

```text
harness/run_phase_bundle.py
harness/om_workflow.py
harness/manage_shared_code_migration.py
harness/acgh/phase.py
harness/acgh/candidate.py
harness/acgh/candidate_select.py
harness/acgh/verdict.py
harness/tests/test_phase_cli.py
harness/tests/test_phase_parity.py
harness/tests/test_phase_evidence.py
harness/tests/test_result_io.py
```

## 2. 검토 흐름

```text
활성 Candidate 선택
→ conflict evidence schema v2 수집·self-check
→ preflight/postmerge 재계산·결속
→ required structural-review gate
→ canonical result·manager summary·practitioner detail·phase-status
```

## 3. 적대적 질문

1. 수집기와 binder가 같은 잘못된 helper를 공유해 상관된 오류를 놓치는가?
2. schema v1 과거 증거가 허위 PASS하는가, 명확히 incomplete/analysis error인가?
3. 증거 없음·필드 누락·알 수 없는 schema에서 verdict와 exit code가 일관적인가?
4. `structural-review`가 required 목록, canonical payload, 요약·상세·status에 모두
   포함되는가?
5. relocation PASS/APPROVAL/BLOCK/잘못된 값이 전체 verdict로 정확히 전파되는가?
6. full detail 경로와 digest가 결과에서 감사 가능하게 남는가?
7. `collector_harness_digest`를 현재 harness와 실제 비교하는가? 오래된 수집기 증거가
   통과하는가?
8. 판단에 관여하는 wrapper·orchestrator·validator·runner가 harness digest에 모두
   포함되는가?
9. public wrapper가 내부 CLI 필수 인자와 exit code를 보존하는가?
10. JSON stdout과 사람용 stdout이 섞여 parser를 오염시키는가?
11. output·registration·run-id에서 traversal 또는 symlink 공격이 가능한가?
12. 수집과 postmerge 사이 active pointer가 바뀌면 어디서 차단되는가?
13. Candidate activation branch 미통합 상태를 문서가 지원 완료로 오해시키는가?
14. source-only와 build-artifact/Runtime·운영 배포 경계가 흐려지는가?
15. timeout, 대형 증거, 동시 실행, stale output에서 부분 결과·overwrite가 가능한가?

## 4. 호환성·반례 test 매트릭스

다음 행마다 실제 상태, exit code, 증거 파일 생성 여부, 다음 행동을 표로 작성한다.

- schema v2 정상·필드 누락·path 누락/추가·digest 변조·알 수 없는 verdict
- schema v1 과거 증거·증거 없음·알 수 없는 schema
- active Candidate 변경·Candidate tree 변경·baseline lock 변경
- collector harness 변경·orchestrator만 변경·validator만 변경
- relocation PASS·APPROVAL·BLOCK·ANALYSIS_ERROR성 payload
- source-tree lock에 artifact digest 입력·build-artifact lock에 digest 누락
- stdout JSON mode·human mode·내부 stderr
- 기존 output 파일·동시 수집·중간 종료·run-id 경로 이탈
- preflight BLOCK 후 postmerge 미실행·required gate timeout
- canonical result와 manager/practitioner summary 변조

test 이름이 아니라 fixture·assertion을 확인한다. 빠진 행에는 먼저 실패해야 하는
회귀 test와 예상 Phase verdict·exit code를 적는다.

## 5. 결과 형식

```text
1. 사실 정정
2. P0
3. P1
4. P2
5. 입력별 호환성·exit code 표
6. 누락된 digest 결속
7. 반례 완전성 표
8. 실제 실행한 test 명령·exit code·통과·skip 수
9. 빠진 회귀 test와 예상 verdict
10. 불필요하거나 중복된 gate·출력·양식
11. 최종 판정: 착수 불가 / 수정 후 재검토 / 3차 통과
```

P0/P1 반례나 test 공백이 남으면 3차 통과를 선택하지 않는다. 수정은 하지 않는다.
