# MVP Foundation Plan

**Date**: 2026-07-31

## Context

This plan captures the first versioned direction for the application based on the initial product
vision: make monthly financial planning easy enough to keep current and reliable.

The core problem is operational friction:

- updating the plan takes effort;
- stale data reduces trust in the numbers;
- reduced trust leads to worse short-term decisions.

This document translates that initial direction into a versioned evolution plan aligned with the
current repository structure, the active Spec Kit workflow, and the financial-integrity rules of
the project constitution.

## Current State

The repository already has a working Python and Streamlit baseline with the Agentic Development
Life Cycle installed.

What is already established:

- Streamlit application, domain layer, service layer, and SQLite persistence.
- Spec Kit flow with `/speckit.refine`, `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`,
  `/speckit.analyze`, `/speckit.implement`, and `/speckit.converge`.
- Quality gates with pytest, Ruff, Pyright, pip-audit, and GitHub Actions.
- Feature specs under `specs/` and historical specs archived under
  `docs/history/feature-specs/`.

Important alignment note:

- The original draft proposed a monthly "credit card invoice total" record.
- The current repository intentionally superseded that approach because it created real
  double-counting risk in the monthly projection.
- The active model uses fixed costs, itemized variable expenses, and monthly income plus optional
  reserve cash outflow.

## Target State

Deliver a small, trustworthy monthly control workflow that is fast to update and easy to validate.

### MVP Scope

In scope for the first usable version:

1. Register monthly fixed costs.
2. Register monthly income.
3. Register optional cash outflow from reserve.
4. Register variable monthly expenses as the source of spend visibility.
5. Show a monthly dashboard with:
   - total income,
   - total costs,
   - projected available margin,
   - simple month status.
6. Show simple month-to-month history with totals.

Out of scope for this phase:

1. Detailed bank or card import (segment installments).
2. Automatic transaction categorization.
3. Full financial goals and net-worth management.
4. Multi-user support and authentication.
5. Advanced analytics, charts, or reconciliation flows.

### Architectural Direction

Recommended stack for the MVP and near-term evolution:

- App: Streamlit with Python.
- Storage: local SQLite.
- Data access: SQLAlchemy.
- Input validation: Pydantic.
- Tests: pytest and targeted AppTest coverage.
- Quality: Ruff, Pyright, pip-audit, and GitHub Actions.

Rationale:

- lowest friction for a solo Python workflow;
- fastest path to a usable UI;
- small operational footprint;
- strong fit with the existing codebase and installed ADLC.

Alternative reserved for a later transition:

- FastAPI plus Jinja2 if the project later needs a more explicit web architecture or deployment
  model.
- This is not the preferred path for the current phase because it adds complexity before the core
  monthly workflow is stable.

## Incremental Milestones

The initial draft used a five-day cadence. In the repository, treat these as five incremental
milestones that can each become one or more refined backlog items.

### Milestone 1: Executable Foundation

Goal: ensure the application opens, persists data, and can be worked on safely.

Target outcomes:

1. Project structure, environment, and local execution are stable.
2. Streamlit app starts cleanly.
3. SQLite persistence is wired and can store the first records.
4. Basic onboarding and ADLC guidance are available in the repository.

### Milestone 2: Fixed Costs Workflow

Goal: make recurring monthly obligations easy to maintain.

Target outcomes:

1. Create and edit fixed monthly costs.
2. Show active fixed costs for the selected cycle.
3. Validate required fields and money inputs.
4. Keep cycle-lock behavior explicit in the UI.

### Milestone 3: Monthly Income and Reserve Workflow

Goal: capture the minimum monthly inputs needed for useful projections.

Target outcomes:

1. Register monthly income.
2. Register optional reserve cash outflow.
3. Maintain itemized variable expenses instead of a single card-invoice total.
4. Display projected monthly margin from persisted data.

### Milestone 4: Monthly View and History

Goal: make the current month legible and preserve lightweight historical comparison.

Target outcomes:

1. Dashboard with the key monthly values.
2. History view with month-level totals.
3. Better UI readability without introducing design-heavy complexity.

### Milestone 5: Quality Baseline and MVP Closure

Goal: close the first MVP with enough confidence to use real data continuously.

Target outcomes:

1. Deterministic tests for critical business rules.
2. Linting, formatting, type checks, and automated CI gates.
3. Updated onboarding and monthly usage guidance.
4. One real-month validation pass using actual user data.

## ADLC and Delivery Rules

The initial draft required spec-first delivery. In this repository, that rule is enforced through
the active Copilot workflow.

Required operating model:

1. Start every new delivery with `/speckit.refine`.
2. Convert the user scope into one INVEST story with Gherkin acceptance criteria.
3. Create or approve a GitHub Issue only after the body is explicit and testable.
4. Generate the feature spec under `specs/` with `/speckit.specify`.
5. Clarify ambiguity before planning or coding.
6. Plan and task each delivery with explicit regression mapping.
7. Implement only after the spec, plan, and tasks agree.
8. Close the feature only when the Definition of Done and acceptance checklist are satisfied.

Required repository assets for this phase:

1. README with setup and flow guidance.
2. Feature issue template.
3. Pull request template.
4. Acceptance checklist.
5. Versioned feature specs and plans.
6. Initial MVP backlog derived from this roadmap.

## Backlog Seed

This plan should seed the first set of refined backlog items.

Recommended initial backlog themes:

1. Executable foundation and local workflow.
2. Fixed costs management.
3. Variable expenses management.
4. Monthly income and reserve tracking.
5. Dashboard and month summary presentation.
6. Historical totals view.
7. Quality baseline and regression coverage.

These are planning themes, not implementation tasks. Each theme should be split through
`/speckit.refine` into a small, testable feature slice.

## Dependencies and Risks

### Primary Dependencies

1. Local Python environment with the repository `.venv`.
2. Stable SQLite persistence and migration-safe schema changes.
3. GitHub Issues and PR workflow.
4. Continued discipline around ADLC artifacts and quality gates.

### Main Risks and Mitigations

1. Risk: loss of momentum from slow visible progress.
   Mitigation: keep slices small and ensure every milestone yields a visible user-facing outcome.
2. Risk: MVP scope expands too early.
   Mitigation: keep this plan frozen for the first baseline and send new ideas to backlog refinement.
3. Risk: low confidence in calculations.
   Mitigation: prioritize deterministic tests for margin, totals, dates, and cycle-lock behavior,
   then validate one real month manually.
4. Risk: technical complexity grows before the workflow is stable.
   Mitigation: defer authentication, imports, reconciliation, and integration-heavy features.
5. Risk: roadmap drift from the implemented model.
   Mitigation: keep future revisions explicit when the target state changes; do not silently edit
   this document after it has been used as a reference.

## Validation Strategy

This plan is considered useful only if it improves delivery discipline and leads to a usable,
trustworthy monthly workflow.

Validation criteria:

1. Each milestone is represented by one or more refined issues and versioned specs.
2. Business-rule changes are covered by deterministic tests.
3. User-visible flows have mapped regression coverage at the right layer.
4. The `quality` workflow stays green across roadmap increments.
5. A real-month dry run confirms the resulting dashboard and totals are trustworthy enough for
   weekly or monthly use.

## Immediate Next Steps

1. Refine the first backlog slice from this plan with `/speckit.refine`.
2. Decide whether the first delivery focus is fixed costs, variable expenses, or historical totals.
3. Generate the corresponding feature spec under `specs/`.
4. Use this plan as the high-level reference when evaluating roadmap tradeoffs.

## Superseded Plans or Related Specs

- Source draft: [PlanoInicial.md](/Users/luisdiniz/Desktop/PlanoInicial.md)
- Workflow guide: [docs/process/ai-workflow.md](../process/ai-workflow.md)
- Definition of Done: [docs/process/definition-of-done.md](../process/definition-of-done.md)
- Acceptance checklist: [docs/process/acceptance-checklist.md](../process/acceptance-checklist.md)
- Historical domain direction: [docs/history/feature-specs/001-data-model-spec.md](../history/feature-specs/001-data-model-spec.md)
- Historical UI direction: [docs/history/feature-specs/002-data-entry-visualization-spec.md](../history/feature-specs/002-data-entry-visualization-spec.md)

This is the first version of the application evolution plan. Future changes in strategy should
create a new dated file that supersedes this one.