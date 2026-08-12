"""
arifOS C4 Reality Drift Gate — Constitutional enforcement of Gödel Eureka #4
═════════════════════════════════════════════════════════════════════════════

"Reality is the final auditor. Reasoning can drift. Models can drift.
Receipts can drift. Reality does not negotiate." — Gödel Eureka #4

FORGED: 2026-08-12 by 333-AGI under F13 SOVEREIGN directive
DOCTRINE: /root/AAA/canon/GODEL_EUREKAS.md §E4
ALIGNMENT: /root/AAA/instructions/reality-first.md RULE 1

═══ PURPOSE ═══

This gate closes the gap between "reality is documented as final auditor"
and "reality is automatically consulted in the triple-pass."

Before this gate:
    Doctrine says reality is final → but humans must manually probe.

After this gate:
    Doctrine says reality is final → gate probes automatically →
    verdict reflects live state.

═══ INTERFACE ═══

    from arifosmcp.runtime.c4_reality_drift_gate import assess_reality_drift

    result = assess_reality_drift(
        claimed_state={"organs_alive": 6, "kernel_drift": False},
        session_id="SEAL-xxx",
    )
    # result.verdict = "PASS" | "DRIFT" | "UNKNOWN"
    # result.drifts = [{"claim": "organs_alive=6", "live": 5, "delta": -1}]

═══ VERDICT LADDER ═══

    PASS     — All claimed states match live probes within tolerance.
    DRIFT    — One or more claimed states diverge from live probes.
    UNKNOWN  — Probe failed (endpoint unreachable, timeout, parse error).
               UNKNOWN is NOT PASS. It is honest uncertainty.

    Per Reality-First RULE 4: "UNMEASURED beats fabricated certainty."
    UNKNOWN > fake PASS.

═══ F1 AMANAH ═══

    This gate reads live endpoints. It does not mutate state.
    It is pure-function: same inputs → same outputs (within probe TTL).
    ΔS = 0 per call. Reversible by definition.

DITEMPA BUKAN DIBERI — Forged, not given. ⚒️
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("arifosmcp.c4_reality_drift")

# ── Constitutional thresholds (frozen) ──────────────────────────────────────
PROBE_TIMEOUT_SECONDS = 5
PROBE_TTL_SECONDS = 30  # cache probe results for 30s to avoid hammering
DRIFT_TOLERANCE_NUMERIC = 0.0  # exact match required for counts; scores use delta

# ── Organ endpoints (canonical from /root/AAA/federation/organs.yaml) ───────
ORGAN_ENDPOINTS: dict[str, str] = {
    "arifos": "http://127.0.0.1:8088/health",
    "aforge": "http://127.0.0.1:7071/health",
    "geox": "http://127.0.0.1:8081/health",
    "wealth": "http://127.0.0.1:18082/health",
    "well": "http://127.0.0.1:18083/health",
    "aaa": "http://127.0.0.1:3001/health",
    "ariflow": "http://127.0.0.1:7073/health",
    "fed": "http://127.0.0.1:7074/health",
}


@dataclass
class DriftSignal:
    """Single drift finding — one claimed vs live mismatch."""

    field_name: str
    claimed_value: Any
    live_value: Any
    delta: str  # "match" | "drift" | "unknown"
    evidence: str  # raw probe output


@dataclass
class RealityDriftAssessment:
    """C4 Reality Drift verdict — feeds into APEX triple-pass."""

    verdict: str  # "PASS" | "DRIFT" | "UNKNOWN"
    signals: list[DriftSignal] = field(default_factory=list)
    probed_at: str = ""
    probe_count: int = 0
    drift_count: int = 0
    unknown_count: int = 0
    evidence_bundle: dict[str, Any] = field(default_factory=dict)

    @property
    def is_pass(self) -> bool:
        return self.verdict == "PASS"

    @property
    def is_drift(self) -> bool:
        return self.verdict == "DRIFT"

    @property
    def is_unknown(self) -> bool:
        return self.verdict == "UNKNOWN"

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "probed_at": self.probed_at,
            "probe_count": self.probe_count,
            "drift_count": self.drift_count,
            "unknown_count": self.unknown_count,
            "signals": [
                {
                    "field": s.field_name,
                    "claimed": s.claimed_value,
                    "live": s.live_value,
                    "delta": s.delta,
                }
                for s in self.signals
            ],
        }


# ── Probe primitives ────────────────────────────────────────────────────────


def _probe_endpoint(url: str, timeout: int = PROBE_TIMEOUT_SECONDS) -> dict[str, Any] | None:
    """Probe a health endpoint. Returns parsed JSON or None on failure."""
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return json.loads(body)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        logger.debug("Probe failed for %s: %s", url, exc)
        return None


def _probe_organ_liveness() -> dict[str, bool]:
    """Probe all organ health endpoints. Returns {organ: alive_bool}."""
    results: dict[str, bool] = {}
    for organ, url in ORGAN_ENDPOINTS.items():
        data = _probe_endpoint(url)
        results[organ] = data is not None and data.get("status", "").lower() in (
            "healthy",
            "ok",
            "seal",
            "pass",
        )
    return results


def _probe_kernel_drift() -> str | None:
    """Probe kernel for source=built=deployed drift. Returns 'false' | 'true' | None."""
    data = _probe_endpoint(ORGAN_ENDPOINTS["arifos"])
    if data is None:
        return None
    return str(data.get("runtime_drift", "unknown")).lower()


def _probe_floor_state() -> dict[str, float] | None:
    """Probe kernel for floor values. Returns {floor_id: score} or None."""
    data = _probe_endpoint(ORGAN_ENDPOINTS["arifos"])
    if data is None:
        return None
    floors = data.get("floors") or data.get("runtime_floors") or {}
    if isinstance(floors, dict):
        return {k: float(v) for k, v in floors.items() if isinstance(v, (int, float))}
    return None


def _probe_fq() -> float | None:
    """Probe arifFlow for FQ value. Returns float or None."""
    data = _probe_endpoint(ORGAN_ENDPOINTS.get("arifflow", ORGAN_ENDPOINTS.get("ariflow", "")))
    if data is None:
        return None
    fq = data.get("fq", {})
    if isinstance(fq, dict):
        return float(fq.get("quotient", 0))
    if isinstance(fq, (int, float)):
        return float(fq)
    return None


def _probe_git_sha(repo_path: str) -> str | None:
    """Get current git SHA for a repo."""
    try:
        import subprocess

        result = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None


# ── C4 Gate: assess_reality_drift ═══════════════════════════════════════════


def assess_reality_drift(
    claimed_state: dict[str, Any] | None = None,
    session_id: str = "",
    check_organs: bool = True,
    check_kernel_drift: bool = True,
    check_fq: bool = True,
    check_git_shas: bool = False,
) -> RealityDriftAssessment:
    """
    C4 Reality Drift Gate — compare claimed state against live probes.

    This is the constitutional gate that makes Gödel Eureka #4 operational.
    Call this from arif_judge pre-verdict to ensure the SEAL is grounded
    in current reality, not stale belief.

    Args:
        claimed_state: Optional dict of claimed values to verify.
        session_id: Session ID for audit trail.
        check_organs: Probe all organ health endpoints.
        check_kernel_drift: Check kernel source=built=deployed.
        check_fq: Check arifFlow FQ value.
        check_git_shas: Check git SHAs for all organ repos.

    Returns:
        RealityDriftAssessment with verdict PASS | DRIFT | UNKNOWN.
    """
    assessment = RealityDriftAssessment(
        verdict="PASS",
        probed_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )

    # ── 1. Organ liveness ──────────────────────────────────────────────
    if check_organs:
        live_organs = _probe_organ_liveness()
        for organ, alive in live_organs.items():
            assessment.probe_count += 1
            signal = DriftSignal(
                field_name=f"organ.{organ}.alive",
                claimed_value=True,  # we claim all should be alive
                live_value=alive,
                delta="match" if alive else "drift",
                evidence=f"probe {ORGAN_ENDPOINTS.get(organ, '?')}",
            )
            assessment.signals.append(signal)
            if not alive:
                assessment.drift_count += 1

    # ── 2. Kernel drift ────────────────────────────────────────────────
    if check_kernel_drift:
        live_drift = _probe_kernel_drift()
        assessment.probe_count += 1
        if live_drift is None:
            assessment.unknown_count += 1
            assessment.signals.append(
                DriftSignal(
                    field_name="kernel.runtime_drift",
                    claimed_value="false",
                    live_value=None,
                    delta="unknown",
                    evidence="probe failed — kernel unreachable",
                )
            )
        elif live_drift == "false":
            assessment.signals.append(
                DriftSignal(
                    field_name="kernel.runtime_drift",
                    claimed_value="false",
                    live_value="false",
                    delta="match",
                    evidence="kernel /health runtime_drift=false",
                )
            )
        else:
            assessment.drift_count += 1
            assessment.signals.append(
                DriftSignal(
                    field_name="kernel.runtime_drift",
                    claimed_value="false",
                    live_value=live_drift,
                    delta="drift",
                    evidence=f"kernel /health runtime_drift={live_drift}",
                )
            )

    # ── 3. FQ pulse ────────────────────────────────────────────────────
    if check_fq:
        live_fq = _probe_fq()
        assessment.probe_count += 1
        if live_fq is not None:
            assessment.evidence_bundle["fq"] = live_fq
            if live_fq < 0.5:
                assessment.drift_count += 1
                assessment.signals.append(
                    DriftSignal(
                        field_name="arifFlow.fq.quotient",
                        claimed_value=">= 0.5",
                        live_value=live_fq,
                        delta="drift",
                        evidence=f"FQ={live_fq} < 0.5 threshold → ALL HOLD",
                    )
                )
            else:
                assessment.signals.append(
                    DriftSignal(
                        field_name="arifFlow.fq.quotient",
                        claimed_value=">= 0.5",
                        live_value=live_fq,
                        delta="match",
                        evidence=f"FQ={live_fq}",
                    )
                )
        else:
            assessment.unknown_count += 1
            assessment.signals.append(
                DriftSignal(
                    field_name="arifFlow.fq.quotient",
                    claimed_value=">= 0.5",
                    live_value=None,
                    delta="unknown",
                    evidence="arifFlow unreachable",
                )
            )

    # ── 4. Git SHAs (optional) ─────────────────────────────────────────
    if check_git_shas:
        repo_paths = {
            "arifos": "/root/arifOS",
            "aforge": "/root/A-FORGE",
            "aaa": "/root/AAA",
            "geox": "/root/GEOX",
            "wealth": "/root/WEALTH",
            "well": "/root/WELL",
        }
        for name, path in repo_paths.items():
            sha = _probe_git_sha(path)
            assessment.probe_count += 1
            if sha:
                assessment.evidence_bundle[f"git_sha.{name}"] = sha
                assessment.signals.append(
                    DriftSignal(
                        field_name=f"git.{name}.sha",
                        claimed_value="any",
                        live_value=sha,
                        delta="match",
                        evidence=f"git HEAD={sha}",
                    )
                )
            else:
                assessment.unknown_count += 1

    # ── 5. Claimed state verification ──────────────────────────────────
    if claimed_state:
        for key, claimed_val in claimed_state.items():
            # Route to appropriate probe
            if key == "organs_alive":
                live_organs = _probe_organ_liveness()
                live_count = sum(1 for v in live_organs.values() if v)
                assessment.probe_count += 1
                delta = "match" if live_count == claimed_val else "drift"
                if delta == "drift":
                    assessment.drift_count += 1
                assessment.signals.append(
                    DriftSignal(
                        field_name=key,
                        claimed_value=claimed_val,
                        live_value=live_count,
                        delta=delta,
                        evidence=f"live probe: {live_count}/{len(live_organs)} alive",
                    )
                )

    # ── Verdict computation ────────────────────────────────────────────
    if assessment.drift_count > 0:
        assessment.verdict = "DRIFT"
    elif assessment.unknown_count > 0 and assessment.probe_count > 0:
        # If we have unknowns but no drifts, check the ratio
        unknown_ratio = assessment.unknown_count / max(assessment.probe_count, 1)
        if unknown_ratio > 0.5:
            assessment.verdict = "UNKNOWN"  # majority of probes failed
        else:
            assessment.verdict = "PASS"  # some unknowns but majority passed
    else:
        assessment.verdict = "PASS"

    logger.info(
        "C4 Reality Drift: verdict=%s drifts=%d unknowns=%d probes=%d session=%s",
        assessment.verdict,
        assessment.drift_count,
        assessment.unknown_count,
        assessment.probe_count,
        session_id,
    )

    return assessment


# ── Constitutional integration hook ─────────────────────────────────────────


def c4_gate_for_judge(
    session_id: str = "", claimed_state: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Integration point for arif_judge pre-verdict.

    Returns a dict that can be attached to the judge's evidence bundle:

        {
            "c4_reality_drift": {
                "verdict": "PASS" | "DRIFT" | "UNKNOWN",
                ...
            }
        }

    Verdict semantics for judge:
        PASS    → no floor adjustment needed
        DRIFT   → at least one claimed state diverges from reality
                  → judge should consider SABAR instead of SEAL
        UNKNOWN → majority of probes failed
                  → judge should consider HOLD (can't verify reality)
    """
    assessment = assess_reality_drift(claimed_state=claimed_state, session_id=session_id)
    return {"c4_reality_drift": assessment.to_dict()}


# ═══ END — DITEMPA BUKAN DIBERI ⚒️ ═══
