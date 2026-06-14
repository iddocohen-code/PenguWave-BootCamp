"""FastAPI dependency injection for authentication and authorization."""

from sqlmodel import Session, select

from fastapi import Depends

from .database import get_session
from .models import User, Session as SessionModel
from .errors import AuthenticationError, AuthorizationError


async def get_current_user(
    token: str, session: Session = Depends(get_session)
) -> User:
    """Dependency: extract Bearer token from header, look up session, return the user if active.

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


# Dependency for extracting the Bearer token from headers
from fastapi.security import HTTPBearer, HTTPAuthenticationCredentials

security = HTTPBearer(auto_error=False)


async def get_token(credentials: HTTPAuthenticationCredentials = Depends(security)) -> str:
    """Extract the Bearer token from the Authorization header."""
    if not credentials:
        return ""
    return credentials.credentials
