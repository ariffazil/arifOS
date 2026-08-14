"""
arifos://rrr — Resource Reality Resolution (RRR)
arifos://skill-health — Catalog-wide skill health
arifos://skill-drift/{name} — Per-skill drift check
════════════════════════════════════════════════

DITEMPA BUKAN DIBERI — Forged, Not Given.

RRR is a pure 111-SENSE function.
  RRR discovers.
  RRR does not think.
  RRR does not verify.
  RRR does not judge.

It answers only: "What reality must be sensed before interpretation begins?"

Doctrine (2026-08-15):
  Intent → RRR → Reality Snapshot → Capability → Skill → Action

  RRR returns resources.
  Capability returns possibilities.
  Skill returns interpretation.
  Seal returns legitimacy.

Schema: rrr/v1.0 (aligned with Copilot draft 2026-08-15)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastmcp import FastMCP

# ═════════════════════════════════════════════════════════════════════════════
# BOOT RESOURCES (always loaded, every intent)
# ═════════════════════════════════════════════════════════════════════════════

BOOT_RESOURCES: list[dict[str, str]] = [
    {"uri": "arifos://identity", "reason": "actor identity", "layer": "L1"},
    {"uri": "arifos://doctrine", "reason": "constitutional constraints", "layer": "L1"},
    {"uri": "arifos://bootstrap", "reason": "federation context", "layer": "L1"},
    {"uri": "arifos://carry-forward", "reason": "prior session state", "layer": "L1"},
    {"uri": "arifos://flow-state", "reason": "FQ metabolic pulse", "layer": "L1"},
    {"uri": "arifos://vitals", "reason": "organ health summary", "layer": "L1"},
]

# ═════════════════════════════════════════════════════════════════════════════
# RRR INTENT → RESOURCE MAP
# ═════════════════════════════════════════════════════════════════════════════

RRR_INTENT_MAP: list[dict[str, Any]] = [
    # ── Federation health ────────────────────────────────────────────────
    {
        "keywords": ["federation", "topology", "organ status", "system health"],
        "intent_class": "federation-health",
        "domain": "federation",
        "mode": "observe",
        "criticality": "low",
        "authority_required": False,
        "required": [
            {"uri": ":8088/health", "layer": "L2", "reason": "kernel health"},
            {"uri": ":7071/health", "layer": "L2", "reason": "A-FORGE health"},
            {"uri": ":8081/health", "layer": "L2", "reason": "GEOX health"},
            {"uri": ":18082/health", "layer": "L2", "reason": "WEALTH health"},
            {"uri": ":18083/health", "layer": "L2", "reason": "WELL health"},
            {"uri": ":3001/health", "layer": "L2", "reason": "AAA health"},
            {"uri": "arifos://skill-health", "layer": "L1", "reason": "skill catalog health"},
        ],
        "optional": [
            {"uri": ":7073/health", "layer": "L2", "reason": "arifFlow FQ"},
        ],
        "evidence_filesystem": [
            {"path": "/root/AAA/federation/organs.yaml", "layer": "L3"},
        ],
        "evidence_external": [
            {"source": "systemctl", "target": "status arifos.service", "layer": "L5"},
            {"source": "docker", "target": "compose ps", "layer": "L5"},
        ],
        "capabilities": ["federation.health", "drift.detection"],
        "skills": ["FORGE-federation-orchestrator", "ASI-drift-watch"],
        "tools": ["curl", "systemctl", "docker"],
        "constraints": ["F2_TRUTH", "F4_CLARITY"],
        "outputs_expected": ["organ_status", "drift_report", "health_summary"],
    },
    # ── Skill metabolism ─────────────────────────────────────────────────
    {
        "keywords": ["skill", "catalog", "skill health", "skill drift", "staleness"],
        "intent_class": "skill-metabolism",
        "domain": "aaa",
        "mode": "audit",
        "criticality": "low",
        "authority_required": False,
        "required": [
            {"uri": "arifos://skill-health", "layer": "L1", "reason": "catalog-wide health"},
        ],
        "optional": [],
        "evidence_filesystem": [
            {"path": "/root/AAA/skills/", "layer": "L3"},
        ],
        "evidence_vector": [
            {"collection": "arifos_skill_mesh", "layer": "L4"},
        ],
        "capabilities": ["skill.audit", "drift.detection"],
        "skills": ["AUDIT-skill-atlas", "AUDIT-recursive-audit", "AUDIT-drift-detector"],
        "tools": ["find", "stat"],
        "constraints": ["F2_TRUTH", "F7_HUMILITY"],
        "outputs_expected": ["skill_health_report", "drift_list", "ecology_summary"],
    },
    # ── GEOX domain ──────────────────────────────────────────────────────
    {
        "keywords": ["geox", "geox audit", "geox deployment", "earth", "seismic", "basin", "prospect", "well log", "petrophysics", "earth science"],
        "intent_class": "geox-domain",
        "domain": "geox",
        "mode": "compute",
        "criticality": "medium",
        "authority_required": False,
        "required": [
            {"uri": ":8081/health", "layer": "L2", "reason": "GEOX organ health"},
            {"uri": "arifos://vitals", "layer": "L1", "reason": "federation vitals"},
        ],
        "optional": [
            {"uri": "arifos://atlas333/paradox/list", "layer": "L1", "reason": "paradox context"},
            {"uri": "arifos://skill-drift/{skill_name}", "layer": "L1", "reason": "skill drift"},
        ],
        "evidence_filesystem": [
            {"path": "/root/AAA/federation/organs.yaml", "layer": "L3"},
        ],
        "evidence_vector": [
            {"collection": "geo_embeddings", "layer": "L4"},
        ],
        "evidence_external": [
            {"source": "git", "target": "GEOX repo", "layer": "L5"},
        ],
        "capabilities": ["geox.compute", "basin.analysis", "seismic.interpret"],
        "skills": ["geox-production-cockpit", "geological-artifact-rigor"],
        "tools": ["mcp__geox__*"],
        "constraints": ["F1_TRUTH", "F2_TRUTH", "F7_HUMILITY"],
        "outputs_expected": ["geox_report", "drift_report", "recommendations"],
    },
    # ── WEALTH domain ────────────────────────────────────────────────────
    {
        "keywords": ["wealth", "capital", "trading", "xauusd", "gold", "portfolio", "npv", "emv"],
        "intent_class": "wealth-domain",
        "domain": "wealth",
        "mode": "compute",
        "criticality": "medium",
        "authority_required": False,
        "required": [
            {"uri": ":18082/health", "layer": "L2", "reason": "WEALTH organ health"},
            {"uri": "arifos://vitals", "layer": "L1", "reason": "federation vitals"},
        ],
        "optional": [],
        "evidence_filesystem": [],
        "capabilities": ["wealth.compute", "capital.analysis", "risk.assessment"],
        "skills": ["XAUUSD-trading-stack", "wealth-claim-state"],
        "tools": ["mcp__wealth__*"],
        "constraints": ["F1_AMANAH", "F2_TRUTH", "F6_EMPATHY"],
        "outputs_expected": ["capital_report", "risk_assessment"],
    },
    # ── WELL domain ──────────────────────────────────────────────────────
    {
        "keywords": ["well", "vitality", "readiness", "homeostasis", "fatigue", "dignity", "sleep"],
        "intent_class": "well-domain",
        "domain": "well",
        "mode": "reflect",
        "criticality": "medium",
        "authority_required": False,
        "required": [
            {"uri": ":18083/health", "layer": "L2", "reason": "WELL organ health"},
            {"uri": "arifos://vitals", "layer": "L1", "reason": "federation vitals"},
        ],
        "optional": [],
        "capabilities": ["well.reflect", "vitality.assessment", "dignity.guard"],
        "skills": ["FORGE-well-boundary-repair", "FORGE-telemetry-watchdog"],
        "tools": ["mcp__well__*"],
        "constraints": ["F6_EMPATHY", "F9_ANTIHANTU"],
        "outputs_expected": ["vitality_report", "readiness_assessment"],
    },
    # ── A-FORGE execution ────────────────────────────────────────────────
    {
        "keywords": ["forge", "execute", "deploy", "build", "sandbox", "lease"],
        "intent_class": "forge-execution",
        "domain": "aforge",
        "mode": "mutate",
        "criticality": "high",
        "authority_required": True,
        "required": [
            {"uri": "arifos://seal-readiness", "layer": "L1", "reason": "vault seal state"},
            {"uri": ":7071/health", "layer": "L2", "reason": "A-FORGE health"},
            {"uri": "arifos://vitals", "layer": "L1", "reason": "federation vitals"},
        ],
        "optional": [
            {"uri": ":7072/health", "layer": "L2", "reason": "A-FORGE MCP"},
        ],
        "evidence_external": [
            {"source": "docker", "target": "compose ps", "layer": "L5"},
        ],
        "capabilities": ["forge.execute", "forge.deploy", "forge.sandbox"],
        "skills": ["FORGE-vps-docker", "FORGE-cicd-docker-deploy"],
        "tools": ["mcp__aforge__forge_execute", "mcp__aforge__forge_shell", "mcp__aforge__forge_docker"],
        "constraints": ["F1_AMANAH", "F2_TRUTH", "F13_SOVEREIGN"],
        "outputs_expected": ["execution_receipt", "deployment_report"],
    },
    # ── Audit / governance ───────────────────────────────────────────────
    {
        "keywords": ["audit", "drift", "constitutional", "floor check", "governance", "compliance"],
        "intent_class": "governance-audit",
        "domain": "federation",
        "mode": "audit",
        "criticality": "medium",
        "authority_required": False,
        "required": [
            {"uri": "arifos://floors", "layer": "L1", "reason": "constitutional floors"},
            {"uri": "arifos://seal-readiness", "layer": "L1", "reason": "seal state"},
            {"uri": "arifos://affordances", "layer": "L1", "reason": "tool risk classes"},
            {"uri": "arifos://skill-health", "layer": "L1", "reason": "skill catalog health"},
            {"uri": "arifos://vitals", "layer": "L1", "reason": "federation vitals"},
        ],
        "optional": [
            {"uri": "arifos://refusal-surface", "layer": "L1", "reason": "refusal taxonomy"},
        ],
        "evidence_filesystem": [
            {"path": "/root/AAA/governance/constitution.v41.json", "layer": "L3"},
            {"path": "/root/AAA/federation/organs.yaml", "layer": "L3"},
        ],
        "evidence_external": [
            {"source": "git", "target": "diff HEAD (all repos)", "layer": "L5"},
        ],
        "capabilities": ["governance.audit", "drift.detection", "floor.compliance"],
        "skills": [
            "apex_floor_check", "apex_audit_coverage_check",
            "ASI-drift-watch", "AUDIT-drift-detector", "AUDIT-repo-reality",
        ],
        "tools": ["curl", "git"],
        "constraints": ["F1_TRUTH", "F2_TRUTH", "F4_CLARITY", "F11_AUDIT"],
        "outputs_expected": ["compliance_report", "drift_list", "floor_status"],
    },
    # ── Web / infrastructure ─────────────────────────────────────────────
    {
        "keywords": ["site", "web", "caddy", "cloudflare", "tunnel", "ssl", "dns"],
        "intent_class": "web-infra",
        "domain": "infra",
        "mode": "observe",
        "criticality": "medium",
        "authority_required": False,
        "required": [
            {"uri": "arifos://vitals", "layer": "L1", "reason": "federation vitals"},
            {"uri": ":3001/health", "layer": "L2", "reason": "AAA cockpit"},
        ],
        "optional": [],
        "evidence_external": [
            {"source": "curl", "target": "https://arif-fazil.com", "layer": "L5"},
            {"source": "tailscale", "target": "status", "layer": "L5"},
        ],
        "capabilities": ["web.deploy", "infra.guard", "ssl.audit"],
        "skills": ["FORGE-agentic-web-builder", "FORGE-infra-guardian"],
        "tools": ["curl", "caddy", "tailscale"],
        "constraints": ["F1_AMANAH", "F11_AUDIT"],
        "outputs_expected": ["site_status", "ssl_report", "tunnel_health"],
    },
    # ── Memory / wisdom ──────────────────────────────────────────────────
    {
        "keywords": ["memory", "recall", "wisdom", "eureka", "atlas", "paradox", "quote"],
        "intent_class": "wisdom-memory",
        "domain": "federation",
        "mode": "recall",
        "criticality": "low",
        "authority_required": False,
        "required": [
            {"uri": "arifos://memory", "layer": "L1", "reason": "memory architecture"},
        ],
        "optional": [
            {"uri": "arifos://atlas333/index", "layer": "L1", "reason": "paradox index"},
            {"uri": "arifos://wisdom/quotes/all", "layer": "L1", "reason": "wisdom quotes"},
        ],
        "evidence_vector": [
            {"collection": "atlas333_eureka", "layer": "L4"},
        ],
        "capabilities": ["memory.recall", "wisdom.query", "atlas.browse"],
        "skills": ["memory-manage", "atlas333-cognitive-geometry", "AGI-dream-engine"],
        "tools": ["arif_memory"],
        "constraints": ["F2_TRUTH", "F7_HUMILITY"],
        "outputs_expected": ["memory_results", "wisdom_context"],
    },
    # ── GitHub / CI ──────────────────────────────────────────────────────
    {
        "keywords": ["github", "pr", "pull request", "issue", "commit", "ci", "actions"],
        "intent_class": "github-ops",
        "domain": "federation",
        "mode": "operate",
        "criticality": "low",
        "authority_required": False,
        "required": [],
        "optional": [],
        "evidence_external": [
            {"source": "git", "target": "status", "layer": "L5"},
            {"source": "git", "target": "log -n 5", "layer": "L5"},
            {"source": "gh", "target": "pr list", "layer": "L5"},
        ],
        "capabilities": ["github.prs", "github.issues", "ci.diagnose"],
        "skills": ["FORGE-github-ops", "FORGE-github-workflow", "FORGE-pr-review", "FORGE-ci-diagnose"],
        "tools": ["git", "gh"],
        "constraints": ["F1_AMANAH", "F11_AUDIT"],
        "outputs_expected": ["pr_status", "ci_report"],
    },
    # ── MCP / tool surface ───────────────────────────────────────────────
    {
        "keywords": ["mcp", "tool surface", "server", "probe", "smoke test"],
        "intent_class": "mcp-ops",
        "domain": "federation",
        "mode": "observe",
        "criticality": "low",
        "authority_required": False,
        "required": [
            {"uri": "arifos://schema", "layer": "L1", "reason": "tool schema"},
            {"uri": "arifos://affordances", "layer": "L1", "reason": "tool risk classes"},
            {"uri": "arifos://vitals", "layer": "L1", "reason": "tool registry status"},
        ],
        "optional": [],
        "capabilities": ["mcp.probe", "mcp.smoke_test", "surface.audit"],
        "skills": ["FORGE-mcp-ops", "FORGE-mcp-probe", "FORGE-mcp-smoke-test", "FORGE-mcp-lifeguard"],
        "tools": ["curl", "mcporter"],
        "constraints": ["F2_TRUTH"],
        "outputs_expected": ["mcp_status", "surface_report"],
    },
    # ── Security ─────────────────────────────────────────────────────────
    {
        "keywords": ["security", "secret", "token", "credential", "ssh", "key rotation"],
        "intent_class": "security-ops",
        "domain": "federation",
        "mode": "audit",
        "criticality": "high",
        "authority_required": True,
        "required": [
            {"uri": "arifos://refusal-surface", "layer": "L1", "reason": "refusal taxonomy"},
            {"uri": "arifos://vitals", "layer": "L1", "reason": "federation vitals"},
        ],
        "optional": [],
        "evidence_external": [
            {"source": "ss", "target": "-tlnp", "layer": "L5"},
        ],
        "capabilities": ["security.audit", "secret.hygiene", "token.rotation"],
        "skills": ["FORGE-secret-hygiene", "FORGE-telegram-audit"],
        "tools": ["ss", "grep"],
        "constraints": ["F1_AMANAH", "F12_RESILIENCE", "F13_SOVEREIGN"],
        "outputs_expected": ["security_report", "secret_age_list"],
    },
]

# ── Default fallback ─────────────────────────────────────────────────────
RRR_DEFAULT: dict[str, Any] = {
    "intent_class": "unknown",
    "domain": "unknown",
    "mode": "observe",
    "criticality": "low",
    "authority_required": False,
    "required": [
        {"uri": "arifos://vitals", "layer": "L1", "reason": "baseline health"},
        {"uri": "arifos://flow-state", "layer": "L1", "reason": "FQ pulse"},
    ],
    "optional": [],
    "capabilities": [],
    "skills": [],
    "tools": [],
    "constraints": ["F2_TRUTH"],
    "outputs_expected": [],
    "confidence": 0.0,
    "notice": "No intent match — returning default boot + vitals. "
              "Agent should probe reality directly.",
}


# ═════════════════════════════════════════════════════════════════════════════
# RRR RESOLVER
# ═════════════════════════════════════════════════════════════════════════════


def resolve_rrr(intent: str) -> dict[str, Any]:
    """Resolve intent to resource reality requirements.

    Pure 111-SENSE function. Does not think. Does not judge.
    Returns structured RRR receipt with boot/task/evidence/skill/tool layers.

    Matching: keyword substring, longest match wins.
    Schema: rrr/v1.0
    """
    intent_lower = intent.lower().strip()
    best_match: dict[str, Any] | None = None
    best_len = 0

    for entry in RRR_INTENT_MAP:
        for kw in entry.get("keywords", []):
            kw_lower = kw.lower()
            if kw_lower in intent_lower and len(kw_lower) > best_len:
                best_match = entry
                best_len = len(kw_lower)

    if best_match is None:
        return {
            "schema_version": "rrr/v1.0",
            "intent": intent,
            "resolved_at": datetime.now(UTC).isoformat(),
            "classification": {
                "intent_class": "unknown",
                "domain": "unknown",
                "mode": "observe",
                "criticality": "low",
                "authority_required": False,
            },
            "boot_resources": BOOT_RESOURCES,
            "task_resources": {
                "required": RRR_DEFAULT.get("required", []),
                "optional": RRR_DEFAULT.get("optional", []),
            },
            "evidence_sources": {"filesystem": [], "vector": [], "external": []},
            "candidate_capabilities": [],
            "candidate_skills": [],
            "toolchain": [],
            "constraints": ["F2_TRUTH"],
            "outputs_expected": [],
            "confidence": {"reality_coverage": 0.0},
            "receipt": {
                "rrr_id": f"RRR-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
                "resource_count": len(BOOT_RESOURCES) + len(RRR_DEFAULT.get("required", [])),
            },
            "notice": RRR_DEFAULT.get("notice", ""),
            "doctrine": (
                "RRR = Retrieve Reality Requirements. "
                "No intent match found — probe reality directly."
            ),
        }

    confidence = min(1.0, best_len / max(len(intent_lower), 1) + 0.3)

    # Count total resources for receipt
    resource_count = (
        len(BOOT_RESOURCES)
        + len(best_match.get("required", []))
        + len(best_match.get("optional", []))
    )

    return {
        "schema_version": "rrr/v1.0",
        "intent": intent,
        "resolved_at": datetime.now(UTC).isoformat(),
        "classification": {
            "intent_class": best_match.get("intent_class", "unknown"),
            "domain": best_match.get("domain", "unknown"),
            "mode": best_match.get("mode", "observe"),
            "criticality": best_match.get("criticality", "low"),
            "authority_required": best_match.get("authority_required", False),
        },
        "boot_resources": BOOT_RESOURCES,
        "task_resources": {
            "required": best_match.get("required", []),
            "optional": best_match.get("optional", []),
        },
        "evidence_sources": {
            "filesystem": best_match.get("evidence_filesystem", []),
            "vector": best_match.get("evidence_vector", []),
            "external": best_match.get("evidence_external", []),
        },
        "candidate_capabilities": best_match.get("capabilities", []),
        "candidate_skills": best_match.get("skills", []),
        "toolchain": best_match.get("tools", []),
        "constraints": best_match.get("constraints", []),
        "outputs_expected": best_match.get("outputs_expected", []),
        "confidence": {
            "reality_coverage": round(confidence, 2),
        },
        "receipt": {
            "rrr_id": f"RRR-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            "resource_count": resource_count,
        },
        "doctrine": (
            "RRR = Retrieve Reality Requirements. "
            "RRR discovers. RRR does not think. RRR does not judge. "
            "Reality chooses the skill. The skill should not choose reality."
        ),
    }


# ═════════════════════════════════════════════════════════════════════════════
# MCP RESOURCE REGISTRATION
# ═════════════════════════════════════════════════════════════════════════════


def register_rrr_resources(mcp: FastMCP) -> list[str]:
    """Register RRR + skill-health + skill-drift as MCP resources.

    3 resources added (2026-08-15):
      arifos://rrr/{intent}         — Resource Reality Resolution
      arifos://skill-health         — Catalog-wide skill health
      arifos://skill-drift/{name}   — Per-skill drift check
    """

    @mcp.resource(
        "arifos://rrr/{intent}",
        description=(
            "RRR — Resource Reality Resolution (schema rrr/v1.0). "
            "Pure 111-SENSE function. Given an intent, returns the minimum "
            "reality set required before interpretation begins: boot resources, "
            "task resources (required/optional), evidence sources (filesystem/"
            "vector/external), candidate capabilities, candidate skills, "
            "toolchain, constitutional constraints, and expected outputs. "
            "RRR discovers. RRR does not think. RRR does not judge."
        ),
    )
    def rrr_resource(intent: str) -> dict[str, Any]:
        """Resolve intent to resource reality requirements."""
        return resolve_rrr(intent)

    @mcp.resource(
        "arifos://skill-health",
        description=(
            "Catalog-wide skill health scan. Returns total/complete/stub/stale "
            "counts, health percentage, broken file references, and ecology "
            "state (HOT/WARM/COLD) from Qdrant. Dynamic — computed from live "
            "filesystem on each read."
        ),
    )
    def skill_health_resource() -> dict[str, Any]:
        """Return live skill catalog health."""
        try:
            from arifosmcp.tools.session_close_macro import probe_skill_health
            return probe_skill_health()
        except Exception as exc:  # noqa: BLE001
            return {"error": str(exc)[:200], "total": 0}

    @mcp.resource(
        "arifos://skill-drift/{skill_name}",
        description=(
            "Per-skill drift check. Verifies a skill's referenced file paths "
            "still exist, checks age and completeness. Returns drift_detected, "
            "broken_paths, age_days, completeness. Call after loading SKILL.md."
        ),
    )
    def skill_drift_resource(skill_name: str) -> dict[str, Any]:
        """Return drift report for a specific skill."""
        try:
            from arifosmcp.tools.session_close_macro import check_skill_drift
            return check_skill_drift(skill_name)
        except Exception as exc:  # noqa: BLE001
            return {"skill": skill_name, "error": str(exc)[:200], "drift_detected": True}

    return [
        "arifos://rrr/{intent}",
        "arifos://skill-health",
        "arifos://skill-drift/{skill_name}",
    ]


__all__ = [
    "register_rrr_resources",
    "resolve_rrr",
    "RRR_INTENT_MAP",
    "BOOT_RESOURCES",
    "RRR_DEFAULT",
]
