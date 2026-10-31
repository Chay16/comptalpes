from decimal import Decimal

from comptalpes.model import Cost


def test_create_cost() -> None:
    cost = Cost(category="house", amount=Decimal("123.45"))
    assert cost.category == "house"
    assert cost.amount == Decimal("123.45")
    cost2 = Cost(category="food", amount=Decimal("67.89"))
    assert cost != cost2
    assert cost == cost
