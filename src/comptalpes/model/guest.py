import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class Guest(BaseModel):
    name: str
    id: uuid.UUID = Field(default_factory=lambda: uuid.uuid4())
    stay: list[str] = Field(default_factory=list)
    paid: dict[str, Decimal] = Field(default_factory=dict)
    due: dict[str, Decimal] = Field(default_factory=dict)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Guest):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def reset_due(self) -> None:
        self.due.clear()

    def add_due(self, category: str, amount: Decimal) -> None:
        self.due[category] = self.due.get(category, Decimal(0)) + amount

    @property
    def total_paid(self) -> Decimal:
        return sum(self.paid.values(), Decimal(0))

    @property
    def total_due(self) -> Decimal:
        return sum(self.due.values(), Decimal(0))

    @property
    def balance(self) -> Decimal:
        return self.total_paid - self.total_due
