from enum import StrEnum


class TicketStatus(StrEnum):
    PENDING = "pending"
    CLASSIFIED = "classified"
    FAILED = "failed"


class Category(StrEnum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    OTHER = "other"


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
