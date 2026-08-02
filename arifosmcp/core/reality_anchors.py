"""
arifosmcp/core/reality_anchors.py — Z5 Reality Anchor Injection
══════════════════════════════════════════════════════════════════

Breaks the strange-loop pattern where kernel tools reference only
internal state. Each anchor forces a tool to touch external reality:

  INIT   → VPS snapshot (load, mem, disk, organ SHAs)
  OBSERVE → hash-verified evidence persisted to disk
  JUDGE  → falsifiable prediction included in reality ledger
  SEAL   → observation hash + VPS delta since init

Design: non-blocking, fail-safe. Anchor failure never blocks governance.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("arifos.reality_anchors")

EVIDENCE_DIR = Path("/root/reality_ledger/evidence")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

# Organ source paths for SHA drift detection
_ORGAN_SRCS: dict[str, str] = {
    "arifos": "/root/arifOS",
    "aforge": "/root/A-FORGE",
    "aaa": "/root/AAA",
    "geox": "/root/GEOX",
    "wealth": "/root/WEALTH",
    "well": "/root/WELL",
}


# ═══════════════════════════════════════════════════════════════════
# ANCHOR 1: INIT — VPS Snapshot
# ═══════════════════════════════════════════════════════════════════

def vps_snapshot() -> dict[str, Any]:
    """Capture live VPS state at init time. Non-blocking, fail-safe."""
    snap: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hostname": "",
        "load_1m": -1.0,
        "mem_used_pct": -1.0,
        "disk_used_pct": -1.0,
        "organ_shas": {},
        "snapshot_hash": "",
    }
    try:
        import socket
        snap["hostname"] = socket.gethostname()
    except Exception:
        pass
    try:
        snap["load_1m"] = round(os.getloadavg()[0], 2)
    except Exception:
        pass
    try:
        with open("/proc/meminfo") as f:
            meminfo = {}
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    meminfo[parts[0].rstrip(":")] = int(parts[1])
            total = meminfo.get("MemTotal", 1)
            avail = meminfo.get("MemAvailable", 0)
            snap["mem_used_pct"] = round((1 - avail / total) * 100, 1)
    except Exception:
        pass
    try:
        st = os.statvfs("/")
        snap["disk_used_pct"] = round((1 - st.f_bavail / st.f_blocks) * 100, 1)
    except Exception:
        pass
    # Organ git SHAs (fast — just HEAD)
    for organ, path in _ORGAN_SRCS.items():
        try:
            head_file = Path(path) / ".git" / "HEAD"
            if head_file.exists():
                content = head_file.read_text().strip()
                if content.startswith("ref:"):
                    ref_path = Path(path) / ".git" / content[5:]
                    if ref_path.exists():
                        snap["organ_shas"][organ] = ref_path.read_text().strip()[:7]
                    else:
                        snap["organ_shas"][organ] = "packed"
                else:
                    snap["organ_shas"][organ] = content[:7]
            else:
                snap["organ_shas"][organ] = "no-git"
        except Exception:
            snap["organ_shas"][organ] = "error"
    # Deterministic hash of the snapshot (for seal reference)
    try:
        raw = json.dumps(snap, sort_keys=True, default=str)
        snap["snapshot_hash"] = hashlib.sha256(raw.encode()).hexdigest()[:16]
    except Exception:
        pass
    return snap


# ═══════════════════════════════════════════════════════════════════
# ANCHOR 2: OBSERVE — Hash-Verified Evidence Persistence
# ═══════════════════════════════════════════════════════════════════

def persist_evidence(
    observation: dict[str, Any],
    *,
    source: str = "arif_observe",
    session_id: str = "",
) -> dict[str, str]:
    """Write observation to disk with SHA-256. Returns {path, hash, ts}.
    
    Non-blocking: returns empty dict on failure.
    """
    try:
        ts = datetime.now(timezone.utc)
        ts_str = ts.strftime("%Y%m%dT%H%M%S")
        evidence_id = hashlib.sha256(
            json.dumps(observation, sort_keys=True, default=str).encode()
        ).hexdigest()[:12]
        
        record = {
            "evidence_id": evidence_id,
            "timestamp": ts.isoformat(),
            "source": source,
            "session_id": session_id,
            "observation": observation,
        }
        raw = json.dumps(record, sort_keys=True, default=str)
        record["sha256"] = hashlib.sha256(raw.encode()).hexdigest()
        
        filename = f"{ts_str}_{source}_{evidence_id}.json"
        path = EVIDENCE_DIR / filename
        path.write_text(json.dumps(record, indent=2, default=str))
        
        return {
            "evidence_id": evidence_id,
            "path": str(path),
            "sha256": record["sha256"],
            "timestamp": ts.isoformat(),
        }
    except Exception as e:
        logger.debug(f"persist_evidence failed (non-blocking): {e}")
        return {}


# ═══════════════════════════════════════════════════════════════════
# ANCHOR 3: JUDGE — Falsifiable Prediction Extraction
# ═══════════════════════════════════════════════════════════════════

def extract_prediction(
    judge_result: dict[str, Any],
    prediction_schema: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Extract falsifiable predictions from judge output.
    
    Returns a dict of {prediction_key: predicted_value} that can be
    checked against future observations. Empty dict if none found.
    """
    predictions: dict[str, Any] = {}
    try:
        # Look for explicit prediction fields in the result
        for key in ("predicted_state", "predictions", "l3_predictions"):
            if key in judge_result and isinstance(judge_result[key], dict):
                predictions.update(judge_result[key])
        
        # Extract from apex_scalars if present (these ARE predictions)
        apex = judge_result.get("apex_scalars", {})
        if isinstance(apex, dict):
            for k in ("g_score", "delta_S", "omega", "psi_le"):
                if k in apex:
                    predictions[f"apex.{k}"] = apex[k]
        
        # Extract from vitals if present
        vitals = judge_result.get("vitals", {})
        if isinstance(vitals, dict):
            for k in ("cpu_pct", "mem_pct", "fq"):
                if k in vitals:
                    predictions[f"vitals.{k}"] = vitals[k]
    except Exception:
        pass
    return predictions


# ═══════════════════════════════════════════════════════════════════
# ANCHOR 4: SEAL — Observation Hash + VPS Delta
# ═══════════════════════════════════════════════════════════════════

def seal_reality_context(
    init_snapshot_hash: str = "",
    evidence_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Build reality context for seal: current VPS delta + evidence refs.
    
    Compares current state against init snapshot hash to detect drift.
    """
    ctx: dict[str, Any] = {
        "seal_timestamp": datetime.now(timezone.utc).isoformat(),
        "init_snapshot_hash": init_snapshot_hash or "none",
        "current_snapshot_hash": "",
        "vps_drift": False,
        "evidence_refs": evidence_ids or [],
    }
    try:
        current = vps_snapshot()
        ctx["current_snapshot_hash"] = current.get("snapshot_hash", "")
        if init_snapshot_hash and ctx["current_snapshot_hash"]:
            ctx["vps_drift"] = (ctx["current_snapshot_hash"] != init_snapshot_hash)
    except Exception:
        pass
    return ctx
