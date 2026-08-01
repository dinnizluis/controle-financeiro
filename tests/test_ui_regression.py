import os
from datetime import date
from decimal import Decimal

from controle_financeiro.models import FixedCostInput, MonthlyIncomeInput, VariableExpenseInput
from controle_financeiro.service import BudgetService
from controle_financeiro.storage import SqliteBudgetRepository


def test_empty_cycle_exposes_entry_forms_and_guidance(build_password_gate_app):
    app, _ = build_password_gate_app(configured_password="change-me", unlocked=True)
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


def test_populated_cycle_exposes_edit_forms_and_income_table(build_password_gate_app):
    app, _ = build_password_gate_app(configured_password="change-me", unlocked=True)
    service = BudgetService(SqliteBudgetRepository(os.environ["CONTROLE_FINANCEIRO_DB_PATH"]))
    current_date = date(2026, 8, 20)

    service.add_fixed_cost(
        "2026-08",
        FixedCostInput(
            name="Aluguel",
            amount=Decimal("2500.00"),
            due_date=date(2026, 8, 5),
            is_active=True,
        ),
        current_date,
    )
    service.add_variable_expense(
        "2026-08",
        VariableExpenseInput(
            description="Mercado",
            amount=Decimal("450.00"),
            due_date=date(2026, 8, 10),
        ),
        current_date,
    )
    service.save_monthly_income(
        "2026-08",
        MonthlyIncomeInput(
            income_total=Decimal("10000.00"),
            reserve_cash_outflow=Decimal("500.00"),
        ),
        current_date,
    )

    app.run()

    assert not app.exception
    assert {button.label for button in app.button} >= {
        "Salvar custo fixo",
        "Atualizar custo fixo",
        "Salvar despesa variavel",
        "Atualizar despesa variavel",
        "Atualizar renda do ciclo",
    }
    assert {selectbox.label for selectbox in app.selectbox} >= {
        "Selecione o custo fixo",
        "Selecione a despesa variavel",
        "Filtro de status",
        "Ordenacao",
    }
    assert not {message.value for message in app.info} & {
        "Ainda nao ha custos fixos para este ciclo.",
        "Ainda nao ha despesas variaveis para este ciclo.",
        "Ainda nao ha renda registrada para este ciclo.",
    }
    assert len(app.dataframe) >= 3
