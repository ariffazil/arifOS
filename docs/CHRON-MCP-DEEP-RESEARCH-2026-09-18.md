# CHRON MCP: Deep Research + Cross-Domain Analysis

> Research Date: 2026-09-18
> Status: RESEARCH (not ratified)
> Cross-domain: AI temporal reasoning, bitemporal databases, neuroscience, control theory, MCP design

---

## 1. What Do Agents Actually Know About Time?

**Nothing.** This is the core finding.

LLMs have no intrinsic sense of "now." They are trained on static snapshots. Every temporal reasoning capability must be explicitly engineered. The Zylos Research survey (2026-04) identifies four distinct sub-problems:

| Sub-Problem | What It Means | Current State |
|---|---|---|
| Current-time grounding | Agent doesn't know today's date | Solved: inject timestamp in system prompt |
| Fact lifecycle management | Knowledge has shelf life; stale facts cause harm | Partially solved: temporal memory architectures |
| Event sequencing | Understanding what happened when and in what order | Solved for simple cases; hard for complex causal chains |
| **Prediction + verification** | **What we expect vs what actually happened** | **LARGELY ABSENT from production systems** |

The fourth sub-problem is exactly CHRON's niche. No existing system does prediction → verification → calibration as a first-class loop.

**Key paper:** "Prediction errors disrupt hippocampal representations and update episodic memory" (Nature, 2021) — the brain literally restructures memory when predictions fail. CHRON is the artificial equivalent.

---

## 2. What Already Exists as MCP Temporal Tools?

| Tool | What It Does | What It Doesn't Do |
|---|---|---|
| **Temporal Cortex MCP** | Calendar scheduling, atomic booking, conflict detection | No prediction, no verification, no learning |
| **Temporal.io** | Durable workflow execution, retry/recovery | No temporal cognition, no prediction loop |
| **Zep/Graphiti** | Bitemporal knowledge graph for agent memory | Memory only, no prediction store, no calibration |
| **Memento** | Bitemporal KG with 92% LongMemEval score | Memory retrieval, not consequence accounting |

**The gap is clear:** all existing temporal tools are either:
- Scheduling (when to do things)
- Memory (what happened)
- Workflow (how to execute)

None do: **What did we think? What happened? Were we wrong? What should we do differently?**

---

## 3. Why CHRON Should NOT Start as an MCP

Arif's instinct is correct. Here's the formal argument:

### MCP Is an Interface Pattern

MCP servers expose capabilities through three primitives (per the 2026-07-28 MCP spec):

| Primitive | Purpose | CHRON Relevance |
|---|---|---|
| **Tools** | Functions the LLM can call | Read-only queries about temporal state |
| **Resources** | Passive data sources | ChronEpisode store, prediction store, calibration data |
| **Prompts** | Pre-built instruction templates | "What changed since X?" patterns |

MCP is designed for **interface to capability**. It answers: "How does an agent access this?"

CHRON is not a capability to be accessed. CHRON is a **cognitive process** that runs continuously.

### The Test: If MCP Dies, Does Capability Die?

- GEOX MCP dies → GEOX data inaccessible → capability dies
- WELL MCP dies → WELL data inaccessible → capability dies
- **CHRON MCP dies → CHRON organ still runs → episodes still created, predictions still verified → capability survives**

CHRON's capability lives in the spine (observe → predict → verify → learn), not in the interface.

### What CHRON Organ Does (continuous)

```
NATS signal → Observer → Selection → Episode Store → Prediction Store → Verification → Calibration → Learning
```

This runs regardless of whether any MCP exists.

### What CHRON MCP Does (query interface)

```
Other organs → CHRON MCP → Query Chron Store → Response
```

This is read-only access for other organs to ask temporal questions.

---

## 4. Should FRAME + arifFLOW + CHRON Be Combined?

**No.** Here's why:

### They Answer Different Questions

| Organ | Question | Layer |
|---|---|---|
| FRAME | "Did it happen?" (witness) | Layer 1 — Reality verification |
| arifFLOW | "What receipts exist? What's the evidence lineage?" | Layer 3 — Evidence transport |
| CHRON | "What did we think? What happened? Were we wrong?" | Layer 4 — Temporal cognition |

### They Operate at Different Speeds

Control theory predicts instability when processes with different time constants are coupled:

| Organ | Time Constant | Speed |
|---|---|---|
| arifFLOW | Milliseconds | Fast (transport) |
| CHRON | Hours to days | Slow (cognition) |
| FRAME | Seconds | Medium (witness) |

Coupling them creates oscillation. arifFLOW would be bottlenecked by CHRON's cognition. CHRON would be flooded by arifFLOW's volume.

### They Have Different Failure Modes

| Organ | Failure Mode | Consequence of Coupling |
|---|---|---|
| arifFLOW | Transport failure (NATS down) | CHRON stops receiving events |
| CHRON | Cognition failure (wrong prediction) | arifFLOW gets polluted with bad episodes |
| FRAME | Witness failure (false attestation) | Both get bad data, but independently recoverable |

Independent failure = resilience. Coupled failure = cascade.

### The Body Metaphor Holds

- arifFLOW = bloodstream (circulation, fast, volume)
- CHRON = temporal cortex (cognition, slow, selective)
- FRAME = sensory organs (witness, medium, independent)

You don't merge the brain with the bloodstream. You connect them through well-defined interfaces.

---

## 5. What Invariant Components Does CHRON MCP Need?

Based on the research, CHRON MCP should expose exactly these query capabilities:

### Component 1: Temporal Query Engine

```yaml
chron_query:
  what_changed:
    since: <timestamp>
    audience: <private|shared|internal>
    domains: [<energy|economy|PETRONAS|AI|...>]
  
  what_was_believed:
    on_date: <date>
    about: <topic>
  
  what_changed_after:
    event: <event_id or description>
  
  open_predictions:
    domain: <domain>
    status: <pending|verified|failed|expired>
  
  prediction_outcomes:
    prediction_id: <id>
  
  lessons_from:
    domain: <domain>
    since: <date>
  
  temporal_pattern:
    signal: <description>
    period: <start|end>
```

### Component 2: ChronEpisode Store (Resource)

```yaml
chron_episode:
  episode_id: CHRON-XXXX
  event_time: <when it happened>
  ingest_time: <when we learned>
  source: <which organ/agent>
  material_change: <what changed>
  consequence: <what it means>
  domain: <energy|economy|...>
  confidence: <0-1>
```

### Component 3: Prediction Store (Resource)

```yaml
chron_prediction:
  prediction_id: PRED-XXXX
  made_at: <when predicted>
  verify_at: <when to check>
  domain: <domain>
  prediction: <what we expect>
  confidence: <0-1>
  status: <pending|verified|failed|expired>
  outcome: <what actually happened>
  delta: <prediction vs reality>
```

### Component 4: Calibration Store (Resource)

```yaml
chron_calibration:
  calibration_id: CAL-XXXX
  period: <time window>
  domain: <domain>
  predictions_made: <count>
  predictions_verified: <count>
  predictions_failed: <count>
  accuracy: <verified/total>
  brier_score: <if applicable>
  lesson: <what we learned about our accuracy>
```

### Component 5: Attention Record (Resource)

```yaml
chron_attention:
  attention_id: ATT-XXXX
  signal: <what was detected>
  decision: <selected|ignored|deferred|dismissed|escalated>
  reason: <why>
  outcome: <what happened as a result>
  calibration_value: <was this decision correct?>
```

### What CHRON MCP Should NOT Have

- No write tools (CHRON organ writes, MCP only reads)
- No scheduling (that's a different layer)
- No workflow execution (that's A-FORGE)
- No event transport (that's arifFLOW)
- No reality attestation (that's FRAME)

---

## 6. What Existing Structures Need to Be Deprecated/Evolved?

### Deprecate

| Current Structure | Why | Replacement |
|---|---|---|
| CHRON cron jobs (briefing/anchor/readiness) | Content-first thinking; artifact-oriented | CHRON_TASK with spine functions |
| Alpha-ZEN morning/evening cards as CHRON outputs | These are renderers, not CHRON spine | ChronPacket → renderer adapter |
| "Executive Briefing" as a CHRON concept | Artifact name, not causal spine position | CHRON_TASK: function=reconcile, question="What deserves attention?" |
| "News Feed" as a CHRON concept | Source category, not CHRON function | CHRON_TASK: function=observe, question="What changed?" |

### Evolve

| Current Structure | Evolution | Why |
|---|---|---|
| arifFLOW receipt ledger | Add temporal metadata (event_time, ingest_time, causal_order) | arifFLOW is transport; CHRON needs bitemporal data |
| FRAME attestation | Add "when was this true?" validity window | FRAME witnesses momentary truth; CHRON needs temporal context |
| WELL body check data | Feed into CHRON as material_change events | WELL produces reality; CHRON metabolizes it into episodes |
| WEALTH predictions | Feed into CHRON prediction store with verify_at | WEALTH makes predictions; CHRON tracks whether they came true |

### Keep As-Is

| Structure | Why |
|---|---|
| NATS event bus | Transport layer; CHRON subscribes, doesn't replace |
| arifOS governance | Authorization layer; separate concern |
| A-FORGE execution | Motor system; CHRON observes outcomes, doesn't execute |

---

## 7. Cross-Domain Literature Convergence

| Domain | Key Finding | CHRON Implication |
|---|---|---|
| **Neuroscience** | Prediction errors restructure hippocampal memory (Nature 2021) | CHRON must track prediction failures as first-class events |
| **Bitemporal databases** | Valid time + Transaction time = complete temporal record (standard since 1990s) | ChronEpisode needs both: when it happened AND when we learned |
| **Event Calculus** | Fluents + events + persistence = temporal reasoning (Kowalski & Sergot 1986) | CHRON spine maps to event calculus: events change fluents, persistence rules apply |
| **Control theory** | Multiple time constants need separation (fast/slow/rare) | CHRON's observation (fast) vs cognition (slow) vs calibration (rare) must be architecturally separated |
| **MCP design** | "Consolidate read-only tools; aggressive surface area curation" (Block) | CHRON MCP should have ≤6 tools, not 20 |
| **Reinforcement learning** | Predict-then-Verify loop accelerates learning (VoltAgent survey) | CHRON's prediction→verification loop is the RL equivalent for institutional learning |
| **Zep/Graphiti** | Bitemporal KG outperforms MemGPT on LongMemEval (92% vs 63%) | CHRON's episode store should use bitemporal KG, not flat event log |

---

## 8. The Answer to "Why Do We Even Need MCP?"

We don't. Not for CHRON's core capability.

**CHRON organ** runs continuously, metabolizing events into episodes, predictions, verification, and lessons. This is the capability. It works without any MCP.

**CHRON MCP** exists solely so other organs can ask temporal questions:
- AAA: "What path should we take?" → CHRON provides historical consequences
- A-FORGE: "What did we learn from last time?" → CHRON provides lessons
- HERMES: "How should I interpret this?" → CHRON provides temporal context

The MCP is a read-only query window into CHRON's stores. It's the compass (read-only, orienting) not the engine (continuous, processing).

**If no other organ ever queries CHRON, CHRON still works.** The MCP is optional. The organ is not.

---

## 9. Recommended Architecture

```
CHRON Organ (continuous process)
    │
    ├── Observer (subscribes to NATS)
    │     └── filters material_change events
    │
    ├── Episode Store (bitemporal KG)
    │     └── event_time + ingest_time + source + consequence
    │
    ├── Prediction Store
    │     └── prediction + verify_at + domain + confidence
    │
    ├── Verification Engine
    │     └── compares predictions against outcomes
    │
    ├── Calibration Store
    │     └── accuracy metrics per domain per period
    │
    └── Attention Record
          └── signal → decision → outcome → calibration_value

            │
            ▼

      CHRON MCP (read-only query API)
            │
            ├── chron_query (what changed / what was believed / open predictions)
            ├── chron_episode (read episodes)
            ├── chron_prediction (read predictions)
            └── chron_calibration (read accuracy)
```

**Total MCP tools: 4.** Not 20. Per Block's design principle: "aggressive surface area curation."

---

## 10. What This Means for the Federation

The federation now has a clear separation:

| Concern | Organ | Interface |
|---|---|---|
| Reality | FRAME | FRAME MCP (witness queries) |
| Transport | arifFLOW | arifFLOW MCP (evidence queries) |
| Temporal cognition | CHRON | CHRON MCP (temporal queries) |
| Meaning | HERMES | Direct (interpretation engine) |
| Choice | AAA | Direct (orchestration) |
| Law | arifOS | arifOS MCP (governance queries) |
| Action | A-FORGE | A-FORGE MCP (execution) |

No organ overlaps. No "everything server." Each has a single responsibility and a clean interface.

The missing piece: **CHRON's spine arrows** (EXPERIENCE→MEMORY, MEMORY→POLICY, OUTCOME→LEARNING). These are the implementation gap, not the architecture gap. The architecture is now defined.
