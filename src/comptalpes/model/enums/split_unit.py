from enum import Enum


class SplitUnit(str, Enum):
    NIGHT = "night"
    PERSON = "person"
    CUSTOM = "custom"
