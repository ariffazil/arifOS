import sys
import os

# Ensure repo root is in path
sys.path.append(os.getcwd())

print("Checking imports for SSE server...")
try:
    from codebase.mcp.entrypoints.sse_entry import main

    print("SUCCESS: codebase.mcp.entrypoints.sse_entry loaded.")
except ImportError as e:
    print(f"FAILURE: Could not import sse_entry: {e}")
except Exception as e:
    print(f"FAILURE: Unexpected error during import: {e}")

try:
    from codebase.mcp.transports.sse import SSETransport

    print("SUCCESS: codebase.mcp.transports.sse loaded.")
except ImportError as e:
    print(f"FAILURE: Could not import SSETransport: {e}")

print("Import check complete.")
