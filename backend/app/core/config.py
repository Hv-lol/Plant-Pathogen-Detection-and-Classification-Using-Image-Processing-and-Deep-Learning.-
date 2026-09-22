from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "PlantGuard AI"
    APP_ENV: str = "local"
    API_V1_PREFIX: str = "/api/v1"
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    SECRET_KEY: str = "change-me-to-a-long-random-string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    # Local default: SQLite so the app runs without Docker/Postgres.
    # Production: postgresql+psycopg://...
    DATABASE_URL: str = "sqlite:///./plantguard.db"

    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    USE_INLINE_JOBS: bool = True

    STORAGE_BACKEND: str = "local"  # local | s3
    LOCAL_STORAGE_PATH: str = "./storage"
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "plantguard_minio"
    S3_SECRET_KEY: str = "plantguard_minio_secret"
    S3_BUCKET: str = "plantguard"
    S3_REGION: str = "us-east-1"

    MAX_UPLOAD_BYTES: int = 10_485_760
    ALLOWED_IMAGE_MIME_TYPES: str = "image/jpeg,image/png,image/webp"
    MIN_IMAGE_WIDTH: int = 224
    MIN_IMAGE_HEIGHT: int = 224

    MODEL_REGISTRY_PATH: str = ""  # empty => backend/models next to the package
    DEFAULT_INFERENCE_DEVICE: str = "cpu"
    QUALITY_POOR_THRESHOLD: float = 40.0
    AUTO_BOOTSTRAP_MODEL: bool = True

    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]

    @property
    def allowed_mimes(self) -> List[str]:
        return [m.strip() for m in self.ALLOWED_IMAGE_MIME_TYPES.split(",") if m.strip()]

    @property
    def storage_root(self) -> Path:
        return Path(self.LOCAL_STORAGE_PATH).resolve()

    @property
    def model_root(self) -> Path:
        if self.MODEL_REGISTRY_PATH.strip():
            p = Path(self.MODEL_REGISTRY_PATH)
            if p.is_absolute():
                return p.resolve()
            # Prefer explicit relative path from cwd
            cwd_candidate = (Path.cwd() / p).resolve()
            if cwd_candidate.exists() or p.parts[0] == "backend":
                return cwd_candidate
        # Always fall back to <repo>/backend/models next to this package
        return (Path(__file__).resolve().parents[2] / "models").resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
