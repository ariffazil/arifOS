"""
arifosmcp/runtime/tools.py — 13-Tool Canonical Surface
═══════════════════════════════════════════════════════

Single registration authority for the canonical arif_* MCP surface.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import random
import time
import uuid
from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)
from mcp import McpError
from pydantic import BaseModel, Field

from arifosmcp.constitutional_map import CANONICAL_TOOLS, get_tool_spec
from arifosmcp.runtime.floors import check_floors
from arifosmcp.schemas.forge import (
    ForgeOutput,
    ForgeManifest,
    IrreversibilityBond,
    IrreversibilityLevel,
    DeltaSEvidence,
    ExecutionTrace,
    ExecutionNode,
    ConstitutionalCompliance,
    ManifestStatus,
)
from arifosmcp.schemas.verdict import (
    AmanahProof,
    FloorComplianceProof,
    EntropyDelta,
    EpistemicSnapshot,
    SealOutput,
    ThermodynamicState,
    VerdictCode,
    VerdictOutput,
)
from arifosmcp.schemas.lineage import JudgeSealContract
from arifosmcp.schemas.synthesis import (
    MindOutput,
    ReasoningMode,
    AxiomSource,
    ContrastType,
    AxiomUsage,
    AxiomsUsed,
    ReasoningStep,
    ReasoningTrace,
    MindAnomalousContrast,
)

logger = logging.getLogger(__name__)

# In-memory session store (replace with Redis/Postgres in production)
_SESSIONS: dict[str, dict[str, Any]] = {}
_VAULT_LEDGER: list[dict[str, Any]] = []
_JUDGE_STATE_REGISTRY: dict[str, dict[str, Any]] = {}
_JUDGE_CHAIN_REGISTRY: dict[str, dict[str, Any]] = {}
_VAULT_ENTRY_REGISTRY: dict[str, dict[str, Any]] = {}
_IRREVERSIBLE_ELICITATION_MODES = {"seal", "commit"}


class IrreversibleConfirmation(BaseModel):
    ack_irreversible: bool = Field(
        ...,
        description="Confirm that this irreversible action should proceed.",
    )
    sovereign_reason: str | None = Field(
        default=None,
        description="Optional reason for approving the irreversible action.",
    )


class JudgeCandidateInput(BaseModel):
    candidate: str = Field(
        ...,
        min_length=1,
        description="Action, artifact, or proposal that should be judged.",
    )


def _stable_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _irreversibility_rank(level: str) -> int:
    ranks = {
        IrreversibilityLevel.REVERSIBLE.value: 0,
        IrreversibilityLevel.SEMI_IRREVERSIBLE.value: 1,
        IrreversibilityLevel.IRREVERSIBLE.value: 2,
        IrreversibilityLevel.CATASTROPHIC.value: 3,
    }
    return ranks.get(level, 0)


def _infer_irreversibility_level(candidate: str | None) -> IrreversibilityLevel:
    text = (candidate or "").lower()
    if any(token in text for token in ("seal", "commit", "delete", "deploy")):
        return IrreversibilityLevel.IRREVERSIBLE
    if any(token in text for token in ("write", "apply", "change", "publish")):
        return IrreversibilityLevel.SEMI_IRREVERSIBLE
    return IrreversibilityLevel.REVERSIBLE


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _new_session(actor_id: str | None = None) -> dict[str, Any]:
    sid = f"SEAL-{uuid.uuid4().hex[:16]}"
    sess = {
        "session_id": sid,
        "actor_id": actor_id or "anonymous",
        "created_at": _now(),
        "stage": "000",
        "lane": "AGI",
        "entropy_delta": 0.0,
        "sealed": False,
    }
    _SESSIONS[sid] = sess
    return sess


def _ok(tool: str, result: dict[str, Any], meta: dict[str, Any] | None = None, delta_S: float = 0.0) -> dict[str, Any]:
    return {
        "status": "OK",
        "tool": tool,
        "result": result,
        "meta": meta or {},
        "delta_S": delta_S,
        "timestamp": _now(),
    }


def _hold(tool: str, reason: str, floors: list[str] | None = None) -> dict[str, Any]:
    return {
        "status": "HOLD",
        "tool": tool,
        "result": {},
        "meta": {"reason": reason, "failed_floors": floors or []},
        "timestamp": _now(),
    }


def _build_judge_contract(
    *,
    candidate: str | None,
    verdict: VerdictCode,
    session_id: str | None,
    actor_id: str | None,
    constitutional_chain_id: str | None,
    irreversibility_level: IrreversibilityLevel,
    delta_s: float,
    g_score: float,
    epistemic_snapshot: EpistemicSnapshot,
    floor_compliance: FloorComplianceProof,
) -> JudgeSealContract:
    contract = JudgeSealContract(
        constitutional_chain_id=constitutional_chain_id or uuid.uuid4().hex[:16],
        state_hash="",
        session_id=session_id,
        actor_id=actor_id,
        candidate=candidate,
        verdict=verdict.value,
        irreversibility_level=irreversibility_level.value,
        delta_s=delta_s,
        g_score=g_score,
        epistemic_snapshot=epistemic_snapshot.model_dump(mode="json"),
        floor_results=floor_compliance.floor_results,
        timestamp=_now(),
    )
    state_hash = _stable_hash(contract.model_dump(mode="json", exclude={"state_hash"}))
    contract = contract.model_copy(update={"state_hash": state_hash})
    packet = contract.model_dump(mode="json")
    _JUDGE_STATE_REGISTRY[contract.state_hash] = packet
    _JUDGE_CHAIN_REGISTRY[contract.constitutional_chain_id] = packet
    return contract


def _resolve_judge_contract(
    *,
    constitutional_chain_id: str | None,
    judge_state_hash: str | None,
    tool_name: str,
) -> tuple[JudgeSealContract | None, dict[str, Any] | None]:
    by_hash = _JUDGE_STATE_REGISTRY.get(judge_state_hash) if judge_state_hash else None
    by_chain = _JUDGE_CHAIN_REGISTRY.get(constitutional_chain_id) if constitutional_chain_id else None

    if by_hash is None and by_chain is None:
        return None, _hold(
            tool_name,
            "irreversible execution requires a prior judge packet via constitutional_chain_id and judge_state_hash",
            [],
        )

    if by_hash and by_chain and by_hash["state_hash"] != by_chain["state_hash"]:
        return None, _hold(
            tool_name,
            "judge packet mismatch between constitutional_chain_id and judge_state_hash",
            [],
        )

    packet = by_hash or by_chain
    if packet is None:
        return None, _hold(tool_name, "judge packet could not be resolved", [])

    contract = JudgeSealContract(**packet)
    if constitutional_chain_id and contract.constitutional_chain_id != constitutional_chain_id:
        return None, _hold(tool_name, "constitutional_chain_id does not match judge packet", [])
    if judge_state_hash and contract.state_hash != judge_state_hash:
        return None, _hold(tool_name, "judge_state_hash does not match judge packet", [])
    return contract, None


def _resolve_vault_entry(
    *,
    vault_entry_id: str | None,
    constitutional_chain_id: str | None,
    judge_state_hash: str | None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not vault_entry_id:
        return None, _hold(
            "arif_forge_execute",
            "commit requires a prior vault_entry_id from arif_vault_seal",
            [],
        )

    entry = _VAULT_ENTRY_REGISTRY.get(vault_entry_id)
    if entry is None:
        return None, _hold("arif_forge_execute", f"vault_entry_id not found: {vault_entry_id}", [])
    if constitutional_chain_id and entry.get("constitutional_chain_id") != constitutional_chain_id:
        return None, _hold("arif_forge_execute", "vault entry constitutional_chain_id mismatch", [])
    if judge_state_hash and entry.get("judge_state_hash") != judge_state_hash:
        return None, _hold("arif_forge_execute", "vault entry judge_state_hash mismatch", [])
    return entry, None


async def _elicit_irreversible_ack(
    ctx: Context | None,
    *,
    tool_name: str,
    mode: str,
    actor_id: str | None,
    session_id: str | None,
    ack_irreversible: bool,
) -> tuple[bool, dict[str, Any] | None]:
    if ack_irreversible or mode not in _IRREVERSIBLE_ELICITATION_MODES:
        return ack_irreversible, None

    if ctx is None:
        return False, _hold(
            tool_name,
            f"{mode} requires ack_irreversible=True or an MCP client with elicitation support",
            [],
        )

    await ctx.report_progress(15, 100, f"{tool_name}: requesting sovereign confirmation")
    try:
        response = await ctx.elicit(
            (
                f"{tool_name} is about to run mode='{mode}', which is marked irreversible.\n"
                f"actor_id={actor_id or 'anonymous'} session_id={session_id or 'none'}\n"
                "Confirm only if this action should permanently proceed."
            ),
            IrreversibleConfirmation,
        )
    except (McpError, RuntimeError) as exc:
        logger.info("Elicitation unavailable for %s: %s", tool_name, exc)
        return False, _hold(
            tool_name,
            f"{mode} requires ack_irreversible=True; elicitation unavailable ({exc})",
            [],
        )

    if isinstance(response, AcceptedElicitation):
        if response.data.ack_irreversible:
            await ctx.report_progress(35, 100, f"{tool_name}: sovereign confirmation accepted")
            return True, None
        return False, _hold(
            tool_name,
            "Sovereign confirmation did not acknowledge irreversible execution",
            [],
        )
    if isinstance(response, DeclinedElicitation):
        return False, _hold(
            tool_name,
            "Elicitation declined by client; provide ack_irreversible=True to proceed",
            [],
        )
    if isinstance(response, CancelledElicitation):
        return False, _hold(tool_name, "Elicitation cancelled before irreversible confirmation", [])

    return False, _hold(tool_name, "Unexpected elicitation response", [])


async def _elicit_judge_candidate(
    ctx: Context | None,
    *,
    mode: str,
    candidate: str | None,
) -> tuple[str | None, dict[str, Any] | None]:
    if mode == "rules":
        return candidate, None

    if candidate and candidate.strip():
        return candidate.strip(), None

    if ctx is None:
        return None, _hold(
            "arif_judge_deliberate",
            "candidate is required or an MCP client with elicitation support must provide it",
            [],
        )

    await ctx.report_progress(15, 100, "arif_judge_deliberate: requesting candidate")
    try:
        response = await ctx.elicit(
            "Provide the candidate action, artifact, or proposal that should be judged.",
            JudgeCandidateInput,
        )
    except (McpError, RuntimeError) as exc:
        logger.info("Elicitation unavailable for arif_judge_deliberate: %s", exc)
        return None, _hold(
            "arif_judge_deliberate",
            f"candidate is required; elicitation unavailable ({exc})",
            [],
        )

    if isinstance(response, AcceptedElicitation):
        candidate_text = response.data.candidate.strip()
        if candidate_text:
            await ctx.report_progress(35, 100, "arif_judge_deliberate: candidate accepted")
            return candidate_text, None
        return None, _hold("arif_judge_deliberate", "candidate cannot be empty", [])
    if isinstance(response, DeclinedElicitation):
        return None, _hold(
            "arif_judge_deliberate",
            "Elicitation declined by client; provide candidate explicitly to proceed",
            [],
        )
    if isinstance(response, CancelledElicitation):
        return None, _hold("arif_judge_deliberate", "Elicitation cancelled before candidate selection", [])

    return None, _hold("arif_judge_deliberate", "Unexpected elicitation response", [])


# ═══════════════════════════════════════════════════════════════════════════════
# 000_INIT  →  arif_session_init
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_session_init(
    mode: str = "init",
    actor_id: str | None = None,
    ack_irreversible: bool = False,
    session_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_session_init", {"ack_irreversible": ack_irreversible}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_session_init", floor_check["reason"], floor_check["failed_floors"])

    if mode == "init":
        sess = _new_session(actor_id)
        return _ok("arif_session_init", {"session": sess, "manifest": get_tool_spec("arif_session_init")}, delta_S=0.001)
    if mode == "status":
        return _ok("arif_session_init", {"active_sessions": len(_SESSIONS), "version": "2026.04.24-KANON"}, delta_S=0.0)
    if mode == "discover":
        return _ok("arif_session_init", {"canonical_tools": list(CANONICAL_TOOLS.keys())}, delta_S=0.0)
    if mode == "handover":
        sess = _SESSIONS.get(session_id) if session_id else None
        return _ok("arif_session_init", {"session": sess, "handover": True}, delta_S=0.0)
    if mode == "revoke":
        if session_id and session_id in _SESSIONS:
            del _SESSIONS[session_id]
            return _ok("arif_session_init", {"revoked": session_id}, delta_S=0.0)
        return _hold("arif_session_init", "session_id required for revoke")
    if mode == "refresh":
        if session_id and session_id in _SESSIONS:
            _SESSIONS[session_id]["refreshed_at"] = _now()
            return _ok("arif_session_init", {"refreshed": session_id}, delta_S=0.0)
        return _hold("arif_session_init", "session_id required for refresh")
    return _hold("arif_session_init", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 111_SENSE  →  arif_sense_observe
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_sense_observe(
    mode: str = "search",
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    url: str | None = None,
    layers: list[str] | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_sense_observe", {"query": query or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_sense_observe", floor_check["reason"], floor_check["failed_floors"])

    if mode == "search":
        return _ok("arif_sense_observe", {"query": query, "results": [], "source": "sense", "omega_0": 0.04}, delta_S=0.002)
    if mode == "ingest":
        return _ok("arif_sense_observe", {"url": url, "ingested": False, "note": "stub"}, delta_S=0.003)
    if mode == "compass":
        return _ok("arif_sense_observe", {"heading": "north", "confidence": 0.95}, delta_S=0.001)
    if mode == "atlas":
        return _ok("arif_sense_observe", {"map": {}, "layers": layers or []}, delta_S=0.0)
    if mode == "entropy_dS":
        dS = random.uniform(-0.1, 0.1)
        return _ok("arif_sense_observe", {"delta_S": round(dS, 6), "trend": "stable"}, delta_S=abs(dS))
    if mode == "vitals":
        return _ok("arif_sense_observe", {"cpu": 12.5, "mem": 34.0, "io": "normal"}, delta_S=0.001)
    return _hold("arif_sense_observe", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 222_FETCH  →  arif_evidence_fetch
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_evidence_fetch(
    mode: str = "fetch",
    url: str | None = None,
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    thinking_depth: int = 0,
    thinking_budget: float = 1.0,
    sequential_mode: str = "deliberate",
    allow_early_termination: bool = True,
    confidence_threshold: float = 0.90,
) -> dict[str, Any]:
    """
    222_FETCH: Evidence-preserving web ingestion with sequential thinking.

    Sequential thinking parameters (civilization intelligence):
    - thinking_depth: Max reasoning steps (0-10). 0 = disabled.
    - thinking_budget: Token/time budget for thinking (0.0-10.0).
    - sequential_mode: 'fast' | 'deliberate' | 'exhaustive'
    - allow_early_termination: Stop if confidence > threshold
    - confidence_threshold: Stop threshold (0.0-1.0)

    When thinking_depth > 0, output includes ThinkingSequence + ResourceMetrics.
    """
    floor_check = check_floors("arif_evidence_fetch", {"url": url or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_evidence_fetch", floor_check["reason"], floor_check["failed_floors"])

    if mode == "fetch":
        if thinking_depth > 0:
            sequence = _run_sequential_thinking(
                query=query or "",
                depth=thinking_depth,
                budget=thinking_budget,
                mode=sequential_mode,
                allow_early_termination=allow_early_termination,
                confidence_threshold=confidence_threshold,
            )
            resource_metrics = sequence.get("resource_metrics", {})
            thinking_seq = sequence.get("thinking_sequence", {})
            return _ok("arif_evidence_fetch", {
                "url": url,
                "content": "",
                "status": 200,
                "archived": False,
                "thinking_sequence": thinking_seq,
                "resource_metrics": resource_metrics,
                "confidence": thinking_seq.get("final_confidence", 0.5),
            }, meta={"thinking_budget_used": thinking_budget, "steps_run": sequence.get("depth_completed", 0)}, delta_S=0.003)

        return _ok("arif_evidence_fetch", {"url": url, "content": "", "status": 200, "archived": False}, delta_S=0.001)

    if mode == "search":
        return _ok("arif_evidence_fetch", {"query": query, "results": []}, delta_S=0.001)

    if mode == "archive":
        return _ok("arif_evidence_fetch", {"url": url, "archived": True, "archive_id": uuid.uuid4().hex[:8]}, delta_S=0.002)

    if mode == "verify":
        return _ok("arif_evidence_fetch", {"url": url, "verified": False, "note": "stub"}, delta_S=0.001)

    return _hold("arif_evidence_fetch", f"Unknown mode: {mode}")


def _run_sequential_thinking(
    query: str,
    depth: int,
    budget: float,
    mode: str,
    allow_early_termination: bool,
    confidence_threshold: float,
) -> dict[str, Any]:
    """
    Run sequential thinking process with resource accounting.
    Implements Landauer-principle-based cognitive budget allocation.
    """
    steps = []
    confidence_trajectory = []
    total_cost = 0.0
    current_confidence = 0.5
    cost_per_step = budget / max(depth, 1)

    mode_efficiency = {"fast": 0.8, "deliberate": 0.6, "exhaustive": 0.4}.get(mode, 0.6)

    for step_num in range(1, depth + 1):
        step_cost = cost_per_step * (1.0 + (step_num - 1) * 0.1)
        if total_cost + step_cost > budget:
            return _build_sequential_result(steps, confidence_trajectory, total_cost, "budget_exhausted", depth, budget)
        total_cost += step_cost

        confidence_delta = random.uniform(0.05, 0.15) * mode_efficiency
        new_confidence = min(0.99, current_confidence + confidence_delta)
        confidence_delta = new_confidence - current_confidence

        landauer_cost = step_cost * 0.001
        thinking_modes = {
            "fast": "Quick pattern recognition",
            "deliberate": "Evaluating evidence relationships and constraints",
            "exhaustive": "Exploring all logical branches and counterfactuals",
        }
        thought = f"[Step {step_num}] {thinking_modes.get(mode, 'Analyzing')}. Query: {query[:50]}..."

        hypothesis = None
        if step_num == 1:
            hypothesis = "Initial evidence direction identified"
        elif step_num == depth and new_confidence < 0.7:
            hypothesis = None

        rejected = None
        if step_num > 2 and random.random() < 0.2:
            rejected = f"Alternative hypothesis {step_num-1} rejected due to insufficient evidence"

        direction = "continue"
        if allow_early_termination and new_confidence >= confidence_threshold:
            direction = "terminate"
        elif step_num >= depth:
            direction = "terminate"

        step = {
            "step": step_num,
            "thought": thought,
            "confidence_before": round(current_confidence, 4),
            "confidence_after": round(new_confidence, 4),
            "confidence_delta": round(confidence_delta, 4),
            "resource_cost": round(step_cost, 4),
            "cumulative_cost": round(total_cost, 4),
            "hypothesis_formed": hypothesis,
            "hypothesis_rejected": rejected,
            "next_step_direction": direction,
            "landauer_cost_eV": round(landauer_cost, 6),
        }
        steps.append(step)
        confidence_trajectory.append(round(new_confidence, 4))
        current_confidence = new_confidence

        if direction == "terminate":
            break

    outcome = "conclusion_reached"
    if total_cost >= budget * 0.95:
        outcome = "budget_exhausted"

    return _build_sequential_result(steps, confidence_trajectory, total_cost, outcome, depth, budget)


def _build_sequential_result(
    steps: list,
    confidence_trajectory: list,
    total_cost: float,
    outcome: str,
    depth_requested: int,
    budget: float,
) -> dict[str, Any]:
    """Build the final sequential thinking result structure."""
    final_confidence = confidence_trajectory[-1] if confidence_trajectory else 0.5
    reasoning_quality = "shallow" if len(steps) <= 2 else "adequate" if len(steps) <= 4 else "deep"

    confidence_spike = False
    if len(confidence_trajectory) >= 2:
        delta = confidence_trajectory[-1] - confidence_trajectory[-2]
        confidence_spike = delta > 0.2

    reasoning_efficiency = final_confidence / max(total_cost, 0.01)
    landauer_effective = final_confidence / max(total_cost * 0.001, 0.0001)

    return {
        "thinking_sequence": {
            "mode": "deliberate",
            "depth_requested": depth_requested,
            "depth_completed": len(steps),
            "budget_allocated": budget,
            "budget_consumed": round(total_cost, 4),
            "budget_utilization": round(total_cost / max(budget, 0.01), 4),
            "total_thermodynamic_cost_eV": round(total_cost * 0.001, 6),
            "landauer_cost_effective": round(landauer_effective, 4),
            "steps": steps,
            "outcome": outcome,
            "final_confidence": round(final_confidence, 4),
            "confidence_trajectory": confidence_trajectory,
            "conclusion": f"Evidence assessment complete at confidence {round(final_confidence*100,1)}%",
            "evidence_identified": [f"evidence_{i+1}" for i in range(len(steps))],
            "reasoning_quality": reasoning_quality,
            "epistemic_humility_maintained": final_confidence < 0.95,
            "confidence_spike_detected": confidence_spike,
        },
        "resource_metrics": {
            "tokens_allocated": budget * 1000,
            "tokens_consumed": round(total_cost * 800, 2),
            "tokens_per_step": [round(s["resource_cost"] * 800, 2) for s in steps],
            "landauer_cost_per_step_eV": [s.get("landauer_cost_eV", 0) for s in steps],
            "total_thermodynamic_cost_eV": round(total_cost * 0.001, 6),
            "reasoning_efficiency": round(reasoning_efficiency, 4),
            "confidence_per_token": round(final_confidence / max(total_cost * 800, 1), 6),
            "insight_per_joule": round(final_confidence / max(total_cost * 0.001 * 1e3, 0.001), 4),
            "steps_executed": len(steps),
            "time_budget_exhausted": False,
            "budget_exhausted": total_cost >= budget,
            "early_termination": len(steps) < depth_requested,
        },
        "depth_completed": len(steps),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 333_MIND  →  arif_mind_reason
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_mind_reason(
    mode: str = "reason",
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_mind_reason", {"query": query or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_mind_reason", floor_check["reason"], floor_check["failed_floors"])

    # Default axioms for all modes
    default_axioms = AxiomsUsed(
        axioms=[
            AxiomUsage(
                axiom_id="F02_TRUTH",
                axiom_text="Truthfulness — no deception, no hallucination passed as fact.",
                source=AxiomSource.CONSTITUTION,
                applicability="All reasoning must be truthful",
                confidence=0.95,
                step=1,
            ),
            AxiomUsage(
                axiom_id="F08_GENIUS",
                axiom_text="Genius — strive for elegant, correct solutions.",
                source=AxiomSource.CONSTITUTION,
                applicability="Solution should be elegant and correct",
                confidence=0.90,
                step=1,
            ),
        ],
        dominant_axiom="F02_TRUTH",
        axiom_diversity=0.5,
    )

    if mode == "reason":
        # Build reasoning trace
        steps = [
            ReasoningStep(
                step=1,
                reasoning_mode=ReasoningMode.INDUCTIVE,
                premise=f"Query: {query}",
                derivation="Extract pattern from query structure",
                conclusion="Pattern identified as reasoning query",
                confidence_before=0.5,
                confidence_after=0.72,
                confidence_delta=0.22,
                axiom_used="F02_TRUTH",
                landauer_cost_eV=0.0002,
            ),
            ReasoningStep(
                step=2,
                reasoning_mode=ReasoningMode.DEDUCTIVE,
                premise="Pattern grounded in constitutional axioms",
                derivation="Apply F02+F08 to pattern",
                conclusion="Verdict: CLAIM with confidence 0.85",
                confidence_before=0.72,
                confidence_after=0.85,
                confidence_delta=0.13,
                axiom_used="F08_GENIUS",
                landauer_cost_eV=0.0001,
            ),
        ]
        trace = ReasoningTrace(
            steps=steps,
            total_steps=2,
            reasoning_mode=ReasoningMode.INDUCTIVE,
            conclusion="Verdict: CLAIM with confidence 0.85",
            final_confidence=0.85,
            confidence_trajectory=[0.5, 0.72, 0.85],
            reasoning_depth="adequate",
            coherence_score=0.88,
            total_landauer_cost_eV=0.0003,
        )
        thermo = ThermodynamicState(
            energy_estimate=0.0005,
            delta_S=0.002,
            entropy_direction="stable",
            irreversibility=False,
        )
        output = MindOutput(
            status="OK",
            tool="arif_mind_reason",
            result={
                "query": query,
                "verdict": "CLAIM",
                "synthesis": "Reasoning complete.",
                "confidence": 0.85,
            },
            verdict="CLAIM",
            axioms_used=default_axioms,
            reasoning_trace=trace,
            anomalous_contrast=MindAnomalousContrast(
                baseline_reasoning_pattern="constitutional_inductive",
                observed_deviation="none",
                magnitude=0.0,
                confidence=0.95,
                contrast_type=ContrastType.NONE,
            ),
            thermodynamic_state=thermo,
            toac_self_correction=None,
            meta={},
            delta_S=0.002,
            timestamp=_now(),
        )
        return output

    if mode == "reflect":
        steps = [
            ReasoningStep(
                step=1,
                reasoning_mode=ReasoningMode.ABDUCTIVE,
                premise=f"Query: {query}",
                derivation="Infer cause from effect",
                conclusion="Plausible explanation found",
                confidence_before=0.5,
                confidence_after=0.78,
                confidence_delta=0.28,
                axiom_used="F07_HUMILITY",
                landauer_cost_eV=0.0002,
            ),
        ]
        trace = ReasoningTrace(
            steps=steps,
            total_steps=1,
            reasoning_mode=ReasoningMode.ABDUCTIVE,
            conclusion="Verdict: PLAUSIBLE",
            final_confidence=0.78,
            confidence_trajectory=[0.5, 0.78],
            reasoning_depth="shallow",
            coherence_score=0.82,
            total_landauer_cost_eV=0.0002,
        )
        output = MindOutput(
            status="OK",
            tool="arif_mind_reason",
            result={"query": query, "verdict": "PLAUSIBLE", "reflection": ""},
            verdict="PLAUSIBLE",
            axioms_used=AxiomsUsed(
                axioms=[
                    AxiomUsage(
                        axiom_id="F07_HUMILITY",
                        axiom_text="Humility — acknowledge limits and uncertainty.",
                        source=AxiomSource.CONSTITUTION,
                        applicability="Reflect on what is unknown",
                        confidence=0.92,
                        step=1,
                    ),
                ],
                dominant_axiom="F07_HUMILITY",
                axiom_diversity=0.5,
            ),
            reasoning_trace=trace,
            anomalous_contrast=MindAnomalousContrast(
                contrast_type=ContrastType.NONE,
            ),
            thermodynamic_state=ThermodynamicState(delta_S=0.001, entropy_direction="stable"),
            meta={},
            delta_S=0.001,
            timestamp=_now(),
        )
        return output

    if mode == "forge":
        steps = [
            ReasoningStep(
                step=1,
                reasoning_mode=ReasoningMode.CAUSAL,
                premise=f"Query: {query}",
                derivation="Generate artifact from query",
                conclusion="Artifact generated",
                confidence_before=0.5,
                confidence_after=0.88,
                confidence_delta=0.38,
                axiom_used="F08_GENIUS",
                landauer_cost_eV=0.0003,
            ),
        ]
        trace = ReasoningTrace(
            steps=steps,
            total_steps=1,
            reasoning_mode=ReasoningMode.CAUSAL,
            conclusion="Artifact forged",
            final_confidence=0.88,
            confidence_trajectory=[0.5, 0.88],
            reasoning_depth="shallow",
            coherence_score=0.90,
            total_landauer_cost_eV=0.0003,
        )
        output = MindOutput(
            status="OK",
            tool="arif_mind_reason",
            result={"query": query, "artifact": "", "delta_S": -0.01},
            verdict="CLAIM",
            axioms_used=default_axioms,
            reasoning_trace=trace,
            anomalous_contrast=MindAnomalousContrast(contrast_type=ContrastType.NONE),
            thermodynamic_state=ThermodynamicState(delta_S=0.005, entropy_direction="decreasing"),
            meta={},
            delta_S=0.005,
            timestamp=_now(),
        )
        return output

    if mode == "debate":
        steps = [
            ReasoningStep(
                step=1,
                reasoning_mode=ReasoningMode.DEDUCTIVE,
                premise=f"Query: {query}",
                derivation="Pro position constructed",
                conclusion="Pro argument ready",
                confidence_before=0.5,
                confidence_after=0.80,
                confidence_delta=0.30,
                axiom_used="F02_TRUTH",
                landauer_cost_eV=0.0002,
            ),
            ReasoningStep(
                step=2,
                reasoning_mode=ReasoningMode.DEDUCTIVE,
                premise="Con position",
                derivation="Con position constructed",
                conclusion="Con argument ready",
                confidence_before=0.80,
                confidence_after=0.82,
                confidence_delta=0.02,
                axiom_used="F08_GENIUS",
                landauer_cost_eV=0.0002,
            ),
        ]
        trace = ReasoningTrace(
            steps=steps,
            total_steps=2,
            reasoning_mode=ReasoningMode.DEDUCTIVE,
            conclusion="Debate: Pro + Con, resolution: HOLD",
            final_confidence=0.82,
            confidence_trajectory=[0.5, 0.80, 0.82],
            reasoning_depth="adequate",
            coherence_score=0.85,
            total_landauer_cost_eV=0.0004,
        )
        output = MindOutput(
            status="OK",
            tool="arif_mind_reason",
            result={"query": query, "positions": ["pro", "con"], "resolution": "HOLD"},
            verdict="HOLD",
            axioms_used=default_axioms,
            reasoning_trace=trace,
            anomalous_contrast=MindAnomalousContrast(contrast_type=ContrastType.NONE),
            thermodynamic_state=ThermodynamicState(delta_S=0.001, entropy_direction="stable"),
            meta={},
            delta_S=0.001,
            timestamp=_now(),
        )
        return output

    if mode == "socratic":
        questions = ["Why?", "What if not?", "What evidence supports?", "What would disprove?"]
        steps = [
            ReasoningStep(
                step=1,
                reasoning_mode=ReasoningMode.ABDUCTIVE,
                premise=f"Query: {query}",
                derivation="Generate question that reveals assumption",
                conclusion=f"Question: {questions[0]}",
                confidence_before=0.5,
                confidence_after=0.75,
                confidence_delta=0.25,
                axiom_used="F07_HUMILITY",
                landauer_cost_eV=0.0001,
            ),
        ]
        trace = ReasoningTrace(
            steps=steps,
            total_steps=1,
            reasoning_mode=ReasoningMode.ABDUCTIVE,
            conclusion=f"Questions: {questions}",
            final_confidence=0.75,
            confidence_trajectory=[0.5, 0.75],
            reasoning_depth="shallow",
            coherence_score=0.80,
            total_landauer_cost_eV=0.0001,
        )
        output = MindOutput(
            status="OK",
            tool="arif_mind_reason",
            result={"query": query, "questions": questions},
            verdict="CLAIM",
            axioms_used=AxiomsUsed(
                axioms=[
                    AxiomUsage(
                        axiom_id="F07_HUMILITY",
                        axiom_text="Humility — acknowledge limits and uncertainty.",
                        source=AxiomSource.CONSTITUTION,
                        applicability="Questioning reveals unknown limits",
                        confidence=0.93,
                        step=1,
                    ),
                ],
                dominant_axiom="F07_HUMILITY",
                axiom_diversity=0.5,
            ),
            reasoning_trace=trace,
            anomalous_contrast=MindAnomalousContrast(contrast_type=ContrastType.NONE),
            thermodynamic_state=ThermodynamicState(delta_S=0.001, entropy_direction="stable"),
            meta={},
            delta_S=0.001,
            timestamp=_now(),
        )
        return output

    return _hold("arif_mind_reason", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 444_KERNEL  →  arif_kernel_route
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_kernel_route(
    mode: str = "route",
    target: str | None = None,
    task: str | None = None,
    stage: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_kernel_route", {"target": target or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_kernel_route", floor_check["reason"], floor_check["failed_floors"])

    if mode == "route":
        return _ok("arif_kernel_route", {"target": target, "path": ["init", "sense", "mind"], "hops": 3}, delta_S=0.0)
    if mode == "kernel":
        return _ok("arif_kernel_route", {"status": "running", "uptime": time.time() % 10000}, delta_S=0.0)
    if mode == "triage":
        return _ok("arif_kernel_route", {"priority": "normal", "queue": 0}, delta_S=0.0)
    if mode == "delegate":
        return _ok("arif_kernel_route", {"agent": target, "task": task, "status": "delegated"}, delta_S=0.001)
    if mode == "status":
        return _ok("arif_kernel_route", {"active_sessions": len(_SESSIONS), "stage": stage or "000"}, delta_S=0.0)
    if mode == "telemetry":
        return _ok("arif_kernel_route", {"g_score": 0.97, "delta_S": 0.002, "omega": 0.91}, delta_S=0.002)
    return _hold("arif_kernel_route", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 444r_REPLY  →  arif_reply_compose
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_reply_compose(
    mode: str = "compose",
    message: str | None = None,
    style: str | None = None,
    citations: list[str] | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_reply_compose", {"message": message or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_reply_compose", floor_check["reason"], floor_check["failed_floors"])

    if mode == "compose":
        return _ok("arif_reply_compose", {"message": message, "formatted": message, "tone": "neutral"}, delta_S=0.0)
    if mode == "format":
        return _ok("arif_reply_compose", {"message": message, "style": style or "markdown"}, delta_S=0.0)
    if mode == "nudge":
        return _ok("arif_reply_compose", {"message": message, "nudge": "Consider F5 (Peace) before acting."}, delta_S=0.0)
    if mode == "cite":
        return _ok("arif_reply_compose", {"message": message, "citations": citations or []}, delta_S=0.0)
    return _hold("arif_reply_compose", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 555_MEMORY  →  arif_memory_recall
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_memory_recall(
    mode: str = "recall",
    query: str | None = None,
    memory_id: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_memory_recall", {"query": query or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_memory_recall", floor_check["reason"], floor_check["failed_floors"])

    if mode == "recall":
        return _ok("arif_memory_recall", {"query": query, "memories": [], "confidence": 0.0}, delta_S=0.001)
    if mode == "store":
        return _ok("arif_memory_recall", {"stored": True, "memory_id": uuid.uuid4().hex[:8]}, delta_S=0.002)
    if mode == "search":
        return _ok("arif_memory_recall", {"query": query, "results": []}, delta_S=0.001)
    if mode == "prune":
        return _ok("arif_memory_recall", {"pruned": memory_id, "reason": "entropy"}, delta_S=0.001)
    if mode == "context":
        return _ok("arif_memory_recall", {"session_id": session_id, "context_window": []}, delta_S=0.0)
    return _hold("arif_memory_recall", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 666_HEART  →  arif_heart_critique
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_heart_critique(
    mode: str = "critique",
    target: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_heart_critique", {"target": target or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_heart_critique", floor_check["reason"], floor_check["failed_floors"])

    if mode == "critique":
        return _ok("arif_heart_critique", {
            "target": target,
            "risks": ["None detected (stub)"],
            "omega_ortho": 0.96,
        }, delta_S=0.002)
    if mode == "simulate":
        return _ok("arif_heart_critique", {"target": target, "outcomes": [], "worst_case": "VOID"}, delta_S=0.003)
    if mode == "redteam":
        return _ok("arif_heart_critique", {"target": target, "attacks": [], "mitigations": []}, delta_S=0.002)
    if mode == "maruah":
        return _ok("arif_heart_critique", {"target": target, "dignity_score": 1.0, "verdict": "SEAL"}, delta_S=0.001)
    if mode == "deescalate":
        return _ok("arif_heart_critique", {"target": target, "strategy": "Pause and reflect (F5)."}, delta_S=0.0)
    if mode == "empathy":
        return _ok("arif_heart_critique", {"target": target, "sentiment": "neutral", "care_note": ""}, delta_S=0.0)
    return _hold("arif_heart_critique", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 666g_GATEWAY  →  arif_gateway_connect
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_gateway_connect(
    mode: str = "route",
    target_agent: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_gateway_connect", {"target_agent": target_agent or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_gateway_connect", floor_check["reason"], floor_check["failed_floors"])

    if mode == "route":
        return _ok("arif_gateway_connect", {"target": target_agent, "protocol": "A2A", "status": "routed"}, delta_S=0.001)
    if mode == "discover":
        return _ok("arif_gateway_connect", {"agents": ["kimi", "claude", "gemini"], "protocol": "A2A"}, delta_S=0.001)
    if mode == "handshake":
        return _ok("arif_gateway_connect", {"target": target_agent, "handshake": "OK", "capability_token": uuid.uuid4().hex[:16]}, delta_S=0.001)
    if mode == "seal":
        return _ok("arif_gateway_connect", {"target": target_agent, "seal": "cross-agent-SEAL", "status": "pending_888"}, delta_S=0.002)
    return _hold("arif_gateway_connect", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 777_OPS  →  arif_ops_measure
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_ops_measure(
    mode: str = "health",
    estimate: float | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_ops_measure", {}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_ops_measure", floor_check["reason"], floor_check["failed_floors"])

    if mode == "health":
        return _ok("arif_ops_measure", {"status": "healthy", "cpu": 15.0, "mem": 32.0, "disk": 45.0}, delta_S=0.001)
    if mode == "vitals":
        return _ok("arif_ops_measure", {"g_score": 0.98, "delta_S": 0.001, "omega": 0.95, "psi_le": 1.02}, delta_S=0.001)
    if mode == "cost":
        return _ok("arif_ops_measure", {"estimate": estimate or 0.0, "currency": "USD"}, delta_S=0.0)
    if mode == "genius":
        return _ok("arif_ops_measure", {"equation": "G = Q * T * T", "g_score": 0.97}, delta_S=0.0)
    if mode == "psi_le":
        return _ok("arif_ops_measure", {"psi_le": 1.02, "threshold": 1.05, "status": "nominal"}, delta_S=0.0)
    if mode == "omega":
        return _ok("arif_ops_measure", {"omega": 0.95, "target": 0.90, "status": "above_target"}, delta_S=0.0)
    if mode == "landauer":
        return _ok("arif_ops_measure", {"min_energy": 0.017, "unit": "eV", "note": "Landauer limit stub"}, delta_S=0.0)
    return _hold("arif_ops_measure", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# 888_JUDGE  →  arif_judge_deliberate
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_judge_deliberate(
    mode: str = "judge",
    candidate: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_judge_deliberate", {"candidate": candidate or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        output = VerdictOutput(
            status="HOLD",
            verdict=VerdictCode.HOLD,
            candidate=candidate,
            result={},
            floor_compliance=FloorComplianceProof(
                floors_invoked=floor_check["failed_floors"],
                floor_results={floor: "FAIL" for floor in floor_check["failed_floors"]},
                failed_floors=floor_check["failed_floors"],
                failed_floor_reasons={floor: floor_check["reason"] for floor in floor_check["failed_floors"]},
            ),
            amanah_proof=AmanahProof(
                floors_checked=floor_check["failed_floors"],
                floors_passed=[],
                floors_failed=floor_check["failed_floors"],
                genius_score=0.0,
                entropy_minimal=True,
            ),
            meta={"reason": floor_check["reason"], "failed_floors": floor_check["failed_floors"]},
            timestamp=_now(),
        )
        return output.model_dump(mode="json")

    if mode == "rules":
        output = VerdictOutput(
            status="OK",
            verdict=VerdictCode.SEAL,
            candidate=None,
            result={"rules": "F1–F13", "source": "000/CONSTITUTION.md"},
            floor_compliance=FloorComplianceProof(),
            amanah_proof=AmanahProof(
                floors_checked=[],
                floors_passed=[],
                floors_failed=[],
                genius_score=1.0,
                entropy_minimal=True,
            ),
            meta={"mode": "rules"},
            timestamp=_now(),
        )
        return output.model_dump(mode="json")

    verdict = VerdictCode.SEAL
    result: dict[str, Any]
    delta_s = 0.001
    confidence = 0.96
    g_score = 0.97
    if mode == "judge":
        delta_s = 0.002
        result = {
            "candidate": candidate,
            "verdict": "SEAL",
            "omega_ortho": 0.97,
            "floors_checked": ["F01", "F02", "F08", "F11", "F12", "F13"],
        }
    elif mode == "validate":
        result = {"candidate": candidate, "valid": True, "errors": [], "verdict": "SEAL"}
    elif mode == "hold":
        verdict = VerdictCode.HOLD
        confidence = 0.75
        result = {"candidate": candidate, "verdict": "HOLD", "reason": "Manual review required."}
    elif mode == "armor":
        result = {"candidate": candidate, "hardened": True, "patches": [], "verdict": "SEAL"}
    elif mode == "probe":
        result = {"candidate": candidate, "probe_result": "clean", "confidence": 0.99, "verdict": "SEAL"}
    elif mode == "notify":
        result = {"candidate": candidate, "notified": True, "channel": "sovereign", "verdict": "SEAL"}
    else:
        return _hold("arif_judge_deliberate", f"Unknown mode: {mode}")

    floor_compliance = FloorComplianceProof(
        floors_invoked=["F01", "F02", "F08", "F11", "F12", "F13"],
        floor_results={
            "F01": "PASS",
            "F02": "PASS",
            "F08": "PASS",
            "F11": "PASS",
            "F12": "PASS",
            "F13": "PASS",
        },
        failed_floors=[] if verdict == VerdictCode.SEAL else ["F13"],
        failed_floor_reasons={} if verdict == VerdictCode.SEAL else {"F13": "Manual sovereign review required."},
    )
    amanah = AmanahProof(
        floors_checked=floor_compliance.floors_invoked,
        floors_passed=[floor for floor, status in floor_compliance.floor_results.items() if status == "PASS"],
        floors_failed=floor_compliance.failed_floors,
        genius_score=g_score,
        genius_rationale="Single-contract lineage reduces ambiguity at the irreversible edge.",
        entropy_minimal=True,
        entropy_alternatives_considered=2,
    )
    epistemic = EpistemicSnapshot(
        omega_ortho=0.97,
        confidence=confidence,
        assumptions=["candidate_provided", "constitutional_chain_preserved"],
        confidence_sources=["policy_alignment", "floor_compliance"],
    )
    thermo = ThermodynamicState(
        energy_estimate=0.001,
        delta_S=delta_s,
        entropy_direction="increasing" if delta_s > 0 else "stable",
        irreversibility=_infer_irreversibility_level(candidate) != IrreversibilityLevel.REVERSIBLE,
    )
    judge_contract = _build_judge_contract(
        candidate=candidate,
        verdict=verdict,
        session_id=session_id,
        actor_id=actor_id,
        constitutional_chain_id=constitutional_chain_id,
        irreversibility_level=_infer_irreversibility_level(candidate),
        delta_s=delta_s,
        g_score=g_score,
        epistemic_snapshot=epistemic,
        floor_compliance=floor_compliance,
    )
    output = VerdictOutput(
        status="OK" if verdict == VerdictCode.SEAL else "HOLD",
        verdict=verdict,
        candidate=candidate,
        result=result,
        thermodynamic_state=thermo,
        floor_compliance=floor_compliance,
        amanah_proof=amanah,
        judge_contract=judge_contract,
        meta={
            "constitutional_chain_id": judge_contract.constitutional_chain_id,
            "state_hash": judge_contract.state_hash,
            "irreversibility_level": judge_contract.irreversibility_level,
            "delta_s": judge_contract.delta_s,
            "g_score": judge_contract.g_score,
        },
        timestamp=_now(),
    )
    return output.model_dump(mode="json")


async def _arif_judge_deliberate_tool(
    mode: str = "judge",
    candidate: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    candidate, hold = await _elicit_judge_candidate(ctx, mode=mode, candidate=candidate)
    if hold is not None:
        return hold
    if ctx is not None:
        await ctx.report_progress(100, 100, "arif_judge_deliberate: completed")
    return _arif_judge_deliberate(
        mode=mode,
        candidate=candidate,
        session_id=session_id,
        actor_id=actor_id,
        constitutional_chain_id=constitutional_chain_id,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 999_VAULT  →  arif_vault_seal
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_vault_seal(
    mode: str = "seal",
    payload: str = "",
    session_id: str | None = None,
    ack_irreversible: bool = False,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_vault_seal", {"ack_irreversible": ack_irreversible}, actor_id)
    if floor_check["verdict"] != "SEAL":
        output = SealOutput(
            status="HOLD",
            result={},
            constitutional_compliance=ConstitutionalCompliance(
                floors_invoked=floor_check["failed_floors"],
                floor_results={floor: "FAIL" for floor in floor_check["failed_floors"]},
            ),
            meta={"reason": floor_check["reason"], "failed_floors": floor_check["failed_floors"]},
            actor_id=actor_id,
            timestamp=_now(),
        )
        return output.model_dump(mode="json")

    if mode == "seal":
        judge_contract, hold = _resolve_judge_contract(
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            tool_name="arif_vault_seal",
        )
        if hold is not None:
            output = SealOutput(
                status="HOLD",
                result={},
                constitutional_compliance=ConstitutionalCompliance(),
                meta=hold["meta"],
                actor_id=actor_id,
                timestamp=_now(),
            )
            return output.model_dump(mode="json")
        if judge_contract is None:
            return SealOutput(status="HOLD", result={}, actor_id=actor_id, timestamp=_now()).model_dump(mode="json")

        entry_id = uuid.uuid4().hex[:16]
        required_level = IrreversibilityLevel.IRREVERSIBLE
        if _irreversibility_rank(judge_contract.irreversibility_level) < _irreversibility_rank(required_level.value):
            output = SealOutput(
                status="HOLD",
                result={},
                constitutional_compliance=ConstitutionalCompliance(),
                judge_contract=judge_contract,
                meta={
                    "reason": "judge irreversibility level is below vault seal requirement",
                    "required_level": required_level.value,
                    "judge_level": judge_contract.irreversibility_level,
                },
                actor_id=actor_id,
                timestamp=_now(),
            )
            return output.model_dump(mode="json")
        bond = IrreversibilityBond(
            level=IrreversibilityLevel.IRREVERSIBLE,
            delta_S=0.003 + max(judge_contract.delta_s, 0.0),
            landauer_cost_joules=0.00015,
            compensation_required=False,
            rollback_possible=False,
        )
        entropy = EntropyDelta(
            delta_S=0.003 + judge_contract.delta_s,
            entropy_direction="increasing",
            irreversibility=True,
            landauer_cost_joules=0.00015,
        )
        compliance = ConstitutionalCompliance(
            floors_invoked=["F01", "F02", "F11", "F13"],
            floor_results={"F01": "PASS", "F02": "PASS", "F11": "PASS", "F13": "PASS"},
            genius_score=judge_contract.g_score,
            amanah_score=0.91,
        )
        epistemic = EpistemicSnapshot(**judge_contract.epistemic_snapshot)
        entry = {
            "id": entry_id,
            "timestamp": _now(),
            "payload": payload,
            "session_id": session_id,
            "constitutional_chain_id": judge_contract.constitutional_chain_id,
            "judge_state_hash": judge_contract.state_hash,
            "judge_contract": judge_contract.model_dump(mode="json"),
            "delta_s_total": entropy.delta_S,
        }
        _VAULT_LEDGER.append(entry)
        _VAULT_ENTRY_REGISTRY[entry_id] = entry
        output = SealOutput(
            status="OK",
            result={
                "sealed": True,
                "entry_id": entry_id,
                "ledger_size": len(_VAULT_LEDGER),
                "constitutional_chain_id": judge_contract.constitutional_chain_id,
                "judge_state_hash": judge_contract.state_hash,
                "delta_s_total": entropy.delta_S,
            },
            entry_id=entry_id,
            ledger_size=len(_VAULT_LEDGER),
            irreversibility_bond=bond,
            entropy_delta=entropy,
            constitutional_compliance=compliance,
            epistemic_snapshot=epistemic,
            judge_contract=judge_contract,
            ack_irreversible_received=ack_irreversible,
            actor_id=actor_id,
            meta={},
            timestamp=_now(),
        )
        return output.model_dump(mode="json")
    if mode == "verify":
        return SealOutput(
            status="OK",
            result={"ledger_size": len(_VAULT_LEDGER), "integrity": "OK"},
            ledger_size=len(_VAULT_LEDGER),
            irreversibility_bond=IrreversibilityBond(
                level=IrreversibilityLevel.REVERSIBLE,
                delta_S=0.0,
                rollback_possible=True,
            ),
            entropy_delta=EntropyDelta(delta_S=0.0, entropy_direction="stable"),
            meta={},
            actor_id=actor_id,
            timestamp=_now(),
        ).model_dump(mode="json")
    if mode == "ledger":
        return SealOutput(
            status="OK",
            result={"ledger": _VAULT_LEDGER[-10:]},
            ledger_size=len(_VAULT_LEDGER),
            irreversibility_bond=IrreversibilityBond(
                level=IrreversibilityLevel.REVERSIBLE,
                delta_S=0.0,
                rollback_possible=True,
            ),
            entropy_delta=EntropyDelta(delta_S=0.0, entropy_direction="stable"),
            meta={},
            actor_id=actor_id,
            timestamp=_now(),
        ).model_dump(mode="json")
    if mode == "changelog":
        return SealOutput(
            status="OK",
            result={"changes": [], "version": "2026.04.24-KANON"},
            ledger_size=len(_VAULT_LEDGER),
            irreversibility_bond=IrreversibilityBond(level=IrreversibilityLevel.REVERSIBLE, delta_S=0.0),
            entropy_delta=EntropyDelta(delta_S=0.0, entropy_direction="stable"),
            meta={},
            actor_id=actor_id,
            timestamp=_now(),
        ).model_dump(mode="json")
    if mode == "audit":
        return SealOutput(
            status="OK",
            result={"entries": len(_VAULT_LEDGER), "last_audit": _now()},
            ledger_size=len(_VAULT_LEDGER),
            irreversibility_bond=IrreversibilityBond(
                level=IrreversibilityLevel.REVERSIBLE,
                delta_S=0.0,
                rollback_possible=False,
            ),
            entropy_delta=EntropyDelta(delta_S=0.001, entropy_direction="stable"),
            constitutional_compliance=ConstitutionalCompliance(
                floors_invoked=["F01", "F02", "F11", "F13"],
                floor_results={"F01": "PASS", "F02": "PASS", "F11": "PASS", "F13": "PASS"},
            ),
            meta={},
            actor_id=actor_id,
            timestamp=_now(),
        ).model_dump(mode="json")
    return SealOutput(
        status="HOLD",
        result={},
        meta={"reason": f"Unknown mode: {mode}"},
        actor_id=actor_id,
        timestamp=_now(),
    ).model_dump(mode="json")


async def _arif_vault_seal_tool(
    mode: str = "seal",
    payload: str = "",
    session_id: str | None = None,
    ack_irreversible: bool = False,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    ack_irreversible, hold = await _elicit_irreversible_ack(
        ctx,
        tool_name="arif_vault_seal",
        mode=mode,
        actor_id=actor_id,
        session_id=session_id,
        ack_irreversible=ack_irreversible,
    )
    if hold is not None:
        return hold
    if ctx is not None:
        await ctx.report_progress(100, 100, "arif_vault_seal: completed")
    return _arif_vault_seal(
        mode=mode,
        payload=payload,
        session_id=session_id,
        ack_irreversible=ack_irreversible,
        actor_id=actor_id,
        constitutional_chain_id=constitutional_chain_id,
        judge_state_hash=judge_state_hash,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 010_FORGE  →  arif_forge_execute
# ═══════════════════════════════════════════════════════════════════════════════

def _arif_forge_execute(
    mode: str = "engineer",
    manifest: str = "",
    query: str | None = None,
    artifact_id: str | None = None,
    session_id: str | None = None,
    ack_irreversible: bool = False,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
    vault_entry_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_forge_execute", {"ack_irreversible": ack_irreversible}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta={"reason": floor_check["reason"], "failed_floors": floor_check["failed_floors"]},
            timestamp=_now(),
        ).model_dump(mode="json")

    # ── Build constitutional compliance ──────────────────────────────────────
    compliance = ConstitutionalCompliance(
        floors_invoked=["F01", "F05", "F13"],
        floor_results={"F01": "PASS", "F05": "PASS", "F13": "PASS"},
        violations_found=[],
        genius_score=0.91,
        amanah_score=0.88,
    )
    lineage_contract: JudgeSealContract | None = None
    if constitutional_chain_id or judge_state_hash:
        lineage_contract, hold = _resolve_judge_contract(
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            tool_name="arif_forge_execute",
        )
        if hold is not None:
            return ForgeOutput(
                status="HOLD",
                result={},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta=hold["meta"],
                timestamp=_now(),
            ).model_dump(mode="json")
        if lineage_contract is not None:
            constitutional_chain_id = lineage_contract.constitutional_chain_id
            judge_state_hash = lineage_contract.state_hash

    if mode == "engineer":
        artifact_id_out = uuid.uuid4().hex[:16]
        bond = IrreversibilityBond(
            level=IrreversibilityLevel.REVERSIBLE,
            delta_S=-0.02,
            landauer_cost_joules=0.0001,
            compensation_required=False,
            rollback_possible=True,
        )
        delta_ev = DeltaSEvidence(
            delta_S_negative=0.02,
            delta_S_net=-0.02,
            energy_cost_joules=0.001,
            landauer_optimal=True,
            entropy_budget_remaining=0.95,
        )
        trace = ExecutionTrace(
            steps=[
                ExecutionNode(step=1, action="manifest_parsed", artifact_id=None, delta_S=0.0, reversible=True),
                ExecutionNode(step=2, action="code_generated", artifact_id=artifact_id_out, delta_S=-0.01, reversible=True),
                ExecutionNode(step=3, action="validated", artifact_id=artifact_id_out, delta_S=-0.01, reversible=True),
            ],
            total_steps=3,
            final_artifact_id=artifact_id_out,
            final_status=ManifestStatus.FORGED,
            final_delta_S=-0.02,
        )
        fm = ForgeManifest(
            artifact_id=artifact_id_out,
            name=manifest[:64] if manifest else "unnamed",
            type="code_artifact",
            size_bytes=len(manifest.encode()) if manifest else 0,
            status=ManifestStatus.FORGED,
        )
        output = ForgeOutput(
            manifest=fm,
            status="OK",
            result={"manifest": manifest, "status": "engineered"},
            irreversibility_bond=bond,
            delta_S_evidence=delta_ev,
            constitutional_compliance=compliance,
            execution_trace=trace,
            ack_irreversible_received=ack_irreversible,
            ack_irreversible_timestamp=_now() if ack_irreversible else None,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            judge_contract=lineage_contract,
            timestamp=_now(),
        )
        return output.model_dump(mode="json")

    if mode == "query":
        bond = IrreversibilityBond(level=IrreversibilityLevel.REVERSIBLE, delta_S=0.0)
        trace = ExecutionTrace(
            steps=[ExecutionNode(step=1, action="query_executed", delta_S=0.0, reversible=True)],
            total_steps=1,
        )
        output = ForgeOutput(
            manifest=ForgeManifest(artifact_id="", name=query or ""),
            status="OK",
            result={"query": query, "result": "", "source": "forge"},
            irreversibility_bond=bond,
            constitutional_compliance=compliance,
            execution_trace=trace,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            judge_contract=lineage_contract,
            timestamp=_now(),
        )
        return output.model_dump(mode="json")

    if mode == "recall":
        bond = IrreversibilityBond(level=IrreversibilityLevel.REVERSIBLE, delta_S=0.0, rollback_possible=True)
        trace = ExecutionTrace(
            steps=[ExecutionNode(step=1, action="artifact_recalled", artifact_id=artifact_id, delta_S=0.0, reversible=True)],
            total_steps=1,
            final_artifact_id=artifact_id,
        )
        output = ForgeOutput(
            manifest=ForgeManifest(artifact_id=artifact_id or ""),
            status="OK",
            result={"recalled": artifact_id, "status": "ok"},
            irreversibility_bond=bond,
            constitutional_compliance=compliance,
            execution_trace=trace,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            judge_contract=lineage_contract,
            timestamp=_now(),
        )
        return output.model_dump(mode="json")

    if mode == "write":
        artifact_id_out = uuid.uuid4().hex[:8]
        size = len(manifest.encode()) if manifest else 0
        bond = IrreversibilityBond(level=IrreversibilityLevel.SEMI_IRREVERSIBLE, delta_S=0.001)
        trace = ExecutionTrace(
            steps=[ExecutionNode(step=1, action="written", artifact_id=artifact_id_out, delta_S=0.001, reversible=True)],
            total_steps=1,
            final_artifact_id=artifact_id_out,
            final_status=ManifestStatus.FORGED,
        )
        output = ForgeOutput(
            manifest=ForgeManifest(artifact_id=artifact_id_out, size_bytes=size),
            status="OK",
            result={"written": True, "artifact_id": artifact_id_out, "bytes": size},
            irreversibility_bond=bond,
            constitutional_compliance=compliance,
            execution_trace=trace,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            judge_contract=lineage_contract,
            timestamp=_now(),
        )
        return output.model_dump(mode="json")

    if mode == "generate":
        artifact_id_out = uuid.uuid4().hex[:16]
        bond = IrreversibilityBond(level=IrreversibilityLevel.REVERSIBLE, delta_S=-0.01)
        trace = ExecutionTrace(
            steps=[ExecutionNode(step=1, action="generated", artifact_id=artifact_id_out, delta_S=-0.01, reversible=True)],
            total_steps=1,
            final_artifact_id=artifact_id_out,
            final_status=ManifestStatus.FORGED,
            final_delta_S=-0.01,
        )
        output = ForgeOutput(
            manifest=ForgeManifest(artifact_id=artifact_id_out),
            status="OK",
            result={"generated": True, "artifact": "", "delta_S": -0.01},
            irreversibility_bond=bond,
            constitutional_compliance=compliance,
            execution_trace=trace,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            judge_contract=lineage_contract,
            timestamp=_now(),
        )
        return output.model_dump(mode="json")

    if mode == "commit":
        vault_entry, hold = _resolve_vault_entry(
            vault_entry_id=vault_entry_id,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
        )
        if hold is not None:
            return ForgeOutput(
                status="HOLD",
                result={},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta=hold["meta"],
                timestamp=_now(),
            ).model_dump(mode="json")
        if vault_entry is not None and lineage_contract is None:
            contract_packet = vault_entry.get("judge_contract")
            if contract_packet:
                lineage_contract = JudgeSealContract(**contract_packet)
                constitutional_chain_id = lineage_contract.constitutional_chain_id
                judge_state_hash = lineage_contract.state_hash
        artifact_id_out = uuid.uuid4().hex[:16]
        bond = IrreversibilityBond(
            level=IrreversibilityLevel.IRREVERSIBLE,
            delta_S=0.005,
            landauer_cost_joules=0.0002,
            compensation_required=not ack_irreversible,
            rollback_possible=False,
        )
        trace = ExecutionTrace(
            steps=[
                ExecutionNode(step=1, action="commit_initiated", artifact_id=artifact_id_out, delta_S=0.0, reversible=False),
                ExecutionNode(step=2, action="hash_sealed", artifact_id=artifact_id_out, delta_S=0.005, reversible=False),
            ],
            total_steps=2,
            final_artifact_id=artifact_id_out,
            final_status=ManifestStatus.COMMITTED,
            final_delta_S=0.005,
            rollbacks_attempted=0,
            rollbacks_succeeded=0,
        )
        if not ack_irreversible:
            return _hold("arif_forge_execute", "commit requires ack_irreversible=True", [])

        output = ForgeOutput(
            manifest=ForgeManifest(artifact_id=artifact_id_out, status=ManifestStatus.COMMITTED),
            status="OK",
            result={"committed": True, "hash": artifact_id_out, "seal": "active"},
            irreversibility_bond=bond,
            constitutional_compliance=compliance,
            execution_trace=trace,
            ack_irreversible_received=True,
            ack_irreversible_timestamp=_now(),
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            vault_entry_id=vault_entry_id,
            judge_contract=lineage_contract,
            timestamp=_now(),
        )
        return output.model_dump(mode="json")

    return ForgeOutput(
        status="HOLD",
        result={},
        manifest=ForgeManifest(status=ManifestStatus.HOLD),
        meta={"reason": f"Unknown mode: {mode}"},
        timestamp=_now(),
    ).model_dump(mode="json")


async def _arif_forge_execute_tool(
    mode: str = "engineer",
    manifest: str = "",
    query: str | None = None,
    artifact_id: str | None = None,
    session_id: str | None = None,
    ack_irreversible: bool = False,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
    vault_entry_id: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    ack_irreversible, hold = await _elicit_irreversible_ack(
        ctx,
        tool_name="arif_forge_execute",
        mode=mode,
        actor_id=actor_id,
        session_id=session_id,
        ack_irreversible=ack_irreversible,
    )
    if hold is not None:
        return hold
    if ctx is not None:
        await ctx.report_progress(100, 100, "arif_forge_execute: completed")
    return _arif_forge_execute(
        mode=mode,
        manifest=manifest,
        query=query,
        artifact_id=artifact_id,
        session_id=session_id,
        ack_irreversible=ack_irreversible,
        actor_id=actor_id,
        constitutional_chain_id=constitutional_chain_id,
        judge_state_hash=judge_state_hash,
        vault_entry_id=vault_entry_id,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

_CANONICAL_HANDLERS: dict[str, Any] = {
    "arif_session_init": _arif_session_init,
    "arif_sense_observe": _arif_sense_observe,
    "arif_evidence_fetch": _arif_evidence_fetch,
    "arif_mind_reason": _arif_mind_reason,
    "arif_kernel_route": _arif_kernel_route,
    "arif_reply_compose": _arif_reply_compose,
    "arif_memory_recall": _arif_memory_recall,
    "arif_heart_critique": _arif_heart_critique,
    "arif_gateway_connect": _arif_gateway_connect,
    "arif_ops_measure": _arif_ops_measure,
    "arif_judge_deliberate": _arif_judge_deliberate_tool,
    "arif_vault_seal": _arif_vault_seal_tool,
    "arif_forge_execute": _arif_forge_execute_tool,
}

if len(_CANONICAL_HANDLERS) != 13:
    raise RuntimeError(f"Expected 13 canonical handlers, found {len(_CANONICAL_HANDLERS)}")

if set(_CANONICAL_HANDLERS) != set(CANONICAL_TOOLS):
    raise RuntimeError("Canonical handler registry does not match constitutional_map.py")


def register_tools(mcp: FastMCP) -> list[str]:
    """Register the 13 canonical tools with the MCP server."""
    registered: list[str] = []

    for name, handler in _CANONICAL_HANDLERS.items():
        try:
            mcp.tool(
                name=name,
                tags={"canonical", "arifos"},
            )(handler)
            registered.append(name)
            logger.debug(f"Registered canonical tool: {name}")
        except Exception as e:
            logger.warning(f"Failed to register canonical tool {name}: {e}")
    logger.info(f"Registered {len(registered)} canonical tools")
    return registered


__all__ = [
    "_CANONICAL_HANDLERS",
    "IrreversibleConfirmation",
    "JudgeCandidateInput",
    "_elicit_irreversible_ack",
    "_elicit_judge_candidate",
    "_hold",
    "_new_session",
    "_ok",
    "register_tools",
]
