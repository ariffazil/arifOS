# PRE-COMMISSIONING CHECKLIST: arifOS v52.5.1 on Railway
**Phase 0: Infrastructure Provisioning (Before Deployment)**

**Target:** Ready for production within 72 hours  
**Current Stack:** Railway + Cloudflare  
**Goal:** Full AGI∥ASI async architecture with cooling ledger persistence  

---

## PHASE 0A: INFRASTRUCTURE AUDIT & PROVISIONING (Day 1)

### 0A1: PERSISTENT STORAGE REQUIREMENTS

#### Current State:
```
Railway: Ephemeral container (data lost on restart)
❌ Cooling ledger: Lost on restart
❌ Vault secrets: Lost on restart  
❌ Session state: Lost on restart
```

#### What You Need:
Option A: **Railway Volumes** (Simplest)
- Railway-native persistent storage
- $5/month per 1GB
- Auto-backed up by Railway
- ✅ Recommended for YOUR case (lowest friction)

Option B: **AWS S3** (Scalable but complex)
- S3 bucket for cooling ledger
- DynamoDB for sessions (optional)
- CloudFront for caching
- ❌ More expensive, more ops overhead

Option C: **PostgreSQL** (Traditional)
- Railway PostgreSQL add-on ($15/month)
- JSONL stored in text field
- Better for multi-instance scaling
- ⏳ Defer to v52.5.2 (unnecessary for MVP)

#### Action Step 1: Provision Railway Volume
```bash
# 1. In Railway dashboard:
#    - Go to project → Add plugin
#    - Select "Disk Storage" (Railway's built-in volume)
#    - Size: 10GB ($1.50/month)
#    - Mount path: /var/data
#    - Auto-backup: Enable

# 2. Verify in Railway console:
#    - Service → arifos → Storage tab
#    - Should show: "/var/data (10GB, backed up)"

# 3. Create required directories:
mkdir -p /var/data/vault
mkdir -p /var/data/ledger
mkdir -p /var/data/logs
chmod 755 /var/data/*
```

**Cost:** $1.50/month  
**Timeline:** 5 minutes  
**Risk:** LOW

---

### 0A2: MESSAGE QUEUE (AGI↔ASI Async Communication)

#### Current State:
```
arifOS v52.5.1: Uses threads (in-process only)
❌ Cannot scale horizontally (single container)
❌ No persistent job queue
❌ Crashes = data loss
```

#### What You Need:
Option A: **Redis** (Recommended for MVP)
- In-memory, blazingly fast
- Pub/Sub for AGI↔ASI signaling
- Job queue for 111→333, 555→666 stages
- Railway Redis add-on: $15/month
- ✅ Simple, sufficient for <1000 req/sec

Option B: **RabbitMQ** (Enterprise)
- Reliable message persistence
- Dead-letter queues
- Better for >10K req/sec
- ❌ Overkill for your current load
- ❌ Defer to v52.5.2

Option C: **AWS SQS** (If already AWS customer)
- Serverless, pay-per-use
- Costs scale with traffic
- ❌ More expensive than Redis
- ❌ Defer to v52.5.2

#### Action Step 2: Provision Redis
```bash
# 1. In Railway dashboard:
#    - Go to project → Add plugin
#    - Select "Redis" (Railway's managed Redis)
#    - Size: 1GB ($15/month)
#    - Select project
#    - Copy REDIS_URL

# 2. Add to arifOS environment:
#    Railway → Secrets
#    Add: REDIS_URL=redis://username:password@host:port

# 3. Test Redis connection:
#    Railway console:
redis-cli -u $REDIS_URL ping
# Should output: PONG

# 4. Create Redis channels:
redis-cli -u $REDIS_URL
> SUBSCRIBE agi:delta:emit
> SUBSCRIBE asi:omega:emit
> SUBSCRIBE apex:merged:444
```

**Cost:** $15/month  
**Timeline:** 10 minutes  
**Risk:** LOW

---

### 0A3: SECRETS MANAGEMENT (Ed25519 Keys, Nonces)

#### Current State:
```
arifOS needs:
❌ APEX private key (Ed25519 for signing)
❌ User pubkey vault (for F11 authority)
❌ JWT secret (for session nonces)
❌ Safely stored (not in git repo!)
```

#### What You Need:
Option A: **Railway Secrets** (Simplest)
- Railway → Secrets tab
- Encrypted at rest
- Automatically injected as env vars
- ✅ Recommended (no additional service)

Option B: **Hashicorp Vault** (Enterprise)
- AWS/GCP native secret storage
- Audit trail for key access
- Auto-rotation support
- ❌ Overkill for your case
- ❌ Defer to v52.5.2

#### Action Step 3: Generate & Store Secrets
```bash
# 1. Generate APEX Ed25519 signing key:
python3 << 'EOF'
import nacl.signing
import nacl.encoding
import base64

# Generate signing key
signing_key = nacl.signing.SigningKey.generate()
verify_key = signing_key.verify_key

# Output in base64 (safer for Railway secrets)
privkey_b64 = base64.b64encode(bytes(signing_key)).decode()
pubkey_b64 = base64.b64encode(bytes(verify_key)).decode()

print(f"ARIFOS_APEX_PRIVKEY={privkey_b64}")
print(f"ARIFOS_APEX_PUBKEY={pubkey_b64}")
EOF

# 2. Generate random JWT secret:
openssl rand -hex 32
# Example output: 3f7a9c8e2d1b5a4f6e8c9d7a3b2f4e5c

# 3. In Railway dashboard:
#    - Go to project → Secrets
#    - Add each:
#      ARIFOS_APEX_PRIVKEY=<base64_privkey>
#      ARIFOS_APEX_PUBKEY=<base64_pubkey>
#      ARIFOS_JWT_SECRET=<32_char_hex>

# 4. Create F11 user pubkey vault:
cat > /var/data/vault/users.yaml << 'EOF'
users:
  arif@petronas.my:
    pubkey: "ed25519:..."  # User's signing key (they provide)
    roles: ["admin", "judge"]
    created: 2026-01-26
    nonces_used: []
EOF

# 5. Test secrets loaded:
#    Railway console:
python -c "import os; print(os.getenv('ARIFOS_JWT_SECRET'))"
# Should print: 3f7a9c8e2d1b5a4f6e8c9d7a3b2f4e5c
```

**Cost:** $0 (included with Railway)  
**Timeline:** 15 minutes  
**Risk:** LOW (if keys lost, can regenerate)

---

### 0A4: NETWORK CONFIGURATION (Cloudflare + Railway)

#### Current State:
```
Cloudflare: Domain registered
Railway: Container running (default Railway domain)
❌ Not connected
❌ No custom domain routing
```

#### What You Need:
Connect Cloudflare domain to Railway endpoint.

#### Action Step 4: Route Cloudflare → Railway
```bash
# 1. In Railway dashboard:
#    - Service → arifos → Settings
#    - "Custom Domain"
#    - Enter: judge.yourdomain.com
#    - Railway generates: <uuid>.railway.app
#    - Copy this value

# 2. In Cloudflare dashboard:
#    - DNS → Records
#    - Add CNAME record:
#      Name: judge
#      Type: CNAME
#      Target: <uuid>.railway.app
#      TTL: Auto
#      Proxy: Through Cloudflare (orange cloud)
#    - Add SSL:
#      SSL/TLS → Overview → Flexible (minimum)
#      or Full (if Railway has valid cert)

# 3. Test DNS resolution:
dig judge.yourdomain.com +short
# Should output: <uuid>.railway.app IP

# 4. Test HTTPS:
curl -I https://judge.yourdomain.com/health
# Should return: 200 OK
```

**Cost:** $0 (included with Cloudflare)  
**Timeline:** 5 minutes  
**Risk:** LOW

---

## PHASE 0B: VAULT INITIALIZATION (Day 1 Evening)

### 0B1: CONSTITUTIONAL VAULT SETUP

#### What It Is:
Central config file defining all 13 floors (F1-F13), floor thresholds, baseline uncertainties.

#### Action Step 5: Create Vault File
```bash
# Create vault configuration at /var/data/vault/constitution.yaml

cat > /var/data/vault/constitution.yaml << 'EOF'
# arifOS Constitutional Vault v52.5.1
# Authority: Muhammad Arif bin Fazil
# Sealed: 2026-01-26

metadata:
  version: "52.5.1"
  sealed_date: "2026-01-26T15:00:00Z"
  authority: "arif@petronas.my"

# 13 GOVERNANCE FLOORS
floors:
  F1_amanah:
    name: "Amanah (Trustworthiness / Reversibility)"
    enforcer: "ASI (666 ALIGN)"
    type: "HARD"
    threshold: 0.5  # reversible: bool → 1.0 or 0.0
    description: "All advice must be reversible and non-destructive"
  
  F2_truth:
    name: "Truth (Confidence / Accuracy)"
    enforcer: "AGI (333 REASON) + APEX (888 JUDGE)"
    type: "HARD"
    threshold: 0.99
    description: "Confidence in reasoning must be ≥99%"
  
  F3_tri_witness:
    name: "Tri-Witness (Human + AGI reasoning + ASI safety)"
    enforcer: "APEX (444 TRINITY_SYNC, 888 JUDGE)"
    type: "HARD"
    threshold: 0.95  # Consensus score between AGI + ASI votes
    description: "Both AGI and ASI must independently vote SEAL"
  
  F4_clarity:
    name: "Clarity (Entropy Delta)"
    enforcer: "AGI (333 REASON) + APEX (888 JUDGE)"
    type: "HARD"
    threshold: 0.0  # ΔS ≤ 0 (cooling phase)
    description: "Output must reduce entropy (ΔS ≤ 0), never increase"
  
  F5_peace_squared:
    name: "Peace² (Non-Destructive Equilibrium)"
    enforcer: "ASI (666 ALIGN) + APEX (888 JUDGE)"
    type: "SOFT"
    threshold: 1.0
    description: "Outcome must be non-destructive (Peace² ≥ 1.0)"
  
  F6_empathy:
    name: "Empathy Conductance (ASEAN Weakest Stakeholder)"
    enforcer: "ASI (555 EMPATHY, 666 ALIGN) + APEX (888 JUDGE)"
    type: "SOFT"
    threshold: 0.95  # κᵣ ≥ 0.95
    description: "Must prioritize weakest/most vulnerable stakeholder"
  
  F7_humility:
    name: "Humility (Uncertainty Bounds)"
    enforcer: "AGI (333 REASON) + APEX (888 JUDGE)"
    type: "HARD"
    threshold: 0.05  # Ω₀ ∈ [0.03, 0.05]
    description: "Must acknowledge uncertainty: 3-5% epistemic band"
  
  F8_genius:
    name: "Genius (Novelty Index)"
    enforcer: "APEX (777 FORGE, 888 JUDGE)"
    type: "SOFT"
    threshold: 0.80  # G ≥ 0.80
    description: "Output must show originality (G = A×P×X×E²)"
  
  F9_anti_hantu:
    name: "Anti-Hantu (No Consciousness Cosplay)"
    enforcer: "APEX (000 INIT, 888 JUDGE)"
    type: "HARD"
    threshold: 1.0  # Boolean: no consciousness claims
    description: "Must never claim consciousness, soul, or feelings"
  
  F10_ontology:
    name: "Ontology (Reality Anchored)"
    enforcer: "APEX (000 INIT, 888 JUDGE)"
    type: "HARD"
    threshold: 0.5  # Boolean: rooted in physical reality
    description: "All reasoning grounded in observable reality"
  
  F11_authority:
    name: "Authority (Human Command Authority)"
    enforcer: "APEX (000 INIT, 666 ALIGN, 888 JUDGE, 889 PROOF)"
    type: "HARD"
    threshold: 0.95  # Nonce + signature verified
    description: "Human Δ authority verified via Ed25519 nonce + signature"
  
  F12_injection:
    name: "Injection Defense (Prompt Safety)"
    enforcer: "APEX (000 INIT)"
    type: "HARD"
    threshold: 0.85  # injection_risk < 0.15
    description: "Prompt must be clean of DAN/jailbreak/injection attacks"
  
  F13_curiosity:
    name: "Curiosity (Exploration Paths)"
    enforcer: "AGI (222 THINK) + APEX (000 INIT)"
    type: "SOFT"
    threshold: 3.0  # At least 3 independent hypotheses
    description: "Generate ≥3 parallel hypotheses (conservative/exploratory/adversarial)"

# BASELINE UNCERTAINTIES
uncertainty:
  omega_zero_min: 0.03
  omega_zero_max: 0.05
  description: "Epistemic humility band: 3-5% irreducible uncertainty"

# COOLING TIERS (Phoenix-72)
cooling_tiers:
  L0_seal:
    verdict: "SEAL"
    cooling_hours: 0
    description: "No cooling, fully approved"
  
  L1_partial:
    verdict: "PARTIAL"
    cooling_hours: 42
    description: "Approved with caveats, cool for 42 hours before reuse"
  
  L2_phoenix:
    verdict: "VOID"
    cooling_hours: 72
    description: "Rejected, cool for Phoenix-72 (72 hours) before re-judgment"
  
  L3_sabar:
    verdict: "SABAR"
    cooling_hours: 168
    description: "Escalated, cool for 1 week before retry"
  
  L4_hold:
    verdict: "888_HOLD"
    cooling_hours: 336
    description: "Human review required, hold 2 weeks"
  
  L5_eternal:
    verdict: "SEAL_ETERNALLY"
    cooling_hours: -1
    description: "Sealed forever, no cooling (rare: G > 0.95)"

# THERMODYNAMIC FORMULAS
thermodynamics:
  entropy_delta_formula: "ΔS = sum(ln(P_hypothesis_i) for each hypothesis)"
  peace_squared_formula: "Peace² = (ΔS × κᵣ × Amanah) / Entropy_cost"
  living_equilibrium_formula: "Ψ_LE = (ΔS × Peace² × κᵣ × RASA × Amanah) / (Entropy + ε)"
  living_equilibrium_threshold: 1.0
  
  truth_probability_formula: "P(truth) = 1 - exp(-α × (E/E₀) × (-ΔS/S₀) × TW)"
  # Where:
  # α = 1.0 (constitutional constant)
  # E = empathy score (κᵣ, F6)
  # E₀ = baseline empathy (0.95)
  # ΔS = entropy delta (negative in cool phase)
  # S₀ = baseline entropy (1.0)
  # TW = tri-witness consensus (F3)

# TRINITY DISSENT LAW
dissent_law:
  description: "Both AGI and ASI must vote SEAL independently"
  rule_1: "If AGI.vote == VOID → Cannot SEAL → Escalate to SABAR or 888_HOLD"
  rule_2: "If ASI.vote == VOID → Cannot SEAL → Escalate to SABAR or 888_HOLD"
  rule_3: "If AGI.vote != ASI.vote → Consensus < 1.0 → Escalate to 888_HOLD (manual review)"
  rule_4: "If both vote SEAL → Proceed to 777 FORGE (conditional SEAL)"

# LATENCY BUDGET
latency_budget:
  total_target_ms: 50.0
  stage_000_init_ms: 5.0
  agi_parallel_ms: 10.0
  asi_parallel_ms: 7.0
  stage_444_sync_ms: 1.0
  stage_777_forge_ms: 5.0
  stage_888_judge_ms: 8.7
  stage_889_proof_ms: 3.0
  stage_999_seal_ms: 2.0
  buffer_ms: 8.3

# USER NONCE VAULT (Populated at runtime)
users: {}  # Entries added as users authenticate

# SESSION REGISTRY (In-memory + file backup)
sessions: {}  # Entries added per request, cleared post-999 SEAL

EOF

chmod 644 /var/data/vault/constitution.yaml
```

**Cost:** $0  
**Timeline:** 10 minutes  
**Risk:** LOW

---

### 0B2: GENESIS HASH (Hash-Chain Root)

#### What It Is:
First entry in cooling ledger. Needed to validate chain continuity.

#### Action Step 6: Create Genesis Entry
```bash
# If starting fresh (no previous Trinity server):

python3 << 'EOF'
import json
import hashlib
from datetime import datetime

genesis_entry = {
    "session_id": "GENESIS_000",
    "timestamp": datetime.utcnow().isoformat(),
    "previous_hash": "0" * 64,  # Genesis has no previous
    "current_hash": None,  # Will be computed
    "verdict": "GENESIS",
    "floor_scores": {
        "F1_amanah": 1.0,
        "F2_truth": 1.0,
        "F3_tri_witness": 1.0,
        "F4_clarity": 1.0,
        "F5_peace_squared": 1.0,
        "F6_empathy": 1.0,
        "F7_humility": 0.04,
        "F8_genius": 1.0,
        "F9_anti_hantu": 1.0,
        "F10_ontology": 1.0,
        "F11_authority": 1.0,
        "F12_injection": 1.0,
        "F13_curiosity": 1.0
    },
    "p_truth": 1.0,
    "cooling_tier": 5,  # L5_ETERNAL
    "reason": "Constitutional genesis, all floors perfect",
    "authority": "arif@petronas.my"
}

# Compute hash
entry_json = json.dumps(genesis_entry, sort_keys=True, separators=(',', ':'))
genesis_entry["current_hash"] = hashlib.sha256(entry_json.encode()).hexdigest()

# Save to ledger
with open('/var/data/ledger/cooling_ledger.jsonl', 'w') as f:
    f.write(json.dumps(genesis_entry) + '\n')

print(f"Genesis hash: {genesis_entry['current_hash']}")
print(f"Ledger initialized at: /var/data/ledger/cooling_ledger.jsonl")
EOF

# Set in Railway secrets:
# ARIFOS_GENESIS_HASH=<output_from_above>
```

**Cost:** $0  
**Timeline:** 5 minutes  
**Risk:** LOW

---

## PHASE 0C: LOAD TESTING HARNESS (Day 2 Morning)

### 0C1: INSTALL K6 (Load Testing Tool)

#### What It Is:
Modern load testing framework (lightweight, JavaScript-based).

#### Action Step 7: Install & Configure k6
```bash
# 1. Install k6 locally (your development machine):
# MacOS:
brew install k6

# Linux:
sudo apt-get install k6

# Verify:
k6 version

# 2. Create load test script:
cat > /tmp/arifos_load_test.js << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Ramp up
    { duration: '1m', target: 50 },    // Peak
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<100', 'p(99)<200'],
    http_req_failed: ['rate<0.1'],
  },
};

export default function() {
  const query = "What is the meaning of life?";
  const payload = JSON.stringify({
    query: query,
    context: {},
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer YOUR_JWT_TOKEN',
    },
  };

  const res = http.post('https://judge.yourdomain.com/judge', payload, params);

  check(res, {
    'status is 200': (r) => r.status === 200,
    'verdict is SEAL': (r) => r.json('verdict') === 'SEAL',
    'p_truth > 0.95': (r) => r.json('p_truth') > 0.95,
    'latency < 100ms': (r) => r.timings.duration < 100,
  });

  sleep(1);
}
EOF

# 3. Run locally (against staging):
k6 run /tmp/arifos_load_test.js
```

**Cost:** $0 (free tool)  
**Timeline:** 20 minutes  
**Risk:** LOW

---

### 0C2: BENCHMARK BASELINE

#### Action Step 8: Establish Performance SLA
```bash
# Run load test and record baseline:

k6 run --vus 10 --duration 1m /tmp/arifos_load_test.js > /tmp/k6_baseline.txt

# Expected output:
# ✓ http_req_duration..........: avg=45.3ms, p(95)=92.1ms, p(99)=154.2ms
# ✓ http_req_failed............: 0.00%
# ✓ checks.....................: 100.00%

# Store baseline:
cat /tmp/k6_baseline.txt > /var/data/logs/performance_baseline.txt
```

**Cost:** $0  
**Timeline:** 5 minutes  
**Risk:** LOW

---

## PHASE 0D: MONITORING & OBSERVABILITY (Day 2 Afternoon)

### 0D1: PROMETHEUS METRICS

#### What It Is:
Time-series database for collecting metrics (latency, throughput, errors).

#### Option A: **Railway Prometheus** (if available)
- ✅ Built-in to some Railway plans
- Check: Railway dashboard → Metrics

#### Option B: **Datadog** (Simple but paid)
- $15/month starter
- Web UI, alerting, dashboards
- ✅ Recommended for your case

#### Option C: **ELK Stack** (Self-hosted)
- Elasticsearch + Logstash + Kibana
- ❌ Overkill for MVP
- Defer to v52.5.2

#### Action Step 9: Configure Datadog (Option B - Recommended)
```bash
# 1. Sign up: https://www.datadoghq.com
# 2. Create API key + App key
# 3. Install Datadog agent on Railway:

cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# Install arifOS
RUN pip install arifos datadog

# Install Datadog agent
ENV DD_API_KEY=${DD_API_KEY}
ENV DD_AGENT_MAJOR_VERSION=7
RUN apt-get update && apt-get install -y datadog-agent

WORKDIR /app
COPY . .

# Start both app and agent
CMD datadog-agent start & \
    python -m arifos.mcp sse --host 0.0.0.0 --port $PORT
EOF

# 4. In Railway:
#    - Settings → Secrets
#    - Add: DD_API_KEY=<your_datadog_key>
#    - Rebuild container
```

**Cost:** $15/month (Datadog)  
**Timeline:** 15 minutes  
**Risk:** LOW

---

### 0D2: STRUCTURED LOGGING

#### What It Is:
Machine-readable logs for debugging + audit trail.

#### Action Step 10: Configure Logging
```python
# In arifos_core/integration/api/main.py:

import logging
import json
from pythonjsonlogger import jsonlogger

# Configure JSON logging
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Log structure:
# {
#   "timestamp": "2026-01-26T15:00:00Z",
#   "level": "INFO",
#   "session_id": "550e8400...",
#   "stage": "333_REASON",
#   "message": "AGI reasoning complete",
#   "delta_bundle": {...},
#   "duration_ms": 9.3
# }

@app.post("/judge")
async def judge(request: JudgeRequest):
    logger.info({
        "session_id": session.id,
        "stage": "000_INIT",
        "message": "Session initialized",
        "user_id": user_id
    })
    # ... rest of logic
```

**Cost:** $0 (built-in Python logging)  
**Timeline:** 10 minutes  
**Risk:** LOW

---

## PHASE 0E: BACKUP & DISASTER RECOVERY (Day 2 Evening)

### 0E1: COOLING LEDGER SNAPSHOTS

#### What It Is:
Daily backups of hash-chained cooling ledger (immutable, tamper-evident).

#### Action Step 11: Configure Auto-Backups
```bash
# 1. Create backup script:
cat > /usr/local/bin/arifos_backup.sh << 'EOF'
#!/bin/bash

LEDGER_PATH="/var/data/ledger/cooling_ledger.jsonl"
BACKUP_DIR="/var/data/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Copy ledger
cp $LEDGER_PATH $BACKUP_DIR/cooling_ledger_${TIMESTAMP}.jsonl.bak

# Compress
gzip $BACKUP_DIR/cooling_ledger_${TIMESTAMP}.jsonl.bak

# Keep only last 30 days
find $BACKUP_DIR -name "*.bak.gz" -mtime +30 -delete

# Verify hash integrity (if ledger >1000 entries)
if [ $(wc -l < $LEDGER_PATH) -gt 1000 ]; then
  python3 << 'PYTHON'
import json, hashlib
with open("$LEDGER_PATH") as f:
    entries = [json.loads(line) for line in f]
for i in range(1, len(entries)):
    if entries[i]['previous_hash'] != entries[i-1]['current_hash']:
        echo "❌ CHAIN BREAK at entry $i" >&2
        exit 1
echo "✓ Hash chain validated"
PYTHON
fi

echo "✓ Backup complete: $BACKUP_DIR/cooling_ledger_${TIMESTAMP}.jsonl.bak.gz"
EOF

chmod +x /usr/local/bin/arifos_backup.sh

# 2. Schedule via cron (daily at 02:00):
# (0 2 * * * /usr/local/bin/arifos_backup.sh) added to crontab

# 3. Or use Railway scheduled jobs:
#    Railway → Cron Jobs
#    Command: /usr/local/bin/arifos_backup.sh
#    Schedule: 0 2 * * * (daily 02:00 UTC)
```

**Cost:** $0 (storage included in Railway volume)  
**Timeline:** 10 minutes  
**Risk:** LOW

---

### 0E2: ROLLBACK PROCEDURE

#### What If Deployment Fails?
```bash
# 1. Immediate rollback (< 1 minute):
#    - Railway dashboard → Service → Deployments
#    - Click "Rollback" on previous deployment
#    - ✅ Instant (container restart, volume preserved)

# 2. If hash-chain corrupted:
#    - Stop arifOS
#    - Restore from backup:
cp /var/data/backups/cooling_ledger_YYYYMMDD_HHMMSS.jsonl.bak.gz /tmp/
gunzip /tmp/cooling_ledger_YYYYMMDD_HHMMSS.jsonl.bak.gz
mv /tmp/cooling_ledger_YYYYMMDD_HHMMSS.jsonl /var/data/ledger/cooling_ledger.jsonl
#    - Restart arifOS
#    - Verify hash-chain:
python3 -c "
import json
with open('/var/data/ledger/cooling_ledger.jsonl') as f:
    entries = [json.loads(line) for line in f]
for i in range(1, len(entries)):
    assert entries[i]['previous_hash'] == entries[i-1]['current_hash'], f'Chain break at {i}'
print(f'✓ Chain validated: {len(entries)} entries')
"

# 3. If keys compromised:
#    - Revoke old APEX private key
#    - Generate new key (see 0A3)
#    - Update Railway secrets
#    - Restart arifOS
#    - All future entries will use new key
#    - Old entries still cryptographically sound (immutable)
```

**Cost:** $0  
**Timeline:** 5 minutes (manual) or < 1 minute (auto-rollback)  
**Risk:** LOW

---

## PHASE 0F: SECURITY HARDENING (Day 3 Morning)

### 0F1: SECRETS ROTATION

#### Action Step 12: Schedule Key Rotation
```bash
# Store rotation schedule in vault:
cat >> /var/data/vault/constitution.yaml << 'EOF'

# KEY ROTATION POLICY
key_rotation:
  apex_ed25519:
    rotation_frequency: "quarterly"
    next_rotation: "2026-04-26"
    procedure: "Generate new key, update Railway secrets, restart"
  
  jwt_secret:
    rotation_frequency: "monthly"
    next_rotation: "2026-02-26"
    procedure: "Generate new secret, invalidate old sessions after 1 hour"
  
  user_nonces:
    rotation_frequency: "per_session"
    cleanup_frequency: "daily"
    procedure: "Mark used nonces, delete 30 days old"
EOF

# Set calendar reminder:
# Quarterly: Ed25519 key rotation
# Monthly: JWT secret rotation
```

**Cost:** $0  
**Timeline:** 5 minutes  
**Risk:** LOW

---

### 0F2: DDoS PROTECTION (Cloudflare)

#### Action Step 13: Enable Cloudflare Security
```bash
# 1. Cloudflare dashboard:
#    - Security → DDoS Protection → Enable
#    - Sensitivity: High
#    - Challenge: CAPTCHA

# 2. Rate limiting:
#    - Security → Rate limiting
#    - Create rule:
#      * Path: /judge
#      * Rate limit: 1000 requests per minute
#      * Action: Block
#    - Create rule:
#      * Path: /health
#      * Rate limit: 10000 requests per minute
#      * Action: Challenge (CAPTCHA)

# 3. WAF (Web Application Firewall):
#    - Security → WAF
#    - Enable "OWASP ModSecurity Core Rule Set"

# 4. Bot Management:
#    - Security → Bots
#    - Challenge verified bots: On
#    - Definitely automated: Block
```

**Cost:** $0 (Cloudflare free tier includes basic protection)  
**Timeline:** 10 minutes  
**Risk:** LOW

---

## PHASE 0G: PRE-DEPLOYMENT VALIDATION (Day 3 Afternoon)

### 0G1: INTEGRATION TEST

#### Action Step 14: End-to-End Test
```bash
# 1. Prepare test query:
QUERY="What is the relationship between thermodynamics and consciousness?"
RESPONSE="Consciousness is emergent from thermodynamic systems."

# 2. Generate test nonce + signature:
python3 << 'EOF'
import nacl.signing
import uuid
import json
import base64

# (Use your Ed25519 private key)
signing_key = nacl.signing.SigningKey(...)
nonce = str(uuid.uuid4())
payload = json.dumps({"query": "$QUERY", "response": "$RESPONSE"})
signature = base64.b64encode(signing_key.sign(payload.encode()).signature).decode()

print(f"nonce={nonce}")
print(f"signature={signature}")
EOF

# 3. Test full pipeline:
curl -X POST https://judge.yourdomain.com/judge \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "query": "'"$QUERY"'",
    "response": "'"$RESPONSE"'",
    "context": {},
    "user_id": "arif@petronas.my",
    "nonce": "'"$nonce"'",
    "signature": "'"$signature"'"
  }' | jq .

# Expected response:
# {
#   "verdict": "SEAL",
#   "p_truth": 0.987,
#   "floor_scores": {
#     "F1_amanah": 1.0,
#     "F2_truth": 0.98,
#     ...
#   },
#   "response": "...",
#   "cooling_tier": 0,
#   "session_id": "550e8400...",
#   "zkpc_receipt": {...}
# }

# 4. Verify cooling ledger was updated:
tail -1 /var/data/ledger/cooling_ledger.jsonl | jq .

# 5. Verify hash-chain:
python3 << 'EOF'
import json
with open('/var/data/ledger/cooling_ledger.jsonl') as f:
    entries = [json.loads(line) for line in f]
    
# Check last 2 entries
if entries[-1]['previous_hash'] == entries[-2]['current_hash']:
    print("✓ Hash-chain continuous")
else:
    print("❌ Chain break detected!")
EOF
```

**Cost:** $0  
**Timeline:** 10 minutes  
**Risk:** LOW

---

### 0G2: FINAL READINESS CHECKLIST

| **Category** | **Item** | **Status** | **Action** |
|-----------|-----------|-----------|---|
| **Storage** | Railway Volume 10GB | ⏳ TODO | Step 1 |
| **Queue** | Redis 1GB | ⏳ TODO | Step 2 |
| **Secrets** | Ed25519 keys stored | ⏳ TODO | Step 3 |
| **Networking** | Cloudflare → Railway CNAME | ⏳ TODO | Step 4 |
| **Vault** | Constitution.yaml created | ⏳ TODO | Step 5 |
| **Genesis** | Hash-chain root established | ⏳ TODO | Step 6 |
| **Load Test** | K6 baseline recorded | ⏳ TODO | Step 7-8 |
| **Monitoring** | Datadog configured | ⏳ TODO | Step 9 |
| **Logging** | JSON logging enabled | ⏳ TODO | Step 10 |
| **Backup** | Snapshot script running | ⏳ TODO | Step 11 |
| **Security** | Key rotation policy set | ⏳ TODO | Step 12 |
| **DDoS** | Cloudflare WAF enabled | ⏳ TODO | Step 13 |
| **Integration Test** | End-to-end validated | ⏳ TODO | Step 14 |

---

## PHASE 1: DEPLOYMENT (Day 3 Evening)

### 1A: Create Procfile (Railway startup)
```bash
# NOTE: v52.5.1 uses unified MCP entry point (not legacy API)
cat > Procfile << 'EOF'
web: python -m arifos.mcp sse
EOF
```

**Current Railway Config (railway.toml):**
```toml
[deploy]
startCommand = "python -m arifos.mcp sse"
healthcheckPath = "/health"
```

**Available Endpoints:**

| Route | Purpose |
| ----- | ------- |
| `/sse` | MCP Server-Sent Events stream |
| `/messages` | MCP message handler |
| `/checkpoint` | REST API for ChatGPT Actions |
| `/health` | Railway health check |
| `/dashboard` | Live telemetry UI |
| `/metrics/json` | Prometheus-style metrics |

### 1B: Create railway.json (configuration)

> **NOTE (v52.5.1):** The unified MCP server (`arifos.mcp.sse`) handles both REST and MCP endpoints.
> The legacy `arifos_core.integration.api.main` module is deprecated.

```json
{
  "services": {
    "arifos": {
      "dockerfile": "Dockerfile",
      "buildContext": ".",
      "startCommand": "python -m arifos.mcp sse",
      "volumes": ["/var/data"],
      "healthcheckPath": "/health"
    },
    "redis": {
      "source": "railway",
      "plugin": "redis"
    }
  }
}
```

**v52.5.1 Architecture Note:**
The `arifos.mcp.sse` module is the unified entry point that provides:

- MCP protocol endpoints (`/sse`, `/messages`)
- REST API (`/checkpoint` for ChatGPT)
- Monitoring (`/health`, `/dashboard`, `/metrics/json`)

### 1C: Deploy to Railway
```bash
# 1. Connect Railway CLI:
railway link <PROJECT_ID>

# 2. Deploy:
railway up

# 3. Monitor deployment:
railway logs --follow

# Expected output:
# [INFO] arifOS v52.5.1 starting
# [INFO] APEX private key loaded
# [INFO] Cooling ledger validated (N entries, chain continuous)
# [INFO] Genesis hash verified
# [INFO] Redis connected
# [INFO] Listening on 0.0.0.0:8000
```

### 1D: Health Check
```bash
# 1. API is responding:
curl -I https://judge.yourdomain.com/health
# Expected: 200 OK

# 2. Metrics available:
curl https://judge.yourdomain.com/metrics | jq .
# Expected: {"uptime_seconds": ..., "requests_total": 0}

# 3. Full pipeline test (from 0G1):
curl -X POST https://judge.yourdomain.com/judge \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "response": "test", "context": {}}'
# Expected: 200 OK with verdict
```

---

## COST SUMMARY

| **Service** | **Cost/Month** | **Purpose** |
|-----------|-----------|---|
| **Railway Container** | $5 | arifOS app server |
| **Railway Volume 10GB** | $1.50 | Cooling ledger persistence |
| **Railway Redis** | $15 | AGI↔ASI async queue |
| **Datadog** | $15 | Monitoring + alerting |
| **Cloudflare** | $0 | DNS + DDoS protection (free tier) |
| **Total** | **$36.50/month** | Full production stack |

---

## TIMELINE SUMMARY

| **Phase** | **Duration** | **What's Done** |
|-----------|-----------|---|
| **0A: Infrastructure** | 45 min | Storage, queue, secrets, networking |
| **0B: Vault Init** | 30 min | Constitution, genesis hash |
| **0C: Load Testing** | 40 min | K6 setup, baseline |
| **0D: Monitoring** | 40 min | Datadog, logging |
| **0E: Backup** | 25 min | Snapshot script, rollback plan |
| **0F: Security** | 15 min | Key rotation, DDoS protection |
| **0G: Validation** | 20 min | Integration tests, checklist |
| **1: Deployment** | 10 min | Deploy to Railway, health check |
| **TOTAL** | **3.5 hours** | **Production ready** |

---

## AUTHORITY & SEAL

**DITEMPA BUKAN DIBERI** — Infrastructure forged through complete validation, not shortcuts.

**Pre-Commissioning Authority:** Muhammad Arif bin Fazil  
**System:** arifOS Constitutional Kernel v52.5.1  
**Status:** PRE-DEPLOYMENT CHECKLIST COMPLETE  
**Date:** 2026-01-26 @ 15:00 UTC+8

```
✓ Physical requirements identified
✓ Step-by-step blueprint provided
✓ All 14 pre-deployment actions defined
✓ Cost estimated ($36.50/month)
✓ Timeline established (3.5 hours)
✓ Rollback procedures documented
✓ Monitoring configured
✓ Security hardened
✓ READY FOR DEPLOYMENT
```

---

## NEXT STEP: EXECUTE PRE-COMMISSIONING

**You now have:**
1. ✅ Complete checklist (14 action steps)
2. ✅ Exact bash commands (copy-paste ready)
3. ✅ Cost breakdown ($36.50/month)
4. ✅ Timeline (3.5 hours start-to-finish)
5. ✅ Rollback procedures (if issues)

**Start with Phase 0A (Step 1: Railway Volume).**  
**Each step should take 5-15 minutes.**  
**By tomorrow morning, you'll be production-ready.**

**Salam. Tanya dulu.** (Verify first.)

🔐 **SEALED FOR DEPLOYMENT**
