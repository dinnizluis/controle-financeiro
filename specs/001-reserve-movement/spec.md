# Feature Specification: Reserve Movement in the Monthly Cycle

**Feature Branch**: `001-reserve-movement`

**Created**: 2026-08-01

**Status**: Draft

**Input**: User description: "Escopo Funcional: Movimentação da Reserva de Emergência no Ciclo — permitir registrar aporte e saque da reserva de emergência no ciclo mensal, para visualizar rapidamente a saúde do orçamento do mês. Aporte reduz a margem projetada (despesa); saque é informativo e não reduz a margem, pois nunca vai para a fatura. Despesa variável pode ser marcada como paga com saque da reserva, excluindo-a do subtotal que reduz a margem de crédito. Dashboard mostra aporte, saque e despesas via reserva do ciclo, com alerta quando há saque."

**Related Backlog Item**: [GitHub Issue #4](https://github.com/dinnizluis/controle-financeiro/issues/4)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record a reserve contribution (aporte) (Priority: P1)

A user closing out their monthly budget wants to record money moved from this month's budget into
their emergency reserve, so that the projected credit-card margin reflects that money as spent
this cycle.

**Why this priority**: Without this, the projected margin can overstate available credit room by
ignoring money that has already left the month's budget toward savings. This is the core value of
the feature and the simplest of the three behaviors to deliver.

**Independent Test**: Can be fully tested by setting a reserve contribution amount on an open
cycle's income record and confirming the projected margin decreases by that amount.

**Acceptance Scenarios**:

1. **Given** an open cycle with an income record and no reserve contribution, **When** the user
   sets a reserve contribution amount and saves, **Then** the projected margin decreases by that
   amount.
2. **Given** an open cycle with an existing reserve contribution, **When** the user updates the
   amount to a new value, **Then** the projected margin recalculates using the new value.

---

### User Story 2 - Record a reserve withdrawal (saque) as an informational alert (Priority: P2)

A user who paid a cash expense out of their emergency reserve this month wants to record that
withdrawal so the dashboard reflects that the reserve was tapped, without it affecting the credit
margin (since that cash never goes to the credit-card invoice).

**Why this priority**: This is the budget-health signal the user explicitly asked for ("alerta
visível quando houver saque"). It depends on the contribution field existing on the same record
but is independently valuable and testable on its own.

**Independent Test**: Can be fully tested by setting a reserve withdrawal amount on an open cycle
and confirming the projected margin is unchanged while the dashboard shows the withdrawal value
and a visible alert.

**Acceptance Scenarios**:

1. **Given** an open cycle with an income record and no reserve withdrawal, **When** the user sets
   a reserve withdrawal amount and saves, **Then** the projected margin does not change.
2. **Given** a cycle with a reserve withdrawal greater than zero, **When** the user opens the
   cycle dashboard, **Then** the withdrawal amount is shown together with a visible alert.
3. **Given** a cycle with no reserve withdrawal recorded, **When** the user opens the cycle
   dashboard, **Then** no reserve-withdrawal alert is shown.

---

### User Story 3 - Mark a variable expense as paid via reserve withdrawal (Priority: P3)

A user who paid a variable expense in cash from the reserve (instead of on credit) wants to flag
that expense so it is not also counted against the credit-card margin, avoiding double-counting
the same spend once as a withdrawal and once as a credit expense.

**Why this priority**: This closes the double-counting risk explicitly called out in the request.
It is the most specific of the three behaviors and builds on the dashboard visibility delivered by
User Story 2.

**Independent Test**: Can be fully tested by flagging an existing variable expense as paid via
reserve withdrawal and confirming it is excluded from the total that reduces the projected margin
while still appearing in a reserve-paid expenses total.

**Acceptance Scenarios**:

1. **Given** an open cycle with a variable expense not flagged as reserve-paid, **When** the user
   marks it as paid via reserve withdrawal and saves, **Then** the expense is excluded from the
   variable-expense subtotal used in the projected margin.
2. **Given** an expense previously flagged as reserve-paid, **When** the user unmarks it, **Then**
   it is included again in the variable-expense subtotal used in the projected margin on the next
   save.
3. **Given** a cycle with one or more reserve-paid expenses, **When** the user opens the cycle
   dashboard, **Then** the total of reserve-paid expenses is shown alongside the contribution and
   withdrawal indicators.

---

### Edge Cases

- What happens when no income record exists yet for the cycle? Reserve contribution and
  withdrawal are treated as `0.00`, matching current default behavior for related income fields.
- What happens when a cycle has both a reserve withdrawal and reserve-paid expenses that do not
  match in value? Both values are shown side by side; no automatic reconciliation or warning about
  the mismatch is required.
- What happens when a user attempts to change reserve contribution, withdrawal, or the
  reserve-paid flag after the cycle's scheduled close date (`end_date`)? The update is rejected
  with a visible lock error, consistent with existing cycle-lock behavior.
- What happens at the lock boundary date itself (`current_date == end_date`)? The update is still
  allowed; only D+1 onward is blocked.
- What happens when multiple variable expenses are flagged as reserve-paid in the same cycle? All
  flagged expenses are excluded from the margin-reducing subtotal and all summed into the
  reserve-paid total shown on the dashboard.

## Acceptance Criteria and Regression Map *(mandatory)*

### Gherkin Scenarios

```gherkin
Feature: Reserve movement in the monthly cycle

  Scenario: User records a reserve contribution
    Given the selected cycle is open and has an income record
    When the user sets a reserve contribution amount and saves
    Then the projected margin reflects the contribution as a reduction

  Scenario: User records a reserve withdrawal
    Given the selected cycle is open and has an income record
    When the user sets a reserve withdrawal amount and saves
    Then the projected margin does not change because of the withdrawal
    And the dashboard shows the withdrawal amount with a visible alert

  Scenario: User marks a variable expense as paid via reserve withdrawal
    Given the selected cycle has a variable expense paid with credit
    When the user marks that expense as paid with reserve withdrawal and saves
    Then the expense is excluded from the total that reduces the projected margin
    And the expense still appears in the reserve-paid expenses list and total

  Scenario: Dashboard shows reserve indicators with no reserve activity
    Given the selected cycle has no reserve contribution or withdrawal recorded
    When the user opens the cycle dashboard
    Then the reserve contribution, withdrawal, and reserve-paid totals show as zero
    And no reserve-withdrawal alert is shown

  Scenario: Reserve fields are locked after cycle close date
    Given the selected cycle's end_date has passed
    When the user attempts to update reserve contribution, withdrawal, or the expense flag
    Then the update is rejected with a visible lock error
```

Write one independent scenario for each primary flow and include error, empty, validation, and
locked-state scenarios where relevant. Do not use implementation details in Gherkin steps.

### UI Flow and Regression Test Map

| Gherkin scenario | Starting screen or state | User action | Observable result | Test layer | Planned test |
|------------------|--------------------------|-------------|-------------------|------------|--------------|
| User records a reserve contribution | Income form, open cycle | Set reserve contribution amount, save | Projected margin decreases by that amount | domain | `tests/test_spec001_contract.py::test_reserve_contribution_reduces_margin` |
| User records a reserve withdrawal | Income form, open cycle | Set reserve withdrawal amount, save | Projected margin unchanged; withdrawal stored | domain | `tests/test_spec001_contract.py::test_reserve_withdrawal_does_not_affect_margin` |
| User marks a variable expense as paid via reserve withdrawal | Variable expense form, open cycle | Mark expense as reserve-paid, save | Expense excluded from variable-expense subtotal in margin calc | domain | `tests/test_spec001_contract.py::test_reserve_paid_expense_excluded_from_margin` |
| Dashboard shows reserve indicators with no reserve activity | Cycle dashboard | Open dashboard with no reserve activity | Contribution, withdrawal, and reserve-paid totals show zero; no alert | ui | `tests/test_ui_regression.py::test_dashboard_reserve_zero_state` |
| Reserve fields are locked after cycle close date | Income/expense form, closed cycle (`current_date > end_date`) | Attempt to save reserve fields or flag | Visible lock error, no data change | domain | `tests/test_spec001_contract.py::test_reserve_fields_locked_after_end_date` |
| Dashboard shows withdrawal alert | Cycle dashboard | Open dashboard with recorded withdrawal and reserve-paid expenses | Values displayed; alert shown because withdrawal > 0 | ui | `tests/test_ui_regression.py::test_dashboard_shows_reserve_indicators_and_alert` |

Use `domain` for money, date, summary, and lifecycle rules; `persistence` for stored data and
history; and `ui` for Streamlit user interactions and displayed outcomes. UI rows target
`streamlit.testing.v1.AppTest`. Each changed business rule also needs deterministic pytest
coverage even when its UI flow is tested.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST let the user set a reserve contribution (aporte) amount on the monthly
  income record of the selected cycle, defaulting to `0.00` when unset.
- **FR-002**: System MUST subtract the reserve contribution from the projected margin using the
  existing closed-cycle margin formula (`income_total - total_fixed_cost - total_variable_expense -
  reserve_contribution`).
- **FR-003**: System MUST let the user set a reserve withdrawal (saque) amount on the monthly
  income record of the selected cycle, defaulting to `0.00` when unset.
- **FR-004**: System MUST NOT include the reserve withdrawal amount in the projected margin
  calculation.
- **FR-005**: System MUST let the user mark an individual variable expense as paid via reserve
  withdrawal, defaulting to unmarked.
- **FR-006**: System MUST exclude variable expenses marked as paid via reserve withdrawal from the
  variable-expense subtotal used in the projected margin calculation.
- **FR-007**: System MUST include variable expenses marked as paid via reserve withdrawal in a
  separate, dashboard-visible reserve-paid expenses total.
- **FR-008**: System MUST display the reserve contribution, reserve withdrawal, and reserve-paid
  expenses total on the cycle dashboard alongside the existing summary indicators.
- **FR-009**: System MUST show a visible alert on the cycle dashboard whenever the cycle's reserve
  withdrawal amount is greater than zero.
- **FR-010**: System MUST validate reserve contribution and reserve withdrawal amounts as
  non-negative Decimal values normalized to two decimal places, consistent with existing money
  fields.
- **FR-011**: System MUST reject updates to reserve contribution, reserve withdrawal, or the
  reserve-paid expense flag once the cycle is locked (from D+1 after `end_date`), showing a
  visible lock error.
- **FR-012**: System MUST preserve existing stored values when the current reserve-cash-outflow
  data is renamed to reserve contribution, so no historical cycle data is lost.

### Key Entities *(include if feature involves data)*

- **Monthly Income (extended)**: existing per-cycle record that now distinguishes a reserve
  contribution (reduces projected margin) from a reserve withdrawal (informational only, no
  effect on projected margin).
- **Variable Expense (extended)**: existing per-cycle expense entry that now carries a flag
  indicating it was paid via reserve withdrawal, which excludes it from the credit-margin
  calculation while keeping it visible in its own reserve-paid total.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can record a reserve contribution and see the projected margin update
  correctly on the same visit to the cycle screen.
- **SC-002**: A user can record a reserve withdrawal and immediately see it displayed with a
  visible alert on the cycle dashboard, with no change to the projected margin.
- **SC-003**: A user can mark a variable expense as reserve-paid and see the projected margin
  update to exclude that expense without leaving the cycle screen.
- **SC-004**: 100% of cycles with a recorded reserve withdrawal show the alert on the dashboard;
  0% of cycles with no reserve withdrawal show it.
- **SC-005**: Existing cycles with previously recorded reserve-outflow values retain the same
  numeric value after the rename, with no data loss.

## Assumptions

- The existing `MonthlyIncome.reserve_cash_outflow` field and its already-implemented margin
  effect are repurposed and renamed to `reserve_contribution`; its behavior in the projected
  margin formula does not change.
- A new, separate `reserve_withdrawal` value is added to the same monthly income record and is
  purely informational; it is not incorporated into any margin formula.
- No general expense-category system is introduced by this feature; reserve contribution and
  withdrawal are modeled as dedicated fields on the existing monthly income record, not as
  categorized expense entries.
- Marking a variable expense as paid via reserve withdrawal is a simple boolean flag on the
  existing variable expense entry, not a new expense type or entity.
- No automatic reconciliation is required between the reserve withdrawal amount and the sum of
  expenses flagged as reserve-paid; both are shown side by side for the user's own judgment.
- Reserve balance carried over across cycles, essential-spend estimation, and any multi-cycle
  comparison view are out of scope for this feature.
