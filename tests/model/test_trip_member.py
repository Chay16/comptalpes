from datetime import date

import pytest
from pydantic import ValidationError

from comptalpes.model.entities import TripMember, User


def build_member(arrival: date, departure: date) -> TripMember:
    return TripMember(
        user=User(name="Alice"), arrival_date=arrival, departure_date=departure
    )


def test_trip_member() -> None:
    member = build_member(date(2026, 1, 10), date(2026, 1, 17))
    assert member.user.name == "Alice"
    assert member.arrival_date == date(2026, 1, 10)
    assert member.departure_date == date(2026, 1, 17)


def test_trip_member_nights() -> None:
    member = build_member(date(2026, 1, 10), date(2026, 1, 17))
    assert member.nights == 7


def test_trip_member_single_night() -> None:
    member = build_member(date(2026, 1, 10), date(2026, 1, 11))
    assert member.nights == 1


def test_trip_member_arrival_after_departure() -> None:
    with pytest.raises(ValidationError):
        build_member(date(2026, 1, 17), date(2026, 1, 10))


def test_trip_member_arrival_equals_departure() -> None:
    with pytest.raises(ValidationError):
        build_member(date(2026, 1, 10), date(2026, 1, 10))
