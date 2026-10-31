import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from comptalpes.model import Day, Guest

CENT = Decimal("0.01")


def load_config(
    config_path: Path,
) -> tuple[list[Day], dict[str, Decimal], dict[str, Guest]]:
    with open(config_path, encoding="utf-8") as f:
        data = json.load(f, parse_float=Decimal)

    guests: dict[str, Guest] = {}
    for i, g in enumerate(data["guests"]):
        paid_decimal = {k: Decimal(str(v)) for k, v in g.get("paid", {}).items()}
        guests[g["name"]] = Guest(
            name=g["name"],
            id=i,
            stay=g.get("stay", []),
            paid=paid_decimal,
        )

    days: list[Day] = [Day(id=i, name=d) for i, d in enumerate(data["days"])]
    prices: dict[str, Decimal] = {
        category: Decimal(str(amount)) for category, amount in data["prices"].items()
    }

    valid_day_names = {d.name for d in days}
    for guest in guests.values():
        invalid_days = set(guest.stay) - valid_day_names
        if invalid_days:
            raise ValueError(f"Day(s) unknown for {guest.name} : {invalid_days}")

    total_prices = sum(prices.values(), Decimal(0))
    total_paid = sum((g.total_paid for g in guests.values()), Decimal(0))
    gap = total_paid - total_prices

    if gap != Decimal(0):
        msg = (
            f"Gap Detected : Total Due = {total_prices:.2f} €, "
            f"Total Paid = {total_paid:.2f} € (gap of {gap:+.2f} €)."
        )
        raise ValueError(msg)

    setup_occupancy(days, list(guests.values()))
    setup_costs(days, prices)

    return days, prices, guests


def setup_occupancy(days: list[Day], guests: list[Guest]) -> None:
    for day in days:
        for guest in guests:
            if day.name in guest.stay:
                day.add_guest(guest)


def setup_costs(days: list[Day], costs: dict[str, Decimal]) -> None:
    if not days:
        return
    nb_days = Decimal(len(days))
    for category, price in costs.items():
        daily_amount = price / nb_days
        for day in days:
            day.costs[category] = daily_amount


def setup_personal_costs(guest: Guest, days: list[Day]) -> None:
    guest.reset_due()
    for day in days:
        if guest in day.guests:
            for category, share in day.cost_per_guest.items():
                guest.add_due(category, share)


def quantize_balances(guests: list[Guest]) -> dict[str, Decimal]:
    raw_balances = {g.name: g.balance for g in guests}

    quantized = {
        name: b.quantize(CENT, rounding=ROUND_HALF_UP)
        for name, b in raw_balances.items()
    }

    discrepancy = sum(quantized.values(), Decimal(0))
    if discrepancy != Decimal(0):
        cents_to_adjust = int(abs(discrepancy / CENT))
        step = -CENT if discrepancy > Decimal(0) else CENT

        sorted_names = sorted(
            raw_balances.keys(),
            key=lambda name: raw_balances[name] - quantized[name],
            reverse=(step > Decimal(0)),
        )

        for i in range(min(cents_to_adjust, len(sorted_names))):
            quantized[sorted_names[i]] += step

    return quantized


def format_transfers_tables(transfers: list[tuple[str, str, Decimal]]) -> str:
    headers = ["From", "To", "Amount (€)"]
    lignes = [(source, dest, f"{montant:.2f}") for source, dest, montant in transfers]

    col_widths = [
        max(len(str(ligne[i])) for ligne in [headers] + lignes)
        for i in range(len(headers))
    ]

    bordure = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    ligne_entete = (
        "| "
        + " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths, strict=True))
        + " |"
    )

    tableau = [bordure, ligne_entete, bordure]
    for source, dest, montant in lignes:
        tableau.append(
            f"| {source:<{col_widths[0]}} "
            f"| {dest:<{col_widths[1]}} "
            f"| {montant:>{col_widths[2]}} |"
        )
    tableau.append(bordure)
    return "\n".join(tableau)
