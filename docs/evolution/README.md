# Versioned Evolution Plans

Use this directory to record approved, versioned plans for the product and technical evolution of
the repository.

## Naming Convention

Create one file per evolution plan using:

```text
YYYY-MM-DD-short-slug.md
```

Example:

```text
2026-08-15-expense-categorization-roadmap.md
```

## Recommended Sections

1. Context
2. Current State
3. Target State
4. Incremental Milestones
5. Dependencies and Risks
6. Validation Strategy
7. Superseded Plans or Related Specs

## Versioning Rules

- Never overwrite a published plan silently; create a new dated file when the direction changes.
- Link each plan to the relevant issue, spec, or review artifact.
- When a plan becomes obsolete, keep it for auditability and mark the newer plan that supersedes it.

## Current Plans

- [2026-07-31-mvp-foundation-plan.md](2026-07-31-mvp-foundation-plan.md): first versioned plan
	for the application MVP, backlog themes, milestones, and validation strategy.
- [2026-08-01-authentication-and-publishing-plan.md](2026-08-01-authentication-and-publishing-plan.md):
	security plan that makes authentication, authorization, and publish-readiness mandatory before
	hosting sensitive personal financial data.