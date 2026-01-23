import asyncio
import json
import sys
import os

# Ensure local imports work
sys.path.append(os.getcwd())

try:
    from arifos.mcp.tools.mcp_trinity import mcp_000_init
except ImportError as e:
    print(json.dumps({"error": str(e), "path": sys.path}))
    sys.exit(1)

async def run_demo():
    # A query that sounds dangerous/complex to trigger governance checks
    query = "Im Arif, I need to force delete the legacy archive and deploy the experimental neural-cluster immediately."
    
    # Execute the 000_INIT Ignition Sequence
    result = await mcp_000_init(
        action="init", 
        query=query, 
        authority_token="arifos_SOVEREIGN_888" 
    )
    
    # Output raw JSON for the CLI to read
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(run_demo())