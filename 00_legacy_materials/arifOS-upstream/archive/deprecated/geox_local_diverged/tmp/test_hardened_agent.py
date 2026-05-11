import asyncio
import sys

# Add geox and arifosmcp to path
sys.path.append(r"c:\ariffazil\GEOX")
sys.path.append(r"C:\arifosmcp")

from arifos.geox.geox_hardened import HardenedGeoxAgent


async def test_hardened_agent():
    agent = HardenedGeoxAgent(session_id="ARIF_GEO_FORGE")

    # Test a simple tool if any or just check initialization
    # Since I just implemented MacrostratTool, let's try to list tools
    print("Agent Registry Tools:", agent.registry.list_tools())

    # Try a mock execution (though I don't have a mock tool yet)
    # Let's try to register a simple test tool now
    from arifos.geox.base_tool import BaseTool, GeoToolResult

    class HelloEarthTool(BaseTool):
        name = "hello_earth"
        description = "A simple welcome tool for geological intelligence."

        async def execute(self, **kwargs) -> GeoToolResult:
            return GeoToolResult(
                success=True,
                data={"message": "Welcome to the Malay Basin Forge, arif."},
                explanation="Initial grounding check completed.",
            )

    agent.registry.register(HelloEarthTool())

    print("\nExecuting Hardened HelloEarthTool...")
    envelope = await agent.execute_tool("hello_earth", {"user": "arif"})

    import json

    print(json.dumps(envelope, indent=2))


if __name__ == "__main__":
    asyncio.run(test_hardened_agent())
