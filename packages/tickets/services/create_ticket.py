from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.classification.tasks.classify_ticket_task import classify_ticket_task
from packages.tickets.enums import TicketStatus
from packages.tickets.models import Ticket
from packages.tickets.schemas import TicketCreate


def create_ticket_(session: Session, body: TicketCreate) -> Ticket:
    existing_id = session.execute(
        select(Ticket.id).where(Ticket.id == body.id)
    ).scalar_one_or_none()
    if existing_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Ticket already exists", "id": body.id},
        )
    ticket_id = body.id
    ticket = Ticket(
        id=body.id,
        subject=body.subject,
        body=body.body,
        status=TicketStatus.PENDING.value,
        category=None,
        priority=None,
        summary=None,
        prompt_version=None,
        last_classified_at=None,
    )
    session.add(ticket)
    session.commit()
    classify_ticket_task.apply_async(args=(ticket_id,))
    return ticket
