# Controle Financeiro Constitution

## Core Principles

### I. Preserve Financial Integrity

All monetary values use `Decimal` and are normalized to two decimal places. Cycle boundaries,
locks, and historical records are domain rules: a feature must not bypass them in the UI or
persistence layer. Any change that can alter stored financial data documents its impact and
provides a reversible or migration-safe path.

### II. Specify Before Implementing

Every feature begins with a versioned spec under `specs/`. The spec states the user outcome,
business rules, acceptance scenarios, edge cases, data impact, and explicit out-of-scope work.
The plan and task list remain aligned with the spec before implementation starts.

### III. Test the Risk First

Each changed business rule has a deterministic pytest case before or alongside its implementation.
Money normalization, date boundaries, cycle locking, summary calculation, and persistence
semantics receive focused tests. Property-based tests are reserved for invariants in domain and
persistence logic; Streamlit UI behavior uses targeted tests or manual acceptance evidence.

### IV. Keep Domain Boundaries Explicit

Business rules belong in the domain, service, or repository layers, not in Streamlit callbacks.
The UI orchestrates validated inputs and shows user-visible errors. Public contracts, persistence
schema changes, and service behavior changes are identified in the plan and reviewed together.

### V. Prefer the Smallest Verifiable Slice

Deliver independently testable user stories in priority order. Reuse the established Python,
Streamlit, SQLAlchemy, Pydantic, pytest, and Ruff patterns before introducing dependencies or
abstractions. New abstraction, storage technology, or external service requires a documented
reason and a simpler rejected alternative.

## Quality Gates

Before a pull request is merged, run pytest with coverage, `ruff format --check`, `ruff check`,
Pyright, and `pip-audit`. The PR links its GitHub Issue and Spec Kit artifacts, records the
commands run, and states any financial-data impact. A reviewer completes the risk-first checklist
for changes that affect money, cycle state, summaries, or historical data.

## Development Workflow

Use the flow `specify -> clarify when needed -> plan -> tasks -> analyze -> implement ->
converge`. Do not implement while the spec, plan, and task list disagree. GitHub Issues prioritize
deliveries; `tasks.md` is the detailed execution record and is not copied into separate issues by


## Governance

This constitution governs Spec Kit artifacts and implementation work. It complements the
Definition of Done and risk-first review checklist; when they conflict, choose the stricter
financial-integrity safeguard. Amendments require a documented reason, an updated version, and
review of affected templates, tests, and documentation.

**Version**: 1.0.0 | **Ratified**: 2026-07-31 | **Last Amended**: 2026-07-31
