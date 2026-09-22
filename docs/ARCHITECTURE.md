# PlantGuard AI — System Architecture

## Product intent

PlantGuard AI is a production-style agricultural intelligence SaaS platform that analyzes plant images for disease and pathogen-*symptom* assessment using computer vision, deep learning, explainable AI, and governed research workflows.

**Scientific constraint:** Visual disease classification from image symptoms must never be presented as laboratory-confirmed pathogen identification unless the dataset and validation protocol explicitly support pathogen-confirmed labels.

## High-level layers

```
CLIENT / ACCESS
  Responsive web, researcher dashboard, admin dashboard,
  mobile capture, REST clients
        │
        ▼
API GATEWAY
  AuthN/AuthZ, validation, rate limiting, logging,
  API versioning (/api/v1), error envelope
        │
        ▼
APPLICATION SERVICES
  Identity, Profile, Images, Diagnosis, Inference,
  Knowledge, Recommendations, Reports, Analytics,
  Datasets, Model Registry, Notifications, Audit
        │
        ▼
AI / ML + DATA PROCESSING
  Quality, detection, classification, severity,
  Grad-CAM, calibration, preprocessing, ETL, evaluation
        │
        ▼
DATA STORAGE
  PostgreSQL · Redis · S3-compatible object storage ·
  Model registry artifacts · Audit logs
        │
        ▼
OBSERVABILITY / DEVOPS
  Docker · CI/CD · monitoring · backups
```

## Logical service map

| Service | Responsibility |
|---------|----------------|
| Identity & Access | Registration, login, JWT access/refresh, RBAC |
| User Profile | Profile fields, preferences, account lifecycle |
| Image Management | Upload validation, object keys, metadata |
| Diagnosis | Job orchestration, result aggregation |
| AI Inference | Active model load, prediction, calibration |
| Explainability | Grad-CAM / Grad-CAM++, overlays |
| Disease Knowledge | Catalog content with source metadata |
| Recommendation | Knowledge-backed, sourced recommendations |
| Report Generation | Async PDF/CSV reports |
| Analytics | Aggregations, trends, exports |
| Dataset Management | Versioning, splits, leakage prevention |
| Model Registry | Lifecycle Dev → Production → Retired |
| Notification | In-app (email-ready) events |
| Audit | Immutable action trail |

## Frontend application map

| Route | Purpose | Access |
|-------|---------|--------|
| `/` | Landing | Public |
| `/login`, `/register`, `/forgot-password`, `/reset-password` | Auth | Public |
| `/dashboard` | User KPIs & recent activity | USER+ |
| `/analyze` | Upload/capture → analysis job | USER+ |
| `/diagnosis/[id]` | Diagnosis result | Owner / expert |
| `/diagnosis/[id]/explain` | Interactive XAI | Owner / expert |
| `/diseases`, `/diseases/[slug]` | Knowledge center | Public/auth |
| `/crops`, `/crops/[id]` | Crop library | Public/auth |
| `/history` | Past diagnoses | USER+ |
| `/reports` | Report generation & download | USER+ |
| `/analytics` | Visual analytics | RESEARCHER+ |
| `/research`, `/research/datasets`, `/research/models` | Research workspace | RESEARCHER+ |
| `/admin`, `/admin/monitoring` | Admin & system health | ADMIN |
| `/settings`, `/profile`, `/help` | Account & docs | USER+ |

## Diagnosis job flow

```
Upload image → create diagnosis job (QUEUED)
  → worker: quality check
  → preprocess
  → plant/leaf gate
  → classify + calibrate confidence
  → generate explanation (+ optional severity)
  → attach knowledge + recommendations
  → COMPLETED | FAILED
Frontend polls GET /ai/jobs/{job_id} (or future websocket/SSE)
```

Job states: `QUEUED` · `PROCESSING` · `COMPLETED` · `FAILED` · `CANCELLED`

## Technology stack

- **Frontend:** Next.js, React, TypeScript, Tailwind, TanStack Query, RHF, Zod
- **Backend:** FastAPI, Pydantic, SQLAlchemy, Alembic, Celery, Redis, JWT/OAuth2-ready
- **Data:** PostgreSQL, Redis, S3-compatible object storage, optional pgvector
- **ML:** PyTorch, torchvision, OpenCV, Albumentations, scikit-learn, MLflow
- **Infra:** Docker Compose, Nginx, GitHub Actions

## Related documents

- [DATABASE.md](./DATABASE.md)
- [API.md](./API.md)
- [ML_PIPELINE.md](./ML_PIPELINE.md)
- [DEPLOYMENT.md](./DEPLOYMENT.md)
- [SECURITY.md](./SECURITY.md)
- [RESEARCH_METHODOLOGY.md](./RESEARCH_METHODOLOGY.md)
