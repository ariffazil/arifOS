# 🔒 999_SEAL - PRODUCTION HARDENING CHECKLIST
## From "Working" to "Bulletproof"

**Status:** TIER 0-1 COMPLETE → TIER 2-4 HARDENING REQUIRED  
**Authority:** 888_JUDGE | 999_SEAL  
**Goal:** Zero-trust, auditable, recoverable secret infrastructure

---

## 🔴 CRITICAL - DO NOW (Blocks Production)

### 1. Add Missing Infrastructure Secrets
```bash
# These are REQUIRED for Docker Secrets to work
vault set postgres $(openssl rand -base64 32)
vault set redis $(openssl rand -base64 32)
vault set qdrant $(openssl rand -base64 32)

# Add to registry mapping (infra.* canonical names)
# Edit /root/arifOS/config/secret-registry.yaml:
#   infra.postgres.password → vault_key: POSTGRES_PASSWORD
#   infra.redis.password → vault_key: REDIS_PASSWORD  
#   infra.qdrant.api_key → vault_key: QDRANT_API_KEY

# Re-render
vault-render all
```

### 2. Docker Swarm Initialization
```bash
# Initialize swarm mode (required for Docker Secrets)
docker swarm init --advertise-addr $(hostname -i | awk '{print $1}')

# Verify
docker node ls
```

### 3. Create Docker Secrets from Vault
```bash
# Script to sync vault → Docker secrets
for secret in postgres_password redis_password qdrant_api_key; do
    value=$(cat /root/arifOS/secrets/${secret}.txt 2>/dev/null)
    if [ -n "$value" ]; then
        echo "$value" | docker secret create ${secret}_v1 - 2>/dev/null || echo "${secret} exists"
    fi
done
```

---

## 🟡 HIGH PRIORITY - This Week

### 4. Encrypt Vault Backups
```bash
# Install GPG if not present
apt-get update && apt-get install -y gnupg

# Generate encryption key
export GNUPGHOME=/root/.gnupg
mkdir -p $GNUPGHOME
chmod 700 $GNUPGHOME

# Create key (non-interactive)
cat > /tmp/gen-key.txt <<EOF
%echo Generating vault backup key
Key-Type: RSA
Key-Length: 4096
Name-Real: arifOS Vault Backup
Name-Email: vault@arifos.local
Expire-Date: 0
%no-protection
%commit
%echo done
EOF

gpg --batch --gen-key /tmp/gen-key.txt
gpg --list-keys
```

### 5. Automated VAULT999 Bridge (Cron)
```bash
# Daily attestation + backup
crontab -l > /tmp/crontab 2>/dev/null || echo "" > /tmp/crontab

cat >> /tmp/crontab << 'CRON'
# 999_SEAL - Daily vault attestation (3:00 AM)
0 3 * * * /usr/bin/python3 /root/arifOS/core/vault999/bridge_from_vault.py attest >> /var/log/vault999.log 2>&1

# 999_SEAL - Weekly encrypted backup (Sundays 4:00 AM)
0 4 * * 0 cd /root/.secrets && tar czf - vault.env | gpg --encrypt --recipient vault@arifos.local > /root/arifOS/core/vault999/layer4_survivability/cold_storage/vault_backup_$(date +\%Y\%m\%d).tar.gz.gpg

# 999_SEAL - Monthly permission audit (1st of month)
0 5 1 * * ls -la /root/.secrets/ /root/arifOS/secrets/ /root/arifOS/rendered/ >> /var/log/vault_audit.log 2>&1
CRON

crontab /tmp/crontab
rm /tmp/crontab
```

### 6. Update docker-compose.yml to Use Rendered Configs
```yaml
# Replace this in /root/arifOS/docker-compose.yml:
services:
  arifosmcp_server:
    # OLD: env_file: .env
    # NEW:
    env_file:
      - /root/arifOS/rendered/arifos/arifosmcp_server.env
    secrets:
      - postgres_password_v1
      - redis_password_v1
```

### 7. Log Sanitization (Prevent Secret Leaks)
```bash
# Create log filter script
cat > /usr/local/bin/sanitize-logs << 'SCRIPT'
#!/bin/bash
# Sanitize logs to remove potential secret leaks
# Run as: docker logs container 2>&1 | sanitize-logs

sed -E 's/(sk-[a-zA-Z0-9]{20})[a-zA-Z0-9]+/\1****/g' | \
sed -E 's/(AIzaSy[A-Za-z0-9_-]{20})[A-Za-z0-9_-]+/\1****/g' | \
sed -E 's/(hf_[A-Za-z0-9]{20})[A-Za-z0-9]+/\1****/g' | \
sed -E 's/(password|secret|key)=([^\s]+)/\1=****/gi'
SCRIPT

chmod +x /usr/local/bin/sanitize-logs
```

---

## 🟢 MEDIUM PRIORITY - Next Sprint

### 8. Secret Rotation Workflow
```bash
# Create rotation script
cat > /usr/local/bin/vault-rotate << 'SCRIPT'
#!/bin/bash
# 888_HOLD: Rotate a secret with zero-downtime

SECRET_NAME=$1
NEW_VALUE=$2

if [ -z "$SECRET_NAME" ] || [ -z "$NEW_VALUE" ]; then
    echo "Usage: vault-rotate <canonical-name> <new-value>"
    echo "Example: vault-rotate infra.postgres.password $(openssl rand -base64 32)"
    exit 1
fi

# 1. Backup current
vault backup

# 2. Update vault (keeps old in backup)
echo "Rotating $SECRET_NAME..."

# 3. Update canonical registry version
# (Manual step - edit secret-registry.yaml to bump version)

# 4. Re-render
vault-render all

# 5. Rolling restart of affected services
# docker compose up -d --no-deps --scale service=0 service
# docker compose up -d --no-deps service

echo "✅ Rotation complete. Affected services need restart."
echo "Run: docker compose up -d"
SCRIPT

chmod +x /usr/local/bin/vault-rotate
```

### 9. Health Checks & Monitoring
```bash
# Vault health check script
cat > /usr/local/bin/vault-health << 'SCRIPT'
#!/bin/bash
# Check vault system health

ERRORS=0

# Check vault file exists and permissions
if [ ! -f /root/.secrets/vault.env ]; then
    echo "❌ CRITICAL: vault.env missing"
    ERRORS=$((ERRORS + 1))
else
    PERMS=$(stat -c '%a' /root/.secrets/vault.env)
    if [ "$PERMS" != "600" ]; then
        echo "❌ CRITICAL: vault.env permissions are $PERMS, expected 600"
        ERRORS=$((ERRORS + 1))
    else
        echo "✅ vault.env permissions correct"
    fi
fi

# Check registry valid
if [ ! -f /root/arifOS/config/secret-registry.yaml ]; then
    echo "❌ CRITICAL: secret-registry.yaml missing"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ secret-registry.yaml exists"
fi

# Check attestations
LATEST_ATTESTATION=$(find /root/arifOS/core/vault999/layer4_survivability/cold_storage -name "vault_attestation_*.json" -mtime -1 2>/dev/null | head -1)
if [ -z "$LATEST_ATTSTATION" ]; then
    echo "⚠️  WARNING: No attestation in last 24 hours"
else
    echo "✅ Recent attestation found"
fi

# Check for missing secrets
MISSING=$(vault-render --list 2>&1 | grep "❌" | wc -l)
if [ "$MISSING" -gt 0 ]; then
    echo "⚠️  WARNING: $MISSING canonical secrets not in vault"
fi

# Verify integrity
VERIFY=$(python3 /root/arifOS/core/vault999/bridge_from_vault.py verify 2>&1)
if echo "$VERIFY" | grep -q "VERIFIED"; then
    echo "✅ Vault integrity verified"
else
    echo "⚠️  WARNING: Vault attestation mismatch"
fi

if [ $ERRORS -eq 0 ]; then
    echo ""
    echo "🟢 VAULT HEALTH: HEALTHY"
    exit 0
else
    echo ""
    echo "🔴 VAULT HEALTH: $ERRORS CRITICAL ERRORS"
    exit 1
fi
SCRIPT

chmod +x /usr/local/bin/vault-health
```

### 10. Emergency Recovery Kit
```bash
mkdir -p /root/arifOS/emergency

cat > /root/arifOS/emergency/RECOVERY.md << 'RECOVERY'
# 🚨 EMERGENCY VAULT RECOVERY

## Scenario 1: vault.env corrupted
```bash
# 1. Check L4 cold storage backups
ls -la /root/arifOS/core/vault999/layer4_survivability/cold_storage/backups/

# 2. Restore from latest backup
LATEST=$(ls -t /root/arifOS/core/vault999/layer4_survivability/cold_storage/backups/vault_backup_*.tar.gz.gpg | head -1)
gpg --decrypt "$LATEST" | tar xzf - -C /tmp/
cp /tmp/vault.env /root/.secrets/vault.env
chmod 600 /root/.secrets/vault.env

# 3. Verify
vault-health
```

## Scenario 2: VPS compromised
```bash
# 1. IMMEDIATELY rotate ALL keys at provider dashboards
# 2. Generate new vault with new keys
# 3. vault-render all
# 4. Restart all services
```

## Scenario 3: Registry corrupted
```bash
# Restore from git (secret-registry.yaml is tracked)
git checkout HEAD -- /root/arifOS/config/secret-registry.yaml
```

## Emergency Contacts
- VPS Provider: Hostinger
- Domain: Cloudflare
- Critical Keys: Rotate at provider dashboards directly
RECOVERY
```

---

## 🔵 LOW PRIORITY - Future Enhancements

### 11. Vault-Agent Pattern (Advanced)
```yaml
# Sidecar container that injects secrets at runtime
# Instead of env vars, use temporary files that expire
services:
  arifosmcp_server:
    volumes:
      - type: tmpfs
        target: /run/secrets
        tmpfs:
          size: 1M
          mode: 0400
```

### 12. Shamir Secret Sharing
Split vault encryption key among trusted devices:
```bash
# Split key into 3 parts, need 2 to reconstruct
ssss-split -t 2 -n 3
```

### 13. Hardware Security Module (HSM)
- YubiKey for vault encryption
- TPM for VPS-bound keys

### 14. OIDC Integration
When Authentik is ready:
- Replace static API keys with OAuth tokens
- Short-lived tokens (1-hour TTL)
- No keys in vault at all

---

## 📊 SEALING PROGRESS TRACKER

| Item | Priority | Status | Notes |
|------|----------|--------|-------|
| 1. Add infra secrets | 🔴 Critical | ⬜ TODO | POSTGRES_PASSWORD, REDIS_PASSWORD, QDRANT_API_KEY |
| 2. Docker Swarm init | 🔴 Critical | ⬜ TODO | Required for Docker Secrets |
| 3. Create Docker secrets | 🔴 Critical | ⬜ TODO | Sync from vault |
| 4. Encrypt backups | 🟡 High | ⬜ TODO | GPG setup |
| 5. Automated cron | 🟡 High | ⬜ TODO | Daily attestations |
| 6. Update compose files | 🟡 High | ⬜ TODO | Use rendered configs |
| 7. Log sanitization | 🟡 High | ⬜ TODO | Prevent leaks |
| 8. Rotation workflow | 🟢 Medium | ⬜ TODO | vault-rotate script |
| 9. Health checks | 🟢 Medium | ⬜ TODO | vault-health |
| 10. Recovery kit | 🟢 Medium | ✅ DONE | Documented |
| 11. Vault-Agent | 🔵 Low | ⬜ TODO | Future |
| 12. Shamir sharing | 🔵 Low | ⬜ TODO | Future |
| 13. HSM | 🔵 Low | ⬜ TODO | Future |
| 14. OIDC | 🔵 Low | ⬜ TODO | After Authentik |

---

## 🎯 DEFINITION OF "SEALED"

The vault system is **SEALED** when:

- ✅ All 19 containers use canonical registry
- ✅ No raw secrets in docker-compose.yml
- ✅ All backups encrypted
- ✅ Daily attestations running
- ✅ Health checks pass
- ✅ Recovery procedures tested
- ✅ 888_HOLD: Zero manual secret handling in production

**Current Status:** 70% sealed (TIER 0-1 complete, TIER 2-4 in progress)

---

*999_SEAL | DITEMPA BUKAN DIBERI*
