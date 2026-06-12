"""
arifosmcp.constitution — Machine-importable Gödel Lock + Strange Loop + Anti-Beautiful-One.

The doctrine is the philosophy. This module is the executable form.
Every agent spec, every MCP tool handler, every kernel gate MUST import
and enforce the 7 axioms in godel_lock.yaml.

Doctrine ref: /root/arifOS/static/arifos/theory/001/000_GODEL_LOCK_AND_ANTI_UNIVERSE_25.md
Sealed: 2026-06-12 by 888_Judge.
Authority: Muhammad Arif bin Fazil (F13 SOVEREIGN).

DITEMPA BUKAN DIBERI — the agent speaks like a mirror; it is forbidden from being a court.
"""
from pathlib import Path
from typing import List, Dict, Any
import yaml

_LOCK_PATH = Path(__file__).parent / "godel_lock.yaml"
GODEL_LOCK_RAW: Dict[str, Any] = yaml.safe_load(_LOCK_PATH.read_text())

# The 7 irreducible axioms
GODEL_AXIOMS: List[Dict[str, Any]] = GODEL_LOCK_RAW["axioms"]
GODEL_META: List[Dict[str, Any]] = GODEL_LOCK_RAW["meta"]
REQUIRED_AXIOM_IDS: set = {"G1", "G2", "G3", "G4", "G5", "G6", "G7"}


class GodelLockIncomplete(RuntimeError):
    """Raised when an agent spec or kernel gate is missing a required axiom."""


def assert_lock_complete() -> None:
    """
    Boot-time invariant: every agent spec, every kernel gate must include all 7 axioms.
    Missing any = the spec is void at boot. The kernel refuses to start.
    """
    present = {a["id"] for a in GODEL_AXIOMS}
    missing = REQUIRED_AXIOM_IDS - present
    if missing:
        raise GodelLockIncomplete(
            f"Gödel lock incomplete: missing axioms {missing}. "
            f"Refusing to boot. See {REQUIRED_AXIOM_IDS} for the irreducible set."
        )


def get_axiom(axiom_id: str) -> Dict[str, Any]:
    """Return the full axiom dict for the given id (e.g. 'G3')."""
    for a in GODEL_AXIOMS:
        if a["id"] == axiom_id:
            return a
    raise KeyError(f"Unknown axiom id: {axiom_id}")


def is_self_authorized_failure(cause: str) -> bool:
    """
    Check whether a given failure cause is a self-authorization violation
    (the anti-Beautiful-One invariant). Returns True for any cause listed in
    a G1-G7 axiom's failure_cause field.
    """
    for a in GODEL_AXIOMS:
        if cause == a.get("failure_cause"):
            return True
    return False


def get_violation_verdict(cause: str) -> str:
    """
    Return the verdict the kernel should emit when an action is blocked
    because it would violate a Gödel lock axiom.
    """
    for a in GODEL_AXIOMS:
        if cause == a.get("failure_cause"):
            return a.get("failure_verdict", "HOLD")
    return "HOLD"  # default safe


# =============================================================================
# Boot-time self-check
# =============================================================================

# When this module is imported, perform the assert_lock_complete check.
# If the YAML is missing or incomplete, the kernel refuses to import.
assert_lock_complete()


__all__ = [
    "check_godel_lock",
    "GodelLockViolation",
    "explain_lock",
    "GODEL_LOCK_RAW",
    "GODEL_AXIOMS",
    "GODEL_META",
    "REQUIRED_AXIOM_IDS",
    "GodelLockIncomplete",
    "assert_lock_complete",
    "get_axiom",
    "is_self_authorized_failure",
    "get_violation_verdict",
]

from .runtime_hook import check_godel_lock, GodelLockViolation, explain_lock

