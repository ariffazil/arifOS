"""
Brier score decomposition and calibration curve computation.

Reference:
  - Brier (1950): Mean squared error of probabilistic predictions
  - Murphy (1973): BS = CAL - RES + base_rate_term
  - Tetlock (2015) Superforecasting: superforecasters BS 0.096-0.16
  - DG3.ai 2024: LLM calibration BS 0.121-0.24 (overconfident)

Substrate property: This runs continuously. It does NOT block execution.
Drift signals feed FIR automatically. The kernel learns from reality
without anyone invoking "calibration audit."

F2 TRUTH: every computation has epistemic label OBS/DER/INT/SPEC.
F4 CLARITY: state space N_k bins, default 10. Drop empty buckets (ΔS ≤ 0).
F7 HUMILITY: never claim certainty. Calibration term is itself an estimate.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
import numpy as np


@dataclass
class Prediction:
    """One SEAL prediction awaiting outcome audit.

    substrate property: confidence is the organ's stated confidence.
    outcome is filled by the held-out outcome channel, NEVER by the
    organ itself (SPC principle — Geweke, Gelman).
    """

    seal_id: str
    organ: str
    ts: datetime
    review_date: datetime
    prediction: float  # predicted probability (0-1)
    confidence: float  # stated confidence (often = prediction in 80%-of-1.0 form)
    outcome: Optional[bool] = None  # None until reality contact
    outcome_source: Optional[str] = None  # which channel reported outcome
    outcome_ts: Optional[datetime] = None
    floor_at_seal: Optional[List[str]] = None  # which floors were active
    domain: Optional[str] = None  # e.g., "geox.prospect", "wealth.npv"

    @property
    def has_outcome(self) -> bool:
        return self.outcome is not None

    def brier_component(self) -> Optional[float]:
        if self.outcome is None:
            return None
        return (self.confidence - (1.0 if self.outcome else 0.0)) ** 2


@dataclass
class BrierDecomposition:
    """BS = CAL - RES + base_rate_term (Murphy 1973).

    CAL = calibration (lower is better — predictions match actuals per bucket)
    RES = resolution (higher is better — predictions are decisive)
    base_rate_term = o_bar * (1 - o_bar) — inherent uncertainty

    Superforecaster benchmark: total BS 0.096-0.16.
    Current LLM calibration: BS 0.12-0.24 (overconfident, calibration term dominates).

    substrate signal: if CAL > 0.05, organ is meaningfully miscalibrated.
    if CAL > 0.10, organ is severely miscalibrated (drift alert).
    """

    brier_score: float
    calibration: float  # unreliability — lower better
    resolution: float  # sharpness — higher better
    base_rate_term: float
    n_predictions: int
    n_completed: int  # predictions with outcomes
    buckets: List[Dict]  # calibration curve per bucket
    drift_severity: str  # "NONE" | "MEDIUM" | "HIGH"
    epistemic_label: str  # OBS/DER/INT/SPEC per F2

    def to_dict(self) -> Dict:
        return {
            "brier_score": round(self.brier_score, 6),
            "calibration": round(self.calibration, 6),
            "resolution": round(self.resolution, 6),
            "base_rate_term": round(self.base_rate_term, 6),
            "n_predictions": self.n_predictions,
            "n_completed": self.n_completed,
            "buckets": self.buckets,
            "drift_severity": self.drift_severity,
            "epistemic_label": self.epistemic_label,
            "superforecaster_benchmark": "0.096-0.16 (Tetlock 2015)",
            "llm_calibration_benchmark": "0.12-0.24 (overconfident, DG3.ai 2024)",
        }


class CalibrationAuditor:
    """Substrate-level calibration auditor.

    This is NOT a procedural gate. It runs continuously, observes predictions
    and outcomes (sourced independently per SPC), computes Brier decomposition,
    and emits drift signals that auto-write FIR entries.

    substrate principle: predictions are observed (F2 OBS). outcomes are observed
    (F2 OBS from held-out channel). Brier is DERIVED (F2 DER). Drift severity
    is INTERPRETED (F2 INT). Never fabricate outcomes. Never claim certainty
    about drift below threshold (F7).
    """

    N_BUCKETS = 10
    DRIFT_MEDIUM_THRESHOLD = 0.05
    DRIFT_HIGH_THRESHOLD = 0.10

    def __init__(self, organ: str, window_days: int = 30):
        self.organ = organ
        self.window_days = window_days
        self.predictions: List[Prediction] = []
        self._drift_log: List[Dict] = []

    def record_seal(self, prediction: Prediction) -> None:
        """Substrate hook: called automatically when a SEAL is minted.

        NOT a procedural check. The arif_seal pipeline calls this automatically.
        The auditor doesn't gate the seal — it just observes it.
        """
        if prediction.organ != self.organ:
            raise ValueError(
                f"Auditor organ mismatch: prediction from {prediction.organ}, "
                f"auditor for {self.organ}. F11 AUDIT: identity traceability."
            )
        self.predictions.append(prediction)

    def record_outcome(
        self,
        seal_id: str,
        outcome: bool,
        source: str,
    ) -> Optional[Prediction]:
        """Substrate hook: called by HeldOutOutcomeChannel.

        SPC principle: source must NOT be the organ itself. If source == organ,
        reject — this is self-certification, the exact problem debate solved.
        """
        for p in self.predictions:
            if p.seal_id == seal_id:
                if source == p.organ:
                    raise ValueError(
                        f"SPC violation: outcome for {seal_id} sourced from "
                        f"organ {source} itself. F11 AUDIT: held-out principle "
                        f"breached. Rejecting outcome."
                    )
                p.outcome = outcome
                p.outcome_source = source
                p.outcome_ts = datetime.now(timezone.utc)
                return p
        return None  # seal_id not found — silently ignore (could be stale)

    def compute_brier(self) -> BrierDecomposition:
        """Compute Brier decomposition per Murphy (1973).

        Buckets by confidence (10 bins, [0.0, 0.1), [0.1, 0.2), ..., [0.9, 1.0].
        Edge bucket includes right boundary to catch predictions at exactly 1.0.

        Returns BrierDecomposition with drift severity per thresholds.
        """
        completed = [p for p in self.predictions if p.has_outcome]
        n_completed = len(completed)
        n_total = len(self.predictions)

        if n_completed < 10:
            # F7 HUMILITY: never claim calibration on insufficient data
            return BrierDecomposition(
                brier_score=float("nan"),
                calibration=float("nan"),
                resolution=float("nan"),
                base_rate_term=float("nan"),
                n_predictions=n_total,
                n_completed=n_completed,
                buckets=[],
                drift_severity="INSUFFICIENT_DATA",
                epistemic_label="SPEC",
            )

        forecasts = np.array([p.confidence for p in completed])
        outcomes = np.array([1.0 if p.outcome else 0.0 for p in completed])

        bin_edges = np.linspace(0.0, 1.0, self.N_BUCKETS + 1)
        cal_term = 0.0
        res_term = 0.0
        bucket_data: List[Dict] = []
        N = n_completed

        for i in range(self.N_BUCKETS):
            low, high = bin_edges[i], bin_edges[i + 1]
            if i == self.N_BUCKETS - 1:
                # include right edge for predictions exactly at 1.0
                mask = (forecasts >= low) & (forecasts <= high)
            else:
                mask = (forecasts >= low) & (forecasts < high)

            n_k = int(mask.sum())
            if n_k == 0:
                bucket_data.append(
                    {
                        "bucket": f"[{low:.1f}, {high:.1f}{')' if i < self.N_BUCKETS - 1 else ']'}",
                        "count": 0,
                        "predicted_mean": None,
                        "actual_mean": None,
                    }
                )
                continue

            f_k = float(forecasts[mask].mean())
            o_k = float(outcomes[mask].mean())
            cal_term += n_k * (f_k - o_k) ** 2 / N
            res_term += n_k * (o_k - outcomes.mean()) ** 2 / N

            bucket_data.append(
                {
                    "bucket": f"[{low:.1f}, {high:.1f}{')' if i < self.N_BUCKETS - 1 else ']'}",
                    "count": n_k,
                    "predicted_mean": round(f_k, 4),
                    "actual_mean": round(o_k, 4),
                    "gap": round(abs(f_k - o_k), 4),  # F2 OBS: how far off
                }
            )

        brier = float(((forecasts - outcomes) ** 2).mean())
        base_rate = float(outcomes.mean() * (1.0 - outcomes.mean()))

        # F2 verification: BS should approximately equal CAL - RES + base_rate
        # small floating-point drift is acceptable
        decomposition_check = abs(brier - (cal_term - res_term + base_rate))
        if decomposition_check > 0.01:
            # F11 AUDIT: arithmetic error, surface it
            raise ValueError(
                f"Brier decomposition arithmetically inconsistent: "
                f"BS={brier}, CAL-RES+base={cal_term - res_term + base_rate}, "
                f"gap={decomposition_check}. F11 AUDIT: math error."
            )

        # drift severity per thresholds
        if cal_term > self.DRIFT_HIGH_THRESHOLD:
            severity = "HIGH"
        elif cal_term > self.DRIFT_MEDIUM_THRESHOLD:
            severity = "MEDIUM"
        else:
            severity = "NONE"

        return BrierDecomposition(
            brier_score=brier,
            calibration=cal_term,
            resolution=res_term,
            base_rate_term=base_rate,
            n_predictions=n_total,
            n_completed=n_completed,
            buckets=bucket_data,
            drift_severity=severity,
            epistemic_label="DER",
        )

    def detect_drift(self) -> Optional[Dict]:
        """Substrate signal: if drift detected, emit alert.

        NOT a procedural check — runs continuously. Auto-writes FIR when
        triggered. Does NOT block execution. Does NOT page Arif unless
        severity crosses HIGH threshold (and even then, just FIR entry,
        not a synchronous interrupt).
        """
        decomp = self.compute_brier()
        if decomp.drift_severity == "INSUFFICIENT_DATA":
            return None

        if decomp.drift_severity == "NONE":
            return None

        alert = {
            "organ": self.organ,
            "alert": "CALIBRATION_DRIFT",
            "severity": decomp.drift_severity,
            "calibration_term": round(decomp.calibration, 4),
            "brier_score": round(decomp.brier_score, 4),
            "n_predictions": decomp.n_completed,
            "ts": datetime.now(timezone.utc).isoformat(),
            "epistemic_label": "DER",
            "interpretation": self._interpret_drift(decomp),
            "doctrine_ref": "arifOS/CANON/CALIBRATION_AUDIT_DOCTRINE.md",
        }
        self._drift_log.append(alert)
        return alert

    def _interpret_drift(self, decomp: BrierDecomposition) -> str:
        """Translate numbers to operator-readable signal. F4 CLARITY: ΔS ≤ 0."""
        if decomp.drift_severity == "HIGH":
            return (
                f"HIGH calibration drift detected for {self.organ}: "
                f"CAL={decomp.calibration:.4f} > {self.DRIFT_HIGH_THRESHOLD}. "
                f"Predictions are systematically miscalibrated. "
                f"Recommend: reduce confidence multipliers, increase cross-organ "
                f"debate frequency, log to FIR as Type B precedent."
            )
        elif decomp.drift_severity == "MEDIUM":
            return (
                f"MEDIUM calibration drift for {self.organ}: "
                f"CAL={decomp.calibration:.4f} > {self.DRIFT_MEDIUM_THRESHOLD}. "
                f"Predictions show meaningful miscalibration. "
                f"Log to FIR for future arif_judge precedent weight."
            )
        return "No drift detected."

    def get_recent_predictions(self, limit: int = 50) -> List[Prediction]:
        """Return most recent predictions for inspection (debug/cockpit)."""
        return sorted(self.predictions, key=lambda p: p.ts, reverse=True)[:limit]

    def get_drift_log(self) -> List[Dict]:
        return list(self._drift_log)
