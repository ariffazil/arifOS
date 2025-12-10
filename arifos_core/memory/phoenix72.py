"""
phoenix72.py — L2 Metabolism (Phoenix-72) for arifOS v33Ω.

Implements the scar → pattern → amendment → canonization workflow.

Specification: spec/PHOENIX_72.md
"""

from __future__ import annotations

import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from .vault999 import Vault999
from .cooling_ledger import CoolingLedger


# -------------------------
# Phoenix Entities
# -------------------------

@dataclass
class Scar:
    timestamp: float
    floor_failures: List[str]
    reason: str
    ledger_ref: Dict[str, Any]


@dataclass
class PhoenixAmendment:
    id: str
    applied_at: str
    reason: str
    tri_witness: float
    delta_s_gain: float
    peace2: float
    changes: Dict[str, Any]
    evidence: List[Dict[str, Any]]


# -------------------------
# Phoenix-72 Engine
# -------------------------

class Phoenix72:
    """
    Phoenix-72 Constitutional Amendment Engine.

    Example:
        phoenix = Phoenix72(vault, ledger)
        scars = phoenix.collect_scars()
        pattern = phoenix.synthesize_pattern(scars)
        amendment = phoenix.propose_amendment(pattern)
        phoenix.apply_amendment(amendment)
    """

    def __init__(self, vault: Vault999, ledger: CoolingLedger):
        self.vault = vault
        self.ledger = ledger

    # ------------------------------------------------------------
    # Phase 1 — SCAR CAPTURE
    # ------------------------------------------------------------

    def collect_scars(self, hours: float = 72.0) -> List[Scar]:
        scars: List[Scar] = []

        for entry in self.ledger.iter_recent(hours=hours):
            failures = entry.get("floor_failures", [])
            if failures:
                scars.append(
                    Scar(
                        timestamp=entry.get("timestamp", time.time()),
                        floor_failures=failures,
                        reason="; ".join(failures),
                        ledger_ref=entry,
                    )
                )

        return scars

    # ------------------------------------------------------------
    # Phase 2 — PATTERN SYNTHESIS
    # ------------------------------------------------------------

    def synthesize_pattern(self, scars: List[Scar]) -> Optional[Dict[str, Any]]:
        if not scars:
            return None

        # Primitive heuristic: group by first failure
        groups = {}
        for scar in scars:
            key = scar.floor_failures[0]
            groups.setdefault(key, []).append(scar)

        # Pick largest cluster as initial pattern
        dominant = max(groups.values(), key=len)
        return {
            "dominant_failure": dominant[0].floor_failures[0],
            "count": len(dominant),
            "evidence": [s.ledger_ref for s in dominant],
        }

    # ------------------------------------------------------------
    # Phase 3 — DRAFT AMENDMENT
    # ------------------------------------------------------------

    def draft_amendment(self, pattern: Dict[str, Any]) -> PhoenixAmendment:
        failure = pattern["dominant_failure"]

        # Example policy: tighten truth_min by +0.005 if Truth floor failing
        floors = self.vault.get_floors().copy()
        changes = {}

        if "Truth" in failure:
            floors["truth_min"] = min(0.999, floors["truth_min"] + 0.005)
            changes["floors"] = floors

        # Other floor tweaks could be added based on pattern

        return PhoenixAmendment(
            id=f"PHOENIX-72-{int(time.time())}",
            applied_at=self._now(),
            reason=f"Phoenix pattern on failure: {failure}",
            tri_witness=0.95,  # placeholder for real Tri-Witness calc
            delta_s_gain=0.2,
            peace2=1.02,
            changes=changes,
            evidence=pattern["evidence"],
        )

    # ------------------------------------------------------------
    # Phase 4–5 — AMENDMENT CANONIZATION
    # ------------------------------------------------------------

    def apply_amendment(self, amendment: PhoenixAmendment) -> None:
        """
        Apply the amendment to Vault-999 and log it to the Cooling Ledger.
        """
        # Update floors in Vault-999
        if "floors" in amendment.changes:
            self.vault.update_floors(
                new_floors=amendment.changes["floors"],
                phoenix_id=amendment.id,
            )

        # Log amendment in Cooling Ledger
        entry = {
            "timestamp": time.time(),
            "query": "PHOENIX-72-AMENDMENT",
            "candidate_output": "N/A",
            "metrics": {
                "truth": 1.0,
                "delta_s": amendment.delta_s_gain,
                "peace_squared": amendment.peace2,
                "kappa_r": 1.0,
                "omega_0": 0.04,
                "rasa": True,
                "amanah": True,
                "tri_witness": amendment.tri_witness,
                "psi": 1.1,
            },
            "verdict": "AMEND",
            "floor_failures": [],
            "sabar_reason": None,
            "organs": {},
            "phoenix_cycle_id": amendment.id,
            "metadata": {"amendment": asdict(amendment)},
        }

        from .cooling_ledger import CoolingEntry, CoolingMetrics

        metrics = CoolingMetrics(**entry["metrics"])
        ledger_entry = CoolingEntry(
            timestamp=entry["timestamp"],
            query=entry["query"],
            candidate_output=entry["candidate_output"],
            metrics=metrics,
            verdict="AMEND",
            floor_failures=[],
            sabar_reason=None,
            organs={},
            phoenix_cycle_id=amendment.id,
            metadata=entry["metadata"],
        )

        self.ledger.append(ledger_entry)

    # ------------------------------------------------------------

    @staticmethod
    def _now() -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
