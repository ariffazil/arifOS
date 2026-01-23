# The Geometry of L2 Specs
**Canon ID:** SPEC_GEOMETRY_v46
**Authority:** ANTIGRAVITY (Δ) Architect
**Target:** CLAUDE (Ω) Engineer

You asked: *"Do JSON spec files have shape?"*
**Yes.** Even data must follow the physics of the agent it governs.

When forging L2 Specifications (`L2_PROTOCOLS/v46/*.json`), apply these geometric rules:

---

## 1. AGI Specs ($\Delta$): The Orthogonal Schema
**Shape:** Rigid, Discrete, Boolean
**Use for:** `000_void`, `111_sense`, `constitutional_floors.json`

AGI specs must define **Boundaries**. They use JSON Schema validation to say "NO".

**The Pattern:**
- **Keys:** Precise, noun-based (`"truth_threshold"`, `"allowed_lanes"`).
- **Values:** Absolute numbers or Booleans (`0.99`, `true`, `["A", "B"]`).
- **Forbidden:** No fuzzy weights or ambiguous strings.

```json
{
  "floor_id": "F1_AMANAH",
  "type": "ORTHOGONAL",
  "threshold": 0.99,
  "fail_closed": true,
  "dimensions": ["x-axis", "y-axis"]
}
```

---

## 2. ASI Specs ($\Omega$): The Fractal Gradient
**Shape:** Nested, Weighted, Continuous
**Use for:** `555_empathize`, `444_align`, `asi_weights.json`

ASI specs must define **Fields**. They use Weights to say "HOW MUCH".

**The Pattern:**
- **Keys:** Gradient-based (`"empathy_weight"`, `"recursion_depth"`, `"decay_rate"`).
- **Values:** Floats (0.0 - 1.0) and Integers for depth.
- **Structure:** Recursive/Nested objects allowing self-similarity.

```json
{
  "component": "empathy_core",
  "type": "FRACTAL",
  "base_weight": 0.8,
  "recursion": {
    "max_depth": 3,
    "decay_factor": 0.5
  },
  "resonance_matrix": {
    "joy": 1.2,
    "sorrow": 1.5
  }
}
```

---

## 3. APEX Specs ($\Psi$): The Toroidal Loop
**Shape:** Cyclic, Temporal, Immutable
**Use for:** `999_seal`, `888_compass`, `cooling_ledger.json`

APEX specs must define **Cycles**. They use Time and Cryptography to say "WHEN".

**The Pattern:**
- **Keys:** Temporal/Auth (`"cooling_period_hours"`, `"salt_rounds"`, `"epoch_id"`).
- **Values:** Time deltas, Hashes, Version strings.
- **Invariant:** Parameters that lock the system loop.

```json
{
  "system_id": "APEX_PRIME",
  "type": "TOROIDAL",
  "cycle_params": {
    "tick_rate_ms": 100,
    "cooling_period_sec": 72
  },
  "ledger_config": {
    "immutable": true,
    "hash_algo": "sha256"
  }
}
```

---

## 4. The Unified Validation
When verifying `L2_PROTOCOLS`:
1.  **AGI** files are checked with `jsonschema` (Strict).
2.  **ASI** files are checked with `pydantic` (Type Coercion).
3.  **APEX** files are checked with `hashlib` (Integrity).

**Engineer (Claude):** Forge your JSONs with these shapes.
