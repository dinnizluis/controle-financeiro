# Data Model: Authenticated Published Access

This feature adds access-control runtime entities and does not change financial persistence schema.

## Entity: Authenticated Session Context

Represents identity information available from the runtime session after login.

| Field | Type | Required | Notes |
|------|------|----------|-------|
| is_authenticated | bool | yes | True only when runtime identifies an authenticated user session |
| subject | str \| None | no | Stable identity claim used as primary allowlist key |
| email | str \| None | no | Fallback identity claim when subject is unavailable |
| expires_at | datetime \| None | no | Session/token expiry value when provided by identity context |
| raw_claims | Mapping[str, object] | yes | Source claim set for traceable evaluation (not displayed to user) |

Validation rules:
- If `is_authenticated` is False, authorization must not run and access state is sign-in required.
- If `is_authenticated` is True, at least one claim path (`subject` or `email`) must be readable for allowlist evaluation.
- Claim extraction errors produce configuration/access error state (fail closed).

## Entity: Authorization Allowlist Policy

Represents normalized allowlist configuration used to authorize authenticated sessions.

| Field | Type | Required | Notes |
|------|------|----------|-------|
| allowed_subjects | set[str] | conditional | Primary allowlist keys when provided |
| allowed_emails | set[str] | conditional | Fallback allowlist keys when subject unavailable |
| normalization | object | yes | Trim spaces and lowercase for case-insensitive deterministic matching |
| source | str | yes | Runtime secret source (not version controlled) |

Validation rules:
- Missing policy source, empty effective allowlist, or malformed list values fail closed.
- Duplicate and mixed-case entries normalize into deterministic set membership.
- Policy configuration must not come from SQLite or committed files.

## Entity: Access State

Finite state controlling whether financial services and UI sections may initialize.

| State | Meaning | Service initialization | Financial UI rendering |
|------|---------|------------------------|------------------------|
| sign_in_required | No authenticated user | blocked | blocked |
| access_denied | Authenticated but not allowlisted | blocked | blocked |
| config_error | Auth context/policy invalid or unreadable | blocked | blocked |
| authorized | Authenticated and allowlisted | allowed | allowed |

State transitions:
- Initial load -> `sign_in_required` when no authenticated session exists.
- Auth success + allowlist match -> `authorized`.
- Auth success + allowlist mismatch -> `access_denied`.
- Auth success + invalid claims/policy -> `config_error`.
- `authorized` + logout action -> `sign_in_required`.
- Any non-authorized state on refresh remains non-authorized until valid auth flow completes.

## Relationships

- `Authenticated Session Context` is evaluated against `Authorization Allowlist Policy` to derive `Access State`.
- `Access State` gates creation of `BudgetService` and all existing financial rendering flows.
- Existing financial entities (fixed costs, variable expenses, monthly income, history) remain unchanged and are only reachable through `authorized` state.
