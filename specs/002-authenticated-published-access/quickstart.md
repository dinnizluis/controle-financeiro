# Quickstart Validation: Password Gate MVP-0

This guide validates the minimum password lock for published access.

## Prerequisites

1. Python virtual environment is available at `.venv`.
2. Project dependencies are installed with dev extras.
3. Runtime secret `APP_ACCESS_PASSWORD` is configured.
4. Test database path can be set with `CONTROLE_FINANCEIRO_DB_PATH` when needed.

## Setup

```bash
.venv/bin/python -m pip install -e ".[dev]"
```

## Runtime Secret Setup

For local validation, configure `.streamlit/secrets.toml` with:

```toml
APP_ACCESS_PASSWORD = "change-me-now"
```

For hosted deployment, configure the same key in Streamlit Cloud secrets.

## Validation Scenarios

### 1) Locked state blocks financial initialization

Run:

```bash
.venv/bin/python -m pytest -q tests/test_ui_auth_access.py::test_password_gate_blocks_financial_ui_before_unlock
```

Expected outcome:
- Test passes.
- Only password prompt state is visible.
- No financial summary/cycle/table/lock content is rendered.

### 2) Correct password unlocks dashboard

Run:

```bash
.venv/bin/python -m pytest -q tests/test_ui_auth_access.py::test_password_gate_unlocks_dashboard_on_valid_password
```

Expected outcome:
- Test passes.
- Dashboard renders with existing financial workflow.

### 3) Missing password config fails closed

Run:

```bash
.venv/bin/python -m pytest -q tests/test_ui_auth_access.py::test_password_gate_missing_secret_fails_closed
```

Expected outcome:
- Test passes.
- App remains blocked with non-sensitive configuration feedback.

## Full Regression Gate

Run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff format --check .
.venv/bin/python -m ruff check .
```

Expected outcome:
- All checks pass.
- Financial data remains hidden until password unlock.

## References

- Data model: [data-model.md](./data-model.md)
- Contracts:
  - [contracts/auth-config-contract.md](./contracts/auth-config-contract.md)
  - [contracts/access-state-ui-contract.md](./contracts/access-state-ui-contract.md)
- Feature spec: [spec.md](./spec.md)
