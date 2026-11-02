from datetime import date
from decimal import Decimal

from pydantic import Field, field_validator, model_validator

from comptalpes.model.entities.base_entity import BaseEntity
from comptalpes.model.entities.trip_member import TripMember
from comptalpes.model.enums import TransferStatus


class Transfer(BaseEntity):
    from_member: TripMember
    to_member: TripMember

    amount: Decimal = Field(gt=0)
    paid_at: date | None = None
    status: TransferStatus = TransferStatus.PROPOSED

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))

    @model_validator(mode="after")
    def validate_members(self):
        if self.from_member.id == self.to_member.id:
            raise ValueError("A trip memeber cannot reimburse himself.")

        if self.status == TransferStatus.PAID and self.paid_at is None:
            raise ValueError("A paid transfer must have a paid date.")

        return self
