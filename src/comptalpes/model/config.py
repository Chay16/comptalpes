from pydantic import BaseModel

from .cost import Cost
from .stay import Stay
from .guest import Guest


class Config(BaseModel):
    costs: list[Cost]
    stay: Stay
    guests: list[Guest]
