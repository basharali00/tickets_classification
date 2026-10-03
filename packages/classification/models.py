from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column

from packages.database import Base


class ClassificationLog(Base):
    __tablename__ = "classification_log"

    id: Mapped[str] = mapped_column(sa.String(), primary_key=True)
    ticket_id: Mapped[str] = mapped_column(
        sa.String(), sa.ForeignKey("tickets.id"), index=True
    )
    prompt_version: Mapped[str] = mapped_column(sa.String())
    llm_provider: Mapped[str] = mapped_column(sa.String())
    llm_model: Mapped[str] = mapped_column(sa.String())
    data: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSONB()),
        default={},
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=False),
        default=datetime.now,
    )
