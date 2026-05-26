# Docker Profiles

| File | Status | Purpose |
|------|--------|---------|
| `../../Dockerfile` | ✅ CANONICAL | Production build — used by `docker-compose.yml` and CI |
| `Dockerfile.hardened` | 🔬 Aspirational | Zero-shell, read-only FS, no-root isolation. Not yet wired into CI. Reference for future hardening pass. |
| `Dockerfile.unified` | 📦 Archived | April 2026 UV-based unified stack experiment. Superseded by canonical `Dockerfile`. Has `PORT=8080` drift. |

Use `Dockerfile` at repo root for all builds.
