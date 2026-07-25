# Current implementation status

> Updated: 2026-07-25
> Branch: `claude/markdown-file-feedback-26933w`
> Last verified implementation commit: `efd7615`
> Nondeveloper guide and handoff implementation commit: `0f0904b`
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
280 passed, 4 skipped in 35.12s
```

This CI-equivalent local run used the two fixed historical mirror refs, so the
previous 35 mirror skips all executed and passed. The remaining four skips
require a live OpenMetadata URL and are not counted as passes. All 14 T25-R
tests pass.

Actual source-candidate gates:

```text
T25-R vendor-reconstructed-candidate  pass (checkpoint e1ffc5a1...)
T25   vendor-ancestry                 pass (candidate 38bccf90...)
T26   customization-survival          pass (candidate 38bccf90...; 7 IDs, 10 required paths)
T60-I required-test-implementations   pass (7/7 selectors resolve)
T30   commit-invariants               pass (candidate 38bccf90...)
T31   id-invariants                   pass (candidate 38bccf90...)
```

Focused product verification:

```text
Prettier (2 changed paths)             pass
DatabaseServiceUtils.test.tsx          pass (13/13; Tibero case pass)
bank contract suite                    3 passed, 4 live-runtime skipped
UI tsc --noEmit                        fail (399 diagnostics; changed paths 0)
UI core Vite build                     exit 0 (2 declaration diagnostics on unchanged upstream paths)
```

The focused UI run used Yarn 1.22.22 and Node 24.15.0 with
`--ignore-engines` because this environment has no Node 22 runtime. The
candidate's own Tibero test passed, but the broad typecheck failure remains a
release blocker rather than being reclassified as a test pass.

Source-candidate CI is defined in `.github/workflows/source-candidate.yml`.
It pins both third-party actions by 40-hex SHA, pins product commit
`38bccf9077...`, fetches the two historical upstream fixtures, runs the
combined test suite, and runs T25/T26/T60-I/T30/T31. The workflow's exact
product fetch, test, and gate commands pass in a clean
local simulation (`280 passed, 4 live skips`; five source gates pass). Remote
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

## Important production blockers

This is not yet evidence that the bank distribution is deployable:

1. The seven owners are deliberately `UNASSIGNED`/`pending`.
2. The two source-snapshot findings were intentionally excluded from the
   candidate: `.claude/settings.json` broadly auto-approves tools, and
   `docker/development/docker-compose.yml` pins ingestion image `1.9.6`.
3. All seven required test selectors now resolve to committed implementations.
   Sybase, Tibero, and the Korean IME source guard pass locally; InstanceCode,
   QueryReport, failed assertion, and bank-column live contracts skip without
   `OPENMETADATA_BASE_URL`. Candidate-bound T62 results therefore do not yet
   exist.
4. T90/T91/T94 judgment contracts are implemented, but no real OpenMetadata
   Docker upgrade run, production-like DB restore, artifact promotion, or
   offline signature verification was executed in this environment.
5. The candidate lock currently binds the source Git tree identity. A complete
   Java/UI build, image/package digest, SBOM, signing, and promotion evidence
   still need to be produced.
6. The focused Tibero Jest suite passes 13/13, but the product-wide UI
   typecheck reports 399 diagnostics. Neither changed Tibero path appears in
   those diagnostics; the broad baseline still must be repaired or
   independently baselined on the supported Node 22 toolchain.

Until those items are closed, the honest release state is **blocked**, not
pass.
