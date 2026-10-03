from collections.abc import Iterator

import alembic.config
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import Session

from packages.database import SessionLocal
from packages.main import app
from packages.settings import settings
from packages.tickets.models import Ticket

# init_db drops the database; never let it touch a non-test one.
assert settings.ENVIRONMENT == "test", "run tests with ENVIRONMENT=test"


def init_db() -> None:
    url = make_url(settings.DATABASE_URL)
    db_name = url.database

    # always connect to admin DB (NOT target DB)
    admin_engine = create_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    with admin_engine.connect() as conn:
        conn.execute(
            text("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = :db_name
                    AND pid <> pg_backend_pid()
            """),
            {"db_name": db_name},
        )
        conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}"'))
        conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    admin_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def create_and_upgrade_db() -> Iterator[None]:
    init_db()
    alembic.config.main(argv=["upgrade", "head"])
    yield


@pytest.fixture
def test_session(create_and_upgrade_db: None) -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
        session.rollback()
        session.execute(delete(Ticket))
        session.commit()


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    client = TestClient(app)
    yield client
    client.close()
