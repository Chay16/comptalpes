from pydantic import BaseModel

from .cost import Cost
from .guest import Guest
from .stay import Stay


class Config(BaseModel):
    costs: list[Cost]
    stay: Stay
    guests: list[Guest]
