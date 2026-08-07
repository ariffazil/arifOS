"""
arifOS A-FORGE Index — The Causal Topology Map
═══════════════════════════════════════════════

Maps the A-FORGE execution layer — the hands of the organism.
Where arifOS governs truth and AAA governs identity, A-FORGE
governs causality. Every action path here changes reality.

The entropy is fundamentally different:
  arifOS   = Truth Entropy   → "Which truth is canonical?"
  AAA      = Identity Entropy → "Which actor is canonical?"
  A-FORGE  = Causal Entropy   → "Which action path is canonical?"

Causal entropy = Route + Bridge + Protocol + Automation + Deployment.
A-FORGE converts ambiguity directly into physical reality — deployments,
emails, notifications, infrastructure mutations. Highest risk per bit.

The organism:
  AAA      = Mind   (decision formation)
  arifOS   = Law    (decision authorization)
  A-FORGE  = Hands  (decision realization)
  VAULT999 = Witness (decision attestation)

DITEMPA BUKAN DIBERI. Forged by 333-AGI Δ MIND.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from fastmcp import FastMCP

AFORGE_STATS: dict[str, Any] = {
    "execution_entry_points": {
        "bridges": 5,
        "gateways": 1,
        "mcp_tools": 114,
        "apa_adapters": 8,
        "scripts": 60,
        "duties": 12,
        "deploy_paths": 5,
    },
    "total_execution_paths_estimated": 205,
    "test_files": 120,
    "governance_files_estimated": 80,
}

CRITICAL_FINDINGS = [
    {
        "id": "CF-AFX-01",
        "title": "Multiple execution paths to same outcome — causal ambiguity",
        "planes": ["routes"],
        "severity": "CRITICAL",
        "description": "The same capability (e.g., GitHub action, email send, deployment) is reachable through 4-5 different paths: MCP tools, APA adapters, bridges, scripts, and duties. Each path has different governance, error handling, and authentication. This is causal entropy — the organism can pull in different directions simultaneously.",
        "remediation": "Capability registry → single authoritative description per capability. Bridges/adapters are views, not independent implementations.",
        "paradox": "P05-order-chaos — many paths, one outcome",
        "paradox_zone": "mind",
    },
    {
        "id": "CF-AFX-02",
        "title": "Bridge explosion — N² interaction growth",
        "planes": ["routes"],
        "severity": "HIGH",
        "description": "5 bridges (calendar, email, github, telegram, ntfy) plus composio adapter create N² interaction complexity. Each bridge carries translation logic, error handling, auth. Entropy grows faster than linearly with each new external surface.",
        "remediation": "Bridge registry — single protocol per external surface. New bridges require governance review.",
        "paradox": "P11-individual-collective — bridge as individual path vs federation as collective",
        "paradox_zone": "contour",
    },
    {
        "id": "CF-AFX-03",
        "title": "Duties as persistent actors — execution metabolism",
        "planes": ["duties"],
        "severity": "HIGH",
        "description": "duties/ contains autonomic agents (recovery, drift scanner, vitality pulse, constitutional sync). Unlike tools (invoked), duties persist. This creates execution metabolism entropy — who started it, who stops it, who owns its state.",
        "remediation": "Duty registry — lifecycle contract per duty. systemd unit for each. Ownership documented.",
        "paradox": "P10-conservation-change — persistent duty vs transient tool",
        "paradox_zone": "memory",
    },
    {
        "id": "CF-AFX-04",
        "title": "Protocol overlap — same destination, different protocols",
        "planes": ["contracts"],
        "severity": "MEDIUM",
        "description": "MCP, A2A, APA, bridges, and raw scripts can all reach the same external services. Protocol overlap means governance must be enforced at multiple layers. A bad action through one protocol bypasses governance on another.",
        "remediation": "Single governance gateway for all outbound execution. Protocols are transports, not authorities.",
        "paradox": "P09-layer-collapse — protocol as governance vs protocol as transport",
        "paradox_zone": "contour",
    },
    {
        "id": "CF-AFX-05",
        "title": "Deployment entropy — desired state vs actual state drift",
        "planes": ["deploy"],
        "severity": "HIGH",
        "description": "5+ deployment surfaces (docker-compose, systemd, deploy scripts, caddy, prometheus) create infrastructure-state entropy. The repo represents desired state; actual runtime inevitably drifts. No mechanism to detect and reconcile.",
        "remediation": "Single deployment manifest. Runtime reconciliation daemon. Drift = alert, not silent acceptance.",
        "paradox": "P03-truth-uncertainty — declared state vs actual state",
        "paradox_zone": "contour",
    },
]

PLANE_MAP = [
    {
        "plane": "routes",
        "name": "Execution Entry Points",
        "canonical_home": "src/interfaces/mcp/",
        "primitives": ["MCP tools", "bridges", "APA adapters", "gateways"],
        "current_locations": [
            "src/interfaces/mcp/ (CANONICAL MCP surface — 114 tools)",
            "bridges/ (5 bridges — calendar, email, github, telegram, ntfy)",
            "apa/ (8 APA adapters — composio, calendar, drive, github, gmail, reddit, sheets, telegram)",
            "gateways/ (constitutional gateway)",
        ],
        "cardinality": "205 estimated execution paths",
        "entropy": "CAUSAL_AMBIGUITY",
        "paradox": "P05-order-chaos — many paths, one outcome",
        "paradox_zone": "mind",
    },
    {
        "plane": "tools",
        "name": "Capability Surface",
        "canonical_home": "src/domain/governance/",
        "primitives": ["tool definitions", "action classifiers", "blast radius", "reversibility"],
        "current_locations": [
            "src/domain/governance/f1Amanah.ts through f9AntiHantu.ts (F1-F13 floor enforcement)",
            "src/infrastructure/tools/ (ToolRegistry, ShellTools, FileTools, SearchTools, etc.)",
            "a_think/affordances.yaml + organ_affordances.yaml (affordance declarations)",
            "contracts/tools.yaml (tool contracts)",
        ],
        "cardinality": "80+ governance files, 114+ MCP tools",
        "entropy": "CAPABILITY_DRIFT",
        "paradox": "P12-capability-authority — capability vs permission to use it",
        "paradox_zone": "judge",
    },
    {
        "plane": "contracts",
        "name": "Execution Contracts",
        "canonical_home": "contracts/",
        "primitives": ["tool contracts", "gateway contracts", "MCP surface", "protocol specs"],
        "current_locations": [
            "contracts/ (3 files — gateway-tools, mcp_surface, tools)",
            "a_think/affordances.yaml + organ_affordances.yaml",
            "proto/ (isomorphism maps, verdict canon, bridge, geox, surface)",
        ],
        "cardinality": "15+ contract files across 3 locations",
        "entropy": "PROTOCOL_OVERLAP",
        "paradox": "P19-story-structure — contract shape vs execution",
        "paradox_zone": "contour",
    },
    {
        "plane": "deploy",
        "name": "Deployment Surface",
        "canonical_home": "deploy/",
        "primitives": ["docker-compose", "systemd units", "Caddyfile", "prometheus configs"],
        "current_locations": [
            "deploy/ (docker-compose.yml, systemd/, caddy/, grafana/, prometheus/)",
            "deploy/af-forge/ (production docker-compose + nginx + SSL)",
            "infrastructure/forge-runner/Dockerfile",
            "systemd/apa-bridge@.service",
        ],
        "cardinality": "5+ deployment surfaces",
        "entropy": "INFRASTRUCTURE_STATE_DRIFT",
        "paradox": "P03-truth-uncertainty — declared state vs actual state",
        "paradox_zone": "contour",
    },
    {
        "plane": "duties",
        "name": "Autonomic Agents",
        "canonical_home": "duties/",
        "primitives": ["autonomic agents", "drift scanners", "vitality pulses", "recovery agents"],
        "current_locations": [
            "duties/ (12 duties — recovery, drift, vitality, sync, scan, notify, orchestrator)",
            "somatic/ (allostatic, coregulation, reflex executor, state-conditioned scars)",
        ],
        "cardinality": "12 duties + somatic engine",
        "entropy": "EXECUTION_METABOLISM",
        "paradox": "P10-conservation-change — persistent duty vs transient tool",
        "paradox_zone": "memory",
    },
    {
        "plane": "witness",
        "name": "Execution Evidence",
        "canonical_home": "VAULT999/",
        "primitives": ["outcome records", "receipts", "seal evidence", "tickets"],
        "current_locations": [
            "src/domain/engine/RunReporter.ts (execution reporting)",
            "src/domain/governance/ForgeSealService.ts (seal evidence)",
            "src/infrastructure/receipts/flowReceiptStore.ts (flow receipts)",
            "src/application/approval/ (ticket store, approval boundary)",
            "data/vault999_outbox/ (outbox records)",
        ],
        "cardinality": "6+ witness surfaces",
        "entropy": "WITNESS_SCATTER",
        "paradox": "P04-evidence-claim — execution record vs truth record",
        "paradox_zone": "judge",
    },
]

MIGRATION_RULES = [
    "1. Delete nothing. This is a map, not a migration.",
    "2. Resolve CF-AFX-01 first — capability registry as single source of truth per capability.",
    "3. Bridge registry — mandate single protocol per external surface.",
    "4. Duty registry — lifecycle contract + systemd ownership per autonomic agent.",
    "5. Single governance gateway — all outbound execution through one gate.",
    "6. Deployment reconciliation daemon — detect and alert on desired vs actual state drift.",
    "7. Witness consolidation — single evidence path: execution → receipt → VAULT999 seal.",
]


def build_aforge_index() -> str:
    content_hash = hashlib.sha256(
        json.dumps(
            {
                "findings": [f["id"] for f in CRITICAL_FINDINGS],
                "planes": [p["plane"] for p in PLANE_MAP],
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()
    generated_at = datetime.now(timezone.utc).isoformat()

    result = {
        "_meta": {
            "resource": "arifos://a-forge-index",
            "title": "arifOS A-FORGE Index — The Causal Topology Map",
            "description": "Maps A-FORGE execution layer: 205 execution paths, 5 bridges, 12 duties, 5 deploy surfaces. Causal entropy — the most dangerous kind.",
            "forged": generated_at,
            "forged_by": "333-AGI Δ MIND",
            "content_hash": content_hash,
            "generated_at": generated_at,
            "generator": "arifOS/arifosmcp/resources/aforge_index.py::build_aforge_index",
            "is_derived": False,
            "annotations": {
                "audience": ["assistant"],
                "priority": 0.9,
                "lastModified": generated_at,
            },
        },
        "entropy": AFORGE_STATS,
        "organism": {
            "description": "Four repositories, one organism. Each layer has its own entropy type.",
            "layers": {
                "AAA (mind)": {
                    "governs": "Cognition",
                    "question": "Who should think?",
                    "entropy_type": "Identity Entropy",
                    "failure_mode": "Cognitive drift",
                },
                "arifOS (law)": {
                    "governs": "Authority",
                    "question": "What is permitted?",
                    "entropy_type": "Truth Entropy",
                    "failure_mode": "Governance drift",
                },
                "A-FORGE (hands)": {
                    "governs": "Action",
                    "question": "How does reality change?",
                    "entropy_type": "Causal Entropy",
                    "failure_mode": "Action drift — CONVERTS ENTROPY INTO PHYSICAL REALITY",
                },
                "VAULT999 (witness)": {
                    "governs": "Evidence",
                    "question": "What actually happened?",
                    "entropy_type": "Attestation Entropy",
                    "failure_mode": "Witness gap",
                },
            },
            "escalation": "Wrong interpretation → Wrong thinker → Wrong action. Cost increases downward.",
        },
        "architecture": {
            "six_planes_aforge": {
                "routes": {
                    "description": "Execution entry points — WHERE action enters the organism",
                    "cardinality": "205 paths",
                    "entropy_type": "Causal ambiguity",
                    "risk": "Same destination, different paths = different governance per path",
                },
                "tools": {
                    "description": "Capability surface — WHAT actions are possible",
                    "cardinality": "114 tools, 80 gov files",
                    "entropy_type": "Capability drift",
                    "risk": "Tool exists, permission exists, but WHEN to use is scattered",
                },
                "contracts": {
                    "description": "Execution contracts — HOW actions are governed",
                    "cardinality": "15+ files, 3 locations",
                    "entropy_type": "Protocol overlap",
                    "risk": "Same action through different protocols bypasses governance",
                },
                "deploy": {
                    "description": "Deployment surface — WHERE code meets infrastructure",
                    "cardinality": "5+ surfaces",
                    "entropy_type": "Infrastructure-state drift",
                    "risk": "Desired state ≠ actual state. Silently accepted.",
                },
                "duties": {
                    "description": "Autonomic agents — WHAT persists and acts autonomously",
                    "cardinality": "12 duties",
                    "entropy_type": "Execution metabolism",
                    "risk": "Who started it? Who stops it? Who owns its state?",
                },
                "witness": {
                    "description": "Execution evidence — WHAT record is left behind",
                    "cardinality": "6+ surfaces",
                    "entropy_type": "Witness scatter",
                    "risk": "Multiple evidence paths → no single truth of what happened",
                },
            },
        },
        "critical_findings": CRITICAL_FINDINGS,
        "plane_map": PLANE_MAP,
        "migration_rules": MIGRATION_RULES,
    }

    return json.dumps(result, indent=2, ensure_ascii=False)


def register_aforge_index(mcp: FastMCP) -> list[str]:
    @mcp.resource(
        "arifos://a-forge-index",
        name="A-FORGE Causal Topology Index",
        mime_type="application/json",
        description="Causal topology map: 205 execution paths, 5 bridges, 12 duties, 5 deploy surfaces. The hands layer — where entropy becomes reality.",
    )
    def aforge_index() -> str:
        """A-FORGE Causal Topology Index — the hands layer's map.

        205 execution paths, 5 bridges creating N² complexity,
        12 autonomic duties, 5 deployment surfaces. Causal entropy
        — the most dangerous kind. Every error here changes reality.

        Migrate rule: delete nothing, alias second, deprecate last.
        """
        return build_aforge_index()

    return ["arifos://a-forge-index"]
