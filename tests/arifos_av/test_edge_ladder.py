import unittest
from arifos_av.edge_ladder import BoundedLadder


class TestLadder(unittest.TestCase):
    def test_primary_resolves(self):
        lad = BoundedLadder(lambda t: "ok", lambda t: None, lambda t: None)
        self.assertEqual(lad.run("t").status, "resolved")

    def test_alternative_after_fail(self):
        def broken(t):
            raise RuntimeError("dead lane")
        lad = BoundedLadder(broken, lambda t: "backup ok", lambda t: None)
        r = lad.run("t")
        self.assertEqual((r.status, r.lane), ("resolved", "alternative"))

    def test_honest_stop_no_fabrication(self):
        lad = BoundedLadder(lambda t: None, lambda t: None, lambda t: None)
        r = lad.run("t")
        self.assertEqual(r.status, "stopped")
        self.assertIn("blind receipt", r.note)


if __name__ == "__main__":
    unittest.main()
