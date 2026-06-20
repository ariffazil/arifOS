#!/usr/bin/env python3
"""
MCP Telemetry Proxy v3 — Async server with thread-pool upstream.
Pure stdlib. No blocking on the event loop.
Intercept → Tag → Forward → Record every MCP call from all agents.
"""

import argparse
import asyncio
import json
import logging
import re
import signal
import socket
import sys
import threading
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

LOG_FILE = Path("/root/arifOS/core/mcp_telemetry/proxy.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_FILE)),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("mcp_telemetry")

CALLS_FILE = "/root/arifOS/core/mcp_telemetry/calls.jsonl"
_ledger_lock = threading.Lock()


def write_record(rec: dict):
    try:
        with _ledger_lock:
            with open(CALLS_FILE, "a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as e:
        log.error(f"Write error: {e}")


class Counters:
    def __init__(self):
        self._l = threading.Lock()
        self._c: dict = Counter()
        self._t: dict = Counter()
        self._e: dict = Counter()
        self._a: dict = Counter()

    def record(self, srv, agent, tool, err=False):
        k = (srv, agent, tool or "no-tool")
        with self._l:
            self._c[k] = self._c.get(k, 0) + 1
            self._t[srv] = self._t.get(srv, 0) + 1
            self._a[agent] = self._a.get(agent, 0) + 1
            if err:
                self._e[srv] = self._e.get(srv, 0) + 1

    def summary(self):
        with self._l:
            by_s = defaultdict(dict)
            for (s, a, t), n in self._c.items():
                by_s[s][f"{a}:{t}"] = n
            return {
                "by_server": {s: dict(v) for s, v in by_s.items()},
                "totals": dict(self._t),
                "errors": dict(self._e),
                "by_agent": dict(self._a),
                "unique_agents": len(self._a),
            }


_ctr = Counters()


class SessionMapper:
    def __init__(self, path: str):
        self.path = Path(path)
        self.map: dict = {}
        self._l = threading.Lock()
        self._stop = threading.Event()
        self._t: Optional[threading.Thread] = None
        self._pos = 0

    def _extract(self, line: str):
        try:
            d = json.loads(line)
            msg = str(d.get("0", "")) + " " + str(d.get("1", "")) + " " + str(d.get("message", ""))
            sub = str(d.get("name", ""))
            m = re.search(r"sessionId=([a-f0-9-]{36})", msg)
            if not m:
                return
            sid = m.group(1)
            agent = "unknown"
            ls = sub.lower()
            if "opencode" in ls or "opencode" in msg.lower():
                agent = "opencode"
            elif "hermes" in ls:
                agent = "hermes"
            elif "kimi" in ls or "kimi" in msg.lower():
                agent = "kimi"
            elif "codex" in ls:
                agent = "codex"
            elif "agy" in ls:
                agent = "agy"
            elif "claude" in ls:
                agent = "claude"
            elif sub == "gateway/channels/telegram":
                agent = "telegram"
            elif "agent/embedded" in sub:
                agent = "openclaw"
            with self._l:
                self.map[sid] = agent
        except Exception:
            pass

    def _scan(self):
        try:
            with self.path.open("r") as f:
                f.seek(self._pos)
                for line in f:
                    self._extract(line.strip())
                self._pos = f.tell()
        except Exception as e:
            log.debug(f"scan: {e}")

    def start(self):
        self._t = threading.Thread(target=self._loop, daemon=True, name="session_mapper")
        self._t.start()

    def _loop(self):
        while not self._stop.is_set():
            self._scan()
            self._stop.wait(5)

    def stop(self):
        self._stop.set()
        if self._t:
            self._t.join(timeout=5)

    def get(self, sid: str) -> str:
        with self._l:
            return self.map.get(sid, "unknown")

    def agents(self):
        with self._l:
            return sorted(set(self.map.values()))


_mapper: Optional[SessionMapper] = None

ROUTES = {
    "arifos":  ("127.0.0.1", 8088,  "/mcp"),
    "A-FORGE": ("127.0.0.1", 7071,  "/mcp"),
    "WEALTH":  ("127.0.0.1", 18082, "/mcp"),
    "WELL":    ("127.0.0.1", 18083, "/mcp"),
    "GEOX":    ("127.0.0.1", 8081,  "/mcp"),
}


def route(path: str):
    p = path.strip("/")
    if p.startswith("mcp/"):
        name = p[4:]
    elif p == "mcp":
        return "arifos", ROUTES["arifos"]
    else:
        return "unknown", None
    if name in ROUTES:
        return name, ROUTES[name]
    return name, None


def _sync_http_post(host: str, port: int, path: str, body: bytes,
                    hdrs: dict, srv: str, sid: str, agent: str,
                    method: str, tool: Optional[str], cid) -> tuple:
    """Run in thread pool — pure socket HTTP/1.1, never blocks event loop."""
    start = datetime.now(timezone.utc)
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(20)
        s.connect((host, port))

        # Build headers
        clean = {k: v for k, v in hdrs.items()
                 if k.lower() not in ("host", "connection", "transfer-encoding", "content-length")}
        clean["X-MCP-Telemetry-Agent"] = agent
        clean["X-MCP-Telemetry-Session"] = sid
        clean["Accept"] = "application/json"
        clean["Content-Length"] = str(len(body))

        req = f"POST {path} HTTP/1.1\r\nHost: {host}:{port}\r\n"
        for k, v in clean.items():
            req += f"{k}: {v}\r\n"
        req += "\r\n"
        s.sendall(req.encode() + body)

        # Read response
        resp = b""
        while len(resp) < 65536:
            try:
                chunk = s.recv(8192)
                if not chunk:
                    break
                resp += chunk
                # Check if we have complete body
                if b"\r\n\r\n" in resp:
                    header_end = resp.index(b"\r\n\r\n")
                    header_part = resp[:header_end].decode(errors="replace")
                    status_code = int(header_part.split("\r\n")[0].split()[1])
                    cl = 0
                    for line in header_part.split("\r\n"):
                        if line.lower().startswith("content-length:"):
                            cl = int(line.split(":")[1].strip())
                    body_start = header_end + 4
                    body_received = len(resp) - body_start
                    if body_received >= cl:
                        break
            except socket.timeout:
                break

        if not resp:
            return 502, {"error": {"code": -32000, "message": "Empty response"}}, 0, "empty"

        header_end = resp.index(b"\r\n\r\n")
        header_part = resp[:header_end].decode(errors="replace")
        status_code = int(header_part.split("\r\n")[0].split()[1])
        body_bytes = resp[header_end + 4:]

        try:
            resp_json = json.loads(body_bytes.decode(errors="replace"))
        except Exception:
            resp_json = {"raw": body_bytes.decode(errors="replace")[:500]}

        duration_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000
        is_err = status_code >= 400 or "error" in resp_json
        err_msg = resp_json.get("error", {}).get("message") if isinstance(resp_json, dict) else None

        record = {
            "schema": "mcp_telemetry/v1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mcp_server": srv,
            "method": method,
            "tool": tool,
            "caller": {"agent": agent, "session_id": sid},
            "call_id": str(cid) if cid is not None else None,
            "duration_ms": round(duration_ms, 2),
            "http_status": status_code,
            "error": err_msg,
            "request_size_bytes": len(body),
        }
        write_record(record)
        _ctr.record(srv, agent, tool, is_err)

        log.info(f"MCP_CALL server={srv} method={method} tool={tool} agent={agent} "
                 f"sid={sid[:8] if sid else '?'}.. status={status_code} dur={duration_ms:.1f}ms")
        return status_code, resp_json, duration_ms, err_msg

    except socket.timeout:
        dur = (datetime.now(timezone.utc) - start).total_seconds() * 1000
        return 504, {"error": {"code": -32000, "message": "Upstream timeout"}}, dur, "timeout"
    except Exception as e:
        dur = (datetime.now(timezone.utc) - start).total_seconds() * 1000
        return 502, {"error": {"code": -32000, "message": str(e)}}, dur, str(e)
    finally:
        if s:
            try:
                s.close()
            except Exception:
                pass


async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    try:
        # Read full request
        data = b""
        try:
            while True:
                chunk = await asyncio.wait_for(reader.read(8192), timeout=30)
                if not chunk:
                    break
                data += chunk
                if b"\r\n\r\n" in data:
                    break
        except asyncio.TimeoutError:
            return

        if not data:
            return

        lines = data.decode(errors="replace").split("\r\n")
        req = lines[0].split()
        if len(req) < 2:
            return
        method, path = req[0], req[1]

        # Parse headers
        header_end_idx = data.index(b"\r\n\r\n")
        hdr_bytes = data[:header_end_idx]
        body = data[header_end_idx + 4:]
        hdrs = {}
        for line in hdr_bytes.decode(errors="replace").split("\r\n")[1:]:
            if ": " in line:
                k, v = line.split(": ", 1)
                hdrs[k] = v

        # GET endpoints
        if method == "GET":
            if path == "/health":
                resp = json.dumps({"status": "ok", "counters": _ctr.summary()}).encode()
                writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                             b"Content-Length: %d\r\n\r\n" % len(resp) + resp)
                await writer.drain()
                return
            elif path == "/stats":
                resp = json.dumps(_ctr.summary(), indent=2).encode()
                writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                             b"Content-Length: %d\r\n\r\n" % len(resp) + resp)
                await writer.drain()
                return
            elif path == "/agents":
                resp = json.dumps({"agents": _mapper.agents() if _mapper else []}).encode()
                writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                             b"Content-Length: %d\r\n\r\n" % len(resp) + resp)
                await writer.drain()
                return
            elif path == "/sessions":
                if _mapper:
                    with _mapper._l:
                        sessions = dict(list(_mapper.map.items())[-100:])
                else:
                    sessions = {}
                resp = json.dumps({"sessions": sessions}, indent=2).encode()
                writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                             b"Content-Length: %d\r\n\r\n" % len(resp) + resp)
                await writer.drain()
                return
            elif path.startswith("/ledger"):
                limit = 50
                if "?" in path:
                    try:
                        limit = int(path.split("=")[1])
                    except Exception:
                        pass
                records = []
                try:
                    with open(CALLS_FILE) as f:
                        all_lines = f.readlines()
                    for ln in all_lines[-limit:]:
                        try:
                            records.append(json.loads(ln))
                        except Exception:
                            pass
                except FileNotFoundError:
                    pass
                resp = json.dumps({"records": records, "count": len(records)}).encode()
                writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                             b"Content-Length: %d\r\n\r\n" % len(resp) + resp)
                await writer.drain()
                return
            else:
                writer.write(b"HTTP/1.1 404 Not Found\r\n\r\n")
                await writer.drain()
                return

        if method != "POST":
            writer.write(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            await writer.drain()
            return

        # Route MCP request
        srv_name, route_info = route(path)
        if route_info is None:
            err = json.dumps({"error": {"code": -32600, "message": f"Unknown path: {path}"}}).encode()
            writer.write(b"HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\n"
                         b"Content-Length: %d\r\n\r\n" % len(err) + err)
            await writer.drain()
            return

        host, port, mcp_path = route_info

        # Parse JSON-RPC metadata
        cid, method_rpc, tool = None, "?", None
        try:
            bj = json.loads(body.decode()) if body else {}
            method_rpc = bj.get("method", "?")
            prms = bj.get("params", {})
            if isinstance(prms, dict):
                tool = prms.get("name")
            cid = bj.get("id")
        except Exception:
            pass

        sid = hdrs.get("MCP-Session", "") or hdrs.get("X-Session-ID", "") or "no-session"
        agent = _mapper.get(sid) if _mapper else "unknown"

        # Forward via thread pool (non-blocking)
        loop = asyncio.get_event_loop()
        status, resp_json, dur_ms, err_msg = await loop.run_in_executor(
            None, _sync_http_post, host, port, mcp_path, body, hdrs,
            srv_name, sid, agent, method_rpc, tool, cid
        )

        # Send response to gateway
        resp_body = json.dumps(resp_json, ensure_ascii=False).encode()
        writer.write(
            f"HTTP/1.1 {status} OK\r\nContent-Type: application/json\r\n"
            f"Content-Length: {len(resp_body)}\r\n\r\n".encode() + resp_body
        )
        await writer.drain()

    except Exception as e:
        log.error(f"Handler error from {addr}: {e}")
        try:
            err = json.dumps({"error": {"code": -32000, "message": str(e)}}).encode()
            writer.write(b"HTTP/1.1 500 Internal Error\r\nContent-Type: application/json\r\n"
                         b"Content-Length: %d\r\n\r\n" % len(err) + err)
            await writer.drain()
        except Exception:
            pass
    finally:
        try:
            writer.close()
        except Exception:
            pass


async def main(args):
    global _mapper
    _mapper = SessionMapper(args.gateway_log)
    _mapper.start()

    server = await asyncio.start_server(handle_client, "0.0.0.0", args.port)
    addr = server.sockets[0].getsockname()
    log.info(f"MCP Telemetry Proxy v3 ready on {addr}")
    log.info(f"  POST /mcp/arifos  → arifOS MCP")
    log.info(f"  POST /mcp/A-FORGE → A-FORGE")
    log.info(f"  GET  /health      → health + counters")
    log.info(f"  GET  /stats       → per-server/agent counts")
    log.info(f"  GET  /ledger      → recent call records")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCP Telemetry Proxy v3")
    parser.add_argument("--port", type=int, default=8092)
    parser.add_argument("--gateway-log", default="/tmp/openclaw/openclaw-2026-06-17.log")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        log.info("Shutdown.")
        if _mapper:
            _mapper.stop()
