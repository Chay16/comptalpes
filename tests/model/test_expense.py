from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from comptalpes.model.entities import (
    Expense,
    ExpenseCategory,
    ExpensePayment,
    ExpenseShare,
    TripMember,
    User,
)
from comptalpes.model.enums import SplitType


def build_member(name: str) -> TripMember:
    return TripMember(
        user=User(name=name),
        arrival_date=date(2026, 1, 10),
        departure_date=date(2026, 1, 17),
    )


ALICE = build_member("Alice")
BOB = build_member("Bob")


def build_expense(
    amount: str = "100.00",
    payments: list[ExpensePayment] | None = None,
    shares: list[ExpenseShare] | None = None,
    category: ExpenseCategory | None = None,
    split_type_override: SplitType | None = None,
) -> Expense:
    return Expense(
        description="Fundue",
        amount=amount,
        expense_date=date(2026, 1, 12),
        category=category or ExpenseCategory(name="Restaurant"),
        split_type_override=split_type_override,
        payments=payments or [],
        shares=shares or [],
    )


def test_expense() -> None:
    expense = build_expense()
    assert expense.description == "Fundue"
    assert expense.amount == Decimal("100.00")
    assert expense.expense_date == date(2026, 1, 12)
    assert expense.payments == []
    assert expense.shares == []


def test_expense_amount_is_quantized() -> None:
    expense = build_expense(amount="99.999")
    assert expense.amount == Decimal("100.00")
    assert expense.amount.as_tuple().exponent == -2


def test_expense_rejects_non_positive_amount() -> None:
    with pytest.raises(ValidationError):
        build_expense(amount="0")
    with pytest.raises(ValidationError):
        build_expense(amount="-50")


def test_expense_split_type_from_category() -> None:
    category = ExpenseCategory(name="Chalet", split_type=SplitType.BY_NIGHTS)
    expense = build_expense(category=category)
    assert expense.split_type == SplitType.BY_NIGHTS


def test_expense_split_type_default() -> None:
    expense = build_expense()
    assert expense.split_type == SplitType.BY_PARTICIPANTS


def test_expense_split_type_override() -> None:
    category = ExpenseCategory(name="Chalet", split_type=SplitType.BY_NIGHTS)
    expense = build_expense(
        category=category, split_type_override=SplitType.BY_PERCENTAGE
    )
    assert expense.split_type == SplitType.BY_PERCENTAGE


def test_expense_payment() -> None:
    payment = ExpensePayment(trip_member=ALICE, amount="60.00")
    assert payment.amount == Decimal("60.00")


def test_expense_payments_total_must_match_amount() -> None:
    payments = [ExpensePayment(trip_member=ALICE, amount="60.00")]
    with pytest.raises(ValidationError):
        build_expense(amount="100.00", payments=payments)


def test_expense_payments_valid() -> None:
    payments = [
        ExpensePayment(trip_member=ALICE, amount="60.00"),
        ExpensePayment(trip_member=BOB, amount="40.00"),
    ]
    expense = build_expense(amount="100.00", payments=payments)
    assert len(expense.payments) == 2


def test_expense_share() -> None:
    share = ExpenseShare(trip_member=ALICE, amount="50.00")
    assert share.amount == Decimal("50.00")
    assert share.quantity == Decimal("0")


def test_expense_shares_total_must_match_amount() -> None:
    shares = [ExpenseShare(trip_member=ALICE, amount="50.00")]
    with pytest.raises(ValidationError):
        build_expense(amount="100.00", shares=shares)


def test_expense_shares_valid() -> None:
    shares = [
        ExpenseShare(trip_member=ALICE, amount="50.00"),
        ExpenseShare(trip_member=BOB, amount="50.00"),
    ]
    expense = build_expense(amount="100.00", shares=shares)
    assert len(expense.shares) == 2


def test_expense_rejects_non_positive_payment_amount() -> None:
    with pytest.raises(ValidationError):
        ExpensePayment(trip_member=ALICE, amount="0")


def test_expense_allows_zero_share_amount() -> None:
    shares = [
        ExpenseShare(trip_member=ALICE, amount="0.00"),
        ExpenseShare(trip_member=BOB, amount="100.00"),
    ]
    expense = build_expense(amount="100.00", shares=shares)
    assert expense.shares[0].amount == Decimal("0.00")
