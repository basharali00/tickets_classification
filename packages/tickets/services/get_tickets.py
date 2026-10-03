from sqlalchemy import func, select
from sqlalchemy.orm import Session

from packages.tickets.enums import Category, Priority
from packages.tickets.models import Ticket


def get_tickets(
    session: Session,
    category: Category | None,
    priority: Priority | None,
    offset: int,
    limit: int,
) -> dict:
    stmt = select(Ticket)
    if category is not None:
        stmt = stmt.where(Ticket.category == category)

    if priority is not None:
        stmt = stmt.where(Ticket.priority == priority)

    total_count = (
        session.execute(select(func.count()).select_from(stmt.subquery())).scalar() or 0
    )

    tickets = (
        session.execute(
            stmt.order_by(Ticket.created_at, Ticket.id).offset(offset).limit(limit)
        )
        .scalars()
        .all()
    )
    return {"total_count": total_count, "result_list": tickets}
