from datetime import date
from decimal import Decimal

from pydantic import Field, field_validator, model_validator

from comptalpes.model.entities.base_entity import BaseEntity
from comptalpes.model.entities.expense_category import ExpenseCategory
from comptalpes.model.entities.trip_member import TripMember
from comptalpes.model.enums.split_type import SplitType


class ExpensePayment(BaseEntity):
    trip_member: TripMember
    amount: Decimal = Field(gt=0)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))


class ExpenseShare(BaseEntity):
    trip_member: TripMember
    amount: Decimal = Field(ge=0)
    quantity: Decimal = Field(default=Decimal("0"), ge=0)
    is_manually_adjusted: bool = False

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))


class Expense(BaseEntity):
    description: str
    amount: Decimal = Field(gt=0)
    expense_date: date

    category: ExpenseCategory
    split_type_override: SplitType | None = None

    payments: list[ExpensePayment] = Field(default_factory=list)
    shares: list[ExpenseShare] = Field(default_factory=list)

    @property
    def split_type(self) -> SplitType:
        return self.split_type_override or self.category.split_type

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"))

    @model_validator(mode="after")
    def validate_totals(self):
        payment_total = sum(
            (payment.amount for payment in self.payments), Decimal("0.00")
        )

        share_total = sum((share.amount for share in self.shares), Decimal("0.00"))

        if self.payments and payment_total != self.amount:
            raise ValueError(
                f"Total payments ({payment_total}) must be egal to ({self.amount})."
            )

        if self.shares and share_total != self.amount:
            raise ValueError(
                f"Total shares ({share_total}) must be egal to ({self.amount})."
            )

        return self
