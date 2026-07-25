# Current implementation status

> Updated: 2026-07-25
> Branch: `claude/markdown-file-feedback-26933w`
> Last verified implementation commit: `f329ad1`
> Detailed review handoff: [`docs/04-진행/CLAUDE_REVIEW_HANDOFF.md`](docs/04-진행/CLAUDE_REVIEW_HANDOFF.md)

## Handoff update policy

This snapshot and the detailed handoff must be updated after every completed
development task or coherent batch, and again before an agent/context
handoff. Each update records the implementation commit, exact verification
result, blockers, pushed state, and next executable step. The full checklist
and document paths are fixed in [`CLAUDE.md`](CLAUDE.md).

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
236 passed, 35 skipped in 25.87s
```

The 35 skips require the historical Linux fixture path
`/home/user/om-mirror`; they are not failures. All 14 T25-R tests pass.

Actual source-candidate gates:

```text
T25-R vendor-reconstructed-candidate  pass (checkpoint e1ffc5a1...)
T25   vendor-ancestry                 pass (candidate 38bccf90...)
T26   customization-survival          pass (candidate 38bccf90...; 7 IDs, 10 required paths)
T30   commit-invariants               pass (candidate 38bccf90...)
T31   id-invariants                   pass (candidate 38bccf90...)
```

## Important production blockers

This is not yet evidence that the bank distribution is deployable:

1. The seven owners are deliberately `UNASSIGNED`/`pending`.
2. The two source-snapshot findings were intentionally excluded from the
   candidate: `.claude/settings.json` broadly auto-approves tools, and
   `docker/development/docker-compose.yml` pins ingestion image `1.9.6`.
3. The seven contract test IDs are specifications; the real API, DB, search,
   permission, UI/IME, Sybase, and Tibero test implementations and results do
   not exist in this repository.
4. T90/T91/T94 judgment contracts are implemented, but no real OpenMetadata
   Docker upgrade run, production-like DB restore, artifact promotion, or
   offline signature verification was executed in this environment.
5. The candidate lock currently binds the source Git tree identity. A complete
   Java/UI build, image/package digest, SBOM, signing, and promotion evidence
   still need to be produced.
6. The focused Tibero Jest test is committed but was not executed because the
   sparse product checkout has neither the UI package manifest nor installed
   UI dependencies.

Until those items are closed, the honest release state is **blocked**, not
pass.
