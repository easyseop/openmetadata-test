# Claude review entry point

Review this branch as an independent safety and completeness audit.

## Handoff maintenance contract

Treat the following files as one handoff set:

- `CLAUDE.md` — review entry point and review rules.
- `docs/00-사용가이드/비개발자_사용_가이드.md` — plain-language user
  workflow, result meanings, and current deployment-readiness statement.
- `docs/00-사용가이드/비개발자_시연_가이드.md` — command-free source
  demonstration, runtime workflow walkthrough, and evidence checklist.
- `docs/02-설계/bank_om_registration_policy.md` — single source for BANK-OM
  issuance, Manifest fields, follow-up commits, repository roles, and future
  LLM-wiki synchronization.
- `STATUS.md` — short, current implementation snapshot.
- `docs/04-진행/CLAUDE_REVIEW_HANDOFF.md` — detailed implementation,
  verification, blockers, and continuation guide.
- `SESSION_STATE.md` — longer-lived decisions and historical continuity.
- `docs/04-진행/openmetadata_dev_roadmap.md` and
  `docs/04-진행/openmetadata_build_plan.md` — task status and specification.

After every completed development task or coherent batch, update the affected
handoff files in the same commit as the implementation when practical. Before
switching agents or exhausting the working context, record:

1. the branch and the implementation commit being handed over;
2. the exact files and behavior changed, including task IDs;
3. the exact verification command, pass/fail/skip counts, and skip reasons;
4. current blockers, assumptions, and the distinction between implemented
   contracts and executed operational evidence;
5. whether the worktree is clean and whether the commit was pushed; and
6. the next executable step or command.

If user-visible status, required business inputs, terminology, approval steps,
error interpretation, or an operating scenario changed, update the
nondeveloper guide in that same batch. The guide must never turn a successful
source-only CI run into a deployment-ready claim.

Never copy credentials, tokens, private keys, or transient approval data into
the handoff. If documentation and code temporarily diverge, treat the handoff
as incomplete rather than guessing that an old status is still current.

Read in this order:

1. [`docs/04-진행/CLAUDE_REVIEW_HANDOFF.md`](docs/04-진행/CLAUDE_REVIEW_HANDOFF.md)
2. [`STATUS.md`](STATUS.md)
3. [`docs/00-사용가이드/비개발자_사용_가이드.md`](docs/00-사용가이드/비개발자_사용_가이드.md)
4. [`docs/00-사용가이드/비개발자_시연_가이드.md`](docs/00-사용가이드/비개발자_시연_가이드.md)
5. [`docs/02-설계/bank_om_registration_policy.md`](docs/02-설계/bank_om_registration_policy.md)
6. [`docs/02-설계/ADR-001-vendor-merge-default.md`](docs/02-설계/ADR-001-vendor-merge-default.md)
7. [`docs/04-진행/openmetadata_build_plan.md`](docs/04-진행/openmetadata_build_plan.md)
8. schemas and modules under `harness/acgh/`

Do not infer deployment readiness from unit-test success. In particular,
confirm that the root-snapshot ancestry blocker, unassigned owners, two
unregistered blocking paths, the partial-only T61 result (source connectors
2/5 high IDs), API/browser runtime skips, unexecuted
`Runtime contracts` workflow, the 90-day-only evidence retention boundary,
missing organization-owned archive, and unexecuted T90/T91/T94 operational
evidence remain visible and fail closed.

Report findings as:

- **Blocking** — could produce a false pass, stale promotion, or unauthorized
  bypass.
- **Serious** — incomplete policy binding, registration gap, or weak evidence.
- **Minor** — maintainability or documentation issue.
- **Validated** — important invariant independently confirmed.

For every finding, cite the exact file and test or counterexample.
