# Codex 작업 요청 — 1.13.0 → 1.13.1 업그레이드 시연 캡처 16장

> 작성: 2026-07-31
> 요청 대상: Codex (브라우저 캡처 가능 환경)
> 산출물: PNG 16장 + 캡처 결과 보고

---

## 0. 이 요청의 배경

임원 대상 발표 자료를 만들고 있습니다. 자료 본문은 이미 완성됐고
(`docs/00-사용가이드/OM_TEMP_업그레이드_예행연습_실행순서.md`),
**각 단계의 실제 화면 캡처만 비어 있습니다.**

현재 작업 환경에서는 브라우저로 GitHub 로그인 세션을 열 수 없어
웹 화면을 찍지 못합니다. Codex 환경에서 대신 찍어 주시면 됩니다.

### 반드시 지켜 주실 것

1. **없는 화면을 만들어 내지 마십시오.** 실제로 실행하거나 실제로 연 화면만
   캡처합니다. 데이터를 넣어 GitHub처럼 보이게 만든 화면은 사용할 수 없습니다.
2. **기대값과 다르면 멈추고 보고하십시오.** 아래 각 항목에 “화면에 반드시
   보여야 하는 값”을 적어 두었습니다. 다르면 원격 저장소가 움직였다는
   뜻이므로, 진행하지 말고 그 화면을 캡처해 보고해 주십시오.
3. **원격에 아무것도 push하지 마십시오.** 이 작업은 읽기와 로컬 실행뿐입니다.
4. **등록 폴더(`harness/registrations/**`)를 수정하지 마십시오.**
   예행연습 스크립트는 이 폴더를 건드리지 않습니다.
5. **토큰·비밀번호·개인 계정 정보가 화면에 찍히지 않게** 해 주십시오.
   GitHub 우측 상단 프로필 영역은 잘라내거나 가려 주시면 됩니다.

---

## 1. 사전 준비

### 1.1 저장소 두 개

| 저장소 | 역할 | 브랜치 |
|---|---|---|
| `easyseop/openmetadata-test` | 검사 도구·기준 (여기서 명령 실행) | `claude/markdown-file-feedback-26933w` |
| `easyseop/OM_TEMP` | 검사 대상 제품 코드 (내려받기만) | `patch/om-1.13.0`, `custom/om-1.13.0` |

```bash
mkdir -p ~/om-work && cd ~/om-work
git clone https://github.com/easyseop/openmetadata-test.git
git clone https://github.com/easyseop/OM_TEMP.git

cd ~/om-work/openmetadata-test
git switch claude/markdown-file-feedback-26933w
git pull --ff-only

python3 -m venv .venv
./.venv/bin/pip install "PyYAML>=6.0" "jsonschema>=4.18" "pathspec>=0.11"
```

### 1.2 출발점이 맞는지 먼저 확인

```bash
cd ~/om-work/OM_TEMP
git fetch origin patch/om-1.13.0 custom/om-1.13.0
git rev-parse origin/patch/om-1.13.0 origin/custom/om-1.13.0
git status --porcelain
```

**기대값**

```
2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50
7d19c8952612e77467b0a80d6287170d814f1de1
```

`git status --porcelain` 은 **빈 출력**이어야 합니다.

> 이 값이 다르면 이후 모든 캡처가 무의미합니다. 여기서 멈추고 보고해 주십시오.

---

## 2. 파일 이름과 저장 위치

```
docs/00-사용가이드/assets/업그레이드시연/
```

| 접두 | 대상 | 예 |
|---|---|---|
| `T` | 터미널 캡처 | `T04-사전점검.png` |
| `G` | GitHub 화면 캡처 | `G02-두브랜치-비교-111.png` |

- 형식: **PNG**
- 터미널: 가로 **1400px 이상**, 배경 어두운 계열, 글자가 선명할 것
- GitHub: 브라우저 창 가로 **1400px 이상** (좁으면 GitHub이 요소를 숨김)
- 강조가 필요한 항목은 아래 “강조 표시” 지침 참고

### 강조 표시

기존 캡처(`docs/00-사용가이드/공유문서/assets/om-temp-manifest/commit-messages/`)와
같은 방식으로 맞춰 주십시오.

- 핵심 숫자·문자열에 **노란 배경 상자**
- 그 옆에 **화살표 + 짧은 한글 라벨**
- 강조본과 원본을 **모두** 남길 것: `G02-...-highlighted.png`, `G02-...-original.png`

강조가 어려우면 **원본만** 주셔도 됩니다. 강조는 이후 단계에서 넣을 수 있습니다.

---

## 3. GitHub 화면 캡처 6장

> 아래 5개 주소(G1~G5)는 표준 GitHub 주소 형식으로 적은 것이며 **실제로 열어
> 확인하지 못했습니다.** 404가 나면 3.7의 대안을 따라 주십시오.
> G6만 열리는 것을 확인했습니다.

### G1 — 브랜치 두 개가 실제로 있다

```
https://github.com/easyseop/OM_TEMP/branches
```

**보여야 할 것:** 목록에 `patch/om-1.13.0` 과 `custom/om-1.13.0`
**파일명:** `G01-브랜치-목록.png`

### G2 ★ — 우리가 손댄 파일이 111개

```
https://github.com/easyseop/OM_TEMP/compare/patch/om-1.13.0...custom/om-1.13.0
```

**보여야 할 것:** 화면 상단 **`111 changed files`**
**강조할 것:** `111` 숫자
**파일명:** `G02-두브랜치-비교-111.png`

> 발표에서 “이 숫자는 우리가 센 게 아니라 GitHub이 센 것”이라고 말할
> 근거입니다. 가장 중요한 GitHub 캡처입니다.

### G3 — 기능별 변경 기록 8건

```
https://github.com/easyseop/OM_TEMP/commits/custom/om-1.13.0
```

**보여야 할 것:** 아래 8건이 위에서부터(최신순이면 역순으로) 보일 것

```
add InstanceCode customization
add QueryReport customization
add Data Assertions customization
add bank column view customization
fix Korean IME handling
add Sybase customization
add Tibero customization
complete Tibero service connection coverage
```

**파일명:** `G03-변경기록-8건.png`

### G4 — 공식 1.13.1이 실제로 배포돼 있다

```
https://github.com/open-metadata/OpenMetadata/releases/tag/1.13.1-release
```

**보여야 할 것:** 태그 이름 `1.13.1-release`
**파일명:** `G04-공식-1.13.1-릴리스.png`

### G5 ★ — 공식이 바꾼 파일이 834개

```
https://github.com/open-metadata/OpenMetadata/compare/1.13.0-release...1.13.1-release
```

**보여야 할 것:** 화면 상단 **`834 changed files`**
**강조할 것:** `834` 숫자
**파일명:** `G05-공식-두버전-비교-834.png`

> 파일 수가 많아 GitHub이 “Showing first N files” 로 잘라 표시할 수 있습니다.
> **총 개수(834)만 보이면 됩니다.**
> G2의 111과 나란히 놓고 “축이 다른 두 숫자”를 설명하는 데 씁니다.

### G6 — 등록표 실물

```
https://github.com/easyseop/openmetadata-test/blob/claude/markdown-file-feedback-26933w/harness/registrations/om-temp-1.13.0/manifests/BANK-OM-001.yaml
```

**보여야 할 것:** `changed_paths:` 와 `required_changed_paths:` 두 항목이
나뉘어 있는 부분
**파일명:** `G06-등록표-BANK-OM-001.png`

### 3.7 주소가 열리지 않을 때 (G2 · G5)

브랜치 이름에 `/` 가 들어가 주소가 깨질 수 있습니다. 그때는 주소를 직접
치지 말고 화면에서 고르십시오.

1. 저장소 메인 → **Compare** 버튼
2. 왼쪽(base) 드롭다운에서 `patch/om-1.13.0` (G5는 `1.13.0-release`)
3. 오른쪽(compare) 드롭다운에서 `custom/om-1.13.0` (G5는 `1.13.1-release`)

결과 화면은 같습니다.

---

## 4. 터미널 캡처 10장

### 4.1 실행 명령

**반드시 `openmetadata-test` 폴더에서** 실행합니다.

```bash
cd ~/om-work/openmetadata-test
PYTHON=./.venv/bin/python harness/tools/upgrade_rehearsal.sh ~/om-work/OM_TEMP
```

스크립트는 6개 구간으로 나뉘어 출력합니다. 구간 경계는
`━━ 숫자. 제목 ━━` 형태의 청록색 줄입니다.

전체 로그를 파일로도 남겨 주십시오.

```bash
PYTHON=./.venv/bin/python harness/tools/upgrade_rehearsal.sh ~/om-work/OM_TEMP \
  2>&1 | tee ~/om-work/rehearsal-full.log
```

### 4.2 캡처 목록

#### T01 — 저장소 두 개 내려받기
1.1의 `git clone` 두 줄이 끝난 화면.
**파일명:** `T01-저장소-clone.png`

#### T02 — 파이썬 준비 완료
```bash
./.venv/bin/python -c "import yaml, jsonschema, pathspec; print('준비 완료')"
```
**보여야 할 것:** `준비 완료`
**파일명:** `T02-파이썬-준비완료.png`

#### T03 — 출발점 두 개
1.2의 `git rev-parse` 결과.
**보여야 할 것:** `2f4f3560e7…` 와 `7d19c89526…`
**파일명:** `T03-출발점-두개.png`

#### T04 — 사전 점검 (구간 0)
**보여야 할 것 (4줄 전부)**
```
  OK  제품 저장소가 깨끗합니다
  OK  1.13.0 공식 기준 branch = 2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50
  OK  1.13.0 행내 branch = 7d19c8952612e77467b0a80d6287170d814f1de1
  OK  두 branch 사이 변경 파일 수 = 111
```
**파일명:** `T04-사전점검.png`

#### T05 — 이름표 확인 (구간 1)
**보여야 할 것**
```
4df83b311f | BANK-OM-001 | add InstanceCode customization
68ebed4801 | BANK-OM-002 | add QueryReport customization
57ee1b3b23 | BANK-OM-003 | add Data Assertions customization
274f2b79b4 | BANK-OM-004 | add bank column view customization
d983f7c540 | BANK-OM-005 | fix Korean IME handling
010750c514 | BANK-OM-006 | add Sybase customization
62e39da8be | BANK-OM-007 | add Tibero customization
7d19c89526 | BANK-OM-007 | complete Tibero service connection coverage
  OK  변경 기록 8건 모두 이름표가 정확히 하나입니다
```
**파일명:** `T05-이름표-8건.png`

#### T06 — 공식 배포본 받기 (구간 2)
**보여야 할 것**
```
  OK  공식 1.13.0 고유번호 = f329dd4a7e47134a2bd5a06af6181b0ee527ddd9
  OK  공식 1.13.1 고유번호 = afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9
```
**파일명:** `T06-공식버전-받기.png`

#### T07 ★ — 적용 전 영향 확인 (구간 3)
JSON 출력이 길어 화면을 넘칩니다. **끝부분의 판정 줄이 반드시 포함**되어야 합니다.
```
  종료코드 2    !!  확인 필요 — 담당자가 영향 경로를 검토해야 합니다 (실패 아님)
```
**강조할 것:** `종료코드 2` 와 `확인 필요`
**파일명:** `T07-영향확인-확인필요.png`

기능별 겹침 수를 따로 뽑은 화면도 있으면 좋습니다(선택).
```bash
grep -oE '"customization_id": "[^"]+"|"changed_watch_path_count": [0-9]+' \
  ~/om-work/upgrade-rehearsal/upgrade-watch.json
```
**기대값:** 001=22, 002=23, 003=19, 004=20, 005=1, 006=4, 007=1
**파일명(선택):** `T07b-기능별-겹침수.png`

#### T08 ★ — 기능 옮겨 얹기 요약표 (구간 5 끝)
**보여야 할 것 — 아래와 정확히 같아야 합니다**
```
  기능           원본기록      부딪힘  되살림
  BANK-OM-001    4df83b311f        18       9
  BANK-OM-002    68ebed4801        18      11
  BANK-OM-003    57ee1b3b23        18       5
  BANK-OM-004    274f2b79b4        18       9
  BANK-OM-005    d983f7c540         0       0
  BANK-OM-006    010750c514         0       0
  BANK-OM-007    62e39da8be         0       0
  BANK-OM-007    7d19c89526         0       0
```
**파일명:** `T08-요약표.png`

> **숫자가 하나라도 다르면 진행하지 말고 보고해 주십시오.**

부딪히는 순간 화면도 하나 있으면 좋습니다(선택).
```
$ git cherry-pick 4df83b311f   # BANK-OM-001
  !!  BANK-OM-001  부딪힌 파일 18개 — 정리 도구를 실행합니다
  OK  BANK-OM-001  되살린 항목 9개
```
**파일명(선택):** `T08b-부딪힌-순간.png`

#### T09 — 예행연습 완료 (구간 6)
**보여야 할 것**
```
  OK  옮겨진 변경 기록 수 = 8
  OK  공식 1.13.1 대비 변경 파일 수 = 111
━━ 예행연습 완료 ━━
```
**파일명:** `T09-예행연습-완료.png`

#### T10 ★★ — 재현 확인 (가장 중요)
```bash
git -C ~/om-work/upgrade-rehearsal/tree rev-parse HEAD^{tree}
cat ~/om-work/upgrade-rehearsal/candidate.txt
```

**보여야 할 것**
```
e490ed82dd9cfe58833b2050a233aae7496541ab
```

**강조할 것:** 위 값 전체
**파일명:** `T10-재현확인-tree.png`

> **이 값이 다르면 반드시 보고해 주십시오.** 이 한 줄이 “내부적으로 해보니
> 됐다”와 “누구나 같은 결과가 나온다”를 가르는 유일한 근거입니다.
>
> 같은 화면의 `candidate.txt` 안 `candidate_sha` 는 **실행할 때마다 달라지는
> 것이 정상입니다.** 변경 기록 번호에는 만든 시각이 섞이기 때문입니다.
> 이 점이 화면에 함께 보이면 좋습니다.

---

## 5. 마치고 정리

```bash
git -C ~/om-work/OM_TEMP worktree remove --force ~/om-work/upgrade-rehearsal/tree
git -C ~/om-work/OM_TEMP branch -D rehearsal/patch-1.13.1 rehearsal/custom-1.13.1
```

`~/om-work/upgrade-rehearsal/` 안의 로그와 JSON은 **지우지 말고 함께 전달**해
주십시오. 캡처의 원본 근거로 씁니다.

---

## 6. 전달해 주실 것

1. PNG 16장 (선택 항목 포함 시 최대 19장)
2. `~/om-work/rehearsal-full.log` — 실행 전체 로그
3. `~/om-work/upgrade-rehearsal/upgrade-watch.json`
4. `~/om-work/upgrade-rehearsal/candidate.txt`
5. `~/om-work/upgrade-rehearsal/conflicts.tsv`
6. 아래 형식의 짧은 보고

```
실행 일시:
실행 환경(OS / git 버전 / python 버전):

출발점 확인       : 일치 / 불일치(내용:            )
요약표 8행        : 일치 / 불일치(내용:            )
tree 번호         : e490ed82dd… 일치 / 불일치(실제:            )
candidate_sha     : (실행마다 다름 — 실제값:            )

캡처 완료: T01~T10 (   /10), G01~G06 (   /6)
못 찍은 것과 사유:
열리지 않은 주소:
```

---

## 7. 요약 — 체크리스트

| | 항목 | 핵심 확인값 |
|---|---|---|
| ☐ | T01 저장소 clone | — |
| ☐ | T02 파이썬 준비 | `준비 완료` |
| ☐ | T03 출발점 | `2f4f3560e7…` / `7d19c89526…` |
| ☐ | T04 사전 점검 | `111` |
| ☐ | T05 이름표 | 8건, 각 1개 |
| ☐ | T06 공식 받기 | `f329dd4a7e…` / `afcb2d2cd7…` |
| ☐ | **T07 ★ 영향 확인** | `종료코드 2` |
| ☐ | **T08 ★ 요약표** | 18/9, 18/11, 18/5, 18/9, 0/0×4 |
| ☐ | T09 완료 | `111` |
| ☐ | **T10 ★★ 재현 확인** | `e490ed82dd…` |
| ☐ | G01 브랜치 목록 | 두 브랜치 존재 |
| ☐ | **G02 ★ 두 브랜치 비교** | `111 changed files` |
| ☐ | G03 변경 기록 | 8건 |
| ☐ | G04 공식 릴리스 | `1.13.1-release` |
| ☐ | **G05 ★ 공식 비교** | `834 changed files` |
| ☐ | G06 등록표 | `required_changed_paths` |

---

## 8. 참고 문서

| 문서 | 내용 |
|---|---|
| `docs/00-사용가이드/OM_TEMP_업그레이드_예행연습_실행순서.md` | 사람이 따라 하는 실행 순서 (이 요청의 원본) |
| `harness/tools/upgrade_rehearsal.sh` | 실행 스크립트 본체 |
| `docs/00-사용가이드/OM_TEMP_1.13.0_1.13.1_업그레이드_실행_가이드.md` | 업그레이드 배경과 충돌 상세 |
| `docs/00-사용가이드/공유문서/assets/om-temp-manifest/commit-messages/` | 기존 캡처 16장 — **강조 표시 스타일 참고용** |
