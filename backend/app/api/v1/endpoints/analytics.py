from fastapi import APIRouter
from sqlalchemy import case, func

from app.api.deps import CurrentUser, DbSession, RequestId
from app.core.errors import success_body
from app.models import Diagnosis, Prediction

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def overview(db: DbSession, user: CurrentUser, request_id: RequestId):
    q = db.query(Diagnosis).filter_by(user_id=user.id)
    total = q.count()
    completed = q.filter_by(status="COMPLETED").count()
    failed = q.filter_by(status="FAILED").count()

    avg_confidence = (
        db.query(func.avg(Diagnosis.overall_confidence))
        .filter(
            Diagnosis.user_id == user.id,
            Diagnosis.status == "COMPLETED",
            Diagnosis.overall_confidence.isnot(None),
        )
        .scalar()
    ) or 0.0

    healthy_count, top_prediction_count = (
        db.query(
            func.sum(case((Prediction.label == "Healthy", 1), else_=0)),
            func.count(Prediction.id),
        )
        .join(Diagnosis, Diagnosis.id == Prediction.diagnosis_id)
        .filter(
            Diagnosis.user_id == user.id,
            Diagnosis.status == "COMPLETED",
            Prediction.rank == 1,
        )
        .one()
    )
    healthy = healthy_count or 0
    diseased = (top_prediction_count or 0) - healthy

    return success_body(
        {
            "total_diagnoses": total,
            "healthy_detections": healthy,
            "diseased_detections": diseased,
            "average_confidence": avg_confidence,
            "completed_diagnoses": completed,
            "failed_diagnoses": failed,
        },
        request_id,
    )
