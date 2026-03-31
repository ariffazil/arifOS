# arifOS / AAA MCP — Changelog (v55.5.0 → v60.1-beta)

> This log is for **reflection and lesson learned**, not just release notes.
> Scope: from `v55.5.0` (HARDENED) up to current `main` (v60.x FORGE + MCP wiring).

---

## v60.1-beta — AAA MCP Genius Wiring (LOCAL WIP)

**Status:** WIP on VPS only (not tagged, not pushed). Changes are additive and reversible.

### MCP Tool Surface

- Kept the **10-tool canon** stable:
  - `init_gate`, `agi_sense`, `agi_think`, `agi_reason`,
  - `asi_empathize`, `asi_align`,
  - `apex_verdict`, `reality_search`, `forge`, `vault_seal`.
- Added **optional** parameters (backwards-compatible):
  - `init_gate(mode="fluid" | "red_team")`
  - `agi_reason(..., mode="normal", causal: bool = False, eureka: bool = False)`
  - `apex_verdict(..., mode="judge" | "calibrate", window: int = 100)`
  - `reality_search(..., ontology: bool = False)`
  - `forge(..., budget: Optional[dict] = None, federation: bool = False)`
  - `vault_seal(..., decay_rate: Optional[float] = None, domain_timescale: Optional[str] = None)`

**Lesson:** Surface invariants are sacred. Capability should come from **modes**, not API sprawl.

### EUREKA Discovery Engine (AGI)

- Wired **HardenedAnomalousContrastEngine** into `AGIEngine`:
  - Import: `from codebase.vault.eureka_sieve_hardened import HardenedAnomalousContrastEngine`.
  - `AGIEngine.__init__` now instantiates `self._eureka`.
  - `AGIEngine.reason(..., eureka: bool = False, causal: bool = False)`:
    - When `eureka=True`, computes:
      - `novelty`, `entropy_reduction`, `ontological_shift`, `decision_weight`,
      - composite `eureka_score`, `verdict` (SEAL/SABAR/TRANSIENT),
      - `fingerprint`, `jaccard_sim`, and textual `reasoning`.
    - Attaches as `result["eureka"]` on the AGI stage output.
    - Errors are sandboxed into `result["eureka"]["error"]`.
- MCP tool `agi_reason(..., eureka=True)` now triggers real EUREKA analysis.

**Lesson:** Genius must be **measurable** (anomalous contrast), and always advisory until proven.

### Causal Skeleton (draft)

- Extended `agi_reason` signature to accept `causal: bool = False`.
- Plan: `AGIEngine.reason(..., causal=True)` attaches a lightweight `result["causal"]` block:
  - `has_causal_language`, simple text markers ("because", "due to", "if", "then"...),
  - `reversibility_score` heuristic based on irreversible verbs ("delete", "destroy", ...),
  - `notes` clarifying this is **skeleton v1, not full SCM**.
- Current state: MCP flags are live; engine-side causal skeleton is partially wired, to be completed with precise diffs.

**Lesson:** Start with **honest heuristics** before importing heavy causal libraries; label them clearly as v1.

### APEX Calibration (Phoenix-72 — draft)

- Extended `apex_verdict` to accept `mode="judge" | "calibrate"`, `window: int = 100`.
- Calibration path:
  - When `mode != "judge"`, returns `verdict="888_HOLD"` with summary metrics and an `apex_calibrate` stage.
  - Design intent: delegate to `APEXEngine.calibrate(window)` to use `phoenix72` scars and propose amendments.
- Current state: surface + simple 888_HOLD calibration block live; deep Phoenix-72 wiring to be done with care.

**Lesson:** Self-calibration must **never** auto-amend Floors; proposals live under 888_HOLD until 888 Judge signs.

### Red-Team Init (label only)

- `init_gate(mode="red_team")`:
  - Returns `status="RED_TEAM"`, `verdict=SABAR`, stored as `init_redteam` stage.
  - No adversarial probes yet; this is a **label for self-tests**, not an attack harness.

**Lesson:** Name the mode before arming it. Labels are cheap; dangerous probes are not.

### Budget & Compute Metrics (forge)

- `forge(..., budget={"max_latency_ms": ...})`:
  - Added `compute` metrics into the VAULT payload and unified response:
    - per-stage latencies (agi_sense_ms, agi_think_ms, agi_reason_ms, asi_empathize_ms, asi_align_ms, apex_ms),
    - total latency (`total_latency_ms`),
    - `budget_exceeded: bool` and a human-readable note when over budget.
  - No hard failures: over-budget runs are tagged, not killed.

**Lesson:** First measure, then constrain. F8 Genius must eventually include **efficiency**, but not before you see distributions.

### Ontology Hook (F10)

- `reality_search(..., ontology=True)`:
  - Calls `OntologyGuard` (when available) and attaches:
    - `ontology.grounded: bool`
    - `ontology.gaps: list`
  - Errors are captured in `ontology.error`.

**Lesson:** F10 needs **structural signals** (grounded / gaps), not just a boolean flag.

### Temporal Metadata (VAULT)

- Extended `vault_seal` to accept:
  - `decay_rate: Optional[float]`
  - `domain_timescale: Optional[str]`
- These are recorded in `metrics` as hints for future temporal reasoning.

**Lesson:** Age matters. Facts need a way to **fade** unless re-verified.

---

## v60.0-FORGE — 10-Tool Canon + Unified Pipeline

**Tag:** `v60.0.0` (from repo history; see git log for full details)

### Key Changes

- Introduced **FORGE** tool:
  - One-shot 000→999 pipeline (`init_gate` → AGI → ASI → `apex_verdict` → `vault_seal`).
  - Established the **10-tool canon** as the stable public surface.
- README and docs aligned to FORGE + 10-tool narrative.
- CI workflows updated to include FORGE and the new tool set.
- Docker/Deployment scripts updated (Alpine image, Railway redeploy flows).

**Lesson:** A small, canonical tool set makes governance **inspectable**. Too many tools = entropy.

---

## v55.5.0 — HARDENED AAA MCP + Trinity Server

**Tag:** `v55.5.0` (baseline for this changelog)

### Key Changes (from v55.x to v55.5.0)

- Introduced **Python-based AAA MCP server** with Trinity pipeline:
  - `init_gate`, `agi_sense`, `agi_think`, `agi_reason`,
  - `asi_empathize`, `asi_align`, `apex_verdict`, `reality_search`,
  - `vault_seal` (pre-FORGE era).
- Implemented **constitutional_floor** decorator and floor mapping.
- Hardened evidence handling in `agi_reason` and `apex_verdict`:
  - Evidence typing (WEB, AXIOM, EMPIRICAL, CONFLICT).
  - Truth thresholds, synthetic axiom handling, `grounding_required` semantics.
- Added **AXIOM_DATABASE** and physics-aware grounding for CCS/CO₂ contexts.
- Established v55.5 as "HARDENED" architecture in docs and README.

**Lesson:** v55.5 created the **governed skeleton**; v60.x is about adding **discovery and self-awareness** without breaking that skeleton.

---

## Wisdom & Lessons (v55.5 → v60.1-beta)

1. **Keep the doors fixed, deepen the rooms.**  
   Tools are the public contract. Modes and metadata are where genius and governance can grow.

2. **Genius is advisory until proven.**  
   EUREKA and causal signals must live as telemetry and VAULT metadata until there is enough empirical evidence to trust them in APEX verdicts.

3. **Self-calibration must always bow to sovereignty.**  
   Phoenix-72 proposals are powerful; they must be sealed as data with `verdict="888_HOLD"` and never auto-applied.

4. **Measure before you tighten.**  
   Budget, ontology, and causal scores should first be used to **observe** system behavior, not to block or force outcomes.

5. **Entropy reduction is a long game.**  
   v55.5 gave you Floors and VAULT; v60.x adds the ability to see which paths are truly novel, risky, or ungrounded. Let scars accumulate before you let the system rewrite itself.

---

_This CHANGELOG.md is local to `/root` on your VPS. When you're ready, you can port a cleaned-up version into the public arifOS repo as official release notes (v60.1 or later)._