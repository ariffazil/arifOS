import unittest
from pathlib import Path

class TestConstitutional(unittest.TestCase):
    def test_kanon_presence(self):
        """F4: Verify arifos.yml presence"""
        self.assertTrue(Path("arifos.yml").exists())
        
    def test_meta_mind_presence(self):
        """F2: Verify K333 Meta-Mind presence"""
        self.assertTrue(Path("000/ROOT/K333_CODE.md").exists())

if __name__ == "__main__":
    unittest.main()
