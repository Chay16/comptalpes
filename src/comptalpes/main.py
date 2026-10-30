import argparse
from decimal import Decimal
from pathlib import Path

from comptalpes import utils


def solver(balances: dict[str, Decimal]) -> list[tuple[str, str, Decimal]]:
    working_balances = dict(balances)

    creditors = sorted(
        [name for name, b in working_balances.items() if b > Decimal(0)],
        key=lambda name: working_balances[name],
        reverse=True,
    )
    debtors = sorted(
        [name for name, b in working_balances.items() if b < Decimal(0)],
        key=lambda name: working_balances[name],
    )

    i = 0
    j = 0
    transfers: list[tuple[str, str, Decimal]] = []

    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]

        debt = working_balances[debtor]
        credit = working_balances[creditor]

        if debt >= Decimal(0):
            i += 1
            continue
        if credit <= Decimal(0):
            j += 1
            continue

        transfer_value = min(-debt, credit)
        working_balances[debtor] += transfer_value
        working_balances[creditor] -= transfer_value
        transfers.append((debtor, creditor, transfer_value))

        if working_balances[debtor] == Decimal(0):
            i += 1
        if working_balances[creditor] == Decimal(0):
            j += 1

    return transfers


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Comptalpes", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--config",
        type=str,
        required=False,
        default=Path(__file__).parent.parent.parent / "data/config.json",
        help="Path to configuration file JSON",
    )
    args = parser.parse_args()

    config_path = Path(args.config)

    days, _, guests = utils.load_config(config_path)

    for guest in guests.values():
        utils.setup_personal_costs(guest, days)

    quantized_balances = utils.quantize_balances(list(guests.values()))
    transfers = solver(quantized_balances)

    print(utils.format_transfers_tables(transfers))
    print(f"Total Transfers : {sum((t[2] for t in transfers), Decimal(0)):.2f} €")


if __name__ == "__main__":
    main()