import argparse
import json
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from comptalpes.model.entities import (
    Expense,
    ExpenseCategory,
    ExpenseShare,
    Transfer,
    Trip,
    TripMember,
    User,
)
from comptalpes.model.enums import SplitType, TransferStatus

CENT = Decimal("0.01")


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


def build_expenses(data: dict) -> list[Expense]:
    expenses = []
    for item in data["expenses"]:
        category_fields = {"name": item["category"]}
        if "split_type" in item:
            category_fields["split_type"] = SplitType(item["split_type"])
        expenses.append(
            Expense(
                description=item["description"],
                amount=item["amount"],
                expense_date=item["expense_date"],
                category=ExpenseCategory(**category_fields),
            )
        )
    return expenses


def participants(expense: Expense, trip: Trip) -> list[TripMember]:
    present = [
        member
        for member in trip.members
        if member.arrival_date <= expense.expense_date < member.departure_date
    ]
    return present or trip.members


def weights(expense: Expense, trip: Trip) -> list[tuple[TripMember, Decimal]]:
    participants_of_expense = participants(expense, trip)
    if expense.split_type == SplitType.BY_NIGHTS:
        return [(member, Decimal(member.nights)) for member in participants_of_expense]
    return [(member, Decimal(1)) for member in participants_of_expense]


def compute_shares(expense: Expense, trip: Trip) -> None:
    member_weights = weights(expense, trip)
    total_weight = sum((weight for _, weight in member_weights), Decimal(0))

    exacts: list[tuple[TripMember, Decimal, Decimal]] = []
    floor_total = Decimal(0)
    for member, weight in member_weights:
        exact = expense.amount * weight / total_weight
        floor = exact.quantize(CENT, rounding=ROUND_HALF_UP)
        exacts.append((member, floor, exact - floor))
        floor_total += floor

    remaining = int((expense.amount - floor_total) / CENT)
    order = sorted(range(len(exacts)), key=lambda i: exacts[i][2], reverse=True)
    amounts = [floor for _, floor, _ in exacts]
    for index in order[: max(remaining, 0)]:
        amounts[index] += CENT

    expense.shares = [
        ExpenseShare(trip_member=member, amount=amounts[index])
        for index, (member, _, _) in enumerate(exacts)
    ]


def paid_by_member(data: dict, trip: Trip) -> dict[str, Decimal]:
    paid: dict[str, Decimal] = {member.user.name: Decimal(0) for member in trip.members}
    for item in data["members"]:
        for advance in item.get("paid", []):
            paid[item["name"]] += Decimal(advance["amount"])
    return paid


def compute_balances(
    trip: Trip, expenses: list[Expense], paid: dict[str, Decimal]
) -> dict[str, Decimal]:
    total_paid = sum(paid.values(), Decimal(0))
    total_expenses = sum((expense.amount for expense in expenses), Decimal(0))
    gap = total_paid - total_expenses
    if gap != Decimal(0):
        msg = (
            f"Gap Detected : Total Expenses = {total_expenses:.2f} €, "
            f"Total Paid = {total_paid:.2f} € (gap of {gap:+.2f} €)."
        )
        raise ValueError(msg)

    balances = {}
    for member in trip.members:
        due = sum(
            (
                share.amount
                for expense in expenses
                for share in expense.shares
                if share.trip_member.id == member.id
            ),
            Decimal(0),
        )
        balances[member.user.name] = paid[member.user.name] - due
    return balances


def solver(balances: dict[str, Decimal], trip: Trip) -> list[Transfer]:
    by_name = {member.user.name: member for member in trip.members}
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
    transfers: list[Transfer] = []

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
        transfers.append(
            Transfer(
                from_member=by_name[debtor],
                to_member=by_name[creditor],
                amount=transfer_value,
                status=TransferStatus.PROPOSED,
            )
        )

        if working_balances[debtor] == Decimal(0):
            i += 1
        if working_balances[creditor] == Decimal(0):
            j += 1

    return transfers


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
    expenses = build_expenses(data)

    for expense in expenses:
        compute_shares(expense, trip)

    paid = paid_by_member(data, trip)
    balances = compute_balances(trip, expenses, paid)
    transfers = solver(balances, trip)

    print(format_transfers_table(transfers))
    print(f"Total Transfers : {sum((t.amount for t in transfers), Decimal(0)):.2f} €")


if __name__ == "__main__":
    main()
