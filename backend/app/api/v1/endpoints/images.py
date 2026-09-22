from fastapi import APIRouter, File, UploadFile

from app.api.deps import CurrentUser, DbSession, RequestId
from app.core.config import settings
from app.core.errors import AppError, success_body
from app.models import Image
from app.services.quality import assess_image_quality
from app.services.storage import build_object_key, checksum_bytes, storage_service

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/upload")
async def upload_image(
    db: DbSession,
    user: CurrentUser,
    request_id: RequestId,
    file: UploadFile = File(...),
):
    if file.content_type not in settings.allowed_mimes:
        raise AppError("INVALID_IMAGE", "Uploaded image MIME type is not supported.", 400)
    data = await file.read()
    if len(data) == 0:
        raise AppError("INVALID_IMAGE", "Empty file.", 400)
    if len(data) > settings.MAX_UPLOAD_BYTES:
        raise AppError("IMAGE_TOO_LARGE", "Image exceeds maximum allowed size.", 400)

    quality = assess_image_quality(data)
    key = build_object_key(f"original/{user.id}", file.filename or "upload.jpg")
    storage_service.put_bytes(key, data, file.content_type or "application/octet-stream")

    image = Image(
        user_id=user.id,
        object_storage_key=key,
        filename=file.filename or "upload.jpg",
        mime_type=file.content_type or "application/octet-stream",
        file_size=len(data),
        width=quality.width,
        height=quality.height,
        checksum=checksum_bytes(data),
        quality_score=quality.score,
    )
    db.add(image)
    db.commit()
    db.refresh(image)

    return success_body(
        {
            "id": image.id,
            "filename": image.filename,
            "mime_type": image.mime_type,
            "file_size": image.file_size,
            "width": image.width,
            "height": image.height,
            "quality_score": image.quality_score,
            "quality_status": quality.status,
            "quality_messages": quality.messages,
            "url": storage_service.url_for(image.object_storage_key),
            "created_at": image.created_at.isoformat(),
        },
        request_id,
    )


@router.get("/{image_id}")
def get_image(image_id: str, db: DbSession, user: CurrentUser, request_id: RequestId):
    image = db.get(Image, image_id)
    if not image or image.user_id != user.id:
        raise AppError("NOT_FOUND", "Image not found.", 404)
    return success_body(
        {
            "id": image.id,
            "filename": image.filename,
            "mime_type": image.mime_type,
            "file_size": image.file_size,
            "width": image.width,
            "height": image.height,
            "quality_score": image.quality_score,
            "url": storage_service.url_for(image.object_storage_key),
            "created_at": image.created_at.isoformat(),
        },
        request_id,
    )
