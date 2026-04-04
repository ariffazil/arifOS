# arifOS MCP - Deployment Guide

> **DITEMPA BUKAN DIBERI** — Forged, Not Given  
> Zero-chaos deployment for the Constitutional AI Governance System

---

## Quick Start (For AI Agents)

### Option 1: One-Command Deploy (Recommended)

```bash
# Deploy to staging
python scripts/deploy.py

# Deploy to production
python scripts/deploy.py --environment production

# Dry run (see what would happen)
python scripts/deploy.py --environment production --dry-run
```

### Option 2: GitHub Actions (No Local Setup)

1. Go to **Actions** → **🚀 Deploy arifOS MCP**
2. Click **Run workflow**
3. Select environment (staging/production)
4. Click **Run workflow**

---

## Deployment Environments

| Environment | URL | Auto-Deploy | Approval Required |
|-------------|-----|-------------|-------------------|
| **Staging** | `https://staging.arif-fazil.com` | On push to `main` | No |
| **Production** | `https://arifosmcp.arif-fazil.com` | Manual only | Yes |

---

## Pre-Deployment Checklist

Before deploying to **production**, ensure:

- [ ] All tests pass (`pytest tests/`)
- [ ] Code is committed and pushed
- [ ] You're on `main` branch
- [ ] No `[no-deploy]` in commit message
- [ ] Version bumped in `pyproject.toml` (optional)

---

## Deployment Stages

The deployment system runs 6 constitutional stages:

```
🔷 Stage 1/6: Validating prerequisites
    └─ F11: Verify identity and authorization
    └─ Check SSH connectivity
    └─ Verify git state (clean for production)

🔷 Stage 2/6: Running test suite
    └─ Unit tests (tests/00_unit/)
    └─ Integration tests (tests/01_integration/)
    └─ Constitutional tests (tests/03_constitutional/) ← F1-F13

🔷 Stage 3/6: Creating rollback backup
    └─ F1 (Amanah): Save current state for reversibility
    └─ Store current git SHA

🔷 Stage 4/6: Deploying to server
    └─ Pull latest code
    └─ Build Docker image
    └─ Restart containers

🔷 Stage 5/6: Health checks
    └─ Verify /health endpoint
    └─ Check tool availability
    └─ Validate MCP protocol

🔷 Stage 6/6: Deployment complete
    └─ Save deployment manifest
    └─ Report success
```

---

## Rollback

If deployment fails, automatic rollback occurs:

```bash
# Manual rollback (if auto-rollback disabled)
python scripts/deploy.py --environment production --rollback

# Or SSH to server and:
ssh root@arif-fazil.com
cd /srv/arifosmcp
docker-compose down
git reset --hard <previous-sha>
docker-compose up -d
```

---

## Configuration

### Environment Variables

Create `.env.deploy` in project root:

```bash
# SSH Configuration
DEPLOY_SSH_KEY_PATH=~/.ssh/arifos_deploy
DEPLOY_STAGING_HOST=staging.arif-fazil.com
DEPLOY_PRODUCTION_HOST=arif-fazil.com

# Notifications (optional)
DEPLOY_SLACK_WEBHOOK=https://hooks.slack.com/services/...
DEPLOY_TELEGRAM_TOKEN=your_bot_token
DEPLOY_TELEGRAM_CHAT_ID=your_chat_id
```

### Server Requirements

Target server must have:

- Docker & Docker Compose installed
- Git repository at `/srv/arifosmcp`
- SSH access for deploy user
- Ports 80/443 available

---

## Troubleshooting

### Issue: "Cannot connect to server"

```bash
# Test SSH manually
ssh root@arif-fazil.com echo "OK"

# If fails, check:
# 1. SSH key added to agent: ssh-add -l
# 2. Server is running: ping arif-fazil.com
# 3. Firewall allows SSH
```

### Issue: "Tests failing"

```bash
# Run tests locally first
pytest tests/00_unit/ -v
pytest tests/03_constitutional/ -v  # Critical: F1-F13

# Skip tests in emergency (not recommended)
python scripts/deploy.py --skip-tests
```

### Issue: "Health check failed"

```bash
# Check server logs
ssh root@arif-fazil.com
docker logs arifosmcp_server

# Check container status
docker-compose ps
```

### Issue: "Permission denied"

```bash
# Ensure SSH key is loaded
ssh-add ~/.ssh/arifos_deploy

# Verify key permissions
chmod 600 ~/.ssh/arifos_deploy
```

---

## Constitutional Safety

The deployment system enforces arifOS principles:

| Floor | Deployment Enforcement |
|-------|----------------------|
| **F1** (Amanah) | Automatic rollback on failure |
| **F2** (Truth) | Honest status reporting, no hiding failures |
| **F4** (Clarity) | Clear stage progression and logging |
| **F11** (Command Auth) | SSH key verification, approved environments only |
| **F13** (Sovereign) | Manual approval for production |

---

## API for AI Agents

### Deploy from Python

```python
import subprocess

# Deploy staging
subprocess.run(["python", "scripts/deploy.py", "--environment", "staging"])

# Deploy production with dry-run first
subprocess.run([
    "python", "scripts/deploy.py",
    "--environment", "production",
    "--dry-run"
])
```

### Deploy via GitHub API

```bash
# Trigger workflow via API
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/ariffazil/arifosmcp/actions/workflows/deploy-automated.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "environment": "staging",
      "dry_run": "false"
    }
  }'
```

---

## Deployment Manifests

Every deployment creates a manifest in `deployment/manifests/`:

```json
{
  "environment": "production",
  "git_sha": "a1b2c3d4...",
  "git_branch": "main",
  "deployer": "kimi-cli",
  "timestamp": "2026-03-15T06:30:00+00:00",
  "status": "completed",
  "stages": [...]
}
```

View deployment history:

```bash
ls -la deployment/manifests/
cat deployment/manifests/deploy_production_20260315_063000.json
```

---

## Emergency Procedures

### Complete System Failure

```bash
# 1. SSH to server
ssh root@arif-fazil.com

# 2. Emergency restart
cd /srv/arifosmcp
docker-compose down
docker-compose up -d

# 3. Check status
curl https://arifosmcp.arif-fazil.com/health
```

### Database Recovery

```bash
# Restore from backup
ssh root@arif-fazil.com
cd /srv/arifosmcp
docker-compose exec postgres pg_restore ...
```

---

## Support

- **Issues**: https://github.com/ariffazil/arifosmcp/issues
- **Documentation**: https://arifos.arif-fazil.com
- **Constitutional Questions**: See CONSTITUTION.md

---

*Ditempa Bukan Diberi — Forged, Not Given [ΔΩΨ | ARIF]*
