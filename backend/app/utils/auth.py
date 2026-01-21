from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets

from jose import jwt
from passlib.context import CryptContext

from ..config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REMEMBER_ME_REFRESH_DAYS,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    expires = now + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expires, "iat": now, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(email: str, remember_me: bool = False) -> tuple[str, datetime]:
    """Create a refresh token and its expiry."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    days = REMEMBER_ME_REFRESH_DAYS if remember_me else REFRESH_TOKEN_EXPIRE_DAYS
    expires = now + timedelta(days=days)
    token = secrets.token_urlsafe(48)
    return token, expires


def hash_refresh_token(token: str) -> str:
    """Hash refresh token for storage."""
    digest = hmac.new(SECRET_KEY.encode(), token.encode(), hashlib.sha256).hexdigest()
    return digest
