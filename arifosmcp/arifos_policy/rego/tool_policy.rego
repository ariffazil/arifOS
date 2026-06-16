# Tool Authority Policy
#
# Purpose: Authorize a tool call based on tool's lane, action class, and resource.
# Used by: arif_kernel_route() and every tool dispatcher.
# F8 LAW: No tool is invoked without a positive OPA verdict + arifOS authority.

package arifos.tool

import future.keywords.if
import future.keywords.in

default allow = false
default deny  = false
default sabar = true

# Tool lanes (mirror GEOX.yaml §3 four-lane discipline)
# Note: explicit set membership per tool to avoid Rego recursion.
discovery_tools := {"system_registry_status", "organ_attest", "ping", "version", "system_status", "health_check", "registry_status", "13_signal_coverage", "assess_reliability", "trace_lineage", "validate_vitality"}
evidence_tools := {"data_ingest", "data_qc", "evidence_discover", "header_inspect", "las_inspect", "segy_inspect", "fault_stick_ingest", "dst_ingest", "data_ingest_bundle", "evidence_attach", "lithology", "scan_las", "basin_resolve", "basin_profile", "query_intake", "attribute_registry_list"}
reasoning_tools := {"seismic_compute", "horizon_contrast", "subsurface_generate", "claim_create", "claim_validate", "claim_challenge", "abduction", "claim_seal", "anomalous_contrast", "waveform_compute", "subsurface_verify_integrity", "evidence_reason", "vision_calibrate", "vision_perceptual_inventory", "vision_audit", "data_qc_bundle", "horizon_contrast_surface", "blockspace_resolution", "coord_transform", "map_context_scene", "seismic_segy_inspect", "seismic_compute_attribute", "blend_volume", "volume_frame", "sequence_interpret"}
judgment_tools := {"claim_validate", "claim_seal", "judge_deliberate", "vault_seal", "forge_execute", "heart_critique", "conformance_report", "vault_query", "mcp_registry_audit"}
wealth_calculate_tools := {"npv", "irr", "dscr", "conservation", "flow", "entropy", "gradient", "time_discount", "energy", "inertia", "field", "signal", "game", "boundary", "omni_wisdom", "agent_path", "entropy_risk", "flow_liquidity", "gradient_price", "energy_productivity", "inequality_kernel", "inertia_leverage", "field_macro", "signal_information", "game_coordination", "boundary_governance", "governance_verdict", "personal_finance", "survival_engine", "stock_analysis", "market_data", "wealth_calculate"}
wealth_audit_tools := {"stock_analysis", "pre_trade", "fundamentals", "verify_math", "position_size", "bursa_evidence", "bursa_snapshot", "bursa_screen", "bursa_cost", "tamak_check", "tac9", "contrast", "confluence", "separate_pl", "r_multiple", "exposure", "wealth_audit"}
well_measure_tools := {"assess_homeostasis", "assess_metabolism", "assess_livelihood", "validate_vitality", "guard_dignity", "measure_gradient", "classify_substrate", "detect_boundary", "compute_metabolic_flux", "medical_boundary", "well_measure"}
weave_orchestrate_tools := {"kernel_route", "gateway_connect", "session_init", "memory_recall", "mind_reason", "reply_compose", "evidence_fetch", "sense_observe", "ops_measure", "forge_plan", "forge_dry_run", "forge_query", "lease_issue", "lease_inspect", "lease_revoke", "system_status", "vault_query", "epistemic_check", "fact_check", "plan_review", "memory_steward", "cross_verify", "weave_orchestrate"}

# Helper: determine lane via set membership
is_discovery(t) if t in discovery_tools
is_evidence(t) if t in evidence_tools
is_reasoning(t) if t in reasoning_tools
is_judgment(t) if t in judgment_tools
is_wealth_calculate(t) if t in wealth_calculate_tools
is_wealth_audit(t) if t in wealth_audit_tools
is_well_measure(t) if t in well_measure_tools
is_weave_orchestrate(t) if t in weave_orchestrate_tools

is_unknown(t) if {
    not is_discovery(t)
    not is_evidence(t)
    not is_reasoning(t)
    not is_judgment(t)
    not is_wealth_calculate(t)
    not is_wealth_audit(t)
    not is_well_measure(t)
    not is_weave_orchestrate(t)
}

# Discovery and evidence lanes: any actor with session
allow if {
    is_discovery(input.tool)
    input.session_id != ""
}

allow if {
    is_evidence(input.tool)
    input.session_id != ""
}

# Reasoning and calculate lanes: require non-empty actor + non-empty session
allow if {
    is_reasoning(input.tool)
    input.actor_id != ""
    input.session_id != ""
}

allow if {
    is_wealth_calculate(input.tool)
    input.actor_id != ""
    input.session_id != ""
}

allow if {
    is_well_measure(input.tool)
    input.actor_id != ""
    input.session_id != ""
}

# Judgment, audit, orchestrate lanes: require sovereign OR governance actor
allow if {
    is_judgment(input.tool)
    input.actor_id in {"arif", "FORGE", "HERMES", "APEX"}
    input.session_id != ""
}

allow if {
    is_wealth_audit(input.tool)
    input.actor_id in {"arif", "FORGE", "HERMES", "APEX"}
    input.session_id != ""
}

allow if {
    is_weave_orchestrate(input.tool)
    input.actor_id in {"arif", "FORGE", "HERMES", "APEX"}
    input.session_id != ""
}

# Unknown tools: always SABAR (default)
sabar if is_unknown(input.tool)

deny if {
    not allow
    not sabar
}

override := true   # arifOS sovereign override is always available

confidence := 0.90 if allow

confidence := 0.80 if {
    not allow
    deny
}

confidence := 0.60 if {
    not allow
    not deny
}
