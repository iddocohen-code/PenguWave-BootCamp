"""SQLModel tables: User, Event, Session (for opaque token storage)."""

import secrets
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class SeverityEnum(str, Enum):
    """Event severity levels — includes CRITICAL to fix the frontend type mismatch."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RoleEnum(str, Enum):
    """User roles for RBAC."""

    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"


class StatusEnum(str, Enum):
    """User account status."""

    active = "active"
    disabled = "disabled"


class User(SQLModel, table=True):
    """User account. ID is the canonical id (usr-001/002/003) shared with event ownership."""

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: RoleEnum
    status: StatusEnum = StatusEnum.active
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Event(SQLModel, table=True):
    """Security event from the data/mock_events.json import. userId can be null (evt-058)."""

    id: str = Field(primary_key=True)
    timestamp: str
    severity: SeverityEnum
    title: str
    description: str
    assetHostname: str
    assetIp: str
    sourceIp: Optional[str] = None
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    userId: Optional[str] = None


class Session(SQLModel, table=True):
    """Opaque session tokens for real logout/revocation. Token is random and indexed for fast lookup."""

    id: str = Field(default_factory=lambda: secrets.token_urlsafe(16), primary_key=True)
    token: str = Field(unique=True, index=True)
    user_id: str = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
