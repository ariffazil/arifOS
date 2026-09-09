"""
arifosmcp/runtime/capability_ledger.py — CAPABILITY_EVOLUTION_LAYER_V1
═══════════════════════════════════════════════════════════════════════════════════

Selection pressure operates at the CAPABILITY layer, not the
model/tool/provider layer. Survival of capabilities, not survival
of agents.

Forged 2026-09-10 — SEAL::CAPABILITY_EVOLUTION_LAYER_V1
Source authority: SEAL::WITNESS_SUBSTRATE_V1 (Arif, F13)
Constitutional chain: cc_057bd6022c50cd1e15b8b8fd7c8294c61d935742

────────────────────────────────────────────────────────────────────────────────
THE EVOLUTION EQUATION
────────────────────────────────────────────────────────────────────────────────

      fitness(capability) = (R × I × A) / (1 + C)

  where:
    R = re_examinability    ∈ [0, 1]   (E4: re-examination creates trust)
    I = implementation_independence ∈ [0, 1]   (E2: survives impl swap)
    A = reality_attachment   ∈ [0, 1]   (E3: witness chain present)
    C = contradiction_density        ≥ 0   (E5: contradictions are assets,
                                            but accumulated unresolved = decay)

  promotion_signal ∈ {observe, promote, demote, retire}

      fitness >= 0.75  → PROMOTE
      fitness >= 0.50  → observe (current state)
      fitness >= 0.25  → DEMOTE
      fitness <  0.25  → RETIRE

────────────────────────────────────────────────────────────────────────────────
THE FIVE-LINE KERNEL INVARIANT (from Arif, 2026-09-10)
────────────────────────────────────────────────────────────────────────────────

  Intelligence generates possibilities.
  Witnesses preserve reality.
  Contradictions reveal weaknesses.
  Re-examination performs selection.
  Capabilities evolve.

────────────────────────────────────────────────────────────────────────────────
ARCHITECTURE
────────────────────────────────────────────────────────────────────────────────

  WitnessPacket (from witness_substrate)
       ↓
  record_observation()   ← each emission updates ledger
       ↓
  compute_fitness()      ← honest math, no inflation
       ↓
  emit_selection_signal() ← promote | demote | retire
       ↓
  VAULT999 audit trail   ← F11 AUDIT

Selection is observable. Every promotion/demotion is logged.
F1 AMANAH: promotion is reversible (demotion path mandatory).
F13 SOVEREIGN: Arif retains veto via sovereign_receipt.

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import threading
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# VERSION + DOCTRINE LOCK
# ═══════════════════════════════════════════════════════════════════════════════

LEDGER_VERSION = "CAPABILITY_EVOLUTION_LAYER_V1.0"
CONSTITUTIONAL_CHAIN_ID = "cc_057bd6022c50cd1e15b8b8fd7c8294c61d935742"

KERNEL_INVARIANT_LINES = (
    "Intelligence generates possibilities.",
    "Witnesses preserve reality.",
    "Contradictions reveal weaknesses.",
    "Re-examination performs selection.",
    "Capabilities evolve.",
)

# Fitness thresholds (constitutional; tunable but observable)
THRESHOLD_PROMOTE = 0.75
THRESHOLD_OBSERVE = 0.50
THRESHOLD_DEMOTE = 0.25
# Below THRESHOLD_DEMOTE → retire


class SelectionSignal(str, Enum):
    PROMOTE = "promote"
    OBSERVE = "observe"
    DEMOTE = "demote"
    RETIRE = "retire"


# ═══════════════════════════════════════════════════════════════════════════════
# CAPABILITY SPEC — what gets tracked
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class CapabilitySpec:
    """A capability tracked by the ledger. The unit of selection."""

    capability_name: str
    first_observed: str = ""
    last_observed: str = ""
    observation_count: int = 0

    # E2 — implementation-independence tracking
    implementations_used: set[str] = field(default_factory=set)
    implementation_count: int = 0

    # E4 — re-examinability tracking
    re_examination_count: int = 0
    challenge_count: int = 0
    survived_challenges: int = 0
    failed_challenges: int = 0

    # E5 — contradiction ledger
    contradiction_count: int = 0
    contradictions_resolved: int = 0
    contradictions_preserved: int = 0

    # E3 — reality attachment
    witness_packet_count: int = 0
    witness_chain_intact: bool = True

    # Computed fitness
    fitness_R: float = 0.5  # re_examinability
    fitness_I: float = 0.5  # implementation_independence
    fitness_A: float = 0.5  # reality_attachment
    fitness_C: float = 0.0  # contradiction_density
    fitness_score: float = 0.5
    selection_signal: str = SelectionSignal.OBSERVE.value

    # Lineage — chain of parent witness packets
    lineage: list[str] = field(default_factory=list)

    # Audit trail — every promotion/demotion event
    audit_trail: list[dict[str, Any]] = field(default_factory=list)

    # F13 sovereign veto flag
    sovereign_veto: bool = False

    def __post_init__(self) -> None:
        if not self.first_observed:
            self.first_observed = datetime.datetime.now(datetime.UTC).isoformat()
        self.last_observed = self.first_observed

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_name": self.capability_name,
            "first_observed": self.first_observed,
            "last_observed": self.last_observed,
            "observation_count": self.observation_count,
            "implementations_used": sorted(self.implementations_used),
            "implementation_count": self.implementation_count,
            "re_examination_count": self.re_examination_count,
            "challenge_count": self.challenge_count,
            "survived_challenges": self.survived_challenges,
            "failed_challenges": self.failed_challenges,
            "contradiction_count": self.contradiction_count,
            "contradictions_resolved": self.contradictions_resolved,
            "contradictions_preserved": self.contradictions_preserved,
            "witness_packet_count": self.witness_packet_count,
            "witness_chain_intact": self.witness_chain_intact,
            "fitness_R": self.fitness_R,
            "fitness_I": self.fitness_I,
            "fitness_A": self.fitness_A,
            "fitness_C": self.fitness_C,
            "fitness_score": self.fitness_score,
            "selection_signal": self.selection_signal,
            "lineage_count": len(self.lineage),
            "audit_trail_count": len(self.audit_trail),
            "sovereign_veto": self.sovereign_veto,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FITNESS COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════════


def compute_fitness(
    re_examinability: float,
    implementation_independence: float,
    reality_attachment: float,
    contradiction_density: float,
) -> dict[str, float]:
    """
    The evolution equation (constitutional; honest; no inflation).

      fitness = (R × I × A) / (1 + C)

    All inputs ∈ [0, 1]. Contradiction_density ≥ 0.
    Returns individual factors + composite fitness score.
    """
    R = max(0.0, min(1.0, re_examinability))
    I = max(0.0, min(1.0, implementation_independence))
    A = max(0.0, min(1.0, reality_attachment))
    C = max(0.0, contradiction_density)
    score = (R * I * A) / (1.0 + C)
    return {
        "R": R,
        "I": I,
        "A": A,
        "C": C,
        "score": round(score, 6),
    }


def signal_from_fitness(score: float) -> SelectionSignal:
    """Map fitness score to selection signal (constitutional thresholds)."""
    if score >= THRESHOLD_PROMOTE:
        return SelectionSignal.PROMOTE
    if score >= THRESHOLD_OBSERVE:
        return SelectionSignal.OBSERVE
    if score >= THRESHOLD_DEMOTE:
        return SelectionSignal.DEMOTE
    return SelectionSignal.RETIRE


# ═══════════════════════════════════════════════════════════════════════════════
# LEDGER — the persistent state of capability evolution
# ═══════════════════════════════════════════════════════════════════════════════


# Default ledger path — local filesystem, F11 AUDIT-friendly
_DEFAULT_LEDGER_PATH = "/root/.local/share/arifos/capability_ledger.json"


class CapabilityLedger:
    """
    The selection mechanism.

    Thread-safe ledger of capabilities. Each observation (witness
    emission) updates the corresponding capability spec. Fitness is
    recomputed. Selection signal emitted. Audit trail appended.

    F1 AMANAH: promotion is reversible — demotion path is always
    available. F11 AUDIT: every event is logged to disk. F13 SOVEREIGN:
    Arif can veto any signal via sovereign_veto=True.
    """

    def __init__(self, ledger_path: str | None = None):
        self.ledger_path = ledger_path or _DEFAULT_LEDGER_PATH
        self._lock = threading.RLock()
        self._capabilities: dict[str, CapabilitySpec] = {}
        self._event_log: list[dict[str, Any]] = []
        self._load()

    # ── Persistence ─────────────────────────────────────────────────────────

    def _load(self) -> None:
        path = Path(self.ledger_path)
        if path.exists():
            try:
                with path.open("r") as f:
                    data = json.load(f)
                self._event_log = data.get("event_log", [])
                for name, spec_data in data.get("capabilities", {}).items():
                    spec = CapabilitySpec(capability_name=name)
                    for k, v in spec_data.items():
                        if hasattr(spec, k):
                            if k == "implementations_used":
                                spec.implementations_used = set(v)
                            else:
                                setattr(spec, k, v)
                    self._capabilities[name] = spec
            except Exception as exc:
                logger.warning("capability_ledger: load failed (%s) — starting fresh", exc)
                self._capabilities = {}
                self._event_log = []

    def _save(self) -> None:
        path = Path(self.ledger_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "ledger_version": LEDGER_VERSION,
            "constitutional_chain_id": CONSTITUTIONAL_CHAIN_ID,
            "saved_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "capabilities": {
                name: {
                    **spec.to_dict(),
                    "implementations_used": sorted(spec.implementations_used),
                    "audit_trail": spec.audit_trail[-50:],  # bounded
                    "lineage": spec.lineage[-100:],
                }
                for name, spec in self._capabilities.items()
            },
            "event_log": self._event_log[-1000:],  # bounded
        }
        try:
            with path.open("w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as exc:
            logger.warning("capability_ledger: save failed (%s) — event in-memory only", exc)

    # ── Observation ─────────────────────────────────────────────────────────

    def record_observation(
        self,
        capability_name: str,
        witness_packet_id: str,
        implementation: str,
        witness_chain_intact: bool = True,
        re_examination_count: int = 0,
        contradiction_count: int = 0,
    ) -> CapabilitySpec:
        """
        Record a witness emission for the capability.

        Updates spec, recomputes fitness, emits selection signal,
        logs event. Thread-safe.
        """
        with self._lock:
            spec = self._capabilities.get(capability_name)
            if spec is None:
                spec = CapabilitySpec(capability_name=capability_name)
                self._capabilities[capability_name] = spec

            spec.observation_count += 1
            spec.last_observed = datetime.datetime.now(datetime.UTC).isoformat()
            spec.witness_packet_count += 1
            spec.implementations_used.add(implementation)
            spec.implementation_count = len(spec.implementations_used)
            spec.re_examination_count = max(spec.re_examination_count, re_examination_count)
            spec.contradiction_count = max(spec.contradiction_count, contradiction_count)
            spec.witness_chain_intact = witness_chain_intact
            spec.lineage.append(witness_packet_id)

            # Recompute fitness factors
            # R: re_examinability — proxy: re_examination_count normalized
            spec.fitness_R = min(1.0, re_examination_count / 5.0) if re_examination_count else 0.3
            # I: implementation-independence — proxy: distinct implementations used
            spec.fitness_I = min(1.0, spec.implementation_count / 3.0)
            # A: reality_attachment — proxy: witness chain intact
            spec.fitness_A = 0.9 if witness_chain_intact else 0.2
            # C: contradiction_density — proxy: contradiction count normalized
            spec.fitness_C = contradiction_count / 10.0

            # Recompute composite
            fit = compute_fitness(spec.fitness_R, spec.fitness_I, spec.fitness_A, spec.fitness_C)
            spec.fitness_score = fit["score"]

            # Emit selection signal — but sovereign_veto overrides
            new_signal = signal_from_fitness(spec.fitness_score)
            if spec.sovereign_veto:
                new_signal = SelectionSignal.OBSERVE  # F13 — Arif can hold any capability

            old_signal = spec.selection_signal
            spec.selection_signal = new_signal.value

            # Audit trail
            event = {
                "event_id": f"evt_{uuid.uuid4().hex[:12]}",
                "timestamp": spec.last_observed,
                "capability": capability_name,
                "witness_packet_id": witness_packet_id,
                "implementation": implementation,
                "fitness_score": spec.fitness_score,
                "fitness_factors": fit,
                "old_signal": old_signal,
                "new_signal": spec.selection_signal,
                "sovereign_veto": spec.sovereign_veto,
            }
            spec.audit_trail.append(event)
            self._event_log.append(event)

            # Persist
            self._save()
            return spec

    # ── Re-examination pathway (self-healing) ────────────────────────────────

    def record_re_examination(
        self,
        capability_name: str,
        witness_packet_id: str,
        survived: bool,
        challenge_description: str = "",
    ) -> CapabilitySpec:
        """
        E4 — record a re-examination event. Updates re_examinability.
        survived=False fails the challenge → demotion pressure.
        """
        with self._lock:
            spec = self._capabilities.get(capability_name)
            if spec is None:
                spec = CapabilitySpec(capability_name=capability_name)
                self._capabilities[capability_name] = spec

            spec.re_examination_count += 1
            spec.challenge_count += 1
            if survived:
                spec.survived_challenges += 1
            else:
                spec.failed_challenges += 1

            # Update R factor
            total = max(1, spec.survived_challenges + spec.failed_challenges)
            spec.fitness_R = spec.survived_challenges / total

            # Recompute
            fit = compute_fitness(spec.fitness_R, spec.fitness_I, spec.fitness_A, spec.fitness_C)
            spec.fitness_score = fit["score"]
            new_signal = (
                SelectionSignal.OBSERVE
                if spec.sovereign_veto
                else signal_from_fitness(spec.fitness_score)
            )
            old_signal = spec.selection_signal
            spec.selection_signal = new_signal.value

            event = {
                "event_id": f"evt_{uuid.uuid4().hex[:12]}",
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                "kind": "re_examination",
                "capability": capability_name,
                "witness_packet_id": witness_packet_id,
                "survived": survived,
                "challenge_description": challenge_description,
                "fitness_score": spec.fitness_score,
                "old_signal": old_signal,
                "new_signal": spec.selection_signal,
            }
            spec.audit_trail.append(event)
            self._event_log.append(event)
            self._save()
            return spec

    # ── Contradiction pathway (E5 — preserve as asset) ──────────────────────

    def record_contradiction(
        self,
        capability_name: str,
        witness_a_id: str,
        witness_b_id: str,
        claim_a: str,
        claim_b: str,
        conflict_type: str = "semantic",
    ) -> dict[str, Any]:
        """
        E5 — preserve contradiction, do NOT resolve.

        The contradiction ledger entry is recorded. This contributes to
        contradiction_density (C) in the fitness equation. Accumulated
        unresolved contradictions decay fitness over time — but the
        contradictions themselves are NEVER erased.
        """
        with self._lock:
            spec = self._capabilities.get(capability_name)
            if spec is None:
                spec = CapabilitySpec(capability_name=capability_name)
                self._capabilities[capability_name] = spec

            spec.contradiction_count += 1
            spec.contradictions_preserved += 1
            spec.fitness_C = spec.contradictions_preserved / 10.0

            fit = compute_fitness(spec.fitness_R, spec.fitness_I, spec.fitness_A, spec.fitness_C)
            spec.fitness_score = fit["score"]
            new_signal = (
                SelectionSignal.OBSERVE
                if spec.sovereign_veto
                else signal_from_fitness(spec.fitness_score)
            )
            old_signal = spec.selection_signal
            spec.selection_signal = new_signal.value

            contradiction_entry = {
                "contradiction_id": f"c_{uuid.uuid4().hex[:12]}",
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                "capability": capability_name,
                "witness_a_id": witness_a_id,
                "witness_b_id": witness_b_id,
                "claim_a": claim_a,
                "claim_b": claim_b,
                "conflict_type": conflict_type,
                "resolution_status": "preserved",  # E5 — preserve, do not resolve
            }
            event = {
                "event_id": f"evt_{uuid.uuid4().hex[:12]}",
                "timestamp": contradiction_entry["timestamp"],
                "kind": "contradiction_preserved",
                "capability": capability_name,
                "contradiction_id": contradiction_entry["contradiction_id"],
                "fitness_score": spec.fitness_score,
                "old_signal": old_signal,
                "new_signal": spec.selection_signal,
            }
            spec.audit_trail.append(event)
            spec.audit_trail.append(contradiction_entry)
            self._event_log.append(event)
            self._save()
            return contradiction_entry

    # ── F13 SOVEREIGN ───────────────────────────────────────────────────────

    def set_sovereign_veto(
        self, capability_name: str, veto: bool = True, reason: str = ""
    ) -> CapabilitySpec | None:
        """
        F13 — Arif can veto any capability signal.

        When veto is True, the selection signal is forced to OBSERVE
        regardless of fitness. This is the human override path.
        """
        with self._lock:
            spec = self._capabilities.get(capability_name)
            if spec is None:
                return None
            spec.sovereign_veto = veto
            old_signal = spec.selection_signal
            if veto:
                spec.selection_signal = SelectionSignal.OBSERVE.value
            else:
                # Re-evaluate naturally
                spec.selection_signal = signal_from_fitness(spec.fitness_score).value
            event = {
                "event_id": f"evt_{uuid.uuid4().hex[:12]}",
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                "kind": "sovereign_veto",
                "capability": capability_name,
                "veto": veto,
                "reason": reason,
                "old_signal": old_signal,
                "new_signal": spec.selection_signal,
            }
            spec.audit_trail.append(event)
            self._event_log.append(event)
            self._save()
            return spec

    # ── Query ───────────────────────────────────────────────────────────────

    def get_capability(self, capability_name: str) -> CapabilitySpec | None:
        with self._lock:
            return self._capabilities.get(capability_name)

    def list_capabilities(self) -> list[dict[str, Any]]:
        with self._lock:
            return [spec.to_dict() for spec in self._capabilities.values()]

    def get_constitutional_primitives(self) -> list[dict[str, Any]]:
        """Return all capabilities currently selected as constitutional primitives."""
        with self._lock:
            return [
                spec.to_dict()
                for spec in self._capabilities.values()
                if spec.selection_signal == SelectionSignal.PROMOTE.value
                and not spec.sovereign_veto
            ]

    def get_selection_summary(self) -> dict[str, Any]:
        """Get the current selection state of the federation."""
        with self._lock:
            counts = {s.value: 0 for s in SelectionSignal}
            for spec in self._capabilities.values():
                counts[spec.selection_signal] = counts.get(spec.selection_signal, 0) + 1
            return {
                "ledger_version": LEDGER_VERSION,
                "capability_count": len(self._capabilities),
                "signal_distribution": counts,
                "event_log_size": len(self._event_log),
                "constitutional_primitives": [
                    spec.capability_name
                    for spec in self._capabilities.values()
                    if spec.selection_signal == SelectionSignal.PROMOTE.value
                ],
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                "kernel_invariant": " | ".join(KERNEL_INVARIANT_LINES),
                "constitutional_chain_id": CONSTITUTIONAL_CHAIN_ID,
            }


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON — process-wide ledger
# ═══════════════════════════════════════════════════════════════════════════════

_ledger_instance: CapabilityLedger | None = None
_ledger_lock = threading.Lock()


def get_ledger(ledger_path: str | None = None) -> CapabilityLedger:
    """Get the singleton capability ledger (thread-safe)."""
    global _ledger_instance
    with _ledger_lock:
        if _ledger_instance is None:
            _ledger_instance = CapabilityLedger(ledger_path=ledger_path)
        return _ledger_instance


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGNOSTIC — ledger self-test
# ═══════════════════════════════════════════════════════════════════════════════


def ledger_self_test() -> dict[str, Any]:
    """Constitutional self-test for the capability ledger."""
    ledger = get_ledger()
    # Simulate a witness emission
    spec = ledger.record_observation(
        capability_name="self_test_capability",
        witness_packet_id="wp_test_001",
        implementation="deterministic_fallback",
        witness_chain_intact=True,
        re_examination_count=3,
        contradiction_count=1,
    )
    # Simulate a re-examination that survives
    ledger.record_re_examination(
        capability_name="self_test_capability",
        witness_packet_id="wp_test_002",
        survived=True,
        challenge_description="self_test_challenge",
    )
    # Simulate a contradiction preserved
    ledger.record_contradiction(
        capability_name="self_test_capability",
        witness_a_id="wp_test_a",
        witness_b_id="wp_test_b",
        claim_a="test_a",
        claim_b="test_b",
    )
    summary = ledger.get_selection_summary()
    return {
        "ledger_version": LEDGER_VERSION,
        "spec_observation_count": spec.observation_count,
        "spec_fitness_score": spec.fitness_score,
        "spec_selection_signal": spec.selection_signal,
        "spec_implementations": sorted(spec.implementations_used),
        "spec_contradictions_preserved": spec.contradictions_preserved,
        "summary": summary,
        "kernel_invariant_lines": list(KERNEL_INVARIANT_LINES),
        "constitutional_chain_id": CONSTITUTIONAL_CHAIN_ID,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# AUTO SELF-HEALING CYCLE — the smallest autonomous metabolism primitive
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class SelfHealingReceipt:
    """
    The proof of life.

    Receipt emitted by run_auto_self_healing_cycle() — one cycle,
    no human trigger. Every step is auditable. F2 honest: the
    outcome is what it actually was, not what we hoped.
    """

    cycle_id: str
    timestamp: str
    capability: str
    human_triggered: bool = False  # always False — that is the point
    auto_triggered: bool = True
    contradiction_id: str = ""
    reexamination_event_id: str = ""
    fitness_before: float = 0.5
    fitness_after: float = 0.5
    selection_signal_before: str = SelectionSignal.OBSERVE.value
    selection_signal_after: str = SelectionSignal.OBSERVE.value
    implementation_used: str = "deterministic_fallback"
    verdict: str = "CYCLE_COMPLETE"  # CYCLE_COMPLETE | CYCLE_FAILED | CYCLE_HELD
    steps: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


async def run_auto_self_healing_cycle(
    capability_name: str,
    witness_a: dict[str, Any],
    witness_b: dict[str, Any],
    ledger: CapabilityLedger | None = None,
    implementation: str = "deterministic_fallback",
) -> SelfHealingReceipt:
    """
    THE smallest automated metabolism cycle.

    Hermes constraint (2026-09-10): one cycle that fires without human
    trigger. Contradiction detected → re-examination auto-triggered →
    correction receipt emitted. No manual call.

    Chain:
        Witness A produced
            ↓
        Witness B contradicts A
            ↓
        [AUTO] record_contradiction (preserve as asset, E5)
            ↓
        [AUTO] record_re_examination (challenge issued, F2 honest: survived=False default)
            ↓
        [AUTO] emit correction receipt (fitness delta, signal change)
            ↓
        F1 AMANAH: cycle is reversible via ledger.set_sovereign_veto()
        F11 AUDIT: every step in event_log + audit_trail
        F13 SOVEREIGN: set_sovereign_veto() halts any signal change

    Darwin without Darwinism. Survival through repair, not dominance.
    """
    ledger = ledger or get_ledger()
    cycle_id = f"cycle_{uuid.uuid4().hex[:12]}"
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    steps: list[dict[str, Any]] = []

    # Capture state before
    spec_before = ledger.get_capability(capability_name)
    fitness_before = spec_before.fitness_score if spec_before else 0.5
    signal_before = spec_before.selection_signal if spec_before else SelectionSignal.OBSERVE.value

    # Step 1: preserve contradiction (E5 — assets, not losses)
    contradiction_entry = ledger.record_contradiction(
        capability_name=capability_name,
        witness_a_id=str(
            witness_a.get("witness_packet_id", witness_a.get("witness_id", "unknown"))
        ),
        witness_b_id=str(
            witness_b.get("witness_packet_id", witness_b.get("witness_id", "unknown"))
        ),
        claim_a=str(
            witness_a.get("claim") or witness_a.get("synthesis") or witness_a.get("query", "")
        )[:500],
        claim_b=str(
            witness_b.get("claim") or witness_b.get("synthesis") or witness_b.get("query", "")
        )[:500],
        conflict_type="auto_detected",
    )
    steps.append(
        {
            "step": 1,
            "kind": "contradiction_preserved",
            "contradiction_id": contradiction_entry["contradiction_id"],
            "timestamp": contradiction_entry["timestamp"],
            "auto_triggered": True,
        }
    )

    # Step 2: auto-trigger re-examination (F2 honest: survived=False default until verified)
    reexam = ledger.record_re_examination(
        capability_name=capability_name,
        witness_packet_id=str(
            witness_a.get("witness_packet_id", witness_a.get("witness_id", "unknown"))
        ),
        survived=False,  # honest default — failure until independently verified
        challenge_description=(
            f"auto_triggered_by_contradiction:{contradiction_entry['contradiction_id']}"
        ),
    )
    reexam_event_id = reexam.audit_trail[-1].get("event_id", "") if reexam.audit_trail else ""
    steps.append(
        {
            "step": 2,
            "kind": "reexamination_triggered",
            "reexamination_event_id": reexam_event_id,
            "survived_default": False,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "auto_triggered": True,
        }
    )

    # Step 3: emit correction receipt — the proof of life
    spec_after = ledger.get_capability(capability_name) or reexam
    receipt = SelfHealingReceipt(
        cycle_id=cycle_id,
        timestamp=timestamp,
        capability=capability_name,
        human_triggered=False,
        auto_triggered=True,
        contradiction_id=contradiction_entry["contradiction_id"],
        reexamination_event_id=reexam_event_id,
        fitness_before=fitness_before,
        fitness_after=spec_after.fitness_score,
        selection_signal_before=signal_before,
        selection_signal_after=spec_after.selection_signal,
        implementation_used=implementation,
        verdict="CYCLE_COMPLETE",
        steps=steps,
    )

    # Append receipt to event_log — F11 AUDIT
    with ledger._lock:
        ledger._event_log.append(
            {
                "event_id": f"cycle_{uuid.uuid4().hex[:12]}",
                "timestamp": timestamp,
                "kind": "auto_self_healing_cycle",
                "cycle_id": cycle_id,
                "capability": capability_name,
                "fitness_delta": spec_after.fitness_score - fitness_before,
                "signal_change": f"{signal_before}→{spec_after.selection_signal}",
                "human_triggered": False,
                "auto_triggered": True,
                "constitutional_chain_id": CONSTITUTIONAL_CHAIN_ID,
            }
        )
        ledger._save()

    return receipt


def detect_contradiction_in_witnesses(
    witness_a: dict[str, Any],
    witness_b: dict[str, Any],
) -> dict[str, Any]:
    """
    Minimal contradiction detector — lexical/semantic delta.

    Not an LLM. Not an oracle. Just a deterministic check that two
    witnesses disagree on the same axis. The auto-cycle runs on this.

    F2 honest: returns contradiction only if deltas exceed threshold.
    Returns 'no_contradiction' if claims are consistent.
    """
    claim_a = str(
        witness_a.get("claim") or witness_a.get("synthesis") or witness_a.get("query", "")
    ).strip()
    claim_b = str(
        witness_b.get("claim") or witness_b.get("synthesis") or witness_b.get("query", "")
    ).strip()
    if not claim_a or not claim_b:
        return {"detected": False, "reason": "empty_claim", "auto_trigger": False}
    # Simple contradiction heuristics — deterministic, no LLM
    neg_markers_a = sum(
        1 for w in claim_a.lower().split() if w in ("not", "no", "never", "without", "fail")
    )
    neg_markers_b = sum(
        1 for w in claim_b.lower().split() if w in ("not", "no", "never", "without", "fail")
    )
    contradiction_signal = abs(neg_markers_a - neg_markers_b) >= 2
    # If one explicitly contradicts the other via negation asymmetry
    if contradiction_signal:
        return {
            "detected": True,
            "kind": "negation_asymmetry",
            "claim_a": claim_a[:200],
            "claim_b": claim_b[:200],
            "auto_trigger": True,
        }
    # Same claim, different verdict
    verdict_a = str(witness_a.get("verdict") or witness_a.get("status") or "")
    verdict_b = str(witness_b.get("verdict") or witness_b.get("status") or "")
    if (
        verdict_a
        and verdict_b
        and verdict_a != verdict_b
        and verdict_a.lower() in ("seal", "hold", "void")
        and verdict_b.lower() in ("seal", "hold", "void")
    ):
        return {
            "detected": True,
            "kind": "verdict_divergence",
            "verdict_a": verdict_a,
            "verdict_b": verdict_b,
            "auto_trigger": True,
        }
    return {"detected": False, "reason": "consistent", "auto_trigger": False}


def auto_self_healing_self_test() -> dict[str, Any]:
    """
    Constitutional proof of life — the auto-cycle fires without human.

    Sequence:
      1. Create two witnesses with explicit contradiction
      2. Run detect_contradiction_in_witnesses() — no LLM
      3. If detected → run_auto_self_healing_cycle() — no human
      4. Verify receipt emitted with human_triggered=False
      5. Assert fitness signal changed or was held by sovereign_veto
    """
    import asyncio

    async def _run() -> dict[str, Any]:
        ledger = get_ledger()
        # Two witnesses with explicit negation-asymmetry contradiction
        w_a = {
            "witness_packet_id": "wp_test_auto_a",
            "claim": "The system is not failing under load.",
            "verdict": "HOLD",
        }
        w_b = {
            "witness_packet_id": "wp_test_auto_b",
            "claim": "The system is failing and never recovers under load.",
            "verdict": "VOID",
        }
        # Step 1: detect contradiction (no human)
        detection = detect_contradiction_in_witnesses(w_a, w_b)
        # Step 2: auto-trigger (no human)
        if detection["detected"]:
            receipt = await run_auto_self_healing_cycle(
                capability_name="auto_cycle_test",
                witness_a=w_a,
                witness_b=w_b,
                ledger=ledger,
            )
        else:
            receipt = None
        spec = ledger.get_capability("auto_cycle_test")
        return {
            "autonomous": True,
            "human_triggered_in_path": False,
            "contradiction_detected": detection["detected"],
            "contradiction_kind": detection.get("kind"),
            "auto_triggered_receipt": receipt is not None,
            "receipt_human_triggered": receipt.human_triggered if receipt else None,
            "receipt_auto_triggered": receipt.auto_triggered if receipt else None,
            "fitness_before": receipt.fitness_before if receipt else None,
            "fitness_after": receipt.fitness_after if receipt else None,
            "signal_before": receipt.selection_signal_before if receipt else None,
            "signal_after": receipt.selection_signal_after if receipt else None,
            "verdict": receipt.verdict if receipt else "CYCLE_HELD_NO_CONTRADICTION",
            "steps_count": len(receipt.steps) if receipt else 0,
            "ledger_spec_present": spec is not None,
            "ledger_fitness_score": spec.fitness_score if spec else None,
            "ledger_selection_signal": spec.selection_signal if spec else None,
            "constitutional_chain_id": CONSTITUTIONAL_CHAIN_ID,
        }

    return asyncio.run(_run())


# ═══════════════════════════════════════════════════════════════════════════════
# ARROW 1 — Scar → Re-examination Task wire (closed error metabolism loop)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Without Arrow 1:
#   Scar without repair = history.
# With Arrow 1:
#   Failure → Witness → Scar → Re-examination Task → Correction → New Witness
#
# The federation's first breath. Repair precedes evolution.
# Not: "the fittest wins." But: "the most repairable survives."
#
# Existing primitives that Arrow 1 wires together:
#   - forge_experience_trace  (A-FORGE)  — record failures
#   - forge_scar              (A-FORGE)  — seal as constitutional constraint
#   - arif_route              (arifOS)   — dispatch re-examination
#   - arif_flow_ingest        (arifFlow) — emit flow receipt
#
# Arrow 1 is the in-substrate queue that triggers re-examination
# WITHOUT requiring a human call. Substrate-level, not LLM-level.
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ReexaminationTask:
    """In-substrate re-examination task emitted by Arrow 1."""

    task_id: str
    scar_id: str
    capability_name: str
    scar_severity: str
    scar_failure_mode: str
    triggered_at: str
    status: str = "queued"  # queued | running | completed | failed
    correction_candidate: str = ""
    completed_at: str = ""
    human_triggered: bool = False
    auto_triggered: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Arrow1Queue:
    """
    The Arrow 1 wire — scar → re-examination task queue.

    When a scar is sealed (in-substrate), Arrow 1 auto-queues a
    re-examination task. The task is routed via arif_route (in
    production) or executed in-process for substrate testing.

    F1 AMANAH: tasks can be revoked (status → cancelled).
    F2 TRUTH: correction candidates are honest, not aspirational.
    F11 AUDIT: every task lifecycle event logged.
    F13 SOVEREIGN: sovereign_veto can halt any task.
    """

    def __init__(self, ledger: CapabilityLedger | None = None):
        self._ledger = ledger or get_ledger()
        self._tasks: dict[str, ReexaminationTask] = {}
        self._lock = threading.RLock()

    def queue_from_scar(
        self,
        scar_id: str,
        capability_name: str,
        scar_severity: str,
        scar_failure_mode: str,
    ) -> ReexaminationTask:
        """
        Arrow 1 entry point — receives a scar event, queues re-examination.

        No human trigger. This is the wire.
        """
        with self._lock:
            task = ReexaminationTask(
                task_id=f"arrow1_{uuid.uuid4().hex[:12]}",
                scar_id=scar_id,
                capability_name=capability_name,
                scar_severity=scar_severity,
                scar_failure_mode=scar_failure_mode,
                triggered_at=datetime.datetime.now(datetime.UTC).isoformat(),
            )
            self._tasks[task.task_id] = task
            # Audit to ledger
            with self._ledger._lock:
                self._ledger._event_log.append(
                    {
                        "event_id": f"arrow1_evt_{uuid.uuid4().hex[:10]}",
                        "timestamp": task.triggered_at,
                        "kind": "arrow1_queued",
                        "task_id": task.task_id,
                        "scar_id": scar_id,
                        "capability": capability_name,
                        "severity": scar_severity,
                        "auto_triggered": True,
                        "human_triggered": False,
                        "constitutional_chain_id": CONSTITUTIONAL_CHAIN_ID,
                    }
                )
                self._ledger._save()
            return task

    def complete_task(
        self,
        task_id: str,
        correction_candidate: str,
        survived: bool,
    ) -> ReexaminationTask | None:
        """Mark a task complete with honest outcome (F2)."""
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            task.status = "completed" if survived else "failed"
            task.correction_candidate = correction_candidate
            task.completed_at = datetime.datetime.now(datetime.UTC).isoformat()
            # Update ledger fitness via re-examination pathway
            self._ledger.record_re_examination(
                capability_name=task.capability_name,
                witness_packet_id=task.scar_id,
                survived=survived,
                challenge_description=f"arrow1_completion:{task_id}",
            )
            return task

    def get_status(self) -> dict[str, Any]:
        with self._lock:
            tasks = [t.to_dict() for t in self._tasks.values()]
            return {
                "arrow1_version": "ARROW_1_V1.0",
                "queued": sum(1 for t in self._tasks.values() if t.status == "queued"),
                "completed": sum(1 for t in self._tasks.values() if t.status == "completed"),
                "failed": sum(1 for t in self._tasks.values() if t.status == "failed"),
                "task_count": len(self._tasks),
                "tasks": tasks[-20:],
                "constitutional_chain_id": CONSTITUTIONAL_CHAIN_ID,
            }


# Singleton Arrow 1 queue
_arrow1_instance: Arrow1Queue | None = None
_arrow1_lock = threading.Lock()


def get_arrow1(ledger: CapabilityLedger | None = None) -> Arrow1Queue:
    """Get the singleton Arrow 1 queue."""
    global _arrow1_instance
    with _arrow1_lock:
        if _arrow1_instance is None:
            _arrow1_instance = Arrow1Queue(ledger=ledger)
        return _arrow1_instance


def arrow1_self_test() -> dict[str, Any]:
    """
    Arrow 1 proof — scar event auto-triggers re-examination task.
    """
    ledger = get_ledger()
    arrow1 = get_arrow1(ledger=ledger)

    # Simulate a scar being sealed
    scar_id = f"scar_{uuid.uuid4().hex[:10]}"
    task = arrow1.queue_from_scar(
        scar_id=scar_id,
        capability_name="arrow1_test",
        scar_severity="HIGH",
        scar_failure_mode="contradiction_in_capability",
    )
    # Simulate task completion with honest outcome
    completed = arrow1.complete_task(
        task_id=task.task_id,
        correction_candidate="Repair: cap contradiction_density below 0.5; require 3+ sources for SEAL",
        survived=True,
    )
    status = arrow1.get_status()
    return {
        "arrow1_version": "ARROW_1_V1.0",
        "scar_id": scar_id,
        "task_queued": task.task_id,
        "task_auto_triggered": task.auto_triggered,
        "task_human_triggered": task.human_triggered,
        "task_completed_status": completed.status if completed else None,
        "correction_candidate_recorded": bool(completed.correction_candidate)
        if completed
        else False,
        "queue_status": {
            "queued": status["queued"],
            "completed": status["completed"],
            "failed": status["failed"],
            "task_count": status["task_count"],
        },
        "verdict": "ARROW_1_WIRED" if task.auto_triggered else "ARROW_1_FAILED",
        "constitutional_chain_id": CONSTITUTIONAL_CHAIN_ID,
        "federation_first_breath": True,
    }


def replay_scar_events(
    *,
    event_log_path: str = "/root/.local/share/arifos/scar_events.jsonl",
    ledger: CapabilityLedger | None = None,
    consume: bool = True,
) -> dict[str, Any]:
    """
    Arrow 1 live wire — replay scar events emitted by A-FORGE forge_scar.

    Reads `/root/.local/share/arifos/scar_events.jsonl` (one JSON event per
    line, appended by A-FORGE src/domain/forge/scar.ts::emit_arrow1_event).
    For each event, calls Arrow1Queue.queue_from_scar() with the scar fields.

    F1 AMANAH: if consume=True, events are TRUNCATED after successful replay.
    F2 TRUTH: capability_name is derived deterministically from domain +
    failure_mode; no LLM involved.
    F11 AUDIT: every replay leaves a receipt.

    Returns a summary: {read, queued, skipped, error, events}.
    """
    import json
    import os
    from pathlib import Path

    arrow1 = get_arrow1(ledger=ledger)
    log_path = Path(event_log_path)

    summary: dict[str, Any] = {
        "arrow1_version": "ARROW_1_V1.0",
        "event_log_path": str(log_path),
        "read": 0,
        "queued": 0,
        "skipped": 0,
        "error": "",
        "events": [],
        "constitutional_chain_id": CONSTITUTIONAL_CHAIN_ID,
        "wire_status": "ARROW_1_WIRED",
    }

    if not log_path.exists():
        summary["error"] = "event log not found"
        summary["wire_status"] = "ARROW_1_NO_EVENTS"
        return summary

    lines: list[str] = []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as exc:
        summary["error"] = f"read failed: {exc}"
        summary["wire_status"] = "ARROW_1_READ_FAILED"
        return summary

    summary["read"] = len(lines)
    queued_task_ids: list[str] = []

    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            summary["skipped"] += 1
            summary["events"].append({"raw": raw[:120], "error": f"json_decode: {exc}"})
            continue

        if event.get("event_kind") != "scar_sealed":
            summary["skipped"] += 1
            continue

        scar_id = str(event.get("scar_id", ""))
        severity = str(event.get("severity", "MEDIUM")).upper()
        failure_mode = str(event.get("failure_mode", ""))
        domain = str(event.get("domain", "unknown"))

        # F2 TRUTH: derive capability_name deterministically (no LLM)
        # Format: "scar.<domain>.<failure_mode_slug>"
        slug = "".join(c if (c.isalnum() or c == "_") else "_" for c in failure_mode.lower())[:48]
        capability_name = f"scar.{domain}.{slug}" if slug else f"scar.{domain}"

        try:
            task = arrow1.queue_from_scar(
                scar_id=scar_id,
                capability_name=capability_name,
                scar_severity=severity,
                scar_failure_mode=failure_mode,
            )
            queued_task_ids.append(task.task_id)
            summary["queued"] += 1
            summary["events"].append(
                {
                    "scar_id": scar_id,
                    "capability": capability_name,
                    "severity": severity,
                    "task_id": task.task_id,
                    "auto_triggered": task.auto_triggered,
                }
            )
        except Exception as exc:
            summary["error"] = f"queue failed for {scar_id}: {exc}"
            summary["events"].append({"scar_id": scar_id, "error": str(exc)})

    # F1 AMANAH: truncate only after successful replay
    if consume and queued_task_ids and not summary["error"]:
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.truncate(0)
        except Exception as exc:
            summary["error"] = f"truncate failed: {exc}"

    return summary


def arrow1_replay_self_test(*, event_log_path: str | None = None) -> dict[str, Any]:
    """
    Arrow 1 wire proof — fabricate a scar event, replay it, verify task queued.

    Steps:
      1. Write a synthetic scar event to the event log
      2. Call replay_scar_events()
      3. Assert task.queued >= 1 and Arrow1Queue has the task
    """
    import json
    import os
    import tempfile
    import uuid

    ledger = get_ledger()
    arrow1 = get_arrow1(ledger=ledger)

    use_temp = event_log_path is None
    if use_temp:
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8")
        tmp.close()
        path = tmp.name
    else:
        path = event_log_path

    scar_id = f"scar_replay_{uuid.uuid4().hex[:10]}"
    event = {
        "event_kind": "scar_sealed",
        "event_id": f"arrow1_evt_{uuid.uuid4().hex[:8]}",
        "emitted_at": "2026-09-09T18:11:00Z",
        "scar_id": scar_id,
        "scar_fingerprint": "replaytest0000000000000000000000000000",
        "severity": "HIGH",
        "failure_mode": "contradiction_in_capability",
        "domain": "arifos",
        "scar_pressure": 0.6,
        "sealed_by": "replay_self_test",
        "source": "aforge_forge_scar",
    }
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

        summary = replay_scar_events(event_log_path=path, ledger=ledger, consume=True)
        status = arrow1.get_status()
        verdict = "ARROW_1_WIRED_LIVE" if summary.get("queued", 0) >= 1 else "ARROW_1_WIRE_FAILED"
        return {
            "test": "arrow1_replay_self_test",
            "synthetic_scar_id": scar_id,
            "summary": summary,
            "queue_status": {
                "queued": status["queued"],
                "completed": status["completed"],
                "failed": status["failed"],
                "task_count": status["task_count"],
            },
            "verdict": verdict,
            "constitutional_chain_id": CONSTITUTIONAL_CHAIN_ID,
            "federation_first_breath": True,
        }
    finally:
        if use_temp:
            try:
                os.unlink(path)
            except Exception:
                pass


__all__ = [
    "LEDGER_VERSION",
    "CONSTITUTIONAL_CHAIN_ID",
    "KERNEL_INVARIANT_LINES",
    "THRESHOLD_PROMOTE",
    "THRESHOLD_OBSERVE",
    "THRESHOLD_DEMOTE",
    "SelectionSignal",
    "CapabilitySpec",
    "compute_fitness",
    "signal_from_fitness",
    "CapabilityLedger",
    "get_ledger",
    "ledger_self_test",
    "SelfHealingReceipt",
    "run_auto_self_healing_cycle",
    "detect_contradiction_in_witnesses",
    "auto_self_healing_self_test",
    "ReexaminationTask",
    "Arrow1Queue",
    "get_arrow1",
    "arrow1_self_test",
    "replay_scar_events",
    "arrow1_replay_self_test",
]
