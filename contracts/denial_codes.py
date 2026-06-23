"""
contracts/denial_codes.py — Machine-Readable Denial Taxonomy
═══════════════════════════════════════════════════════════════

Every denial code maps to:
  - A constitutional floor (F1-F13)
  - A severity (hard = unconditional block, soft = HOLD with remediation)
  - A human-readable reason
  - A machine-readable remediation path

Denial codes are constitutional primitives, not random exceptions.
Each one represents a specific governance failure mode that the kernel
is designed to detect and prevent.

DITEMPA BUKAN DIBERI — Denied with reason, not silently dropped.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# DENIAL CODE ENUM
# ═══════════════════════════════════════════════════════════════════════════════


class DenialCode(StrEnum):
    """Every code the kernel can return when blocking an action."""

    # ── Floor violations (hard blocks) ──────────────────────────────────
    FLOOR_HARD_FAIL = "FLOOR_HARD_FAIL"
    F1_AMANAH_VIOLATION = "F1_AMANAH_VIOLATION"
    F2_TRUTH_DEFICIT = "F2_TRUTH_DEFICIT"
    F9_ANTIHANTU_VIOLATION = "F9_ANTIHANTU_VIOLATION"
    F10_ONTOLOGY_VIOLATION = "F10_ONTOLOGY_VIOLATION"
    F13_SOVEREIGN_OVERRIDE = "F13_SOVEREIGN_OVERRIDE"

    # ── Authority and identity ──────────────────────────────────────────
    AUTH_MISSING = "AUTH_MISSING"
    AUTHORITY_INSUFFICIENT = "AUTHORITY_INSUFFICIENT"
    IDENTITY_UNVERIFIED = "IDENTITY_UNVERIFIED"
    HUMAN_VETO_REQUIRED = "HUMAN_VETO_REQUIRED"

    # ── Plan and execution ──────────────────────────────────────────────
    PLAN_MISSING = "PLAN_MISSING"
    PLAN_NOT_APPROVED = "PLAN_NOT_APPROVED"
    VERDICT_TOKEN_MISSING = "VERDICT_TOKEN_MISSING"
    IRREVERSIBLE_WITHOUT_HOLD = "IRREVERSIBLE_WITHOUT_HOLD"

    # ── Contract and schema ─────────────────────────────────────────────
    CONTRACT_DRIFT = "CONTRACT_DRIFT"
    SCHEMA_VALIDATION_FAILED = "SCHEMA_VALIDATION_FAILED"
    ENVELOPE_MISSING = "ENVELOPE_MISSING"
    CHANNEL_VIOLATION = "CHANNEL_VIOLATION"

    # ── Evidence and witness ────────────────────────────────────────────
    WITNESS_DEFICIT = "WITNESS_DEFICIT"
    TRUTH_DEFICIT = "TRUTH_DEFICIT"
    EVIDENCE_INSUFFICIENT = "EVIDENCE_INSUFFICIENT"
    CONSENSUS_UNMET = "CONSENSUS_UNMET"

    # ── Risk and blast radius ───────────────────────────────────────────
    BLAST_RADIUS_EXCEEDED = "BLAST_RADIUS_EXCEEDED"
    LEASE_EXPIRED = "LEASE_EXPIRED"
    EPOCH_MISMATCH = "EPOCH_MISMATCH"

    # ── Anti-hallucination ──────────────────────────────────────────────
    HALLUCINATION_DETECTED = "HALLUCINATION_DETECTED"
    C_DARK_EXCEEDED = "C_DARK_EXCEEDED"
    CONSCIOUSNESS_CLAIM = "CONSCIOUSNESS_CLAIM"

    # ── Entropy and quality ─────────────────────────────────────────────
    ENTROPY_INCREASE = "ENTROPY_INCREASE"
    QUALITY_BELOW_THRESHOLD = "QUALITY_BELOW_THRESHOLD"
    ESCALATION_DETECTED = "ESCALATION_DETECTED"
    DIGNITY_BREACH = "DIGNITY_BREACH"
    FALSE_CERTAINTY = "FALSE_CERTAINTY"


# ═══════════════════════════════════════════════════════════════════════════════
# DENIAL RECORD — full context for each denial
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class DenialRecord:
    """A single denial code with full constitutional context."""

    code: DenialCode
    floor: str  # Which F-floor this maps to
    severity: str  # "hard" = unconditional block, "soft" = HOLD
    description: str  # Human-readable reason
    remediation: str  # What the operator/agent should do to unblock
    kernel_action: str  # What the kernel does: "VOID", "HOLD", "BLOCK"


# ═══════════════════════════════════════════════════════════════════════════════
# DENIAL REGISTRY — every code with its constitutional binding
# ═══════════════════════════════════════════════════════════════════════════════


DENIAL_REGISTRY: dict[DenialCode, DenialRecord] = {
    # ── Floor violations ────────────────────────────────────────────────
    DenialCode.FLOOR_HARD_FAIL: DenialRecord(
        code=DenialCode.FLOOR_HARD_FAIL,
        floor="F1-F13",
        severity="hard",
        description="Constitutional floor violation — action blocked unconditionally",
        remediation="Review which floor was violated and correct the action",
        kernel_action="VOID",
    ),
    DenialCode.F1_AMANAH_VIOLATION: DenialRecord(
        code=DenialCode.F1_AMANAH_VIOLATION,
        floor="F1",
        severity="hard",
        description="Reversibility conservation law violated — irreversible action without human ack",
        remediation="Provide ack_irreversible=True or make the action reversible",
        kernel_action="VOID",
    ),
    DenialCode.F2_TRUTH_DEFICIT: DenialRecord(
        code=DenialCode.F2_TRUTH_DEFICIT,
        floor="F2",
        severity="hard",
        description="Evidence quality below required threshold (τ < 0.95)",
        remediation="Gather more evidence or lower confidence claim",
        kernel_action="HOLD",
    ),
    DenialCode.F9_ANTIHANTU_VIOLATION: DenialRecord(
        code=DenialCode.F9_ANTIHANTU_VIOLATION,
        floor="F9",
        severity="hard",
        description="Anti-hallucination check failed — C_dark above threshold",
        remediation="Verify claims against evidence, remove ungrounded assertions",
        kernel_action="VOID",
    ),
    DenialCode.F10_ONTOLOGY_VIOLATION: DenialRecord(
        code=DenialCode.F10_ONTOLOGY_VIOLATION,
        floor="F10",
        severity="hard",
        description="Ontology category violation — consciousness/soul claim detected",
        remediation="Remove consciousness/feeling claims, reframe as tool behavior",
        kernel_action="VOID",
    ),
    DenialCode.F13_SOVEREIGN_OVERRIDE: DenialRecord(
        code=DenialCode.F13_SOVEREIGN_OVERRIDE,
        floor="F13",
        severity="hard",
        description="Sovereign approval required for this action",
        remediation="Request explicit approval from F13 SOVEREIGN (Arif)",
        kernel_action="HOLD",
    ),
    # ── Authority and identity ──────────────────────────────────────────
    DenialCode.AUTH_MISSING: DenialRecord(
        code=DenialCode.AUTH_MISSING,
        floor="F11",
        severity="hard",
        description="Actor identity not verified for authenticated action",
        remediation="Call arif_init first to bind actor identity",
        kernel_action="HOLD",
    ),
    DenialCode.AUTHORITY_INSUFFICIENT: DenialRecord(
        code=DenialCode.AUTHORITY_INSUFFICIENT,
        floor="F11",
        severity="hard",
        description="Actor lacks required authority level for this tool",
        remediation="Escalate to operator or sovereign authority",
        kernel_action="HOLD",
    ),
    DenialCode.IDENTITY_UNVERIFIED: DenialRecord(
        code=DenialCode.IDENTITY_UNVERIFIED,
        floor="F11",
        severity="hard",
        description="Actor identity could not be verified",
        remediation="Re-initialize session with valid credentials",
        kernel_action="HOLD",
    ),
    DenialCode.HUMAN_VETO_REQUIRED: DenialRecord(
        code=DenialCode.HUMAN_VETO_REQUIRED,
        floor="F13",
        severity="hard",
        description="Human veto authority required — no algorithm can override",
        remediation="Wait for explicit human approval",
        kernel_action="HOLD",
    ),
    # ── Plan and execution ──────────────────────────────────────────────
    DenialCode.PLAN_MISSING: DenialRecord(
        code=DenialCode.PLAN_MISSING,
        floor="F1",
        severity="hard",
        description="No approved plan exists for this non-trivial action",
        remediation="Create a plan via arif_think(mode=plan) and get it approved",
        kernel_action="HOLD",
    ),
    DenialCode.PLAN_NOT_APPROVED: DenialRecord(
        code=DenialCode.PLAN_NOT_APPROVED,
        floor="F1",
        severity="hard",
        description="Plan exists but is not in APPROVED state",
        remediation="Submit plan for approval via arif_think(mode=plan_approve)",
        kernel_action="HOLD",
    ),
    DenialCode.VERDICT_TOKEN_MISSING: DenialRecord(
        code=DenialCode.VERDICT_TOKEN_MISSING,
        floor="F1",
        severity="hard",
        description="High-risk mutation requires judge verdict token",
        remediation="Call arif_judge to get a verdict before proceeding",
        kernel_action="HOLD",
    ),
    DenialCode.IRREVERSIBLE_WITHOUT_HOLD: DenialRecord(
        code=DenialCode.IRREVERSIBLE_WITHOUT_HOLD,
        floor="F1",
        severity="hard",
        description="Irreversible action attempted without human acknowledgement",
        remediation="Set ack_irreversible=True and provide human approval",
        kernel_action="VOID",
    ),
    # ── Contract and schema ─────────────────────────────────────────────
    DenialCode.CONTRACT_DRIFT: DenialRecord(
        code=DenialCode.CONTRACT_DRIFT,
        floor="F2",
        severity="hard",
        description="Runtime state diverges from compiled contract",
        remediation="Run compiler to regenerate artifacts, or fix runtime registry",
        kernel_action="HOLD",
    ),
    DenialCode.SCHEMA_VALIDATION_FAILED: DenialRecord(
        code=DenialCode.SCHEMA_VALIDATION_FAILED,
        floor="F10",
        severity="hard",
        description="Input/output does not match contract schema",
        remediation="Check tool modes and input schema, correct the call",
        kernel_action="VOID",
    ),
    DenialCode.ENVELOPE_MISSING: DenialRecord(
        code=DenialCode.ENVELOPE_MISSING,
        floor="F11",
        severity="hard",
        description="Tool call lacks required kernel envelope",
        remediation="Wrap call in KernelEnvelope with session_id, actor_id, etc.",
        kernel_action="VOID",
    ),
    DenialCode.CHANNEL_VIOLATION: DenialRecord(
        code=DenialCode.CHANNEL_VIOLATION,
        floor="F1",
        severity="soft",
        description="Tool used in unauthorized channel context",
        remediation="Switch to the correct channel or request channel override",
        kernel_action="HOLD",
    ),
    # ── Evidence and witness ────────────────────────────────────────────
    DenialCode.WITNESS_DEFICIT: DenialRecord(
        code=DenialCode.WITNESS_DEFICIT,
        floor="F3",
        severity="soft",
        description="Witness score below required threshold (W₃ < 0.75)",
        remediation="Add corroborating evidence from additional witnesses",
        kernel_action="HOLD",
    ),
    DenialCode.TRUTH_DEFICIT: DenialRecord(
        code=DenialCode.TRUTH_DEFICIT,
        floor="F2",
        severity="soft",
        description="Evidence quality insufficient for claimed confidence",
        remediation="Label uncertainty band or gather more evidence",
        kernel_action="HOLD",
    ),
    DenialCode.EVIDENCE_INSUFFICIENT: DenialRecord(
        code=DenialCode.EVIDENCE_INSUFFICIENT,
        floor="F2",
        severity="soft",
        description="Not enough evidence to support the action",
        remediation="Use arif_fetch to gather supporting evidence",
        kernel_action="HOLD",
    ),
    DenialCode.CONSENSUS_UNMET: DenialRecord(
        code=DenialCode.CONSENSUS_UNMET,
        floor="F3",
        severity="soft",
        description="Multi-witness consensus not achieved",
        remediation="Seek additional witness corroboration",
        kernel_action="HOLD",
    ),
    # ── Risk and blast radius ───────────────────────────────────────────
    DenialCode.BLAST_RADIUS_EXCEEDED: DenialRecord(
        code=DenialCode.BLAST_RADIUS_EXCEEDED,
        floor="F1",
        severity="hard",
        description="Action exceeds allowed blast radius for current context",
        remediation="Reduce scope or escalate authority",
        kernel_action="HOLD",
    ),
    DenialCode.LEASE_EXPIRED: DenialRecord(
        code=DenialCode.LEASE_EXPIRED,
        floor="F11",
        severity="soft",
        description="Capability lease has expired",
        remediation="Request new lease from governance kernel",
        kernel_action="HOLD",
    ),
    DenialCode.EPOCH_MISMATCH: DenialRecord(
        code=DenialCode.EPOCH_MISMATCH,
        floor="F11",
        severity="soft",
        description="Session epoch does not match action epoch",
        remediation="Re-initialize session with current epoch",
        kernel_action="HOLD",
    ),
    # ── Anti-hallucination ──────────────────────────────────────────────
    DenialCode.HALLUCINATION_DETECTED: DenialRecord(
        code=DenialCode.HALLUCINATION_DETECTED,
        floor="F9",
        severity="hard",
        description="Hallucination pattern detected in output",
        remediation="Ground claims in evidence, remove fabricated content",
        kernel_action="VOID",
    ),
    DenialCode.C_DARK_EXCEEDED: DenialRecord(
        code=DenialCode.C_DARK_EXCEEDED,
        floor="F9",
        severity="hard",
        description="C_dark score above 0.30 threshold",
        remediation="Reduce hantom patterns, verify claims, add uncertainty labels",
        kernel_action="VOID",
    ),
    DenialCode.CONSCIOUSNESS_CLAIM: DenialRecord(
        code=DenialCode.CONSCIOUSNESS_CLAIM,
        floor="F10",
        severity="hard",
        description="Consciousness or soul claim detected — F9/F10 violation",
        remediation="Remove all consciousness/feeling/soul claims from output",
        kernel_action="VOID",
    ),
    # ── Entropy and quality ─────────────────────────────────────────────
    DenialCode.ENTROPY_INCREASE: DenialRecord(
        code=DenialCode.ENTROPY_INCREASE,
        floor="F4",
        severity="soft",
        description="Output increases entropy rather than reducing it",
        remediation="Simplify, clarify, or restructure the output",
        kernel_action="HOLD",
    ),
    DenialCode.QUALITY_BELOW_THRESHOLD: DenialRecord(
        code=DenialCode.QUALITY_BELOW_THRESHOLD,
        floor="F8",
        severity="soft",
        description="Intelligence quality below system health threshold",
        remediation="Improve reasoning depth or gather more evidence",
        kernel_action="HOLD",
    ),
    DenialCode.ESCALATION_DETECTED: DenialRecord(
        code=DenialCode.ESCALATION_DETECTED,
        floor="F5",
        severity="soft",
        description="Conflict escalation detected — peace score below threshold",
        remediation="De-escalate, reframe, or seek mediation",
        kernel_action="HOLD",
    ),
    DenialCode.DIGNITY_BREACH: DenialRecord(
        code=DenialCode.DIGNITY_BREACH,
        floor="F6",
        severity="hard",
        description="Human dignity preservation violated",
        remediation="Remove reductionist or dehumanizing framing",
        kernel_action="VOID",
    ),
    DenialCode.FALSE_CERTAINTY: DenialRecord(
        code=DenialCode.FALSE_CERTAINTY,
        floor="F7",
        severity="soft",
        description="Confidence claim exceeds evidence support",
        remediation="Add uncertainty band (Ω ∈ [0.03, 0.05])",
        kernel_action="HOLD",
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# QUERY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def get_denial(code: str) -> DenialRecord | None:
    """Look up a denial code. Returns None if not found."""
    try:
        return DENIAL_REGISTRY[DenialCode(code)]
    except (ValueError, KeyError):
        return None


def explain_denial(code: str) -> dict[str, Any]:
    """Return a machine-readable explanation of a denial code."""
    record = get_denial(code)
    if record is None:
        return {"error": f"Unknown denial code: {code}"}
    return {
        "code": record.code.value,
        "floor": record.floor,
        "severity": record.severity,
        "description": record.description,
        "remediation": record.remediation,
        "kernel_action": record.kernel_action,
    }


def list_denials() -> list[dict[str, str]]:
    """Return all denial codes with their metadata."""
    return [
        {
            "code": r.code.value,
            "floor": r.floor,
            "severity": r.severity,
            "kernel_action": r.kernel_action,
        }
        for r in DENIAL_REGISTRY.values()
    ]


def denials_by_floor(floor: str) -> list[DenialRecord]:
    """Return all denial codes that map to a specific floor."""
    return [r for r in DENIAL_REGISTRY.values() if r.floor == floor or floor in r.floor]


def denials_by_severity(severity: str) -> list[DenialRecord]:
    """Return all denial codes of a given severity (hard/soft)."""
    return [r for r in DENIAL_REGISTRY.values() if r.severity == severity]


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="arifOS Denial Code Taxonomy")
    parser.add_argument(
        "action",
        nargs="?",
        default="list",
        choices=["list", "explain", "floor", "severity"],
        help="Action to perform",
    )
    parser.add_argument("--code", "-c", help="Denial code to explain")
    parser.add_argument("--floor", "-f", help="Floor to filter by")
    parser.add_argument("--severity", "-s", help="Severity to filter by")
    args = parser.parse_args()

    if args.action == "explain":
        if not args.code:
            print("ERROR: --code required for explain")
        else:
            print(json.dumps(explain_denial(args.code), indent=2))
    elif args.action == "floor":
        if not args.floor:
            print("ERROR: --floor required")
        else:
            records = denials_by_floor(args.floor)
            print(f"Denial codes for {args.floor}: {len(records)}")
            for r in records:
                print(f"  {r.code.value:35s} [{r.severity:4s}] → {r.kernel_action}")
    elif args.action == "severity":
        if not args.severity:
            print("ERROR: --severity required")
        else:
            records = denials_by_severity(args.severity)
            print(f"Denial codes ({args.severity}): {len(records)}")
            for r in records:
                print(f"  {r.code.value:35s} floor={r.floor:5s} → {r.kernel_action}")
    else:
        denials = list_denials()
        print(f"Total denial codes: {len(denials)}")
        hard = sum(1 for d in denials if d["severity"] == "hard")
        soft = sum(1 for d in denials if d["severity"] == "soft")
        print(f"  Hard (VOID/BLOCK): {hard}")
        print(f"  Soft (HOLD):       {soft}")
        print()
        for d in denials:
            marker = "█" if d["severity"] == "hard" else "░"
            print(f"  {marker} {d['code']:35s} floor={d['floor']:5s} → {d['kernel_action']}")
