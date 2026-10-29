"""P4 — the canonical runtime source declaration.

Pure checks only: no dependency on the deployed venv existing, so this suite
runs identically in CI and on the box.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = REPO_ROOT / "scripts" / "probe_runtime_source.py"
DECLARATION_PATH = REPO_ROOT / "scripts" / "runtime_source.json"


def _load_probe():
    spec = importlib.util.spec_from_file_location("probe_runtime_source", PROBE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


probe_mod = _load_probe()


def test_declaration_exists_and_declares_the_three_trees():
    decl = probe_mod.load_declaration()
    assert decl["schema_version"] == "arifos.runtime_source.v1"
    assert decl["canonical_runtime"]["venv"] == "/opt/arifos/current/venv"
    assert decl["other_trees"]["repository"]["path"] == "/root/arifOS"
    assert decl["other_trees"]["deployed_source_copy"]["path"] == "/opt/arifos/app"


def test_canonical_import_root_resolves_to_the_deployed_venv():
    decl = probe_mod.load_declaration()
    root = probe_mod.canonical_import_root(decl)
    assert str(root).startswith("/opt/arifos/current/venv/lib/python")
    assert root.name == "arifosmcp"
    assert root.parent.name == "site-packages"


def test_repo_editable_venv_is_declared_as_a_non_measurement_interpreter():
    decl = probe_mod.load_declaration()
    entry = decl["interpreters"]["/root/arifOS/.venv/bin/python"]
    assert "EDITABLE" in entry
    assert "never a live measurement" in entry


def test_shadow_risk_is_true_inside_the_repository_and_false_outside(tmp_path):
    decl = probe_mod.load_declaration()
    assert probe_mod.shadow_risk(decl, REPO_ROOT) is True
    assert probe_mod.shadow_risk(decl, REPO_ROOT / "arifosmcp" / "runtime") is True
    assert probe_mod.shadow_risk(decl, tmp_path) is False
    assert probe_mod.shadow_risk(decl, "/root") is False


def test_observed_origin_is_either_the_canonical_root_or_the_repository_tree():
    """arifosmcp must resolve to exactly one of the two declared locations - never elsewhere."""
    decl = probe_mod.load_declaration()
    observed = probe_mod.probe()
    origin = observed["observed_import_origin"]
    assert origin is not None
    canonical = str(probe_mod.canonical_import_root(decl))
    repo_tree = str(Path(decl["other_trees"]["repository"]["path"]) / "arifosmcp")
    assert origin == canonical or origin == repo_tree, origin


def test_probe_reports_a_verdict_and_never_raises():
    result = probe_mod.probe()
    assert result["verdict"] in ("CANONICAL", "WRONG_TREE")
    assert result["match"] == (result["verdict"] == "CANONICAL")
    assert "interpreter" in result and "deployed_marker" in result


def test_probe_purges_repository_entries_from_sys_path(monkeypatch):
    decl = probe_mod.load_declaration()
    monkeypatch.syspath_prepend(str(REPO_ROOT))
    assert str(REPO_ROOT) in sys.path
    probe_mod.probe()
    assert str(REPO_ROOT) not in sys.path


def test_exit_code_contract_is_declared():
    decl = probe_mod.load_declaration()
    assert set(decl["probe"]["exit_codes"]) == {"0", "3"}
