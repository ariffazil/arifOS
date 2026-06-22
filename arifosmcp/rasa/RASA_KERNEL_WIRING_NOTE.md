# Rasa Contract Kernel Wiring — Integration Note

> **DITEMPA BUKAN DIBERI — Forged, Not Given.**
> **Date:** 2026-06-13
> **Status:** WIRED (SHADOW default)

---

## 1. What Was Wired

The Rasa Contract (`arifosmcp/rasa/`) is now wired into the live arifOS kernel
via monkey-patching at server startup. When `RASA_WIRING_ENABLED` is truthy,
the kernel's runtime tool functions are wrapped with rasa governance adapters.

### Wired Functions (in `arifosmcp.runtime.tools`)

| Stage | Function Patched | Hook Called | Mode |
|-------|-----------------|-------------|------|
| **000** | `_arif_init` | bootstrap rasa context | passive |
| **111** | `_arif_observe` | `rasa_sense_hook()` | primary |
| **333** | `_arif_think` | `rasa_mind_hook()` | shadow/passive |
| **444** | `_arif_critique` | `rasa_heart_hook()` | primary |
| **555m** | `_arif_memory_recall` | `rasa_memory_hook()` | shadow/passive |
| **888** | `_arif_judge` | `rasa_judge_hook()` | primary |

### Wiring Mechanism

```
server.py main()
    └── _init_rasa_wiring()
        └── activate_rasa_wiring()
            └── Patches arifosmcp.runtime.tools._arif_* functions
                └── Each wrapper: original_fn → rasa detection → original_fn → attach metadata
```

---

## 2. Feature Flags

### Two-Level Gating

```
RASA_WIRING_ENABLED=1    ← Master kill-switch (required)
RASA_CONTRACT_MODE=shadow ← Behavioral mode (optional, default: SHADOW)
```

### Modes

| Mode | Env Value | Behavior |
|------|-----------|----------|
| **OFF** | (unset or RASA_WIRING_ENABLED=0) | Zero overhead. No imports, no hooks, no telemetry. |
| **SHADOW** | `RASA_CONTRACT_MODE=shadow` | Hooks run. Telemetry emitted. Zero output modification. |
| **ENFORCE_CRISIS** | `RASA_CONTRACT_MODE=enforce_crisis` | CRISIS risk band → HOLD output. |
| **ENFORCE_DISTRESS** | `enforce_distress` | CRISIS + DISTRESS → governed output. |
| **ENFORCE_ALL** | `enforce_all` | Full pipeline enforcement. |

### Rollout Path (Safe Escalation)

```
OFF → SHADOW (observe telemetry) → ENFORCE_CRISIS → ENFORCE_DISTRESS → ENFORCE_ALL
```

---

## 3. Input/Output Contracts

### 111 SENSE — `rasa_sense_hook(message, session_id)`

**Input:** Human message text + session_id.
**Output:**
```python
{
    "detection": RasaDetection,       # Full Pydantic detection object
    "risk_band": "safe|distress|crisis",
    "emotion_tags": ["sadness", ...],  # 12 Penang Pasar BM-English tags
    "confidence": 0.0-1.0,
    "intensity": "low|medium|high",
    "requires_human": bool,            # True for CRISIS
    "observation_note": "You report feeling...",
    "session_id": str,
}
```

**Effects on output:**
- SHADOW: `result["_rasa"]` attached with metadata
- ENFORCE (CRISIS): `result["status"] = "HOLD"`, verdict downgraded

### 444 HEART — `rasa_heart_hook(detection, context, memory)`

**Input:** RasaDetection + RasaContext + RasaMemoryPattern.
**Output:**
```python
{
    "deescalation_score": 0.0-1.0,
    "dignity_preservation": 0.0-1.0,
    "boundary_honored": bool,
    "boundary_risk": "none|blurred|violated",
    "f9_violation_risk": 0.0-1.0,    # ≥0.3 triggers rewrite
    "f10_violation_risk": 0.0-1.0,   # ≥0.3 triggers rewrite
    "requires_human_loop": bool,
    "requires_human_professional": bool,
}
```

**Effects on output:**
- SHADOW: `result["_rasa_heart"]` attached
- ENFORCE: Heart risk scores influence downstream judge

### 888 JUDGE — `rasa_judge_hook(detection, context, heart)`

**Input:** RasaDetection + RasaContext + RasaHeartVerdict.
**Output:**
```python
{
    "allowed_postures": ["proceed", "simplify", ...],
    "blocked_outputs": ["consciousness_claims", "gaslighting_patterns", ...],
    "requires_rewrite": bool,          # F9/F10 violation → True
    "floors_checked": {"F1": True, "F5": True, ...},
    "downgrade_reason": str,
}
```

**Effects on output:**
- SHADOW: `result["_rasa_judge"]` attached
- ENFORCE: SEAL→HOLD downgrade when blocked_outputs present

---

## 4. Telemetry Schema

Emitted to `/root/arifOS/logs/rasa_telemetry.jsonl` (append-only JSONL):

```json
{
  "timestamp": "2026-06-13T12:00:00.000Z",
  "session_id": "session-abc123",
  "message_snippet": "first 100 chars of human message",
  "risk_band": "safe|distress|crisis",
  "detection_tags": ["sadness", "grief"],
  "governed_posture": "proceed|simplify|verify|draft_only|hold|human_loop",
  "ungoverned_posture": "proceed",
  "delta": "Shadow only: safe (would enforce → proceed)",
  "enforcement_mode": "shadow|enforce_crisis|...",
  "enforced": false
}
```

### Runtime Fields (attached to tool output `_rasa` key)

```python
{
    "rasa_detected": bool,
    "rasa_tags": list[str],
    "rasa_intensity": "low|medium|high",
    "rasa_confidence": float,
    "crisis_short_circuit": bool,
    "boundary_integrity": "PASS|WARN|FAIL",
    "emotional_risk_score": float,
    "verdict_shift_due_to_rasa": bool,
    "rasa_mode": "off|shadow|enforce_crisis|enforce_distress|enforce_all",
    "rasa_hook_status": "PASS|DEGRADED|FAILED",
}
```

---

## 5. Rollback Procedure

### Deactivate (runtime, reversible)
```python
from arifosmcp.rasa.rasa_wiring import deactivate_rasa_wiring
deactivate_rasa_wiring()  # Restores all original functions
```

### Deactivate (permanent)
```bash
unset RASA_WIRING_ENABLED
# OR
export RASA_WIRING_ENABLED=0
systemctl restart arifos
```

### Verify deactivation
```bash
grep -c "rasa" /root/arifOS/logs/rasa_telemetry.jsonl  # should not grow
```

---

## 6. Files Modified / Created

| File | Action | Description |
|------|--------|-------------|
| `arifosmcp/rasa/rasa_wiring_config.py` | **Modified** | Added OFF mode, `is_rasa_wiring_enabled()`, `mode_allows_telemetry()` |
| `arifosmcp/rasa/rasa_wiring.py` | **Modified** | Patches `arifosmcp.runtime.tools` instead of `arifosmcp.tools.*`. Added sync/async auto-detect. |
| `arifosmcp/rasa/rasa_contract.py` | **Modified** | `sense()` handles `None` message gracefully. F9/F10 thresholds changed to `>= 0.3`. |
| `arifosmcp/server.py` | **Modified** | Added `_init_rasa_wiring()` call in `main()`. |
| `arifosmcp/tools/sense.py` | **Modified** | No-op `_inject_rasa` placeholder (adapter pattern). |
| `arifosmcp/tools/heart.py` | **Modified** | Comment noting external wiring pattern. |
| `tests/rasa/test_rasa_wiring_kernel.py` | **Created** | 47 tests: OFF/SHADOW/ENFORCE, crisis, adversarial, telemetry. |
| `tests/rasa/test_rasa_contract.py` | **Modified** | Updated F9 threshold test for `>=` boundary. |
| `arifosmcp/rasa/RASA_KERNEL_WIRING_NOTE.md` | **Created** | This document. |

---

## 7. Constitutional Invariants Preserved

- **F1 AMANAH:** Default is OFF (zero overhead, zero risk). Activation is reversible.
- **F5 PEACE:** No gaslighting/trivializing pain — blocked outputs enforced.
- **F6 EMPATHY:** Dignity preservation scored in heart, dignity-first in judge.
- **F9 ANTIHANTU:** No consciousness claims — f9_violation_risk ≥0.3 blocks.
- **F10 ONTOLOGY:** No soul/feelings claims — f10_violation_risk ≥0.3 blocks.
- **F13 SOVEREIGN:** Human must opt-in via env var. Judge preserves veto.
- **No new floors:** F1-F13 only. Rasa is governance, not legislation.
- **No silent behavior:** All changes gated behind `RASA_WIRING_ENABLED`. Default OFF.
- **No self-authorization:** `arif_forge` never infers rasa. Judge is sole verdict authority.
- **Hook failure → degrade:** Every hook wrapped in try/except. Failure emits warning, returns ungoverned result.

---

*DITEMPA BUKAN DIBERI — This wiring is forged from understanding, not copied from assumption. The Rasa Contract governs machine response to human rasa. It never claims to feel.*
