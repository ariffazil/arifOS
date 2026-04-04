#!/usr/bin/env python3
from flask import Flask, jsonify
import urllib.request
from datetime import datetime

app = Flask(__name__)

OPENCLAW_HOST = "openclaw"
OPENCLAW_PORT = 18789

@app.route('/health')
def health():
    try:
        req = urllib.request.Request(
            f"http://{OPENCLAW_HOST}:{OPENCLAW_PORT}/",
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                return jsonify({
                    "status": "healthy",
                    "service": "OpenClaw",
                    "upstream": f"{OPENCLAW_HOST}:{OPENCLAW_PORT}",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "verdict": "SEAL"
                }), 200
            else:
                raise Exception(f"Status {resp.status}")
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "service": "OpenClaw",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "verdict": "VOID"
        }), 503

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    try:
        import urllib.request
        url = f"http://{OPENCLAW_HOST}:{OPENCLAW_PORT}/{path}"
        req = urllib.request.Request(url, method=request.method)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read(), resp.status, {'Content-Type': resp.headers.get('Content-Type', 'text/html')}
    except Exception as e:
        return f"Bad Gateway: {e}", 502

from flask import request

if __name__ == '__main__':
    print("Starting Flask shim on port 3001")
    app.run(host='0.0.0.0', port=3001, threaded=True)
