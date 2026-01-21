from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import config
from ..database import get_db
from ..models.user import User
from ..schemas.user import (
    LoginDataResponse,
    LoginRequest,
    LoginResponse,
    RefreshDataResponse,
    RefreshRequest,
    RefreshResponse,
    UserCreate,
    UserDataResponse,
    UserPublicDataResponse,
    UserPublicResponse,
    UserResponse,
)
from ..utils.auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    hash_refresh_token,
    verify_password,
)

router = APIRouter()
_login_rate_limit: dict[tuple[str, str], list[datetime]] = {}


@router.post("/register", response_model=UserDataResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with hashed password
    hashed_pwd = hash_password(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed_pwd)

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    db.refresh(new_user)

    return UserDataResponse(data=UserResponse.model_validate(new_user))


@router.post("/login", response_model=LoginDataResponse)
def login(credentials: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    client_ip = request.client.host if request.client else "unknown"
    rate_key = (client_ip, credentials.email)
    attempts = _login_rate_limit.get(rate_key, [])
    attempts = [ts for ts in attempts if (now - ts).total_seconds() < config.LOGIN_RATE_LIMIT_WINDOW_SECONDS]
    if len(attempts) >= config.LOGIN_RATE_LIMIT_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later."
        )

    user = db.query(User).filter(User.email == credentials.email).first()
    if user and user.locked_until and user.locked_until > now:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked. Try again later."
        )
    if user and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled."
        )
    if not user or not verify_password(credentials.password, user.hashed_password):
        attempts.append(now)
        _login_rate_limit[rate_key] = attempts
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= config.LOGIN_LOCKOUT_THRESHOLD:
                user.locked_until = now + timedelta(minutes=config.LOGIN_LOCKOUT_MINUTES)
            db.add(user)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    user.failed_login_attempts = 0
    user.locked_until = None
    access_token = create_access_token(
        data={"sub": user.email, "verified": user.is_verified}
    )
    refresh_token, refresh_expires = create_refresh_token(
        user.email, remember_me=credentials.remember_me
    )
    user.refresh_token_hash = hash_refresh_token(refresh_token)
    user.refresh_token_expires_at = refresh_expires
    db.add(user)
    db.commit()
    response = LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )
    return LoginDataResponse(data=response)


@router.post("/refresh", response_model=RefreshDataResponse)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Rotate refresh token and issue new access token."""
    token_hash = hash_refresh_token(payload.refresh_token)
    user = db.query(User).filter(User.refresh_token_hash == token_hash).first()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    if user.refresh_token_expires_at and user.refresh_token_expires_at < now:
        user.refresh_token_hash = None
        user.refresh_token_expires_at = None
        db.add(user)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled."
        )

    access_token = create_access_token(data={"sub": user.email})
    new_refresh_token, refresh_expires = create_refresh_token(user.email)
    user.refresh_token_hash = hash_refresh_token(new_refresh_token)
    user.refresh_token_expires_at = refresh_expires
    db.add(user)
    db.commit()

    response = RefreshResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )
    return RefreshDataResponse(data=response)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Revoke refresh token."""
    token_hash = hash_refresh_token(payload.refresh_token)
    user = db.query(User).filter(User.refresh_token_hash == token_hash).first()
    if user:
        user.refresh_token_hash = None
        user.refresh_token_expires_at = None
        db.add(user)
        db.commit()
    return None


@router.get("/me", response_model=UserPublicDataResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user."""
    return UserPublicDataResponse(data=UserPublicResponse.model_validate(current_user))
