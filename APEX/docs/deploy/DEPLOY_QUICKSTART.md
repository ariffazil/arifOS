# arifOS Deployment - Quick Start for AI Agents

> **Zero-chaos deployment in 3 commands or less**

---

## 🚀 TL;DR - Deploy Now

### Option A: One Command (Staging)
```bash
make deploy-staging
```

### Option B: Three Steps (Production - Safe)
```bash
# Step 1: Check readiness
python scripts/deploy_check.py

# Step 2: Dry run
make deploy-dry-run

# Step 3: Deploy
make deploy-production
```

### Option C: GitHub Actions (No Local Setup)
```bash
# Trigger via GitHub CLI
make deploy-gh

# Or go to: https://github.com/ariffazil/arifosmcp/actions/workflows/deploy-automated.yml
```

---

## 📋 Pre-Deploy Checklist (Auto-Validated)

The deployment system automatically checks:

| Check | Auto-Fix | Fails Deployment |
|-------|----------|------------------|
| Git working directory clean | No | Yes (production) |
| On main branch | No | Warning only |
| Tests passing | No | Yes |
| Docker available | N/A | No |
| Deploy script valid | No | Yes |

**To check manually:**
```bash
python scripts/deploy_check.py
```

---

## 🛡️ Safety Features

### Automatic Rollback
If deployment fails, system automatically rolls back to previous version.

### Health Checks
- Validates `/health` endpoint
- Confirms tool availability
- Tests MCP protocol

### Constitutional Enforcement
| Floor | Deployment Safety |
|-------|-------------------|
| **F1** (Amanah) | Automatic rollback on failure |
| **F2** (Truth) | Honest status reporting |
| **F11** (Command Auth) | SSH key verification |
| **F13** (Sovereign) | Manual approval for production |

---

## 📁 Deployment Files Reference

```
arifosmcp/
├── scripts/
│   ├── deploy.py              # Main deployment orchestrator
│   ├── deploy_check.py        # Pre-flight readiness checker
│   └── rebuild-strategy.sh    # Legacy strategy analyzer
├── .github/workflows/
│   └── deploy-automated.yml   # CI/CD pipeline
├── DEPLOY.md                  # Full documentation
├── DEPLOY_QUICKSTART.md       # This file
└── Makefile                   # Shortcuts (make deploy-*)
```

---

## 🎯 Common Scenarios

### "I just fixed a bug, deploy to staging"
```bash
make deploy-staging
```

### "I need to deploy to production carefully"
```bash
# 1. Verify tests pass
pytest tests/ -x

# 2. Check readiness
python scripts/deploy_check.py

# 3. See what would happen
make deploy-dry-run

# 4. Actually deploy
make deploy-production

# 5. Verify it's working
make deploy-verify
```

### "Something went wrong, rollback!"
```bash
# Automatic rollback happens on failure
# Manual rollback:
ssh root@arif-fazil.com "cd /srv/arifosmcp && docker-compose restart"
```

### "I'm an AI agent, what's the safest path?"
```bash
# Always do this for production:
1. python scripts/deploy_check.py    # Verify ready
2. make deploy-dry-run               # Preview changes
3. IF dry-run looks good:
     make deploy-production
4. make deploy-verify                # Confirm success
```

---

## 🔧 Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| "Uncommitted changes" | `git add . && git commit -m "Pre-deploy"` |
| "Tests failing" | `pytest tests/ -v` to see failures |
| "SSH failed" | `ssh-add ~/.ssh/arifos_deploy` |
| "Health check failed" | Check server logs: `make logs` |
| "Deploy script not found" | Ensure you're in project root |

---

## 📊 Deployment Stages

```
🔷 Stage 1/6: Validating prerequisites
   └─ Git state, SSH access, branch check

🔷 Stage 2/6: Running test suite  
   └─ Unit, Integration, Constitutional (F1-F13)

🔷 Stage 3/6: Creating rollback backup
   └─ Save current state for reversibility

🔷 Stage 4/6: Deploying to server
   └─ Pull code, build, restart

🔷 Stage 5/6: Health checks
   └─ Verify endpoints, tools, protocol

🔷 Stage 6/6: Deployment complete
   └─ Save manifest, report success
```

---

## 🌍 Environment URLs

| Environment | URL | Deploy Command |
|-------------|-----|----------------|
| Staging | https://staging.arif-fazil.com | `make deploy-staging` |
| Production | https://arifosmcp.arif-fazil.com | `make deploy-production` |

---

## 💡 Tips for AI Agents

1. **Always check first**: Run `python scripts/deploy_check.py` before any deploy
2. **Staging first**: Always deploy to staging before production
3. **Dry run**: Use `make deploy-dry-run` to preview production changes
4. **Verify after**: Always run `make deploy-verify` to confirm success
5. **Don't panic**: Automatic rollback happens if something goes wrong

---

## 🆘 Emergency Contacts

- **Server Down**: `ssh root@arif-fazil.com "docker-compose restart"`
- **Full Rollback**: See DEPLOY.md "Emergency Procedures" section
- **Constitutional Issues**: Check CONSTITUTION.md F1-F13

---

*Ditempa Bukan Diberi — Forged, Not Given [ΔΩΨ | ARIF]*
