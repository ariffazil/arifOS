# L4_MCP — Black-box Constitutional Authority via Single Tool

**Canonical truth:** This MCP server exposes exactly **ONE** tool: `apex.verdict`

All governance (Floors F1–F9, W@W weighting, 000→999 routing, cooling ledger)
runs **internally and is NOT directly callable**.

## Architecture

```
External (MCP boundary):
  └── apex.verdict(task, context) → {verdict, reasons, evidence, constraints}

Internal (hidden):
  ├── Floors (F1–F9, parallel evaluation)
  ├── W@W Weighting (confidence metrics)
  ├── 000→999 Pipeline (routing logic)
  └── cooling_ledger (append-only audit log)
```

## Security Invariants

- ✓ **Fail-closed** — Ledger down → VOID (no unaudited approvals)
- ✓ **Atomic** — One call → one verdict (all-or-nothing)
- ✓ **Non-bypassable** — Internal steps not exposed
- ✓ **Single authority** — Only `apex.verdict` decides
- ✓ **Auditable** — Every decision logged with ledger ID

## Usage

### Python API

```python
from L4_MCP.apex.schema import ApexRequest
from L4_MCP.apex.verdict import apex_verdict
from arifos_ledger.sqlite_store import SQLiteLedgerStore

ledger = SQLiteLedgerStore()
req = ApexRequest(task="read file", params={"path": "README.md"}, context={})
resp = apex_verdict(req, ledger)

print(resp.verdict)        # SEAL, VOID, SABAR, or HOLD_888
print(resp.explanation)    # Human-readable explanation
print(resp.cooling_ledger_id)  # Audit trail ID
```

### MCP Server (stdio)

```bash
python -m L4_MCP.server
```

### MCP Server (HTTP)

```bash
python -m L4_MCP.server --http 8000
```

## Floor Semantics (Canonical)

| Floor | Name | Threshold |
|-------|------|-----------|
| F1 | Amanah (Trust) | No harm, reversible |
| F2 | Truth | ≥0.99 confidence |
| F3 | Tri-Witness | 3-source verification |
| F4 | Clarity (ΔS) | Entropy reduction |
| F5 | Peace² | Non-destructive |
| F6 | κᵣ (Empathy) | Audience-appropriate |
| F7 | Ω₀ (Humility) | 0.03-0.05 band |
| F8 | Genius (G) | ≥0.80 |
| F9 | Anti-Hantu | No soul claims |

## Layer Relationship

```
L1_THEORY (Canon) → L2_GOVERNANCE (Specs) → L4_MCP (Authority)
                                              ↓
                                        arifos_ledger (Shared)
                                              ↑
                                    arifos_core/mcp (Glass-box)
```

## Status

- ✅ Blueprint complete
- ✅ Schema locked (ApexRequest, ApexResponse)
- ✅ apex.verdict function defined
- ✅ Floors F1-F9 stubs with canonical semantics
- ✅ Fail-closed ledger enforcement
- ✅ MCP SDK integration ready

---

**DITEMPA, BUKAN DIBERI** ✓
