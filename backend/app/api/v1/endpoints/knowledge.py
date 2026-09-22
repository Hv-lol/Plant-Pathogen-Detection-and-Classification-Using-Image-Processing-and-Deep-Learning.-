from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import or_

from app.api.deps import DbSession, RequestId
from app.core.errors import AppError, success_body
from app.models import Crop, Disease

router = APIRouter(tags=["knowledge"])


@router.get("/diseases")
def list_diseases(
    db: DbSession,
    request_id: RequestId,
    q: Optional[str] = Query(default=None),
):
    query = db.query(Disease)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Disease.name.ilike(like), Disease.slug.ilike(like)))
    rows = query.order_by(Disease.name.asc()).all()
    return success_body(
        [
            {
                "id": d.id,
                "name": d.name,
                "slug": d.slug,
                "description": d.description,
                "pathogen_type": d.pathogen_type,
                "pathogen_name": d.pathogen_name,
                "symptoms": d.symptoms,
                "cause": d.cause,
                "prevention": d.prevention,
                "management_notes": d.management_notes,
                "source_metadata": d.source_metadata,
            }
            for d in rows
        ],
        request_id,
    )


@router.get("/diseases/{slug}")
def get_disease(slug: str, db: DbSession, request_id: RequestId):
    d = db.query(Disease).filter_by(slug=slug).first()
    if not d:
        raise AppError("NOT_FOUND", "Disease not found.", 404)
    return success_body(
        {
            "id": d.id,
            "name": d.name,
            "slug": d.slug,
            "description": d.description,
            "pathogen_type": d.pathogen_type,
            "pathogen_name": d.pathogen_name,
            "symptoms": d.symptoms,
            "cause": d.cause,
            "prevention": d.prevention,
            "management_notes": d.management_notes,
            "source_metadata": d.source_metadata,
        },
        request_id,
    )


@router.get("/crops")
def list_crops(db: DbSession, request_id: RequestId):
    rows = db.query(Crop).order_by(Crop.name.asc()).all()
    return success_body(
        [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "scientific_name": c.scientific_name,
                "description": c.description,
            }
            for c in rows
        ],
        request_id,
    )


@router.get("/crops/{crop_id}")
def get_crop(crop_id: str, db: DbSession, request_id: RequestId):
    c = db.get(Crop, crop_id)
    if not c:
        # try slug
        c = db.query(Crop).filter_by(slug=crop_id).first()
    if not c:
        raise AppError("NOT_FOUND", "Crop not found.", 404)
    return success_body(
        {
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "scientific_name": c.scientific_name,
            "description": c.description,
            "diseases": [{"id": d.id, "name": d.name, "slug": d.slug} for d in c.diseases],
        },
        request_id,
    )
