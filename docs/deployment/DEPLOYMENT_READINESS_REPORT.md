# Deployment Readiness Report: V2 Hardened Organs
> **Status:** PHASE 0 COMPLETE — READY FOR PHASE 1  
> **Date:** 2026-04-06  
> **Authority:** 888_JUDGE

---

## Executive Summary

| Item | Status | Notes |
|------|--------|-------|
| Bootstrap fix | ✅ COMPLETE | HARDENED_DISPATCH_MAP populated |
| Compatibility layer | ✅ COMPLETE | Backend version routing ready |
| Shadow mode | ✅ COMPLETE | A/B comparison infrastructure ready |
| Canonical names | ✅ ENFORCED | No legacy leakage |
| Phase 1 deployment | 🟡 READY | Awaiting green light |

---

## Phase 0: Bootstrap Repair ✅

### Problem
```
arifos.init → INIT_KERNEL_500
HARDENED_DISPATCH_MAP has no init_anchor entry
```

### Solution
**File:** `arifosmcp/runtime/tools_hardened_dispatch.py`

```python
HARDENED_DISPATCH_MAP = {
    # Core bootstrap
    "init_anchor": init_anchor_v1,
    "arifos.init": init_anchor_v1,  # ← Canonical alias added
    
    # Memory backends (versioned)
    "engineering_memory": <routed>,
    "arifos.memory": <routed>,       # ← Canonical alias added
    
    # Vault backends (versioned)
    "vault_ledger": <routed>,
    "arifos.vault": <routed>,        # ← Canonical alias added
    "vault": <routed>,
    
    # All megaTools populated
    "agi_mind": agi_mind,
    "asi_heart": asi_heart,
    ...
}
```

### Verification
```bash
python3 -c "
from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP
assert 'init_anchor' in HARDENED_DISPATCH_MAP
assert 'arifos.init' in HARDENED_DISPATCH_MAP
assert 'arifos.memory' in HARDENED_DISPATCH_MAP
assert 'arifos.vault' in HARDENED_DISPATCH_MAP
print('✓ All canonical aliases present')
"
```

---

## Phase 1: Compatibility Layer ✅

### Backend Version Selectors

**Environment Variables:**
```bash
MEMORY_BACKEND_VERSION=v2      # or v1
VAULT_BACKEND_VERSION=v2       # or v1
PROMOTION_BACKEND_VERSION=v2   # or v1
ENABLE_SHADOW_COMPARE=true     # or false
```

### Architecture

```
arifosmcp/runtime/
├── tools_hardened_dispatch.py     # ← Fixed bootstrap
│
├── compatibility/                 # ← NEW
│   ├── __init__.py
│   ├── memory_backend.py          # Routes to v1/v2
│   ├── vault_backend.py           # Routes to v1/v2
│   └── promotion_backend.py       # Routes to v1/v2
│
└── shadow/                        # ← NEW
    ├── __init__.py
    └── comparator.py              # A/B comparison logic
```

### Public MCP Contracts (STABLE)

| Tool | Contract | Stage |
|------|----------|-------|
| `arifos.init` | `mode, payload, session_id` | 000_INIT |
| `arifos.memory` | `query, mode, session_id` | 555_MEMORY |
| `arifos.vault` | `verdict, evidence, session_id` | 999_VAULT |

---

## Phase 2: Shadow Mode ✅

### Comparison Logic

**Memory Shadow:**
```python
comparison = {
    "top_results_match": v1_top == v2_top,
    "ranking_delta": calculate_diff(v1, v2),
    "vault_backed_boosted": v2_has_vault_penalty,
    "contested_penalty_applied": v2_has_contested_penalty,
    "confidence_classes": extract_classes(v2),
}
```

**Vault Shadow:**
```python
comparison = {
    "record_shape_match": shapes_equivalent(v1, v2),
    "verification_grades": v2_grade.to_dict(),
    "supersession_handled": v2_check_supersession,
    "evidence_integrity": v2_evidence_hash_valid,
}
```

### Logging

All comparisons logged to `/var/log/arifos/shadow.log`:
```json
{
  "timestamp": "2026-04-06T...",
  "tool": "arifos.memory",
  "shadow_run": true,
  "match": false,
  "ranking_delta": 0.15,
  "vault_backed_boosted": true,
  "contested_penalty_applied": true,
}
```

---

## Phase 3: Deployment Sequence

### Step-by-Step

```bash
# 1. Verify bootstrap
python3 -m arifosmcp.runtime --test-init

# 2. Enable shadow mode (no traffic shift)
export ENABLE_SHADOW_COMPARE=true
export MEMORY_BACKEND_VERSION=v1
export VAULT_BACKEND_VERSION=v1
systemctl restart arifos-mcp

# 3. Shadow validation (7 days)
# Monitor: /var/log/arifos/shadow.log
# Check: ranking_delta < 0.05

# 4. Canary memory (1% traffic)
export MEMORY_BACKEND_VERSION=v2
export CANARY_PERCENTAGE=1

# 5. Canary vault (1% traffic)
export VAULT_BACKEND_VERSION=v2

# 6. Full cutover
export CANARY_PERCENTAGE=100

# 7. Seal deployment
arifos vault --verdict=SEAL --evidence="V2 deployment complete"
```

---

## Canonical Name Enforcement

### Response Format

**Before (Legacy Leakage):**
```json
{
  "tool": "engineering_memory",
  "stage": "555_MEMORY"
}
```

**After (Canonical):**
```json
{
  "canonical_tool_name": "arifos.memory",
  "tool": "arifos.memory",
  "stage": "555_MEMORY",
  "backend_version": "v2",
  "_confidence_class": "sealed_from_vault",
  "_vault_backed": true
}
```

### Internal Fields (Debug Only)

Fields prefixed with `_` are for internal debugging:
- `_confidence_class`
- `_source_weight`
- `_vault_backed`
- `_contested`
- `_lane`

These do not appear in production responses (STRICT_CANONICAL_NAMES=true).

---

## Contract Tests

### Test Coverage

```
core/organs/tests/
├── test_memory_contracts.py     # ✅ Schema, gates, decay
└── test_vault_contracts.py      # ✅ Schema, grades, chain
```

**Test Count:** 20+ contract tests

### Running Tests

```bash
# Memory tests
pytest core/organs/tests/test_memory_contracts.py -v

# Vault tests
pytest core/organs/tests/test_vault_contracts.py -v

# All tests
pytest core/organs/tests/ -v --tb=short
```

---

## Rollback Plan

### Immediate Rollback

```bash
# Emergency rollback (< 30 seconds)
export MEMORY_BACKEND_VERSION=v1
export VAULT_BACKEND_VERSION=v1
export PROMOTION_BACKEND_VERSION=v1
systemctl restart arifos-mcp

# Verify
arifos init --mode=status | jq .status
# Expected: "SUCCESS"
```

### Auto-Rollback Triggers

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Bootstrap failures | > 0 | Immediate rollback |
| Error rate | > 1% | Alert + investigate |
| Shadow drift | > 20% | Alert + hold |
| Latency p99 | > 500ms | Degrade gracefully |

---

## Success Criteria Checklist

### Pre-Deployment

- [x] Bootstrap fix verified
- [x] Compatibility layer mounted
- [x] Shadow mode implemented
- [x] Canonical names enforced
- [x] Contract tests passing
- [ ] Shadow validation (7 days)
- [ ] Canary traffic (1% → 10% → 50%)
- [ ] Performance benchmarks

### Post-Deployment

- [ ] Bootstrap success rate: 100%
- [ ] Shadow drift: < 5%
- [ ] Vault integrity: 100%
- [ ] Response time p99: < 100ms
- [ ] Error rate: < 0.1%
- [ ] Canonical names: 100%

---

## Files Modified/Created

### Modified
1. `arifosmcp/runtime/tools_hardened_dispatch.py` — Fixed bootstrap

### Created
1. `arifosmcp/runtime/compatibility/__init__.py`
2. `arifosmcp/runtime/compatibility/memory_backend.py`
3. `arifosmcp/runtime/compatibility/vault_backend.py`
4. `arifosmcp/runtime/compatibility/promotion_backend.py`
5. `arifosmcp/runtime/shadow/__init__.py`
6. `arifosmcp/runtime/shadow/comparator.py`
7. `core/organs/tests/test_memory_contracts.py`
8. `core/organs/tests/test_vault_contracts.py`

### Documentation
1. `DEPLOYMENT_V2_PLAN.md` — Full deployment plan
2. `DEPLOYMENT_READINESS_REPORT.md` — This report

---

## Next Actions

| Priority | Action | Owner | ETA |
|----------|--------|-------|-----|
| P0 | Enable shadow mode | DevOps | Today |
| P1 | 7-day shadow validation | QA | 7 days |
| P2 | Canary memory 1% | DevOps | Day 8 |
| P3 | Canary vault 1% | DevOps | Day 10 |
| P4 | Full cutover | DevOps | Day 14 |
| P5 | Seal deployment | 888_JUDGE | Day 14 |

---

## Conclusion

**Phase 0 (Bootstrap Repair):** ✅ COMPLETE  
**Phase 1 (Compatibility):** ✅ READY  
**Phase 2 (Shadow Mode):** ✅ READY  
**Phase 3 (Deployment):** 🟡 PENDING GREEN LIGHT

The hardened memory and vault organs are **ready for staged deployment**. The bootstrap fault is fixed, the compatibility layer is in place, and shadow mode will catch any drift before it affects users.

**Recommended:** Enable shadow mode today, validate for 7 days, then proceed with canary deployment.

---

*DITEMPA BUKAN DIBERI* 🔥  
**Status:** Approved for staged deployment, not direct hot replacement.
