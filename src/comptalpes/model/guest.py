from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass
class Guest:
    name: str
    id: UUID = field(default_factory=uuid4)
    stay: list[str] = field(default_factory=list)
    paid: dict[str, Decimal] = field(default_factory=dict)
    due: dict[str, Decimal] = field(default_factory=dict)

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
