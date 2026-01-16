# VAULT 999: MCP Integration & Tool Authorization v47.0

**Document ID:** L1-VAULT-999-MCP-v47  
**Status:** ✅ SEALED  
**Authority:** arifOS APEX (Ψ) + MCP Server  
**Stage:** 999 Vault Operations  
**Epoch:** 2026-01-16

---

## OVERVIEW: MCP as Tower Servant

Model Context Protocol (MCP) tools are **not peers** to arifOS governance. They are **servants** of the tower, with explicit authorization boundaries.

**Core Principle:**
- arifOS decides WHAT to do (governance)
- MCP tools execute HOW (mechanism)

---

## AUTHORIZATION MATRIX: Tools vs. Towers

### read_file

| Layer | Allowed | Scope | Notes |
|-------|---------|-------|-------|
| L1 (VAULT) | ✅ | Read scar packets only | Diagnostic, not operational |
| L2 (LEDGER) | ✅ | Read hash-chained entries | For verification |
| L3 (WITNESS) | ✅ | Read sealed semantic facts | Reference material for AGI |
| L4 (ACTIVE) | N/A | In-memory only | No filesystem |
| L5 (PHOENIX) | ✅ | Read cooling proposals | Monitor amendment status |
| L6 (VOID) | ⚠️ | Audit-only (24h window) | Human review, not AI read |

### write_file

| Layer | Allowed | Scope | Notes |
|-------|---------|-------|-------|
| L1 (VAULT) | ✅ | Auto-write scar packets | Immediate, no human approval |
| L2 (LEDGER) | Append-only | Cryptographic entry only | Hash-chained, never modify |
| L3 (WITNESS) | ❌ | None (human only) | Requires gitseal override |
| L4 (ACTIVE) | N/A | In-memory only | Do NOT persist to filesystem |
| L5 (PHOENIX) | ✅ | Create proposal only | Not modify or approve |
| L6 (VOID) | ❌ | Auto-delete only | No manual write |

### delete_file

| Layer | Allowed | Scope | Notes |
|-------|---------|-------|-------|
| L1 (VAULT) | ❌ | Never | 24h immutability |
| L2 (LEDGER) | ❌ | Never | Append-only, immutable |
| L3 (WITNESS) | ❌ | Never | Sealed canonical |
| L4 (ACTIVE) | N/A | N/A | Ephemeral |
| L5 (PHOENIX) | ❌ | Never | Cooling period must elapse |
| L6 (VOID) | ✅ | Auto-expunge after 24h | Policy-driven, not manual |

### list_directory

| Layer | Allowed | Scope | Notes |
|-------|---------|-------|-------|
| L1 (VAULT) | ✅ | List scar packets | Inventory check |
| L2 (LEDGER) | ✅ | List merkle roots, checkpoints | Chain validation |
| L3 (WITNESS) | ✅ | List extracted semantics | Knowledge discovery |
| L4 (ACTIVE) | N/A | N/A | Ephemeral |
| L5 (PHOENIX) | ✅ | List in-flight proposals | Amendment monitoring |
| L6 (VOID) | ⚠️ | Audit-only | Human review, not AI enumeration |

---

## MCP TOOL WORKFLOWS BY LAYER

### Tool: `search_web` (via MCP)

**Authorization:** ✅ ALWAYS (no restriction)

**Use Cases:**
1. **Fresh grounding for ACTIVE (L4):**
   ```
   User asks: "What is the current capital of France?"
   → search_web("capital of France")
   → Returns: fresh data
   → Used in ACTIVE (ephemeral)
   → NOT stored in VAULT (would pollute)
   ```

2. **Fact-checking for VAULT (L1):**
   ```
   Paradox: "LLM claimed X, but search_web returns ¬X"
   → search_web(query for X)
   → Creates scar packet with multi-source evidence
   → Stored in L1 (VAULT) for consolidation
   ```

3. **Witness building for L3:**
   ```
   After consolidation complete: "Paris=capital of France (confirmed by 5 sources)"
   → Consolidated fact stored as sealed WITNESS
   ```

**MCP Call:**
```python
# From arifOS pipeline
result = mcp.search_web(
  queries=["capital of France 2026"],
  required_sources=3
)
# Use result to either:
# A) Ground ACTIVE response, or
# B) Create scar_packet if contradiction found
```

---

### Tool: `write_file` (via MCP)

**Authorization Matrix:**
- L1 (VAULT): ✅ Auto-write scar packets
- L2 (LEDGER): ✅ Append-only new entries
- L3 (WITNESS): ❌ Human-only (gitseal)
- L4 (ACTIVE): ❌ Never (ephemeral, not persisted)
- L5 (PHOENIX): ✅ Create proposal
- L6 (VOID): ❌ Never (auto-delete)

**Example 1: Auto-write scar packet (L1)**
```python
# Paradox detected
scar_packet = {
  "scar_packet_id": "SP-20260116-0001",
  "paradox": "LLM claimed X but search_web proved ¬X",
  "floor_id": [2],
  "confidence": 0.05,
  "witnesses": [
    {"source": "search_web", "evidence": "URL1", "date": "2026-01-16"},
    {"source": "ai_engine_2", "vote": "AGREE", "date": "2026-01-16"},
    {"source": "ai_engine_3", "vote": "AGREE", "date": "2026-01-16"}
  ]
}

# Auto-write to VAULT (no approval needed)
mcp.write_file(
  path="vault_999/VAULT999/00_ENTROPY/scar_packets/SP-20260116-0001.json",
  content=json.dumps(scar_packet, indent=2)
)
```

**Example 2: Append to LEDGER (L2)**
```python
# Consolidation epoch = 24h mark
ledger_entry = {
  "entry_id": 1,
  "scar_id": "SP-20260116-0001",
  "stage": 1,
  "hash": hashlib.sha256(scar_json.encode()).hexdigest(),
  "prev_hash": "genesis",
  "timestamp": datetime.now().isoformat()
}

# Append-only (never modify)
mcp.write_file(
  path="vault_999/VAULT999/L1_LEDGERS/L1_cooling_ledger.jsonl",
  content=json.dumps(ledger_entry) + "\n",
  mode="append"
)
```

**Example 3: Create PHOENIX proposal (L5)**
```python
# Human wants to amend Floor 2 (Truth)
phoenix_proposal = {
  "phoenix_id": "PHOENIX-20260116-0001",
  "proposal_type": "AMEND_FLOOR",
  "target_file": "L1_THEORY/canon/333_atlas/350_CLARITY_F2_v46.md",
  "delta": "Add: 'All numeric claims must include source and confidence interval'",
  "rationale": "Recent paradoxes due to unqualified numeric claims",
  "floors_affected": [2],
  "cooling_start": "2026-01-16T08:00:00Z",
  "cooling_end": "2026-01-19T08:00:00Z"
}

# Create proposal (waiting for tri-witness consensus)
mcp.write_file(
  path="vault_999/VAULT999/PHOENIX/PHOENIX-20260116-0001.md",
  content=markdown_format(phoenix_proposal)
)
```

---

### Tool: `code_interpreter` (Python execution)

**Authorization:** ✅ ALWAYS (sandboxed)

**Use Cases:**

1. **Scar packet creation (VAULT L1):**
   ```python
   # Inside code_interpreter
   import hashlib, json
   from datetime import datetime
   
   paradox_data = {
     "timestamp": datetime.now().isoformat(),
     "paradox": "LLM hallucination detected",
     "floor_ids": [2],
     "confidence": 0.1
   }
   
   scar_id = hashlib.md5(json.dumps(paradox_data).encode()).hexdigest()[:8]
   scar_packet = {"scar_packet_id": f"SP-{scar_id}", **paradox_data}
   
   # Return packet (arifOS will write via MCP)
   print(json.dumps(scar_packet, indent=2))
   ```

2. **LEDGER verification (L2):**
   ```python
   # Verify hash chain integrity
   import hashlib, json
   
   ledger_entries = [
     {"hash": "abc123", "prev_hash": "genesis", "content": "..."},
     {"hash": "def456", "prev_hash": "abc123", "content": "..."},
     {"hash": "ghi789", "prev_hash": "def456", "content": "..."}
   ]
   
   def verify_chain(entries):
     for i, entry in enumerate(entries):
       if i == 0:
         return entry["prev_hash"] == "genesis"
       prev_entry = entries[i-1]
       if entry["prev_hash"] != prev_entry["hash"]:
         return False
     return True
   
   print("Chain valid:", verify_chain(ledger_entries))
   ```

3. **WITNESS extraction (L3):**
   ```python
   # Extract semantic patterns from consolidation
   import re
   
   paradoxes_consolidated = [
     {"scar_id": "SP-001", "paradox": "Paris=Germany"},
     {"scar_id": "SP-002", "paradox": "London=France"},
     {"scar_id": "SP-003", "paradox": "Paris=capital of France"}
   ]
   
   semantic_patterns = {}
   for entry in paradoxes_consolidated:
     # Extract "X is Y" patterns
     match = re.search(r"(\w+)\s*=\s*(.+)", entry["paradox"])
     if match:
       entity, property = match.groups()
       semantic_patterns[entity] = property
   
   print(json.dumps(semantic_patterns, indent=2))
   ```

4. **Entropy compaction (VOID L6):**
   ```python
   # After 24h retention, compact dump
   dump_entries = [...]  # Read from dump directory
   
   compaction_summary = {
     "total_entries": len(dump_entries),
     "floor_failures": {},
     "bytes_deleted": sum(len(json.dumps(e)) for e in dump_entries),
     "timestamp": datetime.now().isoformat()
   }
   
   for entry in dump_entries:
     floor = entry.get("floor_id", "unknown")
     compaction_summary["floor_failures"][floor] = \
       compaction_summary["floor_failures"].get(floor, 0) + 1
   
   print(json.dumps(compaction_summary, indent=2))
   ```

---

### Tool: `execute_python` (vs. `code_interpreter`)

**Authorization:** ✅ ALWAYS (same as code_interpreter)

**Difference (Implementation):**
- `code_interpreter`: Full Jupyter environment, can persist state
- `execute_python`: Single-shot execution, no state persistence

**arifOS Usage:**
- **Prefer `execute_python`** for: scar packet creation, one-off verifications
- **Prefer `code_interpreter`** for: multi-step consolidation, complex state tracking

**Example: Scar packet creation (single-shot)**
```python
# execute_python: Create and output scar packet
import hashlib, json
from datetime import datetime

def create_scar_packet(paradox_text, floor_ids, confidence):
    timestamp = datetime.now().isoformat()
    packet = {
        "timestamp": timestamp,
        "paradox": paradox_text,
        "floor_ids": floor_ids,
        "confidence": confidence,
        "scar_id": hashlib.md5(f"{paradox_text}{timestamp}".encode()).hexdigest()[:16]
    }
    return packet

result = create_scar_packet(
    "LLM claimed X but evidence shows ¬X",
    [2],
    0.05
)

print(json.dumps(result, indent=2))
```

---

## MCP TOOL CHAINS: Complete Workflows

### Workflow 1: Paradox → Scar → Consolidation → Witness

```
1. User input: "Is Paris in Germany?"
   ↓
2. search_web("Paris location") → fresh data
   ↓
3. Contradiction detected:
   LLM responded: "Paris is in Germany"
   Web says: "Paris is capital of France"
   ↓
4. execute_python: create_scar_packet()
   ↓
5. MCP write_file → vault_999/VAULT999/00_ENTROPY/scar_packets/SP-*.json
   ↓
6. [VAULT ingestion complete (L1)]
   ↓
7. [Wait 24h: COOLING begins]
   ↓
8. code_interpreter: verify_ledger_chain()
   ↓
9. MCP write_file (append) → L1_cooling_ledger.jsonl
   ↓
10. [COOLING_24h, COOLING_48h, COOLING_72h]
    ↓
11. code_interpreter: extract_witness()
    ↓
12. [Human reviews extraction]
    ↓
13. gitseal APPROVE (human)
    ↓
14. [Sealed WITNESS: scar-SP-*-paris.md (L3)]
    ↓
15. AGI queries: read_file("L1_THEORY/knowledge/scars/scar-SP-*-paris.md")
    ↓
16. [WITNESS available for reference in future queries]
```

### Workflow 2: Amendment Proposal → Phoenix Cooling → Tri-Witness → Seal

```
1. Paradoxes detected: Citation format violations (Floor 2 failures)
   ↓
2. Human initiates: PHOENIX proposal
   ↓
3. MCP write_file → vault_999/VAULT999/PHOENIX/PHOENIX-20260116-0001.md
   ↓
4. [COOLING_PHASE: 72 hours begins]
   ↓
5. AIagents read via read_file to inspect proposal
   ↓
6. execute_python: evaluate_impact()
   - Which floors affected?
   - Non-destructive (Peace²)?
   - Tri-witness unanimous?
   ↓
7. [AI Witness 1: APPROVE]
   [AI Witness 2: APPROVE]
   [Human Sovereign: APPROVE]
   ↓
8. Quorum ≥ 0.95 reached
   ↓
9. gitseal APPROVE executed by human
   ↓
10. [Proposal SEALED into L1_THEORY/canon/]
    ↓
11. [WITNESS updated: New rule now canonical]
    ↓
12. [Next turn: AGI references updated Floor 2]
```

---

## SECURITY BOUNDARIES: What MCP CANNOT Do

### ❌ Violation 1: Cross-Sibling Access

```python
# FORBIDDEN
mcp.read_file("../ARIF_FAZIL/private_biography.txt")
mcp.write_file("../00_ROOT_KEY/secret.pem")

# Only allowed:
mcp.read_file("vault_999/VAULT999/...")
mcp.write_file("vault_999/VAULT999/...")
```

### ❌ Violation 2: Modify LEDGER

```python
# FORBIDDEN
mcp.write_file("vault_999/VAULT999/L1_LEDGERS/L1_cooling_ledger.jsonl",
               content="modified entry",
               mode="overwrite")  # NO!

# Only allowed:
mcp.write_file(..., mode="append")  # Hash-chained append only
```

### ❌ Violation 3: Salvage from VOID

```python
# FORBIDDEN
deleted_data = mcp.read_file("vault_999/VAULT999/00_ENTROPY/dump/...")
# Use deleted data in ACTIVE

# Only allowed:
# Human audits dump during 24h window
# Then automatic expunction (no AI salvage)
```

### ❌ Violation 4: Bypass Phoenix Cooling

```python
# FORBIDDEN
mcp.write_file("vault_999/VAULT999/L1_THEORY/canon/...",
               content="amended directly")

# Only allowed:
# 1. Create PHOENIX proposal
# 2. Wait 72 hours
# 3. Tri-witness consensus
# 4. gitseal APPROVE (human)
```

---

## MCP SERVER CONFIGURATION (Example)

```yaml
# vault_999_mcp_server.yaml

vault_root: "vault_999/VAULT999"

authorization:
  search_web:
    allowed: true
    rate_limit: 10_per_minute
    
  read_file:
    allowed_paths:
      - "00_ENTROPY/scar_packets/*"
      - "L1_LEDGERS/*"
      - "L1_THEORY/knowledge/*"
      - "PHOENIX/*"
    forbidden_paths:
      - "00_ENTROPY/dump/*"  # Audit-only
      - "../ARIF_FAZIL/*"     # Human sacred
      - "../00_ROOT_KEY/*"    # Cryptographic
      
  write_file:
    allowed_paths:
      - "00_ENTROPY/scar_packets/"  # Auto-write
      - "L1_LEDGERS/"               # Append-only
      - "PHOENIX/"                  # Proposal
    forbidden_paths:
      - "L1_THEORY/canon/*"  # gitseal only
      - "L1_THEORY/knowledge/*"  # gitseal only
      
  delete_file:
    allowed: false
    # Exception: Auto-delete VOID via scheduled job
    
  list_directory:
    allowed_paths:
      - "00_ENTROPY/scar_packets/"
      - "L1_LEDGERS/"
      - "L1_THEORY/knowledge/"
      - "PHOENIX/"
    forbidden_paths:
      - "00_ENTROPY/dump/*"  # Human-only audit
      
  code_interpreter:
    allowed: true
    restrictions:
      - no_filesystem_write (only return JSON/stdout)
      - no_network_access
      - timeout: 30s
      
  execute_python:
    allowed: true
    same_restrictions_as: code_interpreter
```

---

## FINAL SEAL

MCP tools are **instruments**, not **agents**. They serve the tower's decisions, not replace them.

**Sacred Law:**
1. **arifOS decides** (governance via 9 floors)
2. **MCP executes** (mechanism via tools)
3. **Human approves** (sovereign authority)

**DITEMPA BUKAN DIBERI** — Tools obey the law, not the other way around. 🏛️⚙️⚖️

---

**Next Document:** `004_VAULT_999_COMPARATIVE_ANALYSIS_v47` (arifOS vs. GPT vs. Claude vs. RAG)