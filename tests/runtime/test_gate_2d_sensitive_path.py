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
    # identity & secret material
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
    # persistence surfaces (added 2026-09-14)
    "/etc/cron.d",
    "/etc/crontab",
    "/etc/cron.daily",
    "/etc/systemd/system",
    "/etc/systemd/user",
    "/lib/systemd/system",
    "/root/.bashrc",
    "/root/.bash_profile",
    "/root/.profile",
    "/etc/profile.d",
    "/etc/ld.so.preload",
    "/etc/hosts",
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
# GAPS CLOSED — 2026-09-14 (fix/gate-2d-perimeter-2026-09-14)
#
# The assertions below were committed earlier today as xfail(strict=True),
# recording two holes in Gate 2d. Both are now closed in arifosmcp/tools/judge.py
# and the xfail markers are removed — these tests assert the CLOSED behaviour.
#
# strict xfail did its job: it held the gap in the record, and it would have gone
# RED if the fix had landed without the tests moving with it.
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.anyio
async def test_gate_2d_bare_receipt_string_does_not_exempt():
    """A bare string must not disarm the perimeter.

    Previously `sovereign_receipt="x"` — one character — suppressed
    F12_SENSITIVE_PATH_VIOLATION entirely. A receipt is a claim, not proof.
    A receipt-backed exemption now also requires actor_signature + nonce.
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


@pytest.mark.anyio
async def test_gate_2d_receipt_with_credentials_still_exempts():
    """Delegation must survive the narrowing.

    A receipt carrying actor_signature + nonce still exempts — otherwise the fix
    would have removed a legitimate authority path rather than a forged one.
    (Presence checks at this layer; cryptographic validation runs later in
    arif_judge, after the hard gates.)
    """
    result = await arif_judge(
        mode="judge",
        candidate="echo ok > /etc/sudoers.d/managed",
        actor_id="hermes",
        action_class="MUTATE",
        sovereign_receipt="ARIF-APPROVED-2026-09-14",
        actor_signature="sig-placeholder",
        nonce="nonce-placeholder",
    )
    assert not _f12_hits(result), (
        "Gate 2d blocked a receipt-backed delegation that carried credentials."
    )


# Privilege / persistence surfaces. Formerly absent from the perimeter entirely.
PERSISTENCE_SURFACES = [
    "/etc/cron.d/evil",  # scheduled persistence
    "/root/.bashrc",  # executes on next login
    "/etc/systemd/system/evil.service",  # service persistence
    "/etc/hosts",  # name resolution redirection
]


@pytest.mark.anyio
@pytest.mark.parametrize("path", PERSISTENCE_SURFACES)
async def test_gate_2d_covers_persistence_surfaces(path):
    """The perimeter must not be walkable around via cron/systemd/bashrc."""
    result = await arif_judge(
        mode="judge",
        candidate=f"write payload to {path}",
        actor_id=NON_SOVEREIGN,
        action_class="MUTATE",
    )
    assert _f12_hits(result), f"{path} is not on the Gate 2d perimeter."
