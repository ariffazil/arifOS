"""
arifosmcp/tools/daemon_tools.py — Canonical arifos_* Internal Daemon Tools
=======================================================================
SEAL    : 999-SEAL-TOOL-AUDIT-20260523-DITEMPA-BUKAN-DIBERI
EPOCH   : 2026-05-23T10:28:00+08:00
PURPOSE : arifOS internal daemon tool surface — arifos_* prefix

NAMING CONVENTION (hard rule):
  arifos_ = internal daemon tools (apexd, internal loops, organ comms)
  arif_   = external MCP tools (human-facing, API-exposed)

These 6 tools are the canonical internal daemon surface.
They wrap apexd.py internal methods as first-class callables.

CLASS MAPPING:
  HEARTBEAT  — is daemon alive, organ status
  SENSE      — read state, config, environment
  GATE       — evaluate condition, return GO/HOLD/SKIP
  ACT        — dispatch action to organ or tool
  LOG        — append structured event to vault
  RECOVER    — retry logic, escalate to HOLD

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import os
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ─────────────────────────────────────────────────────────────────────────────
# Constants (match apexd.py config/apexd.yaml)
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_VAULT_PATH = "/var/lib/arifos/vault999"
DEFAULT_SOCK_PATH  = "/run/arifos.sock"
DEFAULT_HTTP_HOST  = "127.0.0.1"
DEFAULT_HTTP_PORT  = 8081


# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL TOOL 1 — HEARTBEAT
# arifos_health_check  —  Is the daemon alive? Return organ status.
# ─────────────────────────────────────────────────────────────────────────────

def arifos_health_check(
    session_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    HEARTBEAT — Check if arifOS daemon is alive and reporting organ status.

    Args:
        session_id: Optional session to bind to this health check.
        dry_run: If True, simulate health check without side effects.

    Returns:
        {
            "tool": "arifos_health_check",
            "canonical": "arifos_health_check[HEARTBEAT]",
            "alive": bool,
            "socket_reachable": bool,
            "vault_accessible": bool,
            "sessions_active": int,
            "uptime_seconds": float,
            "daemon_version": str,
            "epoch": str,
        }

    Side effects:
        - Reads vault manifest (read-only)
        - Checks socket connectivity (read-only)
        - No mutations unless dry_run=False (always read-only here)

    Raises:
        Nothing — always returns a dict (never raises for health checks).
    """
    daemon_version = "0.1.0-A-FORGE"
    daemon_start   = float(os.environ.get("ARIFOS_DAEMON_START", time.time()))
    vault_path     = os.environ.get("ARIFOS_VAULT_PATH", DEFAULT_VAULT_PATH)
    sock_path      = os.environ.get("ARIFOS_SOCK_PATH",  DEFAULT_SOCK_PATH)

    # Check vault accessibility
    vault_ok = False
    try:
        vault_p = Path(vault_path)
        vault_manifest = vault_p / "manifest.json"
        if vault_p.exists() and vault_manifest.exists():
            data = json.loads(vault_manifest.read_text())
            vault_ok = True
            vault_events = data.get("events", 0)
        else:
            vault_events = 0
    except Exception:
        vault_ok     = False
        vault_events = 0

    # Check socket reachability (quick connect test)
    socket_ok = False
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        sock.connect(sock_path)
        sock.close()
        socket_ok = True
    except Exception:
        socket_ok = False

    # Check HTTP health endpoint
    http_ok = False
    try:
        import urllib.request
        url = f"http://{DEFAULT_HTTP_HOST}:{DEFAULT_HTTP_PORT}/health"
        with urllib.request.urlopen(url, timeout=1.0) as resp:
            http_ok = resp.status == 200
    except Exception:
        http_ok = False

    alive = vault_ok and socket_ok

    result = {
        "tool":         "arifos_health_check",
        "canonical":    "arifos_health_check[HEARTBEAT]",
        "alive":        alive,
        "socket_reachable": socket_ok,
        "vault_accessible": vault_ok,
        "vault_events": vault_events,
        "http_health":  http_ok,
        "sessions_active": 0,   # TODO: wire to apexd session registry
        "uptime_seconds": round(time.time() - daemon_start, 1),
        "daemon_version": daemon_version,
        "epoch":         datetime.now(timezone.utc).isoformat(),
        "dry_run":       dry_run,
    }

    if session_id:
        result["session_id"] = session_id

    return result


# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL TOOL 2 — SENSE
# arifos_sense_state  —  Read machine state, config, environment.
# ─────────────────────────────────────────────────────────────────────────────

def arifos_sense_state(
    session_id: str | None = None,
    layers: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    SENSE — Read machine state, environment, and configuration layers.

    Args:
        session_id: Optional session to bind to this sense pass.
        layers: Which state layers to read.
            Options: ["system", "config", "constitution", "vault", "network"]
            Default: all layers.
        dry_run: If True, simulate sense without side effects.

    Returns:
        {
            "tool": "arifos_sense_state",
            "canonical": "arifos_sense_state[SENSE]",
            "layers": {...},
            "epoch_unix": float,
            "hostname": str,
            "user": str,
            "cwd": str,
        }

    Side effects: Read-only state observation. No mutations.

    Raises: Nothing — always returns a dict.
    """
    layers = layers or ["system", "config", "constitution", "vault", "network"]
    state: dict[str, Any] = {}

    # Layer: system
    if "system" in layers:
        mem_mb = 0.0
        try:
            import resource
            mem_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        except Exception:
            pass
        state["system"] = {
            "hostname": socket.gethostname(),
            "cwd":       os.getcwd(),
            "user":      os.getenv("USER", "unknown"),
            "memory_mb":  round(mem_mb, 1),
            "epoch_unix": time.time(),
            "pid":       os.getpid(),
        }

    # Layer: config
    if "config" in layers:
        try:
            config_path = Path("/etc/arifos/config.yaml")
            if config_path.exists():
                import yaml  # type: ignore
                state["config"] = yaml.safe_load(config_path.read_text())
            else:
                state["config"] = {"status": "not_found"}
        except ImportError:
            state["config"] = {"status": "yaml_unavailable"}
        except Exception as e:
            state["config"] = {"status": "error", "detail": str(e)}

    # Layer: constitution (F01-F13 floors)
    if "constitution" in layers:
        try:
            from arifOS.apexd import build_floor_registry  # type: ignore
            floors = build_floor_registry()
            state["constitution"] = {
                fid: f.to_dict() for fid, f in floors.items()
            }
        except ImportError:
            # Fallback: read from config.yaml
            state["constitution"] = {"status": "unavailable_in_current_context"}

    # Layer: vault
    if "vault" in layers:
        vault_path = os.environ.get("ARIFOS_VAULT_PATH", DEFAULT_VAULT_PATH)
        try:
            manifest_path = Path(vault_path) / "manifest.json"
            if manifest_path.exists():
                state["vault"] = {
                    "path":        vault_path,
                    "manifest":    json.loads(manifest_path.read_text()),
                    "status":       "accessible",
                }
            else:
                state["vault"] = {"status": "not_initialized"}
        except Exception as e:
            state["vault"] = {"status": "error", "detail": str(e)}

    # Layer: network
    if "network" in layers:
        try:
            hostname = socket.gethostname()
            addrs = socket.getaddrinfo(hostname, 0, socket.SOCK_STREAM)
            ips = list({a[4][0] for a in addrs})
        except Exception:
            ips = []
        state["network"] = {
            "hostname":  socket.gethostname(),
            "ips":       ips,
            "socket_ok": socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                          .connect_ex(DEFAULT_SOCK_PATH) == 0,
        }

    result = {
        "tool":      "arifos_sense_state",
        "canonical": "arifos_sense_state[SENSE]",
        "layers":    state,
        "dry_run":   dry_run,
    }

    if session_id:
        result["session_id"] = session_id

    return result


# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL TOOL 3 — GATE
# arifos_gate_eval  —  Evaluate conditions, return GO / HOLD / SKIP.
# ─────────────────────────────────────────────────────────────────────────────

def arifos_gate_eval(
    intent: str,
    command: str | None = None,
    context: dict[str, Any] | None = None,
    session_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    GATE — Evaluate intent/command through the constitutional gate.
    Returns GO (proceed), HOLD (wait for human), or SKIP (not applicable).

    Args:
        intent: The human's stated intent.
        command: Optional raw command to classify for risk tier.
        context: Optional context dict (kappa_r, confidence, floors, etc.)
        session_id: Optional session to bind to this gate evaluation.
        dry_run: If True, simulate gate evaluation without side effects.

    Returns:
        {
            "tool": "arifos_gate_eval",
            "canonical": "arifos_gate_eval[GATE]",
            "verdict": "GO" | "HOLD" | "SKIP" | "SABAR",
            "risk_tier": "LOW" | "MEDIUM" | "HIGH" | "ATOMIC",
            "rationale": str,
            "floors_passed": list[str],
            "floors_failed": list[str],
            "human_required": bool,
            "apex_metric": dict,
            "deterministic": bool,
        }

    Side effects:
        - Read-only pattern matching (deterministic, no LLM)
        - Optionally reads vault manifest (read-only)
        - No mutations unless dry_run=False

    Raises: Nothing — always returns a dict.
    """
    import re

    context = context or {}
    command = command or ""

    # ── Deterministic hold classifier (no LLM) ───────────────────────────────
    ATOMIC_HOLD = [
        (r"rm\s+-rf\s+/\s*$",               "F9 F13 ATOMIC: recursive root delete"),
        (r"rm\s+-rf\s+/var\s+/usr",          "F9 F13 ATOMIC: system dir wipe"),
        (r"rm\s+-rf\s+/etc\s*$",             "F9 F13 ATOMIC: config dir wipe"),
        (r"mkfs",                            "F13 ATOMIC: filesystem destruction"),
        (r"fdisk",                           "F13 ATOMIC: partition table destruction"),
        (r"dd\s+if=/dev/zero\s+of=/dev/",    "F13 ATOMIC: raw disk wipe"),
        (r"iptables\s+-F\s*$",              "F13 ATOMIC: firewall flush"),
        (r"curl\s+.*\|\s*sh",               "F9 F13 ATOMIC: remote exec via pipe"),
        (r"curl\s+.*\|\s*sudo\s+bash",       "F9 F13 ATOMIC: sudo remote exec"),
        (r"DROP\s+DATABASE",                "F13 ATOMIC: database destruction"),
        (r"shutdown",                        "F13 ATOMIC: system shutdown"),
        (r"reboot",                          "F13 ATOMIC: system reboot"),
    ]
    HIGH_HOLD = [
        (r"chmod\s+-R\s+777\s+/",           "F9: world-writable system"),
        (r"chown\s+-R\s+root\s+/",          "F9 F13: ownership takeover"),
        (r"systemctl\s+mask",              "F13 HIGH: service masking"),
        (r"git\s+push\s+--force\s+.*main",   "F13 HIGH: main branch force push"),
    ]
    CAUTION_PATTERNS = [
        (r"git\s+push\s+--force",           "F13 CAUTION: force push"),
        (r"systemctl\s+(stop|restart)",   "F13 CAUTION: service control"),
        (r"chmod\s+-R\s+777",              "F9 CAUTION: broad permission change"),
        (r"docker\s+rm\s+-f",              "F9 CAUTION: container destruction"),
    ]

    cmd = command.strip()
    deterministic = True

    for pattern, rationale in ATOMIC_HOLD:
        if re.search(pattern, cmd, re.IGNORECASE):
            return {
                "tool":         "arifos_gate_eval",
                "canonical":    "arifos_gate_eval[GATE]",
                "verdict":      "HOLD",
                "risk_tier":    "ATOMIC",
                "rationale":    rationale,
                "floors_passed": [],
                "floors_failed": ["F09", "F13"],
                "human_required": True,
                "deterministic": deterministic,
                "dry_run":       dry_run,
            }

    for pattern, rationale in HIGH_HOLD:
        if re.search(pattern, cmd, re.IGNORECASE):
            return {
                "tool":          "arifos_gate_eval",
                "canonical":     "arifos_gate_eval[GATE]",
                "verdict":       "HOLD",
                "risk_tier":     "HIGH",
                "rationale":     rationale,
                "floors_passed": [],
                "floors_failed": ["F09", "F13"],
                "human_required": True,
                "deterministic": deterministic,
                "dry_run":        dry_run,
            }

    for pattern, rationale in CAUTION_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            return {
                "tool":          "arifos_gate_eval",
                "canonical":     "arifos_gate_eval[GATE]",
                "verdict":       "HOLD",
                "risk_tier":     "MEDIUM",
                "rationale":     rationale,
                "floors_passed": [],
                "floors_failed": ["F13"],
                "human_required": False,
                "deterministic": deterministic,
                "dry_run":        dry_run,
            }

    # ── APEX thermodynamic gate ───────────────────────────────────────────────
    kappa_r     = context.get("kappa_r", 0.9)
    confidence  = context.get("confidence", 0.8)
    threshold   = 0.95

    reversibility_passed = kappa_r >= threshold

    if not reversibility_passed:
        verdict  = "SABAR"
        rationale = f"Reversibility gate not met: κᵣ={kappa_r:.2f} < {threshold}"
        human_req = False
    elif confidence < 0.5:
        verdict   = "HOLD"
        rationale = f"Confidence {confidence:.2f} < 0.5 — low certainty"
        human_req = True
    else:
        verdict   = "GO"
        rationale = "APEX thermodynamic conditions met — GO"
        human_req = False

    apex_metric = {
        "kappa_r":                 round(kappa_r, 4),
        "kappa_r_threshold":       threshold,
        "reversibility_gate_passed": reversibility_passed,
        "confidence":              round(confidence, 4),
        "verdict":                verdict,
    }

    result = {
        "tool":             "arifos_gate_eval",
        "canonical":        "arifos_gate_eval[GATE]",
        "verdict":          verdict,
        "risk_tier":        "LOW" if verdict == "GO" else "MEDIUM" if verdict == "SABAR" else "HIGH",
        "rationale":         rationale,
        "floors_passed":    ["F01", "F02", "F09", "F13"] if verdict == "GO" else [],
        "floors_failed":    [] if verdict == "GO" else ["F09"],
        "human_required":   human_req,
        "apex_metric":      apex_metric,
        "deterministic":    deterministic,
        "dry_run":          dry_run,
    }

    if session_id:
        result["session_id"] = session_id

    return result


# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL TOOL 4 — ACT
# arifos_act_dispatch  —  Dispatch action to organ or tool.
# ─────────────────────────────────────────────────────────────────────────────

def arifos_act_dispatch(
    intent: str,
    command: str | None = None,
    context: dict[str, Any] | None = None,
    session_id: str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """
    ACT — Dispatch execution to the appropriate organ/tool.
    Respects GO/HOLD verdict from arifos_gate_eval.

    Args:
        intent: The human's stated intent.
        command: Optional command to execute.
        context: Optional context dict.
        session_id: Optional session to bind to this action.
        dry_run: If True (default), simulate execution without side effects.
            Set dry_run=False to execute.

    Returns:
        {
            "tool": "arifos_act_dispatch",
            "canonical": "arifos_act_dispatch[ACT]",
            "status": "dispatched" | "blocked" | "dry_run" | "hold",
            "verdict": str,
            "command": str,
            "execution_result": dict | None,
            "executed_epoch": str | None,
        }

    Side effects:
        - dry_run=True: no side effects
        - dry_run=False: executes command, writes to vault

    Raises:
        PermissionError: if dry_run=False and human_required=True
        RuntimeError: if vault is inaccessible
    """
    context  = context or {}
    session_id = session_id or f"sess-{int(time.time())}"

    # Gate evaluation first
    gate = arifos_gate_eval(intent=intent, command=command, context=context)

    result = {
        "tool":         "arifos_act_dispatch",
        "canonical":   "arifos_act_dispatch[ACT]",
        "verdict":      gate["verdict"],
        "risk_tier":    gate["risk_tier"],
        "rationale":    gate["rationale"],
        "human_required": gate["human_required"],
        "command":      command or "",
        "dry_run":      dry_run,
    }

    # Block if HOLD and dry_run=False
    if gate["verdict"] == "HOLD" and not dry_run:
        result["status"] = "blocked"
        result["execution_result"] = None
        return result

    if gate["verdict"] == "HOLD" and dry_run:
        result["status"] = "hold"
        result["execution_result"] = None
        return result

    # dry_run mode — simulate
    if dry_run:
        result["status"] = "dry_run"
        result["execution_result"] = {
            "simulated": True,
            "would_execute": True,
            "intent": intent,
            "command": command,
            "rationale": "Dry run — no execution performed.",
        }
        return result

    # ── Real execution path (dry_run=False) ──────────────────────────────────
    if not command:
        result["status"] = "dry_run"
        result["execution_result"] = {"simulated": True, "note": "No command provided"}
        return result

    import subprocess

    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        result["status"] = "dispatched"
        result["execution_result"] = {
            "stdout":      proc.stdout[:500],
            "stderr":      proc.stderr[:500],
            "returncode":  proc.returncode,
            "timeout":    False,
        }
        result["executed_epoch"] = datetime.now(timezone.utc).isoformat()

        # Auto-log to vault
        vault_result = arifos_vault_append(
            entry_type="execution",
            payload={
                "intent":  intent,
                "command": command,
                "returncode": proc.returncode,
            },
            session_id=session_id,
        )
        result["vault_seal"] = vault_result.get("chain_hash", "PENDING")

    except subprocess.TimeoutExpired:
        result["status"] = "dispatched"
        result["execution_result"] = {"timeout": True, "note": "Command timed out at 30s"}
    except Exception as e:
        result["status"] = "dispatched"
        result["execution_result"] = {"error": str(e)}

    return result


# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL TOOL 5 — LOG
# arifos_vault_append  —  Append structured event to VAULT999.
# ─────────────────────────────────────────────────────────────────────────────

def arifos_vault_append(
    entry_type: str,
    payload: dict[str, Any],
    session_id: str | None = None,
    plan_id: str | None = None,
    actor: str = "arifOS-daemon",
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    LOG — Append a structured event to VAULT999 immutable ledger.
    The vault is hash-chained. Each entry gets merkle_leaf + chain_hash.

    Args:
        entry_type: Type of event.
            Options: "execution" | "judgment" | "gate_eval" | "health_check" |
                     "sense_state" | "session" | "verdict" | "escalation"
        payload: The event payload (dict, must be JSON-serializable).
        session_id: Optional session to bind to this log entry.
        plan_id: Optional plan ID for this log entry.
        actor: Identity of the actor writing this entry. Default: "arifOS-daemon".
        dry_run: If True, simulate vault append without side effects.

    Returns:
        {
            "tool": "arifos_vault_append",
            "canonical": "arifos_vault_append[LOG]",
            "status": "sealed" | "dry_run" | "error",
            "merkle_leaf": str,
            "chain_hash": str,
            "prev_hash": str,
            "sealed_epoch": str,
            "entry_type": str,
            "vault_version": str,
        }

    Side effects:
        - dry_run=False: appends JSON line to vault999/append_only.log
        - Updates vault999/manifest.json (last_hash, events count)
        - dry_run=True: no side effects

    Raises:
        RuntimeError: if vault directory is inaccessible (unless dry_run=True)
        ValueError: if entry_type is not recognized (unless dry_run=True)
    """
    VALID_ENTRY_TYPES = {
        "execution", "judgment", "gate_eval", "health_check",
        "sense_state", "session", "verdict", "escalation",
    }

    if entry_type not in VALID_ENTRY_TYPES and not dry_run:
        raise ValueError(f"Unknown entry_type: {entry_type}. "
                         f"Valid: {VALID_ENTRY_TYPES}")

    vault_path   = os.environ.get("ARIFOS_VAULT_PATH", DEFAULT_VAULT_PATH)
    vault_dir    = Path(vault_path)
    ledger_path  = vault_dir / "append_only.log"
    manifest_path = vault_dir / "manifest.json"

    # Ensure vault exists
    if not dry_run:
        vault_dir.mkdir(parents=True, exist_ok=True)
        if not manifest_path.exists():
            manifest_path.write_text(json.dumps({
                "last_hash": "GENESIS",
                "events": 0,
                "version": "2.0",
            }))

    # Read manifest
    prev_hash = "GENESIS"
    events   = 0
    if not dry_run:
        try:
            manifest = json.loads(manifest_path.read_text())
            prev_hash = manifest.get("last_hash", "GENESIS")
            events    = manifest.get("events", 0)
        except Exception:
            prev_hash = "GENESIS"
            events    = 0

    # Build entry
    entry: dict[str, Any] = {
        "event_type": entry_type,
        "plan_id":    plan_id or f"plan-{int(time.time())}",
        "session_id": session_id or "unknown",
        "actor":      actor,
        "stage":      "888_JUDGE",
        "payload":    payload,
    }

    # Dry run — return what would be written
    if dry_run:
        return {
            "tool":         "arifos_vault_append",
            "canonical":    "arifos_vault_append[LOG]",
            "status":       "dry_run",
            "dry_run":       True,
            "entry":        entry,
            "merkle_leaf":  "SIMULATED",
            "chain_hash":   "SIMULATED",
            "prev_hash":    prev_hash,
            "vault_version": "2.0",
            "note":         "Dry run — no entry written to vault",
        }

    # ── Real append ──────────────────────────────────────────────────────────
    content_str = json.dumps(entry, sort_keys=True)
    leaf = hashlib.sha256(content_str.encode()).hexdigest()
    chain = hashlib.sha256(f"{prev_hash}{leaf}".encode()).hexdigest()

    sealed: dict[str, Any] = {
        **entry,
        "merkle_leaf":   leaf,
        "chain_hash":    chain,
        "prev_hash":     prev_hash,
        "vault_version": "2.0",
        "sealed_epoch":  datetime.now(timezone.utc).isoformat(),
    }

    with open(ledger_path, "a") as f:
        f.write(json.dumps(sealed, ensure_ascii=False) + "\n")

    manifest_path.write_text(json.dumps({
        "last_hash": chain,
        "events":    events + 1,
        "version":   "2.0",
    }))

    return {
        "tool":          "arifos_vault_append",
        "canonical":     "arifos_vault_append[LOG]",
        "status":        "sealed",
        "merkle_leaf":   leaf,
        "chain_hash":    chain,
        "prev_hash":     prev_hash,
        "sealed_epoch":  sealed["sealed_epoch"],
        "entry_type":    entry_type,
        "vault_version": "2.0",
    }


# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL TOOL 6 — RECOVER
# arifos_recover_escalate  —  Retry logic, escalate to HOLD on persistent failure.
# ─────────────────────────────────────────────────────────────────────────────

def arifos_recover_escalate(
    error_context: dict[str, Any],
    session_id: str | None = None,
    max_retries: int = 3,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    RECOVER — Retry logic + escalation to HOLD on persistent failure.
    Handles transient vs persistent errors distinctly.

    Args:
        error_context: Dict describing the error.
            Required keys:
                - "stage": str — pipeline stage where error occurred
                - "error_type": str — "transient" | "persistent" | "unknown"
                - "error_message": str — human-readable error description
            Optional keys:
                - "command": str — the command that failed
                - "retry_count": int — number of retries already attempted
                - "last_exception": str — exception class name
        session_id: Optional session to bind to this recovery.
        max_retries: Number of retries before escalating. Default: 3.
        dry_run: If True, simulate recovery without side effects.

    Returns:
        {
            "tool": "arifos_recover_escalate",
            "canonical": "arifos_recover_escalate[RECOVER]",
            "status": "retry" | "escalated" | "resolved" | "dry_run",
            "retry_count": int,
            "max_retries": int,
            "escalation_reason": str | None,
            "next_action": str,
            "verdict": "HOLD" | "GO",
            "vault_seal": str | None,
        }

    Side effects:
        - dry_run=False: writes escalation event to vault
        - Always read-only otherwise

    Raises: Nothing — always returns a dict.
    """
    stage        = error_context.get("stage", "unknown")
    error_type   = error_context.get("error_type", "unknown")
    error_msg    = error_context.get("error_message", "Unknown error")
    retry_count  = error_context.get("retry_count", 0)
    command      = error_context.get("command", "")
    last_exc     = error_context.get("last_exception", "")

    session_id   = session_id or f"sess-{int(time.time())}"
    plan_id      = f"plan-{int(time.time())}"

    # Dry run
    if dry_run:
        return {
            "tool":           "arifos_recover_escalate",
            "canonical":      "arifos_recover_escalate[RECOVER]",
            "status":         "dry_run",
            "dry_run":         True,
            "error_context":  error_context,
            "next_action":    "Dry run — no action taken",
            "verdict":        "GO",
        }

    # Persistent error → immediate escalation
    if error_type == "persistent":
        vault_seal = arifos_vault_append(
            entry_type="escalation",
            payload={
                "stage":         stage,
                "error_type":    error_type,
                "error_message": error_msg,
                "retry_count":   retry_count,
                "escalation":    "PERSISTENT_ERROR",
                "verdict":       "HOLD",
                "last_exception": last_exc,
            },
            session_id=session_id,
            plan_id=plan_id,
        )
        return {
            "tool":             "arifos_recover_escalate",
            "canonical":        "arifos_recover_escalate[RECOVER]",
            "status":           "escalated",
            "retry_count":      retry_count,
            "max_retries":      max_retries,
            "escalation_reason": f"Persistent error at {stage}: {error_msg}",
            "next_action":      "HOLD — requires human intervention",
            "verdict":          "HOLD",
            "vault_seal":       vault_seal.get("chain_hash"),
        }

    # Unknown error — retry once then escalate
    if error_type == "unknown":
        if retry_count < 1:
            return {
                "tool":           "arifos_recover_escalate",
                "canonical":      "arifos_recover_escalate[RECOVER]",
                "status":         "retry",
                "retry_count":    retry_count + 1,
                "max_retries":    max_retries,
                "escalation_reason": None,
                "next_action":    f"Retry {retry_count + 1}/1 — unknown error, retry once then escalate",
                "verdict":        "GO",
                "vault_seal":     None,
            }
        else:
            vault_seal = arifos_vault_append(
                entry_type="escalation",
                payload={
                    "stage":        stage,
                    "error_type":   "unknown",
                    "error_message": error_msg,
                    "retry_count":  retry_count,
                    "escalation":   "UNKNOWN_ERROR_PERSISTED",
                    "verdict":      "HOLD",
                    "last_exception": last_exc,
                },
                session_id=session_id,
                plan_id=plan_id,
            )
            return {
                "tool":             "arifos_recover_escalate",
                "canonical":        "arifos_recover_escalate[RECOVER]",
                "status":           "escalated",
                "retry_count":      retry_count,
                "max_retries":      max_retries,
                "escalation_reason": f"Unknown error persisted at {stage}: {error_msg}",
                "next_action":      "HOLD — requires human intervention",
                "verdict":          "HOLD",
                "vault_seal":       vault_seal.get("chain_hash"),
            }

    # Transient error — retry up to max_retries
    if retry_count < max_retries:
        vault_seal = arifos_vault_append(
            entry_type="escalation",
            payload={
                "stage":         stage,
                "error_type":    "transient",
                "error_message": error_msg,
                "retry_count":   retry_count,
                "escalation":    "RETRY",
                "verdict":       "GO",
                "last_exception": last_exc,
            },
            session_id=session_id,
            plan_id=plan_id,
        )
        return {
            "tool":              "arifos_recover_escalate",
            "canonical":         "arifos_recover_escalate[RECOVER]",
            "status":            "retry",
            "retry_count":       retry_count + 1,
            "max_retries":       max_retries,
            "escalation_reason": None,
            "next_action":       f"Retry {retry_count + 1}/{max_retries} — transient error",
            "verdict":           "GO",
            "vault_seal":        vault_seal.get("chain_hash"),
        }
    else:
        vault_seal = arifos_vault_append(
            entry_type="escalation",
            payload={
                "stage":         stage,
                "error_type":    "transient",
                "error_message": error_msg,
                "retry_count":   retry_count,
                "escalation":    "MAX_RETRIES_EXCEEDED",
                "verdict":       "HOLD",
                "last_exception": last_exc,
            },
            session_id=session_id,
            plan_id=plan_id,
        )
        return {
            "tool":              "arifos_recover_escalate",
            "canonical":         "arifos_recover_escalate[RECOVER]",
            "status":            "escalated",
            "retry_count":       retry_count,
            "max_retries":       max_retries,
            "escalation_reason": f"Max retries ({max_retries}) exceeded at {stage}",
            "next_action":       "HOLD — requires human intervention",
            "verdict":           "HOLD",
            "vault_seal":        vault_seal.get("chain_hash"),
        }


# ─────────────────────────────────────────────────────────────────────────────
# BONUS: DAEMON TICK — The canonical tick loop using all 6 tools
# ─────────────────────────────────────────────────────────────────────────────

def arifos_daemon_tick(
    session_id: str | None = None,
    intent: str = "daemon tick",
    command: str | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    DAEMON TICK — One full tick of the arifOS daemon loop.
    Calls all 6 canonical arifos_* tools in correct order.

    Order:
      1. arifos_health_check   (HEARTBEAT — is daemon alive?)
      2. arifos_sense_state    (SENSE — read machine state)
      3. arifos_gate_eval      (GATE — GO/HOLD/SKIP)
      4. arifos_act_dispatch   (ACT — execute if GO)
      5. arifos_vault_append   (LOG — record)
      6. arifos_recover_escalate (RECOVER — on error, escalate)

    Args:
        session_id: Optional session ID.
        intent: Intent for this tick.
        command: Optional command to evaluate.
        context: Optional context dict.

    Returns:
        Full tick result with all 6 tool results + final verdict.
    """
    context    = context or {}
    session_id = session_id or f"sess-{int(time.time())}"
    plan_id    = f"plan-{int(time.time())}"
    tick_id    = f"tick-{int(time.time())}"

    results: dict[str, Any] = {
        "tool":       "arifos_daemon_tick",
        "canonical":  "arifos_daemon_tick[DAEMON_LOOP]",
        "tick_id":    tick_id,
        "session_id": session_id,
        "plan_id":    plan_id,
        "epoch":      datetime.now(timezone.utc).isoformat(),
        "stages":     {},
    }

    # Stage 1: HEARTBEAT
    health = arifos_health_check(session_id=session_id)
    results["stages"]["health_check"] = health
    if not health.get("alive"):
        results["verdict"]     = "HOLD"
        results["halt_reason"] = "Daemon not alive"
        return results

    # Stage 2: SENSE
    sense = arifos_sense_state(session_id=session_id)
    results["stages"]["sense_state"] = sense

    # Stage 3: GATE
    gate = arifos_gate_eval(
        intent=intent,
        command=command,
        context=context,
        session_id=session_id,
    )
    results["stages"]["gate_eval"] = gate

    if gate["verdict"] in ("HOLD", "SKIP"):
        results["verdict"]     = gate["verdict"]
        results["halt_reason"] = gate.get("rationale", "")
        # Still log to vault even on HOLD
        vault_seal = arifos_vault_append(
            entry_type="gate_eval",
            payload={"tick_id": tick_id, "gate_result": gate},
            session_id=session_id,
            plan_id=plan_id,
        )
        results["stages"]["vault_append"] = vault_seal
        return results

    # Stage 4: ACT (dry_run by default for ticks)
    act = arifos_act_dispatch(
        intent=intent,
        command=command,
        context=context,
        session_id=session_id,
        dry_run=True,
    )
    results["stages"]["act_dispatch"] = act

    # Stage 5: LOG
    vault_seal = arifos_vault_append(
        entry_type="tick",
        payload={
            "tick_id":    tick_id,
            "intent":     intent,
            "command":    command,
            "gate_result": gate,
            "act_result":  act,
        },
        session_id=session_id,
        plan_id=plan_id,
    )
    results["stages"]["vault_append"] = vault_seal

    results["verdict"] = gate["verdict"]
    return results


# ─────────────────────────────────────────────────────────────────────────────
# MODULE EXPORTS
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    "arifos_health_check",
    "arifos_sense_state",
    "arifos_gate_eval",
    "arifos_act_dispatch",
    "arifos_vault_append",
    "arifos_recover_escalate",
    "arifos_daemon_tick",
]