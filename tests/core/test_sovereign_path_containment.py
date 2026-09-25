"""
tests/core/test_sovereign_path_containment.py — sovereign://{file} boundary tests.

Regression for the 2026-09-22 fix: ``_read_file`` must never read a file that
resolves outside ``/opt/arifos/app/static/000``, whether the escape arrives as
an absolute path or as ``../`` (the fastmcp decode-after-match vector that lets
``%2F`` / ``%2e%2e`` smuggle separators past the ``[^/]+`` URI segment guard).

Before the fix, ``_read_file("/etc/hostname")`` returned ``{"status": "OK",
"source": "/etc/hostname"}`` — a live read of a file outside the archive root.
"""

from __future__ import annotations

import importlib
import tempfile
import unittest
from pathlib import Path


def _import_or_skip(module_path: str):
    try:
        return importlib.import_module(module_path)
    except Exception as exc:  # pragma: no cover - environment guard
        raise unittest.SkipTest(f"required module unavailable: {module_path}: {exc}")


class TestSovereignPathContainment(unittest.TestCase):
    def setUp(self) -> None:
        self.sovereign = _import_or_skip("arifosmcp.resources.sovereign")
        self.guard = _import_or_skip("arifosmcp.runtime.path_guard")

    # ── primitive boundary ────────────────────────────────────────────────

    def test_absolute_path_escape_rejected(self) -> None:
        res = self.sovereign._read_file("/etc/hostname")
        self.assertEqual(res.get("status"), "REJECTED")
        self.assertNotEqual(res.get("source"), "/etc/hostname")

    def test_relative_traversal_escape_rejected(self) -> None:
        res = self.sovereign._read_file("../../../../../etc/hostname")
        self.assertEqual(res.get("status"), "REJECTED")

    def test_md_escape_into_other_repo_rejected(self) -> None:
        # .md suffix is a content-type convention, not a boundary: a .md file
        # outside the archive must still be refused by containment.
        res = self.sovereign._read_file("/root/arifOS/README.md")
        self.assertEqual(res.get("status"), "REJECTED")

    def test_bare_basename_not_rejected(self) -> None:
        # Named-key values ("INDEX.md") and plain basenames stay inside the
        # root and must never be misclassified as escapes.
        res = self.sovereign._read_file("INDEX.md")
        self.assertIn(res.get("status"), ("OK", "NOT_FOUND"))
        self.assertNotEqual(res.get("status"), "REJECTED")

    # ── helper semantics ──────────────────────────────────────────────────

    def test_contained_path_allows_descendant(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = self.guard.contained_path(root, "a", "b.md")
            self.assertEqual(p, (root / "a" / "b.md").resolve())

    def test_contained_path_rejects_escape(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(ValueError):
                self.guard.contained_path(root, "../outside.md")
            with self.assertRaises(ValueError):
                self.guard.contained_path(root, "/etc/hostname")

    def test_contained_path_resolves_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "sub").mkdir()
            (root / "sub" / "link.md").symlink_to("/etc/hostname")
            with self.assertRaises(ValueError):
                self.guard.contained_path(root, "sub", "link.md")


if __name__ == "__main__":
    unittest.main()
