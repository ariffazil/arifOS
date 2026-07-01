# arifOS Federation — Internal MCP Surface Map

> **Generated:** 2026-07-01 from live `tools/list` probes.  
> **Scope:** every MCP server known to be running on `af-forge`, grouped by transport and organ.  
> **Caveat:** stdio-only servers are listed by package/role; their exact tool names are inferred from upstream package documentation unless otherwise noted.

---

## Executive Summary

| Transport | Server / Organ | Endpoint | Tool Count | Status |
|-----------|----------------|----------|-----------:|--------|
| HTTP (Streamable) | arifOS kernel | `http://localhost:8088/mcp` | 48 | ✅ reachable |
| HTTP (Streamable) | GEOX | `http://localhost:8081/mcp` | 29 | ✅ reachable |
| HTTP (Streamable) | WEALTH | `http://localhost:18082/mcp` | 32 | ✅ reachable |
| HTTP (Streamable) | WELL | `http://localhost:18083/mcp` | 17 | ✅ reachable |
| HTTP (Streamable) | A-FORGE execution | `http://localhost:7071/mcp` | 75 | ✅ reachable |
| HTTP (Streamable) | A-FORGE MCP gateway | `http://localhost:7072/mcp` | — | ⚠️ 400 (stdio/dedicated gateway?) |
| HTTP (SSE) | Graphiti knowledge graph | `http://localhost:8000` | — | ✅ container running |
| stdio | Sequential Thinking | via Hermes/OpenClaw/Claude Desktop | ~3 | running (many instances) |
| stdio | GitHub | via agents | ~10 | running (many instances) |
| stdio | Memory | via agents | ~3 | running (many instances) |
| stdio | Brave Search | via agents | ~1 | running (many instances) |
| stdio | Supabase | via agents | ~5 | running (many instances) |
| stdio | Filesystem (`/root`) | via agents | ~4 | running (many instances) |
| stdio | Postgres (vault999 + Supabase) | via agents | ~3 | running (many instances) |
| stdio | Perplexity | via agents | ~3 | running (many instances) |
| stdio | Exa | via agents | ~3 | running (many instances) |
| stdio | Cloudflare | `/root/.hermes/mcp_servers/cloudflare_mcp.py` | ~3 | running |
| stdio | Composio | `/root/.hermes/mcp_servers/composio_mcp.py` | ~10 | running |
| stdio | Hermes bridge | `/root/.hermes/mcp_servers/hermes_mcp.py` | ~10 | running |
| stdio | Serena | `uvx --from serena-agent serena start-mcp-server` | ~8 | running |
| stdio | Capability Index | `core/capability_index/mcp_server.py` | ~2 | running |

**Total indexed tools on HTTP organs:** 201  
**Estimated total across all servers:** ~250+

---

## 1. arifOS Kernel (`localhost:8088/mcp`)

Public 7 + expanded45 operator surface.

### Canonical 7

1. `arif_init`
2. `arif_observe`
3. `arif_think`
4. `arif_route`
5. `arif_judge`
6. `arif_act`
7. `arif_seal`

### Expanded45 / Diagnostic / Operator Surface

- `arif_canary`
- `arif_conformance_report`
- `arif_triage`
- `arif_compose`
- `arif_os_attest`
- `arif_organ_attest`
- `arif_organ_attest_all`
- `arif_lease_issue`
- `arif_lease_inspect`
- `arif_lease_revoke`
- `arif_heartbeat`
- `arif_peer_contract_validate`
- `arif_peer_contract_attest`
- `arif_peer_contract_forbid`
- `arif_resolve_tool`
- `arif_get_affordance`
- `arif_retrieve_tools`
- `arif_detect_institutional_shadow_drift`
- `arif_detect_narrative_tension`
- `hermes_system_status`
- `hermes_vault_query`
- `arif_vault_query`
- `hermes_epistemic_check`
- `hermes_fact_check`
- `hermes_cross_verify`
- `hermes_plan_review`
- `hermes_memory_steward`
- `arif_wiki_ingest`
- `arif_wiki_map`
- `arif_wiki_search`
- `arif_wiki_ask`
- `arif_stack_health_probe`
- `arif_organ_consensus`
- `arif_scan_local_instructions`
- `arif_session_budget`
- `arif_floor_status`
- `mcp_drift_check`
- `forge_query` (deprecation proxy)
- `forge_plan` (deprecation proxy)
- `forge_dry_run` (deprecation proxy)
- `forge_plan_and_simulate` (deprecation proxy)

---

## 2. GEOX — Earth Intelligence (`localhost:8081/mcp`)

1. `geox_egs_query_entity`
2. `geox_egs_query_claim`
3. `geox_egs_query_uncertainty`
4. `geox_egs_query_provenance`
5. `geox_egs_claim_create`
6. `geox_egs_claim_challenge`
7. `geox_egs_evidence_attach`
8. `geox_egs_evidence_reason`
9. `geox_egs_seismic_compute`
10. `geox_egs_rock_physics`
11. `geox_egs_data_qc_bundle`
12. `geox_egs_scenario_audit`
13. `geox_geomechanics`
14. `geox_deep_time_state`
15. `geox_well_ingest`
16. `geox_well_qc`
17. `geox_well_desurvey`
18. `geox_petrophysics`
19. `geox_sequence`
20. `geox_surface_status`
21. `geox_seismic_ingest`
22. `geox_seismic_interpret`
23. `geox_vision`
24. `geox_subsurface_model`
25. `geox_basin`
26. `geox_claim`
27. `geox_evidence`
28. `geox_prospect`
29. `geox_seismic_compute`

---

## 3. WEALTH — Capital Intelligence (`localhost:18082/mcp`)

1. `wealth_wisdom_evaluate`
2. `wealth_power_audit`
3. `wealth_capture_scan`
4. `wealth_compute_npv`
5. `wealth_compute_irr`
6. `wealth_conservation_check`
7. `wealth_flow_check`
8. `wealth_runway_check`
9. `wealth_compute_emv`
10. `wealth_emv_compute`
11. `wealth_monte_carlo_simulate`
12. `wealth_monte_carlo`
13. `wealth_compute_evoi`
14. `wealth_evoi_compute`
15. `wealth_confluence_check`
16. `wealth_asymmetry_check`
17. `wealth_fiscal_breakeven`
18. `wealth_stock_analysis`
19. `wealth_personal_finance`
20. `wealth_market_data`
21. `wealth_omni_wisdom`
22. `wealth_agent_path`
23. `wealth_reason_agent`
24. `wealth_vault_write`
25. `wealth_vault_query`
26. `wealth_registry_status`
27. `wealth_system_registry_status`
28. `wealth_boundary_governance`
29. `wealth_survival_engine`
30. `wealth_collapse_signature_scan`
31. `wealth_beautiful_mouse_scan`
32. `wealth_judge_handoff`

---

## 4. WELL — Human Readiness (`localhost:18083/mcp`)

1. `well_health_check`
2. `well_medical_boundary`
3. `well_signal_coverage`
4. `well_classify_substrate`
5. `well_trace_lineage`
6. `well_detect_boundary`
7. `well_measure_gradient`
8. `well_assess_metabolism`
9. `well_assess_homeostasis`
10. `well_check_repair`
11. `well_validate_vitality`
12. `well_assess_livelihood`
13. `well_assess_reliability`
14. `well_compute_metabolic_flux`
15. `well_assess_sovereign_entropy`
16. `well_guard_dignity`
17. `well_registry_status`

---

## 5. A-FORGE — Execution Engine (`localhost:7071/mcp`)

Constitutional actuator + engineering surface.

### Governance / Router

1. `forge_session_init`
2. `forge_health_check`
3. `forge_heart_critique`
4. `forge_check_governance`
5. `forge_execute`
6. `forge_approve`
7. `forge_judge_proxy`
8. `forge_vault`
9. `forge_wealth`
10. `forge_well`
11. `forge_probe`
12. `forge_lock`
13. `forge_pipeline_run`
14. `forge_docket_prep`
15. `forge_execute_sealed`
16. `forge_tier_bind`
17. `forge_policy_check`
18. `forge_policy_set`
19. `forge_policy_remove`
20. `forge_policy_list`
21. `forge_policy_save`

### Infra / Observability

22. `forge_systemctl`
23. `forge_journalctl`
24. `forge_status`
25. `forge_job`
26. `forge_abort`
27. `forge_docker`
28. `forge_netdata_alarms`
29. `forge_netdata_metrics`
30. `forge_scan`
31. `forge_chart`

### Filesystem / Memory / DB

32. `forge_filesystem`
33. `forge_memory`
34. `forge_postgres`
35. `forge_git`
36. `forge_github`

### Research / Web / Browser

37. `forge_research`
38. `forge_search`
39. `forge_minimax_search`
40. `forge_docs_lookup`
41. `forge_browser_navigate`
42. `forge_browser_click`
43. `forge_browser_type`
44. `forge_browser_screenshot`
45. `forge_browser_extract_text`
46. `forge_browser_evaluate_js`
47. `forge_github_search_code`
48. `forge_github_search_repos`
49. `forge_github_get_file`
50. `forge_github_create_or_update_file`
51. `forge_github_create_issue`
52. `forge_github_create_pull_request`

### Shell / Execution

53. `forge_shell`
54. `forge_shell_dryrun`
55. `forge_shell_status`
56. `forge_shell_ledger`
57. `forge_shell_alert_history`

### Tool Forge / Registry / Scar

58. `forge_skill`
59. `forge_seal`
60. `forge_registry`
61. `forge_registry_status`
62. `forge_evaluate`
63. `forge_witness`
64. `forge_scar`
65. `forge_register`
66. `forge_reality_loop`
67. `forge_scar_scan`
68. `forge_skillstore_write`
69. `forge_skillstore_read`

### Artifact Synthesis / Staging

70. `forge_synthesize`
71. `forge_stage`
72. `forge_sandbox_run`
73. `forge_document_ingest`

### Agent / Lease

74. `forge_agent`
75. `forge_lease`

---

## 6. A-FORGE MCP Dedicated Gateway (`localhost:7072/mcp`)

- **Status:** HTTP 400 on StreamableHTTP probe.
- **Likely transport:** stdio or dedicated MCP gateway (not streamable-http on this path).
- **Note:** `7071/mcp` already exposes the full A-FORGE surface above.

---

## 7. Graphiti Knowledge Graph (`localhost:8000`)

- **Package:** `zepai/knowledge-graph-mcp`
- **Transport:** HTTP/SSE on port 8000 (Docker container `graphiti-mcp`).
- **Role:** Episodic knowledge graph (L5/L6 memory substrate).
- **Known tools:** entity search, relation search, graph query, ingest, health.

---

## 8. A-FORGE Sequential Thinking Server

- **Path:** `/root/A-FORGE/services/sequential-thinking/server.py`
- **Transport:** stdio / local socket.
- **Role:** Structured chain-of-thought scratchpad.
- **Known tools:** `sequentialthinking`, `create_thought`, `delete_thought`.

---

## 9. Agent-Spawned Stdio Servers (Hermes / OpenClaw / Claude Desktop)

These are launched per-agent-session; multiple instances may be running concurrently.

| Server | Typical Tools | Notes |
|--------|--------------|-------|
| `@modelcontextprotocol/server-sequential-thinking` | sequentialthinking | Multiple wrappers exist |
| `@modelcontextprotocol/server-github` | search_issues, search_code, create_issue, create_pr, etc. | |
| `@modelcontextprotocol/server-memory` | read_graph, search_nodes, open_nodes, add_nodes | |
| `@modelcontextprotocol/server-brave-search` | brave_web_search | |
| `@supabase/mcp-server-supabase` | query, schema introspection | Project ref `utbmmjmbolmuahwixjqc` |
| `@modelcontextprotocol/server-filesystem` | read_file, write_file, list_directory | Scoped to `/root` |
| `@modelcontextprotocol/server-postgres` | query, schema | vault999 + Supabase pools |
| `@perplexity-ai/mcp-server` | perplexity_ask, perplexity_search | |
| `exa-mcp-server` | exa_search, exa_answer | |
| `cloudflare_mcp.py` | Cloudflare API tools (workers, KV, R2, DNS) | Hermes custom server |
| `composio_mcp.py` | Composio action hub | Hermes custom server |
| `hermes_mcp.py` | Telegram bridge, A2A dispatch | Hermes custom server |
| `serena-agent` | symbol search, file read, diagnostics | LSP-backed codebase tool |
| `core/capability_index/mcp_server.py` | capability_search, capability_select | Federation tool discovery |

---

## Drift / Governance Notes

- **Canonical 7:** only `arif_init`, `arif_observe`, `arif_think`, `arif_route`, `arif_judge`, `arif_act`, `arif_seal` are advertised to external clients by default.
- **Expanded45:** exposed only when `ARIFOS_MCP_EXPOSE_DEV_TOOLS=true`.
- **Capability graph:** `arif_os_attest` and `arif_retrieve_tools` were added to the kernel capability graph in v0.2.2 (2026-07-01) to stop interceptor DENY.
- **Middleware:** DENY/QUARANTINE/VOID responses now carry schema-valid `structuredContent` to prevent MCP SDK output-validation errors.
- **A-FORGE deprecation proxies:** `forge_query`, `forge_plan`, `forge_dry_run`, `forge_plan_and_simulate` on arifOS are thin redirects; real forge tools live on `7071/mcp`.

---

*DITEMPA BUKAN DIBERI.*
