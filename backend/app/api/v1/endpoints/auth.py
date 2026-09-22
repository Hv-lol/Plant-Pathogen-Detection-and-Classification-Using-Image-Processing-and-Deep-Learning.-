from fastapi import APIRouter, Request

from app.api.deps import CurrentUser, DbSession, RequestId
from app.core.errors import success_body
from app.schemas.api import LoginRequest, RefreshRequest, RegisterRequest
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: RegisterRequest, db: DbSession, request_id: RequestId):
    user = auth_service.register_user(db, payload.email, payload.password, payload.full_name)
    tokens = auth_service.issue_tokens(db, user)
    return success_body(
        {"user": auth_service.to_user_out(user).model_dump(), "tokens": tokens.model_dump()},
        request_id,
    )


@router.post("/login")
def login(payload: LoginRequest, db: DbSession, request_id: RequestId):
    user = auth_service.authenticate(db, payload.email, payload.password)
    tokens = auth_service.issue_tokens(db, user)
    return success_body(
        {"user": auth_service.to_user_out(user).model_dump(), "tokens": tokens.model_dump()},
        request_id,
    )


@router.post("/refresh")
def refresh(payload: RefreshRequest, db: DbSession, request_id: RequestId):
    tokens = auth_service.refresh_tokens(db, payload.refresh_token)
    return success_body(tokens.model_dump(), request_id)


@router.post("/logout")
def logout(payload: RefreshRequest, db: DbSession, request_id: RequestId, user: CurrentUser):
    auth_service.logout(db, payload.refresh_token)
    return success_body({"logged_out": True}, request_id)
