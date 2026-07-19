from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import streamlit as st

from controle_financeiro.models import (
    FixedCostInput,
    MonthlyIncomeInput,
    VariableExpenseInput,
    cycle_window,
)
from controle_financeiro.service import BudgetService
from controle_financeiro.storage import DomainLockError, SqliteBudgetRepository


@st.cache_resource
def get_service() -> BudgetService:
    repository = SqliteBudgetRepository(Path("data") / "controle_financeiro.db")
    return BudgetService(repository)


def _money(value: Decimal) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _date_label(value: date | None) -> str:
    if value is None:
        return "-"
    return value.isoformat()


def _datetime_label(value: Any) -> str:
    return value.strftime("%Y-%m-%d %H:%M")


def main() -> None:
    st.set_page_config(page_title="controle-financeiro", layout="wide")
    st.title("Controle Financeiro")
    st.caption("Execucao da Spec001: modelo por ciclo com custos fixos e despesas variaveis.")

    service = get_service()
    today = date.today()
    default_month = date(today.year, today.month, 1)

    with st.sidebar:
        reference_month = st.date_input(
            "Mes de referencia",
            value=default_month,
            help="Todos os registros e indicadores nesta tela se referem apenas ao ciclo mensal selecionado.",
        )
        cycle_key = f"{reference_month.year:04d}-{reference_month.month:02d}"
        st.caption(f"Ciclo selecionado: {cycle_key}")

    summary = service.get_summary(cycle_key)
    cycle_start, cycle_end = cycle_window(cycle_key)

    st.info(
        "Periodo selecionado: "
        f"{cycle_key} (from {cycle_start.isoformat()} to {cycle_end.isoformat()}). "
        "Crie e edite registros de um ciclo por vez; altere o mes de referencia para gerenciar outros meses."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Custos fixos", _money(summary.total_fixed_cost))
    col2.metric("Despesas variaveis", _money(summary.total_variable_expense))
    col3.metric("Margem projetada", _money(summary.projected_margin))
    st.write(f"Status: **{summary.status.value}**")

    tab_fixed, tab_variable, tab_income = st.tabs(
        ["Custos fixos", "Despesas variaveis", "Renda do ciclo"]
    )

    with tab_fixed:
        st.subheader("Cadastrar custo fixo")
        with st.form("fixed_cost_form", clear_on_submit=True):
            name = st.text_input("Nome")
            amount = st.number_input("Valor", min_value=0.0, step=10.0)
            due_date = st.date_input("Data de vencimento", value=None, key="fixed_due_date_create")
            is_active = st.checkbox("Ativo", value=True)
            submitted = st.form_submit_button("Salvar custo fixo")
            if submitted:
                try:
                    service.add_fixed_cost(
                        cycle_key,
                        FixedCostInput(
                            name=name,
                            amount=Decimal(str(amount)),
                            due_date=due_date,
                            is_active=is_active,
                        ),
                        today,
                    )
                    st.rerun()
                except (ValueError, DomainLockError) as exc:
                    st.error(str(exc))

        fixed_costs = service.list_fixed_costs(cycle_key)

        st.subheader("Editar custo fixo")
        if fixed_costs:
            fixed_options = {item.id: item for item in fixed_costs}
            selected_fixed_id = st.selectbox(
                "Selecione o custo fixo",
                options=list(fixed_options.keys()),
                format_func=lambda item_id: (
                    f"{fixed_options[item_id].name} | {_money(fixed_options[item_id].amount)}"
                    f" | {_date_label(fixed_options[item_id].due_date)}"
                ),
                key="fixed_edit_select",
            )
            selected_fixed = fixed_options[selected_fixed_id]
            with st.form("fixed_cost_edit_form"):
                edit_name = st.text_input("Nome", value=selected_fixed.name, key="fixed_name_edit")
                edit_amount = st.number_input(
                    "Valor",
                    min_value=0.0,
                    step=10.0,
                    value=float(selected_fixed.amount),
                    key="fixed_amount_edit",
                )
                edit_due_date = st.date_input(
                    "Data de vencimento",
                    value=selected_fixed.due_date,
                    key="fixed_due_date_edit",
                )
                edit_is_active = st.checkbox("Ativo", value=selected_fixed.is_active, key="fixed_active_edit")
                edit_submitted = st.form_submit_button("Atualizar custo fixo")
                if edit_submitted:
                    try:
                        service.update_fixed_cost(
                            cycle_key,
                            selected_fixed.id,
                            FixedCostInput(
                                name=edit_name,
                                amount=Decimal(str(edit_amount)),
                                due_date=edit_due_date,
                                is_active=edit_is_active,
                            ),
                            today,
                        )
                        st.rerun()
                    except (ValueError, DomainLockError) as exc:
                        st.error(str(exc))
        else:
            st.info("Ainda nao ha custos fixos para este ciclo.")

        fixed_costs = service.list_fixed_costs(cycle_key)

        st.subheader("Custos fixos do ciclo")
        fixed_status_filter = st.selectbox(
            "Filtro de status",
            options=["Todos", "Ativos", "Inativos"],
            key="fixed_status_filter",
        )
        fixed_sort = st.selectbox(
            "Ordenacao",
            options=["Mais recentes", "Mais antigos", "Vencimento crescente", "Vencimento decrescente"],
            key="fixed_sort",
        )

        filtered_fixed = fixed_costs
        if fixed_status_filter == "Ativos":
            filtered_fixed = [item for item in filtered_fixed if item.is_active]
        elif fixed_status_filter == "Inativos":
            filtered_fixed = [item for item in filtered_fixed if not item.is_active]

        if fixed_sort == "Mais antigos":
            filtered_fixed = sorted(filtered_fixed, key=lambda item: item.created_at)
        elif fixed_sort == "Vencimento crescente":
            filtered_fixed = sorted(
                filtered_fixed,
                key=lambda item: (item.due_date is None, item.due_date or date.max),
            )
        elif fixed_sort == "Vencimento decrescente":
            filtered_fixed = sorted(
                filtered_fixed,
                key=lambda item: (item.due_date is None, item.due_date or date.min),
                reverse=True,
            )

        fixed_table = [
            {
                "id": item.id,
                "name": item.name,
                "amount": _money(item.amount),
                "due_date": _date_label(item.due_date),
                "is_active": item.is_active,
                "updated_at": _datetime_label(item.updated_at),
            }
            for item in filtered_fixed
        ]
        st.dataframe(fixed_table, hide_index=True)

    with tab_variable:
        st.subheader("Cadastrar despesa variavel")
        with st.form("variable_expense_form", clear_on_submit=True):
            description = st.text_input("Descricao")
            amount = st.number_input("Valor", min_value=0.0, step=10.0, key="variable_amount")
            due_date = st.date_input("Data de vencimento", value=None, key="variable_due_date")
            submitted = st.form_submit_button("Salvar despesa variavel")
            if submitted:
                try:
                    service.add_variable_expense(
                        cycle_key,
                        VariableExpenseInput(
                            description=description,
                            amount=Decimal(str(amount)),
                            due_date=due_date,
                        ),
                        today,
                    )
                    st.rerun()
                except (ValueError, DomainLockError) as exc:
                    st.error(str(exc))

        variable_expenses = service.list_variable_expenses(cycle_key)

        st.subheader("Editar despesa variavel")
        if variable_expenses:
            variable_options = {item.id: item for item in variable_expenses}
            selected_variable_id = st.selectbox(
                "Selecione a despesa variavel",
                options=list(variable_options.keys()),
                format_func=lambda item_id: (
                    f"{variable_options[item_id].description} | {_money(variable_options[item_id].amount)}"
                    f" | {_date_label(variable_options[item_id].due_date)}"
                ),
                key="variable_edit_select",
            )
            selected_variable = variable_options[selected_variable_id]
            with st.form("variable_expense_edit_form"):
                edit_description = st.text_input(
                    "Descricao",
                    value=selected_variable.description,
                    key="variable_description_edit",
                )
                edit_amount = st.number_input(
                    "Valor",
                    min_value=0.0,
                    step=10.0,
                    value=float(selected_variable.amount),
                    key="variable_amount_edit",
                )
                edit_due_date = st.date_input(
                    "Data de vencimento",
                    value=selected_variable.due_date,
                    key="variable_due_date_edit",
                )
                edit_submitted = st.form_submit_button("Atualizar despesa variavel")
                if edit_submitted:
                    try:
                        service.update_variable_expense(
                            cycle_key,
                            selected_variable.id,
                            VariableExpenseInput(
                                description=edit_description,
                                amount=Decimal(str(edit_amount)),
                                due_date=edit_due_date,
                            ),
                            today,
                        )
                        st.rerun()
                    except (ValueError, DomainLockError) as exc:
                        st.error(str(exc))
        else:
            st.info("Ainda nao ha despesas variaveis para este ciclo.")

        variable_expenses = service.list_variable_expenses(cycle_key)

        st.subheader("Despesas variaveis do ciclo")
        variable_query = st.text_input("Buscar por descricao", key="variable_query")
        variable_sort = st.selectbox(
            "Ordenacao",
            options=["Mais recentes", "Mais antigos", "Vencimento crescente", "Vencimento decrescente"],
            key="variable_sort",
        )

        filtered_variable = variable_expenses
        if variable_query.strip():
            query = variable_query.strip().lower()
            filtered_variable = [item for item in filtered_variable if query in item.description.lower()]

        if variable_sort == "Mais antigos":
            filtered_variable = sorted(filtered_variable, key=lambda item: item.created_at)
        elif variable_sort == "Vencimento crescente":
            filtered_variable = sorted(
                filtered_variable,
                key=lambda item: (item.due_date is None, item.due_date or date.max),
            )
        elif variable_sort == "Vencimento decrescente":
            filtered_variable = sorted(
                filtered_variable,
                key=lambda item: (item.due_date is None, item.due_date or date.min),
                reverse=True,
            )

        variable_table = [
            {
                "id": item.id,
                "description": item.description,
                "amount": _money(item.amount),
                "due_date": _date_label(item.due_date),
                "updated_at": _datetime_label(item.updated_at),
            }
            for item in filtered_variable
        ]
        st.dataframe(variable_table, hide_index=True)

    with tab_income:
        existing_monthly_income = service.get_monthly_income(cycle_key)

        st.subheader("Cadastrar ou editar renda do ciclo")
        st.caption("Registre a renda e a saida de caixa para reserva deste ciclo. Nao ha uma etapa de fechamento: o ciclo trava automaticamente apos a data limite.")
        with st.form("monthly_income_form"):
            income_total = st.number_input(
                "Renda total",
                min_value=0.0,
                step=100.0,
                value=float(existing_monthly_income.income_total) if existing_monthly_income else 0.0,
            )
            reserve_cash_outflow = st.number_input(
                "Saida de caixa para reserva",
                min_value=0.0,
                step=10.0,
                value=float(existing_monthly_income.reserve_cash_outflow) if existing_monthly_income else 0.0,
            )
            submitted = st.form_submit_button(
                "Atualizar renda do ciclo" if existing_monthly_income else "Salvar renda do ciclo"
            )
            if submitted:
                try:
                    service.save_monthly_income(
                        cycle_key,
                        MonthlyIncomeInput(
                            income_total=Decimal(str(income_total)),
                            reserve_cash_outflow=Decimal(str(reserve_cash_outflow)),
                        ),
                        today,
                    )
                    st.rerun()
                except (ValueError, DomainLockError) as exc:
                    st.error(str(exc))

        monthly_income = service.get_monthly_income(cycle_key)

        st.subheader("Renda do ciclo")
        if monthly_income is None:
            st.info("Ainda nao ha renda registrada para este ciclo.")
        else:
            income_table = [
                {
                    "id": monthly_income.id,
                    "income_total": _money(monthly_income.income_total),
                    "reserve_cash_outflow": _money(monthly_income.reserve_cash_outflow),
                    "updated_at": _datetime_label(monthly_income.updated_at),
                }
            ]
            st.dataframe(income_table, hide_index=True)

    st.caption(f"Projeto: {Path(__file__).resolve().parent.parent.parent.name}")


if __name__ == "__main__":
    main()
