from decimal import Decimal

from comptalpes.model import Day, Guest


def test_day() -> None:
    guest = Guest(id=1, name="guest", stay=["day1"], paid={}, due={})
    day1 = Day(
        id=1, name="day1", costs={"a": Decimal(1), "b": Decimal("12.3")}, guests={guest}
    )
    day2 = Day(
        id=2, name="day2", costs={"a": Decimal(2), "b": Decimal(0)}, guests=set()
    )
    assert day1 == day1
    assert day1 != day2
    assert day1.occupancy == 1
    assert day1.cost_per_guest == {"a": Decimal(1), "b": Decimal("12.3")}
    assert day2.cost_per_guest == {}
    day2.add_guest(guest)
    assert day2.occupancy == 1
    assert day2.guests == {guest}
