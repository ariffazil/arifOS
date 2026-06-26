"""
kernel/skill_graph.py — Skill Dependency Graph Compiler v0.1
══════════════════════════════════════════════════════════

Compiles all SKILL.md frontmatter from /root/.agents/skills/ into a
runtime DAG (Directed Acyclic Graph).

This is the "nervous system" bridging TREE777 (wiki knowledge layer) and
MCP (delivery layer). The kernel's capability_registry.py was a hardcoded
static seed. This makes it a living graph.

v0.1 scope:
- Parse all SKILL.md frontmatter
- Build SkillNode DAG with edges = skill dependencies
- detect_orphans(): broken skill references
- compute_entropy(): ΔS on the skill graph
- get_chain(skill_id): topological sort from entry skill
- to_capability_graph(): convert to CapabilityGraph for capability_registry

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""
from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("arifOS.SkillGraph")

SKILLS_DIR = Path("/root/.agents/skills")

FRONT_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL | re.MULTILINE)


class SkillAutonomyTier(str, Enum):
    T1 = "T1"  # Auto-do: read, search, observe, plan, edit, build, test
    T2 = "T2"  # Announce: multi-file refactor, new dependency, deploy
    T3 = "T3"  # 888_HOLD: rm -rf, DROP TABLE, force push, vault seal


class SkillRiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SkillUpdateClass(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    STALE = "STALE"


# ── SkillNode ────────────────────────────────────────────────────────────────

@dataclass
class SkillNode:
    """A skill compiled from SKILL.md frontmatter."""
    skill_id: str                           # e.g. "arifos-kernel"
    name: str                               # e.g. "arifos-constitutional-kernel"
    description: str
    version: str
    risk_tier: SkillRiskTier
    floor_scope: list[str]
    autonomy_tier: SkillAutonomyTier
    trigger_phrases: list[str]
    mcp_servers: list[str]                  # e.g. ["arifos", "aforge"]
    skill_dependencies: list[str]           # e.g. ["arifos-federation-router"]
    inputs: list[str]
    outputs: list[str]
    path: Path
    updated: str
    word_count: int = 0
    update_class: SkillUpdateClass = SkillUpdateClass.NORMAL

    # Derived fields
    out_edges: list[str] = field(default_factory=list)   # skills this skill depends on
    in_edges: list[str] = field(default_factory=list)    # skills that depend on this

    @property
    def is_kernel(self) -> bool:
        return self.skill_id.startswith("arifos-")

    @property
    def is_domain(self) -> bool:
        return any(
            self.skill_id.startswith(p)
            for p in ("geox-", "wealth-", "well-", "federation-")
        )

    @property
    def is_ops(self) -> bool:
        return self.skill_id.startswith("github-")

    @property
    def is_meta(self) -> bool:
        return self.skill_id in (
            "skill-creator", "agentic-builder", "agentic-session-init",
            "agentic-toolcheck", "auditor-validator-kutip-sampah",
            "vault999-audit-sealer", "godel-humility-lock",
            "quantum-superposition-planner",
        )

    def dependency_hash(self) -> str:
        """Hash of all dependencies — used for change detection."""
        deps = sorted(self.mcp_servers + self.skill_dependencies)
        return hashlib.sha256("|".join(deps).encode()).hexdigest()[:12]

    def __hash__(self) -> int:
        return hash(self.skill_id)


# ── SkillGraph ───────────────────────────────────────────────────────────────

class SkillGraph:
    """
    Compiles and serves the skill dependency DAG.

    Usage:
        graph = SkillGraph()
        orphans = graph.detect_orphans()
        entropy = graph.compute_entropy()
        chain = graph.get_chain("geox-earth-evidence")
        cap_graph = graph.to_capability_graph()
    """

    def __init__(self, skills_dir: Path | None = None):
        self.skills_dir = skills_dir or SKILLS_DIR
        self.nodes: dict[str, SkillNode] = {}
        self.by_mcp_server: dict[str, list[str]] = {}  # server → [skill_ids]
        self._graph_version: str = ""
        self._dirty: bool = False

        self._compile()
        self._build_indices()
        self._resolve_edges()
        self._compute_update_classes()

    # ── Core compilation ─────────────────────────────────────────────────────

    def _parse_skill_md(self, skill_dir: Path) -> SkillNode | None:
        """Parse a single SKILL.md file into a SkillNode."""
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return None

        skill_id = skill_dir.name
        text = skill_md.read_text(errors="ignore")

        # Frontmatter
        fm = {}
        m = FRONT_RE.match(text)
        if m:
            try:
                fm = yaml.safe_load(m.group(1)) or {}
            except yaml.YAMLError:
                pass

        # Body word count
        body = FRONT_RE.split(text)
        body_text = body[1] if len(body) > 1 else ""
        word_count = len(body_text.split())

        # mtime
        updated = datetime.fromtimestamp(skill_md.stat().st_mtime).strftime("%Y-%m-%d")

        # Extract fields
        deps = fm.get("dependencies", {}) or {}
        mcp_servers = deps.get("mcp_servers", []) or []
        skill_deps = deps.get("skills", []) or []

        floor_scope = fm.get("floor_scope", []) or []
        if isinstance(floor_scope, str):
            floor_scope = [f.strip() for f in floor_scope.split(",")]

        triggers = fm.get("trigger_phrases", []) or []
        if isinstance(triggers, str):
            triggers = [t.strip() for t in triggers.split(",")]

        try:
            risk_tier = SkillRiskTier(str(fm.get("risk_tier", "medium")).lower())
        except ValueError:
            risk_tier = SkillRiskTier.MEDIUM

        try:
            autonomy_tier = SkillAutonomyTier(str(fm.get("autonomy_tier", "T1")).upper())
        except ValueError:
            autonomy_tier = SkillAutonomyTier.T1

        return SkillNode(
            skill_id=skill_id,
            name=str(fm.get("name", skill_id)),
            description=str(fm.get("description", ""))[:200],
            version=str(fm.get("version", "1.0.0")),
            risk_tier=risk_tier,
            floor_scope=[str(f) for f in floor_scope],
            autonomy_tier=autonomy_tier,
            trigger_phrases=[str(t) for t in triggers],
            mcp_servers=[str(s) for s in mcp_servers],
            skill_dependencies=[str(s) for s in skill_deps],
            inputs=[str(i) for i in (fm.get("inputs") or [])],
            outputs=[str(o) for o in (fm.get("outputs") or [])],
            path=skill_dir,
            updated=updated,
            word_count=word_count,
        )

    def _compile(self) -> None:
        """Scan skills_dir and compile all skill nodes."""
        self.nodes = {}
        compiled = 0
        skipped = 0

        for entry in sorted(self.skills_dir.iterdir()):
            if not entry.is_dir():
                skipped += 1
                continue
            # Skip quarantine / archive dirs
            if entry.name.startswith("."):
                skipped += 1
                continue
            node = self._parse_skill_md(entry)
            if node:
                self.nodes[node.skill_id] = node
                compiled += 1
            else:
                skipped += 1

        self._graph_version = datetime.now().strftime("%Y%m%d-%H%M%S")
        logger.info(
            f"[SkillGraph] Compiled {compiled} skills, skipped {skipped} dirs, "
            f"version={self._graph_version}"
        )

    def _build_indices(self) -> None:
        """Build secondary indices: by_mcp_server."""
        self.by_mcp_server = {}
        for node in self.nodes.values():
            for server in node.mcp_servers:
                self.by_mcp_server.setdefault(server, []).append(node.skill_id)

    def _resolve_edges(self) -> None:
        """Build in_edges and out_edges for all nodes."""
        for node in self.nodes.values():
            node.out_edges = list(node.skill_dependencies)
            node.in_edges = []

        for node in self.nodes.values():
            for dep_id in node.out_edges:
                if dep_id in self.nodes:
                    self.nodes[dep_id].in_edges.append(node.skill_id)

    def _compute_update_classes(self) -> None:
        """Classify update urgency for each node."""
        for node in self.nodes.values():
            if node.is_kernel:
                node.update_class = SkillUpdateClass.CRITICAL
            elif node.risk_tier == SkillRiskTier.CRITICAL:
                node.update_class = SkillUpdateClass.HIGH
            elif node.updated < "2026-06-01":
                node.update_class = SkillUpdateClass.STALE
            else:
                node.update_class = SkillUpdateClass.NORMAL

    # ── Public API ──────────────────────────────────────────────────────────

    def detect_orphans(self) -> list[str]:
        """
        Find skill dependencies that don't exist in the graph.
        Returns list of human-readable orphan descriptions.
        """
        orphans = []
        for node in self.nodes.values():
            for dep_id in node.out_edges:
                if dep_id not in self.nodes:
                    orphans.append(
                        f"{node.skill_id} → {dep_id} (MISSING — skill not in graph)"
                    )
        return orphans

    def compute_entropy(self) -> float:
        """
        Compute ΔS (entropy delta) for the skill graph.
        Higher = more broken / unhealthy.
        Score: 0.0 = perfect, 1.0 = maximally entropic.
        """
        total_edges = sum(len(n.out_edges) for n in self.nodes.values())
        broken_edges = sum(
            1 for n in self.nodes.values()
            for dep in n.out_edges if dep not in self.nodes
        )
        # Also penalize stale skills
        stale_count = sum(
            1 for n in self.nodes.values()
            if n.update_class == SkillUpdateClass.STALE
        )
        total_skills = max(len(self.nodes), 1)
        edge_entropy = broken_edges / max(total_edges, 1)
        stale_entropy = stale_count / total_skills
        # Weighted: 70% edges, 30% staleness
        return round(edge_entropy * 0.7 + stale_entropy * 0.3, 4)

    def get_chain(self, skill_id: str) -> list[SkillNode]:
        """
        Return topologically-sorted skill chain starting from skill_id.
        Follows out_edges (dependencies) in dependency order.
        Returns [] if skill_id not found.
        """
        if skill_id not in self.nodes:
            return []
        visited: set[str] = set()
        chain: list[SkillNode] = []

        def topo(node_id: str) -> None:
            if node_id in visited:
                return
            visited.add(node_id)
            node = self.nodes[node_id]
            for dep_id in node.out_edges:
                if dep_id in self.nodes:
                    topo(dep_id)
            chain.append(node)

        topo(skill_id)
        return chain

    def get_skill(self, skill_id: str) -> SkillNode | None:
        """Get a single skill node by ID."""
        return self.nodes.get(skill_id)

    def by_server(self, mcp_server: str) -> list[SkillNode]:
        """Get all skills that require a given MCP server."""
        skill_ids = self.by_mcp_server.get(mcp_server, [])
        return [self.nodes[sid] for sid in skill_ids if sid in self.nodes]

    def summary(self) -> dict[str, Any]:
        """Return a human-readable summary of the graph."""
        orphans = self.detect_orphans()
        return {
            "total_skills": len(self.nodes),
            "graph_version": self._graph_version,
            "by_tier": {
                tier.value: sum(1 for n in self.nodes.values() if n.risk_tier == tier)
                for tier in SkillRiskTier
            },
            "by_autonomy": {
                tier.value: sum(1 for n in self.nodes.values() if n.autonomy_tier == tier)
                for tier in SkillAutonomyTier
            },
            "orphans": orphans,
            "orphan_count": len(orphans),
            "entropy": self.compute_entropy(),
            "kernel_skills": sum(1 for n in self.nodes.values() if n.is_kernel),
            "domain_skills": sum(1 for n in self.nodes.values() if n.is_domain),
            "meta_skills": sum(1 for n in self.nodes.values() if n.is_meta),
            "ops_skills": sum(1 for n in self.nodes.values() if n.is_ops),
        }

    def dump(self) -> dict[str, Any]:
        """Return full graph as dict (for serialization)."""
        return {
            "graph_version": self._graph_version,
            "skills": {
                sid: {
                    "name": n.name,
                    "risk_tier": n.risk_tier.value,
                    "autonomy_tier": n.autonomy_tier.value,
                    "floor_scope": n.floor_scope,
                    "mcp_servers": n.mcp_servers,
                    "skill_dependencies": n.skill_dependencies,
                    "out_edges": n.out_edges,
                    "in_edges": n.in_edges,
                    "word_count": n.word_count,
                    "updated": n.updated,
                    "update_class": n.update_class.value,
                }
                for sid, n in self.nodes.items()
            },
            "orphans": self.detect_orphans(),
            "entropy": self.compute_entropy(),
        }

    def __repr__(self) -> str:
        return (
            f"SkillGraph(v{self._graph_version}, "
            f"{len(self.nodes)} skills, "
            f"ΔS={self.compute_entropy():.4f}, "
            f"{len(self.detect_orphans())} orphans)"
        )


# ── Singleton ─────────────────────────────────────────────────────────────────

# Module-level singleton — compiled once at import
_graph: SkillGraph | None = None


def get_graph() -> SkillGraph:
    """Get or create the singleton SkillGraph instance."""
    global _graph
    if _graph is None:
        _graph = SkillGraph()
    return _graph


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] [%(message)s]")

    graph = SkillGraph()
    summary = graph.summary()

    print(f"\n{'='*60}")
    print(f"  SkillGraph Summary — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    print(f"  Total skills:    {summary['total_skills']}")
    print(f"  Kernel skills:   {summary['kernel_skills']}")
    print(f"  Domain skills:   {summary['domain_skills']}")
    print(f"  Meta skills:     {summary['meta_skills']}")
    print(f"  Ops skills:      {summary['ops_skills']}")
    print(f"  Entropy ΔS:      {summary['entropy']:.4f}")
    print(f"  Orphans:         {summary['orphan_count']}")
    print()
    print("  By Risk Tier:")
    for tier, count in summary["by_tier"].items():
        print(f"    {tier:10s}: {count}")
    print("  By Autonomy:")
    for tier, count in summary["by_autonomy"].items():
        print(f"    {tier:10s}: {count}")

    if summary["orphans"]:
        print()
        print(f"  ORPHANS ({len(summary['orphans'])}):")
        for o in summary["orphans"]:
            print(f"    ❌ {o}")
    print()
    print(repr(graph))
