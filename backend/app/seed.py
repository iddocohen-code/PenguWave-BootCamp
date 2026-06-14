"""Idempotent database seed: hashed users and 59 events from data/mock_events.json."""

import json
from pathlib import Path
from sqlmodel import Session

from .models import User, Event, RoleEnum, StatusEnum
from .config import settings
from .security import hash_password


def seed_users(session: Session) -> None:
    """Create seed users if they don't exist. Password hashes are computed here."""

    users = [
        User(
            id="usr-001",
            email="admin@penguwave.io",
            password_hash=hash_password(settings.admin_password),
            role=RoleEnum.admin,
            status=StatusEnum.active,
        ),
        User(
            id="usr-002",
            email="analyst@penguwave.io",
            password_hash=hash_password(settings.analyst_password),
            role=RoleEnum.analyst,
            status=StatusEnum.active,
        ),
        User(
            id="usr-003",
            email="viewer@penguwave.io",
            password_hash=hash_password(settings.viewer_password),
            role=RoleEnum.viewer,
            status=StatusEnum.disabled,
        ),
    ]

    for user in users:
        existing = session.get(User, user.id)
        if not existing:
            session.add(user)
    session.commit()


def seed_events(session: Session) -> None:
    """Load 59 events from data/mock_events.json and upsert them by id (idempotent)."""

    # Relative to the repo root, not the backend/ dir.
    data_path = Path(__file__).parent.parent.parent / "data" / "mock_events.json"

    with open(data_path, encoding="utf-8") as f:
        events_data = json.load(f)

    for event_dict in events_data:
        existing = session.get(Event, event_dict["id"])
        if not existing:
            event = Event(**event_dict)
            session.add(event)

    session.commit()
