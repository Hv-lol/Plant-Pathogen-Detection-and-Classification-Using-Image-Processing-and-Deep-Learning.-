"""PlantGuard AI FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.errors import AppError, app_error_handler, http_error_handler
from app.core.logging import configure_logging
from app.ml.inference_engine import inference_engine
from app.services.seed import seed_database
import app.models  # noqa: F401 — register models


configure_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    if settings.AUTO_BOOTSTRAP_MODEL:
        try:
            inference_engine.ensure_ready()
        except Exception:  # noqa: BLE001
            pass
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(HTTPException, http_error_handler)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "service": "PlantGuard AI API",
        "docs": "/docs",
        "health": "/health",
        "frontend": settings.FRONTEND_URL,
        "message": "Open the frontend at http://localhost:3000 — this port is the API only.",
    }


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "plantguard-api"}


@app.get("/ready", tags=["system"])
def ready() -> dict[str, object]:
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        db_ok = True
    except Exception:  # noqa: BLE001
        db_ok = False
    return {
        "status": "ready" if db_ok else "degraded",
        "database": db_ok,
        "model_ready": inference_engine.is_ready,
        "storage_backend": settings.STORAGE_BACKEND,
    }
