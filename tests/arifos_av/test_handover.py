import unittest
from arifos_av.authority import Grant, SpeechAct, Tier
from arifos_av.handover import (
    BareActRejected, ExplanationRequired, HandoverRequest, HumanSovereign,
)

GRANT_T3 = Grant(SpeechAct.DIRECTIVE, Tier.T3, "child on road")


class TestHandover(unittest.TestCase):
    def test_silent_handover_refused(self):
        hs = HumanSovereign()
        req = HandoverRequest("child on road", ("stop", "swerve"), 1, explained=False)
        with self.assertRaises(ExplanationRequired):
            hs.decide(req, SpeechAct.DIRECTIVE, grants=[GRANT_T3])

    def test_bare_ok_is_not_consent(self):
        hs = HumanSovereign()
        req = HandoverRequest("child on road", ("stop", "swerve"), 1, explained=True)
        with self.assertRaises(BareActRejected):
            hs.decide(req, SpeechAct.ACKNOWLEDGE, grants=[GRANT_T3])

    def test_directive_without_grant_refused(self):
        hs = HumanSovereign()
        req = HandoverRequest("child on road", ("stop", "swerve"), 1, explained=True)
        with self.assertRaises(BareActRejected):
            hs.decide(req, SpeechAct.DIRECTIVE)  # no bound lease

    def test_real_directive_with_grant_records(self):
        hs = HumanSovereign()
        req = HandoverRequest("child on road", ("stop", "swerve"), 1, explained=True)
        out = hs.decide(req, SpeechAct.DIRECTIVE, grants=[GRANT_T3])
        self.assertIn("recorded", out)
        self.assertEqual(len(hs.decisions), 1)


if __name__ == "__main__":
    unittest.main()
