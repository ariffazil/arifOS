import unittest
from arifos_av.judgment import Evidence, Judge, Verdict, complete


class TestJudgment(unittest.TestCase):
    def test_done_only_when_verified(self):
        j = Judge("witness")
        self.assertFalse(complete(j.verify("claim", [])))
        self.assertTrue(complete(j.verify("claim", [Evidence("OBS", "probe=ok")])))

    def test_falsifier_wins(self):
        j = Judge("witness")
        v = j.verify("claim", [Evidence("OBS", "x")],
                     falsifier=lambda c, e: True)
        self.assertIs(v, Verdict.FAILED)

    def test_doer_is_not_judge(self):
        doer = Judge("planner")
        witness = Judge("outer")
        self.assertNotEqual(doer.name, witness.name)


if __name__ == "__main__":
    unittest.main()
