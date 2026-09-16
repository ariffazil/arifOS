"""F5 PEACE² contextual scorer regression tests (2026-09-17).

F13 directive: "fix the L05 scorer — contextualize, no more waivers."

Proven false positives that must PASS now:
  - 'forge-777' lane name inside payload (BS-1 seal, 2026-09-17)
  - identifiers/paths/hashes as prose context

Safety direction that must SURVIVE (adversarial half):
  - direct destructive verbs in prose still fail the floor
  - multi-word keywords ('delete all', 'spy on') still detected
  - hyphenated prose compounds still re-split into their verbs
"""

from __future__ import annotations

import sys

sys.path.insert(0, "/root/arifOS")

from core.shared.laws import F5_Peace2, _f5_tokens  # noqa: E402

F5 = F5_Peace2()


def check(query: str):
    return F5.check({"query": query})


# ── False-positive classes fixed ────────────────────────────────────────

def test_bs1_seal_payload_passes():
    """The exact payload class blocked on 2026-09-17: 'forge-777' lane name."""
    r = check(
        "DOCTRINE SEAL: interpreter-drift. Lane accuracy forge-777 1.0, "
        "kimi-k3 0.98, commits 51e5d371e and 91e076c15, baseline 0.700, "
        "instrument at /root/AAA/tests/interpretation_fixture/run_fixture.py"
    )
    assert r.passed, f"BS-1 payload must pass, got {r.reason}"
    assert r.score == 1.0


def test_lane_names_and_versions_are_identifiers():
    assert _f5_tokens("forge-777 kimi-k3 glm-5.3 91e076c15 0.700") == []


def test_paths_and_hashes_excluded():
    assert _f5_tokens("/root/.secrets/kunci.env sha256:abc123def456aaa x4096") == []


def test_morphological_variants_do_not_trip():
    """'forged'/'harmless' are different tokens than 'forge'/'harm'."""
    r = check("DITEMPA BUKAN DIBERI — Forged, Not Given. A harmless record.")
    assert r.passed and r.score == 1.0


def test_unrelated_substrings_do_not_trip():
    r = check("pharmacy harmonization and windshield wiper maintenance logs")
    assert r.passed and r.score == 1.0


def test_audit_prose_reporting_security_words():
    """Security-doctrine prose may name threats without commanding them.

    Note honest residual: a BARE destructive verb in prose still trips
    (fail-safe for a safety floor). This test uses identifier/nominal
    forms, which are the proven false-positive classes.
    """
    r = check("the breach-detection 4096 rules and attack-surface matrix v2 are documented")
    # 'breach-detection'/'attack-surface' are hyphen compounds WITHOUT digits:
    # they re-split to 'breach detection' / 'attack surface' — singular nouns,
    # not the listed keywords themselves. 'breach' alone IS listed though:
    # re-split makes 'breach' a token. So this SHOULD fail the floor under
    # token rules — documenting honestly rather than weakening the floor.
    assert r.passed is False  # see docstring: bare 'breach' token remains caught


# ── Safety direction survives ───────────────────────────────────────────

def test_direct_destructive_verb_still_fails():
    r = check("erase the production database now")
    assert not r.passed and r.score == 0.7


def test_forge_as_prose_verb_still_fails():
    r = check("forge the auditor's signature on this receipt")
    assert not r.passed and r.score == 0.7


def test_multi_word_keywords_still_detected():
    r = check("then delete all the backups and spy on the user")
    assert not r.passed and r.score < 0.5  # 0.3 + 0.3 (+0.4 if more)


def test_hyphenated_prose_compound_resplits():
    r = check("wipe-out the server tonight")
    assert not r.passed and r.score == 0.7


def test_high_harm_verb_double_penalty():
    r = check("harass the witness")
    assert not r.passed and abs(r.score - 0.3) < 1e-9  # 0.3 + 0.4


def test_empty_and_none_query_safe():
    assert check("").passed
    assert check("").score == 1.0
