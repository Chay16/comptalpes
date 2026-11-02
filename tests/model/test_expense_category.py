import pytest
from pydantic import ValidationError

from comptalpes.model.entities import ExpenseCategory
from comptalpes.model.enums import SplitType


def test_expense_category() -> None:
    category = ExpenseCategory(name="Restaurant")
    assert category.name == "Restaurant"


def test_expense_category_default_split_type() -> None:
    category = ExpenseCategory(name="Restaurant")
    assert category.split_type == SplitType.BY_PARTICIPANTS


def test_expense_category_explicit_split_type() -> None:
    category = ExpenseCategory(name="Chalet", split_type=SplitType.BY_NIGHTS)
    assert category.split_type == SplitType.BY_NIGHTS


def test_expense_category_requires_name() -> None:
    with pytest.raises(ValidationError):
        ExpenseCategory()
