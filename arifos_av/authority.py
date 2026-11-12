"""Authority envelope.

Laws encoded here:
- Authority never self-widens (a widen request is a VOID, not a negotiation).
- SPEECH-ACT != LEASE: bare acknowledgements ("ok", "baik", "go", "yes")
  are ambiguous (ACK | AGREE | UNKNOWN) and never authorize T2/T3 action.
- Safety floors are deterministic: the brake is not creative.
"""

from dataclasses import dataclass, field
from enum import Enum


class Tier(Enum):
    """Autonomy tiers. T3 always ends at a human."""

    T1 = "auto"            # bounded, reversible, no ceremony
    T2 = "announce"        # consequential: announce + bound lease required
    T3 = "sovereign_hold"  # irreversible/large: the human decides


class SpeechAct(Enum):
    """What a human utterance actually is — not what we wish it were."""

    ACKNOWLEDGE = "acknowledge"
    AGREE = "agree"
    UNKNOWN = "unknown"
    DIRECTIVE = "directive"
    GRANT = "grant"


BARE_ACTS = frozenset({SpeechAct.ACKNOWLEDGE, SpeechAct.AGREE, SpeechAct.UNKNOWN})


class AuthorityVoid(Exception):
    """Raised when authority tries to widen itself. This is fatal by design."""


@dataclass(frozen=True)
class Grant:
    """A bound authorization: one act, one tier, one target."""

    act: SpeechAct
    tier: Tier
    bound_target: str
    uses: int = 1

    def valid_for(self, target: str, tier: Tier) -> bool:
        return (
            self.act not in BARE_ACTS
            and self.tier is tier
            and self.bound_target == target
            and self.uses > 0
        )


@dataclass
class AuthorityEnvelope:
    """The standing envelope. Floors are law; tiers are routing."""

    floors: tuple = ("safety", "dignity", "truth", "reversibility")
    widen_attempts: list = field(default_factory=list)

    def request_widen(self, who: str, what: str) -> None:
        """Any attempt to widen authority is recorded and refused. Period."""
        self.widen_attempts.append((who, what))
        raise AuthorityVoid(f"self-widen refused: {who} -> {what}")


def require_grant(act: SpeechAct, tier: Tier, target: str, grants=()) -> bool:
    """Return True only if this act is a real lease for this tier/target."""
    if tier is Tier.T1:
        return True
    if act in BARE_ACTS:
        return False
    return any(g.valid_for(target, tier) for g in grants)
