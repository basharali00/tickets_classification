import logging
from datetime import datetime
from uuid import uuid4

from sqlalchemy import select

from helpers.llm.consts import LLM_MODEL_PROVIDER, LLM_PROVIDER_API
from helpers.llm.enums import LLMModel
from packages.classification.models import ClassificationLog
from packages.classification.utils.build_prompt import build_prompt
from packages.database import SessionLocal
from packages.main_celery import app
from packages.tickets.enums import TicketStatus
from packages.tickets.models import Ticket

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
PROMPT_VERSION = "v1"
LLM_MODEL = LLMModel.CLAUDE_OPUS_5_5


@app.task
def classify_ticket_task(ticket_id: str) -> None:
    with SessionLocal() as session:
        ticket = session.execute(
            select(Ticket).where(Ticket.id == ticket_id).with_for_update()
        ).scalar_one()

        if ticket.attempts >= MAX_ATTEMPTS:
            logger.error(
                "ticket reached max attempts",
                extra={
                    "ticket_id": ticket_id,
                    "max_attempts": MAX_ATTEMPTS,
                    "ticket_attempts": ticket.attempts,
                },
            )
            return

        if ticket.status != TicketStatus.PENDING:
            logger.error(
                "ticket is not pending",
                extra={"ticket_id": ticket_id, "ticket_status": ticket.status},
            )
            return

        prompt = build_prompt(
            version=PROMPT_VERSION, subject=ticket.subject, body=ticket.body
        )
        llm_provider = LLM_MODEL_PROVIDER[LLM_MODEL]
        try:
            result = LLM_PROVIDER_API[llm_provider].classify_ticket(
                prompt=prompt, model=LLM_MODEL
            )
            ticket.status = TicketStatus.CLASSIFIED.value
            ticket.category = result.category
            ticket.priority = result.priority
            ticket.summary = result.summary
            ticket.prompt_version = PROMPT_VERSION
            ticket.last_classified_at = datetime.now()
            session.add(
                ClassificationLog(
                    id=str(uuid4()),
                    ticket_id=ticket_id,
                    prompt_version=PROMPT_VERSION,
                    llm_provider=llm_provider,
                    llm_model=LLM_MODEL,
                    data={
                        "attempt": ticket.attempts + 1,
                        **result.model_dump(mode="json"),
                    },
                )
            )
        except Exception:
            logger.exception(
                "ticket classification failed",
                extra={
                    "ticket_id": ticket_id,
                    "ticket_attempts": ticket.attempts + 1,
                },
            )
            ticket.attempts += 1
            if ticket.attempts >= MAX_ATTEMPTS:
                ticket.status = TicketStatus.FAILED.value

        session.commit()
