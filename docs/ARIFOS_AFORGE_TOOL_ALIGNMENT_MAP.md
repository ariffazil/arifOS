# arifOS ↔ A-FORGE Tool Alignment Matrix

**Sovereign request:** map every tool in arifOS and A-FORGE, aligned by tool name, function, code location, docs, physics, and math.

**Survey date:** 2026-06-23  
**Live surfaces queried:** `http://localhost:8088/tools` (arifOS), `:7072/mcp` tools/list (A-FORGE)  
**Codebases walked:** `/root/arifOS`, `/root/A-FORGE`

---

## Executive Summary

| Organ | Role | Live tools | Source-registered | Hidden / gated |
|-------|------|------------|-------------------|----------------|
| **arifOS** (port 8088) | Constitutional kernel — *brain* | **17** | 16 canonical + 1 canary | 5 internal computation engines + 41 diagnostic/lease/attestation tools |
| **A-FORGE** (port 7071/7072) | Execution shell — *hands* | **77** | 80 (3 not yet live) | Internal AgentEngine tool classes, stale `/mcp` advert says 59 |

**Core contract:** arifOS adjudicates (INIT→OBSERVE→REASON→JUDGE→SEAL). A-FORGE executes only after a SEAL/lease, and proxies a subset of arifOS kernel tools so external agents can speak to the brain through the hands.

---

## 1. Aligned by Constitutional Stage

Each row shows the same cognitive function in both organs.

| Stage | arifOS tool | A-FORGE tool(s) | Function summary | Code (arifOS) | Code (A-FORGE) | Docs | Physics / Math |
|-------|-------------|-----------------|------------------|---------------|----------------|------|----------------|
| **000 INIT** | `arif_init` | `arif_session_init` | Bootstrap kernel-born session, identity binding, epoch open/seal | `arifosmcp/runtime/tools.py:4940` (`_arif_session_init`) | `src/interfaces/mcp/core.ts:406` | arifOS: `constitutional_map.py:487`, `prompts/__init__.py:90`; A-FORGE: `MCP_TOOL_CATALOG.md` §1 | Three-phase binding; pre-session lanes do not require `session_id` |
| **111 SENSE** | `arif_observe` | `arif_sense_observe` | Multimodal reality observation: search, ingest, compass, atlas, vitals | `arifosmcp/runtime/tools.py:6362` (`_arif_sense_observe`) | `src/interfaces/mcp/core.ts:554` | arifOS: `constitutional_map.py:511`; A-FORGE: `MCP_TOOL_CATALOG.md` §1 | arifOS: `w_score = f(uncertainty, importance, freshness, background_confidence)`; A-FORGE returns fixed `lambda2_vector: [0.99, 0.98, 0.95]` |
| **111 SENSE** | `arif_explore` | — | Governed multi-step exploration (navigator, prospector, driller, mapper, auto) | Same handler as `arif_observe` | — | arifOS: `constitutional_map.py:533` | Routed through `_arif_sense_observe` |
| **222 EVIDENCE** | `arif_fetch` | `forge_research`, `forge_search`, `forge_minimax_search` | Verified external evidence / web retrieval | `arifosmcp/runtime/tools.py:7454` (`_arif_evidence_fetch`) | `gatewayTools.ts:678`, `688`, `830` | arifOS: `constitutional_map.py:561`; A-FORGE: `docs/prompts/research-intelligence-machine.md` | arifOS: sequential-thinking params (`thinking_depth`, `thinking_budget`, `confidence_threshold`); A-FORGE: confidence = high if >5 results |
| **333 REASON** | `arif_think` | `arif_mind_reason` | Symbolic / LLM reasoning, reflection, plan, critique | `arifosmcp/runtime/tools.py:8892` (`_arif_mind_reason_tool`) | `src/interfaces/mcp/core.ts:573` | arifOS: `constitutional_map.py:584`, `prompts/__init__.py:296`; A-FORGE: `MCP_TOOL_CATALOG.md` §1 | arifOS: structural modes bypass LLM; cognitive modes route through SEA-LION/Ollama; `plan_approve` deterministic L13; A-FORGE: `maxTokens: 500` |
| **444r REPLY** | `arif_compose` | — | Governed response composition, summarization, citation, tone shift | `arifosmcp/runtime/tools.py:10170` (`_arif_reply_compose_tool`) | — | arifOS: `constitutional_map.py:687` | LLM-aware fallback via `runtime.reply_compose`; `ai_involvement` + `language` params |
| **555 ROUTE** | `arif_route` | — | Intent-based routing to GEOX/WEALTH/WELL/A-FORGE | `arifosmcp/tools/kernel_canonical.py:111` | — | arifOS: `constitutional_map.py:641` | Longest-keyword match against `config/organ_intent_map.yaml` |
| **555 ROUTE** | `arif_triage` | — | Session status / preflight / priority | `arifosmcp/tools/kernel_canonical.py:206` | — | arifOS: `constitutional_map.py:655` | Priority string → score 1–4 |
| **555 ROUTE** | `arif_bridge_connect` | `arif_forge_execute` (indirect), `forge_pipeline` | Direct organ tool call bypassing intent map | `arifosmcp/tools/kernel_canonical.py:300` | `core.ts:730`, `1332` | arifOS: `constitutional_map.py:670` | Requires recent alive organ attestation; A-FORGE pipeline uses regex routing |
| **555m MEMORY** | `arif_memory` | `forge_memory_recall`, `forge_memory_store` | Federated memory: recall, remember, promote, revise, forget | `arifosmcp/runtime/tools.py:16461` (`_arif_memory_v5_router`) | `proxyTools.ts:279`, `317` | arifOS: `constitutional_map.py:706`; A-FORGE: `MCP_TOOL_CATALOG.md` §3 | arifOS: v5 native modes → `tool_13_arif_memory.py`; legacy → `_arif_memory_recall`; A-FORGE: falls back to `ls -t /root/arifOS/VAULT999/*.jsonl` |
| **666 CRITIQUE** | `arif_critique` | `arif_heart_critique`, `forge_check_governance` | Ethical / risk / red-team / empathy review | `arifosmcp/runtime/tools.py:11039` (`_arif_heart_critique`) | `core.ts:620`, `629` (same handler) | arifOS: `constitutional_map.py:619`; A-FORGE: `MCP_TOOL_CATALOG.md` §1 | arifOS: scans 10+ indirect-injection regex patterns; 8 risk categories; A-FORGE: shares heart handler |
| **777 MEASURE** | `arif_measure` | `forge_netdata_alarms`, `forge_netdata_metrics`, `forge_log_tail`, `forge_well_state_read` | Resource thermodynamics / health / vitals / topology | `arifosmcp/runtime/tools.py:11868` (`_arif_ops_measure`) | `gatewayTools.ts:814`, `820`; `forgeTools.ts:665`; `core.ts:1124` | arifOS: `constitutional_map.py:795`; A-FORGE: `MCP_TOOL_CATALOG.md` §12 | arifOS: `g_score = max(0, 1-(cpu+mem+disk)/300)`, `omega = max(0, 1-(cpu/100)*0.5)`, `psi_le = 1+(mem/100)*0.1`; A-FORGE: delegates to Netdata / systemd |
| **888 JUDGE** | `arif_kernel_intercept`, `arif_judge` | `forge_judge_proxy` | Constitutional arbitration / verdict | `arifosmcp/tools/arif_kernel_intercept.py:78`; `arifosmcp/runtime/tools.py:13113` (`_arif_judge_deliberate_tool`) | `core.ts:815` | arifOS: `constitutional_map.py:472`, `734`; A-FORGE: `BRAIN_HANDS_MCP_MAPPING.md` | arifOS: verdicts SEAL/SABAR/HOLD/VOID; surfaces institutional scars; A-FORGE forwards to `arifos.arif_judge_deliberate` |
| **999 SEAL** | `arif_seal` | `arif_vault_seal`, `forge_remember` | Immutable VAULT999 ledger write / closure | `arifosmcp/runtime/tools.py:14430` (`_arif_vault_seal_tool`) | `core.ts:848`, `849` (same handler) | arifOS: `constitutional_map.py:752`; A-FORGE: `MCP_TOOL_CATALOG.md` §3 | Requires `ack_irreversible=True`; triggers Supabase `seal_vault999`; A-FORGE default telemetry `{dS:0, peace2:0, psi_le:0, W3:0, G:0}` |
| **010 FORGE** | `arif_forge` | `arif_forge_execute`, `forge_run` | Build / execute / generate / commit / dry-run | `arifosmcp/runtime/tools.py:15241` (`_arif_forge_execute_tool`) | `core.ts:730`, `757` (same handler) | arifOS: `constitutional_map.py:769`; A-FORGE: `MCP_TOOL_CATALOG.md` §2 | arifOS: dry-run default; gated by `side_effects_allowed`; A-FORGE: registers Read/Write/ApplyPatches/List/Grep + WEALTH + MiniMax tools in sandbox |
| **canary** | `arif_canary` | — | Unified transport diagnostic: ping, schema_echo, version_echo, conformance_report | `arifosmcp/tools/canary_multimode.py:38` | — | arifOS: `constitutional_map.py:947` | Zero-floor read-only; supersedes 5 deprecated aliases |

---

## 2. A-FORGE-Only Execution Surface

These tools exist only in A-FORGE; arifOS has no direct equivalent (it delegates execution through `arif_forge`).

### 2.1 Filesystem, Git, GitHub, Docker, DB

| Tool | Function | Code | Docs | Physics / Math |
|------|----------|------|------|----------------|
| `forge_filesystem_read` | Read file/dir; allowed roots `/root`, `/tmp`, `/data`, `/var/log` | `proxyTools.ts:66` | `MCP_TOOL_CATALOG.md` §5 | — |
| `forge_filesystem_write` | Write file; overwrite flag required | `proxyTools.ts:108` | §5 | — |
| `forge_filesystem_glob` | Glob search; cap 500 | `proxyTools.ts:143` | §5 | — |
| `forge_filesystem_grep` | Regex search via `grep -rn | head -200` | `proxyTools.ts:164` | §5 | — |
| `forge_filesystem_stat` | File/directory metadata | `proxyTools.ts:189` | §5 | — |
| `forge_postgres_query` | Raw SQL via `psql --csv`; blocks DROP/TRUNCATE/ALTER even with `mutate=true` | `proxyTools.ts:224` | §6 | — |
| `forge_postgres_schema` | List tables/columns | `proxyTools.ts:250` | §6 | — |
| `forge_git_status` | Working tree + branch + ahead | `proxyTools.ts:355` | §7 | — |
| `forge_git_diff` | Uncommitted diff | `proxyTools.ts:372` | §7 | — |
| `forge_git_log` | Recent commits; count clamped to 50 | `proxyTools.ts:390` | §7 | — |
| `forge_git_commit` | Stage & commit; optional push | `proxyTools.ts:406` | §7 | — |
| `forge_github_search` | Search repos/code/issues/PRs via curl | `proxyTools.ts:438` | §8 | — |
| `forge_github_pr` | List/get/create PRs | `proxyTools.ts:472` | §8 | — |
| `forge_github_search_code` | GitHub code search (typed REST) | `gatewayTools.ts:754` | §9 | — |
| `forge_github_search_repos` | Repo search | `gatewayTools.ts:761` | §9 | — |
| `forge_github_get_file` | Read file from GitHub | `gatewayTools.ts:768` | §9 | — |
| `forge_github_create_or_update_file` | Commit file; optional draft PR | `gatewayTools.ts:776` | §9 | — |
| `forge_github_create_issue` | Create issue | `gatewayTools.ts:790` | §9 | — |
| `forge_github_create_pull_request` | Create PR | `gatewayTools.ts:801` | §9 | — |
| `forge_docker_ps` | List containers | `proxyTools.ts:516` | §10 | — |
| `forge_docker_logs` | Tail logs | `proxyTools.ts:532` | §10 | — |
| `forge_docker_exec` | Execute command in container | `proxyTools.ts:548` | §10 | — |
| `forge_docker_images` | List images | `proxyTools.ts:566` | §10 | — |

### 2.2 Identity, Leases, Agents, Locks

| Tool | Function | Code | Docs | Physics / Math |
|------|----------|------|------|----------------|
| `forge_agent_register` | Register agent identity + authority ceiling | `forgeTools.ts:107` | §4 | Authority ceilings: mutate_files, shell_exec, git_commit, deploy, vault_seal |
| `forge_agent_status` | Query one agent | `forgeTools.ts:150` | §4 | — |
| `forge_agent_list` | List registered agents | `forgeTools.ts:173` | §4 | — |
| `forge_lease_request` | Request bounded authority lease; TTL clamped 3600 s | `forgeTools.ts:407` | §4; `BRAIN_HANDS_MCP_MAPPING.md` | Maps 8-value taxonomy to arifOS classes |
| `forge_lease_status` | Inspect lease TTL/scope | `forgeTools.ts:469` | §4 | — |
| `forge_lease_revoke` | Revoke lease | `forgeTools.ts:531` | §4 | — |
| `forge_lock_acquire` / `request_amanah_lock` | Canonical Amanah/F1 lock | `core.ts:1182`, `1215` | §4 (deprecated alias listed) | TTL ms conversion |
| `forge_lock_release` / `release_amanah_lock` | Canonical Amanah release | `core.ts:1242`, `1269` | §4 | — |

### 2.3 Browser, Search, Research, Monitoring

| Tool | Function | Code | Docs | Physics / Math |
|------|----------|------|------|----------------|
| `forge_research` | Governed web research (Brave) | `gatewayTools.ts:678` | §11; `docs/prompts/research-intelligence-machine.md` | Confidence heuristic |
| `forge_search` | Brave web search | `gatewayTools.ts:688` | §11 | — |
| `forge_docs_lookup` | Context7 docs lookup | `gatewayTools.ts:696` | §11 | — |
| `forge_minimax_search` | Local MiniMax MCP gateway | `gatewayTools.ts:830` | §11 | Calls `localhost:18091/mcp` |
| `minimax_web_search` | Direct MiniMax web search | `core.ts:523` | §11 | — |
| `minimax_understand_image` | Direct MiniMax image understanding | `core.ts:539` | §11 | — |
| `forge_browser_navigate` / `click` / `type` / `screenshot` / `extract_text` / `evaluate_js` | Browser automation | `gatewayTools.ts:704-746` | §11 | Passes `browserInjectionSentinel` |
| `forge_log_tail` | Tail systemd/journalctl logs | `forgeTools.ts:665` | §12 | Lines clamped 200 |
| `forge_netdata_alarms` | Read Netdata alarms | `gatewayTools.ts:814` | §12 | Filters: all/raised/clear/warning/critical |
| `forge_netdata_metrics` | Read Netdata chart data | `gatewayTools.ts:820` | §12 | `GET /api/v1/data?chart=...` |
| `forge_registry_status` | Tool registry truth (hard-coded 31 names — stale) | `forgeTools.ts:563` | §14 | Does **not** reflect full 77-tool live surface |
| `forge_shell_dryrun` | Preview shell output; blocks dangerous patterns | `forgeTools.ts:605` | §14 | Blocks `rm -rf /`, `mkfs`, `dd if=`, `> /dev/`, fork bomb, DROP |
| `forge_job_submit` | Submit async background job | `forgeTools.ts:714` | §14 | In-memory `jobStore` |
| `forge_job_status` | Poll job status | `forgeTools.ts:763` | §14 | — |

### 2.4 Domain Organ Proxies (WEALTH / WELL)

| Tool | Function | Code | Docs | Physics / Math |
|------|----------|------|------|----------------|
| `wealth_evaluate_ROI` | Evaluate investment ROI | `core.ts:985` | §13 | Delegates to `WEALTH_TOOLS[0]`; fallback in `WealthTools.ts:39-105` |
| `wealth_compute_EMV` | Compute Expected Monetary Value | `core.ts:991` | §13 | Delegates to `WEALTH_TOOLS[1]` |
| `wealth_thermodynamic_scan` | Landauer-cost scan | `core.ts:997` | §13 | Delegates to `WEALTH_TOOLS[2]` |
| `forge_well_state_read` | Read WELL `state.json` | `core.ts:1124` | §13 | — |
| `forge_well_readiness_check` | WELL readiness verdict | `core.ts:1129` | §13 | ≥80 OPTIMAL, ≥60 FUNCTIONAL, else LOW_CAPACITY; violations → DEGRADED |
| `forge_well_floor_scan` | Scan 13 W-floors | `core.ts:1134` | §13 | — |
| `forge_well_anchor` | Anchor WELL state to vault999 | `core.ts:1139` | §13 | — |

---

## 3. arifOS-Only Internal / Gated Surfaces

These are **not** on the default public MCP wire but exist in the arifOS codebase.

### 3.1 Internal computation engines (`arifosmcp/mcp_tools.py`)

| Tool | Domain | Function / modes | Code | Physics / Math |
|------|--------|------------------|------|----------------|
| `arifos_compute_physics` | Physics / math | petrophysics, stratigraphy_correlate, geometry_build, monte_carlo, entropy_audit, growth_runway | `arifosmcp/tools_canonical.py:47` | `V = area × thickness × porosity × (1-Sw) / B_o` (bbl); inverse-CDF Monte Carlo; Shannon entropy; multiple-IRR detection; `CAGR = (|last|/|first|)^(1/n) - 1` |
| `arifos_compute_finance` | Finance / economic | npv, irr, mirr, emv, dscr, payback, profitability_index, allocation_rank, budget_optimize, wealth_score_kernel, etc. | `arifosmcp/tools_canonical.py:238` | `EMV = Σ(o_i × p_i)`; `DSCR = EBITDA / debt_service`; discounted payback `Σ cf_i / (1+r)^i`; value/cost greedy knapsack; `svs = verifiable_scope / executable_scope` |
| `arifos_compute_civilization` | Governance / game theory | sustainability_path, game_theory, cross_evidence_synthesize | `arifosmcp/tools_canonical.py:698` | Simplified equal-contribution Shapley: `shapley[agent] = 1/n` |
| `arifos_oracle_bio` | WELL biological state | snapshot_read, readiness_check, floor_scan, log_update, deltascan | `arifosmcp/tools_canonical.py:776` | Proof-of-Friction: `w_scar = action_weight × (1-kappa_r)`; `expected_threshold = w_scar × 10.0`; `friction_ratio = actual_delta / expected_threshold` |
| `arifos_oracle_world` | GEOX / WEALTH external data | geox_scene_load, geox_skills_query, macro_snapshot, series_fetch | `arifosmcp/tools_canonical.py:1030` | Bridges to GEOX MCP (`geox_data_ingest_bundle`, `geox_list_skills`) |

### 3.2 Constitutional physics constants

From `arifosmcp/core/physics/thermodynamics_hardened.py`:

| Constant | Value | Meaning |
|----------|-------|---------|
| `K_BOLTZMANN` | 1.380649×10⁻²³ J/K | Boltzmann constant |
| `T_ROOM` | 300.0 K | Standard operating temperature |
| `LANDAUER_MIN` | `K_BOLTZMANN × T_ROOM × ln(2)` ≈ 2.87×10⁻²¹ J/bit | Minimum energy to erase one bit |
| `MAX_ENTROPY_DELTA` | 0.0 | F4 Clarity: entropy must not increase |
| `MIN_THERMODYNAMIC_EFFICIENCY` | 0.1 (10%) | Minimum thermodynamic efficiency |
| `MAX_OMEGA_ENV` | 0.08 | F7 environmental uncertainty ceiling |

Thermodynamic budget model:
- `COST_PER_REASON_CYCLE` = 1×10⁻³ J
- `COST_PER_TOOL_CALL` = 1×10⁻² J
- `COST_PER_TOKEN` = 1×10⁻⁶ J
- `COST_PER_BIT_PROCESSED` = `LANDAUER_MIN × 100`
- Entropy reduction cost: `bits = |ΔS| × 1000`, `cost = bits × COST_PER_BIT_PROCESSED`

### 3.3 Diagnostic / lease / attestation tools (`DIAGNOSTIC_TOOLS`)

arifOS declares **41** diagnostic tools exposed only when `ARIFOS_MCP_EXPOSE_DEV_TOOLS=true` (default off), except `hermes_vault_query` which is always exposed for the conformance spine.

Categories:
- 7× `hermes_*` cross-verification tools
- 5× deprecated individual canary aliases (`arif_ping`, `arif_schema_echo`, `arif_version_echo`, `arif_transport_echo`, `arif_initialize_probe`)
- 3× lease tools (`arif_lease_issue`, `arif_lease_inspect`, `arif_lease_revoke`)
- 7× federation attestation / heartbeat / peer-contract tools
- 3× forge sub-tools (`forge_query`, `forge_plan`, `forge_dry_run`) — deprecated, moved to A-FORGE MCP
- Narrative / shadow-drift tools
- Diagnostic helpers (`arif_stack_health_probe`, `mcp_drift_check`, `arif_floor_status`)
- ChatGPT compatibility shims (`arif_search`, `arif_fetch`)

---

## 4. Physics & Math Alignment — Side-by-Side

| Domain | arifOS | A-FORGE |
|--------|--------|---------|
| **Thermodynamic floor** | Landauer limit, Shannon entropy, entropy-reduction cost | `wealth_thermodynamic_scan` delegates to WEALTH; fallback `thermodynamicBand` thresholds: CRITICAL ≥50 kJ, HIGH ≥10 kJ, MEDIUM ≥5 kJ, else LOW |
| **Operational health** | `g_score = max(0, 1-(cpu+mem+disk)/300)`, `omega`, `psi_le` | `forge_netdata_*` + `forge_log_tail` read external telemetry; WELL thresholds 60/80 |
| **Finance / ROI** | Full `arifos_compute_finance` engine: NPV, IRR, MIRR, EMV, DSCR, payback, PI, allocation rank, budget optimize | `wealth_evaluate_ROI`, `wealth_compute_EMV` proxy WEALTH; fallback formula in `WealthTools.ts`: `emv = expectedReturn - capitalRequired`, `npv = expectedReturn/(1+r) - capitalRequired`, `objectiveScore = (peaceSquared × knowledgeDelta) / (entropyDelta × capitalDelta)` |
| **Petrophysics** | `V = area × thickness × porosity × (1-Sw) / B_o` in `arifos_compute_physics` | No direct MCP tool; GEOX bridge via `arif_bridge_connect` or `arif_forge_execute` |
| **Monte Carlo** | Inverse-CDF sampling from discrete outcomes/probabilities, returns mean/std/p10/p50/p90 | No direct tool; WEALTH has its own Monte Carlo on port 18082 |
| **Proof-of-Friction / WELL** | `w_scar = action_weight × (1-kappa_r)`; `friction_ratio = actual_delta / expected_threshold` | `forge_well_*` proxies read `state.json` and call WELL server on port 18083 |
| **Action-class severity** | `ReversibilityClass` R1-R5 + `TruthState` enums | `actionClassifier.ts`: IRREVERSIBLE=0 … OBSERVE=7; `requiresGovernance()` / `requires888Hold()` |

---

## 5. Docs & Source-of-Truth Alignment

| Layer | arifOS | A-FORGE |
|-------|--------|---------|
| **Single source of truth** | `arifosmcp/constitutional_map.py` | `docs/MCP_TOOL_CATALOG.md` (77-tool catalog) + `docs/BRAIN_HANDS_MCP_MAPPING.md` |
| **Runtime registry** | `arifosmcp/runtime/tools.py` (`_CANONICAL_HANDLERS`, `_RUNTIME_DIAGNOSTIC_HANDLERS`) | `src/interfaces/mcp/core.ts` + `proxyTools.ts` + `forgeTools.ts` + `gatewayTools.ts` |
| **Tool discovery metadata** | `arifosmcp/resources/tool_discovery_resource.py` | `MCP_TOOL_CATALOG.md` (markdown), no runtime resource equivalent |
| **MCP resources** | `resources/tool_discovery_resource.py`, `resources/resources_index.py` | `src/interfaces/mcp/resources.ts` (`forge://governance/floors`, `forge://vault/records`, `forge://well/state`, etc.) |
| **Prompts** | `arifosmcp/prompts/__init__.py` (7 reality-engineering prompts + F1-F13 + truth hierarchy) | `docs/prompts/research-intelligence-machine.md` |
| **Architecture contract** | `AGENTS.md` §6, §10 | `docs/BRAIN_HANDS_MCP_MAPPING.md`, `docs/api/MCP_CONTRACTS.md`, `AGENTS.md` |

---

## 6. Drift, Gaps, and Discrepancies

### 6.1 Count drift

| Surface | Declared | Live | Gap |
|---------|----------|------|-----|
| arifOS `/health` | `tools_loaded: 16`, `tools_exposed_via_mcp: 20`, `total_declared_tools: 57` | `/tools` returns **17** | Diagnostic/dev tools gated by env var; runtime drift flag true |
| A-FORGE source | **80** registrations | `tools/list` returns **77** | `forge_lock_acquire`, `forge_lock_release`, `forge_pipeline_run` missing at runtime |
| A-FORGE static advert | `GET /mcp` says **59** tools | Live returns 77 | Stale hard-coded advert in `src/interfaces/server.ts:139` |
| A-FORGE registry status | `forge_registry_status` hard-codes **31** names | Live returns 77 | Registry-status tool is stale |

### 6.2 Source/live drift
- **arifOS:** `/health` reports `runtime_drift: true` — local code (`1d504e7`) diverged from production image (`80ef1e6`). Flagged as L10 ONTOLOGY gap.
- **A-FORGE:** Live service predates current TypeScript source by at least 3 tools.

### 6.3 Computation engines not on main wire
- The 5 `arifos_*` computation/oracle engines (`arifos_compute_physics`, `arifos_compute_finance`, `arifos_compute_civilization`, `arifos_oracle_bio`, `arifos_oracle_world`) are implemented in `arifosmcp/tools_canonical.py` and registered via `mcp_tools.py`, but **not** exposed by the default `server.py` MCP surface. They are reachable only through unified/agent-specific MCP factories.

### 6.4 Internal AgentEngine tools not exposed as MCP tools
- `WealthPortfolioOptimizeTool`, `WealthEntropyBudgetTool`, `WealthObjectiveComputeTool` exist as classes in `WealthTools.ts` but are **not** wrapped as MCP tools; only `wealth_evaluate_ROI`, `wealth_compute_EMV`, `wealth_thermodynamic_scan` are exposed.
- `GEOXLogInterpreterBridge` is registered only in the CLI, not in MCP `arif_forge_execute`.

### 6.5 Formula / logic issues spotted
- arifOS `arifos_compute_finance` profitability_index line 427: `npv_result.get("npv", 0.0) if "npv_result" else 0.0` — the string `"npv_result"` is always truthy, so the fallback branch is unreachable.
- A-FORGE `WealthTools.ts` fallback uses fixed base `maruahScore = 0.92` and domain penalties that may not match the canonical WEALTH organ math.
- A-FORGE `arif_sense_observe` returns a fixed `lambda2_vector: [0.99, 0.98, 0.95]` rather than computing it from evidence.

### 6.6 Duplicate or overlapping surfaces
- **MiniMax:** direct tools `minimax_web_search` / `minimax_understand_image` vs gateway tool `forge_minimax_search`.
- **GitHub:** lightweight curl proxy (`forge_github_search`, `forge_github_pr`) vs typed REST gateway (`forge_github_search_code`, `forge_github_create_pull_request`, etc.).
- **Vault seal:** `arif_vault_seal` and `forge_remember` share the same handler.
- **Forge execute:** `arif_forge_execute` and `forge_run` share the same handler.
- **Critique:** `arif_heart_critique` and `forge_check_governance` share the same handler.

---

## 7. Recommended Clean-Up Actions

1. **Reconcile counts:** decide whether `arif_canary` counts as one tool or many; update `/health` metrics and A-FORGE `GET /mcp` advert to match live surfaces.
2. **Refresh A-FORGE build** so `forge_lock_acquire`, `forge_lock_release`, and `forge_pipeline_run` appear on the live wire.
3. **Decide on arifOS computation engines:** either expose `arifos_compute_physics/finance/civilization` and the two oracles on the main MCP surface, or document them explicitly as sub-MCP-only.
4. **Fix `forge_registry_status`** so it dynamically reflects the live tool list instead of a hard-coded 31-name list.
5. **Fix arifOS profitability_index** fallback bug at `tools_canonical.py:427`.
6. **Align WEALTH fallback math** in A-FORGE `WealthTools.ts` with canonical WEALTH organ formulas.
7. **Document aliases** in both organs so external agents know `forge_remember` == `arif_vault_seal`, `forge_run` == `arif_forge_execute`, etc.

---

*Generated by Constitutional Clerk — arifOS Federation.*
