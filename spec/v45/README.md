# spec/v44 - SINGLE RUNTIME AUTHORITY (Track B)

**Version:** v45.0.0 | **Status:** AUTHORITATIVE | **Last Updated:** 2025-12-25

---

## ⚖️ AUTHORITY STATEMENT

**spec/v45/ is the SOLE RUNTIME AUTHORITY for all Track B (tunable) thresholds.**

Runtime loaders MUST use spec/v45/ files (or explicit env override) with fail-closed behavior.

Legacy specs (v35Omega, v38Omega, v42) are retained for history only. They MUST NOT be loaded by default.

---

## 📁 Canonical Spec Files (v45.0)

| File | Purpose | Status |
|------|---------|--------|
| **constitutional_floors.json** | F1-F9 thresholds, red patterns, verdicts | ✅ AUTHORITATIVE |
| **genius_law.json** | G, C_dark, Ψ metrics, GENIUS LAW formula | ✅ AUTHORITATIVE |
| **session_physics.json** | TEARFRAME physics thresholds (budget, burst, streaks) | ✅ AUTHORITATIVE (NEW in v44) |
| **waw_prompt_floors.json** | W@W Federation config (@LAW, @GEOX, @WELL, @RIF, @PROMPT) | ✅ AUTHORITATIVE |
| **cooling_ledger_phoenix.json** | Ledger config, Phoenix-72, scar lifecycle | ✅ AUTHORITATIVE |

**Total Specs:** 5 files, ~53KB, self-contained

---

## 🔄 Version Evolution

- **v35Omega:** Initial spec-driven floors (LEGACY)
- **v38Omega:** Red patterns + precedence order (LEGACY)
- **v42.1:** Dual-order equilibrium, RASA enforcement (LEGACY)
- **v43.0:** Interface & Authority (specialized, see spec/v43/)
- **v45.0:** **TEARFRAME physics + consolidated single authority** ← YOU ARE HERE

---

## 🆕 What's New in v45.0

### 1. **session_physics.json** (NEW)
Extracted TEARFRAME physics thresholds from hardcoded values:
- Budget limits: 80% warn, 100% hard limit
- Burst detection: >30 turns/min with low variance → SABAR
- Streak detection: 3+ consecutive failures → HOLD_888

### 2. **Single Authority Enforcement**
All specs now have v44 headers with explicit authority markers:
```json
{
  "version": "v45.0",
  "authority": "Track B (tunable thresholds) governed by Track A canon",
  "locked": true,
  "_status": "AUTHORITATIVE",
  "_note": "This file is the SOLE RUNTIME AUTHORITY. Loader MUST use this file."
}
```

### 3. **Self-Contained Structure**
v44/ no longer references v42/. All thresholds consolidated into v44/ files.

---

## 🔒 Loader Contract

### Priority Order (Strict):
```
A) ARIFOS_SPEC_DIR env var (directory override)      ← Highest (operator authority)
   OR ARIFOS_FLOORS_SPEC (file override)
B) spec/v45/constitutional_floors.json               ← Authoritative default
C) HARD FAIL (raise exception)                        ← Fail-closed (no silent defaults)

Optional: ARIFOS_ALLOW_LEGACY_SPEC=1 enables fallback to v42/v38/v35 (default OFF)
```

### Validation Requirements:
1. **Structural Validation:** Check for required keys (`floors`, `vitality`, `metrics`, etc.)
2. **Version Check:** Ensure `version` field present and valid
3. **Threshold Types:** Verify all threshold values are correct type (float/bool/int)
4. **Fail-Closed:** Invalid/missing spec → HARD FAIL (unless legacy switch enabled)

### Loaded-From Marker:
All loaders MUST add `_loaded_from` marker to loaded spec data for audit trail:
```json
{
  "version": "v45.0",
  "_loaded_from": "spec/v45/constitutional_floors.json",
  // ... rest of spec
}
```

---

## 📂 Integration Points

### Constitutional Floors:
- **Loader:** `arifos_core/enforcement/metrics.py:_load_floors_spec_unified()`
- **Constants:** `TRUTH_THRESHOLD`, `DELTA_S_THRESHOLD`, `PEACE_SQUARED_THRESHOLD`, etc.
- **Spec:** `spec/v45/constitutional_floors.json`

### GENIUS LAW:
- **Loader:** `arifos_core/enforcement/genius_metrics.py:_load_genius_spec()`
- **Constants:** `G_SEAL`, `G_VOID`, `PSI_SEAL`, `CDARK_SEAL`, etc.
- **Spec:** `spec/v45/genius_law.json`

### Session Physics:
- **Loader:** `arifos_core/governance/session_physics.py:_load_physics_spec()`
- **Constants:** `BUDGET_WARN_LIMIT`, `BUDGET_HARD_LIMIT`, `BURST_TURN_RATE_THRESHOLD`, etc.
- **Spec:** `spec/v45/session_physics.json` (NEW)

### W@W Federation:
- **Loader:** `arifos_core/waw/federation.py:_load_waw_spec()`
- **Spec:** `spec/v45/waw_prompt_floors.json`

### Cooling Ledger:
- **Loader:** `arifos_core/memory/cooling_ledger.py:_load_ledger_spec()`
- **Spec:** `spec/v45/cooling_ledger_phoenix.json`

---

## 🚫 What v44 Is NOT

- **NOT a complete system spec:** Runtime behavior, pipeline stages, memory bands are code-driven
- **NOT Track A canon:** Canonical law lives in `L1_THEORY/canon/` (interpretation authority)
- **NOT mutable at runtime:** Specs are loaded once at module import; changes require service restart

---

## 🔮 Future (v45+)

Potential enhancements (NOT in v44):
- Dynamic threshold reloading (Phoenix-72 runtime amendments)
- Spec versioning with migration scripts
- Per-lane threshold overrides (PHATIC/SOFT/HARD/REFUSE lanes)
- Adaptive thresholds based on session history

---

## 🛡️ Integrity Checks

### Verify v44 Authority:
```python
# Check loaded spec version
from arifos_core.enforcement.metrics import _FLOORS_SPEC_V38
print(f"Version: {_FLOORS_SPEC_V38.get('version')}")
print(f"Loaded from: {_FLOORS_SPEC_V38.get('_loaded_from')}")

# Expected output:
# Version: v45.0
# Loaded from: spec/v45/constitutional_floors.json
```

### Hard-Fail Test:
```bash
# Rename v44 to trigger hard-fail
mv spec/v44 spec/v44_backup

# Run Python (should FAIL if legacy fallback disabled)
python -c "from arifos_core.enforcement import metrics"
# Expected: ImportError or RuntimeError (spec missing)

# Restore
mv spec/v44_backup spec/v44
```

---

## 📜 Track A vs Track B

| Track | Authority | Location | Mutability |
|-------|-----------|----------|------------|
| **Track A (Canon)** | Interpretation | `L1_THEORY/canon/` | Immutable (Phoenix-72 only) |
| **Track B (Spec)** | Thresholds | `spec/v45/` | Tunable (operator override) |
| **Track C (Code)** | Implementation | `arifos_core/` | Follows Track B |

**Governance:** Canon > Spec > Code (Track A governs Track B governs Track C)

---

**DITEMPA, BUKAN DIBERI** - Truth must cool before it rules.

The constitution is forged. Track B authority is unified.
