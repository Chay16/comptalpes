from datetime import date

from pydantic import Field, model_validator

from comptalpes.model.entities.base_entity import BaseEntity
from comptalpes.model.entities.expense import Expense
from comptalpes.model.entities.transfer import Transfer
from comptalpes.model.entities.trip_member import TripMember


class Trip(BaseEntity):
    name: str
    start_date: date
    end_date: date
    currency: str = "EUR"

    members: list[TripMember] = Field(default_factory=list)
    expenses: list["Expense"] = Field(default_factory=list)
    transfers: list["Transfer"] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be anterior to end date.")

        for member in self.members:
            if not (
                self.start_date
                <= member.arrival_date
                < member.departure_date
                <= self.end_date
            ):
                raise ValueError("Trip member dates must be between trip dates.")

        return self
