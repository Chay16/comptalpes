from decimal import Decimal

from pydantic import BaseModel


class Cost(BaseModel):
    category: str
    amount: Decimal

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Cost):
            return False
        return self.category == value.category
