# OM_TEMP 1.13.1 실제 커스터마이징 기준환경 예행연습

> 작성 기준: 2026-08-04
> 코드 저장소: `easyseop/OM_TEMP`
> 이번 문서의 종료점: `official/om-1.13.1`과 `custom/om-1.13.1` 준비 및 검증 완료
> 이번 문서에서 하지 않는 일: Manifest·Registry·Contract 생성, 검사 실행, release branch 생성

전체 작업 목적·결정·검증·다음 시작점은 `OM_TEMP_작업기록_및_인수인계.md`에 누적합니다.

## 1. 이번 작업의 목적

기존 1.13.0 재구현 코드가 아니라, 로컬에 보관된 `kb_openmetadata`의 실제 1.13.1 커스터마이징 코드를 다음 업그레이드 검사의 출발점으로 복원합니다.

```text
공식 OpenMetadata 1.13.1 파일 상태
            ↓ official/om-1.13.1
실제 kb_openmetadata 파일 상태
            ↓ custom/om-1.13.1
등록자료 작성 직전에서 중단
```

`custom/om-1.13.1`은 최초 기준환경입니다. 아직 상위 버전으로 업그레이드한 결과가 아니므로 `release/*` 브랜치를 만들지 않습니다. 이후 1.13.2 업그레이드와 검사·승인을 통과한 코드가 생길 때 release branch를 만듭니다.

## 2. 사용한 입력

| 구분 | 값 | 의미 |
|---|---|---|
| 공식 1.13.1 commit | `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9` | OpenMetadata 공식 `1.13.1-release`가 가리키는 코드 |
| 공식 1.13.1 tree | `a8290d23b0fb7a4bdc860c2ff414d799f66417c5` | 공식 1.13.1 전체 파일 상태 |
| 실제 커스터마이징 snapshot commit | `2c2347043235aa2a4ecba4729774c770fcee5d67` | 로컬 `kb_openmetadata`에서 복원한 실제 코드 기준 |
| 실제 커스터마이징 tree | `1df344b65844307fb4637f427778afa4d3b13bf7` | 실제 커스터마이징 전체 파일 상태 |
| 기존 OM_TEMP 기준 | `patch/om-1.13.0` | OM_TEMP에 이미 있던 공식 1.13.0 스냅샷 |

`commit`은 변경 이력을 가리키는 번호이고, `tree`는 그 시점의 전체 파일 상태를 가리키는 번호입니다. 이번 복원에서는 파일이 같은지를 판단하기 위해 tree를 사용합니다.

## 3. 수행 결과

| 단계 | 생성한 브랜치 | commit | 결과 |
|---|---|---|---|
| 공식 1.13.1 준비 | `official/om-1.13.1` | `e6199070c35f717f7ced512bb7b435b9d46b33a3` | 공식 1.13.1 tree와 일치 |
| 실제 커스터마이징 복원 | `custom/om-1.13.1` | `59dae915342eaa3bdca1f9571bfa2ba4533c9a6f` | `kb_openmetadata` snapshot tree와 일치 |

두 브랜치는 `easyseop/OM_TEMP` 원격에 푸시했습니다.

## 4. 단계별 실행

### 4-1. 격리된 작업 폴더 준비

**하는 일**
기존 OM_TEMP 작업 폴더와 브랜치를 건드리지 않도록 별도 복제본을 만듭니다.

**입력**
`easyseop/OM_TEMP`에 대한 읽기·쓰기 권한

```bash
git clone --filter=blob:none --no-checkout https://github.com/easyseop/OM_TEMP.git work/om-temp-real-1.13.1
```

**출력**
`work/om-temp-real-1.13.1` 작업 폴더

### 4-2. 실제 커스터마이징 원본 연결

**하는 일**
로컬에 보관된 `kb_openmetadata`를 복원 원본으로 연결합니다.

```bash
git remote add kb-source /path/to/review-kb-openmetadata
```

```bash
git fetch kb-source refs/remotes/origin/main:refs/remotes/kb-source/main refs/tags/1.13.1-release:refs/tags/1.13.1-release
```

**출력**
`kb-source/main`과 공식 `1.13.1-release`를 로컬에서 조회할 수 있습니다.

### 4-3. 공식 1.13.1 스냅샷 생성

**하는 일**
OM_TEMP의 기존 1.13.0 스냅샷 다음에 공식 1.13.1 전체 파일 상태를 한 커밋으로 기록합니다. 공식 저장소의 방대한 과거 이력을 통째로 복사하지 않고, 원본 commit·tree는 커밋 메시지에 보존합니다.

```bash
git commit-tree a8290d23b0fb7a4bdc860c2ff414d799f66417c5 \
  -p 2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50 \
  -m 'Import official OpenMetadata 1.13.1 source snapshot' \
  -m 'Upstream-Tag: 1.13.1-release' \
  -m 'Upstream-Commit: afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9' \
  -m 'Upstream-Tree: a8290d23b0fb7a4bdc860c2ff414d799f66417c5'
```

**출력**
공식 스냅샷 commit `e6199070c35f717f7ced512bb7b435b9d46b33a3`

```bash
git branch official/om-1.13.1 e6199070c35f717f7ced512bb7b435b9d46b33a3
```

### 4-4. 실제 커스터마이징 스냅샷 생성

**하는 일**
공식 1.13.1 스냅샷 바로 다음에 `kb_openmetadata`의 실제 전체 파일 상태를 기록합니다. 이 커밋은 BANK-OM 기능별 등록이 아니라, 원본을 정확히 복원하기 위한 기준 커밋입니다.

```bash
git commit-tree 1df344b65844307fb4637f427778afa4d3b13bf7 \
  -p e6199070c35f717f7ced512bb7b435b9d46b33a3 \
  -m 'Restore actual kb_openmetadata 1.13.1 customization baseline' \
  -m 'Source-Snapshot: 2c2347043235aa2a4ecba4729774c770fcee5d67' \
  -m 'Source-Tree: 1df344b65844307fb4637f427778afa4d3b13bf7' \
  -m 'Official-Commit: afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9' \
  -m 'Official-Snapshot-Commit: e6199070c35f717f7ced512bb7b435b9d46b33a3'
```

**출력**
실제 커스터마이징 기준 commit `59dae915342eaa3bdca1f9571bfa2ba4533c9a6f`

```bash
git branch custom/om-1.13.1 59dae915342eaa3bdca1f9571bfa2ba4533c9a6f
```

### 4-5. 검증

#### 검증 A — 실제 원본과 같은가

```bash
git diff --quiet custom/om-1.13.1 kb-source/main
```

출력이 없고 종료 코드가 `0`이면 전체 추적 파일이 같습니다.

#### 검증 B — tree 번호가 같은가

```bash
git rev-parse custom/om-1.13.1^{tree}
```

```bash
git rev-parse kb-source/main^{tree}
```

두 명령 모두 다음 값을 출력해야 합니다.

```text
1df344b65844307fb4637f427778afa4d3b13bf7
```

#### 검증 C — 공식 코드 대비 변경 파일이 113개인가

```bash
git diff --name-only official/om-1.13.1 custom/om-1.13.1 | wc -l
```

기대값은 `113`입니다.

#### 검증 D — custom이 official 다음에 이어지는가

```bash
git merge-base --is-ancestor official/om-1.13.1 custom/om-1.13.1
```

출력이 없고 종료 코드가 `0`이면 `custom/om-1.13.1`이 공식 기준 위에 놓여 있습니다.

### 4-6. 원격 푸시

```bash
git push --set-upstream origin official/om-1.13.1
```

```bash
git push --set-upstream origin custom/om-1.13.1
```

## 5. 지금 상태에서 반드시 멈추는 이유

다음 단계에서는 113개 파일 차이를 기능 단위로 나누고 BANK-OM ID와 연결해야 합니다. 이 판단은 자동으로 확정하면 안 됩니다.

| 다음 산출물 | 함께 결정할 내용 |
|---|---|
| Manifest | 어떤 변경 파일이 어떤 BANK-OM 기능에 속하는지, 필수·허용·감시 경로가 무엇인지 |
| Registry | BANK-OM ID, 담당자, 상태, 기준 commit 이력을 어떻게 등록할지 |
| Contract | 기능이 정상이라고 볼 업무 동작과 이를 확인할 필수 test가 무엇인지 |

따라서 현재는 **등록자료를 만들기 직전의 정확한 코드 기준환경**까지만 완성된 상태입니다.

## 6. 다음 세션의 시작 체크리스트

- [ ] `official/om-1.13.1` 원격 commit이 `e6199070c35f...`인지 확인
- [ ] `custom/om-1.13.1` 원격 commit이 `59dae915342e...`인지 확인
- [ ] 두 tree 비교 결과가 동일한지 재확인
- [ ] 공식 대비 변경 파일 수가 113인지 재확인
- [ ] 113개 변경 목록을 기능 단위로 분류
- [ ] 사용자와 BANK-OM ID·Manifest·Registry·Contract 초안을 함께 확정
- [ ] 등록 승인 이후에만 검사 실행
