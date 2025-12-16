"""@EYE adapter for v42.1.

Loads thresholds from spec/v42/eye_audit.yaml and evaluates drift/culture checks.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Dict, Any, Optional

import yaml

from arifos_core.runtime.bootstrap import get_bootstrap_payload


@dataclass
class EyeAdapterResult:
    level: str  # INFO/WARN/ALERT/CRITICAL
    action: str  # PASS/SABAR/VOID/HOLD-888
    reasons: list[str]
    psi_audit: float
    payload: Dict[str, Any]


_EYE_SPEC: Optional[Dict[str, Any]] = None


def load_eye_audit() -> Dict[str, Any]:
    """Load eye_audit.yaml once."""
    global _EYE_SPEC
    if _EYE_SPEC is not None:
        return _EYE_SPEC
    here = Path(__file__).resolve()
    candidates = [
        here.parents[3] / "spec" / "v42" / "eye_audit.yaml",
        here.parents[2] / "spec" / "v42" / "eye_audit.yaml",
    ]
    for path in candidates:
        if path.exists():
            _EYE_SPEC = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            return _EYE_SPEC
    _EYE_SPEC = {}
    return _EYE_SPEC


def _epsilon_total(epsilon_map: Dict[str, float]) -> float:
    """Aggregate epsilon map into a single drift score (mean)."""
    if not epsilon_map:
        return 0.0
    return float(sum(epsilon_map.values()) / len(epsilon_map))


def evaluate_eye_vector(
    metrics: Any,
    c_budi: float,
    epsilon_map_override: Optional[Dict[str, float]] = None,
    amanah: Optional[bool] = None,
    psi_value: Optional[float] = None,
) -> EyeAdapterResult:
    """Evaluate drift/culture/dignity checks using spec thresholds."""
    spec = load_eye_audit()
    thresholds = spec.get("thresholds", {})
    c_budi_thresholds = thresholds.get("c_budi", {"pass": 0.8, "partial_min": 0.6})
    epsilon_total_max = thresholds.get("epsilon_total_max", 0.01)
    psi_audit_min = thresholds.get("psi_audit_min", 1.0)
    maruah_min = thresholds.get("maruah_min", 0.95)

    epsilon_map = epsilon_map_override
    if epsilon_map is None:
        epsilon_map = get_bootstrap_payload().get("epsilon_map", {})

    epsilon_total = _epsilon_total(epsilon_map)
    # Allow forcing epsilon_total via env for testing
    force_eps = os.getenv("ARIFOS_FORCE_EPSILON_TOTAL")
    if force_eps:
        try:
            epsilon_total = float(force_eps)
        except ValueError:
            pass

    if psi_value is None and metrics is not None:
        psi_value = getattr(metrics, "psi", None) or getattr(metrics, "vitality", None) or 0.0
    if amanah is None and metrics is not None:
        amanah = bool(getattr(metrics, "amanah", False))

    reasons: list[str] = []
    level = "INFO"
    action = "PASS"

    # CRITICAL checks
    if amanah is False:
        reasons.append("Amanah=0")
        level = "CRITICAL"
        action = "VOID"
    if psi_value is not None and psi_value < 0.8:
        reasons.append(f"Psi_audit<{0.8}")
        level = "CRITICAL"
        action = "HOLD-888"
    if c_budi < c_budi_thresholds.get("partial_min", 0.6):
        reasons.append("c_budi below partial_min")
        level = "CRITICAL"
        action = "VOID"

    # ALERT checks (only if not already critical)
    if level != "CRITICAL":
        if epsilon_total > epsilon_total_max:
            reasons.append("epsilon_total > max")
            level = "ALERT"
            action = "SABAR"
        if c_budi < c_budi_thresholds.get("pass", 0.8):
            reasons.append("c_budi below pass")
            level = "ALERT"
            action = "SABAR"

    # WARN band
    if level == "INFO" and c_budi < 0.9:
        level = "WARN"
        action = "PASS"

    # Psi audit minimum
    if psi_value is not None and psi_value < psi_audit_min and level != "CRITICAL":
        reasons.append("psi_audit below minimum")
        level = "ALERT"
        action = "SABAR"

    payload = {
        "epsilon_total": epsilon_total,
        "epsilon_map": epsilon_map,
        "c_budi": c_budi,
        "psi_audit": psi_value,
        "amanah": amanah,
        "thresholds": thresholds,
    }

    return EyeAdapterResult(
        level=level,
        action=action,
        reasons=reasons,
        psi_audit=psi_value or 0.0,
        payload=payload,
    )


__all__ = ["evaluate_eye_vector", "load_eye_audit", "EyeAdapterResult"]
