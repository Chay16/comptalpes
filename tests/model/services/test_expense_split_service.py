from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from comptalpes.model.entities import (
    Expense,
    ExpenseCategory,
    TripMember,
    User,
)
from comptalpes.model.enums import SplitType
from comptalpes.services import ExpenseSplitCalculator


def build_member(name: str, nights: int) -> TripMember:
    arrival = date(2026, 1, 10)
    return TripMember(
        user=User(name=name),
        arrival_date=arrival,
        departure_date=date(2026, 1, 10 + nights),
    )


def build_expense(
    amount: str,
    split_type: SplitType = SplitType.BY_PARTICIPANTS,
) -> Expense:
    return Expense(
        description="Fundue",
        amount=amount,
        expense_date=date(2026, 1, 12),
        category=ExpenseCategory(name="Restaurant", split_type=split_type),
    )


ALICE = build_member("Alice", 7)
BOB = build_member("Bob", 4)


def test_by_participants_equally() -> None:
    expense = build_expense("100.00")
    shares = ExpenseSplitCalculator().calculate(expense, [ALICE, BOB])
    assert [share.amount for share in shares] == [
        Decimal("50.00"),
        Decimal("50.00"),
    ]


def test_by_participants_reminder_to_last() -> None:
    carol = build_member("Carol", 7)
    expense = build_expense("100.00")
    shares = ExpenseSplitCalculator().calculate(expense, [ALICE, BOB, carol])
    assert sum((share.amount for share in shares), Decimal(0)) == Decimal("100.00")
    assert shares[-1].amount == Decimal("33.34")


def test_equally() -> None:
    expense = build_expense("100.00", split_type=SplitType.EQUALLY)
    shares = ExpenseSplitCalculator().calculate(expense, [ALICE, BOB])
    assert [share.amount for share in shares] == [
        Decimal("50.00"),
        Decimal("50.00"),
    ]


def test_by_nights_weighted() -> None:
    expense = build_expense("110.00", split_type=SplitType.BY_NIGHTS)
    shares = ExpenseSplitCalculator().calculate(expense, [ALICE, BOB])
    assert [share.quantity for share in shares] == [
        Decimal(7),
        Decimal(4),
    ]
    assert [share.amount for share in shares] == [
        Decimal("70.00"),
        Decimal("40.00"),
    ]


def test_by_percentage() -> None:
    expense = build_expense("200.00", split_type=SplitType.BY_PERCENTAGE)
    quantities = {ALICE.id: Decimal("70"), BOB.id: Decimal("30")}
    shares = ExpenseSplitCalculator().calculate(expense, [ALICE, BOB], quantities)
    assert [share.amount for share in shares] == [
        Decimal("140.00"),
        Decimal("60.00"),
    ]


def test_by_percentage_requires_quantities() -> None:
    expense = build_expense("200.00", split_type=SplitType.BY_PERCENTAGE)
    with pytest.raises(ValueError, match="Quantities are required"):
        ExpenseSplitCalculator().calculate(expense, [ALICE, BOB])


def test_by_percentage_missing_member_quantity() -> None:
    expense = build_expense("200.00", split_type=SplitType.BY_PERCENTAGE)
    quantities = {ALICE.id: Decimal("100")}
    with pytest.raises(ValueError, match="Missing quantity"):
        ExpenseSplitCalculator().calculate(expense, [ALICE, BOB], quantities)


def test_by_percentage_total_must_be_100() -> None:
    expense = build_expense("200.00", split_type=SplitType.BY_PERCENTAGE)
    quantities = {ALICE.id: Decimal("60"), BOB.id: Decimal("30")}
    with pytest.raises(ValueError, match="add up to 100"):
        ExpenseSplitCalculator().calculate(expense, [ALICE, BOB], quantities)


def test_by_percentage_negative_quantity() -> None:
    expense = build_expense("200.00", split_type=SplitType.BY_PERCENTAGE)
    quantities = {ALICE.id: Decimal("-20"), BOB.id: Decimal("120")}
    with pytest.raises(ValidationError):
        ExpenseSplitCalculator().calculate(expense, [ALICE, BOB], quantities)


def test_quantities_rejected_for_other_split_type() -> None:
    expense = build_expense("100.00")
    quantities = {ALICE.id: Decimal("50"), BOB.id: Decimal("50")}
    with pytest.raises(ValueError, match="only supported for BY_PERCENTAGE"):
        ExpenseSplitCalculator().calculate(expense, [ALICE, BOB], quantities)


def test_no_participants() -> None:
    expense = build_expense("100.00")
    with pytest.raises(ValueError, match="No participants selected"):
        ExpenseSplitCalculator().calculate(expense, [])


def test_expense_amount_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        build_expense("0")
