"""
BOOTSTRAP SKILL: arif_bootstrap_agent_context
==============================================
Forged: 2026-06-14 by FORGE (000Ω)
Target: arifOS core/skills/bootstrap.py
Purpose: Given a role name, returns the canonical reading pack and tool list
         so any agent can self-configure in one call.

Usage:
    context = bootstrap_agent_context("kernel-scribe")
    # Returns: { canonical_files: [...], summaries: {...}, tools: [...],
    #            autonomy: "PROPOSE_ONLY", risk_band: "APPROVE_ONLY" }
"""

# ─── AGENT REGISTRY ────────────────────────────────────────────────
# Maps role_name → (config_dir, role_card_path, description)
AGENT_MAP = {
    "kernel-scribe": {
        "config_dir": "/root/AAA/agents/kernel-scribe",
        "role_card": "/root/AAA/agents/roles/KERNEL_SCRIBE.md",
        "description": "AI internal auditor — reads governance, detects anomalies, proposes constitutional refinements",
        "class": "C2",
        "autonomy": "PROPOSE_ONLY",
        "risk_band": "APPROVE_ONLY",
    },
    "ops-planner": {
        "config_dir": "/root/AAA/agents/ops-planner",
        "role_card": "/root/AAA/agents/roles/OPS_PLANNER.md",
        "description": "Multi-day operational planner — respects WELL (human energy) and WEALTH (capital)",
        "class": "C2",
        "autonomy": "PROPOSE_ONLY",
        "risk_band": "APPROVE_ONLY",
    },
    "self-forge-advisor": {
        "config_dir": "/root/AAA/agents/self-forge-advisor",
        "role_card": "/root/AAA/agents/roles/SELF_FORGE_ADVISOR.md",
        "description": "Self-improvement architect — reads code, finds entropy, proposes refactors",
        "class": "C3",
        "autonomy": "PROPOSE_ONLY",
        "risk_band": "APPROVE_ONLY",
    },
    "external-watcher": {
        "config_dir": "/root/AAA/agents/external-watcher",
        "role_card": "/root/AAA/agents/roles/EXTERNAL_WATCHER.md",
        "description": "Ecosystem sensor — monitors MCP, NATS, Temporal, Graphiti",
        "class": "C1",
        "autonomy": "OBSERVE_ONLY",
        "risk_band": "FULL_AUTO",
    },
}

# Canonical files every agent reads
CANONICAL_BASE = [
    "/root/forge_work/2026-06-14/INDEX.md",
    "/root/forge_work/2026-06-14/AGI_KERNEL_FORGE_PACK.md",
    "/root/AGENTS.md",
    "/root/AAA/AGENTS.md",
]

# Per-organ canonical files (agents that touch specific repos)
ORGAN_FILES = {
    "arifOS": [
        "/root/forge_work/2026-06-14/PER_ORGAN_PATTERNS/arifOS_KERNEL_PATTERNS.md",
        "/root/arifOS/core/skills/THREAT_SCORE_SPEC.md",
        "/root/arifOS/core/skills/SCENARIO_POLICY_SPEC.md",
        "/root/arifOS/core/skills/AUTONOMY_CALIBRATION_SPEC.md",
    ],
    "A-FORGE": [
        "/root/forge_work/2026-06-14/PER_ORGAN_PATTERNS/AFORGE_EXECUTION_PATTERNS.md",
        "/root/forge_work/2026-06-14/INFRA_TOOL_WRAPPERS_SPEC.md",
    ],
    "AAA": [
        "/root/forge_work/2026-06-14/PER_ORGAN_PATTERNS/AAA_CONTROL_PLANE_PATTERNS.md",
        "/root/AAA/wiki/playbook/OPERATOR_PLAYBOOK.md",
    ],
}

# Tool lists per role
ROLE_TOOLS = {
    "kernel-scribe": [
        "arif_memory_recall",
        "arif_sense_observe",
        "arif_threat_score",
        "arif_autonomy_calibrate",
        "arif_scenario_policy_eval",
        "arif_judge_deliberate",
        "arif_reply_compose",
        "arif_organ_attest_all",
    ],
    "ops-planner": [
        "well_assess_homeostasis",
        "well_validate_vitality",
        "wealth_conservation_capital",
        "wealth_flow_liquidity",
        "arif_mind_reason",
        "arif_organ_attest_all",
        "forge_plan",
    ],
    "self-forge-advisor": [
        "arif_sense_observe",
        "arif_memory_recall",
        "arif_threat_score",
        "forge_plan",
        "forge_dry_run",
        "forge_approve",
        "forge_execute",
        "arif_vault_seal",
        "arif_organ_attest_all",
    ],
    "external-watcher": [
        "arif_sense_observe",
        "arif_evidence_fetch",
        "arif_memory_recall",
        "arif_reply_compose",
    ],
}

# Forbidden actions per role
ROLE_FORBIDDEN = {
    "kernel-scribe": ["forge_execute", "arif_vault_seal", "systemctl restart", "docker stop"],
    "ops-planner": ["forge_execute", "arif_vault_seal"],
    "self-forge-advisor": [
        "direct git commit",
        "direct git push",
        "constitutional floor modification",
    ],
    "external-watcher": ["any forge tool", "any organ write", "PROPOSE", "MUTATE", "ATOMIC"],
}


def bootstrap_agent_context(role_name: str) -> dict:
    """
    Given a role name, return the complete agent context:
    - canonical files to read
    - per-file summaries
    - tool list
    - forbidden actions
    - autonomy mode and risk band
    - role description

    Args:
        role_name: One of: kernel-scribe, ops-planner, self-forge-advisor, external-watcher

    Returns:
        dict with keys: role, config_dir, description, class, autonomy, risk_band,
                        canonical_files, files_by_organ, tools, forbidden, summary
    """
    if role_name not in AGENT_MAP:
        return {
            "error": f"Unknown role: {role_name}",
            "available_roles": list(AGENT_MAP.keys()),
            "hint": "Try: kernel-scribe, ops-planner, self-forge-advisor, external-watcher",
        }

    agent = AGENT_MAP[role_name]

    # Build canonical file list
    canonical_files = list(CANONICAL_BASE)
    canonical_files.append(agent["role_card"])

    # Add per-organ files based on role
    if role_name in ("kernel-scribe", "self-forge-advisor"):
        canonical_files.extend(ORGAN_FILES["arifOS"])
    if role_name in ("self-forge-advisor",):
        canonical_files.extend(ORGAN_FILES["A-FORGE"])
    if role_name in ("kernel-scribe", "ops-planner", "external-watcher"):
        canonical_files.extend(ORGAN_FILES["AAA"])

    # Generate summaries
    summaries = {
        "INDEX.md": "Quick-lookup index for the AGI Kernel Forge Pack — 20+ external resources in 6 capability bands",
        "AGI_KERNEL_FORGE_PACK.md": "Full forge pack: 6-band reference library, tiered reading order, per-organ pattern map",
        "AGENTS.md (/root)": "Federation landing protocol — identity, constitutional floors, organ topology",
        "AGENTS.md (/root/AAA)": "AAA control plane rules — build/test/deploy, A2A gateway, HEXAGON agents",
        agent[
            "role_card"
        ]: f"Full role definition for {role_name}: identity, workflow, boundaries, self-assessment",
    }

    if role_name in ("kernel-scribe", "self-forge-advisor"):
        summaries["arifOS_KERNEL_PATTERNS.md"] = (
            "arifOS-specific pattern extraction: durability, middleware, memory, delegation"
        )
        summaries["THREAT_SCORE_SPEC.md"] = (
            "Threat & anomaly scoring skill spec: data model, algorithm, risk levels"
        )
        summaries["SCENARIO_POLICY_SPEC.md"] = (
            "Scenario policy engine: multi-organ DSL, 3 starter policies"
        )
        summaries["AUTONOMY_CALIBRATION_SPEC.md"] = (
            "Autonomy calibration: re-evaluate tool risk bands from observed behavior"
        )

    # Build context
    context = {
        "role": role_name,
        "config_dir": agent["config_dir"],
        "description": agent["description"],
        "class": agent["class"],
        "autonomy_mode": agent["autonomy"],
        "risk_band": agent["risk_band"],
        "canonical_files": canonical_files,
        "tools": ROLE_TOOLS.get(role_name, []),
        "forbidden_actions": ROLE_FORBIDDEN.get(role_name, []),
        "summaries": summaries,
        "bootstrap_command": (
            f"Read {', '.join(canonical_files[:3])} first. "
            f"Then read your role card: {agent['role_card']}. "
            f"Your tools: {', '.join(ROLE_TOOLS.get(role_name, []))}. "
            f"Your autonomy: {agent['autonomy']}. "
            f"Forbidden: {', '.join(ROLE_FORBIDDEN.get(role_name, [])[:3])}... "
            "Extract patterns, don't import frameworks. Forge under arifOS law."
        ),
    }

    return context


def list_all_roles() -> list[dict]:
    """Return summary of all available role agents."""
    return [
        {
            "role": name,
            "description": info["description"],
            "class": info["class"],
            "autonomy": info["autonomy"],
        }
        for name, info in AGENT_MAP.items()
    ]


# ─── SELF-TEST ────────────────────────────────────────────────────
if __name__ == "__main__":
    for role in AGENT_MAP:
        ctx = bootstrap_agent_context(role)
        assert "error" not in ctx, f"Failed for {role}: {ctx}"
        assert len(ctx["canonical_files"]) > 3, f"Too few files for {role}"
        assert len(ctx["tools"]) > 2, f"Too few tools for {role}"
        print(
            f"✅ {role}: {len(ctx['canonical_files'])} files, {len(ctx['tools'])} tools, {ctx['autonomy_mode']}"
        )
    print(f"\n{len(AGENT_MAP)} roles bootstrapped. DITEMPA BUKAN DIBERI.")
