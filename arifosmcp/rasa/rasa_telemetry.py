"""
Rasa Contract Shadow Telemetry Logger — ARIF_RASA_TELEMETRY_v1

DITEMPA BUKAN DIBERI — Forged, Not Given.

Shadow telemetry that logs all rasa governance decisions to an
append-only JSONL file. In SHADOW mode, this is the ONLY effect —
the original kernel output is never modified. In ENFORCE modes,
telemetry continues to log alongside enforcement.

Log format per line:
  {
    "timestamp": "ISO8601",
    "session_id": "...",
    "message_snippet": "first 100 chars",
    "risk_band": "safe|distress|crisis",
    "detection_tags": [...],
    "governed_posture": "proceed|simplify|verify|draft_only|hold|human_loop",
    "ungoverned_posture": "proceed",
    "delta": "what would change",
    "enforcement_mode": "shadow|enforce_crisis|...",
    "enforced": true|false
  }

CONSTITUTIONAL BINDING:
  - F1 AMANAH:  Append-only, never blocks execution
  - F9 ANTIHANTU: No consciousness claims logged
  - F10 ONTOLOGY: No soul/feelings claims logged
  - F13 SOVEREIGN: Human can review logs
"""

from __future__ import annotations

import json
import logging
import os
import threading
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Default log path
_DEFAULT_LOG_PATH = "/root/arifOS/logs/rasa_telemetry.jsonl"

# Write lock for thread safety
_lock = threading.Lock()


class RasaTelemetry:
    """Shadow telemetry logger for rasa governance decisions.

    Logs every rasa pipeline execution to a JSONL file. In SHADOW mode,
    telemetry is the ONLY output — the original kernel behavior is
    completely preserved. Telemetry is append-only and never blocks
    execution.

    Attributes:
        log_path: Full path to the JSONL log file.
        enabled: Whether telemetry is active.
    """

    def __init__(self, log_path: str | None = None):
        """Initialize the telemetry logger.

        Args:
            log_path: Path to the JSONL log file. Defaults to
                      /root/arifOS/logs/rasa_telemetry.jsonl.
        """
        self.log_path = log_path or _DEFAULT_LOG_PATH
        self.enabled = True

        # Ensure directory exists
        log_dir = os.path.dirname(self.log_path)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception as e:
                logger.warning(f"Could not create log directory {log_dir}: {e}")
                self.enabled = False

    def log_shadow(
        self,
        *,
        session_id: str,
        message: str,
        ungoverned_result: dict | None,
        governed_result: dict | None,
        enforcement_mode: str,
        enforced: bool,
    ) -> None:
        """Log a shadow telemetry entry.

        Records the delta between what the kernel WOULD have done
        (ungoverned) and what rasa governance determined (governed).

        Args:
            session_id: Session identifier.
            message: Original human message (truncated to 100 chars).
            ungoverned_result: What the original kernel produced.
            governed_result: What rasa governance determined.
            enforcement_mode: Current RasaContractMode value.
            enforced: Whether enforcement was applied.
        """
        if not self.enabled:
            return

        try:
            # Extract key fields from governed result
            risk_band = "unknown"
            detection_tags: list[str] = []
            governed_posture = "unknown"
            ungoverned_posture = "proceed"

            if governed_result:
                detection = governed_result.get("detection")
                if detection is not None:
                    if hasattr(detection, "risk_band"):
                        risk_band = detection.risk_band.value
                    if hasattr(detection, "emotion_tags"):
                        detection_tags = [t.value for t in detection.emotion_tags]

                judge = governed_result.get("judge")
                if judge is not None and hasattr(judge, "allowed_postures"):
                    postures = judge.allowed_postures
                    if postures:
                        governed_posture = postures[0].value

                final = governed_result.get("final_posture")
                if final is not None:
                    if hasattr(final, "value"):
                        governed_posture = final.value
                    elif isinstance(final, str):
                        governed_posture = final

            # Build delta description
            if enforced:
                delta = f"Output governed: {risk_band} → posture {governed_posture}"
            else:
                delta = f"Shadow only: {risk_band} (would enforce → {governed_posture})"

            # Message snippet (first 100 chars)
            snippet = (message or "")[:100]

            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": session_id or "unknown",
                "message_snippet": snippet,
                "risk_band": risk_band,
                "detection_tags": detection_tags,
                "governed_posture": governed_posture,
                "ungoverned_posture": ungoverned_posture,
                "delta": delta,
                "enforcement_mode": enforcement_mode,
                "enforced": enforced,
            }

            with _lock:
                with open(self.log_path, "a") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        except Exception as e:
            # Telemetry must never block execution
            logger.debug(f"Telemetry write failed (non-blocking): {e}")

    def should_enforce(self, detection, enforcement_mode: str) -> bool:
        """Check if the current mode allows enforcement for this detection.

        Args:
            detection: RasaDetection object or dict with risk_band.
            enforcement_mode: Current RasaContractMode value.

        Returns:
            True if enforcement should be applied.
        """
        if enforcement_mode == "shadow":
            return False

        risk_band = "safe"
        if detection is not None:
            if hasattr(detection, "risk_band"):
                risk_band = detection.risk_band.value
            elif isinstance(detection, dict):
                risk_band = detection.get("risk_band", "safe")

        risk_lower = risk_band.lower() if isinstance(risk_band, str) else str(risk_band).lower()

        if enforcement_mode == "enforce_crisis":
            return risk_lower == "crisis"

        if enforcement_mode == "enforce_distress":
            return risk_lower in ("crisis", "distress")

        if enforcement_mode == "enforce_all":
            return True

        return False

    def read_log(self, limit: int = 20) -> list[dict]:
        """Read the most recent telemetry entries.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            List of telemetry entry dicts, most recent first.
        """
        entries: list[dict] = []
        try:
            if not os.path.exists(self.log_path):
                return entries

            with _lock:
                with open(self.log_path) as f:
                    lines = f.readlines()

            # Return last N entries, reversed (most recent first)
            for line in lines[-limit:]:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

            entries.reverse()
        except Exception as e:
            logger.debug(f"Telemetry read failed: {e}")

        return entries

    def clear_log(self) -> None:
        """Clear the telemetry log (for testing only)."""
        try:
            log_dir = os.path.dirname(self.log_path)
            if not os.path.exists(log_dir):
                return
            with _lock:
                with open(self.log_path, "w") as f:
                    f.write("")
        except Exception:
            pass


__all__ = ["RasaTelemetry"]
