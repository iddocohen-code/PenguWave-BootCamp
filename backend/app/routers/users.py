"""User management endpoints (admin-only): CRUD operations with self-lockout guards."""

from sqlmodel import Session, select
from fastapi import APIRouter, Depends

from ..schemas import UserOut, UserCreate, UserPatch
from ..models import User, RoleEnum, StatusEnum
from ..database import get_session
from ..deps import require_admin
from ..security import hash_password
from ..errors import ValidationError, NotFoundError, AuthorizationError

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserOut])
async def list_users(
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> list[UserOut]:
    """List all users (admin only).

    Returns array of users (200) or {error: "..."} (403/401).
    """
    stmt = select(User)
    users = session.exec(stmt).all()
    return [UserOut(id=u.id, email=u.email, role=u.role, status=u.status) for u in users]


@router.post("", response_model=UserOut, status_code=201)
async def create_user(
    body: UserCreate,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> UserOut:
    """Create a new user (admin only).

    Returns the created user (201) or {error: "..."} (400/403/401).
    """
    # Validate password length
    if len(body.password) < 6:
        raise ValidationError("Password must be at least 6 characters")

    # Check email uniqueness
    stmt = select(User).where(User.email == body.email)
    existing = session.exec(stmt).first()
    if existing:
        raise ValidationError("Email already exists")

    # Create user with hashed password
    user = User(
        id=f"usr-{len(session.exec(select(User)).all()) + 1:03d}",  # Simple ID generation
        email=body.email,
        password_hash=hash_password(body.password),
        role=body.role,
        status=StatusEnum.active,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return UserOut(id=user.id, email=user.email, role=user.role, status=user.status)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str,
    body: UserPatch,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> UserOut:
    """Update a user's role or status (admin only).

    Returns the updated user (200) or {error: "..."} (400/403/404/401).
    """
    # Reject empty patch
    if body.role is None and body.status is None:
        raise ValidationError("At least one field (role, status) must be provided")

    user = session.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")

    # Self-lockout guard: admin cannot disable themselves or demote themselves if sole admin
    if user.id == admin.id:
        if body.status == StatusEnum.disabled:
            raise ValidationError("Cannot lock yourself out")
        if body.role and body.role != RoleEnum.admin:
            # Check if this is the last admin
            stmt = select(User).where(User.role == RoleEnum.admin)
            admin_count = len(session.exec(stmt).all())
            if admin_count == 1:
                raise ValidationError("Cannot demote yourself as the last admin")

    # Update fields
    if body.role is not None:
        user.role = body.role
    if body.status is not None:
        user.status = body.status

    session.add(user)
    session.commit()
    session.refresh(user)

    return UserOut(id=user.id, email=user.email, role=user.role, status=user.status)


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> dict[str, str]:
    """Delete a user (admin only).

    Returns {message: "User deleted"} (200) or {error: "..."} (400/403/404/401).
    """
    user = session.get(User, user_id)
    if not user:
        raise NotFoundError("User not found")

    # Self-deletion guard: admin cannot delete their own account
    if user.id == admin.id:
        raise ValidationError("Cannot delete yourself")

    # Last-admin guard: prevent deleting the last admin
    if user.role == RoleEnum.admin:
        stmt = select(User).where(User.role == RoleEnum.admin)
        admin_count = len(session.exec(stmt).all())
        if admin_count == 1:
            raise ValidationError("Cannot delete the last admin")

    session.delete(user)
    session.commit()

    return {"message": "User deleted"}
