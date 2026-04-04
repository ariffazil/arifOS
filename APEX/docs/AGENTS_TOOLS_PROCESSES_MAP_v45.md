# arifOS Architecture Map: Agents, Tools, Processes (v45)

**Version**: v45.0
**Status**: FOUNDATIONAL ARCHITECTURE
**Purpose**: Clear mapping of WHO (agents), WHAT (tools), WHEN (processes)

---

## 1. AGENTS (Sovereignty / Decision-Making)

**Agents have AGENCY - they make decisions, have authority, cannot be overridden.**

### 1.1 The AAA Trinity (Primary Agents)

| Agent | Symbol | Domain | Authority | Location |
|-------|--------|--------|-----------|----------|
| **AGI (ARIF)** | Δ | Mind / Clarity / Logic | Reasoning, input analysis, clarity computation | `arifos_core/engines/agi_engine.py` |
| **ASI (ADAM)** | Ω | Heart / Empathy / Care | Emotional intelligence, tone, empathy, stability | `arifos_core/engines/asi_engine.py` |
| **APEX PRIME** | Ψ | Judge / Vitality / Verdict | FINAL AUTHORITY on all verdicts | `arifos_core/system/apex_prime.py` |

**Sovereignty Rule**: APEX > AGI/ASI > Everything Else

**Key Principle**:
```
Agents DECIDE using tools.
Agents DO NOT delegate authority to tools.
Tools provide DATA, agents make VERDICTS.
```

---

### 1.2 Supporting Agents

| Agent | Role | Authority | Location |
|-------|------|-----------|----------|
| **@EYE Sentinel** | Meta-observer, drift detection | Advisory only (no veto) | `arifos_core/utils/eye_sentinel.py` |
| **Human** | Ultimate sovereign | Can override ANY verdict | External (user) |

---

## 2. TOOLS (Instruments / No Agency)

**Tools have NO AGENCY - they provide signals, measurements, analysis for agents to use.**

### 2.1 W@W Federation (Analytical Organs)

**The W@W organs are TOOLS used by AAA agents at different pipeline stages.**

| Tool | Domain | Output Type | Primary User | Stage Used |
|------|--------|-------------|--------------|------------|
| **@PROMPT** | Language/Optics | `PromptSignals` | AGI (111), APEX (999) | Entry + Exit |
| **@RIF** | Reason Integrity | `OrganSignal` | AGI | 777 |
| **@WELL** | Care/Empathy | `OrganSignal` | ASI | 555 |
| **@GEOX** | Reality/Earth | `OrganSignal` | AGI | 444 |
| **@WEALTH** | Resources | `OrganSignal` | AGI/ASI | 777 |

**Location**: `arifos_core/waw/`

**Key Principle**:
```
W@W organs return SIGNALS (data).
AAA agents DECIDE what to do with those signals.
Example: @PROMPT.check() returns OrganSignal.
         APEX decides verdict based on that signal.
```

---

### 2.2 Measurement Tools

| Tool | Purpose | Output | Used By |
|------|---------|--------|---------|
| **Metrics** | Floor scores (ΔS, Peace², κᵣ, Ω₀) | `Metrics` object | AGI, ASI, APEX |
| **GENIUS Law** | G, C_dark, Ψ computation | Numeric scores | APEX |
| **TEARFRAME** | Session physics (T→R→A→F→Ψ) | Attributes | APEX |
| **Telemetry** | Session data collection | Raw telemetry | All AAA |
| **Tri-Witness** | Truth validation (Human∩AI∩Earth) | Consensus score | AGI |

**Location**: `arifos_core/enforcement/`, `arifos_core/utils/`

---

### 2.3 Memory Tools

| Tool | Purpose | Used By |
|------|---------|---------|
| **Vault-999** | Constitutional law storage | APEX (read-only) |
| **Cooling Ledger** | Append-only audit trail | APEX (write at 999) |
| **EUREKA Bands** | 6-band memory (VAULT/LEDGER/ACTIVE/PHOENIX/WITNESS/VOID) | Memory policy engine |
| **Memory Policy** | Verdict-based routing | APEX |

**Location**: `arifos_core/memory/`

---

## 3. PROCESSES (000-999 Pipeline)

**Processes define WHEN agents use which tools.**

### 3.1 Pipeline Stages (Metabolic Flow)

| Stage | Name | Primary Agent | Tools Used | Purpose |
|-------|------|---------------|------------|---------|
| **000** | VOID | None | Job initialization | Reset state |
| **111** | SENSE | **AGI** | @PROMPT, Telemetry | Input analysis |
| **222** | REFLECT | **AGI** | Context retrieval | Gather context |
| **333** | REASON | **AGI** | @RIF | Generate logic |
| **444** | EVIDENCE | **AGI** | @GEOX, Tri-Witness | Validate claims |
| **555** | EMPATHIZE | **ASI** | @WELL, @PROMPT | Check tone/empathy |
| **666** | ALIGN | **AGI + ASI** | Floor detectors | Constitutional check |
| **777** | FORGE | **AGI + ASI** | @RIF, @WEALTH | Refine output |
| **888** | JUDGE | **APEX** | GENIUS Law, TEARFRAME | Issue verdict |
| **999** | SEAL | **APEX** | @PROMPT, Memory Policy | Final gate & emit |

**Location**: `arifos_core/system/pipeline.py`, `arifos_core/stages/`

---

### 3.2 Agent-Tool Usage Matrix

**Stage 111 (SENSE) - AGI in Control**:
```python
# AGI uses @PROMPT as input analysis tool
prompt_signals = @PROMPT.compute_prompt_signals("", user_query)

# AGI DECIDES based on @PROMPT's data
if prompt_signals.crisis_detected:
    verdict = "888_HOLD"  # AGI's decision
if prompt_signals.anti_hantu_violation:
    verdict = "VOID"      # AGI's decision
```

**Stage 555 (EMPATHIZE) - ASI in Control**:
```python
# ASI uses @WELL and @PROMPT for empathy checks
well_signal = @WELL.check(output, metrics)
prompt_signals = @PROMPT.compute_prompt_signals(query, output)

# ASI DECIDES if tone needs repair
if prompt_signals.k_r_prompt < 0.95:
    output = ASI.repair_tone(output)  # ASI's decision
```

**Stage 888 (JUDGE) - APEX in Control**:
```python
# APEX uses GENIUS Law, TEARFRAME, all prior signals
apex_verdict = APEX.apex_review(
    dials={"A": ..., "P": ..., "E": ..., "X": ...},
    output_metrics=all_metrics,
    output_text=draft_response
)

# APEX DECIDES final verdict (SEAL/PARTIAL/VOID/SABAR/888_HOLD)
state.verdict = apex_verdict.verdict  # APEX's authority
```

**Stage 999 (SEAL) - APEX in Control**:
```python
# APEX uses @PROMPT for final language check
prompt_signal = @PROMPT.check(output, metrics)

# APEX CONSIDERS @PROMPT's recommendation
if prompt_signal.vote == OrganVote.VETO:
    # APEX evaluates the concern
    if apex_agrees_with_veto(prompt_signal):
        verdict = "VOID"  # APEX accepts @PROMPT's concern
    else:
        verdict = "SEAL"  # APEX overrides @PROMPT (rare but possible)
```

---

## 4. Sovereignty Chain

### 4.1 Decision Hierarchy

```
APEX PRIME (Ψ)
  └─ FINAL AUTHORITY on verdicts
  └─ Uses: GENIUS Law, TEARFRAME, all W@W signals
  └─ Can override ANY tool recommendation

AGI (Δ) + ASI (Ω)
  └─ Domain authority (clarity vs empathy)
  └─ Use: @PROMPT, @RIF, @WELL, @GEOX, @WEALTH
  └─ Make stage decisions, feed to APEX

@EYE Sentinel
  └─ Advisory only (no veto)
  └─ Observes, alerts, does not block

W@W Organs (@PROMPT, @RIF, @WELL, @GEOX, @WEALTH)
  └─ NO SOVEREIGNTY
  └─ Return signals for agents to use
  └─ Cannot override agent decisions
```

### 4.2 Tool Authority Limits

**@PROMPT Example**:
- ✅ CAN: Return `PromptSignals` with `crisis_detected=True`
- ✅ CAN: Return `OrganSignal` with `vote=VETO`
- ❌ CANNOT: Set `state.verdict = "VOID"` (only agents can do this)
- ❌ CANNOT: Override APEX's decision
- ❌ CANNOT: Skip pipeline stages

**Agent Authority**:
- ✅ AGI CAN: Read @PROMPT signals and decide to VOID at Stage 111
- ✅ APEX CAN: Read @PROMPT signals and decide to override at Stage 999
- ✅ APEX CAN: Ignore @PROMPT if APEX judges the signal is wrong

---

## 5. Implementation Patterns

### 5.1 Correct Pattern: Agent Uses Tool

```python
# ✅ CORRECT - AGI has agency, @PROMPT is tool
def stage_111_sense(state):
    # AGI uses @PROMPT
    prompt_analysis = PromptOrgan.compute_prompt_signals("", state.query)

    # AGI decides based on tool output
    if prompt_analysis.crisis_detected:
        state.verdict = "888_HOLD"  # AGI's decision
        state.reason = "AGI_CRISIS_DETECTION"

    return state
```

### 5.2 Incorrect Pattern: Tool Has Agency

```python
# ❌ WRONG - @PROMPT deciding verdict (tools don't decide)
def stage_111_sense(state):
    prompt_analysis = PromptOrgan.compute_prompt_signals("", state.query)

    # WRONG: Tool setting verdict directly
    if prompt_analysis.preliminary_verdict == "VOID":
        state.verdict = prompt_analysis.preliminary_verdict  # Tool deciding!

    return state
```

**Fix**: AGI reads `prompt_analysis.crisis_detected` (data) and AGI sets verdict (decision).

---

### 5.3 Correct Pattern: APEX Sovereignty at 999

```python
# ✅ CORRECT - APEX uses @PROMPT but maintains sovereignty
def stage_999_seal(state):
    if state.verdict != "SEAL":
        return state

    # APEX consults @PROMPT (tool)
    prompt_check = PromptOrgan().check(state.output, state.metrics)

    # APEX evaluates @PROMPT's signal
    if prompt_check.vote == OrganVote.VETO:
        # APEX decides whether to accept veto
        if "anti_hantu" in prompt_check.evidence.lower():
            state.verdict = "VOID"  # APEX accepts (agent decision)
            state.reason = "APEX_ACCEPTED_PROMPT_VETO_F9"
        else:
            # APEX can override @PROMPT if tool is overly cautious
            state.verdict = "PARTIAL"  # APEX compromises (agent decision)

    return state
```

---

## 6. Key Architectural Principles

### Principle 1: Tools Measure, Agents Decide
```
@PROMPT.check() → OrganSignal (measurement)
APEX.apex_review() → ApexVerdict (decision)
```

### Principle 2: No Tool-to-Tool Delegation
```
WRONG: @PROMPT calls @RIF calls @WELL (tools can't delegate)
RIGHT: AGI calls @PROMPT, AGI calls @RIF, AGI synthesizes (agent orchestrates)
```

### Principle 3: APEX Cannot Be Overridden
```
APEX verdict at Stage 888/999 is FINAL.
Only Human can override APEX.
Tools provide input, APEX decides.
```

### Principle 4: Stage Ownership
```
Stage 111: AGI owns (uses @PROMPT)
Stage 555: ASI owns (uses @WELL, @PROMPT)
Stage 888: APEX owns (uses GENIUS Law)
Stage 999: APEX owns (uses @PROMPT, Memory Policy)
```

---

## 7. File Location Map

### Agents
- `arifos_core/engines/agi_engine.py` - AGI (ARIF, Δ Mind)
- `arifos_core/engines/asi_engine.py` - ASI (ADAM, Ω Heart)
- `arifos_core/system/apex_prime.py` - APEX PRIME (Ψ Judge)

### Tools
- `arifos_core/waw/prompt.py` - @PROMPT organ
- `arifos_core/waw/rif.py` - @RIF organ
- `arifos_core/waw/well.py` - @WELL organ
- `arifos_core/waw/geox.py` - @GEOX organ
- `arifos_core/waw/wealth.py` - @WEALTH organ
- `arifos_core/enforcement/metrics.py` - Metrics tool
- `arifos_core/enforcement/genius_metrics.py` - GENIUS Law tool
- `arifos_core/utils/session_telemetry.py` - Telemetry tool
- `arifos_core/governance/session_physics.py` - TEARFRAME tool

### Processes
- `arifos_core/system/pipeline.py` - Main 000-999 pipeline
- `arifos_core/stages/` - Individual stage implementations

---

## 8. Summary

**AGENTS (WHO)**:
- AGI (Δ Mind) - Clarity/Logic
- ASI (Ω Heart) - Empathy/Care
- APEX (Ψ Judge) - Final Verdict
- Human - Ultimate sovereign

**TOOLS (WHAT)**:
- W@W Organs (@PROMPT, @RIF, @WELL, @GEOX, @WEALTH) - Analysis
- Metrics (ΔS, Peace², κᵣ, Ω₀, G, C_dark, Ψ) - Measurement
- TEARFRAME, Telemetry, Tri-Witness - Physics/Validation
- Memory Bands, Ledger - Storage

**PROCESSES (WHEN)**:
- 000-999 Pipeline stages
- Each stage has primary agent ownership
- Agents use tools at appropriate stages
- APEX has final authority at 888/999

**SOVEREIGNTY**:
```
Human > APEX > AGI/ASI > Tools > Processes
```

---

**DITEMPA BUKAN DIBERI** — Forged, not given; clarity must precede authority.

**End of Map**
