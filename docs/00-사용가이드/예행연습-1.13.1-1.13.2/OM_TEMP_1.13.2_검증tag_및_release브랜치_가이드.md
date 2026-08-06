# OM_TEMP 1.13.2 검증 tag 및 release branch 생성 가이드

**전체 순서:** 11/11 · [전체 목차](./OM_TEMP_1.13.1_1.13.2_예행연습_전체목차.html)

> 시작 조건: 필수 검사 실행 완료, BLOCK·ANALYSIS_ERROR 0개, APPROVAL 근거 완료, **1.13.2 업그레이드 후보 SHA와 배포 파일 digest 고정**.  
> 종료점: 검증 tag와 release branch가 검증한 동일 commit을 가리키고, 근거가 release lock과 인수인계서에 보관됩니다.  
> 이 문서에서 하지 않는 일: 미실행 검사를 임의 승인, 다른 commit에서 artifact 재생성, 실제 운영 배포 실행.

**문서 이동:** [← 이전 — 1.13.2 최종 검사·승인](./OM_TEMP_1.13.2_최종검사_및_승인_가이드.html)

## 공통 경로 설정

이 페이지의 명령을 실행할 터미널에서 검사기 저장소로 이동한 뒤 공통 경로를 불러옵니다. 다른 컴퓨터에서는 clone 위치만 바꾸면 됩니다.

```bash
cd <검사기-저장소-clone-경로>
```

```bash
source harness/rehearsal_env.sh
```

`OM_TEST_REPO`는 검사기 저장소, `OM_CODE_REPO`는 OpenMetadata 코드 작업 폴더, `KB_SOURCE_REPO`는 실제 커스터마이징 원본 폴더를 가리킵니다. 새 터미널을 열면 다시 실행합니다.

## 1. tag·release branch·release lock의 차이

| 항목 | 의미 | 누가 읽는가 | 변경 가능성 |
|---|---|---|---|
| 검증 tag `verified/om-1.13.2-bank.1` | 검사를 통과한 정확한 Git commit에 붙이는 고정 이름 | 운영자·Git·CI | 같은 이름을 다른 commit으로 이동하지 않음 |
| release branch `release/om-1.13.2-bank.1` | 운영에서 사용할 검증 코드 branch | 배포 CI·운영자 | 새 승인 없이 commit 추가 금지 |
| release lock | 1.13.2 업그레이드 후보 SHA, 배포 파일 digest, 검사 결과 digest, 정책·도구 버전을 묶은 증거 | T91·배포 승인 절차 | 대상이 바뀌면 새 lock 필요 |

> **\*참고 — 검증 tag**는 Git에서 널리 쓰는 tag에 이 프로젝트의 이름 규칙을 적용한 것입니다. **release lock**은 이 검사 체계에서 정의한 관리파일이며, “검사한 대상”과 “승격할 대상”이 같은지 T91이 확인할 때 사용합니다.

## 2. 승격 전 필수 확인

### 2-1. 정확한 1.13.2 업그레이드 후보 SHA

아래 명령은 9번 페이지에서 공식 1.13.2와 직전 커스텀 코드를 병합해 만든 branch가 현재 가리키는 정확한 commit을 출력합니다. 검사를 끝낸 뒤 이 값이 바뀌었다면 이전 결과는 다른 코드를 검사한 것이므로 재사용하지 않습니다.

```bash
git -C "$OM_CODE_REPO" rev-parse codex/om-1.13.2-merge-candidate
```

이 값을 `<승인된-1.13.2-업그레이드-후보-SHA>`로 기록합니다.

### 2-2. 작업 폴더와 branch 상태

```bash
git -C "$OM_CODE_REPO" status --short --branch
```

미커밋 변경이 없어야 합니다. 업그레이드 후보 branch가 검사 뒤 바뀌었다면 모든 SHA 연결 검사를 다시 실행합니다.

### 2-3. 결과 대상 일치표

| 증거 | 반드시 같은 값 | 확인 결과 |
|---|---|---|
| 검사 대상 lock(`candidate lock`) | `<승인된-1.13.2-업그레이드-후보-SHA>` |  |
| 소스 검사 결과 | 업그레이드 후보 SHA·검사 대상 lock digest |  |
| Contract·patch-kill·typecheck | 업그레이드 후보 SHA·배포 파일 digest |  |
| 승인서 | 검사 결과 digest·업그레이드 후보 SHA·정책 digest |  |
| 배포할 artifact | 검사 결과에 기록된 artifact digest |  |

하나라도 다르면 tag를 만들지 않습니다.

## 3. T91 release lock 확인

`harness/acgh/release.py`에는 release lock 생성·검증 함수가 구현돼 있지만, 현재 저장소에는 신규 운영자가 한 명령으로 실행할 T91 운영 CLI가 없습니다. 따라서 다음 정보가 담긴 release lock을 CI 또는 승인된 운영 실행기가 생성하고 검증해야 합니다.

```yaml
candidate_sha: <승인된-1.13.2-업그레이드-후보-SHA>
candidate_lock_digest: sha256:<candidate-lock-digest>
source_result_digest: sha256:<source-result-digest>
artifact_digests:
  - sha256:<검사한-artifact-digest>
promotion:
  method: promote-existing
```

`promote-existing`은 검사한 artifact를 그대로 승격한다는 뜻입니다. tag 뒤 새로 build한 artifact는 digest가 달라지므로 같은 검사 결과로 배포할 수 없습니다.

> **중단 — 현재 도구 공백:** 유효한 release lock과 T91 결과가 없으면 아래 tag·branch 명령을 실행하지 않습니다. 이 페이지는 필요한 절차를 완성했지만, 실제 승격은 T91 운영 CLI 또는 CI 연동이 추가된 뒤 수행합니다.

:::details release lock 결과별 해석

| 상황 | 판정 | 다음 행동 |
|---|---|---|
| 검사한 후보 SHA·배포 파일 digest·결과 digest가 승격 대상과 모두 같음 | `PASS` 가능 | 같은 대상을 tag·release branch로 승격 |
| 검사한 배포 파일은 `sha256:AAA`, 승격할 파일은 `sha256:BBB` | `BLOCK` | 새 파일을 다시 검사하거나 검사한 파일을 그대로 승격 |
| 필수 검사 결과 또는 승인 정보가 없음 | `ANALYSIS_ERROR` 또는 생성 중단 | 누락 자료를 만든 뒤 T91 재실행 |
| 담당자 검토가 필요한 결과에 승인 근거가 있음 | 정책에 따른 `APPROVAL` 처리 | 승인자·근거·결과 digest를 lock과 연결 |

현재는 이 판정을 한 명령으로 실행할 CLI가 없으므로 실제 결과를 만든 것처럼 표시하지 않습니다.

:::

## 4. 검증 tag 생성

3장의 release lock·T91이 통과한 뒤에만 실행합니다.

```bash
git -C "$OM_CODE_REPO" tag -a verified/om-1.13.2-bank.1 \
  <승인된-1.13.2-업그레이드-후보-SHA> \
  -m "Verified BANK-OM 1.13.2 bank.1"
```

```bash
git -C "$OM_CODE_REPO" rev-list -n 1 verified/om-1.13.2-bank.1
```

출력이 `<승인된-1.13.2-업그레이드-후보-SHA>`와 정확히 같아야 합니다.

## 5. release branch 생성

```bash
git -C "$OM_CODE_REPO" branch \
  release/om-1.13.2-bank.1 \
  verified/om-1.13.2-bank.1
```

```bash
git -C "$OM_CODE_REPO" rev-parse \
  verified/om-1.13.2-bank.1 \
  release/om-1.13.2-bank.1
```

두 줄이 같아야 합니다. 최초 1.13.1 기준에는 release branch를 만들지 않았고, 이번 1.13.2 업그레이드가 검사·승인을 통과했기 때문에 처음 생성합니다.

## 6. 원격 반영

원격 push 권한과 사용자 승인을 확인한 뒤 실행합니다.

```bash
git -C "$OM_CODE_REPO" push origin \
  verified/om-1.13.2-bank.1
```

```bash
git -C "$OM_CODE_REPO" push -u origin \
  release/om-1.13.2-bank.1
```

push 오류가 발생하면 새 tag 이름을 만들거나 force-push하지 않습니다. 원격에 같은 이름이 있는지와 대상 SHA를 먼저 확인합니다.

:::details tag·branch 생성 및 push에서 발생할 수 있는 경우

| 화면 또는 결과 | 뜻 | 조치 |
|---|---|---|
| tag·release branch의 commit SHA가 승인 SHA와 같음 | 로컬 승격 대상 일치 | 원격 권한·승인을 확인하고 push |
| `fatal: tag ... already exists` | 같은 이름의 로컬 tag가 이미 있음 | 기존 tag가 가리키는 commit을 확인; 삭제·이동하지 않음 |
| 원격 push `rejected` | 같은 이름이 원격에 있거나 권한·보호 규칙 위반 | `ls-remote`로 원격 대상을 확인하고 저장소 관리자와 처리 |
| tag는 같지만 release branch SHA가 다름 | 서로 다른 코드를 가리킴 | push 중단; branch를 만든 경위와 승인 SHA를 재확인 |
| 검사 후 새 commit이 추가됨 | 승인한 코드와 현재 branch가 달라짐 | 새 SHA에서 필수 검사를 다시 실행하고 새 release lock 생성 |

:::

## 7. 원격 결과 확인

```bash
git -C "$OM_CODE_REPO" ls-remote origin \
  refs/tags/verified/om-1.13.2-bank.1 \
  refs/heads/release/om-1.13.2-bank.1
```

annotated tag는 tag object와 commit 해석이 다를 수 있으므로 다음 명령도 실행합니다.

```bash
git -C "$OM_CODE_REPO" rev-parse \
  verified/om-1.13.2-bank.1^{commit}
```

최종 commit이 release branch SHA와 같아야 합니다.

## 8. 보관할 인수인계 증거

| 증거 | 보관 목적 |
|---|---|
| official 1.13.2 tag·SHA | 공식 입력 확인 |
| T42·위험 검사 결과 | 병합 전 영향 확인 |
| 충돌 목록·BASE/OURS/THEIRS·해결 diff·승인 | 수동 해결 근거 |
| 1.13.2 등록 변경 제안서(`proposal.yaml`)·승인서·apply 결과 | 등록 변경 승인 근거 |
| 등록·소스·공용 코드·runtime·patch-kill·typecheck·T90 결과 | 최종 판정 근거 |
| release lock·T91 결과 | 검증 대상과 승격 대상 일치 |
| tag·release branch 원격 SHA | 최종 Git 상태 |

## 9. 다음 버전 반복

```text
release/om-1.13.2-bank.1
        ↓ 다음 업그레이드의 직전 custom 기준
새 공식 버전 확인
        ↓ T42 병합 전 영향 검사
vendor merge → 충돌 해결 → 최종 검사 → 새 검증 tag·release branch
```

기존 Manifest를 매번 새 ID로 만들지 않습니다. 같은 업무 기능의 보완이면 같은 BANK-OM ID를 유지하고 새 제품 버전의 Manifest와 commit 이력을 갱신합니다. 독립적으로 배포·제거할 기능일 때만 새 BANK-OM ID를 사용자 승인으로 발급합니다.

## 10. 완료 판정

- tag와 release branch가 같은 승인된 1.13.2 업그레이드 후보 commit을 가리킵니다.
- release lock과 모든 필수 결과가 같은 업그레이드 후보 commit·배포 파일을 가리킵니다.
- 원격 SHA를 확인했습니다.
- 미실행 검사나 환경 대기 항목이 없습니다.
- 인수인계서에 결과 위치와 다음 버전 기준을 기록했습니다.

> **완료의 의미:** 이 기준은 “검증·승격할 코드가 확정됐다”는 뜻입니다. 실제 운영 배포 성공은 조직의 배포 절차와 배포 후 점검 결과로 별도 확인합니다.

**문서 이동:** [← 이전 — 1.13.2 최종 검사·승인](./OM_TEMP_1.13.2_최종검사_및_승인_가이드.html)
