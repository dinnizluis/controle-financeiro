# AI Workflow

This repository uses Spec Kit with GitHub Copilot to keep each change spec-first.
The project constitution at [`.specify/memory/constitution.md`](../../.specify/memory/constitution.md)
defines the mandatory financial-integrity and quality rules.

## Feature Flow

1. Run `/speckit.refine` with the user-provided scope. It creates a proposed INVEST user story,
   Gherkin criteria, UI-flow and regression-test map, then creates one approved GitHub Feature
   Issue.
2. Review the backlog item: it must be independent, valuable, small, and testable. Split it before
   specification when it cannot be delivered as one reviewable slice.
3. Run `/speckit.specify` with the Issue reference to create `specs/<number>-<feature>/spec.md`.
4. Review the spec before code: confirm scope, business rules, acceptance scenarios, edge cases,
   financial-data impact, and what is out of scope.
5. Run `/speckit.clarify` when requirements are ambiguous; update the spec with the accepted answer.
6. Run `/speckit.plan` and review its constitution check, technical context, data impact, and tests.
7. Run `/speckit.tasks`; every changed business rule needs a deterministic pytest task, and every
   user-visible flow needs a mapped UI, domain, or persistence regression task.
8. Run `/speckit.analyze` and resolve inconsistencies between the spec, plan, and task list.
9. Run `/speckit.implement` for one small, reviewable slice at a time.
10. Run `/speckit.converge` after implementation. Address any appended tasks before the delivery is
    considered complete.
11. Open a pull request linking the Issue and Spec Kit artifacts, then complete the risk-first
    review and automated validation.

## Operating Rules

- GitHub Issues prioritize deliveries. `tasks.md` is the execution record; do not use
  `/speckit.taskstoissues` unless the team explicitly decides to split the delivery into separate
  trackable issues.
- `/speckit.refine` creates Issues only after explicit confirmation. It uses the `feature` and
  `backlog` labels; when GitHub CLI is unavailable, it saves the approved text under `backlog/`.
- New features use `specs/` as their versioned source of truth. Existing files in
  `docs/history/feature-specs/` remain historical records and are not migrated in bulk.
- A substantial follow-up creates a new feature directory and links to the superseded artifact.
- Copilot drafts, plans, implements, and reviews. A human approves business rules, financial-data
  impact, tests, and merge decisions.
- AI-generated code does not bypass tests, linting, type checks, dependency auditing, or human
  risk review.
- Use [Regression Testing](regression-testing.md) to map Gherkin criteria to pytest, Hypothesis,
  persistence, and Streamlit AppTest coverage.

## Local Validation

Run these commands before opening or updating a pull request:

```bash
.venv/bin/python -m pytest -q --cov=controle_financeiro --cov-report=term-missing
.venv/bin/python -m ruff format --check .
.venv/bin/python -m ruff check .
.venv/bin/python -m pyright
.venv/bin/python -m pip_audit
```