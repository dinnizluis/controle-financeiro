# Issue 002: Data Entry and Visualization for Cycle Operations

## Context

The data model and persistence rules from spec001 are implemented. The current UI allows basic writes but lacks operator-grade visibility and edit workflows, which makes monthly follow-up slower and more error-prone.

## Objective

Deliver the next MVP slice so users can create, edit, and review cycle data in one place with clear feedback and basic filtering.

## In Scope

- Create and edit fixed costs in the selected cycle.
- Create and edit variable expenses in the selected cycle.
- Create and edit month income (income total and reserve cash outflow) until cycle lock.
- Show per-entity table views in the UI for the selected cycle.
- Add basic filters/sorting to improve data inspection.

## Out of Scope

- Delete flows.
- Charts and trend analytics.
- Transaction import.
- Expense categorization.
- Multi-user support and authentication.
- Weekly invoice check-in (removed from scope entirely; see amendment in [001-data-model-spec.md](001-data-model-spec.md)).
- Final invoice total tracking as part of month income (removed; see amendment in [001-data-model-spec.md](001-data-model-spec.md)).

## Business Rules

- Cycle key validation remains strict (`YYYY-MM` with valid month).
- Lock rules remain unchanged: writes are allowed through `end_date` and blocked from D+1.
- Summary metrics must remain consistent after create/edit operations.
- Error states (validation and lock) must be user-visible and non-breaking.

## Acceptance Criteria

- [ ] Users can create fixed costs, variable expenses, and month income from the UI.
- [ ] Users can edit fixed costs and variable expenses from the UI and changes persist correctly.
- [ ] Users can update month income while cycle is unlocked.
- [ ] Each tab shows a table with cycle data and supports basic filter/sort controls.
- [ ] Lock violations are shown as explicit UI errors without crashing the page.
- [ ] Contract tests cover at least one edit flow and one lock-rejection flow used by the UI.

## Edge Cases

- Invalid cycle key should stop execution with a clear message.
- Empty cycle should show empty-state guidance instead of failing.
- Sorting with optional due dates should remain deterministic when values are missing.
- Updating records at lock boundary date should succeed; D+1 should fail.