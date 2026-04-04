# Changelog

All notable changes to arifOS are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Motto:** DITEMPA BUKAN DIBERI — Forged, Not Given

---

## [2026.3.6-CANON] — 2026-03-06

### Highlights

- **Canonical 13-Tool Surface Locked**: Sacred count enforced by runtime assertion in `aaa_mcp/protocol/aaa_contract.py`. 13 exactly — no more, no less.
- **Phoenix (recall_memory) Retired**: Replaced by `vector_memory` (BGE-M3 768-dim multilingual embeddings + Qdrant + EUREKA sieve). F9 Anti-Hantu compliant.
- **Three-Layer Schema Alignment**: `schemas.py` (JSON Schema) + `contracts.py` (Python runtime guards) + prompts now all agree on Gen3 canonical tool names.
- **ARIF Bands Documented**: A (Anchor) / R (Reflect) / I (Integrate) / F (Forge) / O (Orchestrate) taxonomy written into `333_APPS/L4_TOOLS/README.md` and root `README.md`.
- **L0 Kernel Prompt Aligned**: `l0_kernel_prompt.py` updated — stale `sensory_read` replaced with canonical `ingest_evidence`.

### Added

- `ingest_evidence` + `metabolic_loop` JSON schemas in `aaa_mcp/protocol/schemas.py` (TOOL_INPUT_SCHEMAS + TOOL_OUTPUT_SCHEMAS)
- `metabolic_loop` Python contract in `arifos_aaa_mcp/contracts.py`
- `vector_memory`, `ingest_evidence`, `metabolic_loop` entries in `aaa_mcp/protocol/tool_naming.py`

### Changed

- `arifos_aaa_mcp/contracts.py`: `REQUIRES_SESSION` — `recall_memory` → `vector_memory` (session guard now correctly targets the canonical tool)
- `arifos_aaa_mcp/server.py`: All 4 MCP prompts updated to Gen3 canonical names — `anchor_session`, `reason_mind`, `vector_memory`, `apex_judge`, `seal_vault`; Amanah Handshake (`governance_token`) documented in `audit_then_seal` prompt
- `aaa_mcp/server.py`: Error message updated — `init_session (anchor)` → `anchor_session`
- `aaa_mcp/protocol/l0_kernel_prompt.py`: `sensory_read` → `ingest_evidence`
- `aaa_mcp/README.md`, `docs/00_META/GEMINI.md`: Gen3 canonical names throughout; 11 → 13 tool count

### Removed

- **Archived from public surface**: `recall_memory` (→ `vector_memory`), `fetch_content` (→ `ingest_evidence` url), `inspect_file` (→ `ingest_evidence` file), `trinity_forge` (internal alias only), `query_openclaw` (internal diagnostic)
- Temp artifacts: `debug_mcp_v2.py`, `finalize_seal.py`, `verify_audit.py`, `git_diff_server.txt`

### Fixed

- `contracts.py` REQUIRES_SESSION had `recall_memory` instead of `vector_memory` — `vector_memory` calls were bypassing session validation

**Verdict:** SEAL — F9 (Anti-Hantu) + F4 (Clarity) + F1 (Amanah assertion) all pass. 13-tool surface is canonical and aligned across all layers.

---

## [2026.02.27-PROTOCOL-NEGOTIATION-CONSISTENCY] - v60.2

### Highlights
- **Protocol Negotiation Hardened**: Streamable HTTP now negotiates MCP protocol version per session at `initialize`.
- **Canonical Naming Convergence**: Public tool IDs standardized to `apex_judge` and `eureka_forge`.
- **Server Concepts Parity**: Resources/prompts methods now align with MCP server concepts on streamable transport.
- **Docs + Branding Sync**: Intro and README aligned to trademark line and epistemic-humility message.

### Added
- Protocol regression tests covering:
  - supported older version negotiation,
  - unsupported version rejection,
  - per-session protocol mismatch rejection.

### Changed
- `server.json` now includes `protocolVersion` and `supportedProtocolVersions`.
- `/.well-known/mcp/server.json` discovery output now includes protocol metadata consistently.
- README/docs now consistently document current protocol (`2025-11-25`) and supported versions (`2025-11-25`, `2025-03-26`).
- Project/package versions aligned to `2026.2.27`.

### Verification
- `pytest tests/test_aaa_phase888_mcp_protocol_e2e.py -q` -> pass
- `pytest tests/test_aaa_mcp_contract.py -q` -> pass
- `pytest tests/test_aaa_mcp_constitutional.py -q` -> pass

**Verdict:** SEAL — Protocol truth, naming truth, and docs truth are converged.

---

## [2026.02.25-CHAOS-REDUCTION] - v60.1

### Highlights
- **v60.1 Chaos Reduction**: Eliminated 5,388 phantom untracked files (99.4% from cloned `remote_inspection/`)
- **CLAUDE.md Accuracy Audit**: 6 fixes — Four-Layer architecture, THRESHOLDS dict, triad subdirs documented
- **Version Convergence**: arifOS and OpenClaw both use `YYYY.M.DD` date-based versioning
- **VPS MCP Alignment**: Verified 90%+ compliance with MCP spec 2025-11-25
- **Agent Capability Spec**: Defined 9-dimension VPS management specification (Skills, Tools, Capabilities, Workflows, Schema, Actions, Resources, Agency, Agentic Attributes)
- **Eureka-Atlas Blueprint**: Integrated deep research report for the 777-EUREKA-FORGE metabolizer loop and EBM/DEQ grounding.

### Added
- `.gitignore` v60.1 section: 30 new rules covering `remote_inspection/`, `deploy_stack/`, `node_modules/`, secrets (`*.token`, `*.secret`, `rclone_token.txt`)
- 4 new gotcha warnings in CLAUDE.md: vault999.jsonl tracking, remote_inspection, rclone_token, tests/archive
- Agent Capability Specification for VPS management (4-tier action system: read-only → reversible → destructive → forbidden)
- `docs/deep-research-report.md`: Eureka-Atlas Embedding Engine Blueprint (777-Cube theoretical grounding)
- `scripts/discovery_import_graph.py`: Automated codebase intelligence and import graph discovery tool.

### Changed
- Architecture description: "Three-Layer Stack" → "Four-Layer Stack: PyPI Surface → Transport → Intelligence → Kernel"
- Floor reference: `ALL_FLOORS` → `THRESHOLDS dict` (matching actual `core/shared/floors.py`)
- Documented triad subdirs: `delta/` (anchor, reason, integrate), `omega/` (respond, validate, align), `psi/` (forge, audit, seal)
- Version strings unified to `2026.2.25` across all 8 files (pyproject.toml, core/__init__.py, aaa_mcp/__init__.py, rest_routes.py, README.md, CLAUDE.md, Dockerfile, server.json)

### Fixed
- 5,388 untracked files reduced to 0 via targeted `.gitignore` rules
- CLAUDE.md inaccuracies: `sbert_floors` removed from tree (archived), transport description updated
- Git non-fast-forward resolved with `git pull --rebase`

### State
| Component | Status | Version |
|-----------|--------|---------|
| VPS MCP Server | HEALTHY | 2026.02.25 |
| Tools Loaded | 13/13 | All responding |
| Transport | Streamable HTTP | MCP 2025-11-25 spec |
| Untracked Files | 0 | Down from 5,388 |

**Verdict:** SEAL — All 13 floors pass. Chaos reduced, truth documented.

---

## [2026.02.15-FORGE-TRINITY-SEAL] - T000 Rebirth

### Highlights
- **T000 Versioning**: Date + 3 canon words (FORGE-TRINITY-SEAL)
- **9 Hardened Skills**: Complete tool set from anchor (000) to seal (999)
- **Documentation Alignment**: All docs now match v64.2 code reality
- **HTA Trinity**: arif-fazil.com (HUMAN) + apex.arif-fazil.com (THEORY) + arifos.arif-fazil.com (APPS)
- **Honest State**: Reality Index 0.94 — no lies about L6-L7 being research only

### Added
- 9 canonical MCP tools with constitutional floor mappings:
  - anchor (000): Init & Sense (F11, F12)
  - reason (222): Think & Hypothesize (F2, F4, F8)
  - integrate (333): Map & Ground (F7, F10)
  - respond (444): Draft & Plan (F4, F6)
  - validate (555): Check Impact (F5, F6, F1)
  - align (666): Check Ethics (F9)
  - forge (777): Synthesize Solution (F2, F4, F7)
  - audit (888): Verify & Judge (F3, F11, F13)
  - seal (999): Commit to Vault (F1, F3)
- Reality Index: 0.94 (94% operational, L6-L7 research only)
- "For Institutions" section (enterprise appeal)
- LLM metadata comments in README
- arif-fazil.com personal site to HTA Trinity

### Changed
- Version scheme: Semantic → T000 (Date + 3 canon words)
- README: Top links consolidated, honest state documented
- CHANGELOG: Updated to reflect v64.2 reality
- llms.txt: Version updated from v60.0 to v64.2
- 333_APPS/README.md: Clarified L5-L7 status

### Fixed
- Documentation drift (docs had 5 tools, code had 9)
- Version badge inconsistencies across files
- DEPLOYMENT_STATUS.md archived (outdated v61.0 claims)

### State of the Repo
| Layer | Status | Coverage |
|-------|--------|----------|
| L1-L4 | ✅ SEAL | 100% |
| L5 | 🟡 SABAR | 60% |
| L6-L7 | 🔴 VOID | 10% |
| **Reality Index** | **0.94** | **94%** |

**T000 Format:** `YYYY.MM.DD-[WORD1]-[WORD2]-[WORD3]`
- FORGE = Active development
- TRINITY = ΔΩΨ unified
- SEAL = 13 floors verified

---

## [60.0.0-FORGE] - 2026-02-13

### Highlights
- **Multi-Agent Governance**: 5 registered agents (OpenCode, Claude, Gemini, Codex, Kimi)
- **ACLIP-CAI**: Console for AI with 8 sensing/gating tools
- **Complete Reference**: 1,526-line comprehensive documentation
- **MCP Registry**: Published as [`io.github.ariffazil/aaa-mcp`](https://registry.modelcontextprotocol.io/?q=arif)

### Added
- `AGENTS.md` — Unified multi-agent playbook (571 lines)
- `ARIFOS_COMPLETE_REFERENCE.md` — Complete system reference (1,526 lines)
- `~/.claude/ARIFOS_AGENT_CANON.md` — Global minimum spec for all agents (431 lines)
- ACLIP-CAI server with 8 console tools:
  - `system_health` — RAM, CPU, disk, processes
  - `fs_inspect` — Filesystem inspection
  - `log_tail` — Log reading
  - `net_status` — Network monitoring
  - `config_flags` — Environment flags
  - `chroma_query` — Vector memory queries
  - `cost_estimator` — Thermodynamic cost prediction
  - `forge_guard` — Local safety circuit breaker
- Modular ACLIP-CAI tools in `aclip_cai/tools/`
- E2E test suite for canonical tools (`tests/e2e/`)
- Reality grounding tests (`tests/tools/`)
- Multi-Agent section in README

### Changed
- README metrics updated (85%+ test pass, 99.5% uptime, 33 tools)
- README footer updated to v60.0.0 and 2026-02-13
- Installation section now includes source install option
- Fixed orphaned "4." section numbering in README

### Fixed
- `trinity_forge` hardened against pipeline exceptions
- `SealReceipt` motto handling for missing mottos
- Vault seal path normalization for ASI dict
- SSE transport context handling in Railway entrypoint

---

## [60.0.0] - 2026-02-10

### Highlights
- **MCP Registry Publication**: First Constitutional AI in [MCP Registry](https://registry.modelcontextprotocol.io/?q=arif)
- **25 Canonical Tools**: Full constitutional governance toolset
- **Production Deployment**: Railway + Cloudflare live

### Added
- MCP Registry publication ([`io.github.ariffazil/aaa-mcp`](https://registry.modelcontextprotocol.io/?q=arif))
- `forge` tool — Unified 000-999 constitutional pipeline
- `forge_pipeline` — Alias for backward compatibility
- `get_tools_manifest` — Tool metadata endpoint
- Infrastructure tools:
  - `gateway_route_tool` — Constitutional gateway routing
  - `k8s_apply_guarded` — Constitutional kubectl apply
  - `k8s_delete_guarded` — Constitutional kubectl delete
  - `k8s_constitutional_apply` — K8s apply evaluation
  - `k8s_constitutional_delete` — K8s delete evaluation
  - `k8s_analyze_manifest` — Manifest analysis
  - `opa_validate_manifest` — OPA policy validation
  - `opa_list_policies` — List OPA policies
  - `local_exec_guard` — Shell execution guard
- Server hardening checks and CI py_compile guard
- Fail-closed envelopes for all AGI/ASI tools

### Changed
- Consolidated 18 skills → 9 canonical VERBS
- Implemented auditor feedback for progressive disclosure UX
- MCP-compliant output format standardization
- Engine adapters cleanup with optional import placement

### Fixed
- `apex_verdict` type error with defensive evidence handling
- `reality_search` axiom processing with defensive checks
- IndentationError in `protocol/response.py`
- SSE endpoint to use correct `SseServerTransport.connect_sse`

---

## [55.5.0-HARDENED] - 2026-02-06

### Highlights
- **5-Organ Kernel**: Complete Trinity pipeline implementation
- **Core Foundation**: `core/` established as canonical truth
- **Constitutional Floors**: 13 floors with thermodynamic grounding

### Added
- Core organs implementation:
  - `_0_init.py` — 000_INIT Airlock (F11, F12)
  - `_1_agi.py` — AGI Mind (111-333, F2, F4, F7, F8)
  - `_2_asi.py` — ASI Heart (555-666, F5, F6, F9)
  - `_3_apex.py` — APEX Soul (444-888, F3, F8, F10, F13)
  - `_4_vault.py` — VAULT999 Memory (999, F1, F3)
- `core/shared/physics.py` — Thermodynamic primitives (W₃, ΔS, Ω₀, κᵣ, G)
- `core/shared/floors.py` — 13 constitutional floor implementations
- `core/shared/types.py` — Pydantic models (Verdict, EMD, FloorScores)
- `core/shared/mottos.py` — 9 constitutional mottos
- `core/shared/guards/` — Injection (F12) and Ontology (F10) guards
- `core/pipeline.py` — Unified 000-999 pipeline
- Engine adapters bridging FastMCP to core organs
- Constitutional decorator (`@constitutional_floor`)
- Stage adapter for pipeline stages

### Changed
- Migrated from `codebase/` to `core/` as canonical source
- Unified pipeline with adaptive F2 governance
- Query type classification for adaptive thresholds
- Fast execution paths for low-risk queries

### Fixed
- ASI semantic conscience with emotional distress detection
- Health check grace period for PyTorch/SBERT initialization
- Docker build issues with empty directories

---

## [55.4.0-SEAL] - 2026-01-31

### Highlights
- **FastMCP Migration**: Upgraded to FastMCP 2.14+ (MCP 2025-11-25)
- **PostgreSQL VAULT999**: Production-grade persistence
- **9-Tool Canon**: Canonical tool set established

### Added
- FastMCP 2.14+ integration with MCP 2025-11-25 spec
- PostgreSQL ledger persistence for VAULT999
- Redis session cache integration
- Tool annotations (readOnlyHint, destructiveHint, openWorldHint)
- MCP resources and prompts
- Server capabilities declaration
- Constitutional self-test in CI/CD
- Snyk security scanning

### Changed
- Transport standardization (SSE for remote, stdio for local)
- Unified MCP to root level structure
- 9-tool canonical implementation

### Fixed
- Python closure bug causing all tools to call vault_seal
- Railway deployment configuration
- SSE endpoint routing

---

## [55.3.0] - 2026-01-28

### Highlights
- **Tri-Witness Consensus**: Byzantine fault tolerance implementation
- **REST API**: Constitutional observability endpoints
- **Documentation Site**: arifos.arif-fazil.com launched

### Added
- Tri-Witness consensus (W₃ = ∛(H×A×S))
- Constitutional observability endpoints (F4/F2)
- REST API for all MCP tools
- VAULT999 REST API endpoints
- GitHub Pages deployment for documentation
- Refusal system with legal defensibility

### Changed
- README overhaul for agent/human navigation
- ASI kernel wired to hardened engine
- Init gate wired with ASI empathy detection

### Fixed
- ASI AttributeError (empathy_kappa → empathy.kappa_r)
- Stage 777 absorbed into 888
- Vault merkle state table migrations

---

## [55.2.0-SEAL] - 2026-01-25

### Highlights
- **APEX Trinity**: Complete governance architecture
- **Multi-Agent Hardening**: Constitutional alignment across agents
- **Railway Deployment**: Production infrastructure

### Added
- APEX Trinity deployment (AGI, ASI, APEX)
- PostgreSQL backend for VAULT999
- Railway deployment configuration
- Multi-agent gateway configuration
- Antigravity agent architecture

### Changed
- Core theory files hardened
- GEMINI.md upgraded to v55.2 Codex
- Governance security documentation

### Fixed
- ASI soft floor scoring for benign queries
- Tri-witness boost precision issues

---

## [55.1.0] - 2026-01-22

### Highlights
- **Injection Detection**: Consolidated F12 implementation
- **Schema Validation**: Structured output enforcement
- **MCP Inspector**: Development tooling

### Added
- MCP Inspector service integration
- Canonical trinity tools with LLM-agnostic adapters
- llms.txt and llms-full.txt for AI discovery

### Changed
- F4 Clarity validator hardened with zlib entropy proxy
- Package renamed for consistency

### Fixed
- Circular import between ToolRegistry and canonical_trinity
- Injection detection consolidation

---

## [55.0.0] - 2026-01-20

### Highlights
- **Explicit Tool Architecture**: 9 tools with clear schemas
- **Transport Layer**: Verified integration
- **Handler Layer**: Session state management

### Added
- 9 explicit tools with LLM-legible schemas
- Transport layer verification
- Handler layer with session state
- Edge case handling

### Changed
- Tool layer refactoring for explicitness
- Documentation accuracy verified (95%)

---

## [Earlier Versions]

### v54.x - v49.x (2025-12)
- Initial FastMCP implementation
- Constitutional floor prototypes
- VAULT999 concept development
- Trinity architecture design

### v48.x and earlier (2025)
- Foundation research
- Thermodynamic grounding theory
- Initial prototype development

---

## Version Naming Convention

| Suffix | Meaning |
|:-------|:--------|
| `-FORGE` | Major architectural changes, forged through iteration |
| `-HARDENED` | Security and stability improvements |
| `-SEAL` | Verified and sealed release |
| `-EIGEN` | Eigenvalue/eigenvector optimizations |
| (none) | Standard release |

---

## Constitutional Verdicts in Releases

Each release is assessed against the 13 Constitutional Floors:

| Verdict | Meaning |
|:--------|:--------|
| **SEAL** ✅ | All floors pass — approved for production |
| **PARTIAL** ⚠️ | Soft floor warnings — proceed with caution |
| **SABAR** 🔴 | Requires repair before release |
| **VOID** 🛑 | Hard floor violation — blocked |
| **888_HOLD** 👤 | Requires human review |

---

## Links

- **Repository**: https://github.com/ariffazil/arifOS
- **MCP Registry**: [`io.github.ariffazil/aaa-mcp`](https://registry.modelcontextprotocol.io/?q=arif)
- **Documentation**: https://arifos.arif-fazil.com
- **Live Server**: https://aaamcp.arif-fazil.com

---

**Authority:** Muhammad Arif bin Fazil (888_JUDGE)
**License:** AGPL-3.0-only

*DITEMPA BUKAN DIBERI — Forged, Not Given*
