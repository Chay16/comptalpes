import argparse
import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from comptalpes.model import Config, Cost, Day, Guest

CENT = Decimal("0.01")


def get_args() -> Path:
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
    if not config_path.is_file():
        raise FileNotFoundError(f"{config_path.absolute()}")
    return config_path


def load_config(
    config_path: Path,
) -> Config:
    with open(config_path, encoding="utf-8") as f:
        data = json.load(f, parse_float=Decimal)
    config = Config(**data)
    return config


def setup_occupancy(days: list[Day], guests: list[Guest]) -> None:
    for day in days:
        for guest in guests:
            if day.name in guest.stay:
                day.add_guest(guest)


def setup_costs(days: list[Day], costs: list[Cost]) -> None:
    if not days:
        return
    nb_days = Decimal(len(days))
    for cost in costs:
        daily_amount = cost.amount / nb_days
        for day in days:
            day.costs[cost.category] = daily_amount


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
