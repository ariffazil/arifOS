# DEPLOY_SECRETS.md — Production Secrets Management

> **Constitutional Floor:** F11 (Command Authority)  
> **Motto:** *Ditempa Bukan Diberi — Forged, Not Given*

This document governs the secure management of cryptographic secrets for arifOS MCP production deployments. The `ARIFOS_GOVERNANCE_SECRET` is the root of trust for all authentication contexts.

---

## Table of Contents

1. [Critical Warning](#critical-warning)
2. [Secret Hierarchy](#secret-hierarchy)
3. [Deployment Patterns](#deployment-patterns)
4. [Docker Secrets (Recommended)](#docker-secrets-recommended)
5. [File-Based Secrets](#file-based-secrets)
6. [Environment Variable (Development Only)](#environment-variable-development-only)
7. [Secret Rotation](#secret-rotation)
8. [Verification](#verification)

---

## Critical Warning

⚠️ **NEVER commit secrets to Git.** Secrets committed to version control are permanently compromised.

- `.env` files are in `.gitignore` — keep them there
- Secret files in `secrets/` directory must never be tracked
- Rotate immediately if accidentally exposed

---

## Secret Hierarchy

| Secret | Purpose | Lifespan | Rotation Frequency |
|--------|---------|----------|-------------------|
| `ARIFOS_GOVERNANCE_SECRET` | Root signing key for auth_context JWTs | Permanent (stable) | Annual or on compromise |
| `ARIFOS_SESSION_SECRET` | Session cookie encryption | Permanent | Quarterly |
| `POSTGRES_PASSWORD` | Database access | Deployment | On personnel change |
| `REDIS_PASSWORD` | Cache access | Deployment | On personnel change |
| `QDRANT_API_KEY` | Vector store access | Deployment | On personnel change |

**F11 Continuity Requirement:** `ARIFOS_GOVERNANCE_SECRET` MUST survive container restarts. Ephemeral secrets break session continuity.

---

## Deployment Patterns

### Pattern A: Docker Secrets (Production Recommended)

Use Docker Secrets for swarm/kubernetes deployments. Secrets are mounted as files in `/run/secrets/`.

```yaml
# docker-compose.yml
secrets:
  governance_secret:
    external: true
    name: arifos_governance_secret_v2026

services:
  mcp:
    secrets:
      - source: governance_secret
        target: /run/secrets/governance_secret
    environment:
      - ARIFOS_GOVERNANCE_SECRET_FILE=/run/secrets/governance_secret
```

### Pattern B: File-Based Secrets (Bare Metal/VM)

Store secrets in files outside version control, referenced by path.

```powershell
# Generate once, store securely
New-Item -ItemType Directory -Force -Path "C:\arifos\secrets"
$secret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object { [char]$_ })
$secret | Set-Content -Path "C:\arifos\secrets\governance.secret" -NoNewline
```

```bash
# Linux equivalent
mkdir -p /opt/arifos/secrets
tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 64 > /opt/arifos/secrets/governance.secret
chmod 600 /opt/arifos/secrets/governance.secret
```

### Pattern C: Environment Variable (Development Only)

⚠️ **NOT for production.** Environment variables leak in process listings and logs.

```bash
# .env.development only
ARIFOS_GOVERNANCE_SECRET=dev-secret-do-not-use-in-production
```

---

## Docker Secrets (Recommended)

### Step 1: Create the Secret

```bash
# Generate a cryptographically secure secret
openssl rand -base64 48 | tr -d '\n' > governance.secret

# Create Docker secret (run on swarm manager)
docker secret create arifos_governance_secret_v2026 governance.secret

# Verify
docker secret ls
docker secret inspect arifos_governance_secret_v2026

# Remove local file (now managed by Docker)
rm governance.secret
```

### Step 2: Deploy with Secrets

```yaml
# docker-compose.secrets.yml
version: '3.8'

secrets:
  governance_secret:
    external: true
    name: arifos_governance_secret_v2026
  session_secret:
    external: true
    name: arifos_session_secret_v2026
  postgres_password:
    external: true
    name: arifos_postgres_password

services:
  mcp:
    image: arifos-mcp:latest
    secrets:
      - source: governance_secret
        target: governance_secret
      - source: session_secret
        target: session_secret
    environment:
      - ARIFOS_GOVERNANCE_SECRET_FILE=/run/secrets/governance_secret
      - ARIFOS_SESSION_SECRET_FILE=/run/secrets/session_secret
      - ARIFOS_ENV=production
    
  postgres:
    image: postgres:16-alpine
    secrets:
      - source: postgres_password
        target: postgres_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
```

### Step 3: Deploy

```bash
docker stack deploy -c docker-compose.yml -c docker-compose.secrets.yml arifos
```

---

## File-Based Secrets

### Windows (PowerShell)

```powershell
# scripts/init-secrets.ps1
$secretsDir = "C:\arifos\secrets"
$governanceFile = "$secretsDir\governance.secret"

# Create directory with restricted ACL
New-Item -ItemType Directory -Force -Path $secretsDir
$acl = Get-Acl $secretsDir
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $env:USERNAME, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$acl.SetAccessRule($rule)
Set-Acl $secretsDir $acl

# Generate 64-character alphanumeric secret
$chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
$secret = -join ((1..64) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })

# Write with no newline, restricted permissions
$secret | Set-Content -Path $governanceFile -NoNewline
(Get-Item $governanceFile).IsReadOnly = $true

Write-Host "✓ Governance secret forged at: $governanceFile"
Write-Host "✓ Add to environment: ARIFOS_GOVERNANCE_SECRET_FILE=$governanceFile"
```

### Linux/macOS (Bash)

```bash
#!/bin/bash
# scripts/init-secrets.sh

SECRETS_DIR="/opt/arifos/secrets"
GOVERNANCE_FILE="$SECRETS_DIR/governance.secret"

# Create directory with restricted permissions
sudo mkdir -p "$SECRETS_DIR"
sudo chmod 700 "$SECRETS_DIR"
sudo chown root:root "$SECRETS_DIR"

# Generate 64-character secret
SECRET=$(tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 64)

# Write with restricted permissions
sudo tee "$GOVERNANCE_FILE" > /dev/null <<< "$SECRET"
sudo chmod 600 "$GOVERNANCE_FILE"
sudo chown root:root "$GOVERNANCE_FILE"

echo "✓ Governance secret forged at: $GOVERNANCE_FILE"
echo "✓ Add to environment: ARIFOS_GOVERNANCE_SECRET_FILE=$GOVERNANCE_FILE"
```

---

## Secret Rotation

### Governance Secret Rotation Procedure

⚠️ **WARNING:** Rotating `ARIFOS_GOVERNANCE_SECRET` invalidates all existing auth_context tokens. Coordinate with active sessions.

```bash
# 1. Generate new secret
openssl rand -base64 48 | tr -d '\n' > governance.secret.v2

# 2. Create new Docker secret with version
docker secret create arifos_governance_secret_v2027 governance.secret.v2

# 3. Rolling update to new secret
docker service update --secret-rm governance_secret \
  --secret-add source=arifos_governance_secret_v2027,target=governance_secret \
  arifos_mcp

# 4. Verify all nodes updated
docker service ps arifos_mcp

# 5. Remove old secret (after grace period)
docker secret rm arifos_governance_secret_v2026
```

### Grace Period

Maintain both secrets simultaneously during rotation:

```yaml
# docker-compose.secrets.yml (rotation period)
secrets:
  governance_secret_old:
    external: true
    name: arifos_governance_secret_v2026
  governance_secret_new:
    external: true
    name: arifos_governance_secret_v2027

services:
  mcp:
    secrets:
      - governance_secret_old
      - governance_secret_new
    environment:
      - ARIFOS_GOVERNANCE_SECRET_FILE=/run/secrets/governance_secret_new
      - ARIFOS_GOVERNANCE_SECRET_PREVIOUS_FILE=/run/secrets/governance_secret_old
```

---

## Verification

### Verify Secret Loading

```python
# verify-secrets.py
import os
import secrets

def verify_governance_secret():
    """Verify ARIFOS_GOVERNANCE_SECRET is properly configured."""
    
    # Check file-based secret first (production)
    secret_file = os.environ.get('ARIFOS_GOVERNANCE_SECRET_FILE')
    if secret_file and os.path.exists(secret_file):
        with open(secret_file, 'r') as f:
            secret = f.read().strip()
        print(f"✓ Loaded from file: {secret_file}")
    else:
        # Fall back to environment (dev only)
        secret = os.environ.get('ARIFOS_GOVERNANCE_SECRET')
        if secret:
            print("⚠ Loaded from environment (not recommended for production)")
        else:
            print("✗ ARIFOS_GOVERNANCE_SECRET not configured")
            return False
    
    # Validate entropy
    if len(secret) < 32:
        print(f"✗ Secret too short: {len(secret)} chars (min 32)")
        return False
    
    # Check for high entropy (not predictable)
    unique_chars = len(set(secret))
    if unique_chars < 20:
        print(f"⚠ Low entropy: {unique_chars} unique chars (recommend >20)")
    
    print(f"✓ Secret validated: {len(secret)} chars, {unique_chars} unique")
    return True

if __name__ == "__main__":
    verify_governance_secret()
```

### Health Check Endpoint

The metabolic loop includes secret status in health checks:

```python
# In arifosmcp/core/governance_kernel.py
async def health_check():
    return {
        "status": "healthy",
        "f11_auth": {
            "governance_secret_configured": bool(get_governance_secret()),
            "session_continuity": "stable" if is_secret_persistent() else "EPHEMERAL_WARNING"
        }
    }
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Generate secret | `openssl rand -base64 48 \| tr -d '\n'` |
| Create Docker secret | `docker secret create name file` |
| List secrets | `docker secret ls` |
| Rotate secret | `docker service update --secret-rm old --secret-add new svc` |
| Verify loading | `python scripts/verify-secrets.py` |

---

## Constitutional Compliance

- **F11 (Command Authority):** Secrets provide stable session anchoring
- **F12 (Safety):** Secrets never logged or exposed in error messages
- **F13 (Verification):** Secret integrity verified on every auth_context validation

---

**Version:** 2026.03.12-SEAL  
**Floor:** F11-STABLE  
**Status:** ACTIVE
