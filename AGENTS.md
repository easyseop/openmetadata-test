# Repository working instructions

## Resume the current work first

Every agent or new session must begin with the following sequence. Do not infer the
current task from an old guide or from the newest branch name alone.

1. Run `git status --short --branch` and preserve all existing local changes.
2. Read `docs/04-진행/CODEX_CURRENT_HANDOFF.md` from beginning to end.
3. Confirm that the current branch and commit match the handoff. If they do not,
   do not reset, switch, pull, or overwrite files until the difference is explained.
4. If the documented branch is not available locally, run `git fetch origin`, then
   look for the newest remote branch that contains
   `docs/04-진행/CODEX_CURRENT_HANDOFF.md`. Do not select an unrelated remote branch
   merely because it has the newest commit date.
5. Read the historical `docs/04-진행/CODEX_HANDOFF.md` only when earlier decisions or
   implementation history are needed.

The current handoff is the operational source of truth. Update it after every coherent
work batch, whenever a long command changes phase or fails, before committing or
pushing, and before another computer or agent takes over. Record the exact branch,
commit, dirty files, completed checks, active command, failure reason, retained
evidence, and next executable command. Never write credentials or authentication
tokens into it.

Use these commands when the current work branch is missing locally:

```bash
git fetch origin
git for-each-ref --sort=-committerdate \
  --format='%(refname:short)' refs/remotes/origin
git cat-file -e \
  'origin/<검토할-branch>:docs/04-진행/CODEX_CURRENT_HANDOFF.md'
```

The last command has no output when that branch contains the handoff file. Inspect
the handoff on that remote branch before creating a local branch. Never switch or
reset a dirty worktree solely to follow these instructions.

## Start here

Before continuing the nondeveloper sharing guide, read these files in order:

1. `docs/04-진행/CODEX_CURRENT_HANDOFF.md`
2. `docs/04-진행/CODEX_HANDOFF.md`
3. `docs/04-진행/SHARING_ARTIFACT_REQUIREMENTS.md`
4. `docs/02-설계/bank_om_registration_policy.md`
5. `.agents/skills/clarity-preflight-review/SKILL.md`

Use the repository-local `clarity-preflight-review` skill before previewing,
committing, pushing, or sharing any user-facing HTML or handoff document.

## Wording rules

- Keep normal technical terms such as 커스터마이징, branch, commit, Manifest, API,
  test, Git commit SHA, and digest.
- Explain them with ordinary complete sentences.
- Do not use unrelated metaphors such as 영수증, 요리, 레시피, 짐, or 신호등.
- Never describe a source-tested code version as deployed or used in production.
- Separate implemented, tested, planned, and environment-pending behavior.

## Artifact workflow

- Phase 1 and Phase 2 editable HTML fragments and rendered standalone files live in
  `docs/00-사용가이드/공유문서/`.
- Phase 3 is not approved or complete until the simulation, actual gate output, and
  captured screens are added.
- Update `docs/04-진행/CODEX_CURRENT_HANDOFF.md` after each coherent work batch and
  before changing computers or agents. Move durable historical detail into
  `docs/04-진행/CODEX_HANDOFF.md` only when it is useful beyond the current task.
- Preserve unrelated user files. In particular, do not stage or edit editor swap files.
