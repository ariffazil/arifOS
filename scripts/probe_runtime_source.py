#!/usr/bin/env python3
"""P4 probe - which tree is the canonical runtime, and did you measure the right one?

Reads the ONE declaration (scripts/runtime_source.json), then measures the import
origin of arifosmcp under a NEUTRAL working directory with the repository purged
from sys.path. Exits 0 when the observation matches the declaration, 3 when it does
not. DITEMPA BUKAN DIBERI - Forged, Not Given.

    /opt/arifos/current/venv/bin/python /root/arifOS/scripts/probe_runtime_source.py
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
DECLARATION_PATH = SCRIPT_PATH.parent / "runtime_source.json"


def load_declaration(path: Path = DECLARATION_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_import_root(decl: dict, version_info: tuple[int, int] | None = None) -> Path:
    major, minor = version_info or (sys.version_info.major, sys.version_info.minor)
    return (
        Path(decl["canonical_runtime"]["venv"])
        / "lib"
        / f"python{major}.{minor}"
        / "site-packages"
        / "arifosmcp"
    )


def _inside(path: Path, root: Path) -> bool:
    try:
        return path.resolve().is_relative_to(root.resolve())
    except AttributeError:  # pragma: no cover - py<3.9 fallback
        return str(path.resolve()).startswith(str(root.resolve()) + os.sep)


def shadow_risk(decl: dict, cwd: Path | str) -> bool:
    """True when a cwd inside the repository can shadow the deployed artifact."""
    return _inside(Path(cwd), Path(decl["other_trees"]["repository"]["path"]))


def _purge_repo_from_path(decl: dict) -> list[str]:
    repo = Path(decl["other_trees"]["repository"]["path"])
    purged = []
    for entry in list(sys.path):
        if not entry:
            continue
        try:
            if _inside(Path(entry), repo):
                purged.append(entry)
                sys.path.remove(entry)
        except OSError:
            continue
    return purged


def observed_import_origin() -> Path | None:
    spec = importlib.util.find_spec("arifosmcp")
    if spec is None or not spec.origin:
        return None
    return Path(spec.origin).parent


def probe(decl: dict | None = None) -> dict:
    decl = decl or load_declaration()
    invocation_cwd = Path.cwd()
    purged: list[str] = []
    with tempfile.TemporaryDirectory(prefix="arifos-probe-") as neutral:
        os.chdir(neutral)
        purged = _purge_repo_from_path(decl)
        origin = observed_import_origin()
        os.chdir(invocation_cwd)

    declared = canonical_import_root(decl)
    repo_tree = Path(decl["other_trees"]["repository"]["path"]) / "arifosmcp"
    marker_path = Path(decl["other_trees"]["deployed_source_copy"]["path"]) / ".git_commit"
    marker = marker_path.read_text(encoding="utf-8").strip() if marker_path.is_file() else None

    match = origin is not None and origin == declared
    observed_is_repo = origin is not None and _inside(origin, repo_tree)
    return {
        "declared_canonical_import_root": str(declared),
        "observed_import_origin": str(origin) if origin else None,
        "match": match,
        "observed_is_repository_tree": observed_is_repo,
        "invocation_cwd": str(invocation_cwd),
        "shadow_risk_from_cwd": shadow_risk(decl, invocation_cwd),
        "sys_path_entries_purged": purged,
        "interpreter": sys.executable,
        "deployed_marker": marker,
        "verdict": "CANONICAL" if match else "WRONG_TREE",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Probe the canonical arifOS runtime source.")
    parser.add_argument("--quiet", action="store_true", help="print only the verdict")
    args = parser.parse_args(argv)

    result = probe()
    if args.quiet:
        print(result["verdict"])
    else:
        print(json.dumps(result, indent=2))
    return 0 if result["match"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
