# Phase 0 Research: Authenticated Published Access

## Decision 1: Use Streamlit native OIDC session flow at the UI boundary

- Decision: Use Streamlit authentication primitives for login state and session lifecycle in the app entry flow.
- Rationale: The repository already runs as a Streamlit app and the security plan explicitly recommends native OIDC flow with `st.login()`, `st.user`, and `st.logout()`. This minimizes custom credential handling and keeps auth lifecycle consistent with the framework.
- Alternatives considered:
  - Custom username/password storage in SQLite: rejected due to increased security burden (password storage, reset flow, operational risk) and conflict with project direction.
  - External reverse proxy auth only: rejected for this slice because app-level authorization and fail-closed logic are still required before service initialization.

## Decision 2: Enforce authorization using allowlist policy with subject-first matching and email fallback

- Decision: Evaluate an explicit allowlist policy after authentication, matching stable subject claim first and normalized email only when subject is missing.
- Rationale: This directly implements FR-013 and avoids identity drift from email changes when subject is available. It also keeps authorization deterministic for duplicate/mixed-case/whitespace entries.
- Alternatives considered:
  - Email-only allowlist: rejected because it is less stable than provider subject identifiers.
  - Subject-only allowlist: rejected because it can block legitimate users when providers or environments temporarily omit subject in available claims.

## Decision 3: Fail closed for missing or malformed auth configuration

- Decision: Treat missing/empty/malformed allowlist or missing required claims as access failure; render only non-sensitive denial/configuration states.
- Rationale: FR-005 and FR-006 require safe default behavior. Failing open would create direct data exposure risk.
- Alternatives considered:
  - Fail open with warning banner: rejected because it violates primary privacy requirement and success criteria.
  - Partial rendering with redacted financial values: rejected because metadata leakage (cycle/status/counts) remains possible.

## Decision 4: Place service initialization behind successful authn+authz guard

- Decision: Do not initialize `BudgetService` until access state is authorized.
- Rationale: Current code initializes `get_service()` at app startup. Moving service creation behind access gate is the smallest reliable method to satisfy FR-001, FR-002, and FR-007.
- Alternatives considered:
  - Initialize service but hide UI: rejected because backend state could still load sensitive data.
  - Keep cached service global regardless of auth: rejected due to risk of unauthorized process path exposing data through future UI regressions.

## Decision 5: Keep persistence model unchanged in this slice

- Decision: Do not alter SQLite schema, ownership model, or financial domain entities for this feature.
- Rationale: Spec scope and assumptions explicitly keep single shared dataset behavior while adding access control only.
- Alternatives considered:
  - Introduce user-scoped records now: rejected as a larger architecture change outside this issue.
  - Add auth claims into financial tables: rejected because FR-011 forbids data mutation/migration in this feature.

## Decision 6: Test strategy combines deterministic policy tests and Streamlit UI gating tests

- Decision: Add dedicated domain tests for authorization policy and UI tests for access states and rendering guard behavior.
- Rationale: Constitution Principle III requires deterministic coverage for changed business rules, while auth gate behavior must be validated in actual Streamlit lifecycle rendering.
- Alternatives considered:
  - UI-only tests: rejected because normalization/fail-closed policy logic needs isolated deterministic coverage.
  - Domain-only tests: rejected because guard placement and rendered-state guarantees are UI-observable requirements.
