# AI Workflow

This repository uses Spec Kit with GitHub Copilot to keep each change spec-first.
The project constitution at [`.specify/memory/constitution.md`](../.specify/memory/constitution.md)
defines the mandatory financial-integrity and quality rules.

## Feature Flow

1. Create or select one GitHub Issue for the delivery.
2. Run `/speckit.specify` to create `specs/<number>-<feature>/spec.md`.
3. Review the spec before code: confirm scope, business rules, acceptance scenarios, edge cases,
	 financial-data impact, and what is out of scope.
4. Run `/speckit.clarify` when requirements are ambiguous; update the spec with the accepted answer.
5. Run `/speckit.plan` and review its constitution check, technical context, data impact, and tests.
6. Run `/speckit.tasks`; every changed business rule needs a deterministic pytest task.
7. Run `/speckit.analyze` and resolve inconsistencies between the spec, plan, and task list.
8. Run `/speckit.implement` for one small, reviewable slice at a time.
9. Run `/speckit.converge` after implementation. Address any appended tasks before the delivery is
	 considered complete.
10. Open a pull request linking the Issue and Spec Kit artifacts, then complete the risk-first
		review and automated validation.

## Operating Rules

- GitHub Issues prioritize deliveries. `tasks.md` is the execution record; do not use
	`/speckit.taskstoissues` unless the team explicitly decides to split the delivery into separate
	trackable issues.
- New features use `specs/` as their versioned source of truth. Existing files in `docs/issues/`
	remain historical records and are not migrated in bulk.
- A substantial follow-up creates a new feature directory and links to the superseded artifact.
- Copilot drafts, plans, implements, and reviews. A human approves business rules, financial-data
	impact, tests, and merge decisions.
- AI-generated code does not bypass tests, linting, type checks, dependency auditing, or human
	risk review.

## Local Validation

Run these commands before opening or updating a pull request:

```bash
.venv/bin/python -m pytest -q --cov=controle_financeiro --cov-report=term-missing
.venv/bin/python -m ruff format --check .
.venv/bin/python -m ruff check .
.venv/bin/python -m pyright
.venv/bin/python -m pip_audit
```
