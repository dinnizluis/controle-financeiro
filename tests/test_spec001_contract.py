from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select

from controle_financeiro.models import (
    FixedCostInput,
    MonthSummaryStatus,
    MonthlyCloseInput,
    VariableExpenseInput,
    WeeklyCheckinInput,
    cycle_window,
)
from controle_financeiro.service import BudgetService
from controle_financeiro.storage import DomainLockError, MonthCycleORM, SqliteBudgetRepository


def test_cycle_window_matches_business_day_rule():
    start_date, end_date = cycle_window("2026-07")

    assert start_date == date(2026, 7, 31)
    assert end_date == date(2026, 8, 28)


def test_updates_allowed_through_end_date_blocked_d_plus_one(tmp_path):
    repository = SqliteBudgetRepository(tmp_path / "db.sqlite")
    service = BudgetService(repository)

    service.add_fixed_cost(
        "2026-07",
        FixedCostInput(name="Rent", amount=Decimal("2500.00"), is_active=True),
        current_date=date(2026, 8, 28),
    )

    with pytest.raises(DomainLockError):
        service.add_fixed_cost(
            "2026-07",
            FixedCostInput(name="Gym", amount=Decimal("100.00"), is_active=True),
            current_date=date(2026, 8, 29),
        )


def test_duplicate_weekly_checkin_keeps_history_and_switches_current(tmp_path):
    repository = SqliteBudgetRepository(tmp_path / "db.sqlite")
    service = BudgetService(repository)

    service.add_weekly_checkin(
        "2026-07",
        WeeklyCheckinInput(checkin_date=date(2026, 8, 2), open_invoice_total=Decimal("1000.00")),
        current_date=date(2026, 8, 2),
    )
    service.add_weekly_checkin(
        "2026-07",
        WeeklyCheckinInput(checkin_date=date(2026, 8, 2), open_invoice_total=Decimal("1500.00")),
        current_date=date(2026, 8, 2),
    )

    checkins = service.list_weekly_checkins("2026-07")
    assert len(checkins) == 2
    assert checkins[0].is_current is True
    assert checkins[0].open_invoice_total == Decimal("1500.00")
    assert checkins[1].is_current is False


def test_fixed_cost_month_instance_allows_direct_update_before_lock(tmp_path):
    repository = SqliteBudgetRepository(tmp_path / "db.sqlite")
    service = BudgetService(repository)

    item = service.add_fixed_cost(
        "2026-07",
        FixedCostInput(name="Rent", amount=Decimal("2500.00"), due_date=date(2026, 8, 5), is_active=True),
        current_date=date(2026, 8, 10),
    )

    updated = service.update_fixed_cost(
        "2026-07",
        item.id,
        FixedCostInput(name="Rent", amount=Decimal("2600.00"), due_date=date(2026, 8, 6), is_active=True),
        current_date=date(2026, 8, 10),
    )

    assert updated.amount == Decimal("2600.00")
    assert updated.due_date == date(2026, 8, 6)


def test_monthly_close_can_update_until_end_date_then_locks(tmp_path):
    repository = SqliteBudgetRepository(tmp_path / "db.sqlite")
    service = BudgetService(repository)

    service.add_variable_expense(
        "2026-07",
        VariableExpenseInput(description="Cash only", amount=Decimal("120.00")),
        current_date=date(2026, 8, 20),
    )
    service.save_monthly_close(
        "2026-07",
        MonthlyCloseInput(
            income_total=Decimal("10000.00"),
            final_invoice_total=Decimal("3500.00"),
            reserve_cash_outflow=Decimal("200.00"),
        ),
        current_date=date(2026, 8, 28),
    )
    updated = service.save_monthly_close(
        "2026-07",
        MonthlyCloseInput(
            income_total=Decimal("10000.00"),
            final_invoice_total=Decimal("3600.00"),
            reserve_cash_outflow=Decimal("250.00"),
        ),
        current_date=date(2026, 8, 28),
    )

    assert updated.final_invoice_total == Decimal("3600.00")

    with pytest.raises(DomainLockError):
        service.save_monthly_close(
            "2026-07",
            MonthlyCloseInput(
                income_total=Decimal("10000.00"),
                final_invoice_total=Decimal("3650.00"),
                reserve_cash_outflow=Decimal("250.00"),
            ),
            current_date=date(2026, 8, 29),
        )


def test_invalid_cycle_key_month_is_rejected(tmp_path):
    repository = SqliteBudgetRepository(tmp_path / "db.sqlite")
    service = BudgetService(repository)

    with pytest.raises(ValueError):
        service.get_summary("2026-13")


@pytest.mark.parametrize(
    ("close_payload", "expected_status", "expected_margin"),
    [
        (
            MonthlyCloseInput(
                income_total=Decimal("1000.00"),
                final_invoice_total=Decimal("900.00"),
                reserve_cash_outflow=Decimal("0.00"),
            ),
            MonthSummaryStatus.HEALTHY,
            Decimal("100.00"),
        ),
        (
            MonthlyCloseInput(
                income_total=Decimal("1000.00"),
                final_invoice_total=Decimal("1050.00"),
                reserve_cash_outflow=Decimal("0.00"),
            ),
            MonthSummaryStatus.ATTENTION,
            Decimal("-50.00"),
        ),
        (
            MonthlyCloseInput(
                income_total=Decimal("1000.00"),
                final_invoice_total=Decimal("1060.00"),
                reserve_cash_outflow=Decimal("0.00"),
            ),
            MonthSummaryStatus.CRITICAL,
            Decimal("-60.00"),
        ),
    ],
)
def test_summary_status_thresholds_after_monthly_close(tmp_path, close_payload, expected_status, expected_margin):
    repository = SqliteBudgetRepository(tmp_path / "db.sqlite")
    service = BudgetService(repository)

    service.save_monthly_close("2026-07", close_payload, current_date=date(2026, 8, 28))

    summary = service.get_summary("2026-07")
    assert summary.status == expected_status
    assert summary.projected_margin == expected_margin


def test_summary_status_open_without_monthly_close(tmp_path):
    repository = SqliteBudgetRepository(tmp_path / "db.sqlite")
    service = BudgetService(repository)

    summary = service.get_summary("2026-07")

    assert summary.status == MonthSummaryStatus.OPEN


def test_reading_summary_does_not_create_cycle(tmp_path):
    repository = SqliteBudgetRepository(tmp_path / "db.sqlite")
    service = BudgetService(repository)

    service.get_summary("2026-07")

    with repository._session() as session:
        cycles = session.scalars(select(MonthCycleORM)).all()

    assert cycles == []
