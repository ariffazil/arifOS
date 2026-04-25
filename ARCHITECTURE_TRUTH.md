# arifOS Repository Architecture Truth Summary
## EPOCH-2026-04-25 · arifOS_bot audit

---

## A. What the repo actually is

**arifos** is a constitutional AI agent framework — governance-first, not capability-first.
The core claim is: LLM fluency + GEOX grounding + arifOS governance = governed intelligence.

**Three runtime surfaces:**
1. `arifos/` — the canonical constitutional kernel (tools, core/middleware, runtime/)
2. `arifosmcp/` — MCP server adapter (HTTP transport, tool dispatch, A2A)
3. `core/` — shared organs, kernel, enforcement, vault999 (used by both above)

**Main runtime path:**
```
MCP client → arifosmcp/server.py OR arifosmcp/unified_server.py
           → arifosmcp/runtime/ (ingress → governance → routing → tool dispatch)
           → arifos/tools/ (000-999 constitutional tools)
           → core/shared/floors.py (F1-F13 enforcement)
           → arifos/registry.py (tool lookup)
           → arifosmcp/contracts/ (envelope/verdict/identity schemas)
           → VAULT999 (append-only ledger)
```

**Control boundaries:**
- `arifosmcp/runtime/` — transport ingress, tool dispatch, session management
- `arifos/` — constitutional tools, governance kernel, registry
- `core/shared/floors.py` — authoritative F1-F13 floor enforcement
- `core/shared/` — shared types, physics, crypto, vault client
- `core/vault999/` — cryptographic audit trail

---

## B. What actually needs fixing

### B1. Duplication (source of truth fragmentation)

**1. `contracts/` exists at root AND inside `arifosmcp/contracts/`. Both have same filenames.**
- `arifosmcp/contracts/` is the copy. `contracts/` at root is canonical.
- Recommendation: make `arifosmcp/contracts/` an alias (import redirect), not a copy.

**2. `arifosmcp/core/` exists with governance_kernel.py + floors.py**
- `arifosmcp/core/` is a copy of the governance layer, slightly modified.
- Recommendation: `arifosmcp/` should import from `core/` or `arifos/core/`, not have its own.

**3. `arifosmcp/runtime/` is 55 files — single monolithic directory**
- This is the main MCP runtime engine. No duplication here.
- Recommendation: split into logical subdirs (`runtime/transport/`, `runtime/governance/`, `runtime/tools/`)

**4. `arifosmcp/agentzero/` vs `agentzero/` (root)**
- Root `agentzero/` is empty skeleton. Everything is in `arifosmcp/agentzero/`.
- Recommendation: delete root `agentzero/` once confirmed empty.

**5. `arifosmcp/apps/` vs `apps/` (root)**
- `apps/` at root has full implementations (judge_app.py 31KB, metabolic_monitor.py 49KB)
- `arifosmcp/apps/` has thin wrappers (most files <1KB) + duplicated thin copies
- Recommendation: `arifosmcp/apps/` → redirect imports to `../apps/`, delete duplicate skeleton

---

### B2. Naming inconsistencies

| File | Issue | Proposed |
|------|-------|----------|
| `arifosmcp/tools/fetch_tool.py` | Should be singular | `arifosmcp/tools/fetch.py` |
| `arifosmcp/tools/judge_deliberate.py` | Verb in name | `arifosmcp/tools/judge.py` |
| `arifosmcp/tools/mind_reason.py` | Verb in name | `arifosmcp/tools/reason.py` |
| `arifosmcp/tools/sense_observe.py` | Verb in name | `arifosmcp/tools/sense.py` |
| `arifosmcp/tools/ops_measure.py` | Verb in name | `arifosmcp/tools/ops.py` |
| `arifosmcp/tools/memory_recall.py` | Verb in name | `arifosmcp/tools/memory.py` |
| `arifosmcp/tools/vault_seal.py` | Verb in name | `arifosmcp/tools/vault.py` |
| `arifosmcp/tools/forge_execute.py` | Verb in name | `arifosmcp/tools/forge.py` |
| `arifosmcp/tools/session_init.py` | Verb in name | `arifosmcp/tools/session.py` |
| `arifosmcp/tools/gateway_connect.py` | Verb in name | `arifosmcp/tools/gateway.py` |
| `arifosmcp/tools/heart_critique.py` | Verb in name | `arifosmcp/tools/heart.py` |
| `arifosmcp/tools/kernel_route.py` | Verb in name | `arifosmcp/tools/kernel.py` |
| `arifosmcp/tools/lsp_tools.py` | Plural+tool | `arifosmcp/tools/lsp.py` |
| `arifosmcp/tools/registry.py` | Verb in name | `arifosmcp/tools/registry.py` (keep, it's a registry) |
| `arifosmcp/tools/base.py` | Generic | `arifosmcp/tools/base.py` (KEEP — tool base class) |
| `arifosmcp/tools/reply_compose.py` | Verb in name | `arifosmcp/tools/reply.py` |
| `arifosmcp/tools/evidence_fetch.py` | Verb in name | `arifosmcp/tools/evidence.py` |
| `arifosmcp/tools/reality_bridge.py` | Verb in name | `arifosmcp/tools/reality.py` |
| `arifosmcp/tools/architect_tools.py` | Plural+tool | `arifosmcp/tools/architect.py` |

**Plural-named singular files to normalize:**
- `arifosmcp/runtime/tool_specs.py` → `tool_spec.py`
- `arifosmcp/runtime/schemas.py` → `schema.py`
- `arifosmcp/runtime/models.py` → `model.py`
- `arifosmcp/runtime/sessions.py` → `session.py`
- `arifosmcp/runtime/resources.py` → `resource.py`
- `arifosmcp/runtime/prompts.py` → `prompt.py`
- `arifosmcp/runtime/floors.py` → `floor.py`
- `arifosmcp/runtime/mcp_utils.py` → `mcp_util.py`
- `arifosmcp/runtime/governance_identities.py` → `governance_identity.py`
- `arifosmcp/runtime/storage.py` → `storage.py` (keep — singular already)
- `arifosmcp/runtime/compat.py` → `compat.py` (keep — singular)

**Duplicate source-of-truth contracts:**
- `arifosmcp/contracts/` → redirect to `../../contracts/` (root canonical)
- `arifosmcp/core/` → redirect imports to `../../core/`

---

### B3. Mythical/decorative names in implementation

| Current | Proposed | Rationale |
|---------|----------|-----------|
| `arifOS_a2a.py` | `a2a.py` | "arifOS" is redundant — file is already in arifOS package |
| `arifOS_horizon_cli.py` | `horizon_cli.py` | Same |
| `arifos_http_adapter.py` | `http_adapter.py` | "arifos" redundant |
| `arifos_http_guard_proxy.py` | `guard_proxy.py` | Simplify |
| `arifOS_a2a.py` (root) | `a2a.py` | Same |
| `arifOS_a2a.py` (arifosmcp) | DELETE — exact duplicate | Same content |
| `capability_map.py` | `capability.py` | singular noun for map |
| `constitutional_map.py` | `constitution.py` | singular noun |

---

## C. Migration Plan

### Phase 1 — Safe aliasing (no deletions)
1. Create `arifosmcp/contracts/__init__.py` redirect to root `contracts/`
2. Create `arifosmcp/core/__init__.py` redirect to root `core/`
3. Delete empty `agentzero/` skeleton (root)
4. Create alias for duplicated `arifOS_a2a.py`

### Phase 2 — Rename singular files (import-safe)
1. Rename `arifosmcp/tools/*_*.py` → singular verbs stripped
2. Rename `arifosmcp/runtime/` plural files
3. Update all internal imports for renames

### Phase 3 — Merge duplicate contracts
1. Point `arifosmcp/contracts/` imports to root `contracts/`
2. Remove content copies from `arifosmcp/contracts/`

### Phase 4 — Split arifosmcp/runtime/ (optional — largest gain)
- Move files into subdirectories: `runtime/transport/`, `runtime/governance/`, `runtime/tools/`, `runtime/session/`

### Phase 5 — Push
- Branch: `cleanup/canonical-naming-v1`
- Commit per phase with clean messages

---

## D. Compatibility shim strategy
For every renamed file `foo.py` → `bar.py`:
1. Keep old file as import shim: `foo.py = "use bar.py"`
2. Add deprecation warning
3. After one sprint, remove shim

---

## E. Technical debt remaining after Phase 1-3
- `arifosmcp/runtime/` 55-file monolith (Phase 4)
- `arifosmcp/runtime/tools_internal.py` (63KB — largest file, needs split)
- `arifosmcp/runtime/tools_hardened_dispatch.py` (46KB)
- `arifosmcp/runtime/rest_routes.py` (125KB — largest single file)
- GEOX lives in `geox/` top-level but also in `archive/` (legacy divergence)
- `00_legacy_materials/` (562 files) — archived but not archived-to-cold-storage
