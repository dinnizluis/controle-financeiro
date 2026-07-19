from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import streamlit as st

from controle_financeiro.models import FixedCostInput, MonthlyCloseInput, VariableExpenseInput, WeeklyCheckinInput
from controle_financeiro.service import BudgetService
from controle_financeiro.storage import DomainLockError, SqliteBudgetRepository


@st.cache_resource
def get_service() -> BudgetService:
    repository = SqliteBudgetRepository(Path("data") / "controle_financeiro.db")
    return BudgetService(repository)


def _money(value: Decimal) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main() -> None:
    st.set_page_config(page_title="controle-financeiro", layout="wide")
    st.title("Controle Financeiro")
    st.caption("Spec001 execution: cycle-based data model and weekly check-ins.")

    service = get_service()
    today = date.today()

    with st.sidebar:
        cycle_key = st.text_input("Cycle key (YYYY-MM)", value=f"{today.year:04d}-{today.month:02d}")

    summary = service.get_summary(cycle_key)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Fixed costs", _money(summary.total_fixed_cost))
    col2.metric("Variable expenses", _money(summary.total_variable_expense))
    col3.metric("Latest invoice", _money(summary.latest_open_invoice_total))
    col4.metric("Projected margin", _money(summary.projected_margin))
    st.write(f"Status: **{summary.status.value}**")

    tab_fixed, tab_variable, tab_checkin, tab_close = st.tabs(
        ["Fixed costs", "Variable expenses", "Weekly check-ins", "Month close"]
    )

    with tab_fixed:
        with st.form("fixed_cost_form", clear_on_submit=True):
            name = st.text_input("Name")
            amount = st.number_input("Amount", min_value=0.0, step=10.0)
            due_date = st.date_input("Due date", value=None)
            is_active = st.checkbox("Is active", value=True)
            submitted = st.form_submit_button("Save fixed cost")
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
                    st.success("Fixed cost saved")
                except (ValueError, DomainLockError) as exc:
                    st.error(str(exc))

    with tab_variable:
        with st.form("variable_expense_form", clear_on_submit=True):
            description = st.text_input("Description")
            amount = st.number_input("Amount", min_value=0.0, step=10.0, key="variable_amount")
            due_date = st.date_input("Due date", value=None, key="variable_due_date")
            submitted = st.form_submit_button("Save variable expense")
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
                    st.success("Variable expense saved")
                except (ValueError, DomainLockError) as exc:
                    st.error(str(exc))

    with tab_checkin:
        with st.form("weekly_checkin_form", clear_on_submit=True):
            checkin_date = st.date_input("Check-in date", value=today)
            open_invoice_total = st.number_input("Open invoice total", min_value=0.0, step=10.0)
            submitted = st.form_submit_button("Save check-in")
            if submitted:
                try:
                    service.add_weekly_checkin(
                        cycle_key,
                        WeeklyCheckinInput(
                            checkin_date=checkin_date,
                            open_invoice_total=Decimal(str(open_invoice_total)),
                        ),
                        today,
                    )
                    st.success("Weekly check-in saved")
                except (ValueError, DomainLockError) as exc:
                    st.error(str(exc))

    with tab_close:
        with st.form("month_close_form", clear_on_submit=True):
            income_total = st.number_input("Income total", min_value=0.0, step=100.0)
            final_invoice_total = st.number_input("Final invoice total", min_value=0.0, step=10.0)
            reserve_cash_outflow = st.number_input("Reserve cash outflow", min_value=0.0, step=10.0)
            submitted = st.form_submit_button("Save monthly close")
            if submitted:
                try:
                    service.save_monthly_close(
                        cycle_key,
                        MonthlyCloseInput(
                            income_total=Decimal(str(income_total)),
                            final_invoice_total=Decimal(str(final_invoice_total)),
                            reserve_cash_outflow=Decimal(str(reserve_cash_outflow)),
                        ),
                        today,
                    )
                    st.success("Monthly close saved")
                except (ValueError, DomainLockError) as exc:
                    st.error(str(exc))

    st.caption(f"Workspace: {Path(__file__).resolve().parent.parent.parent.name}")


if __name__ == "__main__":
    main()
