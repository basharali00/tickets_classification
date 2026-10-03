from sqlalchemy import select

from packages.classification.tasks.classify_ticket_task import (
    MAX_ATTEMPTS,
    classify_ticket_task,
)
from packages.database import SessionLocal
from packages.main_celery import app
from packages.tickets.enums import TicketStatus
from packages.tickets.models import Ticket

BATCH_SIZE = 100
DELAY_BETWEEN_TASKS_SECONDS = 1


@app.task
def periodic_classify_tickets_task() -> None:
    with SessionLocal() as session:
        ticket_ids = (
            session.execute(
                select(Ticket.id)
                .where(
                    Ticket.status == TicketStatus.PENDING,
                    Ticket.attempts < MAX_ATTEMPTS,
                )
                .order_by(Ticket.created_at)
                .limit(BATCH_SIZE)
            )
            .scalars()
            .all()
        )

    for index, ticket_id in enumerate(ticket_ids):
        classify_ticket_task.apply_async(
            args=(ticket_id,), countdown=index * DELAY_BETWEEN_TASKS_SECONDS
        )
