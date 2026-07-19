from __future__ import annotations

from datetime import date
from decimal import Decimal

from controle_financeiro.models import (
    FixedCostInput,
    MonthSummary,
    MonthSummaryStatus,
    MonthlyCloseInput,
    VariableExpenseInput,
    WeeklyCheckinInput,
    as_money,
)
from controle_financeiro.storage import SqliteBudgetRepository


class BudgetService:
    def __init__(self, repository: SqliteBudgetRepository):
        self.repository = repository

    def add_fixed_cost(self, cycle_key: str, payload: FixedCostInput, current_date: date):
        return self.repository.save_fixed_cost(cycle_key=cycle_key, payload=payload, current_date=current_date)

    def update_fixed_cost(self, cycle_key: str, fixed_cost_id: str, payload: FixedCostInput, current_date: date):
        return self.repository.save_fixed_cost(
            cycle_key=cycle_key,
            payload=payload,
            current_date=current_date,
            fixed_cost_id=fixed_cost_id,
        )

    def list_fixed_costs(self, cycle_key: str):
        return self.repository.list_fixed_costs(cycle_key)

    def add_variable_expense(self, cycle_key: str, payload: VariableExpenseInput, current_date: date):
        return self.repository.save_variable_expense(cycle_key=cycle_key, payload=payload, current_date=current_date)

    def update_variable_expense(
        self, cycle_key: str, variable_expense_id: str, payload: VariableExpenseInput, current_date: date
    ):
        return self.repository.save_variable_expense(
            cycle_key=cycle_key,
            payload=payload,
            current_date=current_date,
            variable_expense_id=variable_expense_id,
        )

    def list_variable_expenses(self, cycle_key: str):
        return self.repository.list_variable_expenses(cycle_key)

    def add_weekly_checkin(self, cycle_key: str, payload: WeeklyCheckinInput, current_date: date):
        return self.repository.save_weekly_checkin(cycle_key=cycle_key, payload=payload, current_date=current_date)

    def list_weekly_checkins(self, cycle_key: str):
        return self.repository.list_weekly_checkins(cycle_key)

    def save_monthly_close(self, cycle_key: str, payload: MonthlyCloseInput, current_date: date):
        return self.repository.save_monthly_close(cycle_key=cycle_key, payload=payload, current_date=current_date)

    def get_summary(self, cycle_key: str) -> MonthSummary:
        fixed_costs = self.repository.list_fixed_costs(cycle_key)
        variable_expenses = self.repository.list_variable_expenses(cycle_key)
        checkins = self.repository.list_weekly_checkins(cycle_key)
        monthly_close = self.repository.get_monthly_close(cycle_key)

        total_fixed_cost = as_money(
            sum((item.amount for item in fixed_costs if item.is_active), start=Decimal("0.00"))
        )
        total_variable_expense = as_money(sum((item.amount for item in variable_expenses), start=Decimal("0.00")))

        current_checkins = [item for item in checkins if item.is_current]
        latest_open_invoice_total = as_money(current_checkins[0].open_invoice_total) if current_checkins else Decimal("0.00")

        if monthly_close is None:
            projected_margin = as_money((total_fixed_cost + total_variable_expense + latest_open_invoice_total) * Decimal("-1"))
            status = MonthSummaryStatus.OPEN
        else:
            projected_margin = as_money(
                monthly_close.income_total
                - total_fixed_cost
                - total_variable_expense
                - monthly_close.final_invoice_total
                - monthly_close.reserve_cash_outflow
            )
            if projected_margin >= 0:
                status = MonthSummaryStatus.HEALTHY
            elif projected_margin >= as_money(monthly_close.income_total * Decimal("-0.05")):
                status = MonthSummaryStatus.ATTENTION
            else:
                status = MonthSummaryStatus.CRITICAL

        return MonthSummary(
            cycle_key=cycle_key,
            total_fixed_cost=total_fixed_cost,
            total_variable_expense=total_variable_expense,
            latest_open_invoice_total=latest_open_invoice_total,
            projected_margin=projected_margin,
            status=status,
        )
