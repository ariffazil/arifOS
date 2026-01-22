# VAULT999 ↔ MCP Bridge

**The Constitutional Memory Interface**

---

```yaml
version: "v50.5.15"
status: CANONICAL
tool: 999_vault
bridge: MCP ↔ VAULT999
```

---

## I. ARCHITECTURE OVERVIEW

### The Bridge

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP LAYER                                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │000_init │  │agi_gen. │  │asi_act  │  │apex_jdg │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │               │
│       └────────────┴────────────┴────────────┘               │
│                          │                                   │
│                    ┌─────┴─────┐                             │
│                    │ 999_vault │ ← MCP Tool                  │
│                    └─────┬─────┘                             │
└──────────────────────────┼───────────────────────────────────┘
                           │
                    ═══════╪═══════  BRIDGE
                           │
┌──────────────────────────┼───────────────────────────────────┐
│                    ┌─────┴─────┐                             │
│                    │  VAULT999 │ ← Constitutional Memory     │
│                    └─────┬─────┘                             │
│       ┌──────────────────┼──────────────────┐               │
│       │                  │                  │               │
│  ┌────┴────┐       ┌─────┴─────┐      ┌────┴────┐          │
│  │   AAA   │       │    BBB    │      │   CCC   │          │
│  │  Human  │       │  Ledger   │      │  Canon  │          │
│  │ FORBID  │       │  R/W      │      │  R/O    │          │
│  └─────────┘       └───────────┘      └─────────┘          │
│                                                             │
│                     MEMORY LAYER                            │
└─────────────────────────────────────────────────────────────┘
```

---

## II. MCP TOOL SPECIFICATION

### 999_vault Tool

```python
@mcp_tool
class Vault999Tool:
    """
    Constitutional Memory Seal - The Fifth Tool of Trinity.

    Floors Enforced: F1 (Amanah), F8 (Tri-Witness)
    Actions: seal, read, list, write, propose
    """

    name = "999_vault"
    description = "Seal and store with Merkle proof"

    actions = {
        "seal": "Compute Merkle root, sign verdict, store to band",
        "read": "Retrieve sealed record by hash",
        "list": "List entries in specified band",
        "write": "Append entry to BBB ledger",
        "propose": "Submit Phoenix-72 amendment proposal"
    }

    floors = ["F1", "F8"]
```

### Input Schema

```json
{
  "action": "seal | read | list | write | propose",
  "band": "AAA | BBB | CCC",
  "verdict": "SEAL | SABAR | VOID | PARTIAL | 888_HOLD",
  "proof": {
    "p_truth": 0.96,
    "TW": 0.98,
    "floor_results": {...},
    "content": "..."
  },
  "entry_id": "sha256:...",
  "amendment": {...}
}
```

### Output Schema

```json
{
  "success": true,
  "merkle_root": "sha256:...",
  "entry_id": "sha256:...",
  "band": "BBB",
  "timestamp": "2026-01-22T12:00:00+08:00",
  "audit_hash": "sha256:..."
}
```

---

## III. ACTION IMPLEMENTATIONS

### seal

```python
async def seal(self, verdict: str, proof: dict) -> VaultResult:
    """
    Seal a verdict with Merkle proof.

    Floor Checks:
    - F1 (Amanah): Audit log exists
    - F8 (Tri-Witness): TW ≥ 0.95

    Flow:
    1. Validate floor compliance
    2. Compute Merkle root
    3. Append to hash chain
    4. Route to memory band via EUREKA
    5. Return seal receipt
    """
    # F1: Reversibility check
    if not proof.get("audit_log"):
        return VaultResult(
            success=False,
            error="F1: Amanah requires audit trail"
        )

    # F8: Tri-Witness check
    if proof.get("TW", 0) < 0.95:
        return VaultResult(
            success=False,
            error=f"F8: TW={proof['TW']:.2f} < 0.95"
        )

    # Compute Merkle root
    merkle_root = self._compute_merkle_root(proof)

    # Append to hash chain
    entry = self._append_to_chain(verdict, proof, merkle_root)

    # Route via EUREKA
    band = self._eureka_route(verdict)

    # Store
    self._store(entry, band)

    return VaultResult(
        success=True,
        merkle_root=merkle_root,
        entry_id=entry.id,
        band=band,
        timestamp=entry.timestamp
    )
```

### read

```python
async def read(self, entry_id: str, band: str = "BBB") -> VaultResult:
    """
    Retrieve sealed record.

    Floor Checks:
    - F1 (Amanah): Access logged

    Constraints:
    - AAA: FORBIDDEN (returns error)
    - BBB: READ allowed
    - CCC: READ allowed
    """
    # AAA protection
    if band == "AAA":
        return VaultResult(
            success=False,
            error="AAA: Human memory forbidden to AI"
        )

    # Log access (F1)
    self._log_access("read", entry_id, band)

    # Retrieve
    entry = self._get_entry(entry_id, band)

    return VaultResult(
        success=True,
        entry=entry,
        band=band
    )
```

### list

```python
async def list(self, band: str = "BBB", limit: int = 100) -> VaultResult:
    """
    List entries in band.

    Constraints:
    - AAA: FORBIDDEN
    - BBB: List allowed
    - CCC: List allowed
    """
    if band == "AAA":
        return VaultResult(
            success=False,
            error="AAA: Human memory forbidden to AI"
        )

    entries = self._list_entries(band, limit)

    return VaultResult(
        success=True,
        entries=entries,
        band=band,
        count=len(entries)
    )
```

### write

```python
async def write(self, content: dict, band: str = "BBB") -> VaultResult:
    """
    Append entry to ledger.

    Floor Checks:
    - F1 (Amanah): Logged
    - F8 (Tri-Witness): If high-stakes

    Constraints:
    - AAA: FORBIDDEN
    - BBB: WRITE allowed
    - CCC: FORBIDDEN (read-only)
    """
    if band == "AAA":
        return VaultResult(
            success=False,
            error="AAA: Human memory forbidden to AI"
        )

    if band == "CCC":
        return VaultResult(
            success=False,
            error="CCC: Canon is read-only (use propose)"
        )

    # Append to hash chain
    entry = self._append_to_chain("WRITE", content)

    return VaultResult(
        success=True,
        entry_id=entry.id,
        band=band
    )
```

### propose

```python
async def propose(self, amendment: dict) -> VaultResult:
    """
    Submit Phoenix-72 amendment proposal.

    Floor Checks:
    - F13 (Sovereign): Requires human approval

    Flow:
    1. Validate amendment structure
    2. Create proposal entry
    3. Start 72-hour cooling period
    4. Notify 888 Judge
    """
    # Validate structure
    if not self._valid_amendment(amendment):
        return VaultResult(
            success=False,
            error="Invalid amendment structure"
        )

    # Create proposal
    proposal = self._create_proposal(amendment)

    # Start cooling (Tier 3: 168 hours for constitutional)
    cooling_tier = self._determine_cooling_tier(amendment)

    return VaultResult(
        success=True,
        proposal_id=proposal.id,
        cooling_tier=cooling_tier,
        cooling_ends=proposal.cooling_ends,
        status="COOLING",
        note="Awaiting 888 Judge approval"
    )
```

---

## IV. MEMORY BAND ACCESS MATRIX

| Action | AAA | BBB | CCC |
|--------|-----|-----|-----|
| `seal` | ❌ | ✅ | ❌ |
| `read` | ❌ | ✅ | ✅ |
| `list` | ❌ | ✅ | ✅ |
| `write` | ❌ | ✅ | ❌ |
| `propose` | ❌ | ❌ | ⚖️ (Phoenix-72) |

**Legend:**
- ✅ Allowed
- ❌ Forbidden
- ⚖️ Requires Phoenix-72 protocol

---

## V. EUREKA ROUTING

### Verdict → Band Mapping

```python
EUREKA_ROUTES = {
    "SEAL": ("CCC", TTL.FOREVER),      # Perpetual canon
    "PARTIAL": ("BBB", TTL.DAYS_730),  # 2-year ledger
    "888_HOLD": ("BBB", TTL.DAYS_730), # Escalation archive
    "FLAG": ("BBB", TTL.DAYS_30),      # Warning memory
    "VOID": (None, TTL.NEVER),         # Not stored
    "SABAR": (None, TTL.NEVER),        # Not stored
}

def eureka_route(verdict: str) -> tuple[str, TTL]:
    """Route verdict to appropriate memory band."""
    return EUREKA_ROUTES.get(verdict, ("BBB", TTL.DAYS_30))
```

---

## VI. HASH CHAIN IMPLEMENTATION

### Chain Structure

```python
@dataclass
class ChainEntry:
    id: str           # SHA256(content + prev + timestamp)
    prev: str         # Previous entry hash
    timestamp: str    # ISO8601
    verdict: str      # SEAL, PARTIAL, etc.
    content: dict     # Proof payload
    merkle_root: str  # Tree root at this point
    signature: str    # Session signature

class HashChain:
    """Append-only hash chain for BBB ledger."""

    def __init__(self, ledger_path: Path):
        self.path = ledger_path
        self.head = self._load_head()

    def append(self, entry: ChainEntry) -> ChainEntry:
        """Append entry, linking to previous head."""
        entry.prev = self.head.id if self.head else "GENESIS"
        entry.id = self._compute_hash(entry)

        self._persist(entry)
        self.head = entry

        return entry

    def verify(self) -> bool:
        """Verify entire chain integrity."""
        entries = self._load_all()

        for i, entry in enumerate(entries[1:], 1):
            expected_prev = entries[i-1].id
            if entry.prev != expected_prev:
                return False

        return True
```

---

## VII. MERKLE TREE IMPLEMENTATION

### Tree Construction

```python
def compute_merkle_root(entries: list[dict]) -> str:
    """
    Compute Merkle root from entries.

    Structure:
              Root
             /    \
          H(0-1)  H(2-3)
          /   \    /   \
        H0    H1  H2    H3
    """
    if not entries:
        return sha256(b"EMPTY").hexdigest()

    # Hash leaves
    leaves = [sha256(json.dumps(e).encode()).hexdigest() for e in entries]

    # Pad to power of 2
    while len(leaves) & (len(leaves) - 1):
        leaves.append(leaves[-1])

    # Build tree
    while len(leaves) > 1:
        leaves = [
            sha256((leaves[i] + leaves[i+1]).encode()).hexdigest()
            for i in range(0, len(leaves), 2)
        ]

    return leaves[0]
```

---

## VIII. FLOOR ENFORCEMENT

### Pre-Operation Checks

```python
def check_vault_floors(action: str, proof: dict) -> FloorResult:
    """Check F1 and F8 before vault operations."""

    # F1: Amanah (Reversibility)
    if action in ["seal", "write"]:
        if not proof.get("audit_log"):
            return FloorResult(
                passed=False,
                floor="F1",
                reason="Audit log required for seal/write"
            )

    # F8: Tri-Witness (for seal)
    if action == "seal":
        tw = proof.get("TW", 0)
        if tw < 0.95:
            return FloorResult(
                passed=False,
                floor="F8",
                reason=f"TW={tw:.2f} < 0.95 threshold"
            )

    return FloorResult(passed=True)
```

---

## IX. INTEGRATION POINTS

### MCP Server Registration

```python
# In trinity_server.py
from arifos.mcp.tools.mcp_trinity import vault_999_handler

TRINITY_TOOLS = [
    # ... other tools ...
    MCPTool(
        name="999_vault",
        description="Constitutional memory seal",
        handler=vault_999_handler,
        input_schema=VAULT_INPUT_SCHEMA,
        output_schema=VAULT_OUTPUT_SCHEMA
    )
]
```

### Core Memory Connection

```python
# Bridge to core/memory/vault
from arifos.core.memory.vault.vault999 import Vault999
from arifos.core.memory.vault.vault_manager import VaultManager

class MCPVaultBridge:
    """Bridge between MCP tool and core vault."""

    def __init__(self):
        self.vault = Vault999()
        self.manager = VaultManager(self.vault)

    async def handle(self, action: str, params: dict) -> dict:
        """Route MCP action to core vault."""
        handlers = {
            "seal": self.manager.seal,
            "read": self.vault.read,
            "list": self.vault.list,
            "write": self.manager.write,
            "propose": self.manager.propose_amendment
        }

        return await handlers[action](**params)
```

---

## X. USAGE EXAMPLES

### Seal a Verdict

```python
# MCP call
result = await mcp_call("999_vault", {
    "action": "seal",
    "verdict": "SEAL",
    "proof": {
        "p_truth": 0.96,
        "TW": 0.98,
        "floor_results": {
            "F1": "PASS",
            "F2": "PASS",
            # ...
        },
        "content": "Implementation approved",
        "audit_log": True
    }
})

# Result
{
    "success": True,
    "merkle_root": "sha256:abc123...",
    "entry_id": "sha256:def456...",
    "band": "CCC",
    "timestamp": "2026-01-22T12:00:00+08:00"
}
```

### Read from Ledger

```python
result = await mcp_call("999_vault", {
    "action": "read",
    "band": "BBB",
    "entry_id": "sha256:def456..."
})
```

### Propose Amendment

```python
result = await mcp_call("999_vault", {
    "action": "propose",
    "amendment": {
        "floor": "F4",
        "field": "threshold",
        "old_value": 0.7,
        "new_value": 0.75,
        "rationale": "Increase empathy requirements"
    }
})

# Result
{
    "success": True,
    "proposal_id": "prop_001",
    "cooling_tier": 2,
    "cooling_ends": "2026-01-25T12:00:00+08:00",
    "status": "COOLING"
}
```

---

## XI. CANONICAL REFERENCES

| Component | Location |
|-----------|----------|
| **This Doc** | `000_THEORY/011_VAULT_MCP.md` |
| **VAULT999** | `VAULT999/README.md` |
| **MCP Trinity** | `arifos/mcp/tools/mcp_trinity.py` |
| **Vault Core** | `arifos/core/memory/vault/` |
| **Spec** | `arifos/spec/v47/999_vault/` |

---

**Version:** v50.5.15
**Status:** CANONICAL
**Authority:** Muhammad Arif bin Fazil

**DITEMPA BUKAN DIBERI** — Forged, Not Given.
