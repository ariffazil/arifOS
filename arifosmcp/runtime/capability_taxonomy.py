"""
capability_taxonomy.py
═══════════════════════════════════════════════════════════════
Semantic capability taxonomy for arifOS lease scoping.

Maps every forge_* tool to a hierarchical capability path:
    capability:<domain>/<action>/<subcategory>

This allows lease scopes like:
    scope=["capability:fs/*", "capability:vault/read"]

instead of fragile tool-name patterns like:
    scope=["forge_filesystem:*", "forge_vault:*"]

ADR-002 (2026-08-04): Built from live probe of 114 A-FORGE tools.
One source of truth for the tool→capability mapping.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from typing import FrozenSet

# ── Capability domains ──────────────────────────────────────
# Top-level domains group related tools by purpose.

CAPABILITY_DOMAINS: dict[str, str] = {
    "filesystem": "Read/write/delete filesystem operations",
    "shell": "Shell command execution (dry-run + live)",
    "git": "Git operations — status, diff, commit, push",
    "github": "GitHub API — PRs, issues, file CRUD",
    "docker": "Docker container lifecycle",
    "database": "PostgreSQL queries and schema inspection",
    "fetch": "URL fetch, web search, documentation lookup",
    "browser": "Playwright browser automation",
    "vault": "VAULT999 immutable ledger read/write",
    "governance": "Constitutional checks, judge proxy, policy, kernel",
    "forge_meta": "Tool lifecycle — register, evaluate, witness, seal, scar, skill",
    "google": "Google Workspace — Drive, Gmail, Calendar, Sheets",
    "org_bridge": "Cross-organ bridges — WEALTH, WELL",
    "probe": "Health probes and site verification",
    "vps": "VPS management — services, ports, cron, journalctl, web_zen",
    "security": "Security scanning and drift detection",
    "execution": "Execution pipeline — reality loop, parallel, predict, stage",
    "cooling": "Cooling receipts and drift metabolization",
    "chart": "Data visualization and charting",
    "document": "Document intelligence — ingest, OCR, analysis",
    "monitoring": "WM stats, telemetry, model monitoring",
}

# ── Tool → capability mapping ───────────────────────────────
# Every forge_* tool is assigned a capability path.
# Format: "capability:<domain>/<action>[/<sub>]"
# Actions: read, write, delete, execute, manage, inspect, route

TOOL_CAPABILITY_MAP: dict[str, str] = {
    # ── filesystem ──────────────────────────────────────
    "forge_filesystem": "capability:filesystem/*",
    # ── shell ───────────────────────────────────────────
    "forge_shell": "capability:shell/execute",
    "forge_shell_dryrun": "capability:shell/dryrun",
    "forge_shell_alert_history": "capability:shell/inspect",
    "forge_shell_ledger": "capability:shell/inspect",
    "forge_shell_status": "capability:shell/inspect",
    # ── git ─────────────────────────────────────────────
    "forge_git": "capability:git/manage",
    "forge_git_commit": "capability:git/write",
    "forge_worktree": "capability:git/inspect",
    # ── github ──────────────────────────────────────────
    "forge_github": "capability:github/read",
    "forge_github_get_file": "capability:github/read",
    "forge_github_create_issue": "capability:github/write",
    "forge_github_create_or_update_file": "capability:github/write",
    # ── docker ──────────────────────────────────────────
    "forge_docker": "capability:docker/manage",
    # ── database ────────────────────────────────────────
    "forge_postgres": "capability:database/*",
    # ── fetch/search ────────────────────────────────────
    "forge_fetch": "capability:fetch/read",
    "forge_search": "capability:fetch/search",
    "forge_minimax_search": "capability:fetch/search",
    "forge_research": "capability:fetch/research",
    "forge_docs_lookup": "capability:fetch/docs",
    "forge_docsgpt": "capability:fetch/docs",
    # ── browser ─────────────────────────────────────────
    "forge_browser_navigate": "capability:browser/navigate",
    "forge_browser_click": "capability:browser/interact",
    "forge_browser_type": "capability:browser/interact",
    "forge_browser_evaluate_js": "capability:browser/execute",
    "forge_browser_extract_text": "capability:browser/read",
    "forge_browser_screenshot": "capability:browser/read",
    # ── vault ───────────────────────────────────────────
    "forge_vault": "capability:vault/*",
    # ── governance ──────────────────────────────────────
    "forge_check_governance": "capability:governance/check",
    "forge_heart_critique": "capability:governance/review",
    "forge_judge_proxy": "capability:governance/route",
    "forge_kernel": "capability:governance/route",
    "forge_policy": "capability:governance/manage",
    "forge_health_check": "capability:governance/inspect",
    "forge_session_init": "capability:governance/manage",
    # ── forge_meta (tool lifecycle) ─────────────────────
    "forge_register": "capability:forge_meta/register",
    "forge_evaluate": "capability:forge_meta/evaluate",
    "forge_witness": "capability:forge_meta/witness",
    "forge_seal": "capability:forge_meta/seal",
    "forge_scar": "capability:forge_meta/write",
    "forge_scar_scan": "capability:forge_meta/read",
    "forge_skill": "capability:forge_meta/generate",
    "forge_ephemeral": "capability:forge_meta/generate",
    "forge_synthesize": "capability:forge_meta/generate",
    "forge_stage": "capability:forge_meta/manage",
    "forge_tier_bind": "capability:forge_meta/manage",
    "forge_skillstore_read": "capability:forge_meta/read",
    "forge_skillstore_write": "capability:forge_meta/write",
    "forge_surface_audit": "capability:forge_meta/read",
    "forge_surface_guard": "capability:forge_meta/read",
    "forge_fingerprint_check": "capability:forge_meta/read",
    "forge_isomorphism_check": "capability:forge_meta/read",
    # ── google workspace ────────────────────────────────
    "forge_calendar": "capability:google/read",
    "forge_drive": "capability:google/read",
    "forge_gmail": "capability:google/*",
    "forge_sheets": "capability:google/read",
    "forge_send_confirm": "capability:google/write",
    "forge_transfer_confirm": "capability:google/write",
    # ── org bridges ─────────────────────────────────────
    "forge_wealth": "capability:org_bridge/route",
    "forge_well": "capability:org_bridge/route",
    # ── probe ───────────────────────────────────────────
    "forge_probe": "capability:probe/read",
    "forge_probe_site": "capability:probe/read",
    # ── vps management ──────────────────────────────────
    "forge_vps_cron": "capability:vps/read",
    "forge_vps_ports": "capability:vps/read",
    "forge_vps_services": "capability:vps/read",
    "forge_journalctl": "capability:vps/read",
    "forge_netdata_alarms": "capability:vps/read",
    "forge_netdata_metrics": "capability:vps/read",
    "forge_web_zen": "capability:vps/manage",
    # ── security ────────────────────────────────────────
    "forge_security_drift_scan": "capability:security/read",
    "forge_scan": "capability:security/read",
    # ── execution pipeline ──────────────────────────────
    "forge_execute": "capability:execution/manage",
    "forge_execute_sealed": "capability:execution/manage",
    "forge_pipeline_run": "capability:execution/manage",
    "forge_reality_loop": "capability:execution/manage",
    "forge_parallel": "capability:execution/orchestrate",
    "forge_parallel_cancel": "capability:execution/orchestrate",
    "forge_parallel_list": "capability:execution/read",
    "forge_parallel_status": "capability:execution/read",
    "forge_predict": "capability:execution/predict",
    "forge_job": "capability:execution/manage",
    "forge_abort": "capability:execution/manage",
    "forge_agent": "capability:execution/manage",
    "forge_lease": "capability:execution/manage",
    "forge_lock": "capability:execution/manage",
    "forge_status": "capability:execution/read",
    "forge_registry": "capability:execution/read",
    "forge_registry_status": "capability:execution/read",
    "forge_memory": "capability:execution/read",
    "forge_runtime_verify": "capability:execution/verify",
    "forge_verify_timeline": "capability:execution/verify",
    "forge_visual_qa": "capability:execution/verify",
    "forge_visual_seal": "capability:execution/seal",
    "forge_docket_prep": "capability:execution/manage",
    "forge_receipt_draft": "capability:execution/write",
    "forge_canonize": "capability:execution/write",
    "forge_apex_emd": "capability:execution/validate",
    "forge_apex_encode": "capability:execution/encode",
    "forge_apex_metabolize": "capability:execution/metabolize",
    "forge_apex_recompute": "capability:execution/recompute",
    "forge_apex_goal_status": "capability:execution/read",
    "forge_sandbox_run": "capability:execution/sandbox",
    "forge_sandbox_pause": "capability:execution/sandbox",
    "forge_sandbox_resume": "capability:execution/sandbox",
    "forge_sandbox_list_paused": "capability:execution/read",
    "forge_sandbox_auto_evict": "capability:execution/manage",
    # ── cooling ─────────────────────────────────────────
    "forge_cool_drift": "capability:cooling/write",
    "forge_cool_pattern": "capability:cooling/write",
    # ── chart ───────────────────────────────────────────
    "forge_chart": "capability:chart/generate",
    # ── document ────────────────────────────────────────
    "forge_document_ingest": "capability:document/read",
    # ── monitoring ──────────────────────────────────────
    "forge_wm_gaps": "capability:monitoring/read",
    "forge_wm_quality": "capability:monitoring/read",
    "forge_wm_stats": "capability:monitoring/read",
    "forge_entropy_sweep": "capability:monitoring/read",
    # ── code analysis ───────────────────────────────────
    # (forge_code_analysis, forge_skill_audit, forge_skill_scan
    #  are not in the live registry — reserved for future)
}

# ── Capability resolver ────────────────────────────────────


def resolve_capability(tool_name: str) -> str | None:
    """Map a tool name to its canonical capability path.

    Returns None if the tool is not in the taxonomy.
    """
    return TOOL_CAPABILITY_MAP.get(tool_name)


def resolve_tools_for_capability(
    capability_path: str,
    available_tools: FrozenSet[str] | None = None,
) -> list[str]:
    """Return all tool names that match a capability path.

    Supports wildcards:
        "capability:shell/*"      → all shell tools
        "capability:execution/*"  → all execution tools
        "capability:*"            → all tools in taxonomy
        "capability:*/read"       → all read-only tools across domains
        "capability:git/*"        → all git tools

    Args:
        capability_path: The capability scope entry to resolve.
        available_tools: Optional filter — only return tools in this set.

    Returns:
        List of matching tool names, sorted alphabetically.
    """
    if not capability_path.startswith("capability:"):
        return []

    # Parse: "capability:<domain>/<action>"
    path = capability_path[len("capability:") :]  # e.g. "shell/*" or "shell/execute"

    domain_part, _, action_part = path.partition("/")

    matches = []
    for tool, cap in TOOL_CAPABILITY_MAP.items():
        if available_tools is not None and tool not in available_tools:
            continue
        cap_domain, _, cap_action = cap[len("capability:") :].partition("/")

        # Domain matching
        if domain_part != "*" and domain_part != cap_domain:
            continue
        # Action matching
        if action_part not in ("*", "", cap_action):
            continue
        matches.append(tool)

    return sorted(matches)


def get_all_capability_domains() -> list[str]:
    """Return all known capability domains."""
    return sorted(CAPABILITY_DOMAINS.keys())


def get_capability_actions(domain: str) -> list[str]:
    """Return all actions used within a domain."""
    actions = set()
    prefix = f"capability:{domain}/"
    for cap in TOOL_CAPABILITY_MAP.values():
        if cap.startswith(prefix):
            action = cap[len(prefix) :]
            if "/" in action:
                action = action.split("/")[0]
            if action and action != "*":
                actions.add(action)
    return sorted(actions)


# ── Validation ──────────────────────────────────────────────


def validate_taxonomy_coverage(tool_names: list[str]) -> dict:
    """Check taxonomy coverage against a list of tool names.

    Returns:
        { "covered": [...], "missing": [...], "coverage_pct": float }
    """
    covered = [t for t in tool_names if t in TOOL_CAPABILITY_MAP]
    missing = [t for t in tool_names if t not in TOOL_CAPABILITY_MAP]
    pct = len(covered) / max(len(tool_names), 1) * 100
    return {
        "covered": sorted(covered),
        "missing": sorted(missing),
        "coverage_pct": round(pct, 1),
        "total_tools": len(tool_names),
    }
