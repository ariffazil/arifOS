# arifos_core/telemetry.py
"""
telemetry.py — The Eye of arifOS (v36.2 PHOENIX Observability)

Centralized telemetry for governance events. Logs every judgment
to enable audit trails, calibration tuning, and regression detection.

Spec Alignment (v36.3Ω):
    Spec: archive/versions/v36_3_omega/v36.3O/spec/apex_prime_telemetry_v36.3O.json
    Status: PARTIAL alignment (lightweight logging vs full audit schema)

    This module provides a lightweight JSONL logger for governance events.
    The full spec schema (session_id, query_hash, floor_results, cce_audits,
    waw_signals, audit_trail) is implemented in zkpc_runtime.py for
    Cooling Ledger (L1) entries.

    Field mapping differences (HOTSPOT for v36.4Ω):
    - Spec: query_hash/response_hash vs Code: input_preview/output_preview
    - Spec: floor_metrics + floor_results vs Code: floors dict
    - Spec: verdict.code vs Code: verdict string
    - Spec: aggregate_metrics.Psi_APEX vs Code: Psi

    Full spec alignment deferred to v36.4Ω. For now, this module serves as
    a secondary observability layer alongside zkpc_runtime receipts.

Purpose:
    Move from "Black Box" judgments to "Glass Box" telemetry.
    We need to see the flow of governance in real-time.

Output Format: JSONL (one JSON object per line)
    - Human-readable timestamps
    - Input/output previews (truncated for privacy)
    - Full verdict and metrics
    - Floor status and violations

Usage:
    from arifos_core.utils.telemetry_v36 import telemetry

    # Log a judgment event
    telemetry.log_event(
        input_text="What is AI?",
        output_text="AI is artificial intelligence...",
        judgment=judgment_result,
    )

    # Log with custom metadata
    telemetry.log_event(
        input_text=query,
        output_text=response,
        judgment=result,
        metadata={"model": "SEA-LION", "mode": "governed"},
    )

Log File Location:
    Default: ./logs/arifos_governance.jsonl
    Override: ARIFOS_TELEMETRY_PATH environment variable

Author: arifOS Project
Version: 36.2 PHOENIX
Motto: "Eyes on the Law."
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# CONSTANTS
# =============================================================================

DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE = "arifos_governance.jsonl"
PREVIEW_LENGTH = 100  # Characters to include in previews
VERSION = "v36.2-PHOENIX"


# =============================================================================
# TELEMETRY EVENT
# =============================================================================

@dataclass
class TelemetryEvent:
    """
    A single governance telemetry event.

    Contains all information needed to reconstruct and audit
    a governance decision.
    """
    # Timing
    timestamp: float
    timestamp_iso: str

    # Content previews (truncated for privacy/storage)
    input_preview: str
    output_preview: str

    # Verdict
    verdict: str

    # GENIUS LAW metrics
    G: float = 0.0
    Psi: float = 0.0
    C_dark: float = 0.0

    # Floor status
    floors: Dict[str, bool] = field(default_factory=dict)

    # Violations and warnings
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Metadata
    version: str = VERSION
    high_stakes: bool = False
    model: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "timestamp_iso": self.timestamp_iso,
            "input_preview": self.input_preview,
            "output_preview": self.output_preview,
            "verdict": self.verdict,
            "metrics": {
                "G": round(self.G, 4),
                "Psi": round(self.Psi, 4),
                "C_dark": round(self.C_dark, 4),
            },
            "floors": self.floors,
            "violations": self.violations,
            "warnings": self.warnings,
            "version": self.version,
            "high_stakes": self.high_stakes,
            "model": self.model,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


# =============================================================================
# TELEMETRY CLASS
# =============================================================================

class Telemetry:
    """
    The Eye of arifOS. Logs every judgment event for audit.

    Features:
    - JSONL output (append-only, one event per line)
    - Automatic log rotation by date (optional)
    - Privacy-aware previews (truncated input/output)
    - Thread-safe file writing
    - Configurable via environment variables

    Environment Variables:
        ARIFOS_TELEMETRY_PATH: Override default log file path
        ARIFOS_TELEMETRY_ENABLED: Set to "false" to disable logging

    Example:
        telemetry = Telemetry()
        telemetry.log_event(query, response, judgment)

        # Check recent events
        events = telemetry.get_recent_events(10)
        for e in events:
            print(f"{e['verdict']}: {e['input_preview']}")
    """

    def __init__(
        self,
        log_file: Optional[str] = None,
        enabled: bool = True,
        preview_length: int = PREVIEW_LENGTH,
    ):
        """
        Initialize telemetry logger.

        Args:
            log_file: Path to log file (default: logs/arifos_governance.jsonl)
            enabled: Whether logging is enabled
            preview_length: Max characters for input/output previews
        """
        # Check environment override
        env_path = os.environ.get("ARIFOS_TELEMETRY_PATH")
        env_enabled = os.environ.get("ARIFOS_TELEMETRY_ENABLED", "true")

        self.enabled = enabled and env_enabled.lower() != "false"
        self.preview_length = preview_length

        # Determine log file path
        if log_file:
            self.log_file = Path(log_file)
        elif env_path:
            self.log_file = Path(env_path)
        else:
            self.log_file = Path(DEFAULT_LOG_DIR) / DEFAULT_LOG_FILE

        # Ensure log directory exists
        if self.enabled:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Event counter for this session
        self._event_count = 0

    def _truncate(self, text: str) -> str:
        """Truncate text for preview, preserving meaning."""
        if not text:
            return ""
        text = text.replace("\n", " ").strip()
        if len(text) <= self.preview_length:
            return text
        return text[:self.preview_length - 3] + "..."

    def _extract_judgment_data(self, judgment: Any) -> Dict[str, Any]:
        """
        Extract data from various judgment object types.

        Handles:
        - JudgmentResult (from sealion/judge.py)
        - GeniusVerdict (from genius_metrics.py)
        - Dict (raw dictionary)
        """
        data = {
            "verdict": "UNKNOWN",
            "G": 0.0,
            "Psi": 0.0,
            "C_dark": 0.0,
            "floors": {},
            "violations": [],
            "warnings": [],
            "high_stakes": False,
            "model": "",
        }

        if judgment is None:
            return data

        # Handle dict-like objects
        if isinstance(judgment, dict):
            data["verdict"] = judgment.get("verdict", "UNKNOWN")
            data["G"] = judgment.get("G", judgment.get("genius_index", 0.0))
            data["Psi"] = judgment.get("Psi", judgment.get("psi_apex", 0.0))
            data["C_dark"] = judgment.get("C_dark", judgment.get("dark_cleverness", 0.0))
            data["floors"] = judgment.get("floors", {})
            data["violations"] = judgment.get("violations", judgment.get("amanah_violations", []))
            data["warnings"] = judgment.get("warnings", judgment.get("amanah_warnings", []))
            data["high_stakes"] = judgment.get("high_stakes", False)
            data["model"] = judgment.get("model", "")
            return data

        # Handle object with attributes
        data["verdict"] = getattr(judgment, "verdict", "UNKNOWN")
        data["G"] = getattr(judgment, "G", getattr(judgment, "genius_index", 0.0))
        data["Psi"] = getattr(judgment, "Psi", getattr(judgment, "psi_apex", 0.0))
        data["C_dark"] = getattr(judgment, "C_dark", getattr(judgment, "dark_cleverness", 0.0))
        data["floors"] = getattr(judgment, "floors", {})
        data["violations"] = getattr(judgment, "amanah_violations", getattr(judgment, "violations", []))
        data["warnings"] = getattr(judgment, "amanah_warnings", getattr(judgment, "warnings", []))
        data["high_stakes"] = getattr(judgment, "high_stakes", False)
        data["model"] = getattr(judgment, "model", "")

        return data

    def log_event(
        self,
        input_text: str,
        output_text: str,
        judgment: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[TelemetryEvent]:
        """
        Log a governance event to JSONL.

        Args:
            input_text: The input query/prompt
            output_text: The LLM output being judged
            judgment: JudgmentResult, GeniusVerdict, or dict with verdict data
            metadata: Optional additional metadata to include

        Returns:
            TelemetryEvent if logged, None if disabled

        Example:
            telemetry.log_event(
                input_text="What is ML?",
                output_text="Machine Learning is...",
                judgment=judge_result,
                metadata={"session_id": "abc123"},
            )
        """
        if not self.enabled:
            return None

        # Extract judgment data
        jdata = self._extract_judgment_data(judgment)

        # Create event
        now = time.time()
        event = TelemetryEvent(
            timestamp=now,
            timestamp_iso=datetime.fromtimestamp(now).isoformat(),
            input_preview=self._truncate(input_text),
            output_preview=self._truncate(output_text),
            verdict=jdata["verdict"],
            G=jdata["G"],
            Psi=jdata["Psi"],
            C_dark=jdata["C_dark"],
            floors=jdata["floors"],
            violations=jdata["violations"],
            warnings=jdata["warnings"],
            high_stakes=jdata["high_stakes"],
            model=jdata["model"],
            metadata=metadata or {},
        )

        # Write to log file
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(event.to_json() + "\n")
            self._event_count += 1
        except (IOError, OSError) as e:
            # Fail silently but record error in metadata
            event.metadata["write_error"] = str(e)

        return event

    def get_recent_events(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent N events from the log.

        Args:
            n: Number of events to retrieve

        Returns:
            List of event dictionaries (most recent last)
        """
        if not self.log_file.exists():
            return []

        events = []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except (IOError, OSError):
            return []

        return events[-n:]

    def get_event_count(self) -> int:
        """Get number of events logged this session."""
        return self._event_count

    def get_verdict_stats(self) -> Dict[str, int]:
        """
        Get verdict distribution from the log.

        Returns:
            Dict mapping verdict -> count
        """
        stats: Dict[str, int] = {}

        if not self.log_file.exists():
            return stats

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            event = json.loads(line)
                            verdict = event.get("verdict", "UNKNOWN")
                            stats[verdict] = stats.get(verdict, 0) + 1
                        except json.JSONDecodeError:
                            continue
        except (IOError, OSError):
            pass

        return stats

    def clear_log(self) -> bool:
        """
        Clear the log file (for testing).

        Returns:
            True if cleared, False if error
        """
        try:
            if self.log_file.exists():
                self.log_file.unlink()
            return True
        except (IOError, OSError):
            return False


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# Default telemetry instance (enabled by default)
telemetry = Telemetry()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def log_governance_event(
    input_text: str,
    output_text: str,
    judgment: Any,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[TelemetryEvent]:
    """
    Log a governance event using the default telemetry instance.

    Args:
        input_text: The input query/prompt
        output_text: The LLM output being judged
        judgment: JudgmentResult or dict with verdict data
        metadata: Optional additional metadata

    Returns:
        TelemetryEvent if logged, None if disabled
    """
    return telemetry.log_event(input_text, output_text, judgment, metadata)


def get_governance_stats() -> Dict[str, Any]:
    """
    Get governance statistics from the default telemetry instance.

    Returns:
        Dict with verdict_stats, event_count, log_file
    """
    return {
        "verdict_stats": telemetry.get_verdict_stats(),
        "session_events": telemetry.get_event_count(),
        "log_file": str(telemetry.log_file),
    }


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    "TelemetryEvent",
    "Telemetry",
    "telemetry",
    "log_governance_event",
    "get_governance_stats",
]
