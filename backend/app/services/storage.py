import hashlib
from pathlib import Path
from typing import BinaryIO, Optional
from uuid import uuid4

from app.core.config import settings
from app.core.errors import AppError


class StorageService:
    def __init__(self) -> None:
        self.backend = settings.STORAGE_BACKEND
        self.root = settings.storage_root
        if self.backend == "local":
            self.root.mkdir(parents=True, exist_ok=True)

    def put_bytes(self, key: str, data: bytes, content_type: str) -> str:
        if self.backend == "local":
            path = self.root / key
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            return key
        raise AppError("STORAGE_ERROR", "S3 backend not configured in this environment.", 500)

    def put_fileobj(self, key: str, fileobj: BinaryIO, content_type: str) -> str:
        data = fileobj.read()
        return self.put_bytes(key, data, content_type)

    def get_bytes(self, key: str) -> bytes:
        if self.backend == "local":
            path = self.root / key
            if not path.exists():
                raise AppError("NOT_FOUND", "Object not found.", 404)
            return path.read_bytes()
        raise AppError("STORAGE_ERROR", "S3 backend not configured in this environment.", 500)

    def exists(self, key: str) -> bool:
        if self.backend == "local":
            return (self.root / key).exists()
        return False

    def url_for(self, key: str) -> str:
        # Served via API proxy endpoint
        return f"/api/v1/storage/{key}"

    def absolute_path(self, key: str) -> Path:
        return self.root / key


def checksum_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_object_key(prefix: str, filename: str) -> str:
    safe = filename.replace("\\", "_").replace("/", "_")
    return f"{prefix}/{uuid4().hex}_{safe}"


storage_service = StorageService()
