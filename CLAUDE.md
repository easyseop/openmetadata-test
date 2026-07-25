# Claude review entry point

Review this branch as an independent safety and completeness audit.

Read in this order:

1. [`docs/04-진행/CLAUDE_REVIEW_HANDOFF.md`](docs/04-진행/CLAUDE_REVIEW_HANDOFF.md)
2. [`STATUS.md`](STATUS.md)
3. [`docs/02-설계/ADR-001-vendor-merge-default.md`](docs/02-설계/ADR-001-vendor-merge-default.md)
4. [`docs/04-진행/openmetadata_build_plan.md`](docs/04-진행/openmetadata_build_plan.md)
5. schemas and modules under `harness/acgh/`

Do not infer deployment readiness from unit-test success. In particular,
confirm that the root-snapshot ancestry blocker, unassigned owners, two
unregistered blocking paths, missing runtime contract tests, and unexecuted
T90/T91/T94 operational evidence remain visible and fail closed.

Report findings as:

- **Blocking** — could produce a false pass, stale promotion, or unauthorized
  bypass.
- **Serious** — incomplete policy binding, registration gap, or weak evidence.
- **Minor** — maintainability or documentation issue.
- **Validated** — important invariant independently confirmed.

For every finding, cite the exact file and test or counterexample.
