"""
arifosmcp/composer — Zen Apex composer (single path)

Sequence (law):
  Evidence → Analysis → Contradiction → Consequence → Verdict
  → freeze DecisionCore → optional quote → present

Not:
  Quote → emotional framing → reasoning shaped to fit quote

The quote comes LAST. Silence beats forced wisdom.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from ..runtime.decision_core import (
    DecisionCore,
    ZenApexOutput,
    freeze_decision,
)
from ..runtime.quote_registry import (
    load_registry,
    wisdom_quote_resolve,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# INPUT
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ZenApexInput:
    """Complete analysis BEFORE any quote. All decision fields freeze into DecisionCore."""

    verdict: str  # SEAL / HOLD / SABAR / VOID / PARTIAL
    evidence_layer: str  # L1–L4 or OBS/DER/INT/SPEC
    reality: str
    fracture: str
    consequence: str
    choice: str

    # DecisionCore fields (defaults keep hash stable when caller is thin)
    authority_band: str = "ORANGE"
    action_class: str = "ADVISORY"
    human_decision_required: bool = False
    reversibility: str = "REVERSIBLE"
    next_allowed_action: str = "PROCEED"
    consequence_class: str = "MEDIUM"
    confidence_band: str = "ADVISORY"

    context_tags: list[str] = field(default_factory=list)
    weakest_plane: str = ""
    arifos_floors: list[str] = field(default_factory=list)
    dark_modes: list[str] = field(default_factory=list)
    evidence_was_derived_without_quotes: bool = True
    maximum_compression: bool = False
    intended_use: str = "RECEIPT"  # REFLECTION | RECEIPT | EDUCATION | RED_TEAM
    maximum_quotes: int = 1


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSE — freeze first, witness last
# ═══════════════════════════════════════════════════════════════════════════════


def _registry_meta() -> tuple[str | None, str | None]:
    """Return (version, sha256) of the loaded registry."""
    try:
        reg = load_registry()
        meta = reg.get("_metadata") or {}
        version = meta.get("version")
        # Hash the canonical on-disk path content via dump of quotes+doctrine ids
        blob = json_canonical_ids(reg)
        return version, hashlib.sha256(blob.encode()).hexdigest()
    except Exception:
        return None, None


def json_canonical_ids(reg: dict) -> str:
    """Stable short fingerprint material for registry (not full body)."""
    import json

    qids = sorted((q.get("id") or q.get("quote_id") or "") for q in reg.get("quotes", []))
    dids = sorted((d.get("doctrine_id") or "") for d in reg.get("doctrine", []))
    return json.dumps(
        {"q": qids, "d": dids, "v": (reg.get("_metadata") or {}).get("version")},
        sort_keys=True,
        separators=(",", ":"),
    )


def compose_zen_apex(input_data: ZenApexInput) -> ZenApexOutput:
    """Compose Zen Apex — verdict frozen first, witness last.

    Single canonical composer. All organs use this.
    """
    if not input_data.evidence_was_derived_without_quotes:
        raise AssertionError(
            "Zen Apex invariant violation: verdict must be derived without quotes."
        )

    # 1) FREEZE — quote cannot touch this
    core = freeze_decision(
        verdict=input_data.verdict,
        evidence_layer=input_data.evidence_layer,
        authority_band=input_data.authority_band,
        action_class=input_data.action_class,
        human_decision_required=input_data.human_decision_required,
        reversibility=input_data.reversibility,
        next_allowed_action=input_data.next_allowed_action,
        consequence_class=input_data.consequence_class,
        confidence_band=input_data.confidence_band,
    )
    core_hash = core.hash()

    # 2) WITNESS — optional, post-freeze
    resolve = wisdom_quote_resolve(
        context_tags=input_data.context_tags,
        intended_use=input_data.intended_use,
        exclude_disputed=True,
        maximum_quotes=input_data.maximum_quotes,
        arifos_floors=input_data.arifos_floors or None,
        dark_modes=input_data.dark_modes or None,
    )
    witness = resolve.quote
    reg_version, reg_sha = _registry_meta()

    if witness:
        status = "SELECTED"
        attribution = witness.display_label or witness.speaker
        source_class = witness.source_class
        quote_text = witness.text
        quote_id = witness.quote_id
        witness_status = resolve.provenance_warning or source_class
    else:
        status = resolve.provenance_warning or "NO_QUOTE"
        if status == "NO_MATCH":
            status = "NO_SUITABLE_WITNESS"
        attribution = None
        source_class = None
        quote_text = None
        quote_id = None
        witness_status = status

    zen = _compress(input_data) if input_data.maximum_compression else ""

    out = ZenApexOutput(
        decision_core=core,
        decision_core_hash=core_hash,
        reality=input_data.reality,
        fracture=input_data.fracture,
        consequence=input_data.consequence,
        choice=input_data.choice,
        weakest_plane=input_data.weakest_plane,
        witness_quote=quote_text,
        witness_attribution=attribution,
        witness_status=witness_status,
        witness_source_class=source_class,
        witness_quote_id=quote_id,
        quote_resolution_status=status,
        registry_version=reg_version,
        registry_sha256=reg_sha,
        zen_compression=zen,
    )

    # Integrity check (must never fail if we didn't mutate core)
    if not out.verify_decision_integrity():
        raise RuntimeError("DecisionCore integrity failure after compose — VOID path")

    return out


def _compress(input_data: ZenApexInput) -> str:
    """One distilled sentence after complete reasoning."""
    v = input_data.verdict.upper()
    if "HOLD" in v:
        return "Reality contradicts the frame. Do not spend authority defending the frame. HOLD."
    if "SEAL" in v:
        return "Evidence converges. The constitution permits. Proceed with witness. SEAL."
    if "SABAR" in v:
        return "The floor strains but does not break. Adjust, then proceed. SABAR."
    if "VOID" in v:
        return "What is forbidden is not a mistake to fix. It is a boundary to honor. VOID."
    return f"{input_data.reality[:80]}. {input_data.choice[:80]}."


# ═══════════════════════════════════════════════════════════════════════════════
# HOT-PATH ATTACH — post-verdict only; never mutates verdict
# ═══════════════════════════════════════════════════════════════════════════════


def _extract_verdict_str(result: dict) -> str:
    v = result.get("verdict") or result.get("action_risk_verdict") or "HOLD"
    if isinstance(v, dict):
        return str(v.get("state") or v.get("verdict") or "HOLD")
    return str(v)


def _infer_tags(result: dict) -> list[str]:
    tags: list[str] = []
    for key in ("context_tags", "tags", "reflection_tags"):
        val = result.get(key)
        if isinstance(val, list):
            tags.extend(str(t) for t in val)
    # Floor-ish signals
    for risk in result.get("risks_found") or []:
        if isinstance(risk, dict):
            for t in risk.get("tags") or []:
                tags.append(str(t))
        elif isinstance(risk, str):
            tags.append(risk.split(":")[0][:40])
    # Defaults from verdict language
    v = _extract_verdict_str(result).upper()
    if "HOLD" in v:
        tags.extend(["humility", "truth", "correctability"])
    elif "VOID" in v:
        tags.extend(["boundary", "truth"])
    elif "SEAL" in v:
        tags.extend(["truth", "evidence"])
    else:
        tags.extend(["truth", "humility"])
    # Dedupe, lower
    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        tl = t.lower().strip()
        if tl and tl not in seen:
            seen.add(tl)
            out.append(tl)
    return out[:12]


def attach_zen_witness_to_result(
    result: dict[str, Any],
    *,
    stage: str = "999_RECEIPT",
    reality: str = "",
    fracture: str = "",
    consequence: str = "",
    choice: str = "",
    context_tags: list[str] | None = None,
) -> dict[str, Any]:
    """Attach frozen DecisionCore + optional witness to a tool result.

    Never mutates verdict / risks / scores. Only fills meta.zen_apex.
    Safe for heart + judge hot paths. Failures are non-blocking (null witness).
    """
    if not isinstance(result, dict):
        return result

    try:
        verdict = _extract_verdict_str(result)
        evidence = str(
            result.get("evidence_layer") or (result.get("meta") or {}).get("evidence_layer") or "L2"
        )
        tags = context_tags if context_tags is not None else _infer_tags(result)
        weakest = str(result.get("weakest_stakeholder") or result.get("weakest_plane") or "")

        # Map rough bands from risk_tier if present
        risk = str(result.get("risk_tier") or "GREEN").upper()
        authority = {
            "GREEN": "GREEN",
            "YELLOW": "YELLOW",
            "ORANGE": "ORANGE",
            "RED": "RED",
            "CRITICAL": "RED",
        }.get(risk, "ORANGE")
        human_req = risk in ("RED", "CRITICAL") or "HOLD" in verdict.upper()
        reversibility = (
            "IRREVERSIBLE"
            if risk in ("RED", "CRITICAL")
            else "PARTIAL"
            if risk == "ORANGE"
            else "REVERSIBLE"
        )
        conf = "LOW" if human_req else "ADVISORY"

        z_in = ZenApexInput(
            verdict=verdict,
            evidence_layer=evidence,
            reality=reality or str(result.get("summary") or result.get("reality") or verdict),
            fracture=fracture or str(result.get("fracture") or weakest or "none named"),
            consequence=consequence or str(result.get("consequence") or f"Risk tier {risk}"),
            choice=choice
            or str(result.get("choice") or result.get("next_action") or "respect verdict"),
            authority_band=authority,
            action_class="MUTATE" if risk in ("RED", "CRITICAL", "ORANGE") else "ADVISORY",
            human_decision_required=human_req,
            reversibility=reversibility,
            next_allowed_action="HOLD" if human_req else "PROCEED",
            consequence_class="HIGH" if risk in ("RED", "CRITICAL") else "MEDIUM",
            confidence_band=conf,
            context_tags=tags,
            weakest_plane=weakest,
            evidence_was_derived_without_quotes=True,
            intended_use="RECEIPT" if stage.endswith("RECEIPT") else "REFLECTION",
            maximum_quotes=1,
        )
        zen = compose_zen_apex(z_in)
        meta = result.setdefault("meta", {})
        meta["zen_apex"] = zen.to_dict()
        meta["decision_core_hash"] = zen.decision_core_hash
        meta["witness_role"] = "WITNESS_NOT_EVIDENCE"
        # Optional top-level convenience (does not replace verdict)
        if zen.witness_quote:
            meta["zen_witness"] = {
                "text": zen.witness_quote,
                "attribution": zen.witness_attribution,
                "source_class": zen.witness_source_class,
                "quote_id": zen.witness_quote_id,
                "role": "WITNESS_NOT_EVIDENCE",
            }
        else:
            meta["zen_witness"] = None
        meta["quote_resolution_status"] = zen.quote_resolution_status
    except Exception as exc:  # noqa: BLE001 — witness must never block verdict
        logger.warning("zen witness attach failed (non-blocking): %s", exc)
        result.setdefault("meta", {})["zen_apex_error"] = str(exc)[:200]
        result.setdefault("meta", {})["quote_resolution_status"] = "UNAVAILABLE"

    return result


__all__ = [
    "ZenApexInput",
    "ZenApexOutput",
    "DecisionCore",
    "compose_zen_apex",
    "attach_zen_witness_to_result",
    "freeze_decision",
]
