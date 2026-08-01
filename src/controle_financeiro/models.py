from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

MONEY_QUANTUM = Decimal("0.01")


def as_money(value: Decimal | float | str) -> Decimal:
    return Decimal(str(value)).quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


def utc_now() -> datetime:
    return datetime.now(UTC)


def month_key(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"


def parse_month_key(cycle_key: str) -> tuple[int, int]:
    parts = cycle_key.split("-")
    if len(parts) != 2:
        raise ValueError("invalid cycle key")

    year_part, month_part = parts
    if (
        len(year_part) != 4
        or len(month_part) != 2
        or not year_part.isdigit()
        or not month_part.isdigit()
    ):
        raise ValueError("invalid cycle key")

    year, month = int(year_part), int(month_part)
    if month < 1 or month > 12:
        raise ValueError("invalid cycle key")

    return year, month


def next_month(year: int, month: int) -> tuple[int, int]:
    if month == 12:
        return year + 1, 1
    return year, month + 1


def _business_days(year: int, month: int) -> list[date]:
    _, days = calendar.monthrange(year, month)
    result: list[date] = []
    for d in range(1, days + 1):
        candidate = date(year, month, d)
        if candidate.weekday() < 5:
            result.append(candidate)
    return result


def last_business_day(year: int, month: int) -> date:
    return _business_days(year, month)[-1]


def second_to_last_business_day(year: int, month: int) -> date:
    days = _business_days(year, month)
    if len(days) < 2:
        raise ValueError("month has fewer than two business days")
    return days[-2]


def cycle_window(cycle_key: str) -> tuple[date, date]:
    year, month = parse_month_key(cycle_key)
    start_date = last_business_day(year, month)
    next_year, next_month_value = next_month(year, month)
    end_date = second_to_last_business_day(next_year, next_month_value)
    return start_date, end_date


class CycleStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"


class MonthSummaryStatus(StrEnum):
    OPEN = "open"
    HEALTHY = "healthy"
    ATTENTION = "attention"
    CRITICAL = "critical"


class FixedCostInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    amount: Decimal
    due_date: date | None = None
    is_active: bool = True

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        normalized = as_money(value)
        if normalized < 0:
            raise ValueError("amount must be non-negative")
        return normalized


class VariableExpenseInput(BaseModel):
    description: str = Field(min_length=1, max_length=160)
    amount: Decimal
    due_date: date | None = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        normalized = as_money(value)
        if normalized < 0:
            raise ValueError("amount must be non-negative")
        return normalized


class MonthlyIncomeInput(BaseModel):
    income_total: Decimal
    reserve_cash_outflow: Decimal = Decimal("0.00")

    @field_validator("income_total", "reserve_cash_outflow")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        normalized = as_money(value)
        if normalized < 0:
            raise ValueError("amount must be non-negative")
        return normalized


@dataclass(frozen=True, slots=True)
class MonthCycleRecord:
    id: str
    cycle_key: str
    start_date: date
    end_date: date
    status: CycleStatus
    closed_at: datetime | None


@dataclass(frozen=True, slots=True)
class FixedCostRecord:
    id: str
    month_cycle_id: str
    name: str
    amount: Decimal
    due_date: date | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class VariableExpenseRecord:
    id: str
    month_cycle_id: str
    description: str
    amount: Decimal
    due_date: date | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class MonthlyIncomeRecord:
    id: str
    month_cycle_id: str
    income_total: Decimal
    reserve_cash_outflow: Decimal
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class MonthSummary:
    cycle_key: str
    total_fixed_cost: Decimal
    total_variable_expense: Decimal
    projected_margin: Decimal
    status: MonthSummaryStatus
