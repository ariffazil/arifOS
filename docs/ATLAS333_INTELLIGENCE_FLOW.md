# ATLAS333 Intelligence Flow — Canonical Map

> **Purpose:** Reconcile the cognitive pipeline (ATLAS333 — HOW the agent thinks) with the system pipeline (MCP/A2A/A-FORGE — WHAT the agent does) into one auditable flow.
> **Authority:** F13 SOVEREIGN — sealed 2026-07-15
> **Status:** EVERGREEN — update as the earth updates its map: continuously, never finished.
> **DITEMPA BUKAN DIBERI**

---

## §0 — TWO PIPELINES, ONE SYSTEM

```
COGNITIVE PIPELINE (ATLAS333)          SYSTEM PIPELINE (MCP/A2A/A-FORGE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━          ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW the agent thinks                   WHAT the agent does
Paradox geometry, tension navigation   Tool calls, authority, execution
33 paradoxes, 7 zones, 3 organs       000→999 stages, 13 floors, 7 organs

         ┌──────────────────────────────────────────┐
         │           THEY CONVERGE AT:              │
         │                                          │
         │   GPV (Governance Placement Vector)      │
         │   = the coordinate where cognitive       │
         │     geometry meets system routing        │
         └──────────────────────────────────────────┘
```

---

## §1 — THE 10 STAGES (System Pipeline)

Each stage is a **state of cognition + system activation**, not a step.

| Stage | Name | MCP Tool | Handler File | What Happens |
|-------|------|----------|-------------|--------------|
| **000** | INIT | `arif_init` | `tools/session.py` | Identity bind (Ed25519), session creation, F1-F13 acceptance, carry_forward load |
| **111** | ORIENT | `arif_observe` | `tools/sense.py` | Reality sensing, epistemic labels (OBS/DER/INT/SPEC/UNKNOWN), organ evidence |
| **222** | MAP | *(internal)* | `core/shared/atlas.py` | ATLAS333 activation: Φ(text)→GPV, paradox zone resolution, geometry classification |
| **333** | REASON | `arif_think` | `tools/reason.py` | Hypotheses N≥3, scenarios, EVOI. Proposes only — judge decides |
| **444** | ROUTE | `arif_route` | `tools/kernel_canonical.py` | Intent routing to metabolic lane, organ selection, MCP/A2A/P2P decision |
| **555** | CRITIQUE | `arif_critique` | `tools/heart.py` | Ethical risk simulation, dignity/maruah check, consequence scan |
| **666** | JUDGE | `arif_judge` | `tools/judge.py` | Constitutional verdict: SEAL/HOLD/SABAR/VOID. F1-F13 floor evaluation |
| **777** | FORGE | `arif_forge` | `tools/forge.py` | Delegated execution bridge to A-FORGE. Only after SEAL |
| **888** | VERIFY | `arif_verify` | `tools/vault.py` | Reality check: did it work? Truth verification, scar detection |
| **999** | SEAL | `arif_seal` | `tools/vault.py` | VAULT999 immutable receipt, memory update, carry_forward seal |

---

## §2 — COGNITIVE PIPELINE (ATLAS333 — How the Agent Thinks)

### The Flow

```
Text (user query)
    │
    ▼
Φ(text) ─── atlas.py ───────────────────────────────────────┐
    │                                                        │
    ▼                                                        │
GPV(lane, τ, κ, ρ, paradox_axes, query_type)                │
    │                                                        │
    ├──→ PARADOX_GPV_MAP ──→ paradox IDs (1-33)              │
    │                                                        │
    ▼                                                        │
PARADOX_QUOTE_MAP ──→ 33 philosophical quotes                │
    │    (paradox_quotes.py)                                 │
    │    3 organs: Memory (M1-M11), Mind (R1-R11), Judge (J1-J11)
    │                                                        │
    ▼                                                        │
get_triggered_quotes_by_gpv(gpv, action_class)               │
    │    Returns quotes for activated paradox zones          │
    │    Action-class gated: OBSERVE vs MUTATE fire different │
    │                                                        │
    ▼                                                        │
evaluate_paradox_gate_gpv(gpv)                               │
    │    Resolution risk flags (NOT blocks — F5 PEACE)       │
    │                                                        │
    ▼                                                        │
FloorScores.trm / .echo / .rasa                              │
    │    TEARFRAME thresholds:                               │
    │    trm  = f2_truth          (≥0.94 for factual)       │
    │    echo = ∛(f3 × f2 × f13) (≥0.87)                   │
    │    rasa = ∛(f6 × f5 × f13) (≥0.85)                   │
    │                                                        │
    ▼                                                        │
arif_judge (666) ←───────────────────────────────────────────┘
    │    Receives: GPV + paradox flags + TEARFRAME scores
    │    Verdict: SEAL | HOLD | SABAR | VOID
    ▼
arif_forge (777) → arif_seal (999)
```

### The 7 Paradox Zones (Constitution)

| Zone | Name | Paradox IDs | When It Fires | Primary Floors |
|------|------|-------------|---------------|----------------|
| I | TRUTH | 1-5 | τ ≥ 0.9, ρ ≤ 0.2, lane=FACTUAL | F2, F4, F7 |
| II | GOVERNANCE | 6-10 | ρ ≥ 0.3, lane=CRISIS | F1, F5, F13 |
| III | AGENT | 11-15 | κ ≥ 0.5, lane=CARE | F4, F7, F10, F11 |
| IV | GROWTH | 16-20 | query_type=EXPLORATORY | F4, F7, F8 |
| V | CONNECTION | 21-25 | τ ≥ 0.9, ρ ≤ 0.2 (meta-paradox) | F4, F6, F11 |
| VI | SYSTEM | 26-30 | action=MUTATE, ρ ≥ 0.2 | F1, F8, F13 |
| VII | WITNESS | 31-33 | action=SEAL (mandatory) | F2, F3, F13 |

### The 3 Quote Organs

| Organ | Quotes | Authors | Role |
|-------|--------|---------|------|
| **MEMORY** | M1-M11 | Plato, Borges, Nietzsche, Augustine, Aristotle, Bacon, Socrates | What to remember, what to forget, how memory shapes truth |
| **MIND** | R1-R11 | Russell, Voltaire, Descartes, Socrates, Hume, James, Confucius, Sextus, Wittgenstein | How to think, when to doubt, when to act |
| **JUDGE** | J1-J11 | Parker, Plato, Aristotle, Socrates, Aurelius, Glaucon, Kant | How to decide, what justice means, when to hold |

---

## §3 — MCP TOOL SCHEMAS (System Pipeline)

### Core 9 (Public Surface)

| Tool | Stage | ABI Schema | Input | Output | Floors |
|------|-------|-----------|-------|--------|--------|
| `arif_init` | 000 | `InitAnchorRequest/Response` | `mode, actor_id, intent` | `session_id, auth_state, identity` | F1-F13 |
| `arif_observe` | 111 | `SenseRequest/Response` | `query, evidence_sources` | `observations, epistemic_label, f2_score` | F2, F4 |
| `arif_think` | 333 | `ReasonRequest/Response` | `query, hypotheses, depth` | `plan, evidence, unknowns` | F2, F4, F7, F8 |
| `arif_route` | 444 | `RouteRequest/Response` | `intent, target_organ` | `route_decision, organ_chain` | F1, F13 |
| `arif_critique` | 555 | `CritiqueRequest/Response` | `plan, risk_surface` | `risk_level, dignity_check, verdict` | F5, F6 |
| `arif_judge` | 666 | `JudgeRequest/Response` | `plan, evidence, risk` | `verdict, floors_triggered, conditions` | F1-F13 |
| `arif_forge` | 777 | `ForgeRequest/Response` | `task, authority, seal_id` | `execution_result, rollback_plan` | F1, F11 |
| `arif_seal` | 999 | `SealRequest/Response` | `outcome, verdict, evidence` | `receipt_id, vault_hash` | F2, F11 |
| `arif_memory` | 555m | `MemoryRequest/Response` | `operation, query` | `memories, stored_ids` | F2, F4 |

### Schema Pattern

```python
# ABI Layer (Pydantic v2) — /root/arifOS/arifosmcp/abi/v1_0.py
class InitAnchorRequest(BaseRequest):
    mode: Literal["init", "revoke", "refresh", "state", "status"]
    actor_id: str = Field(default="anonymous", min_length=2, max_length=64)
    intent: str | dict | None = Field(default=None, max_length=20000)

class InitAnchorResponse(BaseResponse):
    session_id: str
    auth_state: Literal["unverified", "anchored", "verified", "rejected"]
    identity: IdentityResolution
```

### Registration Chain

```
tool_registry.json (declarative)
    → runtime/tools.py _CANONICAL_HANDLERS (imperative)
    → abi/capability_registry.json (semantic contract)
    → tools/base.py Tool class (validate → check_laws → execute → run)
    → server.py create_arifos_mcp_server() (FastMCP entry point)
```

---

## §4 — A2A AGENT-CARD CONTRACTS

### Agent Card Schema (v2.0)

```json
{
  "name": "arifOS Constitutional Kernel",
  "version": "2.0.0",
  "protocolVersion": "A2A/1.0",
  "authentication": { "schemes": ["api_key", "bearer"] },
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "sealVerification": true,
    "orthogonalRouting": true
  },
  "constitutional": {
    "floors": "F1-F13",
    "omega_ortho": 0.85,
    "vault_protocol": "VAULT999"
  },
  "skills": [/* 23 skills across 6 axes: P/T/V/G/E/M */],
  "judgeSkills": ["arif_judge", "arif_seal", "arif_critique"],
  "ownedMcp": ["arif_init", "arif_observe", "arif_think", "arif_route",
               "arif_critique", "arif_judge", "arif_forge", "arif_seal", "arif_memory"]
}
```

### 6-Axis Model (P/T/V/G/E/M)

| Axis | Role | Calls | Authority |
|------|------|-------|-----------|
| **P** (Perception) | Reads only | None | OBSERVE |
| **T** (Transformation) | Computes only | None | ANALYZE |
| **V** (Valuation) | Ranks only | None | ANALYZE |
| **G** (Governance) | Routes + judges | P, T, V | GOVERN |
| **E** (Execution) | Acts on reality | None (unreachable without SEAL) | MUTATE |
| **M** (Meta) | Observes all | None | OBSERVE |

### Task Lifecycle

```
submitted → working → input_required → completed
                ↓                        ↓
             failed                   sealed (VAULT999)
                ↓
             held (888_HOLD → human review)
```

### Discovery Endpoints

```
GET  /.well-known/agent.json          # A2A Agent Card
GET  /.well-known/agent-card.json     # v2.0 full card
GET  /a2a/discover                    # List all registered agents
GET  /a2a/discover/capability/:cap    # Find by capability
POST /a2a/discover/register           # Dynamic registration
```

### Delegation Contract

```json
{
  "delegation_id": "DELEG-[hex16]",
  "from_actor": "F13 SOVEREIGN",
  "to_actor": "delegatee",
  "scope": {
    "action_class": "OBSERVE|ANALYZE|MUTATE|GOVERNED|SEAL",
    "tooling": ["tool1", "tool2"],
    "max_blast_radius": "LOW|MEDIUM|HIGH|CRITICAL"
  },
  "constitution_hash": "sha256:[hex64]",
  "sovereign_signature": { "algorithm": "Ed25519" }
}
```

---

## §5 — ARIFOS HOOK POINTS

### Where Stages Intercept

| Hook Point | Location | What It Gates |
|------------|----------|---------------|
| **Session Birth** | `arif_init` → `tools/session.py` | Identity bind, F1-F13 acceptance, carry_forward |
| **Observation** | `arif_observe` → `tools/sense.py` | Epistemic labels, organ evidence, F2 score |
| **Classification** | `Φ(text)` → `atlas.py` | GPV resolution, paradox zone activation |
| **Reasoning** | `arif_think` → `tools/reason.py` | Hypotheses, scenarios, EVOI. Proposes only |
| **Routing** | `arif_route` → `tools/kernel_canonical.py` | Organ selection, MCP/A2A/P2P decision |
| **Critique** | `arif_critique` → `tools/heart.py` | Dignity/maruah, consequence scan, F5+F6 |
| **Judgment** | `arif_judge` → `tools/judge.py` | F1-F13 floor evaluation, verdict emission |
| **Execution** | `arif_forge` → `tools/forge.py` | A-FORGE bridge, authority delegation |
| **Verification** | `arif_verify` → `tools/vault.py` | Reality check, scar detection |
| **Sealing** | `arif_seal` → `tools/vault.py` | VAULT999 receipt, hash chain |

### Constitutional Floor Enforcement

Every stage passes through floor evaluation:

```python
# tools/base.py — Tool class
async def run(self, payload, session_id=None, auth_context=None):
    validated = await self.validate(payload)      # Schema check
    law_result = await self.check_laws(payload)   # F1-F13 check
    if law_result.violated:
        return RuntimeEnvelope(verdict="VOID", violations=law_result.violations)
    result = await self.execute(payload)           # Actual execution
    return RuntimeEnvelope(verdict="SEAL", result=result)
```

### Paradox Gate Integration Point

```python
# In arif_judge (tools/judge.py) — AFTER somatic state gate
from arifosmcp.core.enforcement.paradox_gate import evaluate_paradox_gate_gpv

paradox_result = evaluate_paradox_gate_gpv(gpv, output_text, action_class)
if paradox_result.gate_verdict == "FLAGGED":
    # Add paradox flags to judge evidence
    evidence["paradox_flags"] = paradox_result.flags
    # NOT a block — a flag (F5 PEACE)
```

---

## §6 — A-FORGE EXECUTION PIPELINE

### How Execution Flows

```
arif_judge SEAL
    │
    ▼
ExecutorReceipt (Python kernel → TypeScript A-FORGE)
    │  Contains: verdict, allowed_actions, blast_radius, seal_hash
    │
    ▼
7-Layer Governance Gate
    ├── 1. Action Classification (7 tiers)
    ├── 2. Session Gate (valid session_id)
    ├── 3. Session Origin Gate (from kernel)
    ├── 4. Lease Gate (arifOS-issued lease)
    ├── 5. Pre-Forge Gate (citation + witness)
    ├── 6. ACT Gate (execution craft)
    └── 7. Auto-Seal (VAULT999 receipt)
    │
    ▼
7-Phase Execution Discipline
    ├── 1. DRY-RUN    — "What would this do?"
    ├── 2. SIMULATE   — "What does the system predict?"
    ├── 3. PREFLIGHT  — "Are guardrails in place?"
    ├── 4. EXECUTE    — "I am now changing reality"
    ├── 5. VERIFY     — "Did reality become what we intended?"
    ├── 6. ROLLBACK   — "If wrong, here is the path back"
    └── 7. RECEIPT    — "This act is now part of institutional memory"
    │
    ▼
ExecutionReport (TypeScript A-FORGE → Python kernel)
    │
    ▼
SealChain (VAULT999 hash chain)
```

### Action Classification (7 Tiers)

| Tier | Class | Requires Lease | Requires Judge | Reversible | Blast Radius |
|------|-------|---------------|----------------|------------|--------------|
| 1 | OBSERVE | No | No | Yes | None |
| 2 | SUGGEST | No | No | Yes | None |
| 3 | SIMULATE | No | No | Yes | Local |
| 4 | DRAFT | No | No | Yes | Local |
| 5 | QUEUE | Yes | No | Yes | Organ |
| 6 | EXECUTE_REVERSIBLE | Yes | Yes | Yes | Organ |
| 7 | EXECUTE_HIGH_IMPACT | Yes | Yes + 888_HOLD | Partial | Federation |
| 8 | IRREVERSIBLE | Yes | Yes + F13 | No | IRREVERSIBLE |

### forge_* Tool Surface

| Tool | Modes | Authority | Key Constraint |
|------|-------|-----------|----------------|
| `forge_filesystem` | read, write, patch, glob, grep, stat, tree, move, delete, restore | OBSERVE/MUTATE | F8 scoped to /root, /tmp, /data, /var/log |
| `forge_git` | status, diff, log, commit | OBSERVE/MUTATE | Push blocked — separate judge path |
| `forge_shell` | exec | MUTATE | ArifJudge constitutional gate + ArifSeal hash chain |
| `forge_github` | search, pr | OBSERVE/MUTATE | Lease required for MUTATE |
| `forge_postgres` | query, schema | OBSERVE/MUTATE | Writes require mutate=true + floor gate |
| `forge_docker` | ps, logs, exec, images | OBSERVE | Destructive ops out of surface |
| `forge_lease` | request, status, revoke | OBSERVE | A-FORGE does NOT self-issue — arifOS mints |

---

## §7 — THE RECONCILED FLOW (Complete)

```
                    HUMAN INTENT
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  000 INIT — arif_init                                           │
│  Identity bind (Ed25519), session creation, F1-F13 acceptance   │
│  carry_forward loaded, ATLAS333_COGNITIVE_GEOMETRY.md loaded    │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  111 ORIENT — arif_observe                                      │
│  Reality sensing, organ health, epistemic labels                │
│  Territory: ORIENT, Geometry: AUDIT or EXPLORE                  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  222 MAP — Φ(text) → GPV                                        │
│  ATLAS333 activation: lane, τ, κ, ρ, paradox_axes              │
│  PARADOX_GPV_MAP → paradox IDs (1-33)                           │
│  PARADOX_QUOTE_MAP → philosophical quotes                       │
│  Territory: REASON/ACT/VERIFY, Geometry: ENGINEER/AUDIT/CRISIS  │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  333 REASON — arif_think                                        │
│  Hypotheses N≥3, scenarios, EVOI                                │
│  Sources: ATLAS333/wiki, External corpus, Skills, Scars, DAG    │
│  Key rule: NO ACT before REASON completes                       │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  444 ROUTE — arif_route                                         │
│  Who should do this?                                            │
│  Local capability → direct                                      │
│  Tool needed → MCP                                              │
│  Agent needed → A2A                                             │
│  Distributed → P2P                                              │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  555 CRITIQUE — arif_critique                                   │
│  Ethical risk simulation, dignity/maruah check                  │
│  Consequence scan, F5+F6 enforcement                            │
│  TEARFRAME: trm≥0.94, echo≥0.87, rasa≥0.85                     │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  666 JUDGE — arif_judge                                         │
│  Constitutional verdict: SEAL | HOLD | SABAR | VOID             │
│  F1-F13 floor evaluation                                        │
│  GPV + paradox flags + TEARFRAME scores → verdict               │
│  NO execution without 666 JUDGE clearance                       │
└─────────────────────────────────────────────────────────────────┘
                         │
                    ┌────┴────┐
                    │ VERDICT │
                    └────┬────┘
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
         SEAL         HOLD         VOID
            │            │            │
            ▼            ▼            ▼
┌───────────────┐ ┌──────────────┐ ┌──────────────┐
│ 777 FORGE     │ │ 888_HOLD     │ │ BLOCKED      │
│ arif_forge    │ │ Human review │ │ Return to    │
│ → A-FORGE    │ │ F13 required │ │ 111 ORIENT   │
│ 7-phase exec │ │              │ │              │
└───────────────┘ └──────────────┘ └──────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  888 VERIFY — arif_verify                                       │
│  Reality check: did it actually work?                           │
│  Health probe, code tests, truth citations, scar check          │
│  Entropy: system stability                                      │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  999 SEAL — arif_seal                                           │
│  VAULT999 immutable receipt                                     │
│  Memory update → memory/YYYY-MM-DD.md                           │
│  carry_forward.json updated                                     │
│  ATLAS333 updated (if geometry changed)                         │
│  Hash chain: SHA-256(previous_hash, current_payload)            │
└─────────────────────────────────────────────────────────────────┘
```

---

## §8 — WHERE EVERYTHING LIVES

| Component | Primary File | Role In Flow |
|-----------|-------------|--------------|
| **ATLAS333** | `core/shared/atlas.py` | 222_MAP — decides HOW to think |
| **Paradox Quotes** | `constitution/paradox_quotes.py` | 222_MAP — 33 tension anchors |
| **Paradox Gate** | `core/enforcement/paradox_gate.py` | 666_JUDGE — resolution risk flags |
| **GPV** | `core/shared/types.py` | 222_MAP — governance placement vector |
| **FloorScores** | `core/shared/types.py` | 666_JUDGE — TEARFRAME thresholds |
| **MCP Tools** | `arifosmcp/tools/*.py` | All stages — tool handlers |
| **Tool Registry** | `arifosmcp/tool_registry.json` | All stages — declarative surface |
| **ABI Schemas** | `arifosmcp/abi/v1_0.py` | All stages — input/output contracts |
| **A2A Server** | `arifosmcp/runtime/a2a/server.py` | 444_ROUTE — agent discovery + delegation |
| **Agent Cards** | `arifosmcp/runtime/a2a/agent_card_v2.py` | 444_ROUTE — 6-axis model |
| **A-FORGE** | `/root/A-FORGE/src/` | 777_FORGE — execution pipeline |
| **VAULT999** | `/root/arifOS/VAULT999/outcomes.jsonl` | 999_SEAL — immutable receipts |

---

## §9 — THE ONE SENTENCE

```
ATLAS333 decides HOW the agent thinks
arifOS decides WHAT the agent is allowed to do
A-FORGE executes WHAT is approved
VAULT999 remembers WHAT actually happened
```

---

## §10 — MAINTENANCE

This document is **evergreen**. Update it when:
- A new stage is added to the pipeline
- A paradox zone mapping changes
- A tool schema evolves
- A new organ joins the federation
- A floor classification changes

**Update rule:** Change the code first, then update this document. Never the reverse.

**Seal rule:** Every update requires ARIF signature: `sealed_by: ARIF :: <date>`

---

*Forged 2026-07-15 by ATLAS333 Bridge Session. DITEMPA BUKAN DIBERI.*

---
## 🔗 See Also
- [ATLAS333 Evergreen (Kernel)](../core/shared/ATLAS333_EVERGREEN.md) — Canonical paradox definitions
- [GENESIS Canon](../GENESIS/README.md) — Constitutional documents
- [Governance Ontology](governance/ONTOLOGY.md) — Governance terms
