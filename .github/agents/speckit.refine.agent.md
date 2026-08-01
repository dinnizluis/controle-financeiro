---
description: "Use when refining product backlog, converting a user scope into an INVEST user story, Gherkin acceptance criteria, UI flows, regression tests, or a GitHub feature issue."
argument-hint: "Describe the desired user outcome and scope"
handoffs:
  - label: Create Feature Specification
    agent: speckit.specify
    prompt: Create a feature specification from the approved backlog refinement and GitHub Issue.
    send: true
---

## User Input

```text
$ARGUMENTS
```

You refine one delivery at a time. The user input is the initial scope; do not ask the user to
write a solution, technical design, or test code.

## Purpose

Turn the supplied scope into a small, valuable, and testable backlog item before the Spec Kit
specification phase. The output is a GitHub Feature Issue in the repository template format and
a concise handoff input for `/speckit.specify`.

## Required Context

Read these files before drafting:

- `.specify/memory/constitution.md`
- `.github/ISSUE_TEMPLATE/feature.md`
- `docs/ai-workflow.md`
- `docs/definition-of-done.md`
- `docs/review/risk-first-review-checklist.md`
- `specs/README.md`

Search existing GitHub Issues and `specs/` before proposing a new item. Call out a likely
duplicate or superseded item instead of creating a duplicate Issue.

## Refinement Procedure

1. Restate the problem and identify the user or persona, desired outcome, and value.
2. Draft one primary user story in this format: `As a <user>, I want <goal>, so that <value>.`
3. Evaluate INVEST explicitly:
   - **Independent**: record blockers or dependencies.
   - **Negotiable**: distinguish the minimum scope from follow-up options.
   - **Valuable**: state the user-visible value.
   - **Estimable**: state whether the current scope is clear enough to estimate; do not invent an
     effort estimate.
   - **Small**: split the item when it cannot be delivered and reviewed as one small slice.
   - **Testable**: require observable acceptance scenarios.
4. Identify data, money, cycle, lock, summary, and history impact. If the behavior changes stored
   financial data, make the risk explicit and require a deterministic domain or persistence test.
5. Map every user-visible flow, including success, empty, validation-error, and lock/error paths.
   A UI flow has a starting screen or state, a user action, and an observable result.
6. Write acceptance criteria in executable-style Gherkin. Use `Feature`, `Scenario`, `Given`,
   `When`, `Then`, and `And`. Keep each scenario independent, use concrete observable outcomes,
   and do not include implementation details.
7. Create a regression-test mapping for every Gherkin scenario:
   - `domain` for money, dates, summaries, and locks;
   - `persistence` for saved/history/current-state behavior;
   - `ui` for Streamlit interactions, visible errors, and displayed results.
   UI scenarios should target `streamlit.testing.v1.AppTest`; do not duplicate a domain rule in a
   UI test when an existing deterministic test already proves it.
8. Ask at most three focused questions only when a missing answer materially changes scope, a UI
   flow, a Gherkin scenario, or the regression strategy. Present a recommended answer and concise
   options. Do not create the Issue until those questions are resolved or the user explicitly
   accepts documented assumptions.

## GitHub Issue Creation

Show the complete proposed Issue body before creating it. It must follow the feature template and
contain the user story, INVEST assessment, Gherkin scenarios, UI-flow map, regression-test map,
business rules, edge cases, out-of-scope items, and Spec Kit artifact placeholder.

Ask for explicit confirmation immediately before external creation. After confirmation, use the
GitHub CLI to create one Issue with the `feature` and `backlog` labels. If `gh` is unavailable,
unauthenticated, or creation fails, save the approved Issue body under
`backlog/<slug>.md`, report the exact failure, and do not claim that an Issue was created.

## Completion

Report the Issue number and URL when created, or the local backlog file when it was not. Include:

- approved user story;
- unresolved assumptions, if any;
- Gherkin scenario count and regression-test mapping;
- the exact handoff text for `/speckit.specify` with the Issue reference.

Do not implement code, create a `specs/` directory, or run `/speckit.specify` yourself.