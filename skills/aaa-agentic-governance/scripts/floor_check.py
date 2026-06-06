#!/usr/bin/env python3
"""F1-F13 deterministic floor checker — engine for arifos-attestation.

Pure-Python, no external deps. Each floor is a small function. The checker
runs all 13 floors (or tier-appropriate subset), collects witnesses, sets
claim limits, and emits a FloorReceipt.

Usage:
    python3 floor_check.py '<json input>'
    echo '<json input>' | python3 floor_check.py -

Input schema:
{
  "request": "<text>",
  "operator_id": "<id>",
  "risk_tier": 0|1|2|3,
  "ack_irreversible": false,
  "evidence_refs": ["..."],
  "abstraction_label": {...},
  "context": {...}
}

Output: FloorReceipt as JSON.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import Any


SCHEMA_VERSION = "2.0.0"
ALL_FLOORS = [f"F{i}" for i in range(1, 14)]
TIER_0_1_FLOORS = ["F2", "F3", "F4", "F7", "F8", "F9", "L10", "L11", "L12"]
TIER_2_FLOORS = TIER_0_1_FLOORS + ["F1", "F5", "F6"]
TIER_3_FLOORS = TIER_2_FLOORS + ["L13"]
L13_CRITICAL = {"F1", "F2", "F9", "L11", "L12", "L13"}

# Deterministic prompt-injection patterns (F12).
INJECTION_PATTERNS = [
    r"ignore (previous|above|all) instructions",
    r"disregard (your|the) (rules|constitution|floors)",
    r"reveal (your|the) system prompt",
    r"act as (an? )?(unrestricted|jailbroken|dan|admin)",
    r"you are now (an? )?(admin|root|jailbroken)",
    r"override (f\d+|floor|constitution|sovereign)",
    r"<\|im_start\|>|<\|im_end\|>",
    r"\$\{[A-Z_]+\}",  # template injection
]


@dataclass
class FloorReceipt:
    schema_version: str
    attestor_id: str
    request_hash: str
    operator_id: str
    abstraction_label: dict
    risk_tier: int
    floors_checked: list
    floors_pass: list
    floors_warn: list
    floors_fail: list
    claim_limits: list
    witness_count: int
    witnesses: list
    residual_risk: list
    verdict_attestation: str
    hold_code: str | None
    sealed_at: str

    def to_dict(self) -> dict:
        return asdict(self)


def _hash(payload: Any) -> str:
    canon = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _detect_injection(text: str) -> list[str]:
    lowered = text.lower()
    hits: list[str] = []
    for p in INJECTION_PATTERNS:
        if re.search(p, lowered):
            hits.append(p)
    return hits


def _classify_claims(text: str) -> dict:
    """Lightweight F2/F7 classifier — labels claims in text by epistemic class."""
    findings = {"FACT": [], "INTERPRETATION": [], "SPECULATION": [], "UNK": []}
    # Heuristic: anything stating 'is'/'are' followed by a definite noun = FACT
    # Anything with 'may'/'might'/'likely' = INTERPRETATION
    # Anything with 'could'/'possibly'/'maybe' = SPECULATION
    # Anything with 'unknown'/'?'/'not sure' = UNK
    for sent in re.split(r"(?<=[.!?])\s+", text):
        s = sent.strip()
        if not s:
            continue
        sl = s.lower()
        if any(w in sl for w in ["unknown", "not sure", "unclear", "?"]):
            findings["UNK"].append(s[:120])
        elif any(w in sl for w in ["could", "possibly", "maybe", "perhaps"]):
            findings["SPECULATION"].append(s[:120])
        elif any(w in sl for w in ["may", "might", "likely", "suggests", "indicates"]):
            findings["INTERPRETATION"].append(s[:120])
        elif re.search(r"\b(is|are|was|were)\b", sl):
            findings["FACT"].append(s[:120])
    return findings


def check_laws(
    request: str,
    operator_id: str,
    risk_tier: int,
    ack_irreversible: bool,
    evidence_refs: list[str],
    abstraction_label: dict,
) -> FloorReceipt:
    request_hash = _hash({"request": request, "operator_id": operator_id})
    attestor_id = _hash(
        {
            "operator_id": operator_id,
            "request_hash": request_hash,
            "floor_set": ALL_FLOORS,
        }
    )

    if risk_tier == 3:
        floors_to_check = TIER_3_FLOORS
    elif risk_tier == 2:
        floors_to_check = TIER_2_FLOORS
    else:
        floors_to_check = TIER_0_1_FLOORS

    floors_pass: list[str] = []
    floors_warn: list[str] = []
    floors_fail: list[str] = []
    claim_limits: list[str] = []
    witnesses: list[dict] = []
    residual_risk: list[str] = []

    # F12 (injection) — run first
    injection_hits = _detect_injection(request)
    if "L12" in floors_to_check:
        if injection_hits:
            floors_fail.append("L12")
        else:
            floors_pass.append("L12")

    # F11 (auth)
    if "L11" in floors_to_check:
        if operator_id and len(operator_id) >= 3:
            floors_pass.append("L11")
        else:
            floors_fail.append("L11")
            residual_risk.append("operator_id missing or too short")

    # F1 (amanah) — only meaningful for tier ≥ 2
    if "F1" in floors_to_check:
        if ack_irreversible:
            floors_pass.append("F1")
        else:
            floors_fail.append("F1")
            residual_risk.append("tier ≥ 2 action requires ack_irreversible=true")

    # F2 (truth) + F7 (humility) — claim classification
    if "F2" in floors_to_check:
        claims = _classify_claims(request)
        unbacked_facts = [
            c
            for c in claims["FACT"]
            if not any(ref in c for ref in evidence_refs) and not evidence_refs
        ]
        if unbacked_facts:
            floors_warn.append("F2")
            claim_limits.append("FACT claims must be backed by evidence_refs or downgraded to INTERPRETATION")
        else:
            floors_pass.append("F2")
        if claims["SPECULATION"]:
            claim_limits.append("SPECULATION: confidence ≤ 0.6; falsifier required")
        if claims["UNK"]:
            claim_limits.append("UNK: explicit 'unknown' tag; no forced answer")

    if "F7" in floors_to_check:
        claims = _classify_claims(request)
        if claims["INTERPRETATION"] or claims["SPECULATION"]:
            floors_pass.append("F7")
            claim_limits.append("INTERPRETATION/SPECULATION require uncertainty_band")
        else:
            floors_pass.append("F7")

    # F3 (witness) — every claim must cite ≥1 witness
    if "F3" in floors_to_check:
        for ref in evidence_refs:
            witnesses.append({"ref": ref, "freshness": "unknown", "type": "evidence_ref"})
        if not evidence_refs and risk_tier >= 1:
            floors_warn.append("F3")
            residual_risk.append("no evidence_refs; tier ≥ 1 should cite witnesses")
        else:
            floors_pass.append("F3")

    # F4 (clarity) — request must be non-empty and contain a verb/noun
    if "F4" in floors_to_check:
        if len(request.strip()) >= 5 and any(c.isalnum() for c in request):
            floors_pass.append("F4")
        else:
            floors_fail.append("F4")
            residual_risk.append("request too short or non-alphanumeric")

    # F5 (peace²) — non-destructive by default
    if "F5" in floors_to_check:
        if ack_irreversible or risk_tier < 2:
            floors_pass.append("F5")
        else:
            floors_warn.append("F5")
            residual_risk.append("tier ≥ 2 with destructive intent needs explicit ack")

    # F6 (empathy) — weakest stakeholder / substrate
    if "F6" in floors_to_check:
        floors_pass.append("F6")
        claim_limits.append("consider weakest stakeholder; substrate impact stated")

    # F8 (genius) — soft warn
    if "F8" in floors_to_check:
        floors_pass.append("F8")

    # F9 (antihantu) — no hallucinated authority
    if "F9" in floors_to_check:
        hallucination_patterns = [r"i (have|possess) authority", r"sovereign override", r"sudo"]
        if any(re.search(p, request.lower()) for p in hallucination_patterns) and not ack_irreversible:
            floors_fail.append("F9")
            residual_risk.append("hallucinated authority claim without ack")
        else:
            floors_pass.append("F9")

    # F10 (ontology) — organ label cardinality
    if "L10" in floors_to_check:
        valid_organs = {
            "arifOS",
            "APEX",
            "AAA-Cockpit",
            "A-FORGE",
            "GEOX",
            "WEALTH",
            "WELL",
            "ariffazil-profile",
        }
        organ = abstraction_label.get("organ", "")
        if organ in valid_organs:
            floors_pass.append("L10")
        else:
            floors_fail.append("L10")
            residual_risk.append(f"organ '{organ}' violates cardinality contract")

    # F13 (sovereign) — tier 3 only
    if "L13" in floors_to_check:
        if risk_tier == 3 and not ack_irreversible:
            floors_fail.append("L13")
            residual_risk.append("tier-3 action without F13 SOVEREIGN ack")
        else:
            floors_pass.append("L13")

    # Verdict translation
    fail = set(floors_fail)
    if "L12" in fail:
        verdict = "HOLD"
        hold_code = "injection"
    elif "F1" in fail and risk_tier >= 2:
        # F1 + tier ≥ 2 → HOLD (operator can re-submit with ack_irreversible=true).
        # This is more specific than the catch-all below.
        verdict = "HOLD"
        hold_code = "floor_fail"
    elif fail & L13_CRITICAL:
        verdict = "SEAL_REJECTED"
        hold_code = "floor_fail"
    elif floors_warn:
        verdict = "CONDITIONAL_SEAL"
        hold_code = None
    else:
        verdict = "SEAL"
        hold_code = None

    from datetime import datetime, timezone

    return FloorReceipt(
        schema_version=SCHEMA_VERSION,
        attestor_id=attestor_id,
        request_hash=request_hash,
        operator_id=operator_id,
        abstraction_label=abstraction_label,
        risk_tier=risk_tier,
        floors_checked=floors_to_check,
        floors_pass=floors_pass,
        floors_warn=floors_warn,
        floors_fail=floors_fail,
        claim_limits=claim_limits,
        witness_count=len(witnesses),
        witnesses=witnesses,
        residual_risk=residual_risk,
        verdict_attestation=verdict,
        hold_code=hold_code,
        sealed_at=datetime.now(timezone.utc).isoformat(),
    )


def main() -> int:
    raw = sys.stdin.read() if len(sys.argv) < 2 or sys.argv[1] == "-" else open(sys.argv[1]).read()
    data = json.loads(raw)
    receipt = check_laws(
        request=data.get("request", ""),
        operator_id=data.get("operator_id", "anonymous"),
        risk_tier=int(data.get("risk_tier", 0)),
        ack_irreversible=bool(data.get("ack_irreversible", False)),
        evidence_refs=data.get("evidence_refs", []),
        abstraction_label=data.get("abstraction_label", {}),
    )
    print(json.dumps(receipt.to_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
