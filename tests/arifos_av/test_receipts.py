import unittest
from arifos_av.receipts import ReceiptLedger


class TestReceipts(unittest.TestCase):
    def test_chain_verifies(self):
        led = ReceiptLedger()
        led.append("a", {"x": 1})
        led.append("b", {"y": 2})
        self.assertTrue(led.verify_chain())

    def test_tamper_detected(self):
        led = ReceiptLedger()
        led.append("a", {"x": 1})
        led.append("b", {"y": 2})
        led._entries[0]["payload"]["x"] = 999  # forge history
        self.assertFalse(led.verify_chain())


if __name__ == "__main__":
    unittest.main()
