"""Contract: Artifact.timestamp admits the producer's ISO-8601 form.

F4 defect (2026-11-05, sibling report rep-f4795259ff0f, independently
reproduced by 333-AGI via arif_memory remember -> SAFE_VOID_FALLBACK
float_parsing): verdict_wrapper.forge_verdict feeds ISO strings into
Artifact(timestamp) while the model declared float, blocking every
forge_verdict caller server-side.

Invariant under test: both forms validate; no consumer reads .timestamp
arithmetically (grep-proven zero hits), so widening the field breaks nothing.
"""

from __future__ import annotations

from arifosmcp.contracts.artifacts import Artifact


def test_artifact_accepts_iso_timestamp() -> None:
    a = Artifact(
        type="generic",
        creator_id="333-AGI",
        session_id="test",
        timestamp="2026-11-05T09:18:22.053322+00:00",
    )
    assert a.timestamp == "2026-11-05T09:18:22.053322+00:00"


def test_artifact_still_accepts_float_timestamp() -> None:
    a = Artifact(
        type="generic", creator_id="333-AGI", session_id="test", timestamp=1793851722.05
    )
    assert a.timestamp == 1793851722.05
