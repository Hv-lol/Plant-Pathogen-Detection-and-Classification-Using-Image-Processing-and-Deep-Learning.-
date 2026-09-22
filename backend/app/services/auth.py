from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.core.security import (
    create_access_token,
    create_refresh_token_value,
    hash_password,
    hash_token,
    refresh_expiry,
    verify_password,
)
from app.models import RefreshToken, User
from app.models.entities import UserRole
from app.schemas.api import TokenResponse, UserOut


def register_user(db: Session, email: str, password: str, full_name: str) -> User:
    if db.query(User).filter_by(email=email.lower()).first():
        raise AppError("EMAIL_EXISTS", "An account with this email already exists.", 409)
    if len(password) < 8:
        raise AppError("WEAK_PASSWORD", "Password must be at least 8 characters.", 400)
    user = User(
        email=email.lower(),
        password_hash=hash_password(password),
        full_name=full_name.strip(),
        role=UserRole.USER.value,
        is_verified=True,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter_by(email=email.lower()).first()
    if not user or not verify_password(password, user.password_hash):
        raise AppError("INVALID_CREDENTIALS", "Email or password is incorrect.", 401)
    if not user.is_active:
        raise AppError("INACTIVE_USER", "Account is inactive.", 403)
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def issue_tokens(db: Session, user: User) -> TokenResponse:
    access = create_access_token(user.id, {"role": user.role, "email": user.email})
    refresh = create_refresh_token_value()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh),
            expires_at=refresh_expiry(),
        )
    )
    db.commit()
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def refresh_tokens(db: Session, refresh_token: str) -> TokenResponse:
    token_row = (
        db.query(RefreshToken)
        .filter_by(token_hash=hash_token(refresh_token), revoked_at=None)
        .first()
    )
    if not token_row:
        raise AppError("INVALID_REFRESH", "Refresh token is invalid.", 401)
    expires = token_row.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        raise AppError("INVALID_REFRESH", "Refresh token expired.", 401)
    user = db.get(User, token_row.user_id)
    if not user or not user.is_active:
        raise AppError("UNAUTHORIZED", "User not found or inactive.", 401)
    token_row.revoked_at = datetime.now(timezone.utc)
    db.commit()
    return issue_tokens(db, user)


def logout(db: Session, refresh_token: str) -> None:
    token_row = (
        db.query(RefreshToken).filter_by(token_hash=hash_token(refresh_token)).first()
    )
    if token_row and token_row.revoked_at is None:
        token_row.revoked_at = datetime.now(timezone.utc)
        db.commit()


def to_user_out(user: User) -> UserOut:
    return UserOut.model_validate(user)
