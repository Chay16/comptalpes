from datetime import date
from decimal import Decimal

from fastapi import APIRouter
from pydantic import BaseModel

from comptalpes.model.entities import Expense, ExpenseCategory
from comptalpes.model.enums import SplitType

router = APIRouter()


class ExpensePayload(BaseModel):
    description: str
    amount: Decimal
    expense_date: date | None = None
    category: str = "Divers"
    split_type: SplitType | None = None


def build_expense(payload: ExpensePayload) -> Expense:
    return Expense(
        description=payload.description,
        amount=payload.amount,
        expense_date=payload.expense_date or date.today(),
        category=ExpenseCategory(name=payload.category),
        split_type_override=payload.split_type,
    )


@router.get("/expenses/", tags=["expenses"])
def get_expenses():
    expense = build_expense(
        ExpensePayload(
            description="Fundue", amount=Decimal("100"), category="Restaurant"
        )
    )
    return [expense]


@router.post("/expenses/", tags=["expenses"])
def add_expense(payload: ExpensePayload):
    return build_expense(payload)


@router.patch("/expenses/", tags=["expenses"])
def update_expense(payload: ExpensePayload):
    return build_expense(payload)
