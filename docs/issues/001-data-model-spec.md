# Issue 001: Data Modeling for MVP

## Problem

The project currently has only the setup scaffold. Before implementation, we need a clear and testable data model for the MVP so future code can be generated from stable business rules instead of assumptions.

## Goal

Define the minimum domain model for the first implementation phase of the budget app.

## In Scope

- Monthly period representation.
- Fixed monthly costs with optional due date.
- Weekly invoice check-ins for the current month.
- Month close record with income, final invoice total, and optional reserve cash outflow.
- Monthly variable expense representation with optional due date.
- Basic status and projection rules for the dashboard.

## Out of Scope

- Transaction import.
- Expense categorization.
- Multi-user support.
- Authentication.
- Advanced goals or net worth tracking.

## Proposed Domain Concepts

- `Month`
- `FixedCost`
- `VariableExpense`
- `WeeklyInvoiceCheckpoint`
- `MonthlyClose`
- `MonthSummary`

## Business Rules

- A month is identified by year and month.
- Fixed costs are monthly recurring items with a name, amount, active flag, and optional due date.
- Variable expenses are month-linked items with amount and optional due date.
- Weekly check-ins store the open invoice amount for a specific date within the current month.
- The month close stores the final invoice total and optional reserve cash outflow.
- A month accepts a single start and close event.
- The monthly cycle starts on the last business day of a month and ends on the second-to-last business day of the next month.
- Month closing is governed by the scheduled close date (`end_date`) of the cycle.
- Updates to cycle data are allowed through the scheduled close date (`end_date`).
- Updates are blocked from D+1 after the scheduled close date.
- A weekly check-in on an existing date must persist only the latest value as the current state.
- Weekly check-in history must be preserved.
- The dashboard must always show the latest weekly checkpoint as the current projected invoice state.
- The month summary must expose a projected margin and a simple status.

## Acceptance Criteria

- [ ] The MVP entities and value objects are listed and named consistently.
- [ ] The monthly lifecycle is clear: weekly check-ins, then month close.
- [ ] Expense entities support optional due date.
- [ ] The status rule for the month is defined in a deterministic way.
- [ ] The model excludes all non-MVP scope explicitly.
- [ ] The spec is small enough to be used as a reference for implementation.

## Technical Decisions

- Decision 01: Keep technical decisions in this spec (`spec001`) instead of splitting into a separate spec.
- Decision 02: Fixed costs are represented as month-by-month instances. Updates are direct on the current month instance (subject to cycle lock rules).

## Mini Technical Contract (Draft v0)

### General conventions

- Currency fields use decimal precision with 2 fractional digits.
- Date fields use ISO date format (`YYYY-MM-DD`).
- IDs are UUID strings.
- `created_at` and `updated_at` use UTC timestamps.

### Entity: MonthCycle

- Purpose: represent one monthly planning cycle.
- Unique key: `cycle_key` (`YYYY-MM`).
- Fields:
	- `id`: UUID.
	- `cycle_key`: string, required, unique.
	- `start_date`: date, required.
	- `end_date`: date, required.
	- `status`: enum (`open`, `closed`), required.
	- `closed_at`: timestamp, optional.
- Constraints:
	- `start_date` must be the last business day of month N.
	- `end_date` must be the second-to-last business day of month N+1.
	- Only one open cycle per `cycle_key`.
	- A cycle can be closed only once.
	- Data updates are allowed while `current_date <= end_date`.
	- On `current_date > end_date` (D+1 onward), cycle must be considered closed for updates.

### Entity: FixedCost

- Purpose: month-scoped fixed cost instance.
- Fields:
	- `id`: UUID.
	- `month_cycle_id`: UUID, required, FK to `MonthCycle.id`.
	- `name`: string (1-120), required.
	- `amount`: decimal(12,2), required, non-negative.
	- `due_date`: date, optional.
	- `is_active`: boolean, required, default `true`.
	- `created_at`: timestamp, required.
	- `updated_at`: timestamp, required.

### Entity: VariableExpense

- Purpose: month-linked variable expense entries.
- Fields:
	- `id`: UUID.
	- `month_cycle_id`: UUID, required, FK to `MonthCycle.id`.
	- `description`: string (1-160), required.
	- `amount`: decimal(12,2), required, non-negative.
	- `due_date`: date, optional.
	- `created_at`: timestamp, required.
	- `updated_at`: timestamp, required.

### Entity: WeeklyInvoiceCheckpoint

- Purpose: weekly snapshot of open card invoice.
- Fields:
	- `id`: UUID.
	- `month_cycle_id`: UUID, required, FK to `MonthCycle.id`.
	- `checkin_date`: date, required.
	- `open_invoice_total`: decimal(12,2), required, non-negative.
	- `is_current`: boolean, required, default `true`.
	- `created_at`: timestamp, required.
- Constraints:
	- Multiple rows may exist for the same `checkin_date` to preserve history.
	- Exactly one row is flagged as current for a pair (`month_cycle_id`, `checkin_date`).
	- On duplicate check-in date, insert a new row, set previous current row to `is_current=false`, and keep history.
	- Dashboard projection uses the latest current checkpoint in the cycle.

### Entity: MonthlyClose

- Purpose: close the cycle with final month values.
- Fields:
	- `id`: UUID.
	- `month_cycle_id`: UUID, required, unique, FK to `MonthCycle.id`.
	- `income_total`: decimal(12,2), required, non-negative.
	- `final_invoice_total`: decimal(12,2), required, non-negative.
	- `reserve_cash_outflow`: decimal(12,2), required, non-negative, default `0.00`.
	- `closed_at`: timestamp, required.
- Constraints:
	- One row per cycle.
	- Write/update allowed through the scheduled close date (`end_date`).
	- From D+1 after `end_date`, changes are blocked and closure is final.

### Read model: MonthSummary

- Purpose: dashboard projection and status.
- Inputs:
	- Active fixed costs in cycle.
	- Variable expenses in cycle.
	- Latest current weekly checkpoint.
	- Monthly close when available.
- Outputs:
	- `total_fixed_cost`.
	- `total_variable_expense`.
	- `latest_open_invoice_total`.
	- `projected_margin`.
	- `status` (`open`, `healthy`, `attention`, `critical`).

### Update semantics

- Initial load is mandatory before first weekly follow-up.
- Fixed cost behavior:
	- Fixed cost rows are monthly instances.
	- Through `end_date`, direct update is allowed on current month instances.
	- From D+1 after `end_date`, updates are blocked by cycle lock.
- Weekly check-in behavior:
	- New date: create a current checkpoint.
	- Duplicate date: create a new checkpoint as current and keep previous rows as history.
- Month close behavior:
	- Month close is tied to the scheduled close date of the cycle.
	- Through `end_date`, updates are allowed.
	- From D+1 after `end_date`, the cycle is locked for updates.
	- Any second close attempt in the same cycle after lock must be rejected.

## Edge Cases

- What happens if there is no weekly checkpoint yet?
	- Initial data load is required as a premise.
- What happens if the month is closed more than once?
	- Only one month start and one month close are accepted per monthly cycle.
	- Monthly cycle: from the last business day of month N to the second-to-last business day of month N+1.
- How should duplicate weekly check-ins on the same date be handled?
	- The most recent check-in value must always be persisted as current.
- Should the latest checkpoint replace the previous one or coexist as history?
	- It must replace the current value and still keep historical records.

## Notes for Implementation

- This issue should be used as the source of truth before writing the first domain code.
- The next step after this issue is to translate the spec into models and persistence rules.

## Amendment (2026-07-19): Weekly Check-in Removed

- Decision: remove `WeeklyInvoiceCheckpoint` entirely from scope and implementation.
- Rationale: the user's spending is almost entirely on credit card (to accumulate miles), and itemized variable expenses cover that same spend. Keeping both created a real double-counting risk in the projected margin formula (fixed + variable + open invoice total), not just a UX overlap.
- Trade-off accepted: loses weekly reconciliation against the bank-reported invoice and loses the intra-month trend view. Deemed acceptable for MVP; a future detailed invoice import is expected to provide deeper reconciliation instead.
- Impact: `WeeklyCheckinInput`, `WeeklyCheckinRecord`, `WeeklyInvoiceCheckpoint` ORM/table, related service/repository methods, and the UI tab are removed. `MonthSummary` no longer exposes `latest_open_invoice_total`. Open-cycle projected margin is now `-(total_fixed_cost + total_variable_expense)`.
