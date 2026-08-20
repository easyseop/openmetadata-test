# Claude Code project controls

The `/om-plan` workflow is plan-only. The project hooks bind a planning session
to its run, restrict writes to that run's proposal directory, and block apply,
deployment, tag, and push commands.

For `upgrade` mode, after the main proposal is written and before `plan check`:

1. Invoke the `om-plan-official-doc-reviewer` agent with only the current run
   directory and the review task.
2. Copy its returned object into
   `proposal/independent-document-review.yaml` without changing the collected
   facts or document snapshots.
3. If `missing_requirements` is non-empty, add explicit unresolved questions and
   stop the plan from being treated as review-ready.

This second read is an LLM cross-check, not a source of deterministic truth.
The deterministic validator still owns snapshot-digest matching, finding links,
path-remap coverage, and required-output presence.
