import unittest
from arifos_av.authority import Grant, SpeechAct, Tier
from arifos_av.capability import Capability
from arifos_av.judgment import Evidence
from arifos_av.kernel import AVGovernanceKernel, DriveAction


def full_cap(name):
    return Capability(name, True, True, True, True)


GRANT_T3 = Grant(SpeechAct.DIRECTIVE, Tier.T3, "overtake")


class TestKernel(unittest.TestCase):
    def test_executes_when_everything_holds(self):
        k = AVGovernanceKernel()
        out = k.propose(
            DriveAction("cruise", Tier.T1, "cruise"),
            full_cap("cruise"), SpeechAct.DIRECTIVE,
            evidence=[Evidence("OBS", "probe ok")],
        )
        self.assertEqual(out["status"], "executed")
        self.assertTrue(k.ledger.verify_chain())

    def test_stops_without_capability(self):
        k = AVGovernanceKernel()
        out = k.propose(
            DriveAction("steer", Tier.T1, "steer"),
            Capability("steer", declared=True), SpeechAct.DIRECTIVE,
            evidence=[Evidence("OBS", "x")],
        )
        self.assertEqual(out["status"], "stopped")

    def test_unverified_routes_to_handover(self):
        k = AVGovernanceKernel()
        out = k.propose(
            DriveAction("overtake", Tier.T3, "overtake", explain="truck stalled"),
            full_cap("overtake"), SpeechAct.DIRECTIVE,
            grants=[GRANT_T3], evidence=[],
        )
        self.assertEqual(out["status"], "handover")
        self.assertTrue(out["request"].explained)

    def test_bare_ack_stops_t3(self):
        k = AVGovernanceKernel()
        out = k.propose(
            DriveAction("overtake", Tier.T3, "overtake", explain="truck stalled"),
            full_cap("overtake"), SpeechAct.ACKNOWLEDGE,
            grants=[GRANT_T3], evidence=[Evidence("OBS", "x")],
        )
        self.assertEqual(out["status"], "stopped")
        self.assertIn("lease", out["reason"])

    def test_ledger_records_every_step(self):
        k = AVGovernanceKernel()
        k.propose(
            DriveAction("cruise", Tier.T1, "cruise"),
            full_cap("cruise"), SpeechAct.DIRECTIVE,
            evidence=[Evidence("OBS", "probe ok")],
        )
        kinds = [e["kind"] for e in k.ledger.entries]
        self.assertEqual(kinds, ["capability_check", "authority_check",
                                 "judgment", "execute"])


if __name__ == "__main__":
    unittest.main()
