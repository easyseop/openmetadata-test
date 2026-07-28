---
name: clarity-preflight-review
description: Review user-facing HTML, guides, reports, and handoff documents before sharing them. Detect duplicated information, unexplained terms, ambiguous wording, misleading implementation status, and layouts that a first-time department reader cannot follow.
---

# Clarity Preflight Review

Use this skill after editing and before previewing, committing, pushing, or sharing a
user-facing artifact.

## Review workflow

1. Read the complete artifact, not only the edited lines.
2. Compare factual claims with the actual code, schema, Git state, or test result.
3. Fix every blocking issue below before sharing.
4. Read the result again as a department employee who has never seen the repository.
5. Inspect the rendered output when layout matters.

## Blocking checks

### Reader flow

The main flow must answer these questions in this order:

1. Why is this work needed?
2. Which repository, branch, code version, or input is being discussed?
3. What must be prepared before work starts?
4. What happens in chronological order?
5. What does each check decide?
6. What result permits approval or requires stopping?
7. What is complete, what is pending, and what happens next?

Do not place a definition, example, or explanation at the same visual level as a
workflow step when it belongs inside that step.

### Terminology

- Use one term for one concept throughout the artifact.
- Keep widely used technical terms such as 커스터마이징, repository, branch,
  commit, Manifest, API, test, Git commit SHA, and digest when they are precise.
- Explain a technical term with a normal complete sentence at first use.
- Distinguish BANK-OM ID, Git commit message, and Git commit SHA.
- Do not replace technical terms with unrelated metaphors such as 영수증, 요리,
  레시피, 짐, or 신호등.
- Do not invent friendly-sounding labels that are not real code or process terms.

### Ambiguity

- Every sentence must make the actor, object, action, condition, and result clear.
- Replace vague references such as 이것, 후보, 제품, 현재, or 적용 when more than
  one interpretation is possible.
- State whether a finding causes pass, review, block, or no automated decision.
- Use an actual example when a definition alone can be misread.

### Evidence-backed explanation

When introducing a configuration file, command, check, result field, or process term,
do not stop at a dictionary-style definition. Explain it with this compact sequence:

1. **Meaning** — what the item represents in this workflow.
2. **Timing** — when it is first created, when it is updated, and whether it is
   permanent, version-specific, or temporary.
3. **Actual use** — which command, component, or person reads it and for what decision.
4. **Concrete example** — show a real field, path, command, diff, or result from the
   current repository whenever available.
5. **Check and outcome** — state what is compared and whether mismatch causes pass,
   review, block, or no automated decision.

Separate information that Git or another tool can generate automatically from information
that requires a human decision. For example, Git can generate a changed-path list, but it
cannot decide the business invariant for a contract. If an item is optional only for a
specific strategy, label the strategy and do not present it as a universal prerequisite.

### Accuracy

- Separate implemented, tested, planned, and environment-pending behavior.
- Never describe a source-tested code version as deployed or used in production.
- Do not present a proposed field or workflow as currently supported.
- Confirm branch names, commit SHAs, file counts, gate behavior, and test status from
  the repository before writing them.

### Duplication and layout

- Remove repeated definitions, warnings, and status explanations.
- Keep one canonical explanation and refer to it elsewhere.
- Move optional detail into a collapsed section when the main flow becomes too long.
- Check tables, code blocks, labels, and expanded sections for wrapping or overflow.
- Prefer a short before/after example over a paragraph when both convey the same fact.

## Required final pass

Do not share until every answer is yes:

- Can a first-time reader explain the purpose without guessing?
- Can the reader follow purpose, preparation, process, checks, result, and next step?
- Is every term familiar or defined?
- Is each concept explained only once in the main flow?
- Are current and future behavior impossible to confuse?
- Does every status claim match the actual implementation and evidence?
- Is the rendered layout readable when details are expanded?

When updating a preview, follow the user's requested handoff format. If the user asked
for only the HTML link, return only that link.
