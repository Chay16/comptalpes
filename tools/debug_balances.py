import argparse
import json
from decimal import Decimal
from pathlib import Path

from comptalpes.model.entities import (
    Expense,
    ExpenseCategory,
    ExpensePayment,
    Transfer,
    Trip,
    TripMember,
    User,
)
from comptalpes.model.enums import SplitType
from comptalpes.services import (
    BalanceCalculator,
    ExpenseSplitCalculator,
    TransfersCalculator,
)


def get_args() -> Path:
    parser = argparse.ArgumentParser(
        description="Debug balances and transfers",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--data",
        type=str,
        required=False,
        default=Path(__file__).parent / "debug_data.json",
        help="Path to debug data file JSON",
    )
    args = parser.parse_args()
    data_path = Path(args.data)
    if not data_path.is_file():
        raise FileNotFoundError(f"{data_path.absolute()}")
    return data_path


def build_trip(data: dict) -> Trip:
    members = [
        TripMember(
            user=User(name=member["name"]),
            arrival_date=member["arrival_date"],
            departure_date=member["departure_date"],
        )
        for member in data["members"]
    ]
    return Trip(
        name=data["trip"]["name"],
        start_date=data["trip"]["start_date"],
        end_date=data["trip"]["end_date"],
        members=members,
    )


def build_expenses(data: dict, trip: Trip) -> list[Expense]:
    by_name = {member.user.name: member for member in trip.members}
    calculator = ExpenseSplitCalculator()

    def compute_shares(expense: Expense) -> None:
        present = [
            member
            for member in trip.members
            if member.arrival_date <= expense.expense_date < member.departure_date
        ]
        expense.shares = calculator.calculate(expense, present or trip.members)

    expenses = []
    for item in data["expenses"]:
        category_fields = {"name": item["category"]}
        if "split_type" in item:
            category_fields["split_type"] = SplitType(item["split_type"])
        expense = Expense(
            description=item["description"],
            amount=item["amount"],
            expense_date=item["expense_date"],
            category=ExpenseCategory(**category_fields),
        )
        compute_shares(expense)
        expenses.append(expense)

    for item in data["members"]:
        expenses.extend(
            Expense(
                description=advance["description"],
                amount=advance["amount"],
                expense_date=advance["expense_date"],
                category=ExpenseCategory(name=advance["category"]),
                payments=[
                    ExpensePayment(
                        trip_member=by_name[item["name"]],
                        amount=advance["amount"],
                    )
                ],
            )
            for advance in item.get("paid", [])
        )
    return expenses


def format_transfers_table(transfers: list[Transfer]) -> str:
    headers = ["From", "To", "Amount (€)"]
    rows = [
        (t.from_member.user.name, t.to_member.user.name, f"{t.amount:.2f}")
        for t in transfers
    ]

    col_widths = [
        max(len(str(row[i])) for row in [headers] + rows) for i in range(len(headers))
    ]

    border = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_line = (
        "| "
        + " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths, strict=True))
        + " |"
    )

    table = [border, header_line, border]
    for debit, credit, amount in rows:
        table.append(
            f"| {debit:<{col_widths[0]}} "
            f"| {credit:<{col_widths[1]}} "
            f"| {amount:>{col_widths[2]}} |"
        )
    table.append(border)
    return "\n".join(table)


def main() -> None:
    data_path = get_args()
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f, parse_float=Decimal)

    trip = build_trip(data)
    trip.expenses = build_expenses(data, trip)

    balances = BalanceCalculator().calculate(trip)
    transfers = TransfersCalculator().calculate(balances, trip.members)

    print(format_transfers_table(transfers))
    print(f"Total Transfers : {sum((t.amount for t in transfers), Decimal(0)):.2f} €")


if __name__ == "__main__":
    main()
