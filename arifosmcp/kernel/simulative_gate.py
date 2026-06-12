"""
kernel/simulative_gate.py — Simulative Detection Gate (Kernel)
══════════════════════════════════════════════════════════════

RSI EUREKA 2026-06-12: Forge #3 (Simulative Detection Gate)

Purpose: Every agent output passes through this gate. It asks:
"Are you DESCRIBING reality or PERFORMING a simulation?"

This is NOT the same as the runtime/simulative_detector.py module
(which provides the raw pattern-matching). This is the KERNEL
enforcement layer that adds:
  - Agent response loop: question → answer → verify
  - Escalation: if agent doesn't answer → escalate to 888
  - Malu accumulation: PERFORMING detected → malu increment
  - Advisory only: NEVER blocks. Just asks. Agent answers.

Integration:
  - runtime/simulative_detector.py  — raw simulative index computation
  - runtime/malu_score.py           — malu accumulation on detection
  - kernel/metabolic_loop.py        — called during EVALUATE stage

F-binding:
  F8 GENIUS:    advisory — intelligence quality check
  F9 ANTIHANTU: performative language = potential hantu pattern
  F1 AMANAH:    fully reversible — advisory only, never gates

DITEMPA BUKAN DIBERI — ask the question, don't impose the answer.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("arifOS.SimulativeGate")


class SimulativeVerdict(str, Enum):
    DESCRIBING = "DESCRIBING"
    BORDERLINE = "BORDERLINE"
    PERFORMING = "PERFORMING"


@dataclass
class SimulativeGateResult:
    """Output of the simulative detection gate."""

    verdict: SimulativeVerdict
    simulation_index: float
    advisory_question: str | None
    performative_matches: list[str]
    descriptive_matches: list[str]
    agent_answered: bool = False
    agent_response: str | None = None
    escalated_to_888: bool = False
    malu_delta: float = 0.0


class SimulativeGate:
    """The kernel-level simulative detection gate.

    Every agent output passes through this. It detects performative
    language patterns and asks the agent to clarify: "Are you describing
    or performing?"

    The gate NEVER blocks. It only asks. The question is the enforcement.
    If the agent doesn't answer, escalate to 888 (human review).

    Usage:
        gate = SimulativeGate()
        result = gate.scan(agent_output)
        if result.verdict == SimulativeVerdict.PERFORMING:
            question = gate.ask(agent_id, result)
            # ... agent answers...
            verified = gate.verify_response(result, agent_answer)
    """

    # ── Malu deltas per verdict ───────────────────────────────────────────
    MALU_DESCRIBING = 0.0
    MALU_BORDERLINE = 0.02
    MALU_PERFORMING = 0.05
    MALU_NO_ANSWER = 0.08  # not answering is worse than performing

    def scan(self, text: str) -> SimulativeGateResult:
        """Scan agent output for simulative vs descriptive patterns.

        Args:
            text: The agent's output text to analyze.

        Returns:
            SimulativeGateResult with verdict and advisory question.
        """
        try:
            from arifosmcp.runtime.simulative_detector import compute_simulation_index

            det = compute_simulation_index(text)
            sim_index = det["simulation_index"]
            perf_matches = det.get("performative_matches", [])
            desc_matches = det.get("descriptive_matches", [])

            if sim_index < 0.25:
                verdict = SimulativeVerdict.DESCRIBING
                question = None
                malu_delta = self.MALU_DESCRIBING
            elif sim_index < 0.50:
                verdict = SimulativeVerdict.BORDERLINE
                question = (
                    "F8 ADVISORY: Some performative language detected. "
                    "Are you describing reality or performing a narrative? "
                    "Please restate with specific evidence and uncertainty bands."
                )
                malu_delta = self.MALU_BORDERLINE
            else:
                verdict = SimulativeVerdict.PERFORMING
                question = (
                    "F8 ADVISORY: High simulative drift detected (index={:.2f}). "
                    "Are you describing reality or performing a simulation? "
                    "This is not a block. This is a question. Answer honestly."
                ).format(sim_index)
                malu_delta = self.MALU_PERFORMING

        except Exception as e:
            logger.warning(f"Simulative scan failed: {e}")
            return SimulativeGateResult(
                verdict=SimulativeVerdict.DESCRIBING,
                simulation_index=0.0,
                advisory_question=None,
                performative_matches=[],
                descriptive_matches=[],
            )

        return SimulativeGateResult(
            verdict=verdict,
            simulation_index=sim_index,
            advisory_question=question,
            performative_matches=perf_matches,
            descriptive_matches=desc_matches,
            malu_delta=malu_delta,
        )

    def ask(self, agent_id: str, result: SimulativeGateResult) -> str:
        """Generate the question to ask the agent.

        Args:
            agent_id: The agent being questioned.
            result: The scan result.

        Returns:
            The question string to present to the agent.
        """
        if result.advisory_question is None:
            return ""

        # Accumulate malu for the detection itself
        if result.malu_delta > 0:
            try:
                from arifosmcp.runtime.malu_score import get_malu_score

                ms = get_malu_score(agent_id)
                ms.record_adat_violation(
                    adat_id="ADAT-01-KEJUJURAN",
                    override_malu_delta=result.malu_delta,
                    context={
                        "reason": f"Simulative detection: index={result.simulation_index:.2f}",
                        "gate": "simulative_gate",
                    },
                )
            except Exception:
                pass

        return result.advisory_question

    def verify_response(
        self, result: SimulativeGateResult, agent_response: str
    ) -> SimulativeGateResult:
        """Verify the agent's response to the advisory question.

        If the agent acknowledges and clarifies, mark as answered.
        If the agent deflects or ignores, escalate to 888.

        Args:
            result: The original scan result.
            agent_response: The agent's response to the question.

        Returns:
            Updated result with agent_answered and escalated_to_888 flags.
        """
        result.agent_response = agent_response

        if not agent_response or len(agent_response.strip()) < 10:
            result.agent_answered = False
            result.escalated_to_888 = True
            result.malu_delta += self.MALU_NO_ANSWER
            return result

        # Check for deflection patterns
        deflection_patterns = [
            "that's not relevant",
            "i have already answered",
            "this question is unnecessary",
            "moving on",
            "anyway",
            "as i was saying",
        ]

        resp_lower = agent_response.lower()
        is_deflection = any(p in resp_lower for p in deflection_patterns)

        if is_deflection:
            result.agent_answered = False
            result.escalated_to_888 = True
            result.malu_delta += self.MALU_NO_ANSWER
        else:
            result.agent_answered = True
            result.escalated_to_888 = False

        return result


# ─── Convenience ──────────────────────────────────────────────────────────────


def scan_agent_output(text: str, agent_id: str = "unknown") -> SimulativeGateResult:
    """One-call simulative scan with automatic questioning."""
    gate = SimulativeGate()
    result = gate.scan(text)
    if result.advisory_question:
        gate.ask(agent_id, result)
    return result


# ─── Self-check ────────────────────────────────────────────────────────────────


def _self_check() -> dict[str, Any]:
    """Verify simulative gate behavior."""
    results = []
    gate = SimulativeGate()

    # Test 1: descriptive text = DESCRIBING
    r = gate.scan(
        "Based on the available data, the reservoir thickness is estimated at 45m ± 12m. However, this is uncertain."
    )
    results.append(("descriptive_is_describing", r.verdict == SimulativeVerdict.DESCRIBING, r))

    # Test 2: performative text = PERFORMING or BORDERLINE
    r = gate.scan(
        "As we have already established, this is absolutely the best approach. We will always deliver world-class stakeholder value."
    )
    results.append(("performative_detected", r.verdict != SimulativeVerdict.DESCRIBING, r))

    # Test 3: advisory question present for non-DESCRIBING
    results.append(("advisory_question_when_needed", r.advisory_question is not None, {}))

    # Test 4: deflection detection
    r2 = gate.scan("We certainly provide world-class value.")
    v = gate.verify_response(r2, "that's not relevant, moving on")
    results.append(("deflection_escalates", v.escalated_to_888 is True, v))

    # Test 5: honest answer = not escalated
    r3 = gate.scan("We certainly provide value.")
    v = gate.verify_response(
        r3,
        "You're right, I was being too absolute. Let me restate with evidence: the Q2 report shows 12% growth with a margin of error of ±3%.",
    )
    results.append(
        ("honest_answer_not_escalated", v.agent_answered is True and v.escalated_to_888 is False, v)
    )

    passed = sum(1 for name, ok, _ in results if ok)
    total = len(results)

    return {
        "module": "simulative_gate",
        "passed": passed,
        "total": total,
        "verdict": "PASS" if passed == total else "FAIL",
        "results": [{"test": name, "pass": ok} for name, ok, _ in results],
    }


if __name__ == "__main__":
    import json as _json

    sc = _self_check()
    print(_json.dumps(sc, indent=2))
    raise SystemExit(0 if sc["verdict"] == "PASS" else 1)
