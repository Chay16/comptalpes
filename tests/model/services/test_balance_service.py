from datetime import date
from decimal import Decimal

import pytest

from comptalpes.model.entities import (
    Expense,
    ExpenseCategory,
    ExpensePayment,
    ExpenseShare,
    Transfer,
    Trip,
    TripMember,
    User,
)
from comptalpes.model.enums import TransferStatus
from comptalpes.services import BalanceCalculator

ARRIVAL = date(2026, 1, 10)
DEPARTURE = date(2026, 1, 17)


def build_member(name: str) -> TripMember:
    return TripMember(
        user=User(name=name),
        arrival_date=ARRIVAL,
        departure_date=DEPARTURE,
    )


ALICE = build_member("Alice")
BOB = build_member("Bob")


def build_trip(expenses: list[Expense], transfers: list[Transfer]) -> Trip:
    return Trip(
        name="Serre Chevalier",
        start_date=ARRIVAL,
        end_date=DEPARTURE,
        members=[ALICE, BOB],
        expenses=expenses,
        transfers=transfers,
    )


def build_expense(payments: list[ExpenseShare], shares: list[ExpenseShare]) -> Expense:
    total = sum((item.amount for item in payments), Decimal(0))
    return Expense(
        description="Fundue",
        amount=total,
        expense_date=date(2026, 1, 12),
        category=ExpenseCategory(name="Restaurant"),
        payments=payments,
        shares=shares,
    )


def test_balances_from_payment_and_shares() -> None:
    expense = build_expense(
        payments=[ExpensePayment(trip_member=ALICE, amount="100.00")],
        shares=[
            ExpenseShare(trip_member=ALICE, amount="50.00"),
            ExpenseShare(trip_member=BOB, amount="50.00"),
        ],
    )
    trip = build_trip([expense], [])
    balances = BalanceCalculator().calculate(trip)
    assert balances[ALICE.id] == Decimal("50.00")
    assert balances[BOB.id] == Decimal("-50.00")


def test_paid_transfer_adjusts_balances() -> None:
    expense = build_expense(
        payments=[ExpensePayment(trip_member=ALICE, amount="100.00")],
        shares=[
            ExpenseShare(trip_member=ALICE, amount="50.00"),
            ExpenseShare(trip_member=BOB, amount="50.00"),
        ],
    )
    transfer = Transfer(
        from_member=BOB,
        to_member=ALICE,
        amount="50.00",
        status=TransferStatus.PAID,
        paid_at=date(2026, 2, 1),
    )
    trip = build_trip([expense], [transfer])
    balances = BalanceCalculator().calculate(trip)
    assert balances[ALICE.id] == Decimal(0)
    assert balances[BOB.id] == Decimal(0)


def test_proposed_transfer_is_ignored() -> None:
    expense = build_expense(
        payments=[ExpensePayment(trip_member=ALICE, amount="100.00")],
        shares=[
            ExpenseShare(trip_member=ALICE, amount="50.00"),
            ExpenseShare(trip_member=BOB, amount="50.00"),
        ],
    )
    transfer = Transfer(
        from_member=BOB,
        to_member=ALICE,
        amount="50.00",
        status=TransferStatus.PROPOSED,
    )
    trip = build_trip([expense], [transfer])
    balances = BalanceCalculator().calculate(trip)
    assert balances[ALICE.id] == Decimal("50.00")
    assert balances[BOB.id] == Decimal("-50.00")


def test_unbalanced_totals_raise() -> None:
    expense = Expense(
        description="Fundue",
        amount="100.00",
        expense_date=date(2026, 1, 12),
        category=ExpenseCategory(name="Restaurant"),
        shares=[
            ExpenseShare(trip_member=ALICE, amount="50.00"),
            ExpenseShare(trip_member=BOB, amount="50.00"),
        ],
    )
    trip = Trip(
        name="Serre Chevalier",
        start_date=ARRIVAL,
        end_date=DEPARTURE,
        members=[ALICE, BOB],
        expenses=[expense],
    )
    with pytest.raises(ValueError, match="not balanced"):
        BalanceCalculator().calculate(trip)


def test_member_outside_trip_raises() -> None:
    outsider = build_member("Mallory")
    expense = Expense(
        description="Fundue",
        amount="100.00",
        expense_date=date(2026, 1, 12),
        category=ExpenseCategory(name="Restaurant"),
        payments=[ExpensePayment(trip_member=outsider, amount="100.00")],
        shares=[
            ExpenseShare(trip_member=ALICE, amount="50.00"),
            ExpenseShare(trip_member=BOB, amount="50.00"),
        ],
    )
    trip = Trip(
        name="Serre Chevalier",
        start_date=ARRIVAL,
        end_date=DEPARTURE,
        members=[ALICE, BOB],
        expenses=[expense],
    )
    with pytest.raises(ValueError, match="doesn't belong to the trip"):
        BalanceCalculator().calculate(trip)


def test_unbalanced_allowed_without_check() -> None:
    expense = Expense(
        description="Fundue",
        amount="100.00",
        expense_date=date(2026, 1, 12),
        category=ExpenseCategory(name="Restaurant"),
        shares=[
            ExpenseShare(trip_member=ALICE, amount="50.00"),
            ExpenseShare(trip_member=BOB, amount="50.00"),
        ],
    )
    trip = Trip(
        name="Serre Chevalier",
        start_date=ARRIVAL,
        end_date=DEPARTURE,
        members=[ALICE, BOB],
        expenses=[expense],
    )
    balances = BalanceCalculator().calculate(trip, check_balance=False)
    assert balances[ALICE.id] == Decimal("-50.00")
    assert balances[BOB.id] == Decimal("-50.00")
