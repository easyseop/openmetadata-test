# OM_TEMP 1.13.0 → 1.13.1 업그레이드 예행연습 실행 순서

> 최종 갱신: 2026-07-31
>
> 대상: 직접 실행하고 발표 자료용 화면을 캡처할 담당자
>
> 걸리는 시간: 준비 20분(처음 한 번) · 실행 5분
>
> 디스크: OM_TEMP 폴더가 약 230MB 까지 늘어납니다. 공식 배포본 두 시점을
> 통째로 받아 두기 때문이며, 그래야 중간에 네트워크가 끊겨도 끝까지 돕니다.

이 문서는 **한 번 따라 하면 끝까지 가는 순서**입니다. 위에서부터 그대로
실행하시고, 📸 표시가 나오면 그 화면을 캡처하시면 됩니다.

## 저장소가 두 개입니다

| 저장소 | 역할 | 이 문서에서 |
|---|---|---|
| `easyseop/OM_TEMP` | 검사받는 제품 코드 | **내려받기만** 합니다 |
| `easyseop/openmetadata-test` | 검사 도구와 기준 | **모든 명령을 여기서** 칩니다 |

`openmetadata-test` 폴더 안에서, `OM_TEMP` 폴더를 **가리키며** 실행합니다.
이것만 기억하시면 헷갈릴 일이 없습니다.

## 캡처는 모두 16장입니다

| 종류 | 장수 | 표기 |
|---|---|---|
| 터미널 화면 | 10장 | 📸 ① ~ ⑩ |
| GitHub 화면 | 6장 | 📸 G1 ~ G6 |

★ 표시한 것(⑦ ⑧ ⑩ G2 G5)이 발표에서 가장 중요한 다섯 장입니다.

---

# 1부 · 준비 (처음 한 번만)

## 1. 프로그램 확인

```bash
git --version          # 2.43 이상
python3 --version      # 3.11 이상
```

없으면 먼저 설치하십시오.

## 2. 저장소 두 개 내려받기

두 폴더를 나란히 두면 경로가 짧아집니다.

```bash
mkdir -p ~/om-work && cd ~/om-work

git clone https://github.com/easyseop/openmetadata-test.git
git clone https://github.com/easyseop/OM_TEMP.git
```

> 📸 **①** 두 개가 모두 내려받아진 터미널 화면

## 3. 검사 저장소를 작업 브랜치로

```bash
cd ~/om-work/openmetadata-test
git switch claude/markdown-file-feedback-26933w
git pull --ff-only
```

## 4. 파이썬 준비물 설치

```bash
python3 -m venv .venv
./.venv/bin/pip install "PyYAML>=6.0" "jsonschema>=4.18" "pathspec>=0.11"
./.venv/bin/python -c "import yaml, jsonschema, pathspec; print('준비 완료')"
```

> 📸 **②** `준비 완료` 가 찍힌 화면

## 5. 제품 저장소 브랜치 확인

```bash
cd ~/om-work/OM_TEMP
git fetch origin patch/om-1.13.0 custom/om-1.13.0
git rev-parse origin/patch/om-1.13.0 origin/custom/om-1.13.0
```

**아래 두 값이 나와야 합니다.**

```
2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50     ← 공식 코드만 있는 쪽
7d19c8952612e77467b0a80d6287170d814f1de1     ← 우리 기능까지 있는 쪽
```

> 📸 **③** 위 두 번호가 보이는 화면.
> "우리는 정확히 이 코드에서 출발했다"의 근거입니다.

## 6. 제품 저장소가 깨끗한지

```bash
git status --porcelain
```

**아무것도 안 나와야 합니다.** 뭔가 나오면 예행연습이 거부합니다.
검사 대상이 아닌 파일이 섞여 들어가는 것을 막는 안전장치입니다.

---

# 2부 · GitHub 화면 캡처

브라우저에서 찍습니다. **창을 1400px 이상으로 넓혀 주십시오.** 좁으면
GitHub이 화면 요소를 감춥니다. 숫자가 보이는 윗부분만 있으면 되고,
파일 목록까지 내려가지 않으셔도 됩니다.

## G1. 브랜치 두 개가 실제로 있다

```
github.com/easyseop/OM_TEMP/branches
```

`patch/om-1.13.0` 과 `custom/om-1.13.0` 이 목록에 보이면 됩니다.

> 📸 **G1**

## G2. 우리가 손댄 파일이 111개다 ★

```
github.com/easyseop/OM_TEMP/compare/patch/om-1.13.0...custom/om-1.13.0
```

화면 위쪽 **`111 changed files`** 가 핵심입니다.

> 📸 **G2** — 발표에서 "이 숫자는 GitHub이 세어준 것"이라고 말할 수 있는 근거

주소가 열리지 않으면 브랜치 이름의 `/` 때문일 수 있습니다. 그때는
저장소에서 **Compare** 버튼을 누르고 드롭다운으로 왼쪽 `patch/om-1.13.0`,
오른쪽 `custom/om-1.13.0` 을 고르십시오. 결과는 같습니다.

## G3. 기능별 변경 기록 8건

```
github.com/easyseop/OM_TEMP/commits/custom/om-1.13.0
```

`add InstanceCode customization` 부터 아래로 8건이 나열됩니다.

> 📸 **G3**

## G4. 공식 1.13.1이 실제로 배포돼 있다

```
github.com/open-metadata/OpenMetadata/releases/tag/1.13.1-release
```

> 📸 **G4**

## G5. 공식이 바꾼 파일이 834개다 ★

```
github.com/open-metadata/OpenMetadata/compare/1.13.0-release...1.13.1-release
```

화면 위쪽 **`834 changed files`** 가 핵심입니다.

> 📸 **G5** — G2의 111과 나란히 놓고 "축이 다른 두 숫자"를 설명하는 데 씁니다

## G6. 등록표 실물

```
github.com/easyseop/openmetadata-test/blob/claude/markdown-file-feedback-26933w/harness/registrations/om-temp-1.13.0/manifests/BANK-OM-001.yaml
```

`changed_paths`(손댄 파일 전부)와 `required_changed_paths`(없어지면 안 되는
핵심 파일)가 나뉘어 있는 것이 보입니다.

> 📸 **G6**

> **참고** G1~G5의 주소는 표준 형식으로 적은 것이며 실제로 열어 확인하지는
> 못했습니다(사내 환경에서 확인 필요). G6만 열리는 것을 확인했습니다.

---

# 3부 · 예행연습 실행

**반드시 `openmetadata-test` 폴더에서** 실행합니다.

```bash
cd ~/om-work/openmetadata-test
PYTHON=./.venv/bin/python harness/tools/upgrade_rehearsal.sh ~/om-work/OM_TEMP
```

화면이 6개 구간으로 흘러갑니다. 구간마다 캡처하십시오.

## 구간 0 — 사전 점검

```
  OK  제품 저장소가 깨끗합니다
  OK  1.13.0 공식 기준 branch = 2f4f3560e7a8437e2f4f7fcafd00d32ea2d91a50
  OK  1.13.0 행내 branch = 7d19c8952612e77467b0a80d6287170d814f1de1
  OK  두 branch 사이 변경 파일 수 = 111
```

> 📸 **④**

## 구간 1 — 기능별 변경 기록과 이름표

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

> 📸 **⑤**

## 구간 2 — 공식 배포본 받기

```
  OK  공식 1.13.0 고유번호 = f329dd4a7e47134a2bd5a06af6181b0ee527ddd9
  OK  공식 1.13.1 고유번호 = afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9
```

> 📸 **⑥**

## 구간 3 — 적용 전 영향 확인 ★

기능별로 겹치는 파일 수가 나오고, 마지막에 판정이 나옵니다.

```
  종료코드 2    !!  확인 필요 — 담당자가 영향 경로를 검토해야 합니다 (실패 아님)
```

> 📸 **⑦** — **`확인 필요`는 실패가 아닙니다.** 기계가 판단할 수 없어
> 사람에게 넘긴 상태입니다. 통과·실패 두 가지가 아니라 중간 상태를
> 따로 두는 이유를 보여주는 화면입니다.

## 구간 5 — 기능을 하나씩 옮겨 얹기 ★

```
$ git cherry-pick 4df83b311f   # BANK-OM-001
  !!  BANK-OM-001  부딪힌 파일 18개 — 정리 도구를 실행합니다
  OK  BANK-OM-001  되살린 항목 9개
     ⋮
$ git cherry-pick d983f7c540   # BANK-OM-005
  OK  BANK-OM-005  충돌 없음
```

마지막에 요약표가 나옵니다. **아래와 똑같이 나와야 합니다.**

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

> 📸 **⑧** — 요약표 전체
>
> **숫자가 다르면 캡처해서 알려주십시오.** 원격 브랜치가 움직였다는
> 뜻이므로 원인부터 확인해야 합니다.

## 구간 6 — 후보 확인

```
  검사 후보 고유번호 : (실행할 때마다 다른 값)
  OK  옮겨진 변경 기록 수 = 8
  OK  공식 1.13.1 대비 변경 파일 수 = 111
━━ 예행연습 완료 ━━
```

> 📸 **⑨**

---

# 4부 · 남과 같은 결과인지 확인 ★★

여기가 **“내부적으로 해보니 됐어요”와 “누구나 같은 결과가 나옵니다”를
가르는 지점**입니다.

```bash
git -C ~/om-work/upgrade-rehearsal/tree rev-parse HEAD^{tree}
```

**아래 값이 나오면 성공입니다.**

```
e490ed82dd9cfe58833b2050a233aae7496541ab
```

> 📸 **⑩** — 이 화면 하나가 발표 전체의 근거입니다.

## 고유번호가 저와 다른 것은 정상입니다

```bash
cat ~/om-work/upgrade-rehearsal/candidate.txt
```

여기 적힌 `candidate_sha` 는 **실행할 때마다 달라집니다.** 변경 기록 번호에는
만든 시각이 섞여 들어가기 때문입니다.

| | 같아야 하나 | 이유 |
|---|---|---|
| `candidate_sha` (기록 번호) | ✗ 달라도 정상 | 만든 시각이 섞임 |
| `tree` 번호 (파일 내용) | **✓ 같아야 함** | 결과물이 한 글자도 다르지 않음 |

발표에서는 이렇게 말씀하시면 됩니다 —
**“번호는 매번 다르지만 내용은 똑같습니다. 그래서 누가 돌려도 같은 결과입니다.”**

---

# 막혔을 때

| 화면에 나오는 말 | 원인 | 대처 |
|---|---|---|
| `제품 저장소에 커밋하지 않은 변경이 있습니다` | OM_TEMP에 손댄 파일이 있음 | `git -C ~/om-work/OM_TEMP status` 로 확인 후 정리 |
| `검사 저장소 루트에서 실행하십시오` | 폴더를 잘못 잡음 | `cd ~/om-work/openmetadata-test` 후 재실행 |
| `... 이(가) 기대와 다릅니다` | 원격 브랜치가 움직임 | 캡처해서 문의 |
| `python 의존성 부족` | 준비 4단계 안 함 | 4단계 재실행 |
| `... 이(가) 이미 있습니다` | 이전 실행 흔적이 남음 | 아래 정리 명령 |
| `JSON 이외 파일이 부딪혔습니다` | 프로그램 파일이 충돌 | **자동 처리 대상이 아닙니다.** 캡처 후 개발자에게 |
| `... 의 파일 내용을 읽지 못했습니다` | 공식 배포본을 온전히 받지 못함 | 화면에 함께 나오는 `--refetch` 명령을 실행한 뒤 재시도 |

## 다시 돌리기 전 정리

```bash
git -C ~/om-work/OM_TEMP worktree remove --force ~/om-work/upgrade-rehearsal/tree
git -C ~/om-work/OM_TEMP branch -D rehearsal/patch-1.13.1 rehearsal/custom-1.13.1
rm -rf ~/om-work/upgrade-rehearsal
```

---

# 여기까지가 어디까지인가

예행연습이 하는 일은 **검사할 후보 코드를 만드는 데까지**입니다.

| | 상태 |
|---|---|
| 공식 새 버전 위에 기능 7개를 다시 얹기 | 이 문서로 완료 |
| 등록표를 새 코드에 맞추기 | **사람 승인 필요** — 자동화하지 않음 |
| 전체 프로그램 빌드 | 별도 |
| 실제 서버에서 화면·기능 시험 | 별도 |
| 운영 배포 승인 | 별도 |

등록표를 맞추는 절차는 손으로 고치는 것이 금지되어 있고, 반드시
`조사 → 담당자 승인 → 반영` 3단계를 거칩니다. 그래서 이 스크립트에
넣지 않았습니다. 절차는
[`OM_TEMP 검사 전 준비도구 쉬운 사용법`](OM_TEMP_검사전_준비도구_쉬운사용법.md)에
있습니다.

**이 예행연습을 모두 통과해도 배포해도 된다는 뜻이 아닙니다.**
확인한 것은 “코드를 읽어서 알 수 있는 것”까지입니다.
