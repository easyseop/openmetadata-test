---
name: clarity-preflight-review
description: Review user-facing HTML, guides, reports, handoff documents, and operating manuals before sharing them. Detect duplicated information, unexplained terms, sentence-level ambiguity, misleading implementation status, missing examples or recovery steps, and layouts or procedures that a first-time employee cannot follow independently.
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
- Review sentence by sentence. For each sentence, ask whether two readers could
  reasonably assign different actors, inputs, time points, comparison targets, or
  outcomes. Rewrite the sentence until only one operational interpretation remains.
- After every paragraph, write down the first question a new employee would ask.
  If the visible text does not already answer it, add the answer at that point instead
  of relying on a later glossary or the author's background knowledge.
- Replace vague references such as 이것, 후보, 제품, 현재, or 적용 when more than
  one interpretation is possible.
- Detect contextless transitions: a question, answer, warning, example, or term must
  not appear unless the immediately preceding flow makes clear what it refers to.
  Remove orphaned phrases such as "왜 임시 기준인가?", "이 규칙은", "여기서",
  or "그 결과" when the sentence that introduced the 기준, 규칙, place, or result
  was deleted, moved, or renamed.
- Treat a newly appearing word as unexplained even if it is defined later. Either
  introduce it at the point where the process first needs it, or remove it from the
  main flow and keep the internal detail in a collapsed section.
- State whether a finding causes pass, review, block, or no automated decision.
- Use an actual example when a definition alone can be misread. For a field, command,
  check, or operator action, prefer one normal example and one failure example when
  the failure response is not obvious.

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

### First-time operator completeness

Treat a guide as incomplete unless a new employee can perform the work without asking
the author for a missing step. Each executable procedure must state:

1. the exact repository, branch or version, working directory, required files, tools,
   permissions, and environment assumptions;
2. who performs the step and which parts are automatic versus human decisions;
3. the command or UI action, including placeholders and where each value comes from;
4. the expected output file or screen and a real successful example;
5. every result label the operator can receive and the next action for each label;
6. how to recover from a common failure, what to edit, and which checks to rerun;
7. the evidence to retain, its storage location, and the exact completion condition;
8. when the operator must stop and escalate rather than choose a code or business
   resolution alone.

Maintain an example-coverage check while reviewing. Every management-file field, gate,
branch operation, generated artifact, and approval action must have a concrete example
somewhere in the guide, or be explicitly marked as a reference-only item that the
operator does not perform.

### Repeated-question prevention

Before sharing, review the user's earlier questions and group repeated questions by
concept. For every concept that was asked more than once, confirm that the explanation
now answers all of the following at the first point of use:

1. why the concept exists;
2. who creates or decides it;
3. when it is created and updated;
4. whether the step is automatic or requires human judgment;
5. one concrete value or command from the current repository;
6. which check reads it and how the result changes;
7. how it differs from the nearest similar concept.

Then ask the question again as a first-time reader. If the visible explanation still
permits the same question, revise the artifact before sharing. Do not rely on a later
glossary to repair an ambiguity introduced earlier.

## Required final pass

Do not share until every answer is yes:

- Can a first-time reader explain the purpose without guessing?
- Can the reader follow purpose, preparation, process, checks, result, and next step?
- Is every term familiar or defined?
- Does every question, warning, pronoun, and transition have an explicit referent in
  the immediately visible context?
- Is each concept explained only once in the main flow?
- Are current and future behavior impossible to confuse?
- Does every status claim match the actual implementation and evidence?
- Is the rendered layout readable when details are expanded?
- Can a new employee complete preparation, execution, result interpretation, failure
  recovery, rerun, evidence retention, and handoff using this guide alone?
- Does every executable feature have a normal example and, where useful, a failure
  example with the required response?
- Would the user's previously repeated questions be answered at the exact point where
  the relevant term first appears?

When updating a preview, follow the user's requested handoff format. If the user asked
for only the HTML link, return only that link.
