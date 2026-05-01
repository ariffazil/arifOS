"""
arifos/runtime/dag_executor.py — Constitutional DAG Executor

Constitutionally governed Directed Acyclic Graph (DAG) executor for
multi-step agentic tasks. Walks task graphs in dependency order,
with pre-execution F1 (Amanah) irreversibility checks at each node.

DITEMPA BUKAN DIBERI — Forged, Not Given
Author: 888_VALIDATOR | Version: 2026.04.10-CANONICAL
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class NodeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    HELD = "held"  # 888_HOLD — awaiting human ratification


class VerdictStatus(str, Enum):
    SEAL = "SEAL"
    SABAR = "SABAR"
    HOLD_888 = "HOLD_888"
    VOID = "VOID"
    PARTIAL = "PARTIAL"


@dataclass
class DAGNode:
    """A single executable node in the task graph."""
    id: str
    tool_name: str
    mode: str
    args: dict[str, Any]
    dependencies: list[str] = field(default_factory=list)
    status: NodeStatus = NodeStatus.PENDING
    result: Any = None
    verdict: str | None = None
    error: str | None = None
    irreversibility_score: float = 0.0
    floor_violations: list[str] = field(default_factory=list)
    plan_id: str = ""  # Canonical plan that authorized this node


@dataclass
class ExecutionResult:
    """Result of a full DAG execution."""
    dag_id: str
    total_nodes: int
    completed: int
    failed: int
    held: int
    rolled_back: int
    results: dict[str, Any]
    verdicts: dict[str, str]
    halted_at_node: str | None = None
    halt_reason: str | None = None


class ConstitutionalDAGExecutor:
    """
    DAG executor with constitutional pre-checks at each node.

    Execution policy:
    1. Find all nodes whose dependencies are satisfied (COMPLETED nodes only)
    2. For each executable node: run Amanah irreversibility pre-check
    3. If CRITICAL irreversibility → 888_HOLD that node, halt progress
    4. Execute non-held nodes, collect results
    5. Repeat until all nodes processed or halt

    Rollback: If a node fails, all dependent nodes are marked ROLLED_BACK.
    """

    def __init__(
        self,
        dag_id: str,
        hold_manager=None,  # HoldStateManager instance
        irreversibility_scorer=None,  # AmanahIrreversibilityScorer instance
    ):
        self.dag_id = dag_id
        self.hold_manager = hold_manager
        self.scorer = irreversibility_scorer
        self.nodes: dict[str, DAGNode] = {}
        self._executed_order: list[str] = []
        self._halted = False
        self._halt_node: str | None = None
        self._halt_reason: str | None = None

    def add_node(
        self,
        node_id: str,
        tool_name: str,
        mode: str,
        args: dict[str, Any],
        dependencies: list[str] | None = None,
        plan_id: str = "",
    ) -> None:
        """Add a node to the DAG."""
        if node_id in self.nodes:
            raise ValueError(f"Node '{node_id}' already exists in DAG '{self.dag_id}'")
        self.nodes[node_id] = DAGNode(
            id=node_id,
            tool_name=tool_name,
            mode=mode,
            args=args,
            dependencies=dependencies or [],
            plan_id=plan_id,
        )
        logger.info(f"[DAG:{self.dag_id}] Added node '{node_id}' tool={tool_name}.{mode} deps={dependencies}")

    def _get_executable_nodes(self) -> list[DAGNode]:
        """Return all PENDING nodes whose dependencies are fully satisfied."""
        completed_ids = {
            n.id for n in self.nodes.values() if n.status == NodeStatus.COMPLETED
        }
        return [
            n for n in self.nodes.values()
            if n.status == NodeStatus.PENDING
            and all(dep in completed_ids for dep in n.dependencies)
        ]

    def _check_irreversibility(self, node: DAGNode) -> tuple[bool, float, list[str]]:
        """
        Run F1 Amanah pre-check on a node.
        Returns (triggers_hold, score, floor_violations).
        """
        if self.scorer is None:
            return False, 0.0, []

        result = self.scorer.evaluate_payload(
            tool_name=node.tool_name,
            mode=node.mode,
            args=node.args,
        )
        node.irreversibility_score = result.score
        node.floor_violations = result.floor_violations
        return result.triggers_888_hold, result.score, result.floor_violations

    def _trigger_hold(self, node: DAGNode, score: float, floor_violations: list[str]) -> None:
        """Trigger 888_HOLD for a node via HoldStateManager."""
        node.status = NodeStatus.HELD
        self._halted = True
        self._halt_node = node.id
        self._halt_reason = f"F1_AMANAH_CRITICAL: score={score} floors={floor_violations}"

        if self.hold_manager is not None:
            self.hold_manager.create_hold(
                execution_id=f"dag:{self.dag_id}:{node.id}",
                agent_id="dag_executor",
                action_type=f"{node.tool_name}.{node.mode}",
                reason=self._halt_reason,
                risk_level="CRITICAL",
                pathway=2,  # OFFER_HANDOVER
                floor_violations=floor_violations,
            )
            logger.warning(
                f"[DAG:{self.dag_id}] 888_HOLD triggered for node '{node.id}' "
                f"(score={score}, floors={floor_violations})"
            )

    async def execute(
        self,
        node_executor,  # Async callable: (tool_name, mode, args) -> result dict
    ) -> ExecutionResult:
        """
        Execute the DAG to completion or first halt.

        Args:
            node_executor: Async function/tool handler to execute each node.
                           Signature: async def execute_node(node: DAGNode) -> dict

        Returns:
            ExecutionResult with full run record
        """
        logger.info(f"[DAG:{self.dag_id}] Starting execution with {len(self.nodes)} nodes")
        max_iterations = len(self.nodes) * 2  # Safety cap
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Check halt condition
            if self._halted:
                break

            # Get next batch of executable nodes
            executable = self._get_executable_nodes()
            if not executable:
                break  # All PENDING nodes have unmet dependencies or we're done

            for node in executable:
                # ── F1 Amanah pre-check ──────────────────────────────────────────
                triggers_hold, score, floor_violations = self._check_irreversibility(node)

                if triggers_hold:
                    self._trigger_hold(node, score, floor_violations)
                    return self._build_result()

                # ── Execute node ────────────────────────────────────────────────
                node.status = NodeStatus.RUNNING
                try:
                    result = await node_executor(node)
                    node.result = result
                    node.status = NodeStatus.COMPLETED
                    node.verdict = result.get("verdict", "SEAL")
                    self._executed_order.append(node.id)
                    logger.info(f"[DAG:{self.dag_id}] Node '{node.id}' → {node.verdict}")
                except Exception as e:
                    node.status = NodeStatus.FAILED
                    node.error = str(e)
                    logger.error(f"[DAG:{self.dag_id}] Node '{node.id}' FAILED: {e}")
                    # Rollback dependents
                    self._rollback_dependents(node.id)
                    self._halted = True
                    self._halt_node = node.id
                    self._halt_reason = f"node_execution_error: {e}"
                    return self._build_result()

        return self._build_result()

    def _rollback_dependents(self, failed_node_id: str) -> None:
        """Mark all nodes that depend on a failed node as ROLLED_BACK."""
        for node in self.nodes.values():
            if failed_node_id in node.dependencies and node.status == NodeStatus.PENDING:
                node.status = NodeStatus.ROLLED_BACK
                logger.warning(f"[DAG:{self.dag_id}] Node '{node.id}' rolled back (dependency '{failed_node_id}' failed)")

    def _build_result(self) -> ExecutionResult:
        """Build execution result from current state."""
        counts = {s: 0 for s in NodeStatus}
        results: dict[str, Any] = {}
        verdicts: dict[str, str] = {}

        for node in self.nodes.values():
            counts[node.status] += 1
            if node.result is not None:
                results[node.id] = node.result
            if node.verdict is not None:
                verdicts[node.id] = node.verdict

        return ExecutionResult(
            dag_id=self.dag_id,
            total_nodes=len(self.nodes),
            completed=counts[NodeStatus.COMPLETED],
            failed=counts[NodeStatus.FAILED],
            held=counts[NodeStatus.HELD],
            rolled_back=counts[NodeStatus.ROLLED_BACK],
            results=results,
            verdicts=verdicts,
            halted_at_node=self._halt_node,
            halt_reason=self._halt_reason,
        )

    def get_state(self) -> dict[str, Any]:
        """Return current DAG state for inspection."""
        return {
            "dag_id": self.dag_id,
            "halted": self._halted,
            "halt_node": self._halt_node,
            "halt_reason": self._halt_reason,
            "nodes": {
                nid: {
                    "status": n.status.value,
                    "verdict": n.verdict,
                    "score": n.irreversibility_score,
                    "floors": n.floor_violations,
                    "deps": n.dependencies,
                    "error": n.error,
                    "plan_id": n.plan_id,
                }
                for nid, n in self.nodes.items()
            },
            "execution_order": self._executed_order,
        }

    def clear(self) -> None:
        """Reset DAG state for reuse."""
        for node in self.nodes.values():
            node.status = NodeStatus.PENDING
            node.result = None
            node.verdict = None
            node.error = None
            node.irreversibility_score = 0.0
            node.floor_violations = []
        self._executed_order = []
        self._halted = False
        self._halt_node = None
        self._halt_reason = None
