from decimal import Decimal
from pathlib import Path

from comptalpes import utils
from comptalpes.model import Day, Guest


def test_load_config() -> None:
    config_path = Path(__file__).parent / "config-test.json"
    days, prices, guests = utils.load_config(config_path)

    expected_prices = {"house": Decimal("1234.56"), "food": Decimal("78.90")}
    expected_guestA = Guest(
        name="A",
        id=0,
        stay=["1", "2"],
        paid={"house": Decimal("1034.56")},
    )
    expected_guestB = Guest(
        name="B",
        id=1,
        stay=["1"],
        paid={},
    )
    expected_guestC = Guest(
        name="C",
        id=2,
        stay=["1", "2"],
        paid={"house": Decimal("200"), "food": Decimal("78.90")},
    )

    expected_Day1 = Day(
        id=0,
        name="1",
        costs={"house": Decimal("617.28"), "food": Decimal("39.45")},
        guests={expected_guestA, expected_guestB, expected_guestC},
    )
    expected_Day2 = Day(
        id=1,
        name="2",
        costs={"house": Decimal("617.28"), "food": Decimal("39.45")},
        guests={expected_guestA, expected_guestC},
    )
    expected_guests = {"A": expected_guestA, "B": expected_guestB, "C": expected_guestC}
    expected_days = [expected_Day1, expected_Day2]
    assert prices == expected_prices
    assert days == expected_days
    assert guests == expected_guests


def test_setup_occupancy() -> None:
    days = [Day(id=0, name="1"), Day(id=1, name="2")]
    guests = [
        Guest(name="a", id=1, stay=["1"]),
        Guest(name="b", id=2, stay=["1", "2"]),
        Guest(name="c", id=3, stay=["2"]),
    ]

    utils.setup_occupancy(days, guests)
    assert days[0].guests == {guests[0], guests[1]}
    assert days[1].guests == {guests[1], guests[2]}


def test_setup_costs() -> None:
    days = [Day(id=0, name="1"), Day(id=1, name="2")]
    costs = {"house": Decimal("100"), "food": Decimal("44.90")}
    utils.setup_costs(days, costs)
    expected_costs_per_day = {"house": Decimal("50"), "food": Decimal("22.45")}
    assert all(d.costs == expected_costs_per_day for d in days)


def test_setup_personal_costs() -> None:
    costs = {"a": Decimal("100")}
    guestA = Guest(name="a", id=1, stay=["1"], paid={"a": Decimal("100")})
    guestB = Guest(name="b", id=2, stay=["1", "2"])
    guestC = Guest(name="c", id=3, stay=["2"])

    days = [
        Day(id=0, name="1", guests={guestA, guestB}),
        Day(id=1, name="2", guests={guestB, guestC}),
    ]
    utils.setup_costs(days, costs)
    utils.setup_personal_costs(guestA, days)
    utils.setup_personal_costs(guestB, days)
    utils.setup_personal_costs(guestC, days)
    assert guestA.due == {"a": Decimal("25")}
    assert guestB.due == {"a": Decimal("50")}
    assert guestC.due == {"a": Decimal("25")}


def test_quantize_balances_zero_discrepancy():
    guestA = Guest(name="a", id=1, paid={"a": Decimal("10.50")})
    guestB = Guest(name="b", id=2, due={"a": Decimal("10.50")})

    result = utils.quantize_balances([guestA, guestB])

    assert result == {"a": Decimal("10.50"), "b": Decimal("-10.50")}
    assert sum(result.values(), Decimal(0)) == Decimal("0.00")


def test_quantize_balances_positive_discrepancy():
    guestA = Guest(name="a", id=1, paid={"a": Decimal("10.335")})
    guestB = Guest(name="b", id=2, paid={"a": Decimal("10.335")})
    guestC = Guest(name="c", id=3, due={"a": Decimal("20.670")})

    result = utils.quantize_balances([guestA, guestB, guestC])

    assert sum(result.values(), Decimal(0)) == Decimal("0.00")
    assert result["c"] == Decimal("-20.67")
    assert result["a"] + result["b"] == Decimal("20.67")


def test_quantize_balances_negative_discrepancy():
    guestA = Guest(name="a", id=1, due={"a": Decimal("10.335")})
    guestB = Guest(name="b", id=2, due={"a": Decimal("10.335")})
    guestC = Guest(name="c", id=3, paid={"a": Decimal("20.670")})

    result = utils.quantize_balances([guestA, guestB, guestC])

    assert sum(result.values(), Decimal(0)) == Decimal("0.00")
    assert result["c"] == Decimal("20.67")
    assert result["a"] + result["b"] == Decimal("-20.67")


def test_quantize_balances_empty_list():
    guests = []
    result = utils.quantize_balances(guests)
    assert result == {}


def test_format_transfers_tables_standard():
    transfers = [("A", "B", Decimal("10.50")), ("C", "DDDDDDDDDDD", Decimal("123.45"))]

    result = utils.format_transfers_tables(transfers)
    lines = result.split("\n")

    assert len(lines) == 6

    assert lines[0].startswith("+")
    assert lines[0].endswith("+")
    assert lines[2] == lines[0]
    assert lines[5] == lines[0]

    assert "From" in lines[1]
    assert "To" in lines[1]
    assert "Amount (€)" in lines[1]

    assert "A" in lines[3]
    assert "B" in lines[3]
    assert "10.50" in lines[3]

    assert "C" in lines[4]
    assert "DDDDDDDDDDD" in lines[4]
    assert "123.45" in lines[4]


def test_format_transfers_tables_rounding():
    transfers = [("A", "B", Decimal("10.567"))]

    result = utils.format_transfers_tables(transfers)
    assert "10.57" in result


def test_format_transfers_tables_empty():
    result = utils.format_transfers_tables([])
    lines = result.split("\n")

    assert len(lines) == 4
    assert "From" in lines[1]
    assert "To" in lines[1]
    assert "Amount (€)" in lines[1]
