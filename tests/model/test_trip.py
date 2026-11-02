from datetime import date

import pytest
from pydantic import ValidationError

from comptalpes.model.entities import Trip, TripMember, User


def build_member(name: str, arrival: date, departure: date) -> TripMember:
    return TripMember(
        user=User(name=name), arrival_date=arrival, departure_date=departure
    )


def build_trip(
    start: date = date(2026, 1, 10),
    end: date = date(2026, 1, 17),
    members: list[TripMember] | None = None,
) -> Trip:
    return Trip(
        name="Valloire", start_date=start, end_date=end, members=members or []
    )


def test_trip() -> None:
    trip = build_trip()
    assert trip.name == "Valloire"
    assert trip.start_date == date(2026, 1, 10)
    assert trip.end_date == date(2026, 1, 17)
    assert trip.members == []
    assert trip.expenses == []
    assert trip.transfers == []


def test_trip_default_currency() -> None:
    assert build_trip().currency == "EUR"


def test_trip_explicit_currency() -> None:
    trip = Trip(
        name="Genève",
        start_date=date(2026, 1, 10),
        end_date=date(2026, 1, 17),
        currency="CHF",
    )
    assert trip.currency == "CHF"


def test_trip_start_after_end() -> None:
    with pytest.raises(ValidationError):
        build_trip(start=date(2026, 1, 17), end=date(2026, 1, 10))


def test_trip_start_equals_end() -> None:
    with pytest.raises(ValidationError):
        build_trip(start=date(2026, 1, 10), end=date(2026, 1, 10))


def test_trip_member_within_trip_dates() -> None:
    member = build_member("Alice", date(2026, 1, 11), date(2026, 1, 15))
    trip = build_trip(members=[member])
    assert trip.members == [member]


def test_trip_member_boundaries() -> None:
    member = build_member("Alice", date(2026, 1, 10), date(2026, 1, 17))
    trip = build_trip(members=[member])
    assert trip.members == [member]


def test_trip_member_arrives_before_trip() -> None:
    member = build_member("Alice", date(2026, 1, 9), date(2026, 1, 15))
    with pytest.raises(ValidationError):
        build_trip(members=[member])


def test_trip_member_leaves_after_trip() -> None:
    member = build_member("Alice", date(2026, 1, 11), date(2026, 1, 18))
    with pytest.raises(ValidationError):
        build_trip(members=[member])


def test_trip_member_leaves_same_day_as_trip_end() -> None:
    member = build_member("Alice", date(2026, 1, 15), date(2026, 1, 17))
    trip = build_trip(members=[member])
    assert trip.members == [member]
