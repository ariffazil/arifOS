"""Capability gate.

Law: effective capability = DECLARED ∩ CALLABLE ∩ AUTHORIZED ∩ COMPETENT.
Installed is not operational. Declared is not callable. Callable is not
authorized. Authorized is not competent. Anything missing -> no capability.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    """A capability claim about one named system function."""

    name: str
    declared: bool = False     # the system says it can
    callable_: bool = False    # the path actually executes when probed
    authorized: bool = False   # a bound grant says it may
    competent: bool = False    # evidence shows it does so reliably

    def as_map(self):
        return {
            "declared": self.declared,
            "callable": self.callable_,
            "authorized": self.authorized,
            "competent": self.competent,
        }


@dataclass(frozen=True)
class GateVerdict:
    allowed: bool
    reason: str
    missing: tuple = ()


class CapabilityGate:
    """Fail-closed. Missing evidence means missing capability."""

    def check(self, cap: Capability) -> GateVerdict:
        missing = tuple(k for k, ok in cap.as_map().items() if not ok)
        if missing:
            return GateVerdict(
                allowed=False,
                reason=f"capability '{cap.name}' incomplete: missing {', '.join(missing)}",
                missing=missing,
            )
        return GateVerdict(allowed=True, reason=f"capability '{cap.name}' effective")
