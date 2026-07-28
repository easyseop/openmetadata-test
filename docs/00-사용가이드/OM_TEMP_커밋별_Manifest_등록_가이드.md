# OM_TEMP 커밋별 Manifest 등록 가이드

> 대상 코드: `easyseop/OM_TEMP`의 `custom/om-1.13.0`
> Manifest 위치: `easyseop/openmetadata-test/harness/registrations/om-temp-1.13.0/manifests/`

## 이 자료가 필요한 이유

OpenMetadata를 업그레이드한 뒤에도 각 커스터마이징이 빠지지 않았는지 검사하려면, 실제 코드 변경과 검사 기준을 BANK-OM 기능별로 연결해야 합니다. 이 자료는 실제 Git commit에서 확인한 변경 파일을 어떤 Manifest에 등록했는지 보여줍니다.

## 먼저 구분할 두 식별값

| 이름 | 의미 | 이 문서에서의 예 |
|---|---|---|
| BANK-OM ID | 사람이 발급하는 업무 기능 번호 | `BANK-OM-005` |
| Git commit SHA | Git이 한 번의 코드 저장에 자동 부여하는 값 | `d983f7c...` |

Manifest는 **BANK-OM ID마다 한 파일**을 만듭니다. 같은 기능을 후속 보완하면 BANK-OM-007처럼 Git commit SHA는 여러 개가 될 수 있지만 Manifest는 하나입니다.

## 이 자료를 보는 순서

1. 상위 펼치기에서 BANK-OM 기능을 선택합니다.
2. 강조 캡처에서 Git commit SHA, 커밋 제목, Customization-ID를 확인합니다.
3. 기능 단위로 묶은 이유를 읽습니다.
4. 하위 펼치기에서 원본 캡처와 현재 생성된 Manifest 초안 전체를 확인합니다.

강조 캡처는 위치를 빠르게 찾기 위한 **설명용 사본**입니다. GitHub 화면 자체를 확인해야 할 때는 같은 항목의 **원본 캡처** 또는 GitHub commit 링크를 사용합니다.

## 실제 커밋과 Manifest

<details>
<summary><strong>BANK-OM-001 · 기준코드(InstanceCode)</strong></summary>

### 실제 GitHub 커밋

- Git commit SHA: `4df83b311f1ec38156c9b992f34607b22224db85`
- 커밋 제목: `add InstanceCode customization`
- 이 커밋에서 변경한 파일: 48개
- [GitHub에서 실제 커밋 열기](https://github.com/easyseop/OM_TEMP/commit/4df83b311f1ec38156c9b992f34607b22224db85)

![BANK-OM-001 커밋 강조 캡처](공유문서/assets/om-temp-manifest/commit-messages/001-instance-code-highlighted.png)

<details>
<summary>강조 표시가 없는 원본 캡처 보기</summary>

![BANK-OM-001 커밋 원본 캡처](공유문서/assets/om-temp-manifest/commit-messages/001-instance-code-original.png)

</details>

### 왜 하나의 BANK-OM 기능으로 보았나

InstanceCode라는 새 데이터 유형을 정의하고, 저장·검색·API·화면 연결까지 한 번에 추가한 변경입니다. 파일은 여러 개지만 모두 InstanceCode 기능을 동작시키기 위한 한 묶음이므로 BANK-OM-001 하나로 관리합니다.

<details>
<summary><strong>BANK-OM-001 Manifest 초안 전체 보기</strong></summary>

```yaml
schema_version: 1
customization_id: BANK-OM-001
status: active
kind: core-patch
title: 기준코드(InstanceCode)
implementation:
  allowed_changed_paths:
  - bootstrap/sql/migrations/native/1.13.0/mysql/schemaChanges.sql
  - bootstrap/sql/migrations/native/1.13.0/postgres/schemaChanges.sql
  - openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
  - openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/CollectionDAO.java
  - openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/InstanceCodeRepository.java
  - openmetadata-service/src/main/java/org/openmetadata/service/resources/instancecode/InstanceCodeMapper.java
  - openmetadata-service/src/main/java/org/openmetadata/service/resources/instancecode/InstanceCodeResource.java
  - openmetadata-service/src/main/java/org/openmetadata/service/search/SearchIndexFactory.java
  - openmetadata-service/src/main/java/org/openmetadata/service/search/indexes/InstanceCodeIndex.java
  - openmetadata-spec/src/main/resources/elasticsearch/en/instance_code_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/indexMapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/jp/instance_code_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/ru/instance_code_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/zh/instance_code_index_mapping.json
  - openmetadata-spec/src/main/resources/json/schema/api/data/createInstanceCode.json
  - openmetadata-spec/src/main/resources/json/schema/entity/data/instanceCode.json
  - openmetadata-ui/src/main/resources/ui/src/components/AppRouter/AuthenticatedAppRouter.tsx
  - openmetadata-ui/src/main/resources/ui/src/components/InstanceCode/InstanceCodeListPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/constants/constants.ts
  - openmetadata-ui/src/main/resources/ui/src/context/PermissionProvider/PermissionProvider.interface.ts
  - openmetadata-ui/src/main/resources/ui/src/enums/Explore.enum.ts
  - openmetadata-ui/src/main/resources/ui/src/enums/entity.enum.ts
  - openmetadata-ui/src/main/resources/ui/src/enums/search.enum.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/api/data/createInstanceCode.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/data/instanceCode.ts
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ar-sa.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/de-de.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/en-us.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/es-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/fr-fr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/gl-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/he-he.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ja-jp.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/mr-in.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/nl-nl.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pr-pr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-br.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-pt.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ru-ru.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/th-th.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/tr-tr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-cn.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-tw.json
  - openmetadata-ui/src/main/resources/ui/src/pages/InstanceCodeDetailsPage/InstanceCodeDetailsPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/pages/InstanceCodeGroupDetailsPage/InstanceCodeGroupDetailsPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/rest/instanceCodeAPI.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/RouterUtils.ts
  required_changed_paths:
  - openmetadata-service/src/main/java/org/openmetadata/service/resources/instancecode/InstanceCodeResource.java
  - openmetadata-spec/src/main/resources/json/schema/entity/data/instanceCode.json
upgrade_watch:
  paths:
  - bootstrap/sql/migrations/native/1.13.0/mysql/schemaChanges.sql
  - bootstrap/sql/migrations/native/1.13.0/postgres/schemaChanges.sql
  - openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
  - openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/CollectionDAO.java
  - openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/InstanceCodeRepository.java
  - openmetadata-service/src/main/java/org/openmetadata/service/resources/instancecode/InstanceCodeMapper.java
  - openmetadata-service/src/main/java/org/openmetadata/service/resources/instancecode/InstanceCodeResource.java
  - openmetadata-service/src/main/java/org/openmetadata/service/search/SearchIndexFactory.java
  - openmetadata-service/src/main/java/org/openmetadata/service/search/indexes/InstanceCodeIndex.java
  - openmetadata-spec/src/main/resources/elasticsearch/en/instance_code_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/indexMapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/jp/instance_code_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/ru/instance_code_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/zh/instance_code_index_mapping.json
  - openmetadata-spec/src/main/resources/json/schema/api/data/createInstanceCode.json
  - openmetadata-spec/src/main/resources/json/schema/entity/data/instanceCode.json
  - openmetadata-ui/src/main/resources/ui/src/components/AppRouter/AuthenticatedAppRouter.tsx
  - openmetadata-ui/src/main/resources/ui/src/components/InstanceCode/InstanceCodeListPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/constants/constants.ts
  - openmetadata-ui/src/main/resources/ui/src/context/PermissionProvider/PermissionProvider.interface.ts
  - openmetadata-ui/src/main/resources/ui/src/enums/Explore.enum.ts
  - openmetadata-ui/src/main/resources/ui/src/enums/entity.enum.ts
  - openmetadata-ui/src/main/resources/ui/src/enums/search.enum.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/api/data/createInstanceCode.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/data/instanceCode.ts
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ar-sa.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/de-de.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/en-us.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/es-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/fr-fr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/gl-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/he-he.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ja-jp.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/mr-in.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/nl-nl.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pr-pr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-br.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-pt.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ru-ru.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/th-th.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/tr-tr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-cn.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-tw.json
  - openmetadata-ui/src/main/resources/ui/src/pages/InstanceCodeDetailsPage/InstanceCodeDetailsPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/pages/InstanceCodeGroupDetailsPage/InstanceCodeGroupDetailsPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/rest/instanceCodeAPI.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/RouterUtils.ts
assurance:
  contracts:
  - CONTRACT-INSTANCE-CODE
  direct_tests: []
series:
  allowed: false
  depends_on: []
```

</details>

</details>

<details>
<summary><strong>BANK-OM-002 · 쿼리 리포트(QueryReport)</strong></summary>

### 실제 GitHub 커밋

- Git commit SHA: `68ebed4801715f0c30b8a1a614572183fa6097b8`
- 커밋 제목: `add QueryReport customization`
- 이 커밋에서 변경한 파일: 55개
- [GitHub에서 실제 커밋 열기](https://github.com/easyseop/OM_TEMP/commit/68ebed4801715f0c30b8a1a614572183fa6097b8)

![BANK-OM-002 커밋 강조 캡처](공유문서/assets/om-temp-manifest/commit-messages/002-query-report-highlighted.png)

<details>
<summary>강조 표시가 없는 원본 캡처 보기</summary>

![BANK-OM-002 커밋 원본 캡처](공유문서/assets/om-temp-manifest/commit-messages/002-query-report-original.png)

</details>

### 왜 하나의 BANK-OM 기능으로 보았나

QueryReport 데이터 유형, 저장소, API, 검색과 화면 연결을 함께 추가한 변경입니다. BANK-OM-001과 같은 공용 파일도 수정하지만, diff 안의 QUERY_REPORT 연결은 별도 업무 기능이므로 BANK-OM-002로 분리합니다.

<details>
<summary><strong>BANK-OM-002 Manifest 초안 전체 보기</strong></summary>

```yaml
schema_version: 1
customization_id: BANK-OM-002
status: active
kind: core-patch
title: 쿼리 리포트(QueryReport)
implementation:
  allowed_changed_paths:
  - bootstrap/sql/migrations/native/1.13.0/mysql/schemaChanges.sql
  - bootstrap/sql/migrations/native/1.13.0/postgres/schemaChanges.sql
  - openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
  - openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/CollectionDAO.java
  - openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/QueryReportRepository.java
  - openmetadata-service/src/main/java/org/openmetadata/service/resources/queryreport/QueryReportMapper.java
  - openmetadata-service/src/main/java/org/openmetadata/service/resources/queryreport/QueryReportResource.java
  - openmetadata-service/src/main/java/org/openmetadata/service/search/SearchIndexFactory.java
  - openmetadata-service/src/main/java/org/openmetadata/service/search/indexes/QueryReportIndex.java
  - openmetadata-spec/src/main/resources/elasticsearch/en/query_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/en/query_report_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/indexMapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/jp/query_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/jp/query_report_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/ru/query_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/ru/query_report_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/zh/query_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/zh/query_report_index_mapping.json
  - openmetadata-spec/src/main/resources/json/schema/api/data/createQueryReport.json
  - openmetadata-spec/src/main/resources/json/schema/entity/data/queryReport.json
  - openmetadata-ui/src/main/resources/ui/src/components/AppRouter/AuthenticatedAppRouter.tsx
  - openmetadata-ui/src/main/resources/ui/src/components/QueryReport/QueryReportListPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/components/QueryReport/QueryReportQueryEditor/QueryReportQueryEditor.component.tsx
  - openmetadata-ui/src/main/resources/ui/src/constants/constants.ts
  - openmetadata-ui/src/main/resources/ui/src/context/PermissionProvider/PermissionProvider.interface.ts
  - openmetadata-ui/src/main/resources/ui/src/enums/Explore.enum.ts
  - openmetadata-ui/src/main/resources/ui/src/enums/entity.enum.ts
  - openmetadata-ui/src/main/resources/ui/src/enums/search.enum.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/api/data/createQueryReport.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/data/queryReport.ts
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ar-sa.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/de-de.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/en-us.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/es-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/fr-fr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/gl-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/he-he.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ja-jp.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/mr-in.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/nl-nl.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pr-pr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-br.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-pt.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ru-ru.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/th-th.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/tr-tr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-cn.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-tw.json
  - openmetadata-ui/src/main/resources/ui/src/pages/QueryReportDetailsPage/QueryReportDetailsPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/pages/QueryReportYearDetailsPage/QueryReportYearDetailsPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/rest/queryAPI.ts
  - openmetadata-ui/src/main/resources/ui/src/rest/queryReportAPI.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/QueryReportUtils.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/RouterUtils.ts
  required_changed_paths:
  - openmetadata-service/src/main/java/org/openmetadata/service/resources/queryreport/QueryReportResource.java
  - openmetadata-spec/src/main/resources/json/schema/entity/data/queryReport.json
upgrade_watch:
  paths:
  - bootstrap/sql/migrations/native/1.13.0/mysql/schemaChanges.sql
  - bootstrap/sql/migrations/native/1.13.0/postgres/schemaChanges.sql
  - openmetadata-service/src/main/java/org/openmetadata/service/Entity.java
  - openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/CollectionDAO.java
  - openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/QueryReportRepository.java
  - openmetadata-service/src/main/java/org/openmetadata/service/jdbi3/QueryRepository.java
  - openmetadata-service/src/main/java/org/openmetadata/service/resources/queryreport/QueryReportMapper.java
  - openmetadata-service/src/main/java/org/openmetadata/service/resources/queryreport/QueryReportResource.java
  - openmetadata-service/src/main/java/org/openmetadata/service/search/SearchIndexFactory.java
  - openmetadata-service/src/main/java/org/openmetadata/service/search/indexes/QueryReportIndex.java
  - openmetadata-spec/src/main/resources/elasticsearch/en/query_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/en/query_report_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/indexMapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/jp/query_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/jp/query_report_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/ru/query_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/ru/query_report_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/zh/query_index_mapping.json
  - openmetadata-spec/src/main/resources/elasticsearch/zh/query_report_index_mapping.json
  - openmetadata-spec/src/main/resources/json/schema/api/data/createQueryReport.json
  - openmetadata-spec/src/main/resources/json/schema/entity/data/queryReport.json
  - openmetadata-ui/src/main/resources/ui/src/components/AppRouter/AuthenticatedAppRouter.tsx
  - openmetadata-ui/src/main/resources/ui/src/components/QueryReport/QueryReportListPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/components/QueryReport/QueryReportQueryEditor/QueryReportQueryEditor.component.tsx
  - openmetadata-ui/src/main/resources/ui/src/constants/constants.ts
  - openmetadata-ui/src/main/resources/ui/src/context/PermissionProvider/PermissionProvider.interface.ts
  - openmetadata-ui/src/main/resources/ui/src/enums/Explore.enum.ts
  - openmetadata-ui/src/main/resources/ui/src/enums/entity.enum.ts
  - openmetadata-ui/src/main/resources/ui/src/enums/search.enum.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/api/data/createQueryReport.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/data/queryReport.ts
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ar-sa.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/de-de.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/en-us.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/es-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/fr-fr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/gl-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/he-he.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ja-jp.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/mr-in.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/nl-nl.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pr-pr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-br.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-pt.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ru-ru.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/th-th.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/tr-tr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-cn.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-tw.json
  - openmetadata-ui/src/main/resources/ui/src/pages/QueryReportDetailsPage/QueryReportDetailsPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/pages/QueryReportYearDetailsPage/QueryReportYearDetailsPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/rest/queryAPI.ts
  - openmetadata-ui/src/main/resources/ui/src/rest/queryReportAPI.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/QueryReportUtils.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/RouterUtils.ts
assurance:
  contracts:
  - CONTRACT-QUERY-REPORT
  direct_tests: []
series:
  allowed: false
  depends_on: []
```

</details>

</details>

<details>
<summary><strong>BANK-OM-003 · 데이터 검증 결과(Data Assertions)</strong></summary>

### 실제 GitHub 커밋

- Git commit SHA: `57ee1b3b23d644f13e0c1716f0810ddf962e5264`
- 커밋 제목: `add Data Assertions customization`
- 이 커밋에서 변경한 파일: 25개
- [GitHub에서 실제 커밋 열기](https://github.com/easyseop/OM_TEMP/commit/57ee1b3b23d644f13e0c1716f0810ddf962e5264)

![BANK-OM-003 커밋 강조 캡처](공유문서/assets/om-temp-manifest/commit-messages/003-data-assertions-highlighted.png)

<details>
<summary>강조 표시가 없는 원본 캡처 보기</summary>

![BANK-OM-003 커밋 원본 캡처](공유문서/assets/om-temp-manifest/commit-messages/003-data-assertions-original.png)

</details>

### 왜 하나의 BANK-OM 기능으로 보았나

데이터 검증 결과를 조회하는 전용 화면, API 호출, 경로와 메뉴를 함께 추가한 변경입니다. 이 화면 흐름을 한 기능으로 보고 BANK-OM-003으로 등록합니다.

<details>
<summary><strong>BANK-OM-003 Manifest 초안 전체 보기</strong></summary>

```yaml
schema_version: 1
customization_id: BANK-OM-003
status: active
kind: core-patch
title: 데이터 검증 결과(Data Assertions)
implementation:
  allowed_changed_paths:
  - openmetadata-ui/src/main/resources/ui/src/components/AppRouter/AuthenticatedAppRouter.tsx
  - openmetadata-ui/src/main/resources/ui/src/components/MyData/MyDataFailedAssertions/MyDataFailedAssertions.component.tsx
  - openmetadata-ui/src/main/resources/ui/src/constants/constants.ts
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ar-sa.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/de-de.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/en-us.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/es-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/fr-fr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/gl-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/he-he.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ja-jp.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/mr-in.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/nl-nl.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pr-pr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-br.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-pt.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ru-ru.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/th-th.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/tr-tr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-cn.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-tw.json
  - openmetadata-ui/src/main/resources/ui/src/pages/DataAssertionsPage/DataAssertionsPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/pages/MyDataPage/MyDataPage.component.tsx
  - openmetadata-ui/src/main/resources/ui/src/rest/dataAssertionsAPI.ts
  required_changed_paths:
  - openmetadata-ui/src/main/resources/ui/src/pages/DataAssertionsPage/DataAssertionsPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/rest/dataAssertionsAPI.ts
upgrade_watch:
  paths:
  - openmetadata-spec/src/main/resources/json/schema/tests/testCase.json
  - openmetadata-ui/src/main/resources/ui/src/components/AppRouter/AuthenticatedAppRouter.tsx
  - openmetadata-ui/src/main/resources/ui/src/components/MyData/MyDataFailedAssertions/MyDataFailedAssertions.component.tsx
  - openmetadata-ui/src/main/resources/ui/src/constants/constants.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/tests/testCase.ts
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ar-sa.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/de-de.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/en-us.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/es-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/fr-fr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/gl-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/he-he.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ja-jp.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/mr-in.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/nl-nl.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pr-pr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-br.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-pt.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ru-ru.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/th-th.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/tr-tr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-cn.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-tw.json
  - openmetadata-ui/src/main/resources/ui/src/pages/DataAssertionsPage/DataAssertionsPage.tsx
  - openmetadata-ui/src/main/resources/ui/src/pages/MyDataPage/MyDataPage.component.tsx
  - openmetadata-ui/src/main/resources/ui/src/rest/dataAssertionsAPI.ts
assurance:
  contracts:
  - CONTRACT-DATA-ASSERTIONS
  direct_tests: []
series:
  allowed: false
  depends_on: []
```

</details>

</details>

<details>
<summary><strong>BANK-OM-004 · 은행 컬럼 확장 표시</strong></summary>

### 실제 GitHub 커밋

- Git commit SHA: `274f2b79b424e01537a7f2253c33aeecb43aaac4`
- 커밋 제목: `add bank column view customization`
- 이 커밋에서 변경한 파일: 33개
- [GitHub에서 실제 커밋 열기](https://github.com/easyseop/OM_TEMP/commit/274f2b79b424e01537a7f2253c33aeecb43aaac4)

![BANK-OM-004 커밋 강조 캡처](공유문서/assets/om-temp-manifest/commit-messages/004-bank-column-view-highlighted.png)

<details>
<summary>강조 표시가 없는 원본 캡처 보기</summary>

![BANK-OM-004 커밋 원본 캡처](공유문서/assets/om-temp-manifest/commit-messages/004-bank-column-view-original.png)

</details>

### 왜 하나의 BANK-OM 기능으로 보았나

테이블 컬럼 화면에 은행용 표시 항목과 관련 타입·문구를 추가한 변경입니다. 화면에 보이는 결과와 이를 전달하는 타입 변경을 함께 BANK-OM-004로 관리합니다.

<details>
<summary><strong>BANK-OM-004 Manifest 초안 전체 보기</strong></summary>

```yaml
schema_version: 1
customization_id: BANK-OM-004
status: active
kind: core-patch
title: 은행 컬럼 확장 표시
implementation:
  allowed_changed_paths:
  - openmetadata-ui/src/main/resources/ui/src/components/DataAssetSummaryPanelV1/DataAssetSummaryPanelV1.tsx
  - openmetadata-ui/src/main/resources/ui/src/components/Database/SchemaTable/SchemaTable.component.tsx
  - openmetadata-ui/src/main/resources/ui/src/components/Explore/ExploreTree/ExploreTree.tsx
  - openmetadata-ui/src/main/resources/ui/src/components/SearchedData/SearchedData.tsx
  - openmetadata-ui/src/main/resources/ui/src/constants/TableKeys.constants.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/data/database.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/data/databaseSchema.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/data/storedProcedure.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/data/table.ts
  - openmetadata-ui/src/main/resources/ui/src/interface/search.interface.ts
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ar-sa.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/de-de.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/en-us.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/es-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/fr-fr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/gl-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/he-he.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ja-jp.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/mr-in.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/nl-nl.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pr-pr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-br.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-pt.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ru-ru.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/th-th.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/tr-tr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-cn.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-tw.json
  - openmetadata-ui/src/main/resources/ui/src/utils/EntityUtilClassBase.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/EntityUtils.interface.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/EntityUtils.tsx
  - openmetadata-ui/src/main/resources/ui/src/utils/SearchClassBase.ts
  required_changed_paths:
  - openmetadata-ui/src/main/resources/ui/src/components/Database/SchemaTable/SchemaTable.component.tsx
upgrade_watch:
  paths:
  - openmetadata-spec/src/main/resources/json/schema/entity/data/table.json
  - openmetadata-ui/src/main/resources/ui/src/components/DataAssetSummaryPanelV1/DataAssetSummaryPanelV1.tsx
  - openmetadata-ui/src/main/resources/ui/src/components/Database/SchemaTable/SchemaTable.component.tsx
  - openmetadata-ui/src/main/resources/ui/src/components/Explore/ExploreTree/ExploreTree.tsx
  - openmetadata-ui/src/main/resources/ui/src/components/SearchedData/SearchedData.tsx
  - openmetadata-ui/src/main/resources/ui/src/constants/TableKeys.constants.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/data/database.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/data/databaseSchema.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/data/storedProcedure.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/data/table.ts
  - openmetadata-ui/src/main/resources/ui/src/interface/search.interface.ts
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ar-sa.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/de-de.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/en-us.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/es-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/fr-fr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/gl-es.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/he-he.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ja-jp.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ko-kr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/mr-in.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/nl-nl.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pr-pr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-br.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/pt-pt.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/ru-ru.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/th-th.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/tr-tr.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-cn.json
  - openmetadata-ui/src/main/resources/ui/src/locale/languages/zh-tw.json
  - openmetadata-ui/src/main/resources/ui/src/utils/EntityUtilClassBase.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/EntityUtils.interface.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/EntityUtils.tsx
  - openmetadata-ui/src/main/resources/ui/src/utils/SearchClassBase.ts
assurance:
  contracts:
  - CONTRACT-BANK-COLUMN-VIEW
  direct_tests: []
series:
  allowed: false
  depends_on: []
```

</details>

</details>

<details>
<summary><strong>BANK-OM-005 · 한글 입력 조합 보정</strong></summary>

### 실제 GitHub 커밋

- Git commit SHA: `d983f7c540d3fa1fe56ca91adef3f37374890f77`
- 커밋 제목: `fix Korean IME handling`
- 이 커밋에서 변경한 파일: 1개
- [GitHub에서 실제 커밋 열기](https://github.com/easyseop/OM_TEMP/commit/d983f7c540d3fa1fe56ca91adef3f37374890f77)

![BANK-OM-005 커밋 강조 캡처](공유문서/assets/om-temp-manifest/commit-messages/005-korean-ime-highlighted.png)

<details>
<summary>강조 표시가 없는 원본 캡처 보기</summary>

![BANK-OM-005 커밋 원본 캡처](공유문서/assets/om-temp-manifest/commit-messages/005-korean-ime-original.png)

</details>

### 왜 하나의 BANK-OM 기능으로 보았나

SchemaEditor.tsx 한 파일에서 한글 조합 시작·종료 처리를 추가한 변경입니다. 변경 범위가 가장 작고 기능 경계도 분명해, 실제 diff 전체가 Manifest 하나로 등록되는 대표 사례로 사용합니다.

<details>
<summary><strong>대표 사례: 변경 코드 전체 보기</strong></summary>

이 커밋의 변경은 `SchemaEditor.tsx` 한 파일뿐입니다. 아래 네 장은 한 GitHub diff 화면을 위에서 아래 순서로 나눈 것으로, 초록색 줄은 추가 코드이고 빨간색 줄은 삭제 코드입니다.

#### 전체 diff 1/4

![BANK-OM-005 전체 diff 1/4](공유문서/assets/om-temp-manifest/bank-om-005-full-diff/005-korean-ime-diff-part-1.png)

#### 전체 diff 2/4

![BANK-OM-005 전체 diff 2/4](공유문서/assets/om-temp-manifest/bank-om-005-full-diff/005-korean-ime-diff-part-2.png)

#### 전체 diff 3/4

![BANK-OM-005 전체 diff 3/4](공유문서/assets/om-temp-manifest/bank-om-005-full-diff/005-korean-ime-diff-part-3.png)

#### 전체 diff 4/4

![BANK-OM-005 전체 diff 4/4](공유문서/assets/om-temp-manifest/bank-om-005-full-diff/005-korean-ime-diff-part-4.png)

이 전체 diff에서 바뀐 파일 경로는 하나이므로 Manifest의 `allowed_changed_paths`도 한 경로입니다. 같은 파일이 한글 입력 보정의 핵심 구현이므로 `required_changed_paths`에도 같은 경로를 등록했습니다.

</details>

<details>
<summary><strong>BANK-OM-005 Manifest 초안 전체 보기</strong></summary>

```yaml
schema_version: 1
customization_id: BANK-OM-005
status: active
kind: core-patch
title: 한글 입력 조합 보정
implementation:
  allowed_changed_paths:
  - openmetadata-ui/src/main/resources/ui/src/components/Database/SchemaEditor/SchemaEditor.tsx
  required_changed_paths:
  - openmetadata-ui/src/main/resources/ui/src/components/Database/SchemaEditor/SchemaEditor.tsx
upgrade_watch:
  paths:
  - openmetadata-ui/src/main/resources/ui/package.json
  - openmetadata-ui/src/main/resources/ui/src/components/Database/SchemaEditor/SchemaEditor.tsx
assurance:
  contracts:
  - CONTRACT-KOREAN-IME
  direct_tests: []
series:
  allowed: false
  depends_on: []
```

</details>

</details>

<details>
<summary><strong>BANK-OM-006 · Sybase 연결 유형</strong></summary>

### 실제 GitHub 커밋

- Git commit SHA: `010750c514e9bbb7a765414ded3b161b1f5eb621`
- 커밋 제목: `add Sybase customization`
- 이 커밋에서 변경한 파일: 18개
- [GitHub에서 실제 커밋 열기](https://github.com/easyseop/OM_TEMP/commit/010750c514e9bbb7a765414ded3b161b1f5eb621)

![BANK-OM-006 커밋 강조 캡처](공유문서/assets/om-temp-manifest/commit-messages/006-sybase-highlighted.png)

<details>
<summary>강조 표시가 없는 원본 캡처 보기</summary>

![BANK-OM-006 커밋 원본 캡처](공유문서/assets/om-temp-manifest/commit-messages/006-sybase-original.png)

</details>

### 왜 하나의 BANK-OM 기능으로 보았나

Sybase 연결 스키마, 생성 타입, 아이콘과 연결 선택 로직을 함께 추가한 변경입니다. 하나의 DB 연결 유형을 완성하는 파일들을 BANK-OM-006으로 묶습니다.

<details>
<summary><strong>BANK-OM-006 Manifest 초안 전체 보기</strong></summary>

```yaml
schema_version: 1
customization_id: BANK-OM-006
status: active
kind: core-patch
title: Sybase 연결 유형
implementation:
  allowed_changed_paths:
  - openmetadata-spec/src/main/resources/json/schema/entity/services/connections/database/sybaseConnection.json
  - openmetadata-spec/src/main/resources/json/schema/entity/services/databaseService.json
  - openmetadata-ui/src/main/resources/ui/src/assets/svg/service-icon-sybase.svg
  - openmetadata-ui/src/main/resources/ui/src/generated/api/automations/createWorkflow.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/api/services/createDatabaseService.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/api/services/ingestionPipelines/createIngestionPipeline.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/automations/testServiceConnection.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/automations/workflow.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/connections/database/sybaseConnection.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/connections/serviceConnection.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/databaseService.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/ingestionPipelines/ingestionPipeline.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/metadataIngestion/testSuitePipeline.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/metadataIngestion/workflow.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/DatabaseServiceUtils.test.tsx
  - openmetadata-ui/src/main/resources/ui/src/utils/DatabaseServiceUtils.tsx
  - openmetadata-ui/src/main/resources/ui/src/utils/ServiceIconUtils.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/ServiceUtils.tsx
  required_changed_paths:
  - openmetadata-spec/src/main/resources/json/schema/entity/services/connections/database/sybaseConnection.json
upgrade_watch:
  paths:
  - openmetadata-spec/src/main/resources/json/schema/entity/services/connections/database/sybaseConnection.json
  - openmetadata-spec/src/main/resources/json/schema/entity/services/connections/serviceConnection.json
  - openmetadata-spec/src/main/resources/json/schema/entity/services/databaseService.json
  - openmetadata-ui/src/main/resources/ui/src/assets/svg/service-icon-sybase.svg
  - openmetadata-ui/src/main/resources/ui/src/generated/api/automations/createWorkflow.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/api/services/createDatabaseService.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/api/services/ingestionPipelines/createIngestionPipeline.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/automations/testServiceConnection.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/automations/workflow.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/connections/database/sybaseConnection.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/connections/serviceConnection.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/databaseService.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/ingestionPipelines/ingestionPipeline.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/metadataIngestion/testSuitePipeline.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/metadataIngestion/workflow.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/DatabaseServiceUtils.test.tsx
  - openmetadata-ui/src/main/resources/ui/src/utils/DatabaseServiceUtils.tsx
  - openmetadata-ui/src/main/resources/ui/src/utils/ServiceIconUtils.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/ServiceUtils.tsx
assurance:
  contracts:
  - CONTRACT-SYBASE-CONNECTOR
  direct_tests: []
series:
  allowed: false
  depends_on: []
```

</details>

</details>

<details>
<summary><strong>BANK-OM-007 · Tibero 연결 유형</strong></summary>

### 최초 커밋

- Git commit SHA: `62e39da8be65c3ff259802c1cd35f4b0c8baa333`
- 커밋 제목: `add Tibero customization`
- 이 커밋에서 변경한 파일: 8개
- [GitHub에서 실제 커밋 열기](https://github.com/easyseop/OM_TEMP/commit/62e39da8be65c3ff259802c1cd35f4b0c8baa333)

![BANK-OM-007 최초 커밋 강조 캡처](공유문서/assets/om-temp-manifest/commit-messages/007-tibero-initial-highlighted.png)

<details>
<summary>강조 표시가 없는 원본 캡처 보기</summary>

![BANK-OM-007 최초 커밋 원본 캡처](공유문서/assets/om-temp-manifest/commit-messages/007-tibero-initial-original.png)

</details>

### 후속 보완 커밋

- Git commit SHA: `7d19c8952612e77467b0a80d6287170d814f1de1`
- 커밋 제목: `complete Tibero service connection coverage`
- 이 커밋에서 변경한 파일: 2개
- [GitHub에서 실제 커밋 열기](https://github.com/easyseop/OM_TEMP/commit/7d19c8952612e77467b0a80d6287170d814f1de1)

![BANK-OM-007 후속 보완 커밋 강조 캡처](공유문서/assets/om-temp-manifest/commit-messages/007-tibero-followup-highlighted.png)

<details>
<summary>강조 표시가 없는 원본 캡처 보기</summary>

![BANK-OM-007 후속 보완 커밋 원본 캡처](공유문서/assets/om-temp-manifest/commit-messages/007-tibero-followup-original.png)

</details>

### 왜 하나의 BANK-OM 기능으로 보았나

두 커밋 모두 Tibero 연결 유형 하나를 완성합니다. 최초 8개 파일은 allowed_changed_paths에, 후속 커밋에서 처음 추가된 2개 파일은 candidate_additional_paths에 등록합니다. Git commit SHA는 두 개지만 업무 기능 ID와 Manifest는 BANK-OM-007 하나입니다.

<details>
<summary><strong>BANK-OM-007 Manifest 초안 전체 보기</strong></summary>

```yaml
schema_version: 1
customization_id: BANK-OM-007
status: active
kind: core-patch
title: Tibero 연결 유형
implementation:
  allowed_changed_paths:
  - openmetadata-spec/src/main/resources/json/schema/entity/services/connections/database/tiberoConnection.json
  - openmetadata-spec/src/main/resources/json/schema/entity/services/databaseService.json
  - openmetadata-ui/src/main/resources/ui/src/assets/svg/service-icon-tibero.svg
  - openmetadata-ui/src/main/resources/ui/src/generated/api/services/createDatabaseService.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/connections/database/tiberoConnection.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/databaseService.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/DatabaseServiceUtils.tsx
  - openmetadata-ui/src/main/resources/ui/src/utils/ServiceIconUtils.ts
  candidate_additional_paths:
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/connections/serviceConnection.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/DatabaseServiceUtils.test.tsx
  required_changed_paths:
  - openmetadata-spec/src/main/resources/json/schema/entity/services/connections/database/tiberoConnection.json
upgrade_watch:
  paths:
  - openmetadata-spec/src/main/resources/json/schema/entity/services/connections/database/tiberoConnection.json
  - openmetadata-spec/src/main/resources/json/schema/entity/services/connections/serviceConnection.json
  - openmetadata-spec/src/main/resources/json/schema/entity/services/databaseService.json
  - openmetadata-ui/src/main/resources/ui/src/assets/svg/service-icon-tibero.svg
  - openmetadata-ui/src/main/resources/ui/src/generated/api/services/createDatabaseService.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/connections/database/tiberoConnection.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/connections/serviceConnection.ts
  - openmetadata-ui/src/main/resources/ui/src/generated/entity/services/databaseService.ts
  - openmetadata-ui/src/main/resources/ui/src/utils/DatabaseServiceUtils.test.tsx
  - openmetadata-ui/src/main/resources/ui/src/utils/DatabaseServiceUtils.tsx
  - openmetadata-ui/src/main/resources/ui/src/utils/ServiceIconUtils.ts
assurance:
  contracts:
  - CONTRACT-TIBERO-CONNECTOR
  direct_tests: []
series:
  allowed: true
  depends_on: []
```

</details>

</details>

## Manifest 네 목록을 읽는 기준

| 항목 | 이 초안에 들어간 기준 | 검사에서 쓰는 방식 |
|---|---|---|
| `allowed_changed_paths` | 최초 BANK-OM 커밋이 실제 변경한 모든 파일 | 목록 밖 파일을 같은 ID로 변경하면 차단하고, 목록 안 파일이 최종 후보에서 실제로 달라지지 않으면 검토를 요구 |
| `required_changed_paths` | 기능이 적용됐음을 판단하는 핵심 구현 파일 | 파일이 없거나 공식 원본과 같아지면 기능이 빠진 것으로 보고 차단 |
| `candidate_additional_paths` | 같은 ID의 후속 커밋에서 처음 추가된 파일 | 사전 등록 없이 확장한 변경과 승인된 후속 변경을 구분 |
| `upgrade_watch.paths` | 공식 버전 변경 비교 검사(T42)가 확인할 경로 | 공식 새 버전에서 해당 경로가 바뀌면 자동 통과하지 않고 재검토를 요구 |

T42는 공식 OpenMetadata의 이전 버전과 새 버전에서 지정 경로가 바뀌었는지 확인하는 검사입니다. `upgrade_watch.paths`에는 현재 T42 구현에 맞춰 해당 ID의 변경 범위 전체와 직접 수정하지 않았지만 기능이 의존하는 공식 파일을 함께 넣었습니다. 따라서 watch에 있다고 해서 그 파일을 이 커밋이 반드시 수정했다는 뜻은 아닙니다.

## 현재 상태

- BANK-OM-001~007 Manifest 초안 7개 생성 완료
- 실제 Git commit의 변경 파일 목록을 초안에 반영 완료
- 현재 Manifest 스키마 및 기본 의미 검사 7개 통과
- OM_TEMP 전체 코드 build, 업무 동작 test, 1.13.1 업그레이드 비교는 아직 실행 전
- 따라서 이 문서의 Manifest는 **코드 기준 초안**이며 배포 승인 결과가 아님
