"""Utility functions for password hashing and session token management."""

from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    return pwd_context.verify(plain, hashed)


def create_session_token() -> str:
    """Generate a random opaque session token (32 bytes, URL-safe)."""
    return secrets.token_urlsafe(32)
