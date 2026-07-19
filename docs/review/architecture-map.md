# Architecture Map

## Purpose

Provide a fast, high-confidence understanding of the current implementation flow from UI to persistence.

## Runtime Entry Points

- [streamlit_app.py](../../streamlit_app.py): Adds `src/` to `sys.path` and delegates execution to `controle_financeiro.app.main`.
- [src/controle_financeiro/app.py](../../src/controle_financeiro/app.py): Streamlit UI entrypoint, forms, and service orchestration.

## Layered Structure

1. UI Layer
- [src/controle_financeiro/app.py](../../src/controle_financeiro/app.py)
- Responsibilities:
  - Render dashboard metrics and forms.
  - Parse user input into domain input models.
  - Catch domain/storage errors and display messages.

2. Application Service Layer
- [src/controle_financeiro/service.py](../../src/controle_financeiro/service.py)
- Responsibilities:
  - Expose use-case methods (`add_*`, `update_*`, `list_*`, `save_monthly_close`).
  - Aggregate month summary data from repository reads.

3. Domain Model Layer
- [src/controle_financeiro/models.py](../../src/controle_financeiro/models.py)
- Responsibilities:
  - Define input contracts via Pydantic models.
  - Normalize monetary values with 2-decimal precision.
  - Define cycle window calculations and status enums.

4. Persistence Layer
- [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py)
- Responsibilities:
  - Define SQLAlchemy ORM tables.
  - Enforce cycle lock semantics (`current_date > end_date` blocks updates).
  - Persist and query records for fixed costs, variable expenses, check-ins, and month close.

## Main Data Flow

1. User submits a Streamlit form in [src/controle_financeiro/app.py](../../src/controle_financeiro/app.py).
2. UI builds a domain input model from `models.py`.
3. UI calls a method on `BudgetService` in [src/controle_financeiro/service.py](../../src/controle_financeiro/service.py).
4. Service delegates write/read to `SqliteBudgetRepository` in [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py).
5. Repository ensures cycle existence, applies lock checks, and commits.
6. UI displays success/error and refreshes summary from `service.get_summary`.

## Domain-Critical Behaviors

- Cycle boundaries are derived from business days via `cycle_window` in [src/controle_financeiro/models.py](../../src/controle_financeiro/models.py).
- Lock behavior is enforced centrally in `_assert_unlocked` in [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py).
- Weekly duplicate check-ins keep history and switch current-state semantics in repository save logic.
- Summary status and projected margin are computed in `BudgetService.get_summary` in [src/controle_financeiro/service.py](../../src/controle_financeiro/service.py).

## Current Coupling Hotspots

- `BudgetService` currently depends on concrete `SqliteBudgetRepository` type instead of an abstract protocol.
- UI directly converts numeric inputs to `Decimal`, combining presentation and domain conversion concerns.
- App-level behavior and repository lock rules are strongly coupled through `DomainLockError` handling.

## Review Anchors

- Source-of-truth spec: [docs/issues/001-data-model-spec.md](../issues/001-data-model-spec.md)
- Contract tests: [tests/test_spec001_contract.py](../../tests/test_spec001_contract.py)
- Workflow constraints: [docs/ai-workflow.md](../ai-workflow.md)