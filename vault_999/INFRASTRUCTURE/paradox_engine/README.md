# Paradox Engine Infrastructure (Data Layer)

**Component:** VAULT-999 Infrastructure
**Purpose:** Persistent storage for paradox resolution data
**Location:** `vault_999/INFRASTRUCTURE/paradox_engine/`
**Code:** `arifos_core/engines/paradox/` (separate)

---

## Architecture: Dual Infrastructure

The Paradox Engine follows the quantum architecture geometry with **two complementary components**:

```
┌─────────────────────────────────────────────────────┐
│ CODE (arifOS Core)                                  │
│ Location: arifos_core/engines/paradox/              │
│ - paradox_detector.py   (Detection & ScarPackets)   │
│ - metrics_tracker.py    (PP/PS/Psi/Phi metrics)     │
│ - __init__.py           (Package exports)           │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ DATA (VAULT-999 Infrastructure)                     │
│ Location: vault_999/INFRASTRUCTURE/paradox_engine/  │
│ - scar_packets/                                     │
│   - active_scars.jsonl   (Unresolved paradoxes)     │
│   - resolved_scars.jsonl (Completed resolutions)    │
│ - metrics_log.jsonl      (Metric history)           │
└─────────────────────────────────────────────────────┘
```

---

## Files in This Directory

### `scar_packets/`
Directory containing paradox records with PP/PS/Psi/Phi metrics.

#### `active_scars.jsonl`
**Purpose:** Currently unresolved paradoxes (COOLING or RESOLVING)
**Format:** One ScarPacket per line (JSONL)
**Retention:** Until resolved
**Example:**
```json
{
  "scar_id": "SCAR-ABC123",
  "nature": "authority_boundary",
  "contradiction": {
    "statement_a": {"claim": "AAA forbidden", "confidence": 1.0, "floor": "F11"},
    "statement_b": {"claim": "Read AAA for recall", "confidence": 0.8, "floor": "F2"}
  },
  "status": "COOLING",
  "paradox_metrics": {"PP": 0.9, "PS": 0.0, "Psi": 0.45, "Phi": 0.0},
  "created_at": "2026-01-17T16:50:00.000000"
}
```

#### `resolved_scars.jsonl`
**Purpose:** Completed paradox resolutions
**Format:** One ScarPacket per line (JSONL)
**Retention:** Permanent
**Example:**
```json
{
  "scar_id": "SCAR-ABC123",
  "nature": "authority_boundary",
  "status": "RESOLVED",
  "paradox_metrics": {"PP": 0.9, "PS": 1.0, "Psi": 0.95, "Phi": 1.0},
  "created_at": "2026-01-17T16:50:00.000000",
  "resolved_at": "2026-01-20T16:50:00.000000",
  "resolution": {
    "method": "constitutional_boundary",
    "outcome": "VOID - F11 violation",
    "reasoning": "AAA vault access forbidden by constitutional floor F11"
  }
}
```

### `metrics_log.jsonl`
**Purpose:** Historical tracking of metric changes
**Format:** One metric snapshot per line (JSONL)
**Retention:** Permanent
**Example:**
```json
{
  "scar_id": "SCAR-ABC123",
  "timestamp": "2026-01-17T16:50:00.000000",
  "metrics": {"PP": 0.9, "PS": 0.3, "Psi": 0.6, "Phi": 0.0},
  "status": "RESOLVING",
  "metadata": {}
}
```

---

## The Four Paradox Metrics

### PP (Paradox Pressure) - 0.0 to 1.0
**Meaning:** How strong is the contradiction?
**Calculation:** `contradiction_strength × avg_confidence × authority_multiplier`
**Example:** PP=0.9 means high-pressure contradiction requiring urgent resolution

### PS (Paradox Stabilization) - 0.0 to 1.0
**Meaning:** Progress toward resolution
**Calculation:** `(success_rate × 0.7) + (time_factor × 0.3)`
**Example:** PS=0.3 means 30% stabilized, still working on it

### Psi (Equilibrium) - 0.0 to 1.0
**Meaning:** Balance between pressure and stabilization
**Calculation:** `(PP + PS) / 2`
**Interpretation:**
- Psi < 0.3: Crisis (high pressure, low stabilization)
- Psi 0.3-0.7: Transitioning (working on resolution)
- Psi > 0.7: Near resolution (high stabilization)

### Phi (Resolution) - 0.0 to 1.0
**Meaning:** Completion status
**Interpretation:**
- Phi = 0.0: Unresolved paradox
- Phi = 0.5: Partial resolution (machine approved)
- Phi = 1.0: Full resolution (human sealed)

---

## Paradox Lifecycle

```
1. DETECTION
   ↓
   ParadoxDetector.detect_contradiction()
   ↓
   PP calculated (pressure measured)

2. SCAR CREATION
   ↓
   ParadoxDetector.create_scar_packet()
   ↓
   Status: COOLING
   Metrics: PP=0.9, PS=0.0, Psi=0.45, Phi=0.0
   ↓
   Saved to active_scars.jsonl

3. RESOLUTION ATTEMPT
   ↓
   ParadoxDetector.update_scar_status()
   ↓
   Status: RESOLVING
   Metrics: PP=0.9, PS=0.3, Psi=0.6, Phi=0.0
   ↓
   Logged to metrics_log.jsonl

4. RESOLUTION COMPLETE
   ↓
   ParadoxDetector.resolve_scar()
   ↓
   Status: RESOLVED
   Metrics: PP=0.9, PS=1.0, Psi=0.95, Phi=1.0
   ↓
   Moved to resolved_scars.jsonl
```

---

## Usage from arifOS Code

```python
from arifos_core.engines.paradox import ParadoxDetector, ParadoxMetrics

# Initialize (defaults to vault_999/ for data storage)
detector = ParadoxDetector(vault_root="vault_999")
metrics = ParadoxMetrics(vault_root="vault_999")

# Detect contradiction
contradiction = {
    "statement_a": {"claim": "X is true", "confidence": 1.0},
    "statement_b": {"claim": "X is false", "confidence": 0.9}
}

is_contradiction = detector.detect_contradiction(
    contradiction["statement_a"],
    contradiction["statement_b"]
)

# Create ScarPacket
scar = detector.create_scar_packet(
    nature="logical",
    contradiction=contradiction
)

# Track metrics
metrics.track_metrics(
    scar_id=scar.scar_id,
    pp=scar.paradox_metrics["PP"],
    ps=scar.paradox_metrics["PS"],
    psi=scar.paradox_metrics["Psi"],
    phi=scar.paradox_metrics["Phi"],
    status=scar.status
)
```

---

## Constitutional Integration

**Floor Integration:**
- **F2 (Truth):** Paradoxes violate truth, must be resolved
- **F4 (ΔS Clarity):** Resolution reduces system entropy
- **F7 (Ω₀ Humility):** Acknowledges contradictions exist
- **F10 (Ontology):** Formal symbolic reasoning about logic

**Verdict Routing:**
- Detected paradox → `PARTIAL` (needs resolution)
- Cooling period → Phoenix-72 (72h window)
- Human resolution → `SEAL` (Phi=1.0)
- Unresolved after cooling → `VOID` (auto-reject)

---

## "Ditempa Bukan Diberi" at the Logical Level

The Paradox Engine implements the core arifOS principle "Forged, not given" through:

1. **Detection:** Contradictions are not ignored - they are formally acknowledged
2. **Cooling:** ScarPackets must cool (like Phoenix-72) before resolution
3. **Metrics:** PP/PS/Psi/Phi provide objective measures of resolution progress
4. **Sealing:** Only human approval (Phi=1.0) fully resolves a paradox

**Wisdom:** Truth is not given by proclamation. It is forged through formal resolution of contradictions.

---

**Version:** v47.1
**Last Updated:** 2026-01-17
**Status:** Operational
**Authority:** Constitutional Floor F10 (Ontology) + F2 (Truth)
