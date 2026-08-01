# Contract: Password Gate Configuration (MVP-0)

Defines the minimum configuration contract to block public access with a single shared password.

## Purpose

Provide a simple, fail-closed runtime contract for opening the app only after password validation.

## Inputs

| Key | Required | Type | Description |
|-----|----------|------|-------------|
| APP_ACCESS_PASSWORD | yes | string | Shared password used to unlock access to the financial dashboard |

Notes:
- Configuration source must be runtime secrets (`st.secrets`) and never repository files or SQLite.
- Empty, missing, or whitespace-only values are invalid.

## Evaluation Rules

1. If `APP_ACCESS_PASSWORD` is missing or invalid, access must remain blocked (fail-closed).
2. User-provided password must be compared against secret value exactly.
3. Only successful match can transition app state to unlocked.
4. Any mismatch remains locked with non-sensitive feedback.

## Security and Error Contract

- Financial service initialization is forbidden while locked.
- Financial UI (summary, cycle controls, tables, history, lock details) is forbidden while locked.
- Error/feedback messages must not leak secret values.

## Future Evolution (Out of Scope Here)

- OIDC login (`st.login`, `st.user`, `st.logout`)
- Subject/email allowlist authorization
- Token-expiration and robust session lifecycle policies
