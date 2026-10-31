from decimal import Decimal

from comptalpes.main import solver


def test_solver() -> None:
    balances = {
        "creditor": Decimal("100.23"),
        "debtor1": Decimal("-33.41"),
        "debtor2": Decimal("-33.41"),
    }
    transfers = solver(balances)
    assert transfers == [
        ("debtor1", "creditor", Decimal("33.41")),
        ("debtor2", "creditor", Decimal("33.41")),
    ]
