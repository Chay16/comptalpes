from decimal import Decimal
from uuid import UUID

from comptalpes.model.entities.trip import Trip
from comptalpes.model.enums.transfer_status import TransferStatus

ZERO = Decimal("0.00")


class BalanceCalculator:
    def calculate(self, trip: Trip, check_balance: bool = True) -> dict[UUID, Decimal]:
        balances = {member.id: ZERO for member in trip.members}

        for expense in trip.expenses:
            for payment in expense.payments:
                member_id = payment.trip_member.id
                self._validate_member(member_id, balances)
                balances[member_id] += payment.amount

            for share in expense.shares:
                member_id = share.trip_member.id
                self._validate_member(member_id, balances)
                balances[member_id] -= share.amount

        for settlement in trip.transfers:
            if settlement.status != TransferStatus.PAID:
                continue

            sender_id = settlement.from_member.id
            self._validate_member(sender_id, balances)
            balances[sender_id] += settlement.amount

            receiver_id = settlement.to_member.id
            self._validate_member(receiver_id, balances)
            balances[receiver_id] -= settlement.amount

        if check_balance:
            total_balance = sum(balances.values(), ZERO)

            if total_balance != ZERO:
                raise ValueError(f"Balances are not balanced: {total_balance}")

        return balances

    @staticmethod
    def _validate_member(
        member_id: UUID,
        balances: dict[UUID, Decimal],
    ) -> None:
        if member_id not in balances:
            raise ValueError(f"Participant {member_id} doesn't belong to the trip.")
