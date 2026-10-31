from decimal import Decimal
from fastapi import APIRouter

from comptalpes.model import Cost

router = APIRouter()


@router.get("/costs/", tags=["costs"])
def get_costs():
    cost_house = Cost(category="house", amount=Decimal("100"))
    return [cost_house]


@router.post("/costs/{category}", tags=["costs"])
def add_cost(category: str, amount: Decimal):
    new_cost = Cost(category=category, amount=amount)
    print(f"Adding {new_cost}")


@router.patch("/costs/{category}", tags=["costs"])
def update_cost(category: str, amount: Decimal):
    cost = Cost(category=category, amount=amount)
    print(f"Update {cost}")
