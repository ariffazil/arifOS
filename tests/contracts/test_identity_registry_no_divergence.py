"""Tripwire: the two copies of the identity registry must not diverge.

arifOS carries TWO copies of contracts/identity.py:

  contracts/identity.py            imported by ~9 runtime sites, but NOT listed in
                                   pyproject `[tool.setuptools.packages.find].include`
                                   (arifos*/arifosmcp*/core*/schemas*), so it does not
                                   ship in the wheel — production resolves those imports
                                   to a leftover site-packages copy from an older install.
  arifosmcp/contracts/identity.py  ships in the wheel, imported by ~3 sites.

This has already caused two production incidents on 2026-09-30:
  1. the leftover had silently lost the 2026-08-21 Seal C `I_ARIF` entry, whose own
     comment says the consolidation path becomes "structurally unreachable";
  2. commit d43b7fece patched only the minority copy, so the `name/FI-nnn` fix never
     reached the 9 majority sites until 69175c0ec.

The source-of-truth decision (ship `contracts*`, or migrate the 9 imports and delete
the top-level tree) is recorded in carry_forward open loop e-c1a7fe1a and is NOT made
here. This test only guarantees that until then, the copies AGREE — so a one-sided
edit fails loudly instead of shipping a split-brain identity registry.
"""

from __future__ import annotations

import importlib
import pytest

PROBE_IDS = [
    # bare canonical warga names
    "opencode", "hermes", "kimi", "qwen", "claude", "agy", "openclaw", "mcporter",
    "codex", "grok", "gemini", "i-arif", "333-AGI", "arif",
    # the documented lane-qualified form (FATWA K1: FI ids are lane/tier identities)
    "opencode/FI-001", "claude/FI-002", "qwen/FI-003", "agy/FI-004",
    "codex/FI-005", "kimi/FI-008", "kimi-code/FI-008",
    # must stay rejected in BOTH copies — trust boundary control
    "nobody/FI-999", "unknown-actor-xyz", "",
]


def _load(modname: str):
    try:
        return importlib.import_module(modname)
    except ImportError:
        pytest.skip(f"{modname} not importable in this environment")


@pytest.fixture(scope="module")
def copies():
    return _load("contracts.identity"), _load("arifosmcp.contracts.identity")


def test_both_copies_expose_the_same_registry_keys(copies):
    top, packaged = copies
    a, b = set(top.CANONICAL_ACTORS), set(packaged.CANONICAL_ACTORS)
    assert a == b, (
        "identity registry diverged between the two copies. "
        f"only in contracts/: {sorted(a - b)}; "
        f"only in arifosmcp/contracts/: {sorted(b - a)}. "
        "See carry_forward e-c1a7fe1a — edit BOTH or consolidate first."
    )


def test_both_copies_expose_the_same_aliases(copies):
    top, packaged = copies
    for key in sorted(set(top.CANONICAL_ACTORS) & set(packaged.CANONICAL_ACTORS)):
        ta = sorted(top.CANONICAL_ACTORS[key].get("aliases", []) or [])
        pa = sorted(packaged.CANONICAL_ACTORS[key].get("aliases", []) or [])
        assert ta == pa, f"aliases for {key} diverged: contracts={ta} packaged={pa}"


@pytest.mark.parametrize("actor_id", PROBE_IDS)
def test_normalization_agrees_across_copies(copies, actor_id):
    top, packaged = copies
    fn = "normalize_actor_identity"
    if not (hasattr(top, fn) and hasattr(packaged, fn)):
        pytest.skip("normalize_actor_identity missing from a copy")
    a = top.__dict__[fn](actor_id)["normalized"]
    b = packaged.__dict__[fn](actor_id)["normalized"]
    assert a == b, f"normalize_actor_identity({actor_id!r}) diverged: contracts={a} packaged={b}"


def test_both_copies_expose_the_shared_candidate_resolver(copies):
    """The resolver session_auth.exempt_actor_band() depends on must exist in both."""
    top, packaged = copies
    for mod in (top, packaged):
        assert hasattr(mod, "actor_lookup_candidates"), (
            f"{mod.__name__} lacks actor_lookup_candidates — the exempt resolver "
            "would fall back to raw-string matching and re-introduce the "
            "spelling-dependent authority cliff."
        )


@pytest.mark.parametrize("actor_id", ["opencode/FI-001", "kimi/FI-008", "i-arif"])
def test_candidate_resolver_agrees_across_copies(copies, actor_id):
    top, packaged = copies
    assert top.actor_lookup_candidates(actor_id) == packaged.actor_lookup_candidates(actor_id)


def test_trust_boundary_control_still_rejects_unknown(copies):
    """Guard against 'fixing' divergence by making everything resolve."""
    top, packaged = copies
    for mod in (top, packaged):
        assert mod.normalize_actor_identity("nobody/FI-999")["normalized"] is None
        assert mod.normalize_actor_identity("unknown-actor-xyz")["normalized"] is None
