# Sovereignty Drill Failure — 2026-07-05T02:00:38+00:00

## What Happened

Monthly sovereignty drill detected that Tier 3 (Ollama) **did not serve traffic**
when Tier 1 (MiniMax) and Tier 2 (ILMU) were disabled.

## Health Endpoint Response

```json
{"status":"healthy","identity_hash":{"algorithm":"BLAKE3","source":"identity.toml","b3_hash":"afb9c0a4adcabc6d68ec7c573ff38d6b7126aafe78ea6e23f72b6c0b80d2de22","b3_prefix":"afb9c0a4adcabc6d"},"service":"arifOS-mcp","mcp_protocol_version":"2025-11-25","mcp_supported_protocol_versions":["2025-11-25","2025-03-26","2024-11-05"],"release_name":"v2026.07.04-MARHIN","version":"kanon-c6fa7a5","git_commit":"c6fa7a5","git_branch":"main","build_time":"2026-07-05T02:00:14.181508+00:00","image":null,"deployment_source":"native","deployment_marker":"/opt/arifos/app/.git_commit","deployment_marker_exists":true,"runtime_path":"/opt/arifos/app","transport":"streamable-http","tools_loaded":17,"canonical_tools_loaded":17,"tools_exposed_via_mcp":47,"canonical_tools":17,"diagnostic_tools":41,"total_declared_tools":58,"operational_tools":30,"tool_count_semantics":{"canonical_tools_loaded":"Constitutional core tools from CANONICAL_TOOLS (dynamically derived)","diagnostic_tools":"Supporting MCP tools (leases, probes, Hermes, forge helpers, attestation, diagnostics) from DIAGNOSTIC_TOOLS","tools_exposed_via_mcp":"Total tools returned by MCP tools/list (includes all FastMCP registered tools)","total_declared_tools":"CANONICAL_TOOLS + DIAGNOSTIC_TOOLS (the full declared surface)"},"tool_manifest_url":"https://arifos.arif-fazil.com/manifest.txt","tool_manifest_hash":"auto-generated","surface_consistency":{"canonical_hash":"ea7fc3a794a5d363","canonical_count":9,"verdict":"CONSISTENT","vantages":[{"source":"CANONICAL_13","count":9,"hash":"ea7fc3a794a5d363","matches_canonical":true},{"source":"CANONICAL_TOOLS (exposed only)","count":9,"hash":"ea7fc3a794a5d363","matches_canonical":true},{"source":"CANONICAL_TOOLS (full internal superset)","count":17,"hash":"8a83e9a8720de858","matches_canonical":false,"exposed_count":9,"internal_count":8,"internal_tools":["arif_act","arif_bridge_connect","arif_fetch","arif_judge_deliberate","arif_kernel_intercept","arif_measure","arif_memory","arif_triage"],"note":"F13-ratified: internal tools hidden from public facade — NOT a divergence"},{"source":"public_tool_specs","count":0,"hash":"UNAVAILABLE","matches_canonical":true,"note":"vantage unavailable outside live server: 'types.SimpleNamespace' object is not subscriptable"},{"source":"tool_registry.json (arifosmcp)","count":9,"hash":"ea7fc3a794a5d363","matches_canonical":true,"declared_canonical_count":9}],"divergences":[]},"floors_active":13,"floors_enforcement":"active","runtime_floors":{"F1":0.5,"F2":0.99,"F3":0.75,"F4":-0.0,"F5":1.0,"F6":0.7,"F7":0.04,"F8":0.8,"F9":0.0,"L10":1.0,"L11":1.0,"L12":0.425,"L13":1.0},"tool_registry_hash":"0000915bf305bcbf","registry_truth":"VERIFIED","schema_hash":"8d303c886d9d6ea5","contract_status":{"tool_count":9,"input_schemas_published":9,"output_schemas_published":9,"descriptions_published":9,"schemas_complete":true,"contract_drift":false},"contract_drift":false,"runtime_drift":true,"runtime_matches_build":false,"build_commit":"c6fa7a5","live_commit":"9fe4982","git_dirty":null,"graphiti_enabled":true,"token_pressure":{"phase":"1.A — telemetry only","autonomous_compaction_enabled":false,"default_action":"observe_only","global":{"total_tokens_used":0,"active_sessions":0,"ts_utc":"2026-07-05T02:00:37.106632+00:00","note":"Per-session snapshots via token_pressure.snapshot(session_id)"},"advisory":"Token pressure telemetry is LIVE (Phase 1). Auto-compaction is DISABLED by default. F8+F13 sovereign to enable Phase 2 trigger."},"final_authority":"ARIF","vault999_health":"healthy","agent_id":"arifos","identity_marker":"arifos-sovereign-runtime","identity_source":"identity.toml","boot_attestation":true,"langfuse_tracing":{"status":"ACTIVE","host":"https://jp.cloud.langfuse.com","public_key_prefix":"pk-lf-ff07b5...","traced_tools_count":13},"ml_floors":{"ml_floors_enabled":false,"ml_model_available":false,"ml_method":"heuristic","ml_runtime_ready":false,"ml_dependency_status":"disabled","ml_missing_dependencies":[],"ml_model_name":"sentence-transformers/all-MiniLM-L6-v2","ml_hold_reason":null,"ml_hold_state":"disabled"},"federation_epistemology":{"status":"enabled","subjects":0,"ledger_events":0,"bootstrap_events":0,"sources":["ledger","vault_bootstrap"],"witness_oracle":"active","belief_query":"active"},"semantic_readiness":{"graphiti_transport":"healthy","graphiti_storage":"healthy","graphiti_embedding_runtime":"disabled","graphiti_semantic_floor":"disabled"},"seal_readiness":{"vault999_health":"healthy","ack_irreversible_gate":"passable","hold_reasons_schema":"returns top-level reasons[] + next_safe_action","runtime_drift":true,"contract_drift":false,"graphiti_read":"healthy","semantic_floor":"disabled","langfuse_traces":"ACTIVE"},"known_gaps":[{"id":"runtime_drift","title":"Runtime drift: TRUE when local code diverges from production image","detail":"rebuild container to sync","severity":"warning","floors":["L10"]}],"capability_map":{"schema":"capability-map/v1","redaction_policy":"no_raw_credential_values","server_identity":{"continuity_signing":"configured","human_label":"server identity"},"credential_classes":{"server_identity":"configured","storage_access":"configured","provider_access":"partial","ops_controls":"partial"},"capabilities":{"governed_continuity":"enabled","vault_persistence":"enabled","vector_memory":"enabled","external_grounding":"enabled","model_provider_access":"enabled","local_model_runtime":"enabled","auto_deploy":"enabled"},"storage":{"vault_postgres":"configured","session_cache":"configured","vector_memory":"configured"},"providers":{"openai":"not_configured","anthropic":"configured","sea_lion":"configured","deepseek":"configured","google":"not_configured","openrouter":"not_configured","venice":"not_configured","ollama_local":"configured","minimax":"configured","brave":"configured","jina":"configured","perplexity":"configured","firecrawl":"configured","tavily":"configured","exa":"configured","browserless":"configured","ddgs_local":"configured"},"substrates":{"git":"configured","fetch":"configured","memory":"configured","time":"configured","filesystem":"configured","validation":{"everything":{"probe":"configured","protocol_smoke":"configured"}}},"ops":{"webhook_deploy":"configured","grafana_access":"configured","openclaw_restart":"configured","api_bearer_auth":"not_configured"},"notes":["Capability map is redacted by design. It reports what the server can do, never raw credential values.","Agents should reason from capability state and credential classes, not from private secrets/tokens/passwords."]},"provider_status":{"primary_provider":"sea_lion","sea_lion_configured":true,"sea_lion_healthy":true,"ollama_configured":false,"ollama_healthy":false,"deterministic_fallback_available":true,"deterministic_fallback_used":false,"last_fallback_reason":null},"timestamp":"2026-07-05T02:00:38.070334+00:00","freshness":{"status":"fresh","checked_at_utc":"2026-07-05T02:00:38.070355+00:00","source_timestamp_utc":"2026-07-05T02:00:38.070357+00:00","age_seconds":0,"max_fresh_age_seconds":60,"stale_after_seconds":300,"expired_after_seconds":3600},"owner_summary":{"color":"YELLOW","reasons":["vault_healthy","runtime_or_contract_drift_detected"]},"source_commit":"c6fa7a5","source_repo":"https://github.com/ariffazil/arifOS","release_tag":"v2026.07.04-MARHIN","source_of_truth":{"doctrine":"https://github.com/ariffazil/arifOS","runtime":"/health and /tools on this server","canonical_index":"/.well-known/mcp/server.json"},"thermodynamic":{"entropy_delta":-0.0,"peace_squared":0.5,"vitality_index":0.5946,"echo_debt":0.0,"shadow":0.0,"confidence":0.99,"verdict":"SEAL","metabolic_stage":333,"witness":{"human":0.42,"ai":0.32,"earth":0.26}},"governance":{"tau_confidence_system":0.99,"tau_threshold_f2":0.99,"psi_vitality":0.5946,"peace_squared":0.5,"last_seal_timestamp":null,"laws_hard_active":["L01","L02","L04","L07","L09","L10","L11","L12","L13"],"floors_soft_doctrinal":["L03","L05","L06","L08"],"floors_derived_doctrinal":["L03","L08"],"floors_health_report":{"L01":"hard","L02":"hard","L03":"derived","L04":"hard","L05":"soft","L06":"soft","L07":"hard","L08":"derived","L09":"hard","L10":"hard","L11":"hard","L12":"hard","L13":"hard"},"sovereign_status":null,"sovereign_subject":null}}
```

Expected: `llm_tier: "ollama"`
Actual: `llm_tier: "unknown"`

## Constitutional Impact

**This is F13 SOVEREIGN violation (hidden).** If a real Tier 1+2 outage occurred,
system would hard-fail instead of degrading gracefully to Tier 3.

## Next Steps

1. **DO NOT re-enable Tier 1+2 until Tier 3 fixed.**
2. Investigate why Tier 3 failed:
   - Check Ollama status: `systemctl status ollama`
   - Check models: `ollama list`
   - Check port: `ss -tuln | grep 11434`
   - Check disk: `df -h`
   - Check logs: `journalctl -u ollama -n 100`
3. Fix root cause.
4. Re-run drill manually: `/root/arifOS/scripts/sovereignty_drill.sh`
5. Verify success (`llm_tier: "ollama"`) before restoring Tier 1+2.

## Timeline

- **2026-07-05T02:00:38+00:00:** Drill started
- **2026-07-05T02:00:38+00:00:** Tier 1+2 disabled via systemd override
- **2026-07-05T02:00:38+00:00:** arifOS restarted
- **2026-07-05T02:00:38+00:00:** Health check failed (llm_tier != "ollama")
- **2026-07-05T02:00:38+00:00:** Drill aborted, Tier 1+2 NOT restored

## Recovery

```bash
# After fixing Tier 3:
/root/arifOS/scripts/sovereignty_drill.sh

# If success, manually restore Tier 1+2:
rm /etc/systemd/system/arifos.service.d/sovereignty-drill-override.conf
systemctl daemon-reload
systemctl restart arifos
```

**Status:** Tier 1+2 remain disabled. System in manual-recovery mode.
