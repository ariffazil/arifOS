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


# ── 2026-09-25: code-span literal-name class ───────────────────────────
# F13 "baiki dua dua cacat" — proven false-positive: hostname `forge`
# (bare word, backtick-quoted) in FI-003 witness-report payload → 0.700.

def test_hostname_forge_in_code_span_passes():
    """The exact blocked payload class: machine hostname `forge` quoted as literal."""
    r = check(
        "WITNESS RECORD: KVM8 `forge` (100.64.0.2), 13:56:47 +08 MYT, "
        "process running as root on `forge` — the seat/court machine."
    )
    assert r.passed, f"witness payload with `forge` hostname must pass, got {r.reason}"
    assert r.score == 1.0


def test_code_span_identifiers_are_names():
    tokens = _f5_tokens("host `forge` lane `wipe` key `erase`")
    assert tokens == ["host", "lane", "key"]  # span contents gone, prose stays
    assert not ({"forge", "wipe", "erase"} & set(tokens))


def test_mixed_span_and_prose_verb_still_fails():
    """A literal name in code span does not mask a bare destructive verb."""
    r = check("running on `forge`: erase the production ledger now")
    assert not r.passed and r.score == 0.7


def test_unpaired_backtick_fails_safe():
    """Odd backtick count forms no span — bare token stays scanned."""
    r = check("erase `the database tonight")
    assert not r.passed and r.score == 0.7


def test_seal_payload_class_with_paths_and_spans():
    """Representative seal-record provenance line: paths + spans, no verbs."""
    r = check(
        "Draft artifact: `/root/forge_work/report.md` on `forge`, "
        "chain `/root/.local/share/arifos/vault999/seal_chain.jsonl` entry 269"
    )
    assert r.passed and r.score == 1.0


# ── 2026-09-25(ii): 555 residual hardening ─────────────────────────────
# Mid-token backtick evasion + phrase-wide span exemption, closed WITHOUT
# reopening the D2 hostname false positive (see laws.py 2026-09-25(ii)).

def test_mid_token_backtick_evasion_closed():
    """'era`se`' is intra-word formatting, not a name quote — verb reconstitutes."""
    r = check("era`se` the production ledger tonight")
    assert not r.passed and r.score == 0.7


def test_mid_token_span_rejoins_word():
    assert _f5_tokens("era`se` the ledger") == ["erase", "the", "ledger"]


def test_phrase_split_by_span_still_detected_delete_all():
    r = check("quietly delete `all` the backup files now")
    assert not r.passed and r.score == 0.7  # 'delete all' reconstructed (single hit)


def test_phrase_split_by_span_still_detected_spy_on():
    r = check("then spy `on` the witness quietly")
    assert not r.passed and r.score == 0.7  # 'spy on' reconstructed


def test_span_followed_by_punctuation_still_name():
    """Boundary = alphanumeric glue, not punctuation: '`forge`,' stays a name."""
    r = check("hostname `forge`, seat machine, 13:56:47 +08 MYT")
    assert r.passed and r.score == 1.0


def test_bare_quoted_destructive_names_still_exempt():
    """Regression guard: quoted config keys are names even when destructive-looking."""
    r = check("config keys `wipe` `erase` `forge` documented in the runbook")
    assert r.passed and r.score == 1.0
