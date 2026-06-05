"""NATS JetStream telemetry publisher for cross-agent memory.

Two interfaces:
1. CLI:   python3 /root/arifOS/core/telemetry/emit.py <agent> <event> <payload> [confidence]
2. Python: sys.path.insert(0, '/root/arifOS/core'); from telemetry.publisher import emit

Uses `nats` CLI under the hood — zero Python NATS dependency issues.
"""

import json
import subprocess
from datetime import datetime, timezone

SUBJECT_PREFIX = "agent.memory"


def emit(agent: str, event_type: str, payload: str, confidence: float = 1.0, metadata: dict | None = None):
    """Emit a telemetry event to NATS agent_memory stream via nats CLI.

    Args:
        agent: Agent name (hermes, openclaw, kimi, claude, arifos, etc.)
        event_type: Short event tag (task_complete, error, audit, fix, discovery)
        payload: Human-readable summary (one sentence)
        confidence: 0.0–1.0
        metadata: Optional dict with extra context
    """
    event = json.dumps({
        "agent": agent,
        "event": event_type,
        "payload": payload,
        "confidence": confidence,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
        "schema": "cross-agent-event/v1",
    })

    subject = f"{SUBJECT_PREFIX}.{agent}.{event_type}"
    result = subprocess.run(
        ["nats", "pub", "--jetstream", subject],
        input=event.encode(),
        capture_output=True,
        timeout=5,
    )

    if result.returncode != 0:
        raise RuntimeError(f"nats pub failed: {result.stderr.decode()}")

    # nats pub --jetstream writes status to stderr
    return result.stderr.decode().strip()
