"""
arifOS → Federation Organ Heartbeat Publisher (template)

Forged: 2026-06-11 by omega-forge-agent
Status: STAGED. Not wired into any systemd unit. The kernel
heartbeat daemon (arifOS-NATS-heartbeat.service) uses a different
file (arifosmcp/abi/nats_heartbeat_daemon.py); this template is
for the OTHER organs (geox, wealth, well, a-forge, aaa, apex,
hermes, openclaw, cn-organ) to attest to the JetStream stream
'arifos-organs' on subject 'arifos.organ.<organ>'.

To use this for a specific organ:
  1. Copy this file to /opt/<organ>/app/heartbeat_publisher.py
     (or wherever the organ's app lives).
  2. Set ORGAN_NAME = '<organ>' in the constants below.
  3. Set HEALTH_URL = 'http://127.0.0.1:<port>/health'.
  4. Add a systemd unit that runs `python heartbeat_publisher.py`.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

import asyncio
import json
import logging
import signal
import sys
import time
from datetime import UTC, datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("arifOS.federation_heartbeat")

# ──────────────────────────────────────────────────────────────────────
# CONFIGURE THIS BEFORE DEPLOYING
# ──────────────────────────────────────────────────────────────────────
ORGAN_NAME = "<SET_ME>"  # e.g. "geox", "wealth", "well", "a-forge", "aaa"
HEALTH_URL = "http://127.0.0.1:<SET_PORT>/health"
NATS_URL = "nats://127.0.0.1:4222"
PUBLISH_INTERVAL_S = 60
NATS_SUBJECT = f"arifos.organ.{ORGAN_NAME}"  # the stream filter is 'arifos.organ.>'
NATS_STREAM = "arifos-organs"

# Read these from a 60-line example that lives in
# arifOS/abi/heartbeat_publisher_template.py. The other organs
# copy this file and set ORGAN_NAME + HEALTH_URL at the top.

try:
    import httpx
    import nats

    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


async def _fetch_health(timeout_s: float = 5.0) -> dict | None:
    if not DEPS_AVAILABLE:
        return None
    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            r = await client.get(HEALTH_URL)
            if r.status_code == 200:
                return r.json()
    except Exception as e:
        logger.warning("health fetch failed: %s", e)
    return None


async def _publish(nc, payload: bytes) -> tuple[bool, bool]:
    """Returns (plain_ok, js_ok)."""
    plain_ok = False
    js_ok = False
    try:
        await nc.publish(f"{ORGAN_NAME}.health", payload)
        await nc.flush()
        plain_ok = True
    except Exception as e:
        logger.error("plain publish failed: %s", e)
    try:
        js = nc.jetstream()
        await js.publish(NATS_SUBJECT, payload)
        js_ok = True
    except Exception as e:
        logger.warning("JetStream publish failed: %s", e)
    return plain_ok, js_ok


def _build_event(health: dict) -> dict:
    """Build a heartbeat event from the organ's /health payload."""
    return {
        "event": "FEDERATION_HEARTBEAT",
        "organ": ORGAN_NAME,
        "verdict": health.get("verdict") or health.get("status") or "UNKNOWN",
        "tool_count": (
            health.get("tools_loaded")
            or health.get("canonical_tools")
            or health.get("tool_count")
            or 0
        ),
        "registry_truth": health.get("registry_truth", "UNKNOWN"),
        "raw_health": health,
        "timestamp": _now_iso(),
    }


async def main() -> None:
    if ORGAN_NAME == "<SET_ME>":
        logger.error("ORGAN_NAME not configured. Edit this file before running.")
        sys.exit(1)
    if not DEPS_AVAILABLE:
        logger.error("Required deps not installed: nats, httpx")
        sys.exit(1)

    logger.info("Federation heartbeat starting for organ=%s", ORGAN_NAME)
    nc = await nats.connect(NATS_URL)
    logger.info("NATS connected: %s", NATS_URL)

    stop_event = asyncio.Event()
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop_event.set)

    consecutive_failures = 0
    while not stop_event.is_set():
        health = await _fetch_health()
        if health is None:
            consecutive_failures += 1
            logger.warning("health fetch failed (%d consecutive)", consecutive_failures)
        else:
            consecutive_failures = 0
            event = _build_event(health)
            payload = json.dumps(event, default=str).encode()
            plain_ok, js_ok = await _publish(nc, payload)
            logger.info(
                "Heartbeat: organ=%s verdict=%s plain=%s js=%s tool_count=%s",
                ORGAN_NAME,
                event["verdict"],
                plain_ok,
                js_ok,
                event["tool_count"],
            )
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=PUBLISH_INTERVAL_S)
        except asyncio.TimeoutError:
            pass

    await nc.close()
    logger.info("Federation heartbeat stopped for organ=%s", ORGAN_NAME)


if __name__ == "__main__":
    asyncio.run(main())
