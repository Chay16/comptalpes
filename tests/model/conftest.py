from datetime import date

import pytest

from comptalpes.model.entities import TripMember, User


@pytest.fixture
def alice() -> User:
    return User(name="Alice")


@pytest.fixture
def bob() -> User:
    return User(name="Bob")


@pytest.fixture
def member_alice(alice: User) -> TripMember:
    return TripMember(
        user=alice, arrival_date=date(2026, 1, 10), departure_date=date(2026, 1, 17)
    )


@pytest.fixture
def member_bob(bob: User) -> TripMember:
    return TripMember(
        user=bob, arrival_date=date(2026, 1, 10), departure_date=date(2026, 1, 17)
    )
