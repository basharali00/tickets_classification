from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column

from packages.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(sa.String(), primary_key=True)
    subject: Mapped[str] = mapped_column(sa.String())
    body: Mapped[str] = mapped_column(sa.String())
    status: Mapped[str] = mapped_column(sa.String(), index=True)
    category: Mapped[str | None] = mapped_column(sa.String(), nullable=True, index=True)
    priority: Mapped[str | None] = mapped_column(sa.String(), nullable=True, index=True)
    summary: Mapped[str | None] = mapped_column(sa.String(), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(sa.String(), nullable=True)
    attempts: Mapped[int] = mapped_column(default=0)
    data: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSONB()), default={}, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=False), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=False), default=datetime.now, onupdate=datetime.now
    )
    last_classified_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=False),
        nullable=True,
    )
