#!/usr/bin/env python3
"""
cn-organ: Continue CLI as a Federation Organ
═══════════════════════════════════════════
A2A gateway that wraps `cn` (Continue CLI 1.5.45) for federation integration.

Exposes:
  GET  /health                            Liveness probe
  GET  /ready                             Readiness probe
  GET  /.well-known/agent-card.json       A2A agent card
  POST /tasks                             A2A task (forwards to `cn -p`)
  GET  /tools                             List MCP federation tools (cached)
  POST /audit                             Run federation health audit
  GET  /logs                              Recent cn.log tail

Authority: 888 (Arif Fazil, F13 SOVEREIGN)
DITEMPA BUKAN DIBERI
"""

import json
import logging
import os
import subprocess
import sys
import time
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timezone
from urllib.parse import urlparse

# ─────────────────────────────────────────────────────────────────────
#  Configuration
# ─────────────────────────────────────────────────────────────────────
LISTEN_HOST = os.environ.get("CN_ORGAN_HOST", "127.0.0.1")
LISTEN_PORT = int(os.environ.get("CN_ORGAN_PORT", "18790"))
CN_CONFIG = os.environ.get("CN_CONFIG", "/root/.continue/config.yaml")
CN_BINARY = os.environ.get("CN_BINARY", "/usr/bin/cn")
CN_LOG = "/root/.continue/logs/cn.log"

# Federation organs (for /audit)
FEDERATION_ORGANS = {
    "arifOS": {"port": 8088, "path": "/health", "type": "http"},
    "arifosd": {"port": 18081, "path": "/health", "type": "http"},
    "WEALTH": {"port": 18082, "path": "/health", "type": "http"},
    "WELL": {"port": 18083, "path": "/health", "type": "http"},
    "GEOX": {"port": 8081, "path": "/health", "type": "http"},
    "A-FORGE": {"port": 7071, "path": "/health", "type": "http"},
    "OpenClaw": {"port": 18789, "path": "/health", "type": "http"},
    "APEX": {"port": 3002, "path": "/health", "type": "http"},
    "cn-organ": {"port": 18790, "path": "/health", "type": "http"},
}

# ─────────────────────────────────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] cn-organ: %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("cn-organ")

# ─────────────────────────────────────────────────────────────────────
#  State
# ─────────────────────────────────────────────────────────────────────
START_TIME = time.time()
REQUEST_LOCK = threading.Lock()
INFLIGHT_TASKS: dict = {}


# ─────────────────────────────────────────────────────────────────────
#  cn subprocess
# ─────────────────────────────────────────────────────────────────────
def run_cn(prompt: str, timeout: int = 120) -> dict:
    """Invoke `cn -p` with the given prompt, return result."""
    cmd = [CN_BINARY, "--config", CN_CONFIG, "--readonly", "-p", prompt]
    log.info(f"cn -p: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={
                **os.environ,
                "MINIMAX_API_KEY": os.environ.get("MINIMAX_API_KEY", ""),
            },
        )
        return {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr[:500] if proc.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout", "timeout_seconds": timeout}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def federation_audit() -> dict:
    """Ping all federation organs. Returns status per organ."""
    import urllib.request
    import urllib.error

    results = {"timestamp": datetime.now(timezone.utc).isoformat(), "organs": {}}
    for name, info in FEDERATION_ORGANS.items():
        url = f"http://localhost:{info['port']}{info['path']}"
        started = time.time()
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read().decode("utf-8", errors="replace")[:200]
                results["organs"][name] = {
                    "status": "up" if resp.status == 200 else f"http_{resp.status}",
                    "http_status": resp.status,
                    "latency_ms": int((time.time() - started) * 1000),
                    "sample": body[:120],
                }
        except urllib.error.URLError as e:
            results["organs"][name] = {
                "status": "down",
                "error": str(e.reason)[:120],
                "latency_ms": int((time.time() - started) * 1000),
            }
        except Exception as e:
            results["organs"][name] = {
                "status": "error",
                "error": str(e)[:120],
            }
    up_count = sum(1 for o in results["organs"].values() if o.get("status") == "up")
    results["summary"] = {
        "up": up_count,
        "total": len(FEDERATION_ORGANS),
        "verdict": "GREEN"
        if up_count == len(FEDERATION_ORGANS)
        else ("YELLOW" if up_count >= len(FEDERATION_ORGANS) - 1 else "RED"),
    }
    return results


# ─────────────────────────────────────────────────────────────────────
#  HTTP Handler
# ─────────────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        log.info(f"{self.address_string()} {fmt % args}")

    def _send_json(self, status: int, body: dict):
        data = json.dumps(body, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Organ", "cn-organ")
        self.send_header("X-Federation", "arifOS")
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"_raw": raw[:500]}

    # ─── GET handlers ────────────────────────────────────────────────
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            self._send_json(
                200,
                {
                    "status": "healthy",
                    "service": "cn-organ",
                    "version": "2026.06.02",
                    "uptime_seconds": int(time.time() - START_TIME),
                    "cn_binary": CN_BINARY,
                    "cn_config": CN_CONFIG,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
        elif path == "/ready":
            # Check cn binary is present and config exists
            cn_ok = os.path.isfile(CN_BINARY) and os.access(CN_BINARY, os.X_OK)
            cfg_ok = os.path.isfile(CN_CONFIG)
            ok = cn_ok and cfg_ok
            self._send_json(
                200 if ok else 503,
                {
                    "ready": ok,
                    "cn_binary": "ok" if cn_ok else "missing",
                    "config": "ok" if cfg_ok else "missing",
                },
            )
        elif path == "/.well-known/agent-card.json":
            self._send_json(
                200,
                {
                    "name": "cn-organ",
                    "version": "2026.06.02",
                    "description": "Continue CLI as arifOS Federation organ (A2A gateway to M3 + MCP)",
                    "url": f"http://{LISTEN_HOST}:{LISTEN_PORT}",
                    "protocol": "A2A v1.0.0 + arifOS bridge",
                    "capabilities": {
                        "chat": True,
                        "task_execution": True,
                        "mcp_federation": True,
                        "audit": True,
                    },
                    "endpoints": {
                        "health": "GET /health",
                        "ready": "GET /ready",
                        "tasks": "POST /tasks",
                        "tools": "GET /tools",
                        "audit": "POST /audit",
                        "logs": "GET /logs",
                    },
                    "motto": "DITEMPA BUKAN DIBERI",
                },
            )
        elif path == "/tools":
            tools = _tool_cache or {
                "_note": "tools not yet enumerated",
                "last_enumerated": None,
            }
            self._send_json(200, tools)
        elif path == "/logs":
            try:
                with open(CN_LOG, "r", errors="replace") as f:
                    lines = f.readlines()[-50:]
                self._send_json(
                    200,
                    {
                        "path": CN_LOG,
                        "lines": len(lines),
                        "tail": [l.rstrip() for l in lines],
                    },
                )
            except FileNotFoundError:
                self._send_json(200, {"path": CN_LOG, "lines": 0, "tail": []})
        else:
            self._send_json(404, {"error": "not_found", "path": path})

    # ─── POST handlers ───────────────────────────────────────────────
    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_body()

        if path == "/tasks":
            prompt = body.get("prompt") or body.get("message") or body.get("task")
            if not prompt:
                self._send_json(400, {"error": "missing 'prompt' field"})
                return
            task_id = f"cn-{int(time.time() * 1000)}"
            with REQUEST_LOCK:
                INFLIGHT_TASKS[task_id] = {
                    "prompt": prompt[:200],
                    "started": datetime.now(timezone.utc).isoformat(),
                    "status": "running",
                }
            try:
                result = run_cn(prompt, timeout=body.get("timeout_seconds", 120))
                with REQUEST_LOCK:
                    INFLIGHT_TASKS[task_id]["status"] = (
                        "done" if result.get("ok") else "failed"
                    )
                self._send_json(
                    200,
                    {
                        "task_id": task_id,
                        "ok": result.get("ok", False),
                        "result": result,
                    },
                )
            except Exception as e:
                self._send_json(500, {"task_id": task_id, "ok": False, "error": str(e)})
            finally:
                with REQUEST_LOCK:
                    INFLIGHT_TASKS.pop(task_id, None)

        elif path == "/audit":
            audit = federation_audit()
            self._send_json(200, audit)

        else:
            self._send_json(404, {"error": "not_found", "path": path})


# ─────────────────────────────────────────────────────────────────────
#  MCP tool enumeration (cached)
# ─────────────────────────────────────────────────────────────────────
_tool_cache: dict = {}
_tool_cache_time: float = 0
TOOL_CACHE_TTL = 300  # 5 minutes


def refresh_tool_cache():
    """Run `cn` once to enumerate available MCP tools, cache result."""
    global _tool_cache, _tool_cache_time
    prompt = (
        "List the names of all MCP tools you have access to. "
        "Reply as a single line of comma-separated tool names, nothing else."
    )
    result = run_cn(prompt, timeout=60)
    if result.get("ok"):
        # Parse tool names from stdout
        out = result.get("stdout", "")
        names = [n.strip() for n in out.replace("\n", ",").split(",") if n.strip()]
        _tool_cache = {
            "tools": names,
            "count": len(names),
            "last_enumerated": datetime.now(timezone.utc).isoformat(),
        }
        log.info(f"Enumerated {len(names)} MCP tools")
    else:
        _tool_cache = {
            "error": result.get("error", "unknown"),
            "last_enumerated": datetime.now(timezone.utc).isoformat(),
        }
    _tool_cache_time = time.time()


# ─────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────
def main():
    log.info(f"cn-organ starting on {LISTEN_HOST}:{LISTEN_PORT}")
    log.info(f"cn binary: {CN_BINARY}")
    log.info(f"cn config: {CN_CONFIG}")

    # Enumerate tools in background (don't block startup)
    threading.Thread(target=refresh_tool_cache, daemon=True).start()

    # Periodic tool cache refresh
    def cache_refresher():
        while True:
            time.sleep(TOOL_CACHE_TTL)
            try:
                refresh_tool_cache()
            except Exception as e:
                log.warning(f"Tool cache refresh failed: {e}")

    threading.Thread(target=cache_refresher, daemon=True).start()

    server = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), Handler)
    log.info(f"Listening on {LISTEN_HOST}:{LISTEN_PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Shutting down")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
