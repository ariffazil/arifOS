# Tool Lineage Injection Contract — Phase 2 Spec

> **Document Type:** Normative epistemic contract
> **Status:** Draft — pending Phase 1 stabilization
> **Scope:** All canonical tools across arifOS, GEOX, WEALTH, A-FORGE
> **Dependency:** JWT Auth Patch (Phase 1) MUST be stable before injection
> **Motto:** *What produced this verdict must be as immutable as the verdict itself.*

---

## 1. Purpose

Every tool invocation leaves an epistemic trace. Currently, VAULT seals record *who* and *when*, but not *what logic version* produced the seal. This contract makes the federation historically deterministic: any seal can be reconstructed to its exact tool version, schema, and runtime commit.

---

## 2. Lineage Envelope

Every tool result MUST include a `lineage` object:

```json
{
  "lineage": {
    "tool_id": "arif_judge_deliberate",
    "tool_version": "1.3.0",
    "schema_hash": "a3f7c2d9...",
    "git_commit_full": "45ea239044563e74f9c166f86784af3c807a1375",
    "git_commit_short": "45ea2390",
    "runtime_version": "2026.04.26-KANON",
    "claim_state": "JUDGED",
    "timestamp": "2026-04-26T09:54:14+00:00",
    "issuer": "arifOS"
  }
}
```

### Field Definitions

| Field | Source | Rule |
|-------|--------|------|
| `tool_id` | Tool function name / registry key | Canonical `arif_<noun>_<verb>` format |
| `tool_version` | `tool_registry_v2.json` | Semantic version. MUST bump on schema or logic change. |
| `schema_hash` | `sha256(tool_schema_json)` | Deterministic hash of input/output schema JSON. |
| `git_commit_full` | `git rev-parse HEAD` at deploy time | Full 40-character hash. Mandatory. |
| `git_commit_short` | `git rev-parse --short HEAD` at deploy time | Short hash. Optional convenience only. |
| `runtime_version` | `RuntimeEnvelope.version` | Global runtime tag (e.g. `2026.04.26-KANON`). |
| `claim_state` | Tool-specific epistemic tag | One of: `CLAIM`, `OBSERVED`, `COMPUTED`, `ESTIMATE`, `INFERRED`, `SIMULATED`, `JUDGED` |
| `timestamp` | `datetime.now(timezone.utc).isoformat()` | UTC ISO-8601 with offset. |
| `issuer` | Runtime package name | `"arifOS"`, `"GEOX"`, `"WEALTH"`, `"A-FORGE"` |

---

## 3. Schema Hash Rule

```python
import hashlib
import json

def compute_schema_hash(tool_schema: dict) -> str:
    """
    Deterministic SHA-256 of canonical JSON representation.
    Keys sorted. No whitespace. UTF-8.
    """
    canonical = json.dumps(tool_schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
```

**Properties:**
- Same schema → same hash across all runtimes
- Hash changes on: field name, field type, required/optional, enum values, description
- Hash does NOT change on: docstring, comments, formatting

**Storage:** `schema_hash` lives in `tool_registry_v2.json` alongside `tool_version`:

```json
{
  "wealth_evoi_compute": {
    "version": "1.0.0",
    "schema_hash": "a3f7c2d9e8b1d4f5",
    "last_updated": "2026-04-26",
    "schema": { ... }
  }
}
```

---

## 4. Injection Points

### 4.1 `_ok()` — Tool Success Path

Every tool that returns via `_ok()` MUST include lineage:

```python
def _ok(tool: str, result: Any, session_id: str | None = None) -> dict:
    lineage = _resolve_lineage(tool)
    return {
        "status": "success",
        "tool": tool,
        "result": result,
        "lineage": lineage,
        "session_id": session_id,
    }
```

### 4.2 `_arif_vault_seal()` — Ledger Write Path

Seal metadata MUST include lineage snapshot:

```python
seal_payload = {
    "payload": verdict,
    "lineage": lineage,           # ← injected here
    "actor_id": actor_id,
    "session_id": session_id,
    "constitutional_chain_id": chain_id,
    "judge_state_hash": judge_hash,
}
```

VAULT999 `outcomes.jsonl` entry:

```json
{
  "timestamp": "2026-04-26T09:54:14+00:00",
  "verdict": "SEAL",
  "lineage": {
    "tool_id": "arif_judge_deliberate",
    "tool_version": "1.3.0",
    "schema_hash": "a3f7c2d9...",
    "git_commit_full": "45ea239044563e74f9c166f86784af3c807a1375",
    "git_commit_short": "45ea2390",
    "runtime_version": "2026.04.26-KANON"
  },
  "actor_id": "Muhammad Arif bin Fazil",
  "session_id": "sess-001"
}
```

### 4.3 Cross-Repo Tools (GEOX, WEALTH, A-FORGE)

Each repo maintains its own `tool_registry.json` with version + schema_hash. When a tool is invoked via MCP bridge:

1. Originating repo injects its own lineage
2. Bridge forwards lineage in MCP metadata
3. Receiving repo MAY append its own lineage (multi-hop trace)

```json
{
  "lineage": [
    {"tool_id": "geox_prospect_evaluate", "tool_version": "2.1.0", "issuer": "GEOX"},
    {"tool_id": "arif_judge_deliberate", "tool_version": "1.3.0", "issuer": "arifOS"}
  ]
}
```

---

## 5. Version Bump Rules

`tool_version` MUST bump per semantic versioning when:

| Change | Bump |
|--------|------|
| Input schema changes (new field, type change, requiredness) | **MAJOR** |
| Output schema changes | **MAJOR** |
| Logic change affecting verdict/computation | **MINOR** |
| Performance optimization, no logic change | **PATCH** |
| Docstring, comment, formatting | **No bump** |

**Enforcement:** CI gate checks `tool_registry_v2.json` — if `schema_hash` changed but `version` did not bump, build fails.

---

## 6. ClaimState Standardization

All repos adopt a single canonical enum (defined in `arifos-types`):

```python
class ClaimState(str, Enum):
    CLAIM = "CLAIM"           # Direct assertion without evidence
    OBSERVED = "OBSERVED"     # Raw sensor/data input
    COMPUTED = "COMPUTED"     # Algorithmic derivation
    ESTIMATE = "ESTIMATE"     # Statistical/probabilistic
    INFERRED = "INFERRED"     # Model-based inference
    SIMULATED = "SIMULATED"   # Synthetic/model output
    JUDGED = "JUDGED"         # Constitutional deliberation
```

**GEOX migration:** Map existing 8+ local definitions to this canonical enum. Legacy values not in the canonical set become `INFERRED` with a deprecation note.

---

## 7. Registry Immutability

The registry snapshot used for lineage resolution must be **read-only at runtime**.

Rules:
- Load `tool_registry_v2.json` at boot into an in-memory frozen dict
- Refuse any runtime mutation attempt
- If registry changes on disk, restart required — hot-reload forbidden
- Hash of loaded registry logged at startup for audit

This prevents:
- Someone editing `tool_registry_v2.json` → schema hash changes retroactively
- Historical reconstruction breaking due to runtime drift

## 8. Implementation Order

**Blocked by:** JWT Auth Patch (Phase 1) must be stable.

1. **Step 1:** Add `version`, `schema_hash`, `schema` fields to `tool_registry_v2.json`
2. **Step 2:** Implement `_resolve_lineage(tool_id)` helper in `arifosmcp/runtime/tools.py`
3. **Step 3:** Inject lineage into `_ok()` and `_arif_vault_seal()`
4. **Step 4:** Update VAULT999 schema to accept `lineage` field
5. **Step 5:** Backfill historical seals with `"lineage": null` (do not fake data)
6. **Step 6:** Adopt `ClaimState` enum in GEOX, WEALTH, A-FORGE
7. **Step 7:** Add CI gate: schema_hash drift → version bump required

---

## 8. Rollback

- `lineage` field is additive — old consumers ignore it
- VAULT999 supports `"lineage": null` for pre-contract seals
- If rollback needed: remove injection from `_ok()` and `_arif_vault_seal()`; lineage field becomes null again
- No data migration required on rollback

---

## 9. Code Surface to Touch

| File | Change |
|------|--------|
| `arifosmcp/tool_registry_v2.json` | Add `version`, `schema_hash`, `schema` per tool |
| `arifosmcp/runtime/tools.py` | Add `_resolve_lineage()`; inject into `_ok()` and `_arif_vault_seal()` |
| `arifosmcp/constitutional_map.py` | Add `version` and `schema_hash` to `CANONICAL_TOOLS` |
| `packages/arifos-types/py/arifos_types/epistemic.py` | Define `ClaimState` enum |
| `packages/arifos-types/src/epistemic.ts` | TypeScript `ClaimState` enum |
| `A-FORGE/src/mcp/core.ts` | Forward lineage in MCP metadata |
| `geox/` | Migrate local ClaimTag definitions to canonical enum |
| `WEALTH/` | Adopt `ClaimState` in tool outputs |
| `tests/runtime/test_h2_h3_ratification.py` | Assert lineage present in seal output |

---

*Blocked on Phase 1. Do not implement until JWT Auth Patch is stable and sovereign ACK received.*
