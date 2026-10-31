from decimal import Decimal

from comptalpes.model import Guest


def test_guest() -> None:
    guest = Guest(name="guest", stay=["day1"], paid={}, due={})
    guest2 = Guest(name="guest", stay=["day1"], paid={"cat1": Decimal("31")}, due={})
    assert guest == guest
    assert guest != guest2
    assert guest.total_due == 0
    guest.add_due("cat1", Decimal("10"))
    assert guest.due == {"cat1": 10}
    assert guest.total_due == 10
    guest.add_due("cat1", Decimal("20"))
    guest.add_due("cat2", Decimal("1"))
    assert guest.due == {"cat1": 30, "cat2": 1}
    assert guest.total_due == 31
    assert guest.balance == -31
    guest.reset_due()
    assert guest.total_due == 0
    assert guest.total_paid == 0
    assert guest2.total_paid == 31
