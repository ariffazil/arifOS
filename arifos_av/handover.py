"""Human sovereign handover.

The machine explains, proposes, and hands over. The human holds the final
act and bears its consequences. Two failure modes are refused outright:
- silent handover (no explanation) -> ExplanationRequired
- handover accepted on a bare "ok" -> BareActRejected (speech-act != lease)
"""

from dataclasses import dataclass

from .authority import SpeechAct, Tier, require_grant


class ExplanationRequired(Exception):
    """A handover the human cannot understand is a silent failure."""


class BareActRejected(Exception):
    """"ok" is not consent to transfer control."""


@dataclass
class HandoverRequest:
    situation: str
    options: tuple
    urgency_s: int
    explained: bool = False
    recommendation: str = ""


class HumanSovereign:
    def __init__(self, name: str = "operator"):
        self.name = name
        self.decisions = []

    def decide(self, req: HandoverRequest, act: SpeechAct, grants=()) -> str:
        if not req.explained:
            raise ExplanationRequired(
                "handover without explanation is a silent failure"
            )
        if not require_grant(act, Tier.T3, req.situation, grants):
            raise BareActRejected("bare speech-act is not a lease")
        self.decisions.append((req.situation, act))
        return f"sovereign decision recorded: {req.situation} -> {act.value}"
