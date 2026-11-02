from comptalpes.model.entities.base_entity import BaseEntity
from comptalpes.model.enums.split_type import SplitType


class ExpenseCategory(BaseEntity):
    name: str
    split_type: SplitType = SplitType.BY_PARTICIPANTS
