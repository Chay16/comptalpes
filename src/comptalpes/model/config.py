from pydantic import BaseModel

from .cost import Cost
from .day import Day
from .guest import Guest


class Config(BaseModel):
    costs: list[Cost]
    days: list[Day]
    guests: list[Guest]


Config.model_rebuild()
