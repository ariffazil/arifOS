"""
Compatibility wrapper for the legacy governance engine import path.

The current runtime only needs a small subset of the old module: a few derived
metrics helpers and ``wrap_tool_output`` to normalise raw tool results into the
shape expected by the MCP bridge.
"""

from __future__ import annotations

from typing import Any

from arifosmcp.runtime.contracts import AAA_TOOL_STAGE_MAP


def _safe_float(data: dict[str, Any], *keys: str, default: float = 0.0) -> float:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return default
        value = value.get(key)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _derive_apex_dials(tool_name: str, result: dict[str, Any]) -> dict[str, Any]:
    truth = max(0.0, min(1.0, _safe_float(result, "truth_score", default=0.88)))
    peace = max(0.0, min(1.5, _safe_float(result, "peace2", default=1.0)))
    empathy = max(0.0, min(1.0, _safe_float(result, "empathy_score", default=0.9)))
    energy = max(0.0, min(1.0, 1.0 - abs(_safe_float(result, "delta_s", default=0.0))))
    genius = round(truth * min(1.0, peace) * empathy * (energy**2), 4)
    return {
        "tool": tool_name,
        "A": round(truth, 4),
        "P": round(min(1.0, peace), 4),
        "X": round(empathy, 4),
        "E": round(energy, 4),
        "genius_score": genius,
    }


def _calculate_tri_witness_consensus(tool_name: str, result: dict[str, Any]) -> dict[str, Any]:
    _ = tool_name
    human = 1.0 if result.get("authority") or result.get("auth_context") else 0.8
    ai = max(0.0, min(1.0, _safe_float(result, "truth_score", default=0.88)))
    earth = 1.0 if result.get("grounded", True) else 0.7
    w3 = round((human * ai * earth) ** (1 / 3), 4)
    threshold = 0.95
    return {
        "pass": w3 >= threshold,
        "w3": w3,
        "threshold": threshold,
        "tool_class": "UTILITY",
        "human_witness": human,
        "ai_witness": ai,
        "earth_witness": earth,
    }


def _law13_checks(tool_name: str, result: dict[str, Any]) -> dict[str, Any]:
    tri = _calculate_tri_witness_consensus(tool_name, result)
    has_session = bool(result.get("session_id"))
    return {
        "F1_AMANAH": {"required": True, "pass": True},
        "F2_TRUTH": {"required": True, "pass": _safe_float(result, "truth_score", default=0.88) >= 0.7},
        "F3_TRI_WITNESS": {"required": True, "pass": tri["pass"]},
        "F11_AUTHORITY": {"required": True, "pass": has_session or bool(result.get("auth_context"))},
        "F13_SOVEREIGN": {"required": False, "pass": True},
    }


def _derive_vitality_index(
    result: dict[str, Any],
    law_checks: dict[str, Any] | None = None,
    apex_dials: dict[str, Any] | None = None,
) -> dict[str, Any]:
    checks = law_checks or _law13_checks("unknown", result)
    dials = apex_dials or _derive_apex_dials("unknown", result)
    amanah = 1.0 if checks.get("F1_AMANAH", {}).get("pass") else 0.0
    peace = max(0.1, _safe_float(result, "peace2", default=1.0))
    kappa_r = max(0.1, _safe_float(result, "kappa_r", default=0.97))
    rasa = max(0.1, float(dials.get("A", 0.88)))
    delta_s = abs(_safe_float(result, "delta_s", default=0.02))
    psi = round((delta_s * peace * kappa_r * rasa * amanah) / (0.1 + 1e-6), 4)
    return {"psi": psi, "status": "HEALTHY" if psi >= 1.0 else "UNSTABLE"}


def wrap_tool_output(
    tool_name: str | None = None,
    result: dict[str, Any] | None = None,
    *,
    tool: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    tool_name = tool_name or tool or "unknown_tool"
    payload = payload if isinstance(payload, dict) else result if isinstance(result, dict) else {"result": result}
    verdict = str(payload.get("verdict", "SEAL"))
    if verdict not in {"SEAL", "SABAR", "PARTIAL", "VOID", "HOLD", "888_HOLD"}:
        verdict = "SEAL"

    if verdict == "888_HOLD":
        verdict = "HOLD"

    status = "ERROR" if verdict == "VOID" else ("DRY_RUN" if payload.get("dry_run") else "SUCCESS")
    law_checks = _law13_checks(tool_name, payload)
    apex_dials = _derive_apex_dials(tool_name, payload)
    vitality = _derive_vitality_index(payload, law_checks, apex_dials)
    tri = _calculate_tri_witness_consensus(tool_name, payload)
    failed = [name for name, meta in law_checks.items() if meta.get("required") and not meta.get("pass")]

    errors = []
    for name in failed:
        remediation = None
        if name == "F11_AUTHORITY":
            remediation = {
                "next_tool": "init_anchor",
                "required_args": ["actor_id", "intent"],
                "example_payload": {
                    "actor_id": "operator",
                    "intent": "authenticate and continue",
                },
                "retry_safe": True,
            }
        errors.append({"code": name, "message": f"{name} check failed", "remediation": remediation})
    note = payload.get("message") or payload.get("note") or ("Compatibility wrapper output")

    return {
        "ok": verdict != "VOID",
        "tool": tool_name,
        "canonical_name": tool_name,
        "stage": AAA_TOOL_STAGE_MAP.get(tool_name, "333_MIND"),
        "verdict": verdict,
        "status": status,
        "payload": payload,
        "note": note,
        "errors": errors,
        "authority": payload.get("authority", {}),
        "auth_context": payload.get("auth_context"),
        "metrics": {
            "apex_dials": apex_dials,
            "vitality_index": vitality,
            "tri_witness": tri,
        },
    }


__all__ = [
    "_calculate_tri_witness_consensus",
    "_derive_apex_dials",
    "_derive_vitality_index",
    "_law13_checks",
    "wrap_tool_output",
]
