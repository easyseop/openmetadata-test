# Current implementation status

> Updated: 2026-07-28 KST
> Branch: `codex/strict-manifest-gates`
> Last verified implementation commit: `5f54687`
> Fixed-mirror CI compatibility fix: `f661796`
> Strict-scope and stage 2·3 batch verified: 2026-07-28 10:18 KST
> Remote fixed-mirror verification: [`30253003871`](https://github.com/easyseop/openmetadata-test/actions/runs/30253003871), 341 passed / 7 operational skips / 8 source gates
> Current product candidate: `849ae756cd238f218b5e3a6c795a392305cb32ee`
> Strict-scope progress: [`docs/04-진행/STRICT_SCOPE_IMPROVEMENT_PROGRESS.md`](docs/04-진행/STRICT_SCOPE_IMPROVEMENT_PROGRESS.md)
> BANK-OM single operating-policy source: [`docs/02-설계/bank_om_registration_policy.md`](docs/02-설계/bank_om_registration_policy.md)
> Current Codex handoff: [`docs/04-진행/CODEX_HANDOFF.md`](docs/04-진행/CODEX_HANDOFF.md)
> Phase 1·2·3 sharing requirements: [`docs/04-진행/SHARING_ARTIFACT_REQUIREMENTS.md`](docs/04-진행/SHARING_ARTIFACT_REQUIREMENTS.md)
> Portable readability review skill: [`.agents/skills/clarity-preflight-review/SKILL.md`](.agents/skills/clarity-preflight-review/SKILL.md)
> BANK-OM-011 governance registration / evidence rebind: `b1d3fa6` / `c246ae2`
> Recorded BANK-OM-011 evidence run: [`30222439344`](https://github.com/easyseop/openmetadata-test/actions/runs/30222439344)
> UI typecheck baseline delta gate commit: `39294bf`
> Product UI hardening commits: `ddf0dd2`, `70d028a`, `b80d24d`, `849ae756`
> BANK-OM-010 governance registration commit: `d70fe81`
> BANK-OM-010 evidence rebind commit: `5e6d0a8`
> 2026-07-27 06:00 KST repository health check: governance `434d92b`,
> product `b80d24d`; both local/remote pairs clean and equal, latest final-sync
> run [`30219859614`](https://github.com/easyseop/openmetadata-test/actions/runs/30219859614)
> successful, local fixed-mirror suite 316 passed/7 operational skips, no open
> PR/review, both working branches still unprotected
> BANK-OM-009 governance registration commit: `4353f45`
> BANK-OM-009 evidence rebind commit: `89763f3`
> Rendered UI runtime-contract expansion commit: `093724f`
> Runtime patch-kill gate implementation commit: `1956b78`
> Nondeveloper guide and handoff implementation commit: `0f0904b`
> Nondeveloper demonstration runbook commit: `f833f79`
> Actual GitHub screenshot demonstration commit: `258bb8a`
> Friendly customization/verifier explanation commit: `705bb4f`
> Runtime operations documentation commit: `a291f31`
> Runtime evidence retention implementation commit: `502f42f`
> Source patch-kill implementation commits: `a2cbb52`, `7a2fb5f`
> Node 24 artifact action upgrade commit: `8ec6e28`
> Detailed review handoff: [`docs/04-진행/CLAUDE_REVIEW_HANDOFF.md`](docs/04-진행/CLAUDE_REVIEW_HANDOFF.md)
> Nondeveloper entry point: [`docs/00-사용가이드/비개발자_사용_가이드.md`](docs/00-사용가이드/비개발자_사용_가이드.md)
> Nondeveloper demonstration runbook: [`docs/00-사용가이드/비개발자_시연_가이드.md`](docs/00-사용가이드/비개발자_시연_가이드.md)

## Handoff update policy

This snapshot and the detailed handoff must be updated after every completed
development task or coherent batch, and again before an agent/context
handoff. Each update records the implementation commit, exact verification
result, blockers, pushed state, and next executable step. The full checklist
and document paths are fixed in [`CLAUDE.md`](CLAUDE.md).
When user-visible status, inputs, terminology, or operating steps change, the
nondeveloper guide is updated in the same coherent batch.

## Outcome

### 2026-07-27 strict-scope hardening

The first improvement batch is implemented and locally verified. Source
manifests `BANK-OM-001` through `BANK-OM-007` now list the exact files observed
in the pinned snapshot instead of authorizing directories with globs. T25-R
rejects non-literal, unknown, duplicate, or incorrectly owned source paths.
T26 checks the complete registered source inventory as well as the smaller
hard-block `required` subset. T40 checks every changed ownership zone, and T70
protects checker, registration, test, design, technical-reference, progress,
and status files.

Initial focused result: **39 passed**. The actual product candidate `849ae756...`
passes T25/T26/T60-I/T30/T31, and reconstruction checkpoint `e1ffc5a1...`
passes strict T25-R.

### 2026-07-28 stage 2·3 implementation

Stage 2 is implemented and connected to executable runners. T42 now detects
changed watched paths, declared configuration keys, and dependency identifiers;
`watch_suggest.py` proposes directly referenced upstream files but requires code
owner review before registration. T41 rejects empty intent, T43 loads a
versioned external debt policy and measures the candidate, T93 compares exact
per-ID commit history with manifest scope, T50 can require non-empty declarative
checks, and T51 reports same-type scalar/list content changes.

Integration found and fixed two registration defects: BANK-OM-007 now separates
the eight pinned snapshot paths from two registered follow-up paths, and the
candidate-only `useDataFetching.test.tsx` is no longer incorrectly treated as
an upstream watch path. Current candidate `849ae756...` passes T40, T41, T43,
and exact-scope T93 in addition to the previous source gates.

Stage 3 execution support is implemented. `runtime_preflight.py` validates all
required internal URLs, identifiers, authentication/storage-state presence,
and the deployed sha256 artifact digest without echoing secrets. The runtime
workflow now fails before installation if the environment is incomplete.
Actual API/UI/runtime and counterfactual deployment evidence still requires
the bank environment; it is not reported as executed or passed.

The deterministic governance engine is implemented through candidate
registration, vendor/replay routing, required-test result binding, fast lanes,
break-glass validation, advisory LLM memos, upgrade-run evidence, identical
digest promotion, retirement, and signed air-gap verification.

The real `kangdkdk/kb_openmetadata` snapshot is registered as seven source
customizations (`BANK-OM-001` through `BANK-OM-007`) against the official
OpenMetadata `1.13.1-release` commit. A separately identified
candidate-follow-up, `BANK-OM-008`, records the UI type hardening added after
the snapshot reconstruction without pretending it existed in that snapshot.
A second candidate-follow-up, `BANK-OM-009`, closes the shared search result
type mapping gap exposed by that integration.
A third candidate-follow-up, `BANK-OM-010`, makes alert entity-ID suggestions
safe for search-source union members that omit `_source.id`.
A fourth candidate-follow-up, `BANK-OM-011`, requires every generic listing
caller to provide an index-specific response transform instead of assigning a
search-source union to an arbitrary entity type.

T25-R now supplies the snapshot-to-vendor reconstruction planner and candidate
gate. The 113 pinned source paths deterministically classify as 74
single-owner paths, 37 shared paths, and 2 excluded non-product paths.

The actual vendor branch is now built and pushed:

- repository: `easyseop/OpenMetadata`
- branch: `codex/bank-vendor-1.13.1-rebuild`
- reconstruction checkpoint: `e1ffc5a1eb270c3225736544bb309a0c85af6d2c`
- current candidate: `849ae756cd238f218b5e3a6c795a392305cb32ee`
- official parent: `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9`
- seven reconstruction commits, one consecutive `BANK-OM-007` follow-up, and
  four registered candidate-hardening commits (`BANK-OM-008` through
  `BANK-OM-011`)

T25-R passes on the exact reconstruction checkpoint. T25 ancestry, T26
survival, T30 commit invariants, and T31 ID invariants pass on the current
candidate. The unrelated snapshot commit is not in the candidate ancestry,
the checkpoint's 111 registered paths match the snapshot
(JSON semantically, other files byte-for-byte), and the two excluded files
remain at official upstream content.

Static product review then found that Tibero was present in the database
service schema and selector but absent from the generated common connection
`ConfigType`, with no focused utility test. Commit `38bccf9077` adds that enum
member and a Tibero schema-mapping unit test under the same consecutive
`BANK-OM-007` series.

The supported Node 22.17.0 typecheck then exposed three diagnostics introduced
by the bank UI integration: both new list routes omitted the page title required
by their layout wrapper, and the two new search indices were missing from
`ExploreSearchIndex`. Product commit `ddf0dd2eba` fixes all three. The total
diagnostic count fell from 399 to 396, and no candidate-introduced diagnostic
remains. The remaining 16 diagnostics that happen to be in candidate-changed
files are on source lines identical to official upstream 1.13.1.

Full-log comparison then exposed an older OpenMetadata gap that became visible
after adding the two bank indices: `SearchIndex.METADATA_SERVICE` existed in
the enum but not in `SearchIndexSearchSourceMapping`. Product commit
`70d028a035` adds the generated metadata-service search type, completes the
common union, and narrows Curated Assets state to the `DATA_ASSET` result type.
Its focused Jest suite passes 18/18 and the same full typecheck falls again
from 396 to 357 diagnostics.

Product commit `b80d24d831` then preserves `_source.id` when present and falls
back to the guaranteed Elasticsearch hit `_id` for alert entity-ID
suggestions. The AlertsUtil suite passes 112/112, including both ID paths.

Product commit `849ae756cd` then removes the unsafe generic default transform
from `useDataFetching`. Domain and DataProduct listings provide concrete,
index-specific transforms, and a new hook test proves that only transformed
entities enter state. The focused data-fetching/listing suites pass 7/7.

The full official `1.13.1-release` tree was generated and typechecked with
the same Node 22.17.0, Yarn 1.22.22, dependency tree, and command. It also
produced 396 diagnostics across 141 files. Candidate `849ae756` has 355
diagnostics across 133 files: zero new path/code diagnostics and 41 removed.
T63 also fingerprints messages and reports ten new and 51 removed message
variants for review. It therefore returns **approval**, never pass, for this
non-zero baseline.

The ten remaining message variants were independently classified against the
clean-cache full logs as equivalent TypeScript union ordering or rendering
changes. No new semantic
regression was identified in that technical review. This does not approve the
remaining 355 diagnostics: designated-owner baseline approval or repair is
still required.

## Verification

```text
Current local suite: 301 passed, 47 skipped in 19.09s
Historical fixed-mirror suite: 316 passed, 7 skipped in 30.67s
Current remote fixed-mirror suite: 341 passed, 7 operational skips in 217.49s
```

The current 47 skips require the fixed historical mirror or live bank
API/browser/runtime inputs and are not counted as passes. The historical
CI-equivalent local run used the two fixed historical mirror refs, so the
previous 35 mirror skips all executed and passed. Four remaining skips require
a live OpenMetadata URL and three require real authenticated browser pages;
none are counted as passes.

The current product candidate passes T25, T26, T60-I, T30, T31, T40, T41, and
exact-scope T93. The upgrade-risk runner also passes T43 and policy T93. T42
was exercised only as an A-equals-B wiring smoke, so it is not evidence that a
future official OpenMetadata upgrade is safe. The T43 conflict-rate input was
also zero for runner wiring, not a measured upgrade conflict rate.

T61 source negative controls now run the external Sybase and Tibero contract
tests against fixed predecessor commits that do not contain the corresponding
connector patch. Both tests fail as required, so their scoped patch-kill
verdict is pass. The machine result is
`harness/registrations/kb-openmetadata/source-patch-kill-evidence.yaml`, bound
to candidate `849ae756...`, governance registration `b1d3fa6...`, the plan
digest, both predecessor SHAs, and both exact selectors. This is a
**source-capable 2/5 high-ID result**, not complete T61: InstanceCode,
QueryReport, and Data Assertions still require deployed counterfactual stacks.

The separate `Runtime patch-kill` workflow now implements those remaining
three plans. Each selected required test must fail twice on its locked
predecessor deployment while independent API/data/UI probes pass both before
and after. Candidate, predecessor source/tree, deployed artifact digest,
deployment-record digest, governance commit, suite digest, and environment ID
are bound into one fail-closed result and retained for 90 days. All three
no-environment rehearsals correctly returned `analysis_error`; no predecessor
artifact has actually been built or deployed, so the 3/5 runtime evidence is
still pending.

Actual source-candidate gates:

```text
T25-R vendor-reconstructed-candidate  pass (checkpoint e1ffc5a1...)
T25   vendor-ancestry                 pass (candidate 849ae756...)
T26   customization-survival          pass (candidate 849ae756...; 11 IDs, exact registered inventory + 22 required paths)
T60-I required-test-implementations   pass (9/9 selectors resolve)
T30   commit-invariants               pass (candidate 849ae756...)
T31   id-invariants                   pass (candidate 849ae756...)
```

Focused product verification:

```text
Prettier (6 changed paths)             pass
DatabaseServiceUtils.test.tsx          pass (13/13; Tibero case pass)
CuratedAssetsWidget.test.tsx           pass (18/18; pre-existing act warnings remain)
AlertsUtil.test.tsx                    pass (112/112; pre-existing FormContext warnings remain)
useDataFetching/useListingData tests   pass (7/7; pre-existing Router warnings remain)
bank contract source suite             3 passed (Sybase, Tibero, IME source guard)
required operational selectors         2 passed, 7 skipped (4 API, 3 browser)
UI tsc --noEmit (Node 22.17.0)          approval (upstream 396 > candidate 355; new 0, removed 41)
UI core Vite build                     exit 0 (2 declaration diagnostics on unchanged upstream paths)
```

T62 runtime execution is now implemented in
`.github/workflows/runtime-contracts.yml`. Its fail-closed runner executes each
catalog selector in a fresh pytest process, derives outcomes from JUnit XML,
retains retries, atomically writes the candidate lock/test-run set/result, and
checks the result against the actual process exit. A local no-runtime
simulation produced `2 pass, 7 skipped -> block`; an intentionally false exit
was converted to `analysis_error`. The three evidence YAML files are uploaded
with pinned `actions/upload-artifact` code as a non-overwritable, 90-day CI
artifact whose ID, digest, and URL are written to the job summary. No real
runtime workflow has been executed.

The focused UI run used Yarn 1.22.22 and official Node 22.17.0, matching the
product `.nvmrc`; the downloaded archive matched its published SHA-256
`cc9cc294...e97914`. The candidate's own Tibero test passed and the three
candidate-introduced type errors are fixed, but the remaining broad upstream
baseline still blocks a clean product-wide typecheck.

T63 is implemented in `harness/acgh/tsc_baseline.py` with a registration CLI
and machine evidence. It counts a multiset rather than a set so duplicate
diagnostics cannot disappear silently, rejects malformed paths and unexpected
process exits as `analysis_error`, blocks any new candidate diagnostic, and
keeps a non-zero baseline at `approval`. A second message multiset now exposes
same-path/code message substitutions instead of allowing them to remain hidden.

Source-candidate CI is defined in `.github/workflows/source-candidate.yml`.
It pins all third-party actions by 40-hex SHA, pins product commit
`849ae756cd...`, fetches the two historical upstream fixtures, runs the
combined test suite, runs T25/T26/T60-I/T30/T31, and runs the two source-capable
T61 negative controls. Patch-kill evidence is kept as a non-overwritable
90-day artifact. The workflow's exact
product fetch, test, and gate commands pass in a clean
local simulation (`316 passed, 7 operational skips`; five source gates and two
source patch-kill experiments pass).
Historical remote
run `30160752510` also passed. GitHub emitted a Node 20 action deprecation
annotation, so checkout/setup-python were upgraded to pinned Node 24 majors;
Node 24 validation run
[`30160846880`](https://github.com/easyseop/openmetadata-test/actions/runs/30160846880)
then passed with zero annotations. Final evidence-sync run
[`30160922136`](https://github.com/easyseop/openmetadata-test/actions/runs/30160922136)
also passed with `280 passed, 4 skipped`. The nondeveloper guide and handoff
batch then passed remotely in
[`30161253922`](https://github.com/easyseop/openmetadata-test/actions/runs/30161253922)
with `280 passed, 4 skipped in 12.83s` and all five source gates passing.
Runtime implementation `b29d0ce` and documentation `a291f31` are pushed. Their
remote run
[`30162134698`](https://github.com/easyseop/openmetadata-test/actions/runs/30162134698)
passed at head `45d0994` with `293 passed, 5 skipped in 13.68s` and all five
source gates passing.

The first remote source patch-kill run
[`30212561441`](https://github.com/easyseop/openmetadata-test/actions/runs/30212561441)
passed at head `17b7427` with `297 passed, 5 skipped in 19.57s`, all five source
gates, both patch-kill experiments, and evidence upload passing. Artifact
`source-patch-kill-evidence-30212561441-1` has ID `8634882239`, GitHub digest
`sha256:d5afd822...a7bfa32f`, and expiry `2026-10-24T17:26:01Z`. That run exposed
a Node 20 deprecation annotation from upload-artifact v4; commit `8ec6e28`
upgrades both evidence workflows to pinned upload-artifact v7.0.1 commit
`043fb46d...d1fc6a0a`, whose official action metadata uses Node 24.
Validation run
[`30212703620`](https://github.com/easyseop/openmetadata-test/actions/runs/30212703620)
then passed at head `9326696` with zero annotations, `297 passed, 5 skipped in
13.14s`, all five source gates and both patch-kill experiments passing. Its
Node 24-uploaded artifact is `source-patch-kill-evidence-30212703620-1`, ID
`8634920602`, digest `sha256:bb8b9751...b12cf109`, expiry
`2026-10-24T17:30:09Z`.

The rebound `BANK-OM-008` candidate was verified remotely in
[`30214885448`](https://github.com/easyseop/openmetadata-test/actions/runs/30214885448)
at governance head `9e95fd0`: `306 passed, 7 skipped in 13.76s`, all five
source gates, T60-I 9/9, and both source patch-kill experiments passed.
Artifact `source-patch-kill-evidence-30214885448-1` has ID `8635517530`,
digest `sha256:bbb2bddf...ca40a27`, and expires
`2026-10-24T18:31:08Z`.

T63 and its documentation were verified remotely in
[`30215596535`](https://github.com/easyseop/openmetadata-test/actions/runs/30215596535)
at governance head `eb786ad`: `315 passed, 7 skipped in 15.00s`, all five
source gates, T60-I 9/9, and both source patch-kill experiments passed.
Artifact `source-patch-kill-evidence-30215596535-1` has ID `8635710912`,
digest `sha256:231137d0...4c110b`, and expires
`2026-10-24T18:50:55Z`.

The current `BANK-OM-009` candidate was then verified remotely in
[`30216708258`](https://github.com/easyseop/openmetadata-test/actions/runs/30216708258)
at governance head `bc0e957`: `316 passed, 7 skipped in 13.15s`, all five
source gates, T60-I 9/9, and both source patch-kill experiments passed against
the locked product commit `70d028a035...`. Artifact
`source-patch-kill-evidence-30216708258-1` has ID `8636012730`, digest
`sha256:813c26df...50860b4`, and expires `2026-10-24T19:22:20Z`.

The `BANK-OM-010` candidate was verified remotely in
[`30219786626`](https://github.com/easyseop/openmetadata-test/actions/runs/30219786626)
at governance head `90036ff`: `316 passed, 7 skipped in 15.29s`, all five
source gates, 10 active customization IDs, T60-I 9/9, and both source
patch-kill experiments passed against product commit `b80d24d831...`.
Artifact `source-patch-kill-evidence-30219786626-1` has ID `8636860716`,
digest `sha256:88a16a93...7eb5910`, and expires
`2026-10-24T20:49:23Z`.

The `BANK-OM-011` candidate was verified remotely in
[`30222439344`](https://github.com/easyseop/openmetadata-test/actions/runs/30222439344)
at governance head `a715092`: `316 passed, 7 skipped in 13.71s`, all five
source gates, 11 active customization IDs, T60-I 9/9, and both source
patch-kill experiments passed against product commit `849ae756cd...`.
Artifact `source-patch-kill-evidence-30222439344-1` has ID `8637594508`,
digest `sha256:c6221ec8...47c38d5`, and expires
`2026-10-24T22:05:46Z`.

## Important production blockers

This is not yet evidence that the bank distribution is deployable:

1. The eleven registered owners are deliberately `UNASSIGNED`/`pending`.
2. The two source-snapshot findings were intentionally excluded from the
   candidate: `.claude/settings.json` broadly auto-approves tools, and
   `docker/development/docker-compose.yml` pins ingestion image `1.9.6`.
3. All nine required test selectors across the seven business contracts now
   resolve to committed implementations. Sybase and Tibero pass locally. The
   Korean IME source guard also passes but is not browser evidence. InstanceCode,
   QueryReport, failed assertion, and bank-column API selectors skip without
   `OPENMETADATA_BASE_URL`; the Data Assertions page, bank-column page, and real
   IME selectors require their authenticated URLs. The runtime producer now
   records these as `2 pass, 7 skipped -> block`, so a full candidate-bound T62
   pass does not yet exist.
4. Sybase and Tibero source patch-kill negative controls pass, and a separate
   fail-closed runtime checker now exists for the other three high IDs. Those
   three still need separately built and deployed predecessor stacks and real
   executions. Therefore the complete high/critical T61 gate is not passed.
5. T90/T91/T94 judgment contracts are implemented, but no real OpenMetadata
   Docker upgrade run, production-like DB restore, artifact promotion, or
   offline signature verification was executed in this environment.
   Runtime YAML is retained in GitHub for 90 days, but an organization-owned
   long-term evidence archive is not connected.
6. The candidate lock currently binds the source Git tree identity. A complete
   Java/UI build, image/package digest, SBOM, signing, and promotion evidence
   still need to be produced.
7. The focused Tibero, Curated Assets, AlertsUtil, and generic listing suites
   pass 13/13, 18/18, 112/112, and 7/7.
   The supported Node 22 typecheck
   confirms the three candidate-introduced diagnostics are fixed. Official
   upstream reports 396 diagnostics while candidate reports 355; T63 finds
   no new path/code diagnostic and 41 removals, plus ten changed message
   variants for review. It still reports `approval`, not `pass`. The broad
   baseline must be repaired or approved after full-log review before release.
8. GitHub reports both working branches as `protected: false`, and neither
   branch currently has an open pull request. Therefore required checks,
   designated review, and two-person approval are not enforced by repository
   settings. A repository administrator must choose the protected integration
   target and configure the source-candidate check and review policy before
   this workflow can be treated as an enforced release control.

Until those items are closed, the honest release state is **blocked**, not
pass.
