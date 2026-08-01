from controle_financeiro.app import ACCESS_UNLOCKED_SESSION_KEY


def test_password_gate_blocks_financial_ui_before_unlock(build_password_gate_app):
    app, service_calls = build_password_gate_app(configured_password="change-me")

    app.run()

    assert not app.exception
    assert app.subheader[0].value == "Acesso protegido"
    assert app.text_input[0].label == "Senha de acesso"
    assert {button.label for button in app.button} == {"Entrar"}
    assert not app.tabs
    assert not app.metric
    assert not app.dataframe
    assert service_calls["count"] == 0


def test_password_gate_unlocks_dashboard_on_valid_password(build_password_gate_app):
    app, service_calls = build_password_gate_app(configured_password="change-me")

    app.run()
    app.text_input[0].set_value("change-me")
    app.button[0].click()
    app.run()

    assert not app.exception
    assert app.session_state[ACCESS_UNLOCKED_SESSION_KEY] is True
    assert [tab.label for tab in app.tabs] == [
        "Custos fixos",
        "Despesas variaveis",
        "Renda do ciclo",
    ]
    assert service_calls["count"] >= 1


def test_password_gate_missing_secret_fails_closed(build_password_gate_app):
    app, service_calls = build_password_gate_app(configured_password=None)

    app.run()

    assert not app.exception
    assert app.error[0].value == (
        "Configuracao de acesso indisponivel. Defina APP_ACCESS_PASSWORD nos secrets "
        "para desbloquear o app."
    )
    assert not app.tabs
    assert not app.metric
    assert not app.dataframe

    assert service_calls["count"] == 0


def test_password_gate_wrong_password_keeps_app_locked(build_password_gate_app):
    app, service_calls = build_password_gate_app(configured_password="change-me")

    app.run()
    app.text_input[0].set_value("wrong-password")
    app.button[0].click()
    app.run()

    assert not app.exception
    assert app.error[0].value == "Senha invalida."
    assert ACCESS_UNLOCKED_SESSION_KEY not in app.session_state
    assert not app.tabs
    assert not app.metric
    assert not app.dataframe
    assert service_calls["count"] == 0
