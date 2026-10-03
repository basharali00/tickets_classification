from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from packages.tickets.enums import Category, Priority, TicketStatus
from packages.tickets.models import Ticket


def test_list_empty(client: TestClient) -> None:
    response = client.get("/tickets")

    assert response.status_code == 200
    assert response.json() == {"total_count": 0, "result_list": []}


@pytest.fixture
def tickets_fixture(test_session: Session) -> Iterator[list[str]]:
    tickets = [
        ("billing-high", TicketStatus.CLASSIFIED, Category.BILLING, Priority.HIGH),
        ("billing-low", TicketStatus.CLASSIFIED, Category.BILLING, Priority.LOW),
        ("technical-high", TicketStatus.CLASSIFIED, Category.TECHNICAL, Priority.HIGH),
        ("pending", TicketStatus.PENDING, None, None),
    ]
    for ticket_id, status, category, priority in tickets:
        test_session.add(
            Ticket(
                id=ticket_id,
                subject="",
                body="Body",
                status=status,
                category=category,
                priority=priority,
            )
        )
        test_session.commit()
    ticket_ids = [ticket_id for ticket_id, _, _, _ in tickets]
    yield ticket_ids
    test_session.execute(delete(Ticket).where(Ticket.id.in_(ticket_ids)))
    test_session.commit()


def test_list_without_filters_returns_all(
    client: TestClient, tickets_fixture: list[str]
) -> None:
    response = client.get("/tickets")

    assert response.status_code == 200
    assert response.json()["result_list"][0]["id"] == "billing-high"
    assert response.json()["result_list"][1]["id"] == "billing-low"
    assert response.json()["result_list"][2]["id"] == "technical-high"
    assert response.json()["result_list"][3]["id"] == "pending"
    assert response.json()["total_count"] == 4


def test_filter_by_category_excludes_pending(
    client: TestClient, tickets_fixture: list[str]
) -> None:
    response = client.get("/tickets", params={"category": "billing"})

    assert response.status_code == 200
    assert response.json()["result_list"][0]["id"] == "billing-high"
    assert response.json()["result_list"][1]["id"] == "billing-low"
    assert response.json()["total_count"] == 2


def test_filter_by_priority(client: TestClient, tickets_fixture: list[str]) -> None:
    response = client.get("/tickets", params={"priority": "high"})

    assert response.status_code == 200
    assert response.json()["result_list"][0]["id"] == "billing-high"
    assert response.json()["result_list"][1]["id"] == "technical-high"
    assert response.json()["total_count"] == 2


def test_filter_by_category_and_priority(
    client: TestClient, tickets_fixture: list[str]
) -> None:
    response = client.get("/tickets", params={"category": "billing", "priority": "low"})

    assert response.status_code == 200
    assert response.json()["total_count"] == 1
    ticket = response.json()["result_list"][0]
    assert ticket["id"] == "billing-low"
    assert ticket["subject"] == ""
    assert ticket["body"] == "Body"
    assert ticket["status"] == "classified"
    assert ticket["category"] == "billing"
    assert ticket["priority"] == "low"
    assert ticket["summary"] is None
    assert ticket["last_classified_at"] is None


def test_filter_with_no_match(client: TestClient, tickets_fixture: list[str]) -> None:
    response = client.get("/tickets", params={"category": "account"})

    assert response.status_code == 200
    assert response.json() == {"total_count": 0, "result_list": []}
