# =============================================================================
# MODULE 8A — arifos_* VPS CONTROL PLANE TOOLS (Phase 1: Observability)
# =============================================================================
# SEAL    : 999-SEAL-PHASE1-VPS-DAEMON-20260523
# PHASE   : 1 — OBSERVABILITY (no autonomous mutation)
# Trinity : OPENCLAW Δ · Hermes Ω · APEX PRIME Ψ
#
# arifos_* = internal daemon tools (THIS MODULE)
# arif_*   = external MCP tools (DO NOT TOUCH — MODULE 6+7)
#
# Phase 1 goal: arifosd can SEE everything. CANNOT act autonomously yet.
# Naming rule: arifos_ prefix = internal daemon only.
# =============================================================================

import subprocess
import urllib.request
import urllib.error
from collections import defaultdict

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

# Organ endpoints to monitor
ARIFOS_ORGANS = {
    "mcp":   "https://mcp.arif-fazil.com/health",
    "geox":  "https://geox.arif-fazil.com/health",
    "wealth":"https://wealth.arif-fazil.com/health",
    "well":  "https://well.arif-fazil.com/health",
}

# Tick interval (default 60s, configurable via --tick)
DEFAULT_TICK_INTERVAL = 60

# Vault paths
VAULT_LOG         = "/var/log/arifosd/vault.jsonl"
OBSERVABILITY_LOG = "/var/log/arifosd/observability.jsonl"
DAEMON_METRICS_FILE = "/var/run/arifosd/metrics.json"

# Reusable metric counters
DAEMON_START   = time.time()
DAEMON_METRICS = {
    "ticks": 0,
    "holds": 0,
    "seals": 0,
    "organs_up": 0,
    "organs_down": 0,
    "restarts": 0,
    "last_tick": None,
    "last_hold": None,
}


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 1 — arifos_health_check
# Class: HEARTBEAT
# Phase 1 task: Ping all 4 organs. Record status + latency + timestamp.
# ─────────────────────────────────────────────────────────────────────────────

def arifos_health_check(organ: str | None = None) -> dict:
    """
    HEARTBEAT — Check daemon liveness + organ health.

    Without organ arg: checks daemon itself.
    With organ arg: pings specific organ endpoint.
    Returns: { endpoint, status, latency_ms, timestamp }

    Status values: UP / DEGRADED / DOWN / UNKNOWN
    """
    result = {
        "tool": "arifos_health_check",
        "canonical": "arifos_health_check[HEARTBEAT]",
        "epoch": datetime.now(timezone.utc).isoformat(),
    }

    if organ is None:
        # Check daemon itself — socket reachable + vault accessible
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect(SOCK_PATH)
            sock.close()
            daemon_status = "UP"
        except Exception:
            daemon_status = "DOWN"

        vault_ok = Path(VAULT_PATH).exists()
        result["daemon_status"] = daemon_status
        result["vault_accessible"] = vault_ok
        result["uptime_seconds"] = round(time.time() - DAEMON_START, 1)
        result["status"] = "UP" if daemon_status == "UP" and vault_ok else "DEGRADED"
        return result

    # Ping specific organ
    if organ not in ARIFOS_ORGANS:
        return {"tool": "arifos_health_check", "organ": organ,
                "status": "UNKNOWN", "reason": f"Unknown organ: {organ}"}

    url = ARIFOS_ORGANS[organ]
    try:
        start = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "arifosd/0.1.0"})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            latency_ms = round((time.time() - start) * 1000, 1)
            status_code = resp.status
            result["endpoint"]  = url
            result["organ"]     = organ
            result["status_code"] = status_code
            result["latency_ms"] = latency_ms
            result["timestamp"] = datetime.now(timezone.utc).isoformat()
            if status_code == 200:
                result["status"] = "UP"
            elif 200 <= status_code < 300:
                result["status"] = "UP"
            elif 300 <= status_code < 500:
                result["status"] = "DEGRADED"
            else:
                result["status"] = "DOWN"
    except urllib.error.HTTPError as e:
        result["endpoint"]  = url
        result["organ"]     = organ
        result["status"]    = "DOWN"
        result["latency_ms"] = None
        result["error"]     = f"HTTP {e.code}"
        result["timestamp"] = datetime.now(timezone.utc).isoformat()
    except Exception as e:
        result["endpoint"]  = url
        result["organ"]     = organ
        result["status"]    = "DOWN"
        result["latency_ms"] = None
        result["error"]     = str(e)[:80]
        result["timestamp"] = datetime.now(timezone.utc).isoformat()

    return result


def arifos_ping_all_organs() -> dict:
    """
    Ping all 4 organs in one call. Used by the tick loop.
    Returns: { organs: {name: status_result}, summary: {up, down, total} }
    """
    organs = {}
    for name in ARIFOS_ORGANS:
        organs[name] = arifos_health_check(organ=name)
        time.sleep(0.2)  # Rate limit: 200ms between checks

    up_count   = sum(1 for r in organs.values() if r.get("status") == "UP")
    down_count = sum(1 for r in organs.values() if r.get("status") == "DOWN")
    degraded   = sum(1 for r in organs.values() if r.get("status") == "DEGRADED")

    return {
        "tool": "arifos_ping_all_organs",
        "canonical": "arifos_ping_all_organs[HEARTBEAT]",
        "organs": organs,
        "summary": {
            "up": up_count,
            "down": down_count,
            "degraded": degraded,
            "total": len(ARIFOS_ORGANS),
        },
        "epoch": datetime.now(timezone.utc).isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 2 — arifos_sense_state
# Class: SENSE
# Phase 1 task: Read machine state — containers, disk, memory, load, vault state.
# ─────────────────────────────────────────────────────────────────────────────

def arifos_sense_state() -> dict:
    """
    SENSE — Read machine state, config, and arifosd internal metrics.
    Returns normalized JSON state packet.

    Reads:
      - Running containers (docker ps)
      - Disk usage (df -h)
      - Memory (free -m)
      - Load average (uptime)
      - arifosd tick count + last vault write + last HOLD event
    """
    state: dict = {
        "tool": "arifos_sense_state",
        "canonical": "arifos_sense_state[SENSE]",
        "epoch_unix": time.time(),
        "hostname": socket.gethostname(),
    }

    # Disk usage
    try:
        out = subprocess.check_output(
            ["df", "-h", "--output=target,size,used,avail,pcent"],
            text=True, timeout=5
        )
        lines = out.strip().split("\n")
        disks = []
        for line in lines[1:]:
            parts = [p.strip() for p in line.split() if p.strip()]
            if len(parts) >= 5:
                disks.append({
                    "mount": parts[0],
                    "total": parts[1],
                    "used":  parts[2],
                    "avail": parts[3],
                    "pct":   parts[4].replace("%", ""),
                })
        state["disk"] = disks
    except Exception as e:
        state["disk"] = {"error": str(e)[:80]}

    # Memory
    try:
        out = subprocess.check_output(["free", "-m"], text=True, timeout=5)
        lines = out.strip().split("\n")
        if len(lines) >= 2:
            mem_parts = lines[1].split()
            state["memory_mb"] = {
                "total": int(mem_parts[1]) if len(mem_parts) > 1 else 0,
                "used":  int(mem_parts[2]) if len(mem_parts) > 2 else 0,
                "free":  int(mem_parts[3]) if len(mem_parts) > 3 else 0,
            }
    except Exception as e:
        state["memory_mb"] = {"error": str(e)[:80]}

    # Load average
    try:
        out = subprocess.check_output(["uptime"], text=True, timeout=5)
        load_match = re.search(r"load average:\s+([\d.,]+)", out)
        if load_match:
            state["load_avg"] = [float(x) for x in load_match.group(1).split(", ")]
        else:
            state["load_avg"] = []
    except Exception:
        state["load_avg"] = []

    # Docker containers
    try:
        out = subprocess.check_output(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}\t{{.Ports}}"],
            text=True, timeout=10
        )
        containers = []
        for line in out.strip().split("\n"):
            parts = line.split("\t")
            if parts:
                containers.append({
                    "name":   parts[0] if len(parts) > 0 else "?",
                    "status": parts[1] if len(parts) > 1 else "?",
                    "ports":  parts[2] if len(parts) > 2 else "",
                })
        state["containers"] = containers
        state["container_count"] = len(containers)
    except Exception as e:
        state["containers"] = []
        state["container_error"] = str(e)[:80]

    # Daemon metrics
    state["daemon_metrics"] = {
        "ticks":        DAEMON_METRICS["ticks"],
        "holds":        DAEMON_METRICS["holds"],
        "seals":        DAEMON_METRICS["seals"],
        "last_tick":    DAEMON_METRICS["last_tick"],
        "last_hold":    DAEMON_METRICS["last_hold"],
        "uptime_s":     round(time.time() - DAEMON_START, 1),
    }

    # Vault state
    vault_manifest_path = Path(VAULT_PATH) / "manifest.json"
    if vault_manifest_path.exists():
        try:
            manifest = json.loads(vault_manifest_path.read_text())
            state["vault"] = {
                "path":       VAULT_PATH,
                "events":     manifest.get("events", 0),
                "last_hash":  manifest.get("last_hash", "?")[:16],
                "version":    manifest.get("version", "?"),
            }
        except Exception:
            state["vault"] = {"error": "manifest unreadable"}
    else:
        state["vault"] = {"status": "not_initialized"}

    # observability log state
    obs_log = Path(OBSERVABILITY_LOG)
    if obs_log.exists():
        with open(obs_log) as f:
            lines = f.readlines()
        state["observability"] = {
            "path": OBSERVABILITY_LOG,
            "entries": len(lines),
            "last_entry": lines[-1][:120] if lines else "",
        }
    else:
        state["observability"] = {"status": "not_initialized"}

    return state


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 3 — arifos_vault_append (Phase 1 version)
# Class: LOG
# Phase 1 task: Append structured event to vault.jsonl
# Each entry: { timestamp, actor, tool_name, inputs_hash, result, risk_class, notes }
# ─────────────────────────────────────────────────────────────────────────────

def arifos_vault_append(
    entry_type: str,
    actor: str = "arifOS-daemon",
    tool_name: str = "unknown",
    inputs_hash: str = "",
    result_status: str = "OK",
    risk_class: str = "SAFE",
    notes: str = "",
    session_id: str | None = None,
    extra: dict | None = None,
) -> dict:
    """
    LOG — Append structured event to /var/log/arifosd/vault.jsonl
    Append-only. Never overwrite. Never delete.

    Required fields: timestamp, actor, tool_name, inputs_hash, result, risk_class

    Returns: { sealed: bool, entry_id, chain_hash, vault_path }
    """
    Path("/var/log/arifosd").mkdir(parents=True, exist_ok=True)

    entry: dict = {
        "timestamp":    datetime.now(timezone.utc).isoformat(),
        "actor":        actor,
        "tool_name":    tool_name,
        "inputs_hash":  inputs_hash or "none",
        "result":       result_status,
        "risk_class":   risk_class,
        "notes":        notes,
        "entry_type":   entry_type,
        "session_id":   session_id or "daemon",
        "hostname":     socket.gethostname(),
    }
    if extra:
        entry["extra"] = extra

    # Compute content hash for auditability
    content_str = json.dumps(entry, sort_keys=True)
    content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:16]

    # Read previous hash for chain
    prev_hash = "GENESIS"
    try:
        vault_log = Path(VAULT_LOG)
        if vault_log.exists():
            with open(vault_log) as f:
                lines = f.readlines()
            if lines:
                prev_entry = json.loads(lines[-1])
                prev_hash  = prev_entry.get("chain_hash", "GENESIS")
    except Exception:
        pass

    # Chain hash
    chain_hash = hashlib.sha256(f"{prev_hash}{content_hash}".encode()).hexdigest()[:16]
    entry["entry_id"]   = f"ent-{content_hash[:8]}"
    entry["chain_hash"] = chain_hash
    entry["prev_hash"]  = prev_hash

    # Write to vault.jsonl
    try:
        with open(VAULT_LOG, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        sealed = True
    except Exception as e:
        entry["write_error"] = str(e)[:80]
        sealed = False

    return {
        "tool":       "arifos_vault_append",
        "canonical":  "arifos_vault_append[LOG]",
        "sealed":     sealed,
        "entry_id":   entry.get("entry_id"),
        "chain_hash": chain_hash,
        "vault_path": VAULT_LOG,
        "epoch":      entry["timestamp"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 4 — arifos_observability_append (bonus, Phase 1)
# Class: SENSE
# Shorthand for high-frequency tick events (not all need full vault chaining)
# ─────────────────────────────────────────────────────────────────────────────

def arifos_observability_append(tick_data: dict) -> dict:
    """
    SENSE — Append high-frequency tick data to observability.jsonl
    This is separate from vault.jsonl — higher frequency, lower stakes.

    tick_data should include: tick_id, organ_results, sense_state summary
    """
    Path("/var/log/arifosd").mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tick_id":   tick_data.get("tick_id", "?"),
        "organs":    tick_data.get("organs", {}),
        "summary":   tick_data.get("summary", {}),
        "sense":     tick_data.get("sense", {}),
        "hostname":  socket.gethostname(),
    }

    try:
        with open(OBSERVABILITY_LOG, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return {"status": "logged", "entry_count": 1}
    except Exception as e:
        return {"status": "error", "error": str(e)[:80]}


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 5 — arifos_watchdog_restart_alert
# Class: LOG (HEARTBEAT variant)
# Called by watchdog timer. Logs restart event + increments restart counter.
# ─────────────────────────────────────────────────────────────────────────────

def arifos_watchdog_alert(reason: str = "watchdog_timer") -> dict:
    """
    LOG (HEARTBEAT) — Log a watchdog restart event to vault.
    Prevents restart storm: tracks restarts in last hour.
    """
    # Read current restart count from metrics file
    metrics_path = Path("/var/run/arifosd/restart_count.json")
    try:
        if metrics_path.exists():
            metrics = json.loads(metrics_path.read_text())
        else:
            metrics = {"count": 0, "reset_at": None}
    except Exception:
        metrics = {"count": 0, "reset_at": None}

    # Reset if more than 1 hour since last reset
    now = time.time()
    if metrics.get("reset_at"):
        if now - metrics["reset_at"] > 3600:
            metrics = {"count": 0, "reset_at": now}
    else:
        metrics["reset_at"] = now

    metrics["count"] += 1

    # Cap at 5 restarts per hour (matches systemd StartLimitBurst=5)
    if metrics["count"] > 5:
        return {
            "status": "BLOCKED",
            "reason": "Restart storm prevention: >5 restarts in 1 hour",
            "count":  metrics["count"],
            "action": "No restart — manual intervention required",
        }

    # Write updated metrics
    Path("/var/run/arifosd").mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics))

    # Log to vault
    seal = arifos_vault_append(
        entry_type="watchdog_alert",
        actor="arifOS-watchdog",
        tool_name="arifos_watchdog_alert",
        result_status="RESTART",
        risk_class="SAFE",
        notes=f"Watchdog triggered restart. Reason: {reason}",
        extra={"restart_count": metrics["count"], "reason": reason},
    )

    # Increment daemon restart counter
    DAEMON_METRICS["restarts"] = metrics["count"]

    return {
        "status": "RESTART_LOGGED",
        "restart_count": metrics["count"],
        "seal": seal.get("entry_id"),
        "vault_chain": seal.get("chain_hash"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# DAEMON METRICS PERSISTENCE
# ─────────────────────────────────────────────────────────────────────────────

def _save_daemon_metrics():
    """Save current metrics to /var/run/arifosd/metrics.json"""
    Path("/var/run/arifosd").mkdir(parents=True, exist_ok=True)
    try:
        Path("/var/run/arifosd/metrics.json").write_text(
            json.dumps(DAEMON_METRICS, indent=2)
        )
    except Exception:
        pass


def _load_daemon_metrics():
    """Load metrics from /var/run/arifosd/metrics.json"""
    try:
        path = Path("/var/run/arifosd/metrics.json")
        if path.exists():
            loaded = json.loads(path.read_text())
            DAEMON_METRICS.update(loaded)
    except Exception:
        pass


# =============================================================================
# PHASE 1 MAIN LOOP — arifos_vps_tick()
# This is the observability loop. Runs every tick interval.
# Does NOT make autonomous mutations. Only observes, logs, and reports.
# =============================================================================

def arifos_vps_tick(tick_id: str | None = None, tick_interval: int = DEFAULT_TICK_INTERVAL) -> dict:
    """
    PHASE 1 TICK LOOP — ONE tick of the VPS observability daemon.

    Sequence:
      1. HEARTBEAT → arifos_health_check (daemon self-check)
      2. SENSE     → arifos_sense_state (machine state)
      3. HEARTBEAT → arifos_ping_all_organs (4 organ health pings)
      4. LOG       → arifos_observability_append (tick data)
      5. LOG       → arifos_vault_append (structured vault event)

    Phase 1: NO gate, NO dispatch, NO autonomous action.
    """
    tick_id = tick_id or f"tick-{int(time.time())}"
    epoch   = datetime.now(timezone.utc).isoformat()

    result = {
        "tool":      "arifos_vps_tick",
        "canonical": "arifos_vps_tick[DAEMON_LOOP]",
        "tick_id":   tick_id,
        "epoch":     epoch,
        "phase":     1,
        "stages":    {},
    }

    # ── Stage 1: Daemon self-check ──────────────────────────────────────────
    health = arifos_health_check()
    result["stages"]["daemon_health"] = health

    # ── Stage 2: Machine sense ────────────────────────────────────────────────
    sense = arifos_sense_state()
    result["stages"]["sense_state"] = sense

    # ── Stage 3: Organ health pings ─────────────────────────────────────────
    organ_ping = arifos_ping_all_organs()
    result["stages"]["organ_ping"] = organ_ping

    # Update daemon metrics
    DAEMON_METRICS["ticks"]     += 1
    DAEMON_METRICS["last_tick"] = epoch
    DAEMON_METRICS["organs_up"]   = organ_ping["summary"]["up"]
    DAEMON_METRICS["organs_down"] = organ_ping["summary"]["down"]

    # ── Stage 4: Observability log ──────────────────────────────────────────
    obs_entry = {
        "tick_id":  tick_id,
        "organs":   organ_ping["organs"],
        "summary":  organ_ping["summary"],
        "sense": {
            "disk":    sense.get("disk", []),
            "memory":  sense.get("memory_mb", {}),
            "load":    sense.get("load_avg", []),
            "containers": sense.get("container_count", 0),
        },
    }
    obs_result = arifos_observability_append(obs_entry)
    result["stages"]["observability_log"] = obs_result

    # ── Stage 5: Vault seal ───────────────────────────────────────────────────
    # Check for anomalies: any DOWN organs?
    organ_summary = organ_ping["summary"]
    if organ_summary["down"] > 0:
        vault_notes = f"ANOMALY: {organ_summary['down']} organ(s) DOWN: " +                       ", ".join([n for n, r in organ_ping["organs"].items()
                                 if r.get("status") == "DOWN"])
        DAEMON_METRICS["holds"] += 1
        DAEMON_METRICS["last_hold"] = epoch
    else:
        vault_notes = f"All organs UP. Ticks: {DAEMON_METRICS['ticks']}"

    vault_seal = arifos_vault_append(
        entry_type="tick",
        actor="arifOS-vps-daemon",
        tool_name="arifos_vps_tick",
        result_status="OK" if organ_summary["down"] == 0 else "ANOMALY",
        risk_class="SAFE",
        notes=vault_notes,
        extra={
            "tick_id":      tick_id,
            "phase":        1,
            "organ_summary": organ_summary,
            "disk_pct_max": max(
                (int(d.get("pct", 0)) for d in sense.get("disk", [])),
                default=0
            ),
            "memory_used_pct": round(
                sense.get("memory_mb", {}).get("used", 0) /
                max(sense.get("memory_mb", {}).get("total", 1), 1) * 100, 1
            ) if sense.get("memory_mb", {}).get("total", 0) > 0 else 0,
            "container_count": sense.get("container_count", 0),
            "vault_events":  sense.get("vault", {}).get("events", 0),
        },
    )
    result["stages"]["vault_seal"] = vault_seal
    DAEMON_METRICS["seals"] += 1

    # Persist metrics
    _save_daemon_metrics()

    result["verdict"] = "SEAL" if organ_summary["down"] == 0 else "HOLD"
    result["status"]  = "tick_complete"
    return result


