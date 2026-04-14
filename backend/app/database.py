"""Database engine and session management for WENZE."""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

# Import models so SQLModel.metadata knows about all tables before create_all().
from app import models  # noqa: F401

BACKEND_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = BACKEND_ROOT / "wenze.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False lets FastAPI share the connection across threads.
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


ANONYMOUS_USER_ID = "00000000-0000-0000-0000-000000000000"


def _ensure_anonymous_user() -> None:
    """Insert the placeholder user referenced by mobile POSTs before auth exists.

    Idempotent: only inserts if the row is missing. Will be removed when Phase 3
    introduces real authentication.
    """
    from app.models import User

    with Session(engine) as session:
        if session.get(User, ANONYMOUS_USER_ID) is not None:
            return
        session.add(User(
            id=ANONYMOUS_USER_ID,
            name="Anonyme",
            phone_number="",
            country="RDC",
            city_village="Kinshasa",
            neighborhood="",
        ))
        session.commit()


def init_db() -> None:
    """Create all tables. Idempotent — safe to call on every startup."""
    SQLModel.metadata.create_all(engine)
    _ensure_anonymous_user()


def get_session() -> Iterator[Session]:
    """FastAPI dependency for injecting a database session."""
    with Session(engine) as session:
        yield session
