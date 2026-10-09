"""Deployment-drift measurement and evidence hierarchy (extracted from tools.py).

W-02 / W-03: Deployment-drift floor (2026-08-04)
INVARIANT: If substrate.drift or software_release.drift is true, the
payload MUST NOT claim SEAL/PROCEED/SELAMAT and MUST NOT claim
mutation_allowed=true in any nested block.

Extracted 2026-09-28 from arifosmcp/runtime/tools.py (~800 lines of drift
logic scattered across 28K-line monolith). Pure functions only — no
payload mutation, no side effects. apply_deployment_drift_floor remains
in tools.py as the mutation entry point.
"""

from __future__ import annotations

from typing import Any

_SEALISH = frozenset({
    "SEAL", "PROCEED", "OK", "APPROVED", "COMPLETED",
    "completed", "SAFE", "SELAMAT", "FULL",
})

_MEASURED_DRIFT_FIELDS: tuple[tuple[str, str], ...] = (
    ("substrate", "drift"),
    ("software_release", "drift"),
    ("software_release.deployment_invariant", "drift"),
)
_DERIVED_DEGRADED_TOKENS: tuple[str, ...] = ("DEGRADED", "FAIL")
_DRIFT_NEXT_ACTION_BY_CAUSE: dict[str, str] = {
    "DEPLOYMENT_DRIFT": "RECONCILE_SOURCE_BUILT_DEPLOYED",
    "SUBSTRATE_DEGRADED_UNATTRIBUTED": "MEASURE_SUBSTRATE_DEGRADATION_CAUSE",
}


def drift_spots(payload: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """Known payload locations that may carry drift evidence."""
    spots: list[tuple[str, dict[str, Any]]] = [("envelope", payload)]
    res = payload.get("result")
    if isinstance(res, dict):
        spots.append(("result", res))
    return spots


def derive_degradation_cause_from_spots(
    spots: list[tuple[str, dict[str, Any]]],
) -> dict[str, Any] | None:
    """Recover the kernel's own stated cause for DEGRADED substrate label."""
    for loc, d in spots:
        if not isinstance(d, dict):
            continue
        for container_key in ("effective_state", "effective"):
            node = d.get(container_key)
            if isinstance(node, dict) and node.get("session_authority_state"):
                return {
                    "location": f"{loc}.{container_key}",
                    "field": "session_authority_state",
                    "value": str(node["session_authority_state"]),
                }
        cc = d.get("constitutional_check")
        if isinstance(cc, dict) and cc.get("substrate_state"):
            return {
                "location": f"{loc}.constitutional_check",
                "field": "substrate_state",
                "value": str(cc["substrate_state"]),
            }
    return None


def derive_degradation_cause(payload: dict[str, Any]) -> dict[str, Any] | None:
    return derive_degradation_cause_from_spots(drift_spots(payload))


def measure_drift_from_spots(
    spots: list[tuple[str, dict[str, Any]]],
) -> dict[str, Any]:
    """Apply the evidence hierarchy to drift evidence found at `spots`.

    RAW_OBSERVATION > MEASURED_FACT > DERIVED_STATE > REASON_CODE > NARRATIVE_LABEL
    """
    measured: list[dict[str, Any]] = []
    derived: list[dict[str, Any]] = []

    for loc, d in spots:
        if not isinstance(d, dict):
            continue
        sub = d.get("substrate") if isinstance(d.get("substrate"), dict) else {}
        sw = d.get("software_release") if isinstance(d.get("software_release"), dict) else {}
        inv = (
            sw.get("deployment_invariant")
            if isinstance(sw.get("deployment_invariant"), dict)
            else {}
        )
        for prefix, node in (
            ("substrate", sub),
            ("software_release", sw),
            ("software_release.deployment_invariant", inv),
        ):
            if isinstance(node, dict) and isinstance(node.get("drift"), bool):
                measured.append({
                    "location": loc,
                    "field": f"{prefix}.drift",
                    "value": node["drift"],
                    "tier": "MEASURED",
                })
        deg = d.get("degraded")
        if isinstance(deg, list):
            for entry in deg:
                if "drift" in str(entry).lower():
                    measured.append({
                        "location": loc,
                        "field": "degraded[]",
                        "value": str(entry),
                        "tier": "MEASURED",
                    })
        if isinstance(sub, dict) and "state" in sub:
            derived.append({
                "location": loc,
                "field": "substrate.state",
                "value": str(sub.get("state")),
                "tier": "DERIVED",
            })

    measured_true = [f for f in measured if f["value"] is True or f["field"] == "degraded[]"]
    measured_false = [f for f in measured if f["value"] is False]
    derived_degraded = [
        label for label in derived
        if str(label["value"]).upper() in _DERIVED_DEGRADED_TOKENS
    ]

    out: dict[str, Any] = {
        "fired": False,
        "evidence_tier": "NONE",
        "cause": None,
        "location": None,
        "field": None,
        "value": None,
        "measured_facts": measured,
        "derived_labels": derived,
        "superseded": [],
        "derived_degradation_cause": None,
        "rationale": "no drift evidence present",
    }

    if measured_true:
        hit = measured_true[0]
        out.update(
            fired=True, evidence_tier="MEASURED_FACT", cause="DEPLOYMENT_DRIFT",
            location=hit["location"], field=hit["field"], value=hit["value"],
            rationale=f"MEASURED drift=true at {hit['location']}.{hit['field']}={hit['value']}",
        )
        return out

    if derived_degraded and not measured_false:
        hit = derived_degraded[0]
        out.update(
            fired=True, evidence_tier="DERIVED_STATE_UNCONTRADICTED",
            cause="SUBSTRATE_DEGRADED_UNATTRIBUTED",
            location=hit["location"], field=hit["field"], value=hit["value"],
            derived_degradation_cause=derive_degradation_cause_from_spots(spots),
            rationale=f"no drift measurement; DERIVED {hit['location']}.{hit['field']}={hit['value']} — fail-closed",
        )
        return out

    if derived_degraded and measured_false:
        out["superseded"] = [
            {"derived_label": label, "overridden_by": fact, "rule": "MEASURED_FACT > DERIVED_STATE"}
            for label in derived_degraded for fact in measured_false
        ]
        out["derived_degradation_cause"] = derive_degradation_cause_from_spots(spots)
        out["rationale"] = (
            f"DERIVED label overridden by MEASURED drift=false — floor withheld"
        )
        return out

    return out


def measure_deployment_drift(payload: Any) -> dict[str, Any]:
    """Measure deployment drift under explicit evidence hierarchy."""
    if not isinstance(payload, dict):
        return {
            "fired": False, "evidence_tier": "NONE", "cause": None,
            "location": None, "field": None, "value": None,
            "measured_facts": [], "derived_labels": [], "superseded": [],
            "derived_degradation_cause": None,
            "rationale": "payload is not a dict — no evidence surface",
        }
    return measure_drift_from_spots(drift_spots(payload))


def payload_has_deployment_drift(payload: dict[str, Any]) -> bool:
    """Thin predicate over measure_deployment_drift()."""
    return bool(measure_deployment_drift(payload).get("fired"))


def drift_reason_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    """Auditable 'which payload location, which field' record for a firing."""
    return {
        "cause": evidence.get("cause") or "REASON_UNMEASURED",
        "evidence_tier": evidence.get("evidence_tier"),
        "location": evidence.get("location"),
        "field": evidence.get("field"),
        "value": evidence.get("value"),
        "chain": f"{evidence.get('location')}.{evidence.get('field')}={evidence.get('value')}",
        "measured_facts": evidence.get("measured_facts", []),
        "derived_labels": evidence.get("derived_labels", []),
        "superseded": evidence.get("superseded", []),
        "derived_degradation_cause": evidence.get("derived_degradation_cause"),
        "rationale": evidence.get("rationale"),
        "hierarchy": "RAW_OBSERVATION > MEASURED_FACT > DERIVED_STATE > REASON_CODE > NARRATIVE_LABEL",
    }
