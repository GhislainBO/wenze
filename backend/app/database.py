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


def init_db() -> None:
    """Create all tables. Idempotent — safe to call on every startup."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency for injecting a database session."""
    with Session(engine) as session:
        yield session
