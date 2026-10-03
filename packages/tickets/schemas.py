from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from packages.tickets.enums import Category, Priority, TicketStatus


class TicketCreate(BaseModel):
    id: str = Field(max_length=36)
    subject: str = Field(default="", max_length=500)
    body: str = Field(min_length=1, max_length=20_000)


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    subject: str
    body: str
    status: TicketStatus
    category: Category | None
    priority: Priority | None
    summary: str | None
    failure_reason: str | None = None
    created_at: datetime
    updated_at: datetime
    last_classified_at: datetime | None


class TicketList(BaseModel):
    total_count: int
    result_list: list[TicketResponse]
