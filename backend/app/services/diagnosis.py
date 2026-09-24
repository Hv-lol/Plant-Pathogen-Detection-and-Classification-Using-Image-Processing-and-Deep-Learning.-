from __future__ import annotations

import time
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.core.errors import AppError
from app.ml.inference_engine import (
    estimate_severity,
    inference_engine,
    overlay_heatmap,
)
from app.models import (
    Diagnosis,
    Disease,
    Explanation,
    Image,
    ModelVersion,
    Prediction,
    Recommendation,
    SeverityAssessment,
)
from app.models.entities import DiagnosisStatus, ModelVersionStatus
from app.services.quality import assess_image_quality
from app.services.storage import build_object_key, storage_service


RECOMMENDATION_TEMPLATES = {
    "Healthy": [
        {
            "title": "Continue routine scouting",
            "description": "Maintain regular field or greenhouse scouting schedules.",
            "priority": "low",
            "category": "monitoring",
        },
        {
            "title": "Preserve cultural practices",
            "description": "Keep irrigation, sanitation, and canopy management consistent.",
            "priority": "low",
            "category": "prevention",
        },
    ],
    "Bacteria": [
        {
            "title": "Limit spread from symptomatic plants",
            "description": "Avoid working wet canopy; sanitize tools; isolate heavily affected plants for review.",
            "priority": "high",
            "category": "sanitation",
        },
        {
            "title": "Confirm with a plant clinic when needed",
            "description": "Visual bacterial-like symptoms are not species confirmation. Use lab diagnosis for high-value crops.",
            "priority": "high",
            "category": "expert_consultation",
        },
        {
            "title": "Review irrigation and wound entry points",
            "description": "Reduce splash dispersal and mechanical injury where culturally appropriate.",
            "priority": "medium",
            "category": "environmental_management",
        },
    ],
    "Fungi": [
        {
            "title": "Improve airflow and reduce leaf wetness",
            "description": "Canopy management and irrigation timing can slow many fungal symptom complexes.",
            "priority": "high",
            "category": "environmental_management",
        },
        {
            "title": "Remove heavily diseased debris",
            "description": "Sanitation reduces inoculum. Dispose of infected material according to local guidance.",
            "priority": "medium",
            "category": "sanitation",
        },
        {
            "title": "Consult before chemical programs",
            "description": "Fungicide choice and timing require local extension advice and label compliance.",
            "priority": "high",
            "category": "expert_consultation",
        },
    ],
    "Pests": [
        {
            "title": "Identify the pest before treating",
            "description": "This model flags pest-damage patterns, not pest species. Confirm the insect/mite before action.",
            "priority": "high",
            "category": "expert_consultation",
        },
        {
            "title": "Intensify scouting and thresholds",
            "description": "Map infestation hotspots and monitor beneficial insects before broad interventions.",
            "priority": "medium",
            "category": "monitoring",
        },
        {
            "title": "Use cultural and physical controls first",
            "description": "Remove heavily damaged tissue, use barriers/traps where appropriate, and protect beneficials.",
            "priority": "medium",
            "category": "prevention",
        },
    ],
    "Virus": [
        {
            "title": "Manage vectors and planting material",
            "description": "Viral-like symptoms often relate to insect vectors or infected stock. Focus on prevention.",
            "priority": "high",
            "category": "prevention",
        },
        {
            "title": "Remove clearly infected plants when advised",
            "description": "Rogueing can limit spread. Seek local guidance for valuable stands.",
            "priority": "high",
            "category": "sanitation",
        },
        {
            "title": "Seek molecular confirmation for critical cases",
            "description": "Image-based viral category prediction is not a laboratory virus assay.",
            "priority": "high",
            "category": "expert_consultation",
        },
    ],
}


def create_diagnosis(db: Session, user_id: str, image_id: str, crop_id: Optional[str] = None) -> Diagnosis:
    image = db.get(Image, image_id)
    if not image or image.user_id != user_id:
        raise AppError("IMAGE_NOT_FOUND", "Image not found.", 404)
    diagnosis = Diagnosis(
        user_id=user_id,
        image_id=image_id,
        crop_id=crop_id,
        status=DiagnosisStatus.QUEUED.value,
        job_stage="queued",
    )
    db.add(diagnosis)
    db.commit()
    db.refresh(diagnosis)
    return diagnosis


def process_diagnosis(db: Session, diagnosis_id: str) -> Diagnosis:
    diagnosis = (
        db.query(Diagnosis)
        .options(joinedload(Diagnosis.image))
        .filter_by(id=diagnosis_id)
        .first()
    )
    if not diagnosis:
        raise AppError("NOT_FOUND", "Diagnosis not found.", 404)

    try:
        diagnosis.status = DiagnosisStatus.PROCESSING.value
        diagnosis.job_stage = "checking_image_quality"
        db.commit()

        image_bytes = storage_service.get_bytes(diagnosis.image.object_storage_key)
        quality = assess_image_quality(image_bytes)
        diagnosis.quality_status = quality.status
        diagnosis.quality_messages = quality.messages
        diagnosis.image.quality_score = quality.score
        diagnosis.image.width = quality.width
        diagnosis.image.height = quality.height
        db.commit()

        if quality.status == "POOR":
            diagnosis.status = DiagnosisStatus.FAILED.value
            diagnosis.error_code = "POOR_IMAGE_QUALITY"
            diagnosis.error_message = (
                "Please capture another image with better lighting and a clearer view of the leaf."
            )
            diagnosis.job_stage = "failed_quality"
            db.commit()
            return diagnosis

        diagnosis.job_stage = "detecting_plant_leaf"
        db.commit()
        # Plant/leaf gate uses green-area signal already reflected in quality messages.

        diagnosis.job_stage = "analyzing_symptoms"
        db.commit()

        diagnosis.job_stage = "running_disease_classifier"
        db.commit()
        started = time.perf_counter()
        if not inference_engine.ensure_ready():
            raise RuntimeError("MODEL_NOT_AVAILABLE")
        result = inference_engine.predict(image_bytes)
        elapsed_ms = (time.perf_counter() - started) * 1000.0

        mv = (
            db.query(ModelVersion)
            .filter_by(status=ModelVersionStatus.PRODUCTION.value)
            .order_by(ModelVersion.created_at.desc())
            .first()
        )
        diagnosis.model_version_id = mv.id if mv else None
        diagnosis.inference_time_ms = elapsed_ms

        # Clear old predictions if reprocessing
        for p in list(diagnosis.predictions):
            db.delete(p)
        db.flush()

        primary_id = None
        for pred in result["predictions"]:
            disease = db.query(Disease).filter_by(label_key=pred["label"]).first()
            row = Prediction(
                diagnosis_id=diagnosis.id,
                disease_id=disease.id if disease else None,
                label=pred["label"],
                probability=pred["probability"],
                rank=pred["rank"],
            )
            db.add(row)
            db.flush()
            if pred["rank"] == 1:
                primary_id = row.id
                diagnosis.overall_confidence = pred["probability"]

        diagnosis.primary_prediction_id = primary_id

        diagnosis.job_stage = "generating_explanation"
        db.commit()

        top_label = result["predictions"][0]["label"]
        class_index = result["labels"].index(top_label)
        heatmap = inference_engine.gradcam(image_bytes, class_index=class_index)
        overlay = overlay_heatmap(image_bytes, heatmap)
        heat_key = build_object_key(f"heatmaps/{diagnosis.id}", "heatmap.jpg")
        storage_service.put_bytes(heat_key, overlay, "image/jpeg")

        if diagnosis.explanation:
            diagnosis.explanation.heatmap_storage_key = heat_key
            diagnosis.explanation.method = "gradcam"
        else:
            db.add(
                Explanation(
                    diagnosis_id=diagnosis.id,
                    method="gradcam",
                    heatmap_storage_key=heat_key,
                )
            )

        diagnosis.job_stage = "estimating_severity"
        db.commit()
        sev_score, sev_label = estimate_severity(image_bytes)
        if diagnosis.severity:
            diagnosis.severity.severity_score = sev_score
            diagnosis.severity.severity_label = sev_label
        else:
            db.add(
                SeverityAssessment(
                    diagnosis_id=diagnosis.id,
                    severity_score=sev_score,
                    severity_label=sev_label,
                    method="lesion_area_estimate",
                )
            )

        diagnosis.job_stage = "preparing_diagnosis"
        db.commit()

        for rec in list(diagnosis.recommendations):
            db.delete(rec)
        templates = RECOMMENDATION_TEMPLATES.get(
            top_label,
            RECOMMENDATION_TEMPLATES["Fungi"],
        )
        disease = db.query(Disease).filter_by(label_key=top_label).first()
        for t in templates:
            db.add(
                Recommendation(
                    diagnosis_id=diagnosis.id,
                    title=t["title"],
                    description=t["description"],
                    priority=t["priority"],
                    category=t["category"],
                    source_metadata={
                        "type": "knowledge_template",
                        "disease_slug": disease.slug if disease else None,
                        "dataset_label": top_label,
                        "claim_level": "advisory",
                    },
                )
            )

        diagnosis.status = DiagnosisStatus.COMPLETED.value
        diagnosis.job_stage = "completed"
        diagnosis.error_code = None
        diagnosis.error_message = None
        db.commit()
        db.refresh(diagnosis)
        return diagnosis

    except Exception as exc:  # noqa: BLE001
        db.rollback()
        diagnosis.status = DiagnosisStatus.FAILED.value
        diagnosis.job_stage = "failed"
        if str(exc) == "MODEL_NOT_AVAILABLE":
            diagnosis.error_code = "MODEL_NOT_AVAILABLE"
            diagnosis.error_message = "No production model artifact is available."
        else:
            diagnosis.error_code = "INFERENCE_FAILED"
            diagnosis.error_message = "Diagnosis pipeline failed. Please retry."
        db.commit()
        return diagnosis


def get_diagnosis(db: Session, diagnosis_id: str, user_id: str, role: str) -> Diagnosis:
    diagnosis = (
        db.query(Diagnosis)
        .options(
            joinedload(Diagnosis.predictions),
            joinedload(Diagnosis.recommendations),
            joinedload(Diagnosis.severity),
            joinedload(Diagnosis.explanation),
            joinedload(Diagnosis.image),
        )
        .filter_by(id=diagnosis_id)
        .first()
    )
    if not diagnosis:
        raise AppError("NOT_FOUND", "Diagnosis not found.", 404)
    if diagnosis.user_id != user_id and role not in {"ADMIN", "AGRICULTURAL_EXPERT", "RESEARCHER"}:
        raise AppError("FORBIDDEN", "Insufficient permissions.", 403)
    return diagnosis
