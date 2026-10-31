import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from .guest import Guest


class Day(BaseModel):
    name: str
    id: uuid.UUID = Field(default_factory=lambda: uuid.uuid4())
    costs: dict[str, Decimal] = Field(default_factory=dict)
    guests: set["Guest"] = Field(default_factory=set)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Day):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def occupancy(self) -> int:
        return len(self.guests)

    def add_guest(self, new_guest: Guest) -> None:
        self.guests.add(new_guest)

    @property
    def cost_per_guest(self) -> dict[str, Decimal]:
        if not self.guests:
            return {}
        count = Decimal(len(self.guests))
        return {category: amount / count for category, amount in self.costs.items()}
