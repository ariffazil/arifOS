#!/usr/bin/env python3
# =============================================================================
# arifOS Phase 1 — apexd Observability Daemon
# =============================================================================
# SEAL    : seal-20260523T110000-DITEMPA-BUKAN-DIBERI
# EPOCH   : 2026-05-23T11:00:00+08:00
# PHASE   : 1-OBSERVABILITY
# PURPOSE  : apexd can see everything. Cannot yet act autonomously.
#
# Organ endpoints (VPS localhost):
#   arifOS  → localhost:8088   (arifOS MCP Kernel)
#   GEOX    → localhost:18081  (GEOX Earth Intelligence)
#   WEALTH  → localhost:18082  (WEALTH Capital Thermodynamics)
#   WELL    → localhost:8083   (WELL Human Readiness — dead)
#
# Naming constraint:
#   arifos_ = internal daemon tools only (this file)
#   arif_   = external MCP tools (NEVER TOUCH)
# =============================================================================

from __future__ import annotations

import hashlib
import json
import os
import signal
import socket
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# =============================================================================
# syseye: sd_notify integration (WatchdogSec=120 in systemd)
# No external deps — uses ctypes to call libsystemd.so.0 directly.
# If systemd is not running, this silently degrades to no-op.
# =============================================================================

def _send_watchdog_pulse() -> bool:
    """Send WATCHDOG=1 to systemd. Returns True if successful, False if not."""
    try:
        import ctypes
        libc = ctypes.CDLL("libsystemd.so.0", use_errno=True)
        sd_notify = libc.sd_notify
        sd_notify.argtypes = [ctypes.c_int, ctypes.c_char_p]
        sd_notify.restype = ctypes.c_int
        result = sd_notify(0, b"WATCHDOG=1")
        return result == 0
    except (OSError, AttributeError):
        return False


# =============================================================================
# CONFIGURATION
# =============================================================================

VAULT_PATH: str = os.environ.get("APEXD_VAULT", "/var/log/apexd/vault.jsonl")
STATE_PATH: str = os.environ.get("APEXD_STATE", "/var/run/apexd/state.json")
PID_PATH: str = os.environ.get("APEXD_PID", "/var/run/apexd/apexd.pid")
TICK_INTERVAL: int = int(os.environ.get("APEXD_TICK", "60"))
HOSTNAME: str = socket.gethostname()

# Organ definitions (localhost ports on VPS compose stack)
ORGANS: dict[str, dict] = {
    "arifOS": {
        "port": 8080,
        "health_path": "/health",
        "label": "arifOS MCP Kernel",
    },
    "GEOX": {
        "port": 8081,
        "health_path": "/health",
        "label": "GEOX Earth Intelligence",
    },
    "WEALTH": {
        "port": 8082,
        "health_path": "/health",
        "label": "WEALTH Capital Thermodynamics",
    },
    "WELL": {
        "port": 8083,
        "health_path": "/health",
        "label": "WELL Human Readiness",
    },
}

# =============================================================================
# DATACLASSES (no external deps — pure stdlib)
# =============================================================================


@dataclass
class HealthResult:
    endpoint: str
    status: str  # UP | DEGRADED | DOWN | UNKNOWN
    latency_ms: float
    timestamp: str
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class SenseState:
    hostname: str
    tick: int
    timestamp: str
    uptime_seconds: float
    containers_running: int
    containers_total: int
    disk_used_pct: float
    disk_available_gb: float
    memory_used_mb: float
    memory_available_mb: float
    load_avg_1m: float
    last_vault_entries: int
    last_hold_tick: Optional[int]
    organs: dict[str, HealthResult] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items() if k != "organs"}
        d["organs"] = {k: v.to_dict() for k, v in self.organs.items()}
        return d


@dataclass
class VaultEntry:
    timestamp: str
    actor: str
    tool_name: str
    inputs_hash: str
    result: str
    risk_class: str
    notes: str
    tick: Optional[int] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


# =============================================================================
# UTILITIES
# =============================================================================


def hash_inputs(data: dict) -> str:
    """SHA256 hash (first 16 chars) of canonical JSON of input data."""
    canonical = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: str) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


# =============================================================================
# arifos_health_check — Ping all 4 organs, record status + latency
# =============================================================================


def arifos_health_check() -> dict[str, HealthResult]:
    """
    Ping each organ health endpoint via TCP socket.
    Returns: { organ_name: HealthResult }
    Status: UP (<500ms) | DEGRADED (500-2000ms) | DOWN (timeout/refused) | UNKNOWN (other)
    """
    results: dict[str, HealthResult] = {}
    ts = now_iso()

    for name, cfg in ORGANS.items():
        port = cfg["port"]
        path = cfg["health_path"]
        exc_msg: str | None = None

        start = time.monotonic()
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
                request = f"GET {path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
                sock.sendall(request.encode())
                _ = sock.recv(1024)
            latency_ms = (time.monotonic() - start) * 1000

            if latency_ms < 500:
                status = "UP"
            else:
                status = "DEGRADED"

        except socket.timeout:
            latency_ms = (time.monotonic() - start) * 1000
            status = "DOWN"
            exc_msg = "socket.timeout"
        except ConnectionRefusedError:
            latency_ms = (time.monotonic() - start) * 1000
            status = "DOWN"
            exc_msg = "ConnectionRefusedError"
        except Exception as exc:
            latency_ms = (time.monotonic() - start) * 1000
            status = "UNKNOWN"
            exc_msg = str(exc)

        results[name] = HealthResult(
            endpoint=f"localhost:{port}",
            status=status,
            latency_ms=round(latency_ms, 2),
            timestamp=ts,
            error=exc_msg,
        )

    return results


# =============================================================================
# arifos_sense_state — Read VPS system state
# =============================================================================


def arifos_sense_state(
    tick: int,
    uptime_start: float,
    last_vault_entries: int,
    last_hold_tick: Optional[int],
) -> SenseState:
    """
    Read: containers, disk, memory, load average.
    Reads: tick count, last vault write, last HOLD event.
    """
    ts = now_iso()

    # Container counts via docker
    try:
        result = subprocess.run(
            ["docker", "ps", "-q"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        containers_running = len([c for c in result.stdout.strip().split("\n") if c])
        result_total = subprocess.run(
            ["docker", "ps", "-aq"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        containers_total = len([c for c in result_total.stdout.strip().split("\n") if c])
    except Exception:
        containers_running = -1
        containers_total = -1

    # Disk usage
    try:
        result = subprocess.run(
            ["df", "-BG", "/"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        lines = result.stdout.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            avail_gb = int(parts[3].rstrip("G"))
            used_pct = int(parts[4].rstrip("%"))
            disk_available_gb = avail_gb
            disk_used_pct = used_pct
        else:
            disk_available_gb = -1
            disk_used_pct = -1
    except Exception:
        disk_available_gb = -1
        disk_used_pct = -1

    # Memory from /proc/meminfo
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()
        mem: dict[str, int] = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                mem[parts[0].rstrip(":")] = int(parts[1])
        total_kb = mem.get("MemTotal", 0)
        available_kb = mem.get("MemAvailable", mem.get("MemFree", 0))
        used_kb = total_kb - available_kb
        memory_used_mb = round(used_kb / 1024, 1)
        memory_available_mb = round(available_kb / 1024, 1)
    except Exception:
        memory_used_mb = -1
        memory_available_mb = -1

    # Load average
    try:
        load1, _, _ = os.getloadavg()
        load_avg_1m = round(load1, 2)
    except Exception:
        load_avg_1m = -1.0

    return SenseState(
        hostname=HOSTNAME,
        tick=tick,
        timestamp=ts,
        uptime_seconds=round(time.time() - uptime_start, 1),
        containers_running=containers_running,
        containers_total=containers_total,
        disk_used_pct=disk_used_pct,
        disk_available_gb=disk_available_gb,
        memory_used_mb=memory_used_mb,
        memory_available_mb=memory_available_mb,
        load_avg_1m=load_avg_1m,
        last_vault_entries=last_vault_entries,
        last_hold_tick=last_hold_tick,
    )


# =============================================================================
# arifos_vault_append — Append-only JSONL event log
# =============================================================================


def arifos_vault_append(
    actor: str,
    tool_name: str,
    inputs: dict,
    result: str,
    risk_class: str,
    notes: str,
    tick: Optional[int] = None,
) -> VaultEntry:
    """
    Appends structured event to local JSONL file.
    Each entry: { timestamp, actor, tool_name, inputs_hash, result, risk_class, notes, tick }
    Append-only. Never overwrite. Never delete.
    """
    entry = VaultEntry(
        timestamp=now_iso(),
        actor=actor,
        tool_name=tool_name,
        inputs_hash=hash_inputs(inputs),
        result=result,
        risk_class=risk_class,
        notes=notes,
        tick=tick,
    )

    vault_file = ensure_dir(VAULT_PATH)
    with open(vault_file, "a") as f:
        f.write(json.dumps(entry.to_dict(), default=str) + "\n")

    return entry


def vault_entry_count() -> int:
    """Count entries in vault (fast line count)."""
    try:
        with open(VAULT_PATH, "r") as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0


# =============================================================================
# DAEMON STATE PERSISTENCE
# =============================================================================


def load_daemon_state() -> dict:
    """Load tick count and last hold tick from state file."""
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "tick": 0,
            "last_hold_tick": None,
            "restart_count": 0,
            "first_start": now_iso(),
        }


def save_daemon_state(state: dict) -> None:
    """Persist tick count and last hold tick."""
    ensure_dir(STATE_PATH)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, default=str)


def write_pid() -> None:
    """Write PID file."""
    ensure_dir(PID_PATH)
    with open(PID_PATH, "w") as f:
        f.write(str(os.getpid()))


# =============================================================================
# GRACEFUL SHUTDOWN
# =============================================================================

shutdown_requested = False


def request_shutdown(signum, frame):
    global shutdown_requested
    shutdown_requested = True
    print(
        f"\n[apexd] SIGTERM received — graceful shutdown (tick {daemon_state.get('tick', '?')})"
    )


# =============================================================================
# MAIN TICK LOOP
# =============================================================================

daemon_state: dict = {}


def run_tick(tick: int, uptime_start: float) -> tuple[Optional[int], int]:
    """
    Run one tick: health check → sense state → vault append.
    Returns: (last_hold_tick, vault_entry_count)
    """
    # 1. Health check all organs
    health_results = arifos_health_check()

    # 2. Sense system state
    last_hold = daemon_state.get("last_hold_tick")
    vault_count_before = vault_entry_count()
    state = arifos_sense_state(
        tick=tick,
        uptime_start=uptime_start,
        last_vault_entries=vault_count_before,
        last_hold_tick=last_hold,
    )
    state.organs = health_results

    # 3. Vault append — tick event
    any_down = any(r.status == "DOWN" for r in health_results.values())
    any_degraded = any(r.status == "DEGRADED" for r in health_results.values())

    if any_down:
        risk_class = "HIGH"
        result_str = "DOWN"
        notes = f"Organ(s) DOWN: {[n for n, r in health_results.items() if r.status == 'DOWN']}"
    elif any_degraded:
        risk_class = "MEDIUM"
        result_str = "DEGRADED"
        notes = (
            f"Organ(s) DEGRADED: {[n for n, r in health_results.items() if r.status == 'DEGRADED']}"
        )
    else:
        risk_class = "LOW"
        result_str = "UP"
        notes = "All organs operational"

    arifos_vault_append(
        actor="apexd",
        tool_name="arifos_health_check",
        inputs={"organs": list(health_results.keys())},
        result=result_str,
        risk_class=risk_class,
        notes=notes,
        tick=tick,
    )

    # 4. Vault append — sense state summary
    arifos_vault_append(
        actor="apexd",
        tool_name="arifos_sense_state",
        inputs={
            "containers": f"{state.containers_running}/{state.containers_total}",
            "disk_pct": state.disk_used_pct,
            "load_1m": state.load_avg_1m,
        },
        result="OK",
        risk_class="LOW",
        notes=f"tick={tick} uptime={state.uptime_seconds}s",
        tick=tick,
    )

    vault_count_after = vault_entry_count()
    return last_hold, vault_count_after


# =============================================================================
# DAEMON MAIN
# =============================================================================


def main():
    global daemon_state

    # Signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, request_shutdown)
    signal.signal(signal.SIGINT, request_shutdown)

    # Ensure vault directory exists
    ensure_dir(VAULT_PATH)

    # Load persisted state
    daemon_state = load_daemon_state()
    tick = daemon_state.get("tick", 0)
    restart_count = daemon_state.get("restart_count", 0)
    uptime_start = time.time()

    # Write PID
    write_pid()

    print("=" * 60)
    print("arifOS Phase 1 — apexd Observability Daemon")
    print(f"SEAL    : seal-20260523T110000-DITEMPA-BUKAN-DIBERI")
    print(f"EPOCH   : {now_iso()}")
    print(f"Vault   : {VAULT_PATH}")
    print(f"State   : {STATE_PATH}")
    print(f"Tick    : every {TICK_INTERVAL}s")
    print(f"Organs  : {list(ORGANS.keys())}")
    print("=" * 60)

    # Log startup to vault
    arifos_vault_append(
        actor="apexd",
        tool_name="arifos_startup",
        inputs={
            "tick_interval": TICK_INTERVAL,
            "vault_path": VAULT_PATH,
            "hostname": HOSTNAME,
            "restart_count": restart_count,
        },
        result="STARTED",
        risk_class="LOW",
        notes=f"apexd Phase 1 started — tick {tick}",
        tick=tick,
    )

    # Main loop
    while not shutdown_requested:
        tick += 1
        daemon_state["tick"] = tick

        tick_start = time.time()

        try:
            last_hold, vault_count = run_tick(tick, uptime_start)
            daemon_state["last_hold_tick"] = last_hold
            save_daemon_state(daemon_state)

            # syseye: send WATCHDOG=1 to systemd (resets WatchdogSec=120 timer)
            watchdog_ok = _send_watchdog_pulse()

            print(
                f"[{now_iso()}] tick={tick} "
                f"vault_entries={vault_count} "
                f"uptime={int(time.time() - uptime_start)}s "
                f"syseye={'OK' if watchdog_ok else 'MISSING'}"
            )

        except Exception as exc:
            arifos_vault_append(
                actor="apexd",
                tool_name="arifos_tick_error",
                inputs={"tick": tick},
                result="ERROR",
                risk_class="HIGH",
                notes=f"Tick failed: {exc}",
                tick=tick,
            )
            # syseye: still send pulse — process is alive, tick failed is recoverable
            _send_watchdog_pulse()
            print(f"[{now_iso()}] tick={tick} ERROR: {exc}")

        # Sleep for tick interval, accounting for tick duration
        elapsed = time.time() - tick_start
        sleep_time = max(1.0, TICK_INTERVAL - elapsed)
        try:
            time.sleep(sleep_time)
        except InterruptedError:
            break

    # Graceful shutdown
    print(f"\n[apexd] Shutdown complete after {daemon_state.get('tick', 0)} ticks.")
    arifos_vault_append(
        actor="apexd",
        tool_name="arifos_shutdown",
        inputs={"total_ticks": daemon_state.get("tick", 0)},
        result="SHUTDOWN",
        risk_class="LOW",
        notes=f"Graceful SIGTERM shutdown after {daemon_state.get('tick', 0)} ticks",
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
