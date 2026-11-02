from decimal import Decimal
from uuid import UUID

from comptalpes.model.entities.transfer import Transfer
from comptalpes.model.entities.trip_member import TripMember
from comptalpes.model.enums.transfer_status import TransferStatus

ZERO = Decimal("0.00")


class TransfersCalculator:
    def calculate(
        self,
        balances: dict[UUID, Decimal],
        members: list[TripMember],
    ) -> list[Transfer]:

        members_by_id = {member.id: member for member in members}

        creditors = []
        debtors = []

        for member_id, balance in balances.items():
            if member_id not in members_by_id:
                raise ValueError(f"Unknown participant : {member_id}")

            if balance > ZERO:
                creditors.append(
                    [
                        members_by_id[member_id],
                        balance,
                    ]
                )

            elif balance < ZERO:
                debtors.append(
                    [
                        members_by_id[member_id],
                        abs(balance),
                    ]
                )

        creditors.sort(key=lambda item: item[1], reverse=True)
        debtors.sort(key=lambda item: item[1], reverse=True)

        total_credit = sum(
            (item[1] for item in creditors),
            ZERO,
        )

        total_debt = sum(
            (item[1] for item in debtors),
            ZERO,
        )

        if total_credit != total_debt:
            raise ValueError(
                f"Total debt ({total_debt}) must equal total credit ({total_credit})"
            )

        return self._match(debtors, creditors)

    def _match(
        self,
        debtors: list,
        creditors: list,
    ) -> list[Transfer]:

        if not debtors or not creditors:
            return []

        debtor, debt_amount = debtors[0]
        creditor, credit_amount = creditors[0]

        transfer_amount = min(debt_amount, credit_amount)

        settlement = Transfer(
            from_member=debtor,
            to_member=creditor,
            amount=transfer_amount,
            status=TransferStatus.PROPOSED,
        )

        remaining_debt = debt_amount - transfer_amount
        remaining_credit = credit_amount - transfer_amount

        next_debtors = (
            [[debtor, remaining_debt]] if remaining_debt > ZERO else []
        ) + debtors[1:]

        next_creditors = (
            [[creditor, remaining_credit]] if remaining_credit > ZERO else []
        ) + creditors[1:]

        return [
            settlement,
            *self._match(next_debtors, next_creditors),
        ]
