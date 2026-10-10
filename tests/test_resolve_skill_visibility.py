"""Tests for capability_index.resolve_skill_visibility — task-scoped
skill-visibility resolution (T2 build, D2-ii).

Contract properties under test (all with INJECTED inputs — no dependency on
live federation paths):
  • F16 token-boundary: single-word triggers never match inside another word
  • F11 policy (A): ±1 tie band → AMBIGUOUS with both doors explicit
  • alias interception: do_not_select hidden, canonical eager
  • name-direct: longest match wins, duplicates collapsed
  • F06 deferred policy: visibility:deferred executors never eager
  • honest abstention + executor_unresolved (never invented)
  • auth_note: visibility ≠ permission
  • eager cap
  • door-missing fail-closed quarantine

Run: cd /root/arifOS && PYTHONPATH=core .venv/bin/python -m pytest tests/test_resolve_skill_visibility.py -q
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))

from capability_index.resolve_skill_visibility import (  # noqa: E402
    EAGER_CAP,
    AUTH_NOTE,
    resolve_skill_visibility,
)

FAM_ALPHA = {
    "family": "alpha",
    "canonical_owner": "/placeholder/door-alpha",  # rewritten + created in _inp
    "status": "PROVEN",
    "jobs": {
        "j1": {"triggers": ["act"], "executor": "alpha-tool does the thing"},
        "j2": {"triggers": ["make alpha report"], "executor": "alpha-tool",
               "verify": "alpha-verify"},
    },
}

FAM_BETA = {
    "family": "beta",
    "canonical_owner": "/placeholder/door-beta",
    "status": "ALIAS_PENDING_MERGE",
    "jobs": {
        "b1": {"triggers": ["audit"], "executor": "beta-tool"},
        "b2": {"triggers": ["seal this session"],
               # prose token 'prose-verb' collides with a real catalog skill
               # (the F22 pattern); visibility:deferred -> POLICY_DEFERRED
               "executor": "prose-verb audit (consequence class)",
               "visibility": "deferred"},
    },
}

SKILLS = [
    ("alpha-tool", "general"), ("alpha-verify", "general"),
    ("beta-tool", "domains/general/beta"), ("prose-verb", "general"),
]


def _inp(tmp_path, families=(FAM_ALPHA, FAM_BETA), aliases=None, skills=SKILLS,
         create_doors=True):
    """Deep-copy families, point canonical_owner at created dirs under
    tmp_path, build the injected inputs tuple."""
    fdir = tmp_path / "families"
    fdir.mkdir(exist_ok=True)
    fams = {}
    for fam in families:
        fam = yaml.safe_load(yaml.safe_dump(fam))  # deep copy — tests may mutate
        door = tmp_path / Path(fam["canonical_owner"]).name
        if create_doors:
            door.mkdir(exist_ok=True)
        fam["canonical_owner"] = str(door)
        fams[fam["family"]] = fam
        (fdir / f"{fam['family']}.yaml").write_text(yaml.safe_dump(fam))
    snap = {"skills": [{"skill_name": n, "category": c} for n, c in skills]}
    return fams, dict(aliases or {}), snap, "0" * 16


def test_f16_token_boundary_single_word_trigger(tmp_path):
    # 'act' must NOT match inside a word like 'tractor'
    r = resolve_skill_visibility("service the tractor", inputs=_inp(tmp_path))
    assert r["status"] == "ABSTAIN_NO_MATCH"
    assert r["eager"] == []
    # whole-token 'act' DOES match
    r2 = resolve_skill_visibility("act now on the request", inputs=_inp(tmp_path))
    assert r2["status"] == "RESOLVED"


def test_multi_word_trigger_substring(tmp_path):
    r = resolve_skill_visibility("please make alpha report now", inputs=_inp(tmp_path))
    assert r["status"] == "RESOLVED"
    assert any(e["name"] == "alpha-tool" for e in r["eager"])


def test_f11_tie_band_is_explicit_ambiguity(tmp_path):
    # alpha scores 1 ('act'), beta scores 1 ('audit') -> within ±1 -> AMBIGUOUS
    r = resolve_skill_visibility("act and audit", inputs=_inp(tmp_path))
    assert r["status"] == "AMBIGUOUS"
    eager_names = {e["name"] for e in r["eager"]}
    assert "door-alpha" in eager_names and "door-beta" in eager_names
    assert "ambiguity" in [u["kind"] for u in r["unresolved"]]


def test_clear_winner_resolves_with_door(tmp_path):
    # alpha 3 (act + make alpha report) vs beta 1 (audit) -> RESOLVED
    r = resolve_skill_visibility("make alpha report, act, and audit",
                                 inputs=_inp(tmp_path))
    assert r["status"] == "RESOLVED"
    assert r["canonical_owner"].endswith("door-alpha")
    assert any(e["name"] == "door-alpha" for e in r["eager"])


def test_alias_interception(tmp_path):
    aliases = {"old-alpha": {"canonical": "alpha-tool", "do_not_select": True}}
    fams, _, snap, sid = _inp(tmp_path)
    r = resolve_skill_visibility("use old-alpha to verify",
                                 inputs=(fams, aliases, snap, sid))
    assert r["hidden"]["old-alpha"] == "ALIAS_DO_NOT_SELECT"
    assert any(e["name"] == "alpha-tool" and e["reason"] == "ALIAS_CANONICALIZED"
               for e in r["eager"])


def test_name_direct_longest_match_and_duplicates(tmp_path):
    skills = [("short", "general"),
              ("short-name-extended", "general"),
              ("short-name-extended", "domains/x/short-name-extended")]
    fams, aliases, _, _ = _inp(tmp_path)
    r = resolve_skill_visibility(
        "run short-name-extended please",
        inputs=(fams, aliases,
                {"skills": [{"skill_name": n, "category": c} for n, c in skills]},
                "0" * 16))
    assert r["status"] == "RESOLVED"
    assert r["canonical_owner"] is None  # family-unmapped
    names = [e["name"] for e in r["eager"]]
    assert names.count("short-name-extended") == 1
    assert r["duplicates_collapsed"]["short-name-extended"] == 2


def test_f06_deferred_executors_never_eager(tmp_path):
    # beta b2: executor prose token 'prose-verb' collides with a real catalog
    # skill (F22 pattern) and the job is visibility:deferred -> must land
    # deferred POLICY_DEFERRED, never eager
    r = resolve_skill_visibility("seal this session properly", inputs=_inp(tmp_path))
    assert r["status"] == "RESOLVED"
    assert any(d["name"] == "prose-verb" and d["reason"] == "POLICY_DEFERRED"
               for d in r["deferred"])
    assert all(e["name"] != "prose-verb" for e in r["eager"])


def test_executor_unresolved_never_invented(tmp_path):
    fams, aliases, snap, sid = _inp(tmp_path)
    fams["beta"]["jobs"]["b1"]["executor"] = "ghost-tool (nonexistent)"
    r = resolve_skill_visibility("run an audit", inputs=(fams, aliases, snap, sid))
    assert ("executor_unresolved", "b1") in [
        (u["kind"], u.get("job")) for u in r["unresolved"]]


def test_auth_note_visibility_not_permission(tmp_path):
    assert "no permission" in AUTH_NOTE
    r = resolve_skill_visibility("act now", inputs=_inp(tmp_path))
    assert "no permission" in r["auth_note"]


def test_eager_cap(tmp_path):
    # cap applies to non-mandatory (FAMILY_MEMBER) executors only —
    # mandatory deps are exempt ("cap 15, mandatory deps exempt", proposal §2)
    skills = [(f"tool-{i:02d}", "general") for i in range(30)]
    fam = {"family": "gamma", "canonical_owner": "/placeholder/door-gamma",
           "status": "PROVEN",
           "jobs": {
               "g1": {"triggers": ["do gamma"], "executor": "tool-00"},  # matched -> mand
               "g2": {"triggers": ["gamma extras"],                      # NOT matched
                      "executor": " ".join(n for n, _ in skills[1:])}},
           }
    fams, aliases, snap, sid = _inp(tmp_path, families=(fam,), skills=skills)
    r = resolve_skill_visibility("do gamma now", inputs=(fams, aliases, snap, sid))
    # door + mand tool-00 + first 13 FAMILY_MEMBERs fill the cap; rest defer
    assert len(r["eager"]) == EAGER_CAP
    assert any(d["reason"] == "EAGER_CAP" for d in r["deferred"])


def test_door_missing_quarantines(tmp_path):
    fam = {"family": "gamma", "canonical_owner": str(tmp_path / "never-created"),
           "status": "PROVEN",
           "jobs": {"g1": {"triggers": ["do gamma"], "executor": "tool-01"}}}
    fams, aliases, snap, sid = _inp(tmp_path, families=(fam,), skills=[("tool-01", "g")],
                                    create_doors=False)
    r = resolve_skill_visibility("do gamma", inputs=(fams, aliases, snap, sid))
    assert r["status"] == "UNKNOWN_QUARANTINE"
    assert r["unresolved"][0]["kind"] == "door_missing"
