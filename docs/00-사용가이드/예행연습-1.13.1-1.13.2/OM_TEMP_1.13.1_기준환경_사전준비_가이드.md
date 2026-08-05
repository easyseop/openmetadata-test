# OM_TEMP 1.13.1 기준환경 사전 준비 가이드

> 별도 신규 문서 · 기존 코덱스 수정본은 변경하지 않음
> 목적: 공식 1.13.1과 실제 커스터마이징 코드를 복원하기 전에 입력·권한·작업 폴더를 확인
> 종료점: 원격 branch를 로컬에 연결할 수 있는 작업 폴더 준비 완료
> 제외 범위: official·custom branch 생성, Manifest·Registry·Contract 생성, 검사 실행

## 단계 연결 요약

| 구분 | 내용 |
|---|---|
| 이전 단계 요약 | 없음. 이 문서는 실제 1.13.1 기준환경 구성 절차의 시작 단계입니다. |
| 이번 단계 수행 범위 | Git 사용 가능 여부, OM_TEMP 접근 권한, 공식·커스터마이징 원본 commit, 별도 작업 폴더와 Git 작성자 정보를 확인합니다. |
| 이번 단계 완료 결과 | 원격 official·custom branch를 로컬에 연결할 수 있는 작업 폴더가 준비됩니다. |

## 1. 작업 개요

이번 사전 준비에서는 다음 순서로 확인합니다.

```text
Git 사용 가능 확인
    ↓
OM_TEMP 접근 확인
    ↓
실제 kb_openmetadata 원본 확인
    ↓
공식 1.13.1 기준 확인
    ↓
별도 작업 폴더 준비
    ↓
원격 branch 연결 직전에서 종료
```

이 단계가 끝나면 다음 문서에서 원격에 준비된 `official/om-1.13.1`과 `custom/om-1.13.1`을 로컬 branch로 연결하고 코드 상태를 검증합니다.

## 2. 사전 준비 항목

| 준비 항목 | 사용 목적 |
|---|---|
| Git | 원격 코드를 받고 branch·commit·tree를 확인합니다. |
| `easyseop/OM_TEMP` 접근 권한 | 코드를 받고, 다음 단계에서 완성한 branch를 push합니다. |
| 로컬 `review-kb-openmetadata` 폴더 | 실제 1.13.1 커스터마이징 원본으로 사용합니다. |
| `~/om-work` 폴더 | 반복 작업에 사용하는 로컬 작업 공간입니다. 정확한 이름은 밑줄(`om_work`)이 아니라 하이픈(`om-work`)입니다. |
| 인터넷 연결 | GitHub의 OM_TEMP에 연결합니다. |

### 현재 `~/om-work`에 이미 있는 폴더

| 경로 | 현재 역할 | 이번 사전 준비에서의 처리 |
|---|---|---|
| `~/om-work/OM_TEMP` | 기존 OM_TEMP 클론이며 현재 `patch/om-1.13.0`을 사용 중입니다. | 기존 작업을 보존하기 위해 branch를 바꾸거나 파일을 수정하지 않습니다. |
| `~/om-work/openmetadata-test` | 검사기 저장소 클론입니다. | 등록자료를 만들기 전이므로 이 문서에서는 수정하지 않습니다. |
| `~/om-work/om-temp-real-1.13.1` | 이번 1.13.1 복원 예행연습용 폴더입니다. | 없으면 새로 만들고, 있으면 다시 clone하지 않습니다. |

실제 커스터마이징 원본인 `review-kb-openmetadata`는 현재 `~/om-work` 아래에 없습니다. 이 원본만 기존 Codex 작업 폴더의 경로를 사용합니다.

## 3. 단계별 명령

### 3-1. Git 설치 확인

**수행 내용**
이 컴퓨터에서 Git 명령을 사용할 수 있는지 확인합니다.

**실행 위치**
아무 폴더에서 실행해도 됩니다.

```bash
git --version
```

**예상 결과**

```text
git version 2.x.x
```

`command not found`가 나오면 Git을 설치하기 전까지 진행하지 않습니다.

### 3-2. OM_TEMP 읽기 권한 확인

**수행 내용**
인터넷 연결과 `easyseop/OM_TEMP`를 읽을 수 있는지 확인합니다. 파일을 내려받거나 수정하지는 않습니다.

```bash
git ls-remote --heads https://github.com/easyseop/OM_TEMP.git
```

**예상 결과**
여러 줄의 SHA와 branch 이름이 출력됩니다.

로그인 오류 또는 `Repository not found`가 나오면 GitHub 로그인을 확인한 뒤 다시 실행합니다. 같은 오류가 반복되면 다음 단계로 이동하지 않습니다.

### 3-3. 실제 커스터마이징 원본 확인

**수행 내용**
`custom/om-1.13.1` 복원에 사용할 실제 `kb_openmetadata` commit을 확인합니다.

```bash
git -C /Users/seop/Documents/Codex/2026-07-24/sites-plugin-sites-openai-bundled/work/review-kb-openmetadata rev-parse refs/remotes/origin/main
```

**예상 결과**

```text
2c2347043235aa2a4ecba4729774c770fcee5d67
```

이 값이 다르면 실제 커스터마이징 원본이 달라진 것입니다. 결과를 기록하고 branch를 만들지 않습니다.

### 3-4. 공식 1.13.1 기준 확인

**수행 내용**
`official/om-1.13.1`에 기록할 공식 OpenMetadata 1.13.1 commit을 확인합니다.

```bash
git -C /Users/seop/Documents/Codex/2026-07-24/sites-plugin-sites-openai-bundled/work/review-kb-openmetadata rev-parse refs/tags/1.13.1-release
```

**예상 결과**

```text
afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9
```

이 값이 다르면 공식 기준이 달라진 것입니다. 결과를 기록하고 branch를 만들지 않습니다.

### 3-5. 작업 폴더로 이동

**수행 내용**
반복 작업에 사용하는 `~/om-work`로 이동합니다. `~`는 현재 사용자의 홈 폴더인 `/Users/seop`을 뜻합니다.

```bash
cd ~/om-work
```

이 명령은 파일을 변경하지 않고 현재 터미널 위치만 바꿉니다.

### 3-6. OM_TEMP를 별도 폴더에 clone

**수행 내용**
이번 복원 작업만 수행할 `om-temp-real-1.13.1` 폴더를 만듭니다.

```bash
git clone --filter=blob:none --no-checkout https://github.com/easyseop/OM_TEMP.git om-temp-real-1.13.1
```

`--filter=blob:none`은 처음부터 모든 대용량 파일을 받지 않고 필요할 때 받습니다. `--no-checkout`은 아직 코드 파일을 펼치지 않는다는 뜻입니다.

**예상 결과**
`~/om-work/om-temp-real-1.13.1` 폴더가 생성됩니다. 기존 `~/om-work/OM_TEMP`는 수정되지 않습니다.

이미 같은 폴더가 있다면 이 clone 명령을 다시 실행하지 않습니다.

### 3-7. 실제 원본 폴더 연결

**수행 내용**
새 작업 폴더에서 로컬 `review-kb-openmetadata`를 `kb-source`라는 이름으로 조회할 수 있게 연결합니다. 원본 폴더의 파일은 수정하지 않습니다.

**필요성**
새로 clone한 `om-temp-real-1.13.1`은 GitHub의 `easyseop/OM_TEMP`만 알고 있습니다. 실제 커스터마이징 코드는 별도 로컬 폴더인 `review-kb-openmetadata`에 있으므로, 새 작업 폴더에 그 위치를 먼저 알려줘야 합니다.

이 명령은 코드를 복사하지 않습니다. `kb-source`라는 이름과 실제 원본 폴더의 경로만 새 작업 폴더의 Git 설정에 기록합니다.

```bash
git -C ~/om-work/om-temp-real-1.13.1 remote add kb-source /Users/seop/Documents/Codex/2026-07-24/sites-plugin-sites-openai-bundled/work/review-kb-openmetadata
```

**예상 결과**
출력이 없습니다.

`remote kb-source already exists`가 나오면 이미 연결되어 있다는 뜻입니다. 다음 명령으로 실제 연결 주소를 확인합니다.

```bash
git -C ~/om-work/om-temp-real-1.13.1 remote -v
```

`kb-source`가 `review-kb-openmetadata` 경로를 가리키면 다시 추가하지 않습니다.

**적용 조건**
실제 커스터마이징 원본에서 `custom/om-1.13.1`을 처음 복원하는 과정을 재현할 때 실행합니다. 이미 원격에 만들어진 `custom/om-1.13.1`을 내려받기만 하는 경우에는 실행하지 않습니다.

### 3-8. 복원에 필요한 기준 가져오기

**수행 내용**
실제 커스터마이징 commit과 공식 1.13.1 tag를 새 작업 폴더에서 사용할 수 있게 가져옵니다. 아직 branch는 만들지 않습니다.

**필요성**
3-7은 원본 위치만 등록했기 때문에 새 작업 폴더에는 아직 실제 커스터마이징 commit이 없습니다. 3-8의 `fetch`가 원본 Git 이력을 실제로 읽어 와야 원본과 원격 custom branch의 동일성을 확인할 수 있습니다.

- 실제 커스터마이징 commit은 다음 단계의 `custom/om-1.13.1` 생성에 사용합니다.
- 공식 `1.13.1-release` tag는 다음 단계의 `official/om-1.13.1` 생성에 사용합니다.

```bash
git -C ~/om-work/om-temp-real-1.13.1 fetch kb-source refs/remotes/origin/main:refs/remotes/kb-source/main refs/tags/1.13.1-release:refs/tags/1.13.1-release
```

**예상 결과**
`kb-source/main`과 `1.13.1-release`가 새로 추가됐다는 메시지가 표시됩니다.

`couldn't find remote ref` 또는 `not a git repository`가 나오면 필요한 commit이나 tag를 가져오지 못한 것입니다. branch를 만들지 말고 3-3·3-4의 원본 경로와 기준값부터 다시 확인합니다.

**기존 원격 branch 활용 시**
현재 `easyseop/OM_TEMP` 원격에는 `official/om-1.13.1`과 `custom/om-1.13.1`이 이미 있습니다. 최초 복원을 재현하지 않고 이 branch를 사용하기만 한다면 3-7·3-8 대신 `git fetch origin`으로 원격 branch를 받습니다.

### 3-9. Git 작성자 확인

**수행 내용**
향후 승인된 코드 변경 commit에 기록될 작성자 이름과 이메일을 확인합니다.

```bash
git -C ~/om-work/om-temp-real-1.13.1 config user.name
```

```bash
git -C ~/om-work/om-temp-real-1.13.1 config user.email
```

두 명령 중 하나라도 빈 출력이면 작성자 정보를 설정한 뒤 진행합니다. 다른 사람의 이름이나 이메일을 임의로 입력하지 않습니다.

**작성자 정보 미설정 시 조치**
아래 설정은 `~/om-work/om-temp-real-1.13.1`에만 적용됩니다. 다른 Git 저장소의 작성자 정보는 바뀌지 않습니다.

먼저 첫 번째 명령의 `JISEOP LEE`를 commit에 표시할 본인 이름으로 확인하거나 바꾼 뒤 실행합니다.

```bash
git -C ~/om-work/om-temp-real-1.13.1 config --local user.name "JISEOP LEE"
```

두 번째 명령의 `YOUR_GITHUB_EMAIL`을 본인 GitHub 계정의 이메일 또는 GitHub에서 제공한 비공개 이메일 주소로 바꾼 뒤 실행합니다. `YOUR_GITHUB_EMAIL` 문구를 그대로 등록하면 안 됩니다.

```bash
git -C ~/om-work/om-temp-real-1.13.1 config --local user.email "YOUR_GITHUB_EMAIL"
```

이 이름과 이메일은 향후 이 작업 폴더에서 만드는 Git commit의 작성자 정보로 기록됩니다. GitHub 로그인이나 push 권한을 설정하는 명령은 아닙니다.

**등록 결과 확인**
등록 명령을 실행한 뒤 아래 두 명령을 다시 실행합니다.

```bash
git -C ~/om-work/om-temp-real-1.13.1 config --local --get user.name
```

```bash
git -C ~/om-work/om-temp-real-1.13.1 config --local --get user.email
```

첫 번째 결과에 본인 이름, 두 번째 결과에 본인 이메일이 나오면 3-9가 완료된 것입니다. 여전히 빈 출력이거나 다른 사람의 정보가 나오면 commit을 만들지 않습니다.

### 3-10. 현재 상태 확인

**수행 내용**
새 작업 폴더가 준비됐는지 확인합니다.

```bash
git -C ~/om-work/om-temp-real-1.13.1 status --short
```

현재 기준에서는 `D`가 13,853줄 표시됩니다. 이는 `--no-checkout`으로 전체 파일을 아직 펼치지 않아 나타나는 상태이며, 사용자가 파일을 삭제한 결과가 아닙니다. 일반 `git add`나 `git commit`으로 이 목록을 반영하지 않습니다. 다음 문서에서 원격 custom branch로 전환하면 코드 파일이 작업 폴더에 펼쳐지고 이 목록이 사라집니다.

## 4. 사전 준비 완료 기준

다음 항목이 모두 맞으면 사전 준비가 끝난 것입니다.

- [ ] `git --version`이 정상 출력됩니다.
- [ ] OM_TEMP branch 목록을 읽을 수 있습니다.
- [ ] 실제 원본 commit이 `2c234704…`입니다.
- [ ] 공식 1.13.1 commit이 `afcb2d2…`입니다.
- [ ] `~/om-work/om-temp-real-1.13.1` 작업 폴더가 있습니다.
- [ ] 기존 `~/om-work/OM_TEMP`의 branch와 파일은 변경되지 않았습니다.
- [ ] `kb-source`가 실제 원본 폴더를 가리킵니다.
- [ ] Git 작성자 이름과 이메일이 비어 있지 않습니다.

하나라도 맞지 않으면 branch 연결 단계로 이동하지 않습니다.

## 5. 다음 단계

사전 준비가 끝나면 `OM_TEMP_1.13.1_로컬브랜치_연결_및_검증_가이드.md`를 열어 다음 작업을 수행합니다.

1. 원격 official·custom branch 기준 commit 확인
2. 원격 branch를 같은 이름의 로컬 branch로 연결
3. custom 코드 파일을 작업 폴더에 구성
4. 실제 원본 동일성·113개 변경·branch 관계 검증

Manifest·Registry·Contract는 그 이후 사용자와 함께 작성합니다.

**문서 이동:** [다음 단계 — 로컬 branch 연결 및 검증](./OM_TEMP_1.13.1_로컬브랜치_연결_및_검증_가이드.md)
