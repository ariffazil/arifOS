# APEX-MCP-001 — Runtime Governance Envelope for MCP

**Version:** v2026.06.20
**Authority:** F13 SOVEREIGN — Muhammad Arif bin Fazil
**Status:** SPECIFICATION — binding for all federation organs
**Supersedes:** None (new)

---

## 1. Core Invariant

> **Every MCP-visible output that can influence agent state must carry an APEX envelope, except transport frames, which remain protocol-pure JSON-RPC.**

APEX is not the brain. APEX is not the model. APEX is the nervous system plus constitutional reflex arc.

---

## 2. The 10 APEX Gates

### 2.1 Inner Cognitive Gates (6)

These gate epistemic quality — the intelligence of each claim.

| # | Gate | Question | APEX-Law Dial | Score Source |
|---|------|----------|---------------|--------------|
| 1 | **Amanah Gate** | Is the claim no stronger than the evidence? | AKAL | confidence ≤ f(evidence) |
| 2 | **Presence Gate** | Is the source LIVE, CACHED, or INFERRED? | PRESENT | present_boundary classification |
| 3 | **Humility Gate** | Is uncertainty explicit? | AKAL | uncertainty band declared |
| 4 | **Signal Gate** | Is evidence quality scored? | ENTROPY | evidence_refs quality |
| 5 | **Understanding Gate** | Is the reasoning coherent? | AKAL | no non-sequitur detected |
| 6 | **Energy Gate** | Was compute/token/tool cost tracked? | ENERGY | C ≤ B ratio |

### 2.2 Kernel Gates (4)

These gate constitutional compliance — the legality of each action.

| # | Gate | Question | APEX-Law Dial | Score Source |
|---|------|----------|---------------|--------------|
| 7 | **Authority Gate** | Is this actor allowed to do this? | AUTHORITY | principal ∈ registry |
| 8 | **Reversibility Gate** | Is the action reversible, mutable, or irreversible? | EXPLORATION×AMANAH | action_class classification |
| 9 | **Proof Gate** | Does ZKPC level match risk? | EXPLORATION×AMANAH | proof_level vs action_class |
| 10 | **Sovereign Gate** | Does F13 require human veto/hold? | AUTHORITY | F13 halt channel |

### 2.3 Gate → APEX-Law Dial Mapping

```
Amanah Gate      ──→ AKAL (A)         \
Humility Gate    ──→ AKAL (A)          ├─ A dial = f(amanah, humility, understanding)
Understanding Gate ──→ AKAL (A)        /
Presence Gate    ──→ PRESENT (P)       ── P dial
Signal Gate      ──→ ENTROPY (S)       ── S dial
Energy Gate      ──→ ENERGY (E)        ── E dial
Authority Gate   ──→ AUTHORITY (H)     ── H dial (kernel gate, pre-computation)
Reversibility Gate ──→ EXPLORATION×AMANAH (U)
Proof Gate       ──→ EXPLORATION×AMANAH (U) ── U dial = f(reversibility, proof)
Sovereign Gate   ──→ AUTHORITY (H)     ── H dial override (F13 veto = instant VOID)
```

---

## 3. The APEX Envelope

### 3.1 Schema

Every MCP tool response carries this envelope at the `apex` key:

```json
{
  "result": { ... },
  "apex": {
    "equation": "g(t)=A(t)·P(t)·H(t)·√(S(t)·U(t))·E(t)²",
    "gates": {
      "amanah":      { "pass": true,  "score": 0.92, "detail": "confidence 0.92 ≤ evidence 0.95" },
      "presence":    { "pass": true,  "score": 1.0,  "detail": "LIVE", "boundary": "LIVE" },
      "humility":    { "pass": true,  "score": 0.88, "detail": "uncertainty band [0.03, 0.05]" },
      "signal":      { "pass": true,  "score": 0.85, "detail": "2 evidence refs, quality HIGH" },
      "understanding": { "pass": true, "score": 0.90, "detail": "coherent reasoning chain" },
      "energy":      { "pass": true,  "score": 0.78, "detail": "cost 0.22 ≤ budget 1.0" },
      "authority":   { "pass": true,  "score": 1.0,  "detail": "actor verified", "actor_id": "opencode" },
      "reversibility": { "pass": true, "score": 1.0, "detail": "READ action_class", "action_class": "READ" },
      "proof":       { "pass": true,  "score": 0.85, "detail": "ZKPC_OBSERVATION matches READ", "proof_level": "ZKPC_OBSERVATION" },
      "sovereign":   { "pass": true,  "score": 1.0,  "detail": "no F13 halt active" }
    },
    "dials": {
      "A": 0.90,
      "P": 1.0,
      "H": 1.0,
      "S": 0.85,
      "U": 0.92,
      "E": 0.78
    },
    "G": 0.87,
    "verdict": "SEAL",
    "weakest_gate": "energy",
    "timestamp": "2026-06-20T10:30:00Z"
  }
}
```

### 3.2 Gate Verdict Shape

Each gate produces:

```python
{
    "pass": bool,       # Did the gate pass?
    "score": float,     # 0.0 to 1.0
    "detail": str,      # Human-readable explanation
    # Optional domain-specific fields:
    "boundary": str,    # Presence gate: "LIVE" | "CACHED" | "INFERRED"
    "action_class": str, # Reversibility gate: "READ" | "MUTATE" | "ATOMIC" | "IRREVERSIBLE"
    "proof_level": str,  # Proof gate: "ZKPC_NONE" | "ZKPC_OBSERVATION" | "ZKPC_AUDIT" | "ZKPC_CERTAINTY"
    "actor_id": str,     # Authority gate: verified actor
}
```

### 3.3 Verdict Lattice

```
VOID > HOLD > SABAR > SEAL
```

- Any gate `pass: false` → overall verdict at least HOLD
- `Sovereign gate pass: false` → instant VOID
- `G ≥ 0.80` → SEAL (if no gates failed)
- `0.50 ≤ G < 0.80` → SABAR
- `G < 0.50` → HOLD

### 3.4 Computation

```python
# 10 gates → 6 dials → G score → verdict

# A dial = geometric_mean(amanah.score, humility.score, understanding.score)
# P dial = presence.score
# H dial = min(authority.score, sovereign.score)  # kernel gate
# S dial = signal.score
# U dial = geometric_mean(reversibility.score, proof.score)
# E dial = energy.score

# G = A × P × H × √(S × U) × E²
```

---

## 4. MCP Primitive Integration

### 4.1 Tools — Explicit APEX in structuredContent

MCP tools return `apex` as a top-level key in the response dict. This is **data**, not transport.

**FastMCP serialization:** Tools return `dict`. FastMCP serializes to JSON. The `apex` key flows through as structured content.

```python
# Tool function returns:
return {
    "result": { ... domain output ... },
    "apex": apex_envelope(tool_name="geox_well_compute", result=result, ...)
}
```

**outputSchema integration:** Add `"apex"` to the output schema's `properties` and to `required`:

```json
{
  "type": "object",
  "properties": {
    "result": { ... },
    "apex": { "$ref": "#/$defs/ApexEnvelope" }
  },
  "required": ["result", "apex"]
}
```

### 4.2 Resources — Canon Metadata in Annotations

Resources carry APEX canon in `annotations`:

```json
{
  "uri": "geox://basin/profile",
  "name": "Basin Profile",
  "annotations": {
    "audience": ["assistant"],
    "priority": 0.9,
    "apex_canon": "g(t)=A(t)·P(t)·H(t)·√(S(t)·U(t))·E(t)²",
    "apex_version": "v2026.06.20"
  }
}
```

### 4.3 Prompts — Axiom Grounding in Messages

Prompts include APEX axiom preamble as the first system message:

```
APEX CANON — Runtime Constitutional Physics
g(t) = A(t) · P(t) · H(t) · √(S(t)·U(t)) · E(t)²

10 Gates enforced before every action:
  [Cognitive] Amanah · Presence · Humility · Signal · Understanding · Energy
  [Kernel]    Authority · Reversibility · Proof · Sovereign

Verdict: G≥0.80→SEAL | 0.50≤G<0.80→SABAR | G<0.50→HOLD | axiom violated→VOID
Evidence discipline: OBS/DER/INT/SPEC
Boundary: {LIVE, CACHED, INFERRED}

DITEMPA BUKAN DIBERI
```

### 4.4 Transport — No APEX

Transport is pure JSON-RPC over stdio or Streamable HTTP. No governance semantics in protocol layer. This is a hard invariant.

---

## 5. Organ Responsibilities

### 5.1 arifOS (Kernel)

- **Kernel enforcement:** All 10 gates evaluated before tool execution
- **Gate source:** `_enforce_nine_signal` → extended with APEX gates
- **Envelope injection:** `_coerce_public_envelope` adds `apex` key
- **Resources:** All `arifos://` resources carry `apex_canon` annotation
- **Prompts:** All prompt messages include axiom preamble

### 5.2 GEOX (Earth Evidence)

- **Gate source:** `get_standard_envelope` extended with `apex` key
- **Cognitive gates:** amanah (from claim_state), presence (from perception_class), signal (from evidence_refs), humility (from uncertainty)
- **Kernel gates:** authority (from actor_id), reversibility (inherited READ for evidence), proof (ZKPC_OBSERVATION), sovereign (passthrough)

### 5.3 WEALTH (Capital Intelligence)

- **Gate source:** `create_envelope` extended with `apex` key
- **Cognitive gates:** amanah (from confidence), signal (from g_score), energy (from entropy_s)
- **Kernel gates:** authority (from session), reversibility (all capital tools are READ), proof (ZKPC_OBSERVATION), sovereign (passthrough)

### 5.4 WELL (Vitality)

- **Gate source:** New `apex_envelope()` call added to each tool
- **Cognitive gates:** presence (LIVE from state.json), humility (from truth_status), signal (from well_score)
- **Kernel gates:** authority (from operator_id), reversibility (all WELL tools are READ), proof (ZKPC_OBSERVATION), sovereign (passthrough)

### 5.5 A-FORGE (Execution Shell)

- **Gate source:** `apexDials.ts` extended with 10-gate decomposition
- **All 10 gates evaluated** at execution boundary
- **Terminal output:** Forge receipts include full APEX envelope
- **Existing code:** `calculateGeniusFromFloors` already computes G from 13 floors

### 5.6 AAA (Control Plane)

- **A2A deliberation:** Response includes APEX envelope
- **Gate source:** Absorbed from arifOS kernel judgment
- **Deliberation verdict:** Extended with gate-by-gate breakdown

---

## 6. Implementation Phases

### Phase 1: Shared Module (Immediate)
- Create `apex_envelope.py` in arifOS as canonical implementation
- Export as importable module for GEOX, WEALTH, WELL

### Phase 2: arifOS Kernel (Immediate)
- Wire `_apex_gates()` into `_coerce_public_envelope`
- All 19 canonical tools get `apex` key in response

### Phase 3: Evidence Organs (Next)
- GEOX: `get_standard_envelope` + `apex` key
- WEALTH: `create_envelope` + `apex` key
- WELL: per-tool `apex_envelope()` call

### Phase 4: Execution Layer (Next)
- A-FORGE: extend `apexDials.ts` with 10-gate decomposition
- AAA: extend deliberation response with APEX envelope

---

## 7. Naming Convention

### APEX-Law (Philosophical)
```
AKAL · PRESENT · ENERGY · ENTROPY · EXPLORATION×AMANAH
```
The 6 intelligence dimensions. Used in theory, scoring, and the G equation.

### APEX-Gates (Executable)
```
Amanah · Presence · Humility · Signal · Understanding · Energy
+ Authority · Reversibility · Proof · Sovereign
```
The 10 runtime enforcement gates. Used in code, tool responses, and kernel enforcement.

**Do not force weak acronym symmetry. Preserve the doctrine.**

---

## 8. Verification

To verify APEX compliance for an organ:

1. Every tool response has `apex` key with all 10 gates
2. Every gate has `pass`, `score`, `detail`
3. Overall `verdict` matches gate logic (any failed → at least HOLD)
4. `G` matches dial computation
5. Resources carry `apex_canon` in annotations
6. Prompts include axiom preamble
7. Transport has no APEX fields

---

**DITEMPA BUKAN DIBERI** — The envelope is forged through gates, not assumed through confidence.
