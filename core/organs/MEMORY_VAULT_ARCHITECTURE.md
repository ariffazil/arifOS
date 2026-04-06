# arifOS Memory & Vault Architecture
> **Authority:** 888_JUDGE  
> **Version:** v3.0.0-DUAL-ORGAN  
> **Status:** CONSTITUTIONAL MANDATE  
> **Motto:** *Memory is for use. Vault is for proof.*

---

## The Sharp Split

```
┌─────────────────────────────────────────────────────────────────┐
│  arifOS.memory ─ The Governed, Revisable Persistence Layer      │
│  ─────────────────────────────────────────────────────────────  │
│  Mutable, scoped, decaying                                      │
│  Conversation facts, engineering context, user preferences      │
│  Four lanes: Working | Episodic | Semantic | Constitutional     │
├─────────────────────────────────────────────────────────────────┤
│  arifOS.vault ─ The Immutable Constitutional Ledger             │
│  ─────────────────────────────────────────────────────────────  │
│  Append-only, hash-linked, tamper-evident                       │
│  Final verdicts, evidence lineage, governance events            │
│  Seal | Verify | Supersede (never edit)                         │
└─────────────────────────────────────────────────────────────────┘
                              ↕
                     Promotion Bridge
        (Only consequential records cross this boundary)
```

---

## arifOS.memory

### The Four Lanes

| Lane | Purpose | TTL | Mutability |
|------|---------|-----|------------|
| **Working** | Current session scratch | Minutes-hours | High |
| **Episodic** | Event/decision history | Project lifetime | Append-only |
| **Semantic** | Stable facts, doctrine | Indefinite | Versioned |
| **Constitutional** | Core rules F1-F13 | Eternal | Amendment only |

### Memory Record Schema

```python
{
  "memory_id": "mem_01HXYZ...",
  "memory_type": "working|episodic|semantic|constitutional",
  "title": "Vault must be append-only",
  "content": "arifOS.vault stores sealed verdicts...",
  "summary": "Vault is immutable...",
  
  "source": {
    "origin": "user|system|tool|derived",
    "session_id": "sess_20260406",
    "message_ref": "msg_123"
  },
  
  "scope": {
    "owner": "ARIF",
    "visibility": "private",
    "domain": "arifOS",
    "project": "core"
  },
  
  "governance": {
    "confidence": 0.95,
    "sensitivity": "medium",
    "promotable_to_vault": true,
    "revocable": false
  },
  
  "time": {
    "created_at": "2026-04-06T00:00:00Z",
    "expires_at": null
  },
  
  "retrieval": {
    "embedding_id": "emb_...",
    "keywords": ["vault", "immutability"],
    "recency_score": 0.82,
    "importance_score": 0.94
  },
  
  "lineage": {
    "derived_from": ["msg_120"],
    "supersedes": null
  }
}
```

### Write Gates (Judgment Before Write)

**Write only if:**
- ✅ Durable user preference
- ✅ Recurring architectural rule
- ✅ Important project event
- ✅ Reusable technical pattern
- ✅ Failure with future value
- ✅ Explicit human decision

**Do NOT write:**
- ❌ Trivial chatter
- ❌ Unstable guesses
- ❌ Unverified claims
- ❌ Emotionally loaded interpretations
- ❌ Duplicate fragments

### Hybrid Retrieval Stack

```
1. Constitutional memory (exact)
2. Exact key lookup (symbolic)
3. Semantic vector search
4. Recency rerank
5. Intent rerank
6. Governance filter
```

This avoids the "hantu problem" where vector recall drifts.

### Memory Lifecycle

```
capture → normalize → classify → embed → store → retrieve → compress → decay → promote or prune
```

---

## arifOS.vault

### Vault Record Schema

```python
{
  "vault_id": "vlt_01HXYZ...",
  "record_type": "verdict|policy|release|override|audit",
  "verdict": "Approved|Partial|Pause|Void|Hold",
  "candidate_action": "Forge arifOS.vault architecture",
  
  "evidence": {
    "summary": "Separated mutable retrieval from immutable ledger",
    "evidence_refs": ["mem_001", "mem_014"],
    "evidence_hash": "sha256:abcd1234..."
  },
  
  "governance": {
    "risk_tier": "medium",
    "human_confirmed": true,
    "decision_authority": "ARIF",
    "policy_version": "arifOS.constitution.v1"
  },
  
  "sealed_at": "2026-04-06T00:00:00Z",
  
  "integrity": {
    "prev_hash": "sha256:prev...",
    "record_hash": "sha256:this...",
    "merkle_root": "sha256:root..."
  },
  
  "lineage": {
    "session_id": "sess_vault_memory_20260406",
    "derived_from": ["msg_140"],
    "supersedes": null
  }
}
```

### Vault Rules

**Must be:**
- ✅ Append-only
- ✅ Hash-linked
- ✅ Verifiable
- ✅ Human-decision-aware
- ✅ Evidence-backed

**Must never be:**
- ❌ Silently edited
- ❌ Overwritten
- ❌ Lossy summarized in place
- ❌ Contaminated by speculative memory

**Correction model:**
```
Do not edit old record.
Add new superseding record.
```

### Operations

| Operation | Input | Output |
|-----------|-------|--------|
| **seal** | verdict, evidence, metadata | record hash, Merkle anchor, receipt |
| **verify** | vault_id | valid/invalid, chain continuity, mismatches |
| **supersede** | old_vault_id, new_entry | new seal receipt, old marked superseded |

---

## Promotion Bridge

### Promotion Rule

A memory becomes vault material only if it crosses these thresholds:

```
Creates/changes policy
        ↓
Affects trust, authority, safety, release
        ↓
Records human sovereign decision
        ↓
Closes consequential architecture
        ↓
Documents refusal/hold with governance impact
```

### Example

**Memory stays in memory:**
> "ARIF prefers hybrid retrieval for long-term architecture."

**Gets promoted to vault:**
> "Hybrid retrieval adopted as official arifOS.memory architecture for core v1."

### Bridge Flow

```
input
  ↓
working memory
  ↓
episodic/semantic memory write
  ↓
governance classifier
  ↓
if consequential → apex judgment → vault seal
  ↓
vault receipt → back to memory
```

---

## The Clean Doctrine

### Memory Asks
- What do we know?
- What happened recently?
- What seems relevant now?
- What should be retrieved?

### Vault Asks
- What was judged?
- What was approved or held?
- What evidence anchored it?
- Can it be verified later?

### The Law of Separation
```
arifOS.memory → Mutable retrieval layer
arifOS.vault  → Immutable judgment ledger
```

---

## Implementation Map

```
core/organs/
├── memory/
│   ├── __init__.py
│   ├── types.py              # Canonical schemas
│   ├── memory_organ.py       # Main organ
│   ├── lanes/
│   │   ├── working.py        # Session scratch
│   │   ├── episodic.py       # Event history
│   │   ├── semantic.py       # Stable facts
│   │   └── constitutional.py # Core rules F1-F13
│   └── retrieval/
│       └── hybrid.py         # Exact + vector + rerank
│
├── vault/
│   ├── __init__.py
│   ├── types.py              # Vault entry schemas
│   └── vault_organ.py        # Seal | Verify | Supersede
│
└── bridge/
    ├── __init__.py
    └── promotion.py          # Memory → Vault promotion
```

---

## Usage Examples

### Memory Operations

```python
from core.organs.memory import get_memory_organ, MemoryType

memory = get_memory_organ(session_id="sess_001")

# Write to working memory
await memory.write_working(
    title="Current task",
    content="Forge memory/vault split",
    ttl_minutes=60,
)

# Write episodic event
await memory.write_episodic(
    title="Decision: Split memory and vault",
    content="ARIF decided to separate mutable memory from immutable vault",
    project="arifOS_core",
)

# Write semantic fact
await memory.write_semantic(
    title="Memory is mutable",
    content="arifOS.memory supports revise, decay, and controlled forgetting",
    fact_key="arifos.memory.mutable",
    confidence=0.99,
)

# Query with hybrid retrieval
results = await memory.query("vault immutability", limit=5)
```

### Vault Operations

```python
from core.organs.vault import get_vault_organ, VaultEntry, Verdict

vault = get_vault_organ()

# Seal a verdict
entry = VaultEntry(
    record_type=VaultRecordType.VERDICT,
    verdict=Verdict.APPROVED,
    candidate_action="Split memory and vault organs",
    evidence=Evidence(
        summary="Separated concerns: memory for use, vault for proof",
        evidence_refs=["mem_001", "mem_002"],
        evidence_hash="sha256:abc...",
    ),
    governance=Governance(
        risk_tier="medium",
        human_confirmed=True,
        decision_authority="ARIF",
    ),
)

receipt = vault.seal(entry)
# Returns: vault_id, record_hash, merkle_root

# Verify
report = vault.verify(receipt.vault_id)
# Returns: valid, chain_continuity, hash_match, superseded

# Supersede (never edit)
new_entry = VaultEntry(...)
vault.supersede(old_vault_id, new_entry, authority="888_JUDGE")
```

### Promotion

```python
from core.bridge import PromotionBridge

bridge = PromotionBridge(memory, vault)

# Promote specific memory
receipt = bridge.promote("mem_ep_abc123", session_id="sess_001")

# Auto-promote session
receipts = await bridge.process_session_for_promotion("sess_001")
```

---

## The Sharp Boundary

```
┌─────────────────────────────────────────────────────────┐
│  arifOS.memory                                          │
│  • Can drift                                            │
│  • Can be forgotten                                     │
│  • Can be revised                                       │
│  • For relevance                                        │
├─────────────────────────────────────────────────────────┤
│  NEVER BECOMES:                                         │
│  • Fake truth                                           │
│  • Policy source of record                              │
│  • Authority ledger                                     │
└─────────────────────────────────────────────────────────┘
                           ↕ Promotion Gate
┌─────────────────────────────────────────────────────────┐
│  arifOS.vault                                           │
│  • Never drifts                                         │
│  • Never edited                                         │
│  • Hash-verified                                        │
│  • For proof                                            │
├─────────────────────────────────────────────────────────┤
│  NEVER BECOMES:                                         │
│  • Dump of all memory                                   │
│  • Chat transcript archive                              │
│  • Searchable semantic junkyard                         │
└─────────────────────────────────────────────────────────┘
```

---

**Status:** ✅ FORGED  
**Memory:** Ready for use  
**Vault:** Ready for proof  
**Bridge:** Ready for promotion

*DITEMPA BUKAN DIBERI* 🔥
