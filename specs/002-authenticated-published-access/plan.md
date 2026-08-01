# Implementation Plan: Authenticated Published Access

**Branch**: `002-authenticated-published-access` | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-authenticated-published-access/spec.md`

## Summary

Protect the published Streamlit app with the smallest verifiable privacy barrier: a single shared
password from `st.secrets` that blocks all financial service initialization and financial UI
rendering until the current session is unlocked. This slice deliberately avoids OIDC, allowlist,
logout, and token-lifecycle behavior, which remain future evolution.

## Technical Context

**Language/Version**: Python 3.11+ (project supports >=3.11,<3.13)

**Primary Dependencies**: Streamlit, SQLAlchemy, Pydantic

**Storage**: SQLite single shared dataset (`data/controle_financeiro.db` by default)

**Testing**: pytest, pytest-cov, streamlit.testing.v1.AppTest, pyright, pip-audit

**Coverage Target**: Minimum line coverage of **90%** for `controle_financeiro`

**Target Platform**: Streamlit app in local and hosted runtime with configured secrets

**Project Type**: Single Python Streamlit application

**Performance Goals**: No meaningful regression to current first-render flow for unlocked users;
locked and invalid-config flows must short-circuit before budget service initialization.

**Constraints**: Fail-closed access; secrets-only configuration; no changes to financial
calculations/cycle rules/history semantics; no data migrations.

**Scale/Scope**: Single owner or tiny trusted household sharing one dataset; no per-user data
isolation in this slice.

## Constitution Check

Pre-implementation review:

- Principle I - Preserve Financial Integrity: PASS. Scope only gates access and does not change
  money, cycle, or history rules.
- Principle II - Specify Before Implementing: PASS. Spec, plan, tasks, and quickstart all target
  the same MVP-0 password gate.
- Principle III - Test the Risk First: PASS. Locked, unlocked, invalid-config, invalid-password,
  helper, and empty-state scenarios are covered by deterministic pytest/AppTest cases.
- Principle IV - Keep Domain Boundaries Explicit: PASS. UI orchestrates access state and existing
  service boundaries remain intact.
- Principle V - Prefer the Smallest Verifiable Slice: PASS. Delivery stays on the password-only
  path without introducing new modules or auth providers.

## Regression Test Strategy *(mandatory)*

Map every MVP-0 scenario in `spec.md` to its smallest effective automated test.

| Scenario | Risk or rule | Test layer | Planned test | Rationale |
|----------|--------------|------------|--------------|-----------|
| Visitor is stopped before financial services initialize | Prevent exposure before unlock and prevent service startup | ui | `tests/test_ui_auth_access.py::test_password_gate_blocks_financial_ui_before_unlock` | Verifies visible locked state and guard ordering in real Streamlit lifecycle |
| Correct password unlocks the dashboard | Happy path after password validation | ui | `tests/test_ui_auth_access.py::test_password_gate_unlocks_dashboard_on_valid_password` | Ensures the dashboard remains reachable after unlock |
| Missing password configuration fails closed | Broken config cannot degrade to open access | ui | `tests/test_ui_auth_access.py::test_password_gate_missing_secret_fails_closed` | Confirms non-sensitive fail-closed behavior |
| Wrong password keeps the app locked | Invalid secret entry must not initialize services | ui | `tests/test_ui_auth_access.py::test_password_gate_wrong_password_keeps_app_locked` | Verifies negative validation path in the real UI flow |
| Unlocked user still reaches existing empty monthly state | Existing empty-cycle UX must survive the gate | ui | `tests/test_ui_regression.py::test_empty_cycle_exposes_entry_forms_and_guidance` | Guards the baseline dashboard shell after unlock |
| Password helper and session state logic remain deterministic | Secrets/session helper regressions should fail fast | unit | `tests/test_app_helpers.py` | Covers configuration parsing, session state, formatting, and env-based service wiring |

Validation gate for this slice:

- `.venv/bin/python -m pytest --cov=controle_financeiro --cov-report=term-missing --cov-fail-under=90 -q`
- `.venv/bin/python -m ruff format --check .`
- `.venv/bin/python -m ruff check .`
- `.venv/bin/pyright`
- `.venv/bin/pip-audit`

## Project Structure

### Documentation (this feature)

```text
specs/002-authenticated-published-access/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── access-state-ui-contract.md
│   └── auth-config-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
streamlit_app.py
src/
└── controle_financeiro/
  ├── app.py
  ├── models.py
  ├── service.py
  └── storage.py

tests/
├── conftest.py
├── test_app_helpers.py
├── test_spec001_contract.py
├── test_ui_regression.py
└── test_ui_auth_access.py
```

**Structure Decision**: Keep the existing single-project Streamlit architecture, reuse the current
service/repository boundaries, and add only focused tests plus password-gate logic in the UI entry
point.

## MVP Complexity and Estimate

Heuristic adopted for this feature slice (same model as `tasks.md`):

- `B` (blast radius): 1-3
- `U` (unknowns): 1-3
- `T` (test load): 1-3
- `Score = B + U + T` (3..9)

MVP-0 task-set used for execution planning: T001-T004.

Planning metrics:

- Total score: 14
- Average score per task: 3.5
- Complexity class: XS
- Critical path: T001 -> T002 -> T003 -> T004 (~1.5 working days)
- Feature worst-case estimate: **~1 working day**

Operational reading:

- Half day to day 1: password gate + focused UI regressions
- Remaining buffer: helper coverage, validation evidence, and deploy secret verification# Implementation Plan: Authenticated Published Access

**Branch**: `002-authenticated-published-access` | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-authenticated-published-access/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command; its definition describes the execution workflow.

## Summary

Protect the published Streamlit app with an auth-first access gate that blocks all financial
service initialization and financial UI rendering until the user is authenticated and explicitly
allowlisted. The feature uses Streamlit native OIDC session primitives at the UI boundary,
evaluates authorization with deterministic normalization rules (subject preferred, email fallback),
and fails closed for missing or malformed auth configuration.

MVP-0 execution override: implement only a single shared password gate using `st.secrets`
(`APP_ACCESS_PASSWORD`) as the fastest privacy barrier for the published app. OIDC/allowlist/logout
flows are deferred to future evolution.

## Technical Context

**Language/Version**: Python 3.11+ (project supports >=3.11,<3.13)

**Primary Dependencies**: Streamlit, SQLAlchemy, Pydantic

**Storage**: SQLite single shared dataset (`data/controle_financeiro.db` by default)

**Testing**: pytest, streamlit.testing.v1.AppTest, pytest-cov

**Target Platform**: Streamlit app in local and hosted runtime with configured OIDC provider

**Project Type**: Single Python Streamlit application

**Performance Goals**: No meaningful regression to current first-render flow for authorized users;
anonymous and unauthorized flows must short-circuit before budget service initialization.

**Constraints**: Fail-closed authorization; secrets-only configuration (no VCS or SQLite auth
config); no changes to financial calculations/cycle rules/history semantics; no data migrations.

**Scale/Scope**: Single owner or tiny trusted household sharing one dataset; no per-user data
isolation in this slice.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-Phase 0 gate review:

- Principle I - Preserve Financial Integrity: PASS. Scope explicitly avoids financial data mutation,
  migrations, or rule changes; feature only gates access.
- Principle II - Specify Before Implementing: PASS. Spec exists with user stories, Gherkin,
  requirements, and success criteria.
- Principle III - Test the Risk First: PASS with planned coverage. New auth/authorization rules
  have deterministic domain and UI tests mapped below.
- Principle IV - Keep Domain Boundaries Explicit: PASS. Authorization policy will be testable and
  separate from Streamlit widget code; UI only orchestrates access states.
- Principle V - Prefer the Smallest Verifiable Slice: PASS. Single-slice auth gate + allowlist +
  logout, no multi-user redesign.

Gate decision before research: PASS (no blocking violations).

## Regression Test Strategy *(mandatory)*

Map every Gherkin scenario in `spec.md` to its smallest effective automated test. The plan must
name the intended test file and avoid tests that merely repeat a lower-layer assertion.

| Gherkin scenario | Risk or rule | Test layer | Planned test | Rationale |
|------------------|--------------|------------|--------------|-----------|
| Anonymous visitor is stopped before financial services initialize | Prevent exposure before auth and prevent service startup | ui | `tests/test_ui_auth_access.py::test_anonymous_user_sees_login_gate_before_service_init` | Verifies rendered state and guard ordering in real Streamlit lifecycle |
| Allowlisted authenticated user reaches the dashboard | Happy path after authn+authz | ui | `tests/test_ui_auth_access.py::test_allowlisted_user_can_open_dashboard` | Ensures existing dashboard remains reachable for approved identities |
| Authenticated but non-allowlisted user is denied | Authorization mismatch must fail closed | domain | `tests/test_auth_policy.py::test_non_allowlisted_identity_is_rejected` | Policy normalization and matching are deterministic business rules |
| Authenticated but non-allowlisted user is denied | Denied user must not see financial UI | ui | `tests/test_ui_auth_access.py::test_non_allowlisted_user_sees_denied_state_without_financial_content` | Confirms policy outcome is enforced at presentation boundary |
| Missing authorization configuration fails closed | Broken config cannot degrade to open access | domain | `tests/test_auth_policy.py::test_missing_claim_or_invalid_allowlist_fails_closed` | Validates fail-closed behavior independent of Streamlit rendering |
| Missing authorization configuration fails closed | Fail-closed state must be non-sensitive in UI | ui | `tests/test_ui_auth_access.py::test_invalid_auth_config_or_claims_show_fail_closed_state` | Ensures errors do not leak financial metadata |
| Authorized user logs out to a non-sensitive state | Session termination must clear sensitive view | ui | `tests/test_ui_auth_access.py::test_logout_returns_user_to_non_sensitive_entry_state` | Validates signed-out state and post-logout rendering |
| Authorized user can still access empty monthly state | Existing empty-cycle UX must survive auth gate | ui | `tests/test_ui_auth_access.py::test_allowlisted_user_sees_existing_empty_state_after_login` | Guards against regressions in current baseline onboarding/empty flow |

- Use deterministic pytest tests for financial calculations, dates, validation, lifecycle, and
  lock rules.
- Use temporary SQLite databases for persistence and history behavior.
- Use `streamlit.testing.v1.AppTest` for Streamlit workflows and visible empty, error, and success
  states.
- Use Hypothesis only for high-value invariants and boundary combinations that are impractical to
  enumerate.

## Project Structure

### Documentation (this feature)

```text
specs/002-authenticated-published-access/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── access-state-ui-contract.md
│   └── auth-config-contract.md
└── tasks.md
```

### Source Code (repository root)
```text
streamlit_app.py
src/
└── controle_financeiro/
  ├── app.py
  ├── models.py
  ├── service.py
  ├── storage.py
  └── auth.py                 # planned new policy module

tests/
├── conftest.py
├── test_spec001_contract.py
├── test_ui_regression.py
├── test_auth_policy.py         # planned new domain policy tests
└── test_ui_auth_access.py      # planned new UI access-gate tests
```

**Structure Decision**: Keep the existing single-project Streamlit architecture and add one
focused auth policy module plus dedicated domain/UI regression tests. No repository split and no
storage schema expansion are required.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

Post-Phase 1 gate re-check:

- Principle I - Preserve Financial Integrity: PASS. Data model and contracts introduce no financial
  record mutation paths.
- Principle II - Specify Before Implementing: PASS. Plan artifacts remain aligned to spec and
  assumptions.
- Principle III - Test the Risk First: PASS. All Gherkin scenarios are mapped to concrete pytest
  targets.
- Principle IV - Keep Domain Boundaries Explicit: PASS. Contracts separate UI access states from
  policy evaluation responsibilities.
- Principle V - Prefer the Smallest Verifiable Slice: PASS. Scope constrained to authn/authz gate,
  logout, and regression protection.

No constitution violations require complexity exemptions.

## MVP Complexity and Estimate

Heuristic adopted for this feature slice (same model as `tasks.md`):

- `B` (blast radius): 1-3
- `U` (unknowns): 1-3
- `T` (test load): 1-3
- `Score = B + U + T` (3..9)

MVP-0 task-set used for execution planning: T001-T004.

Planning metrics:

- Total score: 14
- Average score per task: 3.5
- Complexity class: XS
- Critical path: T001 -> T002 -> T003 -> T004 (~1.5 working days)
- Feature worst-case estimate: **~1 working day**

Operational reading:

- Half day to day 1: password gate + locked/unlocked regressions
- Remaining buffer: quickstart validation and deployment secret verification
