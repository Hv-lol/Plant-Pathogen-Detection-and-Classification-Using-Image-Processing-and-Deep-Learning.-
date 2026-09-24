from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.api.deps import CurrentUser
from app.core.config import settings
from app.core.errors import AppError

router = APIRouter(prefix="/storage", tags=["storage"])


@router.get("/{object_path:path}")
def get_object(object_path: str, user: CurrentUser):
    # Auth required; object paths are unguessable UUIDs. Ownership checks are
    # enforced at image/diagnosis endpoints for listings.
    root = settings.storage_root.resolve()
    path = (root / object_path).resolve()
    if not path.is_relative_to(root) or not path.exists() or not path.is_file():
        raise AppError("NOT_FOUND", "Object not found.", 404)
    return FileResponse(path)
