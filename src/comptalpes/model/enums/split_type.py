from enum import Enum


class SplitType(str, Enum):
    BY_NIGHTS = "by_nights"
    EQUALLY = "equally"
    BY_PARTICIPANTS = "by_participants"
    BY_PERCENTAGE = "by_percentage"
