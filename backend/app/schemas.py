"""Pydantic schemas for request/response bodies and OpenAPI documentation."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from .models import RoleEnum, SeverityEnum, StatusEnum
from .sanitize import escape_event_text


class LoginIn(BaseModel):
    """Request body for POST /api/auth/login."""

    email: EmailStr
    password: str


class UserOut(BaseModel):
    """User object returned in responses. Never includes password."""

    id: str
    email: str
    role: RoleEnum
    status: StatusEnum


class TokenOut(BaseModel):
    """Response body for successful login: a Bearer token + user info."""

    token: str
    user: UserOut


class UserCreate(BaseModel):
    """Request body for POST /api/users (admin only)."""

    email: EmailStr
    password: str
    role: RoleEnum


class UserPatch(BaseModel):
    """Request body for PATCH /api/users/{id} (admin only). All fields optional."""

    role: Optional[RoleEnum] = None
    status: Optional[StatusEnum] = None


class EventOut(BaseModel):
    """Event returned in responses, with HTML-escaped text fields for XSS safety."""

    id: str
    timestamp: str
    severity: SeverityEnum
    title: str
    description: str
    assetHostname: str
    assetIp: str
    sourceIp: Optional[str] = None
    tags: list[str]
    userId: Optional[str] = None

    @field_validator("title", "description")
    @classmethod
    def escape_text_fields(cls, v: Optional[str]) -> Optional[str]:
        """Escape title and description on output so stored XSS (evt-052) is rendered inert."""
        return escape_event_text(v)


class TriageOut(BaseModel):
    """AI SOC-analyst triage for an event: the three sections plus event context."""

    event_id: str
    severity: SeverityEnum
    summary: str
    blast_radius: str
    next_step: str


class ErrorOut(BaseModel):
    """Standardized error response shape: {"error": "..."}."""

    error: str
