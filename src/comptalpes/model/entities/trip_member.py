from datetime import date

from pydantic import model_validator

from comptalpes.model.entities.base_entity import BaseEntity
from comptalpes.model.entities.user import User


class TripMember(BaseEntity):
    user: User
    arrival_date: date
    departure_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.arrival_date >= self.departure_date:
            raise ValueError("Arrival date should be anterior to departure date.")
        return self

    @property
    def nights(self) -> int:
        return (self.departure_date - self.arrival_date).days
