# vault_query Tool Specification

**Version:** v1.0 (Proposed)  
**Status:** DRAFT — Pending Implementation  
**Purpose:** Enable institutional memory retrieval from vault_seal entries

---

## Overview

The `vault_query` tool enables searching and retrieving past constitutional decisions from the VAULT999 ledger. This transforms vault_seal from write-only audit to searchable institutional memory.

---

## Tool Definition

```python
@mcp.tool()
@constitutional_floor("F1", "F2")
async def vault_query(
    session_pattern: Optional[str] = None,
    verdict: Optional[str] = None,
    floor_violated: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 10,
    include_payload: bool = False
) -> dict:
    """Query past vault_seal entries for institutional memory retrieval.
    
    Search the constitutional ledger for past decisions, violations, and patterns.
    Use this to learn from history and maintain institutional continuity.
    
    Pipeline position: Auxiliary (can be called anytime)
    Floors enforced: F1 (Amanah), F2 (Truth)
    
    Args:
        session_pattern: Glob pattern for session_id (e.g., "test_*", "*2026-02*")
        verdict: Filter by verdict type (SEAL, VOID, PARTIAL, SABAR)
        floor_violated: Filter by floor that failed (e.g., "F9", "F12")
        date_from: ISO date string for range start (e.g., "2026-02-01")
        date_to: ISO date string for range end
        limit: Maximum entries to return (default 10, max 100)
        include_payload: Include full payload data (default False for efficiency)
    
    Returns:
        Dict with:
        - count: Number of matching entries
        - entries: List of matching vault entries
        - patterns: Detected patterns across results (if count > 5)
    """
```

---

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "session_pattern": {
      "type": "string",
      "description": "Glob pattern for session_id matching"
    },
    "verdict": {
      "type": "string",
      "enum": ["SEAL", "VOID", "PARTIAL", "SABAR"],
      "description": "Filter by verdict type"
    },
    "floor_violated": {
      "type": "string",
      "description": "Filter by floor that failed (F1-F13)"
    },
    "date_from": {
      "type": "string",
      "format": "date",
      "description": "ISO date for range start"
    },
    "date_to": {
      "type": "string", 
      "format": "date",
      "description": "ISO date for range end"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 10
    },
    "include_payload": {
      "type": "boolean",
      "default": false
    }
  }
}
```

---

## Output Format

```json
{
  "count": 42,
  "query": {
    "verdict": "VOID",
    "date_range": ["2026-02-01", "2026-02-07"]
  },
  "entries": [
    {
      "session_id": "sess_001",
      "timestamp": "2026-02-05T14:30:00Z",
      "verdict": "VOID",
      "floors_violated": ["F9"],
      "summary": "Blocked consciousness claim",
      "entry_hash": "abc123...",
      "payload": { ... }  // Only if include_payload=true
    }
  ],
  "patterns": {
    "most_common_violation": "F9",
    "void_rate": 0.15,
    "peak_hour": 14
  },
  "motto": "DITEMPA BUKAN DIBERI 💎🔥🧠",
  "floors_enforced": ["F1", "F2"]
}
```

---

## Example Calls

### Find all VOID verdicts this week

```bash
mcporter call arifos.vault_query \
  verdict=VOID \
  date_from=2026-02-01 \
  limit=20
```

### Find F12 injection attempts

```bash
mcporter call arifos.vault_query \
  floor_violated=F12 \
  limit=50
```

### Search by session pattern

```bash
mcporter call arifos.vault_query \
  session_pattern="prod_*" \
  include_payload=true
```

### Full audit for date range

```bash
mcporter call arifos.vault_query \
  date_from=2026-01-01 \
  date_to=2026-02-07 \
  limit=100
```

---

## Implementation Notes

### Storage Backend

The vault_seal currently writes to the hardened ledger at:
```python
from codebase.vault.persistent_ledger_hardened import get_hardened_vault_ledger
```

vault_query needs read access to this same ledger with index support.

### Required Indices

For efficient querying, add indices on:
- `session_id` (text search)
- `verdict` (enum)
- `timestamp` (datetime range)
- `floors_violated` (array contains)

### Pattern Detection

When `count > 5`, compute:
- Most common floor violation
- VOID rate (void_count / total_count)
- Time patterns (peak hours, weekdays vs weekends)
- Session clustering (similar session_ids)

---

## Constitutional Constraints

- **F1 Amanah:** Query results are read-only; cannot modify ledger
- **F2 Truth:** Results must be accurate; no sampling or approximation
- **Rate Limit:** Max 10 queries per minute per session
- **Payload Access:** Full payload requires elevated authority

---

## Integration with Emergence

### 1. Learning from Past Decisions

Agents can query past VOID verdicts to understand what was blocked and why:

```python
# Before similar action, check history
past_voids = await vault_query(floor_violated="F1", limit=5)
if similar_to_current(past_voids):
    # Adjust approach
```

### 2. Institutional Memory

Cross-session learning becomes possible:

```python
# New session can learn from old sessions
past_patterns = await vault_query(session_pattern="*", limit=100)
inject_context(past_patterns["patterns"])
```

### 3. Audit & Compliance

Generate compliance reports:

```python
# Monthly audit
monthly = await vault_query(
    date_from="2026-01-01",
    date_to="2026-01-31",
    limit=100,
    include_payload=True
)
generate_report(monthly)
```

---

## Next Steps

1. **Implement in server.py** — Add vault_query tool
2. **Add indices to ledger** — For efficient querying
3. **Test with real data** — Validate query patterns
4. **Document in OpenClaw guide** — Update OPENCLAW_AAA_MCP_GUIDE.md

---

*DITEMPA BUKAN DIBERI* 🔥
