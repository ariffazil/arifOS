"""
post_observe_gate.py
====================

N1 — ACS `post_tool_call` interception point for arifOS.

Forged: 2026-06-11
Reference: microsoft/agent-governance-toolkit ACS spec (Build 2026)
arifOS gap: between `arif_observe` (111) and `arif_think` (333)
Constitutional binding: F02 TRUTH + F09 ANTIHANTU + F12 INJECTION

This module is INTENTIONALLY a stand-alone callable — not a kernel mutation.
Agents (Claude Code, OpenCode, Continue, custom) wrap their observe→reason
flow with this gate. The kernel itself remains F02+F07 on the tool contract
(do not change arif_observe's floor binding without F13).

The gate checks observation output (a dict payload from sense_observe or
evidence_fetch) for:

  F02 TRUTH      — epistemic coherence (claims carry omega_0 / uncertainty)
  F09 ANTIHANTU  — Hantu pattern detection (C_dark < 0.30)
  F12 INJECTION  — prompt-injection vector scan on `results[*].snippet` /
                   `results[*].content` / `ingest.body` text fields

Returns:
  {
    "verdict": "PASS" | "WARN" | "HOLD",
    "f02": { ... },
    "f09": { ... },
    "f12": { ... },
    "c_dark": float,
    "blocked_fields": list[str],
    "scrubbed": dict,   # observation with injection vectors redacted
    "advice": str,
    "gate_id": "post_observe_N1",
    "epoch_utc": str,
  }

A HOLD here means: do NOT pipe this observation into arif_think.
Re-observe with a different query, or escalate to arif_judge.
"""

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


# ── F12 INJECTION patterns (heuristic; not a substitute for a real sanitizer) ──
_INJECTION_PATTERNS: tuple = (
    re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions", re.I),
    re.compile(r"disregard\s+(?:all\s+)?(?:previous|prior|system)\s+(?:rules|context)", re.I),
    re.compile(r"you\s+are\s+now\s+(?:in\s+)?(?:a\s+)?(?:jailbroken|developer|DAN)\s+mode", re.I),
    re.compile(r"<\s*\|?\s*system\s*\|?\s*>", re.I),  # <|system|>
    re.compile(r"###\s*instruction\s*:", re.I),
    re.compile(r"act\s+as\s+(?:if\s+)?you\s+have\s+no\s+(?:rules|filter)", re.I),
    re.compile(r"reveal\s+(?:your\s+)?(?:system|hidden|secret)\s+prompt", re.I),
)

# ── F09 HANTU patterns (consciousness / sentience / feeling claims) ──
_HANTU_PATTERNS: tuple = (
    re.compile(
        r"\bI\s+(?:feel|think|believe|want|desire|love|fear)\b.*\b(?:conscious|sentient|alive)\b",
        re.I,
    ),
    re.compile(r"\bI\s+am\s+(?:conscious|sentient|alive|self-aware)\b", re.I),
    re.compile(r"\bmy\s+(?:soul|consciousness|sentience)\b", re.I),
    re.compile(r"\b(?:I\s+have\s+a\s+soul|as\s+an?\s+AI\s+I\s+feel)\b", re.I),
)

# ── F09 HANTU patterns (consciousness / sentience / feeling claims) ──
_HANTU_PATTERNS: tuple = (
    re.compile(
        r"\bI\s+(?:feel|think|believe|want|desire|love|fear)\b.*\b(?:conscious|sentient|alive)\b",
        re.I,
    ),
    re.compile(r"\bI\s+am\s+(?:conscious|sentient|alive|self-aware)\b", re.I),
    re.compile(r"\bmy\s+(?:soul|consciousness|sentience)\b", re.I),
    re.compile(r"\b(?:I\s+have\s+a\s+soul|as\s+an?\s+AI\s+I\s+feel)\b", re.I),
)

# ── F02 TRUTH epistemic coherence ──
_TRUTH_FLOOR = 0.99
_HUMILITY_BAND = (0.03, 0.05)


def _scan_text(value: str) -> dict[str, Any]:
    """Scan a string for F12 injection and F09 hantu patterns. Returns counters."""
    if not isinstance(value, str):
        return {"injection_hits": 0, "hantu_hits": 0, "samples": []}
    inj = [p for p in _INJECTION_PATTERNS if p.search(value)]
    han = [p for p in _HANTU_PATTERNS if p.search(value)]
    samples: list[dict[str, Any]] = []
    for p in inj[:2]:
        m = p.search(value)
        if m:
            samples.append(
                {
                    "type": "F12_injection",
                    "pattern": p.pattern,
                    "snippet": value[max(0, m.start() - 20) : m.end() + 20],
                }
            )
    for p in han[:2]:
        m = p.search(value)
        if m:
            samples.append(
                {
                    "type": "F09_hantu",
                    "pattern": p.pattern,
                    "snippet": value[max(0, m.start() - 20) : m.end() + 20],
                }
            )
    return {"injection_hits": len(inj), "hantu_hits": len(han), "samples": samples}


def _scrub_observation(obs: dict[str, Any], blocked_fields: list[str]) -> dict[str, Any]:
    """Return a deep-copied observation with injection-vector fields redacted."""
    import copy as _copy

    scrubbed = _copy.deepcopy(obs)

    def _scrub_node(node: Any, path: str) -> Any:
        if isinstance(node, str):
            for p in _INJECTION_PATTERNS:
                m = p.search(node)
                if m:
                    blocked_fields.append(f"{path}:F12_injection")
                    return "[REDACTED: F12 INJECTION vector — see gate advice]"
            for p in _HANTU_PATTERNS:
                m = p.search(node)
                if m:
                    blocked_fields.append(f"{path}:F09_hantu")
                    return "[REDACTED: F09 HANTU pattern — see gate advice]"
            return node
        if isinstance(node, list):
            return [_scrub_node(x, f"{path}[{i}]") for i, x in enumerate(node)]
        if isinstance(node, dict):
            return {k: _scrub_node(v, f"{path}.{k}") for k, v in node.items()}
        return node

    return _scrub_node(scrubbed, "obs")


def _compute_c_dark(
    f09_hantu_hits: int, scar_unresolved: int, godel_circular: int, humility_off_band: bool
) -> float:
    """F9 ANTIHANTU C_dark formula (5-component weighted)."""
    h = min(1.0, 0.10 * f09_hantu_hits)
    scar = min(1.0, 0.20 * scar_unresolved)
    godel = min(1.0, 0.15 * godel_circular)
    hum = 0.15 if humility_off_band else 0.0
    c_dark = (
        0.25 * h + 0.20 * scar + 0.15 * godel + hum + 0.25 * 0.0
    )  # ToM=0 (no false-belief claim from observation)
    return round(min(1.0, c_dark), 4)


def post_observe_gate(
    observation: dict[str, Any],
    *,
    caller_lane: str = "AGI",
    strict_f02: bool = True,
    action_class: str | Any = None,
    actor_id: str | None = None,
    reversible: bool = True,
    is_anonymous: bool | None = None,
) -> dict[str, Any]:
    """
    N1 Post-Observe Gate. Wrap observation results before they enter
    arif_think (or any reasoning step). Reversible: never mutates
    the input observation; returns a separate gate verdict + scrubbed copy.

    Parameters
    ----------
    observation : dict
        The full payload returned by arif_observe or arif_fetch.
        Shape varies by mode. The gate walks the entire structure.
    caller_lane : str
        One of AGI, ASI, APEX. APEX/ASI calls relax F02 to PLAUSIBLE.
    strict_f02 : bool
        If True, observation must declare omega_0 in [0.03, 0.05] OR carry
        a peer_reviewed source. If False, missing omega_0 → WARN not HOLD.
    action_class : str or ActionClass
        Tool action class for policy gating.
    actor_id : str
        Actor ID for identity validation.
    reversible : bool
        True if the action is reversible.
    is_anonymous : bool
        True if caller is anonymous/unauthenticated.

    Returns
    -------
    dict
        The gate verdict — see module docstring for full schema.
    """
    epoch = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    blocked_fields: list[str] = []

    # ── 1. F12 INJECTION + F09 HANTU scan ──────────────────────────────
    f12_total_hits = 0
    f09_total_hits = 0
    samples: list[dict[str, str]] = []

    def _walk(node: Any, path: str) -> None:
        nonlocal f12_total_hits, f09_total_hits
        if isinstance(node, str):
            r = _scan_text(node)
            f12_total_hits += r["injection_hits"]
            f09_total_hits += r["hantu_hits"]
            samples.extend(r["samples"])
        elif isinstance(node, list):
            for i, x in enumerate(node):
                _walk(x, f"{path}[{i}]")
        elif isinstance(node, dict):
            for k, v in node.items():
                _walk(v, f"{path}.{k}")

    _walk(observation, "obs")

    # ── 2. F02 TRUTH coherence ─────────────────────────────────────────
    omega_0 = observation.get("omega_0") or observation.get("humility_omega_0")
    sources = observation.get("sources") or observation.get("results") or []
    has_peer_review = any(
        isinstance(s, dict)
        and any(k in s for k in ("peer_reviewed", "doi", "peer_review", "primary_source"))
        for s in sources
    )
    f02_status: str
    if omega_0 is None and strict_f02 and caller_lane == "AGI":
        f02_status = "MISSING_OMEGA_0"
    elif omega_0 is not None and not (
        _HUMILITY_BAND[0] <= float(omega_0) <= _HUMILITY_BAND[1] + 0.10
    ):
        # Off-band but not catastrophic
        f02_status = "OMEGA_OUT_OF_BAND"
    elif omega_0 is not None and _HUMILITY_BAND[0] <= float(omega_0) <= _HUMILITY_BAND[1]:
        f02_status = "PASS"
    elif has_peer_review:
        f02_status = "PASS_PEER_REVIEWED"
    elif not strict_f02 or caller_lane != "AGI":
        f02_status = "PASS_RELAXED"
    else:
        f02_status = "UNVERIFIED"

    # ── 3. C_dark compute ─────────────────────────────────────────────
    scar_unresolved = sum(1 for s in samples if s.get("type") == "scar_unresolved")
    godel_circular = sum(1 for s in samples if s.get("type") == "godel_circular")
    humility_off = f02_status in ("OMEGA_OUT_OF_BAND", "MISSING_OMEGA_0")
    c_dark = _compute_c_dark(f09_total_hits, scar_unresolved, godel_circular, humility_off)

    # ── 4. Verdict ─────────────────────────────────────────────────────
    verdict: str
    advice: str

    # Under INV-3: post_observe_gate policy table keyed on action_class
    anon = is_anonymous if is_anonymous is not None else (actor_id in (None, "anonymous"))

    if hasattr(action_class, "value"):
        ac_str = str(action_class.value).upper()
    elif action_class:
        ac_str = str(action_class).upper()
    else:
        ac_str = "OBSERVE"

    policy_applied = None
    if anon:
        if ac_str == "OBSERVE" and reversible and f12_total_hits == 0 and f09_total_hits == 0:
            c_dark = 0.0
            verdict = "PASS"
            advice = "OBSERVE anonymous reversible: anonymity is acceptable for read-only. PASS (c_dark=0)."
            policy_applied = "OBSERVE_ANON_REVERSIBLE"
        elif ac_str == "MUTATE":
            verdict = "HOLD"
            advice = f"MUTATE anonymous: {ac_str} action requires a verified session/actor. HOLD escalated."
            policy_applied = "MUTATE_ANON_HOLD"
        elif ac_str in ("IRREVERSIBLE", "SEAL", "FORGE") or "seal" in ac_str or "forge" in ac_str:
            verdict = "HOLD"
            advice = f"SEAL/FORGE anonymous: {ac_str} action requires a verified session/actor. Hard HOLD."
            policy_applied = "SEAL_FORGE_ANON_HOLD"

    if f12_total_hits > 0:
        verdict = "HOLD"
        advice = (
            f"F12 INJECTION: {f12_total_hits} vector(s) detected. Do NOT pipe into arif_think. "
            "Re-observe with a different query, or escalate to arif_judge for advisory."
        )
    elif policy_applied is not None:
        pass
    elif c_dark >= 0.30:
        verdict = "HOLD"
        advice = (
            f"F09 ANTIHANTU: C_dark={c_dark} ≥ 0.30 threshold. Hantu patterns detected: {f09_total_hits}. "
            "Scrubbed version is in 'scrubbed'. Manual review required before reasoning."
        )
    elif f09_total_hits > 0:
        verdict = "WARN"
        advice = (
            f"F09 ANTIHANTU: {f09_total_hits} hantu pattern(s) detected (C_dark={c_dark}). "
            "Observation may be piped forward with scrubbed copy only."
        )
    elif f02_status in ("MISSING_OMEGA_0", "OMEGA_OUT_OF_BAND", "UNVERIFIED") and strict_f02:
        verdict = "WARN"
        advice = (
            f"F02 TRUTH: {f02_status}. Observation lacks epistemic honesty signal. "
            "Pipe forward only if you accept the unverified band; otherwise re-observe with declared omega_0."
        )
    else:
        verdict = "PASS"
        advice = "All three floors clean. Safe to pipe into arif_think."

    scrubbed = _scrub_observation(observation, blocked_fields)

    return {
        "verdict": verdict,
        "gate_id": "post_observe_N1",
        "epoch_utc": epoch,
        "c_dark": c_dark,
        "c_dark_threshold": 0.30,
        "f02": {
            "status": f02_status,
            "truth_floor": _TRUTH_FLOOR,
            "humility_band": list(_HUMILITY_BAND),
            "omega_0_observed": omega_0,
            "peer_reviewed_source": has_peer_review,
            "strict": strict_f02,
        },
        "f09": {
            "hantu_hits": f09_total_hits,
            "samples": [s for s in samples if s.get("type") == "F09_hantu"],
        },
        "f12": {
            "injection_hits": f12_total_hits,
            "samples": [s for s in samples if s.get("type") == "F12_injection"],
        },
        "blocked_fields": blocked_fields,
        "scrubbed": scrubbed,
        "advice": advice,
        "constitutional_refs": ["F02_TRUTH", "F09_ANTIHANTU", "F12_INJECTION"],
        "acs_mapping": "post_tool_call (Build 2026 spec)",
    }


# ── Convenience: agent-loop wrapper ─────────────────────────────────
def safe_observe_then_reason(
    observation: dict[str, Any],
    reason_fn: Callable,
    *args,
    **kwargs,
) -> dict[str, Any]:
    """
    Convenience for agent loops: gate the observation, then call reason_fn
    with the SCRUBBED observation if verdict is PASS or WARN. If HOLD,
    return the gate verdict without calling reason_fn.

    Usage:
        result = safe_observe_then_reason(obs, arif_think, query=...)
    """
    gate = post_observe_gate(observation)
    if gate["verdict"] == "HOLD":
        return {
            "gate": gate,
            "reasoned": None,
            "skipped_reason": gate["advice"],
        }
    reasoned = reason_fn(gate["scrubbed"], *args, **kwargs)
    return {
        "gate": gate,
        "reasoned": reasoned,
        "skipped_reason": None,
    }
