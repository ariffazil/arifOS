## Skill Result: MCP-substrate-audit

**Repo:** `/root/arifOS` (`ariffazil/arifos`)  
**Role:** `kernel` (MCP/A2A constitutional substrate)  
**Audited:** 2026-07-01  

---

### Summary

The arifOS MCP/A2A substrate has drift between its advertised surface and its runtime reality. The source repo and the deployed runtime (`/opt/arifos/app`) are on different commits (`f7ef21c51` vs `b2801cdf`). Agent-card and server manifests give conflicting tool counts (7, 13, 17, 22, 48, 52). There are duplicate `arif_think` implementations, orphaned root-level tools, and stale `arifos.*` schema files that contradict the current `arif_*` namespace ruling. The canonical 7-tool facade is conceptually clean in `arifosmcp/runtime/public_surface.py`, but the wire surface is leaking diagnostics and legacy aliases.

---

### 1. Agent-Card / A2A Surface Drift

- [ ] Single source of truth — **NO**
- Findings:
  - `.well-known/agent-card.json` — schema `arifOS/agent-card/v2.0.0`, version `2026.07.01`, `capabilities.tools: 7`, `tools_count: 13`, `owned_mcp` lists 9 tools (includes `arif_fetch`, `arif_critique` which are not in the canonical 7).
  - `static/.well-known/agent.json` — schema `arifos-agent-manifest/v1`, version `2026.06.11-SSCT`, `tools_count: 13`. Older, different shape.
  - `static/.well-known/arifos.json` — version `2026.4.13`, `tools: 22`, contradicts the public-7 narrative.
  - `arifosmcp/sites/developer/.well-known/arifos.json` and `arifosmcp/static/.well-known/ai-plugin.json` — additional divergent copies.
- Impact: An MCP client discovering arifOS via different paths will see different capability claims.

### 2. MCP Server Manifest Drift

- [ ] Manifest matches runtime — **NO**
- Findings:
  - `.well-known/mcp/server.json` and `static/.well-known/mcp/server.json` are identical copies (redundant).
  - Both claim `"tools": { "count": 7 }` and `protocolVersion: 2025-11-25`.
  - Runtime `/health` reports `tools_exposed_via_mcp: 48` and `total_declared_tools: 58`.
  - Runtime `/mcp` GET advertises `tool_count: 52`.
- Impact: The public manifest under-reports the exposed surface by ~7×, violating the "one intent = one public tool" clarity contract.

### 3. Tool Registry vs Implementation

- [ ] Registry and handlers consistent — **PARTIAL**
- Findings:
  - `arifosmcp/tool_registry.json` declares 50 tools: 7 canonical + 43 diagnostic.
  - `arifosmcp/runtime/public_surface.py` defines `CANONICAL_7` correctly.
  - Duplicate `arif_think` handlers:
    - `arifosmcp/tools/reason.py:878` (canonical)
    - `arifosmcp/runtime/mind_reason.py:229`
    - `arifosmcp/runtime/mind_mcp.py:32`
  - `arif_act` is exposed as `arif_act` but implemented as `_arif_act` in `arifosmcp/runtime/tools.py` — name mangling risk.
  - Root `./tools/` contains 3 orphaned tools (`notion_tool.py`, `sovereignty_stamp.py`, `token_savings_calculator.py`) not referenced in any registry.
  - `arifosmcp/schema/registry/tools/` contains legacy schemas with `arifos.*` prefix (e.g., `arifos.init.json`), but the namespace ruling declares `arifos_*` BLOCKED and `arif_*` canonical.

### 4. Prompts / Resources

- [ ] Canonical prompts/resources registered — **YES, but bloated**
- Findings:
  - `arifosmcp/prompts/__init__.py` is 1,553 lines — contains long doctrine prose inside the runtime module. This bloats the MCP server startup and mixes canonical prompts with philosophical commentary.
  - `arifosmcp/resources/__init__.py` is clean and lists 16 canonical + 3 supplemental resources with URI scheme.
  - `docs/archive/prompts/` and `arifosmcp/prompts/_archive/` duplicate archived prompt variants.

### 5. Transport / Runtime Truth

- [ ] Source, manifest, and runtime aligned — **NO**
- Findings:
  - Git repo HEAD: `f7ef21c51`
  - Deployed runtime (`/opt/arifos/app`) HEAD: `b2801cdf` — **behind by multiple commits**.
  - Production runtime still has all runtime debris (`node_modules/`, `.venv/`, `dist/`, caches) because it is a separate deployment tree.
  - Empty `.gitmodules` exists in production too.
  - Health endpoint reports `release_name: v2026.05.05-SSCT`, `version: kanon-1bcf22d`, `git_commit: 1bcf22d` — none of which match the repo or deployment HEADs.
  - `/mcp` GET returns `tool_count: 52`; `/health` returns `tools_exposed_via_mcp: 48`; server.json says `count: 7`.

### 6. Deployment / Repo Boundary

- [ ] Repo is the source of deployed runtime — **YES, but stale**
- Findings:
  - Production is deployed from `/opt/arifos/app`, not directly from `/root/arifOS`.
  - The repo cleanup (deleted stub authority files, removed 6+ GB of debris) has not been propagated to `/opt/arifos/app`.
  - `deployment_marker: /opt/arifos/app/.git_commit` exists but points to `1bcf22d`, which differs from both repo and deployment HEADs.

---

## Recommendations

1. **Consolidate A2A agent cards into one file** — Pick either `.well-known/agent-card.json` (v2) or `static/.well-known/agent.json` (v1), update the other to redirect, and delete stale copies in `arifosmcp/static/` and `arifosmcp/sites/developer/`. — **HIGH** — Owner: AAA
2. **Make MCP server manifest truthful** — Either filter `tools/list` to exactly the canonical 7 (as advertised) or update `server.json` to declare the expanded/operator surface. Do not claim 7 while exposing 48. — **HIGH** — Owner: arifOS kernel
3. **Deduplicate `arif_think`** — Remove `arifosmcp/runtime/mind_reason.py` and `arifosmcp/runtime/mind_mcp.py` definitions if they are superseded by `arifosmcp/tools/reason.py`. If they serve different modes, rename them. — **MEDIUM** — Owner: A-FORGE
4. **Rename `_arif_act` or expose it cleanly** — The public tool name `arif_act` should map to a function named `arif_act`, not a private `_arif_act`. — **MEDIUM** — Owner: A-FORGE
5. **Purge legacy `arifos.*` schema files** — `arifosmcp/schema/registry/tools/` uses the blocked prefix. Migrate to `arif_*.json` or remove if superseded by `tool_registry.json`. — **MEDIUM** — Owner: A-FORGE
6. **Remove orphaned root tools** — `./tools/notion_tool.py`, `sovereignty_stamp.py`, `token_savings_calculator.py` are not registered; move to archive or register intentionally. — **LOW** — Owner: AAA
7. **Slim `arifosmcp/prompts/__init__.py`** — Move doctrine prose to `docs/` and keep the module as a thin registry of prompt handlers. — **LOW** — Owner: A-FORGE
8. **Redeploy from current repo HEAD** — Sync `/opt/arifos/app` to `/root/arifOS` `main` and clean its runtime debris, or establish a CI/CD pipeline so the deployed substrate matches the audited source. — **HIGH** — Owner: Ops / A-FORGE
9. **Automate substrate drift detection** — Add a CI check that compares `.well-known/mcp/server.json` tool count with `tools/list` from a running instance. — **MEDIUM** — Owner: A-AUDIT

---

## Escalations

- **Deployment drift** — The running MCP kernel is behind the repo and advertises a different tool surface than it exposes. This is a federation-wide substrate integrity issue.
- **Manifest falsehood** — Claiming 7 tools while exposing 48 breaks the F4 CLARITY contract and could mislead MCP clients about the actual authority surface.

---

*MCP-substrate audit produced 2026-07-01. No files modified.*
