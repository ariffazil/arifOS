import sys
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
