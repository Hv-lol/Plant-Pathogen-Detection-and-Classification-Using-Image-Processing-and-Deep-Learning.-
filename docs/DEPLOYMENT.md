# PlantGuard AI — Deployment Architecture

## Local development (Docker Compose)

Services:

| Service | Role |
|---------|------|
| `frontend` | Next.js app |
| `api` | FastAPI application |
| `worker` | Celery workers (inference, reports, training jobs) |
| `postgres` | Primary database |
| `redis` | Cache + broker |
| `minio` | S3-compatible object storage |
| `nginx` | Reverse proxy (optional local TLS termination) |
| `mailhog` (optional) | Email catcher for auth flows |

## Environment configuration

All secrets and connection strings come from environment variables (see `.env.example`). Never commit real secrets.

## CI/CD pipeline

```
Lint → Type check → Unit tests → Integration tests → Build → Security checks → Docker build
```

GitHub Actions workflows live under `infra/ci-cd/`.

## Cloud readiness

Compose maps cleanly to managed cloud services:

- Containers → ECS/GKE/AKS or equivalent
- PostgreSQL → managed Postgres
- Redis → managed Redis
- MinIO → S3 / Blob / GCS
- Nginx → ALB/Cloud Load Balancing + ACM/managed certs

## Health checks

- API: `/health` and `/ready` (DB + Redis + storage reachability)
- Worker: Celery ping / custom heartbeat
- Frontend: HTTP 200 on root

## Backups

- PostgreSQL: scheduled logical dumps + PITR where available
- Object storage: versioning + lifecycle policies
- Model artifacts: checksummed copies in registry storage

## Performance targets

- Track API p95 for non-inference routes
- Track average + p95 inference latency per model version
- Paginate large lists; use thumbnails in history/analytics
- Generate large reports asynchronously
