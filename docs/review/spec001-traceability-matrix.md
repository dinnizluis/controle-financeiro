# Spec001 Traceability Matrix

## How To Use

1. Start from the requirement statement in [docs/issues/001-data-model-spec.md](../issues/001-data-model-spec.md).
2. Confirm implementation pointers.
3. Confirm test evidence in [tests/test_spec001_contract.py](../../tests/test_spec001_contract.py).
4. Mark gaps explicitly.

## Matrix

| Spec Rule | Implementation Pointer | Test Evidence | Status | Gap Notes |
|---|---|---|---|---|
| `cycle_key` format and month validity are enforced before cycle usage | `parse_month_key` in [src/controle_financeiro/models.py](../../src/controle_financeiro/models.py) and summary guard in [src/controle_financeiro/app.py](../../src/controle_financeiro/app.py) | `test_invalid_cycle_key_month_is_rejected` in [tests/test_spec001_contract.py](../../tests/test_spec001_contract.py) | Covered |  |
| Currency uses decimal precision with 2 fractional digits | `as_money` in [src/controle_financeiro/models.py](../../src/controle_financeiro/models.py) and Numeric(12,2) fields in [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py) | Indirectly covered in all value assertions | Partial | Add dedicated rounding edge-case test |
| `cycle_key` lifecycle boundaries follow business-day rule | `cycle_window`, `last_business_day`, `second_to_last_business_day` in [src/controle_financeiro/models.py](../../src/controle_financeiro/models.py) | `test_cycle_window_matches_business_day_rule` in [tests/test_spec001_contract.py](../../tests/test_spec001_contract.py) | Covered |  |
| Updates allowed through `end_date`, blocked from D+1 | `_assert_unlocked` in [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py) | `test_updates_allowed_through_end_date_blocked_d_plus_one` and monthly close lock test in [tests/test_spec001_contract.py](../../tests/test_spec001_contract.py) | Covered |  |
| Fixed costs are month-scoped instances and direct update allowed pre-lock | `save_fixed_cost` update path in [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py) | `test_fixed_cost_month_instance_allows_direct_update_before_lock` in [tests/test_spec001_contract.py](../../tests/test_spec001_contract.py) | Covered |  |
| Variable expenses support optional due date | `VariableExpenseInput.due_date` in [src/controle_financeiro/models.py](../../src/controle_financeiro/models.py) and ORM `due_date` in [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py) | No direct test for due_date persistence | Gap | Add contract test for create/read with due date |
| Duplicate weekly check-ins keep history and switch current row | Removed (2026-07-19): `WeeklyInvoiceCheckpoint` was removed from scope per amendment in [docs/issues/001-data-model-spec.md](../issues/001-data-model-spec.md) | N/A | Removed | Superseded by itemized variable expenses; see amendment rationale |
| Month close has one row per cycle and can update until lock | `save_monthly_close` in [src/controle_financeiro/storage.py](../../src/controle_financeiro/storage.py) | `test_monthly_close_can_update_until_end_date_then_locks` in [tests/test_spec001_contract.py](../../tests/test_spec001_contract.py) | Covered |  |
| Summary exposes deterministic status and projected margin | `BudgetService.get_summary` in [src/controle_financeiro/service.py](../../src/controle_financeiro/service.py) | `test_summary_status_thresholds_after_monthly_close` and `test_summary_status_open_without_monthly_close` in [tests/test_spec001_contract.py](../../tests/test_spec001_contract.py) | Covered |  |

## Exit Criteria

- Every row is either `Covered` or has a tracked `Gap Notes` action.
- Any `Gap` has an associated test task before feature expansion.