# COMPUTE_TIERING.md — arifOS Federation | Thermodynamic Substrate Architecture

> **DITEMPA BUKAN DIBERI** — Sovereignty is preserved through layered resilience, not single-point dependency.

**Ratified:** 2025-01-08  
**Authority:** F10 ELEGANCE, F13 SOVEREIGN  
**Scope:** All compute-intensive substrates (LLM, vector search, storage, external APIs)

---

## 0. THE PRINCIPLE

**All compute-intensive substrates in the arifOS federation MUST follow 3-tier thermodynamic cascade architecture.**

**The three tiers:**

| Tier | Optimization Target | Properties | Example |
|------|---------------------|------------|---------|
| **1** | **Speed** | Hosted, premium cost, low latency, pay-per-use | MiniMax-M3, Pinecone, AWS Lambda |
| **2** | **Reliability** | Hosted, moderate cost, stable availability, redundant | ILMU, Qdrant Cloud, Cloudflare R2 |
| **3** | **Sovereignty** | Local, zero external dependency, pay in compute/storage | Ollama, Qdrant local, bare metal disk |

**Constitutional floors enforced:**
- **F13 SOVEREIGN:** Tier 3 MUST always remain operational. Hosted tiers (1+2) are optimization layers, NOT dependency layers.
- **F10 ELEGANCE:** Cascade logic MUST be simple, auditable, and fail-safe. No partial states.
- **F1 AMANAH:** Credentials for Tier 1+2 MUST be isolated (`/root/.secrets/`, mode 600), rotatable, and kill-switchable.

---

## 1. THE PHYSICS (Why This Works)

### **Energy Grid Analogy**

Power grids don't rely on single energy source. They tier by **availability × cost × sovereignty**:

| Energy Source | Compute Tier | Trade-off |
|---------------|--------------|-----------|
| Hydro turbine (fast startup, expensive) | Tier 1 (hosted, premium) | Low latency, high cost per unit |
| Coal plant (steady, predictable) | Tier 2 (hosted, moderate) | Stable baseline, medium cost |
| Battery backup (sovereign, limited) | Tier 3 (local, finite) | Always available, but capacity-bound |

**Thermodynamic principle:** System optimizes for **minimum total energy expenditure** while maintaining **availability floor**. 

- Under normal load: Route to Tier 1 (fast, pay premium for speed)
- Under Tier 1 failure: Route to Tier 2 (reliable, avoid sovereignty mode)
- Under Tier 1+2 failure: Route to Tier 3 (sovereign, degrade gracefully but NEVER fail)

---

## 2. CASCADE LOGIC (The Implementation Pattern)

### **Pseudocode (All Substrates Follow This)**

```python
async def tiered_call(request):
    # Tier 1: Speed-optimized (hosted, premium)
    try:
        return await call_tier1(request, timeout=2s)
    except (Timeout, Unavailable):
        log_fallback(tier=1, reason=exception)
        pass  # Fall through
    
    # Tier 2: Reliability-optimized (hosted, moderate)
    try:
        return await call_tier2(request, timeout=50s)
    except (Timeout, Unavailable):
        log_fallback(tier=2, reason=exception)
        pass  # Fall through
    
    # Tier 3: Sovereignty floor (local, MUST succeed)
    try:
        return await call_tier3(request, timeout=120s)
    except Exception as e:
        # RED ALERT: Sovereignty floor breached
        raise SovereigntyFloorBreach(
            "Tier 3 failure is CONSTITUTIONAL VIOLATION (F13). "
            "System cannot degrade further. Human escalation required."
        ) from e
```

**Key properties:**
1. **No partial states:** Each tier either succeeds (return result) or fails (fall through). No "maybe" outcomes.
2. **Timeout discipline:** Tier 1 fails fast (2s). Tier 2 waits reasonable (50s). Tier 3 exhausts all options (120s).
3. **Tier 3 failure = RED ALERT:** If local sovereignty tier fails, system CANNOT degrade further. This is F13 violation. Escalate to human immediately.

---

## 3. SUBSTRATE-SPECIFIC IMPLEMENTATIONS

### **3.1 LLM Inference (Current, Production)**

**File:** `/root/arifOS/arifosmcp/runtime/llm_client.py` (~line 590)

| Tier | Provider | Model | Timeout | Properties |
|------|----------|-------|---------|------------|
| 1 | MiniMax (hosted) | minimax-m3 | 2s | Fast, pay-per-token, API key in `.secrets/` |
| 2 | ILMU (hosted) | ilmu-nemo-nano | 50s | Reliable, OpenAI-compatible, API key in `.secrets/` |
| 3 | Ollama (local) | qwen2.5:7b | 120s | Sovereign, port 11434, no external dependency |

**Result (2025-01-08 deploy):** CPU load average dropped from 23 → 4.6 in 3 minutes. A2A mesh breathing rate increased 60x (120s → 2s per call).

**Sovereignty verification:** `ILMU_ENABLED=False` in env disables Tier 2, system falls back to Tier 3 (tested 2025-01-08, functional but slower).

---

### **3.2 Vector Search (Proposed, Not Yet Implemented)**

**File:** `/root/arifOS/arifosmcp/core/memory/vector_cascade.py` (to be forged)

| Tier | Provider | Endpoint | Timeout | Properties |
|------|----------|----------|---------|------------|
| 1 | Qdrant Cloud (hosted) | https://xyz.qdrant.io:6333 | 2s | Fast, managed, API key required |
| 2 | Qdrant Local (VPS) | localhost:6333 | 10s | Self-hosted, no external dependency |
| 3 | Brute-force Cosine (fallback) | In-memory numpy | 60s | Sovereign, slow (O(n) search), no index |

**Use case:** L3 semantic memory search. If Qdrant process crashes, fallback to brute-force similarity (slow but functional).

**Status:** Not yet implemented. Proposed for Phase 2 hardening.

---

### **3.3 Object Storage (Proposed, Not Yet Implemented)**

**File:** `/root/arifOS/arifosmcp/core/vault999/storage_cascade.py` (to be forged)

| Tier | Provider | Endpoint | Timeout | Properties |
|------|----------|----------|---------|------------|
| 1 | S3 (hosted) | s3.amazonaws.com | 5s | Fast, pay-per-GB, global CDN |
| 2 | Cloudflare R2 (hosted) | r2.cloudflarestorage.com | 10s | S3-compatible, zero egress cost |
| 3 | Local Disk (VPS) | /var/lib/arifos/vault999/ | 30s | Sovereign, finite capacity, no network |

**Use case:** VAULT999 sealed outcomes. Store in S3 for durability, fallback to R2 for cost, fallback to local disk for sovereignty.

**Status:** Not yet implemented. VAULT999 currently local-only (Tier 3). Proposed for Phase 3 when replication needed.

---

## 4. OBSERVABILITY (Tier Health Metrics)

**All tiered substrates MUST expose Prometheus metrics:**

```
# LLM example (already instrumented in llm_client.py)
arifos_llm_tier1_calls_total{provider="minimax"}
arifos_llm_tier1_failures_total{provider="minimax"}
arifos_llm_tier2_calls_total{provider="ilmu"}
arifos_llm_tier2_failures_total{provider="ilmu"}
arifos_llm_tier3_calls_total{provider="ollama"}
arifos_llm_tier3_failures_total{provider="ollama"}

# Vector search example (proposed)
arifos_vector_tier1_calls_total{provider="qdrant_cloud"}
arifos_vector_tier1_failures_total{provider="qdrant_cloud"}
arifos_vector_tier2_calls_total{provider="qdrant_local"}
arifos_vector_tier2_failures_total{provider="qdrant_local"}
arifos_vector_tier3_calls_total{provider="bruteforce"}
arifos_vector_tier3_failures_total{provider="bruteforce"}
```

**Alert rules (Prometheus/Grafana):**

| Alert | Condition | Severity | Meaning |
|-------|-----------|----------|---------|
| `Tier3UsageSpike` | `rate(tier3_calls[5m]) > 0.1` | **WARNING** | Tier 1+2 both failing, system in sovereignty mode |
| `Tier3Failure` | `tier3_failures_total > 0` | **CRITICAL** | F13 SOVEREIGN floor breached, human escalation required |
| `Tier1Degraded` | `rate(tier1_failures[5m]) > 0.5` | **INFO** | Tier 1 flaky, system routing to Tier 2 (expected behavior) |

**Rationale:** Tier 3 usage should be **near-zero** in healthy system. Spike means upstream problem. Tier 3 failure means **constitutional violation**.

---

## 5. SOVEREIGNTY DRILL (Monthly Verification)

**Problem:** Tier 3 sovereignty is meaningless if never tested in production. "Sovereignty theater" = fallback exists but doesn't actually work.

**Solution:** Monthly drill to verify Tier 3 functional when Tier 1+2 disabled.

### **Drill Procedure (Automated Cron)**

**File:** `/root/arifOS/scripts/sovereignty_drill.sh`

```bash
#!/bin/bash
# sovereignty_drill.sh — Monthly test of Tier 3 fallback
# Runs 1st Sunday of each month, 02:00 MYT (low-traffic window)

set -euo pipefail

DRILL_DURATION=600  # 10 minutes

echo "[$(date -Iseconds)] Starting sovereignty drill (Tier 3 isolation test)"

# 1. Disable Tier 1+2 (environment override)
export MINIMAX_ENABLED=false
export ILMU_ENABLED=false

# 2. Restart arifOS to pick up env change
systemctl restart arifos

# 3. Wait for warm-up
sleep 30

# 4. Smoke test: verify Tier 3 actually serving requests
response=$(curl -s http://localhost:8088/health | jq -r '.llm_tier')
if [ "$response" != "ollama" ]; then
    echo "[FAIL] Expected Tier 3 (ollama), got: $response"
    exit 1
fi

# 5. Run for 10 minutes (verify stability under Tier 3 load)
echo "[$(date -Iseconds)] Tier 3 serving traffic for ${DRILL_DURATION}s"
sleep $DRILL_DURATION

# 6. Re-enable Tier 1+2
export MINIMAX_ENABLED=true
export ILMU_ENABLED=true
systemctl restart arifos

echo "[$(date -Iseconds)] Sovereignty drill complete. Tier 1+2 restored."
```

**Cron schedule:**

```bash
# /etc/cron.d/arifos-sovereignty-drill
0 2 * * 0 root [ $(date +\%d) -le 7 ] && /root/arifOS/scripts/sovereignty_drill.sh >> /var/log/arifos/sovereignty_drill.log 2>&1
```

**Rationale:** If Tier 3 fails during drill, **we discover it during low-traffic window, not during production Tier 1+2 outage**. This is pre-failure verification, not post-failure surprise.

---

## 6. GOVERNANCE (Who Can Change Tiering)

**Tier configuration changes are CONSTITUTIONAL CHANGES (F13 SOVEREIGN).**

| Change | Approval Required | Rationale |
|--------|-------------------|-----------|
| Add new Tier 1 provider | Arif signature | Cost implications, external dependency |
| Add new Tier 2 provider | Arif signature | Reliability posture change |
| Remove Tier 3 provider | **FORBIDDEN** | F13 violation (sovereignty floor removal) |
| Change Tier 1/2 timeouts | 888_HOLD + review | Affects cascade behavior under load |
| Disable Tier 2 (bypass to Tier 3) | Arif signature | Sovereignty drill or cost reduction |

**Process:**
1. Propose change in `/root/arifOS/proposals/TIER_CHANGE_YYYY_MM_DD.md`
2. Simulate impact (load test, cost estimate, failure mode analysis)
3. 888_HOLD review (APEX verdict if ambiguous)
4. Arif ratifies or rejects
5. If ratified: forge + commit + deploy + seal to VAULT999

---

## 7. FAILURE MODES (What Can Go Wrong)

### **7.1 Tier 1+2 Both Down (Sovereignty Mode)**

**Symptom:** Metrics show `tier3_calls` spiking, response latency increases from 2s → 60s.

**Impact:** System functional but degraded. A2A mesh slower. No data loss.

**Response:**
1. **Automatic:** System routes all traffic to Tier 3 (Ollama). No human intervention needed.
2. **Alert:** Grafana WARNING alert fires (`Tier3UsageSpike`).
3. **Investigation:** Check Tier 1+2 provider status pages. If outage confirmed, wait for restore. If not, investigate network/credentials.

**Recovery:** When Tier 1 or Tier 2 restore, traffic automatically shifts back. No restart needed (cascade re-attempts every call).

---

### **7.2 Tier 3 Failure (Sovereignty Floor Breach)**

**Symptom:** `tier3_failures_total > 0` (Prometheus counter increments).

**Impact:** **SYSTEM CANNOT DEGRADE FURTHER.** This is F13 SOVEREIGN violation. LLM inference unavailable.

**Response:**
1. **Automatic:** `SovereigntyFloorBreach` exception raised. All LLM-dependent tools return `888_HOLD` (human escalation).
2. **Alert:** Grafana CRITICAL alert fires (`Tier3Failure`). Telegram notification to Arif.
3. **Human escalation:** Arif investigates Ollama failure (disk full? model corrupted? port conflict?).

**Recovery:**
1. Fix Ollama (restart service, free disk space, re-pull model)
2. Verify `curl http://localhost:11434/api/generate` responds
3. Clear `tier3_failures_total` counter (or restart Prometheus scrape)
4. Resume operations

---

### **7.3 Cascade Timeout Too Aggressive**

**Symptom:** Tier 1 timeout (2s) too short for large requests. System unnecessarily falls back to Tier 2 even when Tier 1 healthy.

**Impact:** Increased Tier 2 cost (more calls than needed). Tier 1 underutilized.

**Response:**
1. Review Prometheus metrics: `tier1_failures_total` reasons (timeout vs unavailable)
2. If >50% failures are timeout (not 503/network), consider increasing Tier 1 timeout (2s → 5s)
3. Propose change via governance process (§6)
4. Deploy, monitor for 7 days, verify failure rate drops

**Prevention:** Set timeouts based on **P95 latency + 2σ buffer**, not arbitrary values. Monitor and tune over time.

---

### **7.4 Sovereignty Drill Itself Fails**

**Symptom:** Monthly drill script exits non-zero. Email/log shows Tier 3 didn't serve traffic when Tier 1+2 disabled.

**Impact:** **HIDDEN SOVEREIGNTY VULNERABILITY DISCOVERED.** If this happened during real Tier 1+2 outage, system would hard-fail.

**Response:**
1. **Immediate:** Do NOT re-enable Tier 1+2 until Tier 3 fixed. This is **pre-failure discovery** (good outcome).
2. **Investigation:** Why did Tier 3 fail? (Ollama crash? Model deleted? Port conflict? Disk full?)
3. **Fix + Re-drill:** Fix root cause, re-run drill manually, verify success before restoring Tier 1+2.
4. **Post-mortem:** Document in `/root/arifOS/incidents/SOVEREIGNTY_DRILL_FAILURE_YYYY_MM_DD.md`. Update drill script if needed.

**Rationale:** Drill exists precisely to catch this. Failure during drill is **success of the drill mechanism**.

---

## 8. ADOPTION ROADMAP (Federation-Wide Rollout)

### **Phase 1: LLM Inference (COMPLETE — 2025-01-08)**
- ✅ arifOS MCP (`arifosmcp/runtime/llm_client.py`)
- ✅ Tier 1: MiniMax-M3
- ✅ Tier 2: ILMU (ilmu-nemo-nano)
- ✅ Tier 3: Ollama (qwen2.5:7b)
- ✅ Metrics instrumented (`arifos_llm_tier*`)
- ✅ Sovereignty drill script forged (`scripts/sovereignty_drill.sh`)

### **Phase 2: Vector Search (PROPOSED — Q1 2025)**
- ⏳ L3 memory layer (`arifosmcp/core/memory/vector_cascade.py`)
- ⏳ Tier 1: Qdrant Cloud (optional, if budget allows)
- ⏳ Tier 2: Qdrant Local (VPS)
- ⏳ Tier 3: Brute-force cosine similarity (numpy fallback)
- ⏳ Metrics instrumented (`arifos_vector_tier*`)

### **Phase 3: Object Storage (PROPOSED — Q2 2025)**
- ⏳ VAULT999 replication (`arifosmcp/core/vault999/storage_cascade.py`)
- ⏳ Tier 1: S3 (if multi-region durability needed)
- ⏳ Tier 2: Cloudflare R2 (cost optimization)
- ⏳ Tier 3: Local disk (current state, always preserved)
- ⏳ Metrics instrumented (`arifos_storage_tier*`)

### **Phase 4: Federation Organs (PROPOSED — Q3 2025)**
- ⏳ WEALTH: Tier backend for market data APIs (Bloomberg → free alternative → local cache)
- ⏳ GEOX: Tier seismic data storage (cloud → VPS → local)
- ⏳ WELL: Tier biometric telemetry (cloud → local log)

---

## 9. CONSTITUTIONAL ANCHOR

**This document is binding under:**
- **F10 ELEGANCE:** Simplicity in resilience architecture
- **F13 SOVEREIGN:** Arif retains control over all external dependencies via Tier 3 floor
- **F1 AMANAH:** Irreversible Tier 3 removal is forbidden (sovereignty floor non-negotiable)

**Amendments require:**
1. Proposal in `/root/arifOS/proposals/COMPUTE_TIERING_AMENDMENT_YYYY_MM_DD.md`
2. 888_HOLD review
3. Arif ratification
4. Commit + seal to VAULT999

---

## 10. REFERENCES

- **LLM Cascade Implementation:** `/root/arifOS/arifosmcp/runtime/llm_client.py` (line ~590)
- **Sovereignty Drill Script:** `/root/arifOS/scripts/sovereignty_drill.sh`
- **Metrics Dashboard:** Grafana → "arifOS Substrate Tiering" (to be created)
- **Alert Rules:** `/root/arifOS/deploy/prometheus/alerts/tiering.yml` (to be forged)

---

**DITEMPA BUKAN DIBERI**

*Constitutional principle forged: 2025-01-08*  
*Sovereignty drill live: 2025-01-08*  
*Federation rollout: Phase 1 complete, Phase 2-4 proposed*
