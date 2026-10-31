from decimal import Decimal

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
    config_path = utils.get_args()
    config = utils.load_config(config_path)
    days = utils.generate_days_from_stay(config.stay)

    valid_day_names = {d.name for d in days}
    for guest in config.guests:
        invalid_days = set(guest.stay) - valid_day_names
        if invalid_days:
            raise ValueError(f"Day(s) unknown for {guest.name} : {invalid_days}")

    total_costs = sum([c.amount for c in config.costs], Decimal(0))
    total_paid = sum([g.total_paid for g in config.guests], Decimal(0))
    gap = total_paid - total_costs

    if gap != Decimal(0):
        msg = (
            f"Gap Detected : Total Costs = {total_costs:.2f} €, "
            f"Total Paid = {total_paid:.2f} € (gap of {gap:+.2f} €)."
        )
        raise ValueError(msg)

    utils.setup_occupancy(days, config.guests)
    utils.setup_costs(days, config.costs)
    for guest in config.guests:
        utils.setup_personal_costs(guest, days)

    quantized_balances = utils.quantize_balances(config.guests)
    transfers = solver(quantized_balances)

    print(utils.format_transfers_tables(transfers))
    print(f"Total Transfers : {sum((t[2] for t in transfers), Decimal(0)):.2f} €")


if __name__ == "__main__":
    main()
