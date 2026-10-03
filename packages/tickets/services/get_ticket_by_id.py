from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.tickets.models import Ticket


def get_ticket_by_id(session: Session, ticket_id: str) -> Ticket:
    ticket = session.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    ).scalar_one_or_none()

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "Ticket not found", "id": ticket_id},
        )

    return ticket
