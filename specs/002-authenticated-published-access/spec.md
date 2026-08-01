# Feature Specification: Authenticated Published Access

**Feature Branch**: `10-feat-streamlit-auth-oidc-allowlist`

**Created**: 2026-08-01

**Status**: MVP-0 Delivered

**Input**: User description: "Issue: https://github.com/dinnizluis/controle-financeiro/issues/10"

## Execution Scope Override (MVP-0)

Current execution scope is intentionally reduced to the smallest privacy barrier:

- Single shared password gate via `st.secrets` (`APP_ACCESS_PASSWORD`)
- Block all financial initialization/rendering before valid password
- Fail-closed when password config is missing/invalid
- No logout flow in this slice

Future evolution remains explicitly deferred:

- OIDC with `st.login()` / `st.user` / `st.logout()`
- Allowlist by identity (subject preferred, email fallback)
- Explicit logout lifecycle and forced token-expiration behavior
- Multi-user authorization or per-user data isolation

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Block public access before data load (Priority: P1)

As the owner of the published app, I need visitors without the shared password to be stopped before
any financial component is initialized, so that sensitive monthly budget data is never exposed
publicly.

**Why this priority**: This is the minimum privacy barrier for safe publication. Without it, all
other controls are irrelevant because financial data can leak at first page load.

**Independent Test**: Can be fully tested by opening the app without an unlocked session and
verifying that only the password gate is visible while financial views and data loading do not
happen.

**Acceptance Scenarios**:

1. **Given** a visitor without a valid unlocked session, **When** they open the app URL, **Then**
   the app shows only the password entry state and no financial data or controls.
2. **Given** a visitor without a valid unlocked session, **When** they refresh or reopen the app,
   **Then** the app remains locked and no financial data is shown.

---

### User Story 2 - Unlock dashboard with the configured password (Priority: P1)

As the owner of the published app, I need the configured shared password to unlock the existing
dashboard, so that publication remains private without changing the financial workflow.

**Why this priority**: The feature is only useful if the owner can still reach the current monthly
workflow after passing the gate.

**Independent Test**: Can be fully tested by entering the configured password and verifying that
the current dashboard shell renders normally.

**Acceptance Scenarios**:

1. **Given** a visitor who enters the configured shared password, **When** the app validates the
   password, **Then** the app grants access and shows the current financial dashboard.
2. **Given** an unlocked user whose selected cycle has no records yet, **When** the dashboard
   loads, **Then** the existing empty-state guidance is shown without authorization errors.

---

### User Story 3 - Fail closed on bad or missing configuration (Priority: P1)

As the owner of the published app, I need missing configuration or invalid password attempts to
keep the app locked, so that misconfiguration or misuse never exposes financial data.

**Why this priority**: The privacy barrier must default to closed behavior, not best-effort access.

**Independent Test**: Can be fully tested by omitting `APP_ACCESS_PASSWORD` and by entering a wrong
password, verifying that the app remains locked and non-sensitive.

**Acceptance Scenarios**:

1. **Given** `APP_ACCESS_PASSWORD` is missing, empty, or invalid, **When** the app loads, **Then**
   the app shows a non-sensitive configuration error and no financial data.
2. **Given** a visitor enters a wrong password, **When** the app validates the entry, **Then** the
   app remains locked, shows non-sensitive feedback, and does not initialize financial services.

---

### Edge Cases

- What happens when `APP_ACCESS_PASSWORD` is missing, empty, or whitespace-only? The app fails
  closed and blocks all financial rendering.
- What happens when a visitor enters the wrong password repeatedly? The app remains locked and no
  financial service initialization occurs.
- What happens when the user refreshes before unlocking? The app stays on the locked entry state.
- What happens when the unlocked cycle has no records yet? The dashboard still reaches the existing
  empty-state guidance without access errors.

## Acceptance Criteria and Regression Map *(mandatory)*

### Gherkin Scenarios

```gherkin
Feature: Protected published access to the Streamlit finance app

  Scenario: Visitor is stopped before financial services initialize
    Given the published app is opened without a valid unlocked session
    When the entry screen loads
    Then the app shows a password prompt
    And financial services are not initialized
    And no financial summary, cycle selector, table, or lock message is shown

  Scenario: Correct password unlocks the dashboard
    Given the visitor enters the configured shared password
    When the app validates the password
    Then the app initializes financial services
    And the current financial dashboard is shown

  Scenario: Missing password configuration fails closed
    Given APP_ACCESS_PASSWORD is missing or invalid
    When the entry screen loads
    Then the app shows a non-sensitive configuration error
    And financial services are not initialized
    And no financial summary, cycle selector, table, or lock message is shown

  Scenario: Wrong password keeps the app locked
    Given the visitor enters an invalid password
    When the app validates the password
    Then the app remains locked
    And financial services are not initialized
    And no financial summary, cycle selector, table, or lock message is shown

  Scenario: Unlocked user still reaches existing empty monthly state
    Given the user has already unlocked the app with the configured password
    And the selected cycle has no fixed costs and no variable expenses yet
    When the dashboard loads
    Then the app shows the authenticated shell and existing empty-state guidance
    And no access error is shown
```

### UI Flow and Regression Test Map

| Gherkin scenario | Starting screen or state | User action | Observable result | Test layer | Planned test |
|------------------|--------------------------|-------------|-------------------|------------|--------------|
| Visitor is stopped before financial services initialize | Published app entry, locked session | Open app | Password prompt only, no service init, no financial UI | ui | `tests/test_ui_auth_access.py::test_password_gate_blocks_financial_ui_before_unlock` |
| Correct password unlocks the dashboard | Published app entry, locked session | Enter valid password | Dashboard loads with summary, cycle controls, and forms | ui | `tests/test_ui_auth_access.py::test_password_gate_unlocks_dashboard_on_valid_password` |
| Missing password configuration fails closed | Published app entry, missing `APP_ACCESS_PASSWORD` | Open app | Non-sensitive config error, no service init | ui | `tests/test_ui_auth_access.py::test_password_gate_missing_secret_fails_closed` |
| Wrong password keeps the app locked | Published app entry, locked session | Enter invalid password | Locked state persists with non-sensitive error | ui | `tests/test_ui_auth_access.py::test_password_gate_wrong_password_keeps_app_locked` |
| Unlocked user still reaches existing empty monthly state | Unlocked session with empty cycle | Open app | Existing empty-state guidance appears after unlock | ui | `tests/test_ui_regression.py::test_empty_cycle_exposes_entry_forms_and_guidance` |

Use `ui` for Streamlit user interactions and displayed outcomes. UI rows target
`streamlit.testing.v1.AppTest`. Deterministic helper coverage for password configuration,
session-state, and formatting helpers lives in `tests/test_app_helpers.py`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST require a successful password unlock before any financial service
  initialization.
- **FR-002**: System MUST deny access to any session without a successful password unlock and show
  only a non-sensitive locked entry state.
- **FR-003**: System MUST grant access only when the user-provided password exactly matches
  `APP_ACCESS_PASSWORD` from runtime secrets.
- **FR-004**: System MUST fail closed when `APP_ACCESS_PASSWORD` is missing, empty, unreadable, or
  invalid.
- **FR-005**: System MUST keep the app locked when the visitor enters the wrong password.
- **FR-006**: System MUST ensure no financial summary, cycle selection, record table, lock status,
  or history information is rendered before unlock succeeds.
- **FR-007**: System MUST preserve all existing money calculations, cycle boundaries, lock rules,
  and history behavior for unlocked sessions.
- **FR-008**: System MUST NOT create, mutate, or migrate financial records solely by enabling the
  password gate.
- **FR-009**: System MUST obtain the shared password from secure runtime secrets, not
  version-controlled files or SQLite data.
- **FR-010**: System MUST keep OIDC login, allowlist authorization, explicit logout, and forced
  token-expiration handling outside this feature scope.

### Key Entities *(include if feature involves data)*

- **Password Gate Configuration**: runtime secret holding the shared password used to unlock the
  app.
- **Unlocked Session State**: transient runtime state indicating whether the current session has
  already passed password validation.
- **Access State**: one of locked, configuration error, or unlocked, controlling whether financial
  services may initialize.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of locked app entries present only the password-gate state and expose zero
  financial indicators.
- **SC-002**: 100% of valid password submissions can reach the current dashboard without new
  authorization errors.
- **SC-003**: 100% of missing or invalid password configuration states fail closed before any
  financial service initialization.
- **SC-004**: Zero financial records are created, modified, or deleted solely by enabling the
  password-gate flow.

## Assumptions

- The first published release remains single-owner or a deliberately tiny trusted household sharing
  one SQLite dataset; per-user data isolation is out of scope.
- The shared password is maintained by the app owner through secure deployment secrets.
- Existing dashboard and monthly workflow behavior stays unchanged after unlock.

## Delivery Sizing (MVP-0)

Sizing for issue #10 uses a lightweight complexity heuristic documented in `tasks.md`:

- Score per task = `B (blast radius) + U (unknowns) + T (test load)`
- Bands: XS (3-4), S (5-6), M (7-8), L (9)

MVP-0 sizing snapshot:

- Active MVP tasks: T001-T004
- Total complexity score: 14
- Average task score: 3.5 (XS)
- Critical path estimate: ~1.5 working days
- Consolidated worst-case estimate (integration + validation buffer): **~1 working day**# Feature Specification: Authenticated Published Access

**Feature Branch**: `10-feat-streamlit-auth-oidc-allowlist`

**Created**: 2026-08-01

**Status**: Draft

**Input**: User description: "Issue: https://github.com/dinnizluis/controle-financeiro/issues/10"

## Execution Scope Override (MVP-0)

Current execution scope is intentionally reduced to the smallest privacy barrier:

- Single shared password gate via `st.secrets` (`APP_ACCESS_PASSWORD`)
- Block all financial initialization/rendering before valid password
- Fail-closed when password config is missing/invalid
- No logout flow in this slice

The OIDC + allowlist + logout model remains valid as future evolution and is intentionally deferred.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Block anonymous access before data load (Priority: P1)

As the owner of the published app, I need anonymous visitors to be stopped before any financial
component is initialized, so that sensitive monthly budget data is never exposed publicly.

**Why this priority**: This is the minimum privacy barrier for safe publication. Without it, all
other controls are irrelevant because financial data can leak at first page load.

**Independent Test**: Can be fully tested by opening the app with no authenticated user and
verifying only a sign-in prompt is visible while financial views and data loading do not happen.

**Acceptance Scenarios**:

1. **Given** a visitor with no authenticated session, **When** they open the app URL, **Then**
   the app shows a sign-in entry state and no financial data or controls.
2. **Given** a visitor with no authenticated session, **When** they refresh or reopen the app,
   **Then** the app remains in the sign-in entry state with no financial data shown.

---

### User Story 2 - Allow only approved authenticated users (Priority: P2)

As the owner of the published app, I need authenticated access to be restricted to an explicit
allowlist, so that identity verification and authorization both protect the same dataset.

**Why this priority**: Authentication alone is not enough for sensitive data. Authorization ensures
only approved identities can view the shared SQLite dataset.

**Independent Test**: Can be fully tested by checking that an allowlisted authenticated user can
access the dashboard while a non-allowlisted authenticated user receives access denied.

**Acceptance Scenarios**:

1. **Given** an authenticated user whose identity matches the allowlist, **When** they open the
   app, **Then** the app grants access and shows the financial dashboard.
2. **Given** an authenticated user whose identity does not match the allowlist, **When** they open
   the app, **Then** the app shows access denied and no financial data.
3. **Given** an authenticated user but missing or invalid authorization configuration, **When**
   they open the app, **Then** the app fails closed with a non-sensitive configuration or access
   error and no financial data.

---

### User Story 3 - Return to non-sensitive state on logout (Priority: P3)

As an approved user, I need to log out and return to a non-sensitive entry state, so that private
financial data is not left visible when I finish a session.

**Why this priority**: This closes the basic session loop and reduces accidental exposure on shared
or unattended devices.

**Independent Test**: Can be fully tested by logging out from an authorized session and verifying
that financial data is no longer visible and the sign-in entry state is restored.

**Acceptance Scenarios**:

1. **Given** an authorized session on the dashboard, **When** the user logs out, **Then** the app
   returns to the non-authenticated entry state with no financial data visible.
2. **Given** a user who logged out, **When** the app page is refreshed, **Then** it remains in a
   non-sensitive entry state until authentication succeeds again.

---

### Edge Cases

- What happens when the allowlist contains duplicate, mixed-case, or extra-space entries? Identity
  matching remains deterministic and unauthorized users are still denied.
- How does the system handle an authenticated identity with missing required claims for the chosen
  authorization rule? Access is denied with a non-sensitive error and no data exposure.
- What happens when allowlist configuration is missing, empty, or malformed? The app fails closed
  and blocks all financial rendering.
- What happens when an unauthorized authenticated user refreshes repeatedly? The denial state is
  consistently enforced and no financial service initialization occurs.
- What happens when the authorized cycle has no records yet? Authorized users still reach the
  existing empty-state guidance without authorization errors.

## Acceptance Criteria and Regression Map *(mandatory)*

### Gherkin Scenarios

```gherkin
Feature: Protected published access to the Streamlit finance app

  Scenario: Anonymous visitor is stopped before financial services initialize
    Given the published app is opened without an authenticated user
    When the entry screen loads
    Then the app shows a sign-in prompt
    And financial services are not initialized
    And no financial summary, cycle selector, table, or lock message is shown

  Scenario: Allowlisted authenticated user reaches the dashboard
    Given the user is authenticated with the configured identity provider
    And the user identity matches the configured allowlist
    When the entry screen loads
    Then the app initializes financial services
    And the financial dashboard is shown
    And a visible logout action is available

  Scenario: Authenticated but non-allowlisted user is denied
    Given the user is authenticated with the configured identity provider
    And the user identity does not match the configured allowlist
    When the entry screen loads
    Then the app shows an access-denied state
    And financial services are not initialized
    And no financial summary, cycle selector, table, or lock message is shown

  Scenario: Missing authorization configuration fails closed
    Given the user is authenticated with the configured identity provider
    And required authorization claims or allowlist configuration are missing or invalid
    When the entry screen loads
    Then the app shows a non-sensitive configuration or access error
    And financial services are not initialized
    And no financial summary, cycle selector, table, or lock message is shown

  Scenario: Authorized user logs out to a non-sensitive state
    Given the user is authenticated and allowlisted
    When the user chooses logout
    Then the app returns to a non-authenticated entry state
    And no financial summary, cycle selector, table, or lock message is shown

  Scenario: Authorized user can still access empty monthly state
    Given the user is authenticated and allowlisted
    And the selected cycle has no fixed costs and no variable expenses yet
    When the entry screen loads
    Then the app shows the authenticated shell and existing empty-state guidance
    And no authorization error is shown
```

Write one independent scenario for each primary flow and include error, empty, validation, and
locked-state scenarios where relevant. Do not use implementation details in Gherkin steps.

### UI Flow and Regression Test Map

| Gherkin scenario | Starting screen or state | User action | Observable result | Test layer | Planned test |
|------------------|--------------------------|-------------|-------------------|------------|--------------|
| Anonymous visitor is stopped before financial services initialize | Published app entry, no authenticated user | Open app | Sign-in prompt only, no service init, no financial UI | ui | `tests/test_ui_auth_access.py::test_anonymous_user_sees_login_gate_before_service_init` |
| Allowlisted authenticated user reaches the dashboard | Published app entry, authenticated allowlisted user | Open app | Dashboard loads with summary, cycle controls, and logout | ui | `tests/test_ui_auth_access.py::test_allowlisted_user_can_open_dashboard` |
| Authenticated but non-allowlisted user is denied | Published app entry, authenticated non-allowlisted user | Open app | Access denied, no service init, no financial UI | domain | `tests/test_auth_policy.py::test_non_allowlisted_identity_is_rejected` |
| Authenticated but non-allowlisted user is denied | Published app entry, authenticated non-allowlisted user | Open app | Access denied UI state without financial content | ui | `tests/test_ui_auth_access.py::test_non_allowlisted_user_sees_denied_state_without_financial_content` |
| Missing authorization configuration fails closed | Published app entry, authenticated user with missing claim or malformed allowlist | Open app | Non-sensitive config/access error, no service init | domain | `tests/test_auth_policy.py::test_missing_claim_or_invalid_allowlist_fails_closed` |
| Missing authorization configuration fails closed | Published app entry, authenticated user with missing claim or malformed allowlist | Open app | Non-sensitive fail-closed UI, no financial content | ui | `tests/test_ui_auth_access.py::test_invalid_auth_config_or_claims_show_fail_closed_state` |
| Authorized user logs out to a non-sensitive state | Authenticated allowlisted dashboard | Click logout | App returns to signed-out entry state | ui | `tests/test_ui_auth_access.py::test_logout_returns_user_to_non_sensitive_entry_state` |
| Authorized user can still access empty monthly state | Authenticated allowlisted user with empty cycle | Open app | Existing empty-state guidance appears after auth | ui | `tests/test_ui_auth_access.py::test_allowlisted_user_sees_existing_empty_state_after_login` |

Use `domain` for money, date, summary, and lifecycle rules; `persistence` for stored data and
history; and `ui` for Streamlit user interactions and displayed outcomes. UI rows target
`streamlit.testing.v1.AppTest`. Each changed business rule also needs deterministic pytest
coverage even when its UI flow is tested.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST require authenticated identity before any financial service
  initialization.
- **FR-002**: System MUST deny access to any non-authenticated session and show only a non-sensitive
  sign-in entry state.
- **FR-003**: System MUST apply explicit authorization after authentication using a configured
  allowlist policy.
- **FR-004**: System MUST grant access only when the authenticated identity matches the configured
  allowlist.
- **FR-005**: System MUST deny access when identity claims required by the authorization rule are
  missing, unreadable, or invalid.
- **FR-006**: System MUST fail closed when allowlist configuration is missing, empty, or malformed.
- **FR-007**: System MUST ensure no financial summary, cycle selection, record table, lock status,
  or history information is rendered before authentication and authorization succeed.
- **FR-008**: System MUST provide a visible logout action for authorized sessions.
- **FR-009**: System MUST return to a non-sensitive entry state after logout, with no financial
  data rendered.
- **FR-010**: System MUST preserve all existing money calculations, cycle boundaries, lock rules,
  and history behavior for authorized sessions.
- **FR-011**: System MUST NOT create, mutate, or migrate financial records as part of this feature.
- **FR-012**: System MUST obtain identity-provider settings and allowlist configuration from secure
  runtime secrets, not version-controlled files or SQLite data.
- **FR-013**: System MUST support the approved allowlist rule for this feature: stable subject
  identifier preferred, with email fallback when subject is unavailable.
- **FR-014**: System MUST keep forced token-expiration logout outside this feature scope.

### Key Entities *(include if feature involves data)*

- **Authenticated Session Context**: runtime identity state indicating whether the user is logged in
  and exposing identity claims used for authorization decisions.
- **Authorization Allowlist Policy**: approved identity list and normalization rules used to allow
  or deny access after authentication.
- **Access State**: one of sign-in required, access denied, configuration error, or authorized app
  state controlling whether financial services can initialize.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of anonymous app entries present only the sign-in state and expose zero
  financial indicators.
- **SC-002**: 100% of authenticated users not in the allowlist are denied before any financial
  service initialization.
- **SC-003**: 100% of authenticated allowlisted users can reach the current dashboard and complete
  the existing monthly flow without new authorization errors.
- **SC-004**: 100% of logout actions return users to a non-sensitive entry state with no financial
  content visible.
- **SC-005**: Zero financial records are created, modified, or deleted solely by enabling the
  authentication and authorization flow.

## Assumptions

- The first published release remains single-owner or a deliberately tiny trusted household sharing
  one SQLite dataset; per-user data isolation is out of scope.
- The identity provider is already configured to issue subject and/or email claims usable for
  allowlist checks.
- Allowlist values are maintained by the app owner through secure deployment secrets.
- Forced session-expiration enforcement based on token lifetime is handled by a later feature slice.
- Existing dashboard and monthly workflow behavior stays unchanged for authorized users.

## Delivery Sizing (MVP-0)

Sizing for issue #10 uses a lightweight complexity heuristic documented in `tasks.md`:

- Score per task = `B (blast radius) + U (unknowns) + T (test load)`
- Bands: XS (3-4), S (5-6), M (7-8), L (9)

MVP-0 sizing snapshot:

- Active MVP tasks: T001-T004
- Total complexity score: 14
- Average task score: 3.5 (XS)
- Critical path estimate: ~1.5 working days
- Consolidated worst-case estimate (integration + validation buffer): **~1 working day**
