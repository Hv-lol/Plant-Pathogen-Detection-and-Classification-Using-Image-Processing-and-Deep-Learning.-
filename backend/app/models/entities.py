from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    BigInteger,
    String,
    Text,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> str:
    return str(uuid4())


class UserRole(str, Enum):
    USER = "USER"
    RESEARCHER = "RESEARCHER"
    AGRICULTURAL_EXPERT = "AGRICULTURAL_EXPERT"
    ADMIN = "ADMIN"


class DiagnosisStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ModelVersionStatus(str, Enum):
    DEVELOPMENT = "development"
    VALIDATION = "validation"
    CANDIDATE = "candidate"
    APPROVED = "approved"
    PRODUCTION = "production"
    RETIRED = "retired"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    users: Mapped[list["User"]] = relationship(
        secondary="user_roles", back_populates="roles"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), default=UserRole.USER.value, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    roles: Mapped[list[Role]] = relationship(
        secondary="user_roles", back_populates="users"
    )
    images: Mapped[list["Image"]] = relationship(back_populates="user")
    diagnoses: Mapped[list["Diagnosis"]] = relationship(back_populates="user")


class UserRoleLink(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"), primary_key=True)


class PlantSpecies(Base):
    __tablename__ = "plant_species"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    common_name: Mapped[str] = mapped_column(String(255), nullable=False)
    scientific_name: Mapped[str] = mapped_column(String(255), nullable=False)
    family: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Crop(Base):
    __tablename__ = "crops"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    scientific_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    diseases: Mapped[list["Disease"]] = relationship(
        secondary="crop_diseases", back_populates="crops"
    )


class Disease(Base):
    __tablename__ = "diseases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pathogen_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    pathogen_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    symptoms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prevention: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    management_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    label_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    crops: Mapped[list[Crop]] = relationship(
        secondary="crop_diseases", back_populates="diseases"
    )


class CropDisease(Base):
    __tablename__ = "crop_diseases"
    __table_args__ = (UniqueConstraint("crop_id", "disease_id"),)

    crop_id: Mapped[str] = mapped_column(ForeignKey("crops.id"), primary_key=True)
    disease_id: Mapped[str] = mapped_column(ForeignKey("diseases.id"), primary_key=True)


class Image(Base):
    __tablename__ = "images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    object_storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    checksum: Mapped[str] = mapped_column(String(128), nullable=False)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="images")
    diagnoses: Mapped[list["Diagnosis"]] = relationship(back_populates="image")


class Model(Base):
    __tablename__ = "models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    architecture: Mapped[str] = mapped_column(String(128), nullable=False)
    framework: Mapped[str] = mapped_column(String(64), default="pytorch")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    versions: Mapped[list["ModelVersion"]] = relationship(back_populates="model")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    model_id: Mapped[str] = mapped_column(ForeignKey("models.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    dataset_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    artifact_uri: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precision: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recall: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    f1_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    inference_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        String(64), default=ModelVersionStatus.DEVELOPMENT.value
    )
    class_labels: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    model: Mapped[Model] = relationship(back_populates="versions")


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    image_id: Mapped[str] = mapped_column(ForeignKey("images.id"), nullable=False)
    crop_id: Mapped[Optional[str]] = mapped_column(ForeignKey("crops.id"), nullable=True)
    plant_species_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("plant_species.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), default=DiagnosisStatus.QUEUED.value)
    primary_prediction_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    overall_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    inference_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_version_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("model_versions.id"), nullable=True
    )
    quality_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    quality_messages: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    job_stage: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    user: Mapped[User] = relationship(back_populates="diagnoses")
    image: Mapped[Image] = relationship(back_populates="diagnoses")
    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates="diagnosis", cascade="all, delete-orphan"
    )
    explanation: Mapped[Optional["Explanation"]] = relationship(
        back_populates="diagnosis", uselist=False, cascade="all, delete-orphan"
    )
    severity: Mapped[Optional["SeverityAssessment"]] = relationship(
        back_populates="diagnosis", uselist=False, cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="diagnosis", cascade="all, delete-orphan"
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    diagnosis_id: Mapped[str] = mapped_column(ForeignKey("diagnoses.id"), nullable=False)
    disease_id: Mapped[Optional[str]] = mapped_column(ForeignKey("diseases.id"), nullable=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)

    diagnosis: Mapped[Diagnosis] = relationship(back_populates="predictions")
    disease: Mapped[Optional[Disease]] = relationship()


class Explanation(Base):
    __tablename__ = "explanations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    diagnosis_id: Mapped[str] = mapped_column(
        ForeignKey("diagnoses.id"), unique=True, nullable=False
    )
    method: Mapped[str] = mapped_column(String(64), default="gradcam")
    heatmap_storage_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    mask_storage_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    diagnosis: Mapped[Diagnosis] = relationship(back_populates="explanation")


class SeverityAssessment(Base):
    __tablename__ = "severity_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    diagnosis_id: Mapped[str] = mapped_column(
        ForeignKey("diagnoses.id"), unique=True, nullable=False
    )
    severity_score: Mapped[float] = mapped_column(Float, nullable=False)
    severity_label: Mapped[str] = mapped_column(String(64), nullable=False)
    method: Mapped[str] = mapped_column(String(64), default="lesion_area_estimate")

    diagnosis: Mapped[Diagnosis] = relationship(back_populates="severity")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    diagnosis_id: Mapped[str] = mapped_column(ForeignKey("diagnoses.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(32), default="medium")
    category: Mapped[str] = mapped_column(String(64), default="monitoring")
    source_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    diagnosis: Mapped[Diagnosis] = relationship(back_populates="recommendations")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(64), default="info")
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    diagnosis_id: Mapped[Optional[str]] = mapped_column(ForeignKey("diagnoses.id"), nullable=True)
    storage_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    report_type: Mapped[str] = mapped_column(String(64), default="diagnosis_pdf")
    status: Mapped[str] = mapped_column(String(32), default="queued")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
