"""FastAPI dependency injection for authentication and authorization."""

from sqlmodel import Session, select

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .database import get_session
from .models import User, Session as SessionModel
from .errors import AuthenticationError, AuthorizationError

# Extracts the Bearer token from the Authorization header. auto_error=False so a
# missing header yields no credentials (handled below) rather than FastAPI's default 403.
security = HTTPBearer(auto_error=False)


async def get_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Extract the Bearer token from the Authorization header (empty string if absent)."""
    if not credentials:
        return ""
    return credentials.credentials


async def get_current_user(
    token: str = Depends(get_token), session: Session = Depends(get_session)
) -> User:
    """Dependency: read the Bearer token, look up the session, return the user if active.

    Raises AuthenticationError if token is missing, invalid, or the user is disabled.
    """
    if not token:
        raise AuthenticationError("Authentication required")

    # Look up the session token in the database
    stmt = select(SessionModel).where(SessionModel.token == token)
    session_record = session.exec(stmt).first()

    if not session_record:
        raise AuthenticationError("Invalid or expired token")

    # Get the user
    user = session.get(User, session_record.user_id)
    if not user or user.status.value != "active":
        raise AuthenticationError("User not found or disabled")

    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Dependency: ensure the current user has the admin role."""
    if user.role.value != "admin":
        raise AuthorizationError("Admin role required")
    return user
