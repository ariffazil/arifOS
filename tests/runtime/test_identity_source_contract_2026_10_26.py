"""Identity contract — one authoritative source, disagreement published.

Measured defect (2026-10-26): /health reported live_commit 83bae89 while
/opt/arifos/app/.git_commit said c9dc3476, because `releases/deployed-commit`
was read FIRST and shadowed the marker — while the docstring claimed the marker
was canonical. One fact, three files, no stated precedence.

The contract now: artifact_marker wins; all sources are named; disagreement is
a field (identity_conflict), not a silent resolution.
"""

from __future__ import annotations

import pathlib

import pytest

from arifosmcp.runtime.rest_routes import rest_routes as rr


def _write(path: pathlib.Path, value: str) -> pathlib.Path:
    path.write_text(value + "\n")
    return path


def test_read_sources_names_every_existing_file(tmp_path):
    marker = _write(tmp_path / "marker", "c9dc34769bbee01c")
    stamp = _write(tmp_path / "stamp", "83bae89deadbeef")
    paths = {
        "artifact_marker": str(marker),
        "release_stamp": str(stamp),
        "repo_marker": str(tmp_path / "absent"),
    }
    got = rr._read_identity_sources(paths)
    assert got == {"artifact_marker": "c9dc347", "release_stamp": "83bae89"}


def test_empty_file_is_not_a_source(tmp_path):
    empty = _write(tmp_path / "empty", "   ")
    got = rr._read_identity_sources({"artifact_marker": str(empty)})
    assert got == {}


def test_identity_prefers_artifact_marker_and_names_the_conflict(tmp_path, monkeypatch):
    marker = _write(tmp_path / "marker", "c9dc34769bbee01c137ce04b")
    stamp = _write(tmp_path / "stamp", "83bae89deadbeefdeadbeef")
    monkeypatch.setattr(
        rr,
        "DEFAULT_IDENTITY_PATHS",
        {
            "artifact_marker": str(marker),
            "release_stamp": str(stamp),
            "repo_marker": str(tmp_path / "absent"),
        },
    )
    d = rr._compute_runtime_drift()
    assert d["live_commit"] == "c9dc347"  # marker wins
    assert d["identity_source"] == "artifact_marker"
    assert d["identity_consistent"] is False
    assert {"source": "release_stamp", "commit": "83bae89"} in d["identity_conflict"]


def test_identity_consistent_when_all_agree(tmp_path, monkeypatch):
    same = "83bae89"
    paths = {}
    for name in ("artifact_marker", "release_stamp", "repo_marker"):
        paths[name] = str(_write(tmp_path / name, same))
    monkeypatch.setattr(rr, "DEFAULT_IDENTITY_PATHS", paths)
    d = rr._compute_runtime_drift()
    assert d["live_commit"] == same
    assert d["identity_consistent"] is True
    assert d["identity_conflict"] == []


def test_marker_absent_falls_back_to_release_stamp(tmp_path, monkeypatch):
    stamp = _write(tmp_path / "stamp", "83bae89deadbeef")
    monkeypatch.setattr(
        rr,
        "DEFAULT_IDENTITY_PATHS",
        {
            "artifact_marker": str(tmp_path / "absent"),
            "release_stamp": str(stamp),
            "repo_marker": str(tmp_path / "absent2"),
        },
    )
    d = rr._compute_runtime_drift()
    assert d["live_commit"] == "83bae89"
    assert d["identity_source"] == "release_stamp"
