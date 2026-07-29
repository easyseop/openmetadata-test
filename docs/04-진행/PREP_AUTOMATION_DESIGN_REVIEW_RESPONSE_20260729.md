# 검사 전 사전준비 자동화 설계 검토 대응

> 검토 파일: `PREP_AUTOMATION_DESIGN_REVIEW_20260729.md`
> 검토 기준: `fb891934e9977427befdd5fb9832eadc8fe7ba01`
> 대응 상태: 0~6단계 구현·OM_TEMP 1.13.0 검증 완료 · 사람 승인 대기

## 결론

검토 결과를 수용해 먼저 Manifest v2 등록자료와 소스 검사 기준선을 복구한 뒤,
읽기 전용 분석·차단 판정·제안·digest 승인·원자 적용 순서로
`plan`·`apply` 자동화 본체를 구현했습니다.

이번 대응은 검사 전 입력자료 준비 자동화의 설계와 기준선을 다룹니다. 실제
`vendor-merge`, 전체 build, 행내 Runtime test와 운영 배포 승인을 완료한
것은 아닙니다.

## 이번 배치에서 반영한 항목

1. T41 소스 실행기가 Manifest v1 필드를 직접 읽던 결함을 수정했습니다.
   소스·업그레이드 실행기 모두 `manifest.declared_scope()`를 사용합니다.
2. Registry의 `provenance`를 명시적 필수 필드로 바꿨습니다.
   기존 snapshot ID는 `source-snapshot`, 이후 신규 ID는
   `candidate-follow-up`을 직접 선택해야 합니다.
3. 등록자료 재구성 오류가 Python traceback으로 끝나지 않고
   `analysis_error` JSON과 exit code 3을 반환하도록 보강했습니다.
4. BANK-OM-007 예시를 실제 10개 변경 경로로 고쳤고, 후속 commit의 추가
   경로 2개를 제안서 예시에 모두 넣었습니다.
5. source owner 부분집합, 공용 소유맵, Candidate SHA, 동시 적용, Git
   edge case 등 검토서의 추가 차단 조건을 설계서에 반영했습니다.
6. symlink·submodule·Git LFS 차단을 Git tree mode와 blob 검사로
   구현했습니다.
7. 도입 순서를 기준선 복구 → 읽기 전용 분석 → 차단 판정 → 제안서 →
   승인·적용 → 실제 검증 → 문서 반영의 7단계로 수정했습니다.

## 실제 재검증

원격 `easyseop/OM_TEMP`의 1.13.0 patch/custom과 공식 OpenMetadata
`f329dd4a...`를 사용해 BANK-OM commit 8개를 결정론적으로 재구성했습니다.

- 재구성 후보: `3a2811cf6ec3bc172a59c307c6c70d14c3631b80`
- 후보 tree: `9495a31c99c888780ac72f3ee1bc7f7e729002de`
- 등록자료 검사: 5종 PASS
- 소스 게이트: 8종 PASS
- T41: Manifest v2 `changed_paths`를 읽어 PASS

재현 명령과 상태 경계는
`harness/registrations/om-temp-1.13.0/REPRODUCIBILITY.md`에 보관합니다.
기존 `63820f88...`는 원격에 없는 과거 로컬 후보였으므로 1.13.0 결과 파일을
현재 재구성 후보 결과로 교체했습니다.

## 2026-07-30 구현 결과

- `prepare_registration.py plan / approval-template / apply`
- BANK-OM별 commit inventory와 최종 diff 자동 계산
- 제안·사람 판단·변경 diff·digest 생성
- ID 누락·중복, merge·빈 commit, 혼합 소유, 무관 이력, 필수 경로,
  source/shared owner, symlink·submodule·LFS 차단
- 공식 patch에 없는 행내 경로는 watch에 자동 추가하지 않고 기능별 질문으로 묶음
- 승인 digest·patch/custom SHA·등록자료 digest 재확인
- 동시 적용 잠금, 원자적 파일 교체, 실패 rollback
- Candidate lock v2 `source-tree` / `build-artifact` 구분
- 기존 하드코딩 Manifest 생성기 제거

실제 OM_TEMP 1.13.0 plan은 자동 변경 0건, 사람 판단 5건, 차단·분석 오류
0건으로 `REVIEW_REQUIRED`다. 사람 승인 없이 등록자료를 적용하지 않았다.
결정론적 재실행 결과도 같았다. 등록자료 5종과 Candidate lock v2에 결속한
소스 게이트 8종은 PASS다.

## 남은 외부 입력

1. 1.13.0의 기능별 bank-only watch 질문 5건에 대한 담당자 판단과 승인자
2. 조직 owner 배정
3. 원격 `patch/om-1.13.1`·`custom/om-1.13.1` 후보
4. 전체 build, 행내 runtime, 실제 산출물·배포 증거

1.13.1 후보와 사람 값을 추측하거나 과거 결과로 대체하지 않습니다.
