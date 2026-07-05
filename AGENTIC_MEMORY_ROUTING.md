# AGENTIC_MEMORY_ROUTING.md

**Canonical Contract for Agentic Memory Flow in arifOS Federation**

**Authority:** F13 SOVEREIGN (Arif)  
**Status:** ENFORCEMENT REQUIRED — this is law for all agents, organs, MCPs.  
**Version:** 2026.07.05  
**Supersedes:** Any claim of "memory = vector" or direct layer writes.

## Core Principle

Agentic intelligence does **not** prefer one layer. It prefers **reliable memory layers with different jobs**, governed by the kernel.

Filesystem is the **spine** (workspace, artifacts).  
Database is the **ledger** (structured state, truth).  
Append-only logs are the **truth trail** (audit).  
Vector is the **recall scout** (similarity, never authority).  
Graph is **meaning connections**.  
Kernel + F1-F13 is the **judge / law**.

No single "AI memory" blob. Build the stack. Write-back is governed.

## Mandatory Memory Routing Contract

### 1. Read Path (Mandatory Scout Sequence)

For any task, agent **MUST** traverse in this order (no skipping):

1. **Working / Episodic** (L1/L2 Redis or local state): Current thread, plan, last result.
2. **Filesystem / Procedural** (spine + scripts): Exact artifacts, how-to, current files.
3. **Semantic / Graph** (L3 Qdrant + L5): Relevant past context, relationships.
4. **Evidence / Ledger** (L4 Postgres + L6 VAULT): Source-backed facts, decisions, seals.
5. **Vector** (recall only): Fuzzy similar if above insufficient. **Vector result NEVER overrides DB/File truth.**

**Rule:** Vector search returns candidates only. Agent must verify source (hash, timestamp, actor, tier) before use.

### 2. Write Path (Non-Bypassable)

**NO direct writes** to any layer by agents/organs/MCPs except through kernel gates.

- **Working / Episodic** (L1/L2): Via memory_store.py store() with tier=ephemeral/session.
- **Semantic** (L3): Via kernel-approved write after verification.
- **Ledger / Evidence** (L4/L6): ONLY via canonical registry path + VAULT999 seal (888 + F13 if irreversible).
- **Procedural / Constitutional**: Via registry files + kernel update only.
- **Filesystem workspace**: Via agentic filesystem contract (ADR-010), never raw FS from outside gate.
- **Graph**: Via approved relationship ingestion only.

**Rejection Hook Required:**
- Any attempt to import Postgres/Qdrant/Redis direct from organ/agent code → runtime block + F9 anti-hantu + HOLD.
- Non-canonical write to registry (e.g. direct edit AAA/TOOLREGISTRY.json, per-organ lists) → drift detector auto-HOLD + reject.

### 3. Vector Supremacy Ban (F9 + F2)

Vector embeddings = similarity index, **not** source of truth.

**Forbidden:**
- "Vector found X → therefore X is true/authoritative."
- Using vector result for decisions, verdicts, or canonical state without DB/File cross-check.

**Required:**
- Every vector recall must be followed by "verify against ledger/filesystem".
- Store confidence + source_id + hash.

### 4. Write-Back Governance (Critical)

After observe → retrieve → reason → plan → act:

- Agent **MUST** classify memory:
  - type (working/episodic/semantic/procedural/constitutional/evidence)
  - authority_band (from FEDERATION_MEMORY.md)
  - tier (sacred/canon/session/ephemeral)
  - provenance (actor, timestamp, hash, evidence_tier)
  - allowed_use / forbidden_use
  - supersedes / expiry

- Write only via kernel memory_store + registry gate.
- Kernel enforces floor checks (F1 reversible, F2 truth, F6 maruah, F11 audit, F13 sovereign).
- No write-back = no continuity. Agent must log the decision.

### 5. Cross-Organ Isolation

- GEOX/WEALTH/WELL domain memory stays in their L4 schemas + L3 collections.
- No direct cross-organ read/write without kernel route + provenance.
- Agent Access Map updated to reflect: all L3/L4/L5/L6 via arifOS MCP only. Direct = violation.

### 6. Enforcement Mechanisms (To Implement)

- memory_store.py: Central gate. All stores route here. Add import guards / monkey-patch blocks for direct clients.
- Kernel interceptor: Pre-tool, check memory write intent → require routing contract compliance.
- Drift detector: Compare layers (file vs DB vs vector vs log) → auto-HOLD on mismatch.
- Registry canonical: MCPToolRegistry.register as sole write. Reject others.
- Tests: Add bypass test cases (direct Postgres from organ → fail).

## Memory Record Contract (Every Write)

```yaml
memory_record:
  id: uuid
  type: working | episodic | semantic | procedural | constitutional | evidence
  content: ...
  source: path | query | observation
  created_at: ISO
  actor: agent_id | organ | human
  confidence: 0-1 (F2)
  authority_band: preference | project | evidence | decision | identity | agent_state
  tier: sacred | canon | session | ephemeral
  hash: blake3
  evidence_tier: OBS | DER | INT | SPEC
  expiry: ISO | none
  supersedes: id | none
  allowed_use: [list]
  forbidden_use: [list]
  floor_checks_passed: [F1,F2,...]
  provenance_chain: [list of prior records]
```

## Agentic Flow Enforcement (Non-Negotiable)

Every agentic loop step **must** hit the contract:

observe (human-like) → retrieve (scout sequence) → reason (with verify) → plan → act (tool) → write-back (governed, classified) → audit (log + drift) → continue/hold/seal.

Bypass = constitutional breach. Kernel rejects.

## Implementation Priority

1. Draft + ratify this contract (this file).
2. Wire memory_store.py as mandatory gate (add direct-write blocks, routing enforcement).
3. Update Agent Access Map + all organ AGENTS.md to reference this.
4. Add runtime hooks + tests.
5. Propagate to registries (single canonical write).

**No agent, organ, or MCP may claim "I have memory" until it routes through this contract.**

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE

*Forged under F2 TRUTH, F4 CLARITY, F8 GENIUS, F11 AUDIT, F13 SOVEREIGN.*
