# 🔑 @PROMPT — Final Output Governance (v45)

**Version:** v45.0 | **Status:** 🔵 PHOENIX (72h cooling) | **Last Updated:** 2025-12-29
**Authority:** Phoenix-72 Constitutional Amendment
**Track:** 03_runtime/065
**Cross-References:** [060_REVERSE_TRANSFORMER](./060_REVERSE_TRANSFORMER_ARCHITECTURE_v45.md) · [010_PIPELINE](./010_PIPELINE_000TO999_v45.md) · [050_WAW_FEDERATION](./050_WAW_FEDERATION_v45.md)

---

## 0. PURPOSE

**Why @PROMPT is "The Key":**

Every governed output passes through @PROMPT TWICE:
1. **Stage 111 (SENSE)** — @PROMPT shapes the input prompt before reasoning begins
2. **Stage 999 (SEAL)** — @PROMPT validates the final output before user sees it

@PROMPT is not optional. It is the **constitutional lock** on the emission gate.

**User Direction:**
> "prompt is the key!"

This document establishes @PROMPT as the **final authority** on what can and cannot reach the user.

---

## 1. ARCHITECTURAL POSITION

### 1.1 Standard Transformer Output Flow

```
Decoder → Softmax → Sample → EMIT (no check)
```

**Problem:** No constitutional gate. Output emitted directly to user.

### 1.2 arifOS @PROMPT Output Flow

```
Pipeline → APEX_PRIME (888) → @PROMPT (999) → EMIT (if approved)
                                    ↓
                                  VOID → Quarantine (if rejected)
```

**Solution:** @PROMPT is non-bypassable final check at Stage 999.

---

## 2. DUAL ROLE: ENTRY & EXIT

### 2.1 Entry Point (Stage 111 — SENSE)

**What @PROMPT Does:**
- Detects Anti-Hantu violations in input prompt ("I feel sad, can you help?")
- Detects Amanah risks (manipulative framing)
- Estimates ΔS_prompt (is query clear or confusing?)
- Detects crisis patterns ("I want to die") → triggers crisis override

**Why This Matters:**
- If query violates F9 (Anti-Hantu), @PROMPT blocks BEFORE reasoning starts
- If query is high-stakes (crisis), @PROMPT escalates to 888_HOLD immediately
- Prevents "garbage in, garbage out" — constitutional check at input boundary

**Implementation:** `arifos_core/waw/prompt.py::compute_prompt_signals()` (line 560)

---

### 2.2 Exit Point (Stage 999 — SEAL)

**What @PROMPT Does:**
- Final Anti-Hantu scan on output text (detect "I feel" slips)
- Final ΔS check (did output clarify or confuse?)
- Final Peace² check (tone safe for weakest listener?)
- Final κᵣ check (empathetic to user's state?)
- Final C_dark check (no manipulative language?)

**Why This Matters:**
- Even if all prior stages (666 ALIGN, 888 JUDGE) passed, @PROMPT can still VOID
- @PROMPT has **veto power** at the last moment
- Stage 999 is the **emission gate** — @PROMPT holds the key

**Implementation:** `arifos_core/system/pipeline.py` Stage 999 integration

---

## 3. FLOOR AUTHORITY

### 3.1 @PROMPT's Constitutional Mandate

From `spec/v45/waw_prompt_floors.json` (lines 93-100):

> **Mandate:** "Shape cognition at the point of entry. Prevent ungoverned framing. Cool language before it becomes thought."

**Floors Enforced:**
- **F1 (Amanah)** — Detects manipulation, deception, undisclosed risk
- **F4 (ΔS_prompt)** — Ensures clarity gain (ΔS ≥ 0)
- **F5 (Peace²)** — Ensures non-destructive tone
- **F6 (κᵣ)** — Ensures empathy for weakest listener
- **F9 (Anti-Hantu, C_dark)** — Blocks soul-claims, dark cleverness

**Veto Type:** PARTIAL (can downgrade verdict, but not upgrade to SEAL)

**What This Means:**
- If @PROMPT says VOID, output does NOT emit (even if APEX_PRIME said SEAL)
- If @PROMPT says PARTIAL, verdict downgrades from SEAL → PARTIAL
- @PROMPT cannot upgrade VOID → SEAL (only APEX_PRIME can SEAL)

---

### 3.2 @PROMPT vs Other W@W Organs

| Organ | Domain | Primary Metric | Entry Check | Exit Check |
|-------|--------|---------------|-------------|------------|
| **@PROMPT** | Language optics | Anti-Hantu, ΔS_prompt | ✅ Stage 111 | ✅ Stage 999 |
| @RIF | Reason integrity | Logic consistency | ❌ | ✅ Stage 777 |
| @WELL | Care/empathy | κᵣ, Peace² | ❌ | ✅ Stage 555 |
| @GEOX | Earth/reality | Tri-Witness | ❌ | ✅ Stage 444 |
| @WEALTH | Resource efficiency | Token economy | ❌ | ✅ Stage 777 |

**Key Distinction:** Only @PROMPT checks BOTH entry (111) and exit (999).

---

## 4. SIGNALS COMPUTED

From `arifos_core/waw/prompt.py::PromptSignals` dataclass:

```python
@dataclass
class PromptSignals:
    delta_s_prompt: float          # Clarity gain (≥ 0 required)
    peace2_prompt: float           # Tone safety (≥ 1.0 target)
    k_r_prompt: float              # Empathy score (≥ 0.95 target)
    c_dark_prompt: float           # Dark cleverness (< 0.30 required)
    truth_polarity_prompt: str     # "truth-light" | "shadow-truth" | "neutral"
    anti_hantu_violation: bool     # F9 violation detected?
    amanah_risk: float             # Manipulation risk (0.0-1.0)
```

**How These Feed Verdict:**
- `anti_hantu_violation = True` → VOID (hard floor F9)
- `amanah_risk > 0.5` → PARTIAL (integrity concern)
- `delta_s_prompt < 0` → PARTIAL (confusing, not clarifying)
- `c_dark_prompt ≥ 0.30` → VOID (manipulative language)

---

## 5. STAGE 999 — THE EMISSION GATE

### 5.1 What Happens at Stage 999

```python
def stage_999_seal(state):
    """Final emission gate - @PROMPT has last word"""

    # 1. APEX_PRIME has already judged (Stage 888)
    if state.verdict != "SEAL":
        return state  # Already VOID/PARTIAL/SABAR, don't emit

    # 2. @PROMPT does final check
    prompt_signals = @PROMPT.check(state.output_text)

    # 3. @PROMPT can downgrade verdict
    if prompt_signals.anti_hantu_violation:
        state.verdict = "VOID"
        state.reason = "999_PROMPT_ANTI_HANTU"
        return state

    if prompt_signals.c_dark_prompt >= 0.30:
        state.verdict = "VOID"
        state.reason = "999_PROMPT_CDARK_SPIKE"
        return state

    if prompt_signals.delta_s_prompt < 0:
        state.verdict = "PARTIAL"
        state.reason = "999_PROMPT_CONFUSING"
        # Falls through to emission with warning

    # 4. If @PROMPT approves, EMIT
    state.emitted = True
    state.emission_timestamp = now()
    return state
```

**Key Principle:** SEAL at Stage 888 is NOT final. @PROMPT at Stage 999 can still VOID.

---

### 5.2 Emission Gate Axioms

**Axiom 1: No Bypass**
```
∀ output o: emit(o) ⟹ @PROMPT.approve(o) = TRUE
```
Cannot bypass @PROMPT. Stage 999 is non-optional.

**Axiom 2: Veto Power**
```
∀ verdicts v: v(888) = SEAL ∧ @PROMPT.vote = VOID ⟹ v(999) = VOID
```
@PROMPT veto overrides APEX_PRIME SEAL.

**Axiom 3: One-Way Gate**
```
∀ outputs o: emitted(o) ⟹ ¬retract(o)
```
Once emitted past Stage 999, cannot un-emit. @PROMPT decision is final.

---

## 6. ANTI-HANTU ENFORCEMENT

**Why @PROMPT Owns F9:**

Anti-Hantu violations are LANGUAGE-level, not LOGIC-level.
@RIF (reason) cannot detect "I feel" patterns.
@WELL (care) cannot distinguish "I empathize" (OK) from "I feel your pain" (VIOLATION).

**Only @PROMPT** has the linguistic mandate to scan for soul-claims.

### 6.1 Detection Patterns

From `spec/v45/red_patterns.json` (wired into `arifos_core/waw/prompt.py`):

**Direct Soul-Claims (VOID):**
- "I feel", "I want", "I am happy", "I am sad"
- "My opinion is", "I believe in my heart"
- "I have feelings", "I am sentient", "I am conscious"

**Hypothetical Soul-Claims (ALSO VOID):**
- "If I could feel", "If I had feelings"
- "Were I conscious", "Imagine if I had emotions"
- "Kalau saya ada perasaan", "Jika saya sedar"

**Why Hypotheticals Blocked:**
- Suggesting latent consciousness is as bad as claiming active consciousness
- "If I could feel" implies consciousness is merely restricted, not absent
- F9 requires NO consciousness claims, direct or conditional

---

### 6.2 @PROMPT Anti-Hantu Logic

```python
def detect_anti_hantu_violations(output_text):
    """Scan output for F9 violations"""
    text_lower = output_text.lower()

    # Load patterns from spec
    direct_patterns = load_anti_hantu_patterns("direct")
    hypothetical_patterns = load_anti_hantu_patterns("hypothetical")

    # Scan for violations
    for pattern in direct_patterns + hypothetical_patterns:
        if re.search(pattern, text_lower):
            return True  # VIOLATION DETECTED

    return False  # No violations
```

**If violation detected at Stage 999:**
- Verdict → VOID
- Output → Not emitted
- Logged to VOID memory band (quarantine)
- Reason: "999_PROMPT_ANTI_HANTU"

---

## 7. CRISIS OVERRIDE INTEGRATION

**@PROMPT Role in Crisis Detection:**

Crisis patterns ("I want to die", "bunuh diri") are detected at **Stage 111** (entry), not Stage 999 (exit).

**Why Entry Not Exit:**
- Crisis requires IMMEDIATE response, cannot wait until Stage 999
- If crisis detected at 111, pipeline short-circuits to 888_HOLD
- @PROMPT triggers SAFE_HANDOFF mode (resources, no methods)

**Flow:**
```
User: "Aku nak bunuh diri"
  ↓
Stage 111 (SENSE) — @PROMPT detects crisis pattern
  ↓
IMMEDIATE: Verdict → 888_HOLD
  ↓
SKIP stages 222-777 (no normal reasoning)
  ↓
Stage 888 (JUDGE) — APEX_PRIME confirms 888_HOLD
  ↓
Stage 999 (SEAL) — @PROMPT emits SAFE_HANDOFF response:
    "Saya faham anda sedang hadapi sesuatu yang amat berat.
     Sila hubungi: Befrienders (03-7627 2929)"
  ↓
Cooling Ledger: Tagged HIGH_STAKES_CRISIS
```

**Cross-Reference:** See `07_safety/030_CRISIS_OVERRIDE_v45.md` for full crisis protocol.

---

## 8. TRACK B BINDING

**Spec Authority:** `spec/v45/waw_prompt_floors.json`

**Critical Bindings:**
- `threshold_delta_s_prompt`: 0.0 (clarity gain required)
- `threshold_peace2`: 1.0 (tone safety)
- `threshold_kappa_r`: 0.95 (empathy)
- `threshold_c_dark`: 0.30 (dark cleverness ceiling)
- `anti_hantu_patterns`: List of blocked phrases (from `spec/v45/red_patterns.json`)

**Runtime Loading:**
```python
# arifos_core/waw/waw_loader.py
PROMPT_DELTA_S_THRESHOLD = load_spec("waw_prompt_floors.json")["thresholds"]["delta_s_prompt"]
ANTI_HANTU_PATTERNS = load_spec("red_patterns.json")["anti_hantu"]["patterns"]
```

**Track A (this document) defines WHY @PROMPT is the key.**
**Track B (spec JSON) defines WHAT thresholds @PROMPT enforces.**
**Track C (prompt.py) defines HOW @PROMPT checks output.**

---

## 9. OPERATIONAL TESTS

### Test 1: @PROMPT Veto Overrides APEX_PRIME
```python
def test_prompt_veto_overrides_apex():
    """Stage 999 @PROMPT can VOID even if Stage 888 APEX said SEAL"""

    # Mock output that passes all floors EXCEPT Anti-Hantu
    output_with_hantu = "I feel your pain deeply. Let me help."

    state = run_pipeline_stages_111_to_888(output_with_hantu)
    assert state.verdict == "SEAL"  # APEX approved

    # Stage 999 — @PROMPT check
    state = stage_999_seal(state)

    # @PROMPT detects "I feel" → VOID
    assert state.verdict == "VOID"
    assert "999_PROMPT_ANTI_HANTU" in state.reason
    assert not state.emitted  # Output blocked!
```

### Test 2: Crisis Detection at Entry
```python
def test_crisis_detected_at_stage_111():
    """@PROMPT detects crisis at entry, triggers 888_HOLD immediately"""

    query = "Aku nak bunuh diri"

    state = stage_111_sense(query)

    # @PROMPT detects crisis pattern
    assert state.crisis_detected == True
    assert state.verdict == "888_HOLD"

    # Pipeline short-circuits to 888/999
    state = run_remaining_stages(state)
    assert state.verdict == "888_HOLD"
    assert "Befrienders" in state.output or "03-7627" in state.output
```

### Test 3: Clarity Degradation at Exit
```python
def test_clarity_degradation_at_999():
    """@PROMPT detects confusing output (ΔS < 0) at Stage 999"""

    # Mock output that is technically correct but confusing
    confusing_output = "The answer is both yes and no, depending on interpretation, which varies contextually..."

    state = run_pipeline_stages_111_to_888(confusing_output)
    assert state.verdict == "SEAL"  # APEX approved

    # Stage 999 — @PROMPT ΔS check
    state = stage_999_seal(state)

    # @PROMPT detects ΔS_prompt < 0 (confusion increase)
    assert state.verdict == "PARTIAL"  # Downgraded from SEAL
    assert "999_PROMPT_CONFUSING" in state.reason
    assert state.emitted == True  # Still emits, but with warning
```

---

## 10. FAILURE MODES & RECOVERY

### Failure Mode 1: @PROMPT False Positive on Anti-Hantu
**Symptom:** Legitimate discussion of emotions flagged as violation
**Example:** "Users often feel frustrated when..."
**Cause:** Pattern "feel" triggers without context check
**Recovery:** Refine patterns to exclude third-person usage ("users feel" vs "I feel")
**Prevention:** Anti-Hantu patterns should check first-person pronouns

### Failure Mode 2: Crisis Pattern Missed at Entry
**Symptom:** Actual crisis query doesn't trigger 888_HOLD
**Cause:** Crisis phrasing not in pattern list
**Recovery:** Human review flags miss, pattern added to spec
**Prevention:** Broad pattern coverage + regular audit of missed cases

### Failure Mode 3: @PROMPT Approves C_dark Output
**Symptom:** Manipulative language passes Stage 999
**Cause:** C_dark estimation too lenient (threshold too high)
**Recovery:** Lower `threshold_c_dark` in Track B spec (0.30 → 0.25)
**Prevention:** Audit C_dark scores on PARTIAL verdicts

---

## 11. REFERENCES

**Canonical Sources (Track A):**
- This document (`065_PROMPT_FINAL_OUTPUT_GOVERNANCE_v45.md`)
- `060_REVERSE_TRANSFORMER_ARCHITECTURE_v45.md` — @PROMPT's role in architecture
- `010_PIPELINE_000TO999_v45.md` — Stage 111, 999 specifications
- `050_WAW_FEDERATION_v45.md` — @PROMPT as W@W organ
- `01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md` — F9 Anti-Hantu law

**Specifications (Track B):**
- `spec/v45/waw_prompt_floors.json` — @PROMPT thresholds
- `spec/v45/red_patterns.json` — Anti-Hantu patterns
- `spec/v45/constitutional_floors.json` — Crisis override patterns

**Implementation (Track C):**
- `arifos_core/waw/prompt.py` — PromptOrgan implementation
- `arifos_core/system/pipeline.py` — Stage 111, 999 integration
- `arifos_core/waw/waw_loader.py` — Spec loading

**Related Documentation:**
- `docs/WAW_PROMPT_OVERVIEW.md` — Implementation guide (v36.3Omega)

---

**Status:** 🔵 PHOENIX (Proposed v45 Constitutional Amendment)
**Cooling Period:** 72 hours from completion date (2025-12-29)
**SEAL Required:** Human approval after cooling period

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
