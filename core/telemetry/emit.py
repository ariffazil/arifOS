#!/usr/bin/env python3
"""Cross-agent telemetry emitter. One call, one NATS message.

Usage:
    python3 /root/arifOS/core/telemetry/emit.py hermes federation_audit "Audit done." 0.95
"""

import json
import subprocess
import sys
from datetime import datetime, timezone


def main():
    if len(sys.argv) < 4:
        print("Usage: emit.py <agent> <event_type> <payload> [confidence]")
        sys.exit(1)

    agent = sys.argv[1]
    event_type = sys.argv[2]
    payload = sys.argv[3]
    confidence = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0

    event = json.dumps(
        {
            "agent": agent,
            "event": event_type,
            "payload": payload,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "schema": "cross-agent-event/v1",
        }
    )

    subject = f"agent.memory.{agent}.{event_type}"
    result = subprocess.run(
        ["nats", "pub", "--jetstream", subject],
        input=event.encode(),
        capture_output=True,
        timeout=5,
    )

    if result.returncode != 0:
        print(f"FAILED: {result.stderr.decode()}", file=sys.stderr)
        sys.exit(1)

    # nats pub --jetstream prints to stderr, capture it
    output = result.stderr.decode().strip()
    print(output)


if __name__ == "__main__":
    main()
