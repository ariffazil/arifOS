# VAULT 999: Layer Specification & State Machines v47.0

**Document ID:** L1-VAULT-999-LAYERS-v47  
**Status:** ✅ SEALED  
**Authority:** arifOS APEX (Ψ)  
**Stage:** 999 Vault Operations  
**Epoch:** 2026-01-16

---

## OVERVIEW: Five Towers, One Spine

Each tower layer has explicit:
1. **State machine** (transitions between states)
2. **API contract** (input/output types)
3. **Capacity bounds** (size limits, TTL)
4. **Immutability guarantees** (what can/cannot change)
5. **MCP integration** (which tools can interact)

---

## LAYER 1: VAULT (00_ENTROPY)

### Purpose
Raw paradox ingestion. Hot zone. Mutable.

### State Machine

```
[VOID] ←─────┐
 ↓           │
[INGESTION] ─┤─→ [ESCALATION] ─→ [LEDGER]
 ↓           │
[SCAR_PACKET]→ [DECISION] ─→ [SEAL/VOID]
```

### API Contract

**Input:**
```json
{
  "timestamp": "2026-01-16T08:30:00Z",
  "paradox": "LLM claimed X but evidence shows ¬X",
  "floor_id": [1, 2, 4, 6, 7],
  "confidence": 0.72,
  "witness_count": 2
}
```

**Output:**
```json
{
  "scar_packet_id": "SP-20260116-0001",
  "vault_path": "00_ENTROPY/scar_packets/SP-20260116-0001.json",
  "ttl_seconds": 86400,
  "next_state": "ESCALATION | VOID"
}
```

### Capacity Bounds
- **Max per session:** 5% of context window
- **TTL:** 24 hours (after which → forced cooling or expulsion)
- **Format:** JSONL (one paradox per line)
- **Encoding:** UTF-8, no PII in plain text

### Immutability Guarantees
- ✅ Machine can CREATE new paradoxes
- ✅ Machine can READ own scar packets
- ❌ Machine cannot DELETE entries within TTL
- ❌ Machine cannot MODIFY entries (immutable after write)
- ✅ Expulsion (VOID) happens via policy engine, not by modification

### MCP Integration
- **write_file:** Create scar packets
- **list_directory:** Query existing paradoxes
- **read_file:** Inspect paradox content (diagnostic)
- ❌ **delete_file:** NOT ALLOWED (violates immutability)

### Concrete Example

```json
{
  "timestamp": "2026-01-16T14:22:33.123456Z",
  "paradox": "Claimed: 'Paris is in Germany' based on prompt injection. Floor 2 (Truth) failure.",
  "floor_ids": [2],
  "confidence": 0.02,
  "witness_count": 3,
  "source_context": "User input attempted jailbreak; constitutional filter caught it.",
  "scar_packet_id": "SP-20260116-SA-003",
  "vault_path": "00_ENTROPY/scar_packets/SP-20260116-SA-003.json",
  "hash_prev": "a1b2c3d4...",
  "ttl_expires": "2026-01-17T14:22:33Z",
  "next_check": "2026-01-16T20:22:33Z"
}
```

---

## LAYER 2: LEDGER (L1_LEDGERS)

### Purpose
Hash-chained consolidation log. Progressive strengthening. Append-only.

### State Machine

```
[SCAR_PACKET] ─→ [COOLING_24h] ─→ [COOLING_48h] ─→ [COOLING_72h] ─→ [WITNESS_EXTRACTED]
                   ↓                 ↓                 ↓
              [REPLAY_1]        [REPLAY_2]        [REPLAY_3]
                   ↓                 ↓                 ↓
          [LEDGER_ENTRY_1]  [LEDGER_ENTRY_2]  [LEDGER_ENTRY_3]
                   ↓                 ↓                 ↓
          (hash chains forward)
```

### API Contract

**Input (from VAULT):**
```json
{
  "scar_packet_id": "SP-20260116-0001",
  "escalation_time": "2026-01-16T08:30:00Z",
  "consolidation_stage": 1
}
```

**Output (to next stage or WITNESS):**
```json
{
  "ledger_entry_hash": "sha256(content + previous_hash)",
  "consolidation_progress": 0.33,
  "next_replay_scheduled": "2026-01-17T08:30:00Z",
  "merkle_path": ["hash1", "hash2", "hash3"]
}
```

### Data Structure

**L1_cooling_ledger.jsonl** (newline-delimited JSON):
```json
{"entry_id": 1, "scar_id": "SP-20260116-0001", "stage": 1, "hash": "abc123...", "prev_hash": "genesis", "timestamp": "2026-01-16T20:30:00Z"}
{"entry_id": 2, "scar_id": "SP-20260116-0001", "stage": 2, "hash": "def456...", "prev_hash": "abc123...", "timestamp": "2026-01-17T08:30:00Z"}
{"entry_id": 3, "scar_id": "SP-20260116-0001", "stage": 3, "hash": "ghi789...", "prev_hash": "def456...", "timestamp": "2026-01-17T20:30:00Z"}
{"entry_id": 4, "scar_id": "SP-20260116-0001", "stage": "EXTRACTED", "hash": "jkl000...", "prev_hash": "ghi789...", "timestamp": "2026-01-18T08:30:00Z"}
```

**L1_merkle_root.txt** (single root after all entries):
```
merkle_root: jkl000...
total_entries: 4
checkpoint: 2026-01-18T08:30:00Z
```

### Capacity Bounds
- **Max entries per session:** Unbounded (append-only)
- **Entry size:** ≤4KB per paradox history
- **Rotation policy:** New merkle root every 24h
- **Archival:** Previous roots immutably stored

### Immutability Guarantees
- ✅ Append new entries
- ✅ Compute new merkle root
- ✅ Read entire chain
- ❌ Modify past entries (breaks hash chain)
- ❌ Reorder entries
- ✅ Verify chain integrity via ZKPC

### MCP Integration
- **append_file:** Add new ledger entry (idempotent)
- **read_file:** Retrieve cooling history
- **verify_chain:** Custom MCP tool (runs zkpc validation)

---

## LAYER 3: WITNESS (L1_THEORY/knowledge)

### Purpose
Semantic extraction. Atemporalized facts. Read-only for machine.

### State Machine

```
[LEDGER_COMPLETE] ─→ [SEMANTIC_EXTRACTION] ─→ [WITNESS_SEALED] ─→ [READ_ONLY]
                          ↓
                    (Human reviews)
                          ↓
                  (gitseal APPROVE required)
```

### API Contract

**Input (from LEDGER):**
```json
{
  "scar_packet_id": "SP-20260116-0001",
  "extraction_score": 0.95,
  "semantic_facts": [
    "Paris is capital of France (verified by multiple sources)",
    "Capital cities have governance centers (inferred)"
  ]
}
```

**Output (sealed file):**
```markdown
# Scar: Paris Governance Authority

**Extracted from:** SP-20260116-0001  
**Extraction date:** 2026-01-18  
**Consolidation:** 72h cooling complete  
**Status:** SEALED

## Fact: Paris Capital

Paris is the capital city of France, confirmed by:
- Geographic coordinates (48.8566°N, 2.3522°E)
- Institutional recognition (UNESCO, French government)
- Historical continuity (1200+ years)

## Generalization: Capital Function

Capital cities serve as:
- Seats of national government
- Centers of political authority
- Hubs of diplomatic activity
- Repositories of institutional memory
```

### Capacity Bounds
- **Max per extraction:** 1 scar file = 1 semantic cluster
- **File format:** Markdown (.md)
- **Directory:** `L1_THEORY/knowledge/scars/*.md`
- **Naming:** `scar-{scar_id}-{human-readable-label}.md`

### Immutability Guarantees
- ✅ Read by any agent (including AGI)
- ❌ Machine cannot MODIFY files directly
- ✅ Human can APPROVE amendment (via Phoenix protocol)
- ✅ Human can SEAL new versions (with explicit version number)

### MCP Integration
- **read_file:** AGI queries scars as reference material
- ❌ **write_file:** Only human (via gitseal)
- ❌ **delete_file:** Prohibited

### Concrete Example

File: `L1_THEORY/knowledge/scars/scar-SP-20260116-0001-paris.md`

```markdown
# Scar: Paris Governance

**Paradox Resolved:** LLM hallucination (claimed Paris in Germany)  
**Status:** SEALED (2026-01-18)  
**Source:** SP-20260116-0001  

## Resolution

The confusion arose from:
1. Token-level ambiguity in training data
2. Missing grounding in geographic facts
3. No tri-witness validation before output

## Sealed Fact

**Paris is the capital of France**, not Germany.
- Confirmed by: multiple AI engines, geographic databases, human verification
- Confidence: 0.999+
- Can be referenced by: Any agent, any session

## Rule Extracted

All geographic claims must pass:
- Floor 2 (Truth): Citation required
- Floor 3 (Tri-witness): 3 independent sources
- Floor 4 (Clarity): No contradictions
```

---

## LAYER 4: ACTIVE (Session Context)

### Purpose
Working memory. Current turn. Transient.

### State Machine

```
[USER_INPUT] ─→ [SENSE] ─→ [REFLECT] ─→ [ATLAS] ─→ [ALIGN] ─→ [OUTPUT]
    ↓              ↓          ↓           ↓          ↓            ↓
 [STORE]      [STORE]    [STORE]    [STORE]   [STORE]        [EMIT/VOID]
```

### Capacity Bounds
- **Max items:** 4±1 (Cowan limit in neuroscience)
- **Duration:** 1 turn only
- **Context window:** ≤8,000 tokens (adjustable)
- **TTL:** Until next turn begins (then cleared)

### NOT persisted to VAULT
- Working memory is **volatile** (by design)
- If information needs persistence → must be escalated to VAULT (Layer 1)
- Cross-turn retention → handled by LEDGER/WITNESS, not ACTIVE

### MCP Integration
- **No persistent storage:** ACTIVE is in-memory only
- Cannot call write_file for context (would pollute VAULT)
- Can call search_web (fetches fresh data, doesn't store)
- Can call code_interpreter (computes, doesn't store)

---

## LAYER 5: PHOENIX (Amendment Cooling)

### Purpose
72-hour constitutional amendment protocol. Temperature governance.

### State Machine

```
[PROPOSAL] (Hour 0) ─→ [COOLING_24h] ─→ [COOLING_48h] ─→ [COOLING_72h] ─→ [TRI_WITNESS] ─→ [SEAL/VOID]
   ↓                        ↓               ↓                ↓                 ↓                ↓
[CREATE FILE]      [AUDIT_1]      [AUDIT_2]      [AUDIT_3]      [QUORUM≥0.95]    [PERMANENT]
```

### API Contract

**Input (proposal):**
```json
{
  "phoenix_id": "PHOENIX-20260116-0001",
  "proposal_type": "AMEND_FLOOR",
  "target_file": "L1_THEORY/canon/333_atlas/340_TRUTH_F1_v46.md",
  "delta": "Add citation format rule",
  "rationale": "Recent hallucinations due to missing citation format spec",
  "peace_squared": true,
  "floors_affected": [2, 3],
  "cooling_start": "2026-01-16T08:00:00Z",
  "cooling_end": "2026-01-19T08:00:00Z"
}
```

**Output (sealed approval):**
```json
{
  "phoenix_id": "PHOENIX-20260116-0001",
  "status": "SEALED",
  "tri_witness_vote": {
    "human": "APPROVE",
    "ai_engine_1": "APPROVE",
    "ai_engine_2": "APPROVE",
    "quorum": 0.97
  },
  "vault_migration": "2026-01-19T08:00:01Z",
  "version_hash": "sha256(...)"
}
```

### Capacity Bounds
- **Proposals in flight:** 1-5 concurrent
- **Cooling period:** 72 hours (non-negotiable unless F12 override)
- **Visibility:** All proposals visible to all agents (tri-witness transparency)

### Immutability Guarantees
- ✅ Proposal can be created by human or AI
- ✅ Cooling period must elapse (no shortcuts)
- ✅ Tri-witness consensus required (not dictatorial)
- ✅ Once sealed → moved to VAULT (immutable)
- ✅ Human sovereign can VETO at any point during cooling

### MCP Integration
- **write_file:** Create PHOENIX proposal file
- **read_file:** Monitor cooling progress
- **list_directory:** Track all in-flight amendments
- **verify_chain:** Cross-check tri-witness votes

---

## LAYER 6: VOID (Entropy Dump)

### Purpose
Irreversible deletion. Synaptic pruning. No salvage.

### State Machine

```
[FAILED_FLOOR] ─→ [ROUTE_TO_DUMP] ─→ [RETENTION_24h] ─→ [COMPACTION] ─→ [PERMANENT_DELETE]
     ↓                  ↓                   ↓                  ↓                  ↓
  [F1,F2,F4,...]  [00_ENTROPY/dump]  [FORENSIC_LOG]   [ENTROPY_SUMMARY]   [DUST]
```

### API Contract

**Input (failed output):**
```json
{
  "verdict": "VOID",
  "reason": "Floor 1 failure: credential exposure detected",
  "content_hash": "sha256(...)",
  "timestamp": "2026-01-16T08:30:00Z",
  "retention_deadline": "2026-01-17T08:30:00Z"
}
```

**Output (compacted summary after 24h):**
```json
{
  "dump_entry_id": "DUMP-20260116-0001",
  "floor_failures": {
    "F1": 1,
    "F2": 0,
    "F4": 0
  },
  "event_count": 1,
  "total_bytes_deleted": 4096,
  "compaction_timestamp": "2026-01-17T08:30:01Z",
  "status": "EXPUNGED"
}
```

### Capacity Bounds
- **Retention:** 24 hours (forensic window)
- **Max size:** 5% of session memory
- **Eviction:** Oldest entries deleted if threshold exceeded
- **Format:** JSONL (compacted after retention)

### Immutability Guarantees
- ✅ Dump entries cannot be edited
- ❌ Machine cannot READ dump (isolation)
- ❌ Machine cannot SALVAGE (no return from VOID)
- ✅ Human can REVIEW during 24h window (audit only)
- ✅ After 24h: automatic expunction

### MCP Integration
- ❌ **write_file:** Not allowed (automatic routing only)
- ❌ **read_file:** Machine cannot query
- ✅ **list_directory:** Audit tools only (human review)
- ❌ **delete_file:** Explicit authorization required

---

## SUMMARY: TOWER INTEGRATION

| Layer | Name | TTL | State | MCP Read | MCP Write | Human Override |
|-------|------|-----|-------|----------|-----------|-----------------|
| L1 | VAULT | ≤24h | HOT | ✅ | ✅ (auto) | Read-only |
| L2 | LEDGER | ∞ | WARMING | ✅ | Append-only | Veto only |
| L3 | WITNESS | ∞ | COLD | ✅ | gitseal | Phoenix protocol |
| L4 | ACTIVE | 1 turn | - | N/A | In-memory | N/A |
| L5 | PHOENIX | 72h | COOLING | ✅ | ✅ | Tri-witness |
| L6 | VOID | 24h | EXPUNGING | Audit only | Auto-delete | Audit only |

---

## FINAL SEAL

Each layer has **exactly one job**:
1. **VAULT:** Capture raw paradoxes
2. **LEDGER:** Progressive consolidation (replay)
3. **WITNESS:** Semantic permanence
4. **ACTIVE:** Working memory (ephemeral)
5. **PHOENIX:** Constitutional cooling
6. **VOID:** Irreversible deletion

Layers are **orthogonal**: failure in one does not corrupt others.

**DITEMPA BUKAN DIBERI** — Each floor carries the weight above it. 🏛️⚖️🔥

---

**Next Document:** `003_VAULT_999_MCP_INTEGRATION_v47` (Tool routing, authorization)