import asyncio
import sys
from arifos.mcp.trinity_server import create_trinity_server

async def perform_debug():
    print("DEBUG: Initializing Trinity Server...", file=sys.stderr)
    try:
        server = create_trinity_server()
        print("DEBUG: Server Created.", file=sys.stderr)
        
        # Manually call 000_init as if via MCP
        print("DEBUG: Calling 000_init(action='validate')...", file=sys.stderr)
        # We access the internal tool function directly for this test since we can't easily mock the full MCP protocol stream in a simple script without pipe
        # But we can check if the function itself runs
        
        from arifos.mcp.tools.mcp_trinity import mcp_000_init
        
        result = await mcp_000_init(action="validate", session_id="KIMI-DEBUG")
        print(f"DEBUG: Result: {result}", file=sys.stderr)
        
        if result['status'] == 'SEAL':
             print("SUCCESS: 000_init returned SEAL", file=sys.stderr)
        else:
             print("FAILURE: 000_init returned " + result.get('status', 'UNKNOWN'), file=sys.stderr)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(perform_debug())
