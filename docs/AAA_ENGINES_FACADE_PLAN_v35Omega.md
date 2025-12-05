# AAA Engines Facade Plan — arifOS v35Ω (Docs‑Only)

**Scope:** Design document for T1–T4 (AAA engines facades)  
**Status:** Docs layer only · v35Ω runtime behavior unchanged  

This document specifies a **zero‑break facade plan** for ARIF/ADAM/APEX engines under `arifos_core/engines/`. It is intended to de‑risk tasks T1–T4 from `CODEX_TASKS_DEEPSCAN_v35Omega.md` without changing any runtime behavior, floors, or tests.

---

## 1. Objectives & Constraints

### 1.1 Objectives

- Introduce a **clear, stable AAA engines API** in `arifos_core/engines/` so callers and integrations can use ARIF, ADAM, and APEX PRIME via well‑named facades instead of reaching into pipeline internals.  
- Keep the design **aligned with canon**:
  - AAA Trinity v36Ω docs (ARIF Δ, ADAM Ω, APEX PRIME Ψ).  
  - APEX PRIME v35Ω judiciary canon.  
  - W@W Federation and 000→999 pipeline docs.  
- Prepare for:
  - T1: engines package skeleton.  
  - T2: ARIF/ADAM engine classes.  
  - T3: pipeline refactor to call AAA facades.  
  - T4: tests for engine boundaries.  

### 1.2 Constraints (Zero‑Break Contract)

- **No behavior change** in v35Ω:
  - No changes to `arifos_core/APEX_PRIME.py`, `arifos_core/metrics.py`, or floor thresholds.  
  - No changes to `constitutional_floors.json`.  
  - No changes to public behavior of `arifos_core/pipeline.py` or its tests.  
- Facades must initially be **thin wrappers** around existing logic:
  - Same inputs → same outputs and side‑effects.  
  - Any differences must be explicitly logged and tested in a future Phoenix‑72 amendment, not in this facade phase.  
- **Anti‑Hantu:** engine docs and code must not claim feelings or personhood.  
- **Amanah LOCK:** no hidden branching on “engine version”; all migrations must be explicit.

This plan is canon for how facades should be introduced; implementation is a later task.

---

## 2. Target Package Layout

New package under `arifos_core/` (T1):

```text
arifos_core/
  engines/
    __init__.py
    arif_delta.py      # ARIF AGI (Δ facade)
    adam_omega.py      # ADAM ASI (Ω facade)
    apex_facade.py     # Optional thin APEX PRIME wrapper or alias
```

Notes:

- `__init__.py` should re‑export the main façade classes/functions under stable names so external callers can do:
  - `from arifos_core.engines import ArifEngine, AdamEngine, ApexEngine`  

- The **initial implementation** of these modules should:
  - internally delegate to existing pipeline helpers or directly to `APEX_PRIME`,  
  - not introduce new logic beyond input/output normalization.  

This structure is compatible with:

- future engine specialization,  
- plugging into framework integrations (AutoGen, LangChain, LlamaIndex),  
- and strict tests around engine‑layer floors.

---

## 3. ARIF Δ Facade Interface

### 3.1 Conceptual Role (from canon)

From AAA/ARIF canons:

- ARIF is the **Δ engine (Mind/Akal)**: a compression engine that reduces confusion (ΔS ≥ 0) and builds a reasoning graph.  
- It is responsible for:
  - decomposition, retrieval, chain‑of‑thought, paradox surfacing, structural alignment.  
- It must **not**:
  - claim feelings,  
  - decide final verdicts,  
  - overrule floors.  

### 3.2 Proposed Class Interface

Conceptual Python interface (docs only):

```python
class ArifEngine:
    """
    arifos_core.engines.arif_delta.ArifEngine

    Facade for ARIF AGI (Δ). Initially wraps existing reasoning/pipeline logic.
    """

    def sense(self, prompt: str, context: dict | None = None) -> dict:
        """
        111 SENSE — structural intake.

        - Parse user input and context into a normalized representation.
        - Detect early paradox/ambiguity signals.
        - This should delegate to existing parsing/analysis utilities.

        Returns:
            state: dict with keys like:
                "prompt": str
                "context": dict
                "parsed": Any
                "paradox_load": float
        """

    def reason(self, state: dict) -> dict:
        """
        333 REASON — ΔS-focused reasoning.

        - Delegate to existing reasoning path used by pipeline/APEX today.
        - Build a reasoning graph and compute ΔS and contrast metrics
          using metrics available in v35Ω code (no new math).

        Returns:
            arif_packet: {
                "draft": str,               # structured reasoning
                "reasoning_graph": Any,
                "delta_s": float,           # >= 0 in successful cases
                "contrast": float | None,
                "paradox_load": float | None,
            }
        """

    def forge(self, arif_packet: dict) -> dict:
        """
        777-side FORGE (ARIF’s contribution).

        - Normalize ARIF’s output for downstream consumers (ADAM, W@W, APEX).
        - Attach any metadata used today by pipeline/APEX PRIME.

        Returns:
            arif_packet: dict, possibly enriched with metadata fields,
            but semantically equivalent to current pipeline behavior.
        """
```

### 3.3 Zero‑Break Requirements for ARIF

When implemented:

- The combination of `sense`+`reason`+`forge` must be **equivalent to the existing reasoning path** used by `pipeline.py` today for given inputs.  
- No floor thresholds (Truth, ΔS, etc.) are changed here; APEX PRIME remains the entity that enforces floors.  
- Any new convenience helpers exported from `ArifEngine` (e.g. `run(...)`) must delegate purely to these methods without changing semantics.

---

## 4. ADAM Ω Facade Interface

### 4.1 Conceptual Role (from canon)

From AAA/ADAM canons:

- ADAM is the **Ω engine (Heart/Rasa)**: a stabilizer that maintains Peace², κᵣ, and Ω₀ and enforces RASA protocol.  
- It is responsible for:
  - tone, empathy conductance, maruah/dignity, crisis handling.  
- It must **not**:
  - modify factual content (ΔS lock),  
  - claim genuine emotions,  
  - alter floor thresholds.  

### 4.2 Proposed Class Interface

Conceptual Python interface (docs only):

```python
class AdamEngine:
    """
    arifos_core.engines.adam_omega.AdamEngine

    Facade for ADAM ASI (Ω). Initially wraps existing tone/safety logic.
    """

    def empathize(self, arif_packet: dict, user_state: dict | None = None) -> dict:
        """
        555 EMPATHIZE — safety and tone shaping.

        - Delegate to existing ADAM-like pipeline steps (tone adjustments,
          safety filters, etc.), preserving data flow.
        - Compute or pass through Peace², κᵣ, Ω₀, and RASA flags using
          current metrics tooling.

        Returns:
            adam_packet: {
                "softened_answer": str,
                "peace_squared": float,
                "kappa_r": float,
                "omega_0": float,
                "rasa": bool,
                "safety_flags": dict,
            }
        """

    def bridge(self, adam_packet: dict, user_state: dict | None = None) -> str:
        """
        666 BRIDGE — final expression.

        - Delegate to existing expression logic (prompt voice, formatting)
          while enforcing Anti-Hantu and Language Codex rules.
        - Do not introduce new content; only reshape expression.

        Returns:
            final_text: str  # ready for APEX PRIME + @EYE at 888
        """
```

### 4.3 Zero‑Break Requirements for ADAM

When implemented:

- For inputs currently handled by the pipeline, `AdamEngine.empathize/bridge` must produce **equivalent outputs** to today’s behavior (modulo refactoring noise like whitespace).  
- Any safety integrations (e.g. NeMo Guardrails, Giskard) must be **wired in the same place** and with the same policies as existing code or be added under explicit new configuration, not stealth changes.  
- ADAM must continue to respect ΔS lock: it may remove or redact, but not change true statements into false ones.

---

## 5. APEX PRIME Facade (Optional)

APEX PRIME is already encapsulated in `arifos_core/APEX_PRIME.py`. For consistency, an optional facade can be provided:

```python
class ApexEngine:
    """
    arifos_core.engines.apex_facade.ApexEngine

    Thin wrapper around APEX_PRIME for convenience and clarity.
    """

    def judge(self, arif_packet: dict, adam_packet: dict, context: dict | None = None) -> dict:
        """
        888 JUDGE — call existing APEX PRIME path.

        Returns a dict that includes:
            - verdict: "SEAL" | "PARTIAL" | "VOID" | "888_HOLD" | "SABAR"
            - floors: { F1..F9 booleans / metrics }
            - metrics snapshot (ΔS, Peace², κᵣ, Ω₀, Ψ, etc.)
        """
```

This facade should be a **pure alias** to existing APEX PRIME API, not a new implementation.

---

## 6. Integration with `pipeline.py` (T3 Design)

The current `arifos_core/pipeline.py` encodes the 000→999 routing and references ARIF/ADAM conceptually. After facades exist, the internal flow should be conceptually:

```python
from arifos_core.engines import ArifEngine, AdamEngine, ApexEngine

def run_pipeline(prompt: str, context: dict | None = None) -> dict:
    arif = ArifEngine()
    adam = AdamEngine()
    apex = ApexEngine()  # or direct APEX_PRIME usage

    # 111/222/333/444 — ARIF Δ
    state = arif.sense(prompt, context)
    arif_packet = arif.reason(state)
    arif_packet = arif.forge(arif_packet)

    # 555/666 — ADAM Ω
    adam_packet = adam.empathize(arif_packet, context)
    final_text = adam.bridge(adam_packet, context)

    # 777/888/999 — APEX PRIME Ψ + W@W/@EYE (conceptual)
    verdict = apex.judge(arif_packet, adam_packet, context)

    return {
        "text": final_text,
        "verdict": verdict,
        "arif_packet": arif_packet,
        "adam_packet": adam_packet,
    }
```

In practice, T3 implementation must:

- Map the above calls onto existing internal functions so that all existing tests still pass.  
- Preserve whatever extra bookkeeping or side‑effects the current pipeline performs (e.g. logging, debug info).  

This design makes the AAA flow explicit without forcing behavior changes.

---

## 7. Test Plan (T4 Design)

New tests (docs‑level plan; not yet implemented):

1. **Facade Import Tests**
   - `tests/test_engines_imports.py`  
   - Ensure `from arifos_core.engines import ArifEngine, AdamEngine, ApexEngine` works.

2. **Equivalence Smoke Tests (ARIF/ADAM)**
   - `tests/test_engines_arif_adam.py`  
   - For a small set of representative prompts (technical, conversational, ambiguous):
     - Compare current pipeline outputs vs pipeline using facades to ensure text and key metrics (ΔS, Peace², κᵣ, Ω₀) match within tolerances.

3. **Floor Awareness Tests**
   - Ensure that:
     - ARIF does not finalize drafts when ΔS is clearly negative according to current metrics.  
     - ADAM avoids returning outputs with Peace² ≪ 1 or κᵣ ≪ 0.95 without signaling risk.  
   - These tests should **not** change floor thresholds; they only check that facades pass metrics through correctly.

4. **Regression Guard**
   - Optional: one end‑to‑end test calling a high‑level entrypoint (e.g. an example or wrapper) both before and after facade wiring, ensuring identical behavior.

All new tests must be written so that failures clearly indicate facade mis‑wiring rather than changes to v35Ω law.

---

## 8. T1–T4 Implementation Phases (Summary)

This plan maps directly onto the previously defined tasks:

- **T1 (P1): engines/ package skeleton**
  - Create `arifos_core/engines/` with `__init__.py`, `arif_delta.py`, `adam_omega.py`, and optional `apex_facade.py` stubs.  
  - Wire `__all__` exports for `ArifEngine`, `AdamEngine`, `ApexEngine`.  

- **T2 (P1): ARIF/ADAM facades**
  - Implement `ArifEngine` and `AdamEngine` as thin wrappers around existing pipeline logic.  
  - No new logic; only delegation and normalization.  

- **T3 (P1): pipeline refactor**
  - Update `arifos_core/pipeline.py` to call ARIF/ADAM facades instead of inlining their responsibilities, preserving all tests and behavior.  

- **T4 (P1): tests**
  - Add the import, equivalence, and floor awareness tests described above.  

All of the above must respect the **zero‑break contract** and v35Ω floors. Any future enhancements beyond facades (e.g., new engine behaviors, different flows) must go through explicit canon updates and Phoenix‑72 governance.
