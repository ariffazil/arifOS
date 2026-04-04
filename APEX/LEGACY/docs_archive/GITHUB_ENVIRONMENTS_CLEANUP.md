# GitHub Environments Cleanup — arifOS

**Date:** 2026-02-22  
**Authority:** 888_JUDGE

## Current Status

### Repository Secrets (Active) ✅
These are configured at repository level and work for all workflows:
- `DOCKERHUB_TOKEN` — Docker Hub authentication
- `DOCKERHUB_USERNAME` — Docker Hub username
- `RAILWAY_TOKEN` — Legacy Railway deployment (can be removed)
- `VPS_HOST` — 72.62.71.199
- `VPS_SSH_KEY` — SSH private key for VPS access
- `VPS_USERNAME` — root

### Environments (Needs Cleanup)
**Stale/Delete:**
- `000-arifOS / arifOS-pr-113` — Old PR preview
- `000-arifOS / arifOS-pr-138-...` — Old PR preview  
- `000-arifOS / arifOS-pr-61` — Old PR preview
- `000-arifOS / arifOS-pr-64` — Old PR preview
- `amusing-insight / production` — Legacy environment
- `aware-perfection / production` — Legacy environment
- `enchanting-success / production` — Legacy environment
- `peaceful-hope / production` — Legacy environment
- `arifOS / production` — Duplicate
- `000-arifOS / production` — Duplicate
- `copilot` — Unused

**Keep & Configure:**
- `production` — Main production environment ✅ Configured
- `pypi` — PyPI publishing environment ✅ Configured
- `github-pages` — GitHub Pages deployment (auto-managed) ✅
- `staging` — Staging environment (optional)

## Required Actions

### 1. Delete Stale Environments (Manual)
Go to: https://github.com/ariffazil/arifOS/settings/environments

Delete these environments (click gear icon → Delete):
- All `000-arifOS / arifOS-pr-*` entries
- All `* / production` entries except the main `production`
- `copilot`

### 2. Configure Production Environment
**URL:** https://github.com/ariffazil/arifOS/settings/environments/production

**Settings:**
- ✅ **Required reviewers:** 1 (yourself)
- ✅ **Wait timer:** 0 minutes
- ✅ **Deployment branches:** `main` only (Protected branches only)

**Secrets to Add:** (via GitHub UI)
1. `VPS_HOST` = `72.62.71.199`
2. `VPS_USERNAME` = `root`
3. `VPS_SSH_KEY` = [Your SSH private key]

### 3. Configure PyPI Environment
**URL:** https://github.com/ariffazil/arifOS/settings/environments/pypi

**Settings:**
- ✅ **Required reviewers:** 1 (yourself)
- ✅ **Wait timer:** 0 minutes
- ✅ **Deployment branches:** `main` only

**Secrets to Add:**
1. `PYPI_API_TOKEN` = [Your PyPI token]

### 4. Optional: Staging Environment
If you want a staging environment:
- Create new environment: `staging`
- Same settings as production
- Point to staging VPS/subdomain

## Workflow Updates Required

Update `.github/workflows/deploy.yml` to use environment:

```yaml
jobs:
  deploy_vps:
    name: Deploy to VPS
    needs: selftest
    runs-on: ubuntu-latest
    environment: production  # <-- ADD THIS
    steps:
      # ... rest of deployment
```

This enables:
- Manual approval gates before production deploy
- Environment-specific secrets
- Deployment history tracking

## Cleanup Verification

After cleanup, you should have only:
1. `production` — VPS deployment target
2. `pypi` — PyPI package publishing
3. `github-pages` — Documentation site (auto)
4. `staging` — (Optional) Staging deployment

**All stale PR environments should be deleted.**

## Floor Compliance

- **F1 Amanah:** Environments add approval gates = safer deployments
- **F2 Truth:** Clear separation of prod/staging = verifiable states  
- **F11 Authority:** Required reviewers = human oversight on production
- **F4 ΔS:** Cleanup reduces entropy in CI/CD configuration

---

**Status:** 🔴 **ACTION REQUIRED** — Manual cleanup needed via GitHub UI
**Next Step:** Go to https://github.com/ariffazil/arifOS/settings/environments and delete stale entries
