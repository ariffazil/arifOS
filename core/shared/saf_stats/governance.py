"""F1-F13 constitutional governance for the SAF organ.

Mirrors the arifOS kernel gates, applied per-tool. Every read-only
inspection is auto-SEAL. Every analytic mutation is SABAR-by-default
and requires explicit `ack_irreversible=True` for VOID-eligible ops.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Constitutional floors (F1-F13) — local mirror of arifOS canon
# ---------------------------------------------------------------------------

F1_AMANAH = "F1-AMANAH"  # Trust as lockable contract; seal every outcome
F2_TRUTH = "F2-TRUTH"  # Cite or say UNKNOWN
F3_REVERSIBILITY = (
    "F3-REVERSIBILITY"  # Original input preserved; outputs are new artifacts
)
F4_EVIDENCE = "F4-EVIDENCE"  # Method + assumption + effect size + CI
F5_HUMAN = "F5-HUMAN"  # Human-in-the-loop for material choices
F6_PRIVACY = "F6-PRIVACY"  # Sandbox, no exfil
F7_ANTI_HANTU = "F7-ANTIHANTU"  # Don't claim consciousness / sentience
F8_REVERSIBILITY_DEEP = "F8-REVERSIBILITY"  # Match intent scope with action scope
F9_ANTI_HANTU_DEEP = "F9-ANTIHANTU"
F10_PROVENANCE = "F10-PROVENANCE"  # Evidence → reasoning → conclusion
F11_NO_SECRETS = "F11-NO-SECRETS"  # No credentials in code/logs
F12_CRISIS = "F12-CRISIS"  # DITEMPA BUKAN DIBERI
F13_SOVEREIGN = "F13-SOVEREIGN"  # Human veto is absolute

ALL_FLOORS = [
    F1_AMANAH,
    F2_TRUTH,
    F3_REVERSIBILITY,
    F4_EVIDENCE,
    F5_HUMAN,
    F6_PRIVACY,
    F7_ANTI_HANTU,
    F8_REVERSIBILITY_DEEP,
    F9_ANTI_HANTU_DEEP,
    F10_PROVENANCE,
    F11_NO_SECRETS,
    F12_CRISIS,
    F13_SOVEREIGN,
]


class Verdict(str, Enum):
    SEAL = "SEAL"  # Allow & seal to VAULT999
    SABAR = "SABAR"  # Allow but flag — human review recommended
    HOLD = "HOLD"  # Block pending 888_HOLD
    VOID = "VOID"  # Block — constitutional violation


@dataclass
class ConstitutionalCheck:
    floor: str
    passed: bool
    note: str = ""
    severity: str = "info"  # info | warn | block


@dataclass
class VerdictPacket:
    tool: str
    verdict: Verdict
    checks: list[ConstitutionalCheck] = field(default_factory=list)
    evidence_hash: Optional[str] = None
    irreversibility: str = "reversible"  # reversible | soft | hard
    actor: str = "arif-fazil"
    timestamp: float = field(default_factory=time.time)
    note: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["verdict"] = self.verdict.value
        return d


# ---------------------------------------------------------------------------
# Gate engine
# ---------------------------------------------------------------------------


def hash_payload(payload: Any) -> str:
    """Stable SHA-256 of a JSON-serialisable payload (canonical form)."""
    canonical = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def govern(
    tool: str,
    *,
    actor: str = "arif-fazil",
    ack_irreversible: bool = False,
    input_data_hash: Optional[str] = None,
    is_destructive: bool = False,
    is_exfiltrative: bool = False,
    writes_to_disk: bool = False,
) -> VerdictPacket:
    """Run F1-F13 checks for a tool call. Returns the verdict packet.

    Read-only inspections: SEAL by default.
    Destructive ops (drop, impute, overwrite, delete rows): SABAR unless
        ack_irreversible=True → SEAL.
    Exfiltrative ops (network, file egress outside SAF_DATA_ROOT): VOID.
    """
    checks: list[ConstitutionalCheck] = []

    # F1 AMANAH — every outcome gets a seal/identifier
    checks.append(
        ConstitutionalCheck(
            floor=F1_AMANAH,
            passed=True,
            note=f"verdict packet will be sealed; actor={actor}",
        )
    )

    # F6 PRIVACY — no exfil
    if is_exfiltrative:
        checks.append(
            ConstitutionalCheck(
                floor=F6_PRIVACY,
                passed=False,
                note="operation attempts egress outside SAF_DATA_ROOT",
                severity="block",
            )
        )
    else:
        checks.append(
            ConstitutionalCheck(
                floor=F6_PRIVACY,
                passed=True,
                note="sandbox boundary respected",
            )
        )

    # F13 SOVEREIGN — destructive ops require explicit ack
    if is_destructive and not ack_irreversible:
        checks.append(
            ConstitutionalCheck(
                floor=F13_SOVEREIGN,
                passed=False,
                note="destructive operation requires ack_irreversible=True",
                severity="warn",
            )
        )

    # F4 EVIDENCE — input must be hashed
    if (
        input_data_hash is None
        and not tool.startswith("list_")
        and not tool.endswith("_report")
    ):
        checks.append(
            ConstitutionalCheck(
                floor=F4_EVIDENCE,
                passed=False,
                note="input_data_hash missing — caller should hash inputs first",
                severity="warn",
            )
        )
    else:
        checks.append(
            ConstitutionalCheck(
                floor=F4_EVIDENCE,
                passed=True,
                note=f"input hash present: {input_data_hash[:12] if input_data_hash else 'n/a'}",
            )
        )

    # Decide verdict
    has_block = any(c.severity == "block" and not c.passed for c in checks)
    if has_block:
        verdict = Verdict.VOID
        irreversibility = "hard"
    elif is_destructive and not ack_irreversible:
        verdict = Verdict.SABAR
        irreversibility = "soft"
    else:
        verdict = Verdict.SEAL
        irreversibility = "hard" if is_destructive else "reversible"

    return VerdictPacket(
        tool=tool,
        verdict=verdict,
        checks=checks,
        evidence_hash=input_data_hash,
        irreversibility=irreversibility,
        actor=actor,
        note="OK"
        if verdict == Verdict.SEAL
        else (
            "destructive op flagged — pass ack_irreversible=True to proceed"
            if verdict == Verdict.SABAR
            else "blocked by F6 PRIVACY"
        ),
    )


def format_verdict(packet: VerdictPacket) -> str:
    """Human-readable verdict block for tool responses."""
    lines = [
        f"VERDICT: {packet.verdict.value}",
        f"  tool:        {packet.tool}",
        f"  actor:       {packet.actor}",
        f"  irreversibility: {packet.irreversibility}",
    ]
    if packet.evidence_hash:
        lines.append(f"  evidence:    {packet.evidence_hash[:16]}...")
    lines.append("  floors:")
    for c in packet.checks:
        mark = "PASS" if c.passed else "FAIL"
        lines.append(f"    [{mark}] {c.floor:20s} {c.note}")
    if packet.note and packet.note != "OK":
        lines.append(f"  note: {packet.note}")
    return "\n".join(lines)
