# Contract: Access State to UI Behavior (MVP-0)

Defines required user-visible behavior for password lock and unlock states.

## Purpose

Guarantee deterministic non-sensitive behavior before unlock, with financial rendering only after valid password.

## State Contract

| Access state | Required UI | Forbidden UI | Service initialization |
|-------------|-------------|--------------|------------------------|
| locked | Password prompt and non-sensitive helper text | Summary metrics, cycle selector, data tables, lock/history details | Must not run |
| config_error | Non-sensitive configuration error text | Summary metrics, cycle selector, data tables, lock/history details | Must not run |
| unlocked | Existing dashboard shell and monthly workflow | N/A | Must run |

## Behavioral Guarantees

1. First render starts in `locked` when password is configured.
2. Missing/invalid password configuration yields `config_error` and remains blocked.
3. Wrong password keeps app `locked` and does not initialize financial service.
4. Correct password transitions app to `unlocked` and allows normal dashboard behavior.

## Regression Mapping

This contract is verified by planned tests in:
- `tests/test_ui_auth_access.py`
