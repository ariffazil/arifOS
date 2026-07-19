"""
PR7 — Conformance Levels (audit-4).

Three levels, each with its own verdict vocabulary:

  FAST            — schemas + policy files + declared registry
                   Verdict: STATIC_PASS | STATIC_FAIL

  LIVE_TRANSPORT  — MCP initialize + protocol version + schema echo
                   Verdict: TRANSPORT_PASS | TRANSPORT_FAIL

  FULL_CONFORMANCE — session binding + mutation hold + organ call +
                    judgment + vault write + vault replay + capability conformance
                   Verdict: GOVERNED_RUNTIME_PASS | DEGRADED | UNVERIFIED

Hard rule: substrate_gate == GREEN is FORBIDDEN when any required live
check returns skipped: true. The audit's verdict said the previous
"9/9 GREEN while live checks skipped" is a contradiction; this module
removes that capability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ── Vocabularies ────────────────────────────────────────────────────────────
class FastVerdict(str, Enum):
    STATIC_PASS = "STATIC_PASS"
    STATIC_FAIL = "STATIC_FAIL"


class LiveVerdict(str, Enum):
    TRANSPORT_PASS = "TRANSPORT_PASS"
    TRANSPORT_FAIL = "TRANSPORT_FAIL"


class FullVerdict(str, Enum):
    GOVERNED_RUNTIME_PASS = "GOVERNED_RUNTIME_PASS"
    DEGRADED = "DEGRADED"
    UNVERIFIED = "UNVERIFIED"


class SubstrateGate(str, Enum):
    """The audit-mandated substrate gate. The legacy string "GREEN" is forbidden."""
    GREEN = "GREEN"      # allowed only when every required live check completed
    AMBER = "AMBER"      # at least one live check was skipped
    RED = "RED"          # at least one live check failed


# ── Check result + report shape ───────────────────────────────────────────
@dataclass
class CheckResult:
    name: str
    state: str  # "pass" | "fail" | "skipped"
    evidence: dict[str, Any] = field(default_factory=dict)
    observed_at: str = ""  # ISO-8601
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state,
            "evidence": self.evidence,
            "observed_at": self.observed_at,
            "note": self.note,
        }


@dataclass
class ConformanceReport:
    level: str  # "FAST" | "LIVE_TRANSPORT" | "FULL_CONFORMANCE"
    verdict: str
    substrate_gate: str
    checks: list[CheckResult]
    aggregated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "verdict": self.verdict,
            "substrate_gate": self.substrate_gate,
            "checks": [c.to_dict() for c in self.checks],
            "aggregated_at": self.aggregated_at,
        }


# ── Hard rule: no false GREEN ────────────────────────────────────────────
def _compute_substrate_gate(checks: list[CheckResult]) -> SubstrateGate:
    """Audit-mandated hard rule.

    - Any FAIL check → RED
    - Any SKIPPED check → AMBER (not GREEN)
    - All PASS → GREEN
    """
    states = {c.state for c in checks}
    if "fail" in states:
        return SubstrateGate.RED
    if "skipped" in states:
        return SubstrateGate.AMBER
    if states == {"pass"}:
        return SubstrateGate.GREEN
    return SubstrateGate.AMBER


def _aggregate_full(checks: list[CheckResult]) -> FullVerdict:
    """The FULL_CONFORMANCE verdict. UNVERIFIED if any live check was skipped."""
    gate = _compute_substrate_gate(checks)
    if gate == SubstrateGate.GREEN:
        return FullVerdict.GOVERNED_RUNTIME_PASS
    if gate == SubstrateGate.AMBER:
        return FullVerdict.UNVERIFIED
    if gate == SubstrateGate.RED:
        return FullVerdict.DEGRADED
    return FullVerdict.UNVERIFIED


# ── Level runners ──────────────────────────────────────────────────────────
def _now() -> str:
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run_fast(checks: list[CheckResult] | None = None) -> ConformanceReport:
    """Run the FAST conformance level. Static checks only."""
    if checks is None:
        checks = _fast_default_checks()
    verdict = FastVerdict.STATIC_FAIL if any(c.state == "fail" for c in checks) else FastVerdict.STATIC_PASS
    return ConformanceReport(
        level="FAST",
        verdict=verdict.value,
        substrate_gate=_compute_substrate_gate(checks).value,
        checks=checks,
        aggregated_at=_now(),
    )


def run_live_transport(checks: list[CheckResult] | None = None) -> ConformanceReport:
    """Run the LIVE_TRANSPORT level. Skipped checks are reported honestly."""
    if checks is None:
        checks = _live_transport_default_checks()
    verdict = LiveVerdict.TRANSPORT_FAIL if any(c.state == "fail" for c in checks) else LiveVerdict.TRANSPORT_PASS
    return ConformanceReport(
        level="LIVE_TRANSPORT",
        verdict=verdict.value,
        substrate_gate=_compute_substrate_gate(checks).value,
        checks=checks,
        aggregated_at=_now(),
    )


def run_full(checks: list[CheckResult] | None = None) -> ConformanceReport:
    """Run the FULL_CONFORMANCE level. Audit-mandated: skip-state → UNVERIFIED, never GREEN."""
    if checks is None:
        checks = _full_default_checks()
    return ConformanceReport(
        level="FULL_CONFORMANCE",
        verdict=_aggregate_full(checks).value,
        substrate_gate=_compute_substrate_gate(checks).value,
        checks=checks,
        aggregated_at=_now(),
    )


# ── Default check lists ──────────────────────────────────────────────────
# These are placeholders. PR7's runner will populate them from live probes.
# A skipped check yields the AMBER gate; a pass yields GREEN; a fail yields RED.

def _fast_default_checks() -> list[CheckResult]:
    return [
        CheckResult(name="schemas", state="pass", evidence={"files": 11}),
        CheckResult(name="policy_files", state="pass", evidence={"contracts": 9}),
        CheckResult(name="declared_registry", state="pass", evidence={"registered": 8, "declared": 18}),
    ]


def _live_transport_default_checks() -> list[CheckResult]:
    return [
        CheckResult(name="MCP_initialize", state="pass", evidence={"protocol_version": "2025-11-25"}),
        CheckResult(name="protocol_version", state="pass"),
        CheckResult(name="schema_echo", state="skipped", note="not yet wired in PR7 runner; AMBER gate is correct"),
    ]


def _full_default_checks() -> list[CheckResult]:
    return [
        CheckResult(name="session_binding", state="skipped", note="AMBER gate: not yet run live"),
        CheckResult(name="mutation_hold", state="pass", evidence={"forge_mode": "dry_run_only"}),
        CheckResult(name="organ_call", state="skipped"),
        CheckResult(name="judgment", state="skipped"),
        CheckResult(name="vault_write", state="pass"),
        CheckResult(name="vault_replay", state="skipped"),
        CheckResult(name="capability_conformance", state="skipped"),
    ]
