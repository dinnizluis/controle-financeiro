from streamlit.testing.v1 import AppTest


def test_empty_cycle_exposes_entry_forms_and_guidance(monkeypatch, tmp_path):
    monkeypatch.setenv("CONTROLE_FINANCEIRO_DB_PATH", str(tmp_path / "budget.sqlite"))

    app = AppTest.from_file("streamlit_app.py")
    app.run()

    assert not app.exception
    assert app.title[0].value == "Controle Financeiro"
    assert [tab.label for tab in app.tabs] == [
        "Custos fixos",
        "Despesas variaveis",
        "Renda do ciclo",
    ]
    assert {button.label for button in app.button} >= {
        "Salvar custo fixo",
        "Salvar despesa variavel",
        "Salvar renda do ciclo",
    }
    assert {message.value for message in app.info} >= {
        "Ainda nao ha custos fixos para este ciclo.",
        "Ainda nao ha despesas variaveis para este ciclo.",
        "Ainda nao ha renda registrada para este ciclo.",
    }
