#!/usr/bin/env python3
"""NATS Prometheus exporter — exposes /metrics from NATS /varz and /jsz.

Binds 127.0.0.1:9222 (no external exposure).
Polls NATS HTTP monitoring on 127.0.0.1:8222.
"""
from __future__ import annotations

import json
import os
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

NATS_URL = os.environ.get("NATS_MONITOR_URL", "http://127.0.0.1:8222")
LISTEN_HOST = os.environ.get("EXPORTER_HOST", "127.0.0.1")
LISTEN_PORT = int(os.environ.get("EXPORTER_PORT", "9222"))
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "15"))

_metrics: dict[str, Any] = {}
_lock = threading.Lock()


def _fetch(path: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(f"{NATS_URL}{path}", timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return {}


def _gauge(name: str, value: float | int, labels: str = "") -> str:
    return f"{name}{labels} {value if value is not None else 0}\n"


def _collect() -> str:
    with _lock:
        data = dict(_metrics)

    varz = data.get("varz", {})
    jsz = data.get("jsz", {})

    lines: list[str] = []
    lines.append("# HELP nats_server_up NATS monitoring reachable\n")
    lines.append("# TYPE nats_server_up gauge\n")
    lines.append(_gauge("nats_server_up", 1 if varz else 0))

    lines.append("# HELP nats_server_connections Current client connections\n")
    lines.append("# TYPE nats_server_connections gauge\n")
    lines.append(_gauge("nats_server_connections", varz.get("connections")))

    lines.append("# HELP nats_server_subscriptions Current subscriptions\n")
    lines.append("# TYPE nats_server_subscriptions gauge\n")
    lines.append(_gauge("nats_server_subscriptions", varz.get("subscriptions")))

    lines.append("# HELP nats_server_slow_consumers Total slow consumers\n")
    lines.append("# TYPE nats_server_slow_consumers counter\n")
    lines.append(_gauge("nats_server_slow_consumers", varz.get("slow_consumers")))

    lines.append("# HELP nats_server_mem_bytes Memory used in bytes\n")
    lines.append("# TYPE nats_server_mem_bytes gauge\n")
    lines.append(_gauge("nats_server_mem_bytes", varz.get("mem")))

    lines.append("# HELP nats_server_cpu_percent CPU usage percent\n")
    lines.append("# TYPE nats_server_cpu_percent gauge\n")
    lines.append(_gauge("nats_server_cpu_percent", varz.get("cpu")))

    lines.append("# HELP nats_server_uptime_seconds Server uptime in seconds\n")
    lines.append("# TYPE nats_server_uptime_seconds gauge\n")
    lines.append(_gauge("nats_server_uptime_seconds", varz.get("uptime_ns", 0) / 1e9 if varz.get("uptime_ns") else None))

    lines.append("# HELP nats_jetstream_streams Number of JetStream streams\n")
    lines.append("# TYPE nats_jetstream_streams gauge\n")
    lines.append(_gauge("nats_jetstream_streams", jsz.get("streams")))

    lines.append("# HELP nats_jetstream_messages_total Total JetStream messages\n")
    lines.append("# TYPE nats_jetstream_messages_total gauge\n")
    lines.append(_gauge("nats_jetstream_messages_total", jsz.get("messages")))

    lines.append("# HELP nats_jetstream_bytes_total Total JetStream bytes\n")
    lines.append("# TYPE nats_jetstream_bytes_total gauge\n")
    lines.append(_gauge("nats_jetstream_bytes_total", jsz.get("bytes")))

    lines.append("# HELP nats_jetstream_consumers Number of JetStream consumers\n")
    lines.append("# TYPE nats_jetstream_consumers gauge\n")
    lines.append(_gauge("nats_jetstream_consumers", jsz.get("consumers")))

    return "".join(lines)


def _poll_loop() -> None:
    while True:
        try:
            varz = _fetch("/varz")
            jsz = _fetch("/jsz")
            with _lock:
                _metrics["varz"] = varz
                _metrics["jsz"] = jsz
        except Exception:
            pass
        time.sleep(POLL_INTERVAL)


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/metrics":
            body = _collect().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/health":
            body = b'{"status":"healthy"}\n'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        pass


def main() -> None:
    threading.Thread(target=_poll_loop, daemon=True).start()
    server = HTTPServer((LISTEN_HOST, LISTEN_PORT), _Handler)
    print(f"NATS Prometheus exporter listening on {LISTEN_HOST}:{LISTEN_PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
