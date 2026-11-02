from enum import Enum


class TransferStatus(str, Enum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    PAID = "paid"
    CANCELLED = "cancelled"
