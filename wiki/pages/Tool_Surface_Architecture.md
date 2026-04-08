---
type: Concept
tags: [architecture, tools, contracts, generation, compatibility, drift]
sources: [tool_specs.py, tools.py, tools_hardened_dispatch.py, __main__.py, server.py, rest_routes.py, resources.py, public_registry.py, tool_registry.json]
last_sync: 2026-04-08
confidence: 0.94
---

# Tool Surface Architecture

`arifosmcp/runtime/tool_specs.py` is the best current candidate for **canonical tool truth** inside arifOS. Every other tool surface should either execute that contract, adapt older callers to it, or render it outward to transports and docs.

## Canonical Surface

| Tool | Stage | Layer |
| :--- | :--- | :--- |
| `arifos_init` | 000 | GOVERNANCE |
| `arifos_sense` | 111 | MACHINE |
| `arifos_mind` | 333 | INTELLIGENCE |
| `arifos_route` | 444 | GOVERNANCE |
| `arifos_heart` | 666 | INTELLIGENCE |
| `arifos_ops` | 777 | MACHINE |
| `arifos_judge` | 888 | GOVERNANCE |
| `arifos_memory` | 555 | INTELLIGENCE |
| `arifos_vault` | 999 | GOVERNANCE |
| `arifos_forge` | 010 | EXECUTION |
| `arifos_vps_monitor` | 111 | MACHINE |

## Current Surface Layers

### 1. Canonical Contract

- `arifosmcp/runtime/tool_specs.py`
- Defines canonical ids, count, schemas, and migration aliases.

### 2. Runtime Execution Surface

- `arifosmcp/runtime/tools.py`
- `arifosmcp/runtime/__main__.py`
- `arifosmcp/runtime/kernel_router.py`
- These files dispatch or select runtime tools directly.

### 3. Compatibility Surface

- `arifosmcp/runtime/tools_hardened_dispatch.py`
- `arifosmcp/runtime/megaTools/__init__.py`
- `arifosmcp/runtime/compatibility/memory_backend.py`
- `arifosmcp/runtime/compatibility/vault_backend.py`
- These files preserve older names or route legacy flows into the canonical runtime.

### 4. Transport / Registry Surface

- `arifosmcp/runtime/server.py`
- `arifosmcp/runtime/rest_routes.py`
- `arifosmcp/runtime/resources.py`
- `arifosmcp/runtime/public_registry.py`
- `arifosmcp/tool_registry.json`
- These files expose tool names to REST, MCP, discovery manifests, or resource documents.

### 5. Wiki / Narrative Surface

- `wiki/pages/MCP_Tools.md`
- `wiki/index.md`
- audit and concept pages that describe the tool surface

## Structural Law

The stable target architecture is:

`tool_specs.py` → runtime handlers / compatibility adapter → generated transport surfaces → generated wiki inventory

Under this model:

- concept pages remain narrative
- inventory pages remain derivative
- compatibility stays explicit and temporary

## 888_HOLD

The following are governance-sensitive and should not be deleted in this pass:

- legacy mega-tool namespace
- dotted-name compatibility paths
- old registry manifests consumed by unknown clients

They should first be isolated behind one compatibility adapter and checked by drift automation.
