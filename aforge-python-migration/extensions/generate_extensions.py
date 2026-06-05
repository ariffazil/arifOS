import os
import json

EXTENSIONS = {
    "arifosmcp": "http://localhost:8088/mcp",  # live VPS port; use 8080 for Docker dev
    "filesystem": "http://localhost:8002/mcp",
    "git": "http://localhost:8003/mcp",
    "fetch": "http://localhost:8005/mcp",
    "time": "http://localhost:8001/mcp",
    "memory": "http://localhost:8004/mcp",
    "grafana": "http://localhost:3000/api/mcp"
}

BRIDGE_PY = r"""import sys
import json
import requests

def main(url):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            request = json.loads(line)
            response = requests.post(url, json=request, headers=headers, stream=True)
            for response_line in response.iter_lines():
                if response_line:
                    decoded = response_line.decode('utf-8')
                    if decoded.startswith("data: "):
                        print(decoded[6:], flush=True)
                    elif decoded.startswith("{"):
                        print(decoded, flush=True)
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": request.get("id", "unknown") if 'request' in locals() else "unknown",
                "error": {"code": -32603, "message": str(e)}
            }), flush=True)

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    main(sys.argv[1])
"""

for name, url in EXTENSIONS.items():
    path = os.path.join("/root/extensions", name)
    os.makedirs(path, exist_ok=True)
    
    # Write bridge.py
    with open(os.path.join(path, "bridge.py"), "w") as f:
        f.write(BRIDGE_PY)
    
    # Write gemini-extension.json
    manifest = {
        "name": name,
        "version": "1.0.0",
        "description": f"ArifOS {name} AGI extension",
        "mcpServers": {
            name: {
                "command": "python3",
                "args": ["${extensionPath}/bridge.py", url]
            }
        }
    }
    with open(os.path.join(path, "gemini-extension.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    # Write GEMINI.md for context
    with open(os.path.join(path, "GEMINI.md"), "w") as f:
        f.write(f"# {name.upper()} Extension\n\nThis extension provides {name} tools governed by arifOS.\n")

