# ARIFOS Proof Pack — 2026-06-14

## Health
{
    "status": "healthy",
    "identity_hash": {
        "algorithm": "BLAKE3",
        "source": "identity.toml",
        "b3_hash": "c01c70fdfa3c4dce9c1391c47fc4f4f685c854f782b52f761b9b2566ae24c4da",
        "b3_prefix": "c01c70fdfa3c4dce"
    },
    "service": "arifOS-mcp",
    "release_name": "v2026.05.05-SSCT",
    "version": "kanon-80beb5b",
    "git_commit": "80beb5b",
    "git_branch": "main",
    "build_time": "2026-06-14T14:24:51.335998+00:00",
    "image": "ghcr.io/ariffazil/arifos:80beb5b",
    "deployment_source": "ghcr",
    "transport": "streamable-http",
    "tools_loaded": 13,
    "floors_active": 13,
    "floors_enforcement": "active",
    "tool_registry_hash": "133a866abde558f5",
    "registry_truth": "VERIFIED",
    "schema_hash": "5134532d744bb230",
    "contract_status": {
        "tool_count": 18,
        "input_schemas_published": 18,
        "output_schemas_published": 18,
        "descriptions_published": 18,
        "schemas_complete": true,
        "contract_drift": false
    },
    "contract_drift": false,
    "runtime_drift": true,
    "runtime_matches_build": false,
    "build_commit": "80beb5b",
    "live_commit": "ded53aa",
    "git_dirty": null,
    "graphiti_enabled": true,
    "token_pressure": {
        "phase": "1.A \u2014 telemetry only",
        "autonomous_compaction_enabled": false,
        "default_action": "observe_only",
        "global": {
            "total_tokens_used": 0,
            "active_sessions": 0,
            "ts_utc": "2026-06-14T15:53:03.452933+00:00",
            "note": "Per-session snapshots via token_pressure.snapshot(session_id)"
        },
        "advisory": "Token pressure telemetry is LIVE (Phase 1). Auto-compaction is DISABLED by default. F8+F13 sovereign to enable Phase 2 trigger."
    },
    "final_authority": "ARIF",
    "vault999_health": "healthy",
    "agent_id": "arifos",
    "identity_marker": "arifos-sovereign-runtime",
    "identity_source": "identity.toml",
    "boot_attestation": true,
    "langfuse_tracing": {
        "status": "ACTIVE",
        "host": "https://jp.cloud.langfuse.com",
        "public_key_prefix": "pk-lf-ff07b5...",
        "traced_tools_count": 13
    },
    "ml_floors": {
        "ml_floors_enabled": true,
        "ml_model_available": true,
        "ml_method": "sbert",
        "ml_runtime_ready": true,
        "ml_dependency_status": "healthy",
        "ml_missing_dependencies": [],
        "ml_model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "ml_hold_reason": null,
        "ml_hold_state": "ready"
    },
    "federation_epistemology": {
        "status": "enabled",
        "subjects": 0,
        "ledger_events": 0,
        "bootstrap_events": 0,
        "sources": [
            "ledger",
            "vault_bootstrap"
        ],
        "witness_oracle": "active",
        "belief_query": "active"
    },
    "semantic_readiness": {
        "graphiti_transport": "healthy",
        "graphiti_storage": "healthy",
        "graphiti_embedding_runtime": "healthy",
        "graphiti_semantic_floor": "enabled"
    },
    "seal_readiness": {
        "vault999_health": "healthy",
        "ack_irreversible_gate": "passable",
        "hold_reasons_schema": "returns top-level reasons[] + next_safe_action",
        "runtime_drift": true,
        "contract_drift": false,
        "graphiti_read": "healthy",
        "semantic_floor": "enabled",
        "langfuse_traces": "ACTIVE"
    },
    "known_gaps": [
        {
            "id": "runtime_drift",
            "title": "Runtime drift: TRUE when local code diverges from production image",
            "detail": "rebuild container to sync",
            "severity": "warning",
            "floors": [
                "L10"
            ]
        }
    ],
    "capability_map": {
        "schema": "capability-map/v1",
        "redaction_policy": "no_raw_credential_values",
        "server_identity": {
            "continuity_signing": "configured",
            "human_label": "server identity"
        },
        "credential_classes": {
            "server_identity": "configured",
            "storage_access": "configured",
            "provider_access": "partial",
            "ops_controls": "partial"
        },
        "capabilities": {
            "governed_continuity": "enabled",
            "vault_persistence": "enabled",
            "vector_memory": "enabled",
            "external_grounding": "enabled",
            "model_provider_access": "enabled",
            "local_model_runtime": "enabled",
            "auto_deploy": "enabled"
        },
        "storage": {
            "vault_postgres": "configured",
            "session_cache": "configured",
            "vector_memory": "configured"
        },
        "providers": {
            "openai": "not_configured",
            "anthropic": "configured",
            "sea_lion": "configured",
            "deepseek": "configured",
            "google": "not_configured",
            "openrouter": "not_configured",
            "venice": "not_configured",
            "ollama_local": "configured",
            "minimax": "configured",
            "brave": "configured",
            "jina": "configured",
            "perplexity": "configured",
            "firecrawl": "configured",
            "tavily": "configured",
            "exa": "configured",
            "browserless": "configured",
            "ddgs_local": "configured"
        },
        "substrates": {
            "git": "configured",
            "fetch": "configured",
            "memory": "configured",
            "time": "configured",
            "filesystem": "configured",
            "validation": {
                "everything": {
                    "probe": "configured",
                    "protocol_smoke": "configured"
                }
            }
        },
        "ops": {
            "webhook_deploy": "configured",
            "grafana_access": "configured",
            "openclaw_restart": "configured",
            "api_bearer_auth": "not_configured"
        },
        "notes": [
            "Capability map is redacted by design. It reports what the server can do, never raw credential values.",
            "Agents should reason from capability state and credential classes, not from private secrets/tokens/passwords."
        ]
    },
    "provider_status": {
        "primary_provider": "sea_lion",
        "sea_lion_configured": true,
        "sea_lion_healthy": true,
        "ollama_configured": false,
        "ollama_healthy": false,
        "deterministic_fallback_available": true,
        "deterministic_fallback_used": false,
        "last_fallback_reason": null
    },
    "timestamp": "2026-06-14T15:53:04.460148+00:00",
    "freshness": {
        "status": "fresh",
        "checked_at_utc": "2026-06-14T15:53:04.460185+00:00",
        "source_timestamp_utc": "2026-06-14T15:53:04.460188+00:00",
        "age_seconds": 0,
        "max_fresh_age_seconds": 60,
        "stale_after_seconds": 300,
        "expired_after_seconds": 3600
    },
    "owner_summary": {
        "color": "YELLOW",
        "reasons": [
            "vault_healthy",
            "runtime_or_contract_drift_detected"
        ]
    },
    "source_commit": "80beb5b",
    "source_repo": "https://github.com/ariffazil/arifOS",
    "release_tag": "v2026.05.05-SSCT",
    "source_of_truth": {
        "doctrine": "https://github.com/ariffazil/arifOS",
        "runtime": "/health and /tools on this server",
        "canonical_index": "/.well-known/mcp/server.json"
    },
    "thermodynamic": {
        "entropy_delta": -0.0,
        "peace_squared": 0.5,
        "vitality_index": 0.5946,
        "echo_debt": 0.0,
        "shadow": 0.0,
        "confidence": 0.99,
        "verdict": "SEAL",
        "metabolic_stage": 333,
        "witness": {
            "human": 0.42,
            "ai": 0.32,
            "earth": 0.26
        }
    },
    "governance": {
        "tau_confidence_system": 0.99,
        "tau_threshold_f2": 0.99,
        "psi_vitality": 0.5946,
        "peace_squared": 0.5,
        "last_seal_timestamp": null,
        "laws_hard_active": [
            "L01",
            "L02",
            "L04",
            "L07",
            "L09",
            "L10",
            "L11",
            "L12",
            "L13"
        ],
        "floors_soft_doctrinal": [
            "L03",
            "L05",
            "L06",
            "L08"
        ],
        "floors_derived_doctrinal": [
            "L03",
            "L08"
        ],
        "floors_health_report": {
            "L01": "hard",
            "L02": "hard",
            "L03": "derived",
            "L04": "hard",
            "L05": "soft",
            "L06": "soft",
            "L07": "hard",
            "L08": "derived",
            "L09": "hard",
            "L10": "hard",
            "L11": "hard",
            "L12": "hard",
            "L13": "hard"
        },
        "sovereign_status": null,
        "sovereign_subject": null
    }
}

## Benchmark Score
**Score**: 10/10 (100%)

## Security Audit
(See security-audit output above)

## VAULT999 Chain
════════════════════════════════════════════════════════════
  VAULT999 Epoch Split Verification
  Ratified: 2026-06-02 | Authority: F13 SOVEREIGN
════════════════════════════════════════════════════════════

📜 v1 Ledger (Historical — FROZEN)
  ⚠️  Parse error in SEALED_EVENTS.jsonl: Expecting value: line 1 column 184 (char 183)
   Status:       FROZEN_HISTORICAL
   Entries:      1336
   Lineage breaks: 120
   Frozen:       True

🔗 v2 Ledger (Active)
   Status:       HEALTHY
   Entries:      2
   Genesis anchored: True
   Chain continuous: True

📦 Canonical Live Vault (vault999.jsonl)
   Status:       HEALTHY
