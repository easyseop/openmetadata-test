# OM_TEMP 1.13.1 로컬 branch 연결 및 검증 가이드

**전체 순서:** 2/11 · [전체 목차](./OM_TEMP_1.13.1_1.13.2_예행연습_전체목차.html)

> 문서 성격: 사전 준비 이후에 사용하는 별도 실행 문서
> 목적: 원격 OM_TEMP에 준비된 official·custom branch를 로컬 작업 폴더에 연결하고 실제 코드 상태를 검증
> 시작 조건: `OM_TEMP_1.13.1_기준환경_사전준비_가이드`의 완료 기준 충족
> 종료점: `custom/om-1.13.1` 코드가 로컬 작업 폴더에 구성되고 6개 검증 절차 통과
> 제외 범위: 새 snapshot commit 생성, 원격 push, Manifest·Registry·Contract 생성, 검사기 실행

**문서 이동:** [← 이전 단계 — 기준환경 사전 준비](./OM_TEMP_1.13.1_기준환경_사전준비_가이드.html)

## 공통 경로 설정

이 페이지의 명령을 실행할 터미널에서 검사기 저장소로 이동한 뒤 공통 경로를 불러옵니다. 다른 컴퓨터에서는 clone 위치만 바꾸면 됩니다.

```bash
cd <검사기-저장소-clone-경로>
```

```bash
source harness/rehearsal_env.sh
```

`OM_TEST_REPO`는 검사기 저장소, `OM_CODE_REPO`는 OpenMetadata 코드 작업 폴더, `KB_SOURCE_REPO`는 실제 커스터마이징 원본 폴더를 가리킵니다. 새 터미널을 열면 다시 실행합니다.

## 단계 연결 요약

| 구분 | 내용 |
|---|---|
| 이전 단계 요약 | Git 사용 가능 여부, OM_TEMP 접근 권한, 원본 commit, `$OM_CODE_REPO` 작업 폴더와 Git 작성자 정보를 확인했습니다. |
| 이번 단계 수행 범위 | 원격 official·custom branch를 같은 이름의 로컬 branch로 연결하고 실제 커스터마이징 코드를 작업 폴더에 구성합니다. |
| 이번 단계 완료 결과 | 로컬 branch commit, 작업 폴더 상태, 실제 원본 동일성, 113개 변경 파일과 official 기준 포함 관계가 검증됩니다. |

## 1. 작업 개요

현재 원격 `easyseop/OM_TEMP`에는 다음 두 branch가 이미 준비되어 있습니다.

| branch | 역할 | 기준 commit |
|---|---|---|
| `official/om-1.13.1` | 공식 OpenMetadata 1.13.1을 보관한 기준 코드 | `e6199070…` |
| `custom/om-1.13.1` | 공식 1.13.1에 실제 커스터마이징 113개 파일 차이를 적용한 코드 | `59dae915…` |

따라서 이 문서에서는 같은 코드를 다시 만들지 않습니다. 원격 branch를 로컬 branch에 연결한 뒤 아래 상태를 확인합니다.

```text
원격 기준 확인
    ↓
로컬 official branch 연결
    ↓
로컬 custom branch 연결 및 파일 구성
    ↓
코드·변경 파일 수·branch 관계 검증
    ↓
등록자료 작성 직전에서 종료
```

## 2. 실행 전 확인

| 확인 항목 | 요구 상태 | 불일치 시 조치 |
|---|---|---|
| 작업 폴더 | `$OM_CODE_REPO` 존재 | 사전 준비 가이드부터 다시 확인 |
| 원격 저장소 | `origin`이 `easyseop/OM_TEMP`를 가리킴 | branch 연결 중단 |
| official 원격 commit | `e6199070c35f717f7ced512bb7b435b9d46b33a3` | 결과 기록 후 중단 |
| custom 원격 commit | `59dae915342eaa3bdca1f9571bfa2ba4533c9a6f` | 결과 기록 후 중단 |
| 현재 `D` 목록 | `--no-checkout` 때문에 표시된 13,853개 항목 | `git add`·`git commit` 금지 |

## 3. 단계별 실행

### 3-1. 원격 branch 정보 갱신

**수행 내용**
`origin`의 최신 branch 위치를 로컬 Git 정보에 반영합니다. 작업 폴더의 코드 파일은 아직 변경하지 않습니다.

**입력**
인터넷 연결과 `easyseop/OM_TEMP` 읽기 권한

**실행 명령**

```bash
git -C "$OM_CODE_REPO" fetch origin
```

**예상 결과**
오류 없이 종료됩니다. 새로운 원격 변경이 있으면 branch 이름과 commit 정보가 표시될 수 있습니다.

**중단 조건**
로그인 오류 또는 `Repository not found`가 표시되면 다음 단계로 이동하지 않습니다.

### 3-2. 원격 official commit 확인

**수행 내용**
로컬 official branch가 연결될 원격 commit을 확인합니다.

**입력**
3-1에서 갱신한 `origin/official/om-1.13.1`

**실행 명령**

```bash
git -C "$OM_CODE_REPO" rev-parse refs/remotes/origin/official/om-1.13.1
```

**예상 결과**

```text
e6199070c35f717f7ced512bb7b435b9d46b33a3
```

결과가 다르면 원격 official 기준이 문서 작성 시점 이후 변경된 것입니다. branch를 연결하지 말고 결과를 기록합니다.

### 3-3. 원격 custom commit 확인

**수행 내용**
로컬 custom branch가 연결될 원격 commit을 확인합니다.

**입력**
3-1에서 갱신한 `origin/custom/om-1.13.1`

**실행 명령**

```bash
git -C "$OM_CODE_REPO" rev-parse refs/remotes/origin/custom/om-1.13.1
```

**예상 결과**

```text
59dae915342eaa3bdca1f9571bfa2ba4533c9a6f
```

결과가 다르면 원격 custom 기준이 문서 작성 시점 이후 변경된 것입니다. branch를 연결하지 말고 결과를 기록합니다.

### 3-4. 로컬 branch 중복 여부 확인

**수행 내용**
같은 이름의 로컬 branch가 이미 있는지 확인합니다.

**실행 명령**

```bash
git -C "$OM_CODE_REPO" branch --list official/om-1.13.1
```

```bash
git -C "$OM_CODE_REPO" branch --list custom/om-1.13.1
```

**예상 결과**
처음 실행하는 환경에서는 두 명령 모두 빈 출력입니다.

**기존 branch가 표시된 경우**
3-5·3-6의 생성 명령을 실행하지 않습니다. 4장의 검증 명령으로 기존 branch가 예상 commit을 가리키는지 확인합니다.

### 3-5. 로컬 official branch 연결

**수행 내용**
원격 official branch를 추적하는 같은 이름의 로컬 branch를 만듭니다. 현재 작업 branch는 바뀌지 않습니다.

**입력**
3-2에서 확인한 `origin/official/om-1.13.1`

**실행 명령**

```bash
git -C "$OM_CODE_REPO" branch --track official/om-1.13.1 origin/official/om-1.13.1
```

**예상 결과**

```text
branch 'official/om-1.13.1' set up to track 'origin/official/om-1.13.1'.
```

**산출물**
로컬 `official/om-1.13.1` branch. 4-2의 기준 commit 검증에 사용됩니다.

### 3-6. 로컬 custom branch 연결 및 코드 구성

**수행 내용**
원격 custom branch를 추적하는 로컬 branch를 만들고 해당 branch로 전환합니다. `--no-checkout` 상태였던 코드 파일이 작업 폴더에 구성됩니다.

**입력**
3-3에서 확인한 `origin/custom/om-1.13.1`

**실행 명령**

```bash
git -C "$OM_CODE_REPO" switch -c custom/om-1.13.1 --track origin/custom/om-1.13.1
```

**예상 결과**

```text
Switched to a new branch 'custom/om-1.13.1'
branch 'custom/om-1.13.1' set up to track 'origin/custom/om-1.13.1'.
```

**산출물**
로컬 `custom/om-1.13.1` branch와 작업 폴더에 구성된 실제 커스터마이징 코드. 4장의 전체 검증과 다음 단계의 등록자료 작성에 사용됩니다.

## 4. 결과 검증

각 명령은 개별적으로 실행합니다. 예상 결과와 하나라도 다르면 등록자료 작성으로 이동하지 않습니다.

### 4-1. 현재 branch 확인

```bash
git -C "$OM_CODE_REPO" branch --show-current
```

**예상 결과**

```text
custom/om-1.13.1
```

### 4-2. official·custom commit 확인

```bash
git -C "$OM_CODE_REPO" rev-parse official/om-1.13.1
```

**예상 결과:** `e6199070c35f717f7ced512bb7b435b9d46b33a3`

```bash
git -C "$OM_CODE_REPO" rev-parse custom/om-1.13.1
```

**예상 결과:** `59dae915342eaa3bdca1f9571bfa2ba4533c9a6f`

### 4-3. 작업 폴더 변경 여부 확인

```bash
git -C "$OM_CODE_REPO" status --short
```

**예상 결과**
출력이 없습니다. 사전 준비 단계에서 보였던 13,853개의 `D`도 사라져야 합니다.

출력이 있으면 파일을 임의로 추가하거나 삭제하지 말고 표시된 목록을 기록합니다.

### 4-4. 실제 커스터마이징 원본과 동일성 확인

**수행 내용**
로컬 custom branch의 파일 상태가 `kb-source/main`의 실제 원본과 같은지 비교합니다.

```bash
git -C "$OM_CODE_REPO" diff --quiet custom/om-1.13.1 kb-source/main
```

```bash
echo $?
```

**예상 결과:** `0`

`0`은 두 코드의 파일 내용이 같다는 뜻입니다. `1`이면 차이가 있으므로 등록자료를 만들지 않습니다.

### 4-5. 커스터마이징 변경 파일 수 확인

**수행 내용**
공식 1.13.1과 custom 1.13.1 사이에서 달라진 파일 수를 확인합니다.

```bash
git -C "$OM_CODE_REPO" diff --name-only official/om-1.13.1 custom/om-1.13.1 | wc -l
```

**예상 결과:** `113`

이 수치는 113개의 파일이 다르다는 뜻이며 BANK-OM 커스터마이징 ID가 113개라는 뜻이 아닙니다. 다음 단계에서 각 변경 파일을 `BANK-OM-001` 같은 커스터마이징 관리 ID에 연결합니다.

### 4-6. official 기준 포함 여부 확인

**수행 내용**
custom branch의 Git 이력 안에 official branch의 기준 commit이 포함되어 있는지 확인합니다.

```bash
git -C "$OM_CODE_REPO" merge-base --is-ancestor official/om-1.13.1 custom/om-1.13.1
```

```bash
echo $?
```

**예상 결과:** `0`

`0`은 custom branch가 공식 1.13.1을 기준으로 이어진 코드라는 뜻입니다. `1`이면 branch 관계가 예상과 다르므로 중단합니다.

## 5. 완료 기준

- [ ] 현재 branch가 `custom/om-1.13.1`입니다.
- [ ] 로컬 official commit이 `e6199070…`입니다.
- [ ] 로컬 custom commit이 `59dae915…`입니다.
- [ ] `git status --short`가 빈 출력입니다.
- [ ] 실제 커스터마이징 원본 동일성 검사 결과가 `0`입니다.
- [ ] official·custom 간 변경 파일 수가 `113`입니다.
- [ ] official 기준 포함 여부 검사 결과가 `0`입니다.

## 6. 다음 단계

완료 기준을 모두 충족하면 코드 기준환경 준비가 끝납니다. 다음 단계에서는 113개 변경 파일을 BANK-OM 커스터마이징 ID별로 연결하고 사용자 확인을 거쳐 Manifest·Registry·Contract 초안을 작성합니다.

**문서 이동:** [다음 단계 — 113개 변경 파일과 BANK-OM ID 연결](./OM_TEMP_1.13.1_113개_변경파일_기능분류_가이드.html)

이 문서에서는 다음 작업을 수행하지 않습니다.

- 원격 branch 변경 또는 push
- 새로운 commit 생성
- Manifest·Registry·Contract 생성
- openmetadata-test 검사 실행

**문서 이동:** [← 이전 단계 — 기준환경 사전 준비](./OM_TEMP_1.13.1_기준환경_사전준비_가이드.html)
