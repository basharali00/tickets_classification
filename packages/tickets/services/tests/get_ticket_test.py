from collections.abc import Iterator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from packages.tickets.enums import Category, Priority, TicketStatus
from packages.tickets.models import Ticket


@pytest.fixture
def pending_ticket(test_session: Session) -> Iterator[Ticket]:
    ticket = Ticket(
        id="t-1",
        subject="Refund",
        body="Charged twice",
        status=TicketStatus.PENDING,
    )
    test_session.add(ticket)
    test_session.commit()
    yield ticket
    test_session.execute(delete(Ticket).where(Ticket.id == ticket.id))
    test_session.commit()


def test_get_returns_pending_ticket(client: TestClient, pending_ticket: Ticket) -> None:
    response = client.get("/tickets/t-1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "t-1"
    assert data["subject"] == "Refund"
    assert data["body"] == "Charged twice"
    assert data["status"] == "pending"
    assert data["category"] is None


@pytest.fixture
def classified_ticket(test_session: Session) -> Iterator[Ticket]:
    ticket = Ticket(
        id="t-1",
        subject="Refund",
        body="Charged twice",
        status=TicketStatus.CLASSIFIED,
        category=Category.BILLING,
        priority=Priority.HIGH,
        summary="Customer reports a double charge.",
        last_classified_at=datetime.now(),
    )
    test_session.add(ticket)
    test_session.commit()
    yield ticket
    test_session.execute(delete(Ticket).where(Ticket.id == ticket.id))
    test_session.commit()


def test_get_returns_classification_fields(
    client: TestClient, classified_ticket: Ticket
) -> None:
    data = client.get("/tickets/t-1").json()

    assert data["status"] == "classified"
    assert data["category"] == "billing"
    assert data["priority"] == "high"
    assert data["summary"] == "Customer reports a double charge."
    assert data["last_classified_at"] is not None


def test_get_unknown_id_returns_404(client: TestClient) -> None:
    response = client.get("/tickets/missing")

    assert response.status_code == 404
    assert response.json()["detail"]["id"] == "missing"
