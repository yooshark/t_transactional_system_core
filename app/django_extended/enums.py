from enum import StrEnum


class TransactionStatusType(StrEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
