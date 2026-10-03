from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from dependencies.get_db_session import get_db_session
from packages.tickets.enums import Category, Priority
from packages.tickets.schemas import TicketCreate, TicketList, TicketResponse
from packages.tickets.services.create_ticket import create_ticket_
from packages.tickets.services.get_ticket_by_id import get_ticket_by_id
from packages.tickets.services.get_tickets import get_tickets

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(body: TicketCreate, session: Session = Depends(get_db_session)):
    return create_ticket_(session=session, body=body)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, session: Session = Depends(get_db_session)):
    return get_ticket_by_id(session=session, ticket_id=ticket_id)


@router.get("", response_model=TicketList)
def list_tickets(
    session: Session = Depends(get_db_session),
    category: Category | None = Query(None),
    priority: Priority | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return get_tickets(
        session=session,
        category=category,
        priority=priority,
        offset=offset,
        limit=limit,
    )
