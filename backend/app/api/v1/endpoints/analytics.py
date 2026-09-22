from fastapi import APIRouter
from sqlalchemy import func

from app.api.deps import CurrentUser, DbSession, RequestId
from app.core.errors import success_body
from app.models import Diagnosis

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def overview(db: DbSession, user: CurrentUser, request_id: RequestId):
    q = db.query(Diagnosis).filter_by(user_id=user.id)
    total = q.count()
    completed = q.filter_by(status="COMPLETED").count()
    failed = q.filter_by(status="FAILED").count()

    healthy = 0
    diseased = 0
    conf_sum = 0.0
    conf_n = 0
    for d in q.filter_by(status="COMPLETED").all():
        top = next((p for p in d.predictions if p.rank == 1), None)
        if top:
            if top.label == "Healthy" or top.label.lower() == "healthy":
                healthy += 1
            else:
                diseased += 1
        if d.overall_confidence is not None:
            conf_sum += d.overall_confidence
            conf_n += 1

    return success_body(
        {
            "total_diagnoses": total,
            "healthy_detections": healthy,
            "diseased_detections": diseased,
            "average_confidence": (conf_sum / conf_n) if conf_n else 0.0,
            "completed_diagnoses": completed,
            "failed_diagnoses": failed,
        },
        request_id,
    )
