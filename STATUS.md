# Current implementation status

> Updated: 2026-07-27
> Branch: `claude/markdown-file-feedback-26933w`
> Last verified implementation commit: `093724f`
> Rendered UI runtime-contract expansion commit: `093724f`
> Nondeveloper guide and handoff implementation commit: `0f0904b`
> Runtime operations documentation commit: `a291f31`
> Runtime evidence retention implementation commit: `502f42f`
> Source patch-kill implementation commits: `a2cbb52`, `7a2fb5f`
> Node 24 artifact action upgrade commit: `8ec6e28`
> Detailed review handoff: [`docs/04-진행/CLAUDE_REVIEW_HANDOFF.md`](docs/04-진행/CLAUDE_REVIEW_HANDOFF.md)
> Nondeveloper entry point: [`docs/00-사용가이드/비개발자_사용_가이드.md`](docs/00-사용가이드/비개발자_사용_가이드.md)

## Handoff update policy

This snapshot and the detailed handoff must be updated after every completed
development task or coherent batch, and again before an agent/context
handoff. Each update records the implementation commit, exact verification
result, blockers, pushed state, and next executable step. The full checklist
and document paths are fixed in [`CLAUDE.md`](CLAUDE.md).
When user-visible status, inputs, terminology, or operating steps change, the
nondeveloper guide is updated in the same coherent batch.

## Outcome

The deterministic governance engine is implemented through candidate
registration, vendor/replay routing, required-test result binding, fast lanes,
break-glass validation, advisory LLM memos, upgrade-run evidence, identical
digest promotion, retirement, and signed air-gap verification.

The real `kangdkdk/kb_openmetadata` snapshot is registered as seven
customizations (`BANK-OM-001` through `BANK-OM-007`) against the official
OpenMetadata `1.13.1-release` commit.

T25-R now supplies the snapshot-to-vendor reconstruction planner and candidate
gate. The 113 pinned source paths deterministically classify as 67
single-owner paths, 44 shared paths, and 2 excluded non-product paths.

The actual vendor branch is now built and pushed:

- repository: `easyseop/OpenMetadata`
- branch: `codex/bank-vendor-1.13.1-rebuild`
- reconstruction checkpoint: `e1ffc5a1eb270c3225736544bb309a0c85af6d2c`
- current candidate: `38bccf90779a8afe4a4f0e9313e11706f6d940d4`
- official parent: `afcb2d2cd7e7c28f1d0ce60538c60a96f4eb9dc9`
- seven reconstruction commits plus one consecutive `BANK-OM-007` follow-up

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

## Verification

```text
297 passed, 7 skipped in 31.18s
```

This CI-equivalent local run used the two fixed historical mirror refs, so the
previous 35 mirror skips all executed and passed. Four remaining skips require
a live OpenMetadata URL and three require real authenticated browser pages;
none are counted as passes. All 14 T25-R tests pass.

T61 source negative controls now run the external Sybase and Tibero contract
tests against fixed predecessor commits that do not contain the corresponding
connector patch. Both tests fail as required, so their scoped patch-kill
verdict is pass. The machine result is
`harness/registrations/kb-openmetadata/source-patch-kill-evidence.yaml`, bound
to candidate `38bccf90...`, governance implementation `7a2fb5f...`, the plan
digest, both predecessor SHAs, and both exact selectors. This is a
**source-capable 2/5 high-ID result**, not complete T61: InstanceCode,
QueryReport, and Data Assertions still require deployed counterfactual stacks.

Actual source-candidate gates:

```text
T25-R vendor-reconstructed-candidate  pass (checkpoint e1ffc5a1...)
T25   vendor-ancestry                 pass (candidate 38bccf90...)
T26   customization-survival          pass (candidate 38bccf90...; 7 IDs, 10 required paths)
T60-I required-test-implementations   pass (9/9 selectors resolve)
T30   commit-invariants               pass (candidate 38bccf90...)
T31   id-invariants                   pass (candidate 38bccf90...)
```

Focused product verification:

```text
Prettier (2 changed paths)             pass
DatabaseServiceUtils.test.tsx          pass (13/13; Tibero case pass)
bank contract source suite             3 passed (Sybase, Tibero, IME source guard)
required operational selectors         2 passed, 7 skipped (4 API, 3 browser)
UI tsc --noEmit                        fail (399 diagnostics; changed paths 0)
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

The focused UI run used Yarn 1.22.22 and Node 24.15.0 with
`--ignore-engines` because this environment has no Node 22 runtime. The
candidate's own Tibero test passed, but the broad typecheck failure remains a
release blocker rather than being reclassified as a test pass.

Source-candidate CI is defined in `.github/workflows/source-candidate.yml`.
It pins all third-party actions by 40-hex SHA, pins product commit
`38bccf9077...`, fetches the two historical upstream fixtures, runs the
combined test suite, runs T25/T26/T60-I/T30/T31, and runs the two source-capable
T61 negative controls. Patch-kill evidence is kept as a non-overwritable
90-day artifact. The workflow's exact
product fetch, test, and gate commands pass in a clean
local simulation (`297 passed, 7 operational skips`; five source gates and two
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

## Important production blockers

This is not yet evidence that the bank distribution is deployable:

1. The seven owners are deliberately `UNASSIGNED`/`pending`.
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
4. Sybase and Tibero source patch-kill negative controls pass, but the three
   API-based high IDs still need separately deployed without-patch stacks.
   Therefore the complete high/critical T61 gate is not passed.
5. T90/T91/T94 judgment contracts are implemented, but no real OpenMetadata
   Docker upgrade run, production-like DB restore, artifact promotion, or
   offline signature verification was executed in this environment.
   Runtime YAML is retained in GitHub for 90 days, but an organization-owned
   long-term evidence archive is not connected.
6. The candidate lock currently binds the source Git tree identity. A complete
   Java/UI build, image/package digest, SBOM, signing, and promotion evidence
   still need to be produced.
7. The focused Tibero Jest suite passes 13/13, but the product-wide UI
   typecheck reports 399 diagnostics. Neither changed Tibero path appears in
   those diagnostics; the broad baseline still must be repaired or
   independently baselined on the supported Node 22 toolchain.

Until those items are closed, the honest release state is **blocked**, not
pass.
