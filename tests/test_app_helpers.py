from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from streamlit.errors import StreamlitSecretNotFoundError

from controle_financeiro import app


class SecretsStub:
    def __init__(self, value=None, *, should_raise: bool = False):
        self.value = value
        self.should_raise = should_raise

    def get(self, key: str):
        assert key == app.ACCESS_PASSWORD_SECRET_KEY
        if self.should_raise:
            raise StreamlitSecretNotFoundError("APP_ACCESS_PASSWORD missing")
        return self.value


@pytest.mark.parametrize(
    ("secret_value", "expected"),
    [("change-me", "change-me"), ("   ", None), (123, None)],
)
def test_get_configured_access_password_validates_secret(monkeypatch, secret_value, expected):
    monkeypatch.setattr(app.st, "secrets", SecretsStub(secret_value), raising=False)

    assert app._get_configured_access_password() == expected


def test_get_configured_access_password_returns_none_when_secret_missing(monkeypatch):
    monkeypatch.setattr(app.st, "secrets", SecretsStub(should_raise=True), raising=False)

    assert app._get_configured_access_password() is None


def test_access_session_helpers_round_trip(monkeypatch):
    session_state = {}
    monkeypatch.setattr(app.st, "session_state", session_state, raising=False)

    assert app._is_access_unlocked() is False

    app._set_access_unlocked(True)

    assert app._is_access_unlocked() is True


def test_display_format_helpers_cover_empty_and_populated_values():
    assert app._money(Decimal("1234.5")) == "R$ 1.234,50"
    assert app._date_label(None) == "-"
    assert app._date_label(date(2026, 8, 1)) == "2026-08-01"
    assert app._datetime_label(datetime(2026, 8, 1, 11, 52, tzinfo=UTC)) == "2026-08-01 11:52"


def test_get_service_uses_database_path_from_environment(monkeypatch, tmp_path):
    database_path = tmp_path / "custom.sqlite"
    monkeypatch.setenv("CONTROLE_FINANCEIRO_DB_PATH", str(database_path))

    if hasattr(app.get_service, "clear"):
        app.get_service.clear()

    service = app.get_service()

    assert service.repository.engine.url.database == str(database_path)

    if hasattr(app.get_service, "clear"):
        app.get_service.clear()
