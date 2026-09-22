# PlantGuard AI — Dependency Map

## Runtime dependency graph

```
Browser (Next.js)
  → Nginx (optional)
    → FastAPI API
      → PostgreSQL
      → Redis
      → MinIO/S3
      → Celery workers
           → Redis broker
           → PostgreSQL
           → MinIO/S3
           → PyTorch model artifacts
```

## Package map

### Frontend
- next, react, react-dom
- typescript
- (Phase 4+) tailwindcss, @tanstack/react-query, react-hook-form, zod, framer-motion, recharts

### Backend
- fastapi, uvicorn, pydantic, pydantic-settings
- sqlalchemy, alembic, psycopg
- celery, redis
- python-jose, passlib[argon2]
- boto3 (S3/MinIO)
- pytest, httpx

### ML research (`ml/`)
- torch, torchvision
- opencv-python, albumentations
- scikit-learn, numpy, pandas
- mlflow, optuna

### Infrastructure
- postgres:16, redis:7, minio, nginx
- GitHub Actions for CI

## Inter-service contracts

| Producer | Consumer | Contract |
|---------|----------|----------|
| Frontend | API | REST `/api/v1` + OpenAPI schemas |
| API | Worker | Celery task names + job IDs |
| Worker | Object storage | Key conventions under `plantguard/` |
| Worker | Model registry | `model_versions.artifact_uri` + checksum |
| API | Postgres | SQLAlchemy models / Alembic revisions |

## What must not couple

- Frontend must not import ML code
- UI must not hard-code disease predictions
- Training notebooks must not write directly to production tables without registry APIs
- Secrets must not be baked into images
