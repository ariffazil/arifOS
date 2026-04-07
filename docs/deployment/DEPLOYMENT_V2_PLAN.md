# V2 Hardened Organs — Deployment Plan
> **Status:** PHASE 0 — Bootstrap Repair  
> **Authority:** 888_JUDGE  
> **Classification:** CRITICAL PATH

---

## Root Cause: INIT_KERNEL_500

**Fault:** `HARDENED_DISPATCH_MAP` was empty  
**Effect:** `arifos.init` → `init_anchor` fails with kernel panic  
**Fix:** Populate dispatch map with canonical aliases

---

## Phase 0: Fix Bootstrap (IMMEDIATE) ✅

### File: `arifosmcp/runtime/tools_hardened_dispatch.py`

**Required Changes:**
1. ✅ Populate `HARDENED_DISPATCH_MAP` with all canonical tool names
2. ✅ Add `arifos.init` → `init_anchor` alias
3. ✅ Add `arifos.memory` → `engineering_memory` alias
4. ✅ Add `arifos.vault` → `vault_ledger` alias
5. ✅ Add version selector infrastructure

### Verification

```bash
# Test bootstrap
python3 -c "
from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP
assert 'init_anchor' in HARDENED_DISPATCH_MAP, 'init_anchor missing'
assert 'arifos.init' in HARDENED_DISPATCH_MAP, 'arifos.init missing'
assert 'arifos.memory' in HARDENED_DISPATCH_MAP, 'arifos.memory missing'
assert 'arifos.vault' in HARDENED_DISPATCH_MAP, 'arifos.vault missing'
print('✓ Bootstrap dispatch map valid')
"
```

---

## Phase 1: Mount V2 Internals (BEHIND COMPATIBILITY LAYER)

### Backend Version Selectors

```python
# Environment variables
MEMORY_BACKEND_VERSION=v2      # or v1
VAULT_BACKEND_VERSION=v2       # or v1
PROMOTION_BACKEND_VERSION=v2   # or v1
ENABLE_SHADOW_COMPARE=true     # or false
```

### Compatibility Layer Structure

```
arifosmcp/runtime/
├── tools_hardened_dispatch.py     # Version selector + dispatch map
├── compatibility/
│   ├── __init__.py
│   ├── memory_backend.py          # Routes to v1 or v2
│   ├── vault_backend.py           # Routes to v1 or v2
│   └── promotion_backend.py       # Routes to v1 or v2
└── shadow/
    ├── __init__.py
    └── comparator.py              # A/B comparison logic
```

### Public MCP Contracts (STABLE)

**arifos.init**
```json
{
  "mode": "init|revoke|refresh|state|status",
  "payload": {},
  "session_id": "string?",
  "actor_id": "string?"
}
```

**arifos.memory**
```json
{
  "query": "string",
  "mode": "vector_query|vector_store|engineer|query",
  "session_id": "string?"
}
```

**arifos.vault**
```json
{
  "verdict": "SEAL|PARTIAL|VOID|HOLD",
  "evidence": "string?",
  "session_id": "string?"
}
```

---

## Phase 2: Shadow Mode (VALIDATION)

### Shadow Comparison Logic

For every `arifos.memory` request:
```python
# Execute both backends
v1_result = memory_v1(query)
v2_result = memory_v2(query)

# Compare
comparison = {
    "top_results_match": v1_top == v2_top,
    "ranking_delta": calculate_ranking_diff(v1, v2),
    "contested_handled": v2_has_contested_penalty,
    "vault_override_applied": v2_has_vault_boost,
    "confidence_classes": extract_confidence_classes(v2),
}

# Log if significant drift
if comparison["ranking_delta"] > threshold:
    logger.warning("Memory shadow drift detected", comparison)
```

For every `arifos.vault` request:
```python
# Execute both backends
v1_receipt = vault_v1.seal(entry)
v2_receipt = vault_v2.seal(entry)

# Compare
comparison = {
    "record_shape_match": shapes_equivalent(v1, v2),
    "verification_grades": v2_grade.to_dict(),
    "supersession_handled": v2_check_supersession,
    "evidence_integrity": v2_evidence_hash_valid,
}
```

### Shadow Logging

```python
# Logged fields
{
    "timestamp": "2026-04-06T...",
    "tool": "arifos.memory",
    "shadow_run": True,
    "v1_result_hash": "sha256:abc...",
    "v2_result_hash": "sha256:def...",
    "comparison": {
        "match": False,
        "ranking_delta": 0.15,
        "vault_backed_boosted": True,
        "contested_penalty_applied": True,
    }
}
```

---

## Phase 3: Canary Deployment

### Gradual Rollout

```bash
# Step 1: 1% traffic to v2
MEMORY_BACKEND_VERSION=v2
VAULT_BACKEND_VERSION=v1
CANARY_PERCENTAGE=1

# Step 2: 10% traffic
CANARY_PERCENTAGE=10

# Step 3: 50% traffic
CANARY_PERCENTAGE=50

# Step 4: Full cutover
MEMORY_BACKEND_VERSION=v2
VAULT_BACKEND_VERSION=v2
PROMOTION_BACKEND_VERSION=v2
```

### Rollback Trigger

```python
# Auto-rollback conditions
if error_rate > 0.01:          # >1% errors
    rollback_to_v1()
elif shadow_drift > 0.20:       # >20% ranking drift
    alert_but_continue()
elif bootstrap_fails > 0:       # Any bootstrap failure
    immediate_rollback()
```

---

## Phase 4: Full Cutover

### Checklist

- [ ] Bootstrap stable for 7 days
- [ ] Shadow comparison shows <5% drift
- [ ] Vault verification grades 100% valid
- [ ] Promotion outcomes logged correctly
- [ ] No legacy tool name leakage
- [ ] Canonical response names enforced
- [ ] Contract tests passing

### Seal Deployment Record

```python
# Final step: seal in vault
deployment_entry = VaultEntry(
    record_type=VaultRecordType.RELEASE,
    verdict=Verdict.APPROVED,
    candidate_action="Deploy memory/vault v2 to production",
    evidence=Evidence(
        summary="Shadow validation passed, canary stable",
        evidence_refs=["shadow_logs", "contract_tests"],
    ),
    governance=Governance(
        risk_tier="high",
        human_confirmed=True,
        decision_authority="888_JUDGE",
    ),
)
```

---

## Critical Path Files

| Phase | File | Purpose |
|-------|------|---------|
| 0 | `tools_hardened_dispatch.py` | Bootstrap fix |
| 1 | `compatibility/memory_backend.py` | Version routing |
| 1 | `compatibility/vault_backend.py` | Version routing |
| 2 | `shadow/comparator.py` | A/B comparison |
| 2 | `config/environment.py` | Feature flags |
| 3 | `canary/router.py` | Traffic splitting |
| 4 | `core/organs/vault/` | Deployment seal |

---

## Environment Configuration

```bash
# Required env vars
export MEMORY_BACKEND_VERSION=v2
export VAULT_BACKEND_VERSION=v2
export PROMOTION_BACKEND_VERSION=v2
export ENABLE_SHADOW_COMPARE=true
export STRICT_CANONICAL_NAMES=true
export LEGACY_TOOL_NAMES_VISIBLE=false

# Optional tuning
export SHADOW_LOG_LEVEL=INFO
export CANARY_PERCENTAGE=10
export ROLLBACK_THRESHOLD_ERROR=0.01
export ROLLBACK_THRESHOLD_DRIFT=0.20
```

---

## Rollback Procedure

```bash
# Immediate rollback
export MEMORY_BACKEND_VERSION=v1
export VAULT_BACKEND_VERSION=v1
export PROMOTION_BACKEND_VERSION=v1
systemctl restart arifos-mcp

# Verify rollback
arifos.init --mode=status | jq .status  # Should be SUCCESS
```

---

## Verification Commands

```bash
# 1. Bootstrap test
python3 -c "from arifosmcp.runtime import HARDENED_DISPATCH_MAP; print('OK')"

# 2. Memory backend test
arifos memory --query="test" --mode=query | jq .canonical_tool_name
# Expected: "arifos.memory"

# 3. Vault backend test
arifos vault --verdict=SEAL --evidence="test" | jq .verification_grade
# Expected: {chain_valid: true, ...}

# 4. Shadow mode test
grep "shadow_run" /var/log/arifos/mcp.log | head -5

# 5. Canonical name enforcement
curl -s http://localhost:8080/mcp/tools/call \
  -d '{"name":"arifos.memory"}' | jq .tool
# Expected: "arifos.memory" (not "engineering_memory")
```

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Bootstrap success | 100% | `arifos.init` returns SUCCESS |
| Shadow drift | <5% | Ranking comparison |
| Vault integrity | 100% | `verify()` returns fully_valid |
| Response time | <100ms | p99 latency |
| Error rate | <0.1% | 500 errors / total requests |
| Canonical names | 100% | No legacy names in responses |

---

**Current Status:** Phase 0 complete — bootstrap fixed  
**Next Action:** Deploy compatibility layer  
**ETA to Production:** 14 days (with shadow validation)

*DITEMPA BUKAN DIBERI* 🔥
