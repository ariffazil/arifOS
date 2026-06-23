# ADR-013: Naming Geometry — Kernel (2-term dot) vs A-FORGE (3-term underscore)

**Status:** RATIFIED  
**Date:** 2026-06-23  
**Sovereign:** Arif (F13)  
**Forge session:** Kimi Code audit / arifOS Federation  
**Supersedes:** Implicit naming conventions in `tool_spec.py`, `alias_shim.py`, and `CANONICAL13_MIGRATION.md`  
**Related:** ADR-009 (Compiler SSOT), `CANONICAL13_MIGRATION.md`, `A-FORGE/docs/MCP_TOOL_CATALOG.md`

---

## Context

The federation now runs three overlapping tool-naming geometries:

1. **2-term underscore (`arifos_init`, `arifos_sense`)** — early kernel spec in `tool_spec.py`.
2. **3-term underscore (`arif_session_init`, `arif_sense_observe`)** — the current live MCP surface (Phase 1 enforcement).
3. **2-term dot (`arif.session`, `arif.observe`)** — the target canonical13 surface documented in `CANONICAL13_MIGRATION.md`.

A-FORGE, meanwhile, has settled on a mixed surface dominated by **3-term underscore** (`forge_filesystem_read`) with some 2-term leaks (`forge_pipeline`, `forge_research`) and verb-first exceptions (`request_amanah_lock`).

This drift creates three problems:
- **Cognitive load:** Agents cannot infer authority from the name alone.
- **Surface bloat:** The live kernel exposes far more than 13 conceptual tools.
- **Governance misalignment:** Tool names no longer map 1:1 to constitutional axes (000_INIT → 999_VAULT).

## Decision

Establish a **dual-geometry naming law**:

| Layer | Geometry | Example | Rationale |
|-------|----------|---------|-----------|
| **arifOS kernel (brain)** | **2-term dot** | `arif.judge` | One name = one constitutional axis. Action is selected by `mode`. |
| **A-FORGE actuator (hands)** | **3-term underscore** | `forge_filesystem_read` | One name = one operational capability. Verb suffix makes execution intent explicit. |

### Why 2-term dot for the kernel

The kernel is a **governance coordinate system**, not a capability catalog. Its tools should name *lanes of authority*, not specific maneuvers:

- `arif.session` → 000_INIT
- `arif.observe` → 111_SENSE / 222_EVIDENCE
- `arif.reason` → 333_REASON / 444_CRITIQUE
- `arif.reply` → 444r_REPLY
- `arif.route` → 555_ROUTE
- `arif.memory` → 555m_MEMORY
- `arif.forge` → 666_FORGE
- `arif.judge` → 888_JUDGE
- `arif.vault` → 999_VAULT
- `arif.attest` → organ attestation
- `arif.shadow` → institutional-shadow audit
- `arif.ops` → health / vitals / probes

The verb is moved into `mode` because the constitutional stage is the invariant; the maneuver is a parameter.

### Why 3-term underscore for A-FORGE

A-FORGE is an **execution catalog**. Agents need to know *what* is being acted on and *what action* is taken:

- `forge_filesystem_read` — reads files
- `forge_git_commit` — commits code
- `forge_browser_navigate` — drives a browser
- `forge_lease_request` — requests a lease

The extra term prevents collision across domains (filesystem vs git vs docker) and makes the tool self-describing without requiring a `mode` lookup.

## Geometric intelligence score

| Dimension | 2-term dot (kernel) | 3-term underscore (A-FORGE) |
|-----------|:-------------------:|:---------------------------:|
| Orthogonality | 9/10 | 7/10 |
| Compression | 9/10 | 5/10 |
| Discoverability | 6/10 | 9/10 |
| Extensibility | 8/10 | 6/10 |
| Governance alignment | 10/10 | 5/10 |
| **Overall** | **8.4** | **6.4** |

The kernel optimizes for **law and orthogonality**; A-FORGE optimizes for **operability and self-description**.

## Migration plan

### Phase 1 — COMPLETE
Current live surface uses 3-term underscore names (`arif_session_init`, `arif_judge_deliberate`, etc.).

### Phase 2 — IN PROGRESS
1. Register **2-term dot aliases** (`arif.session`, `arif.observe`, etc.) on both HTTP and stdio transports.
2. Keep 3-term names **callable** but hide them from `tools/list` over time.
3. Update `CANONICAL13_MIGRATION.md` alias tables to include dot → 3-term mappings.
4. Update client configs (`.mcp.json`, `.kimi/mcp.json`, etc.) to prefer dot names where supported.

### Phase 3 — TARGET 2026-09-01
1. Remove 3-term aliases from public discovery.
2. Make 2-term dot the only names returned by `tools/list`.
3. Keep 3-term aliases callable for backward compatibility until 2026-12-31.

## Runtime implementation

### stdio path (`arifosmcp/runtime/__main__.py`)
Add dot aliases to `LEGACY_NAME_MAP` imported from `tool_spec.py`:

```python
"arif.session": "arif_session_init",
"arif.observe": "arif_sense_observe",
"arif.reason": "arif_mind_reason",
"arif.judge": "arif_judge_deliberate",
"arif.vault": "arif_vault_seal",
# ... (full table in CANONICAL13_MIGRATION.md)
```

### HTTP path (`arifosmcp/server.py`)
Extend `alias_shim.register_new_canonical_tools` or add a parallel `register_dot_aliases` call to register `arif.*` names that dispatch to the same handlers as the 2-term underscore aliases.

## Consequences

### Positive
- Names now encode constitutional topology (kernel) or operational capability (A-FORGE).
- Reduces surface bloat on the kernel from dozens of tools to 13 axes.
- Preserves separation of powers: `arif.judge` is unambiguously authoritative; `forge_*` is unambiguously executory.

### Negative
- Requires dual-mode alias maintenance during Phase 2.
- Clients must update tool names or rely on aliases.
- Documentation must remain consistent across `AGENTS.md`, `CANONICAL13_MIGRATION.md`, and `MCP_TOOL_CATALOG.md`.

### Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Dot names break clients that only allow underscores | Keep 3-term aliases callable through 2026-12-31. |
| Alias map drifts from canonical spec | Source aliases from `contracts/tools.yaml` (ADR-009 SSOT) and compile them. |
| A-FORGE copies kernel naming | Enforce 3-term rule in A-FORGE PR review; add lint check. |

## Success criteria

- [ ] `arif.*` dot aliases registered on both stdio and HTTP transports.
- [ ] `tools/list` in canonical13 mode returns only 13 dot-named kernel tools.
- [ ] A-FORGE catalog documents the brain/hands naming separation.
- [ ] CI enforces: kernel tools ≤13 public names; A-FORGE tools follow `forge_domain_action` or approved exceptions.

---

*DITEMPA BUKAN DIBERI — Kernel = 2-term law. Hands = 3-term craft.*
