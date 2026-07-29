# OM_TEMP 1.13.0 소스 검사 재현 기준

> 상태: Manifest v2 T41·Candidate lock v2 반영 후 2026-07-30 재검증 완료
> 범위: 소스 등록자료 5종과 소스 게이트 8종
> 운영 배포 상태: 미실행

## 재검증 입력

- 공식 기준: `open-metadata/OpenMetadata`
  `f329dd4a7e47134a2bd5a06af6181b0ee527ddd9`
- 원격 patch: `easyseop/OM_TEMP` `patch/om-1.13.0`
  `2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50`
- 원격 custom: `easyseop/OM_TEMP` `custom/om-1.13.0`
  `7d19c8952612e77467b0a80d6287170d814f1de1`
- 원격 patch와 공식 기준의 Git tree:
  `da56c24d61a98dc4ed1001800c80866a13bc1645`

OM_TEMP 원격은 공식 Git 계보를 보존하지 않은 독립 snapshot입니다. 소스
게이트의 공식 포함 관계를 재검증하기 위해 원격 patch 이후 BANK-OM commit
8개를 공식 기준 commit 위에 같은 순서로 다시 적용했습니다.

## 결정론적 재구성

다음 명령은 임시 clone에서 실행합니다. `user.name`, `user.email`과
`--committer-date-is-author-date`를 고정해야 같은 후보 SHA가 만들어집니다.

```bash
git clone --filter=blob:none --no-checkout \
  https://github.com/easyseop/OM_TEMP.git \
  /tmp/om-temp-1.13.0-source-recheck

git -C /tmp/om-temp-1.13.0-source-recheck fetch --filter=blob:none \
  https://github.com/open-metadata/OpenMetadata.git \
  f329dd4a7e47134a2bd5a06af6181b0ee527ddd9

git -C /tmp/om-temp-1.13.0-source-recheck switch \
  -c recheck/deterministic-1.13.0 \
  origin/custom/om-1.13.0

git -C /tmp/om-temp-1.13.0-source-recheck \
  -c user.name="JISEOP LEE" \
  -c user.email="71008721+easyseop@users.noreply.github.com" \
  rebase \
  --onto f329dd4a7e47134a2bd5a06af6181b0ee527ddd9 \
  origin/patch/om-1.13.0 \
  recheck/deterministic-1.13.0 \
  --committer-date-is-author-date
```

예상 결과:

- 후보 commit:
  `3a2811cf6ec3bc172a59c307c6c70d14c3631b80`
- 후보 tree:
  `9495a31c99c888780ac72f3ee1bc7f7e729002de`
- 후보 tree는 기존 원격 custom 최종 tree와 같습니다.

## 실행 결과

- `registration-validation-results.json`: 5종 PASS
- `source-gate-results.json`: 8종 PASS
- Candidate lock schema v2는 이 결과가 실제 build 산출물이 아니라
  `artifact_kind: source-tree`임을 명시
- T41은 Manifest v1 필드를 직접 읽지 않고
  `manifest.declared_scope()`로 Manifest v2 `changed_paths`를 읽었습니다.
- 기존 `63820f88...` 결과는 원격에 없는 과거 로컬 후보에 결속돼 있었으므로
  현재 파일은 위 결정론적 후보의 재실행 결과로 교체했습니다.

이 결과는 소스 코드 구조와 등록자료의 일치를 확인합니다. OpenMetadata 전체
build, 행내 Contract test, 담당자 승인과 운영 배포 완료를 의미하지 않습니다.

OM_TEMP 1.13.1 후보는 아직 원격에 없으므로 1.13.1 결과 파일은 이 재검증
범위에 포함하지 않습니다.
