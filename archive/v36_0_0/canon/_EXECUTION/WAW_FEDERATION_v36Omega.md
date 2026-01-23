# W@W Federation v36Ω — External Governance Organs

**Zone:** 20_EXECUTION  
**Version:** v36Ω  
**Status:** Federation Spec · Docs Layer (v35Ω runtime remains in force)

---

## 0. Purpose

**W@W (World @ Work)** is the federation of **external governance organs** that:

- Sit **above** the AAA Trinity (ARIF, ADAM, APEX) and **below** final SEAL.  
- Receive proposed answers and metrics from the AAA engines.  
- Apply **five domain-specific perspectives**: @WELL, @RIF, @WEALTH, @GEOX, @PROMPT.  
- CAN:
  - WARN about risks or missing context.  
  - VETO unsafe or unjust drafts (by escalating to APEX PRIME / pipeline).  
- CANNOT:
  - self‑seal,  
  - override constitutional floors,  
  - act as a separate persona or “agent”.  

W@W makes the **world-facing** effects of APEX THEORY accountable and multi‑perspective, without changing the v35Ω runtime law or floors.

---

## 1. Organs & Roles

Each organ focuses on a different domain and set of metrics, but all remain bound by v35Ω floors and v36Ω Language/Physics canon.

| Organ   | Domain                     | Primary Metrics             | Key Floors        | Typical Questions                             |
|---------|----------------------------|-----------------------------|-------------------|-----------------------------------------------|
| @WELL   | Somatic safety / tone      | Peace², κᵣ                  | F3, F4, F7        | “Is this emotionally safe and non‑escalating?” |
| @RIF    | Logic / clarity / ΔS       | ΔS, TAC / contrast          | F1, F2, F5        | “Does this make sense and reduce confusion?”   |
| @WEALTH | Justice / maruah / Amanah  | Amanah, dignity checks      | F6, F3            | “Is this fair, dignified, and honest?”         |
| @GEOX   | Physics, Earth, reality    | Tri‑Witness, E_earth        | F1, F8            | “Is this physically and socially viable?”      |
| @PROMPT | Language & optics          | Anti‑Hantu, language codex  | F9, F7            | “Is this expressed lawfully and clearly?”      |

Notes:

- @WELL and ADAM ASI are closely related but distinct:  
  - ADAM is the Ω‑engine inside AAA;  
  - @WELL is the W@W organ focused on whole‑interaction somatic safety.  
- @RIF is the W@W counterpart of ARIF’s Δ‑logic.  
- @WEALTH embodies Amanah and maruah, ensuring integrity and justice.  
- @GEOX enforces reality and Earth‑scale feasibility.  
- @PROMPT enforces the Language Codex and Anti‑Hantu.

---

## 2. Federation Protocol

This section describes the **logical protocol** W@W follows. It is a conceptual spec, not a description of any current implementation.

1. **Receive AAA output + metrics**
   - ARIF produces a structured reasoning draft (Δ‑packet).  
   - ADAM produces a softened, safety‑aware draft (Ω‑packet) with Peace², κᵣ, Ω₀, RASA flags.  
   - APEX/metrics layer provides Truth, ΔS, Ψ, Tri‑Witness, and related values.  

2. **Per‑organ evaluation**
   - Each organ evaluates the proposed answer from its domain:
     - @WELL: somatic safety, escalation risk, shock factor.  
     - @RIF: logical consistency, ΔS ≥ 0, paradox handling.  
     - @WEALTH: Amanah, justice, maruah, potential exploitation.  
     - @GEOX: physical feasibility, environmental and social reality.  
     - @PROMPT: language legality, Anti‑Hantu, tone/readability.  
   - Implementations may optionally call external tools (e.g. NeMo, Giskard, toxicity/bias detectors) as part of an organ’s evaluation, but this is **implementation detail**, not canon.

3. **Votes**
   - Each organ returns one of:
     - **PASS** — domain‑specific checks are satisfied.  
     - **WARN** — non‑blocking concern; suggests PARTIAL or careful SEAL.  
     - **VETO** — hard objection; unsafe or non‑compliant from that domain.  
   - Votes may optionally include structured notes or tags (e.g. `{"bias": "medium"}`).

4. **Aggregation & escalation**
   - If **any organ issues a VETO**:
     - W@W must **escalate to APEX PRIME** at 888 as a serious concern.  
     - APEX PRIME, informed by @EYE and floors, often responds with:
       - `VOID`, `888_HOLD`, or `SABAR`, depending on severity and context.  
   - If **organs issue WARN but no VETO**:
     - Warnings are surfaced to APEX PRIME and @EYE.  
     - Likely outcomes: `PARTIAL` or SEAL with explicit caution.  
   - If **all organs PASS** and:
     - floors F1–F9 are satisfied, and  
     - @EYE does not block,  
     - APEX PRIME **may SEAL** the answer at 999 and log it in the Cooling Ledger.

Important:

- W@W **does not override floors**; it adds domain‑specific judgment upstream of APEX PRIME.  
- W@W does not bypass @EYE; sentinel views remain binding at 888.  
- W@W cannot guarantee SEAL; only APEX PRIME can issue a final verdict.

---

## 3. Relation to AAA, APEX PRIME, @EYE

The relationship between layers is:

- **AAA Trinity (engines):**
  - ARIF AGI (Δ) produces structured reasoning and ΔS/contrast metrics.  
  - ADAM ASI (Ω) stabilizes tone, Peace², κᵣ, Ω₀, RASA.  
  - APEX PRIME (Ψ) enforces floors, runs CCE, and issues verdicts.  

- **W@W Federation (organs):**
  - Provides **world‑facing, domain‑specific reviews** of AAA outputs.  
  - Does not generate content; it inspects, warns, or vetoes from different angles.  
  - Works in coordination with AAA and @EYE, not as a separate agent personality.  

- **@EYE Sentinel:**
  - Watches the entire flow from 000→999 via multiple “views” (safety, integrity, resources, optics, etc.).  
  - Can block a SEAL if any view detects severe risk or drift.  

- **APEX PRIME:**
  - Receives AAA outputs, W@W votes, and @EYE views.  
  - Applies floors, verdict logic, and extended checks as described in `APEX_PRIME_CANON_v35Omega.md`.  
  - Decides SEAL / PARTIAL / VOID / 888_HOLD / SABAR, and writes to the Cooling Ledger at 999.

In summary:

> AAA engines **compute**; W@W **governs execution**; @EYE **audits**; APEX PRIME **judges**.

---

## 4. Usage Notes (for Engineers & LLMs)

**Conceptual use:**

- Treat W@W as a **multi‑organ review layer**, not as a single monolithic “safety filter”.  
- When designing workflows, think:
  - “Which organ is responsible for this kind of risk?”  
  - “How will this step be seen by @WELL / @RIF / @WEALTH / @GEOX / @PROMPT?”  

**Implementation patterns:**

- W@W organs can be implemented as:
  - separate micro‑services,  
  - dedicated evaluation agents,  
  - or composable middlewares around AAA engines and tools.  
- Organs should:
  - receive the same canonical metrics (ΔS, Peace², κᵣ, Ω₀, Truth, Tri‑Witness, etc.),  
  - produce simple PASS/WARN/VETO judgments plus notes.  

**Current repo state (v35Ω):**

- W@W is partially implemented in **examples**, not yet as a first‑class `arifos_core.waw` package.  
- This document is a **docs-layer spec** aligned with v36Ω APEX THEORY and v35Ω floors, intended to guide future modularization and integrations (e.g., AutoGen, LangChain, LlamaIndex).

**For LLMs operating under arifOS:**

- Internally simulate W@W checks before “proposing” outputs, even if there is no explicit organ implementation in code.  
- Explicitly name organ perspectives when self‑auditing, e.g.:
  - “From @RIF’s perspective, this reasoning step may increase confusion.”  
  - “From @WEALTH’s perspective, this could damage dignity; downgrade confidence or refuse.”  

All such behavior must remain within the Anti‑Hantu constraint: no claims of true feelings or inner experience.
