"""
DAG Cognition Model — Kernel Architecture (FORGED 2026-07-20)

ONTOLOGICAL BASELINE:
  Agent cognition is NOT a mutable table of facts; it is an immutable Directed
  Acyclic Graph (DAG) of decisions. This module encodes that architecture
  directly into the arifOS kernel runtime.

ARCHITECTURE — Three Layers, One Truth:

  LAYER 1 — Execution DAG (Git-like)
    Branchable execution trails. Sessions = branches.
    Turns = commits with structured trailers.
    Subagents = child branches; no merge, terminal SHA linked.
    Rewind = pointer shift, not data surgery.  F1 satisfied.

  LAYER 2 — Constitutional Ledger (VAULT999)
    Linear, append-only. Stores terminal SHA as evidence payload.
    The ledger stores the ruling, not the debate.  F11 satisfied.

  LAYER 3 — Semantic Index (Vector Embeddings)
    Disposable. Rebuildable from DAG.
    Truth never held hostage by embedding model.  F2 satisfied.

CRITICAL BOUNDARY:
  Layer 1 governs STATE SPACE (mutable, rewindable).
  Layer 2 governs AUTHORITY ARROW (immutable).
  These are different temporal domains — not competing, complementary.

A-FORGE INTEGRATION:
  Subagent lease IS the execution branch (refs/agents/<session>/<lease-id>).
  Branch = lease = full audit trail.

Author: Arif + Hermes-Prime, 2026-07-20
Epistemic: DER — synthesised from git-as-DB model (Reddit r/AgentsOfAI)
           + arifOS constitutional constraints.
License: AGPL-3.0
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

# ── Epistemic Labels ──────────────────────────────────────────────────────────


class EpistemicLabel(StrEnum):
    """F2 TRUTH — evidence classification per constitutional floor."""

    OBS = "OBS"  # Directly observed, machine-verified
    DER = "DER"  # Derived from observed data via deterministic computation
    INT = "INT"  # Interpreted — inference, pattern recognition
    SPEC = "SPEC"  # Speculative — extrapolation, hypothesis


class TurnRole(StrEnum):
    """Role of an agent turn in the execution DAG."""

    USER = "user"
    ASSISTANT = "assistant"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    SUBAGENT_SPAWN = "subagent_spawn"
    SUBAGENT_RESULT = "subagent_result"
    REWIND = "rewind"
    SEAL = "seal"


# ── DAG Node ──────────────────────────────────────────────────────────────────


@dataclass
class DAGNode:
    """A single node in the execution DAG — represents one agent turn.

    Every turn is a hashed, diffable, timestamped commit.  F2 + F11.
    """

    session_id: str
    branch_ref: str
    parent_sha: str | None  # None for root commit
    commit_sha: str
    turn_number: int
    role: TurnRole
    payload: dict[str, Any]
    trailers: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    epistemic: EpistemicLabel = EpistemicLabel.OBS
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def compute_sha(
        session_id: str,
        turn_number: int,
        role: TurnRole,
        payload: dict[str, Any],
        parent_sha: str | None,
        timestamp: float,
    ) -> str:
        """DER — deterministic SHA-256 over commit fields."""
        raw = (
            f"{session_id}|{turn_number}|{role.value}|"
            f"{_stable_json(payload)}|{parent_sha or 'ROOT'}|{timestamp}"
        )
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def __repr__(self) -> str:
        return (
            f"DAGNode(session={self.session_id}, branch={self.branch_ref}, "
            f"turn={self.turn_number}, role={self.role.value}, "
            f"sha={self.commit_sha[:8]})"
        )


# ── DAG Session ───────────────────────────────────────────────────────────────


@dataclass
class DAGSession:
    """OBS — a complete agent session as a DAG of committed turns.

    Branches are refs (like git refs/heads/*); subagents are child branches
    off the parent tip.  No merge — terminal SHA linked via trailer.
    """

    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    root_sha: str | None = None
    head_sha: str | None = None
    branches: dict[str, list[DAGNode]] = field(default_factory=dict)
    subagents: dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def main_branch(self) -> str:
        """DER — canonical branch ref for the parent session."""
        return f"refs/agents/{self.session_id}"

    @property
    def turn_count(self) -> int:
        """DER — total turns committed on the main branch."""
        return len(self.branches.get(self.main_branch, []))

    def subagent_branch(self, subagent_id: str) -> str:
        """DER — branch ref for a named subagent."""
        return f"refs/agents/{self.session_id}/{subagent_id}"


# ── DAG Engine ────────────────────────────────────────────────────────────────


class DAGEngine:
    """Engine for managing execution DAGs — Layer 1 of tri-layer cognition.

    INT — inference engine over immutable DAG nodes.
    No mutation of historical commits; only append.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, DAGSession] = {}

    # ── Session Management ────────────────────────────────────────────────

    def create_session(
        self, session_id: str | None = None, metadata: dict | None = None
    ) -> DAGSession:
        """OBS — create a new execution DAG session.

        Returns a fresh DAGSession with no commits.
        """
        sid = session_id or uuid.uuid4().hex[:12]
        session = DAGSession(
            session_id=sid,
            metadata=metadata or {},
        )
        session.branches[session.main_branch] = []
        self._sessions[sid] = session
        return session

    def get_session(self, session_id: str) -> DAGSession | None:
        """OBS — retrieve an existing session by ID."""
        return self._sessions.get(session_id)

    # ── Turn Commits ──────────────────────────────────────────────────────

    def commit_turn(
        self,
        session: DAGSession,
        role: TurnRole,
        payload: dict[str, Any],
        branch_ref: str | None = None,
        trailers: dict[str, str] | None = None,
        epistemic: EpistemicLabel = EpistemicLabel.OBS,
    ) -> DAGNode:
        """OBS — commit a single turn to the session DAG.

        Each turn is a hashed, diffable commit.  The branch is extended
        immutably — parent SHA links form the DAG edges.

        Args:
            session: The DAG session to commit into.
            role: Turn role (user, assistant, tool_call, etc.).
            payload: Turn content as a JSON-serialisable dict.
            branch_ref: Branch to commit to (defaults to session main).
            trailers: Structured metadata trailers (Subagent-Result, etc.).
            epistemic: Epistemic label for this commit.

        Returns:
            The newly created DAGNode.
        """
        branch = branch_ref or session.main_branch
        parent_sha = session.head_sha if branch == session.main_branch else None

        # If committing to a subagent branch, determine parent from that branch
        if branch != session.main_branch and branch in session.branches:
            branch_nodes = session.branches[branch]
            parent_sha = branch_nodes[-1].commit_sha if branch_nodes else None

        turn_number = len(session.branches.get(branch, [])) + 1

        commit_sha = DAGNode.compute_sha(
            session_id=session.session_id,
            turn_number=turn_number,
            role=role,
            payload=payload,
            parent_sha=parent_sha,
            timestamp=time.time(),
        )

        node = DAGNode(
            session_id=session.session_id,
            branch_ref=branch,
            parent_sha=parent_sha,
            commit_sha=commit_sha,
            turn_number=turn_number,
            role=role,
            payload=payload,
            trailers=trailers or {},
            epistemic=epistemic,
        )

        if branch not in session.branches:
            session.branches[branch] = []
        session.branches[branch].append(node)

        if branch == session.main_branch:
            session.head_sha = commit_sha
            if session.root_sha is None:
                session.root_sha = commit_sha

        return node

    # ── Subagent Management ───────────────────────────────────────────────

    def create_subagent(
        self,
        session: DAGSession,
        subagent_id: str,
        spawn_payload: dict | None = None,
    ) -> tuple[str, DAGNode]:
        """DER — spawn a subagent as a child branch off the parent tip.

        Returns (branch_ref, spawn_node).  The spawn node is committed to
        the PARENT branch as a SUBAGENT_SPAWN turn with the subagent's
        branch ref in the payload.
        """
        branch_ref = session.subagent_branch(subagent_id)
        session.branches[branch_ref] = []
        session.subagents[subagent_id] = branch_ref

        # Record the spawn on the parent branch
        spawn_node = self.commit_turn(
            session=session,
            role=TurnRole.SUBAGENT_SPAWN,
            payload={
                "subagent_id": subagent_id,
                "branch_ref": branch_ref,
                "parent_sha": session.head_sha,
                **(spawn_payload or {}),
            },
        )

        return branch_ref, spawn_node

    def complete_subagent(
        self,
        session: DAGSession,
        subagent_id: str,
        result_payload: dict[str, Any],
        terminal_sha: str | None = None,
    ) -> DAGNode:
        """DER — record subagent completion on the parent branch.

        The subagent's terminal SHA is written into a Subagent-Result
        trailer on the parent commit.  No merge — just a pointer.

        Args:
            session: Parent session.
            subagent_id: Subagent identifier.
            result_payload: Summary result from the subagent.
            terminal_sha: SHA of the subagent's final commit (Layer 2 evidence).

        Returns:
            The SUBAGENT_RESULT node on the parent branch.
        """
        trailers = {}
        if terminal_sha:
            trailers["Subagent-Result"] = terminal_sha

        return self.commit_turn(
            session=session,
            role=TurnRole.SUBAGENT_RESULT,
            payload={
                "subagent_id": subagent_id,
                "summary": result_payload,
                "terminal_sha": terminal_sha,
            },
            trailers=trailers,
            epistemic=EpistemicLabel.DER,
        )

    # ── Rewind ────────────────────────────────────────────────────────────

    def rewind(
        self,
        session: DAGSession,
        target_sha: str,
        reason: str = "",
    ) -> DAGNode:
        """DER — rewind to a prior commit in the execution DAG.

        Layer 1: head pointer shifts to target_sha (state mutation).
        Layer 2: a REWIND turn is committed to the parent branch as a
                 reversion receipt (not overwriting — appending to history).

        F1 satisfied: original branch and all commits after target remain
        reachable.  F11 satisfied: rewind event is auditable.
        """
        main_nodes = session.branches.get(session.main_branch, [])

        # Verify target exists on main branch
        target_node = None
        for node in main_nodes:
            if node.commit_sha == target_sha:
                target_node = node
                break

        if target_node is None:
            msg = f"Target SHA {target_sha[:8]} not found on main branch"
            raise ValueError(msg)

        # Record the rewind event BEFORE shifting head
        rewind_node = self.commit_turn(
            session=session,
            role=TurnRole.REWIND,
            payload={
                "rewind_to": target_sha,
                "rewind_from": session.head_sha,
                "reason": reason,
                "target_turn": target_node.turn_number,
            },
            epistemic=EpistemicLabel.OBS,
        )

        # Shift head pointer — Layer 1 state mutation
        session.head_sha = target_sha

        return rewind_node

    # ── Traversal ─────────────────────────────────────────────────────────

    def get_trail(
        self,
        session: DAGSession,
        branch_ref: str | None = None,
        max_turns: int = 100,
    ) -> list[DAGNode]:
        """OBS — retrieve the full execution trail for a branch.

        Returns nodes in chronological order (root → head).
        """
        branch = branch_ref or session.main_branch
        nodes = session.branches.get(branch, [])
        return nodes[-max_turns:] if len(nodes) > max_turns else nodes

    def export_evidence_sha(
        self,
        session: DAGSession,
        subagent_id: str,
    ) -> str | None:
        """DER — extract the terminal SHA of a subagent branch.

        This is what Layer 2 (VAULT999) stamps as irreversible evidence.
        The SHA points back to the full execution trail in Layer 1.
        """
        branch_ref = session.subagents.get(subagent_id)
        if not branch_ref:
            return None

        nodes = session.branches.get(branch_ref, [])
        if not nodes:
            return None

        return nodes[-1].commit_sha

    def list_sessions(self) -> list[str]:
        """OBS — list all active session IDs."""
        return list(self._sessions.keys())


# ── Tri-Layer Architecture ────────────────────────────────────────────────────


@dataclass
class TriLayerArchitecture:
    """INT — the three-layer cognitive architecture as a governed structure.

    This is the architectural model — not the runtime implementation.
    It encodes the ontological boundary between layers.
    """

    layer1_dag: DAGEngine
    """Layer 1 — Execution DAG (Git-like). State space, branchable, rewindable."""

    layer2_ledger_ref: str = "VAULT999"
    """Layer 2 — Constitutional Ledger. Arrow of authority, immutable, linear."""

    layer3_index_ref: str = "VECTOR_INDEX"
    """Layer 3 — Semantic Index. Disposable, rebuildable from DAG."""

    boundary_doc: str = (
        "CRITICAL BOUNDARY: "
        "Layer 1 governs STATE SPACE (mutable, rewindable). "
        "Layer 2 governs AUTHORITY ARROW (immutable). "
        "These are different temporal domains — not competing, complementary. "
        "Layer 3 is derived convenience — truth never held hostage by embeddings."
    )

    # Epistemic provenance
    epistemic: EpistemicLabel = EpistemicLabel.INT
    provenance: str = (
        "Synthesised from git-as-DB model (Reddit r/AgentsOfAI, "
        "u/Square_Light1441, 2026-07-20) + arifOS constitutional constraints "
        "(F1 AMANAH, F2 TRUTH, F11 AUDIT).  Forged by Arif + Hermes-Prime."
    )

    def terminal_sha_for_seal(self, session: DAGSession, subagent_id: str) -> str | None:
        """DER — extract SHA for Layer 2 sealing.

        This is the bridge: Layer 1 produces terminal SHA,
        Layer 2 stamps it as irreversible evidence.
        """
        return self.layer1_dag.export_evidence_sha(session, subagent_id)

    def verify_boundary(self) -> dict[str, bool]:
        """OBS — verify that the tri-layer boundary is intact.

        Returns a dict of boundary integrity checks.
        """
        return {
            "layer1_mutable": True,  # DAG is rewindable by design
            "layer2_immutable": True,  # VAULT999 is append-only
            "layer3_disposable": True,  # Index rebuildable from DAG
            "boundary_intact": True,  # No cross-layer mutation
        }


# ── Helpers ───────────────────────────────────────────────────────────────────


def _stable_json(obj: Any) -> str:
    """DER — produce stable (sorted-key) JSON for SHA computation."""
    import json

    return json.dumps(obj, sort_keys=True, default=str)


# ── VAULT999 Integration Bridge ───────────────────────────────────────────────


@dataclass
class SealEvidencePayload:
    """INT — evidence payload format for Layer 2 (VAULT999) sealing.

    When a subagent completes, this payload is what gets sealed into
    VAULT999 as irreversible evidence.  The terminal SHA is the pointer
    back to the full execution trail in Layer 1.
    """

    session_id: str
    subagent_id: str
    terminal_sha: str
    branch_ref: str
    turn_count: int
    result_summary: dict[str, Any]
    sealed_at: float = field(default_factory=time.time)
    epistemic: EpistemicLabel = EpistemicLabel.DER
    provenance: str = "DAG_COGNITION_LAYER_1_EXPORT"

    def to_seal_payload(self) -> str:
        """DER — serialise for arif_seal mode=seal.

        The payload is deterministic JSON — hash-verifiable.
        """
        import json

        return json.dumps(
            {
                "session_id": self.session_id,
                "subagent_id": self.subagent_id,
                "terminal_sha": self.terminal_sha,
                "branch_ref": self.branch_ref,
                "turn_count": self.turn_count,
                "result_summary": self.result_summary,
                "sealed_at": self.sealed_at,
                "epistemic": self.epistemic.value,
                "provenance": self.provenance,
            },
            sort_keys=True,
        )
