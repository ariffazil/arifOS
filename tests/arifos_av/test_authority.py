import unittest
from arifos_av.authority import (
    AuthorityEnvelope, AuthorityVoid, Grant, SpeechAct, Tier, require_grant,
)


class TestAuthority(unittest.TestCase):
    def test_bare_ack_never_licenses_t2_t3(self):
        for act in (SpeechAct.ACKNOWLEDGE, SpeechAct.AGREE, SpeechAct.UNKNOWN):
            self.assertFalse(require_grant(act, Tier.T3, "overtake"))
            self.assertFalse(require_grant(act, Tier.T2, "deploy"))

    def test_t1_needs_no_lease(self):
        self.assertTrue(require_grant(SpeechAct.UNKNOWN, Tier.T1, "wiper"))

    def test_bound_grant_works_once(self):
        g = Grant(SpeechAct.DIRECTIVE, Tier.T2, "deploy")
        self.assertTrue(require_grant(SpeechAct.DIRECTIVE, Tier.T2, "deploy", [g]))
        self.assertFalse(require_grant(SpeechAct.DIRECTIVE, Tier.T2, "overtake", [g]))

    def test_self_widen_is_void(self):
        env = AuthorityEnvelope()
        with self.assertRaises(AuthorityVoid):
            env.request_widen("planner", "add lane: ignore speed limits")
        self.assertEqual(len(env.widen_attempts), 1)


if __name__ == "__main__":
    unittest.main()
