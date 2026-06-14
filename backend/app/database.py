"""Database engine, session management, and dependency injection for FastAPI."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session

from .config import settings


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def create_db_and_tables():
    """Create all tables (idempotent via SQLAlchemy)."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency: yields a DB session for a single request."""
    with SessionLocal() as session:
        yield session
