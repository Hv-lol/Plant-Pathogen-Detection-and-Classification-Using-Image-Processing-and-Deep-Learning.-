# PlantGuard AI — Security Architecture

## Principles

- Least privilege RBAC
- Secrets only via environment / secret manager
- Never store plaintext passwords
- Never store large images in PostgreSQL
- Never return internal stack traces to clients
- Audit critical mutations and auth events

## Authentication

- Password hashing: Argon2id (preferred) or bcrypt
- Access JWT (short-lived) + refresh tokens (rotating, revocable)
- Email verification and password reset tokens time-bounded
- OAuth-ready interfaces without hard-coding a single IdP

## Authorization

Roles: `USER` · `RESEARCHER` · `AGRICULTURAL_EXPERT` · `ADMIN`

Resource ownership checks on diagnoses, images, and reports. Research and admin routes require elevated roles.

## Upload security

- Extension allowlist: JPG, JPEG, PNG, WEBP
- MIME sniffing (not client-declared alone)
- Max file size and minimum resolution
- Corrupt-image rejection
- Store outside web root in object storage; serve via signed URLs

## Application hardening

- CORS allowlist
- CSRF strategy for cookie-based flows where applicable
- SQLAlchemy parameterized queries (no string-built SQL)
- XSS-safe frontend rendering
- Rate limiting on auth, upload, inference
- Secure headers (HSTS in prod, CSP, X-Content-Type-Options, etc.)
- Encrypted transport (HTTPS) in deployment

## Audit

Logged actions include: login/logout, diagnosis create/delete, report generation, dataset upload/delete, model deploy/rollback, admin user/role changes, disease content edits.

## Threat notes (non-exhaustive)

| Threat | Mitigation |
|--------|------------|
| Credential stuffing | Rate limits, lockout policy, strong password rules |
| Malicious uploads | MIME/size validation, isolated object storage |
| Model artifact tampering | Checksums + registry approval workflow |
| Privilege escalation | Server-side RBAC on every route |
| Data leakage (ML) | Split validation, near-dupe detection |

See also: API error codes must not leak existence of private resources beyond policy.
