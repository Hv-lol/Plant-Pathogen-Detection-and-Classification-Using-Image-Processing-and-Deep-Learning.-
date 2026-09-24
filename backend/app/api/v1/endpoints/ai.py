from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession, RequestId
from app.core.errors import success_body
from app.models import Diagnosis, ModelVersion
from app.models.entities import DiagnosisStatus, ModelVersionStatus
from app.services.diagnosis import get_diagnosis, process_diagnosis
from app.core.database import SessionLocal
from app.core.config import settings
from fastapi import BackgroundTasks

router = APIRouter(prefix="/ai", tags=["ai"])


def _run_job(diagnosis_id: str) -> None:
    db = SessionLocal()
    try:
        process_diagnosis(db, diagnosis_id)
    finally:
        db.close()


@router.post("/inference")
def inference(payload: dict, background_tasks: BackgroundTasks, db: DbSession, user: CurrentUser, request_id: RequestId):
    from app.services.diagnosis import create_diagnosis

    diagnosis = create_diagnosis(db, user.id, payload["image_id"], payload.get("crop_id"))
    if settings.USE_INLINE_JOBS:
        background_tasks.add_task(_run_job, diagnosis.id)
    return success_body(
        {
            "job_id": diagnosis.id,
            "diagnosis_id": diagnosis.id,
            "status": diagnosis.status,
            "stage": diagnosis.job_stage,
        },
        request_id,
    )


@router.get("/jobs/{job_id}")
def job_status(job_id: str, db: DbSession, user: CurrentUser, request_id: RequestId):
    diagnosis = get_diagnosis(db, job_id, user.id, user.role)
    return success_body(
        {
            "job_id": diagnosis.id,
            "diagnosis_id": diagnosis.id,
            "status": diagnosis.status,
            "stage": diagnosis.job_stage,
            "error_code": diagnosis.error_code,
            "error_message": diagnosis.error_message,
        },
        request_id,
    )


@router.get("/models/active")
def active_model(db: DbSession, user: CurrentUser, request_id: RequestId):
    mv = (
        db.query(ModelVersion)
        .filter_by(status=ModelVersionStatus.PRODUCTION.value)
        .order_by(ModelVersion.created_at.desc())
        .first()
    )
    if not mv:
        return success_body(None, request_id)
    return success_body(
        {
            "id": mv.id,
            "version": mv.version,
            "status": mv.status,
            "artifact_uri": mv.artifact_uri,
            "class_labels": mv.class_labels,
            "claim": "visual_symptom_classification",
        },
        request_id,
    )
