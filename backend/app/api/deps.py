from typing import Annotated, Optional

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import AppError
from app.core.security import try_decode_token
from app.models import User
from app.models.entities import UserRole

bearer = HTTPBearer(auto_error=False)


def get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer)],
) -> User:
    if credentials is None or not credentials.credentials:
        raise AppError("UNAUTHORIZED", "Authentication required.", 401)
    payload = try_decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise AppError("INVALID_TOKEN", "Access token is invalid or expired.", 401)
    user = db.get(User, payload.get("sub"))
    if not user or not user.is_active:
        raise AppError("UNAUTHORIZED", "User not found or inactive.", 401)
    return user


def get_optional_user(
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer)],
) -> Optional[User]:
    if credentials is None:
        return None
    try:
        return get_current_user(db, credentials)
    except AppError:
        return None


def require_roles(*roles: UserRole):
    allowed = {r.value for r in roles}

    def _checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in allowed and user.role != UserRole.ADMIN.value:
            raise AppError("FORBIDDEN", "Insufficient permissions.", 403)
        return user

    return _checker


DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
RequestId = Annotated[str, Depends(get_request_id)]
