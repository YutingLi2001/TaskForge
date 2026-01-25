import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    REMEMBER_ME_REFRESH_DAYS,
    SECRET_KEY,
)
from ..database import get_db
from ..models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expires = now + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expires, "iat": now, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(email: str, remember_me: bool = False) -> tuple[str, datetime]:
    """Create a refresh token and its expiry."""
    now = datetime.now(timezone.utc)
    days = REMEMBER_ME_REFRESH_DAYS if remember_me else REFRESH_TOKEN_EXPIRE_DAYS
    expires = now + timedelta(days=days)
    token = secrets.token_urlsafe(48)
    return token, expires


def hash_refresh_token(token: str) -> str:
    """Hash refresh token for storage."""
    digest = hmac.new(SECRET_KEY.encode(), token.encode(), hashlib.sha256).hexdigest()
    return digest


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise credentials_exception from exc

    token_type = payload.get("type")
    if token_type != "access":
        raise credentials_exception

    if payload.get("sub") is None:
        raise credentials_exception

    return payload


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Return the authenticated user or raise 401."""
    payload = decode_access_token(token)
    email = payload.get("sub")
    user = await db.scalar(select(User).where(User.email == email))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled.",
        )
    return user
