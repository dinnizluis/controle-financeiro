import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def build_password_gate_app(monkeypatch, tmp_path):
    from controle_financeiro import app as app_module

    database_path = tmp_path / "budget.sqlite"
    monkeypatch.setenv("CONTROLE_FINANCEIRO_DB_PATH", str(database_path))

    original_get_service = app_module.get_service
    if hasattr(original_get_service, "clear"):
        original_get_service.clear()

    def _build(*, configured_password: str | None = "change-me", unlocked: bool = False):
        service_calls = {"count": 0}

        def tracked_get_service():
            service_calls["count"] += 1
            return original_get_service()

        monkeypatch.setattr(
            app_module,
            "_get_configured_access_password",
            lambda: configured_password,
        )
        monkeypatch.setattr(app_module, "get_service", tracked_get_service)

        app = AppTest.from_file("streamlit_app.py")
        if unlocked:
            app.session_state[app_module.ACCESS_UNLOCKED_SESSION_KEY] = True
        return app, service_calls

    return _build
