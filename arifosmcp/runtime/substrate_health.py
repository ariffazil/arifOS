"""
Substrate Health — Degraded-Dominance Gate
═══════════════════════════════════════════════════════════════════════════════

The substrate must never produce SEAL when degraded. This module provides the
fast, in-process check that gates judge_deliberate and vault_seal.

Per ChatGPT insight: "Warnings must dominate praise. Proof must dominate poetry.
Failure must dominate ceremony."

Per arifOS CapabilitySurface.StatusAlignment:
  - ALIGNED: outer verdict matches inner truth + live probe
  - OVERCLAIM: says SEAL/OK but inner is HOLD/FAIL or probe fails
  - UNDERCLAIM: says HOLD/DEGRADED but actually works
  - DARK: unreachable — transport/auth broken, no probe possible

If any critical subsystem is degraded → verdict MUST be HOLD, never SEAL.

DITEMPA BUKAN DIBERI — The substrate is forged, not given.
"""

from __future__ import annotations

import os


# Critical subsystems that block SEAL when degraded
# If any of these is False/MISSING/EMPTY, we suppress positive verdicts.
CRITICAL_SUBSYSTEMS = (
    "vault_chain",  # VAULT999 has seals we can read
    "constitution_hash",  # The constitution identity is resolvable
    "federation_health",  # Federation organs are reachable (best-effort)
)


def substrate_health_check() -> dict[str, str]:
    """
    Fast in-process substrate health check.

    Returns a dict mapping each critical subsystem name to a status:
      - "OK": present and well-formed
      - "MISSING": path doesn't exist
      - "EMPTY": path exists but no content
      - "DEGRADED": present but partial/corrupt
      - "UNKNOWN": cannot determine

    This is intentionally cheap — no network calls, no DB queries.
    """
    health: dict[str, str] = {}

    # ── vault_chain ────────────────────────────────────────────────────
    vault_dir = (
        os.environ.get("VAULT999_PATH") or os.environ.get("ARIFOS_VAULT_DIR") or "/agent/vault999"
    )
    if not os.path.exists(vault_dir):
        health["vault_chain"] = "MISSING"
    elif os.path.isdir(vault_dir):
        jsonl_files = [
            f
            for f in os.listdir(vault_dir)
            if f.endswith(".jsonl") and os.path.isfile(os.path.join(vault_dir, f))
        ]
        non_empty = [f for f in jsonl_files if os.path.getsize(os.path.join(vault_dir, f)) > 0]
        if not jsonl_files:
            health["vault_chain"] = "EMPTY"
        elif not non_empty:
            health["vault_chain"] = "EMPTY"
        else:
            health["vault_chain"] = "OK"
    else:
        # vault_path is a file
        if os.path.getsize(vault_dir) > 0:
            health["vault_chain"] = "OK"
        else:
            health["vault_chain"] = "EMPTY"

    # ── constitution_hash ─────────────────────────────────────────────
    # Try to find the constitution identity file
    constitution_paths = [
        os.environ.get("ARIFOS_CONSTITUTION_PATH"),
        "/opt/arifos/app/static/constitution.json",
        "/root/arifOS/static/constitution.json",
    ]
    constitution_found = False
    for path in constitution_paths:
        if path and os.path.exists(path) and os.path.getsize(path) > 0:
            constitution_found = True
            break
    health["constitution_hash"] = "OK" if constitution_found else "MISSING"

    # ── federation_health ─────────────────────────────────────────────
    # Best-effort: check if any organ endpoint responds on localhost.
    # Cheap timeout (50ms). If unsure, report UNKNOWN (not degraded).
    health["federation_health"] = _probe_federation_health()

    return health


def _probe_federation_health() -> str:
    """Probe a couple of organ ports cheaply. Returns OK/DEGRADED/UNKNOWN."""
    import socket

    organ_ports = [
        (8088, "arifOS"),  # constitutional kernel
        (18082, "WEALTH"),  # capital
        (18083, "WELL"),  # vitality
    ]
    reachable = 0
    for port, _name in organ_ports:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.05):
                reachable += 1
        except (OSError, socket.timeout):
            pass
    if reachable == len(organ_ports):
        return "OK"
    if reachable >= 1:
        return "DEGRADED"
    return "UNKNOWN"


def degraded_dominance_gate() -> tuple[bool, str, dict[str, str]]:
    """
    The single gate. If degraded, no positive verdict (SEAL/SABAR) is allowed.

    Returns:
        (degraded, reason, health)
        - degraded: True if ANY critical subsystem is not OK
        - reason: human-readable explanation
        - health: full subsystem health dict

    Usage:
        degraded, reason, health = degraded_dominance_gate()
        if degraded:
            return {"verdict": "HOLD", "reason": reason, "health": health}
    """
    health = substrate_health_check()
    degraded_subsystems = [name for name in CRITICAL_SUBSYSTEMS if health.get(name) != "OK"]
    degraded = len(degraded_subsystems) > 0
    if degraded:
        reason = "degraded-dominance gate fired: critical subsystems not OK — " + ", ".join(
            f"{s}={health.get(s)}" for s in degraded_subsystems
        )
    else:
        reason = "substrate aligned — all critical subsystems OK"
    return degraded, reason, health


# ── Test surface ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 80)
    print("Substrate Health Check — degraded-dominance gate")
    print("=" * 80)

    health = substrate_health_check()
    print("\nSubsystem health:")
    for name, status in health.items():
        marker = "✓" if status == "OK" else "✗"
        print(f"  {marker} {name}: {status}")

    degraded, reason, _ = degraded_dominance_gate()
    print(f"\nDegraded: {degraded}")
    print(f"Reason: {reason}")

    if degraded:
        print("\n→ Verdict MUST be HOLD, never SEAL.")
    else:
        print("\n→ Verdict MAY be SEAL.")
