"""A public checkout must not require another machine's private filesystem."""

import subprocess
import unittest
from pathlib import Path, PurePosixPath, PureWindowsPath

ROOT = Path(__file__).resolve().parents[2]


class CheckoutPortabilityTests(unittest.TestCase):
    def test_tracked_symlinks_are_relative(self):
        entries = (
            subprocess.check_output(["git", "ls-files", "--stage", "-z"], cwd=ROOT)
            .decode()
            .split("\0")
        )
        absolute = []
        for entry in filter(None, entries):
            metadata, path = entry.split("\t", 1)
            mode, blob, _ = metadata.split()
            if mode != "120000":
                continue
            target = (
                subprocess.check_output(["git", "cat-file", "blob", blob], cwd=ROOT)
                .decode()
                .strip()
            )
            if PurePosixPath(target).is_absolute() or PureWindowsPath(target).is_absolute():
                absolute.append(f"{path} -> {target}")
        self.assertEqual(absolute, [], "Nonportable tracked symlinks: " + "; ".join(absolute))


if __name__ == "__main__":
    unittest.main()
