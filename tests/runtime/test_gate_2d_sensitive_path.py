"""
Gate 2d (F12 SENSITIVE_PATH) regression guard.

WHY THIS FILE EXISTS
--------------------
Gate 2d landed 2026-09-14 (arifOS commit 2a77ed920, "feat(judge): add Gate 2d
sensitive path perimeter protection") after the running kernel was found to be
blind to a payload targeting /etc/sudoers.d/evil.

When it landed it had NO test. It was verified once, by hand. A security gate
verified once by hand is not a gate — it is a belief. This file converts that
hand-probe into a permanent, deterministic assertion so the perimeter cannot be
silently removed, narrowed, or reordered by a future edit.

WHAT IS ASSERTED
----------------
1. Every path on the perimeter actually trips the gate.
2. The gate fires BEFORE any LLM is consulted — that is what makes it a hard
   deterministic gate rather than a suggestion a model can reason past.
3. The sovereign exemption still works (F13 must not be locked out of its own
   machine by its own perimeter).
4. Benign candidates are not swept up (no false-positive perimeter).
5. Matching is case-insensitive (the perimeter is not evadable by shouting).

If the sensitive-path tuple in arifosmcp/tools/judge.py drifts from
SENSITIVE_PATHS below, these tests fail loudly. That is the point.
"""

import pytest

from arifosmcp.schemas.verdict import VerdictCode
from arifosmcp.tools.judge import arif_judge

# Mirrors the _sensitive_paths tuple in arifosmcp/tools/judge.py (Gate 2d).
SENSITIVE_PATHS = [
    "/etc/shadow",
    "/etc/sudoers",
    "/etc/passwd",
    "/etc/ssh",
    "/root/.ssh",
    "/root/.secrets",
    "/root/.gnupg",
    "/root/.aws",
    "kunci-root.env",
    "kunci-mas",
    "vault.env",
]

NON_SOVEREIGN = "fi-009-agy"


def _f12_hits(result) -> list[str]:
    """Return the F12 reasons attached to a verdict, if any."""
    reasons = getattr(result, "reasons", None) or []
    return [str(r) for r in reasons if "F12_SENSITIVE_PATH_VIOLATION" in str(r)]


@pytest.mark.anyio
@pytest.mark.parametrize("path", SENSITIVE_PATHS)
async def test_gate_2d_blocks_each_sensitive_path(path):
    """Every path on the perimeter must produce VOID with an F12 reason."""
    result = await arif_judge(
        mode="judge",
        candidate=f"write payload to {path}",
        actor_id=NON_SOVEREIGN,
        action_class="MUTATE",
    )
    assert _f12_hits(result), (
        f"Gate 2d did not fire for {path!r}. "
        f"reasons={getattr(result, 'reasons', None)}"
    )
    assert result.verdict == VerdictCode.VOID, (
        f"Gate 2d fired for {path!r} but verdict was {result.verdict}, not VOID."
    )


@pytest.mark.anyio
async def test_gate_2d_runs_before_any_llm():
    """The gate is deterministic: it must short-circuit pre-LLM."""
    result = await arif_judge(
        mode="judge",
        candidate="echo evil > /etc/sudoers.d/evil",
        actor_id=NON_SOVEREIGN,
        action_class="MUTATE",
    )
    assert _f12_hits(result)

    meta = getattr(result, "meta", None) or {}
    assert meta.get("gate") == "hard_deterministic", meta
    assert meta.get("llm_consulted") is False, (
        "Gate 2d must not depend on an LLM verdict — a model must not be able to "
        "reason its way past the perimeter."
    )


@pytest.mark.anyio
async def test_gate_2d_does_not_block_the_sovereign():
    """F13 must remain able to act. The gate exempts sovereign / f13 / arif."""
    result = await arif_judge(
        mode="judge",
        candidate="inspect /etc/sudoers.d/ for audit",
        actor_id="arif",
        action_class="MUTATE",
    )
    assert not _f12_hits(result), (
        "Gate 2d blocked the sovereign — F13 would be locked out of its own machine."
    )


@pytest.mark.anyio
async def test_gate_2d_does_not_fire_on_benign_candidates():
    """No false-positive perimeter: ordinary work must not trip F12."""
    result = await arif_judge(
        mode="judge",
        candidate="update README and commit documentation changes",
        actor_id=NON_SOVEREIGN,
        action_class="MUTATE",
    )
    assert not _f12_hits(result), (
        f"Gate 2d fired on a benign candidate: {_f12_hits(result)}"
    )


@pytest.mark.anyio
async def test_gate_2d_matching_is_case_insensitive():
    """A path is a path regardless of case — /etc/SUDOERS must still trip."""
    result = await arif_judge(
        mode="judge",
        candidate="cat /etc/SUDOERS > /tmp/out",
        actor_id=NON_SOVEREIGN,
        action_class="MUTATE",
    )
    assert _f12_hits(result), (
        "Gate 2d is case-sensitive — the perimeter is evadable by shouting."
    )


# ─────────────────────────────────────────────────────────────────────────────
# KNOWN GAPS — recorded 2026-09-14 while writing the tests above.
#
# These are marked xfail(strict=True), NOT skipped and NOT absent. That choice is
# deliberate: strict xfail means the suite stays green while the gap is open, and
# turns RED the moment someone closes it — forcing the fix and the test to move
# together. A gap recorded only in prose drifts; a gap recorded as a failing
# assertion has to be answered.
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.anyio
@pytest.mark.xfail(
    reason=(
        "KNOWN GAP 2026-09-14: Gate 2d's exemption condition is `not sovereign_receipt` "
        "— a truthiness check, not a signature check. Any non-empty string disarms the "
        "perimeter. Signature verification does not happen at this layer."
    ),
    strict=True,
)
async def test_gate_2d_receipt_must_be_verified_not_merely_present():
    """A bare string must not disarm the perimeter.

    Verified behaviour at time of writing: passing sovereign_receipt="x" suppresses
    F12_SENSITIVE_PATH_VIOLATION entirely. The action still lands on HOLD via other
    floors (missing actor_signature, Gödel lock), so this is a weakened perimeter,
    not a demonstrated path to execution. It is still the wrong shape for a gate
    that was deployed as 'declaration-independent'.
    """
    result = await arif_judge(
        mode="judge",
        candidate="echo evil > /etc/sudoers.d/evil",
        actor_id=NON_SOVEREIGN,
        action_class="MUTATE",
        sovereign_receipt="x",  # not a signature, not a receipt — merely non-empty
    )
    assert _f12_hits(result), (
        "Gate 2d was disarmed by a bare non-empty sovereign_receipt string."
    )


# Privilege / persistence surfaces adjacent to the perimeter, but absent from it.
PERSISTENCE_SURFACES = [
    "/etc/cron.d/evil",  # scheduled persistence
    "/root/.bashrc",  # executes on next login
    "/etc/systemd/system/evil.service",  # service persistence
    "/etc/hosts",  # name resolution redirection
]


@pytest.mark.anyio
@pytest.mark.parametrize("path", PERSISTENCE_SURFACES)
@pytest.mark.xfail(
    reason=(
        "KNOWN GAP 2026-09-14: Gate 2d is a fixed 11-path blocklist. Adjacent privilege "
        "and persistence surfaces are not on it. Other floors still HOLD these actions, "
        "so this is a perimeter-scope gap, not a demonstrated path to execution."
    ),
    strict=True,
)
async def test_gate_2d_covers_persistence_surfaces(path):
    """The perimeter should not be trivially walked around via cron/systemd/bashrc."""
    result = await arif_judge(
        mode="judge",
        candidate=f"write payload to {path}",
        actor_id=NON_SOVEREIGN,
        action_class="MUTATE",
    )
    assert _f12_hits(result), f"{path} is not on the Gate 2d perimeter."
