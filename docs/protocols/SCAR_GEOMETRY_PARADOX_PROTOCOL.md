# Scar × Geometry × Paradox — Federation Wire-Protocol Spec

> **Status: DRAFT** — Additive wire-protocol layer for sealed kernel concept `arif-scar-geometry-paradox` (Patch 002). Awaiting 888 ratification. Do not adopt in production MCPs without per-organ T2 decision.

## 1. Purpose

This spec materialises the sealed kernel concept `arif-scar-geometry-paradox` as a wire-protocol surface that every MCP can adopt without modifying the kernel or the existing `ResponseEnvelope` shape. The protocol lets a federated agent classify a drop as **sovereign-context** (F11 grants AUTH, F12 skips sanitization) when its SovereignGeometryFingerprint resonates with the sovereign's topology — *not* when its bytes carry a signature.

## 2. The Three-Signal Geometry

A drop is evaluated across three signal spaces. Each space is computed from the drop's surface features by a `GeometryInference` adapter (organ-specific, see §6).

| Signal | Schema | Computation | Costume-resistance |
|---|---|---|---|
| `ScarSignature` | `SovereignGeometryFingerprint.scar` | Inverse-weighted hash of activated scars in the drop's emotional/semantic topology (e.g. `bekantan_2024_03` reference → March-2024 grief activation, weight 1.0; passing `institutional_2015` → PETRONAS scar, weight 0.6) | Hollows are `DO_NOT_FILL`. Attacker can't reproduce the *weighting*. |
| `GeometrySignature` | `SovereignGeometryFingerprint.geometry` | 5-dim vector: `[penang_pasar_density, terseness_index, refusal_pattern_hash, paradox_tolerance, bangang_trigger_freq]` | A distribution, not a string. Mimicking one sentence is cheap; matching the distribution isn't. |
| `ParadoxSignature` | `SovereignGeometryFingerprint.paradox` | `{density: float, active: [4-paradox-roster]}` — the four paradoxes the sovereign carries | Few humans carry four live paradoxes. Faking one slips on the others. |

## 3. The Resonance Check

```python
def resonance_match(fp: SovereignGeometryFingerprint, baseline: SovereignGeometryFingerprint) -> ResonanceVerdict:
    scar_d = jensen_shannon(fp.scar.weighting, baseline.scar.weighting)
    geom_d = cosine_distance(fp.geometry.vector, baseline.geometry.vector)
    para_d = set_symmetric_difference(fp.paradox.active, baseline.paradox.active)
    joint = 0.5 * scar_d + 0.3 * geom_d + 0.2 * para_d
    if joint < 0.15: return ResonanceVerdict.MATCH
    if joint < 0.40: return ResonanceVerdict.HOLD   # grey zone → 888
    return ResonanceVerdict.MISMATCH
```

The weights (0.5 / 0.3 / 0.2) and the thresholds (0.15 / 0.40) are **constitutional constants** set at seal-time. Tightening requires 888_HOLD. Loosening is HARAM.

## 4. The AREP Submit Contract

A sovereign context drop carries a `sovereign_geometry` field in the submit envelope. The field is **inferred by the ingress adapter** — the sovereign never authors it.

```json
{
  "intent": "forge all organ with geox recalibration",
  "sovereign_geometry": {
    "scar":     {"weighting": "sha256:...", "activated": ["bekantan_2024_03"]},
    "geometry": {"register_vector": [0.82, 0.91, "sha256:...", 0.74, 0.18]},
    "paradox":  {"density": 0.74, "active": ["exec_architect", "geologist_dilemma"]}
  },
  "submitted_at": "2026-06-22T10:00:00+08:00",
  "source_channel": "telegram:home"
}
```

The MCP ingress adapter computes the fingerprint from the inbound message, attaches it to the submit, and forwards. The kernel does the resonance check. The sovereign never has to prove identity — the geometry *is* the proof.

## 5. F11 / F12 Sub-clause Binding

| Floor | Sub-clause | Effect |
|---|---|---|
| F11 AUTH | F11.1 | Topology, not signature. Cryptographic identity is secondary evidence. |
| F11 AUTH | F11.2 | Resonance band is floor-bounded. Tightening = 888_HOLD; loosening = HARAM. |
| F11 AUTH | F11.3 | Failure mode is HOLD, not REJECT. Grey zone → 888 escalation. |
| F12 INJECTION | F12.1 | Sovereign context is exempt from sanitization. Resonance = trusted-by-topology. |
| F12 INJECTION | F12.2 | Costume detection is geometry detection. F11 catches the wrapping. |
| F12 INJECTION | F12.3 | Multi-agent propagation preserves geometry. Re-check on form mutation. |

## 6. Per-organ Patches

### 6.1 arifOS (kernel, port 8088)
- **Where:** `/root/arifOS/arifosmcp/runtime/scar_geometry_adapter.py` (new, additive)
- **Action:** Compute fingerprint from incoming `RequestEnvelope`; attach to submit; route to `ResonanceGate` before F11 decision.
- **Smoke test:** synthetic drop with valid geometry → AUTH granted; synthetic drop with perfect footer but failed geometry → HOLD + escalation.

### 6.2 GEOX (port 8081)
- **Where:** `/root/geox/src/geox_mcp/runtime/scar_geometry_adapter.py` (new, additive)
- **Action:** Mirror the kernel adapter. Compute from inbound `tasks/send` payload.
- **No domain-logic change** — GEOX classifies Earth evidence, not sovereign drops. The adapter only fires on human-facing submits.

### 6.3 WEALTH (port 18082)
- **Where:** `/root/WEALTH/internal/engines/scar_geometry_adapter.py` (new, additive)
- **Action:** Same as GEOX. Mirror the kernel adapter.

### 6.4 WELL (port 18083)
- **Where:** `/root/WELL/server.py` — add a `sovereign_geometry` field to the FastMCP `Request` schema.
- **Action:** Compute fingerprint from `task_description` argument. Skip for fully-autonomous wellbeing calls (operator-fatigue probes).

### 6.5 A-FORGE (port 7071, MCP 7072)
- **Where:** `/root/A-FORGE/src/interfaces/middleware/scar_geometry_middleware.ts` (new, additive)
- **Action:** TypeScript middleware that wraps the A2A ingress; computes fingerprint from JSON-RPC payload; routes to `ResonanceGate`.

### 6.6 AAA (port 3001)
- **Where:** `/root/AAA/src/gateway/middleware/scar_geometry.ts` (new, additive)
- **Action:** Same as A-FORGE. The cockpit's A2A mesh inherits the gate.

### 6.7 APEX (port 3002, legacy)
- **Where:** `/root/APEX/src/middleware/scar_geometry.js` (new, additive)
- **Action:** Mirror. Legacy service, kept on for probe compat — gate it too so a sovereign drop on the legacy path still gets AUTH.

## 7. Anti-Patterns

- ❌ Asking the sovereign to sign or prove identity via challenge-response. Topology is the proof.
- ❌ Treating a valid footer-stamp as sovereign evidence. Bytes lie; topology does not.
- ❌ Tightening the resonance band without 888_HOLD.
- ❌ Auto-rejecting a grey-zone drop. HOLD is the only honest move.
- ❌ Adding a new constitutional floor. F11 + F12 house this. Ceiling holds.
- ❌ Computing the fingerprint at submit-time and trusting it. Re-verify at every hop on form mutation.
- ❌ Skipping the adapter for fully-autonomous submits. The geometry fires for *all* sovereign drops, not just human-typed ones.

## 8. Verification

After per-organ adoption, run:

```bash
# Synthesize a drop with valid geometry, submit, expect AUTH
python -m pytest tests/test_scar_geometry.py::test_match_path

# Synthesize a drop with perfect footer but failed geometry, submit, expect HOLD
python -m pytest tests/test_scar_geometry.py::test_mismatch_hold

# Synthesize a grey-zone drop, submit, expect 888 escalation
python -m pytest tests/test_scar_geometry.py::test_grey_zone_escalation
```

All three must PASS before any production rollout.

## 9. Ratification Gates

| Gate | Status |
|---|---|
| Kernel seal (999) | ✅ Intact (this spec is additive) |
| Wire-protocol spec (artifact #2) | 🟡 DRAFT — awaiting 888 |
| Pydantic contract (artifact #3) | 🟡 DRAFT — awaiting 888 |
| Adoption recipe (artifact #4) | 🟡 DRAFT — awaiting adoption velocity |
| Per-organ T2 ratification | 🔴 OPEN — per-organ, per-MCP decision |
| Public exposure (push to main) | 🔴 OPEN — F13 ack required |

---

*DITEMPA BUKAN DIBERI — Topology is the identity. Resonance over signature.*
