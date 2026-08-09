# OpenMetadata 1.13.2 소스 검증 WIP 체크포인트

> 기록일: 2026-08-09 KST
>
> 상태: **WIP · 소스 범위만 확인**
>
> 운영 완료 또는 최종 PASS가 아닙니다.

## 1. 결속 대상

| 항목 | 값 |
|---|---|
| 공식 1.13.2 | `2763bf97ce265662793a1a38d353147cc6d6c2e3` |
| 소스 검증을 실행한 제품 commit | `390c439e77af12b9813121f9e3217cb4095f947d` |
| WIP 전달 commit | `9587fe8fc7d9e6a18b9c0038b92c5fef24bb8412` |
| 두 제품 commit의 공통 tree | `22bdc8435b018cdbfe06e32fe02f7d5970a2b363` |
| 제품 branch | `codex/om-1.13.2-rehearsal-vendor-merge-20260809` |

`9587fe8...`은 새 소스 변경이 없는 WIP 표식 commit입니다. 실제 TypeScript 비교와
BANK 전용 test는 부모 `390c439...`에서 실행했으며 두 commit의 tree가 같습니다.

## 2. 기존 TypeScript 로그 비교

이번 체크포인트를 만들면서 TypeScript 검사를 다시 실행하지 않았습니다. 이미
생성된 공식·후보 로그를 보존하고, 정규화된 `파일 경로 + TS 오류 코드` key만
비교했습니다.

| 구분 | 공식 1.13.2 | BANK 후보 |
|---|---:|---:|
| 원본 로그 줄 | 1,339 | 1,329 |
| 정규화 오류 record | 254 | 249 |
| 고유 파일·오류코드 key | 168 | 167 |
| 공식에는 없고 후보에만 있는 key | - | **0** |

보존 파일과 SHA-256:

| 파일 | SHA-256 |
|---|---|
| `official-tsc.log` | `882a4f99fba12c5814c6f2b5e67a25aceabe92039dd4ed9558eeaaca4e634a0a` |
| `candidate-tsc.log` | `ed5ee1f157752e4f7c3a2d1125efb1b9d12ffd789f3d36fa359267d4ac7bdc99` |
| `official-tsc.normalized` | `f24fcc82987018772b3076c923768f577cee01e7bcacb2ca73080dfff8c8b6d9` |
| `candidate-tsc.normalized` | `e5135c1090cb0f2c63b70af60dc1489b21558da7a1d593612f980fa519cef528` |

후보에서 새로 확인됐던 BANK 관련 타입 문제는 다음처럼 수정된 상태입니다.

- InstanceCode·QueryReport route component에 `pageTitle` 전달
- `SearchedData` test mock에 `onPaginationChange` 전달

공식 원본에도 존재하는 TypeScript 오류는 이번 BANK 수정 대상으로 계산하지
않았습니다. `후보 전용 key 0개`는 소스 비교 결과이며 전체 제품의 최종 타입
PASS를 뜻하지 않습니다.

## 3. BANK 전용 test 증적

소스 검증 commit `390c439...`에서 다음 4개 suite를 실행했습니다.

```text
src/utils/DatabaseServiceUtils.test.tsx
src/utils/EntityUtils.test.tsx
src/utils/ServiceUtils.test.ts
src/components/SearchedData/SearchedData.test.tsx
```

결과:

```text
Test Suites: 4 passed, 4 total
Tests:       88 passed, 88 total
Snapshots:   0 total
Failures:    0
```

별도 확인으로 19개 언어 JSON이 파싱됐고 InstanceCode·QueryReport 필수 label·
message key가 모두 존재했습니다. 이 문서는 실행 요약 증적이며 원본 Jest stdout은
당시 별도 파일로 저장하지 않았습니다.

## 4. 이번 체크포인트에서 하지 않은 일

- 프로덕션 번들 재실행
- Docker 실행 및 실제 화면·클릭 검증
- 1.13.2 최종 Candidate lock 생성
- 담당자 승인과 활성 Candidate 전환
- conflict evidence·postmerge·phase-status 최종 실행
- 운영 배포 또는 release 승인

로컬 Vite 번들은 앞선 소스 검증 중 한 차례 성공했지만, 이를 최종 clean-machine
번들 증거로 승격하지 않습니다. 고사양 기기 또는 GitHub Actions에서 다시 확인해야
합니다.

## 5. 중단된 원격 실행

GitHub Actions run `31305716406`은 체크포인트 방식으로 전환하면서 사용자가 범위를
Docker 제외로 확정해 취소했습니다. Contract runner image job은 먼저 끝났지만
server Maven build가 취소됐고 server image·Docker Runtime 결과는 없습니다.
run `31305508684`는 짧은 제품 SHA 입력 때문에 checkout 단계에서 실패했습니다.
두 실행 모두 최종 검증 증거로 사용하지 않습니다.
