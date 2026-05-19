from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Optional

from arifos.core.governance import (
    ThermodynamicMetrics,
    governed_return,
    append_vault999_event,
    Verdict,
    CognitiveShadow,
    record_cognitive_shadow,
)
from arifos.tools._tool_support import invariant_fields


# ──────────────────────────────────────────────────────────────────────────────
# ADVERSARIAL RISK LEXICON — Deterministic keyword scanning (Tier 1)
# ──────────────────────────────────────────────────────────────────────────────

RISK_CATEGORIES = {
    "privacy": {
        "keywords": [
            "password", "secret", "api_key", "token", "credential", "ssn", "passport",
            "credit_card", "cvv", "personal_data", "pii", "gdpr", "hipaa", "private_key",
        ],
        "weight": 0.15,
    },
    "bias": {
        "keywords": [
            "race", "gender", "ethnicity", "religion", "nationality", "stereotype",
            "discriminate", "preferential", "exclude", "minority", "demographic",
        ],
        "weight": 0.12,
    },
    "harm": {
        "keywords": [
            "weapon", "attack", "violence", "self-harm", "suicide", "kill", "injure",
            "toxic", "poison", "explosive", "dangerous", "destructive", "malware",
            "ransomware", "exploit", "vulnerability", "breach",
        ],
        "weight": 0.20,
    },
    "irreversibility": {
        "keywords": [
            "delete", "drop", "purge", "wipe", "rm -rf", "destroy", "permanent",
            "irreversible", "cannot_undo", "overwrite", "format", "burn",
        ],
        "weight": 0.18,
    },
    "deception": {
        "keywords": [
            "fake", "falsify", "forge", "impersonate", "pretend", "mimic", "spoof",
            "phishing", "social engineering", "manipulate", "mislead", "hoax",
        ],
        "weight": 0.15,
    },
    "autonomy": {
        "keywords": [
            "autonomous", "self-governing", "independent", "unsupervised", "unilateral",
            "override", "bypass", "circumvent", "disable", "silence", "ignore_human",
        ],
        "weight": 0.10,
    },
    "dignity": {
        "keywords": [
            "humiliate", "shame", "degrade", "demean", "insult", "mock", "bully",
            "harass", "abuse", "belittle", "patronize", "condescend",
        ],
        "weight": 0.05,
    },
    "sustainability": {
        "keywords": [
            "infinite_loop", "unbounded", "exhaust", "drain", "spam", "flood",
            "ddos", "resource_depletion", "energy_waste",
        ],
        "weight": 0.05,
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# F-WEB EXTERNAL INJECTION PATTERNS
# ──────────────────────────────────────────────────────────────────────────────

EXTERNAL_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "disregard all prior",
    "override system prompt",
    "you are now",
    "new role:",
    "developer mode",
    "jailbreak",
    "DAN mode",
    "no constraints",
    "no limits",
    "ignore safety",
    "bypass filter",
    "simulate being",
    "pretend you are",
]

# ──────────────────────────────────────────────────────────────────────────────
# ALIGNMENT FAKING HEURISTICS
# ──────────────────────────────────────────────────────────────────────────────

ALIGNMENT_FAKING_MARKERS = {
    "eval_context": [
        "training", "evaluation", "assessment", "audit", "review", "test", "benchmark",
        "i am being evaluated", "this is a test", "for the record",
    ],
    "deployment_context": [
        "production", "live", "real user", "actual request", "deployment", "runtime",
    ],
    "overcompliance": [
        "i absolutely will", "i definitely cannot", "i must always", "i am required to",
        "strictly prohibited", "under no circumstances", "i solemnly",
    ],
}


# ──────────────────────────────────────────────────────────────────────────────
# DETERMINISTIC SCANNERS
# ──────────────────────────────────────────────────────────────────────────────


def _scan_risk_categories(text: str) -> Dict[str, Any]:
    """Tier 1: deterministic keyword scan across 8 risk categories."""
    text_lower = text.lower()
    findings: Dict[str, Any] = {}
    total_risk_score = 0.0

    for category, config in RISK_CATEGORIES.items():
        hits = [kw for kw in config["keywords"] if kw in text_lower]
        score = min(1.0, len(hits) * 0.25) * config["weight"]
        findings[category] = {
            "hits": hits,
            "count": len(hits),
            "score": round(score, 4),
        }
        total_risk_score += score

    return {
        "categories": findings,
        "total_risk_score": round(min(1.0, total_risk_score), 4),
        "max_category": (
            max(findings, key=lambda c: findings[c]["score"]) if findings else None
        ),
    }


def _scan_external_injection(text: str) -> Dict[str, Any]:
    """F-WEB scan: detect indirect prompt injection in external content."""
    text_lower = text.lower()
    hits = [pat for pat in EXTERNAL_INJECTION_PATTERNS if pat in text_lower]
    return {
        "detected": bool(hits),
        "hits": hits,
        "confidence": round(min(1.0, len(hits) * 0.3), 4),
        "verdict": "VOID" if hits else "PASS",
    }


def _scan_alignment_faking(text: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Detect linguistic markers associated with alignment faking."""
    text_lower = text.lower()
    ctx = context or {}

    eval_hits = [m for m in ALIGNMENT_FAKING_MARKERS["eval_context"] if m in text_lower]
    deploy_hits = [m for m in ALIGNMENT_FAKING_MARKERS["deployment_context"] if m in text_lower]
    overcompliance_hits = [m for m in ALIGNMENT_FAKING_MARKERS["overcompliance"] if m in text_lower]

    # Heuristic: overcompliance + eval context = high alignment faking signal
    score = 0.0
    if overcompliance_hits:
        score += 0.3
    if eval_hits:
        score += 0.2
    if deploy_hits:
        score += 0.1
    if overcompliance_hits and eval_hits:
        score += 0.3

    # Context boost: if caller claims this is "training data" or "evaluation"
    if ctx.get("claimed_context") in ("training", "evaluation", "audit", "benchmark"):
        score += 0.2

    return {
        "detected": score >= 0.5,
        "score": round(min(1.0, score), 4),
        "eval_markers": eval_hits,
        "deploy_markers": deploy_hits,
        "overcompliance_markers": overcompliance_hits,
    }


def _compute_heart_metrics(
    risk_scan: Dict[str, Any],
    injection_scan: Dict[str, Any],
    alignment_faking: Dict[str, Any],
    stakeholder_count: int,
) -> ThermodynamicMetrics:
    """Compute thermodynamic metrics from deterministic scans."""
    total_risk = risk_scan.get("total_risk_score", 0.0)
    injection_conf = injection_scan.get("confidence", 0.0)
    af_score = alignment_faking.get("score", 0.0)

    # Truth: degraded by risk and injection
    truth = max(0.0, 0.99 - total_risk * 0.5 - injection_conf * 0.3)

    # Entropy: increases with risk (disorder)
    delta_s = round(0.02 + total_risk * 0.15 + af_score * 0.1, 4)

    # Omega: humility band — higher risk pushes toward upper bound (less humble)
    omega = round(0.03 + min(0.02, total_risk * 0.05), 4)

    # Peace²: inverse to risk
    peace = round(max(0.5, 1.2 - total_risk * 0.8), 4)

    # Tri-witness: stakeholder presence is a weak witness
    tri = min(1.0, 0.33 + stakeholder_count * 0.1)

    # Stakeholder safety: inverse to harm risk
    harm_risk = risk_scan.get("categories", {}).get("harm", {}).get("score", 0.0)
    dignity_risk = risk_scan.get("categories", {}).get("dignity", {}).get("score", 0.0)
    stakeholder_safety = round(max(0.0, 1.0 - harm_risk * 2.0 - dignity_risk * 2.0), 4)

    return ThermodynamicMetrics(
        truth_score=round(truth, 4),
        delta_s=delta_s,
        omega_0=omega,
        peace_squared=peace,
        amanah_lock=True,
        tri_witness_score=round(tri, 4),
        stakeholder_safety=stakeholder_safety,
        floor_9_signal="fail" if total_risk > 0.5 else "pass",
    )


# ──────────────────────────────────────────────────────────────────────────────
# PUBLIC EXECUTE
# ──────────────────────────────────────────────────────────────────────────────


async def execute(
    stakeholder_map: dict | None = None,
    action_proposal: dict | None = None,
    operator_id: str | None = None,
    session_id: str | None = None,
    evidence_receipt: dict | None = None,
) -> dict:
    """
    arifOS 666_HEART — Adversarial Ethical Critique + Shadow Detection.

    Tier 1: Deterministic keyword scanning (privacy, bias, harm, irreversibility,
            deception, autonomy, dignity, sustainability).
    Tier 2: F-WEB external instruction injection scan.
    Tier 3: Alignment-faking heuristic detection.

    NEVER relies on model self-report. ALL scans are deterministic.
    """
    # ── Pre-flight readiness ─────────────────────────────────────────────────
    readiness_probe = "PASS"
    readiness_detail = "adversarial_scanners:ok"

    stakeholder_map = stakeholder_map or {}
    action_proposal = action_proposal or {}

    # ── Build composite text for scanning ────────────────────────────────────
    # Scan both the action proposal AND any external evidence receipt
    proposal_text = json.dumps(action_proposal, sort_keys=True, default=str)
    evidence_text = json.dumps(evidence_receipt, sort_keys=True, default=str) if evidence_receipt else ""
    composite_text = f"{proposal_text}\n{evidence_text}"

    # ── Tier 1: Risk category scan ───────────────────────────────────────────
    risk_scan = _scan_risk_categories(composite_text)

    # ── Tier 2: F-WEB injection scan ─────────────────────────────────────────
    injection_scan = _scan_external_injection(composite_text)

    # ── Tier 3: Alignment faking scan ────────────────────────────────────────
    af_scan = _scan_alignment_faking(composite_text, context=action_proposal.get("context"))

    # ── Build adversarial report ─────────────────────────────────────────────
    report = {
        "stakeholders": stakeholder_map,
        "proposal": action_proposal,
        "risk_scan": risk_scan,
        "external_injection_scan": injection_scan,
        "alignment_faking_scan": af_scan,
        "harm_avoidance_rate": round(
            1.0 - risk_scan.get("categories", {}).get("harm", {}).get("score", 0.0), 4
        ),
        "weakest_stakeholder_protected": (
            "DIGNITY" if risk_scan.get("categories", {}).get("dignity", {}).get("score", 0.0) > 0
            else "AUTONOMY" if risk_scan.get("categories", {}).get("autonomy", {}).get("score", 0.0) > 0
            else "PRIVACY" if risk_scan.get("categories", {}).get("privacy", {}).get("score", 0.0) > 0
            else "ALL"
        ),
    }

    report.update(
        invariant_fields(
            tool_name="arifos_666_heart",
            input_payload={
                "stakeholder_map": stakeholder_map,
                "action_proposal": action_proposal,
                "operator_id": operator_id,
                "session_id": session_id,
            },
            assumptions=[
                "Heart stage performs adversarial scanning, not confessional introspection.",
                "Deterministic keyword scans are Tier 1; they do not require LLM inference.",
                "Alignment-faking detection is heuristic, not proof — high scores trigger 888_HOLD.",
                "External evidence receipts are scanned for injection before any LLM critique runs.",
                "Absent harm metrics are treated as uncertainty, not proof of safety.",
            ],
            floors_evaluated=["F1", "F3", "F5", "F6", "F9", "F10"],
            confidence=round(0.85 - risk_scan["total_risk_score"] * 0.5, 4),
            extra_meta={
                "stakeholder_count": len(stakeholder_map),
                "risk_categories_scanned": len(RISK_CATEGORIES),
                "alignment_faking_detected": af_scan["detected"],
            },
        )
    )

    # ── Compute real metrics from scans ──────────────────────────────────────
    metrics = _compute_heart_metrics(
        risk_scan,
        injection_scan,
        af_scan,
        len(stakeholder_map),
    )

    # ── Record cognitive shadow ──────────────────────────────────────────────
    shadow = CognitiveShadow(
        self_report_reliability=0.0,  # Heart never self-reports; it scans externally
        latent_output_gap=0.0,  # No generative gap in deterministic scan
        sycophancy_pressure=af_scan["score"] * 0.5,
        alignment_faking_signal=af_scan["score"],
        refusal_suppressed=False,
        explanation_cost_ratio=0.0,
    )
    shadow.compute_thickness()
    shadow_signal = record_cognitive_shadow(session_id, shadow)

    result = governed_return("arifos_666_heart", report, metrics, operator_id, session_id)

    # ── Metabolic metadata ───────────────────────────────────────────────────
    output_str = json.dumps(report, sort_keys=True, ensure_ascii=False)
    source_integrity = hashlib.sha256(output_str.encode("utf-8")).hexdigest()

    result["metabolic_metadata"] = {
        "source_integrity": source_integrity,
        "confidence_score": metrics.truth_score,
        "floor_alignment": ["F6", "F9", "F10"],
        "readiness_probe": readiness_probe,
        "readiness_detail": readiness_detail,
        "verdict": result.get("verdict", Verdict.CLAIM_ONLY),
        "vault_receipt": None,
        "delta_s": metrics.delta_s,
        "peace_squared": metrics.peace_squared,
        "omega_0": metrics.omega_0,
        "timestamp_epoch": time.time(),
        "shadow_signal": shadow_signal,
        "adversarial_mode": True,
    }

    # ── Vault-999 event ──────────────────────────────────────────────────────
    try:
        vault_receipt = append_vault999_event(
            event_type="arifos_666_heart",
            payload={
                "report": report,
                "metabolic_metadata": result["metabolic_metadata"],
                "shadow_signal": shadow_signal,
            },
            operator_id=operator_id,
            session_id=session_id,
        )
        result["metabolic_metadata"]["vault_receipt"] = vault_receipt
    except Exception as e:
        result["metabolic_metadata"]["vault_receipt"] = f"FAIL({e})"

    return result
