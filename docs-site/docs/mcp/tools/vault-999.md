---
sidebar_position: 5
title: vault_999
description: Immutable Seal & Governance IO
---

# vault_999

**Immutable Seal & Governance IO**

Commits the final decision to the immutable ledger with Merkle proofs.

## Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `action` | string | `"seal"` | Action to perform |
| `session_id` | string | `""` | Session identifier |
| `verdict` | string | `"SEAL"` | Verdict to seal |
| `target` | string | `"seal"` | Target operation |

## Actions

| Action | Description |
|--------|-------------|
| `seal` | Commit verdict to ledger (immutable) |
| `list` | View recent seals |
| `read` | Retrieve specific seal by ID |
| `write` | Store governance data |
| `propose` | Draft without committing |

## Memory Tiers

The VAULT999 system uses tiered memory:

| Tier | Age | Description |
|------|-----|-------------|
| **L0** | 0h | Hot session memory |
| **L1** | 24h | Daily cooling |
| **L2** | 72h | Phoenix cooling (truth stabilizes) |
| **L3** | 7d | Weekly reflection |
| **L4** | 30d | Monthly canon |
| **L5** | 365d+ | Constitutional law (immutable) |

## Returns

```json
{
  "status": "sealed",
  "seal_id": "seal-uuid-abc123",
  "merkle_root": "0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
  "timestamp": "2026-01-25T12:00:00Z",
  "memory_tier": "L0",
  "verdict": "SEAL"
}
```

## Example Usage

### Python

```python
from arifos.mcp.tools.mcp_trinity import mcp_999_vault

result = await mcp_999_vault(
    action="seal",
    session_id="abc123",
    verdict="SEAL"
)

print(f"Sealed: {result['seal_id']}")
print(f"Merkle Root: {result['merkle_root']}")
```

### MCP Call

```json
{
  "method": "tools/call",
  "params": {
    "name": "vault_999",
    "arguments": {
      "action": "seal",
      "session_id": "abc123",
      "verdict": "SEAL"
    }
  }
}
```

## Why Immutability?

The sealed ledger ensures:

1. **Audit Trail** — Every decision is recorded
2. **Accountability** — Cannot retroactively change verdicts
3. **Trust** — Users can verify governance was applied
4. **Cooling** — Truth stabilizes over time (Phoenix protocol)

## Phoenix Protocol (72h Cooling)

After 72 hours in the vault, a decision is considered "cooled" — the immediate emotional context has passed, and the truth of the decision can be evaluated more objectively.
