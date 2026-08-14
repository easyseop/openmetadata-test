# Claude 적대적 구현 재검토 요청 — `/om-plan` 보강 E안

## 검토 대상

- 저장소: `easyseop/openmetadata-test`
- branch: `codex/om-plan-e-hardening-20260814`
- 구현 기준 commit: `1f02e1d3a0c77b9d62f5763835d91cbadc1d5804`
- 구현 tree: `d5dd83ded1fd5689a8c630d99452e5f0bf836afc`
- 이전 기준: `a564d483e2c9727ffdaff6bea67662a24232bbb2`
- 이전 최종 설계 검토:
  `/Users/seop/Desktop/om-plan_E안_최종판단_재검토_결과_20260814.md`
- 현재 구현 인수인계:
  `docs/04-진행/CODEX_CURRENT_HANDOFF.md`

## 지시문

아래 지시문을 그대로 사용한다.

```text
easyseop/openmetadata-test의
codex/om-plan-e-hardening-20260814 branch를 읽기 전용으로 적대 검토해줘.

정확한 구현 기준은 commit
1f02e1d3a0c77b9d62f5763835d91cbadc1d5804,
tree d5dd83ded1fd5689a8c630d99452e5f0bf836afc 이다.

먼저 다음 두 파일을 처음부터 끝까지 읽어라.
1. docs/04-진행/CODEX_CURRENT_HANDOFF.md
2. docs/04-진행/OM_PLAN_E_HARDENING_CLAUDE_REVIEW_REQUEST_20260814.md

이전 설계 검토 결과
~/Desktop/om-plan_E안_최종판단_재검토_결과_20260814.md가 있으면 함께 읽어라.
없으면 현재 인수인계 1·3·5·6절을 검토 기준으로 사용하라.

목표는 구현자의 설명에 동의하는 것이 아니라 다음 주장을 반증하는 것이다.

1. final plan-validate는 사람 또는 보호된 CI가 보관한
   --expected-input-lock-digest가 없으면 절대 review_ready에 도달하지 않는다.
2. run-request.yaml, input-lock.yaml, discovered-facts.json을 다른 commit 기준으로
   함께 재작성해도 이전 expected digest 때문에 analysis_error가 된다.
3. upgrade 공식 문서 snapshot, official-doc-sources.yaml, discovered facts를 함께
   일관 재작성해도 official_doc_sources_digest 결속 때문에 analysis_error가 된다.
4. branch 이동만으로 preflight 당시 pinned SHA가 무효화되지 않는다(C03 유지).
5. 공용 verdict enum APPROVAL과 비-plan 소비자는 변경되지 않았다.
6. review_state=review_ready는 trusted digest 대조 성공 후에만 기록된다.
7. note-only·빈 proposal은 block이다.
8. no_change는 rationale, affected_customization_ids, 재계산 facts evidence와 expected
   값이 모두 있어야 review_ready 후보가 된다.
9. preflight 출력이 run-request 의도 확인 경계를 충분히 드러내며,
   E안이 preflight 전의 잘못된 사람 판단까지 보증한다고 오해하게 하지 않는다.
10. LLM이 preflight·validate·expected를 모두 통제하는 시나리오를 코드가 안전하다고
    가장하지 않는다.

반례 검증은 임시 저장소에서 수행해도 되지만 원본 branch, code, schema, test,
문서, Git index를 수정하지 마라. commit, push, merge, reset, checkout, Skill 설치,
release도 하지 마라.

특히 다음 공격을 직접 실행하라.
- expected 누락·형식 오류·불일치
- request+lock+facts 3파일 일관 재작성
- upgrade 문서 bytes+source records+facts+lock까지 가능한 범위에서 동시 재작성
- LLM이 새 expected까지 선택한 경우와 사람이 이전 expected를 유지한 경우 비교
- approval verdict와 review_state 조합 변조
- {"note":"ok"}, 빈 decisions/findings, 근거 없는 no_change,
  관계없는 evidence를 붙인 no_change
- C03 branch 이동
- checker commit 또는 schema만 바뀐 경우

각 발견은 P0/P1/P2로 분류하고 반드시 파일·함수·실행 반례를 적어라.
P0/P1이 없더라도 수행한 공격과 실제 결과를 표로 남겨라.

다음은 이번 재검토에서 구현 결함으로 다시 묶지 마라. 단, 현재 코드가 완료했다고
거짓 표시하면 지적하라.
- C44 전용 회귀 test
- boundary lint 문자열 결합 회피
- hook 절대경로 강화
- Q3·Q6·Q7·Q8·Q9
- 완전 무인 C+ 구현

결과는 다음 한 파일에만 작성하고 중단하라.
~/Desktop/om-plan_E안_구현재검토_결과_20260814.md

최종 형식:
1. 검증 기준 branch·commit·tree·worktree 상태
2. 실행한 공격 시나리오와 실제 결과
3. P0/P1/P2
4. 구현 주장 1~10의 참/거짓 판정
5. 누락된 반례 test
6. 최종 판정: 채택 / 수정 후 재검토 / 거부
```

## 검토 종료 조건

Claude는 결과 파일을 작성한 뒤 구현·수정·commit·push를 시작하지 않습니다.
P0/P1 수정 여부와 다음 구현 범위는 결과를 Codex와 사용자가 대조한 뒤 결정합니다.
