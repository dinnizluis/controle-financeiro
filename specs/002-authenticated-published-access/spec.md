# Feature Specification: Authenticated Published Access

**Feature Branch**: `10-feat-streamlit-auth-oidc-allowlist`

**Created**: 2026-08-01

**Status**: Draft

**Input**: User description: "Issue: https://github.com/dinnizluis/controle-financeiro/issues/10"

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
