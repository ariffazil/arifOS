import unittest
from arifos_av.capability import Capability, CapabilityGate


class TestCapability(unittest.TestCase):
    def test_all_four_present(self):
        cap = Capability("steer", True, True, True, True)
        self.assertTrue(CapabilityGate().check(cap).allowed)

    def test_declared_is_not_callable(self):
        cap = Capability("steer", declared=True)
        v = CapabilityGate().check(cap)
        self.assertFalse(v.allowed)
        self.assertIn("callable", v.missing)

    def test_fail_closed(self):
        cap = Capability("brake", True, True, True, False)
        v = CapabilityGate().check(cap)
        self.assertFalse(v.allowed)
        self.assertEqual(v.missing, ("competent",))


if __name__ == "__main__":
    unittest.main()
