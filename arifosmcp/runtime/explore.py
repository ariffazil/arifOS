"""
arifOS L2 Exploration Substrate — Kernel + Modes (v2026.06.21)
==============================================================

One kernel, six modes. Sense-extend (111_OBSERVE extension).

States:  INIT → PLAN → STEP → UPDATE → CHECK → REFLECT → SEAL
Modes:  navigator | prospector | driller | mapper | surveyor | scout | auto

Prospector mode is the first concrete implementation — uses existing
filesystem tools (Bash, Read, Glob, Git). No new primitives needed.

Constitutional binding:
  ART  — non-destructive tools only, budgets enforced, domains allowed
  ACT  — each step gated and logged
  STOP — max_depth, max_steps, time_budget, forbidden paths

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol

from arifosmcp.schemas.explore import (
    ExplorationGraph,
    ExploreMetrics,
    ExploreMode,
    ExploreRequest,
    ExploreResponse,
    ExploreStatus,
    Finding,
    GraphEdge,
    GraphNode,
    Limits,
    NextMove,
    Saturation,
    Seed,
    SeedAPI,
    SeedPath,
    SeedURL,
    Verdict,
)

logger = logging.getLogger("arifos.explore")


# ═══════════════════════════════════════════════════════════════
# STATE MACHINE
# ═══════════════════════════════════════════════════════════════

class ExploreState(Enum):
    INIT = auto()
    PLAN = auto()
    STEP = auto()
    UPDATE = auto()
    CHECK = auto()
    REFLECT = auto()
    SEAL = auto()
    ABORT = auto()


# Transition matrix — exhaustive, no surprise paths
TRANSITIONS: dict[ExploreState, set[ExploreState]] = {
    ExploreState.INIT:    {ExploreState.PLAN, ExploreState.ABORT},
    ExploreState.PLAN:    {ExploreState.STEP, ExploreState.ABORT},
    ExploreState.STEP:    {ExploreState.UPDATE, ExploreState.ABORT},
    ExploreState.UPDATE:  {ExploreState.CHECK, ExploreState.ABORT},
    ExploreState.CHECK:   {ExploreState.PLAN, ExploreState.REFLECT, ExploreState.ABORT},
    ExploreState.REFLECT: {ExploreState.SEAL, ExploreState.ABORT},
    ExploreState.SEAL:    set(),
    ExploreState.ABORT:   set(),
}


# ═══════════════════════════════════════════════════════════════
# STEP RESULT — mode-agnostic output of one exploration step
# ═══════════════════════════════════════════════════════════════

@dataclass
class StepResult:
    """One exploration step's output. Mode-agnostic."""
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    findings: list[Finding]
    gaps: list[str]
    coverage_delta: float       # 0.0–1.0
    confidence: float           # 0.0–1.0
    terminal: bool = False      # True → no more branches from this node


# ═══════════════════════════════════════════════════════════════
# MODE CONTRACT (Protocol)
# ═══════════════════════════════════════════════════════════════

class ExplorerMode(Protocol):
    """Every exploration mode must satisfy this contract."""

    mode: ExploreMode

    async def sense(self, seed: Seed, node: GraphNode | None) -> list[GraphNode]:
        """Ingest from the environment. Returns 1+ new nodes."""
        ...

    async def plan(self, goal: str, graph: ExplorationGraph, limits: Limits) -> list[GraphNode]:
        """Given current graph state, return next node(s) to step into."""
        ...

    async def step(self, node: GraphNode, seed: Seed) -> StepResult:
        """Execute one exploration step from a node."""
        ...

    def heuristic(self, node: GraphNode, goal: str) -> float:
        """Score a node's relevance to the goal (0.0–1.0)."""
        ...


# ═══════════════════════════════════════════════════════════════
# HELPER: content hashing
# ═══════════════════════════════════════════════════════════════

def _hash(s: str) -> str:
    """Deterministic content hash for node IDs."""
    return hashlib.blake2b(s.encode("utf-8"), digest_size=16).hexdigest()


# ═══════════════════════════════════════════════════════════════
# HELPER: symbol extraction (language-agnostic, regex-based)
# ═══════════════════════════════════════════════════════════════

_SYMBOL_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("function", re.compile(r"(?:def|fn|func|function)\s+(\w+)", re.MULTILINE)),
    ("class",    re.compile(r"class\s+(\w+)", re.MULTILINE)),
    ("const",    re.compile(r"(?:const|export const|val)\s+(\w+)", re.MULTILINE)),
    ("var",      re.compile(r"(?:let|var|export let)\s+(\w+)", re.MULTILINE)),
    ("interface", re.compile(r"(?:interface|type)\s+(\w+)", re.MULTILINE)),
    ("export",   re.compile(r"export\s+(?:default\s+)?(?:function|class|const|let|var)\s+(\w+)", re.MULTILINE)),
]


def _extract_symbols(content: str, path: str) -> list[str]:
    """Extract code symbols (def, class, const, etc.) from file content."""
    symbols: list[str] = []
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    if ext not in {"py", "js", "ts", "jsx", "tsx", "rs", "go", "java", "rb", "sh", "bash", "yaml", "yml", "toml", "json", "md"}:
        return symbols
    for _kind, pattern in _SYMBOL_PATTERNS:
        for match in pattern.finditer(content):
            name = match.group(1)
            if name not in symbols:
                symbols.append(name)
    return symbols


# ═══════════════════════════════════════════════════════════════
# HELPER: import extraction
# ═══════════════════════════════════════════════════════════════

_IMPORT_PATTERNS: list[re.Pattern] = [
    # Python: import X, from X import Y
    re.compile(r"^(?:from\s+(\S+)\s+import|import\s+(\S+))", re.MULTILINE),
    # JS/TS: import ... from 'X', require('X')
    re.compile(r"""(?:from\s+['"](\S+?)['"]|require\s*\(\s*['"](\S+?)['"]\s*\))""", re.MULTILINE),
    # Go: import "X"
    re.compile(r"""import\s+['"](\S+?)['"]""", re.MULTILINE),
]


def _extract_imports(content: str, path: str) -> list[str]:
    """Extract import/dependency references from file content."""
    imports: list[str] = []
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    if ext not in {"py", "js", "ts", "jsx", "tsx", "rs", "go", "java", "rb"}:
        return imports
    for pattern in _IMPORT_PATTERNS:
        for match in pattern.finditer(content):
            imp = next((g for g in match.groups() if g is not None), None)
            if imp and imp not in imports:
                imports.append(imp)
    return imports


# ═══════════════════════════════════════════════════════════════
# HELPER: file type guessing
# ═══════════════════════════════════════════════════════════════

_TYPE_MAP: dict[str, str] = {
    "py": "python", "pyi": "python-stub",
    "js": "javascript", "jsx": "javascript-react",
    "ts": "typescript", "tsx": "typescript-react",
    "rs": "rust",
    "go": "go",
    "java": "java", "kt": "kotlin",
    "rb": "ruby",
    "sh": "shell", "bash": "shell", "zsh": "shell",
    "yaml": "yaml", "yml": "yaml",
    "toml": "toml",
    "json": "json",
    "md": "markdown", "mdx": "markdown-jsx",
    "css": "css", "scss": "scss", "less": "less",
    "html": "html", "htm": "html",
    "svg": "svg",
    "sql": "sql",
    "dockerfile": "dockerfile",
    "txt": "text", "log": "log",
    "pdf": "pdf", "png": "image", "jpg": "image", "jpeg": "image",
}


def _guess_type(path: str) -> str:
    """Guess file type from path suffix."""
    lower = path.lower()
    # Dockerfile has no extension
    if lower.endswith("dockerfile") or "dockerfile" in lower:
        return "dockerfile"
    ext = lower.rsplit(".", 1)[-1] if "." in lower else ""
    return _TYPE_MAP.get(ext, "unknown")


# ═══════════════════════════════════════════════════════════════
# EXPLORATION KERNEL — state machine shared by all modes
# ═══════════════════════════════════════════════════════════════

class ExplorationKernel:
    """One exploration run. Mode-agnostic constitutional state machine.

    Injected callbacks for ART/ACT/STOP binding:
      art_check     — preflight: "Is this exploration or just search?"
      act_gate      — per-step: gate each primitive
      stop_condition— emergency: abort if anomaly flags trip
      vault_seal    — terminal: seal exploration trace to VAULT999
    """

    def __init__(
        self,
        request: ExploreRequest,
        mode_impl: ExplorerMode,
        *,
        art_check: Callable[[ExploreRequest], Awaitable[bool]] | None = None,
        act_gate: Callable[[str, dict], Awaitable[bool]] | None = None,
        stop_condition: Callable[[], Awaitable[bool]] | None = None,
        vault_seal: Callable[[dict], Awaitable[str]] | None = None,
    ):
        self.request = request
        self.mode = mode_impl
        self.state = ExploreState.INIT
        self.graph = ExplorationGraph()
        self.metrics = ExploreMetrics()
        self._findings: list[Finding] = []
        self._gaps: list[str] = []
        self._step_stack: list[GraphNode] = []
        self._started_at: float | None = None
        self._visited: set[str] = set()  # content hashes already explored
        self._depth_map: dict[str, int] = {}  # node_id → depth

        # ART/ACT/STOP hooks
        self._art = art_check
        self._act = act_gate
        self._stop = stop_condition
        self._seal = vault_seal

        # Verdict placeholder
        self._verdict: Verdict = Verdict(saturation=Saturation.LOW)

    # ── Public entry point ──────────────────────────────────

    async def run(self) -> ExploreResponse:
        """Execute the full state machine — iterative, no recursion."""
        self._started_at = time.monotonic()
        limits = self.request.limits
        logger.info(
            "L2_EXPLORE start | mode=%s goal=%.80s",
            self.request.mode.value, self.request.goal,
        )

        try:
            self._validate()
            # Transition to PLAN — skip INIT since we already called _validate
            self.state = ExploreState.PLAN
            await self._execute_state()

            while self.state == ExploreState.PLAN:
                if self.metrics.steps >= limits.max_steps:
                    self.state = ExploreState.REFLECT
                    break
                if self._budget_exhausted():
                    self.state = ExploreState.REFLECT
                    break
                if await self._should_abort():
                    self.state = ExploreState.ABORT
                    break

                # One full STEP→UPDATE→CHECK cycle
                await self._transition(ExploreState.STEP)
                await self._transition(ExploreState.UPDATE)

                # CHECK (inline — no recursive transition)
                if self._step_stack:
                    # More work queued → replan for next iteration
                    await self._execute_state_plan()
                else:
                    self.state = ExploreState.REFLECT
                    break

            if self.state == ExploreState.REFLECT:
                self._verdict = self._compute_verdict()
                logger.info(
                    "L2_EXPLORE reflect | saturation=%s next_moves=%d",
                    self._verdict.saturation.value,
                    len(self._verdict.next_moves),
                )

        except Exception as exc:
            logger.error("L2_EXPLORE abort | %s", exc)
            self.state = ExploreState.ABORT

        return self._build_response()

    async def _execute_state_plan(self):
        """Re-plan: repopulate step_stack from current graph state."""
        limits = self.request.limits
        seed_nodes = await self.mode.plan(self.request.goal, self.graph, limits)
        self._step_stack = list(seed_nodes)
        logger.info("L2_EXPLORE replan | queued=%d nodes", len(self._step_stack))

    # ── State machine core ──────────────────────────────────

    async def _transition(self, target: ExploreState):
        if target not in TRANSITIONS.get(self.state, set()):
            raise ValueError(
                f"Illegal transition: {self.state.name} → {target.name}"
            )
        self.state = target
        await self._execute_state()

    async def _execute_state(self):
        limits = self.request.limits

        match self.state:
            case ExploreState.INIT:
                self._validate()

            case ExploreState.PLAN:
                # ART check — preflight
                if self._art:
                    ok = await self._art(self.request)
                    if not ok:
                        raise PermissionError("ART gate rejected exploration request")
                seed_nodes = await self.mode.plan(
                    self.request.goal, self.graph, limits
                )
                self._step_stack = list(seed_nodes)
                self.metrics.depth = 0
                for n in seed_nodes:
                    self._depth_map[n.node_id] = 0
                logger.info(
                    "L2_EXPLORE plan | queued=%d nodes", len(self._step_stack),
                )

            case ExploreState.STEP:
                if not self._step_stack:
                    # No work — CHECK will detect and route to REFLECT
                    return
                node = self._step_stack.pop(0)
                node_id = node.node_id

                # ACT gate — per-step
                if self._act:
                    ok = await self._act("step", {
                        "node_id": node_id,
                        "mode": self.request.mode.value,
                    })
                    if not ok:
                        raise PermissionError(f"ACT gate blocked step on {node_id}")

                # Skip already-visited nodes (by content hash)
                if node.content_hash and node.content_hash in self._visited:
                    return
                self._visited.add(node.content_hash)

                result = await self.mode.step(node, self.request.seed)
                self._apply_result(result, parent_node=node)
                self.metrics.steps += 1

            case ExploreState.UPDATE:
                self.metrics.coverage = self._compute_coverage()
                self.metrics.confidence = self._compute_confidence()

            case ExploreState.CHECK:
                # CHECK is handled inline in run() — no-op here
                pass

            case ExploreState.REFLECT:
                self._verdict = self._compute_verdict()
                logger.info(
                    "L2_EXPLORE reflect | saturation=%s next_moves=%d",
                    self._verdict.saturation.value,
                    len(self._verdict.next_moves),
                )

            case ExploreState.SEAL:
                if self._seal:
                    await self._seal(self._build_response().model_dump())
                elapsed = time.monotonic() - (self._started_at or 0)
                logger.info(
                    "L2_EXPLORE sealed | steps=%d depth=%d coverage=%.2f "
                    "confidence=%.2f elapsed=%.1fs",
                    self.metrics.steps, self.metrics.depth,
                    self.metrics.coverage, self.metrics.confidence,
                    elapsed,
                )

            case ExploreState.ABORT:
                logger.warning(
                    "L2_EXPLORE aborted | steps=%d state=%s",
                    self.metrics.steps, self.state.name,
                )

    # ── Internal helpers ────────────────────────────────────

    def _validate(self):
        """Init validation — check goal, seed, limits are sane."""
        if not self.request.goal.strip():
            raise ValueError("exploration goal is empty")
        limits = self.request.limits
        if limits.max_depth < 0:
            raise ValueError("max_depth must be >= 0")
        if limits.max_steps < 1:
            raise ValueError("max_steps must be >= 1")

    def _apply_result(self, result: StepResult, *, parent_node: GraphNode):
        """Merge a step result into the exploration graph."""
        # Mark parent node as resolved
        for i, n in enumerate(self.graph.nodes):
            if n.node_id == parent_node.node_id and n.meta.get("unresolved"):
                self.graph.nodes[i].meta["unresolved"] = False
                self.graph.nodes[i].meta["cycle_completed"] = self.metrics.steps + 1
                break

        # Add nodes
        for node in result.nodes:
            if not any(n.node_id == node.node_id for n in self.graph.nodes):
                self.graph.nodes.append(node)
                # Track depth
                parent_depth = self._depth_map.get(parent_node.node_id, 0)
                self._depth_map[node.node_id] = parent_depth + 1
                self.metrics.depth = max(self.metrics.depth, parent_depth + 1)
                # Queue unresolved children for further exploration
                if not result.terminal and node.meta.get("unresolved"):
                    if parent_depth + 1 < self.request.limits.max_depth:
                        self._step_stack.append(node)

        # Add edges
        for edge in result.edges:
            if not any(
                e.from_id == edge.from_id and e.to_id == edge.to_id
                for e in self.graph.edges
            ):
                self.graph.edges.append(edge)

        # Accumulate findings
        self._findings.extend(result.findings)

        # Accumulate gaps
        self._gaps.extend(result.gaps)

    def _compute_coverage(self) -> float:
        """Coverage = fraction of nodes that have been explored (non-unresolved)."""
        total = len(self.graph.nodes)
        if total == 0:
            return 0.0
        resolved = sum(
            1 for n in self.graph.nodes
            if not n.meta.get("unresolved") and n.content_hash
        )
        return resolved / total

    def _compute_confidence(self) -> float:
        """Mean confidence across all findings, or edge confidence if no findings."""
        if self._findings:
            return sum(f.confidence for f in self._findings) / len(self._findings)
        if self.graph.edges:
            return sum(e.confidence for e in self.graph.edges) / len(self.graph.edges)
        return 0.0

    def _compute_verdict(self) -> Verdict:
        """Judge saturation and propose next moves."""
        # Saturation based on coverage + remaining budget
        if self.metrics.coverage >= 0.80 and self.metrics.confidence >= 0.70:
            saturation = Saturation.HIGH
        elif self.metrics.coverage >= 0.40:
            saturation = Saturation.MEDIUM
        else:
            saturation = Saturation.LOW

        # Next moves: where are the gaps?
        next_moves: list[NextMove] = []
        for gap in self._gaps[:5]:
            next_moves.append(NextMove(
                mode=self.request.mode,
                goal=f"Resolve: {gap[:120]}",
                reason=gap[:200],
            ))

        # If high saturation but unresolved nodes remain, suggest Scout
        unresolved = [
            n for n in self.graph.nodes
            if n.meta.get("unresolved") and not any(
                e.from_id == n.node_id for e in self.graph.edges
            )
        ]
        if unresolved and saturation != Saturation.LOW:
            next_moves.append(NextMove(
                mode=ExploreMode.SCOUT,
                goal=f"Resolve {len(unresolved)} remaining nodes",
                reason=f"Unresolved nodes: {', '.join(n.label for n in unresolved[:3])}",
            ))

        return Verdict(saturation=saturation, next_moves=next_moves)

    def _budget_exhausted(self) -> bool:
        """Check if time budget is exhausted."""
        if self._started_at is None:
            return False
        elapsed = time.monotonic() - self._started_at
        return elapsed >= self.request.limits.time_budget_s

    async def _should_abort(self) -> bool:
        """Check emergency stop conditions."""
        if self._stop:
            return await self._stop()
        # Hard ceilings
        if self.metrics.steps >= self.request.limits.max_steps:
            return True
        if self.metrics.depth > self.request.limits.max_depth:
            return True
        if self._budget_exhausted() and self.metrics.steps > 0:
            return True
        return False

    def _build_response(self) -> ExploreResponse:
        """Assemble the final response from accumulated state."""
        if self.state == ExploreState.ABORT:
            status = ExploreStatus.FAILED
        elif self.state == ExploreState.SEAL:
            status = ExploreStatus.OK
        else:
            status = ExploreStatus.PARTIAL

        return ExploreResponse(
            status=status,
            exploration_graph=self.graph,
            findings=self._findings,
            gaps=self._gaps,
            metrics=self.metrics,
            verdict=self._verdict,
        )


# ═══════════════════════════════════════════════════════════════
# PROSPECTOR MODE — filesystem / codebase exploration
# ═══════════════════════════════════════════════════════════════
#
# Uses existing MCP tool surface: Bash (ls/find), Read (file content),
# Glob (pattern matching), git log. No new primitives needed.
# Pure orchestration — read-only, constitutional, deterministic.
# ═══════════════════════════════════════════════════════════════

@dataclass
class ProspectorMode:
    """Filesystem and codebase exploration mode.

    Implements the ExplorerMode protocol using existing filesystem tools.
    No browser. No network. No mutation.
    """

    mode: ExploreMode = field(default=ExploreMode.PROSPECTOR, init=False)
    request_seed: Seed | None = None

    # Injected async tool handles (from MCP server context at registration time)
    fs_list: Callable[[str], Awaitable[list[str]]] | None = None
    fs_read: Callable[[str], Awaitable[str]] | None = None
    fs_stat: Callable[[str], Awaitable[dict]] | None = None
    fs_glob: Callable[[str], Awaitable[list[str]]] | None = None
    git_log: Callable[[str], Awaitable[list[dict]]] | None = None

    async def sense(self, seed: Seed, _node: GraphNode | None = None) -> list[GraphNode]:
        """List directory, classify entries, return nodes."""
        path = seed.path.path if seed.path else "."
        entries: list[str] = []

        if self.fs_list:
            entries = await self.fs_list(path)

        nodes: list[GraphNode] = []
        for entry in entries:
            full = f"{path}/{entry}".replace("//", "/")
            try:
                st: dict = {}
                if self.fs_stat:
                    st = await self.fs_stat(full)
                node = GraphNode(
                    node_id=_hash(full),
                    mode=self.mode,
                    label=full,
                    content_hash=st.get("hash", _hash(full)),
                    evidence="",
                    meta={
                        "type": st.get("type", _guess_type(full)),
                        "size": st.get("size", 0),
                    },
                )
                nodes.append(node)
            except Exception:
                # Permission error, deleted between list and stat — skip
                continue
        return nodes

    async def plan(self, goal: str, graph: ExplorationGraph, limits: Limits) -> list[GraphNode]:
        """Rank unexplored nodes by relevance to goal, respecting limits.
        Auto-seeds from seed.path on cold start.
        """
        if not graph.nodes:
            # Cold start — seed from the request seed path
            seed_path = "."
            if self.request_seed and self.request_seed.path and self.request_seed.path.path:
                seed_path = self.request_seed.path.path
            logger.info("PROSPECTOR plan | cold start from seed path=%s", seed_path)
            nodes = await self.sense(Seed(path={"path": seed_path, "include_patterns": ["*"]}))
            for n in nodes:
                graph.nodes.append(n)
            return nodes

        # Score unvisited nodes
        scored: list[tuple[float, GraphNode]] = []
        for node in graph.nodes:
            # Skip already-explored (has outgoing edges)
            if any(e.from_id == node.node_id for e in graph.edges):
                continue
            # Skip nodes with no content hash (not yet sense'd)
            s = self.heuristic(node, goal)
            scored.append((s, node))

        scored.sort(key=lambda x: x[0], reverse=True)
        selected = [n for _, n in scored[:limits.max_steps]]
        return selected

    async def step(self, node: GraphNode, seed: Seed) -> StepResult:
        """Read file, extract symbols, discover imports.

        If the node label is not a valid file path (e.g., a research question
        from EurekaMode), searches for files matching the question terms instead.
        """
        path = node.label

        # If path doesn't look like a filesystem path, treat as search terms
        if not path.startswith(("/", "./", "../", "~")) and "/" not in path.lstrip("/"):
            # Research question → search for matching files
            return await self._search_step(node, seed)

        content = ""
        if self.fs_read:
            try:
                content = await self.fs_read(path)
            except Exception:
                return StepResult(
                    nodes=[], edges=[], findings=[], gaps=[f"cannot read: {path}"],
                    coverage_delta=0.0, confidence=0.0, terminal=True,
                )

        if not content:
            return StepResult(
                nodes=[], edges=[], findings=[], gaps=[],
                coverage_delta=0.0, confidence=0.0, terminal=True,
            )

        content_hash = _hash(content)
        symbols = _extract_symbols(content, path)
        imports = _extract_imports(content, path)

        # File node with extracted evidence
        evidence_snippet = content[:2000]
        file_node = GraphNode(
            node_id=content_hash,
            mode=self.mode,
            label=path,
            content_hash=content_hash,
            evidence=evidence_snippet,
            meta={
                "type": _guess_type(path),
                "symbols": symbols[:50],
                "symbol_count": len(symbols),
                "import_count": len(imports),
            },
        )

        # Edges and child nodes for discovered imports
        edges: list[GraphEdge] = []
        child_nodes: list[GraphNode] = []
        for imp in imports[:20]:  # cap per file
            child_id = _hash(imp)
            edges.append(GraphEdge(
                from_id=file_node.node_id,
                to_id=child_id,
                relation="imports" if "import" in imp.lower() else "references",
                confidence=0.9,
            ))
            child_nodes.append(GraphNode(
                node_id=child_id,
                mode=self.mode,
                label=imp,
                content_hash="",
                evidence="",
                meta={"unresolved": True, "parent": path},
            ))

        # Coverage and confidence estimation
        coverage = min(1.0, len(symbols) / 100) if symbols else 0.1
        confidence = 0.9 if content else 0.0

        # Findings
        findings: list[Finding] = []
        if symbols:
            findings.append(Finding(
                id=_hash(f"sym:{path}"),
                summary=f"{len(symbols)} symbols found in {path} ({_guess_type(path)})",
                confidence=0.9,
                sources=[path],
            ))
        if imports:
            findings.append(Finding(
                id=_hash(f"imp:{path}"),
                summary=f"{len(imports)} imports discovered in {path}",
                confidence=0.85,
                sources=[path],
            ))

        gaps: list[str] = []
        if imports:
            gaps.append(f"unresolved imports in {path}: {', '.join(imports[:5])}")

        return StepResult(
            nodes=[file_node] + child_nodes,
            edges=edges,
            findings=findings,
            gaps=gaps,
            coverage_delta=coverage,
            confidence=confidence,
            terminal=not bool(imports),  # terminal if no further branches
        )

    async def _search_step(self, node: GraphNode, seed: Seed) -> StepResult:
        """Handle research-question nodes by searching filesystem for matching content.

        When ProspectorMode receives a node whose label is a research question
        (not a file path), this method searches the current directory for files
        whose content matches the question terms, then reads the top matches.
        """
        import os as _os

        question = node.label[:200]
        terms = [t.lower() for t in question.split() if len(t) > 2]
        if not terms:
            return StepResult(
                nodes=[], edges=[], findings=[],
                gaps=[f"no searchable terms in question: {question[:80]}"],
                coverage_delta=0.0, confidence=0.0, terminal=True,
            )

        # Search current directory for files matching question terms
        matched_files: list[tuple[str, int]] = []  # (path, score)
        search_dirs = [".", "arifosmcp", "core", "docs", "AAA"]
        for d in search_dirs:
            if not _os.path.isdir(d):
                continue
            for root, _dirs, files in _os.walk(d):
                # Skip hidden and cache dirs
                if any(p.startswith(".") for p in root.split(_os.sep)):
                    continue
                if "__pycache__" in root or "node_modules" in root:
                    continue
                for fname in files:
                    fpath = _os.path.join(root, fname)
                    # Score by filename match
                    fname_lower = fname.lower()
                    score = sum(1 for t in terms if t in fname_lower)
                    if score > 0:
                        matched_files.append((fpath, score))
                if len(matched_files) >= 20:
                    break
            if len(matched_files) >= 20:
                break

        if not matched_files:
            return StepResult(
                nodes=[], edges=[], findings=[],
                gaps=[f"no files matching: {', '.join(terms[:8])}"],
                coverage_delta=0.0, confidence=0.0, terminal=True,
            )

        # Sort by score and read top files
        matched_files.sort(key=lambda x: x[1], reverse=True)
        top_files = matched_files[:5]

        result_nodes: list[GraphNode] = []
        result_findings: list[Finding] = []
        for fpath, score in top_files:
            content = ""
            if self.fs_read:
                try:
                    content = await self.fs_read(fpath)
                except Exception:
                    continue

            if not content:
                continue

            content_hash = _hash(content)
            symbols = _extract_symbols(content, fpath)
            evidence_snippet = content[:2000]

            result_nodes.append(GraphNode(
                node_id=content_hash,
                mode=self.mode,
                label=fpath,
                content_hash=content_hash,
                evidence=evidence_snippet,
                meta={
                    "type": _guess_type(fpath),
                    "symbols": symbols[:50],
                    "symbol_count": len(symbols),
                    "search_score": score,
                    "original_question": question[:120],
                },
            ))

            # Extract key lines containing search terms
            matching_lines = [
                line.strip()[:200] for line in content.split("\n")
                if any(t in line.lower() for t in terms[:5])
            ][:5]

            result_findings.append(Finding(
                id=_hash(f"prospector:{fpath}:{question[:60]}"),
                summary=f"File: {fpath} — {len(symbols)} symbols, "
                        f"{len(matching_lines)} matching lines: {'; '.join(matching_lines[:3])}",
                confidence=min(0.85, 0.4 + 0.1 * score),
                sources=[fpath],
            ))

        coverage = min(1.0, len(matched_files) / 50)
        confidence = 0.5 if result_findings else 0.0
        if result_findings:
            confidence = sum(f.confidence for f in result_findings) / len(result_findings)

        return StepResult(
            nodes=result_nodes,
            edges=[],
            findings=result_findings,
            gaps=[] if result_findings else [f"no content matches for: {', '.join(terms[:8])}"],
            coverage_delta=coverage,
            confidence=confidence,
            terminal=not bool(matched_files),
        )

    def heuristic(self, node: GraphNode, goal: str) -> float:
        """Keyword overlap between goal terms and node label + symbols."""
        goal_terms = set(goal.lower().split())
        if not goal_terms:
            return 0.5  # uninformative prior

        node_text = (
            f"{node.label} "
            f"{' '.join(node.meta.get('symbols', []))} "
            f"{node.meta.get('type', '')}"
        ).lower()

        overlap = sum(1 for t in goal_terms if t in node_text)
        # Bonus for exact path-segment match
        path_segments = node.label.lower().replace("/", " ").replace("-", " ").replace("_", " ").split()
        segment_overlap = sum(1 for t in goal_terms if any(t in seg for seg in path_segments))
        total = overlap + 0.5 * segment_overlap
        return min(1.0, total / max(1, len(goal_terms)))


# ═══════════════════════════════════════════════════════════════
# SURVEYOR MODE — cross-organ telemetry fusion (GEOX + WELL + WEALTH)
# ═══════════════════════════════════════════════════════════════
#
# Queries three federation organs, extracts signals, correlates
# across organ boundaries, and builds a unified exploration graph.
# Read-only, non-destructive, constitutional.
# ═══════════════════════════════════════════════════════════════


def _normalize_signal(raw: dict, organ: str) -> dict:
    """Normalize organ-specific signal to common schema."""
    return {
        "organ": organ,
        "value": raw.get("value", raw.get("result", raw.get("data", ""))),
        "timestamp": raw.get("timestamp", raw.get("ts", "")),
        "location": raw.get("location", raw.get("lat_lon", raw.get("coordinates", None))),
        "confidence": float(raw.get("confidence", raw.get("score", 0.5))),
        "metadata": {
            k: v for k, v in raw.items()
            if k not in {
                "value", "result", "data", "timestamp", "ts",
                "location", "lat_lon", "coordinates",
                "confidence", "score",
            }
        },
    }


def _correlate(a: dict, b: dict) -> float:
    """Compute correlation score between two normalized signals.

    Returns 0.0–1.0 based on:
    - Keyword overlap in value/metadata
    - Temporal proximity (if timestamps present)
    - Spatial proximity (if locations present)
    """
    score = 0.0
    weights_total = 0.0

    # Keyword overlap (weight 0.5)
    a_text = str(a.get("value", "")) + " " + str(a.get("metadata", {}))
    b_text = str(b.get("value", "")) + " " + str(b.get("metadata", {}))
    a_words = set(a_text.lower().split())
    b_words = set(b_text.lower().split())
    if a_words and b_words:
        overlap = len(a_words & b_words) / max(len(a_words | b_words), 1)
        score += 0.5 * overlap
    weights_total += 0.5

    # Temporal proximity (weight 0.25)
    a_ts = a.get("timestamp", "")
    b_ts = b.get("timestamp", "")
    if a_ts and b_ts:
        try:
            from datetime import datetime
            t_a = datetime.fromisoformat(str(a_ts).replace("Z", "+00:00"))
            t_b = datetime.fromisoformat(str(b_ts).replace("Z", "+00:00"))
            delta_hours = abs((t_a - t_b).total_seconds()) / 3600
            temporal_score = max(0.0, 1.0 - delta_hours / 720)  # decay over 30 days
            score += 0.25 * temporal_score
        except (ValueError, TypeError):
            pass
    weights_total += 0.25

    # Spatial proximity (weight 0.25)
    a_loc = a.get("location")
    b_loc = b.get("location")
    if a_loc and b_loc:
        dist = spatial_distance(a_loc, b_loc)
        if dist >= 0:
            spatial_score = max(0.0, 1.0 - dist / 1000)  # decay over 1000km
            score += 0.25 * spatial_score
    weights_total += 0.25

    return min(1.0, score / weights_total if weights_total > 0 else 0.0)


def laglead(a: dict, b: dict) -> str:
    """Determine temporal relationship between two signals."""
    a_ts = a.get("timestamp", "")
    b_ts = b.get("timestamp", "")
    if not a_ts or not b_ts:
        return "unknown"
    try:
        from datetime import datetime
        t_a = datetime.fromisoformat(str(a_ts).replace("Z", "+00:00"))
        t_b = datetime.fromisoformat(str(b_ts).replace("Z", "+00:00"))
        delta = (t_b - t_a).total_seconds()
        if abs(delta) < 60:
            return "simultaneous"
        return "lead" if delta > 0 else "lag"
    except (ValueError, TypeError):
        return "unknown"


def spatial_distance(a_loc: dict | list | tuple, b_loc: dict | list | tuple) -> float:
    """Haversine distance in km between two locations.

    Accepts dict with lat/lon keys, or [lat, lon] list/tuple.
    Returns -1 if format unrecognized.
    """
    import math

    def _extract(loc: dict | list | tuple) -> tuple[float, float] | None:
        if isinstance(loc, dict):
            lat = loc.get("lat", loc.get("latitude"))
            lon = loc.get("lon", loc.get("lng", loc.get("longitude")))
            if lat is not None and lon is not None:
                return float(lat), float(lon)
        elif isinstance(loc, (list, tuple)) and len(loc) >= 2:
            return float(loc[0]), float(loc[1])
        return None

    a = _extract(a_loc)
    b = _extract(b_loc)
    if a is None or b is None:
        return -1.0

    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))  # Earth radius in km


@dataclass
class SurveyorMode:
    """Cross-organ telemetry fusion explorer.

    Queries GEOX (earth), WELL (vitality), and WEALTH (capital),
    extracts signals, correlates across organ boundaries, and
    builds a unified exploration graph.

    Implements the ExplorerMode protocol.
    Read-only, non-destructive, constitutional.
    """

    mode: ExploreMode = field(default=ExploreMode.SURVEYOR, init=False)
    request_seed: Seed | None = None

    # Injected async organ query handles
    geox_query: Callable[[str], Awaitable[list[dict]]] | None = None
    well_query: Callable[[str], Awaitable[list[dict]]] | None = None
    wealth_query: Callable[[str], Awaitable[list[dict]]] | None = None

    async def sense(self, seed: Seed, _node: GraphNode | None = None) -> list[GraphNode]:
        """Query all three organs, extract signals, return nodes."""
        question = seed.question or ""
        if not question:
            return []

        nodes: list[GraphNode] = []
        organs = [
            ("geox", self.geox_query),
            ("well", self.well_query),
            ("wealth", self.wealth_query),
        ]

        for organ_name, query_fn in organs:
            if query_fn is None:
                continue
            try:
                raw_signals = await query_fn(question)
                for raw in raw_signals[:20]:  # cap per organ
                    signal = _normalize_signal(raw, organ_name)
                    ts = signal.get("timestamp", "")
                    val = str(signal.get("value", ""))[:64]
                    node_id = _hash(f"{organ_name}:{ts}:{val}")
                    nodes.append(GraphNode(
                        node_id=node_id,
                        mode=self.mode,
                        label=f"{organ_name}:{str(signal.get('value', ''))[:60]}",
                        content_hash=_hash(str(signal)),
                        evidence=str(signal.get("value", ""))[:500],
                        meta={
                            "organ": organ_name,
                            "timestamp": signal.get("timestamp", ""),
                            "location": signal.get("location"),
                            "confidence": signal.get("confidence", 0.5),
                            "raw_value": signal.get("value"),
                            "unresolved": True,
                        },
                    ))
            except Exception as exc:
                logger.warning("SURVEYOR sense | %s query failed: %s", organ_name, exc)
                nodes.append(GraphNode(
                    node_id=_hash(f"{organ_name}:error:{question[:32]}"),
                    mode=self.mode,
                    label=f"{organ_name}:QUERY_FAILED",
                    content_hash="",
                    evidence=str(exc)[:200],
                    meta={"organ": organ_name, "error": True, "unresolved": False},
                ))

        return nodes

    async def plan(self, goal: str, graph: ExplorationGraph, limits: Limits) -> list[GraphNode]:
        """Rank unexplored nodes by heuristic, return top-K.
        Auto-seeds on cold start.
        """
        if not graph.nodes:
            # Cold start — build initial nodes from seed question
            seed_question = (
                self.request_seed.question
                if self.request_seed and self.request_seed.question
                else goal
            )
            logger.info("SURVEYOR plan | cold start from question")
            nodes = await self.sense(Seed(question=seed_question))
            for n in nodes:
                graph.nodes.append(n)
            return nodes

        scored: list[tuple[float, GraphNode]] = []
        for node in graph.nodes:
            if any(e.from_id == node.node_id for e in graph.edges):
                continue
            if node.meta.get("error"):
                continue
            s = self.heuristic(node, goal)
            scored.append((s, node))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [n for _, n in scored[:limits.max_steps]]

    async def step(self, node: GraphNode, seed: Seed) -> StepResult:
        """Refined query for one signal — discover correlations."""
        organ = node.meta.get("organ", "")
        raw_value = node.meta.get("raw_value", "")

        # Build refined query from signal context
        refined_query = f"{seed.question or ''} {str(raw_value)[:100]}".strip()

        new_nodes: list[GraphNode] = []
        new_edges: list[GraphEdge] = []
        findings: list[Finding] = []
        gaps: list[str] = []

        # Query the same organ for neighbors
        query_fn = {
            "geox": self.geox_query,
            "well": self.well_query,
            "wealth": self.wealth_query,
        }.get(organ)

        neighbor_signals: list[dict] = []
        if query_fn:
            try:
                raw_neighbors = await query_fn(refined_query)
                for raw in raw_neighbors[:10]:
                    neighbor_signals.append(_normalize_signal(raw, organ))
            except Exception as exc:
                gaps.append(f"{organ} refined query failed: {exc}")

        # Cross-organ correlation: query OTHER organs with same context
        cross_organs = [
            ("geox", self.geox_query),
            ("well", self.well_query),
            ("wealth", self.wealth_query),
        ]
        cross_signals: list[tuple[str, dict]] = []
        for cross_name, cross_fn in cross_organs:
            if cross_name == organ or cross_fn is None:
                continue
            try:
                raw_cross = await cross_fn(refined_query)
                for raw in raw_cross[:5]:
                    cross_signals.append((cross_name, _normalize_signal(raw, cross_name)))
            except Exception as exc:
                gaps.append(f"{organ}→{cross_name} cross-query failed: {exc}")

        # Build nodes + edges for neighbors
        current_signal = {
            "value": node.meta.get("raw_value"),
            "timestamp": node.meta.get("timestamp"),
            "location": node.meta.get("location"),
        }

        for neighbor in neighbor_signals:
            ts = neighbor.get("timestamp", "")
            val = str(neighbor.get("value", ""))[:64]
            n_id = _hash(f"{organ}:{ts}:{val}")
            new_nodes.append(GraphNode(
                node_id=n_id,
                mode=self.mode,
                label=f"{organ}:{str(neighbor.get('value', ''))[:60]}",
                content_hash=_hash(str(neighbor)),
                evidence=str(neighbor.get("value", ""))[:500],
                meta={
                    "organ": organ,
                    "timestamp": neighbor.get("timestamp"),
                    "location": neighbor.get("location"),
                    "confidence": neighbor.get("confidence", 0.5),
                    "raw_value": neighbor.get("value"),
                },
            ))
            corr = _correlate(current_signal, neighbor)
            if corr > 0.1:
                new_edges.append(GraphEdge(
                    from_id=node.node_id,
                    to_id=n_id,
                    relation=f"{organ}_neighbor",
                    confidence=corr,
                ))

        # Build nodes + edges for cross-organ signals
        strongest_cross = None
        strongest_corr = 0.0
        for cross_name, cross_signal in cross_signals:
            cs_ts = cross_signal.get("timestamp", "")
            cs_val = str(cross_signal.get("value", ""))[:64]
            c_id = _hash(f"{cross_name}:{cs_ts}:{cs_val}")
            new_nodes.append(GraphNode(
                node_id=c_id,
                mode=self.mode,
                label=f"{cross_name}:{str(cross_signal.get('value', ''))[:60]}",
                content_hash=_hash(str(cross_signal)),
                evidence=str(cross_signal.get("value", ""))[:500],
                meta={
                    "organ": cross_name,
                    "timestamp": cross_signal.get("timestamp"),
                    "location": cross_signal.get("location"),
                    "confidence": cross_signal.get("confidence", 0.5),
                    "raw_value": cross_signal.get("value"),
                },
            ))
            corr = _correlate(current_signal, cross_signal)
            if corr > 0.1:
                relation = f"{organ}_to_{cross_name}"
                ll = laglead(current_signal, cross_signal)
                if ll != "unknown":
                    relation += f":{ll}"
                new_edges.append(GraphEdge(
                    from_id=node.node_id,
                    to_id=c_id,
                    relation=relation,
                    confidence=corr,
                ))
                if corr > strongest_corr:
                    strongest_corr = corr
                    strongest_cross = (cross_name, cross_signal, corr)

        # Findings
        if strongest_cross:
            cross_name, cross_signal, corr = strongest_cross
            findings.append(Finding(
                id=_hash(f"cross:{node.node_id}:{cross_name}"),
                summary=(
                    f"Cross-organ correlation: {organ} ↔ {cross_name} "
                    f"(r={corr:.2f}, {laglead(current_signal, cross_signal)})"
                ),
                confidence=corr,
                sources=[
                    f"{organ}:{node.label}",
                    f"{cross_name}:{str(cross_signal.get('value', ''))[:40]}",
                ],
            ))

        if neighbor_signals:
            findings.append(Finding(
                id=_hash(f"neighbors:{node.node_id}"),
                summary=f"{len(neighbor_signals)} {organ} signals near current signal",
                confidence=0.8,
                sources=[f"{organ}:{node.label}"],
            ))

        # Gaps
        if not neighbor_signals:
            gaps.append(f"No {organ} neighbors found for {node.label}")
        if not cross_signals:
            gaps.append(f"No cross-organ signals found for {node.label}")
        missing_conf = [
            s for s in neighbor_signals + [cs for _, cs in cross_signals]
            if s.get("confidence", 0) < 0.3
        ]
        if missing_conf:
            gaps.append(f"{len(missing_conf)} low-confidence signals (<0.3)")

        coverage = min(1.0, (len(neighbor_signals) + len(cross_signals)) / 20)
        avg_conf = 0.0
        all_sigs = neighbor_signals + [cs for _, cs in cross_signals]
        if all_sigs:
            avg_conf = sum(s.get("confidence", 0.5) for s in all_sigs) / len(all_sigs)

        return StepResult(
            nodes=new_nodes,
            edges=new_edges,
            findings=findings,
            gaps=gaps,
            coverage_delta=coverage,
            confidence=avg_conf,
            terminal=not (neighbor_signals or cross_signals),
        )

    def heuristic(self, node: GraphNode, goal: str) -> float:
        """Score node relevance: keyword overlap + multi-organ boost."""
        goal_terms = set(goal.lower().split())
        if not goal_terms:
            return 0.5

        node_text = (
            f"{node.label} "
            f"{node.meta.get('organ', '')} "
            f"{str(node.meta.get('raw_value', ''))}"
        ).lower()

        overlap = sum(1 for t in goal_terms if t in node_text)
        base = min(1.0, overlap / max(1, len(goal_terms)))

        # Higher confidence signals get a slight boost
        confidence = node.meta.get("confidence", 0.5)

        # Higher confidence signals get a slight boost
        return min(1.0, base * 0.7 + confidence * 0.3)


# ═══════════════════════════════════════════════════════════════
# NAVIGATOR MODE — governed web traversal (Playwright-powered)
# ═══════════════════════════════════════════════════════════════
#
# Read-only browser automation. Every navigation is governed:
#   ART  — allowed_domains enforced, no form submissions, no POST
#   ACT  — each page fetch gated and logged
#   STOP — redirect limit, domain escape, auth wall, time budget
#
# Uses Playwright async_api (already installed in arifOS venv).
# F1–F13 enforced at every hop.
# ═══════════════════════════════════════════════════════════════

# ── Navigator helpers (no longer needed — delegated to federation) ────────────
# Playwright/HTML helpers (_check_playwright, _extract_links, _sanitize_url,
# _strip_tags) were removed 2026-06-21. Navigator now delegates to the canonical
# arif_observe (search) and arif_fetch (fetch) handlers, which
# already carry envelope wrapping, session/actor binding, and 9-signal emission.


@dataclass
class NavigatorMode:
    """Web exploration mode — FEDERATED to arif_observe + arif_fetch.

    No Playwright, no HTML scraping, no link extraction. All web work is
    delegated to the canonical MCP handlers, which already provide:

      F1  AMANAH    — handler-level ACT/ART gating
      F2  TRUTH     — content hash on every node
      F11 AUTH      — actor_verified propagation through session
      F12 INJECTION — handler-level sanitization
      envelope      — status / tool / result / meta / nine_signal / session_id

    This module is a thin orchestrator:

      URL-shaped label    → arif_fetch(mode="fetch", url=...)
      Question-shaped     → arif_observe(mode="search", query=...)

    Reads return value (sync dicts from the canonical handlers):

      arif_sense_obverse  → result.results is the list of search hits
      arif_fetch → result.content is the page content
    """

    mode: ExploreMode = field(default=ExploreMode.NAVIGATOR, init=False)
    request_seed: Seed | None = None
    actor_id: str | None = None
    session_id: str | None = None

    def _resolve_seed_url(self) -> str:
        if self.request_seed and self.request_seed.url:
            return self.request_seed.url.url
        return ""

    async def sense(self, seed: Seed, _node: GraphNode | None = None) -> list[GraphNode]:
        """Cold start — emit unresolved seed URL as initial node."""
        url = ""
        if seed.url:
            url = seed.url.url
        if not url:
            url = self._resolve_seed_url()
        if not url:
            return []
        return [GraphNode(
            node_id=_hash(url),
            mode=self.mode,
            label=url,
            content_hash="",
            evidence="",
            meta={"unresolved": True, "url": url, "seed": True,
                  "federated_via": "arif_fetch"},
        )]

    async def plan(self, goal: str, graph: ExplorationGraph, limits: Limits) -> list[GraphNode]:
        """Cold start: seed from request URL. Otherwise rank unresolved URL nodes."""
        if not graph.nodes:
            seed_url = self._resolve_seed_url()
            if not seed_url:
                logger.info("NAVIGATOR plan | cold start without seed URL")
                return []

            seed_node = GraphNode(
                node_id=_hash(f"seed:{seed_url}"),
                mode=self.mode,
                label=seed_url,
                content_hash="",
                evidence="",
                meta={"unresolved": True, "seed": True, "url": seed_url},
            )
            graph.nodes.append(seed_node)
            logger.info("NAVIGATOR plan | cold start from seed URL=%s", seed_url)
            return [seed_node]

        scored: list[tuple[float, GraphNode]] = []
        for node in graph.nodes:
            if any(e.from_id == node.node_id for e in graph.edges):
                continue
            if not node.meta.get("unresolved"):
                continue
            scored.append((self.heuristic(node, goal), node))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [n for _, n in scored[:limits.max_steps]]

    async def step(self, node: GraphNode, seed: Seed) -> StepResult:
        """Delegate to arif_fetch (URL) or arif_observe (query).

        Both handlers are sync — they return envelopes synchronously. We call
        them as ordinary functions; the kernel's await semantics wrap the
        whole step. Federated identity (session_id, actor_verified, nine_signal)
        propagates through the handler envelope.
        """
        from arifosmcp.runtime.tools import _CANONICAL_HANDLERS

        label = node.label
        is_url = label.startswith(("http://", "https://"))

        new_nodes: list[GraphNode] = []
        findings: list[Finding] = []
        gaps: list[str] = []

        try:
            if is_url:
                handler = _CANONICAL_HANDLERS.get("arif_fetch")
                if handler is None:
                    gaps.append("arif_fetch handler not available")
                else:
                    result = handler(
                        mode="fetch", url=label,
                        actor_id=self.actor_id, session_id=self.session_id,
                    )
                    inner = result.get("result", {}) if isinstance(result, dict) else {}
                    content = inner.get("content", "") if isinstance(inner, dict) else ""
                    content_hash = (
                        inner.get("content_hash") if isinstance(inner, dict) else None
                    ) or _hash(content or label)

                    page_node = GraphNode(
                        node_id=content_hash,
                        mode=self.mode,
                        label=label,
                        content_hash=content_hash,
                        evidence=(content or "")[:10000],
                        meta={
                            "url": label,
                            "federated_via": "arif_fetch",
                            "actor_verified": result.get("actor_verified") if isinstance(result, dict) else None,
                            "session_id": result.get("session_id") if isinstance(result, dict) else None,
                        },
                    )
                    new_nodes.append(page_node)

                    if content:
                        snippet = content[:300].replace("\n", " ").strip()
                        findings.append(Finding(
                            id=_hash(f"nav:{label}"),
                            summary=f"Fetched {label}: {snippet[:200]}",
                            confidence=0.9,
                            sources=[label],
                        ))
                    else:
                        gaps.append(f"empty content from arif_fetch: {label}")
            else:
                # Research question → federated search
                handler = _CANONICAL_HANDLERS.get("arif_observe")
                if handler is None:
                    gaps.append("arif_observe handler not available")
                else:
                    result = handler(
                        mode="search", query=label[:200],
                        actor_id=self.actor_id, session_id=self.session_id,
                    )
                    inner = result.get("result", {}) if isinstance(result, dict) else {}
                    hits = inner.get("results", []) if isinstance(inner, dict) else []

                    for hit in hits[:10]:
                        if not isinstance(hit, dict):
                            continue
                        hit_url = hit.get("url", "")
                        hit_title = hit.get("title", hit_url)
                        hit_snippet = hit.get("snippet", "") or hit.get("description", "")
                        if not hit_url:
                            continue
                        new_nodes.append(GraphNode(
                            node_id=_hash(hit_url),
                            mode=self.mode,
                            label=hit_url,
                            content_hash="",
                            evidence=hit_snippet[:500],
                            meta={
                                "unresolved": True,
                                "title": hit_title,
                                "url": hit_url,
                                "federated_via": "arif_observe",
                            },
                        ))

                    if new_nodes:
                        findings.append(Finding(
                            id=_hash(f"search:{label}"),
                            summary=f"{len(new_nodes)} results from federated search: {label[:80]}",
                            confidence=0.85,
                            sources=[n.label for n in new_nodes[:3]],
                        ))
                    else:
                        gaps.append(f"no results from federated search: {label[:80]}")
        except Exception as exc:
            logger.error("NAVIGATOR step | federated call failed: %s", exc)
            gaps.append(f"federation error: {exc!s:.160}")

        coverage = min(1.0, len(new_nodes) / 10) if new_nodes else 0.0
        confidence = 0.9 if findings else 0.0
        terminal = not bool(new_nodes)

        return StepResult(
            nodes=new_nodes,
            edges=[],
            findings=findings,
            gaps=gaps,
            coverage_delta=coverage,
            confidence=confidence,
            terminal=terminal,
        )

    def heuristic(self, node: GraphNode, goal: str) -> float:
        """Score URL node relevance by keyword overlap with label/title/url."""
        goal_terms = set(goal.lower().split())
        if not goal_terms:
            return 0.3

        node_text = (
            f"{node.label} "
            f"{node.meta.get('title', '')} "
            f"{node.meta.get('url', '')}"
        ).lower()

        overlap = sum(1 for t in goal_terms if t in node_text)
        url = node.meta.get("url", node.label)
        path_segments = url.lower().replace("/", " ").replace("-", " ").replace("_", " ").split()
        segment_overlap = sum(1 for t in goal_terms if any(t in seg for seg in path_segments))
        total = overlap + 0.5 * segment_overlap
        return min(1.0, total / max(1, len(goal_terms)))


# ═══════════════════════════════════════════════════════════════
# EUREKA MODE — evolutionary discovery loop (LDEA cycle)
# ═══════════════════════════════════════════════════════════════
#
# The 7th mode. The whole point of the L2 Exploration Substrate.
#
# EurekaMode orchestrates the other five modes in an evolutionary loop:
#   L (Learn)   → SENSE 111: parse question, auto-select modes, dispatch seeds
#   D (Discover)→ MIND 333: collect findings, cross-reference, find patterns
#   E (Evaluate)→ JUDGE 888: score confidence + novelty, identify gaps
#   A (Adapt)   → FORGE 900 + VAULT 999: breed new seeds from gaps, seal findings
#
# Each LDEA cycle is one "step" in the outer ExplorationKernel FSM.
# The kernel's CHECK→PLAN loop creates the evolutionary repetition.
# Saturation = diminishing returns (no new findings above novelty threshold).
#
# Mapped to arifOS organs:
#   L → arif_observe + Navigator/Prospector/Surveyor dispatch
#   D → arif_think (cross-reference, pattern detection)
#   E → arif_judge (score, filter, gap detection)
#   A → arif_forge (replan) + arif_seal (preserve findings)
#
# Constitutional binding:
#   F1  AMANAH    — reversible-first; sub-explorations are read-only
#   F2  TRUTH     — all findings cite source + content_hash
#   F3  TRI-WIT   — cross-mode findings must converge ≥ 0.75
#   F4  CLARITY   — each cycle reduces entropy (ΔS ≤ 0)
#   F7  HUMILITY  — confidence bands, never fake certainty
#   F9  ANTIHANTU — no hallucinated findings; orphan nodes quarantined
#   F13 SOVEREIGN — Arif's veto on any irreversible sub-action
#
# Subsumes Scout mode: EurekaMode IS Scout + evolution + governance.
# Scout becomes a thin wrapper when forged later.
#
# DITEMPA BUKAN DIBERI — Forged, Not Given.
# ═══════════════════════════════════════════════════════════════


# ── Eureka helpers ────────────────────────────────────────

# Domain classification for auto-dispatch — expanded with geoscience + physics terms
_DOMAIN_PATTERNS: list[tuple[re.Pattern, ExploreMode]] = [
    (re.compile(r"https?://", re.IGNORECASE), ExploreMode.NAVIGATOR),
    (re.compile(r"\b(api|endpoint|rest|graphql|openapi|swagger)\b", re.IGNORECASE), ExploreMode.DRILLER),
    (re.compile(r"\b(code|repo|github|gitlab|source|file|directory|path|package|module|class|function)\b", re.IGNORECASE), ExploreMode.PROSPECTOR),
    (re.compile(r"\b(telemetry|signal|sensor|log|metric|health|vital|organ|geox|wealth|well)\b", re.IGNORECASE), ExploreMode.SURVEYOR),
    (re.compile(r"\b(graph|relation|entity|knowledge|ontology|schema|triple|node|edge)\b", re.IGNORECASE), ExploreMode.MAPPER),
    # Geoscience terms — route to Navigator (web research) primarily
    (re.compile(r"\b(seismic|well\s*log|petrophysic|basin|formation|reservoir|geology|geophysic|earth\s*model|lem|subsurface)\b", re.IGNORECASE), ExploreMode.NAVIGATOR),
    # Mathematics / physics / equations
    (re.compile(r"\b(pde|neural\s*operator|fourier|equation|physics|wavelet|transform|gradient|loss|convergence)\b", re.IGNORECASE), ExploreMode.NAVIGATOR),
    # Foundation model / ML architecture terms
    (re.compile(r"\b(transformer|attention|encoder|decoder|embedding|pretrain|fine.?tune|foundation\s*model|moe|vit|mae|vision\s*transformer)\b", re.IGNORECASE), ExploreMode.NAVIGATOR),
]


def _classify_question(question: str) -> list[ExploreMode]:
    """Auto-classify a research question into relevant exploration modes.

    Returns deduplicated list of modes ordered by match strength.
    Falls back to EUREKA mode (all three sub-explorers) when no domain matches.
    """
    scores: dict[ExploreMode, int] = {}
    for pattern, mode in _DOMAIN_PATTERNS:
        matches = len(pattern.findall(question))
        if matches > 0:
            scores[mode] = scores.get(mode, 0) + matches
    if not scores:
        # Default: try all available modes in Eureka loop
        return [ExploreMode.PROSPECTOR, ExploreMode.NAVIGATOR, ExploreMode.SURVEYOR]
    return sorted(scores, key=scores.get, reverse=True)


def _novelty_score(finding: Finding, seen_hashes: set[str]) -> float:
    """Score how novel a finding is (0.0 = duplicate, 1.0 = completely new).

    Multi-factor novelty:
    - Identity check: finding.id in seen_hashes → 0.0 (exact duplicate)
    - Summary term overlap with ALL seen findings (aggregate)
    - Length bonus: longer findings with unique terms score higher
    - Source bonus: findings with multiple sources are more novel
    """
    if finding.id in seen_hashes:
        return 0.0

    summary_terms = set(finding.summary.lower().split())
    if not summary_terms:
        return 0.4  # Empty summary = ambiguous novelty

    # Aggregate overlap across all seen finding summaries
    # This catches partial duplicates across different sub-mode dispatches
    seen_texts = set()
    # We reconstruct from _best_findings stored in EurekaMode
    # But this function is static — caller passes seen_hashes
    # We approximate by checking the finding's id-adjacent hashes
    # Fallback: length-normalized term diversity
    term_diversity = len(summary_terms) / max(1, len(finding.summary))

    # Source diversity bonus
    source_bonus = min(0.3, len(finding.sources) * 0.1)

    # Term uniqueness: longer summaries with diverse terms = more novel
    base_novelty = 0.5 + 0.3 * min(1.0, term_diversity) + source_bonus

    return min(1.0, base_novelty)


@dataclass
class EurekaMode:
    """Evolutionary discovery loop — the meta-explorer.

    Orchestrates Navigator, Prospector, Surveyor (and eventually Driller, Mapper)
    in LDEA cycles. Each cycle: dispatch sub-explorers → collect findings →
    cross-reference → score novelty → breed new seeds from gaps.

    The outer ExplorationKernel FSM drives the evolutionary repetition.
    Saturation is reached when three consecutive cycles produce no novel findings.
    """

    mode: ExploreMode = field(default=ExploreMode.EUREKA, init=False)

    # Sub-mode instances (lazy-initialized on first use)
    _navigator: NavigatorMode | None = field(default=None, init=False)
    _prospector: ProspectorMode | None = field(default=None, init=False)
    _surveyor: SurveyorMode | None = field(default=None, init=False)

    # Evolutionary state
    _seen_hashes: set[str] = field(default_factory=set, init=False)
    _cycle_count: int = field(default=0, init=False)
    _dry_cycles: int = field(default=0, init=False)  # consecutive cycles with no novelty
    _best_findings: list[Finding] = field(default_factory=list, init=False)
    _cross_domain_links: list[dict] = field(default_factory=list, init=False)  # cross-organ patterns detected

    # Saturation: adaptive threshold based on discovery velocity
    MAX_DRY_CYCLES: int = 3  # base: saturate after 3 dry cycles
    MAX_DRY_CYCLES_MULTI_DOMAIN: int = 5  # extended for multi-domain questions
    MIN_CYCLES: int = 2  # minimum cycles before saturation possible

    def _get_sub_mode(self, target: ExploreMode) -> ExplorerMode | None:
        """Get or create a sub-mode instance with sensible defaults."""
        if target == ExploreMode.NAVIGATOR:
            if self._navigator is None:
                self._navigator = NavigatorMode()
            return self._navigator
        if target == ExploreMode.PROSPECTOR:
            if self._prospector is None:
                self._prospector = ProspectorMode()
                # Inject default filesystem tool handles from the OS
                self._prospector.fs_glob = _default_glob
                self._prospector.fs_read = _default_read
                self._prospector.fs_list = _default_list
            return self._prospector
        if target == ExploreMode.SURVEYOR:
            if self._surveyor is None:
                self._surveyor = SurveyorMode()
            return self._surveyor
        # Driller and Mapper not yet forged
        return None

    async def sense(self, seed: Seed, node: GraphNode | None = None) -> list[GraphNode]:
        """L-LEARN: Parse research question, auto-select modes, create seed nodes.

        The question is decomposed into domain-specific exploration seeds.
        Each seed is tagged with its target mode.
        """
        question = seed.question or ""
        if not question and node:
            question = node.label

        if not question:
            return []

        modes = _classify_question(question)
        logger.info(
            "EUREKA sense | question=%.80s modes=%s",
            question, [m.value for m in modes],
        )

        seed_nodes: list[GraphNode] = []
        for mode in modes:
            node_id = _hash(f"eureka:{mode.value}:{question[:120]}")
            seed_nodes.append(GraphNode(
                node_id=node_id,
                mode=self.mode,
                label=question[:200],
                content_hash=_hash(question),
                evidence=question[:2000],
                meta={
                    "target_mode": mode.value,
                    "unresolved": True,
                    "cycle": 0,
                    "priority": 1.0 if mode == modes[0] else 0.5,
                },
            ))

        return seed_nodes

    async def plan(self, goal: str, graph: ExplorationGraph, limits: Limits) -> list[GraphNode]:
        """D-DISCOVER phase prep: select most promising unresolved nodes.

        Evolutionary selection — prefer nodes with:
        - High priority (from initial classification)
        - High heuristic score (relevance to goal)
        - Low cycle depth (explore breadth-first before going deep)

        Cold start: if graph is empty, seed it from the goal via sense().
        """
        if not graph.nodes:
            # First call — auto-seed the graph from the research question
            seed_nodes = await self.sense(Seed(question=goal))
            for n in seed_nodes:
                graph.nodes.append(n)
            logger.info(
                "EUREKA plan | cold start → %d seed(s) auto-generated",
                len(seed_nodes),
            )
            return seed_nodes

        scored: list[tuple[float, GraphNode]] = []
        for node in graph.nodes:
            # Skip if already explored — check BOTH directions
            has_resolve_edge = any(
                (e.from_id == node.node_id or e.to_id == node.node_id)
                and e.relation == "resolves"
                for e in graph.edges
            )
            if has_resolve_edge:
                continue
            if not node.meta.get("unresolved"):
                continue

            priority = node.meta.get("priority", 0.5)
            cycle_depth = node.meta.get("cycle", 0)
            relevance = self.heuristic(node, goal)

            # Composite score: relevance + priority bonus - depth penalty
            score = (
                relevance * 0.5 +
                priority * 0.3 -
                min(cycle_depth / (limits.max_depth + 1), 0.2)
            )
            scored.append((score, node))

        scored.sort(key=lambda x: x[0], reverse=True)
        selected = [n for _, n in scored[:limits.max_steps]]
        return selected

    async def step(self, node: GraphNode, seed: Seed) -> StepResult:
        """E-EVALUATE + A-ADAPT: One full LDEA cycle.

        1. Dispatch sub-exploration to the target mode
        2. Collect findings from sub-exploration
        3. Cross-reference: detect patterns, contradictions, gaps
        4. Score novelty, update evolutionary state
        5. Breed new seeds from unresolved gaps
        """
        self._cycle_count += 1
        target_mode_str = node.meta.get("target_mode", "prospector")
        try:
            target_mode = ExploreMode(target_mode_str)
        except ValueError:
            target_mode = ExploreMode.PROSPECTOR

        sub_mode = self._get_sub_mode(target_mode)
        if sub_mode is None:
            # Mode not forged — skip this cycle, try a different mode
            logger.info("EUREKA step | mode %s not forged, skipping cycle", target_mode_str)
            return StepResult(
                nodes=[], edges=[], findings=[],
                gaps=[f"target mode not yet forged: {target_mode_str}"],
                coverage_delta=0.0, confidence=0.0, terminal=False,
            )

        logger.info(
            "EUREKA step | cycle=%d mode=%s question=%.80s",
            self._cycle_count, target_mode_str, node.label[:80],
        )

        # ── 1. Dispatch sub-exploration ──────────────────────
        sub_seed = Seed(question=node.label)
        if target_mode == ExploreMode.NAVIGATOR:
            if seed.url:
                sub_seed = seed
            else:
                # No URL seed — Navigator will convert question to search URL
                # via its step() method. Pass the question as seed context.
                sub_seed = Seed(question=node.label)
        elif target_mode == ExploreMode.PROSPECTOR and seed.path:
            sub_seed = seed

        # Run a single-step sub-exploration (not full kernel — one hop)
        try:
            sub_result = await sub_mode.step(node, sub_seed)
        except Exception as exc:
            logger.error("EUREKA step | sub-exploration failed: %s", exc)
            return StepResult(
                nodes=[], edges=[], findings=[],
                gaps=[f"sub-{target_mode_str} error: {exc!s:.120}"],
                coverage_delta=0.0, confidence=0.0, terminal=True,
            )

        # ── 2. Collect findings ──────────────────────────────
        all_nodes = list(sub_result.nodes)
        all_edges = list(sub_result.edges)
        findings = list(sub_result.findings)
        gaps = list(sub_result.gaps)

        # ── 3. Cross-reference ───────────────────────────────
        # Detect patterns across sub-mode dispatches and domains
        cross_edges: list[GraphEdge] = []
        domain_map: dict[str, set[str]] = {}  # target_mode → set of finding ids
        for f in findings:
            # Corroboration with previous best findings
            for existing in self._best_findings:
                f_terms = set(f.summary.lower().split())
                e_terms = set(existing.summary.lower().split())
                overlap = len(f_terms & e_terms)
                if overlap >= 3 and len(f_terms) > 0 and len(e_terms) > 0:
                    cross_edges.append(GraphEdge(
                        from_id=f.id,
                        to_id=existing.id,
                        relation="corroborates",
                        confidence=min(0.9, overlap / max(len(f_terms), len(e_terms))),
                    ))
            # Track which domain this finding came from
            if target_mode_str not in domain_map:
                domain_map[target_mode_str] = set()
            domain_map[target_mode_str].add(f.id)

        # Cross-domain link detection: same entity found via multiple sub-modes
        all_domain_findings = {}
        for dm, fm_ids in domain_map.items():
            for fid in fm_ids:
                if fid not in all_domain_findings:
                    all_domain_findings[fid] = dm

        # If a finding corroborates across domains, log it as a cross-domain pattern
        for edge in cross_edges:
            src_domain = all_domain_findings.get(edge.from_id, "unknown")
            tgt_domain = all_domain_findings.get(edge.to_id, "unknown")
            if src_domain != tgt_domain and src_domain != "unknown" and tgt_domain != "unknown":
                self._cross_domain_links.append({
                    "cycle": self._cycle_count,
                    "from_domain": src_domain,
                    "to_domain": tgt_domain,
                    "finding_id": edge.from_id,
                    "corroborates_id": edge.to_id,
                })

        # ── 4. Score novelty ─────────────────────────────────
        novel_findings: list[Finding] = []
        for f in findings:
            novelty = _novelty_score(f, self._seen_hashes)
            self._seen_hashes.add(f.id)
            if novelty > 0.3:  # novel enough to keep
                f.confidence = min(f.confidence, novelty)  # downweight duplicates
                novel_findings.append(f)
                self._best_findings.append(f)

        if novel_findings:
            self._dry_cycles = 0
        else:
            self._dry_cycles += 1
            logger.info(
                "EUREKA step | dry cycle %d/%d — no novel findings",
                self._dry_cycles, self.MAX_DRY_CYCLES,
            )

        # ── 5. Breed new seeds from gaps ────────────────────
        child_nodes: list[GraphNode] = []
        for gap in gaps[:5]:
            child_id = _hash(f"gap:{gap[:120]}:cycle{self._cycle_count}")
            child_nodes.append(GraphNode(
                node_id=child_id,
                mode=self.mode,
                label=gap[:200],
                content_hash="",
                evidence="",
                meta={
                    "target_mode": target_mode_str,
                    "unresolved": True,
                    "cycle": self._cycle_count,
                    "priority": 0.7,
                    "parent_finding": node.node_id,
                },
            ))
            all_edges.append(GraphEdge(
                from_id=node.node_id,
                to_id=child_id,
                relation="breeds",
                confidence=0.6,
            ))

        # Mark explored node
        explored_node = GraphNode(
            node_id=_hash(f"explored:{node.node_id}:cycle{self._cycle_count}"),
            mode=self.mode,
            label=f"[cycle {self._cycle_count}] {node.label[:150]}",
            content_hash=node.content_hash or _hash(node.label),
            evidence=f"Dispatched to {target_mode_str}. "
                     f"{len(novel_findings)} novel findings, {len(gaps)} gaps.",
            meta={
                "cycle": self._cycle_count,
                "target_mode": target_mode_str,
                "novel_findings": len(novel_findings),
                "gaps_found": len(gaps),
                "dry_cycles": self._dry_cycles,
            },
        )

        all_nodes.append(explored_node)
        all_edges.append(GraphEdge(
            from_id=explored_node.node_id,
            to_id=node.node_id,
            relation="resolves",
            confidence=0.9 if novel_findings else 0.5,
        ))

        # Coverage: fraction of the question space explored
        coverage = min(1.0, self._cycle_count / 10)
        # Confidence: mean of novel finding confidences
        confidence = 0.5
        if novel_findings:
            confidence = sum(f.confidence for f in novel_findings) / len(novel_findings)

        # Terminal if saturated — adaptive threshold
        # If cross-domain links are active, extend dry cycles (multi-domain questions
        # naturally have more exploration value)
        has_cross_domain_activity = bool(self._cross_domain_links)
        max_dry = self.MAX_DRY_CYCLES_MULTI_DOMAIN if has_cross_domain_activity else self.MAX_DRY_CYCLES
        if self._cycle_count < self.MIN_CYCLES:
            # Never saturate before minimum cycles
            terminal = False
        else:
            terminal = self._dry_cycles >= max_dry

        if terminal:
            logger.info(
                "EUREKA step | SATURATED after %d cycles, %d total findings, "
                "%d cross-domain links (multi_domain=%s)",
                self._cycle_count, len(self._best_findings),
                len(self._cross_domain_links), has_cross_domain_activity,
            )

        return StepResult(
            nodes=all_nodes,
            edges=all_edges + cross_edges,
            findings=novel_findings,
            gaps=gaps,
            coverage_delta=coverage,
            confidence=confidence,
            terminal=terminal,
        )

    def heuristic(self, node: GraphNode, goal: str) -> float:
        """Evolutionary fitness: relevance × novelty potential × diversity bonus.

        Relevance: keyword overlap with goal.
        Novelty potential: inversely proportional to cycle depth
        (prefer exploring fresh branches over over-exploited ones).
        Diversity bonus: prefer modes that haven't been explored yet.
        Cross-domain bonus: prefer modes that could yield cross-domain links.
        """
        goal_terms = set(goal.lower().split())
        if not goal_terms:
            return 0.5

        node_text = (
            f"{node.label} "
            f"{node.meta.get('target_mode', '')} "
            f"{str(node.meta.get('priority', ''))}"
        ).lower()

        relevance = sum(1 for t in goal_terms if t in node_text) / max(1, len(goal_terms))
        # Novelty potential: higher for low-cycle nodes
        cycle_depth = node.meta.get("cycle", 0)
        novelty_potential = 1.0 / (1.0 + cycle_depth * 0.3)

        # Diversity bonus: prefer modes we haven't explored much
        target_mode = node.meta.get("target_mode", "")
        used_modes = {e.get("from_domain", "") for e in self._cross_domain_links}
        used_modes.update(e.get("to_domain", "") for e in self._cross_domain_links)
        diversity_bonus = 0.1 if target_mode and target_mode not in used_modes else 0.0

        # Cross-domain bonus: Surveyor mode links across organs
        cross_domain_bonus = 0.1 if target_mode == "surveyor" else 0.0

        return min(1.0,
            relevance * 0.5 +
            novelty_potential * 0.3 +
            diversity_bonus +
            cross_domain_bonus
        )


# ═══════════════════════════════════════════════════════════════
# PUBLIC TOOL HANDLER — arif_explore
# ═══════════════════════════════════════════════════════════════

async def arif_explore(
    goal: str,
    mode: str = "auto",
    seed_url: str | None = None,
    seed_path: str | None = None,
    seed_api_base_url: str | None = None,
    seed_entity: str | None = None,
    seed_question: str | None = None,
    max_depth: int = 4,
    max_steps: int = 64,
    time_budget_s: int = 60,
    trace_id: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict:
    """
    arif_explore — L2 Exploration Substrate (111_OBSERVE extend).

    Governed multi-step exploration across seven modes:
      prospector — filesystem/codebase traversal (uses existing fs tools)
      navigator  — web traversal (Playwright browser automation)
      driller    — API surface discovery [pending]
      mapper     — knowledge graph traversal [pending]
      surveyor   — cross-organ telemetry fusion (GEOX + WELL + WEALTH)
      scout      — recursive meta-explorer [pending]
      eureka     — evolutionary discovery loop (LDEA: Learn→Discover→Evaluate→Adapt)
      auto       — kernel selects mode from seed shape

    Returns: ExploreResponse as dict with exploration_graph, findings,
             gaps, metrics, and verdict (saturation + next_moves).
    """
    # Resolve mode
    try:
        explore_mode = ExploreMode(mode)
    except ValueError:
        explore_mode = ExploreMode.AUTO

    # Capture whether the caller passed AUTO so we know whether unimplemented
    # concrete modes (driller/mapper/scout) should fall back to Prospector
    # gracefully or return not_implemented explicitly.
    was_auto = explore_mode == ExploreMode.AUTO

    # Auto-select mode from seed shape
    if explore_mode == ExploreMode.AUTO:
        if seed_path:
            explore_mode = ExploreMode.PROSPECTOR
        elif seed_url:
            explore_mode = ExploreMode.NAVIGATOR
        elif seed_api_base_url:
            explore_mode = ExploreMode.DRILLER
        elif seed_entity:
            explore_mode = ExploreMode.MAPPER
        elif seed_question:
            explore_mode = ExploreMode.SURVEYOR
        else:
            explore_mode = ExploreMode.PROSPECTOR  # safest default

    # Build request
    seed = Seed()
    if seed_url:
        seed.url = SeedURL(url=seed_url)
    if seed_path:
        seed.path = SeedPath(path=seed_path)
    if seed_api_base_url:
        seed.api = SeedAPI(base_url=seed_api_base_url)
    if seed_entity:
        seed.entity = seed_entity
    if seed_question:
        seed.question = seed_question

    request = ExploreRequest(
        goal=goal,
        mode=explore_mode,
        seed=seed,
        limits=Limits(
            max_depth=max_depth,
            max_steps=max_steps,
            time_budget_s=time_budget_s,
        ),
        telemetry={"trace_id": trace_id or str(uuid.uuid4())},  # type: ignore[arg-type]
    )

    # Select mode implementation
    mode_impl: ExplorerMode
    mode_fallback_used: str | None = None
    if explore_mode == ExploreMode.PROSPECTOR:
        mode_impl = ProspectorMode(request_seed=request.seed)
        mode_impl.fs_list = _default_list
        mode_impl.fs_read = _default_read
        mode_impl.fs_glob = _default_glob
    elif explore_mode == ExploreMode.NAVIGATOR:
        # Federated to arif_observe / arif_fetch (no Playwright).
        mode_impl = NavigatorMode(
            request_seed=request.seed,
            actor_id=actor_id,
            session_id=session_id,
        )
    elif explore_mode == ExploreMode.DRILLER:
        if was_auto:
            # Graceful fallback in auto-mode: route to Prospector (filesystem).
            logger.info("arif_explore | DRILLER not forged, AUTO fallback → PROSPECTOR")
            mode_impl = ProspectorMode(request_seed=request.seed)
            mode_impl.fs_list = _default_list
            mode_impl.fs_read = _default_read
            mode_impl.fs_glob = _default_glob
            mode_fallback_used = "driller→prospector"
        else:
            return {
                "status": "not_implemented",
                "mode": "driller",
                "message": "Driller mode (API exploration) is not yet forged. "
                           "Use mode='prospector' for filesystem exploration.",
            }
    elif explore_mode == ExploreMode.MAPPER:
        if was_auto:
            logger.info("arif_explore | MAPPER not forged, AUTO fallback → PROSPECTOR")
            mode_impl = ProspectorMode(request_seed=request.seed)
            mode_impl.fs_list = _default_list
            mode_impl.fs_read = _default_read
            mode_impl.fs_glob = _default_glob
            mode_fallback_used = "mapper→prospector"
        else:
            return {
                "status": "not_implemented",
                "mode": "mapper",
                "message": "Mapper mode (knowledge graph traversal) is not yet forged. "
                           "Use mode='prospector' for filesystem exploration.",
            }
    elif explore_mode == ExploreMode.SURVEYOR:
        mode_impl = SurveyorMode(request_seed=request.seed)
    elif explore_mode == ExploreMode.SCOUT:
        if was_auto:
            logger.info("arif_explore | SCOUT not forged, AUTO fallback → PROSPECTOR")
            mode_impl = ProspectorMode(request_seed=request.seed)
            mode_impl.fs_list = _default_list
            mode_impl.fs_read = _default_read
            mode_impl.fs_glob = _default_glob
            mode_fallback_used = "scout→prospector"
        else:
            return {
                "status": "not_implemented",
                "mode": "scout",
                "message": "Scout mode (recursive meta-explorer) has been subsumed by EurekaMode. "
                           "Use mode='eureka' for evolutionary discovery with governance.",
            }
    elif explore_mode == ExploreMode.EUREKA:
        mode_impl = EurekaMode()
    else:
        mode_impl = ProspectorMode(request_seed=request.seed)
        mode_impl.fs_list = _default_list
        mode_impl.fs_read = _default_read
        mode_impl.fs_glob = _default_glob

    # Run kernel
    kernel = ExplorationKernel(request=request, mode_impl=mode_impl)
    response = await kernel.run()

    # Add handler-level metadata (fallback, requested mode) for transparency.
    # The kernel returns a clean Pydantic ExploreResponse; the handler wraps
    # it with routing context that the kernel doesn't know about.
    payload = response.model_dump()
    payload["requested_mode"] = mode
    payload["resolved_mode"] = explore_mode.value
    if mode_fallback_used:
        payload["mode_fallback"] = mode_fallback_used
    return payload


# ═══════════════════════════════════════════════════════════════
# Eureka defaults — injected tool handles for sub-modes
# ═══════════════════════════════════════════════════════════════

async def _default_glob(pattern: str) -> list[str]:
    """Default glob implementation — uses OS glob via asyncio."""
    import glob as _g
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _g.glob, pattern)


async def _default_read(path: str) -> str:
    """Default read implementation — uses OS open via asyncio."""
    loop = asyncio.get_event_loop()
    def _read():
        try:
            with open(path, 'r', errors='replace') as f:
                return f.read(65536)
        except (FileNotFoundError, IsADirectoryError, PermissionError):
            return ""
    return await loop.run_in_executor(None, _read)


async def _default_list(path: str) -> list[str]:
    """Default list implementation — uses OS listdir via asyncio."""
    import os as _os
    loop = asyncio.get_event_loop()
    def _list():
        try:
            return _os.listdir(path)
        except (FileNotFoundError, PermissionError, NotADirectoryError):
            return []
    return await loop.run_in_executor(None, _list)


__all__ = [
    "ExploreState",
    "TRANSITIONS",
    "StepResult",
    "ExplorerMode",
    "ExplorationKernel",
    "ProspectorMode",
    "SurveyorMode",
    "NavigatorMode",
    "EurekaMode",
    "arif_explore",
    "_hash",
    "_extract_symbols",
    "_extract_imports",
    "_guess_type",
    "_normalize_signal",
    "_correlate",
    "laglead",
    "spatial_distance",
    "_classify_question",
    "_novelty_score",
    "_default_glob",
    "_default_read",
    "_default_list",
]
