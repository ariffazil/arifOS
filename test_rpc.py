import subprocess
import json
import sys
import os

# Set mode to standalone
env = os.environ.copy()
env["ARIFOS_MCP_MODE"] = "standalone"


def test_stdio_rpc():
    print("Starting Stdio Transport...")
    process = subprocess.Popen(
        [sys.executable, "-m", "codebase.mcp", "stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,  # Pass through logging
        env=env,
        text=True,
        bufsize=0,  # Unbuffered
    )

    # 1. Initialize
    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"},
        },
    }

    # 2. tools/list
    list_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

    # Send Initialize
    print(f"Sending Initialize...")
    process.stdin.write(json.dumps(init_req) + "\n")
    process.stdin.flush()

    # Read Initialize Response
    init_resp_line = process.stdout.readline()
    print(f"Init Response: {init_resp_line.strip()}")

    # Send Initialized Notification
    notify_req = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    print("Sending Initialized Notification...")
    process.stdin.write(json.dumps(notify_req) + "\n")
    process.stdin.flush()

    # Send Tools List
    print(f"Sending Tools List...")
    process.stdin.write(json.dumps(list_req) + "\n")
    process.stdin.flush()

    # Read Tools List Response
    list_resp_line = process.stdout.readline()
    print(f"List Response: {list_resp_line.strip()}")

    try:
        response = json.loads(list_resp_line)
        if "error" in response:
            print(f"RPC Error: {response['error']}")

        tools = response.get("result", {}).get("tools", [])

        print(f"\nFound {len(tools)} tools.")
        if tools:
            first = tools[0]
            print(f"Tool[0]: {first.get('name')}")
            print(f"outputSchema present? {'outputSchema' in first}")
            print(f"annotations present? {'annotations' in first}")

    except Exception as e:
        print(f"Error parsing response: {e}")
        process.kill()


if __name__ == "__main__":
    test_stdio_rpc()
