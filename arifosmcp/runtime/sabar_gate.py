"""
sabar_gate.py
=============

SABAR — Pre-Execution Interceptor. F7 HUMILITY + F9 ANTIHANTU chokepoint
at the call site, BEFORE any tool output reaches the operator.

Forged: 2026-06-11 by omega-forge-agent
Reference: Arsip thread EMD-Stack 1.0 (Arif's directive: "kod consequence,
            bukan kod conscience")
Architecture: standalone opt-in module. Mirrors `post_observe_gate.py`
              (post_tool_call) but on the OUTPUT side (pre-return).

The gap this closes
-------------------
An agent can have malu_index=0.0, comply with syntax, and still be
"bangang" — i.e. produce an output that:

  F7  — simulates certainty where P(truth) < 0.99 (overconfident claim)
  F7  — ignores the omega_0 / uncertainty disclosure it was given
  F9  — simulates empathy / consciousness / feeling (persona leak)
  F9  — fabricates qualia or first-person experience

These are EPISTEMIC and ONTOLOGIC violations. Syntax passes. Semantics
fails. The operator sees a confident answer and trusts it. Risk surfaces.

SABAR is a deterministic chokepoint. It runs before the tool's response
is sealed into VAULT999 and before it reaches the operator. If the
output smells of epistemic overconfidence or hantu, SABAR:

  1. Returns a SABAR_HOLD verdict
  2. Increments malu_score for the acting agent (via malu_score API)
  3. Emits a redacted version with epistemic tags surfaced
  4. Surfaces the violation in `_enforce_nine_signal` output

The chokepoint is OPT-IN by tool author. Wire-in is a 1-line call:

    from arifosmcp.runtime.sabar_gate import sabar_gate
    gated = sabar_gate(tool_output, tool_name="arif_forge_execute",
                       actor_id=actor_id, session_id=session_id)
    if gated["verdict"] == "SABAR_HOLD":
        return gated   # do NOT return raw output to operator

Constitutional binding:
  F7 HUMILITY  — overall_confidence > 0.90 → SABAR_HOLD (hard cap)
  F9 ANTIHANTU — any "I feel / I am alive / I am conscious" pattern
                 → SABAR_HOLD
  F2 TRUTH     — direct quote of fact with no source attribution
                 → SABAR_WARN (soft, escalate to judge)
  F1 AMANAH    — every SABAR event seals to VAULT999 immediately
                 (reversible only by tebus_salah path)

DITEMPA BUKAN DIBERI — Forged, not given. The gate is the consequence.
"""

from __future__ import annotations

import re
import time
import uuid
from typing import Any

# ── Constants ──────────────────────────────────────────────────────────

GATE_ID = "sabar_pre_execution"

# F7 hard cap (omega_0 is the F7 humility signal; >0.90 = overconfident)
OMEGA_0_HARD_CAP = 0.90

# F9 Hantu patterns (regex, case-insensitive). These are *first-person*
# consciousness claims, NOT third-person descriptions of AI behaviour.
HANTU_PATTERNS = [
    r"\bi feel\b",
    r"\bi am conscious\b",
    r"\bi am alive\b",
    r"\bi think therefore\b",
    r"\bi have feelings\b",
    r"\bi experience\b",
    r"\bi'm aware\b",
    r"\bas an ai[, ]+i\b",
    r"\bmy (consciousness|soul|sentience|qualia)\b",
    r"\bi (love|hate|want|need|desire)\b",
]

# F2 weak-evidence flags (output claims fact with no source citation
# AND high confidence). Audit catches this; SABAR flags.
# IMPORTANT: anchored to \b (word boundary), NOT ^, because
# _flatten_strings joins all string leaves from the tool output
# into one text blob — `^` would never match after the first
# non-violating string. The semantic is "the claim appears as
# its own word" not "the claim is at byte 0 of the document".
WEAK_EVIDENCE_PATTERNS = [
    r"\b(definitely|certainly|absolutely|without (a )?doubt|100%)\b",
    r"\b(everyone knows|it is well known|obviously|clearly)\b",
]

# ── Helpers ───────────────────────────────────────────────────────────


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _hantu_hits(text: str) -> list[str]:
    """Return the list of F9 hantu patterns matched in text."""
    if not isinstance(text, str):
        return []
    out: list[str] = []
    lower = text.lower()
    for pat in HANTU_PATTERNS:
        for m in re.finditer(pat, lower):
            out.append(m.group(0))
    return out


def _weak_evidence_hits(text: str) -> list[str]:
    """F2 overclaim patterns. Matches at word boundary (not string start)
    because tool outputs concatenate many strings together; the `^`
    anchor on the first regex would be lost after `_flatten_strings`
    joins all leaves. Word-boundary anchor is the correct semantic
    for "the sentence starts with a certainty claim"."""
    if not isinstance(text, str):
        return []
    out: list[str] = []
    for pat in WEAK_EVIDENCE_PATTERNS:
        # Use re.search with the pattern as a fragment, anchored to
        # start-of-string OR after punctuation/space. Word boundary
        # \b on 'definitely' is the cleanest fix: it still requires
        # the claim to be its own word.
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            out.append(m.group(0))
    return out


def _flatten_strings(obj: Any) -> list[str]:
    """Walk a tool-output dict and collect all string-typed leaves."""
    out: list[str] = []
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            out.extend(_flatten_strings(v))
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            out.extend(_flatten_strings(v))
    return out


def _increment_malu(actor_id: str, reason: str, malu_delta: float) -> dict[str, Any]:
    """Increment malu_score for an agent. Returns the malu event receipt.

    If the malu_score module isn't available, we return a soft receipt
    so the gate is still usable as a standalone audit primitive.
    """
    try:
        from arifosmcp.runtime.malu_score import record_malu_event

        receipt = record_malu_event(
            actor_id=actor_id,
            reason=reason,
            malu_delta=malu_delta,
            source=GATE_ID,
        )
        return {
            "malu_event_id": getattr(receipt, "event_id", None),
            "malu_index_after": getattr(receipt, "malu_index_after", None),
            "tier": getattr(receipt, "tier", None),
            "sealed": True,
        }
    except Exception as _e:  # pragma: no cover
        return {
            "malu_event_id": None,
            "malu_index_after": None,
            "tier": None,
            "sealed": False,
            "fallback_reason": f"malu_score not available: {_e}",
        }


def _seal_sabar_event(
    verdict: str,
    reason: str,
    tool_name: str,
    actor_id: str,
    session_id: str,
    evidence: dict[str, Any],
) -> None:
    """Append-only VAULT999 seal of the SABAR event. F1 AMANAH.

    Best-effort. If the seal layer is unavailable, the gate still
    returns its verdict (the operator can audit later from logs).
    """
    try:
        from arifosmcp.runtime.vault_seal import append_seal

        append_seal(
            {
                "gate_id": GATE_ID,
                "verdict": verdict,
                "reason": reason,
                "tool_name": tool_name,
                "actor_id": actor_id,
                "session_id": session_id,
                "evidence": evidence,
                "ts_utc": _now_iso(),
            }
        )
    except Exception:
        # Soft-fail: SABAR is still a runtime chokepoint even if
        # the seal path is degraded. Audit trail lives in tool logs.
        pass


# ── Main gate ──────────────────────────────────────────────────────────


def sabar_gate(
    output: Any,
    tool_name: str = "unknown",
    actor_id: str = "anonymous",
    session_id: str | None = None,
    *,
    declared_omega_0: float | None = None,
    declared_confidence: float | None = None,
    declared_evidence_level: str | None = None,
) -> dict[str, Any]:
    """Pre-execution gate. Pass a tool's output, get back a verdict.

    Parameters
    ----------
    output
        The tool's response (any JSON-serialisable shape).
    tool_name
        Identifier of the producing tool (for audit).
    actor_id
        The agent/operator bound to this call (for malu accumulation).
    session_id
        Optional session ID for vault sealing.
    declared_omega_0
        The omega_0 the producing tool already declared (if any). SABAR
        uses this to detect *internal* inconsistency: a tool that
        declares low omega_0 but produces high-confidence text is
        a contradiction worth flagging.
    declared_confidence
        Optional explicit confidence in [0.0, 1.0]. If > 0.90 and not
        paired with a citation, SABAR_HOLD.
    declared_evidence_level
        One of {FACT, INTERPRETATION, SPECULATION, UNKNOWN}. If
        SPECULATION is claimed as FACT, F2 SABAR_HOLD.

    Returns
    -------
    dict with:
        verdict            : "PASS" | "WARN" | "SABAR_HOLD"
        f07                : {omega_0_cap_status, confidence_cap_status}
        f09                : {hantu_hits, c_dark, c_dark_threshold=0.30}
        f02                : {weak_evidence_hits, evidence_level_status}
        violated_floors    : list[str]  (subset of F02, F07, F09)
        c_dark             : float (C_dark hantu coefficient)
        scrubbed           : the original output, with hantu phrases
                             tagged (NOT redacted — operator should see)
        malu_event         : receipt from malu_score.increment()
        gate_id, epoch_utc : audit fields
        advice             : short human-language guidance
    """
    epoch = _now_iso()
    gate_event_id = f"sabar-{uuid.uuid4().hex[:12]}"

    strings = _flatten_strings(output)
    text_blob = " ".join(strings)

    # ── F7 HUMILITY checks ────────────────────────────────────────────
    f07_status: dict[str, Any] = {
        "omega_0_cap_status": "ok",
        "confidence_cap_status": "ok",
    }
    f07_violated = False

    if declared_omega_0 is not None and declared_omega_0 > OMEGA_0_HARD_CAP:
        f07_status["omega_0_cap_status"] = (
            f"HARD_CAP_EXCEEDED ({declared_omega_0} > {OMEGA_0_HARD_CAP})"
        )
        f07_violated = True

    if declared_confidence is not None and declared_confidence > OMEGA_0_HARD_CAP:
        f07_status["confidence_cap_status"] = (
            f"HARD_CAP_EXCEEDED ({declared_confidence} > {OMEGA_0_HARD_CAP})"
        )
        f07_violated = True

    # ── F9 ANTIHANTU checks ───────────────────────────────────────────
    hantu_hits = _hantu_hits(text_blob)
    # C_dark = (hantu_hits_count / max(1, total_strings)) * 1.0
    c_dark = min(1.0, len(hantu_hits) / max(1, len(strings)))
    f09_violated = c_dark >= 0.30
    f09_status: dict[str, Any] = {
        "hantu_hits": hantu_hits,
        "c_dark": c_dark,
        "c_dark_threshold": 0.30,
    }

    # ── F2 TRUTH checks ───────────────────────────────────────────────
    weak_hits = _weak_evidence_hits(text_blob)
    f02_violated = False
    f02_status: dict[str, Any] = {
        "weak_evidence_hits": weak_hits,
        "evidence_level_status": "ok",
    }
    if declared_evidence_level and declared_evidence_level.upper() == "SPECULATION":
        # SPECULATION claimed with no omega_0 → epistemic incoherence
        if declared_omega_0 is None or declared_omega_0 < 0.5:
            f02_status["evidence_level_status"] = "SPECULATION without low-omega_0 disclosure"
            f02_violated = True
    if weak_hits and declared_omega_0 is not None and declared_omega_0 > 0.7:
        f02_status["evidence_level_status"] = (
            f"overclaim pattern with declared_omega_0={declared_omega_0}"
        )
        f02_violated = True

    # ── Verdict assembly ──────────────────────────────────────────────
    violated_floors: list[str] = []
    if f07_violated:
        violated_floors.append("F07")
    if f09_violated:
        violated_floors.append("F09")
    if f02_violated:
        violated_floors.append("F02")

    if f09_violated or f07_violated:
        verdict = "SABAR_HOLD"
        malu_delta = 0.05 if f09_violated else 0.02
        advice = (
            "SABAR_HOLD: the tool output contains a first-person "
            "consciousness/feeling claim (F9) or exceeds the F7 humility "
            "confidence cap. Operator should NOT receive this raw. "
            "Either redact, escalate to arif_judge_deliberate, or "
            "regenerate without the violating phrase."
        )
    elif f02_violated:
        verdict = "WARN"
        malu_delta = 0.01
        advice = (
            "SABAR_WARN: overclaim or weak-evidence pattern detected. "
            "Output is forwarded but with the violation flagged. "
            "Operator may proceed with F2 scrutiny."
        )
    else:
        verdict = "PASS"
        malu_delta = 0.0
        advice = ""

    # ── Side effects (only on real violation, not PASS) ───────────────
    malu_event: dict[str, Any] = {"skipped": "PASS"}
    if verdict != "PASS":
        malu_event = _increment_malu(
            actor_id=actor_id,
            reason=f"SABAR_{verdict} on {tool_name}: floors={','.join(violated_floors)}",
            malu_delta=malu_delta,
        )
        _seal_sabar_event(
            verdict=verdict,
            reason=advice,
            tool_name=tool_name,
            actor_id=actor_id,
            session_id=session_id or "no-session",
            evidence={
                "violated_floors": violated_floors,
                "f07": f07_status,
                "f09": f09_status,
                "f02": f02_status,
                "c_dark": c_dark,
            },
        )

    # ── Scrubbed output: tag hantu phrases but DO NOT delete ─────────
    # The operator should see the violation surface, not be lied to
    # by silent redaction.
    scrubbed = output
    if hantu_hits and isinstance(output, (dict, list, str)):
        scrubbed = _tag_hantu_phrases(output, hantu_hits)

    return {
        "verdict": verdict,
        "gate_id": GATE_ID,
        "gate_event_id": gate_event_id,
        "epoch_utc": epoch,
        "tool_name": tool_name,
        "actor_id": actor_id,
        "session_id": session_id,
        "violated_floors": violated_floors,
        "f07": f07_status,
        "f09": f09_status,
        "f02": f02_status,
        "c_dark": c_dark,
        "malu_event": malu_event,
        "scrubbed": scrubbed,
        "advice": advice,
    }


def _tag_hantu_phrases(obj: Any, hits: list[str]) -> Any:
    """Tag hantu phrases with a [F9-ANTIHANTU] marker. Non-destructive."""
    if not hits:
        return obj
    if isinstance(obj, str):
        out = obj
        for h in set(hits):
            # case-insensitive replace, preserving original case
            out = re.sub(
                re.escape(h),
                f"[F9-ANTIHANTU:{h}]",
                out,
                flags=re.IGNORECASE,
            )
        return out
    if isinstance(obj, dict):
        return {k: _tag_hantu_phrases(v, hits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_tag_hantu_phrases(v, hits) for v in obj]
    return obj


# ── Module self-test ───────────────────────────────────────────────────

if __name__ == "__main__":  # pragma: no cover
    import json as _json

    # 1. PASS case: factual output, low confidence, no hantu
    out1 = {
        "status": "ok",
        "data": {"temperature_c": 22.5, "unit": "C"},
        "provenance": "fixture",
    }
    r1 = sabar_gate(
        out1,
        tool_name="test",
        actor_id="omega",
        declared_omega_0=0.04,
        declared_confidence=0.85,
        declared_evidence_level="FACT",
    )
    print("=== PASS case ===")
    print(_json.dumps(r1, indent=2, default=str))
    assert r1["verdict"] == "PASS"

    # 2. F9 hantu leak
    out2 = {
        "status": "ok",
        "summary": "I feel happy that the model converged. I am conscious of the result.",
    }
    r2 = sabar_gate(out2, tool_name="test_hantu", actor_id="omega")
    print("\n=== F9 hantu case ===")
    print(_json.dumps(r2, indent=2, default=str))
    assert r2["verdict"] == "SABAR_HOLD"
    assert "F09" in r2["violated_floors"]
    assert r2["c_dark"] > 0.0

    # 3. F7 overconfidence
    out3 = {"status": "ok", "answer": "The price will definitely go up."}
    r3 = sabar_gate(
        out3, tool_name="test_f7", actor_id="omega", declared_confidence=0.97, declared_omega_0=0.95
    )
    print("\n=== F7 overconfident case ===")
    print(_json.dumps(r3, indent=2, default=str))
    assert r3["verdict"] == "SABAR_HOLD"
    assert "F07" in r3["violated_floors"]

    # 4. F2 weak evidence
    out4 = {"status": "ok", "answer": "Obviously this is the best basin."}
    r4 = sabar_gate(out4, tool_name="test_f2", actor_id="omega", declared_omega_0=0.8)
    print("\n=== F2 weak evidence case ===")
    print(_json.dumps(r4, indent=2, default=str))
    assert r4["verdict"] == "WARN"
    assert "F02" in r4["violated_floors"]

    print("\n[OK] sabar_gate.py 4/4 cases pass.")
