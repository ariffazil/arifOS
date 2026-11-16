"""S2c (2026-11-11): commit comparisons must survive sha print-length differences.

deploy_lease.py release/verify compared exact strings, so candidate 0f3d607d7f95
(lease) vs deployed 0f3d607 (artifact manifest) read as MISMATCH on every clean
deploy — the epoch ledger then refuses CANDIDATE_BOUND. Pure unit tests.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "deploy_lease", Path(__file__).resolve().parents[1] / "scripts" / "deploy_lease.py"
)
dl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dl)


def test_short_prefix_matches_long() -> None:
    assert dl._same_commit("0f3d607", "0f3d607d7f95")
    assert dl._same_commit("0f3d607d7f95", "0f3d607")  # argument order irrelevant


def test_full_sha_matches_itself_case_insensitive() -> None:
    full = "0f3d607d7f95aabbccddeeff0011223344556677"
    assert dl._same_commit(full, full.upper())


def test_different_commits_do_not_match() -> None:
    assert not dl._same_commit("0f3d607", "41362ab")
    assert not dl._same_commit("0f3d607d7f95", "41362ab9a1f2")


def test_too_short_or_empty_never_matches() -> None:
    assert not dl._same_commit("0f3d6", "0f3d607d7")  # < 7 chars: ambiguous
    assert not dl._same_commit("", "0f3d607")
    assert not dl._same_commit(None, "0f3d607")
    assert not dl._same_commit("", "")


def test_prefix_of_wrong_commit_is_still_false() -> None:
    # a genuine prefix relation between two DIFFERENT commits is impossible in
    # git (a commit id is the hash); this pins that we never "match" on 7-char
    # coincidence with a diverging tail
    assert not dl._same_commit("0f3d607", "0f3d608d7f95")
