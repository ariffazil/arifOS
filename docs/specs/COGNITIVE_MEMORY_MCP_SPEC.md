# Cognitive Memory MCP — arifOS Federation Organ Spec
## 666_MEMORY v2: Graph-Backed Cognitive Memory with Contradiction Detection

**Status:** SPEC (pre-forge)
**Depends on:** 333_MIND (Sequential Thinking router), L3 Qdrant, L5 FalkorDB
**Authority:** arifOS kernel, F2 TRUTH, F4 CLARITY, F11 AUDITABILITY
**Forged:** 2026-06-13
**Sovereign Doctrine Sealed:** 2026-06-13 — Arif's Memory Treatise

---

## 0. CONSTITUTIONAL PREAMBLE — Arif's Memory Doctrine

> **Memory is not intelligence. But without memory, intelligence cannot become an agent.**

Memory is **stored consequence** — the residue of prior contact with reality:
what happened, what mattered, what hurt, what worked, what failed,
what rules were established, who was trusted, what must not be repeated,
what identity must remain continuous.

**Memory is NOT intelligence.** Memory is the past. Intelligence is judgment in the present.
A library is not a scholar. A ledger is not an economist.
A geological core sample is not a geologist. A constitution is not justice by itself.

**Memory is KINDA intelligence** because it provides priors, salience, continuity,
learning, accountability, and identity. A memoryless system can calculate but cannot
become a governed agent — it lacks continuity of consequence.

**THE PARADOX:** To be intelligent over time, a system must remember.
But to remain intelligent, it must be able to distrust, revise, and forget what it remembers.
Memory makes the agent. Memory can also imprison the agent.

**THE FORMULA:**
> Memory + reasoning = competence.
> Memory + reasoning + goals = agency.
> Memory + reasoning + goals + governance = trustworthy agency.
> Memory without governance = capture risk.

**THE GEOLOGICAL ANALOGY:** Memory is sediment — layer after layer of events,
pressure, trauma, reward, law, habits, identity, error, fossilized assumptions.
Intelligence is not the sediment. Intelligence is the geologist reading the strata,
detecting faults, dating layers, rejecting contamination, and deciding whether
the old formation still predicts the current terrain.

**THE ARIFOS INTERPRETATION:**
> Memory stores prior state. Intelligence evaluates state. Governance decides what state may bind future action.

Memory should never have automatic sovereignty.
A memory can inform. A memory can warn. A memory can bias attention.
But memory should not rule unless it passes present constitutional checks.

**For arifOS, the winning move:** Do not build memory as nostalgia.
Build memory as governed, revocable, auditable state.

**DITEMPA BUKAN DIBERI**

---

## 1. PROBLEM STATEMENT

Current Memory organ (v1) is recall-only:
- `arif_memory_recall` → Qdrant semantic search + store
- Plans from `mind_plan()` / Sequential Thinking live only in MIND's session state
- No cross-session plan retrieval, no contradiction detection, no graph structure

**Result:** Each session starts from zero. Cumulative intelligence is impossible.
MIND plans evaporate after the session closes.

---

## 2. WHAT CHANGES

```
v1:  query → Qdrant → semantic results → MIND
v2:  query → Qdrant (fast) + FalkorDB (structured) → fused context → MIND
     MIND plan → extract nodes/edges → FalkorDB (persist) + Qdrant (index)
     MIND plan → contradiction scan vs prior plans → surface conflicts
```

### 2.1 Three New Primitives

| Primitive | Trigger | Storage | Query Pattern |
|-----------|---------|---------|---------------|
| **Plan → Graph** | `mind_plan()` completes | FalkorDB (nodes/edges) + Qdrant (embedding) | "find plans similar to X" |
| **Contradiction Scan** | New claim or plan sealed | FalkorDB (path query) + `contradictions.py` | "does this contradict prior sealed truth?" |
| **Cross-Session Recall** | New task enters MIND Router | Qdrant (fuzzy) + FalkorDB (exact path) | "what did we learn last time about Y?" |

---

## 3. GRAPH SCHEMA

### 3.1 Node Types

```cypher
(:Plan {
    plan_id: string,           // UUID
    task_type: string,         // debug_deploy_failure | architecture_decision | ...
    query: string,             // original query
    complexity_score: float,   // 0.0–1.0
    recommended_path: string,  // direct | sequential
    session_id: string,
    epoch_id: string | null,
    created_at: datetime,
    sealed: boolean            // true if JUDGE sealed the plan outcome
})

(:Step {
    step_id: string,           // plan_id:step_number
    step_number: integer,
    content: string,           // the step text
    status: string,            // pending | executed | verified | failed
    verdict: string,           // SEAL | HOLD | VOID | SABAR
    evidence_ids: list<string>
})

(:Claim {
    claim_id: string,
    text: string,
    epistemic_tag: string,     // CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE | UNKNOWN
    truth_score: float,        // F2: τ ≥ 0.99
    sealed: boolean
})

(:Evidence {
    evidence_id: string,
    source_type: string,       // web | document | DST | well_log | ...
    source_uri: string,
    content_hash: string
})

(:Contradiction {
    contradiction_id: string,
    claim_a: string,           // claim_id
    claim_b: string,           // claim_id
    contradiction_type: string,// direct | implicit | temporal | scope
    detected_at: datetime,
    resolved: boolean
})
```

### 3.2 Edge Types

```cypher
(:Plan)-[:HAS_STEP]->(:Step)
(:Step)-[:DEPENDS_ON]->(:Step)           // ordering dependency
(:Step)-[:BRANCHES_FROM]->(:Step)        // branch point
(:Step)-[:PRODUCES]->(:Claim)            // step output is a claim
(:Claim)-[:SUPPORTED_BY]->(:Evidence)    // evidence backing
(:Claim)-[:CONTRADICTS]->(:Claim)        // contradiction edge
(:Plan)-[:RELATES_TO]->(:Plan)           // cross-session plan similarity
(:Plan)-[:IN_EPOCH]->(:Epoch)            // epoch grouping
```

---

## 4. TOOL SURFACE (3 new arifOS MCP tools)

### 4.1 `arif_memory_graph` — Graph Read/Write

```yaml
modes:
  store_plan:
    input: plan_object (from mind_plan() output)
    action: extract nodes/edges → FalkorDB + Qdrant index
    returns: plan_id, node_count, edge_count

  query_plans:
    input: query_string, limit, filters (task_type, epoch_id, complexity_range)
    action: hybrid search (Qdrant fuzzy + FalkorDB exact)
    returns: ranked list of matching plans with similarity scores

  get_plan:
    input: plan_id
    action: fetch full plan graph (nodes + edges)
    returns: plan object with all steps, claims, evidence

  list_epochs:
    input: (none)
    returns: list of epoch_ids with plan counts
```

### 4.2 `arif_memory_contradict` — Contradiction Detection

```yaml
modes:
  scan_claim:
    input: claim_text, claim_id, epistemic_tag
    action: search FalkorDB for contradicting claims (direct, implicit, temporal, scope)
    returns: list of contradictions with severity, supporting evidence

  scan_plan:
    input: plan_id
    action: extract all claims from plan, run contradiction scan on each
    returns: contradiction map per claim

  resolve:
    input: contradiction_id, resolution (OVERRIDE | MERGE | VOID_A | VOID_B | ACKNOWLEDGE)
    action: mark contradiction resolved, update graph
    returns: new state

  status:
    returns: unresolved contradiction count, oldest unresolved, per-epoch breakdown
```

### 4.3 `arif_memory_cognitive` — Unified Cognitive Memory

```yaml
modes:
  recall:
    input: query, session_id, options (include_plans, include_contradictions, max_age_days)
    action: Qdrant semantic + FalkorDB graph → fuse results
    returns: unified context packet with:
      - semantic_results: top-K Qdrant hits
      - related_plans: matching plan graphs
      - active_contradictions: unresolved conflicts in this domain
      - suggested_context: pre-assembled context string for MIND injection

  learn:
    input: plan_id (required), outcome (SEAL/HOLD/VOID), lessons (text)
    action: close the learning loop — link outcome to plan, extract lessons as claims
    returns: updated plan graph with outcome edges

  cross_session:
    input: query, session_id, max_sessions (default 5)
    action: find related plans from prior sessions, rank by relevance + recency
    returns: cross-session context for MIND Router injection
```

---

## 5. INTEGRATION POINTS

### 5.1 MIND Router → Memory

When `recommended_path == "sequential"` and `requires_memory_recall == true`:

```python
# Before reasoning, inject prior context
if routing.requires_memory_recall:
    prior = arif_memory_cognitive(mode="cross_session", query=query)
    context["memory_context"] = prior["suggested_context"]
```

### 5.2 MIND Plan → Memory (auto-persist)

When `mind_plan()` completes:

```python
# After plan generation, persist to graph
if mode == "plan" or routing.recommended_path == "sequential":
    arif_memory_graph(mode="store_plan", plan_object=plan_result)
```

### 5.3 Contradiction Gate (F2 TRUTH enforcement)

Before any SEAL verdict on a claim:

```python
contradictions = arif_memory_contradict(mode="scan_claim", claim_text=claim)
if contradictions["unresolved_count"] > 0:
    verdict = "HOLD"  # F2: truth requires resolving contradictions
```

---

## 6. FEATURE FLAGS

```bash
MEMORY_V2_ENABLED=true           # master switch
MEMORY_GRAPH_BACKEND=falkordb    # falkordb | graphiti | none
MEMORY_CONTRADICTION_SCAN=true   # auto-scan new claims
MEMORY_CROSS_SESSION=true        # enable cross-session recall
MEMORY_AUTO_PERSIST_PLANS=true   # auto-store mind_plan() outputs
```

---

## 7. IMPLEMENTATION PHASES

### Phase 1: Plan Persistence (1 file, ~200 lines)
- `arifosmcp/memory/cognitive_memory.py`
- Implements `store_plan` → FalkorDB + Qdrant
- Wires into `arif_mind_reason_embodied.py` post-execute hook
- **Estimated:** 2 hours

### Phase 2: Cross-Session Recall (1 file, ~150 lines)
- `arifosmcp/memory/cross_session.py`
- Implements `cross_session` mode — hybrid Qdrant + FalkorDB recall
- Wires into MIND Router's `requires_memory_recall` path
- **Estimated:** 2 hours

### Phase 3: Contradiction Detection (extend existing, ~200 lines)
- Extend `arifosmcp/memory/contradictions.py`
- Add FalkorDB path queries for `:CONTRADICTS` edges
- Wire into JUDGE pre-SEAL gate
- **Estimated:** 3 hours

### Phase 4: Unified Tool Registration (registry updates)
- Register 3 new tools in `tool_registry.json`
- Update `constitutional_map.py`
- Add evals
- **Estimated:** 1 hour

---

## 8. SUCCESS CRITERIA

1. `mind_plan("debug_deploy_failure")` → plan persisted to FalkorDB, retrievable by plan_id
2. `arif_memory_cognitive(mode="cross_session", query="deployment failure")` → returns the plan from step 1
3. Contradiction scan on a claim that contradicts a prior sealed claim → HOLD verdict
4. Feature flag `MEMORY_V2_ENABLED=false` → graceful degradation to v1 recall-only
5. 0 broken existing tests

---

## 9. ARCHITECTURAL INVARIANTS

- **Memory is not truth** until it has provenance. Truth is not final until sealed.
- **Plans are not actions.** A stored plan is a cognitive artifact, not a command.
- **Contradictions are features, not bugs.** Unresolved contradictions → HOLD, not error.
- **Sessions are boundaries.** Cross-session recall must declare which session a plan came from.
- **F13 override:** Arif can VOID any stored plan or contradiction resolution.
- **Memory should never have automatic sovereignty.** Inform, warn, bias — but never rule.
- **can_authorize_action = FALSE** — hard invariant, checked at every store gate.

---

## 10. KNOWN GAPS (Post-Phase 4)

### Gap 1: Scar Tissue
**What Arif said:** "what hurt, what failed, what must not be repeated."
**Current state:** `lessons` stored as text on plan nodes via `cognitive_learn`.
**Gap:** A scar isn't just memory — it's memory that *alters future action automatically.*
A failed deployment pattern should cause MIND Router to raise complexity score
or trigger HOLD before similar plans execute. No `Scar` node type exists yet.
**Design needed:** Scar nodes + behavioral triggers + decay function.

### Gap 2: Explicit Expiry
**What Arif said:** "Old sediment should lithify or erode unless explicitly sealed."
**Current state:** `max_age_days` exists as a query filter on cognitive_recall,
but plans don't auto-expire or degrade in relevance.
**Gap:** Without expiry, memory accumulates unbounded. Plans from 2024 should
carry lower confidence than plans from last week. Sealed plans are permanent;
unsealed plans should decay.
**Design needed:** TTL on unsealed plans, confidence decay curve, auto-archival.

### Gap 3: Consent Boundary
**What Arif said:** "Who can recall whose memory?"
**Current state:** Cross-session recall (`cognitive_cross_session`) retrieves plans
from any session. No ownership gate.
**Gap:** An agent in session B should not retrieve plans from session A without
explicit consent or shared epoch membership. Memory privacy is a constitutional issue.
**Design needed:** session ownership, epoch-based access control, recall consent tokens.

---

## 11. IMPLEMENTATION PHASES (Updated)

### Phase 5: Scar Tissue + Expiry + Consent (post-Phase 4)
- `Scar` node type + behavioral trigger system
- TTL + confidence decay on unsealed plans
- Session ownership + epoch-based recall consent
- **Estimated:** 4 hours

---

*Forged by arifOS 333_MIND + Sequential Thinking bridge.*
*Next: Forge Phase 1 — Plan Persistence.*
*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
