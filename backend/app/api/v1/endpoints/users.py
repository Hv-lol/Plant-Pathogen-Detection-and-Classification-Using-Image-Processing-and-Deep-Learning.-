from fastapi import APIRouter

from app.api.deps import CurrentUser, RequestId
from app.core.errors import success_body
from app.services.auth import to_user_out

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def me(user: CurrentUser, request_id: RequestId):
    return success_body(to_user_out(user).model_dump(), request_id)
