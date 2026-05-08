# NODE_SPEC — WEALTH Node Runtime Specification

> **Version:** v1.0.0-canonical  
> **Status:** Implementation Spec  
> **DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## 1. Definition

A **WEALTH node** is the minimal executable unit that can:
1. Receive a proposed capital operation,
2. Run F1-F13 floor checks,
3. Compute financial and dignity metrics,
4. Issue or block a 999_SEAL,
5. Emit immutable telemetry to VAULT999,
6. Expose a queryable MCP interface.

A node may be personal (individual), institutional (SME/NGO), or federated (multi-node). All nodes share the same kernel logic.

---

## 2. Variables

| Variable | Type | Description |
|----------|------|-------------|
| node_id | UUID | Unique node identifier |
| node_tier | enum | personal, institutional, federation |
| runtime_version | semver | Node software version |
| vault_path | path | Absolute path to VAULT999 JSONL |
| config_path | path | Path to node configuration |
| mcp_enabled | boolean | Whether MCP stdio server is active |
| last_seal_epoch | ISO8601 | Timestamp of most recent 999_SEAL |
| seal_count | integer | Total seals issued |
| hold_count | integer | Total holds triggered |
| void_count | integer | Total voids issued |

---

## 3. Invariants

1. **VAULT999 immutability:** Records are append-only. No mutation or deletion permitted.
2. **Floor check precedence:** No seal may be issued without a current `checkFloors()` pass.
3. **Local-first default:** Financial data must not leave the node without explicit user_consent (F8).
4. **MCP safety:** MCP tools do not bypass floor logic. They are thin wrappers over kernel functions.
5. **Version compatibility:** Nodes running different `runtime_version` must resolve to the same floor verdicts for identical inputs.

---

## 4. State Transitions

### Node Boot

```
OFFLINE
→ Load config
→ Initialize VAULT999
→ Check runtime integrity
→ ONLINE (idle)
```

### Operation Processing

```
ONLINE
→ Receive operation
→ checkFloors()
→ If VOID: log, return void
→ If 888_HOLD: stage hold, log, return hold
→ Compute domain logic (networth, cashflow, capitalx)
→ seal999()
→ If SEALED: append VAULT999, emit telemetry
→ If 888-HOLD: append VAULT999, block execution
→ Return result
```

### MCP Query

```
ONLINE
→ MCP host requests tool/resource
→ Route to kernel/wealth function
→ Run governance checks if operation is stateful
→ Return JSON result
→ Log invocation to VAULT999 (capitalx, seal, floor checks only)
```

### Failure Recovery

```
ONLINE
→ Crash or corruption detected
→ Enter DEGRADED mode
→ Replay VAULT999 from tail
→ Validate last seal integrity hash
→ If valid: return ONLINE
→ If invalid: enter LOCKDOWN (human intervention required)
```

---

## 5. Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| **Vault corruption** | JSONL line unreadable | Skip corrupt line, flag in telemetry, require human review if >1% loss |
| **Runtime downgrade** | Older version accepts overrides newer blocks | Version gate: reject operations if runtime_version < minimum_spec |
| **MCP bypass attempt** | Host sends malformed schema to evade floor check | Zod strict validation; reject unknown properties |
| **Config drift** | Node config modified without seal | Hash config at boot; compare against last sealed config hash |
| **Network exfiltration** | Local data leaves node without consent | F8 block on external_sync without user_consent; OS-level firewall rule optional |
| **Entropy fatigue** | Node accepts operations with marginally passing floors until systemic risk accumulates | Rolling window ΔS tracker; trigger SABAR if 3 consecutive operations have ΔS > -0.01 |
| **Federation desync** | Multi-node consensus drifts | Cross-node seal hash comparison; majority witness rule |

---
*NODE_SPEC v1.0.0-canonical | 999 SEAL ALIVE*
