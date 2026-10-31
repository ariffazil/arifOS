"""Importing a read-only probe must not require privileged filesystem writes."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2] / "arifosmcp/runtime/capability_drift.py"


def load_probe():
    spec = importlib.util.spec_from_file_location("capability_drift_import_probe", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CapabilityCacheImportTests(unittest.TestCase):
    def test_import_does_not_create_directories(self):
        with patch.object(Path, "mkdir", side_effect=PermissionError("read-only filesystem")):
            module = load_probe()
        self.assertTrue(callable(module.record_test_result))

    def test_record_creates_cache_directory_when_needed(self):
        with tempfile.TemporaryDirectory() as directory:
            module = load_probe()
            module.TEST_CACHE_PATH = Path(directory) / "new-directory/cache.json"
            module.record_test_result("arif_init", passed=True, invoked_at=100)
            cache = json.loads(module.TEST_CACHE_PATH.read_text(encoding="utf-8"))
            self.assertTrue(cache["arif_init"]["last_pass"])
            self.assertEqual(cache["arif_init"]["last_invocation_at"], 100)


if __name__ == "__main__":
    unittest.main()
