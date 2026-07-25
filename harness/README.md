# ACGH — 하네스 (실행 코드)

OpenMetadata 커스터마이징 자동 검증 도구의 구현.

> **통합 전략:** 기본 운영은 vendor merge이며, 현재 구현된
> `patchlock`·`reapply`·`resolve`·`replay`는 선택 patch-replay 모드다.
> T24~T29 candidate/ancestry/survival/conflict/routing과 실제 7개 등록부까지
> 구현됐고 T25-R은 ancestry 없는 snapshot의 안전한 재구성 계획과 candidate를
> 검증한다. 단, 실제 vendor branch 재구성과 운영 contract test 실행 전에는
> release pass가 아니다.

> **요구사항 충족(영역 A1~A8)·검증기 22종의 왜/안 지키면/방법론·전체 개발 범위·
> 설계 배경은 루트 [`../README.md`](../README.md) 가 정본이다.** 이 파일은 하네스
> 실행에 필요한 최소 정보만 둔다.

## 빠른 시작

```bash
cd harness
pip install jsonschema pathspec pyyaml pytest    # 또는 pip install -e ".[dev]"
python -m pytest                                  # 현재 270개: 235 pass·35 mirror skip
bash fixtures/fetch_upstream.sh                   # 실제 OM 미러(없으면 미러 테스트 자동 skip)
```

Python 3.11 · git 2.43+ · 의존: PyYAML·jsonschema≥4.18·pathspec≥0.11.

## 구현 모듈 (현재 270개 테스트: 235 pass·35 mirror skip)

| 모듈 | 담당 | 루트 README 검증기# / 영역 |
|---|---|---|
| `verdict.py` | 4상태 판정 집계(fail-closed) | 21 / A6 |
| `result_io.py` | 결과계약·CI 어댑터(원자적·stale=analysis_error) | A6 |
| `evidence.py` | 감사카드(승인/LLM 분리) | 22 / A6 |
| `binding.py` | SHA 결속(repo-qualified inputs) | 17 / A6 |
| `candidate.py` | 통합 전략·candidate-lock·결과 입력 결속 | 11 / A2·A3 |
| `ancestry.py` | vendor 공통 이력·승인 target 포함 검증 | 1 / A2 |
| `vendor_rebuild.py` | root snapshot 재구성 계획·공유 hunk 소유·candidate 검증 | 1 / A1·A2 |
| `survival.py`·`registry.py` | active ID 생존·실제 7개 등록 그래프 | 1·14·15 / A1·A2 |
| `conflicts.py`·`routing.py` | merge 해결 증거·vendor/replay 명시 라우팅 | 1 / A2 |
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
| `testruns.py` | 필수 테스트 결과↔candidate/artifact/version 결속 | 14·17 / A6 |
| `fastlane.py`·`breakglass.py` | 변경 유형별 경량 경로·긴급 예외 검증 | 19 / A7 |
| `impact_memo.py` | 근거 기반 LLM Memo·품질지표(판정권 없음) | 22 / A5 |
| `upgrade_run.py` | migration·차등·rollback 12단계 결과 계약 | 18 / A6 |
| `release.py` | 동일 candidate/image/Helm digest 승격 | 20 / A6 |
| `retirement.py` | active→retired 증거·상태 전환 | 3·4 / A1·A3 |
| `airgap.py` | 내부망 파일 해시·release-lock·오프라인 서명 재검증 | 20 / A6 |

입력(manifest·patch-source-lock·정책 YAML)·출력(acgh-result·change-evidence)·판정
4상태 상세는 루트 README '개발자 빠른 시작' 참조.

## T25-R vendor 재구성

`--repo`에는 공식 target과 root snapshot의 두 고정 commit object가 모두 있어야
한다. `plan`은 실제 tree diff가 등록한 113개 경로와 같은지 확인하고 결정적 JSON
계획을 출력한다.

```bash
acgh-vendor-rebuild \
  --repo /path/to/object-complete-repo \
  --registration registrations/kb-openmetadata \
  plan
```

실제 고정 Git 객체에서 source plan이 통과했으며 결과는 67개 단독 소유, 44개
공유 파일, 2개 제외 경로다. 공유 파일의 실제 symbol·JSON key·route·SQL block을
검사해 `registrations/kb-openmetadata/shared-path-owners.yaml`에 owner를
기록했다.

```bash
acgh-vendor-rebuild \
  --repo /path/to/object-complete-repo \
  --registration registrations/kb-openmetadata \
  verify \
  --candidate <full-candidate-sha> \
  --shared-owners registrations/kb-openmetadata/shared-path-owners.yaml
```

검증기는 candidate가 공식 target에서 시작했는지, unrelated snapshot commit을
merge하지 않았는지, commit마다 ID가 정확히 하나인지, 경로 소유가 맞는지,
registered JSON의 최종 의미 값과 나머지 파일 내용은 snapshot과 같은지, 제외
경로는 upstream 그대로인지 확인한다.

## 디렉터리

```
harness/
  acgh/            # 구현 모듈(위 표)
    schema/        # 모든 입력·결과·attestation·release/transfer JSON Schema
  registrations/   # 실제 kb_openmetadata 7개 manifest·contract·registry
  policies/        # repository-layout.yaml · sensitive-zones.yaml
  fixtures/        # fetch_upstream.sh · upstream-lock.yaml
  tests/           # 모듈별 테스트(conftest.py가 실제 미러 제공)
  pyproject.toml
```

## 문제 해결

- `ModuleNotFoundError: jsonschema/pathspec` → `pip install jsonschema pathspec`.
- 미러 의존 테스트가 skip → `bash fixtures/fetch_upstream.sh` 실행 후 재시도.
- 프록시/TLS 오류 → `/root/.ccr/README.md` 참조.
