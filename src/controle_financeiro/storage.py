from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from controle_financeiro.models import (
    CycleStatus,
    FixedCostInput,
    FixedCostRecord,
    MonthCycleRecord,
    MonthlyIncomeInput,
    MonthlyIncomeRecord,
    VariableExpenseInput,
    VariableExpenseRecord,
    cycle_window,
    parse_month_key,
    utc_now,
)


class DomainLockError(RuntimeError):
    pass


class Base(DeclarativeBase):
    pass


class MonthCycleORM(Base):
    __tablename__ = "month_cycles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    cycle_key: Mapped[str] = mapped_column(String(7), nullable=False, unique=True, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default=CycleStatus.OPEN.value)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FixedCostORM(Base):
    __tablename__ = "fixed_costs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    month_cycle_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("month_cycles.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class VariableExpenseORM(Base):
    __tablename__ = "variable_expenses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    month_cycle_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("month_cycles.id"), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(String(160), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class MonthlyIncomeORM(Base):
    __tablename__ = "monthly_income"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    month_cycle_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("month_cycles.id"), nullable=False, unique=True
    )
    income_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reserve_cash_outflow: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def _id() -> str:
    return str(uuid.uuid4())


def build_engine(database_path: str | Path | None = None):
    if database_path is None:
        database_path = Path("data") / "controle_financeiro.db"
    else:
        database_path = Path(database_path)

    if str(database_path) == ":memory:":
        url = "sqlite+pysqlite:///:memory:"
    else:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite+pysqlite:///{database_path}"

    return create_engine(url, future=True)


class SqliteBudgetRepository:
    def __init__(self, database_path: str | Path | None = None):
        self.engine = build_engine(database_path)
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False, future=True)

    def _session(self) -> Session:
        return self.session_factory()

    def _get_cycle(self, session: Session, cycle_key: str) -> MonthCycleORM | None:
        # Keep read and write behavior consistent for invalid cycle keys.
        parse_month_key(cycle_key)
        return session.scalar(select(MonthCycleORM).where(MonthCycleORM.cycle_key == cycle_key))

    def _ensure_cycle(self, session: Session, cycle_key: str) -> MonthCycleORM:
        cycle = self._get_cycle(session, cycle_key)
        if cycle is not None:
            return cycle

        start_date, end_date = cycle_window(cycle_key)
        now = utc_now()
        cycle = MonthCycleORM(
            id=_id(),
            cycle_key=cycle_key,
            start_date=start_date,
            end_date=end_date,
            status=CycleStatus.OPEN.value,
            closed_at=None,
            created_at=now,
            updated_at=now,
        )
        session.add(cycle)
        session.flush()
        return cycle

    def _assert_unlocked(self, cycle: MonthCycleORM, current_date: date) -> None:
        if current_date > cycle.end_date:
            raise DomainLockError("cycle is locked from D+1 after end_date")

    def _to_cycle(self, item: MonthCycleORM) -> MonthCycleRecord:
        return MonthCycleRecord(
            id=item.id,
            cycle_key=item.cycle_key,
            start_date=item.start_date,
            end_date=item.end_date,
            status=CycleStatus(item.status),
            closed_at=item.closed_at,
        )

    def get_or_create_cycle(self, cycle_key: str) -> MonthCycleRecord:
        with self._session() as session:
            cycle = self._ensure_cycle(session, cycle_key)
            session.commit()
            return self._to_cycle(cycle)

    def save_fixed_cost(
        self,
        cycle_key: str,
        payload: FixedCostInput,
        current_date: date,
        fixed_cost_id: str | None = None,
    ) -> FixedCostRecord:
        with self._session() as session:
            cycle = self._ensure_cycle(session, cycle_key)
            self._assert_unlocked(cycle, current_date)
            now = utc_now()

            if fixed_cost_id is None:
                row = FixedCostORM(
                    id=_id(),
                    month_cycle_id=cycle.id,
                    name=payload.name,
                    amount=payload.amount,
                    due_date=payload.due_date,
                    is_active=payload.is_active,
                    created_at=now,
                    updated_at=now,
                )
                session.add(row)
            else:
                row = session.scalar(
                    select(FixedCostORM).where(
                        FixedCostORM.id == fixed_cost_id, FixedCostORM.month_cycle_id == cycle.id
                    )
                )
                if row is None:
                    raise ValueError("fixed cost not found")
                row.name = payload.name
                row.amount = payload.amount
                row.due_date = payload.due_date
                row.is_active = payload.is_active
                row.updated_at = now

            session.commit()
            session.refresh(row)
            return FixedCostRecord(
                id=row.id,
                month_cycle_id=row.month_cycle_id,
                name=row.name,
                amount=row.amount,
                due_date=row.due_date,
                is_active=row.is_active,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )

    def list_fixed_costs(self, cycle_key: str) -> list[FixedCostRecord]:
        with self._session() as session:
            cycle = self._get_cycle(session, cycle_key)
            if cycle is None:
                return []
            rows = session.scalars(
                select(FixedCostORM)
                .where(FixedCostORM.month_cycle_id == cycle.id)
                .order_by(FixedCostORM.created_at.desc())
            ).all()
            return [
                FixedCostRecord(
                    id=row.id,
                    month_cycle_id=row.month_cycle_id,
                    name=row.name,
                    amount=row.amount,
                    due_date=row.due_date,
                    is_active=row.is_active,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                )
                for row in rows
            ]

    def save_variable_expense(
        self,
        cycle_key: str,
        payload: VariableExpenseInput,
        current_date: date,
        variable_expense_id: str | None = None,
    ) -> VariableExpenseRecord:
        with self._session() as session:
            cycle = self._ensure_cycle(session, cycle_key)
            self._assert_unlocked(cycle, current_date)
            now = utc_now()

            if variable_expense_id is None:
                row = VariableExpenseORM(
                    id=_id(),
                    month_cycle_id=cycle.id,
                    description=payload.description,
                    amount=payload.amount,
                    due_date=payload.due_date,
                    created_at=now,
                    updated_at=now,
                )
                session.add(row)
            else:
                row = session.scalar(
                    select(VariableExpenseORM).where(
                        VariableExpenseORM.id == variable_expense_id,
                        VariableExpenseORM.month_cycle_id == cycle.id,
                    )
                )
                if row is None:
                    raise ValueError("variable expense not found")
                row.description = payload.description
                row.amount = payload.amount
                row.due_date = payload.due_date
                row.updated_at = now

            session.commit()
            session.refresh(row)
            return VariableExpenseRecord(
                id=row.id,
                month_cycle_id=row.month_cycle_id,
                description=row.description,
                amount=row.amount,
                due_date=row.due_date,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )

    def list_variable_expenses(self, cycle_key: str) -> list[VariableExpenseRecord]:
        with self._session() as session:
            cycle = self._get_cycle(session, cycle_key)
            if cycle is None:
                return []
            rows = session.scalars(
                select(VariableExpenseORM)
                .where(VariableExpenseORM.month_cycle_id == cycle.id)
                .order_by(VariableExpenseORM.created_at.desc())
            ).all()
            return [
                VariableExpenseRecord(
                    id=row.id,
                    month_cycle_id=row.month_cycle_id,
                    description=row.description,
                    amount=row.amount,
                    due_date=row.due_date,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                )
                for row in rows
            ]

    def save_monthly_income(
        self,
        cycle_key: str,
        payload: MonthlyIncomeInput,
        current_date: date,
    ) -> MonthlyIncomeRecord:
        with self._session() as session:
            cycle = self._ensure_cycle(session, cycle_key)
            self._assert_unlocked(cycle, current_date)

            row = session.scalar(
                select(MonthlyIncomeORM).where(MonthlyIncomeORM.month_cycle_id == cycle.id)
            )
            now = utc_now()
            if row is None:
                row = MonthlyIncomeORM(
                    id=_id(),
                    month_cycle_id=cycle.id,
                    income_total=payload.income_total,
                    reserve_cash_outflow=payload.reserve_cash_outflow,
                    created_at=now,
                    updated_at=now,
                )
                session.add(row)
            else:
                row.income_total = payload.income_total
                row.reserve_cash_outflow = payload.reserve_cash_outflow
                row.updated_at = now

            session.commit()
            session.refresh(row)
            return MonthlyIncomeRecord(
                id=row.id,
                month_cycle_id=row.month_cycle_id,
                income_total=row.income_total,
                reserve_cash_outflow=row.reserve_cash_outflow,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )

    def get_monthly_income(self, cycle_key: str) -> MonthlyIncomeRecord | None:
        with self._session() as session:
            cycle = self._get_cycle(session, cycle_key)
            if cycle is None:
                return None
            row = session.scalar(
                select(MonthlyIncomeORM).where(MonthlyIncomeORM.month_cycle_id == cycle.id)
            )
            if row is None:
                return None
            return MonthlyIncomeRecord(
                id=row.id,
                month_cycle_id=row.month_cycle_id,
                income_total=row.income_total,
                reserve_cash_outflow=row.reserve_cash_outflow,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
