"""T1 IDENTITY_CANON v1 test suite (2026-10-22).

Reads the content-hashed shared fixture and asserts the canon rule for both
the resolver and the comparator. The fixture hash check makes silent drift
between the Python and TypeScript suites impossible.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

FIXTURE = REPO_ROOT / "contracts" / "identity_canon_fixtures.json"


def _load_fixture() -> dict:
    doc = json.loads(FIXTURE.read_text())
    body = json.dumps(
        {k: doc[k] for k in ("canon_version", "rule", "cases")},
        indent=2,
    )
    assert hashlib.sha256(body.encode()).hexdigest() == doc["content_sha256"], (
        "fixture content hash mismatch — fixtures drifted; regenerate before testing"
    )
    return doc


def test_fixture_hash_intact():
    _load_fixture()


def test_all_fixture_cases_resolve():
    from contracts.identity_canon import resolve_actor_identity

    for case in _load_fixture()["cases"]:
        r = resolve_actor_identity(case["raw"])
        assert r["claimed"] == case["claimed"], f"claim mutated for {case['raw']!r}"
        assert r["canonical_id"] == case["canonical_id"], (
            f"canonical mismatch for {case['raw']!r}: {r['canonical_id']!r} != {case['canonical_id']!r}"
        )
        assert r["comparison_key"] == case["comparison_key"], (
            f"comparison_key mismatch for {case['raw']!r}"
        )


def test_same_principal_equivalences():
    from contracts.identity_canon import same_principal

    pairs = [
        ("arif-fazil", "arif"),
        ("ARIF_FAZIL", "ariffazil"),
        ("333-AGI", "333-agi"),
        ("claude/opus-5.5", "CLAUDE"),
        ("kimi-code/FI-008", "fi-008"),
        ("mesa-test-agent", "mesa_test_agent"),
    ]
    for a, b in pairs:
        assert same_principal(a, b), f"{a!r} and {b!r} must be one principal"


def test_different_principals_stay_different():
    from contracts.identity_canon import same_principal

    for a, b in [("arif", "333-AGI"), ("claude", "kimi-code/FI-008"), ("nova-9", "arif")]:
        assert not same_principal(a, b), f"{a!r} must not equal {b!r}"


def test_claim_never_rewritten():
    from contracts.identity_canon import resolve_actor_identity

    for raw in ["claude/opus-5.5", "ARIF_FAZIL", "333-AGI", "kimi-code/FI-008"]:
        r = resolve_actor_identity(raw)
        assert r["claimed"] == raw, f"IDENTITY_CANON violation: claim {raw!r} rewritten"


def test_wrapper_comparator_accepts_known_fork_pair():
    """The exact pair that false-fired session_actor_mismatch on 2026-10-21."""
    from contracts.identity_canon import same_principal

    assert same_principal("claude/opus-5.5", "CLAUDE")


def test_sovereign_spoof_shapes_do_not_become_arif():
    """Multi-token natural-language claims stay out of the sovereign canon."""
    from contracts.identity_canon import same_principal

    assert not same_principal("ARIF FAZIL THE GREAT", "arif")
    assert not same_principal("F13 SOVEREIGN", "arif")
