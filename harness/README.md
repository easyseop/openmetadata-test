# ACGH — OpenMetadata 커스터마이징 자동 검증 도구

> Deterministic CI controls for preserving and validating OpenMetadata
> customizations across upstream upgrades.

행내 커스터마이징이 업스트림 업그레이드에서 **빠짐없이 · 규칙대로 · 재현
가능하게** 새 버전에 올라갔는지를 사람 기억이 아니라 기계가 판정한다. 상세
설계·요구사항은 저장소 루트 문서를 본다(이 README는 **실행 진입점**).

이 도구가 결정적으로 검증하는 것은 **등록·재적용·구조**이고, **업무 동작의
정확성**은 계층 3(테스트)이 담당한다 — 검증기 카탈로그 §0 경계 참조.

## 현재 지원하는 기능 (MVP1 = 케이스 A·B·C·D)

| 영역 | 모듈 | 상태 |
|---|---|---|
| 4상태 판정 엔진(severity 집계·fail-closed) | `acgh/verdict.py` | ✅ |
| 결과계약·CI 어댑터(원자적 write·stale=analysis_error) | `acgh/result_io.py` | ✅ |
| 감사카드(게이트 집계·승인/LLM 분리) | `acgh/evidence.py` | ✅ |
| git 프리미티브(trailer·-z·tree) | `acgh/gitprim.py` | ✅ |
| 경로 소유·glob 문법(공용) | `acgh/layout.py` + `policies/repository-layout.yaml` | ✅ |
| manifest 스키마·의미검증 | `acgh/manifest.py` | ✅ |
| patch-lock(source/application 분리·CAS) | `acgh/patchlock.py`·`acgh/integrator.py` | ✅ |
| 커밋·ID 단위 등록 불변식(P0-5) | `acgh/invariants.py` | ✅ |
| 재적용 탐지/해결 모드 | `acgh/reapply.py`·`acgh/resolve.py` | ✅ |
| clean-room replay | `acgh/replay.py` | ✅ |
| 구현범위 drift(touched/net) | `acgh/drift.py` | ✅ |
| 민감영역·의도 게이트 | `acgh/zones.py` + `policies/sensitive-zones.yaml` | ✅ |
| SHA 결속(repository-qualified inputs) | `acgh/binding.py` | ✅ |
| 최종상태 불변식(counterfactual) | `acgh/finalstate.py` | ✅ |
| 보장범위 표(게이트 출력 결합) | `acgh/scope.py` | ✅ |
| upgrade_watch(케이스 D)·영향분석 | `acgh/upgrade_watch.py`·`acgh/impact.py` | ✅ |
| 정책 노후화 drift | `acgh/policy_drift.py` | ✅ |
| 선언형 verifier(비실행형) | `acgh/verifier.py` | ✅ |

## 아직 지원하지 않는 기능 (MVP2 이후)

- 실행형 verifier(import·스크립트·컨테이너) — **sandbox 러너 필요**(현재 거부→analysis_error).
- contract↔test 결속·patch-kill·업그레이드 차등 테스트(T60/T61/T90).
- 정책 self-approval 차단·digest 승격·내부망 반입(T70/T91/T94).
- 부채 게이트·구조화 diff provider·범용 LLM Memo(T43/T51·52/T80).

## 요구 환경

- Python 3.11, git 2.43+
- 의존: `PyYAML`, `jsonschema>=4.18`, `pathspec>=0.11`

## 설치

```bash
cd harness
pip install jsonschema pathspec pyyaml pytest   # 또는: pip install -e ".[dev]"
```

## 테스트 실행

```bash
cd harness
python -m pytest            # 현재 143개 통과
python -m pytest -q         # 조용히
python -m pytest -q; python -m pytest -q   # 결정성 확인(두 번 동일)
```

실제 OpenMetadata 미러가 없으면 미러 의존 테스트는 **자동 skip**된다(순수
판정 로직 테스트는 미러 없이도 통과). 미러 연결은 아래 참조.

## 실제 OpenMetadata 미러 연결

게이트/재적용/업그레이드 테스트는 **고정 버전의 실제 OM**을 쓴다(합성 더미
금지). 두 고정 태그만 blobless로 가져온다:

```bash
bash fixtures/fetch_upstream.sh    # /home/user/om-mirror 에 생성
# UPSTREAM_A = 1.12.13-release (e6c6650…)
# UPSTREAM_B = 1.13.0-release  (f329dd4…)
```

`tests/conftest.py`가 미러에서 실제 파일 blob을 온디맨드로 가져온다.

## 입력 파일

- **manifest**(커스터마이징 명세): `implementation.allowed/required_changed_paths`,
  `upgrade_watch.paths/configuration_keys/dependencies`, `assurance.contracts/direct_tests`,
  `series`. 스키마: `acgh/schema/manifest.schema.json`. **임의 shell 필드 없음**(P0-8).
- **patch-source-lock**: 고정 40-hex SHA만, series 순서(topological). 스키마:
  `acgh/schema/patch-source-lock.schema.json`.
- **정책**: `policies/repository-layout.yaml`(경로 소유), `policies/sensitive-zones.yaml`(민감영역).

## 출력 파일과 판정 상태

- **acgh-result**(불변 기계 판정): `acgh/schema/acgh-result.schema.json`.
  `result_digest`는 canonical payload의 SHA-256(관측 메타데이터 제외).
- **change-evidence**(감사카드): 게이트 집계 + 승인/LLM **분리** 필드.
- **판정 4상태**: `pass < approval < block < analysis_error`(severity 집계).
  exit: pass=0·block=1·approval=2·analysis_error=3. **분석 실패=차단**(fail-closed).

## 디렉터리 구조

```
harness/
  acgh/            # 구현 모듈(위 표)
    schema/        # JSON Schema(manifest·patch-lock·result·evidence)
  policies/        # repository-layout.yaml · sensitive-zones.yaml
  fixtures/        # fetch_upstream.sh · upstream-lock.yaml
  tests/           # 모듈별 테스트(conftest.py가 실제 미러 제공)
  pyproject.toml
```

## 개발·테스트 규칙

- 게이트/재적용 테스트는 **실제 OM 미러**로(합성 더미 금지). 순수 판정 로직
  단위 테스트는 최소 합성 픽스처 가능.
- 결정성: 같은 입력 → 같은 출력(git 환경 고정, pathspec factory=`gitignore` 고정).
- fail-closed: 검증 불가·미분류·빈 입력은 `analysis_error`(승인 불가).
- 커밋마다 트레일러 규칙 사용(루트 `SESSION_STATE.md` 참조).

## 문제 해결

- `ModuleNotFoundError: jsonschema/pathspec` → `pip install jsonschema pathspec`.
- 미러 의존 테스트가 skip → `bash fixtures/fetch_upstream.sh` 실행 후 재시도.
- 프록시/TLS 오류 → 루트 환경 안내(`/root/.ccr/README.md`) 참조.
