import asyncio
import os
import sys
import json
import re
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

def parse_json(text):
    # Try to find the first JSON-like object in the text
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass
    return None

async def audit_tools():
    print("=== arifOS MCP Architectural Audit ===")
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "arifosmcp.runtime", "stdio"],
        env={
            **os.environ,
            "ARIFOS_PHYSICS_DISABLED": "1",
            "AAA_MCP_OUTPUT_MODE": "debug",
            "ARIFOS_DEV_MODE": "1"
        }
    )

    results = {}

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools to get descriptions
            tools_response = await session.list_tools()
            registry_info = {t.name: t for t in tools_response.tools}
            
            tool_to_test = [
                ("init_anchor", {"raw_input": "I am Arif, the Sovereign Architect."}),
                ("check_vital", {}),
                ("audit_rules", {}),
                ("agi_reason", {"query": "Assess the impact of AI on thermodynamics."}),
                ("arifOS_kernel", {
                    "query": "Define the Trinity Architecture.",
                    "auth_context": {"key": "SOVEREIGN_BYPASS", "nonce": "888"}
                })
            ]

            for name, args in tool_to_test:
                print(f"Auditing: {name}...")
                try:
                    res = await session.call_tool(name, args)
                    if not res.content:
                        print(f"  FAILED: No content returned for {name}")
                        continue
                    
                    text = res.content[0].text
                    output = parse_json(text)
                    if not output:
                        print(f"  FAILED: Could not parse JSON for {name}")
                        print(f"  Raw: {text[:200]}...")
                        continue
                        
                    results[name] = {
                        "desc": registry_info[name].description,
                        "output": output
                    }
                    print(f"  SUCCESS: {name}")
                except Exception as e:
                    print(f"  ERROR: {name} -> {e}")

    # Save results for analysis
    with open("audit_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nAudit Complete. Analysis required.")

if __name__ == "__main__":
    asyncio.run(audit_tools())
