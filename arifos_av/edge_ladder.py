"""Bounded fallback ladder.

When the primary lane fails: one independent alternative, then one
forensic attempt, then an honest stop. Never sweep every lane, never
replace real content with metadata or guesses.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LadderResult:
    status: str   # resolved | forensic | stopped
    lane: str
    note: str


class BoundedLadder:
    def __init__(self, primary, alternative, forensic):
        self.lanes = (
            ("primary", primary),
            ("alternative", alternative),
            ("forensic", forensic),
        )

    def run(self, task: str) -> LadderResult:
        last_note = "no lane attempted"
        for name, fn in self.lanes:
            try:
                out = fn(task)
            except Exception as exc:  # lane broke: record, move one step
                last_note = f"{name} failed: {exc}"
                continue
            if out:
                status = "resolved" if name != "forensic" else "forensic"
                return LadderResult(status, name, str(out))
            last_note = f"{name} returned empty"
        return LadderResult("stopped", "none", f"honest stop; blind receipt; {last_note}")
