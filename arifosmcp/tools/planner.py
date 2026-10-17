"""arifOS Path Engine — PlanGraph + 3-path superposition (kernel single source).

SPEC of record: F13 chat 2026-10-14 (kernel-single-source architecture).

    Verb count UNCHANGED (8). Future modes compose this substrate:
    arif_think dag/branches/clarify, arif_judge score/collapse.
    This module is the deterministic engine those modes will call.
    Status: PRODUCED — not yet wired into arif_think dispatch.

Contract (F13 spec, 2026-10-14):

    Inputs : carry-forward open loops + CHRON predictions due + FQ pulse.
    Output : compact PlanGraph ≤ 2 KB with EXACTLY 3 candidate paths, each
             carrying steps, reversibility, blast_radius,
             expected_uncertainty_reduction (heuristic — labeled INT),
             and a falsifier ("what evidence would kill this path").
    Powers : collapse stays arif_judge, execution stays arif_forge.
             Every path is ADVISORY_ONLY and UNSEALABLE under
             OBSERVE_ONLY — thinking is not acting.
    Purity : file reads + one localhost GET (:7073/health). No mutation,
             no side-effecting tools, no LLM calls (deterministic).

Anti-hantu: quantum vocabulary is METAPHOR on the uncertainty substrate
(arifos://reality/state). Three paths = superposition; judge = collapse.
No literal quantum claims. DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

# ── Spec types ─────────────────────────────────────────────────────────

Reversibility = Literal["read_only", "reversible", "ext_reversible", "irreversible"]
BlastRadius = Literal["self", "session", "organ", "federation", "external"]
Provenance = Literal["live", "cached", "mock"]
NodeStatus = Literal["pending", "frontier", "running", "done", "failed", "frozen"]
VerdictToken = Literal["SEAL", "SABAR", "HOLD", "VOID"]  # canonical lattice D6


class PlanNode(BaseModel):
    id: str
    goal: str
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    deps: list[str] = Field(default_factory=list)
    tool: str | None = None
    reversibility: Reversibility = "read_only"
    blast_radius: BlastRadius = "self"
    est_cost: float = 0.0
    p_success: float | None = None
    status: NodeStatus = "pending"
    evidence_refs: list[str] = Field(default_factory=list)
    provenance: Provenance = "live"


class PlanVerdict(BaseModel):
    verdict: VerdictToken
    reason_code: str = ""
    floor_ids: list[str] = Field(default_factory=list)


class PathCandidate(BaseModel):
    id: str
    name: str
    node_ids: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    reversibility: Reversibility = "read_only"
    blast_radius: BlastRadius = "self"
    expected_uncertainty_reduction: float = 0.0  # heuristic — INT label
    uncertainty_note: str = ""
    falsifier: str = ""
    evidence_refs: list[str] = Field(default_factory=list)


class PlanGraph(BaseModel):
    id: str
    root_intent: str  # verbatim — fixes intent-propagation defect class
    nodes: list[PlanNode] = Field(default_factory=list)
    candidates: list[PathCandidate] = Field(default_factory=list)
    history: list[str] = Field(default_factory=list)  # graph diffs, ATG-style repair basis
    verdict: PlanVerdict | None = None  # only arif_judge collapse may set
    created_at: str = ""
    advisory: str = ""
    unsealable: bool = True  # advisory output can never feed arif_seal directly

    def compact(self) -> dict[str, Any]:
        """Compact dict for ≤2 KB wire form. Verdict withheld unless collapsed."""
        return {
            "id": self.id,
            "root_intent": self.root_intent[:120],
            "paths": [
                {
                    "id": c.id,
                    "name": c.name,
                    "steps": [s[:80] for s in c.steps[:5]],
                    "reversibility": c.reversibility,
                    "blast_radius": c.blast_radius,
                    "expected_uncertainty_reduction": round(c.expected_uncertainty_reduction, 2),
                    "uncertainty_note": c.uncertainty_note[:90],
                    "falsifier": c.falsifier[:90],
                }
                for c in self.candidates
            ],
            "verdict": self.verdict.model_dump() if self.verdict else None,
            "advisory": self.advisory[:160],
            "unsealable": self.unsealable,
        }


# ── Data gatherers (injectable paths for tests; pure reads) ───────────

CARRY_FORWARD_PATH = "/root/.local/share/arifos/carry_forward.json"
CHRON_PREDICTIONS_PATH = "/root/chron/data/predictions.jsonl"
FQ_HEALTH_URL = "http://127.0.0.1:7073/health"
OUTPUT_BUDGET_BYTES = 2048  # F13 spec: output maximum 2 KB


def load_open_loops(path: str = CARRY_FORWARD_PATH) -> list[dict[str, str]]:
    """Typed open loops from carry-forward (schema arifos.carry_forward.v3)."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    loops: list[dict[str, str]] = []
    for e in data.get("entries", []) or []:
        kind = e.get("kind") or ""
        if kind in ("open_loop", "888_HOLD_resume"):
            loops.append(
                {
                    "id": str(e.get("id", "")),
                    "content": str(e.get("content", ""))[:200],
                    "kind": kind,
                }
            )
    return loops


def load_due_predictions(
    path: str = CHRON_PREDICTIONS_PATH, *, horizon_days: int = 7, limit: int = 3
) -> list[dict[str, str]]:
    """CHRON predictions whose verify_at arrives within horizon, soonest first."""
    try:
        with open(path, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
    except (OSError, json.JSONDecodeError):
        return []
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=horizon_days)
    due: list[tuple[datetime, dict[str, str]]] = []
    for r in rows:
        if r.get("status") not in (None, "ACTIVE"):
            continue  # birth records always read ACTIVE; verdicts live elsewhere
        raw = str(r.get("verify_at", ""))
        try:
            at = datetime.fromisoformat(raw)
        except ValueError:
            continue
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
        if now <= at <= cutoff:
            due.append(
                (
                    at,
                    {
                        "prediction_id": str(r.get("prediction_id", "")),
                        "claim": str(r.get("claim", ""))[:120],
                        "verify_at": raw,
                        "confidence": str(r.get("confidence", "")),
                    },
                )
            )
    due.sort(key=lambda t: t[0])
    return [item for _, item in due[:limit]]


def load_fq(url: str = FQ_HEALTH_URL, *, timeout_s: float = 2.0) -> float | None:
    """Live FQ quotient from arifFlow :7073 (live SOT, never a cache file)."""
    try:
        with urllib.request.urlopen(url, timeout=timeout_s) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return float(payload.get("fq", {}).get("quotient"))
    except Exception:
        return None


# ── Path engine (deterministic; exactly 3 paths) ────────────────────────

_ADVISORY = (
    "ADVISORY_ONLY — unsealable under OBSERVE_ONLY. Collapse requires "
    "arif_judge; execution requires arif_forge."
)


def generate_paths(
    intent: str,
    *,
    cf_path: str = CARRY_FORWARD_PATH,
    chron_path: str = CHRON_PREDICTIONS_PATH,
    fq_url: str = FQ_HEALTH_URL,
    now: float | None = None,
) -> PlanGraph:
    """Build a first-batch PlanGraph with 3 candidate paths.

    Path 1 RESOLVE   — close the newest open loop (highest known-unknown).
    Path 2 VERIFY    — observe CHRON predictions due (calibration fuel).
    Path 3 CLARIFY   — ask the sovereign one binary question (SABAR path).

    All uncertainty figures are deterministic heuristics labeled INT;
    they are ranking signals, not measurements.
    """
    _now = now if now is not None else time.time()
    loops = load_open_loops(cf_path)
    due = load_due_predictions(chron_path)
    fq = load_fq(fq_url)

    contested = [l for l in loops if "CONTESTED" in l["content"].upper()]
    newest_loop = loops[-1] if loops else None

    nodes: list[PlanNode] = [
        PlanNode(
            id="n_cf_snapshot",
            goal="read carry-forward open loops",
            reversibility="read_only",
            provenance="live" if loops else "cached",
        ),
        PlanNode(
            id="n_chron_due",
            goal=f"read CHRON predictions due ≤7d (n={len(due)})",
            reversibility="read_only",
            provenance="live" if due else "cached",
        ),
        PlanNode(
            id="n_fq_pulse",
            goal=f"FQ pulse = {fq if fq is not None else 'UNREACHABLE'}",
            reversibility="read_only",
            provenance="live" if fq is not None else "cached",
        ),
    ]

    candidates: list[PathCandidate] = []

    # Path 1 — RESOLVE top open loop
    if newest_loop:
        eur1 = min(0.3 + 0.05 * len(loops), 0.6)
        candidates.append(
            PathCandidate(
                id="path_resolve",
                name="resolve-open-loop",
                node_ids=["n_cf_snapshot"],
                steps=[
                    f"scope loop {newest_loop['id']}: {newest_loop['content'][:80]}",
                    "propose reversible-first closure step",
                    "verify closure against reality probe",
                ],
                reversibility="reversible",
                blast_radius="organ",
                expected_uncertainty_reduction=eur1,
                uncertainty_note="INT heuristic: known-unknown removal, scales with open-loop count",
                falsifier="loop turns out superseded/duplicate (closure adds nothing) → path dead",
                evidence_refs=[newest_loop["id"]],
            )
        )
    else:
        candidates.append(
            PathCandidate(
                id="path_resolve",
                name="resolve-open-loop",
                node_ids=["n_cf_snapshot"],
                steps=["no open loops found — confirm carry-forward is live, not silent-empty"],
                reversibility="read_only",
                blast_radius="self",
                expected_uncertainty_reduction=0.0,
                uncertainty_note="data_gap: carry-forward empty or unreadable",
                falsifier="carry-forward serves live open loops next read → path becomes resolvable",
            )
        )

    # Path 2 — VERIFY due predictions
    eur2 = min(0.15 * len(due), 0.6)
    candidates.append(
        PathCandidate(
            id="path_verify",
            name="verify-due-predictions",
            node_ids=["n_chron_due"],
            steps=(
                [f"observe outcome: {d['claim'][:70]}" for d in due]
                if due
                else ["no predictions due ≤7d — read calibration state instead"]
            ),
            reversibility="read_only",
            blast_radius="self",
            expected_uncertainty_reduction=eur2,
            uncertainty_note="INT heuristic: each verification converts forecast uncertainty into scored knowledge",
            falsifier="all due predictions resolve UNVERIFIABLE (no calibration gain) → path yields zero",
        )
    )

    # Path 3 — CLARIFY (SABAR path; always present)
    eur3 = 0.4 if contested else 0.1
    ask = (
        f"adjudicate contested item: {contested[0]['content'][:70]}"
        if contested
        else "confirm priority: engine work before spread, per 2026-10-14 sequence?"
    )
    candidates.append(
        PathCandidate(
            id="path_clarify",
            name="clarify-sovereign",
            node_ids=["n_fq_pulse"],
            steps=[f"pose ONE binary question to F13: {ask}", "hold all mutation until answer"],
            reversibility="read_only",
            blast_radius="self",
            expected_uncertainty_reduction=eur3,
            uncertainty_note="INT heuristic: sovereign binary answer collapses the widest branch set",
            falsifier="answer already present in F13 channel log → asking wastes attention",
        )
    )

    pg = PlanGraph(
        id=f"pg_{int(_now * 1000):x}",
        root_intent=intent,
        nodes=nodes,
        candidates=candidates,
        history=[f"v0 first-batch: {len(nodes)} source nodes, {len(candidates)} paths"],
        created_at=datetime.fromtimestamp(_now, tz=timezone.utc).isoformat(),
        advisory=_ADVISORY,
        unsealable=True,
    )
    return pg


def compact_within_budget(pg: PlanGraph, budget: int = OUTPUT_BUDGET_BYTES) -> dict[str, Any]:
    """Compact dict hard-capped at budget bytes (F13 spec ≤2 KB)."""
    out = pg.compact()
    serialized = json.dumps(out, separators=(",", ":"), default=str)
    while len(serialized.encode("utf-8")) > budget:
        for p in out["paths"]:
            p["steps"] = [s[: max(20, len(s) - 20)] for s in p["steps"]]
            p["uncertainty_note"] = p["uncertainty_note"][:60]
            p["falsifier"] = p["falsifier"][:60]
        serialized = json.dumps(out, separators=(",", ":"), default=str)
        if all(len(s) <= 20 for p in out["paths"] for s in p["steps"]):
            break
    return out


__all__ = [
    "PlanGraph",
    "PlanNode",
    "PlanVerdict",
    "PathCandidate",
    "generate_paths",
    "compact_within_budget",
    "load_open_loops",
    "load_due_predictions",
    "load_fq",
    "OUTPUT_BUDGET_BYTES",
]
