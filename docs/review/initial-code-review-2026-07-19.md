# Initial Code Review - 2026-07-19

## Findings (Ordered by Severity)

1. High - Invalid `cycle_key` can break main page rendering
- Evidence:
  - `cycle_key` is free text in [src/controle_financeiro/app.py](../../src/controle_financeiro/app.py#L33).
  - `service.get_summary(cycle_key)` is called without guard in [src/controle_financeiro/app.py](../../src/controle_financeiro/app.py#L35).
  - `parse_month_key` does not validate month range in [src/controle_financeiro/models.py](../../src/controle_financeiro/models.py#L27).
  - `cycle_window` is invoked while creating cycles in [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py#L128).
- Risk:
  - Inputs like `2026-13` may raise exceptions during page load and interrupt UI flow.
- Suggested action:
  - Add strict `cycle_key` validation (format + month range) before summary query.
  - Catch summary-load validation errors and show a user-friendly message.

2. High - Read operations have write side effects (implicit cycle creation)
- Evidence:
  - List/get methods call `_ensure_cycle`, which inserts new rows if cycle does not exist in [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py#L123).
  - Read APIs trigger `_ensure_cycle` in [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py#L215), [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py#L287), [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py#L349), and [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py#L413).
- Risk:
  - Passive reads create persistent data, making auditability and lifecycle semantics less explicit.
- Suggested action:
  - Separate read-only retrieval from explicit cycle creation/start behavior.
  - Keep auto-create only on first write operation, if that is the intended rule.

3. Medium - No DB-level guard for single current weekly checkpoint per date
- Evidence:
  - Uniqueness rule is enforced in code by setting old rows `is_current=False` before insert in [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py#L319).
  - There is no DB partial unique index on `(month_cycle_id, checkin_date)` filtered by `is_current=true` in [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py#L73).
- Risk:
  - Concurrent writes can violate the intended invariant and leave more than one current row.
- Suggested action:
  - Add a DB-level uniqueness strategy or a serialized transaction approach for this invariant.

4. Medium - Summary status thresholds are not directly tested
- Evidence:
  - Status branching logic is in [src/controle_financeiro/service.py](../../src/controle_financeiro/service.py#L86).
  - Existing tests in [tests/test_spec001_contract.py](../../tests/test_spec001_contract.py) do not assert all status branches and boundary values.
- Risk:
  - Future edits can silently change business behavior for status classification.
- Suggested action:
  - Add explicit tests for OPEN, HEALTHY, ATTENTION, and CRITICAL, including boundary thresholds.

## Open Questions

1. Should invalid cycle inputs fail fast with validation at UI level, or should service normalize/reject centrally?
2. Is automatic cycle creation on read intended as a product behavior, or only a bootstrap convenience?
3. Should weekly checkpoint invariants be strongly enforced at DB schema level for future multi-user or concurrent writes?

## Testing Gaps Summary

- Missing direct tests for `cycle_key` invalid month values.
- Missing direct tests for summary status boundaries.
- Missing tests for optional due-date persistence in variable expenses.