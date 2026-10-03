from collections.abc import Iterator
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from packages.tickets.enums import TicketStatus
from packages.tickets.models import Ticket


@pytest.fixture
def enqueue_classification() -> Iterator[mock.MagicMock]:
    with mock.patch(
        "packages.tickets.services.create_ticket.classify_ticket_task.apply_async"
    ) as apply_async:
        yield apply_async


@pytest.fixture
def cleanup(test_session: Session) -> Iterator[None]:
    yield
    test_session.execute(delete(Ticket).where(Ticket.id == "t-1004"))
    test_session.commit()


def test_create_ticket_successful(
    client: TestClient,
    test_session: Session,
    cleanup: None,
    enqueue_classification: mock.MagicMock,
) -> None:
    request_body = {
        "id": "t-1004",
        "subject": "Change email on account",
        "body": "I'd like to change the email address on my account from my old work address to my personal one. What do I need to do?",
    }
    response = client.post(
        "/tickets",
        json={
            "id": request_body["id"],
            "subject": request_body["subject"],
            "body": request_body["body"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == request_body["id"]
    assert data["subject"] == request_body["subject"]
    assert data["body"] == request_body["body"]
    assert data["status"] == "pending"
    assert data["category"] is None
    assert data["priority"] is None
    assert data["summary"] is None
    assert data["last_classified_at"] is None
    assert "attempts" not in data
    assert "data" not in data
    assert "prompt_version" not in data

    ticket = test_session.execute(
        select(Ticket).where(Ticket.id == request_body["id"])
    ).scalar_one()
    assert ticket.status == "pending"
    assert ticket.attempts == 0
    assert ticket.data == {}
    enqueue_classification.assert_called_once_with(args=("t-1004",))


@pytest.fixture
def existing_ticket(test_session: Session) -> Iterator[Ticket]:
    ticket = Ticket(id="t-1", subject="", body="Original", status=TicketStatus.PENDING)
    test_session.add(ticket)
    test_session.commit()
    yield ticket
    test_session.execute(delete(Ticket).where(Ticket.id == ticket.id))
    test_session.commit()


def test_create_duplicate_ticket_raise_exception(
    client: TestClient,
    existing_ticket: Ticket,
    enqueue_classification: mock.MagicMock,
) -> None:
    response = client.post("/tickets", json={"id": "t-1", "body": "Second"})
    assert response.status_code == 409
    enqueue_classification.assert_not_called()
