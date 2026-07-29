# OM_TEMP 1.13.0 → 1.13.1 업그레이드 실행 가이드

> 공식 기준: OpenMetadata `1.13.0-release` → `1.13.1-release`
>
> 로컬 branch: `patch/om-1.13.1`, `custom/om-1.13.1`
>
> 최종 검사 대상 commit: `dee330ebd5abfe33e1ac61e1ca31879746a1b423`

## 1. 이번 작업의 목적

공식 1.13.1 코드 위에 BANK-OM-001~007을 순서대로 다시 적용하고, 실제 충돌을
해결한 뒤 Manifest와 Git 이력이 일치하는지 검사했습니다. 이 결과는 소스 코드
수준의 업그레이드 검증이며 운영 배포 완료를 뜻하지 않습니다.

## 2. 적용 전에 확인한 영향

공식 1.13.0과 1.13.1 사이에서 834개 파일이 바뀌었습니다. 그중 Manifest의
`upgrade_watch.paths`와 겹치는 경로가 7개 BANK-OM 모두에서 발견되어
`APPROVAL` 결과가 나왔습니다.

`APPROVAL`은 실패가 아닙니다. 자동 적용 전에 담당자가 영향 경로를 확인해야
한다는 뜻입니다.

| BANK-OM | 공식 버전에서 바뀐 감시 경로 |
|---|---:|
| BANK-OM-001 | 22개 |
| BANK-OM-002 | 23개 |
| BANK-OM-003 | 19개 |
| BANK-OM-004 | 20개 |
| BANK-OM-005 | 1개 |
| BANK-OM-006 | 4개 |
| BANK-OM-007 | 1개 |

## 3. branch 생성과 커스터마이징 적용

```bash
git worktree add -b patch/om-1.13.1   ../om-temp-1.13.1-upgrade 1.13.1-release
git -C ../om-temp-1.13.1-upgrade switch -c custom/om-1.13.1
```

`patch/om-1.13.1`은 공식 1.13.1 코드만 보관합니다. `custom/om-1.13.1`은
그 위에 BANK-OM 커밋을 적용한 검사 대상 branch입니다. 두 branch는 현재 로컬에만
있고 GitHub에는 아직 push하지 않았습니다.

## 4. 실제 충돌과 해결

| BANK-OM | 1.13.1 적용 commit | 실제 충돌 | 처리 |
|---|---|---|---|
| BANK-OM-001 | `83b1e0ac7d` | 번역 JSON 18개 | 각 파일의 BANK-OM 키 9개 |
| BANK-OM-002 | `8b368af0a2` | 번역 JSON 18개 | 각 파일의 BANK-OM 키 11개 |
| BANK-OM-003 | `e1d181d728` | 번역 JSON 18개 | 각 파일의 BANK-OM 키 5개 |
| BANK-OM-004 | `ed870cd63d` | 번역 JSON 18개 | 각 파일의 BANK-OM 키 9개 |
| BANK-OM-005 | `dfd3ad5e1c` | 충돌 없음 | 자동 적용 |
| BANK-OM-006 | `15b85814f5` | 충돌 없음 | 자동 적용 |
| BANK-OM-007 | `e7e4ba67b6 + dee330ebd5` | 충돌 없음 | 두 커밋을 순서대로 적용 |

001~004에서 표시된 18개는 매번 같은 번역 JSON 경로입니다. 따라서 서로 다른
72개 파일이 충돌한 것이 아니라, **18개 고유 파일에서 네 번의 충돌 사건**이
발생한 것입니다.

각 충돌 파일에서 세 값을 비교했습니다.

1. 공통 기준 JSON
2. 공식 1.13.1 JSON
3. 적용 중인 BANK-OM JSON

여기서 leaf key는 `label.instance-code`처럼 JSON에서 실제 값을 담는 마지막
항목 이름입니다. 공식 변경 키와 BANK-OM 변경 키가 하나도 겹치지 않은 경우에만 공식 1.13.1
JSON을 유지하고 BANK-OM 키를 추가했습니다. 같은 키를 양쪽이 모두 바꿨다면
자동 해결하지 않고 명령이 중단되도록 했습니다.

```bash
./.venv/bin/python   harness/tools/resolve_nonoverlapping_json_conflicts.py   --repo ../om-temp-1.13.1-upgrade
```

## 5. 1.13.1 기준자료 다시 생성

1.13.0 자료를 그대로 검사하지 않고 `om-temp-1.13.1` 등록 폴더를 새로
만들었습니다. Manifest와 Contract의 업무 기준은 재사용하고, 공식 SHA·검사 대상
SHA·전체 diff·공용 경로·정책 파일은 1.13.1 기준으로 다시 생성했습니다.

| 자료 | 실제 결과 |
|---|---:|
| Manifest | 7개 |
| Registry | BANK-OM 7개 |
| Contract | 7개, 필수 Python test 9개 |
| 전체 변경 경로 | 111개 |
| 공용 경로 | 37개 |

## 6. 실제 검사 결과

| 검사명 | 무엇을 확인했나 | 결과 |
|---|---|---|
| 공식 기준 이력 포함 | 공식 1.13.1에서 시작했는지 | PASS |
| 커스터마이징 생존 | 핵심 파일과 Contract 연결이 남았는지 | PASS |
| 필수 테스트 코드 존재 | Python test 파일·함수가 있는지 | PASS |
| 커밋 작성 규칙 | 각 커밋에 BANK-OM ID가 하나인지 | PASS |
| ID 연결 규칙 | 미등록 ID와 잘못된 후속 커밋이 없는지 | PASS |
| 변경 범위 | Manifest에 등록된 파일만 바꿨는지 | PASS |
| 민감 경로 | 별도 정책을 위반하지 않았는지 | PASS |
| 커밋별 실제 경로 일치 | 실제 변경 파일과 Manifest가 같은지 | PASS |

## 7. 현재 완료와 다음 단계

- 완료: 공식 1.13.1 branch 생성, BANK-OM-001~007 적용, JSON 충돌 해결
- 완료: 1.13.1 등록자료 생성 및 사전자료 검증 5종 PASS
- 완료: 소스 검사 8종 PASS
- 미완료: OpenMetadata 전체 build
- 미완료: Contract test 실제 실행
- 미완료: 기능 담당자 지정과 배포 승인
- 미완료: GitHub push와 검증 tag 생성

다음 단계는 전체 build와 실행 가능한 Contract test를 수행한 뒤, 실제 Git
화면·터미널·검사 결과를 캡처해 시연 문서에 추가하는 것입니다.
