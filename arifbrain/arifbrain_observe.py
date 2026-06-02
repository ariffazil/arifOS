#!/usr/bin/env python3
"""
arifbrain_observe.py — Phase 1 federation heartbeat
=====================================================

Polls organ health + VAULT999 height, embeds a structured snapshot into
Qdrant (collection: `arifbrain_states`), and whispers to Telegram if any
organ is degraded.

This is the audit-validated Phase 1: embed-only, no LLM, no Graphiti.
The whole script is ~150 lines, no Temporal SDK needed.

Schedule: every 4h via cron (root crontab).
Logs:     /var/log/arifos/arifbrain.log
Status:   `arifbrain-observe` systemd unit (MemoryMax=512M).

Phase 1b (2026-06-02): federation-probe refactor.
  - One call to A-FORGE /api/federation-probe returns all 6 organs + verdict
  - Falls back to individual organ polls if probe is unreachable
  - Snapshot text now includes the GREEN/YELLOW/RED verdict

Phase 1c (2026-06-02): federation expanded to 9 organs.
  - Federation-probe was extended to 9 organs (added arifosd, APEX, OpenClaw, cn-organ)
  - Fallback ORGANS dict updated to all 9 to match
  - Comments and log messages bumped 6→9 to match reality
  - Shape unchanged; old Qdrant points still valid (backward compatible)

Authority: Ω (A-ENGINEER) | F1 Safety (reversible) | F9 Anti-Hantu
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────────────────
# Config — env-overridable
# ─────────────────────────────────────────────────────────
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3:latest")
COLLECTION = os.getenv("ARIFBRAIN_COLLECTION", "arifbrain_states")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", "1024"))

# Organ endpoints — health, optional /identity for richer payload
# Primary: A-FORGE /api/federation-probe (1 call, 9 organs + verdict)
# Fallback: individual polls (used if probe is unreachable)
# 9 organs: arifOS, arifosd, WEALTH, WELL, GEOX, A-FORGE, APEX, OpenClaw, cn-organ
FEDERATION_PROBE_URL = os.getenv(
    "ARIFBRAIN_PROBE_URL", "http://127.0.0.1:7071/api/federation-probe"
)
ORGANS = {
    "arifOS": os.getenv("ARIFBRAIN_ARIFOS_URL", "http://127.0.0.1:8088/health"),
    "arifosd": os.getenv("ARIFBRAIN_ARIFOSD_URL", "http://127.0.0.1:18081/health"),
    "WEALTH": os.getenv("ARIFBRAIN_WEALTH_URL", "http://127.0.0.1:18082/health"),
    "WELL": os.getenv("ARIFBRAIN_WELL_URL", "http://127.0.0.1:18083/health"),
    "GEOX": os.getenv("ARIFBRAIN_GEOX_URL", "http://127.0.0.1:8081/health"),
    "A-FORGE": os.getenv("ARIFBRAIN_AFORGE_URL", "http://127.0.0.1:7071/health"),
    "APEX": os.getenv("ARIFBRAIN_APEX_URL", "http://127.0.0.1:3002/health"),
    "OpenClaw": os.getenv("ARIFBRAIN_OPENCLAW_URL", "http://127.0.0.1:18789/health"),
    "cn-organ": os.getenv("ARIFBRAIN_CNORGAN_URL", "http://127.0.0.1:18790/health"),
}

# VAULT999 height source — we use the writer on 5001 (gives chain height)
VAULT_URL = os.getenv("ARIFBRAIN_VAULT_URL", "http://127.0.0.1:5001/health")

# Whisper channel — Hermes webhook (F13 sovereign territory; opt-in only)
# Set ARIFBRAIN_WHISPER_ENABLED=true once Telegram credentials are wired correctly.
WHISPER_ENABLED = os.getenv("ARIFBRAIN_WHISPER_ENABLED", "false").lower() == "true"
HERMES_URL = os.getenv("ARIFBRAIN_HERMES_URL", "http://127.0.0.1:18001/send")
HERMES_CHAT_ID = os.getenv("ARIFBRAIN_CHAT_ID", "267378578")

# Timezone
TZ_KL = timezone.utc  # all timestamps UTC; converted in display if needed

LOG_PATH = Path("/var/log/arifos/arifbrain.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("arifbrain")

HTTP_TIMEOUT_S = 10
EMBED_TIMEOUT_S = 60


# ─────────────────────────────────────────────────────────
# HTTP helpers
# ─────────────────────────────────────────────────────────
def _http_get(url: str, timeout: int = HTTP_TIMEOUT_S) -> tuple[int, str, dict | None]:
    """GET url. Returns (status_code, body_text, parsed_json_or_None)."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            body = r.read().decode(errors="replace")
            try:
                return r.status, body, json.loads(body)
            except json.JSONDecodeError:
                return r.status, body, None
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:200], None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 0, f"{type(e).__name__}: {e}", None


def _http_post(url: str, payload: dict, timeout: int = HTTP_TIMEOUT_S) -> tuple[int, str]:
    """POST json payload. Returns (status, body)."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode(errors="replace")[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:200]
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 0, f"{type(e).__name__}: {e}"


def _http_put(url: str, payload: dict, timeout: int = HTTP_TIMEOUT_S) -> tuple[int, str]:
    """PUT json payload. Used for Qdrant collection creation."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="PUT"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode(errors="replace")[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:200]
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 0, f"{type(e).__name__}: {e}"


# ─────────────────────────────────────────────────────────
# Observe
# ─────────────────────────────────────────────────────────
def poll_organs() -> dict[str, dict[str, Any]]:
    """Poll federation via A-FORGE /api/federation-probe (1 call, 9 organs).

    Falls back to individual organ polls if the probe is unreachable.
    Returns {name: {status, code, url, excerpt, latency_ms?}, "__summary__"?: {...}}.
    """
    # Try federation-probe (single call, 9 organs + verdict)
    code, body, parsed = _http_get(FEDERATION_PROBE_URL)
    if code == 200 and isinstance(parsed, dict) and "organs" in parsed:
        snapshot: dict[str, dict[str, Any]] = {}
        for name, info in parsed["organs"].items():
            raw_status = info.get("status", "unknown")
            # Map probe vocabulary (up/down) → arifbrain (healthy/degraded)
            if raw_status == "up":
                status = "healthy"
            elif raw_status == "down":
                status = "degraded"
            else:
                status = raw_status
            snapshot[name] = {
                "status": status,
                "code": info.get("http_status", 0),
                "url": info.get("url", ""),
                "excerpt": (info.get("sample", "") or "")[:120],
                "latency_ms": info.get("latency_ms", 0),
            }
        summary = parsed.get("summary", {})
        if summary:
            snapshot["__summary__"] = {
                "verdict": summary.get("verdict", "?"),
                "up": summary.get("up", 0),
                "total": summary.get("total", 0),
            }
            log.info(
                f"federation-probe: {summary.get('verdict', '?')} "
                f"({summary.get('up', 0)}/{summary.get('total', 0)})"
            )
        return snapshot

    # Fallback: individual polls (9 separate HTTP calls)
    log.warning(
        f"federation-probe unreachable at {FEDERATION_PROBE_URL} ({code}); "
        f"falling back to individual organ polls"
    )
    snapshot = {}
    for name, url in ORGANS.items():
        code, body, parsed = _http_get(url)
        if code == 200 and isinstance(parsed, dict):
            status = parsed.get("status") or parsed.get("verdict") or "healthy"
            if status not in ("healthy", "live", "ok", "VERIFIED"):
                status = "degraded"
        elif code == 0:
            status = "unreachable"
        else:
            status = f"http_{code}"
        snapshot[name] = {
            "status": status,
            "code": code,
            "url": url,
            "excerpt": body[:120],
        }
    return snapshot


def poll_vault_height() -> int | str:
    """Read VAULT999 chain height from writer."""
    code, body, parsed = _http_get(VAULT_URL)
    if code == 200 and isinstance(parsed, dict):
        return parsed.get("chain_height", parsed.get("vault_seals_count", "?"))
    return "unknown"


# ─────────────────────────────────────────────────────────
# Compress + embed
# ─────────────────────────────────────────────────────────
def compress_snapshot(ts: str, organs: dict, vault_height: Any) -> str:
    """Build a short structured string (~200 chars) for embedding.

    Format: 'state TS: arifOS=healthy | WEALTH=healthy | ... | vault=N | verdict=GREEN'

    The optional `__summary__` key (added by poll_organs from federation-probe)
    is consumed to append the verdict without polluting the per-organ entries.
    """
    parts = [f"state {ts}"]
    summary = organs.get("__summary__")
    for name, info in organs.items():
        if name == "__summary__":
            continue
        parts.append(f"{name}={info['status']}")
    parts.append(f"vault={vault_height}")
    if summary:
        parts.append(f"verdict={summary.get('verdict', '?')}")
    return " | ".join(parts)


def embed(text: str) -> list[float] | None:
    """Embed via Ollama /api/embed (single prompt). Returns 1024-dim vec or None."""
    payload = json.dumps({"model": EMBED_MODEL, "input": text[:8000]}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embed",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=EMBED_TIMEOUT_S) as r:
                data = json.loads(r.read().decode())
            vecs = data.get("embeddings")
            if isinstance(vecs, list) and vecs and len(vecs[0]) == VECTOR_SIZE:
                return vecs[0]
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
            time.sleep(1 + attempt)
    return None


def upsert_point(point_id: str, vec: list[float], payload: dict) -> bool:
    """Upsert single point to Qdrant. Returns True on success."""
    body = {"points": [{"id": point_id, "vector": vec, "payload": payload}]}
    code, body_resp = _http_put(
        f"{QDRANT_URL}/collections/{COLLECTION}/points?wait=false",
        body,
    )
    return code in (200, 201)


def ensure_collection() -> None:
    """Create arifbrain_states collection if missing (1024d cosine)."""
    code, _, _ = _http_get(f"{QDRANT_URL}/collections/{COLLECTION}")
    if code == 200:
        log.info(f"collection '{COLLECTION}' exists ✓")
        return
    log.info(f"creating collection '{COLLECTION}' (size={VECTOR_SIZE}, cosine)")
    code, body = _http_put(
        f"{QDRANT_URL}/collections/{COLLECTION}",
        {
            "vectors": {"size": VECTOR_SIZE, "distance": "Cosine"},
            "optimizers_config": {"indexing_threshold": 10000},
        },
    )
    if code not in (200, 201):
        log.error(f"failed to create collection: {code} {body}")
        sys.exit(2)


# ─────────────────────────────────────────────────────────
# Whisper (Telegram via Hermes)
# ─────────────────────────────────────────────────────────
def whisper(down_organs: list[str], ts: str) -> bool:
    """Send a Telegram whisper if any organ is down. Returns True on success."""
    msg = f"⚠️ arifbrain: {', '.join(down_organs)} degraded at {ts}"
    code, body = _http_post(
        HERMES_URL,
        {
            "chat_id": HERMES_CHAT_ID,
            "text": msg,
        },
    )
    if code in (200, 201, 202):
        log.info(f"whispered to telegram ({code})")
        return True
    log.warning(f"whisper failed: {code} {body}")
    return False


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────
def main() -> int:
    started = datetime.now(timezone.utc)
    log.info(f"=== arifbrain_observe START ({started.isoformat()}) ===")

    # 0. Preflight
    code, _, _ = _http_get(QDRANT_URL)
    if code != 200:
        log.error(f"Qdrant unreachable at {QDRANT_URL}: {code}")
        return 1
    test = embed("ping")
    if test is None:
        log.error(f"Ollama unreachable or bge-m3 missing at {OLLAMA_URL}")
        return 1

    # 1. Ensure collection
    ensure_collection()

    # 2. Observe
    ts = started.isoformat()
    organs = poll_organs()
    vault_height = poll_vault_height()
    text = compress_snapshot(ts, organs, vault_height)
    log.info(f"snapshot: {text}")

    # 3. Embed + upsert
    vec = embed(text)
    if vec is None:
        log.error("embedding failed; aborting")
        return 1
    point_id = hashlib.sha256(text.encode()).hexdigest()[:32]
    payload = {
        "ts": ts,
        "text": text,
        "snapshot": {"organs": organs, "vault_height": vault_height},
        "source": "arifbrain_phase1",
        "schema": "v1",
    }
    if not upsert_point(point_id, vec, payload):
        log.error("qdrant upsert failed")
        return 1
    log.info(f"upserted point id={point_id[:12]}… to {COLLECTION}")

    # 4. Whisper if any organ degraded (opt-in, F13 sovereign territory)
    # Skip the synthetic __summary__ key (added by federation-probe) — it has no status.
    down = [
        k
        for k, v in organs.items()
        if k != "__summary__" and v.get("status") not in ("healthy", "live", "ok", "VERIFIED", "up")
    ]
    if down:
        log.warning(f"degraded organs: {', '.join(down)}")
        if WHISPER_ENABLED:
            whisper(down, ts)
        else:
            log.info("whisper disabled (ARIFBRAIN_WHISPER_ENABLED=false); would have alerted")
    else:
        log.info("all organs healthy — no whisper needed")

    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    log.info(f"=== arifbrain_observe DONE in {elapsed:.1f}s ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
