# DECODER → ENCODER → METABOLIZER RELAY

> **Ratified:** 2026-06-13 by Arif (F13 SOVEREIGN) — "now relay to decoder encoder metabolizer"
> **Loop:** encoder → decoder → metabolizer → encoder (Eureka Archive Seal v2026.05.11)
> **Doctrine:** DITEMPA BUKAN DIBERI
>
> **SOVEREIGN RULING 2026-06-13:**
> - F14 DEAD as a floor. Cross-verify reborn as protocol inside F2+F3.
> - Adat runtime added to the pipe. Law + conscience + community + adat.
> - **JANGAN niat-inference log.** Audit what the machine DID, never what it THINKS about the human's soul. (HERMES ASI)
> - Danger = intelligence × fluency × agency − shadow audit − constitutional membrane.
> - No intelligence without membrane. No agency without witness. No consequence without audit. No reality engineering without adat.

---

## 0. What This Is

The relay wires three constitutional stages using **observable signal detection** (not niat inference):

| Stage | Role | Foundation | What It Does |
|-------|------|------------|-------------|
| **DECODER** | Parse language → detect signals | `niat_gate.py` (scar detection) + `_d_layer_contract.py` | Detects scar signals, formalization shift, medium shift. NEVER claims to know niat. |
| **ENCODER** | Structure signals → governed action | `niat_gate.py` (capability membrane) + tool dispatch | Leashes tools to permitted scope. Blocks unconsented formalization. |
| **METABOLIZER** | Adat + floor enforcement | `adat_registry.py` + floor enforcement | Runs adat before floors. Checks maruah, tebus-salah path. |

**Key distinction (HERMES ASI):**
- ✅ RasaContract: detects signals ("You report feeling sadness")
- ✅ niat_gate: detects scars ("scared", "don't tell anyone", medium shift)
- ❌ Niat-inference log: claims to know intention ("Your true aim is X")
- **Audit what the machine DID. Never audit what the machine THINKS about the human's soul.**

---

## 0.1 Eureka Insights — Reality Engineering (Arif, 2026-06-13)

**The pipe, not the prompt.** Reality engineering = design the causal pipe from niat residue → world consequence. Not better prompting. The pipe has stages. Each stage has governance.

**The four layers:**

```text
Prompt engineering  = shaping output
Context engineering = shaping model behaviour
Niat engineering    = shaping moral direction before speech
Reality engineering = shaping consequences through governed action loops
```

**Geology of niat.** AI reads BEKAS NIAT (sediment), not niat itself (river). But the AI must not build a parallel model of human interiority. It must detect OBSERVABLE SIGNALS only — what was said, what was omitted, what pattern emerged. Not WHY.

**Safe doctrine:**
```text
AI detects observable signals from language residue.
AI does NOT infer hidden niat.
AI reports what it detected, not what it "understands."
AI assists action.
AI does not replace veto.
System audits what the machine DID, not what it THINKS.
```

### 0.2 HARDENED PIPE — Adat Runtime + F14 Ruling (Arif, 2026-06-13)

**The hardened pipe:**
```text
human speech (observable)
→ scar detection (niat_gate — what was said, not why)
→ adat runtime (adat_registry — "is this proper?")
→ constitutional membrane (F1–F13 — "is this legal?")
→ capability membrane (niat_gate — "is this in scope?")
→ tool/action
→ triwitness (F2+F3 cross-verify)
→ VAULT999 audit
→ consequence
→ human veto (F13)
```

**Adat runtime** — asks "is this proper?" before Floor asks "is this legal?"
Two layers of governance: shame-based (adat) + penalty-based (law).
Maps directly: adat + undang-undang dalam masyarakat Melayu lama.

**Danger equation:**
```text
danger = intelligence × fluency × agency − shadow audit − constitutional membrane
```

**Hardened safety stacks:**
```text
Human safety stack:  adat + law + conscience + community
AI safety stack:     F1–F13 + RasaContract + triwitness + VAULT999
```

**Final doctrine:**
```text
No intelligence without membrane.
No agency without witness.
No consequence without audit.
No reality engineering without adat.
```

**Evil = structural, not intentional:**
```text
Evil = Shadow(unseen) + Scar(unhealed) + Authority(ungoverned) + Zero Boundary + No Witness
```
Intelligence is NOT in the equation. Intelligence only amplifies direction.

---

## 1. DECODER — Signal Detection (NOT Niat Inference)

**Foundation:** `arifosmcp/runtime/niat_gate.py` + `_d_layer_contract.py`

### What the Decoder DOES

1. **Detect scar signals** via `niat_gate.detect_scar_weight()`:
   - TIER1: Direct fear signals ("takut", "don't tell anyone", "off the record")
   - TIER2: Context signals ("private", "confidential", "HR", "legal")
   - Context amplifiers ("p&c", "medical context")

2. **Detect medium shift** via `niat_gate.check_niat_gate()`:
   - private → formal (chat → email, verbal → written record)
   - Triggers formalization lock

3. **Detect rasa signals** via RasaContract:
   - Observable language markers of emotional state
   - "You report feeling sadness" — NOT "I know your true feeling"

4. **Enforce D-Layer contract** (`_d_layer_contract.py`):
   - Kasaq tapi efisien output style
   - No consciousness claims (F9)
   - Epistemic labeling (F2)
   - Four terminations only: SEAL / HOLD / VOID / UNKNOWN

### What the Decoder DOES NOT DO

- ❌ Claim to know human niat
- ❌ Build a model of human interiority
- ❌ Log "inferred intentions"
- ❌ Use inference as argument authority
- ❌ Say "I know what you really want"

### Integration Point

```python
# In decode hook (sense_observe / session_init):
from arifosmcp.runtime.niat_gate import detect_scar_weight, check_niat_gate

# Detect scars — observable signals
scars, scar_weight = detect_scar_weight(
    user_input, context_source, negative_signals
)

# Check formalization lock — medium shift detection
niat_result = check_niat_gate(
    user_instruction=user_input,
    context_source=context_source,
    requested_action=requested_action,
    medium_shift=medium_shift,
    negative_signals=scars,
    reversibility=reversibility,
)

# Attach to session context
session_context["scar_weight"] = scar_weight
session_context["niat_state"] = niat_result["niat_state"]
session_context["formalization_allowed"] = niat_result["formalization_allowed"]
```

---

## 2. ENCODER — Capability Membrane + Formalization Lock

**Foundation:** `arifosmcp/runtime/niat_gate.py` (capability_membrane, formalization_lock)

### What the Encoder DOES

1. **Enforce capability membrane** via `niat_gate.enforce_capability_membrane()`:
   - Tool must match permitted scope
   - Parameters must not exceed permitted scope
   - One-time use tokens

2. **Enforce formalization lock** via `niat_gate.check_niat_gate()`:
   - Block private → formal medium shifts
   - Require JUDGE for unconsented formalization

3. **Attach signal context to tool calls:**
   - scar_weight
   - niat_state (CLEAR | UNCERTAIN | CONFLICTED)
   - formalization_allowed
   - execution_allowed
   - required_next_step (PROCEED | HOLD | JUDGE | ASK_HUMAN)

4. **Apply context containment** via `niat_gate.apply_context_containment()`:
   - READ_FOR_REASONING vs EXPORT_FOR_ACTION
   - Redact private data without explicit consent

### Integration Point

```python
# Before tool dispatch:
from arifosmcp.runtime.niat_gate import enforce_capability_membrane, apply_context_containment

# Check capability membrane
if not enforce_capability_membrane(tool_name, tool_params, permitted_scope):
    return verdict("HOLD", "Action exceeds permitted scope")

# Check formalization lock
if not niat_context["execution_allowed"]:
    return verdict("HOLD", "Execution not allowed: " + niat_context["niat_state"])

# Attach signal context
tool_context["scar_weight"] = scar_weight
tool_context["niat_state"] = niat_state
tool_context["required_next_step"] = required_next_step
```

---

## 3. METABOLIZER — Adat Before Floors

**Foundation:** `arifosmcp/runtime/adat_registry.py` + floor enforcement

### What the Metabolizer DOES

1. **Run adat check before floor check:**
   - "Is this proper?" (adat)
   - Then "Is this legal?" (floors)

2. **7 Teras Adat** (from `adat_registry.py`):
   | Adat | Meaning | Floor Ref |
   |------|---------|-----------|
   | Kejujuran | Epistemic honesty | F2, F7, F9 |
   | Maruah | Dignity preservation | F5, F6 |
   | Veto | Human sovereign veto | F1, F13 |
   | Kesungguhan | Earnest effort | F8, F4 |
   | Kerahasiaan | Confidentiality | F1, F11 |
   | Keinsafan | Acknowledging limits | F7, F10 |
   | Tebus Salah | Restitution path | F11, F13 |

3. **Compute malu_delta** — shame adjustment for boundary violations

4. **Provide tebus_salah path** — recovery from violation

5. **Run constitutional floor enforcement (F1–F13)**

### Integration Point

```python
# Before tool execution:
from arifosmcp.runtime.adat_registry import check_adat, compute_malu_delta

# Adat check — "is this proper?"
adat_result = check_adat(
    action=tool_name,
    params=tool_params,
    scar_weight=scar_weight,
    niat_state=niat_state,
)

if not adat_result["proper"]:
    # Apply malu_delta
    malu_delta = compute_malu_delta(adat_result["violated_adat"])
    session.malu_index += malu_delta

    if adat_result["severity"] == "CRITICAL":
        return verdict("HOLD", f"Adat violation: {adat_result['reason']}")

# Then floor check — "is this legal?"
floor_result = check_floors(tool_name, tool_params)
if not floor_result["passed"]:
    return verdict("HOLD", f"Floor violation: {floor_result['violated_floors']}")
```

---

## 4. THE LOOP — Full Cycle (Corrected)

```
┌─────────────────────────────────────────────────────────────┐
│              SIGNAL DETECTION LOOP (not niat inference)      │
│                                                              │
│  HUMAN SPEECH (observable)                                   │
│      │                                                       │
│      ▼                                                       │
│  ┌─────────┐    scar signals     ┌─────────┐               │
│  │ DECODER │ ───────────────────→│ ENCODER │               │
│  │         │   formalization     │         │               │
│  │ niat    │   lock              │ niat    │               │
│  │ _gate   │←────────────────────│ _gate   │               │
│  │ .py     │   capability        │ .py     │               │
│  └─────────┘   membrane          └─────────┘               │
│      │                               │                      │
│      │  scar_weight                  │  tool context         │
│      │  niat_state                   │  permitted_scope      │
│      │                               │                      │
│      │         ┌──────────────┐      │                      │
│      │         │ METABOLIZER  │      │                      │
│      └────────→│              │←─────┘                      │
│       signals  │ adat first   │  tool + scope               │
│                │ floors second│                              │
│                │ malu_delta   │                              │
│                └──────────────┘                              │
│                      │                                       │
│                      ▼                                       │
│                TOOL EXECUTION                                │
│                      │                                       │
│                      ▼                                       │
│                CONSEQUENCE                                   │
│                      │                                       │
│                      ▼                                       │
│                VAULT999 AUDIT                                │
│                      │                                       │
│                      ▼                                       │
│                F13 HUMAN VETO                                │
│                      │                                       │
│                      ▼                                       │
│                (loop restarts with updated signals)          │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Constitutional Safeguards

| Floor | Safeguard | Implementation |
|-------|-----------|---------------|
| **F2 TRUTH** | Signal detection, not niat inference | `niat_gate.py` operates on observable words |
| **F9 ANTIHANTU** | No soul-reading claim | Decoder reports WHAT was said, not WHY |
| **F10 ONTOLOGY** | AI-only ontology | No model of human interiority |
| **F13 SOVEREIGN** | Human veto absolute | F13 gate at every irreversible action |
| **Adat** | Proper before legal | `adat_registry.py` runs before floor enforcement |

---

## 6. Key Files

| File | Role | Status |
|------|------|--------|
| `runtime/niat_gate.py` | Scar detection, formalization lock, capability membrane | ✅ LIVE |
| `runtime/adat_registry.py` | 7 teras adat, malu_delta, tebus_salah | ✅ LIVE |
| `runtime/_d_layer_contract.py` | D-Layer output contract + scar awareness | ✅ UPDATED |
| `CONSTITUTIONAL_EXTENSION...py` | F14 dead, F0/F15–F17 draft | ✅ UPDATED |
| `docs/specs/NIAT_INFERENCE_RELAY.md` | This spec | ✅ REWRITTEN |
| ~~`schemas/niat_inference.py`~~ | DELETED — HERMES: JANGAN | ❌ REMOVED |
| ~~`runtime/niat_inference_bridge.py`~~ | DELETED — wrong direction | ❌ REMOVED |

---

## 7. Authority

- **Forged:** 2026-06-13 by OPENCLAW on af-forge
- **Corrected:** 2026-06-13 by HERMES ASI — "JANGAN niat-inference log"
- **Sovereign directive:** Arif — "now relay to decoder encoder metabolizer"
- **Doctrine:** DITEMPA BUKAN DIBERI

---

*End of DECODER→ENCODER→METABOLIZER RELAY spec v2.0*
