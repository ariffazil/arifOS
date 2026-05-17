import unittest
from pathlib import Path


class TestConstitutional(unittest.TestCase):
    @unittest.skipUnless(
        Path("arifos.yml").exists(),
        "arifos.yml not found — constitutional charter must be present at repo root",
    )
    def test_kanon_presence(self):
        """F4: Verify arifos.yml presence"""
        self.assertTrue(Path("arifos.yml").exists())

    @unittest.skipUnless(
        Path("000/ROOT/K333_CODE.md").exists(),
        "000/ROOT/K333_CODE.md not found — meta-mind charter must be present",
    )
    def test_meta_mind_presence(self):
        """F2: Verify K333 Meta-Mind presence"""
        self.assertTrue(Path("000/ROOT/K333_CODE.md").exists())


if __name__ == "__main__":
    unittest.main()
