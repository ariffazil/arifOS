"""
DRAFT_CONTROL_DOCTRINE carry-forward + contradiction minimal.
Every serious action emits carry_forward.json + memory entry + receipt.
L5 memory clarity.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

CARRY_PATH = os.getenv("ARIFOS_CARRY_FORWARD", "/root/.local/share/arifos/carry_forward.json")
CLARITY_LEDGER_PATH = os.getenv(
    "ARIFOS_CLARITY_LEDGER",
    "/root/.local/share/arifos/carry_forward.clarity_ledger.jsonl",
)
CONTRA_LEDGER = os.getenv(
    "ARIFOS_CONTRADICTION_LEDGER", "/root/arifOS/arifosmcp/runtime/contradiction_ledger.jsonl"
)


def _emit_sidecar(entry: dict[str, Any]) -> str:
    """Append a clarity receipt to the sidecar JSONL ledger WITHOUT touching
    the v2 generational carry_forward dict. Returns path written.

    2026-09-12 GUARD (canary event SEAL-38cbac302a574600): the legacy
    'not a list → corrupted → recover' branch destroyed the v2 dict twice
    in one day (26.6KB generational state → 310B array). A dict on the
    canonical path is the arifos.carry_forward.v2 state written by
    carry_forward.py — it is NEVER corruption. Divert, never destroy.
    """
    os.makedirs(os.path.dirname(CLARITY_LEDGER_PATH), exist_ok=True)
    with open(CLARITY_LEDGER_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return CLARITY_LEDGER_PATH


def emit_carry_forward(
    action: str, session_id: str, actor_id: str, evidence_layer: str, receipt: dict[str, Any]
) -> str:
    """Stage 555/999: ensure memory survives. Returns path written.

    S2 HARDENING (2026-08-08): atomic write via tmp+rename prevents
    corruption from crashes during write. STAMPED backup written to
    sidecar directory on each successful write.
    """
    entry = {
        "ts": time.time(),
        "action": action,
        "session_id": session_id,
        "actor_id": actor_id,
        "evidence_layer": evidence_layer,
        "receipt": receipt,
        "doctrine": "CLARITY-CARRY-FORWARD",
    }
    try:
        os.makedirs(os.path.dirname(CARRY_PATH), exist_ok=True)
        data: list[dict[str, Any]] = []
        if os.path.exists(CARRY_PATH):
            with open(CARRY_PATH) as f:
                loaded = json.load(f)
            if not isinstance(loaded, list):
                # 2026-09-12 GUARD (canary SEAL-38cbac302a574600): a dict here
                # is the v2 generational state (arifos.carry_forward.v2) —
                # NOT corruption. The legacy "recover" branch destroyed it on
                # every arif_seal (26.6KB → 310B, twice on 2026-09-12).
                # Divert this entry to the sidecar ledger; never destroy.
                return _emit_sidecar(entry)
            data = loaded
        data.append(entry)
        trimmed = data[-50:]  # keep last 50

        # ── Atomic write: tmp file → os.replace() ──────────────────────
        tmp_path = CARRY_PATH + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(trimmed, f, indent=2)
            f.flush()
        os.replace(tmp_path, CARRY_PATH)  # atomic on same filesystem

        # ── STAMPED backup ─────────────────────────────────────────────
        backup_dir = os.path.join(os.path.dirname(CARRY_PATH), "carry_forward_backups")
        os.makedirs(backup_dir, exist_ok=True)
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(entry["ts"]))
        backup_path = os.path.join(backup_dir, f"carry_forward-{stamp}-{session_id[:8]}.json")
        with open(backup_path, "w") as bf:
            json.dump(trimmed, bf, indent=2)

        return CARRY_PATH
    except Exception:
        return "carry_forward_failed"


def open_contradiction(
    claim_a: str, claim_b: str, source_a: str, source_b: str, severity: str = "HIGH"
) -> str:
    """Stage 333: log to ledger. Returns entry id."""
    entry = {
        "id": f"contra-{int(time.time())}",
        "claim_a": claim_a,
        "claim_b": claim_b,
        "source_a": source_a,
        "source_b": source_b,
        "severity": severity,
        "resolution_status": "OPEN",
        "ts": time.time(),
    }
    try:
        os.makedirs(os.path.dirname(CONTRA_LEDGER), exist_ok=True)
        with open(CONTRA_LEDGER, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return entry["id"]
    except Exception:
        return "contra_write_failed"


# Hook example: call from law on CLARITY or from seal success.
