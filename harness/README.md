# ACGH — 하네스 (실행 코드)

OpenMetadata 커스터마이징 자동 검증 도구의 구현.

> **통합 전략:** 기본 운영은 vendor merge이며, 현재 구현된
> `patchlock`·`reapply`·`resolve`·`replay`는 선택 patch-replay 모드다.
> T24 candidate-lock과 T25 vendor ancestry gate는 구현됐고, customization
> 생존·실제 등록 게이트는 ADR-001의 T26~T29로 추가 개발한다.

> **요구사항 충족(영역 A1~A8)·검증기 22종의 왜/안 지키면/방법론·전체 개발 범위·
> 설계 배경은 루트 [`../README.md`](../README.md) 가 정본이다.** 이 파일은 하네스
> 실행에 필요한 최소 정보만 둔다.

## 빠른 시작

```bash
cd harness
pip install jsonschema pathspec pyyaml pytest    # 또는 pip install -e ".[dev]"
python -m pytest                                  # 현재 183개: 148 pass·35 mirror skip
bash fixtures/fetch_upstream.sh                   # 실제 OM 미러(없으면 미러 테스트 자동 skip)
```

Python 3.11 · git 2.43+ · 의존: PyYAML·jsonschema≥4.18·pathspec≥0.11.

## 구현 모듈 (현재 183개 테스트: 148 pass·35 mirror skip)

| 모듈 | 담당 | 루트 README 검증기# / 영역 |
|---|---|---|
| `verdict.py` | 4상태 판정 집계(fail-closed) | 21 / A6 |
| `result_io.py` | 결과계약·CI 어댑터(원자적·stale=analysis_error) | A6 |
| `evidence.py` | 감사카드(승인/LLM 분리) | 22 / A6 |
| `binding.py` | SHA 결속(repo-qualified inputs) | 17 / A6 |
| `candidate.py` | 통합 전략·candidate-lock·결과 입력 결속 | 11 / A2·A3 |
| `ancestry.py` | vendor 공통 이력·승인 target 포함 검증 | 1 / A2 |
| `gitprim.py` | git 프리미티브(trailer·-z·tree) | — |
| `layout.py` | 경로 소유·glob 문법(공용) | 6·7 / A4 |
| `manifest.py` | manifest 스키마·의미검증 | 12 / A1 |
| `patchlock.py`·`integrator.py` | patch-lock(분리·CAS) | 11 / A3 |
| `invariants.py` | 커밋·ID 등록 검사 | 2·3 / A1 |
| `reapply.py`·`resolve.py` | 재적용 탐지/해결 2모드 | 1 / A2 |
| `replay.py` | clean-room replay | 5 / A3 |
| `drift.py` | 구현범위 drift(touched/net) | 6 / A4 |
| `zones.py` | 민감영역·의도 게이트 | 7 / A4 |
| `finalstate.py` | 최종상태 불변식(counterfactual) | 4 / A3 |
| `scope.py` | 보장범위 표(게이트 출력 결합) | — |
| `upgrade_watch.py`·`impact.py` | upgrade_watch(케이스 D)·영향분석 | 9·22 / A5 |
| `policy_drift.py` | 정책 노후화 drift | 8 / A5 |
| `verifier.py` | 선언형 verifier(비실행형) | 12 / A4 |

입력(manifest·patch-source-lock·정책 YAML)·출력(acgh-result·change-evidence)·판정
4상태 상세는 루트 README '개발자 빠른 시작' 참조.

## 디렉터리

```
harness/
  acgh/            # 구현 모듈(위 표)
    schema/        # JSON Schema(manifest·candidate-lock·patch-lock·result·evidence)
  policies/        # repository-layout.yaml · sensitive-zones.yaml
  fixtures/        # fetch_upstream.sh · upstream-lock.yaml
  tests/           # 모듈별 테스트(conftest.py가 실제 미러 제공)
  pyproject.toml
```

## 문제 해결

- `ModuleNotFoundError: jsonschema/pathspec` → `pip install jsonschema pathspec`.
- 미러 의존 테스트가 skip → `bash fixtures/fetch_upstream.sh` 실행 후 재시도.
- 프록시/TLS 오류 → `/root/.ccr/README.md` 참조.
