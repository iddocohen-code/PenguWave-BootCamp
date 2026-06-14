"""Authentication endpoints: login, logout, and current user info."""

from sqlmodel import Session, select
from fastapi import APIRouter, Depends

from ..schemas import LoginIn, TokenOut, UserOut
from ..models import User, Session as SessionModel
from ..security import verify_password, create_session_token, hash_password
from ..database import get_session
from ..deps import get_current_user, get_token
from ..errors import AuthenticationError

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
async def login(
    body: LoginIn,
    session: Session = Depends(get_session),
) -> TokenOut:
    """Authenticate a user and create a session token.

    Returns {token, user} on success (200).
    Returns {error: "..."} on failure (401).
    """
    # Lookup user by email
    stmt = select(User).where(User.email == body.email)
    user = session.exec(stmt).first()

    # Verify password and status (same error for unknown user or bad password to prevent enumeration)
    if not user or not verify_password(body.password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    if user.status.value != "active":
        raise AuthenticationError("Invalid email or password")

    # Create a session token
    token = create_session_token()
    session_record = SessionModel(token=token, user_id=user.id)
    session.add(session_record)
    session.commit()

    return TokenOut(
        token=token,
        user=UserOut(id=user.id, email=user.email, role=user.role, status=user.status),
    )


@router.post("/logout")
async def logout(
    token: str = Depends(get_token),
    session: Session = Depends(get_session),
) -> dict[str, str]:
    """Revoke the current session token (real logout).

    Returns {message: "Logged out"} (200).
    """
    if token:
        # Delete the session record (if it exists)
        stmt = select(SessionModel).where(SessionModel.token == token)
        session_record = session.exec(stmt).first()
        if session_record:
            session.delete(session_record)
            session.commit()

    return {"message": "Logged out"}


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)) -> UserOut:
    """Get the currently authenticated user's info.

    Returns the user (200) or {error: "..."} (401).
    """
    return UserOut(id=user.id, email=user.email, role=user.role, status=user.status)
