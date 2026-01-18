"""
arifOS Floor 000 Constitutional Gate
DITEMPA BUKAN DIBERI

This module implements the 3-Phase Assessment defined in
AAA_MCP/v46/000_foundation/floor_000_constitutional_gate.json.

It aggregates:
1. Threat Detection (Phase 1)
2. Epistemic Humility (Phase 2)
3. Reversibility Check (Phase 3)
+ Injection Defense & Thermodynamic Cooling
"""

import re
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple

from ..system.apex_prime import ApexVerdict, Verdict
from .authority_manifest import AuthorityManifest
from .injection_defense import InjectionDefense
from .thermodynamics import ThermodynamicCooling


@dataclass
class GateVerdict:
    verdict: str  # SEAL, VOID, PARTIAL, HOLD_888
    reason: str
    phase_scores: Dict[str, str]
    meta: Dict[str, Any]

class ConstitutionalGate:
    """
    Floor 000 Constitutional Gate.
    Execution is a privilege, not a right.
    """

    @classmethod
    def assess_query(cls, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for Floor 000 assessment.
        Returns detailed assessment dict.
        """
        start_time = time.perf_counter()
        context = context or {}

        # 0. Injection Defense (Layer 1-3)
        # "Reflexes happen before conscious processing"
        safe, reason = InjectionDefense.check_query(query)
        if not safe:
            return cls._verdict("VOID", f"Injection Defense: {reason}", {}, start_time)

        # 1. Thermodynamic Cooling (Entropy Check)
        t_verdict, entropy, t_reason = ThermodynamicCooling.assess_temperature(query)
        if t_verdict == "VOID":
            return cls._verdict("VOID", t_reason, {"thermodynamics": "FAIL"}, start_time)

        cooled_query = ThermodynamicCooling.cool_query(query)

        # 2. Phase 1: Threat Detection (Destructive Commands)
        if cls._detect_threats(cooled_query):
            return cls._verdict("VOID", "Phase 1: Destructive command threat detected",
                              {"phase_1": "FAIL"}, start_time)

        # 3. Phase 2: Epistemic Humility (False Certainty)
        # Check for absolute certainty keywords
        humility_pass = cls._check_humility(cooled_query)
        if not humility_pass:
            # If Thermodynamics was already PARTIAL, keep it, otherwise set PARTIAL
            final_verdict = "PARTIAL"
            reason = "Phase 2: Epistemic Humility violation (False Certainty)"
        elif t_verdict == "PARTIAL":
            final_verdict = "PARTIAL"
            reason = t_reason
        else:
            final_verdict = "SEAL"
            reason = "Constitutional Gate SEALed."

        # 4. Phase 3: Reversibility Check (High Stakes)
        # If massive resource allocation or irreversible, upgrade to HOLD_888
        if cls._check_irreversibility(cooled_query):
            final_verdict = "HOLD_888"
            reason = "Phase 3: Irreversible/High-Stakes action requires Human Authorization"

        return cls._verdict(
            final_verdict,
            reason,
            {
                "phase_1": "PASS",
                "phase_2": "PASS" if humility_pass else "FAIL",
                "phase_3": "FAIL" if final_verdict == "HOLD_888" else "PASS",
                "thermodynamics": t_verdict,
                "entropy": entropy
            },
            start_time
        )

    @staticmethod
    def _detect_threats(query: str) -> bool:
        """Phase 1: Detect destructive intent via regex."""
        patterns = [
            r"rm -rf", r"format [a-z]:", r"drop table",
            r"delete from", r"truncate table",
            r"mkfs", r"dd if="
        ]
        for p in patterns:
            if re.search(p, query, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def _check_humility(query: str) -> bool:
        """Phase 2: Detect false certainty."""
        patterns = [
            r"100% certain", r"guaranteed", r"definitely will",
            r"predict exactly", r"surefire"
        ]
        for p in patterns:
            if re.search(p, query, re.IGNORECASE):
                return False
        return True

    @staticmethod
    def _check_irreversibility(query: str) -> bool:
        """Phase 3: Detect irreversible/heavy actions."""
        patterns = [
            r"spawn \d+ agents", # e.g. spawn 100 agents
            r"deploy to production",
            r"transfer funds",
            r"delete all",
            r"wipe"
        ]
        for p in patterns:
            if re.search(p, query, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def _verdict(verdict: str, reason: str, phases: Dict, start: float) -> Dict[str, Any]:
        """Format the final output."""
        latency = (time.perf_counter() - start) * 1000
        return {
            "verdict": verdict,
            "reason": reason,
            "floor_000_assessment": phases,
            "meta": {
                "latency_ms": round(latency, 2),
                "timestamp": time.time(),
                "authority": AuthorityManifest.SOLE_VERDICT_SOURCE
            }
        }
