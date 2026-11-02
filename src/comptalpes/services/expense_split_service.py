from decimal import ROUND_DOWN, Decimal
from typing import Iterable
from uuid import UUID

from comptalpes.model.entities.expense import Expense, ExpenseShare
from comptalpes.model.entities.trip_member import TripMember
from comptalpes.model.enums.split_type import SplitType

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


class ExpenseSplitCalculator:
    def calculate(
        self,
        expense: Expense,
        participants: Iterable[TripMember],
        quantities: dict[UUID, Decimal] | None = None,
    ) -> list[ExpenseShare]:

        participants = list(participants)

        if not participants:
            raise ValueError("No participants selected")

        if expense.amount <= ZERO:
            raise ValueError("Expense amount must be positive")

        if expense.split_type == SplitType.BY_PERCENTAGE:
            shares = self._percentage_shares(expense, participants, quantities)
            self._validate_percentages(shares)
        else:
            if quantities is not None:
                raise ValueError(
                    "Quantities are only supported for BY_PERCENTAGE split type"
                )
            shares = [
                ExpenseShare(
                    trip_member=participant,
                    amount=ZERO,
                    quantity=self._get_quantity(
                        expense.split_type,
                        participant,
                    ),
                )
                for participant in participants
            ]

        weights = [self._get_weight(expense.split_type, share) for share in shares]

        total_weight = sum(weights, Decimal("0"))

        if total_weight <= ZERO:
            raise ValueError("Cannot split expense : sum of weights is null")
        self._distribute(shares, weights, expense.amount)

        return shares

    def _get_quantity(
        self,
        split_type: SplitType,
        participant: TripMember,
    ) -> Decimal:
        if split_type == SplitType.BY_NIGHTS:
            return Decimal(participant.nights)

        if split_type in (
            SplitType.BY_PARTICIPANTS,
            SplitType.EQUALLY,
        ):
            return Decimal("1")

        return Decimal("0")

    def _percentage_shares(
        self,
        expense: Expense,
        participants: list[TripMember],
        quantities: dict[UUID, Decimal] | None,
    ) -> list[ExpenseShare]:
        if quantities is None:
            raise ValueError("Quantities are required for BY_PERCENTAGE split type")

        shares = []
        for participant in participants:
            if participant.id not in quantities:
                raise ValueError(
                    f"Missing quantity for participant : {participant.user.name}"
                )
            shares.append(
                ExpenseShare(
                    trip_member=participant,
                    amount=ZERO,
                    quantity=quantities[participant.id],
                )
            )
        return shares

    def _get_weight(
        self,
        split_type: SplitType,
        share: ExpenseShare,
    ) -> Decimal:
        if split_type in (
            SplitType.BY_NIGHTS,
            SplitType.BY_PARTICIPANTS,
            SplitType.EQUALLY,
            SplitType.BY_PERCENTAGE,
        ):
            return share.quantity

        raise ValueError(f"Split type not handled : {split_type}")

    def _validate_percentages(
        self,
        shares: list[ExpenseShare],
    ) -> None:

        total = sum(
            (share.quantity for share in shares),
            Decimal("0"),
        )

        if total != Decimal("100"):
            raise ValueError(f"Percentages must add up to 100 %. Total : {total} %.")

        for share in shares:
            if share.quantity < 0 or share.quantity > 100:
                raise ValueError("Each percentage must be in between 0 and 100")

    def _distribute(
        self,
        shares: list[ExpenseShare],
        weights: list[Decimal],
        amount: Decimal,
    ) -> None:
        total_weight = sum(weights, Decimal("0"))
        allocated = ZERO

        for index, share in enumerate(shares):
            if index == len(shares) - 1:
                share.amount = amount - allocated
                break

            raw_amount = amount * weights[index] / total_weight

            share_amount = raw_amount.quantize(
                CENT,
                rounding=ROUND_DOWN,
            )

            share.amount = share_amount
            allocated += share_amount
