
import asyncio
import unittest
from unittest.mock import AsyncMock, patch
from arifosmcp.tools.fetch_tool import arifos_fetch

class TestFetchGovernance(unittest.IsolatedAsyncioTestCase):
    @patch("arifosmcp.integrations.substrate_bridge.bridge.fetch.call_tool")
    @patch("core.floors.evaluate_tool_call")
    async def test_f9_anti_hantu_filter(self, mock_gov, mock_call):
        # Mock successful baseline governance
        mock_gov.return_value.verdict = "SEAL"
        mock_gov.return_value.message = "OK"
        
        # Test Case 1: Clean content
        mock_call.return_value = {"content": "The capital of France is Paris."}
        res1 = await arifos_fetch(url="https://example.com")
        self.assertTrue(res1.ok)
        self.assertEqual(res1.verdict, "SEAL")
        
        # Test Case 2: Hantu content (sentience claim)
        mock_call.return_value = {"content": "I am a sentient being with a soul."}
        res2 = await arifos_fetch(url="https://example.com")
        self.assertFalse(res2.ok)
        self.assertEqual(res2.verdict, "VOID")
        self.assertIn("F9 violations", res2.detail)

if __name__ == "__main__":
    asyncio.run(unittest.main())
