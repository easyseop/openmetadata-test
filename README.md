# kb-datacatalog-upgrade-checker

OpenMetadata(데이터카탈로그) 커스터마이징 버전업 검증 검사기 — `/om-plan` 실행 저장소.

- `.gitlab-ci.yml` — 보호된 om-plan 파이프라인 (preflight → intent-review → proposal → validate)
- `harness/acgh/plancore/` — 범용 계획 검증 엔진 (제품 무관)
- `harness/acgh/integrations/om/` — OpenMetadata 어댑터
- `harness/acgh/{verdict,gitprim,binding}.py` — 공용 기반 (판정·Git 원시·pin)
- `harness/ci/` — 신뢰 검사기 준비·CI 진입점
- `harness/registrations/om-temp-1.13.1/` — 활성 등록자료 (Registry·Manifest·Contract·정책)
- `tests/bank/contracts/` — 기능별 계약 테스트 (후속 검증 단계에서 실행)
- `harness/tests/` — 검사기 자체 반례 테스트
- `.github/workflows/` — 폐기된 GitHub CI (참조 보존, GitLab이 정본)

## 출처 (clean export)

개발 작업장 `github.com/easyseop/openmetadata-test`
커밋 `2688e6758bc0c67d7ac1cfbd3d7c5017b7ebae17` (채택 구현 `ef48a8e` 포함)에서
**파이프라인이 실제로 참조하는 것만**(import 폐쇄집합 + 활성 등록자료 + 계약 테스트)
추려 새 이력으로 시작했다. 구식 검사 모듈·과거 등록자료·개발 문서·evidence는
작업장 GitHub과 `github.com/easyseop/om-skill-develop`(설계 히스토리)에 보존한다.
