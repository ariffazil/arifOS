# CHANGELOG — arifOS Constitutional AI Kernel

All changes follow [T000 versioning](T000_VERSIONING.md): `YYYY.MM.DD-PHASE-STATE`.
**Creed:** DITEMPA BUKAN DIBERI — Forged, Not Given.

---

## [2026.3.22-INIT-ANCHOR-UNIFIED] — 2026-03-22 — INIT-ANCHOR-UNIFIED

**T000:** 2026.03.22-INIT-ANCHOR-UNIFIED  
**Theme:** The Ignition State of Intelligence — ONE tool for ALL constitutional session operations

### Forged

- **Unified `init_anchor` Mega-Tool** — The ONE entry point for Stage 000
  - Consolidated: `init_anchor`, `init_anchor_state`, `revoke_anchor_state`, `get_caller_status`
  - 5 modes: `init` | `state` | `status` | `revoke` | `refresh`
  - Single implementation in `init_anchor_impl` with mode dispatch
  - Fixed critical `kwargs` bug (line 166 undefined reference)

### Constitutional Enforcement

- **F11 (Command Authority)**: Identity canonicalization via "I'm Arif" semantic detection
- **F12 (Injection Defense)**: Payload sanitization integrated into unified dispatch
- **F13 (Sovereign Override)**: `human_approval` flag persistence across all modes

### Legacy Compatibility

- CAPABILITY_MAP routing preserved:
  - `init_anchor_state` → `init_anchor(mode="state")`
  - `revoke_anchor_state` → `init_anchor(mode="revoke")`
  - `get_caller_status` → `init_anchor(mode="status")`

### Artifacts

- `arifosmcp/runtime/tools.py` — Unified dispatch with kwargs fix
- `arifosmcp/runtime/tools_internal.py` — 5-mode implementation
- `arifosmcp/runtime/tool_specs.py` — Updated unified description
- `tests/test_init_unification.py` — NEW comprehensive test suite
- `INIT_ANCHOR_UNIFICATION_SUMMARY.md` — Architectural documentation

---

## [2026.3.14-NERVOUS-SYSTEM-9-FORGED] — 2026-03-14 — NERVOUS-SYSTEM-9-FORGED

**T000:** 2026.03.14-NERVOUS-SYSTEM-9-FORGED
**Theme:** ACLIP Infrastructure Hardening — 9-Sense Nervous System

### Added

- **Nervous System 9 — Hardened Internal Toolset:**
  - `system_health` (111_SENSE): Hardware telemetry with container awareness
  - `process_list` (111_SENSE): Process enumeration with filtering
  - `net_status` (111_SENSE): Network connectivity diagnostics
  - `chroma_query` (555_MEMORY): Vector memory with dual Qdrant API support
  - `arifos_list_resources` (999_VAULT): Namespaced resource enumeration
  - `arifos_read_resource` (999_VAULT): Namespaced asset retrieval
  - `log_tail` (111_SENSE): Smart log streaming with auto-path detection
  - `fs_inspect` (111_SENSE): Sandboxed filesystem inspection
  - `cost_estimator` (444_ROUTER): Thermodynamic (ΔS) cost projection

### Changed

- All 9 internal tools now return canonical `RuntimeEnvelope` objects
- All 9 tools accept `session_id` and `auth_context` for full governance
- All 9 tools subject to F11 (Command Auth) and F12 (Injection) floors
- All 9 operations sealed to VAULT999 immutable ledger
- `chroma_query` auto-detects Qdrant version (v1.7 legacy / v1.8+ modern)
- `list_resources` and `read_resource` namespaced as `arifos_*` to prevent MCP collisions

### Infrastructure

- `arifosmcp/intelligence/console_tools.py` — Consolidated 9-tool implementation
- `arifosmcp/intelligence/cli.py` — ACLIP-CAI server synchronization
- `arifosmcp/runtime/phase2_tools.py` — Registration alignment
- `arifosmcp/intelligence/tools/fs_inspector.py` — Added inspect_path alias
- `arifosmcp/intelligence/tools/net_monitor.py` — Added check_connectivity alias
- `arifosmcp/intelligence/tools/thermo_estimator.py` — Cost estimation engine

### Documentation

- `docs/architecture/NERVOUS_SYSTEM_9.md` — Complete architectural reference
- `docs/architecture/TOOL_INVENTORY.md` — Updated with all 39 tools (23 public + 9 machine + 7 deprecated)
- `arifosmcp/sites/developer/docs/tools.html` — Website updated with Machine Tools section
- Comprehensive deprecated tools section with migration guide

### Verification

- **42 comprehensive tests** added for internal tools
- **100% pass rate** on all 9 hardened tools (9/9 SEALED)
- **E2E constitutional compliance** verified

---

## [2026.3.8-APEX-METRICS-HARDENING-SEAL] — 2026-03-08 — APEX-METRICS-HARDENING-SEAL

**T000:** 2026.03.08-APEX-METRICS-HARDENING-SEAL  
**Theme:** APEX thermodynamic math hardening, dashboard runtime recovery, and deployment truth alignment

### Changed
- `arifosmcp/intelligence/core/thermo_budget.py` now caps entropy removal to the entropy baseline actually available in-session.
- `arifosmcp/sites/apex-dashboard/index.html` now posts `SystemCall` bodies for live polling and normalizes both thermo and telemetry envelopes into one UI schema.
- Dashboard rendering now uses canonical fields (`G_dagger`, `eta`, `C`) rather than stale aliases that only existed in older demo payloads.

### Fixed
- JSX inline CSS variable usage no longer throws before dashboard mount.
- Live APEX payloads from thermo snapshots no longer crash on missing `governed_score` / `intelligence_efficiency`.
- `eta` and `G_dagger` can no longer be inflated by cumulative `delta_s` exceeding the configured entropy baseline.

### Verification
- `pytest tests/aclip_cai/test_thermo.py -q` -> pass
- `pytest tests/core/test_outputs.py -q` -> pass

---

## [2026.2.27] — 2026-02-27 — FORGE-PROTOCOL-NEGOTIATION-CONSISTENCY-SEAL

**T000:** 2026.02.27-FORGE-PROTOCOL-NEGOTIATION-CONSISTENCY-SEAL  
**Theme:** MCP version negotiation hardening, canonical tool naming convergence, and docs/runtime alignment.

### Added
- Streamable HTTP protocol negotiation tests for supported, unsupported, and mismatch session flows.
- MCP method parity for `resources/list`, `resources/read`, `prompts/list`, and `prompts/get` in streamable transport.

### Changed
- Canonical tool names converged to `apex_judge` and `eureka_forge` across runtime/tests/docs.
- Streamable HTTP handshake now negotiates `protocolVersion` per session and enforces header consistency.
- Discovery metadata now publishes `protocolVersion` and `supportedProtocolVersions` in `server.json` and well-known routes.
- Intro/docs trademark messaging aligned: "DITEMPA, BUKAN DIBERI" + epistemic humility subtitle.
- Package/release versions aligned to `2026.2.27`.

### Verification
- `pytest tests/test_aaa_phase888_mcp_protocol_e2e.py -q` -> pass
- `pytest tests/test_aaa_mcp_contract.py -q` -> pass
- `pytest tests/test_aaa_mcp_constitutional.py -q` -> pass

---

## [2026.2.23-2] — 2026-02-23 — FORGE-APEX-OBJECTIVE-ALIGNMENT-PHASE2-SEAL

**T000:** 2026.02.23-FORGE-APEX-OBJECTIVE-ALIGNMENT-PHASE2-SEAL  
**Theme:** APEX objective nonstationarity governance + release truth alignment

### Added
- Deterministic self-audit metadata in core constitutional decorator/evaluator envelopes.
- Objective contract at 000 init with APEX axes (`akal`, `present`, `energy`, `exploration`).
- Objective lineage threading into pipeline provenance and VAULT999 seal payload.

### Changed
- APEX judge now evaluates objective drift and enforces nonstationary escalation:
  - drift >= threshold -> `SABAR`
  - drift >= hold threshold -> `888_HOLD`
- Phase-2 drift policy is now query-type aware (FACTUAL stricter than EXPLORATORY/TEST).
- `test_all_tools_live.py --ci` now uses `pytest-json-report` when available and no longer passes unsupported `--report-log`.
- README badges and release note block aligned with current workflow reality (`Live Tests` + `CI`).
- MCP live test validator now handles missing thermo snapshots safely and `vault_seal` returns top-level `status` compatibility for live-suite assertions.

### Why Tests Badge Was Failing
- `live_tests.yml` invokes `python test_all_tools_live.py --ci`.
- Runner previously injected unsupported `--report-log=test-results.json`, causing argparse failure before suite execution.

---

## [2026.2.23] — 2026-02-23 — FORGE-SSE-PRIMARY-CONTEXT-HARDENING-SEAL

**T000:** 2026.02.23-FORGE-SSE-PRIMARY-CONTEXT-HARDENING-SEAL  
**Theme:** Runtime truth alignment + MCP context hardening + docs/metadata reconciliation

### Added
- MCP resource contracts surfaced in unified server:
  - `arifos://templates/full-context`
  - `arifos://schemas/tooling`
- MCP orchestration prompts surfaced in unified server:
  - `arifos.prompt.trinity_forge`
  - `arifos.prompt.anchor_reason`
  - `arifos.prompt.audit_then_seal`

### Changed
- Runtime defaults reaffirmed as **SSE primary** with HTTP `/mcp` fallback and stdio optional local mode.
- `README.md` updated to reflect current tool/resource/prompt surface and live links.
- `AGENTS.md` updated with current runtime truth and transport guidance.
- `server.json` and `static/.well-known/mcp/server.json` updated to 2026.2.23 metadata and discovery links.
- `pyproject.toml` package version updated to `2026.2.23`; project URLs aligned to current endpoints.
- Requirements reconciled for FastMCP v3 parity (`arifosmcp.transport/requirements.txt` now matches runtime line).

### Hardened
- Unified tool handlers in `arifosmcp.transport/server.py` now include stronger session/auth continuity semantics:
  - deterministic F11 block envelope when `session_id` is missing downstream,
  - standardized envelope fields (`floors`, `truth`, `next_actions`) for recovery-oriented clients,
  - continuity context fields (`actor_id`, `auth_token`, `parent_session_id`, `auth_context`) on major stages.

---

## [2026.2.22-2] — 2026-02-22 — FORGE-PHOENIX-REBIRTH-INFRASTRUCTURE-SEAL

**T000:** 2026.02.22-FORGE-PHOENIX-REBIRTH-INFRASTRUCTURE-SEAL  
**Theme:** Phoenix Mode — Machine death and resurrection with full sovereignty preservation

### Added
- **Phoenix Kit** — Complete sovereignty exfiltration package (45K, 74 files) in `XXX/`:
  - `metabolic_memory/` — 2 Scars (3.4K constitutional audit trails from L2_PHOENIX)
  - `sovereign_secrets/` — `.env.master`, API keys, SSL certificates
  - `infrastructure_scars/` — Systemd services, Nginx configs, PostgreSQL/Redis setup
  - `ssl_certs/` — 3 domain certificates (agi, arifos, arifosmcp)
  - `rebirth_verify.sh` — Automated post-migration validation script
  - `PHOENIX_README.md` — Migration guide and checklist
- **Infrastructure Reconciliation** — Fixed nginx upstream ports (8080→8889) for REST bridge
- **DNS Reconciliation** — Added `console.arif-fazil.com` CNAME via Cloudflare API
- **Registry Proofs Verified** — All three MCP registry proofs aligned:
  - `server.json`: `io.github.ariffazil/arifos-mcp`
  - `README.md`: `<!-- mcp-name: io.github.ariffazil/arifos-mcp -->`
  - `Dockerfile`: `LABEL io.modelcontextprotocol.server.name="io.github.ariffazil/arifos-mcp"`

### Changed
- **docker-compose.vps.yml** — Changed from FastMCP HTTP to REST bridge (`python -m arifosmcp.transport rest`)
- **nginx_config/arifosmcp** — All REST endpoints now route to port 8889 (was 8080)
- **Health endpoint** — `/health` now served on port 8889 via REST bridge

### Fixed
- **503 Cloudflare Error** — Nginx was routing `/health` to wrong upstream port (8080 vs 8889)
- **Port mapping** — REST bridge (8889) and SSE (8888) now correctly exposed

---

## [2026.2.22] — 2026-02-22 — FORGE-INTELLIGENCE-KERNEL-UPGRADE-SEAL

**T000:** 2026.02.22-FORGE-INTELLIGENCE-KERNEL-UPGRADE-SEAL  
**Theme:** arifosmcp.intelligence re-architecture to 9-Sense Federation Hub

### Added
- **9-Sense Infrastructure Console** — `arifosmcp.intelligence` re-architected into a sensory kernel:
  - `core/lifecycle.py` — INIT/SABAR/HOLD/VOID state machine
  - `core/floor_audit.py` — F1-F13 runtime validation
  - `core/mcp_server.py` — 9 canonical system calls federation
  - `core/vault_logger.py` — Tri-Witness + VAULT999 integration
  - `core/thermo_budget.py` — Thermodynamic resource allocator
  - `core/federation.py` — Multi-agent coordination protocol
- **9 Canonical System Calls** — Standardized tool surface across federation hub:
  - `anchor`, `reason`, `integrate`, `respond`, `validate`, `align`, `forge`, `audit`, `seal`
- **Thermodynamic Governance** — Real-time enforcement of ΔS ≤ 0, P² ≥ 1.0, and Ω₀ ∈ [0.03, 0.05].

### Changed
- **L0 Kernel description** — Updated in `README.md`, `GEMINI.md`, and `AGENTS.md` to reflect the federation hub and sensory kernel.
- **Agent Guide** — `AGENTS.md` updated with official MCP protocol resource links.

---

## [2026.2.19] — 2026-02-19 — FORGE-CHATGPT-INTEGRATION-SEAL

**T000:** 2026.02.19-FORGE-CHATGPT-INTEGRATION-SEAL  
**Theme:** ChatGPT integration and tool annotations for read‑only operations

### Added
- **ChatGPT Deep Research compatibility** — Added `search` and `fetch` tools following FastMCP spec:
  - `search(query)` returns cached result IDs (URLs) using arifOS reality grounding
  - `fetch(id)` retrieves full cached record for ChatGPT analysis
- **Read‑only tool annotations** — Added `readOnlyHint=True` to all safe tools:
  - Container tools: `container_list`, `container_logs`, `sovereign_health`
  - ACLIP‑CAI tools: all 9 sensing/gating tools
  - ChatGPT tools: `search`, `fetch`
- **Tool count** — Now 17 MCP tools (10 pipeline + 5 container + 2 ChatGPT)

### Technical Details
- `search` uses `web_search_noapi` (Brave‑based) with 5‑minute caching
- `fetch` returns cached results; IDs are URLs from search
- Read‑only annotations allow ChatGPT Chat mode to skip confirmation prompts
- Deep Research mode automatically uses `search`/`fetch` when available

---

## [2026.2.18] — 2026-02-18 — FORGE-MCP-PROTOCOL-SEAL

**T000:** 2026.02.18-FORGE-MCP-PROTOCOL-SEAL  
**Theme:** Full MCP JSON-RPC protocol compliance for SSE transport

### Fixed
- **`/messages` endpoint** — Complete MCP JSON-RPC protocol implementation:
  - `initialize` — Returns protocolVersion, serverInfo, capabilities
  - `notifications/initialized` — Client acknowledgment (empty response)
  - `ping` — Keepalive method
  - `tools/list` — Returns full tool schemas with inputSchema
  - `tools/call` — Execute tools with proper JSON-RPC response format
- **Route ordering** — Moved catch-all `/{tool_name}` to END of route list to prevent
  intercepting `/sse` and `/messages` requests
- **POST /sse handling** — Now returns proper HTTP 405 (Method Not Allowed) instead of 404
- **FunctionTool calling** — Fixed `tools/call` to use `.fn` attribute for FastMCP FunctionTool
  objects (they are not directly callable)

### Technical Details
- Starlette routes now correctly ordered: specific routes first, catch-all last
- SSE endpoint accepts both GET (streaming) and POST (405 response)
- All MCP lifecycle methods return proper JSON-RPC 2.0 responses
- Tool schemas include full inputSchema with properties, required fields, and enums

---

## [2026.2.17] — 2026-02-17 — FORGE-VPS-SEAL

**T000:** 2026.02.17-FORGE-VPS-SEAL  
**Theme:** Infrastructure sovereignty + H1.1 Production Observability

### Added
- **H1.1 Production Observability** — `/health` now returns granular governance metrics:
  - `postgres.status` / `postgres.lag_ms` — VAULT999 ledger liveness
  - `redis.status` / `redis.version` — MindVault session cache liveness
  - `core_pipeline.verdict` — Live constitutional pipeline verdict on health check
  - `mcp_tools.tool_count` — Count of registered MCP tools
  - `memory.percent` / `memory.available` — Host memory pressure
- **Starlette lifespan context** in `arifosmcp.transport/rest.py` — health checks now register on
  application startup instead of requiring `main()` to be called
- `EnvironmentFile=/opt/arifos/.env` in systemd unit — secrets loaded securely from disk,
  not baked into service file

### Fixed
- `HealthMonitor.check_all` now merges dict return values from individual checks instead
  of discarding sub-fields (postgres lag, redis version, pipeline verdict were all silently lost)
- `HealthMonitor.status[name]` now correctly reflects `{"status": False}` dict results
  (previously `bool(dict)` was always `True`)
- `redis_client.get_redis_client` replaced brittle manual URL parser with `redis.from_url`
  — fixes crash on `redis://localhost:6379/0` (DB index `/0` broke `int(port_str)`)
- Postgres `permission denied for schema public` — granted `ALL ON SCHEMA public TO arifos`
- `monitoring.py` critical tool list updated to use MCP verb names (`anchor`, `reason`, …)
  instead of internal graph names (`init_gate`, `agi_sense`, …)
- `rest.py` missing stdlib imports (`datetime`, `asyncio`, `uvicorn`, `json`, `time`, `uuid`)
  that caused `NameError` on VPS startup after import refactor

### Changed
- **Deployment platform: Railway → Hostinger VPS** (primary)
  - `railway.toml` deleted
  - `docker-compose.railway-local.yml` → `docker-compose.yml`
  - `DEPLOYMENT.md` rewritten for VPS (systemd + nginx + certbot)
  - `arifosmcp.nginx.conf` rewritten: proxy to port 8080, SSE-safe (no buffering, `proxy_buffering off`)
  - `server.json` SSE URL updated: `arifos-production.up.railway.app` → `arifosmcp.arif-fazil.com`
- `pyproject.toml` URLs corrected: `aaamcp.arif-fazil.com` → `arifosmcp.arif-fazil.com`

### Infrastructure (VPS)
- Systemd service `arifos-mcp.service` — auto-start, `Restart=always`, `RestartSec=5`
- Nginx reverse proxy with SSL (Let's Encrypt) — `arifosmcp.arif-fazil.com`
- PostgreSQL 17 (native) + Redis 8.0.2 (native) — both healthy and connected

---

## [2026.2.15] — 2026-02-15 — FORGE-TRINITY-SEAL

**T000:** 2026.02.15-FORGE-TRINITY-SEAL  
**Theme:** Codebase consolidation + MCP schema alignment + T000 versioning

### Added
- `core/shared/sbert_floors.py` — SBERT-based semantic floor classifier for F5/F6/F9
  replacing keyword heuristics (H1.2 foundation); lazy-loads `all-MiniLM-L6-v2`
- `arifosmcp.transport/config/capability_modules.yaml` — migrated from `arifos/config/`
- `MCP_NAME_TO_REGISTRY` dict and `get_tool_by_mcp_name()` in `arifosmcp.transport/protocol/tool_registry.py`
- `MCP_TO_GRAPH` dict in `arifosmcp.transport/protocol/tool_graph.py`
- `trinity_forge` added to `server.json` (was implemented but missing from schema)
- `AGENTS.md` rewritten as focused 150-line agent guide for coding agents

### Removed
- `arifos/` — entire pre-v52 legacy package (no `__init__.py`, not importable, 3 dead files)
- `codebase/` — 82 files / 21,047 lines of dead code (agi/, asi/, apex/, init/, shared/, vault/)
  Runtime (`arifosmcp.transport/server.py`) was already importing 100% from `core/`
- `core/asi/` — single-file subdirectory; `sbert_floors.py` moved to `core/shared/`
- `build/` — stale setuptools artifact directory
- `railway.toml`, `docker-compose.railway-local.yml` (renamed)
- 6 test files archived to `tests/archive/` (depended on deleted `codebase/` / `arifos/` APIs)

### Fixed
- `server.json` floor descriptions now match actual `@constitutional_floor()` decorators
  (e.g. `align` was claiming F5+F6+F9 but decorator is only F9)
- `core/shared/floors.py` F8 Genius check removed stale `from codebase.floors.genius import`
  try/except; collapsed to the fallback path that was always running
- `pyproject.toml` stale `arifos*` / `codebase*` package discovery entries removed
- mypy overrides updated from `arifos.*` to `core.*`

### Changed
- `core/organs/_2_asi.py` import: `from core.asi.sbert_floors` → `from core.shared.sbert_floors`
- `arifosmcp.transport/server.py` capability YAML path: `../arifos/config/…` → `config/…` (local)

---

## [2026.1.26] — 2026-01-26 — LIVE-DASHBOARD-SEAL

**Theme:** Live governance metrics, dashboard integration, constitutional floor pass 13/13

### Added
- `LiveMetricsService` — real-time constitutional metrics from VAULT999 ledger
- Live τ (truth), κᵣ (empathy), Ψ (vitality), ΔS (clarity) computation
- `/metrics` (Prometheus) and `/api/governance-status` (JSON) endpoints serving live data with `calibration_mode` transparency

### Fixed
- Removed all static placeholder metrics (0.99, 0.98, 0.85)
- τ now computed from actual eval harness; Ω₀ from uncertainty engine

---

## [2026.1.24] — 2026-01-24 — UNIFIED-CORE-SEAL

**Theme:** AAA_MCP unified, pure bridge architecture

### Changed
- `arifosmcp.transport/` becomes pure transport adapter — all decision logic moved to `core/`
- `core/` established as the single decision kernel with no transport imports

---

## [2026.1.18] — 2026-01-18 — CONSTITUTIONAL-FORGE

**Theme:** 13 Constitutional Floors, Trinity Engines, MCP foundation

### Added
- 13 constitutional floors F1–F13 with hard/soft enforcement
- Trinity architecture (ΔΩΨ): AGI Mind, ASI Heart, APEX Soul
- 9-tool MCP pipeline: anchor → reason → integrate → respond → validate → align → forge → audit → seal
- VAULT999 immutable ledger with Merkle chaining
- `@constitutional_floor()` decorator for automatic floor enforcement

---

*Format: [T000 Date] — Date — PHASE-STATE | Full spec: T000_VERSIONING.md*
