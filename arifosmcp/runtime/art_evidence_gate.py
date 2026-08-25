"""ART evidence gates wired to arifFlow.

This module is the kernel-side adapter for the three pre-execution evidence
questions. It deliberately does not add vault writes: arifFlow receives the
receipts as the flow/audit witness, while the kernel remains the authority
that decides whether execution may continue.

Gates:
  1. SelfCheck — map the intent to a canonical skill gene.
  2. SufficientContext — combine risk proximity and context audit mode.
  3. AtomicDecomposition — split the intent into inspectable atoms.

A result of INSUFFICIENT or INCONSISTENT is returned to ART as HOLD. UNKNOWN
degrades gracefully unless every evidence source is unavailable.
"""
from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger("arifosmcp.art_evidence_gate")

ARIFLOW_INGEST_URL = os.getenv("ARIFLOW_INGEST_URL", "http://127.0.0.1:7073/ingest")
ARIFLOW_EVIDENCE_GATE_ENABLED = os.getenv(
    "ARIFLOW_EVIDENCE_GATE_ENABLED", "1"
).lower() not in {"0", "false", "no", "off"}
ARIFLOW_TIMEOUT_S = float(os.getenv("ARIFLOW_EVIDENCE_GATE_TIMEOUT_S", "1.5"))


class EvidenceVerdict(StrEnum):
    """Canonical evidence result vocabulary."""

    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"
    INCONSISTENT = "INCONSISTENT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class EvidenceGateResult:
    """Machine-readable ART evidence result."""

    verdict: EvidenceVerdict
    gates: dict[str, dict[str, Any]]
    receipts: dict[str, dict[str, Any]]


GENE_KEYWORDS = {
    "boundary_sensing": ["boundary", "edge", "limit", "threshold"],
    "conservation_accounting": ["conservation", "mass balance", "audit", "ledger"],
    "entropy_reduction": ["entropy", "disorder", "negentropy", "order", "cleanup"],
    "gradient_detection": ["gradient", "anomaly", "outlier", "diff", "delta"],
    "reaction_gating": ["gate", "permit", "block", "approve", "refuse", "react"],
    "homeostasis_regulation": ["homeostasis", "stability", "equilibrium", "regulate"],
    "immune_response": ["immune", "threat", "attack", "defense", "scan"],
    "metabolic_flow_management": ["flow", "rate", "throughput", "metabolic", "bandwidth"],
    "lineage_and_replay": ["lineage", "history", "replay", "trace", "provenance"],
    "scar_learning": ["scar", "failure", "lesson", "post-mortem"],
    "multi_organ_translation": ["translate", "bridge", "vocabulary", "interpret"],
    "execution_discipline": ["execute", "dispatch", "forge", "apply", "run"],
}

ATOMIC_KEYWORDS = {
    "claim", "fact", "evidence", "data", "found", "observed", "measured",
    "test", "verify", "audit", "scan", "check", "grep", "find", "lookup",
    "compute", "deploy", "delete", "create", "update", "write", "send",
}
DISCOURSE_MARKERS = {
    "because", "therefore", "thus", "hence", "so", "and", "but", "however",
}

_RISK_ACTION_MAP = {
    "OBSERVE": "READ",
    "ANALYZE": "ADVISORY",
    "DRAFT": "ADVISORY",
    "SIMULATE": "ADVISORY",
    "MUTATE": "MUTATE",
    "EXTERNAL_SIDE_EFFECT": "MUTATE",
    "IRREVERSIBLE": "ATOMIC",
}
_CONTEXT_EVENT_MAP = {
    "OBSERVE": "CONTEXT_RETRIEVAL_TRACE",
    "ANALYZE": "CONTEXT_RETRIEVAL_TRACE",
    "DRAFT": "CONTEXT_RETRIEVAL_HIGH_RISK",
    "SIMULATE": "CONTEXT_RETRIEVAL_HIGH_RISK",
    "MUTATE": "CONTEXT_RETRIEVAL_HIGH_RISK",
    "EXTERNAL_SIDE_EFFECT": "CONTEXT_AUTHORITY_UPGRADE",
    "IRREVERSIBLE": "CONTEXT_CANONICAL_WRITE",
}
_CONTEXT_RISK_MAP = {
    "OBSERVE": "routine",
    "ANALYZE": "routine",
    "DRAFT": "routine",
    "SIMULATE": "routine",
    "MUTATE": "canonical",
    "EXTERNAL_SIDE_EFFECT": "external_action",
    "IRREVERSIBLE": "canonical",
}


def _intent_text(tool_name: str, payload: dict[str, Any]) -> str:
    parts = [str(tool_name or "unknown")]
    for key, value in (payload or {}).items():
        if key.startswith("_"):
            continue
        parts.append(f"{key}={value}")
    return " ".join(parts)


def _match_skill_gene(intent_text: str) -> str | None:
    text = (intent_text or "").lower()
    for gene, keywords in GENE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return gene
    return None


def _gate_selfcheck(
    intent_text: str, *, canonical_tool: bool = False,
) -> tuple[EvidenceVerdict, str, str | None]:
    try:
        from arifosmcp.runtime.skills_contracts_resource import serve_skill_gene

        if canonical_tool:
            return EvidenceVerdict.SUFFICIENT, "canonical_tool_manifest", None
        candidate = _match_skill_gene(intent_text)
        if candidate is None or serve_skill_gene(candidate) is None:
            return EvidenceVerdict.INSUFFICIENT, "skills_contracts:no_gene_match", candidate
        return EvidenceVerdict.SUFFICIENT, f"skills_contracts:{candidate}", candidate
    except (ImportError, ModuleNotFoundError) as exc:
        return EvidenceVerdict.UNKNOWN, f"import_error:{exc}", None
    except Exception as exc:
        return EvidenceVerdict.UNKNOWN, f"runtime:{exc}", None


def _gate_sufficient_context(
    *,
    tool_name: str,
    action_class: str,
    is_reversible: bool,
    session_id: str,
    actor_id: str,
) -> tuple[EvidenceVerdict, str, dict[str, Any]]:
    details: dict[str, Any] = {}
    rolls: list[EvidenceVerdict | str] = []

    risk_action = _RISK_ACTION_MAP.get(action_class, "READ")
    try:
        from arifosmcp.runtime.risk_ledger import gate_risk

        risk = gate_risk(
            tool_name=tool_name,
            action_class=risk_action,
            ack_irreversible=not is_reversible,
            session_id=session_id,
            actor_id=actor_id,
        )
        details["gate_risk_verdict"] = risk.verdict.name
        details["gate_risk_proximity"] = risk.proximity
        details["gate_risk_band"] = risk.proximity_band.name
        rolls.append(risk.verdict.name)
    except (ImportError, ModuleNotFoundError) as exc:
        details["gate_risk_error"] = f"import_error:{exc}"
        rolls.append(EvidenceVerdict.UNKNOWN)
    except Exception as exc:
        details["gate_risk_error"] = f"runtime:{exc}"
        rolls.append(EvidenceVerdict.UNKNOWN)

    try:
        from arifosmcp.runtime.context_audit import audit_classify

        audit_mode = audit_classify(
            event_type=_CONTEXT_EVENT_MAP.get(action_class, "CONTEXT_RETRIEVAL_TRACE"),
            risk_class=_CONTEXT_RISK_MAP.get(action_class, "routine"),
        )
        details["audit_mode"] = audit_mode.name
        rolls.append(audit_mode.name)
    except (ImportError, ModuleNotFoundError) as exc:
        details["audit_error"] = f"import_error:{exc}"
        rolls.append(EvidenceVerdict.UNKNOWN)
    except Exception as exc:
        details["audit_error"] = f"runtime:{exc}"
        rolls.append(EvidenceVerdict.UNKNOWN)

    if any(roll in ("HOLD", "VOID") for roll in rolls):
        return EvidenceVerdict.INSUFFICIENT, "context_or_risk:HOLD_or_VOID", details
    if all(roll in (EvidenceVerdict.UNKNOWN, "UNKNOWN") for roll in rolls):
        return EvidenceVerdict.UNKNOWN, "all_unknown", details
    source = "context_or_risk:sufficient"
    if EvidenceVerdict.UNKNOWN in rolls or "UNKNOWN" in rolls:
        source = "context_or_risk:sufficient_with_warning"
    return EvidenceVerdict.SUFFICIENT, source, details


def _decompose(intent_text: str) -> list[str]:
    text = (intent_text or "").strip()
    if not text:
        return []
    sentences = [part.strip() for part in text.replace("\n", ". ").replace(";", ". ").split(".") if part.strip()]
    atoms: list[str] = []
    for sentence in sentences:
        words = set(sentence.lower().split())
        if words & ATOMIC_KEYWORDS or words & DISCOURSE_MARKERS or len(sentence.split()) >= 3:
            atoms.append(sentence)
    return atoms


def _gate_atomic_decomposition(intent_text: str) -> tuple[EvidenceVerdict, str, list[str]]:
    atoms = _decompose(intent_text)
    if atoms:
        return EvidenceVerdict.SUFFICIENT, f"atomic:decomposed_to_{len(atoms)}_atoms", atoms
    return EvidenceVerdict.INSUFFICIENT, "atomic:no_atoms_decomposed", []


def aggregate_evidence(verdicts: dict[str, str]) -> str:
    values = list(verdicts.values())
    if "INCONSISTENT" in values:
        return EvidenceVerdict.INCONSISTENT
    if "INSUFFICIENT" in values:
        return EvidenceVerdict.INSUFFICIENT
    if "UNKNOWN" in values and "SUFFICIENT" not in values:
        return EvidenceVerdict.UNKNOWN
    return EvidenceVerdict.SUFFICIENT


def _emit_flow_receipt(
    *, actor_id: str, session_id: str, gate: str, verdict: str,
    source: str, payload: dict[str, Any], witness_organs: list[str],
) -> dict[str, Any]:
    epistemic = {
        "SUFFICIENT": "Specification",
        "INSUFFICIENT": "Observation",
        "INCONSISTENT": "Interpretation",
        "UNKNOWN": "Observation",
    }.get(verdict, "Observation")
    body = {
        "receipt_id": str(uuid.uuid4()),
        "previous_receipt_hash": None,
        "created_at": datetime.now(UTC).isoformat(),
        "actor_id": actor_id,
        "session_id": session_id,
        "session_token": None,
        "step_type": "Verify",
        "risk_class": "T0Observe",
        "topology_id": "art-evidence-gate",
        "lane_id": 0,
        "step_number": 1,
        "cost_ns": 250_000_000,
        "preceding_verify_cost_ns": None,
        "epistemic_label": epistemic,
        "floor_verdict": "Pass" if verdict == "SUFFICIENT" else "Caution",
        "intent_reason": f"ART evidence gate '{gate}' evaluation",
        "expected_outcome": f"verdict={verdict}; source={source}",
        "cooling_decision": "None",
        "tri_witness_votes": None,
        "merkle_root": None,
        "merkle_inclusion_proof": None,
        "payload": {"gate": gate, "verdict": verdict, "source": source, **payload},
        "formula_version": "qg.v0.3.1-vector",
        "formula_hash": "sha256:arifflow-fq-v2.2-2026-08-14",
        "witness_organs": witness_organs,
        "apex_block": None,
        "flow_block": None,
        "projection_block": None,
    }
    request = urllib.request.Request(
        ARIFLOW_INGEST_URL,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=ARIFLOW_TIMEOUT_S) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        return {"status": "http_error", "code": exc.code, "body": exc.read().decode()[:500]}
    except Exception as exc:
        return {"status": "exception", "error": str(exc)}


def run_art_evidence_gates(
    *, tool_name: str, action_class: str, is_reversible: bool,
    session_id: str, actor_id: str, payload: dict[str, Any],
    canonical_tool: bool = False,
) -> EvidenceGateResult:
    """Run all three gates and emit one arifFlow receipt per gate."""

    if not ARIFLOW_EVIDENCE_GATE_ENABLED:
        return EvidenceGateResult(
            verdict=EvidenceVerdict.UNKNOWN,
            gates={"disabled": {"verdict": EvidenceVerdict.UNKNOWN, "source": "disabled"}},
            receipts={},
        )

    intent_text = _intent_text(tool_name, payload)
    started = time.monotonic()

    selfcheck_verdict, selfcheck_source, matched_gene = _gate_selfcheck(
        intent_text, canonical_tool=canonical_tool
    )
    context_verdict, context_source, context_details = _gate_sufficient_context(
        tool_name=tool_name, action_class=action_class, is_reversible=is_reversible,
        session_id=session_id, actor_id=actor_id,
    )
    atomic_verdict, atomic_source, atoms = _gate_atomic_decomposition(intent_text)

    verdicts = {
        "selfcheck": selfcheck_verdict.value,
        "sufficient_context": context_verdict.value,
        "atomic_decomposition": atomic_verdict.value,
    }
    verdict = EvidenceVerdict(aggregate_evidence(verdicts))
    gates = {
        "selfcheck": {
            "verdict": selfcheck_verdict.value, "source": selfcheck_source,
            "matched_gene": matched_gene, "intent_text": intent_text,
        },
        "sufficient_context": {
            "verdict": context_verdict.value, "source": context_source,
            "details": context_details,
        },
        "atomic_decomposition": {
            "verdict": atomic_verdict.value, "source": atomic_source,
            "atom_count": len(atoms), "atoms_preview": atoms[:3],
        },
    }
    receipts = {
        "selfcheck": _emit_flow_receipt(
            actor_id=actor_id, session_id=session_id, gate="selfcheck",
            verdict=selfcheck_verdict.value, source=selfcheck_source,
            payload={"matched_gene": matched_gene}, witness_organs=["arifos"],
        ),
        "sufficient_context": _emit_flow_receipt(
            actor_id=actor_id, session_id=session_id, gate="sufficient_context",
            verdict=context_verdict.value, source=context_source,
            payload={"details": context_details}, witness_organs=["arifos", "aforge"],
        ),
        "atomic_decomposition": _emit_flow_receipt(
            actor_id=actor_id, session_id=session_id, gate="atomic_decomposition",
            verdict=atomic_verdict.value, source=atomic_source,
            payload={"atom_count": len(atoms), "atoms_preview": atoms[:3]},
            witness_organs=["arifos"],
        ),
    }
    for receipt in receipts.values():
        if receipt.get("status") in {"exception", "http_error"}:
            logger.warning("arifFlow evidence receipt failed: %s", receipt)
    gates["elapsed_ms"] = round((time.monotonic() - started) * 1000, 2)
    return EvidenceGateResult(verdict=verdict, gates=gates, receipts=receipts)


__all__ = [
    "ARIFLOW_EVIDENCE_GATE_ENABLED", "EvidenceVerdict", "EvidenceGateResult",
    "aggregate_evidence", "run_art_evidence_gates",
]
