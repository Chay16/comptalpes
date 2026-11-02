from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from comptalpes.model.entities import Transfer, TripMember
from comptalpes.model.enums import TransferStatus


def test_transfer(member_alice: TripMember, member_bob: TripMember) -> None:
    transfer = Transfer(
        from_member=member_alice, to_member=member_bob, amount=Decimal("50.00")
    )
    assert transfer.amount == 50
    assert transfer.paid_at is None
    assert transfer.status == TransferStatus.PROPOSED


def test_transfer_amount_is_quantized(
    member_alice: TripMember, member_bob: TripMember
) -> None:
    transfer = Transfer(
        from_member=member_alice, to_member=member_bob, amount=Decimal("10.999")
    )
    assert transfer.amount.as_tuple().exponent == -2


def test_transfer_rejects_non_positive_amount(
    member_alice: TripMember, member_bob: TripMember
) -> None:
    with pytest.raises(ValidationError):
        Transfer(from_member=member_alice, to_member=member_bob, amount=Decimal("0"))
    with pytest.raises(ValidationError):
        Transfer(from_member=member_alice, to_member=member_bob, amount=Decimal("-10"))


def test_transfer_rejects_same_members(member_alice: TripMember) -> None:
    with pytest.raises(ValidationError):
        Transfer(
            from_member=member_alice, to_member=member_alice, amount=Decimal("20.00")
        )


def test_transfer_paid_requires_paid_at(
    member_alice: TripMember, member_bob: TripMember
) -> None:
    with pytest.raises(ValidationError):
        Transfer(
            from_member=member_alice,
            to_member=member_bob,
            amount=Decimal("20.00"),
            status=TransferStatus.PAID,
        )


def test_transfer_paid_with_paid_at(
    member_alice: TripMember, member_bob: TripMember
) -> None:
    transfer = Transfer(
        from_member=member_alice,
        to_member=member_bob,
        amount=Decimal("20.00"),
        status=TransferStatus.PAID,
        paid_at=date(2026, 2, 1),
    )
    assert transfer.paid_at == date(2026, 2, 1)
