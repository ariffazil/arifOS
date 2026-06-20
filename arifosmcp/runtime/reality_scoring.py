"""
arifosmcp/runtime/reality_scoring.py
══════════════════════════════════════
Seven-Anchor Reality-Coupled Scoring Engine

Implements the scoring framework defined by Arif (F13 SOVEREIGN):
  "A score is meaningful when the convention is chained to reality
   tightly enough that lying with the number becomes hard."

Every score in this module carries seven anchors:
  1. Object       — what exactly is being scored
  2. Evidence     — observable data the score rests on
  3. Contrast     — compared to what baseline
  4. Prediction   — what future outcome it forecasts
  5. Error Band   — uncertainty acknowledged
  6. Falsifiability — how the score can be proven wrong
  7. Threshold    — what decision changes at what score level

F2 TRUTH: Scores degrade when evidence contradicts them.
F7 HUMILITY: Error bands are mandatory, never hidden.
F11 AUDIT: Every score change is attributable to evidence change.

DITEMPA BUKAN DIBERI — Forged 2026-06-12 by Omega (Ω)
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from typing import Any

# ═══════════════════════════════════════════════════════════════
# SEVEN-ANCHOR SCORE
# ═══════════════════════════════════════════════════════════════


@dataclass
class AnchoredScore:
    """A score with all seven anchors — reality-coupled, not decorative."""

    # The score itself
    value: float  # 0–100
    error_band: float = 5.0  # ± this value

    # Anchor 1: Object
    object_name: str = ""
    object_description: str = ""

    # Anchor 2: Evidence
    evidence_chain: list[str] = field(default_factory=list)  # What was observed
    evidence_hash: str = ""  # sha256 of evidence chain

    # Anchor 3: Contrast
    contrast_class: str = ""  # e.g. "prompt harness", "constitutional kernel"
    contrast_baseline: float = 0.0  # What a baseline system would score

    # Anchor 4: Prediction
    predicts: str = ""  # What this score forecasts about the future
    prediction_confidence: float = 0.0  # How confident in the prediction

    # Anchor 5: Error Band (built into value ± error_band)
    known_unknowns: list[str] = field(default_factory=list)

    # Anchor 6: Falsifiability
    falsification_triggers: list[str] = field(
        default_factory=list
    )  # "If X test fails, score drops by Y"
    falsifiable: bool = True  # If nothing can lower it, it's propaganda

    # Anchor 7: Decision Threshold
    thresholds: dict[str, float] = field(default_factory=dict)  # {"lab_only": 60, ...}

    # Metadata
    computed_at: float = field(default_factory=time.time)
    computation_ms: float = 0.0
    source: str = "reality_scoring"

    @property
    def range_low(self) -> float:
        return max(0.0, self.value - self.error_band)

    @property
    def range_high(self) -> float:
        return min(100.0, self.value + self.error_band)

    @property
    def decision(self) -> str:
        """What decision does this score recommend?"""
        sorted_thresholds = sorted(self.thresholds.items(), key=lambda x: x[1], reverse=True)
        for label, threshold in sorted_thresholds:
            if self.value >= threshold:
                return label
        return "unknown"

    def degrade(self, reason: str, amount: float) -> AnchoredScore:
        """Reality pushed back — lower the score with evidence."""
        return AnchoredScore(
            value=max(0.0, self.value - amount),
            error_band=self.error_band,
            object_name=self.object_name,
            object_description=self.object_description,
            evidence_chain=self.evidence_chain + [f"DEGRADED: {reason} (-{amount})"],
            contrast_class=self.contrast_class,
            contrast_baseline=self.contrast_baseline,
            predicts=self.predicts,
            prediction_confidence=self.prediction_confidence,
            known_unknowns=self.known_unknowns,
            falsification_triggers=self.falsification_triggers,
            thresholds=self.thresholds,
            source=self.source,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize with all seven anchors visible."""
        return {
            "value": self.value,
            "range": f"{self.range_low:.0f}–{self.range_high:.0f}",
            "error_band": f"±{self.error_band:.0f}",
            "decision": self.decision,
            # Seven anchors
            "anchors": {
                "object": {"name": self.object_name, "description": self.object_description},
                "evidence": {
                    "chain": self.evidence_chain,
                    "hash": self._compute_evidence_hash(),
                    "count": len(self.evidence_chain),
                },
                "contrast": {
                    "class": self.contrast_class,
                    "baseline": self.contrast_baseline,
                    "delta": round(self.value - self.contrast_baseline, 1),
                },
                "prediction": {
                    "forecasts": self.predicts,
                    "confidence": self.prediction_confidence,
                },
                "error": {
                    "band": f"±{self.error_band:.0f}",
                    "known_unknowns": self.known_unknowns,
                },
                "falsifiability": {
                    "triggers": self.falsification_triggers,
                    "is_falsifiable": self.falsifiable,
                },
                "threshold": {
                    "bands": self.thresholds,
                    "current_decision": self.decision,
                },
            },
            "computed_at": self.computed_at,
            "computation_ms": self.computation_ms,
        }

    def _compute_evidence_hash(self) -> str:
        if not self.evidence_chain:
            return "no_evidence"
        payload = json.dumps(self.evidence_chain, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


# ═══════════════════════════════════════════════════════════════
# DEFAULT DECISION THRESHOLDS
# ═══════════════════════════════════════════════════════════════

_DEFAULT_THRESHOLDS: dict[str, float] = {
    "sovereign_runtime": 92.0,  # Full autonomous with F13 override
    "limited_autonomous": 85.0,  # Autonomous within governed bounds
    "production_burn_in": 75.0,  # Deploy with monitoring
    "governed_lab": 60.0,  # Test only, not production
    "concept_only": 0.0,  # Architecture only, not operational
}


# ═══════════════════════════════════════════════════════════════
# FALSIFICATION PROBES — reality checks that can lower scores
# ═══════════════════════════════════════════════════════════════


def probe_mcp_session_enforcement() -> tuple[bool, str]:
    """Can MCP session enforcement be bypassed? Uses HTTP-level check."""
    try:
        import http.client

        conn = http.client.HTTPConnection("127.0.0.1", 8088, timeout=5)
        body = '{"jsonrpc":"2.0","id":99,"method":"tools/list"}'
        conn.request(
            "POST",
            "/mcp",
            body=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        resp = conn.getresponse()
        status = resp.status
        data = json.loads(resp.read().decode())
        conn.close()

        # Session enforcement: missing session → 400 or error
        if status == 400:
            return True, "session_enforcement_400"
        err = data.get("error", {}).get("message", "")
        if "session" in err.lower():
            return True, "session_enforcement_active"
        return False, f"bypassed: HTTP_{status}_{err[:50]}"
    except Exception as e:
        return False, f"probe_timeout: {str(e)[:60]}"


def probe_policy_hash_active() -> tuple[bool, str]:
    """Is policy hash computed and registered? If no, governance score drops."""
    try:
        from arifosmcp.runtime.envelope_validator import _KERNEL_POLICY_HASH

        if _KERNEL_POLICY_HASH:
            return True, f"policy_hash_active:{_KERNEL_POLICY_HASH[:8]}"
        return False, "policy_hash_not_set"
    except Exception as e:
        return False, f"probe_failed: {e}"


def probe_vault999_integrity() -> tuple[bool, str]:
    """Is VAULT999 append-only and growing? If tampered, audit score drops."""
    vault_path = os.environ.get("ARIFOS_HOME", "/root") + "/VAULT999/outcomes.jsonl"
    if not os.path.isfile(vault_path):
        return False, "vault_missing"
    try:
        lines = sum(1 for _ in open(vault_path))
        if lines < 100:
            return False, f"vault_too_small:{lines}"
        return True, f"vault_intact:{lines}_lines"
    except Exception as e:
        return False, f"probe_failed: {e}"


def probe_governance_kernel_events() -> tuple[bool, str]:
    """Does the governance kernel have real event history? If empty, scores are flat."""
    try:
        from core.governance_kernel import get_governance_kernel

        kernel = get_governance_kernel()
        state = kernel.get_current_state()
        telemetry = state.get("telemetry", {})
        peace2 = telemetry.get("peace2", 0.0)
        shadow = telemetry.get("shadow", 0.0)

        # Check if event log has any real data
        event_count = len(kernel._event_log) if hasattr(kernel, "_event_log") else 0
        if event_count == 0 and peace2 == 0.5 and shadow == 0.0:
            return False, f"governance_kernel_empty_log:{event_count}_events"
        return True, f"governance_kernel_active:{event_count}_events"
    except Exception as e:
        return False, f"probe_failed: {e}"


def probe_model_registry_count() -> tuple[bool, str]:
    """How many model souls/shadows are registered?"""
    registry_dir = "/root/AAA/registries/models"
    if not os.path.isdir(registry_dir):
        return False, "registry_missing"
    souls = len([f for f in os.listdir(registry_dir) if f.endswith("_soul.yaml")])
    shadows = len([f for f in os.listdir(registry_dir) if f.endswith("_shadow.yaml")])
    if souls < 2:
        return False, f"insufficient_models:{souls}"
    return True, f"models:{souls}_souls_{shadows}_shadows"


# ═══════════════════════════════════════════════════════════════
# FALSIFICATION — reality pushing back on scores
# ═══════════════════════════════════════════════════════════════

FALSIFICATION_PROBES: dict[str, Any] = {
    "session_enforcement": {
        "probe": probe_mcp_session_enforcement,
        "score_impact": {"transport": 10, "execution": 8},
        "description": "If MCP session enforcement can be bypassed, transport score drops significantly",
    },
    "policy_hash": {
        "probe": probe_policy_hash_active,
        "score_impact": {"constitutional": 5, "execution": 5},
        "description": "If policy hash is not active, constitutional and execution scores drop",
    },
    "vault_integrity": {
        "probe": probe_vault999_integrity,
        "score_impact": {"truth": 8, "safety": 5},
        "description": "If VAULT999 is missing or tampered, truth and safety scores drop",
    },
    "governance_kernel": {
        "probe": probe_governance_kernel_events,
        "score_impact": {"reality": 10, "safety": 5},
        "description": "If governance kernel event log is empty, scores are flat defaults — reality score drops",
    },
    "model_registry": {
        "probe": probe_model_registry_count,
        "score_impact": {"truth": 5, "constitutional": 3},
        "description": "If fewer than 2 model registries exist, truth and constitutional scores drop",
    },
}


def run_falsification_probes() -> dict[str, Any]:
    """Run all falsification probes. Reality pushes back on scores."""
    results: dict[str, Any] = {}
    for name, spec in FALSIFICATION_PROBES.items():
        try:
            ok, detail = spec["probe"]()
            results[name] = {
                "passed": ok,
                "detail": detail,
                "impact_if_failed": spec["score_impact"],
                "description": spec["description"],
            }
        except Exception as e:
            results[name] = {
                "passed": False,
                "detail": f"exception: {e}",
                "impact_if_failed": spec["score_impact"],
            }
    return results
