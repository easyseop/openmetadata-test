# OM_TEMP 1.13.0 → 1.13.1 업그레이드 예행연습 실행 순서 · 코덱스 수정본

> 최종 갱신: 2026-08-04 · 코덱스 문구 검토본
>
> 대상: 직접 실행하고 발표 자료용 화면을 캡처할 담당자
>
> 걸리는 시간: 처음 준비 20분 · 이후 실행은 5분
>
> 디스크: OM_TEMP 폴더는 약 230MB까지 늘어납니다. 공식 1.13.0과 1.13.1
> 소스를 모두 받아 두기 때문에, 다운로드가 끝난 뒤에는 네트워크 연결이
> 끊겨도 예행연습을 계속 실행할 수 있습니다.
>
> **후보 코드 생성 예행연습은 다른 노트북에서도 완주했습니다.**
> 2026-08-03에 문서 작성에 사용한 환경과 다른 노트북(macOS 26.5.2 · Git
> 2.50.1 · Python 3.9.6)에서 4부까지 실행했고, tree SHA
> `e490ed82dd…`가 동일하게 나왔습니다. 이는 파일 경로·내용·mode가 같은
> 후보 코드를 재현했다는 뜻이며, build·행내 기능 시험·운영 배포 완료를 뜻하지
> 않습니다. 캡처와 실행 로그는
> [`assets/업그레이드시연/`](assets/업그레이드시연/) 에 있습니다.

이 문서는 준비부터 후보 코드 생성과 소스 검사까지 시간 순서대로 설명합니다.
이미 같은 환경에서 한 번 실행했다면 바로 아래 **0부**에서 시작하고,
처음 실행한다면 **1부**부터 진행하십시오. 📸 표시는 발표 자료로 남길
화면을 뜻합니다.

## 저장소가 두 개입니다

| 저장소 | 역할 | 이 문서에서 |
|---|---|---|
| `easyseop/OM_TEMP` | 업그레이드 연습용 제품 소스 | 1~4부에서는 읽고 임시 worktree만 만듭니다 |
| `easyseop/openmetadata-test` | Manifest·검사 도구·결과·문서 | **안내된 명령의 기준 작업 폴더**입니다 |

명령은 별도 안내가 없으면 `openmetadata-test` 저장소 루트에서
실행하며, `--repo` 또는 스크립트 인자로 `OM_TEMP` 경로를 지정합니다.

## 이 문서에서 쓰는 말

화면·명령·결과 파일과 같은 용어를 사용합니다. 처음 보는 용어는 아래에서
뜻을 설명하되, branch나 commit을 별도의 별칭으로 바꾸지 않습니다.

| 용어 | 이 문서의 표기 | 이 문서에서의 의미 |
|---|---|---|
| `branch` | **branch** | 특정 코드 이력을 가리키는 Git branch |
| `commit` | **commit** | 한 번에 저장한 코드 변경과 설명 |
| `commit SHA` | **Git commit SHA** | 특정 commit을 고정해서 가리키는 값 |
| `Customization-ID` | **Customization-ID** | commit을 BANK-OM 기능과 연결하는 프로젝트 내부 ID |
| `conflict` | **충돌** | Git이 변경 내용을 자동으로 합치지 못해 중단한 상태 |
| `resolve` | **해결** | 충돌한 내용을 검토해 하나의 결과로 확정하는 작업 |
| merge commit | **merge commit** | 두 branch 이력을 연결하며 부모가 둘인 Git commit |
| leaf / entry | **항목** | JSON 파일에서 중첩 경로로 식별되는 최종 이름-값 쌍 |
| `candidate` | **후보 코드** | 공식 1.13.1 소스에 BANK-OM 변경을 재적용한 검사 대상 코드 상태 |
| `upstream`, `공식` | **공식 OpenMetadata 소스** | 행내 커스터마이징을 적용하지 않은 공식 기준 코드 |
| `upgrade_watch` | **업그레이드 감시 경로** | 공식 버전 변경 시 담당자가 영향을 다시 검토할 경로 목록 |

## 캡처는 모두 26장입니다

| 종류 | 장수 | 표기 |
|---|---|---|
| 터미널 화면 | 16장 | 📸 ① ~ ⑯ (⑭~⑯ 은 6부, 선택) |
| GitHub 화면 | 10장 | 📸 G1 ~ G6 (G3b 2장, G6 3장 포함) |

구간 3(영향 확인)은 화면이 길어서 **위·아래 두 장**으로 나눠 찍으시면
읽기 좋습니다.

★ 표시한 것(⑦ ⑧ ⑩ G2 G5)이 발표에서 가장 중요한 다섯 장입니다.

## 지금 어디까지 왔나

아래 표는 2026-08-03에 확보한 캡처와 실행 증거를 기준으로 작성했습니다.
✅는 해당 화면이나 결과가 이미 있다는 뜻이며, 운영 배포 완료를 뜻하지
않습니다. 시연 당일 새로 실행할 항목은 ☐로 표시했습니다.

|  | 단계 | 무엇 | 확인값 |
|---|---|---|---|
| ✅ | 1부 1~4 | 준비물 설치 | `준비 완료` |
| ✅ | 1부 5 | 기준 SHA 확인 | `2f4f3560e7…` / `7d19c89526…` |
| ☐ | **1부 6** | **작업 폴더 깨끗한지** | **빈 출력** |
| ✅ | 2부 G1 | branch 목록 | `Ahead 8` |
| ✅ | 2부 G2 ★ | 두 branch 비교 | `8 commits` · `111 files` |
| ✅ | 2부 G3 | commit 목록 | 8건 + 맨 아래 `2f4f356` |
| ✅ | 2부 G3b | Customization-ID 상세 2장 | `Customization-ID:` |
| ✅ | 2부 G4 | 공식 릴리스 | `1.13.1-release` · `afcb2d2` |
| ✅ | 2부 G5 ★ | 공식 두 버전 비교 | `Files changed 834` |
| ✅ | 2부 G6 | Manifest 실물 3장 | `required_changed_paths` |
| ☐ | **3부** | **예행연습 실행** | 요약표 8행 |
| ☐ | **4부 ★★** | **재현 확인** | `e490ed82dd…` |
| ☐ | **5부** | **후보 검사 · 승인 시 원격 공유** | 등록 5/5 · 게이트 8/8 |
| ☐ | 6부 (선택) | Manifest 만드는 과정 | `REVIEW_REQUIRED` |

> **시연 당일 다시 수행할 항목은 네 가지입니다.** 1부 6번에서 작업
> 폴더 상태를 확인하고, 3부에서 후보 코드를 만든 뒤, 4부에서 tree SHA를
> 대조합니다. 5부의 원격 push와 검사는 저장소 쓰기 권한과 담당자 승인을 받은
> 경우에만 수행합니다.

### 기존 캡처의 사용 범위

[`assets/업그레이드시연/`](assets/업그레이드시연/) 에 캡처가 들어 있고,
아래 본문에도 붙여 두었습니다. 대부분 그대로 사용할 수 있지만, 구간 5의
요약표 캡처 ⑧은 과거 집계 방식의 숫자를 보여주므로 **현재 스크립트로
다시 찍어야 합니다.** 캡처 출처는 다음과 같습니다.

| 종류 | 어디서 나온 것 |
|---|---|
| GitHub 화면 (G1 ~ G6 전부) | 이번 시연 담당자가 직접 찍은 것 |
| 터미널 화면 (④~⑩) | 2026-08-03 **다른 컴퓨터**에서 전 과정을 돌려 찍은 것 |
| 터미널 화면 일부 (구간 0~3) | 담당자가 직접 돌려 찍은 것도 함께 실었습니다 |

다른 노트북의 터미널 캡처는 작성 환경에만 의존한 절차가 아니라는 재현
근거입니다. 두 노트북에서 같은 tree SHA가 나온 사실을 설명할 때 사용하십시오.
GitHub 캡처는 담당자가 직접 확인한 화면을 사용합니다.

지금 하시는 것은 발표 전 직접 돌려 보는 예행연습입니다.

---

# 0부 · 이미 준비가 끝났다면 (시연 직전 4단계)

전에 한 번 돌려 본 컴퓨터라면 1부를 건너뛰고 여기서 시작하십시오.

```bash
# ① 지난 예행연습이 만든 임시 worktree와 branch만 정리합니다.
#    아래 경로와 branch가 예행연습 산출물인지 먼저 확인한 뒤 실행하십시오.
git -C ~/om-work/OM_TEMP worktree remove --force ~/om-work/upgrade-rehearsal/tree
git -C ~/om-work/OM_TEMP branch -D rehearsal/patch-1.13.1 rehearsal/custom-1.13.1
rm -rf ~/om-work/upgrade-rehearsal

# ② 검사 저장소 최신화
cd ~/om-work/openmetadata-test && git pull --ff-only

# ③ 예행연습 실행
PYTHON=./.venv/bin/python harness/tools/upgrade_rehearsal.sh ~/om-work/OM_TEMP

# ④ 확인 — 여기가 하이라이트
git -C ~/om-work/upgrade-rehearsal/tree rev-parse HEAD^{tree}
```

마지막 줄에서 아래 값이 나오면 성공입니다.

```
e490ed82dd9cfe58833b2050a233aae7496541ab
```

## 기존 clone을 다시 사용할 수 있나

**사용할 수 있습니다.** 저장소를 다시 clone할 필요는 없습니다. 다만
지난 예행연습이 만든 임시 worktree와 branch가 남아 있으면 새 실행이 중단되므로,
0부 ①에서 예행연습 산출물만 정리합니다.

| 상황 | 실제 동작 |
|---|---|
| 정리하지 않고 그대로 재실행 | 0~3단계는 진행되며, 4단계에서 `... 이(가) 이미 있습니다`라는 메시지와 함께 중단됩니다. 기존 결과는 변경하지 않습니다 |
| 위 ① 정리 후 재실행 | 정상 완주하고 **같은 확인값**이 나옴 |
| 공식 소스를 이미 받아 둔 상태 | 다시 받아도 문제 없음. 두 번째부터는 훨씬 빠름 |
| 제품 저장소 원본 | 원격에 아무것도 올리지 않으므로 그대로 |
| 등록 폴더 | 예행연습이 건드리지 않음 |

이전 작업의 백업 폴더(예: `~/om-work-before-...`)가 있다면 **지우지 말고 그냥
두십시오.** 이번 실행과 무관합니다.

## 검사 저장소를 꼭 최신화해야 하나

**시연 전에는 최신화하십시오.** 스크립트뿐 아니라 기대 SHA, Manifest,
검사 정책과 문서가 함께 맞아야 하기 때문입니다. `git pull --ff-only`이
실패하면 로컬 변경을 임의로 지우지 말고 `git status` 결과를 확인한 뒤
저장소 담당자에게 문의하십시오.

---

# 1부 · 처음 하는 컴퓨터라면 (준비)

## 1. 프로그램 확인

```bash
git --version          # 2.43 이상
python3 --version      # 3.9 이상이면 됩니다
```

없으면 먼저 설치하십시오.

## 2. 저장소 두 개 내려받기

두 폴더를 나란히 두면 경로가 짧아집니다.

```bash
# 두 저장소를 나란히 둘 작업 폴더를 만들고 그리로 들어갑니다
mkdir -p ~/om-work && cd ~/om-work

git clone https://github.com/easyseop/openmetadata-test.git   # 검사 도구와 기준
git clone https://github.com/easyseop/OM_TEMP.git             # 검사받을 제품 코드
```

> 📸 **①** 두 개가 모두 내려받아진 터미널 화면

## 3. 검사 저장소를 작업 branch로

```bash
cd ~/om-work/openmetadata-test
git switch claude/markdown-file-feedback-26933w   # 이 시연에 쓰는 branch로 옮깁니다
git pull --ff-only                                # 최신 내용을 받아옵니다
```

## 4. 파이썬 준비물 설치

```bash
# 이 폴더 전용 파이썬 공간(.venv)을 만듭니다. 컴퓨터 전체 설정은 건드리지 않습니다
python3 -m venv .venv

# 검사 도구가 쓰는 준비물 세 개를 그 안에만 설치합니다
./.venv/bin/pip install "PyYAML>=6.0" "jsonschema>=4.18" "pathspec>=0.11"

# 셋 다 제대로 들어갔는지 불러와 봅니다
./.venv/bin/python -c "import yaml, jsonschema, pathspec; print('준비 완료')"
```

> 📸 **②** `준비 완료`가 찍힌 화면

## 5. 예행연습 기준 SHA 확인

```bash
cd ~/om-work/OM_TEMP

# 두 branch를 GitHub 에서 내 컴퓨터로 받아옵니다 (작업 중인 파일은 안 건드립니다)
git fetch origin patch/om-1.13.0 custom/om-1.13.0

# 받아온 두 branch가 지금 어느 commit을 가리키는지 SHA로 확인합니다
git rev-parse origin/patch/om-1.13.0 origin/custom/om-1.13.0
```

**아래 두 값이 나와야 합니다.**

```
2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50     ← 공식 1.13.0 기준 commit
7d19c8952612e77467b0a80d6287170d814f1de1     ← BANK-OM 커스터마이징 기준 commit
```

> 📸 **③** 위 두 Git commit SHA가 보이는 화면

![예행연습 기준 SHA](assets/업그레이드시연/T03b-출발점-두개-직접실행.png)

확대

> 실제로 이렇게 나옵니다. 맨 아래 두 줄이 위 기대값과 같습니다

### 두 명령이 하는 일이 다릅니다

| 명령 | 하는 일 |
|---|---|
| `git fetch` | GitHub 서버에서 branch **두 개를 내 컴퓨터로 받아옵니다.** 아직 아무것도 확인하지 않습니다 |
| `git rev-parse` | 받아온 두 branch가 **정확히 어느 commit을 가리키는지** Git commit SHA로 확인합니다 |

`fetch`는 받아만 오고 **작업 중인 파일은 건드리지 않습니다.** 그래서 바로
다음 6번의 결과가 여전히 비어 있게 나옵니다. 받아온 내용은 `origin/...`이라는
별도 이름에 보관되며, 그래서 명령에 `origin/`이 붙습니다.

### 왜 branch를 두 개나 받나

하나만으로는 공식 기준과 BANK-OM 커스터마이징의 변경 범위를 비교할 수 없기 때문입니다.

| branch | 내용 |
|---|---|
| `patch/om-1.13.0` | **공식 OpenMetadata 1.13.0 기준 코드.** BANK-OM 커스터마이징이 적용되기 전 상태 |
| `custom/om-1.13.0` | 공식 1.13.0 기준 코드에 **BANK-OM-001~007 커스터마이징을 적용한 상태** |

```text
공식 OpenMetadata 1.13.0
  = patch/om-1.13.0 (2f4f3560e7…)
        │
        ├─ BANK-OM-001 적용
        ├─ BANK-OM-002 적용
        │   ⋮  (commit 8건)
        └─ BANK-OM-007 후속 commit
              = custom/om-1.13.0 (7d19c89526…)

     custom (공식 코드 + BANK-OM 커스터마이징)
   −  patch (공식 기준 코드)
   ─────────────────────────
   =  커스터마이징으로 변경된 파일 111개
```

### 왜 Git commit SHA까지 확인하나

**branch 이름은 움직이기 때문입니다.** `custom/om-1.13.0`이라는 이름은 그대로여도,
누가 새 코드를 올리면 그 이름이 가리키는 **실제 코드가 바뀝니다.** 이름은
가리키는 대상이 바뀔 수 있고, 번호는 한 번 정해지면 바뀌지 않습니다.

이 시연의 모든 숫자 — `111`, `834`, `e490ed82dd…` — 는 **위 두 SHA를
기준으로 실행했을 때만** 유효합니다. 따라서 시작 전에 SHA를 확인하고 기록하여,
결과의 산출 기준을 추적할 수 있게 합니다.

> **값이 다르게 나오면 멈추십시오.** 원격 branch가 그 사이 움직였다는 뜻이고,
> 뒤따르는 숫자가 문서와 맞지 않게 됩니다. 캡처해서 문의해 주십시오.

이 확인은 **예행연습 스크립트도 0단계에서 똑같이 합니다.** 5번을 건너뛰어도
스크립트가 잡아내며, 다르면 이렇게 멈춥니다.

```
중단: 1.13.0 공식 기준 branch 이(가) 기대와 다릅니다. 실제=... 기대=2f4f3560e7...
```

5번을 따로 둔 것은 **캡처 때문**입니다. 스크립트 출력보다 이 화면이 발표에
쓰기 깔끔합니다.

## 6. 작업 폴더가 깨끗한지

```bash
# 아직 기록하지 않은 변경을 한 줄씩 보여줍니다 (--porcelain 은 짧게 출력하라는 뜻)
git status --porcelain
```

**아무것도 안 나와야 합니다.**

### 왜 이걸 보나

`git status --porcelain`은 **아직 기록하지 않은 변경**을 한 줄씩 보여줍니다.
아무 줄도 안 나온다는 것은 **현재 checkout 상태에 커밋하지 않은 변경이 없다는 뜻**입니다.
현재 branch의 SHA가 5번의 기준 SHA와 같은지는 5번의 `git rev-parse` 결과로 별도 확인합니다.

여기서 뭔가 나온다면 두 가지 중 하나입니다.

| 나오는 것 | 뜻 |
|---|---|
| `M 파일이름` | 누군가 그 파일을 고쳐 놓고 기록하지 않았음 |
| `?? 파일이름` | 원래 없던 파일이 들어와 있음 |

어느 쪽이든 **현재 checkout 상태에 커밋하지 않은 변경이 있다**는 뜻입니다.
그 상태로 진행하면 기준 commit 밖의 변경이 결과에 섞일 수 있으므로,
변경의 출처와 처리 방법을 확인한 뒤 다시 실행해야 합니다.

그래서 예행연습 스크립트도 0단계에서 같은 검사를 하고, 비어 있지 않으면
아예 시작하지 않습니다.

```
중단: 제품 저장소에 커밋하지 않은 변경이 있습니다. 정리 후 다시 실행하십시오
```

무엇이 남아 있는지 보려면 `--porcelain`을 빼고 실행하면 자세히 나옵니다.

```bash
git status
```

---

# 2부 · GitHub 화면 캡처

브라우저에서 찍습니다. **창을 1400px 이상으로 넓혀 주십시오.** 좁으면
GitHub이 화면 요소를 감춥니다. 숫자가 보이는 윗부분만 있으면 되고,
파일 목록까지 내려가지 않으셔도 됩니다.

## G1. branch 두 개가 실제로 있다

```
github.com/easyseop/OM_TEMP/branches
```

`patch/om-1.13.0`과 `custom/om-1.13.0`이 목록에 보이면 됩니다.

`custom/om-1.13.0` 줄의 **`Ahead 8`**도 함께 나오면 좋습니다. 공식 기준 이후에
BANK-OM 커스터마이징 commit 8건이 추가됐음을 GitHub이 계산한 값입니다.

> 📸 **G1**

![브랜치 목록](assets/업그레이드시연/G01-브랜치-목록.png)

확대

> 실제로 이렇게 나옵니다. `patch/om-1.13.0`가 Default, `custom/om-1.13.0`가 Ahead 8

## G2. 우리가 변경한 파일이 111개다 ★

```
github.com/easyseop/OM_TEMP/compare/patch/om-1.13.0...custom/om-1.13.0
```

화면 위쪽 **`8 commits`** 와 **`111 files changed`** 가 핵심입니다.

> 📸 **G2** — 발표에서 "이 숫자는 GitHub이 세어준 것"이라고 말할 수 있는 근거

![두 branch 비교 111개](assets/업그레이드시연/G02-두브랜치-비교-111.png)

확대

> 실제로 이렇게 나옵니다. `8 commits` · `111 files changed` · `1 contributor`
>
> ⚠️ **오른쪽 초록색 `Create pull request` 버튼을 누르지 마십시오.**
> 두 branch를 합치자는 요청이 저장소에 실제로 만들어집니다. 우리는 보기만
> 하는 중입니다. 실수로 누르셨으면 만들어진 페이지에서 `Close pull request`
> 로 닫으면 되고, 그것만으로 코드가 바뀌지는 않습니다.

### 왼쪽·오른쪽 방향이 맞는지

```
base: patch/om-1.13.0        ← 기준점 (공식 코드만)
compare: custom/om-1.13.0    ← 비교 대상 (공식 + BANK-OM 커스터마이징)
```

GitHub은 **기준점에는 없고 비교 대상에만 있는 것**을 보여줍니다. 그래서 이
방향이면 결과가 곧 **우리가 더한 것**입니다. 뒤집으면 같은 111개가 나오지만
"빼는 것"으로 표시돼 읽기 어렵습니다.

### 아래 기록 목록도 같이 보십시오

5번에서 터미널로 확인한 것과 같은 기록입니다. GitHub은 7자리, 예행연습
스크립트는 10자리로 보여줄 뿐 같은 것입니다.

| GitHub 화면 | 5번 터미널 |
|---|---|
| `add InstanceCode customization` · `4df83b3` | `4df83b311f` |
| `add QueryReport customization` · `68ebed4` | `68ebed4801` |
| `add Data Assertions customization` · `57ee1b3` | `57ee1b3b23` |
| `add bank column view customization` · `274f2b7` | `274f2b79b4` |

주소가 열리지 않으면 branch 이름의 `/` 때문일 수 있습니다. 그때는
저장소에서 **Compare** 버튼을 누르고 드롭다운으로 왼쪽 `patch/om-1.13.0`,
오른쪽 `custom/om-1.13.0`을 고르십시오. 결과는 같습니다.

## G3. BANK-OM 커스터마이징 commit 8건

```
github.com/easyseop/OM_TEMP/commits/custom/om-1.13.0
```

> 📸 **G3** — 목록 전체. **맨 아래 줄까지 나오게** 찍으십시오.

![commit 8건](assets/업그레이드시연/G03-변경기록-8건.png)

확대

> 실제로 이렇게 나옵니다. 맨 아래 `Import official OpenMetadata 1.13.0 source snapshot`이 출발점이고 그 위에 8건이 쌓여 있습니다

### 맨 아래 줄이 출발점입니다

목록 맨 아래에 `Import official OpenMetadata 1.13.0 source snapshot` ·
`2f4f356`이 있습니다. 이것이 5번에서 확인한 `2f4f3560e7…`, 곧 **공식 코드만
있는 출발점**입니다. 그 이후에 BANK-OM 커스터마이징 commit 8건이 이어집니다.

```text
7d19c89  complete Tibero service connection coverage   ← 맨 위 = custom/om-1.13.0
62e39da  add Tibero customization
010750c  add Sybase customization
d983f7c  fix Korean IME handling                         BANK-OM commit 8건
274f2b7  add bank column view customization
57ee1b3  add Data Assertions customization
68ebed4  add QueryReport customization
4df83b3  add InstanceCode customization
─────────────────────────────────────────
2f4f356  Import official OpenMetadata 1.13.0 snapshot  ← 맨 아래 = 출발점(공식)
```

5번에서 터미널로 확인한 구조가 **이 화면 하나에 그대로 나옵니다.** 발표에서
"공식 기준 이후에 BANK-OM 커스터마이징 commit이 추가됐다"고 설명할 때 사용할 수 있습니다.

## G3b. Customization-ID가 붙은 실제 화면 ★

commit 목록에서 아래 두 commit의 상세 화면을 각각 엽니다. 파일 수가 큰
BANK-OM-001과 파일 한 개를 변경한 BANK-OM-005를 비교합니다.

```
github.com/easyseop/OM_TEMP/commit/4df83b3     ← 큰 기능
github.com/easyseop/OM_TEMP/commit/d983f7c     ← 작은 기능
```

**보여야 할 것:** 제목 아래의 `Customization-ID:` 줄과 `N files changed`

> 📸 **G3b-1**, **G3b-2**

![Customization-ID BANK-OM-001](assets/업그레이드시연/G03b-1-이름표-BANK-OM-001.png)

확대

> 큰 기능 — `Customization-ID: BANK-OM-001`, `48 files changed`

![Customization-ID BANK-OM-005](assets/업그레이드시연/G03b-2-이름표-BANK-OM-005.png)

확대

> 작은 기능 — `Customization-ID: BANK-OM-005`, `1 file changed`

### 왜 이게 중요한가

```
add InstanceCode customization
Customization-ID: BANK-OM-001      ← 이 한 줄
```

`Customization-ID` trailer는 이 commit을 어느 BANK-OM 기능과
연결할지 명시합니다. 검사기는 공식 기준 이후의 각 commit에서 이 trailer를
정확히 하나 읽어 Manifest와 대조합니다. 없거나 여러 개면 commit 소유 기능을
하나로 정할 수 없으므로 BLOCK으로 중단합니다.

### 크기가 다른 둘을 고르는 이유

| commit | 기능 | 바꾼 파일 |
|---|---|---|
| `4df83b3` | BANK-OM-001 기준코드 | **48개** |
| `d983f7c` | BANK-OM-005 한글 입력 | **1개** |

두 기능은 변경 파일 수가 크게 다르지만, 관리 규칙은 같습니다. commit마다
Customization-ID를 하나 기록하고, 해당 ID의 Manifest가 변경 범위를 관리합니다.

참고로 8건 전체의 파일 수는 다음과 같습니다.

```text
BANK-OM-001  48개    BANK-OM-005   1개
BANK-OM-002  55개    BANK-OM-006  18개
BANK-OM-003  25개    BANK-OM-007   8개
BANK-OM-004  33개    BANK-OM-007   2개 (후속)
```

`4df83b3` 화면의 `1 parent 2f4f356`도 함께 나오면 좋습니다. 첫 BANK-OM commit의
직접 부모가 공식 1.13.0 기준 commit임을 확인할 수 있습니다.

## G4. 공식 OpenMetadata 1.13.1 release 확인

```
github.com/open-metadata/OpenMetadata/releases/tag/1.13.1-release
```

**보여야 할 것:** 제목 `1.13.1-release`와 그 아래 줄의 **`afcb2d2`**

> 📸 **G4**

![공식 1.13.1 릴리스](assets/업그레이드시연/G04-공식-1.13.1-릴리스.png)

확대

> 실제로 이렇게 나옵니다. 제목 옆 `afcb2d2`가 터미널이 대조하는 번호입니다

`afcb2d2`는 3부 구간 2에서 확인하는
`afcb2d2cd7e7c28f1d0ce…`와 같은 Git commit SHA입니다. 이 화면은
예행연습이 공식 1.13.1 release commit을 입력으로 사용했음을 보여줍니다.
release 공개는 행내 운영 배포와 다른 상태입니다.

> **새 버전 공개를 자동으로 탐지하거나 업그레이드 대상을 자동 결정하지는 않습니다.**
> 담당자가 대상 버전을 지정하면, 그다음부터 공식 소스 수신·Git commit SHA 대조·
> BANK-OM 영향 계산을 자동으로 수행합니다. 발표 중 "새 버전이 나오면 자동으로
> 알려주나요?"라는 질문에는 이 범위를 구분해 답하십시오.

## G5. 공식이 바꾼 파일이 834개다 ★

```
github.com/open-metadata/OpenMetadata/compare/1.13.0-release...1.13.1-release
```

화면 위쪽 탭에 있는 **`Files changed 834`** 가 핵심입니다. 그 왼쪽의
`Commits 168`은 공식이 두 버전 사이에 쌓은 commit 수입니다 — 우리 쪽
8건과 대비됩니다.

> 📸 **G5** — G2의 111과 나란히 놓고 "축이 다른 두 숫자"를 설명하는 데 씁니다

![공식 두 버전 비교 834개](assets/업그레이드시연/G05-공식-두버전-비교-834.png)

확대

> 실제로 이렇게 나옵니다. `Commits 168` · `Files changed 834`

## G6. BANK-OM별 검사 기준은 어디에 있는가

> G1~G5는 제품 소스와 공식 소스의 Git 사실을 확인했습니다. Git만으로는
> 어떤 파일이 기능 유지에 필수인지 결정할 수 없습니다. 이 프로젝트는 사람이
> 검토한 기능별 범위를 `easyseop/openmetadata-test`의 Manifest에 기록하고,
> 검사기가 그 Manifest와 실제 코드를 비교합니다.

```
github.com/easyseop/openmetadata-test/blob/claude/markdown-file-feedback-26933w/harness/registrations/om-temp-1.13.0/manifests/BANK-OM-001.yaml#L56-L58
```

주소 끝의 `#L56-L58`을 **빠뜨리지 마십시오.** 이걸 붙여야 115줄짜리 파일에서
필요한 부분만 노랗게 강조된 채 열립니다.

> ⚠️ **`Raw` 버튼을 누르지 마십시오.** 누르면 GitHub 화면 없이 원문 글씨만
> 나와서 발표에 쓸 수 없습니다. 주소를 그대로 열면 됩니다.

**보여야 할 것:** `changed_paths` 목록의 끝부분과, 강조된
`required_changed_paths` 두 줄

> 📸 **G6** — 115줄이라 위·중간·아래 세 장으로 나눠 찍습니다.

![Manifest 위쪽](assets/업그레이드시연/G06-1-등록표-위.png)

확대

> 1~26줄. 머리말 6줄과 `changed_paths` 시작

![Manifest 필수 경로](assets/업그레이드시연/G06-2-등록표-필수경로.png)

확대

> 56~58줄이 노랗게 강조된 부분. G6 세 장 중 이 화면이 가장 중요합니다

![Manifest 아래쪽](assets/업그레이드시연/G06-3-등록표-아래.png)

확대

> 88~115줄. `upgrade_watch` 끝과 `assurance`·`series`

### 이 파일 한 장의 구조

`BANK-OM-001.yaml`은 115줄이고, 크게 **네 구역**으로 나뉩니다.

| 줄 | 구역 | 뜻 | 개수 |
|---|---|---|---|
| 1~6 | 머리말 | 번호·제목·종류 | — |
| 7~55 | `changed_paths` | **이 기능이 변경한 파일 전부** | 48개 |
| 56~58 | `required_changed_paths` | 그중 **없어지면 안 되는 것** | 2개 |
| 59~108 | `upgrade_watch.paths` | **공식이 바꾸면 확인해야 할 것** | 48개 |
| 109~115 | 꼬리말 | 정상 판정 조건, 연결 관계 | — |

세 번째 구역이 3부 구간 3에서 본 `48개 중 22개` 같은 숫자의 출처입니다.

### 변경 경로 48개의 구성

`changed_paths` 48개는 성격이 두 가지로 나뉩니다. **공식 1.13.0에 그 파일이
원래 있었는지**로 갈라집니다.

```text
BANK-OM-001 기준코드(InstanceCode) 기능 · 48개

  ┌─ 원래 있던 공식 파일을 고친 것 ······ 32개
  │     ├─ 번역 문구 파일 ················ 19개
  │     └─ 그 외 ························ 13개
  │           Entity.java, CollectionDAO.java,
  │           constants.ts, RouterUtils.ts …
  │
  └─ 원래 없던 파일을 새로 만든 것 ······· 16개
        InstanceCodeResource.java,
        InstanceCodeRepository.java,
        instanceCode.json,
        InstanceCodeListPage.tsx …
```

이 사례에서 `InstanceCode…`이름의 파일은 BANK-OM-001이 새로 추가한 경로입니다.
신규 여부는 파일 이름만으로 일반화하지 않고, 공식 1.13.0 tree에 같은 경로가
있는지를 기준으로 계산합니다.

새 기능 하나를 넣으려면 **새 파일을 만드는 것만으로는 안 됩니다.** 만든 것을
기존 프로그램이 알아보게 해 줘야 합니다.

| 고친 기존 파일 | 왜 고쳐야 했나 |
|---|---|
| `Entity.java` | 프로그램에 "기준코드라는 종류가 있다"고 등록 |
| `CollectionDAO.java` | 데이터베이스에서 읽고 쓰는 통로를 연결 |
| `RouterUtils.ts` · `AuthenticatedAppRouter.tsx` | 화면 주소를 새 페이지에 연결 |
| `constants.ts` · `entity.enum.ts` | 이름·상수 목록에 항목 추가 |
| `schemaChanges.sql` | 데이터베이스에 표를 새로 만드는 명령 추가 |
| `ko-kr.json` 등 번역 19개 | 화면에 나올 문구를 언어별로 추가 |

이 commit은 같은 화면 문구를 19개 locale 파일에 추가했습니다. 따라서
기능 하나의 변경이 여러 언어 파일에 반복해서 나타납니다.

### `required_changed_paths`는 신규 파일 목록이 아닙니다

BANK-OM-001만 보면 그렇게 보입니다. 강조된 두 줄이 마침 둘 다 새로 만든
파일이기 때문입니다.

```yaml
required_changed_paths:
- …/instancecode/InstanceCodeResource.java     ← 새로 만든 파일
- …/json/schema/entity/data/instanceCode.json  ← 새로 만든 파일
```

**그러나 규칙이 아닙니다.** 다른 기능을 보면 반대입니다.

| 기능 | 변경한 파일 | 새로 만든 것 | `required` 로 지목한 것 |
|---|---|---|---|
| BANK-OM-001 기준코드 | 48개 | 16개 | 새로 만든 파일 2개 |
| BANK-OM-002 조회리포트 | 55개 | 18개 | 새로 만든 파일 2개 |
| BANK-OM-003 데이터점검 | 25개 | 3개 | 새로 만든 파일 2개 |
| **BANK-OM-004 컬럼보기** | 33개 | **0개** | **기존 공식 파일 1개** |
| **BANK-OM-005 한글입력** | 1개 | **0개** | **기존 공식 파일 1개** |
| BANK-OM-006 Sybase 연결 | 18개 | 3개 | 새로 만든 파일 1개 |
| BANK-OM-007 Tibero 연결 | 10개 | 3개 | 새로 만든 파일 1개 |

BANK-OM-004와 005는 **새로 만든 파일이 하나도 없습니다.** 원래 있던 공식
코드만 고친 기능입니다. 그래도 "없어지면 안 되는 것"은 있어야 하니, 기존
파일을 지목해 뒀습니다.

두 항목의 실제 차이는 이렇습니다.

|  | `changed_paths` | `required_changed_paths` |
|---|---|---|
| 누가 정하나 | **자동화 도구** — Git commit diff에서 계산 | **사람** — 담당자가 판단해 지목 |
| 무엇이 들어가나 | 변경한 파일 **전부** | 그중 골라낸 **일부** |
| 신규/기존 | 섞여 있음 | 섞여 있음 (기능마다 다름) |

따라서 준비 도구의 `plan`은
`required_changed_paths`를 임의로 정하지 않습니다. 파일 누락만으로
기능 미적용을 확정할 수 있는지는 업무·기술 담당자가 판단해야 합니다.

### 두 목록을 구분하는 이유 — 판정이 다릅니다

업그레이드 뒤 검사기는 **두 목록에 똑같은 검사 두 가지**를 합니다.

| 검사 | 묻는 것 |
|---|---|
| 파일이 있는가 | 새 코드에 그 파일이 남아 있나 |
| 공식과 내용이 다른가 | 우리가 넣은 변경이 아직 살아 있나 |

두 번째가 중요합니다. **파일이 남아 있어도 내용이 공식과 똑같아졌다면
우리 변경은 사라진 것**이기 때문입니다. 업그레이드하면서 공식 코드로
덮여 버린 경우가 여기 해당합니다.

같은 검사인데, **어느 목록에 있느냐에 따라 결과가 갈립니다.**

| 발견한 것 | `changed_paths`에만 있는 파일 | `required_changed_paths`에 있는 파일 |
|---|---|---|
| 파일이 사라짐 | `expected_path_missing`<br>**확인 필요** (종료코드 2) | `required_path_missing`<br>**중단** (종료코드 1) |
| 내용이 공식과 같아짐 | `expected_state_not_distinct`<br>**확인 필요** (종료코드 2) | `required_state_not_distinct`<br>**중단** (종료코드 1) |

- **확인 필요** — 사람이 보고 "괜찮다" 하면 넘어갑니다.
- **중단** — 사람이 승인해도 이 단계에서는 통과시킬 수 없습니다.

### 공식 버전 변경에서 경로 삭제·이동도 발생합니다

**일어납니다.** 공식이 1.13.0 → 1.13.1 로 가면서 한 일을 세어 보면 이렇습니다.

|  | 파일 수 |
|---|---|
| 새로 추가 | 137개 |
| 내용 수정 | 694개 |
| **삭제** | **2개** |
| **이름 변경** | **1개** |

공식 버전 변경에는 파일 추가·수정뿐 아니라 삭제와 이름 변경도 포함될 수
있습니다. 따라서 이전 버전의 경로가 다음 버전에 그대로 남는다고 가정할 수
없습니다.

다만 **이번에는 BANK-OM 변경 범위와 겹치지 않았습니다.** OpenMetadata가 없앤 3개는 BANK-OM이 변경한
111개에 하나도 포함되지 않습니다. 그래서 3부 실행에서 이 경고가 나오지
않았습니다. 다음 버전에서도 그러리라는 보장은 없습니다.

없어지는 경로는 파일 성격에 따라 다릅니다.

| 어떤 파일 | 없어지는 경우 |
|---|---|
| 공식 파일을 고친 것 (68개) | **공식이 그 파일을 지우거나 옮김.** 우리가 고칠 대상 자체가 사라진 것 |
| 우리가 새로 만든 것 (43개) | 재적용 뒤 사라졌다면 BANK-OM 변경이 빠졌을 가능성이 큼. 다만 공식 새 버전이 같은 경로를 새로 만들 수도 있으므로 내용과 이력을 함께 확인 |

### 경로 누락과 내용 소실의 판정

**심각도는 같고, 표시되는 이름이 다릅니다.**

| 상황 | 표시 | 판정 |
|---|---|---|
| 파일이 아예 없다 | `…_path_missing` | 목록에 따라 확인 필요 / 중단 |
| 파일은 있는데 공식과 내용이 같다 | `…_state_not_distinct` | 〃 |

둘 다 결론은 하나입니다 — **새 코드에 우리 변경이 없다.** 그래서 판정을
다르게 둘 이유가 없습니다.

이름을 나눈 것은 **어디를 봐야 하는지가 다르기 때문**입니다.

- `path_missing` → 공식 저장소에서 그 파일이 어디로 갔는지 찾습니다
- `state_not_distinct` → 우리 변경이 왜 덮였는지 그 파일 안을 봅니다

한 파일에 두 이름이 동시에 나오지는 않습니다. 파일이 없으면 내용을 비교할
수 없으니, **먼저 있는지 보고 있을 때만 내용을 비교합니다.**

### 전체 변경 범위와 필수 범위를 함께 관리하는 이유

**둘 중 하나만 두면 안 되기 때문입니다.**

`required` 만 두면 — BANK-OM-001에서 검사받는 파일이 48개가 아니라 **2개**가
됩니다. 나머지 46개는 통째로 사라져도 검사에 걸리지 않습니다.

`changed_paths` 만 두고 전부 중단 기준으로 삼으면 — **업그레이드를 거의
통과시킬 수 없습니다.** BANK-OM-001의 48개 중 19개가 번역 문구 파일인데, 공식이
같은 자리에 비슷한 문구를 넣기만 해도 "내용이 같아졌다"로 멈춥니다. 기능은
정상인데도 그렇습니다.

그래서 **전부 보되, 멈추는 것은 핵심만**으로 나눴습니다.

```text
changed_paths 48개  ← 하나도 놓치지 않고 전부 본다
    └─ required 2개  ← 이 둘만 사라지면 즉시 멈춘다
```

BANK-OM-001로 예를 들면 이렇습니다.

| 파일 | 어디 속하나 | 사라지면 |
|---|---|---|
| `ko-kr.json` (한글 문구) | `changed_paths` 만 | 확인 필요 — 문구는 다시 넣으면 됨 |
| `constants.ts` (상수 추가) | `changed_paths` 만 | 확인 필요 |
| `InstanceCodeResource.java` | **`required`** | **중단** — 기준코드 기능의 입구 |
| `instanceCode.json` | **`required`** | **중단** — 기준코드의 정의 자체 |

담당자가 고른 두 파일은 누락만으로 BANK-OM-001 미적용을 확정할 수 있는
핵심 구현입니다. 나머지 46개가 중요하지 않다는 뜻은 아닙니다. 누락 시
APPROVAL로 담당자 검토를 요구하지만, 누락만으로 자동 BLOCK을 확정하지 않는
범위입니다.

> 이 동작은 시험으로 고정돼 있습니다 —
> `harness/tests/test_survival.py`의
> `test_required_path_missing_blocks`,
> `test_required_path_identical_to_upstream_blocks`,
> `test_non_required_expected_path_missing_requires_approval`,
> `test_non_required_expected_path_absorbed_by_upstream_requires_approval`.

### 새 Manifest에도 필수 경로가 필요합니다

**아닙니다. 비워 둘 수 없습니다.** 새 기능에 번호를 발급할 때 사람이 반드시
적어 넣어야 하는 항목입니다.

새 BANK-OM 번호를 만들려면 `plan`에 **입력 파일을 하나 더** 줍니다.

```bash
… plan … --new-id-input ~/om-work/new-id.yaml
```

그 파일에 아래 여덟 항목이 **모두** 있어야 합니다. 하나라도 빠지면
`INVALID_NEW_CUSTOMIZATION` 으로 막힙니다.

```yaml
BANK-OM-008:
  title: 예금 상품 코드                 # 기능 이름
  owner: 데이터관리부 홍길동             # 담당자
  owner_status: assigned              # assigned | pending
  criticality: high                   # low | medium | high | critical
  kind: core-patch                    # core-patch | extension | governance
  provenance: candidate-follow-up
  required_changed_paths:             # ★ 없어지면 안 되는 파일
  - openmetadata-spec/…/depositCode.json
  contracts:                          # 정상이라고 판단할 조건
  - CONTRACT-DEPOSIT-CODE
```

> `contracts`에 적는 이름은 **`contracts.yaml`에 이미 등록돼 있어야 하고**,
> 그쪽에도 이 번호가 적혀 있어야 합니다. 한쪽만 적으면
> `lacks reverse binding` 으로 막힙니다. 양쪽이 서로를 가리켜야 "이 기능은
> 이 조건으로 판정한다"가 성립하기 때문입니다.

자동화 도구가 채우는 것과 사람이 채우는 것이 정확히 갈립니다.

| 항목 | 누가 | 근거 |
|---|---|---|
| `changed_paths` | **자동화 도구** | Git commit diff에서 계산 |
| `upgrade_watch.paths` | **자동화 도구 + 담당자 검토** | 공식 기준에도 있는 변경 경로는 자동 포함하고, 의존 경로는 제안·승인으로 추가 |
| `required_changed_paths` | **사람** | 코드에 없는 판단 |
| `title` · `owner` · `criticality` | **사람** | 〃 |
| `contracts` | **사람** | 〃 |

`kind: core-patch` 인 기능은 `required_changed_paths`가 **빈 목록이어도
안 됩니다.** 최소 한 개는 지목해야 Manifest 자체가 읽히지 않고 오류로 멈춥니다.

```
core-patch must declare at least one required_changed_paths entry
```

지금 등록된 7개는 **전부 `core-patch`** 이고, 그래서 전부 1개 이상을
가지고 있습니다.

적어 넣는 경로는 **`changed_paths` 안에 있어야** 합니다. 해당 기능의 변경 범위에
없는 파일을 필수 경로로 지정할 수는 없기 때문입니다. 범위를 벗어나면
이렇게 막힙니다.

```
required path not covered by current changed scope: '…'
```

### 기존 기능에 변경 경로가 추가돼도 다시 검토합니다

번호를 새로 만들 때만이 아닙니다. 기존 기능이 **전에 없던 파일을 건드리면**
`plan`이 그 파일 하나하나에 대해 다시 묻습니다.

```
REQUIRED_PATH_DECISION
새 변경 파일이 빠질 때 기능이 소실되는지 판단하고
required_changed_paths 추가 여부를 확인해야 합니다.
```

**정리하면 — `required`는 처음에도 사람이 정하고, 파일이 늘어날 때마다
다시 사람에게 묻습니다.** 자동화 도구가 이 값을 스스로 채우는 경로는 없습니다.

### Manifest 7장을 합치면 G2의 111이 됩니다

|  | 값 |
|---|---|
| Manifest 7장의 `changed_paths` 수를 단순 합산하면 | 190개 |
| 여러 기능이 함께 변경한 파일의 중복을 제거하면 | **111개** |
| G2의 GitHub 비교 화면 | **111 files changed** |

**정확히 맞습니다.** Manifest에 적힌 파일 목록과 GitHub이 직접 센 파일 목록이
한 개도 어긋나지 않습니다. 이것이 "Manifest가 실제 코드와 맞다"는 뜻입니다.

190과 111의 차이 79개는 **여러 기능이 같은 파일을 함께 만졌기** 때문입니다.
예를 들어 번역 파일 `ko-kr.json` 하나에 네 기능이 각자 문구를 넣었습니다.

중복을 제거한 111개를 다시 갈라 보면 이렇게 됩니다.

```text
BANK-OM 커스터마이징이 변경한 파일 111개
  ├─ 원래 있던 공식 파일을 고친 것 ······ 68개
  └─ 원래 없던 파일을 새로 만든 것 ······ 43개
```

발표에서는 이렇게 말씀하시면 됩니다 —

> "OM_TEMP 1.13.0에서 BANK-OM 커스터마이징이 변경한 경로는 111개입니다.
> 그중 68개는 기존 공식 파일을 수정했고 43개는 당시 공식 1.13.0에 없던
> 경로입니다. 실제 충돌 여부는 공식 1.13.1 변경과 재적용 결과를 비교해
> 판단합니다."

이 68개는 충돌 가능성을 우선 검토할 기존 공식 파일 범위입니다. 실제
재적용에서는 이 가운데 locale JSON 18개가 Git 충돌로 중단됐습니다.

---

# 3부 · 예행연습 실행

## 무엇을 예행연습하는 것인가

**이 예행연습은 다음 코드 상태를 가정합니다.**

> OM_TEMP의 `custom/om-1.13.0`에는 공식 OpenMetadata 1.13.0과
> BANK-OM-001~007 커스터마이징 commit 8건이 있습니다. 이 변경을 공식
> OpenMetadata 1.13.1 소스에 commit별로 재적용해 충돌을 진단합니다.

스크립트는 공식 1.13.1을 받은 뒤 BANK-OM commit 8건을 순서대로
`cherry-pick`하여 진단용 후보 코드를 만듭니다. 이 방식은 기능별 충돌을
분리해 설명하기 위한 이번 예행연습 방식입니다. 목표 운영 전략인
`vendor-merge`를 실제로 수행했다는 증거는 아니며, 실제
`vendor-merge` 후보 생성과 검사는 아직 **NOT VERIFIED**입니다.

```text
     공식 1.13.0 ──── BANK-OM commit 8건 ────► OM_TEMP 1.13.0 연습 코드
          │
          │  공식이 834개 파일을 바꿈
          ▼
     공식 1.13.1 ──── BANK-OM commit 8건 ────► 진단용 후보 코드
                       (commit별 재적용)
```

## 무엇을 확인하려는 것인가

네 가지입니다.

|  | 확인하는 것 | 어디서 나오나 |
|---|---|---|
| 1 | 공식이 바꾼 834개가 **BANK-OM 업그레이드 감시 경로와 어디서 겹치는가** | 구간 3 |
| 2 | BANK-OM commit 8건이 공식 1.13.1에 **순서대로 재적용되는가** | 구간 5 |
| 3 | 재적용 중 발생한 충돌을 **자동으로 안전하게 해결할 수 있는가** | 구간 5 |
| 4 | 다른 환경에서도 **같은 tree SHA의 후보 코드가 만들어지는가** | 4부 |

이 시연의 결론은 commit별 재적용으로 같은 파일 상태를 재현할 수 있다는
것입니다. 이 결론을 build 성공, 실제 기능 정상, vendor-merge 검증 또는 배포
승인으로 확대해서 설명하지 않습니다.

## 무엇은 확인하지 않는가

**여기서 확인하는 것은 "코드를 읽어서 알 수 있는 것"까지입니다.**

| 확인하지 않는 것 | 언제 하나 |
|---|---|
| 프로그램이 빌드되는가 | 별도 단계 |
| 화면이 뜨고 기능이 실제로 도는가 | 별도 단계 |
| Manifest를 새 후보 코드 기준으로 승인·반영하는 것 | 6부에서 절차만 설명하며 실제 승인·apply는 수행하지 않음 |

## 무엇을 건드리지 않는가

실행 전에 범위를 밝혀 둡니다.

|  |  |
|---|---|
| 원격 저장소 (GitHub) | **아무것도 올리지 않습니다** |
| 등록 폴더 | 건드리지 않습니다 |
| OM_TEMP 의 기존 branch | 바꾸지 않습니다 |
| 만들어지는 곳 | `~/om-work/upgrade-rehearsal/` 새 폴더 안에만 |

되돌리려면 그 폴더를 지우면 됩니다. 0부 ① 의 세 줄이 그 명령입니다.

## 실행

**반드시 `openmetadata-test` 폴더에서** 실행합니다.

```bash
# ① 검사 도구가 있는 저장소로 이동합니다.
#    검사 대상(OM_TEMP)이 아니라 검사 도구 쪽에서 명령을 칩니다.
cd ~/om-work/openmetadata-test

# ② 예행연습을 실행합니다. 아래 한 줄이 세 부분으로 되어 있습니다.
#
#    PYTHON=./.venv/bin/python
#        1부 4번에서 만든 전용 파이썬을 쓰라는 뜻입니다.
#        컴퓨터에 원래 깔린 파이썬에는 필요한 준비물이 없어서 지정해 줍니다.
#
#    harness/tools/upgrade_rehearsal.sh
#        예행연습 스크립트. 검사 저장소 안에 들어 있습니다.
#
#    ~/om-work/OM_TEMP
#        검사할 제품 코드가 있는 폴더. 읽기만 하고 바꾸지 않습니다.
PYTHON=./.venv/bin/python harness/tools/upgrade_rehearsal.sh ~/om-work/OM_TEMP
```

화면이 6개 구간으로 이어집니다. 구간마다 캡처하십시오. 중간에 멈추면
맨 아래 **막혔을 때** 표를 보시면 됩니다.

## 구간 0 — 사전 점검

```
  OK  제품 저장소가 깨끗합니다
  OK  1.13.0 제품 원본 branch = 2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50
  OK  1.13.0 행내 branch = 7d19c8952612e77467b0a80d6287170d814f1de1
  OK  두 branch 사이 변경 파일 수 = 111
```

> 📸 **④**

![사전 점검](assets/업그레이드시연/T04-사전점검.png)

확대

> 실제로 이렇게 나옵니다 (2026-08-03 실행)

## 구간 1 — 기능별 commit과 Customization-ID

```
4df83b311f | BANK-OM-001 | add InstanceCode customization
68ebed4801 | BANK-OM-002 | add QueryReport customization
57ee1b3b23 | BANK-OM-003 | add Data Assertions customization
274f2b79b4 | BANK-OM-004 | add bank column view customization
d983f7c540 | BANK-OM-005 | fix Korean IME handling
010750c514 | BANK-OM-006 | add Sybase customization
62e39da8be | BANK-OM-007 | add Tibero customization
7d19c89526 | BANK-OM-007 | complete Tibero service connection coverage
  OK  commit 8건 모두 Customization-ID가 정확히 하나입니다
```

> 📸 **⑤**

![Customization-ID 8건](assets/업그레이드시연/T05-이름표-8건.png)

확대

> 실제로 이렇게 나옵니다 (2026-08-03 실행)

## 구간 2 — 공식 OpenMetadata 소스 받기

```
  OK  OpenMetadata 1.13.0 Git commit SHA = f329dd4a7e47134a2bd5a06af6181b0ee527ddd9
  OK  OpenMetadata 1.13.1 Git commit SHA = afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9
```

> 📸 **⑥**

![공식 OpenMetadata 소스 받기](assets/업그레이드시연/T06-공식버전-받기.png)

확대

> 실제로 이렇게 나옵니다 (2026-08-03 실행)

## 구간 3 — 적용 전 영향 확인 ★

**이 구간이 이 시연에서 가장 설명이 필요한 부분입니다.** 화면에 JSON이
길게 출력되므로 읽는 순서를 먼저 정리합니다.

> 📸 **⑦** — 화면이 길어서 위·아래 두 장으로 나눠 찍습니다. 아래 설명마다
> 해당 부분을 다시 붙여 두었으니 **보면서 읽으시면 됩니다.**
>
> 화면의 `공식`·`upstream`·`OFFICIAL_1_13_0`은 모두 같은 것을 가리킵니다 —
> **BANK-OM 커스터마이징이 적용되지 않은 공식 OpenMetadata 소스**입니다. 나머지 용어는 문서
> 맨 앞 **「이 문서에서 쓰는 말」** 표에 있습니다.

### 한 줄로 말하면

> **OpenMetadata가 1.13.0 → 1.13.1로 가면서 바꾼 834개 중, 우리가 감시
> 목록에 적어 둔 파일이 몇 개나 걸렸는지 세어 주는 것**입니다.

### 숫자가 어디서 나온 것인지부터

화면에는 숫자가 여러 개 나오는데 **출처가 다릅니다.** 이걸 구분하지 않으면
헷갈립니다.

| 숫자 | 무엇을 센 것 | 누가 센 것 | 미리 확인해 둔 값 |
|---|---|---|---|
| **834** | OpenMetadata 1.13.0 → 1.13.1 사이 파일 차이 | 검사기 | **G5** 화면 `Files changed 834` — 같음 ✓ |
| **111** (구간 0) | 우리가 변경한 파일 수 | 검사기 | **G2** 화면 `111 files changed` — 같음 ✓ |
| **8** (구간 1) | 우리 commit 수 | 검사기 | **G2** `8 commits`, **G3** 목록 — 같음 ✓ |
| **48** (분모) | BANK-OM-001 업그레이드 감시 경로의 크기 | **Manifest에 적힌 값** | **G6-3** 화면 `upgrade_watch.paths` — 같음 ✓ |
| **22** | 업그레이드 감시 경로 48개 중 이번에 바뀐 것 | 검사기 | **미리 알 수 없는 값** — 이번에 처음 나옵니다 |

앞의 네 개는 **2부에서 GitHub 화면으로 이미 확인한 값**입니다. 터미널이
같은 숫자를 다시 출력하는지 대조하는 용도입니다. 하나라도 다르면 그 자리에서
멈춥니다.

**마지막 22가 이 구간에서 새로 나오는 유일한 정보입니다.** 나머지는 다
"아까 본 그 숫자가 맞다"는 확인이고, 22는 "그래서 이번 업그레이드에서
우리가 확인할 파일이 이만큼이다"는 답입니다.

> **업그레이드 감시 경로은 어느 등록 폴더에서 읽나** — 구간 3은
> `harness/registrations/om-temp-1.13.1`을 읽습니다. G6에서 브라우저로
> 열어 본 것은 `om-temp-1.13.0` 쪽이었습니다. **지금은 두 폴더의 감시
> 목록이 같아서** 48이라는 숫자가 양쪽에서 똑같이 나옵니다.

### 지금은 아직 합치기 전입니다 — 그래서 업그레이드 감시 경로만 나옵니다

**맞습니다.** 이 시점에는 새 후보 코드(후보)가 아직 없습니다. 비교할 수
있는 것이 **목록 두 개**뿐입니다.

```text
Manifest의 업그레이드 감시 경로          OpenMetadata가 바꾼 파일
   (48개)         ∩            (834개)         =  22개
```

파일 내용을 비교한 것이 아니라 **파일 이름이 겹치는지만 본 것**입니다.
그래서 이 22개는 **확인 대상**이지 **문제 목록이 아닙니다.**

무엇을 언제 알 수 있는지 순서로 보면 이렇습니다.

| 시점 | 알 수 있는 것 | 어디서 |
|---|---|---|
| **합치기 전** (지금) | 업그레이드 감시 경로와 **겹치는 파일이 있는가** | **구간 3** |
| 합치는 중 | 실제로 **충돌하는가** (충돌) | 구간 5 |
| 합친 뒤 | 우리 변경이 **살아남았는가** (소실) | **이 예행연습 다음 단계** |

세 번째가 앞에서 본 `required_changed_paths` 검사입니다. 후보가 만들어진
뒤라야 "파일이 있는가 / 내용이 아직 다른가"를 볼 수 있으므로, 이
예행연습에는 들어 있지 않습니다.

**그래서 구간 3의 22개는 그 자체로 문제를 뜻하지 않습니다.** 22개가
걸린 채로도 구간 5에서 충돌이 하나도 안 날 수 있고, 실제로 이번에는
자동으로 다 풀렸습니다.

### 화면 맨 아래부터 보십시오 — `upstream`

```json
"upstream": {
  "base": "OFFICIAL_1_13_0",
  "target": "OFFICIAL_1_13_1",
  "changed_path_count": 834
}
h1 small{display:block;margin-top:.45rem;font-size:.48em;font-weight:650;color:var(--muted);letter-spacing:.01em}
```

| 이름 | 뜻 |
|---|---|
| `base` | 비교 **출발점**. 지금 우리가 깔고 쓰는 OpenMetadata 1.13.0 |
| `target` | **올라갈** OpenMetadata 1.13.1 |
| `changed_path_count` | 그 사이에 바뀐 파일 수. **우리 기능과 무관하게 OpenMetadata 쪽에서 일어난 변경** |

![영향 확인 · 아래쪽](assets/업그레이드시연/T07c-영향확인-판정.png)

확대

> 화면 맨 아래. `upstream` 세 줄과 그 위의 `gate`가 나오는 부분

G5 화면의 `Files changed 834`와 같은 숫자입니다. GitHub이 센 값과 우리
터미널이 센 값이 일치한다는 뜻입니다.

### `affected_customizations` — 기능별로 몇 개가 걸렸나

```json
{
  "customization_id": "BANK-OM-001",
  "changed_watch_path_count": 22,
  "changed_watch_paths": [ … 22개 나열 … ],
  "changed_configuration_keys": [],
  "changed_dependencies": []
}
```

| 이름 | 뜻 |
|---|---|
| `customization_id` | 어느 기능인지 |
| `changed_watch_paths` | 그 기능의 업그레이드 감시 경로(`upgrade_watch.paths`)에 적힌 파일 중, **이번 업그레이드에서 실제로 바뀐 것** |
| `changed_watch_path_count` | 그 개수 |
| `changed_configuration_keys` | **설정값 이름** 단위 감시 결과 (아래 설명) |
| `changed_dependencies` | **라이브러리 이름** 단위 감시 결과 (아래 설명) |

**영향을 받은 기능만 목록에 올라옵니다.** 하나도 안 걸린 기능은 아예 나오지
않습니다. 이번에는 7개가 모두 걸렸습니다.

![영향 확인 · 위쪽](assets/업그레이드시연/T07b-영향확인-앞부분.png)

확대

> 맨 위 `BANK-OM-001` 항목. `changed_watch_path_count: 22` 아래로
> 걸린 파일 22개가 그대로 나열됩니다

### 22라는 숫자를 어떻게 읽나

`22`는 **그 기능이 지켜보는 파일 중 이번에 바뀐 것의 개수**입니다.
전체가 몇 개인지 같이 봐야 뜻이 통합니다.

| 기능 | 업그레이드 감시 경로 (Manifest에 적힌 값) | 이번에 바뀐 것 (검사기가 센 값) |
|---|---|---|
| BANK-OM-001 기준코드 | 48개 | **22개** |
| BANK-OM-002 조회리포트 | 56개 | **23개** |
| BANK-OM-003 데이터점검 | 27개 | **19개** |
| BANK-OM-004 컬럼보기 | 34개 | **20개** |
| BANK-OM-005 한글입력 | 2개 | **1개** |
| BANK-OM-006 Sybase | 19개 | **4개** |
| BANK-OM-007 Tibero | 11개 | **1개** |

**이 표가 구간 3의 결과물입니다.** OpenMetadata가 834개를 바꿨지만, 기준코드
기능 담당자가 실제로 봐야 할 것은 **22개**입니다. 834개를 다 뒤질 필요가
없도록 좁혀 주는 것이 이 검사의 목적입니다.

왼쪽 열은 **우리가 미리 적어 둔 값**이고, 오른쪽 열은 **검사기가 이번에
센 값**입니다. 왼쪽이 비어 있으면 오른쪽도 0이 됩니다 — 아래 `[]` 두
항목이 바로 그 경우입니다.

BANK-OM-005(한글 입력)는 업그레이드 감시 경로이 2개뿐인데 그중 1개가 걸렸습니다.
`package.json` 입니다. 코드를 한 줄도 안 건드려도 **의존하는 라이브러리
버전이 바뀌면** 한글 입력이 깨질 수 있어서 넣어 둔 것이고, 이번에 실제로
바뀌었습니다. 업그레이드 감시 경로을 파일 단위로 넓게 잡아 두는 이유가 이것입니다.

### `[]` 로 비어 있는 두 항목은 무엇인가

파일 단위 말고 **더 좁게** 보는 두 축이 준비돼 있습니다.

| 항목 | 무엇을 보나 | 어떻게 |
|---|---|---|
| `changed_configuration_keys` | **설정값 이름** | 이번에 바뀐 `.yaml`·`.json`·`.toml` 파일의 변경 내용 안에 우리가 등록한 설정 이름이 나오는지 |
| `changed_dependencies` | **라이브러리 이름** | 이번에 바뀐 `package.json`·`pom.xml`의 변경 내용 안에 우리가 등록한 라이브러리 이름이 나오는지 |

**지금 둘 다 비어 있는 이유는 우리가 아무것도 등록하지 않았기 때문입니다.**
Manifest 7장 어디에도 `upgrade_watch.configuration_keys`와
`upgrade_watch.dependencies` 항목 자체가 없습니다.

> **"안 걸렸다"가 아니라 "안 보고 있다"입니다.** 기능은 만들어져 있지만
> 입력이 비어서 그 축의 감시는 실제로는 꺼져 있습니다. 예를 들어
> BANK-OM-005 가 `undici` 라이브러리 버전을 감시하고 싶다면 Manifest에
> 그 이름을 적어야 하고, 지금은 적혀 있지 않습니다. 발표에서 이 부분을
> 물으면 **"파일 단위 감시는 돌고 있고, 설정값·라이브러리 단위는 아직
> 우리가 입력을 채우지 않았다"** 고 답하시면 됩니다.

### `gate` — 판정

```json
"gate": {
  "name": "upgrade-watch",
  "verdict": "approval",
  "reasons": [ "BANK-OM-001: upstream A->B changed paths=22 (e.g. …Entity.java)", … ],
  "meaning": "approval은 자동 실패가 아니라, 영향을 받은 BANK-OM을 검토한 뒤 적용하라는 뜻이다."
}
```

| 이름 | 뜻 |
|---|---|
| `name` | 어느 검사인지. `upgrade-watch` = "우리 업그레이드 감시 경로의 파일이 이번에 바뀌었나" |
| `verdict` | 판정. `pass` / `approval` / `block` / `analysis_error` 중 하나 |
| `reasons` | 사람이 읽을 한 줄 요약. 기능별 건수와 **대표 파일 하나**(`e.g.`) |
| `meaning` | 판정의 뜻을 결과 파일에 그대로 박아 둔 것 |

![영향 확인 · gate](assets/업그레이드시연/T07c-영향확인-판정.png)

확대

> `gate`의 `reasons` 일곱 줄과 `verdict: approval`, 그리고 맨 아래
> 종료코드 2

`reasons`의 `A->B`는 `upstream.base -> upstream.target`, 즉 1.13.0 → 1.13.1
입니다. `e.g.` 뒤의 파일은 **예시 하나**일 뿐이고 전체 목록은 위쪽
`changed_watch_paths`에 있습니다.

`meaning`을 결과 파일에 넣어 둔 이유는, 나중에 이 파일만 따로 보는 사람이
`approval`을 실패로 읽지 않게 하기 위해서입니다.

### 종료코드 2

```
  종료코드 2    !!  확인 필요 — 담당자가 영향 경로를 검토해야 합니다 (실패 아님)
```

| 판정 | 종료코드 | 뜻 |
|---|---|---|
| `pass` | 0 | 업그레이드 감시 경로에 걸린 것이 하나도 없음 |
| `block` | 1 | 안전하게 진행할 수 없음 |
| **`approval`** | **2** | **걸린 것이 있으니 사람이 보고 진행** ← 지금 이것 |
| `analysis_error` | 3 | 판단 자체가 불가능. 통과로 보면 안 됨 |

**`확인 필요`는 실패가 아닙니다.** 자동화 도구가 판단할 수 없어 사람에게 넘긴
상태입니다. 통과·실패 두 가지가 아니라 중간 상태를 따로 둔 이유가
이 화면에 나옵니다.

> 이 검사는 **자동으로 막지 않습니다.** 그 파일이 바뀌었다고 해서 우리
> 기능이 깨진다는 뜻은 아니기 때문입니다. 번역 파일에 다른 언어
> 문구 한 줄이 추가된 것일 수도 있습니다. 그래서 "봐야 한다"까지만
> 말하고 판단은 사람에게 남깁니다.

## 구간 4 — 작업 폴더 만들기

화면에는 명령 두 줄과 결과 한 줄만 지나갑니다.

```
$ git -C ~/om-work/OM_TEMP worktree add -q -b rehearsal/patch-1.13.1 …/tree OFFICIAL_1_13_1
$ git -C …/tree switch -q -c rehearsal/custom-1.13.1
  OK  작업 폴더: ~/om-work/upgrade-rehearsal/tree
```

**공식 1.13.1 소스를 기준으로 별도의 임시 작업 폴더를 만드는
단계**입니다. 이 폴더에는 아직 BANK-OM 변경이 없습니다. 구간 5에서
commit 8건을 순서대로 재적용합니다.

| 하는 일 | 뜻 |
|---|---|
| `worktree add` | 같은 저장소에서 **별도 폴더**를 하나 더 엽니다. 원래 폴더는 그대로 둔 채 작업할 수 있습니다 |
| `switch -c` | 그 폴더에서 작업할 **새 branch 이름**을 만듭니다 |

> 캡처는 따로 필요 없습니다. 확인할 값이 없고 다음 구간으로 바로 넘어갑니다.
> 다만 **`이미 있습니다` 로 멈춘다면** 지난 실행 흔적이 남은 것이므로
> 0부 ① 의 정리 세 줄을 먼저 실행하십시오.

## 구간 5 — BANK-OM commit을 순서대로 재적용하기 ★

### 이 구간에서 실행하는 작업

구간 4에서 **OpenMetadata 1.13.1 을 그대로 펼쳐 놓은 빈 작업 폴더**를
만들었습니다. 우리 기능은 하나도 없는 상태입니다.

구간 5는 그 위에 **BANK-OM commit 8건을 한 건씩 재적용합니다.**
이 예행연습 스크립트가 사용하는 명령은 `git cherry-pick`입니다.

```
$ git cherry-pick 4df83b311f   # BANK-OM-001
  !!  BANK-OM-001  충돌한 파일 18개 — 충돌 해결 도구를 실행합니다
    resolved …/locale/languages/ar-sa.json: BANK-OM leaf changes=9
    resolved …/locale/languages/de-de.json: BANK-OM leaf changes=9
     ⋮  (18줄)
  OK  BANK-OM-001  충돌 18개 중 18개 해결 · 항목 162개 되살림
     ⋮
$ git cherry-pick d983f7c540   # BANK-OM-005
  OK  BANK-OM-005  충돌 없음
```

### 이번 예행연습에서 `cherry-pick`을 쓰는 이유

commit별로 재적용하면 어떤 BANK-OM 기능에서 충돌이 발생했는지 분리해서
기록할 수 있습니다. 이는 충돌 진단과 시연을 위한 선택입니다. 확정 운영
전략인 `vendor-merge` 전체를 대체하거나 검증한 것은 아닙니다.

![체리픽과 커밋별 머지의 기록 구조 비교](assets/업그레이드시연/도식-체리픽-머지-비교.svg)

확대

왼쪽은 이번 스크립트가 만든 선형 commit 재적용 결과입니다. 오른쪽은 과거
snapshot commit을 개별적으로 여덟 번 merge한 비교 실험입니다. 오른쪽은 목표
운영 방식인 “직전 custom branch에 새 patch branch를 한 번 merge”한
`vendor-merge`와 다른 실험입니다.

<details>
<summary><b>상세 비교 — 이번 commit별 재적용과 merge 실험의 차이</b></summary>

#### 이번 스크립트가 commit별 재적용을 선택한 이유

BANK-OM 기능은 Customization-ID가 있는 commit과 Manifest로 연결됩니다.
이번 스크립트는 기능별 충돌 건수를 분리하기 위해 commit 8건을 순서대로
재적용합니다.

기억하실 것은 2부 G3 화면입니다. 우리 코드는 이렇게 쌓여 있습니다.

```text
OpenMetadata 1.13.0 원본
    │
    ├─ 4df83b311f  BANK-OM-001 기준코드      ← commit 1건 = 기능 1개
    ├─ 68ebed4801  BANK-OM-002 조회리포트
    │      ⋮
    └─ 7d19c89526  BANK-OM-007 후속
```

각 commit에는 `Customization-ID: BANK-OM-NNN` trailer가 있고,
같은 ID의 후속 commit도 있을 수 있습니다. `cherry-pick`은 선택한 commit의
변경을 현재 branch에 새 commit으로 재적용합니다.

> **핵심:** 이번 `cherry-pick` 방식은 기능별 충돌 진단과
> 재현 가능한 시연을 위한 것입니다. 아래 merge 비교는 같은 snapshot commit을
> 개별 merge한 제한된 실험이며, 실제 `vendor-merge` 운영 경로의 적합성을
> 판정하지 않습니다.

#### 머지해도 충돌은 똑같이 납니다 — 그게 이유가 아닙니다

**실제로 머지를 해 보고 세었습니다.**

| 방법 | 충돌한 파일 |
|---|---|
| `cherry-pick` 8건 (지금 방식) | 18개 |
| `merge` 한 번 | **18개 — 똑같습니다** |

두 실험 모두 같은 18개 locale JSON에서 충돌했습니다. 따라서 이번
`cherry-pick` 선택의 목적은 충돌 수를 줄이는 것이 아닙니다. JSON의 최종
leaf 값은 같았지만 일부 직렬화 순서는 달랐으므로, 이 비교를 파일 byte가
항상 같다는 주장으로 확대하지 않습니다.

#### 두 실험의 commit 이력 차이

동일한 snapshot commit을 개별 merge한 비교 실험에서는 다음과 같은 이력이
생겼습니다.

```text
[ 머지한 경우 ]
  1c52b42904  Merge …                       Customization-ID = (없음)   ← 충돌 해결분 19개 파일이 여기
  7d19c89526  complete Tibero coverage      Customization-ID = BANK-OM-007
  62e39da8be  add Tibero customization      Customization-ID = BANK-OM-007
      ⋮
```

이 비교 실험에서는 충돌 해결 내용이 Customization-ID가 없는 merge commit에
기록되어, 기능별 충돌 건수를 바로 나누기 어려웠습니다.

```text
[ cherry-pick 한 경우 ]
  <새 번호>  add InstanceCode customization  Customization-ID = BANK-OM-001  ← 001 의 해결분은 여기
  <새 번호>  add QueryReport customization   Customization-ID = BANK-OM-002  ← 002 의 해결분은 여기
      ⋮  (8건, 전부 Customization-ID 하나씩)
```

**충돌 해결 내용이 해당 BANK-OM commit에 포함됩니다.** 요약표가 기능별로
`18 / 162`, `18 / 198` 처럼 기능별로 나오는 것도 이 구조 때문입니다. 머지하면 "어딘가에서
18개 충돌" 한 줄로 끝납니다.

#### 현재 예행연습 검사가 읽는 commit 범위

5부의 소스 검사는 이번 진단용 후보에서 공식 1.13.1 이후 commit과
Customization-ID를 다음과 같이 읽습니다.

```bash
git rev-list OFFICIAL_1_13_1..HEAD     # commit 8건이 나와야 함
# 그리고 각 BANK-OM commit에 Customization-ID가 정확히 하나
```

개별 merge 비교 결과에는 Customization-ID가 없는 merge commit이 추가되므로
이 예행연습의 선형 commit 범위 검사에 그대로 사용할 수 없습니다. 그렇다고
모든 merge 전략을 사용할 수 없다는 뜻은 아닙니다. 실제 vendor-merge 후보는
별도의 전략 결속과 검사 기준으로 검증해야 합니다.

|  | `cherry-pick` | `merge` |
|---|---|---|
| 충돌한 파일 | 18개 | 18개 (같음) |
| 충돌 JSON의 최종 leaf 값 | 기준 | 같음 (일부 key 순서는 다름) |
| 후보의 commit | **8건, 전부 Customization-ID 하나씩** | 9건, **그중 하나는 Customization-ID 없음** |
| 충돌 해결분의 소속 | **해당 BANK-OM commit** | Customization-ID 없는 머지 기록 |
| 검사기가 읽을 수 있나 | **예** | 아니오 |

> 참고로 우리 저장소의 1.13.0 은 공식 저장소에서 **코드 tree만 가져온
> 스냅샷**이라 공식 이력과 조상이 이어져 있지 않습니다. 그래서 공식
> 1.13.1 태그에 대고 바로 머지하면 `refusing to merge unrelated histories`
> 로 아예 거부되고, 억지로 붙이면 **734개**가 충돌합니다. 위의 18개는
> 우리 저장소 안에 1.13.1 스냅샷을 먼저 만들어 조상을 이어 준, 머지에
> 가장 유리한 조건에서 나온 값입니다.

#### "커밋 번호별로 머지하면 되지 않나" — 해 봤습니다

가장 자주 나오는 대안이라 실제로 8번 머지해 보았습니다.

**먼저, 공식 1.13.1 태그에 대고 커밋 하나를 머지하면 시작조차 못 합니다.**

```
$ git merge 4df83b311f
fatal: refusing to merge unrelated histories
```

우리 1.13.0 은 공식에서 **코드 tree만 가져온 스냅샷**이라 공식 이력과 조상이
이어져 있지 않기 때문입니다. 그래서 우리 저장소 안에 1.13.1 스냅샷을 먼저
만들어 조상을 이어 준 뒤 — **머지에 가장 유리한 조건에서** — 8번 머지한
결과가 이렇습니다.

|  | `cherry-pick` 8번 | `merge` 8번 |
|---|---|---|
| 최종 파일 내용 | `e490ed82dd…` | **`e490ed82dd…` — 똑같습니다** |
| 후보의 commit 수 | **8건** | **16건** |
| Customization-ID가 있는 기록 | 8건 (전부) | 8건 |
| **Customization-ID 없는 기록** | **0건** | **8건** |
| 후보가 공식 1.13.1 에서 출발하나 | **예** | **아니오** |
| 후보의 조상 이력에 1.13.0이 포함되는가 | **아니오** | **예** |

**파일 내용은 한 글자도 다르지 않습니다.** 말씀하신 대로 결과물만 보면
커밋별 머지로도 됩니다.

#### 8건이 어떻게 16건이 되나 — 실제 기록입니다

이 비교 실험의 `git merge`는 **실행할 때마다 merge commit을 하나
만듭니다.** 8번 merge했으므로 merge commit도 8개
생깁니다.

```text
[ 커밋별로 8번 머지한 결과 — git log --graph ]

*   08dbbd0530 Merge commit '7d19c89526' into try/each   ← merge commit 8
|\
| * 7d19c89526 complete Tibero service connection coverage
* | b0ceb77f99 Merge commit '62e39da8be' into try/each   ← merge commit 7
|\|
| * 62e39da8be add Tibero customization
* | 3f92bc5c1b Merge commit '010750c514' into try/each   ← merge commit 6
|\|
| * 010750c514 add Sybase customization
        ⋮   (같은 모양이 반복)
* | 59678fd35d Merge commit '4df83b311f' into try/each   ← merge commit 1
|\|
| * 4df83b311f add InstanceCode customization
* | b63242d7a7 Import official OpenMetadata 1.13.1 source snapshot
|/
* 2f4f3560e7 Import official OpenMetadata 1.13.0 source snapshot  ← 여기로 이어짐
```

**추가되는 것은 `Merge commit …` 8개입니다.** BANK-OM commit 8건은 그대로 있고,
여기에 merge commit 8개가 추가되어 모두 16건이 됩니다. 그리고 맨 아래를 보면 두 이력이
`2f4f3560e7` **1.13.0 스냅샷에서 갈라져 나온 것**으로 남습니다.

같은 명령을 체리픽 결과에 대고 찍으면 이렇습니다.

```text
[ 체리픽 결과 — git log --graph ]

* 17bbbcdf67 complete Tibero service connection coverage
* fa17da1620 add Tibero customization
* 2505217935 add Sybase customization
* 2990ea7244 fix Korean IME handling
* 423c29ca37 add bank column view customization
* 4d655064b2 add Data Assertions customization
* 4529312ea0 add QueryReport customization
* 55d0e1bd7f add InstanceCode customization
* afcb2d2cd7 chore(release): Prepare Branch for `1.13.1`   ← 공식 1.13.1
```

**한 줄로 곧게 8건이고, merge commit이 없고, 맨 아래가 공식 1.13.1 입니다.**

두 실험은 commit 이력을 만드는 방식이 다릅니다.

|  | BANK-OM commit 8건을 | merge commit | 맨 아래 |
|---|---|---|---|
| `cherry-pick` | **변경 내용을 새 commit으로 재적용**<br>`4df83b311f` → `55d0e1bd7f` | 없음 | 공식 1.13.1 |
| `merge` | **원본을 그대로 데려옴**<br>`4df83b311f` 그대로 | **8개 생김** | 1.13.0 스냅샷 |

문제는 아래 세 줄입니다.

1. **머지할 때마다 Customization-ID 없는 기록이 하나씩 더 생깁니다.** 8번 머지하면
  8건이 붙어 후보 기록이 16건이 됩니다. 충돌을 푼 내용은 그 Customization-ID 없는
  기록 쪽에 들어갑니다.
2. **후보가 공식 1.13.1 에서 출발하지 않게 됩니다.** 우리 스냅샷에서
  출발한 것이 되어, "이 후보는 공식 1.13.1 을 바탕으로 만들었다"를
  Git 으로 증명할 수 없습니다.
3. **후보의 조상 이력에 1.13.0이 포함됩니다.** merge는 commit 하나만 가져오는 것이
  아니라 **그 커밋의 조상 전부**를 붙이기 때문입니다. `4df83b311f`의
  조상에는 `2f4f3560e7 Import official OpenMetadata 1.13.0 source snapshot`
  이 들어 있습니다.

> **여기서 구분해야 할 점이 있습니다.** 조상 이력에 1.13.0이 포함된다는 것은 **1.13.0의 파일이
> 최종 결과에 다시 섞인다는 뜻이 아닙니다.** 위 표의 첫 줄대로 최종 파일 내용은 양쪽이
> 완전히 같습니다. 차이는 **commit 계보**입니다. 후보의 조상 목록에
> `2f4f3560e7 Import official OpenMetadata 1.13.0 source snapshot`이
> 들어가고, 그 결과 후보가 공식 1.13.1 의 자손이 아니게 됩니다.
> **파일 내용은 정상인데 출발점을 증명할 수 없게 되는 것**입니다.

검사기 8종 중 `vendor-ancestry`가 정확히 이것을 봅니다.

> 승인된 공식 target 이 후보의 조상이어야 한다 — 아니면 `block`

커밋별 머지 결과는 이 조건에서 걸립니다.

#### merge commit이 무엇이고, 조상이 왜 문제인가

**merge commit은 두 branch 이력을 연결하는 Git commit입니다.** 일반 commit은 부모가 하나지만, merge commit은
**부모가 둘**입니다 — 후보 branch의 직전 상태와, 방금 데려온 BANK-OM commit.
이어 붙였다는 사실 자체가 하나의 기록으로 남는 것이고, **충돌을 푼 내용도
그 안에 들어갑니다.**

조상 문제는 두 가지로 갈립니다. 둘 다 Git 으로 확인한 값입니다.

| 확인한 것 | 체리픽 | 커밋별 머지 |
|---|---|---|
| 후보의 조상에 **1.13.0 스냅샷**이 있나 | 아니오 | **예** |
| 후보의 조상에 **공식 1.13.1 커밋**(`afcb2d2cd7`)이 있나 | **예** | **아니오** |

**두 번째 줄이 진짜 문제입니다.** 머지를 하려면 우리 저장소 안에 1.13.1
스냅샷을 **직접 만들어야** 했습니다. 그 순간 후보는 우리가 만든 커밋에서
출발한 것이 되고, **공식이 낸 그 커밋에서 출발했다는 사실을 Git 이 더는
보증해 주지 못합니다.**

> "이 후보는 공식 1.13.1 을 바탕으로 만들었습니다" 를 **말이 아니라 Git
> 으로 증명할 수 있느냐** — 이것이 `vendor-ancestry` 게이트가 보는 것입니다.

#### 이 비교를 운영 전략의 결론으로 사용하면 안 됩니다

위 결과는 과거 snapshot의 BANK-OM commit을 하나씩 merge한 비교
실험입니다. 목표 운영 전략인 `vendor-merge`는 직전 custom branch의 전체
이력에 새 공식 patch branch를 한 번 merge하는 방식이므로, 입력 이력과 merge
횟수가 다릅니다.

| 구분 | 목적 | 현재 상태 |
|---|---|---|
| commit별 `cherry-pick` | BANK-OM별 충돌을 분리한 이번 예행연습 | 후보 코드 생성과 tree SHA 재현 확인 |
| commit별 merge 비교 | 동일 snapshot commit을 개별 merge했을 때 이력 비교 | 제한된 비교 실험 |
| 실제 `vendor-merge` | 직전 custom 전체 이력과 새 patch를 병합하는 목표 운영 경로 | **NOT VERIFIED** |

따라서 “merge는 운영에 사용할 수 없다”거나 “cherry-pick이 확정 운영
방식이다”라고 결론 내리지 않습니다. 실제 vendor-merge 후보를 만든 뒤 후보
생성 이력, Candidate lock의 전략 값, 소스 검사와 runtime 결과를 다시 결속해야
운영 경로를 판단할 수 있습니다.

`cherry-pick`은 파일 전체를 덮어쓰는 명령이 아니라 선택한 commit의
변경을 현재 코드에 재적용합니다. Git이 자동 병합하지 못한 부분은 충돌로
중단되고, 담당자가 결과를 검토해야 합니다.

#### 특정 파일만 골라서 올리는 것인가 — 아닙니다

**`cherry-pick`은 파일을 고르지 않습니다.** 그 commit이 바꾼 파일
**전부**를 한꺼번에 적용합니다.

BANK-OM-001을 실제로 세어 본 값입니다.

|  | 파일 수 |
|---|---|
| 원본 commit `4df83b311f`이 바꾼 파일 | **48개** |
| `cherry-pick`이 적용을 시도한 파일 | **48개 전부** |
| 그중 조용히 들어간 것 | **30개** |
| 그중 충돌해서 멈춘 것 | **18개** |
| 옮겨진 뒤 후보에서 그 기록이 바꾼 파일 | **48개** |

**들어가고 안 들어가고가 갈린 게 아닙니다.** 48개 전부 들어갑니다.
갈리는 것은 **"자동으로 되느냐, 멈추느냐"** 입니다.

```text
cherry-pick 4df83b311f   ← 파일 48개 전부를 대상으로 시작
      │
      ├─ 30개  새 버전이 안 건드린 파일 → 그냥 들어감
      │
      └─ 18개  새 버전도 건드린 파일   → git 이 멈춤
                    │
                    └─ 충돌 해결 도구가 이 18개만 항목 단위로 처리
      │
cherry-pick --continue   ← 48개 전부가 담긴 commit 1건으로 마무리
```

**마무리된 뒤 BANK-OM-001 변경은 하나의 새 commit으로 기록됩니다.** 실제 후보에서 확인한 값은
이렇습니다.

```
$ git log -1 --format='%s%n%b' <재적용된 commit>
add InstanceCode customization
Customization-ID: BANK-OM-001

$ git show --stat --name-only <재적용된 commit> | wc -l
48
```

Customization-ID도 그대로 따라왔습니다. **"commit 1건 = 기능 1개"** 구조가 새 원본
위에서도 유지된다는 것이 `cherry-pick`을 쓰는 이유입니다.

#### "항목"은 기능이 아닙니다

여기서 **항목**이라는 말이 자주 나오는데, BANK-OM 번호와는 전혀 다른
단위입니다. 크기 순서로 보면 이렇습니다.

```text
기능        BANK-OM-001 기준코드                   ← 번호 1개
  └ commit   4df83b311f                          ← 커밋 1건
      └ 파일       ko-kr.json 등 48개               ← 여기까지가 git 이 보는 단위
          └ 항목       label.instance-code = "인스턴스 코드"
                       label.code-group    = "Code Group"
                          ⋮  ko-kr.json 안에 9개    ← 충돌 해결 도구가 보는 단위
```

| 단위 | 예 | 개수 |
|---|---|---|
| 기능 | BANK-OM-001 | 1 |
| commit | `4df83b311f` | 1건 |
| 파일 | `ko-kr.json` | 48개 |
| **항목** | **`label.instance-code`** | **`ko-kr.json` 안에만 9개** |

**항목은 파일 안의 줄 하나에 가깝습니다.** "같은 항목을 양쪽이 고쳤다"는
것은 "기능이 겹쳤다"가 아니라 **"`label.instance-code` 라는 이름 하나를
새 버전도 쓰고 우리도 썼다"** 는 뜻입니다.

#### BANK-OM 버전으로 파일 전체를 덮어쓰는가

**아닙니다.** 실제 파일에서 세어 본 값으로 보여드립니다.

`cherry-pick`은 **파일을 통째로 가져오지 않습니다.** 그 기록이 만든
**변경분만** 새 파일에 다시 적용합니다.

한국어 문구 파일 `ko-kr.json` 하나를 실제로 세어 본 값입니다.

|  | 항목 수 |
|---|---|
| 새 버전(1.13.1)이 이 파일에서 바꾼 항목 | **118개** |
| BANK-OM-001이 이 파일에 넣은 항목 | **9개** |
| **겹치는 항목** | **0개** |

겹치는 것이 하나도 없으므로 결과는 **118개 그대로 + 우리 9개 추가**입니다.
새 버전이 한 일은 하나도 지워지지 않습니다.

우리가 넣은 9개는 이런 이름들입니다.

```text
label.instance-code          = 인스턴스 코드
label.instance-code-plural   = 인스턴스 코드
label.code-group             = Code Group
label.code-name              = Code Name
label.code-value             = Code Value
label.sort-order             = Sort Order
   ⋮
```

이번 공식 1.13.1 변경에서는 이 아홉 JSON leaf path를 수정하지 않았으므로
leaf path 교집합이 0개였습니다. 다음 버전에서도 항상 겹치지 않는다고 가정하지
않고 실행할 때마다 다시 계산합니다.

Git은 JSON 의미 구조가 아니라 줄과 주변 문맥을 기준으로 병합합니다. 이번에는
공식 1.13.1의 대규모 서식·배치 변경과 BANK-OM 항목 추가가 같은 줄 구간에 있어
자동 병합이 중단됐습니다. 충돌 해결 도구는 BASE·OURS·THEIRS를 JSON으로 읽어
최종 leaf path의 교집합을 다시 계산합니다.

#### 그럼 사람이 봐야 하는 경우는

**겹칠 때입니다.** 그때는 자동으로 아무 쪽도 고르지 않고 **멈춥니다.**

| 상황 | 어떻게 되나 |
|---|---|
| 항목이 안 겹침 | 자동으로 우리 항목만 끼워 넣음 |
| **같은 항목을 양쪽이 고침** | **멈춤** — 어느 쪽을 남길지 사람이 결정 |
| **JSON이 아닌 파일이 충돌** | **멈춤** — 자동 처리 대상이 아님 |

멈출 때 나오는 화면입니다.

```
    …/ko-kr.json: overlapping leaf changes: ['label.instance-code']
중단: BANK-OM-001: 새 버전과 우리가 같은 항목을 고쳤습니다. 어느 쪽을 남길지는
    자동으로 정할 수 없으므로 코드 담당자가 직접 결정해야 합니다.
    위 overlapping leaf changes 줄에 그 항목 이름이 있습니다.
```

```
중단: BANK-OM-001: JSON 이외 파일이 충돌했습니다. 자동 해결 대상이 아니므로
    코드 담당자가 직접 해결해야 합니다
```

**파일 전체를 BANK-OM 버전으로 덮어쓰거나 기존 BANK-OM commit을 수정하는 작업은 자동으로 하지 않습니다.**
그건 업무 판단이라 사람 몫입니다. 이번 실행에서는 겹친 것이 하나도 없어서
8건 모두 자동으로 넘어갔습니다.

> **자동으로 넘어간 것도 그냥 믿고 끝내지는 않습니다.** 후보가 만들어진
> 뒤 검사기가 "우리 변경이 새 코드에 실제로 살아 있는가"를 다시 봅니다
> (앞의 `required_changed_paths` 검사). 여기 자동 처리는 **후보를 만드는
> 단계**이고, 판정은 그다음입니다.

#### 이 예행연습 스크립트에서는 `cherry-pick` 방식이 고정돼 있습니다

다음 설명은 전체 운영 전략이 아니라 이 스크립트의 실행 방식에만
해당합니다.

> 스크립트는 충돌 유무와 관계없이 BANK-OM commit 8건을 모두
> `cherry-pick`합니다. 충돌이 발생한 뒤 임의로 선택하는 명령이 아닙니다.

이번 실행에서는 BANK-OM-005·006과 BANK-OM-007의 두 commit이 충돌 없이
재적용됐지만, 동일하게 `cherry-pick`을 사용했습니다.

**선택은 그 안에서 충돌이 났을 때 생깁니다.**

```text
이번 스크립트의 commit 8건  →  cherry-pick
                          │
              ┌───────────┴───────────┐
        충돌 없음                   충돌 발생
     그대로 올라감          ┌────────┴────────┐
                     항목 안 겹침        항목 겹침 / JSON 아님
                    자동으로 처리            ★ 멈춤 ★
                                        여기서 사람이 고릅니다
```

멈췄을 때 사람이 고를 수 있는 것은 세 가지입니다.

| 고르는 것 | 무슨 뜻인가 | 뒤따르는 일 |
|---|---|---|
| **BANK-OM 변경을 유지한다** | 공식 변경과의 호환성을 검토한 뒤 BANK-OM 동작을 유지 | 관련 test와 소스 검사를 다시 실행 |
| **새 버전을 따른다** | 새 버전 동작을 받아들인다 | 후보 코드의 해결 내용을 같은 BANK-OM ID로 기록하고, 경로가 달라지면 6부의 `plan → 승인 → apply`로 Manifest를 갱신 |
| **둘을 합친다** | 양쪽을 살리는 코드를 새로 쓴다 | 같은 BANK-OM ID로 해결 내용을 기록하고 Manifest·Contract·test 재검토 |

**어느 쪽도 자동화 도구가 정하지 않습니다.** "새 버전을 따른다"는 곧 **행내
커스터마이징을 하나 바꾸는 일**이고, 그건 코드 담당자와 업무 담당자가
결정할 문제입니다.

> 정리하면, `cherry-pick`은 이 스크립트가 commit을 재적용하는 방식이고,
> 충돌 해결 방향은 코드·업무 담당자가 별도로 판단할 사항입니다. 이번 실행은
> JSON leaf path가 겹치지 않아 자동 초안을 만들 수 있었으며, 그 결과도 후속
> 검사로 다시 확인해야 합니다.

</details>

### 요약표

마지막에 요약표가 나옵니다. **아래와 똑같이 나와야 합니다.**

```
  기능           원본 commit       충돌파일   해결파일   되살린항목
  BANK-OM-001    4df83b311f           18         18          162
  BANK-OM-002    68ebed4801           18         18          198
  BANK-OM-003    57ee1b3b23           18         18           90
  BANK-OM-004    274f2b79b4           18         18          162
  BANK-OM-005    d983f7c540            0          0            0
  BANK-OM-006    010750c514            0          0            0
  BANK-OM-007    62e39da8be            0          0            0
  BANK-OM-007    7d19c89526            0          0            0
```

### 어느 열끼리 비교하는 것인가

**앞의 두 열만 서로 비교하시면 됩니다.** 둘 다 파일 개수이고, **같아야
합니다.**

| 열 | 단위 | 보는 법 |
|---|---|---|
| 충돌파일 | 파일 개수 | 몇 개가 충돌했나 |
| 해결파일 | 파일 개수 | 그중 몇 개를 해결했나 — **충돌파일과 같아야 함** |
| 되살린항목 | **항목 개수** | 단위가 다릅니다. 비교 대상이 아닙니다 |

`18 = 18`이면 **충돌을 하나도 남기지 않고 해결했다**는 뜻입니다.
하나라도 남으면 그 자리에서 멈추므로 다음 기능으로 넘어가지 않습니다.

세 번째 열은 **참고용 상세**입니다. 파일 안에서 실제로 몇 줄을 손봤는지
보여줄 뿐이고, 앞의 두 열과 맞춰 볼 숫자가 아닙니다.

| 단위 | BANK-OM-001 의 경우 |
|---|---|
| 파일 | 18개가 충돌하고 18개를 해결 |
| 항목 | 그 18개 파일 안에서 파일당 9개씩, 합계 **162개** |

BANK-OM-001은 화면 문구 9개를 19개 언어에 넣은 기능입니다. 그중 18개
언어 파일을 새 버전도 건드려서 충돌했고, **파일마다 우리 문구 9개씩을
되살려** 넣은 것입니다.

```text
ko-kr.json  (충돌한 파일 1개)
   ├─ "기준코드"        ← 되살린 항목 1
   ├─ "기준코드 그룹"    ← 되살린 항목 2
   │      ⋮
   └─ 9번째 문구        ← 되살린 항목 9
       ×  18개 언어 파일  =  162개
```

기능별로 항목 수가 다른 것도 같은 이유입니다 — BANK-OM-002는 파일당
11개(18×11=198), BANK-OM-003은 5개(18×5=90)를 넣었습니다.

> **왜 덮어쓰지 않고 "되살린다"고 하나** — 충돌한 번역 파일은 새 버전 것을
> 그대로 두고, **우리가 넣었던 항목만 다시 반영합니다.** 새 버전이 그
> 파일에 추가한 다른 언어 문구는 그대로 살아 있습니다. 양쪽이 **같은 항목**을
> 건드렸다면 이 자동 처리를 하지 않고 멈춥니다.
>
> 📸 **⑧** — 요약표 전체
>
> **숫자가 다르면 캡처해서 알려주십시오.** 원격 branch가 움직였다는
> 뜻이므로 원인부터 확인해야 합니다.

![기능별 요약표](assets/업그레이드시연/T08-요약표.png)

확대

> **⚠️ 이 ⑧ 이미지는 과거 집계 화면이므로 발표 자료에 사용하지
> 마십시오.** 오른쪽 열이 파일 하나의 값인 9 · 11 · 5 · 9로 표시돼 있습니다.
> 현재 스크립트를 다시 실행해 합계 162 · 198 · 90 · 162가 나온 화면으로
> 교체해야 합니다.
>
> 과거 스크립트는 충돌 해결 도구가 출력한 18줄 중 첫 줄만 합계처럼
> 표시했습니다. 집계 표시를 수정한 뒤에도 후보 코드 tree SHA
> `e490ed82dd…`는 같았습니다. 즉 후보 코드 내용은 바뀌지 않았고 요약
> 숫자 계산만 수정됐습니다.

## 구간 6 — 후보 확인

```
  검사 후보 Git commit SHA : (실행할 때마다 다른 값)
  OK  옮겨진 commit 수 = 8
  OK  공식 1.13.1 대비 변경 파일 수 = 111
━━ 예행연습 완료 ━━
```

> 📸 **⑨**

![예행연습 완료](assets/업그레이드시연/T09-예행연습-완료.png)

확대

> 실제로 이렇게 나옵니다 (2026-08-03 실행)

---

# 4부 · 후보 코드 재현성 확인 ★★

이 단계에서는 실행 환경이 달라도 같은 파일 상태의 후보 코드가 만들어졌는지
tree SHA로 대조합니다.

```bash
# 만들어진 후보 폴더의 '파일 내용 전체'를 번호 하나로 요약해 찍습니다.
#   -C <폴더>     그 폴더에서 실행하라는 뜻
#   HEAD^{tree}   지금 상태의 파일 내용 (만든 시각은 빼고)
git -C ~/om-work/upgrade-rehearsal/tree rev-parse HEAD^{tree}
```

**아래 값이 나오면 이번 commit별 재적용 예행연습의 후보 코드 생성이
재현된 것입니다.**

```
e490ed82dd9cfe58833b2050a233aae7496541ab
```

> 📸 **⑩** — 이 화면 하나가 발표 전체의 근거입니다.

![재현 확인](assets/업그레이드시연/T10-재현확인-tree.png)

확대

> 실제로 이렇게 나옵니다 (2026-08-03 실행)

## 후보 commit SHA는 달라도 정상입니다

```bash
# 이번 실행에서 만들어진 후보의 정보를 그대로 출력합니다
cat ~/om-work/upgrade-rehearsal/candidate.txt
```

`candidate_sha`는 재적용 과정에서 새로 만들어진 commit의 SHA이므로
committer 시각 등 commit metadata에 따라 달라질 수 있습니다.

|  | 같아야 하나 | 이유 |
|---|---|---|
| `candidate_sha` (Git commit SHA) | ✗ 달라도 정상 | 만든 시각이 섞임 |
| `tree` SHA (파일 상태) | **✓ 같아야 함** | 파일 경로·내용·mode가 동일함 |

발표에서는 “후보 commit SHA는 실행 시각에 따라 달라질 수 있지만, tree SHA가
같으므로 이번 예행연습이 만든 파일 상태는 동일합니다”라고 설명하십시오.

---

# 5부 · 후보 코드 검사와 원격 공유 준비

> 먼저 로컬 임시 worktree의 후보 코드를 검사합니다. 원격 push는 검사 통과
> 뒤에 저장소 쓰기 권한과 담당자 승인을 확인한 경우에만 수행합니다. 시연을
> 위해 원격 branch를 임의로 만들지 마십시오.

## 1. 검사 대상 worktree 확인

```bash
git -C ~/om-work/upgrade-rehearsal/tree rev-parse HEAD^{tree}
git -C ~/om-work/upgrade-rehearsal/tree status --porcelain
```

첫 줄은 4부의 `e490ed82dd…`와 같아야 하고, 두 번째 명령은 아무것도
출력하지 않아야 합니다. 다르면 검사하지 말고 3부부터 다시 확인하십시오.

## 2. 등록자료 검사 5종

```bash
cd ~/om-work/openmetadata-test

./.venv/bin/python harness/registrations/om-temp-1.13.0/validate_registration_bundle.py \
  --repo ~/om-work/upgrade-rehearsal/tree \
  --registration harness/registrations/om-temp-1.13.1 \
  --output ~/om-work/upgrade-rehearsal/registration-validation-results.json
```

| 붙인 값 | 뜻 |
|---|---|
| `--repo` | 3부에서 만든 후보 코드 worktree |
| `--registration` | 대조할 1.13.1 등록 폴더 |

**나와야 할 것 — 5개 항목이 모두 `pass`**

| 검사 | 확인값 |
|---|---|
| Manifest 구조와 작성 규칙 | 7개 Manifest |
| Registry·Manifest·Contract 연결 | 7개 BANK-OM |
| Git 전체 변경 목록 | 111개 경로 |
| 공용 파일 소유정보 | 37개 공용 경로 |
| 필수 테스트 코드 존재 | 9개 Python pytest |

> 📸 **⑪**

## 3. 소스 게이트 8종

```bash
./.venv/bin/python harness/run_source_candidate_gates.py \
  --repo ~/om-work/upgrade-rehearsal/tree \
  --harness harness \
  --registration harness/registrations/om-temp-1.13.1 \
  --layout harness/registrations/om-temp-1.13.1/repository-layout.yaml \
  --sensitive-zones harness/registrations/om-temp-1.13.1/sensitive-zones.yaml \
  --output ~/om-work/upgrade-rehearsal/source-gate-results.json
```

**나와야 할 것 — 8개가 모두 `pass`**

| 게이트 | 무엇을 보나 |
|---|---|
| `vendor-ancestry` | 후보가 공식 1.13.1 의 자손인가 |
| `customization-survival` | **우리 변경이 새 코드에 살아남았는가** |
| `required-test-implementations` | 필수 테스트가 실제로 있는가 |
| `commit-invariants` | commit의 형태 규칙 |
| `id-invariants` | Customization-ID 규칙 |
| `drift` | Manifest와 코드가 어긋났는가 |
| `sensitive-zones` | 민감 경로에 허용되지 않은 변경이 있는가 |
| `exact-scope-history` | 변경 범위가 Manifest와 정확히 같은가 |

> 📸 **⑫**

두 번째 `customization-survival`이 **G6에서 본 `required_changed_paths`
를 실제로 확인하는 검사**입니다. 앞에서 설명한 "파일이 있는가 / 내용이
아직 다른가" 두 가지를 여기서 봅니다.

## 4. 결과 확인

```bash
cat ~/om-work/upgrade-rehearsal/registration-validation-results.json
cat ~/om-work/upgrade-rehearsal/source-gate-results.json
```

소스 게이트 결과의 `candidate_lock.candidate`에는 후보 코드의 tree SHA가 함께 기록됩니다.

```json
"candidate_lock": {
  "candidate": {
    "tree_sha": "e490ed82dd9cfe58833b2050a233aae7496541ab"
  }
}
```

**4부에서 확인하신 값과 같아야 합니다.** 같으면 "이 검사 결과는 내가 만든
그 후보에 대한 것"이 성립합니다. 4부의 확인값이 왜 중요한지가 여기서
드러납니다.

> 📸 **⑬** — 이 화면이 이 시연의 마지막입니다.

## 5. 승인받은 경우에만 원격 branch로 공유

다른 사람이 같은 후보를 검사해야 할 때만 저장소 owner에게 branch 이름과
대상 tree SHA를 확인받은 뒤 실행합니다. 현재 문서만으로 push 권한이 부여되는
것은 아닙니다.

```bash
cd ~/om-work/upgrade-rehearsal/tree

# 아래 두 branch 생성이 승인된 경우에만 실행
git push origin OFFICIAL_1_13_1:refs/heads/patch/om-1.13.1
git push origin HEAD:refs/heads/custom/om-1.13.1
```

push 후에는 GitHub에서 두 branch의 Git commit SHA와 4부의 tree SHA를
대조하고, 검사 결과 파일을 같은 후보 SHA와 함께 보관합니다.

## 그래도 배포해도 된다는 뜻은 아닙니다

여기까지 전부 통과해도 확인된 것은 **코드를 읽어서 알 수 있는 것**까지입니다.

| 남은 것 | 상태 |
|---|---|
| 전체 프로그램 빌드 | 미실행 · 증거 없음 |
| 실제 서버에서 화면·기능 시험 | 미실행 · 증거 없음 |
| 운영 배포 승인 | 미승인 |

---

# 6부 · Manifest는 어떻게 만들어지나 (선택)

> **5부까지가 시연의 본체입니다.** 여기는 "그 Manifest는 누가 어떻게 만드느냐"는
> 질문이 나왔을 때 펼치는 부분입니다. 발표에서 건너뛰어도 앞의 결론은
> 그대로입니다.

G6에서 본 `BANK-OM-001.yaml` 같은 파일을 **Manifest**라고 부릅니다.
기능 하나가 어느 파일을 건드리는지, 그중 무엇이 없어지면 안 되는지를 적어 둔
문서입니다. 검사기는 코드가 아니라 **이 문서를 기준으로** 판정합니다.

## Manifest는 승인 없이 직접 수정하지 않습니다

Manifest는 검사 기준이므로 변경 근거와 승인 기록이 필요합니다. 현재 구현된
정식 변경 경로는 **`plan → 사람 승인 → apply`** 세 단계입니다.

```text
plan  ──────►  담당자 승인  ──────►  apply
(조사)          (사람 판단)          (반영)

읽기만 함        질문에 답함         승인한 그대로만 씀
아무것도         등록 폴더를         제안이 조금이라도
안 바꿈          안 건드림           바뀌면 거부
```

| 단계 | 하는 일 | 등록 폴더를 바꾸나 |
|---|---|---|
| `plan` | Git 사실을 계산해 **제안서**를 만듦 | **아니오** |
| 승인 | 사람이 질문에 답하고 승인서를 씀 | 아니오 |
| `apply` | 승인서와 제안서가 정확히 맞을 때만 반영 | **예** |

자동화 도구가 하는 것은 **Git에서 읽을 수 있는 사실**뿐입니다 — 어느 commit이
어느 파일을 바꿨는가. 자동화 도구가 하지 않는 것은 **업무 판단**입니다 — 그중
무엇이 없어지면 안 되는가, 담당자는 누구인가.

## 1. plan — 조사만 합니다

검사 저장소 최상위에서 실행합니다.

```bash
cd ~/om-work/openmetadata-test

./.venv/bin/python harness/prepare_registration.py plan \
  --repo ~/om-work/OM_TEMP \
  --registration harness/registrations/om-temp-1.13.0 \
  --patch-ref origin/patch/om-1.13.0 \
  --custom-ref origin/custom/om-1.13.0 \
  --product-version 1.13.0 \
  --output ~/om-work/plan-out
```

| 붙인 값 | 뜻 |
|---|---|
| `--repo` | 읽을 제품 코드 폴더 |
| `--registration` | 대조할 등록 폴더 |
| `--patch-ref` | 공식 코드만 있는 branch |
| `--custom-ref` | BANK-OM 커스터마이징 commit이 포함된 branch |
| `--product-version` | 어느 버전의 등록인지 |
| `--output` | 조사 결과를 쌓을 **바깥** 폴더 |

**실제 출력입니다.**

```json
{
  "analysis_error_count": 0,
  "blocked_count": 0,
  "change_count": 0,
  "output": "/Users/…/om-work/plan-out",
  "proposal_digest": "sha256:502a6824bb60e02b0d6cf4a66043e9e5d9ec0b22ed70b2c3387437b738d278b7",
  "review_count": 5,
  "status": "REVIEW_REQUIRED"
}
```

> 📸 **⑭**
>
> 위 digest는 저장소에 보관된 OM_TEMP 1.13.0 제안의 실제 값입니다. 같은
> patch SHA·custom SHA·등록자료로 다시 실행했다면 같은 digest가 나와야 합니다.
> 다르면 입력 중 하나가 바뀐 것이므로 정상으로 간주하지 말고
> `summary.md`와 `diff.patch`를 다시 검토하십시오. `apply`는
> 승인서와 현재 제안의 digest가 다르면 중단합니다.

**종료코드는 2입니다.** 실패가 아닙니다. 3부 구간 3에서 본 것과 같은 뜻으로,
**사람이 답할 질문이 남았다**는 표시입니다.

| 상태 | 종료코드 | 뜻 |
|---|---|---|
| `READY` | 0 | 추가 질문 없음. 제안 내용을 검토한 뒤에도 명시적 승인 필요 |
| `REVIEW_REQUIRED` | 2 | **사람이 답할 질문이 있음** ← 지금 이것 |
| `BLOCKED` | 1 | 안전하게 반영할 수 없음. 원인을 고치고 다시 |
| `ANALYSIS_ERROR` | 3 | 판단 자체가 불가능. **통과로 보면 안 됨** |

### plan 이 정말 아무것도 안 바꿨는지 확인

```bash
# 조사 후 검사 저장소에 바뀐 것이 있는지 봅니다
git -C ~/om-work/openmetadata-test status --porcelain
```

**아무것도 안 나옵니다.** 조사 결과는 전부 `--output` 으로 지정한 바깥
폴더에만 쌓입니다. "조사는 읽기 전용"이라는 것을 문서로 약속하는 데 그치지
않고 이 한 줄로 직접 확인할 수 있습니다.

### 생기는 파일

```bash
# 조사 결과로 어떤 파일들이 생겼는지 봅니다
ls ~/om-work/plan-out
```

| 파일 | 내용 |
|---|---|
| `summary.md` | 사람이 먼저 읽는 한 장짜리 요약 |
| `review-required.yaml` | **담당자가 답해야 할 질문 목록** |
| `proposal.yaml` | 제안 전문. 다음 단계의 입력 |
| `proposal-digest.txt` | 제안 내용의 digest |
| `commit-inventory.yaml` | commit별로 어느 파일을 바꿨는지 |
| `current-diff-paths.txt` | 지금 두 branch의 파일 차이 |
| `diff.patch` | Manifest가 어떻게 바뀌는지. **이번엔 0바이트** |
| `proposed-registration/` | 바뀔 Manifest 원본. **이번엔 비어 있음** |

마지막 두 개가 비어 있습니다. **자동 변경 0건** —
자동화 도구가 고칠 것은 하나도 없고, 남은 것은 전부 사람이 답할 질문이라는 뜻입니다.

## 2. 질문 읽기 — 자동화 도구가 답하지 않는 것

```bash
cat ~/om-work/plan-out/summary.md                  # 한 장짜리 요약부터 봅니다
head -30 ~/om-work/plan-out/review-required.yaml   # 담당자가 답할 질문 목록 앞 30줄
```

이번에 나온 질문 5건입니다.

| 번호 | 기능 | 파일 수 | 질문 |
|---|---|---|---|
| `REVIEW-0001` | BANK-OM-001 | 16개 | 공식에 없는 행내 전용 파일을 계속 지켜볼 것인가 |
| `REVIEW-0002` | BANK-OM-002 | 18개 | 〃 |
| `REVIEW-0003` | BANK-OM-003 | 3개 | 〃 |
| `REVIEW-0004` | BANK-OM-006 | 3개 | 〃 |
| `REVIEW-0005` | BANK-OM-007 | 3개 | 〃 |

> 📸 **⑮**

### 왜 이건 자동화 도구가 못 정하나

이 파일들은 **현재 공식 OpenMetadata 기준에는 없고 BANK-OM이 추가한 경로**입니다.
향후 공식 버전이 같은 경로를 새로 만들 가능성과 해당 기능의 운영 중요도를 고려해,
업그레이드 감시 경로에 계속 포함할지 담당자가 결정해야 합니다.

**이 판단은 코드 비교만으로 확정할 수 없습니다.** 기능의 실제 사용 여부와 영향도를
아는 담당자가 답해야 하므로 자동화 도구는 임의로 결정하지 않고
`REVIEW_REQUIRED`로 남깁니다.

## 3. 승인서 쓰기

빈 서식을 받습니다. `--proposal`에는 **폴더가 아니라 `proposal.yaml` 파일**을
줍니다.

```bash
./.venv/bin/python harness/prepare_registration.py approval-template \
  --proposal ~/om-work/plan-out/proposal.yaml \
  --output ~/om-work/approval.yaml
```

| 붙인 값 | 뜻 |
|---|---|
| `--proposal` | 방금 만든 제안서 **파일** (폴더가 아닙니다) |
| `--output` | 여기에 빈 승인서를 만들어 줍니다 |

```yaml
schema_version: 1
proposal_digest: sha256:502a6824bb60e02b0d6cf4a66043e9e5d9ec0b22ed70b2c3387437b738d278b7
approved_by: REPLACE_WITH_APPROVER_ID
approved_at: REPLACE_WITH_RFC3339_TIME
decisions:
- finding_id: REVIEW-0001
  decision: accept_proposal
  reason: REPLACE_WITH_REVIEW_REASON
  …
```

`REPLACE_WITH_…`로 표시된 세 종류의 값을 채웁니다. 각 결정의
`reason`은 질문마다 별도로 작성합니다.

| 자리 | 채우는 값 | 예 |
|---|---|---|
| `approved_by` | 승인자 ID | `hong.gildong` (형식 예시, 실제 승인자 아님) |
| `approved_at` | 승인 시각 (시차 포함) | `2026-08-03T14:00:00+09:00` |
| `reason` | **질문별 판단 사유** | `운영 중 사용 중인 화면이라 감시 유지` |

> **사유는 질문마다 따로 씁니다.** 다섯 건에 같은 문장을 붙여 넣는 것은
> 형식상 통과하지만, 나중에 "왜 그렇게 정했느냐"에 답할 근거가 없어집니다.
> 이 승인서가 그대로 감사 기록으로 남습니다.
>
> **시각은 시차까지 적어야 합니다.** `2026-08-03T14:00` 처럼 `+09:00`이
> 없으면 거부됩니다. 어느 지역 시간인지 모르면 승인 시점이 특정되지
> 않기 때문입니다.

## 4. 빈 승인서가 거부되는 방식

아래 명령과 결과는 빈 승인서가 실제 변경 전에 차단되는지 검증한 예입니다.
발표에서는 다시 실행하지 말고 기존 캡처와 결과를 보여주십시오.

```bash
./.venv/bin/python harness/prepare_registration.py apply \
  --repo ~/om-work/OM_TEMP \
  --registration harness/registrations/om-temp-1.13.0 \
  --proposal ~/om-work/plan-out/proposal.yaml \
  --approval ~/om-work/approval.yaml
```

| 붙인 값 | 뜻 |
|---|---|
| `--repo` | branch가 승인 때와 그대로인지 다시 확인 |
| `--registration` | 실제로 반영할 등록 폴더 |
| `--proposal` | 승인받은 바로 그 제안서 |
| `--approval` | 채워 넣은 승인서 |

```json
{
  "code": "POLICY_REFUSED",
  "message": "approval still contains placeholder approver",
  "status": "BLOCKED"
}
```

**종료코드 1로 막힙니다.** 등록 폴더는 그대로입니다.

발표에서 보여줄 만한 화면입니다. "승인 절차가 형식적인 것 아니냐"는
물음에 **빈 승인서로는 실제로 반영이 안 된다**는 것을 그 자리에서 보여줄 수
있습니다.

> 📸 **⑯**

`apply`가 거부하는 경우는 이것 말고도 있습니다.

| 상황 | 왜 막나 |
|---|---|
| 승인서의 digest가 제안서와 다름 | 승인한 제안이 아닌 다른 것을 반영하려는 것 |
| 두 branch가 그 사이 움직임 | 승인 시점과 코드가 달라짐 |
| Manifest·담당자 목록이 그 사이 바뀜 | 승인자가 본 기준이 아님 |
| 질문에 빠짐없이 답하지 않음 | 답하지 않은 판단이 남음 |
| 다른 사람이 같은 폴더에 반영 중 | 동시에 쓰면 결과가 섞임 |

**"승인한 그 순간의 상태가 아니면 반영하지 않는다"** — 모두 이 한 가지 규칙입니다.

## 5. 실제 승인 후 apply가 성공하면

> **아래 JSON은 성공 형식을 설명하는 예시입니다.** 현재 OM_TEMP
> 1.13.0 제안은 사람 승인과 실제 `apply`를 수행하지 않았습니다. 예시의
> `hong.gildong`도 실제 승인자가 아닙니다.

```json
{
  "status": "APPLIED",
  "approved_by": "hong.gildong",
  "patch_sha": "2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50",
  "custom_head_sha": "7d19c8952612e77467b0a80d6287170d814f1de1",
  "proposal_digest": "sha256:502a6824bb60e02b0d6cf4a66043e9e5d9ec0b22ed70b2c3387437b738d278b7",
  "written_files": ["commit-inventory.yaml", "current-diff-paths.txt"]
}
```

`written_files`가 **실제로 쓴 파일 전부**입니다. 승인서에 없는 파일은
쓰지 않습니다.

> **발표 시연에서는 실제 승인값을 만들거나 `apply`를 실행하지
> 마십시오.** 빈 승인서가 BLOCK되는 4번까지만 보여주면 승인 강제를 설명할 수
> 있습니다. 실제 apply는 승인 권한을 가진 담당자가 제안 digest와 질문별 사유를
> 확인한 뒤 수행하며, 반영 후 등록자료 검사와 소스 검사를 다시 실행합니다.

## Manifest 안에는 무엇이 적혀 있나

`BANK-OM-005`(한글 입력 보정) 전문입니다. Manifest 7장 중 가장 짧아 전체를 한 화면에 실을 수 있습니다.

```yaml
customization_id: BANK-OM-005
status: active
kind: core-patch
title: 한글 입력 조합 보정
implementation:
  changed_paths:                     # 이 기능이 변경한 파일 전부
  - …/SchemaEditor/SchemaEditor.tsx
  required_changed_paths:            # 그중 없어지면 안 되는 것
  - …/SchemaEditor/SchemaEditor.tsx
upgrade_watch:
  paths:                             # 공식이 바꾸면 확인해야 할 것
  - …/ui/package.json
  - …/SchemaEditor/SchemaEditor.tsx
assurance:
  contracts:
  - CONTRACT-KOREAN-IME              # 정상이라고 판단할 조건
```

세 줄만 구분하시면 됩니다.

| 항목 | 뜻 | 없으면 |
|---|---|---|
| `changed_paths` | 이 기능이 **변경한 파일 전부** | 범위를 알 수 없음 |
| `required_changed_paths` | 그중 **하나라도 사라지면 실패** | 기능이 조용히 지워져도 통과함 |
| `upgrade_watch.paths` | 이 파일이 바뀌면 **확인 필요** | 3부 구간 3의 `48개 중 22개` 같은 숫자가 안 나옴 |

3부 구간 3에서 본 `BANK-OM-001 … 22`는 **여기 `upgrade_watch.paths`에
적힌 48개 중 이번 업그레이드가 22개를 건드렸다**는 뜻입니다. 그 48이
어디서 나온 숫자인지가 이 화면에 있습니다.

> 구간 5 요약표의 `18`과는 다른 숫자입니다. 그쪽은 **실제로 합칠 때
> 충돌한 파일 수**이고, 여기 22는 **합치기 전에 이름만 대조해 본 수**입니다.

`package.json`이 업그레이드 감시 경로에 있는 이유도 같습니다. 코드를 직접 고치지
않아도 **의존하는 라이브러리 버전이 바뀌면** 한글 입력이 깨질 수 있기
때문입니다.

## 더 자세한 절차

새 기능에 번호를 새로 발급하거나 Manifest를 처음부터 쓰는 절차는 이 문서 범위
밖입니다.

| 자료 | 다루는 것 |
|---|---|
| [`OM_TEMP 검사 전 준비도구 쉬운 사용법`](OM_TEMP_검사전_준비도구_쉬운사용법.md) | 역할별로 누가 무엇을 하는지, 상태값 읽는 법 |
| [`OM_TEMP Manifest 작성 단계별 가이드`](OM_TEMP_Manifest_작성_단계별_가이드.md) | 항목 하나하나를 정하는 기준 |
| [`BANK-OM 등록 정책`](../02-설계/bank_om_registration_policy.md) | 번호 발급 규칙과 저장소 역할 |

---

# 막혔을 때

| 화면에 나오는 말 | 원인 | 대처 |
|---|---|---|
| `제품 저장소에 커밋하지 않은 변경이 있습니다` | OM_TEMP에 변경한 파일이 있음 | `git -C ~/om-work/OM_TEMP status` 로 확인 후 정리 |
| `검사 저장소 루트에서 실행하십시오` | 폴더를 잘못 잡음 | `cd ~/om-work/openmetadata-test` 후 재실행 |
| `... 이(가) 기대와 다릅니다` | 원격 branch가 움직임 | 캡처해서 문의 |
| `python 의존성 부족` | 준비 4단계 안 함 | 4단계 재실행 |
| `... 이(가) 이미 있습니다` | 이전 실행 흔적이 남음 | 아래 정리 명령 |
| `JSON 이외 파일이 충돌했습니다` | 프로그램 파일이 충돌 | **자동 처리 대상이 아닙니다.** 캡처 후 개발자에게 |
| `... 의 파일 내용을 읽지 못했습니다` | 공식 소스를 온전히 받지 못함 | 화면에 함께 나오는 `--refetch` 명령을 실행한 뒤 재시도 |

## 다시 돌리기 전 정리

맨 위 **0부 ①** 의 세 줄과 같습니다.

---

# 확인 완료 범위와 남은 일

이 문서로 확인하는 범위는 commit별 재적용을 통한 진단용 후보 코드 생성과
소스 수준 검사입니다. 목표 운영 전략, build, 실제 기능과 배포 승인은 별도
증거가 필요합니다.

|  | 상태 |
|---|---|
| 공식 1.13.1에 BANK-OM commit 8건 재적용 | **예행연습 완료·재현 확인** — 운영 전략 검증은 아님 |
| 등록자료 검사 5종·소스 게이트 8종 | 실행 방법 구현·기존 결과 있음. 시연 후보에서 다시 실행해 같은 tree SHA에 결속 |
| Manifest 변경 제안·승인·반영 | `plan` 구현·실행 완료, 5개 판단은 **REVIEW_REQUIRED**, 실제 승인·apply 미실행 |
| 실제 `vendor-merge` 후보 생성과 전략 검증 | **NOT VERIFIED** |
| 전체 프로그램 빌드 | 미실행 · 증거 없음 |
| 실제 서버에서 화면·기능 시험 | 미실행 · 증거 없음 |
| 운영 배포 승인 | 미승인 |

Manifest는 직접 편집하지 않고 `plan → 담당자 승인 → apply` 절차로
변경합니다. 6부는 실제 OM_TEMP 1.13.0 `plan` 결과와 빈 승인서 BLOCK
동작을 설명합니다. 실제 승인자 지정과 `apply`는 수행하지 않았습니다.

## 함께 보는 자료

| 자료 | 용도 |
|---|---|
| `assets/업그레이드시연/` | 이 순서를 실제로 돌려 찍은 캡처와 실행 로그 |
| `OM_TEMP_검사전_준비도구_쉬운사용법.md` | 5부의 절차를 역할별로 나눠 설명한 것 |
| `OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드.md` | 충돌 상세와 배경 설명 |

---

**이 예행연습을 모두 통과해도 배포해도 된다는 뜻이 아닙니다.**
확인한 것은 “코드를 읽어서 알 수 있는 것”까지입니다.
