"""
arifOS Repository Atlas — ATLAS333 Cognitive Map
════════════════════════════════════════════════

Maps the 4,098 files across 589 directories into the 6-plane architecture.
Follows the same methodology as arifos://index for the resource namespace
but at repository scale. Every directory is classified by plane, entropy
signal, and paradox zone.

The geometry:
  - law/     → constitutional, immutable, amendment-only
  - state/   → runtime, volatile, per-call
  - surface/ → generated metadata, public-facing
  - identity/→ sovereign, agent cards, keys
  - method/  → operational, versioned
  - corpus/  → reference, append-only

Entropy signals:
  - CLEAN      → focused purpose, no overlap
  - SCATTERED  → multiple concerns mixed
  - DUPLICATE  → same concern handled elsewhere

Repos are namespaces at scale. The same entropy metric applies:
  H = redundancy (duplicate dirs) + grammar_variance + scatter_rate

DITEMPA BUKAN DIBERI. Forged by 333-AGI Δ MIND.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from fastmcp import FastMCP

# ── REPO ENTROPY BASELINE ──
REPO_STATS: dict[str, Any] = {
    "total_files": 4098,
    "total_directories": 589,
    "file_extensions": 65,
    "python_files": 2061,
    "markdown_files": 983,
    "json_files": 360,
    "depth_max": 9,
    "depth_2_files": 2238,
    "leaf_directories_pct": 76,
}

DUPLICATE_DIRECTORIES = {
    "kernel": 9,
    "memory": 8,
    "scripts": 6,
    "tests": 6,
    "contracts": 6,
    "core": 5,
    "governance": 5,
    "agents": 5,
    "arifos": 4,
    "registry": 4,
    "schemas": 4,
    "docs": 4,
    "federation": 4,
    "paradox": 4,
    "apps": 4,
}

# ── TOP-LEVEL DIRECTORY CLASSIFICATION ──
# Each entry: name, plane, entropy_signal, justification, overlaps_with
DIRECTORY_MAP: list[dict[str, Any]] = [
    # ═══ law/ — constitutional, immutable ═══
    {
        "name": "GENESIS/",
        "plane": "law",
        "entropy": "CLEAN",
        "files": 54,
        "justification": "Foundational CANON documents — FLOOR_TABLE.json, 000_KERNEL_CANON.md, F1-F13 definitions. Immutable constitutional root.",
        "overlaps": None,
        "paradox_zone": "judge",
        "paradox": "P12-capability-authority — who may amend the immutable",
    },
    {
        "name": "governance/",
        "plane": "law",
        "entropy": "CLEAN",
        "files": 4,
        "justification": "Amendment system, floors.json, authority.json, scar.json. Constitutional governance ratchets.",
        "overlaps": "Complementary to core/ (data vs code)",
        "paradox_zone": "judge",
        "paradox": "P06-stability-rigidity — governance ratchets",
    },
    {
        "name": "contracts/",
        "plane": "law",
        "entropy": "SCATTERED",
        "files": 42,
        "justification": "Machine-readable constitutional contracts. Contains its own schemas/ subdirectory (overlaps with top-level schemas/). Also contains runtime code (compiler.py).",
        "overlaps": "contracts/schemas/ vs schemas/",
        "paradox_zone": "contour",
        "paradox": "P19-story-structure — contract shape vs enactment",
    },
    {
        "name": "core/",
        "plane": "law",
        "entropy": "CLEAN",
        "files": 28,
        "justification": "Constitutional floor enforcement engine — laws.py, governance_kernel.py, judgment.py. Code implements what CANON declares.",
        "overlaps": "Complementary to GENESIS/ (code vs canon)",
        "paradox_zone": "judge",
        "paradox": "P33-self-governance — code enforcing code",
    },
    {
        "name": "schemas/",
        "plane": "law",
        "entropy": "DUPLICATE",
        "files": 9,
        "justification": "JSON schema contracts for receipts, vault events, evidence. DUPLICATE of contracts/schemas/.",
        "overlaps": "contracts/schemas/",
        "paradox_zone": "contour",
        "paradox": "P04-evidence-claim — schema as claim vs schema as evidence",
    },
    # ═══ state/ — runtime, volatile ═══
    {
        "name": "arifosmcp/",
        "plane": "state",
        "entropy": "CRITICALLY_SCATTERED",
        "files": 129,
        "justification": "Main MCP server runtime. 129 top-level entries, 400+ files in runtime/ alone. INTERNALLY MIRRORS the entire repo structure — has its own contracts/, core/, docs/, tests/, VAULT999/, schemas/, static/. The single largest structural entropy source.",
        "overlaps": "Mirrors: contracts/, core/, docs/, tests/, VAULT999/, schemas/, static/",
        "paradox_zone": "mind",
        "paradox": "P09-layer-collapse — runtime mirrors canon; P22-unity-diversity — one package, many identities",
    },
    {
        "name": "arifos/",
        "plane": "state",
        "entropy": "CLEAN",
        "files": 10,
        "justification": "Python subpackage — AAA, forge, identity, consent modules. Runtime library code.",
        "overlaps": "arifos/identity/ runtime vs identity.toml derelict",
        "paradox_zone": "memory",
        "paradox": "P02-remember-forget — stale identity pointer",
    },
    {
        "name": "config/",
        "plane": "state",
        "entropy": "CLEAN",
        "files": 8,
        "justification": "Runtime configuration — apexd.yaml, MCP client configs, sovereignty charter.",
        "overlaps": None,
        "paradox_zone": "mind",
        "paradox": "P15-local-global — per-client config vs federation config",
    },
    {
        "name": ".arifos/",
        "plane": "state",
        "entropy": "CLEAN",
        "files": 10,
        "justification": "Live runtime sessions, agent scripts, metrics — volatile session state.",
        "overlaps": None,
        "paradox_zone": "memory",
        "paradox": "P01-energy-entropy — session state as energy budget",
    },
    # ═══ surface/ — generated, public-facing ═══
    {
        "name": "static/",
        "plane": "surface",
        "entropy": "CLEAN",
        "files": 30,
        "justification": "Public surface — HTML, .well-known/, llms.txt, dashboards, MCP discovery index. Generated artifacts.",
        "overlaps": None,
        "paradox_zone": "contour",
        "paradox": "P20-name-shape — public name vs internal shape",
    },
    {
        "name": "federation/",
        "plane": "surface",
        "entropy": "CLEAN",
        "files": 2,
        "justification": "Federation tool manifest, GEOX topology — machine-readable organ registry.",
        "overlaps": None,
        "paradox_zone": "contour",
        "paradox": "P22-unity-diversity — one federation, many organs",
    },
    {
        "name": "dist/",
        "plane": "surface",
        "entropy": "CLEAN",
        "files": 5,
        "justification": "Generated distribution — .whl, .tar.gz. Build output, not source.",
        "overlaps": None,
        "paradox_zone": "mind",
        "paradox": "P16-open-closed — distribution vs source",
    },
    {
        "name": "build/",
        "plane": "surface",
        "entropy": "CLEAN",
        "files": 2,
        "justification": "Build output — ephemeral generation.",
        "overlaps": None,
        "paradox_zone": "mind",
        "paradox": "P16-open-closed — build vs source",
    },
    # ═══ identity/ — sovereign, rare ═══
    {
        "name": "identity.toml",
        "plane": "identity",
        "entropy": "DUPLICATE",
        "files": 1,
        "justification": "Derelict pointer — shows '/root/AAA/identity.toml' as canonical. FROZEN. Actual identity runtime in arifos/identity/.",
        "overlaps": "arifos/identity/",
        "paradox_zone": "memory",
        "paradox": "P02-remember-forget — stale pointer still top-level",
    },
    # ═══ method/ — operational, versioned ═══
    {
        "name": "scripts/",
        "plane": "method",
        "entropy": "CLEAN",
        "files": 71,
        "justification": "Operational scripts — deploy, vault verify, drift check, health probes, SOT cron.",
        "overlaps": None,
        "paradox_zone": "mind",
        "paradox": "P07-light-shadow — script as shadow of process",
    },
    {
        "name": "tests/",
        "plane": "method",
        "entropy": "CLEAN",
        "files": 225,
        "justification": "Comprehensive test suite — floors, governance, kernel, federation, adversarial. Operational verification.",
        "overlaps": "conformance/ (both verify behavior)",
        "paradox_zone": "judge",
        "paradox": "P32-certainty-uncertainty — tests prove, conformance verifies",
    },
    {
        "name": "deploy/",
        "plane": "method",
        "entropy": "CLEAN",
        "files": 28,
        "justification": "Deployment — Docker compose, systemd units, Caddyfile, bootstrap, prometheus.",
        "overlaps": None,
        "paradox_zone": "mind",
        "paradox": "P10-conservation-change — deploy changes vs state conservation",
    },
    {
        "name": "commands/",
        "plane": "method",
        "entropy": "CLEAN",
        "files": 8,
        "justification": "CLI commands — arif_exec.py, arif_run.py, operational protocol docs.",
        "overlaps": None,
        "paradox_zone": "mind",
        "paradox": "P05-order-chaos — command as ordered intent",
    },
    {
        "name": "skills/",
        "plane": "method",
        "entropy": "CLEAN",
        "files": 27,
        "justification": "Agent behavioral skill definitions — 50+ SKILL.md files, operational instructions.",
        "overlaps": None,
        "paradox_zone": "memory",
        "paradox": "P08-tradition-innovation — skills as institutional memory",
    },
    {
        "name": "conformance/",
        "plane": "method",
        "entropy": "DUPLICATE",
        "files": 6,
        "justification": "Conformance test harness — spec-gated verification. Conceptually overlaps with tests/.",
        "overlaps": "tests/ (both verify system behavior)",
        "paradox_zone": "judge",
        "paradox": "P32-certainty-uncertainty — spec conformance vs pragmatic testing",
    },
    {
        "name": "eval/",
        "plane": "method",
        "entropy": "CLEAN",
        "files": 5,
        "justification": "Model evaluation harness — scoring, agent adapters, HF governed intelligence.",
        "overlaps": None,
        "paradox_zone": "judge",
        "paradox": "P21-measurable-meaningful — eval metrics vs real capability",
    },
    {
        "name": "supabase/",
        "plane": "method",
        "entropy": "CLEAN",
        "files": 12,
        "justification": "Database migrations — SQL, triggers, config. Operational data layer.",
        "overlaps": None,
        "paradox_zone": "memory",
        "paradox": "P10-conservation-change — migrating schema vs preserving data",
    },
    {
        "name": ".github/",
        "plane": "method",
        "entropy": "CLEAN",
        "files": 30,
        "justification": "CI/CD workflows, issue templates, CODEOWNERS, copilot instructions.",
        "overlaps": None,
        "paradox_zone": "mind",
        "paradox": "P17-utility-truth — CI as utility, not truth",
    },
    # ═══ corpus/ — reference, append-only ═══
    {
        "name": "VAULT999/",
        "plane": "corpus",
        "entropy": "CLEAN",
        "files": 30,
        "justification": "Immutable sealed truth ledger — outcomes.jsonl (append-only), seal chain. The canonical hash-chained truth store.",
        "overlaps": None,
        "paradox_zone": "judge",
        "paradox": "P31-permanence-reversibility — seal as permanent commitment",
    },
    {
        "name": "docs/",
        "plane": "corpus",
        "entropy": "SCATTERED",
        "files": 189,
        "justification": "Comprehensive reference — architecture, ADRs, runbooks, guides, API docs. 189 files across multiple concerns.",
        "overlaps": "GENESIS/ (constitutional docs), memory/ (historical context)",
        "paradox_zone": "contour",
        "paradox": "P03-truth-uncertainty — documentation vs reality",
    },
    {
        "name": "memory/",
        "plane": "corpus",
        "entropy": "SCATTERED",
        "files": 8,
        "justification": "Dated session-memory files. Historical working memory. Some overlap with docs/ and VAULT999/.",
        "overlaps": "docs/, VAULT999/",
        "paradox_zone": "memory",
        "paradox": "P02-remember-forget — what to keep, what to archive",
    },
    {
        "name": "proof/",
        "plane": "corpus",
        "entropy": "DUPLICATE",
        "files": 4,
        "justification": "Acceptance manifests, proof epoch results. Overlaps with reports/ and VAULT999/ — three evidence homes.",
        "overlaps": "reports/, VAULT999/",
        "paradox_zone": "judge",
        "paradox": "P04-evidence-claim — proof as evidence, seal as truth",
    },
    {
        "name": "proposals/",
        "plane": "corpus",
        "entropy": "CLEAN",
        "files": 1,
        "justification": "Design proposals. Reference for design decisions.",
        "overlaps": None,
        "paradox_zone": "mind",
        "paradox": "P08-tradition-innovation — proposals as innovation seed",
    },
    {
        "name": "theory/",
        "plane": "corpus",
        "entropy": "CLEAN",
        "files": 2,
        "justification": "APEX theory reference documents.",
        "overlaps": None,
        "paradox_zone": "contour",
        "paradox": "P35-positive-closed — theory as closed system",
    },
    {
        "name": "okf/",
        "plane": "corpus",
        "entropy": "CLEAN",
        "files": 2,
        "justification": "Orthogonal Knowledge Framework — ATLAS333, APEX flow, type taxonomy, ZEN.",
        "overlaps": None,
        "paradox_zone": "contour",
        "paradox": "P13-doubt-decision — framework as decision scaffold",
    },
    {
        "name": "00_legacy_materials/",
        "plane": "corpus",
        "entropy": "CLEAN",
        "files": 1,
        "justification": "Archived legacy materials — historical, frozen.",
        "overlaps": None,
        "paradox_zone": "memory",
        "paradox": "P02-remember-forget — legacy as fossil record",
    },
]

CRITICAL_FINDINGS = [
    {
        "id": "CF-01",
        "title": "arifosmcp/ is the entropy hotspot",
        "description": "129 top-level entries, 400+ files in runtime/ alone. Internally mirrors the entire repo (has its own contracts/, core/, docs/, tests/, VAULT999/, schemas/, static/). This is the largest structural entropy source — a shadow hierarchy inside the runtime package.",
        "plane": "state",
        "paradox": "P09-layer-collapse",
        "severity": "CRITICAL",
        "remediation": "Flatten mirror: remove internal duplicates, reference top-level sources by path or import.",
    },
    {
        "id": "CF-02",
        "title": "schemas/ vs contracts/schemas/ — two schema homes",
        "description": "JSON data contracts live in two places. Top-level schemas/ has 9 files; contracts/schemas/ has 5. Same purpose, different locations.",
        "plane": "law",
        "paradox": "P04-evidence-claim",
        "severity": "HIGH",
        "remediation": "Merge into contracts/schemas/ as canonical. Deprecate top-level schemas/.",
    },
    {
        "id": "CF-03",
        "title": "conformance/ vs tests/ — two verification surfaces",
        "description": "Both verify system behavior. tests/ is broad and pragmatic; conformance/ is spec-gated. Functional overlap.",
        "plane": "method",
        "paradox": "P32-certainty-uncertainty",
        "severity": "MEDIUM",
        "remediation": "Move conformance/ under tests/conformance/. Single test root.",
    },
    {
        "id": "CF-04",
        "title": "proof/ vs reports/ vs VAULT999/ — three evidence homes",
        "description": "Three places where evidentiary output lands. proof/ has acceptance manifests, reports/ has JSON scorecards, VAULT999/ has canonical sealed truth. Hierarchy unclear.",
        "plane": "corpus",
        "paradox": "P04-evidence-claim",
        "severity": "HIGH",
        "remediation": "VAULT999/ = canonical sealed truth (append-only). reports/ = generated summaries (derived, deletable). proof/ → merge into VAULT999/.",
    },
    {
        "id": "CF-05",
        "title": "identity.toml — derelict pointer",
        "description": "Stale pointer to /root/AAA/identity.toml. FROZEN. Actual identity runtime lives in arifos/identity/. No clean top-level identity plane — identity embedded in state with stale law file at top.",
        "plane": "identity",
        "paradox": "P02-remember-forget",
        "severity": "MEDIUM",
        "remediation": "Replace with symlink. Add README explaining 'identity belongs to AAA, this is a pointer.'",
    },
]


def build_atlas() -> str:
    """Assemble the repository cognitive atlas."""
    import math

    total_dirs = len(DIRECTORY_MAP)

    # Plane distribution
    plane_dist: dict[str, int] = {}
    for d in DIRECTORY_MAP:
        plane_dist[d["plane"]] = plane_dist.get(d["plane"], 0) + 1

    # Entropy signals
    signal_dist: dict[str, int] = {}
    for d in DIRECTORY_MAP:
        signal_dist[d["entropy"]] = signal_dist.get(d["entropy"], 0) + 1

    # Critical findings severity
    severity_dist: dict[str, int] = {}
    for f in CRITICAL_FINDINGS:
        severity_dist[f["severity"]] = severity_dist.get(f["severity"], 0) + 1

    # Attestation
    stable_payload = json.dumps(
        {
            "directories": [d["name"] for d in DIRECTORY_MAP],
            "findings": [f["id"] for f in CRITICAL_FINDINGS],
        },
        sort_keys=True,
    )
    content_hash = hashlib.sha256(stable_payload.encode()).hexdigest()
    generated_at = datetime.now(timezone.utc).isoformat()

    result = {
        "_meta": {
            "resource": "arifos://atlas-repo",
            "title": "arifOS Repository Atlas — ATLAS333 Cognitive Map",
            "description": "4,098 files, 589 directories classified into 6-plane architecture. 5 critical findings. 170 duplicate directory instances. Entropy signals per directory.",
            "forged": generated_at,
            "forged_by": "333-AGI Δ MIND",
            "content_hash": content_hash,
            "generated_at": generated_at,
            "generator": "arifOS/arifosmcp/resources/atlas_repo.py::build_atlas",
            "is_derived": False,
            "annotations": {
                "audience": ["assistant"],
                "priority": 0.9,
                "lastModified": generated_at,
            },
        },
        "repo_stats": REPO_STATS,
        "entropy": {
            "duplicate_directory_instances": 170,
            "top_duplicates": dict(sorted(DUPLICATE_DIRECTORIES.items(), key=lambda x: -x[1])[:10]),
            "plane_distribution": {
                "law": plane_dist.get("law", 0),
                "state": plane_dist.get("state", 0),
                "surface": plane_dist.get("surface", 0),
                "identity": plane_dist.get("identity", 0),
                "method": plane_dist.get("method", 0),
                "corpus": plane_dist.get("corpus", 0),
            },
            "entropy_signals": signal_dist,
            "critical_finding_severity": severity_dist,
        },
        "critical_findings": CRITICAL_FINDINGS,
        "directory_map": DIRECTORY_MAP,
        "migration_rules": [
            "1. Delete nothing. This is a map, not a migration.",
            "2. Resolve CF-01 first (arifosmcp/ mirror) — highest entropy reduction.",
            "3. Merge schemas/ → contracts/schemas/ (CF-02).",
            "4. Move conformance/ → tests/conformance/ (CF-03).",
            "5. Consolidate proof/ + reports/ → VAULT999/ + reports/ with clear hierarchy (CF-04).",
            "6. Fix identity.toml → pointer or symlink (CF-05).",
            "7. After CF-01 resolved: apply 6-plane directory structure.",
        ],
        "6_plane_proposed": {
            "law": ["GENESIS/", "governance/", "contracts/", "core/"],
            "state": ["arifosmcp/", "arifos/", "config/", ".arifos/", "var/", "logs/"],
            "surface": ["static/", "federation/", "dist/", "build/"],
            "identity": ["identity.toml → pointer"],  # identity lives in AAA
            "method": [
                "scripts/",
                "tests/",
                "deploy/",
                "commands/",
                "skills/",
                "eval/",
                "supabase/",
                ".github/",
                ".agents/",
            ],
            "corpus": ["VAULT999/", "docs/", "memory/", "audits/", "proposals/", "theory/", "okf/"],
        },
    }

    return json.dumps(result, indent=2, ensure_ascii=False)


def register_atlas_repo(mcp: FastMCP) -> list[str]:
    """Register arifos://atlas-repo — the ATLAS333 repository cognitive map."""

    @mcp.resource(
        "arifos://atlas-repo",
        name="arifOS Repository Atlas",
        mime_type="application/json",
        description="ATLAS333 cognitive map: 4,098 files, 589 directories, 6-plane classification, 5 critical findings, 170 duplicate directory instances.",
    )
    def atlas_repo() -> str:
        """arifOS Repository Atlas — ATLAS333-style cognitive map.

        Maps every top-level directory into the 6-plane architecture
        (law/state/surface/identity/method/corpus). Identifies 5 critical
        entropy findings with remediation paths.

        This is a cognitive map, not a migration — delete nothing.
        """
        return build_atlas()

    return ["arifos://atlas-repo"]
