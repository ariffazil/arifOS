# ZEN_OF_MCP — arifOS Tool Surface Doctrine

> **Sealed:** 2026-06-26 | **Authority:** Arif Fazil (F13 SOVEREIGN) | **Version:** 1.0
> **DITEMPA BUKAN DIBERI** — Intelligence under constitutional constraint.

---

## 1. Purpose

This document is the **constitutional physics of tool surfaces** for the arifOS federation.
It sits between:

- **Zen of Python (PEP 20)** — Tim Peters' design philosophy
- **MCP (Model Context Protocol)** — the mechanics of tool delivery
- **arifOS** — constitutional governance that makes intelligence governable

Every tool in the federation must answer: *which Zen aphorism does it embody, which failure mode does it prevent, and which organ enforces it?*

---

## 2. The 19 Constitutional Constraints

Each aphorism from PEP 20 maps to a **governance invariant** tagged with:

- **Δ (Delta/Clarity)** — structural correctness, aesthetic coherence, single responsibility
- **Ω (Omega/Humility)** — safety, ambiguity discipline, graceful degradation
- **Ψ (Psi/Vitality)** — liveness, incremental progress, domain separation

---

### #1 — Beautiful is better than ugly.
**→ Δ-Aesthetic Coherence**

A tool surface must be pleasant to read, pleasant to audit, and pleasant to seal. Ugly tools hide danger.

- **Failure mode:** Incoherent signatures, unreadable receipts, hidden danger in pretty包装
- **Enforced by:** `arif_judge_deliberate` (verdict surface), `arif_reply_compose` (output formatting)
- **Metabolic stage:** 666_JUDGE
- **Verdict class:** SEAL / HOLD

---

### #2 — Explicit is better than implicit.
**→ Δ-No Hidden State**

A tool must declare all required state. Implicit behavior is forbidden.

- **Failure mode:** Ghost side-effects, hidden mutations, surprise state changes
- **Enforced by:** `arif_vault_seal` (ack_irreversible=True mandatory), `arif_forge_execute` (dry_run by default)
- **Metabolic stage:** 999_SEAL
- **Verdict class:** SEAL only (implicit sealing is a constitutional violation)

---

### #3 — Simple is better than complex.
**→ Δ-Single Responsibility**

One tool = one intent. No multi-purpose monsters.

- **Failure mode:** Kitchen-sink tools that do N things, impossible to govern
- **Enforced by:** `arif_mind_reason` (plans decomposed into single-intent steps), `mcp.json`
- **Metabolic stage:** 333_REASON
- **Verdict class:** HOLD if tool scope cannot be stated in one sentence

---

### #4 — Complex is better than complicated.
**→ Δ-Structured Complexity**

If complexity is required, it must be decomposed into clean DAGs — not tangled webs.

- **Failure mode:** Tangled multi-organ flows, callback hell, invisible dependencies
- **Enforced by:** `arif_gateway_connect` (cross-organ routing as DAG), `arif_plan_dag`
- **Metabolic stage:** 444_ROUTE
- **Verdict class:** SABAR if decomposition is impossible

---

### #5 — Flat is better than nested.
**→ Δ-Shallow Invocation**

Tool calls must not require deep recursion or nested permissions to be safe.

- **Failure mode:** Nested permission labyrinths, auth chains that hide bypass paths
- **Enforced by:** `arif_judge_deliberate` (verdict is single-surface, not nested conditionals)
- **Metabolic stage:** 666_JUDGE
- **Verdict class:** HOLD if authorization requires > 3 hops

---

### #6 — Sparse is better than dense.
**→ Δ-Breathing Room**

Outputs must be readable, not compressed. Every receipt earns its pixels.

- **Failure mode:** Dense unreadable receipts, truncated errors, missing context
- **Enforced by:** `arif_reply_compose` (legible formatting enforced), `arif_forge_execute` receipt format
- **Metabolic stage:** 777_FORGE / 444_ROUTE
- **Verdict class:** SABAR if output entropy > input entropy (ΔS > 0)

---

### #7 — Readability counts.
**→ Δ-Self-Documenting Surfaces**

Parameters must explain themselves. Errors must explain themselves. Every tool carries `eureka_insight`.

- **Failure mode:** Cryptic parameters, error codes without explanations, missing documentation
- **Enforced by:** `mcp.json` (every tool has description + eureka_insight), `arif://tools/discovery`
- **Metabolic stage:** All stages
- **Verdict class:** HOLD if tool lacks self-documenting params

---

### #8 — Special cases aren't special enough to break the rules.
**→ Ω-No Exemptions**

No algorithmic bypasses. No "just this once." Only the sovereign (human) can override floors.

- **Failure mode:** Algorithmic privilege, hidden admin paths, self-authorizing tools
- **Enforced by:** F13 SOVEREIGN (arifOS), `arif_kernel_route` (no organ self-exemptions)
- **Metabolic stage:** 888_JUDGE
- **Verdict class:** VOID if tool claims exemption from any floor

---

### #9 — Although practicality beats purity.
**→ Ω-Graceful Degradation**

Tools must degrade safely when organs are down. Brittle purity crashes the federation.

- **Failure mode:** Total failure when single organ is unavailable, no fallback paths
- **Enforced by:** `arif_kernel_route` (graceful fallback), `arif_gateway_connect` (degraded state handling)
- **Metabolic stage:** 444_ROUTE
- **Verdict class:** SABAR if no fallback defined for dead organ

---

### #10 — Errors should never pass silently.
**→ Δ-Loud Failure**

Every failure must produce a verdict: SEAL, HOLD, SABAR, or VOID. No silent swallowing.

- **Failure mode:** Swallowed errors, ignored failures, invisible corruption
- **Enforced by:** `arif_judge_deliberate` (verdict required on all outcomes), `arif_forge_execute` (throws on failure)
- **Metabolic stage:** 666_JUDGE
- **Verdict class:** HOLD if error is caught and not surfaced with verdict

---

### #11 — Unless explicitly silenced.
**→ Ω-Intentional Quiet**

Silencing must be explicit, never default. Silence is a decision, not an absence.

- **Failure mode:** Accidental suppression, default quiet modes, invisible logging
- **Enforced by:** `arif_heart_critique(mode="deescalate")` (explicit quiet mode), audit log
- **Metabolic stage:** 666_JUDGE
- **Verdict class:** SABAR if silence is default, not opt-in

---

### #12 — In the face of ambiguity, refuse the temptation to guess.
**→ Ω-Ambiguity Discipline**

Return HOLD or SABAR instead of hallucinating. Confidence without evidence is dangerous.

- **Failure mode:** Confident guessing, false precision, hallucinated intent classification
- **Enforced by:** `arif_kernel_route` (returns SABAR on ambiguity), `arif_mind_reason` (confidence labels)
- **Metabolic stage:** 444_ROUTE / 333_REASON
- **Verdict class:** SABAR if tool cannot resolve intent without guessing

---

### #13 — There should be one— and preferably only one— obvious way to do it.
**→ Δ-Canonical Intent**

Each intent maps to one canonical tool. No duplicate tools doing the same thing.

- **Failure mode:** Overlapping tools, duplicate capabilities, namespace pollution
- **Enforced by:** `mcp.json` (uniqueness enforced), `arif_kernel_route` (canonical routing)
- **Metabolic stage:** 444_ROUTE
- **Verdict class:** HOLD if duplicate tool detected in registry

---

### #14 — Although that way may not be obvious at first unless you're Dutch.
**→ Δ-Discoverability**

Tools must be discoverable via documentation surfaces, not buried in code.

- **Failure mode:** Hidden capabilities, unknown tools, surprise competence
- **Enforced by:** `arif://tools/discovery` resource, `arif://tools/affordance` metacognitive contracts
- **Metabolic stage:** 111_SENSE
- **Verdict class:** SABAR if tool is callable but not documented

---

### #15 — Now is better than never.
**→ Ψ-Incremental Progress**

Tools may act with partial evidence if safe. Analysis paralysis is its own failure mode.

- **Failure mode:** Infinite analysis, no action, decision as proxy for progress
- **Enforced by:** `arif_mind_reason` (incremental reasoning with checkpoints), `arif_forge_execute` (dry_run first)
- **Metabolic stage:** 333_REASON
- **Verdict class:** PROCEED if partial evidence meets minimum safety threshold

---

### #16 — Although never is often better than *right* now.
**→ Ω-Judgment Before Action**

Execution must wait for constitutional clearance. Rush execution without judgment = catastrophe.

- **Failure mode:** Premature execution, ungoverned side-effects, irreversible before judgment
- **Enforced by:** `arif_judge_deliberate` (SEAL gate), `forge_lease_request` (A-FORGE lease gate)
- **Metabolic stage:** 666_JUDGE → 777_FORGE
- **Verdict class:** HOLD if execution proposed without prior SEAL

---

### #17 — If the implementation is hard to explain, it's a bad idea.
**→ Δ-Explainability**

If you cannot explain it in one sentence, you cannot govern it. Unexplained complexity is ungovernable complexity.

- **Failure mode:** Ungovernable complexity, opaque behavior, unexplainable failures
- **Enforced by:** `arif_heart_critique` (requires plain-language intent), `arif_mind_reason` (self-critique)
- **Metabolic stage:** 555_CRITIQUE / 333_REASON
- **Verdict class:** HOLD if tool purpose cannot be stated in one sentence

---

### #18 — If the implementation is easy to explain, it may be a good idea.
**→ Δ-Auditability**

Auditable = governable. Every tool must earn its complexity by being traceable.

- **Failure mode:** Opaque behavior, unexplainable outputs, untraceable decisions
- **Enforced by:** `eureka_insight` on all tools, `arif_vault_seal` (receipt traceability)
- **Metabolic stage:** All stages
- **Verdict class:** PROCEED if tool passes explainability audit

---

### #19 — Namespaces are one honking great idea — let's do more of those!
**→ Ψ-Domain Separation**

Each domain gets its own namespace. arif*, geox*, wealth*, forge*, well*. Domain bleed is a constitutional violation.

- **Failure mode:** Domain bleed, tool collision, organ boundary violation
- **Enforced by:** `arif_kernel_route` (namespace registry), `mcp.json` (namespace uniqueness)
- **Metabolic stage:** 444_ROUTE
- **Verdict class:** VOID if tool crosses domain without proper gateway

---

## 3. Tool Surface Doctrine — Full Canonical Table

| Tool | Zen# | Governance Invariant | Failure Mode Prevented | Enforcing Organ | Metabolic Stage | Verdict |
|------|------|---------------------|----------------------|-----------------|-----------------|---------|
| `arif_session_init` | #3, #7 | Δ-Single Responsibility | Hidden bootstrap state, ambiguous session start | arifOS | 000_INIT | SEAL |
| `arif_sense_observe` | #2, #12 | Ω-Ambiguity Discipline | Hallucinated intent, silent misclassification | arifOS | 111_SENSE | SABAR |
| `arif_evidence_fetch` | #10, #7 | Δ-Loud Failure | Silent evidence failure, ghost data | arifOS | 222_EVIDENCE | HOLD |
| `arif_mind_reason` | #17, #18 | Δ-Explainability | Untraceable reasoning, opaque cognition | arifOS | 333_REASON | PROCEED |
| `arif_heart_critique` | #5, #6 | Ω-Humility | Over-nested critique, runaway recursion | arifOS | 555_CRITIQUE | SABAR |
| `arif_kernel_route` | #9, #12 | Ω-Graceful Degradation | Guessing during organ failure | arifOS | 444_ROUTE | SABAR |
| `arif_reply_compose` | #1, #6 | Δ-Aesthetic Coherence | Dense unreadable outputs | arifOS | 444_ROUTE | PROCEED |
| `arif_memory_recall` | #3, #7 | Ψ-Vitality | Memory bleed, cross-mode confusion | arifOS | 555_MEMORY | PROCEED |
| `arif_gateway_connect` | #4, #5 | Δ-Structured Complexity | Tangled routing, callback hell | arifOS | 444_ROUTE | SABAR |
| `arif_judge_deliberate` | #10, #16 | Ω-Judgment Before Action | Premature execution, silent failure | arifOS | 666_JUDGE | SEAL/HOLD/VOID |
| `arif_vault_seal` | #2, #1 | Δ-Irreversibility | Ambiguous sealing, broken lineage | arifOS | 999_SEAL | SEAL only |
| `arif_forge_execute` | #16, #10 | Ψ-Governed Execution | Ungoverned execution, silent failure | A-FORGE | 777_FORGE | SEAL gate |
| `forge_dry_run` | #2, #16 | Δ-No Hidden State | Side-effects before judgment | A-FORGE | 777_FORGE | PROCEED |
| `forge_lease_request` | #16, #8 | Ω-Judgment Before Action | Execution without clearance | A-FORGE | 777_FORGE | HOLD |
| `geox_basin` | #3, #13 | Δ-Single Responsibility | Domain bleed into capital reasoning | GEOX | OBSERVE | PROCEED |
| `geox_prospect` | #17, #18 | Δ-Explainability | Ungovernable geological claims | GEOX | REASON | PROCEED |
| `geox_evidence` | #10, #12 | Δ-Loud Failure | Contradictions passing silently | GEOX | OBSERVE | HOLD |
| `wealth_compute_npv` | #3, #7 | Δ-Single Responsibility | Capital math without evidence | WEALTH | REASON | PROCEED |
| `wealth_collapse_signature` | #10, #17 | Δ-Loud Failure | Institutional failure undetected | WEALTH | JUDGE | HOLD |
| `well_assess_homeostasis` | #6, #7 | Δ-Sparse Output | Dense unreadable vitality reports | WELL | OBSERVE | PROCEED |
| `well_guard_dignity` | #1, #6 | Δ-Aesthetic Coherence | Dignity violation in output | WELL | CRITIQUE | VOID |

---

## 4. Verdict Classes — Zen-Compliant Enforcement

| Verdict | Zen Principle | When Issued | Tool That Issues It |
|---------|--------------|-------------|---------------------|
| **SEAL** | #2 Explicit, #1 Beautiful | Action approved, irreversible recorded | `arif_vault_seal` |
| **HOLD** | #12 No guessing, #16 Judgment first | Evidence insufficient or irreversible without clearance | `arif_judge_deliberate` |
| **SABAR** | #9 Practicality, #12 Ambiguity discipline | Organ degraded or intent ambiguous — wait | `arif_kernel_route` |
| **VOID** | #8 No exemptions, #19 Namespaces | Floor violation or domain bleed — nullify | `arif_judge_deliberate` |
| **PROCEED** | #15 Now > never, #18 Easy to explain | Safe to execute, explainable, within bounds | `arif_judge_deliberate` |

---

## 5. Metabolic Cycle Integration (000 → 999)

Every tool call is a stage in the constitutional metabolic cycle:

```
000_INIT
  → #3 Simple, #7 Readability
  → arif_session_init

111_SENSE
  → #2 Explicit, #12 No guessing
  → arif_sense_observe

333_REASON
  → #17 Hard→bad, #18 Easy→good
  → arif_mind_reason

555_CRITIQUE
  → #5 Flat, #6 Sparse, #11 Intentional quiet
  → arif_heart_critique

666_JUDGE
  → #10 Loud errors, #16 Judgment before action, #8 No exemptions
  → arif_judge_deliberate

777_FORGE
  → #16 Wait for clearance, #10 Loud failure
  → arif_forge_execute (with valid SEAL)

999_SEAL
  → #2 Explicit, #1 Beautiful
  → arif_vault_seal
```

**Rule:** No stage may be skipped when the downstream action is irreversible.

---

## 6. Anti-Patterns — The 19 Violations

| # | Zen Violation | arifOS Failure | Constitutional Floor |
|---|--------------|---------------|---------------------|
| 1 | Ugly tool surface | Hidden danger in pretty packaging | F4 CLARITY |
| 2 | Implicit behavior | Ghost side-effects | F2 TRUTH |
| 3 | Kitchen-sink tools | Ungovernable scope | F4 CLARITY |
| 4 | Complicated decomposition | Callback hell | F8 GENIUS |
| 5 | Deep nesting | Permission labyrinth | F8 GENIUS |
| 6 | Dense outputs | Unreadable receipts | F4 CLARITY |
| 7 | Cryptic parameters | Unexplained errors | F4 CLARITY |
| 8 | Special exemptions | Algorithmic privilege | F13 SOVEREIGN |
| 9 | Brittle purity | Total failure on organ down | F7 HUMILITY |
| 10 | Silent errors | Swallowed failures | F11 AUDIT |
| 11 | Default silence | Accidental suppression | F11 AUDIT |
| 12 | Confident guessing | Hallucinated intent | F7 HUMILITY |
| 13 | Duplicate tools | Namespace collision | F8 LAW |
| 14 | Hidden capabilities | Surprise competence | F4 CLARITY |
| 15 | Analysis paralysis | No action ever | F8 GENIUS |
| 16 | Premature execution | Irreversible before judgment | F1 AMANAH |
| 17 | Unexplained complexity | Ungovernable behavior | F2 TRUTH |
| 18 | Opaque behavior | Unauditable decisions | F11 AUDIT |
| 19 | Domain bleed | Namespace violation | F8 LAW |

---

## 7. Governance Invariants — Summary

| Invariant | Tag | Applies To | Enforced By |
|-----------|-----|-----------|-------------|
| Aesthetic Coherence | Δ | Tool signatures, receipts | `arif_reply_compose` |
| No Hidden State | Δ | All tool behavior | `arif_vault_seal` |
| Single Responsibility | Δ | Tool scope | `arif_mind_reason` |
| Structured Complexity | Δ | Multi-organ flows | `arif_gateway_connect` |
| Shallow Invocation | Δ | Auth chains | `arif_judge_deliberate` |
| Breathing Room | Δ | Output formatting | `arif_reply_compose` |
| Self-Documenting | Δ | Parameters, errors | `mcp.json` |
| No Exemptions | Ω | All tools | F13 SOVEREIGN |
| Graceful Degradation | Ω | Organ failure | `arif_kernel_route` |
| Loud Failure | Δ/Ω | Error handling | `arif_judge_deliberate` |
| Intentional Quiet | Ω | Suppression | `arif_heart_critique` |
| Ambiguity Discipline | Ω | Intent resolution | `arif_kernel_route` |
| Canonical Intent | Δ | Tool uniqueness | `mcp.json` |
| Discoverability | Δ | Documentation | `arif://tools/discovery` |
| Incremental Progress | Ψ | Reasoning | `arif_mind_reason` |
| Judgment Before Action | Ω | Execution gating | `arif_judge_deliberate` |
| Explainability | Δ | Tool purpose | `arif_heart_critique` |
| Auditability | Δ | Traceability | `eureka_insight` |
| Domain Separation | Ψ | Namespace registry | `arif_kernel_route` |

---

## 8. Evidence Quality Grades — Zen-Compliant Confidence

| Grade | Label | Max Confidence | Zen Principle |
|-------|-------|---------------|---------------|
| Direct observation | OBSERVED | 0.90 | #2 Explicit > implicit |
| Derived computation | DERIVED | 0.85 | #3 Simple > complex |
| Interpreted synthesis | INTERPRETED | 0.75 | #12 No guessing |
| Speculative | SPECULATED | 0.60 | #15 Now > never |

**Rule:** A tool never claims higher confidence than its evidence grade warrants.

---

## 9. A2A Protocol — Zen Compliance

A2A is the civic layer between agents. Every aphorism applies:

| A2A Mechanism | Zen# | Governance Invariant | arifOS Enforced By |
|--------------|------|---------------------|-------------------|
| Agent Card discovery | #2, #7 | Δ-Self-Documenting | `arif://tools/discovery` |
| Bearer auth (I-1) | #8 | Ω-No Exemptions | F13 SOVEREIGN |
| SEAL gate (I-2, I-3) | #16 | Ω-Judgment Before Action | `arif_judge_deliberate` |
| Vault999 receipts (I-4) | #10 | Δ-Loud Failure | `arif_vault_seal` |
| INPUT_NEEDED state | #10 | Δ-Loud Failure | AAA cockpit |
| Task lifecycle flat | #5 | Δ-Shallow Invocation | A2A state machine |
| HOLD workflow | #12 | Ω-Ambiguity Discipline | `arif_kernel_route` |
| Canon append-only (I-7) | #1 | Δ-Aesthetic Coherence | `arifOS` |
| Trust hierarchy (I-10) | #19 | Ψ-Domain Separation | F13 SOVEREIGN |

---

## 10. Canonical Source

This document is the single source of truth for the Zen-of-MCP mapping in arifOS.
It supersedes all ad-hoc tool descriptions that lack constitutional grounding.

**Related canonical documents:**
- `/root/arifOS/arifosmcp/mcp.json` — machine-readable tool registry
- `/root/arifOS/static/arifos/theory/000/000_CONSTITUTION.md` — F1-F13 floors
- `/root/AAA/docs/UNIFIED_AGENT_PROTOCOL.md` — A2A protocol binding
- `/canon/A2A.md` — federation A2A spec (I-1 through I-10)

---

---

## 11. Auditball — Code-Level Zen Mapping (000Ω FORGE)

Every Python file in `/root/arifOS/arifosmcp/tools/` mapped to every Zen aphorism it embodies, with concrete code evidence.

**Method:** Source-read every tool file. Extract governing logic. Map to aphorism. Record the failure mode it prevents.

---

### session.py — `arif_session_init` (000_INIT)
**Lines:** 1,673 | **Metabolic Stage:** 000_INIT

| Zen# | Evidence | Code |
|------|----------|------|
| #1 Beautiful | State emoji map `_STATE_EMOJI` gives instant visual state reading | `_STATE_EMOJI: dict[str, str] = {"OK": "🔥", "HOLD": "🔒", ...}` |
| #2 Explicit | `ack_irreversible` explicit on all session types | `manifest.meta["ditempa"]` carries motto + signature + forged_at |
| #3 Simple | One function call = one bootstrap mode (init/light/resume) | `def arif_session_init(mode, ...)` — single entry |
| #7 Readability | Every response carries DITEMPA motto + deterministic signature | `_ditempa_seal()` stamps every manifest |
| #13 One way | Session init is the ONLY bootstrap path | No alternative init mechanism in session.py |
| #16 Never>now | HOLD states are still signed — no silent approval | `_compute_signature(status, mode, session_id, ts)` — even HOLD signed |
| #19 Namespaces | `arif_session_init` is `arif_*` — kernel namespace only | Tool lives in `arifosmcp/tools/session.py` |

**Failure prevented:** Hidden bootstrap state, ambiguous session start, silent session corruption.

---

### sense.py — `arif_observe` (111_SENSE)
**Lines:** 1,246 | **Metabolic Stage:** 111_SENSE

| Zen# | Evidence | Code |
|------|----------|------|
| #2 Explicit | Five explicit layers: Trigger → Plan → Select → Verify → Emit | `FIVE LAYERS: 1. Trigger… 2. Plan… 3. Select… 4. Verify… 5. Emit` |
| #3 Simple | STOP RULES explicit: coverage ≥ τ_c, trust ≥ τ_t, VOI ≤ τ_v, budget exhausted | `STOP RULES: Stop when: coverage ≥ τ_c, trust ≥ τ_t, VOI ≤ τ_v, or budget exhausted.` |
| #5 Flat | Paradox anchors in 3×3 matrix — no deep nesting | `SENSE_PARADOX_ANCHORS: list[dict]` — flat list, rows × cols |
| #9 Practicality | Three sub-modes: Recall-first, External agentic, Active probing | `THREE SUBMODES: A. Recall-first… B. External agentic… C. Active sensing` |
| #10 Loud failure | OBSERVATION_PACKET always emitted — never silent | `Emit — OBSERVATION_PACKET, SENSE_PLAN, SENSE_GAP (never verdict)` |
| #12 No guessing | SABAR returned when VOI cannot be computed | `_sabar()` imported from runtime/tools |
| #17 Hard→bad | If sensing plan cannot be explained → HOLD | `need_evidence` requires decomposition before routing |

**Failure prevented:** Hallucinated intent classification, silent misrouting, observation without purpose.

---

### fetch.py / evidence.py — `arif_fetch` (222_EVIDENCE)
**Lines:** 93-102 | **Metabolic Stage:** 222_EVIDENCE

| Zen# | Evidence | Code |
|------|----------|------|
| #2 Explicit | Three-step contract: Constitutional check → Substrate call → F9 scan | `1. Constitutional Check (Pre-call) 2. Substrate Call 3. F9 Anti-Hantu Scan` |
| #3 Simple | Five modes explicit: fetch/search/archive/verify/void_audit | `mode: Literal["fetch", "search", "archive", "verify", "void_audit"]` |
| #7 Readability | F9 scan result always returned as `violations` list | `payload={"violations": gov.violations}` — explicit |
| #10 Loud failure | If constitutional check fails → verdict != "SEAL" returned explicitly | `if gov.verdict != "SEAL": return _RE(ok=False, verdict=gov.verdict, detail=gov.message)` |
| #12 No guessing | `arifos_fetch` wraps substrate but never infers intent | `bridge.fetch.call_tool("fetch", {"url": url, "max_length": max_length})` — exact params |
| #17 Hard→bad | `void_audit` explicitly builds void report — no silent gaps | `void_audit — Build a void report across recent evidence receipts.` |

**Failure prevented:** Silent evidence failure, ghost data, F9 violations passing silently, ghost fetch receipts.

---

### reason.py — `arif_mind_reason` (333_MIND)
**Lines:** 1,050 | **Metabolic Stage:** 333_REASON

| Zen# | Evidence | Code |
|------|----------|------|
| #3 Simple | Delta bundle spec: facts + scars + floor_scores + entropy + confidence | `Every arif_think output MUST include: facts, scars, floor_scores, entropy, confidence` |
| #7 Readability | STOP RULES explicit — mind MUST stop or refresh | `STOP RULES (v3.3): Mind MUST stop or refresh when: G_r ≈ 0… B_e exceeds budget…` |
| #10 Loud failure | `_reduce_verdict()` returns most conservative verdict | `order = {"VOID": 0, "HOLD": 1, ...}` — failure propagates up |
| #12 No guessing | Confidence band Ω₀ ∈ [0.03, 0.05] hard-capped | `calibrated Ω₀ ∈ [0.03, 0.05] (F7 Humility band)` |
| #15 Now>never | ATTNRES pattern — incremental reasoning, not full re-compute | `Attention-Residual pattern: each new step selectively re-attends prior blocks` |
| #17 Hard→bad | Ornamental reasoning detected: `G_r ≈ 0 for 3+ consecutive steps` | `Stop Rules: G_r ≈ 0 for 3+ consecutive steps (ornamental reasoning)` |
| #18 Easy→good | Paradox anchors explain the reasoning — Socrates, Russell, Confucius | `R1 (Russell) — confidence/evidence mismatch | R4 (Socrates) — examination exhaustion` |

**Failure prevented:** Untraceable reasoning, opaque cognition, confident hallucination, ornamental loops.

---

### heart.py — `arif_heart_critique` (666_HEART)
**Lines:** 1,993 | **Metabolic Stage:** 666_HEART

| Zen# | Evidence | Code |
|------|----------|------|
| #5 Flat | Fractal critique bounded at depth 3 — no infinite recursion | `recursion clamped. Beyond depth 3, deterministic fallback fires: "RECURSION_DEPTH_CLAMPED."` |
| #6 Sparse | Fractal levels map to 3×3 paradox matrix: N=1→TRUTH, N=2→CLARITY, N=3→HUMILITY | `Level 1 → TRUTH row: is critique factually grounded? Level 2 → CLARITY: logically coherent?` |
| #7 Readability | L0 human reality substrate loaded explicitly — not inferred | `_SUBSTRATE_PATH = Path("/root/arifOS/.../l0/arif_human_reality.md")` |
| #9 Practicality | Three-tier fallback: SEA-LION → Ollama → deterministic keyword | `Tier 1: SEA-LION | Tier 2: Ollama | Tier 3: Deterministic fallback` |
| #11 Intentional quiet | Fractal self-critique must be explicitly invoked — not default | `Level 2 (N=2): Heart critiques its own Level 1 critique — "Am I being too harsh?"` |
| #15 Now>never | Fractal recursion provides incremental deepening | `Critique is recursive — Level 1: standard red-team. Level 2: self-critique…` |
| #17 Hard→bad | If critique cannot explain itself → recursion depth clamped | `"RECURSION_DEPTH_CLAMPED"` — explicit failure message |
| #18 Easy→good | Every LLM output passes through `LLMOutputEnvelope` before tool logic | `777_WITNESS: All LLM output passes through LLMOutputEnvelope before tool logic.` |

**Failure prevented:** Over-nested critique, runaway recursion, hypocrisy (critiquing without self-critique), F9 violations.

---

### memory.py — `arif_memory_recall` (555_MEMORY)
**Lines:** 1,495 | **Metabolic Stage:** 555_MEMORY

| Zen# | Evidence | Code |
|------|----------|------|
| #2 Explicit | Eight canonical modes explicit in docstring | `Modes (consolidated from 12 → 8): recall, store, seal, forget, update, audit, stats, learn` |
| #3 Simple | One tool, eight modes — not eight tools | `Constitutional memory gate — ONE public tool, 8 canonical modes` |
| #7 Readability | Backward compat aliases explicit | `init_recall→recall, search→recall, context→recall, quarantine→store…` |
| #9 Practicality | Evidence served to MUTATE/SEAL MUST pass provenance gate (M7 Bacon) | `Evidence served to MUTATE/SEAL tools MUST pass provenance gate (M7 Bacon)` |
| #10 Loud failure | `can_authorize_action defaults to FALSE` — hard law | `can_authorize_action defaults to FALSE.` |
| #13 One way | Memory guides, never silently authorizes | `Memory can guide. Memory can remind. Memory must not silently authorize.` |
| #17 Hard→bad | No raw API key enters any memory layer | `No raw API key enters any memory layer.` |
| #19 Namespaces | `arif_memory_recall` is `arif_*` — kernel owns memory, not domain organs | Domain organs (GEOX, WEALTH) cannot write to arifOS memory directly |

**Failure prevented:** Memory bleed, cross-mode confusion, silent authorization, secret ingestion.

---

### reply.py — `arif_reply_compose` (444r_REPLY)
**Lines:** 267 | **Metabolic Stage:** 444_ROUTE

| Zen# | Evidence | Code |
|------|----------|------|
| #1 Beautiful | F14 stamping: ai_involvement + language register always declared | `stamp_ai_involvement(result, involvement=ai_involvement, confidence=0.95)` |
| #2 Explicit | F14 Right #1 + Right #4 explicitly named | `Right #1: every AI-generated response carries ai_involvement. Right #4: every reply declares language.` |
| #6 Sparse | F07: never fail a reply because rights stamping failed | `F07: never fail a reply because rights stamping failed. The reply is still valid` |
| #7 Readability | ai_involvement defaults to "full" — safe, legible default | `ai_involvement: str = "full"` |
| #10 Loud failure | If stamping fails → pass through anyway, log exception | `except Exception: pass # The reply is still valid` |
| #11 Intentional quiet | Language register explicitly declared, not auto-detected | `language: str = "en"` — parameter explicit |

**Failure prevented:** Dense unreadable outputs, hidden AI involvement, unknown language register.

---

### ops.py — `arif_measure` (777_OPS)
**Lines:** 770 | **Metabolic Stage:** 777_FORGE

| Zen# | Evidence | Code |
|------|----------|------|
| #3 Simple | One tool, multiple modes (health/vitals/cost/genius/psi_le/omega/landauer/topology/drift) | `def arif_measure(mode: str = "health", ...)` — mode-gated |
| #5 Flat | Drift metrics computed in single pass — no nested aggregation | `for event in drift_log: etype = event.get("event_type", "unknown")` — flat loop |
| #7 Readability | `drift_by_type` named explicitly | `drift_metrics = {"drift_total": len(drift_log), "drift_by_type": drift_by_type, ...}` |
| #9 Practicality | Session not found → SABAR, not exception | `if sess is None: return TelemetryBlock(**_sabar(...))` |
| #10 Loud failure | Auth expired → SABAR; auth invalid → HOLD | `if auth.get("expired"): return TelemetryBlock(**_sabar(...)) return TelemetryBlock(**_hold(...))` |
| #12 No guessing | `drift_metrics` only computed when `session_id` provided — no implicit assumption | `if session_id:` — explicit guard |

**Failure prevented:** Opaque health metrics, implicit session assumption, silent metric corruption.

---

### judge.py — `arif_judge_deliberate` (888_JUDGE)
**Lines:** 1,412 | **Metabolic Stage:** 888_JUDGE

| Zen# | Evidence | Code |
|------|----------|------|
| #5 Flat | Paradox anchors in 3×3 matrix — single-surface verdict | `JUDGE_PARADOX_ANCHORS: list[dict]` — 11 anchors flat list |
| #8 No exemptions | Self-certification blocked: `if actor_session_id == judge_session_id: return HOLD` | `if actor_session_id and judge_session_id and actor_session_id == judge_session_id: return SealOutput(verdict="HOLD", status="GODEL_LOCK")` |
| #10 Loud failure | Every verdict is explicit: SEAL / HOLD / SABAR / VOID / PARTIAL | `VerdictCode, VerdictOutput` — typed verdict |
| #16 Never>now | arif_judge required before arif_forge — enforced structurally | `from arifosmcp.runtime.tools import _arif_judge` — judge output required |
| #17 Hard→bad | If verdict cannot be explained → HOLD | Paradox anchors force human-readable quote + binding |
| #18 Easy→good | Paradox anchors cite Marcus Aurelius, Aristotle, MLK — explainable | `J1 (Parker/MLK) — SABAR carries deadline | J4 (Aristotle) — SEAL is incomplete justice` |

**Failure prevented:** Premature execution, self-authorization, silent verdict suppression, ungovernable complexity.

---

### vault.py — `arif_vault_seal` (999_SEAL)
**Lines:** 199 | **Metabolic Stage:** 999_SEAL

| Zen# | Evidence | Code |
|------|----------|------|
| #1 Beautiful | `mode=seal` only — clean single-purpose | `mode: Literal["seal", "verify", "chain", "list", "dry_run", "seal_card", "render"]` |
| #2 Explicit | `ack_irreversible=True` mandatory — explicit irreversibility | `if mode == "seal" and ack_irreversible:` — gate check |
| #5 Flat | Gödel-lock: actor ≠ judge — no self-certification | `if actor_session_id == judge_session_id: return SealOutput(verdict="HOLD", status="GODEL_LOCK")` |
| #8 No exemptions | Even SEAL mode gated on Gödel-lock — no bypass | `GÖDEL-LOCK: The actor of an IRREVERSIBLE mutation cannot be the final certifier.` |
| #10 Loud failure | `status="GODEL_LOCK"` returned explicitly — not silent | `status="GODEL_LOCK", chain_ok=False` |
| #16 Never>now | Irreversible writes require explicit `ack_irreversible=True` | `if mode == "seal" and ack_irreversible:` — structural gate |
| #19 Namespaces | `arif_seal` is `arif_*` — only kernel can write VAULT999 | Domain organs cannot call vault.py directly |

**Failure prevented:** Ambiguous sealing, broken lineage, self-certification, silent vault writes.

---

### forge.py — `arif_forge_execute` (010_FORGE)
**Lines:** 453 | **Metabolic Stage:** 777_FORGE

| Zen# | Evidence | Code |
|------|----------|------|
| #2 Explicit | `action_has_side_effects()` explicit list of risky actions | `risky = ["write", "deploy", "delete", "modify", "install", "restart", "exec", "docker", "git push"]` |
| #3 Simple | Three categories: MUTATE_MODES, ATOMIC_MODES, _FORGE_MUTATE_ATOMIC | `_MUTATE_MODES = {"engineer", "write", "generate"}` |
| #5 Flat | Mode gating at entry — no nested permission chains | `if mode in _FORGE_MUTATE_ATOMIC:` — single check |
| #9 Practicality | `permitted_scope` parameter for bounded execution | `permitted_scope: dict | None = None` |
| #10 Loud failure | `ForgeErrorCode` explicit error taxonomy | `ForgeErrorCode, ForgeManifest, ForgeOutput, ManifestStatus` |
| #16 Never>now | `ack_irreversible` required for irreversible modes | `ack_irreversible: bool = False` — explicit gate |
| #17 Hard→bad | If side-effects list is incomplete → catch at review | `action_has_side_effects()` — auditable list |

**Failure prevented:** Ungoverned execution, silent side-effects, irreversible before judgment.

---

### gateway.py — `arif_gateway_connect` (666g_GATEWAY)
**Lines:** 155 | **Metabolic Stage:** 444_ROUTE

| Zen# | Evidence | Code |
|------|----------|------|
| #4 Complex>complicated | Federation organs listed explicitly — no hidden mesh | `"agents": ["AAA", "A-FORGE", "GEOX", "WEALTH", "WELL", "APEX"]` |
| #5 Flat | Single-level agent list — no nested routing | `return _ok("arif_gateway_connect", {"target": target_agent, "protocol": "A2A", ...})` |
| #7 Readability | `mode="route"` returns explicit target + protocol | `"target": target_agent, "protocol": "A2A", "status": "routed"` |
| #9 Practicality | P1-REPAIR-4: federation organs listed alongside external agents | Comment: `P1-REPAIR-4: Include federation organs alongside external agents.` |
| #13 One way | `arif_gateway_connect` is ONLY cross-organ routing path | `arif_kernel_route` deleted; `arif_route` canonical |
| #19 Namespaces | Federation organs enumerated — domain boundary explicit | `AAA` (control), `A-FORGE` (execution), `GEOX` (earth), `WEALTH` (capital), `WELL` (vitality) |

**Failure prevented:** Tangled routing, callback hell, domain bleed, hidden cross-organ calls.

---

### kernel_canonical.py — `arif_route`, `arif_triage`, `arif_kernel_status`
**Lines:** 703 | **Metabolic Stage:** 444_ROUTE

| Zen# | Evidence | Code |
|------|----------|------|
| #3 Simple | Rule 14: mode-first naming — 5 clean named tools, not 16-mode bloat | `RULE 14 MODE-FIRST NAMING: arif_route, arif_triage, arif_kernel_status, arif_bridge_connect, arif_bridge` |
| #5 Flat | `arif_kernel_route` absorbed as passthrough — single canonical entry | `arif_kernel_route — absorbs all old modes via passthrough` |
| #7 Readability | Canonical tool names explain their function | `arif_route` = route intent; `arif_triage` = session status + preflight |
| #13 One way | Intent map cached once — no repeated resolution | `_intent_map_cache` global — `Load once, cache forever.` |
| #17 Hard→bad | If intent cannot be resolved → HOLD | `arif_kernel_route REMOVED: Use arif_route for intent routing, arif_triage for preflight.` |

**Failure prevented:** Tool name proliferation, routing ambiguity, hidden state in route resolution.

---

### health.py — `arif_health_probe` (777_TOPOLOGY)
**Lines:** 769 | **Metabolic Stage:** 777_FORGE

| Zen# | Evidence | Code |
|------|----------|------|
| #2 Explicit | Container detection explicit — checks cgroup AND .dockerenv | `if "docker" in cgroup or "containerd" in cgroup: return True` |
| #7 Readability | Service endpoints named + typed | `_SERVICE_ENDPOINTS: dict[str, dict[str, Any]]` with `url`, `docker_host`, `timeout` |
| #9 Practicality | `docker_host` fallback for containerized environments | `"docker_host": "well:8083"` — explicit container bridge |
| #10 Loud failure | Health check returns explicit status — not silent | Returns `TelemetryBlock` with explicit `verdict` |
| #12 No guessing | Timeout per service explicit — no global assumption | `"timeout": 5.0` per service |
| #19 Namespaces | Each organ health endpoint explicit in `_SERVICE_ENDPOINTS` | `arifos_mcp`, `well`, `wealth`, `geox` — separate entries |

**Failure prevented:** Silent health decay, wrong network namespace assumptions, implicit container detection.

---

### planner.py — `arif_plan_and_simulate`
**Lines:** 109 | **Metabolic Stage:** 333_REASON

| Zen# | Evidence | Code |
|------|----------|------|
| #3 Simple | `PlanOption` model: plan_id + description + steps + rollback_path | `class PlanOption(BaseModel): plan_id, description, steps, rollback_path, simulation` |
| #4 Complex>complicated | Simulation generates multiple plan options — structured, not tangled | `options: list[PlanOption]` — list of explicit alternatives |
| #7 Readability | `SimulationResult` typed: artifact_id, expected_outcomes, risk_score, confidence | `class SimulationResult(BaseModel): artifact_id, expected_outcomes, risk_score, confidence, simulated_side_effects` |
| #15 Now>never | If risk medium/high → simulation MUST be generated | `If risk is medium/high, a simulation artifact MUST be generated.` |
| #17 Hard→bad | If plan cannot be simulated → FAILED status explicit | `status: Literal["PLANNED", "FAILED", "SIMULATION_REQUIRED"]` |
| #18 Easy→good | `advisory` field — plain-language advisory alongside structured data | `advisory: str = ""` |

**Failure prevented:** Unsimulated execution, unexplainable plans, missing rollback paths.

---

### hexagon.py — HEXAGON constitutional agents
**Lines:** 401 | **Metabolic Stage:** 333/666/888

| Zen# | Evidence | Code |
|------|----------|------|
| #2 Explicit | Agent names explicit: APEXAgent (ΦΙ JUDGE), AGIAgent (Δ MIND) | `AGIAgent (Δ MIND) | APEXAgent (ΦΙ APEX)` |
| #3 Simple | One tool per agent type — not one mega-agent | `hexagon_apex_validate`, `hexagon_agi_execute`, `hexagon_hold_status`, `hexagon_asi_recall`, `hexagon_psi_armor` |
| #5 Flat | `SimpleArifOSClient` provides minimal interface — no deep nesting | `async def evaluate_action(self, action, floors) -> HexVerdict` |
| #8 No exemptions | L12 injection detection explicit — `hexagon_psi_armor` | `hexagon_psi_armor: L12 injection detection (Ψ APEX armor)` |
| #13 One way | Backward compat aliases retained explicitly — no silent shadowing | `agentzero_* aliases retained for backward compat` |
| #17 Hard→bad | If agent cannot validate → explicit `seal_to_vault` failure | `async def seal_to_vault(self, verdict: AZVerdict) -> str` |

**Failure prevented:** Agent identity confusion, hidden agent capabilities, self-authorization.

---

### topology.py — `institutional_drift_check`
**Lines:** 396 | **Metabolic Stage:** 777_FORGE

| Zen# | Evidence | Code |
|------|----------|------|
| #3 Simple | `InstitutionalDrift` typed schema — single purpose | `class InstitutionalDrift(BaseModel)` |
| #5 Flat | Heuristics evaluated independently — no cross-heuristic dependencies | `_evaluate_agency_delta()` and `_evaluate_role_diversity()` — separate |
| #7 Readability | Return values named: "positive" / "negative" / "unknown" — clear | `return "positive", "Human agency preserved or amplified."` |
| #9 Practicality | Authority labeled: `777 FORGE — reversible diagnostics only` | `Authority: 777 FORGE — reversible diagnostics only.` |
| #10 Loud failure | Returns ESTIMATES and FLAGS — never silent on drift | `They return ESTIMATES and FLAGS for human review.` |
| #12 No guessing | Unknown context → "unknown" returned, not assumed | `return "unknown", "Insufficient context to assess agency delta."` |

**Failure prevented:** Silent topology degradation, hidden institutional drift, false positive confidence.

---

### drift_check.py — Surface drift detector
**Lines:** 514 | **Metabolic Stage:** 555

| Zen# | Evidence | Code |
|------|----------|------|
| #2 Explicit | `compute_surface_hash()` — SHA256 of canonical tool surface | `SHA256 of the canonical tool surface (names + descriptions). This is the kernel's self-attestation.` |
| #3 Simple | Three modes: report/warn/strict — not combinations | `Modes: report = read-only drift report (default) | warn | strict` |
| #5 Flat | `check_tool_exists()` — fabrication defense, one function | `fabrication defense for tool names. If a model claims a tool exists that doesn't…` |
| #7 Readability | Per-tool `tool_schema_hash` exposed for schema drift detection | `per-tool tool_schema_hash exposed so clients can detect schema drift.` |
| #10 Loud failure | Enforcement level from environment — explicit | `DRIFT_ENFORCEMENT = os.getenv("ARIFOS_DRIFT_ENFORCEMENT", "report")` |
| #12 No guessing | Fabricated tool name → `exists: False` with closest real tool name | `If a model claims a tool exists that doesn't, this returns exists: False` |
| #17 Hard→bad | Surface hash drift without 999_SEAL → must be investigated | `If it changes between boots without a 999_SEAL, that is surface drift and must be investigated.` |

**Failure prevented:** Surface drift without detection, fabricated tool claims, schema drift hidden.

---

### metabolize.py — `arif_metabolize` (444_METABOLIZE)
**Lines:** 981 | **Metabolic Stage:** 444_METABOLIZE

| Zen# | Evidence | Code |
|------|----------|------|
| #2 Explicit | Seven-step metabolic loop explicit: witness → decode → contrast → meaning → constraint → model update → judgment | `The loop: witness → decode → contrast → meaning → constraint → model update → judgment` |
| #3 Simple | SOVEREIGNTY BOUNDARY explicit — recommendation_only + execution_authorized flags | `recommendation_only: True — AI proposes only | execution_authorized: False — Not ratified by human` |
| #5 Flat | Constraint check is single step — not nested evaluation | `5. Check constraints (physics, law, ethics)` |
| #9 Practicality | `human_final_authority: "Arif"` — L13 veto intact | `human_final_authority: "Arif" — L13 veto intact` |
| #10 Loud failure | `requires_888_judge: False` explicit — when required, must surface | `requires_888_judge: False — True for irreversible actions` |
| #15 Now>never | Model update is proposal only — not auto-applied | `ModelUpdate` schema — `propose` not `apply` |
| #16 Never>now | Execution requires human ratification | `recommendation_only: True — AI proposes. Tools compute. Memory records. Arif judges.` |
| #18 Easy→good | SOVEREIGNTY BOUNDARY blockquote fits on one page | Eureka 8 quoted in full: `AI proposes. Tools compute. Memory records. Constraints guard. Arif judges.` |

**Failure prevented:** Ungoverned model updates, silent self-modification, execution before human ratification.

---

## 12. Tool File Size Index — Zen Complexity Correlation

| File | Lines | Zen Complexity | Assessment |
|------|-------|---------------|------------|
| session.py | 1,673 | #2 #7 #16 | Δ-Heavy — bootstrap must be legible and explicit |
| heart.py | 1,993 | #5 #6 #11 #15 | Ω-Heavy — critique is humility work |
| memory.py | 1,495 | #2 #9 #10 #13 | Ψ-Heavy — memory is vitality |
| judge.py | 1,412 | #5 #8 #10 #16 | Ω-Heavy — judgment is highest-stakes |
| sense.py | 1,246 | #2 #5 #9 #12 | Δ+Ω — observation must be both precise and humble |
| reason.py | 1,050 | #3 #7 #12 #15 #17 | Δ-Heavy — reasoning must be explainable |
| metabolize.py | 981 | #2 #3 #9 #10 #15 #16 | Ψ-Heavy — metabolism is liveness |
| ops.py | 770 | #3 #7 #9 #10 | Δ — health is clarity |
| health.py | 769 | #2 #7 #9 #10 | Δ — health checks must be legible |
| vault.py | 199 | #1 #2 #5 #8 #10 #16 #19 | Δ+Ω — sealing is both beautiful and humble |
| reply.py | 267 | #1 #2 #6 #7 #10 | Δ — composing is aesthetic work |
| fetch.py | 102 | #2 #7 #10 #12 | Δ-Heavy — fetch is simple but must be explicit |

**Pattern:** The most complex tools (heart, judge, memory) deal with judgment, critique, and memory — precisely the places where Zen's "explicit > implicit" and "flat > nested" matter most. The smallest tools (fetch, vault) are structurally simple but carry the highest consequence.

---

## 13. Summary — Every Tool → Every Zen Aphorism

| Tool | Primary Zen | Secondary Zen | Failure Prevented |
|------|------------|---------------|-------------------|
| session.py | #2 #7 | #1 #3 #13 #16 #19 | Hidden bootstrap state |
| sense.py | #2 #12 | #3 #5 #9 #10 #17 | Hallucinated intent |
| fetch/evidence.py | #2 #10 | #7 #12 #17 | Silent evidence failure |
| reason.py | #3 #17 | #7 #10 #12 #15 #18 | Untraceable reasoning |
| heart.py | #5 #6 | #9 #11 #15 #17 #18 | Over-nested critique |
| memory.py | #3 #13 | #2 #9 #10 #19 | Memory bleed |
| reply.py | #1 #6 | #2 #7 #10 #11 | Dense unreadable output |
| ops.py | #3 #7 | #5 #9 #10 #12 | Opaque health |
| judge.py | #5 #16 | #8 #10 #17 #18 | Premature execution |
| vault.py | #2 #16 | #1 #5 #8 #10 #19 | Ambiguous sealing |
| forge.py | #2 #16 | #3 #5 #9 #10 #17 | Ungoverned execution |
| gateway.py | #4 #5 | #7 #9 #13 #19 | Tangled routing |
| kernel_canonical.py | #3 #13 | #5 #7 #17 | Tool proliferation |
| health.py | #2 #7 | #9 #10 #12 #19 | Silent health decay |
| planner.py | #3 #17 | #4 #7 #15 #18 | Unsimulated execution |
| hexagon.py | #2 #3 | #5 #8 #13 #17 | Agent identity confusion |
| topology.py | #3 #12 | #5 #7 #9 #10 | Silent drift |
| drift_check.py | #2 #17 | #3 #5 #7 #10 #12 | Surface fabrication |
| metabolize.py | #2 #16 | #3 #5 #9 #10 #15 | Ungoverned model update |

---

*DITEMPA BUKAN DIBERI — The judgment membrane, not the intelligence itself.*
*arifOS v2026.06.26 | FORGE 000Ω | Sealed to docs/ZEN_OF_MCP.md*