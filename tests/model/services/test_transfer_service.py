from datetime import date
from decimal import Decimal

import pytest

from comptalpes.model.entities import TripMember, User
from comptalpes.model.enums import TransferStatus
from comptalpes.services import TransfersCalculator


def build_member(name: str) -> TripMember:
    return TripMember(
        user=User(name=name),
        arrival_date=date(2026, 1, 10),
        departure_date=date(2026, 1, 17),
    )


ALICE = build_member("Alice")
BOB = build_member("Bob")
CAROL = build_member("Carol")


def test_simple_settlement() -> None:
    balances = {ALICE.id: Decimal("50.00"), BOB.id: Decimal("-50.00")}
    transfers = TransfersCalculator().calculate(balances, [ALICE, BOB])
    assert len(transfers) == 1
    assert transfers[0].from_member.id == BOB.id
    assert transfers[0].to_member.id == ALICE.id
    assert transfers[0].amount == Decimal("50.00")
    assert transfers[0].status == TransferStatus.PROPOSED


def test_one_debtor_several_creditors() -> None:
    balances = {
        ALICE.id: Decimal("30.00"),
        BOB.id: Decimal("20.00"),
        CAROL.id: Decimal("-50.00"),
    }
    transfers = TransfersCalculator().calculate(balances, [ALICE, BOB, CAROL])
    assert len(transfers) == 2
    assert all(t.from_member.id == CAROL.id for t in transfers)
    assert sum((t.amount for t in transfers), Decimal(0)) == Decimal("50.00")


def test_zero_balances_no_transfers() -> None:
    balances = {ALICE.id: Decimal(0), BOB.id: Decimal(0)}
    assert TransfersCalculator().calculate(balances, [ALICE, BOB]) == []


def test_empty_balances() -> None:
    assert TransfersCalculator().calculate({}, []) == []


def test_unbalanced_credit_and_debt_raises() -> None:
    balances = {ALICE.id: Decimal("50.00"), BOB.id: Decimal("-40.00")}
    with pytest.raises(ValueError, match="must equal total credit"):
        TransfersCalculator().calculate(balances, [ALICE, BOB])


def test_unknown_member_raises() -> None:
    outsider = build_member("Mallory")
    balances = {outsider.id: Decimal("50.00"), BOB.id: Decimal("-50.00")}
    with pytest.raises(ValueError, match="Unknown participant"):
        TransfersCalculator().calculate(balances, [ALICE, BOB])


def test_unbalanced_allowed_without_check() -> None:
    balances = {ALICE.id: Decimal("50.00"), BOB.id: Decimal("-40.00")}
    transfers = TransfersCalculator().calculate(
        balances, [ALICE, BOB], check_balance=False
    )
    assert len(transfers) == 1
    assert transfers[0].amount == Decimal("40.00")
