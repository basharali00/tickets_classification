from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from packages.settings import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(engine, autoflush=False)


class Base(DeclarativeBase):
    pass
