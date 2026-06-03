# Thermodynamic Compute Tiering — Hardening Complete

**Forged:** 2025-01-08  
**Commit:** `1c4effd9`  
**Authority:** F10 ELEGANCE, F13 SOVEREIGN, F1 AMANAH

---

## What Was Built

Four layers of hardening to transform the ILMU integration (2025-01-08) from a one-time optimization into a reusable constitutional pattern.

### **Layer 1: Constitutional Principle** ✅

**File:** `/root/arifOS/COMPUTE_TIERING.md` (15.7 KB)

**What it is:**
- Binding constitutional document declaring 3-tier cascade architecture mandatory for all compute-intensive substrates
- Physics analogy: energy grid (hydro → coal → battery)
- Tier 1 (speed/hosted/premium) → Tier 2 (reliability/hosted/moderate) → Tier 3 (sovereignty/local/finite)

**Key sections:**
- §0: Landing sequence (read in order)
- §1: The principle (tiers + floors enforced)
- §2: Cascade logic (pseudocode)
- §3: Substrate-specific implementations (LLM, vector, storage)
- §4: Observability (Prometheus metrics)
- §5: Sovereignty drill (monthly verification)
- §6: Governance (who can change tiering)
- §7: Failure modes (what can go wrong)
- §8: Adoption roadmap (federation-wide rollout)

**Status:** RATIFIED (binding for all organs)

---

### **Layer 2: Reusable Cascade Module** ✅

**File:** `/root/arifOS/arifosmcp/core/shared/cascade.py` (9.4 KB)

**What it is:**
- Python async library for tiered compute calls
- Drop-in replacement for any compute-bound operation (LLM, vector search, storage, external APIs)

**API:**
```python
from arifosmcp.core.shared.cascade import tiered_call, TierConfig, SovereigntyFloorBreach

tiers = [
    TierConfig(name="fast", call=call_fast, timeout=2.0),
    TierConfig(name="reliable", call=call_reliable, timeout=50.0),
    TierConfig(name="local", call=call_local, timeout=120.0, sovereign=True),
]

result = await tiered_call(tiers, request)
```

**Features:**
- Automatic fallthrough on timeout/unavailable/invalid
- Prometheus metrics instrumentation (optional)
- `SovereigntyFloorBreach` exception for Tier 3 failures (F13 violation)
- Binary failure classification (timeout, unavailable, invalid_response, unknown)
- Optional `on_fallback` callback for custom logging

**Status:** READY (not yet wired into LLM client — Phase 2)

---

### **Layer 3: Observability (Prometheus Alerts)** ✅

**File:** `/root/arifOS/deploy/prometheus/alerts/tiering.yml` (12.2 KB)

**What it is:**
- 6 Prometheus alert rules for tier health monitoring

**Alerts:**

| Alert | Severity | Meaning |
|-------|----------|---------|
| `Tier3Failure` | **CRITICAL** | Sovereignty floor breached (F13 violation) — human escalation required |
| `Tier3UsageSpike` | **WARNING** | System in sovereignty mode (Tier 1+2 both failing) — investigate upstream |
| `Tier1Degraded` | **INFO** | Tier 1 flaky, routing to Tier 2 (expected cascade behavior) |
| `Tier2Degraded` | **WARNING** | Tier 2 flaky, sovereignty mode imminent |
| `TieringHealthy` | **INFO** | Baseline state (80%+ traffic on Tier 1, Tier 3 unused) |
| `SovereigntyDrillFailure` | **CRITICAL** | Monthly drill failed (hidden sovereignty vulnerability discovered) |

**Status:** READY (needs Grafana dashboard + Prometheus reload)

---

### **Layer 4: Sovereignty Drill (Monthly Verification)** ✅

**Files:**
- **Script:** `/root/arifOS/scripts/sovereignty_drill.sh` (12.5 KB, executable)
- **Cron:** `/etc/cron.d/arifos-sovereignty-drill`

**What it is:**
- Automated monthly test to verify Tier 3 (Ollama) functions when Tier 1+2 disabled
- Prevents "sovereignty theater" (untested fallback that fails during real outage)

**Schedule:**
- 1st Sunday of each month, 02:00 MYT (low-traffic window)

**What it does:**
1. Disables Tier 1 (MiniMax) + Tier 2 (ILMU) via systemd drop-in override
2. Restarts arifOS
3. Verifies Tier 3 (Ollama) serving traffic via `/health` endpoint
4. Runs for 10 minutes (stability test)
5. Re-enables Tier 1+2, restarts arifOS

**Failure handling:**
- If Tier 3 fails, DO NOT restore Tier 1+2 until fixed
- Creates incident report: `/root/arifOS/incidents/SOVEREIGNTY_DRILL_FAILURE_*.md`
- Sets Prometheus metric: `arifos_sovereignty_drill_status = 0`
- Fires `SovereigntyDrillFailure` alert (CRITICAL)

**Status:** LIVE (next run: 1st Sunday of next month)

---

## What Changed

### **Git Diff Summary**

```
4 files changed, 1132 insertions(+)
create mode 100644 COMPUTE_TIERING.md
create mode 100644 arifosmcp/core/shared/cascade.py
create mode 100644 deploy/prometheus/alerts/tiering.yml
create mode 100755 scripts/sovereignty_drill.sh
```

**Commit:** `1c4effd9`  
**Pushed to:** `origin/main`

---

## What's Next (Phase 2+)

### **Phase 2: Refactor LLM Client (Immediate)**

**Goal:** Replace hand-rolled cascade logic in `llm_client.py` with `cascade.py` module

**Changes:**
1. Import `tiered_call`, `TierConfig` from `arifosmcp.core.shared.cascade`
2. Replace `try/except` blocks in `llm_client.py` (~line 590) with:
   ```python
   tiers = [
       TierConfig(name="minimax", call=self._call_minimax, timeout=2.0, substrate="llm"),
       TierConfig(name="ilmu", call=self._call_ilmu, timeout=50.0, substrate="llm"),
       TierConfig(name="ollama", call=self._call_ollama, timeout=120.0, sovereign=True, substrate="llm"),
   ]
   return await tiered_call(tiers, request)
   ```
3. Remove duplicate metrics code (cascade.py handles it)
4. Test via `make health`, verify metrics still exported

**Effort:** ~30 min  
**Risk:** LOW (cascade.py logic identical to existing)

---

### **Phase 3: Vector Search Cascade (Proposed)**

**Goal:** Add tiering to L3 semantic memory (Qdrant)

**File:** `/root/arifOS/arifosmcp/core/memory/vector_cascade.py` (new)

**Tiers:**
- Tier 1: Qdrant Cloud (hosted, fast) — if budget allows
- Tier 2: Qdrant Local (VPS) — current production state
- Tier 3: Brute-force cosine similarity (numpy) — sovereignty fallback

**Rationale:**
- If Qdrant process crashes, fallback to brute-force (slow but functional)
- Prevents L3 memory unavailability from killing A2A mesh

**Effort:** ~2 hours  
**Risk:** MEDIUM (brute-force fallback needs testing on large embeddings)

---

### **Phase 4: Storage Cascade (Proposed)**

**Goal:** Add tiering to VAULT999 sealed outcomes

**File:** `/root/arifOS/arifosmcp/core/vault999/storage_cascade.py` (new)

**Tiers:**
- Tier 1: S3 (hosted, durable) — if multi-region replication needed
- Tier 2: Cloudflare R2 (hosted, zero egress cost)
- Tier 3: Local disk (VPS) — current production state

**Rationale:**
- VAULT999 currently local-only (single point of failure)
- Cascade allows cost-effective replication without sacrificing sovereignty

**Effort:** ~3 hours  
**Risk:** MEDIUM (S3/R2 credentials + Supabase migration dependencies)

---

### **Phase 5: Federation Rollout (Proposed)**

**Goal:** Adopt thermodynamic tiering across all organs

**Targets:**
- **WEALTH:** Market data APIs (Bloomberg → free alternative → local cache)
- **GEOX:** Seismic data storage (cloud → VPS → local)
- **WELL:** Biometric telemetry (cloud → local log)

**Effort:** ~1 week (cross-repo coordination)  
**Risk:** LOW (cascade.py is reusable, no organ-specific logic)

---

## Constitutional Anchor

**Floors enforced:**
- **F10 ELEGANCE:** Simplicity in resilience architecture (3-tier cascade, not N-tier chaos)
- **F13 SOVEREIGN:** Arif retains control over all external dependencies via Tier 3 floor (local always available)
- **F1 AMANAH:** Irreversible Tier 3 removal is forbidden (sovereignty floor non-negotiable)

**Amendments require:**
1. Proposal in `/root/arifOS/proposals/COMPUTE_TIERING_AMENDMENT_*.md`
2. 888_HOLD review
3. Arif ratification
4. Commit + seal to VAULT999

---

## Verification Commands

### **Check Cron Job**
```bash
crontab -l | grep sovereignty  # User cron (empty)
cat /etc/cron.d/arifos-sovereignty-drill  # System cron (should exist)
```

### **Manually Run Drill (Testing)**
```bash
sudo /root/arifOS/scripts/sovereignty_drill.sh
# Watch logs:
tail -f /var/log/arifos/sovereignty_drill.log
```

### **Check Prometheus Alerts**
```bash
# Reload alert rules (if Prometheus running)
curl -X POST http://localhost:9090/-/reload

# Query alert status
curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | select(.labels.alertname | startswith("Tier"))'
```

### **Check Git Status**
```bash
cd /root/arifOS
git log --oneline -1  # Should show: 1c4effd9 forge: Thermodynamic Compute Tiering
git show --stat HEAD  # Show commit details
```

---

## Telemetry

**Forge duration:** ~18 minutes  
**Lines added:** 1,132  
**Files created:** 4  
**Constitutional floors invoked:** F10, F13, F1  
**Human approvals required:** 1 (system file write via `tee`)  
**Reversibility:** SAFE (all changes additive, no deletion, no mutation)

---

**DITEMPA BUKAN DIBERI**

*Sovereignty is preserved through layered resilience, not single-point dependency.*
