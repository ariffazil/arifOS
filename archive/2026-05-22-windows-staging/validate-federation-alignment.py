#!/usr/bin/env python3
"""Local Cockpit Federation Alignment Validator.
Enforces arifOS alignment, verifies stdio MCP negotiation, and maps capability health.
"""

import sys
import subprocess
import json


def test_stdio_negotiation():
    print("[*] Testing local stdio MCP protocol negotiation...")
    initialize_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "validator"},
        },
    }

    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "arifosmcp.runtime", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, _ = proc.communicate(input=json.dumps(initialize_request) + "\n", timeout=5)

        if not stdout:
            print("[FAIL] Stdio server returned empty response.")
            return False

        response = json.loads(stdout.strip())
        negotiated_version = response.get("result", {}).get("protocolVersion")

        if negotiated_version == "2024-11-05":
            print(f"[PASS] Successfully negotiated protocol version down to {negotiated_version}.")
            return True
        else:
            print(f"[FAIL] Server replied with unsupported version: {negotiated_version}.")
            return False

    except Exception as e:
        print(f"[FAIL] Error running stdio negotiation test: {e}")
        return False


def check_local_ports():
    print("[*] Checking local cockpit MCP server ports...")
    import socket

    ports = {"arifos": 8080, "geox": 8081, "wealth": 8082, "well": 8083}

    for name, port in ports.items():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            result = s.connect_ex(("127.0.0.1", port))
            if result == 0:
                print(f"[ONLINE] {name} is active on local port {port}.")
            else:
                print(
                    f"[OFFLINE] {name} is offline on port {port} (Normal if running remote-first)."
                )


def main():
    print("=== arifOS Federation Alignment Diagnostic ===")
    negotiation_ok = test_stdio_negotiation()
    check_local_ports()

    if negotiation_ok:
        print("\n[RESULT] Alignment status: EXCELLENT (Dynamic protocol negotiation active).")
        sys.exit(0)
    else:
        print("\n[RESULT] Alignment status: WARNING (Stdio negotiation drift detected).")
        sys.exit(1)


if __name__ == "__main__":
    main()
